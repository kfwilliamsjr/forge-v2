# Golden Dataset — FORGE v2
*Created: 2026-04-15*

Per Master Build Guide: "Build a set of 10–20 loan files where you already know the correct answer. Run every new or updated skill against this dataset before it touches live files. This is the single highest-leverage QA activity available to a non-technical owner."

## Target composition (guide recommendation)
- 25% clean approvals
- 25% clean declines
- 30% borderline files
- 20% edge cases

## Candidate deals to lock as golden
From existing completed work:

| # | Deal | Source | Expected Verdict | Category |
|---|------|--------|------------------|----------|
| 1 | Advanced Integrated Pain & Spine | `knowledge-base/sample-deals/` | APPROVE | Clean approval (medical, CRE-secured) |
| 2 | Mirzai | `UNDERWRITING_V1_START_HERE/` | TBD | From CIF archive |
| 3 | TTH | Swift Capital/Deals | APPROVE | Clean approval |
| 4 | Heavy Highway | `UNDERWRITING_V1_START_HERE/` | TBD | From CIF archive |
| 5 | Elite Cargo | `UNDERWRITING_V1_START_HERE/` | TBD | From CIF archive |
| 6 | Tallahassee | `UNDERWRITING_V1_START_HERE/` | TBD | From CIF archive |
| 7 | AIPSS | `UNDERWRITING_V1_START_HERE/` | APPROVE | Clean approval |
| 8 | Amber Alexander | Swift Capital/Deals | FLAG/CONDITIONAL | Festival Loan borderline |
| 9 | Brown/Krystal (Tier 4, BK) | Broker pipeline | DECLINE + refer | Clean decline (MCA-adjacent) |
| 10 | (TBD acquisition) | BizBuySell mining | TBD | Edge case |

## Structure per deal
```
golden/deal_01_aipss/
├── inputs/
│   ├── tax_return_2024.pdf (REDACTED — PII removed)
│   ├── bank_statements_3mo.pdf (REDACTED)
│   └── intake_form.json
├── expected_outputs/
│   ├── cash_flow.json (expected structured result)
│   ├── grid_match.json (expected verdict)
│   └── memo_narrative_key_figures.json (expected numbers in memo)
└── provenance.md (what deal this was, when underwritten, final outcome)
```

## PII handling for golden files
Per CLAUDE.md retention policy, borrower PII must be deleted 30 days post-decision. Golden dataset requires SYNTHETIC or REDACTED versions of source docs. Do NOT include real SSNs, account numbers, or full PFS details. Replace with realistic but fake values that preserve the underwriting math.

## QA protocol (Phase 4)
1. Whenever a skill is modified, run it against all golden inputs.
2. Compare actual outputs to expected outputs field-by-field.
3. Accuracy target: 100% on calculation skills, >98% on extraction, >95% on drafting.
4. Any regression = block promotion to production. Fix skill, re-test.

## Status — 2026-04-15 (Session 3)

**Operational.** First three fixtures locked. Harness green 16/16.

### Built
- `fixtures/aipss/input.json` + `expected/aipss.json` — CRE-secured medical expansion, $1.699M
- `fixtures/mirzai/input.json` + `expected/mirzai.json` — CIF regular loan, multi-owner S-Corp, $175K
- `fixtures/amber_alexander/input.json` + `expected/amber_alexander.json` — Festival microloan, $12K
- `tools/run_golden.py` — deterministic regression harness, ANSI output, exit 0/1/2

### Run it
```bash
cd Agentic_Overhaul/FORGE_v2/golden
python3 tools/run_golden.py                 # all fixtures
python3 tools/run_golden.py --fixture aipss # single
```

### What's verified vs. structural-only
Harness runs DETERMINISTIC skills end-to-end (DSCR math, commission, character screen). Skills with LLM-generated narrative (memo, festival report, grant summary) and extraction skills requiring real PDFs are marked `STRUCTURAL_ONLY` — verified via live run in Session 4.

### Known limitation
Current `expected/*.json` numbers were set to match the pure-Python runner's math during Session 3, not reconciled to the actual signed credit memos. Before promoting to production QA gate, reconcile each expected file against the signed memo values so the harness enforces the real underwritten truth, not the runner's self-agreement.

### Remaining fixtures to add
- [ ] TTH — Swift Capital, clean approval reference
- [ ] Heavy Highway — CIF archive, edge case
- [ ] Elite Cargo — CIF archive
- [ ] Brown/Krystal Tier 4 BK decline — clean decline with referral-out
- [ ] A BizBuySell acquisition edge case

### Remaining wiring
- [ ] Replace inline Python math in runner with calls into `underwriteos.cashflow` functions (single source of truth for arithmetic)
- [ ] Add structural verifier for DOCX/XLSX outputs (section headers, required cells)
- [ ] Git pre-commit hook: any `.md` edit under `skills/` re-runs the harness
