#!/usr/bin/env python3
"""harness/migrate.py — the forward-only migrations runner (S1; D-036; R4/R7).

Contract (the 2026-10-16 review §7 S1, made mechanical):
  * forward-only: no down/rollback exists by design (history is append-only)
  * versioned:    NNNN_name.sql, strictly increasing, unique versions
  * baseline:     the version set must start at 0001 — a hole below the applied
                  head is refused (ARV-MIG-004), an applied file edited after
                  apply is refused (ARV-MIG-005), a destructive statement without
                  "-- arv-baseline-bump:" is refused (ARV-MIG-003)
  * re-runnable:  applying nothing new is a no-op exit 0 (ARV-MIG-001 reports it);
                  the bookkeeping row for a fully-applied, unchanged set is NEVER
                  rewritten (double application is structurally impossible: each
                  file applies inside ONE transaction together with its row)
  * atomic:       file + bookkeeping row commit together or not at all
  * verifiable:   --verify re-checks every recorded checksum against the files

Every failure prints: rule ID, what, repair (diagnostics contract).
Exit 0 = ok; exit 1 = refusal/failure.
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg  # noqa: E402

FILE_RE = re.compile(r"^(\d{4})_(.+)\.sql$")
DESTRUCTIVE_RE = re.compile(
    r"(?is)\b(DROP\s+TABLE|DROP\s+COLUMN|DROP\s+SCHEMA|TRUNCATE|ALTER\s+TABLE\s+\S+\s+DROP|DELETE\s+FROM)\b"
)
BUMP_RE = re.compile(r"(?m)^\s*--\s*arv-baseline-bump:\s*(\d+)")


def _die(code: str, what: str, repair: str) -> "None":
    print(f"FAIL {code}: {what}")
    print(f"      repair: {repair}")
    sys.exit(1)


def _fail(code: str, what: str, repair: str) -> tuple:
    print(f"FAIL {code}: {what}")
    print(f"      repair: {repair}")
    return None, code


def discover(mdir: str) -> list:
    out = []
    for name in sorted(os.listdir(mdir)):
        m = FILE_RE.match(name)
        if not m:
            _die("ARV-MIG-006", f"unparsable migration filename: {name}",
                 "migration files are NNNN_name.sql with a 4-digit zero-padded version")
        out.append((int(m.group(1)), m.group(2), os.path.join(mdir, name)))
    return out


def applied(db: str) -> dict:
    pg.psql(
        "CREATE SCHEMA IF NOT EXISTS arv; "
        "CREATE TABLE IF NOT EXISTS arv.schema_migrations ("
        "version BIGINT PRIMARY KEY, name TEXT NOT NULL, checksum TEXT NOT NULL, "
        "applied_at TIMESTAMPTZ NOT NULL DEFAULT now(), applied_by TEXT NOT NULL);",
        db=db,
    )
    r = pg.psql("SELECT version, checksum FROM arv.schema_migrations ORDER BY version;", db=db)
    if r.returncode != 0:
        _die("ARV-MIG-007", "cannot read the migrations bookkeeping table",
             f"the rig's DB must be reachable and arv.schema_migrations readable: {r.stderr.strip()[:200]}")
    rows = {}
    for line in r.out.splitlines():
        parts = line.split("|")
        if len(parts) == 2:
            rows[int(parts[0])] = parts[1]
    return rows


def run(db: str, mdir: str) -> int:
    files = discover(mdir)
    if not files:
        _die("ARV-MIG-008", f"no migrations found in {mdir}", "S1 ships 0001_baseline.sql — the directory cannot be empty")
    versions = [v for v, _, _ in files]
    if versions[0] != 1 or versions != list(range(1, len(versions) + 1)):
        _die("ARV-MIG-004", f"the version set is not a gapless sequence from the baseline: {versions}",
             "migrations are forward-only from 0001; renumber the directory (no holes, no recycling)")
    done = applied(db)
    for v, name, path in files:
        blob = open(path, "rb").read()
        digest = hashlib.sha256(blob).hexdigest()
        if v in done:
            if done[v] != digest:
                _die("ARV-MIG-005", f"applied migration {v:04d}_{name} was EDITED after apply (recorded checksum differs)",
                     "an applied migration is immutable history — revert the file edit or add a new migration")
            continue  # already applied, unchanged: the no-op path
        text = blob.decode("utf-8", "replace")
        if DESTRUCTIVE_RE.search(text) and not BUMP_RE.search(text):
            _die("ARV-MIG-003", f"migration {v:04d}_{name} contains a destructive statement without an explicit baseline bump",
                 "destructive operations require a '-- arv-baseline-bump: <n>' directive line in the file (the owner-visible paper trail)")
        # ONE transaction: the migration AND its bookkeeping row commit together.
        # (The -c argument travels via subprocess argv — no shell, no quoting layer.)
        sql = text
        stmt = (
            "BEGIN;\n" + sql +
            f"\nINSERT INTO arv.schema_migrations (version, name, checksum, applied_by) "
            f"VALUES ({v}, '{name}', '{digest}', 'harness/migrate.py');\nCOMMIT;"
        )
        r = pg.psql(stmt, db=db)
        if r.returncode != 0:
            _die("ARV-MIG-009", f"migration {v:04d}_{name} failed and was rolled back",
                 f"fix the SQL; the DB is unchanged (transaction proof): {r.stderr.strip()[:300]}")
        print(f"applied {v:04d}_{name}")
    return 0


def verify(db: str, mdir: str) -> int:
    files = discover(mdir)
    done = applied(db)
    bad = []
    for v, name, path in files:
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if v not in done:
            bad.append(f"{v:04d}_{name}: not applied")
        elif done[v] != digest:
            bad.append(f"{v:04d}_{name}: checksum drift (edited after apply)")
    if bad:
        _die("ARV-MIG-010", f"verify failed: {'; '.join(bad)}", "run migrate; never edit an applied file (ARV-MIG-005)")
    print(f"verify OK: {len(files)} migration(s) applied, checksums match")
    return 0


def main() -> int:
    cfg = pg.config()
    db = os.environ.get("PGDATABASE", "postgres")
    mdir = cfg["ARV_MIGRATIONS_DIR"]
    if "--verify" in sys.argv:
        return verify(db, mdir)
    pre = len(applied(db))
    rc = run(db, mdir)
    if rc == 0:
        post = len(applied(db))
        if post == pre:
            print("ARV-MIG-001: nothing to apply — no-op (all recorded, unchanged)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
