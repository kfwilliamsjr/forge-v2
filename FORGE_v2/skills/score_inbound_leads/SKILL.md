---
name: score_inbound_leads
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 3-risk-compliance
depends_on: []
policy_refs: [policy/lead_scoring.yaml, policy/colony_grids.yaml]
---

# SKILL: score_inbound_leads

## Layer 1 — Trigger Description
Use to score Supabase lead-form submissions against Keith's 100-point model (Deal Fit 40 + Borrower Quality 30 + Engagement 20 + Revenue Potential 10). Outputs HOT / WARM / COLD ranking and routes to the appropriate Tier 1-5 playbook.

## Layer 2 — Negative Trigger
- Do NOT route Tier 5 leads to MCA products (permanent policy exclusion).
- Do NOT score without source Supabase export — no synthetic scoring.
- Do NOT skip the MCA-exclusion check (Step 0).
- Do NOT email borrower from this skill — scoring only, comms handled separately.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| supabase_export_file | file | Yes |
| scoring_date | date | Yes |

## Layer 4 — Procedure

### Step 0 — MCA exclusion filter
For each lead, scan notes/message for MCA signals: "merchant cash advance", "MCA", "factor rate", "daily ACH", "holdback", "Kapitus / Credibly / OnDeck / Rapid / Shopify Capital". If any match → auto-classify Tier 5, route to `decline_mca_nurture_email`, do NOT score further. MCA referrals are permanently excluded.

### Step 1 — Load scoring model from policy
From `policy/lead_scoring.yaml → model_v1`: 100 points total across 4 dimensions:

**Deal Fit (40 pts)**
| Criterion | Pts |
|---|---|
| Industry Top-Tier (medical, dental, vet, pharmacy, CRE, FUND 750+ franchise) | 15 |
| Industry Acceptable (gas station/branded, hotel/flag, 5+yr biz, FUND 600-749) | 10 |
| Industry Lowest-Tier (car wash, RV park, startup no-CRE) | 3 |
| Industry Not Acceptable (nursing home, golf, cannabis) | 0 |
| Loan $250K-$2M (sweet spot) | 10 |
| Loan $150K-$250K | 7 |
| Loan $2M-$5M | 8 |
| Loan <$150K or >$5M | 3 |
| CRE collateral | 10 |
| Equipment/inventory only | 5 |
| No collateral | 0 |
| SBA-eligible use clearly stated | 5 |
| Unclear/risky use | 0 |

**Borrower Quality (30 pts)**
| Criterion | Pts |
|---|---|
| Credit 700+ | 10 |
| Credit 675-699 | 7 |
| Credit <675 or unknown | 3 |
| 5+ years experience | 10 |
| 2-4 years | 6 |
| <2 years / startup | 2 |
| Equity 15%+ | 5 |
| Equity 10% | 3 |
| No equity info | 0 |
| Financials provided | 5 |
| No financials | 0 |

**Engagement Signals (20 pts)**
| Criterion | Pts |
|---|---|
| Phone number provided | 5 |
| Detailed message (>2 sentences) | 5 |
| Timeline/urgency mentioned | 5 |
| Google Ads UTM tagged | 3 |
| Organic / direct | 2 |
| Referral source mentioned | 5 |

**Revenue Potential (10 pts)** — commission estimate × loan amount × broker rate
| Est. commission | Pts |
|---|---|
| > $30K | 10 |
| $10K-$30K | 7 |
| $5K-$10K | 5 |
| < $5K | 2 |

### Step 2 — Classification thresholds
- **HOT (75-100):** Call within 24h. Tier 1-2 lead.
- **WARM (45-74):** Email within 48h. Tier 2-3.
- **COLD (0-44):** Auto-decline with referral template or park. Tier 4-5.

### Step 3 — Tier routing (Keith's 5-Tier framework)
- Tier 1 (score 85-100, fits Colony top-tier grid): → `rank_outreach_prospects` → Keith call
- Tier 2 (score 70-84): → email + discovery
- Tier 3 (score 55-69, needs nurture): → 7-day nurture sequence
- Tier 4 (BK / character issues / credit-repair): → PeopleFund + Clearinghouse CDFI referral + nurture
- Tier 5 (MCA / ineligible): → decline email, exit

### Step 4 — Character flag
If lead mentions BK, criminal history, prior default → flag `character_screening_required` and route to `screen_sba_character_loe_needed` before commission calc.

### Step 5 — Emit ranked output
```json
{
  "scoring_date": "2026-04-15",
  "leads_scored": 12,
  "hot": [{"name":"...","score":87,"tier":1,"rationale":"...","next_action":"call"}],
  "warm": [...],
  "cold": [...],
  "mca_declined": [...],
  "character_flags": [...]
}
```

### Step 6 — Audit
Log: date, lead count, HOT/WARM/COLD counts, MCA-declined count, model_version.

## Layer 5 — Output Schema
Ranked array of leads with score breakdown, tier, routing recommendation.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy borrower-prospecting (3 modes → 3 skills). |
