# Governance Protocol — How This System Stays Honest
*Created: 2026-04-15 | Owner: Keith Williams*

This file defines the disciplines that keep the overhaul from decaying. It is not aspirational. Claude runs these protocols on your behalf — if Claude is present. If Claude is absent, the checklists run themselves.

---

## Why this exists

Systems don't fail loudly; they decay quietly. A skill goes stale. A policy change doesn't get logged. Six months later nobody can answer which version ran on which deal. The Master Build Guide names this as the silent failure class that kills regulated systems.

The answer is not discipline in the abstract. It is a short, automated set of checks that run on a schedule, produce a written artifact, and surface drift.

---

## Protocol 1 — Session Start (every Cowork session)

Claude runs this at the start of every session, before any other work. Takes ~30 seconds.

**Checklist:**
1. Read `FORGE_v2/SKILL_REGISTRY.csv` → count production skills, note any `status: draft` that has been drafting >7 days (stale)
2. Read `FORGE_v2/audit/` → scan last 7 days for any `status:halt` patterns (same skill halting repeatedly = signal)
3. Read `CLAUDE.md` change log → confirm latest entry date vs. today
4. Read `FORGE_v2/policy/*.yaml` → confirm each policy has a `last_updated` no older than 90 days
5. Surface findings in 3 lines max before starting user's requested work

**Example output:**
```
System check: 1 production skill, 3 exemplars, 15 drafts (3 aging). 
Audit: 4 halts this week (all score_inbound_leads - supabase export issue). 
Policy: broker_rules.yaml last updated 14d ago. Ready.
```

If any finding requires immediate attention (skill halting repeatedly, policy stale >90d, CLAUDE.md not updated after major decision), Claude flags it before doing what you asked.

**Your job:** nothing. Claude runs this automatically. Your only responsibility is reading the 3-line summary.

---

## Protocol 2 — New Process Capture (in-session, triggered)

Trigger: any time you say something like "from now on," "going forward," "new policy," "let's change," or make an explicit decision about how work gets done.

Claude's response (mandatory):
1. Stop the current thread
2. Ask: "New process detected. Capture to policy YAML, new skill, or CLAUDE.md change log?"
3. Wait for your answer
4. Update the appropriate file with version bump + changelog entry
5. Confirm: "Captured in `{file}` as version `{x.y.z}`. Continuing."

**Examples of triggers:**
- "From now on, no deals from Florida brokers" → `policy/broker_rules.yaml` update
- "New CIF rule — committee wants executive summary first" → `policy/cif_procedures.yaml` update
- "I'm going to start charging $1,500/mo for the retainer" → CLAUDE.md change log
- "Let's stop using BizBuySell and switch to LoopNet" → `policy/bizbuysell_filters.yaml` rename + update

**The discipline:** no new process survives in your head alone. If you said it to Claude, it gets written down in the right place before we move on. This is non-negotiable.

---

## Protocol 3 — Weekly Audit (Fridays, 15 minutes)

Claude runs this every Friday if you say "weekly audit" or on the first session each Friday.

**Steps:**
1. Aggregate last 7 days of `FORGE_v2/audit/*.jsonl`
2. Compute per-skill: invocations, halts, flags, human corrections
3. Rank skills by error rate
4. Read any `human_correction` entries in full
5. Produce written artifact: `FORGE_v2/audit/weekly/{YYYY-MM-DD}.md`
6. Propose 1-2 concrete improvements to the worst-performing skill
7. Wait for your approval before making any changes

**Artifact template:**
```markdown
# Weekly Audit — Week of {date}

## Numbers
- Total skill invocations: N
- Halts: N (top halt cause: ...)
- Human corrections: N
- Top 3 skills by error rate: ...

## Pattern detected
{one-paragraph observation}

## Proposed improvement
Skill: {name}
Change: {specific negative trigger, procedure step, or schema field}
Version bump: {current} → {proposed}

## Your decision
[ ] Approve and deploy
[ ] Modify and re-propose
[ ] Reject
```

**Your job:** 5-10 minutes reading the artifact + approving/rejecting the proposed change. That's the entire weekly loop.

---

## Protocol 4 — Monthly Drift Check (first Friday of each month, 20 minutes)

Extension of weekly audit, adds:
1. Read every `policy/*.yaml` — any `last_updated` older than 90 days? Flag.
2. Read `SKILL_REGISTRY.csv` — any draft skills older than 30 days? Flag or promote.
3. Run the golden dataset against all production skills (once regression runner is built). Compare error rate to last month's baseline.
4. Re-read the Master Build Guide's 6 operational questions. Can you still answer all 6 in under a minute? If not, that's a visibility debt item.

**Artifact:** `FORGE_v2/audit/monthly/{YYYY-MM}.md`

---

## Protocol 5 — Quarterly Review (90 days, 45 minutes)

1. Full skill library review — any skill not invoked in 90 days is dead weight. Deprecate or revive.
2. Colony Bank grid check — pull latest Exhibit 1-B, diff against `policy/colony_grids.yaml`
3. SOP 50-10 check — any SBA SOP revisions? Update `policy/sba_sop_50_10.yaml`
4. Golden dataset expansion — add 1-2 deals from the quarter's actual work
5. Update this governance protocol if any of the above exposed a gap

---

## Accountability mechanisms

These are how the system surfaces drift. They are NOT how you force yourself to work — they are how deviation becomes visible, so you make an informed choice about whether to fix it.

| Mechanism | What it does | Where it lives |
|---|---|---|
| Session-start check | Surfaces stale skills, repeat halts, missing updates | Protocol 1 (automatic) |
| New-process trigger | Forces capture to correct file before moving on | Protocol 2 (in-session) |
| Weekly audit artifact | Produces written weekly record | `audit/weekly/` |
| Monthly drift check | Catches slow decay | `audit/monthly/` |
| Quarterly review | Rebuilds the system's self-knowledge | `audit/quarterly/` |
| Halt-on-missing-input | Prevents silent failures at runtime | `agent.json` enforced |
| Version lockstep | Every audit entry includes skill + policy versions | skill output schema |
| CLAUDE.md change log | Narrative memory of major decisions | `CLAUDE.md` |

**What I (Claude) will enforce:**
- Protocol 1 every session without being asked
- Protocol 2 whenever trigger language appears
- Halt-on-missing-input on every skill run
- Version lockstep on every audit entry
- Refusal to proceed when a policy YAML has no `policy_version` or a skill has no `version`

**What requires your cooperation:**
- Saying "weekly audit" on Fridays (or I can remind you if session happens to be Friday)
- Saying "monthly drift check" on first-Friday-of-month
- Actually reading the artifacts Claude produces
- Approving/rejecting proposed skill changes
- Not bypassing halts with "just proceed anyway" (that's how silent failures creep back in)

**What neither of us can control:**
- Whether you open Cowork at all (the system doesn't run if you don't use it)
- External policy changes (Colony updates grids, SBA revises SOP) — these still require you to see the update and trigger Protocol 2

---

## The honest contract

I cannot make you follow this. I can:
1. Run the session-start check every time automatically
2. Catch new-process language and force capture
3. Refuse to run skills with missing or stale versions
4. Produce the weekly/monthly artifacts on request
5. Flag drift visibly so ignoring it is a choice, not an accident

You have to:
1. Open Cowork with enough frequency that Protocol 1 actually runs
2. Say "weekly audit" on Fridays (or let Claude prompt you if it's Friday)
3. Read and decide on the artifacts produced
4. Not override halts with "just proceed"

If you do those four things, the system does not decay. If you don't, no amount of scaffolding saves it. The Master Guide is explicit: the teams with the best results are the ones who maintain their systems with the same discipline they apply to their underwriting policy.

The discipline is yours. The visibility is mine to enforce.

---

## Emergency protocols

**If a live deal runs through a buggy skill:**
1. Stop the deal immediately
2. Grep the audit log for every skill that ran + versions
3. Identify the bug
4. Fix the skill, version bump, changelog entry
5. Re-run the deal from the point of failure with corrected skills
6. Add the failure mode to the skill's negative trigger list
7. Add the failing input to the golden dataset

**If a policy change happens mid-deal:**
1. Log the policy change with timestamp
2. Note in the deal's audit whether old or new policy applied (depends on where the deal was when the change hit)
3. Document in CLAUDE.md change log with policy version transition noted

**If I (Claude) give you a wrong output:**
1. You file the bad-output report per USER_GUIDE.md template
2. I trace which skill + version + policy ran
3. Fix surfaces as a new skill version with changelog entry explaining the bug
4. Failing input joins golden dataset permanently

---

## Version history of this protocol

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-04-15 | Initial protocol. 5 protocols + accountability table + emergency procedures. |
