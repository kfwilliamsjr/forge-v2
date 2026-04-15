"""
Reconcile — deal-level gap and quality reporter.

Takes a bundle of extractor outputs (1120-S / 1040 / IRS transcript /
credit report / etc.) plus a deal meta dict, and returns:
  - a list of missing required items, keyed by deal.type
  - a list of quality warnings (null fields, stale returns, OCR-looking
    garbage values)
  - a ready/not-ready verdict

No LLM. No numeric math. Pure bookkeeping.

Deal type taxonomy:
    refi        — debt refinance, existing operating business
    expansion   — existing business adding location/equipment
    acquisition — change of ownership / business purchase
    startup     — < 2 years operating history
    cdfi        — CDFI / non-SBA deal (looser doc standards)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

DealType = Literal["refi", "expansion", "acquisition", "startup", "cdfi"]


# Per-deal-type required doc matrix. Each entry is a logical doc class
# that must appear at least once in the bundle.
_REQUIRED_BY_TYPE: dict[str, set[str]] = {
    "refi": {
        "business_returns_3yr",
        "personal_returns_2yr",
        "interim_financials",
        "debt_schedule",
        "credit_report",
        "pfs",
    },
    "expansion": {
        "business_returns_3yr",
        "personal_returns_2yr",
        "interim_financials",
        "debt_schedule",
        "credit_report",
        "pfs",
        "use_of_proceeds",
    },
    "acquisition": {
        "seller_returns_3yr",
        "buyer_personal_returns_2yr",
        "purchase_agreement",
        "business_valuation",
        "credit_report",
        "pfs",
        "use_of_proceeds",
    },
    "startup": {
        "buyer_personal_returns_2yr",
        "projections_2yr",
        "business_plan",
        "credit_report",
        "pfs",
        "use_of_proceeds",
    },
    "cdfi": {
        "business_returns_2yr",
        "interim_financials",
        "credit_report",
        "pfs",
    },
}


@dataclass
class DocItem:
    """One logical document in a deal bundle."""
    doc_class: str
    path: str
    extracted: dict[str, Any] = field(default_factory=dict)
    year: Optional[int] = None


@dataclass
class DealBundle:
    deal_name: str
    deal_type: DealType
    docs: list[DocItem] = field(default_factory=list)


@dataclass
class ReconcileReport:
    deal_name: str
    deal_type: str
    missing_docs: list[str]
    null_fields: list[str]
    warnings: list[str]
    ready: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "deal_name": self.deal_name,
            "deal_type": self.deal_type,
            "ready": self.ready,
            "missing_docs": self.missing_docs,
            "null_fields": self.null_fields,
            "warnings": self.warnings,
        }


# Critical fields by doc_class — if null, flag as gap.
_CRITICAL_FIELDS = {
    "business_returns_3yr": [
        "gross_receipts", "ordinary_business_income_line_22",
        "depreciation_preferred", "net_income_preferred",
    ],
    "business_returns_2yr": [
        "gross_receipts", "ordinary_business_income_line_22",
        "depreciation_preferred", "net_income_preferred",
    ],
    "seller_returns_3yr": [
        "gross_receipts", "ordinary_business_income_line_22",
        "depreciation_preferred",
    ],
    "personal_returns_2yr": ["agi_line_11", "total_income_line_9"],
    "buyer_personal_returns_2yr": ["agi_line_11", "total_income_line_9"],
    "credit_report": [],  # credit report has its own shape
}

# If an extractor returns an int <= OCR_NOISE_MAX it's almost certainly
# a line number bleed-through, not a real dollar value.
_OCR_NOISE_MAX = 99


def reconcile(bundle: DealBundle) -> ReconcileReport:
    required = _REQUIRED_BY_TYPE.get(bundle.deal_type, set())
    present = {d.doc_class for d in bundle.docs}
    missing = sorted(required - present)

    null_fields: list[str] = []
    warnings: list[str] = []

    for doc in bundle.docs:
        crits = _CRITICAL_FIELDS.get(doc.doc_class, [])
        for f in crits:
            val = doc.extracted.get(f)
            tag = f"{doc.doc_class}[{doc.year or '?'}].{f}"
            if val is None:
                null_fields.append(tag)
            elif isinstance(val, (int, float)) and 0 < val <= _OCR_NOISE_MAX:
                warnings.append(
                    f"{tag}={val} — suspicious small integer, likely OCR line-number bleed"
                )

        # Stale return warning (> 2 years old relative to most recent in bundle)
        years = [d.year for d in bundle.docs if d.year]
        if years and doc.year and (max(years) - doc.year) > 2:
            warnings.append(f"{doc.doc_class}[{doc.year}] is stale (>2 yrs old)")

    ready = not missing and not null_fields
    return ReconcileReport(
        deal_name=bundle.deal_name,
        deal_type=bundle.deal_type,
        missing_docs=missing,
        null_fields=null_fields,
        warnings=warnings,
        ready=ready,
    )
