---
name: match_colony_grid
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 3-risk-compliance
depends_on: [extract_sba_deal_parameters]
policy_refs: [policy/colony_grids.yaml, policy/sba_sop_50_10.yaml]
---

# SKILL: match_colony_grid

## Layer 1 — Trigger Description
Use after SBA deal parameters have been extracted. Selects the correct Colony Bank SBSL loan grid (industry-specific, franchise, CRE-secured, or general) and evaluates the deal's hard requirements against that grid's thresholds. Returns PASS / CONDITIONAL / FAIL with specific policy citations.

## Layer 2 — Negative Trigger
- Do NOT use for brokered deals where Colony is NOT the target lender (Keith is a Colony W-2 employee — brokering Colony deals is an employment conflict; see `policy/broker_rules.yaml → no_colony_brokering`).
- Do NOT use for CIF deals (use CIF procedures skill).
- Do NOT use for prohibited industries (nursing homes, assisted living, golf courses, cannabis) — return FAIL with SOP reference, do not attempt grid match.
- Do NOT use if `extract_sba_deal_parameters` has not run or returned incomplete industry classification.
- Do NOT override SOP 50-10 with grid language — SOP governs when in conflict.

## Layer 3 — Input Schema
| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| deal_id | string | Yes | router | — |
| industry_naics | string | Yes | extract skill | NAICS code |
| industry_classification | enum | Yes | extract skill | See grid taxonomy |
| deal_type | enum | Yes | extract skill | `"startup"` \| `"buy_sell"` \| `"expansion"` \| `"refi"` |
| loan_amount | currency | Yes | application | |
| project_costs | currency | Yes | application | Total sources & uses |
| cre_percent_of_project | percent | Conditional | application | Required if any CRE |
| equity_injection_percent | percent | Yes | application | |
| borrower_credit_score | int | Yes | credit report | Middle score, primary guarantor |
| borrower_liquidity_months | float | Yes | PFS | Liquid assets ÷ monthly global debt+living |
| years_industry_experience | int | Yes | resume / interview | |
| franchise_fund_score | int | Conditional | FUND database | Required if franchise |
| collateral_type | enum | Yes | application | `"cre_1st"` \| `"cre_2nd"` \| `"me"` \| `"none"` |
| borrower_dscr | ratio | Yes | calculate_business_cash_flow | |
| global_dscr | ratio | Yes | calculate_global_cash_flow | |
| geographic_state | string | Yes | application | 2-letter |
| sba_guaranty_percent | percent | Yes | loan structure | 75% or 85% |

## Layer 4 — Procedure

1. Validate inputs. HALT if any required missing.
2. Screen for prohibited industries (load `policy/colony_grids.yaml → prohibited`). If match, return FAIL with SOP citation.
3. Select grid using this priority order:
   1. Industry-specific grid (medical, pharmacy, hotel, gas station, childcare, funeral home, car wash, RV park)
   2. Franchise grid (if franchise AND no industry-specific match): Tier 1 (FUND 750+), Tier 2 (650-749), Tier 3 (600-649), reject if <600
   3. CRE-Secured grid (if `cre_percent_of_project >= 75` AND `collateral_type == "cre_1st"`)
   4. Business Loans / Acquisition grid (if operating history >= 5 yrs)
   5. General / Non-Specialty grid (default)
4. Load thresholds for selected grid from `policy/colony_grids.yaml → grids.{grid_name}`.
5. Check each hard requirement (each returns PASS or FAIL):
   - borrower_dscr >= grid.min_borrower_dscr
   - global_dscr >= grid.min_global_dscr
   - borrower_credit_score >= grid.min_credit_score
   - equity_injection_percent >= grid.min_equity_injection
   - borrower_liquidity_months >= grid.min_liquidity_months
   - years_industry_experience >= grid.min_experience_years
   - loan_amount <= grid.max_loan_amount
6. Check geographic eligibility: if `sba_guaranty_percent < 75`, confirm state is in Colony's Southeast US footprint; else nationwide eligible.
7. Apply rate shock test: recompute DSCR at +3.00% rate. If post-shock global DSCR < `grid.min_global_dscr_after_shock` (default 1.00), add to flags.
8. Aggregate verdict:
   - All checks PASS → `verdict: "PASS"`
   - Any single hard threshold FAIL by <10% variance → `verdict: "CONDITIONAL"`, list exceptions + compensating factors needed
   - Multiple FAILs or >10% variance on any → `verdict: "FAIL"`
9. Check SOP 50-10 overlays: character determination (flag if LOE needed), use-of-proceeds eligibility, affiliation rules.
10. Write audit entry with grid selected, thresholds applied, every check result.
11. Return output per Layer 5.

## Layer 5 — Output Schema
```json
{
  "status": "ok" | "halt",
  "skill": "match_colony_grid",
  "version": "1.0.0",
  "timestamp": "ISO",
  "deal_id": "...",
  "grid_selected": "Medical_Dental_Vet_Professional",
  "grid_selection_rationale": "NAICS 621111 matches industry-specific grid",
  "verdict": "PASS" | "CONDITIONAL" | "FAIL",
  "checks": [
    {"requirement": "min_borrower_dscr", "threshold": 1.15, "actual": 1.45, "result": "PASS"},
    {"requirement": "min_credit_score", "threshold": 675, "actual": 680, "result": "PASS"}
  ],
  "exceptions_needed": [],
  "compensating_factors_suggested": [],
  "rate_shock_post_dscr": 1.02,
  "sop_flags": ["loe_required_due_to_disclosed_misdemeanor"],
  "policy_citations": ["Colony Grid v2024-03-24", "SBA SOP 50-10 Character Determination §120.110"],
  "audit_ref": "audit/{deal_id}.jsonl#line{n}"
}
```

## Examples

### Example 1 — PASS (Advanced Integrated Pain)
Medical practice, CRE purchase, DSCR 1.45x, 680 credit, 15% equity, 8 mo liquidity.
→ Grid: Medical/Dental/Vet/Professional
→ All checks PASS
→ verdict: "PASS"

### Example 2 — CONDITIONAL (borderline)
Restaurant franchise, FUND 640, DSCR 1.18x (grid min 1.25x), 680 credit.
→ Grid: Franchise Tier 3
→ DSCR variance = 5.6% below min
→ verdict: "CONDITIONAL", compensating factors: ["larger_equity_injection", "additional_liquidity", "personal_guaranty_of_spouse"]

### Example 3 — FAIL (prohibited)
Assisted living facility acquisition.
→ Step 2 prohibited screen catches it
→ verdict: "FAIL", citation: "Colony Grid Prohibited Industries + SBA SOP 50-10 affiliate rules"

## Changelog
| Version | Date | Change | Approved by |
|---------|------|--------|-------------|
| 1.0.0 | 2026-04-15 | Initial atomic version. Extracted from legacy sba-deal-screener (was 3-in-1). Reads thresholds from policy YAML instead of hardcoding. | Keith Williams (pending) |
