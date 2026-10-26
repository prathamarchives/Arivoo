#!/usr/bin/env python3
"""harness/recover.py — the §3.1 recovery walk (P3-02; SYS-06's acceptance arm).

The convergence-idempotent walk over the staging journal (the §2.9 disposable
recovery substrate): OLDEST-FIRST (created_at,id — the stable total order; a
multi-row re-drive assigns edition ordinals deterministically, never by
arrival luck), terminal rows NEVER touched (the terminal discipline — complete
and failed are final; a second walk is a byte-identical no-op), every row's
outcome NAMED on its own line (a row's failure never stops the walk — the
next row proceeds), and the journal reads are row_to_json — ONE escaped line
per row, JSON-parsed at the boundary, never a re-parse of psql text (a title
carrying pipes, newlines, or a 'MARK' token can never corrupt the read).

The metadata re-drive: the canonical body is reconstructed from the journal
row's recorded FIELDS (the one construction home, commands._import_body) and
HASH-CHECKED against the row's body_hash BEFORE any drive — a mismatch is the
named ARV-IMP-001 (never a drive with an invented body, never a silent 409).
The drive itself re-verifies the blob FIRST (the phantom-closure: a complete
Source without bytes is impossible — §4.4), then rides the SAME spine under
the ORIGINAL idempotency key (replayed -> the recorded result; committed ->
exactly-once by the command_log's composite key).

The orphan sweep (the P3-01 notverified's named promise): a blob resident with
NO source row referencing it (any owner — the arv_read cross-owner check) and
NO non-terminal journal row carrying it is pure residue -> deleted (the §4.4
delete arm; a REFERENCED blob is never deleted, even corrupt — CAP-15's
refusal stands). .put- temps are ignored (the #84 pin's ignorable class).

Exit 0 = the walk completed and every row's outcome is named (a failed row is
a NAMED product of the walk, not a walk failure); exit 1 = the machinery
itself failed (the rig unreachable, a batch refused).
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
    """One owner-scoped batch through arv_app (the GUC set in the same batch —
    RLS is the scope); None on a named machinery failure (the caller REPORTS it,
    never treats it as zero rows — a silent empty is a guessed state)."""
    r = pg.psql(sql, db=db, user=user)
    return r.out if r.returncode == 0 else None


def _fail(db: str, owner: str, r: dict, code: str, *, clean: bool = False) -> None:
    """Mark the row failed with the named reason; a corrupt artifact is cleaned
    ONLY when unreferenced by any source row (the arv_read cross-owner check)."""
    _batch(f"SET app.current_owner={commands._q(owner)}; "
           f"UPDATE arv.import_journal SET state='failed', fail_reason={commands._q(code)}, "
           f"updated_at={commands._q(clock.now())} WHERE id={commands._q(r['id'])};", db=db)
    if clean and not _referenced(db, r["digest"]):
        blob.delete(r["digest"])
    print(f"WALK key={r['idempotency_key']} from={r['state']} to=failed reason={code} source=-")


def _referenced(db: str, digest: str) -> bool:
    """Cross-owner byte-reuse check (Q11: another owner's Source may reference
    the same digest) — the arv_read auditor's count; an UNREADABLE check is
    fail-closed to True (the blob is KEPT, never deleted on a guessed
    reference set)."""
    out = _batch(f"SELECT count(*) FROM arv.source WHERE digest={commands._q(digest)};",
                 db=db, user="arv_read")
    if out is None:
        return True  # fail-closed: an unreadable reference set keeps the artifact
    return out.strip() not in ("", "0")


def _verify(db: str, owner: str, r: dict) -> bool:
    """The staging exit condition (§3.1) and the phantom-closure arm (§4.4):
    re-verify the blob BEFORE any drive — absent/corrupt is a NAMED failure,
    never a promoted or phantom Source."""
    try:
        blob.get(r["digest"])
        return True
    except KeyError as e:
        code = e.args[0].split(":")[0] if e.args else "ARV-BLOB-000"  # e.args[0]: str(e) would carry KeyError's repr quotes
        _fail(db, owner, r, code, clean=(code == "ARV-BLOB-003"))
        return False


def _drive(db: str, owner: str, r: dict) -> None:
    """The metadata re-drive: the hash-checked body reconstruction, then the
    SAME spine under the ORIGINAL key (replayed/committed -> complete; the
    011 race -> the row stays staging_verified for the next walk; any other
    named refusal -> failed)."""
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
    """The whole walk: the non-terminal rows oldest-first, then the orphan
    sweep, then the named summary. The rows batch is row_to_json — one escaped
    line per row; a malformed line is a NAMED refusal for that row, never a
    walk-crashing parse; a machinery failure is a NAMED exit-1, never a silent
    zero-rows guess."""
    raw = _batch(f"SET app.current_owner={commands._q(owner)}; "
                 f"SELECT row_to_json(j) FROM (SELECT id, idempotency_key, client_id, work_id, title, digest, "
                 f"media_type, byte_size, acquired_via, state, body_hash, actor, created_at FROM arv.import_journal "
                 f"WHERE state IN ('staging','staging_verified')) j ORDER BY created_at, id;", db=db)
    if raw is None:
        print("FAIL ARV-IMP-003: the walk's journal read was refused at the boundary — the walk exits, "
              "never a guessed zero-rows state")
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
        print("FAIL ARV-IMP-003: the walk's sweep reads were refused at the boundary — the sweep is skipped, "
              "never a guessed keep-set")
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
    health = pg.psql("SELECT 1;", db=db, user="arv_read")
    if health.returncode != 0:
        print(f"FAIL ARV-DB-003: the rig is unreachable at the approved boundary — the walk refuses, "
              f"never a guessed state; raw: {health.stderr.strip()[:200]}")
        return 1
    return walk(db=db, owner=a.owner)


if __name__ == "__main__":
    sys.exit(main())
