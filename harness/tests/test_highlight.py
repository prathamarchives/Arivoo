#!/usr/bin/env python3
"""harness/tests/test_highlight.py — P3-04 acceptance suite (the Highlight
revision/tombstone machine's contract pins; RTM §2.5 item 5 + §3.3, SYS-01/02/05,
PLAN's P3-04 card).

Red-first (LAW-11): committed BEFORE the implementation; at the predecessor
b200e55 the suite fails with ARV-TEST-000 (machinery-absent: commands.py's
revise_highlight/tombstone_highlight/restore_highlight and query.py's
get-history arm do not exist — the record-18 §4.1 precedent class).

THE MACHINE (RTM §3.3 — active --edit--> active(revision n+1); active
--delete--> tombstoned --restore--> active, current revision unchanged; the
governed purge is P3-06/09's, NEVER this slice's):

  revisions    a NEW immutable row per edit, PK (id, revision) — the prior
               revision byte-unchanged (SYS-02); the selected content is
               RE-DERIVED from the SAME Source version's stored bytes at new
               offsets (the quote/anchor slice invariant: a client never
               supplies anchor truth) + a NEW anchor row (append-only; the
               prior revision's anchor stays, referenced by the prior row);
               the source reference is IDENTITY-FIXED by construction — a
               revision NEVER crosses Source versions (SYS-05's wrong-version
               class refused; re-import/edition-change never retargets)
  tombstone    a typed lifecycle EVENT row (append-only, owner-scoped,
               provenance-complete); tombstoned hides from ordinary retrieval
               (list excludes, get refuses with the typed ARV-QRY-003) while
               the governed history (get-history) retains every revision and
               every event; the current view is DERIVED from the events
               (rebuildable — no state column duplicating a derivable fact)
  alternation  tombstone only from active; restore only from tombstoned —
               named refusals at the command boundary (ARV-HLC-001 absent/
               cross-owner the SAME refusal, never a side channel; ARV-HLC-002
               revise-of-tombstoned; ARV-HLC-003 double-tombstone; ARV-HLC-004
               restore-of-active) + the DB-level backstop (the advisory-lock
               alternation trigger — races and hostile direct writes are
               refused at the substrate)
  acks         every highlight-family ack names durability_rung=local_durable
               (SYS-01 — the rung the local store independently knows; queued/
               server_durable arrive with P3-08's sync, never claimed early)

Cases (the HLG registry — this file is the contract's declaration):
  HLG-01 the revision happy path: revise appends revision 2 (re-derived
         content at new offsets + a NEW anchor row); the prior revision
         byte-unchanged (independent read); the ack carries revision=2 and
         durability_rung=local_durable
  HLG-02 mutation rejection on the authored rows: direct-DB UPDATE and
         DELETE on arv.highlight refused by ARV-CAP-005 (SYS-02's append-only
         law at the substrate); the history intact after (the lifecycle
         arms are pinned at HLG-06, where event rows exist)
  HLG-03 dangling/absent references + cross-owner isolation: revise/
         tombstone/restore on an absent id and on ANOTHER OWNER's highlight
         are the SAME ARV-HLC-001 refusal (never a side channel); the other
         owner's history never observable
  HLG-04 same-key replay + conflicting body + the ordinal backstop: same
         key+body -> status=replayed (one effect); same key+different body
         -> ARV-CMD-409 (zero effect); a direct-DB duplicate (id, revision)
         insert -> the PK violation (the concurrent-loser backstop)
  HLG-04b the two-process revise race: every lawful outcome (the loser's
         011 zero-effect, or serialization) leaves the ordinals contiguous
  HLG-05 the crash matrix at each transactional boundary: revise + tombstone
         at after-begin / pre-commit (zero effect) and post-commit-pre-ack
         (the lost ack: the effect IS committed, no ack); the same-key
         replay converges the lost ack to the recorded result
  HLG-06 the tombstone/restore machine: tombstoned hidden from get-capture
         (ARV-QRY-003) and list-captures; get-history retains everything;
         restore returns it; double-tombstone (ARV-HLC-003), restore-of-
         active (ARV-HLC-004), revise-of-tombstoned (ARV-HLC-002) refused;
         the lifecycle rows' own UPDATE/DELETE refused (ARV-CAP-005); the
         DB alternation trigger refuses the hostile direct duplicate
  HLG-07 the identity-fix pin (source re-import): a NEW edition (source v2)
         of the same work NEVER retargets a highlight — revise still binds
         the ORIGINAL source version; every revision carries the same
         source_id (SYS-05's never-silent-retarget)
  HLG-08 re-extraction stability: a new generation over the same source
         version leaves every revision's anchor and the history untouched;
         resolve-anchor still resolves (the typed surface unchanged)
  HLG-09 the independent current-view rebuild: the current view (active
         state + the current revision's content) re-derived from the
         get-history rows ALONE equals the get-capture answer (SYS-02's
         rebuildable-views acceptance)
  HLG-10 the ack-rung pins: create/revise/tombstone/restore acks ALL name
         durability_rung=local_durable (SYS-01)
  HLG-11 the schema-convention audits (0007): no DEFAULTs on identity/time
         (LAW-24), the append-only + alternation triggers, RLS forced + the
         owner policy, the grants (arv_app insert/select; arv_read select),
         the highlight identity constraint, the composite-FK convention
  HLG-12 the row-protocol framing on the history arm: a selected text
         containing U+2028 (legal in a JSON string, never escaped by
         row_to_json) survives get-history with intact newline-only framing
         (the #88 round-2 lesson on the new arm)

Run: python3 harness/tests/test_highlight.py   (exit 0 = green)
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

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


# ---------------------------------------------------------------- the RED gate
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                          "revise_highlight", "--help"], capture_output=True, text=True)
_absent_cmd = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "get-history", "--owner", "A", "--id", "x"],
                         capture_output=True, text=True, timeout=60)
_absent_arm = "invalid choice" in _probe2.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0007_*.sql"))
if _absent_cmd or _absent_arm or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-04 machinery is absent (machinery-absent "
          f"class; revise_highlight command absent: {_absent_cmd}; get-history "
          f"arm absent: {_absent_arm}; migration 0007 present: {bool(_mig)}) — "
          "the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

# ---------------------------------------------------------------- the harness
from harness.adapters import pg  # noqa: E402

DB = ENV = None
TEXT = ("The compound act of reading.\n"
        "Second paragraph: the first selection lives here, plainly.\n"
        "Third paragraph: the revised selection lives here instead.\n"
        "Fourth paragraph closes.\n")


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=180, env=ENV)


def import_src(key: str, title: str, file: str, owner: str = "A",
               media: str = "text/plain", work_id: str = None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), "import_source", "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
         "--file", file, "--media-type", media]
    if title is not None:
        a += ["--title", title]
    if work_id:
        a += ["--work-id", work_id]
    return cli(*a)


def mk_highlight(key: str, source_id: str, start: int, end: int,
                 owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "create_highlight",
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--source-id", source_id,
               "--start", str(start), "--end", str(end))


def revise(key: str, hl_id: str, start: int, end: int, owner: str = "A",
           client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "revise_highlight",
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--id", hl_id, "--start", str(start), "--end", str(end))


def lifecycle(op: str, key: str, hl_id: str, owner: str = "A",
              client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), op,
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--id", hl_id)


def crash(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "crash.py"), *args)


def qy(arm: str, owner: str, id_: str) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), arm, "--owner", owner, "--id", id_)


def audit(query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_read", "-d", DB, "-c", query],
                           capture_output=True, text=True, timeout=60,
                           env=ENV).stdout.strip()


def audit_rows(query: str) -> list:
    return [ln for ln in audit(query).splitlines() if ln.strip()]


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    """A hostile/direct write attempt AS the app role (the substrate's own guard)."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_app", "-d", DB,
                            "-c", f"SET app.current_owner='{owner}'; {sql}"],
                           capture_output=True, text=True, timeout=60, env=ENV)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def history_rows(owner: str, hl_id: str) -> list:
    p = qy("get-history", owner, hl_id)
    if p.returncode != 0:
        return []
    return [json.loads(ln) for ln in p.stdout.split("\n") if ln.strip()]


def derived_state(rows: list) -> str:
    """The current lifecycle view DERIVED from the history rows alone (parity)."""
    evs = [r for r in rows if r.get("kind") == "lifecycle"]
    t = sum(1 for e in evs if e["event"] == "tombstone")
    r = sum(1 for e in evs if e["event"] == "restore")
    return "tombstoned" if t > r else "active"


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p304")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ---------------- the fixture: real bytes, two owners
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "revisions.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("first selection")
        e1 = s1 + len("first selection")
        s2 = TEXT.index("revised selection")
        e2 = s2 + len("revised selection")

        p = import_src("imp-A", "Revisions", str(src_file))
        sid_a = ack_field(p, "result_ref")
        wid_a = ack_field(p, "work_id")
        p = mk_highlight("hl-A1", sid_a, s1, e1)
        h1 = ack_field(p, "result_ref")
        pb = import_src("imp-B", "B's book", str(src_file), owner="B")
        sid_b = ack_field(pb, "result_ref")
        pb = mk_highlight("hl-B1", sid_b, s1, e1, owner="B")
        hb = ack_field(pb, "result_ref")

        # ---- HLG-01 — the revision happy path
        p = revise("rev-A1", h1, s2, e2)
        rev2 = ack_field(p, "revision")
        rung = ack_field(p, "durability_rung")
        rows = audit_rows(f"SELECT revision || '|' || selected_text || '|' || anchor_id FROM "
                          f"arv.highlight WHERE id='{h1}' ORDER BY revision;")
        hist_revs = [r for r in history_rows("A", h1) if r.get("kind") == "revision"]
        ok1 = (p.returncode == 0 and "status=committed" in p.stdout
               and rev2 == "2" and rung == "local_durable"
               and len(rows) == 2
               and rows[0].split("|")[0] == "1" and rows[0].split("|")[1] == TEXT[s1:e1]
               and rows[1].split("|")[0] == "2" and rows[1].split("|")[1] == TEXT[s2:e2]
               and rows[0].split("|")[2] != rows[1].split("|")[2]      # a NEW anchor row
               and len(hist_revs) == 2)
        check("HLG-01", ok1,
              "revise appends immutable revision 2 (re-derived content + a NEW anchor row); the prior revision byte-unchanged; the ack carries revision=2 + durability_rung=local_durable",
              "the revision machine must append a new immutable row derived from the same source version's stored bytes, never mutate the prior row")

        # ---- HLG-02 — mutation rejection on the authored rows
        before = audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';")
        up = app_sql(f"UPDATE arv.highlight SET selected_text='forged' WHERE id='{h1}';")
        dele = app_sql(f"DELETE FROM arv.highlight WHERE id='{h1}';")
        after = audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';")
        sel1 = audit(f"SELECT selected_text FROM arv.highlight WHERE id='{h1}' AND revision=1;")
        ok2 = ("ARV-CAP-005" in up.stderr and "ARV-CAP-005" in dele.stderr
               and before == after == "2" and sel1 == TEXT[s1:e1])
        check("HLG-02", ok2,
              "direct-DB UPDATE/DELETE on the authored rows refused (ARV-CAP-005); the history intact after",
              "the append-only trigger must refuse every mutation of the authoritative rows (SYS-02)")

        # ---- HLG-03 — dangling/absent + cross-owner isolation
        pr1 = revise("rev-abs", "00000000-0000-7000-8000-000000000001", s1, e1)
        pr2 = revise("rev-Bsteal", hb, s1, e1)                     # A revising B's highlight
        pt1 = lifecycle("tombstone_highlight", "tomb-abs",
                        "00000000-0000-7000-8000-000000000002")
        pt2 = lifecycle("tombstone_highlight", "tomb-Bsteal", hb)   # A tombstoning B's
        pr3 = lifecycle("restore_highlight", "res-Bsteal", hb)       # A restoring B's
        ok3 = (pr1.returncode == 1 and "ARV-HLC-001" in pr1.stdout
               and pr2.returncode == 1 and "ARV-HLC-001" in pr2.stdout
               and pt1.returncode == 1 and "ARV-HLC-001" in pt1.stdout
               and pt2.returncode == 1 and "ARV-HLC-001" in pt2.stdout
               and pr3.returncode == 1 and "ARV-HLC-001" in pr3.stdout
               and audit(f"SELECT count(*) FROM arv.highlight WHERE id='{hb}';") == "1"
               and qy("get-history", "A", hb).returncode == 1)      # B's history never observable
        check("HLG-03", ok3,
              "absent + cross-owner references are the SAME ARV-HLC-001 refusal on every arm (revise/tombstone/restore); the other owner's history never observable",
              "never a side channel: an out-of-scope id and a nonexistent id are indistinguishable (RTM §2.10)")

        # ---- HLG-04 — same-key replay + conflicting body + the ordinal backstop
        n_before = audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';")
        p_replay = revise("rev-A1", h1, s2, e2)                    # the SAME key + body
        p_conflict = revise("rev-A1", h1, s1, e1)                   # the SAME key, DIFFERENT body
        n_after = audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';")
        dup = app_sql(f"INSERT INTO arv.highlight (id, revision, selected_text, source_id, anchor_id, "
                      f"owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
                      f"SELECT id, 2, selected_text, source_id, anchor_id, owner_scope, actor, run_id, "
                      f"input_hash, 'hostile-dup', created_at FROM arv.highlight WHERE id='{h1}' AND revision=1;")
        contig = audit_rows(f"SELECT revision FROM arv.highlight WHERE id='{h1}' ORDER BY revision;")
        ok4 = (p_replay.returncode == 0 and "status=replayed" in p_replay.stdout
               and p_conflict.returncode == 1 and "ARV-CMD-409" in p_conflict.stdout
               and n_before == n_after
               and "duplicate key" in dup.stderr                      # the PK backstop
               and contig == [str(i) for i in range(1, len(contig) + 1)])
        check("HLG-04", ok4,
              "same key+body replays (one effect); same key+different body refuses ARV-CMD-409 (zero effect); a duplicate (id, revision) insert violates the PK",
              "exactly-once is a contract: the replay returns the recorded result, the conflict refuses, the ordinal race backs onto the PK")

        # ---- HLG-04b — the two-process revise race (every lawful outcome)
        ra = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                               "revise_highlight", "--owner", "A", "--actor", "owner",
                               "--client-id", "cli-r", "--idem-key", "race-A",
                               "--id", h1, "--start", str(s1), "--end", str(e1)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        rb = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                               "revise_highlight", "--owner", "A", "--actor", "owner",
                               "--client-id", "cli-r", "--idem-key", "race-B",
                               "--id", h1, "--start", str(s2), "--end", str(e2)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        ra.communicate(timeout=180)
        rb.communicate(timeout=180)
        contig2 = audit_rows(f"SELECT revision FROM arv.highlight WHERE id='{h1}' ORDER BY revision;")
        race_ok = (len(contig2) in (3, 4)
                   and contig2 == [str(i) for i in range(1, len(contig2) + 1)]
                   and all(a_ != "" for a_ in audit_rows(
                       "SELECT h.anchor_id FROM arv.highlight h JOIN arv.anchor a ON a.id=h.anchor_id "
                       f"WHERE h.id='{h1}' ORDER BY h.revision;")))
        check("HLG-04b", race_ok,
              "the concurrent revise race: both writers finish, every lawful outcome leaves the ordinals contiguous (the loser's 011 is zero-effect; serialization is lawful too)",
              "the ordinal convention: the loser's insert aborts — an honest retry re-reads; never a gap, never a duplicate ordinal")

        # ---- HLG-05 — the crash matrix (revise + tombstone at each boundary)
        n0 = int(audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';"))
        c1 = crash("--command", "revise_highlight", "--point", "after-begin",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-r1",
                   "--id", h1, "--start", str(s1), "--end", str(e1))
        c2 = crash("--command", "revise_highlight", "--point", "pre-commit",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-r2",
                   "--id", h1, "--start", str(s1), "--end", str(e1))
        n_mid = int(audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';"))
        c3 = crash("--command", "revise_highlight", "--point", "post-commit-pre-ack",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-r3",
                   "--id", h1, "--start", str(s1), "--end", str(e1))
        n_lost = int(audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';"))
        lost_ack = revise("crash-r3", h1, s1, e1, client="cli-c")   # the same-key replay resolves it
        n_replay = int(audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';"))
        e0 = int(audit("SELECT count(*) FROM arv.highlight_lifecycle;"))
        c4 = crash("--command", "tombstone_highlight", "--point", "after-begin",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-t1", "--id", h1)
        c5 = crash("--command", "tombstone_highlight", "--point", "pre-commit",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-t2", "--id", h1)
        e_mid = int(audit("SELECT count(*) FROM arv.highlight_lifecycle;"))
        c6 = crash("--command", "tombstone_highlight", "--point", "post-commit-pre-ack",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-t3", "--id", h1)
        e_lost = int(audit("SELECT count(*) FROM arv.highlight_lifecycle;"))
        conv = lifecycle("tombstone_highlight", "crash-t3", h1, client="cli-c")
        e_conv = int(audit("SELECT count(*) FROM arv.highlight_lifecycle;"))
        ok5 = (c1.returncode == 2 and c2.returncode == 2 and c3.returncode == 2
               and c4.returncode == 2 and c5.returncode == 2 and c6.returncode == 2
               and n_mid == n0                          # after-begin + pre-commit: zero effect
               and n_lost == n0 + 1                     # post-commit-pre-ack: the effect IS committed
               and lost_ack.returncode == 0 and "status=replayed" in lost_ack.stdout
               and n_replay == n_lost                    # the replay added NOTHING
               and e_mid == e0 and e_lost == e0 + 1
               and conv.returncode == 0 and "status=replayed" in conv.stdout
               and e_conv == e_lost)
        check("HLG-05", ok5,
              "crashes at each boundary (revise + tombstone): exit 2, no ack; after-begin/pre-commit leave zero effect; post-commit-pre-ack commits the effect and the same-key replay converges to the recorded result",
              "zero-or-one effect per command, never partial (SYS-04): the commit point is the only effect boundary")

        # ---- HLG-06 — the tombstone/restore machine (a FRESH highlight: h6)
        p6 = mk_highlight("hl-A6", sid_a, s1, e1)
        h6 = ack_field(p6, "result_ref")
        p = lifecycle("tombstone_highlight", "tomb-A1", h6)
        get_t = qy("get-capture", "A", h6)
        listing = cli(str(REPO / "harness" / "query.py"), "list-captures", "--owner", "A")
        hist_t = history_rows("A", h6)
        p_restore = lifecycle("restore_highlight", "res-A1", h6)
        get_r = qy("get-capture", "A", h6)
        lifecycle("tombstone_highlight", "tomb-A2", h6)               # lawful: active -> tombstoned
        p_double = lifecycle("tombstone_highlight", "tomb-A4", h6)   # double-tombstone
        p_rev_tomb = revise("rev-tomb", h6, s1, e1)                  # revise-of-tombstoned
        lifecycle("restore_highlight", "res-A2", h6)                  # lawful: tombstoned -> active
        p_res_active = lifecycle("restore_highlight", "res-A3", h6)  # restore-of-active
        ev_count = int(audit(f"SELECT count(*) FROM arv.highlight_lifecycle WHERE highlight_id='{h6}';"))
        lifecycle("tombstone_highlight", "tomb-A5", h6)               # lawful: active -> tombstoned
        hostile = app_sql(f"INSERT INTO arv.highlight_lifecycle (id, highlight_id, event, owner_scope, "
                          f"actor, run_id, input_hash, idempotency_key, created_at) VALUES "
                          f"('00000000-0000-7000-8000-00000000000a', '{h6}', 'tombstone', 'A', "
                          f"'owner', 'hostile-run', 'hostile-hash', 'hostile-key', "
                          f"'2026-10-28T00:00:00+00:00');")
        upl = app_sql(f"UPDATE arv.highlight_lifecycle SET event='restore' WHERE highlight_id='{h6}';")
        delel = app_sql(f"DELETE FROM arv.highlight_lifecycle WHERE highlight_id='{h6}';")
        ev_after = int(audit(f"SELECT count(*) FROM arv.highlight_lifecycle WHERE highlight_id='{h6}';"))
        ok6 = (p.returncode == 0 and "status=committed" in p.stdout
               and get_t.returncode == 1 and "ARV-QRY-003" in get_t.stdout
               and h6 not in listing.stdout.split()
               and h1 not in listing.stdout.split()                   # h1 tombstoned by c6's lost-ack commit
               and len([r for r in hist_t if r.get("kind") == "lifecycle"]) == 1
               and len([r for r in hist_t if r.get("kind") == "revision"]) == 1  # history retained
               and p_restore.returncode == 0 and get_r.returncode == 0
               and p_double.returncode == 1 and "ARV-HLC-003" in p_double.stdout
               and p_rev_tomb.returncode == 1 and "ARV-HLC-002" in p_rev_tomb.stdout
               and p_res_active.returncode == 1 and "ARV-HLC-004" in p_res_active.stdout
               and ev_count == 4                                     # tomb,res,tomb,res — one per LAWFUL transition
               and "ARV-HLC-003" in hostile.stderr                   # the substrate refuses the duplicate
               and "ARV-CAP-005" in upl.stderr and "ARV-CAP-005" in delel.stderr
               and ev_after == 5)                                    # 4 lawful + tomb-A5
        check("HLG-06", ok6,
              "tombstone hides from get-capture (ARV-QRY-003) + list-captures; history retains all; restore returns it; double-tombstone/restore-of-active/revise-of-tombstoned refused by name; the lifecycle rows' own mutations refused; the DB alternation trigger refuses the hostile duplicate",
              "the §3.3 machine: alternation enforced at the command boundary AND the substrate; the governed history never loses a row")

        # ---- HLG-07 — the identity-fix pin (re-import NEVER retargets)
        lifecycle("restore_highlight", "res-A0", h1)                  # back to active for the revise
        p_v2 = import_src("imp-A2", "Revisions", str(src_file), work_id=wid_a)
        sid_v2 = ack_field(p_v2, "result_ref")
        ver = audit(f"SELECT source_version FROM arv.source WHERE id='{sid_v2}';")
        src_before = audit_rows(f"SELECT DISTINCT source_id FROM arv.highlight WHERE id='{h1}';")
        p = revise("rev-A2", h1, s1, e1)
        src_after = audit_rows(f"SELECT DISTINCT source_id FROM arv.highlight WHERE id='{h1}';")
        ok7 = (ver == "2"
               and len(src_before) == 1 and len(src_after) == 1
               and src_before == src_after
               and sid_v2 not in src_after
               and p.returncode == 0)
        check("HLG-07", ok7,
              "a new edition (source v2) NEVER retargets: every revision of the highlight still binds the ORIGINAL source version",
              "identity-fixed by construction — a revision NEVER crosses Source versions (SYS-05); the edition is a different source row")

        # ---- HLG-08 — re-extraction stability
        pe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                             "extract_source", "--owner", "A", "--actor", "owner",
                             "--client-id", "cli-1", "--idem-key", "ext-A2",
                             "--source-id", sid_a], capture_output=True, text=True,
                            env=ENV, timeout=180)
        n_rev = int(audit(f"SELECT count(*) FROM arv.highlight WHERE id='{h1}';"))
        n_anc = int(audit(f"SELECT count(*) FROM arv.highlight h JOIN arv.anchor a ON a.id=h.anchor_id "
                          f"WHERE h.id='{h1}';"))
        first_anchor = audit(f"SELECT h.anchor_id FROM arv.highlight h WHERE h.id='{h1}' "
                             f"AND h.revision=1;")
        pr = qy("resolve-anchor", "A", first_anchor)
        resolved = False
        if pr.returncode == 0 and pr.stdout.strip():
            try:
                resolved = json.loads(pr.stdout.strip().splitlines()[0]).get("state") == "resolved"
            except (json.JSONDecodeError, IndexError):
                resolved = False
        ok8 = (pe.returncode == 0 and n_anc == n_rev and resolved)
        check("HLG-08", ok8,
              "a new generation over the same source version leaves every revision's anchor intact (one per revision); resolve-anchor still resolves revision 1's anchor",
              "derived state is disposable; the authoritative anchor rows never move under a re-extraction (SYS-07)")

        # ---- HLG-09 — the independent current-view rebuild
        hist = history_rows("A", h1)
        state = derived_state(hist)
        revs = [r for r in hist if r.get("kind") == "revision"]
        max_rev = max(r["revision"] for r in revs)
        cur_hist = next(r for r in revs if r["revision"] == max_rev)
        getc = qy("get-capture", "A", h1)
        cur_view = json.loads(getc.stdout.splitlines()[0]) if getc.returncode == 0 else {}
        ok9 = (state == "active"
               and cur_view.get("revision") == max_rev
               and cur_view.get("selected_text") == cur_hist["selected_text"]
               and cur_view.get("id") == h1)
        check("HLG-09", ok9,
              "the current view re-derived from the get-history rows ALONE equals the get-capture answer (state + current revision + content)",
              "views are rebuildable projections (SYS-02): no state column duplicates a derivable fact")

        # ---- HLG-10 — the ack-rung pins
        pa = mk_highlight("hl-A9", sid_a, s1, e1)
        h9 = ack_field(pa, "result_ref")
        p_r = revise("rev-A9", h9, s2, e2)
        p_t = lifecycle("tombstone_highlight", "tomb-A9", h9)
        p_rr = lifecycle("restore_highlight", "res-A9", h9)
        ok10 = (ack_field(pa, "durability_rung") == "local_durable"
                and ack_field(p_r, "durability_rung") == "local_durable"
                and ack_field(p_t, "durability_rung") == "local_durable"
                and ack_field(p_rr, "durability_rung") == "local_durable")
        check("HLG-10", ok10,
              "create/revise/tombstone/restore acks ALL name durability_rung=local_durable",
              "SYS-01: the acknowledgment names the rung the store independently knows — never the request's send state")

        # ---- HLG-11 — the schema-convention audits (0007)
        cols = audit_rows("SELECT column_name || '|' || COALESCE(column_default, '-') FROM "
                          "information_schema.columns WHERE table_schema='arv' AND "
                          "table_name='highlight_lifecycle' ORDER BY ordinal_position;")
        no_defs = all(c.split("|")[1] == "-" for c in cols)
        trg_upd = audit("SELECT count(*) FROM information_schema.triggers WHERE "
                        "event_object_table='highlight_lifecycle' AND event_manipulation='UPDATE';")
        trg_ins = audit("SELECT count(*) FROM information_schema.triggers WHERE "
                        "event_object_table='highlight_lifecycle' AND event_manipulation='INSERT';")
        rls = audit("SELECT relrowsecurity FROM pg_class WHERE relname='highlight_lifecycle';")
        grant_app = set(audit("SELECT string_agg(privilege_type, ',' ORDER BY privilege_type) FROM "
                              "information_schema.role_table_grants WHERE table_schema='arv' AND "
                              "table_name='highlight_lifecycle' AND grantee='arv_app';").split(","))
        grant_read = set(audit("SELECT string_agg(privilege_type, ',' ORDER BY privilege_type) FROM "
                               "information_schema.role_table_grants WHERE table_schema='arv' AND "
                               "table_name='highlight_lifecycle' AND grantee='arv_read';").split(","))
        ident = audit("SELECT count(*) FROM pg_constraint WHERE conrelid='arv.highlight'::regclass "
                      "AND contype='u' AND (SELECT count(*) FROM unnest(conkey)) = 2;")
        fk = audit("SELECT count(*) FROM pg_constraint WHERE conrelid='arv.highlight_lifecycle'::regclass "
                   "AND contype='f' AND confrelid='arv.highlight'::regclass;")
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' AND "
                    "tablename='highlight_lifecycle' AND policyname='owner_isolation';")
        ok11 = (no_defs and trg_upd == "1" and trg_ins == "1" and rls == "t"
                and grant_app >= {"INSERT", "SELECT"} and grant_read == {"SELECT"}
                and ident == "1" and fk == "1" and pol == "1")
        check("HLG-11", ok11,
              "0007's conventions: no DEFAULTs (LAW-24), the append-only + alternation triggers, RLS forced + owner policy, arv_app INSERT/SELECT + arv_read SELECT, the highlight identity constraint + the composite FK",
              "the 0002/0004 substrate conventions hold on every authoritative table")

        # ---- HLG-12 — the row-protocol framing (U+2028 on the new arm)
        hard = "before\u2028after"          # the JSON-legal line separator, raw inside a JSON string
        t20 = "line one\n" + hard + " closes the thought.\nline three\n"
        hard_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "u2028.md"
        hard_file.write_text(t20, encoding="utf-8")
        ph_src = import_src("imp-A20", "Framing", str(hard_file))
        sid20 = ack_field(ph_src, "result_ref")
        i_b = t20.index("before")
        i_ae = t20.index("after") + len("after")
        p_h20 = mk_highlight("hl-A20", sid20, i_b, i_ae)
        h20 = ack_field(p_h20, "result_ref")
        pr20 = revise("rev-A20", h20, 0, 8)
        hh = history_rows("A", h20)
        framing_ok = (p_h20.returncode == 0 and pr20.returncode == 0
                      and len(hh) == 2
                      and all(isinstance(r, dict) for r in hh)
                      and any(r.get("kind") == "revision" and r.get("revision") == 2
                              and r.get("selected_text") == t20[0:8] for r in hh)
                      and any(r.get("kind") == "revision" and r.get("revision") == 1
                              and r.get("selected_text") == hard for r in hh))
        check("HLG-12", framing_ok,
              "U+2028 inside the stored text survives get-history with intact newline-only row framing (the #88 round-2 lesson on the new arm)",
              "row_to_json emits one escaped JSON line per row; the reader splits on the newline ONLY — a U+2028 must never corrupt the framing")

        print()
        if FAILS:
            print(f"RED — {len(FAILS)} failing: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-04 acceptance suite (HLG-01..12) passes")
        return 0
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
