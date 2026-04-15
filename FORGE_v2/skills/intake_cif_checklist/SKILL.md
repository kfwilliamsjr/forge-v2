---
name: intake_cif_checklist
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 1-extraction
depends_on: []
policy_refs: [policy/cif_procedures.yaml]
---

# SKILL: intake_cif_checklist

## Layer 1 — Trigger Description
Use when a new CIF borrower enters the pipeline and must be screened against the CIF intake checklist (3 product types: Regular Loans ≤$250K, VI Leap Fund Grants $5K-$15K, Festival Loans microloans). Produces a completed checklist and readiness score.

## Layer 2 — Negative Trigger
- Do NOT use for SBA broker deals (use `extract_sba_deal_parameters`).
- Do NOT use if borrower has not signed CIF engagement letter.
- Do NOT estimate missing checklist items — HALT and draft doc request (route to `draft_cif_doc_request_email`).
- Do NOT classify product type if borrower has not declared intended use (ask, don't guess).

## Layer 3 — Input Schema
| Field | Type | Required | Source |
|-------|------|----------|--------|
| deal_id | string | Yes | router |
| borrower_legal_name | string | Yes | intake form |
| borrower_entity_type | enum | Yes | intake form |
| product_type_requested | enum | Yes | intake | `"regular_loan"` \| `"vi_leap_grant"` \| `"festival_loan"` |
| requested_amount | currency | Yes | intake form |
| documents_provided | list[string] | Yes | ShareFile / inbox |
| engagement_letter_signed | bool | Yes | docusign |

## Layer 4 — Procedure

### Step 1 — Validate inputs
- HALT if `engagement_letter_signed = false`. Route to `draft_outbound_email` with subject template `ENGAGEMENT_PENDING`.
- HALT if `product_type_requested` is not one of the three valid enums. Do NOT infer from request amount or language. Ask Keith.

### Step 2 — Load product-specific checklist
Read `policy/cif_procedures.yaml → intake_checklists.{product_type}`. Checklists:

**festival_loan** (11 items, Sections I–II): Loan Application, Festival Readiness Assessment Form, Credit Report (CIF pulls), Photo ID, Entity Docs, Business License/Vendor Permit, W-9, Bank Statements (3mo biz + 3mo personal), Most Recent Tax Return, Personal Financial Statement, Vendor invoices/cost estimates.

**vi_leap_grant** (10 items, Essential + Vendor): Grant Application, Business Plan/Narrative, Entity Docs, Business License, Most Recent Tax Return, Bank Statements (3-6mo), Photo ID, Vendor Quotes/Invoices, Vendor Contracts, Wiring Instructions.

**regular_loan** (13 standard + 5 construction-conditional): Loan Application (CIF format), Business Plan, Entity Formation, Business License, 3yr Business Tax Returns, 3yr Personal Tax Returns, YTD P&L, Balance Sheet, Bank Statements (6-12mo biz), PFS, Debt Schedule, Credit Report (CIF pulls), Photo ID. If construction: Construction Budget, Contractor Bids, Permits, Environmental Reports, Plans/Blueprints.

### Step 3 — Map documents_provided to checklist items
Use filename pattern matching (policy YAML carries the regex table):
- `application|app` → Loan/Grant Application
- `readiness` → Festival Readiness
- `credit` → Credit Report (mark "CIF to pull" if absent)
- `ID|license|DL|passport` → Photo ID
- `articles|bylaws|operating|formation|DBA` → Entity Docs
- `W-?9` → W-9
- `bank|statement` → Bank Statements
- `tax|1040|1120|1065` → Tax Returns
- `PFS|personal.financial` → PFS
- `invoice|quote|estimate` → Vendor Invoices
- `contract` → Vendor Contracts
- `wiring|wire` → Wiring Instructions
- `P&L|profit|income.statement` → P&L
- `balance.sheet` → Balance Sheet
- `debt.schedule` → Debt Schedule
- `business.plan` → Business Plan

Mark each item: `HAVE` | `MISSING` | `BLOCKER` (blocker = missing AND required before underwriting can proceed: application, credit, tax returns, entity docs).

### Step 4 — Compute readiness score
`readiness_score = (items_have / items_required) * 100`, rounded to integer.
- ≥90: ready for cash flow.
- 70-89: flag, draft doc request for gaps.
- <70: HALT, draft full doc request, do not proceed to cash flow.

### Step 5 — VI Leap Grant-specific check
If `product_type = vi_leap_grant`, compute `grant_to_revenue_ratio = requested_amount / trailing_12mo_revenue` (if revenue known). If >2.0x, add flag `grant_exceeds_2x_revenue` to output — readiness concern, not automatic decline.

### Step 6 — Regular Loan cap check
If `product_type = regular_loan` AND `requested_amount > 250000`, HALT. CIF regular loan cap is $250K. Surface message: "Amount exceeds CIF regular loan cap. Options: restructure to ≤$250K, or refer out."

### Step 7 — Write audit entry
Append to `audit/{deal_id}.jsonl` with full checklist state, readiness score, product_type, policy_version.

### Step 8 — Return output
Per Layer 5 schema. If `readiness_score < 70` OR any BLOCKER present, set `next_action = "draft_doc_request_email"` and pass missing_items to `draft_cif_doc_request_email`.

## Layer 5 — Output Schema
```json
{
  "status": "ok" | "halt" | "flag",
  "deal_id": "...",
  "product_type": "festival_loan",
  "checklist": [
    {"item": "Tax Return 2024", "present": true, "source": "ShareFile/tax2024.pdf"},
    {"item": "Bank statements (3 mo)", "present": false, "source": null}
  ],
  "readiness_score": 78,
  "missing_items": ["Bank statements (3 mo)"],
  "next_action": "draft_doc_request_email",
  "audit_ref": "..."
}
```

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Flesh out from legacy cif-deal-intake after FORGE copy. |
