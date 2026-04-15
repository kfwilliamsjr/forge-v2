---
name: extract_cif_financials
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 1-extraction
depends_on: [generate_cif_deal_data]
policy_refs: [policy/cif_procedures.yaml]
---

# SKILL: extract_cif_financials

## Layer 1 — Trigger Description
Use to parse business tax returns (1120-S, Schedule C, 1065), P&Ls, and bank statements into structured financial data for a CIF underwriting package. Outputs typed fields consumed by `calculate_business_cash_flow`.

## Layer 2 — Negative Trigger
- Do NOT use for personal tax returns (use `extract_personal_financials`).
- Do NOT extract from unsigned / draft tax returns — must be signed or e-filed confirmation.
- Do NOT extract from photographs of returns — PDF only (OCR quality requirement).
- Do NOT infer missing line items. If Box X is blank, output null; let downstream decide.

## Layer 3 — Input Schema
| Field | Type | Required |
|-------|------|----------|
| deal_id | string | Yes |
| tax_return_files | list[file] | Yes |
| entity_type | enum | Yes |
| tax_years_required | list[int] | Yes |

## Layer 4 — Procedure

### Step 1 — Classify each file
For each file in `tax_return_files`, identify form type by header text:
- "Form 1120-S" → S-Corp return
- "Form 1120" → C-Corp return
- "Form 1065" → Partnership return
- "Schedule C" → Sole Proprietorship (attached to 1040)
- "Form 1040" → Personal (reject — wrong skill; route to `extract_personal_financials`)

### Step 2 — Validate signature/efile
HALT if form shows "DRAFT" watermark, no signature line populated, and no e-file confirmation stamp. Swift Capital policy: unsigned returns do not enter the UW package.

### Step 3 — Extract per-form fields

**1120-S (S-Corp):**
| Field | Form Location |
|---|---|
| gross_revenue | Line 1a (or 1c if returns+allowances) |
| cogs | Line 2 |
| compensation_officers | Line 7 |
| salaries_wages | Line 8 |
| rent | Line 11 |
| taxes_licenses | Line 12 |
| interest_expense | Line 13 |
| depreciation | Line 14 |
| other_deductions | Line 19 |
| total_deductions | Line 20 |
| ordinary_business_income | Line 21 |

**Schedule C (Sole Prop):**
| Field | Form Location |
|---|---|
| gross_revenue | Line 1 |
| cogs | Line 4 |
| gross_profit | Line 7 |
| total_expenses | Line 28 |
| depreciation | Line 13 |
| interest_expense | Lines 16a + 16b |
| owner_draw | Line 26 (wages not to self; this is informational) |
| net_profit_loss | Line 31 |

**1065 (Partnership):**
| Field | Form Location |
|---|---|
| gross_revenue | Line 1a |
| cogs | Line 2 |
| depreciation | Line 16a |
| interest_expense | Line 15 |
| ordinary_business_income | Line 22 |

### Step 4 — Source attribution (MANDATORY)
Every extracted numeric value MUST include `source: "<filename>#p<page>L<line>"`. If extraction fails for a line, output `null` with `source_attempted` and `extraction_error`. NEVER fabricate. NEVER interpolate from other lines.

### Step 5 — Cross-check with bank statements
If bank statements included, sum 12 trailing months of deposits. If tax return gross_revenue diverges from bank deposits by >20%, emit flag `revenue_bank_discrepancy` with both figures. Do NOT adjust tax return figures — flag only.

### Step 6 — Return structured object
```json
{
  "deal_id": "...",
  "entity_type": "...",
  "tax_years": [
    {
      "year": 2024,
      "form": "1120-S",
      "fields": {"gross_revenue": {"value": 487500, "source": "Tax_2024.pdf#p1L1a"}, ...},
      "extraction_completeness": 0.92,
      "flags": ["revenue_bank_discrepancy"]
    }
  ]
}
```

### Step 7 — Write audit entry
Log: skill, deal_id, file hashes, extraction_completeness per year, flag list.

## Layer 5 — Output Schema
Structured financial object per tax year per entity. All values have source attribution.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.9.0-draft | 2026-04-15 | Stub. Legacy cif-cash-flow did extraction inline — this separates it per atomic law. |
