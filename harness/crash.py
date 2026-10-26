#!/usr/bin/env python3
"""harness/crash.py — the crash-injection helper (S3; extended P3-01 + P3-02).

SIGKILL at one injection point — the spine's three (S3): after-begin /
pre-commit / post-commit-pre-ack (§1.6's lost-ack); the import's three phase
boundaries (P3-02): after-staging / after-put / after-verify. Exit 2 = crashed
(no ack, by design); a usage error is exit 1 named (the _UsageParser override
— argparse's exit-2 masquerade never fires).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.commands import record_event, import_source, create_highlight  # noqa: E402

POINTS = ("after-begin", "pre-commit", "post-commit-pre-ack",
          "after-staging", "after-put", "after-verify")
SPINE_POINTS = ("after-begin", "pre-commit", "post-commit-pre-ack")


class _UsageParser(argparse.ArgumentParser):
    """F4: every argparse error exits 1 named (exit 2 is the crash vocabulary)."""
    def error(self, message: str):
        print(f"CRASH-USAGE: {message} — a named usage refusal (exit 1), never "
              "exit 2 (argparse's default masquerades as a crash)")
        self.exit(1)


def main() -> int:
    ap = _UsageParser(description="crash-injection helper (S3 + P3-01 + P3-02)")
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
    ap.add_argument("--work-id", default=None)
    ap.add_argument("--file", default=None)
    ap.add_argument("--media-type", default="text/plain")
    ap.add_argument("--source-id", default=None)
    ap.add_argument("--start", default=None, type=int)
    ap.add_argument("--end", default=None, type=int)
    a = ap.parse_args()
    if a.command != "import_source" and a.point not in SPINE_POINTS:
        print(f"CRASH-USAGE: the point {a.point!r} is an import-phase boundary — it exists "
              "only on import_source (the phased machine); a named usage refusal, never "
              "exit 2 (the argparse-masquerade lesson)")
        return 1
    db = os.environ.get("PGDATABASE", "postgres")
    if a.command == "record_event":
        rc = record_event(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                          idem_key=a.idem_key, payload=a.payload, crash_at=a.point)
    elif a.command == "import_source":
        rc = import_source(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, title=a.title, work_id=a.work_id,
                           file=a.file, media_type=a.media_type, crash_at=a.point)
    else:
        rc = create_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, source_id=a.source_id,
                              start=a.start, end=a.end, crash_at=a.point)
    if rc == 2:
        print(f"CRASHED-AT {a.point}: killed -9 (no ack emitted — by design)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
