# Schema Conventions — FORGE v2
*Version: 1.0 | Last updated: 2026-04-15*

These conventions apply to every skill in the library. Non-negotiable.

## File & Folder Rules
- One skill per folder. Folder name = skill name in `snake_case`.
- Each skill folder contains exactly three files: `SKILL.md`, `CHANGELOG.md`, optional `EXAMPLES.md`.
- Master registry: `FORGE_v2/SKILL_REGISTRY.csv` — every skill listed with version + status.

## The 5 Layers (all mandatory)
1. **Trigger Description** — when to invoke
2. **Negative Trigger** — when NOT to invoke
3. **Input Schema** — typed field table with required flags
4. **Procedure** — numbered deterministic steps
5. **Output Schema** — typed return contract

Missing any layer = skill is not production-eligible.

## Versioning
- SemVer: `major.minor.patch`
- Patch = clarification/typo fix
- Minor = new optional input field, additional output field, expanded negative triggers
- Major = breaking change to input/output schema, threshold change, policy change
- Never overwrite. Old version archived in `_legacy/v{x.y.z}/` subfolder.

## Halt Behavior (uniform across all skills)
When required input is missing:
```json
{
  "status": "halt",
  "skill": "{skill_name}",
  "version": "{version}",
  "missing_fields": ["field_a", "field_b"],
  "message": "Human-readable reason",
  "audit_ref": "audit/{deal_id}.jsonl#line{n}"
}
```

Never estimate. Never guess. Halt and report.

## Standard Field Types
| Type | Format | Example |
|------|--------|---------|
| string | UTF-8 | "Bellanti Holdings LLC" |
| float | no commas, 2 decimals for money | 350000.00 |
| int | whole number | 680 |
| date | ISO 8601 | "2026-04-15" |
| currency | float + implied USD | 350000.00 |
| percent | float, 0-100 | 25.50 |
| ratio | float, 2 decimals | 1.23 |
| file | absolute path string | "/path/to/doc.pdf" |
| enum | one of listed values | "SBA" \| "Festival" \| "Grant" |

## Common Output Fields (all skills return)
Every skill output MUST include:
- `status` — "ok" | "halt" | "flag"
- `skill` — skill name
- `version` — semver string
- `timestamp` — ISO 8601
- `audit_ref` — pointer to log entry

## Audit Log Format (JSONL, append-only)
One line per skill invocation. Path: `audit/{deal_id}.jsonl`

```json
{"ts":"2026-04-15T14:32:11Z","deal_id":"BEL_2026-04","skill":"calculate_dscr","version":"1.0.0","inputs_hash":"sha256:abc...","outputs_hash":"sha256:def...","status":"ok","rationale":"NOI $142K, debt service $98K, ratio 1.45x"}
```

## Policy References
Skills do NOT hardcode thresholds. All policy lives in `policy/*.yaml`:
- `policy/colony_grids.yaml` — Colony Bank SBSL loan grids
- `policy/cif_procedures.yaml` — CIF underwriting procedures
- `policy/sba_sop_50_10.yaml` — SBA SOP thresholds
- `policy/broker_rules.yaml` — broker business policies (MCA exclusion, Form 159, etc.)

Skill reads YAML → applies threshold. Policy change = edit one YAML file. All skills inherit.

## Naming Conventions
- Skill names: `verb_object` snake_case. `calculate_dscr`, `extract_tax_returns`, `write_committee_memo`.
- Never generic: no `underwrite_loan`, no `process_deal`, no `handle_email`.

## Router Contract
Every skill MUST have a trigger description distinct from every other skill. The router picks one skill per input. If two skills could fire, one trigger is wrong — fix it, don't let the router guess.
