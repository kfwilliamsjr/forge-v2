"""
Form 1120-S extractor (two-pass, layout-tolerant).

Day 6 rewrite: the Day 3 version was a single regex-per-field scanner that
overfit to the AIPSS fillable-PDF layout. Running it against the Mirzai and
Tropical Treasure Hunt training deals returned all-None because every deal
used a different tax prep software (different column widths, dot fills,
spacing). Post-OCR output added another layer of variance.

New strategy: two-pass scan.
  Pass 1 - Anchor on the line description text (e.g., "Compensation of officers").
           This is stable across software - the IRS controls the form labels.
  Pass 2 - Walk to the right of the anchor and capture the rightmost integer
           on the same line. This is how humans read tax returns.

Rules retained from Day 3:
  Finding #1 - Schedule M-1 Line 1 preferred over 1120-S Line 22 for net income
  Finding #2 - Form 4562 Part IV Line 22 preferred over 1120-S Line 14 for depreciation

Scanned PDFs are auto-routed through OCR by `extract.ocr.read_pdf_text`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .ocr import read_pdf_text


# Integer with optional commas, optional negative sign, optional parens.
# Negative lookahead on word chars prevents matching "4b", "1125-E", "27A"
# where the digits are part of a form/line reference, not a dollar value.
_INT_RE = re.compile(r"\(?-?[\d,]+\)?(?![\w\-])")


def _to_int(s: Optional[str]) -> Optional[int]:
    if s is None:
        return None
    s = s.strip().replace(",", "")
    if not s or s in ("-", "(", ")"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        n = int(s)
    except ValueError:
        try:
            n = int(float(s))
        except ValueError:
            return None
    return -n if neg else n


def _is_money_token(token: str) -> bool:
    """
    Heuristic: a dollar-value token either contains a comma (e.g. "11,373"),
    has 3+ digits ("195"), or is negative/parenthesized. Short integers
    like "1", "5", "22" are almost always line numbers or sub-indexes on
    IRS forms and should be ignored.
    """
    stripped = token.strip().strip("()").lstrip("-").replace(",", "")
    if not stripped.isdigit():
        return False
    has_comma = "," in token
    neg = token.startswith("(") or token.startswith("-")
    return has_comma or len(stripped) >= 3 or neg


def _first_money_on_line(line: str) -> Optional[int]:
    """Return the first money-token integer on a line, or None."""
    for token in _INT_RE.findall(line):
        if _is_money_token(token):
            return _to_int(token)
    return None


def _rightmost_money_on_line(line: str) -> Optional[int]:
    """Return the rightmost money-token integer on a line, or None."""
    for token in reversed(_INT_RE.findall(line)):
        if _is_money_token(token):
            return _to_int(token)
    return None


def _last_int_on_line(line: str) -> Optional[int]:
    """
    Return the very last integer on a line, regardless of size. Used for
    1120-S page 1 line items where the rightmost token is always the dollar
    value by IRS form construction, even when small (e.g. Line 14 dep = $27).

    The small-int noise filter is intentionally NOT applied here — on the
    anchor line the rightmost integer IS the value. OCR line-number bleed
    affects adjacent/fallback lines, which use _first_money_on_line instead.
    """
    matches = _INT_RE.findall(line)
    if not matches:
        return None
    return _to_int(matches[-1])


def _find_line_with_next(text: str, anchor: str, flags: int = re.I) -> Optional[tuple[str, str]]:
    """
    Return (anchor_line, next_line) for the first case-insensitive match of
    anchor. Next line is included because tax return layouts sometimes wrap
    the value onto the following line when the description column is narrow.
    """
    pattern = re.compile(re.escape(anchor), flags)
    m = pattern.search(text)
    if m is None:
        return None
    start = text.rfind("\n", 0, m.start()) + 1
    end = text.find("\n", m.end())
    if end == -1:
        end = len(text)
    anchor_line = text[start:end]
    # Grab the next line too for wrap handling.
    next_start = end + 1
    next_end = text.find("\n", next_start)
    if next_end == -1:
        next_end = len(text)
    next_line = text[next_start:next_end] if next_start < len(text) else ""
    return anchor_line, next_line


def _scan_line_value(text: str, anchor: str, mode: str = "last") -> Optional[int]:
    """
    Two-pass scan. Find the line containing the anchor, strip the anchor and
    everything to its left, then extract the value.

    mode="last"  - take the very last integer on the line. Correct for
                   1120-S Page 1 single-column line items where the dollar
                   value is always rightmost, even when small (e.g. $27).
    mode="first_money" - take the first money-token integer after the anchor.
                   Correct for Schedule M-1's 2-column layout where values
                   on the right column can follow the left-column value.

    Falls back to the next line when the anchor line has no value (handles
    value-wrap in narrow-column layouts).
    """
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
    # Next-line fallback only returns money tokens, never raw small integers.
    # This prevents picking up spurious sub-option markers from continuation
    # lines (e.g. "Rollover 2 QCD 3" under IRA distributions).
    return _first_money_on_line(next_line)


# Field anchor table. Order matters for Form 4562 Part IV Line 22 disambiguation.
_LINE_ANCHORS = {
    "gross_receipts": "Gross receipts or sales",
    "total_income_line_6": "Total income (loss)",
    "compensation_of_officers": "Compensation of officers",
    "salaries_wages": "Salaries and wages",
    "rents": "Rents",
    "taxes_licenses": "Taxes and licenses",
    "interest_expense": "Interest (see instructions)",
    "depreciation_line_14": "Depreciation from Form 4562",
    "total_deductions_line_21": "Total deductions",
    "ordinary_business_income_line_22": "Ordinary business income",
    "m1_net_income_per_books": "Net income (loss) per books",
}


def _extract_form_4562_total(text: str) -> Optional[int]:
    """
    Form 4562 Part IV Line 22 is the total depreciation line, labeled
    "Total. Add amounts from line 12, lines 14 through 17..." The label
    typically wraps across 2-3 text lines before the value appears, so we
    scan a multi-line window for the distinctive "22    <value>" terminator.
    """
    m = re.search(r"Add amounts from line 12", text)
    if m is None:
        return None
    # Take a 5-line window starting at the match.
    window_start = text.rfind("\n", 0, m.start()) + 1
    lines = text[window_start:].splitlines()[:5]
    window = " ".join(lines)
    # The line 22 value is the last integer on the wrapped block, but we need
    # to exclude section headers like "23 For assets..." that may follow.
    # Truncate at the next line-23 marker if present.
    cut = re.search(r"\b23\s+For assets", window)
    if cut:
        window = window[:cut.start()]
    return _last_int_on_line(window)


def _extract_header(text: str) -> dict:
    out: dict = {"entity_name": None, "ein": None, "tax_year": None}
    # EIN anywhere in text - first hit wins
    m = re.search(r"\b(\d{2}-\d{7})\b", text)
    if m:
        out["ein"] = m.group(1)
    # Tax year from "Form 1120-S (YYYY)" header
    m = re.search(r"Form\s*1120-?S\s*\((\d{4})\)", text)
    if m:
        out["tax_year"] = int(m.group(1))

    # Entity name — try two strategies:
    # Strategy 1 (most reliable): Page 1 "Name" field. On 1120-S page 1,
    # the entity name follows "Name" and precedes the EIN field. The label
    # "Number, street, and room" or "Address" follows on the next line.
    # Pattern: "Name" <whitespace> <ENTITY NAME> on the same or next line,
    # before "Number" or "Address" or "Type" appears.
    name_block = re.search(
        r"(?:^|\n)\s*Name\b[:\s]*([A-Z][A-Z0-9 &/.,\'\-]+?)(?:\s{2,}|\n)",
        text,
    )
    if name_block:
        candidate = name_block.group(1).strip()
        # Reject if it's just "Name" repeated or a form instruction
        if len(candidate) > 3 and candidate.upper() not in ("NAME", "NUMBER"):
            out["entity_name"] = candidate

    # Strategy 2 (fallback): page 2+ continuation header:
    # "Form 1120-S (2024)   ENTITY NAME   88-3540616"
    if out["entity_name"] is None:
        m = re.search(
            r"Form\s*1120-?S\s*\(\d{4}\)\s+([A-Z][A-Z0-9 &/.,\'\-]+?)\s{2,}\d{2}-\d{7}",
            text,
        )
        if m:
            out["entity_name"] = m.group(1).strip()

    return out


def extract_1120s(pdf_path: str | Path) -> dict:
    """
    Extract a normalized 1120-S schema from a tax return PDF.

    Transparently OCRs scanned PDFs. Returns a dict with raw line values plus
    `_preferred` fields that apply the Day 3 rules:
        net_income_preferred  = M-1 Line 1 if present, else Line 22
        depreciation_preferred = Form 4562 Part IV Line 22 if present, else Line 14
    """
    text = read_pdf_text(pdf_path, profile="high")
    out: dict = {"source_path": str(pdf_path)}

    # Header
    out.update(_extract_header(text))

    # Line items via two-pass scan. M-1 uses first-money mode because it's a
    # 2-column form where the anchor line can contain another line-number
    # after the value. Everything else uses last-int mode.
    for field, anchor in _LINE_ANCHORS.items():
        mode = "first_money" if field == "m1_net_income_per_books" else "last"
        out[field] = _scan_line_value(text, anchor, mode=mode)

    # Form 4562 Part IV Line 22
    out["form_4562_part_iv_total"] = _extract_form_4562_total(text)

    # Finding #1 - prefer Schedule M-1 Line 1
    m1 = out.get("m1_net_income_per_books")
    line22 = out.get("ordinary_business_income_line_22")
    if m1 is not None:
        out["net_income_preferred"] = m1
        out["net_income_source"] = "schedule_m1_line_1"
    else:
        out["net_income_preferred"] = line22
        out["net_income_source"] = "form_1120s_line_22_fallback"

    # Finding #2 - prefer Form 4562 Part IV total
    f4562 = out.get("form_4562_part_iv_total")
    line14 = out.get("depreciation_line_14")
    if f4562 is not None and (line14 is None or f4562 >= line14):
        out["depreciation_preferred"] = f4562
        out["depreciation_source"] = "form_4562_part_iv_line_22"
    else:
        out["depreciation_preferred"] = line14
        out["depreciation_source"] = "form_1120s_line_14_fallback"

    return out
