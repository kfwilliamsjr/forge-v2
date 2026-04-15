# operations/references — mirror of Keith-owned interpretations of client source docs

**Pattern:**
- Client source docs (CIF P&P DOCX, Grant Guidelines PDF) stay in `~/Desktop/Swift Capital Underwriting/Credit Policy/` as read-only client archives.
- Keith-owned interpretations (MD files he wrote) mirror HERE so they're contract-portable. If a client contract ends, the interpretation stays with Keith.
- The compiled operational truth lives in `FORGE_v2/policy/*.yaml`. Skills read the YAML only.

**Mirror on next Claude Code session (one command):**

```bash
cp "$HOME/Desktop/Swift Capital Underwriting/Credit Policy/CIF_UNDERWRITING_PROCEDURES.md" \
   "$HOME/Desktop/SBA_Lending_Claude_MD/Agentic_Overhaul/operations/references/CIF_UNDERWRITING_PROCEDURES.md"
```

Run again whenever you update your interpretation in the Swift folder.

**Provenance index:** `FORGE_v2/policy/policy_sources.yaml` — lists every source doc + YAML it compiled into + last sync date.
