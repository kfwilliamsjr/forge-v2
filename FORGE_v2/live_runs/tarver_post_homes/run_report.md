# Tarver / Post Homes — Live System Run
*Run date: 2026-04-15 | Policy version: 1.0.0 | Lane: sba_broker*

End-to-end pass through FORGE v2. Every skill output below is deterministic or traceable to a policy YAML citation.

---

## Step 1 — `extract_sba_deal_parameters`

| Field | Value | Source |
|---|---|---|
| industry_label | `sober_living_recovery_housing` | borrower disclosure |
| NAICS | 623220 | inferred |
| deal_type | expansion + working_capital | UOP |
| loan_amount_range | $350K–$600K | intake |
| recommended_ask | **$450K** | harness sizing (payer-mix risk) |
| prohibited_industry | **false** (SOP 50-10 does not list sober living) | `sba_sop_50_10.yaml → ineligible_businesses` |
| colony_employment_conflict | **TRUE** | `broker_rules.yaml` — Keith is W-2 Colony SBSL |

**Verdict:** proceed on broker lane, Colony excluded.

---

## Step 2 — `score_inbound_leads` (100-pt model)

Policy: `lead_scoring.yaml`.

| Category | Pts | Rationale |
|---|---|---|
| Deal fit: loan size $450K (sweet spot) | +15 | within $350K–$5M |
| Industry: specialty healthcare (watch list, not top/prohibited) | +3 | non-top, non-prohibited |
| Deal type: expansion | +7 | |
| Credit 700+ (self-reported, unverified) | +8 | acceptable band |
| Equity injection: $350K already in (>15% of ask) | +10 | strong |
| Industry experience: unverified | 0 | |
| Engagement: form partial + warm referral (Healthy Connections verbal) | +8 | +3 partial +5 warm |
| Revenue potential: real_estate service level, $9K est commission | +7 | |
| **TOTAL** | **58** | **Tier 3 (nurture) trending Tier 2 once credit/payer mix verified** |

**Verdict:** Tier 3 now; Tier 2 after credit pull + payer mix doc. Action: keep in active pipeline, request docs this week.

---

## Step 3 — `screen_sba_character_loe_needed`

Policy: `sba_sop_50_10.yaml → character_triggers`.

- Bankruptcy last 7yr: **unknown** → must verify on tri-merge + Form 912
- Felony: **unknown** → Form 912 required for any 20%+ owner
- Tax liens unsatisfied: **unknown** → credit report + IRS check
- CAIVRS: **required** (all SBA-backed)
- LOE: **conditional** — fires only if credit pull reveals disclosed items

**Output:**
```json
{"status": "ok", "loe_required": null, "form_912_required": true, "caivrs_required": true, "blocker": false, "halt_until_credit_pulled": true}
```

---

## Step 4 — `calculate_broker_commission`

Policy: `broker_rules.yaml`.

- Service level: `real_estate` (CRE-secured sober living)
- Rate: **2.0%**
- Range: $350K × 2% = **$7,000** → $600K × 2% = **$12,000** (recommended $450K = $9,000)
- Form 159: **required** (SBA-backed)
- Paid by: **borrower** (separate engagement letter)
- Any lender referral fee on top: additive

---

## Step 5 — `calculate_business_cash_flow` + `calculate_global_cash_flow`

**Engine:** `underwriteos.cashflow` (Decimal-precise, deterministic). Called via `skills/calculate_business_cash_flow/underwriteos_adapter.py`. LLM does not touch DSCR math — hard rule.

**Inputs (locked sizing):**
- Loan: **$350,000**, 120 months, 11.5% variable
- Annual DS: **$59,050.08** (Decimal amortization from engine)
- Shocked DS @ +300bps (14.5%): **$66,480.48**
- Personal living: $36,000/yr (KS, above USVI $24K floor)
- VA disability grossed-up 1.25x: $110K → **$137,500** personal income equivalent
- Personal DS: $12,000/yr | Liquid assets: $0 (not yet documented)

Source payloads + raw engine output: `uwos_runs/{low_case,high_case}.{json,out.json}`

### Scenario A — Low Revenue Case ($126K revenue, private-pay only)

Opex assumption: $94,500 (25% NI margin heuristic). Still heuristic — replaceable once borrower plan lands.

| Metric | Engine Output | Threshold | Verdict |
|---|---|---|---|
| BANI | $31,500.00 | | |
| Borrower DSCR | **0.53x** | 1.25x | **FAIL** |
| Global DSCR | **1.58x** | 1.10x | **PASS** (carried by VA) |
| Rate-shock Borrower DSCR | **0.47x** | 1.00x | **FAIL** |
| Liquidity ratio | 0.00 | n/a | pending liquid-asset doc |

### Scenario B — High Revenue Case ($345.6K, insurance/grant payer mix)

Opex assumption: $172,800 (50% NI margin heuristic).

| Metric | Engine Output | Threshold | Verdict |
|---|---|---|---|
| BANI | $172,800.00 | | |
| Borrower DSCR | **2.93x** | 1.25x | **PASS** |
| Global DSCR | **2.90x** | 1.10x | **PASS** |
| Rate-shock Borrower DSCR | **2.60x** | 1.00x | **PASS** |

### Verdict

**Business DSCR is binary on payer mix.** Low case (private-pay only) fails borrower DSCR and fails rate-shock. High case (insurance/grant contracts) clears every threshold with room. Global DSCR passes in both scenarios — VA disability income ($137.5K grossed-up) carries the deal when business cash flow is thin.

**Two gaps still estimate-grade, not engine-grade:**
1. Opex margins (50%/25%) are industry heuristics, not borrower's operating plan
2. Revenue cases themselves are borrower-projected, not historical — no operating history exists

---

## Step 6 — `match_colony_grid`

**HALT — colony_employment_conflict.** Not evaluated. Routing to alternate lenders per `lender_profiles.yaml`.

---

## Step 7 — Lender shortlist (Colony excluded)

From `lender_profiles.yaml` matched against deal profile (specialty healthcare, startup-adjacent, CRE-secured, $450K):

| Rank | Lender | Why | Expected Path |
|---|---|---|---|
| 1 | **Live Oak Bank** | Healthcare vertical, projection-based cash flow comfort | Primary submission |
| 2 | **Newtek Bank** | Aggressive national, startup-friendly | Parallel if Live Oak declines |
| 3 | **Celtic Bank** | Flexible on specialty | Tertiary |
| 4 | **Readycap Lending** | Non-bank, specialty-comfortable | Fallback |

---

## Step 8 — Blockers before lender submission

1. Entity name verified on KS SOS
2. Tri-merge credit pulled (not self-report)
3. Payer mix documented (insurance contracts, grant agreements, or court-referral pipeline)
4. Healthy Connections → written referral agreement
5. Licensing timeline confirmed (KS sober-living authority)
6. C of O confirms residential use (church-to-residential conversion)
7. VA award letter (rating pct + permanence)
8. Equity injection seasoning — 2 months bank statements showing the $350K
9. Form 912 (all 20%+ owners)
10. CAIVRS clear

---

## Step 9 — Deliverables produced by this run

- `deal_data.json` — canonical structured record
- `run_report.md` — this file
- Next action: `draft_outbound_email` (SBA account) with doc request list + engagement letter attached. **Draft only — Keith approves before send.**

---

## Policy citations (audit trail)

- `broker_rules.yaml` — commission rate, Form 159, Colony exclusion
- `lead_scoring.yaml → inbound_lead_scoring` — 58-pt score derivation
- `sba_sop_50_10.yaml → character_triggers` — Form 912 / CAIVRS / LOE logic
- `sba_sop_50_10.yaml → equity_injection` — $350K seasoning requirement
- `lender_profiles.yaml` — 4-lender shortlist ranking
- `cif_procedures.yaml` — NOT invoked (wrong lane)

---

## Honest gaps in this run

1. ~~Cash-flow math is estimate-grade.~~ **CLOSED 2026-04-15.** `underwriteos.cashflow` is wired via `underwriteos_adapter.py`. Amortization + DSCR + rate shock are Decimal-precise.
2. **Opex margin (50% / 25%) is a heuristic.** Still needs borrower operating plan to replace.
3. **Credit is self-reported 700+.** No tri-merge yet.
4. **Payer mix is the whole deal.** If the $1,920/bed rate isn't contracted, the deal collapses to the low case — which fails borrower DSCR (0.53x) and fails rate shock (0.47x). Global DSCR still passes because of VA income, but no SBA lender underwrites a borrower DSCR of 0.53x on projections alone. **This is a payer-mix documentation deal, not a credit deal.**
