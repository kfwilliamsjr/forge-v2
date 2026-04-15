---
name: write_committee_memo
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 4-output
depends_on: [calculate_business_cash_flow, calculate_global_cash_flow, run_cif_stress_tests]
policy_refs: [policy/cif_procedures.yaml]
---

# SKILL: write_committee_memo

## Layer 1 — Trigger Description
Use to generate the full CIF Loan Committee memo for Regular Loans up to $250K. Produces a structured DOCX + PDF with executive summary, borrower profile, cash flow analysis, risk factors, conditions, and recommendation. Goes to Akem for review before committee (Pat Morris / Ronnie Johnson / Omi Pennick).

## Layer 2 — Negative Trigger
- Do NOT use for Festival Loans (use `write_festival_report`).
- Do NOT use for Grants (use `write_grant_summary`).
- Do NOT generate narrative numbers that conflict with structured cash flow outputs — every dollar and ratio in narrative must trace to `calculate_*_cash_flow` outputs.
- Do NOT forward to committee directly — memo approval workflow is Keith → Akem → committee.
- Do NOT skip PDF generation (use `generate_loan_report_pdf.py` with teal branding).

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| deal_data_json_path | file | Yes |
| cash_flow_output | object | Yes |
| global_cash_flow_output | object | Yes |
| stress_test_output | object | Yes |
| risk_factors | list[string] | Yes |
| proposed_conditions | list[string] | Yes |
| recommendation | enum | Yes |

## Layer 4 — Procedure

### Step 1 — Pre-flight
HALT if `deal_data_json.request.deal_type != "regular_loan"`. HALT if `requested_amount > 250000` (CIF regular loan cap). HALT if any of: `cash_flow_output.base_dscr`, `global_cash_flow_output.global_dscr`, `stress_test_output` (all 4 scenarios) is null.

### Step 2 — Build DOCX (8-15 pages)

1. **Executive Summary** (1 paragraph) — Who, what, how much, why, recommendation. Example: "CIF is evaluating a $185,000 regular loan to JJ Creationz LLC (St. Thomas, USVI) to fund equipment purchase and working capital. Base DSCR 1.34x, Global DSCR 1.18x, all stress tests pass. Recommendation: APPROVE WITH CONDITIONS."

2. **Borrower Profile** — Entity history, ownership table (% ownership, role, FICO, net worth), management experience, industry.

3. **Loan Request** — Amount, term, rate, use of proceeds itemized, collateral offered.

4. **Credit Analysis** — Detailed scores (all 3 bureaus), derogatory items line-by-line, LOE if any character items (flag need for `screen_sba_character_loe_needed` run if applicable).

5. **Financial Analysis**
   - 5a. Business Financial Summary — 3-year revenue, expenses, trends
   - 5b. Personal Financial Summary — income, assets, liabilities (from PFS)
   - 5c. Cash Flow Analysis — full 3-layer model with every line item visible
   - 5d. DSCR Summary Table — base + 4 stress tests

6. **Collateral Analysis** — Asset coverage, margin analysis per SBA/CIF collateral margins (85% improved CRE, 50% unimproved, 75% new M&E, 50% used M&E NBV).

7. **Five Cs Assessment** — Character / Capacity / Capital / Collateral / Conditions. 1 paragraph each.

8. **Risk Factors & Mitigants** — Numbered list.

9. **Conditions of Approval** — Numbered, CIF-standard (insurance naming CIF additional insured, UCC-1 on business assets, personal guarantee from 20%+ owners, no material adverse change) plus deal-specific.

10. **Recommendation** — Approve / Conditional / Decline with rationale tied to DSCR + Five Cs.

11. **Appendices** — Supporting schedules, cash flow detail.

### Step 3 — Number-verification sweep (hallucination guard — MANDATORY)
Before writing to disk, extract every numeric token from the DOCX narrative (currency, percentage, ratio). For each, require a match in structured input (`cash_flow_output`, `global_cash_flow_output`, `stress_test_output`, `deal_data_json.financials`). If any narrative number lacks a traced source, HALT and emit `unverified_narrative_number` with the token list. NO memo ships with unverified figures.

### Step 4 — XLSX workbook (required)
Generate G8WAY-style cash-flow workbook per `write_festival_report` Step 4 specs. 6 sheets: Cover / Business CF / Personal CF / Liabilities / BDO Global CF / Stress Test. Formula-driven, cross-sheet refs.

### Step 5 — PDF via approved script
`generate_loan_report_pdf.py {docx} {pdf}`. No other path.

### Step 6 — File management
Prior versions → `Report/Old Drafts/`. Save:
- `Report/Loan_Committee_Memo_{Borrower}_{YYYY-MM-DD}.docx`
- `Report/Loan_Committee_Memo_{Borrower}_{YYYY-MM-DD}.pdf`
- `Report/{Borrower}_Cash_Flow_Workbook_{YYYY-MM-DD}.xlsx`

### Step 7 — Approval workflow routing
Return 3 file paths + recommendation. Do NOT send. Keith reviews XLSX, says "send it" → invoke `draft_outbound_email`:
- Stage A (Submit to Akem): TO=akem.durand@cifvi.org, CC=[nikky.cole@cifvi.org, keith@swiftcapitoptions.com], all 3 files attached. Pipeline → `submitted_to_akem`.
- Stage B (Committee, only after Akem approves): TO=[pat.morris, ronnie.johnson, omi.pennick]@cifvi.org, CC=[akem, nikky, keith]. Pipeline → `submitted_to_committee`.

### Step 8 — Audit
Log: deal_id, policy_version, file hashes × 3, verified-number-count, flagged-number-count, recommendation, stage transition.

## Layer 5 — Output Schema
Returns DOCX + PDF paths + hallucination-check report (all numbers traced or flagged).

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy cif-memo-writer. Adds hallucination guard from Master Guide. |
