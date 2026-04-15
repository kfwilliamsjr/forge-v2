"""
Real-data validation: run the cashflow engine against financials extracted
directly from the Advanced Integrated Pain & Spine Solutions G8WAY workbook.

If this test passes, the engine produces the same DSCRs as the G8WAY spreadsheet
using ONLY the underlying raw inputs (revenue, net income, interest, D&A, debt
service). No calibration. This is the proof that the math is correct.

G8WAY source: DSCR (UW) tab, Bank-Adjusted columns.
Target DSCRs: Y1 = 1.23x, Y2 = 1.25x.
"""

from decimal import Decimal
from pathlib import Path

from underwriteos.cashflow import (
    bank_adjusted_net_income,
    run_cashflow,
    total_annual_debt_service,
)
from underwriteos.fixtures import load_deal


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "advanced_integrated_pain.json"


def test_advanced_integrated_pain_real_fixture():
    deal = load_deal(FIXTURE_PATH)

    # 1. Verify total annual debt service matches the G8WAY
    ads = total_annual_debt_service(deal["debts"])
    expected_ads = Decimal(str(deal["expected"]["total_annual_debt_service"]))
    assert ads == expected_ads, f"ADS mismatch: engine={ads}, G8WAY={expected_ads}"

    # 2. Verify BANI for each year matches the G8WAY to the penny
    for stmt in deal["statements"]:
        bani = bank_adjusted_net_income(stmt)
        expected = Decimal(str(deal["expected"]["bani_by_year"][str(stmt.year)]))
        assert bani == expected, (
            f"Year {stmt.year} BANI mismatch: engine={bani}, G8WAY={expected}"
        )

    # 3. Run full cashflow and verify DSCRs round to the G8WAY values
    result = run_cashflow(
        statements=deal["statements"],
        post_close_debts=deal["debts"],
        guarantors=deal["guarantors"],
    )

    for year_str, expected_dscr in deal["expected"]["borrower_dscr_by_year"].items():
        year = int(year_str)
        actual = result.borrower_dscr_by_year[year]
        expected = Decimal(str(expected_dscr))
        assert actual == expected, (
            f"Year {year} DSCR mismatch: engine={actual}, G8WAY target={expected}"
        )


def test_fixture_metadata_loaded():
    deal = load_deal(FIXTURE_PATH)
    assert deal["meta"]["deal_name"] == "Advanced Integrated Pain & Spine Solutions LLC"
    assert deal["meta"]["loan_type"] == "sba_7a"
    assert deal["meta"]["loan_amount"] == 1699000
    assert len(deal["statements"]) == 2
    assert len(deal["debts"]) == 2
