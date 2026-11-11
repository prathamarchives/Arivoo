#!/usr/bin/env python3
"""harness/tests/test_note_reference.py — P3-06 acceptance suite, SLICE TWO
of the two-slice sequence (CLAIM-057, the version-aware REFERENCE machine's
contract pins; RTM §2.5 item 7 + item 9 + §3.3, SYS-02/03 primary, SYS-01/04
standing, PLAN's P3-06 card). The note CORE machine is CLAIM-056's slice,
LANDED at PR #91 — this suite re-homes the reference assertions the LAW-05
split (9608a3a) moved out of test_note.py: none deleted from the project.
Red-first (LAW-11): at CLAIM-056's merged head 36e34920 the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt).

THE MACHINE (RTM §2.5 item 7): references are EXPLICIT, VERSION-AWARE, and
PER-REVISION — arv.note_reference rows (kind work/source/anchor/highlight/
note; highlight/note refs MUST name the target revision, work/source/anchor
MUST NOT — note_reference_ref_shape_check; the set semantics UNIQUE per
(note, revision, kind, target); the target-existence + caller-scope guard at
the command boundary AND the substrate). The referenced (id, revision) pair
is PINNED at write time — the immutable revision is what a reference means,
never a silent retarget. Each revision carries its OWN reference set
(replacement semantics: the revise's set replaces; the prior revision's rows
stay untouched and accurate). The read arms render the refs array
version-aware; a free-standing note's refs render as JSON null. The spine's
canonical body covers content AND the canonical sorted reference set — the
same logical set in a different CLI order is the SAME command (LAW-23).

Refusal codes: ARV-NTE-003 absent/another-owner's/nonexistent-revision
target (the SAME refusal, never a side channel — both boundaries); 006 the
shape classes (missing @rev, forbidden @rev, unknown kind, malformed id);
007 the substrate's note-existence binding; 008 the duplicate (set
semantics); ARV-CAP-005 the append-only substrate.

Cases (the NTR registry; each pin's full statement lives at its check()):
  NTR-01 create with the full mixed reference set (work/source/anchor
         versionless + highlight@1) — the per-revision rows + the ack rung;
         a free-standing note renders refs null; provenance complete
  NTR-02 the shape classes: highlight without @rev; work WITH @rev; unknown
         kind; malformed id — ARV-NTE-006, zero effect
  NTR-03 the dangling targets: absent work/source/anchor/highlight/note and
         a highlight at a nonexistent revision — ARV-NTE-003, zero effect
  NTR-04 the caller-scope boundary: another owner's work/source/highlight/
         note are the SAME 003 refusal (never a side channel)
  NTR-05 the set semantics + the canonical replay: a duplicate target 008;
         the same set SHUFFLED replays (LAW-23); a conflicting body 409s
  NTR-06 the substrate: direct UPDATE/DELETE refused at BOTH boundaries;
         the hostile dangling insert meets the guard; the hostile
         work-with-revision meets the shape CHECK; RLS FORCED; the grants
  NTR-07 version-aware immutability: a historical highlight/note reference
         stays at its pinned revision through the target's later revises; a
         current-revision reference is accepted
  NTR-08 replacement semantics: revision 2 carries its OWN set; revision
         1's rows stay; the history renders both sets accurately
  NTR-09 the export-ready rebuild: the current view (content + refs)
         re-derived from the history rows ALONE equals the get-note answer
  NTR-10 the crash matrix WITH references: pre-commit leaves zero note rows
         AND zero reference rows; post-commit-pre-ack commits both and the
         replay converges the lost ack (zero-or-one WHOLE-command effect)
  NTR-11 the schema audits (0010): the exact column set, the shape CHECK,
         the two triggers, RLS enabled AND FORCED, the grants, the UNIQUEs
  NTR-12 the tombstone boundary: a tombstoned note's governed history
         retains every revision with its OWN refs; restore returns the
         current view with its refs; the ordinary read never leaks them
  NTR-13 (P4-D slice two, CLAIM-076) the seven-kind write round-trip: the
         full mixed set incl. bookmark@rev + journal_block@rev lands; get-note
         renders the seven-entry refs array; the STORED new-kind refs resolve
         through the ONE surface (the compose); revision 2 carries its OWN
         new-kind set (the replacement semantics)
  NTR-14 the shape law for the new kinds: a bare bookmark/journal_block (no
         @rev) and a non-digit pin refuse ARV-NTE-006; a duplicate target
         008; the same set SHUFFLED replays under the same key (LAW-23); a
         different set under the same key 409s
  NTR-15 the no-oracle for the new kinds: absent, cross-owner, and a
         nonexistent revision on a live target are the SAME ARV-NTE-003
         refusal (template-normalized byte-equal), zero effect
  NTR-16 the substrate backstop (0018): the out-of-vocabulary direct INSERT
         still refuses the kind CHECK (the widening is exactly two kinds,
         never open); a bookmark/journal_block row without the revision
         refuses the shape CHECK; the WELL-FORMED direct row for each new
         kind is ADMITTED — proving the guard routes the new kinds to THEIR
         tables (not the note ELSE arm); the ghost target refuses ARV-NTE-003
         at the substrate

Run: python3 harness/tests/test_note_reference.py   (exit 0 = green)
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

# P4-D slice two (CLAIM-076) — the machinery-absent probe (LAW-11): the
# write-completion machinery is the SEVEN-kind vocabulary at the note --ref
# boundary. The probe is DB-FREE by construction: the parse refusal precedes
# the spine's connection (the nonexistent database below is never reached at
# the RED tree — the vocabulary refusal fires first; at the GREEN tree the
# parse passes and the connection refuses, the probe's one-job output check
# unaffected). At the five-kind tree this prints the machinery-absent RED.
_p76 = subprocess.run(
    [sys.executable, str(REPO / "harness" / "commands.py"), "create_note",
     "--owner", "A", "--actor", "owner", "--client-id", "cli-probe",
     "--idem-key", "p4d2-machinery-absent-probe", "--content", "probe",
     "--ref", "bookmark:00000000-0000-0000-0000-000000000000@1"],
    capture_output=True, text=True, timeout=60,
    env=dict(os.environ, PGDATABASE="arv_p4d2_red_probe_absent"))
if "ARV-NTE-006" in _p76.stdout and "bookmark" in _p76.stdout:
    print("FAIL ARV-TEST-000: the P4-D slice two write-completion machinery is "
          "absent (machinery-absent class; the note --ref vocabulary still "
          "refuses the bookmark kind — the seven-kind widening is not landed) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


_probe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                          "create_note", "--help"], capture_output=True, text=True)
_absent_ref = "--ref" not in _probe.stdout
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0010_*.sql"))
if _absent_ref or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-06 reference machinery is absent "
          f"(machinery-absent class; --ref surface on create_note absent: "
          f"{_absent_ref}; migration 0010 present: {bool(_mig)}) — the "
          "implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

DB = ENV = None

# the fixture source text: two spans for the highlight revision ladder
TEXT = ("The note-bearing reading.\n"
        "Second paragraph: the first span lives here, plainly.\n"
        "Third paragraph: the moved span lives here instead.\n"
        "Fourth paragraph closes.\n")


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=240, env=ENV)


def import_src(key: str, title: str, file: str, owner: str = "A",
               media: str = "text/plain") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "commands.py"), "import_source",
               "--owner", owner, "--actor", "owner", "--client-id", "cli-1",
               "--idem-key", key, "--file", file, "--media-type", media,
               "--title", title)


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
               "--idem-key", key, "--id", hl_id, "--start", str(start),
               "--end", str(end))


def note_cmd(op: str, key: str, owner: str = "A", client: str = "cli-1",
             id_: str = None, content: str = None, content_file=None,
             refs: list = None) -> subprocess.CompletedProcess:
    """The note-family CLI driver. refs: canonical ref strings
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


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def typed(p: subprocess.CompletedProcess) -> "dict | None":
    """The typed answer: ONE JSON line on stdout, exit 0."""
    lines = [ln for ln in p.stdout.split("\n") if ln.strip()]
    if p.returncode != 0 or len(lines) != 1:
        return None
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError:
        return None


def history_rows(owner: str, note_id: str) -> list:
    p = qy("get-note-history", owner, note_id)
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
    DB = pg.create_scratch_db("p306r")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ------- the fixture: real bytes, two owners, a revised highlight
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
        phb = mk_highlight("hl-B1", sid_b, s1, e1, owner="B")
        hlb = ack_field(phb, "result_ref")
        pnb = mk_note("note-B1", content="B's private deep thinking.", owner="B")
        noteb = ack_field(pnb, "result_ref")
        ph1 = mk_highlight("hl-A1", sid_a, s1, e1)
        h1 = ack_field(ph1, "result_ref")
        ph2 = revise_hl("hl-A1r", h1, s2, e2)
        assert ph2.returncode == 0, "fixture: the highlight revise must succeed"
        anc_a = audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{h1}' "
                      f"AND revision=1;")

        # ---- NTR-01 — create with the full mixed reference set
        refs_a = [f"work:{wid_a}", f"source:{sid_a}", f"anchor:{anc_a}",
                  f"highlight:{h1}@1"]
        p1 = mk_note("n-A1", content="The first referenced thinking.", refs=refs_a)
        n1 = ack_field(p1, "result_ref")
        rev1 = ack_field(p1, "revision")
        rung1 = ack_field(p1, "durability_rung")
        # a free-standing note beside (the null rendering is never vacuous)
        pfs = mk_note("n-free", content="Free-standing, zero references.")
        nfs = ack_field(pfs, "result_ref")
        g1 = typed(qy("get-note", "A", n1))
        gfs = typed(qy("get-note", "A", nfs))
        rr = audit_rows(f"SELECT ref_kind, ref_id, ref_revision::text FROM "
                        f"arv.note_reference WHERE note_id='{n1}' "
                        f"ORDER BY ref_kind, ref_id;")
        prov = audit_rows(f"SELECT actor, idempotency_key FROM arv.note_reference "
                          f"WHERE note_id='{n1}' ORDER BY ref_kind;")
        ok1 = (p1.returncode == 0 and "status=committed" in p1.stdout
               and rev1 == "1" and rung1 == "local_durable"
               and g1 is not None
               and g1.get("refs") == [{"kind": "anchor", "id": anc_a, "revision": None},
                                       {"kind": "highlight", "id": h1, "revision": 1},
                                       {"kind": "source", "id": sid_a, "revision": None},
                                       {"kind": "work", "id": wid_a, "revision": None}]
               and gfs is not None and gfs.get("refs") is None
               and rr == [f"anchor|{anc_a}|", f"highlight|{h1}|1",
                          f"source|{sid_a}|", f"work|{wid_a}|"]
               and len(prov) == 4 and set(prov) == {"owner|n-A1"})
        check("NTR-01", ok1,
              "create with the mixed set appends the revision-1 note row AND the per-revision reference rows (work/source/anchor versionless, highlight@1 version-aware); get-note renders the version-aware refs array; a free-standing note renders refs as JSON null (zero rows aggregated); every reference row carries the command provenance (actor + the idem-key ref); the ack names revision=1 + durability_rung=local_durable",
              "the note's references are explicit per-revision rows — the free-standing law holds (zero references legal) and the mixed shape renders exactly (RTM §2.5 item 7)")

        # ---- NTR-02 — the shape classes (ARV-NTE-006)
        before = audit("SELECT count(*) FROM arv.note;")
        before_r = audit("SELECT count(*) FROM arv.note_reference;")
        p_sh1 = mk_note("n-sh1", content="x", refs=[f"highlight:{h1}"])
        p_sh2 = mk_note("n-sh2", content="x", refs=[f"work:{wid_a}@2"])
        p_sh3 = mk_note("n-sh3", content="x", refs=[f"chapter:{wid_a}"])
        p_sh4 = mk_note("n-sh4", content="x", refs=["work:not-a-uuid"])
        after = audit("SELECT count(*) FROM arv.note;")
        after_r = audit("SELECT count(*) FROM arv.note_reference;")
        ok2 = (p_sh1.returncode == 1 and "ARV-NTE-006" in p_sh1.stdout
               and p_sh2.returncode == 1 and "ARV-NTE-006" in p_sh2.stdout
               and p_sh3.returncode == 1 and "ARV-NTE-006" in p_sh3.stdout
               and p_sh4.returncode == 1 and "ARV-NTE-006" in p_sh4.stdout
               and after == before and after_r == before_r)
        check("NTR-02", ok2,
              "the four shape classes refuse with ARV-NTE-006 and zero effect: a highlight/note reference without @rev (version-aware by construction), a work/source/anchor reference WITH @rev (the Source id IS the version; Work/Anchor carry no revision dimension), an unknown kind, a malformed id — never a silent reinterpretation",
              "the reference grammar is exact: kind:id for work/source/anchor, kind:id@rev for highlight/note (RTM §2.5 item 7's shape law)")

        # ---- NTR-03 — the dangling targets (ARV-NTE-003)
        ghost = "00000000-0000-7000-8000-00000000000d"
        p_dw = mk_note("n-dw", content="x", refs=[f"work:{ghost}"])
        p_ds = mk_note("n-ds", content="x", refs=[f"source:{ghost}"])
        p_da = mk_note("n-da", content="x", refs=[f"anchor:{ghost}"])
        p_dh = mk_note("n-dh", content="x", refs=[f"highlight:{h1}@1",
                                                  f"highlight:{ghost}@1"])
        p_dn = mk_note("n-dn", content="x", refs=[f"note:{ghost}@1"])
        p_drev = mk_note("n-drev", content="x", refs=[f"highlight:{h1}@99"])
        ok3 = (p_dw.returncode == 1 and "ARV-NTE-003" in p_dw.stdout
               and p_ds.returncode == 1 and "ARV-NTE-003" in p_ds.stdout
               and p_da.returncode == 1 and "ARV-NTE-003" in p_da.stdout
               and p_dh.returncode == 1 and "ARV-NTE-003" in p_dh.stdout
               and p_dn.returncode == 1 and "ARV-NTE-003" in p_dn.stdout
               and p_drev.returncode == 1 and "ARV-NTE-003" in p_drev.stdout
               and audit("SELECT count(*) FROM arv.note;") == before)
        check("NTR-03", ok3,
              "every dangling target class refuses with ARV-NTE-003 and zero effect: an absent work/source/anchor, an absent highlight/note, a highlight at a NONEXISTENT revision (the (id, revision) pair must exist) — and a valid reference beside a dangling one still refuses the whole command (the set is atomic with the note revision)",
              "a reference means an existing (id, revision) pair in the caller's scope — never a forward or dangling pointer (RTM §2.5 item 7; the anchor-typing precedent)")

        # ---- NTR-04 — the caller-scope boundary (never a side channel)
        p_xw = mk_note("n-xw", content="x", refs=[f"work:{wid_b}"])
        p_xs = mk_note("n-xs", content="x", refs=[f"source:{sid_b}"])
        p_xh = mk_note("n-xh", content="x", refs=[f"highlight:{hlb}@1"])
        p_xn = mk_note("n-xn", content="x", refs=[f"note:{noteb}@1"])
        # the refusal TEMPLATE is byte-identical to the absent-target form
        # modulo the caller-supplied id (which the caller already knows —
        # never an existence side channel)
        tmpl_w = p_xw.stdout.replace(wid_b, "<id>")
        tmpl_abs = p_dw.stdout.replace(ghost, "<id>")
        ok4 = (p_xw.returncode == 1 and "ARV-NTE-003" in p_xw.stdout
               and p_xs.returncode == 1 and "ARV-NTE-003" in p_xs.stdout
               and p_xh.returncode == 1 and "ARV-NTE-003" in p_xh.stdout
               and p_xn.returncode == 1 and "ARV-NTE-003" in p_xn.stdout
               and tmpl_w == tmpl_abs)
        check("NTR-04", ok4,
              "references to ANOTHER OWNER's work/source/highlight/note are the SAME ARV-NTE-003 refusal as the absent targets — the refusal text never distinguishes another owner's object from a nonexistent one (no existence side channel through the reference boundary; the session is RLS-scoped to the caller)",
              "absent and another owner's are the SAME refusal at every boundary (RTM §2.10; LAW-22 owner isolation — the reference check rides the caller-scoped read)")

        # ---- NTR-05 — the set semantics + the canonical replay (LAW-23)
        p_dup = mk_note("n-dup", content="x", refs=[f"work:{wid_a}",
                                                    f"source:{sid_a}",
                                                    f"work:{wid_a}"])
        # the same logical set SHUFFLED under the SAME key -> REPLAY (LAW-23)
        rep = mk_note("n-A1", content="The first referenced thinking.",
                      refs=[f"highlight:{h1}@1", f"work:{wid_a}",
                            f"anchor:{anc_a}", f"source:{sid_a}"])
        cnt = audit(f"SELECT count(*) FROM arv.note WHERE id='{n1}';")
        cnt_r = audit(f"SELECT count(*) FROM arv.note_reference WHERE note_id='{n1}';")
        # the same key with a DIFFERENT set -> ARV-CMD-409, zero effect
        conf = mk_note("n-A1", content="The first referenced thinking.",
                       refs=[f"work:{wid_a}"])
        conf_r = audit(f"SELECT count(*) FROM arv.note_reference WHERE note_id='{n1}';")
        ok5 = (p_dup.returncode == 1 and "ARV-NTE-008" in p_dup.stdout
               and rep.returncode == 0 and "status=replayed" in rep.stdout
               and cnt == "1" and cnt_r == "4" and conf_r == "4"
               and conf.returncode == 1 and "ARV-CMD-409" in conf.stdout)
        check("NTR-05", ok5,
              "a duplicate target in one command refuses with ARV-NTE-008 (the set is a set); the SAME logical reference set in a DIFFERENT CLI order under the same idem key REPLAYS the committed result (the canonical body covers the sorted set — exactly-once over the LOGICAL command); a different set under the same key is a conflicting body — ARV-CMD-409, zero effect",
              "the reference set is part of the command's logical identity (LAW-23): canonical form, order-independent hash, one effect")

        # ---- NTR-06 — the substrate (the hostile direct writes)
        up_r = app_sql(f"UPDATE arv.note_reference SET ref_id=ref_id WHERE note_id='{n1}';")
        dele_r = app_sql(f"DELETE FROM arv.note_reference WHERE note_id='{n1}';")
        up_rt = super_sql(f"UPDATE arv.note_reference SET ref_id=ref_id WHERE note_id='{n1}';")
        dele_rt = super_sql(f"DELETE FROM arv.note_reference WHERE note_id='{n1}';")
        host_ref = app_sql(
            f"INSERT INTO arv.note_reference (id, note_id, note_revision, ref_kind, ref_id, "
            f"ref_revision, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
            f"VALUES (gen_random_uuid(), '{n1}', 1, 'work', '{ghost}', NULL, 'A', 'owner', "
            f"'run-hostile', 'ih', 'hostile-1', now());")
        host_shape = app_sql(
            f"INSERT INTO arv.note_reference (id, note_id, note_revision, ref_kind, ref_id, "
            f"ref_revision, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
            f"VALUES (gen_random_uuid(), '{n1}', 1, 'work', '{wid_a}', 3, 'A', 'owner', "
            f"'run-hostile', 'ih', 'hostile-2', now());")
        host_bind = app_sql(
            f"INSERT INTO arv.note_reference (id, note_id, note_revision, ref_kind, ref_id, "
            f"ref_revision, owner_scope, actor, run_id, input_hash, idempotency_key, created_at) "
            f"VALUES (gen_random_uuid(), '{n1}', 9, 'work', '{wid_a}', NULL, 'A', 'owner', "
            f"'run-hostile', 'ih', 'hostile-3', now());")
        cnt_r2 = audit(f"SELECT count(*) FROM arv.note_reference WHERE note_id='{n1}';")
        ok6 = (up_r.returncode == 1 and "permission denied" in up_r.stderr
               and dele_r.returncode == 1 and "permission denied" in dele_r.stderr
               and "ARV-CAP-005" in up_rt.stderr and "ARV-CAP-005" in dele_rt.stderr
               and host_ref.returncode == 1 and "ARV-NTE-003" in host_ref.stderr
               and host_shape.returncode == 1
               and "note_reference_ref_shape_check" in host_shape.stderr
               and host_bind.returncode == 1 and "ARV-NTE-007" in host_bind.stderr
               and cnt_r2 == "4")
        check("NTR-06", ok6,
              "direct UPDATE/DELETE on arv.note_reference is refused at BOTH boundaries (arv_app: permission denied; the superuser: ARV-CAP-005 append-only); the hostile direct INSERT with a dangling target meets the substrate guard's ARV-NTE-003; a work-with-revision insert meets note_reference_ref_shape_check; a reference row bound to a nonexistent (note, revision) meets ARV-NTE-007 — zero rows land",
              "the substrate guards the reference rows independently of the command boundary (the 0007/0008 convention: the trigger checks existence-in-scope, the CHECK pins the shape, the append-only law holds")

        # ---- NTR-07 — version-aware immutability (never a silent retarget)
        # n7 refs highlight H at its HISTORICAL revision 1; H is at revision 2
        p7 = mk_note("n-7", content="the version-aware subject.",
                     refs=[f"highlight:{h1}@1"])
        n7 = ack_field(p7, "result_ref")
        g7 = typed(qy("get-note", "A", n7))
        revise_hl("hl-A1r2", h1, s1, e1)          # H now at revision 3
        g7b = typed(qy("get-note", "A", n7))
        # a reference at the CURRENT revision (3) is accepted
        p7c = mk_note("n-7c", content="refs the current revision.",
                      refs=[f"highlight:{h1}@3"])
        # a note-to-note historical reference: n9 refs n7@1; n7 then revises
        p9 = mk_note("n-9", content="refs the note at its first revision.",
                     refs=[f"note:{n7}@1"])
        n9 = ack_field(p9, "result_ref")
        revise_note("n-7r", n7, content="the note's second thinking.")
        g9 = typed(qy("get-note", "A", n9))
        ok7 = (g7 is not None
               and g7.get("refs") == [{"kind": "highlight", "id": h1, "revision": 1}]
               and g7b is not None
               and g7b.get("refs") == [{"kind": "highlight", "id": h1, "revision": 1}]
               and p7c.returncode == 0
               and g9 is not None
               and g9.get("refs") == [{"kind": "note", "id": n7, "revision": 1}])
        check("NTR-07", ok7,
              "a historical highlight reference stays at its pinned revision after the target revises again (still @1 — the reference is to the IMMUTABLE revision, never a silent retarget); a reference at the current revision is accepted; a note-to-note historical reference stays @1 after the referenced note revises",
              "references are version-aware and immutable-in-meaning: the referenced (id, revision) pair is pinned at write time (RTM §2.5 item 7 — referenceable historical revisions)")

        # ---- NTR-08 — replacement semantics (each revision's OWN set)
        pv9 = revise_note("n-9r", n9, content="the second thinking of n9.",
                          refs=[f"source:{sid_a}", f"note:{n7}@1"])
        h9 = history_rows("A", n9)
        h9r1 = [r for r in h9 if r.get("kind") == "revision" and r.get("revision") == 1]
        h9r2 = [r for r in h9 if r.get("kind") == "revision" and r.get("revision") == 2]
        g9b = typed(qy("get-note", "A", n9))
        r1_rows = audit_rows(f"SELECT ref_kind FROM arv.note_reference WHERE "
                             f"note_id='{n9}' AND note_revision=1 ORDER BY ref_kind;")
        r2_rows = audit_rows(f"SELECT ref_kind FROM arv.note_reference WHERE "
                             f"note_id='{n9}' AND note_revision=2 ORDER BY ref_kind;")
        ok8 = (pv9.returncode == 0
               and len(h9r1) == 1
               and h9r1[0].get("refs") == [{"kind": "note", "id": n7, "revision": 1}]
               and len(h9r2) == 1
               and h9r2[0].get("refs") == [{"kind": "note", "id": n7, "revision": 1},
                                            {"kind": "source", "id": sid_a, "revision": None}]
               and g9b is not None
               and g9b.get("refs") == h9r2[0].get("refs")
               and r1_rows == ["note"] and r2_rows == ["note", "source"])
        check("NTR-08", ok8,
              "the revise carries its OWN full reference set (replacement semantics): revision 2's set replaces revision 1's for the CURRENT view while revision 1's rows stay untouched and accurate — the history renders each revision with its own set, and the substrate holds both sets side by side",
              "a revision is a complete immutable snapshot (content + reference set): editing never rewrites the past (RTM §2.5 item 9 — Note revisions authoritative)")

        # ---- NTR-09 — the export-ready rebuild from history alone
        h_all = history_rows("A", n9)
        revs = [r for r in h_all if r.get("kind") == "revision"]
        cur = max(revs, key=lambda r: r["revision"])
        state = derived_state(h_all)
        g9c = typed(qy("get-note", "A", n9))
        ok9 = (state == "active" and g9c is not None
               and g9c.get("revision") == cur.get("revision")
               and g9c.get("content") == cur.get("content")
               and (g9c.get("refs") or []) == (cur.get("refs") or [])
               and all(r.get("actor") for r in revs)
               and all(r.get("created_at") for r in revs))
        check("NTR-09", ok9,
              "the current view (state + current revision + content + the REFERENCE SET + attribution on every revision) re-derived from the get-note-history rows ALONE equals the get-note answer — every revision retrievable, attributable, and referenceable from history alone",
              "PLAN's P3-06 acceptance: 'every revision is retrievable, attributable, and referenceable' — the history rows carry everything the P3-09 export needs (SYS-07's authoritative substrate)")

        # ---- NTR-10 — the crash matrix WITH references
        nf = audit("SELECT count(*) FROM arv.note;")
        nfr = audit("SELECT count(*) FROM arv.note_reference;")
        c_pc = crash("--command", "create_note", "--point", "pre-commit",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create",
                     "--content", "crash-create content", "--ref", f"work:{wid_a}")
        nf2 = audit("SELECT count(*) FROM arv.note;")
        nfr2 = audit("SELECT count(*) FROM arv.note_reference;")
        c_pa = crash("--command", "create_note", "--point", "post-commit-pre-ack",
                     "--owner", "A", "--client-id", "cr-1", "--idem-key", "crash-create2",
                     "--content", "the lost-ack create body", "--ref", f"work:{wid_a}")
        nf3 = audit("SELECT count(*) FROM arv.note;")
        nfr3 = audit("SELECT count(*) FROM arv.note_reference;")
        rep_c = note_cmd("create_note", "crash-create2", client="cr-1",
                         content="the lost-ack create body", refs=[f"work:{wid_a}"])
        n_pa = ack_field(rep_c, "result_ref")
        g_pa = typed(qy("get-note", "A", n_pa))
        r_pc = crash("--command", "revise_note", "--point", "pre-commit",
                     "--owner", "A", "--client-id", "cr-2", "--idem-key", "crash-revise",
                     "--id", n1, "--content", "crash-revise body",
                     "--ref", f"source:{sid_a}")
        nfr4 = audit("SELECT count(*) FROM arv.note_reference;")
        ok10 = (c_pc.returncode == 2 and nf2 == nf and nfr2 == nfr
                and c_pa.returncode == 2 and nf3 == str(int(nf) + 1)
                and nfr3 == str(int(nfr) + 1)
                and rep_c.returncode == 0 and "status=replayed" in rep_c.stdout
                and g_pa is not None
                and g_pa.get("refs") == [{"kind": "work", "id": wid_a, "revision": None}]
                and r_pc.returncode == 2 and nfr4 == nfr3)
        check("NTR-10", ok10,
              "a create/revise carrying references at pre-commit leaves ZERO note rows AND ZERO reference rows (the whole logical command — content and references — is one transactional effect); at post-commit-pre-ack BOTH are committed (exit 2, no ack) and the same-key replay converges the lost ack with the references intact; a crashed revise leaves the reference rows unchanged",
              "the crash-injection spine (§1.6/§3.3): a crashed command either never happened or is durably recorded WHOLE — content and references are never split across the boundary")

        # ---- NTR-11 — the schema audits (migration 0010)
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='note_reference' "
                          "ORDER BY ordinal_position;")
        trig = audit_rows("SELECT tgname FROM pg_trigger WHERE "
                          "tgrelid='arv.note_reference'::regclass AND NOT tgisinternal "
                          "ORDER BY tgname;")
        rls = audit_rows("SELECT relrowsecurity::text, relforcerowsecurity::text FROM "
                         "pg_class WHERE oid='arv.note_reference'::regclass;")
        grants = audit("SELECT CASE WHEN 'arv_app=ar/postgres' = ANY (string_to_array("
                       "trim(relacl::text, '{}'), ',')) THEN 'ar' ELSE relacl::text END "
                       "FROM pg_class WHERE oid='arv.note_reference'::regclass;")
        uniq = audit_rows("SELECT conname FROM pg_constraint WHERE conrelid="
                          "'arv.note_reference'::regclass AND contype='u' ORDER BY conname;")
        chk = audit_rows("SELECT conname FROM pg_constraint WHERE conrelid="
                         "'arv.note_reference'::regclass AND contype='c' ORDER BY conname;")
        ok11 = (cols == ["id", "note_id", "note_revision", "ref_kind", "ref_id",
                         "ref_revision", "owner_scope", "actor", "run_id",
                         "input_hash", "idempotency_key", "created_at"]
                and trig == ["note_reference_guard", "note_reference_immutable"]
                and rls == ["true|true"]
                and uniq == ["note_reference_id_owner_scope_key",
                             "note_reference_note_id_note_revision_ref_kind_ref_id_owner__key"]
                and chk == ["note_reference_actor_check",
                            "note_reference_note_revision_check",
                            "note_reference_ref_kind_check",
                            "note_reference_ref_shape_check"]
                and grants == "ar")
        check("NTR-11", ok11,
              "the 0010 schema audits: the exact twelve-column set (identity + the per-revision binding + the version-aware target + provenance); the two triggers (the guard + the immutable append-only); RLS enabled AND FORCED; the two UNIQUE constraints (the id/owner key + the per-revision set semantics); the CHECK constraints (revision >= 1, the kind enum, the actor enum, the ref SHAPE); arv_app holds INSERT + SELECT only",
              "the substrate is the authority the command boundary rides (the 0007/0008/0009 convention — every constraint named, none decorative)")

        # ---- NTR-12 — the tombstone boundary (refs never leak, history keeps all)
        p12 = mk_note("n-12", content="the tombstone subject.",
                      refs=[f"work:{wid_a}"])
        n12 = ack_field(p12, "result_ref")
        revise_note("n-12r", n12, content="the second thinking.",
                    refs=[f"source:{sid_a}"])
        t12 = lifecycle("tombstone_note", "n-12t", n12)
        g_t = qy("get-note", "A", n12)
        h12 = history_rows("A", n12)
        h12r1 = [r for r in h12 if r.get("kind") == "revision" and r.get("revision") == 1]
        h12r2 = [r for r in h12 if r.get("kind") == "revision" and r.get("revision") == 2]
        listed = [ln for ln in qy("list-notes", "A").stdout.splitlines() if ln.strip()]
        s12 = lifecycle("restore_note", "n-12s", n12)
        g12 = typed(qy("get-note", "A", n12))
        ok12 = (t12.returncode == 0
                and g_t.returncode == 1 and "ARV-QRY-003" in g_t.stdout
                and len(h12r1) == 1
                and h12r1[0].get("refs") == [{"kind": "work", "id": wid_a, "revision": None}]
                and len(h12r2) == 1
                and h12r2[0].get("refs") == [{"kind": "source", "id": sid_a, "revision": None}]
                and n12 not in listed
                and s12.returncode == 0 and g12 is not None
                and g12.get("refs") == [{"kind": "source", "id": sid_a, "revision": None}])
        check("NTR-12", ok12,
              "a tombstoned note's ordinary read refuses ARV-QRY-003 with NO refs leak; the governed history retains every revision WITH its own reference set; list-notes hides it; restore returns the current view with its current reference set — the tombstone governs visibility, never the recorded references",
              "tombstone hides from ordinary retrieval while the governed history retains everything (§3.3; the reference rows are part of the retained record)")

        # ---- NTR-13 — the seven-kind write round-trip (P4-D slice two,
        # CLAIM-076: the bookmark + journal_block families join the write
        # vocabulary — the bounded increment CLAIM-075's own not-verified
        # list named; the reference system completes over the seven families)
        pbm = cli(str(REPO / "harness" / "commands.py"), "create_bookmark",
                  "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                  "--idem-key", "bm-A1", "--source-id", sid_a,
                  "--start", str(s1), "--end", str(e1))
        bm1 = ack_field(pbm, "result_ref")
        mbm = cli(str(REPO / "harness" / "commands.py"), "move_bookmark",
                  "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                  "--idem-key", "bm-A1m", "--id", bm1,
                  "--start", str(s2), "--end", str(e2))
        pjb = cli(str(REPO / "harness" / "commands.py"), "journal_block",
                  "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                  "--idem-key", "jb-A1", "--kind", "raw",
                  "--content", "The raw thinking the note references.")
        jb1 = ack_field(pjb, "result_ref").split("@")[0]
        rjb = cli(str(REPO / "harness" / "commands.py"), "revise_journal_block",
                  "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                  "--idem-key", "jb-A1r", "--id", jb1,
                  "--content", "The revised raw thinking.")
        pbmb = cli(str(REPO / "harness" / "commands.py"), "create_bookmark",
                   "--owner", "B", "--actor", "owner", "--client-id", "cli-1",
                   "--idem-key", "bm-B1", "--source-id", sid_b,
                   "--start", str(s1), "--end", str(e1))
        bmb = ack_field(pbmb, "result_ref")
        pjbb = cli(str(REPO / "harness" / "commands.py"), "journal_block",
                   "--owner", "B", "--actor", "owner", "--client-id", "cli-1",
                   "--idem-key", "jb-B1", "--kind", "creative",
                   "--content", "B's private creative block.")
        jbb = ack_field(pjbb, "result_ref").split("@")[0]
        refs7 = [f"work:{wid_a}", f"source:{sid_a}", f"anchor:{anc_a}",
                 f"highlight:{h1}@1", f"note:{nfs}@1",
                 f"bookmark:{bm1}@1", f"journal_block:{jb1}@2"]
        p13 = mk_note("n-13", content="The seven-kind referenced thinking.", refs=refs7)
        n13 = ack_field(p13, "result_ref")
        g13 = typed(qy("get-note", "A", n13))
        rr13 = audit_rows(f"SELECT ref_kind, ref_id, ref_revision::text FROM "
                          f"arv.note_reference WHERE note_id='{n13}' AND note_revision=1 "
                          f"ORDER BY ref_kind, ref_id;")
        # the compose round-trip: the STORED new-kind refs resolve through the
        # ONE surface (CLAIM-075's resolve-reference — pinned bookmark@1 is
        # HISTORICAL after the move to revision 2; journal_block@2 is CURRENT)
        rb = cli(str(REPO / "harness" / "query.py"), "resolve-reference",
                 "--owner", "A", "--ref", f"bookmark:{bm1}@1")
        rj = cli(str(REPO / "harness" / "query.py"), "resolve-reference",
                 "--owner", "A", "--ref", f"journal_block:{jb1}@2")
        bm_ans = json.loads(rb.stdout.splitlines()[0]) if rb.returncode == 0 else None
        jb_ans = json.loads(rj.stdout.splitlines()[0]) if rj.returncode == 0 else None
        # revision 2's OWN new-kind set (the replacement semantics: the pinned
        # pair may be any existing revision — journal_block@1 superseded-but-retained)
        p13r = revise_note("n-13r", n13, content="The second seven-kind thinking.",
                           refs=[f"bookmark:{bm1}@2", f"journal_block:{jb1}@1"])
        g13r = typed(qy("get-note", "A", n13))
        ok13 = (pbm.returncode == 0 and mbm.returncode == 0
                and pjb.returncode == 0 and rjb.returncode == 0
                and p13.returncode == 0 and "status=committed" in p13.stdout
                and g13 is not None and g13.get("refs") == [
                    {"kind": "anchor", "id": anc_a, "revision": None},
                    {"kind": "bookmark", "id": bm1, "revision": 1},
                    {"kind": "highlight", "id": h1, "revision": 1},
                    {"kind": "journal_block", "id": jb1, "revision": 2},
                    {"kind": "note", "id": nfs, "revision": 1},
                    {"kind": "source", "id": sid_a, "revision": None},
                    {"kind": "work", "id": wid_a, "revision": None}]
                and len(rr13) == 7
                and f"bookmark|{bm1}|1" in rr13 and f"journal_block|{jb1}|2" in rr13
                and bm_ans is not None and bm_ans.get("state") == "historical"
                and bm_ans.get("pinned_revision") == 1 and bm_ans.get("current_revision") == 2
                and jb_ans is not None and jb_ans.get("state") == "current"
                and jb_ans.get("revision") == 2
                and p13r.returncode == 0
                and g13r is not None and g13r.get("refs") == [
                    {"kind": "bookmark", "id": bm1, "revision": 2},
                    {"kind": "journal_block", "id": jb1, "revision": 1}])
        check("NTR-13", ok13,
              "the seven-kind write round-trip: the full mixed reference set incl. bookmark@1 + journal_block@2 lands (the per-revision rows + the committed ack); get-note renders the seven-entry version-aware refs array in the canonical order; the STORED new-kind refs resolve through the ONE surface (the pinned bookmark@1 answering historical with current_revision alongside — never a silent retarget; the journal_block@2 answering current); revision 2 carries its OWN new-kind set (the replacement semantics over the new families, the pinned pair at any existing revision)",
              "the reference system is complete over the seven landed families only when a reference to a bookmark or a journal block can be STORED (RTM §2 item 10's @Reference over the entity families; the CLAIM-057 substrate widened, never a second implementation)")

        # ---- NTR-14 — the shape law + the canonical replay for the new kinds
        before14 = audit("SELECT count(*) FROM arv.note;")
        p_bare_bm = mk_note("n-14a", content="x", refs=[f"bookmark:{bm1}"])
        p_bare_jb = mk_note("n-14b", content="x", refs=[f"journal_block:{jb1}"])
        p_nonrev = mk_note("n-14c", content="x", refs=[f"bookmark:{bm1}@x"])
        p_dup = mk_note("n-14d", content="x",
                        refs=[f"bookmark:{bm1}@1", f"bookmark:{bm1}@1"])
        after14 = audit("SELECT count(*) FROM arv.note;")
        p14 = mk_note("n-14e", content="the replay subject.",
                      refs=[f"bookmark:{bm1}@1", f"journal_block:{jb1}@2"])
        n14 = ack_field(p14, "result_ref")
        p14s = note_cmd("create_note", "n-14e", content="the replay subject.",
                        refs=[f"journal_block:{jb1}@2", f"bookmark:{bm1}@1"])
        p14x = note_cmd("create_note", "n-14e", content="the replay subject.",
                        refs=[f"bookmark:{bm1}@1"])
        ok14 = (p_bare_bm.returncode == 1 and "ARV-NTE-006" in p_bare_bm.stdout
                and p_bare_jb.returncode == 1 and "ARV-NTE-006" in p_bare_jb.stdout
                and p_nonrev.returncode == 1 and "ARV-NTE-006" in p_nonrev.stdout
                and p_dup.returncode == 1 and "ARV-NTE-008" in p_dup.stdout
                and after14 == before14
                and p14.returncode == 0
                and p14s.returncode == 0 and ack_field(p14s, "result_ref") == n14
                and p14x.returncode == 1 and "ARV-CMD-409" in p14x.stdout)
        check("NTR-14", ok14,
              "the shape law at the widened boundary: a bare bookmark/journal_block reference (no @rev — version-aware by construction) and a non-digit pin refuse ARV-NTE-006 with zero effect; the duplicate target refuses ARV-NTE-008 (the set semantics over the new kinds); the same logical set in a SHUFFLED CLI order replays under the same idem key (LAW-23 — the canonical body covers the sorted set); a different set under the same key is the ARV-CMD-409 conflict",
              "the grammar is exact and closed: the two new kinds join the revisioned arm (kind:id@rev), never the bare arm — the same substrate law, the same canonical body")

        # ---- NTR-15 — the no-oracle for the new kinds (ARV-NTE-003)
        before15 = audit("SELECT count(*) FROM arv.note;")
        p_abs_bm = mk_note("n-15a", content="x", refs=[f"bookmark:{ghost}@1"])
        p_abs_jb = mk_note("n-15b", content="x", refs=[f"journal_block:{ghost}@1"])
        p_x_bm = mk_note("n-15c", content="x", refs=[f"bookmark:{bmb}@1"])
        p_x_jb = mk_note("n-15d", content="x", refs=[f"journal_block:{jbb}@1"])
        p_rev99 = mk_note("n-15e", content="x", refs=[f"bookmark:{bm1}@99"])
        after15 = audit("SELECT count(*) FROM arv.note;")
        ok15 = (p_abs_bm.returncode == 1 and "ARV-NTE-003" in p_abs_bm.stdout
                and p_abs_jb.returncode == 1 and "ARV-NTE-003" in p_abs_jb.stdout
                and p_x_bm.returncode == 1 and "ARV-NTE-003" in p_x_bm.stdout
                and p_x_jb.returncode == 1 and "ARV-NTE-003" in p_x_jb.stdout
                and p_rev99.returncode == 1 and "ARV-NTE-003" in p_rev99.stdout
                and after15 == before15
                and p_x_bm.stdout.replace(bmb, ghost) == p_abs_bm.stdout
                and p_x_jb.stdout.replace(jbb, ghost) == p_abs_jb.stdout)
        check("NTR-15", ok15,
              "the no-oracle at the widened write boundary: the absent bookmark/journal_block target, another owner's bookmark/journal_block, and a nonexistent revision on a live bookmark are the SAME ARV-NTE-003 refusal — template-normalized byte-equal — with zero effect, never an existence side channel",
              "the caller-scope law composes over the new families identically (RTM §2.5 item 7's never-a-side-channel, both boundaries)")

        # ---- NTR-16 — the substrate backstop (the 0018 widening)
        p16 = mk_note("n-16", content="the backstop subject.")
        n16 = ack_field(p16, "result_ref")
        _cols = ("(id, note_id, note_revision, ref_kind, ref_id, ref_revision, "
                 "owner_scope, actor, run_id, input_hash, idempotency_key, created_at)")
        p_ov = app_sql(f"INSERT INTO arv.note_reference {_cols} VALUES "
                       f"('11111111-1111-4111-8111-111111111111', '{n16}', 1, "
                       f"'reading_list', '{bm1}', NULL, 'A', 'owner', 'run-hostile', "
                       f"'deadbeef', 'hostile-ov', now());")
        p_null_bm = app_sql(f"INSERT INTO arv.note_reference {_cols} VALUES "
                            f"('22222222-2222-4222-8222-222222222222', '{n16}', 1, "
                            f"'bookmark', '{bm1}', NULL, 'A', 'owner', 'run-hostile', "
                            f"'deadbeef', 'hostile-nbm', now());")
        p_null_jb = app_sql(f"INSERT INTO arv.note_reference {_cols} VALUES "
                            f"('33333333-3333-4333-8333-333333333333', '{n16}', 1, "
                            f"'journal_block', '{jb1}', NULL, 'A', 'owner', 'run-hostile', "
                            f"'deadbeef', 'hostile-njb', now());")
        p_ok_bm = app_sql(f"INSERT INTO arv.note_reference {_cols} VALUES "
                          f"('44444444-4444-4444-8444-444444444444', '{n16}', 1, "
                          f"'bookmark', '{bm1}', 1, 'A', 'owner', 'run-hostile', "
                          f"'deadbeef', 'hostile-okbm', now());")
        p_ok_jb = app_sql(f"INSERT INTO arv.note_reference {_cols} VALUES "
                          f"('55555555-5555-4555-8555-555555555555', '{n16}', 1, "
                          f"'journal_block', '{jb1}', 2, 'A', 'owner', 'run-hostile', "
                          f"'deadbeef', 'hostile-okjb', now());")
        p_ghost = app_sql(f"INSERT INTO arv.note_reference {_cols} VALUES "
                          f"('66666666-6666-4666-8666-666666666666', '{n16}', 1, "
                          f"'bookmark', '{ghost}', 1, 'A', 'owner', 'run-hostile', "
                          f"'deadbeef', 'hostile-gh', now());")
        ok16 = (p_ov.returncode != 0
                and "note_reference_ref_kind_check" in p_ov.stderr
                and p_null_bm.returncode != 0
                and "note_reference_ref_shape_check" in p_null_bm.stderr
                and p_null_jb.returncode != 0
                and "note_reference_ref_shape_check" in p_null_jb.stderr
                and p_ok_bm.returncode == 0
                and p_ok_jb.returncode == 0
                and p_ghost.returncode != 0 and "ARV-NTE-003" in p_ghost.stderr)
        check("NTR-16", ok16,
              "the 0018 substrate backstop: the out-of-vocabulary direct INSERT ('reading_list') still refuses the kind CHECK — the widening is exactly the two named kinds, never an open enum; a bookmark/journal_block row without the revision refuses the shape CHECK; the WELL-FORMED direct row for each new kind is ADMITTED — the guard routes the new kinds to THEIR tables (a real bookmark at revision 1 accepted: had the note ELSE arm run, the bookmark uuid would refuse ARV-NTE-007/003 — the routing proven by acceptance, not by prose); the ghost target refuses ARV-NTE-003 at the substrate (both boundaries, never one alone)",
              "the substrate mirrors the command surface exactly (the 0007/0008 convention); the widened guard arms are part of the widening, never a vocabulary-only change")

        print()
        if FAILS:
            print(f"RED — the P3-06 reference suite fails: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-06 acceptance suite, slice two (NTR-01..16) passes")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
