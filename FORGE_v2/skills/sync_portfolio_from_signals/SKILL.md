---
name: sync_portfolio_from_signals
version: 1.0.0
status: production
triggers:
  - "sync portfolio"
  - "what's new on my deals"
  - "check signals"
  - "refresh portfolio from email"
---

# sync_portfolio_from_signals

## Layer 1 — Trigger
Read email / Sent / ShareFile / Supabase signals and queue inferred portfolio updates for Keith's review. NEVER writes portfolio.json directly — always goes through `pending_updates.json`.

## Layer 2 — Signal sources (priority order)
1. **SBA inbox + Sent** — Gmail MCP, `keith@sbalendingnetwork.com`. Uses `gmail_search_messages` / `gmail_read_thread`. Tag signals as `sba_gmail` / `sba_sent`.
2. **Swift inbox + Sent** — Chrome MCP (Google Workspace, `keith@swiftcapitaloptions.com`). Open Gmail via browser, navigate, read. Tag `swift_gmail` / `swift_sent`.
3. **CIF ShareFile** — Chrome MCP. Navigate to CIF portal, list new documents per deal folder. Tag `sharefile`.
4. **Supabase** — via daily-lead-prospecting sweep. HOT leads (score >= 75) auto-queue as `new_deal: true`. Tag `supabase`.

## Layer 3 — Inference rules
For each deal in `portfolio.json`, match signals by:
- Borrower name (fuzzy) in subject/body/filename
- Email thread ID tracked per deal (add `thread_ids` array to deal record as needed)
- `deal_id` literal

**Stage transition heuristics:**
| Observed signal | Proposed stage | Confidence |
|---|---|---|
| Sent memo+XLSX+PDF to Akem | committee (owner=akem) | 0.85 |
| Akem reply "approved" | committee (owner=committee) | 0.80 |
| Committee reply "approved" | closing | 0.80 |
| Committee reply "decline" | decision (blocker=declined) | 0.90 |
| New ShareFile doc in deal folder | no stage change; update last_action | 0.60 |
| Borrower "here are the docs" | spreads_ready | 0.70 |
| No contact 14+ days | add blocker="stale_14d" | 0.90 |
| Supabase HOT lead | new_deal=true, stage=intake | 0.75 |

Confidence < 0.60: do not queue — log only.

## Layer 4 — Procedure
1. Load `portfolio/portfolio.json` — enumerate active deals (not in closing/purge).
2. Query each source. For each signal:
   - Identify deal (or flag `new_deal`)
   - Determine proposed update per Layer 3 table
   - Call `python3 portfolio/tools/append_pending.py --deal_id X --source Y --signal "..." [--proposed_stage ...] --confidence Z`
3. Run `python3 portfolio/tools/regenerate_dashboard.py` to surface PENDING section.
4. Notify Keith: "N pending updates queued. Review at PORTFOLIO.html or run approve_pending.py --list."

## Layer 5 — Policy
- **Review-first by default.** Nothing hits portfolio.json without `approve_pending.py --approve`.
- **Never auto-send email.** If a signal implies an outbound (follow-up, thank-you, decline), draft only and queue in email-drafter.
- **Never infer a decision gate.** spreads_ready, uw_complete, memo_draft, memo_final transitions require Keith's explicit `promote_deal` — sync can suggest but not apply.
- **Every signal is auditable.** Full quote/summary stored in `signal` field. If borrower disputes, the evidence is on disk.
- **Graduation to auto-apply:** after 30 consecutive days with zero rejected sync updates, flip review-first off for confidence >= 0.85 updates. Not before.
