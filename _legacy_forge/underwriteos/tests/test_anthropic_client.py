"""
Tests for the Anthropic client wrapper.

We never hit the real API in tests. We monkeypatch `anthropic.Anthropic`
to return a fake client whose `messages.create` returns a stub response.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest


def _install_fake_anthropic(monkeypatch, captured: dict):
    """Install a fake `anthropic` module in sys.modules."""
    fake = types.ModuleType("anthropic")

    class _Block:
        def __init__(self, text): self.text = text

    class _Usage:
        input_tokens = 123
        output_tokens = 45

    class _Resp:
        def __init__(self, text):
            self.content = [_Block(text)]
            self.usage = _Usage()
            self.stop_reason = "end_turn"

    class _Messages:
        def create(self, **kwargs):
            captured["call"] = kwargs
            return _Resp("STUB DRAFT — from fake client")

    class _Client:
        def __init__(self, api_key=None):
            captured["api_key"] = api_key
            self.messages = _Messages()

    fake.Anthropic = _Client
    monkeypatch.setitem(sys.modules, "anthropic", fake)


def test_build_generator_raises_without_api_key(monkeypatch):
    _install_fake_anthropic(monkeypatch, {})
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from underwriteos.memo.anthropic_client import build_generator
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        build_generator()


def test_build_generator_raises_without_sdk(monkeypatch):
    # Force import to fail
    monkeypatch.setitem(sys.modules, "anthropic", None)
    from underwriteos.memo import anthropic_client
    # Reload to re-trigger the import inside build_generator
    with pytest.raises(ImportError, match="anthropic SDK"):
        anthropic_client.build_generator(api_key="test")


def test_build_generator_happy_path(monkeypatch, tmp_path: Path):
    captured: dict = {}
    _install_fake_anthropic(monkeypatch, captured)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-abc")

    from underwriteos.memo.anthropic_client import build_generator
    audit = tmp_path / "audit.jsonl"
    gen = build_generator(audit_path=audit)

    out = gen("Draft a loan purpose for Mirzai Group LLC")
    assert out == "STUB DRAFT — from fake client"

    # Client was constructed with the env key
    assert captured["api_key"] == "sk-test-abc"

    # messages.create was called with the right shape
    call = captured["call"]
    assert call["model"]
    assert call["temperature"] == 0.2
    assert call["max_tokens"] == 1024
    assert call["system"].startswith("You are a senior SBA 7(a)")
    assert call["messages"] == [
        {"role": "user", "content": "Draft a loan purpose for Mirzai Group LLC"}
    ]

    # Audit record written
    lines = audit.read_text().strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["draft"] == "STUB DRAFT — from fake client"
    assert rec["input_tokens"] == 123
    assert rec["output_tokens"] == 45
    assert rec["prompt"].startswith("Draft a loan purpose")


def test_generator_integrates_with_narrative_module(monkeypatch, tmp_path: Path):
    """End-to-end: build_generator() output plugs into narrative.configure_generator()."""
    captured: dict = {}
    _install_fake_anthropic(monkeypatch, captured)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-xyz")

    from underwriteos.memo import narrative
    from underwriteos.memo.anthropic_client import build_generator

    gen = build_generator(audit_path=tmp_path / "audit.jsonl")
    narrative.configure_generator(gen)
    try:
        d = narrative.draft_loan_purpose(
            deal_name="Test LLC",
            deal_type="acquisition",
            loan_amount=500_000,
            use_of_proceeds=[{"purpose": "Business acquisition", "amount": 500_000}],
        )
        assert d.draft == "STUB DRAFT — from fake client"
        assert d.section_key == "loan_purpose"
        # Prompt that went to the fake client must contain the deal facts
        assert "Test LLC" in captured["call"]["messages"][0]["content"]
        assert "$500,000" in captured["call"]["messages"][0]["content"]
    finally:
        narrative.configure_generator(narrative._default_generate)
