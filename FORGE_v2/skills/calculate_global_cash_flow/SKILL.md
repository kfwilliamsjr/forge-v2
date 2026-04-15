---
name: calculate_global_cash_flow
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 2-calculation
depends_on: [calculate_business_cash_flow, extract_personal_financials]
policy_refs: [policy/cif_procedures.yaml, policy/colony_grids.yaml]
---

# SKILL: calculate_global_cash_flow

## Layer 1 — Trigger Description
Use after business cash flow is computed. Combines business adjusted cash flow + personal income (W-2, other sources) minus personal debt service + personal living expenses. Outputs Global DSCR used by both Colony Bank SBA grids and CIF procedures.

## Layer 2 — Negative Trigger
- Do NOT use for pure business-only decisions (some Festival Loans, certain grants) — use business DSCR.
- Do NOT estimate personal living expenses — use borrower's PFS declaration OR policy default ($5K/mo adult + $1K/child), not both.
- Do NOT double-count: if owner compensation is on business return AND borrower's W-2, count the W-2 figure only (policy.owner_comp_handling).
- Do NOT run if `calculate_business_cash_flow` returned halt.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| business_adjusted_cash_flow | currency | Yes |
| personal_income_w2 | currency | Yes |
| personal_other_income | currency | No |
| personal_debt_service_annual | currency | Yes |
| personal_living_expenses_annual | currency | Yes |
| guarantor_count | int | Yes |

## Layer 4 — Procedure

### Step 1 — Validate inputs
HALT if `business_adjusted_cash_flow` is null (must run `calculate_business_cash_flow` first). HALT if `personal_debt_service_annual` is null (credit report required).

### Step 2 — No-double-count rule
Per CIF procedures: if borrower is sole prop (Schedule C) or S-Corp owner-operator taking K-1 distributions, business income already flows to personal return. In Layer 3, count ONLY non-business personal income: W-2 from outside jobs, rental, investment, alimony, child support. Do NOT add K-1 or Schedule C income a second time.

### Step 3 — Living expense floor
`living_expenses_used = max(personal_living_expenses_annual, policy.cif.living_expense_floor)`. CIF USVI Head-of-Household default: $24,000/yr ($2,000/mo). Use HIGHER of borrower-stated or policy floor.

### Step 4 — Personal debt service cleanup
From credit report monthly minimums × 12:
- Zero out balances < $500 (policy threshold)
- Zero out authorized-user accounts (borrower not primary obligor)
- Use Experian bureau as primary; reconcile only if scores diverge >50 points

### Step 5 — Compute global cash flow
```
net_personal_cf = personal_income_w2
                + personal_other_income
                - federal_state_local_taxes_effective
                - living_expenses_used
                - personal_debt_service_annual

global_cash_available = business_adjusted_cash_flow + net_personal_cf
```

### Step 6 — Compute proposed debt service
```
monthly_pmt = (rate/12 * loan_amount) / (1 - (1 + rate/12)^(-term_months))
proposed_annual_ds = monthly_pmt * 12
total_annual_ds = proposed_annual_ds + existing_business_ds_not_refinanced
```

### Step 7 — Compute global DSCR
```
global_dscr = global_cash_available / total_annual_ds
```

### Step 8 — Apply threshold (policy lookup)
Threshold source depends on lane:
- **CIF deals:** `policy/cif_procedures.yaml → dscr.global_threshold` (default 1.10x)
- **SBA broker deals (Colony):** `policy/colony_grids.yaml → {grid_name}.global_dscr_min` (default 1.10x general, grid-specific for industry)

Return `threshold_applied` and `threshold_source`.

### Step 9 — Rate shock test (Colony rule, applicable if variable-rate)
If `rate_type = variable`: compute `stressed_rate = rate + 0.03` (300 bps), recalculate PMT, recalculate global_dscr. Colony minimum after shock: 1.00x. Return `post_rate_shock_dscr`.

### Step 10 — Pass/fail determination
- `pass` if `global_dscr >= threshold_applied` AND (`post_rate_shock_dscr >= 1.00` if variable-rate, else N/A)
- `fail` otherwise
- Emit `conditional` if within 0.05x of threshold (gray zone for committee discussion)

### Step 11 — Write audit entry
Log all inputs, all outputs, threshold source + version, pass/fail, any flags (e.g., `living_expense_below_floor_adjusted`, `small_balance_zeroed`, `rate_shock_fail`).

## Layer 5 — Output Schema
Returns global_cash_flow, global_dscr, threshold_applied, pass_fail, post_rate_shock_dscr.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy cif-cash-flow. |
