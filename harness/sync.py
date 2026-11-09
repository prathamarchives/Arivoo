#!/usr/bin/env python3
"""harness/sync.py — the sync driver (P3-08; CLAIM-059; RTM §3.4/§3.5 + SYS-08
+ D-018/D-032).

The outbox walk: read the owner's non-terminal rows in SEQUENCE order; per
row: mark delivered (attempts+1, its own committed update) BEFORE the send —
a death between the mark and the answer leaves 'delivered', the state the
next pass's replay resolves; apply the command on the SERVER database through
the SAME kernel (python3 harness/commands.py <command> ... with
PGDATABASE=<server> ARV_SITE=server — the server-site application enqueues
the server_outbox handoff row in its own transaction, D-018); classify:
  rc=0 -> acknowledged (the replay IS the exactly-once resolution; the
          server's result_ref rides the row, the ARV-SYN-008 law)
  rc=1 + ARV-CMD-409 -> failed (the typed body conflict — terminal, visible,
          both bodies preserved; never a silent LWW)
  rc=1 other -> retryable (the named refusal — the outage class
          ARV-CMD-010/ARV-DB-003 or the server-side validation mismatch)
  rc=2 / deadline -> uncertain (the honest unknown; only the next pass's
          same-key replay resolves it)
attempts >= --max-attempts on a retryable outcome -> failed (the terminal
policy; the local mutation remains local-durable). Exit 0 = the walk
completed (explicitly queued/retryable is a legitimate end state).

THE IDENTITY BRIDGE: the two domains mint their own entity ids; the driver
translates a referenced local id to the server's id for the SAME logical
entity through the two idempotency ledgers (the local creating command's
key -> the server's recorded result_ref) — the equality contract across
domains is over COUNTS + CONTENTS + per-entity chains, never raw id equality.
THE SOUNDNESS GATE (the SEV round-1 F2 repair): a server answer is a valid
translation ONLY when the local outbox row for the creating command rests
'acknowledged' — a 409-divergent creator's answer belongs to a DIFFERENT
logical command and never satisfies a referencer.

Environment (the main()-PGDATABASE precedent): the LOCAL database is
PGDATABASE; the server database arrives as --server-db. ARV_SITE=server is
set ONLY on the server-side child invocation, never this process. Crash
injection: --crash-at {pre-send, post-apply-pre-ack, post-ack} kills the
driver hard (SIGKILL on itself) at the FIRST row reaching that point.
"""
import argparse
import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from harness.adapters import pg, clock, blob  # noqa: E402

NON_TERMINAL = ("pending", "delivered", "uncertain", "retryable")


def _q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def _die() -> None:
    os.kill(os.getpid(), signal.SIGKILL)


def _app(db: str, owner: str, sql: str) -> "tuple[int, str]":
    """One owner-scoped arv_app statement on <db> (RLS rides the session)."""
    r = pg.psql(f"SET app.current_owner={_q(owner)}; {sql}", db=db, user="arv_app")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _scalar(db: str, owner: str, sql: str) -> str:
    """One owner-scoped scalar read ('' when no row)."""
    rc, out = _app(db, owner, sql)
    return out.strip().split("\n")[0] if rc == 0 and out.strip() else ""


def _rows(db: str, owner: str, sql: str) -> list:
    rc, out = _app(db, owner, sql)
    return [ln for ln in out.split("\n") if ln.strip()] if rc == 0 else []


def _create_key(local_db: str, owner: str, local_id: str) -> str:
    """The bridge's local half: the creating command's key for a local entity
    id (the command_log's result_ref; a create/import command preferred over
    later same-entity commands — the creator is always the EARLIEST seq). THE
    SOUNDNESS GATE: the key counts ONLY when its outbox row rests
    'acknowledged' (a 409-divergent creator's server answer belongs to a
    different logical command). A WORK id is never a result_ref — the work
    bridge goes through any acknowledged source of that work."""
    key = _scalar(local_db, owner,
                  f"SELECT c.idempotency_key FROM arv.command_log c JOIN arv.outbox o "
                  f"ON o.owner_scope = c.owner_scope AND o.idempotency_key = c.idempotency_key "
                  f"WHERE c.owner_scope={_q(owner)} AND c.result_ref={_q(local_id)} "
                  f"AND o.state = 'acknowledged' "
                  f"ORDER BY (c.command_name IN ('import_source','create_highlight',"
                  f"'create_bookmark','create_note')) DESC, c.created_at, c.idempotency_key "
                  f"LIMIT 1;")
    if not key:
        key = _scalar(local_db, owner,
                      f"SELECT c.idempotency_key FROM arv.source s "
                      f"JOIN arv.command_log c ON c.result_ref = s.id::text "
                      f"AND c.owner_scope = s.owner_scope "
                      f"JOIN arv.outbox o ON o.owner_scope = c.owner_scope "
                      f"AND o.idempotency_key = c.idempotency_key "
                      f"WHERE s.owner_scope={_q(owner)} AND s.work_id={_q(local_id)} "
                      f"AND o.state = 'acknowledged' "
                      f"ORDER BY s.created_at LIMIT 1;")
    return key


def _translate(local_db: str, server_db: str, owner: str, local_id: str) -> str:
    """The identity bridge: local entity id -> the server's id for the SAME
    logical entity, through the two idempotency ledgers. '' when the creating
    command has no server answer yet (the ordering dependency)."""
    key = _create_key(local_db, owner, local_id)
    if not key:
        return ""
    ref = _scalar(server_db, owner,
                  f"SELECT result_ref FROM arv.command_log "
                  f"WHERE owner_scope={_q(owner)} AND idempotency_key={_q(key)};")
    return ref if ref else ""


def _translate_work(local_db: str, server_db: str, owner: str, work_local: str) -> str:
    """The work-id bridge: through any synced source of that work (the local
    source's key -> the server's source ref -> the server source's work)."""
    src_server = _translate(local_db, server_db, owner, _scalar(
        local_db, owner, f"SELECT id FROM arv.source WHERE owner_scope={_q(owner)} "
                         f"AND work_id={_q(work_local)} ORDER BY created_at LIMIT 1;"))
    if not src_server:
        return ""
    return _scalar(server_db, owner, f"SELECT work_id FROM arv.source "
                                     f"WHERE owner_scope={_q(owner)} AND id={_q(src_server)};")


def _refs_args(refs: list, local_db: str, server_db: str, owner: str) -> "tuple[list, str]":
    """The reference set -> the --ref surface, each target TRANSLATED through
    the bridge (a local id is meaningless on the server; an untranslatable
    target is the named ARV-SYN-009 ordering dependency)."""
    out: list = []
    for r in refs or []:
        t = _translate(local_db, server_db, owner, r[1])
        if not t:
            return [], (f"ARV-SYN-009: the referenced {r[0]} {r[1]} is not yet "
                        "server-durable — the identity dependency (the creating "
                        "command has no server answer; ordering resolves it on "
                        "the next pass)")
        out += ["--ref", f"{r[0]}:{t}@{r[2]}" if r[2] is not None else f"{r[0]}:{t}"]
    return out, ""


def _cli_args(row: dict, local_db: str, server_db: str, owner: str) -> "tuple[list, str]":
    """The server-side invocation for one outbox row: (argv, error) — the
    identity references translated, an untranslatable one the named
    ARV-SYN-009 dependency, never a wrong-id delivery."""
    p = json.loads(row["payload"])
    c = row["command_name"]
    if c == "import_source":
        try:
            data = blob.get(p["digest"])
        except KeyError as e:
            return None, f"ARV-SYN-009: the source blob is unavailable for the re-materialized import — {e.args[0] if e.args else e}"
        tmp = tempfile.NamedTemporaryFile(prefix="arv-sync-", delete=False)
        tmp.write(data)
        tmp.close()
        argv = ["--file", tmp.name, "--media-type", p["media_type"],
                "--acquired-via", p["acquired_via"]]
        if p["title"] is not None:
            argv += ["--title", p["title"]]
        else:
            w = _translate_work(local_db, server_db, owner, p["work_id"])
            if not w:
                return None, (f"ARV-SYN-009: the work {p['work_id']} is not yet "
                                "server-durable — the identity dependency (the "
                                "work-bridge resolves only through an acknowledged "
                                "source of that work)")
            argv += ["--work-id", w]
        return argv, ""
    if c in ("create_highlight", "create_bookmark"):
        sid = _translate(local_db, server_db, owner, p["source_id"])
        if not sid:
            return None, f"ARV-SYN-009: the source {p['source_id']} is not yet server-durable — the identity dependency (the creating command has no server answer; ordering resolves it on the next pass)"
        return ["--source-id", sid, "--start", str(p["start"]), "--end", str(p["end"])], ""
    if c == "record_session":
        # P4-C slice two (CLAIM-071; the SEV round-1 F1 repair — the dead
        # letter closed for the session family, the SYN-18 precedent's law:
        # never a dead letter in the outbox-carrying set): the session event
        # DELIVERS through the translated source id with the recorded
        # kind/span/dwell; the server-side event binds the SERVER's own
        # serving generation (the site-local binding law — each site's rows
        # bind that site's generation ids, never a cross-site uuid
        # transplant). A server that has not extracted rests the row
        # retryable with the command's own named ARV-SES-002 reason — a
        # truthful state, never a dead letter
        sid = _translate(local_db, server_db, owner, p["source_id"])
        if not sid:
            return None, f"ARV-SYN-009: the source {p['source_id']} is not yet server-durable — the identity dependency (the creating command has no server answer; ordering resolves it on the next pass)"
        argv = ["--source-id", sid, "--event", p["event"],
                "--start", str(p["start"]), "--end", str(p["end"])]
        if p.get("dwell_ms") is not None:
            argv += ["--dwell-ms", str(p["dwell_ms"])]
        return argv, ""
    if c == "save_position":
        # P4-A slice two (CLAIM-066; the SEV round-1 F1 repair — the dead
        # letter closed): the position save DELIVERS through the translated
        # source id; the server-side save binds the SERVER's own serving
        # generation (the site-local binding law — each site's rows bind that
        # site's generation ids, never a cross-site uuid transplant). A server
        # that has not extracted rests the row retryable with the command's
        # own named ARV-POS-002 reason — a truthful state, never a dead letter
        sid = _translate(local_db, server_db, owner, p["source_id"])
        if not sid:
            return None, f"ARV-SYN-009: the source {p['source_id']} is not yet server-durable — the identity dependency (the creating command has no server answer; ordering resolves it on the next pass)"
        return ["--source-id", sid, "--start", str(p["start"]), "--end", str(p["end"])], ""
    if c in ("revise_highlight", "move_bookmark"):
        i = _translate(local_db, server_db, owner, p["id"])
        if not i:
            return None, f"ARV-SYN-009: the entity {p['id']} is not yet server-durable — the identity dependency"
        return ["--id", i, "--start", str(p["start"]), "--end", str(p["end"])], ""
    if c in ("tombstone_highlight", "restore_highlight", "tombstone_bookmark",
             "restore_bookmark", "tombstone_note", "restore_note"):
        i = _translate(local_db, server_db, owner, p["id"])
        if not i:
            return None, f"ARV-SYN-009: the entity {p['id']} is not yet server-durable — the identity dependency"
        return ["--id", i], ""
    if c == "create_note":
        refs, err = _refs_args(p.get("refs"), local_db, server_db, owner)
        if err:
            return None, err
        return ["--content", p["content"]] + refs, ""
    if c == "revise_note":
        i = _translate(local_db, server_db, owner, p["id"])
        if not i:
            return None, f"ARV-SYN-009: the note {p['id']} is not yet server-durable — the identity dependency"
        refs, err = _refs_args(p.get("refs"), local_db, server_db, owner)
        if err:
            return None, err
        return ["--id", i, "--content", p["content"]] + refs, ""
    return None, f"ARV-SYN-000: the command {c} is not in the outbox-carrying set — never delivered"


def _apply(server_db: str, row: dict, argv: list, timeout: float) -> "tuple[object, str]":
    """The server-side application: the SAME kernel, the server site — the
    child in its own process group so a deadline kill reaps the psql session
    too (the blocked-transaction rollback class)."""
    full = [sys.executable, str(REPO / "harness" / "commands.py"), row["command_name"],
            "--owner", row["owner"], "--actor", row["actor"],
            "--client-id", row["client_id"], "--idem-key", row["idempotency_key"]] + argv
    env = dict(os.environ, PGDATABASE=server_db, ARV_SITE="server")
    p = subprocess.Popen(full, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=timeout)
        return p.returncode, out or ""
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            p.kill()
        p.wait()
        return "timeout", ""


def _outcome(row: dict, rc: object, out: str, max_attempts: int) -> "tuple[str, str, str]":
    """The classifier: (state, reason, server_ref)."""
    ref = ""
    for ln in out.splitlines():
        if "result_ref=" in ln:
            ref = ln.split("result_ref=")[1].split()[0]
            break
    if rc == 0:
        return "acknowledged", "", ref
    if rc == 2:
        return "uncertain", "the command process died mid-flight (the crash class) — the next pass's same-key replay resolves it", ""
    if rc == "timeout":
        return "uncertain", "the delivery deadline passed with no response — never an assumed failure or success", ""
    first_fail = next((ln for ln in out.splitlines() if ln.startswith("FAIL ")), out[:160])
    if "ARV-CMD-409" in out:
        return "failed", first_fail, ""
    return ("failed" if row["attempts"] >= max_attempts else "retryable"), first_fail, ""


def do_sync(owner: str, server_db: str, timeout: float, max_attempts: int,
            crash_at: str) -> int:
    local_db = os.environ.get("PGDATABASE", "postgres")
    rows = _rows(local_db, owner,
                 "SELECT seq || '|' || idempotency_key || '|' || client_id || '|' || actor || "
                 "'|' || command_name || '|' || body_hash || '|' || state || '|' || attempts || "
                 "'|' || payload FROM arv.outbox WHERE state IN "
                 "('pending','delivered','uncertain','retryable') ORDER BY seq;")
    if not rows:
        print(f"SYNC-DONE owner={owner} rows=0")
        return 0
    # the pipe positions are KNOWN (payload rides LAST — single-line canonical
    # JSON by construction; the established _sess_rows law)
    names = ("seq", "idempotency_key", "client_id", "actor", "command_name",
             "body_hash", "state", "attempts", "payload")
    parsed = [{"owner": owner, **dict(zip(names, ln.split("|", 8)))} for ln in rows]
    for row in parsed:
        row["attempts"] = int(row["attempts"])
    done = 0
    for row in parsed:
        ts = clock.now()
        rc_u, out_u = _app(local_db, owner,
                           f"UPDATE arv.outbox SET state='delivered', attempts=attempts+1, "
                           f"last_reason=NULL, updated_at={_q(ts)} WHERE owner_scope={_q(owner)} "
                           f"AND idempotency_key={_q(row['idempotency_key'])};")
        if rc_u != 0:
            print(f"FAIL ARV-SYN-011: the delivered-mark refused for key "
                  f"{row['idempotency_key']} — {out_u.strip()[:200]}")
            return 1
        row["attempts"] += 1
        if crash_at == "pre-send":
            _die()
        # THE PER-ROW CONTAINMENT (the SEV round-1 F1 repair): an undeliverable
        # payload is the named ARV-SYN-013 terminal failure for THAT row — the
        # walk CONTINUES; one poisoned row may never block every later row
        try:
            argv, err = _cli_args(row, local_db, server_db, owner)
        except Exception as e:  # the undeliverable class — named, contained
            argv, err = None, (f"ARV-SYN-013: the payload is undeliverable — "
                               f"{type(e).__name__}: {e}")
        tmp_file = next((a for a in (argv or []) if a.startswith("/tmp/arv-sync-")), None)
        if argv is None:
            # the undeliverable class (ARV-SYN-013) is TERMINAL on first
            # observation — a payload that cannot parse will never parse; the
            # dependency class (ARV-SYN-009) stays retryable until the policy
            if "ARV-SYN-013" in err:
                state, reason = "failed", err
            else:
                state, reason = ("failed" if row["attempts"] >= max_attempts else "retryable"), err
            rc_o, out_o = _app(local_db, owner,
                               f"UPDATE arv.outbox SET state={_q(state)}, last_reason={_q(reason)}, "
                               f"updated_at={_q(clock.now())} WHERE owner_scope={_q(owner)} "
                               f"AND idempotency_key={_q(row['idempotency_key'])};")
            print(f"SYNC key={row['idempotency_key']} state={state} reason={err.split(':')[0]}")
            done += 1
            continue
        rc, out = _apply(server_db, row, argv, timeout)
        if tmp_file:
            try:
                os.unlink(tmp_file)  # the SEV round-1 F5 repair: no leaked staging file per attempt
            except OSError:
                pass
        if crash_at == "post-apply-pre-ack":
            _die()
        state, reason, ref = _outcome(row, rc, out, max_attempts)
        rc_o, out_o = _app(local_db, owner,
                           f"UPDATE arv.outbox SET state={_q(state)}, "
                           f"server_ref={'NULL' if not ref else _q(ref)}, "
                           f"last_reason={'NULL' if not reason else _q(reason)}, "
                           f"updated_at={_q(clock.now())} WHERE owner_scope={_q(owner)} "
                           f"AND idempotency_key={_q(row['idempotency_key'])};")
        if rc_o != 0:
            print(f"FAIL ARV-SYN-012: the outcome-mark refused for key "
                  f"{row['idempotency_key']} — {out_o.strip()[:200]}")
            return 1
        tail = f" server_ref={ref}" if ref else (f" reason={reason[:80]}" if reason else "")
        print(f"SYNC key={row['idempotency_key']} state={state}{tail}")
        done += 1
        if crash_at == "post-ack":
            _die()
    print(f"SYNC-DONE owner={owner} rows={done}")
    return 0


def do_status(owner: str) -> int:
    local_db = os.environ.get("PGDATABASE", "postgres")
    counts = _rows(local_db, owner,
                   "SELECT state || '=' || count(*) FROM arv.outbox GROUP BY state "
                   "ORDER BY state;")
    print(f"SYNC-STATUS owner={owner} " + " ".join(counts))
    for ln in _rows(local_db, owner,
                    "SELECT idempotency_key || ' state=' || state || ' attempts=' || attempts "
                    "FROM arv.outbox WHERE state IN ('pending','delivered','uncertain',"
                    "'retryable') ORDER BY seq;"):
        print(f"SYNC-QUEUED {ln}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the sync driver (P3-08)")
    sub = ap.add_subparsers(dest="arm", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--owner", required=True)
    s.add_argument("--server-db", required=True)
    s.add_argument("--timeout", type=float, default=30.0)
    s.add_argument("--max-attempts", type=int, default=3)
    s.add_argument("--crash-at", default=None,
                   choices=["pre-send", "post-apply-pre-ack", "post-ack"])
    t = sub.add_parser("status")
    t.add_argument("--owner", required=True)
    a = ap.parse_args()
    if a.arm == "status":
        return do_status(a.owner)
    return do_sync(a.owner, a.server_db, a.timeout, a.max_attempts, a.crash_at)


if __name__ == "__main__":
    sys.exit(main())
