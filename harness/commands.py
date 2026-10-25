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


class Session:
    """ONE persistent psql session (the command's transaction boundary; statements
    execute as they are fed — markers make execution observable).

    A dedicated reader thread drains stdout line-by-line into a queue (the pipe
    is small; an undrained pipe would eventually deadlock the server side), and
    read_until() consumes lines until the marker (psql flushes per statement —
    verified empirically, record 18 §4.3)."""

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
        sess.read_until(MARK_BEGUN)
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
            if sess.proc.poll() is not None:
                # The SEV round's P3: the session DIED (ON_ERROR_STOP) on a unique
                # violation this key does not own — a zero-effect race loss, NOT a stall.
                print(f"FAIL ARV-CMD-011: the session ended before the commit marker — a concurrent "
                      "writer won a unique constraint this key does not own (zero effect, the transaction rolled back)")
                print("      repair: retry the SAME idempotency key (the ordinal is re-read) or use a new one")
                return 1
            raise  # a live session with no marker: the honest unknown (ARV-CMD-010)
        if crash_at == "pre-commit":
            sess.kill()
            return 2
        sess.send("COMMIT;")
        sess.send(f"\\echo {MARK_COMMITTED}")
        sess.read_until(MARK_COMMITTED)
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


def import_source(*, db, owner, actor, client_id, idem_key, title=None, work_id=None,
                  file=None, media_type="text/plain", acquired_via="cli-import",
                  crash_at: str = None) -> int:
    """The first real product command: import a Source (P3-01; RTM §3.1's tail:
    blob verified readable+digest-matched BEFORE the metadata commit, then the
    work+source+command_log rows in ONE transaction).  Q12-neutral: the blob
    rides the adapter; the Source stores the ref, never the bytes."""
    path = pathlib.Path(file) if file else None
    if path is None or not path.is_file():
        print(f"FAIL ARV-CAP-001: the import file {file!r} is absent or unreadable — the bytes are read and hashed BEFORE any effect")
        print("      repair: pass --file with a readable path; a missing file is a named refusal, never a partial import")
        return 1
    data = path.read_bytes()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*", media_type):
        # The SEV round's P2: a pipe-carrying media_type later crashed the capture
        # path's pipe-delimited reads; the token grammar is where it enters.
        print(f"FAIL ARV-CAP-009: media_type {media_type!r} is not a MIME token pair (type/subtype, "
              "token charset only) — free-form text is a title/payload, never a media type")
        print("      repair: pass a MIME pair like text/plain or text/markdown")
        return 1
    digest = blob.put(data)
    try:
        blob.get(digest)  # the §3.1 verify: readable AND digest-matched (get re-hashes)
    except KeyError as e:
        print(f"FAIL ARV-CAP-004: the blob verify failed — {e}")
        print("      repair: the store is corrupt at this digest; the staging cleanup is P3-02's recovery walk — a Source NEVER commits without verified bytes")
        return 1
    body = json.dumps({"work_id": work_id, "title": title, "digest": digest,
                      "media_type": media_type, "acquired_via": acquired_via,
                      "byte_size": len(data)},
                     sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def build(sess: "Session", body_hash: str):
        if (title is None) == (work_id is None):
            raise _CapRefusal("ARV-CAP-007",
                              "exactly one of --title (a new work) or --work-id (an existing work) is required — an import names its work",
                              "pass --title OR --work-id, never both, never neither")
        ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
        stmts = []
        new_work = work_id
        if work_id is None:
            new_work = ids.new_id()
            stmts.append(f"INSERT INTO arv.work (id, title, owner_scope, actor, run_id, input_hash, created_at) "
                         f"VALUES ({_q(new_work)}, {_q(title)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, {_q(ts)});")
        elif not _sess_row(sess, f"SELECT id || '|' FROM arv.work WHERE id={_q(work_id)};"):
            raise _CapRefusal("ARV-CAP-006",
                              f"work {work_id} does not exist in the caller's scope",
                              "import against an existing work id, or create a new work with --title")
        sid = ids.new_id()
        version = _sess_row(sess, f"SELECT (COALESCE(MAX(source_version), 0) + 1) || '|' FROM arv.source "
                                  f"WHERE work_id={_q(new_work)};").split("|")[0] or "1"
        stmts.append(f"INSERT INTO arv.source (id, work_id, digest, media_type, byte_size, blob_ref, acquired_via, "
                     f"import_state, source_version, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
                     f"VALUES ({_q(sid)}, {_q(new_work)}, {_q(digest)}, {_q(media_type)}, {len(data)}, {_q(digest)}, "
                     f"{_q(acquired_via)}, 'complete', {version}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
                     f"{_q(idem_key)}, {_q(ts)});")
        return sid, stmts, f" work_id={new_work}"

    return _spine(db=db, owner=owner, actor=actor, client_id=client_id, idem_key=idem_key,
                  command="import_source", payload=body, build=build, crash_at=crash_at)


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


REGISTRY = {"record_event": record_event, "import_source": import_source,
            "create_highlight": create_highlight}


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
