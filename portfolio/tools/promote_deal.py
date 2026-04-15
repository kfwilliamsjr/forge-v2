#!/usr/bin/env python3
"""
promote_deal.py — advance a deal's stage, log the decision, regenerate dashboard.

Usage:
    python3 promote_deal.py DEAL_ID NEW_STAGE [--note "text"] [--next "text"]

Example:
    python3 promote_deal.py AMBER_2026-04 committee --note "Final approval given" --next "Await committee vote"
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "portfolio.json"
LOG = ROOT / "decisions.log.jsonl"
REGEN = ROOT / "tools" / "regenerate_dashboard.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deal_id")
    ap.add_argument("new_stage")
    ap.add_argument("--note", default="")
    ap.add_argument("--next", dest="next_action", default="")
    ap.add_argument("--owner", default="keith")
    args = ap.parse_args()

    data = json.loads(PORTFOLIO.read_text())
    valid_stages = set(data["stages"])
    if args.new_stage not in valid_stages:
        print(f"ERROR: stage '{args.new_stage}' not in {sorted(valid_stages)}")
        sys.exit(2)

    deal = next((d for d in data["deals"] if d["deal_id"] == args.deal_id), None)
    if not deal:
        print(f"ERROR: deal_id '{args.deal_id}' not found")
        sys.exit(2)

    old_stage = deal["stage"]
    ts = datetime.now().isoformat(timespec="seconds")

    deal["stage"] = args.new_stage
    deal["days_in_stage"] = 0
    deal["last_action"] = args.note or f"Promoted {old_stage} -> {args.new_stage} at {ts}"
    if args.next_action:
        deal["next_action"] = args.next_action
    deal["decision_owner"] = args.owner
    deal["blocker"] = None

    data["_last_updated"] = ts[:10]
    PORTFOLIO.write_text(json.dumps(data, indent=2))

    with LOG.open("a") as f:
        f.write(json.dumps({
            "ts": ts, "deal_id": args.deal_id,
            "from": old_stage, "to": args.new_stage,
            "note": args.note, "next": args.next_action,
        }) + "\n")

    print(f"{args.deal_id}: {old_stage} -> {args.new_stage}  [logged]")
    subprocess.run([sys.executable, str(REGEN)], check=False)


if __name__ == "__main__":
    main()
