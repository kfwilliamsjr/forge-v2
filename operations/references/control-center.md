# FORGE — Control Center
*Last updated: 2026-04-02 | Keith Williams*
*This is the master index. Read this first every session.*

---

## MISSION

Replace W2 income (Colony Bank VP-Underwriter) within 12 months.
**Minimum target: $15,000/month business revenue. No cap on upside.**

---

## ACTIVE SPRINT — SBA Lending Network

**Sprint goal:** Close the gap between $1K/month (Swift Capital retainer) and $15K/month.
**Blocker chain:** Rebrand → Domain → Website Live → CDFI Outreach Activation → New Retainer Clients

### Sprint Status
| Item | Status |
|------|--------|
| Rebrand decision (Covenra vs. Fortivara) | 🔴 BLOCKING — not finalized |
| New domain purchase | ⏳ Waiting on rebrand |
| Website update + live | ⏳ Waiting on domain |
| CDFI outreach (10 banks + 5 CDFIs) | ⏳ Waiting on website |
| SAM.gov registration | ✅ SUBMITTED 4/3/2026 — UEI: L6URLN12LLS4. Financial Assistance registration. SBALendingclub Corporation, 474 Martin St, Philadelphia, PA 19128-3422. Status: Submitted → awaiting IRS TIN validation (~2 biz days) → DLA CAGE code (~2-10 biz days) → Active. Must submit notarized Entity Administrator letter within 60 days of activation. Unblocks 8(a) + CDFI Fund TA once Active. |
| MBE prequalification (NMSDC Hub) | ✅ Submitted 4/1/2026. No invite received as of 4/2/2026. Continue checking keith.williams@sbalendingnetwork.com (spam too). |
| Philadelphia Catalyst Fund | ✅ Application submitted. Response ~4 weeks. Contact: catalyst@phila.gov |
| PBLN Incentive Grant | ✅ Submitted 4/1/2026. 5-day lender response window. VestedIn as referring lender |
| Philadelphia OEO Minority Cert | ⏳ Apply this week |
| Intuit QuickBooks Hero Grant | ✅ Essay sent to Akem Durand (akem.durand@cifvi.org) 4/1/2026. Closes May 15, 2026. NOTE: Essay references "12-15 years experience" — correct is 15+ years. Confirm with Akem before he submits. |
| Google Black Founders Fund | 👁️ MONITOR WEEKLY — page live but NO open 2026 US application. Language reads past tense ("awarded more than $40M"). Checked 4/1/2026. Check again 4/8. |
| Comcast RISE | 👁️ MONITOR MONTHLY — Philadelphia NOT in 2025 round. 2025 cities: Boston, Grand Rapids, Nashville, Seattle, South Valley UT. Check again May 1. |
| MBDA Business Center outreach | ✅ Email sent 4/2/2026 to Tish Lewis (tlewis@theenterprisecenter.com). Subject: "PA MBDA Business Center — New Client Inquiry." Awaiting response. Howard Brown bounced — he is no longer the contact. |

---

## CURRENT BLOCKERS (Ordered by Impact)

1. **No additional retainer clients** — Swift Capital ($1K/mo) is the only recurring revenue. Target: 2 new retainer clients at $3K–$8K/month each. Prospect list built 4/1/2026. Outreach ready to activate.
2. ~~**SAM.gov validation pending**~~ — COMPLETE 4/3/2026. UEI: L6URLN12LLS4. 8(a) and CDFI Fund TA now unblocked.
3. **MBE cert in-process** — No NMSDC Hub invite as of 4/2/2026. Keep checking keith.williams@sbalendingnetwork.com (spam too). Tish Lewis (Enterprise Center MBDA) emailed 4/2/2026 — waiting on response re: MBE cert process ($200).
4. **ClearPath auto-email not deployed** — Code written, never pushed. `gh auth login` → `git push origin main`. 10 minutes.

~~**Rebrand**~~ — REMOVED as blocker 4/1/2026. SBA Lending Network is the brand. No rebrand needed before revenue. Revisit at $10K+/month if desired.

---

## BUSINESS STATUS DASHBOARD

| Business | Status | Monthly Rev | Target | Label |
|----------|--------|-------------|--------|-------|
| SBA Lending Network | 🔴 Active Sprint | $1,000 | $10K–$15K | PRIMARY SPRINT |
| Atlas Materials Transport | 🟡 Monitor & Scale | ~$7K avg | $2K–$15K+ | MONITOR AND SCALE |
| Greenwich Hazleton Group | ⚪ Hold | $434/mo (rental) | Decision pending | HOLD |
| TaskSats | 🟢 Deployed | $0 | TBD | ACTIVE BUILD |

---

## NEXT SINGLE ACTION

**Make the Firstrust warm call.**
Brief is in FIRSTRUST_CALL_BRIEF.md. This is your fastest path to a new retainer client. One call, 20 minutes. Everything else is downstream.

---

## SESSION LOG

| Date | Session Focus | Output |
|------|---------------|--------|
| 2026-04-05 (Evening) | **TaskSats deployment session.** Vercel deployment from GitHub completed. Custom domains configured: tasksats.com (307→www), www.tasksats.com, tasksats.ai — all live with SSL. GoDaddy DNS records set (A records + CNAME www). Supabase env vars (VITE_SUPABASE_URL + VITE_SUPABASE_ANON_KEY) added to Vercel Production+Preview. Redeployed with fresh build. Separate Vercel account created (Hobby plan) to isolate TaskSats from Atlas/SBA businesses. Launch Plan fully updated. Backend Gameplan document created. **Status: DEPLOYED TO PRODUCTION. Backend build is next priority.** | TaskSats_Launch_Plan.md rewritten. TaskSats_Backend_Gameplan.md created. FORGE control-center.md updated. |
| 2026-04-05 | CIF Swift Capital underwriting sprint. Email sweep confirmed 0 emails Apr 4-5. **Key discoveries:** (1) JJ Creationz REDIRECTED — Akem told Nikky Apr 1 to use festival loan procedure instead of grant. (2) Amber Alexander confirmed as active underwriting deal — two ShareFile upload events (Mar 29, Mar 31), credit pulled. (3) NEW DEAL: Cultured Delights spotted in ShareFile Mar 16 activity — not yet tracked. (4) Grant checklist updated Apr 3 — business plan removed. **Deliverables:** SWIFT_CAPITAL_SERVICE_PLAN.md updated. CIF_UNDERWRITING_PROCEDURES.md updated. Amber Alexander deal folder created. Festival_Loan_Report_Amber_Alexander_DRAFT.docx built. G8WAY data reference sheet built. ShareFile access blocked (requires login) — Keith needs to pull docs to complete the underwriting. **Next:** Keith pulls docs from rtpark.sharefile.com (St. Thomas Carnival Microloans > Amber Alexander- Booth #33), feeds data to complete the G8WAY and Festival Loan Report. | All MD files updated. Amber Alexander deal folder fully scaffolded. Report DRAFT + G8WAY reference ready. |
| 2026-04-02 (Late Night) | Security infrastructure deep dive: Cisco Meraki Z3-HW identified (employer-issued, DO NOT plug in until IT releases from their org), Tailscale mesh VPN walkthrough (laptop + GrapheneOS phone, 3-device setup), hard drive stack (Samsung T7 Shield x2 for backup, T9 for Mac mini working storage, Synology NAS deferred to Q4 2026), Gmail personal divorce plan documented, Vernon CEO/CFO digital workflow protocol built, business phone (215-290-5738, GrapheneOS) logged, HubSpot MCP connector identified (UUID: 875dee50), Azibo reminder scheduled for Tuesday 4/7 9am. FORGE_TRANSFER_PROMPT.md updated with all above. | FORGE_TRANSFER_PROMPT.md updated. Azibo scheduled task created. |
| 2026-04-02 (Evening) | GHG grant proposal rebuilt as V3 ($50K, general, 8 slides): corrected Jumpstart Wilmington/Catalyst Fund, 433 S Heald first project, Vernon govt agency bio, removed Black Squirrel cover branding. SBA Lending Network deal memo built ($25K ask, Black Squirrel Collective, Thomas Webster credited, real revenue history: $18K/2024/27K/2025/$12.5K shown). LIHTC clarified: not applicable to turn-the-key for-sale properties. FORGE_TRANSFER_PROMPT.md rewritten from scratch. Annual revenue history added to sba-lending-roadmap.md. | GHG_BlackSquirrel_TA_Grant_Proposal.pptx (V3), SBA_LendingNetwork_TA_Grant_Proposal.pptx, sba-lending-roadmap.md, GHG_Property_Tracker.md, FORGE_TRANSFER_PROMPT.md updated. |
| 2026-04-02 (Morning) | Sent emails review, FORGE updates, Nick Nedd logged, Vernon GHG activated, Tish Lewis sent ✅, Black Squirrel TA grant presentation built (11 slides V1/V2), Hemlane replacement researched (save $945/yr), PIDC + Reinvestment Fund Gmail drafts created, call log Excel built | GHG_BlackSquirrel_TA_Grant_Proposal.pptx, SBA_Lending_Call_Log.xlsx, GHG_Property_Tracker.md, CDFI_BANK_PROSPECT_LIST.md all updated. |
| 2026-04-01 | PA DCED grants, PA CDFI outreach, national grants research, Catalyst Fund submission, BIRT filing, CAL license, SAM.gov, PBLN, MBE cert, Intuit form (stopped — third-party only), FORGE system design | All MD files updated. FORGE files built. Transfer prompt + Master prompt created. |
| 2026-03-31 | CIF deal pipeline, email automation, funding strategy, CROSS_DEPARTMENT_ANALYSIS | CLAUDE.md, CDFI_FUNDING_STRATEGY.md, CROSS_DEPARTMENT_ANALYSIS.md updated |
| 2026-03-30 | Swift Capital service plan, TTH loan report, deal tracker | SWIFT_CAPITAL_SERVICE_PLAN.md approved. Deal tracker live. |
| 2026-03-29 | DSCR engine fix, deal screener skill, ClearPath dashboard | Engine validated 1.23x/1.25x. 78 files pushed to GitHub. |

---

## FILES INDEX

| File | Purpose | Location |
|------|---------|---------|
| control-center.md | This file — master index + sprint status | ~/Desktop/FORGE/ |
| budget-tracker.md | Monthly actuals, renewal calendar, capital plan | ~/Desktop/FORGE/ |
| systems-inventory.md | All tools, accounts, sites (no secrets) | ~/Documents/FORGE/ |
| workflow-map.md | How work moves across each business | ~/Documents/FORGE/ |
| automation-backlog.md | All automation ideas ranked | ~/Documents/FORGE/ |
| weekly-audit.md | Weekly ops review log | ~/Documents/FORGE/ |
| security-register.md | Permissions, access, exposure risks | ~/Documents/FORGE/ |
| sba-lending-roadmap.md | Sequenced revenue sprint for SBA | ~/Documents/FORGE/ |
| CLAUDE.md | SBA Lending Network full project memory | ~/Desktop/SBA_Lending_Claude_MD/ |
| CDFI_FUNDING_STRATEGY.md | All grant/loan tracking | ~/Desktop/SBA_Lending_Claude_MD/ |
| CERTIFICATION_STRATEGY.md | MBE, OEO, PA DGS, CDFI cert paths | ~/Desktop/SBA_Lending_Claude_MD/ |
| CROSS_DEPARTMENT_ANALYSIS.md | How SBA + CIF/Swift Capital cross-pollinate | ~/Desktop/SBA_Lending_Claude_MD/ |
| SWIFT_CAPITAL_SERVICE_PLAN.md | CIF client master plan | ~/Desktop/Swift Capital Underwriting/ |
| GHG_Strategy_Playbook.md | GHG real estate strategy | ~/Desktop/Greenwich Hazleton Group_GHG/ |
