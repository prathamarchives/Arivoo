#!/usr/bin/env python3
"""harness/tests/test_references.py — P4-D slice one acceptance suite (CLAIM-075,
the stable @-reference system — the RTM §2 item 10 reservation landing; PLAN's 4D
row elaborated one phase deep at the P4-C exit; record 67 §2). Red-first (LAW-11):
at CLAIM-074's merged head 4a750db the suite fails with ARV-TEST-000
(machinery-absent; red-01.txt).

THE CONTRACT: the reference RESOLUTION surface — ONE typed read arm over the
seven landed entity families (Work, Source, Anchor, Highlight, Bookmark, Note,
Journal block), composing the CLAIM-057 note-reference substrate (the same
'kind:id[@rev]' grammar, the same uuid law, the same per-family revision
dimension), never a second implementation. The LOGICAL TARGET IDENTITY is
separated from the SELECTED HISTORICAL REVISION (the answer carries the id —
the stable uuid identity — and the revision information as separate fields;
titles/labels/content change without breaking references: the identity is the
uuid, and a pinned revision serves exactly as pinned while an unpinned
reference tracks the current revision).

THE GRAMMAR: kind:id for the bare families (work, source, anchor — no revision
dimension; a supplied @rev is malformed, exactly the substrate's law); kind:id
and kind:id@rev for the revisioned families (highlight, bookmark, note,
journal_block — the pin optional at the resolution boundary: unpinned asks
'where is the current?', pinned asks 'exactly as pinned, never a retarget');
the revision is digits >= 1.

THE SIX EXPLICIT STATES (the typed resolution, never a guess — exclusive,
observable, fail-closed; every answer carries exactly one):
  current      the target live and the resolution serving the current state —
               the unpinned reference resolving to the current revision (or a
               pin at the current revision; the bare families' identity read);
               for anchors the composed anchor-resolution verdict 'resolved'
               (the answer carries the serving generation_id — the compose
               proof)
  historical   a pinned revision resolving exactly as pinned — superseded but
               retained (the append-only substrate guarantees retention): the
               answer serves the PINNED revision's address and names the
               current revision alongside — never a silent retarget
  tombstoned   the target lifecycle-tombstoned (highlight/bookmark/note): the
               reference answers the tombstone state — for unpinned AND pinned
               forms alike (a pin never bypasses a tombstone) — and serves NO
               revision and NO content ('without leaking deleted private
               content'); restore returns the reference to current
  unavailable  the target absent from the current view: the anchor-resolution
               class — the anchor row live but its location view not servable
               (the composed verdict 'unresolved' with its named cause:
               no-current-generation, stale-generation, location-unmatched)
  ambiguous    the anchor-resolution class — the composed verdict 'ambiguous'
               (the fallback evidence locates the pattern at TWO OR MORE
               positions; the answer carries the hit count)
  purged       the governed purge invalidated the access: a purge-ledger row
               (owner, kind, entity_id) — the 0013 permanence record — WINS
               over every other state (a purged tombstoned target answers
               purged); the pin never bypasses it either

Refusal codes (exit 1, the frozen shape):
  ARV-REF-001  the dangling reference — the absent id, another owner's id, and
               a nonexistent target revision on a live target are the SAME
               refusal, byte-equal whatever was asked (the no-oracle; the
               substrate's ARV-NTE-003 law at the resolution boundary)
  ARV-REF-002  the malformed reference — unknown kind, non-uuid id, revision
               grammar violations (a revision on a bare family; non-digit /
               zero revisions), the hostile and oversized strings: refused,
               never clamped, never guessed (a reference string is DATA,
               never an instruction — imported hostile strings never acquire
               authority by being read)

Cases (the REF registry; each pin's full statement lives at its check()):
  REF-01 the resolution round-trip + the identity/revision separation: all
         SEVEN kinds resolve current with the frozen answer shape (ONE JSON
         line; api_version=1; kind; id — the logical identity echoed exact;
         state; resolved_ref — the address a client fetches); the revisioned
         families carry the CURRENT revision when unpinned; the bare families
         carry no revision field; the anchor's current answer carries the
         serving generation_id (the P3-03b compose); capability.py's
         references reserved-surface row names the landed arm
  REF-02 the version pinning + the historical state: a pin at a superseded
         revision answers historical — the pinned revision served exactly as
         pinned (resolved_ref = the pinned form), the current revision named
         alongside — never a silent retarget; a pin at the current revision
         answers current; the unpinned and pinned forms of the SAME target
         differ exactly by the selected revision (the separation); the note
         machine's own stored reference (get-note's refs) resolves through
         the ONE surface — the compose, never a second implementation; the
         content changes (two revisions) never break the reference (the
         identity is the uuid)
  REF-03 the tombstoned state: highlight/bookmark/note tombstoned answer
         tombstoned for BOTH the unpinned and the pinned forms (a pin never
         bypasses a tombstone); the answer carries NO revision and NO
         resolved_ref and NO content (the tombstone is the answer — deleted
         private content never leaks through a reference); restore returns
         the reference to current
  REF-04 the unavailable + ambiguous states (the anchor-resolution compose):
         an anchor over a never-extracted source answers unavailable with the
         named cause (no-current-generation); the drifted-tiling anchor over
         repeated content answers ambiguous with evidence_hits >= 2; the
         same fixture family's resolved anchor answers current with the
         serving generation_id; the unavailable/ambiguous answers carry NO
         resolved_ref (nothing was resolved — the honest answer, never a
         nearest-match retarget)
  REF-05 the purged state + the precedence + the ledger's closed vocabulary:
         a purge-ledger row makes the reference answer purged (unpinned AND
         pinned — the governed purge invalidates the access); purged WINS
         over tombstoned (the precedence: the permanence record is the
         stronger invalidation); the purged answer carries NO revision and
         NO resolved_ref; the 0013 ledger's kind CHECK refuses a
         journal_block row (the closed vocabulary — the substrate pin, never
         a second vocabulary)
  REF-06 the typed refusals + the no-oracle + the hostile-string law + the
         state machine's laws: for EVERY family the absent id and another
         owner's id are the SAME ARV-REF-001 refusal (template-normalized
         byte-equal — never an existence side channel); a nonexistent target
         revision on a live target is the SAME class; the malformed forms
         (unknown kind, non-uuid, a revision on a bare family, @0, @x, the
         SQL-metacharacter string, the 10k oversize string) refuse ARV-REF-002;
         every refusal is exit 1 with ZERO answer lines; the read never
         writes (the command_log row count unchanged across the probes); the
         observed states across the whole suite are EXACTLY the closed six

Run: python3 harness/tests/test_references.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): the resolution arm is absent at
# the RED tree — the cheapest honest probe for the one new surface.
_p = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                     "resolve-reference", "--owner", "A",
                     "--ref", "note:00000000-0000-0000-0000-000000000000"],
                    capture_output=True, text=True, timeout=60)
_absent_arm = "invalid choice" in _p.stderr
if _absent_arm:
    print(f"FAIL ARV-TEST-000: the P4-D slice one reference-resolution machinery "
          f"is absent (machinery-absent class; the resolve-reference arm absent: "
          f"{_absent_arm}) — the implementation lands after this RED, never "
          "before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

DB = ENV = None

ABSENT = "00000000-0000-0000-0000-000000000000"
KINDS_BARE = ("work", "source", "anchor")
KINDS_REV = ("highlight", "bookmark", "note", "journal_block")
SIX = ("current", "historical", "tombstoned", "unavailable", "ambiguous", "purged")
OBSERVED: list = []          # every (state) the suite observes — REF-06's law


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


def cmd(op: str, *args, owner="A", key=None, client="cli-1") -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client, "--idem-key", key]
    return cli(*a, *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


def res(ref: str, owner="A") -> subprocess.CompletedProcess:
    return query("resolve-reference", "--owner", owner, "--ref", ref)


def extract(key: str, source_id: str, owner="A") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor",
               "owner", "--client-id", "cli-1", "--idem-key", key,
               "--source-id", source_id)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if ln.startswith("ACK") and field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def typed(p: subprocess.CompletedProcess):
    """The typed answer: ONE JSON line on stdout, exit 0."""
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    if p.returncode != 0 or len(lines) != 1:
        return None
    try:
        d = json.loads(lines[0])
    except json.JSONDecodeError:
        return None
    if isinstance(d, dict) and d.get("state") in SIX:
        OBSERVED.append(d["state"])
    return d


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def plant(sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
                           "-U", "postgres", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60, env=ENV)


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_app", "-d", DB,
                           "-c", f"SET app.current_owner='{owner}'; {sql}"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def fresh_file(name: str, text: str) -> str:
    d = tempfile.mkdtemp(prefix="arv-ref-")
    f = pathlib.Path(d) / name
    f.write_text(text, encoding="utf-8")
    return str(f)


def import_src(key: str, title: str, file: str, owner="A") -> subprocess.CompletedProcess:
    return cmd("import_source", "--title", title, "--file", file, key=key, owner=owner)


def highlight(key: str, source_id: str, start: int, end: int, owner="A"):
    p = cmd("create_highlight", "--source-id", source_id, "--start", str(start),
            "--end", str(end), key=key, owner=owner)
    hid = ack_field(p, "result_ref")
    return p, hid


def purge_row(kind: str, entity_id: str, owner="A") -> subprocess.CompletedProcess:
    """A governed-purge ledger entry through the 0013 INSERT grant (arv_app,
    the owner's own scope — the designed writer surface; the COMMAND is
    D-011's later slice, the LEDGER is this surface's read substrate)."""
    return app_sql(
        f"INSERT INTO arv.purge_ledger (owner_scope, kind, entity_id, reason, "
        f"actor, created_at) VALUES ('{owner}', '{kind}', '{entity_id}', "
        f"'the reference-slice probe purge', 'owner', now());", owner=owner)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4d1")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4d1-"))

        # ---------------- the fixtures ----------------
        # A's main source (extracted — the resolved-anchor substrate)
        TEXT1 = ("# The Reference Essay\n\n"
                 "The opening paragraph sets the frame.\n\n"
                 "The middle paragraph carries the marked passage.\n\n"
                 "The closing paragraph completes it.\n")
        src1 = ack_field(import_src("ref-src-1", "The Reference Essay",
                                    fresh_file("essay.md", TEXT1)), "result_ref")
        extract("ref-ext-1", src1)
        gs = json.loads(next(ln for ln in query("get-source", "--owner", "A",
                                                "--id", src1).stdout.splitlines()
                             if ln.strip()))
        work1 = gs["work_id"]

        # hl1: revisions 1..3 (create + revise x2); its anchor resolves
        _, hl1 = highlight("ref-hl-1", src1, 66, 86)
        cmd("revise_highlight", "--id", hl1, "--start", "67", "--end", "87",
            key="ref-hl-2")
        cmd("revise_highlight", "--id", hl1, "--start", "68", "--end", "88",
            key="ref-hl-3")
        anc1 = audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{hl1}';")
        gen1 = audit(f"SELECT id FROM arv.extraction_generation WHERE "
                     f"source_id='{src1}' AND state='current';")

        # the tombstone fixtures (all three tombstone families)
        _, hl_t = highlight("ref-hlt-1", src1, 10, 30)
        cmd("tombstone_highlight", "--id", hl_t, key="ref-hlt-2")
        bm_t = ack_field(cmd("create_bookmark", "--source-id", src1,
                             "--start", "23", "--end", "43", key="ref-bmt-1"),
                         "result_ref")
        cmd("tombstone_bookmark", "--id", bm_t, key="ref-bmt-2")

        # bm1: the bookmark, moved once — revisions 1..2
        bm1 = ack_field(cmd("create_bookmark", "--source-id", src1, "--start",
                            "62", "--end", "82", key="ref-bm-1"), "result_ref")
        cmd("move_bookmark", "--id", bm1, "--start", "63", "--end", "83",
            key="ref-bm-2")

        # note1: revisions 1..3, EVERY revision CARRYING the substrate
        # reference highlight:<hl1>@1 (the note machine's own --ref law — the
        # refs attach PER REVISION, so each revise restates the pin; the
        # compose probe then reads the CURRENT revision's stored ref)
        n1 = ack_field(cmd("create_note", "--content", "The first note body.",
                           "--ref", f"highlight:{hl1}@1", key="ref-n-1"),
                       "result_ref")
        cmd("revise_note", "--id", n1, "--content", "The second body.",
            "--ref", f"highlight:{hl1}@1", key="ref-n-2")
        cmd("revise_note", "--id", n1, "--content", "The third body.",
            "--ref", f"highlight:{hl1}@1", key="ref-n-3")

        # note_tomb: created, then tombstoned (rev 1 only)
        nt = ack_field(cmd("create_note", "--content", "The tombstone note body.",
                           key="ref-nt-1"), "result_ref")
        cmd("tombstone_note", "--id", nt, key="ref-nt-2")

        # note_purge: live, plus the ledger row
        np_ = ack_field(cmd("create_note", "--content", "The purged note body.",
                            key="ref-np-1"), "result_ref")
        purge_row("note", np_)

        # hl_pt: tombstoned AND purged — the precedence fixture
        _, hpt = highlight("ref-hpt-1", src1, 5, 15)
        cmd("tombstone_highlight", "--id", hpt, key="ref-hpt-2")
        purge_row("highlight", hpt)

        # jb1: the journal block, revised once — revisions 1..2
        jb1 = ack_field(cmd("journal_block", "--kind", "raw", "--content",
                            "The first raw thinking.", key="ref-jb-1"),
                        "result_ref").split("@")[0]
        cmd("revise_journal_block", "--id", jb1, "--content",
            "The revised thinking.", key="ref-jb-2")

        # src2: imported, NEVER extracted — the unavailable anchor
        src2 = ack_field(import_src("ref-src-2", "The Unextracted Essay",
                                    fresh_file("unex.md",
                                               "The unextracted source text stands alone.\n")),
                         "result_ref")
        _, _hne = highlight("ref-hne-1", src2, 4, 20)
        anc_ne = audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{_hne}';")

        # src3: repeated content + the planted drifted tiling — the
        # ambiguous anchor (the ANC-05 fixture class, replicated exactly)
        B = "alpha\n\nbeta gamma delta\n\n"
        S5 = B + B + B + B + "omega closing text.\n"
        src3 = ack_field(import_src("ref-src-3", "The Ambiguous Essay",
                                    fresh_file("ambig.md", S5)), "result_ref")
        extract("ref-ext-3", src3)
        _, _hamb = highlight("ref-hamb-1", src3, 7, 17)
        anc_amb = audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{_hamb}';")
        gen3 = audit(f"SELECT id FROM arv.extraction_generation WHERE "
                     f"source_id='{src3}' AND state='current';")
        pl1 = plant(f"UPDATE arv.extraction_generation SET state='superseded' "
                    f"WHERE id='{gen3}'; "
                    f"INSERT INTO arv.extraction_generation (id, source_id, ordinal, "
                    f"state, extractor, extractor_config, input_digest, "
                    f"idempotency_key, body_hash, owner_scope, actor, run_id, "
                    f"input_hash, created_at, updated_at) "
                    f"SELECT gen_random_uuid(), '{src3}', 2, 'current', extractor, "
                    f"extractor_config, input_digest, 'drifted-tiling-ref', body_hash, "
                    f"owner_scope, actor, run_id, input_hash, now(), now() "
                    f"FROM arv.extraction_generation WHERE id='{gen3}';")
        gen3b = audit(f"SELECT id FROM arv.extraction_generation WHERE "
                      f"source_id='{src3}' AND state='current';")
        d3a = hashlib.sha256(S5[0:7].encode()).hexdigest()
        d3b = hashlib.sha256(S5[17:].encode()).hexdigest()
        pl2 = plant(f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, "
                    f"end_off, text, digest, owner_scope, actor, run_id, input_hash, "
                    f"created_at) SELECT gen_random_uuid(), '{gen3b}', 1, 0, 7, "
                    f"'{S5[0:7]}', '{d3a}', owner_scope, actor, run_id, input_hash, "
                    f"now() FROM arv.extraction_generation WHERE id='{gen3b}'; "
                    f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, "
                    f"end_off, text, digest, owner_scope, actor, run_id, input_hash, "
                    f"created_at) SELECT gen_random_uuid(), '{gen3b}', 2, 17, "
                    f"{len(S5)}, '{S5[17:]}', '{d3b}', owner_scope, actor, run_id, "
                    f"input_hash, now() FROM arv.extraction_generation "
                    f"WHERE id='{gen3b}';")

        # B's fixtures — the cross-owner probes (one per family)
        b_src = ack_field(import_src("ref-bsrc", "B's Source",
                                     fresh_file("bsrc.md",
                                                "B's own source document.\n"),
                                     owner="B"), "result_ref")
        b_gs = json.loads(next(ln for ln in query("get-source", "--owner", "B",
                                                  "--id", b_src).stdout.splitlines()
                               if ln.strip()))
        _, b_hl = highlight("ref-bhl", b_src, 3, 13, owner="B")
        b_anc = audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{b_hl}';")
        b_bm = ack_field(cmd("create_bookmark", "--source-id", b_src, "--start",
                             "0", "--end", "10", key="ref-bbm", owner="B"),
                         "result_ref")
        b_note = ack_field(cmd("create_note", "--content", "B's own note.",
                               key="ref-bn", owner="B"), "result_ref")
        b_jb = ack_field(cmd("journal_block", "--kind", "creative", "--content",
                             "B's own creative block.", key="ref-bjb", owner="B"),
                         "result_ref").split("@")[0]

        # ---- REF-01 — the round-trip + the identity/revision separation
        r_w = typed(res(f"work:{work1}"))
        r_s = typed(res(f"source:{src1}"))
        r_a = typed(res(f"anchor:{anc1}"))
        r_h = typed(res(f"highlight:{hl1}"))
        r_b = typed(res(f"bookmark:{bm1}"))
        r_n = typed(res(f"note:{n1}"))
        r_j = typed(res(f"journal_block:{jb1}"))
        cap_row = cap("surfaces")
        ok1 = (r_w and r_w.get("state") == "current"
               and r_w.get("kind") == "work" and r_w.get("id") == work1
               and r_w.get("resolved_ref") == f"work:{work1}"
               and r_w.get("api_version") == 1 and "revision" not in r_w
               and r_s and r_s.get("state") == "current"
               and r_s.get("kind") == "source" and r_s.get("id") == src1
               and r_s.get("resolved_ref") == f"source:{src1}"
               and "revision" not in r_s
               and r_a and r_a.get("state") == "current"
               and r_a.get("kind") == "anchor" and r_a.get("id") == anc1
               and r_a.get("resolved_ref") == f"anchor:{anc1}"
               and r_a.get("generation_id") == gen1 and "revision" not in r_a
               and r_h and r_h.get("state") == "current"
               and r_h.get("kind") == "highlight" and r_h.get("id") == hl1
               and r_h.get("revision") == 3
               and r_h.get("resolved_ref") == f"highlight:{hl1}@3"
               and r_b and r_b.get("state") == "current"
               and r_b.get("kind") == "bookmark" and r_b.get("id") == bm1
               and r_b.get("revision") == 2
               and r_b.get("resolved_ref") == f"bookmark:{bm1}@2"
               and r_n and r_n.get("state") == "current"
               and r_n.get("kind") == "note" and r_n.get("id") == n1
               and r_n.get("revision") == 3
               and r_n.get("resolved_ref") == f"note:{n1}@3"
               and r_j and r_j.get("state") == "current"
               and r_j.get("kind") == "journal_block" and r_j.get("id") == jb1
               and r_j.get("revision") == 2
               and r_j.get("resolved_ref") == f"journal_block:{jb1}@2"
               and '"references"' in cap_row.stdout
               and "resolve-reference" in cap_row.stdout)
        check("REF-01", ok1,
              "the resolution round-trip over ALL SEVEN families: every live target "
              "answers current with the frozen shape (ONE JSON line, api_version=1, "
              "kind, id — the LOGICAL IDENTITY echoed exact, state, resolved_ref — "
              "the fetch address); the revisioned families carry the CURRENT revision "
              "when unpinned (highlight@3, bookmark@2, note@3, journal_block@2 — the "
              "derived max); the bare families (work/source/anchor) carry NO revision "
              "field (the identity/revision separation structural); the anchor's "
              "current answer carries the serving generation_id (the P3-03b compose "
              "proof); capability.py's references row names the landed arm",
              "query.py resolve-reference: the typed read arm over the seven landed "
              "families composing the per-family row reads (the CLAIM-057 substrate's "
              "own checks), the revision derived per family, the anchor verdict "
              "composed — never a second implementation")

        # ---- REF-02 — the version pinning + the historical state
        p_h1 = typed(res(f"highlight:{hl1}@1"))
        p_h3 = typed(res(f"highlight:{hl1}@3"))
        p_n1 = typed(res(f"note:{n1}@1"))
        p_b1 = typed(res(f"bookmark:{bm1}@1"))
        p_j1 = typed(res(f"journal_block:{jb1}@1"))
        gnote = json.loads(next(ln for ln in query("get-note", "--owner", "A",
                                                   "--id", n1).stdout.splitlines()
                                if ln.strip()))
        stored = (gnote.get("refs") or [{}])[0]
        p_stored = typed(res(f"{stored.get('kind')}:{stored.get('id')}@"
                             f"{stored.get('revision')}"))
        ok2 = (p_h1 and p_h1.get("state") == "historical"
               and p_h1.get("pinned_revision") == 1
               and p_h1.get("current_revision") == 3
               and p_h1.get("resolved_ref") == f"highlight:{hl1}@1"
               and p_h3 and p_h3.get("state") == "current"
               and p_h3.get("revision") == 3
               and p_n1 and p_n1.get("state") == "historical"
               and p_n1.get("pinned_revision") == 1
               and p_n1.get("current_revision") == 3
               and p_n1.get("resolved_ref") == f"note:{n1}@1"
               and p_b1 and p_b1.get("state") == "historical"
               and p_b1.get("pinned_revision") == 1
               and p_b1.get("current_revision") == 2
               and p_j1 and p_j1.get("state") == "historical"
               and p_j1.get("pinned_revision") == 1
               and p_j1.get("current_revision") == 2
               and stored.get("kind") == "highlight" and stored.get("id") == hl1
               and int(stored.get("revision")) == 1
               and p_stored and p_stored.get("state") == "historical"
               and p_stored.get("resolved_ref") == f"highlight:{hl1}@1")
        check("REF-02", ok2,
              "the version pinning: a pin at a SUPERSEDED revision answers historical "
              "— the pinned revision served EXACTLY as pinned (resolved_ref = the "
              "pinned form) with the current revision named alongside (never a silent "
              "retarget); a pin at the CURRENT revision answers current; the unpinned "
              "and pinned forms of one target differ exactly by the selected revision "
              "(the logical identity one, the selected revision many); the note "
              "machine's OWN stored reference (get-note's refs — the CLAIM-057 "
              "substrate) resolves through the ONE surface to the same pinned answer "
              "(the compose); two content revisions later the reference still resolves "
              "(the identity is the uuid — titles/labels/content change without "
              "breaking references)",
              "the resolution must honor the pin EXACTLY (the substrate's "
              "version-aware law): serving the current revision to a pinned reference "
              "is the forbidden silent retarget; the stored-ref round-trip must go "
              "through the same resolution path, never a second implementation")

        # ---- REF-03 — the tombstoned state
        t_h = typed(res(f"highlight:{hl_t}"))
        t_hp = typed(res(f"highlight:{hl_t}@1"))
        t_b = typed(res(f"bookmark:{bm_t}"))
        t_n = typed(res(f"note:{nt}"))
        t_np = typed(res(f"note:{nt}@1"))
        cmd("restore_note", "--id", nt, key="ref-nt-3")
        t_r = typed(res(f"note:{nt}"))
        ok3 = (t_h and t_h.get("state") == "tombstoned"
               and t_hp and t_hp.get("state") == "tombstoned"
               and t_b and t_b.get("state") == "tombstoned"
               and t_n and t_n.get("state") == "tombstoned"
               and t_np and t_np.get("state") == "tombstoned"
               and all("revision" not in d and "resolved_ref" not in d
                       and "content" not in d
                       for d in (t_h, t_hp, t_b, t_n, t_np))
               and all(d.get("id") in (hl_t, bm_t, nt)
                       and d.get("api_version") == 1
                       for d in (t_h, t_hp, t_b, t_n, t_np))
               and t_r and t_r.get("state") == "current"
               and t_r.get("revision") == 1)
        check("REF-03", ok3,
              "the tombstoned state across all three lifecycle families "
              "(highlight/bookmark/note): the reference answers tombstoned for BOTH "
              "the unpinned and the PINNED forms (a pin never bypasses a tombstone); "
              "the answer carries NO revision, NO resolved_ref, NO content — the "
              "tombstone is the answer, deleted private content never leaks through "
              "a reference; restore returns the reference to current (the lifecycle "
              "parity composed, never re-derived)",
              "the tombstone check must precede the revision resolution (the "
              "lifecycle state governs the whole identity); a pinned historical "
              "revision of a tombstoned target is STILL the tombstone answer — the "
              "reference surface never becomes a tombstone bypass")

        # ---- REF-04 — the unavailable + ambiguous states (the anchor compose)
        u_ne = typed(res(f"anchor:{anc_ne}"))
        u_amb = typed(res(f"anchor:{anc_amb}"))
        u_ok = typed(res(f"anchor:{anc1}"))
        ok4 = (pl1.returncode == 0 and pl2.returncode == 0
               and u_ne and u_ne.get("state") == "unavailable"
               and u_ne.get("cause") == "no-current-generation"
               and u_ne.get("kind") == "anchor" and u_ne.get("id") == anc_ne
               and u_amb and u_amb.get("state") == "ambiguous"
               and int(u_amb.get("evidence_hits") or 0) >= 2
               and u_amb.get("id") == anc_amb
               and u_ok and u_ok.get("state") == "current"
               and u_ok.get("generation_id") == gen1
               and "resolved_ref" not in u_ne and "resolved_ref" not in u_amb)
        check("REF-04", ok4,
              "the unavailable and ambiguous states — the anchor-resolution class "
              "composed (never re-implemented): an anchor over a NEVER-EXTRACTED "
              "source answers unavailable with the NAMED cause "
              "(no-current-generation — the target absent from the current view, the "
              "row retained); the drifted-tiling anchor over repeated content "
              "answers ambiguous with evidence_hits >= 2 (the locator matches "
              "multiple candidates — the honest answer, never a first-hit "
              "retarget); the same fixture family's resolved anchor answers current "
              "with the serving generation_id; the unavailable/ambiguous answers "
              "carry NO resolved_ref (nothing was resolved)",
              "the resolution must compose the P3-03b machinery's typed verdicts "
              "verbatim (unresolved->unavailable with the cause, ambiguous->ambiguous "
              "with the hit count, resolved->current with the generation_id) — a "
              "nearest-match retarget or a silent skip of the anchor verdict is the "
              "forbidden behavior (SYS-05)")

        # ---- REF-05 — the purged state + the precedence + the closed vocabulary
        g_np = typed(res(f"note:{np_}"))
        g_npp = typed(res(f"note:{np_}@1"))
        g_pt = typed(res(f"highlight:{hpt}"))
        v_jb = purge_row("journal_block", jb1)
        ok5 = (g_np and g_np.get("state") == "purged"
               and g_np.get("kind") == "note" and g_np.get("id") == np_
               and g_npp and g_npp.get("state") == "purged"
               and g_pt and g_pt.get("state") == "purged"
               and all("revision" not in d and "resolved_ref" not in d
                       for d in (g_np, g_npp, g_pt))
               and v_jb.returncode != 0
               and "purge_ledger_purge_kind_check" in (v_jb.stderr or ""))
        check("REF-05", ok5,
              "the purged state + the precedence: a purge-ledger row makes the "
              "reference answer purged for BOTH the unpinned and the PINNED forms "
              "(the governed purge invalidates the access — the 0013 permanence "
              "record); purged WINS over tombstoned (the tombstoned+purged highlight "
              "answers purged — the purge is the stronger invalidation); the purged "
              "answer carries NO revision and NO resolved_ref; the ledger's own kind "
              "CHECK refuses a journal_block row (the 0013 closed vocabulary — the "
              "substrate pin, this surface never widens it)",
              "the purge-ledger lookup must precede every other state derivation "
              "(the precedence: purged > tombstoned > current/historical); the "
              "journal_block refusal is the 0013 substrate's own CHECK — widening "
              "the ledger vocabulary is a substrate change, never this surface's "
              "choice")

        # ---- REF-06 — the refusals + the no-oracle + the hostile-string law
        before = audit("SELECT count(*) FROM arv.command_log;")
        # B's own entities for the cross-owner asks (per family)
        xb = {"work": b_gs["work_id"], "source": b_src, "anchor": b_anc,
              "highlight": b_hl, "bookmark": b_bm, "note": b_note,
              "journal_block": b_jb}
        norm_ok, code_ok, no_ans = True, True, True
        for k in KINDS_BARE + KINDS_REV:
            r_x = res(f"{k}:{xb[k]}")                 # A asks B's entity
            r_a = res(f"{k}:{ABSENT}")                # A asks an absent id
            nx = (r_x.stdout.replace(xb[k], "<ID>"), r_x.stderr)
            na = (r_a.stdout.replace(ABSENT, "<ID>"), r_a.stderr)
            norm_ok = norm_ok and (nx == na)
            code_ok = code_ok and r_x.returncode == 1 and r_a.returncode == 1 \
                and "FAIL ARV-REF-001:" in r_x.stdout \
                and "FAIL ARV-REF-001:" in r_a.stdout
            no_ans = no_ans and typed(r_x) is None and typed(r_a) is None
        # the nonexistent target revision on a LIVE target — the same class
        r_rev = res(f"note:{n1}@9")
        r_revx = res(f"note:{ABSENT}@9")
        nrv = (r_rev.stdout.replace(n1, "<ID>"), r_rev.stderr)
        nax = (r_revx.stdout.replace(ABSENT, "<ID>"), r_revx.stderr)
        # the malformed forms — the hostile-string law
        hostiles = [
            "capture:" + ABSENT,                      # unknown kind
            "note:not-a-uuid",                        # non-uuid id
            f"work:{work1}@1",                        # revision on a bare family
            f"source:{src1}@2",                       # ditto
            f"anchor:{anc1}@1",                       # ditto
            f"note:{n1}@0",                           # zero revision
            f"note:{n1}@x",                           # non-digit revision
            "note:' OR '1'='1",                       # SQL metacharacters
            "journal_block:" + "z" * 10000,           # the oversize hostile string
        ]
        m_ok = True
        for h in hostiles:
            r_m = res(h)
            m_ok = m_ok and r_m.returncode == 1 \
                and "FAIL ARV-REF-002:" in r_m.stdout and typed(r_m) is None
        after = audit("SELECT count(*) FROM arv.command_log;")
        ok6 = (norm_ok and code_ok and no_ans
               and r_rev.returncode == 1 and "FAIL ARV-REF-001:" in r_rev.stdout
               and nrv == nax
               and m_ok
               and int(before) == int(after)
               and set(OBSERVED) == set(SIX)
               and all(s in SIX for s in OBSERVED))
        check("REF-06", ok6,
              "the typed refusals + the no-oracle + the hostile-string law: for "
              "EVERY family the absent id and another owner's id are the SAME "
              "ARV-REF-001 refusal (template-normalized byte-equal — never an "
              "existence side channel); a nonexistent target revision on a live "
              "target is the SAME class (the substrate's ARV-NTE-003 law); the "
              "malformed forms — unknown kind, non-uuid, a revision on a bare "
              "family, @0, @x, the SQL-metacharacter string, the 10k oversize "
              "string — refuse ARV-REF-002 (a reference string is DATA, never an "
              "instruction: imported hostile strings never acquire authority by "
              "being read); every refusal is exit 1 with ZERO answer lines; the "
              "resolution never writes (the command_log count unchanged); the "
              "observed states across the whole suite are EXACTLY the closed six "
              "(exclusive, observable, fail-closed)",
              "the no-oracle must hold at the resolution boundary for every family "
              "(absent == cross-owner == nonexistent-revision, byte-equal after id "
              "normalization); the malformed grammar refuses with the named code "
              "never a clamp; the six-state vocabulary is closed — an unknown state "
              "is a named refusal, never a guess")

        print()
        if FAILS:
            print(f"RED — the P4-D slice one suite fails: {', '.join(FAILS)}")
            return 1
        print("REFERENCE SUITE GREEN — REF-01..06 (the stable @-reference system: "
              "the six explicit states, the version-aware resolution over the seven "
              "families, the no-oracle, composing the CLAIM-057 substrate)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
