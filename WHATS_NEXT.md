# What's Next — Sequenced Action List
*Created: 2026-04-15 | Updated after FORGE copy confirmed*

## What I can see now that FORGE is copied

Your legacy FORGE contains 4 actual skills (not 6 as CLAUDE.md described):
- ✅ `cif-cash-flow`
- ✅ `cif-memo-writer`
- ✅ `cif-deal-intake`
- ✅ `borrower-prospecting`
- ❌ `broker-client-intake` — referenced in CLAUDE.md but not built
- ❌ `lead-tiering` — referenced in CLAUDE.md but not built

**Action:** update CLAUDE.md change log to reflect the actual state (2 skills planned, never built).

Also copied into `_legacy_forge/`:
- Substantial operational content: `CONTEXT_BRIEF.md`, `SYSTEM_GUIDE.md`, `workflow-map.md`, `control-center.md`, `weekly-audit.md`, `sba-lending-roadmap.md`, `ACTIVE_PIPELINE.json`, `FORGE_MASTER_PROMPT.md`, `IT_SETUP_PLAN.md`, `security-*.md`, `budget-tracker.md`
- `underwriteos/` engine (the 94-test production-grade Python you inventoried 2026-04-11)

This is more than "skills." You have a partial agent platform already. Some of this merges into FORGE_v2; some stays separate.

---

## Session 2 plan (next session, ~90 minutes)

### Part A — Flesh out the 4 real skills (~60 min)
1. Read each legacy SKILL.md
2. Merge its procedure content into the matching FORGE_v2 stub(s)
3. Promote from `0.9.0-draft` → `1.0.0`
4. Result: 4 legacy skills → 10 atomic skills in v2, all 5-layer compliant, all tested

Mapping:
| Legacy skill | FORGE_v2 atomic splits |
|---|---|
| cif-deal-intake | intake_cif_checklist + generate_cif_deal_data + draft_cif_doc_request_email |
| cif-cash-flow | extract_cif_financials + calculate_business_cash_flow (already gold) + calculate_global_cash_flow + run_cif_stress_tests |
| cif-memo-writer | write_festival_report + write_grant_summary + write_committee_memo |
| borrower-prospecting | score_inbound_leads + mine_bizbuysell_listings + rank_outreach_prospects |

### Part B — Populate core policy YAMLs (~20 min)
5. `colony_grids.yaml` — read from `knowledge-base/lender-grids/colony-bank/`, structure all 16 grids
6. `cif_procedures.yaml` — read from `Swift Capital Underwriting/Credit Policy/CIF_UNDERWRITING_PROCEDURES.md`
7. `lead_scoring.yaml` — pull 100-pt model from legacy borrower-prospecting
8. `sba_sop_50_10.yaml` — skeleton with key thresholds (character, proceeds, collateral margins)

### Part C — Wire in existing assets (~10 min)
9. Decide: `_legacy_forge/CONTEXT_BRIEF.md` — merge into `Agentic_Overhaul/` or deprecate (CLAUDE.md serves this role)
10. Decide: `_legacy_forge/underwriteos/` — this is the Python engine. Does it get called from skills as a computation backend? Recommend: yes, wire it to `calculate_business_cash_flow` as the math engine. Skill reads inputs, passes to underwriteos, gets back deterministic numbers. Best of both worlds: skill file = human-readable procedure, underwriteos = tested Python for the math.

**End of Session 2:** Phase 2 complete. 19 skills exist (1 router + 18 atomic). Core policy YAMLs populated. Ready for live testing.

---

## Session 3 plan (~60 minutes)

### Part A — Golden dataset (~40 min)
1. Pick 3 of the 7 candidate deals (AIPSS recommended first — already validated)
2. Create redacted input package (synthesize PII, preserve math)
3. Write `expected_outputs.json` for each skill that should fire
4. Commit to `FORGE_v2/golden/`

### Part B — Regression runner (~15 min)
5. Simple Python script: `tools/run_golden.py {skill_name}` — executes skill against all golden inputs, diffs against expected, reports pass/fail
6. Usage becomes your pre-deploy check: before any skill gets promoted to production, `run_golden.py` must pass

### Part C — Update CLAUDE.md (~5 min)
7. Add one section to CLAUDE.md: **"Agentic System — see `Agentic_Overhaul/`"** with pointers to README, USER_GUIDE, registry. Don't rewrite CLAUDE.md. It keeps doing what it does.

**End of Session 3:** Phase 3 + 4 foundations complete. You have regression testing, a production agent config, and full audit logging discipline.

---

## Session 4 plan (~45 minutes) — Operational integration

1. Run one live deal end-to-end through the new system (suggest: Tarver / Post Homes — Tier 1-2 broker deal already in pipeline). Compare to how you'd do it manually. Fix any friction.
2. Run one CIF deal through (suggest: Amber Alexander Festival Loan — already in progress). Same comparison.
3. Write operational SOP: "Monday morning routine" and "Friday weekly loop" tuned to your actual week
4. Update `FORGE_v2/SKILL_REGISTRY.csv` with observed accuracy data

**End of Session 4:** Overhaul done. System in production. Weekly improvement loop running.

---

## Beyond session 4 — Ongoing cadence

Weekly (Fridays, 30 min): audit log review → 1 skill improvement → regression test → promote.

Monthly: expand golden dataset by 1 deal. Rotate through edge cases.

Quarterly: review the 6 ops questions. Any drift? Fix it.

Yearly: Colony grid revisions, SOP 50-10 updates → policy YAML version bump, re-run regression.

---

## Open decisions (need your input)

1. **Underwriteos integration.** Do we wire `_legacy_forge/underwriteos/` into `calculate_business_cash_flow` as the math engine? Recommend yes. **Your call.**

2. **Non-skill legacy files** (`control-center.md`, `workflow-map.md`, `weekly-audit.md`, `sba-lending-roadmap.md`, etc.). These are operational documents, not skills. Options:
   - a) Move them to `Agentic_Overhaul/operations/` (cleanest)
   - b) Leave them in `_legacy_forge/` and reference from CLAUDE.md
   - c) Merge useful content into this overhaul's docs, delete the rest
   
   Recommend (a). **Your call.**

3. **Phantom skills** (broker-client-intake, lead-tiering). CLAUDE.md documented them as built. They're not. Do you want them built now, or is that scope creep?
   - `broker-client-intake` — probably worth building (you have live broker deals this week). Could fold into a single `intake_broker_client` skill.
   - `lead-tiering` — already effectively inside `score_inbound_leads`. Probably redundant.
   
   **Your call.**

4. **CLAUDE.md treatment.** Narrative change log, very heavy. Keep as-is and add pointer, or slim it down?
   
   Recommend keep as-is + pointer. Don't break what works. **Your call.**

---

## Right now, today

You have:
- ✅ Full plan + audit
- ✅ Visual roadmap
- ✅ Isolated portable folder
- ✅ 4 production-quality skill exemplars
- ✅ 15 atomic skill stubs (Layers 1+2 done)
- ✅ agent.json with hard rules, halt behavior, MCP routing
- ✅ 2 policy YAMLs populated (broker_rules, email_voice_rules)
- ✅ Audit log format
- ✅ Golden dataset plan
- ✅ User guide
- ✅ Next-steps doc (this file)

**Before you start Session 2, answer the 4 open decisions above.** 5-minute task. That unblocks everything else.

Then in the next Cowork session say:
> Continue Phase 2 from Agentic_Overhaul/WHATS_NEXT.md. Execute Session 2 Part A, B, C. Here are my answers to the 4 open decisions: [your answers].

And we go.
