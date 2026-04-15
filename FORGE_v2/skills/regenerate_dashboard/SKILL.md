---
name: regenerate_dashboard
version: 1.0.0
status: production
triggers:
  - "regenerate dashboard"
  - "show portfolio"
  - "update portfolio"
  - "portfolio dashboard"
  - "where are my deals"
---

# regenerate_dashboard

## Layer 1 — Trigger
Rebuild PORTFOLIO.html from portfolio.json. One HTML file, opens in browser, shows "NEEDS YOU TODAY" at top + full pipeline by stage below.

## Layer 2 — Inputs
- `Agentic_Overhaul/portfolio/portfolio.json` (required)

## Layer 3 — Outputs
- `Agentic_Overhaul/portfolio/PORTFOLIO.html`

## Layer 4 — Procedure
1. Run `python3 Agentic_Overhaul/portfolio/tools/regenerate_dashboard.py`
2. Confirm deal count + "needs Keith" count in output
3. Share computer:// link to PORTFOLIO.html

## Layer 5 — Policy
- Never auto-edit portfolio.json here. Read only. Use `promote_deal` to change state.
- Fail loud if portfolio.json is missing or malformed.
