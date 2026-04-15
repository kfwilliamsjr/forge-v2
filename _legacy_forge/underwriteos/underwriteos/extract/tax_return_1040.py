"""
Form 1040 extractor (two-pass, layout-tolerant).

Day 6 rewrite using the same label-anchor + last-int-on-line pattern as the
1120-S extractor. Retains the K-1 dedupe logic from Day 4:
  personal_income_ex_k1 excludes Schedule 1 Line 5 (S-corp flow-through) so
  the global DSCR formula doesn't double-count business NI.

Scanned PDFs are auto-routed through OCR by extract.ocr.read_pdf_text.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .ocr import read_pdf_text
from .tax_return_1120s import (
    _find_line_with_next,
    _last_int_on_line,
    _first_money_on_line,
    _INT_RE,
    _to_int,
    _is_money_token,
)


def _scan(text: str, anchor: str, mode: str = "last") -> Optional[int]:
    result = _find_line_with_next(text, anchor)
    if result is None:
        return None
    anchor_line, next_line = result
    anchor_pos = anchor_line.lower().find(anchor.lower())
    tail = anchor_line[anchor_pos + len(anchor):]
    picker = _last_int_on_line if mode == "last" else _first_money_on_line
    val = picker(tail)
    if val is not None:
        return val
    return _first_money_on_line(next_line)


# Anchors sourced from IRS Form 1040 label text. Descriptions are stable
# across tax prep software; column widths are not.
_ANCHORS = {
    "wages_line_1a": "Total amount from Form(s) W-2",
    "taxable_interest_2b": "Taxable interest",
    "ordinary_dividends_3b": "Ordinary dividends",
    "ira_taxable_4b": "IRA distributions",
    "pensions_taxable_5b": "Pensions and annuities",
    "social_security_taxable_6b": "Social security benefits",
    "capital_gain_loss_line_7": "Capital gain or (loss)",
    "additional_income_line_8": "Additional income from Schedule 1",
    "total_income_line_9": "Add lines 1z",
    "agi_line_11": "adjusted gross income",
    "taxable_income_line_15": "This is your taxable income",
    "sch1_line_5_scorp_rental": "Rental real estate, royalties, partnerships, S corporations",
}


_SCHEDULE_C_ANCHORS = {
    "gross_receipts": "Gross receipts or sales",
    "cost_of_goods_sold": "Cost of goods sold",
    "gross_income": "Gross income",
    "advertising": "Advertising",
    "car_truck_expenses": "Car and truck expenses",
    "depreciation": "Depreciation and section 179",
    "insurance": "Insurance (other than health)",
    "interest_mortgage": "Mortgage (paid to banks",
    "interest_other": "Other interest",
    "rent_lease_vehicles": "Vehicles, machinery",
    "rent_lease_other": "Other business property",
    "repairs_maintenance": "Repairs and maintenance",
    "taxes_licenses": "Taxes and licenses",
    "utilities": "Utilities",
    "wages": "Wages (less employment credits)",
    "other_expenses": "Other expenses",
    "total_expenses": "Total expenses before",
    "net_profit_loss": "Net profit or (loss)",
}


def _extract_schedule_c(text: str) -> dict | None:
    """
    Extract Schedule C (Profit or Loss from Business) from a 1040 PDF.

    Returns None if Schedule C is not detected in the text. Otherwise
    returns a dict of field → value mappings. The net_profit_loss field
    maps to the same role as 1120-S net_income_preferred for cashflow.py.
    """
    # Detect Schedule C presence — look for the form header
    if not re.search(r"Schedule\s+C\b.*Profit or Loss", text, re.I):
        return None

    result: dict = {}

    # Business name — appears after "Name of proprietor" or "Business name"
    m = re.search(
        r"(?:Business name|Name of proprietor|Principal business or profession)"
        r"[:\s]*([A-Z][A-Z0-9 &/.,\'\-]+?)(?:\s{2,}|\n)",
        text,
    )
    result["business_name"] = m.group(1).strip() if m else None

    # NAICS code
    m = re.search(r"Business code\s*(\d{6})", text)
    if not m:
        m = re.search(r"Principal business.*?(\d{6})", text)
    result["naics"] = m.group(1) if m else None

    # Line items
    for field, anchor in _SCHEDULE_C_ANCHORS.items():
        result[field] = _scan(text, anchor)

    # Preferred fields for cashflow.py compatibility
    result["net_income_preferred"] = result.get("net_profit_loss")
    result["depreciation_preferred"] = result.get("depreciation")

    return result


def extract_1040(pdf_path: str | Path) -> dict:
    """
    Extract a normalized 1040 schema. Transparently OCRs scanned PDFs.
    """
    text = read_pdf_text(pdf_path, profile="high")
    out: dict = {"source_path": str(pdf_path)}

    # Header
    m = re.search(r"Form 1040 \((\d{4})\)", text)
    out["tax_year"] = int(m.group(1)) if m else None
    m = re.search(r"\b(\d{3}-\d{2}-\d{4})\b", text)
    out["primary_ssn"] = m.group(1) if m else None
    m = re.search(r"Form 1040 \(\d{4}\)\s+([A-Z][A-Z &.'\-]+?)\s{2,}\d{3}-\d{2}-\d{4}", text)
    out["taxpayer_names"] = m.group(1).strip() if m else None

    for field, anchor in _ANCHORS.items():
        out[field] = _scan(text, anchor)

    # Wages: line 1a is canonical; some years also show line 1z aggregate
    out["wages_preferred"] = out.get("wages_line_1a")

    # K-1 flow-through separated for DSCR dedupe
    out["k1_flow_through"] = out.get("sch1_line_5_scorp_rental") or 0

    # Personal income excluding K-1 (prevents double-count vs business BANI)
    components = [
        out.get("wages_preferred") or 0,
        out.get("taxable_interest_2b") or 0,
        out.get("ordinary_dividends_3b") or 0,
        out.get("ira_taxable_4b") or 0,
        out.get("pensions_taxable_5b") or 0,
        out.get("social_security_taxable_6b") or 0,
        out.get("capital_gain_loss_line_7") or 0,
    ]
    out["personal_income_ex_k1"] = sum(components)

    # Schedule C extraction — sole-prop / disregarded-entity years.
    # If Schedule C is present, the borrower's business P&L lives here
    # instead of on a separate 1120-S. These fields map 1:1 to the
    # cashflow.py inputs that normally come from 1120-S extraction.
    out["schedule_c"] = _extract_schedule_c(text)

    return out
