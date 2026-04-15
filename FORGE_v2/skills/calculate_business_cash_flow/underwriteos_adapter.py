#!/usr/bin/env python3
"""
underwriteos_adapter.py — single entry point from ANY skill into the
deterministic Python math engine.

HARD RULE (per CLAUDE.md): LLMs do not do DSCR math. They call this adapter
with a JSON payload and read a JSON result. No exceptions.

Usage from shell:
    echo '{...deal_data...}' | python3 underwriteos_adapter.py
    python3 underwriteos_adapter.py path/to/deal_data.json

Input schema (minimum):
{
  "deal_id": "TARVER_2026-04",
  "business": {
    "year": 2025, "revenue": 345600, "operating_expenses": 172800,
    "depreciation": 0, "amortization": 0, "interest_expense": 0,
    "net_income": 172800, "owner_compensation": 0
  },
  "new_loan": {"principal": 350000, "annual_rate": 0.115, "term_months": 120, "rate_type": "variable"},
  "existing_debts": [],
  "personal": {"name": "Guarantor",
               "annual_w2_income": 137500,
               "other_income": 0,
               "annual_personal_debt_service": 12000,
               "annual_living_expenses": 36000,
               "liquid_assets": 0}
}

Output: CashFlowResult as JSON + policy-threshold comparisons.
"""
from __future__ import annotations
import json
import sys
from decimal import Decimal
from pathlib import Path

# mount underwriteos
HERE = Path(__file__).resolve()
UWOS = HERE.parents[3] / "_legacy_forge" / "underwriteos"
sys.path.insert(0, str(UWOS))

from underwriteos.cashflow import (  # type: ignore
    IncomeStatement, Debt, PersonalCashFlow, AffiliateEntity,
    bank_adjusted_net_income, total_annual_debt_service,
    total_shocked_annual_debt_service, borrower_dscr, global_dscr,
    liquidity_ratio, affiliate_contribution,
)

# policy thresholds (mirror cif_procedures.yaml; SBA lane uses Colony floors)
THRESHOLDS = {
    "borrower_dscr_min": Decimal("1.25"),
    "global_dscr_min": Decimal("1.10"),
    "rate_shock_bps": 300,
    "post_shock_min": Decimal("1.00"),
    "usvi_living_floor": Decimal("24000"),
}


def _d(x) -> Decimal:
    return Decimal(str(x or 0))


def run(payload: dict) -> dict:
    b = payload["business"]
    stmt = IncomeStatement(
        year=b["year"],
        revenue=_d(b["revenue"]),
        operating_expenses=_d(b.get("operating_expenses", 0)),
        depreciation=_d(b.get("depreciation", 0)),
        amortization=_d(b.get("amortization", 0)),
        interest_expense=_d(b.get("interest_expense", 0)),
        net_income=_d(b.get("net_income", 0)),
        owner_compensation=_d(b.get("owner_compensation", 0)),
        one_time_addbacks=_d(b.get("one_time_addbacks", 0)),
        required_distributions=_d(b.get("required_distributions", 0)),
        tax_allocation=_d(b.get("tax_allocation", 0)),
    )

    nl = payload["new_loan"]
    new_debt = Debt(
        lender=nl.get("lender", "new_sba_loan"),
        balance=_d(nl["principal"]),
        annual_rate=_d(nl["annual_rate"]),
        term_months=int(nl["term_months"]),
        rate_type=nl.get("rate_type", "variable"),
        annual_payment_override=(_d(nl["annual_payment_override"]) if nl.get("annual_payment_override") else None),
    )
    existing = [
        Debt(
            lender=d.get("lender", "existing"),
            balance=_d(d.get("balance", 0)),
            annual_rate=_d(d.get("annual_rate", 0)),
            term_months=int(d.get("term_months", 0) or 0),
            rate_type=d.get("rate_type", "fixed"),
            annual_payment_override=(_d(d["annual_payment_override"]) if d.get("annual_payment_override") else None),
        )
        for d in payload.get("existing_debts", [])
    ]
    debts = [new_debt] + existing

    p = payload["personal"]
    # enforce living-expense floor (HOH)
    living = max(_d(p.get("annual_living_expenses", 0)), THRESHOLDS["usvi_living_floor"])
    pcf = PersonalCashFlow(
        name=p.get("name", "Guarantor"),
        annual_w2_income=_d(p.get("annual_w2_income", 0)),
        other_income=_d(p.get("other_income", 0)),
        annual_personal_debt_service=_d(p.get("annual_personal_debt_service", 0)),
        annual_living_expenses=living,
        liquid_assets=_d(p.get("liquid_assets", 0)),
    )

    # affiliates — each is a pass-through entity the guarantor owns a share of.
    # Attributable FCF rolls into Global DSCR numerator as a first-class additive
    # (replaces the "stuff K-1 distributions into other_income" shim).
    affiliates: list[AffiliateEntity] = []
    for a in payload.get("affiliates", []):
        a_stmt_raw = a.get("stmt", {})
        a_stmt = IncomeStatement(
            year=a_stmt_raw.get("year", b["year"]),
            revenue=_d(a_stmt_raw.get("revenue", 0)),
            operating_expenses=_d(a_stmt_raw.get("operating_expenses", 0)),
            depreciation=_d(a_stmt_raw.get("depreciation", 0)),
            amortization=_d(a_stmt_raw.get("amortization", 0)),
            interest_expense=_d(a_stmt_raw.get("interest_expense", 0)),
            net_income=_d(a_stmt_raw.get("net_income", 0)),
            owner_compensation=_d(a_stmt_raw.get("owner_compensation", 0)),
            one_time_addbacks=_d(a_stmt_raw.get("one_time_addbacks", 0)),
            required_distributions=_d(a_stmt_raw.get("required_distributions", 0)),
            tax_allocation=_d(a_stmt_raw.get("tax_allocation", 0)),
        )
        a_debts = [
            Debt(
                lender=d.get("lender", "affiliate_debt"),
                balance=_d(d.get("balance", 0)),
                annual_rate=_d(d.get("annual_rate", 0)),
                term_months=int(d.get("term_months", 0) or 0),
                rate_type=d.get("rate_type", "fixed"),
                annual_payment_override=(_d(d["annual_payment_override"]) if d.get("annual_payment_override") else None),
            )
            for d in a.get("debts", [])
        ]
        affiliates.append(AffiliateEntity(
            name=a.get("name", "affiliate"),
            ownership_pct=_d(a.get("ownership_pct", 0)),
            stmt=a_stmt,
            debts=a_debts,
        ))
    aff_contrib = affiliate_contribution(affiliates) if affiliates else Decimal(0)

    bani = bank_adjusted_net_income(stmt)
    ads = total_annual_debt_service(debts)
    shocked_ads = total_shocked_annual_debt_service(debts, THRESHOLDS["rate_shock_bps"])
    bdscr = borrower_dscr(bani, ads)
    # Global numerator includes affiliate attributable FCF when provided
    gdscr = global_dscr(bani + aff_contrib, pcf.total_income, ads, pcf.annual_personal_debt_service, pcf.annual_living_expenses)
    shock_bdscr = borrower_dscr(bani, shocked_ads)
    monthly_global_debt = (ads + pcf.annual_personal_debt_service) / 12
    monthly_living = pcf.annual_living_expenses / 12
    liq = liquidity_ratio(pcf.liquid_assets, monthly_global_debt, monthly_living)

    return {
        "status": "ok",
        "deal_id": payload.get("deal_id"),
        "engine": "underwriteos.cashflow",
        "bani": str(bani),
        "affiliate_contribution": str(aff_contrib),
        "annual_debt_service": str(ads),
        "shocked_annual_debt_service": str(shocked_ads),
        "borrower_dscr": str(bdscr),
        "global_dscr": str(gdscr),
        "rate_shock_borrower_dscr": str(shock_bdscr),
        "liquidity_ratio": str(liq),
        "thresholds": {k: str(v) for k, v in THRESHOLDS.items()},
        "verdicts": {
            "borrower_dscr": "PASS" if bdscr >= THRESHOLDS["borrower_dscr_min"] else "FAIL",
            "global_dscr": "PASS" if gdscr >= THRESHOLDS["global_dscr_min"] else "FAIL",
            "rate_shock": "PASS" if shock_bdscr >= THRESHOLDS["post_shock_min"] else "FAIL",
        },
    }


def main():
    if len(sys.argv) > 1:
        payload = json.loads(Path(sys.argv[1]).read_text())
    else:
        payload = json.loads(sys.stdin.read())
    print(json.dumps(run(payload), indent=2))


if __name__ == "__main__":
    main()
