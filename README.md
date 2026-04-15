# Agentic Overhaul — Portable Home
*Created: 2026-04-15 | Owner: Keith Williams | Status: Phase 1 complete, Phase 2 in progress*

## What this folder is
A single, portable, isolated home for Keith's entire agentic system overhaul. Every skill, policy, audit log, and piece of governance lives inside this folder. Zip it → upload anywhere → full system travels with it.

## Why it exists
Audit of existing skills against Anthropic's Agentic Workflow Master Build Guide (2026-04-15) revealed structural gaps: no negative triggers, no input/output schemas, no versioning, no router, no audit log, no golden dataset. Domain content is strong; scaffolding is weak. This overhaul adds the scaffolding without rewriting the expertise.

## Folder map

```
Agentic_Overhaul/
├── README.md                      ← you are here
├── AUDIT_AND_PLAN.md              ← full audit + 4-phase plan
├── ROADMAP.html                   ← visual roadmap
├── HOW_TO_MOUNT_FORGE.md          ← copy your existing FORGE here
├── _legacy_forge/                 ← (Keith copies ~/Desktop/FORGE/ here)
└── FORGE_v2/                      ← the new clean skill library
    ├── agent.json                 ← agent config (halt rules, MCPs, hard rules, retention)
    ├── SCHEMA_CONVENTIONS.md      ← the 5-layer standard + field types
    ├── SKILL_REGISTRY.csv         ← every skill, version, status, dependencies
    ├── skills/                    ← 19 skill folders (1 production, 3 exemplars, 15 stubs)
    │   ├── _template/             ← canonical 5-layer template
    │   ├── route_task/            ← [PRODUCTION] routes every request
    │   ├── calculate_business_cash_flow/  ← [EXEMPLAR] gold standard
    │   ├── match_colony_grid/     ← [EXEMPLAR] gold standard
    │   ├── draft_outbound_email/  ← [EXEMPLAR] gold standard
    │   └── ...15 atomic skill stubs (flesh out next session)
    ├── policy/                    ← YAML policy files (replaces hardcoded thresholds)
    │   ├── README.md
    │   ├── broker_rules.yaml      ← [POPULATED] MCA exclusion, commission schedule
    │   └── email_voice_rules.yaml ← [POPULATED] voice, account routing, banned phrases
    ├── golden/                    ← regression test dataset (PII-redacted)
    │   └── README.md              ← 10 candidate deals listed
    └── audit/                     ← append-only JSONL logs per deal
        └── README.md              ← log format + the 6 ops questions answered
```

## What's complete (today)
- ✅ Isolated portable folder
- ✅ 5-layer SKILL template + SCHEMA_CONVENTIONS
- ✅ Router skill (production-ready v1.0.0)
- ✅ 3 gold-standard exemplar skills (one per lane)
- ✅ 15 atomic skill stubs (Layers 1+2 populated)
- ✅ agent.json with halt rules, MCP routing, hard-rule list, retention policy
- ✅ 2 policy YAMLs populated (broker_rules, email_voice_rules)
- ✅ Golden dataset scaffold (10 candidate deals listed)
- ✅ Audit log scaffold (JSONL format + reading commands)
- ✅ Skill registry CSV

## What's next (Phase 2 completion)
Requires FORGE copied into `_legacy_forge/`:
- [ ] Flesh out 15 stub skills from legacy FORGE content
- [ ] Populate remaining policy YAMLs (`colony_grids.yaml`, `cif_procedures.yaml`, `sba_sop_50_10.yaml`, `vi_leap_grant_rules.yaml`, `lead_scoring.yaml`, `bizbuysell_filters.yaml`)
- [ ] Redact + structure 7 golden dataset deals
- [ ] Build simple Python regression runner for golden set
- [ ] Update CLAUDE.md with pointer to this folder (one line, not a rewrite)

## When you're ready to use this
1. Copy FORGE per `HOW_TO_MOUNT_FORGE.md` (5 seconds via Terminal)
2. Tell next session: "Read `Agentic_Overhaul/README.md`. We're continuing Phase 2 — flesh out the stub skills from `_legacy_forge/`."
3. That's the complete handoff — no other context needed.

## Portability promise
Zip this folder = portable agentic system. No dependencies outside it except:
- MCP servers (defined in `agent.json`, external configs)
- Python script `generate_loan_report_pdf.py` (referenced, lives in Swift Capital Templates)
- Source documents per deal (always borrower-specific, not in this folder)

## The Master Guide's 6 questions — can you answer them?
1. What skills are in production? → `SKILL_REGISTRY.csv` (today: 1 production, 3 exemplar, 15 stub)
2. What version is each skill? → `SKILL_REGISTRY.csv` version column
3. When was each skill last tested? → golden runner logs (Phase 4)
4. Which MCP servers are connected? → `agent.json → mcp_servers`
5. Where are the audit logs? → `audit/` (populated once Phase 3 goes live)
6. What happens when agent is uncertain? → `agent.json → uncertainty_behavior` (halt, don't guess)

Five of six answerable today. The sixth (audit logs) activates when skills run under `agent.json` enforcement in Phase 3.
