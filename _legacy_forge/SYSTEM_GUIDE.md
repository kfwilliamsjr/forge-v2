# SBA Lending Network — System Guide & Training Manual
*Keep this on your desktop. Updated: 2026-04-10*
*This document teaches you how your agent system works and how to interact with it effectively.*

---

## How Your System Works (The 30-Second Version)

You have two layers working together:

**Layer 1 — Cowork Skills (you trigger, free):** These are specialized commands you run inside Cowork sessions. You say "intake Amber Alexander" and the Deal Intake skill runs. No extra cost beyond your subscription.

**Layer 2 — Agent SDK Agents (autonomous, ~$50-90/month):** These run on schedules without you. The Prospecting Agent finds borrower leads at 7 AM. The Outreach Agent contacts CDFIs on Mondays. You review what they found.

Both layers read from the same structured data files (JSON), which keeps everything in sync.

---

## Where Everything Lives

Here's the physical layout on your Mac desktop:

```
~/Desktop/FORGE/                              ← Your operating system (command center)
├── CONTEXT_BRIEF.md                          ← Slim context for agents (50 lines, cheap)
├── ACTIVE_PIPELINE.json                      ← Current deals as structured data
├── SYSTEM_GUIDE.md                           ← YOU ARE HERE
├── control-center.md                         ← Sprint status dashboard
├── FORGE_MASTER_PROMPT.md                    ← AI Chief of Staff instructions
├── templates/
│   └── deal_data_schema.json                 ← Blank template for new deals
├── skills/                                   ← YOUR CUSTOM SKILLS LIVE HERE
│   └── cif-deal-intake/
│       └── SKILL.md                          ← Deal Intake skill (active)
└── underwriteos/                             ← Python underwriting engine

~/Desktop/Swift Capital Underwriting/         ← Client work (CIF deals)
├── Deals_Swift Capital/
│   └── [Deal Name]/
│       ├── deal_data.json                    ← Structured deal data
│       ├── Report/                           ← Final deliverables (DOCX + PDF)
│       └── Notes/                            ← Deal notes, email drafts

~/Desktop/SBA_Lending_Claude_MD/              ← Business strategy & master memory
├── CLAUDE.md                                 ← Full project memory (source of truth)
├── CERTIFICATION_STRATEGY.md
├── CDFI_FUNDING_STRATEGY.md
└── Business_Documents/
```

### Where Skills Live (Important)

Your custom skills are in **`~/Desktop/FORGE/skills/`**. Each skill has its own folder with a `SKILL.md` file inside.

These are NOT built into Cowork's system menu — they're custom to your business. The way Claude knows about them: every Cowork session reads your `CLAUDE.md` file on startup, and CLAUDE.md has a "Custom Skills" section that maps your trigger phrases to skill files.

**Think of it like this:** CLAUDE.md is the receptionist. You walk in and say "intake Amber Alexander." The receptionist (CLAUDE.md) says "ah, that's a Deal Intake request" and pulls the right instruction manual (SKILL.md) off the shelf for Claude to follow.

---

## How to Talk to the System

This is the most important section. Your system responds to natural language — you don't need to type commands exactly. But certain phrases trigger specific workflows.

### Skill Triggers (Say These in Cowork)

| You Say | What Happens | Skill Used |
|---------|-------------|------------|
| **"What's next?"** | Reads pipeline, sorts by priority, tells you which deal needs attention and what's missing | CIF Deal Intake (proactive mode) |
| **"Intake Amber Alexander, Festival Loan"** | Creates deal folder, runs checklist, marks docs as HAVE/MISSING/BLOCKER, creates deal_data.json, drafts doc request email to Nikky | CIF Deal Intake |
| **"New deal: Zefo's, VI Leap Grant"** | Same as above but for a grant application | CIF Deal Intake |
| **"What docs am I missing for JJ Creationz?"** | Scans deal folder, compares against checklist, gives gap report | CIF Deal Intake |
| **"Build cash flow for Amber Alexander"** | Runs 3-layer cash flow + 4 stress tests, outputs workbook | CIF Cash Flow *(coming soon)* |
| **"Write memo for JJ Creationz"** | Generates credit memo DOCX + PDF from structured data | CIF Memo Writer *(coming soon)* |
| **"Pipeline report"** | Reads ACTIVE_PIPELINE.json, formats update for Akem/Nikky | Built-in |
| **"What's my pipeline?"** | Quick status summary of all active deals | Built-in |
| **"Screen this deal: [details]"** | Runs SBA Deal Screener against Colony Bank grids | SBA Deal Screener |

### How the System Tells You What to Do (Pipeline-Driven Workflow)

You don't have to remember which deal needs what. The system knows.

**Daily Email Sweep** (scheduled task, runs automatically):
- Checks keith@swiftcapitaloptions.com for new messages
- Matches emails from Nikky, Akem, or ShareFile to active pipeline deals
- Detects when new documents arrive
- Updates deal_data.json checklists automatically
- Presents: "Amber's credit report just came in. 3 items still missing. Want me to draft the request?"

**Pipeline Reporter** (Monday 9 AM or on-demand):
- Reads ACTIVE_PIPELINE.json
- For each deal, checks what stage it's at and what's blocking progress
- Surfaces the highest-priority next action
- Formats report for Akem + Nikky

**The flow:** Email Sweep catches incoming docs → Pipeline Reporter surfaces what's next → You say "intake [name]" or "build cash flow" → Skill executes → Deal moves forward.

You go from **"let me check what Amber needs"** to **"the system says Amber needs 3 more docs and here's the email draft."**

### How to Give Good Instructions

Claude works best when you give it:

1. **A borrower name** — "Amber Alexander" not "that lady with the festival booth"
2. **A deal type** — "Festival Loan" or "VI Leap Grant" or "Regular Loan"
3. **What you want done** — "intake", "build cash flow", "write memo", "check docs"

**Good examples:**
- "Intake Amber Alexander, Festival Loan"
- "Build cash flow for JJ Creationz"
- "What docs am I missing for Alvin's Hot Sauce?"
- "Draft a pipeline report for Monday"
- "Screen this deal: restaurant, $180K SBA 7(a), owner credit 720, 3 years in business"

**Less effective:**
- "Do the thing for Amber" (which thing? what deal type?)
- "Process the new applications" (which ones? what stage?)
- "Help me with CIF stuff" (too vague — pick a specific deal and action)

### Starting a New Cowork Session

When you open a fresh Cowork session:
1. **Mount your folders** — Make sure FORGE, Swift Capital Underwriting, and SBA_Lending_Claude_MD are all connected
2. **Claude reads CLAUDE.md automatically** — this loads your entire project context
3. **Start giving commands** — "intake [name]", "pipeline report", etc.

If Claude seems to not know about your skills or pipeline, say: **"Read FORGE/CONTEXT_BRIEF.md and FORGE/skills/cif-deal-intake/SKILL.md"** — this forces it to load the context.

---

## Key Concepts (Plain English)

### JSON vs MD Files
- **MD files** = your journals. Full narrative, change logs, context. You read these.
- **JSON files** = your forms. Structured data with labeled fields. Agents read these.
- You keep both. Skills update both automatically. You never edit JSON by hand.
- **Why both?** MD files are easy for you to read and edit in any text editor. JSON files are easy for agents to parse without burning tokens reading through paragraphs of text. The deal_data.json for a deal might be 100 lines of structured data that an agent reads in 200 tokens. The equivalent narrative in an MD file would burn 2,000+ tokens.

### Tokens (Your Currency)
- Units Claude reads/writes. ~1 token = 0.75 words. A page of text ≈ 400 tokens.
- Loading CLAUDE.md = ~8,000 tokens (expensive — like running the meter with the car parked).
- Loading CONTEXT_BRIEF.md = ~800 tokens (cheap — 90% savings).
- Lower token usage = more deals per session, fewer rate limits, lower API costs.
- **Your old approach:** 30,000-45,000 tokens per session. **New approach:** ~5,000-8,000 tokens per session.

### Skills vs Agents
- **Skill** = a tool you activate by saying a command. Like a power tool — you pick it up, use it, put it down. Runs inside your Cowork session. Free (covered by subscription).
- **Agent** = an autonomous worker that runs on a schedule. Like an employee — they do their job while you sleep. Runs via Agent SDK on Anthropic's API. Costs money (tokens).

### Model Tiering (Save 60-70% on API Costs)

You have three Claude models. Use the right one for the job:

| Model | Use For | Cost (per 1M tokens) | When |
|-------|---------|---------------------|------|
| **Opus 4.6** | Strategy, complex judgment, credit memo narratives, underwriting decisions | $15 input / $75 output | Cowork sessions, memo narrative generation |
| **Sonnet 4.6** | Doc extraction, cash flow math, email drafts, pipeline reports, templates | $3 input / $15 output | Most agent tasks, structured work |
| **Haiku 4.5** | Lead classification, yes/no screening, JSON parsing, status checks | $0.80 input / $4 output | Prospecting agent, lead qualification |

**Rule of thumb:** If the task needs *judgment*, use Opus. If it needs *execution*, use Sonnet. If it needs a *quick answer*, use Haiku.

**Your Cowork sessions** default to Opus — that's correct for interactive strategy work. **Agent SDK agents** should be set to Sonnet or Haiku unless they're writing narratives.

### UnderwriteOS
- Your Python underwriting engine in ~/Desktop/FORGE/underwriteos/
- Extracts data from tax returns, credit reports, financial statements
- Calculates DSCR, stress tests, risk flags — deterministic math, no AI guessing
- Agents call it under the hood so you don't have to build spreadsheets manually

### DSCR (Debt Service Coverage Ratio)
- The core number in every underwriting deal. Measures: can the borrower afford the loan payments?
- **Formula:** Net Income Available / Annual Debt Service
- **CIF minimum:** 1.25x (meaning the borrower earns 25% more than their total debt payments)
- **Your system calculates 5 versions:** Base DSCR, +personal debt stress, +living expense stress, combined stress, severe stress

---

## Daily Workflow

### Morning (7-8 AM)
1. **Check agent outputs** — Prospecting Agent ran at 7 AM. Review leads it found.
2. **Approve/reject outreach emails** — Agent drafts, you decide. Never auto-sends.
3. **CIF email sweep** — Scheduled task checks keith@swiftcapitaloptions.com for new items.

### During Work Sessions
4. **Process CIF deals using skills:**
   - "Intake [borrower name]" → Deal Intake skill runs checklist, creates deal_data.json
   - "Build cash flow for [borrower]" → Cash Flow Builder runs numbers
   - "Write memo for [borrower]" → Memo Writer generates DOCX + PDF
   - "Pipeline report" → Formats weekly update for Akem/Nikky

5. **Review agent-generated leads:**
   - Hot leads → Call or email personally
   - Warm leads → Agent sends nurture email (you approve first)
   - Cold leads → Auto-decline with referral

### Monday Morning
6. **Pipeline report** auto-generates at 9 AM. Review, approve, send to Akem + Nikky.
7. **CDFI/Bank Outreach Agent** ran at 6 AM. Review new prospect research and outreach drafts.

---

## How Agents Save You Money

### Per-Deal Comparison
| Metric | Before (Manual) | After (Skills + Agents) |
|--------|-----------------|------------------------|
| Your time per deal | 60-90 min | 10-15 min (review + approve) |
| Tokens per deal | 3,000-5,500 | ~600 |
| Sessions before rate limit | 2-3 deals | 8-10 deals |
| Monthly deal capacity | 8-12 | 30-40 |

### Monthly Impact
| Metric | Before | After |
|--------|--------|-------|
| Monthly API cost (agents) | $0 | ~$50-90 |
| Monthly revenue capacity | ~$1,000 (capped by time) | $15,000+ (capped by pipeline) |
| Token spend per session | 30,000-45,000 | 5,000-8,000 |

---

## Agent Status Dashboard

| Agent/Skill | Type | Schedule | Status | Monthly Cost |
|-------------|------|----------|--------|-------------|
| **CIF Deal Intake** | Cowork Skill | On-demand | ✅ BUILT | $0 |
| **CIF Cash Flow Builder** | Cowork Skill | On-demand | ✅ BUILT | $0 |
| **CIF Credit Memo Writer** | Cowork Skill | On-demand | ✅ BUILT | $0 |
| Pipeline Reporter | Cowork Skill | Mon 9 AM + on-demand | EXISTS (optimize) | $0 |
| Borrower Prospecting Agent | Agent SDK | Daily 7 AM | WEEK 2 | ~$30-50/mo |
| CDFI/Bank Outreach Agent | Agent SDK | Weekly Mon 6 AM | WEEK 2 | ~$15-25/mo |
| Lead Qualification Agent | Agent SDK | Event-driven | WEEK 2 | ~$5-15/mo |

---

## Troubleshooting

**"Claude doesn't know about my skills"**
→ Say: "Read FORGE/skills/cif-deal-intake/SKILL.md" to force-load it. Or: "Read CLAUDE.md" to reload full context.

**"Claude is slow / hitting rate limits"**
→ Check if the session loaded CLAUDE.md (8K+ tokens). If so, it's context-heavy. For routine deal work, tell Claude to use CONTEXT_BRIEF.md instead.

**"Deal data isn't synced between MD and JSON"**
→ Run the Deal Intake skill on the deal. It reconciles both files.

**"Agent didn't run"**
→ Check Claude Console > Managed Agents > Sessions. Look for errors. Most common: API key expired or rate limit hit.

**"UnderwriteOS extractor failed"**
→ Check if the PDF is scanned (image) vs. digital text. Scanned PDFs need OCR.

**"I want to add a new skill"**
→ Say "I want to create a skill for [X]" in a Cowork session. The skill-creator tool will guide you through building it.

---

## Key Contacts

| Name | Role | Email | Use |
|------|------|-------|-----|
| Akem Durand | CIF Loan Officer | akem.durand@cifvi.org | Deal approvals, pipeline reports |
| Nikky Cole | CIF Loan Assistant | nikky.cole@cifvi.org | Document requests, ShareFile |
| Varsovia Fernandez | PA CDFI Network | vfernandez@pacdfinetwork.org | CDFI relationship, grants |
| MBDA Business Center | The Enterprise Center | — | Free business services, cert help |

---

## Weekend Sprint Checklist (April 12-13)

- [x] Review CONTEXT_BRIEF.md — captures everything agents need
- [x] Review ACTIVE_PIPELINE.json — pipeline data accurate
- [x] Review deal_data_schema.json — covers all CIF deal fields
- [x] Build CIF Deal Intake skill
- [x] Build CIF Cash Flow Builder skill
- [x] Build CIF Credit Memo Writer skill
- [ ] Build/update sbalendingnetwork.com landing page + intake form
- [ ] Set up Google Ads account + apply $500 credit
- [ ] Create Campaign 1 (SBA Borrowers)
- [ ] Test UnderwriteOS tax_return_1040.py on a real CIF doc
- [ ] Update FORGE control-center.md with new sprint status

---

## Quick Reference Card

**To onboard a deal:** "Intake [Name], [Deal Type]"
**To check missing docs:** "What docs am I missing for [Name]?"
**To run cash flow:** "Build cash flow for [Name]"
**To write a memo:** "Write memo for [Name]"
**To check pipeline:** "What's my pipeline?"
**To generate Monday report:** "Pipeline report"
**To screen an SBA deal:** "Screen this deal: [details]"
**To force-load context:** "Read FORGE/CONTEXT_BRIEF.md"
**To force-load a skill:** "Read FORGE/skills/[skill-name]/SKILL.md"

---

---

## Data Retention Policy (Borrower PII)

You handle sensitive financial data — tax returns, credit reports, bank statements, PFS. Here's the rule:

**Delete borrower financial documents 30 days after committee decision.**

The system tracks this automatically. When a deal reaches committee_decision status, it starts a 30-day countdown. The Pipeline Reporter will flag deals due for purge: "JJ Creationz — committee decision 4/15, purge due 5/15."

**What gets deleted:** Tax returns, credit reports, bank statements, PFS, anything with SSN/EIN/account numbers.
**What stays:** deal_data.json, credit memo, cash flow workbook, deal notes, G8WAY reference. These are your permanent record with no raw PII.

**ShareFile workflow:** You download files from CIF's ShareFile when the system tells you it needs them. After committee decision + 30 days, your local copies get deleted. ShareFile originals stay with CIF — their retention, their responsibility.

---

## How Documents Flow Through the System

```
ShareFile (CIF's system)
    ↓ Keith downloads when system requests
Deal Folder (your desktop)
    ↓ Skills read and extract data
deal_data.json (structured, no raw PII)
    ↓ Cash Flow Builder runs numbers
Cash Flow Results → deal_data.json
    ↓ Memo Writer generates deliverable
Credit Memo (DOCX + PDF) → delivered to Akem
    ↓ Committee decides
30-day countdown → raw financial docs deleted
    ↓
Permanent record: deal_data.json + memo + workbook + notes
```

You never have to remember what docs to download or when to delete them. The system tells you both.

---

*This guide will be updated as skills and agents come online. Check the Agent Status Dashboard above for current state.*
