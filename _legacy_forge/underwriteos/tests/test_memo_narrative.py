import pytest

from underwriteos.memo import narrative as nar


def _stub_generator(capture: list[str]):
    def gen(prompt: str) -> str:
        capture.append(prompt)
        return f"STUBBED DRAFT for prompt len={len(prompt)}"
    return gen


def test_default_generator_raises_without_config():
    with pytest.raises(RuntimeError, match="No LLM generator configured"):
        nar.draft_loan_purpose(
            deal_name="Test", deal_type="refi", loan_amount=100_000,
            use_of_proceeds=[],
        )


def test_loan_purpose_prompt_structure():
    captured = []
    d = nar.draft_loan_purpose(
        deal_name="Mirzai Group LLC",
        deal_type="acquisition",
        loan_amount=310_000,
        use_of_proceeds=[
            {"purpose": "Business acquisition", "amount": 300_000},
            {"purpose": "Working capital", "amount": 10_000},
        ],
        generate=_stub_generator(captured),
    )
    assert len(captured) == 1
    prompt = captured[0]
    assert "Mirzai Group LLC" in prompt
    assert "$310,000" in prompt
    assert "$300,000" in prompt
    assert "acquisition" in prompt
    assert "SBA 7(a)" in prompt
    assert d.section_key == "loan_purpose"
    assert d.prompt_version  # versioned
    assert d.draft.startswith("STUBBED DRAFT")
    assert len(d.reviewer_notes) >= 2


def test_project_summary_includes_facts():
    cap = []
    d = nar.draft_project_summary(
        deal_name="Mirzai Group LLC",
        borrower_description="Food service operator purchasing existing restaurant.",
        key_facts={"NAICS": "722513", "Seller": "Munchies LLC", "Purchase Price": "$310,000"},
        generate=_stub_generator(cap),
    )
    prompt = cap[0]
    assert "Munchies LLC" in prompt
    assert "722513" in prompt
    assert "bullet" not in prompt.lower() or "no bullet" in prompt.lower()
    assert d.section_key == "project_summary"


def test_strengths_weaknesses_format_instruction():
    cap = []
    nar.draft_strengths_weaknesses(
        deal_snapshot={"revenue": 757_140, "dscr": 1.35, "credit_score": 680},
        generate=_stub_generator(cap),
    )
    prompt = cap[0]
    assert "STRENGTHS" in prompt
    assert "WEAKNESSES" in prompt
    assert "757140" in prompt or "757,140" in prompt or "revenue" in prompt


def test_conditions_addresses_risk_flags():
    cap = []
    d = nar.draft_conditions(
        deal_type="acquisition",
        risk_flags=["New owner — no direct industry experience", "Seller note subordination required"],
        generate=_stub_generator(cap),
    )
    prompt = cap[0]
    assert "acquisition" in prompt
    assert "Seller note subordination" in prompt
    assert "No direct industry experience".lower() in prompt.lower()
    assert d.section_key == "conditions_covenants"


def test_configure_generator_installs_globally():
    cap = []
    nar.configure_generator(_stub_generator(cap))
    try:
        d = nar.draft_loan_purpose(
            deal_name="X", deal_type="refi", loan_amount=50_000, use_of_proceeds=[],
        )
        assert d.draft.startswith("STUBBED DRAFT")
    finally:
        # Reset to avoid polluting other tests
        nar.configure_generator(nar._default_generate)
