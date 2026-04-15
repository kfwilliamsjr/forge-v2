# Operations — legacy references + pipeline + templates
*Last updated: 2026-04-15*

This folder holds non-skill operational artifacts that used to live loose under `FORGE/` and the project root. They are preserved here for reference. The FORGE_v2 skills do not read from this folder — they read from `FORGE_v2/policy/*.yaml`.

## Layout
```
operations/
├── references/       # Old briefs, guides, call prep, roadmap, security, budget
├── pipeline/         # ACTIVE_PIPELINE.json (live deal state)
└── templates/        # deal_data_schema.json, referral-agreement templates
```

## Rule
- **Source-of-truth lives in `FORGE_v2/policy/`** — not here.
- **Pipeline state lives in `operations/pipeline/ACTIVE_PIPELINE.json`** — skills that need to read/append pipeline state write there.
- **Legacy reference docs** (CONTEXT_BRIEF, SYSTEM_GUIDE, workflow-map) are kept for human reading only. They are NOT loaded by skills. When they conflict with policy YAML, YAML wins.

## What was moved here
- `CONTEXT_BRIEF.md`, `SYSTEM_GUIDE.md` — old agent context files (superseded by CLAUDE.md + FORGE_v2)
- `workflow-map.md`, `control-center.md`, `weekly-audit.md`, `sba-lending-roadmap.md` — operational narrative
- `FORGE_MASTER_PROMPT.md`, `FORGE_TRANSFER_PROMPT.md` — prior session bootstraps
- `IT_SETUP_PLAN.md`, `security-*.md` — infrastructure plan
- `budget-tracker.md`, `automation-backlog.md`, `systems-inventory.md`, `philly-tech-events.md`
- `CDFI_BANK_PROSPECT_LIST.md`, `FIRSTRUST_CALL_BRIEF.md` — prospect intel (referenced by `rank_outreach_prospects` via policy ref, not hardcoded)
- `ACTIVE_PIPELINE.json` → `pipeline/ACTIVE_PIPELINE.json`
- `deal_data_schema.json` → `templates/deal_data_schema.json`
