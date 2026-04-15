# Day 10 Findings — Tropical Treasure Hunt (CIF Deal)

*Date: 2026-04-08*
*Deal: Tropical Treasure Hunt Co — CIF Loan, $250,000 approved*
*Signed memo: Loan_Report_Tropical_Treasure_Hunt_4-1-2026.pdf (Keith Williams, 3/31/2026)*
*Workbook: G8WAY_CIF_Tropical_Treasure_Hunt.xlsx*

## TL;DR

Phase 1 extraction ran against a real CIF deal for the first time. Multiple extractor bugs surfaced and one architectural gap in the memo engine was exposed. Phase 2 (reconcile + render) and Phase 3 (section diff) were **halted intentionally** until the extractor and template issues below are fixed — rendering a memo from broken inputs against the wrong template would burn time without finding new bugs.

**Summary: four critical bugs, two architectural gaps, one OCR research task.**

---

## Critical Bugs (Extraction)

### Bug 1 — OCR line-number fusion on scanned tax returns

**Severity: critical**

Scanned Schedule C and 1120-S returns have line numbers in the leftmost column. Tesseract runs the line number into the value via a comma, producing fused tokens:

- 2022 Schedule C Line 1: `1,188,300.` → actual value $188,300, extractor sees $1,188,300
- 2023 Schedule C Line 1: `1,328,424.` → actual value $328,424
- 2024 1120-S Line 6: `6,239,056.` → actual value $239,056 (but extractor returned `6239056`)

**Why Day 9's comma fix didn't catch this:** The Day 9 postprocess rejoins numbers that OCR *split* apart (`757 i 140` → `757,140`). This is the opposite problem — numbers that OCR *fused* with an adjacent line number. Different bug.

**Fix direction:**
- Short term: detect pattern `<1-2 digit>,<3-digit>,<3-digit>...` where leading group matches a nearby line number. Strip the leading group.
- Long term: use tesseract `--psm 6` with TSV output so line numbers stay in their own column by x-coordinate. This is the correct fix but requires re-plumbing `extract/ocr.py`.

### Bug 2 — Space-after-comma money tokens not matched

**Severity: critical**

2024 1120-S Line 1a shows `466, 391.` (space after comma — OCR artifact). My money regex requires `\d{3}` immediately after the comma and doesn't match.

Result: `gross_receipts: None` for 2024 — the single most important extractor output, missed.

**Fix:** Allow optional whitespace in the money regex thousands separator: `(\d{1,3})(?:,\s*(\d{3}))+`. One-line change.

### Bug 3 — PFS Form 413 net_worth sign dropped

**Severity: critical — underwriting risk**

Signed memo: Anthony C. Schultz personal net worth = **($37,817)** (negative).
Extractor output: `net_worth: 37882` (positive, $65 magnitude off).

A negative net worth is a material risk factor. The sign flip masks it. **This is the kind of bug that misleads an underwriter.**

Root cause: `extract/pfs_413.py` computes `net_worth = total_assets - total_liabilities` but returns `abs()` somewhere in the flow, or my anchor isn't reading a pre-computed cell that has the correct sign.

**Fix:** audit the sign-preservation path in `pfs_413.py`. Add a regression test with a negative-net-worth PFS fixture.

Also: total_liabilities came back $120,261 vs. signed memo $120,196 ($65 diff). Probably a subcomponent I'm not summing. Investigate.

### Bug 4 — Small-integer OCR noise returned as real values

**Severity: high**

2024 1120-S extraction returned:
- `compensation_of_officers: 7`
- `salaries_wages: 8`

These are line-number bleed (OCR read the line label "7" and "8" as the values). My `reconcile.py` has an `_OCR_NOISE_MAX = 99` filter that flags these after the fact — but **the extractor itself happily returned them**. That's wrong. The extractor should reject any integer ≤ $99 as implausible unless it has explicit `.dd` decimals.

**Fix:** add a plausibility filter to `_first_money_on_line()` in `tax_return_1120s.py` and `tax_return_1040.py`: reject `int` values under $100 unless the token has decimals.

---

## Architectural Gaps

### Gap A — G8WAY reader scans the wrong sheets

**Severity: architectural — blocks every CIF deal**

The G8WAY workbook is a **multi-program template with 76 sheets**. Different programs use different sheets:

- `7(a) or Conventional` / `7(a) Companion` / `504`
- `USDA` / `USDA Cash Flow` / `USDA BSE Calculation` / `USDA P&L` / `USDA Debt Details`
- `DSCR (UW)` / `Global DSCR (UW)` — underwriter cash flow for any program
- `PFS & DTI` / `Balance Sheet (Borrower)` / `PF Balance Sheet (Borrower)` — standard regardless of program
- `Executive Summary` — headline values, **canonical for every deal**

My Day 9 `extract/g8way.py` only looks at USDA sheets. The TTH workbook has the USDA template sheets present (empty, unused — they're part of the master template) so my reader "found" them and pulled garbage from stray cells. Result: total_liabilities returned as **-$134,847** (negative sign, wrong magnitude), dscr fields all None, requested_rate 10.25% (actual 8.00%), requested_term 300 months (actual 84 months).

**The Executive Summary sheet has everything I need in clean labeled cells.** Verified cell-by-cell:

| Cell | Label | Value | Cross-check vs signed memo |
|---|---|---|---|
| B8 | Colony Bank Exposure | 250,000 | ✅ matches approved loan |
| B59 | 2022 Sales/Revenue | 188,300 | ✅ |
| C59 | 2023 Sales/Revenue | 328,424 | ✅ |
| D59 | 2024 Sales/Revenue | 466,391 | ✅ |
| E59 | YTD 2025 Sales | 548,641 | ✅ (memo says $548K YTD Oct) |
| F59 | Proj Y1 Sales | 700,000 | ✅ |
| D60 | 2024 Borrower DSCR | 1.655 | ✅ (memo: 1.66x) |
| F60 | Proj Y1 DSCR | 1.662 | ✅ (memo: 1.66x) |
| F61 | Proj Y1 Global DSCR | 1.982 | ⚠️ memo says 1.22x — investigate |
| G65 | Avg Personal Credit Score | 611 | — |
| A71 | Workbook version | Version 2025-03-25 | — |

**Fix direction:** Rewrite `extract/g8way.py` with priority order:
1. `Executive Summary` — pull headline values (revenue by year, DSCR by year, global DSCR, loan amount, credit score, liquidity, version string). **New primary path.**
2. `Boarding Sheet` — loan terms fallback
3. Program-specific sheets (`7(a)`, `USDA`, etc.) — detail fallback only if Exec Summary is missing
4. Never trust a USDA sheet value if a non-USDA program is indicated

### Gap B — CIF deals need a separate template, not a Colony Bank override

**Severity: architectural — blocks every CIF memo render**

Day 7's `memo/template.py` has `get_template("cdfi")` which takes the Colony Bank 32-section spine and drops the SBA-specific sections. That was wrong. The signed TTH CIF memo is structurally different:

**CIF memo sections (from the signed 4-1-2026 TTH report):**
1. Header (Applicant, Owner/Guarantor, Location, Approved Loan, Program)
2. Terms / Sources and Uses (table)
3. Proposed Loan Terms (Amount, Rate, Fees, Amortization, P&I, ADS, Collateral Position, Borrower Equity)
4. Business Overview (narrative)
5. Request Summary (narrative)
6. Loan Readiness / Cash Flow Snapshot (historical + projected DSCR table)
7. Supplemental Global Cash Flow / Guarantor Support (narrative + metrics)
8. Collateral Support (table)
9. Net Risk to Bank (calc)
10. Conditions
11. Signature block

This is **not** Colony Bank minus SBA sections — it's a completely different template. Fewer sections, different section order, different render types.

**Fix direction:** create `memo/template_cif.py` as a parallel sibling to Colony Bank's template. Update `get_template()` to route `cdfi` to the CIF template entirely, not an override chain.

### Gap C — Entity name missed on 1120-S

**Severity: medium**

`extract/tax_return_1120s.py` returned `entity_name: None` on the TTH 2024 return. The entity name ("Tropical Treasure Hunt Co") is on page 1 of any 1120-S in the "Name" field next to the EIN box. EIN extracted correctly (66-0886551) so the anchor logic works for numeric fields but not for text.

**Fix:** add a text anchor pass that finds "Name" on the first 20 lines and returns the next non-label token.

---

## OCR Research Task

All four TTH tax returns are scanned (not text-layer). The high-quality OCR profile improves accuracy substantially but does not eliminate line-number fusion or space-after-comma artifacts. The right fix is layout-aware extraction via tesseract TSV output (`-c preserve_interword_spaces=1 tsv`), which returns per-word bounding boxes. Line numbers and values land in different x-coordinate columns and can be separated deterministically.

**Est. effort:** 1-2 days. Target: Day 11 or 12.

---

## Cross-check Scoreboard — What the Engine Got Right

Not all news is bad. The following were correct on the first pass:

- **EIN extraction** (2024 1120-S): 66-0886551 ✓
- **Tax year detection** (2024 1120-S): 2024 ✓
- **S-corp election detection**: First-year S-corp correctly identified via `01/01/2024` election date in the header
- **Ordinary Business Income Line 22**: $61,535 — matches the signed memo's S-corp K-1 pass-through of $61,535 ✓
- **PFS cash on hand**: $34,000 — matches memo exactly ✓
- **PFS automobiles**: $48,379 — reasonable
- **PFS salary**: $35,000 — matches guarantor income
- **2023 Schedule C business net loss**: correctly identified as ($6,742) via Schedule 1 line 3 anchor, matches memo
- **NOL carryforward identification**: $136,800 (2022 NOL from Schedule 1 Line 8a) — matches memo
- **Signed loan report PDF is text-layer, not scanned** — read cleanly without OCR, 16,129 chars in one pass

The engine's *math* layer and the *known-good* extractor paths work fine. The failures are concentrated in OCR-dependent extractors on scanned returns, and in the G8WAY reader's sheet selection logic.

---

## Day 10 Work Plan (Revised)

Given the scope of findings, Day 10 should be a **fix commit**, not a feature commit. Ordered:

1. **G8WAY reader rewrite** — Executive Summary primary path, program-aware fallback. Add a TTH golden fixture test using the real workbook (cached values only, no PII). **Highest leverage fix — unlocks every CIF deal.**
2. **OCR line-number fusion fix** — short-term regex heuristic, defer TSV layout fix to Day 11/12
3. **OCR space-after-comma fix** — 1-line regex change to money pattern
4. **PFS 413 net_worth sign fix** — preserve negative net worth; add negative-fixture regression test
5. **Small-integer OCR noise filter in extractors** — reject int ≤ $99 without decimals
6. **1120-S entity name extraction** — add Name anchor on page 1
7. **CIF memo template** — `memo/template_cif.py` — parallel sibling to Colony Bank template
8. **`get_template("cdfi")` routing** — point to CIF template, drop the override chain
9. **Day 10 commit:** "Day 10: TTH findings fixes — G8WAY exec summary reader, OCR line-number fusion, PFS sign, CIF template"

Phases 2 and 3 (reconcile + render + section diff) resume on Day 10.5 once the fixes above are in. Target: a clean render of the TTH memo that can be diffed section-by-section against the signed 4-1-2026 report.

---

## Files Touched in Phase 1 Investigation (no code changes yet)

- Read: `extract/ocr.py` (caller)
- Read: `extract/tax_return_1120s.py` (extracted 2024 TTH)
- Read: `extract/pfs_413.py` (extracted TTH PFS)
- Read: `extract/g8way.py` (read TTH G8WAY — returned garbage as documented above)
- Read: TTH signed loan report PDF — clean text extraction, scoreboard captured
- OCR cache populated for: 2022 / 2023 / 2024 business + 2024 personal tax returns (~60s each at standard profile)

No commits yet. Ship the fixes as Day 10, then resume Phase 2/3 on the same deal.
