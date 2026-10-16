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
Run: python3 harness/tests/test_migrations.py   (exit 0 = green)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]

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

    finally:
        pg.drop_scratch_db(test_db)
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILS:
        print(f"RED — {len(FAILS)} failure(s): {', '.join(FAILS)} — S1 acceptance not met")
        return 1
    print("GREEN — S1 acceptance (a)-(e) + must-rejects all observed on the real stack")
    return 0


if __name__ == "__main__":
    sys.exit(main())
