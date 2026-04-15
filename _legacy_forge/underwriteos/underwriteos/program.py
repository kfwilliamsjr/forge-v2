"""
Program-aware routing for UnderwriteOS.

A "program" is the credit framework a deal must be underwritten under.
The same engine services SBA 7(a) deals at Colony Bank AND CDFI deals
at CIF/Swift Capital — they share extractors and math, but they diverge
on which policy YAML applies, which memo template renders, and which
G8WAY sheets are authoritative.

This module is the single dispatch point. Detection is filename- and
hint-driven (cheap, deterministic). Each Program ties to:

    - a list of policy YAML files (loaded in order; later overrides earlier)
    - a memo template key
    - a primary G8WAY sheet name (DSCR (UW) for everything we've seen
      so far, but kept here so a future program can override)

Add a new program by appending to PROGRAMS and updating detect_program().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Literal, Optional

import yaml

ProgramKey = Literal[
    "sba_7a_colony",   # SBA 7(a) under Colony Bank SBSL profile
    "sba_7a_generic",  # SBA 7(a), no specific lender profile yet
    "cif_cdfi",        # Community Investment Fund VI (CIF) — Swift Capital client
    "cdfi_generic",    # Other CDFI / mission lender, baseline profile
]


@dataclass(frozen=True)
class Program:
    key: ProgramKey
    label: str
    policy_files: tuple[str, ...]   # relative to repo config/
    memo_template: str              # template registry key
    primary_g8way_sheet: str = "DSCR (UW)"
    fallback_g8way_sheets: tuple[str, ...] = (
        "Global DSCR (UW)", "Executive Summary", "Boarding Sheet",
    )


PROGRAMS: dict[ProgramKey, Program] = {
    "sba_7a_colony": Program(
        key="sba_7a_colony",
        label="SBA 7(a) — Colony Bank SBSL",
        policy_files=("rules_sba_sop_50_10.yaml", "rules_colony_bank.yaml"),
        memo_template="colony_bank",
    ),
    "sba_7a_generic": Program(
        key="sba_7a_generic",
        label="SBA 7(a) — Generic Lender",
        policy_files=("rules_sba_sop_50_10.yaml",),
        memo_template="colony_bank",
    ),
    "cif_cdfi": Program(
        key="cif_cdfi",
        label="CIF — Community Investment Fund VI",
        policy_files=("rules_cdfi_standard.yaml",),
        memo_template="cif",
    ),
    "cdfi_generic": Program(
        key="cdfi_generic",
        label="CDFI — Generic Mission Lender",
        policy_files=("rules_cdfi_standard.yaml",),
        memo_template="cif",
    ),
}


_CIF_TOKENS = ("cif", "swift capital", "treasure hunt", "festival", "vi leap")
_COLONY_TOKENS = ("colony bank", "sbsl", "colony")
_SBA_TOKENS = ("sba", "7(a)", "7a", "504")


def _any(tokens: Iterable[str], hay: str) -> bool:
    return any(t in hay for t in tokens)


def detect_program(
    paths: Iterable[str] = (),
    extra_hints: Iterable[str] = (),
) -> Program:
    """
    Decide which Program applies. Priority: CIF > Colony > SBA generic > CDFI generic.

    The CIF check fires first because every CIF deal must use CIF policy
    even if the file path also mentions SBA (e.g. an SBA-style debt
    schedule submitted to CIF).
    """
    hay = " ".join(p.lower() for p in (*paths, *extra_hints))

    if _any(_CIF_TOKENS, hay):
        return PROGRAMS["cif_cdfi"]
    if _any(_COLONY_TOKENS, hay):
        return PROGRAMS["sba_7a_colony"]
    if _any(_SBA_TOKENS, hay):
        return PROGRAMS["sba_7a_generic"]
    # Default: assume Colony Bank — that's the dominant case in production today.
    return PROGRAMS["sba_7a_colony"]


def load_policy(program: Program, config_dir: str | Path) -> dict:
    """
    Merge the program's policy YAMLs in order. Later files override
    earlier ones at the top-level key granularity (shallow merge — deeper
    merging is on the Day 11 backlog).
    """
    config_dir = Path(config_dir)
    merged: dict = {}
    for fname in program.policy_files:
        p = config_dir / fname
        if not p.exists():
            raise FileNotFoundError(f"Policy file missing: {p}")
        with open(p) as fh:
            data = yaml.safe_load(fh) or {}
        for k, v in data.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = {**merged[k], **v}
            else:
                merged[k] = v
    merged.setdefault("_program", program.key)
    return merged
