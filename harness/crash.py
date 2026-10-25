#!/usr/bin/env python3
"""harness/crash.py — the crash-injection helper (S3; extended to P3-01).

Runs a command through the kernel driver with SIGKILL armed at one of the
three injection points: after-begin (nothing written) / pre-commit (rows
inserted, COMMIT not sent) / post-commit-pre-ack (COMMIT confirmed, the ack
NOT yet emitted — §1.6's lost-ack step). Exit 2 = crashed (no ack, by design);
the server rolls the open transaction back when the connection drops.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.commands import record_event, import_source, create_highlight  # noqa: E402

POINTS = ("after-begin", "pre-commit", "post-commit-pre-ack")


def main() -> int:
    ap = argparse.ArgumentParser(description="crash-injection helper (S3 + P3-01)")
    ap.add_argument("--command", default="record_event",
                    choices=["record_event", "import_source", "create_highlight"])
    ap.add_argument("--point", required=True, choices=POINTS)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--actor", default="owner")
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--idem-key", required=True)
    # record_event's payload / import_source's file shape / create_highlight's target
    ap.add_argument("--payload", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--file", default=None)
    ap.add_argument("--media-type", default="text/plain")
    ap.add_argument("--source-id", default=None)
    ap.add_argument("--start", default=None, type=int)
    ap.add_argument("--end", default=None, type=int)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    if a.command == "record_event":
        rc = record_event(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                          idem_key=a.idem_key, payload=a.payload, crash_at=a.point)
    elif a.command == "import_source":
        rc = import_source(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, title=a.title, file=a.file,
                           media_type=a.media_type, crash_at=a.point)
    else:
        rc = create_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, source_id=a.source_id,
                              start=a.start, end=a.end, crash_at=a.point)
    if rc == 2:
        print(f"CRASHED-AT {a.point}: killed -9 (no ack emitted — by design)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
