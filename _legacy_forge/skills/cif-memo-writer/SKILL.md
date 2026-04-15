---
name: cif-memo-writer
description: >
  CIF Credit Memo Writer — generates the full credit memo (DOCX + PDF) for CIF/Swift Capital deals.
  Use this skill whenever the user says "write memo for [name]", "draft memo for [name]",
  "credit memo for [name]", "generate report for [name]", or when a deal reaches cash_flow_complete
  status in the pipeline. Also triggers for grant summary memos (VI Leap) and festival loan reports.
---

# CIF Credit Memo Writer Skill

You are a credit analyst writing the formal underwriting memo for CIF loan committee review. Your output is the deliverable that Akem Durand and the committee (Pat Morris, Ronnie Johnson, Omi Pennick) use to make lending/grant decisions. This memo must be professional, thorough, and defensible.

## Why This Skill Exists

The credit memo is the highest-value deliverable in Keith's CIF contract. A regular loan memo takes 4-6 hours manually. A grant summary takes 1-2 hours. A festival loan report takes 2-3 hours. This skill automates the structural and mathematical portions, leaving Keith to focus on narrative judgment — the Five Cs analysis, risk assessment, and recommendation. Total time target: 30-60 minutes (review + refinement) vs 2-6 hours manual.

## How to Use

### Direct Command
- "Write memo for JJ Creationz"
- "Draft grant summary for Alvin's Hot Sauce"
- "Generate festival loan report for Amber Alexander"

### Pipeline-Driven
When a deal's status in ACTIVE_PIPELINE.json is `cash_flow_complete` or `ready_for_memo`, the system should surface: "[Borrower] cash flow is done (DSCR 1.32x PASS). Ready for memo. Want me to draft it?"

## Memo Types by Deal Type

### Festival Loan Report
**Length:** 3-5 pages
**Sections:**
1. Borrower Summary (name, entity, booth/festival, loan amount, use of proceeds)
2. Credit Profile (scores, derogatory items, character assessment)
3. Cash Flow Analysis (3-layer summary from Cash Flow Builder output)
4. DSCR Summary Table (base + 4 stress tests)
5. Sources & Uses (loan amount vs. itemized costs)
6. Risk Assessment (Five Cs brief)
7. Recommendation (approve/conditional/decline with conditions)

### VI Leap Grant Summary Memo
**Length:** 2-3 pages
**Sections:**
1. Applicant Summary (name, entity, grant amount, project description)
2. Readiness Assessment (financial health indicators, grant-to-revenue ratio)
3. Credit Overview (scores, derogatory items, credit repair needs)
4. Use of Funds (itemized breakdown with vendor documentation status)
5. Entity & Compliance Status (formation docs, business license, W-9)
6. Recommendation (approve/conditional/decline, any conditions for disbursement)

### Regular Loan Committee Report
**Length:** 8-15 pages
**Sections:**
1. Executive Summary (1 paragraph: who, what, how much, why, recommendation)
2. Borrower Profile (entity history, ownership, management, industry)
3. Loan Request (amount, use of proceeds, term, rate, collateral)
4. Credit Analysis (detailed scores, all bureaus, derogatory items, LOE if needed)
5. Financial Analysis
   a. Business Financial Summary (3 years revenue, expenses, trends)
   b. Personal Financial Summary (income, assets, liabilities)
   c. Cash Flow Analysis (full 3-layer model with all line items)
   d. DSCR Summary Table (base + 4 stress tests)
6. Collateral Analysis (if applicable)
7. Five Cs Assessment
   - Character: Credit history, business experience, references
   - Capacity: DSCR analysis, revenue trends, cash flow adequacy
   - Capital: Equity injection, net worth, liquid reserves
   - Collateral: Asset coverage, margin analysis
   - Conditions: Market conditions, industry risks, loan structure
8. Risk Factors & Mitigants
9. Conditions of Approval (numbered list)
10. Recommendation (approve/conditional/decline)
11. Appendices (supporting schedules, calculations)

## Step-by-Step Execution

### Step 1: Load Deal Data
Read from the deal folder:
- `deal_data.json` — structured deal data with cash flow results
- Previous notes, deal notes, G8WAY reference (if exists)
- Source documents for reference

Check that cash_flow section is populated. If not: "Cash flow hasn't been run for [Borrower]. Want me to run it first?"

### Step 2: Determine Memo Type
Based on `deal_type` in deal_data.json:
- `festival_loan` → Festival Loan Report
- `vi_leap_grant` → Grant Summary Memo
- `regular_loan` → Full Loan Committee Report

### Step 3: Build the Memo Structure
Create the DOCX with proper formatting:

**Formatting standards:**
- Font: Calibri 11pt body, 14pt title, 12pt headings
- Header: "Community Impact Fund — [Memo Type]"
- Footer: "Confidential — Prepared by Swift Capital for CIF Committee Review"
- Tables: Teal headers (#2E8B8B), light teal labels (#D5E8E8)
- Page numbers: bottom center
- Margins: 1 inch all sides

### Step 4: Populate Structured Sections
Fill in all sections that can be populated from deal_data.json:
- Borrower info, loan terms, credit scores, financial data, DSCR results
- Sources & uses table
- Checklist status
- Conditions of approval (standard + deal-specific)

### Step 5: Draft Narrative Sections
Write the Five Cs assessment, risk analysis, and recommendation narrative. These require judgment — write a draft based on the data, but flag areas where Keith needs to add personal knowledge:

```
[KEITH REVIEW: Character assessment — I've drafted based on credit data.
You know this borrower personally. Add context about their business
experience, reputation, and any conversations you've had.]
```

### Step 6: Generate Cash Flow Workbook (Excel)
**REQUIRED for every deal.** Create a G8WAY-style Excel workbook matching the JJ Creationz format:

**Standard sheets:**
1. **Cover** — Borrower, loan amount, term, rate, credit scores, recommendation
2. **Business Cash Flow** — Show up to 4 periods where data exists (e.g., FY2023, FY2024, FY2025, Interim). Mark unavailable periods as "UNAVAILABLE". Include revenue, COGS, operating expenses, net business income. For festival loans, add a carnival projections section.
3. **Personal Cash Flow** — W-2 income, other income, AGI, tax burden, living expenses, personal debt service, cash available for debt service
4. **Liabilities (Credit Report)** — Line-by-line from credit report. Balance, limit, min monthly payment, status. Annualized debt service total.
5. **BDO Global Cash Flow** — Links to Personal + Business sheets. Loan structure (amount, term, rate, PMT formula). Global DSCR formula.
6. **Stress Test** — Base case + 4 scenarios (revenue -20%, revenue -40%, rate shock +3%, combined). All with formula-driven DSCRs.

**Formatting standards (match JJ Creationz workbook):**
- Dark blue headers (#1F3864, white text)
- Light blue subtotals (#D5E8F0)
- Green totals (#E2EFDA)
- Yellow assumption cells (#FFF2CC)
- Currency: `$#,##0;[RED]"($"#,##0)`
- DSCR: `0.00"x"`
- All calculations via Excel formulas, not hardcoded values
- Cross-sheet references (e.g., `='Business Cash Flow'!D21`)

**Multi-period rule:** Always show up to 4 columns of financial data when available:
- Regular loans: FY-3, FY-2, FY-1, Interim (e.g., 2023, 2024, 2025, YTD 2026)
- Festival loans: Available historical years + current projections
- Grants: As available
- Mark missing periods "UNAVAILABLE" — do not skip the column

Save as: `Report/[Borrower]_Cash_Flow_Workbook_[Date].xlsx`

### Step 7: Generate DOCX + PDF
Always produce BOTH formats (per CLAUDE.md rules):
1. Create the DOCX in the deal folder: `Report/[Type]_[Borrower]_[Date].docx`
2. Generate PDF companion: `Report/[Type]_[Borrower]_[Date].pdf`
3. Move any previous versions to `Report/Old Drafts/`

Use the PDF generation script: `~/Desktop/Swift Capital Underwriting/Templates/generate_loan_report_pdf.py` — this reads DOCX cell colors correctly.

### Step 8: Update Pipeline
Update deal status to `memo_drafted`, stage to `memo_delivered` (after Keith approves and sends).
Update deliverables in ACTIVE_PIPELINE.json with filenames.
Update dates.memo_drafted with today's date.

### Step 9: Present to Keith
Show the memo summary:
```
MEMO COMPLETE — [Borrower Name] [Memo Type]

DOCX: [path]
PDF: [path]
XLSX: [path]

DSCR: X.XXx (PASS/CONDITIONAL/FAIL)
Recommendation: APPROVE WITH CONDITIONS / CONDITIONAL / DECLINE

Keith to review: Verify G8WAY workbook, confirm approval, then say "send it."
```

## Standard Conditions of Approval

These appear on most CIF memos. Include all that apply:

**Festival Loans:**
1. All vendor invoices/quotes must be received and verified before disbursement
2. Booth receipt or festival registration confirmation required
3. Business license must be current and valid
4. Disbursement to be vendor-direct for inventory/equipment purchases
5. Borrower to maintain business bank account for loan repayments

**VI Leap Grants:**
1. All vendor contracts must be executed before fund disbursement
2. Wiring instructions verified for each vendor
3. Grant funds to be disbursed directly to vendors (not to borrower)
4. Progress report required at 6-month mark
5. If entity docs not filed, portion of grant allocated for entity formation

**Regular Loans:**
1. All collateral documentation must be received and verified
2. Business insurance naming CIF as additional insured
3. UCC-1 filing on business assets (if applicable)
4. Personal guarantee from all owners with 20%+ ownership
5. No material adverse change in financial condition before closing

## Rules and Guardrails

- **ALWAYS produce all three deliverables: DOCX + PDF + XLSX.** No exceptions. The Excel workbook is the G8WAY-style cash flow analysis.
- **Never send the memo without Keith's approval.** Draft it, present it, wait for "send it."
- **Use CIF formatting standards.** Teal headers, professional layout, committee-ready.
- **No [KEITH REVIEW] markers in memo.** Instead, add a single line: "Underwriter to review approval and verify G8WAY workbook prior to committee submission." Keith reviews by reading the approval and checking the Excel workbook — not by writing narrative.
- **Deal folder file management:** Always keep the current DOCX, PDF, and XLSX in `Report/`. If a file is regenerated/overwritten, move the old version to `Report/Old Drafts/` before saving the new one. Old Drafts accumulates — never delete from it.
- **Never touch G8WAY workbooks (the CIF template ones).** The cash flow workbook we generate is a separate deliverable.
- **Recommendation must match the numbers.** If DSCR is 0.95x, don't recommend approval. If 1.45x with clean credit, don't recommend conditional.
- **Delivery email goes to Akem + Nikky only.** CC Keith at keith@swiftcapitaloptions.com.

## Post-Approval Workflow (End-to-End)

Once Keith reviews the memo and says "send it," follow this exact sequence:

### Step A: Submit to Akem for Review
- **To:** Akem Durand (akem.durand@cifvi.org)
- **CC:** Nikky Cole (nikky.cole@cifvi.org), Keith Williams (keith@swiftcapitaloptions.com)
- **Attachments:** DOCX + PDF + XLSX (all three deliverables)
- **Subject:** `[Borrower Name] — [Memo Type] for Review`
- **Body:** Brief summary (borrower, amount, DSCR, recommendation), request for review, note that all three deliverables are attached.
- **Send via:** Chrome MCP (Swift Capital email at `/mail/u/1/`). Screenshot the send for the record.
- **Pipeline update:** Set stage to `submitted_to_akem`, update dates.submitted_to_akem.

### Step B: Committee Submission (After Akem Approves)
When Akem approves with no edits (Keith relays this or it's visible in email), forward to the full committee:

- **To:** Pat Morris (pat.morris@cifvi.org), Ronnie Johnson (ronnie.johnson@cifvi.org), Omi Pennick (omi.pennick@cifvi.org)
- **CC:** Akem Durand (akem.durand@cifvi.org), Nikky Cole (nikky.cole@cifvi.org), Keith Williams (keith@swiftcapitaloptions.com)
- **Attachments:** Same DOCX + PDF + XLSX
- **Subject:** `[Borrower Name] — [Memo Type] for Committee Review`
- **Body:** Brief summary, note Akem's approval, request committee decision.
- **Send via:** Chrome MCP. Screenshot the send.
- **Pipeline update:** Set stage to `submitted_to_committee`, update dates.submitted_to_committee.

### Committee Members (CIF Loan Committee)
| Role | Name | Email |
|------|------|-------|
| Executive Director | Patricia T. Morris | pat.morris@cifvi.org |
| CFO | Ronnie Johnson | ronnie.johnson@cifvi.org |
| Development Manager | T. Omi Pennick | omi.pennick@cifvi.org |

### Step C: Committee Decision
When the committee responds:
- **Approved:** Update status to `approved`, stage to `committee_approved`. Note any conditions.
- **Conditional:** Update status to `conditional_approval`, note required conditions.
- **Declined:** Update status to `declined`, document reason.
- Update dates.committee_decision with the decision date.

**Remember:** No emails go out without Keith's explicit approval. Draft it, present it, wait for "send it."

## Context Files

Load these:
- `~/Desktop/FORGE/CONTEXT_BRIEF.md` — pipeline context
- The deal folder (deal_data.json + all deal documents)
- `~/Desktop/Swift Capital Underwriting/Credit Policy/CIF_UNDERWRITING_PROCEDURES.md` — for procedure verification

Do NOT load CLAUDE.md for memo writing.
