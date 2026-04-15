## New Skill Requests

- **scan_sba_inbox** (Keith 2026-04-15) — scan keith@sbalendingnetwork.com Gmail inbox + sent folder for SBA-relevant threads (new leads, lender responses, borrower replies, committee decisions). Surface: unread prospects, stalled threads, decision deadlines. Output: prioritized action list. Chrome MCP required (Gmail MCP is personal email only).

## Policy Gaps (surfaced by reconciliation)

- **Owner comp addback (S-corp / LLC)** — per-deal decision, not universal. AIPSS memo: $285K owner W-2, no addback. Mirzai memo: $25K owner salary, no addback (deducted separately). Translator + adapter now gated on `owner_compensation_addback: true` flag in fixture `financials_business`. Need corresponding policy YAML entry in `cif_procedures.yaml` documenting when addback is justified (e.g. owner paid from another source, or owner comp exceeds industry median).
- **Tax allocation deduction** — memo applies explicit tax deduction ($119 Mirzai Y1, similar for AIPSS). Adapter handles via `required_distributions` field as a workaround. Clean solution: add `tax_allocation_deduction` as a first-class field in `IncomeStatement` dataclass. Low urgency — $1–$1000 impact on BANI typically.
- **Affiliate cash flow aggregation** — memos that include multi-entity guarantors (Mirzai has 3 operating affiliates + 1 holding) compute global DSCR by summing each entity's independent CF/DS. Adapter approximates via `other_income = K-1 distributions aggregate`. Variance on Mirzai: 0.02 DSCR (engine 1.65 vs memo 1.63). Acceptable for now; flag as enhancement.
