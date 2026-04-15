---
name: rank_outreach_prospects
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 3-risk-compliance
depends_on: []
policy_refs: [policy/lead_scoring.yaml]
---

# SKILL: rank_outreach_prospects

## Layer 1 — Trigger Description
Use to rank a list of CDFI and Bank prospects for outbound relationship outreach. Applies warm-contact weighting (referral, prior engagement, introducer credibility) and deal-volume potential. Outputs a prioritized call list with draft outreach angle per prospect.

## Layer 2 — Negative Trigger
- Do NOT include prospects flagged as Do-Not-Contact (internal list or prior reject).
- Do NOT auto-draft outreach — this skill ranks, `draft_outbound_email` writes.
- Do NOT use for borrower prospects (this is B2B / lender / CDFI outreach only).

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| prospect_list_file | file | Yes |
| outreach_goal | enum | Yes | `"deal_flow"` \| `"uw_contract"` \| `"referral_partner"` |

## Layer 4 — Procedure

### Step 1 — Load prospect list
Read `prospect_list_file` (typically `FORGE/CDFI_BANK_PROSPECT_LIST.md` or operations/prospects.md). Parse: name, organization, role, email, phone, relationship_history, last_contact_date, prior_response_status.

### Step 2 — Filter Do-Not-Contact
Remove any prospect with `status = DNC`, `status = rejected_definite`, or `status = unsubscribed`. Log excluded count.

### Step 3 — Apply priority-score weights
From `policy/lead_scoring.yaml → outreach_priority_weights`:

| Factor | Weight | Applies when |
|---|---|---|
| Warm contact (former employer / existing relationship) | +30 | Firstrust, Republic Bank, VestedIn, FBCO alumni |
| Prior communication (email sent, awaiting reply) | +15 | last_contact within 30d, no response yet |
| High volume potential (large SBA portfolio or UW backlog) | +20 | WSFS, Reinvestment Fund, PIDC |
| Mission alignment (CDFI, MBE-focused, CRA-motivated) | +15 | United Bank of Philly, WORC, Enterprise Center |
| Geographic proximity (Philadelphia metro) | +10 | Local |
| MBE cert advantage | +10 | Prospects that prioritize MBE vendors |
| No response to prior outreach | -10 | Previously contacted, silent |
| Long follow-up gap (>14 days since last contact) | -5 | Stalled engagement |

### Step 4 — Goal-specific angle suggestion
For each prospect, based on `outreach_goal`:
- `deal_flow` (broker seeking deal sources): angle = "Do you have deals outside your box I could place nationwide?"
- `uw_contract` (seeking recurring UW retainer): angle = "I can take UW workload off your team — proof: FBCO contract 2023-2024, CIF current, 94-test production UW engine."
- `referral_partner` (bidirectional referrals): angle = "I refer deals I can't fit to your box; let's set up reciprocal workflow."

### Step 5 — Compute ranked output
```
priority_score = sum(applicable_weights)
```
Sort descending. Classify:
- **CALL TODAY** (score ≥ 50): Warm + high-potential. Phone first if number available.
- **EMAIL THIS WEEK** (25-49): Email draft, personalized by relationship history.
- **NURTURE** (10-24): Add to newsletter/quarterly touch.
- **PARK** (<10): Move to cold-storage list, revisit quarterly.

### Step 6 — Emit output
```json
{
  "outreach_goal": "uw_contract",
  "prospects_ranked": 28,
  "call_today": [{"name":"Howard Brown","org":"MBDA/Enterprise Center","score":65,"angle":"...","message_type":"phone","reason_for_rank":"warm_contact + mission_alignment + proximity"}],
  "email_this_week": [...],
  "nurture": [...],
  "park": [...]
}
```

### Step 7 — Cadence tracking
Update prospect list with today's date as `last_evaluated`. Do NOT mark `last_contact` — that fires only after Keith actually sends an outreach.

### Step 8 — Audit
Log: prospect_count, DNC_excluded, priority_distribution, goal, policy_version.

## Layer 5 — Output Schema
Ranked prospect list with score, warm-contact path, suggested angle, suggested message type.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. |
