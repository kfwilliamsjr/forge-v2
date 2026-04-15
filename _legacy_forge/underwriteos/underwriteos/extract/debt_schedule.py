"""
Business debt schedule extractor.

Feeds the ADS (Annual Debt Service) input for DSCR. The borrower
provides a debt schedule — typically one of:

    1. A PDF printout from QuickBooks / bank portal.
    2. A borrower-filled SBA debt schedule form (SBA Form 2202).
    3. An ad-hoc Excel or text list the banker scanned.

Every row we care about has six columns:
    creditor | original_amount | current_balance | monthly_payment |
    interest_rate | maturity_date

This module runs OCR (if needed), post-processes the text, then walks
lines looking for rows that contain at least TWO money values and a
recognizable interest rate or date — the minimum signal we need to
trust the row. Rows are scored and low-confidence rows are flagged.

ADS is computed as sum(monthly_payment * 12) across all rows. The
caller decides which subset of debt goes into ADS (typically all
business debt, not the refinanced loan).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

from underwriteos.extract.ocr import read_pdf_text


# Money: require a thousands-comma OR an explicit .dd decimal so we don't
# swallow years, row numbers, or rate fragments. Also refuse anything
# immediately followed by "%" (that's an interest rate, not a dollar amount).
_MONEY_RE = re.compile(
    r"(?<![\w.])\$?("
    r"\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?"   # 1,234 or 1,234.56
    r"|\d+\.\d{2}"                           # 925.00
    r")(?![\d%])"
)
# Percent rate: 5.25% or 0.0525 — we only accept the % form to avoid
# picking up stray decimals.
_RATE_RE = re.compile(r"(\d{1,2}(?:\.\d{1,3})?)\s*%")
# Maturity date: 12/31/2029 or 2029-12-31 or Dec 2029
_DATE_RE = re.compile(
    r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"\d{4}-\d{2}-\d{2}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})",
    re.IGNORECASE,
)
# Header-ish lines we should not mistake for data rows.
_HEADER_TOKENS = {
    "creditor", "lender", "original", "balance", "payment",
    "rate", "maturity", "total", "totals", "debt schedule",
}


@dataclass
class DebtRow:
    creditor: Optional[str] = None
    original_amount: Optional[float] = None
    current_balance: Optional[float] = None
    monthly_payment: Optional[float] = None
    interest_rate: Optional[float] = None   # decimal, e.g. 0.0525
    maturity: Optional[str] = None
    raw_line: str = ""
    confidence: float = 0.0                 # 0..1

    def annual_debt_service(self) -> Optional[float]:
        if self.monthly_payment is None:
            return None
        return round(self.monthly_payment * 12, 2)


@dataclass
class DebtSchedule:
    source_path: str
    rows: list[DebtRow] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_balance(self) -> float:
        return round(sum(r.current_balance or 0 for r in self.rows), 2)

    @property
    def total_monthly_payment(self) -> float:
        return round(sum(r.monthly_payment or 0 for r in self.rows), 2)

    @property
    def annual_debt_service(self) -> float:
        return round(self.total_monthly_payment * 12, 2)

    def to_dict(self) -> dict:
        return {
            "source_path": self.source_path,
            "rows": [asdict(r) for r in self.rows],
            "warnings": self.warnings,
            "total_balance": self.total_balance,
            "total_monthly_payment": self.total_monthly_payment,
            "annual_debt_service": self.annual_debt_service,
        }


def _parse_money(tok: str) -> float:
    return float(tok.replace(",", "").replace("$", ""))


def _is_header_line(line: str) -> bool:
    lower = line.lower()
    hits = sum(1 for t in _HEADER_TOKENS if t in lower)
    # A line is a header if it names 3+ header tokens and has no money.
    return hits >= 3 and not _MONEY_RE.search(line)


def _extract_creditor(line: str, first_money_start: int) -> Optional[str]:
    """Take text up to the first money token as the creditor name."""
    head = line[:first_money_start].strip(" -\t|")
    # Strip leading row numbers like "1." or "1)"
    head = re.sub(r"^\d{1,2}[.)\]]\s*", "", head)
    if len(head) < 2:
        return None
    # Reject if it's just header noise
    if head.lower() in _HEADER_TOKENS:
        return None
    return head[:80]


def _parse_line(line: str) -> Optional[DebtRow]:
    """Try to extract a debt row from a single text line. Return None
    if the line clearly isn't a data row."""
    stripped = line.strip()
    if not stripped or _is_header_line(stripped):
        return None
    # Totals/subtotal rows — never data
    first_word = stripped.split()[0].lower() if stripped.split() else ""
    if first_word in ("total", "totals", "subtotal", "subtotals"):
        return None

    money_matches = list(_MONEY_RE.finditer(stripped))
    if len(money_matches) < 2:
        # Need at least original + balance, or balance + payment.
        return None

    rate_match = _RATE_RE.search(stripped)
    date_match = _DATE_RE.search(stripped)

    # Confidence heuristic: money count + presence of rate + presence of date
    conf = 0.0
    conf += min(len(money_matches), 3) * 0.2   # up to 0.6
    if rate_match: conf += 0.25
    if date_match: conf += 0.15
    conf = min(conf, 1.0)

    if conf < 0.4:
        return None

    values = [_parse_money(m.group(1)) for m in money_matches]

    # Assign by positional heuristic — columns in a debt schedule are
    # almost always: orig, balance, payment. If we only have 2, assume
    # balance + payment.
    if len(values) >= 3:
        original, balance, payment = values[0], values[1], values[2]
    else:
        original, balance, payment = None, values[0], values[1]

    # Sanity check: monthly payment should be much smaller than balance.
    # If not, we probably mis-ordered — swap.
    if balance and payment and payment > balance:
        balance, payment = payment, balance

    row = DebtRow(
        creditor=_extract_creditor(stripped, money_matches[0].start()),
        original_amount=original,
        current_balance=balance,
        monthly_payment=payment,
        interest_rate=(float(rate_match.group(1)) / 100.0) if rate_match else None,
        maturity=date_match.group(0) if date_match else None,
        raw_line=stripped,
        confidence=round(conf, 2),
    )
    return row


def extract_debt_schedule(pdf_path: str | Path) -> DebtSchedule:
    """
    Parse a borrower-provided debt schedule PDF into structured rows.

    Returns DebtSchedule with rows and warnings. Never raises on parse
    failure — an empty rows list with a warning is a valid result for
    a schedule that's too messy to machine-read.
    """
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(str(p))

    schedule = DebtSchedule(source_path=str(p))

    try:
        text = read_pdf_text(p)
    except Exception as e:
        schedule.warnings.append(f"Failed to read PDF text: {e}")
        return schedule

    if not text.strip():
        schedule.warnings.append("PDF produced no text even after OCR.")
        return schedule

    for line in text.splitlines():
        row = _parse_line(line)
        if row:
            schedule.rows.append(row)

    if not schedule.rows:
        schedule.warnings.append(
            "No debt rows matched. Schedule may be a non-standard format — "
            "request a filled SBA Form 2202 from the borrower."
        )

    # Flag low-confidence rows
    low = [r for r in schedule.rows if r.confidence < 0.6]
    if low:
        schedule.warnings.append(
            f"{len(low)} of {len(schedule.rows)} rows have confidence "
            f"below 0.6 — underwriter must verify against source."
        )

    return schedule


# Pure-text helper used by tests (and by a caller that already has the
# text in hand from a different extractor).
def parse_debt_schedule_text(text: str, source_path: str = "<text>") -> DebtSchedule:
    schedule = DebtSchedule(source_path=source_path)
    for line in text.splitlines():
        row = _parse_line(line)
        if row:
            schedule.rows.append(row)
    return schedule
