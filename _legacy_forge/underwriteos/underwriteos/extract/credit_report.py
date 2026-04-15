"""
Credit report extractor (Merchants Credit Bureau / RMCR format).

Pulls the fields the cashflow engine and policy gates need:
  - Applicant name, SSN, DOB
  - All bureau scores found (Equifax, Experian, TransUnion FICO)
  - Trade summary by category (mortgage, auto, installment, revolving) with
    count, balance, high credit, monthly payments, past due
  - Totals row (this is the authoritative monthly debt service used for global
    DSCR — Day 3 finding: PFS understated by ~60% vs credit report)
  - Secured/unsecured debt totals
  - Revolving utilization %, total debt/high credit %
  - Derogatory summary (charge-offs, collections, bankruptcy, public records,
    30/60/90-day late counts, inquiries)

Reader: pdftotext -layout. No LLM.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional

_INT = r"(\d[\d,]*)"


def _to_int(s: Optional[str]) -> Optional[int]:
    if s is None:
        return None
    s = s.strip().replace(",", "").replace("$", "")
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        try:
            return int(float(s))
        except ValueError:
            return None


def _read_text(pdf_path: str | Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


# Trade summary row: LABEL  COUNT  BALANCE  HIGH_CREDIT  PAYMENTS  PAST_DUE
def _row(label: str) -> re.Pattern:
    return re.compile(
        rf"{label}\s+{_INT}\s+{_INT}\s+{_INT}\s+{_INT}\s+{_INT}",
        re.IGNORECASE,
    )


_ROW_PATTERNS = {
    "mortgage": _row(r"MORTGAGE"),
    "auto": _row(r"AUTO"),
    "education": _row(r"EDUCATION"),
    "other_installment": _row(r"OTHER INSTALLMENT"),
    "open": _row(r"OPEN"),
    "revolving": _row(r"REVOLVING"),
    "other": _row(r"OTHER"),
    "total": _row(r"TOTAL"),
}

_SCORE_PATTERNS = {
    "equifax": re.compile(r"EQUIFAX[/\s]?FICO[^\n]*\n[^\n]*?SCORE:\s*(\d{3})", re.I),
    "experian": re.compile(r"EXPERIAN[/\s]?FICO[^\n]*\n[^\n]*?SCORE:\s*(\d{3})", re.I),
    "transunion": re.compile(r"TRANS\s*UNION[/\s]?FICO[^\n]*\n[^\n]*?SCORE:\s*(\d{3})", re.I),
}

_FIELD_PATTERNS = {
    "applicant_name": re.compile(r"^APPLICANT\s+([A-Z][A-Z, ]+?)\s{2,}CO-APPLICANT", re.M),
    "applicant_ssn": re.compile(r"SOC SEC #\s+(\d{3}-\d{2}-\d{4})\s+DOB\s+(\d{2}/\d{2}/\d{4})"),
    "secured_debt": re.compile(r"SECURED DEBT\s+" + _INT),
    "unsecured_debt": re.compile(r"UNSECURED DEBT\s+" + _INT),
    "revolving_utilization_pct": re.compile(r"REVOLVING CREDIT\s+(\d+)%", re.S),
    "total_debt_high_credit_pct": re.compile(r"TOTAL DEBT/HIGH CREDIT\s+(\d+)%"),
    "charge_offs": re.compile(r"CHARGE OFFS:\s+(\d+)"),
    "collections": re.compile(r"COLLECTIONS:\s+(\d+)"),
    "bankruptcy": re.compile(r"BANKRUPTCY:\s+(\d+)"),
    "public_records": re.compile(r"PUBLIC RECORDS:\s+(\d+)"),
    "thirty_day_late": re.compile(r"30 DAYS:\s*(\d+)"),
    "sixty_day_late": re.compile(r"60 DAYS:\s*(\d+)"),
    "ninety_day_late": re.compile(r"90 DAYS:\s*(\d+)"),
    "inquiries": re.compile(r"INQUIRIES:\s+(\d+)"),
}


def extract_credit_report(pdf_path: str | Path) -> dict:
    """
    Extract a normalized credit report schema.

    Output includes a `monthly_debt_service` convenience field equal to the
    TOTAL row's PAYMENTS column. Multiply by 12 for `annual_personal_debt_service`
    in the global DSCR calculation. This is Keith's reconciliation rule:
    personal_debt_service = max(PFS notes payable, credit_report TOTAL × 12).
    """
    text = _read_text(pdf_path)
    out: dict = {"source_path": str(pdf_path)}

    # Trade summary rows
    trades: dict = {}
    for key, pat in _ROW_PATTERNS.items():
        m = pat.search(text)
        if m is None:
            trades[key] = None
            continue
        trades[key] = {
            "count": int(m.group(1)),
            "balance": _to_int(m.group(2)),
            "high_credit": _to_int(m.group(3)),
            "monthly_payment": _to_int(m.group(4)),
            "past_due": _to_int(m.group(5)),
        }
    out["trades"] = trades

    # Totals shortcut
    if trades.get("total"):
        out["total_balance"] = trades["total"]["balance"]
        out["total_high_credit"] = trades["total"]["high_credit"]
        out["monthly_debt_service"] = trades["total"]["monthly_payment"]
        out["annual_debt_service"] = trades["total"]["monthly_payment"] * 12
        out["total_past_due"] = trades["total"]["past_due"]
    else:
        out["monthly_debt_service"] = None
        out["annual_debt_service"] = None

    # Bureau scores
    scores: dict = {}
    for bureau, pat in _SCORE_PATTERNS.items():
        m = pat.search(text)
        if m:
            scores[bureau] = int(m.group(1))
    out["scores"] = scores
    out["primary_score"] = max(scores.values()) if scores else None

    # Other fields
    for key, pat in _FIELD_PATTERNS.items():
        m = pat.search(text)
        if m is None:
            out[key] = None
            continue
        if key == "applicant_ssn":
            out["applicant_ssn"] = m.group(1)
            out["applicant_dob"] = m.group(2)
        elif key == "applicant_name":
            out[key] = m.group(1).strip()
        elif key in ("revolving_utilization_pct", "total_debt_high_credit_pct"):
            out[key] = int(m.group(1))
        elif key in ("charge_offs", "collections", "bankruptcy", "public_records",
                     "thirty_day_late", "sixty_day_late", "ninety_day_late", "inquiries"):
            out[key] = int(m.group(1))
        else:
            out[key] = _to_int(m.group(1))

    return out
