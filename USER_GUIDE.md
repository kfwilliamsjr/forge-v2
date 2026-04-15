# User Guide — How to Run Your Agentic System
*Created: 2026-04-15 | Owner: Keith Williams | Audience: You*

This is not an architecture doc. This is how you USE the system day-to-day. Read once. Keep on your desk.

---

## The mental model (60 seconds)

You talk to Claude. Claude runs the **Router**. The Router picks the right **Skill**. The Skill reads from **Policy YAMLs**. The Skill produces an output. Every action is logged to **Audit**.

```
YOU → Claude → route_task → [skill_A → skill_B → skill_C] → output + audit entry
```

If the skill chain can't run (missing docs, ambiguous request, PII detected, policy violation) → it **HALTS** and tells you what's missing. It never guesses.

That halt behavior is the whole point. Every time it halts, you saved yourself from a silent error.

---

## How to start any task

There are only five ways to start a task. Pick one. Say it clearly.

### 1. CIF deal work
| What you say | What runs |
|---|---|
| "Intake [borrower name]" | `intake_cif_checklist` → `generate_cif_deal_data` → `draft_cif_doc_request_email` |
| "Build cash flow for [name]" | `extract_cif_financials` → `calculate_business_cash_flow` → `calculate_global_cash_flow` → `run_cif_stress_tests` |
| "Write memo for [name]" | `write_committee_memo` |
| "Write festival report for [name]" | `write_festival_report` |
| "Write grant summary for [name]" | `write_grant_summary` |

### 2. SBA broker deal work
| What you say | What runs |
|---|---|
| "Screen this deal: [description]" | `extract_sba_deal_parameters` → `match_colony_grid` → `calculate_broker_commission` |
| "Does [borrower] need an LOE?" | `screen_sba_character_loe_needed` |

### 3. Prospecting / lead work
| What you say | What runs |
|---|---|
| "Score today's inbound leads" | `score_inbound_leads` |
| "Mine BizBuySell for [criteria]" | `mine_bizbuysell_listings` |
| "Rank my outreach prospects" | `rank_outreach_prospects` |

### 4. Email / comms
| What you say | What runs |
|---|---|
| "Draft email to [name] about [topic]" | `draft_outbound_email` |
| "Follow up with [name] on [deal]" | `draft_outbound_email` |

### 5. Anything else
If your request doesn't match the table above, the Router will either halt (and ask you to clarify) or propose the closest skill and ask you to confirm. Never proceed on a guess.

---

## The 5 things the system will ALWAYS do

1. **Halt on missing input.** If a skill needs a tax return and there isn't one, it stops. Don't argue with it — upload the doc and restart.
2. **Log every decision.** Every skill run writes to `FORGE_v2/audit/{deal_id}.jsonl`. You can reconstruct any past decision.
3. **Verify numbers against sources.** No number appears in a memo without a source doc it came from.
4. **Draft, never send.** No email goes out without you clicking send. Screenshot every outbound at the moment of send (standing rule).
5. **Read policy from YAML.** No threshold is hardcoded. Change a policy YAML → every skill inherits it on next run.

---

## The 5 things the system will NEVER do

1. **Never guess a missing number.** If depreciation isn't on the return, it halts. It will not estimate.
2. **Never email Colony Bank as a target lender.** Employment conflict is enforced in `broker_rules.yaml`.
3. **Never refer an MCA product.** Hard rule. Excluded lenders listed in policy.
4. **Never use Gmail MCP for Swift Capital.** Swift uses Chrome MCP only. Hardwired.
5. **Never write to a G8WAY xlsx programmatically.** openpyxl corrupts it. You enter data manually; the system builds a reference table for you.

---

## Daily workflow (what to do each morning)

**15-minute opener:**
1. Check Gmail for overnight inbound leads. Forward any to Claude: *"Score today's inbound leads."*
2. Check Swift Capital Chrome inbox. Any CIF doc updates? If yes: *"Resume [deal name] — Nikky sent the [doc]."*
3. Check calendar. Any call prep needed today? *"Pull call prep for [name]."*
4. Scan active broker pipeline. Any deal awaiting next step? *"Status on [deal]."*

**What the system does for you:** router logs every request, you always have a clean audit trail, nothing falls through cracks.

---

## When you finish a deal or decision

Say: *"Close out [deal_name] — committee decided [approve/decline] on [date]."*

What happens:
1. Audit log gets the final decision entry
2. `deal_data.json` updates with committee_decision + date
3. System calendars the PII-deletion reminder (30 days out per your retention policy)
4. Borrower financial docs stay in deal folder until the 30-day mark, then get purged

You don't have to remember the 30-day rule. The system remembers.

---

## When something goes wrong

The Master Guide's rule: don't say "the output was wrong." Say exactly what was wrong, on which file, in which field.

**Template for reporting a bad output to Claude (paste this into chat):**
```
Skill: {skill_name}
Deal: {deal_id}
Field: {which_number_or_section}
Expected: {correct value + source doc with page/line}
Actual: {what the skill produced}
My fix: {what you think is wrong in the skill or policy}
```

Example:
```
Skill: calculate_business_cash_flow
Deal: BEL_2026-04
Field: interest_expense
Expected: $30,500 (from Form 1120-S Line 18, page 2)
Actual: $27,000
My fix: looks like it grabbed Line 17 instead of 18
```

That's 30 seconds. I fix the skill in minutes. No guessing.

---

## The weekly loop (Fridays, 30 minutes)

Per the Master Build Guide, improvement is a cadence, not a project. Every Friday:

1. **Collect** — Open `FORGE_v2/audit/` and look at this week's halt lines. Any pattern? (same skill halting? same missing field?)
2. **Analyze** — Which skill had the most corrections from you? That's your top priority.
3. **Improve** — Fix the #1 failing skill's negative trigger or procedure. Bump version. Add changelog entry.
4. **Test** — Run the updated skill against 2-3 golden dataset deals. If error rate improves, promote to production. If it regresses, revert.

This loop is what separates a system that gets better from one that just sits there. 30 minutes a week = compounding quality.

---

## Version control discipline

Every policy change you make (a new Colony Bank grid revision, a new CIF procedure, a new excluded industry):

1. Edit the YAML in `FORGE_v2/policy/`.
2. Bump the version at the top: `policy_version: 1.0.0 → 1.1.0`.
3. Add a line to the top commenting what changed.
4. Save.

That's it. All skills that reference that YAML will use the new version on their next run. The old version is never deleted — it's archived automatically with audit log retention, so you can always answer "which policy version applied to this deal?"

---

## When you bring on a new lender grid or policy

Don't write it into a skill. Don't rewrite SKILL.md.

1. Create `FORGE_v2/policy/{lender_name}_grids.yaml`
2. Add it to `depends_on` or `policy_refs` in the relevant skills (e.g., `match_colony_grid` becomes `match_lender_grid` with `lender_name` as an input parameter)
3. Test against golden dataset
4. Promote

One YAML = one lender. Infinite scalability without rewriting skills.

---

## The 6 questions you should always be able to answer (Master Guide)

| Question | Where to look |
|---|---|
| What skills are in production? | `FORGE_v2/SKILL_REGISTRY.csv` — filter by `status=production` |
| What version is each skill? | Same CSV, `version` column |
| When was each skill last tested? | `FORGE_v2/golden/` run logs (once regression runner is live) |
| Which MCP servers are connected? | `FORGE_v2/agent.json → mcp_servers` |
| Where are the audit logs? | `FORGE_v2/audit/{deal_id}.jsonl` + `audit/comms.jsonl` + `audit/routing.jsonl` |
| What happens when agent is uncertain? | `agent.json → uncertainty_behavior` — halt, don't guess |

If you can answer all 6 in under a minute, your visibility is fine. If you can't, that's your next weekly-loop item.

---

## Graduating to local agents (future)

Your original requirement: portable, uploadable. This entire folder is that.

When you're ready to run this outside Cowork:
1. Zip `Agentic_Overhaul/` — full system in one file.
2. Upload to your chosen runtime (Claude Agent SDK, OpenAI Assistants, local ollama wrapper, etc.).
3. Point the runtime at `FORGE_v2/agent.json`. That file tells it everything.
4. Hook up MCPs per the `mcp_servers` list.

No rewrite needed. The skill files are portable across any agent runtime that reads markdown SKILL files.

---

## One sentence to remember

**The system is only as smart as its instructions — your job is writing clear instructions, not writing code.**

That is Anthropic's thesis. It is also the reason this works at solo-operator scale: you already know the underwriting. You just need the discipline to write it down once, version it, and let the system apply it consistently.

---

## Quick reference card

| Need to... | Say this |
|---|---|
| Start any deal | "Intake [name]" or "Screen [deal]" |
| Run numbers | "Cash flow for [name]" |
| Write memo | "Write memo for [name]" |
| Draft email | "Draft email to [name] about [topic]" |
| Score leads | "Score today's inbound leads" |
| Report a bug | Paste bad-output template above |
| Add lender | Drop YAML in `policy/`, reference it in skill |
| Change threshold | Edit YAML, bump version |
| Find past decision | `grep` audit/{deal_id}.jsonl |
| Close out deal | "Close out [deal] — committee [decided] on [date]" |
