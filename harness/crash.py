#!/usr/bin/env python3
"""harness/crash.py — the crash-injection helper (S3; D-036).

Runs record_event through the command driver with SIGKILL armed at one of the
three injection points (the review §7 S3's kill matrix):
  after-begin          — transaction open, nothing written
  pre-commit           — both rows inserted, COMMIT not sent
  post-commit-pre-ack  — COMMIT confirmed, acknowledgment NOT yet emitted

Exit 2 = crashed (no ack — by design; that is the point). The DB-side effect of
killing the psql session is exactly the app process dying mid-transaction: the
server rolls the open transaction back when the connection drops.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.commands import record_event  # noqa: E402

POINTS = ("after-begin", "pre-commit", "post-commit-pre-ack")


def main() -> int:
    ap = argparse.ArgumentParser(description="crash-injection helper (S3)")
    ap.add_argument("--point", required=True, choices=POINTS)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--actor", default="owner")
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--idem-key", required=True)
    ap.add_argument("--payload", required=True)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    rc = record_event(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                      idem_key=a.idem_key, payload=a.payload, crash_at=a.point)
    if rc == 2:
        print(f"CRASHED-AT {a.point}: killed -9 (no ack emitted — by design)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
