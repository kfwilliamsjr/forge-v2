# Agentic Flow Overhaul — Audit & Plan
*Created: 2026-04-15 | Status: DRAFT awaiting Keith approval | No skills modified yet*

## 1. Source of Standards
Anthropic Master Build Guide (uploaded 2026-04-15). Core mandates:
- Every skill has 5 layers: **Trigger | Negative Trigger | Input Schema | Procedure | Output Schema**
- Every skill is **atomic** — one job
- Every skill is **versioned** with a changelog
- Every invocation is **logged**
- Build a **router** skill and a **golden dataset**
- Biggest leverage point: **Policy Engine MCP**

## 2. Skill-by-Skill Audit

Legend: ✅ present | ❌ missing | ⚠️ partial

| Skill | Location | Trigger | Neg Trigger | Input Schema | Procedure | Output Schema | Versioned | Atomic | Score |
|-------|----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| sba-deal-screener | `SBA_Lending_Claude_MD/skills/` | ✅ | ❌ | ⚠️ | ⚠️ | ❌ | ❌ | ❌ (3 jobs) | 2/7 |
| email-drafter | `SBA_Lending_Claude_MD/skills/` | ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ✅ | 2/7 |
| cif-deal-intake | `FORGE/skills/` (not mounted) | likely ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ (3 jobs) | ~1/7 |
| cif-cash-flow | `FORGE/skills/` | likely ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ (4 jobs) | ~1/7 |
| cif-memo-writer | `FORGE/skills/` | likely ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ (3 doc types) | ~1/7 |
| borrower-prospecting | `FORGE/skills/` | likely ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ (3 modes) | ~1/7 |
| broker-client-intake | `FORGE/skills/` | unknown | ❌ | ❌ | ? | ❌ | ❌ | ? | unknown |
| lead-tiering | `FORGE/skills/` | unknown | ❌ | ❌ | ? | ❌ | ❌ | ? | unknown |

**Verdict:** every skill in the library needs structural rework. None are currently production-grade by the guide's standard.

## 3. System-Level Findings

| # | Gap | Impact | Severity |
|---|-----|--------|:-:|
| 1 | No router skill | Overlapping triggers → wrong skill fires silently | HIGH |
| 2 | No `agent.json` config | No halt_on_missing_input, no invocation logging | HIGH |
| 3 | No audit log | Cannot answer "which version ran on this deal?" | HIGH (regulated) |
| 4 | No golden dataset | Skill changes ship without regression testing | HIGH |
| 5 | No Policy Engine MCP | Every policy change = manual skill rewrite | MEDIUM → the biggest future leverage |
| 6 | Skill library fragmented (3 paths) | No single "what's in production" answer | MEDIUM |
| 7 | CLAUDE.md mixes narrative memory with skill docs | Router has no clean registry to read | LOW |
| 8 | G8WAY manual entry (openpyxl corrupts) | Kills cash-flow skill automation | HIGH (separate track) |
| 9 | Dual email context (Gmail MCP + Chrome MCP for Swift) | Re-explained each session | LOW (fix via agent.json) |

## 4. Phased Overhaul Plan

### Phase 1 — Visibility & Audit (this session, read-only)
- [x] Produce this audit doc
- [x] Produce visual roadmap (HTML)
- [ ] Produce full skill registry after reading FORGE folder (requires Keith to mount `~/Desktop/FORGE/`)
- **Deliverables:** `AUDIT_AND_PLAN.md`, `ROADMAP.html`, `SKILL_REGISTRY.csv`
- **Risk:** zero. Nothing is modified.

### Phase 2 — Standardize Skills (1–2 sessions)
For each skill:
1. Add Negative Trigger block (Keith writes the exceptions from domain knowledge; Claude drafts)
2. Add Input Schema (table: field | type | required)
3. Add Output Schema (exact return contract)
4. Rewrite procedure as numbered deterministic steps
5. Version at `v1.0` + create `CHANGELOG.md` in skill folder
6. **Split multi-job skills into atomic skills:**
   - `cif-cash-flow` → `extract_cif_financials` + `calculate_business_cash_flow` + `calculate_global_cash_flow` + `run_stress_tests`
   - `cif-memo-writer` → `write_festival_report` + `write_grant_summary` + `write_committee_memo`
   - `borrower-prospecting` → `score_inbound_leads` + `mine_bizbuysell` + `rank_outreach_prospects`
   - `cif-deal-intake` → `run_cif_checklist` + `generate_deal_data_json` + `draft_doc_request_email`
   - `sba-deal-screener` → `extract_deal_parameters` + `match_colony_grid` + `calculate_broker_commission`
7. Consolidate all skills under ONE library path: `~/Desktop/FORGE/skills/` (move SBA + email-drafter there).
- **Deliverables:** 15–18 atomic skill files, each 5-layer compliant, versioned.
- **Risk:** medium. Live workflows must keep running. Mitigation: old skills stay in place as `_legacy/` until new ones pass golden-dataset tests.

### Phase 3 — Router + Agent Config (1 session)
- Build `route_task.md` — first skill invoked on every request. Classifies (CIF / SBA broker / grant / email / prospecting) → returns dispatch plan.
- Write `agent.json`:
  ```json
  {
    "agent_id": "sba_lending_agent_v1",
    "version": "1.0.0",
    "skill_directory": "~/Desktop/FORGE/skills/",
    "routing_skill": "route_task.md",
    "execution_rules": {
      "max_skill_chain_depth": 6,
      "require_router_first": true,
      "halt_on_missing_input": true,
      "log_skill_invocations": true
    },
    "audit": {
      "log_path": "~/Desktop/FORGE/audit/",
      "log_skill_selected": true,
      "log_skill_version": true,
      "log_decision_rationale": true
    }
  }
  ```
- Stand up append-only JSONL audit log per deal: `FORGE/audit/{deal_id}.jsonl`
- **Deliverables:** router skill, agent.json, audit scaffold.
- **Risk:** low. Parallel to live work.

### Phase 4 — Golden Dataset + Policy MCP (ongoing, 2–4 weeks)
- Lock 7 deals as golden: AIPSS, Mirzai, TTH, Heavy Highway, Elite Cargo, Tallahassee, Advanced Integrated Pain. Each deal = input folder + expected output.
- QA protocol: every skill change runs against golden set before promotion. >2% human correction rate = skill needs rework.
- **Policy Engine MCP (lightweight v1):** YAML-ify Colony grids + CIF procedures + SBA SOP thresholds. Skills read from `policy/*.yaml` instead of hardcoding thresholds. Policy change = one YAML edit, all skills get it.
- **Deliverables:** `FORGE/golden/` folder, `FORGE/policy/*.yaml`, QA script.
- **Risk:** low — additive.

## 5. Out of Scope for This Overhaul
- Fixing G8WAY xlsx corruption (separate initiative — migrate to Google Sheets or build macro-enabled xlsm template)
- Rewriting CLAUDE.md (keep as narrative memory; add pointer to skill registry)
- Building Gmail/Chrome MCP unification (Phase 3 agent.json handles the routing rule)
- ClearPath tool refactor (separate product)

## 6. The One-Screen Truth
You have strong domain content and weak agentic scaffolding. The overhaul adds scaffolding without rewriting your expertise. After Phase 3 you'll have: one skill library, one router, one audit log, one agent config, and golden-dataset regression testing. That puts you ahead of 95% of lending shops using AI — most don't even know to ask these questions.

## 7. Decision Required From Keith
1. **Approve Phase 1 scope?** (this audit + registry + roadmap — no code changes)
2. **Mount `~/Desktop/FORGE/` in next session** so I can read the actual FORGE skills and complete the registry?
3. **Approve Phase 2 decomposition plan?** (15–18 atomic skills replacing 8 current ones)
4. **Reserve 2 sessions this week for Phase 2 execution?**

Nothing moves until you say go.
