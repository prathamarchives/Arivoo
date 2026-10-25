#!/usr/bin/env python3
"""harness/query.py — the authenticated retrieval surface (P3-01; RTM SYS-09).

The read boundary: every query runs through the approved adapter as the
arv_app role WITH the owner GUC set — RLS scopes every row; an id outside
the caller's scope and an id that does not exist are the SAME refusal
(ARV-QRY-001), never a side channel revealing another owner's object
existence (RTM §2.10's privacy principle on the read path). Reads are
side-effect-free: no command-log rows, no derived state. Exit 0 = rows
printed (one JSON object per line for get-*; one id per line for
list-captures); exit 1 = the named refusal.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg  # noqa: E402

CAP_SQL = ("SELECT h.id, h.revision, h.selected_text, h.source_id, a.source_digest, "
           "a.start_off, a.end_off, a.context_before, a.context_after, a.media_type, h.created_at "
           "FROM arv.highlight h JOIN arv.anchor a ON a.id = h.anchor_id "
           "WHERE h.id = {id} ORDER BY h.revision DESC LIMIT 1;")
CAP_FIELDS = ("id", "revision", "selected_text", "source_id", "source_digest", "start",
              "end", "context_before", "context_after", "media_type", "created_at")
SRC_SQL = ("SELECT s.id, s.work_id, w.title, s.digest, s.media_type, s.byte_size, "
           "s.import_state, s.source_version, s.created_at "
           "FROM arv.source s JOIN arv.work w ON w.id = s.work_id WHERE s.id = {id};")
SRC_FIELDS = ("id", "work_id", "title", "digest", "media_type", "byte_size",
              "import_state", "source_version", "created_at")
LIST_SQL = "SELECT id FROM arv.highlight ORDER BY created_at, id;"


def _read(db: str, owner: str, sql: str) -> list:
    """One owner-scoped read: the GUC + the SELECT in ONE batch (RLS enforced)."""
    q = "'" + owner.replace("'", "''") + "'"
    r = pg.psql(f"SET app.current_owner={q}; {sql}", db=db, user="arv_app")
    if r.returncode != 0:
        print(f"FAIL ARV-QRY-002: the read failed — {r.stderr.strip()}")
        return None
    return [ln for ln in r.out.splitlines() if ln.strip()]


def _refuse(id_: str) -> int:
    print(f"FAIL ARV-QRY-001: no such object ({id_}) in the caller's scope — absent and "
          "another owner's are the SAME refusal, never a side channel")
    print("      repair: check the id against the caller's own capture list (query.py list-captures)")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="the authenticated retrieval surface (P3-01)")
    sub = ap.add_subparsers(dest="what", required=True)
    for name in ("get-capture", "get-source"):
        p = sub.add_parser(name)
        p.add_argument("--owner", required=True)
        p.add_argument("--id", required=True)
    p = sub.add_parser("list-captures")
    p.add_argument("--owner", required=True)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    if a.what == "list-captures":
        rows = _read(db, a.owner, LIST_SQL)
        if rows is None:
            return 1
        for ln in rows:
            print(ln)
        return 0
    sql, fields = (CAP_SQL, CAP_FIELDS) if a.what == "get-capture" else (SRC_SQL, SRC_FIELDS)
    rows = _read(db, a.owner, sql.format(id="'" + a.id.replace("'", "''") + "'"))
    if rows is None:
        return 1
    if not rows:
        return _refuse(a.id)
    vals = rows[0].split("|")
    obj = {k: v for k, v in zip(fields, vals)}
    for k in ("revision", "byte_size", "source_version", "start", "end"):
        if k in obj:
            obj[k] = int(obj[k])
    print(json.dumps(obj, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
