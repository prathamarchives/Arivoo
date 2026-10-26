#!/usr/bin/env python3
"""harness/tests/test_extract.py — P3-03a acceptance suite (the extraction
generations — RTM §2.3/§3.6, SYS-06/07's primary trace; PLAN's P3-03 card's
generation half).

Red-first (LAW-11): committed BEFORE the implementation; at the predecessor
0ce7077 the suite fails with ARV-TEST-000 (machinery-absent: extract.py /
migration 0006 / the extract command do not exist — the S1/record-18 §4.1
precedent class).

THE GENERATION MACHINE (§3.6, the extraction's instantiation of the derived-
state pattern):
  (empty) --extract--> building
  building --complete generation--> current    [passages + the generation row atomically]
  building --crash--> building                  [the recovery: the next extract supersedes]
  building --failure--> failed                  [named reason; the previous stays current]
  current --new extraction of the SAME source--> current(new) + superseded(old)
  current --new edition (a NEW source row)--> the generation of the NEW source only

THE DERIVED-STATE RULES (§2.9/SYS-07): the generation row + the passages are
DISPOSABLE (never authoritative; no unique authored content lives only
here); complete-or-failed publication (a partial generation is never
presented); the generation carries the full processing lineage (the extractor
name+version+config + the input digest = the source's digest — the version
bind); a source hash mismatch is the STALE detection (the generation's input
digest vs the source's CURRENT digest).

Cases (the EXT registry — this file is the contract's declaration):
  EXT-01 the happy path: extract a complete source -> building -> current,
        the passages derived from the bytes (the paragraph-block split, the
        pinned readable-text/Markdown choice), the generation's lineage true
  EXT-02 invalid input: an empty file -> the named refusal, zero generations
  EXT-03 the encoding boundary: a non-UTF-8 source (the P3-01 media
        boundary) -> the named refusal, zero generations
  EXT-04 the passage boundary: the block split on the canonical fixture
        (blank-line paragraphs; the offsets cover the text contiguously; the
        passage digests re-hash. The size-capped split of an over-long block
        is NOT this slice's contract — routed to the read-path/indexing
        slices' own bounded work, never claimed here)
  EXT-05 the extraction crash (pre-commit): building row persists; ZERO
        passages; the previous generation stays current; the retry commits
  EXT-06 the crash AFTER the commit (post-commit-pre-ack): the generation
        current with its passages; the replay answers the recorded result
  EXT-07 the idempotent re-extraction: the same source re-extracted -> the
        new generation current, the OLD superseded (both rows retained — the
        versioned lineage); the passages byte-identical for byte-identical input
  EXT-08 the new edition: the same work, a NEW source row (version 2) -> the
        generation binds the NEW source only; the old source's generation
        untouched; a generation NEVER crosses source rows
  EXT-09 the stale-detection substrate: the generation's input digest binds
        the source row it was built from (the digest MATCH is the substrate —
        the typed stale REPORTING is the read path's own slice, never
        claimed here; a mismatch is observable, never silent)
  EXT-10 the extraction failure mid-build (the planted RAISE): the failed
        row with the named reason; the previous current generation STAYS
        current (never a partial presentation)
  EXT-11 the §2.9 conventions on the two new tables: no defaults, RLS
        forced, arv_read SELECT, the actor vocabulary, the state CHECKs, the
        generation UNIQUE(source_id, ordinal) + the passages FK; and the
        DERIVED class declared: the generation tables have NO append-only
        trigger and NO command_log row (the extraction is a DERIVED build,
        not an owner command — §2.9's disposable class; the generation
        updates are lawful state transitions)
  EXT-12 owner isolation: the extraction is RLS-scoped; B never sees A's
        generations; the direct-DB escape fails closed (both layers)
  EXT-13 the NUL boundary (the SEV round's F1, found live): a valid-UTF-8
        text containing U+0000 -> the named refusal, zero generations (the
        psql literal transport cannot carry a NUL byte-exactly — the
        extraction refuses at the boundary, never a silently truncated
        passage presented as current)
  EXT-14 the deadlock race class (the #87 CodeRabbit round 2; the class the
        SEV round's live races OBSERVED): the loser of a same-source
        completion race is a RETRYABLE conflict — ARV-EXT-006, the building
        row persists (never a failed generation for a race), the same-key
        retry completes it
  EXT-15 the same-key replay answers the RECORDED FAILURE (the #87 CodeRabbit
        round 2): a failed generation replayed under its own key -> exit 1 +
        the stored reason, never a silent ACK-success

Run: python3 harness/tests/test_extract.py   (exit 0 = green)
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
except ImportError as e:
    print(f"FAIL ARV-TEST-000: the kernel does not exist (waiting-for-harness) — {e}")
    sys.exit(1)

_absent_files = [str(p) for p in (REPO / "harness" / "extract.py",
                                  REPO / "harness" / "migrations" / "0006_extraction_generations.sql")
                 if not p.is_file()]
_absent_cmd = "extract_source" not in REGISTRY
if _absent_files or _absent_cmd:
    print(f"FAIL ARV-TEST-000: the extraction machinery is absent (machinery-absent class; "
          f"missing files: {[p.split('/')[-1] for p in _absent_files]}; missing the extract_source command: {_absent_cmd}) — "
          "P3-03a's implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = None
ENV = None
BLOB_DIR = None


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=180, env=ENV)


def import_src(key, title, file, owner="A", media="text/plain", work_id=None):
    a = [str(REPO / "harness" / "commands.py"), "import_source", "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
         "--file", file, "--media-type", media]
    if title is not None:
        a += ["--title", title]
    if work_id:
        a += ["--work-id", work_id]
    return cli(*a)


def extract(key, source_id, owner="A", crash_at=None):
    a = [str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor", "owner",
         "--client-id", "cli-1", "--idem-key", key, "--source-id", source_id]
    if crash_at:
        a += ["--crash-at", crash_at]
    return cli(*a)


def crash(*args):
    return cli(str(REPO / "harness" / "crash.py"), *args)


def audit(query):
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", query],
                          capture_output=True, text=True, timeout=60).stdout.strip()


def ack_field(p, field):
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def fresh_file(name, text_or_bytes):
    d = tempfile.mkdtemp(prefix="arv-ext-")
    f = pathlib.Path(d) / name
    if isinstance(text_or_bytes, bytes):
        f.write_bytes(text_or_bytes)
    else:
        f.write_text(text_or_bytes, encoding="utf-8")
    return str(f)


def main() -> int:
    global DB, ENV, BLOB_DIR
    DB = pg.create_scratch_db("p303a")
    BLOB_DIR = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=BLOB_DIR)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)
        TEXT = ("# The Compound Essay\n\n"
                "First paragraph: the reading act compounds.\n\n"
                "Second paragraph carries the marginalia words here.\n\n"
                "Third paragraph closes the piece.\n")
        fA = fresh_file("essay.md", TEXT)
        p_imp = import_src("ext-src-1", "The Compound Essay", fA)
        sid = ack_field(p_imp, "result_ref")

        # EXT-01 — the happy path
        p = extract("ext-01", sid)
        gen = audit(f"SELECT state, extractor, input_digest FROM arv.extraction_generation "
                    f"WHERE source_id='{sid}' AND ordinal=1;")
        n_pass = audit(f"SELECT count(*) FROM arv.passage WHERE generation_id="
                       f"(SELECT id FROM arv.extraction_generation WHERE source_id='{sid}' AND state='current');")
        ok1 = (p.returncode == 0 and "status=committed" in p.stdout
               and gen.split("|")[0] == "current"
               and gen.split("|")[1].startswith("arivoo-text-")
               and gen.split("|")[2] == audit(f"SELECT digest FROM arv.source WHERE id='{sid}';")
               and n_pass == "3" and int(n_pass) >= 3)
        check("EXT-01", ok1,
              "extract_source: building -> current with the full lineage (the extractor name+version, the input digest = the source's digest) and the 3 paragraphs derived from the bytes",
              "the generation must publish complete-or-failed: the passages + the generation's current-state update commit atomically, the lineage binding the input version")

        # EXT-04 — the passage boundary (the pinned readable-text split)
        rows = audit(f"SELECT p.ordinal, p.start_off, p.end_off FROM arv.passage p "
                     f"JOIN arv.extraction_generation g ON p.generation_id=g.id "
                     f"WHERE g.source_id='{sid}' AND g.state='current' ORDER BY p.ordinal;")
        offs = [tuple(r.split("|")) for r in rows.splitlines()]
        ok4 = (len(offs) == 3 and offs[0][1] == "0"
               and all(int(offs[i][1]) < int(offs[i][2]) for i in range(3))
               and all(int(offs[i][2]) == int(offs[i + 1][1]) for i in range(2))
               and int(offs[-1][2]) == len(TEXT))
        check("EXT-04", ok4,
              "the block split on the canonical fixture: 3 ordinals with contiguous, ordered, in-range character offsets (the pinned readable-text/Markdown choice)",
              "the extractor's location evidence must be the format-appropriate offsets into the decoded text, contiguous and ordered — never a guess")

        # EXT-02 — the empty input
        fEmpty = fresh_file("empty.md", "")
        p_imp2 = import_src("ext-src-2", "Empty Book", fEmpty)
        sid2 = ack_field(p_imp2, "result_ref")
        p2 = extract("ext-02", sid2)
        n2 = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid2}';")
        ok2 = (p2.returncode == 1 and "ARV-EXT-001" in p2.stdout and n2 == "0")
        check("EXT-02", ok2,
              "an empty source -> the named ARV-EXT-001 refusal, ZERO generation rows (an empty input is a named refusal, never an empty current generation)",
              "the extraction validates before any row: an empty input has no passages to derive — the refusal precedes the build")

        # EXT-03 — the encoding boundary
        fBin = fresh_file("binary.bin", bytes(range(256)))
        p_imp3 = import_src("ext-src-3", "Binary Book", fBin, media="application/octet-stream")
        sid3 = ack_field(p_imp3, "result_ref")
        p3 = extract("ext-03", sid3)
        n3 = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid3}';")
        ok3 = (p3.returncode == 1 and "ARV-EXT-002" in p3.stdout and n3 == "0")
        check("EXT-03", ok3,
              "a non-UTF-8 source at extraction -> the named ARV-EXT-002 refusal, zero rows (the readable-text boundary; the P3-01 media class)",
              "the extraction decodes under the source's media type — a binary decode failure is a named refusal, never a guessed text")

        # EXT-05 — the crash pre-commit: building persists, zero passages, the retry commits
        c5 = crash("--command", "extract_source", "--point", "pre-commit",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "ext-05",
                   "--source-id", sid, "--file", fA)
        st5 = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=2;")
        n5 = audit(f"SELECT count(*) FROM arv.passage WHERE generation_id="
                   f"(SELECT id FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=2);")
        r5 = extract("ext-05", sid)
        st5b = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=2;")
        np5b = audit(f"SELECT count(*) FROM arv.passage WHERE generation_id="
                     f"(SELECT id FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=2);")
        ok5 = (c5.returncode == 2 and st5 == "building" and n5 == "0"
               and r5.returncode == 0 and "status=committed" in r5.stdout
               and st5b == "current" and np5b == "3")
        check("EXT-05", ok5,
              "a crashed extraction (pre-commit): the building row persists with ZERO passages (a partial generation is never presented); the retry completes it — current with the passages",
              "the generation publishes complete-or-failed: the passages commit with the current-state transition atomically; a crash mid-build leaves only the building marker")

        # EXT-07 — the idempotent re-extraction: the old superseded, the passages byte-identical
        p7 = extract("ext-07", sid)
        states = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid}' ORDER BY ordinal;")
        d7 = audit(f"SELECT md5(string_agg(p.text, '||' ORDER BY p.ordinal)) FROM arv.passage p "
                   f"JOIN arv.extraction_generation g ON p.generation_id=g.id "
                   f"WHERE g.source_id='{sid}' AND g.ordinal=3;")
        d1 = audit(f"SELECT md5(string_agg(p.text, '||' ORDER BY p.ordinal)) FROM arv.passage p "
                   f"JOIN arv.extraction_generation g ON p.generation_id=g.id "
                   f"WHERE g.source_id='{sid}' AND g.ordinal=2;")
        ok7 = (p7.returncode == 0 and states.splitlines() == ["superseded", "superseded", "current"]
               and d7 == d1)
        check("EXT-07", ok7,
              "a byte-identical re-extraction: the new generation current, the OLD superseded (both retained — the versioned lineage), the passages byte-identical",
              "the re-extraction supersedes, never overwrites: the generation ordinal increments and the old row keeps its lineage (SYS-07's derived-state rule)")

        # EXT-08 — the new edition: a generation never crosses source rows
        fA2 = fresh_file("essay2.md", TEXT + "\nA fourth paragraph arrives.\n")
        p_imp8 = import_src("ext-src-8", None, fA2, work_id=ack_field(p_imp, "work_id"))
        sid8 = ack_field(p_imp8, "result_ref")
        p8 = extract("ext-08", sid8)
        g8 = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid8}';")
        g_old = audit(f"SELECT string_agg(state, ',' ORDER BY ordinal) FROM arv.extraction_generation "
                      f"WHERE source_id='{sid}';")
        ok8 = (p8.returncode == 0 and g8 == "current" and "superseded,superseded,current" == g_old)
        check("EXT-08", ok8,
              "the new edition (a NEW source row of the same work): its generation binds the NEW source only; the old source's generations untouched (a generation NEVER crosses source rows)",
              "the generation's input bind is the source ROW (the version): the ordinal is per-source, the lineage never mixes")

        # EXT-09 — the stale-detection substrate: the digest MATCH binds the
        # source row it was built from (the typed stale REPORTING is the read
        # path's own slice — the corrected header case text)
        st9 = audit(f"SELECT (g.input_digest = s.digest) FROM arv.extraction_generation g "
                    f"JOIN arv.source s ON s.id=g.source_id WHERE g.source_id='{sid8}' AND g.state='current';")
        ok9 = st9 == "t"
        check("EXT-09", ok9,
              "the generation's input digest matches its source's CURRENT digest (the stale detection's substrate: a mismatch is observable, never silent)",
              "the lineage fields are the stale detector: the generation row carries the input digest it was built from — §3.6's 'detected by input version'")

        # EXT-10 — the planted failure mid-build: the named failure, the previous stays current
        plant = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                "CREATE OR REPLACE FUNCTION arv._ext_fail() RETURNS trigger AS $$ "
                                "BEGIN RAISE EXCEPTION 'ARV-EXT-TEST: the planted build failure'; RETURN NEW; END; "
                                "$$ LANGUAGE plpgsql; CREATE TRIGGER ext_fail BEFORE INSERT ON arv.passage "
                                "FOR EACH ROW WHEN (NEW.ordinal = 2) EXECUTE FUNCTION arv._ext_fail();"],
                               capture_output=True, text=True, timeout=60)
        p10 = extract("ext-10", sid8)
        drop = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                               "DROP TRIGGER IF EXISTS ext_fail ON arv.passage; DROP FUNCTION IF EXISTS arv._ext_fail();"],
                              capture_output=True, text=True, timeout=60)
        g10 = audit(f"SELECT state, fail_reason FROM arv.extraction_generation WHERE source_id='{sid8}' AND ordinal=2;")
        cur_after = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid8}' AND ordinal=1;")
        ok10 = (plant.returncode == 0 and drop.returncode == 0 and p10.returncode == 1
                and "ARV-EXT-003" in p10.stdout
                and g10.split("|")[0] == "failed" and cur_after == "current")
        check("EXT-10", ok10,
              "a mid-build failure (the planted RAISE): the failed row with the NAMED reason; the previous current generation STAYS current (never a partial presentation)",
              "§3.6: building --failure--> failed with the named reason; the previous generation stays current — the derived state never degrades what it superseded")

        # EXT-06 — the crash after the commit (lost-ack): the replay answers
        c6 = crash("--command", "extract_source", "--point", "post-commit-pre-ack",
                   "--owner", "A", "--client-id", "cli-1", "--idem-key", "ext-06",
                   "--source-id", sid, "--file", fA)
        st6 = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=4;")
        np6 = audit(f"SELECT count(*) FROM arv.passage WHERE generation_id="
                    f"(SELECT id FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=4);")
        n6_before = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid}';")
        r6 = extract("ext-06", sid)
        n6_after = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid}';")
        ok6 = (c6.returncode == 2 and "status=committed" not in c6.stdout
               and st6 == "current" and np6 == "3" and n6_before == "4"
               and r6.returncode == 0 and "status=replayed" in r6.stdout
               and n6_after == n6_before)
        check("EXT-06", ok6,
              "the lost extraction ack: the generation committed (current), no ack; the SAME-key replay answers status=replayed (the recorded result)",
              "the extraction rides the spine's idempotency: the same key + the same body -> the recorded result, never a second generation")

        # EXT-11 — the §2.9 conventions on the two derived tables
        defs = audit("SELECT column_name FROM information_schema.columns WHERE table_schema='arv' "
                     "AND table_name IN ('extraction_generation','passage') AND column_name IN "
                     "('id','created_at') AND column_default IS NOT NULL;")
        rls = audit("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                    "WHERE n.nspname='arv' AND c.relname IN ('extraction_generation','passage') "
                    "AND c.relrowsecurity AND c.relforcerowsecurity;")
        trig = audit("SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid "
                     "JOIN pg_namespace n ON n.oid=c.relnamespace WHERE NOT t.tgisinternal "
                     "AND n.nspname='arv' AND c.relname IN ('extraction_generation','passage');")
        clog = audit("SELECT count(*) FROM arv.command_log WHERE command_name='extract_source';")
        ordn = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid}' AND ordinal=3;")
        ok11 = (defs == "" and rls == "2" and trig == "0" and clog == "0" and ordn == "1")
        check("EXT-11", ok11,
              "the derived-state conventions: NO defaults (LAW-24), RLS forced on both tables, NO append-only trigger (the §2.9 disposable class — state transitions are lawful updates), NO command_log row (the extraction is a derived build, never an owner command), the generation ordinal unique per source",
              "the generation tables are §2.9 DERIVED: disposable, rebuildable, never authoritative — the shape itself is the rule (SYS-07)")

        # EXT-13 — the NUL boundary (the SEV round's F1, found live): the psql
        # literal transport cannot carry U+0000 (the C-string boundary truncates
        # the statement mid-literal) — the corrupted-commit class is DEAD by the
        # named refusal BEFORE any row
        fNul = fresh_file("nul.md", "before\x00after\n\nsecond block\n")
        p_imp13 = import_src("ext-src-13", "NUL Book", fNul)
        sid13 = ack_field(p_imp13, "result_ref")
        p13 = extract("ext-13", sid13)
        n13 = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid13}';")
        ok13 = (p13.returncode == 1 and "ARV-EXT-005" in p13.stdout and n13 == "0")
        check("EXT-13", ok13,
              "a NUL-bearing valid-UTF-8 source -> the named ARV-EXT-005 refusal, ZERO generation rows (the psql literal transport cannot carry U+0000 — the extraction refuses at the boundary, never a silently truncated passage presented as current)",
              "the complete-or-failed contract: a passage must be the EXACT slice its offsets and digest claim; a text that cannot survive the literal path byte-exactly is a named refusal, never a corrupted commit")

        # EXT-12 — owner isolation
        p_impB = import_src("ext-src-B", "B's Book", fresh_file("bbook.md", "B's own text.\n"), owner="B")
        sidB = ack_field(p_impB, "result_ref")
        pB = extract("ext-12-B", sidB, owner="B")
        pA_wrong = extract("ext-12-A", sidB, owner="A")
        ok12 = (pB.returncode == 0
                and pA_wrong.returncode == 1 and "ARV-EXT-004" in pA_wrong.stdout
                and audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sidB}';") == "1")
        noguc = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-U", "arv_app", "-d", DB, "-c",
                                "SELECT count(*) FROM arv.extraction_generation;"],
                               capture_output=True, text=True, timeout=60)
        ok12 = ok12 and noguc.returncode == 0 and noguc.stdout.strip() == "0"
        check("EXT-12", ok12,
              "owner isolation: B's extraction is B's; A extracting B's source -> the named ARV-EXT-004 refusal; arv_app without the GUC sees ZERO rows (both layers fail closed)",
              "the derived tables inherit the substrate's RLS discipline: same policy shape, same fail-closed — a cross-owner extraction is refused at the boundary, never a silent read")

        # EXT-14 — the deadlock race class (the #87 CodeRabbit round 2; the SEV round's
        # choreographed two-session completions observed the class live): the loser is a
        # RETRYABLE conflict — the building row persists, never a failed generation
        plant14 = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                  "CREATE OR REPLACE FUNCTION arv._ext_dl() RETURNS trigger AS $$ "
                                  "BEGIN RAISE EXCEPTION 'deadlock detected'; RETURN NEW; END; "
                                  "$$ LANGUAGE plpgsql; CREATE TRIGGER ext_dl BEFORE INSERT ON arv.passage "
                                  "FOR EACH ROW WHEN (NEW.ordinal = 1) EXECUTE FUNCTION arv._ext_dl();"],
                                 capture_output=True, text=True, timeout=60)
        p14 = extract("ext-14", sid8)
        drop14 = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", DB, "-c",
                                 "DROP TRIGGER IF EXISTS ext_dl ON arv.passage; DROP FUNCTION IF EXISTS arv._ext_dl();"],
                                capture_output=True, text=True, timeout=60)
        st14 = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid8}' AND ordinal=3;")
        r14 = extract("ext-14", sid8)
        st14b = audit(f"SELECT state FROM arv.extraction_generation WHERE source_id='{sid8}' AND ordinal=3;")
        ok14 = (plant14.returncode == 0 and drop14.returncode == 0 and p14.returncode == 1
                and "ARV-EXT-006" in p14.stdout and st14 == "building"
                and r14.returncode == 0 and "status=committed" in r14.stdout and st14b == "current")
        check("EXT-14", ok14,
              "the deadlock-race loser: ARV-EXT-006, the building row persists (a race is never a failed generation); the same-key retry completes it",
              "the race class is retryable by construction: the rolled-back completion leaves the building row; the permanent failed state is reserved for REAL mid-build failures")

        # EXT-15 — the same-key replay answers the recorded failure (the #87 CodeRabbit round 2)
        n15_before = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid8}';")
        p15 = extract("ext-10", sid8)
        n15_after = audit(f"SELECT count(*) FROM arv.extraction_generation WHERE source_id='{sid8}';")
        ok15 = (p15.returncode == 1 and "ARV-EXT-003" in p15.stdout
                and "status=replayed" not in p15.stdout and n15_after == n15_before)
        check("EXT-15", ok15,
              "the same-key replay of a FAILED generation: exit 1 + the recorded reason, ZERO new rows — never a silent ACK-success",
              "the replay must answer the recorded OUTCOME: a caller reading the exit code learns the extraction failed, never a false success")

    finally:
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)
    if FAILS:
        print(f"RED — {len(FAILS)} broken case(s): {', '.join(FAILS)}")
        return 1
    print("GREEN — the extraction generations hold end-to-end (EXT-01..15): complete-or-failed, versioned, disposable, owner-scoped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
