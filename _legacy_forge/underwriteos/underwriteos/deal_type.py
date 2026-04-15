"""
Deal-type auto-detection from a bundle's doc set + filenames.

Rules (evaluated in order — first match wins):

    acquisition — purchase agreement OR seller tax returns present
    startup     — < 2 years business tax returns AND projections present
    refi        — refinance/payoff docs OR existing SBA loans listed
    expansion   — equipment quote/construction/lease amendment present
    cdfi        — filename/path contains 'CIF', 'CDFI', 'Swift Capital', etc.

Default: 'refi' (most common repeat business). Always returns a value —
never None — so downstream code can branch without null checks.

The detector is filename-based for speed. A second pass could open
purchase agreements and parse them, but that's not worth the cost for
v1 — the filename signal is strong enough in practice.
"""
from __future__ import annotations

from typing import Iterable, Literal

DealType = Literal["refi", "expansion", "acquisition", "startup", "cdfi"]


_CDFI_TOKENS = ("cif", "cdfi", "swift capital", "treasure hunt", "festival")
_ACQUISITION_TOKENS = (
    "purchase agreement", "purchase and sale", "bill of sale",
    "seller", "asset purchase", "letter of intent", "loi ",
)
_STARTUP_TOKENS = ("projection", "pro forma", "business plan", "pro-forma")
_REFI_TOKENS = ("payoff", "refinance", "refi ", "existing loan", "note to be refinanced")
_EXPANSION_TOKENS = (
    "equipment quote", "invoice", "lease amendment", "construction contract",
    "buildout", "tenant improvement", "ti budget",
)


def _any_in(tokens: Iterable[str], haystacks: Iterable[str]) -> bool:
    hay = " ".join(h.lower() for h in haystacks)
    return any(tok in hay for tok in tokens)


def detect_deal_type(
    paths: Iterable[str],
    doc_classes: Iterable[str] = (),
    extra_hints: Iterable[str] = (),
) -> DealType:
    """
    Infer deal type from file paths + known doc_classes + extra hints.

    Args:
        paths: filesystem paths of all deal docs (filenames carry signal).
        doc_classes: logical doc_class labels already assigned (optional).
        extra_hints: any additional strings to search (e.g. deal name).

    Returns:
        One of: cdfi | acquisition | startup | refi | expansion.
    """
    paths = list(paths)
    classes = list(doc_classes)
    hints = list(extra_hints)
    search = paths + classes + hints

    # 1. CDFI takes priority — its doc/approval standards are looser
    if _any_in(_CDFI_TOKENS, search):
        return "cdfi"

    # 2. Acquisition signal is very strong (purchase agreement)
    if _any_in(_ACQUISITION_TOKENS, search) or "seller_returns_3yr" in classes:
        return "acquisition"

    # 3. Startup: projections present AND no / short business returns
    has_projections = _any_in(_STARTUP_TOKENS, search)
    has_biz_returns = any(
        c in classes for c in ("business_returns_3yr", "business_returns_2yr")
    )
    if has_projections and not has_biz_returns:
        return "startup"

    # 4. Explicit refinance signals
    if _any_in(_REFI_TOKENS, search):
        return "refi"

    # 5. Expansion signals
    if _any_in(_EXPANSION_TOKENS, search):
        return "expansion"

    # Default
    return "refi"
