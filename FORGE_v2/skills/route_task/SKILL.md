---
name: route_task
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 5-routing
depends_on: []
policy_refs: []
---

# SKILL: route_task

**This skill runs FIRST on every agent invocation. No other skill fires until this one completes.**

## Layer 1 — Trigger Description
Use on every inbound request (voice, text, email forward, file drop, scheduled task). Reads the user input, classifies the task, confirms required inputs are present, returns a dispatch plan specifying which skill(s) to invoke in what order.

## Layer 2 — Negative Trigger
- Do NOT use if the request is pure conversation (e.g., "hi", "thanks", status question Claude can answer directly from CLAUDE.md without running a skill).
- Do NOT use if a prior route_task has already been logged for this same deal_id in the current session AND the user input is a continuation (no new intent).
- Do NOT dispatch downstream skills if required inputs are missing — return halt with the missing-inputs list.
- Do NOT invoke more than one skill per classified intent. If two skills plausibly fit, one trigger is ambiguous — flag for Keith.

## Layer 3 — Input Schema
| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| user_input | string | Yes | chat / forward / task | Raw request text |
| deal_id | string | No | inferred from borrower name or explicit | Format: `{SHORT}_{YYYY-MM}` (e.g., `BEL_2026-04`) |
| attached_files | list[file] | No | uploads | Paths to any uploaded docs |
| context_hint | enum | No | user | `"CIF"` \| `"SBA_broker"` \| `"prospecting"` \| `"comms"` \| `"grant"` \| `null` |

## Layer 4 — Procedure

### Step 1: Classify intent
Match `user_input` against the trigger table below. Pick the SINGLE best match. If confidence < 0.8 (i.e., two triggers could fit), HALT and ask Keith to disambiguate.

| Intent | Lane | Keywords / Patterns | Dispatch |
|--------|------|---------------------|----------|
| New CIF deal intake | CIF | "intake [name]", "new CIF deal", "onboard [borrower]" | `intake_cif_checklist` → `generate_cif_deal_data` → `draft_cif_doc_request_email` |
| CIF cash flow analysis | CIF | "cash flow for [name]", "DSCR for [name]", "run numbers" | `extract_cif_financials` → `calculate_business_cash_flow` → `calculate_global_cash_flow` → `run_cif_stress_tests` |
| CIF committee memo | CIF | "write memo", "draft memo", "committee report" | `write_committee_memo` |
| CIF festival report | CIF | "festival report", "festival loan" | `write_festival_report` |
| CIF grant summary | CIF | "grant summary", "VI Leap" | `write_grant_summary` |
| SBA deal screening | SBA | "screen this deal", "is this deal eligible", "Colony grid" | `extract_sba_deal_parameters` → `match_colony_grid` → `calculate_broker_commission` |
| SBA character / LOE | SBA | "LOE needed", "character determination", "derogatory credit" | `screen_sba_character_loe_needed` |
| Score inbound leads | Prospecting | "score leads", "supabase leads", "rank inbound" | `score_inbound_leads` |
| Mine listings | Prospecting | "mine bizbuysell", "find acquisition targets" | `mine_bizbuysell_listings` |
| Rank outreach prospects | Prospecting | "who should I call", "rank prospects", "CDFI outreach" | `rank_outreach_prospects` |
| Draft outbound email | Comms | "draft email", "email [name]", "reach out", "follow up" | `draft_outbound_email` |

### Step 2: Validate required inputs
For the dispatched skill chain, check that each skill's Layer 3 required fields are resolvable from `attached_files` + `user_input` + `deal_id`. If any required field is missing:
```json
{"status": "halt", "reason": "missing_input", "skill": "{first_skill_in_chain}", "missing": ["field_a"], "message": "Cannot run {skill}. Need: {field_a}. Upload or provide."}
```

### Step 3: Log the routing decision
Append to `audit/{deal_id}.jsonl`:
```json
{"ts":"ISO","event":"route","input_excerpt":"first 80 chars","classified_intent":"...","confidence":0.95,"dispatch_chain":["skill_a","skill_b"],"reason":"matched keyword 'cash flow for'"}
```

### Step 4: Dispatch
Invoke first skill in chain with resolved inputs. On its `ok` return, pass outputs to next skill. On any `halt` from downstream, stop the chain and surface the halt to Keith.

### Step 5: Uncertainty handling
- Confidence < 0.8 → HALT, ask Keith to clarify intent
- No intent matched → HALT, surface the input with suggestion: "Not matched to any skill. Closest match: {skill}. Proceed?"
- Two skills plausibly fit → flag as routing-trigger-overlap bug, log for weekly review

## Layer 5 — Output Schema
```json
{
  "status": "ok" | "halt",
  "skill": "route_task",
  "version": "1.0.0",
  "timestamp": "ISO",
  "deal_id": "...",
  "classified_intent": "...",
  "confidence": 0.0,
  "dispatch_chain": ["skill_a", "skill_b"],
  "audit_ref": "audit/{deal_id}.jsonl#line{n}"
}
```

If `status: halt`:
```json
{
  "status": "halt",
  "reason": "low_confidence" | "missing_input" | "no_match" | "trigger_overlap",
  "options": ["skill_a", "skill_b"],
  "message": "Human-readable prompt for Keith"
}
```

## Examples

### Example 1 — Clean routing
**Input:** "Build cash flow for Bellanti"
→ Intent: CIF cash flow analysis | Confidence: 0.96
→ Chain: `extract_cif_financials` → `calculate_business_cash_flow` → `calculate_global_cash_flow` → `run_cif_stress_tests`

### Example 2 — Missing input halt
**Input:** "Score the inbound leads"
→ Intent: Score inbound leads | Confidence: 0.98
→ Chain: `score_inbound_leads`
→ But required input `supabase_export_file` is missing
→ Status: halt | Message: "Cannot run score_inbound_leads. Need: supabase_export_file. Export today's leads and upload."

### Example 3 — Trigger overlap
**Input:** "Write up Bellanti for Pat"
→ Could match: `write_committee_memo` OR `write_festival_report`
→ Confidence: 0.65 (ambiguous)
→ Status: halt | Message: "Two skills could fit. Is this a committee memo or a festival report?"

## Changelog
| Version | Date | Change | Approved by |
|---------|------|--------|-------------|
| 1.0.0 | 2026-04-15 | Initial router. 11 intents across 4 lanes. | Keith Williams (pending) |
