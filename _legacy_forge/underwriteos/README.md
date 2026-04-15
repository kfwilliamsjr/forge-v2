# UnderwriteOS

Bank-grade SBA 7(a) and owner-occupied CRE underwriting memo engine. Folder-watched. Deterministic math. LLM only for narrative and classification.

**V1 promise:** Drop a borrower document package in the Inbox. Ten minutes later a complete spread, DSCR/global cash flow, policy gate results, risk flags, missing-items list, and an 80%-complete credit memo land in the Outbox. Two human review checkpoints: spread and final memo.

## Status
Day 1 scaffold. Cash flow engine validated against Advanced Integrated Pain & Spine Solutions (Y1 DSCR 1.23x, Y2 DSCR 1.25x).

## Architecture
Pure-Python cash flow and policy engines. Claude API for document classification, narrative generation, and risk identification. No LLM ever touches a number.

```
ShareFile sync → Inbox/[Deal]/  →  watcher  →  pipeline  →  Outbox/[Deal]/  →  human review  →  Archive/[Deal]/
```

Pipeline stages: classify → extract → normalize → spread → cashflow → policy → risk → missing → memo → render.

## Hard rules
- Never commit borrower documents, completed memos, spreads, or anything containing PII.
- All math is deterministic Python with unit tests.
- Policy gates live in `config/*.yaml` — never hardcoded.
- Every run produces `run_log.json` for audit.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env  # add ANTHROPIC_API_KEY
```

## Running tests
```bash
pytest tests/ -v
```

## Day 1 deliverables
- Repo scaffold
- `cashflow.py` — borrower DSCR, global DSCR, liquidity, rate shock
- `tests/test_cashflow.py` — validated against Advanced Integrated Pain
- `config/rules_colony_bank.yaml` — Colony Bank SBSL profile
- `config/rules_cdfi_standard.yaml` — CIF/CDFI override profile
- `config/rules_sba_sop_50_10.yaml` — SBA hard rules

## Roadmap
14-day plan in `docs/PLAN.md`.
