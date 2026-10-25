#!/usr/bin/env python3
"""harness/tests/test_migrations.py — S1 acceptance suite (Phase 2 Layer 2.1; D-036).

Red-first (LAW-11): this file was committed BEFORE the implementation and observed
failing with ARV-TEST-000 (waiting-for-harness) — the red evidence is preserved in
record 18 §4.1. Every failure prints a named code, the violation, and the repair
(diagnostics contract, OPERATING-MODEL §8.4).

S1 acceptance (the 2026-10-16 review §7, mapped to named codes):
  (a) fresh DB -> migrate -> schema present, verified by an INDEPENDENT psql connection
      (the test's own subprocess — not migrate.py's code path)        ARV-TEST-003
  (b) second migrate run = no-op (nothing re-applied)                ARV-TEST-004
  (c) migrate on a populated DB preserves every row (count+checksum) ARV-TEST-005
  (d) drop DB -> replay -> identical schema hash                     ARV-TEST-006
  (e) must-reject: applied-migration drift (edited after apply)      ARV-MIG-005
      must-reject: out-of-order (hole) application                   ARV-MIG-004
      must-reject: destructive migration without baseline bump       ARV-MIG-003
      positive control: WITH the -- arv-baseline-bump directive the
      destructive migration applies                                  ARV-TEST-007

P3-M0 acceptance (the migration oracle; PLAN's P3-M0 card + RTM §5; the directive's
§6.2 eight-point contract; F-009/F-010 — the rebuilt RED-first enumeration, this
suite's own declaration — CLAIM-045, record 38 §3):
  (f) comment-proof destructive detection (F-009):
      comments BETWEEN keywords must not evade the guard              ARV-TEST-011
      destructive words in COMMENTS ONLY must not falsely refuse       ARV-TEST-012
  (g) embedded transaction control is refused pre-execution, with zero
      effects + zero bookkeeping proven by independent reads:
      the arv.ghost form (CREATE; COMMIT; SELECT 1/0)                 ARV-TEST-013
      an embedded BEGIN                                               ARV-TEST-014
  (h) the admitted fail-closed grammar:
      procedural/dynamic SQL (DO) WITHOUT the directive refused       ARV-TEST-015
      WITH the -- arv-baseline-bump directive it applies (control)     ARV-TEST-016
      the 0001_baseline bootstrap exemption is name-scoped (control)  ARV-TEST-023
  (i) safe migration filenames (F-010): the crafted-quote name that
      poisoned the ledger at the predecessor is refused pre-run        ARV-TEST-017
      the alphabet violation (uppercase/hyphen) is refused             ARV-TEST-018
  (j) bidirectional directory<->ledger history (ARV-MIG-012):
      an extra ledger row not in the directory -> migrate AND verify   ARV-TEST-019
      an applied file removed from the directory -> verify AND migrate ARV-TEST-025
  (k) observation-only verify (ARV-MIG-013):
      on a never-migrated DB verify refuses and CREATES NOTHING        ARV-TEST-020
      on a healthy DB verify rewrites no bookkeeping (control)         ARV-TEST-021
  (l) zero-effects + nonempty-oracle proofs (§6.2; A08):
      normal multi-statement failure -> zero tables, zero rows         ARV-TEST-022
      the full-content ledger/schema/RLS/trigger/policy oracle         ARV-TEST-024
Run: python3 harness/tests/test_migrations.py   (exit 0 = green)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
REAL_MIGRATIONS = str(REPO / "harness" / "migrations")

# ARV-TEST-000: the waiting-for-harness class — the review's fail-first contract.
try:
    sys.path.insert(0, str(REPO))
    from harness.adapters import pg  # noqa: E402
    from harness import migrate  # noqa: E402
except ImportError as e:  # ARV-TEST-000
    print("FAIL ARV-TEST-000: the harness does not exist yet (waiting-for-harness) —")
    print("      import failed:", e)
    print("      repair: implement harness/adapters/pg.py and harness/migrate.py (S1)")
    sys.exit(1)

FAILS: list[str] = []


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def run_migrate(db: str, migrations_dir: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, ARV_MIGRATIONS_DIR=migrations_dir, PGDATABASE=db)
    return subprocess.run(
        [sys.executable, str(REPO / "harness" / "migrate.py")],
        capture_output=True, text=True, env=env, timeout=120,
    )


def sql(db: str, query: str, user: str = None) -> subprocess.CompletedProcess:
    """An INDEPENDENT psql connection (the test's own subprocess, never
    migrate.py's code path — the S1 form of the independent read, LAW-13's spirit;
    S2 strengthens it to the arv_read role)."""
    cmd = ["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1"]
    if user:
        cmd += ["-U", user]
    cmd += ["-d", db, "-c", query]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def schema_hash(db: str) -> str:
    q = (
        "SELECT table_name||'|'||column_name||'|'||data_type||'|'||is_nullable "
        "FROM information_schema.columns WHERE table_schema='arv' "
        "ORDER BY table_name, ordinal_position;"
    )
    r = sql(db, q)
    import hashlib
    return hashlib.sha256(r.stdout.encode()).hexdigest()


def ledger(db: str, cols: str = "version, name, checksum, applied_by") -> list:
    """The INDEPENDENT full-content read of the bookkeeping table (A08: the
    oracle compares actual values, never a count alone; the caller names the
    columns — 021 includes applied_at, the SEV-9b strengthening)."""
    r = sql(db, f"SELECT {cols} FROM arv.schema_migrations ORDER BY version;")
    return [tuple(line.split("|")) for line in r.stdout.strip().splitlines() if "|" in line]


def regclass(db: str, name: str) -> str:
    """An INDEPENDENT existence read: 'arv.evidence_event' present or NULL."""
    return sql(db, f"SELECT to_regclass('{name}');").stdout.strip()


def newdir(tmp: str, sub: str, real_names: list = (), files: dict = None) -> str:
    """A scratch migrations directory: copies of real files + synthetic files."""
    d = os.path.join(tmp, sub)
    os.makedirs(d, exist_ok=True)
    for n in real_names:
        shutil.copy(os.path.join(REAL_MIGRATIONS, n), os.path.join(d, n))
    for n, blob in (files or {}).items():
        with open(os.path.join(d, n), "w") as f:
            f.write(blob)
    return d


def file_digest(path: str) -> str:
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    # (0) the real stack is reachable — the S1 rig precondition
    r = pg.psql("SELECT 1;", db="postgres")
    check("ARV-TEST-001", r.returncode == 0,
          "PostgreSQL reachable through the adapter (the real stack, not a mock)",
          "start the rig: locally the .pg cluster on 5433; CI the postgres:17 service — PGHOST/PGPORT/PGUSER name it (FACT-001 records the engine)")

    tmp = tempfile.mkdtemp(prefix="arv_s1_")
    test_db = pg.create_scratch_db("s1_accept")
    try:
        real_migrations = str(REPO / "harness" / "migrations")

        # (a) fresh DB -> migrate -> schema present via INDEPENDENT psql
        r1 = run_migrate(test_db, real_migrations)
        check("ARV-TEST-002", r1.returncode == 0,
              f"migrate on a fresh DB exits 0 (stderr tail: {r1.stderr.strip()[-120:] or 'none'})",
              "repair the runner per its own ARV-MIG-NNN output")
        rows = sql(test_db, "SELECT count(*) FROM arv.schema_migrations;").stdout.strip()
        roles = sql(test_db, "SELECT count(*) FROM pg_roles WHERE rolname IN ('arv_app','arv_read');").stdout.strip()
        expected = str(len([f for f in os.listdir(real_migrations) if f.endswith(".sql")]))
        check("ARV-TEST-003", rows == expected and roles == "2",
              f"INDEPENDENT psql read: schema_migrations has all {rows} migration(s) applied and both roles exist ({roles}) — the baseline is real",
              "the migration did not produce the declared baseline — inspect the migrations dir vs the DB")

        # (b) second migrate run = no-op
        before = sql(test_db, "SELECT count(*) FROM arv.schema_migrations;").stdout.strip()
        r2 = run_migrate(test_db, real_migrations)
        after = sql(test_db, "SELECT count(*) FROM arv.schema_migrations;").stdout.strip()
        check("ARV-TEST-004", r2.returncode == 0 and before == after,
              f"second migrate run is a no-op (rows before={before}, after={after}, exit={r2.returncode})",
              "the runner re-applied or errored on a fully-applied DB — forward-only bookkeeping is broken (ARV-MIG-002 class)")

        # (c) populated DB: a NEW migration must preserve existing rows
        mdir = os.path.join(tmp, "pop")
        os.makedirs(mdir)
        shutil.copy(os.path.join(real_migrations, "0001_baseline.sql"), mdir)
        with open(os.path.join(mdir, "0002_sentinel.sql"), "w") as f:
            f.write("CREATE TABLE IF NOT EXISTS arv.sentinel (k TEXT PRIMARY KEY, v TEXT NOT NULL);\n"
                    "GRANT SELECT ON arv.sentinel TO arv_read;\n")
        db_c = pg.create_scratch_db("s1_pop")
        run_migrate(db_c, mdir)
        sql(db_c, "INSERT INTO arv.sentinel VALUES ('a','1'),('b','2'),('c','3');")
        with open(os.path.join(mdir, "0003_more.sql"), "w") as f:
            f.write("CREATE TABLE IF NOT EXISTS arv.spare (id BIGINT PRIMARY KEY);\n")
        rc = run_migrate(db_c, mdir)
        cnt = sql(db_c, "SELECT count(*) FROM arv.sentinel;").stdout.strip()
        import hashlib
        cs = hashlib.sha256(sql(db_c, "SELECT k||v FROM arv.sentinel ORDER BY k;").stdout.encode()).hexdigest()[:16]
        check("ARV-TEST-005", rc.returncode == 0 and cnt == "3",
              f"migrate on a populated DB preserves every row (count={cnt}, checksum={cs}, new migration applied)",
              "a migration disturbed existing rows — atomicity or scoping is broken")
        pg.drop_scratch_db(db_c)

        # (d) drop DB -> replay -> identical schema hash
        db_1 = pg.create_scratch_db("s1_hash1")
        db_2 = pg.create_scratch_db("s1_hash2")
        run_migrate(db_1, real_migrations)
        run_migrate(db_2, real_migrations)
        h1, h2 = schema_hash(db_1), schema_hash(db_2)
        check("ARV-TEST-006", h1 == h2 and len(h1) == 64,
              f"replay from scratch yields the identical schema hash ({h1[:16]}...)",
              "replay is not deterministic — a migration is not a pure function of its file")
        pg.drop_scratch_db(db_1)
        pg.drop_scratch_db(db_2)

        # (e) must-rejects
        #   edited-after-apply (checksum drift) -> ARV-MIG-005
        mdir2 = os.path.join(tmp, "drift")
        os.makedirs(mdir2)
        shutil.copy(os.path.join(real_migrations, "0001_baseline.sql"), mdir2)
        db_e = pg.create_scratch_db("s1_drift")
        run_migrate(db_e, mdir2)
        with open(os.path.join(mdir2, "0001_baseline.sql"), "a") as f:
            f.write("\n-- post-apply edit (the must-reject)\n")
        re_ = run_migrate(db_e, mdir2)
        check("ARV-TEST-007", re_.returncode != 0 and "ARV-MIG-005" in re_.stdout + re_.stderr,
              "an APPLIED migration file edited after apply is REFUSED with ARV-MIG-005 (applied-migration drift)",
              "the runner must compare the file's checksum against the recorded one and refuse on drift")
        pg.drop_scratch_db(db_e)

        #   out-of-order hole -> ARV-MIG-004
        mdir3 = os.path.join(tmp, "hole")
        os.makedirs(mdir3)
        with open(os.path.join(mdir3, "0005_hole.sql"), "w") as f:
            f.write("CREATE TABLE IF NOT EXISTS arv.hole (id BIGINT PRIMARY KEY);\n")
        db_h = pg.create_scratch_db("s1_hole")
        rh = run_migrate(db_h, mdir3)
        check("ARV-TEST-008", rh.returncode != 0 and "ARV-MIG-004" in rh.stdout + rh.stderr,
              "starting at version 5 (hole below) is REFUSED with ARV-MIG-004 (forward-only, from the baseline)",
              "the runner must reject a version set that does not start at the baseline 0001")
        pg.drop_scratch_db(db_h)

        #   destructive without baseline bump -> ARV-MIG-003; with it -> applies
        mdir4 = os.path.join(tmp, "drop")
        os.makedirs(mdir4)
        shutil.copy(os.path.join(real_migrations, "0001_baseline.sql"), mdir4)
        with open(os.path.join(mdir4, "0002_dropbad.sql"), "w") as f:
            f.write("DROP TABLE arv.schema_migrations;\n")
        db_d = pg.create_scratch_db("s1_drop")
        rd = run_migrate(db_d, mdir4)
        check("ARV-TEST-009", rd.returncode != 0 and "ARV-MIG-003" in rd.stdout + rd.stderr,
              "a destructive migration WITHOUT -- arv-baseline-bump is REFUSED with ARV-MIG-003",
              "the runner must scan for destructive statements and require the explicit baseline-bump directive")
        with open(os.path.join(mdir4, "0002_dropbad.sql"), "w") as f:
            f.write("-- arv-baseline-bump: 2\nCREATE TABLE arv.temp_x (id INT);\nDROP TABLE arv.temp_x;\n")
        rd2 = run_migrate(db_d, mdir4)
        check("ARV-TEST-010", rd2.returncode == 0,
              "positive control: WITH the -- arv-baseline-bump directive the destructive migration applies",
              "the directive path is broken — the refusal must gate, not block")
        pg.drop_scratch_db(db_d)

        # ------------------------------------------------------------------
        # P3-M0 acceptance (the migration oracle; CLAIM-045) — RED-first group:
        # every named refusal below is observed failing at the predecessor
        # (red-01.txt) before the implementation lands.
        # ------------------------------------------------------------------

        # (f) F-009 comment-evasion: comments BETWEEN keywords must not dodge the
        # destructive guard — at the predecessor this file APPLIED silently.
        d_f9 = newdir(tmp, "sneaky", ["0001_baseline.sql"], {
            "0002_guarded.sql": "CREATE TABLE IF NOT EXISTS arv.guarded (id INT);\n",
            "0003_sneaky.sql": "DROP /* comment splits the guard */ TABLE arv.guarded;\n",
        })
        db_f9 = pg.create_scratch_db("s1_f9")
        pg_f9 = run_migrate(db_f9, d_f9)
        f9_schema = sql(db_f9, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-011", pg_f9.returncode != 0 and "ARV-MIG-003" in pg_f9.stdout + pg_f9.stderr
              and regclass(db_f9, "arv.guarded") == "" and f9_schema == "0",
              "a destructive statement with comments BETWEEN keywords is REFUSED with ARV-MIG-003 pre-execution — the DB completely untouched (the SEV-7 strongest form: no arv schema, nothing applied)",
              "the destructive guard must scan comment-stripped executable text AND fire before the first DB touch — a text-regex on raw bytes is evadable (F-009)")
        pg.drop_scratch_db(db_f9)

        # (f) F-009 mirror: destructive words in COMMENTS ONLY must apply cleanly
        # — at the predecessor the raw-regex guard FALSELY refused this file.
        d_cm = newdir(tmp, "comment", ["0001_baseline.sql"], {
            "0002_comment.sql":
                "-- NOTE: someday an owner might drop table arv.nothing here, and\n"
                "-- a naive guard would truncate this file's review — the words live in\n"
                "-- comments only; the executable text creates one benign table.\n"
                "CREATE TABLE IF NOT EXISTS arv.benign (id INT);\n",
        })
        db_cm = pg.create_scratch_db("s1_cm")
        r_cm = run_migrate(db_cm, d_cm)
        check("ARV-TEST-012", r_cm.returncode == 0 and regclass(db_cm, "arv.benign") == "arv.benign",
              "destructive words inside COMMENTS ONLY do not refuse (comment content is never executable — no false positive)",
              "the guard must strip comments before scanning — comment text is not executable (F-009's mirror)")
        pg.drop_scratch_db(db_cm)

        # (g) the arv.ghost form: embedded COMMIT + trailing failure — at the
        # predecessor the ghost table PERSISTED while the runner reported rollback.
        d_gh = newdir(tmp, "ghost", ["0001_baseline.sql"], {
            "0002_ghost.sql": "CREATE TABLE IF NOT EXISTS arv.ghost (id INT);\nCOMMIT;\nSELECT 1/0;\n",
        })
        db_gh = pg.create_scratch_db("s1_ghost")
        r_gh = run_migrate(db_gh, d_gh)
        gh_ledger = ledger(db_gh) if regclass(db_gh, "arv.schema_migrations") else []
        check("ARV-TEST-013", r_gh.returncode != 0 and "ARV-MIG-011" in r_gh.stdout + r_gh.stderr
              and regclass(db_gh, "arv.ghost") == ""
              and gh_ledger == [] and regclass(db_gh, "arv.schema_migrations") == "",
              f"an embedded COMMIT (CREATE; COMMIT; SELECT 1/0) is REFUSED with ARV-MIG-011 BEFORE execution — the DB completely untouched (the SEV-7 strongest form: no ghost, no ledger table, nothing applied; the predecessor's persisted ghost is red-01.txt)",
              "the runner owns the ONE transaction boundary — embedded transaction control must be refused by a comment/string-aware scan BEFORE any DB touch, never executed (the §6.2 zero-effects proof)")
        pg.drop_scratch_db(db_gh)

        # (g) embedded BEGIN — at the predecessor this file applied (a nested BEGIN
        # is a psql warning, not an error) and its table+row landed.
        d_bg = newdir(tmp, "begin", ["0001_baseline.sql"], {
            "0002_begin.sql": "BEGIN;\nCREATE TABLE IF NOT EXISTS arv.begtab (id INT);\n",
        })
        db_bg = pg.create_scratch_db("s1_begin")
        r_bg = run_migrate(db_bg, d_bg)
        check("ARV-TEST-014", r_bg.returncode != 0 and "ARV-MIG-011" in r_bg.stdout + r_bg.stderr
              and regclass(db_bg, "arv.begtab") == "",
              "an embedded BEGIN is REFUSED with ARV-MIG-011 pre-execution (zero effects)",
              "the runner owns the transaction boundary — BEGIN/COMMIT/ROLLBACK/SAVEPOINT tokens in executable text must refuse")
        pg.drop_scratch_db(db_bg)

        # (h) the admitted fail-closed grammar: procedural/dynamic SQL (a DO
        # block) WITHOUT the directive — at the predecessor it applied.
        d_do = newdir(tmp, "doer", ["0001_baseline.sql"], {
            "0002_doer.sql": "DO $do$ BEGIN NULL; END $do$;\n",
        })
        db_do = pg.create_scratch_db("s1_do")
        r_do = run_migrate(db_do, d_do)
        check("ARV-TEST-015", r_do.returncode != 0 and "ARV-MIG-015" in r_do.stdout + r_do.stderr,
              "a procedural construct (DO block) OUTSIDE the baseline WITHOUT -- arv-baseline-bump is REFUSED with ARV-MIG-015 (fail closed)",
              "the admitted grammar cannot classify procedural/dynamic bodies — the directive is the owner-visible paper trail that admits them (the card's fail-closed contract)")
        pg.drop_scratch_db(db_do)

        # (h) positive control: WITH the directive the same construct applies.
        d_dd = newdir(tmp, "declared", ["0001_baseline.sql"], {
            "0002_declared.sql": "-- arv-baseline-bump: 1\nDO $do$ BEGIN NULL; END $do$;\n",
        })
        db_dd = pg.create_scratch_db("s1_dd")
        r_dd = run_migrate(db_dd, d_dd)
        check("ARV-TEST-016", r_dd.returncode == 0 and len(ledger(db_dd)) == 2,
              "positive control: WITH the -- arv-baseline-bump directive the procedural construct applies (the refusal gates, never blocks)",
              "the directive path is broken — the grammar's admission of declared procedural constructs")
        pg.drop_scratch_db(db_dd)

        # (i) F-010: the crafted-quote filename that POISONED the ledger at the
        # predecessor (the name interpolated into the runner's own INSERT, its
        # template tail consumed by a trailing '-- ' comment: applied exit 0
        # with a fake-checksum row 2 AND a smuggled row 999 — red-01.txt) —
        # refused pre-run by the safe-alphabet check, zero rows beyond baseline.
        evil_name = ("x', 'aaa', 'bbb'); INSERT INTO arv.schema_migrations "
                     "(version, name, checksum, applied_by) VALUES (999, 'smuggled', 'ccc', 'ddd'); --")
        d_ev = newdir(tmp, "evil", ["0001_baseline.sql"], {
            f"0002_{evil_name}.sql": "CREATE TABLE IF NOT EXISTS arv.evil (id INT);\n",
        })
        db_ev = pg.create_scratch_db("s1_evil")
        r_ev = run_migrate(db_ev, d_ev)
        ev_schema = sql(db_ev, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-017", r_ev.returncode != 0 and "ARV-MIG-014" in r_ev.stdout + r_ev.stderr
              and regclass(db_ev, "arv.schema_migrations") == "" and ev_schema == "0",
              f"the crafted-quote filename (the ledger-poisoning payload) is REFUSED with ARV-MIG-014 at discovery, BEFORE any execution — the DB untouched (no arv schema, no ledger — the discovery refusal precedes even 0001's apply; the predecessor's poisoned ledger is red-01.txt)",
              "migration filenames are restricted to the documented safe alphabet — a name outside [a-z0-9_] can never be interpolated into the bookkeeping INSERT (F-010)")
        pg.drop_scratch_db(db_ev)

        # (i) the alphabet violation (uppercase + hyphen) — refused at discovery.
        d_bn = newdir(tmp, "badname", ["0001_baseline.sql"], {
            "0002_Bad-Name.sql": "CREATE TABLE IF NOT EXISTS arv.badname (id INT);\n",
        })
        db_bn = pg.create_scratch_db("s1_bn")
        r_bn = run_migrate(db_bn, d_bn)
        bn_schema = sql(db_bn, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-018", r_bn.returncode != 0 and "ARV-MIG-014" in r_bn.stdout + r_bn.stderr
              and bn_schema == "0",
              "a filename outside the safe alphabet (uppercase/hyphen) is REFUSED with ARV-MIG-014 with the DB completely untouched (the 017-sibling assertion, SEV-9d)",
              "discover() must enforce the safe filename alphabet before any name reaches the ledger — and before the first DB touch")
        pg.drop_scratch_db(db_bn)

        # (j) bidirectional history: an EXTRA LEDGER ROW the directory does not
        # carry — at the predecessor migrate was a silent no-op, verify silent OK.
        d_x = newdir(tmp, "xrow", ["0001_baseline.sql", "0002_evidence_event.sql", "0003_command_log.sql"])
        db_x = pg.create_scratch_db("s1_xrow")
        run_migrate(db_x, d_x)
        sql(db_x, "INSERT INTO arv.schema_migrations (version, name, checksum, applied_by) "
                  "VALUES (999, 'ghost', 'x', 'attacker');")
        r_xm = run_migrate(db_x, d_x)
        env = dict(os.environ, ARV_MIGRATIONS_DIR=d_x, PGDATABASE=db_x)
        r_xv = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--verify"],
                              capture_output=True, text=True, env=env, timeout=120)
        check("ARV-TEST-019", r_xm.returncode != 0 and "ARV-MIG-012" in r_xm.stdout + r_xm.stderr
              and r_xv.returncode != 0 and "ARV-MIG-012" in r_xv.stdout + r_xv.stderr,
              "an extra ledger row (version 999, not in the directory) is REFUSED by BOTH migrate and verify with ARV-MIG-012 (bidirectional history)",
              "history consistency is directory<->ledger BOTH ways — an applied version the directory cannot account for is a poisoned bookkeeping (ARV-MIG-012)")
        pg.drop_scratch_db(db_x)

        # (k) observation-only verify: on a never-migrated DB verify must refuse
        # AND CREATE NOTHING — at the predecessor it bootstrapped arv.schema_migrations.
        db_v = pg.create_scratch_db("s1_vobs")
        env = dict(os.environ, ARV_MIGRATIONS_DIR=REAL_MIGRATIONS, PGDATABASE=db_v)
        r_v = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--verify"],
                             capture_output=True, text=True, env=env, timeout=120)
        v_schema = sql(db_v, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-020", r_v.returncode != 0 and "ARV-MIG-013" in r_v.stdout + r_v.stderr
              and regclass(db_v, "arv.schema_migrations") == "" and v_schema == "0",
              "verify on a never-migrated DB REFUSES with ARV-MIG-013 and CREATES NOTHING (no arv schema, no bootstrapped table — observation-only)",
              "verify must never fabricate the ledger it claims to observe — a missing ledger is an honest typed refusal, never a CREATE side effect (ARV-MIG-013)")
        pg.drop_scratch_db(db_v)

        # (k) control: verify on a healthy DB rewrites no bookkeeping.
        db_h = pg.create_scratch_db("s1_vok")
        run_migrate(db_h, REAL_MIGRATIONS)
        before_h = ledger(db_h, cols="version, name, checksum, applied_by, applied_at")
        r_h = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--verify"],
                             capture_output=True, text=True,
                             env=dict(os.environ, ARV_MIGRATIONS_DIR=REAL_MIGRATIONS, PGDATABASE=db_h), timeout=120)
        check("ARV-TEST-021", r_h.returncode == 0
              and ledger(db_h, cols="version, name, checksum, applied_by, applied_at") == before_h,
              "verify on a healthy DB exits 0 and leaves every ledger row byte-identical INCLUDING applied_at (no rewrites, no bookkeeping — the SEV-9b strengthening)",
              "verify is read-only on the healthy path too — any row change, timestamps included, is a side effect")
        pg.drop_scratch_db(db_h)

        # (l) §6.2 zero-effects: a normal multi-statement failure (a runtime error
        # INSIDE the admitted grammar — a duplicate CREATE, never a grammar
        # refusal) leaves zero tables and zero bookkeeping.
        d_zf = newdir(tmp, "zerofx", ["0001_baseline.sql"], {
            "0002_ok_a.sql": "CREATE TABLE IF NOT EXISTS arv.ok_a (id INT);\n",
            "0003_fails.sql": "CREATE TABLE IF NOT EXISTS arv.ok_b (id INT);\n"
                              "CREATE TABLE arv.ok_b (id INT);\n",
        })
        db_zf = pg.create_scratch_db("s1_zf")
        r_zf = run_migrate(db_zf, d_zf)
        zf_ledger = [row[0] for row in ledger(db_zf)]
        check("ARV-TEST-022", r_zf.returncode != 0 and "ARV-MIG-009" in r_zf.stdout + r_zf.stderr
              and regclass(db_zf, "arv.ok_b") == "" and regclass(db_zf, "arv.ok_a") == "arv.ok_a"
              and zf_ledger == ["1", "2"],
              "a normal multi-statement runtime failure rolls back to ZERO effects (ok_b absent, ok_a preserved from the earlier file, ledger unchanged beyond it)",
              "file+row atomicity: the failing file leaves nothing behind, earlier applied files stay applied")
        pg.drop_scratch_db(db_zf)

        # (h) control: the 0001_baseline bootstrap exemption is name-scoped — the
        # baseline's own DO block (roles) applies WITHOUT any directive.
        d_be = newdir(tmp, "exempt", ["0001_baseline.sql"])
        db_be = pg.create_scratch_db("s1_exempt")
        r_be = run_migrate(db_be, d_be)
        be_roles = sql(db_be, "SELECT count(*) FROM pg_roles WHERE rolname IN ('arv_app','arv_read');").stdout.strip()
        check("ARV-TEST-023", r_be.returncode == 0 and be_roles == "2",
              "the declared 0001_baseline bootstrap exemption: the baseline's own DO block applies WITHOUT a directive (the exemption is scoped to exactly version 1, name 'baseline')",
              "the exemption is name-scoped — the same DO block at 0002 requires the directive (ARV-TEST-015 proves the mirror)")
        pg.drop_scratch_db(db_be)

        # (l) A08 nonempty oracle: the real directory's applied state compared at
        # FULL content — every ledger row's version/name/checksum/applied_by
        # against the file digests, plus the schema/security objects.
        db_or = pg.create_scratch_db("s1_oracle")
        run_migrate(db_or, REAL_MIGRATIONS)
        rows_or = ledger(db_or)
        want = []
        for fn in sorted(os.listdir(REAL_MIGRATIONS)):
            if fn.endswith(".sql"):
                v, nm = fn.split("_", 1)
                want.append((str(int(v)), nm[:-4], file_digest(os.path.join(REAL_MIGRATIONS, fn)), "harness/migrate.py"))
        rls = sql(db_or, "SELECT relname, relrowsecurity FROM pg_class WHERE relname IN "
                         "('evidence_event','command_log') AND relnamespace='arv'::regnamespace ORDER BY relname;").stdout.strip()
        rls_ok = len(rls.splitlines()) == 2 and all(l.endswith("|t") for l in rls.splitlines())
        trig = sql(db_or, "SELECT count(*) FROM pg_trigger WHERE tgrelid IN "
                          "('arv.evidence_event'::regclass, 'arv.command_log'::regclass) AND NOT tgisinternal;").stdout.strip()
        pol = sql(db_or, "SELECT count(*) FROM pg_policies WHERE schemaname='arv';").stdout.strip()
        check("ARV-TEST-024", rows_or == want and rls_ok and trig == "2" and pol == "2",
              f"the nonempty oracle: every ledger row equals the file digest triple ({rows_or == want}), both tables RLS-forced, both immutable triggers present, both owner policies present",
              "A08: a row count is not a recovery proof — the oracle compares actual values")
        pg.drop_scratch_db(db_or)

        # (j) the missing applied tail: an applied file REMOVED from the
        # directory — at the predecessor verify reported 'OK: 1 migration(s)'.
        d_mt = newdir(tmp, "mtail", ["0001_baseline.sql"], {
            "0002_tail.sql": "CREATE TABLE IF NOT EXISTS arv.tail_tab (id INT);\n",
        })
        db_mt = pg.create_scratch_db("s1_mtail")
        run_migrate(db_mt, d_mt)
        os.remove(os.path.join(d_mt, "0002_tail.sql"))
        r_mtv = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--verify"],
                                capture_output=True, text=True,
                                env=dict(os.environ, ARV_MIGRATIONS_DIR=d_mt, PGDATABASE=db_mt), timeout=120)
        r_mtm = run_migrate(db_mt, d_mt)
        check("ARV-TEST-025", r_mtv.returncode != 0 and "ARV-MIG-012" in r_mtv.stdout + r_mtv.stderr
              and r_mtm.returncode != 0 and "ARV-MIG-012" in r_mtm.stdout + r_mtm.stderr,
              "an applied file removed from the directory (a ledger row the directory cannot account for) is REFUSED by BOTH verify and migrate with ARV-MIG-012",
              "bidirectional history: the directory missing an applied version is a broken history — never a silent 'OK: 1 migration(s)'")
        pg.drop_scratch_db(db_mt)

        # ------------------------------------------------------------------
        # P3-M0 acceptance — THE SEV REVIEW ROUND (the fresh-context reviewer's
        # findings, each RED-first at the 946719e head; red-02.txt):
        #   SEV-1 (P0) phantom dollar-quote  -> ARV-TEST-026/027
        #   SEV-2 ALTER IF EXISTS DROP CONSTRAINT -> ARV-TEST-028
        #   SEV-3 data-modifying CTE inside an admitted head -> ARV-TEST-029/030
        #   SEV-4 ledger interior hole (out-of-order re-apply) -> ARV-TEST-031
        #   SEV-5 a renamed applied file (ledger name drift) -> ARV-TEST-032
        #   SEV-8 PREPARE TRANSACTION / CREATE INDEX CONCURRENTLY -> 033/034
        #   SEV-9 the exemption-scope pin + the empty-directory pin -> 035/036
        #   SEV-6 the E-string over-refusal -> ARV-TEST-037
        # ------------------------------------------------------------------

        # SEV-1 Repro A (P0): '$' inside an unquoted identifier (b$$c) opened a
        # PHANTOM dollar-quote at the predecessor, hiding an executable DROP TABLE
        # from every guard — the file APPLIED exit 0 (red-02.txt).
        d_pd = newdir(tmp, "phantom", ["0001_baseline.sql"], {
            "0002_smuggle.sql":
                "CREATE TABLE arv.victim (id INT, b$$c INT);\n"
                "DROP TABLE arv.victim;\n"
                "CREATE TABLE arv.wall (id INT, d$$e INT);\n",
        })
        db_pd = pg.create_scratch_db("s1_phantom")
        r_pd = run_migrate(db_pd, d_pd)
        pd_schema = sql(db_pd, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-026", r_pd.returncode != 0 and "ARV-MIG-003" in r_pd.stdout + r_pd.stderr
              and pd_schema == "0",
              "a '$' inside an unquoted identifier (b$$c) is identifier text, NOT a dollar-quote opener — the hidden DROP TABLE is REFUSED with ARV-MIG-003 pre-execution, the DB untouched (SEV-1)",
              "the mask must be identifier-aware (PG's own rule: $ does not open a dollar-quote when the previous char is an identifier char) — a phantom mask swallows executable text")
        pg.drop_scratch_db(db_pd)

        # SEV-1 Repro B (P0): the phantom hole hid a COMMIT — the arv.ghost table
        # PERSISTED at the predecessor while ARV-MIG-009 asserted 'the DB is
        # unchanged' (the §6.2 defect again, through the oracle's own scanner).
        d_pg3 = newdir(tmp, "ghost3", ["0001_baseline.sql"], {
            "0002_ghost3.sql":
                "CREATE TABLE IF NOT EXISTS arv.ghost3 (id INT);\n"
                "ALTER TABLE arv.ghost3 ADD COLUMN b$$c INT;\n"
                "COMMIT;\n"
                "SELECT 1/0;\n"
                "ALTER TABLE arv.ghost3 ADD COLUMN d$$e INT;\n",
        })
        db_pg3 = pg.create_scratch_db("s1_ghost3")
        r_pg3 = run_migrate(db_pg3, d_pg3)
        pg3_schema = sql(db_pg3, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-027", r_pg3.returncode != 0 and "ARV-MIG-011" in r_pg3.stdout + r_pg3.stderr
              and regclass(db_pg3, "arv.ghost3") == "" and pg3_schema == "0",
              "a COMMIT hidden behind a phantom dollar-quote is REFUSED with ARV-MIG-011 pre-execution — no persisted ghost, no false rollback claim, the DB untouched (SEV-1's §6.2 repro)",
              "the identifier-aware mask restores the ARV-MIG-011 guard's view of ALL executable transaction control")
        pg.drop_scratch_db(db_pg3)

        # SEV-2: 'ALTER TABLE IF EXISTS x DROP CONSTRAINT' evaded the destructive
        # guard at the predecessor (the single-\S+ object match missed IF EXISTS).
        d_dc = newdir(tmp, "dropcon", ["0001_baseline.sql"], {
            "0002_dc.sql": "CREATE TABLE arv.dc (id INT);\n"
                           "ALTER TABLE arv.dc ADD CONSTRAINT dc_pk PRIMARY KEY (id);\n",
            "0003_dropcon.sql": "ALTER TABLE IF EXISTS arv.dc DROP CONSTRAINT dc_pk;\n",
        })
        db_dc = pg.create_scratch_db("s1_dc")
        r_dc = run_migrate(db_dc, d_dc)
        dc_schema = sql(db_dc, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-028", r_dc.returncode != 0 and "ARV-MIG-003" in r_dc.stdout + r_dc.stderr
              and dc_schema == "0",
              "ALTER TABLE IF EXISTS ... DROP CONSTRAINT is REFUSED with ARV-MIG-003 without the directive (the IF EXISTS modifier no longer breaks the destructive match — SEV-2)",
              "the destructive ALTER branch must tolerate the IF EXISTS modifier between TABLE and the object name")
        pg.drop_scratch_db(db_dc)

        # SEV-3: a data-modifying CTE inside an admitted head (CTAS with
        # INSERT ... RETURNING) inserted a row at the predecessor with no
        # directive — the grammar's own 'schema, not queries' premise.
        d_ct = newdir(tmp, "ctas", ["0001_baseline.sql"], {
            "0002_base_t.sql": "CREATE TABLE arv.base_t (id INT);\n",
            "0003_ctas_insert.sql":
                "CREATE TABLE arv.seed AS WITH i AS (INSERT INTO arv.base_t VALUES (42) RETURNING *) SELECT * FROM i;\n",
        })
        db_ct = pg.create_scratch_db("s1_ctas")
        r_ct = run_migrate(db_ct, d_ct)
        ct_schema = sql(db_ct, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-029", r_ct.returncode != 0 and "ARV-MIG-015" in r_ct.stdout + r_ct.stderr
              and ct_schema == "0",
              "a data-modifying CTE inside an admitted head (CTAS with INSERT) is REFUSED with ARV-MIG-015 without the directive — zero effects (SEV-3)",
              "the grammar must inspect admitted heads' bodies for data-modifying statements — migrations declare schema, never queries")
        pg.drop_scratch_db(db_ct)

        # SEV-3 control: WITH the directive the same construct applies.
        d_ctd = newdir(tmp, "ctasd", ["0001_baseline.sql"], {
            "0002_base_t.sql": "CREATE TABLE arv.base_t (id INT);\n",
            "0003_ctas_declared.sql":
                "-- arv-baseline-bump: 1\n"
                "CREATE TABLE arv.seed AS WITH i AS (INSERT INTO arv.base_t VALUES (42) RETURNING *) SELECT * FROM i;\n",
        })
        db_ctd = pg.create_scratch_db("s1_ctasd")
        r_ctd = run_migrate(db_ctd, d_ctd)
        ct_rows = sql(db_ctd, "SELECT count(*) FROM arv.base_t;").stdout.strip()
        check("ARV-TEST-030", r_ctd.returncode == 0 and ct_rows == "1",
              "positive control: WITH the -- arv-baseline-bump directive the data-modifying CTE applies (the refusal gates, never blocks)",
              "the directive path is broken — the grammar's admission of declared data-modifying constructs")
        pg.drop_scratch_db(db_ctd)

        # SEV-4: an interior hole in the applied ledger (row 2 hand-deleted) let
        # the predecessor silently RE-APPLY 0002 out of order.
        d_hole = newdir(tmp, "lhole", ["0001_baseline.sql"], {
            "0002_h_a.sql": "CREATE TABLE IF NOT EXISTS arv.h_a (id INT);\n",
            "0003_h_b.sql": "CREATE TABLE IF NOT EXISTS arv.h_b (id INT);\n",
        })
        db_hole = pg.create_scratch_db("s1_lhole")
        run_migrate(db_hole, d_hole)
        sql(db_hole, "DELETE FROM arv.schema_migrations WHERE version=2;")
        r_hm = run_migrate(db_hole, d_hole)
        r_hv = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--verify"],
                              capture_output=True, text=True,
                              env=dict(os.environ, ARV_MIGRATIONS_DIR=d_hole, PGDATABASE=db_hole), timeout=120)
        check("ARV-TEST-031", r_hm.returncode != 0 and "ARV-MIG-012" in r_hm.stdout + r_hm.stderr
              and r_hv.returncode != 0 and "ARV-MIG-012" in r_hv.stdout + r_hv.stderr,
              "an INTERIOR HOLE in the applied ledger (a hand-deleted row leaving {1,3}) is REFUSED by BOTH migrate and verify with ARV-MIG-012 — never a silent out-of-order re-application (SEV-4)",
              "the applied set must be a contiguous prefix of the directory versions — a hole is a broken history, exactly like an extra row")
        pg.drop_scratch_db(db_hole)

        # SEV-5: an applied file RENAMED in place — the predecessor's migrate and
        # verify both passed silently while the ledger kept the old name forever.
        d_rn = newdir(tmp, "renamed", ["0001_baseline.sql"], {
            "0002_oldname.sql": "CREATE TABLE IF NOT EXISTS arv.rn_tab (id INT);\n",
        })
        db_rn = pg.create_scratch_db("s1_rn")
        run_migrate(db_rn, d_rn)
        os.rename(os.path.join(d_rn, "0002_oldname.sql"), os.path.join(d_rn, "0002_newname.sql"))
        r_rnm = run_migrate(db_rn, d_rn)
        r_rnv = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py"), "--verify"],
                               capture_output=True, text=True,
                               env=dict(os.environ, ARV_MIGRATIONS_DIR=d_rn, PGDATABASE=db_rn), timeout=120)
        check("ARV-TEST-032", r_rnm.returncode != 0 and "ARV-MIG-012" in r_rnm.stdout + r_rnm.stderr
              and r_rnv.returncode != 0 and "ARV-MIG-012" in r_rnv.stdout + r_rnv.stderr,
              "an applied file renamed in the directory (the ledger row still carries the old name) is REFUSED by BOTH migrate and verify with ARV-MIG-012 (SEV-5)",
              "the bidirectional check must compare NAMES, not only versions and checksums — 'every ledger row must correspond to a directory file' means the whole identity")
        pg.drop_scratch_db(db_rn)

        # SEV-8a: two-phase transaction control — PREPARE TRANSACTION reached psql
        # at the predecessor under the directive (a server refusal, not the
        # oracle's own boundary).
        d_pt = newdir(tmp, "prep", ["0001_baseline.sql"], {
            "0002_prep.sql": "-- arv-baseline-bump: 1\nPREPARE TRANSACTION 'x1';\n",
        })
        db_pt = pg.create_scratch_db("s1_prep")
        r_pt = run_migrate(db_pt, d_pt)
        check("ARV-TEST-033", r_pt.returncode != 0 and "ARV-MIG-011" in r_pt.stdout + r_pt.stderr
              and regclass(db_pt, "arv.schema_migrations") == "",
              "PREPARE TRANSACTION (two-phase commit control) is REFUSED with ARV-MIG-011 pre-execution — even under the directive, the runner owns the transaction boundary (SEV-8)",
              "transaction control includes the two-phase forms: PREPARE TRANSACTION / COMMIT PREPARED / ROLLBACK PREPARED join the refused token set")
        pg.drop_scratch_db(db_pt)

        # SEV-8b: CREATE INDEX CONCURRENTLY classifies 'admitted' but cannot run
        # inside the runner's single transaction — at the predecessor it reached
        # psql and died as ARV-MIG-009 with a misleading 'fix the SQL'.
        d_cc = newdir(tmp, "conc", ["0001_baseline.sql"], {
            "0002_conc.sql": "CREATE TABLE IF NOT EXISTS arv.conc_t (id INT);\n"
                             "CREATE INDEX CONCURRENTLY conc_idx ON arv.conc_t (id);\n",
        })
        db_cc = pg.create_scratch_db("s1_conc")
        r_cc = run_migrate(db_cc, d_cc)
        check("ARV-TEST-034", r_cc.returncode != 0 and "ARV-MIG-015" in r_cc.stdout + r_cc.stderr,
              "CREATE INDEX CONCURRENTLY is REFUSED by the admitted grammar with its named construct (it cannot run inside the runner's single transaction — never a misleading runtime 009)",
              "the grammar must name CONCURRENTLY as unclassified fail-closed, not admit it into a guaranteed psql failure")
        pg.drop_scratch_db(db_cc)

        # SEV-9a pin: the 0001_baseline exemption is NAME-SCOPED — the same DO
        # block named 0002_baseline must still refuse (a widened exemption would
        # fail this pin).
        d_ex2 = newdir(tmp, "exempt2", ["0001_baseline.sql"], {
            "0002_baseline.sql": "DO $do$ BEGIN NULL; END $do$;\n",
        })
        db_ex2 = pg.create_scratch_db("s1_exempt2")
        r_ex2 = run_migrate(db_ex2, d_ex2)
        check("ARV-TEST-035", r_ex2.returncode != 0 and "ARV-MIG-015" in r_ex2.stdout + r_ex2.stderr,
              "the bootstrap exemption is scoped to EXACTLY (version 1, name 'baseline') — the same DO block at 0002_baseline is REFUSED with ARV-MIG-015 (the exemption-scope pin, SEV-9a)",
              "the exemption is (v==1 and name=='baseline'), never a name-only or version-only match")
        pg.drop_scratch_db(db_ex2)

        # SEV-9c pin: the empty directory refuses with its named code (the card's
        # listed behavior, now permanently pinned).
        d_empty = os.path.join(tmp, "emptydir")
        os.makedirs(d_empty, exist_ok=True)
        db_em = pg.create_scratch_db("s1_empty")
        r_em = run_migrate(db_em, d_empty)
        em_schema = sql(db_em, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-036", r_em.returncode != 0 and "ARV-MIG-008" in r_em.stdout + r_em.stderr
              and em_schema == "0",
              "an empty migrations directory is REFUSED with ARV-MIG-008 and the DB untouched (the card's listed behavior, pinned — SEV-9c)",
              "S1 ships 0001_baseline.sql — the directory cannot be empty; the refusal precedes any DB touch")
        pg.drop_scratch_db(db_em)

        # SEV-6: the E-string escaped literal — a valid PostgreSQL file the
        # predecessor's mask FALSELY refused (ARV-MIG-016, the over-refusal
        # direction) because it did not know E'...' processes backslash escapes.
        d_es = newdir(tmp, "estr", ["0001_baseline.sql"], {
            "0002_estr.sql": "CREATE TABLE arv.estr (id INT, v TEXT DEFAULT E'a\\', ');\n",
        })
        db_es = pg.create_scratch_db("s1_estr")
        r_es = run_migrate(db_es, d_es)
        check("ARV-TEST-037", r_es.returncode == 0 and regclass(db_es, "arv.estr") == "arv.estr",
              "a valid E'...' escaped-string default APPLIES cleanly (E-strings process backslash escapes regardless of standard_conforming_strings — the mask knows the E-prefix rule; SEV-6)",
              "the mask must lex E'...' as an escaped string (the E-prefix rule: E immediately before the quote, not part of a longer identifier) — over-refusal of valid SQL is a defect too")
        pg.drop_scratch_db(db_es)

        # ------------------------------------------------------------------
        # P3-M0 acceptance — THE SEV RE-REVIEW ROUND (agent-ff3e3170 at 39a56e0):
        #   SEV-10 (P0) the astral-plane phantom — PG's scan.l is BYTE-oriented
        #   (\200-\377): every UTF-8 byte of an astral char (e.g. \U0001F600)
        #   CONTINUES an identifier, so 'c<emoji>$$' is ONE identifier to PG —
        #   the \uFFFF-capped mask dropped identifier context there and re-opened
        #   the SAME P0 one Unicode level up. RED-03 = these two cases at 39a56e0.
        # ------------------------------------------------------------------

        # SEV-10 Repro A (P0): the astral identifier hid an executable DROP TABLE
        # from every guard at 39a56e0 — the file APPLIED exit 0 (red-03.txt).
        d_as = newdir(tmp, "astral", ["0001_baseline.sql"], {
            "0002_smuggle_astral.sql":
                "CREATE TABLE arv.v2 (id INT, c\U0001F600$$ INT);\n"
                "DROP TABLE arv.v2;\n"
                "CREATE TABLE arv.w2 (id INT, d\U0001F600$$ INT);\n",
        })
        db_as = pg.create_scratch_db("s1_astral")
        r_as = run_migrate(db_as, d_as)
        as_schema = sql(db_as, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-038", r_as.returncode != 0 and "ARV-MIG-003" in r_as.stdout + r_as.stderr
              and as_schema == "0",
              "an ASTRAL-plane identifier char (PG's byte-oriented lexer: every high-bit byte continues an identifier) keeps identifier context through its '$$' — the hidden DROP TABLE is REFUSED with ARV-MIG-003 pre-execution, the DB untouched (SEV-10)",
              "the mask's identifier classes must cover ALL codepoints >= U+0080 (PG's scan.l rule is byte-based, never codepoint-capped at U+FFFF)")
        pg.drop_scratch_db(db_as)

        # SEV-10 Repro B (P0): the astral hole hid a COMMIT — the ghost table
        # PERSISTED at 39a56e0 while ARV-MIG-009 asserted 'the DB is unchanged'.
        d_ag = newdir(tmp, "astralghost", ["0001_baseline.sql"], {
            "0002_ghost_astral.sql":
                "CREATE TABLE IF NOT EXISTS arv.g4 (id INT);\n"
                "ALTER TABLE arv.g4 ADD COLUMN c\U0001F600$$ INT;\n"
                "COMMIT;\n"
                "SELECT 1/0;\n"
                "ALTER TABLE arv.g4 ADD COLUMN d\U0001F600$$ INT;\n",
        })
        db_ag = pg.create_scratch_db("s1_aghost")
        r_ag = run_migrate(db_ag, d_ag)
        ag_schema = sql(db_ag, "SELECT count(*) FROM information_schema.schemata WHERE schema_name='arv';").stdout.strip()
        check("ARV-TEST-039", r_ag.returncode != 0 and "ARV-MIG-011" in r_ag.stdout + r_ag.stderr
              and regclass(db_ag, "arv.g4") == "" and ag_schema == "0",
              "a COMMIT hidden behind an astral identifier's '$$' is REFUSED with ARV-MIG-011 pre-execution — no persisted g4, no false rollback claim, the DB untouched (SEV-10's §6.2 repro)",
              "byte-oriented identifier continuation: ALL codepoints >= U+0080 are identifier material to PG's lexer — the mask must agree exactly")
        pg.drop_scratch_db(db_ag)

    finally:
        pg.drop_scratch_db(test_db)
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILS:
        print(f"RED — {len(FAILS)} failure(s): {', '.join(FAILS)} — S1 + P3-M0 acceptance not met")
        return 1
    print("GREEN — S1 acceptance (a)-(e) + the P3-M0 migration-oracle acceptance (f)-(l) all observed on the real stack")
    return 0


if __name__ == "__main__":
    sys.exit(main())
