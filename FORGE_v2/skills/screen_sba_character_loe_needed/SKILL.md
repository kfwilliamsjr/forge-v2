---
name: screen_sba_character_loe_needed
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 3-risk-compliance
depends_on: []
policy_refs: [policy/sba_sop_50_10.yaml]
---

# SKILL: screen_sba_character_loe_needed

## Layer 1 — Trigger Description
Use when borrower discloses derogatory credit items, criminal filings, prior business failures, or government-loan defaults. Determines whether a Letter of Explanation (LOE) is required per SBA SOP 50-10 character determination criteria, and what the LOE must address.

## Layer 2 — Negative Trigger
- Do NOT write the LOE itself (that's a separate drafting skill, future).
- Do NOT make character decisions — this skill flags the requirement, not the outcome.
- Do NOT skip disclosed items because they're "minor" — SBA Form 912 disclosure rules are strict.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| credit_report_file | file | Conditional |
| criminal_disclosure | list[object] | No |
| prior_default_disclosure | list[object] | No |

## Layer 4 — Procedure

### Step 1 — Load SBA character triggers from policy
From `policy/sba_sop_50_10.yaml → character_determination_triggers`:

**Credit-based triggers (from credit report):**
- Bankruptcy (any chapter, within 7 years)
- Tax liens (federal or state, unresolved or within 7 years of resolution)
- Judgments (civil, unresolved or within 7 years)
- Collections (>$1,000 aggregate or any single >$500 unresolved)
- Charge-offs (within 7 years)
- Foreclosure (within 7 years)
- Current delinquencies ≥ 60 days

**Disclosure-based triggers (from borrower disclosure):**
- Criminal arrests (any, lifetime — SBA Form 912)
- Criminal convictions (any, lifetime)
- Current parole / probation
- Prior default on any federal loan (SBA, FHA, VA, student, etc.) — triggers CAIVRS check
- Prior default on state/local government loan
- Prior business failure with unpaid creditors

### Step 2 — Parse credit report (if provided)
Pull derogatory items. For each item, capture: item type, date, amount, status (open/resolved), creditor.

### Step 3 — Cross-reference disclosures to triggers
For each trigger match, add an entry to `loe_required_items`:
```json
{
  "trigger_category": "bankruptcy",
  "detail": "Chapter 7 discharged 2022-08",
  "source": "credit_report_TU.pdf#p3",
  "loe_must_address": [
    "What circumstances led to the bankruptcy",
    "What has changed financially since discharge",
    "Timeline of recovery",
    "Demonstration of current stability"
  ]
}
```

### Step 4 — CAIVRS flag
If ANY prior federal loan default is disclosed, emit `caivrs_check_required`. SBA lender MUST run CAIVRS; character determination may be blocked until CAIVRS clears.

### Step 5 — SBA Form 912 flag
If ANY criminal disclosure present, emit `form_912_required` AND `fingerprint_card_fd258_conditional` (may be required for unresolved or serious offenses — lender + SBA discretion).

### Step 6 — Determine aggregate verdict
- `loe_required = true` if any trigger matched
- `loe_required = false` ONLY if credit is clean AND no criminal / prior-default disclosure
- If unresolved federal debt, unresolved tax lien, or active parole: emit `character_review_blocker` — may disqualify under SOP, requires underwriter judgment before proceeding

### Step 7 — Emit output
```json
{
  "status": "ok",
  "deal_id": "...",
  "loe_required": true,
  "loe_required_items": [<per Step 3>],
  "caivrs_check_required": false,
  "form_912_required": false,
  "character_review_blocker": false,
  "recommendation": "Draft LOE addressing the listed items before submitting package.",
  "policy_version": "...",
  "audit_ref": "..."
}
```

### Step 8 — Audit
Log: deal_id, trigger count by category, verdict flags, policy_version. Redact specific amounts and dates from audit line (PII) — keep only trigger categories and counts.

## Layer 5 — Output Schema
Returns LOE-required flag + itemized list of what the LOE must address.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. New skill — previously just a flag in sba-deal-screener. |
