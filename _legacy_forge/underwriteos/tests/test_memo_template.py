from underwriteos.memo import COLONY_BANK_SECTIONS, get_template, MemoSection


def test_template_has_all_aipss_sections():
    keys = {s.key for s in COLONY_BANK_SECTIONS}
    # Sanity: every critical section from the AIPSS report is present
    critical = {
        "signatures_approval", "package_summary", "borrowers_guarantors",
        "loan_terms", "loan_purpose", "project_summary", "sources_uses",
        "income_statement_analysis", "debt_service_coverage_analysis",
        "balance_sheet_analysis", "global_dscr_analysis",
        "collateral_analysis", "sba_eligibility", "strengths_weaknesses",
        "conditions_covenants",
    }
    assert critical.issubset(keys)


def test_template_ordering_stable():
    t1 = get_template()
    t2 = get_template()
    assert [s.key for s in t1] == [s.key for s in t2]


def test_refi_requires_refinance_section():
    refi = {s.key: s for s in get_template("refi")}
    assert refi["refinance"].required is True


def test_cdfi_drops_sba_sections():
    cdfi = {s.key: s for s in get_template("cdfi")}
    assert cdfi["sba_eligibility"].required is False
    assert cdfi["existing_sba_loans"].required is False
    # But core credit analysis is still required
    assert cdfi["debt_service_coverage_analysis"].required is True


def test_startup_drops_ratio_analysis():
    startup = {s.key: s for s in get_template("startup")}
    assert startup["ratio_industry_analysis"].required is False


def test_unknown_deal_type_returns_base_template():
    base = get_template()
    unknown = get_template("nonsense")
    assert [s.key for s in base] == [s.key for s in unknown]
    assert [s.required for s in base] == [s.required for s in unknown]
