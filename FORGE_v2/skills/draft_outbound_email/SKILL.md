---
name: draft_outbound_email
version: 1.0.0
last_updated: 2026-04-15
owner: Keith Williams
status: production
tier: 6-comms
depends_on: []
policy_refs: [policy/email_voice_rules.yaml]
---

# SKILL: draft_outbound_email

## Layer 1 — Trigger Description
Use when Keith asks to draft an outbound email from a SBA Lending Network or Swift Capital account. Produces an HTML email draft with the correct signature, brand styling, and Keith's voice. Always saves as DRAFT — never auto-sends.

## Layer 2 — Negative Trigger
- Do NOT auto-send. Every output is a draft awaiting Keith's review.
- Do NOT use for Swift Capital emails via the Gmail MCP — Swift uses Chrome MCP only (see `policy/email_voice_rules.yaml → account_routing`).
- Do NOT include em-dashes (—). Use regular hyphens or rewrite.
- Do NOT use AI-tell phrases: "I'd be happy to", "I hope this email finds you well", "Please don't hesitate to reach out", "I wanted to circle back".
- Do NOT omit the signature block. Every email includes it.
- Do NOT send emails to borrower with PII (full SSN, account numbers) in the body.
- Do NOT use plain text. Every draft is `contentType: "text/html"`.

## Layer 3 — Input Schema
| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| from_account | enum | Yes | user | `"sba"` (keith@sbalendingnetwork.com) \| `"swift"` (keith@swiftcapitaloptions.com) \| `"personal"` (keithfwilliamsjr@gmail.com) |
| to_recipients | list[string] | Yes | user | Valid email addresses |
| cc_recipients | list[string] | No | user | |
| bcc_recipients | list[string] | No | user | |
| subject | string | Yes | user or skill | No em-dashes |
| purpose | enum | Yes | user | `"doc_request"` \| `"introduction"` \| `"follow_up"` \| `"deal_update"` \| `"memo_approval"` \| `"prospect_outreach"` \| `"general"` |
| key_points | list[string] | Yes | user | Bullet points the email must convey |
| attachments | list[file] | No | user | Absolute paths |
| cta_link | string | No | user | Defaults to Cal.com if purpose in [prospect_outreach, introduction] |

## Layer 4 — Procedure

1. Validate inputs per Layer 3. HALT if missing.
2. Route account → MCP based on `from_account`:
   - `"sba"` or `"personal"` → Gmail MCP (`gmail_create_draft`)
   - `"swift"` → Chrome MCP (never Gmail MCP — hard rule from CLAUDE.md)
3. Load voice rules from `policy/email_voice_rules.yaml`:
   - Banned phrases list (apply during drafting)
   - Signature HTML per account
   - Brand color tokens (#C8922A gold, #1B2E4B navy for SBA account)
4. Draft the body following this structure:
   - Opening: one sentence, direct, name-first. No "I hope..."
   - Body: 1-3 short paragraphs covering `key_points` in order given
   - CTA: if applicable, link styled in brand gold. Cal.com URL for SBA prospect outreach: `https://cal.com/keith-williams-qeicz8/30min`
   - Closing: "Best," or "Thanks," — never "Warm regards"
5. Append the full HTML signature block for `from_account`.
6. Run AI-tell check: scan body for banned phrases from policy YAML. If found, rewrite and log the substitution.
7. Run em-dash check: search body+subject for `—`. If found, replace with hyphen or rewrite.
8. Run PII check: scan body for patterns matching full SSN (`\d{3}-\d{2}-\d{4}`) or account numbers (8+ consecutive digits). Flag if found, HALT.
9. Create draft via correct MCP. Capture draft_id.
10. Log to audit: from_account, recipients, subject, purpose, draft_id, banned-phrase substitutions made, timestamp.
11. Return output per Layer 5.

## Layer 5 — Output Schema
```json
{
  "status": "ok" | "halt" | "flag",
  "skill": "draft_outbound_email",
  "version": "1.0.0",
  "timestamp": "ISO",
  "from_account": "sba",
  "draft_id": "gmail_draft_abc123",
  "subject": "...",
  "to_recipients": ["..."],
  "mcp_used": "gmail" | "chrome",
  "substitutions_made": [{"phrase": "I'd be happy to", "replaced_with": "Glad to"}],
  "pii_flags": [],
  "audit_ref": "audit/comms.jsonl#line{n}",
  "review_link": "https://mail.google.com/mail/u/0/#drafts/..."
}
```

If `status: halt`:
```json
{"status":"halt","reason":"pii_detected","details":"Body contains pattern matching SSN. Remove before drafting."}
```

## Examples

### Example 1 — SBA prospect outreach
**Input:** from_account=sba, purpose=prospect_outreach, to=christina@example.com, key_points=["Saw your listing on BizBuySell", "SBA 7(a) could cover 90% of purchase price", "30-min call to walk through your options"].
→ Drafts with Cal.com CTA, gold-styled link, SBA signature, no em-dashes, no "I hope..."
→ Status: ok | mcp_used: gmail

### Example 2 — Swift Capital memo to committee
**Input:** from_account=swift, to=[pat.morris@cifvi.org, ronnie.johnson@cifvi.org], cc=[akem.durand@cifvi.org, nikky.cole@cifvi.org], attachments=[memo.docx, memo.pdf, cashflow.xlsx].
→ Routes via Chrome MCP (not Gmail)
→ Status: ok | mcp_used: chrome

### Example 3 — HALT on PII
**Input:** key_points contains "borrower SSN is 123-45-6789"
→ PII check catches pattern
→ Status: halt | reason: pii_detected

## Changelog
| Version | Date | Change | Approved by |
|---------|------|--------|-------------|
| 1.0.0 | 2026-04-15 | Initial version. Supersedes legacy email-drafter. Adds account routing (Gmail vs Chrome MCP), PII check, em-dash check, audit logging. | Keith Williams (pending) |
