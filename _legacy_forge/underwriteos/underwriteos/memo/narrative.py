"""
LLM narrative hooks for memo sections.

Strict boundary rules:
    - NEVER pass numeric calculations to the LLM. DSCR, BANI, ADS are
      computed by cashflow.py and referenced by value. The LLM's job
      is to frame them in prose, not to derive them.
    - ALL outputs are treated as drafts. The reviewer (Keith) must
      edit before the memo goes to committee.
    - Every prompt is deterministic and versioned — no per-deal prompt
      engineering. If a prompt needs tuning, it's a code change.
    - LLM backend is pluggable via the `generate` callable. Default
      `generate` raises — tests inject a stub. Production wires in the
      Anthropic client.

Each section builder returns a dict with:
    prompt       — the exact prompt sent to the model (for audit log)
    draft        — the model's output
    reviewer_notes — hints for the underwriter on what to double-check
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

# Bump when prompts change. Logged with every draft for reproducibility.
PROMPT_VERSION = "2026-04-08.v1"


Generator = Callable[[str], str]


def _default_generate(prompt: str) -> str:
    raise RuntimeError(
        "No LLM generator configured. Pass generate=... to the narrative "
        "builder or wire in underwriteos.memo.narrative.configure_generator()."
    )


_GENERATOR: Generator = _default_generate


def configure_generator(fn: Generator) -> None:
    """Install a process-wide LLM callable. Production wires in an
    Anthropic client wrapper; tests install a deterministic stub."""
    global _GENERATOR
    _GENERATOR = fn


@dataclass
class NarrativeDraft:
    section_key: str
    prompt: str
    draft: str
    reviewer_notes: list[str]
    prompt_version: str = PROMPT_VERSION


def _call(prompt: str, generate: Optional[Generator]) -> str:
    fn = generate or _GENERATOR
    return fn(prompt).strip()


# ---------------- Loan Purpose ----------------

def draft_loan_purpose(
    deal_name: str,
    deal_type: str,
    loan_amount: int,
    use_of_proceeds: list[dict],
    generate: Optional[Generator] = None,
) -> NarrativeDraft:
    uop_lines = "\n".join(
        f"  - {u.get('purpose', '?')}: ${u.get('amount', 0):,}"
        for u in use_of_proceeds
    )
    prompt = (
        f"Write a 2-3 sentence Loan Purpose statement for an SBA 7(a) "
        f"credit memo. Deal: {deal_name}. Type: {deal_type}. "
        f"Loan amount: ${loan_amount:,}. Use of proceeds:\n{uop_lines}\n"
        f"Be factual and terse. No marketing language. No adjectives like "
        f"'exciting' or 'promising'. Do not restate numbers the reader "
        f"can see in the Sources and Uses table."
    )
    draft = _call(prompt, generate)
    return NarrativeDraft(
        section_key="loan_purpose",
        prompt=prompt,
        draft=draft,
        reviewer_notes=[
            "Verify use-of-proceeds categories match the approved Sources & Uses table.",
            "Confirm the stated deal type matches the signed term sheet.",
        ],
    )


# ---------------- Project Summary ----------------

def draft_project_summary(
    deal_name: str,
    borrower_description: str,
    key_facts: dict,
    generate: Optional[Generator] = None,
) -> NarrativeDraft:
    facts_lines = "\n".join(f"  - {k}: {v}" for k, v in key_facts.items())
    prompt = (
        f"Write a 4-6 sentence Project Summary for an SBA credit memo. "
        f"Deal: {deal_name}. Borrower description:\n{borrower_description}\n"
        f"Key facts:\n{facts_lines}\n"
        f"Describe what the borrower does, what the project is, and why "
        f"the project makes business sense. Do not include DSCR or "
        f"financial ratios — those are in the DSCR section. Plain prose, "
        f"no bullet points, no headings."
    )
    draft = _call(prompt, generate)
    return NarrativeDraft(
        section_key="project_summary",
        prompt=prompt,
        draft=draft,
        reviewer_notes=[
            "Does the narrative match what the borrower said in the interview?",
            "Any material risk omitted? Add to Strengths & Weaknesses.",
        ],
    )


# ---------------- Strengths & Weaknesses ----------------

def draft_strengths_weaknesses(
    deal_snapshot: dict,
    generate: Optional[Generator] = None,
) -> NarrativeDraft:
    prompt = (
        "Given this SBA deal snapshot, list 3-5 STRENGTHS and 3-5 "
        "WEAKNESSES as separate bullet lists. Be specific and "
        "underwriting-focused. Strengths should be financial, "
        "operational, or structural facts. Weaknesses should be real "
        "risks a credit committee will ask about — not marketing fluff. "
        "Never invent facts not in the snapshot.\n\n"
        f"Snapshot:\n{deal_snapshot}\n\n"
        "Format:\nSTRENGTHS:\n- ...\n\nWEAKNESSES:\n- ..."
    )
    draft = _call(prompt, generate)
    return NarrativeDraft(
        section_key="strengths_weaknesses",
        prompt=prompt,
        draft=draft,
        reviewer_notes=[
            "Every weakness must have a corresponding mitigant — add to "
            "Conditions & Covenants if not already there.",
            "Remove any fluff; committees hate adjectives without facts.",
        ],
    )


# ---------------- Conditions & Covenants ----------------

def draft_conditions(
    deal_type: str,
    risk_flags: list[str],
    generate: Optional[Generator] = None,
) -> NarrativeDraft:
    flags_lines = "\n".join(f"  - {r}" for r in risk_flags) or "  (none)"
    prompt = (
        f"Draft 5-10 standard + risk-specific loan conditions for an "
        f"SBA 7(a) credit memo. Deal type: {deal_type}. "
        f"Known risk flags:\n{flags_lines}\n"
        f"Include standard items (life insurance collateral assignment, "
        f"UCC-1, personal guaranty, hazard insurance, monthly/quarterly "
        f"financial reporting) plus specific conditions that address "
        f"each risk flag above. One condition per bullet. Terse, "
        f"bank-style language."
    )
    draft = _call(prompt, generate)
    return NarrativeDraft(
        section_key="conditions_covenants",
        prompt=prompt,
        draft=draft,
        reviewer_notes=[
            "Every risk flag must have at least one condition addressing it.",
            "Check against Colony Bank's standard conditions library before finalizing.",
        ],
    )
