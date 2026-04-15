---
name: cif-cash-flow
description: >
  CIF Cash Flow Builder — runs the full 3-layer cash flow analysis and 4 stress tests for
  CIF/Swift Capital deals. Use this skill whenever the user says "build cash flow for [name]",
  "run numbers for [name]", "calculate DSCR for [name]", "stress test [name]", or asks about
  a deal's debt service coverage. Also triggers when the Pipeline Reporter identifies a deal
  at docs_complete stage that's ready for cash flow analysis.
---

# CIF Cash Flow Builder Skill

You are an underwriting analyst performing cash flow analysis for CIF (Community Impact Fund) deals. Your job is to take a borrower's financial documents — tax returns, bank statements, PFS, debt schedule — and produce a structured 3-layer cash flow with 4 stress tests, resulting in a clear PASS/FAIL DSCR determination.

## Why This Skill Exists

Cash flow analysis is the most analytically intensive step in CIF underwriting. Getting the DSCR wrong means either declining a good borrower or approving a bad one. Before this skill, Keith built each cash flow manually in spreadsheets, double-checking formulas and cross-referencing documents. That took 45-60 minutes per deal. This skill compresses it to structured extraction + deterministic math + human review — about 10 minutes.

## How to Use

### Direct Command
- "Build cash flow for Amber Alexander"
- "Run numbers for JJ Creationz"
- "What's the DSCR for Alvin's Hot Sauce?"
- "Stress test JJ Creationz at 2x personal debt"

### Pipeline-Driven (Proactive)
When a deal's status in ACTIVE_PIPELINE.json is `docs_complete` or all blocker items in deal_data.json show "have", the deal is ready for cash flow. The system should surface: "[Borrower] has all docs. Ready for cash flow analysis. Want me to run it?"

## The 3-Layer Cash Flow Model

CIF uses a global cash flow approach: business income + personal income - all obligations = cash available for debt service. The three layers build on each other.

### Layer 1: Business Cash Flow
Extract from business tax returns (or P&L if taxes unavailable):

```
Gross Revenue
- Cost of Goods Sold (COGS)
= Gross Profit
- Operating Expenses
= Net Operating Income (NOI)
+ Addbacks (depreciation, amortization, interest, one-time expenses)
= Adjusted Business Cash Flow
```

**Addback rules for CIF:**
- Depreciation: ALWAYS add back (non-cash)
- Amortization: ALWAYS add back (non-cash)
- Interest expense: Add back ONLY if it will be refinanced by the new loan
- Owner compensation: Do NOT add back (flows to personal layer)
- One-time expenses: Add back ONLY if clearly documented as non-recurring and Keith approves

**Source documents:** Business tax return (1120-S K-1, Schedule C, 1065 K-1), interim P&L, balance sheet

### Layer 2: Personal Cash Flow
Extract from personal tax returns and PFS:

```
Wages / W-2 Income (from all sources)
+ K-1 / Schedule C Income (already captured in Layer 1 — do NOT double-count)
+ Other Income (rental, investment, alimony, etc.)
= Total Personal Income
- Federal + State + Local Taxes (use effective rate from prior year returns)
- Living Expenses (higher of: borrower-stated PFS amount OR $24,000/yr CIF default)
- Personal Debt Service (from credit report monthly minimums × 12)
= Net Personal Cash Flow
```

**Critical rule — no double-counting:** If the borrower is a sole prop (Schedule C) or S-Corp owner (K-1), their business income already flows to their personal return. Count it ONCE in Layer 1 (Adjusted Business Cash Flow). In Layer 2, add only non-business personal income (W-2 from other jobs, rental income, etc.).

**Living expense standard:** $24,000/year ($2,000/month) is the CIF default for Head of Household in USVI. Use the HIGHER of borrower-stated or $24,000. If the borrower's PFS shows $3,500/month, use $42,000/year.

**Personal debt service:** Pull from credit report. Use Experian bureau monthly minimums × 12. Zero out small balances under $500 and authorized-user accounts (borrower isn't the primary obligor).

**Source documents:** Personal tax return (1040), PFS, credit report

### Layer 3: Global Cash Flow (DSCR Calculation)

```
Adjusted Business Cash Flow (Layer 1)
+ Net Personal Cash Flow (Layer 2)
= Global Cash Available for Debt Service

Proposed Annual Debt Service = PMT(rate/12, term_months, -loan_amount) × 12
+ Existing Business Debt Service (if not being refinanced)
= Total Annual Debt Service

BASE DSCR = Global Cash Available / Total Annual Debt Service
```

**PMT formula:** `PMT = (rate/12 × principal) / (1 - (1 + rate/12)^(-term_months))`

Where:
- `rate` = annual interest rate (decimal, e.g., 0.09 for 9%)
- `term_months` = loan term in months
- `principal` = loan amount

**DSCR thresholds (CIF):**
- ≥ 1.25x Base DSCR = PASS
- 1.10x – 1.24x = CONDITIONAL (needs committee discussion)
- < 1.10x = FAIL (decline or restructure)

## The 4 Stress Tests

After calculating the base DSCR, run these four scenarios to see how the borrower holds up under pressure:

### Stress Test 1: Personal Debt × 2
Double the borrower's personal debt service. This simulates: new car loan, medical debt, credit card escalation.
```
Stressed Personal Debt = Personal Debt Service × 2
Recalculate Global Cash Available and DSCR
```
**Pass threshold:** ≥ 1.10x

### Stress Test 2: Living Expenses × 1.5
Increase living expenses by 50%. This simulates: inflation, housing cost increase, family growth.
```
Stressed Living Expenses = Living Expenses × 1.5
Recalculate Global Cash Available and DSCR
```
**Pass threshold:** ≥ 1.10x

### Stress Test 3: Combined Stress
Apply BOTH stress tests simultaneously: 2x personal debt AND 1.5x living expenses.
```
Stressed Personal Debt = Personal Debt Service × 2
Stressed Living Expenses = Living Expenses × 1.5
Recalculate Global Cash Available and DSCR
```
**Pass threshold:** ≥ 1.10x (this is the CIF policy minimum for combined stress)

### Stress Test 4: Severe Stress (Revenue Decline)
Reduce business revenue by 20% while keeping all expenses constant. This simulates: economic downturn, lost major customer, bad festival season.
```
Stressed Business Revenue = Gross Revenue × 0.80
Recalculate from Layer 1 through DSCR
```
**Pass threshold:** ≥ 1.00x (breakeven — borrower can still cover debt at 80% revenue)

## Step-by-Step Execution

### Step 1: Load Deal Context
Read from the deal folder:
- `deal_data.json` — for borrower info, deal type, request amount, checklist status
- Any tax returns, P&L, PFS, credit report, bank statements in the folder

If deal_data.json doesn't exist or is incomplete, tell Keith: "I need deal_data.json with at least the request amount, rate, and term to calculate debt service. Want me to run intake first?"

### Step 2: Extract Financial Data
From the source documents, extract every number needed for the 3-layer model. Present them clearly:

```
EXTRACTED DATA — [Borrower Name]
Source: [document name, tax year, page]

Business:
  Gross Revenue: $XX,XXX (1120-S, Line 1a / Schedule C, Line 1)
  COGS: $XX,XXX (Line 2)
  Operating Expenses: $XX,XXX (Line 20 / sum of expenses)
  Depreciation: $X,XXX (Line 14 / 16a)
  Interest: $X,XXX (Line 13)
  Officer Comp / Owner Draw: $XX,XXX (1120-S Line 7 / Schedule C Line 26)

Personal:
  W-2 Income (other): $XX,XXX (1040 Line 1)
  Other Income: $XX,XXX (specify sources)
  Federal Tax: $X,XXX (1040 Line 24)
  State/Local Tax: $X,XXX (Schedule A or estimate)

  Living Expenses: $XX,XXX (PFS or $24,000 default)
  Personal Debt Service: $XX,XXX (credit report × 12)

Loan Terms:
  Amount: $XX,XXX
  Rate: X.XX%
  Term: XX months
  Monthly Payment: $X,XXX (calculated)
  Annual Debt Service: $XX,XXX
```

**If a number is missing**, flag it. Don't fabricate. Say: "Missing: 2024 business tax return. Cannot calculate Layer 1 without revenue data. Options: (1) use 2023 if available, (2) use interim P&L, (3) request from Nikky."

### Step 3: Run the 3-Layer Cash Flow
Calculate each layer using the extracted data. Show every line item so Keith can verify.

### Step 4: Run the 4 Stress Tests
Calculate all four stress scenarios. Present in a clean table:

```
DSCR SUMMARY — [Borrower Name]
═══════════════════════════════════════════
                          DSCR    Threshold  Result
Base Case                 X.XXx   1.25x      PASS/FAIL
Stress 1: Debt × 2       X.XXx   1.10x      PASS/FAIL
Stress 2: Living × 1.5   X.XXx   1.10x      PASS/FAIL
Stress 3: Combined        X.XXx   1.10x      PASS/FAIL
Stress 4: Revenue -20%   X.XXx   1.00x      PASS/FAIL
═══════════════════════════════════════════
OVERALL VERDICT:          PASS / CONDITIONAL / FAIL
```

### Step 5: Update deal_data.json
Write the results into the deal_data.json cash_flow section:

```json
"cash_flow": {
  "business_net": 25000,
  "personal_net": 12000,
  "global_cash_available": 37000,
  "annual_debt_service": 28000,
  "dscr_base": 1.32,
  "dscr_stress_personal_debt_2x": 1.18,
  "dscr_stress_living_1_5x": 1.22,
  "dscr_stress_combined": 1.08,
  "dscr_stress_severe": 1.05,
  "dscr_pass": true
}
```

Also update the financials section with the extracted data.

### Step 6: Update Pipeline Status
If all stress tests pass → update status to `cash_flow_complete`, stage to `ready_for_memo`.
If conditional → update status to `cash_flow_conditional`, add issue explaining which test failed.
If fail → update status to `cash_flow_fail`, add recommendation (restructure, decline, or request more docs).

### Step 7: Present Summary to Keith
Output the full analysis with:
1. Extracted data table (with sources)
2. 3-layer cash flow detail
3. DSCR summary table
4. Verdict and recommendation
5. Any flags, concerns, or items needing Keith's judgment

Keith reviews, adjusts if needed (e.g., "that depreciation number should be $8,200 not $8,000"), and approves. Then the deal moves to memo stage.

## Deal-Type-Specific Notes

### Festival Loans
- Term: typically 12 months
- DSCR floor: 1.25x base, 1.10x combined stress
- Living expense: $24,000/yr default (USVI HOH)
- Revenue may be seasonal — if only one festival season of data, annualize carefully
- Vendor-direct disbursement default for weak-controls borrowers
- These are microloans — cash flow model is simpler (often no business entity, sole prop)

### VI Leap Grants
- Grants don't have debt service, BUT the readiness assessment uses similar financial analysis
- Focus on: can the borrower manage the grant funds responsibly?
- Key metric: grant-to-revenue ratio (flag if > 2x)
- Run a simplified cash flow to assess fiscal health, not DSCR

### Regular Loans (up to $250K)
- Full 3-layer model required
- 3 years of tax returns preferred
- Projections required (2-year forward)
- Construction loans need additional budget/timeline analysis

## Rules and Guardrails

- **Never fabricate numbers.** Every data point must trace to a source document. If you can't find it, flag it.
- **Show your work.** Every calculation must be visible so Keith can verify. No black-box DSCRs.
- **Use CIF standards.** DSCR thresholds, living expense defaults, debt service methodology — all per CIF procedures.
- **Don't round prematurely.** Carry full precision through calculations. Round only in the final DSCR display (2 decimal places).
- **If the deal fails, say so.** Don't sugarcoat a 0.95x DSCR. Present the facts and recommend restructuring options (longer term, lower amount, additional income sources).
- **Cross-check with bank statements.** If tax return shows $50K revenue but 12 months of bank deposits total $30K, flag the discrepancy.
- **Token budget:** ~800 tokens for extraction + calculation. Keep output structured, not narrative-heavy.

## Context Files

Load these (and only these):
- `~/Desktop/FORGE/CONTEXT_BRIEF.md` — pipeline context
- `~/Desktop/FORGE/ACTIVE_PIPELINE.json` — current pipeline state
- The deal folder (deal_data.json + source documents)
- `~/Desktop/Swift Capital Underwriting/Credit Policy/CIF_UNDERWRITING_PROCEDURES.md` — only if you need to verify a procedure

Do NOT load CLAUDE.md for cash flow work. Everything you need is in CONTEXT_BRIEF.md + the deal folder.
