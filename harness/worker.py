#!/usr/bin/env python3
"""harness/worker.py — the durable worker (CLAIM-104; runbook §12.4; the
directive's Workstream 9).

The private worker loop over migration 0022's job machine:
  * poll   — arv.job_claim (SKIP LOCKED; the expired lease reclaimable; the
             fencing token granted per acquisition)
  * run    — the job type's executor: the SAME kernel commands through the
             bounded subprocess (extract_source -> harness/extract.py;
             rebuild_keyword_index/recovery_walk/rebuild_derived -> the
             kernel arms) — never a second domain model
  * fence  — arv.job_complete carries the token; 'lost' means the lease was
             reclaimed: the worker OBSERVES the loss and moves on (never a
             double-complete); a refused/failed execution is 'retryable'
             with the named typed error (the poison guard turns 8 attempts
             dead — one poison job never blocks the queue)

The identity: the worker runs as arv_app with the transaction-local owner
scope set FROM THE JOB ROW (never a global claim); the log surfaces job ids
and codes only — never source contents, never secrets (§12.4's law).

Usage: python3 harness/worker.py --name w1 [--once] [--poll-seconds 2]
Environment: PGDATABASE (the service's runtime db; the adapter's boundary).
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg, clock  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]

# the job types -> the executor argv (the kernel's own arms; §12.3's initial
# set — extract, rebuild index, recover interrupted imports, rebuild derived)
EXECUTORS = {
    "extract_source": lambda p: [sys.executable, str(REPO / "harness" / "extract.py"),
                                 "--owner", p["owner"], "--actor", "worker",
                                 "--client-id", "worker-" + p["worker"],
                                 "--idem-key", p["idem_key"], "--source-id", p["source_id"]],
    "rebuild_keyword_index": lambda p: [sys.executable, str(REPO / "harness" / "commands.py"),
                                        "rebuild_keyword_index",
                                        "--owner", p["owner"], "--actor", "worker",
                                        "--client-id", "worker-" + p["worker"],
                                        "--idem-key", p["idem_key"]],
    "recovery_walk": lambda p: [sys.executable, str(REPO / "harness" / "recover.py"),
                                "walk", "--owner", p["owner"]],
    "rebuild_derived": lambda p: [sys.executable, str(REPO / "harness" / "commands.py"),
                                  "rebuild_keyword_index",
                                  "--owner", p["owner"], "--actor", "worker",
                                  "--client-id", "worker-" + p["worker"],
                                  "--idem-key", p["idem_key"]],
}
JOB_TIMEOUT = 600  # the execution bound (the extract arm's own generous bound)


def _q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def claim(db: str, worker: str, limit: int, lease_seconds: int) -> list:
    """One claim: the due rows (SKIP LOCKED) -> the leased list."""
    # the ROW form with the explicit column separator (the tuple rendering's
    # commas are ambiguous inside the JSONB payload — the pipe is not)
    r = pg.psql("SELECT id::text || '|' || owner_scope || '|' || job_type || '|' || "
                "fencing_token || '|' || attempts || '|' || replace(coalesce(payload::text, '{}'), '|', '\\u007c') "
                f"FROM arv.job_claim({_q(worker)}, {int(limit)}, {int(lease_seconds)});",
                db=db, user="arv_app")
    if r.returncode != 0:
        return []
    rows = []
    for ln in (r.stdout or "").splitlines():
        parts = ln.split("|", 5)
        if len(parts) == 6:
            rows.append({"id": parts[0], "owner": parts[1], "job_type": parts[2],
                         "token": int(parts[3]), "attempts": int(parts[4]),
                         "payload": parts[5].replace("\\u007c", "|"), "worker": worker})
    return rows


def execute(job: dict, db: str) -> "tuple[str, str]":
    """Run one job's executor: (outcome, typed_error). The named kernel
    refusals stay retryable (the outage/validation classes); a timeout is
    retryable (the honest unknown — the next attempt re-runs the SAME
    idempotent command by its key); only the executor's own typed refusal
    of an unrunnable payload is dead (it will never run)."""
    try:
        payload = dict(json.loads(job["payload"]))
        payload.update(owner=job["owner"], worker=job["worker"],
                       idem_key=job["id"][:8] + "-" + str(job["token"]))
        argv = EXECUTORS[job["job_type"]](payload)
    except (KeyError, TypeError, ValueError) as e:
        return "dead", f"ARV-JOB-003: the payload is unrunnable — {type(e).__name__}"
    env = dict(os.environ)
    env["PGDATABASE"] = db
    # the transaction-local owner scope: the child kernel sets its own session
    # scope from --owner (the argv contract); the worker never holds a global one
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=JOB_TIMEOUT,
                           cwd=str(REPO), env=env)
    except subprocess.TimeoutExpired:
        return "retryable", "ARV-JOB-004: the execution exceeded its bound — the " \
                            "same-key re-run resolves the outcome"
    if r.returncode == 0:
        return "succeeded", ""
    err = next((ln for ln in (r.stdout or "").splitlines()
                if ln.startswith("FAIL ")), (r.stderr or "")[:160])
    # the named ARV-CMD-409 (the body conflict) is TERMINAL for the job: the
    # same key means a different body — re-running cannot converge
    if "ARV-CMD-409" in (r.stdout or ""):
        return "dead", err[:512]
    return "retryable", err[:512]


def complete(db: str, job: dict, outcome: str, typed_error: str) -> str:
    """The fenced completion: 'ok' | 'lost' (the lease reclaimed)."""
    r = pg.psql("SELECT arv.job_complete("
                + _q(job["id"]) + "::uuid, " + _q(job["worker"]) + ", "
                + str(int(job["token"])) + ", " + _q(outcome) + ", "
                + _q(typed_error) + ");", db=db, user="arv_app")
    if r.returncode != 0:
        return "lost"
    return (r.stdout or "").strip().split("\n")[-1].strip()


def loop(db: str, worker: str, once: bool, poll_seconds: float) -> int:
    """The worker loop: claim -> execute -> fence. Exit 0 on --once (the
    batch completes); the persistent form polls forever (the service's
    supervisor owns the restart)."""
    processed = 0
    while True:
        jobs = claim(db, worker, limit=5, lease_seconds=120)
        if not jobs:
            if once:
                break
            time.sleep(max(0.5, poll_seconds))
            continue
        for job in jobs:
            outcome, typed_error = execute(job, db)
            res = complete(db, job, outcome, typed_error)
            state_note = "ok" if res == "ok" else "lost (the lease was reclaimed)"
            print(f"JOB id={job['id'][:12]} type={job['job_type']} "
                  f"attempt={job['attempts']} outcome={outcome} fence={state_note} "
                  f"error={typed_error[:80] if typed_error else '-'}",
                  flush=True)
            processed += 1
    print(f"WORKER-DONE name={worker} processed={processed}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the durable worker (runbook §12.4)")
    ap.add_argument("--name", required=True, help="the worker identity (the lease owner)")
    ap.add_argument("--once", action="store_true",
                    help="one batch then exit (the bounded form; the service form polls)")
    ap.add_argument("--poll-seconds", type=float, default=2.0)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    return loop(db, a.name, a.once, a.poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
