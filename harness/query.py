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
# P3-04 (RTM §3.3): tombstoned hides from ordinary retrieval — the list EXCLUDES
# the ids whose committed event parity says tombstoned (tombstone_count >
# restore_count; order-independent, rebuildable — never a state column).  An
# HAVING over zero lifecycle rows yields no row -> NOT EXISTS -> active stays listed.
LIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT DISTINCT h.id FROM arv.highlight h "
            "WHERE NOT EXISTS (SELECT 1 FROM arv.highlight_lifecycle l "
            "WHERE l.highlight_id = h.id AND l.owner_scope = h.owner_scope "
            "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
            "count(*) FILTER (WHERE l.event = 'restore')) ORDER BY h.id) t;")
# P3-04: the governed history — EVERY revision + EVERY lifecycle event, one JSON
# row per line (the ANC-10/#88 newline-only framing contract: row_to_json escapes
# below U+0020 ONLY, so U+2028 travels raw inside the string and the reader splits
# on \n ONLY).  The current view is DERIVED from these rows (HLG-09's rebuild).
HIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT h.id, 'revision' AS kind, h.revision, "
            "h.selected_text, h.anchor_id, NULL::text AS event, h.actor, h.created_at "
            "FROM arv.highlight h WHERE h.id = {id} UNION ALL "
            "SELECT l.highlight_id, 'lifecycle' AS kind, NULL::integer AS revision, "
            "NULL::text AS selected_text, NULL::uuid AS anchor_id, l.event, l.actor, "
            "l.created_at FROM arv.highlight_lifecycle l WHERE l.highlight_id = {id}) t "
            "ORDER BY t.created_at, t.revision NULLS LAST, t.kind;")
# P3-04: the single-id parity read — tombstoned iff tombstones > restores.
STATE_SQL = ("SELECT count(*) FILTER (WHERE event = 'tombstone') || '|' || "
             "count(*) FILTER (WHERE event = 'restore') FROM arv.highlight_lifecycle "
             "WHERE highlight_id = {id};")
ANC_SQL = ("SELECT row_to_json(t)::text FROM (SELECT a.id AS anchor_id, a.source_id, a.source_digest, "
           "a.start_off, a.end_off, a.context_before, a.context_after, g.id AS generation_id, "
           "g.input_digest FROM arv.anchor a LEFT JOIN arv.extraction_generation g "
           "ON g.source_id = a.source_id AND g.state = 'current' WHERE a.id = {id}) t;")
PASS_SQL = ("SELECT row_to_json(t)::text FROM (SELECT id, ordinal, start_off, end_off, text "
            "FROM arv.passage WHERE generation_id = {gid} ORDER BY ordinal) t;")


def _read(db: str, owner: str, sql: str) -> list:
    """One owner-scoped read: the GUC + the SELECT in ONE batch (RLS enforced).
    Row framing is NEWLINE-ONLY (the ANC-10 contract): PostgreSQL emits one
    JSON row per line, and row_to_json escapes control characters below
    U+0020 ONLY — U+2028/U+2029/U+0085 travel raw inside the JSON string, so a
    str.splitlines() reader would split a row on them and corrupt the framing
    (the observed pre-fix crash: JSONDecodeError 'Unterminated string')."""
    q = "'" + owner.replace("'", "''") + "'"
    r = pg.psql(f"SET app.current_owner={q}; {sql}", db=db, user="arv_app")
    if r.returncode != 0:
        print(f"FAIL ARV-QRY-002: the read failed — {r.stderr.strip()}")
        return None
    return [ln for ln in r.out.split("\n") if ln.strip()]


def _refuse(id_: str) -> int:
    print(f"FAIL ARV-QRY-001: no such object ({id_}) in the caller's scope — absent and "
          "another owner's are the SAME refusal, never a side channel")
    print("      repair: check the id against the caller's own capture list (query.py list-captures)")
    return 1


def _refuse_tombstoned(id_: str) -> int:
    """P3-04 (RTM §3.3): the typed tombstone refusal on the ordinary read path —
    hidden from retrieval, never erased; the governed history keeps everything."""
    print(f"FAIL ARV-QRY-003: highlight {id_} is tombstoned — hidden from ordinary retrieval "
          "(the governed history at get-history retains every revision and event)")
    print("      repair: query.py get-history for the governed view; commands.py restore_highlight "
          "returns it to ordinary retrieval (the revisions were never touched)")
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
    for name in ("get-capture", "get-source", "get-history"):
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
    if a.what == "get-history":
        # the governed history (P3-04): every revision + every lifecycle event —
        # rows printed as-is, each already ONE escaped JSON line (the framing law)
        rows = _read(db, a.owner, HIST_SQL.format(id="'" + a.id.replace("'", "''") + "'"))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id)
        for ln in rows:
            print(ln)
        return 0
    if a.what == "get-capture":
        # P3-04 (RTM §3.3): the ordinary read refuses tombstoned ids with the
        # typed code; the governed history keeps them addressable
        qid = "'" + a.id.replace("'", "''") + "'"
        rows = _read(db, a.owner, STATE_SQL.format(id=qid))
        if rows is None:
            return 1
        t_n, r_n = (int(x) for x in rows[0].split("|"))
        if t_n > r_n:
            return _refuse_tombstoned(a.id)
        rows = _read(db, a.owner, CAP_SQL.format(id=qid))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id)
        print(json.dumps(json.loads(rows[0]), ensure_ascii=False))
        return 0
    sql = SRC_SQL
    rows = _read(db, a.owner, sql.format(id="'" + a.id.replace("'", "''") + "'"))
    if rows is None:
        return 1
    if not rows:
        return _refuse(a.id)
    print(json.dumps(json.loads(rows[0]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
