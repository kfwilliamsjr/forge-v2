---
name: skill_name_in_snake_case
version: 1.0.0
last_updated: YYYY-MM-DD
owner: Keith Williams
status: draft | production | deprecated
tier: 1-extraction | 2-calculation | 3-risk-compliance | 4-output | 5-routing | 6-comms
depends_on: [other_skill_names]
policy_refs: [policy/colony_grids.yaml, policy/cif_procedures.yaml, policy/sba_sop_50_10.yaml]
---

# SKILL: {human_readable_name}

## Layer 1 — Trigger Description
ONE sentence. Specific domain language. Tells the router WHEN to invoke this skill.

**Good example:** "Use when a CIF borrower submits a Festival Loan application requiring a cash-flow-based microloan recommendation."

**Bad example:** "Use for CIF stuff."

## Layer 2 — Negative Trigger (MANDATORY)
Explicit boundaries. When this skill must NOT fire.

- Do NOT use if {exception_1}
- Do NOT use if {exception_2}
- Do NOT use for {out_of_scope_case}

These are the most important lines in the file. Write the exceptions from your underwriting experience.

## Layer 3 — Input Schema
Every field the skill needs before it can run. Missing required field = HALT, do not guess.

| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| borrower_legal_name | string | Yes | intake_form | — |
| loan_amount | float | Yes | intake_form | USD, no commas |
| tax_returns | list[file] | Yes | ShareFile | 2 years min |
| {field} | {type} | {Yes/No} | {source} | {notes} |

**Halt rule:** if any required field is missing or unparseable, return `{"status": "halt", "missing": [field_names]}` and stop.

## Layer 4 — Procedure
Numbered, deterministic steps. No implicit logic.

1. Validate all required inputs per Layer 3. If missing, HALT.
2. Load policy from `policy/{file}.yaml` — do NOT hardcode thresholds.
3. {specific_step}
4. {specific_step}
5. Log invocation to `audit/{deal_id}.jsonl` with skill name, version, inputs hash, timestamp.
6. Return output per Layer 5 schema.

## Layer 5 — Output Schema
Exact shape of what this skill returns. Downstream skills depend on this contract.

| Field | Type | Description |
|-------|------|-------------|
| status | string | "ok" \| "halt" \| "flag" |
| {result_field} | {type} | {description} |
| audit_ref | string | Path to audit log entry |

**Example output:**
```json
{
  "status": "ok",
  "result_field": "value",
  "audit_ref": "audit/2026-04-15_bellanti.jsonl#line42"
}
```

## Changelog
| Version | Date | Change | Approved by |
|---------|------|--------|-------------|
| 1.0.0 | YYYY-MM-DD | Initial version | Keith Williams |
