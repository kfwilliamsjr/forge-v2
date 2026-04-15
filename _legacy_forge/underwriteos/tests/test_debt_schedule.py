"""
Tests for the debt schedule extractor.

Uses parse_debt_schedule_text() to drive the parser directly — we
don't need a real PDF to validate the row-matching logic.
"""
from __future__ import annotations

import pytest

from underwriteos.extract.debt_schedule import (
    parse_debt_schedule_text,
    _parse_line,
    DebtRow,
)


SAMPLE = """\
Business Debt Schedule                      As of 03/31/2026
Creditor          Original      Balance     Payment    Rate    Maturity
1. Wells Fargo    250,000.00    187,543.21    3,250.00  6.25%   12/15/2029
2. Chase Bank      75,000.00     42,108.55      925.00  7.00%   06/30/2028
3. SBA 7(a)       500,000.00    461,200.00    5,450.00  9.75%   04/01/2034
Totals            825,000.00    690,851.76    9,625.00
"""


def test_parses_three_real_rows():
    sched = parse_debt_schedule_text(SAMPLE)
    assert len(sched.rows) == 3
    creditors = [r.creditor for r in sched.rows]
    assert any("Wells Fargo" in c for c in creditors)
    assert any("Chase" in c for c in creditors)
    assert any("SBA" in c for c in creditors)


def test_row_values_match_source():
    sched = parse_debt_schedule_text(SAMPLE)
    wf = sched.rows[0]
    assert wf.original_amount == 250_000.00
    assert wf.current_balance == 187_543.21
    assert wf.monthly_payment == 3_250.00
    assert wf.interest_rate == pytest.approx(0.0625)
    assert wf.maturity == "12/15/2029"
    assert wf.confidence >= 0.9


def test_ads_computation():
    sched = parse_debt_schedule_text(SAMPLE)
    # 3250 + 925 + 5450 = 9625 monthly → 115,500 annual
    assert sched.total_monthly_payment == 9_625.00
    assert sched.annual_debt_service == 115_500.00
    assert sched.total_balance == 690_851.76


def test_header_line_rejected():
    assert _parse_line("Creditor   Original   Balance   Payment   Rate   Maturity") is None


def test_totals_line_rejected_gracefully():
    # "Totals" row has no rate and no date — confidence falls below 0.4
    row = _parse_line("Totals            825,000.00    690,851.76    9,625.00")
    # Either rejected or picked up with low confidence that gets flagged.
    # Accept either but don't let it poison the real rows.
    sched = parse_debt_schedule_text(SAMPLE)
    assert sched.total_monthly_payment == 9_625.00  # real rows only


def test_empty_input():
    sched = parse_debt_schedule_text("")
    assert sched.rows == []
    assert sched.annual_debt_service == 0.0


def test_payment_balance_swap_defense():
    # Pathological ordering — "payment" column printed before "balance"
    # Parser should detect payment > balance is wrong and swap.
    line = "Acme Bank    50,000.00   1,200.00   45,000.00   5.50%   01/01/2030"
    row = _parse_line(line)
    assert row is not None
    # After swap: balance=45000, payment=1200
    assert row.current_balance == 45_000.00
    assert row.monthly_payment == 1_200.00


def test_row_needs_two_money_values():
    assert _parse_line("Just a narrative line with one number 1,234.56") is None


def test_two_money_row_accepted_with_rate():
    line = "Chase  42,108.55  925.00  7.00%  06/30/2028"
    row = _parse_line(line)
    assert row is not None
    # 2 money values → original=None, balance=42108.55, payment=925
    assert row.original_amount is None
    assert row.current_balance == 42_108.55
    assert row.monthly_payment == 925.00
