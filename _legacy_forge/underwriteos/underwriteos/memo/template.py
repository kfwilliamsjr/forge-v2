"""
Colony Bank SBSL canonical loan-report section template.

Extracted from the AIPSS final report (3/11/2026, 1,773 lines, fully
approved by Bryan Meadows). This is the section spine every UnderwriteOS
memo must populate. Subsequent sections can be extended or marked
optional per deal.type, but the order and names should match so downstream
reviewers see a familiar document.

Each section has:
    key      — canonical snake_case id used in the renderer
    title    — the exact header string that appears in the PDF
    required — whether this section is mandatory for a v1 memo
    source   — where the data comes from (extractor, user input, LLM narrative)
    type     — how it's rendered: narrative | table | kv_grid | signature_block
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

SourceType = Literal[
    "extractor",       # populated from structured extraction
    "calc",            # computed by cashflow.py
    "user",            # user input / manual
    "llm_narrative",   # LLM draft, reviewed by underwriter
    "signature",       # static signature block
]

RenderType = Literal[
    "narrative", "table", "kv_grid", "signature_block", "list"
]


@dataclass(frozen=True)
class MemoSection:
    key: str
    title: str
    required: bool
    source: SourceType
    render: RenderType
    notes: str = ""


# Ordered by appearance in the AIPSS report. Keys are the downstream
# contract — do not rename without updating the renderer.
COLONY_BANK_SECTIONS: list[MemoSection] = [
    MemoSection("signatures_approval", "Signatures and Approval", True, "signature", "signature_block",
                "Keith as VP-Underwriter, Bryan Meadows as SVP-Credit Manager."),
    MemoSection("conditions", "Conditions", True, "llm_narrative", "list",
                "Bulleted conditions list. LLM drafts, underwriter edits."),

    MemoSection("package_summary", "Package Summary", True, "extractor", "kv_grid",
                "Owner, NAICS, risk rating, referral info, franchise flag, 912 flag."),
    MemoSection("borrowers_guarantors", "Borrowers and Guarantors", True, "extractor", "table",
                "All borrowing entities + guarantors with role, structure, formation date."),
    MemoSection("loan_terms", "Loan Terms", True, "user", "kv_grid",
                "Loan amount, term, rate, amort, guaranty %, fees."),
    MemoSection("loan_purpose", "Loan Purpose", True, "llm_narrative", "narrative"),
    MemoSection("total_exposure", "Total Exposure", True, "extractor", "kv_grid",
                "All existing + proposed Colony Bank exposure."),
    MemoSection("project_summary", "Project Summary", True, "llm_narrative", "narrative"),
    MemoSection("sources_uses", "Sources and Uses", True, "user", "table"),
    MemoSection("sources_uses_comments", "Sources and Uses Comments", False, "llm_narrative", "narrative"),

    MemoSection("ownership_summary", "Ownership Summary", True, "extractor", "table"),
    MemoSection("management", "Management", True, "llm_narrative", "narrative",
                "Principal bios, experience, roles."),

    MemoSection("income_statement_analysis", "Income Statement Analysis", True, "extractor", "table",
                "3-year spread from 1120-S/1120/1040 extractor output."),
    MemoSection("debt_service_coverage_analysis", "Debt Service Coverage Analysis", True, "calc", "table",
                "BANI, ADS, Borrower DSCR, rate-shock DSCR."),
    MemoSection("balance_sheet_analysis", "Balance Sheet Analysis", True, "extractor", "table"),
    MemoSection("reconciliation_net_worth", "Reconciliation of Net Worth Analysis", False, "extractor", "table"),
    MemoSection("pro_forma_balance_sheet", "Pro Forma Balance Sheet Analysis", True, "calc", "table"),
    MemoSection("working_capital_analysis", "Working Capital Analysis", True, "calc", "table"),
    MemoSection("ratio_industry_analysis", "Ratio/Industry Analysis", True, "calc", "table",
                "Coverage, leverage, operating, expense-to-sales, DSCR ratios + industry benchmarks."),

    MemoSection("individual_analysis", "Individual Analysis", True, "extractor", "table",
                "Per-principal income, personal debts, living expenses."),
    MemoSection("global_dscr_analysis", "Global DSCR Analysis", True, "calc", "table"),
    MemoSection("global_debt_liquidity", "Global Debt/Liquidity Analysis", True, "calc", "table",
                "Uses PFS 413 global_liquid_assets."),

    MemoSection("collateral_analysis", "Collateral Analysis", True, "extractor", "table"),
    MemoSection("collateral_notes", "Collateral Notes / Comments", False, "llm_narrative", "narrative"),

    MemoSection("environmental_investigation", "Environmental Investigation", True, "user", "kv_grid"),
    MemoSection("brand_franchise_license", "Brand/Franchise/License", False, "user", "kv_grid"),
    MemoSection("other_background", "Other Background Information/Construction", False, "llm_narrative", "narrative"),
    MemoSection("refinance", "Refinance", False, "llm_narrative", "narrative",
                "Only required if deal.type == refi or includes refi component."),

    MemoSection("sba_eligibility", "SBA Eligibility", True, "llm_narrative", "kv_grid",
                "SOP 50-10 eligibility checklist. Use of proceeds, size, affiliation, character."),
    MemoSection("existing_sba_loans", "Existing SBA Loans", True, "user", "table"),
    MemoSection("lender_policy_exceptions", "Lender Policy Exceptions", False, "llm_narrative", "list"),

    MemoSection("strengths_weaknesses", "Strengths and Weaknesses", True, "llm_narrative", "list",
                "Bullet list of mitigants and risks. LLM drafts, underwriter finalizes."),
    MemoSection("conditions_covenants", "Conditions and Covenants", True, "llm_narrative", "list"),
    MemoSection("third_party_reports", "Third Party Reports & Agreements", True, "user", "list"),
]


# Optional-section rules by deal type.
_OPTIONAL_OVERRIDES: dict[str, dict[str, bool]] = {
    "refi": {"refinance": True},  # required for refi deals
    "acquisition": {"sources_uses_comments": True, "other_background": True},
    "startup": {"ratio_industry_analysis": False},  # no historicals
    "cdfi": {
        "sba_eligibility": False,
        "existing_sba_loans": False,
        "lender_policy_exceptions": False,
    },
}


def get_template_for_program(program_key: str) -> list[MemoSection]:
    """
    Program-aware template router. Use this in new code instead of
    get_template(deal_type). Maps a Program.memo_template key to the
    correct section spine.

        colony_bank → Colony Bank 32-section SBA template
        cif         → CIF lean 12-section template (parallel sibling)
    """
    if program_key == "cif":
        from .template_cif import get_cif_template
        return get_cif_template()
    # Default: Colony Bank SBA spine
    return list(COLONY_BANK_SECTIONS)


def get_template(deal_type: Optional[str] = None) -> list[MemoSection]:
    """
    Return the ordered memo section list, with required flags adjusted
    for the given deal.type. If deal_type is None, returns the base SBA
    7(a) Colony Bank template unchanged.
    """
    if deal_type is None or deal_type not in _OPTIONAL_OVERRIDES:
        return list(COLONY_BANK_SECTIONS)

    overrides = _OPTIONAL_OVERRIDES[deal_type]
    out = []
    for sec in COLONY_BANK_SECTIONS:
        if sec.key in overrides:
            out.append(MemoSection(
                key=sec.key, title=sec.title,
                required=overrides[sec.key],
                source=sec.source, render=sec.render, notes=sec.notes,
            ))
        else:
            out.append(sec)
    return out
