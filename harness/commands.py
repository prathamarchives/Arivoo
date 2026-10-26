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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg, clock, ids, blob  # noqa: E402

MARK_CHECK = "MARK:CHECK"
MARK_BEGUN = "MARK:BEGUN"
MARK_INSERTS = "MARK:INSERTS_DONE"
MARK_COMMITTED = "MARK:COMMITTED"


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
        return ev_id, [stmt], ""

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


def _spine(*, db, owner, actor, client_id, idem_key, command, payload, build,
           crash_at: str = None) -> int:
    """The shared product-command protocol — the record_event spine generalized:
    replay check -> build (validation + ids + statements, BEFORE any write) ->
    BEGIN -> effects + command_log -> COMMIT -> ack.  Crash points sit between
    phases; the concurrent loser rides _replay_after_conflict (a unique
    constraint is not a replay promise, P3-K0).  build(sess, body_hash) returns
    (result_ref, statements, ack_extra); a _CapRefusal inside build prints the
    named code and leaves ZERO rows (the validation precedes the transaction)."""
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
            print(f"ACK command={command} idem_key={idem_key} status=replayed result_ref={recorded_ref}")
            return 0
        try:
            ref, stmts, extra = build(sess, body_hash)
        except _CapRefusal as r:
            print(f"FAIL {r.code}: {r}")
            print(f"      repair: {r.repair}")
            return 1
        ts = clock.now()
        stmts = stmts + [f"INSERT INTO arv.command_log (owner_scope, idempotency_key, client_id, command_name, body_hash, result_ref, actor, created_at) "
                         f"VALUES ({_q(owner)}, {_q(idem_key)}, {_q(client_id)}, {_q(command)}, {_q(body_hash)}, {_q(ref)}, {_q(actor)}, {_q(ts)});"]
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
        for s in stmts:
            sess.send(s)
        sess.send(f"\\echo {MARK_INSERTS}")
        try:
            sess.read_until(MARK_INSERTS)
        except TimeoutError:
            recorded = _replay_after_conflict(db=db, owner=owner, idem_key=idem_key, body_hash=body_hash)
            if recorded == "replayed":
                ref_r = _recorded_ref(db=db, owner=owner, idem_key=idem_key)
                print(f"ACK command={command} idem_key={idem_key} status=replayed result_ref={ref_r}")
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
        print(f"ACK command={command} idem_key={idem_key} status=committed result_ref={ref}{extra}")
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
        return sid, stmts, f" work_id={new_work}"
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
        print("      repair: pass a MIME pair like text/plain or text/markdown")
        return 1
    if (title is None) == (work_id is None):
        print("FAIL ARV-CAP-007: exactly one of --title (a new work) or --work-id (an existing work) "
              "is required — an import names its work")
        print("      repair: pass --title OR --work-id, never both, never neither")
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
                  f" work_id={wid_ack.split('|')[0] if wid_ack else ''}")
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
        if not _journal_txn(sess, f"UPDATE arv.import_journal SET state='staging_verified', "
                            f"updated_at={_q(clock.now())} WHERE owner_scope={_q(owner)} "
                            f"AND idempotency_key={_q(idem_key)};", idem_key=idem_key):
            return 1
        if crash_at == "after-verify":
            sess.kill()
            return 2
        build = _import_build(owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,  # phase 3: the ONE metadata txn
                              title=title, work_id=work_id, digest=digest, media_type=media_type,
                              byte_size=len(data), acquired_via=acquired_via)
        return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                      command="import_source", payload=body, build=build, crash_at=crash_at)
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
            text = blob.get(digest).decode("utf-8")
        except UnicodeDecodeError:
            raise _CapRefusal("ARV-CAP-008",
                              f"source {source_id} is not valid UTF-8 text (P3-01 supports readable text/Markdown — the media-type boundary)",
                              "import the source with a supported media type; binary formats land with their own slices")
        except KeyError as e:
            raise _CapRefusal("ARV-CAP-004", f"the source's blob failed to verify — {e}",
                              "the store is corrupt at this digest; never a capture against unverifiable bytes")
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
        ]
        return hl_id, stmts, ""

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="create_highlight", payload=body, build=build, crash_at=crash_at)


def _extract_source(**kwargs):
    """P3-03a (CLAIM-052): the extraction command — the derived-build path lives
    in harness/extract.py as its own module (§2.9's boundary made structural: NO
    command_log row; the generation row IS the idempotency record). Imported at
    CALL time: extract.py imports this module's spine pieces (Session, _q,
    _sess_row, canonical_body, _dead_exit) at ITS module level, so a module-level
    import here would be circular in the extract-first load order."""
    from harness.extract import extract_source
    return extract_source(**kwargs)


REGISTRY = {"record_event": record_event, "import_source": import_source,
            "create_highlight": create_highlight, "extract_source": _extract_source}


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
    return create_highlight(db=db, owner=a.owner, actor=a.actor, client_id=a.client_id,
                            idem_key=a.idem_key, source_id=a.source_id,
                            start=a.start, end=a.end)


if __name__ == "__main__":
    sys.exit(main())
