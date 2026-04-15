---
name: calculate_business_cash_flow
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 2-calculation
depends_on: [extract_cif_financials]
policy_refs: [policy/cif_procedures.yaml, policy/sba_sop_50_10.yaml]
---

# SKILL: calculate_business_cash_flow

## Layer 1 — Trigger Description
Use when extracted business financial data (tax returns, P&L, bank statements) must be converted into a bank-adjusted cash flow figure for a CIF or SBA underwriting decision. Produces Net Income + addbacks = Cash Available for Debt Service.

## Layer 2 — Negative Trigger
- Do NOT use for personal cash flow (use `calculate_personal_cash_flow`).
- Do NOT use for global cash flow combining business + personal (use `calculate_global_cash_flow`).
- Do NOT estimate depreciation or interest if not explicitly on the tax return — HALT and request source doc.
- Do NOT apply CRE rent expense addback if the borrower does NOT own the operating real estate (addback requires ownership + replacement with debt service).
- Do NOT use on construction loans with no stabilized operating history.
- Do NOT use when fiscal year is partial (< 12 months) without proration disclosure.

## Layer 3 — Input Schema
| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| deal_id | string | Yes | router | — |
| borrower_legal_name | string | Yes | intake | — |
| entity_type | enum | Yes | tax return | `"sole_prop"` \| `"S_corp"` \| `"C_corp"` \| `"partnership"` \| `"LLC_disregarded"` |
| tax_year | int | Yes | tax return | e.g., 2025 |
| gross_revenue | currency | Yes | tax return | |
| net_income | currency | Yes | tax return | Line 21 (1120-S) or Schedule C Line 31 |
| depreciation | currency | Yes | tax return | — |
| amortization | currency | No | tax return | |
| interest_expense | currency | Yes | tax return | Business loan interest only |
| owner_compensation | currency | Conditional | tax return / W-2 | Required if S-Corp/C-Corp |
| one_time_expenses | currency | No | owner disclosure + supporting doc | Must have source doc |
| rent_paid_to_owner_re | currency | No | lease | Only if borrower owns CRE |
| new_debt_service_annual | currency | Yes | proposed loan terms | For DSCR downstream |

## Math Backend — underwriteos (DETERMINISTIC)

**HARD RULE: the LLM does NOT perform DSCR math.** All arithmetic routes through `underwriteos.cashflow` — a pure-Python, Decimal-based, fully tested engine (94 passing tests).

- Backend module: `Agentic_Overhaul/_legacy_forge/underwriteos/underwriteos/cashflow.py`
- Key functions: `amortized_payment()`, `bank_adjusted_cash_flow()`, `borrower_dscr()`, `global_dscr()`, `liquidity_ratio()`, `rate_shock_dscr()`
- Call pattern: build a JSON payload of inputs → shell out to `python3 -m underwriteos.cashflow` → read JSON result → write into deal_data + audit log.
- **Fallback rule:** if the Python backend is unavailable, HALT with `math_backend_unavailable` — never estimate DSCR from memory.
- Rounding: 2dp banker rounding on money, 2dp on ratios (Decimal, ROUND_HALF_UP).
- Audit: every call writes inputs + outputs + module version to `audit/{deal_id}.jsonl`.

## Layer 4 — Procedure

1. Validate all required inputs per Layer 3. If missing, HALT with field names.
2. Load CIF cash-flow addback rules from `policy/cif_procedures.yaml → business_cashflow.addbacks`.
3. Compute Base Cash Flow:
   ```
   base_cf = net_income + depreciation + amortization + interest_expense
   ```
4. Apply owner compensation policy per `policy/cif_procedures.yaml → addbacks.owner_compensation`:
   - **CIF lane:** NEVER add back. Owner comp flows to the personal layer via W-2/K-1. Full stop.
   - **SBA lane:** Case-by-case, gated on explicit `owner_compensation_addback: true` flag in the deal payload PLUS a documented rationale in `_note_owner_comp`. Default (flag absent or false) = NO ADDBACK.
   - **Never add back** when W-2 wages are already expensed on the tax return as market-rate salary AND the lender is not normalizing to industry average.
   - **Audit trail:** AIPSS_2026-03 and MIRZAI_2026-01 both have `owner_compensation_addback: false` — see the policy YAML `audit_cases` block for the reasoning on each.
5. Apply one-time addbacks ONLY if `one_time_expenses.source_doc` is present. If no source doc, skip and flag.
6. Apply rent-to-owner addback ONLY if `rent_paid_to_owner_re > 0` AND the loan proceeds are replacing that rent with a mortgage (verified from use_of_proceeds).
7. Compute Bank-Adjusted Cash Flow:
   ```
   adjusted_cf = base_cf + owner_comp_adj + one_time_addbacks + rent_addback
   ```
8. Compute Borrower DSCR:
   ```
   borrower_dscr = adjusted_cf / new_debt_service_annual
   ```
9. Compare to `policy.cif_procedures.yaml → dscr_thresholds.borrower_min` (default 1.25x Colony, 1.20x CIF). Flag if below.
10. Append audit entry to `audit/{deal_id}.jsonl` with inputs hash, all addback values with sources, final DSCR.
11. Return output per Layer 5.

## Layer 5 — Output Schema
```json
{
  "status": "ok" | "halt" | "flag",
  "skill": "calculate_business_cash_flow",
  "version": "1.0.0",
  "timestamp": "ISO",
  "deal_id": "...",
  "tax_year": 2025,
  "base_cash_flow": 142500.00,
  "addbacks": {
    "owner_comp_adjustment": 0.00,
    "one_time_expenses": 0.00,
    "rent_to_owner_re": 0.00
  },
  "adjusted_cash_flow": 142500.00,
  "new_annual_debt_service": 98000.00,
  "borrower_dscr": 1.45,
  "threshold_applied": 1.25,
  "pass_fail": "PASS",
  "variance_from_threshold": 0.20,
  "flags": [],
  "audit_ref": "audit/BEL_2026-04.jsonl#line12"
}
```

## Examples

### Example 1 — Clean S-Corp DSCR
**Input:** Bellanti Holdings S-Corp, 2025 return. NI $45K, Dep $67K, Int $30K, Owner W-2 $85K (reasonable for industry). New debt $98K/yr.
→ base_cf = 45 + 67 + 30 = $142K
→ owner_comp_adj = 0 (within range)
→ adjusted_cf = $142K
→ borrower_dscr = 142 / 98 = 1.45x → PASS

### Example 2 — HALT on missing depreciation
**Input:** Borrower submits P&L only, no tax return.
→ `depreciation` not on P&L
→ Status: halt | missing_fields: ["depreciation"] | Message: "P&L does not show depreciation line. Request full tax return (Form 1120-S or 1040 Schedule C)."

### Example 3 — FLAG on unsupported addback
**Input:** Owner claims $40K "one-time legal fees" addback but provides no supporting doc.
→ Skip addback (Step 5 guardrail)
→ adjusted_cf calculated without it
→ flags: ["unsupported_addback_claimed", "owner_disclosed_40k_without_source_doc"]
→ Status: flag (not halt — calc completes conservatively)

## Changelog
| Version | Date | Change | Approved by |
|---------|------|--------|-------------|
| 1.0.0 | 2026-04-15 | Initial version. Splits from legacy cif-cash-flow skill (4→1). Replaces hardcoded thresholds with policy YAML refs. | Keith Williams (pending) |
