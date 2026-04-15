# FORGE — Security Register
*Last updated: 2026-04-01 | Keith Williams*
*Access risks, permissions, and exposure flags.*
*This file contains NO credentials, tokens, keys, or passwords.*

---

## SECURITY RULES (Non-Negotiable)

1. MD files contain descriptions and context only — never credentials, tokens, keys, or passwords
2. Default to read-only audit behavior before recommending any changes
3. Any action involving deletion, money movement, publishing, contracts, or external sending requires Keith's explicit approval
4. Flag anything that looks like a permissions risk or exposed credential immediately

---

## CREDENTIAL STORAGE POLICY

| Category | Where to Store | Where NOT to Store |
|----------|---------------|-------------------|
| Email passwords | Mac Keychain or 1Password | MD files, GitHub, chat |
| API keys / tokens | 1Password (install) | NEVER in code repos or MD files |
| Database passwords | .env files (gitignored) | Never committed to GitHub |
| Domain registrar access | 1Password | MD files |
| Bank / financial accounts | 1Password | Anywhere digital |
| Social Security / EIN | Physical documents + 1Password | MD files, email |

**1Password status:** ✅ ACTIVE (4/3/2026). $51.71/yr Individual plan. YubiKey #1 (Primary) + YubiKey #2 (Backup) registered as 2FA. Emergency Kit printed and stored. Installed on Mac Mini + personal laptop.

---

## KNOWN EXPOSURE RISKS

| Risk | Severity | Status | Mitigation |
|------|---------|--------|------------|
| G8WAY workbook password (SBSL) referenced in CLAUDE.md | 🔴 HIGH | Open | Remove from CLAUDE.md. Store in 1Password (once installed). |
| keithfwilliamsjr@gmail.com used for personal + grant applications | ✅ MITIGATING | In progress | DECISION 4/3: Removing personal Gmail from Mac Mini entirely. All business moves to Google Workspace. Personal email isolated to personal devices only. |
| No centralized password manager | ✅ RESOLVED | Closed 4/4/2026 | 1Password active. YubiKey #1 + #2 registered as 2FA. Emergency Kit printed + stored. |
| Passwords potentially reused or weak across accounts | 🔴 HIGH | Open | 1Password active — migration order: Gmail → Apple ID → GoDaddy → GitHub → Hostinger → Yahoo. Step 2 (deferred). |
| Auto-email code committed locally but not pushed | 🟡 MEDIUM | Open | After push: verify .env files are gitignored. Confirm no credentials in committed code before pushing. |
| ShareFile credentials not documented anywhere in FORGE | 🟢 LOW risk of loss | Open | Keith knows how to access. Confirm credentials are in 1Password (once installed). |
| SAM.gov entity registration contains EIN and legal address | 🟢 LOW (government system) | Active | Normal. Monitor for any unauthorized use of UEI once activated. |
| Supabase connection strings in codebase | 🟡 MEDIUM | Verify | Must be in .env files (gitignored). Verify before any public deployment. |
| Multiple email accounts for different businesses | 🟡 MEDIUM | Ongoing | Gmail MCP is personal only. Swift Capital work uses Chrome MCP. SBA Lending Network uses Titan. Document and enforce separation. |

---

## ACCOUNT ACCESS MAP (Updated 4/3/2026 — Post-YubiKey Deployment)

| Account | Access Method | 2FA Status | Notes |
|---------|--------------|-----------|-------|
| keithfwilliamsjr@gmail.com | REMOVING FROM MAC MINI | ✅ YubiKey x2 + Google Auth. SMS removed. | Personal ONLY. No business use. No agent access. |
| keith@swiftcapitaloptions.com | Chrome MCP (browser only) | Unknown | Swift Capital client work ONLY |
| keith.williams@sbalendingnetwork.com | Titan webmail → migrating to Google Workspace | Pending | SBA Lending Network business — will become primary |
| Apple ID (personal) | REMOVING FROM MAC MINI | ✅ YubiKey x2 + Recovery Key (offline) | Personal only. New business Apple ID planned. |
| SAM.gov | Username/password | Unknown | Entity registration. UEI: L6URLN12LLS4 |
| tax-services.phila.gov | Username: SBAlendingnetwork | Unknown | BIRT filing |
| eclipse.phila.gov | Username/password | Unknown | CAL license |
| GitHub | gh auth login (browser flow) | ✅ YubiKey x2 + Google Auth. Recovery codes stored. | Secured 4/3/2026 |
| GoDaddy | Dashboard login | ✅ YubiKey x2 + Google Auth | Secured 4/3/2026 |
| Hostinger | VPS control panel | ✅ Google Auth. Email 2FA removed. | Secured 4/3/2026 |
| Yahoo | Password + Authenticator | ✅ Google Auth. Phone retained (platform limit). Password update pending. | Low priority |
| Supabase | Dashboard login | Unknown | Two active projects. ADD 2FA. |
| nmsdc.org Hub | Awaiting invite email | N/A | Invite to keith.williams@sbalendingnetwork.com |
| DeleteMe | Personal Gmail login | ✅ Google Auth | $209 paid (2-year plan). Renewal: bi-annual. Removes personal data from brokers. |

**Completed 4/3/2026:** YubiKey deployed on Gmail, Apple ID, GitHub, GoDaddy, Hostinger. SMS removed where possible. DeleteMe purchased.
**Still needed:** 1Password setup → password migration → Supabase 2FA → SAM.gov 2FA.

---

## PERMISSIONS RULES (Cowork Sessions)

Claude is NOT permitted to take these actions without explicit approval:
- Send any email (draft → show Keith → explicit "send it" before any send)
- Delete any file
- Modify any sharing permissions on documents
- Execute any financial transaction or submit any financial form
- Publish any website changes
- Submit any application or contract
- Access passwords, stored credentials, or autofill data

---

## AUTOMATION SECURITY BOUNDARIES

| Automation | Permitted | Not Permitted |
|------------|-----------|--------------|
| CIF daily email sweep | Read, triage, draft | Send without approval |
| CIF pipeline report | Draft report | Distribute without approval |
| BizBuySell scanner (future) | Scrape, screen, draft | Send outreach without approval |
| Deal intake pipeline (future) | Receive, analyze, draft | Send to lender without approval |
| Grant applications | Research, draft | Submit without explicit confirmation |

---

## GITIGNORE CHECKLIST (SBA Lending Network Repo)

Before any commit or push, verify these are in .gitignore:
- `.env` files
- `.env.local` files
- `*.sqlite` database files
- `node_modules/`
- Any file containing API keys, connection strings, or secrets

**Last verified:** 3/29/2026 (commit 4911e50)

---

## INCIDENT LOG

| Date | Incident | Resolution |
|------|---------|-----------|
| 2026-03-31 | TTH folder accidentally renamed while file was open in Excel — data loss | Lesson: NEVER rename, move, or delete files while Keith has them open. Always confirm files are closed first. |
| 2026-04-01 | Intuit Hero Grant form started with Keith's email — discovered self-nomination is prohibited | Stopped before any false certification. Third-party nominator required. |

---

*Update this file whenever: a new account is created, a security issue is identified, permissions change, or an incident occurs.*
