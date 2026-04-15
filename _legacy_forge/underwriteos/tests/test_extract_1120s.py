"""
Validate the 1120-S extractor against the Advanced Integrated Pain & Spine
Solutions training package (2024 + 2025 returns).

Asserts both Day 3 findings:
  Finding #1 - Schedule M-1 Line 1 is preferred over 1120-S Line 22
  Finding #2 - Form 4562 Part IV Line 22 is preferred over 1120-S Line 14

PDFs are not committed. Tests skip if the training folder is not present.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from underwriteos.extract.tax_return_1120s import extract_1120s


# Allow override via env var; otherwise look in the standard local training dir.
TRAINING_DIR = Path(
    os.environ.get(
        "UNDERWRITEOS_AIP_TRAINING_DIR",
        "/sessions/hopeful-admiring-turing/aip_docs",
    )
)

PDF_2024 = TRAINING_DIR / "Tax Return 2024 for Advanced Integrated Pain and Spine Solutions LLC.pdf"
PDF_2025 = TRAINING_DIR / "biz_2025.pdf"  # decrypted with qpdf, password 23351

pytestmark = pytest.mark.skipif(
    not (PDF_2024.exists() and PDF_2025.exists()),
    reason="AIPSS training PDFs not present in this environment",
)


def test_extract_1120s_2024():
    r = extract_1120s(PDF_2024)
    assert r["ein"] == "87-0935663"
    assert r["tax_year"] == 2024
    assert r["gross_receipts"] == 195_723
    assert r["compensation_of_officers"] == 50_000
    assert r["salaries_wages"] == 10_070
    assert r["rents"] == 12_592
    assert r["interest_expense"] == 11_373
    assert r["depreciation_line_14"] == 27
    assert r["ordinary_business_income_line_22"] == 67_653
    # Finding #1 - M-1 Line 1 wins
    assert r["m1_net_income_per_books"] == 68_721
    assert r["net_income_preferred"] == 68_721
    assert r["net_income_source"] == "schedule_m1_line_1"
    # Finding #2 - Form 4562 Part IV total
    assert r["form_4562_part_iv_total"] == 27
    assert r["depreciation_source"] == "form_4562_part_iv_line_22"


def test_extract_1120s_2025():
    r = extract_1120s(PDF_2025)
    assert r["ein"] == "87-0935663"
    assert r["tax_year"] == 2025
    assert r["gross_receipts"] == 213_145
    assert r["compensation_of_officers"] == 50_000
    assert r["salaries_wages"] == 6_762
    assert r["interest_expense"] == 11_023
    assert r["ordinary_business_income_line_22"] == 69_227
    # Finding #1
    assert r["m1_net_income_per_books"] == 67_541
    assert r["net_income_preferred"] == 67_541
    assert r["net_income_source"] == "schedule_m1_line_1"
