# UnderwriteOS — Build Status

*Last updated: 2026-04-10*
*Current state: Day 10.5 complete. 94/94 tests green. Commit `bec6551` pushed.*

## What UnderwriteOS Does

Bank-grade SBA 7(a), owner-occupied CRE, and CDFI underwriting memo engine. V1 promise: ingest borrower documents → extract → spread → DSCR/global cash flow → risks/missing items → policy gates → 80% memo draft in ~10 minutes.

**Immutable rule:** Claude API is used for classification, narrative, and risk identification only. It never computes numbers. DSCR, global cash flow, ADS, and every other ratio are done in Python in `cashflow.py`. This boundary is load-bearing and enforced at the module level.

## Commit History

| Commit | Day | Summary |
|---|---|---|
| `e67a1a4` | Day 1 | Scaffold, cashflow engine, YAML rules |
| `5ca7f9c` | Day 2 | AIPSS real-fixture validation — engine matches G8WAY to the penny |
| `7f21d76` | Day 3 | 1120-S extractor with M-1 Line 1 + Form 4562 rules |
| `9ba089f` | Day 4 | 1040 extractor with K-1 dedupe for global DSCR |
| `a33130b` | Day 5 | Credit report tri-merge parser (Merchants Credit Bureau RMCR) |
| `2b2f50a` | Day 6 | OCR preprocessor + two-pass layout-tolerant extractors |
| `b197f2e` | Day 6.5 | IRS transcript extractor + reconcile gaps reporter |
| `0cfd73e` | Day 7 | OCR quality profiles + PFS 413 + memo template + deal-type detector |
| `b9a09ab` | Day 8 | Column-aware PFS + memo renderer + LLM narrative hooks + E2E demo |
| `3788b6d` | Day 9 | OCR comma fix + Anthropic client + G8WAY reader + debt schedule extractor |
| `f31bb5f` | — | BUILD_STATUS.md doc |
| `8b0e8e2` | **Day 10** | **Multi-program architecture (SBA + CDFI), CIF template, OCR space-comma fix** |
| `bec6551` | **Day 10.5** | **PFS sign fix, Schedule C extractor, G8WAY program-aware reader, entity name extraction** |

## Module Inventory

### Core routing + math (no LLM allowed)

- **`underwriteos/program.py`** — *(Day 10)* Program-aware routing. `Program` dataclass, `PROGRAMS` registry (`sba_7a_colony`, `sba_7a_generic`, `cif_cdfi`, `cdfi_generic`). `detect_program(paths, hints)` with CIF > Colony > SBA-generic > default-Colony priority. `load_policy(program, config_dir)` merges per-program YAML files in order (e.g. SOP 50-10 then Colony Bank overrides).
- **`underwriteos/cashflow.py`** — DSCR, global DSCR, ADS, rate-shock stress, bank-adjusted net income.
- **`underwriteos/reconcile.py`** — Deal-level gaps reporter. Required-document matrix per deal type. Flags null critical fields, OCR noise, stale returns. Returns a ready/not-ready verdict.
- **`underwriteos/deal_type.py`** — Filename-based deal type classifier. Priority: cdfi > acquisition > startup > refi > expansion > default(refi).
- **`underwriteos/fixtures.py`** — AIPSS golden fixture loader for regression tests.

### Document extractors

- **`underwriteos/extract/ocr.py`** — `ocrmypdf` + `tesseract` wrapper. Three quality profiles (fast / standard / high). `postprocess_ocr_text()` rejoins thousands-separated numbers + fixes space-after-comma artifacts (`"466, 391."` → `"466,391."`). Line-number fusion stripping researched and deferred to tesseract TSV layout fix (false positives on legit values like `1,268,644`).
- **`underwriteos/extract/tax_return_1120s.py`** — Two-pass label-anchor 1120-S extractor. M-1 Line 1 preferred over Line 22. Form 4562 Part IV Line 22 preferred over Line 14. *(Day 10.5)* Entity name extraction from page-1 Name field (primary) with page-2+ continuation header fallback. Small-int filter architecture documented: anchor-line values are positional (no filter needed), fallback/next-line values use `_first_money_on_line` which applies ≥3-digit or comma/negative filter.
- **`underwriteos/extract/tax_return_1040.py`** — Two-pass 1040 extractor with K-1 dedupe. *(Day 10.5)* **Schedule C extraction** for sole-prop/disregarded-entity years: business_name, NAICS, gross_receipts, COGS, depreciation, total_expenses, net_profit_loss. Maps `net_income_preferred` and `depreciation_preferred` for cashflow.py compatibility.
- **`underwriteos/extract/irs_transcript_1040.py`** — IRS Record of Account / Return Transcript parser.
- **`underwriteos/extract/credit_report.py`** — Tri-merge credit report parser (Merchants Credit Bureau RMCR).
- **`underwriteos/extract/pfs_413.py`** — Column-aware SBA Form 413 extractor. *(Day 10.5)* Parenthetical negative support (`(52,345)` → `-52345`). Net worth cross-check: computed `total_assets - total_liabilities` with ±$1 rounding tolerance; overrides extracted value when they disagree. New `net_worth_source` field tracks provenance.
- **`underwriteos/extract/g8way.py`** — **READ ONLY.** *(Day 10.5 rewrite)* Program-aware sheet selection. Primary: `DSCR (UW)` (authoritative per TTH Day 10 findings). Fallback chain: `Global DSCR (UW)` → `Executive Summary` → `Boarding Sheet` → USDA sheets. Caller can pass `primary_sheet` + `fallback_sheets` from `Program` dataclass. New snapshot fields: `sheet_used_for_dscr`, `gross_receipts_y1`, `net_income_y1`, `cash_flow_y1`, `annual_debt_service`. Identity search checks `Boarding Sheet` + `Executive Summary` + USDA sheets, tries "applicant" label as fallback.
- **`underwriteos/extract/debt_schedule.py`** — Business debt schedule PDF extractor. Feeds ADS into DSCR.

### Memo engine

- **`underwriteos/memo/template.py`** — Colony Bank 32-section canonical spine. *(Day 10)* Added `get_template_for_program(program_key)` router: `"colony_bank"` → 32-section SBA spine, `"cif"` → 12-section CIF spine. Old `get_template(deal_type)` preserved for back-compat.
- **`underwriteos/memo/template_cif.py`** — *(Day 10)* CIF lean 12-section spine (header → terms → S&U → business overview → request summary → loan readiness → global cash flow → collateral → net risk → S/W → conditions → signature). No SBA eligibility, no existing SBA loans, no rate-shock.
- **`underwriteos/memo/renderer.py`** — `python-docx` renderer with per-section render types. Teal brand color. `[MISSING]` tags for gaps.
- **`underwriteos/memo/narrative.py`** — LLM narrative hooks. Four builders: loan purpose, project summary, strengths/weaknesses, conditions.
- **`underwriteos/memo/anthropic_client.py`** — Thin Anthropic SDK adapter. Audit JSONL log (gitignored, contains deal PII).

### Config

- **`config/rules_sba_sop_50_10.yaml`** — SBA SOP 50-10-8 hard stops. Final authority — overrides any lender profile.
- **`config/rules_colony_bank.yaml`** — Colony Bank SBSL thresholds (1.25x DSCR, 1.10x Global, 675 FICO, 10% equity, etc.).
- **`config/rules_cdfi_standard.yaml`** — CDFI baseline (1.15x DSCR, 1.05x Global, 600 FICO, 5% equity). Mission-driven lender defaults.

### Scripts

- **`scripts/run_mirzai_e2e.py`** — End-to-end demo: Mirzai bundle → extract → reconcile → draft memo `.docx`.

## Test Suite (94/94 green)

```
tests/test_cashflow.py                 — DSCR math golden cases
tests/test_extract_1040.py             — 1040 extractor + K-1 dedupe + Schedule C (5 tests)
tests/test_extract_1120s.py            — 1120-S extractor + M-1/4562 rules + entity name
tests/test_extract_credit_report.py    — Tri-merge credit report parser
tests/test_extract_pfs_413.py          — Form 413: column-aware + parenthetical neg + cross-check (5 tests)
tests/test_real_fixture.py             — AIPSS golden regression
tests/test_reconcile.py                — Deal-level gaps reporter
tests/test_deal_type.py                — Filename-based deal classifier
tests/test_memo_template.py            — Colony Bank template + overrides
tests/test_memo_renderer.py            — python-docx renderer
tests/test_memo_narrative.py           — LLM narrative hooks + default generator guard
tests/test_anthropic_client.py         — Anthropic adapter (fake SDK via monkeypatch)
tests/test_ocr_postprocess.py          — Rejoin + space-after-comma fix (12 tests)
tests/test_g8way.py                    — G8WAY snapshot reader: USDA fallback + DSCR(UW) priority + program override (5 tests)
tests/test_debt_schedule.py            — Business debt schedule extractor
tests/test_program.py                  — Program detection priority + policy load/merge + template routing (10 tests)
```

## Validated On Real Deals

- **Advanced Integrated Pain & Spine (AIPSS)** — Golden fixture. Engine matches G8WAY and the signed Colony Bank credit memo to the penny. PFS 413 all fields correct.
- **Mirzai Group / Munchies LLC** — Acquisition. Seller 1120-S extracted cleanly.
- **Mirzai principal** — IRS Record of Account. AGI $223,952, taxable income $155,802, MFJ, SE income $24,101.
- **Tropical Treasure Hunt (TTH)** — Scanned tax returns + G8WAY analysis. Deal was never approved (discarded as training fixture). G8WAY `DSCR (UW)` sheet confirmed as authoritative cash flow source. Entity name typo confirmed. Day 10 TTH findings documented in `docs/DAY_10_TTH_FINDINGS.md`.

## Day 11+ Queue

- Colony Bank SBA deal end-to-end walkthrough (Keith providing deal when ready)
- Zefo's CIF completion (paused — missing docs, awaiting Akem response on term/program)
- Tesseract TSV layout output (proper line-number fusion fix)
- First Claude Agent SDK loop wrapping pipeline as tools
- SQLite deal-state table (shared memory for agent work)
- Anthropic narrative end-to-end run with review loop
- UCC lien search integration
- M&E appraisal normalizer
- CLI + config surface (`underwriteos run <deal_dir>`)

## Architecture Rules (Do Not Violate)

1. **LLM boundary.** Claude API only for classification/narrative/risk ID. Never for numeric math.
2. **No PII in Git.** `.gitignore` blocks `Inbox/`, `Outbox/`, `Archive/`, `*.pdf`, `*.xlsx`, `*.docx`, `out/narrative_audit/`.
3. **YAML-driven policy.** Per-program YAML files in `config/`, merged by `program.load_policy()`. Never hardcode a threshold in Python.
4. **G8WAY workbooks are read-only.** `openpyxl` drops .wmf images and data validation. `extract/g8way.py` only reads cached values.
5. **Keys from env vars.** `ANTHROPIC_API_KEY`, `UNDERWRITEOS_OCR_CLEAN`. Never hardcoded or committed.
6. **Push workflow.** Sandbox writes files. Keith runs `git add/commit/push` from Mac Terminal.
7. **Agent architecture.** Agents are orchestration layer ON TOP of deterministic engine. Python modules are tools the agent calls. Math never moves into the LLM.

## Pickup Phrase

`start Colony Bank deal walkthrough — <deal name>` or `start day 11 with <task>`
