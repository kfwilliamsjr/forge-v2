"""
Cash flow engine tests.

The Advanced Integrated Pain & Spine Solutions deal is the gold-standard
reference. The G8WAY spread for that deal produces:
    Y1 Borrower DSCR: 1.23x
    Y2 Borrower DSCR: 1.25x

These tests construct synthetic financials calibrated to hit those exact
ratios so the engine has a known-good target. When the real G8WAY values
are extracted into JSON fixtures (Day 6), this test gets replaced with
fixture-driven assertions.
"""

from decimal import Decimal
import pytest

from underwriteos.cashflow import (
    Debt,
    IncomeStatement,
    PersonalCashFlow,
    amortized_payment,
    bank_adjusted_net_income,
    borrower_dscr,
    global_dscr,
    run_cashflow,
)


def test_amortized_payment_known_value():
    # $1,699,000 SBA 7(a) at 11.50% over 25 years (300 months) — Pain & Spine deal
    pmt = amortized_payment(Decimal("1699000"), Decimal("0.1150"), 300)
    # Expected monthly payment ~ $17,279 (verify against any standard amortization calculator)
    assert Decimal("17000") < pmt < Decimal("17600"), f"Got {pmt}"


def test_amortized_payment_zero_interest():
    pmt = amortized_payment(Decimal("12000"), Decimal("0"), 12)
    assert pmt == Decimal("1000.00")


def test_bani_basic():
    stmt = IncomeStatement(
        year=2024,
        revenue=Decimal("2500000"),
        net_income=Decimal("180000"),
        interest_expense=Decimal("25000"),
        depreciation=Decimal("40000"),
        amortization=Decimal("0"),
        owner_compensation=Decimal("0"),
        one_time_addbacks=Decimal("0"),
        required_distributions=Decimal("0"),
    )
    bani = bank_adjusted_net_income(stmt)
    assert bani == Decimal("245000.00")


def test_bani_with_addbacks_and_distributions():
    stmt = IncomeStatement(
        year=2024,
        revenue=Decimal("2500000"),
        net_income=Decimal("180000"),
        interest_expense=Decimal("25000"),
        depreciation=Decimal("40000"),
        owner_compensation=Decimal("60000"),
        one_time_addbacks=Decimal("10000"),
        required_distributions=Decimal("30000"),
    )
    # 180 + 25 + 40 + 60 + 10 - 30 = 285
    assert bank_adjusted_net_income(stmt) == Decimal("285000.00")


def test_borrower_dscr_basic():
    assert borrower_dscr(Decimal("250000"), Decimal("200000")) == Decimal("1.25")


def test_borrower_dscr_zero_ads_raises():
    with pytest.raises(ValueError):
        borrower_dscr(Decimal("100"), Decimal("0"))


def test_global_dscr_basic():
    # BANI 200k + personal 80k = 280k
    # ADS 150k + personal debt 30k + living 50k = 230k
    # 280 / 230 = 1.217... → 1.22
    result = global_dscr(
        bani=Decimal("200000"),
        personal_income=Decimal("80000"),
        ads=Decimal("150000"),
        personal_debt_service=Decimal("30000"),
        living_expenses=Decimal("50000"),
    )
    assert result == Decimal("1.22")


def test_advanced_integrated_pain_target_dscrs():
    """
    Reference deal: Advanced Integrated Pain & Spine Solutions LLC
    Loan: $1,699,000 SBA 7(a) at 11.50% / 300 months
    Target Y1 DSCR: 1.23x
    Target Y2 DSCR: 1.25x

    This test uses synthetic BANI values calibrated to produce the target
    ratios when divided by the actual loan's annual debt service. When the
    real financials are extracted into a JSON fixture, replace this with
    fixture-based assertions.
    """
    debt = Debt(
        lender="Colony Bank",
        balance=Decimal("1699000"),
        annual_rate=Decimal("0.1150"),
        term_months=300,
        rate_type="variable",
        secured_by="OOCRE + business assets",
    )
    annual_ds = debt.annual_payment  # ~$207,348/yr

    # Calibrated BANI values that produce 1.23x and 1.25x
    target_y1 = Decimal("1.23")
    target_y2 = Decimal("1.25")
    bani_y1 = (annual_ds * target_y1).quantize(Decimal("0.01"))
    bani_y2 = (annual_ds * target_y2).quantize(Decimal("0.01"))

    stmts = [
        IncomeStatement(year=2025, revenue=Decimal("2800000"), net_income=bani_y1),
        IncomeStatement(year=2026, revenue=Decimal("2950000"), net_income=bani_y2),
    ]

    result = run_cashflow(
        statements=stmts,
        post_close_debts=[debt],
        guarantors=[],
        rate_shock_bps=300,
    )

    assert result.borrower_dscr_by_year[2025] == Decimal("1.23"), \
        f"Y1 DSCR should be 1.23x, got {result.borrower_dscr_by_year[2025]}"
    assert result.borrower_dscr_by_year[2026] == Decimal("1.25"), \
        f"Y2 DSCR should be 1.25x, got {result.borrower_dscr_by_year[2026]}"

    # Rate shock should produce a LOWER DSCR than the unshocked
    assert result.rate_shock_dscr_by_year[2025] < result.borrower_dscr_by_year[2025]
    assert result.rate_shock_dscr_by_year[2026] < result.borrower_dscr_by_year[2026]


def test_run_cashflow_with_guarantor():
    debt = Debt(
        lender="Test Bank",
        balance=Decimal("500000"),
        annual_rate=Decimal("0.10"),
        term_months=120,
        rate_type="fixed",
    )
    stmts = [IncomeStatement(year=2024, revenue=Decimal("1000000"), net_income=Decimal("120000"))]
    guarantor = PersonalCashFlow(
        name="Owner",
        annual_w2_income=Decimal("90000"),
        annual_personal_debt_service=Decimal("18000"),
        annual_living_expenses=Decimal("48000"),
        liquid_assets=Decimal("75000"),
    )
    result = run_cashflow(stmts, [debt], [guarantor])

    assert result.borrower_dscr_by_year[2024] > 0
    assert result.global_dscr_by_year[2024] > 0
    assert result.liquidity_ratio > 0
    assert "BANI" in result.audit[0]


def test_fixed_rate_debt_not_shocked():
    debt = Debt(
        lender="Fixed Bank",
        balance=Decimal("100000"),
        annual_rate=Decimal("0.08"),
        term_months=120,
        rate_type="fixed",
    )
    assert debt.shocked_annual_payment(300) == debt.annual_payment


def test_variable_rate_debt_is_shocked():
    debt = Debt(
        lender="Var Bank",
        balance=Decimal("100000"),
        annual_rate=Decimal("0.08"),
        term_months=120,
        rate_type="variable",
    )
    assert debt.shocked_annual_payment(300) > debt.annual_payment
