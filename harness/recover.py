#!/usr/bin/env python3
"""harness/recover.py — the §3.1 recovery walk (P3-02; SYS-06's acceptance arm).

Convergence-idempotent, OLDEST-FIRST (created_at,id), terminal rows NEVER
touched (a second walk is a byte-identical no-op, pinned by updated_at), every
row's outcome NAMED on its own line (a row's failure never stops the walk).
Journal reads are row_to_json — ONE escaped line per row, JSON-parsed at the
boundary, never a re-parse of psql text (pipes/newlines/'MARK' cannot corrupt).
The re-drive reconstructs the canonical body from the row's recorded FIELDS and
HASH-CHECKS it against body_hash BEFORE any drive (a mismatch is ARV-IMP-001);
re-verifies the blob FIRST (the phantom-closure: a complete Source without
bytes is impossible — §4.4); rides the SAME spine under the ORIGINAL key.
The sweep deletes journal-less residue, protecting referenced (any owner, the
arv_read cross-owner check — Q11 byte-reuse) and live-staging blobs; a
REFERENCED blob is never deleted, even corrupt (CAP-15 stands); .put- temps
are ignored (the #84 pin's ignorable class). Exit 0 = every row's outcome
named; exit 1 = a named machinery failure (ARV-IMP-003 — never a silent guess).
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg, blob, clock  # noqa: E402
import harness.commands as commands  # noqa: E402

import hashlib  # noqa: E402


def _batch(sql: str, *, db: str, user: str = "arv_app") -> "str | None":
    """One owner-scoped batch (GUC set in the same batch); None = a NAMED
    machinery failure — a silent empty is a guessed state."""
    r = pg.psql(sql, db=db, user=user)
    return r.out if r.returncode == 0 else None


def _fail(db: str, owner: str, r: dict, code: str, *, clean: bool = False) -> None:
    """Mark the row failed with the named reason; a corrupt artifact is cleaned
    only when unreferenced by any source row (the cross-owner check)."""
    _batch(f"SET app.current_owner={commands._q(owner)}; "
           f"UPDATE arv.import_journal SET state='failed', fail_reason={commands._q(code)}, "
           f"updated_at={commands._q(clock.now())} WHERE id={commands._q(r['id'])};", db=db)
    if clean and not _referenced(db, r["digest"]):
        blob.delete(r["digest"])
    print(f"WALK key={r['idempotency_key']} from={r['state']} to=failed reason={code} source=-")


def _referenced(db: str, digest: str) -> bool:
    """The arv_read cross-owner count; an UNREADABLE check is fail-closed True
    (the blob is KEPT — never deleted on a guessed reference set)."""
    out = _batch(f"SELECT count(*) FROM arv.source WHERE digest={commands._q(digest)};",
                 db=db, user="arv_read")
    if out is None:
        return True  # fail-closed: an unreadable reference set keeps the artifact
    return out.strip() not in ("", "0")


def _verify(db: str, owner: str, r: dict) -> bool:
    """§3.1's staging exit + §4.4's phantom-closure: re-verify the blob BEFORE
    any drive — absent/corrupt is a NAMED failure, never a promoted Source."""
    try:
        blob.get(r["digest"])
        return True
    except KeyError as e:
        code = e.args[0].split(":")[0] if e.args else "ARV-BLOB-000"  # e.args[0]: str(e) would carry KeyError's repr quotes
        _fail(db, owner, r, code, clean=(code == "ARV-BLOB-003"))
        return False


def _drive(db: str, owner: str, r: dict) -> None:
    """The hash-checked body reconstruction, then the SAME spine under the
    ORIGINAL key (replayed/committed -> complete; 011 -> retry-race, the row
    stays staging_verified for the next walk; any other refusal -> failed)."""
    body = commands._import_body(title=r["title"], work_id=r["work_id"], digest=r["digest"],
                                 media_type=r["media_type"], byte_size=r["byte_size"],
                                 acquired_via=r["acquired_via"])
    got = hashlib.sha256(commands.canonical_body(
        command="import_source", client_id=r["client_id"], owner_scope=owner,
        actor=r["actor"], payload=body).encode()).hexdigest()
    if got != r["body_hash"]:
        _fail(db, owner, r, "ARV-IMP-001")  # the reconstruction mismatch — never a drive with an invented body
        return
    build = commands._import_build(owner=owner, actor=r["actor"], client_id=r["client_id"],
                                   idem_key=r["idempotency_key"], title=r["title"], work_id=r["work_id"],
                                   digest=r["digest"], media_type=r["media_type"], byte_size=r["byte_size"],
                                   acquired_via=r["acquired_via"])
    cap = io.StringIO()
    real = sys.stdout
    sys.stdout = cap
    try:
        rc = commands._spine(db=db, owner=owner, actor=r["actor"], client_id=r["client_id"],
                             idem_key=r["idempotency_key"], command="import_source",
                             payload=body, build=build, crash_at=None)
    finally:
        sys.stdout = real
    out = cap.getvalue()
    if rc == 0:
        status = "replayed" if "status=replayed" in out else "driven"
        ref = ""
        for ln in out.splitlines():
            if "result_ref=" in ln:
                ref = ln.split("result_ref=")[1].split()[0]
        if status == "replayed":  # the recorded result IS the convergence — the spine never ran the transaction
            _batch(f"SET app.current_owner={commands._q(owner)}; "
                   f"UPDATE arv.import_journal SET state='complete', source_id={commands._q(ref)}, "
                   f"updated_at={commands._q(clock.now())} WHERE id={commands._q(r['id'])} "
                   f"AND state='staging_verified';", db=db)
        print(f"WALK key={r['idempotency_key']} from={r['state']} to=complete reason={status} source={ref}")
    elif "ARV-CMD-011" in out:
        print(f"WALK key={r['idempotency_key']} from={r['state']} to=staging_verified reason=retry-race source=-")
    else:
        code = "ARV-CMD-010"
        for ln in out.splitlines():
            if ln.startswith("FAIL "):
                code = ln.split()[1].rstrip(":")
                break
        _fail(db, owner, r, code)


def walk(*, db: str, owner: str) -> int:
    """The non-terminal rows oldest-first, then the sweep, then the named
    summary; a malformed line is a NAMED refusal for that row (ARV-IMP-002);
    a machinery failure is a NAMED exit-1 (ARV-IMP-003)."""
    raw = _batch(f"SET app.current_owner={commands._q(owner)}; "
                 f"SELECT row_to_json(j) FROM (SELECT id, idempotency_key, client_id, work_id, title, digest, "
                 f"media_type, byte_size, acquired_via, state, body_hash, actor, created_at FROM arv.import_journal "
                 f"WHERE state IN ('staging','staging_verified')) j ORDER BY created_at, id;", db=db)
    if raw is None:
        print("FAIL ARV-IMP-003: the walk's journal read was refused at the boundary — the walk exits, never a guessed zero-rows state")
        return 1
    rows = []
    for ln in (l for l in raw.splitlines() if l.strip()):
        try:
            rows.append(json.loads(ln))
        except json.JSONDecodeError:
            print("WALK key=<unreadable> from=<journal> to=unchanged reason=ARV-IMP-002 source=-")
    driven = 0
    failed_before = 0
    for r in rows:
        if r["state"] == "staging":
            if _verify(db, owner, r):
                _batch(f"SET app.current_owner={commands._q(owner)}; "
                       f"UPDATE arv.import_journal SET state='staging_verified', "
                       f"updated_at={commands._q(clock.now())} WHERE id={commands._q(r['id'])} "
                       f"AND state='staging';", db=db)
                r["state"] = "staging_verified"
                driven += 1
                _drive(db, owner, r)
            else:
                failed_before += 1
        else:
            if _verify(db, owner, r):
                driven += 1
                _drive(db, owner, r)
            else:
                failed_before += 1
    kept_out = _batch("SELECT digest FROM arv.source;", db=db, user="arv_read")
    live_out = _batch(f"SELECT digest FROM arv.import_journal "
                      f"WHERE state IN ('staging','staging_verified');", db=db, user="arv_read")
    if kept_out is None or live_out is None:
        print("FAIL ARV-IMP-003: the walk's sweep reads were refused at the boundary — the sweep is skipped, never a guessed keep-set")
        return 1
    kept = set(kept_out.split()) | set(live_out.split())
    swept = [d for d in blob.residents() if d not in kept]
    for d in swept:
        blob.delete(d)
    counts = _batch(f"SET app.current_owner={commands._q(owner)}; "
                    f"SELECT state, count(*) FROM arv.import_journal GROUP BY state ORDER BY state;", db=db)
    if counts is None:
        print("FAIL ARV-IMP-003: the walk's summary read was refused — exit 1, never a guessed summary")
        return 1
    summary = {s: 0 for s in ("staging", "staging_verified", "complete", "failed")}
    for ln in counts.splitlines():
        if "|" in ln:
            summary[ln.split("|")[0]] = int(ln.split("|")[1])
    print(f"SWEEP deleted={len(swept)} kept={len(kept)}")
    print(f"WALK-DONE owner={owner} rows={len(rows)} driven-or-replayed={driven} "
          f"verify-failed={failed_before} already-complete={summary['complete']} already-failed={summary['failed']} "
          f"still-staging={summary['staging']} still-verified={summary['staging_verified']} swept={len(swept)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the §3.1 recovery walk (P3-02)")
    ap.add_argument("--owner", required=True)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    if pg.psql("SELECT 1;", db=db, user="arv_read").returncode != 0:
        print("FAIL ARV-DB-003: the rig is unreachable at the approved boundary — the walk refuses, never a guessed state")
        return 1
    return walk(db=db, owner=a.owner)


if __name__ == "__main__":
    sys.exit(main())
