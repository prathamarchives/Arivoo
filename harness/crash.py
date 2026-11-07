#!/usr/bin/env python3
"""harness/crash.py — the crash-injection helper (S3; extended P3-01 + P3-02).

SIGKILL at one injection point — the spine's three (S3): after-begin /
pre-commit / post-commit-pre-ack (§1.6's lost-ack); the import's three phase
boundaries (P3-02): after-staging / after-put / after-verify; the extraction
rides the spine's three (P3-03a). Exit 2 = crashed (no ack, by design); a
usage error is exit 1 named (the _UsageParser override — argparse's exit-2
masquerade never fires).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.commands import record_event, import_source, create_highlight  # noqa: E402
from harness.commands import revise_highlight, tombstone_highlight, restore_highlight  # noqa: E402
from harness.commands import (create_bookmark, move_bookmark,  # noqa: E402
                              tombstone_bookmark, restore_bookmark)
from harness.commands import (create_note, revise_note,  # noqa: E402
                              tombstone_note, restore_note)
from harness.commands import save_position  # noqa: E402  # P4-A slice two: the position save joins the crash matrix
from harness.commands import record_session  # noqa: E402  # P4-C slice two: the session event joins the crash matrix
from harness.extract import extract_source  # noqa: E402

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
                    choices=["record_event", "import_source", "create_highlight",
                             "extract_source", "revise_highlight", "tombstone_highlight",
                             "restore_highlight", "create_bookmark", "move_bookmark",
                             "tombstone_bookmark", "restore_bookmark",
                             "create_note", "revise_note", "tombstone_note",
                             "restore_note", "save_position", "record_session"])
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
    ap.add_argument("--event", default=None,
                    help="the session-event kind (record_session; P4-C slice two)")
    ap.add_argument("--dwell-ms", default=None, type=int,
                    help="the coarse dwell in milliseconds (dwell events only)")
    ap.add_argument("--id", default=None, help="the highlight/bookmark/note id (the P3-04/05/06 families)")
    ap.add_argument("--content", default=None,
                    help="the note's authored content, inline (P3-06)")
    ap.add_argument("--content-file", default=None,
                    help="the note's long-form authoring surface: a UTF-8 file read losslessly (P3-06)")
    ap.add_argument("--ref", action="append", default=None, metavar="KIND:ID[@REV]",
                    help="an explicit version-aware reference (repeatable; P3-06 slice two)")
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
    elif a.command == "extract_source":
        rc = extract_source(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, source_id=a.source_id, crash_at=a.point)
    elif a.command == "revise_highlight":
        rc = revise_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, id_=a.id, start=a.start, end=a.end,
                              crash_at=a.point)
    elif a.command == "tombstone_highlight":
        rc = tombstone_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                 idem_key=a.idem_key, id_=a.id, crash_at=a.point)
    elif a.command == "restore_highlight":
        rc = restore_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                               idem_key=a.idem_key, id_=a.id, crash_at=a.point)
    elif a.command == "create_bookmark":
        rc = create_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                             idem_key=a.idem_key, source_id=a.source_id,
                             start=a.start, end=a.end, crash_at=a.point)
    elif a.command == "move_bookmark":
        rc = move_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, id_=a.id, start=a.start, end=a.end,
                           crash_at=a.point)
    elif a.command == "tombstone_bookmark":
        rc = tombstone_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                idem_key=a.idem_key, id_=a.id, crash_at=a.point)
    elif a.command == "restore_bookmark":
        rc = restore_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, id_=a.id, crash_at=a.point)
    elif a.command == "create_note":
        rc = create_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                         idem_key=a.idem_key, content=a.content,
                         content_file=a.content_file, refs=a.ref, crash_at=a.point)
    elif a.command == "revise_note":
        rc = revise_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                         idem_key=a.idem_key, id_=a.id, content=a.content,
                         content_file=a.content_file, refs=a.ref, crash_at=a.point)
    elif a.command == "tombstone_note":
        rc = tombstone_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, id_=a.id, crash_at=a.point)
    elif a.command == "restore_note":
        rc = restore_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                          idem_key=a.idem_key, id_=a.id, crash_at=a.point)
    elif a.command == "save_position":
        rc = save_position(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, source_id=a.source_id,
                           start=a.start, end=a.end, crash_at=a.point)
    elif a.command == "record_session":
        rc = record_session(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, source_id=a.source_id,
                            event=a.event, start=a.start, end=a.end,
                            dwell_ms=a.dwell_ms, crash_at=a.point)
    else:
        rc = create_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, source_id=a.source_id,
                              start=a.start, end=a.end, crash_at=a.point)
    if rc == 2:
        print(f"CRASHED-AT {a.point}: killed -9 (no ack emitted — by design)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
