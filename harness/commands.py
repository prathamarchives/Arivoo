#!/usr/bin/env python3
"""harness/commands.py — the idempotent command path (S3; D-036; LAW-23's pattern early).

One command registry behind a CLI; every command is:
  * ATOMIC      — the effect (evidence row) and the idempotency record (command_log
                  row) commit in ONE transaction on ONE persistent psql session
  * IDEMPOTENT  — the replay check (key + body hash) runs BEFORE any insert on the
                  same session; a replay returns the recorded result; the composite
                  PK backstops races (a colliding insert = unique violation)
  * ACK-AFTER-COMMIT — the acknowledgment is emitted only after the COMMIT marker
                  is observed on the session's stdout (never speculatively)
  * OWNER-SCOPED — the session GUC app.current_owner scopes every statement (RLS)

Crash injection (harness/crash.py) rides the same driver: SIGKILL on the psql
session at after-begin / pre-commit / post-commit-pre-ack — connection loss makes
the server roll the open transaction back (the DB-side effect is exactly the app
process dying mid-transaction).

Every failure prints a named code + repair (diagnostics contract).
Exit 0 = acked; exit 1 = refused; exit 2 = crashed (no ack — by design).
"""
import argparse
import hashlib
import os
import queue
import signal
import subprocess
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg, clock, ids  # noqa: E402

MARK_CHECK = "MARK:CHECK"
MARK_BEGUN = "MARK:BEGUN"
MARK_INSERTS = "MARK:INSERTS_DONE"
MARK_COMMITTED = "MARK:COMMITTED"


def _q(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


class Session:
    """ONE persistent psql session (the command's transaction boundary; statements
    execute as they are fed — markers make execution observable).

    A dedicated reader thread drains stdout line-by-line into a queue (the pipe
    is small; an undrained pipe would eventually deadlock the server side), and
    read_until() consumes lines until the marker (psql flushes per statement —
    verified empirically, record 18 §4.3)."""

    def __init__(self, db: str, user: str, owner: str):
        self.proc = subprocess.Popen(
            ["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
             "-U", user, "-d", db],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
        self._lines: "queue.Queue[str | None]" = queue.Queue()
        self._reader = threading.Thread(target=self._drain, daemon=True)
        self._reader.start()
        self.send(f"SET app.current_owner={_q(owner)};")

    def _drain(self) -> None:
        for line in self.proc.stdout:
            self._lines.put(line.rstrip("\n"))
        self._lines.put(None)  # EOF

    def send(self, text: str) -> None:
        self.proc.stdin.write(text + "\n")
        self.proc.stdin.flush()

    def read_until(self, marker: str, timeout: float = 30.0) -> list:
        """Consume stdout lines until the marker appears."""
        lines: list[str] = []
        end = clock.mono() + timeout
        while clock.mono() < end:
            try:
                line = self._lines.get(timeout=0.2)
            except queue.Empty:
                continue
            if line is None:
                break
            lines.append(line)
            if marker in line:
                return lines
        raise TimeoutError(f"ARV-CMD-010: session marker {marker} not observed — psql stalled "
                           "(repair: the rig's DB must be reachable)")

    def kill(self) -> None:
        """kill -9 the session process (the crash injector's arm)."""
        try:
            os.kill(self.proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.proc.wait(timeout=10)

    def close(self) -> None:
        try:
            self.send("\\q")
        except (BrokenPipeError, ValueError, OSError):
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def record_event(*, db: str, owner: str, actor: str, client_id: str,
                 idem_key: str, payload: str, crash_at: str = None) -> int:
    """The first registered command: append one evidence event, exactly once.

    ONE session, phases in order (the crash points sit between them):
      SET owner -> replay check -> BEGIN; INSERT evidence; INSERT command_log;
      COMMIT -> ack.
    """
    body_hash = hashlib.sha256(f"record_event|{client_id}|{owner}|{actor}|{payload}".encode()).hexdigest()
    sess = Session(db, "arv_app", owner)
    try:
        # Phase 0: replay check (RLS scopes it to this owner's keyspace)
        sess.send(f"SELECT body_hash, result_ref FROM arv.command_log "
                  f"WHERE idempotency_key={_q(idem_key)};")
        sess.send(f"\\echo {MARK_CHECK}")
        lines = sess.read_until(MARK_CHECK)
        row = next((l for l in lines if "|" in l and "MARK" not in l), "")
        if row:
            recorded_hash, recorded_ref = row.split("|")
            if recorded_hash != body_hash:
                print(f"FAIL ARV-CMD-409: idempotency key {idem_key!r} is already recorded with a DIFFERENT body "
                      "(no silent overwrite — exactly-once is a contract, not a preference)")
                print("      repair: use a new idempotency key for a new body; the same key must mean the same command")
                return 1
            print(f"ACK command=record_event idem_key={idem_key} status=replayed result_ref={recorded_ref}")
            return 0

        # Phases 1..3: the transaction (effect + idempotency record, atomically)
        ev_id = ids.new_id()
        ts = clock.now()
        sess.send("BEGIN;")
        sess.send(f"\\echo {MARK_BEGUN}")
        sess.read_until(MARK_BEGUN)
        if crash_at == "after-begin":
            sess.kill()
            return 2  # crashed: no ack (nothing written yet)
        sess.send(f"INSERT INTO arv.evidence_event (id, event_type, payload, owner_scope, actor, run_id, input_hash, created_at) "
                  f"VALUES ({_q(ev_id)}, 'event', {_q(payload)}, {_q(owner)}, {_q(actor)}, {_q('run-' + client_id)}, {_q(body_hash[:16])}, {_q(ts)});")
        sess.send(f"INSERT INTO arv.command_log (owner_scope, idempotency_key, client_id, command_name, body_hash, result_ref, actor, created_at) "
                  f"VALUES ({_q(owner)}, {_q(idem_key)}, {_q(client_id)}, 'record_event', {_q(body_hash)}, {_q(ev_id)}, {_q(actor)}, {_q(ts)});")
        sess.send(f"\\echo {MARK_INSERTS}")
        sess.read_until(MARK_INSERTS)
        if crash_at == "pre-commit":
            sess.kill()
            return 2  # crashed: no ack (the open transaction rolls back with the connection)
        sess.send("COMMIT;")
        sess.send(f"\\echo {MARK_COMMITTED}")
        sess.read_until(MARK_COMMITTED)
        if crash_at == "post-commit-pre-ack":
            sess.kill()
            return 2  # crashed: committed, NO ack emitted — the re-run returns the recorded ack
        print(f"ACK command=record_event idem_key={idem_key} status=committed result_ref={ev_id}")
        return 0
    except TimeoutError as e:
        print(f"FAIL ARV-CMD-010: {e}")
        return 1
    finally:
        try:
            sess.close()
        except Exception:
            pass


REGISTRY = {"record_event": record_event}


def main() -> int:
    ap = argparse.ArgumentParser(description="the idempotent command path (S3)")
    ap.add_argument("command", choices=sorted(REGISTRY))
    ap.add_argument("--owner", required=True)
    ap.add_argument("--actor", default="owner",
                    choices=["owner", "runtime-agent", "worker", "model-decision"])
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--idem-key", required=True)
    ap.add_argument("--payload", required=True)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    return REGISTRY[a.command](db=db, owner=a.owner, actor=a.actor,
                               client_id=a.client_id, idem_key=a.idem_key, payload=a.payload)


if __name__ == "__main__":
    sys.exit(main())
