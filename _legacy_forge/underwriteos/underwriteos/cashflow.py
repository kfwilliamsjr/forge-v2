"""
Cash flow engine — pure Python, deterministic, auditable.

NEVER let an LLM touch these calculations. All math is testable and tied to
SBA SOP 50-10 and Colony Bank SBSL standards.

Formulas:
    Bank-Adjusted Net Income (BANI)
        = Net Income + Interest + Depreciation + Amortization + Owner Comp Addback
          + One-Time Addbacks - Required Distributions - Tax Allocation

    Affiliate Attributable FCF
        = ownership_pct * (Affiliate BANI - Affiliate ADS)
        Used as a first-class additive to Global DSCR numerator for owners of
        multiple pass-through entities (K-1 distributions modeled precisely).

    Annual Debt Service (ADS)
        = sum of (annual P&I) for all debts in the post-close debt schedule

    Borrower DSCR = BANI / ADS

    Global DSCR = (BANI + Personal Net Income) / (ADS + Personal Debt Service + Living Expenses)

    Liquidity Ratio = Global Liquid Assets / (Monthly Global Debt + Monthly Living Expenses)

    Rate-Shock DSCR = BANI / ADS_at_rate_plus_300bps
        Applied only to variable-rate debt. Fixed-rate debt uses original ADS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal


# ---------- helpers ----------

def _money(x) -> Decimal:
    """Coerce to Decimal with 2dp banker rounding."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _ratio(x) -> Decimal:
    """Coerce to Decimal with 2dp ratio rounding."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def amortized_payment(principal: Decimal, annual_rate: Decimal, term_months: int) -> Decimal:
    """
    Standard mortgage amortization. Returns MONTHLY payment.

    P = L * [c(1+c)^n] / [(1+c)^n - 1]
    where c = monthly rate, n = term months
    """
    p = Decimal(str(principal))
    r = Decimal(str(annual_rate))
    n = int(term_months)
    if n <= 0:
        raise ValueError("term_months must be positive")
    if r == 0:
        return _money(p / n)
    c = r / Decimal(12)
    one_plus_c_n = (Decimal(1) + c) ** n
    pmt = p * (c * one_plus_c_n) / (one_plus_c_n - Decimal(1))
    return _money(pmt)


# ---------- data classes ----------

@dataclass
class IncomeStatement:
    """One year of business financials. All values in dollars."""
    year: int
    revenue: Decimal
    cogs: Decimal = Decimal(0)
    operating_expenses: Decimal = Decimal(0)
    depreciation: Decimal = Decimal(0)
    amortization: Decimal = Decimal(0)
    interest_expense: Decimal = Decimal(0)
    net_income: Decimal = Decimal(0)
    owner_compensation: Decimal = Decimal(0)  # added back if business will not require it post-close
    one_time_addbacks: Decimal = Decimal(0)
    required_distributions: Decimal = Decimal(0)  # K-1 distributions required to cover owner taxes
    tax_allocation: Decimal = Decimal(0)  # explicit tax-reserve deduction (S-corp/LLC); separate from required_distributions


@dataclass
class Debt:
    """
    A single debt instrument in the post-close debt schedule.

    Two construction modes:
      1. From terms: provide balance + annual_rate + term_months. Payment is amortized.
      2. From lender quote: provide annual_payment_override directly. Use this when
         you have the lender's quoted debt service and don't need to recompute it.
    """
    lender: str
    balance: Decimal = Decimal(0)
    annual_rate: Decimal = Decimal(0)
    term_months: int = 0
    rate_type: Literal["fixed", "variable"] = "fixed"
    secured_by: str = ""
    annual_payment_override: Decimal | None = None  # if set, used instead of amortization

    @property
    def monthly_payment(self) -> Decimal:
        if self.annual_payment_override is not None:
            return _money(Decimal(str(self.annual_payment_override)) / Decimal(12))
        return amortized_payment(self.balance, self.annual_rate, self.term_months)

    @property
    def annual_payment(self) -> Decimal:
        if self.annual_payment_override is not None:
            return _money(Decimal(str(self.annual_payment_override)))
        return _money(self.monthly_payment * 12)

    def shocked_annual_payment(self, shock_bps: int = 300) -> Decimal:
        """Rate shock applies to variable-rate debt only."""
        if self.rate_type == "fixed":
            return self.annual_payment
        if self.annual_payment_override is not None:
            # Cannot re-amortize without terms; apply a proportional shock estimate
            # based on rate delta over current rate. Falls back to unshocked if rate unknown.
            if self.annual_rate > 0:
                shock_factor = Decimal(1) + (Decimal(shock_bps) / Decimal(10000)) / self.annual_rate
                return _money(self.annual_payment * shock_factor)
            return self.annual_payment
        shocked_rate = self.annual_rate + (Decimal(shock_bps) / Decimal(10000))
        shocked_monthly = amortized_payment(self.balance, shocked_rate, self.term_months)
        return _money(shocked_monthly * 12)


@dataclass
class PersonalCashFlow:
    """Guarantor personal income, debt, and living expenses (annual)."""
    name: str
    annual_w2_income: Decimal = Decimal(0)
    other_income: Decimal = Decimal(0)
    annual_personal_debt_service: Decimal = Decimal(0)
    annual_living_expenses: Decimal = Decimal(0)
    liquid_assets: Decimal = Decimal(0)

    @property
    def total_income(self) -> Decimal:
        return _money(self.annual_w2_income + self.other_income)


@dataclass
class CashFlowResult:
    bani_by_year: dict[int, Decimal]
    annual_debt_service: Decimal
    borrower_dscr_by_year: dict[int, Decimal]
    global_dscr_by_year: dict[int, Decimal]
    liquidity_ratio: Decimal
    rate_shock_ads: Decimal
    rate_shock_dscr_by_year: dict[int, Decimal]
    audit: list[str] = field(default_factory=list)


# ---------- engine ----------

def bank_adjusted_net_income(stmt: IncomeStatement) -> Decimal:
    """
    BANI = Net Income + Interest + Depreciation + Amortization
           + Owner Comp Addback + One-Time Addbacks - Required Distributions

    Owner comp is added back ONLY when the business will not need to pay it
    post-close (e.g., owner is taking a salary from another source, or the
    addback is justified in the credit memo).
    """
    bani = (
        stmt.net_income
        + stmt.interest_expense
        + stmt.depreciation
        + stmt.amortization
        + stmt.owner_compensation
        + stmt.one_time_addbacks
        - stmt.required_distributions
        - stmt.tax_allocation
    )
    return _money(bani)


# ---------- affiliate aggregation ----------

@dataclass
class AffiliateEntity:
    """
    A pass-through entity the guarantor owns a share of. Its attributable free
    cash flow rolls into the guarantor's Global DSCR numerator.
    """
    name: str
    ownership_pct: Decimal  # 0.0 .. 1.0
    stmt: IncomeStatement
    debts: list[Debt] = field(default_factory=list)

    @property
    def free_cash_flow(self) -> Decimal:
        """Affiliate BANI - Affiliate ADS. May be negative."""
        bani = bank_adjusted_net_income(self.stmt)
        ads = total_annual_debt_service(self.debts)
        return _money(bani - ads)

    @property
    def attributable_fcf(self) -> Decimal:
        """Owner's share of affiliate FCF."""
        return _money(Decimal(str(self.ownership_pct)) * self.free_cash_flow)


def affiliate_contribution(affiliates: list[AffiliateEntity]) -> Decimal:
    """Sum of attributable FCF across all affiliates. Negative contributions allowed."""
    return _money(sum((a.attributable_fcf for a in affiliates), Decimal(0)))


def total_annual_debt_service(debts: list[Debt]) -> Decimal:
    return _money(sum((d.annual_payment for d in debts), Decimal(0)))


def total_shocked_annual_debt_service(debts: list[Debt], shock_bps: int = 300) -> Decimal:
    return _money(sum((d.shocked_annual_payment(shock_bps) for d in debts), Decimal(0)))


def borrower_dscr(bani: Decimal, ads: Decimal) -> Decimal:
    if ads == 0:
        raise ValueError("Annual debt service is zero — DSCR undefined")
    return _ratio(bani / ads)


def global_dscr(
    bani: Decimal,
    personal_income: Decimal,
    ads: Decimal,
    personal_debt_service: Decimal,
    living_expenses: Decimal,
) -> Decimal:
    numerator = bani + personal_income
    denominator = ads + personal_debt_service + living_expenses
    if denominator == 0:
        raise ValueError("Global denominator is zero")
    return _ratio(numerator / denominator)


def liquidity_ratio(
    liquid_assets: Decimal,
    monthly_global_debt: Decimal,
    monthly_living_expenses: Decimal,
) -> Decimal:
    denom = monthly_global_debt + monthly_living_expenses
    if denom == 0:
        raise ValueError("Liquidity denominator is zero")
    return _ratio(liquid_assets / denom)


def run_cashflow(
    statements: list[IncomeStatement],
    post_close_debts: list[Debt],
    guarantors: list[PersonalCashFlow],
    rate_shock_bps: int = 300,
) -> CashFlowResult:
    """
    Full cash flow run for a deal. Pure function. No side effects.
    """
    audit: list[str] = []

    bani_by_year = {s.year: bank_adjusted_net_income(s) for s in statements}
    audit.append(f"BANI by year: {dict((y, str(v)) for y, v in bani_by_year.items())}")

    ads = total_annual_debt_service(post_close_debts)
    audit.append(f"Total post-close ADS: {ads}")

    shocked_ads = total_shocked_annual_debt_service(post_close_debts, rate_shock_bps)
    audit.append(f"Rate-shocked ADS (+{rate_shock_bps}bps): {shocked_ads}")

    borrower_dscr_by_year = {y: borrower_dscr(bani, ads) for y, bani in bani_by_year.items()}
    rate_shock_dscr_by_year = {y: borrower_dscr(bani, shocked_ads) for y, bani in bani_by_year.items()}

    total_personal_income = sum((g.total_income for g in guarantors), Decimal(0))
    total_personal_debt = sum((g.annual_personal_debt_service for g in guarantors), Decimal(0))
    total_living = sum((g.annual_living_expenses for g in guarantors), Decimal(0))
    total_liquid = sum((g.liquid_assets for g in guarantors), Decimal(0))

    global_dscr_by_year = {
        y: global_dscr(bani, total_personal_income, ads, total_personal_debt, total_living)
        for y, bani in bani_by_year.items()
    }

    monthly_global_debt = (ads + total_personal_debt) / Decimal(12)
    monthly_living = total_living / Decimal(12)
    liq = liquidity_ratio(total_liquid, monthly_global_debt, monthly_living) if (monthly_global_debt + monthly_living) > 0 else Decimal(0)

    return CashFlowResult(
        bani_by_year=bani_by_year,
        annual_debt_service=ads,
        borrower_dscr_by_year=borrower_dscr_by_year,
        global_dscr_by_year=global_dscr_by_year,
        liquidity_ratio=liq,
        rate_shock_ads=shocked_ads,
        rate_shock_dscr_by_year=rate_shock_dscr_by_year,
        audit=audit,
    )
