# FORGE — Systems Inventory
*Last updated: 2026-04-02 | Keith Williams*
*Descriptions only. No credentials, tokens, or passwords in this file.*

---

## HOSTING & INFRASTRUCTURE

| System | Purpose | Provider | Status |
|--------|---------|---------|--------|
| Mac Mini | Local command center, ground truth for all files | Personal hardware | Active |
| Hostinger VPS | Hosts sbalendingnetwork.com and atlastransport site | Hostinger | Active |
| GitHub (private repo) | Version control — sba-lending-network repo | github.com/Atlasmaterialstransport/sba-lending-network | Active |
| Supabase | Database — two active projects (SBA + Atlas) | supabase.com | Active |
| TP-Link BE11000 Tri-Band Wi-Fi 7 Router | Replaces Verizon router. Split networks: personal + Mac Mini business. | TP-Link | Purchased 4/3/2026 — not yet configured |
| SanDisk Extreme Pro SSD 1TB (SDSSDE81-1T) — **FORGE-DRIVE** | Local working storage, secure file transfer, encrypted backup | SanDisk (Best Buy) | ✅ Purchased 4/3/2026. Connected. Renamed to FORGE-DRIVE. |
| YubiKey 5C NFC x2 | Hardware auth for Tailscale, 1Password, Google, GitHub | Yubico (Best Buy) | ✅ Both registered on 1Password 4/4/2026. Key #1 = Primary. Key #2 = Backup. Tailscale registration pending. |
| Tailscale (Free tier) | Encrypted mesh VPN — Mac Mini + Laptop + GrapheneOS phone | tailscale.com | Planned — install after router setup |
| 1Password | Credential vault — all accounts, API keys, secrets | 1password.com ($51.71/yr) | ✅ Active 4/3/2026. YubiKey #1 + #2 registered as 2FA. Installed on Mac Mini + personal laptop. |
| Google Workspace (Business Starter) | Business email: keith.williams@sbalendingnetwork.com | Google ($7/mo) | ✅ Signed up 4/4/2026. DNS verification + MX records pending at Hostinger. |

---

## DOMAINS & WEBSITES

| Site | Domain | Host | Status |
|------|--------|------|--------|
| SBA Lending Network | sbalendingnetwork.com | Hostinger VPS | Live — rebrand pending |
| Atlas Materials Transport | atlasmaterialstransport.com (verify) | Hostinger VPS | Live — operational |
| TaskSats | tasksats.com (GoDaddy domain purchased 3/15/2026) | TBD | Parked — concept stage |

---

## TOOLS — ACTIVE

| Tool | What It Does | Account | Used For |
|------|-------------|---------|---------|
| Cowork (Claude Desktop) | AI Chief of Staff — this session | Anthropic | Strategy, analysis, document creation, browser automation |
| Claude Code (Terminal) | Coding, deployment, git | Anthropic | Building ClearPath, G8WAY, auto-email |
| ClearPath Tool | SBA deal pipeline + underwriting dashboard | localhost:3000 | Deal screening, DSCR tracking, pipeline management |
| G8WAY Engine | SBA underwriting calculation engine | localhost:3001 | Financial analysis, risk assessment, report generation |
| QuickBooks | Business accounting for SBA Lending Network | Intuit — existing customer | Bookkeeping, P&L, tax prep |
| Cal.com | Scheduling | cal.com | Client/prospect meetings |
| Gmail | Personal email | keithfwilliamsjr@gmail.com | Personal use, grant correspondence |
| Google Workspace | Business email (Swift Capital work) | keith@swiftcapitaloptions.com | All CIF/Swift Capital client communications |
| ~~Titan / Business Email~~ | ~~SBA Lending Network business email~~ | keith.williams@sbalendingnetwork.com | REPLACING with Google Workspace (signed up 4/4/2026). Cancel Titan after MX records point to Google. |
| ShareFile | Document collection from CIF clients | swift.sharefile.com | Borrower doc intake for CIF deals |
| Alignable | Small business network | Keith's account | CDFI networking, visibility |
| CIF Deal Tracker | XLSX deal log | ~/Desktop/Swift Capital Underwriting/CIF_Deal_Tracker.xlsx | Active CIF pipeline tracking |
| Obsidian | Local notes + FORGE vault | ~/Documents/FORGE/ | FORGE OS — this system |

---

## TOOLS — TO INSTALL (Prioritized)

| Tool | Phase | Why | Install Method |
|------|-------|-----|---------------|
| Superpowers (Claude Code skill) | Phase 1 | Battle-tested coding skills for TDD, debugging | `claude install-skill github.com/obra/superpowers` |
| Context7 (MCP) | Phase 1 | Up-to-date library docs prevents hallucinated APIs | Claude Code MCP server |
| Task Master AI (MCP) | Phase 1 | Structured task management from roadmap | Claude Code MCP server |
| Tavily (MCP) | Phase 2 | AI-native search for lead enrichment, due diligence | Claude Code MCP server |
| fastmcp | Phase 2 | Build custom MCP to connect Cowork to G8WAY API | npm |
| n8n | Phase 3 | Visual workflow automation for deal intake pipeline | Self-hosted or cloud |
| Firecrawl | Phase 3 | Web scraping for BizBuySell scanner | MCP server |

---

## ACCOUNTS — REGISTRATIONS & CERTIFICATIONS

| Account / Registration | Status | Where | Notes |
|------------------------|--------|-------|-------|
| SAM.gov Entity Registration | ✅ COMPLETE | sam.gov | UEI: L6URLN12LLS4. Financial Assistance registration. SBALendingclub Corporation, 474 Martin St, Philadelphia, PA 19128-3422. Ref# INC-GSAFSD20864717. Expires ~4/3/2027. |
| Philadelphia Tax Center (BIRT) | ✅ Active | tax-services.phila.gov | Username: SBAlendingnetwork. All years filed (2022-2025). |
| Commercial Activity License (CAL) | ✅ Active | eclipse.phila.gov | License #1003618. No expiration. |
| Tax Clearance Certificate | ✅ Issued | Philadelphia | Conf# L0009251566. Valid through May 1, 2026. |
| NMSDC MBE Prequalification | ✅ Submitted | nmsdc.org | Awaiting Hub invite email at keith.williams@sbalendingnetwork.com. |
| Philadelphia OEO Minority Cert | ⏳ Not started | phila.gov/OEO | Apply this week. |
| PA DGS MBE/MWBE Cert | ⏳ Month 1-2 | pa.gov/DGS | After Philadelphia OEO cert. |
| SBA 8(a) Certification | ⏳ Pending SAM.gov | sba.gov | Blocked until SAM.gov UEI active. Contact Tish Lewis (tlewis@theenterprisecenter.com) for MBDA prep — Howard Brown no longer correct contact. |
| Emerging CDFI Certification | 📋 On hold | cdfifund.gov | Financing Entity test is a blocker. Requires nonprofit arm. |

---

## ATLAS MATERIALS TRANSPORT — SYSTEMS

| System | Purpose | Status |
|--------|---------|--------|
| Admin Portal | Internal deal management | Live |
| Shipper Portal | TCC Materials and other shippers | Live |
| Carrier Portal | Jachino Pallet LLC and others | Live |
| GitHub Repo | Same repo as SBA Lending Network | Active |

---

## GHG — SYSTEMS

| System | Purpose | Status |
|--------|---------|--------|
| 433 S Heald Street, Wilmington DE | Active rental, $5,211/year net cash flow | Active |
| Philadelphia Land Bank Application | 16-unit submission | ⏳ Pending decision |
| GHG_Strategy_Playbook.md | Pipeline playbook | ~/Desktop/Greenwich Hazleton Group_GHG/ |
| GHG_Property_Tracker.md | Property tracking | ~/Desktop/Greenwich Hazleton Group_GHG/ |

---

## KEY CONTACTS

| Name | Role | Org | Contact | Relationship |
|------|------|-----|---------|-------------|
| Kevin Williams | CEO | Black Squirrel Collective | kevin@blacksquirrel.co | Black Squirrel RiSE cohort executive. Keith knows him directly. CC'd on Keith's 4/1/2026 email. |
| Thomas Webster | Executive Director (BSEA) / Chief Program Officer | Black Squirrel Collective | thom@blacksquirrel.co | Black Squirrel RiSE cohort executive. Keith knows him directly. CC'd on Keith's 4/1/2026 email. |
| James Burnett | Chief Strategic Design Officer | Black Squirrel Collective | Email on file (TO field on Keith's 4/1/2026 email) | Primary Keith contact at Black Squirrel. Knows Keith directly. |
| Akem Durand | Executive Director | CIF / RTPark | akem.durand@cifvi.org | Active client — CIF/Swift Capital outsourced UW |
| Nikky Cole | Operations | CIF / RTPark | nikky.cole@cifvi.org | Doc intake contact for all CIF deals |
| Rendell Bradley | PA MBDA Business Center Director | The Enterprise Center | Via Tish Lewis: tlewis@theenterprisecenter.com | ⚠️ Howard Brown email bounced (smtp-out.flockmail.com SMTP error 4/1/2026). Bradley is current Director. Entry point is Tish Lewis, Business Development Manager. General line: 215-895-4008. mbda@theenterprisecenter.com |
| Tish Lewis | Business Development Manager | The Enterprise Center MBDA | tlewis@theenterprisecenter.com | Correct entry point for MBDA engagement form. Send new outreach here. |
| Varsovia Fernandez | Program Officer | PA CDFI Network | vfernandez@pacdfinetwork.org, 717.725.6356 | ✅ Email sent 4/1/2026 via keith.williams@sbalendingnetwork.com — re: HDBA mailing list + PMBDA |
| Vernon Stevenson | CEO/Construction | GHG | vsteven1130@gmail.com | 50/50 partner on GHG. First week tasks sent 4/1/2026 (Vernon GHG 1st week tasks.docx). GHG activating. |
| Nick Nedd | Carrier Partner | Atlas Materials Transport (Velocity Freight Solutions LLC) | nicholas.nedd88@gmail.com | Partnership letter sent 4/1/2026. Setting up carrier authority: USDOT + MC number ($300) + insurance ($750K liability/$100K cargo, ~$200-500/mo — cost split with Keith) + BOC-3 ($30-50) + UCR ($69/yr). Total setup ~$400-430. Timeline: ~3 weeks from MC application. |
| Isiah Thomas | Warm Network Contact | Philadelphia Business Lending Network (possible) | izt102@gmail.com | Keith reached out 4/1/2026 requesting PBLN contacts. Awaiting response. Reconnection email sent. |
| Delia | Tenant | GHG / Ayi Mensah Park (Condo 401) | drgafricana@gmail.com | Active tenant. April receipt + May 2026 invoice sent 3/31/2026. |

---

*Rule: This file contains descriptions and purposes only. Never write passwords, tokens, API keys, or account numbers in this file.*
