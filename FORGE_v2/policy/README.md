# Policy Engine — FORGE v2
*Version: 1.0 | Created: 2026-04-15*

This folder holds all business rules, thresholds, and grids as structured YAML. Skills READ from these files — they never hardcode thresholds. One policy change = one YAML edit = all skills inherit.

## Why this exists
Per the Master Build Guide: "Build the Policy Engine MCP first. Your internal credit policy is the most valuable MCP you can build." Even without a live MCP server, structured YAML accomplishes the same goal at solo-operator scale: single source of truth, versioned, auditable.

## Files (to be populated in next sessions)

| File | Source content to migrate |
|------|---------------------------|
| `colony_grids.yaml` | `knowledge-base/lender-grids/colony-bank/` (16 grids) |
| `cif_procedures.yaml` | `Swift Capital Underwriting/Credit Policy/CIF_UNDERWRITING_PROCEDURES.md` |
| `sba_sop_50_10.yaml` | SBA SOP 50-10 key thresholds (character, eligibility, proceeds, collateral) |
| `broker_rules.yaml` | CLAUDE.md "Broker Business Policies (Standing)" + Commission Schedule |
| `email_voice_rules.yaml` | `skills/email-drafter/SKILL.md` voice rules + banned phrase list + signature HTML |
| `vi_leap_grant_rules.yaml` | CIF grant eligibility + scoring |
| `lead_scoring.yaml` | 100-point model from borrower-prospecting |
| `bizbuysell_filters.yaml` | Industry exclusions + geographic + price filters |

## Versioning
Each YAML carries its own `policy_version` at the top. Skill audit logs record which policy version was applied. Policy change = increment version + changelog entry at top of file.

## Example structure (colony_grids.yaml skeleton)

```yaml
policy_version: 1.0.0
last_updated: 2026-04-15
source: knowledge-base/lender-grids/colony-bank/

prohibited:
  - nursing_homes
  - assisted_living
  - golf_courses
  - cannabis

global_defaults:
  min_borrower_dscr: 1.25
  min_global_dscr: 1.10
  min_credit_score: 675
  min_equity_injection: 0.10
  min_liquidity_months: 6
  rate_shock_add: 0.03
  min_global_dscr_post_shock: 1.00

grids:
  medical_dental_vet_professional:
    min_borrower_dscr: 1.15
    min_credit_score: 675
    min_equity_injection: 0.10
    max_loan_amount: 5000000
    notes: "Licensed, experienced. Practice buy-in allowed."

  franchise_tier_1:
    min_fund_score: 750
    min_borrower_dscr: 1.20
    min_credit_score: 700

  # ... 14 more grids
```

## Do NOT
- Do not edit SKILL.md files to change thresholds. Edit the YAML.
- Do not add a new threshold to a YAML without bumping the version.
- Do not delete old policy versions — archive to `policy/_archive/{version}/`.
