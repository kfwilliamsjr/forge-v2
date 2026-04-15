"""
CIF (Community Investment Fund VI) memo template.

Parallel sibling to template.py (Colony Bank 32-section spine).
Structure derived from the signed CIF loan reports Keith has produced
for Swift Capital. CIF memos are leaner than SBA bank memos: no SOP
50-10 eligibility section, no existing-SBA-loans table, no rate-shock
analysis required (CIF can write fixed-rate loans).

Sections are intentionally fewer and reorder around the borrower-story
arc CIF underwriters expect: header → terms → narrative → cash flow →
collateral → conditions → signature.

This template is loaded via memo.template.get_template_for_program("cif").
"""
from __future__ import annotations

from .template import MemoSection


CIF_SECTIONS: list[MemoSection] = [
    MemoSection("header", "Loan Report Header", True, "extractor", "kv_grid",
                "Applicant, Owner/Guarantor, Location, Approved Loan, Program."),
    MemoSection("loan_terms", "Proposed Loan Terms", True, "user", "kv_grid",
                "Amount, rate, fees, amortization, P&I, ADS, collateral position, borrower equity."),
    MemoSection("sources_uses", "Sources and Uses", True, "user", "table"),
    MemoSection("business_overview", "Business Overview", True, "llm_narrative", "narrative"),
    MemoSection("request_summary", "Request Summary", True, "llm_narrative", "narrative",
                "Use of proceeds + borrower story."),
    MemoSection("loan_readiness", "Loan Readiness / Cash Flow Snapshot", True, "calc", "table",
                "Historical + projected DSCR. Driven by cashflow.py, NEVER LLM."),
    MemoSection("global_cash_flow", "Supplemental Global Cash Flow / Guarantor Support",
                True, "calc", "table"),
    MemoSection("collateral_support", "Collateral Support", True, "extractor", "table"),
    MemoSection("net_risk", "Net Risk to Bank", True, "calc", "kv_grid"),
    MemoSection("strengths_weaknesses", "Strengths and Weaknesses", True, "llm_narrative", "list"),
    MemoSection("conditions", "Conditions", True, "llm_narrative", "list"),
    MemoSection("signature_block", "Signature and Approval", True, "signature", "signature_block"),
]


def get_cif_template() -> list[MemoSection]:
    return list(CIF_SECTIONS)
