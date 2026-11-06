#!/usr/bin/env python3
"""harness/tests/test_sync.py — P3-08 acceptance suite (CLAIM-059, the local
outbox, the sync driver, and the recovery semantics; PLAN's P3-08 card; RTM
§3.4/§3.5 + SYS-08 + D-018/D-032). Red-first (LAW-11): at CLAIM-058's merged
head 67e37fa the suite fails with ARV-TEST-000 (machinery-absent; red-01.txt).

THE CONTRACT: the local authoritative mutation and its client-outbox intent
commit ATOMICALLY (RTM §4.2 — one local transaction: the effect rows + the
command-log row + the outbox row); local and cloud are SEPARATE durability
domains bridged by the outbox, never one transaction (D-032/Q12 — the rig
models the two domains as two databases on the loopback boundary). The outbox
state machine (RTM §3.4): pending -> delivered -> acknowledged, with uncertain
(timeout after possible server commit — replay by the SAME idempotency key
resolves it, never an assumed outcome), retryable (named reason; the terminal
policy flips it to failed after --max-attempts), failed (visible; the local
mutation remains local-durable). The server applies a delivered command
through the SAME command kernel and idempotency semantics as a direct API
call (RTM §3.5 — one command core, two execution sites): unknown key ->
apply; known key + same body -> the recorded result (no duplicate logical
effect); known key + different body -> ARV-CMD-409 surfaced as the delivery's
typed conflict. NO authored-content LWW: competing bodies both persist. The
IDENTITY BRIDGE: the two domains mint their own entity ids; the driver
translates a referenced local id to the server's id for the SAME logical
entity through the two idempotency ledgers (the creating command's key ->
the server's recorded result_ref) — the equality contract is over COUNTS +
CONTENTS + per-entity chains, never over raw id equality. The server-site
application enqueues the SERVER outbox handoff row in its own transaction
(D-018: post-commit enrichment — the consumers are P4+'s).

Refusal codes: ARV-SYN-004 the immutable delivery keys; ARV-SYN-005 the
declared transition graph; ARV-SYN-006 attempts monotonicity; ARV-SYN-007
the append-only audit trail; ARV-SYN-008 the acknowledged-requires-server_ref
law; ARV-SYN-009 an identity dependency not yet server-durable; ARV-SYN-010
the server outbox's append-only law.

Cases (the SYN registry; each pin's full statement lives at its check()):
  SYN-01 the atomic enqueue: a committed local command carries its outbox
         row in the SAME transaction (a pre-commit crash leaves ZERO outbox
         rows; a post-commit crash leaves the row — the zero-or-one proof)
  SYN-02 restart before sync: committed captures stay local-durable with
         every row honestly pending; ONE sync pass acknowledges them all;
         the independent remote read confirms the count+content equality
  SYN-03 duplicate delivery: a re-delivered row REPLAYS by the same key +
         body (the kernel's own semantics) — zero duplicate logical effects
         (the server's row counts unchanged); acknowledged rows are skipped
  SYN-04 out-of-order delivery: a hostile pre-delivery of a LATER row on
         the server refuses cleanly (zero effect); the ordered pass lands
         everything; the revision chain + contents equal the local truth
  SYN-05 retry after uncertain acknowledgment: a held server-side advisory
         lock blocks the delivery past the driver's deadline -> uncertain
         (the named reason); release + re-sync -> replay resolves ->
         acknowledged; exactly one new revision (no duplicate)
  SYN-06 server outage: the unreachable server class -> every row retryable
         with the named reason (never lost, never failed on attempt 1); the
         local state untouched; the recovered pass acknowledges everything
  SYN-07 the remote/local mismatch: a key the server already carries with a
         DIFFERENT body -> ARV-CMD-409 -> failed (terminal, visible, both
         bodies preserved — never a silent last-write-wins)
  SYN-08 cross-owner sync: the driver's owner scoping delivers ONLY the
         named owner's rows (RLS on the outbox read); B's rows land only
         under B's sync; the hostile cross-owner read sees nothing
  SYN-09 process death around the ack-update: pre-send death (delivered,
         server empty), post-apply-pre-ack death (delivered, server
         committed — the re-sync REPLAYS, no duplicate), post-ack death
         (acknowledged; re-sync skips; counts unchanged)
  SYN-10 the independent remote read: after a full-family sync (import,
         highlight, bookmark, note, revise, tombstone, restore, refs) the
         arv_read counts per family + the note contents + the lifecycle
         parity equal the local truth (the acceptance's equality)
  SYN-11 the outbox substrate guards: the hostile direct-SQL matrix (the
         key retarget, the illegal transition, the attempts decrease, the
         delete, the acknowledged-without-ref) + RLS + the 0012 schema
         audits
  SYN-12 the status arm: the per-state counts honest against arv_read; the
         non-terminal rows listed; the ladder vocabulary named
  SYN-13 the server-outbox handoff (D-018): one pending row per APPLIED
         command, atomic with the application; a REPLAYED delivery adds
         none; local commands never touch it; its append-only law
  SYN-14 the ordering law: the driver delivers in sequence order — the
         revise/tombstone/restore chain lands in order (a wrong order would
         refuse: tombstone-before-revise is ARV-NTE-002), the server's
         lifecycle event ordering follows, every row acknowledged
  SYN-15 the no-lost-writes acceptance: every local product command's key
         has exactly one outbox row; every row rests in a TRUTHFUL state
         (acknowledged carries server_ref; retryable/failed carry the named
         reason); the server's command-log key set == the acknowledged set
         plus the 409-failed set; zero rows silently dropped
  SYN-18 the position delivery (the SEV round-1 F1 repair): the
         save_position outbox row DELIVERS — the server-side save
         re-executes through the TRANSLATED source id and binds the
         SERVER's own serving generation (the site-local binding law:
         each site's rows bind that site's generation ids, never a
         cross-site uuid transplant); the row acknowledges with its
         server_ref and the server's read arm answers the delivered row

Run: python3 harness/tests/test_sync.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the driver + the migration must
# be ABSENT at the RED tree — the implementation lands after this RED, never
# before it (LAW-11; the KWR-01 precedent form)
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "sync.py"), "sync", "--help"],
                        capture_output=True, text=True)
_absent_driver = not _probe.stdout.strip() or "unrecognized" in _probe.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0012_*.sql"))
if _absent_driver or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-08 sync machinery is absent (machinery-absent "
          f"class; the driver absent: {_absent_driver}; migration 0012 present: "
          f"{bool(_mig)}) — the implementation lands after this RED, never before "
          "it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

LOC = SRV = None
ENV = None

TEXT = ("The sync corpus: the persistent anchor phrase lives here.\n"
        "Second line carries the measurable span for capture.\n")


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def cli(*args, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=300, env=env or ENV)


def cmd(op: str, *args, owner="A", key=None, env=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args, env=env)


def crash(*args, owner="A", key=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "crash.py"), "--command", args[0], "--owner", owner,
         "--client-id", "cli-crash", "--idem-key", key or "crash-x", "--point", args[1]]
    return cli(*a, *args[2:])


def sync(*extra, owner="A", server_db=None, env=None) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "sync.py"), "sync", "--owner", owner,
               "--server-db", server_db or SRV, *extra, env=env)


def status(owner="A", env=None) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "sync.py"), "status", "--owner", owner, env=env)


def audit(db: str, query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_read", "-d", db, "-c", query],
                           capture_output=True, text=True, timeout=60,
                           env=ENV).stdout.strip()


def audit_rows(db: str, query: str) -> list:
    return [ln for ln in audit(db, query).split("\n") if ln.strip()]


def app_sql(db: str, sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_app", "-d", db,
                            "-c", f"SET app.current_owner='{owner}'; {sql}"],
                           capture_output=True, text=True, timeout=60, env=ENV)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def ob(db: str, key: str, col: str = "state") -> str:
    """One outbox column for a key, read independently (arv_read)."""
    return audit(db, f"SELECT {col} FROM arv.outbox WHERE owner_scope='A' "
                     f"AND idempotency_key='{key}';")


def srv_note(nid_local: str, col: str = "result_ref") -> str:
    """The server's id for a locally-created note — through the identity
    bridge (the CREATING command's key -> the server's recorded result_ref;
    the creator preferred over later same-entity commands — the driver's own
    deterministic rule, mirrored here for the independent check)."""
    key = audit(LOC, f"SELECT idempotency_key FROM arv.command_log "
                     f"WHERE owner_scope='A' AND result_ref='{nid_local}' "
                     f"ORDER BY (command_name IN ('import_source','create_highlight',"
                     f"'create_bookmark','create_note')) DESC, created_at, idempotency_key "
                     f"LIMIT 1;")
    return audit(SRV, f"SELECT {col} FROM arv.command_log "
                      f"WHERE owner_scope='A' AND idempotency_key='{key}';")


def main() -> int:
    global LOC, SRV, ENV
    LOC = pg.create_scratch_db("p308loc")
    SRV = pg.create_scratch_db("p308srv")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=LOC, ARV_BLOB_DIR=blob_dir)
    try:
        for db in (LOC, SRV):
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=180,
                           env=dict(ENV, PGDATABASE=db), check=True)
        srv_env = dict(ENV, PGDATABASE=SRV, ARV_SITE="server")

        # the shared fixture: the corpus file + owner A's first captures
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "sync.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("persistent anchor")
        e1 = s1 + len("persistent anchor")
        s2 = TEXT.index("measurable span")
        e2 = s2 + len("measurable span")
        pi = cmd("import_source", "--file", str(src_file), "--media-type", "text/plain",
                 "--title", "The Sync Corpus", key="sy-imp1")
        sid = ack_field(pi, "result_ref")
        ph = cmd("create_highlight", "--source-id", sid, "--start", str(s1),
                 "--end", str(e1), key="sy-hl1")
        hid = ack_field(ph, "result_ref")
        pn = cmd("create_note", "--content", "The first sync note: sesquine token.",
                 key="sy-n1")
        nid = ack_field(pn, "result_ref")

        # ---- SYN-01 — the atomic enqueue (the zero-or-one proof)
        cnt_ob = int(audit(LOC, "SELECT count(*) FROM arv.outbox WHERE owner_scope='A';"))
        c_pre = crash("create_note", "pre-commit", "--content", "A crashed note never enqueues.",
                      key="sy-crash1")
        cnt_pre = int(audit(LOC, "SELECT count(*) FROM arv.outbox WHERE owner_scope='A' "
                                 "AND idempotency_key='sy-crash1';"))
        cnt_note_pre = int(audit(LOC, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                                      "AND content LIKE '%crashed note%';"))
        c_post = crash("create_note", "post-commit-pre-ack",
                       "--content", "A post-commit crash enqueues atomically.",
                       key="sy-crash2")
        cnt_post = int(audit(LOC, "SELECT count(*) FROM arv.outbox WHERE owner_scope='A' "
                                  "AND idempotency_key='sy-crash2';"))
        cnt_note_post = int(audit(LOC, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                                       "AND content LIKE '%post-commit crash%';"))
        cl_ob = audit_rows(LOC, "SELECT idempotency_key FROM arv.command_log c WHERE "
                                "c.owner_scope='A' AND c.command_name IN "
                                "('import_source','create_highlight','create_note') "
                                "ORDER BY idempotency_key;")
        ob_all = audit_rows(LOC, "SELECT idempotency_key FROM arv.outbox WHERE "
                                 "owner_scope='A' ORDER BY idempotency_key;")
        ok1 = (pi.returncode == 0 and ph.returncode == 0 and pn.returncode == 0
               and cnt_ob == 3 and len(ob_all) == 4
               and c_pre.returncode == 2 and cnt_pre == 0 and cnt_note_pre == 0
               and c_post.returncode == 2 and cnt_post == 1 and cnt_note_post == 1
               and cl_ob == ob_all)
        check("SYN-01", ok1,
              "the atomic enqueue: every committed product command carries its outbox row in the SAME transaction (three commands, three pending rows, the command-log key set == the outbox key set); a pre-commit crash leaves ZERO outbox rows and ZERO note rows; a post-commit-pre-ack crash leaves BOTH (the commit happened, the ack never emitted) — the zero-or-one proof of RTM §4.2's one-commit-point law",
              "the outbox INSERT must ride the spine's statement list between BEGIN and COMMIT — never a second transaction (a crashed command must never enqueue, a committed one must never miss its row)")

        # ---- SYN-02 — restart before sync (the offline day)
        g = cli(str(REPO / "harness" / "query.py"), "get-note", "--owner", "A", "--id", nid)
        st_all = audit_rows(LOC, "SELECT DISTINCT state FROM arv.outbox WHERE "
                                 "owner_scope='A' ORDER BY state;")
        r2 = sync()
        acks = audit_rows(LOC, "SELECT idempotency_key FROM arv.outbox WHERE "
                               "owner_scope='A' AND state='acknowledged' ORDER BY idempotency_key;")
        srv_notes = audit_rows(SRV, "SELECT content FROM arv.note WHERE owner_scope='A' "
                                    "ORDER BY content;")
        loc_notes = audit_rows(LOC, "SELECT content FROM arv.note WHERE owner_scope='A' "
                                    "ORDER BY content;")
        srv_hl = audit(SRV, "SELECT count(*) FROM arv.highlight WHERE owner_scope='A';")
        ok2 = (g.returncode == 0 and "sesquine" in g.stdout
               and st_all == ["pending"]
               and r2.returncode == 0
               and len(acks) == 4
               and srv_notes == loc_notes and len(srv_notes) == 2
               and srv_hl == "1")
        check("SYN-02", ok2,
              "restart before sync: the committed captures stay readable locally (local_durable — get-note answers while every outbox row is honestly pending, the offline day); ONE sync pass acknowledges all five rows; the independent arv_read on the server confirms the note contents equal the local set and the highlight landed — the count-and-content equality (SYS-08's user scenario)",
              "the local domain is authoritative on its own (D-032's separate durability domains); the sync never gates local reads; the server read must be independent (arv_read), never the driver's own session")

        # ---- SYN-03 — duplicate delivery (the replay never duplicates)
        srv_cl_before = audit(SRV, "SELECT count(*) FROM arv.command_log WHERE owner_scope='A';")
        srv_note_before = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        r3a = sync()  # a full second pass: every row acknowledged -> skipped
        srv_cl_mid = audit(SRV, "SELECT count(*) FROM arv.command_log WHERE owner_scope='A';")
        # a hostile DIRECT re-application of an already-delivered key on the server
        r3b = cmd("create_note", "--content", "The first sync note: sesquine token.",
                  key="sy-n1", env=srv_env)
        srv_note_after = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        # the forced re-send of a delivered-but-unacked row (SYN-09's class, here for the duplicate proof)
        app_sql(LOC, "UPDATE arv.outbox SET state='retryable', updated_at=now() "
                     "WHERE owner_scope='A' AND idempotency_key='sy-crash2';")
        r3c = sync()
        srv_note_final = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        st_c2 = ob(LOC, "sy-crash2")
        ok3 = (r3a.returncode == 0 and srv_cl_mid == srv_cl_before
               and r3b.returncode == 0 and "status=replayed" in r3b.stdout
               and srv_note_after == srv_note_before
               and r3c.returncode == 0 and st_c2 == "acknowledged"
               and srv_note_final == srv_note_before)
        check("SYN-03", ok3,
              "duplicate delivery: a second full pass touches nothing (acknowledged rows are skipped — the server's command-log count unchanged); a hostile DIRECT re-application of a delivered key+body REPLAYS (status=replayed, zero new rows); a re-sent delivered-row (the retryable re-drive) replays through the kernel's same-key+same-body semantics — zero duplicate logical effects at every layer",
              "the idempotency is the KERNEL's own (the command-log replay check), never a driver-side dedup — the driver merely re-invokes with the same key and the deterministic translated body")

        # ---- SYN-04 — out-of-order delivery (the hostile reorder absorbs)
        pr = cmd("revise_note", "--id", nid, "--content",
                 "Revised once: the aurora token rides.", key="sy-n1r1")
        # the hostile PRE-delivery of the LATER row on the server (the reorder)
        h4 = cmd("revise_note", "--id", nid, "--content",
                 "Revised once: the aurora token rides.", key="sy-n1r1", env=srv_env)
        srv_before4 = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        r4 = sync()
        st_r1 = ob(LOC, "sy-n1r1")
        snid = srv_note(nid)
        srv_revs = audit_rows(SRV, f"SELECT revision || '|' || content FROM arv.note "
                                   f"WHERE id='{snid}' ORDER BY revision;")
        ok4 = (pr.returncode == 0 and h4.returncode == 1 and "ARV-NTE-001" in h4.stdout
               and srv_before4 == "2"
               and r4.returncode == 0 and st_r1 == "acknowledged"
               and srv_revs[-1].endswith("the aurora token rides.")
               and len(srv_revs) == 2)
        check("SYN-04", ok4,
              "out-of-order delivery: the hostile pre-delivery of the LATER command (the revise, before the note exists on the server) REFUSES with the named code (ARV-NTE-001 — absent in the caller's scope) and leaves ZERO effect (the server's note count unchanged); the ordered pass then lands create-then-revise; the server's note carries exactly the two revisions with the revised content — the reorder is absorbed by the kernel's own guards, never by reordering the truth",
              "the driver must deliver in sequence order (the outbox seq) so the creator precedes its referencers; a hostile reorder must meet the same named refusals a direct API caller would — never a partial or wrong effect")

        # ---- SYN-05 — retry after uncertain acknowledgment (the held lock)
        pr5 = cmd("revise_note", "--id", nid, "--content",
                  "Revised twice under an uncertain sky: the borealis token.",
                  key="sy-n1r2")
        lock_id = srv_note(nid)  # the SERVER's note id — the identity bridge: the server-side command locks the SERVER id's canonical key
        lock = subprocess.Popen(["psql", "-X", "-A", "-t", "-U", "postgres", "-d", SRV],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, bufsize=1, env=ENV)
        lock.stdin.write(f"SELECT pg_advisory_lock(hashtext('{lock_id}'));\n")
        lock.stdin.flush()
        r5a = sync("--timeout", "3")
        st5a = ob(LOC, "sy-n1r2")
        reason5 = ob(LOC, "sy-n1r2", "last_reason") or ""
        lock.stdin.write(f"SELECT pg_advisory_unlock(hashtext('{lock_id}'));\n\\q\n")
        lock.stdin.flush()
        lock.wait(timeout=30)
        r5b = sync()
        st5b = ob(LOC, "sy-n1r2")
        snid5 = srv_note(nid)
        srv_revs5 = audit_rows(SRV, f"SELECT revision FROM arv.note WHERE id='{snid5}' "
                                    f"ORDER BY revision;")
        ok5 = (pr5.returncode == 0 and r5a.returncode == 0 and st5a == "uncertain"
               and "deadline" in reason5
               and r5b.returncode == 0 and st5b == "acknowledged"
               and [r.split("|")[0] for r in srv_revs5] == ["1", "2", "3"])
        check("SYN-05", ok5,
              "retry after uncertain acknowledgment: the server-side advisory lock (the note's canonical key — the SAME lock the kernel's serialized transitions take) blocks the delivery past the driver's deadline; the row rests at uncertain with the named timeout reason (never an assumed failure or success — RTM §3.4's lost-response state); release + re-sync REPLAYS the same key: the row acknowledges and the server carries exactly revision 3 once (the blocked attempt rolled back; the replay applied exactly once — no duplicate revision)",
              "the uncertain state is the honest unknown: the deadline passed with the server's commit status unobserved; only the next pass's same-key replay (the kernel's own resolution) may move it — to acknowledged (applied) or retryable (refused), never silently dropped")

        # ---- SYN-06 — server outage (the unreachable class)
        pr6 = cmd("create_note", "--content", "The outage note: the cinder token.",
                  key="sy-out1")
        r6a = sync("--server-db", "arv_p308_nonexistent")
        st6a = ob(LOC, "sy-out1")
        reason6 = ob(LOC, "sy-out1", "last_reason") or ""
        att6 = ob(LOC, "sy-out1", "attempts")
        g6 = cli(str(REPO / "harness" / "query.py"), "get-note", "--owner", "A", "--id",
                 ack_field(pr6, "result_ref"))
        r6b = sync()
        st6b = ob(LOC, "sy-out1")
        sn6 = srv_note(ack_field(pr6, "result_ref"))
        c6 = audit(SRV, f"SELECT content FROM arv.note WHERE id='{sn6}';")
        ok6 = (pr6.returncode == 0 and r6a.returncode == 0 and st6a == "retryable"
               and "ARV-CMD-010" in reason6 and att6 == "1"
               and g6.returncode == 0 and "cinder" in g6.stdout
               and r6b.returncode == 0 and st6b == "acknowledged" and "cinder" in c6)
        check("SYN-06", ok6,
              "server outage: the unreachable server class (a nonexistent database — the connection refused family) leaves the row retryable with the named reason (the kernel's own ARV-CMD-010 session marker observation), attempts=1 — never failed on the first attempt, never lost; the local capture stays readable (local_durable through the outage); the recovered pass acknowledges it and the server carries the content — the queued state is honest and recoverable",
              "the outage is a RETRYABLE class by definition (the server's state is unknown-but-reachable-later); only the terminal policy (attempts >= max) may fail a row, and only with the named reason")

        # ---- SYN-07 — the remote/local mismatch (the typed conflict, no LWW)
        d7 = cmd("create_note", "--content", "The server's competing body for the key.",
                 key="sy-conf1", env=srv_env)
        l7 = cmd("create_note", "--content", "The local body for the same key.",
                 key="sy-conf1")
        r7 = sync()
        st7 = ob(LOC, "sy-conf1")
        reason7 = ob(LOC, "sy-conf1", "last_reason") or ""
        loc_note7 = audit(LOC, "SELECT content FROM arv.note WHERE owner_scope='A' "
                               "AND content LIKE '%same key%';")
        srv_note7 = audit(SRV, "SELECT content FROM arv.note WHERE owner_scope='A' "
                               "AND content LIKE '%competing body%';")
        ok7 = (d7.returncode == 0 and l7.returncode == 0 and r7.returncode == 0
               and st7 == "failed" and "ARV-CMD-409" in reason7
               and loc_note7 == "The local body for the same key."
               and srv_note7 == "The server's competing body for the key.")
        check("SYN-07", ok7,
              "the remote/local mismatch: the server already carries the key with a DIFFERENT body (the competing direct application); the delivery surfaces the kernel's typed conflict (ARV-CMD-409) and the row rests at failed — terminal, visible, the reason recorded; BOTH bodies persist (the local note and the server note each intact) — never a silent last-write-wins for authored content (RTM §3.5's third case)",
              "the conflict is the delivery's typed outcome, never a destructive resolution; the owner decides — the row's failed state with the named reason IS the surfacing")

        # ---- SYN-08 — cross-owner sync (the isolation)
        pb8 = cmd("import_source", "--file", str(src_file), "--media-type", "text/plain",
                  "--title", "B's Corpus", key="sy-impB", owner="B")
        pn8 = cmd("create_note", "--content", "B's private sesquine thinking.",
                  key="sy-nB", owner="B")
        r8a = sync(owner="B")
        stB1 = audit(LOC, "SELECT state FROM arv.outbox WHERE owner_scope='B' "
                          "AND idempotency_key='sy-impB';")
        srv_a_notes = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
        srv_b_notes = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='B';")
        # the hostile cross-owner read: A's session must see ZERO of B's outbox rows
        # (the psql SET command tag leaks a line — the LAST line is the answer)
        hostile = app_sql(LOC, "SELECT count(*) FROM arv.outbox WHERE owner_scope='B';", owner="A")
        # A's sync must never deliver B's rows (already all acknowledged anyway —
        # the counts prove the isolation held through the whole suite)
        r8b = sync(owner="A")
        srv_b_after = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='B';")
        ok8 = (pb8.returncode == 0 and pn8.returncode == 0 and r8a.returncode == 0
               and r8b.returncode == 0
               and stB1 == "acknowledged"
               and srv_b_notes == "1" and srv_b_after == "1"
               and srv_a_notes == audit(LOC, "SELECT count(*) FROM arv.note WHERE owner_scope='A';")
               and hostile.stdout.strip().split("\n")[-1] == "0")
        check("SYN-08", ok8,
              "cross-owner sync: B's sync delivers B's rows only (the RLS-scoped outbox read — A's session sees ZERO of B's rows, the hostile read returns 0); A's sync never touches B's delivery state; the server carries each owner's notes under that owner's scope with the counts equal to the local truth per owner — the isolation holds across BOTH domains",
              "the driver's every read and update rides the owner-scoped arv_app session (app.current_owner) — the outbox RLS is the structural isolation, never a driver-side filter")

        # ---- SYN-09 — process death around the ack-update
        pr9 = cmd("create_note", "--content", "The death-matrix note: perihelion.",
                  key="sy-d1")
        r9a = sync("--crash-at", "pre-send")
        st9a = ob(LOC, "sy-d1")
        srv9a = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                           "AND content LIKE '%perihelion%';")
        r9b = sync()
        st9b = ob(LOC, "sy-d1")
        srv9b = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                           "AND content LIKE '%perihelion%';")
        pr9c = cmd("create_note", "--content", "The second death note: aphelion.",
                   key="sy-d2")
        r9c = sync("--crash-at", "post-apply-pre-ack")
        st9c = ob(LOC, "sy-d2")
        srv9c = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                           "AND content LIKE '%aphelion%';")
        r9d = sync()
        st9d = ob(LOC, "sy-d2")
        srv9d = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                           "AND content LIKE '%aphelion%';")
        pr9e = cmd("create_note", "--content", "The third death note: nadir.",
                   key="sy-d3")
        r9e = sync("--crash-at", "post-ack")
        st9e = ob(LOC, "sy-d3")
        r9f = sync()
        srv9f = audit(SRV, "SELECT count(*) FROM arv.note WHERE owner_scope='A' "
                           "AND content LIKE '%nadir%';")
        ok9 = (pr9.returncode == 0 and r9a.returncode != 0 and st9a == "delivered"
               and srv9a == "0"
               and r9b.returncode == 0 and st9b == "acknowledged" and srv9b == "1"
               and pr9c.returncode == 0 and r9c.returncode != 0 and st9c == "delivered"
               and srv9c == "1"
               and r9d.returncode == 0 and st9d == "acknowledged" and srv9d == "1"
               and pr9e.returncode == 0 and r9e.returncode != 0 and st9e == "acknowledged"
               and r9f.returncode == 0 and srv9f == "1")
        check("SYN-09", ok9,
              "process death around the outbox acknowledgment: pre-send death leaves the row delivered with the server EMPTY (the re-sync applies once); post-apply-pre-ack death leaves the row delivered with the server COMMITTED (the independent read proves it — the re-sync REPLAYS the same key, acknowledges, and the server count stays exactly one — the death window never duplicates); post-ack death leaves the row acknowledged (the update committed before the death; the re-sync skips it) — the three death windows of SYS-08's matrix, each resolving to exactly-once",
              "the delivered-mark precedes the send (its own committed update) and the acknowledged-mark follows the server's answer — the two marks bracket the uncertainty window the replay resolves")

        # ---- SYN-10 — the independent remote read (the full-family equality)
        ph10 = cmd("revise_highlight", "--id", hid, "--start", str(s2), "--end", str(e2),
                   key="sy-hl1r")
        pbm = cmd("create_bookmark", "--source-id", sid, "--start", str(s1),
                  "--end", str(e1), key="sy-bm1")
        bm_id = ack_field(pbm, "result_ref")
        pn10 = cmd("create_note", "--content",
                   "The referenced note: the culmination token.",
                   "--ref", f"highlight:{hid}@1", key="sy-n10")
        n10 = ack_field(pn10, "result_ref")
        pl = cmd("tombstone_note", "--id", n10, key="sy-n10t")
        prs = cmd("restore_note", "--id", n10, key="sy-n10r")
        pm = cmd("move_bookmark", "--id", bm_id, "--start", str(s2), "--end", str(e2),
                 key="sy-bm1m")
        pt = cmd("tombstone_highlight", "--id", hid, key="sy-hl1t")
        r10 = sync()
        # the identity bridge for the referenced highlight
        shid = srv_note(hid)
        n10_srv = srv_note(n10)
        fam_counts = []
        for tbl in ("source", "highlight", "bookmark", "note", "command_log"):
            fam_counts.append((audit(LOC, f"SELECT count(*) FROM arv.{tbl} WHERE owner_scope='A';"),
                               audit(SRV, f"SELECT count(*) FROM arv.{tbl} WHERE owner_scope='A';")))
        refs_srv = audit_rows(SRV, f"SELECT ref_kind || '|' || ref_id FROM arv.note_reference "
                                   f"WHERE note_id='{n10_srv}' ORDER BY ref_kind;")
        hl_srv = audit(SRV, f"SELECT count(*) FROM arv.highlight_lifecycle WHERE owner_scope='A';")
        bm_srv = audit_rows(SRV, f"SELECT revision FROM arv.bookmark WHERE id="
                                f"'{srv_note(bm_id)}' ORDER BY revision;")
        ok10 = (ph10.returncode == 0 and pbm.returncode == 0 and pn10.returncode == 0
                and pl.returncode == 0 and prs.returncode == 0 and pm.returncode == 0
                and pt.returncode == 0 and r10.returncode == 0
                and all(a == b for a, b in fam_counts)
                and refs_srv == [f"highlight|{shid}"]
                and hl_srv == "1" and bm_srv == ["1", "2"]
                and ob(LOC, "sy-n10r") == "acknowledged")
        check("SYN-10", ok10,
              "the independent remote read: after one sync pass over a full-family sequence (highlight revise, bookmark create+move, note create with a version-aware reference, tombstone, restore, highlight tombstone) the arv_read counts per family equal the local truth on BOTH domains; the note's reference row points at the SERVER's highlight id (the identity bridge — the reference survived the domain crossing); the highlight's lifecycle event landed; the bookmark carries both revisions — the count-and-content equality of SYS-08's acceptance",
              "the equality is per-family counts + per-entity chains + contents (never raw id equality — the two domains mint their own ids; the bridge is the two idempotency ledgers)")

        # ---- SYN-11 — the outbox substrate guards (the hostile matrix; the
        # mutations run as the SUPERUSER — arv_app holds no DELETE on arv.outbox
        # by grant, so the triggers are the remaining guard and must fire BY NAME)
        pg11 = cmd("create_note", "--content", "The guard note: the sentinel token.",
                   key="sy-guard1")
        # the attempts-decrease guard needs a NON-terminal row with a legal
        # same-state edge (delivered->delivered): the terminal-row mutations
        # fire the transition guard first — the correct order, so the 006 pin
        # rides its own delivered-state row
        app_sql(LOC, "UPDATE arv.outbox SET state='delivered', attempts=1, "
                     "updated_at=now() WHERE owner_scope='A' "
                     "AND idempotency_key='sy-guard1';")
        def _su(sql: str) -> subprocess.CompletedProcess:
            return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                                   "-U", "postgres", "-d", LOC, "-c", sql],
                                  capture_output=True, text=True, timeout=60, env=ENV)
        d_del = _su("DELETE FROM arv.outbox WHERE owner_scope='A' AND idempotency_key='sy-n1';")
        d_ret = _su("UPDATE arv.outbox SET payload='{\"x\":1}' "
                    "WHERE owner_scope='A' AND idempotency_key='sy-n1';")
        d_bh = _su("UPDATE arv.outbox SET body_hash='deadbeef' "
                   "WHERE owner_scope='A' AND idempotency_key='sy-n1';")
        d_key = _su("UPDATE arv.outbox SET idempotency_key='hijack' "
                    "WHERE owner_scope='A' AND idempotency_key='sy-n1';")
        d_bad = _su("UPDATE arv.outbox SET state='acknowledged' "
                    "WHERE owner_scope='A' AND idempotency_key='sy-n1';")
        d_dec = _su("UPDATE arv.outbox SET attempts=attempts-1 "
                    "WHERE owner_scope='A' AND idempotency_key='sy-guard1';")
        cols = audit_rows(LOC, "SELECT column_name FROM information_schema.columns "
                               "WHERE table_schema='arv' AND table_name='outbox' "
                               "ORDER BY ordinal_position;")
        rls = audit_rows(LOC, "SELECT relrowsecurity::text || '|' || "
                              "relforcerowsecurity::text FROM pg_class "
                              "WHERE oid='arv.outbox'::regclass;")
        grants = audit(LOC, "SELECT count(*) FROM (SELECT unnest(relacl) AS a FROM pg_class "
                            "WHERE oid='arv.outbox'::regclass) x WHERE a::text "
                            "LIKE 'arv_app=arw/%';")
        stchk = audit_rows(LOC, "SELECT conname FROM pg_constraint WHERE conrelid="
                                "'arv.outbox'::regclass AND contype='c' ORDER BY conname;")
        ok11 = (all("ARV-SYN-007" in r.stderr for r in (d_del,))
                and all("ARV-SYN-004" in r.stderr for r in (d_ret, d_bh, d_key))
                and "ARV-SYN-005" in d_bad.stderr
                and "ARV-SYN-006" in d_dec.stderr
                and cols == ["owner_scope", "seq", "idempotency_key", "client_id",
                             "actor", "command_name", "body_hash", "payload", "state",
                             "attempts", "last_reason", "server_ref", "created_at",
                             "updated_at"]
                and rls == ["true|true"] and grants == "1"
                and any("state" in c for c in stchk)
                and hostile.stdout.strip().split("\n")[-1] == "0")
        check("SYN-11", ok11,
              "the outbox substrate guards: DELETE refused (ARV-SYN-007 — the sync-intent audit trail is authoritative state, RTM §4.4); the delivery keys immutable after enqueue (payload, body_hash, idempotency_key — ARV-SYN-004, the tamper guard); the illegal transition refused (acknowledged from acknowledged's terminal form and the pending->acknowledged shortcut — ARV-SYN-005, the declared graph); attempts never decrease (ARV-SYN-006); the 14-column schema exact, RLS enabled AND forced, arv_app holds UPDATE (the transitions) beside INSERT/SELECT — the hostile matrix of the substrate law",
              "the substrate guards are the backstop behind the driver: a hostile direct-SQL writer meets the same named refusals the command path would — never a silent mutation of sync intent")

        # ---- SYN-12 — the status arm (the honest queued state)
        pr12 = cmd("create_note", "--content", "The status note: the meridian token.",
                   key="sy-st1")
        s12 = status()
        pending_count = audit(LOC, "SELECT count(*) FROM arv.outbox WHERE owner_scope='A' "
                                   "AND state='pending';")
        sync()  # settle
        s12b = status()
        ok12 = (pr12.returncode == 0 and s12.returncode == 0
                and f"pending={pending_count}" in s12.stdout
                and "meridian" not in s12.stdout
                and s12b.returncode == 0
                and "acknowledged=" in s12b.stdout
                and "SYNC-STATUS" in s12b.stdout)
        check("SYN-12", ok12,
              "the status arm: the per-state counts printed honest against the independent arv_read count (the pending row visible as queued — the honest state, never an error); after the settling pass the acknowledged count renders; the payload contents never leak into the status line (the locator vocabulary only) — the ladder's queued/retryable/server_durable states are first-class query surface",
              "the status arm reads through the same owner-scoped session (RLS) — the counts are the owner's own truth, and the states are the RTM §4.3 vocabulary verbatim")

        # ---- SYN-13 — the server-outbox handoff (D-018/D-032)
        applied_keys = audit_rows(SRV, "SELECT idempotency_key FROM arv.command_log "
                                       "WHERE owner_scope='A' ORDER BY idempotency_key;")
        handoff_keys = audit_rows(SRV, "SELECT idempotency_key FROM arv.server_outbox "
                                       "WHERE owner_scope='A' ORDER BY idempotency_key;")
        handoff_states = audit_rows(SRV, "SELECT DISTINCT state FROM arv.server_outbox "
                                         "WHERE owner_scope='A' ORDER BY state;")
        local_handoff = audit(LOC, "SELECT count(*) FROM arv.server_outbox;")
        # a replayed delivery adds NO new handoff row
        app_sql(LOC, "UPDATE arv.outbox SET state='retryable', updated_at=now() "
                     "WHERE owner_scope='A' AND idempotency_key='sy-st1';")
        h_before = audit(SRV, "SELECT count(*) FROM arv.server_outbox WHERE owner_scope='A';")
        sync()
        h_after = audit(SRV, "SELECT count(*) FROM arv.server_outbox WHERE owner_scope='A';")
        # the append-only law: the hostile mutations run as the SUPERUSER (the
        # only role that passes the grant layer — arv_app holds INSERT/SELECT
        # only, so the trigger is the remaining guard and must fire BY NAME)
        h_up = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                               "-U", "postgres", "-d", SRV, "-c",
                               "UPDATE arv.server_outbox SET state='enriched' "
                               "WHERE owner_scope='A' AND idempotency_key='sy-n1';"],
                              capture_output=True, text=True, timeout=60, env=ENV)
        h_del = subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                               "-U", "postgres", "-d", SRV, "-c",
                               "DELETE FROM arv.server_outbox WHERE owner_scope='A' "
                               "AND idempotency_key='sy-n1';"],
                              capture_output=True, text=True, timeout=60, env=ENV)
        srls = audit_rows(SRV, "SELECT relrowsecurity::text || '|' || "
                               "relforcerowsecurity::text FROM pg_class "
                               "WHERE oid='arv.server_outbox'::regclass;")
        ok13 = (applied_keys == handoff_keys and handoff_states == ["pending"]
                and local_handoff == "0"
                and h_before == h_after
                and "ARV-SYN-010" in h_up.stderr and "ARV-SYN-010" in h_del.stderr
                and srls == ["true|true"])
        check("SYN-13", ok13,
              "the server-outbox handoff: every server-APPLIED command carries its pending enrichment row ATOMICALLY (the server's command-log key set == the handoff key set — one transaction, D-018); a REPLAYED delivery adds none (the replay path inserts nothing); the local domain's handoff table stays empty (local commands never enrich — the site split); the table is append-only at the substrate (ARV-SYN-010 refuses both the update and the delete — the enrichment consumers land as their own P4+ slices over this contract); RLS forced",
              "the handoff is the D-018 separation made mechanical: the client outbox bridges durability domains, the server outbox hands off to the enrichment future — two tables, two laws, never one mixed surface")

        # ---- SYN-14 — the ordering law (the sequence discipline)
        pr14 = cmd("create_note", "--content", "The ordering note: the zenia token.",
                   key="sy-o1")
        o1 = ack_field(pr14, "result_ref")
        pr14b = cmd("revise_note", "--id", o1, "--content",
                    "The ordering note revised: the zephyr token.", key="sy-o2")
        pr14c = cmd("tombstone_note", "--id", o1, key="sy-o3")
        pr14d = cmd("restore_note", "--id", o1, key="sy-o4")
        r14 = sync()
        so1 = srv_note(o1)
        revs14 = audit_rows(SRV, f"SELECT revision FROM arv.note WHERE id='{so1}' "
                                 f"ORDER BY revision;")
        ev14 = audit_rows(SRV, f"SELECT event FROM arv.note_lifecycle WHERE note_id='{so1}' "
                               f"ORDER BY created_at, id;")
        states14 = audit_rows(LOC, "SELECT state FROM arv.outbox WHERE owner_scope='A' "
                                   "AND idempotency_key IN ('sy-o1','sy-o2','sy-o3','sy-o4') "
                                   "ORDER BY idempotency_key;")
        g14 = cli(str(REPO / "harness" / "query.py"), "get-note", "--owner", "A", "--id", o1)
        ok14 = (r14.returncode == 0 and states14 == ["acknowledged"] * 4
                and [r.split("|")[0] for r in revs14] == ["1", "2"]
                and ev14 == ["tombstone", "restore"]
                and g14.returncode == 0 and "zephyr" in g14.stdout)
        check("SYN-14", ok14,
              "the ordering law: the driver delivers in outbox sequence — create precedes revise precedes tombstone precedes restore; the server's note carries the revision chain 1,2 in order and its lifecycle events in commit order (tombstone then restore — a wrong order would have refused: revise-after-tombstone is ARV-NTE-002, restore-before-tombstone is ARV-NTE-005); all four rows acknowledged; the local read confirms the restored current revision — the sequence discipline is the delivery's own law, never the truth's",
              "ORDER BY seq within the owner's rows; the referencer's identity bridge resolves only after its creator's acknowledgment (the same pass's earlier row) — the ordering is structural, never incidental")

        # ---- SYN-15 — the no-lost-writes acceptance (the global sweep)
        prod = "('import_source','create_highlight','revise_highlight','tombstone_highlight',\
'restore_highlight','create_bookmark','move_bookmark','tombstone_bookmark','restore_bookmark',\
'create_note','revise_note','tombstone_note','restore_note')"
        loc_keys = set(audit_rows(LOC, f"SELECT idempotency_key FROM arv.command_log "
                                       f"WHERE owner_scope='A' AND command_name IN {prod};"))
        ob_keys = set(audit_rows(LOC, "SELECT idempotency_key FROM arv.outbox "
                                      "WHERE owner_scope='A';"))
        srv_keys = set(audit_rows(SRV, f"SELECT idempotency_key FROM arv.command_log "
                                       f"WHERE owner_scope='A';"))
        ack_keys = set(audit_rows(LOC, "SELECT idempotency_key FROM arv.outbox "
                                       "WHERE owner_scope='A' AND state='acknowledged';"))
        fail409 = set(audit_rows(LOC, "SELECT o.idempotency_key FROM arv.outbox o "
                                      "WHERE o.owner_scope='A' AND o.state='failed' "
                                      "AND o.last_reason LIKE '%ARV-CMD-409%';"))
        bad_rows = audit_rows(LOC, "SELECT idempotency_key FROM arv.outbox WHERE owner_scope='A' "
                                   "AND ((state='acknowledged' AND (server_ref IS NULL OR server_ref='')) "
                                   "OR ((state IN ('retryable','failed','uncertain')) "
                                   "AND (last_reason IS NULL OR last_reason='')) "
                                   "OR (state='pending'));")
        ok15 = (loc_keys == ob_keys
                and srv_keys == (ack_keys | fail409)
                and not bad_rows)
        check("SYN-15", ok15,
              "the no-lost-writes acceptance: every local product command's key has exactly one outbox row (the enqueue never misses — the atomic law held for the whole suite's traffic); the server's command-log key set == the acknowledged set plus the 409-failed set (every delivered row reached the server exactly once — no lost writes, and the only non-acknowledged terminal is the TYPED conflict); every row rests in a truthful state (acknowledged carries its server_ref; retryable/failed/uncertain carry the named reason; zero rows left pending) — the acceptance's 'each committed local write is either server-durable or explicitly queued/retryable' over the ENTIRE matrix",
              "the sweep is global over the suite's traffic — any silent drop, any duplicate, any reason-less failure state fails it; this is the acceptance pin of PLAN's P3-08 card")

        # ---- SYN-16 — the poisoned-payload containment (the SEV round-1 F1)
        pr16 = cmd("create_note", "--content", "The post-poison note: the heliotrope.",
                   key="sy-poison2")
        app_sql(LOC, "INSERT INTO arv.outbox (owner_scope, idempotency_key, client_id, "
                     "actor, command_name, body_hash, payload, state, attempts, "
                     "created_at, updated_at) VALUES ('A', 'sy-poison1', 'cli-1', 'owner', "
                     "'create_note', '" + "0" * 64 + "', 'not-json-at-all', 'pending', 0, "
                     "now(), now());")
        r16 = sync()
        st16 = ob(LOC, "sy-poison1")
        reason16 = ob(LOC, "sy-poison1", "last_reason") or ""
        st16b = ob(LOC, "sy-poison2")
        sn16 = srv_note(ack_field(pr16, "result_ref")) if pr16.returncode == 0 else ""
        c16 = audit(SRV, f"SELECT content FROM arv.note WHERE id='{sn16}';") if sn16 else ""
        ok16 = (pr16.returncode == 0 and r16.returncode == 0
                and st16 == "failed" and "ARV-SYN-013" in reason16
                and st16b == "acknowledged" and "heliotrope" in c16)
        check("SYN-16", ok16,
              "the poisoned-payload containment: a hostile outbox row whose payload is not the canonical JSON (inserted directly at the substrate — the append-only keys accept the INSERT, no shape guard exists by design) is a NAMED terminal failure for THAT row (ARV-SYN-013, the undeliverable class) and the walk CONTINUES — the later row delivers and acknowledges; never an unhandled crash, never a blocked queue",
              "per-row error containment: one corrupted row may never block every later row in every subsequent pass — the driver names the failure, fails the row, and moves on")

        # ---- SYN-17 — the divergent-bridge containment (the SEV round-1 F2, THE P0)
        d17 = cmd("create_note", "--content", "The server's divergent creator body.",
                  key="sy-div1", env=srv_env)
        l17 = cmd("create_note", "--content", "The local divergent creator body.",
                  key="sy-div1")
        pr17 = cmd("revise_note", "--id", ack_field(l17, "result_ref"), "--content",
                   "The referencer revision: the indigo token.", key="sy-div2")
        r17 = sync()
        st17 = ob(LOC, "sy-div1")
        st17b = ob(LOC, "sy-div2")
        reason17b = ob(LOC, "sy-div2", "last_reason") or ""
        div_srv_note = audit(SRV, "SELECT id FROM arv.note WHERE owner_scope='A' "
                                  "AND content='The server''s divergent creator body.';")
        div_srv_revs = audit(SRV, f"SELECT count(*) FROM arv.note WHERE id='{div_srv_note}';")
        ok17 = (d17.returncode == 0 and l17.returncode == 0 and pr17.returncode == 0
                and r17.returncode == 0
                and st17 == "failed" and "ARV-CMD-409" in (ob(LOC, "sy-div1", "last_reason") or "")
                and "ARV-SYN-009" in reason17b
                and div_srv_revs == "1")
        check("SYN-17", ok17,
              "the divergent-bridge containment: the creator's delivery failed the typed 409 conflict (the server carries the key with a DIFFERENT body — a competing logical command); the referencer NEVER translates through the competing server answer — the identity bridge resolves only through creators whose own delivery rests acknowledged, so the referencer holds the named ARV-SYN-009 dependency instead of delivering against the WRONG entity; the server's competing note stays exactly one revision — no effect from the local lineage ever lands on it",
              "the bridge's soundness gate: a server command_log answer is a valid translation ONLY when the local outbox row for the creating command rests acknowledged — the 409-divergent answer belongs to a different logical command and must never satisfy a referencer")

        # ---- SYN-18 — the position delivery (the SEV round-1 F1 repair: the
        # dead letter closed — save_position joins the outbox-carrying set's
        # DELIVERY half, not just its enqueue half)
        # the site-local binding law: the delivered save binds the SERVER's own
        # serving generation — the rig extracts on BOTH sites (the local save
        # needs the local generation, the delivered save the server's), and the
        # pin asserts the server row's generation IS the server's, never the
        # local uuid transplanted
        ex_loc = cli(str(REPO / "harness" / "extract.py"), "--owner", "A", "--actor",
                     "owner", "--client-id", "cli-1", "--idem-key", "sy-extloc1",
                     "--source-id", sid, env=ENV)
        srv_sid = audit(SRV, "SELECT result_ref FROM arv.command_log "
                             "WHERE owner_scope='A' AND idempotency_key='sy-imp1';")
        ex_srv = cli(str(REPO / "harness" / "extract.py"), "--owner", "A", "--actor",
                     "owner", "--client-id", "cli-1", "--idem-key", "sy-extsrv1",
                     "--source-id", srv_sid, env=srv_env)
        s3 = TEXT.index("persistent anchor")
        p_pos = cmd("save_position", "--source-id", sid, "--start", str(s3),
                    "--end", str(s3 + 8), key="sy-pos1")
        r18 = sync()
        st18 = ob(LOC, "sy-pos1")
        ref18 = ob(LOC, "sy-pos1", "server_ref")
        srv_pos = audit(SRV, f"SELECT start_off || '|' || end_off || '|' || generation_id "
                             f"FROM arv.reading_position WHERE owner_scope='A' "
                             f"AND source_id='{srv_sid}';")
        srv_gen = audit(SRV, f"SELECT id FROM arv.extraction_generation "
                             f"WHERE source_id='{srv_sid}' AND state='current' "
                             f"ORDER BY ordinal DESC LIMIT 1;")
        loc_gen = audit(LOC, f"SELECT id FROM arv.extraction_generation "
                             f"WHERE source_id='{sid}' AND state='current' "
                             f"ORDER BY ordinal DESC LIMIT 1;")
        g18 = cli(str(REPO / "harness" / "query.py"), "get-position", "--owner", "A",
                  "--source", srv_sid, env=srv_env)
        ok18 = (ex_loc.returncode == 0 and ex_srv.returncode == 0
                and p_pos.returncode == 0 and f"result_ref={sid}@1" in p_pos.stdout
                and r18.returncode == 0
                and st18 == "acknowledged" and ref18 == f"{srv_sid}@1"
                and srv_pos == f"{s3}|{s3 + 8}|{srv_gen}"
                and srv_gen and srv_gen != loc_gen
                and g18.returncode == 0 and '"state": "saved"' in g18.stdout
                and '"save_ordinal": 1' in g18.stdout)
        check("SYN-18", ok18,
              "the position delivery (the SEV round-1 F1 repair): the save_position outbox row DELIVERS — "
              "the server-side save re-executes through the TRANSLATED source id, binds the SERVER's own "
              "serving generation (the site-local binding law: each site's rows bind that site's generation "
              "ids — the pin asserts the server row's generation IS the server's, and the two sites' "
              "generation uuids differ), acks <server-source>@1, and the row acknowledges with its "
              "server_ref; the server's read arm answers the delivered row (state=saved, ordinal 1) — "
              "never a dead letter in the outbox-carrying set",
              "harness/sync.py _cli_args' save_position branch (the translated source id + the offsets) — "
              "the command was already in _SYNC_COMMANDS (the enqueue); the delivery completes the "
              "no-lost-writes law for the position family")

        print()
        if FAILS:
            print(f"RED — the P3-08 sync suite fails: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-08 acceptance suite (SYN-01..18) passes")
        return 0
    finally:
        pg.drop_scratch_db(LOC)
        pg.drop_scratch_db(SRV)


if __name__ == "__main__":
    sys.exit(main())
