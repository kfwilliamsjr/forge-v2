# IT SETUP PLAN — April 3, 2026
*Session tracker. Update in real time as steps are completed.*
*Goal: Full security stack operational before agents go live.*

---

## STATUS: END OF DAY 4/4/2026 — Steps 1+3 done. Resume tomorrow with Action Required check, Tailscale, router.

---

## EXECUTION ORDER

| Step | Task | Status | Notes |
|------|------|--------|-------|
| 1 | **Install 1Password** — create vault, set master password, register YubiKeys | ✅ DONE | Account created. Extension installed. Secret key issued. Emergency Kit printed + stored. YubiKey #1 ✅. YubiKey #2 ✅. Installed on personal laptop. Deferred: FORGE-DRIVE encryption, vault sync confirmation. |
| 2 | **Password migration** — all 6 priority accounts to 20+ char random | ⏳ | Gmail → Apple ID → GoDaddy → GitHub → Hostinger → Yahoo |
| 3 | **Google Workspace** — business email (keith@sbalendingnetwork.com) | ✅ DONE | Workspace Starter ($7/mo) signed up 4/4/2026. DNS verified. MX records set at Hostinger. Inbox active (keith@sbalendingnetwork.com). Chrome Work profile created. "Action Required" badge still showing — check tomorrow. |
| 4 | **New business Apple ID** — tied to SBA Lending Network email | ⏳ | After Google Workspace is live. |
| 5 | **Router setup** — TP-Link BE11000, split networks (personal + Mac Mini) | ⏳ | Unbox, configure, secure. |
| 6 | **Tailscale** — mesh Mac Mini + Laptop + GrapheneOS phone | ⏳ | Install on all 3 devices. Enable exit node on Mac Mini. |
| 7 | **YubiKey on Tailscale + 1Password** — passkey registration | 🟡 PARTIAL | 1Password: DONE (both keys). Tailscale: pending Step 6. |
| 8 | **Remove personal accounts from Mac Mini** — Gmail, personal Apple ID, ShareFile | ⏳ | LAST — only after business email + 1Password are fully operational. |
| 9 | **Mac Mini hardening** — FileVault, energy settings, launchd services | ⏳ | Auto-recovery after power failure. |
| 10 | **Verification** — test full stack from remote location | ⏳ | Coffee shop test: Tailscale, ClearPath, email, 1Password. |

---

## PURCHASES (4/3/2026)

| Item | Price | Status |
|------|-------|--------|
| YubiKey 5C NFC x2 | $105.00 | ✅ Purchased |
| SanDisk Extreme Pro SSD 1TB (FORGE-DRIVE) | $224.99 | ✅ Purchased + Connected |
| TP-Link BE11000 Wi-Fi 7 Router | $219.99 | ✅ Purchased |
| DeleteMe (2-year plan) | $209.00 | ✅ Purchased |
| UPS Battery Backup | ~$50 | ⏳ Still needed |
| Second backup drive | ~$80 | ⏳ Still needed |
| 1Password Individual (annual) | $51.71 | ✅ Signed up 4/3. Renewal 4/18/2026. |
| Google Workspace Business Starter (monthly) | $7.00/mo | ✅ Signed up 4/4/2026. |
| **Total spent** | **$817.69** | |

---

## STEP 1 LOG — 1PASSWORD

- [x] Go to 1password.com → sign up (Individual plan, $51.71/year billed annually on 4/18/2026) ✅ 4/3/2026
- [x] Generate master password (20+ characters, written down offline) ✅ 4/3/2026
- [x] Install on Mac Mini ✅ 4/3/2026
- [x] Install on personal laptop ✅ 4/4/2026
- [x] Install browser extension (Chrome) ✅ 4/3/2026
- [x] Secret key issued ✅ 4/3/2026
- [x] Emergency Kit: saved to FORGE-DRIVE ✅ 4/4/2026
- [x] Emergency Kit: printed from personal laptop, PDF deleted ✅ 4/4/2026
- [x] Register YubiKey #1 as 2FA (Primary Yubi Key) ✅ 4/4/2026
- [x] Register YubiKey #2 as backup 2FA (Backup Yubi Key) ✅ 4/4/2026
- [x] Store printed Emergency Kit in physical safe ✅ 4/4/2026
- [ ] Confirm vault syncs across devices
- [ ] Encrypt FORGE-DRIVE (reformat to APFS Encrypted — deferred, do before Step 2)

### HARDWARE REFERENCE
- **SanDisk Extreme Pro SSD 1TB** → renamed to **FORGE-DRIVE**
  - Role: Local working storage, secure file transfer, encrypted backup
  - Mount point: Desktop / Finder sidebar under Locations
  - Referenced in all FORGE files as "FORGE-DRIVE"

## STEP 2 LOG — PASSWORD MIGRATION

| Account | Old password replaced | New password (20+ random) stored in 1Password | 2FA confirmed | Status |
|---------|----------------------|----------------------------------------------|---------------|--------|
| Gmail (personal) | — | — | ✅ YubiKey + Auth | ⏳ |
| Apple ID (personal) | — | — | ✅ YubiKey + Recovery Key | ⏳ |
| GoDaddy | — | — | ✅ YubiKey + Auth | ⏳ |
| GitHub | — | — | ✅ YubiKey + Auth | ⏳ |
| Hostinger | — | — | ✅ Auth | ⏳ |
| Yahoo | — | — | ✅ Auth | ⏳ |

## STEP 3 LOG — GOOGLE WORKSPACE

- [x] Sign up for Google Workspace Business Starter ($7/mo) ✅ 4/4/2026
- [x] Admin account: keithfwilliamsjr@gmail.com (recovery email)
- [x] Domain: sbalendingnetwork.com
- [x] Business email: keith.williams@sbalendingnetwork.com (or keith@sbalendingnetwork.com — confirm)
- [x] Verify domain ownership (DNS TXT record at Hostinger) ✅ 4/4/2026
- [x] Set up MX records at Hostinger (replace Titan MX records) ✅ 4/4/2026
- [x] DNS propagation ✅ 4/4/2026
- [x] Chrome Work profile created for keith@sbalendingnetwork.com ✅ 4/4/2026
- [ ] Resolve "Action Required" badge in Chrome Work profile
- [ ] Send/receive test email
- [ ] Install 1Password extension in Work profile
- [ ] Install Claude in Chrome extension in Work profile
- [ ] Migrate Titan email data if needed
- [ ] Connect Gmail MCP to business email
- [ ] Store Google Workspace admin password in 1Password
- [ ] Cancel Titan email subscription (after confirming Workspace is fully operational)

## STEP 4 LOG — BUSINESS APPLE ID
*(To be filled when we reach this step)*

## STEP 5 LOG — ROUTER SETUP
*(To be filled when we reach this step)*

## STEP 6 LOG — TAILSCALE
*(To be filled when we reach this step)*

## STEP 7 LOG — YUBIKEY REGISTRATION (TAILSCALE + 1PASSWORD)
*(To be filled when we reach this step)*

## STEP 8 LOG — REMOVE PERSONAL ACCOUNTS FROM MAC MINI
*(To be filled when we reach this step — THIS IS LAST)*

## STEP 9 LOG — MAC MINI HARDENING
*(To be filled when we reach this step)*

## STEP 10 LOG — VERIFICATION
*(To be filled when we reach this step)*

---

*After Step 10 is complete: agents are cleared to run. Not before.*

---

## SESSION LOG

### 4/4/2026 — Day 2

**Completed:**
- Step 1 (1Password): Account created, extension installed, Emergency Kit printed + stored, YubiKey #1 + #2 registered as 2FA, installed on personal laptop
- Step 3 (Google Workspace): Business Starter ($7/mo) signed up, domain verified, MX records set, inbox active, Chrome Work profile created
- Step 7 partial: YubiKeys registered on 1Password (Tailscale side pending)

**Deferred:**
- Step 2 (password migration) — tabled by user
- FORGE-DRIVE encryption (reformat to APFS Encrypted)
- Vault sync confirmation across devices
- Tailscale setup — deferred to 4/5/2026

**Open items for tomorrow (4/5/2026):**
1. Resolve "Action Required" badge in Chrome Work profile
2. Install 1Password + Claude in Chrome extensions in Work profile
3. Send/receive test email from keith@sbalendingnetwork.com
4. Store Google Workspace password in 1Password
5. Tailscale setup (Mac Mini + Laptop + GrapheneOS phone)
6. Router setup (TP-Link BE11000 — still in box)
7. Encrypt FORGE-DRIVE

**Spent today:** $7.00 (Google Workspace)
**Running total:** $817.69
