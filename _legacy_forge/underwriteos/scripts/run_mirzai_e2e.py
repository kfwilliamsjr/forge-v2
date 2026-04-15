#!/usr/bin/env python3
"""
End-to-end Mirzai Group LLC demo run.

Walks a real deal bundle through:
    1. Extractors (1120-S seller, IRS transcript principal)
    2. deal_type.detect_deal_type()
    3. reconcile.reconcile()
    4. Narrative stubs (no LLM — uses a deterministic stub)
    5. memo.render_memo() → draft .docx

Writes artifacts to /sessions/hopeful-admiring-turing/mnt/FORGE/out/.
Nothing here commits PII — the output doc IS the deal memo, treat
accordingly.
"""
from __future__ import annotations

import json
from pathlib import Path

from underwriteos.extract.tax_return_1120s import extract_1120s
from underwriteos.extract.irs_transcript_1040 import (
    extract_irs_transcript_1040,
    is_irs_transcript,
)
from underwriteos.deal_type import detect_deal_type
from underwriteos.reconcile import DealBundle, DocItem, reconcile
from underwriteos.memo import DealContext, render_memo, missing_required_sections
from underwriteos.memo import narrative as nar


DEAL_ROOT = Path(
    "/sessions/hopeful-admiring-turing/mnt/UNDERWRITING_V1_START_HERE/Mirzai Group/2of2"
)
OUT_DIR = Path("/sessions/hopeful-admiring-turing/mnt/FORGE/out")


def _stub_generate(prompt: str) -> str:
    return (
        f"[DRAFT — stub generator, replace with Anthropic client]\n"
        f"(prompt length: {len(prompt)} chars)"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1. Inventory + extraction ---
    all_files = sorted(DEAL_ROOT.glob("*.pdf"))
    print(f"Deal root: {DEAL_ROOT}")
    print(f"Files found: {len(all_files)}")
    for f in all_files:
        print(f"  - {f.name}")

    seller_returns = []
    principal_income = None

    for f in all_files:
        name = f.name.lower()
        if "tax return - seller" in name or "munchies" in name:
            print(f"\n[extract_1120s] {f.name}")
            r = extract_1120s(f)
            seller_returns.append(r)
            print(f"  gross_receipts: {r.get('gross_receipts')}")
            print(f"  line_22:        {r.get('ordinary_business_income_line_22')}")
            print(f"  m1_line_1:      {r.get('m1_net_income_per_books')}")
            print(f"  net_income_preferred: {r.get('net_income_preferred')} "
                  f"({r.get('net_income_source')})")
        elif "tax return transcripts" in name or "principal" in name:
            if is_irs_transcript(f):
                print(f"\n[extract_irs_transcript_1040] {f.name}")
                principal_income = extract_irs_transcript_1040(f)
                print(f"  agi:            {principal_income.get('agi')}")
                print(f"  taxable_income: {principal_income.get('taxable_income')}")

    # --- 2. Deal type detection ---
    deal_type = detect_deal_type([str(f) for f in all_files])
    print(f"\nDetected deal type: {deal_type}")

    # --- 3. Reconcile ---
    docs = []
    for r in seller_returns:
        docs.append(DocItem(
            doc_class="seller_returns_3yr",
            path=r["source_path"],
            year=r.get("tax_year"),
            extracted=r,
        ))
    if principal_income:
        docs.append(DocItem(
            doc_class="buyer_personal_returns_2yr",
            path=principal_income["source_path"],
            year=principal_income.get("tax_year"),
            extracted=principal_income,
        ))
    # Purchase agreement presence
    for f in all_files:
        if "purchase" in f.name.lower():
            docs.append(DocItem(doc_class="purchase_agreement", path=str(f)))

    bundle = DealBundle(
        deal_name="Mirzai Group LLC — Acquisition of Munchies LLC",
        deal_type=deal_type,
        docs=docs,
    )
    report = reconcile(bundle)
    print(f"\nReconcile verdict: ready={report.ready}")
    print(f"Missing docs:  {report.missing_docs}")
    print(f"Null fields:   {len(report.null_fields)}")
    for n in report.null_fields[:5]:
        print(f"  - {n}")
    if report.warnings:
        print(f"Warnings:")
        for w in report.warnings[:5]:
            print(f"  - {w}")

    (OUT_DIR / "mirzai_reconcile.json").write_text(
        json.dumps(report.to_dict(), indent=2)
    )

    # --- 4. Narratives (stub generator) ---
    nar.configure_generator(_stub_generate)

    loan_purpose = nar.draft_loan_purpose(
        deal_name="Mirzai Group LLC",
        deal_type="acquisition",
        loan_amount=310_000,
        use_of_proceeds=[
            {"purpose": "Business acquisition (Munchies LLC)", "amount": 300_000},
            {"purpose": "Closing costs + working capital", "amount": 10_000},
        ],
    )
    project_summary = nar.draft_project_summary(
        deal_name="Mirzai Group LLC",
        borrower_description="Buyer acquiring existing food-service operator Munchies LLC.",
        key_facts={
            "Seller 2024 Revenue": f"${seller_returns[0].get('gross_receipts') or 'n/a':,}"
                if seller_returns and seller_returns[0].get('gross_receipts') else "n/a",
            "Seller 2024 Net Income (M-1)": f"${seller_returns[0].get('net_income_preferred') or 'n/a':,}"
                if seller_returns and seller_returns[0].get('net_income_preferred') else "n/a",
            "Principal AGI 2024": f"${principal_income.get('agi'):,}" if principal_income else "n/a",
            "Purchase Price": "$310,000",
        },
    )

    # --- 5. Render memo ---
    sr = seller_returns[0] if seller_returns else {}
    ctx = DealContext(
        deal_name="Mirzai Group LLC — Acquisition of Munchies LLC",
        deal_type=deal_type,
        sections={
            "signatures_approval": {
                "underwriter": "Keith Williams, VP - Underwriter",
                "credit_manager": "Bryan Meadows, SVP - Credit Manager",
                "date": "2026-04-08",
            },
            "package_summary": {
                "Deal Type": deal_type,
                "Buyer Entity": "Mirzai Group LLC",
                "Seller Entity": "Munchies LLC",
                "Loan Amount": "$310,000",
                "Purchase Price": "$310,000",
            },
            "borrowers_guarantors": [
                {"Entity": "Mirzai Group LLC", "Role": "Borrower (NewCo)", "Structure": "LLC"},
                {"Entity": "Qayoom A. Mirzai", "Role": "Guarantor / Principal", "Structure": "Individual"},
            ],
            "loan_terms": {
                "Loan Amount": "$310,000",
                "Program": "SBA 7(a)",
                "Term": "10 years",
                "Rate": "Prime + 2.75% variable",
                "Guaranty Fee": "TBD",
            },
            "loan_purpose": loan_purpose.draft,
            "total_exposure": {"Proposed Colony Bank Debt": "$310,000"},
            "project_summary": project_summary.draft,
            "sources_uses": [
                {"Source": "SBA 7(a)", "Amount": "$310,000", "Use": "Business acquisition + closing"},
            ],
            "ownership_summary": [
                {"Owner": "Qayoom A. Mirzai", "%": "100%"},
            ],
            "management": "Qayoom Mirzai, principal. Detail bio to be inserted.",
            "income_statement_analysis": [
                {
                    "Year": sr.get("tax_year") or "2024",
                    "Gross Receipts": f"${sr.get('gross_receipts', 0):,}" if sr.get("gross_receipts") else "n/a",
                    "Line 22": f"${sr.get('ordinary_business_income_line_22', 0):,}" if sr.get("ordinary_business_income_line_22") else "n/a",
                    "M-1 Net Income": f"${sr.get('m1_net_income_per_books', 0):,}" if sr.get("m1_net_income_per_books") else "n/a",
                    "Preferred NI": f"${sr.get('net_income_preferred', 0):,}" if sr.get("net_income_preferred") else "n/a",
                },
            ],
            "debt_service_coverage_analysis": [
                {"Metric": "BANI (placeholder)", "Value": "TO BE COMPUTED via cashflow.py"},
                {"Metric": "ADS", "Value": "TO BE COMPUTED"},
                {"Metric": "Borrower DSCR", "Value": "TO BE COMPUTED"},
            ],
            "balance_sheet_analysis": [{"Item": "TBD", "Value": "Pending seller balance sheet"}],
            "pro_forma_balance_sheet": [{"Item": "TBD", "Value": "Pending closing statement"}],
            "working_capital_analysis": [{"Metric": "TBD", "Value": "Pending"}],
            "ratio_industry_analysis": [{"Ratio": "TBD", "Value": "Pending", "Industry": "NAICS 722513"}],
            "individual_analysis": [
                {
                    "Principal": "Qayoom A. Mirzai",
                    "AGI 2024": f"${principal_income.get('agi'):,}" if principal_income and principal_income.get("agi") else "n/a",
                    "Taxable Income": f"${principal_income.get('taxable_income'):,}" if principal_income and principal_income.get("taxable_income") else "n/a",
                    "Filing Status": principal_income.get("filing_status") if principal_income else "n/a",
                },
            ],
            "global_dscr_analysis": [{"Metric": "Global DSCR", "Value": "TO BE COMPUTED"}],
            "global_debt_liquidity": [{"Metric": "Global Liquidity Ratio", "Value": "PFS not yet extracted"}],
            "collateral_analysis": [{"Asset": "Business assets (acquired)", "Margin": "TBD"}],
            "environmental_investigation": {"RSRA Required": "TBD — restaurant use"},
            "sba_eligibility": {
                "Size Standard": "Pass (small business)",
                "Use of Proceeds": "Change of ownership — eligible per SOP 50-10-8",
                "Character": "Pending 912 review",
            },
            "existing_sba_loans": [{"Loan": "None"}],
            "strengths_weaknesses": [
                "Strength: Seller 2024 Line 22 income confirms cash flow",
                "Strength: Principal AGI $223,952 supports personal guaranty",
                "Weakness: New owner / transition risk",
                "Weakness: Seller M-1 Line 1 materially below Line 22 (book-tax diff to explain)",
            ],
            "conditions_covenants": [
                "Standard: life insurance collateral assignment on principal",
                "Standard: UCC-1 on business assets",
                "Deal-specific: 60-day transition period with seller",
                "Deal-specific: Monthly financials required for first 12 months post-close",
            ],
            "third_party_reports": ["Business valuation (pending)", "Phase I ESA (TBD)"],
        },
    )

    missing = missing_required_sections(ctx)
    print(f"\nMissing required sections: {missing}")

    out_path = OUT_DIR / "Mirzai_Group_LLC_DRAFT_Memo.docx"
    render_memo(ctx, out_path)
    print(f"\nDraft memo written: {out_path}")
    print(f"Size: {out_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
