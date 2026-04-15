# Day 3 Learnings — Advanced Integrated Pain Training Package

Analysis of the 7 documents dropped in `UNDERWRITING_V1_START_HERE/Advanced_Integrated_Pain_V1_Training/analysis/`.

## Documents received
| # | Document | Type | Notes |
|---|---|---|---|
| 1 | Tax Return 2024 — Advanced Integrated Pain LLC | Form 1120-S | Native PDF, text-extractable |
| 2 | Tax Return 2025 — Advanced Integrated Pain LLC | Form 1120-S | Password-protected (23351), decrypted |
| 3 | Joint Tax Return 2024 — Narendren & Ava | Form 1040 | Native PDF |
| 4 | Joint Tax Return 2025 — Narendren & Ava | Form 1040 | Password-protected (23351), decrypted |
| 5 | Credit Report — Narendren Narayanasamy | Merchants Credit Bureau tri-merge | Native PDF |
| 6 | Personal Financial Statement — SBA Form 413 | SBA form | Native PDF |
| 7 | Interim P&L — AIPSS through 10/31/2025 | QuickBooks export | Native PDF |

**Missing from package:** 2023 business 1120-S, 2023 personal 1040, 3 months of business bank statements, debt schedule (for business), interim balance sheet.

## Extraction engineering findings

### All 7 documents are native (text-based) PDFs
`pdftotext -layout` pulls every value cleanly. **Claude vision fallback is NOT needed for this document set.** If every deal you pull from CIF / SBA lenders comes in this format, extraction can be 100% deterministic regex over text, which is cheaper, faster, and auditable. Vision only needs to activate when a page returns no text (scanned image PDFs).

### Finding #1 — G8WAY pulls Net Income from Schedule M-1 Line 1, NOT Form 1120-S Line 22
This is the single most important discovery of the day.

| Year | 1120-S Line 22 (Ordinary Biz Income) | Schedule M-1 Line 1 (Net Income per Books) | G8WAY used |
|---|---|---|---|
| 2024 | $67,653 | **$68,721** | $68,721 |
| 2025 | $69,227 | **$67,541** | $67,541 |

If I built the extractor to pull Line 22 (the obvious candidate), every DSCR would be wrong. The spread hits Line 22 first as a fallback, but the canonical value is **Schedule M-1 Line 1 ("Net income (loss) per books")** when Schedule M-1 is filed. M-1 reconciles book income to taxable income — it's the truer picture of cash-basis earnings. For 2024 the diff is +$1,068 (book > taxable, likely depreciation timing), for 2025 the diff is −$1,686 (book < taxable, likely non-deductible meals).

**Extractor rule:** pull M-1 Line 1 as primary; fall back to Line 22 only if M-1 is not filed (small S-corps under $250K receipts can omit M-1).

### Finding #2 — Depreciation does not come from Line 14
1120-S Line 14 shows: 2024 = $27, 2025 = $16. G8WAY shows D&A = $169 (2024) and $158 (2025). The G8WAY number is ~6× Line 14.

Line 14 only captures depreciation "not claimed on Form 1125-A or elsewhere." The rest is buried in Form 4562 (Section 179, MACRS, other depreciation) and may flow through COGS on Form 1125-A. The true total depreciation = sum of Form 4562 Part II Line 14 + Part III Line 17 + Part IV Line 21, plus any Form 1125-A depreciation.

**Extractor rule:** read Form 4562 directly, sum the authoritative totals. Do not trust 1120-S Line 14 alone. For this deal the numbers are small enough that the error wouldn't change a decision, but on a $1.7M deal with real depreciation this rule matters.

### Finding #3 — Interim P&L does not reconcile to the full-year tax return
QuickBooks interim Jan–Oct 2025: Revenue $180,696, Net Income $115,279.
Filed 2025 full-year 1120-S: Revenue $213,145, Line 22 $69,227, M-1 Line 1 $67,541.

The interim overstates net income by ~$48K because year-end CPA adjustments (accrued payroll tax, owner compensation, depreciation, owner tax distributions) are not yet booked. **Never trust interim NI as-is** — it needs to be discounted by expected year-end adjustments, or thrown out entirely when the filed return covers the same period.

**Engine implication:** if a fixture contains both an interim and a filed return covering the same year, the filed return wins. Interim only contributes when it adds periods not covered by any filed return.

### Finding #4 — PFS under-reports personal debt service by ~60%
This is the cross-reference you flagged. The data confirms your instinct.

**PFS Form 413 shows:**
- Notes Payable monthly payment: **$2,528**
- Mortgage balance: $291,628

**Credit report tri-merge shows:**
- Mortgage: $285,500 balance / $2,566/mo
- SoFi personal loan: $61,049 / $1,774/mo
- CBNA installment: $13,845 / $754/mo
- BofA auto: $12,966 / $391/mo
- Multiple revolving accounts (BofA, Citi, Target, AMEX): ~$28,460 total balance, ~$797/mo minimum payments
- **Total monthly debt service: $6,282/mo ($75,384/yr)**

**Gap: PFS captured roughly the SoFi payment ($2,528 ≈ $1,774 SoFi + misc).** The borrower (or whoever filled out the form) understated personal debt by approximately **$3,754/mo = $45,048/yr**. That's the exact reason you cross-reference.

**Engine rule:** in Global DSCR, use `personal_debt_service = max(PFS_notes_payable, credit_report_total_monthly_minimums × 12)`. Credit report total minimum payments is usually the more accurate floor. Record the delta as a risk flag on the deal.

### Finding #5 — Cash/liquidity needs bank statement verification
PFS claims: Cash $75,113 + Savings $10,368 = **$85,481 liquid in banks.**

No bank statements in the package. Per your rule, this value is **unverified** and must be adjusted down (or confirmed) against 3 months of business + personal bank statements. The engine should treat PFS cash as a *claim*, not a fact, until statements land.

**Engine rule:** tag PFS cash and savings with `verification_status: unverified` until bank statements are extracted and cross-checked. Liquidity ratio calculation uses the verified value if present, falls back to PFS with a warning flag.

### Finding #6 — Credit strength confirmed
- **Equifax FICO Classic V9: 782** (excellent)
- TransUnion and Experian scores present in the full credit report (not surfaced by my quick grep — need to extract them too)
- Credit report mentions reason codes: "Ratio of balance to limit on bank revolving or other rev accts too high" and "Amount owed on revolving accounts is too high" — but at 782 these are advisory, not disqualifying
- Revolving utilization: 32% ($28,460 balance / $90,200 limit)
- Total debt/high credit ratio: 67%

Narendren's FICO 782 puts this deal comfortably above Colony Bank's 675 minimum and any CDFI floor. Credit is a strength, not a risk.

## Cross-reference-adjusted PFS

This is what the *real* PFS looks like after the engine applies the adjustments:

| Line | PFS as filed | Adjusted | Source of adjustment |
|---|---|---|---|
| Cash on hand + savings | $85,481 | **TBD — needs bank statements** | Verify via 3-month statements |
| IRA/Retirement | $264,549 | $264,549 | No change (excluded from SBA liquidity anyway) |
| Life insurance CSV | $43,573 | $43,573 | No change |
| Stocks and bonds | $10,022 | $10,022 | No change |
| Real estate | $860,000 | $860,000 | Needs Zillow/appraisal spot-check if primary residence |
| **Liquid assets (SBA definition)** | **$139,076** | **TBD** | = Cash + Savings + Stocks + LI CSV, excl. retirement & RE |
| Mortgage balance | $291,628 | $285,500 | Credit report (more recent) |
| Notes payable balance | Unknown | $87,860 | SoFi $61,049 + CBNA $13,845 + Auto $12,966 |
| Revolving balance | Not listed | $28,460 | Credit report |
| **Total liabilities** | $407,342 | $401,820 | Credit report total |
| Monthly debt service | $2,528 | **$6,282** | Credit report total minimums (+$3,754/mo) |
| Annual debt service | $30,336 | **$75,384** | × 12 |

## What this means for the V1 engine build

1. **The extractor is simpler than I expected** — pdftotext handles the full package. Vision API is a day-30 concern, not a day-3 concern.

2. **The extractor is harder than I expected in one specific way** — it needs form-aware logic, not just regex. Schedule M-1 Line 1 vs Line 22 is a rule the code must know. Form 4562 totals vs Line 14 is a rule. Credit report total minimums vs PFS notes payable is a rule.

3. **The cross-reference layer is its own phase.** Raw extraction → per-document schema → cross-reference reconciliation → canonical deal record. The reconciliation step applies Keith's rules:
   - Cash/liquidity = min(PFS, bank statement verified)
   - Personal debt service = max(PFS, credit report minimums × 12)
   - Mortgage balance = most recent of (PFS, credit report, bank 1098)
   - Business revenue/NI = filed return if interim overlaps

4. **Missing from the package** — I still need, in priority order:
   - 2023 business 1120-S (to complete the 3-year spread)
   - 3 months of business bank statements (to verify cash + cross-check revenue)
   - Business debt schedule (to build post-close ADS independently of the G8WAY's number)
   - 2023 personal 1040
   - The actual seller note document ($6,344.16/yr line item in G8WAY)

## Next actions

1. Build `underwriteos/extract/tax_return_1120s.py` with the Finding #1 and Finding #2 rules baked in
2. Build `underwriteos/extract/tax_return_1040.py` — simpler, pulls AGI, wages, K-1 flow-through
3. Build `underwriteos/extract/credit_report.py` — tri-merge parser, returns all three scores + debt totals
4. Build `underwriteos/extract/pfs_form_413.py` — SBA Form 413 field extraction
5. Build `underwriteos/reconcile.py` — cross-reference layer applying the rules above
6. Test the whole stack against this deal, confirm the engine produces 1.23x/1.25x from extracted (not fixtured) data
