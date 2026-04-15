---
name: intake_broker_client
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 1-extraction
depends_on: []
policy_refs: [policy/broker_rules.yaml, policy/sba_sop_50_10.yaml, policy/email_voice_rules.yaml]
---

# SKILL: intake_broker_client

## Layer 1 — Trigger Description
Use when a new SBA broker client enters the pipeline (inbound lead from sbalendingnetwork.com /get-started, referral, warm intro). Runs full broker engagement intake in under 60 seconds: collects borrower data, runs 5-tier classification, produces Broker Referral Agreement + Form 159 packet, drafts welcome email. Single-source entry point for the broker side of the business (mirror of `intake_cif_checklist` for Swift Capital side).

## Layer 2 — Negative Trigger
- Do NOT run for CIF/Swift Capital borrowers (use `intake_cif_checklist`).
- Do NOT run for Colony Bank as-lender deals — employment conflict. Route to alternative lender.
- Do NOT run for MCA prospects — auto-decline per broker policy.
- Do NOT create engagement without Keith's approval of the referral agreement terms (20% / 12-month tail or fixed fee).
- Do NOT skip Form 159 — required for all SBA-backed deals.
- Do NOT CC lender/borrower on internal pipeline updates until engagement is executed.

## Layer 3 — Input Schema
| Field | Type | Required | Source |
|-------|------|----------|--------|
| deal_id | string | Yes | router |
| borrower_legal_name | string | Yes | intake form |
| borrower_entity_type | enum | Yes | intake form |
| borrower_state | string | Yes | intake form |
| contact_name | string | Yes | intake form |
| contact_email | string | Yes | intake form |
| contact_phone | string | No | intake form |
| lead_source | enum | Yes | `website` \| `referral` \| `direct` \| `ad` \| `outbound` |
| deal_type | enum | Yes | `acquisition` \| `expansion` \| `cre_purchase` \| `refinance` \| `equipment` |
| industry | string | Yes | intake form |
| loan_amount_requested | currency | Yes | intake form |
| collateral_offered | list[string] | Yes | intake form |
| service_level_proposed | enum | Yes | `standard` \| `real_estate` \| `full_service` |
| character_disclosure | list[string] | No | intake form |

## Layer 4 — Procedure

### Step 1 — MCA / Colony / Ineligible pre-filter
Reject immediately if:
- Product requested is MCA / factor-rate financing → send Tier 5 decline email, exit.
- Lender intended is Colony Bank (or borrower is known to Keith from Colony pipeline) → HALT with `colony_employment_conflict`, route to alternative lender shortlist.
- Industry is cannabis / nursing home / golf / assisted living (Colony unacceptable; most SBA lenders restricted) → flag `restricted_industry_requires_specialty_lender`.

### Step 2 — Tier classification (run `score_inbound_leads` subroutine)
Use the 100-pt model. Tier assignment:
- **Tier 1** (85-100, Colony top-tier fit) — Call within 24h. Full service.
- **Tier 2** (70-84) — Email + discovery call this week.
- **Tier 3** (55-69) — Nurture + info-gather.
- **Tier 4** (BK / character issues / credit repair) — Route to PeopleFund + Clearinghouse CDFI + nurture sequence.
- **Tier 5** (MCA / ineligible) — Decline with referral-out email.

### Step 3 — Create deal folder
`Deals_Broker/{borrower_normalized}/` with: `deal_data.json`, `Engagement/`, `Packet/`, `Lender_Submissions/`, `Correspondence/`.

### Step 4 — Populate deal_data.json
Canonical schema (broker variant):
```json
{
  "deal_id": "...",
  "lane": "sba_broker",
  "policy_version": "...",
  "borrower": {"name": "...", "entity_type": "...", "state": "..."},
  "contact": {"name":"...","email":"...","phone":"..."},
  "request": {"deal_type":"...","industry":"...","amount":...,"use_of_proceeds":null,"collateral":[...]},
  "broker": {
    "service_level": "real_estate",
    "commission_rate": 0.02,
    "commission_amount_estimated": null,
    "engagement_signed": false,
    "form_159_on_file": false,
    "tail_months": 12
  },
  "tier": 1,
  "status": "intake",
  "stage": "engagement_pending",
  "lender_shortlist": [],
  "dates": {"intake":"<today>"}
}
```

### Step 5 — Character pre-screen
If `character_disclosure` non-empty → invoke `screen_sba_character_loe_needed` → attach output. Flag `loe_required` in deal_data.

### Step 6 — Generate Broker Referral Agreement (docx)
Use template at `operations/templates/Broker_Referral_Agreement.docx` (from Playbooks). Pre-fill: borrower name, entity, date, service_level, commission_rate, tail_months=12, Form 159 disclosure clause. Save to `Engagement/{Borrower}_Referral_Agreement_{date}.docx`.

### Step 7 — Commission estimate
Invoke `calculate_broker_commission` with service_level, loan_amount, lender_type="sba_bank" (default), is_sba_backed=true. Write result into deal_data.broker.commission_amount_estimated.

### Step 8 — Lender shortlist (Colony-excluded)
Based on industry + tier + loan size, produce candidate lender list from `policy/lender_profiles.yaml`:
- Tier 1 standard SBA 7(a) $350K-$5M: Live Oak, Newtek, Celtic
- Tier 2 CDFI-friendly: VestedIn, LiftFund, Accion Opp Fund
- Tier 4 BK/credit-repair: PeopleFund, Clearinghouse CDFI
- Never shortlist Colony.

### Step 9 — Draft welcome email
Invoke `draft_outbound_email` with from_account="sba" (Gmail MCP, keith@sbalendingnetwork.com). Content:
- Welcome + engagement agreement attached
- Next steps (doc checklist, discovery call via Cal.com link)
- Form 159 disclosure paragraph
- Full HTML signature with Book-a-Consult button (per email_voice_rules.yaml)
- CAN-SPAM footer

Do NOT send. Draft only.

### Step 10 — Pipeline update
Append entry to `ACTIVE_PIPELINE.json` with tier, stage=`engagement_pending`, next_action="Keith: review engagement letter + welcome draft, send when approved".

### Step 11 — Surface summary to Keith
```
{Borrower} — {Tier N} Broker Intake Complete

Deal: {industry} / {amount} / {service_level}
Commission est: ${amount} ({rate}%)
LOE needed: {yes/no}
Lender shortlist: {3-5 names, Colony excluded}

Deliverables:
  • Referral Agreement draft: {path}
  • Welcome email draft: {draft_id}
  • deal_data.json: {path}

Next: Review + approve, then "send welcome to {name}".
```

### Step 12 — Audit
Log: deal_id, tier, industry, amount, service_level, lender_shortlist, loe_flag, policy_version.

## Layer 5 — Output Schema
```json
{
  "status": "ok" | "halt" | "declined",
  "deal_id": "...",
  "tier": 1,
  "folder_path": "...",
  "engagement_doc_path": "...",
  "welcome_email_draft_id": "...",
  "commission_estimate": 7000,
  "lender_shortlist": ["Live Oak","Newtek","Celtic"],
  "loe_required": false,
  "next_action": "keith_review_engagement",
  "audit_ref": "..."
}
```

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-15 | Initial. Consolidates CLAUDE.md phantom `broker-client-intake` + `lead-tiering` into a single atomic intake skill. `lead-tiering` subsumed into `score_inbound_leads` (redundant). |
