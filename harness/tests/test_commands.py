#!/usr/bin/env python3
"""harness/tests/test_commands.py — S3 acceptance suite (Phase 2 Layer 2.1; D-036).

Red-first (LAW-11): committed BEFORE the implementation; the red run fails with
ARV-TEST-019 (waiting-for-harness: commands.py does not exist) — preserved in
record 18 §4.3.

S3 acceptance (the 2026-10-16 review §7, mapped to named codes):
  (a) replay the same command N times -> exactly ONE row; replays return the
      recorded result (idempotency key + transaction)                  ARV-TEST-020
  (b) same key + DIFFERENT body -> named conflict code ARV-CMD-409,
      no silent overwrite, no state change                            ARV-TEST-021
  (c) kill -9 at each injection point -> restart -> state equals the
      clean run (compared via the INDEPENDENT arv_read role)           ARV-TEST-022
  (d) acknowledgment never precedes commit: a post-commit-pre-ack crash
      leaves the row committed with NO ack emitted; the re-run returns
      the recorded ack (exactly-once)                                  ARV-TEST-023
  (e) cross-owner keyspaces are isolated (composite PK): owner B using
      owner A's key is NOT a conflict (different keyspace)             ARV-TEST-024
Run: python3 harness/tests/test_commands.py   (exit 0 = green)
"""
import os
import pathlib
import subprocess
import sys

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


try:
    from harness.adapters import pg  # noqa: E402
    from harness import commands  # noqa: E402
except ImportError as e:  # ARV-TEST-019
    print("FAIL ARV-TEST-019: the command path does not exist yet (waiting-for-harness) —", e)
    sys.exit(1)


def run_cli(*args) -> subprocess.CompletedProcess:
    """The command path AS THE CALLER SEES IT (a subprocess CLI — acks on stdout)."""
    cmd = [sys.executable, str(REPO / "harness" / "commands.py"), *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                          env=dict(os.environ, PGDATABASE=DB))


DB = None  # set in main()


def record(db: str, key: str, payload: str, owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(REPO / "harness" / "commands.py"), "record_event",
           "--owner", owner, "--actor", "owner", "--client-id", client,
           "--idem-key", key, "--payload", payload]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                          env=dict(os.environ, PGDATABASE=db))


def crash(db: str, point: str, key: str, payload: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(REPO / "harness" / "crash.py"), "--point", point,
           "--owner", "A", "--actor", "owner", "--client-id", "cli-crash",
           "--idem-key", key, "--payload", payload]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                          env=dict(os.environ, PGDATABASE=db))


def audit(db: str, query: str) -> str:
    """Independent state read (LAW-13): the arv_read role, direct psql."""
    r = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                        "-U", "arv_read", "-d", db, "-c", query],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def state_fingerprint(db: str) -> str:
    """Content-level state (the ids adapter's UUIDs are non-deterministic BY DESIGN;
    their correctness is asserted separately: 020 replays return the same ref, 023
    checks ack<->row correspondence). What must match after recovery: the evidence
    content and the command_log identity, nothing else."""
    import hashlib
    ev = audit(db, "SELECT owner_scope||'|'||payload FROM arv.evidence_event ORDER BY owner_scope, payload;")
    cl = audit(db, "SELECT idempotency_key||'|'||client_id||'|'||body_hash FROM arv.command_log ORDER BY idempotency_key;")
    return hashlib.sha256((ev + "||" + cl).encode()).hexdigest()[:24]


def main() -> int:
    global DB
    DB = pg.create_scratch_db("s3")
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=120,
                       env=dict(os.environ, PGDATABASE=DB), check=True)

        # (a) replay N times -> exactly one row; replays return the recorded result
        acks = [record(DB, "k-a", "hello") for _ in range(5)]
        ev = audit(DB, "SELECT count(*) FROM arv.evidence_event;")
        cl = audit(DB, "SELECT count(*) FROM arv.command_log;")
        committed = [a for a in acks if a.returncode == 0 and "status=committed" in a.stdout]
        replayed = [a for a in acks if a.returncode == 0 and "status=replayed" in a.stdout]
        refs = set(l.split("result_ref=")[1].split()[0] for a in acks
                   for l in a.stdout.splitlines() if "result_ref=" in l)
        check("ARV-TEST-020", ev == "1" and cl == "1" and len(committed) == 1 and len(replayed) == 4 and len(refs) == 1,
              f"5 replays -> exactly ONE evidence row ({ev}) + ONE command_log row ({cl}); 1 committed ack + 4 replayed acks, all the SAME result_ref ({len(refs)} distinct)",
              "the command must check the idempotency key BEFORE inserting and return the recorded result on replay — never insert twice (the composite PK backstops races)")

        # (b) same key + different body -> ARV-CMD-409, no state change
        before = state_fingerprint(DB)
        rb = record(DB, "k-a", "DIFFERENT-BODY")
        after = state_fingerprint(DB)
        check("ARV-TEST-021", rb.returncode != 0 and "ARV-CMD-409" in rb.stdout + rb.stderr and before == after,
              "same key + different body -> named conflict ARV-CMD-409, exit non-zero, state unchanged (no silent overwrite)",
              "compare the body hash against the recorded one and refuse with the named code — an overwrite would corrupt exactly-once")

        # (c) kill -9 at each injection point -> restart -> state equals the clean run
        for point in ("after-begin", "pre-commit", "post-commit-pre-ack"):
            dbp = pg.create_scratch_db(f"s3_{point.replace('-', '_')}")
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PGDATABASE=dbp), check=True)
            rc = crash(dbp, point, "k-crash", "payload-crash")
            ev_c = audit(dbp, "SELECT count(*) FROM arv.evidence_event;")
            # restart: re-run the command normally
            rr = record(dbp, "k-crash", "payload-crash", client="cli-crash")
            ev_r = audit(dbp, "SELECT count(*) FROM arv.evidence_event;")
            cl_r = audit(dbp, "SELECT count(*) FROM arv.command_log;")
            fp = state_fingerprint(dbp)
            # the clean reference run
            dbc = pg.create_scratch_db(f"s3_clean_{point.replace('-', '_')}")
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PGDATABASE=dbc), check=True)
            rclean = record(dbc, "k-crash", "payload-crash", client="cli-crash")
            fpc = state_fingerprint(dbc)
            if point == "post-commit-pre-ack":
                okp = (rc.returncode != 0 and "ACK" not in rc.stdout and ev_c == "1"
                       and rr.returncode == 0 and "status=replayed" in rr.stdout
                       and ev_r == "1" and cl_r == "1" and fp == fpc)
                what = (f"crash {point}: NO ack emitted, row already committed (ev={ev_c}); re-run -> replayed ack, "
                        f"state equals the clean run ({fp == fpc})")
            else:
                okp = (rc.returncode != 0 and "ACK" not in rc.stdout and ev_c == "0"
                       and rr.returncode == 0 and "status=committed" in rr.stdout
                       and ev_r == "1" and cl_r == "1" and fp == fpc)
                what = (f"crash {point}: transaction rolled back (ev={ev_c}), no ack; re-run -> committed, "
                        f"state equals the clean run ({fp == fpc})")
            check("ARV-TEST-022", okp, what,
                  "kill -9 at the point, then re-run: the recovered state must equal the clean run exactly (rollback or replay — never divergence, never duplicates)")
            pg.drop_scratch_db(dbp)
            pg.drop_scratch_db(dbc)

        # (d) explicit ordering proof: ack strictly after commit (post-commit-pre-ack left a
        #     committed row with no ack in (c); here: the normal path's ack only appears after
        #     the commit marker is observed — combined with (c)'s no-ack-without-commit)
        rnorm = record(DB, "k-d", "ordering")
        committed_row = audit(DB, f"SELECT result_ref FROM arv.command_log WHERE idempotency_key='k-d';")
        check("ARV-TEST-023", rnorm.returncode == 0 and "status=committed" in rnorm.stdout
              and f"result_ref={committed_row}" in rnorm.stdout.replace(" ", ""),
              "the normal path's ack carries the COMMITTED row's result_ref (printed only after the commit marker) — (c)'s crash arm proves the converse: no ack without commit",
              "the ack must be emitted strictly after COMMIT is confirmed — never speculatively")

        # (e) cross-owner keyspaces: owner B reuses owner A's key -> NOT a conflict
        rA = record(DB, "shared-key", "owner-A-body", owner="A", client="cli-A")
        rB = record(DB, "shared-key", "owner-B-body", owner="B", client="cli-B")
        ev_both = audit(DB, "SELECT count(*) FROM arv.evidence_event WHERE payload IN ('owner-A-body','owner-B-body');")
        check("ARV-TEST-024", rA.returncode == 0 and rB.returncode == 0 and ev_both == "2",
              "the same idempotency key in two owners' keyspaces is two independent commands (composite PK owner_scope+key) — no cross-owner coupling (LAW-22)",
              "the command_log PK must be (owner_scope, idempotency_key), never a global key — a global key would let one owner's key usage collide with another's")

    finally:
        pg.drop_scratch_db(DB)

    print()
    if FAILS:
        print(f"RED — {len(FAILS)} failure(s): {', '.join(FAILS)} — S3 acceptance not met")
        return 1
    print("GREEN — S3 acceptance (a)-(e) observed: idempotency, atomicity, crash recovery, ack ordering, owner-scoped keyspaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
