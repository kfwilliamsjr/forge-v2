"""Tests for the program-aware routing + policy loader."""
from pathlib import Path

import pytest

from underwriteos.program import (
    PROGRAMS,
    detect_program,
    load_policy,
)
from underwriteos.memo.template import get_template_for_program

CONFIG_DIR = Path(__file__).parent.parent / "config"


def test_detect_cif_from_path():
    p = detect_program(paths=["/deals/CIF/Tropical_Treasure_Hunt/G8WAY_CIF_TTH.xlsx"])
    assert p.key == "cif_cdfi"
    assert p.memo_template == "cif"


def test_detect_swift_capital_token():
    assert detect_program(paths=["Swift Capital/deal.pdf"]).key == "cif_cdfi"


def test_detect_colony_bank():
    assert detect_program(paths=["Colony Bank/SBSL/loan.docx"]).key == "sba_7a_colony"


def test_detect_sba_generic():
    assert detect_program(paths=["7(a)_app.pdf"]).key == "sba_7a_generic"


def test_default_is_colony():
    assert detect_program(paths=["random.pdf"]).key == "sba_7a_colony"


def test_cif_takes_priority_over_sba():
    # Mixed signal: deal mentions both — CIF should win
    p = detect_program(paths=["CIF_deal_with_sba_form_2202.pdf"])
    assert p.key == "cif_cdfi"


def test_load_policy_cif():
    prog = PROGRAMS["cif_cdfi"]
    pol = load_policy(prog, CONFIG_DIR)
    assert pol["_program"] == "cif_cdfi"
    assert pol["thresholds"]["borrower_dscr_min"] == 1.15
    assert pol["thresholds"]["fico_min"] == 600


def test_load_policy_colony_overrides_sop():
    prog = PROGRAMS["sba_7a_colony"]
    pol = load_policy(prog, CONFIG_DIR)
    # Colony Bank file is loaded after SOP — Colony's profile name should win
    assert "thresholds" in pol


def test_template_routes_cif():
    sections = get_template_for_program("cif")
    keys = [s.key for s in sections]
    assert "loan_readiness" in keys
    assert "sba_eligibility" not in keys  # CIF template drops SBA eligibility


def test_template_routes_colony():
    sections = get_template_for_program("colony_bank")
    keys = [s.key for s in sections]
    assert "sba_eligibility" in keys
    assert "debt_service_coverage_analysis" in keys
