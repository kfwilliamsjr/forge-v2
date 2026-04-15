---
name: show_system_map
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 5-routing
depends_on: []
policy_refs: []
---

# SKILL: show_system_map

## Layer 1 — Trigger Description
Render and surface the FORGE v2 System Swim-Lane Map — a single-file HTML with five Mermaid diagrams (architecture, CIF swim-lane, SBA-broker swim-lane, policy YAML map, next-build plan). Fires on Keith's request (explicit trigger) AND automatically at the start of any build, refactor, or skill-creation session (implicit trigger). Purpose: give Keith a visual anchor during internal build work AND a client-ready diagram when explaining the operation to a prospective underwriting customer.

## Layer 2 — Negative Trigger
- Do NOT render inline ASCII copies of the map — always link the HTML file.
- Do NOT regenerate the map every message; generate once per session unless the system structure has changed (new skill, new YAML, new tier) — then regenerate and bump the `Last updated` timestamp in the HTML.
- Do NOT simplify the map for "casual" questions — the full map IS the simplification. Keith reads the whole thing.
- Do NOT strip the "This is prototype — expected values pending real-memo reconciliation" caveat when showing to a customer. Trust and accountability.

## Layer 3 — Input Schema
| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| reason | enum | No | caller | `"keith_request"` \| `"building"` \| `"client_demo"` \| `"auto_start"` |
| regenerate | bool | No | caller | Force rebuild from current SKILL_REGISTRY.csv + policy/ |

## Layer 4 — Procedure

### Step 1 — Explicit trigger detection
Fire when `user_input` matches any of:
- "show me the map" / "show the system map" / "show me how this works"
- "walk me through the system" / "explain the system"
- "map it out" / "visual" / "diagram"
- "I'm explaining this to a customer" / "client demo" / "walk through for [name]"

### Step 2 — Implicit trigger (auto-fire when building)
Fire automatically at the start of a session whenever the user's opening intent matches any of:
- Building a new skill / policy YAML / golden fixture
- Refactoring the agentic system
- Adding a lender, product type, or tier
- Session-resume messages that reference Session 2/3/4 build work
- Any message containing: "build", "overhaul", "refactor", "proceed" (when prior context is build-related)

On auto-fire: surface the link at the top of the response, then continue with the requested work. Do not pause the build for acknowledgment.

### Step 3 — Freshness check
Compare HTML `Last updated` timestamp to mtime of:
- `FORGE_v2/SKILL_REGISTRY.csv`
- `FORGE_v2/policy/*.yaml`
- `FORGE_v2/skills/*/SKILL.md`

If any is newer than the HTML, regenerate.

### Step 4 — Regeneration (when needed)
Rebuild `Agentic_Overhaul/SYSTEM_MAP_v2.html` from templates embedded in this skill. Reads:
- Skill list from `SKILL_REGISTRY.csv` (status, tier, lane)
- Policy YAML list from `policy/` directory
- Lane-skill mapping derived from `lane` column + `depends_on`

Keep the 5-panel layout fixed. Refresh the skill-node names and the policy YAML map.

### Step 5 — Surface to user
Emit a minimal response:
```
[View System Map](computer:///sessions/modest-brave-bohr/mnt/SBA_Lending_Claude_MD/Agentic_Overhaul/SYSTEM_MAP_v2.html)
```
Then proceed with whatever work was actually requested. No preamble, no narration of what the map contains — the map contains itself.

### Step 6 — Client-demo mode
If `reason == client_demo` OR Keith signals he's showing this to a prospect:
- Keep the link at the top.
- Append a 3-sentence plain-English description suitable for reading aloud while the customer looks at the diagram:
  1. "Every request enters through a router that picks the right lane."
  2. "Each lane walks the deal through six tiers — extraction, calculation, risk, output, routing, comms — all governed by policy YAMLs with no hardcoded numbers."
  3. "DSCR math never touches an LLM — it runs on a tested Python engine with 94 passing tests."
- Do NOT add sales language. The diagram + the three sentences is the pitch.

### Step 7 — Audit
Log trigger type (`keith_request` / `building` / `client_demo` / `auto_start`) and whether regeneration fired. Append to `audit/show_system_map.jsonl`.

## Layer 5 — Output Schema
```json
{
  "status": "ok",
  "skill": "show_system_map",
  "version": "1.0.0",
  "map_path": "Agentic_Overhaul/SYSTEM_MAP_v2.html",
  "map_url": "computer:///sessions/modest-brave-bohr/mnt/SBA_Lending_Claude_MD/Agentic_Overhaul/SYSTEM_MAP_v2.html",
  "trigger_type": "keith_request | building | client_demo | auto_start",
  "regenerated": false,
  "last_updated_timestamp": "2026-04-15"
}
```

## Examples

### Example 1 — Keith asks mid-build
User: "show me the map"
→ Link surfaced. No other output. Work continues.

### Example 2 — Auto-fire on build session
User: "proceed with Session 4"
→ Map link at top of response, then Session 4 work continues immediately.

### Example 3 — Client demo
User: "I'm on a call with a potential UW customer, walk me through the system"
→ Link + 3-sentence plain-English script appended. Nothing else.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-15 | Initial. Keith requested persistent visual anchor for builds + client demos. |
