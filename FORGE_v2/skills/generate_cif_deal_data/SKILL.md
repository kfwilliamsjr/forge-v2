---
name: generate_cif_deal_data
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 1-extraction
depends_on: [intake_cif_checklist]
policy_refs: [policy/cif_procedures.yaml]
---

# SKILL: generate_cif_deal_data

## Layer 1 — Trigger Description
Use after CIF intake checklist is complete and readiness score ≥70. Produces the canonical `deal_data.json` file for the deal — single source of truth consumed by all downstream CIF skills (cash flow, memo, stress tests).

## Layer 2 — Negative Trigger
- Do NOT run if `intake_cif_checklist` returned readiness_score < 70 or status = halt.
- Do NOT include raw PII (full SSN, account numbers) in deal_data.json — only aggregated / hashed values.
- Do NOT overwrite an existing deal_data.json — version it (v1 → v2) in the deal folder.
- Do NOT populate fields not validated against source documents (every value must have `source` attribute).

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| intake_checklist_output | object | Yes |
| source_doc_paths | list[file] | Yes |

## Layer 4 — Procedure

### Step 1 — Locate or create deal folder
Path: `Deals_Swift Capital/{borrower_name_normalized}/`. Normalize: replace spaces with underscores, strip punctuation. Fuzzy-match existing folders before creating new (e.g., "JJ Creationz" matches "JJ_Creationz"). If folder exists with `deal_data.json`, read it → Step 2 (update mode). If not, create scaffold: `deal_data.json`, `Report/`, `Report/Old Drafts/`, `Notes/`, `Drafts/`.

### Step 2 — Populate canonical fields
Fields populated at intake stage only (financials stay null until `extract_cif_financials` runs):

```json
{
  "deal_id": "<lowercase-hyphenated-borrower>",
  "schema_version": "1.0.0",
  "policy_version": "<from cif_procedures.yaml>",
  "borrower": {
    "name": "<legal name>",
    "dba": "<if applicable>",
    "entity_type": "<LLC|Corp|Sole Prop|...>",
    "state": "<USVI|...>",
    "ownership": []
  },
  "request": {
    "deal_type": "<festival_loan|vi_leap_grant|regular_loan>",
    "amount": 0,
    "use_of_proceeds": null,
    "term_months": null,
    "rate": null
  },
  "status": "intake",
  "stage": "pending_docs",
  "dates": {
    "intake": "<today YYYY-MM-DD>",
    "docs_complete": null,
    "cash_flow_complete": null,
    "memo_drafted": null,
    "submitted_to_akem": null,
    "submitted_to_committee": null,
    "committee_decision": null
  },
  "checklist": [<from intake output, each item with item/status/source>],
  "financials": null,
  "cash_flow": null,
  "credit": null,
  "deliverables": {"docx": null, "pdf": null, "xlsx": null},
  "audit_refs": []
}
```

### Step 3 — Enforce PII scrubbing rules
- NEVER write full SSN. Write last-4 only, prefixed `xxx-xx-`.
- NEVER write full account numbers. Write last-4 only.
- NEVER write full DOB. Write year only if required.
- Credit scores are OK (not PII under CIF policy).

### Step 4 — Version existing files
If `deal_data.json` already exists and differs materially, move old to `deal_data.v{N}.json` before writing new. Never delete old versions (retention = committee decision + 30 days per `agent.json`).

### Step 5 — Update ACTIVE_PIPELINE.json
Append or update the pipeline entry with: deal_id, borrower name, deal_type, status, stage, next_action, priority.

### Step 6 — Write audit entry
Log: skill=generate_cif_deal_data, deal_id, schema_version, policy_version, write_mode (create|update|version-bump).

### Step 7 — Return pointer + validation summary
Return absolute path to deal_data.json + list of fields populated vs null + any schema validation warnings.

## Layer 5 — Output Schema
Writes `Deals_Swift Capital/{deal_name}/deal_data.json` conforming to master schema. Returns pointer + validation summary.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Uses existing deal_data_schema.json from SBA_Lending_Claude_MD. |
