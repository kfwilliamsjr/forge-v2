# FORGE — Automation Backlog
*Last updated: 2026-04-01 | Keith Williams*
*All automation ideas ranked by revenue impact. Labels applied per FORGE protocol.*

---

## HOW TO READ THIS FILE

Labels:
- `APPROVED BUILD` — build now
- `HOLD` — valid, not yet time
- `DEFER` — build after primary targets
- `DISTRACTION` — kill it
- `MONITOR ONLY` — stay aware

Decision hierarchy: Speed to revenue → Reduce touch points → Simplicity → Security → Maintainability → Scalability

---

## TIER 1 — APPROVED BUILD (Build Now)

### 1. ClearPath Auto-Email Deployment
**Label:** `APPROVED BUILD`
**What:** Push the existing auto-email follow-up code to Vercel. It's written. Just needs `gh auth login` → `git push origin main`.
**Revenue line:** Faster borrower follow-up = faster document collection = faster deal pipeline.
**Time:** 10 minutes.
**How:** Open Terminal → `gh auth login` (browser flow) → `git push origin main`

### 2. CDFI Outreach Email Sequence
**Label:** `APPROVED BUILD` (pending rebrand completion)
**What:** Personalized outreach emails to 15 banks + 5 CDFIs using LSP positioning. Drafted by FORGE, approved and sent by Keith.
**Revenue line:** Each retainer client = $3K–$8K/month recurring.
**Pitch:** "Minority-owned SBA underwriting and deal sourcing firm. We pre-screen SBA/CRE deals ($750K–$5M) and support outsourced underwriting for lenders managing volume or backlog."
**Dependencies:** Rebrand finalized → new domain live → updated website.

### 3. Weekly CIF Pipeline Report (Already Live — Verify)
**Label:** `APPROVED BUILD` (verify it's still running)
**What:** Scheduled task runs Mondays 9AM — drafts pipeline update to Akem + Nikky.
**Revenue line:** Keeps client relationship tight. Demonstrates value.
**Action:** Verify scheduled task is still active in Cowork.

---

## TIER 2 — HOLD (Valid — Not Yet)

### 4. SBA Financial Analyst Skill
**Label:** `HOLD`
**What:** Upload tax returns → Claude extracts all line items → calculates Borrower DSCR, Global DSCR, liquidity, Net Risk to Bank. Saves 2–4 hours per deal.
**Revenue line:** Direct — faster deal processing enables more deals per month.
**Dependencies:** Deal Screener v1 validated on real deal first. Run Advanced Integrated Pain through screener.
**Builds on:** Skills_and_Agents_Master_Plan.md #2

### 5. Credit Memo Writer Skill
**Label:** `HOLD`
**What:** Drafts 22-page Colony Bank format credit memos from structured deal data.
**Revenue line:** Reduces report writing from 4–6 hours to 30-minute review.
**Dependencies:** Financial Analyst skill (#4) working first.
**Builds on:** Skills_and_Agents_Master_Plan.md #3

### 6. LOE (Letter of Explanation) Writer Skill
**Label:** `HOLD`
**What:** Drafts character explanation letters for borrowers with derogatory credit or criminal filings, per SBA SOP 50-10 character determination requirements.
**Revenue line:** Removes deal-killing bottleneck on borderline approvals.
**Dependencies:** Credit Memo Writer (#5) in place.

### 7. Atlas Shipper Outreach Automation
**Label:** `HOLD`
**What:** Automated prospecting emails to new shippers. Template built, personalized per target, queued for Keith/Nick approval.
**Revenue line:** More shippers = more loads = Atlas revenue growth toward $15K+/month.
**Dependencies:** Nick operational as day-to-day operator. Core SBA revenue hitting $10K+/month first.

### 8. CIF Deal Screener Variant
**Label:** `HOLD`
**What:** Fork the SBA Deal Screener skill for CIF criteria — readiness score routing (12-14 → loan, 8-11 → grant, ≤7 → TA), USVI-specific checks, Vision 2040 alignment.
**Revenue line:** Faster CIF deal routing = more deals processed per month on same retainer.
**Dependencies:** SBA Deal Screener v1 validated on a real deal first.

### 9. ClearPath Pipeline Unification
**Label:** `HOLD`
**What:** Add CIF deal categories to ClearPath (CIF Loan, CIF Grant, CIF Festival Loan). One dashboard for all revenue streams.
**Revenue line:** Better pipeline visibility = better prioritization = faster to revenue.
**Dependencies:** ClearPath deployed to production (not just localhost).

---

## TIER 3 — DEFER (Build After Targets Hit)

### 10. Daily BizBuySell Scanner
**Label:** `DEFER`
**What:** Scrapes new business listings daily → runs through Deal Screener → generates digest of SBA-eligible deals.
**Revenue line:** Lead gen engine for brokered deals.
**Dependencies:** Deal Screener validated + Broker Outreach Writer (#11) working + Firecrawl MCP installed.

### 11. Broker Outreach Writer Skill
**Label:** `DEFER`
**What:** Given a BizBuySell listing, generates personalized outreach email to listing broker with SBA pre-screen built in.
**Revenue line:** Value-first outreach = higher response rates = more brokered deals.
**Dependencies:** Deal Screener validated + lead flow established.

### 12. Deal Intake Agent (Full Pipeline)
**Label:** `DEFER`
**What:** Lead submits → Deal Screener → document request email → Financial Analyst → Credit Memo → notify Keith. Reduces 8–12 hours per deal to 1–2 hours of Keith's review time.
**Revenue line:** Enables 10x deal volume without proportional time increase.
**Dependencies:** All Phase 1-2 skills validated on real deals.

### 13. Monthly Revenue Tracker
**Label:** `DEFER`
**What:** Monthly automated summary — revenue vs. $15K target, pipeline projection, off-track flag.
**Revenue line:** Accountability tool — ensures early warning if trajectory is off.
**Dependencies:** Real revenue flowing from multiple sources.

### 14. SEO Content Writer Skill
**Label:** `DEFER`
**What:** Generates SBA lending content targeting high-intent search keywords. "SBA loan for [industry]" articles, qualification guides, etc.
**Revenue line:** Organic traffic = inbound leads = free deal flow.
**Dependencies:** Website finalized post-rebrand + basic brokerage pipeline working.

---

## DISTRACTION — KILLED

### TaskSats Build
**Label:** `DISTRACTION`
**Why:** Bitcoin AI labor marketplace. Zero revenue, zero clients, zero validation. SBA and Atlas are not at target yet. Do not touch until $15K/month is consistent.

### OpenClaw / Atlas Telegram Bot
**Label:** `DISTRACTION` — RETIRED
**Why:** Replaced by Claude Code + Cowork. More capable, simpler, already working. Do not reinstall.

### AI Team Roles (dedicated CEO, accountant, legal, marketing agents)
**Label:** `DISTRACTION`
**Why:** Premature. Build skills that let one Claude switch modes. Dedicated agents when volume demands it.

### 5+ Certifications Simultaneously
**Label:** `DISTRACTION`
**Why:** Certifications open doors, they don't close revenue. MBE + Philadelphia OEO is enough for now. Don't stack PA DGS + SBA 8(a) + CDFI cert all at once.

---

## MONITOR ONLY

### Google for Startups Black Founders Fund
**Label:** `MONITOR ONLY`
**What:** Up to $100K equity-free. US-based Black founder, post-revenue, <$5M raised. Check weekly at startup.google.com/programs/black-founders-fund/united-states/
**Action:** Check weekly. Apply same day a 2026 US round opens.

### Comcast RISE
**Label:** `MONITOR ONLY`
**What:** $10K grant to BIPOC-owned Philadelphia businesses. Philadelphia not in 2025 round.
**Action:** Check comcastrise.com monthly. Apply same day Philadelphia opens.

### NAACP Powershift Grant
**Label:** `MONITOR ONLY`
**What:** $25K grant for Black entrepreneurs. Opens ~October 2026.
**Action:** Calendar reminder September 2026 to prepare.

### SBA Community Advantage SBLC
**Label:** `MONITOR ONLY`
**What:** Become a direct SBA originator (up to $350K loans). Requires CDFI certification first. Long-term revenue transformation.
**Action:** Monitor SBA announcements. Pursue after CDFI cert path is underway.

---

## COMPLETED AUTOMATIONS

| Automation | Status | Notes |
|------------|--------|-------|
| CIF Daily Email Sweep | ✅ Live | Weekdays 8AM, keith@swiftcapitaloptions.com |
| CIF Monday Pipeline Report | ✅ Live | Mondays 9AM, drafts update for Akem + Nikky |
| CIF Monday Inbox Cleanup | ✅ Live | Mondays 9AM, triages inbox |
| ClearPath DSCR Engine | ✅ Validated | 1.23x/1.25x match vs Colony Bank credit memo |
| SBA Deal Screener Skill | ✅ v1 Live | Validated on Advanced Integrated Pain & Spine |
| PDF Generation Script | ✅ Live | generate_loan_report_pdf.py reads DOCX colors correctly |
