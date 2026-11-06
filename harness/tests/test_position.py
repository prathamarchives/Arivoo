#!/usr/bin/env python3
"""harness/tests/test_position.py — P4-A slice two acceptance suite (CLAIM-066,
the source-open/position surface: the reserved surface made real; PLAN's
elaborated P4-A slice two card; the #99 notverified's serving-generation
routing rides here; record 58 §2).
Red-first (LAW-11): at CLAIM-065's merged head 562b70f the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the save_position command, the
get-position read arm, and migration 0014 are absent.

THE CONTRACT (P4-A slice two's letter): the reading-position contract on the
EXISTING substrate — the position rows (owner+source scoped, keyed to the
CURRENT generation — the serving-generation field), the save command through
the spine's own ack contract (the P4-00b frozen grammar), the position read
arm (the last-saved position + its generation binding, the no-oracle), ONE
migration. The position is the owner's reading state — never shared, never
inferred; the READER CLIENT is P4-B's separate repo (no client work here).

Cases (the POS registry; each pin's full statement lives at its check()):
  POS-01 the save->reopen->return round-trip at the real boundary: a save
         against an extracted source acks with the full frozen contract
         (status=committed result_ref=<source>@<ordinal>
         durability_rung=local_durable api_version=1); the reopen (a FRESH
         get-position invocation) returns the saved offsets + its generation
         binding (saved_generation_id == the current generation,
         generation_matches=true); the position row's column set carries NO
         content copy (the structural no-copy law, the BMK-01 class)
  POS-02 the typed save refusals + the substrate guards: an absent source and
         ANOTHER OWNER's source are the SAME ARV-POS-001 refusal (the
         no-oracle at the write boundary); a source with no serving
         generation refuses ARV-POS-002 (the position binds to the generation
         the reader was reading — never extracted means no readable derived
         view to position into); invalid offsets refuse ARV-POS-003 (never
         clamped, never guessed); every refusal leaves ZERO position rows;
         direct-DB UPDATE/DELETE refuse at the substrate (ARV-POS-005, the
         append-only law), a hostile INSERT with a SKIPPED ordinal refuses
         ARV-POS-004 (the ordinal law), a hostile INSERT binding ANOTHER
         SOURCE's generation refuses ARV-POS-006 (the generation-bind law)
  POS-03 the idempotency + the position advance: same key+body ->
         status=replayed (one row, the same result_ref); same key+different
         body -> ARV-CMD-409 (zero effect); a second save with a NEW key
         appends ordinal 2 and the read arm returns the NEWEST (the
         last-saved position — where the reader last was); the save rides the
         CLIENT outbox (the _SYNC_COMMANDS membership — the sync intent);
         the crash matrix's lost-ack arm: post-commit-pre-ack exits 2 with
         the effect committed and the replay converges the ack
  POS-04 THE GENERATION BINDING HONEST ACROSS A RE-EXTRACTION (the
         serving-generation routing): after a re-extraction supersedes the
         saved generation, get-position returns the SAVED offsets
         byte-unchanged + saved_generation_id == the ORIGINAL generation +
         current_generation_id == the NEW one + generation_matches=false —
         NEVER a silent retarget (no offset remapping, no rebinding of the
         saved row); the saved row's generation_id is immutable (the row
         audit); a NEW save after the re-extraction binds the CURRENT
         generation (the serving-generation routing: new saves ride the
         serving generation)
  POS-05 the read arm's no-oracle + the typed answers: get-position on an
         absent source refuses with the SAME bytes as get-source on the same
         id (ARV-QRY-001 — one machinery, the family="source" form); owner B
         reading A's source-with-a-saved-position gets the SAME refusal as B
         reading an absent source (never a leak that a position exists); an
         in-scope source NEVER SAVED answers the typed no_position_saved
         ANSWER at exit 0 (a state, never a failure — the capability measure
         precedent) with api_version=1
  POS-06 the reserved surface made real + the schema conventions (0014):
         capability.py's surfaces row for source-open/position names the
         LANDED backend verbs (save_position/get_position) while the reader
         client stays P4-B (owner_phase P4-A/B unchanged); the schema
         conventions audited — NO DEFAULTs (LAW-24), RLS enabled AND FORCED
         + the owner policy, the grants (INSERT+SELECT to arv_app, SELECT to
         arv_read, NO UPDATE/DELETE), the two composite FKs (source +
         generation), the (owner, source, ordinal) UNIQUE; the frozen ack
         grammar on every ack and replay line (api_version)

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no reader-client work
(P4-B's repo); no dwell/session events (D-010's boundary, P4-C's); no
EPUB/PDF increments (the following P4-A slices).

Run: python3 harness/tests/test_position.py   (exit 0 = green)
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
# per surface.
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                          "save_position", "--help"], capture_output=True, text=True)
_absent_cmd = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "get-position", "--owner", "A", "--source", "x"],
                         capture_output=True, text=True, timeout=60)
_absent_arm = "invalid choice" in _probe2.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0014_*.sql"))
if _absent_cmd or _absent_arm or not _mig:
    print(f"FAIL ARV-TEST-000: the P4-A slice two position machinery is absent "
          f"(machinery-absent class; save_position command absent: {_absent_cmd}; "
          f"get-position arm absent: {_absent_arm}; migration 0014 present: {bool(_mig)}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None
# the corpus: a reading text with several paragraphs — the derived view the
# reader positions into (decoded-text coordinates)
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


def cmd(op: str, *args, owner="A", key=None, client="cli-1",
        crash_at=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client]
    if key is not None:
        a += ["--idem-key", key]
    if crash_at is not None:
        a += ["--crash-at", crash_at]
    return cli(*a, *args)


def extract(key: str, source_id: str, owner: str = "A") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor", "owner",
               "--client-id", "cli-1", "--idem-key", key, "--source-id", source_id)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


def save(source_id: str, start: int, end: int, key: str, owner="A",
         crash_at=None) -> subprocess.CompletedProcess:
    if crash_at is not None:
        # THE HOUSE CRASH VOCABULARY (the NTE-06 pattern; the implementation-cycle
        # amendment disclosed in the GREEN commit): the injection rides
        # harness/crash.py --point — commands.py itself carries no --crash-at flag
        # (exit 2 is crash.py's vocabulary, never argparse's)
        return cli(str(REPO / "harness" / "crash.py"), "--command", "save_position",
                   "--point", crash_at, "--owner", owner, "--actor", "owner",
                   "--client-id", "cli-1", "--idem-key", key,
                   "--source-id", source_id, "--start", str(start), "--end", str(end))
    return cmd("save_position", "--source-id", source_id,
               "--start", str(start), "--end", str(end), key=key, owner=owner)


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


def audit_rows(sql: str) -> list:
    return [ln for ln in audit(sql).splitlines() if ln.strip()]


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    """A hostile/direct write attempt AS the app role (the substrate's own guard)."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_app", "-d", DB,
                           "-c", f"SET app.current_owner='{owner}'; {sql}"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def super_sql(sql: str) -> subprocess.CompletedProcess:
    """The append-only trigger's own audience: a role WITH update/delete
    permission (the rig superuser) — the trigger fires where the least-privilege
    app role is stopped earlier at the permission boundary."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "postgres", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60, env=ENV)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4a2")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4a2-"))

        # the fixtures: TWO extracted sources (the second for the
        # generation-bind guard's cross-source probe) + one never-extracted
        f1 = tmp / "reading.txt"
        f1.write_text(TEXT, encoding="utf-8")
        r_i1 = cmd("import_source", "--title", "The Reading Text",
                   "--file", str(f1), key="imp-1")
        src1 = ref_of(r_i1)
        r_e1 = extract("ext-1", src1)
        f2 = tmp / "other.txt"
        f2.write_text("A different document entirely.\nIts paragraphs are its own.\n",
                      encoding="utf-8")
        r_i2 = cmd("import_source", "--title", "The Other Text",
                   "--file", str(f2), key="imp-2")
        src2 = ref_of(r_i2)
        extract("ext-2", src2)
        f3 = tmp / "never.txt"
        f3.write_text("Imported but never extracted.\n", encoding="utf-8")
        r_i3 = cmd("import_source", "--title", "The Unextracted Text",
                   "--file", str(f3), key="imp-3")
        src3 = ref_of(r_i3)
        gen1 = jline(cap("measure", "--owner", "A", "--source", src1)).get("generation_id", "")

        # ---- POS-01 — the save->reopen->return round-trip
        start, end = len(TEXT) // 3, len(TEXT) // 2
        r_s1 = save(src1, start, end, key="pos-1")
        ack1 = next((ln for ln in r_s1.stdout.splitlines() if ln.startswith("ACK")), "")
        # the reopen: a FRESH read invocation returns the saved position
        r_g1 = get_pos("A", src1)
        g1 = jline(r_g1)
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='reading_position';")
        no_content = cols and not any(c in ("content", "text", "selected_text",
                                            "passage_text", "body") for c in cols)
        need_cols = {"id", "owner_scope", "source_id", "save_ordinal",
                     "generation_id", "start_off", "end_off", "actor",
                     "run_id", "input_hash", "idempotency_key", "created_at"}
        ok1 = (r_s1.returncode == 0
               and "status=committed" in ack1
               and f"result_ref={src1}@1" in ack1
               and "save=1" in ack1
               and "durability_rung=local_durable" in ack1
               and "api_version=1" in ack1
               and r_g1.returncode == 0
               and g1.get("state") == "saved"
               and g1.get("source_id") == src1
               and g1.get("save_ordinal") == 1
               and g1.get("start_off") == start
               and g1.get("end_off") == end
               and g1.get("saved_generation_id") == gen1
               and g1.get("current_generation_id") == gen1
               and g1.get("generation_matches") is True
               and g1.get("api_version") == 1
               and no_content and need_cols <= set(cols))
        check("POS-01", ok1,
              "the save->reopen->return round-trip at the real boundary: the save acks with the "
              "full frozen contract (status=committed + result_ref=<source>@<ordinal> + save=<n> + "
              "durability_rung=local_durable + api_version=1); the reopen (a FRESH get-position) "
              "returns the saved offsets + its generation binding (saved_generation_id == the "
              "current generation, generation_matches=true); the row's column set carries NO "
              "content copy (the structural no-copy law)",
              "harness/commands.py save_position through the spine's own ack contract + "
              "harness/query.py get-position over migration 0014's reading_position rows — never "
              "a second durability path, never a content column")

        # ---- POS-02 — the typed save refusals + the substrate guards
        absent = str(_uuid.uuid4())
        r_abs = save(absent, 0, 5, key="posx-1")
        r_xo = save(src1, 0, 5, key="posx-2", owner="B")
        r_ng = save(src3, 0, 5, key="posx-3")
        r_o1 = save(src1, -1, 5, key="posx-4")
        r_o2 = save(src1, 10, 10, key="posx-5")
        r_o3 = save(src1, 10, len(TEXT) + 999, key="posx-6")
        rows_before = audit("SELECT count(*) FROM arv.reading_position;")
        # the substrate guards (the hostile-write backstops)
        g_upd = super_sql(f"UPDATE arv.reading_position SET start_off = 0;")
        g_del = super_sql(f"DELETE FROM arv.reading_position;")
        g_ord = app_sql(f"INSERT INTO arv.reading_position (id, owner_scope, source_id, "
                        f"save_ordinal, generation_id, start_off, end_off, actor, run_id, "
                        f"input_hash, idempotency_key, created_at) VALUES ("
                        f"'{_uuid.uuid4()}', 'A', '{src1}', 9, '{gen1}', 0, 5, 'owner', "
                        f"'run-hostile', 'deadbeef', 'hostile-1', now());")
        gen2_src = jline(cap("measure", "--owner", "A", "--source", src2)).get("generation_id", "")
        g_bind = app_sql(f"INSERT INTO arv.reading_position (id, owner_scope, source_id, "
                         f"save_ordinal, generation_id, start_off, end_off, actor, run_id, "
                         f"input_hash, idempotency_key, created_at) VALUES ("
                         f"'{_uuid.uuid4()}', 'A', '{src1}', 2, '{gen2_src}', 0, 5, 'owner', "
                         f"'run-hostile', 'deadbeef', 'hostile-2', now());")
        rows_after = audit("SELECT count(*) FROM arv.reading_position;")
        ok2 = (r_abs.returncode == 1 and "FAIL ARV-POS-001:" in r_abs.stdout
               and r_xo.returncode == 1 and "FAIL ARV-POS-001:" in r_xo.stdout
               and r_abs.stdout.replace(absent, "<id>") == r_xo.stdout.replace(src1, "<id>")
               and r_ng.returncode == 1 and "FAIL ARV-POS-002:" in r_ng.stdout
               and "generation" in r_ng.stdout
               and r_o1.returncode == 1 and "FAIL ARV-POS-003:" in r_o1.stdout
               and r_o2.returncode == 1 and "FAIL ARV-POS-003:" in r_o2.stdout
               and r_o3.returncode == 1 and "FAIL ARV-POS-003:" in r_o3.stdout
               and rows_before == "1" and rows_after == "1"
               and "ARV-POS-005" in g_upd.stderr
               and "ARV-POS-005" in g_del.stderr
               and "ARV-POS-004" in g_ord.stderr
               and "ARV-POS-006" in g_bind.stderr)
        check("POS-02", ok2,
              "the typed save refusals + the substrate guards: absent source and ANOTHER OWNER's "
              "source are the SAME ARV-POS-001 refusal (the no-oracle at the write boundary); a "
              "source with no serving generation refuses ARV-POS-002; invalid offsets (negative / "
              "empty / beyond the text) refuse ARV-POS-003 — never clamped; every refusal leaves "
              "ZERO new rows; direct-DB UPDATE/DELETE refuse ARV-POS-005 (append-only), a hostile "
              "INSERT with a skipped ordinal refuses ARV-POS-004 (the ordinal law), a hostile "
              "INSERT binding ANOTHER SOURCE's generation refuses ARV-POS-006 (the "
              "generation-bind law)",
              "the typed refusals in commands.py save_position + migration 0014's guard "
              "triggers (the serialized advisory lock, the ordinal law, the generation-bind law, "
              "the append-only law)")

        # ---- POS-03 — the idempotency + the position advance + the lost ack
        r_rep = save(src1, start, end, key="pos-1")
        ack_rep = next((ln for ln in r_rep.stdout.splitlines() if ln.startswith("ACK")), "")
        r_409 = save(src1, start, end + 3, key="pos-1")
        # the position advance: a NEW key appends ordinal 2; the read arm returns the NEWEST
        start2, end2 = 0, 10
        r_s2 = save(src1, start2, end2, key="pos-2")
        r_g2 = get_pos("A", src1)
        g2 = jline(r_g2)
        # the crash matrix's lost-ack arm: post-commit-pre-ack exits 2, the effect IS committed,
        # the same-key replay converges the ack
        start3, end3 = 20, 30
        r_cr = save(src1, start3, end3, key="pos-3", crash_at="post-commit-pre-ack")
        # the outbox ride (the implementation-cycle amendment, disclosed: counted AFTER the
        # crash arm — the CRASHED-BUT-COMMITTED save's sync intent rode the same transaction,
        # so the count proves both the ordinary saves AND the crash-committed one; the RED's
        # pre-crash placement could never reach 3 — refusals enqueue nothing, by POS-02's own law)
        obx = audit("SELECT count(*) FROM arv.outbox WHERE command_name = 'save_position';")
        g3_after_crash = jline(get_pos("A", src1))
        r_conv = save(src1, start3, end3, key="pos-3")
        ack_conv = next((ln for ln in r_conv.stdout.splitlines() if ln.startswith("ACK")), "")
        ok3 = (r_rep.returncode == 0 and "status=replayed" in ack_rep
               and f"result_ref={src1}@1" in ack_rep
               and "api_version=1" in ack_rep
               and r_409.returncode == 1 and "FAIL ARV-CMD-409:" in r_409.stdout
               and r_s2.returncode == 0 and f"result_ref={src1}@2" in r_s2.stdout
               and "save=2" in r_s2.stdout
               and r_g2.returncode == 0
               and g2.get("save_ordinal") == 2
               and g2.get("start_off") == start2 and g2.get("end_off") == end2
               and obx.isdigit() and int(obx) >= 3
               and r_cr.returncode == 2
               and g3_after_crash.get("save_ordinal") == 3
               and g3_after_crash.get("start_off") == start3
               and r_conv.returncode == 0 and "status=replayed" in ack_conv
               and f"result_ref={src1}@3" in ack_conv)
        check("POS-03", ok3,
              "the idempotency + the position advance: same key+body -> status=replayed (one row, "
              "the same result_ref); same key+different body -> ARV-CMD-409 (zero effect); a "
              "second save with a NEW key appends ordinal 2 and the read arm returns the NEWEST "
              "(the last-saved position); the save rides the CLIENT outbox (the sync intent); the "
              "lost-ack arm: post-commit-pre-ack exits 2 with the effect committed (the reader's "
              "position IS saved) and the same-key replay converges the ack",
              "the spine's own idempotency + the _SYNC_COMMANDS membership + the crash "
              "injection — the position command inherits the command path's whole contract")

        # ---- POS-04 — THE GENERATION BINDING ACROSS A RE-EXTRACTION
        # (the serving-generation routing: the #99 notverified's disclosure)
        saved_before = jline(get_pos("A", src1))
        r_re = extract("ext-1b", src1)  # the re-extraction: a NEW generation supersedes gen1
        gen_new = jline(cap("measure", "--owner", "A", "--source", src1)).get("generation_id", "")
        r_g4 = get_pos("A", src1)
        g4 = jline(r_g4)
        row_gen = audit("SELECT generation_id FROM arv.reading_position "
                        "WHERE source_id = '" + src1 + "' "
                        "ORDER BY save_ordinal DESC LIMIT 1;")
        # a NEW save after the re-extraction binds the CURRENT generation
        r_s5 = save(src1, 40, 50, key="pos-5")
        g5 = jline(get_pos("A", src1))
        ok4 = (r_re.returncode == 0
               and gen_new and gen_new != gen1
               and saved_before.get("saved_generation_id") == gen1
               and r_g4.returncode == 0
               and g4.get("start_off") == start3 and g4.get("end_off") == end3
               and g4.get("saved_generation_id") == gen1
               and g4.get("current_generation_id") == gen_new
               and g4.get("generation_matches") is False
               and row_gen == gen1
               and r_s5.returncode == 0 and "save=4" in r_s5.stdout
               and g5.get("save_ordinal") == 4
               and g5.get("saved_generation_id") == gen_new
               and g5.get("generation_matches") is True)
        check("POS-04", ok4,
              "THE GENERATION BINDING HONEST ACROSS A RE-EXTRACTION (the serving-generation "
              "routing): after a re-extraction supersedes the saved generation, get-position "
              "returns the SAVED offsets byte-unchanged + saved_generation_id == the ORIGINAL "
              "generation + current_generation_id == the NEW one + generation_matches=false — "
              "NEVER a silent retarget (no offset remapping, no rebinding of the saved row; the "
              "row audit: the saved generation_id still the original); a NEW save after the "
              "re-extraction binds the CURRENT generation (new saves ride the serving "
              "generation, save=4, matches=true)",
              "the serving-generation field on every position row + the read arm's join to the "
              "current generation — the position binds to the generation the reader was reading, "
              "and the answer says which generation it addresses")

        # ---- POS-05 — the read arm's no-oracle + the typed answers
        r_gp_abs = get_pos("A", absent)
        r_gs_abs = query("get-source", "--owner", "A", "--id", absent)
        r_gp_xo = get_pos("B", src1)  # A's source carries a SAVED position — never a leak
        r_gp_babs = get_pos("B", absent)
        # an in-scope source NEVER SAVED: the typed ANSWER at exit 0
        r_gp_none = get_pos("A", src3)
        gnone = jline(r_gp_none)
        ok5 = (r_gp_abs.returncode == 1 and "FAIL ARV-QRY-001:" in r_gp_abs.stdout
               and r_gs_abs.returncode == 1
               and r_gp_abs.stdout == r_gs_abs.stdout
               and r_gp_xo.returncode == 1 and "FAIL ARV-QRY-001:" in r_gp_xo.stdout
               and r_gp_xo.stdout.replace(src1, "<id>") == r_gp_babs.stdout.replace(absent, "<id>")
               and r_gp_none.returncode == 0
               and gnone.get("state") == "no_position_saved"
               and gnone.get("source_id") == src3
               and gnone.get("api_version") == 1)
        check("POS-05", ok5,
              "the read arm's no-oracle + the typed answers: get-position on an absent source "
              "refuses with the SAME bytes as get-source on the same id (ARV-QRY-001 — one "
              "machinery, the family=\"source\" form); owner B reading A's source-with-a-saved-"
              "position gets the SAME refusal as B reading an absent source (never a leak that a "
              "position exists); an in-scope source NEVER SAVED answers the typed "
              "no_position_saved ANSWER at exit 0 (a state, never a failure) with api_version=1",
              "the shared _refuse form + the one-statement flag|payload read (the source "
              "existence, the position row, and the generation binding in ONE snapshot)")

        # ---- POS-06 — the reserved surface made real + the schema conventions
        r_sur = cap("surfaces")
        srows = jlines(r_sur)
        pos_row = next((row for row in srows
                        if row.get("surface") == "source-open/position"), {})
        # the schema conventions (0014): no DEFAULTs, RLS forced, the grants, the FKs, the UNIQUE
        defaults = audit("SELECT count(*) FROM information_schema.columns "
                         "WHERE table_schema='arv' AND table_name='reading_position' "
                         "AND column_default IS NOT NULL;")
        rls = audit("SELECT relrowsecurity AND relforcerowsecurity FROM pg_class "
                    "WHERE oid = 'arv.reading_position'::regclass;")
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' "
                    "AND tablename='reading_position' AND policyname='owner_isolation' "
                    "AND roles::text = '{arv_app}';")
        grants = audit("SELECT has_table_privilege('arv_app','arv.reading_position','INSERT') "
                       "|| '|' || has_table_privilege('arv_app','arv.reading_position','UPDATE') "
                       "|| '|' || has_table_privilege('arv_app','arv.reading_position','DELETE') "
                       "|| '|' || has_table_privilege('arv_read','arv.reading_position','SELECT');")
        fks = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                    "'arv.reading_position'::regclass AND contype = 'f' "
                    "AND array_length(conkey, 1) = 2;")
        uniq = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                     "'arv.reading_position'::regclass AND contype = 'u' "
                     "AND pg_get_constraintdef(oid) = 'UNIQUE (owner_scope, source_id, save_ordinal)';")
        ok6 = (r_sur.returncode == 0
               and all(row.get("api_version") == 1 for row in srows)
               and pos_row.get("owner_phase") == "P4-A/B"
               and "save_position" in str(pos_row.get("reservation", ""))
               and "get_position" in str(pos_row.get("reservation", ""))
               and defaults == "0"
               and rls == "t" and pol == "1"
               and grants == "true|false|false|true"  # the || concatenation's full-word form (the test_import.py:533 precedent; the RED's 't|f|f|t' was never green — the implementation-cycle amendment, disclosed)
               and fks == "2" and uniq == "1"
               and "api_version=1" in ack1 and "api_version=1" in ack_rep)
        check("POS-06", ok6,
              "the reserved surface made real + the schema conventions (0014): capability.py's "
              "surfaces row for source-open/position names the LANDED backend verbs "
              "(save_position/get_position) while the reader client stays P4-B (owner_phase "
              "P4-A/B unchanged — the CAP-03 pin holds); the schema audited — NO DEFAULTs "
              "(LAW-24), RLS enabled AND FORCED + the owner_isolation policy on arv_app, the "
              "grants (INSERT+SELECT to arv_app, SELECT to arv_read, NO UPDATE/DELETE), the two "
              "composite FKs (source + generation), the (owner, source, ordinal) UNIQUE; the "
              "frozen ack grammar on every ack and replay line (api_version)",
              "harness/capability.py's RESERVED_SURFACES registry updated to the landed contract "
              "+ migration 0014's conventions (the 0004/0008/0009 substrate pattern)")

        if FAILS:
            print(f"\nPOSITION SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the source-open/position contract is broken or unimplemented)")
            return 1
        print("\nPOSITION SUITE GREEN — POS-01..06 (the source-open/position surface: the "
              "save->reopen->return round-trip with the serving-generation binding honest "
              "across a re-extraction, the typed refusals with the substrate guards, the "
              "no-oracle read arm)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
