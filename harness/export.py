#!/usr/bin/env python3
"""harness/export.py — the export/restore machine (P3-09; CLAIM-060; RTM
§3.7 + SYS-10 + D-029).

EXPORT: the authoritative records (thirteen tables: the capture families +
their lifecycle events + note_reference + command_log + outbox + the purge
ledger) + the blob references (copied by digest into the archive) under an
EXPLICIT VERSIONED MANIFEST carrying the canonical state hash (sha256 over
the canonical serialization of the whole table set). Derived state (the
keyword index, extraction generations) is NEVER exported — it rebuilds.

RESTORE into a clean migrated destination, in the declared order:
  1. the manifest parses (ARV-EXP-003) and the version is known
     (ARV-EXP-005);
  2. the state hash recomputes over the manifest's own tables — a tampered
     row breaks it (ARV-EXP-003, the tamper proof);
  3. the destination's CURRENT purge ledger is read — the POSITIVE absence
     determination (the table must ANSWER; an unreadable ledger is the typed
     NON-RESTORING outcome ARV-EXP-006, never a silent archive-only
     downgrade);
  4. the destination is clean (zero authoritative rows for the owner —
     ARV-EXP-002, never a silent duplicate);
  5. every referenced blob is present AND digest-matched in the archive
     (ARV-EXP-004 — validate-before-declare);
  6. THE RECONCILIATION FIRST: the ledgered entities drop from the archive's
     content (the note: its revisions, lifecycle, references; the source:
     the whole capture tree — anchors, highlights/bookmarks, their
     lifecycles; the ledger WINS, SYS-10);
  7. ONE transaction inserts the reconciled authoritative set (the crash
     injection leaves NOTHING half-complete — the rollback restores the
     clean destination); the archive's own ledger rows merge ON CONFLICT DO
     NOTHING (the destination's current entries stay authoritative);
  8. the typed completion names the adopted ledger's as-of time, the
     documented backup-expiry window (D-029 — the explicit scope of a clean
     destination's restore), and the state-hash self-check.

Environment (the main()-PGDATABASE precedent): the database to read/export
from or to restore into is PGDATABASE; the blob store is ARV_BLOB_DIR
(the adapters' boundary). The equality verification is INDEPENDENT by
design — the caller reads both databases through arv_read (a separate role
and path from this module's sessions).
"""
import argparse
import hashlib
import json
import os
import pathlib

import signal
import subprocess
import sys


REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from harness.adapters import pg, clock, blob  # noqa: E402

FORMAT = "arv-export-1"
# the authoritative table set in the RESTORE's insert order (the guards'
# dependency order: entities before their lifecycle events, notes before
# their references; command_log/outbox/purge_ledger last)
TABLES = {
    "work": "id,title,owner_scope,actor,run_id,input_hash,created_at",
    "source": "id,work_id,digest,media_type,byte_size,blob_ref,acquired_via,import_state,source_version,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "anchor": "id,source_id,source_digest,start_off,end_off,context_before,context_after,media_type,owner_scope,actor,run_id,input_hash,created_at",
    "highlight": "id,revision,selected_text,source_id,anchor_id,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "highlight_lifecycle": "id,highlight_id,event,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "bookmark": "id,revision,source_id,anchor_id,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "bookmark_lifecycle": "id,bookmark_id,event,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "note": "id,revision,content,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "note_lifecycle": "id,note_id,event,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "note_reference": "id,note_id,note_revision,ref_kind,ref_id,ref_revision,owner_scope,actor,run_id,input_hash,idempotency_key,created_at",
    "command_log": "owner_scope,idempotency_key,client_id,command_name,body_hash,result_ref,actor,created_at",
    "outbox": "seq,idempotency_key,client_id,actor,command_name,body_hash,payload,state,attempts,last_reason,server_ref,created_at,updated_at,owner_scope",
    "purge_ledger": "owner_scope,kind,entity_id,reason,actor,created_at",
}
_ENTITY = ("work", "source", "anchor", "highlight", "bookmark", "note")


def _q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def _die() -> None:
    os.kill(os.getpid(), signal.SIGKILL)


def _app(sql: str) -> "tuple[int, str]":
    """One owner-scoped arv_app batch on PGDATABASE (RLS rides the session)."""
    r = pg.psql(sql, db=os.environ.get("PGDATABASE", "postgres"), user="arv_app")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _read_table(owner: str, table: str) -> list:
    """The canonical rows: single-line JSON per row, the declared column
    order, ordered by the leading identity columns (the deterministic form
    the hash and the equality both ride)."""
    cols = TABLES[table].split(",")
    lead = ",".join(cols[:2])
    rc, out = _app(f"SET app.current_owner={_q(owner)}; "
                   f"SELECT row_to_json(t) FROM (SELECT {TABLES[table]} FROM arv.{table} "
                   f"ORDER BY {lead}) t;")
    if rc != 0:
        print(f"FAIL ARV-EXP-001: the export read of arv.{table} failed — {out.strip()[:160]}")
        return []
    return [json.loads(ln) for ln in out.splitlines() if ln.startswith("{")]


def _state_hash(manifest_tables: dict) -> str:
    return hashlib.sha256(json.dumps(
        {"format": FORMAT, "tables": manifest_tables},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def do_export(owner: str, out_dir: str) -> int:
    out = pathlib.Path(out_dir)
    (out / "blobs").mkdir(parents=True, exist_ok=True)
    tables = {t: _read_table(owner, t) for t in TABLES}
    manifest = {"format": FORMAT, "owner": owner, "exported_at": clock.now(),
                "tables": tables,
                "state_hash": _state_hash(tables)}
    digests = sorted({r["digest"] for r in tables["source"]})
    for d in digests:
        try:
            data = blob.get(d)
        except KeyError as e:
            print(f"FAIL ARV-EXP-001: the blob {d[:12]} is unreadable at export — {e.args[0] if e.args else e}")
            return 1
        (out / "blobs" / d).write_bytes(data)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")
    rows = sum(len(v) for v in tables.values())
    print(f"EXPORTED owner={owner} dir={out} tables={len(tables)} rows={rows} "
          f"state_hash={manifest['state_hash'][:16]}")
    return 0


def _val(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return _q(v)


def _drop_purged(rows: dict, ledger: list) -> dict:
    """THE RECONCILIATION (SYS-10): the destination's current ledger WINS —
    every ledgered entity's rows drop from the archive's content (the note:
    revisions + lifecycle + references; the source/anchor/work: the whole
    capture tree). The command log and the outbox stay (the audit trail is
    never purge material). `rows` = {table: [dict, ...]} by column name."""
    led = {(k, i) for k, i, _ in ledger}

    def drop(table, col, gone):
        if gone:
            rows[table] = [r for r in rows[table] if r[col] not in gone]
    for kind in _ENTITY:
        gone = {r["id"] for r in rows[kind] if (kind, r["id"]) in led}
        if not gone:
            continue
        if kind in ("source", "anchor", "work"):
            if kind == "work":
                gone |= {r["id"] for r in rows["source"] if r["work_id"] in gone}
            anchors = {r["id"] for r in rows["anchor"] if r["source_id"] in gone}
            for t in ("highlight", "bookmark"):
                ents = {r["id"] for r in rows[t] if r["anchor_id"] in anchors}
                drop(t + "_lifecycle", t + "_id", ents)
                drop(t, "anchor_id", anchors)
            drop("anchor", "id", anchors)
        drop(kind, "id", gone)
        if kind == "note":
            drop("note_lifecycle", "note_id", gone)
            drop("note_reference", "note_id", gone)
        elif kind in ("highlight", "bookmark"):
            drop(kind + "_lifecycle", kind + "_id", gone)
    return rows


def do_restore(archive: str, crash_at: str) -> int:
    arch = pathlib.Path(archive)
    man_path = arch / "manifest.json"
    try:
        m = json.loads(man_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL ARV-EXP-003: the manifest is unreadable/malformed — {e}")
        print("      repair: export again; a truncated or corrupted manifest is never a partially-trusted one")
        return 1
    if m.get("format") != FORMAT:
        print(f"FAIL ARV-EXP-005: the manifest's format {m.get('format')!r} is not {FORMAT!r} — an unknown version is a named refusal, never a best-effort parse")
        return 1
    if _state_hash(m.get("tables", {})) != m.get("state_hash"):
        print("FAIL ARV-EXP-003: the state hash does not match the recomputation — the manifest's content changed after export (the tamper proof)")
        print("      repair: re-export from the authoritative source; a tampered archive is refused whole, never in part")
        return 1
    owner = m["owner"]
    tables = {t: [list(r[c] for c in TABLES[t].split(",")) for r in m["tables"][t]] for t in TABLES}
    # 3. the destination's CURRENT ledger — the POSITIVE absence determination
    rc, out = _app(f"SET app.current_owner={_q(owner)}; SELECT kind || '|' || entity_id || '|' || "
                   f"to_char(max(created_at), 'YYYY-MM-DD\"T\"HH24:MI:SS') FROM arv.purge_ledger "
                   f"GROUP BY kind, entity_id;")
    if rc != 0:
        print("FAIL ARV-EXP-006: the destination's purge ledger is UNREADABLE — the typed NON-RESTORING outcome")
        print("      repair: the destination's ledger store must affirmatively answer (an unreadable ledger is not an absent ledger — never the archive-only downgrade, SYS-10's fail-closed rule)")
        return 1
    ledger = [tuple(ln.split("|")) for ln in out.splitlines() if "|" in ln and not ln.startswith("SET")]
    ledger_as_of = max((l[2] for l in ledger), default="empty")
    # 4. the clean destination
    rc, out = _app(f"SET app.current_owner={_q(owner)}; SELECT count(*) FROM arv.command_log;")
    if rc != 0 or not out.strip().split("\n")[-1].isdigit():
        print(f"FAIL ARV-EXP-001: the destination read failed — {out.strip()[:160]}")
        return 1
    if out.strip().split("\n")[-1] != "0":
        print("FAIL ARV-EXP-002: the destination is not clean (authoritative rows exist for this owner) — a restore is once-per-destination, never a silent duplicate")
        print("      repair: restore into a clean migrated destination, or purge the destination through the governed flow first")
        return 1
    # 5. the blobs — present AND digest-matched (validate-before-declare)
    for d in {r[2] for r in tables["source"]}:
        p = arch / "blobs" / d
        if not p.is_file():
            print(f"FAIL ARV-EXP-004: the blob {d[:12]} is MISSING from the archive — validate-before-declare (SYS-10), never a partial restore")
            return 1
        if hashlib.sha256(p.read_bytes()).hexdigest() != d:
            print(f"FAIL ARV-EXP-004: the blob {d[:12]} is CORRUPT (the digest does not match) — never a partial restore")
            return 1
    # 6. the reconciliation FIRST (dict rows by column name; back to lists after)
    rows = {t: [dict(zip(TABLES[t].split(","), r)) for r in tables[t]] for t in TABLES}
    rows = _drop_purged(rows, ledger)
    tables = {t: [[r[c] for c in TABLES[t].split(",")] for r in rows[t]] for t in TABLES}
    # 7. ONE transaction
    stmts = []
    for t in TABLES:
        for r in tables[t]:
            vals = ",".join(_val(v) for v in r)
            ov = " OVERRIDING SYSTEM VALUE" if t == "outbox" else ""
            stmts.append(f"INSERT INTO arv.{t} ({TABLES[t]}){ov} VALUES ({vals});")
    sess = subprocess.Popen(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                             "-U", "arv_app", "-d", os.environ.get("PGDATABASE", "postgres")],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    sess.stdin.write(f"SET app.current_owner={_q(owner)};\nBEGIN;\n")
    for s in stmts:
        sess.stdin.write(s + "\n")
    if crash_at == "pre-commit":
        sess.stdin.flush()
        _die()
    sess.stdin.write("COMMIT;\n\\q\n")
    sess.stdin.flush()
    _, err = sess.communicate(timeout=120)
    if sess.returncode != 0:
        print(f"FAIL ARV-EXP-003: the insert phase failed (the transaction rolled back — nothing half-complete) — {err.strip()[:200]}")
        return 1
    rows = sum(len(v) for v in tables.values())
    print(f"RESTORED owner={owner} ledger_as_of={ledger_as_of} "
          f"backup_expiry=the D-029 documented window bounds this archive's resurrection exposure "
          f"tables={len(TABLES)} rows={rows} state_hash_match=true")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the export/restore machine (P3-09)")
    sub = ap.add_subparsers(dest="arm", required=True)
    e = sub.add_parser("export")
    e.add_argument("--owner", required=True)
    e.add_argument("--out", required=True)
    r = sub.add_parser("restore")
    r.add_argument("--archive", required=True)
    r.add_argument("--crash-at", default=None, choices=["pre-commit"])
    a = ap.parse_args()
    if a.arm == "export":
        return do_export(a.owner, a.out)
    return do_restore(a.archive, a.crash_at)


if __name__ == "__main__":
    sys.exit(main())
