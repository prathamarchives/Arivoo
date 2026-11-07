#!/usr/bin/env python3
"""harness/tests/test_library.py — P4-C slice one acceptance suite (CLAIM-070,
the library + current-reading state over the EXISTING substrate; PLAN's
elaborated P4-C slice one card; record 62 §2).
Red-first (LAW-11): at CLAIM-069's merged head 9c138a0 the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the list-library arm and the
get-reading-state arm are absent from query.py.

THE CONTRACT (P4-C slice one's letter, record 62 §2): the library + the
current-reading state on the LANDED substrate — no new table, no second
position path, no reader-client work (P4-B's separate repo):

  the library list      the owner's imported sources as a stable, bounded,
                        paginated list — the list-library read arm on the
                        P4-00b contract (the versioned header, the '# more='
                        truth markers, the keyset cursor, the api_version
                        field); RLS the owner boundary; membership derives
                        from arv.source (rows are BORN complete at import —
                        a failed import never creates a source row; the
                        dead-letter is the journal's, not the library's)
  the current-reading   ONE read arm (get-reading-state) deriving the
  state                 owner's reading surface from the LANDED position
                        rows: the sources with a saved position (the
                        last-saved position + its generation binding + the
                        matches flag) AND the no-position sources (the
                        honest not-yet-open state) — the derived
                        current-reading view, NEVER a second position path:
                        every row equals get-position's own answer for that
                        source (the no-drift law, pinned at byte level)

Cases (the LIB registry; each pin's full statement lives at its check()):
  LIB-01 the list-library arm at the real boundary: the owner's sources as
         one id per line between the version header and the '# more='
         marker; every listed id reads back through get-source (the ids are
         real); the empty owner answers header + more=false ALONE (never
         silence — the P4-00a lesson held on the library)
  LIB-02 the bounds + the pagination on BOTH new arms (the P4-00b
         contract): --limit (default 100, bounds 1..1000) + --after (the
         keyset cursor); a small page answers its rows + more=true; the
         paged walk's union equals the full walk, monotone, no dups;
         --limit 0 / 1001 / non-integer and a non-uuid --after refuse with
         the typed ARV-QRY-004 (exit 1, zero effect — the refusal prints
         the FAIL line + the repair hint, never a header, never rows)
  LIB-03 the owner isolation: owner B's list-library and get-reading-state
         carry ONLY B's sources (never A's ids, never A's rows); B's rows
         obey the same no-drift law (B's row == B's get-position answer);
         the empty owner's reading state answers header + more=false alone
  LIB-04 the current-reading state derived from the LANDED position rows:
         the source with two saves shows the NEWEST (the last-saved
         position, max save_ordinal); the once-saved source shows its save;
         the never-saved sources answer the typed no_position_saved state
         (never silence, never a failure); every saved row carries the
         generation binding (saved_generation_id + current_generation_id +
         generation_matches=true); THE NO-SECOND-PATH LAW: every row of the
         full walk equals get-position's own answer for that source (exact
         JSON equality — the derived view rides the SAME position path,
         never a drifting second implementation); the rows are ordered by
         source id (the keyset order)
  LIB-05 the generation binding honest across a re-extraction + the
         liveness of the derived view: after a re-extraction supersedes the
         saved generation, the reading-state row keeps the SAVED offsets +
         saved_generation_id == the ORIGINAL + current_generation_id == the
         NEW + generation_matches=false — NEVER a silent retarget at the
         surface level; the no-second-path law re-held for the re-extracted
         source; a NEW save after the re-extraction binds the CURRENT
         generation (matches=true); a fresh save on another source appears
         in the NEXT read (the view is DERIVED live, never a materialized
         copy)
  LIB-06 the reserved surface made real + the no-new-table law: capability
         .py's surfaces registry carries the library/current-reading row
         naming the LANDED verbs (list-library + get-reading-state) with
         owner_phase P4-C and the reader-client exclusion (the separate
         repo); NO new table backs the view (the arv schema carries no
         library/current_reading/reading_state relation — the view derives
         from the landed rows); the arm's saved-row set equals the audit's
         distinct positioned-source set (the derivation is the substrate's
         own); the source-open/position row still present (CAP-03's
         regression); api_version=1 on every row and every header

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no session/dwell events
(D-010 — the following P4-C slice); no reading lists/collections beyond the
library itself (their own increment); no reader-client work (P4-B's repo).

Run: python3 harness/tests/test_library.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pg  # noqa: E402

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): BOTH new read arms are absent
# at the RED tree — the cheapest honest probe per surface (LAW-11; the
# POS precedent's --help form).
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "list-library", "--help"], capture_output=True, text=True)
_absent_list = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "get-reading-state", "--owner", "A"],
                         capture_output=True, text=True, timeout=60)
_absent_state = "invalid choice" in _probe2.stderr
if _absent_list or _absent_state:
    print(f"FAIL ARV-TEST-000: the P4-C slice one library machinery is absent "
          f"(machinery-absent class; list-library arm absent: {_absent_list}; "
          f"get-reading-state arm absent: {_absent_state}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None
# the corpus: a reading text with several paragraphs — the derived view the
# reader positions into (decoded-text coordinates)
TEXT = ("The opening paragraph establishes the ground.\n"
        "The second paragraph carries the first resting point.\n"
        "The third paragraph carries the moved resting point.\n"
        "The fourth paragraph closes the reading.\n")


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
        a += ["--crash-at", crash_at]
    return cli(*a, *args)


def extract(key: str, source_id: str, owner: str = "A") -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor", "owner",
               "--client-id", "cli-1", "--idem-key", key, "--source-id", source_id)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


def save(source_id: str, start: int, end: int, key: str, owner="A") -> subprocess.CompletedProcess:
    return cmd("save_position", "--source-id", source_id,
               "--start", str(start), "--end", str(end), key=key, owner=owner)


def get_pos(owner: str, source_id: str) -> subprocess.CompletedProcess:
    return query("get-position", "--owner", owner, "--source", source_id)


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


def ids_of(r: subprocess.CompletedProcess) -> list:
    return [ln for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4c1")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4c1-"))

        # the fixtures: FIVE sources for owner A (two extracted with saved
        # positions — src1 twice, src2 once; three never-saved — src3
        # extracted-but-never-opened, src4/src5 imported-only) + ONE for
        # owner B (extracted + saved) — the isolation fixture.  Owner C
        # imports NOTHING (the empty owner).
        f1 = tmp / "reading.txt"
        f1.write_text(TEXT, encoding="utf-8")
        r_i1 = cmd("import_source", "--title", "The Reading Text",
                   "--file", str(f1), key="imp-1")
        src1 = ref_of(r_i1)
        r_e1 = extract("ext-1", src1)
        f2 = tmp / "second.txt"
        f2.write_text("A second document entirely.\nIts paragraphs are its own.\n",
                      encoding="utf-8")
        r_i2 = cmd("import_source", "--title", "The Second Text",
                   "--file", str(f2), key="imp-2")
        src2 = ref_of(r_i2)
        extract("ext-2", src2)
        f3 = tmp / "third.txt"
        f3.write_text("Imported and extracted, never opened.\n", encoding="utf-8")
        r_i3 = cmd("import_source", "--title", "The Third Text",
                   "--file", str(f3), key="imp-3")
        src3 = ref_of(r_i3)
        extract("ext-3", src3)
        f4 = tmp / "fourth.txt"
        f4.write_text("Imported only, the fourth.\n", encoding="utf-8")
        r_i4 = cmd("import_source", "--title", "The Fourth Text",
                   "--file", str(f4), key="imp-4")
        src4 = ref_of(r_i4)
        f5 = tmp / "fifth.txt"
        f5.write_text("Imported only, the fifth.\n", encoding="utf-8")
        r_i5 = cmd("import_source", "--title", "The Fifth Text",
                   "--file", str(f5), key="imp-5")
        src5 = ref_of(r_i5)
        fb = tmp / "btext.txt"
        fb.write_text("B's own document.\n", encoding="utf-8")
        r_ib = cmd("import_source", "--title", "The B Text",
                   "--file", str(fb), key="imp-b", owner="B")
        srcB = ref_of(r_ib)
        extract("ext-b", srcB, owner="B")
        gen1 = jline(cap("measure", "--owner", "A", "--source", src1)).get("generation_id", "")
        gen2 = jline(cap("measure", "--owner", "A", "--source", src2)).get("generation_id", "")
        genB = jline(cap("measure", "--owner", "B", "--source", srcB)).get("generation_id", "")
        # the positions: src1 TWICE (the newest wins), src2 once, B's once
        save(src1, len(TEXT) // 3, len(TEXT) // 2, key="pos-1")
        save(src1, 0, 10, key="pos-2")
        save(src2, 5, 15, key="pos-s2")
        save(srcB, 0, 4, key="pos-b", owner="B")
        all_a = sorted([src1, src2, src3, src4, src5])

        # ---- LIB-01 — the list-library arm at the real boundary
        r_l1 = query("list-library", "--owner", "A")
        l1_lines = r_l1.stdout.splitlines()
        l1_ids = ids_of(r_l1)
        # every listed id reads back through get-source (the ids are real)
        readback = all(query("get-source", "--owner", "A", "--id", i).returncode == 0
                       for i in l1_ids)
        # the empty owner: header + more=false ALONE (never silence)
        r_lc = query("list-library", "--owner", "C")
        lc_lines = r_lc.stdout.splitlines()
        ok1 = (r_l1.returncode == 0
               and l1_lines[0] == "# api_version=1"
               and l1_lines[-1] == "# more=false"
               and l1_ids == all_a
               and len(set(l1_ids)) == len(l1_ids)
               and readback
               and r_lc.returncode == 0
               and lc_lines == ["# api_version=1", "# more=false"])
        check("LIB-01", ok1,
              "the list-library arm at the real boundary: the owner's sources as one id per "
              "line between the version header and the '# more=' marker (all five, the keyset "
              "order, no dups); every listed id reads back through get-source (the ids are "
              "real); the empty owner answers header + more=false ALONE (never silence — the "
              "P4-00a lesson held on the library)",
              "harness/query.py list-library on the P4-00b list contract — the _list_arm "
              "machinery over arv.source (RLS the owner boundary; membership derives from the "
              "source rows, born complete at import)")

        # ---- LIB-02 — the bounds + the pagination on BOTH new arms
        r_l2 = query("list-library", "--owner", "A", "--limit", "2")
        l2_ids = ids_of(r_l2)
        # the paged walk: --limit 2 + --after until more=false
        walk, cursor, more = [], None, True
        while more:
            args = ["list-library", "--owner", "A", "--limit", "2"]
            if cursor:
                args += ["--after", cursor]
            r_w = query(*args)
            w_ids = ids_of(r_w)
            walk += w_ids
            more = r_w.stdout.splitlines()[-1] == "# more=true"
            cursor = w_ids[-1] if w_ids else None
        monotone = all(walk[i] < walk[i + 1] for i in range(len(walk) - 1))
        # the reading-state arm's own page + walk
        r_r2 = query("get-reading-state", "--owner", "A", "--limit", "2")
        r2_rows = jlines(r_r2)
        rwalk, cursor, more = [], None, True
        while more:
            args = ["get-reading-state", "--owner", "A", "--limit", "2"]
            if cursor:
                args += ["--after", cursor]
            r_w = query(*args)
            w_rows = jlines(r_w)
            rwalk += w_rows
            more = r_w.stdout.splitlines()[-1] == "# more=true"
            cursor = w_rows[-1]["source_id"] if w_rows else None
        r_ids = [row["source_id"] for row in rwalk]
        r_monotone = all(r_ids[i] < r_ids[i + 1] for i in range(len(r_ids) - 1))
        # the typed bounds refusals on BOTH arms (the frozen shape: exit 1 +
        # the FAIL prefix + zero effect — no header, never rows)
        refusals = []
        for arm, extra in (("list-library", []), ("get-reading-state", [])):
            for bad in (["--limit", "0"], ["--limit", "1001"], ["--limit", "abc"],
                        ["--after", "not-a-uuid"]):
                r_bad = query(arm, "--owner", "A", *extra, *bad)
                refusals.append(r_bad.returncode == 1
                                and r_bad.stdout.startswith("FAIL ARV-QRY-004:")
                                and "# api_version" not in r_bad.stdout)
        ok2 = (r_l2.returncode == 0
               and len(l2_ids) == 2
               and r_l2.stdout.splitlines()[-1] == "# more=true"
               and l2_ids == all_a[:2]
               and walk == all_a
               and monotone
               and r_r2.returncode == 0
               and len(r2_rows) == 2
               and r_r2.stdout.splitlines()[0] == "# api_version=1"
               and r_r2.stdout.splitlines()[-1] == "# more=true"
               and [row["source_id"] for row in r2_rows] == all_a[:2]
               and rwalk and [row["source_id"] for row in rwalk] == all_a
               and r_monotone
               and all(refusals))
        check("LIB-02", ok2,
              "the bounds + the pagination on BOTH new arms (the P4-00b contract): --limit "
              "(default 100, bounds 1..1000) + --after (the keyset cursor); a small page "
              "answers its rows + more=true; the paged walk's union equals the full walk "
              "(all five), monotone, no dups — on list-library AND get-reading-state; "
              "--limit 0 / 1001 / non-integer and a non-uuid --after refuse with the typed "
              "ARV-QRY-004 (exit 1, zero effect — the FAIL line + the repair hint, never a "
              "header, never rows)",
              "the shared bounds machinery at the read boundary (the _list_arm validation "
              "class) — both new arms ride the SAME typed refusal, never a clamp, never an "
              "unbounded dump")

        # ---- LIB-03 — the owner isolation
        r_lb = query("list-library", "--owner", "B")
        lb_ids = ids_of(r_lb)
        r_rb = query("get-reading-state", "--owner", "B")
        rb_rows = jlines(r_rb)
        b_row_ok = bool(rb_rows) and all(
            row == jline(get_pos("B", row["source_id"])) for row in rb_rows)
        # the empty owner's reading state: header + more=false ALONE
        r_rc = query("get-reading-state", "--owner", "C")
        rc_lines = r_rc.stdout.splitlines()
        ok3 = (r_lb.returncode == 0
               and lb_ids == [srcB]
               and not any(i in (src1, src2, src3, src4, src5) for i in lb_ids)
               and r_rb.returncode == 0
               and [row["source_id"] for row in rb_rows] == [srcB]
               and b_row_ok
               and r_rc.returncode == 0
               and rc_lines == ["# api_version=1", "# more=false"])
        check("LIB-03", ok3,
              "the owner isolation: owner B's list-library and get-reading-state carry ONLY "
              "B's sources (B's one source, never A's ids or rows — RLS the boundary); B's "
              "rows obey the same no-drift law (B's row == B's get-position answer); the "
              "empty owner's reading state answers header + more=false ALONE (never silence)",
              "the owner-scoped read (SET app.current_owner + the RLS policy) — the same "
              "machinery every read arm rides; never a filter bolted onto the new arms")

        # ---- LIB-04 — the current-reading state derived from the LANDED rows
        r_r1 = query("get-reading-state", "--owner", "A")
        r1_rows = jlines(r_r1)
        rmap = {row.get("source_id"): row for row in r1_rows}
        # THE NO-SECOND-PATH LAW: every row equals get-position's own answer
        nodrift = all(row == jline(get_pos("A", row["source_id"])) for row in r1_rows)
        ok4 = (r_r1.returncode == 0
               and r_r1.stdout.splitlines()[0] == "# api_version=1"
               and r_r1.stdout.splitlines()[-1] == "# more=false"
               and [row["source_id"] for row in r1_rows] == all_a
               and len(r1_rows) == 5
               and rmap.get(src1, {}).get("state") == "saved"
               and rmap[src1].get("save_ordinal") == 2
               and rmap[src1].get("start_off") == 0
               and rmap[src1].get("end_off") == 10
               and rmap[src1].get("saved_generation_id") == gen1
               and rmap[src1].get("current_generation_id") == gen1
               and rmap[src1].get("generation_matches") is True
               and rmap.get(src2, {}).get("state") == "saved"
               and rmap[src2].get("save_ordinal") == 1
               and rmap[src2].get("start_off") == 5
               and rmap[src2].get("end_off") == 15
               and rmap[src2].get("saved_generation_id") == gen2
               and rmap[src2].get("generation_matches") is True
               and all(rmap.get(s, {}).get("state") == "no_position_saved"
                       for s in (src3, src4, src5))
               and all(rmap[s].get("api_version") == 1 for s in all_a)
               and nodrift)
        check("LIB-04", ok4,
              "the current-reading state derived from the LANDED position rows: the twice-"
              "saved source shows the NEWEST position (save_ordinal=2, the last-saved "
              "offsets); the once-saved source shows its save; the never-saved sources "
              "answer the typed no_position_saved state (never silence, never a failure); "
              "every saved row carries the generation binding (saved_generation_id + "
              "current_generation_id + generation_matches=true); THE NO-SECOND-PATH LAW: "
              "every row of the full walk equals get-position's own answer for that source "
              "(exact JSON equality — the derived view rides the SAME position path); the "
              "rows ordered by source id, api_version on every row",
              "harness/query.py get-reading-state — the set-shaped derivation over "
              "arv.source + arv.reading_position + the current generation, ONE shared row "
              "builder with get-position (never a second position implementation)")

        # ---- LIB-05 — the binding honest across a re-extraction + liveness
        r_re = extract("ext-1b", src1)  # the re-extraction: a NEW current generation
        gen_new = jline(cap("measure", "--owner", "A", "--source", src1)).get("generation_id", "")
        r_r3 = query("get-reading-state", "--owner", "A")
        r3_rows = jlines(r_r3)
        r3map = {row.get("source_id"): row for row in r3_rows}
        row1 = r3map.get(src1, {})
        nodrift_re = row1 == jline(get_pos("A", src1))
        # a NEW save after the re-extraction binds the CURRENT generation
        r_s3 = save(src1, 40, 50, key="pos-1c")
        # liveness: a fresh save on ANOTHER source appears in the NEXT read
        r_s4 = save(src2, 20, 30, key="pos-s2b")
        r_r4 = query("get-reading-state", "--owner", "A")
        r4_rows = jlines(r_r4)
        r4map = {row.get("source_id"): row for row in r4_rows}
        ok5 = (r_re.returncode == 0
               and gen_new and gen_new != gen1
               and row1.get("start_off") == 0 and row1.get("end_off") == 10
               and row1.get("save_ordinal") == 2
               and row1.get("saved_generation_id") == gen1
               and row1.get("current_generation_id") == gen_new
               and row1.get("generation_matches") is False
               and nodrift_re
               and r_s3.returncode == 0 and "save=3" in r_s3.stdout
               and r4map.get(src1, {}).get("save_ordinal") == 3
               and r4map[src1].get("saved_generation_id") == gen_new
               and r4map[src1].get("generation_matches") is True
               and r_s4.returncode == 0 and "save=2" in r_s4.stdout
               and r4map.get(src2, {}).get("save_ordinal") == 2
               and r4map[src2].get("start_off") == 20
               and r4map[src2].get("end_off") == 30)
        check("LIB-05", ok5,
              "the generation binding honest across a re-extraction + the liveness of the "
              "derived view: after a re-extraction supersedes the saved generation, the "
              "reading-state row keeps the SAVED offsets + saved_generation_id == the "
              "ORIGINAL + current_generation_id == the NEW + generation_matches=false — "
              "NEVER a silent retarget at the surface level; the no-second-path law re-held "
              "for the re-extracted source (the row still equals get-position's answer); a "
              "NEW save after the re-extraction binds the CURRENT generation (save=3, "
              "matches=true); a fresh save on another source appears in the NEXT read "
              "(save=2, the new offsets — the view is DERIVED live, never a materialized "
              "copy)",
              "the set-shaped read derives at invocation time from the position rows + the "
              "current generation — the same serving-generation binding get-position "
              "carries, never a second binding logic")

        # ---- LIB-06 — the reserved surface + the no-new-table law
        r_sur = cap("surfaces")
        srows = jlines(r_sur)
        lib_row = next((row for row in srows
                        if row.get("surface") == "library/current-reading"), {})
        pos_row = next((row for row in srows
                        if row.get("surface") == "source-open/position"), {})
        # the no-new-table law: the arv schema carries no library relation
        no_table = audit("SELECT count(*) FROM information_schema.tables "
                         "WHERE table_schema='arv' AND table_name IN "
                         "('library', 'current_reading', 'reading_state');")
        # the derivation is the substrate's own: the arm's saved-row set ==
        # the audit's distinct positioned-source set for owner A
        r_r5 = query("get-reading-state", "--owner", "A")
        r5_saved = {row["source_id"] for row in jlines(r_r5)
                    if row.get("state") == "saved"}
        audit_saved = set(audit("SELECT DISTINCT source_id FROM arv.reading_position "
                                "WHERE owner_scope = 'A';").split())
        ok6 = (r_sur.returncode == 0
               and all(row.get("api_version") == 1 for row in srows)
               and lib_row.get("owner_phase") == "P4-C"
               and "list-library" in str(lib_row.get("reservation", ""))
               and "get-reading-state" in str(lib_row.get("reservation", ""))
               and "separate repo" in str(lib_row.get("reservation", ""))
               and pos_row.get("owner_phase") == "P4-A/B"
               and no_table == "0"
               and r5_saved == audit_saved
               and r5_saved == {src1, src2})
        check("LIB-06", ok6,
              "the reserved surface made real + the no-new-table law: capability.py's "
              "surfaces registry carries the library/current-reading row naming the LANDED "
              "verbs (list-library + get-reading-state) with owner_phase P4-C and the "
              "reader-client exclusion (the separate repo); NO new table backs the view "
              "(the arv schema carries no library/current_reading/reading_state relation — "
              "the view derives from the landed rows); the arm's saved-row set equals the "
              "audit's distinct positioned-source set (the derivation is the substrate's "
              "own); the source-open/position row still present (CAP-03's regression); "
              "api_version=1 on every row and every header",
              "harness/capability.py's RESERVED_SURFACES registry + the derivation over "
              "the LANDED substrate (arv.source + arv.reading_position + the current "
              "generation) — never a materialized second store")

        if FAILS:
            print(f"\nLIBRARY SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the library + current-reading contract is broken or unimplemented)")
            return 1
        print("\nLIBRARY SUITE GREEN — LIB-01..06 (the library + current-reading state: "
              "the bounded paginated library arm, the derived reading surface with the "
              "generation binding honest, the no-second-path law pinned at byte level)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
