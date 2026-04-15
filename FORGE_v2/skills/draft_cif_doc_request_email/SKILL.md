---
name: draft_cif_doc_request_email
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 6-comms
depends_on: [intake_cif_checklist]
policy_refs: [policy/cif_procedures.yaml, policy/email_voice_rules.yaml]
---

# SKILL: draft_cif_doc_request_email

## Layer 1 — Trigger Description
Use when CIF intake returns missing checklist items. Drafts a doc-request email TO Nikky Cole (nikky.cole@cifvi.org), CC Akem Durand (akem.durand@cifvi.org), listing the specific missing items with ShareFile upload instructions. Sent from Swift Capital account via Chrome MCP only.

## Layer 2 — Negative Trigger
- Do NOT send via Gmail MCP. Swift Capital uses Chrome MCP only (hard rule from CLAUDE.md).
- Do NOT draft if no missing items (nothing to request).
- Do NOT CC borrower on doc request — always internal (Nikky + Akem).
- Do NOT attach actual documents — request is for UPLOAD, not transmission.
- Do NOT auto-send. Draft only, Keith reviews.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| borrower_legal_name | string | Yes |
| missing_items | list[string] | Yes |
| product_type | enum | Yes |
| sharefile_folder_link | string | No |

## Layer 4 — Procedure

### Step 1 — Validate
HALT if `missing_items` is empty (nothing to request). HALT if `borrower_legal_name` is blank.

### Step 2 — Compose the email body
Template (plain text, warm professional tone per `email_voice_rules.yaml`):

```
Subject: {borrower_legal_name} — Document Request for {product_type_label}

Hi Nikky,

I'm beginning the underwriting review for {borrower_legal_name}'s {product_type_label}. Could you please send over the following documents at your earliest convenience?

{numbered list of missing_items}

If any of these have already been uploaded to ShareFile, just point me to the folder and I'll pull them from there.

Thanks,
Keith
```

`product_type_label` mapping:
- `festival_loan` → "Festival Loan application"
- `vi_leap_grant` → "VI Leap Grant application"
- `regular_loan` → "regular loan application"

### Step 3 — Pass to draft_outbound_email subroutine
Call `draft_outbound_email` with:
- `from_account = "swift"` (forces Chrome MCP routing — Gmail MCP is HARD-BLOCKED for Swift per agent.json)
- `to = ["nikky.cole@cifvi.org"]`
- `cc = ["akem.durand@cifvi.org", "keith@swiftcapitoptions.com"]`
- `bcc = []`
- `subject` + `body` from Step 2
- `attachments = []` (request is for UPLOAD, not transmission)
- `html = false` (doc requests are plain text internally — HTML signature reserved for external outreach)

### Step 4 — Verify MCP routing
Before returning, confirm `account_routing = "chrome_mcp"` in the sub-skill output. If `gmail_mcp` is returned, HALT and report `MCP_ROUTING_VIOLATION`.

### Step 5 — Return draft pointer
Return `draft_id`, draft URL, recipient list. Do NOT auto-send. Keith must explicitly approve via "send it" before transmission (and he screenshots the send per standing rule).

## Layer 5 — Output Schema
Returns draft_id + review link. Never auto-sends.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Wraps draft_outbound_email with CIF-specific defaults. |
