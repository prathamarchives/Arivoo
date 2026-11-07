#!/usr/bin/env python3
"""harness/tests/test_session.py — P4-C slice two acceptance suite (CLAIM-071,
the session/dwell events surface: D-010's durable behavior data; PLAN's
elaborated P4-C slice two card; the RTM §2.10 reservation: ReadingSession
checkpoints — behavior events INSIDE the D-010 boundary; record 63 §2).
Red-first (LAW-11): at CLAIM-070's merged head fd6fb9f the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the record_session command,
the list-session-events read arm, and migration 0015 are absent.

THE CONTRACT (P4-C slice two's letter, record 63 §2): the approved
reading-session checkpoint events on the EXISTING substrate — the closed
event vocabulary (session_start | checkpoint | dwell | session_end — coarse
behavior facts, never input traces), the event rows (owner+source scoped,
keyed to the CURRENT generation — the serving-generation binding the
position surface established; ONE append-only migration 0015), the write
command through the spine's own ack contract (idempotent, the frozen
grammar, the client outbox ride), the read arm (the session/dwell listing
bounded/paginated on the P4-00b contract), and D-010's boundary as TYPED
REFUSALS at the write boundary — keystroke/mouse-shaped payloads,
search-query/agent-prompt event kinds refuse named (ARV-SES-004), never
silently stored. The coarse position composes the LANDED position surface
(never a second position path: the offsets validate against the same
derived view, the same ONE read_text home).

Cases (the SES registry; each pin's full statement lives at its check()):
  SES-01 the record->read round-trip at the real boundary: the four event
         kinds each record durably through the spine's frozen ack contract
         (status=committed result_ref=<source>@<ordinal> events=<n>
         durability_rung=local_durable api_version=1); a FRESH read
         invocation lists them (one JSON row per event, the version header,
         the '# more=' truth marker); the row's column set carries NO
         free-text column (the structural D-010 no-trace law: no content/
         query/prompt/trace column exists — the behavior row is coordinates
         + the coarse dwell, never captured input)
  SES-02 the typed record refusals + the substrate guards: an absent source
         and ANOTHER OWNER's source are the SAME ARV-SES-001 refusal (the
         no-oracle at the write boundary); a source with no serving
         generation refuses ARV-SES-002 (a session event positions into the
         derived view — never extracted means nothing to checkpoint into);
         invalid offsets refuse ARV-SES-003 (never clamped — the coarse
         span validated against the derived view's extent); THE D-010
         BOUNDARY REFUSALS: an event kind outside the closed vocabulary
         (the named adversarial kinds: keystroke / search_query /
         agent_prompt) refuses ARV-SES-004 with D-010 named in the refusal;
         the shape law: a dwell event without --dwell-ms and a non-dwell
         event with one refuse ARV-SES-005; every refusal leaves ZERO rows;
         the substrate guards: direct UPDATE/DELETE refuse ARV-SES-006
         (append-only), a hostile INSERT with a SKIPPED ordinal refuses
         ARV-SES-007 (the ordinal law), a hostile INSERT binding ANOTHER
         SOURCE's generation refuses ARV-SES-008 (the generation-bind law),
         a hostile INSERT with an out-of-vocabulary event kind refuses at
         the SUBSTRATE CHECK (the D-010 boundary below the command too)
  SES-03 the idempotency + the outbox ride + the lost-ack arm: same
         key+body -> status=replayed (one row, the same result_ref); same
         key+different body -> ARV-CMD-409 (zero effect); the command rides
         the CLIENT outbox (the _SYNC_COMMANDS membership — the sync
         intent); the crash matrix's lost-ack arm: post-commit-pre-ack
         exits 2 with the effect committed and the replay converges the ack
  SES-04 the coarse-position composition + the generation binding: the
         events record the serving generation at write time; after a
         re-extraction the RECORDED rows are unchanged (append-only: the
         recorded generation_id stays the ORIGINAL — the behavior history
         never retargets, never rewrites); a NEW event after the
         re-extraction binds the CURRENT generation (new events ride the
         serving generation); the position composition: a checkpoint at the
         same offsets as a saved position coexists (the event stream and
         the position rows are SEPARATE surfaces over the SAME coordinates
         — never a second position path: get-position still answers the
         position row, unchanged by the events)
  SES-05 the read arm's bounded/paginated contract + the owner isolation:
         the P4-00b bounds (--limit default 100 bounds 1..1000 + --after
         the keyset cursor; the typed ARV-QRY-004 on 0/1001/non-integer/
         non-uuid, exit 1, zero effect); the paged walk's union equals the
         full walk, monotone, no dups; the empty owner answers header +
         more=false ALONE (never silence); owner B's listing carries ONLY
         B's events (RLS the boundary — never A's rows)
  SES-06 the reserved surface made real + the schema conventions (0015):
         capability.py's surfaces registry names the LANDED verbs
         (record_session + list-session-events) with owner_phase P4-C, the
         D-010 boundary named, and the reader-client exclusion; the schema
         audited — NO DEFAULTs (LAW-24), RLS enabled AND FORCED + the
         owner policy, the grants (INSERT+SELECT to arv_app, SELECT to
         arv_read, NO UPDATE/DELETE), the two composite FKs (source +
         generation), the (owner, source, ordinal) UNIQUE, the closed
         event vocabulary CHECK at the substrate, the dwell shape + bounds
         CHECKs; the frozen ack grammar on every ack and replay line
         (api_version)

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no journal/blocks surface
(the following P4-C slice); no reader-client work (P4-B's separate repo); no
fine-grained tracing beyond the approved vocabulary (D-010 — the boundary is
the REFUSAL, not a clamp).

Run: python3 harness/tests/test_session.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import uuid as _uuid

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pg  # noqa: E402

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the command, the read arm, and
# the migration are each absent at the RED tree — the cheapest honest probe
# per surface (the POS precedent's --help form).
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                          "record_session", "--help"], capture_output=True, text=True)
_absent_cmd = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "list-session-events", "--owner", "A"],
                         capture_output=True, text=True, timeout=60)
_absent_arm = "invalid choice" in _probe2.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0015_*.sql"))
if _absent_cmd or _absent_arm or not _mig:
    print(f"FAIL ARV-TEST-000: the P4-C slice two session/dwell machinery is absent "
          f"(machinery-absent class; record_session command absent: {_absent_cmd}; "
          f"list-session-events arm absent: {_absent_arm}; migration 0015 present: {bool(_mig)}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None
# the corpus: a reading text with several paragraphs — the derived view the
# session events position into (decoded-text coordinates, the coarse spans)
TEXT = ("The opening paragraph establishes the ground.\n"
        "The second paragraph carries the first resting point.\n"
        "The third paragraph carries the moved resting point.\n"
        "The fourth paragraph closes the reading.\n")


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


def cmd(op: str, *args, owner="A", key=None, client="cli-1") -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args)


def extract(key: str, source_id: str, owner: str = "A") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor", "owner",
               "--client-id", "cli-1", "--idem-key", key, "--source-id", source_id)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


def rec(source_id: str, event: str, start: int, end: int, key: str, owner="A",
        dwell=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), "record_session", "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
         "--source-id", source_id, "--event", event,
         "--start", str(start), "--end", str(end)]
    if dwell is not None:
        a += ["--dwell-ms", str(dwell)]
    return cli(*a)


def crash_rec(source_id: str, event: str, start: int, end: int, key: str,
              point: str, dwell=None) -> subprocess.CompletedProcess:
    # THE HOUSE CRASH VOCABULARY (the NTE-06 pattern): the injection rides
    # harness/crash.py --point — commands.py itself carries no --crash-at flag
    # (exit 2 is crash.py's vocabulary, never argparse's).  The dwell rides
    # the same invocation (the shape law: a dwell event without --dwell-ms
    # refuses BEFORE the crash vocabulary could ever fire — the RED draft's
    # omission, amended)
    a = [str(REPO / "harness" / "crash.py"), "--command", "record_session",
         "--point", point, "--owner", "A", "--actor", "owner",
         "--client-id", "cli-1", "--idem-key", key,
         "--source-id", source_id, "--event", event,
         "--start", str(start), "--end", str(end)]
    if dwell is not None:
        a += ["--dwell-ms", str(dwell)]
    return cli(*a)


def save_pos(source_id: str, start: int, end: int, key: str) -> subprocess.CompletedProcess:
    return cmd("save_position", "--source-id", source_id,
               "--start", str(start), "--end", str(end), key=key)


def get_pos(owner: str, source_id: str) -> subprocess.CompletedProcess:
    return query("get-position", "--owner", owner, "--source", source_id)


def ref_of(r: subprocess.CompletedProcess) -> str:
    for ln in r.stdout.splitlines():
        if ln.startswith("ACK") and "result_ref=" in ln:
            return ln.split("result_ref=")[1].split()[0]
    return ""


def jline(r: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(next(ln for ln in r.stdout.splitlines() if ln.strip()))
    except Exception:
        return {}


def jlines(r: subprocess.CompletedProcess) -> list:
    return [json.loads(ln) for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    """A hostile/direct write attempt AS the app role (the substrate's own guard)."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_app", "-d", DB,
                           "-c", f"SET app.current_owner='{owner}'; {sql}"],
                          capture_output=True, text=True, timeout=60,
                          env=ENV)


def super_sql(sql: str) -> subprocess.CompletedProcess:
    """The append-only trigger's own audience: a role WITH update/delete
    permission (the rig superuser) — the trigger fires where the least-privilege
    app role is stopped earlier at the permission boundary."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "postgres", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4c2")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4c2-"))

        # the fixtures: TWO extracted sources for owner A (the second for the
        # cross-source event stream) + one never-extracted + B's own extracted
        f1 = tmp / "reading.txt"
        f1.write_text(TEXT, encoding="utf-8")
        r_i1 = cmd("import_source", "--title", "The Reading Text",
                   "--file", str(f1), key="imp-1")
        src1 = ref_of(r_i1)
        extract("ext-1", src1)
        f2 = tmp / "other.txt"
        f2.write_text("A second document for the stream.\nIts paragraphs are its own.\n",
                      encoding="utf-8")
        r_i2 = cmd("import_source", "--title", "The Second Text",
                   "--file", str(f2), key="imp-2")
        src2 = ref_of(r_i2)
        extract("ext-2", src2)
        f3 = tmp / "never.txt"
        f3.write_text("Imported but never extracted.\n", encoding="utf-8")
        r_i3 = cmd("import_source", "--title", "The Unextracted Text",
                   "--file", str(f3), key="imp-3")
        src3 = ref_of(r_i3)
        fb = tmp / "btext.txt"
        fb.write_text("B's own document.\n", encoding="utf-8")
        r_ib = cmd("import_source", "--title", "The B Text",
                   "--file", str(fb), key="imp-b", owner="B")
        srcB = ref_of(r_ib)
        extract("ext-b", srcB, owner="B")
        gen1 = jline(cap("measure", "--owner", "A", "--source", src1)).get("generation_id", "")
        gen2 = jline(cap("measure", "--owner", "A", "--source", src2)).get("generation_id", "")
        genB = jline(cap("measure", "--owner", "B", "--source", srcB)).get("generation_id", "")

        # ---- SES-01 — the record->read round-trip at the real boundary
        p1s, p1e = len(TEXT) // 3, len(TEXT) // 2
        r_s1 = rec(src1, "session_start", 0, 10, key="ses-1")
        ack1 = next((ln for ln in r_s1.stdout.splitlines() if ln.startswith("ACK")), "")
        r_s2 = rec(src1, "checkpoint", p1s, p1e, key="ses-2")
        ack2 = next((ln for ln in r_s2.stdout.splitlines() if ln.startswith("ACK")), "")
        r_s3 = rec(src1, "dwell", p1s, p1e, key="ses-3", dwell=4500)
        ack3 = next((ln for ln in r_s3.stdout.splitlines() if ln.startswith("ACK")), "")
        r_s4 = rec(src1, "session_end", p1s, p1e, key="ses-4")
        ack4 = next((ln for ln in r_s4.stdout.splitlines() if ln.startswith("ACK")), "")
        # a second source's event (the cross-source stream)
        r_s5 = rec(src2, "session_start", 0, 5, key="ses-5")
        # the read: a FRESH invocation lists the owner's event stream
        r_l1 = query("list-session-events", "--owner", "A")
        l1_rows = jlines(r_l1)
        by_key = {(row.get("source_id"), row.get("event_ordinal")): row for row in l1_rows}
        cols = [ln for ln in subprocess.run(
            ["psql", "-X", "-A", "-t", "-U", "arv_read", "-d", DB, "-c",
             "SELECT column_name FROM information_schema.columns "
             "WHERE table_schema='arv' AND table_name='reading_session';"],
            capture_output=True, text=True, timeout=60, env=ENV).stdout.split() if ln.strip()]
        no_freetext = cols and not any(
            c in ("content", "text", "query", "prompt", "trace", "keystroke",
                  "mouse", "payload", "body", "selected_text") for c in cols)
        need_cols = {"id", "owner_scope", "source_id", "event", "event_ordinal",
                     "generation_id", "start_off", "end_off", "dwell_ms", "actor",
                     "run_id", "input_hash", "idempotency_key", "created_at"}
        row1 = by_key.get((src1, 1), {})
        row2 = by_key.get((src1, 2), {})
        row3 = by_key.get((src1, 3), {})
        row4 = by_key.get((src1, 4), {})
        ok1 = (r_s1.returncode == 0
               and "status=committed" in ack1
               and f"result_ref={src1}@1" in ack1
               and "events=1" in ack1
               and "durability_rung=local_durable" in ack1
               and "api_version=1" in ack1
               and r_s4.returncode == 0 and f"result_ref={src1}@4" in ack4
               and "events=4" in ack4
               and r_l1.returncode == 0
               and r_l1.stdout.splitlines()[0] == "# api_version=1"
               and r_l1.stdout.splitlines()[-1] == "# more=false"
               and len(l1_rows) == 5
               and all(row.get("api_version") == 1 for row in l1_rows)
               and row1.get("event") == "session_start"
               and row1.get("start_off") == 0 and row1.get("end_off") == 10
               and row1.get("dwell_ms") is None
               and row1.get("generation_id") == gen1
               and row2.get("event") == "checkpoint"
               and row2.get("start_off") == p1s and row2.get("end_off") == p1e
               and row3.get("event") == "dwell" and row3.get("dwell_ms") == 4500
               and row4.get("event") == "session_end"
               and by_key.get((src2, 1), {}).get("event") == "session_start"
               and by_key[(src2, 1)].get("generation_id") == gen2
               and no_freetext and need_cols <= set(cols))
        check("SES-01", ok1,
              "the record->read round-trip at the real boundary: the four event kinds "
              "(session_start/checkpoint/dwell/session_end) each record durably through the "
              "spine's frozen ack contract (status=committed + result_ref=<source>@<ordinal> + "
              "events=<n> + durability_rung=local_durable + api_version=1); a FRESH read "
              "invocation lists the owner's whole event stream (one JSON row per event, the "
              "version header, the '# more=' truth marker, api_version on every row); the "
              "generation binding recorded at write time (the serving generation); the dwell "
              "carried only on the dwell event; the row's column set carries NO free-text "
              "column (the structural D-010 no-trace law)",
              "harness/commands.py record_session through the spine's own ack contract + "
              "harness/query.py list-session-events over migration 0015's reading_session "
              "rows — never a second durability path, never a content/query/prompt column")

        # ---- SES-02 — the typed refusals + the substrate guards
        absent = str(_uuid.uuid4())
        r_abs = rec(absent, "session_start", 0, 5, key="sesx-1")
        r_xo = rec(src1, "session_start", 0, 5, key="sesx-2", owner="B")
        r_ng = rec(src3, "session_start", 0, 5, key="sesx-3")
        r_o1 = rec(src1, "checkpoint", -1, 5, key="sesx-4")
        r_o2 = rec(src1, "checkpoint", 10, 10, key="sesx-5")
        r_o3 = rec(src1, "checkpoint", 10, len(TEXT) + 999, key="sesx-6")
        # THE D-010 BOUNDARY REFUSALS: the named adversarial kinds
        r_d1 = rec(src1, "keystroke", 0, 5, key="sesx-7")
        r_d2 = rec(src1, "search_query", 0, 5, key="sesx-8")
        r_d3 = rec(src1, "agent_prompt", 0, 5, key="sesx-9")
        # the shape law: dwell without --dwell-ms; non-dwell with one
        r_sh1 = rec(src1, "dwell", 0, 5, key="sesx-10")
        r_sh2 = rec(src1, "checkpoint", 0, 5, key="sesx-11", dwell=100)
        rows_before = audit("SELECT count(*) FROM arv.reading_session;")
        # the substrate guards (the hostile-write backstops)
        g_upd = super_sql("UPDATE arv.reading_session SET start_off = 0;")
        g_del = super_sql("DELETE FROM arv.reading_session;")
        g_ord = app_sql(f"INSERT INTO arv.reading_session (id, owner_scope, source_id, event, "
                        f"event_ordinal, generation_id, start_off, end_off, dwell_ms, actor, "
                        f"run_id, input_hash, idempotency_key, created_at) VALUES ("
                        f"'{_uuid.uuid4()}', 'A', '{src1}', 'checkpoint', 9, '{gen1}', 0, 5, "
                        f"NULL, 'owner', 'run-hostile', 'deadbeef', 'hostile-1', now());")
        g_bind = app_sql(f"INSERT INTO arv.reading_session (id, owner_scope, source_id, event, "
                         f"event_ordinal, generation_id, start_off, end_off, dwell_ms, actor, "
                         f"run_id, input_hash, idempotency_key, created_at) VALUES ("
                         f"'{_uuid.uuid4()}', 'A', '{src1}', 'checkpoint', 5, '{gen2}', 0, 5, "
                         f"NULL, 'owner', 'run-hostile', 'deadbeef', 'hostile-2', now());")
        # the D-010 boundary at the SUBSTRATE: the closed vocabulary CHECK
        g_d010 = app_sql(f"INSERT INTO arv.reading_session (id, owner_scope, source_id, event, "
                         f"event_ordinal, generation_id, start_off, end_off, dwell_ms, actor, "
                         f"run_id, input_hash, idempotency_key, created_at) VALUES ("
                         f"'{_uuid.uuid4()}', 'A', '{src1}', 'keystroke', 5, '{gen1}', 0, 5, "
                         f"NULL, 'owner', 'run-hostile', 'deadbeef', 'hostile-3', now());")
        rows_after = audit("SELECT count(*) FROM arv.reading_session;")
        ok2 = (r_abs.returncode == 1 and "FAIL ARV-SES-001:" in r_abs.stdout
               and r_xo.returncode == 1 and "FAIL ARV-SES-001:" in r_xo.stdout
               and r_abs.stdout.replace(absent, "<id>") == r_xo.stdout.replace(src1, "<id>")
               and r_ng.returncode == 1 and "FAIL ARV-SES-002:" in r_ng.stdout
               and "generation" in r_ng.stdout
               and r_o1.returncode == 1 and "FAIL ARV-SES-003:" in r_o1.stdout
               and r_o2.returncode == 1 and "FAIL ARV-SES-003:" in r_o2.stdout
               and r_o3.returncode == 1 and "FAIL ARV-SES-003:" in r_o3.stdout
               and r_d1.returncode == 1 and "FAIL ARV-SES-004:" in r_d1.stdout
               and "D-010" in r_d1.stdout
               and r_d2.returncode == 1 and "FAIL ARV-SES-004:" in r_d2.stdout
               and r_d3.returncode == 1 and "FAIL ARV-SES-004:" in r_d3.stdout
               and r_sh1.returncode == 1 and "FAIL ARV-SES-005:" in r_sh1.stdout
               and r_sh2.returncode == 1 and "FAIL ARV-SES-005:" in r_sh2.stdout
               and rows_before == "5" and rows_after == "5"
               and "ARV-SES-006" in g_upd.stderr
               and "ARV-SES-006" in g_del.stderr
               and "ARV-SES-007" in g_ord.stderr
               and "ARV-SES-008" in g_bind.stderr
               and "reading_session_event_check" in g_d010.stderr)
        check("SES-02", ok2,
              "the typed record refusals + the substrate guards: absent source and ANOTHER "
              "OWNER's source are the SAME ARV-SES-001 refusal (the no-oracle at the write "
              "boundary); a source with no serving generation refuses ARV-SES-002; invalid "
              "offsets refuse ARV-SES-003 (never clamped — the coarse span against the derived "
              "view's extent); THE D-010 BOUNDARY REFUSALS: the event kinds outside the closed "
              "vocabulary (keystroke / search_query / agent_prompt) refuse ARV-SES-004 with "
              "D-010 named; the shape law (dwell without --dwell-ms, non-dwell with one) "
              "refuses ARV-SES-005; every refusal leaves ZERO rows; the substrate guards: "
              "UPDATE/DELETE refuse ARV-SES-006 (append-only), the skipped ordinal refuses "
              "ARV-SES-007 (the ordinal law), the cross-source generation refuses ARV-SES-008 "
              "(the generation-bind law), and the out-of-vocabulary kind refuses at the "
              "SUBSTRATE CHECK (the D-010 boundary below the command too)",
              "the typed refusals in commands.py record_session + migration 0015's guard "
              "triggers + the closed vocabulary CHECK (the serialized advisory lock, the "
              "ordinal law, the generation-bind law, the append-only law)")

        # ---- SES-03 — the idempotency + the outbox ride + the lost-ack arm
        r_rep = rec(src1, "checkpoint", p1s, p1e, key="ses-2")
        ack_rep = next((ln for ln in r_rep.stdout.splitlines() if ln.startswith("ACK")), "")
        r_409 = rec(src1, "checkpoint", 0, 5, key="ses-2")
        # the outbox ride: the CLIENT outbox row per recorded event
        obx = audit("SELECT count(*) FROM arv.outbox WHERE command_name = 'record_session';")
        # the crash matrix's lost-ack arm: post-commit-pre-ack exits 2, the
        # effect IS committed, the same-key replay converges the ack
        r_cr = crash_rec(src1, "dwell", 20, 30, key="ses-cr", point="post-commit-pre-ack",
                         dwell=1500)
        rows_after_crash = audit("SELECT count(*) FROM arv.reading_session;")
        r_conv = rec(src1, "dwell", 20, 30, key="ses-cr", dwell=1500)
        ack_conv = next((ln for ln in r_conv.stdout.splitlines() if ln.startswith("ACK")), "")
        ok3 = (r_rep.returncode == 0 and "status=replayed" in ack_rep
               and f"result_ref={src1}@2" in ack_rep
               and "api_version=1" in ack_rep
               and r_409.returncode == 1 and "FAIL ARV-CMD-409:" in r_409.stdout
               and obx.isdigit() and int(obx) >= 5
               and r_cr.returncode == 2
               and rows_after_crash == "6"
               and r_conv.returncode == 0 and "status=replayed" in ack_conv
               and f"result_ref={src1}@5" in ack_conv)
        check("SES-03", ok3,
              "the idempotency + the outbox ride + the lost-ack arm: same key+body -> "
              "status=replayed (one row, the same result_ref); same key+different body -> "
              "ARV-CMD-409 (zero effect); the command rides the CLIENT outbox (the sync "
              "intent — every committed event enqueued); the lost-ack arm: post-commit-pre-ack "
              "exits 2 with the effect committed (the behavior event IS durable) and the "
              "same-key replay converges the ack",
              "the spine's own idempotency + the _SYNC_COMMANDS membership + the crash "
              "injection — the session command inherits the command path's whole contract")

        # ---- SES-04 — the coarse-position composition + the generation binding
        # a position save at the same coordinates (the two surfaces coexist)
        r_pos = save_pos(src1, p1s, p1e, key="pos-comp")
        gp = jline(get_pos("A", src1))
        # the re-extraction: a NEW generation supersedes gen1
        r_re = extract("ext-1b", src1)
        gen_new = jline(cap("measure", "--owner", "A", "--source", src1)).get("generation_id", "")
        # the RECORDED rows are unchanged (append-only; the recorded binding stays)
        rec_gens = audit("SELECT DISTINCT generation_id FROM arv.reading_session "
                         "WHERE source_id = '" + src1 + "' AND event_ordinal <= 4;")
        # the read arm still reports the RECORDED generation (never retargeted)
        r_l2 = query("list-session-events", "--owner", "A", "--limit", "100")
        l2_rows = jlines(r_l2)
        l2_old = next((row for row in l2_rows
                       if row.get("source_id") == src1 and row.get("event_ordinal") == 1), {})
        # a NEW event after the re-extraction binds the CURRENT generation
        r_new = rec(src1, "checkpoint", 0, 10, key="ses-new")
        l2b_rows = jlines(query("list-session-events", "--owner", "A", "--limit", "100"))
        l2_new = next((row for row in l2b_rows
                       if row.get("source_id") == src1 and row.get("event") == "checkpoint"
                       and row.get("event_ordinal") == 6), {})
        gp2 = jline(get_pos("A", src1))
        ok4 = (r_pos.returncode == 0
               and gp.get("state") == "saved" and gp.get("save_ordinal") == 1
               and gp.get("generation_matches") is True
               and r_re.returncode == 0
               and gen_new and gen_new != gen1
               and rec_gens == gen1
               and l2_old.get("generation_id") == gen1
               and r_new.returncode == 0 and "events=6" in r_new.stdout
               and l2_new.get("generation_id") == gen_new
               and gp2.get("saved_generation_id") == gen1
               and gp2.get("current_generation_id") == gen_new
               and gp2.get("generation_matches") is False)
        check("SES-04", ok4,
              "the coarse-position composition + the generation binding: the events record "
              "the serving generation at write time; after a re-extraction the RECORDED rows "
              "are unchanged (append-only: the recorded generation_id stays the ORIGINAL — "
              "the behavior history never retargets, never rewrites; the read arm reports "
              "the recorded binding); a NEW event after the re-extraction binds the CURRENT "
              "generation (events=6, the new generation); the position composition: a "
              "checkpoint at the same coordinates as a saved position coexists (the event "
              "stream and the position rows are SEPARATE surfaces over the SAME coordinates "
              "— never a second position path: get-position still answers the position row "
              "with its own honest binding, matches=false across the re-extraction)",
              "the serving-generation field on every event row + the append-only substrate "
              "— the behavior history is provenance, never a live retarget")

        # ---- SES-05 — the read arm's bounds + the owner isolation
        r_l3 = query("list-session-events", "--owner", "A", "--limit", "3")
        l3_rows = jlines(r_l3)
        walk, cursor, more = [], None, True
        while more:
            args = ["list-session-events", "--owner", "A", "--limit", "3"]
            if cursor:
                args += ["--after", cursor]
            r_w = query(*args)
            w_rows = jlines(r_w)
            walk += w_rows
            more = r_w.stdout.splitlines()[-1] == "# more=true"
            cursor = w_rows[-1]["event_id"] if w_rows else None
        walk_ids = [row["event_id"] for row in walk]
        monotone = all(walk_ids[i] < walk_ids[i + 1] for i in range(len(walk_ids) - 1))
        refusals = []
        for bad in (["--limit", "0"], ["--limit", "1001"], ["--limit", "abc"],
                    ["--after", "not-a-uuid"]):
            r_bad = query("list-session-events", "--owner", "A", *bad)
            refusals.append(r_bad.returncode == 1
                            and r_bad.stdout.startswith("FAIL ARV-QRY-004:")
                            and "# api_version" not in r_bad.stdout)
        # the empty owner: header + more=false ALONE (never silence)
        r_lc = query("list-session-events", "--owner", "C")
        lc_lines = r_lc.stdout.splitlines()
        # B's isolation: B's own event, never A's
        r_lb = rec(srcB, "session_start", 0, 4, key="ses-b", owner="B")
        r_lB = query("list-session-events", "--owner", "B")
        lB_rows = jlines(r_lB)
        ok5 = (r_l3.returncode == 0
               and len(l3_rows) == 3
               and r_l3.stdout.splitlines()[-1] == "# more=true"
               and len(walk) == 7
               and monotone
               and len(set(walk_ids)) == len(walk_ids)
               and all(refusals)
               and r_lc.returncode == 0
               and lc_lines == ["# api_version=1", "# more=false"]
               and r_lb.returncode == 0
               and r_lB.returncode == 0
               and len(lB_rows) == 1
               and lB_rows[0].get("source_id") == srcB
               and lB_rows[0].get("generation_id") == genB
               and not any(row.get("source_id") in (src1, src2, src3) for row in lB_rows))
        check("SES-05", ok5,
              "the read arm's bounded/paginated contract + the owner isolation: the P4-00b "
              "bounds (--limit default 100 bounds 1..1000 + --after the keyset cursor; the "
              "typed ARV-QRY-004 on 0/1001/non-integer/non-uuid — exit 1, zero effect, never "
              "a header, never rows); the paged walk's union equals the full walk (all seven "
              "of A's events), monotone, no dups; the empty owner answers header + "
              "more=false ALONE (never silence); owner B's listing carries ONLY B's own "
              "event (RLS the boundary — never A's rows, never A's sources)",
              "the shared bounds machinery at the read boundary + the owner-scoped read "
              "(SET app.current_owner + the RLS policy) — the same machinery every arm rides")

        # ---- SES-06 — the reserved surface + the schema conventions (0015)
        r_sur = cap("surfaces")
        srows = jlines(r_sur)
        ses_row = next((row for row in srows
                        if row.get("surface") == "session/dwell-events"), {})
        defaults = audit("SELECT count(*) FROM information_schema.columns "
                         "WHERE table_schema='arv' AND table_name='reading_session' "
                         "AND column_default IS NOT NULL;")
        rls = audit("SELECT relrowsecurity AND relforcerowsecurity FROM pg_class "
                    "WHERE oid = 'arv.reading_session'::regclass;")
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' "
                    "AND tablename='reading_session' AND policyname='owner_isolation' "
                    "AND roles::text = '{arv_app}';")
        grants = audit("SELECT has_table_privilege('arv_app','arv.reading_session','INSERT') "
                       "|| '|' || has_table_privilege('arv_app','arv.reading_session','UPDATE') "
                       "|| '|' || has_table_privilege('arv_app','arv.reading_session','DELETE') "
                       "|| '|' || has_table_privilege('arv_read','arv.reading_session','SELECT');")
        fks = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                    "'arv.reading_session'::regclass AND contype = 'f' "
                    "AND array_length(conkey, 1) = 2;")
        uniq = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                     "'arv.reading_session'::regclass AND contype = 'u' "
                     "AND pg_get_constraintdef(oid) = "
                     "'UNIQUE (owner_scope, source_id, event_ordinal)';")
        vocab = audit("SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                      "WHERE conrelid = 'arv.reading_session'::regclass AND contype = 'c' "
                      "AND pg_get_constraintdef(oid) LIKE '%session_start%';")
        ok6 = (r_sur.returncode == 0
               and all(row.get("api_version") == 1 for row in srows)
               and ses_row.get("owner_phase") == "P4-C"
               and "record_session" in str(ses_row.get("reservation", ""))
               and "list-session-events" in str(ses_row.get("reservation", ""))
               and "D-010" in str(ses_row.get("reservation", ""))
               and "separate repo" in str(ses_row.get("reservation", ""))
               and defaults == "0"
               and rls == "t" and pol == "1"
               and grants == "true|false|false|true"
               and fks == "2" and uniq == "1"
               and vocab.strip() != ""
               and "api_version=1" in ack1 and "api_version=1" in ack_rep)
        check("SES-06", ok6,
              "the reserved surface made real + the schema conventions (0015): capability.py's "
              "surfaces registry names the LANDED verbs (record_session + "
              "list-session-events) with owner_phase P4-C, the D-010 boundary named, and the "
              "reader-client exclusion (the separate repo); the schema audited — NO DEFAULTs "
              "(LAW-24), RLS enabled AND FORCED + the owner_isolation policy on arv_app, the "
              "grants (INSERT+SELECT to arv_app, SELECT to arv_read, NO UPDATE/DELETE), the "
              "two composite FKs (source + generation), the (owner, source, ordinal) UNIQUE, "
              "the closed event vocabulary CHECK at the substrate; the frozen ack grammar on "
              "every ack and replay line (api_version)",
              "harness/capability.py's RESERVED_SURFACES registry updated to the landed "
              "contract + migration 0015's conventions (the 0004/0008/0009/0014 substrate "
              "pattern)")

        if FAILS:
            print(f"\nSESSION SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the session/dwell contract is broken or unimplemented)")
            return 1
        print("\nSESSION SUITE GREEN — SES-01..06 (the session/dwell events surface: the "
              "closed vocabulary durable through the spine, the D-010 boundary as typed "
              "refusals at both the command and the substrate, the bounded read arm)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
