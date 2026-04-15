---
name: extract_sba_deal_parameters
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 1-extraction
depends_on: []
policy_refs: [policy/sba_sop_50_10.yaml]
---

# SKILL: extract_sba_deal_parameters

## Layer 1 — Trigger Description
Use to parse an SBA broker deal description (email, intake form, voice memo) into structured parameters required by `match_colony_grid` and `calculate_broker_commission`. Outputs industry, deal type, loan amount, use of proceeds, collateral, equity, FUND score.

## Layer 2 — Negative Trigger
- Do NOT use for CIF deals (use `intake_cif_checklist`).
- Do NOT use for Colony-as-lender deals (employment conflict — see `policy/broker_rules.yaml`).
- Do NOT use for MCA referrals (permanently excluded per broker policy).
- Do NOT estimate missing parameters — if a required field cannot be extracted, mark "Not Provided" and halt downstream grid matching.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| source_text | string | Yes |
| source_files | list[file] | No |

## Layer 4 — Procedure

### Step 1 — Pre-filter for excluded deals
Scan `source_text` for keywords that immediately disqualify:
- MCA / merchant cash advance / Kapitus / Credibly / OnDeck MCA / Rapid Finance → HALT with `excluded_product_mca`. Route to decline template.
- Colony Bank / Colony / SBSL / Keith's employer → HALT with `colony_employment_conflict`. Route to alternative lender selection (Live Oak / Newtek / Celtic / VestedIn / LiftFund).
- Cannabis / marijuana / dispensary → HALT with `sba_ineligible_industry`.
- Nursing home / assisted living / golf course → HALT with `colony_unacceptable_industry` if intended lender is Colony; otherwise flag for alternative lender.

### Step 2 — Extract required fields
From free-form `source_text`, extract and tag every value with source (text line # or file page):

| Field | Type | Required | Extraction Hints |
|---|---|---|---|
| borrower_legal_name | string | Yes | Proper-noun entity; look for "LLC", "Inc", "Corp" |
| borrower_state | string | Yes | USPS 2-letter or full state name |
| industry | string | Yes | Match against Colony grid industries: medical, dental, vet, pharmacy, franchise (name + FUND tier), gas station (branded?), hotel (flag?), CRE, professional services |
| naics_code | string | No | If stated |
| deal_type | enum | Yes | `acquisition` \| `expansion` \| `cre_purchase` \| `refinance` \| `working_capital` \| `equipment` |
| loan_amount | currency | Yes | Dollar figure, normalized (e.g. "$1.2M" → 1200000) |
| use_of_proceeds | list[string] | Yes | Itemized if possible |
| collateral | list[object] | Yes | Each: {type: CRE \| equipment \| inventory \| none, est_value, improved/unimproved, new/used} |
| equity_injection_pct | percent | Yes | Stated or inferable from sources & uses |
| equity_source | string | No | Cash / seller-note / gift / SBA-compliant? |
| liquidity_months | decimal | No | If stated |
| fund_tier | enum | No | `FUND_750+` \| `FUND_600-749` \| `FUND_<600` — for franchise deals |
| franchise_name | string | No | If franchise |
| existing_business_years | int | No | If expansion / refi |
| guarantors | list[object] | No | Each: {name, ownership_pct, FICO if stated} |
| credit_score_primary | int | No | Range OK |
| character_issues_disclosed | list[string] | No | BK, collections, judgments, criminal filings — triggers `screen_sba_character_loe_needed` downstream |

### Step 3 — Missing-field handling
For every REQUIRED field not extracted, set value = `null` and add to `missing_required_fields` list. HALT downstream grid matching if any required field missing — do not pass a half-formed deal to `match_colony_grid`.

### Step 4 — Confidence scoring
For each extracted field, assign confidence 0-1 based on explicitness (direct quote = 1.0, inferred from context = 0.6, heuristic = 0.3). If any required field confidence < 0.6, flag for human verification before proceeding.

### Step 5 — Sanitize for PII logging
Redact SSN, DOB, full account numbers, full DL numbers before writing to audit log. Keep names, entity names, loan amounts, industry — these are not PII per agent.json policy.

### Step 6 — Emit structured output
```json
{
  "deal_id": "...",
  "source_hash": "sha256:...",
  "parameters": {<fields from Step 2>},
  "missing_required_fields": [],
  "confidence_flags": [],
  "excluded_reason": null,
  "audit_ref": "..."
}
```

### Step 7 — Audit entry
Log: skill, deal_id, source_hash, required_field_count, missing_count, confidence_avg, excluded flag if applicable.

## Layer 5 — Output Schema
Structured deal parameter object consumed by downstream SBA skills.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy sba-deal-screener (3-in-1 → atomic). |
