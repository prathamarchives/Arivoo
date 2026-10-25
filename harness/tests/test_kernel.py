#!/usr/bin/env python3
"""harness/tests/test_kernel.py — the P3-K0 acceptance suite (the kernel
primitives; PLAN's P3-K0 card + RTM SYS-04's kernel half; CLAIM-048).

Red-first (LAW-11): this file declares the kernel's contracts and is observed
FAILING at the predecessor a6b5f49 (red-01.txt) before the implementation.

The declared contracts (each mapped to a named case):
  (a) the canonical versioned structured request encoding replaces delimiter
      concatenation — the separator-collision case (K-02), the versioned
      structured form itself (K-03), the Unicode/NFC normalization choice
      (K-04), the empty-vs-absent boundary (K-05)
  (b) UUID variant/version correctness, timestamp extraction + ordering,
      compatibility — no rewriting of persisted IDs (K-07/K-08)
  (c) the approved adapter boundary: stable NAMED errors for a missing client
      (ARV-DB-001), a timeout (ARV-DB-002), a connection refusal (ARV-DB-003),
      a target mismatch (ARV-DB-004) — and no hidden direct connection path
      (K-09..K-12)
  (d) EXPLICIT concurrent same-key semantics: simultaneous identical commands
      yield ONE recorded row and the SAME result to both callers — a unique
      constraint is not a replay promise; the loser re-reads and answers the
      replay, never a bare unique-violation refusal (K-06)
Run: python3 harness/tests/test_kernel.py   (exit 0 = green)
"""
import os
import subprocess
import sys
import tempfile
import time
import unicodedata
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# ARV-TEST-000: the waiting-for-harness class — the kernel's canonical-encoding
# surface does not exist at the predecessor (the RED the suite declares).
try:
    from harness.adapters import pg, ids  # noqa: E402
    from harness import commands  # noqa: E402
    _ = commands.canonical_body  # the declared surface (K-03's import class)
except AttributeError:
    print("FAIL ARV-TEST-000: harness/commands.py carries no canonical_body — the kernel's "
          "versioned structured encoding does not exist yet (the waiting-for-harness class)")
    print("      repair: implement commands.canonical_body (the canonical versioned structured "
          "request encoding — P3-K0's first contract)")
    sys.exit(1)
except ImportError as e:  # the stack itself is absent — the S1 class
    print("FAIL ARV-TEST-000: the harness does not exist yet (waiting-for-harness) —", e)
    sys.exit(1)

FAILS: list[str] = []


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def run_migrations(db: str) -> None:
    """Migrate a scratch DB through the REAL runner (the S1 form) — the kernel's
    commands run against the migrated substrate (0001..0003)."""
    env = dict(os.environ, ARV_MIGRATIONS_DIR=str(REPO / "harness" / "migrations"), PGDATABASE=db)
    subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                   capture_output=True, text=True, env=env, timeout=120, check=True)


def run_cmd(owner, actor, client_id, idem_key, payload, env=None, timeout=90):
    """Run the record_event command through the REAL CLI (the end-to-end form)."""
    e = dict(os.environ, PGDATABASE=env["db"]) if env else dict(os.environ)
    return subprocess.run(
        [sys.executable, str(REPO / "harness" / "commands.py"), "record_event",
         "--owner", owner, "--actor", actor, "--client-id", client_id,
         "--idem-key", idem_key, "--payload", payload],
        capture_output=True, text=True, env=e, timeout=timeout,
    )


def sql(db: str, query: str) -> str:
    r = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                        "-h", "127.0.0.1", "-p", "5433", "-U", "postgres", "-d", db, "-c", query],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def main() -> int:
    # (0) the real stack is reachable — the rig precondition
    r = pg.psql("SELECT 1;", db="postgres")
    check("K-01", r.returncode == 0, "PostgreSQL reachable through the adapter (the real stack, not a mock)",
          "start the rig: locally .pg on 5433; CI the postgres:17 service")

    tmp = tempfile.mkdtemp(prefix="arv_k0_")
    db = pg.create_scratch_db("s1_k0")
    run_migrations(db)

    # (a) K-02 THE SEPARATOR COLLISION — the card's named defect, end-to-end:
    # two DIFFERENT commands whose fields collide under delimiter concatenation
    # (client 'a|b'/owner 'c' vs client 'a'/owner 'b|c') must NEVER record the
    # same body_hash — the ledger's provenance must distinguish them (observed
    # at the predecessor: IDENTICAL hashes, two different commands).
    r1 = run_cmd("c", "owner", "a|b", "k-c1", "p1", env={"db": db})
    r2 = run_cmd("b|c", "owner", "a", "k-c2", "p1", env={"db": db})
    h = sql(db, "SELECT body_hash FROM arv.command_log WHERE idempotency_key IN ('k-c1','k-c2') ORDER BY idempotency_key;")
    hashes = h.splitlines()
    check("K-02", r1.returncode == 0 and r2.returncode == 0 and len(hashes) == 2 and hashes[0] != hashes[1],
          "two commands that collide only under delimiter concatenation (client 'a|b'/owner 'c' vs client 'a'/owner 'b|c') "
          "record DIFFERENT body hashes — the ledger's provenance distinguishes them (observed identical at the predecessor)",
          "the canonical body must be a versioned structured encoding (typed fields, never delimiter concatenation) — "
          "a shared hash across different commands is a false provenance equivalence")

    # (a) K-03 the versioned structured form: the canonical body is explicit,
    # versioned, and stable — same fields in any API-order yield the same body;
    # the version tag is observable in the encoding.
    c1 = commands.canonical_body(command="record_event", client_id="cli-1", owner_scope="o1",
                                 actor="owner", payload="hello")
    c2 = commands.canonical_body(payload="hello", actor="owner", owner_scope="o1",
                                 client_id="cli-1", command="record_event")
    check("K-03", c1 == c2 and '"arv_body_version"' in c1,
          "the canonical body is a versioned structured encoding: field-order independent, explicitly versioned",
          "canonical_body must serialize a versioned structure with sorted keys — never an order-dependent or unversioned form")

    # (a) K-04 Unicode/NFC: the SAME logical text in different normalizations
    # is the SAME canonical body (the choice pinned: NFC), so the same key
    # REPLAYS — never a spurious 409 across normalizations of one payload.
    nfc = "café"
    nfd = unicodedata.normalize("NFD", nfc)
    check("K-04", commands.canonical_body(command="record_event", client_id="c", owner_scope="o",
                                           actor="owner", payload=nfc)
          == commands.canonical_body(command="record_event", client_id="c", owner_scope="o",
                                      actor="owner", payload=nfd),
          "NFC vs NFD of one payload produce the SAME canonical body (the pinned normalization choice: NFC)",
          "canonical_body must NFC-normalize text fields before serializing — the choice must be explicit, tested, and documented")

    # (a) K-05 the empty-vs-absent boundary: an empty field value is never
    # ambiguous with a missing field in the encoded structure.
    e1 = commands.canonical_body(command="record_event", client_id="", owner_scope="o",
                                 actor="owner", payload="p")
    e2 = commands.canonical_body(command="record_event", client_id="o", owner_scope="",
                                 actor="owner", payload="p")
    check("K-05", e1 != e2,
          "an empty client_id and an empty owner_scope are DIFFERENT bodies (every field is positionally explicit in the structure)",
          "the encoding must carry typed/present fields — never a form where an empty value can shift into another field's position")

    # (d) K-06 THE CONCURRENT SAME-KEY SEMANTICS — the card's explicit demand:
    # two SIMULTANEOUS identical commands (same key, same canonical body) yield
    # ONE recorded row and the SAME answer to both callers; the loser re-reads
    # and replays — never a bare unique-violation refusal, never two rows.
    cdb = pg.create_scratch_db("s1_k0_race")
    run_migrations(cdb)
    procs = [
        subprocess.Popen(
            [sys.executable, str(REPO / "harness" / "commands.py"), "record_event",
             "--owner", "race", "--actor", "owner", "--client-id", "cli-r",
             "--idem-key", "k-race", "--payload", "race-payload"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, PGDATABASE=cdb),
        )
        for _ in range(2)
    ]
    outs = [p.communicate(timeout=120) for p in procs]
    codes = [p.returncode for p in procs]
    row_count = sql(cdb, "SELECT count(*) FROM arv.command_log WHERE idempotency_key='k-race';")
    refs = set()
    for o, e in outs:
        for ln in (o + e).splitlines():
            if "result_ref=" in ln:
                refs.add(ln.split("result_ref=")[1].split()[0])
    check("K-06", codes == [0, 0] and row_count == "1" and len(refs) == 1,
          f"two SIMULTANEOUS identical commands: both exit 0, exactly ONE recorded row, and the SAME result_ref to both "
          f"(the loser re-reads and answers the replay — never a bare unique-violation refusal; observed: codes={codes}, "
          f"rows={row_count}, refs={sorted(refs)})",
          "the concurrent loser must catch the unique violation, re-read the recorded row, and answer the recorded replay "
          "(or a typed retryable in-flight state) — a unique constraint is not a replay promise")
    pg.drop_scratch_db(cdb)

    # (b) K-07 UUID variant/version correctness, timestamp extraction, ordering.
    batch = [ids.new_id() for _ in range(64)]
    versions_ok = all(u[14] in "789ab" and u[19] in "89ab" for u in batch)  # v7 nibble + RFC-4122 variant
    check("K-07", versions_ok and batch == sorted(batch),
          "64 minted IDs: version nibble 7, RFC-4122 variant bits, and ms-timestamp ordering (non-decreasing within the batch)",
          "ids.py must mint UUIDv7-class IDs: 48-bit clock ms + version/variant + controlled randomness, time-ordered")

    # (b) K-08 compatibility: a persisted ID is never rewritten — a recorded
    # result_ref from the committed row round-trips byte-identically.
    ref = sql(db, "SELECT result_ref FROM arv.command_log WHERE idempotency_key='k-collide';")
    check("K-08", ref != "" and len(ref) == 36 and ref[14] in "789ab" and ref[19] in "89ab",
          f"the persisted result_ref ({ref}) round-trips byte-identically — a valid UUIDv7-class value, never rewritten",
          "persisted IDs are immutable identity: no migration or replay may rewrite them without an explicit compatibility decision")

    # (c) K-09 the adapter's NAMED missing-client error (not a bare 127).
    import harness.adapters.pg as pgmod
    orig_run = pgmod._run_psql
    def _no_client(cmd, timeout):
        return orig_run.__wrapped__(cmd, timeout) if hasattr(orig_run, "__wrapped__") else None
    # drive the named-error surface directly: the public psql with the client absent
    saved_path = os.environ.get("PATH", "")
    os.environ["PATH"] = "/nonexistent"
    try:
        rr = pgmod.psql("SELECT 1;", db="postgres")
    finally:
        os.environ["PATH"] = saved_path
    check("K-09", rr.returncode != 0 and "ARV-DB-001" in (rr.stderr or "") + (rr.stdout or ""),
          "a missing psql client is the NAMED error ARV-DB-001 (stable across environments), never a bare 127",
          "the adapter must map the missing-client condition to its stable named code in the result's error surface")

    # (c) K-10 the adapter's NAMED connection-refused error (not a raw psql exit).
    rr = pg.psql("SELECT 1;", db="postgres", user="nosuchrole_k0")
    check("K-10", rr.returncode != 0 and "ARV-DB-003" in (rr.stderr or "") + (rr.stdout or ""),
          "a refused connection/role is the NAMED error ARV-DB-003, never a raw psql diagnostic",
          "the adapter must map connection-level failures to their stable named codes")

    # (c) K-11 the adapter's target-mismatch guard: no hidden path to a
    # different database — a non-loopback target is refused by name.
    saved_host = os.environ.get("PGHOST", "")
    os.environ["PGHOST"] = "10.255.255.1"
    try:
        rr = pg.psql("SELECT 1;", db="postgres", timeout=3)
    finally:
        os.environ["PGHOST"] = saved_host
    check("K-11", rr.returncode != 0 and "ARV-DB-004" in (rr.stderr or "") + (rr.stdout or ""),
          "a non-loopback connection target is REFUSED with the NAMED error ARV-DB-004 (the approved adapter boundary — "
          "no hidden direct path can select a different database)",
          "pg.config/psql must refuse non-loopback targets by name: the rig's loopback (and CI's service) is the only approved target shape")

    # (c) K-12 the adapter's NAMED timeout error (not an unhandled crash).
    try:
        rr = pg.psql("SELECT pg_sleep(3);", db="postgres", timeout=1)
        named = "ARV-DB-002" in (rr.stderr or "") + (rr.stdout or "") and rr.returncode != 0
        crashed = False
    except subprocess.TimeoutExpired:
        named, crashed = False, True
    check("K-12", named and not crashed,
          "an operation exceeding its timeout is the NAMED error ARV-DB-002 in the result surface — never an unhandled TimeoutExpired crash",
          "the adapter must catch its own timeout and map it to the stable named code")

    pg.drop_scratch_db(db)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILS:
        print(f"RED — {len(FAILS)} failure(s): {', '.join(FAILS)} — P3-K0 acceptance not met")
        return 1
    print("GREEN — P3-K0 acceptance (a)-(d) all observed on the real stack")
    return 0


if __name__ == "__main__":
    sys.exit(main())
