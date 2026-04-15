"""
Anthropic client wrapper for narrative generation.

Thin adapter that conforms to the `Generator` callable contract in
`underwriteos.memo.narrative`: `Callable[[str], str]`.

Design rules:
    - Zero numeric computation. Narrative only. DSCR/BANI/ADS are
      computed by cashflow.py and passed in as formatted strings.
    - Every call is logged to an audit file so drafts are reproducible.
      The audit log captures: timestamp, prompt_version, model, prompt,
      response, token counts. Never commit this log to Git — it contains
      deal PII.
    - API key comes from env var ANTHROPIC_API_KEY. Never hardcoded.
    - Deterministic defaults: temperature 0.2, max_tokens 1024. Tuning
      is a code change, not a per-call knob.
    - Graceful degradation: if the SDK isn't installed or the key is
      missing, constructor raises with a clear message so tests and
      offline runs fail fast instead of swallowing silent stubs.

Wire-up from a run script:

    from underwriteos.memo import narrative
    from underwriteos.memo.anthropic_client import build_generator
    narrative.configure_generator(build_generator())
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Callable, Optional

# Default production model. Bump intentionally, not accidentally.
DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.2

# System prompt applied to every narrative call. Keeps the model inside
# the underwriting voice and blocks fluff/adjective drift.
_SYSTEM_PROMPT = (
    "You are a senior SBA 7(a) credit underwriter drafting sections of a "
    "bank credit memo for a lending committee. Voice: factual, terse, "
    "bank-formal. No marketing language. No adjectives like 'exciting', "
    "'promising', 'robust'. Never invent numbers, ratios, or facts not "
    "given in the prompt. If a number is needed but not provided, write "
    "'[TBD]' instead of guessing. Output the requested section only — "
    "no preamble, no sign-off, no meta commentary."
)


def _default_audit_path() -> Path:
    # Default lives under the sandbox working dir, NOT the repo.
    # Deal PII must never enter Git.
    root = Path(os.environ.get(
        "UNDERWRITEOS_AUDIT_DIR",
        "/sessions/hopeful-admiring-turing/mnt/FORGE/out/narrative_audit",
    ))
    root.mkdir(parents=True, exist_ok=True)
    return root / f"narrative_{_dt.date.today().isoformat()}.jsonl"


def build_generator(
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    audit_path: Optional[Path] = None,
    api_key: Optional[str] = None,
) -> Callable[[str], str]:
    """
    Return a Generator callable that routes prompts through the
    Anthropic Messages API.

    Raises ImportError if the `anthropic` SDK is not installed.
    Raises RuntimeError if ANTHROPIC_API_KEY is missing.
    """
    try:
        import anthropic  # type: ignore
    except ImportError as e:
        raise ImportError(
            "anthropic SDK not installed. Run: pip install anthropic"
        ) from e

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY env var not set. Export it before running, "
            "or pass api_key= to build_generator()."
        )

    client = anthropic.Anthropic(api_key=key)
    audit = audit_path or _default_audit_path()

    def _generate(prompt: str) -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        # Concatenate text blocks. Non-text blocks (tool use, etc.)
        # shouldn't occur here but we guard anyway.
        parts = []
        for block in resp.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        draft = "".join(parts).strip()

        # Audit record — append-only JSONL.
        record = {
            "ts": _dt.datetime.utcnow().isoformat() + "Z",
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt": prompt,
            "draft": draft,
            "input_tokens": getattr(resp.usage, "input_tokens", None),
            "output_tokens": getattr(resp.usage, "output_tokens", None),
            "stop_reason": getattr(resp, "stop_reason", None),
        }
        with audit.open("a") as f:
            f.write(json.dumps(record) + "\n")

        return draft

    return _generate
