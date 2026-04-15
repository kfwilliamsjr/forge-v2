# Claude Code Handoff — Initial Repo + CI Setup

**Run this ONCE from Keith's Mac terminal. Copy the prompt below into a Claude Code session opened at `~/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul/`.**

---

## One-liner to open Claude Code in the right folder

```bash
cd ~/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul && claude
```

## Paste this into Claude Code

```
Initialize this folder as a git repo, wire up the pre-commit hook, run the golden harness, commit everything, push to a new GitHub repo named "forge-v2" under the Atlasmaterialstransport account, and verify the GitHub Actions harness workflow goes green.

Exact steps:

1. Confirm we are in ~/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul (`pwd`). Abort if not.

2. Initialize git:
   git init
   git branch -M main

3. Install the local pre-commit hook:
   git config core.hooksPath .githooks
   chmod +x .githooks/pre-commit

4. Sanity-run the harness BEFORE committing:
   python3 FORGE_v2/golden/tools/run_golden.py
   Expect: "Summary: 16/16 passed" — abort if not green.

5. Stage everything honoring .gitignore:
   git add -A
   git status

6. Create the initial commit:
   git commit -m "Initial commit — FORGE v2 engine + portfolio state machine

   - Deterministic math backend (BANI, DSCR, rate shock, liquidity, affiliate FCF)
   - 9 policy YAMLs (single source of truth for thresholds)
   - 20+ atomic skills
   - 3 reconciled golden fixtures (AIPSS, Mirzai, Amber) — 16/16 green
   - Portfolio state machine (portfolio.json + promote_deal + regenerate_dashboard)
   - Scheduled Intelligence Loop (sync_portfolio_from_signals + approve_pending)
   - CI: GitHub Actions runs harness on every PR"

7. Verify you're authenticated as kfwilliamsjr and create the repo PUBLIC:
   gh api user --jq .login   # must print "kfwilliamsjr" — if not, run `gh auth login` first
   gh repo create kfwilliamsjr/forge-v2 --public --source=. --remote=origin --push --description "FORGE v2 — deterministic SBA/CDFI underwriting engine + portfolio state machine"
   (Atlasmaterialstransport is Keith's OLD org — do NOT push there. Target is kfwilliamsjr.)

8. Verify the CI workflow queued and succeeds:
   gh run watch
   Expect: golden.yml completes green.

9. Print the repo URL and a summary: commit sha, CI status, files tracked count, files ignored count.

10. If anything fails, DO NOT force-push or bypass. Report the error and stop.

Hard rules:
- Never use --no-verify
- Never commit borrower PII (the .gitignore blocks it; verify no PII slipped through before push)
- Do not touch the website/ repo — this is a SEPARATE repo for Agentic_Overhaul only
```

---

## What this sets up

- **New GitHub repo:** `kfwilliamsjr/forge-v2` — PUBLIC (portfolio material + future licensing visibility).
- **Local pre-commit hook:** every commit runs `run_golden.py`. A regression = commit blocked.
- **GitHub Actions:** every push/PR runs the harness in the cloud. A regression = red CI badge, PR blocked.
- **.gitignore:** blocks borrower PII, local audit logs, regenerable dashboard HTML.
- **Separate from the website repo:** engine IP ≠ marketing site.

## After initial setup — your working loop

From then on, every time we finish work in Cowork, the end-of-session prompt in Claude Code is just:

```
Review the working tree, run the harness, commit if green, push to origin main.
```

That's it. Cowork builds the business; Claude Code hardens the engine into version control. Both converge through `CLAUDE.md` + the harness.

## Second repo to sync: website/ (existing — remote is stale)

`~/Desktop/SBA_Lending_Claude_MD/website/` is a git repo currently pointed at the OLD `Atlasmaterialstransport/sba-lending-network`. You've since pulled the repo under `kfwilliamsjr/sba-lending-network`. The local remote is stale.

Fix in a second Claude Code session (NOT tonight — keep tonight focused on forge-v2):

```
cd ~/Desktop/SBA_Lending_Claude_MD/website
claude
```

Then tell Claude Code:
> Update the origin remote from Atlasmaterialstransport/sba-lending-network to kfwilliamsjr/sba-lending-network. Verify with `gh repo view`. Then review uncommitted changes (CLAUDE.md, CommissionSelector.tsx, prospecting SQL migration, etc.), commit what's clean, and push.

## Repo naming note

You already have `kfwilliamsjr/underwriteos` (your existing underwriting tool). FORGE v2's internal Python package is also named `underwriteos` — that's fine, it lives inside `forge-v2` as `_legacy_forge/underwriteos/`. No naming collision at the repo level.
