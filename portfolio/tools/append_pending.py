#!/usr/bin/env python3
"""
append_pending.py — called by scheduled sweeps. Appends an inferred update
to pending_updates.json. Does NOT modify portfolio.json.

Usage:
    python3 append_pending.py \
        --deal_id AMBER_2026-04 \
        --source swift_gmail \
        --signal "Thread 2026-04-15 from Akem: approved. Forwarding to committee." \
        --proposed_stage committee \
        --proposed_next "Await committee vote" \
        --confidence 0.85

Schema per entry:
    { ts, source, deal_id, signal, proposed_stage?, proposed_next?,
      proposed_blocker?, proposed_owner?, confidence, inferred_fields:{...} }
"""
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PENDING = ROOT / "pending_updates.json"

VALID_SOURCES = {"sba_gmail", "swift_gmail", "sharefile", "supabase", "manual", "swift_sent", "sba_sent"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deal_id", required=True)
    ap.add_argument("--source", required=True, choices=sorted(VALID_SOURCES))
    ap.add_argument("--signal", required=True, help="Human-readable evidence (quote/summary)")
    ap.add_argument("--proposed_stage", default=None)
    ap.add_argument("--proposed_next", default=None)
    ap.add_argument("--proposed_blocker", default=None)
    ap.add_argument("--proposed_owner", default=None)
    ap.add_argument("--confidence", type=float, default=0.7)
    ap.add_argument("--new_deal", action="store_true", help="Flag: this deal doesn't exist yet; create on approval")
    args = ap.parse_args()

    data = json.loads(PENDING.read_text())
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "source": args.source,
        "deal_id": args.deal_id,
        "signal": args.signal,
        "confidence": args.confidence,
        "new_deal": args.new_deal,
    }
    if args.proposed_stage: entry["proposed_stage"] = args.proposed_stage
    if args.proposed_next: entry["proposed_next"] = args.proposed_next
    if args.proposed_blocker: entry["proposed_blocker"] = args.proposed_blocker
    if args.proposed_owner: entry["proposed_owner"] = args.proposed_owner

    data["pending"].append(entry)
    data["_last_sweep"] = entry["ts"]
    PENDING.write_text(json.dumps(data, indent=2))
    print(f"Queued: {args.deal_id} ({args.source}, conf {args.confidence})")


if __name__ == "__main__":
    main()
