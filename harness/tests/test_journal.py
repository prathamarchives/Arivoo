#!/usr/bin/env python3
"""harness/tests/test_journal.py — P4-C slice three acceptance suite (CLAIM-072,
the journal/blocks surface: the writing lab; PLAN's elaborated P4-C slice
three card; record 64 §2).
Red-first (LAW-11): at CLAIM-072's commit A 87ffe31 (on CLAIM-071's merged
head 78b3654) the suite fails with ARV-TEST-000 (machinery-absent;
red-01.txt) — the journal_block/revise_journal_block commands, the
list-journal/get-journal/get-journal-history read arms, and migration 0016
are absent.

THE CONTRACT (P4-C slice three's letter): journal as a writing lab —
source-optional raw/creative blocks, long raw thinking preserved
losslessly, no forced short-note funnel:

- THE BLOCK ROWS — append-only, owner-scoped, the raw|creative kind
  vocabulary CLOSED at the substrate (the named CHECK refuses
  out-of-vocabulary kinds below the command); the LONG raw thinking
  preserved LOSSLESSLY (the full text stored — never a truncated form,
  never a funneled rewrite; the write->read round-trip byte-honest);
  revisions are NEW rows (the governed-history convention).
- THE WRITE — through the spine's own ack contract (idempotent, the frozen
  grammar, the crash-matrix membership via crash.py; the client-outbox ride
  re-homed to the FOLLOWING slice by the LAW-05 split — the membership and
  the delivery land TOGETHER there, never the dead-letter window):
  result_ref=<block>@<revision>.
- THE READ ARMS — the journal listing (bounded/paginated on the P4-00b
  contract, the keyset cursor, the version key) + the single-block read
  (the lossless round-trip) + the governed history (every revision).
- THE SOURCE-OPTIONAL LAW — a block binds a source only when the author
  says so (an optional binding, never forced; a sourceless block is a
  FIRST-CLASS journal row).
- THE NO-FORCED-FUNNEL LAW — the journal never forces the short-note form:
  the landed note machine stays its own surface (no silent conversion
  either way).

Cases (the JNL registry; each pin's full statement lives at its check()):
  JNL-01 the lossless round-trip: a LONG raw block (multi-paragraph, the
         framing-law characters — pipes, newlines, U+2028, the CJK — and
         >8 KB) written through the --file channel acks with the frozen
         grammar (status=committed result_ref=<block>@1 revision=1
         durability_rung=local_durable api_version=1); a FRESH
         get-journal returns the content BYTE-IDENTICAL (the full long
         raw thinking, never truncated); the creative kind ditto; the
         row's column set carries content TEXT (no truncating length)
  JNL-02 the closed kind vocabulary + the channel law + the typed
         refusals: an out-of-vocabulary kind refuses ARV-JNL-002 (named,
         zero effect — never clamped); neither/both content channels
         refuse ARV-JNL-003 (the NTE-010 channel-law class); the empty
         content refuses ARV-JNL-004; the absent/cross-owner block on the
         revise path is the SAME refusal ARV-JNL-001 (the no-oracle); the
         absent/cross-owner source at the bind refuses ARV-JNL-005 (the
         no-oracle at the binding); every refusal leaves ZERO rows
  JNL-03 the source-OPTIONAL law + the no-forced-funnel law: a sourceless
         block is a FIRST-CLASS row (acks, reads, lists — never a forced
         binding); a source-bound block carries the binding in the read
         answer; a journal write leaves arv.note's row-count UNCHANGED
         (the note machine never invoked — no silent conversion); the
         note machine's own surface still works (its rows stay its own)
  JNL-04 the revision machine + the governed history + the spine's whole
         contract: the revise command appends revision 2 (a NEW row;
         revision 1 intact); the current read returns revision 2's
         content byte-honest; the history returns EVERY revision in
         order; the idempotency (same key+body -> replayed, the same
         result_ref; same key+different body -> ARV-CMD-409, zero
         effect); the ENQUEUE pin (the delivery-carrying form —
         CLAIM-073's re-home LANDED: every committed journal write
         carries its outbox row in the SAME transaction, the refusals
         and replays adding none — the family rides the client outbox
         like every landed family); the crash matrix's lost-ack arm
         (post-commit-pre-ack exits 2, the effect committed, the replay
         converges)
  JNL-05 the read arms' list contract + the owner isolation:
         list-journal bounded/paginated (the ARV-QRY-004 bounds
         refusals, the keyset walk at --limit 2, the version header, the
         observed truth markers, the empty journal's two-line answer);
         every JSON row carries api_version=1; owner B sees only B's
         blocks; get-journal on absent vs cross-owner is the byte-equal
         ARV-QRY-001 refusal
  JNL-06 the reserved surface + the 0016 substrate conventions:
         capability.py's journal/blocks row (owner_phase P4-C, the
         LANDED verbs named, the reader-client exclusion); the schema
         audited — NO DEFAULTs (LAW-24), RLS enabled AND FORCED + the
         owner policy, the grants (INSERT+SELECT to arv_app, SELECT to
         arv_read, NO UPDATE/DELETE), the kind CHECK by name, the
         composite source FK, the (id, revision) PK, the append-only
         trigger (ARV-JNL-006), the hostile INSERT with a phantom
         revision refuses ARV-JNL-007, the hostile INSERT binding an
         absent source refuses ARV-JNL-008; the frozen ack grammar on
         every ack and replay line

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no @-reference
resolution over journal blocks (beyond the landed note machine — its own
increment); no diagram/structured-block contract (the P4-C reservation —
its own round-trip proof required before "supported"); no reader-client
work (P4-B's repo); no tombstone/restore machine on the journal blocks
(the §3.3 increment — its own slice, the governed-erasure question
D-011's); no anchor-class location beyond the optional source binding
(the @-reference increment's surface).

Run: python3 harness/tests/test_journal.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import uuid as _uuid

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pg  # noqa: E402

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the two write commands, the
# three read arms, and the migration are each absent at the RED tree — the
# cheapest honest probe per surface.
_p = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                     "journal_block", "--help"], capture_output=True, text=True)
_absent_write = "invalid choice" in _p.stderr
_p2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                      "list-journal", "--owner", "A"],
                     capture_output=True, text=True, timeout=60)
_absent_list = "invalid choice" in _p2.stderr
_p3 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                      "get-journal", "--owner", "A", "--id", "x"],
                     capture_output=True, text=True, timeout=60)
_absent_get = "invalid choice" in _p3.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0016_*.sql"))
if _absent_write or _absent_list or _absent_get or not _mig:
    print(f"FAIL ARV-TEST-000: the P4-C slice three journal/blocks machinery is absent "
          f"(machinery-absent class; journal_block command absent: {_absent_write}; "
          f"list-journal arm absent: {_absent_list}; get-journal arm absent: "
          f"{_absent_get}; migration 0016 present: {bool(_mig)}) — the implementation "
          "lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None
# the corpus: the LONG raw thinking — multi-paragraph, the framing-law
# characters (pipes, newlines, U+2028, the CJK), and >8 KB so a truncating
# funnel could never pass the round-trip
PARA = ("The raw thinking paragraph that carries pipes | and newlines\n"
        "and the line separator \u2028 and the CJK 中文段落 and more text to fill.\n")
LONG_RAW = PARA * 70  # > 8 KB (the GREEN repair: the authored *60 gave 7,560 chars — below the suite's own >8192 self-check and the documented >8 KB intent; *70 gives 8,820, the truncating-funnel proof restored)
CREATIVE = ("The creative opening.\n\u2028The creative middle with pipes | inside.\n"
            "The creative close.\n")


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


def cmd(op: str, *args, owner="A", key=None, client="cli-1",
        crash_at=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client]
    if key is not None:
        a += ["--idem-key", key]
    if crash_at is not None:
        # THE HOUSE CRASH VOCABULARY (the NTE-06 pattern): the injection rides
        # harness/crash.py --point (exit 2 is crash.py's vocabulary)
        return cli(str(REPO / "harness" / "crash.py"), "--command", op,
                   "--point", crash_at, "--owner", owner, "--actor", "owner",
                   "--client-id", client, "--idem-key", key, *args)
    return cli(*a, *args)


def jblock(kind: str, key: str, content: str = None, file: str = None,
           source: str = None, owner="A") -> subprocess.CompletedProcess:
    a = ["--kind", kind]
    if content is not None:
        a += ["--content", content]
    if file is not None:
        a += ["--file", file]
    if source is not None:
        a += ["--source-id", source]
    return cmd("journal_block", *a, key=key, owner=owner)


def jrevise(block_id: str, key: str, content: str = None, file: str = None,
            owner="A", crash_at=None) -> subprocess.CompletedProcess:
    a = ["--id", block_id]
    if content is not None:
        a += ["--content", content]
    if file is not None:
        a += ["--file", file]
    return cmd("revise_journal_block", *a, key=key, owner=owner, crash_at=crash_at)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


def get_block(owner: str, block_id: str) -> subprocess.CompletedProcess:
    return query("get-journal", "--owner", owner, "--id", block_id)


def ref_of(r: subprocess.CompletedProcess) -> str:
    for ln in r.stdout.splitlines():
        if ln.startswith("ACK") and "result_ref=" in ln:
            return ln.split("result_ref=")[1].split()[0]
    return ""


def jline(r: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(next(ln for ln in r.stdout.splitlines() if ln.strip()))
    except Exception:
        return {}


def jlines(r: subprocess.CompletedProcess) -> list:
    return [json.loads(ln) for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def page(r: subprocess.CompletedProcess) -> "tuple[list, str, str]":
    lines = [ln for ln in r.stdout.split("\n") if ln != ""]
    if len(lines) < 2:
        return [], "", ""
    return lines[1:-1], lines[0], lines[-1]


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def audit_rows(sql: str) -> list:
    return [ln for ln in audit(sql).splitlines() if ln.strip()]


def super_sql(sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "postgres", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60, env=ENV)


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_app", "-d", DB,
                           "-c", f"SET app.current_owner='{owner}'; {sql}"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4c3")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4c3-"))

        # the fixtures: one source (the optional binding target) + B's own
        f1 = tmp / "reading.txt"
        f1.write_text("The source document for the optional binding.\n", encoding="utf-8")
        r_i1 = cmd("import_source", "--title", "The Binding Source",
                   "--file", str(f1), key="imp-1")
        src1 = ref_of(r_i1)
        extract_r = cli(str(REPO / "harness" / "extract.py"), "--owner", "A",
                        "--actor", "owner", "--client-id", "cli-1",
                        "--idem-key", "ext-1", "--source-id", src1)
        # the long raw thinking as a FILE (the long form's own channel)
        fraw = tmp / "raw.txt"
        fraw.write_text(LONG_RAW, encoding="utf-8")

        # ---- JNL-01 — the lossless round-trip
        r_j1 = jblock("raw", key="jnl-1", file=str(fraw))
        ack1 = next((ln for ln in r_j1.stdout.splitlines() if ln.startswith("ACK")), "")
        blk1 = ref_of(r_j1).split("@")[0] if ref_of(r_j1) else ""
        r_g1 = get_block("A", blk1)
        g1 = jline(r_g1)
        r_j2 = jblock("creative", key="jnl-2", content=CREATIVE)
        blk2 = ref_of(r_j2).split("@")[0] if ref_of(r_j2) else ""
        r_g2 = get_block("A", blk2)
        g2 = jline(r_g2)
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='journal_block';")
        content_text = "content" in cols
        need_cols = {"id", "revision", "kind", "content", "source_id", "owner_scope",
                     "actor", "run_id", "input_hash", "idempotency_key", "created_at"}
        ok1 = (r_i1.returncode == 0 and extract_r.returncode == 0
               and r_j1.returncode == 0
               and "status=committed" in ack1
               and f"result_ref={blk1}@1" in ack1
               and "durability_rung=local_durable" in ack1
               and "api_version=1" in ack1
               and r_g1.returncode == 0
               and g1.get("revision") == 1
               and g1.get("kind") == "raw"
               and g1.get("content") == LONG_RAW          # THE LOSSLESS LAW
               and g1.get("api_version") == 1
               and r_j2.returncode == 0
               and g2.get("kind") == "creative"
               and g2.get("content") == CREATIVE
               and content_text and need_cols <= set(cols)
               and len(LONG_RAW) > 8192)
        check("JNL-01", ok1,
              "the lossless round-trip: a LONG raw block (multi-paragraph, the framing-law "
              "characters — pipes, newlines, U+2028, the CJK — and >8 KB) written through the "
              "--file channel acks with the frozen grammar (status=committed + "
              "result_ref=<block>@1 + durability_rung=local_durable + api_version=1); a FRESH "
              "get-journal returns the content BYTE-IDENTICAL (the full long raw thinking, "
              "never truncated — the funneled form could never pass); the creative kind "
              "ditto; the row's column set carries content TEXT (no truncating length)",
              "harness/commands.py journal_block (the two content channels, the spine's own "
              "ack contract) + harness/query.py get-journal over migration 0016's "
              "journal_block rows — never a truncation, never a rewrite")

        # ---- JNL-02 — the kind vocabulary + the channel law + the typed refusals
        absent = str(_uuid.uuid4())
        r_k = jblock("summary", key="jnlx-1", content="x")     # out of vocabulary
        r_c1 = cmd("journal_block", "--kind", "raw", key="jnlx-2")  # neither channel
        r_c2 = jblock("raw", key="jnlx-3", content="x", file=str(fraw))  # both channels
        r_e = jblock("raw", key="jnlx-4", content="")          # the empty content
        r_abs = jrevise(absent, key="jnlx-5", content="x")     # the no-oracle (absent)
        r_xo = jrevise(blk1, key="jnlx-6", content="x", owner="B")  # cross-owner
        r_sb = jblock("raw", key="jnlx-7", content="x", source=absent)  # the bind (absent)
        r_sxo = jblock("raw", key="jnlx-8", content="x", source=src1, owner="B")  # cross-owner bind
        rows_before = audit("SELECT count(*) FROM arv.journal_block;")
        ok2 = (r_k.returncode == 1 and "FAIL ARV-JNL-002:" in r_k.stdout
               and r_c1.returncode == 1 and "FAIL ARV-JNL-003:" in r_c1.stdout
               and r_c2.returncode == 1 and "FAIL ARV-JNL-003:" in r_c2.stdout
               and r_e.returncode == 1 and "FAIL ARV-JNL-004:" in r_e.stdout
               and r_abs.returncode == 1 and "FAIL ARV-JNL-001:" in r_abs.stdout
               and r_xo.returncode == 1 and "FAIL ARV-JNL-001:" in r_xo.stdout
               and r_abs.stdout.replace(absent, "<id>") == r_xo.stdout.replace(blk1, "<id>")
               and r_sb.returncode == 1 and "FAIL ARV-JNL-005:" in r_sb.stdout
               and r_sxo.returncode == 1 and "FAIL ARV-JNL-005:" in r_sxo.stdout
               and r_sb.stdout.replace(absent, "<id>") == r_sxo.stdout.replace(src1, "<id>")
               and rows_before == "2")  # only jnl-1 + jnl-2 landed; every refusal zero-effect
        check("JNL-02", ok2,
              "the closed kind vocabulary + the channel law + the typed refusals: an "
              "out-of-vocabulary kind refuses ARV-JNL-002 (named, zero effect — never "
              "clamped); neither/both content channels refuse ARV-JNL-003 (the NTE-010 "
              "channel-law class); the empty content refuses ARV-JNL-004; the "
              "absent/cross-owner block on the revise path is the SAME refusal ARV-JNL-001 "
              "(the no-oracle — byte-equal after the id normalize); the absent/cross-owner "
              "source at the bind refuses ARV-JNL-005 (the no-oracle at the binding); "
              "every refusal leaves ZERO rows",
              "the typed refusals in commands.py journal_block/revise_journal_block + "
              "migration 0016's named kind CHECK (the 0015 D-010 pattern: the boundary "
              "structural below the command)")

        # ---- JNL-03 — the source-OPTIONAL law + the no-forced-funnel law
        notes_before = audit("SELECT count(*) FROM arv.note;")
        r_j3 = jblock("raw", key="jnl-3", content="A sourceless block is a first-class row.\n")
        blk3 = ref_of(r_j3).split("@")[0] if ref_of(r_j3) else ""
        r_j4 = jblock("raw", key="jnl-4", content="A bound block.\n", source=src1)
        blk4 = ref_of(r_j4).split("@")[0] if ref_of(r_j4) else ""
        g3 = jline(get_block("A", blk3))
        g4 = jline(get_block("A", blk4))
        notes_after = audit("SELECT count(*) FROM arv.note;")
        # the note machine's own surface still works, its rows stay its own
        r_n = cmd("create_note", "--content", "A note of its own surface.\n", key="nte-1")
        note_id = ref_of(r_n)
        notes_final = audit("SELECT count(*) FROM arv.note;")
        jnl_rows = audit("SELECT count(*) FROM arv.journal_block;")
        ok3 = (r_j3.returncode == 0 and r_j4.returncode == 0
               and g3.get("source_id") is None      # THE SOURCE-OPTIONAL LAW
               and g3.get("content") == "A sourceless block is a first-class row.\n"
               and g4.get("source_id") == src1      # the binding when the author says so
               and notes_before == "0"
               and notes_after == "0"               # THE NO-FORCED-FUNNEL LAW (zero notes)
               and r_n.returncode == 0 and note_id != ""
               and notes_final == "1"               # the note machine works, its rows its own
               and jnl_rows == "4")
        check("JNL-03", ok3,
              "the source-OPTIONAL law + the no-forced-funnel law: a sourceless block is a "
              "FIRST-CLASS row (acks, reads — never a forced binding, source_id null in the "
              "answer); a source-bound block carries the binding in the read answer; a "
              "journal write leaves arv.note's row-count UNCHANGED (the note machine never "
              "invoked — no silent conversion either way); the note machine's own surface "
              "still works (create_note acks, its rows stay its own)",
              "the optional source binding on the block row (the composite FK with the "
              "NULL-when-unbound form) + the journal write path never touching arv.note — "
              "the two surfaces separate by construction")

        # ---- JNL-04 — the revision machine + the governed history + the spine's contract
        r_rep = jblock("raw", key="jnl-1", file=str(fraw))       # same key+body -> replayed
        ack_rep = next((ln for ln in r_rep.stdout.splitlines() if ln.startswith("ACK")), "")
        r_409 = jblock("raw", key="jnl-1", content="different body")  # same key, different body
        fraw2 = tmp / "raw2.txt"
        fraw2.write_text("The revised long thinking, still lossless \u2028 with pipes |.\n" * 40,
                         encoding="utf-8")
        r_rev = jrevise(blk1, key="jnl-5", file=str(fraw2))
        ack_rev = next((ln for ln in r_rev.stdout.splitlines() if ln.startswith("ACK")), "")
        g_after = jline(get_block("A", blk1))
        r_hist = query("get-journal-history", "--owner", "A", "--id", blk1)
        hrows = jlines(r_hist)
        # the lost-ack arm: post-commit-pre-ack exits 2, the effect committed, the replay converges
        r_cr = jrevise(blk1, key="jnl-6", content="The crash-armed revision body.\n",
                       crash_at="post-commit-pre-ack")
        g_crash = jline(get_block("A", blk1))
        r_conv = jrevise(blk1, key="jnl-6", content="The crash-armed revision body.\n")
        ack_conv = next((ln for ln in r_conv.stdout.splitlines() if ln.startswith("ACK")), "")
        revs = audit_rows("SELECT revision FROM arv.journal_block WHERE id = '" + blk1 +
                          "' ORDER BY revision;")
        ok4 = (r_rep.returncode == 0 and "status=replayed" in ack_rep
               and f"result_ref={blk1}@1" in ack_rep and "api_version=1" in ack_rep
               and r_409.returncode == 1 and "FAIL ARV-CMD-409:" in r_409.stdout
               and r_rev.returncode == 0 and f"result_ref={blk1}@2" in ack_rev
               and "revision=2" in ack_rev
               and g_after.get("revision") == 2
               and g_after.get("content") == fraw2.read_text(encoding="utf-8")
               and r_hist.returncode == 0
               and [h.get("revision") for h in hrows] == [1, 2]     # EVERY revision, in order
               and all(h.get("api_version") == 1 for h in hrows)
               and revs == ["1", "2", "3"]                              # every revision row on the substrate, in order (the GREEN repair: the audit sits AFTER the crash arm, so the honest pin includes the crash-committed third — no skips, no phantoms; the authored ["1","2"] named the pre-crash state and was unsatisfiable at this position alongside g_crash revision=3)
               and r_cr.returncode == 2                              # crash.py's vocabulary
               and g_crash.get("revision") == 3                      # the effect committed
               and r_conv.returncode == 0 and "status=replayed" in ack_conv
               and f"result_ref={blk1}@3" in ack_conv
               and int(audit("SELECT count(*) FROM arv.outbox WHERE command_name IN "
                            "('journal_block', 'revise_journal_block');")) == 6)  # the ENQUEUE pin, the delivery-carrying form (CLAIM-073's re-home LANDED — the SUPERSESSION of the split tree's ZERO-outbox-row form, the amendment typed and disclosed): every committed journal write rides the client outbox in the SAME transaction — jnl-1/jnl-2 the JNL-01 creates + jnl-3/jnl-4 the JNL-03 creates + jnl-5 the revise + jnl-6 the crash-committed revise; the refusals (jnlx-*: the vocabulary/channel/no-oracle/cross-owner classes) and the replays (jnl-1 replay, jnl-6 converge) add NONE — the spine's own atomic law
        check("JNL-04", ok4,
              "the revision machine + the governed history + the spine's whole contract: the "
              "revise command appends revision 2 (a NEW row; revision 1 intact on the "
              "substrate); the current read returns revision 2's content byte-honest; the "
              "history returns EVERY revision in order (the export-ready form); the "
              "idempotency (same key+body -> replayed, the same result_ref; same "
              "key+different body -> ARV-CMD-409, zero effect); the ENQUEUE pin "
              "(the delivery-carrying form — CLAIM-073's re-home LANDED, the supersession of "
              "the split tree's ZERO-outbox-row form: every committed journal write carries "
              "its outbox row in the SAME transaction, the refusals and replays adding none — "
              "the family rides the client outbox like every landed family, the writing lab's "
              "no-lost-writes law); the crash matrix's lost-ack arm (post-commit-pre-ack "
              "exits 2, the effect committed, the same-key replay converges the ack)",
              "revise_journal_block through the spine's own idempotency + the crash.py "
              "injection — the journal inherits the command path's whole contract; the "
              "outbox ride landed with CLAIM-073 (the re-home's own account, the LAW-05 "
              "split's named landing)")

        # ---- JNL-05 — the read arms' list contract + the owner isolation
        r_l0 = query("list-journal", "--owner", "A", "--limit", "0")
        r_l1001 = query("list-journal", "--owner", "A", "--limit", "1001")
        r_labc = query("list-journal", "--owner", "A", "--limit", "abc")
        r_full = query("list-journal", "--owner", "A")
        body, hdr, marker = page(r_full)
        ids_full = body
        # the keyset walk at --limit 2
        rows, markers, after = [], [], None
        while True:
            r = query("list-journal", "--owner", "A", "--limit", "2", *(["--after", after] if after else []))
            b, h, m = page(r)
            if r.returncode != 0:
                rows, markers = [], []
                break
            rows.extend(b)
            markers.append(m)
            if m != "# more=true" or not b:
                break
            after = b[-1]
        # B's isolation + the no-oracle on the read
        fb = tmp / "braw.txt"
        fb.write_text("B's own journal block.\n", encoding="utf-8")
        r_b = jblock("raw", key="bjnl-1", file=str(fb), owner="B")
        bblk = ref_of(r_b).split("@")[0] if ref_of(r_b) else ""
        r_bl = query("list-journal", "--owner", "B")
        bbody, bhdr, bmarker = page(r_bl)
        r_ga = get_block("A", absent)
        r_gb = get_block("B", blk1)   # A's block read as B
        r_gbabs = get_block("B", absent)
        # C's empty journal: header + marker ALONE
        r_c = query("list-journal", "--owner", "C")
        c_lines = [ln for ln in r_c.stdout.split("\n") if ln != ""]
        ok5 = (r_l0.returncode == 1 and "FAIL ARV-QRY-004:" in r_l0.stdout
               and r_l1001.returncode == 1 and "FAIL ARV-QRY-004:" in r_l1001.stdout
               and r_labc.returncode == 1 and "FAIL ARV-QRY-004:" in r_labc.stdout
               and r_full.returncode == 0
               and hdr == "# api_version=1" and marker == "# more=false"
               and sorted(ids_full) == sorted([blk1, blk2, blk3, blk4])
               and rows == sorted([blk1, blk2, blk3, blk4])   # the walk's union, in order
               and markers[0] == "# more=true" and markers[-1] == "# more=false"
               and all(m == "# more=true" for m in markers[:-1])
               and r_b.returncode == 0
               and r_bl.returncode == 0
               and bbody == [bblk]
               and not (set([blk1, blk2, blk3, blk4]) & set(bbody))
               and r_ga.returncode == 1 and "FAIL ARV-QRY-001:" in r_ga.stdout
               and r_gb.returncode == 1 and "FAIL ARV-QRY-001:" in r_gb.stdout
               and r_ga.stdout == r_gb.stdout
               and r_gb.stdout.replace(blk1, "<id>") == r_gbabs.stdout.replace(absent, "<id>")
               and r_c.returncode == 0
               and c_lines == ["# api_version=1", "# more=false"])
        check("JNL-05", ok5,
              "the read arms' list contract + the owner isolation: list-journal "
              "bounded/paginated (the ARV-QRY-004 bounds refusals — 0/1001/not-an-integer; "
              "the keyset walk at --limit 2 with the union exact, no dups, the markers "
              "observed; the version header; the empty journal's two-line answer — never "
              "pure silence); every JSON row carries api_version=1; owner B sees only B's "
              "blocks; get-journal on absent vs cross-owner is the byte-equal ARV-QRY-001 "
              "refusal (the no-oracle)",
              "the shared _list_arm/_page_args machinery on the journal listing + the shared "
              "_refuse form on the block read — the read boundary the whole surface rides")

        # ---- JNL-06 — the reserved surface + the 0016 substrate conventions
        r_sur = cap("surfaces")
        srows = jlines(r_sur)
        jrow = next((row for row in srows if row.get("surface") == "journal/blocks"), {})
        defaults = audit("SELECT count(*) FROM information_schema.columns "
                         "WHERE table_schema='arv' AND table_name='journal_block' "
                         "AND column_default IS NOT NULL;")
        rls = audit("SELECT relrowsecurity AND relforcerowsecurity FROM pg_class "
                    "WHERE oid = 'arv.journal_block'::regclass;")
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname='arv' "
                    "AND tablename='journal_block' AND policyname='owner_isolation' "
                    "AND roles::text = '{arv_app}';")
        grants = audit("SELECT has_table_privilege('arv_app','arv.journal_block','INSERT') "
                       "|| '|' || has_table_privilege('arv_app','arv.journal_block','UPDATE') "
                       "|| '|' || has_table_privilege('arv_app','arv.journal_block','DELETE') "
                       "|| '|' || has_table_privilege('arv_read','arv.journal_block','SELECT');")
        kindchk = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                        "'arv.journal_block'::regclass AND contype = 'c' "
                        "AND pg_get_constraintdef(oid) LIKE '%kind%' "
                        "AND pg_get_constraintdef(oid) LIKE '%raw%' "
                        "AND pg_get_constraintdef(oid) LIKE '%creative%';")
        fk = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                   "'arv.journal_block'::regclass AND contype = 'f' "
                   "AND pg_get_constraintdef(oid) LIKE '%arv.source%';")
        pk = audit("SELECT count(*) FROM pg_constraint WHERE conrelid = "
                   "'arv.journal_block'::regclass AND contype = 'p' "
                   "AND pg_get_constraintdef(oid) = 'PRIMARY KEY (id, revision)';")
        g_upd = super_sql("UPDATE arv.journal_block SET content = 'x';")
        g_ins = app_sql(f"INSERT INTO arv.journal_block (id, revision, kind, content, "
                        f"source_id, owner_scope, actor, run_id, input_hash, idempotency_key, "
                        f"created_at) VALUES ('{_uuid.uuid4()}', 9, 'raw', 'hostile', NULL, "
                        f"'A', 'owner', 'run-hostile', 'deadbeef', 'hostile-1', now());")
        g_bind = app_sql(f"INSERT INTO arv.journal_block (id, revision, kind, content, "
                         f"source_id, owner_scope, actor, run_id, input_hash, idempotency_key, "
                         f"created_at) VALUES ('{_uuid.uuid4()}', 4, 'raw', 'hostile', "
                         f"'{_uuid.uuid4()}', 'A', 'owner', 'run-hostile', 'deadbeef', "
                         f"'hostile-2', now());")
        ok6 = (r_sur.returncode == 0
               and all(row.get("api_version") == 1 for row in srows)
               and jrow.get("owner_phase") == "P4-C"
               and "journal_block" in str(jrow.get("reservation", ""))
               and "list-journal" in str(jrow.get("reservation", ""))
               and "P4-B" in str(jrow.get("reservation", ""))
               and defaults == "0"
               and rls == "t" and pol == "1"
               and grants == "true|false|false|true"
               and kindchk == "1" and fk == "1" and pk == "1"
               and "ARV-JNL-006" in g_upd.stderr
               and "ARV-JNL-007" in g_ins.stderr
               and "ARV-JNL-008" in g_bind.stderr
               and "api_version=1" in ack1 and "api_version=1" in ack_rev)
        check("JNL-06", ok6,
              "the reserved surface + the 0016 substrate conventions: capability.py's "
              "journal/blocks row (owner_phase P4-C, the LANDED verbs named — journal_block/"
              "revise_journal_block/list-journal/get-journal — the reader-client exclusion "
              "held); the schema audited — NO DEFAULTs (LAW-24), RLS enabled AND FORCED + the "
              "owner_isolation policy on arv_app, the grants (INSERT+SELECT to arv_app, "
              "SELECT to arv_read, NO UPDATE/DELETE), the kind CHECK by name (raw|creative), "
              "the composite source FK, the (id, revision) PK, the append-only trigger "
              "(ARV-JNL-006 on UPDATE/DELETE), the hostile INSERT with a phantom revision "
              "refuses ARV-JNL-007, the hostile INSERT binding an absent source refuses "
              "ARV-JNL-008; the frozen ack grammar on every ack and replay line",
              "harness/capability.py's RESERVED_SURFACES row + migration 0016's conventions "
              "(the 0014/0015 substrate pattern: the named kind CHECK, the guards, RLS, the "
              "grants)")

        if FAILS:
            print(f"\nJOURNAL SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the journal/blocks contract is broken or unimplemented)")
            return 1
        print("\nJOURNAL SUITE GREEN — JNL-01..06 (the journal/blocks surface: the writing "
              "lab — the lossless long raw thinking, the closed kind vocabulary, the "
              "source-optional law, the no-forced-funnel boundary, the governed revisions)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
