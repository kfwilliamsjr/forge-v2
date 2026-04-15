---
name: write_festival_report
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 4-output
depends_on: [calculate_business_cash_flow, calculate_global_cash_flow, run_cif_stress_tests]
policy_refs: [policy/cif_procedures.yaml]
---

# SKILL: write_festival_report

## Layer 1 — Trigger Description
Use to generate the Festival Loan report (CIF microloan product, <$50K typical). Produces a DOCX + PDF deliverable following CIF festival loan template. Festival loans are cash-flow-based with lighter documentation than Regular Loans.

## Layer 2 — Negative Trigger
- Do NOT use for Regular Loans ≤$250K (use `write_committee_memo`).
- Do NOT use for VI Leap Fund Grants (use `write_grant_summary`).
- Do NOT generate without at least one year of business tax return or 6 months of bank statements.
- Do NOT omit PDF — finalized approvals require both DOCX and PDF (CLAUDE.md hard rule).
- Do NOT insert narrative figures that don't match the structured cash flow output (consistency check required).

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| deal_data_json_path | file | Yes |
| cash_flow_output | object | Yes |
| stress_test_output | object | Yes |
| output_folder | string | Yes |

## Layer 4 — Procedure

### Step 1 — Validate readiness
HALT if `cash_flow_output.base_dscr` is null, OR `stress_test_output` missing any of 4 scenarios, OR `deal_data_json.request.deal_type != "festival_loan"`.

### Step 2 — Compose DOCX (3-5 pages)
Sections in order:

1. **Borrower Summary** — Legal name, DBA, entity type, booth/festival name, loan amount, use of proceeds (one paragraph).
2. **Credit Profile** — TU/EX/EQ scores, derogatory items table, character assessment narrative (borrower-supplied LOE referenced if present).
3. **Cash Flow Analysis** — 3-layer summary (business / personal / global) with source-document citations. Living expense floor and addback rules called out.
4. **DSCR Summary Table** — Base + 4 stress scenarios (from `run_cif_stress_tests` output). Teal header (#2E8B8B), light-teal labels (#D5E8E8).
5. **Sources & Uses** — Loan amount vs. itemized vendor costs. Identify which items are vendor-direct disbursement.
6. **Risk Assessment** — Five Cs in condensed form (2-3 sentences each).
7. **Recommendation** — Approve / Conditional / Decline with numbered conditions (pull from policy standard conditions for festival_loan).

### Step 3 — Formatting standards
- Font: Calibri 11pt body, 14pt title, 12pt headings
- Header: "Community Impact Fund — Festival Loan Report"
- Footer: "Confidential — Prepared by Swift Capital for CIF Committee Review"
- Tables: Teal header #2E8B8B, light-teal labels #D5E8E8, white body
- Page numbers: bottom center
- Margins: 1 inch all sides

### Step 4 — Generate cash-flow workbook (XLSX, required)
Call `xlsx` skill. Sheets: Cover, Business Cash Flow (up to 4 periods; mark unavailable "UNAVAILABLE"), Personal Cash Flow, Liabilities (Credit Report), BDO Global Cash Flow (formula-driven cross-sheet refs), Stress Test. All formulas — no hardcoded values. Match JJ Creationz formatting palette: dark-blue headers #1F3864, light-blue subtotals #D5E8F0, green totals #E2EFDA, yellow assumption cells #FFF2CC.

### Step 5 — Consistency check
Compare every numeric appearing in DOCX narrative against same field in cash_flow_output and stress_test_output. If mismatch, HALT and emit `narrative_numbers_divergence` with field list. No memo ships with inconsistent numbers.

### Step 6 — PDF generation
Run `~/Desktop/Swift Capital Underwriting/Templates/generate_loan_report_pdf.py {docx} {pdf}`. This script reads DOCX cell colors and renders teal correctly. Do NOT use plain ReportLab — that was the root cause of the TTH 3/31 color bug.

### Step 7 — File management
Move any prior DOCX/PDF/XLSX in `Report/` to `Report/Old Drafts/`. Save new as:
- `Report/Festival_Loan_Report_{Borrower}_{YYYY-MM-DD}.docx`
- `Report/Festival_Loan_Report_{Borrower}_{YYYY-MM-DD}.pdf`
- `Report/{Borrower}_Cash_Flow_Workbook_{YYYY-MM-DD}.xlsx`

### Step 8 — Update deal_data.json
Set `status = memo_drafted`, `dates.memo_drafted = today`, `deliverables.{docx,pdf,xlsx}` paths populated.

### Step 9 — Write audit
Log: deal_id, file hashes of all 3 deliverables, dscr verdict, recommendation text, consistency-check result.

### Step 10 — Surface to Keith
Return summary with three file paths + DSCR + recommendation. Keith reviews the XLSX, confirms approval, then says "send it" → downstream `draft_outbound_email` (to Akem, CC Nikky+Keith) fires.

## Layer 5 — Output Schema
Returns paths to DOCX + PDF in `Deals_Swift Capital/{deal}/Report/`.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy cif-memo-writer (3 doc types → 3 skills). |
