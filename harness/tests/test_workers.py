#!/usr/bin/env python3
"""harness/tests/test_workers.py — CLAIM-104: the durable-workers suite (WS9).

The §12.2 laws over migration 0022's machine, each probed on a REAL migrated
scratch db (the runbook's own named test paths)."""
import os, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from harness.adapters import ids

REPO = pathlib.Path(__file__).resolve().parents[2]
ENV = dict(os.environ)  # the runner env INHERITED (its PGHOST/PGPORT point at its own postgres)
ENV.setdefault("PGHOST", "127.0.0.1")
ENV.setdefault("PGUSER", "postgres")
ENV.setdefault("PGPORT", "5433")  # the local rig port; the CI runner's own PGPORT (5432) wins through inheritance
import pathlib as _pl
_pgbin = "/home/z/my-project/pgbuild/root/usr/lib/postgresql/17/bin"
if _pl.Path(_pgbin).exists():  # the sandbox's psql prepends only when present (portable)
    ENV["PATH"] = _pgbin + ":" + ENV.get("PATH", "")
    ENV["LD_LIBRARY_PATH"] = "/home/z/my-project/pgbuild/root/usr/lib/x86_64-linux-gnu:/home/z/my-project/pgbuild/root/usr/lib"
FAILS = []

def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok: FAILS.append(code)

def psql(db, sql, user="arv_app"):
    return subprocess.run(["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-h", ENV["PGHOST"], "-p", ENV["PGPORT"], "-U", user, "-d", db, "-c", sql],
                          capture_output=True, text=True, timeout=120, env=ENV)

def main() -> int:
    db = "arv_t104_" + ids.new_id().replace("-", "")[:8]
    psql("postgres", f"CREATE DATABASE {db}", user="postgres")
    r = subprocess.run(["python3", "harness/migrate.py"], cwd=str(REPO), capture_output=True,
                       text=True, timeout=300, env=dict(ENV, PGDATABASE=db, ARV_MIGRATIONS_DIR="harness/migrations"))
    try:
        check("WRK-01", r.returncode == 0, "the scratch db migrated through 0022")
        def enqueue(key, jtype="recovery_walk", payload="{}"):
            return psql(db, "SET app.current_owner='A'; INSERT INTO arv.job (id, owner_scope, job_type, "
                    f"payload_version, payload, idem_key, state, created_at, updated_at) VALUES "
                    f"(gen_random_uuid(), 'A', '{jtype}', 1, '{payload}', '{key}', 'queued', now(), now());")
        # WRK-02: the claim (SKIP LOCKED + the fencing token)
        enqueue("t1")
        r = psql(db, "SELECT fencing_token || '|' || attempts FROM arv.job_claim('w1', 5, 60);")
        check("WRK-02", r.returncode == 0 and r.stdout.strip().startswith("1|1"),
              "the claim leases with the monotonic fencing token (token=1, attempts=1)")
        # WRK-03: the fencing — a stale token cannot complete
        jid = psql(db, "SELECT id FROM arv.job LIMIT 1;", user="postgres").stdout.strip()
        r = psql(db, f"SELECT arv.job_complete('{jid}', 'w1', 999, 'succeeded', NULL);")
        check("WRK-03", "lost" in (r.stdout or ""), "the stale fencing token answers 'lost' (never a double-complete)")
        # WRK-04: the reclaim (the expired lease; the token increments)
        psql(db, "UPDATE arv.job SET lease_expires_at = now() - interval '1s';", user="postgres")
        r = psql(db, "SELECT fencing_token FROM arv.job_claim('w2', 5, 60);")
        check("WRK-04", r.stdout.strip().startswith("2"), "the expired lease is reclaimable (the token increments to 2)")
        # WRK-05: the stale holder (token 1) cannot complete after the reclaim
        r = psql(db, f"SELECT arv.job_complete('{jid}', 'w1', 1, 'succeeded', NULL);")
        check("WRK-05", "lost" in (r.stdout or ""),
              "the stale WORKER cannot complete the reclaimed job (§12.2's own letter)")
        # WRK-06: the rightful holder completes
        r = psql(db, f"SELECT arv.job_complete('{jid}', 'w2', 2, 'succeeded', NULL);")
        check("WRK-06", "ok" in (r.stdout or ""), "the rightful holder's fenced completion answers 'ok'")
        # WRK-07: the dedupe convergence
        r = enqueue("t1")
        check("WRK-07", r.returncode != 0 and "duplicate key" in (r.stderr or ""),
              "the duplicate submission converges (the UNIQUE refusal — one logical job)")
        # WRK-08: the poison guard (8 attempts -> dead)
        enqueue("t8")
        jid8 = psql(db, "SELECT id FROM arv.job WHERE idem_key='t8';", user="postgres").stdout.strip()
        st = ""
        for i in range(9):
            # the backoff clock elapses (the test-side simulation: available_after
            # passes before the next claim sees the row due again)
            psql(db, "UPDATE arv.job SET available_after = now() - interval '1s' WHERE id='" + jid8 + "';", user="postgres")
            psql(db, f"SELECT arv.job_claim('wp', 5, 1);")  # the 1s lease
            psql(db, "UPDATE arv.job SET lease_expires_at = now() - interval '2s' WHERE id='" + jid8 + "';", user="postgres")
            tok = psql(db, "SELECT fencing_token FROM arv.job WHERE id='" + jid8 + "';", user="postgres").stdout.strip()
            psql(db, f"SELECT arv.job_complete('{jid8}', 'wp', {tok}, 'retryable', 'the poison probe');")
            st = psql(db, "SELECT state FROM arv.job WHERE id='" + jid8 + "';", user="postgres").stdout.strip()
            if st == "dead":
                break
        check("WRK-08", st == "dead", "the poison job goes dead at the retry limit (the trigger's own path; never blocks the queue)")
        # WRK-09: one poison never blocks the next job
        enqueue("t9")
        r = psql(db, "SELECT count(*) FROM arv.job_claim('wn', 5, 60);")
        check("WRK-09", r.returncode == 0 and r.stdout.strip() not in ("", "0"),
              "the next job claims fine after the poison (the queue unblocked)")
        # WRK-10: the end-to-end loop (the worker over a real extract job)
        src = subprocess.run([sys.executable, "-I", str(REPO / "harness/commands.py"),
                              "import_source", "--owner", "A", "--client-id", "t104", "--idem-key", "t104-i",
                              "--title", "T104", "--file", "/tmp/w9.txt"],
                             capture_output=True, text=True, timeout=120, env=dict(ENV, PGDATABASE=db))
        sid = src.stdout.split("result_ref=")[1].split()[0] if src.returncode == 0 else ""
        check("WRK-10a", bool(sid), "the extract job's source imports")
        psql(db, "SET app.current_owner='A'; INSERT INTO arv.job (id, owner_scope, job_type, payload_version, "
                 f"payload, idem_key, state, created_at, updated_at) VALUES (gen_random_uuid(), 'A', "
                 f"'extract_source', 1, '{{\"source_id\": \"{sid}\"}}', 't104-e1', 'queued', now(), now());")
        w = subprocess.run([sys.executable, "-I", str(REPO / "harness/worker.py"),
                            "--name", "t104w", "--once"],
                           capture_output=True, text=True, timeout=300, env=dict(ENV, PGDATABASE=db))
        st = psql(db, "SELECT state FROM arv.job WHERE idem_key='t104-e1';", user="postgres").stdout.strip()
        gens = psql(db, "SELECT count(*) FROM arv.extraction_generation;", user="postgres").stdout.strip()
        check("WRK-10", w.returncode == 0 and st == "succeeded" and gens == "1"
              and "outcome=succeeded" in w.stdout and "fence=ok" in w.stdout,
              "the end-to-end loop: claim -> the SAME extract arm -> the fenced completion -> the generation")
    finally:
        psql("postgres", f"DROP DATABASE {db}", user="postgres")
    print()
    if FAILS:
        print("RED — the workers suite refuses:", ", ".join(FAILS)); return 1
    print("GREEN — the durable-workers suite (WRK-01..10) passes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
