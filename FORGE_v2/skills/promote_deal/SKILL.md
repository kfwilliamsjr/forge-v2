---
name: promote_deal
version: 1.0.0
status: production
triggers:
  - "promote [deal]"
  - "advance [deal]"
  - "move [deal] to"
  - "approve spreads for [deal]"
  - "approve UW for [deal]"
  - "approve memo for [deal]"
  - "final approval [deal]"
---

# promote_deal

## Layer 1 — Trigger
Advance a deal's stage on Keith's approval at one of 4 decision gates.

## Layer 2 — Stage model
`intake -> spreads_ready -> uw_complete -> memo_draft -> memo_final -> committee -> decision -> closing -> purge`

Decision gates (require Keith):
- **spreads_ready** — Keith reviews initial spreads/G8WAY before UW begins
- **uw_complete** — Keith approves UW conclusions before memo drafting
- **memo_draft** — Keith reviews memo edits before final
- **memo_final** — Keith gives final approval before committee send

## Layer 3 — Inputs
- `deal_id` (required)
- `new_stage` (required — must be in valid stages)
- `--note` (optional — logs to decisions.log.jsonl)
- `--next` (optional — updates next_action)
- `--owner` (optional — default "keith")

## Layer 4 — Procedure
1. Run `python3 Agentic_Overhaul/portfolio/tools/promote_deal.py DEAL_ID NEW_STAGE --note "..." --next "..."`
2. Tool writes portfolio.json, appends decisions.log.jsonl, regenerates PORTFOLIO.html
3. Surface link to updated dashboard

## Layer 5 — Policy
- Every promotion is logged. Immutable audit trail.
- Only Keith promotes through the 4 decision gates. Other transitions (e.g., memo_final -> committee) can be automated.
- Never promote past `closing` without `committee_decision` date set (30-day purge clock).
