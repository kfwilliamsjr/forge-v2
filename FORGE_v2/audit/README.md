# Audit Log — FORGE v2
*Created: 2026-04-15 | Append-only | Retention: 7 years (2555 days)*

Every skill invocation writes one JSONL line here. This is your compliance trail and silent-failure detector.

## File layout
- `audit/{deal_id}.jsonl` — per-deal log for underwriting/broker deals
- `audit/comms.jsonl` — all email drafts + sends across accounts
- `audit/routing.jsonl` — router decisions across all inputs (cross-deal pattern analysis)

## Line format (JSONL)
```json
{
  "ts": "2026-04-15T14:32:11Z",
  "deal_id": "BEL_2026-04",
  "skill": "calculate_business_cash_flow",
  "version": "1.0.0",
  "policy_versions_applied": {"cif_procedures.yaml": "1.0.0"},
  "inputs_hash": "sha256:abc...",
  "outputs_hash": "sha256:def...",
  "status": "ok",
  "rationale": "NOI $142K, debt service $98K, DSCR 1.45x >= 1.25 threshold",
  "human_correction": null
}
```

## What each field is for
| Field | Purpose |
|-------|---------|
| ts | Timestamp (ISO 8601 UTC) |
| deal_id | Which deal this decision belongs to |
| skill | Which skill fired |
| version | SemVer at time of run (critical for "which version ran on this file?") |
| policy_versions_applied | Snapshot of policy versions used |
| inputs_hash | SHA-256 of normalized input JSON — for reproducibility |
| outputs_hash | SHA-256 of output JSON — tamper detection |
| status | ok / halt / flag |
| rationale | Human-readable reason (Master Guide: "log decision rationale") |
| human_correction | null until Keith corrects. When corrected, this field logs the correction for the improvement loop. |

## Append-only discipline
Never edit past lines. Corrections are NEW lines with `event: "correction"` and a pointer to the original line number.

## Retention
SBA/CDFI regulatory best practice: 7 years from loan maturity or decision. Default `retention_days: 2555` in `agent.json`.

## Reading the log
```bash
# Find every skill that ran on a deal
cat audit/BEL_2026-04.jsonl | jq .skill

# Find every halt in the last 7 days
find audit/ -name "*.jsonl" -mtime -7 | xargs grep '"status":"halt"'

# Count routing decisions by intent
cat audit/routing.jsonl | jq .classified_intent | sort | uniq -c
```

## The 6 questions this log answers (per Master Guide)
1. What skills are currently in production? → grep unique skill names
2. What version is each skill? → grep unique (skill, version) pairs
3. When was each skill last tested? → cross-reference with golden/ run logs
4. Which MCP servers are connected? → agent.json
5. Where are the audit logs? → right here
6. What happens when the agent is uncertain? → grep status:halt + status:flag
