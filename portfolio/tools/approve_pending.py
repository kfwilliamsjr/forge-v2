#!/usr/bin/env python3
"""
approve_pending.py — apply selected pending updates into portfolio.json.

Usage:
    python3 approve_pending.py --list             # print queue
    python3 approve_pending.py --approve 0 2 3    # apply entries at those indices
    python3 approve_pending.py --reject 1         # drop entry
    python3 approve_pending.py --approve-all
    python3 approve_pending.py --clear            # purge queue

All changes log to decisions.log.jsonl with source=sync tag.
Regenerates PORTFOLIO.html after any change.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "portfolio.json"
PENDING = ROOT / "pending_updates.json"
LOG = ROOT / "decisions.log.jsonl"
REGEN = ROOT / "tools" / "regenerate_dashboard.py"


def list_pending(data):
    if not data["pending"]:
        print("Queue empty.")
        return
    for i, e in enumerate(data["pending"]):
        tag = "[NEW]" if e.get("new_deal") else "    "
        print(f"  {i:>2}  {tag} {e['deal_id']:<24} ({e['source']}, conf {e['confidence']})")
        print(f"        signal : {e['signal'][:90]}")
        if e.get("proposed_stage"):   print(f"        -> stage={e['proposed_stage']}")
        if e.get("proposed_next"):    print(f"        -> next={e['proposed_next'][:90]}")
        if e.get("proposed_blocker"): print(f"        -> blocker={e['proposed_blocker']}")
        if e.get("proposed_owner"):   print(f"        -> owner={e['proposed_owner']}")


def apply_entry(port, e):
    deal = next((d for d in port["deals"] if d["deal_id"] == e["deal_id"]), None)
    if not deal and e.get("new_deal"):
        deal = {"deal_id": e["deal_id"], "borrower": e["deal_id"], "lane": "broker",
                "stage": "intake", "decision_owner": "keith", "days_in_stage": 0,
                "last_action": e["signal"], "next_action": e.get("proposed_next", ""),
                "blocker": None, "notes": f"Auto-created by sync ({e['source']})"}
        port["deals"].append(deal)
    if not deal:
        return f"SKIP {e['deal_id']} — not found and not flagged new_deal"
    if e.get("proposed_stage"):
        deal["stage"] = e["proposed_stage"]; deal["days_in_stage"] = 0
    if e.get("proposed_next"):    deal["next_action"] = e["proposed_next"]
    if e.get("proposed_blocker"): deal["blocker"] = e["proposed_blocker"]
    if e.get("proposed_owner"):   deal["decision_owner"] = e["proposed_owner"]
    deal["last_action"] = e["signal"]
    return f"APPLIED {e['deal_id']} from {e['source']}"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--approve", nargs="+", type=int)
    g.add_argument("--reject", nargs="+", type=int)
    g.add_argument("--approve-all", action="store_true")
    g.add_argument("--clear", action="store_true")
    args = ap.parse_args()

    pending = json.loads(PENDING.read_text())

    if args.list:
        list_pending(pending); return

    if args.clear:
        pending["pending"] = []
        PENDING.write_text(json.dumps(pending, indent=2))
        print("Queue cleared."); return

    if args.reject:
        kept = [e for i, e in enumerate(pending["pending"]) if i not in set(args.reject)]
        pending["pending"] = kept
        PENDING.write_text(json.dumps(pending, indent=2))
        print(f"Rejected {len(args.reject)}. Queue: {len(kept)}."); return

    indices = list(range(len(pending["pending"]))) if args.approve_all else args.approve
    port = json.loads(PORTFOLIO.read_text())
    ts = datetime.now().isoformat(timespec="seconds")
    applied, kept = [], []
    for i, e in enumerate(pending["pending"]):
        if i in set(indices):
            result = apply_entry(port, e)
            applied.append((e, result))
        else:
            kept.append(e)
    port["_last_updated"] = ts[:10]
    PORTFOLIO.write_text(json.dumps(port, indent=2))
    pending["pending"] = kept
    PENDING.write_text(json.dumps(pending, indent=2))
    with LOG.open("a") as f:
        for e, result in applied:
            f.write(json.dumps({"ts": ts, "kind": "sync_approve", "entry": e, "result": result}) + "\n")
    for _, r in applied: print(r)
    subprocess.run([sys.executable, str(REGEN)], check=False)


if __name__ == "__main__":
    main()
