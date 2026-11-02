#!/usr/bin/env python3
"""harness/tests/test_note.py — P3-06 acceptance suite, SLICE ONE of the
two-slice sequence (the note CORE machine's contract pins; RTM §2.5 item 7 +
item 9 + §3.3/§3.2, SYS-01/02/03 primary, SYS-01/04 standing, PLAN's P3-06
card). The explicit version-aware REFERENCE machine (arv.note_reference, the
--ref surface, its guards and cases) is CLAIM-057's slice — the LAW-05
bounded-diff split, the P3-M0 three-slice sequence precedent. Red-first
(LAW-11): committed BEFORE the implementation; at the predecessor f86e52b the
suite fails with ARV-TEST-000 (machinery-absent; red-01.txt).

THE MACHINE (RTM §2.5 item 7 — "the owner's deep raw thinking", slice one):

  the row      identity + immutable revisions + the AUTHORED long-form
               content — free-standing (NO source binding, unlike the
               highlight/bookmark families; read_bytes + UTF-8 LOSSLESS; the
               NUL boundary named here — ARV-NTE-009, never mid-protocol)
  revisions    a NEW immutable row per revise (PK (id, revision)); THE
               SERIALIZED TRANSITION: the per-note advisory xact lock (the
               canonical-key form — the SAME key the 0009 guards take)
               FIRST, then state read + validation + inserts + commit, ALL
               inside ONE transaction (build_txn): competing revisers
               serialize; a revision can never commit after tombstoning
  tombstone    §3.3's machine: typed lifecycle EVENT rows (append-only,
               owner-scoped, provenance-complete); tombstoned hides from
               ordinary retrieval (ARV-QRY-003) while the governed history
               retains every revision and event; restore returns it; the
               lifecycle commands run the SAME locked form, the timestamp
               INSIDE (the history renders the serialized commit order)
  substrate    0009's guards: the advisory-locked alternation trigger
               (ARV-NTE-004/005), the strengthened revision-append guard
               (phantom ARV-NTE-001; non-contiguous ARV-NTE-011; tombstoned
               ARV-NTE-002), the ARV-CAP-005 append-only triggers, RLS
               enabled AND FORCED, the ownership uniques
  acks         every note-family ack names durability_rung=local_durable

The refusal codes: ARV-NTE-001 absent/another-owner's (the SAME refusal,
  never a side channel; at the substrate also the phantom append + the ghost
  lifecycle target); ARV-NTE-002 tombstoned (restore precedes edit, at the
  boundary AND the substrate guard); ARV-NTE-004 already tombstoned /
  ARV-NTE-005 not tombstoned (the alternation); ARV-NTE-009 NUL in the
  content; ARV-NTE-010 the content-source refusal (neither/both/unreadable/
  not-UTF-8); ARV-NTE-011 the non-contiguous append (exactly max+1).

Cases (the NTE registry — this file is the contract's declaration):
  NTE-01 create: revision=1 + durability_rung in the ack; the exact
         nine-column set (content-bearing, NO source binding); the content
         byte-identical; provenance complete
  NTE-02 lossless long-form + Unicode (40 paragraphs: CJK, combining,
         astral, RTL, C0 controls, U+2028/U+2029, quotes, backslashes,
         trailing whitespace) round trips through create -> get-note AND
         get-note-history; the inline arm; ARV-NTE-010 + the NUL boundary
         ARV-NTE-009 (zero rows)
  NTE-03 the append-only substrate + the strengthened revision guard:
         UPDATE/DELETE on arv.note at BOTH boundaries (permission +
         ARV-CAP-005, zero rows); the ghost-target lifecycle insert, the
         PHANTOM append (ARV-NTE-001), the GAP append (ARV-NTE-011)
  NTE-04 cross-owner isolation: absent and ANOTHER OWNER's are the SAME
         ARV-NTE-001 refusal; get/list/history never observe the other
         owner's notes
  NTE-05 same-key replay + conflicting body + the ordinal backstop: same
         key + same body -> replayed (one effect); different body ->
         ARV-CMD-409 (create and revise both); the SAME KEY on a DIFFERENT
         NOTE -> ARV-CMD-409 (the target id rides the revise body — the
         #91 round's Major); the direct-DB duplicate meets ARV-NTE-011
  NTE-06 the crash/restart matrix: after-begin/pre-commit (zero effect) and
         post-commit-pre-ack (the lost ack: the effect IS committed); the
         replay converges
  NTE-07 the tombstone/restore machine: hidden from get-note (ARV-QRY-003)
         and list (an ACTIVE fixture beside); the history retains every
         revision and event; double-tombstone (004), restore-of-active
         (005), revise-of-tombstoned (002), the hostile tombstoned append
         (002 at the substrate), the lifecycle mutations (ARV-CAP-005)
  NTE-08 the current view (state + revision + content + attribution)
         re-derived from the history rows ALONE equals the get-note answer
         (the export-ready history)
  NTE-09 the ack-rung pins: the four acks ALL name durability_rung=
         local_durable (SYS-01)
  NTE-10 the schema audits (0009): no DEFAULTs (LAW-24), the four triggers,
         RLS enabled AND FORCED + the owner policy, the grants, the PKs
  NTE-11 the row-protocol framing: U+2028/U+2029 travel raw inside the JSON
         string; history survives with newline-only framing
  NTE-12 the competing-revisions SERIALIZATION: the parked first reviser
         HOLDS the lock across its blocked transition (pg_locks), the
         second WAITS on it; both revisions commit (2 then 3, each
         byte-identical, revision 1 untouched)
  NTE-13 the revise-vs-tombstone SERIALIZATION + THE CANONICAL LOCK KEY (the
         review round's F3): the UPPERCASED-id revise takes the SAME
         canonical key as the substrate guards — the tombstone serializes
         against it; a revision NEVER commits after tombstoning; the late
         mixed-case revise gets the clean ARV-NTE-002 (never the
         ARV-CMD-010 stall wrapper); the history renders the serialized
         commit order
  NTE-14 the UUID-SPELLING CANONICALIZATION (the #91 round-2 finding
         4439931169: PostgreSQL's uuid input also accepts braced/no-hyphen/
         uppercase spellings of ONE note): a variant-spelling retry REPLAYS
         (revise AND tombstone — never ARV-CMD-409) and the boundary lock
         key is the canonical key (the braced revise waits AT the boundary
         while the canonical key is held — zero granted keys for arv_app)

Run: python3 harness/tests/test_note.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

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


_probe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                          "create_note", "--help"], capture_output=True, text=True)
_absent_cmd = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "get-note", "--owner", "A", "--id", "x"],
                         capture_output=True, text=True, timeout=60)
_absent_arm = "invalid choice" in _probe2.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0009_*.sql"))
if _absent_cmd or _absent_arm or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-06 machinery is absent (machinery-absent "
          f"class; create_note command absent: {_absent_cmd}; get-note "
          f"arm absent: {_absent_arm}; migration 0009 present: {bool(_mig)}) — "
          "the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

from harness.adapters import clock, pg  # noqa: E402
from harness.commands import Session  # noqa: E402

DB = ENV = None

# the long-form Unicode round-trip fixture (NTE-02/NTE-11)
LONG_FORM = (
    "# Deep note — the reading session\n\n"
    "Opening block: free-standing owner thought, preserved exactly.\n"
    "A tab-indented line.\n\ttab start, content, tab\tend.\n"
    "Carriage return and line feed together:\r\nthe CR-LF line.\n"
    "A bare carriage return:\rthe bare-CR line.\n\n"
    + "".join(
        f"Paragraph {i:03d} — CJK 中文 preserved; combining e\u0301; astral "
        f"\U0001F4D6\U0001F9E0; RTL \u0639\u0631\u0628\u064a\u0629; symbols \u00bb \u2192 \u2261.\n"
        for i in range(40))
    + "The raw line separator U+2028 [\u2028] and paragraph separator U+2029 [\u2029] inside one line.\n"
    "Control characters: SOH \u0001 STX \u0002 BEL \u0007 VT \u000b FF \u000c.\n"
    "Quote ' single, \" double, backslash \\ literal, percent %, dollar $$, semicolon ;\n"
    "A final line with trailing spaces   and a trailing tab\t.\n"
)


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=240, env=ENV)


def note_cmd(op: str, key: str, owner: str = "A", client: str = "cli-1",
             id_: str = None, content: str = None,
             content_file=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client, "--idem-key", key]
    if id_ is not None:
        a += ["--id", id_]
    if content is not None:
        a += ["--content", content]
    if content_file is not None:
        a += ["--content-file", content_file]
    return cli(*a)


def mk_note(key: str, content: str = None, content_file=None, owner: str = "A",
            client: str = "cli-1") -> subprocess.CompletedProcess:
    return note_cmd("create_note", key, owner=owner, client=client,
                    content=content, content_file=content_file)


def revise_note(key: str, note_id: str, content: str = None, content_file=None,
                owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    return note_cmd("revise_note", key, owner=owner, client=client, id_=note_id,
                    content=content, content_file=content_file)


def lifecycle(op: str, key: str, note_id: str, owner: str = "A",
              client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), op,
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--id", note_id)


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
    # NEWLINE-ONLY framing (the ANC-10 law): splitlines() would split on U+2028
    return [ln for ln in audit(query).split("\n") if ln.strip()]


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    """A hostile/direct write attempt AS the app role (the substrate's own guard)."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_app", "-d", DB,
                            "-c", f"SET app.current_owner='{owner}'; {sql}"],
                           capture_output=True, text=True, timeout=60, env=ENV)


def super_sql(sql: str) -> subprocess.CompletedProcess:
    """The append-only trigger's own audience: a role WITH update/delete
    permission (the rig superuser)."""
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "postgres", "-d", DB, "-c", sql],
                           capture_output=True, text=True, timeout=60, env=ENV)


def _poll(sql: str, timeout: float = 20.0) -> bool:
    """Wait until a superuser observation holds (condition-based, never sleep)."""
    end = clock.mono() + timeout
    while clock.mono() < end:
        if super_sql(sql).stdout.strip() == "1":
            return True
        time.sleep(0.25)
    return False


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def note_rows(note_id: str) -> list:
    """The authoritative rows, read independently (arv_read) as ONE escaped
    JSON line per revision (a pipe-delimited read would fragment)."""
    rows = audit_rows(f"SELECT row_to_json(t)::text FROM (SELECT revision, content, actor, "
                      f"run_id, input_hash, idempotency_key FROM arv.note "
                      f"WHERE id='{note_id}' ORDER BY revision) t;")
    return [json.loads(r) for r in rows]


def history_rows(owner: str, note_id: str) -> list:
    p = qy("get-note-history", owner, note_id)
    if p.returncode != 0:
        return []
    return [json.loads(ln) for ln in p.stdout.split("\n") if ln.strip()]


def typed(p: subprocess.CompletedProcess) -> "dict | None":
    """The typed answer: ONE JSON line on stdout, exit 0."""
    lines = [ln for ln in p.stdout.split("\n") if ln.strip()]
    if p.returncode != 0 or len(lines) != 1:
        return None
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError:
        return None


def fresh_file(name: str, text_or_bytes):
    d = tempfile.mkdtemp(prefix="arv-nte-")
    f = pathlib.Path(d) / name
    if isinstance(text_or_bytes, bytes):
        f.write_bytes(text_or_bytes)
    else:
        f.write_bytes(text_or_bytes.encode("utf-8"))  # bytes: NO newline translation
    return str(f)


def derived_state(rows: list) -> str:
    """The current lifecycle view DERIVED from the history rows alone (parity)."""
    evs = [r for r in rows if r.get("kind") == "lifecycle"]
    t = sum(1 for e in evs if e["event"] == "tombstone")
    r = sum(1 for e in evs if e["event"] == "restore")
    return "tombstoned" if t > r else "active"


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p306")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ---------------- the fixture: free-standing notes, two owners
        long_file = fresh_file("deep-note.md", LONG_FORM)
        pnb = mk_note("note-B1", content="B's private deep thinking.", owner="B")
        noteb = ack_field(pnb, "result_ref")
        p1 = mk_note("n-A1", content_file=long_file)
        n1 = ack_field(p1, "result_ref")

        # ---- NTE-01 — the create happy path + the structural pins
        rev1 = ack_field(p1, "revision")
        rung1 = ack_field(p1, "durability_rung")
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='note' "
                          "ORDER BY ordinal_position;")
        expected_cols = ["id", "revision", "content", "owner_scope", "actor",
                         "run_id", "input_hash", "idempotency_key", "created_at"]
        rows1 = note_rows(n1)
        ok1 = (p1.returncode == 0 and "status=committed" in p1.stdout
               and rev1 == "1" and rung1 == "local_durable"
               and cols == expected_cols                       # exactly the nine — no source binding
               and len(rows1) == 1 and rows1[0]["revision"] == 1
               and rows1[0]["content"] == LONG_FORM            # byte-identical content
               and rows1[0]["actor"] == "owner"                # attribution
               and rows1[0]["idempotency_key"] == "n-A1")      # the command provenance ref
        check("NTE-01", ok1,
              "create appends the revision-1 row (the authored content byte-identical, provenance complete, the exact nine-column set — content-bearing, NO source binding: the free-standing law); the ack carries revision=1 + durability_rung=local_durable",
              "the note is the owner's free-standing deep thinking: identity + authored content ONLY in this slice (RTM §2.5 item 7; the references are CLAIM-057's)")

        # ---- NTE-02 — lossless long-form + Unicode + the content-source boundaries
        g1 = typed(qy("get-note", "A", n1))
        h1_rows = [r for r in history_rows("A", n1) if r.get("kind") == "revision"
                   and r.get("revision") == 1]
        inline_content = "Inline — short but Unicode-heavy: 中é\U0001F4D6 \u2028\u2029 done."
        pi = mk_note("n-inline", content=inline_content)
        ni = ack_field(pi, "result_ref")
        gi = typed(qy("get-note", "A", ni))
        p_neither = cli(str(REPO / "harness" / "commands.py"), "create_note",
                        "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                        "--idem-key", "n-neither")
        p_both = cli(str(REPO / "harness" / "commands.py"), "create_note",
                     "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                     "--idem-key", "n-both", "--content", "x", "--content-file", long_file)
        bad_utf8 = fresh_file("bad.bin", b"\xff\xfe not utf8 \x00\x00")
        pbad = mk_note("n-badutf8", content_file=bad_utf8)
        nul_file = fresh_file("nul.md", "before NUL \u0000 after NUL")
        pnul = mk_note("n-nul", content_file=nul_file)
        nul_count = audit("SELECT count(*) FROM arv.note WHERE content LIKE '%before NUL%';")
        ok2 = (g1 is not None and g1.get("content") == LONG_FORM
               and len(h1_rows) == 1 and h1_rows[0].get("content") == LONG_FORM
               and pi.returncode == 0 and gi is not None
               and gi.get("content") == inline_content
               and p_neither.returncode == 1 and "ARV-NTE-010" in p_neither.stdout
               and p_both.returncode == 1 and "ARV-NTE-010" in p_both.stdout
               and pbad.returncode == 1 and "ARV-NTE-010" in pbad.stdout
               and pnul.returncode == 1 and "ARV-NTE-009" in pnul.stdout
               and nul_count == "0")
        check("NTE-02", ok2,
              "long-form content (CJK, combining, astral emoji, RTL, C0 control characters, U+2028/U+2029, quotes/backslashes, trailing whitespace) round trips byte-identically through create -> get-note AND get-note-history; the inline --content arm round trips; the content-source refusals (neither/both/not-UTF-8 — ARV-NTE-010) and the NUL boundary (ARV-NTE-009, zero rows — never the mid-protocol death)",
              "the note preserves the owner's deep raw thinking losslessly — read_bytes + UTF-8 decode, no newline translation, no trimming; the NUL boundary is the standing spine residual, named at this boundary")

        # ---- NTE-03 — the append-only substrate + the strengthened revision guard
        ghost = "00000000-0000-7000-8000-00000000000d"
        before = audit("SELECT count(*) FROM arv.note;")
        up = app_sql(f"UPDATE arv.note SET content=content WHERE id='{n1}';")
        dele = app_sql(f"DELETE FROM arv.note WHERE id='{n1}';")
        up_t = super_sql(f"UPDATE arv.note SET content=content WHERE id='{n1}';")
        dele_t = super_sql(f"DELETE FROM arv.note WHERE id='{n1}';")
        after = audit("SELECT count(*) FROM arv.note;")
        # the hostile ghost-target lifecycle insert
        host_lc = app_sql(
            f"INSERT INTO arv.note_lifecycle (id, note_id, event, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) VALUES (gen_random_uuid(), "
            f"'{ghost}', 'tombstone', 'A', 'owner', 'run-hostile', 'ih', 'hostile-2', now());")
        # the PHANTOM append: revision 2 onto a never-created identity
        host_phantom = super_sql(
            f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) VALUES ('{ghost}', 2, 'phantom', 'A', "
            f"'owner', 'run-hostile', 'ih', 'hostile-4', now());")
        # the GAP append: revision 5 on an active max-1 note (NTE-05's revise makes 2 later)
        host_gap = super_sql(
            f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) SELECT id, 5, content, owner_scope, "
            f"actor, run_id, input_hash, idempotency_key, created_at FROM arv.note "
            f"WHERE id='{n1}' AND revision=1;")
        ok3 = (up.returncode == 1 and "permission denied" in up.stderr
               and dele.returncode == 1 and "permission denied" in dele.stderr
               and "ARV-CAP-005" in up_t.stderr and "ARV-CAP-005" in dele_t.stderr
               and before == after
               and host_lc.returncode == 1 and "ARV-NTE-001" in host_lc.stderr
               and host_phantom.returncode == 1 and "ARV-NTE-001" in host_phantom.stderr
               and host_gap.returncode == 1 and "ARV-NTE-011" in host_gap.stderr)
        check("NTE-03", ok3,
              "direct-DB UPDATE/DELETE on arv.note refused at BOTH boundaries (permission + ARV-CAP-005, zero rows); the hostile ghost-target lifecycle insert refused (ARV-NTE-001); the strengthened revision guard refuses the phantom append (revision 2 onto a never-created identity — ARV-NTE-001) and the gap append (revision 5 on an active max-1 note — ARV-NTE-011, the ordinal backstop promoted to the named substrate refusal); the lifecycle mutations meet ARV-CAP-005",
              "the substrate conventions of 0002/0004/0007/0008 extended to the note family: append-only, existence-in-scope, the contiguous §3.3 revision ladder (LAW-20/21/22/24)")

        # ---- NTE-04 — cross-owner isolation
        pr_abs = revise_note("n-abs", "00000000-0000-7000-8000-00000000000e",
                             content="absent target")
        pr_x_rev = revise_note("n-xrev", noteb, content="A revising B's note")
        pr_x_tomb = lifecycle("tombstone_note", "n-xtomb", noteb)
        pr_x_rest = lifecycle("restore_note", "n-xrest", noteb)
        g_x = qy("get-note", "A", noteb)
        g_xh = qy("get-note-history", "A", noteb)
        listed_a = [ln for ln in qy("list-notes", "A").stdout.splitlines() if ln.strip()]
        listed_b = [ln for ln in qy("list-notes", "B").stdout.splitlines() if ln.strip()]
        ok4 = (pr_abs.returncode == 1 and "ARV-NTE-001" in pr_abs.stdout
               and pr_x_rev.returncode == 1 and "ARV-NTE-001" in pr_x_rev.stdout
               and pr_x_tomb.returncode == 1 and "ARV-NTE-001" in pr_x_tomb.stdout
               and pr_x_rest.returncode == 1 and "ARV-NTE-001" in pr_x_rest.stdout
               and g_x.returncode == 1 and "ARV-QRY-001" in g_x.stdout
               and g_xh.returncode == 1 and "ARV-QRY-001" in g_xh.stdout
               and noteb not in listed_a and noteb in listed_b)
        check("NTE-04", ok4,
              "revise/tombstone/restore on an absent id and on ANOTHER OWNER's note are the SAME ARV-NTE-001 refusal (never a side channel); get-note/get-note-history refuse with ARV-QRY-001 and list-notes never lists the other owner's note (while the owner's own list carries it)",
              "absent and another owner's are the SAME refusal at every note-family boundary (RTM §2.10; the LAW-22 owner isolation)")

        # ---- NTE-05 — same-key replay + conflicting body + the ordinal backstop
        rep = mk_note("n-A1", content_file=long_file)
        cnt = audit(f"SELECT count(*) FROM arv.note WHERE id='{n1}';")
        conf = mk_note("n-A1", content="a different body under the same key")
        conf_cnt = audit(f"SELECT count(*) FROM arv.note WHERE id='{n1}';")
        rev2_file = fresh_file("rev2.md", "The second thinking — revised content.\nWith a second line.\n")
        pv2 = revise_note("n-A1r", n1, content_file=rev2_file)
        rep2 = revise_note("n-A1r", n1, content_file=rev2_file)
        rev_rows = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        conf2 = revise_note("n-A1r", n1, content="a conflicting revise body")
        rev_rows2 = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        # the #91 review round's Major: the same key on a DIFFERENT note is a
        # different command (ARV-CMD-409, zero effect on it) — the id rides the body
        pnb2 = mk_note("n-B2", content="the cross-note replay subject.")
        nb2 = ack_field(pnb2, "result_ref")
        px = revise_note("n-A1r", nb2, content_file=rev2_file)
        rev_rows3 = audit_rows(f"SELECT revision FROM arv.note WHERE id='{nb2}' ORDER BY revision;")
        # the ordinal backstop: the strengthened guard fires FIRST (the BEFORE
        # trigger precedes the PK)
        dupe = super_sql(f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, "
                         f"run_id, input_hash, idempotency_key, created_at) SELECT id, 2, "
                         f"content, owner_scope, actor, run_id, input_hash, idempotency_key, "
                         f"created_at FROM arv.note WHERE id='{n1}' AND revision=1;")
        ok5 = (rep.returncode == 0 and "status=replayed" in rep.stdout
               and rep.stdout.count("replayed") == 1 and cnt == "1"
               and conf.returncode == 1 and "ARV-CMD-409" in conf.stdout and conf_cnt == "1"
               and pv2.returncode == 0 and "revision=2" in pv2.stdout
               and rep2.returncode == 0 and "status=replayed" in rep2.stdout
               and rev_rows == ["1", "2"] and conf2.returncode == 1
               and "ARV-CMD-409" in conf2.stdout and rev_rows2 == ["1", "2"]
               and px.returncode == 1 and "ARV-CMD-409" in px.stdout
               and rev_rows3 == ["1"]
               and dupe.returncode == 1 and "ARV-NTE-011" in dupe.stderr)
        check("NTE-05", ok5,
              "same key + same body -> status=replayed (one effect); same key + different body -> ARV-CMD-409 (create and revise both); the SAME KEY on a DIFFERENT NOTE -> ARV-CMD-409 with zero effect on it (the target id rides the revise body — the #91 review round's Major); the direct-DB duplicate insert meets the contiguity refusal ARV-NTE-011 (the guard precedes the PK)",
              "the idempotent spine's exactly-once contract over the note family (RTM §4/LAW-23: the same key must mean the same command — a different target is a different command)")

        # ---- NTE-06 — the crash/restart matrix (create + revise + tombstone)
        nf = audit("SELECT count(*) FROM arv.note;")
        c_ab = crash("--command", "create_note", "--point", "after-begin",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create",
                     "--content", "crash-create content")
        c_pc = crash("--command", "create_note", "--point", "pre-commit",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create2",
                     "--content", "crash-create content")
        nf2 = audit("SELECT count(*) FROM arv.note;")
        c_pa = crash("--command", "create_note", "--point", "post-commit-pre-ack",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create3",
                     "--content", "the lost-ack create body")
        nf3 = audit("SELECT count(*) FROM arv.note;")
        rep_c = note_cmd("create_note", "crash-create3", client="cr-1",
                         content="the lost-ack create body")
        n_pa = ack_field(rep_c, "result_ref")
        got_pa = typed(qy("get-note", "A", n_pa))
        r_ab = crash("--command", "revise_note", "--point", "after-begin",
                     "--owner", "A", "--client-id", "cr-2", "--idem-key", "crash-revise",
                     "--id", n1, "--content", "crash-revise body")
        r_pc = crash("--command", "revise_note", "--point", "pre-commit",
                     "--owner", "A", "--client-id", "cr-2", "--idem-key", "crash-revise2",
                     "--id", n1, "--content", "crash-revise body")
        rev_after = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        r_pa = crash("--command", "revise_note", "--point", "post-commit-pre-ack",
                     "--owner", "A", "--client-id", "cr-2", "--idem-key", "crash-revise3",
                     "--id", n1, "--content", "the lost-ack revise body")
        rev_after2 = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        rep_r = note_cmd("revise_note", "crash-revise3", client="cr-2", id_=n1,
                         content="the lost-ack revise body")
        rev_after3 = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        t_pc = crash("--command", "tombstone_note", "--point", "pre-commit",
                     "--owner", "A", "--client-id", "cr-3", "--idem-key", "crash-tomb",
                     "--id", n1)
        ev_after = audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n1}';")
        t_pa = crash("--command", "tombstone_note", "--point", "post-commit-pre-ack",
                     "--owner", "A", "--client-id", "cr-3", "--idem-key", "crash-tomb2",
                     "--id", n1)
        ev_after2 = audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n1}';")
        rep_t = lifecycle("tombstone_note", "crash-tomb2", n1, client="cr-3")
        ev_after3 = audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n1}';")
        lifecycle("restore_note", "post-crash-restore", n1)  # return to active for the later cases
        ok6 = (c_ab.returncode == 2 and c_pc.returncode == 2 and nf2 == nf
               and c_pa.returncode == 2 and nf3 == str(int(nf) + 1)
               and rep_c.returncode == 0 and "status=replayed" in rep_c.stdout
               and got_pa is not None and got_pa.get("content") == "the lost-ack create body"
               and r_ab.returncode == 2 and r_pc.returncode == 2 and rev_after == ["1", "2"]
               and r_pa.returncode == 2 and rev_after2 == ["1", "2", "3"]
               and rep_r.returncode == 0 and "status=replayed" in rep_r.stdout
               and rev_after3 == ["1", "2", "3"]
               and t_pc.returncode == 2 and ev_after == "0"
               and t_pa.returncode == 2 and ev_after2 == "1"
               and rep_t.returncode == 0 and "status=replayed" in rep_t.stdout
               and ev_after3 == "1")
        check("NTE-06", ok6,
              "create/revise/tombstone at after-begin + pre-commit leave ZERO effect; at post-commit-pre-ack the effect IS committed (exit 2, no ack) and the same-key replay converges every lost ack with the recorded result — the zero-or-one-effect contract at every transaction boundary",
              "the crash-injection spine (§1.6/§3.3): a crashed command either never happened or is durably recorded — the replay resolves which (never a duplicate logical effect)")

        # ---- NTE-07 — the tombstone/restore machine
        pside = mk_note("n-side", content="the active beside.")
        nside = ack_field(pside, "result_ref")
        p7 = mk_note("n-tomb", content="the tombstone machine's subject.\nSecond line.")
        n7 = ack_field(p7, "result_ref")
        pv7 = revise_note("n-tomb-r", n7, content="the revised subject.")
        t7 = lifecycle("tombstone_note", "n-tomb-t", n7)
        g_t = qy("get-note", "A", n7)
        listed = [ln for ln in qy("list-notes", "A").stdout.splitlines() if ln.strip()]
        hist7 = history_rows("A", n7)
        h7_rev1 = [r for r in hist7 if r.get("kind") == "revision" and r.get("revision") == 1]
        h7_rev2 = [r for r in hist7 if r.get("kind") == "revision" and r.get("revision") == 2]
        h7_ev = [r for r in hist7 if r.get("kind") == "lifecycle"]
        dbl = lifecycle("tombstone_note", "n-tomb-t2", n7)
        rest = lifecycle("restore_note", "n-tomb-r1", n7)
        r_act = lifecycle("restore_note", "n-tomb-r0", n7)
        g_after = typed(qy("get-note", "A", n7))
        listed_after = [ln for ln in qy("list-notes", "A").stdout.splitlines() if ln.strip()]
        rev_t = revise_note("n-tomb-x", n7, content="revise of an active note after restore")
        # the substrate revision-append guard: a hostile revision-99 insert on
        # the TOMBSTONED note is refused; the lifecycle mutations meet ARV-CAP-005
        lifecycle("tombstone_note", "n-tomb-t3", n7)
        host_rev = super_sql(
            f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) SELECT id, 99, content, owner_scope, "
            f"actor, run_id, input_hash, idempotency_key, created_at FROM arv.note "
            f"WHERE id='{n7}' AND revision=2;")
        lc_mut = super_sql("UPDATE arv.note_lifecycle SET event='restore';")
        lifecycle("restore_note", "n-tomb-r2", n7)  # return to active for the later cases
        ok7 = (t7.returncode == 0 and "durability_rung=local_durable" in t7.stdout
               and g_t.returncode == 1 and "ARV-QRY-003" in g_t.stdout
               and n7 not in listed and nside in listed
               and len(h7_rev1) == 1 and h7_rev1[0].get("content") == "the tombstone machine's subject.\nSecond line."
               and len(h7_rev2) == 1 and h7_rev2[0].get("content") == "the revised subject."
               and len(h7_ev) == 1 and h7_ev[0].get("event") == "tombstone"
               and dbl.returncode == 1 and "ARV-NTE-004" in dbl.stdout
               and rest.returncode == 0 and r_act.returncode == 1
               and "ARV-NTE-005" in r_act.stdout
               and g_after is not None and g_after.get("content") == "the revised subject."
               and g_after.get("revision") == 2 and n7 in listed_after
               and rev_t.returncode == 0 and "revision=3" in rev_t.stdout
               and host_rev.returncode == 1 and "ARV-NTE-002" in host_rev.stderr
               and lc_mut.returncode == 1 and "ARV-CAP-005" in lc_mut.stderr)
        check("NTE-07", ok7,
              "tombstoned hides from get-note (the typed ARV-QRY-003) and list-notes (the active fixture still listed) while get-note-history retains every revision (content byte-identical) and every event; double-tombstone (ARV-NTE-004), restore-of-active (ARV-NTE-005), revise-of-tombstoned (ARV-NTE-002), and the hostile revision-append on a tombstoned note (ARV-NTE-002 at the substrate) are all refused; restore returns the note with the CURRENT revision's content unchanged",
              "the §3.3 alternation at BOTH boundaries over the note family (the 0007/0008 precedent): tombstone only from active, restore only from tombstoned, the governed history never loses a byte")

        # ---- NTE-08 — the independent current-view rebuild (the export-ready history)
        h_all = history_rows("A", n7)
        revs = [r for r in h_all if r.get("kind") == "revision"]
        cur = max(revs, key=lambda r: r["revision"])
        state = derived_state(h_all)
        g8 = typed(qy("get-note", "A", n7))
        ok8 = (state == "active" and g8 is not None
               and g8.get("revision") == cur.get("revision")
               and g8.get("content") == cur.get("content")
               and all(r.get("actor") for r in revs)
               and all(r.get("created_at") for r in revs))
        check("NTE-08", ok8,
              "the current view (state + current revision + content + attribution on every revision) re-derived from the get-note-history rows ALONE equals the get-note answer — every revision retrievable, attributable, and referenceable from history alone (the export-ready history)",
              "PLAN's P3-06 acceptance: 'every revision is retrievable, attributable, and referenceable' — the history rows carry everything the P3-09 export needs (SYS-07's authoritative substrate)")

        # ---- NTE-09 — the ack-rung pins
        p9 = mk_note("n-9", content="the rung pin.")
        n9 = ack_field(p9, "result_ref")
        p9r = revise_note("n-9r", n9, content="the rung pin, revised.")
        p9t = lifecycle("tombstone_note", "n-9t", n9)
        p9s = lifecycle("restore_note", "n-9s", n9)
        acks = [p9.stdout, p9r.stdout, p9t.stdout, p9s.stdout]
        ok9 = (p9.returncode == 0 and p9r.returncode == 0 and p9t.returncode == 0
               and p9s.returncode == 0
               and all("durability_rung=local_durable" in a for a in acks))
        check("NTE-09", ok9,
              "create/revise/tombstone/restore acks ALL name durability_rung=local_durable (SYS-01)",
              "every note-family acknowledgment reports the honest rung (RTM §3.2: local_durable = the local commit observed)")

        # ---- NTE-10 — the schema-convention audits (0009; the pg_catalog reads)
        defs = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name IN "
                          "('note', 'note_lifecycle') AND column_default IS NOT NULL;")
        trg_n = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.note'::regclass AND NOT tgisinternal;").split())
        trg_l = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.note_lifecycle'::regclass AND NOT tgisinternal;").split())
        rls_rows = [audit(f"SELECT relrowsecurity || '|' || relforcerowsecurity FROM pg_class "
                          f"WHERE relname='{t}' AND relkind='r';")
                    for t in ("note", "note_lifecycle")]
        grants = {}
        for tbl in ("note", "note_lifecycle"):
            for role in ("arv_app", "arv_read"):
                grants[(tbl, role)] = set(audit(
                    f"SELECT privilege_type FROM aclexplode((SELECT relacl FROM pg_class "
                    f"WHERE relname='{tbl}')) WHERE grantee = "
                    f"(SELECT oid FROM pg_roles WHERE rolname='{role}');").split())
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' AND "
                    "tablename IN ('note', 'note_lifecycle') AND "
                    "policyname='owner_isolation';")
        pks = [audit(f"SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE "
                     f"contype='p' AND conrelid='arv.{t}'::regclass;")
               for t in ("note", "note_lifecycle")]
        ok10 = (not defs
                and trg_n == {"note_immutable", "note_revision_guard"}
                and trg_l == {"note_lifecycle_guard", "note_lifecycle_immutable"}
                and rls_rows == ["true|true"] * 2
                and all(grants[(t, "arv_app")] >= {"INSERT", "SELECT"}
                        for t in ("note", "note_lifecycle"))
                and all(grants[(t, "arv_read")] == {"SELECT"}
                        for t in ("note", "note_lifecycle"))
                and pol == "2"
                and pks == ["PRIMARY KEY (id, revision)", "PRIMARY KEY (id)"])
        check("NTE-10", ok10,
              "the 0009 schema conventions: NO DEFAULTs on any column (LAW-24); the four triggers (two ARV-CAP-005 append-only + the alternation guard + the strengthened revision-append guard); RLS enabled AND FORCED with the owner_isolation policy; arv_app INSERT/SELECT + arv_read SELECT; the PK shapes (note (id,revision); the event table id + the ownership unique)",
              "the substrate conventions of 0002/0004/0007/0008 extended unchanged to the note family (LAW-20/21/22/24; the migration is the authority)")

        # ---- NTE-11 — the row-protocol framing on the history arm
        h1_all = history_rows("A", n1)
        r1_rows = [r for r in h1_all if r.get("kind") == "revision" and r.get("revision") == 1]
        sep_line = "The raw line separator U+2028 [\u2028] and paragraph separator U+2029 [\u2029] inside one line.\n"
        ok11 = (len(r1_rows) == 1
                and r1_rows[0].get("content") == LONG_FORM   # the U+2028/U+2029 survived byte-exact
                and sep_line in (r1_rows[0].get("content") or "")
                and all(isinstance(r, dict) for r in h1_all))
        check("NTE-11", ok11,
              "U+2028/U+2029 inside the note CONTENT travel raw inside the JSON string and survive get-note-history with intact newline-only framing (the content byte-identical against the fixture's own string — never a psql round-trip)",
              "row_to_json emits one escaped JSON line per row; the reader splits on the newline ONLY — U+2028/U+2029 must never corrupt the framing (the #88/#89/#90 lesson on every new arm)")

        # ---- NTE-12 — the competing-revisions SERIALIZATION (two revisers)
        p12 = mk_note("n-12", content="the serialization subject.")
        n12 = ack_field(p12, "result_ref")
        # the held ACCESS EXCLUSIVE on arv.note parks the first reviser AFTER its
        # advisory-lock acquisition — the wait observations stay exact
        t_hold = Session(DB, "postgres", "A")
        t_hold.send("BEGIN; LOCK TABLE arv.note IN ACCESS EXCLUSIVE MODE; \\echo HELD12")
        t_hold.read_until("HELD12")
        mv1 = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                "revise_note", "--owner", "A", "--actor", "owner",
                                "--client-id", "cli-12", "--idem-key", "race-rev-1",
                                "--id", n12, "--content", "competing revision one — the first writer"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mv1_blocked = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                            "AND wait_event_type='Lock' AND query LIKE '%FROM arv.note n WHERE n.id%'")
        lock_held = super_sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a "
                              "ON a.pid=l.pid WHERE l.locktype='advisory' AND l.granted "
                              "AND a.usename='arv_app' AND a.query LIKE '%FROM arv.note n WHERE n.id%'").stdout.strip()
        mv2 = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                "revise_note", "--owner", "A", "--actor", "owner",
                                "--client-id", "cli-12", "--idem-key", "race-rev-2",
                                "--id", n12, "--content", "competing revision two — the second writer"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mv2_waited = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                           "AND wait_event='advisory' AND query LIKE '%pg_advisory_xact_lock%'")
        t_hold.close()  # the release: the parked first reviser proceeds, commits, frees the lock
        mv1_rc, mv2_rc = mv1.wait(timeout=120), mv2.wait(timeout=120)
        revs12 = sorted(int(r) for r in audit_rows(f"SELECT revision FROM arv.note WHERE id='{n12}';"))
        c12 = {r["revision"]: r["content"] for r in note_rows(n12)}
        rep12 = revise_note("race-rev-1", n12,
                            content="competing revision one — the first writer", client="cli-12")
        ok12 = (mv1_blocked and lock_held == "1" and mv2_waited
                and mv1_rc == 0 and mv2_rc == 0 and revs12 == [1, 2, 3]
                and c12.get(1) == "the serialization subject."
                and c12.get(2) == "competing revision one — the first writer"
                and c12.get(3) == "competing revision two — the second writer"
                and rep12.returncode == 0 and "status=replayed" in rep12.stdout)
        check("NTE-12", ok12,
              "two concurrent revisers on one note serialize on the per-note advisory xact lock: the parked first reviser HOLDS the lock across its complete blocked transition (pg_locks), the second WAITS on it; both revisions commit (2 then 3, each byte-identical to its authored content, revision 1 untouched) — legal ordering, conflict never silently destroys a revision; the same-key replay converges",
              "the card's 'competing revisions' acceptance + the #90 round-3 lesson applied from the start: the complete revise lives INSIDE one transaction behind the advisory lock the 0009 guards take")

        # ---- NTE-13 — the revise-vs-tombstone SERIALIZATION + THE CANONICAL LOCK KEY
        p13 = mk_note("n-13", content="the tombstone-race subject.")
        n13 = ack_field(p13, "result_ref")
        t_hold2 = Session(DB, "postgres", "A")
        t_hold2.send("BEGIN; LOCK TABLE arv.note IN ACCESS EXCLUSIVE MODE; \\echo HELD13")
        t_hold2.read_until("HELD13")
        # the reviser invoked with the UPPERCASED id — the canonical-key pin (F3)
        mv = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                               "revise_note", "--owner", "A", "--actor", "owner",
                               "--client-id", "cli-13", "--idem-key", "race-rev-t",
                               "--id", n13.upper(), "--content", "the revise that must land BEFORE the tombstone"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mv_blocked = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                           "AND wait_event_type='Lock' AND query LIKE '%FROM arv.note n WHERE n.id%'")
        lock2 = super_sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a "
                          "ON a.pid=l.pid WHERE l.locktype='advisory' AND l.granted "
                          "AND a.usename='arv_app' AND a.query LIKE '%FROM arv.note n WHERE n.id%'").stdout.strip()
        tb = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                               "tombstone_note", "--owner", "A", "--actor", "owner",
                               "--client-id", "cli-13", "--idem-key", "race-tomb-t",
                               "--id", n13],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        # the tombstone's serialized form waits at its OWN first statement (the
        # F1 repair), not inside the trigger
        tb_waited = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                          "AND wait_event='advisory' AND query LIKE '%pg_advisory_xact_lock%'", 11.0)
        t_hold2.close()          # the release: the revise commits, THEN the tombstone proceeds
        mv_rc, tb_rc = mv.wait(timeout=120), tb.wait(timeout=120)
        revs13 = sorted(int(r) for r in audit_rows(f"SELECT revision FROM arv.note WHERE id='{n13}';"))
        ev13 = int(audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n13}';"))
        # the late revise, again via the MIXED-CASE id: the clean refusal, never
        # the split-key stall wrapper
        rev_late = revise_note("race-late", n13.upper(),
                               content="the late mixed-case revise — must be refused")
        # the F1 pin: the history renders the SERIALIZED COMMIT ORDER (the lifecycle
        # timestamp taken INSIDE its locked section)
        h13 = history_rows("A", n13)
        kinds13 = [r.get("kind") for r in h13]
        rev2_ts = next((r["created_at"] for r in h13
                        if r.get("kind") == "revision" and r.get("revision") == 2), None)
        tomb_ts = next((r["created_at"] for r in h13
                        if r.get("kind") == "lifecycle" and r.get("event") == "tombstone"), None)
        ok13 = (mv_blocked and lock2 == "1" and tb_waited
                and mv_rc == 0 and tb_rc == 0 and ev13 == 1 and revs13 == [1, 2]
                and rev_late.returncode == 1 and "ARV-NTE-002" in rev_late.stdout
                and "ARV-CMD-010" not in rev_late.stdout
                and "ARV-CMD-010" not in mv.stdout and "ARV-CMD-010" not in tb.stdout
                and kinds13 == ["revision", "revision", "lifecycle"]
                and rev2_ts is not None and tomb_ts is not None and rev2_ts <= tomb_ts)
        check("NTE-13", ok13,
              "the revise-vs-tombstone interleaving is SERIALIZED on the per-note advisory xact lock — invoked with the UPPERCASED id, the reviser takes the SAME canonical lock key as the substrate guards (hashtext of the uuid's lowercase text): it holds the lock across its complete blocked transition, the tombstone waits ON it until the revise commits (revision 2 then exactly one tombstone event); a revision NEVER commits after tombstoning; the late mixed-case revise gets the clean ARV-NTE-002 — never the ARV-CMD-010 stall wrapper of the split-key defect; the history renders the serialized commit order (the lifecycle timestamp taken INSIDE its locked section)",
              "RTM §3.3: edit only from active — the complete transition inside ONE transaction behind the same advisory lock the lifecycle guard takes; one note, one canonical lock key (claim-055 F5's class closed for the note family — the review round's F3)")

        # ---- NTE-14 — the UUID-SPELLING CANONICALIZATION (the #91 round-2
        # CodeRabbit 4439931169: PostgreSQL's uuid input also accepts braced,
        # no-hyphen, and uppercase spellings of ONE note): every spelling is
        # the SAME logical command — the payload REPLAYS across spellings
        # (LAW-23) and the lock key is the CANONICAL key (the substrate
        # guards' own hashtext key — never a second granted key for one note)
        p14 = mk_note("n-14c", content="the spelling-canonicalization subject.")
        n14id = ack_field(p14, "result_ref")
        rf14 = fresh_file("n14.md", "the NTE-14 canonicalization body.\n")
        pv14 = revise_note("n-14r", n14id, content_file=rf14)
        pr_b = revise_note("n-14r", "{" + n14id + "}", content_file=rf14)
        pr_n = revise_note("n-14r", n14id.replace("-", ""), content_file=rf14)
        t14 = Session(DB, "postgres", "A")
        t14.send(f"SELECT pg_advisory_lock(hashtext('{n14id}')); \\echo HELD14")
        t14.read_until("HELD14")
        mv14 = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                 "revise_note", "--owner", "A", "--actor", "owner",
                                 "--client-id", "cli-14b", "--idem-key", "n-14rb",
                                 "--id", "{" + n14id + "}", "--content", "v3 via the braced spelling"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, env=ENV)
        wait14 = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                       "AND wait_event='advisory' AND query LIKE '%pg_advisory_xact_lock%'")
        g14 = super_sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a "
                        "ON a.pid=l.pid WHERE l.locktype='advisory' AND l.granted "
                        "AND a.usename='arv_app';").stdout.strip()
        t14.close()  # the release: the braced revise proceeds and commits
        mv14rc = mv14.wait(timeout=120)
        tb14 = lifecycle("tombstone_note", "n-14t", n14id)
        tb14u = lifecycle("tombstone_note", "n-14t", n14id.upper())
        tb14b = lifecycle("tombstone_note", "n-14t", "{" + n14id + "}")
        revs14 = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n14id}' ORDER BY revision;")
        ev14 = int(audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n14id}';"))
        ok14 = (pv14.returncode == 0 and "revision=2" in pv14.stdout
                and pr_b.returncode == 0 and "status=replayed" in pr_b.stdout
                and pr_n.returncode == 0 and "status=replayed" in pr_n.stdout
                and wait14 and g14 == "0" and mv14rc == 0
                and "revision=3" in mv14.stdout
                and tb14.returncode == 0 and "durability_rung" in tb14.stdout
                and tb14u.returncode == 0 and "status=replayed" in tb14u.stdout
                and tb14b.returncode == 0 and "status=replayed" in tb14b.stdout
                and revs14 == ["1", "2", "3"] and ev14 == 1)
        check("NTE-14", ok14,
              "every PostgreSQL-accepted UUID spelling of one note is the SAME logical command: the braced/no-hyphen revise retry and the uppercase/braced tombstone retry all REPLAY the committed result (never ARV-CMD-409); the boundary lock key is the canonical key — the braced revise waits AT its own first statement while the canonical key is held (zero granted advisory keys for arv_app, never a second key for one note)",
              "LAW-23 + the one-lock contract: the payload AND the lock key carry the canonical UUID text (the substrate guards' own hashtext key); a spelling is a spelling, never an identity (the #91 round-2 finding 4439931169)")

        print()
        if FAILS:
            print(f"RED — {len(FAILS)} failing: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-06 acceptance suite, slice one (NTE-01..14) passes")
        return 0
    finally:
        # the scratch DB DROPPED after every run (ARV_KEEP_DB overrides)
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
