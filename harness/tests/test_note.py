#!/usr/bin/env python3
"""harness/tests/test_note.py — P3-06 acceptance suite (the Note machine's
contract pins; RTM §2.5 item 7 + item 9 + §3.3/§3.2, SYS-01/02/03 primary,
SYS-01/04 standing, PLAN's P3-06 card).

Red-first (LAW-11): committed BEFORE the implementation; at the predecessor
f86e52b the suite fails with ARV-TEST-000 (machinery-absent: commands.py's
create_note/revise_note/tombstone_note/restore_note and query.py's get-note
arm do not exist; migration 0009 absent — the record-18 §4.1 / red-01.txt
precedent class).

THE MACHINE (RTM §2.5 item 7 — "the owner's deep raw thinking"):

  the row      identity + immutable revisions + the AUTHORED long-form
               content — the note is free-standing by default (NO source
               binding by construction, unlike the highlight/bookmark
               families); the content is owner-authored bytes read
               LOSSLESSLY (read_bytes + utf-8 decode — no newline
               translation, no trimming); long-form and Unicode preserved
               byte-identically; the diagram/structured-block contract is
               NOT frozen here (P4-C's reservation — plain text only)
  references   explicit, version-aware, per-revision rows (arv.note_reference):
               kind IN (work | source | anchor | highlight | note); a
               highlight/note reference MUST name the target revision
               (kind:id@rev — version-aware by construction); a
               work/source/anchor reference MUST NOT (the source id IS the
               version; work/anchor carry no revision dimension) — the
               shape is a substrate CHECK; the TARGET must exist in the
               caller's scope (absent, another owner's, and a nonexistent
               target revision are the SAME ARV-NTE-003 refusal, never a
               side channel); duplicate targets in one command are refused
               (ARV-NTE-008 — the reference set is a set); the reference
               rows of a PAST revision are immutable — a historical
               reference stays accurate after the target revises
  revisions    a NEW immutable row per revise (PK (id, revision) — the
               0004/0007/0008 revision-per-row shape); the new revision
               carries its OWN full content and reference set (replacement
               semantics; the prior revision's rows untouched); THE
               SERIALIZED TRANSITION (the #90 round-3 lesson applied from
               the start): the complete revise — the per-note advisory xact
               lock (the SAME lock the 0009 guards take) acquired as the
               transaction's FIRST statement, then the state read, the
               active validation, the reference validation, the inserts,
               and the commit, ALL inside ONE transaction (build_txn) —
               competing revisers serialize (both revisions persist, legal
               ordering; never a silent overwrite) and a revision can
               never commit after tombstoning
  tombstone    the §3.3 machine shared with the highlight/bookmark
               families: typed lifecycle EVENT rows (append-only,
               owner-scoped, provenance-complete); tombstoned hides from
               ordinary retrieval (list excludes, get-note refuses with
               the typed ARV-QRY-003) while the governed history retains
               every revision, every reference row, and every event;
               restore returns it (the revisions were never touched)
  substrate    migration 0009's guards: the lifecycle alternation trigger
               (advisory-locked per-note: tombstone only from active,
               restore only from tombstoned — ARV-NTE-004/005), the
               revision-append guard (a revision > 1 append on a
               tombstoned note refused — ARV-NTE-002 at the substrate),
               the reference guard (the note (id, revision) the row
               belongs to must exist — ARV-NTE-007; the target must exist
               in scope — ARV-NTE-003), the version-aware CHECK, the
               ARV-CAP-005 append-only triggers on all three tables, RLS
               enabled AND FORCED, the composite-ownership convention
  acks         every note-family ack names durability_rung=local_durable
               (SYS-01)

The note-family refusal codes (the diagnostics contract):
  ARV-NTE-001  the note does not exist in the caller's scope (absent and
               another owner's are the SAME refusal, never a side channel)
  ARV-NTE-002  the note is tombstoned — restore precedes edit (command
               boundary + the substrate revision-append guard)
  ARV-NTE-003  the reference TARGET does not exist in the caller's scope /
               the named target revision does not exist (absent, another
               owner's, nonexistent revision: the SAME refusal)
  ARV-NTE-004  already tombstoned (the second tombstone)
  ARV-NTE-005  not tombstoned (the restore of an active note)
  ARV-NTE-006  the reference SHAPE refusal (unknown kind; malformed id;
               missing @rev on a highlight/note reference; a forbidden
               @rev on a work/source/anchor reference)
  ARV-NTE-007  the substrate reference guard: the note (id, revision) the
               reference row belongs to does not exist (the hostile
               direct-write backstop)
  ARV-NTE-008  duplicate reference target in one command (set semantics)
  ARV-NTE-009  NUL (U+0000) in the content — PostgreSQL TEXT cannot carry
               it; the named note-boundary refusal of the standing spine
               residual (refused, never the ugly mid-protocol death)
  ARV-NTE-010  the content-source refusal (neither/both of --content /
               --content-file; unreadable; not valid UTF-8)

Cases (the NTE registry — this file is the contract's declaration):
  NTE-01 the create happy path + the structural pins: the ack carries
         revision=1 + durability_rung=local_durable; the note row's exact
         nine-column set (content-bearing, NO source binding — the
         free-standing law); the reference rows land per-revision with the
         exact supplied set; a free-standing note (zero refs) is legal;
         provenance complete on every row
  NTE-02 lossless long-form + Unicode: multi-paragraph long-form content
         with CJK, combining marks, astral emoji, RTL, control characters
         (C0 except NUL), U+2028/U+2029 — create → get-note → history: the
         content byte-identical at every read; the NUL boundary refused
         with ARV-NTE-009 (zero effect); the inline --content arm round
         trips too
  NTE-03 dangling targets + invalid versions + the append-only substrate:
         absent work/source/anchor/highlight/note targets refused
         (ARV-NTE-003); a highlight reference at a nonexistent revision
         refused (ARV-NTE-003 — the invalid source-version relationship);
         the shape refusals (highlight ref without @rev; work ref with
         @rev — ARV-NTE-006); direct-DB UPDATE/DELETE on arv.note and
         arv.note_reference refused at BOTH boundaries (permission +
         ARV-CAP-005); the hostile direct note_reference insert with a
         dangling target refused by the substrate guard (ARV-NTE-003);
         the hostile ghost-target lifecycle insert refused (ARV-NTE-001);
         the hostile revision-append on a tombstoned note refused by the
         substrate guard (ARV-NTE-002); THE PHANTOM-IDENTITY AND GAP APPENDS
         refused by the strengthened revision guard (the review round's
         convergent finding: a revision > 1 onto a never-created identity —
         ARV-NTE-001; a non-contiguous revision (max+2 or beyond) on an
         ACTIVE note — ARV-NTE-011, the ordinal backstop promoted to the
         named substrate refusal); the version-aware CHECK pinned
         (a work ref carrying a revision — refused at the substrate)
  NTE-04 cross-owner isolation: revise/tombstone/restore on an absent id
         and on ANOTHER OWNER's note are the SAME ARV-NTE-001 refusal;
         references to another owner's objects are the SAME ARV-NTE-003
         refusal (never a side channel); get/list/history never observe
         the other owner's notes
  NTE-05 same-key replay + conflicting body + the ordinal backstop: same
         key + same logical body (the reference order shuffled — the
         canonical form) -> status=replayed (one effect); same key +
         different body -> ARV-CMD-409 (zero effect); a direct-DB
         duplicate (id, revision) insert -> the PK violation
  NTE-06 the crash/restart matrix: create + revise + tombstone at
         after-begin / pre-commit (zero effect) and post-commit-pre-ack
         (the lost ack: the effect IS committed); the same-key replay
         converges every lost ack
  NTE-07 the tombstone/restore machine: tombstoned hidden from get-note
         (ARV-QRY-003) and list-notes (an ACTIVE fixture beside — the
         exclusion never vacuous); the history retains content, reference
         rows, and events; restore returns it (the content byte-identical);
         double-tombstone (ARV-NTE-004), restore-of-active (ARV-NTE-005),
         revise-of-tombstoned (ARV-NTE-002) refused; lifecycle mutations
         refused at the substrate
  NTE-08 the version-aware reference machine: a historical highlight
         reference stays accurate after the target revises (rev 2 exists;
         the note still refs rev 1); a note-to-note historical reference
         stays accurate after the referenced note revises; each revision
         carries its OWN reference set (rev 1's set immutable after the
         revise that carries a different set)
  NTE-09 the independent current-view rebuild (THE EXPORT-READY HISTORY):
         the current view (state + current revision + content + reference
         set + attribution) re-derived from the get-note-history rows
         ALONE equals the get-note answer — every revision retrievable,
         attributable, and referenceable from history alone
  NTE-10 the ack-rung pins: create/revise/tombstone/restore acks ALL name
         durability_rung=local_durable (SYS-01)
  NTE-11 the schema-convention audits (0009): no DEFAULTs (LAW-24), the
         append-only + alternation + revision-append + reference triggers,
         RLS enabled AND FORCED + the owner policy, the grants, the PK
         shapes, the version-aware CHECK
  NTE-12 the row-protocol framing on the history arm: U+2028/U+2029 inside
         the note CONTENT travel raw inside the JSON string and survive
         get-note-history with intact newline-only framing (the
         #88/#89/#90 lesson on every new arm)
  NTE-13 the competing-revisions SERIALIZATION (the card's "competing
         revisions — conflict never silently destroys a revision"): two
         concurrent revisers on one note serialize on the per-note
         advisory xact lock — the blocked first reviser HOLDS the lock
         across its complete transition (pg_locks), the second waits ON
         it; both revisions commit (2 then 3, each byte-identical to its
         authored content, revision 1 untouched) — legal ordering, no
         silent overwrite; the same-key replay converges
  NTE-14 the revise-vs-tombstone SERIALIZATION (the #90 round-3 Major's
         class, applied from the start — BMK-13's deterministic form): the
         blocked revise holds the advisory lock across its complete
         transition while the tombstone waits ON it — the revision commits
         first, the tombstone then proceeds from the committed active
         state; a revision NEVER commits after tombstoning; the revise
         that arrives after the tombstone gets the clean ARV-NTE-002; the
         history arm renders the serialized commit order (the lifecycle
         command's timestamp is taken INSIDE its locked section — the
         review round's F1 repair: a tombstone can never render before a
         revision that committed first)
  NTE-15 the case-variant lock-key serialization (the review round's F3,
         claim-055 F5's class closed for the note family): a revise invoked
         with the UPPERCASED note id takes the SAME canonical lock key as
         the substrate guards (hashtext of the uuid's canonical lowercase
         text form) — a concurrent tombstone still serializes against it
         (the late revise refused with the clean ARV-NTE-002, never the
         ARV-CMD-010 stall wrapper of the split-key defect)

Run: python3 harness/tests/test_note.py   (exit 0 = green)
"""
import hashlib
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


# ---------------------------------------------------------------- the RED gate
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

# ---------------------------------------------------------------- the harness
from harness.adapters import clock, pg  # noqa: E402
from harness.commands import Session  # noqa: E402

DB = ENV = None

# the reading fixture: distinctive spans for the highlight targets (the note
# family authors its own content; the SOURCE exists to be referenced)
TEXT = ("The note-bearing reading.\n"
        "Second paragraph: the first span lives here, plainly.\n"
        "Third paragraph: the moved span lives here instead.\n"
        "Fourth paragraph closes.\n")

# the long-form Unicode round-trip fixture (NTE-02/NTE-12): CJK, combining,
# astral, RTL, control characters (C0 minus NUL), the raw separators, and
# enough bulk to be honestly long-form
LONG_FORM = (
    "# Deep note — the reading session\n\n"
    "Opening block: free-standing owner thought, preserved exactly.\n"
    "A tab-indented line follows.\n"
    "\ttab start, content, tab\tend.\n"
    "Carriage return and line feed together:\r\nthe CR-LF line.\n"
    "A bare carriage return:\rthe bare-CR line.\n\n"
    + "".join(
        f"Paragraph {i:03d} — 中文字符 preserved; the combining sequence e\u0301 "
        f"(e + U+0301); an astral emoji \U0001F4D6 and another \U0001F9E0; "
        f"right-to-left عربية rode through; the symbols \u00bb \u2192 \u2261 ride raw.\n"
        for i in range(40))
    + "The raw line separator U+2028 [\u2028] and paragraph separator U+2029 [\u2029] inside one line.\n"
    "Control characters: SOH \u0001 STX \u0002 BEL \u0007 VT \u000b FF \u000c ESC-with-the-letter-following \u001b[0m.\n"
    "Quote ' single, \" double, backslash \\ literal, percent %, dollar $$, semicolon ;\n"
    "A final line with trailing spaces   and a trailing tab\t.\n"
)


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=240, env=ENV)


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


def revise_hl(key: str, hl_id: str, start: int, end: int,
              owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "revise_highlight",
               "--owner", owner, "--actor", "owner", "--client-id", client,
               "--idem-key", key, "--id", hl_id, "--start", str(start), "--end", str(end))


def note_cmd(op: str, key: str, owner: str = "A", client: str = "cli-1",
             id_: str = None, content: str = None, content_file=None,
             refs: list = None) -> subprocess.CompletedProcess:
    """The note-family CLI driver. refs: list of canonical ref strings
    ('kind:id' or 'kind:id@rev')."""
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client, "--idem-key", key]
    if id_ is not None:
        a += ["--id", id_]
    if content is not None:
        a += ["--content", content]
    if content_file is not None:
        a += ["--content-file", content_file]
    for r in (refs or []):
        a += ["--ref", r]
    return cli(*a)


def mk_note(key: str, content: str = None, content_file=None, refs: list = None,
            owner: str = "A", client: str = "cli-1") -> subprocess.CompletedProcess:
    return note_cmd("create_note", key, owner=owner, client=client,
                    content=content, content_file=content_file, refs=refs)


def revise_note(key: str, note_id: str, content: str = None, content_file=None,
                refs: list = None, owner: str = "A",
                client: str = "cli-1") -> subprocess.CompletedProcess:
    return note_cmd("revise_note", key, owner=owner, client=client, id_=note_id,
                    content=content, content_file=content_file, refs=refs)


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
    # NEWLINE-ONLY framing (the ANC-10 law): the note content carries raw
    # U+2028/U+2029 which a str.splitlines() reader would split on — the
    # audit reads of content-bearing rows use the same framing law as the
    # history arm
    return [ln for ln in audit(query).split("\n") if ln.strip()]


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


def note_rows(note_id: str, owner: str = "A") -> list:
    """The authoritative note rows, read independently (arv_read) as ONE
    escaped JSON line per revision — the content carries raw newlines and
    U+2028, so a pipe-delimited psql read would fragment the row (the framing
    law applied to the audit reads too)."""
    rows = audit_rows(f"SELECT row_to_json(t)::text FROM (SELECT revision, content, actor, "
                      f"run_id, input_hash, idempotency_key FROM arv.note "
                      f"WHERE id='{note_id}' ORDER BY revision) t;")
    return [json.loads(r) for r in rows]


def ref_rows(note_id: str, revision: int) -> list:
    """The per-revision reference rows, read independently."""
    return audit_rows(f"SELECT ref_kind || '|' || ref_id || '|' || "
                      f"COALESCE(ref_revision::text, '-') FROM arv.note_reference "
                      f"WHERE note_id='{note_id}' AND note_revision={revision} "
                      f"ORDER BY ref_kind, ref_id;")


def history_rows(owner: str, note_id: str) -> list:
    p = qy("get-note-history", owner, note_id)
    if p.returncode != 0:
        return []
    return [json.loads(ln) for ln in p.stdout.split("\n") if ln.strip()]


def typed(p: subprocess.CompletedProcess) -> "dict | None":
    """The typed answer: ONE JSON line on stdout, exit 0.  The framing is
    NEWLINE-ONLY (the ANC-10 law — the note CONTENT carries raw U+2028/U+2029
    which a str.splitlines() reader would split on; the split('\n') form is
    the framing law applied to the test's own reader)."""
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

        # ---------------- the fixture: real bytes, two owners, a revised highlight
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "reading.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("first span")
        e1 = s1 + len("first span")
        s2 = TEXT.index("moved span")
        e2 = s2 + len("moved span")

        p = import_src("imp-A", "The Reading", str(src_file))
        sid_a = ack_field(p, "result_ref")
        wid_a = ack_field(p, "work_id")
        pb = import_src("imp-B", "B's book", str(src_file), owner="B")
        sid_b = ack_field(pb, "result_ref")
        wid_b = ack_field(pb, "work_id")
        # owner B's own highlight + note (the cross-owner targets)
        phb = mk_highlight("hl-B1", sid_b, s1, e1, owner="B")
        hlb = ack_field(phb, "result_ref")
        pnb = mk_note("note-B1", content="B's private deep thinking.", owner="B")
        noteb = ack_field(pnb, "result_ref")
        # owner A's highlight: revision 1, then revised to 2 (the version ladder)
        ph1 = mk_highlight("hl-A1", sid_a, s1, e1)
        h1 = ack_field(ph1, "result_ref")
        ph2 = revise_hl("hl-A1r", h1, s2, e2)
        assert ph2.returncode == 0, "fixture: the highlight revise must succeed"
        anc_a = audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{h1}' "
                      f"AND revision=1;")

        # ---- NTE-01 — the create happy path + the structural pins
        long_file = fresh_file("deep-note.md", LONG_FORM)
        refs_a = [f"work:{wid_a}", f"source:{sid_a}", f"anchor:{anc_a}",
                  f"highlight:{h1}@1"]
        p1 = mk_note("n-A1", content_file=long_file, refs=refs_a)
        n1 = ack_field(p1, "result_ref")
        rev1 = ack_field(p1, "revision")
        rung1 = ack_field(p1, "durability_rung")
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='note' "
                          "ORDER BY ordinal_position;")
        expected_cols = ["id", "revision", "content", "owner_scope", "actor",
                         "run_id", "input_hash", "idempotency_key", "created_at"]
        rows1 = note_rows(n1)
        got_refs = ref_rows(n1, 1)
        want_refs = sorted([f"work|{wid_a}|-", f"source|{sid_a}|-",
                            f"anchor|{anc_a}|-", f"highlight|{h1}|1"])
        # the free-standing law: a note with NO references is legal
        p1f = mk_note("n-Afree", content="A free-standing thought.")
        nfree = ack_field(p1f, "result_ref")
        free_refs = audit(f"SELECT count(*) FROM arv.note_reference "
                          f"WHERE note_id='{nfree}';")
        ok1 = (p1.returncode == 0 and "status=committed" in p1.stdout
               and rev1 == "1" and rung1 == "local_durable"
               and cols == expected_cols                       # exactly the nine — no source binding
               and len(rows1) == 1 and rows1[0]["revision"] == 1
               and rows1[0]["content"] == LONG_FORM            # byte-identical content
               and rows1[0]["actor"] == "owner"               # attribution
               and rows1[0]["idempotency_key"] == "n-A1"      # the command provenance ref
               and got_refs == want_refs                       # the per-revision reference set
               and p1f.returncode == 0 and free_refs == "0")
        check("NTE-01", ok1,
              "create appends the revision-1 row (the authored content byte-identical, provenance complete, the exact nine-column set — content-bearing, NO source binding) + the per-revision reference rows (work/source/anchor versionless, highlight@1 version-aware); a free-standing note carries zero reference rows; the ack carries revision=1 + durability_rung=local_durable",
              "the note is the owner's free-standing deep thinking: identity + authored content + optional explicit references ONLY (RTM §2.5 item 7)")

        # ---- NTE-02 — lossless long-form + Unicode round trips
        g1 = typed(qy("get-note", "A", n1))
        h1_rows = [r for r in history_rows("A", n1) if r.get("kind") == "revision"
                   and r.get("revision") == 1]
        inline_content = "Inline — short but Unicode-heavy: 中\u00e9\U0001F4D6 \u2028\u2029 done."
        pi = mk_note("n-inline", content=inline_content)
        ni = ack_field(pi, "result_ref")
        gi = typed(qy("get-note", "A", ni))
        nul_file = fresh_file("nul.md", "before NUL \u0000 after NUL")
        pnul = mk_note("n-nul", content_file=nul_file)
        nul_count = audit(f"SELECT count(*) FROM arv.note WHERE content LIKE '%before NUL%';")
        bad_utf8 = fresh_file("bad.bin", b"\xff\xfe not utf8 \x00\x00")
        pbad = mk_note("n-badutf8", content_file=bad_utf8)
        ok2 = (g1 is not None and g1.get("content") == LONG_FORM
               and len(h1_rows) == 1 and h1_rows[0].get("content") == LONG_FORM
               and pi.returncode == 0 and gi is not None
               and gi.get("content") == inline_content
               and pnul.returncode == 1 and "ARV-NTE-009" in pnul.stdout
               and nul_count == "0"
               and pbad.returncode == 1 and "ARV-NTE-010" in pbad.stdout)
        check("NTE-02", ok2,
              "long-form content (40 paragraphs: CJK, combining e+U+0301, astral emoji, RTL, C0 control characters, U+2028/U+2029, quotes/backslashes, trailing whitespace) round trips byte-identically through create -> get-note AND get-note-history; the inline --content arm round trips too; NUL in the content is refused with the named ARV-NTE-009 (zero rows — never the mid-protocol death); a non-UTF-8 content file is refused with ARV-NTE-010",
              "the note preserves the owner's deep raw thinking losslessly — read_bytes + UTF-8 decode, no newline translation, no trimming; the NUL boundary is the standing spine residual, named at this boundary (RTM §2.5 item 7)")

        # ---- NTE-03 — dangling targets + invalid versions + the append-only substrate
        ghost = "00000000-0000-7000-8000-00000000000d"
        pr_w = mk_note("n-dw", content="x", refs=[f"work:{ghost}"])
        pr_s = mk_note("n-ds", content="x", refs=[f"source:{ghost}"])
        pr_a = mk_note("n-da", content="x", refs=[f"anchor:{ghost}"])
        pr_h = mk_note("n-dh", content="x", refs=[f"highlight:{h1}@1", f"highlight:{ghost}@1"])
        pr_n = mk_note("n-dn", content="x", refs=[f"note:{ghost}@1"])
        pr_rev = mk_note("n-drev", content="x", refs=[f"highlight:{h1}@99"])
        # the shape refusals: highlight without @rev; work WITH @rev; unknown kind; malformed id
        pr_shape1 = mk_note("n-sh1", content="x", refs=[f"highlight:{h1}"])
        pr_shape2 = mk_note("n-sh2", content="x", refs=[f"work:{wid_a}@2"])
        pr_shape3 = mk_note("n-sh3", content="x", refs=[f"chapter:{wid_a}"])
        pr_shape4 = mk_note("n-sh4", content="x", refs=["work:not-a-uuid"])
        # the duplicate-refusal (set semantics)
        pr_dup = mk_note("n-dup", content="x", refs=[f"work:{wid_a}", f"source:{sid_a}",
                                                     f"work:{wid_a}"])
        before = audit("SELECT count(*) FROM arv.note;")
        before_r = audit("SELECT count(*) FROM arv.note_reference;")
        up = app_sql(f"UPDATE arv.note SET content=content WHERE id='{n1}';")
        dele = app_sql(f"DELETE FROM arv.note WHERE id='{n1}';")
        up_r = app_sql(f"UPDATE arv.note_reference SET ref_id=ref_id WHERE note_id='{n1}';")
        dele_r = app_sql(f"DELETE FROM arv.note_reference WHERE note_id='{n1}';")
        up_t = super_sql(f"UPDATE arv.note SET content=content WHERE id='{n1}';")
        dele_t = super_sql(f"DELETE FROM arv.note WHERE id='{n1}';")
        up_rt = super_sql(f"UPDATE arv.note_reference SET ref_id=ref_id WHERE note_id='{n1}';")
        dele_rt = super_sql(f"DELETE FROM arv.note_reference WHERE note_id='{n1}';")
        after = audit("SELECT count(*) FROM arv.note;")
        after_r = audit("SELECT count(*) FROM arv.note_reference;")
        # the hostile direct reference insert: a dangling target meets the substrate guard
        host_ref = app_sql(
            f"INSERT INTO arv.note_reference (id, note_id, note_revision, ref_kind, ref_id, "
            f"ref_revision, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
            f"VALUES (gen_random_uuid(), '{n1}', 1, 'work', '{ghost}', NULL, 'A', 'owner', "
            f"'run-hostile', 'ih', 'hostile-1', now());")
        # the hostile ghost-target lifecycle insert
        host_lc = app_sql(
            f"INSERT INTO arv.note_lifecycle (id, note_id, event, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) VALUES (gen_random_uuid(), "
            f"'{ghost}', 'tombstone', 'A', 'owner', 'run-hostile', 'ih', 'hostile-2', now());")
        # the version-aware CHECK at the substrate: a work ref carrying a revision
        host_shape = app_sql(
            f"INSERT INTO arv.note_reference (id, note_id, note_revision, ref_kind, ref_id, "
            f"ref_revision, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
            f"VALUES (gen_random_uuid(), '{n1}', 1, 'work', '{wid_a}', 3, 'A', 'owner', "
            f"'run-hostile', 'ih', 'hostile-3', now());")
        # THE STRENGTHENED REVISION GUARD (the review round's convergent finding):
        # the phantom-identity append (revision 2 onto a never-created id) and the
        # non-contiguous gap append (revision 5 on an ACTIVE note whose max is 2)
        # are both refused at the substrate
        host_phantom = super_sql(
            f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) VALUES ('{ghost}', 2, 'phantom', 'A', "
            f"'owner', 'run-hostile', 'ih', 'hostile-4', now());")
        host_gap = super_sql(
            f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) SELECT id, 5, content, owner_scope, "
            f"actor, run_id, input_hash, idempotency_key, created_at FROM arv.note "
            f"WHERE id='{n1}' AND revision=1;")
        ok3 = (pr_w.returncode == 1 and "ARV-NTE-003" in pr_w.stdout
               and pr_s.returncode == 1 and "ARV-NTE-003" in pr_s.stdout
               and pr_a.returncode == 1 and "ARV-NTE-003" in pr_a.stdout
               and pr_h.returncode == 1 and "ARV-NTE-003" in pr_h.stdout
               and pr_n.returncode == 1 and "ARV-NTE-003" in pr_n.stdout
               and pr_rev.returncode == 1 and "ARV-NTE-003" in pr_rev.stdout
               and pr_shape1.returncode == 1 and "ARV-NTE-006" in pr_shape1.stdout
               and pr_shape2.returncode == 1 and "ARV-NTE-006" in pr_shape2.stdout
               and pr_shape3.returncode == 1 and "ARV-NTE-006" in pr_shape3.stdout
               and pr_shape4.returncode == 1 and "ARV-NTE-006" in pr_shape4.stdout
               and pr_dup.returncode == 1 and "ARV-NTE-008" in pr_dup.stdout
               and up.returncode == 1 and "permission denied" in up.stderr
               and dele.returncode == 1 and "permission denied" in dele.stderr
               and up_r.returncode == 1 and "permission denied" in up_r.stderr
               and dele_r.returncode == 1 and "permission denied" in dele_r.stderr
               and "ARV-CAP-005" in up_t.stderr and "ARV-CAP-005" in dele_t.stderr
               and "ARV-CAP-005" in up_rt.stderr and "ARV-CAP-005" in dele_rt.stderr
               and before == after and before_r == after_r
               and host_ref.returncode == 1 and "ARV-NTE-003" in host_ref.stderr
               and host_lc.returncode == 1 and "ARV-NTE-001" in host_lc.stderr
               and host_shape.returncode == 1 and "note_reference_ref_shape_check" in host_shape.stderr
               and host_phantom.returncode == 1 and "ARV-NTE-001" in host_phantom.stderr
               and host_gap.returncode == 1 and "ARV-NTE-011" in host_gap.stderr)
        check("NTE-03", ok3,
              "every dangling target class refused at the boundary (ARV-NTE-003: absent work/source/anchor/highlight/note AND a highlight at a nonexistent revision — the invalid source-version relationship); the shape classes refused (ARV-NTE-006: missing @rev, forbidden @rev, unknown kind, malformed id); duplicates refused (ARV-NTE-008); direct-DB UPDATE/DELETE refused at BOTH boundaries on arv.note and arv.note_reference (permission + ARV-CAP-005, zero rows); the substrate reference guard refuses the hostile dangling insert (ARV-NTE-003), the ghost-target lifecycle insert (ARV-NTE-001), and the version-aware CHECK refuses the work-ref-with-revision shape",
              "references are explicit, version-aware, and validated against the caller's scope at the command boundary AND the substrate (RTM §2.5 item 7; the 0007/0008 composite-reference convention)")

        # ---- NTE-04 — cross-owner isolation
        pr_abs = revise_note("n-abs", "00000000-0000-7000-8000-00000000000e",
                             content="absent target")
        pr_x_rev = revise_note("n-xrev", noteb, content="A revising B's note")
        pr_x_tomb = lifecycle("tombstone_note", "n-xtomb", noteb)
        pr_x_rest = lifecycle("restore_note", "n-xrest", noteb)
        pr_x_ref_w = mk_note("n-xrefw", content="x", refs=[f"work:{wid_b}"])
        pr_x_ref_s = mk_note("n-xrefs", content="x", refs=[f"source:{sid_b}"])
        pr_x_ref_h = mk_note("n-xrefh", content="x", refs=[f"highlight:{hlb}@1"])
        pr_x_ref_n = mk_note("n-xrefn", content="x", refs=[f"note:{noteb}@1"])
        g_x = qy("get-note", "A", noteb)
        g_xh = qy("get-note-history", "A", noteb)
        listed_a = [ln for ln in qy("list-notes", "A").stdout.splitlines() if ln.strip()]
        ok4 = (pr_abs.returncode == 1 and "ARV-NTE-001" in pr_abs.stdout
               and pr_x_rev.returncode == 1 and "ARV-NTE-001" in pr_x_rev.stdout
               and pr_x_tomb.returncode == 1 and "ARV-NTE-001" in pr_x_tomb.stdout
               and pr_x_rest.returncode == 1 and "ARV-NTE-001" in pr_x_rest.stdout
               and pr_x_ref_w.returncode == 1 and "ARV-NTE-003" in pr_x_ref_w.stdout
               and pr_x_ref_s.returncode == 1 and "ARV-NTE-003" in pr_x_ref_s.stdout
               and pr_x_ref_h.returncode == 1 and "ARV-NTE-003" in pr_x_ref_h.stdout
               and pr_x_ref_n.returncode == 1 and "ARV-NTE-003" in pr_x_ref_n.stdout
               and g_x.returncode == 1 and "ARV-QRY-001" in g_x.stdout
               and g_xh.returncode == 1 and "ARV-QRY-001" in g_xh.stdout
               and noteb not in listed_a)
        check("NTE-04", ok4,
              "revise/tombstone/restore on an absent id and on ANOTHER OWNER's note are the SAME ARV-NTE-001 refusal; references to another owner's work/source/highlight/note are the SAME ARV-NTE-003 refusal (never a side channel revealing object existence); get-note/get-note-history refuse with ARV-QRY-001 and list-notes never lists the other owner's note",
              "absent and another owner's are the SAME refusal at every note-family boundary (RTM §2.10; the LAW-22 owner isolation)")

        # ---- NTE-05 — same-key replay + conflicting body + the ordinal backstop
        # replay: the same key + the same logical body with the reference ORDER SHUFFLED
        # (the canonical form hashes identically) -> replayed, one effect
        rep = mk_note("n-A1", content_file=long_file,
                      refs=[f"highlight:{h1}@1", f"work:{wid_a}", f"anchor:{anc_a}",
                            f"source:{sid_a}"])
        cnt = audit(f"SELECT count(*) FROM arv.note WHERE id='{n1}';")
        cnt_r = audit(f"SELECT count(*) FROM arv.note_reference WHERE note_id='{n1}';")
        # conflicting body: the same key, different content -> ARV-CMD-409, zero effect
        conf = mk_note("n-A1", content="a different body under the same key")
        conf_cnt = audit(f"SELECT count(*) FROM arv.note WHERE id='{n1}';")
        # the revise replay + conflict
        rev2_file = fresh_file("rev2.md", "The second thinking — revised content.\nWith a second line.\n")
        pv2 = revise_note("n-A1r", n1, content_file=rev2_file, refs=[f"source:{sid_a}"])
        rep2 = revise_note("n-A1r", n1, content_file=rev2_file, refs=[f"source:{sid_a}"])
        rev_rows = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        conf2 = revise_note("n-A1r", n1, content="a conflicting revise body")
        rev_rows2 = audit_rows(f"SELECT revision FROM arv.note WHERE id='{n1}' ORDER BY revision;")
        # the ordinal backstop: a direct-DB duplicate (id, revision) insert -> the
        # strengthened revision guard fires FIRST (the contiguity refusal — the
        # BEFORE trigger precedes the PK constraint; the PK remains the backstop
        # for any guard-bypassed path)
        dupe = super_sql(f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, "
                         f"run_id, input_hash, idempotency_key, created_at) SELECT id, 2, "
                         f"content, owner_scope, actor, run_id, input_hash, idempotency_key, "
                         f"created_at FROM arv.note WHERE id='{n1}' AND revision=1;")
        ok5 = (rep.returncode == 0 and "status=replayed" in rep.stdout
               and rep.stdout.count("replayed") == 1 and cnt == "1" and cnt_r == "4"
               and conf.returncode == 1 and "ARV-CMD-409" in conf.stdout and conf_cnt == "1"
               and pv2.returncode == 0 and "revision=2" in pv2.stdout
               and rep2.returncode == 0 and "status=replayed" in rep2.stdout
               and rev_rows == ["1", "2"] and conf2.returncode == 1
               and "ARV-CMD-409" in conf2.stdout and rev_rows2 == ["1", "2"]
               and dupe.returncode == 1 and "ARV-NTE-011" in dupe.stderr)
        check("NTE-05", ok5,
              "same key + same logical body (reference order shuffled — the canonical form) -> status=replayed with exactly one effect row set; same key + different body -> ARV-CMD-409 with zero effect (create and revise both); the direct-DB duplicate (id, revision) insert meets the PK violation — the ordinal backstop",
              "the idempotent spine's exactly-once contract over the note family (RTM §4; a unique constraint is not a replay promise but it IS the ordinal backstop)")

        # ---- NTE-06 — the crash/restart matrix (create + revise + tombstone)
        nf = audit("SELECT count(*) FROM arv.note;")
        nfr = audit("SELECT count(*) FROM arv.note_reference;")
        c_ab = crash("--command", "create_note", "--point", "after-begin",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create",
                     "--content", "crash-create content")
        c_pc = crash("--command", "create_note", "--point", "pre-commit",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create2",
                     "--content", "crash-create content")
        nf2 = audit("SELECT count(*) FROM arv.note;")
        nfr2 = audit("SELECT count(*) FROM arv.note_reference;")
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
        # restore for the later cases (the machine returns to active)
        lifecycle("restore_note", "post-crash-restore", n1)
        ok6 = (c_ab.returncode == 2 and c_pc.returncode == 2 and nf2 == nf and nfr2 == nfr
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
              "create/revise/tombstone at after-begin + pre-commit leave ZERO effect (no note row, no reference rows, no event); at post-commit-pre-ack the effect IS committed (exit 2, no ack) and the same-key replay converges every lost ack with the recorded result — the zero-or-one-effect contract at every transaction boundary",
              "the crash-injection spine (§1.6/§3.3): a crashed command either never happened or is durably recorded — the replay resolves which (never a duplicate logical effect)")

        # ---- NTE-07 — the tombstone/restore machine
        # an ACTIVE fixture beside (the exclusion is never vacuous)
        pside = mk_note("n-side", content="the active beside.")
        nside = ack_field(pside, "result_ref")
        p7 = mk_note("n-tomb", content="the tombstone machine's subject.\nSecond line.")
        n7 = ack_field(p7, "result_ref")
        # a second-revision reference set to prove the history retains PAST sets
        pv7 = revise_note("n-tomb-r", n7, content="the revised subject.",
                          refs=[f"source:{sid_a}"])
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
        # the substrate revision-append guard: a hostile revision-3 insert on the
        # TOMBSTONED note is refused (re-tombstone first)
        lifecycle("tombstone_note", "n-tomb-t3", n7)
        host_rev = super_sql(
            f"INSERT INTO arv.note (id, revision, content, owner_scope, actor, run_id, "
            f"input_hash, idempotency_key, created_at) SELECT id, 99, content, owner_scope, "
            f"actor, run_id, input_hash, idempotency_key, created_at FROM arv.note "
            f"WHERE id='{n7}' AND revision=2;")
        lc_mut = super_sql(f"UPDATE arv.note_lifecycle SET event='restore' "
                           f"WHERE note_id='{n7}';")
        lifecycle("restore_note", "n-tomb-r2", n7)  # return to active for NTE-08/09
        ok7 = (t7.returncode == 0 and "durability_rung=local_durable" in t7.stdout
               and g_t.returncode == 1 and "ARV-QRY-003" in g_t.stdout
               and n7 not in listed and nside in listed
               and len(h7_rev1) == 1 and h7_rev1[0].get("content") == "the tombstone machine's subject.\nSecond line."
               and len(h7_rev2) == 1 and h7_rev2[0].get("content") == "the revised subject."
               and h7_rev2[0].get("refs") == [{"kind": "source", "id": sid_a, "revision": None}]
               and h7_rev1[0].get("refs") is None
               and len(h7_ev) == 1 and h7_ev[0].get("event") == "tombstone"
               and dbl.returncode == 1 and "ARV-NTE-004" in dbl.stdout
               and r_act.returncode == 1 and "ARV-NTE-005" in r_act.stdout
               and rest.returncode == 0 and g_after is not None
               and g_after.get("content") == "the revised subject."
               and g_after.get("revision") == 2
               and n7 in listed_after
               and rev_t.returncode == 0 and "revision=3" in rev_t.stdout
               and host_rev.returncode == 1 and "ARV-NTE-002" in host_rev.stderr
               and lc_mut.returncode == 1 and "ARV-CAP-005" in lc_mut.stderr)
        check("NTE-07", ok7,
              "tombstoned hides from get-note (the typed ARV-QRY-003) and list-notes (the active fixture still listed) while get-note-history retains every revision (content byte-identical), each revision's OWN reference set, and every event; double-tombstone (ARV-NTE-004), restore-of-active (ARV-NTE-005), and the hostile revision-append on a tombstoned note (ARV-NTE-002 at the substrate) are refused; restore returns the note with the CURRENT revision's content unchanged; lifecycle mutations meet ARV-CAP-005",
              "the §3.3 alternation at BOTH boundaries over the note family (the 0007/0008 precedent): tombstone only from active, restore only from tombstoned, the governed history never loses a byte")

        # ---- NTE-08 — the version-aware reference machine
        # N8 refs highlight H at its HISTORICAL revision 1; H has revision 2 already
        p8 = mk_note("n-8", content="the version-aware subject.",
                     refs=[f"highlight:{h1}@1"])
        n8 = ack_field(p8, "result_ref")
        g8 = typed(qy("get-note", "A", n8))
        # revise the highlight again (revision 3): the note's reference stays @1
        revise_hl("hl-A1r2", h1, s1, e1)
        g8b = typed(qy("get-note", "A", n8))
        h8 = history_rows("A", n8)
        h8r1 = [r for r in h8 if r.get("kind") == "revision" and r.get("revision") == 1]
        # a reference at the CURRENT revision (3) is accepted
        p8c = mk_note("n-8c", content="refs the current revision.",
                      refs=[f"highlight:{h1}@3"])
        # a note-to-note historical reference: N9 refs N8@1; N8 then revises
        p9 = mk_note("n-9", content="refs the note at its first revision.",
                     refs=[f"note:{n8}@1"])
        n9 = ack_field(p9, "result_ref")
        revise_note("n-8r", n8, content="the note's second thinking.")
        g9 = typed(qy("get-note", "A", n9))
        # each revision carries its OWN reference set: revise n9 with a different set
        pv9 = revise_note("n-9r", n9, content="the second thinking of n9.",
                          refs=[f"source:{sid_a}", f"note:{n8}@1"])
        h9 = history_rows("A", n9)
        h9r1 = [r for r in h9 if r.get("kind") == "revision" and r.get("revision") == 1]
        h9r2 = [r for r in h9 if r.get("kind") == "revision" and r.get("revision") == 2]
        ok8 = (g8 is not None and g8.get("refs") == [{"kind": "highlight", "id": h1, "revision": 1}]
               and g8b is not None and g8b.get("refs") == [{"kind": "highlight", "id": h1, "revision": 1}]
               and len(h8r1) == 1 and h8r1[0].get("refs") == [{"kind": "highlight", "id": h1, "revision": 1}]
               and p8c.returncode == 0
               and g9 is not None and g9.get("refs") == [{"kind": "note", "id": n8, "revision": 1}]
               and pv9.returncode == 0
               and h9r1[0].get("refs") == [{"kind": "note", "id": n8, "revision": 1}]
               and h9r2[0].get("refs") == [{"kind": "note", "id": n8, "revision": 1},
                                            {"kind": "source", "id": sid_a, "revision": None}])
        check("NTE-08", ok8,
              "a historical highlight reference stays accurate after the target revises again (still @1 — the reference is to the immutable revision, never a silent retarget); a reference at the current revision is accepted; a note-to-note historical reference stays @1 after the referenced note revises; each revision carries its OWN reference set (revision 1's set immutable after the revise that carries a different set)",
              "references are version-aware and immutable-in-meaning: the referenced (id, revision) pair is pinned at write time (RTM §2.5 item 7 — referenceable historical revisions)")

        # ---- NTE-09 — the independent current-view rebuild (the export-ready history)
        # n9 now: revisions 1 and 2, active, revision 2 = the current view
        h_all = history_rows("A", n9)
        revs = [r for r in h_all if r.get("kind") == "revision"]
        cur = max(revs, key=lambda r: r["revision"])
        state = derived_state(h_all)
        g9b = typed(qy("get-note", "A", n9))
        rebuilt_refs = cur.get("refs") or []
        answer_refs = g9b.get("refs") or []
        ok9 = (state == "active" and g9b is not None
               and g9b.get("revision") == cur.get("revision")
               and g9b.get("content") == cur.get("content")
               and rebuilt_refs == answer_refs
               and all(r.get("actor") for r in revs)
               and all(r.get("created_at") for r in revs))
        check("NTE-09", ok9,
              "the current view (state + current revision + content + the reference set + attribution on every revision) re-derived from the get-note-history rows ALONE equals the get-note answer — every revision retrievable, attributable, and referenceable from history alone (the export-ready history)",
              "PLAN's P3-06 acceptance: 'every revision is retrievable, attributable, and referenceable' — the history rows carry everything the P3-09 export needs (SYS-07's authoritative substrate)")

        # ---- NTE-10 — the ack-rung pins
        p10 = mk_note("n-10", content="the rung pin.")
        n10 = ack_field(p10, "result_ref")
        p10r = revise_note("n-10r", n10, content="the rung pin, revised.")
        p10t = lifecycle("tombstone_note", "n-10t", n10)
        p10s = lifecycle("restore_note", "n-10s", n10)
        acks = [p10.stdout, p10r.stdout, p10t.stdout, p10s.stdout]
        ok10 = (p10.returncode == 0 and p10r.returncode == 0 and p10t.returncode == 0
                and p10s.returncode == 0
                and all("durability_rung=local_durable" in a for a in acks))
        check("NTE-10", ok10,
              "create/revise/tombstone/restore acks ALL name durability_rung=local_durable (SYS-01)",
              "every note-family acknowledgment reports the honest rung (RTM §3.2: local_durable = the local commit observed)")

        # ---- NTE-11 — the schema-convention audits (0009; the pg_catalog reads)
        defs = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name IN "
                          "('note', 'note_lifecycle', 'note_reference') "
                          "AND column_default IS NOT NULL;")
        trg_n = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.note'::regclass AND NOT tgisinternal;").split())
        trg_l = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.note_lifecycle'::regclass AND NOT tgisinternal;").split())
        trg_r = set(audit("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.note_reference'::regclass AND NOT tgisinternal;").split())
        rls_rows = [audit(f"SELECT relrowsecurity || '|' || relforcerowsecurity FROM pg_class "
                          f"WHERE relname='{t}' AND relkind='r';")
                    for t in ("note", "note_lifecycle", "note_reference")]
        grants = {}
        for tbl in ("note", "note_lifecycle", "note_reference"):
            for role in ("arv_app", "arv_read"):
                grants[(tbl, role)] = set(audit(
                    f"SELECT privilege_type FROM aclexplode((SELECT relacl FROM pg_class "
                    f"WHERE relname='{tbl}')) WHERE grantee = "
                    f"(SELECT oid FROM pg_roles WHERE rolname='{role}');").split())
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' AND "
                    "tablename IN ('note', 'note_lifecycle', 'note_reference') AND "
                    "policyname='owner_isolation';")
        pks = [audit(f"SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE "
                     f"contype='p' AND conrelid='arv.{t}'::regclass;")
               for t in ("note", "note_lifecycle", "note_reference")]
        checks_c = audit_rows("SELECT conname FROM pg_constraint WHERE conrelid = "
                              "'arv.note_reference'::regclass AND contype = 'c' "
                              "ORDER BY conname;")
        ok11 = (not defs
                and trg_n == {"note_immutable", "note_revision_guard"}
                and trg_l == {"note_lifecycle_guard", "note_lifecycle_immutable"}
                and trg_r == {"note_reference_guard", "note_reference_immutable"}
                and rls_rows == ["true|true"] * 3
                and all(grants[(t, "arv_app")] >= {"INSERT", "SELECT"}
                        for t in ("note", "note_lifecycle", "note_reference"))
                and all(grants[(t, "arv_read")] == {"SELECT"}
                        for t in ("note", "note_lifecycle", "note_reference"))
                and pol == "3"
                and pks == ["PRIMARY KEY (id, revision)", "PRIMARY KEY (id)",
                            "PRIMARY KEY (id)"]
                and "note_reference_ref_shape_check" in checks_c)
        check("NTE-11", ok11,
              "the 0009 schema conventions: NO DEFAULTs on any column (LAW-24 — ids/clock via adapters); the six triggers (three ARV-CAP-005 append-only + the lifecycle alternation + the revision-append + the reference guards); RLS enabled AND FORCED on all three tables with the owner_isolation policy; arv_app INSERT/SELECT + arv_read SELECT on all three; the PK shapes (note (id,revision); the event/reference tables id + the ownership uniques); the version-aware CHECK (note_reference_ref_shape_check)",
              "the substrate conventions of 0002/0004/0007/0008 extended unchanged to the note family (LAW-20/21/22/24; the migration is the authority)")

        # ---- NTE-12 — the row-protocol framing on the history arm
        # LONG_FORM carries raw U+2028 and U+2029 inside its separator line; the
        # NEWLINE-ONLY reader on history_rows must keep the row intact
        h1_all = history_rows("A", n1)
        r1_rows = [r for r in h1_all if r.get("kind") == "revision" and r.get("revision") == 1]
        sep_line = "The raw line separator U+2028 [\u2028] and paragraph separator U+2029 [\u2029] inside one line.\n"
        ok12 = (len(r1_rows) == 1
                and r1_rows[0].get("content") == LONG_FORM   # the U+2028/U+2029 survived byte-exact
                and sep_line in (r1_rows[0].get("content") or "")
                and all(isinstance(r, dict) for r in h1_all))
        check("NTE-12", ok12,
              "U+2028/U+2029 inside the note CONTENT travel raw inside the JSON string and survive get-note-history with intact newline-only framing (the content byte-identical against the fixture's own string — never a psql round-trip)",
              "row_to_json emits one escaped JSON line per row; the reader splits on the newline ONLY — U+2028/U+2029 must never corrupt the framing (the #88/#89/#90 lesson on every new arm)")

        # ---- NTE-13 — the competing-revisions SERIALIZATION (two revisers)
        p13 = mk_note("n-13", content="the serialization subject.")
        n13 = ack_field(p13, "result_ref")
        # the held ACCESS EXCLUSIVE on arv.note_reference parks each reviser
        # AFTER its advisory-lock acquisition (the ref insert is the first
        # post-lock write) — the tombstone/lifecycle paths never touch this
        # table before the advisory lock, so the wait observations are exact
        t_hold = Session(DB, "postgres", "A")
        t_hold.send("BEGIN; LOCK TABLE arv.note_reference IN ACCESS EXCLUSIVE MODE; \\echo HELD13")
        t_hold.read_until("HELD13")
        mv1 = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                "revise_note", "--owner", "A", "--actor", "owner",
                                "--client-id", "cli-13", "--idem-key", "race-rev-1",
                                "--id", n13, "--content", "competing revision one — the first writer",
                                "--ref", f"source:{sid_a}"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mv1_blocked = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                            "AND wait_event_type='Lock' AND query LIKE '%INSERT INTO arv.note_reference%'")
        lock_held = super_sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a "
                              "ON a.pid=l.pid WHERE l.locktype='advisory' AND l.granted "
                              "AND a.usename='arv_app' AND a.query LIKE '%INSERT INTO arv.note_reference%'").stdout.strip()
        mv2 = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                "revise_note", "--owner", "A", "--actor", "owner",
                                "--client-id", "cli-13", "--idem-key", "race-rev-2",
                                "--id", n13, "--content", "competing revision two — the second writer",
                                "--ref", f"source:{sid_a}"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mv2_waited = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                           "AND wait_event='advisory' AND query LIKE '%pg_advisory_xact_lock%'")
        t_hold.close()  # the release: the parked first reviser proceeds, commits, frees the lock
        mv1_rc, mv2_rc = mv1.wait(timeout=120), mv2.wait(timeout=120)
        revs13 = sorted(int(r) for r in audit_rows(f"SELECT revision FROM arv.note WHERE id='{n13}';"))
        c13 = {r["revision"]: r["content"] for r in note_rows(n13)}
        rep13 = revise_note("race-rev-1", n13, content="competing revision one — the first writer",
                            refs=[f"source:{sid_a}"], client="cli-13")
        ok13 = (mv1_blocked and lock_held == "1" and mv2_waited
                and mv1_rc == 0 and mv2_rc == 0 and revs13 == [1, 2, 3]
                and c13.get(1) == "the serialization subject."
                and c13.get(2) == "competing revision one — the first writer"
                and c13.get(3) == "competing revision two — the second writer"
                and rep13.returncode == 0 and "status=replayed" in rep13.stdout)
        check("NTE-13", ok13,
              "two concurrent revisers on one note serialize on the per-note advisory xact lock: the blocked first reviser HOLDS the lock across its complete blocked transition (pg_locks), the second WAITS on it; both revisions commit (2 then 3, each byte-identical to its authored content, revision 1 untouched) — legal ordering, conflict never silently destroys a revision; the same-key replay converges",
              "the card's 'competing revisions' acceptance + the #90 round-3 lesson applied from the start: the complete revise lives INSIDE one transaction behind the advisory lock the 0009 guards take")

        # ---- NTE-14 — the revise-vs-tombstone SERIALIZATION (a revision never commits after tombstoning)
        p14 = mk_note("n-14", content="the tombstone-race subject.")
        n14 = ack_field(p14, "result_ref")
        t_hold2 = Session(DB, "postgres", "A")
        t_hold2.send("BEGIN; LOCK TABLE arv.note_reference IN ACCESS EXCLUSIVE MODE; \\echo HELD14")
        t_hold2.read_until("HELD14")
        mv = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                               "revise_note", "--owner", "A", "--actor", "owner",
                               "--client-id", "cli-14", "--idem-key", "race-rev-t",
                               "--id", n14, "--content", "the revise that must land BEFORE the tombstone",
                               "--ref", f"source:{sid_a}"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mv_blocked = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                           "AND wait_event_type='Lock' AND query LIKE '%INSERT INTO arv.note_reference%'")
        lock2 = super_sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a "
                          "ON a.pid=l.pid WHERE l.locktype='advisory' AND l.granted "
                          "AND a.usename='arv_app' AND a.query LIKE '%INSERT INTO arv.note_reference%'").stdout.strip()
        tb = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                               "tombstone_note", "--owner", "A", "--actor", "owner",
                               "--client-id", "cli-14", "--idem-key", "race-tomb-t",
                               "--id", n14],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        # the tombstone's serialized form takes the advisory lock as its OWN first
        # statement (the F1 repair) — it waits THERE, not inside the trigger
        tb_waited = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                          "AND wait_event='advisory' AND query LIKE '%pg_advisory_xact_lock%'", 11.0)
        t_hold2.close()          # the release: the revise commits, THEN the tombstone proceeds
        mv_rc, tb_rc = mv.wait(timeout=120), tb.wait(timeout=120)
        revs14 = sorted(int(r) for r in audit_rows(f"SELECT revision FROM arv.note WHERE id='{n14}';"))
        ev14 = int(audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n14}';"))
        rev_late = revise_note("race-late", n14, content="the late revise — must be refused")
        # the F1 pin: the history renders the SERIALIZED COMMIT ORDER — the revision-2
        # row's created_at precedes the tombstone event's (both timestamps were taken
        # INSIDE their locked sections, so the render order follows the commit order)
        h14 = history_rows("A", n14)
        kinds14 = [r.get("kind") for r in h14]
        rev2_ts = next((r["created_at"] for r in h14
                        if r.get("kind") == "revision" and r.get("revision") == 2), None)
        tomb_ts = next((r["created_at"] for r in h14
                        if r.get("kind") == "lifecycle" and r.get("event") == "tombstone"), None)
        ok14 = (mv_blocked and lock2 == "1" and tb_waited
                and mv_rc == 0 and tb_rc == 0 and ev14 == 1 and revs14 == [1, 2]
                and rev_late.returncode == 1 and "ARV-NTE-002" in rev_late.stdout
                and kinds14 == ["revision", "revision", "lifecycle"]
                and rev2_ts is not None and tomb_ts is not None and rev2_ts <= tomb_ts)
        check("NTE-14", ok14,
              "the revise-vs-tombstone interleaving is SERIALIZED on the per-note advisory xact lock: the blocked revise holds it across its complete transition, the tombstone waits ON it until the revise commits (revision 2 then exactly one tombstone event); a revise that arrives AFTER the tombstone gets the clean ARV-NTE-002 — a revision never commits after tombstoning; the history renders the serialized commit order (the lifecycle timestamp taken INSIDE its locked section — the F1 repair)",
              "RTM §3.3: edit only from active — the complete transition inside ONE transaction behind the same advisory lock the lifecycle guard takes (the #90 round-3 Major's class, applied from the start)")

        # ---- NTE-15 — the case-variant lock-key serialization (F3, claim-055 F5's class closed)
        p15 = mk_note("n-15", content="the case-variant subject.")
        n15 = ack_field(p15, "result_ref")
        t_hold3 = Session(DB, "postgres", "A")
        t_hold3.send("BEGIN; LOCK TABLE arv.note_reference IN ACCESS EXCLUSIVE MODE; \\echo HELD15")
        t_hold3.read_until("HELD15")
        mv_u = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                 "revise_note", "--owner", "A", "--actor", "owner",
                                 "--client-id", "cli-15", "--idem-key", "race-rev-u",
                                 "--id", n15.upper(), "--content", "the uppercase-id revise",
                                 "--ref", f"source:{sid_a}"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        mvu_blocked = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                            "AND wait_event_type='Lock' AND query LIKE '%INSERT INTO arv.note_reference%'")
        # the canonical-key advisory lock is held by the UPPERCASED-id reviser
        lock_u = super_sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a "
                           "ON a.pid=l.pid WHERE l.locktype='advisory' AND l.granted "
                           "AND a.usename='arv_app' AND a.query LIKE '%INSERT INTO arv.note_reference%'").stdout.strip()
        tb_l = subprocess.Popen([sys.executable, str(REPO / "harness" / "commands.py"),
                                 "tombstone_note", "--owner", "A", "--actor", "owner",
                                 "--client-id", "cli-15", "--idem-key", "race-tomb-l",
                                 "--id", n15],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)
        tb_l_waited = _poll("SELECT count(*) FROM pg_stat_activity WHERE usename='arv_app' "
                            "AND wait_event='advisory' AND query LIKE '%pg_advisory_xact_lock%'", 11.0)
        t_hold3.close()
        mvu_rc, tbl_rc = mv_u.wait(timeout=120), tb_l.wait(timeout=120)
        revs15 = sorted(int(r) for r in audit_rows(f"SELECT revision FROM arv.note WHERE id='{n15}';"))
        ev15 = int(audit(f"SELECT count(*) FROM arv.note_lifecycle WHERE note_id='{n15}';"))
        # the late revise, again via the MIXED-CASE id: the clean refusal, never the
        # split-key stall wrapper
        rev_late15 = revise_note("race-late15", n15.upper(),
                                 content="the late mixed-case revise — must be refused")
        ok15 = (mvu_blocked and lock_u == "1" and tb_l_waited
                and mvu_rc == 0 and tbl_rc == 0 and ev15 == 1 and revs15 == [1, 2]
                and rev_late15.returncode == 1 and "ARV-NTE-002" in rev_late15.stdout
                and "ARV-CMD-010" not in rev_late15.stdout
                and "ARV-CMD-010" not in mv_u.stdout and "ARV-CMD-010" not in tb_l.stdout)
        check("NTE-15", ok15,
              "the case-variant lock-key serialization: a revise invoked with the UPPERCASED note id takes the SAME canonical lock key as the substrate guards (hashtext of the uuid's canonical lowercase text) — the concurrent tombstone serializes against it (the revision commits first, exactly one tombstone event), and the late mixed-case revise gets the clean ARV-NTE-002 — never the ARV-CMD-010 stall wrapper of the split-key defect",
              "one note, one lock key: the boundary's advisory lock must be the substrate's canonical key whatever the CLI spelling (claim-055 F5's class, closed for the note family — the review round's F3)")

        print()
        if FAILS:
            print(f"RED — {len(FAILS)} failing: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-06 acceptance suite (NTE-01..15) passes")
        return 0
    finally:
        # the rig's scratch database DROPPED after every suite run (the #89
        # round-2 convention; ARV_KEEP_DB overrides for local inspection)
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
