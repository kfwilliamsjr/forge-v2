---
name: run_cif_stress_tests
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 2-calculation
depends_on: [calculate_business_cash_flow, calculate_global_cash_flow]
policy_refs: [policy/cif_procedures.yaml]
---

# SKILL: run_cif_stress_tests

## Layer 1 — Trigger Description
Use after business + global cash flows are computed. Runs 4 standard stress scenarios: (1) 10% revenue decline, (2) 15% revenue decline, (3) +3.00% rate shock, (4) combined 10% revenue + rate shock. Reports DSCR under each scenario with PASS/FAIL flags.

## Layer 2 — Negative Trigger
- Do NOT run on startup deals with no operating history (stress-testing projections is low-confidence).
- Do NOT skip any scenario — all 4 are required per CIF procedures.
- Do NOT use custom scenarios without policy approval.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| baseline_revenue | currency | Yes |
| baseline_business_cf | currency | Yes |
| baseline_global_cf | currency | Yes |
| baseline_living_expenses | currency | Yes |
| baseline_personal_debt_service | currency | Yes |
| baseline_annual_debt_service | currency | Yes |
| proposed_rate | percent | Yes |
| proposed_term_months | int | Yes |
| loan_amount | currency | Yes |
| rate_type | enum | Yes | `fixed` \| `variable` |

## Layer 4 — Procedure

CIF canonical stress panel is 4 scenarios. All 4 MUST run; partial is a procedure violation.

### Scenario 1 — Personal Debt × 2
- Stressed personal debt = `baseline_personal_debt_service * 2`
- Recompute `global_cf_stressed = baseline_business_cf + (net_personal_cf_baseline - baseline_personal_debt_service)` (back out baseline) then subtract `2 * baseline_personal_debt_service`
- `dscr = global_cf_stressed / baseline_annual_debt_service`
- **Threshold: ≥ 1.10x**

### Scenario 2 — Living Expenses × 1.5
- Stressed living expenses = `baseline_living_expenses * 1.5`
- Recompute global CF with the additional 0.5x living-expense drain
- `dscr = global_cf_stressed / baseline_annual_debt_service`
- **Threshold: ≥ 1.10x**

### Scenario 3 — Combined Stress (Scenarios 1 + 2 simultaneously)
- Stressed personal debt = baseline × 2 AND stressed living expenses = baseline × 1.5
- Recompute global CF under both drains
- `dscr = global_cf_stressed / baseline_annual_debt_service`
- **Threshold: ≥ 1.10x** (CIF combined-stress minimum)

### Scenario 4 — Severe: Revenue -20%
- Stressed revenue = `baseline_revenue * 0.80`
- Recompute business cash flow holding all expenses constant:
  `business_cf_stressed = baseline_business_cf - (baseline_revenue * 0.20 * gross_margin_ratio)` — or, if granular data available, flow -20% revenue through full P&L holding fixed costs constant.
- Recompute global CF, then DSCR
- **Threshold: ≥ 1.00x** (breakeven — can still service debt at 80% revenue)

### Rate-shock companion (runs alongside, not a 5th scenario)
If `rate_type = variable`, also compute `stressed_rate = proposed_rate + 0.03`, recompute PMT → new annual_debt_service, and re-run Scenario 4 with the stressed rate. This surfaces double-exposure (revenue + rate) for committee visibility.

### Aggregate verdict
- **PASS** = all 4 scenarios meet their respective thresholds AND base DSCR ≥ 1.25x (from upstream skill)
- **CONDITIONAL** = base passes but 1-2 stress scenarios fail; requires committee discussion
- **FAIL** = base fails OR ≥3 stress scenarios fail

### Present output table
```
DSCR SUMMARY — {borrower}
Base Case              X.XXx   1.25x     PASS/FAIL
Stress 1: Debt × 2     X.XXx   1.10x     PASS/FAIL
Stress 2: Living × 1.5 X.XXx   1.10x     PASS/FAIL
Stress 3: Combined     X.XXx   1.10x     PASS/FAIL
Stress 4: Rev -20%     X.XXx   1.00x     PASS/FAIL
VERDICT: PASS / CONDITIONAL / FAIL
```

### Audit
Log all 4 scenario inputs + outputs, thresholds applied, policy_version, rate-shock result if applicable.

## Layer 5 — Output Schema
Array of 4 scenario objects, each with revenue, cf, dscr, pass_fail.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy cif-cash-flow. |
