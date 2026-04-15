---
name: write_grant_summary
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 4-output
depends_on: [intake_cif_checklist]
policy_refs: [policy/cif_procedures.yaml, policy/vi_leap_grant_rules.yaml]
---

# SKILL: write_grant_summary

## Layer 1 — Trigger Description
Use to generate the VI Leap Fund Grant summary (CIF grant product, $5K-$15K, non-repayable). Produces a DOCX + PDF following CIF grant template. Grant decisions emphasize need, impact, and eligibility — not cash flow / DSCR.

## Layer 2 — Negative Trigger
- Do NOT use for loan products (Festival or Regular).
- Do NOT compute DSCR — grants are not debt-repaid.
- Do NOT omit eligibility screen (USVI residency, disadvantaged business criteria).
- Do NOT approve without readiness_score ≥ CIF grant threshold from policy YAML.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| borrower_narrative | string | Yes |
| eligibility_evidence | list[file] | Yes |
| impact_use_of_funds | string | Yes |
| requested_grant_amount | currency | Yes |

## Layer 4 — Procedure

### Step 1 — Eligibility screen
Load `policy/vi_leap_grant_rules.yaml`. Verify:
- USVI-based business (entity state = VI, or principal place of business VI)
- Disadvantaged business criteria met (minority / women / veteran / LMI geography per policy)
- Grant amount within $5K-$15K range
- Entity status compliant (or noted as "entity formation to be funded by grant" per standard condition)
- readiness_score ≥ policy threshold (default 70)

HALT if any eligibility gate fails. Emit `eligibility_fail` with specific gate name.

### Step 2 — Grant-to-revenue readiness flag
Compute `ratio = requested_grant_amount / trailing_12mo_revenue` (if revenue known). If >2.0x, add `grant_exceeds_2x_revenue` flag — readiness concern, not automatic decline. Surface prominently in memo.

### Step 3 — Compose DOCX (2-3 pages)
1. **Applicant Summary** — name, entity, grant amount, one-paragraph project description.
2. **Readiness Assessment** — financial health indicators (revenue trend, bank stability, entity maturity), grant-to-revenue ratio, readiness score.
3. **Credit Overview** — scores, derogatory items summary, credit-repair needs if relevant (not disqualifying for grants but committee context).
4. **Use of Funds** — itemized vendor breakdown: vendor name, item, amount, vendor-contract-status (executed / pending / none). Wiring-instructions-received flag per vendor.
5. **Entity & Compliance Status** — formation docs, business license, W-9, any compliance gaps.
6. **Recommendation** — Approve / Conditional / Decline with standard VI Leap conditions (vendor contracts executed before disbursement; wiring verified; vendor-direct disbursement; 6-month progress report; if entity not formed, portion allocated to formation).

### Step 4 — Formatting
Same CIF brand standards as festival report: teal headers #2E8B8B, Calibri 11pt, header "Community Impact Fund — VI Leap Fund Grant Summary", footer "Confidential — Prepared by Swift Capital for CIF Committee Review".

### Step 5 — PDF generation
Use `generate_loan_report_pdf.py`. XLSX is NOT required for grants (no DSCR model).

### Step 6 — File management
Move prior versions to `Report/Old Drafts/`. Save:
- `Report/VI_Leap_Grant_Summary_{Borrower}_{YYYY-MM-DD}.docx`
- `Report/VI_Leap_Grant_Summary_{Borrower}_{YYYY-MM-DD}.pdf`

### Step 7 — Update deal_data.json
`status = memo_drafted`, `deliverables.{docx,pdf}` populated, xlsx = null (grants don't require workbook).

### Step 8 — Audit + surface
Log all eligibility gates, flags, recommendation. Return summary to Keith for review before "send it".

## Layer 5 — Output Schema
Returns paths to DOCX + PDF + eligibility verdict.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. |
