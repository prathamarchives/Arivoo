#!/usr/bin/env python3
"""harness/tests/test_bookmark.py — P3-05 acceptance suite (the Bookmark
machine's contract pins; RTM §2.5 item 6 + §3.3/§3.2, SYS-01/02/05, PLAN's
P3-05 card).

Red-first (LAW-11): committed BEFORE the implementation; at the predecessor
6938efa the suite fails with ARV-TEST-000 (machinery-absent: commands.py's
create_bookmark/move_bookmark/tombstone_bookmark/restore_bookmark and
query.py's get-bookmark arm do not exist; migration 0008 absent — the
record-18 §4.1 / red-01.txt precedent class).

THE MACHINE (RTM §2.5 item 6 — "the stable return location"):

  the row      identity + the source-versioned Anchor/location reference;
               NO copy of source content — the arv.bookmark columns are the
               structural law (no text column exists; the location evidence
               lives in the anchor row alone; a client never supplies anchor
               truth — the offsets are DERIVED from the stored bytes)
  revisions    a NEW immutable row per move (PK (id, revision) — the 0004
               revision-per-row shape); the location re-derived from the SAME
               Source version's stored bytes at the new offsets + a NEW
               anchor row; the source reference IDENTITY-FIXED by
               construction — a bookmark revision NEVER crosses Source
               versions (SYS-05; re-import/edition-change never retargets)
  tombstone    the §3.3 machine shared with the highlight family: typed
               lifecycle EVENT rows (append-only, owner-scoped,
               provenance-complete); tombstoned hides from ordinary
               retrieval (list excludes, get refuses with the typed
               ARV-QRY-003) while the governed history retains everything;
               alternation (tombstone only from active; restore only from
               tombstoned) at the command boundary (ARV-BMK-003/004) AND the
               substrate (the advisory-lock guard trigger)
  resolution   THE P3-05 ACCEPTANCE: get-bookmark returns the saved location
               or reports the typed unresolved-anchor state (SYS-05's
               resolved | unresolved | ambiguous — with the named causes
               no-current-generation / stale-generation / location-unmatched)
               — NEVER a silent retarget (the answer's offsets are the
               anchor's own, whatever the derived view did; the anchor row
               is immutable)
  acks         every bookmark-family ack names durability_rung=local_durable
               (SYS-01)

Cases (the BMK registry — this file is the contract's declaration):
  BMK-01 the create happy path + THE NO-COPY LAW: the ack carries
         revision=1 + durability_rung=local_durable; the anchor derived from
         the stored bytes (offsets + contexts + the source's own digest);
         the bookmark row's column set carries NO content column (the
         structural pin — "do not duplicate source text")
  BMK-02 the invalid-anchor targets + the append-only pins: create against
         an absent source (ARV-CAP-002), invalid offsets (ARV-CAP-003),
         non-UTF-8 bytes (ARV-CAP-008); direct-DB UPDATE/DELETE on
         arv.bookmark refused at BOTH boundaries (permission + ARV-CAP-005)
  BMK-03 cross-owner isolation: move/tombstone/restore on an absent id and
         on ANOTHER OWNER's bookmark are the SAME ARV-BMK-001 refusal;
         get/list/history never observe the other owner's objects
  BMK-04 same-key replay + conflicting body + the ordinal backstop: same
         key+body -> status=replayed (one effect); same key+different body
         -> ARV-CMD-409 (zero effect); a direct-DB duplicate (id, revision)
         insert -> the PK violation
  BMK-05 the crash/restart matrix: move + tombstone at after-begin /
         pre-commit (zero effect) and post-commit-pre-ack (the lost ack: the
         effect IS committed); the same-key replay converges the lost ack
  BMK-06 the tombstone/restore machine: tombstoned hidden from get-bookmark
         (ARV-QRY-003) and list-bookmarks (an ACTIVE fixture beside — the
         exclusion never vacuous); history retained; restore returns it;
         double-tombstone (ARV-BMK-003), restore-of-active (ARV-BMK-004),
         move-of-tombstoned (ARV-BMK-002) refused; the DB guard refuses the
         hostile duplicate and the ghost target; lifecycle mutations refused
  BMK-07 the identity-fix pin (re-import): a NEW edition (source v2) of the
         same work NEVER retargets — move still binds the ORIGINAL source
         version; get-bookmark still resolves AT THE SAVED LOCATION (the
         acceptance: return to the saved location, never a retarget)
  BMK-08 the typed-resolution headline: get-bookmark answers the typed state
         over five fixtures — resolved (location + generation + passages);
         unresolved/no-current-generation (the never-extracted source);
         unresolved/stale-generation (the planted digest break);
         unresolved/location-unmatched with evidence_hits == 1 (the drifted
         tiling — the single hit is a DETECTION, never a retarget);
         ambiguous with hits == 2 (the repeated content) — and in EVERY
         case the anchor row and the bookmark's binding are byte-unchanged
  BMK-09 the independent current-view rebuild: the current view (state +
         current revision's source/anchor/location) re-derived from the
         get-bookmark-history rows ALONE equals the get-bookmark answer
  BMK-10 the ack-rung pins: create/move/tombstone/restore acks ALL name
         durability_rung=local_durable (SYS-01)
  BMK-11 the schema-convention audits (0008): no DEFAULTs (LAW-24), the
         append-only + alternation triggers, RLS enabled AND FORCED +
         owner policy, the grants, the two composite FKs on arv.bookmark,
         the no-FK trigger-form convention on the lifecycle table
  BMK-12 the row-protocol framing on the history arm: a U+2028 inside the
         bookmark's location evidence (the anchor's context window) travels
         raw inside a JSON string and survives get-bookmark-history with
         intact newline-only framing (the #88/#89 lesson on every new arm)

Run: python3 harness/tests/test_bookmark.py   (exit 0 = green)
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
                          "create_bookmark", "--help"], capture_output=True, text=True)
_absent_cmd = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "get-bookmark", "--owner", "A", "--id", "x"],
                         capture_output=True, text=True, timeout=60)
_absent_arm = "invalid choice" in _probe2.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0008_*.sql"))
if _absent_cmd or _absent_arm or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-05 machinery is absent (machinery-absent "
          f"class; create_bookmark command absent: {_absent_cmd}; get-bookmark "
          f"arm absent: {_absent_arm}; migration 0008 present: {bool(_mig)}) — "
          "the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

# ---------------------------------------------------------------- the harness
from harness.adapters import pg  # noqa: E402

DB = ENV = None
TEXT = ("The reader's return.\n"
        "Second paragraph: the first position lives here, plainly.\n"
        "Third paragraph: the moved position lives here instead.\n"
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


def extract(key: str, source_id: str, owner: str = "A") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor", "owner",
               "--client-id", "cli-1", "--idem-key", key, "--source-id", source_id)


def mk_bookmark(key: str, source_id: str, start: int, end: int,
                owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "create_bookmark",
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--source-id", source_id,
               "--start", str(start), "--end", str(end))


def move(key: str, bm_id: str, start: int, end: int, owner: str = "A",
         client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "move_bookmark",
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--id", bm_id, "--start", str(start), "--end", str(end))


def lifecycle(op: str, key: str, bm_id: str, owner: str = "A",
              client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), op,
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--id", bm_id)


def crash(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "crash.py"), *args)


def qy(arm: str, owner: str, id_: str = None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "query.py"), arm, "--owner", owner]
    if id_ is not None:
        a += ["--id", id_]
    return cli(*a)


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


def super_sql(sql: str) -> subprocess.CompletedProcess:
    """The append-only trigger's own audience: a role WITH update/delete
    permission (the rig superuser) — the trigger fires where the least-privilege
    app role is stopped earlier at the permission boundary (both refusals are
    the substrate's law; this pins the TRIGGER)."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "postgres", "-d", DB, "-c", sql],
                           capture_output=True, text=True, timeout=60, env=ENV)


def plant(sql: str) -> subprocess.CompletedProcess:
    """Fixture surgery over DERIVED state only (the ANC convention: generations
    and passages are disposable/rebuildable — never an authoritative row)."""
    return subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres",
                           "-d", DB, "-c", sql], capture_output=True, text=True,
                          timeout=60, env=ENV)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def history_rows(owner: str, bm_id: str) -> list:
    p = qy("get-bookmark-history", owner, bm_id)
    if p.returncode != 0:
        return []
    return [json.loads(ln) for ln in p.stdout.split("\n") if ln.strip()]


def typed(p: subprocess.CompletedProcess) -> "dict | None":
    """The typed answer: ONE JSON line on stdout, exit 0."""
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    if p.returncode != 0 or len(lines) != 1:
        return None
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError:
        return None


def fresh_file(name: str, text_or_bytes):
    d = tempfile.mkdtemp(prefix="arv-bmk-")
    f = pathlib.Path(d) / name
    if isinstance(text_or_bytes, bytes):
        f.write_bytes(text_or_bytes)
    else:
        f.write_text(text_or_bytes, encoding="utf-8")
    return str(f)


def derived_state(rows: list) -> str:
    """The current lifecycle view DERIVED from the history rows alone (parity)."""
    evs = [r for r in rows if r.get("kind") == "lifecycle"]
    t = sum(1 for e in evs if e["event"] == "tombstone")
    r = sum(1 for e in evs if e["event"] == "restore")
    return "tombstoned" if t > r else "active"


def anchor_snapshot(bm_id: str) -> list:
    """The authoritative location evidence, read independently (the
    never-silently-retargeted pin's before/after material)."""
    return audit_rows(f"SELECT a.start_off || '|' || a.end_off || '|' || a.context_before || "
                      f"'|' || a.context_after || '|' || a.source_digest FROM arv.anchor a "
                      f"JOIN arv.bookmark b ON b.anchor_id = a.id WHERE b.id = '{bm_id}' "
                      f"ORDER BY b.revision;")


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p305")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ---------------- the fixture: real bytes, two owners, one generation
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "positions.md"
        src_file.write_text(TEXT, encoding="utf-8")
        p1s = TEXT.index("first position")
        p1e = p1s + len("first position")
        p2s = TEXT.index("moved position")
        p2e = p2s + len("moved position")

        p = import_src("imp-A", "Positions", str(src_file))
        sid_a = ack_field(p, "result_ref")
        wid_a = ack_field(p, "work_id")
        pe = extract("ext-A", sid_a)
        assert pe.returncode == 0, "fixture: the extraction must succeed"
        pb = import_src("imp-B", "B's book", str(src_file), owner="B")
        sid_b = ack_field(pb, "result_ref")
        pb = mk_bookmark("bm-B1", sid_b, p1s, p1e, owner="B")
        bmb = ack_field(pb, "result_ref")
        p = mk_bookmark("bm-A1", sid_a, p1s, p1e)
        b1 = ack_field(p, "result_ref")

        # ---- BMK-01 — the create happy path + THE NO-COPY LAW
        rev1 = ack_field(p, "revision")
        rung = ack_field(p, "durability_rung")
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='bookmark' "
                          "ORDER BY ordinal_position;")
        content_cols = [c for c in cols if c in ("selected_text", "text", "content",
                                                 "quote", "body", "title")]
        anc = audit_rows(f"SELECT a.start_off || '|' || a.end_off || '|' || a.source_digest "
                         f"FROM arv.anchor a JOIN arv.bookmark b ON b.anchor_id=a.id "
                         f"WHERE b.id='{b1}' AND b.revision=1;")
        rows = audit_rows(f"SELECT revision || '|' || source_id || '|' || anchor_id FROM "
                          f"arv.bookmark WHERE id='{b1}';")
        ok1 = (p.returncode == 0 and "status=committed" in p.stdout
               and rev1 == "1" and rung == "local_durable"
               and not content_cols                                  # NO content column — the structural law
               and len(cols) == 10                                   # exactly the declared set
               and anc and anc[0].split("|")[0] == str(p1s) and anc[0].split("|")[1] == str(p1e)
               and len(rows) == 1 and rows[0].split("|")[1] == sid_a)
        check("BMK-01", ok1,
              "create appends the revision-1 row (identity + the derived version-tied anchor, the source's own digest); the ack carries revision=1 + durability_rung=local_durable; arv.bookmark carries NO content column (the no-copy law made structural)",
              "a bookmark is the stable return location: identity + the anchor reference ONLY — source text is never duplicated into the bookmark row (RTM §2.5 item 6)")

        # ---- BMK-02 — the invalid-anchor targets + the append-only pins
        pr_abs = mk_bookmark("bm-abs", "00000000-0000-7000-8000-000000000001", 0, 5)
        pr_off = mk_bookmark("bm-off", sid_a, 5, 3)
        pr_big = mk_bookmark("bm-big", sid_a, 0, 10 ** 6)
        bin_file = fresh_file("bin.dat", b"\xff\xfe\x00binary-not-utf8")
        p_bin = import_src("imp-bin", "Binary", bin_file)
        sid_bin = ack_field(p_bin, "result_ref")
        pr_bin = mk_bookmark("bm-bin", sid_bin, 0, 4)
        before = audit(f"SELECT count(*) FROM arv.bookmark;")
        up = app_sql(f"UPDATE arv.bookmark SET anchor_id=anchor_id WHERE id='{b1}';")
        dele = app_sql(f"DELETE FROM arv.bookmark WHERE id='{b1}';")
        up_t = super_sql(f"UPDATE arv.bookmark SET anchor_id=anchor_id WHERE id='{b1}';")
        dele_t = super_sql(f"DELETE FROM arv.bookmark WHERE id='{b1}';")
        after = audit(f"SELECT count(*) FROM arv.bookmark;")
        ok2 = (pr_abs.returncode == 1 and "ARV-CAP-002" in pr_abs.stdout
               and pr_off.returncode == 1 and "ARV-CAP-003" in pr_off.stdout
               and pr_big.returncode == 1 and "ARV-CAP-003" in pr_big.stdout
               and pr_bin.returncode == 1 and "ARV-CAP-008" in pr_bin.stdout
               and up.returncode == 1 and "permission denied" in up.stderr
               and dele.returncode == 1 and "permission denied" in dele.stderr
               and "ARV-CAP-005" in up_t.stderr and "ARV-CAP-005" in dele_t.stderr
               and before == after)
        check("BMK-02", ok2,
              "the invalid-anchor targets refused by name at the command boundary (ARV-CAP-002 absent source; ARV-CAP-003 invalid offsets, never clamped; ARV-CAP-008 non-UTF-8); direct-DB mutations of the authored rows refused at BOTH boundaries (permission + the ARV-CAP-005 append-only trigger)",
              "a dangling or malformed anchor target is refused BEFORE any write (zero effect); authoritative rows are append-only (SYS-02)")

        # ---- BMK-03 — cross-owner isolation (absent and another owner's: the SAME refusal)
        pm1 = move("mv-abs", "00000000-0000-7000-8000-000000000002", p1s, p1e)
        pm2 = move("mv-Bsteal", bmb, p1s, p1e)                     # A moving B's bookmark
        pt1 = lifecycle("tombstone_bookmark", "tomb-abs",
                        "00000000-0000-7000-8000-000000000003")
        pt2 = lifecycle("tombstone_bookmark", "tomb-Bsteal", bmb)   # A tombstoning B's
        pr3 = lifecycle("restore_bookmark", "res-Bsteal", bmb)      # A restoring B's
        g_other = qy("get-bookmark", "A", bmb)
        h_other = qy("get-bookmark-history", "A", bmb)
        l_b = qy("list-bookmarks", "B")
        l_a = qy("list-bookmarks", "A")
        hist_b_visible = audit(f"SELECT count(*) FROM arv.bookmark WHERE id='{bmb}' AND owner_scope='A';")
        ok3 = (pm1.returncode == 1 and "ARV-BMK-001" in pm1.stdout
               and pm2.returncode == 1 and "ARV-BMK-001" in pm2.stdout
               and pt1.returncode == 1 and "ARV-BMK-001" in pt1.stdout
               and pt2.returncode == 1 and "ARV-BMK-001" in pt2.stdout
               and pr3.returncode == 1 and "ARV-BMK-001" in pr3.stdout
               and g_other.returncode == 1 and "ARV-QRY-001" in g_other.stdout
               and h_other.returncode == 1 and "ARV-QRY-001" in h_other.stdout
               and l_b.returncode == 0 and bmb in l_b.stdout.split()
               and bmb not in l_a.stdout.split()
               and b1 in l_a.stdout.split()
               and hist_b_visible == "0")
        check("BMK-03", ok3,
              "absent and another owner's bookmark are the SAME ARV-BMK-001/ARV-QRY-001 refusal on every arm (move/tombstone/restore/get/history/list) — never a side channel; the other owner's objects never observable",
              "owner isolation on every path (RTM §2.10): the refusal never distinguishes absent from foreign")

        # ---- BMK-04 — same-key replay + conflicting body + the ordinal backstop
        pm = move("mv-A1", b1, p2s, p2e)
        pm_again = move("mv-A1", b1, p2s, p2e)
        pm_conflict = move("mv-A1", b1, p1s, p1e)                  # same key, different body
        n_after_replay = int(audit(f"SELECT count(*) FROM arv.bookmark WHERE id='{b1}';"))
        dup = super_sql(f"INSERT INTO arv.bookmark (id, revision, source_id, anchor_id, owner_scope, "
                        f"actor, run_id, input_hash, idempotency_key, created_at) SELECT id, 2, "
                        f"source_id, anchor_id, owner_scope, actor, run_id, input_hash, "
                        f"'dup-key', created_at FROM arv.bookmark WHERE id='{b1}' AND revision=1;")
        ok4 = (pm.returncode == 0 and "status=committed" in pm.stdout
               and pm_again.returncode == 0 and "status=replayed" in pm_again.stdout
               and pm_conflict.returncode == 1 and "ARV-CMD-409" in pm_conflict.stdout
               and n_after_replay == 2                              # ONE move effect, never two
               and dup.returncode == 1 and "duplicate key" in dup.stderr)
        check("BMK-04", ok4,
              "same key+body -> status=replayed (one effect); same key+different body -> ARV-CMD-409 (zero effect); the direct-DB duplicate (id, revision) insert refused by the PK (the concurrent-loser backstop)",
              "exactly-once is a contract (SYS-04): the replay returns the recorded result; a colliding body never silently overwrites")

        # ---- BMK-05 — the crash/restart matrix (move + tombstone at each boundary)
        n0 = int(audit(f"SELECT count(*) FROM arv.bookmark WHERE id='{b1}';"))
        c1 = crash("--command", "move_bookmark", "--point", "after-begin",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-m1",
                   "--id", b1, "--start", str(p1s), "--end", str(p1e))
        c2 = crash("--command", "move_bookmark", "--point", "pre-commit",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-m2",
                   "--id", b1, "--start", str(p1s), "--end", str(p1e))
        n_mid = int(audit(f"SELECT count(*) FROM arv.bookmark WHERE id='{b1}';"))
        c3 = crash("--command", "move_bookmark", "--point", "post-commit-pre-ack",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-m3",
                   "--id", b1, "--start", str(p1s), "--end", str(p1e))
        n_lost = int(audit(f"SELECT count(*) FROM arv.bookmark WHERE id='{b1}';"))
        lost_ack = move("crash-m3", b1, p1s, p1e, client="cli-c")   # the same-key replay resolves it
        n_replay = int(audit(f"SELECT count(*) FROM arv.bookmark WHERE id='{b1}';"))
        e0 = int(audit("SELECT count(*) FROM arv.bookmark_lifecycle;"))
        c4 = crash("--command", "tombstone_bookmark", "--point", "after-begin",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-t1", "--id", b1)
        c5 = crash("--command", "tombstone_bookmark", "--point", "pre-commit",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-t2", "--id", b1)
        e_mid = int(audit("SELECT count(*) FROM arv.bookmark_lifecycle;"))
        c6 = crash("--command", "tombstone_bookmark", "--point", "post-commit-pre-ack",
                   "--owner", "A", "--client-id", "cli-c", "--idem-key", "crash-t3", "--id", b1)
        e_lost = int(audit("SELECT count(*) FROM arv.bookmark_lifecycle;"))
        conv = lifecycle("tombstone_bookmark", "crash-t3", b1, client="cli-c")
        e_conv = int(audit("SELECT count(*) FROM arv.bookmark_lifecycle;"))
        ok5 = (c1.returncode == 2 and c2.returncode == 2 and c3.returncode == 2
               and c4.returncode == 2 and c5.returncode == 2 and c6.returncode == 2
               and n_mid == n0 and n_lost == n0 + 1 and n_replay == n_lost
               and lost_ack.returncode == 0 and "status=replayed" in lost_ack.stdout
               and e_mid == e0 and e_lost == e0 + 1
               and conv.returncode == 0 and "status=replayed" in conv.stdout
               and e_conv == e_lost)
        check("BMK-05", ok5,
              "crashes at each boundary (move + tombstone): exit 2, no ack; after-begin/pre-commit leave zero effect; post-commit-pre-ack commits the effect and the same-key replay converges to the recorded result (nothing added)",
              "zero-or-one effect per command, never partial (SYS-04): the commit point is the only effect boundary — the restart/replay class from the card")

        # ---- BMK-06 — the tombstone/restore machine (a FRESH bookmark: b6 + an ACTIVE b7)
        p6 = mk_bookmark("bm-A6", sid_a, p1s, p1e)
        b6 = ack_field(p6, "result_ref")
        p7 = mk_bookmark("bm-A7", sid_a, p1s, p1e)
        b7 = ack_field(p7, "result_ref")
        p = lifecycle("tombstone_bookmark", "tomb-A1", b6)
        get_t = qy("get-bookmark", "A", b6)
        listing = qy("list-bookmarks", "A")
        hist_t = history_rows("A", b6)
        p_restore = lifecycle("restore_bookmark", "res-A1", b6)
        get_r = qy("get-bookmark", "A", b6)
        lifecycle("tombstone_bookmark", "tomb-A2", b6)               # lawful: active -> tombstoned
        p_double = lifecycle("tombstone_bookmark", "tomb-A4", b6)   # double-tombstone
        p_mv_tomb = move("mv-tomb", b6, p1s, p1e)                   # move-of-tombstoned
        lifecycle("restore_bookmark", "res-A2", b6)                  # lawful: tombstoned -> active
        p_res_active = lifecycle("restore_bookmark", "res-A3", b6)  # restore-of-active
        ev_count = int(audit(f"SELECT count(*) FROM arv.bookmark_lifecycle WHERE bookmark_id='{b6}';"))
        lifecycle("tombstone_bookmark", "tomb-A5", b6)               # lawful: active -> tombstoned
        hostile = app_sql(f"INSERT INTO arv.bookmark_lifecycle (id, bookmark_id, event, owner_scope, "
                          f"actor, run_id, input_hash, idempotency_key, created_at) VALUES "
                          f"('00000000-0000-7000-8000-00000000000a', '{b6}', 'tombstone', 'A', "
                          f"'owner', 'hostile-run', 'hostile-hash', 'hostile-key', "
                          f"'2026-10-31T00:00:00+00:00');")
        upl = super_sql(f"UPDATE arv.bookmark_lifecycle SET event='restore' WHERE bookmark_id='{b6}';")
        delel = super_sql(f"DELETE FROM arv.bookmark_lifecycle WHERE bookmark_id='{b6}';")
        ghost = app_sql(f"INSERT INTO arv.bookmark_lifecycle (id, bookmark_id, event, owner_scope, "
                        f"actor, run_id, input_hash, idempotency_key, created_at) VALUES "
                        f"('00000000-0000-7000-8000-00000000000b', "
                        f"'00000000-0000-7000-8000-00000000000c', 'tombstone', 'A', "
                        f"'owner', 'hostile-run', 'hostile-hash', 'hostile-ghost', "
                        f"'2026-10-31T00:00:00+00:00');")
        ev_after = int(audit(f"SELECT count(*) FROM arv.bookmark_lifecycle WHERE bookmark_id='{b6}';"))
        ok6 = (p.returncode == 0 and "status=committed" in p.stdout
               and get_t.returncode == 1 and "ARV-QRY-003" in get_t.stdout
               and listing.returncode == 0 and b7 in listing.stdout.split()
               and b6 not in listing.stdout.split()
               and b1 not in listing.stdout.split()                   # b1 tombstoned by c6's lost-ack commit
               and len([r for r in hist_t if r.get("kind") == "lifecycle"]) == 1
               and len([r for r in hist_t if r.get("kind") == "revision"]) == 1
               and p_restore.returncode == 0 and get_r.returncode == 0
               and p_double.returncode == 1 and "ARV-BMK-003" in p_double.stdout
               and p_mv_tomb.returncode == 1 and "ARV-BMK-002" in p_mv_tomb.stdout
               and p_res_active.returncode == 1 and "ARV-BMK-004" in p_res_active.stdout
               and ev_count == 4                                     # tomb,res,tomb,res — one per LAWFUL transition
               and "ARV-BMK-003" in hostile.stderr                   # the substrate refuses the duplicate
               and "ARV-BMK-001" in ghost.stderr                     # the substrate refuses the nonexistent target
               and "ARV-CAP-005" in upl.stderr and "ARV-CAP-005" in delel.stderr
               and ev_after == 5)                                    # 4 lawful + tomb-A5
        check("BMK-06", ok6,
              "tombstone hides from get-bookmark (ARV-QRY-003) + list-bookmarks (the ACTIVE fixture stays listed — the exclusion is never vacuous over an empty listing); history retains all; restore returns it; double-tombstone/move-of-tombstoned/restore-of-active refused by name; the lifecycle rows' own mutations refused; the DB alternation trigger refuses the hostile duplicate and the ghost target",
              "the §3.3 machine: alternation enforced at the command boundary AND the substrate; the governed history never loses a row")

        # ---- BMK-07 — the identity-fix pin (re-import NEVER retargets; the saved location holds)
        lifecycle("restore_bookmark", "res-A0", b1)                  # back to active for the move
        snap_before = anchor_snapshot(b1)
        p_v2 = import_src("imp-A2", None, str(src_file), work_id=wid_a)
        sid_v2 = ack_field(p_v2, "result_ref")
        ver = audit(f"SELECT source_version FROM arv.source WHERE id='{sid_v2}';")
        src_before = audit_rows(f"SELECT DISTINCT source_id FROM arv.bookmark WHERE id='{b1}';")
        p = move("mv-A2", b1, p2s, p2e)
        src_after = audit_rows(f"SELECT DISTINCT source_id FROM arv.bookmark WHERE id='{b1}';")
        g = qy("get-bookmark", "A", b1)
        a7 = typed(g)
        ok7 = (ver == "2"
               and len(src_before) == 1 and len(src_after) == 1
               and src_before == src_after
               and sid_v2 not in src_after
               and p.returncode == 0
               and a7 is not None and a7.get("state") == "resolved"
               and a7.get("start_off") == p2s and a7.get("end_off") == p2e
               and a7.get("source_id") == sid_a
               and anchor_snapshot(b1)[:len(snap_before)] == snap_before)   # the prior revisions' evidence untouched
        check("BMK-07", ok7,
              "a new edition (source v2) NEVER retargets: the move still binds the ORIGINAL source version, and get-bookmark returns the SAVED location (resolved at the moved offsets over v1's own generation) — never a silent jump to v2",
              "identity-fixed by construction — a bookmark revision NEVER crosses Source versions (SYS-05); the edition is a different source row")

        # ---- BMK-08 — the typed-resolution headline (five fixtures + the never-retarget pin)
        # (a) resolved — b1 above (pinned again here with the full answer shape)
        ga = qy("get-bookmark", "A", b1)
        a8a = typed(ga)
        # (b) the never-extracted source: no current generation
        f8b = fresh_file("never.md", "The never-extracted paragraph sits here.\n\nSecond.\n")
        p8b = import_src("imp-8b", "Never Book", f8b)
        sid8b = ack_field(p8b, "result_ref")
        p8b = mk_bookmark("bm-8b", sid8b, 0, 9)
        b8b = ack_field(p8b, "result_ref")
        g8b = qy("get-bookmark", "A", b8b)
        a8b = typed(g8b)
        # (c) the stale surface: a planted digest break on the current generation
        f8c = fresh_file("stale.md", "The stale-detection substrate paragraph.\n\nSecond.\n")
        p8c = import_src("imp-8c", "Stale Book", f8c)
        sid8c = ack_field(p8c, "result_ref")
        extract("ext-8c", sid8c)
        mk_bookmark("bm-8c", sid8c, 0, 9)
        b8c = audit(f"SELECT id FROM arv.bookmark WHERE idempotency_key='bm-8c';")
        pl8c = plant(f"UPDATE arv.extraction_generation SET input_digest='deadbeef' "
                     f"WHERE source_id='{sid8c}' AND state='current';")
        g8c = qy("get-bookmark", "A", b8c)
        a8c = typed(g8c)
        # (d) the drifted tiling with exactly ONE relocated evidence match: the DETECTION
        f8d = fresh_file("drift.md", "alpha opening paragraph text.\n\nbeta middle content.\n\ngamma closing words.\n")
        p8d = import_src("imp-8d", "Drift Book", f8d)
        sid8d = ack_field(p8d, "result_ref")
        extract("ext-8d", sid8d)
        TEXTD = pathlib.Path(f8d).read_text(encoding="utf-8")
        mk_bookmark("bm-8d", sid8d, 53, 59)
        b8d = audit(f"SELECT id FROM arv.bookmark WHERE idempotency_key='bm-8d';")
        drift8 = TEXTD[21:]
        d8 = hashlib.sha256(drift8.encode("utf-8")).hexdigest()
        gen8d = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid8d}' AND state='current';")
        pl8d = plant(f"UPDATE arv.extraction_generation SET state='superseded' WHERE id='{gen8d}'; "
                     f"INSERT INTO arv.extraction_generation (id, source_id, ordinal, state, extractor, "
                     f"extractor_config, input_digest, idempotency_key, body_hash, owner_scope, actor, "
                     f"run_id, input_hash, created_at, updated_at) "
                     f"SELECT gen_random_uuid(), '{sid8d}', 2, 'current', extractor, extractor_config, "
                     f"input_digest, 'drifted-tiling-1', body_hash, owner_scope, actor, run_id, input_hash, "
                     f"now(), now() FROM arv.extraction_generation WHERE id='{gen8d}';")
        gen8d2 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid8d}' AND state='current';")
        pl8d2 = plant(f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, text, "
                      f"digest, owner_scope, actor, run_id, input_hash, created_at) "
                      f"SELECT gen_random_uuid(), '{gen8d2}', 1, 0, {len(drift8)}, '{drift8}', '{d8}', "
                      f"owner_scope, actor, run_id, input_hash, now() "
                      f"FROM arv.extraction_generation WHERE id='{gen8d2}';")
        g8d = qy("get-bookmark", "A", b8d)
        a8d = typed(g8d)
        # (e) the ambiguity class: the fallback evidence matches at TWO positions
        B8 = "alpha\n\nbeta gamma delta\n\n"
        S8e = B8 + B8 + B8 + B8 + "omega closing text.\n"
        f8e = fresh_file("ambig.md", S8e)
        p8e = import_src("imp-8e", "Ambiguous Book", f8e)
        sid8e = ack_field(p8e, "result_ref")
        extract("ext-8e", sid8e)
        mk_bookmark("bm-8e", sid8e, 7, 17)
        b8e = audit(f"SELECT id FROM arv.bookmark WHERE idempotency_key='bm-8e';")
        gen8e = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid8e}' AND state='current';")
        pl8e = plant(f"UPDATE arv.extraction_generation SET state='superseded' WHERE id='{gen8e}'; "
                     f"INSERT INTO arv.extraction_generation (id, source_id, ordinal, state, extractor, "
                     f"extractor_config, input_digest, idempotency_key, body_hash, owner_scope, actor, "
                     f"run_id, input_hash, created_at, updated_at) "
                     f"SELECT gen_random_uuid(), '{sid8e}', 2, 'current', extractor, extractor_config, "
                     f"input_digest, 'drifted-tiling-2', body_hash, owner_scope, actor, run_id, input_hash, "
                     f"now(), now() FROM arv.extraction_generation WHERE id='{gen8e}';")
        gen8e2 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid8e}' AND state='current';")
        d8e1 = hashlib.sha256(S8e[0:7].encode()).hexdigest()
        d8e2 = hashlib.sha256(S8e[17:].encode()).hexdigest()
        pl8e2 = plant(f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, text, "
                      f"digest, owner_scope, actor, run_id, input_hash, created_at) "
                      f"SELECT gen_random_uuid(), '{gen8e2}', 1, 0, 7, '{S8e[0:7]}', '{d8e1}', "
                      f"owner_scope, actor, run_id, input_hash, now() "
                      f"FROM arv.extraction_generation WHERE id='{gen8e2}'; "
                      f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, text, "
                      f"digest, owner_scope, actor, run_id, input_hash, created_at) "
                      f"SELECT gen_random_uuid(), '{gen8e2}', 2, 17, {len(S8e)}, '{S8e[17:]}', '{d8e2}', "
                      f"owner_scope, actor, run_id, input_hash, now() "
                      f"FROM arv.extraction_generation WHERE id='{gen8e2}';")
        g8e = qy("get-bookmark", "A", b8e)
        a8e = typed(g8e)
        # the never-retarget pin: the anchor evidence byte-unchanged through every read
        snap_after = {bid: anchor_snapshot(bid) for bid in (b1, b8b, b8c, b8d, b8e)}
        ok8 = (ga.returncode == 0
               and a8a is not None and a8a.get("state") == "resolved"
               and a8a.get("generation_id") and a8a.get("passage_ids")
               and a8a.get("bookmark_id") == b1 and a8a.get("revision") == 4
               and g8b.returncode == 0
               and a8b is not None and a8b.get("state") == "unresolved"
               and "no-current-generation" in (a8b.get("cause") or "")
               and pl8c.returncode == 0 and g8c.returncode == 0
               and a8c is not None and a8c.get("state") == "unresolved"
               and "stale-generation" in (a8c.get("cause") or "")
               and pl8d.returncode == 0 and pl8d2.returncode == 0 and g8d.returncode == 0
               and a8d is not None and a8d.get("state") == "unresolved"
               and "location-unmatched" in (a8d.get("cause") or "")
               and int(a8d.get("evidence_hits") or 0) == 1
               and a8d.get("start_off") == 53 and a8d.get("end_off") == 59
               and pl8e.returncode == 0 and pl8e2.returncode == 0 and g8e.returncode == 0
               and a8e is not None and a8e.get("state") == "ambiguous"
               and int(a8e.get("evidence_hits") or 0) >= 2
               and snap_after[b1][:len(snap_before)] == snap_before  # b1's prior-revision evidence untouched by the reads
               and snap_after[b8d] and snap_after[b8d][0].split("|")[0] == "53"
               and snap_after[b8d][0].split("|")[1] == "59"          # the drifted fixture's anchor STILL at its own offsets
               and snap_after[b8b] and snap_after[b8c] and snap_after[b8e])
        check("BMK-08", ok8,
              "get-bookmark answers the TYPED state over every fixture: resolved (location + generation + passage ids); unresolved/no-current-generation; unresolved/stale-generation; unresolved/location-unmatched with evidence_hits == 1 (the single hit a DETECTION, the original offsets echoed — never a retarget); ambiguous with hits >= 2 — exit 0 in every case (a typed answer, never a failure), the anchor evidence byte-unchanged",
              "the P3-05 acceptance: return to the saved location or report the typed unresolved-anchor state; never silently retarget (SYS-05) — a nearest-match guess is the forbidden behavior")

        # ---- BMK-09 — the independent current-view rebuild
        hist = history_rows("A", b1)
        state = derived_state(hist)
        revs = [r for r in hist if r.get("kind") == "revision"]
        max_rev = max(r["revision"] for r in revs)
        cur_hist = next(r for r in revs if r["revision"] == max_rev)
        g9 = qy("get-bookmark", "A", b1)
        cur_view = typed(g9) or {}
        ok9 = (state == "active"
               and cur_view.get("revision") == max_rev
               and cur_view.get("source_id") == cur_hist["source_id"]
               and cur_view.get("anchor_id") == cur_hist["anchor_id"]
               and cur_view.get("start_off") == cur_hist["start_off"]
               and cur_view.get("end_off") == cur_hist["end_off"]
               and cur_view.get("bookmark_id") == b1)
        check("BMK-09", ok9,
              "the current view re-derived from the get-bookmark-history rows ALONE equals the get-bookmark answer (state + current revision's source/anchor/location)",
              "views are rebuildable projections (SYS-02): no state column duplicates a derivable fact")

        # ---- BMK-10 — the ack-rung pins
        pa = mk_bookmark("bm-A9", sid_a, p1s, p1e)
        b9 = ack_field(pa, "result_ref")
        p_m = move("mv-A9", b9, p2s, p2e)
        p_t = lifecycle("tombstone_bookmark", "tomb-A9", b9)
        p_rr = lifecycle("restore_bookmark", "res-A9", b9)
        ok10 = (ack_field(pa, "durability_rung") == "local_durable"
                and ack_field(p_m, "durability_rung") == "local_durable"
                and ack_field(p_t, "durability_rung") == "local_durable"
                and ack_field(p_rr, "durability_rung") == "local_durable")
        check("BMK-10", ok10,
              "create/move/tombstone/restore acks ALL name durability_rung=local_durable",
              "SYS-01: the acknowledgment names the rung the store independently knows — never the request's send state")

        # ---- BMK-11 — the schema-convention audits (0008; the pg_catalog reads)
        coldefs = audit_rows("SELECT column_name || '|' || COALESCE(column_default, '-') FROM "
                             "information_schema.columns WHERE table_schema='arv' AND "
                             "table_name IN ('bookmark', 'bookmark_lifecycle') ORDER BY table_name, "
                             "ordinal_position;")
        no_defs = all(c.split("|")[1] == "-" for c in coldefs)
        trg_b = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.bookmark'::regclass AND NOT tgisinternal;").split())
        trg_l = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.bookmark_lifecycle'::regclass AND NOT tgisinternal;").split())
        rls = audit("SELECT relrowsecurity || '|' || relforcerowsecurity FROM pg_class "
                    "WHERE relname='bookmark' AND relkind='r';")
        rls_l = audit("SELECT relrowsecurity || '|' || relforcerowsecurity FROM pg_class "
                      "WHERE relname='bookmark_lifecycle' AND relkind='r';")
        grants = {}
        for tbl in ("bookmark", "bookmark_lifecycle"):
            for role in ("arv_app", "arv_read"):
                grants[(tbl, role)] = set(audit(
                    f"SELECT privilege_type FROM aclexplode((SELECT relacl FROM pg_class "
                    f"WHERE relname='{tbl}')) WHERE grantee = "
                    f"(SELECT oid FROM pg_roles WHERE rolname='{role}');").split())
        fk_b = audit("SELECT count(*) FROM pg_constraint WHERE "
                     "conrelid='arv.bookmark'::regclass AND contype='f';")
        fk_l = audit("SELECT count(*) FROM pg_constraint WHERE "
                     "conrelid='arv.bookmark_lifecycle'::regclass AND contype='f';")
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' AND "
                    "tablename IN ('bookmark', 'bookmark_lifecycle') AND "
                    "policyname='owner_isolation';")
        # NOTE: a boolean CONCAT (||) renders 'true'/'false' (text context); the
        # HLG-11 single-column read renders 't' — the two forms differ, both pin
        # ENABLED+FORCED
        ok11 = (no_defs
                and trg_b == {"bookmark_immutable"}
                and trg_l == {"bookmark_lifecycle_guard", "bookmark_lifecycle_immutable"}
                and rls == "true|true" and rls_l == "true|true"
                and grants[("bookmark", "arv_app")] >= {"INSERT", "SELECT"}
                and grants[("bookmark", "arv_read")] == {"SELECT"}
                and grants[("bookmark_lifecycle", "arv_app")] >= {"INSERT", "SELECT"}
                and grants[("bookmark_lifecycle", "arv_read")] == {"SELECT"}
                and fk_b == "2" and fk_l == "0" and pol == "2")
        check("BMK-11", ok11,
              "0008's conventions: no DEFAULTs (LAW-24), the append-only triggers on both tables + the insert-guard/alternation trigger on the lifecycle table, RLS enabled AND FORCED on both (relforcerowsecurity — the owner does not bypass), arv_app INSERT/SELECT + arv_read SELECT, the two composite FKs on arv.bookmark (source + anchor inseparable from the owner scope), the lifecycle table's no-FK trigger-form convention",
              "the 0002/0004 substrate conventions hold on every authoritative table; the composite FK ties the bookmark to its own source and anchor")

        # ---- BMK-12 — the row-protocol framing (U+2028 on the new arm)
        hard = "before\u2028after"          # the JSON-legal line separator, raw inside a JSON string
        t20 = ("short page.\n" + hard + " sits right before the marked zone.\n"
               "line three closes the fixture.\n")
        hard_file = fresh_file("u2028.md", t20)
        ph_src = import_src("imp-A20", "Framing", hard_file)
        sid20 = ack_field(ph_src, "result_ref")
        z_s = t20.index("marked zone")
        z_e = z_s + len("marked zone")
        p_h20 = mk_bookmark("bm-A20", sid20, z_s, z_e)
        b20 = ack_field(p_h20, "result_ref")
        pm20 = move("mv-A20", b20, t20.index("line three"), t20.index("line three") + 5)
        hh = history_rows("A", b20)
        # the NEWLINE-ONLY reader on history_rows (the ANC-10 framing law): a
        # splitlines() reader would itself split on U+2028 and corrupt the rows;
        # the expectation is the fixture's own 32-char window, computed in Python
        # (never a psql round-trip — .strip() would eat a trailing space)
        expected_cb = t20[max(0, z_s - 32):z_s]
        framing_ok = (p_h20.returncode == 0 and pm20.returncode == 0
                      and len(hh) == 2
                      and all(isinstance(r, dict) for r in hh)
                      and "\u2028" in expected_cb                 # the raw separator rides the evidence window
                      and any(r.get("kind") == "revision" and r.get("revision") == 1
                              and r.get("context_before") == expected_cb for r in hh)
                      and any(r.get("kind") == "revision" and r.get("revision") == 2 for r in hh))
        check("BMK-12", framing_ok,
              "U+2028 inside the bookmark's location evidence (the anchor's context window, byte-exact against the fixture's own 32-char window) travels raw inside the JSON string and survives get-bookmark-history with intact newline-only framing (both revision rows parse)",
              "row_to_json emits one escaped JSON line per row; the reader splits on the newline ONLY — a U+2028 must never corrupt the framing (the #88/#89 lesson applied to every new arm)")

        print()
        if FAILS:
            print(f"RED — {len(FAILS)} failing: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-05 acceptance suite (BMK-01..12) passes")
        return 0
    finally:
        # the rig's scratch database DROPPED after every suite run (the #89
        # round-2 convention; ARV_KEEP_DB overrides for local inspection)
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
