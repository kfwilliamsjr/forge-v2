#!/usr/bin/env python3
"""
regenerate_dashboard.py — reads portfolio.json, writes PORTFOLIO.html.

Single HTML file, no server, opens in browser from desktop. Top section =
"NEEDS YOU TODAY" (decision_owner == 'keith'). Below = full pipeline by stage.

Usage:
    python3 regenerate_dashboard.py
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # portfolio/
PORTFOLIO = ROOT / "portfolio.json"
PENDING = ROOT / "pending_updates.json"
OUT = ROOT / "PORTFOLIO.html"

STAGE_COLORS = {
    "intake":         "#94a3b8",
    "spreads_ready":  "#fbbf24",
    "uw_complete":    "#fbbf24",
    "memo_draft":     "#fb923c",
    "memo_final":     "#f97316",
    "committee":      "#a78bfa",
    "decision":       "#818cf8",
    "closing":        "#4ade80",
    "purge":          "#64748b",
}

LANE_BADGE = {
    "sba_broker":    "SBA BROKER",
    "broker":        "BROKER",
    "cif_uw":        "CIF UW",
    "cif_festival":  "CIF FESTIVAL",
    "cif_grant":     "CIF GRANT",
}


def age_class(days: int | None) -> str:
    if days is None:
        return ""
    if days <= 3:
        return "age-fresh"
    if days <= 10:
        return "age-warm"
    return "age-stale"


def fmt_money(x):
    if x is None:
        return "—"
    return f"${x:,.0f}"


def render(data: dict) -> str:
    deals = data["deals"]
    needs_keith = [d for d in deals if d.get("decision_owner") == "keith"]
    by_stage: dict[str, list] = {s: [] for s in data["stages"]}
    for d in deals:
        by_stage.setdefault(d["stage"], []).append(d)

    updated = data.get("_last_updated", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    def deal_row(d):
        dscr = d.get("bdscr_y1")
        dscr_txt = f"{dscr:.2f}x" if dscr else "—"
        gd = d.get("global_dscr_y1")
        gd_txt = f"{gd:.2f}x" if gd else "—"
        lane = LANE_BADGE.get(d.get("lane", ""), d.get("lane", ""))
        blocker = f'<span class="blocker">{d["blocker"]}</span>' if d.get("blocker") else ""
        return f"""
        <tr class="{age_class(d.get('days_in_stage'))}">
          <td><b>{d['borrower']}</b><br><span class="sub">{d['deal_id']}</span></td>
          <td><span class="lane">{lane}</span></td>
          <td>{fmt_money(d.get('loan_amount'))}</td>
          <td>{dscr_txt} / {gd_txt}</td>
          <td>{d.get('days_in_stage','—')}d</td>
          <td>{d.get('last_action','')}</td>
          <td><b>{d.get('next_action','')}</b><br>{blocker}</td>
        </tr>"""

    needs_html = "".join(deal_row(d) for d in needs_keith) or '<tr><td colspan="7" class="empty">Nothing waiting on you. Good.</td></tr>'

    # pending updates from sweeps
    pending_html = ""
    try:
        pend = json.loads(PENDING.read_text()).get("pending", [])
    except Exception:
        pend = []
    if pend:
        rows = ""
        for i, e in enumerate(pend):
            tag = '<span class="new-tag">NEW</span>' if e.get("new_deal") else ""
            proposals = []
            if e.get("proposed_stage"):   proposals.append(f"stage→<b>{e['proposed_stage']}</b>")
            if e.get("proposed_owner"):   proposals.append(f"owner→<b>{e['proposed_owner']}</b>")
            if e.get("proposed_blocker"): proposals.append(f"blocker=<b>{e['proposed_blocker']}</b>")
            if e.get("proposed_next"):    proposals.append(f"next: {e['proposed_next'][:80]}")
            rows += f"""<tr>
              <td>{i}</td>
              <td>{tag}<b>{e['deal_id']}</b></td>
              <td><span class="lane">{e['source']}</span></td>
              <td>{e['confidence']:.2f}</td>
              <td>{e['signal'][:120]}</td>
              <td>{'<br>'.join(proposals)}</td>
            </tr>"""
        pending_html = f"""
        <div class="pending">
          <h2>PENDING SYNC UPDATES ({len(pend)}) — review &amp; approve</h2>
          <div class="sub">Approve: <code>python3 portfolio/tools/approve_pending.py --approve 0 1 2</code> &middot; Reject: <code>--reject N</code> &middot; All: <code>--approve-all</code></div>
          <table><thead><tr>
            <th>#</th><th>Deal</th><th>Source</th><th>Conf</th><th>Signal</th><th>Proposed change</th>
          </tr></thead><tbody>{rows}</tbody></table>
        </div>"""

    stage_sections = []
    for stage in data["stages"]:
        deals_in = by_stage.get(stage, [])
        if not deals_in:
            continue
        color = STAGE_COLORS.get(stage, "#888")
        rows = "".join(deal_row(d) for d in deals_in)
        stage_sections.append(f"""
        <div class="stage-card">
          <h3 style="border-left:4px solid {color};">{stage.upper().replace('_',' ')} <span class="count">{len(deals_in)}</span></h3>
          <table><thead><tr>
            <th>Borrower</th><th>Lane</th><th>Loan</th><th>BDSCR/GDSCR</th><th>Age</th><th>Last</th><th>Next</th>
          </tr></thead><tbody>{rows}</tbody></table>
        </div>""")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>SBA Lending Network — Portfolio</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin:0; padding:20px; background:#0b1220; color:#e6edf3; }}
  h1 {{ color:#2E8B8B; margin:0 0 4px; font-size:26px; }}
  .sub {{ color:#8b949e; font-size:12px; }}
  .hero {{ background:linear-gradient(90deg,#7c2d12,#b45309); border-radius:10px; padding:18px; margin:16px 0 22px; border:2px solid #f59e0b; }}
  .hero h2 {{ margin:0 0 10px; color:#fde68a; font-size:18px; }}
  .stage-card {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:14px 18px; margin-bottom:14px; }}
  .stage-card h3 {{ margin:0 0 10px; padding-left:10px; color:#e6edf3; font-size:15px; }}
  .count {{ background:#2E8B8B; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px; margin-left:6px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th, td {{ text-align:left; padding:8px; border-bottom:1px solid #30363d; vertical-align:top; }}
  th {{ color:#2E8B8B; font-size:11px; text-transform:uppercase; }}
  .lane {{ background:#0d1117; padding:2px 6px; border-radius:4px; font-size:10px; color:#79c0ff; }}
  .blocker {{ background:#ef4444; color:#fff; padding:2px 6px; border-radius:4px; font-size:10px; display:inline-block; margin-top:4px; }}
  .age-fresh td {{ background:rgba(74,222,128,0.04); }}
  .age-warm td {{ background:rgba(251,191,36,0.04); }}
  .age-stale td {{ background:rgba(239,68,68,0.08); }}
  .empty {{ text-align:center; color:#4ade80; font-style:italic; padding:20px; }}
  .pending {{ background:#1e293b; border:2px solid #38bdf8; border-radius:10px; padding:16px; margin:16px 0 22px; }}
  .pending h2 {{ margin:0 0 6px; color:#38bdf8; font-size:16px; }}
  .pending code {{ background:#0d1117; padding:2px 6px; border-radius:3px; color:#79c0ff; font-size:11px; }}
  .new-tag {{ background:#4ade80; color:#000; padding:1px 5px; border-radius:3px; font-size:10px; margin-right:6px; font-weight:700; }}
  .meta {{ color:#8b949e; font-size:11px; margin-top:20px; text-align:right; }}
</style></head><body>
<h1>SBA Lending Network — Live Portfolio</h1>
<div class="sub">State machine v{data.get('_schema_version','1.0.0')} &middot; file last updated {updated} &middot; dashboard regenerated {now}</div>

<div class="hero">
  <h2>NEEDS YOU TODAY ({len(needs_keith)})</h2>
  <table><thead><tr>
    <th>Borrower</th><th>Lane</th><th>Loan</th><th>BDSCR/GDSCR</th><th>Age</th><th>Last</th><th>Next</th>
  </tr></thead><tbody>{needs_html}</tbody></table>
</div>

{pending_html}

{''.join(stage_sections)}

<div class="meta">Source: portfolio/portfolio.json &middot; Regenerated by regenerate_dashboard.py</div>
</body></html>"""


def main():
    data = json.loads(PORTFOLIO.read_text())
    OUT.write_text(render(data))
    needs = sum(1 for d in data["deals"] if d.get("decision_owner") == "keith")
    print(f"Wrote {OUT}  ({len(data['deals'])} deals, {needs} need Keith)")


if __name__ == "__main__":
    main()
