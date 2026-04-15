# Day 6 Training Learnings — 3 New Deals

*Date: 2026-04-08*
*Deals reviewed: RES Energy Solutions (SBA/Colony), Mirzai Group dba Munchies (SBA/Colony), Tropical Treasure Hunt (CIF/CDFI)*

## Executive Summary

The AIPSS-trained extractors (Days 3–5) overfit harder than expected. Running them against 3 new deals produced **near-total extraction failure** on every tax return. This is the expected outcome of training against one deal, and the fix is mechanical, not architectural. The engine math, YAML policy model, and reconciliation design remain sound — the break is at the extractor layer, exactly where it should be.

**What broke:** 100% of tax return extractions on new deals returned mostly-null fields.
**Root cause:** Three separate document format classes the extractors don't handle yet.
**Fix scope:** Add an OCR preprocessing layer, a transcript extractor, and loosen the page-1 line regex. None of this touches the cashflow engine or policy gates.

## Findings

### Finding #3 — Scanned image PDFs require an OCR preprocessing pass

**Affected documents:**
- All 3 Tropical Treasure Hunt business returns (2022, 2023, 2024)
- TTH 2024 personal return
- Munchies LLC seller return (2024 1120-S)

**Symptom:** `pdftotext -layout` returns 7–10 bytes (empty) on these files. They're image-only scans with no text layer.

**Fix:** Add `underwriteos/extract/ocr.py` that runs `ocrmypdf --force-ocr --skip-big 50` before handing to the form extractors. `ocrmypdf` is already installed in the sandbox. OCR time measured at ~21 seconds for a 4-page business return. Tesseract OCR quality is good enough on the TTH 2024 return that Schedule M-1 Line 1 extracted correctly ($60,262) on the first try after OCR — the Day 3 rule held. Other lines need looser regex (see Finding #5).

**Pipeline change:** Classifier stage must detect `len(pdftotext output) < threshold` → route through OCR → then extract. This needs to be implicit in the pipeline, not a separate user action.

### Finding #4 — IRS account transcripts are a separate document class

**Affected documents:**
- Mirzai Group principal 2024 joint return (IRS "Record of Account" transcript, not a filed 1040)

**Symptom:** Zero fields extract. Document is a labeled text dump, not a form layout.

**Format reality:**
```
Adjusted gross income:                              $223,952.00
Taxable income:                                     $155,802.00
Total wages:                                        $24,000.00
Total self employment tax:                          $3,688.00
SE taxable income taxpayer:                         $24,101.00
```

**Fix:** Build `underwriteos/extract/irs_transcript_1040.py` as a separate module. Transcripts have advantages over filed returns for underwriting: they're IRS-verified (can't be fabricated), they show balance due and penalties (character signal — Mirzai owes $26,921 including penalties), and they include the received date (filed 9/27/2025 for tax year 2024 — late-filed).

**Underwriting signal learned:** The Mirzai transcript shows **penalty $882 + late payment $839 + interest $947 = $2,668 in IRS accruals** and an installment agreement established 11/15/2025. This is a character finding that would go in the Letter of Explanation section of the memo. The engine should flag transcripts with `charge_off_balance > 0` or `installment_agreement == True` as character items requiring borrower explanation.

### Finding #5 — 1120-S/1040 regex is too strict for layout variance

**Affected documents:**
- TTH 2024 business return (post-OCR) — only M-1 Line 1 matched
- Mirzai seller return — nothing matched

**Root cause:** Current regex patterns require the exact spacing pattern `^N<desc>...N<value>$`. Different tax prep software (Drake, Lacerte, ProSeries, ProConnect, TurboTax Business) produces different column widths and dot-fill counts. Post-OCR output adds another layer of spacing variance.

**Fix:** Rewrite extractor as a two-pass scan. Pass 1 anchors on the line description (e.g., "Compensation of officers"). Pass 2 pulls the rightmost integer on the same line. This is how humans read tax returns — find the label, look right.

### Finding #6 — Deal type drives the document set and analytical frame

**Three deal types now in the training set, each teaching something different:**

| Deal | Type | What it teaches |
|------|------|-----------------|
| AIPSS | Operating biz refi/growth ($1.7M) | Standard BANI + global DSCR baseline |
| Mirzai/Munchies | Business acquisition ($352,800) | Seller return analysis + buyer personal, purchase price allocation, going-concern validation |
| Tropical Treasure Hunt | CDFI growth loan ($300–350K, incomplete) | Missing-items handling, CDFI relaxed policy profile, S-corp election conversion mid-history |
| RES Energy | Large SBA CRE ($4.88M) | Upper-end deal complexity, oil & gas NAICS, committee-level approval chain |

**Acquisition deals need a different document topology than refi deals.** In an acquisition, the BUYER's personal returns and the SELLER's business returns are the two relevant document streams, not the borrower's own history. The extractor chain doesn't currently encode that relationship.

**Fix:** Add `deal.type` to the meta layer with values `refi | expansion | acquisition | startup | cdfi`. Document requirements and reconciliation rules branch on this field.

### Finding #7 — TTH is deliberately incomplete and teaches the "gaps report" feature

Keith flagged TTH as **not something he would approve** and noted the G8WAY is incomplete. This is a *valuable* training signal because the V1 pipeline promise is "80% memo draft with a gaps list." An incomplete deal should produce:

1. A `gaps_report.json` listing every missing field, the document that should contain it, and whether the gap is a hard stop (can't proceed) or a soft flag (can proceed with LOE).
2. A memo draft that includes a "Missing Items" section at the top, populated from the gaps report.
3. No fabricated numbers. Missing fields stay missing.

The current pipeline doesn't have a gaps reporter. **This is a Day 6 addition now, not a Day 10 addition.**

### Finding #8 — Colony Bank loan reports are a standardized 21-page template

Both Mirzai and RES loan reports follow an identical Colony Bank template:
1. Cover / Package Name / signatures
2. Package Summary (NAICS, risk rating, referral, fees, SOP version, 912 issue flag)
3. Borrowers and Guarantors tables
4. Loan Terms (rate type, amount, term, amortization)
5. Sources & Uses
6. Financial Analysis (BANI, DSCR, global DSCR)
7. Collateral analysis
8. Character / Credit analysis
9. Risk rating rationale
10. Conditions and Covenants

**This IS my memo template.** Day 9 should not invent a template — it should extract this structure from the existing Mirzai/RES/AIPSS reports and templatize it with Jinja. Keith already knows what "banker-grade" looks like — it looks like these reports. The LLM's job is narrative voice inside the known structural slots, nothing more.

## How this improves the process

### Immediate changes (Day 6 scope, before any new engine work)

1. **`extract/ocr.py`** — Classifier + ocrmypdf preprocessing. Any PDF with < 100 bytes of text after pdftotext goes through OCR automatically.
2. **`extract/irs_transcript_1040.py`** — New module for IRS Record of Account format. Captures AGI, taxable income, wages, SE income, balance due, penalties, installment agreement status. Outputs the same schema as `tax_return_1040.py` so downstream code doesn't care about the source format.
3. **Rewrite `tax_return_1120s.py` and `tax_return_1040.py`** to use two-pass line scanning (label anchor → rightmost int on line). This kills the AIPSS overfit.
4. **Add `deal.type` meta field** to the fixture schema. Default `refi`, new values `acquisition | startup | cdfi | expansion`.
5. **Build `reconcile.py` with a gaps reporter**. Output: `{"resolved": {...}, "gaps": [{"field": "...", "source_expected": "...", "severity": "hard|soft"}, ...]}`.
6. **Extract the Colony Bank memo template** from the Mirzai loan report PDF into `templates/memo_colony_bank.jinja`. Use as the Day 9 starting point.

### Test coverage additions

Golden fixtures to add (redacted JSON, no PII committed):
- `fixtures/mirzai_munchies_acquisition.json` — tests acquisition deal type, IRS transcript handling, character item flagging
- `fixtures/tth_cdfi_incomplete.json` — tests gaps reporter, CDFI policy profile, OCR preprocessing
- `fixtures/res_energy_large_sba.json` — tests large deal handling, committee approval chain structure

Each fixture becomes a regression test. The test suite grows from 18 to ~25 by end of Day 6.

### Rules baked in from this review (add to reconcile.py)

| Rule | Source | Applies to |
|------|--------|------------|
| IRS transcript `installment_agreement == True` → character flag, require LOE | Mirzai | all transcripts |
| IRS transcript `balance_due + penalties > 0` → character flag, require payment plan evidence | Mirzai | all transcripts |
| Scanned PDFs auto-route through ocrmypdf before extract | TTH, Munchies | all extractors |
| Deal type = acquisition → seller returns analyze business quality, buyer returns analyze repayment ability; do NOT combine their personal incomes | Mirzai | acquisition deals only |
| Incomplete G8WAY (any required field missing) → memo draft includes Missing Items section, does NOT fabricate numbers | TTH | all deals |
| Deal amount > $2M → committee approval chain with 5 named reviewers in memo footer | RES | large SBA deals only |

## What the 3 deals did NOT expose

Worth naming explicitly so we don't assume the system is complete:

- **No partnership returns (1065)** yet. All 4 training deals are 1120-S or sole prop.
- **No Schedule C-only borrowers.** AIPSS had 1120-S flow-through; Mirzai is an acquisition, not a Schedule C analysis.
- **No multi-entity borrowers.** No training deal has borrower with 2+ operating businesses.
- **No real estate appraisals** in the document set. Collateral analysis for CRE deals isn't calibrated.
- **No bank statement spreads.** Mirzai has one bank statement referenced for a cash adjustment but we haven't parsed it yet.
- **No construction draw analysis.**
- **No franchise agreements** or FDD reviews.

These are Phase 2 training priorities, not blockers.

## Honest assessment

The extractors are less robust than Day 5 suggested. The cashflow engine, YAML policy layer, and reconciliation design are still sound — those didn't touch any of the broken paths. One day of extractor hardening (pass-1-label, pass-2-number + OCR preprocessor + transcript module) rebuilds the extractor layer to handle all 4 deals in the training set instead of 1. That's the honest answer to "how do we improve the code as we go" — we catch format variance early by running it through multiple deals before we build the next layer on top, which is exactly the sequencing we chose.

**Next action:** Build the Day 6 extractor hardening before PFS + reconciliation layer, because PFS reconciliation depends on extractors actually working across document formats.
