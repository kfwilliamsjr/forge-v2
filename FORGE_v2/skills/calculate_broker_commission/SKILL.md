---
name: calculate_broker_commission
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 2-calculation
depends_on: [extract_sba_deal_parameters]
policy_refs: [policy/broker_rules.yaml]
---

# SKILL: calculate_broker_commission

## Layer 1 — Trigger Description
Use to compute estimated broker commission on an SBA deal using Keith's tiered schedule: 1% standard (non-RE), 2% real estate, 3% full-service underwriting. Also determines if Form 159 is required (all SBA-backed deals) and if CDFI fee rules apply (borrower-paid, separate engagement letter).

## Layer 2 — Negative Trigger
- Do NOT calculate commission for Colony-as-lender deals (employment conflict — return $0 and flag).
- Do NOT apply any commission tier without explicit service-level designation from Keith.
- Do NOT assume loan-proceeds fee on CDFI products — CDFI fees are borrower-paid on separate engagement letter (policy hard rule).
- Do NOT produce numbers if loan amount is missing or deal is MCA (excluded category).

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| loan_amount | currency | Yes |
| service_level | enum | Yes | `"standard"` \| `"real_estate"` \| `"full_service"` |
| lender_type | enum | Yes | `"sba_bank"` \| `"cdfi"` \| `"other"` |
| is_sba_backed | bool | Yes |

## Layer 4 — Procedure

### Step 1 — Pre-checks
- HALT if `loan_amount` null or ≤ 0.
- HALT if deal was tagged `excluded_product_mca` upstream.
- HALT if `lender = Colony` (employment conflict) → return `commission_amount: 0`, `flags: ["colony_employment_conflict"]`.

### Step 2 — Load rate table from policy
From `policy/broker_rules.yaml → commission_schedule`:
| service_level | rate |
|---|---|
| standard | 0.01 (1%) — non-RE deals, referral/brokering only |
| real_estate | 0.02 (2%) — CRE or real-estate-secured |
| full_service | 0.03 (3%) — full UW + evaluation + packaging |

### Step 3 — Compute commission
```
commission_amount = loan_amount * rate_from_table[service_level]
```
Round to nearest dollar.

### Step 4 — Form 159 determination
```
form_159_required = is_sba_backed  # ALL SBA-backed deals require Form 159 disclosure
```
If required, flag: both borrower and broker must sign, submitted with loan package, no exceptions (policy hard rule).

### Step 5 — Fee-source determination
- If `lender_type = "sba_bank"` → `fee_source = "loan_proceeds"`, `engagement_letter_required = false` (commission paid at close out of loan proceeds).
- If `lender_type = "cdfi"` → `fee_source = "borrower_direct"`, `engagement_letter_required = true`. Rationale: CDFI Fund rules prohibit loan-proceeds broker fees on most CDFI products. Packaging/advisory fees billed to borrower on separate engagement letter. If also SBA-backed, disclose on Form 159.
- If `lender_type = "other"` → flag `fee_source_manual_review`, require Keith's explicit approval before using loan-proceeds.

### Step 6 — Emit output
```json
{
  "status": "ok",
  "service_level": "real_estate",
  "commission_rate": 0.02,
  "commission_amount": 14000,
  "form_159_required": true,
  "fee_source": "loan_proceeds",
  "engagement_letter_required": false,
  "flags": []
}
```

### Step 7 — Audit
Log: deal_id, loan_amount, service_level, rate, amount, fee_source, form_159 flag, policy_version.

## Layer 5 — Output Schema
```json
{"status":"ok","commission_rate":0.02,"commission_amount":7000,"form_159_required":true,"fee_source":"loan_proceeds","engagement_letter_required":false,"flags":[]}
```

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Splits from legacy sba-deal-screener. |
