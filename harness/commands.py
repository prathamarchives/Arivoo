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
import json
import os
import pathlib
import queue
import re
import signal
import subprocess
import sys
import threading
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg, clock, ids, blob  # noqa: E402
from harness.formats import _FmtRefusal, check_registered, decode, read_text  # noqa: E402  # P4-A slice one: the format adapter registry — ONE home (formats.py), the import boundary the only caller; P4-A slice three (CLAIM-067): read_text — the ONE home for 'the readable text of a stored source' (the derived view feeds extraction, the keyword index, and the offset validations)

MARK_CHECK = "MARK:CHECK"
MARK_BEGUN = "MARK:BEGUN"
MARK_INSERTS = "MARK:INSERTS_DONE"
MARK_COMMITTED = "MARK:COMMITTED"

# P4-00b (CLAIM-063): the client/API version field — ONE home for the frozen
# contract's version token. Every write ack carries `api_version={API_VERSION}`
# and every read surface reports the same value (query.py/extract.py import
# THIS constant — one fact, one home). The version changes only through the
# boundary contract's own change process (PLAN's P4-00b card; RTM §5).
API_VERSION = 1

# P3-08 (CLAIM-059): the OUTBOX-CARRYING command set — the durable-capture
# product families whose committed local writes carry sync intent (RTM §4.2:
# the effect rows + the command-log row + the outbox row in ONE transaction).
# record_event (the kernel's own evidence surface) and rebuild_keyword_index
# (the derived layer — the server re-derives its own, P3-09's contract) stay
# OUT: their server-side story is not a delivery. The spine enqueues the
# CLIENT outbox row on the local site and the SERVER outbox handoff row on
# the server site (ARV_SITE=server — the D-018 separation: one command core,
# two execution sites, two outboxes, never one mixed surface).
_SYNC_COMMANDS = ("import_source", "create_highlight", "revise_highlight",
                  "tombstone_highlight", "restore_highlight", "create_bookmark",
                  "move_bookmark", "tombstone_bookmark", "restore_bookmark",
                  "create_note", "revise_note", "tombstone_note", "restore_note",
                  "save_position", "record_session", "journal_block",
                  "revise_journal_block", "create_reading_list", "add_to_list",
                  "remove_from_list")
# P4-C slice four (CLAIM-073; the LAW-05 split's named re-home — the enqueue
# and the delivery landing TOGETHER, never the enqueue-without-delivery
# dead-letter window the CLAIM-066/071 SEV rounds established law for): the
# journal family joins the outbox-carrying set — the writing lab's
# no-lost-writes law completes with sync.py's _cli_args journal branches.
# P4-C slice five (CLAIM-074): the reading-list family rides the SAME law —
# the enqueue and the delivery in one slice (the SYN-22 pin's own letter)


def _q(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def _qn(s: "str | None") -> str:
    """The journal's nullable fields (work_id XOR title): a real NULL for None — the
    re-drive's JSON round-trip depends on it (never the string 'None')."""
    return _q(s) if s is not None else "NULL"


class Session:
    """ONE persistent psql session (the command's transaction boundary; statements
    execute as they are fed — markers make execution observable).

    A dedicated reader thread drains stdout line-by-line into a queue (the pipe
    is small; an undrained pipe would eventually deadlock the server side),
    read_until() consumes lines until the marker (psql flushes per statement —
    verified empirically, record 18 §4.3), and a SECOND pump drains stderr into
    a buffer from construction (SEV-7's refinement, P3-02: the death classifier
    reads the OBSERVED drained cause — never the poll()-inferred guess, never
    a lagging read that lost the duplicate-key line)."""

    def __init__(self, db: str, user: str, owner: str):
        cfg = pg.config()
        if cfg["PGHOST"] not in pg.LOOPBACK:  # the same approved-boundary guard as pg.psql (the #83 round)
            raise RuntimeError("ARV-DB-004: the configured target is outside the approved adapter boundary "
                               "(loopback only) — the command session refuses, never a hidden path")
        self.proc = subprocess.Popen(
            ["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
             "-U", user, "-d", db],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
        self._lines: "queue.Queue[str | None]" = queue.Queue()
        self._eof = False
        self._err: list[str] = []
        self._reader = threading.Thread(target=self._drain, daemon=True)
        self._reader.start()
        self._errpump = threading.Thread(target=self._drain_err, daemon=True)
        self._errpump.start()
        self.send(f"SET app.current_owner={_q(owner)};")

    def _drain(self) -> None:
        for line in self.proc.stdout:
            self._lines.put(line.rstrip("\n"))
        self._eof = True
        self._lines.put(None)  # EOF

    def _drain_err(self) -> None:
        for line in self.proc.stderr:
            self._err.append(line)
        # stderr EOF: the pump ends — everything the process ever said is in _err

    def dead_reason(self) -> "str | None":
        """The DRAINED stderr cause of a DEAD session, or None when it is alive
        (SEV-7: the classification reads the observed cause, never a guess).
        EOF on stdout means the process closed its output — it is gone or
        going; wait() makes the death CERTAIN before the cause is read, so the
        pump has flushed everything it will ever carry (never the lagging-read
        class that lost the duplicate-key line at the pre-refinement tree)."""
        if self.proc.poll() is None and not self._eof:
            return None  # a live session: the stall class, never a guess
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        self._errpump.join(timeout=5)  # the pump's final flush after the reap
        return "".join(self._err)

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
        raise TimeoutError(f"session marker {marker} not observed — psql stalled "
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


def canonical_body(*, command: str, client_id: str, owner_scope: str, actor: str, payload: str) -> str:
    """P3-K0's first contract: the canonical versioned structured request
    encoding. Delimiter concatenation was the card's named defect (two
    DIFFERENT commands sharing one body hash — a false provenance equivalence,
    observed live at the predecessor). The canonical form:
      * VERSIONED: 'arv_body_version' is explicit in the structure itself;
      * STRUCTURED: typed named fields, never positional tokens — an empty
        value is unambiguous with a missing one (K-05);
      * FIELD-ORDER INDEPENDENT: the fields are serialized with sorted keys;
      * NFC-NORMALIZED: text fields are normalized (the pinned choice, K-04) —
        the same logical text in different normalizations is the SAME body, so
        the same key replays across them.
    Same canonical body + same key -> the same recorded result (the replay);
    a different canonical body under the same key -> ARV-CMD-409."""
    import json
    import unicodedata
    nfc = lambda t: unicodedata.normalize("NFC", t)
    return json.dumps(
        {"arv_body_version": 1, "actor": nfc(actor), "client_id": nfc(client_id),
         "command": nfc(command), "owner_scope": nfc(owner_scope), "payload": nfc(payload)},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )


def _recorded_ref(*, db: str, owner: str, idem_key: str) -> str:
    """An independent read of the recorded result_ref (the replay answer)."""
    r = pg.psql(f"SELECT result_ref FROM arv.command_log "
                f"WHERE owner_scope={_q(owner)} AND idempotency_key={_q(idem_key)};", db=db)
    return r.out.strip()


def _replay_after_conflict(*, db: str, owner: str, idem_key: str, body_hash: str) -> str:
    """The concurrent loser's resolution path (SYS-04's explicit semantics):
    same canonical body -> 'replayed' (the caller answers the recorded result);
    different body -> 'conflict' (ARV-CMD-409 printed); neither -> '' (honest
    unknown). A unique constraint is not a replay promise — THIS is."""
    r = pg.psql(f"SELECT body_hash FROM arv.command_log "
                f"WHERE owner_scope={_q(owner)} AND idempotency_key={_q(idem_key)};", db=db)
    recorded_hash = r.out.strip()
    if not recorded_hash:
        return ""
    if recorded_hash != body_hash:
        print(f"FAIL ARV-CMD-409: idempotency key {idem_key!r} is already recorded with a DIFFERENT body "
              "(the concurrent writer's body won the race — no silent overwrite)")
        print("      repair: use a new idempotency key for a new body; the same key must mean the same command")
        return "conflict"
    return "replayed"


_DUP = "duplicate key value violates unique constraint"
_CONN = ("connection to server", "server closed the connection", "terminating connection",
         "connection refused", "could not connect", "password authentication", "no password")


def _dead_exit(sess: "Session", *, idem_key: str) -> "int | None":
    """The dead-session classifier (SEV-7's refinement, routed at P3-01's SEV
    round): a DEAD session's cause is read from the DRAINED stderr — the
    observed duplicate-key violation is ARV-CMD-011 (zero effect: the
    transaction rolled back; retry the SAME key), a connection-class death is
    the NEW ARV-CMD-012 (the §4.1 UNCERTAIN class: the commit state is
    unknowable from the client — the same-key replay resolves it), an
    unrecognized death stays the honest ARV-CMD-010. A LIVE session returns
    None — the caller's stall class, never a guess."""
    cause = sess.dead_reason()
    if cause is None:
        return None
    if _DUP in cause:
        print(f"FAIL ARV-CMD-011: the session ended before the commit marker — a concurrent "
              "writer won a unique constraint this key does not own (zero effect, the transaction rolled back)")
        print("      repair: retry the SAME idempotency key (the ordinal is re-read) or use a new one")
        return 1
    if any(s in cause for s in _CONN):
        print(f"FAIL ARV-CMD-012: the session died on an infrastructure error — the outcome is UNCERTAIN "
              f"(§4.1: the commit state is unknowable from the client); observed cause: {cause.strip()[:200]}")
        print("      repair: replay the SAME idempotency key — the replay check answers committed-vs-rolled-back "
              "from the recorded state; never assume either")
        return 1
    print(f"FAIL ARV-CMD-010: the session died before the marker with an unrecognized cause — the honest "
          f"unknown; raw cause: {cause.strip()[:200]}")
    print("      repair: inspect the rig's health; the same-key replay is safe (the transaction either committed or rolled back)")
    return 1


def record_event(*, db: str, owner: str, actor: str, client_id: str,
                 idem_key: str, payload: str, crash_at: str = None) -> int:
    """The first registered command: append one evidence event, exactly once.

    Rides the shared _spine (P3-01's DRY: the S3 protocol and the product
    commands' protocol are ONE protocol — replay check -> BEGIN; INSERT
    evidence; INSERT command_log; COMMIT -> ack; the crash points between
    phases; the concurrent-loser resolution).  The behavior is S3-accepted;
    the suites (S3's five + the kernel's twelve) pin it across the refactor.
    """
    def build(sess: "Session", body_hash: str):
        ev_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmt = (f"INSERT INTO arv.evidence_event (id, event_type, payload, owner_scope, actor, run_id, input_hash, created_at) "
                f"VALUES ({_q(ev_id)}, 'event', {_q(payload)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, {_q(ts)});")
        return ev_id, [stmt], " durability_rung=local_durable"  # P4-00b (F3): the kernel's own evidence surface names its rung — the ack grammar's required token on this path too

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id,
                  idem_key=idem_key, command="record_event", payload=payload,
                  build=build, crash_at=crash_at)


class _CapRefusal(Exception):
    """A named validation refusal at the command boundary (zero effect — RTM §6)."""

    def __init__(self, code: str, msg: str, repair: str):
        super().__init__(msg)
        self.code, self.repair = code, repair


def _sess_row(sess: "Session", sql: str) -> str:
    """One row (or scalar) read on the open session; '' when no row.  Callers
    pass pipe-delimited selects (a trailing '|' on scalars) so the filter
    below — the record_event-proven form — can never mistake a psql command
    tag (SET / INSERT 0 1) for a result row."""
    sess.send(sql)
    sess.send(f"\\echo {MARK_CHECK}")
    lines = sess.read_until(MARK_CHECK)
    return next((l for l in lines if "|" in l and "MARK" not in l), "")

def _sess_rows(sess: "Session", sql: str) -> list:
    """The multi-row form of _sess_row: every pipe-framed row the query
    returns (the callers select locator columns first and split on the KNOWN
    pipe positions — content columns ride LAST)."""
    sess.send(sql)
    sess.send(f"\\echo {MARK_CHECK}")
    lines = sess.read_until(MARK_CHECK)
    return [l for l in lines if "|" in l and "MARK" not in l]



def _spine(*, db, owner, actor, client_id, idem_key, command, payload, build=None,
           crash_at: str = None, build_txn=None) -> int:
    """The shared product-command protocol — the record_event spine generalized:
    replay check -> build (validation + ids + statements, BEFORE any write) ->
    BEGIN -> effects + command_log -> COMMIT -> ack.  Crash points sit between
    phases; the concurrent loser rides _replay_after_conflict (a unique
    constraint is not a replay promise, P3-K0).  build(sess, body_hash) returns
    (result_ref, statements, ack_extra); a _CapRefusal inside build prints the
    named code and leaves ZERO rows (the validation precedes the transaction).
    build_txn (the #90 round-3 repair's phase; exactly one of build/build_txn):
    the SAME contract but executed INSIDE the transaction, right after BEGIN —
    the caller's advisory xact lock (its first statement) covers the state
    read, validation, and construction, so a concurrent lifecycle writer can
    never overtake the transition; a _CapRefusal there ROLLs BACK and prints
    the same named code with zero rows (the read-before-BEGIN defect class)."""
    if (build is None) == (build_txn is None):
        raise ValueError("the spine needs exactly one of build / build_txn — the command's build phase")
    body_hash = hashlib.sha256(canonical_body(command=command, client_id=client_id,
                                              owner_scope=owner, actor=actor,
                                              payload=payload).encode()).hexdigest()
    sess = Session(db, "arv_app", owner)
    try:
        row = _sess_row(sess, f"SELECT body_hash || '|' || result_ref FROM arv.command_log "
                              f"WHERE idempotency_key={_q(idem_key)};")
        if row:
            recorded_hash, recorded_ref = row.split("|")
            if recorded_hash != body_hash:
                print(f"FAIL ARV-CMD-409: idempotency key {idem_key!r} is already recorded with a DIFFERENT body "
                      "(no silent overwrite — exactly-once is a contract, not a preference)")
                print("      repair: use a new idempotency key for a new body; the same key must mean the same command")
                return 1
            # P4-00b (F3 closed): the replayed ack names its rung too — the
            # recorded command_log row committed locally, so the replay's
            # answer is local_durable exactly like the first ack (SYS-01 on
            # EVERY acknowledgment path) — plus the version token.
            print(f"ACK command={command} idem_key={idem_key} status=replayed "
                  f"result_ref={recorded_ref} durability_rung=local_durable api_version={API_VERSION}")
            return 0
        try:
            if build is not None:
                ref, stmts, extra = build(sess, body_hash)
            else:
                ref, stmts, extra = None, [], None
        except _CapRefusal as r:
            print(f"FAIL {r.code}: {r}")
            print(f"      repair: {r.repair}")
            return 1
        sess.send("BEGIN;")
        sess.send(f"\\echo {MARK_BEGUN}")
        try:
            sess.read_until(MARK_BEGUN)
        except TimeoutError:
            rc = _dead_exit(sess, idem_key=idem_key)
            if rc is not None:
                return rc
            raise  # a live session with no marker: the honest unknown (ARV-CMD-010)
        if crash_at == "after-begin":
            sess.kill()
            return 2
        if build_txn is not None:
            # THE LOCKED SECTION (the #90 round-3 repair): the state read, validation,
            # and construction run INSIDE the transaction behind the caller's advisory
            # xact lock — a lifecycle writer commits BEFORE the lock (the read sees it:
            # the clean refusal) or waits for this transaction's end; a refusal rolls
            # back with zero rows
            try:
                ref, stmts, extra = build_txn(sess, body_hash)
            except _CapRefusal as r:
                sess.send("ROLLBACK;")
                print(f"FAIL {r.code}: {r}")
                print(f"      repair: {r.repair}")
                return 1
        ts = clock.now()
        stmts = stmts + [f"INSERT INTO arv.command_log (owner_scope, idempotency_key, client_id, command_name, body_hash, result_ref, actor, created_at) "
                         f"VALUES ({_q(owner)}, {_q(idem_key)}, {_q(client_id)}, {_q(command)}, {_q(body_hash)}, {_q(ref)}, {_q(actor)}, {_q(ts)});"]
        # P3-08 (CLAIM-059): the outbox row rides the SAME transaction — the
        # client outbox (sync intent) on the local site, the server outbox
        # (the D-018 enrichment handoff) on the server site. ARV_SITE is read
        # here per-call (the main()-PGDATABASE precedent; the LAW-24 lint's
        # ambient set never included env reads).
        if command in _SYNC_COMMANDS:
            if os.environ.get("ARV_SITE", "local") == "server":
                stmts.append(f"INSERT INTO arv.server_outbox (owner_scope, idempotency_key, "
                             f"command_name, body_hash, state, created_at) "
                             f"VALUES ({_q(owner)}, {_q(idem_key)}, {_q(command)}, "
                             f"{_q(body_hash)}, 'pending', {_q(ts)});")
            else:
                stmts.append(f"INSERT INTO arv.outbox (owner_scope, idempotency_key, client_id, "
                             f"actor, command_name, body_hash, payload, state, attempts, "
                             f"created_at, updated_at) VALUES ({_q(owner)}, {_q(idem_key)}, "
                             f"{_q(client_id)}, {_q(actor)}, {_q(command)}, {_q(body_hash)}, "
                             f"{_q(payload)}, 'pending', 0, {_q(ts)}, {_q(ts)});")
        for s in stmts:
            sess.send(s)
        sess.send(f"\\echo {MARK_INSERTS}")
        try:
            sess.read_until(MARK_INSERTS)
        except TimeoutError:
            recorded = _replay_after_conflict(db=db, owner=owner, idem_key=idem_key, body_hash=body_hash)
            if recorded == "replayed":
                ref_r = _recorded_ref(db=db, owner=owner, idem_key=idem_key)
                print(f"ACK command={command} idem_key={idem_key} status=replayed "
                      f"result_ref={ref_r} durability_rung=local_durable api_version={API_VERSION}")
                return 0
            if recorded == "conflict":
                return 1
            rc = _dead_exit(sess, idem_key=idem_key)  # SEV-7: the drained OBSERVED cause, never the poll()-inferred guess
            if rc is not None:
                return rc
            raise  # a live session with no marker: the honest unknown (ARV-CMD-010)
        if crash_at == "pre-commit":
            sess.kill()
            return 2
        sess.send("COMMIT;")
        sess.send(f"\\echo {MARK_COMMITTED}")
        try:
            sess.read_until(MARK_COMMITTED)
        except TimeoutError:
            rc = _dead_exit(sess, idem_key=idem_key)
            if rc is not None:
                return rc
            raise  # a live session with no marker: the honest unknown (ARV-CMD-010)
        if crash_at == "post-commit-pre-ack":
            sess.kill()
            return 2
        # P4-00b: the frozen ack grammar's tail — the version token rides
        # every committed ack (the compatibility matrix's foundation).
        print(f"ACK command={command} idem_key={idem_key} status=committed "
              f"result_ref={ref}{extra} api_version={API_VERSION}")
        return 0
    except TimeoutError as e:
        print(f"FAIL ARV-CMD-010: {e}")
        return 1
    finally:
        try:
            sess.close()
        except Exception:
            pass


def _import_body(*, title, work_id, digest, media_type, byte_size, acquired_via) -> str:
    """The canonical import payload — ONE construction home (command + walk; the
    journal's body_hash proves it — a mismatch is ARV-IMP-001)."""
    return json.dumps({"work_id": work_id, "title": title, "digest": digest,
                      "media_type": media_type, "acquired_via": acquired_via,
                      "byte_size": byte_size},
                     sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _import_build(*, owner, actor, client_id, idem_key, title, work_id, digest,
                  media_type, byte_size, acquired_via):
    """Phase 3's statements (shared with the walk's re-drive): the work insert
    when --title, the Source BORN complete, the ordinal re-read, and the
    journal's complete update RIDING the same transaction."""
    def build(sess: "Session", body_hash: str):
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts, new_work = [], work_id
        if work_id is None:
            new_work = ids.new_id()
            stmts.append(f"INSERT INTO arv.work (id, title, owner_scope, actor, run_id, input_hash, created_at) "
                         f"VALUES ({_q(new_work)}, {_q(title)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, {_q(ts)});")
        elif not _sess_row(sess, f"SELECT id || '|' FROM arv.work WHERE id={_q(work_id)};"):
            raise _CapRefusal("ARV-CAP-006", f"work {work_id} does not exist in the caller's scope",
                              "import against an existing work id, or create a new work with --title")
        sid = ids.new_id()
        version = _sess_row(sess, f"SELECT (COALESCE(MAX(source_version), 0) + 1) || '|' FROM arv.source "
                                  f"WHERE work_id={_q(new_work)};").split("|")[0] or "1"
        stmts.append(f"INSERT INTO arv.source (id, work_id, digest, media_type, byte_size, blob_ref, acquired_via, "
                     f"import_state, source_version, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
                     f"VALUES ({_q(sid)}, {_q(new_work)}, {_q(digest)}, {_q(media_type)}, {byte_size}, {_q(digest)}, "
                     f"{_q(acquired_via)}, 'complete', {version}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                     f"{_q(idem_key)}, {_q(ts)});")
        stmts.append(f"UPDATE arv.import_journal SET state='complete', source_id={_q(sid)}, updated_at={_q(ts)} "
                     f"WHERE owner_scope={_q(owner)} AND idempotency_key={_q(idem_key)};")
        return sid, stmts, f" work_id={new_work} durability_rung=local_durable"
    return build


def _journal_txn(sess: "Session", stmt: str, *, idem_key: str) -> bool:
    """One journal-phase transaction — its own commit and marker; a dead
    session classifies (SEV-7), a live stall is the named ARV-CMD-010."""
    try:
        sess.send("BEGIN;")
        sess.send(stmt)
        sess.send("COMMIT;")
        sess.send(f"\\echo {MARK_COMMITTED}")
        sess.read_until(MARK_COMMITTED)
        return True
    except TimeoutError:
        rc = _dead_exit(sess, idem_key=idem_key)
        if rc is not None:
            return False
        print(f"FAIL ARV-CMD-010: the journal transaction for key {idem_key!r} did not reach its "
              "commit marker — the honest unknown (the transaction rolled back or never ran)")
        print("      repair: inspect the rig's health; the same-key retry is safe (nothing committed)")
        return False


def import_source(*, db, owner, actor, client_id, idem_key, title=None, work_id=None,
                  file=None, media_type="text/plain", acquired_via="cli-import",
                  crash_at: str = None) -> int:
    """The phased import (P3-02; RTM §3.1): validation -> the replay/conflict
    check BEFORE any staging -> the staging UPSERT (the same-key rewind) ->
    put+verify INSIDE staging -> staging_verified -> ONE metadata transaction
    (work + Source born complete + command_log + the journal's complete update,
    atomically). Q12-neutral; a refused request stages NOTHING."""
    path = pathlib.Path(file) if file else None
    if path is None or not path.is_file():
        print(f"FAIL ARV-CAP-001: the import file {file!r} is absent or unreadable — the bytes are read and hashed BEFORE any effect")
        print("      repair: pass --file with a readable path; a missing file is a named refusal, never a partial import")
        return 1
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*", media_type):
        print(f"FAIL ARV-CAP-009: media_type {media_type!r} is not a MIME token pair (type/subtype, "
              "token charset only) — free-form text is a title/payload, never a media type")
        print("      repair: pass a MIME pair like text/plain or application/json (the intake-supported formats — see `python3 harness/capability.py matrix`; opaque bytes ride the application/octet-stream passthrough)")
        return 1
    if (title is None) == (work_id is None):
        print("FAIL ARV-CAP-007: exactly one of --title (a new work) or --work-id (an existing work) "
              "is required — an import names its work")
        print("      repair: pass --title OR --work-id, never both, never neither")
        return 1
    # P4-A slice one (CLAIM-065): the FORMAT REGISTRY check — AFTER the MIME
    # grammar (CAP-009 precedes: the grammar is the entry boundary), BEFORE
    # any effect. The approval registry IS the capability matrix: a MIME-valid
    # but unregistered type is the typed ARV-FMT-001 refusal, zero effect.
    try:
        check_registered(media_type)
    except _FmtRefusal as r:
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    data = path.read_bytes()
    digest = blob.digest_of(data)
    body = _import_body(title=title, work_id=work_id, digest=digest, media_type=media_type,
                        byte_size=len(data), acquired_via=acquired_via)
    body_hash = hashlib.sha256(canonical_body(command="import_source", client_id=client_id,
                                              owner_scope=owner, actor=actor,
                                              payload=body).encode()).hexdigest()
    sess = Session(db, "arv_app", owner)
    try:
        # phase 0.5 — the replay/conflict check BEFORE any staging; the CRASH-DOMAIN guard
        # (#4): the journal row's body_hash extends the same-key rule past the command_log's reach
        row = _sess_row(sess, f"SELECT body_hash || '|' || result_ref FROM arv.command_log "
                              f"WHERE idempotency_key={_q(idem_key)};")
        if row:
            recorded_hash, recorded_ref = row.split("|")
            if recorded_hash != body_hash:
                print(f"FAIL ARV-CMD-409: idempotency key {idem_key!r} is already recorded with a DIFFERENT body "
                      "(no silent overwrite — exactly-once is a contract, not a preference)")
                print("      repair: use a new idempotency key for a new body; the same key must mean the same command")
                return 1
            wid_ack = _sess_row(sess, f"SELECT work_id || '|' FROM arv.source WHERE id={_q(recorded_ref)};")
            print(f"ACK command=import_source idem_key={idem_key} status=replayed result_ref={recorded_ref}"
                  f" work_id={wid_ack.split('|')[0] if wid_ack else ''} durability_rung=local_durable"
                  f" api_version={API_VERSION}")
            return 0
        jrowj = _sess_row(sess, f"SELECT row_to_json(j) || '|' FROM (SELECT body_hash, client_id FROM "
                                f"arv.import_journal WHERE idempotency_key={_q(idem_key)}) j;")
        if jrowj:
            jr = json.loads(jrowj.split("|", 1)[0])
            # the re-drive domain's identity is the IMPORT itself: a fresh retry may carry a
            # different client_id (provenance) — recompute the row's body under the ROW'S client
            # and only a genuinely different import (same key, different payload) is the 409
            alt = hashlib.sha256(canonical_body(command="import_source", client_id=jr["client_id"],
                                                owner_scope=owner, actor=actor,
                                                payload=body).encode()).hexdigest()
            if alt != jr["body_hash"]:
                print(f"FAIL ARV-CMD-409: idempotency key {idem_key!r} is already recorded with a DIFFERENT body "
                      "(a crashed attempt's journal row carries a different import — the crash-domain replay guard)")
                print("      repair: use a new idempotency key for a new body; the same key must mean the same command")
                return 1
        if work_id is not None and not _sess_row(sess, f"SELECT id || '|' FROM arv.work WHERE id={_q(work_id)};"):
            print(f"FAIL ARV-CAP-006: work {work_id} does not exist in the caller's scope")
            print("      repair: import against an existing work id, or create a new work with --title")
            return 1
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]  # phase 1: the staging UPSERT (own txn; the rewind)
        if not _journal_txn(sess,
                            f"INSERT INTO arv.import_journal (id, owner_scope, actor, idempotency_key, client_id, "
                            f"work_id, title, digest, media_type, byte_size, acquired_via, state, body_hash, run_id, "
                            f"input_hash, created_at, updated_at) VALUES ({_q(ids.new_id())}, {_q(owner)}, {_q(actor)}, "
                            f"{_q(idem_key)}, {_q(client_id)}, {_qn(work_id)}, {_qn(title)}, {_q(digest)}, {_q(media_type)}, "
                            f"{len(data)}, {_q(acquired_via)}, 'staging', {_q(body_hash)}, {_q(run_id)}, {_q(ih)}, "
                            f"{_q(ts)}, {_q(ts)}) ON CONFLICT (owner_scope, idempotency_key) DO UPDATE SET "
                            f"state='staging', fail_reason=NULL, source_id=NULL, updated_at={_q(ts)}, "
                            f"client_id={_q(client_id)}, body_hash={_q(body_hash)}, run_id={_q(run_id)}, input_hash={_q(ih)};",
                            idem_key=idem_key):
            return 1
        if crash_at == "after-staging":
            sess.kill()
            return 2
        blob.put(data)  # phase 2: put + verify INSIDE staging (§3.1's exit condition)
        if crash_at == "after-put":
            sess.kill()
            return 2
        try:
            blob.get(digest)  # the §3.1 verify: readable AND digest-matched (get re-hashes)
        except KeyError as e:
            reason = e.args[0].split(":")[0] if e.args else "ARV-BLOB-000"  # e.args[0]: str(e) would carry KeyError's repr quotes
            _journal_txn(sess, f"UPDATE arv.import_journal SET state='failed', "
                          f"fail_reason={_q(reason)}, updated_at={_q(clock.now())} "
                          f"WHERE owner_scope={_q(owner)} AND idempotency_key={_q(idem_key)};",
                         idem_key=idem_key)
            print(f"FAIL ARV-CAP-004: the blob verify failed — {e.args[0] if e.args else e}")
            print("      repair: the store is corrupt at this digest; the row is failed(retryable) and the recovery walk cleans the unreferenced artifact — a Source NEVER commits without verified bytes")
            return 1
        # P4-A slice one (CLAIM-065): the FORMAT DECODE + the format's own
        # grammar — AFTER the blob staging (the staged-bytes contract: the
        # refusal NAMES the digest, the bytes stay recoverable, the journal
        # row failed-retryable — the ARV-CAP-004 pattern extended to the
        # format class). Staged bytes are never lost.
        try:
            decode(media_type, data, digest)
        except _FmtRefusal as r:
            _journal_txn(sess, f"UPDATE arv.import_journal SET state='failed', "
                          f"fail_reason={_q(r.code)}, updated_at={_q(clock.now())} "
                          f"WHERE owner_scope={_q(owner)} AND idempotency_key={_q(idem_key)};",
                         idem_key=idem_key)
            print(f"FAIL {r.code}: {r}")
            print(f"      repair: {r.repair} [digest={r.digest}]")
            return 1
        if not _journal_txn(sess, f"UPDATE arv.import_journal SET state='staging_verified', "
                            f"updated_at={_q(clock.now())} WHERE owner_scope={_q(owner)} "
                            f"AND idempotency_key={_q(idem_key)};", idem_key=idem_key):
            return 1
        if crash_at == "after-verify":
            sess.kill()
            return 2
        def build_with_index(sess2: "Session", body_hash: str):
            sid, stmts, ack = _import_build(owner=owner, actor=actor, client_id=client_id,
                                            idem_key=idem_key, title=title, work_id=work_id,
                                            digest=digest, media_type=media_type,
                                            byte_size=len(data), acquired_via=acquired_via)(sess2, body_hash)
            # P3-07: the source's full decoded text rides the SAME metadata
            # transaction (the explicit-lag contract — a committed source is
            # searchable immediately; a refused import leaves zero rows).
            # P4-A slice three (CLAIM-067): the text-access routes through the
            # ONE home — the epub's derived view indexes exactly like the text
            # formats' own bytes
            try:
                src_text = read_text(media_type, digest)
            except (UnicodeDecodeError, KeyError, _FmtRefusal):
                src_text = ""  # the non-text boundary: the source commits; the findability rung indexes text only
            return sid, stmts + _kwr_index_stmts(owner, "source", sid, 1, [src_text], clock.now()), ack

        return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                      command="import_source", payload=body, build=build_with_index, crash_at=crash_at)
    finally:
        try:
            sess.close()
        except Exception:
            pass


def create_highlight(*, db, owner, actor, client_id, idem_key, source_id,
                     start, end, crash_at: str = None) -> int:
    """The capture command: commit the selected text WITH its version-tied
    anchor (P3-01; RTM §2.4/§2.5).  The selected text is DERIVED from the
    stored bytes at the given offsets — a client never supplies anchor truth;
    the anchor's source_digest is read from the source row itself, so the tie
    to that Source version is by construction (the §6 wrong-version class)."""
    body = json.dumps({"source_id": source_id, "start": start, "end": end},
                     sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        row = _sess_row(sess, f"SELECT digest || '|' || media_type FROM arv.source WHERE id={_q(source_id)};")
        if not row:
            raise _CapRefusal("ARV-CAP-002",
                              f"source {source_id} does not exist in the caller's scope — a dangling anchor target is REFUSED at the command boundary (RTM §6)",
                              "import the source first; a capture may only anchor into a source version visible to this owner")
        digest, media_type = row.split("|")
        try:
            # P4-A slice three (CLAIM-067): the ONE read_text home — the
            # epub's derived view is the offset domain
            text = read_text(media_type, digest)
        except UnicodeDecodeError:
            raise _CapRefusal("ARV-CAP-008",
                              f"source {source_id} is not valid UTF-8 text (P3-01 supports readable text/Markdown — the media-type boundary)",
                              "import the source with a supported media type; binary formats land with their own slices")
        except KeyError as e:
            raise _CapRefusal("ARV-CAP-004", f"the source's blob failed to verify — {e}",
                              "the store is corrupt at this digest; never a capture against unverifiable bytes")
        except _FmtRefusal as r:
            # the epub derivation's own refusal (unreachable for a source that
            # passed the import walk — the derivation is deterministic over
            # digest-verified bytes; the arm is the honest backstop, never a
            # crash)
            raise _CapRefusal("ARV-CAP-008",
                              f"source {source_id}'s derived text cannot be produced — {r}",
                              "the store's bytes changed under the digest (the corruption class); never a capture against an underivable view")
        if not (0 <= start < end <= len(text)):
            raise _CapRefusal("ARV-CAP-003",
                              f"offsets [{start},{end}) are invalid for a {len(text)}-character text — never clamped, never guessed",
                              "supply 0 <= start < end <= the decoded text length")
        selected = text[start:end]
        anchor_id, hl_id = ids.new_id(), ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [
            f"INSERT INTO arv.anchor (id, source_id, source_digest, start_off, end_off, context_before, "
            f"context_after, media_type, owner_scope, actor, run_id, input_hash, created_at) VALUES "
            f"({_q(anchor_id)}, {_q(source_id)}, {_q(digest)}, {start}, {end}, "
            f"{_q(text[max(0, start - 32):start])}, {_q(text[end:end + 32])}, {_q(media_type)}, "
            f"{_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, {_q(ts)});",
            f"INSERT INTO arv.highlight (id, revision, selected_text, source_id, anchor_id, owner_scope, actor, "
            f"run_id, input_hash, idempotency_key, created_at) VALUES ({_q(hl_id)}, 1, {_q(selected)}, "
            f"{_q(source_id)}, {_q(anchor_id)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
            f"{_q(idem_key)}, {_q(ts)});",
        ] + _kwr_index_stmts(owner, "highlight", hl_id, 1,
                             [selected, text[max(0, start - 32):start], text[end:end + 32]], ts)
        return hl_id, stmts, f" revision=1 durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="create_highlight", payload=body, build=build, crash_at=crash_at)


# ------------------------------------------------- P3-04: the revision/tombstone machine (RTM §3.3/§2.5)

def _hl_refusal(code: str, hl_id: str, extra: str = "", repair: str = "") -> _CapRefusal:
    """The highlight-family boundary refusals — absent and another owner's are
    the SAME refusal, never a side channel (RTM §2.10 on the write path)."""
    msg = extra or (f"highlight {hl_id} does not exist in the caller's scope — absent and "
                    "another owner's are the SAME refusal, never a side channel")
    return _CapRefusal(code, msg, repair or "check the id against the caller's own capture list "
                       "(query.py list-captures); a highlight is only ever addressable "
                       "by its owner")


def _hl_current(sess: "Session", hl_id: str) -> tuple:
    """One read: the current (max) revision + its source binding + the DERIVED
    lifecycle state (the parity of the committed events — order-independent,
    rebuildable; never a state column duplicating a derivable fact)."""
    row = _sess_row(sess,
                    f"SELECT h.revision || '|' || h.source_id || '|' || COALESCE("
                    f"(SELECT CASE WHEN count(*) FILTER (WHERE l.event = 'tombstone') > "
                    f"count(*) FILTER (WHERE l.event = 'restore') THEN 'tombstoned' "
                    f"ELSE 'active' END FROM arv.highlight_lifecycle l "
                    f"WHERE l.highlight_id = h.id AND l.owner_scope = h.owner_scope), 'active') "
                    f"FROM arv.highlight h WHERE h.id = {_q(hl_id)} "
                    f"ORDER BY h.revision DESC LIMIT 1;")
    if not row:
        raise _hl_refusal("ARV-HLC-001", hl_id)
    revision, source_id, state = row.split("|")
    return int(revision), source_id, state


def revise_highlight(*, db, owner, actor, client_id, idem_key, id_,
                     start, end, crash_at: str = None) -> int:
    """§3.3's edit transition: append a NEW immutable revision (n+1) — the
    selected content RE-DERIVED from the SAME Source version's stored bytes at
    the new offsets (a client never supplies anchor truth; the source binding is
    identity-fixed by construction, a revision NEVER crosses Source versions),
    a NEW anchor row (the prior revision's anchor stays, referenced by the prior
    row).  Tombstoned refuses (ARV-HLC-002: restore first)."""
    body = json.dumps({"id": id_, "start": start, "end": end},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        revision, source_id, state = _hl_current(sess, id_)
        if state != "active":
            raise _CapRefusal("ARV-HLC-002",
                              f"highlight {id_} is tombstoned — a tombstoned highlight is hidden "
                              "from ordinary use until restored (RTM §3.3: restore precedes edit)",
                              "restore the highlight first (commands.py restore_highlight); the "
                              "governed history retains every revision meanwhile")
        row = _sess_row(sess, f"SELECT digest || '|' || media_type FROM arv.source WHERE id={_q(source_id)};")
        if not row:
            raise _CapRefusal("ARV-CAP-004", f"the revision's source {source_id} is not loadable",
                              "the store is corrupt at this id; the identity-fix refuses, never a guess")
        digest, media_type = row.split("|")
        try:
            # P4-A slice three (CLAIM-067): the ONE read_text home
            text = read_text(media_type, digest)
        except UnicodeDecodeError:
            raise _CapRefusal("ARV-CAP-008",
                              f"source {source_id} is not valid UTF-8 text (the media-type boundary)",
                              "the revision re-derives from stored text; binary formats are their own slices")
        except KeyError as e:
            raise _CapRefusal("ARV-CAP-004", f"the source's blob failed to verify — {e}",
                              "the store is corrupt at this digest; never a revision against unverifiable bytes")
        except _FmtRefusal as r:
            raise _CapRefusal("ARV-CAP-008",
                              f"source {source_id}'s derived text cannot be produced — {r}",
                              "the store's bytes changed under the digest (the corruption class); never a revision against an underivable view")
        if not (0 <= start < end <= len(text)):
            raise _CapRefusal("ARV-CAP-003",
                              f"offsets [{start},{end}) are invalid for a {len(text)}-character text — "
                              "never clamped, never guessed",
                              "supply 0 <= start < end <= the decoded text length")
        selected = text[start:end]
        anchor_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [
            f"INSERT INTO arv.anchor (id, source_id, source_digest, start_off, end_off, context_before, "
            f"context_after, media_type, owner_scope, actor, run_id, input_hash, created_at) VALUES "
            f"({_q(anchor_id)}, {_q(source_id)}, {_q(digest)}, {start}, {end}, "
            f"{_q(text[max(0, start - 32):start])}, {_q(text[end:end + 32])}, {_q(media_type)}, "
            f"{_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, {_q(ts)});",
            f"INSERT INTO arv.highlight (id, revision, selected_text, source_id, anchor_id, owner_scope, "
            f"actor, run_id, input_hash, idempotency_key, created_at) VALUES ({_q(id_)}, {revision + 1}, "
            f"{_q(selected)}, {_q(source_id)}, {_q(anchor_id)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, "
            f"{_q(ih)}, {_q(idem_key)}, {_q(ts)});",
        ] + _kwr_index_stmts(owner, "highlight", id_, revision + 1,
                             [selected, text[max(0, start - 32):start], text[end:end + 32]], ts)
        return id_, stmts, f" revision={revision + 1} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="revise_highlight", payload=body, build=build, crash_at=crash_at)


def _lifecycle_command(*, command, event, db, owner, actor, client_id, idem_key,
                       id_, crash_at, refusal_code, refusal_msg, refusal_repair) -> int:
    """§3.3's tombstone/restore transitions: ONE typed lifecycle EVENT row per
    LAWFUL transition (append-only, owner-scoped, provenance-complete).  The
    named command-boundary refusals are the clean first line; the substrate's
    advisory-lock alternation trigger (0007) is the race + hostile backstop."""
    body = json.dumps({"id": id_}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        _, _, state = _hl_current(sess, id_)
        if (event == "tombstone" and state != "active") or (event == "restore" and state != "tombstoned"):
            raise _CapRefusal(refusal_code, refusal_msg(id_), refusal_repair)
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.highlight_lifecycle (id, highlight_id, event, owner_scope, actor, "
                 f"run_id, input_hash, idempotency_key, created_at) VALUES ({_q(ids.new_id())}, "
                 f"{_q(id_)}, {_q(event)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)});"]
        return id_, stmts, " durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command=command, payload=body, build=build, crash_at=crash_at)


def tombstone_highlight(*, db, owner, actor, client_id, idem_key, id_, crash_at: str = None) -> int:
    """§3.3's delete transition: tombstoned — hidden from ordinary retrieval
    (list/get), the governed history retained; recoverable by restore."""
    return _lifecycle_command(
        command="tombstone_highlight", event="tombstone", db=db, owner=owner, actor=actor,
        client_id=client_id, idem_key=idem_key, id_=id_, crash_at=crash_at,
        refusal_code="ARV-HLC-003",
        refusal_msg=lambda i: (f"highlight {i} is already tombstoned — the §3.3 alternation "
                               "(tombstone only from active; the current view is DERIVED from "
                               "the events, never a state column)"),
        refusal_repair="restore the highlight first (commands.py restore_highlight); a second "
                       "tombstone is a no-op refused with its named code, never a second event row")


def restore_highlight(*, db, owner, actor, client_id, idem_key, id_, crash_at: str = None) -> int:
    """§3.3's restore transition: tombstoned -> active (the current revision
    unchanged — the revisions were never touched)."""
    return _lifecycle_command(
        command="restore_highlight", event="restore", db=db, owner=owner, actor=actor,
        client_id=client_id, idem_key=idem_key, id_=id_, crash_at=crash_at,
        refusal_code="ARV-HLC-004",
        refusal_msg=lambda i: (f"highlight {i} is not tombstoned — the §3.3 alternation "
                               "(restore only from tombstoned)"),
        refusal_repair="nothing to restore: the highlight is active in ordinary retrieval; "
                       "a tombstone precedes every restore")


# ------------------------------------------------- P3-05: the bookmark machine (RTM §2.5 item 6 + §3.3)

def _derive_anchor(sess: "Session", *, source_id, start, end, owner, actor,
                   client_id, body_hash):
    """The version-tied location derivation — ONE construction home for the
    bookmark family (the create_highlight/revise_highlight convention; the
    highlight family keeps its landed inline form, pinned by HLG — a refactor
    of landed code is its own slice, never this one's diff).  The offsets are
    validated against the DECODED stored bytes and the anchor row (source
    digest, contexts, media type) is derived — a client never supplies anchor
    truth; the tie to the Source version is by construction (SYS-05's §6
    wrong-version class refused at the boundary).  Returns (anchor_id,
    anchor_stmt); refusals raise _CapRefusal."""
    row = _sess_row(sess, f"SELECT digest || '|' || media_type FROM arv.source WHERE id={_q(source_id)};")
    if not row:
        raise _CapRefusal("ARV-CAP-002",
                          f"source {source_id} does not exist in the caller's scope — a dangling anchor target is REFUSED at the command boundary (RTM §6)",
                          "import the source first; a bookmark may only anchor into a source version visible to this owner")
    digest, media_type = row.split("|")
    try:
        # P4-A slice three (CLAIM-067): the ONE read_text home
        text = read_text(media_type, digest)
    except UnicodeDecodeError:
        raise _CapRefusal("ARV-CAP-008",
                          f"source {source_id} is not valid UTF-8 text (P3-01 supports readable text/Markdown — the media-type boundary)",
                          "import the source with a supported media type; binary formats land with their own slices")
    except KeyError as e:
        raise _CapRefusal("ARV-CAP-004", f"the source's blob failed to verify — {e}",
                          "the store is corrupt at this digest; never a bookmark against unverifiable bytes")
    except _FmtRefusal as r:
        raise _CapRefusal("ARV-CAP-008",
                          f"source {source_id}'s derived text cannot be produced — {r}",
                          "the store's bytes changed under the digest (the corruption class); never a bookmark against an underivable view")
    if not (0 <= start < end <= len(text)):
        raise _CapRefusal("ARV-CAP-003",
                          f"offsets [{start},{end}) are invalid for a {len(text)}-character text — never clamped, never guessed",
                          "supply 0 <= start < end <= the decoded text length")
    anchor_id, ts, ih = ids.new_id(), clock.now(), body_hash[:16]
    stmt = (f"INSERT INTO arv.anchor (id, source_id, source_digest, start_off, end_off, context_before, "
            f"context_after, media_type, owner_scope, actor, run_id, input_hash, created_at) VALUES "
            f"({_q(anchor_id)}, {_q(source_id)}, {_q(digest)}, {start}, {end}, "
            f"{_q(text[max(0, start - 32):start])}, {_q(text[end:end + 32])}, {_q(media_type)}, "
            f"{_q(owner)}, {_q(actor)}, {_q('run-' + client_id)}, {_q(ih)}, {_q(ts)});")
    return anchor_id, stmt, text


def _bm_refusal(code: str, bm_id: str) -> _CapRefusal:
    """The bookmark-family boundary refusal — absent and another owner's are
    the SAME refusal, never a side channel (RTM §2.10 on the write path)."""
    return _CapRefusal(code, f"bookmark {bm_id} does not exist in the caller's scope — absent and "
                       "another owner's are the SAME refusal, never a side channel",
                       "check the id against the caller's own bookmark list (query.py list-bookmarks); "
                       "a bookmark is only ever addressable by its owner")


def _bm_current(sess: "Session", bm_id: str) -> tuple:
    """One read: the current (max) revision + its source binding + the DERIVED
    lifecycle state (the parity of the committed events — order-independent,
    rebuildable; never a state column duplicating a derivable fact)."""
    row = _sess_row(sess,
                    f"SELECT b.revision || '|' || b.source_id || '|' || COALESCE("
                    f"(SELECT CASE WHEN count(*) FILTER (WHERE l.event = 'tombstone') > "
                    f"count(*) FILTER (WHERE l.event = 'restore') THEN 'tombstoned' "
                    f"ELSE 'active' END FROM arv.bookmark_lifecycle l "
                    f"WHERE l.bookmark_id = b.id AND l.owner_scope = b.owner_scope), 'active') "
                    f"FROM arv.bookmark b WHERE b.id = {_q(bm_id)} "
                    f"ORDER BY b.revision DESC LIMIT 1;")
    if not row:
        raise _bm_refusal("ARV-BMK-001", bm_id)
    revision, source_id, state = row.split("|")
    return int(revision), source_id, state


def _bm_insert(bm_id, revision, source_id, anchor_id, owner, actor, client_id,
               idem_key, body_hash) -> str:
    ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
    return (f"INSERT INTO arv.bookmark (id, revision, source_id, anchor_id, owner_scope, actor, "
            f"run_id, input_hash, idempotency_key, created_at) VALUES ({_q(bm_id)}, {revision}, "
            f"{_q(source_id)}, {_q(anchor_id)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
            f"{_q(idem_key)}, {_q(ts)});")


def create_bookmark(*, db, owner, actor, client_id, idem_key, source_id,
                    start, end, crash_at: str = None) -> int:
    """P3-05 (RTM §2.5 item 6): the stable return location — identity + the
    source-versioned Anchor; NO copy of source content (the row carries no
    text; the location evidence lives in the anchor row alone — the column
    set is the structural law)."""
    body = json.dumps({"source_id": source_id, "start": start, "end": end},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        anchor_id, anchor_stmt, text = _derive_anchor(
            sess, source_id=source_id, start=start, end=end, owner=owner,
            actor=actor, client_id=client_id, body_hash=body_hash)
        bm_id = ids.new_id()
        ts = clock.now()
        return bm_id, [anchor_stmt, _bm_insert(bm_id, 1, source_id, anchor_id, owner,
                                               actor, client_id, idem_key, body_hash)] + \
            _kwr_index_stmts(owner, "bookmark", bm_id, 1,
                             [text[start:end], text[max(0, start - 32):start],
                              text[end:end + 32]], ts), \
            " revision=1 durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="create_bookmark", payload=body, build=build, crash_at=crash_at)


def move_bookmark(*, db, owner, actor, client_id, idem_key, id_,
                  start, end, crash_at: str = None) -> int:
    """§3.3's edit transition for the bookmark: append a NEW immutable
    revision (n+1) with a NEW anchor at the new offsets — the location
    RE-DERIVED from the SAME Source version's stored bytes (identity-fixed: a
    bookmark revision NEVER crosses Source versions; the §6 wrong-version
    class is refused at the command boundary by construction).  Tombstoned
    refuses (ARV-BMK-002: restore first).  THE SERIALIZED TRANSITION (the
    #90 round-3 repair, CodeRabbit's 14:43Z Major): the complete transition —
    the per-bookmark advisory xact lock (the SAME lock the 0008 lifecycle
    guard takes) acquired as the transaction's FIRST statement, then the
    state read, active validation, revision selection, anchor construction,
    inserts, and commit, ALL inside the one transaction: a tombstone/restore
    either commits BEFORE the lock (the read sees it — the clean ARV-BMK-002)
    or waits until the move commits — a revision can never commit after
    tombstoning (the read-before-BEGIN defect this closes)."""
    body = json.dumps({"id": id_, "start": start, "end": end},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build_txn(sess: "Session", body_hash: str):
        _sess_row(sess, f"SELECT hashtext({_q(id_)}) || '|' || pg_advisory_xact_lock(hashtext({_q(id_)}));")  # the lock FIRST, held to the commit
        revision, source_id, state = _bm_current(sess, id_)
        if state != "active":
            raise _CapRefusal("ARV-BMK-002",
                              f"bookmark {id_} is tombstoned — a tombstoned bookmark is hidden "
                              "from ordinary use until restored (RTM §3.3: restore precedes edit)",
                              "restore the bookmark first (commands.py restore_bookmark); the "
                              "governed history retains every revision meanwhile")
        anchor_id, anchor_stmt, text = _derive_anchor(
            sess, source_id=source_id, start=start, end=end, owner=owner,
            actor=actor, client_id=client_id, body_hash=body_hash)
        return id_, [anchor_stmt, _bm_insert(id_, revision + 1, source_id, anchor_id,
                                             owner, actor, client_id, idem_key, body_hash)] + \
            _kwr_index_stmts(owner, "bookmark", id_, revision + 1,
                             [text[start:end], text[max(0, start - 32):start],
                              text[end:end + 32]], clock.now()), \
            f" revision={revision + 1} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="move_bookmark", payload=body, build_txn=build_txn, crash_at=crash_at)


def _bm_lifecycle_command(*, command, event, db, owner, actor, client_id, idem_key,
                          id_, crash_at, refusal_code, refusal_msg, refusal_repair) -> int:
    """§3.3's tombstone/restore transitions: ONE typed lifecycle EVENT row per
    LAWFUL transition (append-only, owner-scoped, provenance-complete).  The
    named command-boundary refusals are the clean first line; the substrate's
    advisory-lock alternation trigger (0008) is the race + hostile backstop."""
    body = json.dumps({"id": id_}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        _, _, state = _bm_current(sess, id_)
        if (event == "tombstone" and state != "active") or (event == "restore" and state != "tombstoned"):
            raise _CapRefusal(refusal_code, refusal_msg(id_), refusal_repair)
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.bookmark_lifecycle (id, bookmark_id, event, owner_scope, actor, "
                 f"run_id, input_hash, idempotency_key, created_at) VALUES ({_q(ids.new_id())}, "
                 f"{_q(id_)}, {_q(event)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)});"]
        return id_, stmts, " durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command=command, payload=body, build=build, crash_at=crash_at)


def tombstone_bookmark(*, db, owner, actor, client_id, idem_key, id_, crash_at: str = None) -> int:
    """§3.3's delete transition: tombstoned — hidden from ordinary retrieval
    (get/list), the governed history retained; recoverable by restore."""
    return _bm_lifecycle_command(
        command="tombstone_bookmark", event="tombstone", db=db, owner=owner, actor=actor,
        client_id=client_id, idem_key=idem_key, id_=id_, crash_at=crash_at,
        refusal_code="ARV-BMK-003",
        refusal_msg=lambda i: (f"bookmark {i} is already tombstoned — the §3.3 alternation "
                               "(tombstone only from active; the current view is DERIVED from "
                               "the events, never a state column)"),
        refusal_repair="restore the bookmark first (commands.py restore_bookmark); a second "
                       "tombstone is a no-op refused with its named code, never a second event row")


def restore_bookmark(*, db, owner, actor, client_id, idem_key, id_, crash_at: str = None) -> int:
    """§3.3's restore transition: tombstoned -> active (the current revision
    unchanged — the revisions were never touched)."""
    return _bm_lifecycle_command(
        command="restore_bookmark", event="restore", db=db, owner=owner, actor=actor,
        client_id=client_id, idem_key=idem_key, id_=id_, crash_at=crash_at,
        refusal_code="ARV-BMK-004",
        refusal_msg=lambda i: (f"bookmark {i} is not tombstoned — the §3.3 alternation "
                               "(restore only from tombstoned)"),
        refusal_repair="nothing to restore: the bookmark is active in ordinary retrieval; "
                       "a tombstone precedes every restore")


# ------------------------------------------------- P3-06: the note machine (RTM §2.5 item 7 + §3.3)

def _nte_refusal(code: str, note_id: str) -> _CapRefusal:
    """The note-family boundary refusal — absent and another owner's are
    the SAME refusal, never a side channel (RTM §2.10 on the write path)."""
    return _CapRefusal(code, f"note {note_id} does not exist in the caller's scope — absent and "
                       "another owner's are the SAME refusal, never a side channel",
                       "check the id against the caller's own note list (query.py list-notes); "
                       "a note is only ever addressable by its owner")


def _nte_current(sess: "Session", note_id: str) -> tuple:
    """One read: the current (max) revision + the DERIVED lifecycle state
    (the parity of the committed events — order-independent, rebuildable;
    never a state column duplicating a derivable fact)."""
    row = _sess_row(sess,
                    f"SELECT n.revision || '|' || COALESCE("
                    f"(SELECT CASE WHEN count(*) FILTER (WHERE l.event = 'tombstone') > "
                    f"count(*) FILTER (WHERE l.event = 'restore') THEN 'tombstoned' "
                    f"ELSE 'active' END FROM arv.note_lifecycle l "
                    f"WHERE l.note_id = n.id AND l.owner_scope = n.owner_scope), 'active') "
                    f"FROM arv.note n WHERE n.id = {_q(note_id)} "
                    f"ORDER BY n.revision DESC LIMIT 1;")
    if not row:
        raise _nte_refusal("ARV-NTE-001", note_id)
    revision, state = row.split("|")
    return int(revision), state


def _nte_content(*, content: "str | None", content_file: "str | None") -> str:
    """The authored-content source: exactly one of --content / --content-file;
    the file read LOSSLESSLY (read_bytes + UTF-8 decode — no newline
    translation, no trimming); the NUL boundary named (the standing spine
    residual refused at THIS boundary with its code, never the mid-protocol
    death)."""
    if (content is None) == (content_file is None):
        raise _CapRefusal("ARV-NTE-010",
                          "exactly one of --content / --content-file is required — the authored "
                          "content must arrive through one named channel",
                          "pass --content-file for the long-form authoring surface, or --content "
                          "for an inline body; never both, never neither")
    try:
        body = content if content is not None else \
            pathlib.Path(content_file).read_bytes().decode("utf-8")
    except FileNotFoundError:
        raise _CapRefusal("ARV-NTE-010",
                          f"the content file {content_file!r} does not exist — the authored "
                          "content cannot be read",
                          "supply an existing readable file path")
    except (IsADirectoryError, PermissionError, OSError) as e:
        raise _CapRefusal("ARV-NTE-010", f"the content file cannot be read — {e}",
                          "supply an existing readable file path")
    except UnicodeDecodeError:
        raise _CapRefusal("ARV-NTE-010",
                          "the content file is not valid UTF-8 — the note preserves the owner's "
                          "text losslessly and refuses a lossy interpretation",
                          "supply valid UTF-8; binary formats are their own slices")
    if "\x00" in body:
        raise _CapRefusal("ARV-NTE-009",
                          "the content contains NUL (U+0000) — PostgreSQL TEXT cannot carry it "
                          "(the standing spine residual, named at the note boundary — never "
                          "the mid-protocol death)",
                          "remove the NUL byte; the lossless note surface is every other "
                          "Unicode codepoint")
    return body


def _nte_canon_id(id_: str) -> str:
    """The note identity's ONE canonical form (the #91 round-2 finding
    4439931169: PostgreSQL's uuid input accepts braced, no-hyphen, and
    uppercase spellings of the SAME note): every parseable spelling reduces
    to the canonical hyphenated lowercase text — the payload (LAW-23: a
    variant-spelling retry is the SAME logical command and must REPLAY)
    and the lock key (hashtext of the canonical text — the substrate
    guards' own key, never a second key for one note) both carry it. An
    unparseable spelling cannot be a note (the uuid column) — it keeps its
    lowercased form: a spelling PostgreSQL ACCEPTS meets the ARV-NTE-001
    same-refusal at the state read; a spelling PostgreSQL REFUSES (garbage,
    urn:uuid: prefixes, stray whitespace — never a note id by construction)
    fails the uuid cast inside the session and surfaces the generic
    ARV-CMD-010 session-death wrapper with ZERO effect — the raw-cast
    class shared with the read arms and the landed families, routed with
    the round-2 sibling class to its own slice (the SEV round-4 F1)."""
    try:
        return str(uuid.UUID(id_))
    except (ValueError, AttributeError, TypeError):
        return id_.lower()


def _nte_body(content: str, note_id: "str | None" = None,
              refs: list = None) -> str:
    """The canonical note payload — ONE construction home (the command's body
    hash proves it; exactly-once is over the LOGICAL command). revise_note
    carries the target id in its CANONICAL UUID form (_nte_canon_id — the
    spelling-independent identity: a different note is a different command
    and must meet ARV-CMD-409, never a false replay; every spelling of one
    note is the SAME logical command, matching the canonical lock key)."""
    payload = {"content": content}
    if note_id is not None:
        payload["id"] = note_id
    if refs:
        # CLAIM-057 (the slice-two extension): the canonical sorted reference
        # set rides the payload — the same logical set in a different CLI
        # order hashes identically (LAW-23 over the LOGICAL command). The
        # key is ABSENT for a zero-reference command, so a no-refs body is
        # byte-identical to the note-core slice's committed form: retries of
        # pre-0010 commands replay across the slice boundary, never a false
        # ARV-CMD-409.
        payload["refs"] = [[k, t, r] for k, t, r in refs]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


# P4-D slice two (CLAIM-076; record 68 §2): the write completion — the
# seven landed families, the revision dimension split exactly as the
# resolution surface's grammar law (CLAIM-075) and the 0018 substrate
# CHECK: bare work/source/anchor; revisioned highlight/note/bookmark/
# journal_block (the @rev pin required — the immutable (id, revision) pair
# is what a stored reference MEANS).
_REF_KINDS = ("work", "source", "anchor", "highlight", "note",
              "bookmark", "journal_block")
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                      r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _nte_refs(refs: "list[str] | None") -> list:
    """P3-06 slice two (RTM §2.5 item 7): parse + shape-validate the
    reference strings 'kind:id' / 'kind:id@rev'. Returns the canonical
    sorted [(kind, id, rev|None), ...] (the canonical form is what the body
    hash covers — the same logical reference set in a different CLI order
    is the SAME command); the TARGET existence check is the caller's
    session read per kind."""
    if not refs:
        return []
    out, seen = [], set()
    for r in refs:
        kind, sep, rest = r.partition(":")
        if not sep or kind not in _REF_KINDS:
            raise _CapRefusal("ARV-NTE-006",
                              f"the reference {r!r} names an unknown kind {kind!r} — the "
                              f"referenceable kinds are exactly {_REF_KINDS}",
                              "supply kind:id with kind in work/source/anchor/highlight/"
                              "note/bookmark/journal_block")
        target, at, rev = rest.partition("@")
        if not _UUID_RE.match(target):
            raise _CapRefusal("ARV-NTE-006",
                              f"the reference {r!r} carries a malformed id {target!r} — a "
                              "reference target is a UUID",
                              "supply the target's UUID (query.py list-* / get-*)")
        if kind in ("highlight", "note", "bookmark", "journal_block"):
            if not rev or not rev.isdigit() or int(rev) < 1:
                raise _CapRefusal("ARV-NTE-006",
                                  f"the {kind} reference {r!r} must name the target revision "
                                  "(kind:id@rev — version-aware by construction)",
                                  f"supply {kind}:<uuid>@<revision>; the reference pins the "
                                  "immutable (id, revision) pair, never a silent retarget")
            r_ = int(rev)
        else:
            if at:
                raise _CapRefusal("ARV-NTE-006",
                                  f"the {kind} reference {r!r} must NOT name a revision — the "
                                  "Source id IS the version; Work/Anchor carry no revision "
                                  "dimension",
                                  f"supply {kind}:<uuid> (the bare identity reference)")
            r_ = None
        if (kind, target) in seen:
            raise _CapRefusal("ARV-NTE-008",
                              f"the reference target {kind}:{target} appears more than once — "
                              "the reference set is a set (one reference per target per "
                              "revision)",
                              "supply each target once; a revision pins one version of one "
                              "target")
        seen.add((kind, target))
        out.append((kind, target, r_))
    return sorted(out, key=lambda t: (t[0], t[1]))


def _nte_check_targets(sess: "Session", refs: list) -> None:
    """The TARGET existence check per kind (the session is RLS-scoped to the
    caller: another owner's object is invisible — absent, another owner's,
    and a nonexistent target revision are the SAME refusal, never a side
    channel; the referenced rows are immutable so the check cannot be
    invalidated between validation and commit; the 0010 substrate guard is
    the hostile direct-write backstop)."""
    for kind, target, rev in refs:
        if kind == "work":
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.work WHERE id={_q(target)};")
        elif kind == "source":
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.source WHERE id={_q(target)};")
        elif kind == "anchor":
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.anchor WHERE id={_q(target)};")
        elif kind == "highlight":
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.highlight WHERE id={_q(target)} "
                                  f"AND revision={rev};")
        elif kind == "bookmark":
            # P4-D slice two (CLAIM-076): the write completion's target arm —
            # the same RLS-scoped existence-at-revision read, the same
            # no-oracle refusal (the 0018 guard's own arm mirrors this)
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.bookmark WHERE id={_q(target)} "
                                  f"AND revision={rev};")
        elif kind == "journal_block":
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.journal_block WHERE "
                                  f"id={_q(target)} AND revision={rev};")
        else:
            row = _sess_row(sess, f"SELECT id || '|' FROM arv.note WHERE id={_q(target)} "
                                  f"AND revision={rev};")
        if not row:
            raise _CapRefusal("ARV-NTE-003",
                              f"the referenced {kind} ({target}" + (f"@{rev}" if rev else "") +
                              ") does not exist in the caller's scope — absent, another "
                              "owner's, and a nonexistent target revision are the SAME "
                              "refusal, never a side channel",
                              "reference a target from the caller's own library at an "
                              "existing revision (query.py list-* / get-*)")


def _nte_ref_stmts(note_id: str, revision: int, refs: list, owner, actor, client_id,
                   idem_key, body_hash) -> list:
    """The per-revision reference INSERTs — they ride the SAME transaction
    as the note revision (one whole-command effect: content and references
    commit together or not at all; the crash matrix's zero-or-one contract)."""
    ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
    return [f"INSERT INTO arv.note_reference (id, note_id, note_revision, ref_kind, ref_id, "
            f"ref_revision, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
            f"VALUES ({_q(ids.new_id())}, {_q(note_id)}, {revision}, {_q(kind)}, {_q(target)}, "
            f"{rev if rev is not None else 'NULL'}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, "
            f"{_q(ih)}, {_q(idem_key)}, {_q(ts)});" for kind, target, rev in refs]


# ------------------------------------------------- P4-E slice one: the scoped agent access (CLAIM-077; record 69 §2)

def _agt_label(label: str) -> str:
    """The label law (the 0017 name-law convention): the owner's own name for
    the credential — 1..128 chars, no NULs; refused ARV-AGT-003, never
    clamped, never truncated."""
    if label is None or not (1 <= len(label) <= 128) or "\x00" in label:
        raise _CapRefusal("ARV-AGT-003",
                          f"the credential label {label!r} is not a valid label — 1..128 "
                          "characters, no NULs (the owner's own name for the credential, "
                          "never clamped, never truncated)",
                          "supply a label of 1..128 characters without NULs")
    return label


def mint_agent_credential(*, db, owner, actor, client_id, idem_key, label,
                          crash_at: str = None) -> int:
    """P4-E slice one (CLAIM-077; record 69 §2): the owner-minted scoped agent
    credential — the authorization primitive of the PLAN 4E row. The token
    VALUE: 32 bytes of secrets-quality randomness, urlsafe-encoded, shown
    EXACTLY ONCE in this command's first ack (the password-reset convention);
    ONLY the sha256 is stored (the value never persisted, never logged). The
    replay (the same key + the same body) returns the recorded result_ref and
    NO token line — the spine's replay path never re-runs build. The token is
    NOT part of the canonical body (it is the EFFECT of the mint, never the
    request). NO outbox ride: the credential is a LOCAL access primitive,
    never owner content to replicate (the design decision at record 69 §2)."""
    try:
        label_c = _agt_label(label)
    except _CapRefusal as r:
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    # LAW-24: the randomness lives in the adapters (ids.new_agent_token — the
    # argv-safe first character constrained there, the F-074-1 class caught
    # live by this slice's own measured set)
    token = ids.new_agent_token()
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    payload = json.dumps({"label": label_c}, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        cred_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.agent_credential (id, owner_scope, label, "
                 f"token_hash, scopes, actor, run_id, input_hash, idempotency_key, "
                 f"created_at) VALUES ({_q(cred_id)}, {_q(owner)}, {_q(label_c)}, "
                 f"{_q(token_hash)}, 'read', {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)});"]
        return cred_id, stmts, f" token={token} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id,
                  idem_key=idem_key, command="mint_agent_credential",
                  payload=payload, build=build, crash_at=crash_at)


def revoke_agent_credential(*, db, owner, actor, client_id, idem_key, id_,
                            crash_at: str = None) -> int:
    """The revocation: the ONE-WAY transition (revoked_at NULL -> set, never
    unset — the 0019 guard is the substrate law, this command the typed
    surface). The absent and cross-owner credentials are the SAME no-oracle
    refusal (ARV-AGT-001 — never a side channel); the already-revoked refuses
    the alternation (ARV-AGT-004, the guard's own code). The read log is
    NEVER touched — the audit history is append-only evidence, preserved
    across the revocation."""
    payload = json.dumps({"id": id_}, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        row = _sess_row(sess, f"SELECT (revoked_at IS NOT NULL)::int || '|' FROM "
                              f"arv.agent_credential WHERE id={_q(id_)} "
                              f"AND owner_scope={_q(owner)};")
        if not row:
            raise _CapRefusal("ARV-AGT-001",
                              f"the credential {id_} does not grant access in the "
                              "caller's scope — absent, another owner's, and already "
                              "revoked are the SAME refusal, never a side channel",
                              "revoke one of the caller's own credentials "
                              "(the audit read names them); the credential id comes "
                              "from the mint ack's result_ref")
        if row.split("|")[0] == "1":
            raise _CapRefusal("ARV-AGT-004",
                              f"the credential {id_} is already revoked — the "
                              "revocation is final (mint a new credential if access "
                              "is wanted again)",
                              "a revoked credential stays revoked; mint a new one "
                              "for renewed access")
        ts = clock.now()
        stmts = [f"UPDATE arv.agent_credential SET revoked_at={_q(ts)} "
                 f"WHERE id={_q(id_)} AND owner_scope={_q(owner)};"]
        return id_, stmts, " durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id,
                  idem_key=idem_key, command="revoke_agent_credential",
                  payload=payload, build=build, crash_at=crash_at)


# ------------------------------------------------- P3-07: the keyword index (RTM §2.5 findability)

_KWR_CJK = re.compile(r"[\u4e00-\u9fff]")


def _kwr_tokens(text: str) -> list:
    """P3-07: the tokenizer — case-folded UNICODE word tokens ([not-word-chars-excluded] under
    re.UNICODE: Latin, Greek, Cyrillic, accented forms, digits — every script
    Python's word class carries), each CJK character ADDITIONALLY as a
    single-character token AND the containing CJK run as its own token (a
    single-character or a whole-run CJK query both find the text); the
    word-boundary law: whole tokens only, never a prefix match. DEDUPLICATED
    per document (the index is a set)."""
    out: set = set()
    for run in re.findall(r"[^\W_]+", (text or "").casefold(), re.UNICODE):
        out.add(run)
        out.update(_KWR_CJK.findall(run))
    return sorted(out)


def _kwr_provenance(texts: list) -> tuple:
    """SYS-07: the index row's processing/input provenance — the extractor
    identity, its config, and the indexed text's digest (the 0006
    extraction-generation convention applied to the keyword rung)."""
    joined = "\n".join(texts)
    return ("kwr-tokenizer", "unicode-word+cjk-single",
            hashlib.sha256(joined.encode("utf-8", "surrogateescape")).hexdigest())


def _kwr_index_stmts(owner: str, kind: str, entity_id: str, revision: int,
                     texts: list, ts: str) -> list:
    """The index maintenance for ONE entity: replace its rows (DELETE the
    entity's tokens, INSERT the new set). The statements ride the SAME
    transaction as the capture (the explicit-lag contract: a committed
    capture is searchable immediately; a refused capture leaves zero rows —
    one transactional effect, never a partial)."""
    toks = set()
    for tx in texts:
        toks.update(_kwr_tokens(tx))
    extractor, config, digest = _kwr_provenance(texts)
    stmts = [f"DELETE FROM arv.keyword_index WHERE owner_scope={_q(owner)} "
             f"AND kind={_q(kind)} AND entity_id={_q(entity_id)};"]
    stmts += [f"INSERT INTO arv.keyword_index (owner_scope, kind, entity_id, revision, "
              f"token, extractor, extractor_config, input_digest, created_at) VALUES "
              f"({_q(owner)}, {_q(kind)}, {_q(entity_id)}, {revision}, {_q(tk)}, "
              f"{_q(extractor)}, {_q(config)}, {_q(digest)}, {_q(ts)});" for tk in sorted(toks)]
    return stmts


def _kwr_rebuild_stmts(sess: "Session", owner: str, ts: str) -> list:
    """The rebuild: re-derive the OWNER's whole index from the authored rows
    alone (the acceptance pin — delete/rebuild restores expected results).
    The searchable set: the sources' extracted passages (the CURRENT
    generation per source), the highlights' selected text + anchor windows,
    the bookmarks' anchor windows + spans, the notes' current-revision
    content. Tombstoned captures are indexed AND filtered at query time
    (the parity join — the index never governs visibility)."""
    stmts = [f"DELETE FROM arv.keyword_index WHERE owner_scope={_q(owner)};"]
    # sources: the FULL decoded text re-read from the verified blob (the same
    # text the import indexed — the findability rung indexes the source as
    # imported, the passage-level granularity is the extraction slice's own)
    # P4-A slice three (CLAIM-067): the rebuild reads the media type too — the
    # ONE read_text home (the epub's derived view re-derives identically)
    for row in _sess_rows(sess,
            f"SELECT id || '|' || media_type || '|' || digest FROM arv.source "
            f"WHERE owner_scope={_q(owner)} ORDER BY id;"):
        sid, mt, digest = row.split("|", 2)
        try:
            text = read_text(mt, digest)
        except (UnicodeDecodeError, KeyError, _FmtRefusal):
            text = ""  # the non-text boundary: not indexed, never a rebuild refusal
        stmts += _kwr_index_stmts(owner, "source", sid, 1, [text], ts)
# highlights: the current revision's selected text + the anchor windows
    # (row_to_json: the windows carry raw newlines — the pipe-delimited form
    # fragments on them, the #89/#90/#91 ANC-10 lesson)
    for row in _sess_rows(sess,
            f"SELECT row_to_json(t)::text || '|' FROM (SELECT h.id, h.revision, "
            f"h.selected_text, a.context_before, a.context_after "
            f"FROM arv.highlight h JOIN arv.anchor a ON a.id = h.anchor_id "
            f"WHERE h.owner_scope={_q(owner)} AND h.revision = (SELECT MAX(h2.revision) "
            f"FROM arv.highlight h2 WHERE h2.id = h.id AND h2.owner_scope={_q(owner)}) "
            f"ORDER BY h.id) t;"):
        jr = json.loads(row.rsplit("|", 1)[0])
        stmts += _kwr_index_stmts(owner, "highlight", jr["id"], int(jr["revision"]),
                                  [jr["selected_text"], jr["context_before"],
                                   jr["context_after"]], ts)
# bookmarks: the current revision's anchor windows + the span re-derived
    # from the anchor's OWN source digest + offsets through the verified blob
    # (fully re-derivable WITHOUT the extraction state — the anchor row is
    # the location evidence; row_to_json for the newline law)
    for row in _sess_rows(sess,
            f"SELECT row_to_json(t)::text || '|' FROM (SELECT b.id, b.revision, "
            f"a.context_before, a.context_after, a.source_digest, "
            f"a.start_off AS a_start, a.end_off AS a_end, s.media_type "
            f"FROM arv.bookmark b "
            f"JOIN arv.anchor a ON a.id = b.anchor_id "
            f"JOIN arv.source s ON s.id = a.source_id AND s.owner_scope = a.owner_scope "
            f"WHERE b.owner_scope={_q(owner)} AND b.revision = (SELECT MAX(b2.revision) "
            f"FROM arv.bookmark b2 WHERE b2.id = b.id "
            f"AND b2.owner_scope={_q(owner)}) ORDER BY b.id) t;"):
        jr = json.loads(row.rsplit("|", 1)[0])
        try:
            # the SEV round-1 P1 repair (CLAIM-067): the anchor's source digest
            # read WITH its media type through the ONE read_text home — an
            # epub-anchored bookmark's span re-derives exactly like every other
            # text-access site (the raw decode SILENTLY VANISHED it from
            # search after the rebuild)
            src_text = read_text(jr["media_type"], jr["source_digest"])
        except (UnicodeDecodeError, KeyError, _FmtRefusal):
            src_text = ""
        span = src_text[jr["a_start"]:jr["a_end"]]
        stmts += _kwr_index_stmts(owner, "bookmark", jr["id"], int(jr["revision"]),
                                  [span, jr["context_before"], jr["context_after"]], ts)


    # notes: the current revision's authored content (row_to_json: the
    # long-form content carries raw newlines — the same framing law)
    for row in _sess_rows(sess,
            f"SELECT row_to_json(t)::text || '|' FROM (SELECT n.id, n.revision, "
            f"n.content FROM arv.note n "
            f"WHERE n.owner_scope={_q(owner)} AND n.revision = (SELECT MAX(n2.revision) "
            f"FROM arv.note n2 WHERE n2.id = n.id AND n2.owner_scope={_q(owner)}) "
            f"ORDER BY n.id) t;"):
        jr = json.loads(row.rsplit("|", 1)[0])
        stmts += _kwr_index_stmts(owner, "note", jr["id"], int(jr["revision"]),
                                  [jr["content"]], ts)
    return stmts


def rebuild_keyword_index(*, db, owner, actor, client_id, idem_key,
                         crash_at: str = None) -> int:
    """P3-07's rebuild command: re-derive the caller's whole keyword index
    from the authored rows alone (the acceptance: delete/rebuild restores
    expected results — the index is a derived, rebuildable layer, never an
    authority). Idempotent by construction (the full delete + re-derive);
    the spine's command-log row records the run."""
    body = json.dumps({"owner": owner}, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        ts = clock.now()
        stmts = _kwr_rebuild_stmts(sess, owner, ts)
        # the run's identity ref (command_log.result_ref carries each family's
        # address form — a uuid text for entity commands, <source>@<ordinal>
        # for positions, TEXT since 0014; the owner name is NOT a valid ref;
        # the rebuild owns no entity, its ref is the run itself)
        return ids.new_id(), stmts, " index=rebuilt durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="rebuild_keyword_index", payload=body, build=build, crash_at=crash_at)


def create_note(*, db, owner, actor, client_id, idem_key, content=None,
                content_file=None, refs=None, crash_at: str = None) -> int:
    """P3-06 (RTM §2.5 item 7): the deep owner-authored Note — a fresh
    identity + revision 1 + the authored long-form content + the explicit
    version-aware reference set. Free-standing by construction (zero
    references is legal — NO source binding exists on the row); the content
    is read LOSSLESSLY (read_bytes + UTF-8 decode, no newline translation);
    every target validated in the caller's scope BEFORE any write (the
    referenced rows are immutable, so the pre-BEGIN validation cannot be
    invalidated by a race; the 0010 substrate guard is the hostile-write
    backstop)."""
    try:
        body_content = _nte_content(content=content, content_file=content_file)
        refs_c = _nte_refs(refs)
    except _CapRefusal as r:  # the parse precedes the spine (the body hash needs the canonical form)
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    body = _nte_body(body_content, refs=refs_c)

    def build(sess: "Session", body_hash: str):
        _nte_check_targets(sess, refs_c)
        note_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
                 f"input_hash, idempotency_key, created_at) VALUES ({_q(note_id)}, 1, "
                 f"{_q(body_content)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)});"] + \
            _nte_ref_stmts(note_id, 1, refs_c, owner, actor, client_id, idem_key, body_hash) + \
            _kwr_index_stmts(owner, "note", note_id, 1, [body_content], ts)
        return note_id, stmts, " revision=1 durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="create_note", payload=body, build=build, crash_at=crash_at)


def revise_note(*, db, owner, actor, client_id, idem_key, id_, content=None,
                content_file=None, refs=None, crash_at: str = None) -> int:
    """§3.3's edit transition for the note: append a NEW immutable revision
    (n+1) carrying its OWN full content AND reference set (replacement
    semantics — the prior revision's rows and references stay untouched and
    accurate). THE SERIALIZED TRANSITION (the #90 round-3 lesson applied from
    the start): the complete transition — the per-note advisory xact lock (the
    SAME lock the 0009 guards take) acquired as the transaction's FIRST
    statement, then the state read, the active validation, the inserts, and
    the commit, ALL inside ONE transaction: competing revisers serialize
    (both revisions persist, legal ordering — never a silent overwrite) and a
    tombstone either commits BEFORE the lock (the read sees it — the clean
    ARV-NTE-002) or waits for this transaction's end — a revision can never
    commit after tombstoning."""
    try:
        body_content = _nte_content(content=content, content_file=content_file)
        refs_c = _nte_refs(refs)
    except _CapRefusal as r:  # the parse precedes the spine (the body hash needs the canonical form)
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    body = _nte_body(body_content, note_id=_nte_canon_id(id_), refs=refs_c)  # the target id in the body: a different note is a different command (LAW-23)

    def build_txn(sess: "Session", body_hash: str):
        # THE CANONICAL LOCK KEY (the review round's F3 + the round-2 finding
        # 4439931169, claim-055 F5's class closed for the note family): the
        # substrate guards lock on hashtext(NEW.id::text) — the uuid type's
        # TEXT rendering is canonical — so the boundary lock must take the
        # SAME key whatever the CLI spelling, never a second lock for one note
        key = _nte_canon_id(id_)
        _sess_row(sess, f"SELECT hashtext({_q(key)}) || '|' || pg_advisory_xact_lock(hashtext({_q(key)}));")  # the lock FIRST, held to the commit
        revision, state = _nte_current(sess, id_)
        if state != "active":
            raise _CapRefusal("ARV-NTE-002",
                              f"note {id_} is tombstoned — a tombstoned note is hidden "
                              "from ordinary use until restored (RTM §3.3: restore precedes edit)",
                              "restore the note first (commands.py restore_note); the "
                              "governed history retains every revision meanwhile")
        _nte_check_targets(sess, refs_c)
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
                 f"input_hash, idempotency_key, created_at) VALUES ({_q(id_)}, {revision + 1}, "
                 f"{_q(body_content)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)});"] + \
            _nte_ref_stmts(id_, revision + 1, refs_c, owner, actor, client_id, idem_key, body_hash) + \
            _kwr_index_stmts(owner, "note", id_, revision + 1, [body_content], ts)
        return id_, stmts, f" revision={revision + 1} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="revise_note", payload=body, build_txn=build_txn, crash_at=crash_at)


def _nte_lifecycle_command(*, command, event, db, owner, actor, client_id, idem_key,
                           id_, crash_at, refusal_code, refusal_msg, refusal_repair) -> int:
    """§3.3's tombstone/restore transitions: ONE typed lifecycle EVENT row per
    LAWFUL transition (append-only, owner-scoped, provenance-complete). THE
    SERIALIZED + TIME-HONEST FORM (the review round's F1): the complete
    transition — the per-note advisory xact lock (the canonical lowercase key,
    the SAME lock the 0009 guards take) acquired as the transaction's FIRST
    statement, then the state read, the alternation validation, the timestamp
    (taken INSIDE the locked section, so a lifecycle event can never render
    before a revision that committed first), the insert, and the commit, ALL
    inside ONE transaction: a concurrent reviser commits BEFORE the lock (the
    read sees it) or waits for this transaction's end — the history arm's
    created_at ordering follows the serialized commit order. The substrate's
    advisory-lock alternation trigger (0009) remains the hostile backstop."""
    body = json.dumps({"id": _nte_canon_id(id_)}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build_txn(sess: "Session", body_hash: str):
        key = _nte_canon_id(id_)
        _sess_row(sess, f"SELECT hashtext({_q(key)}) || '|' || pg_advisory_xact_lock(hashtext({_q(key)}));")  # the lock FIRST, held to the commit
        _, state = _nte_current(sess, id_)
        if (event == "tombstone" and state != "active") or (event == "restore" and state != "tombstoned"):
            raise _CapRefusal(refusal_code, refusal_msg(id_), refusal_repair)
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]  # ts INSIDE the locked section
        stmts = [f"INSERT INTO arv.note_lifecycle (id, note_id, event, owner_scope, actor, "
                 f"run_id, input_hash, idempotency_key, created_at) VALUES ({_q(ids.new_id())}, "
                 f"{_q(id_)}, {_q(event)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)});"]
        return id_, stmts, " durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command=command, payload=body, build_txn=build_txn, crash_at=crash_at)


def tombstone_note(*, db, owner, actor, client_id, idem_key, id_, crash_at: str = None) -> int:
    """§3.3's delete transition: tombstoned — hidden from ordinary retrieval
    (get/list), the governed history (content, references, events) retained;
    recoverable by restore."""
    return _nte_lifecycle_command(
        command="tombstone_note", event="tombstone", db=db, owner=owner, actor=actor,
        client_id=client_id, idem_key=idem_key, id_=id_, crash_at=crash_at,
        refusal_code="ARV-NTE-004",
        refusal_msg=lambda i: (f"note {i} is already tombstoned — the §3.3 alternation "
                               "(tombstone only from active; the current view is DERIVED from "
                               "the events, never a state column)"),
        refusal_repair="restore the note first (commands.py restore_note); a second "
                       "tombstone is a no-op refused with its named code, never a second "
                       "event row")


def restore_note(*, db, owner, actor, client_id, idem_key, id_, crash_at: str = None) -> int:
    """§3.3's restore transition: tombstoned -> active (the current revision
    unchanged — the revisions were never touched)."""
    return _nte_lifecycle_command(
        command="restore_note", event="restore", db=db, owner=owner, actor=actor,
        client_id=client_id, idem_key=idem_key, id_=id_, crash_at=crash_at,
        refusal_code="ARV-NTE-005",
        refusal_msg=lambda i: (f"note {i} is not tombstoned — the §3.3 alternation "
                               "(restore only from tombstoned)"),
        refusal_repair="nothing to restore: the note is active in ordinary retrieval; "
                       "a tombstone precedes every restore")


def _extract_source(**kwargs):
    """P3-03a (CLAIM-052): the extraction command — the derived-build path lives
    in harness/extract.py as its own module (§2.9's boundary made structural: NO
    command_log row; the generation row IS the idempotency record). Imported at
    CALL time: extract.py imports this module's spine pieces (Session, _q,
    _sess_row, canonical_body, _dead_exit) at ITS module level, so a module-level
    import here would be circular in the extract-first load order."""
    from harness.extract import extract_source
    return extract_source(**kwargs)


# P4-C slice three (CLAIM-072; record 64 §2): the journal/blocks surface —
# the writing lab. The closed kind vocabulary (the 0015 D-010 pattern: the
# substrate CHECK below the command, the command's typed refusal above it).
_JNL_KINDS = ("raw", "creative")


def _jnl_kind(kind: str) -> str:
    """The writing lab's closed vocabulary: raw (the raw thinking) | creative
    (the creative writing) — never clamped, never a silent default."""
    if kind not in _JNL_KINDS:
        raise _CapRefusal("ARV-JNL-002",
                          f"the journal block kind {kind!r} is not in the writing lab's "
                          "closed vocabulary (raw | creative) — the kind is the block's "
                          "own class, never clamped",
                          "pass --kind raw (the raw thinking) or --kind creative (the "
                          "creative writing); a 'summary'/'note'-shaped kind is exactly "
                          "the forced funnel this surface refuses")
    return kind


def _jnl_content(*, content: "str | None", file: "str | None") -> str:
    """The journal's content channels: exactly one of --content / --file (the
    NTE-010 channel-law class, the journal's own code); the file read
    LOSSLESSLY (read_bytes + UTF-8 decode — no newline translation, no
    trimming — the long raw thinking arrives whole); the empty body and the
    NUL-carrying body refused (a block is writing, never a placeholder)."""
    if (content is None) == (file is None):
        raise _CapRefusal("ARV-JNL-003",
                          "exactly one of --content / --file is required — the journal "
                          "body must arrive through one named channel",
                          "pass --file for the long-form thinking surface (read "
                          "losslessly), or --content for an inline body; never both, "
                          "never neither")
    try:
        body = content if content is not None else \
            pathlib.Path(file).read_bytes().decode("utf-8")
    except FileNotFoundError:
        raise _CapRefusal("ARV-JNL-003",
                          f"the content file {file!r} does not exist — the journal body "
                          "cannot be read",
                          "supply an existing readable file path")
    except (IsADirectoryError, PermissionError, OSError) as e:
        raise _CapRefusal("ARV-JNL-003", f"the content file cannot be read — {e}",
                          "supply an existing readable file path")
    except UnicodeDecodeError:
        raise _CapRefusal("ARV-JNL-003",
                          "the content file is not valid UTF-8 — the journal preserves "
                          "the owner's thinking losslessly and refuses a lossy "
                          "interpretation",
                          "supply valid UTF-8; binary formats are their own slices")
    if not body:
        raise _CapRefusal("ARV-JNL-004",
                          "the journal body is empty — a block is writing, never a "
                          "placeholder",
                          "pass the body through --file or --content; an empty block "
                          "is refused, never stored")
    if "\x00" in body:
        raise _CapRefusal("ARV-JNL-004",
                          "the journal body contains NUL (U+0000) — PostgreSQL TEXT "
                          "cannot carry it losslessly, and the journal never rewrites "
                          "the owner's thinking",
                          "remove the NUL bytes; the lossless law refuses a silent "
                          "substitution")
    return body


def _jnl_refusal(code: str, block_id: str) -> _CapRefusal:
    """The journal-family boundary refusal — absent and another owner's are
    the SAME refusal, never a side channel (RTM §2.10 on the write path)."""
    return _CapRefusal(code, f"journal block {block_id} does not exist in the caller's "
                       "scope — absent and another owner's are the SAME refusal, never "
                       "a side channel",
                       "check the id against the caller's own journal listing "
                       "(query.py list-journal); a block is only ever addressable by "
                       "its owner")


def _jnl_current(sess: "Session", block_id: str) -> int:
    """One read: the current (max) revision — None when the block is absent
    from the caller's scope (RLS makes absent and cross-owner the same
    no-row; the no-oracle rides the caller's own refusal)."""
    row = _sess_row(sess, f"SELECT revision || '|' FROM arv.journal_block "
                    f"WHERE id = {_q(block_id)} ORDER BY revision DESC LIMIT 1;")
    if not row:
        raise _jnl_refusal("ARV-JNL-001", block_id)
    return int(row.split("|")[0])


def _jnl_check_source(sess: "Session", source_id: "str | None", owner: str) -> None:
    """THE SOURCE-OPTIONAL LAW's honest boundary: a binding is OPTIONAL (None
    is a first-class sourceless block) but a BOUND block's source must exist
    in the caller's scope — absent and cross-owner the SAME refusal (the
    no-oracle at the binding; the source row is immutable so the pre-BEGIN
    validation cannot be invalidated by a race)."""
    if source_id is None:
        return
    n = _sess_row(sess, f"SELECT count(*) || '|' FROM arv.source "
                  f"WHERE id = {_q(source_id)} AND owner_scope = {_q(owner)};")
    if not n or int(n.split("|")[0]) == 0:
        raise _CapRefusal("ARV-JNL-005",
                          f"the bound block's source {source_id} does not exist in the "
                          "caller's scope — absent and another owner's are the SAME "
                          "refusal, never a side channel",
                          "the source binding is OPTIONAL (omit --source-id for a "
                          "sourceless block — a first-class journal row); a bound "
                          "block names one of the caller's own sources "
                          "(query.py list-library)")


def journal_block(*, db, owner, actor, client_id, idem_key, kind,
                  content=None, file=None, source_id=None, crash_at: str = None) -> int:
    """P4-C slice three (CLAIM-072; record 64 §2): the writing lab's write —
    a fresh journal block identity + revision 1 + the authored body (the
    LONG raw thinking preserved LOSSLESSLY — never a truncated or funneled
    form) + the OPTIONAL source binding. The no-forced-funnel law lives
    here: the write never touches arv.note (the note machine stays its own
    surface — no silent conversion either way)."""
    try:
        kind_c = _jnl_kind(kind)
        body_content = _jnl_content(content=content, file=file)
    except _CapRefusal as r:  # the parse precedes the spine (the body hash needs the canonical form)
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    payload = {"kind": kind_c, "content": body_content}
    if source_id is not None:
        payload["source_id"] = source_id
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        _jnl_check_source(sess, source_id, owner)
        block_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.journal_block (id, revision, kind, content, "
                 f"source_id, owner_scope, actor, run_id, input_hash, idempotency_key, "
                 f"created_at) VALUES ({_q(block_id)}, 1, {_q(kind_c)}, "
                 f"{_q(body_content)}, {_qn(source_id)}, {_q(owner)}, {_q(actor)}, "
                 f"{_q(run_id)}, {_q(ih)}, {_q(idem_key)}, {_q(ts)});"]
        return f"{block_id}@1", stmts, " revision=1 durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="journal_block", payload=body, build=build, crash_at=crash_at)


def revise_journal_block(*, db, owner, actor, client_id, idem_key, id_,
                         content=None, file=None, crash_at: str = None) -> int:
    """The writing lab's edit transition: append a NEW immutable revision
    (n+1) carrying its OWN full body (replacement semantics — the prior
    revision's row stays untouched and accurate; the governed history). THE
    SERIALIZED TRANSITION (the 0009 pattern): the per-block advisory xact
    lock (the SAME lock the 0016 guard takes) acquired as the transaction's
    FIRST statement, then the state read, the insert, and the commit, ALL
    inside ONE transaction — competing revisers serialize (both revisions
    persist, legal ordering — never a silent overwrite)."""
    try:
        body_content = _jnl_content(content=content, file=file)
    except _CapRefusal as r:
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    payload = {"id": _nte_canon_id(id_), "content": body_content}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build_txn(sess: "Session", body_hash: str):
        # THE CANONICAL LOCK KEY (the note family's F3 form): the substrate
        # guard locks on hashtext(NEW.id::text) — the uuid TEXT rendering is
        # canonical — so the boundary lock takes the SAME key whatever the
        # CLI spelling, never a second lock for one block
        key = _nte_canon_id(id_)
        _sess_row(sess, f"SELECT hashtext({_q(key)}) || '|' || pg_advisory_xact_lock(hashtext({_q(key)}));")  # the lock FIRST, held to the commit
        revision = _jnl_current(sess, id_)
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.journal_block (id, revision, kind, content, "
                 f"source_id, owner_scope, actor, run_id, input_hash, idempotency_key, "
                 f"created_at) SELECT {_q(id_)}, {revision + 1}, kind, {_q(body_content)}, "
                 f"source_id, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                 f"{_q(idem_key)}, {_q(ts)} FROM arv.journal_block "
                 f"WHERE id = {_q(id_)} AND revision = {revision};"]
        return f"{id_}@{revision + 1}", stmts, f" revision={revision + 1} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="revise_journal_block", payload=body, build_txn=build_txn,
                  crash_at=crash_at)


def _rls_name(name: str) -> str:
    """The name law (ARV-RLS-003): the owner's own label, 1..512 chars, no
    NULs — refused, never clamped, never silently defaulted."""
    if not (1 <= len(name) <= 512):
        raise _CapRefusal("ARV-RLS-003",
                          f"the list name length {len(name)} is outside 1..512 — the "
                          "name is the owner's own label, bounded, never clamped",
                          "pass a name of 1..512 characters")
    if "\x00" in name:
        raise _CapRefusal("ARV-RLS-003",
                          "the list name contains NUL (U+0000) — PostgreSQL TEXT "
                          "cannot carry it losslessly, and the list never rewrites "
                          "the owner's label",
                          "remove the NUL bytes; the lossless law refuses a silent "
                          "substitution")
    return name


def _rls_check_list(sess: "Session", list_id: str, owner: str) -> None:
    """THE NO-ORACLE (ARV-RLS-001): absent and another owner's list are the
    SAME refusal, never a side channel (the RTM §2.10 law on the write
    path; the list row is immutable so the in-transaction check cannot be
    invalidated by a race)."""
    n = _sess_row(sess, f"SELECT count(*) || '|' FROM arv.reading_list "
                  f"WHERE id = {_q(list_id)} AND owner_scope = {_q(owner)};")
    if not n or int(n.split("|")[0]) == 0:
        raise _CapRefusal("ARV-RLS-001",
                          f"the reading list {list_id} does not exist in the caller's "
                          "scope — absent and another owner's are the SAME refusal, "
                          "never a side channel",
                          "check the id against the caller's own list-lists answer; a "
                          "list is only ever addressable by its owner")


def _rls_check_source(sess: "Session", source_id: str, owner: str) -> None:
    """THE NO-ORACLE AT THE MEMBERSHIP (ARV-RLS-002): the member source must
    exist in the caller's scope — absent and another owner's the SAME
    refusal (the 0016 source-bind law's shape, REQUIRED here: the list
    membership is never source-optional)."""
    n = _sess_row(sess, f"SELECT count(*) || '|' FROM arv.source "
                  f"WHERE id = {_q(source_id)} AND owner_scope = {_q(owner)};")
    if not n or int(n.split("|")[0]) == 0:
        raise _CapRefusal("ARV-RLS-002",
                          f"the member source {source_id} does not exist in the "
                          "caller's scope — absent and another owner's are the SAME "
                          "refusal, never a side channel",
                          "check the id against the caller's own list-library answer; "
                          "a membership names one of the caller's own sources")


def _rls_event(*, db, owner, actor, client_id, idem_key, list_id, source_id,
               op, command, crash_at: str = None) -> int:
    """The membership event write (CLAIM-074; record 66 §2): ONE append-only
    event row ('added' or 'removed') — the current membership is DERIVED
    (the last op per pair wins), the event rows are the recovery substrate
    (RTM §2 item 9: every add/remove retained, never a destructive delete).
    The alternation law lives at the substrate (ARV-RLS-008, the guard under
    the per-pair advisory lock); the command's own idempotency (the spine's
    key semantics) never double-inserts — a same-key replay returns the
    recorded result, a different-body same-key refuses ARV-CMD-409."""
    payload = {"list": _nte_canon_id(list_id), "source": _nte_canon_id(source_id),
               "op": op}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        _rls_check_list(sess, _nte_canon_id(list_id), owner)
        _rls_check_source(sess, _nte_canon_id(source_id), owner)
        ev_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.reading_list_member (id, list_id, source_id, op, "
                 f"owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
                 f"VALUES ({_q(ev_id)}, {_q(_nte_canon_id(list_id))}, "
                 f"{_q(_nte_canon_id(source_id))}, {_q(op)}, {_q(owner)}, {_q(actor)}, "
                 f"{_q(run_id)}, {_q(ih)}, {_q(idem_key)}, {_q(ts)});"]
        return ev_id, stmts, " durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command=command, payload=body, build=build, crash_at=crash_at)


def create_reading_list(*, db, owner, actor, client_id, idem_key, name,
                        crash_at: str = None) -> int:
    """P4-C slice five (CLAIM-074; record 66 §2): the reading-list surface —
    the user-defined lists over the landed library (the North Star owner
    words' third surface). THE NAME LAW (ARV-RLS-003): 1..512, no NULs —
    the owner's own label, refused never clamped. THE IDENTITY LAW (Q11's
    baseline): the identity is the uuid, NEVER the name — two lists may
    share one name (no uniqueness, no auto-merge); the ack carries
    result_ref=<list-id> (the bare uuid, the create class)."""
    try:
        name_c = _rls_name(name)
    except _CapRefusal as r:  # the parse precedes the spine (the body hash needs the canonical form)
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    payload = {"name": name_c}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        list_id = ids.new_id()
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = [f"INSERT INTO arv.reading_list (id, name, owner_scope, actor, "
                 f"run_id, input_hash, idempotency_key, created_at) "
                 f"VALUES ({_q(list_id)}, {_q(name_c)}, {_q(owner)}, {_q(actor)}, "
                 f"{_q(run_id)}, {_q(ih)}, {_q(idem_key)}, {_q(ts)});"]
        return list_id, stmts, " durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="create_reading_list", payload=body, build=build,
                  crash_at=crash_at)


def add_to_list(*, db, owner, actor, client_id, idem_key, list_id, source_id,
                crash_at: str = None) -> int:
    """The membership add: ONE 'added' event row (append-only; the current
    view derives). See _rls_event for the whole contract."""
    return _rls_event(db=db, owner=owner, actor=actor, client_id=client_id,
                      idem_key=idem_key, list_id=list_id, source_id=source_id,
                      op="added", command="add_to_list", crash_at=crash_at)


def remove_from_list(*, db, owner, actor, client_id, idem_key, list_id, source_id,
                     crash_at: str = None) -> int:
    """The membership remove: ONE 'removed' event row (append-only; the
    current view derives — the history keeps the membership). See _rls_event
    for the whole contract."""
    return _rls_event(db=db, owner=owner, actor=actor, client_id=client_id,
                      idem_key=idem_key, list_id=list_id, source_id=source_id,
                      op="removed", command="remove_from_list", crash_at=crash_at)


def save_position(*, db, owner, actor, client_id, idem_key, source_id,
                  start, end, crash_at: str = None) -> int:
    """P4-A slice two (CLAIM-066; record 58 §2): the source-open/position
    surface — the reading-position contract on the EXISTING substrate.  The
    position rows are owner+source scoped, keyed to the CURRENT generation
    (THE SERVING-GENERATION FIELD: the position binds to the extraction
    generation the reader was reading — a re-extraction's answer is honest
    about which generation the position addresses, never a silent
    retarget).  Append-only saves (the bookmark revision shape); the read
    arm derives the last-saved position (max ordinal).  NO content column
    exists — the row is the owner's reading state, never a copy of source
    text.  THE SERIALIZED SAVE (the 0009/#90 pattern): the complete
    transition — the per-(owner, source) advisory xact lock (the SAME lock
    the 0014 guard takes), then the state read, the validation, the
    construction, and the commit, ALL inside ONE transaction — competing
    savers serialize (both saves persist, legal ordering) and the ordinal
    law holds by construction (max+1 under the lock)."""
    body = json.dumps({"source_id": source_id, "start": start, "end": end},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build_txn(sess: "Session", body_hash: str):
        key = owner + "|" + source_id
        _sess_row(sess, f"SELECT hashtext({_q(key)}) || '|' || pg_advisory_xact_lock(hashtext({_q(key)}));")  # the lock FIRST, held to the commit
        # ONE read: the source's digest + media type + the CURRENT generation
        # (the serving generation the new save binds; '' when none serves —
        # ARV-POS-002). P4-A slice three (CLAIM-067): the media type rides the
        # same ONE read — the position's offsets validate against the DERIVED
        # view (the ONE read_text home), never a second decode path
        row = _sess_row(sess, f"SELECT s.digest || '|' || s.media_type || '|' || COALESCE((SELECT g.id::text "
                              f"FROM arv.extraction_generation g WHERE g.source_id = s.id "
                              f"AND g.owner_scope = s.owner_scope AND g.state = 'current' "
                              f"ORDER BY g.ordinal DESC LIMIT 1), '') FROM arv.source s "
                              f"WHERE s.id = {_q(source_id)};")
        if not row:
            raise _CapRefusal("ARV-POS-001",
                              f"source {source_id} does not exist in the caller's scope — absent and "
                              "another owner's are the SAME refusal, never a side channel (RTM §2.10 "
                              "on the write path)",
                              "check the id against the caller's own sources (query.py get-source "
                              "reads the import ack's result_ref back); a position is only ever "
                              "saved by the source's owner")
        digest, media_type, gen_id = row.split("|", 2)
        if not gen_id:
            raise _CapRefusal("ARV-POS-002",
                              f"source {source_id} has no current extraction generation — the position "
                              "binds to the generation the reader was reading (the serving-generation "
                              "field); a source with no serving generation has no readable derived "
                              "view to position into",
                              "extract the source first (harness/extract.py extract_source); the "
                              "position save follows the serving generation")
        try:
            # P4-A slice three (CLAIM-067): the ONE read_text home — the epub's
            # derived view is the position's offset domain
            text = read_text(media_type, digest)
        except (KeyError, UnicodeDecodeError) as e:
            # the corrupt-blob class (one code, one home — the bookmark family's
            # own wording): the bytes cannot verify for the position's boundary
            raise _CapRefusal("ARV-CAP-004", f"the source's blob failed to verify — {e}",
                              "the store is corrupt at this digest; never a position against "
                              "unverifiable bytes")
        except _FmtRefusal as r:
            raise _CapRefusal("ARV-CAP-004", f"the source's derived text cannot be produced — {r}",
                              "the store's bytes changed under the digest (the corruption class); never a position against an underivable view")
        if not (0 <= start < end <= len(text)):
            raise _CapRefusal("ARV-POS-003",
                              f"offsets [{start},{end}) are invalid for a {len(text)}-character text — "
                              "never clamped, never guessed",
                              "supply 0 <= start < end <= the decoded text length (the derived "
                              "view's own coordinates)")
        nxt = _sess_row(sess, f"SELECT COALESCE(max(save_ordinal), 0) || '|' FROM "
                              f"arv.reading_position WHERE source_id = {_q(source_id)} "
                              f"AND owner_scope = {_q(owner)};")
        ordinal = int(nxt.rstrip("|") or "0") + 1
        pos_id, ts, run_id, ih = ids.new_id(), clock.now(), "run-" + client_id, body_hash[:16]
        stmt = (f"INSERT INTO arv.reading_position (id, owner_scope, source_id, save_ordinal, "
                f"generation_id, start_off, end_off, actor, run_id, input_hash, "
                f"idempotency_key, created_at) VALUES ({_q(pos_id)}, {_q(owner)}, "
                f"{_q(source_id)}, {ordinal}, {_q(gen_id)}, {start}, {end}, {_q(actor)}, "
                f"{_q(run_id)}, {_q(ih)}, {_q(idem_key)}, {_q(ts)});")
        return f"{source_id}@{ordinal}", [stmt], f" save={ordinal} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="save_position", payload=body, build_txn=build_txn, crash_at=crash_at)


# P4-C slice two (CLAIM-071; record 63 §2): D-010's APPROVED event vocabulary
# — the closed set of coarse behavior facts. Anything else (the D-010-named
# exclusions: keystroke/mouse-shaped payloads, search-query/agent-prompt
# event kinds) is REFUSED at the write boundary with the boundary named,
# never silently stored, never clamped into the vocabulary.
SESSION_EVENTS = ("session_start", "checkpoint", "dwell", "session_end")


def record_session(*, db, owner, actor, client_id, idem_key, source_id,
                   event, start, end, dwell_ms=None, crash_at: str = None) -> int:
    """P4-C slice two (CLAIM-071; record 63 §2): the session/dwell events
    surface — D-010's durable behavior data as the reading-session
    checkpoint events (the RTM §2.10 reservation).  THE CLOSED VOCABULARY:
    session_start | checkpoint | dwell | session_end — coarse behavior
    facts; an event kind outside the set refuses ARV-SES-004 WITH D-010
    NAMED (the boundary is the refusal, never a clamp, never a silent
    store).  THE SHAPE LAW (ARV-SES-005): a dwell event carries --dwell-ms
    (bounded 1..86400000 — a coarse measure); every other kind refuses it.
    THE NO-ORACLE (ARV-SES-001): absent and another owner's source are the
    SAME refusal.  THE SERVING-GENERATION BINDING (ARV-SES-002): an event
    positions into the derived view — never extracted means nothing to
    checkpoint into; the row records the CURRENT generation (the behavior
    history is provenance, never retargeted by a later re-extraction).  THE
    COARSE SPAN (ARV-SES-003): the offsets validate against the derived
    view's extent (the ONE read_text home — never a second decode path).
    THE SERIALIZED SAVE (the 0009/0014 pattern): the advisory lock, the
    state read, the validation, the construction, and the commit ALL inside
    ONE transaction; the ordinal law holds by construction (max+1 under the
    lock).  NO free-text argument exists — the row is coordinates + the
    coarse dwell, never captured input (the structural D-010 no-trace law)."""
    try:
        if event not in SESSION_EVENTS:
            raise _CapRefusal("ARV-SES-004",
                              f"event kind {event!r} is outside the approved session-event "
                              "vocabulary (session_start | checkpoint | dwell | session_end) — "
                              "D-010's boundary: durable behavior data is explicit actions + "
                              "reading sessions + coarse position/dwell; NO keystroke/mouse "
                              "traces, NO search-query or agent-prompt history (refused, never "
                              "stored, never clamped into the vocabulary)",
                              "record one of the approved kinds; input traces and query/prompt "
                              "histories are outside the durable-behavior contract by the "
                              "owner's D-010 decision")
        if event == "dwell":
            if dwell_ms is None or not (1 <= dwell_ms <= 86400000):
                raise _CapRefusal("ARV-SES-005",
                                  f"a dwell event requires --dwell-ms within 1..86400000 "
                                  f"(got {dwell_ms!r}) — the coarse dwell is the event's own "
                                  "fact, bounded to a day (never a fine-grained trace)",
                                  "supply --dwell-ms (milliseconds, 1..86400000) on dwell "
                                  "events only")
        elif dwell_ms is not None:
            raise _CapRefusal("ARV-SES-005",
                              f"--dwell-ms is carried only by dwell events (got event "
                              f"{event!r} with --dwell-ms {dwell_ms!r}) — the shape law: the "
                              "coarse dwell is the dwell event's own fact",
                              "drop --dwell-ms (only 'dwell' events carry it)")
    except _CapRefusal as r:  # the boundary check precedes the spine (the NTE parse precedent)
        print(f"FAIL {r.code}: {r}")
        print(f"      repair: {r.repair}")
        return 1
    body = json.dumps({"source_id": source_id, "event": event, "start": start,
                       "end": end, "dwell_ms": dwell_ms},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build_txn(sess: "Session", body_hash: str):
        key = owner + "|" + source_id
        _sess_row(sess, f"SELECT hashtext({_q(key)}) || '|' || pg_advisory_xact_lock(hashtext({_q(key)}));")  # the lock FIRST, held to the commit
        # ONE read: the source's digest + media type + the CURRENT generation
        # (the serving generation the new event binds; '' when none serves —
        # ARV-SES-002). The media type rides the same ONE read — the event's
        # offsets validate against the DERIVED view (the ONE read_text home)
        row = _sess_row(sess, f"SELECT s.digest || '|' || s.media_type || '|' || COALESCE((SELECT g.id::text "
                              f"FROM arv.extraction_generation g WHERE g.source_id = s.id "
                              f"AND g.owner_scope = s.owner_scope AND g.state = 'current' "
                              f"ORDER BY g.ordinal DESC LIMIT 1), '') FROM arv.source s "
                              f"WHERE s.id = {_q(source_id)};")
        if not row:
            raise _CapRefusal("ARV-SES-001",
                              f"source {source_id} does not exist in the caller's scope — absent and "
                              "another owner's are the SAME refusal, never a side channel (RTM §2.10 "
                              "on the write path)",
                              "check the id against the caller's own sources (query.py get-source "
                              "reads the import ack's result_ref back); a session event is only "
                              "ever recorded by the source's owner")
        digest, media_type, gen_id = row.split("|", 2)
        if not gen_id:
            raise _CapRefusal("ARV-SES-002",
                              f"source {source_id} has no current extraction generation — the session "
                              "event binds to the generation the reader was reading (the "
                              "serving-generation binding); a source with no serving generation has "
                              "no readable derived view to checkpoint into",
                              "extract the source first (harness/extract.py extract_source); the "
                              "session event follows the serving generation")
        try:
            # the ONE read_text home — the derived view is the event's offset domain
            text = read_text(media_type, digest)
        except (KeyError, UnicodeDecodeError) as e:
            raise _CapRefusal("ARV-CAP-004", f"the source's blob failed to verify — {e}",
                              "the store is corrupt at this digest; never a session event "
                              "against unverifiable bytes")
        except _FmtRefusal as r:
            raise _CapRefusal("ARV-CAP-004", f"the source's derived text cannot be produced — {r}",
                              "the store's bytes changed under the digest (the corruption class); never an event against an underivable view")
        if not (0 <= start < end <= len(text)):
            raise _CapRefusal("ARV-SES-003",
                              f"offsets [{start},{end}) are invalid for a {len(text)}-character text — "
                              "never clamped, never guessed",
                              "supply 0 <= start < end <= the decoded text length (the derived "
                              "view's own coordinates — the coarse span)")
        nxt = _sess_row(sess, f"SELECT COALESCE(max(event_ordinal), 0) || '|' FROM "
                              f"arv.reading_session WHERE source_id = {_q(source_id)} "
                              f"AND owner_scope = {_q(owner)};")
        ordinal = int(nxt.rstrip("|") or "0") + 1
        ev_id, ts, run_id, ih = ids.new_id(), clock.now(), "run-" + client_id, body_hash[:16]
        stmt = (f"INSERT INTO arv.reading_session (id, owner_scope, source_id, event, "
                f"event_ordinal, generation_id, start_off, end_off, dwell_ms, actor, run_id, "
                f"input_hash, idempotency_key, created_at) VALUES ({_q(ev_id)}, {_q(owner)}, "
                f"{_q(source_id)}, {_q(event)}, {ordinal}, {_q(gen_id)}, {start}, {end}, "
                f"{dwell_ms if dwell_ms is not None else 'NULL'}, {_q(actor)}, "
                f"{_q(run_id)}, {_q(ih)}, {_q(idem_key)}, {_q(ts)});")
        return f"{source_id}@{ordinal}", [stmt], f" events={ordinal} durability_rung=local_durable"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="record_session", payload=body, build_txn=build_txn, crash_at=crash_at)


REGISTRY = {"record_event": record_event, "import_source": import_source,
            "create_highlight": create_highlight, "extract_source": _extract_source,
            "revise_highlight": revise_highlight, "tombstone_highlight": tombstone_highlight,
            "restore_highlight": restore_highlight, "create_bookmark": create_bookmark,
            "mint_agent_credential": mint_agent_credential,
            "revoke_agent_credential": revoke_agent_credential,
            "move_bookmark": move_bookmark, "tombstone_bookmark": tombstone_bookmark,
            "restore_bookmark": restore_bookmark, "create_note": create_note,
            "revise_note": revise_note, "tombstone_note": tombstone_note,
            "rebuild_keyword_index": rebuild_keyword_index,
            "restore_note": restore_note, "save_position": save_position,
            "record_session": record_session}


def main() -> int:
    ap = argparse.ArgumentParser(description="the idempotent command path (S3 + P3-01: the first real product commands)")
    sub = ap.add_subparsers(dest="command", required=True)
    def _common(p):
        p.add_argument("--owner", required=True)
        p.add_argument("--actor", default="owner", choices=["owner", "runtime-agent", "worker", "model-decision"])
        p.add_argument("--client-id", required=True)
        p.add_argument("--idem-key", required=True)
    p = sub.add_parser("record_event")
    _common(p)
    p.add_argument("--payload", required=True)
    p = sub.add_parser("import_source")
    _common(p)
    p.add_argument("--title", default=None)
    p.add_argument("--work-id", default=None)
    p.add_argument("--file", required=True)
    p.add_argument("--media-type", default="text/plain")
    p.add_argument("--acquired-via", default="cli-import")
    p = sub.add_parser("create_highlight")
    _common(p)
    p.add_argument("--source-id", required=True)
    p.add_argument("--start", required=True, type=int)
    p.add_argument("--end", required=True, type=int)
    p = sub.add_parser("create_bookmark")
    _common(p)
    p.add_argument("--source-id", required=True)
    p.add_argument("--start", required=True, type=int)
    p.add_argument("--end", required=True, type=int)
    for name in ("revise_highlight", "tombstone_highlight", "restore_highlight"):
        p = sub.add_parser(name)
        _common(p)
        p.add_argument("--id", required=True)
        if name == "revise_highlight":
            p.add_argument("--start", required=True, type=int)
            p.add_argument("--end", required=True, type=int)
    for name in ("move_bookmark", "tombstone_bookmark", "restore_bookmark"):
        p = sub.add_parser(name)
        _common(p)
        p.add_argument("--id", required=True)
        if name == "move_bookmark":
            p.add_argument("--start", required=True, type=int)
            p.add_argument("--end", required=True, type=int)
    for name in ("create_note", "revise_note"):
        p = sub.add_parser(name)
        _common(p)
        p.add_argument("--content", default=None,
                       help="the authored content, inline (exactly one of --content / --content-file)")
        p.add_argument("--content-file", default=None,
                       help="the long-form authoring surface: a UTF-8 file read losslessly")
        p.add_argument("--ref", action="append", default=None, metavar="KIND:ID[@REV]",
                       help="an explicit version-aware reference (repeatable; highlight/note/"
                            "bookmark/journal_block MUST name the target revision, "
                            "work/source/anchor MUST NOT)")
        if name == "revise_note":
            p.add_argument("--id", required=True)
    p = sub.add_parser("rebuild_keyword_index")
    _common(p)
    for name in ("tombstone_note", "restore_note"):
        p = sub.add_parser(name)
        _common(p)
        p.add_argument("--id", required=True)
    p = sub.add_parser("save_position")
    _common(p)
    p.add_argument("--source-id", required=True)
    p.add_argument("--start", required=True, type=int,
                   help="the reading window's start offset (decoded-text coordinates)")
    p.add_argument("--end", required=True, type=int,
                   help="the reading window's end offset (0 <= start < end <= the text length)")
    p = sub.add_parser("record_session")
    _common(p)
    p.add_argument("--source-id", required=True)
    p.add_argument("--event", required=True,
                   help="the session-event kind (the D-010 closed vocabulary: session_start | "
                        "checkpoint | dwell | session_end — anything else refuses ARV-SES-004)")
    p.add_argument("--start", required=True, type=int,
                   help="the coarse span's start offset (decoded-text coordinates)")
    p.add_argument("--end", required=True, type=int,
                   help="the coarse span's end offset (0 <= start < end <= the text length)")
    p.add_argument("--dwell-ms", default=None, type=int,
                   help="the coarse dwell in milliseconds (dwell events only, 1..86400000)")
    # P4-E slice one (CLAIM-077): the scoped agent access — the credential
    # mint + the one-way revocation (the READ arms live in query.py; NO write
    # command ever accepts a token — READ-ONLY structural)
    p = sub.add_parser("mint_agent_credential")
    _common(p)
    p.add_argument("--label", required=True,
                   help="the owner's own name for the credential (1..128 chars, no NULs)")
    p = sub.add_parser("revoke_agent_credential")
    _common(p)
    p.add_argument("--id", required=True,
                   help="the credential id (the mint ack's result_ref)")
    # P4-C slice three (CLAIM-072): the writing lab — the journal/blocks surface
    for name in ("journal_block", "revise_journal_block"):
        p = sub.add_parser(name)
        _common(p)
        p.add_argument("--kind", required=(name == "journal_block"),
                       help="the writing lab's closed vocabulary: raw (the raw thinking) | "
                            "creative (the creative writing) — anything else refuses ARV-JNL-002")
        p.add_argument("--content", default=None,
                       help="the journal body, inline (exactly one of --content / --file)")
        p.add_argument("--file", default=None,
                       help="the long-form thinking surface: a UTF-8 file read losslessly "
                            "(the long raw thinking arrives whole, never truncated)")
        if name == "journal_block":
            p.add_argument("--source-id", default=None,
                           help="the OPTIONAL source binding (omit for a sourceless block — "
                                "a first-class journal row; a bound block names one of the "
                                "caller's own sources)")
        else:
            p.add_argument("--id", required=True)
    # P4-C slice five (CLAIM-074): the reading-list surface — the user-defined
    # lists over the landed library (the membership event writes)
    for name in ("create_reading_list", "add_to_list", "remove_from_list"):
        p = sub.add_parser(name)
        _common(p)
        if name == "create_reading_list":
            p.add_argument("--name", required=True,
                           help="the list's own label, 1..512 chars (the identity is the "
                                "uuid, NEVER the name — two lists may share one; the "
                                "name is immutable at this slice)")
        else:
            p.add_argument("--list", required=True,
                           help="the caller's own list id (absent/cross-owner refuses "
                                "ARV-RLS-001 — the no-oracle)")
            p.add_argument("--source", required=True,
                           help="the member source id (absent/cross-owner refuses "
                                "ARV-RLS-002 — the no-oracle at the binding)")
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    if a.command == "record_event":
        return record_event(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, payload=a.payload)
    if a.command == "import_source":
        return import_source(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                             idem_key=a.idem_key, title=a.title, work_id=a.work_id,
                             file=a.file, media_type=a.media_type,
                             acquired_via=a.acquired_via)
    if a.command == "revise_highlight":
        return revise_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                idem_key=a.idem_key, id_=a.id, start=a.start, end=a.end)
    if a.command == "tombstone_highlight":
        return tombstone_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                   idem_key=a.idem_key, id_=a.id)
    if a.command == "restore_highlight":
        return restore_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                  idem_key=a.idem_key, id_=a.id)
    if a.command == "create_bookmark":
        return create_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                               idem_key=a.idem_key, source_id=a.source_id,
                               start=a.start, end=a.end)
    if a.command == "move_bookmark":
        return move_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                             idem_key=a.idem_key, id_=a.id, start=a.start, end=a.end)
    if a.command == "tombstone_bookmark":
        return tombstone_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                  idem_key=a.idem_key, id_=a.id)
    if a.command == "restore_bookmark":
        return restore_bookmark(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                idem_key=a.idem_key, id_=a.id)
    if a.command == "create_note":
        return create_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, content=a.content,
                           content_file=a.content_file, refs=a.ref)
    if a.command == "revise_note":
        return revise_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, id_=a.id, content=a.content,
                           content_file=a.content_file, refs=a.ref)
    if a.command == "rebuild_keyword_index":
        return rebuild_keyword_index(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                     idem_key=a.idem_key)
    if a.command == "tombstone_note":
        return tombstone_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, id_=a.id)
    if a.command == "restore_note":
        return restore_note(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, id_=a.id)
    if a.command == "save_position":
        return save_position(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                             idem_key=a.idem_key, source_id=a.source_id,
                             start=a.start, end=a.end)
    if a.command == "record_session":
        return record_session(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                              idem_key=a.idem_key, source_id=a.source_id,
                              event=a.event, start=a.start, end=a.end, dwell_ms=a.dwell_ms)
    if a.command == "journal_block":
        # P4-C slice three (CLAIM-072): the writing lab's write
        return journal_block(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                             idem_key=a.idem_key, kind=a.kind, content=a.content,
                             file=a.file, source_id=a.source_id)
    if a.command == "revise_journal_block":
        return revise_journal_block(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                    idem_key=a.idem_key, id_=a.id, content=a.content,
                                    file=a.file)
    # P4-C slice five (CLAIM-074): the reading-list writes
    if a.command == "create_reading_list":
        return create_reading_list(db=db, owner=a.owner, actor=a.actor,
                                   client_id=a.client_id, idem_key=a.idem_key,
                                   name=a.name)
    if a.command == "add_to_list":
        return add_to_list(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                           idem_key=a.idem_key, list_id=a.list, source_id=a.source)
    if a.command == "remove_from_list":
        return remove_from_list(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                                idem_key=a.idem_key, list_id=a.list, source_id=a.source)
    # P4-E slice one (CLAIM-077): the scoped agent access — the credential
    # mint + the one-way revocation (READ-ONLY lives in query.py's arms)
    if a.command == "mint_agent_credential":
        return mint_agent_credential(db=db, owner=a.owner, actor=a.actor,
                                     client_id=a.client_id, idem_key=a.idem_key,
                                     label=a.label)
    if a.command == "revoke_agent_credential":
        return revoke_agent_credential(db=db, owner=a.owner, actor=a.actor,
                                       client_id=a.client_id, idem_key=a.idem_key,
                                       id_=a.id)
    return create_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, source_id=a.source_id,
                            start=a.start, end=a.end)


if __name__ == "__main__":
    sys.exit(main())
