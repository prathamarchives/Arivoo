#!/usr/bin/env python3
"""harness/query.py — the authenticated retrieval surface (P3-01; RTM SYS-09)
+ the typed anchor resolution (P3-03b; RTM §2.9 item 4, SYS-05).

Every query runs through the approved adapter as arv_app WITH the owner GUC
set — RLS scopes every row; an id outside the caller's scope and a nonexistent
id are the SAME refusal (ARV-QRY-001), never a side channel revealing another
owner's object existence (RTM §2.10 on the read path). Reads are
side-effect-free. Exit 0 = rows (one JSON line for get-*; one id per line for
list-captures) AND exit 0 = a typed resolution ANSWER (resolved | unresolved |
ambiguous — SYS-05's states are answers, never failures); exit 1 = the named
refusal.

THE TYPED RESOLUTION (resolve-anchor; P3-03b): a typed query, NEVER a
nearest-match guess —
  resolved     the location evidence validates WITHIN the anchor's OWN Source
               version against the CURRENT generation: the digest chain (the
               anchor's source_digest == the generation's input_digest) AND a
               contiguous covering of [start_off, end_off) by the passages AND
               the recorded contexts still surround the slice in the derived
               view
  unresolved   the honest miss with a NAMED cause: no-current-generation;
               stale-generation (the digest chain broke — the typed stale
               surface); location-unmatched (no covering and the fallback
               evidence found fewer than two hits — a single candidate is a
               DETECTION, never a retarget)
  ambiguous    the fallback matching evidence (context_before + context_after)
               locates the pattern at TWO OR MORE positions in the derived
               view — the anchor's evidence cannot pick one; the original
               evidence is preserved (the anchor row is immutable)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg  # noqa: E402

# THE P1 SEV FIX (the round-1 BLOCKED finding): free-text fields legally carry
# pipes and newlines, so the output is structured AT THE SQL BOUNDARY (row_to_json
# emits ONE escaped JSON line per row) — never re-parsed by splitting psql text.
CAP_SQL = ("SELECT row_to_json(t)::text FROM (SELECT h.id AS id, h.revision, h.selected_text, "
           "h.source_id, a.source_digest, a.start_off AS start, a.end_off AS end, a.context_before, "
           "a.context_after, a.media_type, h.created_at FROM arv.highlight h "
           "JOIN arv.anchor a ON a.id = h.anchor_id WHERE h.id = {id} "
           "ORDER BY h.revision DESC LIMIT 1) t;")
SRC_SQL = ("SELECT row_to_json(t)::text FROM (SELECT s.id AS id, s.work_id, w.title, s.digest, "
           "s.media_type, s.byte_size, s.import_state, s.source_version, s.created_at "
           "FROM arv.source s JOIN arv.work w ON w.id = s.work_id WHERE s.id = {id}) t;")
LIST_SQL = "SELECT row_to_json(t)::text FROM (SELECT id FROM arv.highlight ORDER BY created_at, id) t;"
ANC_SQL = ("SELECT row_to_json(t)::text FROM (SELECT a.id AS anchor_id, a.source_id, a.source_digest, "
           "a.start_off, a.end_off, a.context_before, a.context_after, g.id AS generation_id, "
           "g.input_digest FROM arv.anchor a LEFT JOIN arv.extraction_generation g "
           "ON g.source_id = a.source_id AND g.state = 'current' WHERE a.id = {id}) t;")
PASS_SQL = ("SELECT row_to_json(t)::text FROM (SELECT id, ordinal, start_off, end_off, text "
            "FROM arv.passage WHERE generation_id = {gid} ORDER BY ordinal) t;")


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


def _resolve(db: str, owner: str, anchor_id: str) -> int:
    """SYS-05's typed resolution — one JSON answer line at exit 0; ARV-QRY-001
    for out-of-scope/absent. The join never crosses Source versions (the anchor
    binds its OWN version; a new edition is a different source row and cannot
    appear here)."""
    q = "'" + anchor_id.replace("'", "''") + "'"
    rows = _read(db, owner, ANC_SQL.format(id=q))
    if rows is None:
        return 1
    if not rows:
        return _refuse(anchor_id)
    a = json.loads(rows[0])
    out = {"anchor_id": anchor_id, "source_id": a["source_id"],
           "start_off": a["start_off"], "end_off": a["end_off"]}
    cb, ca = a["context_before"], a["context_after"]
    if not a["generation_id"]:
        _say(out, state="unresolved", cause="no-current-generation", evidence_hits=0)
        return 0
    if a["input_digest"] != a["source_digest"]:
        _say(out, state="unresolved", cause="stale-generation", evidence_hits=0)
        return 0
    rows = _read(db, owner, PASS_SQL.format(gid="'" + a["generation_id"] + "'"))
    if rows is None:
        return 1
    ps = [json.loads(r) for r in rows]
    view = "".join(p["text"] for p in ps)          # the derived view, ordinal order
    base = ps[0]["start_off"] if ps else 0           # the view's source-anchor
    span = a["end_off"] - a["start_off"]
    cur, covered, ids = a["start_off"], 0, []         # the primary: a contiguous covering
    for p in sorted(ps, key=lambda p: p["start_off"]):
        if p["start_off"] > cur:
            break
        if p["end_off"] <= cur:
            continue
        covered += min(p["end_off"], a["end_off"]) - cur
        cur = p["end_off"]
        ids.append(p["id"])
        if cur >= a["end_off"]:
            break
    rs, re_ = a["start_off"] - base, a["end_off"] - base
    ok_ev = (covered >= span and cur >= a["end_off"]
             and view[max(0, rs - len(cb)):rs] == cb[max(0, len(cb) - rs):]
             and view[re_:min(len(view), re_ + len(ca))] == ca[:max(0, min(len(view), re_ + len(ca)) - re_)])
    if ok_ev:
        _say(out, state="resolved", generation_id=a["generation_id"],
             passage_ids=",".join(ids))
        return 0
    hits = 0                                           # the fallback: cb + gap + ca
    for i in range(len(view)):
        j = i + len(cb) + span
        if view.startswith(cb, i) and j + len(ca) <= len(view) and view.startswith(ca, j):
            hits += 1
    if hits >= 2:
        _say(out, state="ambiguous", evidence_hits=hits)
    else:
        _say(out, state="unresolved", cause="location-unmatched", evidence_hits=hits)
    return 0


def _say(out: dict, **kw) -> None:
    out.update(kw)
    print(json.dumps(out, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser(description="the authenticated retrieval surface (P3-01)")
    sub = ap.add_subparsers(dest="what", required=True)
    for name in ("get-capture", "get-source"):
        p = sub.add_parser(name)
        p.add_argument("--owner", required=True)
        p.add_argument("--id", required=True)
    p = sub.add_parser("list-captures")
    p.add_argument("--owner", required=True)
    p = sub.add_parser("resolve-anchor")
    p.add_argument("--owner", required=True)
    p.add_argument("--id", required=True)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    if a.what == "resolve-anchor":
        return _resolve(db, a.owner, a.id)
    if a.what == "list-captures":
        rows = _read(db, a.owner, LIST_SQL)
        if rows is None:
            return 1
        for ln in rows:
            print(json.loads(ln)["id"])
        return 0
    sql = CAP_SQL if a.what == "get-capture" else SRC_SQL
    rows = _read(db, a.owner, sql.format(id="'" + a.id.replace("'", "''") + "'"))
    if rows is None:
        return 1
    if not rows:
        return _refuse(a.id)
    print(json.dumps(json.loads(rows[0]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
