# How to Get Your FORGE Skills Into This Overhaul
*Created: 2026-04-15*

## The problem
Your existing FORGE skills live at `~/Desktop/FORGE/skills/`. The Cowork session is mounted on `~/Desktop/SBA_Lending_Claude_MD/` — so I can't read FORGE from here. I also cannot mount folders from my side; only you can.

## Solution: copy FORGE into this overhaul folder

This serves two goals at once:
1. I can audit the actual skill files
2. Your whole overhaul (old + new) lives in ONE portable folder you can zip/upload anywhere when you graduate to localized agents

## Option A — Terminal (fastest, 5 seconds)
Open Terminal and paste this single command:

```bash
cp -R ~/Desktop/FORGE/ ~/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul/_legacy_forge/
```

That's it. Tell me "done" and I'll audit immediately.

## Option B — Finder (no terminal)
1. Open Finder
2. Go to `~/Desktop/` (your Desktop)
3. Right-click the `FORGE` folder → **Copy**
4. Navigate to `~/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul/_legacy_forge/`
5. Right-click inside → **Paste Item**
6. Tell me "done"

## Option C — Drag & Drop
Drag the `FORGE` folder from your Desktop into `SBA_Lending_Claude_MD/Agentic_Overhaul/_legacy_forge/` in Finder.
**Important:** hold `Option` while dragging to COPY (not move). Moving would break the live skills your current workflow depends on.

## What happens after
Once FORGE is in `_legacy_forge/`, I'll:
1. Read every SKILL.md file
2. Score each on the 5-layer compliance checklist
3. Update the registry CSV with real data (not inferred)
4. Rewrite each as atomic v1.0 skills in `FORGE_v2/skills/`
5. Your old FORGE keeps running untouched on your Desktop — nothing breaks

## When this overhaul is portable
Everything — legacy audit, new atomic skills, router, agent.json, policy YAMLs, golden dataset, audit logs — lives inside:

```
~/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul/
```

Zip that folder = full portable agentic system. Upload to a local agent runtime, another machine, or back into Cowork on a different computer — no dependencies outside this folder.
