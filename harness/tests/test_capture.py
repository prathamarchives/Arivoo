#!/usr/bin/env python3
"""harness/tests/test_capture.py — P3-01 acceptance suite (the §1.6 capture checkpoint).

Red-first (LAW-11): committed BEFORE the implementation; the red run fails with
ARV-TEST-000 (machinery-absent: import_source/create_highlight/query do not
exist — the S1/record-18 §4.1 precedent, the same waiting-for-harness class as
the P3-K0 kernel suite).

THE §1.6 CAPTURE CHECKPOINT (D-041 element 4; RTM SYS-09's pre-registered
path; PLAN's P3-01 acceptance) — the checkpoint the slice must walk END-TO-END
through the REAL boundary (subprocess CLIs, the real psql kernel, the real
content-addressed blob store, the real owner-scoped RLS reads):

  import -> persist identity -> highlight with version-tied anchor ->
  lost-ack -> restart/retry -> exactly-one-effect -> authenticated
  retrieval -> independent read

Every state claim is made by an INDEPENDENT reader (the arv_read role, direct
psql — LAW-13), never by the path under test. The product commands are the
PLAN card's kernel-contract carriers: atomic, idempotent, attributed, stable
named failures (CAP-00x), the §6 failure matrix honored.

Cases (the CAP registry — this file is the contract's declaration):
  CAP-01 import through the real boundary (commit + the §2 shape observed)
  CAP-02 persist identity — the authenticated get_source read
  CAP-03 highlight with version-tied anchor (selected text DERIVED from bytes)
  CAP-04 the dangling-source refusal (§6's wrong-version/dangling class)
  CAP-05 invalid offsets refused, zero effect
  CAP-06 lost-ack: crash post-commit-pre-ack — committed, NO ack (§4.1)
  CAP-07 restart/retry: the same key replays the RECORDED ack
  CAP-08 exactly-one-effect: the retry added NOTHING (the independent count)
  CAP-09 authenticated retrieval + cross-owner isolation (never reveals existence)
  CAP-10 the independent read reconciles the whole checkpoint (arv_read)
  CAP-11 direct DB access fails closed (RLS without the owner GUC)
  CAP-12 same key + different body -> ARV-CMD-409, state unchanged
  CAP-13 crash before commit -> zero effect; retry commits exactly one
  CAP-14 the Q11 baseline: same bytes re-imported = a NEW Source row, ONE blob
  CAP-15 blob corrupt at verify -> ARV-CAP-004, zero rows (never promoted)
  CAP-16 import file missing -> ARV-CAP-001, zero effect
  CAP-17 the §2 substrate conventions on all four tables (LAW-24 no-defaults,
        RLS forced, arv_read grants, the append-only triggers)

Run: python3 harness/tests/test_capture.py   (exit 0 = green)
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
    from harness.commands import REGISTRY  # noqa: E402
except ImportError as e:  # the substrate itself absent
    print(f"FAIL ARV-TEST-000: the kernel does not exist (waiting-for-harness) — {e}")
    sys.exit(1)

_missing = [n for n in ("import_source", "create_highlight") if n not in REGISTRY]
_absent_files = [str(p) for p in (REPO / "harness" / "query.py", REPO / "harness" / "adapters" / "blob.py",
                                  REPO / "harness" / "migrations" / "0004_p3_01_capture_skeleton.sql")
                 if not p.is_file()]
if _missing or _absent_files:
    print(f"FAIL ARV-TEST-000: the capture machinery is absent (machinery-absent class; "
          f"missing commands: {_missing}; missing files: {[p.split('/')[-1] for p in _absent_files]}) — "
          "P3-01's implementation lands after this RED, never before it")
    sys.exit(1)

DB = None
ENV = None
BLOB_DIR = None


def cli(*args) -> subprocess.CompletedProcess:
    """The product path AS THE CALLER SEES IT (a subprocess CLI — acks on stdout)."""
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=180, env=ENV)


def cmd(mod: str, *args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / mod), *args)


def import_src(key: str, title: str, file: str, owner: str = "A",
               media: str = "text/plain", work_id: str = None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), "import_source", "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
         "--title", title, "--file", file, "--media-type", media]
    if work_id:
        a += ["--work-id", work_id]
    return cli(*a)


def highlight(key: str, source_id: str, start: int, end: int,
              owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "create_highlight",
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--source-id", source_id,
               "--start", str(start), "--end", str(end))


def crash(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "crash.py"), *args)


def audit(query: str) -> str:
    """Independent state read (LAW-13): the arv_read role, direct psql."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", query],
                          capture_output=True, text=True, timeout=60).stdout.strip()


def audit_rows(query: str) -> list:
    return [ln for ln in audit(query).splitlines() if ln.strip()]


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def main() -> int:
    global DB, ENV, BLOB_DIR
    DB = pg.create_scratch_db("p301")
    BLOB_DIR = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=BLOB_DIR)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ---- the checkpoint's fixture: real bytes on disk (a readable-text source)
        TEXT = ("Reading is the compound act.\n"
                "The second paragraph carries the selected words: marginalia lives here.\n"
                "The third paragraph closes the page.\n")
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "day-one.md"
        src_file.write_text(TEXT, encoding="utf-8")
        digest = hashlib.sha256(src_file.read_bytes()).hexdigest()
        # the known selection: the phrase inside paragraph two
        sel = TEXT.index("marginalia")
        start, end = sel, sel + len("marginalia")

        # CAP-01 — import through the real boundary (checkpoint step 1: import)
        p = import_src("imp-1", "Day One", str(src_file))
        sid = ack_field(p, "result_ref")
        wid = ack_field(p, "work_id")
        n_work = audit("SELECT count(*) FROM arv.work;")
        src_row = audit_rows(f"SELECT digest, media_type, byte_size, import_state, source_version, work_id "
                             f"FROM arv.source WHERE id='{sid}';")
        ok1 = (p.returncode == 0 and "status=committed" in p.stdout
               and n_work == "1" and len(src_row) == 1
               and src_row[0].split("|") == [digest, "text/plain", str(len(src_file.read_bytes())),
                                             "complete", "1", wid]
               and audit(f"SELECT title FROM arv.work WHERE id='{wid}';") == "Day One")
        check("CAP-01", ok1,
              f"import_source commits ONE work + ONE source (digest-true, complete, version 1) — ack {sid[:8]}",
              "the import must verify the blob readable+digest-matched BEFORE the commit and land work+source+command_log in ONE transaction")

        # CAP-02 — persist identity: the authenticated owner-scoped read
        q = cmd("query.py", "get-source", "--owner", "A", "--id", sid)
        try:
            j = json.loads(q.stdout)
        except Exception:
            j = {}
        ok2 = (q.returncode == 0 and j.get("digest") == digest and j.get("work_id") == wid
               and j.get("title") == "Day One" and j.get("import_state") == "complete")
        check("CAP-02", ok2,
              "get_source returns the persisted identity (work title, digest, state) through the owner-scoped read",
              "the retrieval surface must read through the app role with the owner GUC — RLS is the scope, never a filter bolted on after")

        # CAP-03 — highlight with version-tied anchor (checkpoint step 3)
        h = highlight("hl-1", sid, start, end)
        hid = ack_field(h, "result_ref")
        hl_row = audit_rows(f"SELECT revision, selected_text, source_id FROM arv.highlight WHERE id='{hid}';")
        an_row = audit_rows(f"SELECT source_id, source_digest, start_off, end_off, media_type "
                            f"FROM arv.anchor WHERE id=(SELECT anchor_id FROM arv.highlight WHERE id='{hid}');")
        ok3 = (h.returncode == 0 and "status=committed" in h.stdout and len(hl_row) == 1
               and hl_row[0].split("|") == ["1", "marginalia", sid] and len(an_row) == 1
               and an_row[0].split("|")[:2] == [sid, digest]
               and an_row[0].split("|")[3] == str(end))
        check("CAP-03", ok3,
              "create_highlight derives the selected text FROM THE BYTES and ties the anchor to the source digest (version-tied)",
              "the anchor must be minted against the source's CURRENT digest inside the command — a client-supplied anchor text is never trusted")

        # CAP-04 — the dangling-source refusal (§6's class, this rung's form)
        ghost = "00000000-0000-7000-8000-000000000000"
        g = highlight("hl-ghost", ghost, 0, 5)
        n_hl = audit("SELECT count(*) FROM arv.highlight;")
        n_an = audit("SELECT count(*) FROM arv.anchor;")
        check("CAP-04", g.returncode != 0 and "ARV-CAP-002" in g.stdout + g.stderr
              and n_hl == "1" and n_an == "1",
              "a highlight against a nonexistent source -> ARV-CAP-002, zero rows (REFUSED at the command boundary)",
              "validate the source id inside the owner's scope BEFORE the transaction opens — a dangling anchor never enters the store")

        # CAP-05 — invalid offsets refused, zero effect
        b1 = highlight("hl-bad1", sid, end, start)
        b2 = highlight("hl-bad2", sid, 0, len(TEXT) + 10)
        ok5 = (b1.returncode != 0 and "ARV-CAP-003" in b1.stdout + b1.stderr
               and b2.returncode != 0 and "ARV-CAP-003" in b2.stdout + b2.stderr
               and audit("SELECT count(*) FROM arv.highlight;") == "1")
        check("CAP-05", ok5, "start>=end and end>length each -> ARV-CAP-003, zero effect",
              "offsets are validated against the actual decoded length — never clamped, never guessed")

        # CAP-06 — lost-ack (checkpoint step 4): crash post-commit-pre-ack
        c = crash("--command", "create_highlight", "--point", "post-commit-pre-ack",
                  "--owner", "A", "--client-id", "cli-crash", "--idem-key", "hl-lost",
                  "--source-id", sid, "--start", str(start), "--end", str(end))
        lost_committed = audit("SELECT count(*) FROM arv.highlight WHERE idempotency_key='hl-lost';")
        check("CAP-06", c.returncode == 2 and "ACK" not in c.stdout and lost_committed == "1",
              "crash post-commit-pre-ack: the capture IS committed, NO ack emitted (commit-before-acknowledgment)",
              "the ack is emitted only after the COMMIT marker is observed; the row's presence with no ack is the honest uncertain state")

        # CAP-07 — restart/retry (checkpoint step 5): the replay answers the recorded result
        r = highlight("hl-lost", sid, start, end, client="cli-crash")
        lost_ref = audit("SELECT id FROM arv.highlight WHERE idempotency_key='hl-lost';")
        check("CAP-07", r.returncode == 0 and "status=replayed" in r.stdout
              and ack_field(r, "result_ref") == lost_ref,
              "the retry with the SAME key replays the RECORDED result (the lost-ack resolution)",
              "the replay check runs before any insert and answers from command_log — the client never assumes failure")

        # CAP-08 — exactly-one-effect (checkpoint step 6): the independent count
        n_hl2 = audit("SELECT count(*) FROM arv.highlight;")
        n_cl = audit("SELECT count(*) FROM arv.command_log;")
        check("CAP-08", n_hl2 == "2" and n_cl == "4",
              f"after the retry: exactly TWO highlights (CAP-03 + the lost-ack one), FOUR command_log rows — the replay added NOTHING",
              "idempotency is observed from OUTSIDE (arv_read counts), never asserted from inside the command")

        # CAP-09 — authenticated retrieval + cross-owner isolation (checkpoint step 7)
        t = cmd("query.py", "get-capture", "--owner", "A", "--id", lost_ref)
        try:
            tj = json.loads(t.stdout)
        except Exception:
            tj = {}
        cross = cmd("query.py", "get-capture", "--owner", "B", "--id", lost_ref)
        listed = cmd("query.py", "list-captures", "--owner", "B")
        ok9 = (t.returncode == 0 and tj.get("selected_text") == "marginalia"
               and tj.get("source_digest") == digest and tj.get("revision") == 1
               and cross.returncode != 0 and "ARV-QRY-001" in cross.stdout + cross.stderr
               and listed.returncode == 0 and listed.stdout.strip() in ("", "0 rows"))
        check("CAP-09", ok9,
              "the owner retrieves the capture through the scoped read; owner B gets the SAME ARV-QRY-001 for A's capture (existence never revealed) and lists nothing",
              "RLS must scope every read; the not-found refusal must be identical for 'absent' and 'another owner's' — never a side channel")

        # CAP-10 — the independent read reconciles the checkpoint (checkpoint step 8)
        rows = audit_rows("SELECT owner_scope, idempotency_key, command_name, result_ref FROM arv.command_log ORDER BY created_at;")
        ok10 = (len(rows) == 4 and all(r.split("|")[0] == "A" for r in rows)
                and all(r.split("|")[2] in ("import_source", "create_highlight") for r in rows))
        check("CAP-10", ok10,
              "arv_read independently reconciles: 4 attributed command rows, all owner A, names in the product vocabulary",
              "the checkpoint's final step is a cross-owner-capable INDEPENDENT read — the app path never grades its own homework")

        # CAP-11 — direct DB access fails closed (RLS without the owner GUC)
        leak = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                               "-U", "arv_app", "-d", DB, "-c",
                               "INSERT INTO arv.highlight (id, revision, selected_text, source_id, anchor_id, "
                               "owner_scope, actor, run_id, input_hash, idempotency_key, created_at) VALUES "
                               "('11111111-1111-7111-8111-111111111111', 1, 'x', "
                               f"'{sid}', '00000000-0000-7000-8000-000000000000', 'A', 'owner', 'r', 'h', 'k', '2026-01-01T00:00:00Z');"],
                              capture_output=True, text=True, timeout=60)
        check("CAP-11", leak.returncode != 0 and "row-level security" in (leak.stdout + leak.stderr).lower()
              and audit("SELECT count(*) FROM arv.highlight;") == "2",
              "a direct psql INSERT as arv_app without the owner GUC is REFUSED by RLS (fails closed, zero rows)",
              "current_setting(...,true) is NULL when unset and the policy must fail CLOSED — an unscoped session writes nothing")

        # CAP-12 — same key + different body -> ARV-CMD-409, state unchanged
        other_file = src_file.with_suffix(".other")
        other_file.write_text("entirely different bytes\n", encoding="utf-8")
        before = audit("SELECT count(*) FROM arv.source;")
        x = import_src("imp-1", "Day One", str(other_file))
        after = audit("SELECT count(*) FROM arv.source;")
        check("CAP-12", x.returncode != 0 and "ARV-CMD-409" in x.stdout + x.stderr and before == after,
              "same idem key + different bytes -> the named conflict, source count unchanged",
              "the canonical body includes the digest, so different bytes are a DIFFERENT body — the replay check must refuse, never overwrite")

        # CAP-13 — crash before commit -> zero effect; the retry commits exactly one
        c2 = crash("--command", "import_source", "--point", "pre-commit",
                   "--owner", "A", "--client-id", "cli-crash", "--idem-key", "imp-crash",
                   "--title", "Crash Book", "--file", str(src_file))
        n_after_crash = audit("SELECT count(*) FROM arv.source;")
        rr = import_src("imp-crash", "Crash Book", str(src_file))
        n_after_retry = audit("SELECT count(*) FROM arv.source;")
        crash_works = audit("SELECT count(*) FROM arv.work;")
        check("CAP-13", c2.returncode == 2 and "ACK" not in c2.stdout and n_after_crash == "1"
              and rr.returncode == 0 and "status=committed" in rr.stdout and n_after_retry == "2" and crash_works == "2",
              "crash pre-commit on import: zero effect (rolled back); the SAME key retries to exactly one committed source+work",
              "the transaction rolls back with the connection; the blob store is content-addressed so the re-put is a no-op — exactly-once is about the ROWS")

        # CAP-14 — the Q11 baseline: same bytes re-imported = a NEW Source row, ONE blob
        reimp = import_src("imp-2", "Day One", str(src_file), work_id=wid)
        sid2 = ack_field(reimp, "result_ref")
        srcs = audit_rows(f"SELECT source_version FROM arv.source WHERE work_id='{wid}' ORDER BY source_version;")
        blobs = [p for p in pathlib.Path(BLOB_DIR).iterdir() if p.is_file()]
        ok14 = (reimp.returncode == 0 and sid2 != sid and [r.split("|")[0] for r in srcs] == ["1", "2"]
                and len(blobs) == 1 and blobs[0].name == digest)
        check("CAP-14", ok14,
              "re-import of the SAME bytes under the same work: a NEW Source row (version 2), the blob store holds ONE copy (byte-reuse is storage-level, never identity)",
              "Q11 baseline: no auto-merge, no identity uniqueness — content addressing dedups the BYTES, the Source rows multiply honestly")

        # CAP-15 — blob corrupt at verify -> ARV-CAP-004, zero rows (never promoted)
        third_file = src_file.with_suffix(".third")
        third_file.write_bytes(b"third body of bytes\n")
        d3 = hashlib.sha256(third_file.read_bytes()).hexdigest()
        pathlib.Path(BLOB_DIR, d3).write_bytes(b"corrupt: wrong bytes under the right digest")  # the planted corruption
        cap15 = import_src("imp-3", "Third Book", str(third_file))
        n_src3 = audit("SELECT count(*) FROM arv.source WHERE digest='" + d3 + "';")
        check("CAP-15", cap15.returncode != 0 and "ARV-CAP-004" in cap15.stdout + cap15.stderr and n_src3 == "0",
              "a blob whose content does not re-hash to its digest -> ARV-CAP-004, the Source NEVER commits (fail-closed verify)",
              "verify = get + re-hash after put; a corrupt store fails the import NAMED, zero rows — never a complete Source without true bytes")

        # CAP-16 — import file missing -> ARV-CAP-001, zero effect
        miss = import_src("imp-4", "Ghost Book", "/nonexistent/day-one.md")
        check("CAP-16", miss.returncode != 0 and "ARV-CAP-001" in miss.stdout + miss.stderr
              and audit("SELECT count(*) FROM arv.work;") == "2",
              "a missing import file -> ARV-CAP-001, zero rows (named refusal, zero effect)",
              "the file is read and hashed BEFORE anything persists; absence is a named refusal, never a partial import")

        # CAP-17 — the §2 substrate conventions on the four new tables
        defs = audit("SELECT table_name, column_name FROM information_schema.columns "
                     "WHERE table_schema='arv' AND table_name IN ('work','source','anchor','highlight') "
                     "AND column_name IN ('id','created_at') AND column_default IS NOT NULL;")
        rls = audit("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                    "WHERE n.nspname='arv' AND c.relname IN ('work','source','anchor','highlight') "
                    "AND c.relrowsecurity AND c.relforcerowlevelsecurity;")
        trig = audit("SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid "
                     "JOIN pg_namespace n ON n.oid=c.relnamespace WHERE NOT t.tgisinternal "
                     "AND n.nspname='arv' AND c.relname IN ('work','source','anchor','highlight');")
        mut_app = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "arv_app", "-d", DB, "-c",
                                  f"SET app.current_owner='A'; UPDATE arv.work SET title='hacked' WHERE id='{wid}';"],
                                 capture_output=True, text=True, timeout=60)
        mut_priv = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                  f"UPDATE arv.work SET title='hacked' WHERE id='{wid}';"],
                                 capture_output=True, text=True, timeout=60)
        check("CAP-17", defs == "" and rls == "4" and trig == "4"
              and mut_app.returncode != 0 and "permission denied" in mut_app.stdout + mut_app.stderr
              and mut_priv.returncode != 0 and "ARV-CAP-005" in mut_priv.stdout + mut_priv.stderr
              and audit(f"SELECT title FROM arv.work WHERE id='{wid}';") == "Day One",
              "the four tables: NO defaults on id/created_at (LAW-24), RLS enabled+forced on all four, mutations rejected on BOTH layers (arv_app: permission denied; even the superuser: the trigger's ARV-CAP-005) — the title unchanged",
              "the §2 conventions are schema-level: no UPDATE/DELETE grants for arv_app, and the append-only trigger guards even privileged paths with the named code")

    finally:
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)
    if FAILS:
        print(f"RED — {len(FAILS)} broken case(s): {', '.join(FAILS)}")
        return 1
    print("GREEN — the §1.6 capture checkpoint holds end-to-end (CAP-01..17)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
