# FORGE — Security Infrastructure Setup Checklist
*Created: 2026-04-03 | Keith Williams*
*Complete stack: Tailscale + 1Password + YubiKey + Google Workspace + New Router*

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────┐
│                   TAILSCALE MESH                     │
│              (encrypted, private network)            │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Mac Mini │  │  Laptop  │  │  GrapheneOS Phone │  │
│  │ (home)   │  │ (mobile) │  │  (215-290-5738)   │  │
│  │ Always On│  │ Anywhere │  │  Notifications    │  │
│  └────┬─────┘  └────┬─────┘  └───────────────────┘  │
│       │              │                                │
│  ┌────┴──────────────┴────────────────────────────┐  │
│  │            SERVICES (Mac Mini)                  │  │
│  │  ClearPath (localhost:3000)                     │  │
│  │  G8WAY Engine (localhost:3001)                  │  │
│  │  Supabase (local dev)                           │  │
│  │  Scheduled Tasks (Claude Code / Cowork)         │  │
│  │  Auto-email system (Vercel, external)           │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

AUTHENTICATION LAYERS:
  YubiKey ──► Tailscale device enrollment (one-time per device)
  YubiKey ──► 1Password vault unlock (first time per device)
  YubiKey ──► Google Workspace admin (sensitive changes only)
  YubiKey ──► Mac Mini FileVault (boot/restart only)

  Password ──► Mac Mini daily login (Touch ID optional)
  API Keys ──► Agent automation (.env files, never exposed)
  1Password ──► Everything else (all accounts, all credentials)
```

---

## COST SUMMARY

| Item | Cost | Type | Status |
|------|------|------|--------|
| Tailscale (Free tier, 3 devices) | $0 | Monthly | Planned |
| 1Password Individual | $2.99 | Monthly | Planned |
| Google Workspace Business Starter | $7.20 | Monthly | Planned |
| YubiKey 5C NFC x2 | $105.00 | One-time | ✅ Purchased 4/3 |
| TP-Link BE11000 Wi-Fi 7 Router | $219.99 | One-time | ✅ Purchased 4/3 |
| SanDisk Extreme Pro SSD 1TB | $224.99 | One-time | ✅ Purchased 4/3 |
| UPS Battery Backup (CyberPower 600VA) | ~$50 | One-time | Needed |
| Second backup drive (Samsung T7 Shield) | ~$80 | One-time | Needed |
| **Total ongoing** | **~$10.19/month** | | |
| **Total one-time (spent)** | **$549.98** | | |
| **Total one-time (remaining)** | **~$130** | | UPS + backup drive |

---

## PHASE 1: FOUNDATION (Do First — 1 Hour)

### 1.1 — Purchase Hardware
- [x] YubiKey 5C NFC x2 — $105 (Best Buy, 4/3/2026) ✅
- [x] TP-Link BE11000 Tri-Band Wi-Fi 7 Router — $219.99 (Best Buy, 4/3/2026) ✅
- [x] SanDisk Extreme Pro SSD 1TB (SDSSDE81-1T) — $224.99 (Best Buy, 4/3/2026) ✅
- [ ] UPS battery backup (CyberPower CP600LCD or similar) — ~$50 (still needed)
- [ ] Second backup drive (Samsung T7 Shield 1TB ~$80) — for backup rotation (still needed)
- [ ] DO NOT plug in Cisco Meraki Z3-HW — employer-issued, Colony Bank IT must release first

### 1.2 — Set Up New Router
- [ ] Unbox and connect new router to modem
- [ ] Change default admin password (store in 1Password later)
- [ ] Set network name (SSID) — use something non-identifying
- [ ] Enable WPA3 encryption (or WPA2 if devices don't support WPA3)
- [ ] Disable WPS (Wi-Fi Protected Setup) — security risk
- [ ] Update router firmware to latest version
- [ ] Connect Mac Mini, laptop, and phone to new network
- [ ] Connect UPS to Mac Mini power — protects against brief outages

### 1.3 — Install 1Password
- [ ] Sign up at 1password.com ($2.99/month Individual plan)
- [ ] Install on Mac Mini
- [ ] Install on laptop
- [ ] Install on GrapheneOS phone
- [ ] Install browser extension on Chrome
- [ ] Register YubiKey #1 as 2FA method in 1Password
- [ ] Register YubiKey #2 as backup 2FA method
- [ ] Store 1Password Emergency Kit in physical safe (NOT digital)

### 1.4 — Migrate All Credentials to 1Password
- [ ] SAM.gov login
- [ ] tax-services.phila.gov (Username: SBAlendingnetwork)
- [ ] eclipse.phila.gov (CAL license)
- [ ] GitHub account
- [ ] Supabase dashboard
- [ ] Hostinger VPS control panel
- [ ] NMSDC Hub (when invite arrives)
- [ ] ShareFile (swift.sharefile.com)
- [ ] Cal.com
- [ ] Domain registrar accounts (Namecheap/GoDaddy)
- [ ] G8WAY workbook password (remove from CLAUDE.md after storing)
- [ ] Router admin credentials
- [ ] All other accounts from security-register.md

---

## PHASE 2: TAILSCALE MESH (30 Minutes)

### 2.1 — Create Tailscale Account
- [ ] Sign up at tailscale.com (use new Google Workspace email once created, or personal for now)
- [ ] Choose Free plan (up to 3 devices)

### 2.2 — Install on All Devices
- [ ] Install Tailscale on Mac Mini → note Tailscale IP (100.x.x.x)
- [ ] Install Tailscale on laptop → note Tailscale IP
- [ ] Install Tailscale on GrapheneOS phone → note Tailscale IP
- [ ] Verify all 3 devices can see each other: `tailscale status`

### 2.3 — Lock Down with YubiKey
- [ ] Enable Tailscale device approval (admin console → Device Settings)
- [ ] Register YubiKey as auth method for Tailscale account
- [ ] Test: try adding a fake device — should require YubiKey tap to approve
- [ ] Store Tailscale account credentials in 1Password

### 2.4 — Configure Mac Mini as Always-On Node
- [ ] Enable Tailscale to run at login (System Settings → Login Items)
- [ ] Set Mac Mini to "Prevent automatic sleeping" (System Settings → Energy)
- [ ] Set Mac Mini to "Start up automatically after power failure" (Energy settings)
- [ ] Test: from laptop on phone hotspot, access Mac Mini via Tailscale IP — confirm connectivity

### 2.5 — Test Remote Access
- [ ] From laptop on a DIFFERENT network (phone hotspot or coffee shop):
  - [ ] `ping 100.x.x.x` (Mac Mini Tailscale IP) — should respond
  - [ ] Open browser to `http://100.x.x.x:3000` — should show ClearPath
  - [ ] Open browser to `http://100.x.x.x:3001` — should show G8WAY
  - [ ] SSH to Mac Mini: `ssh keith@100.x.x.x` — should connect

---

## PHASE 3: GOOGLE WORKSPACE (45 Minutes)

### 3.1 — Set Up Google Workspace
- [ ] Go to workspace.google.com → Start free trial or sign up ($7.20/month Business Starter)
- [ ] Use domain: sbalendingnetwork.com
- [ ] Verify domain ownership (DNS TXT record via Hostinger)
- [ ] Create primary account: keith@sbalendingnetwork.com (or keith.williams@)
- [ ] Set up MX records to route email through Google (replaces Titan)

### 3.2 — Migrate from Titan Email
- [ ] Export/forward important emails from Titan (keith.williams@sbalendingnetwork.com)
- [ ] Update email references everywhere:
  - [ ] SAM.gov contact email
  - [ ] NMSDC application
  - [ ] Philadelphia OEO (when applying)
  - [ ] All CDFI/bank outreach templates
  - [ ] Cal.com booking notifications
  - [ ] GitHub account email
- [ ] Keep Titan active for 30 days as forwarding fallback, then cancel

### 3.3 — Secure Google Workspace
- [ ] Register YubiKey #1 as 2FA on Google account
- [ ] Register YubiKey #2 as backup
- [ ] Enable Advanced Protection Program (optional, maximum security)
- [ ] Store Google Workspace admin credentials in 1Password

### 3.4 — Connect Gmail MCP to Business Email
- [ ] In Cowork, disconnect personal Gmail MCP (keithfwilliamsjr@gmail.com)
- [ ] Reconnect Gmail MCP to new Google Workspace account (keith@sbalendingnetwork.com)
- [ ] Test: search for emails, verify access works
- [ ] This enables agents to read/draft business email directly

### 3.5 — Set Up Google Drive Structure
- [ ] Create folder: `SBA Lending Network/`
  - [ ] Subfolder: `Client Documents/`
  - [ ] Subfolder: `Proposals/`
  - [ ] Subfolder: `Certifications/`
  - [ ] Subfolder: `Grants/`
- [ ] Connect Google Drive MCP in Cowork (search MCP registry for Google Drive connector)

---

## PHASE 4: FILE ACCESS ARCHITECTURE

### 4.1 — Document Storage Map

| Document Type | Primary Location | Backup | Agent Access |
|---------------|-----------------|--------|-------------|
| FORGE system files (MD) | Mac Mini ~/Desktop/FORGE/ | Samsung T7 Shield #1 | Direct (Cowork mount) |
| Client borrower docs | ShareFile | Google Drive | Chrome MCP / ShareFile MCP |
| SBA proposals & deliverables | Google Drive | Samsung T7 Shield #1 | Google Drive MCP |
| Grant applications | Google Drive | Samsung T7 Shield #1 | Google Drive MCP |
| Code repos | GitHub (private) | Mac Mini local | Claude Code / Git |
| ClearPath database | Supabase | Local Supabase backup | API / .env keys |
| Personal documents | Samsung T7 Shield #2 (encrypted) | N/A | Mount when needed only |
| Credentials | 1Password | Emergency Kit (physical) | Never — agents use .env |

### 4.2 — Personal Document Access
- [ ] Personal docs live on Samsung T7 Shield #2 (encrypted with Mac disk utility)
- [ ] Plug in and mount ONLY when you need Cowork to access personal files
- [ ] Unmount when done — this is your air gap for personal data
- [ ] Agents NEVER get persistent access to personal documents

### 4.3 — Agent Credential Access (No YubiKey Needed)
- [ ] All API keys and tokens stored in .env files on Mac Mini
- [ ] .env files are gitignored (verify: `cat .gitignore | grep env`)
- [ ] Agents read credentials from .env at runtime — no interactive login needed
- [ ] Scheduled tasks authenticate via stored tokens, not browser flow
- [ ] YubiKey is ONLY for: new device enrollment, admin changes, emergency access

---

## PHASE 5: MAC MINI HARDENING

### 5.1 — System Security
- [ ] Enable FileVault disk encryption (System Settings → Privacy & Security)
  - Uses password on boot/restart only
  - YubiKey can serve as secondary unlock (via pam-u2f, optional advanced setup)
- [ ] Set auto-login after FileVault unlock (so Mac resumes after power failure + UPS)
- [ ] Enable firewall (System Settings → Network → Firewall)
- [ ] Disable remote login for all users EXCEPT your account
- [ ] Set Mac Mini to never sleep (Energy → Prevent automatic sleeping)
- [ ] Set "Start up automatically after power failure" ON

### 5.2 — Agent Continuity (Agents Keep Running When You're Away)
- [ ] Tailscale runs as system service — survives sleep/wake, persists across sessions
- [ ] ClearPath and G8WAY: set up as launchd services (auto-start on boot)
  ```bash
  # Create launch agent for ClearPath
  # File: ~/Library/LaunchAgents/com.sbalending.clearpath.plist
  # Sets working directory, runs npm start, restarts on failure
  ```
- [ ] Scheduled Cowork tasks: run via Claude's scheduler (already set up)
- [ ] If Mac Mini restarts (power outage beyond UPS capacity):
  1. FileVault asks for password (you must enter remotely or physically)
  2. After login, Tailscale auto-connects
  3. LaunchAgents restart ClearPath + G8WAY automatically
  4. Scheduled tasks resume on next trigger

### 5.3 — Backup Schedule
- [ ] Weekly: plug in Samsung T7 Shield #1, run Time Machine or rsync of FORGE + code
- [ ] Monthly: verify 1Password Emergency Kit is accessible
- [ ] Quarterly: test full restore from backup (pick one folder, restore, verify)

---

## PHASE 6: DISCONNECT PERSONAL GMAIL FROM BUSINESS

### 6.1 — Separate Personal from Business
- [ ] Remove Gmail MCP connection to keithfwilliamsjr@gmail.com
- [ ] All business correspondence moves to Google Workspace (keith@sbalendingnetwork.com)
- [ ] Personal Gmail stays for personal use only — no agent access
- [ ] Grant correspondence currently on personal Gmail: forward key threads to business email
- [ ] Update control-center.md and systems-inventory.md to reflect new email architecture

### 6.2 — Email Architecture (Final State)

| Email | Purpose | Agent Access | Device |
|-------|---------|-------------|--------|
| keith@sbalendingnetwork.com | ALL SBA Lending Network business | Gmail MCP (full) | Mac Mini + Laptop |
| keith@swiftcapitaloptions.com | Swift Capital / CIF work only | Chrome MCP (browser) | Mac Mini + Laptop |
| keithfwilliamsjr@gmail.com | Personal only | NONE — disconnected | Personal devices ONLY |

### 6.3 — Mac Mini Isolation Policy (NEW — 4/3/2026)
- [ ] Remove personal Gmail (keithfwilliamsjr@gmail.com) from Chrome on Mac Mini
- [ ] Remove personal Google account from Mac Mini entirely
- [ ] Remove personal ShareFile access from Mac Mini
- [ ] Create NEW business Apple ID (tied to SBA Lending Network email once Google Workspace is live)
- [ ] Sign Mac Mini into business Apple ID only
- [ ] Personal Apple ID stays on personal laptop and phone only
- [ ] Storage: Google Drive (business) + SanDisk SSD (local working files) — no personal cloud storage on Mac Mini

---

## VERIFICATION CHECKLIST (After Everything Is Set Up)

- [ ] From laptop at a coffee shop, can you access ClearPath via Tailscale?
- [ ] From laptop, can you SSH into Mac Mini?
- [ ] Can Cowork read/draft emails on keith@sbalendingnetwork.com?
- [ ] Does 1Password sync across all 3 devices?
- [ ] Is YubiKey required to add a new device to Tailscale?
- [ ] Does Mac Mini auto-recover after a simulated power cycle?
- [ ] Are all .env files gitignored? (`git status` shows no secrets)
- [ ] Is G8WAY workbook password removed from CLAUDE.md and stored in 1Password?
- [ ] Can scheduled tasks run without any manual login or YubiKey tap?
- [ ] Is personal Gmail fully disconnected from all business tools?

---

## ORDER OF OPERATIONS (Suggested Sequence)

1. Buy YubiKeys + router + UPS (order today, arrive in 2-3 days)
2. Install 1Password NOW (no hardware needed, $2.99/month)
3. Migrate all credentials to 1Password this session
4. Set up new router when it arrives
5. Install Tailscale on all devices (30 min)
6. Set up Google Workspace (45 min — requires DNS changes, allow 24h propagation)
7. Migrate from Titan to Google Workspace
8. Connect Gmail MCP to business email
9. Harden Mac Mini (FileVault, launchd services, energy settings)
10. Test everything from a remote location
11. Disconnect personal Gmail from business tools
12. Update all FORGE files to reflect new architecture

---

*This checklist is a living document. Update status as each item is completed.*
*Store NO credentials in this file — all secrets go in 1Password.*
