#!/usr/bin/env python3
"""harness/tests/test_import.py — P3-02 acceptance suite (the §3.1 import state machine).

Red-first (LAW-11): committed BEFORE the implementation; at the predecessor the
suite fails with ARV-TEST-000 (machinery-absent: recover.py / migration 0005 /
the phased crash points / the stderr-drained death classifier do not exist —
the S1/record-18 §4.1 precedent, the same waiting-for-harness class as the
P3-01 capture suite).

THE IMPORT STATE MACHINE (RTM §3.1, the freeze; PLAN's P3-02 card; SYS-06's
pre-registered paths; the Q11 baseline at RTM §7.5):

  (nonexistent) --request--> staging
  staging --blob verified--> staging_verified     [digest computed; blob readable]
  staging --blob absent/corrupt--> failed          [named reason; artifact cleaned]
  staging --crash--> staging                       [the recovery walk re-walks; no phantom Source]
  staging_verified --metadata commit--> complete   [the Source row + blob ref atomically]
  staging_verified --commit crash--> staging_verified [zero-or-one effect; the walk re-drives]
  staging_verified --invalid metadata--> failed    [named reason]
  complete --re-import (same bytes)--> complete    [a NEW Source row per Q11; the old stays]

THE RECOVERY WALK (recover.py): convergence-idempotent, OLDEST-FIRST (the
journal's created_at,id total order), terminal rows NEVER touched (the
terminal discipline, pinned by updated_at), every row's outcome NAMED (never a
silent skip), the metadata re-drive reconstructs the canonical body from the
journal row's recorded fields (hash-checked BEFORE the drive — the
reconstruction-mismatch class is ARV-IMP-001), and the orphan sweep deletes
journal-less blob residue while protecting live-staging and referenced blobs.

Cases (the IMP registry — this file is the contract's declaration):
  IMP-01 the phased import end-to-end: the journal row complete + source_id,
        the source row complete (the §2 shape), one walk changes nothing
  IMP-02 the Q11 baseline: identical bytes imported twice = TWO Source rows,
        ONE blob (byte-reuse is storage-level, never identity)
  IMP-03 two similar-but-different works: no auto-merge, no uniqueness fires
  IMP-04 the same-key retry after a clean crash: re-drive -> exactly one source
  IMP-05 crash after-staging (the journal row committed, NO blob yet): the walk
        marks failed(ARV-BLOB-002 absent); the SAME-key retry completes
  IMP-06 crash after-put (staging row + blob present): the walk verifies ->
        staging_verified -> re-drives the metadata commit -> complete
  IMP-07 the corrupt blob at the walk: failed(ARV-BLOB-003) + the unreferenced
        artifact DELETED (the delete arm); the retry re-puts and completes
  IMP-08 crash after-verify (staging_verified, blob present): the walk
        re-drives -> complete; exactly one source
  IMP-09 the lost metadata ack (post-commit-pre-ack): committed, NO ack, the
        journal row rode the commit (complete in-transaction) -> the walk
        reports already-complete; the same-key replay answers the recorded ack
        (zero-or-one: the source count stays ONE)
  IMP-10 the vanished blob at staging_verified: the re-drive re-verifies ->
        failed(ARV-BLOB-002) — NEVER a phantom complete Source
  IMP-11 hostile journal text (pipes/newlines/'MARK' in the title): the
        row_to_json reads never corrupt; the body reconstruction hash-exact;
        the title round-trips WHOLE
  IMP-12 the walk's convergence: run TWICE = identical end states; terminal
        rows' updated_at UNCHANGED (the terminal discipline)
  IMP-13 the two-crash re-drive: OLDEST-FIRST, both complete, each
        exactly-one; the same-work variant: versions 1,2,3 (the re-read ordinal)
  IMP-14 owner isolation: the journal RLS-scoped; B's walk is blind to A's
        rows; the direct-DB journal access fails closed (both layers)
  IMP-15 the 409 conflict stages NO blob (the P3-01 notverified's orphan class
        dead by construction: the replay check precedes the put)
  IMP-16 the orphan sweep: residue referenced by no source row AND no
        non-terminal journal row deleted (incl. a terminal-FAILED row's
        unreferenced digest); a live-staging row's blob and a referenced blob
        PROTECTED
  IMP-17 the journal's §2/§2.9 conventions: NO defaults on id/created_at, RLS
        forced, arv_read SELECT, the actor/state CHECKs, UNIQUE(owner,key), and
        the declared ABSENCE of the append-only trigger (mutable by design)
  IMP-20 the coherent-forged row (round-1 F3): BOTH work_id and title NULL
        with a CONSISTENT body_hash, planted by direct SQL (the CLI's CAP-007
        blocks the request shape): the walk NAMES it (ARV-IMP-004), marks the
        row failed, and CONTINUES — the later rows still driven, WALK-DONE
        still printed (never the _q(None) crash that aborted the walk)
  IMP-21 the different-body same-key retry over a crashed attempt (the #4
        finding): the command_log replay check cannot see a crashed attempt,
        so the JOURNAL row's body_hash is the crash-domain replay guard — the
        mismatched body under the same key is the named ARV-CMD-409 (zero
        effect: no UPSERT rewind, no put), never a silent field mix-up
  IMP-22 a refused failed-transition write is NAMED, never a false recovery
        (the #7 finding): the planted RAISE on the row's failed-UPDATE makes
        the walk print ARV-IMP-003 (the row is NOT failed) instead of the
        lying to=failed line — and the next walk still converges it

The SEV-7 stderr-classification cases (the planted-trigger dup-key -> 011 from
the DRAINED stderr; the killed-backend connection-class -> the §4.1 uncertain
012 resolved by the same-key replay) are CLAIM-051's own bounded slice — the
P3-01 SEV-11 routing's split form, adopted when SIZE-002's bound forced the
one-behavior-per-slice rule (LAW-05): they declare their own RED there.

Run: python3 harness/tests/test_import.py   (exit 0 = green)
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


# ---------------------------------------------------------------- the RED gate
try:
    from harness.adapters import pg  # noqa: E402
    from harness.commands import REGISTRY, canonical_body  # noqa: E402
    from harness.crash import POINTS  # noqa: E402
except ImportError as e:
    print(f"FAIL ARV-TEST-000: the kernel does not exist (waiting-for-harness) — {e}")
    sys.exit(1)

_absent_files = [str(p) for p in (REPO / "harness" / "recover.py",
                                  REPO / "harness" / "migrations" / "0005_import_journal.sql")
                 if not p.is_file()]
_absent_points = [pt for pt in ("after-staging", "after-put", "after-verify") if pt not in POINTS]
if _absent_files or "import_source" not in REGISTRY:
    print(f"FAIL ARV-TEST-000: the import-state machinery is absent (machinery-absent class; "
          f"missing files: {[p.split('/')[-1] for p in _absent_files]}; missing crash points: {_absent_points}) — "
          "P3-02's implementation lands after this RED, never before it")
    sys.exit(1)

DB = None
ENV = None
BLOB_DIR = None


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=180, env=ENV)


def import_src(key: str, title: str, file: str, owner: str = "A",
               media: str = "text/plain", work_id: str = None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), "import_source", "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
         "--file", file, "--media-type", media]
    if title is not None:
        a += ["--title", title]
    if work_id:
        a += ["--work-id", work_id]
    return cli(*a)


def crash(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "crash.py"), *args)


def walk(owner: str) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "recover.py"), "--owner", owner)


def audit(query: str, db: str = None) -> str:
    """Independent state read (LAW-13): the arv_read role, direct psql."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", db or DB, "-c", query],
                          capture_output=True, text=True, timeout=60).stdout.strip()


def jrow(key: str, cols: str = "state, fail_reason, source_id") -> str:
    return audit(f"SELECT {cols} FROM arv.import_journal "
                 f"WHERE idempotency_key='{key}' AND owner_scope='A';")


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def resident(digest: str) -> bool:
    return (pathlib.Path(BLOB_DIR) / digest).is_file()


def fresh_file(name: str, text: str) -> str:
    d = tempfile.mkdtemp(prefix="arv-imp-")
    f = pathlib.Path(d) / name
    f.write_text(text, encoding="utf-8")
    return str(f)


def main() -> int:
    global DB, ENV, BLOB_DIR
    DB = pg.create_scratch_db("p302")
    BLOB_DIR = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=BLOB_DIR)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)
        TEXT_A = "Alpha document.\nThe quick brown fox jumps over the lazy dog.\nFinal line.\n"
        TEXT_A2 = "Alpha document, second edition.\nThe quick brown fox jumps over the lazy dog.\n"
        fA, fA2 = fresh_file("alpha.md", TEXT_A), fresh_file("alpha2.md", TEXT_A2)

        # IMP-01 — the phased import end-to-end (§3.1's happy path)
        p = import_src("imp-01", "Day One", fA)
        sid, wid = ack_field(p, "result_ref"), ack_field(p, "work_id")
        jr = jrow("imp-01", "state, source_id, fail_reason")
        ok1 = (p.returncode == 0 and "status=committed" in p.stdout
               and jr.split("|")[0] == "complete" and jr.split("|")[1] == sid
               and jr.split("|")[2].strip() == ""
               and audit(f"SELECT import_state FROM arv.source WHERE id='{sid}';") == "complete"
               and audit(f"SELECT count(*) FROM arv.source;") == "1")
        w1 = walk("A")
        ok1 = ok1 and w1.returncode == 0 and "already-complete" in w1.stdout
        check("IMP-01", ok1,
              "the phased import lands the journal row complete + source_id and the source row complete; a walk over it is a no-op (already-complete)",
              "import_source must stage -> verify -> ONE metadata commit -> mark the journal complete; the walk never re-drives terminal rows")

        # IMP-02 — the Q11 baseline: identical bytes twice (§7.5: a NEW Source row; byte-reuse storage-level)
        p2 = import_src("imp-02", "Day One Copy", fA)
        sid2 = ack_field(p2, "result_ref")
        digest = hashlib.sha256(pathlib.Path(fA).read_bytes()).hexdigest()
        ok2 = (p2.returncode == 0 and sid2 != sid
               and audit("SELECT count(*) FROM arv.source;") == "2"
               and audit("SELECT count(*) FROM arv.work;") == "2"
               and jrow("imp-02").split("|")[0] == "complete"
               and resident(digest))
        check("IMP-02", ok2,
              "identical bytes imported twice = TWO Source rows under TWO works, ONE blob (byte-reuse is storage-level, never identity — the Q11 baseline)",
              "no auto-merge, no identity uniqueness: every import is its own Source; the blob store dedups by content addressing only")

        # IMP-03 — similar-but-different works: no merge, no uniqueness refusal
        p3 = import_src("imp-03", "Day One", fA2)  # same title, different bytes
        ok3 = (p3.returncode == 0
               and audit("SELECT count(*) FROM arv.work WHERE title='Day One';") == "2"
               and audit("SELECT count(*) FROM arv.source;") == "3"
               and hashlib.sha256(pathlib.Path(fA2).read_bytes()).hexdigest() != digest
               and resident(hashlib.sha256(pathlib.Path(fA2).read_bytes()).hexdigest()))
        check("IMP-03", ok3,
              "two similar-but-different works with the SAME title both land (no auto-merge, no uniqueness constraint fires — Q11)",
              "identity is the UUID only; title/byte similarity never merges or refuses")

        # IMP-04 — the same-key retry after a clean crash: exactly one source
        c1 = crash("--command", "import_source", "--point", "after-verify",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-04",
                   "--title", "Retry Case", "--file", fA)
        ok4a = (c1.returncode == 2 and "CRASHED-AT after-verify" in c1.stdout
                and jrow("imp-04").split("|")[0] == "staging_verified"
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-04';") == "0")
        r4 = import_src("imp-04", "Retry Case", fA)  # the SAME key, the same body
        sid4 = ack_field(r4, "result_ref")
        ok4 = (ok4a and r4.returncode == 0 and "status=committed" in r4.stdout
               and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-04';") == "1"
               and jrow("imp-04").split("|")[0] == "complete"
               and audit(f"SELECT count(*) FROM arv.work WHERE title='Retry Case';") == "1")
        check("IMP-04", ok4,
              "a crashed import retried under the SAME key re-drives the phases and commits EXACTLY ONE source (never two, never zero)",
              "the retry is the recovery substrate's re-drive: the journal row rewinds, the metadata commit runs once under the same idempotency key")

        # IMP-05 — crash after-staging: journal staging, NO blob -> the walk: failed(absent); the same-key retry completes
        fE5 = fresh_file("echo5.md", "Echo five bytes: the absent-blob staging case — never imported before this point.\n")
        d5 = hashlib.sha256(pathlib.Path(fE5).read_bytes()).hexdigest()
        c5 = crash("--command", "import_source", "--point", "after-staging",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-05",
                   "--title", "Absent Blob", "--file", fE5)
        ok5a = (c5.returncode == 2 and jrow("imp-05").split("|")[0] == "staging"
                and not resident(d5)
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-05';") == "0")
        w5 = walk("A")
        ok5b = (w5.returncode == 0 and "ARV-BLOB-002" in w5.stdout
                and jrow("imp-05", "state, fail_reason").split("|")[0] == "failed"
                and "ARV-BLOB-002" in jrow("imp-05", "state, fail_reason"))
        r5 = import_src("imp-05", "Absent Blob", fE5)  # failed is RETRYABLE (the card's acceptance)
        ok5 = (ok5a and ok5b and r5.returncode == 0
               and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-05';") == "1"
               and jrow("imp-05").split("|")[0] == "complete")
        check("IMP-05", ok5,
              "crash after staging (no blob put): the walk names failed(ARV-BLOB-002 absent) with NO phantom source; the SAME-key retry re-puts and completes — failed/retryable, never falsely complete",
              "the staging exit verify is the blob's readable+digest-matched proof; absent bytes are a named failure, and the retry re-runs the phases under the same key")

        # IMP-06 — crash after-put: staging + blob present -> the walk verifies -> re-drives -> complete
        c6 = crash("--command", "import_source", "--point", "after-put",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-06",
                   "--title", "Put Landed", "--file", fA)
        ok6a = (c6.returncode == 2 and jrow("imp-06").split("|")[0] == "staging"
                and resident(digest))
        w6 = walk("A")
        ok6 = (ok6a and w6.returncode == 0
               and jrow("imp-06").split("|")[0] == "complete"
               and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-06';") == "1")
        check("IMP-06", ok6,
              "crash after the put (blob present, staging): the walk re-verifies, drives staging_verified, and commits the metadata exactly once",
              "the walk re-walks staging rows whose bytes landed: verify -> staging_verified -> the metadata re-drive under the recorded key")

        # IMP-07 — the corrupt blob at the walk: failed(ARV-BLOB-003) + the unreferenced artifact DELETED; retry re-puts
        fB = fresh_file("corruptible.md", "Beta bytes for the corrupt-blob walk case.\n")
        dB = hashlib.sha256(pathlib.Path(fB).read_bytes()).hexdigest()
        c7 = crash("--command", "import_source", "--point", "after-put",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-07",
                   "--title", "Corrupt Blob", "--file", fB)
        ok7a = c7.returncode == 2 and jrow("imp-07").split("|")[0] == "staging" and resident(dB)
        (pathlib.Path(BLOB_DIR) / dB).write_bytes(b"rotten bytes that re-hash to nothing valid")  # the on-disk rot
        w7 = walk("A")
        ok7b = (w7.returncode == 0 and "ARV-BLOB-003" in w7.stdout
                and jrow("imp-07", "state, fail_reason").split("|")[0] == "failed"
                and "ARV-BLOB-003" in jrow("imp-07", "state, fail_reason")
                and not resident(dB))  # unreferenced + corrupt -> the staging artifact CLEANED
        r7 = import_src("imp-07", "Corrupt Blob", fB)  # the retry re-puts clean bytes
        ok7 = (ok7a and ok7b and r7.returncode == 0 and resident(dB)
               and jrow("imp-07").split("|")[0] == "complete"
               and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-07';") == "1")
        check("IMP-07", ok7,
              "a corrupt blob at the walk: failed(ARV-BLOB-003), the unreferenced artifact DELETED (the delete arm), and the same-key retry re-puts clean bytes and completes — never a promoted corrupt Source",
              "corruption is named and cleaned at the staging class only; a REFERENCED blob is never silently deleted (CAP-15's refusal stands)")

        # IMP-08 — crash after-verify: staging_verified -> the walk re-drives -> complete (exactly one)
        fC = fresh_file("charlie.md", "Charlie bytes: the staging_verified re-drive case.\n")
        c8 = crash("--command", "import_source", "--point", "after-verify",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-08",
                   "--title", "Staging Verified", "--file", fC)
        ok8a = (c8.returncode == 2 and jrow("imp-08").split("|")[0] == "staging_verified"
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-08';") == "0")
        w8 = walk("A")
        ok8 = (ok8a and w8.returncode == 0
               and jrow("imp-08").split("|")[0] == "complete"
               and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-08';") == "1"
               and audit("SELECT count(*) FROM arv.work WHERE title='Staging Verified';") == "1")
        check("IMP-08", ok8,
              "crash before the metadata commit (staging_verified): the walk re-drives the SAME key -> complete; exactly one source, exactly one work",
              "the staging_verified exit is the metadata commit: the walk re-drives it via the recorded fields under the original idempotency key")

        # IMP-09 — the lost metadata ack (post-commit-pre-ack): the metadata
        # transaction carried the journal's complete update ATOMICALLY (P3-02's
        # in-transaction convergence — one transaction, one truth: the journal can
        # NEVER lag the commit), so the crash leaves the row complete, the source
        # committed, and NO ack; the walk reports already-complete and the
        # same-key replay answers from the recorded state (zero-or-one).
        c9 = crash("--command", "import_source", "--point", "post-commit-pre-ack",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-09",
                   "--title", "Lost Ack", "--file", fA)
        ok9a = (c9.returncode == 2 and "status=committed" not in c9.stdout
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-09';") == "1"
                and jrow("imp-09", "state, source_id").split("|")[0] == "complete")  # converged in-transaction
        w9 = walk("A")
        sid9 = audit("SELECT id FROM arv.source WHERE idempotency_key='imp-09';")
        r9 = import_src("imp-09", "Lost Ack", fA)  # the same-key replay answers the recorded state
        ok9 = (ok9a and w9.returncode == 0 and "already-complete" in w9.stdout
               and jrow("imp-09", "state, source_id").split("|")[0] == "complete"
               and jrow("imp-09", "state, source_id").split("|")[1].strip() == sid9
               and r9.returncode == 0 and "status=replayed" in r9.stdout and "work_id=" in r9.stdout
               and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-09';") == "1")
        check("IMP-09", ok9,
              "the lost metadata ack: the journal rode the commit (complete in-transaction, source_id set), no ack emitted; the walk reports already-complete and the SAME-key replay answers status=replayed — the source count stays ONE (zero-or-one effect)",
              "the journal's complete transition rides the metadata transaction itself — one transaction, one truth; the lost-ack is recovered by the replay's recorded answer, never a second effect")

        # IMP-10 — the vanished blob at staging_verified: NEVER a phantom complete Source
        fD = fresh_file("delta.md", "Delta bytes: the phantom-closure case.\n")
        dD = hashlib.sha256(pathlib.Path(fD).read_bytes()).hexdigest()
        c10 = crash("--command", "import_source", "--point", "after-verify",
                    "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-10",
                    "--title", "Vanished Blob", "--file", fD)
        (pathlib.Path(BLOB_DIR) / dD).unlink()  # the bytes vanish between verify and the re-drive
        w10 = walk("A")
        ok10 = (c10.returncode == 2 and w10.returncode == 0
                and jrow("imp-10", "state, fail_reason").split("|")[0] == "failed"
                and "ARV-BLOB-002" in jrow("imp-10", "state, fail_reason")
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-10';") == "0")
        check("IMP-10", ok10,
              "a blob that vanishes after verify: the re-drive RE-VERIFIES before the commit -> failed(ARV-BLOB-002), NO source row — a complete Source without bytes is impossible (§4.4)",
              "the metadata commit's precondition is the verified blob, re-checked at every drive: the phantom-complete class is closed at the walk, not just at the command")

        # IMP-11 — hostile journal text: row_to_json reads + hash-exact body reconstruction + WHOLE round-trip
        HOSTILE = "P|pe\"Mark:BEGUN\"\nline2\ttabbed"
        fE = fresh_file("hostile.md", "Hostile-title bytes.\n")
        c11 = crash("--command", "import_source", "--point", "after-verify",
                    "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-11",
                    "--title", HOSTILE, "--file", fE)
        w11 = walk("A")
        stored = audit("SELECT title FROM arv.work WHERE id=(SELECT work_id FROM arv.source "
                       "WHERE idempotency_key='imp-11');")
        ok11 = (c11.returncode == 2 and w11.returncode == 0
                and jrow("imp-11").split("|")[0] == "complete"
                and stored == HOSTILE
                and "ARV-IMP-001" not in w11.stdout
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-11';") == "1")
        check("IMP-11", ok11,
              "a title carrying pipes, quotes, a 'MARK:' marker, and a NEWLINE: the walk's row_to_json reads never corrupt, the canonical body reconstructs hash-exact (no ARV-IMP-001), and the title round-trips WHOLE",
              "journal reads are JSON at the SQL boundary (one escaped line per row) and the re-drive rebuilds the canonical body from the recorded FIELDS — never a re-parse of psql text, never marker-fragile")

        # IMP-12 — the walk's convergence: run over a FRESH staging row, then
        # twice-run = identical states; terminal rows untouched
        fL = fresh_file("lima.md", "Lima bytes: the convergence discipline case.\n")
        dL = hashlib.sha256(pathlib.Path(fL).read_bytes()).hexdigest()
        crash("--command", "import_source", "--point", "after-put",
              "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-12x",
              "--title", "Convergence", "--file", fL)
        w12a = walk("A")  # the first walk drives imp-12x to complete + sweeps
        ok12a = (w12a.returncode == 0 and jrow("imp-12x").split("|")[0] == "complete"
                and resident(dL))
        before = audit("SELECT id, state, updated_at FROM arv.import_journal ORDER BY created_at, id;")
        n_src = audit("SELECT count(*) FROM arv.source;")
        wa, wb = walk("A"), walk("A")
        after = audit("SELECT id, state, updated_at FROM arv.import_journal ORDER BY created_at, id;")
        ok12 = (ok12a and wa.returncode == 0 and wb.returncode == 0
                and before == after  # the terminal discipline: updated_at UNCHANGED across two walks
                and audit("SELECT count(*) FROM arv.source;") == n_src)
        check("IMP-12", ok12,
              "the walk is convergence-idempotent: after the first walk drives the fresh staging row to complete, running it TWICE MORE changes NOTHING (states and updated_at byte-identical; no new sources)",
              "the walk touches only non-terminal rows; complete/failed are terminal by §3.1 — the second walk must be a no-op, never a re-drive")

        # IMP-13 — the two-crash re-drive: oldest-first; both complete; the same-work variant re-reads the ordinal.
        # A --work-id crash needs an EXISTING work (the --title path creates the work INSIDE phase 3 — a crashed
        # --title import has no work yet, and crash.py prints no ACK to harvest a work_id from) — the base import
        # lands the work first, then two crashed --work-id imports pile up at staging_verified for ONE walk.
        fF0 = fresh_file("foxtrot0.md", "Foxtrot base bytes: the work-existence anchor.\n")
        p13w = import_src("imp-13w", "Foxtrot", fF0)
        wF = ack_field(p13w, "work_id")
        fF1, fF2 = fresh_file("foxtrot1.md", "Foxtrot one bytes.\n"), fresh_file("foxtrot2.md", "Foxtrot two bytes.\n")
        c13a = crash("--command", "import_source", "--point", "after-verify",
                     "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-13a",
                     "--work-id", wF, "--file", fF1)
        c13b = crash("--command", "import_source", "--point", "after-verify",
                     "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-13b",
                     "--work-id", wF, "--file", fF2)
        w13 = walk("A")
        versions = audit(f"SELECT source_version FROM arv.source WHERE work_id='{wF}' ORDER BY source_version;")
        ok13 = (p13w.returncode == 0 and c13a.returncode == 2 and c13b.returncode == 2 and w13.returncode == 0
                and jrow("imp-13a").split("|")[0] == "complete"
                and jrow("imp-13b").split("|")[0] == "complete"
                and versions.splitlines() == ["1", "2", "3"]
                and audit(f"SELECT count(*) FROM arv.source WHERE work_id='{wF}';") == "3")
        check("IMP-13", ok13,
              "two crashed imports re-driven by ONE walk: oldest-first, both complete, each exactly-one; the same-work imports re-read the ordinal and land versions 2,3 after the base's 1",
              "the walk processes the journal in created_at,id order (the stable total order); the edition ordinal is re-read at every drive — the loser never duplicates")

        # IMP-14 — owner isolation: the journal RLS-scoped; B's walk blind to A; direct-DB fails closed
        fG = fresh_file("golf.md", "Golf bytes: owner B's staging row.\n")
        c14 = crash("--command", "import_source", "--point", "after-verify",
                    "--owner", "B", "--client-id", "cli-1", "--idem-key", "imp-14",
                    "--title", "B's Work", "--file", fG)
        wB = walk("B")  # B's own walk completes B's row
        wA = walk("A")  # A's walk must be blind to it
        ok14 = (c14.returncode == 2
                and audit("SELECT count(*) FROM arv.import_journal WHERE owner_scope='B';") == "1"
                and wB.returncode == 0
                and audit("SELECT state FROM arv.import_journal WHERE idempotency_key='imp-14';") == "complete"
                and "imp-14" not in wA.stdout)
        noguc_sel = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-U", "arv_app", "-d", DB, "-c",
                                    "SELECT count(*) FROM arv.import_journal;"],
                                   capture_output=True, text=True, timeout=60)
        noguc_ins = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "arv_app", "-d", DB, "-c",
                                    "INSERT INTO arv.import_journal (id, owner_scope, actor, idempotency_key, "
                                    "client_id, digest, media_type, byte_size, acquired_via, state, body_hash, "
                                    "run_id, input_hash, created_at, updated_at) VALUES "
                                    "('22222222-2222-7222-8222-222222222222', 'A', 'owner', 'rogue', 'cli', "
                                    "'" + "0" * 64 + "', 'text/plain', 1, 'rogue', 'staging', 'x', 'r', 'h', "
                                    "'2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z');"],
                                   capture_output=True, text=True, timeout=60)
        ok14 = ok14 and noguc_sel.returncode == 0 and noguc_sel.stdout.strip() == "0" \
            and noguc_ins.returncode != 0 \
            and ("row-level security" in noguc_ins.stdout + noguc_ins.stderr
                 or "violates row-level" in noguc_ins.stdout + noguc_ins.stderr)
        check("IMP-14", ok14,
              "the journal is owner-scoped end-to-end: B's walk completes only B's row, A's walk never sees it (RLS); arv_app WITHOUT the owner GUC sees ZERO rows (the fail-closed SELECT) and its INSERT is refused by the RLS WITH CHECK (CAP-11's form)",
              "the staging journal inherits the substrate's RLS discipline: same policy shape, same fail-closed on both layers — the walk's scope is the walking owner's rows only")

        # IMP-15 — the 409 conflict stages NO blob (the P3-01 orphan class dead by construction)
        fH = fresh_file("hotel.md", "Hotel bytes: the conflict-path no-staging case.\n")
        dH = hashlib.sha256(pathlib.Path(fH).read_bytes()).hexdigest()
        import_src("imp-15", "Conflict Base", fH)
        before_residents = sorted(p.name for p in pathlib.Path(BLOB_DIR).iterdir() if p.name[0] != ".")
        p15 = import_src("imp-15", "Conflict Base DIFFERENT BODY", fH)  # same key, different body
        after_residents = sorted(p.name for p in pathlib.Path(BLOB_DIR).iterdir() if p.name[0] != ".")
        ok15 = (p15.returncode == 1 and "ARV-CMD-409" in p15.stdout
                and before_residents == after_residents
                and audit("SELECT count(*) FROM arv.import_journal WHERE idempotency_key='imp-15';") == "1")
        check("IMP-15", ok15,
              "a same-key/different-body conflict refuses with ZERO staging: the replay check precedes the put, the store's residents unchanged (the P3-01 notverified's orphan class is dead by construction)",
              "the phased order is request -> replay check -> journal -> put -> verify -> commit: a refused command must never leave staged bytes")

        # IMP-16 — the orphan sweep: journal-less residue deleted; live-staging and referenced blobs protected
        planted = hashlib.sha256(b"orphan residue from a pre-0005 era import").hexdigest()
        (pathlib.Path(BLOB_DIR) / planted).write_bytes(b"orphan residue from a pre-0005 era import")
        fI = fresh_file("india.md", "India bytes: the live-staging protection case.\n")
        dI = hashlib.sha256(pathlib.Path(fI).read_bytes()).hexdigest()
        crash("--command", "import_source", "--point", "after-put",
              "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-16",
              "--title", "Live Staging", "--file", fI)
        w16 = walk("A")
        ok16 = (w16.returncode == 0 and not resident(planted)
                and resident(dI) and resident(digest)
                and jrow("imp-16").split("|")[0] == "complete")
        check("IMP-16", ok16,
              "the orphan sweep deletes residue referenced by no source row AND no non-terminal journal row (including a terminal-FAILED row's unreferenced digest — the designed staging-artifact cleanup) while protecting live-staging and referenced blobs",
              "the keep-set is the source-referenced digests (any owner) united with the non-terminal journal rows' digests; everything else is residue and goes")

        # IMP-17 — the journal's §2/§2.9 conventions (mutable by design: NO append-only trigger)
        defs = audit("SELECT column_name FROM information_schema.columns "
                     "WHERE table_schema='arv' AND table_name='import_journal' "
                     "AND column_name IN ('id','created_at','updated_at') AND column_default IS NOT NULL;")
        rls = audit("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                     "WHERE n.nspname='arv' AND c.relname='import_journal' "
                     "AND c.relrowsecurity AND c.relforcerowsecurity;")
        trig = audit("SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid "
                     "JOIN pg_namespace n ON n.oid=c.relnamespace WHERE NOT t.tgisinternal "
                     "AND n.nspname='arv' AND c.relname='import_journal';")
        # the grants are read by the SUPERUSER (information_schema.role_table_grants
        # shows a role only its own grants — arv_read's audit read cannot see arv_app's;
        # has_table_privilege from postgres sees both)
        privs = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                "SELECT has_table_privilege('arv_app','arv.import_journal','INSERT') || '|' || "
                                "has_table_privilege('arv_app','arv.import_journal','SELECT') || '|' || "
                                "has_table_privilege('arv_app','arv.import_journal','UPDATE') || '|' || "
                                "has_table_privilege('arv_read','arv.import_journal','SELECT') || '|' || "
                                "has_table_privilege('arv_app','arv.import_journal','DELETE');"],
                               capture_output=True, text=True, timeout=60).stdout.strip()
        badstate = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "arv_app", "-d", DB, "-c",
                                  "SET app.current_owner='A'; UPDATE arv.import_journal "
                                  "SET state='nonsense' WHERE idempotency_key='imp-01';"],
                                 capture_output=True, text=True, timeout=60)
        ok17 = (defs == "" and rls == "1" and trig == "0"
                and privs == "true|true|true|true|false"  # arv_app: INSERT+SELECT+UPDATE, arv_read: SELECT, and NO DELETE (rows transition, never erased)
                and badstate.returncode != 0 and "check" in badstate.stdout + badstate.stderr)
        check("IMP-17", ok17,
              "the journal's conventions: NO defaults on id/created_at/updated_at (LAW-24), RLS enabled+forced, the state CHECK refuses unknown states, arv_app INSERT/SELECT/UPDATE with NO DELETE (rows transition, never erased), arv_read SELECT — and NO append-only trigger (the §2.9 disposable class, mutable by design)",
              "the staging journal is the recovery substrate, not authoritative data: state transitions are UPDATEs by design, bounded by the state CHECK and RLS — the declared absence of the immutability trigger is the design, pinned here")

        # IMP-20 — the coherent-forged row (round-1 F3): BOTH NULL, a consistent
        # body_hash, planted by direct SQL (CAP-007 blocks the CLI shape only):
        # the walk NAMES it, marks failed, and CONTINUES (never the crash)
        fM = fresh_file("mike.md", "Mike bytes: the walk-continues case.\n")
        mbytes = pathlib.Path(fM).read_bytes()
        mput = hashlib.sha256(mbytes).hexdigest()
        (pathlib.Path(BLOB_DIR) / mput).write_bytes(mbytes)  # the blob resident: the verify passes
        forge_body = json.dumps({"work_id": None, "title": None, "digest": mput,
                                "media_type": "text/plain", "acquired_via": "cli-import",
                                "byte_size": len(mbytes)},
                               sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        forge_hash = hashlib.sha256(canonical_body(command="import_source", client_id="cli-1",
                                                    owner_scope="A", actor="owner",
                                                    payload=forge_body).encode()).hexdigest()
        plant20 = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "arv_app", "-d", DB, "-c",
                                 f"SET app.current_owner='A'; INSERT INTO arv.import_journal "
                                 f"(id, owner_scope, actor, idempotency_key, client_id, work_id, title, "
                                 f"digest, media_type, byte_size, acquired_via, state, body_hash, run_id, "
                                 f"input_hash, created_at, updated_at) VALUES ('44444444-4444-7444-8444-444444444444', "
                                 f"'A', 'owner', 'imp-20-forged', 'cli-1', NULL, NULL, '{mput}', 'text/plain', "
                                 f"{len(mbytes)}, 'cli-import', 'staging_verified', '{forge_hash}', 'r', 'h', "
                                 f"'2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z');"],
                                capture_output=True, text=True, timeout=60)
        c20b = crash("--command", "import_source", "--point", "after-put",
                     "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-20b",
                     "--title", "Walk Continues", "--file", fM)  # the LATER row: must still be driven
        w20 = walk("A")
        ok20 = (plant20.returncode == 0 and c20b.returncode == 2 and w20.returncode == 0
                and "ARV-IMP-004" in w20.stdout and "WALK-DONE" in w20.stdout
                and jrow("imp-20-forged", "state, fail_reason").split("|")[0] == "failed"
                and "ARV-IMP-004" in jrow("imp-20-forged", "state, fail_reason")
                and jrow("imp-20b").split("|")[0] == "complete")
        check("IMP-20", ok20,
              "the coherent-forged both-NULL row (direct SQL, hash-consistent): the walk names ARV-IMP-004, marks the row failed, and CONTINUES — the later crashed row still driven to complete, WALK-DONE still printed, never the un-named crash that aborted the walk",
              "the walk's drive pre-checks the work binding (the CLI's CAP-007 XOR mirrored at the row level): a forge is a NAMED refusal, the row fails, the walk proceeds — the fail-closed contract holds for rows no code path of the machine could have written")

        # IMP-21 — the different-body same-key retry over a crashed attempt (#4):
        # the command_log cannot see the crash; the journal row's body_hash is the guard
        fN = fresh_file("november.md", "November bytes: the crash-domain 409 case.\n")
        c21 = crash("--command", "import_source", "--point", "after-put",
                    "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-21",
                    "--title", "Body X", "--file", fN)
        ok21a = (c21.returncode == 2 and jrow("imp-21").split("|")[0] == "staging")
        p21 = import_src("imp-21", "Body Y DIFFERENT", fA)  # the same key, a DIFFERENT body
        ok21 = (ok21a and p21.returncode == 1 and "ARV-CMD-409" in p21.stdout
                and jrow("imp-21", "state, title").split("|")[0] == "staging"
                and jrow("imp-21", "state, title").split("|")[1].strip() == "Body X"
                and audit("SELECT count(*) FROM arv.source WHERE idempotency_key='imp-21';") == "0")
        check("IMP-21", ok21,
              "a different body under the same key over a crashed attempt: the journal row's body_hash is the crash-domain replay guard -> the named ARV-CMD-409, the row UNTOUCHED (still the first attempt's staging truth), zero effect — never a silent field mix-up",
              "the same key must mean the same command in the crash domain too: the replay check reads command_log AND the journal's body_hash — a mismatch is the named conflict, never an UPSERT that leaves the row claiming the first body while the source commits the second")

        # IMP-22 — a refused failed-transition write is NAMED (#7): the planted RAISE
        # on the failed-UPDATE makes _batch return None; the walk must print ARV-IMP-003
        fO = fresh_file("oscar.md", "Oscar bytes: the named-refusal case.\n")
        dO = hashlib.sha256(pathlib.Path(fO).read_bytes()).hexdigest()
        c22 = crash("--command", "import_source", "--point", "after-put",
                    "--owner", "A", "--client-id", "cli-1", "--idem-key", "imp-22",
                    "--title", "Named Refusal", "--file", fO)
        (pathlib.Path(BLOB_DIR) / dO).unlink()  # the blob absent: the walk will try to fail the row
        plant22 = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                 "CREATE OR REPLACE FUNCTION arv._refuse_fail() RETURNS trigger AS $$ "
                                 "BEGIN RAISE EXCEPTION 'ARV-IMP-TEST: the refused failed-write'; RETURN NEW; END; "
                                 "$$ LANGUAGE plpgsql; CREATE TRIGGER refuse_fail BEFORE UPDATE ON arv.import_journal "
                                 "FOR EACH ROW WHEN (NEW.state = 'failed') EXECUTE FUNCTION arv._refuse_fail();"],
                                capture_output=True, text=True, timeout=60)
        w22 = walk("A")
        st_after_w22 = jrow("imp-22", "state, fail_reason")  # captured BEFORE the drop+re-walk (the assert's moment)
        drop22 = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                 "DROP TRIGGER IF EXISTS refuse_fail ON arv.import_journal; "
                                 "DROP FUNCTION IF EXISTS arv._refuse_fail();"],
                                capture_output=True, text=True, timeout=60)
        w22b = walk("A")  # the next walk converges the still-nonterminal row honestly
        ok22 = (c22.returncode == 2 and plant22.returncode == 0 and drop22.returncode == 0
                and w22.returncode == 0 and "ARV-IMP-003" in w22.stdout
                and "to=failed reason=ARV-BLOB-002" not in w22.stdout
                and st_after_w22.split("|")[0] == "staging"
                and w22b.returncode == 0
                and jrow("imp-22", "state, fail_reason").split("|")[0] == "failed"
                and "ARV-BLOB-002" in jrow("imp-22", "state, fail_reason"))
        check("IMP-22", ok22,
              "a refused failed-transition write is NAMED (ARV-IMP-003 — the row is NOT failed on that walk), never the lying to=failed line; the row stays nonterminal, the NEXT walk converges it honestly (failed ARV-BLOB-002)",
              "the walk's report must never claim a transition that did not happen: a refused write is a named machinery refusal, the row's state is the truth, the next walk re-drives it")

    finally:
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)
    if FAILS:
        print(f"RED — {len(FAILS)} broken case(s): {', '.join(FAILS)}")
        return 1
    print("GREEN — the §3.1 import state machine + the recovery walk hold end-to-end (IMP-01..22)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
