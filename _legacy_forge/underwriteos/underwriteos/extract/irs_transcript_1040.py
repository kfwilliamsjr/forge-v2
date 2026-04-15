"""
IRS 1040 transcript extractor.

Handles the 'Record of Account' and 'Return Transcript' formats from
IRS Get Transcript service. These are labeled key:value layouts — much
simpler than parsing raw 1040 forms, but do NOT contain K-1 detail or
wage breakdown (that lives on the 'Wage & Income Transcript').

Fields captured: tax_year, filing_status, AGI, taxable_income,
tax_per_return, SE income, transcript_type.

For global cash flow, AGI is the primary driver — K-1 flow-through must
come from the entity-level 1120-S extractor's Schedule K-1 output, not
from this transcript.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .ocr import read_pdf_text


_MONEY_RE = re.compile(r"-?\$?([\d,]+)\.\d{2}")


def _money(text: str, label: str) -> Optional[int]:
    for line in text.splitlines():
        if label.lower() in line.lower():
            m = _MONEY_RE.search(line)
            if m:
                val = int(m.group(1).replace(",", ""))
                if "-$" in line.split(label, 1)[-1][:20]:
                    val = -val
                return val
    return None


def _match(text: str, pattern: str, flags: int = 0) -> Optional[str]:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def is_irs_transcript(pdf_path: str | Path) -> bool:
    """Cheap sniff — does the first page look like an IRS transcript?"""
    text = read_pdf_text(pdf_path)[:2000]
    return (
        "Record of Account" in text
        or "Return Transcript" in text
        or "Tax Return Transcript" in text
    )


def extract_irs_transcript_1040(pdf_path: str | Path) -> dict:
    pdf_path = str(pdf_path)
    text = read_pdf_text(pdf_path)

    # Transcript type
    if "Record of Account" in text:
        transcript_type = "record_of_account"
    elif "Return Transcript" in text or "Tax Return Transcript" in text:
        transcript_type = "return_transcript"
    else:
        transcript_type = "unknown"

    # Tax year from "Tax Period Ending: 12-31-2024"
    year = None
    m = re.search(r"Tax Period Ending:\s*\d{2}-\d{2}-(\d{4})", text)
    if m:
        year = int(m.group(1))

    filing_status = _match(text, r"Filing status:\s*([A-Za-z ]+?)(?:\s{2,}|$)", re.MULTILINE)

    return {
        "source_path": pdf_path,
        "transcript_type": transcript_type,
        "tax_year": year,
        "filing_status": filing_status,
        "agi": _money(text, "Adjusted gross income"),
        "taxable_income": _money(text, "Taxable income"),
        "tax_per_return": _money(text, "Tax per return"),
        "se_income_taxpayer": _money(text, "SE taxable income taxpayer"),
        "se_income_spouse": _money(text, "SE taxable income spouse"),
        "total_se_tax": _money(text, "Total self employment tax"),
        # Fields that require Wage & Income transcript, not available here:
        "wages_line_1a": None,
        "k1_flow_through": None,
        "personal_income_ex_k1": None,
        "notes": (
            "Record of Account / Return Transcript does not include wage or "
            "K-1 breakdown. For global DSCR, use AGI as proxy and pull K-1 "
            "detail from entity 1120-S Schedule K-1."
        ),
    }
