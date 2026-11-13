#!/usr/bin/env python3
"""harness/tests/test_export.py — P3-09 acceptance suite (CLAIM-060, the
export/restore machine + the integrated durable-capture proof; PLAN's P3-09
card; RTM §3.7 + SYS-10 + D-029). Red-first (LAW-11): at CLAIM-059's merged
head 7df713b the suite fails with ARV-TEST-000 (machinery-absent;
red-01.txt).

THE CONTRACT: export = the authoritative records (work, source, anchor,
highlight, bookmark, note + their lifecycle events + note_reference,
command_log, outbox) + the blob references + the purge/retention state,
under an EXPLICIT VERSIONED MANIFEST with the canonical state hash; restore
validates references and blob availability BEFORE declaring completion (the
RTM §3.7 manifest_complete -> restored_pending_validation -> restored
machine); THE PURGE-LEDGER RECONCILIATION RUNS FIRST (SYS-10: the
destination's CURRENT ledger wins over older archive content — a purge
cannot be resurrected by restore); the no-ledger path is FAIL-CLOSED with a
POSITIVE absence determination (an unreadable ledger is a typed
non-restoring outcome, never a silent archive-only downgrade); a genuinely
clean destination completes as an EXPLICITLY scoped owner action naming (a)
the adopted ledger's as-of time and (b) the documented backup-expiry window
(D-029); the restore is TRANSACTIONAL (an interruption leaves nothing
half-complete); the derived indexes REBUILD from the restored authoritative
state (never exported); the equality verification is INDEPENDENT (arv_read
on both databases — a separate role and path from the restore).

Refusal codes: ARV-EXP-001 the usage class; ARV-EXP-002 the non-clean
destination (a second restore never silently duplicates); ARV-EXP-003 the
malformed/tampered manifest (the state-hash mismatch is the tamper proof);
ARV-EXP-004 the missing/corrupt blob (validate-before-declare); ARV-EXP-005
the unknown format version; ARV-EXP-006 the unreadable ledger (the typed
non-restoring outcome); ARV-PRG-001 the purge ledger's append-only law.

Cases (the EXP registry; each pin's full statement lives at its check()):
  EXP-01 the export form: the versioned manifest, the canonical table set,
         the blob copies digest-verified, the canonical state hash
  EXP-02 restore + the equality: every exported table's rows byte-equal on
         the destination (the INDEPENDENT arv_read comparison, per-family
         sorted rows), the restore's own state-hash self-check true
  EXP-03 repeated restore: a second clean destination restores equal; a
         second restore into the SAME destination is refused (ARV-EXP-002)
         with zero new rows
  EXP-04 the missing blob: the archive with a blob removed refuses
         BEFORE any insert (zero rows — validate-before-declare)
  EXP-05 the malformed archive: the truncated manifest, the tampered row
         (the state-hash mismatch), the unknown version — each a named
         refusal with zero rows
  EXP-06 the interrupted restore: the crash injection mid-restore leaves
         ZERO rows (the transactional rollback); the re-run completes and
         equals
  EXP-07 purge then restore: the destination's ledger entry for a note
         drops the note's every row (revisions, lifecycle, references); a
         ledger entry for a source drops the capture tree (the source, its
         anchors, the highlights/bookmarks anchored to it, their
         lifecycles); the ledger WINS — the export never resurrects
  EXP-08 the no-ledger law: the dropped ledger table is the typed
         non-restoring outcome (zero rows, never the archive-only
         downgrade); the genuinely clean destination completes naming the
         ledger's as-of AND the backup-expiry window (D-029's explicit
         scope)
  EXP-09 the rebuild: after the restore, rebuild_keyword_index on the
         destination re-derives the index and the searches answer the same
         as the source (the corrupt-index class: the index deleted first,
         the rebuild restores the answers)
  EXP-10 the substrate + the scoping: the purge ledger append-only (the
         UPDATE and the DELETE both refused ARV-PRG-001), RLS-forced, the
         0013 schema audits; the export's owner scoping (B's rows never in
         A's manifest)

Run: python3 harness/tests/test_export.py   (exit 0 = green)
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the export arm + the migration
# must be ABSENT at the RED tree — the implementation lands after this RED,
# never before it (LAW-11; the SYN/KWR precedent form)
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "export.py"),
                         "export", "--help"], capture_output=True, text=True)
_absent_arm = not _probe.stdout.strip() or "unrecognized" in _probe.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0013_*.sql"))
if _absent_arm or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-09 export/restore machinery is absent "
          f"(machinery-absent class; the export arm absent: {_absent_arm}; "
          f"migration 0013 present: {bool(_mig)}) — the implementation lands "
          "after this RED, never before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

SRC = DST = None
ENV = None

TEXT = ("The export corpus: the perennial phrase rides here.\n"
        "A second line with the capture window inside.\n")


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def cli(*args, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=300, env=env or ENV)


def cmd(op: str, *args, owner="A", key=None, env=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args, env=env)


def exp(*args, env=None) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "export.py"), *args, env=env or ENV)


def audit(db: str, query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_read", "-d", db, "-c", query],
                           capture_output=True, text=True, timeout=60,
                           env=ENV).stdout.strip()


def app_sql(db: str, sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_app", "-d", db,
                            "-c", f"SET app.current_owner='{owner}'; {sql}"],
                           capture_output=True, text=True, timeout=60, env=ENV)


def su_sql(db: str, sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "postgres", "-d", db, "-c", sql],
                          capture_output=True, text=True, timeout=60, env=ENV)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


TABLES = ("work", "source", "extraction_generation", "reading_position",
          "anchor", "highlight", "highlight_lifecycle",
          "bookmark", "bookmark_lifecycle", "note", "note_lifecycle",
          "journal_block", "reading_list", "note_reference",
          "reading_list_member", "reading_session",
          "command_log", "outbox", "purge_ledger")
# the per-table canonical TSV form read through arv_read (the INDEPENDENT
# path — a separate role from the restore's own session; SYS-10's rule).
# P4-F (CLAIM-079): the three P4-C families + the generation binding
# substrate join the manifest set — the widened authoritative export (the
# owning suite's table set follows the widened TABLES; the fixture writes
# none of them, so the pins observe the EMPTY rows honestly). The SEV
# repair (F-079-2) adds the AUTHORED reading_position family (0014's
# append-only position rows — the owner's saved position, exported with
# its generation binding); F-079-1's reorder rides the machine's TABLES
# order itself (journal_block/reading_list BEFORE note_reference — 0018's
# ARV-NTE-003 guard checks the journal-block target at insert time).
_TSV = {
    "work": "SELECT id||'|'||title FROM arv.work WHERE owner_scope='{}' ORDER BY id",
    "source": "SELECT id||'|'||digest FROM arv.source WHERE owner_scope='{}' ORDER BY id",
    "extraction_generation": "SELECT id||'|'||state FROM arv.extraction_generation WHERE owner_scope='{}' ORDER BY id",
    "reading_position": "SELECT source_id||'|'||save_ordinal||'|'||start_off||'|'||end_off FROM arv.reading_position WHERE owner_scope='{}' ORDER BY source_id, save_ordinal",
    "anchor": "SELECT id||'|'||source_id FROM arv.anchor WHERE owner_scope='{}' ORDER BY id",
    "highlight": "SELECT id||'|'||revision||'|'||selected_text FROM arv.highlight WHERE owner_scope='{}' ORDER BY id, revision",
    "highlight_lifecycle": "SELECT highlight_id||'|'||event FROM arv.highlight_lifecycle WHERE owner_scope='{}' ORDER BY id",
    "bookmark": "SELECT id||'|'||revision FROM arv.bookmark WHERE owner_scope='{}' ORDER BY id, revision",
    "bookmark_lifecycle": "SELECT bookmark_id||'|'||event FROM arv.bookmark_lifecycle WHERE owner_scope='{}' ORDER BY id",
    "note": "SELECT id||'|'||revision||'|'||content FROM arv.note WHERE owner_scope='{}' ORDER BY id, revision",
    "note_lifecycle": "SELECT note_id||'|'||event FROM arv.note_lifecycle WHERE owner_scope='{}' ORDER BY id",
    "note_reference": "SELECT note_id||'|'||ref_kind||'|'||ref_id FROM arv.note_reference WHERE owner_scope='{}' ORDER BY id",
    "journal_block": "SELECT id||'|'||revision FROM arv.journal_block WHERE owner_scope='{}' ORDER BY id, revision",
    "reading_list": "SELECT id||'|'||name FROM arv.reading_list WHERE owner_scope='{}' ORDER BY id",
    "reading_list_member": "SELECT list_id||'|'||source_id||'|'||op FROM arv.reading_list_member WHERE owner_scope='{}' ORDER BY id",
    "reading_session": "SELECT source_id||'|'||event FROM arv.reading_session WHERE owner_scope='{}' ORDER BY id",
    "command_log": "SELECT idempotency_key||'|'||body_hash FROM arv.command_log WHERE owner_scope='{}' ORDER BY idempotency_key",
    "outbox": "SELECT idempotency_key||'|'||state FROM arv.outbox WHERE owner_scope='{}' ORDER BY idempotency_key",
    "purge_ledger": "SELECT kind||'|'||entity_id FROM arv.purge_ledger WHERE owner_scope='{}' ORDER BY kind, entity_id",
}


def tsv(db: str, table: str, owner: str = "A") -> list:
    q = _TSV[table].format(owner)
    return [ln for ln in audit(db, q).split("\n") if ln.strip()]


def counts_equal(tables=None, owner="A", dst=None) -> bool:
    d = dst or DST
    for t in (tables or TABLES):
        if tsv(SRC, t, owner) != tsv(d, t, owner):
            return False
    return True


def main() -> int:
    global SRC, DST, ENV
    SRC = pg.create_scratch_db("p309src")
    DST = pg.create_scratch_db("p309dst")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=SRC, ARV_BLOB_DIR=blob_dir)
    try:
        for db in (SRC, DST):
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=180,
                           env=dict(ENV, PGDATABASE=db), check=True)
        dst_env = dict(ENV, PGDATABASE=DST)

        # the fixture: a full-family library on SRC (owner A) + one B note
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "export.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("perennial phrase")
        e1 = s1 + len("perennial phrase")
        s2 = TEXT.index("capture window")
        e2 = s2 + len("capture window")
        pi = cmd("import_source", "--file", str(src_file), "--media-type",
                 "text/plain", "--title", "The Export Corpus", key="ex-imp1")
        sid = ack_field(pi, "result_ref")
        ph = cmd("create_highlight", "--source-id", sid, "--start", str(s1),
                 "--end", str(e1), key="ex-hl1")
        hid = ack_field(ph, "result_ref")
        pbm = cmd("create_bookmark", "--source-id", sid, "--start", str(s2),
                  "--end", str(e2), key="ex-bm1")
        bm_id = ack_field(pbm, "result_ref")
        pn = cmd("create_note", "--content",
                 "The export note: the welkin token rides once.",
                 "--ref", f"highlight:{hid}@1", key="ex-n1")
        nid = ack_field(pn, "result_ref")
        cmd("revise_note", "--id", nid, "--content",
            "The export note revised: the welkin token stays.", key="ex-n1r")
        cmd("tombstone_note", "--id", nid, key="ex-n1t")
        cmd("restore_note", "--id", nid, key="ex-n1rr")
        pb_note = cmd("create_note", "--content", "B's private welkin thinking.",
                      key="ex-nB", owner="B")

        # ---- EXP-01 — the export form
        arch = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch-"))
        r1 = exp("export", "--owner", "A", "--out", str(arch))
        man = arch / "manifest.json"
        m = json.loads(man.read_text()) if man.is_file() else {}
        blobs = sorted(p.name for p in (arch / "blobs").glob("*")) if (arch / "blobs").is_dir() else []
        src_digest = audit(SRC, f"SELECT digest FROM arv.source WHERE id='{sid}';")
        blob_ok = all((pathlib.Path(arch / "blobs" / b).stat().st_size > 0 for b in blobs))
        ok1 = (r1.returncode == 0 and man.is_file()
               and m.get("format") == "arv-export-1" and m.get("owner") == "A"
               and set(m.get("tables", {}).keys()) == set(TABLES)
               and len(m.get("state_hash", "")) == 64
               and src_digest in blobs and blob_ok
               and len(m["tables"]["note"]) == 2 and len(m["tables"]["note_lifecycle"]) == 2)
        check("EXP-01", ok1,
              "the export form: the versioned manifest (format arv-export-1, the owner, the authoritative table set incl. the outbox state, the purge ledger, and P4-F's widened families — the journal blocks, the reading lists + membership, the session events, the generation binding substrate), the canonical state hash (64-hex over the sorted table rows), the blob copies present and non-empty (the source's digest among them) — export = authoritative records + blob references + the purge/retention state under an explicit versioned manifest (SYS-10's interface)",
              "the export reads through the owner-scoped session (RLS — B's rows structurally absent), serializes each table canonically, hashes the whole, and copies the referenced blobs by digest")

        # ---- EXP-02 — restore + the equality (the INDEPENDENT comparison)
        r2 = exp("restore", "--archive", str(arch), env=dst_env)
        self_check = "state_hash_match=true" in r2.stdout
        ledger_named = "ledger_as_of=" in r2.stdout and "backup_expiry" in r2.stdout
        ok2 = (r2.returncode == 0 and self_check and ledger_named
               and counts_equal())
        check("EXP-02", ok2,
              "restore + the equality: the restore into the clean migrated destination completes with its own state-hash self-check TRUE and the typed completion naming the ledger's as-of and the backup-expiry window; the INDEPENDENT arv_read comparison (a separate role and path from the restore's session) finds every exported table's rows byte-equal on both databases — the count-and-content equality over the whole authoritative set",
              "the restore validates references and blobs BEFORE declaring completion (SYS-10), inserts the whole authoritative set in ONE transaction, and the equality is verified through arv_read — never the restore's own session")

        # ---- EXP-03 — repeated restore
        dst2 = pg.create_scratch_db("p309dst2")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=dst2), check=True)
        r3a = exp("restore", "--archive", str(arch), env=dict(ENV, PGDATABASE=dst2))
        eq3 = counts_equal(dst=dst2)
        r3b = exp("restore", "--archive", str(arch), env=dst_env)
        cnt_after = audit(DST, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        ok3 = (r3a.returncode == 0 and eq3
               and r3b.returncode == 1 and "ARV-EXP-002" in r3b.stdout
               and cnt_after == "2")
        check("EXP-03", ok3,
              "repeated restore: a SECOND clean destination restores to the same equality (the archive is a reusable substrate); a second restore into the SAME destination is REFUSED with the named code (ARV-EXP-002 — the destination is no longer clean) and the row counts are unchanged — never a silent duplicate",
              "the clean-destination check runs before any insert; the restore is once-per-destination by construction (the append-only substrate would refuse duplicate PKs, but the refusal must be the honest named one at the boundary)")
        pg.drop_scratch_db(dst2)

        # ---- EXP-04 — the missing blob
        arch4 = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch4-"))
        shutil.copytree(arch, arch4, dirs_exist_ok=True)
        (arch4 / "blobs" / src_digest).unlink()
        db4 = pg.create_scratch_db("p309d4")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db4), check=True)
        r4 = exp("restore", "--archive", str(arch4), env=dict(ENV, PGDATABASE=db4))
        cnt4 = audit(db4, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        ok4 = (r4.returncode == 1 and "ARV-EXP-004" in r4.stdout and cnt4 == "0")
        check("EXP-04", ok4,
              "the missing blob: the archive with the source's blob removed REFUSES with the named code BEFORE any insert (zero rows on the migrated destination) — validate-before-declare (RTM §3.7's restored_pending_validation -> failed edge: missing blob is the named failure, nothing half-complete)",
              "the blob availability check (present AND digest-matched) precedes the insert phase; a missing blob is never a warning")
        pg.drop_scratch_db(db4)

        # ---- EXP-05 — the malformed archive
        db5 = pg.create_scratch_db("p309d5")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db5), check=True)
        e5env = dict(ENV, PGDATABASE=db5)
        arch5 = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch5-"))
        shutil.copytree(arch, arch5, dirs_exist_ok=True)
        (arch5 / "manifest.json").write_text('{"format": "arv-export-1", "trunc')
        r5a = exp("restore", "--archive", str(arch5), env=e5env)
        arch5b = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch5b-"))
        shutil.copytree(arch, arch5b, dirs_exist_ok=True)
        m5 = json.loads((arch5b / "manifest.json").read_text())
        m5["tables"]["note"][0][2] = "TAMPERED CONTENT"
        (arch5b / "manifest.json").write_text(json.dumps(m5))
        r5b = exp("restore", "--archive", str(arch5b), env=e5env)
        arch5c = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch5c-"))
        shutil.copytree(arch, arch5c, dirs_exist_ok=True)
        m5c = json.loads((arch5c / "manifest.json").read_text())
        m5c["format"] = "arv-export-999"
        (arch5c / "manifest.json").write_text(json.dumps(m5c))
        r5c = exp("restore", "--archive", str(arch5c), env=e5env)
        cnt5 = audit(db5, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        ok5 = (r5a.returncode == 1 and "ARV-EXP-003" in r5a.stdout
               and r5b.returncode == 1 and "ARV-EXP-003" in r5b.stdout
               and r5c.returncode == 1 and "ARV-EXP-005" in r5c.stdout
               and cnt5 == "0")
        check("EXP-05", ok5,
              "the malformed archive: the truncated manifest, the TAMPERED row (the state-hash recomputation catches the edit — the hash is the tamper proof), and the unknown format version each refuse with their named codes and leave ZERO rows on the destination",
              "the manifest's parse, the version gate, and the state-hash recomputation precede any insert; a tampered archive is never a partially-trusted one")
        pg.drop_scratch_db(db5)

        # ---- EXP-06 — the interrupted restore
        db6 = pg.create_scratch_db("p309d6")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db6), check=True)
        r6a = exp("restore", "--archive", str(arch), "--crash-at", "pre-commit",
                  env=dict(ENV, PGDATABASE=db6))
        cnt6 = audit(db6, "SELECT count(*) FROM arv.source WHERE owner_scope='A';")
        r6b = exp("restore", "--archive", str(arch), env=dict(ENV, PGDATABASE=db6))
        eq6 = counts_equal(dst=db6)
        ok6 = (r6a.returncode != 0 and cnt6 == "0"
               and r6b.returncode == 0 and eq6)
        check("EXP-06", ok6,
              "the interrupted restore: the crash injection mid-restore (after the inserts, before the commit) leaves ZERO rows — the whole restore is ONE transaction, the rolled-back state is the clean destination again (nothing half-complete, RTM §3.7's failed edge); the re-run completes and the full equality holds",
              "the insert phase rides a single BEGIN..COMMIT; the interruption is observable as the clean-destination invariant (zero rows), never as a partial library")
        pg.drop_scratch_db(db6)

        # ---- EXP-07 — purge then restore (the ledger WINS)
        db7 = pg.create_scratch_db("p309d7")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db7), check=True)
        e7 = dict(ENV, PGDATABASE=db7)
        # the destination's CURRENT ledger: the note AND the source are purged
        app_sql(db7, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, "
                     f"reason, actor, created_at) VALUES ('A', 'note', '{nid}', "
                     f"'the governed purge (the test substrate surface)', 'owner', now());")
        app_sql(db7, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, "
                     f"reason, actor, created_at) VALUES ('A', 'source', '{sid}', "
                     f"'the governed purge (the test substrate surface)', 'owner', now());")
        r7 = exp("restore", "--archive", str(arch), env=e7)
        note_gone = audit(db7, f"SELECT count(*) FROM arv.note WHERE id='{nid}';")
        note_lc_gone = audit(db7, f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{nid}';")
        note_ref_gone = audit(db7, f"SELECT count(*) FROM arv.note_reference WHERE note_id='{nid}';")
        src_gone = audit(db7, f"SELECT count(*) FROM arv.source WHERE id='{sid}';")
        anchors_gone = audit(db7, "SELECT count(*) FROM arv.anchor WHERE owner_scope='A';")
        hl_gone = audit(db7, f"SELECT count(*) FROM arv.highlight WHERE id='{hid}';")
        bm_gone = audit(db7, f"SELECT count(*) FROM arv.bookmark WHERE id='{bm_id}';")
        work_kept = audit(db7, "SELECT count(*) FROM arv.work WHERE owner_scope='A';")
        cl_kept = audit(db7, "SELECT count(*) FROM arv.command_log WHERE owner_scope='A';")
        ok7 = (r7.returncode == 0 and note_gone == "0" and note_lc_gone == "0"
               and note_ref_gone == "0" and src_gone == "0" and anchors_gone == "0"
               and hl_gone == "0" and bm_gone == "0"
               and work_kept == "1" and cl_kept == str(len(tsv(SRC, "command_log"))))
        check("EXP-07", ok7,
              "purge then restore: the destination's CURRENT ledger entries WIN over the older archive content — the ledgered NOTE drops its every row (both revisions, both lifecycle events, its references) and the ledgered SOURCE drops the whole capture tree (the source, its anchors, the highlight and the bookmark anchored to it, their lifecycles); the un-purged authoritative state (the work, the full command log) restores intact — a purge cannot be resurrected by restore (SYS-10's permanence rule)",
              "the reconciliation runs FIRST (before any insert): the ledgered entity keys intersect the archive's rows and the drop is by construction, never a post-hoc cleanup")
        pg.drop_scratch_db(db7)

        # ---- EXP-08 — the no-ledger law (fail-closed + the explicit scope)
        db8 = pg.create_scratch_db("p309d8")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db8), check=True)
        su_sql(db8, "DROP TABLE arv.purge_ledger;")
        r8a = exp("restore", "--archive", str(arch), env=dict(ENV, PGDATABASE=db8))
        cnt8 = audit(db8, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        db8b = pg.create_scratch_db("p309d8b")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db8b), check=True)
        r8b = exp("restore", "--archive", str(arch), env=dict(ENV, PGDATABASE=db8b))
        asof = "ledger_as_of=empty" in r8b.stdout
        expiry = "backup_expiry" in r8b.stdout
        eq8 = counts_equal(dst=db8b)
        ok8 = (r8a.returncode == 1 and "ARV-EXP-006" in r8a.stdout and cnt8 == "0"
               and r8b.returncode == 0 and asof and expiry and eq8)
        check("EXP-08", ok8,
              "the no-ledger law: the UNREADABLE ledger (the table dropped — the read-error/outage class) is the typed NON-RESTORING outcome (ARV-EXP-006, zero rows) — an unreadable ledger is never treated as absent, never a silent downgrade to the archive-only path; the GENUINELY clean destination (the empty ledger, the positive absence determination) completes as an explicitly scoped owner action NAMING the adopted ledger's as-of (empty) AND the documented backup-expiry window (D-029 — the window that bounds this archive's resurrection exposure)",
              "the ledger read requires a POSITIVE answer (the table answers 'zero rows for this owner'); anything else is the typed refusal; the clean-path completion prints the explicit scope")
        pg.drop_scratch_db(db8)
        pg.drop_scratch_db(db8b)

        # ---- EXP-09 — the rebuild (the derived layer re-derives)
        # P4-00a amendment (CLAIM-062, disclosed): the search arm now ALWAYS
        # prints the column header (the labeled form — CON-05; the Phase 3
        # exit gate's routed repair), so the EMPTY-index search answers with
        # the header ALONE — zero result rows, never pure silence. The pin's
        # substance is unchanged: the index is empty pre-rebuild and the
        # searches answer exactly as the source post-rebuild.
        app_sql(DST, "DELETE FROM arv.keyword_index;")
        empty_search = cli(str(REPO / "harness" / "query.py"), "search", "--owner", "A",
                           "welkin", env=dst_env)
        rb = cmd("rebuild_keyword_index", key="ex-rebuild-1", env=dst_env)
        s_dst = cli(str(REPO / "harness" / "query.py"), "search", "--owner", "A",
                    "welkin", env=dst_env)
        s_src = cli(str(REPO / "harness" / "query.py"), "search", "--owner", "A",
                    "welkin", env=ENV)
        _empty_lines = [ln for ln in empty_search.stdout.strip().split("\n") if ln.strip()]
        # P4-00b amendment (CLAIM-063, disclosed — the second extension of this
        # line, the P4-00a precedent): the search header now carries the
        # api_version token (BND-06's frozen form). The pin's substance is
        # unchanged: the EMPTY-index search answers with the header ALONE.
        _hdr = "# api_version=1 kind|entity_id|revision|matched_terms"
        ok9 = (empty_search.returncode == 0
               and _empty_lines == [_hdr]
               and rb.returncode == 0 and "status=committed" in rb.stdout
               and s_dst.returncode == 0 and bool(s_dst.stdout.strip())
               and sorted(s_dst.stdout.strip().split("\n")) == sorted(s_src.stdout.strip().split("\n")))
        check("EXP-09", ok9,
              "the rebuild: the restored destination's derived index is EMPTY by construction (the index is never exported — derived state); after the deletion (the corrupt-index class) the searches return nothing; rebuild_keyword_index re-derives the index from the restored authoritative rows ALONE and the searches answer EXACTLY as the source does (the same welkin hits, the same shape) — fully_operational (RTM §3.7's final edge)",
              "the derived layer's rebuild is the landed P3-07 command over the restored authoritative state — no second derivation path, no exported index")
        # restore the index on DST for the later equality sweeps (the rebuild added a command_log row on DST only)
        _ = rb

        # ---- EXP-10 — the substrate + the scoping (the ledger row FIRST —
        # the append-only trigger is per-row, so the hostile mutations need
        # a row to hit)
        app_sql(SRC, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, "
                     f"actor, created_at) VALUES ('A', 'note', "
                     f"'00000000-0000-7000-8000-0000000000e1', 'the substrate pin', 'owner', now());")
        u10 = su_sql(SRC, "UPDATE arv.purge_ledger SET reason='x' WHERE owner_scope='A';")
        d10 = su_sql(SRC, "DELETE FROM arv.purge_ledger WHERE owner_scope='A';")
        cols = [ln for ln in audit(SRC, "SELECT column_name FROM information_schema.columns "
                                        "WHERE table_schema='arv' AND table_name='purge_ledger' "
                                        "ORDER BY ordinal_position;").split("\n") if ln.strip()]
        rls = [ln for ln in audit(SRC, "SELECT relrowsecurity::text||'|'||relforcerowsecurity::text "
                                       "FROM pg_class WHERE oid='arv.purge_ledger'::regclass;").split("\n") if ln.strip()]
        b_absent = "welkin" in json.dumps(m) and "B's private" not in json.dumps(m)
        hostile = app_sql(SRC, "SELECT count(*) FROM arv.purge_ledger WHERE owner_scope='B';")
        ok10 = ("ARV-PRG-001" in u10.stderr and "ARV-PRG-001" in d10.stderr
                and cols == ["owner_scope", "kind", "entity_id", "reason", "actor", "created_at"]
                and rls == ["true|true"]
                and b_absent
                and hostile.stdout.strip().split("\n")[-1] == "0")
        check("EXP-10", ok10,
              "the substrate + the scoping: the purge ledger is append-only at the substrate (the UPDATE and the DELETE both refused with ARV-PRG-001 — the ledger IS the permanence record, D-029); the six-column schema exact, RLS enabled AND forced; the export's owner scoping holds (B's private content never in A's manifest; the hostile cross-owner ledger read sees zero) — the ledger and the archive are owner-scoped like every authoritative surface",
              "the purge ledger's permanence is structural (the append-only trigger), the export reads through the RLS-scoped session, and the hostile reads meet the same owner isolation as the command path")
        _ = pb_note

        # ---- EXP-11 — the mid-restore ledger write (the SEV round-1 F1: the
        # restore-side TOCTOU — the ledger read must be SERIALIZED against
        # concurrent ledger writes by the restore's own transaction lock)
        db11 = pg.create_scratch_db("p309d11")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db11), check=True)
        e11env = dict(ENV, PGDATABASE=db11)
        import time as _t
        r11p = subprocess.Popen([sys.executable, str(REPO / "harness" / "export.py"),
                                 "restore", "--archive", str(arch)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                env=e11env)
        _t.sleep(1.2)  # MID-INSERT-PHASE: the reconciliation's lock is already held
        w_start = _t.monotonic()
        writer = subprocess.Popen(["psql", "-X", "-A", "-t", "-U", "arv_app", "-d", db11,
                                   "-c", f"SET app.current_owner='A'; INSERT INTO arv.purge_ledger "
                                         f"(owner_scope, kind, entity_id, reason, actor, created_at) "
                                         f"VALUES ('A', 'note', '{nid}', 'the mid-restore write', 'owner', now());"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=e11env)
        r11_out, _ = r11p.communicate(timeout=120)
        r_end = _t.monotonic()
        w_out = writer.communicate(timeout=60)
        w_end = _t.monotonic()
        class _R:  # the completed-process shape the assertions read
            returncode = r11p.returncode
            stdout = r11_out or ""
        r11 = _R()
        w_rc = writer.returncode
        writer_landed_after = w_end > r_end  # the blocking proof: the write could not commit inside the restore
        note_cnt = audit(db11, f"SELECT count(*) FROM arv.note WHERE id='{nid}';")
        led_cnt = audit(db11, f"SELECT count(*) FROM arv.purge_ledger WHERE kind='note' AND entity_id='{nid}';")
        # the LEGAL outcomes under the SERIALIZABLE reconciliation: (a) the
        # write preceded the snapshot — the note dropped; (b) the write
        # followed the restore's commit — the note present with the row (the
        # purge pending the governed command); (c) the write landed mid-flight
        # — the restore ABORTED with the typed retryable refusal and ZERO
        # rows (the re-run converges). NEVER the silent neither.
        order_a = (r11.returncode == 0 and note_cnt == "0" and led_cnt == "1")
        order_b = (r11.returncode == 0 and note_cnt == "2" and led_cnt == "1"
                   and writer_landed_after)  # the write PROVABLY followed the restore's commit
        aborted = (r11.returncode == 1 and "ARV-EXP-007" in r11.stdout
                   and note_cnt == "0")
        if aborted:
            r11b = exp("restore", "--archive", str(arch), env=e11env)
            note_cnt = audit(db11, f"SELECT count(*) FROM arv.note WHERE id='{nid}';")
            aborted = aborted and r11b.returncode == 0 and note_cnt == "0"
        ok11 = (w_rc == 0 and (order_a or order_b or aborted))
        check("EXP-11", ok11,
              "the mid-restore ledger write: a purge-ledger insert attempted DURING the restore is SERIALIZED against the reconciliation — the outcome is one of the three legal forms: the write observed (the note dropped from the restored set), the write after the commit (the note restored, the row present — the purge pending the governed command, D-011's flow), or the typed serialization abort (ARV-EXP-007, zero rows, the re-run converging on the new ledger state); never the silent neither (the note present while the reconciliation claimed an empty ledger)",
              "the reconciliation's ledger read happens INSIDE the SERIALIZABLE restore transaction — a concurrent ledger write is serially ordered against it, never interleaved past it")
        pg.drop_scratch_db(db11)

        # ---- EXP-12 — the overlapping ledger entry (the SEV round-1 F2: the
        # promised ON CONFLICT DO NOTHING merge, never a mislabeled failure)
        db12 = pg.create_scratch_db("p309d12")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db12), check=True)
        e12env = dict(ENV, PGDATABASE=db12)
        app_sql(db12, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, "
                      f"actor, created_at) VALUES ('A', 'note', '{nid}', "
                      f"'the destination current entry', 'owner', now());")
        arch12 = pathlib.Path(tempfile.mkdtemp(prefix="arv-arch12-"))
        app_sql(SRC, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, "
                     f"actor, created_at) VALUES ('A', 'note', '{nid}', "
                     f"'the archive older entry', 'owner', now());")
        exp("export", "--owner", "A", "--out", str(arch12))
        r12 = exp("restore", "--archive", str(arch12), env=e12env)
        reason12 = audit(db12, f"SELECT reason FROM arv.purge_ledger WHERE kind='note' AND entity_id='{nid}';")
        note12 = audit(db12, f"SELECT count(*) FROM arv.note WHERE id='{nid}';")
        ok12 = (r12.returncode == 0 and reason12 == "the destination current entry"
                and note12 == "0")
        check("EXP-12", ok12,
              "the overlapping ledger entry: the destination's current entry and the archive's older entry for the SAME (owner, kind, entity) — the restore MERGES (ON CONFLICT DO NOTHING: the destination's reason preserved, never a duplicate-key crash, never the mislabeled manifest failure) and the reconciliation drops the ledgered entity either way (both entries name it)",
              "the archive's ledger rows merge on conflict with the destination's current entries staying authoritative — the permanence record is additive, never overwritten")
        pg.drop_scratch_db(db12)

        # ---- EXP-13 — the stray-row gate (the SEV round-1 F5: every
        # authoritative table checked, never the command_log proxy alone)
        db13 = pg.create_scratch_db("p309d13")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db13), check=True)
        e13env = dict(ENV, PGDATABASE=db13)
        app_sql(db13, "INSERT INTO arv.note (id, revision, content, owner_scope, actor, "
                      "run_id, input_hash, idempotency_key, created_at) VALUES "
                      "('00000000-0000-7000-8000-0000000000f9', 1, 'a stray row with no "
                      "command_log', 'A', 'owner', 'run-stray', 'ih', 'stray-1', now());")
        r13 = exp("restore", "--archive", str(arch), env=e13env)
        stray = audit(db13, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        ok13 = (r13.returncode == 1 and "ARV-EXP-002" in r13.stdout and stray == "1")
        check("EXP-13", ok13,
              "the stray-row gate: a destination carrying a single stray authoritative row with NO command_log entry (the hostile direct-insert class) still REFUSES the restore (ARV-EXP-002) — the clean-destination check covers EVERY authoritative table, never the command_log count alone; the stray row is untouched (zero new rows)",
              "the gate is the union count over the whole authoritative set — any pre-existing owner content refuses the restore, never a silent mixed state")
        pg.drop_scratch_db(db13)

        # ---- EXP-14 — the purged-highlight reference cascade (the SEV round-1
        # F3: the reference rows pointing at a purged entity drop with it)
        db14 = pg.create_scratch_db("p309d14")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db14), check=True)
        e14env = dict(ENV, PGDATABASE=db14)
        app_sql(db14, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, "
                      f"actor, created_at) VALUES ('A', 'highlight', '{hid}', "
                      f"'the governed purge (the test substrate surface)', 'owner', now());")
        r14 = exp("restore", "--archive", str(arch), env=e14env)
        hl14 = audit(db14, f"SELECT count(*) FROM arv.highlight WHERE id='{hid}';")
        refs14 = audit(db14, f"SELECT count(*) FROM arv.note_reference WHERE ref_kind='highlight' AND ref_id='{hid}';")
        note14 = audit(db14, f"SELECT count(*) FROM arv.note WHERE id='{nid}';")
        ok14 = (r14.returncode == 0 and hl14 == "0" and refs14 == "0" and note14 == "2")
        check("EXP-14", ok14,
              "the purged-highlight reference cascade: a ledger entry for the HIGHLIGHT drops the highlight and its lifecycle AND the note_reference rows pointing at it (a reference to purged material is purge material by the tree semantics) — the referencing NOTE itself survives intact; the restore completes cleanly (never the coarse whole-archive refusal the substrate's reference guard would force)",
              "the reconciliation drops the reference rows of every purged entity kind — the D-011 cascade semantics, applied at the restore boundary")
        pg.drop_scratch_db(db14)

        # ---- EXP-15 — the purged-anchor cascade (the SEV round-2 F6: a
        # ledgered ANCHOR id is in the anchor domain — the captures anchored
        # to it drop, never the coarse whole-archive FK refusal)
        db15 = pg.create_scratch_db("p309d15")
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, timeout=180,
                       env=dict(ENV, PGDATABASE=db15), check=True)
        e15env = dict(ENV, PGDATABASE=db15)
        anchor_id = audit(SRC, f"SELECT anchor_id FROM arv.highlight WHERE id='{hid}';")
        app_sql(db15, f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, "
                      f"actor, created_at) VALUES ('A', 'anchor', '{anchor_id}', "
                      f"'the governed purge (the test substrate surface)', 'owner', now());")
        r15 = exp("restore", "--archive", str(arch), env=e15env)
        anc15 = audit(db15, f"SELECT count(*) FROM arv.anchor WHERE id='{anchor_id}';")
        hl15 = audit(db15, f"SELECT count(*) FROM arv.highlight WHERE id='{hid}';")
        bm15 = audit(db15, f"SELECT count(*) FROM arv.bookmark WHERE id='{bm_id}';")
        src15 = audit(db15, f"SELECT count(*) FROM arv.source WHERE id='{sid}';")
        refs15 = audit(db15, f"SELECT count(*) FROM arv.note_reference WHERE ref_kind='highlight' AND ref_id='{hid}';")
        ok15 = (r15.returncode == 0 and anc15 == "0" and hl15 == "0" and bm15 == "1"
                and src15 == "1" and refs15 == "0")
        check("EXP-15", ok15,
              "the purged-anchor cascade: a ledger entry for an ANCHOR (a kind the ledger's CHECK admits) drops the anchor AND every capture anchored to THAT anchor (the highlight with its lifecycle, the references pointing at it) — the BOOKMARK survives (it derived its OWN anchor row — each capture's location evidence is its own; the purge was one location, not the source's every capture), the SOURCE survives; the restore completes cleanly, never the coarse whole-archive refusal the dangling anchor_id foreign key would force",
              "the ledgered anchor ids are already in the anchor domain — the cascade maps them directly, never through the source-id domain")
        pg.drop_scratch_db(db15)

        print()
        if FAILS:
            print(f"RED — the P3-09 export/restore suite fails: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-09 acceptance suite (EXP-01..15) passes")
        return 0
    finally:
        pg.drop_scratch_db(SRC)
        pg.drop_scratch_db(DST)


if __name__ == "__main__":
    sys.exit(main())
