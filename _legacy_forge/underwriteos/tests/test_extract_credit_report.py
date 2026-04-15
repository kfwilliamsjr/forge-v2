"""
Validate the credit report extractor against the Narayanasamy RMCR.

Day 3 finding it must support: TOTAL row monthly_payment is the authoritative
personal debt service used in global DSCR. PFS understated by ~60% vs this.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from underwriteos.extract.credit_report import extract_credit_report


TRAINING_DIR = Path(
    os.environ.get(
        "UNDERWRITEOS_AIP_TRAINING_DIR",
        "/sessions/hopeful-admiring-turing/aip_docs",
    )
)
PDF = TRAINING_DIR / "Credit Report for Narendren Narayanasamy.pdf"

pytestmark = pytest.mark.skipif(
    not PDF.exists(),
    reason="Narayanasamy credit report PDF not present in this environment",
)


def test_extract_credit_report():
    r = extract_credit_report(PDF)

    # Identity
    assert r["applicant_name"] == "NARAYANASAMY, NARENDREN"
    assert r["applicant_ssn"] == "233-51-2045"
    assert r["applicant_dob"] == "12/16/1971"

    # Scores
    assert r["scores"]["equifax"] == 782
    assert r["primary_score"] == 782

    # Trade summary totals (the Day 3 reconciliation values)
    assert r["total_balance"] == 401_820
    assert r["total_high_credit"] == 602_597
    assert r["monthly_debt_service"] == 6_282
    assert r["annual_debt_service"] == 6_282 * 12  # 75,384

    # Category breakdown
    assert r["trades"]["mortgage"]["count"] == 5
    assert r["trades"]["mortgage"]["balance"] == 285_500
    assert r["trades"]["mortgage"]["monthly_payment"] == 2_566
    assert r["trades"]["revolving"]["count"] == 11
    assert r["trades"]["revolving"]["balance"] == 28_460
    assert r["trades"]["other_installment"]["balance"] == 74_894
    assert r["trades"]["other_installment"]["monthly_payment"] == 2_528

    # Secured/unsecured split
    assert r["secured_debt"] == 298_466
    assert r["unsecured_debt"] == 103_354

    # Utilization
    assert r["revolving_utilization_pct"] == 32
    assert r["total_debt_high_credit_pct"] == 67

    # Derogatory profile (clean)
    assert r["charge_offs"] == 0
    assert r["collections"] == 0
    assert r["bankruptcy"] == 0
    assert r["public_records"] == 0
    assert r["thirty_day_late"] == 0
    assert r["sixty_day_late"] == 0
    assert r["ninety_day_late"] == 0
    assert r["inquiries"] == 4
