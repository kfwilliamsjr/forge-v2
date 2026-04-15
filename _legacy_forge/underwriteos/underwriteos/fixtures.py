"""Load deal fixtures from JSON into engine dataclasses."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from .cashflow import Debt, IncomeStatement, PersonalCashFlow


def _dec(v) -> Decimal:
    return Decimal(str(v)) if v is not None else Decimal(0)


def load_deal(path: str | Path) -> dict:
    """
    Load a JSON fixture and return a dict with engine-ready objects:
        {
            "meta": {...},
            "statements": [IncomeStatement, ...],
            "debts": [Debt, ...],
            "guarantors": [PersonalCashFlow, ...],
            "expected": {...},
        }
    """
    data = json.loads(Path(path).read_text())

    statements = [
        IncomeStatement(
            year=int(s["year"]),
            revenue=_dec(s.get("revenue", 0)),
            cogs=_dec(s.get("cogs", 0)),
            operating_expenses=_dec(s.get("operating_expenses", 0)),
            depreciation=_dec(s.get("depreciation", 0)),
            amortization=_dec(s.get("amortization", 0)),
            interest_expense=_dec(s.get("interest_expense", 0)),
            net_income=_dec(s.get("net_income", 0)),
            owner_compensation=_dec(s.get("owner_compensation", 0)),
            one_time_addbacks=_dec(s.get("one_time_addbacks", 0)),
            required_distributions=_dec(s.get("required_distributions", 0)),
        )
        for s in data["statements"]
    ]

    debts = [
        Debt(
            lender=d["lender"],
            balance=_dec(d.get("balance", 0)),
            annual_rate=_dec(d.get("annual_rate", 0)),
            term_months=int(d.get("term_months", 0)),
            rate_type=d.get("rate_type", "fixed"),
            secured_by=d.get("secured_by", ""),
            annual_payment_override=(
                _dec(d["annual_payment_override"])
                if d.get("annual_payment_override") is not None
                else None
            ),
        )
        for d in data["debts"]
    ]

    guarantors = [
        PersonalCashFlow(
            name=g["name"],
            annual_w2_income=_dec(g.get("annual_w2_income", 0)),
            other_income=_dec(g.get("other_income", 0)),
            annual_personal_debt_service=_dec(g.get("annual_personal_debt_service", 0)),
            annual_living_expenses=_dec(g.get("annual_living_expenses", 0)),
            liquid_assets=_dec(g.get("liquid_assets", 0)),
        )
        for g in data.get("guarantors", [])
    ]

    return {
        "meta": {
            "deal_name": data.get("deal_name"),
            "source_document": data.get("source_document"),
            "source_tab": data.get("source_tab"),
            "loan_type": data.get("loan_type"),
            "loan_amount": data.get("loan_amount"),
        },
        "statements": statements,
        "debts": debts,
        "guarantors": guarantors,
        "expected": data.get("expected_results", {}),
    }
