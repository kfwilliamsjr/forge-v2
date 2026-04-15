# UnderwriteOS — 14-Day Execution Plan

**Goal:** Working prototype that ingests a borrower package from a ShareFile-synced inbox and outputs a complete spread, DSCR, policy gates, risk flags, missing-items list, and 80%-complete credit memo.

**Reference deal:** Advanced Integrated Pain & Spine Solutions LLC ($1,699,000 SBA 7(a), Y1 DSCR 1.23x, Y2 DSCR 1.25x).

| Day | Deliverable | Status |
|---|---|---|
| 1 | Repo scaffold, cashflow.py, tests passing, 3 YAML rule files | DONE |
| 2 | Document classifier (Claude API) — tags every file in a CIF deal folder | |
| 3 | Tax return extractor (1040, 1120-S, Schedule C) → schema |  |
| 4 | Credit report + bank statement extractor |  |
| 5 | Real-fixture validation: extract Advanced Integrated Pain financials from PDF, run cashflow, hit 1.23x/1.25x without calibration |  |
| 6 | Spread writer → spread.xlsx from G8WAY-derived template |  |
| 7 | **Checkpoint 1: end-to-end on one real deal, numbers only** |  |
| 8 | Policy gate engine — load YAML, evaluate hard stops + soft flags |  |
| 9 | Missing items detector + risk flagger (Claude) |  |
| 10 | Memo template (Jinja2) modeled on Pain & Spine memo |  |
| 11 | Memo generator — narrative via Claude, deterministic from schema |  |
| 12 | DOCX + PDF renderer wired to existing generate_loan_report_pdf.py |  |
| 13 | Folder watcher, debounce, re-run-on-edit, archive flow, run_log audit |  |
| 14 | **Demo: drop fresh CIF deal in inbox, walk away, return with full memo** |  |

## Build order rationale
Cash flow engine first because it must be perfect and has a known-good target. Extraction second because it's the highest-risk component and benefits from having validated downstream code to feed. Memo generation last because it depends on everything upstream.

## Hard rules during build
- No borrower documents committed to git, ever.
- No LLM in any math path.
- Every commit runs `pytest tests/`.
- Every change to a YAML rules file gets a one-line note in the commit message.

## Decisions still open
- Final repo name (working name: `underwriteos`).
- Memo voice second sample needed for triangulation if Pain & Spine alone isn't enough.
- ShareFile sync folder path on the production Mac.
