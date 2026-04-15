"""
SBA Form 413 (Personal Financial Statement) extractor.

Column-aware parser. Form 413 is a two-column grid: assets on the
left, liabilities on the right. A naive label-anchor scan picks up the
wrong column's value when a label phrase shares a line with a different
entry (e.g. "Real Estate" asset vs "Mortgages on Real Estate" liability).

Approach: detect the column split position dynamically from the
"ASSETS ... LIABILITIES" header line, then scan each line restricted
to the appropriate half.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .ocr import read_pdf_text


# Matches: -1,234  1,234.56  (1,234)  (1,234.56)
_MONEY_RE = re.compile(r"\([\d,]+(?:\.\d{2})?\)|-?[\d,]+(?:\.\d{2})?")


def _first_money(segment: str) -> Optional[int]:
    """First token in a line segment that looks like a money value.
    Requires comma OR >=3 digits to exclude line-number bleed.
    Supports parenthetical negatives: (52,345) → -52345."""
    for m in _MONEY_RE.finditer(segment):
        tok = m.group()
        # Detect parenthetical negative: (1,234) → -1234
        is_paren_neg = tok.startswith("(") and tok.endswith(")")
        if is_paren_neg:
            tok = tok[1:-1]  # strip parens
        clean = tok.replace(",", "").replace("-", "").replace(".", "")
        if not clean.isdigit():
            continue
        int_part = tok.replace(",", "").split(".")[0].lstrip("-")
        if "," in tok or len(int_part) >= 3:
            try:
                val = int(round(float(tok.replace(",", ""))))
                if is_paren_neg:
                    val = -abs(val)
                elif tok.startswith("-"):
                    val = -abs(val)
                return val
            except ValueError:
                continue
    return None


def _find_column_split(lines: list[str]) -> int:
    """Locate the column boundary from the ASSETS/LIABILITIES header.
    Returns a character index. Default 80 if header not found."""
    for line in lines:
        if "ASSETS" in line and "LIABILITIES" in line:
            liab_pos = line.find("LIABILITIES")
            assets_end = line.find("ASSETS") + len("ASSETS")
            return (assets_end + liab_pos) // 2
    return 80


def _find_grid_bounds(lines: list[str]) -> tuple[int, int]:
    """Return (start, end) indices for the assets/liabilities grid.

    Start = ASSETS/LIABILITIES header line. End = first 'Section 1' line
    after the header, or end of file. Restricting to the grid prevents
    prose in the form's instructions (which contains phrases like
    'personal net worth' and '§124.104') from polluting anchor matches.
    """
    start = 0
    end = len(lines)
    for i, line in enumerate(lines):
        if "ASSETS" in line and "LIABILITIES" in line:
            start = i
            break
    for i in range(start + 1, len(lines)):
        if re.match(r"\s*Section\s+1", lines[i]):
            end = i
            break
    return start, end


def _scan_column(
    lines: list[str],
    anchor: str,
    col_start: int,
    col_end: Optional[int] = None,
) -> Optional[int]:
    """Scan for an anchor phrase within [col_start, col_end) on each
    line. When matched, return the first money-token on the remainder
    of that column, or on the next line's same column if the current
    is empty."""
    for i, line in enumerate(lines):
        seg = line[col_start:col_end] if col_end else line[col_start:]
        if anchor.lower() in seg.lower():
            pos = seg.lower().find(anchor.lower())
            tail = seg[pos + len(anchor):]
            val = _first_money(tail)
            if val is not None:
                return val
            if i + 1 < len(lines):
                next_seg = (
                    lines[i + 1][col_start:col_end]
                    if col_end else lines[i + 1][col_start:]
                )
                nv = _first_money(next_seg)
                if nv is not None:
                    return nv
    return None


_ASSET_ANCHORS = {
    "cash_on_hand_in_banks": "Cash on Hand",
    "savings_accounts": "Savings Accounts",
    "ira_retirement": "IRA or Other Retirement",
    "accounts_notes_receivable": "Accounts & Notes Receivable",
    "life_insurance_csv": "Life Insurance",
    "stocks_and_bonds": "Stocks and Bonds",
    "real_estate": "Real Estate",
    "automobiles": "Automobiles",
    "other_personal_property": "Other Personal Property",
    "other_assets": "Other Assets",
}

_LIABILITY_ANCHORS = {
    "accounts_payable": "Accounts Payable",
    "notes_payable_banks": "Notes Payable to Banks",
    "installment_account_auto": "Installment Account (Auto)",
    "installment_account_other": "Installment Account (Other)",
    "loans_against_life_insurance": "Loan",
    "mortgages_on_real_estate": "Mortgages on Real Estate",
    "unpaid_taxes": "Unpaid Taxes",
    "other_liabilities": "Other Liabilities",
    "total_liabilities": "Total Liabilities",
    "net_worth": "Net Worth",
}

_INCOME_ANCHORS = {
    "salary": "Salary",
    "net_investment_income": "Net Investment Income",
    "real_estate_income": "Real Estate Income",
    "other_income": "Other Income",
}

_CONTINGENT_ANCHORS = {
    "as_endorser_co_maker": "As Endorser",
    "legal_claims_judgments": "Legal Claims",
    "provision_federal_income_tax": "Provision for Federal Income Tax",
    "other_special_debt": "Other Special Debt",
}

_LIQUID_FIELDS = ("cash_on_hand_in_banks", "savings_accounts", "stocks_and_bonds")
_RETIREMENT_FIELDS = ("ira_retirement",)


def extract_pfs_413(pdf_path: str | Path) -> dict:
    pdf_path = Path(pdf_path)
    text = read_pdf_text(str(pdf_path), profile="standard")
    lines = text.splitlines()

    split = _find_column_split(lines)
    grid_start, grid_end = _find_grid_bounds(lines)
    grid_lines = lines[grid_start:grid_end]

    assets = {
        k: _scan_column(grid_lines, a, col_start=0, col_end=split)
        for k, a in _ASSET_ANCHORS.items()
    }
    liabilities = {
        k: _scan_column(grid_lines, a, col_start=split)
        for k, a in _LIABILITY_ANCHORS.items()
    }
    # Income and contingent grids live after Section 1 — scan full doc
    # but the anchors are distinctive enough not to false-match.
    income = {k: _scan_column(lines, a, col_start=0) for k, a in _INCOME_ANCHORS.items()}
    contingent = {
        k: _scan_column(lines, a, col_start=split)
        for k, a in _CONTINGENT_ANCHORS.items()
    }

    liquid = sum((assets.get(f) or 0) for f in _LIQUID_FIELDS)
    retirement_margined = sum(
        int((assets.get(f) or 0) * 0.5) for f in _RETIREMENT_FIELDS
    )
    global_liquid_assets = liquid + retirement_margined

    # Total assets appears on a "Total ______ 1,675,987" line in the
    # assets column, not tied to an anchor label. The value often
    # appears on the line AFTER the "Total" label due to underscore
    # placement. Scan grid lines for a "Total" hit, take the first
    # money token on that line OR the next line within the assets column.
    total_assets = None
    for i, line in enumerate(grid_lines):
        left = line[:split]
        if re.search(r"\bTotal\b", left):
            for j in (i, i + 1):
                if j >= len(grid_lines):
                    break
                candidate = _first_money(grid_lines[j][:split])
                if candidate and candidate >= 100_000:
                    total_assets = candidate
                    break
            if total_assets:
                break

    extracted_nw = liabilities.get("net_worth")
    extracted_tl = liabilities.get("total_liabilities")

    # Cross-check: if both total_assets and total_liabilities are present,
    # compute net_worth = total_assets - total_liabilities. If OCR dropped
    # the sign on net_worth (common with parenthetical negatives or faint
    # minus signs), the computed value is more trustworthy.
    computed_nw = None
    nw_source = "extracted"
    if total_assets is not None and extracted_tl is not None:
        computed_nw = total_assets - extracted_tl
        if extracted_nw is not None:
            # Allow ±$1 tolerance for rounding (common on PFS forms)
            if abs(extracted_nw - computed_nw) <= 1:
                nw_source = "extracted"
                computed_nw = extracted_nw  # keep the form's own number
            else:
                nw_source = "computed (extracted disagreed)"
        else:
            nw_source = "computed (not extracted)"

    final_nw = computed_nw if computed_nw is not None else extracted_nw

    return {
        "source_path": str(pdf_path),
        "assets": assets,
        "liabilities": liabilities,
        "income": income,
        "contingent_liabilities": contingent,
        "total_assets": total_assets,
        "total_liabilities": extracted_tl,
        "net_worth": final_nw,
        "net_worth_source": nw_source,
        "global_liquid_assets": global_liquid_assets,
        "column_split_at": split,
        "notes": (
            "global_liquid_assets = cash + savings + stocks + 50% retirement, "
            "per Colony Bank SBSL liquidity convention. "
            "net_worth cross-checked: total_assets - total_liabilities."
        ),
    }
