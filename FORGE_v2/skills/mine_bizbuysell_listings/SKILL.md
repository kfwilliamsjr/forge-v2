---
name: mine_bizbuysell_listings
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 1-extraction
depends_on: []
policy_refs: [policy/colony_grids.yaml, policy/bizbuysell_filters.yaml]
---

# SKILL: mine_bizbuysell_listings

## Layer 1 — Trigger Description
Use to scan BizBuySell (via Chrome MCP) for SBA-eligible acquisition listings in the $150K-$5M range. Pre-screens against Colony Bank appetite tiers and outputs a ranked prospect list with broker contact info and deal-fit scores.

## Layer 2 — Negative Trigger
- Do NOT contact listing brokers from this skill — output is a prospect list only.
- Do NOT include prohibited industries (cannabis, nursing homes, assisted living, golf courses).
- Do NOT use cached data older than 7 days — fresh scan only.
- Do NOT scan outside Colony's Southeast US footprint for sub-75% guaranty deals.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| search_filters | object | Yes |
| max_results | int | No | default 25 |

## Layer 4 — Procedure

### Step 1 — Build search queries
From `policy/bizbuysell_filters.yaml` defaults + user filters:
- **Priority industries** (run parallel searches):
  - medical/dental practice
  - pharmacy / vet clinic
  - national-brand gas station
  - national-flag hotel
  - CRE-secured professional services
- **Price range:** $150K-$5M (SBA 7(a) sweet spot)
- **Geography:** Nationwide if 75%+ SBA guaranty applies; Southeast US otherwise (Colony footprint)

Search URLs pattern: `site:bizbuysell.com [industry] for sale [state] cash flow [year]`. Run web searches first to identify listing URLs.

### Step 2 — Navigate to each listing via Chrome MCP
For each candidate URL, `mcp__Claude_in_Chrome__navigate` → `get_page_text` → `javascript_tool` to extract:
- asking_price
- SDE / cash_flow
- gross_revenue
- years_established
- broker_name
- brokerage_firm
- listing_id

⚠️ Web-search summaries are estimates. Always verify against the real listing page before scoring. ⚠️ BizBuySell hides broker phone/email behind login — extract broker NAME and FIRM, research contact separately.

### Step 3 — Research broker contact (separate searches)
For each broker:
- `[Broker Name] [Brokerage] email contact`
- `[Brokerage] email "@domain.com"`
- Check brokerage's own website contact page via Chrome MCP
- If masked (e.g., `f***@hedgestone.com`), try `[firstinitial][lastname]@domain.com` and `[firstname].[lastname]@domain.com` — flag `email_guessed` for Keith verification before send.
- If form-only, note phone instead.

### Step 4 — Estimated DSCR pre-screen
For each listing with SDE data:
```
assumed_financing: LTV 80%, rate 10.0%, term 10yr (120 months)
loan_amount = asking_price * 0.80
annual_ds = PMT(0.10/12, 120, -loan_amount) * 12
est_dscr = sde / annual_ds
```
If `est_dscr < 1.25x` → classify FAIL regardless of other factors.

### Step 5 — Industry-specific flags
- Gas stations: must be national brand (Shell, Mobil, Chevron, BP, etc.). Unbranded = Colony likely decline.
- Franchises: note FUND tier if identifiable. FUND 750+ = top-tier, 600-749 = acceptable.
- Hotels: must be national flag.
- Medical/dental: flag if practice vs. MSO structure.

### Step 6 — Appetite-tier scoring
Use `policy/colony_grids.yaml → appetite_tiers`:
- **Top-Tier** (15 pts deal-fit): medical, dental, vet, pharmacy, CRE-secured professional, FUND 750+ franchise
- **Acceptable** (10 pts): branded gas station, flag hotel, 5+yr profitable business, FUND 600-749
- **Lowest-Tier** (3 pts): car wash, RV park, startup w/o CRE
- **Not Acceptable** (0, exclude): nursing home, assisted living, golf, cannabis

### Step 7 — Emit ranked prospect list
```json
{
  "scan_date": "2026-04-15",
  "listings_evaluated": 42,
  "hot": [{"url":"...","industry":"...","ask":850000,"sde":185000,"est_dscr":1.34,"tier":"Top","broker":{...},"est_commission":17000,"score":82}],
  "warm": [...],
  "fail": [...],
  "excluded": [{"url":"...","reason":"cannabis"}]
}
```

### Step 8 — Broker contact patterns (append, don't overwrite)
Maintain rolling table in `operations/broker_contacts.md` with confirmed / guessed / form-only status + last outreach date.

### Step 9 — Audit
Log: scan_date, queries run, listings visited, hot/warm/fail/excluded counts, dscr pre-screen fail count.

### Step 10 — Downstream handoff
Pass `hot + warm` to `rank_outreach_prospects` (optional) or directly to `draft_outbound_email` (one draft per listing, Keith approval required — never auto-send).

## Layer 5 — Output Schema
Ranked listings with URL, industry, asking price, SBA eligibility score, recommended outreach.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. |
