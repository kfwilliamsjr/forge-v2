"""
Validate the 1040 extractor against the Narayanasamy joint returns (2024+2025).

PDFs not committed. Tests skip if the training folder is missing.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from underwriteos.extract.tax_return_1040 import extract_1040


TRAINING_DIR = Path(
    os.environ.get(
        "UNDERWRITEOS_AIP_TRAINING_DIR",
        "/sessions/hopeful-admiring-turing/aip_docs",
    )
)

PDF_2024 = TRAINING_DIR / "Joint Tax Return 2024 for Ava M. Monti (Narayanasamy) and Narendren Narayanasamy.pdf"
PDF_2025 = TRAINING_DIR / "pers_2025.pdf"  # decrypted with qpdf, password 23351

pytestmark = pytest.mark.skipif(
    not (PDF_2024.exists() and PDF_2025.exists()),
    reason="Narayanasamy training PDFs not present in this environment",
)


def test_extract_1040_2024():
    r = extract_1040(PDF_2024)
    assert r["primary_ssn"] == "233-51-2045"
    assert r["tax_year"] == 2024
    assert r["wages_preferred"] == 50_000
    assert r["taxable_interest_2b"] == 2_116
    assert r["ordinary_dividends_3b"] == 2_513
    assert r["capital_gain_loss_line_7"] == -16
    assert r["agi_line_11"] == 109_289
    assert r["taxable_income_line_15"] == 76_085
    # K-1 flow through matches 2024 1120-S Line 22
    assert r["k1_flow_through"] == 67_653
    # Personal income excluding K-1 (no double count vs business cashflow)
    assert r["personal_income_ex_k1"] == 50_000 + 2_116 + 2_513 + (-16)


def test_extract_1040_2025():
    r = extract_1040(PDF_2025)
    assert r["primary_ssn"] == "233-51-2045"
    assert r["tax_year"] == 2025
    assert r["wages_preferred"] == 50_000
    assert r["taxable_interest_2b"] == 2_520
    assert r["ordinary_dividends_3b"] == 2_581
    assert r["agi_line_11"] == 124_328
    # K-1 flow through matches 2025 1120-S Line 22
    assert r["k1_flow_through"] == 69_227
    assert r["personal_income_ex_k1"] == 50_000 + 2_520 + 2_581


def test_schedule_c_absent_on_scorp_return():
    """When the 1040 has K-1 flow-through but no Schedule C, schedule_c should be None."""
    if not PDF_2024.exists():
        pytest.skip("Training PDF not present")
    r = extract_1040(PDF_2024)
    assert r["schedule_c"] is None


def test_schedule_c_detection():
    """Smoke test: _extract_schedule_c returns None for text without Schedule C."""
    from underwriteos.extract.tax_return_1040 import _extract_schedule_c
    assert _extract_schedule_c("Some random text with no Schedule C header") is None


def test_schedule_c_synthetic():
    """Synthetic Schedule C text to validate field extraction."""
    from underwriteos.extract.tax_return_1040 import _extract_schedule_c
    text = """
Schedule C (Form 1040)    Profit or Loss From Business    2022
Name of proprietor   ZEFO'S ENTERPRISES
Business code  722511
Gross receipts or sales          1a    188,300
Cost of goods sold               4     45,000
Gross income                     7    143,300
Depreciation and section 179    13     17,982
Total expenses before            28    83,038
Net profit or (loss)             31    60,262
"""
    result = _extract_schedule_c(text)
    assert result is not None
    assert result["business_name"] == "ZEFO'S ENTERPRISES"
    assert result["naics"] == "722511"
    assert result["gross_receipts"] == 188_300
    assert result["depreciation"] == 17_982
    assert result["net_profit_loss"] == 60_262
    assert result["net_income_preferred"] == 60_262
    assert result["depreciation_preferred"] == 17_982
