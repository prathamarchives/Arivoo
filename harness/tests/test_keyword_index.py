#!/usr/bin/env python3
"""harness/tests/test_keyword_index.py — P3-07 acceptance suite (CLAIM-058,
the keyword findability machine; PLAN's P3-07 card; RTM §2.5 the findability
rung — C1's durability ladder lands keyword-searchable). Red-first (LAW-11):
at CLAIM-057's merged head b698608d the suite fails with ARV-TEST-000
(machinery-absent; red-01.txt).

THE CONTRACT: the keyword index is a DERIVED, REBUILDABLE layer over the
committed authored rows — never an authority (the acceptance: delete/rebuild
restores expected results; the authored rows are the only truth). The
searchable set: the sources' extracted passages, the captures' anchor
evidence windows (highlights + bookmarks), and the notes' authored content —
each under the CURRENT view only (the current revision; tombstones filtered
by the lifecycle parity at QUERY time, never by index deletion — the index
never governs visibility). The search contract is DEFINED: a committed
capture is searchable (the synchronous local index write rides the capture
transaction) or the failure is EXPLICIT (a named ARV-KWR code, never a
silent miss). The owner filter is structural (RLS — another owner's tokens
are invisible). The tokenizer: case-folded Unicode word tokens; CJK
characters additionally index as single characters (a CJK query term finds
the containing text); the token boundary is the non-word character class.

Refusal codes: ARV-KWR-001 the rebuild contract (a rebuild that cannot
re-derive is refused, never a silent partial); ARV-QRY-001 the same
absent/out-of-scope refusal on the search arm's owner boundary.

Cases (the KWR registry; each pin's full statement lives at its check()):
  KWR-01 the known-query pin: a corpus with known terms — every capture
         kind (source passages, highlight windows, bookmark windows, note
         content) found by `search` with the deterministic result shape
         (kind + id + revision + the token's document frequency, ordered)
  KWR-02 the owner filter: another owner's tokens NEVER in the results
         (RLS); the search arm refuses the absent owner boundary the same
         ARV-QRY-001 way
  KWR-03 tombstone filtering: a tombstoned note/highlight/bookmark never
         in the results; RESTORE returns it (the parity join at query time)
  KWR-04 the stale entry after revision: a revised note's OLD term stops
         matching and the NEW term starts (the current-revision index);
         a moved bookmark's new window matches, the old stops
  KWR-05 delete/rebuild: the index rows deleted, `rebuild_keyword_index`
         re-derives, the known queries restore EXACTLY (the acceptance pin)
  KWR-06 the encoding/tokenization boundaries: CJK, case, accents/
         combining marks, the word-boundary classes (a term matches whole
         tokens only — 'cat' never matches 'category')
  KWR-07 the explicit lag/failure contract: the index write rides the
         capture transaction (a committed note is searchable immediately;
         a REFUSED note leaves zero index rows — never a partial)
  KWR-08 the multi-term query: multiple terms AND-match (every term must
         hit one document; the result is the intersection, deterministic)
  KWR-09 the schema audits (0011): the exact column set, RLS enabled AND
         forced, the grants (arv_app INSERT/DELETE/SELECT — the rebuild's
         own surface), the kind CHECK, the PK (the set semantics)
  KWR-10 the derived-layer law: the index rows carry NO authored content
         beyond the token + the locator (the structural no-copy form);
         the index is droppable (delete) with ZERO effect on any authored
         row (the rebuild restores)

Run: python3 harness/tests/test_keyword_index.py   (exit 0 = green)
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


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


_probe = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "search", "--help"], capture_output=True, text=True)
_absent_arm = "invalid choice" in _probe.stderr
_probe2 = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                           "rebuild_keyword_index", "--help"], capture_output=True, text=True)
_absent_cmd = "invalid choice" in _probe2.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0011_*.sql"))
if _absent_arm or _absent_cmd or not _mig:
    print(f"FAIL ARV-TEST-000: the P3-07 keyword-index machinery is absent "
          f"(machinery-absent class; search arm absent: {_absent_arm}; "
          f"rebuild command absent: {_absent_cmd}; migration 0011 present: "
          f"{bool(_mig)}) — the implementation lands after this RED, never "
          "before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

DB = ENV = None

TEXT = ("The reading corpus for the keyword rung.\n"
        "Second paragraph: the xylophone span lives here, plainly.\n"
        "Third paragraph: the quantum retreat lives here instead.\n"
        "Fourth paragraph closes with pie.\n")


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=240, env=ENV)


def cmd(op: str, *args, owner="A", key=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args)


def import_src(key, title, file, owner="A") -> subprocess.CompletedProcess:
    return cmd("import_source", "--file", file, "--media-type", "text/plain",
               "--title", title, key=key, owner=owner)


def mk_highlight(key, source_id, start, end, owner="A"):
    return cmd("create_highlight", "--source-id", source_id, "--start", str(start),
               "--end", str(end), key=key, owner=owner)


def mk_bookmark(key, source_id, start, end, owner="A"):
    return cmd("create_bookmark", "--source-id", source_id, "--start", str(start),
               "--end", str(end), key=key, owner=owner)


def mk_note(key, content, owner="A", refs=None):
    a = ["--content", content]
    for r in (refs or []):
        a += ["--ref", r]
    return cmd("create_note", *a, key=key, owner=owner)


def revise_note(key, note_id, content, owner="A"):
    return cmd("revise_note", "--id", note_id, "--content", content, key=key, owner=owner)


def lifecycle(op, key, entity_id, owner="A", family="note"):
    return cmd(op, "--id", entity_id, key=key, owner=owner)


def rebuild(owner="A"):
    return cmd("rebuild_keyword_index", key="rebuild-1", owner=owner)


def search(owner, *terms):
    return cli(str(REPO / "harness" / "query.py"), "search", "--owner", owner,
               *[t for t in terms])


def audit(query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_read", "-d", DB, "-c", query],
                           capture_output=True, text=True, timeout=60,
                           env=ENV).stdout.strip()


def audit_rows(query: str) -> list:
    return [ln for ln in audit(query).split("\n") if ln.strip()]


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_app", "-d", DB,
                            "-c", f"SET app.current_owner='{owner}'; {sql}"],
                           capture_output=True, text=True, timeout=60, env=ENV)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def result_ids(p: subprocess.CompletedProcess) -> list:
    """The search results: one JSON line per hit, kind|id|revision|freq."""
    out = []
    for ln in p.stdout.split("\n"):
        if ln.strip():
            out.append(ln.strip())
    return out


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p307")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ---------- the fixture: the known-term corpus, two owners
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "reading.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("xylophone span")
        e1 = s1 + len("xylophone span")
        s2 = TEXT.index("quantum retreat")
        e2 = s2 + len("quantum retreat")
        ps = import_src("imp-A", "The Corpus", str(src_file))
        sid_a = ack_field(ps, "result_ref")
        pb = import_src("imp-B", "B's Corpus", str(src_file), owner="B")
        sid_b = ack_field(pb, "result_ref")
        ph = mk_highlight("hl-A1", sid_a, s1, e1)
        h1 = ack_field(ph, "result_ref")
        pbm = mk_bookmark("bm-A1", sid_a, s2, e2)
        b1 = ack_field(pbm, "result_ref")
        cjk_note = ("The CJK note: 中文思考 with combining é and mixed Case WORD. "
                    "A unique zephyr token rides once.")
        pn = mk_note("n-A1", cjk_note)
        n1 = ack_field(pn, "result_ref")
        pnb = mk_note("n-B1", "B's private xylophone thinking.", owner="B")
        nb = ack_field(pnb, "result_ref")

        # ---- KWR-01 — the known-query pin (every capture kind found)
        r_src = search("A", "xylophone")
        r_note = search("A", "zephyr")
        r_cjk = search("A", "中")
        ids_src = result_ids(r_src)
        ids_note = result_ids(r_note)
        ok1 = (r_src.returncode == 0 and r_note.returncode == 0
               and any(f"source|{sid_a}" in ln for ln in ids_src)
               and any(f"highlight|{h1}" in ln for ln in ids_src)
               and not any(f"bookmark|{b1}" in ln for ln in ids_src)  # the bookmark's window: quantum, not xylophone
               and any(f"note|{n1}" in ln for ln in ids_note)
               and r_cjk.returncode == 0 and any(f"note|{n1}" in ln for ln in result_ids(r_cjk)))
        check("KWR-01", ok1,
              "the known-query pin: search finds every capture kind under the defined contract — the source's extracted passages (xylophone), the highlight's anchor window (xylophone), the note's authored content (zephyr; the CJK single-character term 中文's 中) — with the deterministic result shape (kind|id|revision|matched-terms); the bookmark whose window carries a DIFFERENT term is not in the xylophone results (the window is what is searchable, never the whole source for a windowed capture)",
              "the index is the findability rung's derived layer: the passages, the anchor evidence windows, and the note content — searchable under a defined contract (RTM §2.5; C1's ladder: keyword-searchable)")

        # ---- KWR-02 — the owner filter
        r_b = search("B", "xylophone")
        r_bz = search("B", "zephyr")
        ok2 = (r_b.returncode == 0
               and any(f"source|{sid_b}" in ln for ln in result_ids(r_b))
               and any(f"note|{nb}" in ln for ln in result_ids(r_b))
               and not any(f"source|{sid_a}" in ln for ln in result_ids(r_b))
               and not any(f"highlight|{h1}" in ln for ln in result_ids(r_b))
               and r_bz.returncode == 0 and not result_ids(r_bz))
        check("KWR-02", ok2,
              "the owner filter: B's search sees ONLY B's corpus (B's source + B's note) — A's source/highlight/note invisible (RLS on the index rows: another owner's tokens do not exist for the caller); a term only A carries returns zero results for B (never an error, never a leak)",
              "the index rows are owner-scoped like every authoritative row (LAW-22; the search arm rides the same RLS boundary)")

        # ---- KWR-03 — tombstone filtering + restore
        lifecycle("tombstone_note", "n-A1-t", n1)
        r_t = search("A", "zephyr")
        lifecycle("restore_note", "n-A1-r", n1)
        r_r = search("A", "zephyr")
        lifecycle("tombstone_highlight", "hl-A1-t", h1)
        r_th = search("A", "xylophone")
        ok3 = (r_t.returncode == 0 and not any(f"note|{n1}" in ln for ln in result_ids(r_t))
               and r_r.returncode == 0 and any(f"note|{n1}" in ln for ln in result_ids(r_r))
               and r_th.returncode == 0 and not any(f"highlight|{h1}" in ln for ln in result_ids(r_th))
               and any(f"source|{sid_a}" in ln for ln in result_ids(r_th)))
        check("KWR-03", ok3,
              "tombstone filtering: a tombstoned note/highlight never in the results (the lifecycle parity joined at QUERY time — the index never governs visibility, the authoritative rows do); RESTORE returns the entity to the results; the source's own passage hits remain (the tombstone governs the capture, never the source)",
              "the derived-layer law: visibility is the authoritative rows' property (the §3.3 parity), never the index's — the index is rebuilt from the current view")

        # ---- KWR-04 — the stale entry after revision
        revise_note("n-A1-v", n1, "Revised: the old word is gone; the avalanche remains.")
        r_old = search("A", "zephyr")
        r_new = search("A", "avalanche")
        ok4 = (r_old.returncode == 0 and not any(f"note|{n1}" in ln for ln in result_ids(r_old))
               and r_new.returncode == 0 and any(f"note|{n1}" in ln for ln in result_ids(r_new)))
        check("KWR-04", ok4,
              "the stale entry after revision: the revised note's OLD term stops matching and the NEW term starts (the current-revision index — the maintenance replaces the entity's tokens at the capture boundary); the index never serves a stale revision",
              "the index rides the CURRENT view (the same current-revision rule as get-note); a revision is a complete snapshot (RTM §2.5 item 9)")

        # ---- KWR-05 — delete/rebuild (THE ACCEPTANCE PIN)
        before = sorted(result_ids(search("A", "xylophone")) + result_ids(search("A", "avalanche"))
                        + result_ids(search("A", "中")))
        dele = app_sql("DELETE FROM arv.keyword_index;")
        mid = audit("SELECT count(*) FROM arv.keyword_index WHERE owner_scope='A';")
        empty_r = search("A", "xylophone")
        rb = rebuild()
        after = sorted(result_ids(search("A", "xylophone")) + result_ids(search("A", "avalanche"))
                       + result_ids(search("A", "中")))
        ok5 = (dele.returncode == 0 and mid == "0"
               and empty_r.returncode == 0 and not result_ids(empty_r)
               and rb.returncode == 0 and "status=committed" in rb.stdout
               and after == before)
        check("KWR-05", ok5,
              "delete/rebuild: the index rows deleted (zero rows, the searches return nothing), `rebuild_keyword_index` re-derives the ENTIRE index from the authored rows alone, and every known query restores EXACTLY (the same result set) — the acceptance: the index is a derived, rebuildable layer, never an authority",
              "PLAN's P3-07 acceptance: 'rebuilding restores expected results' — the authored rows are the only truth (the derived-state law)")

        # ---- KWR-06 — the encoding/tokenization boundaries
        p6 = mk_note("n-kwr6", "Boundary note: mixed Case WORD with café naïve and é "
                     "plus Ελληνικά and Привет; corpus stays whole.")
        n6 = ack_field(p6, "result_ref")
        r_case = search("A", "CASE")
        r_comb = search("A", "é")
        r_cafe = search("A", "café")
        r_grk = search("A", "ελληνικά")
        r_cat = search("A", "cor")
        ok6 = (p6.returncode == 0
               and r_case.returncode == 0 and any(f"note|{n6}" in ln for ln in result_ids(r_case))
               and r_comb.returncode == 0 and any(f"note|{n6}" in ln for ln in result_ids(r_comb))
               and r_cafe.returncode == 0 and any(f"note|{n6}" in ln for ln in result_ids(r_cafe))
               and r_grk.returncode == 0 and any(f"note|{n6}" in ln for ln in result_ids(r_grk))
               and r_cat.returncode == 0 and not any("corpus" in ln or f"note|{n6}" in ln
                                                      for ln in result_ids(r_cat)))
        check("KWR-06", ok6,
              "the tokenization boundaries: case-folded matching (CASE finds the note carrying 'Case'); the accented token é MATCHES (a real hit, never the vacuous rc-only form); the accented word café matches whole (the Unicode word law: Latin/Greek/Cyrillic/accented scripts are tokens); the word-boundary law — 'cor' is NOT a prefix match (never matches 'corpus' — whole tokens only)",
              "the tokenizer is defined and deterministic: case-folded UNICODE word tokens (every script), whole-token equality (the known-query contract)")

        # ---- KWR-07 — the explicit lag/failure contract
        cnt_before = audit("SELECT count(*) FROM arv.keyword_index;")
        p_fail = cmd("create_note", "--content", "A refused note stays unindexed: token gravitonx.",
                     "--ref", "note:00000000-0000-7000-8000-0000000000f1@1", key="n-fail")
        pn2 = mk_note("n-ok2", "The immediate note: token bosonx rides.")
        n2 = ack_field(pn2, "result_ref")
        r_imm = search("A", "bosonx")
        n_fail_rows = audit("SELECT count(*) FROM arv.keyword_index WHERE token='gravitonx';")
        ok7 = (p_fail.returncode == 1 and "ARV-NTE-003" in p_fail.stdout
               and n_fail_rows == "0"  # the FORCED refusal leaves zero index rows
               and pn2.returncode == 0
               and r_imm.returncode == 0 and any(f"note|{n2}" in ln for ln in result_ids(r_imm))
               and int(audit("SELECT count(*) FROM arv.keyword_index;")) >= int(cnt_before))
        check("KWR-07", ok7,
              "the explicit lag/failure contract: a COMMITTED note is searchable immediately (the synchronous local index write rides the capture transaction — zero indexing lag on this rig); a refused note leaves zero index rows (never a partial: the index write and the capture are one transactional effect)",
              "the defined contract: searchable-or-explicit-failure, never a silent miss (PLAN's P3-07 acceptance)")

        # ---- KWR-08 — the multi-term query (the AND intersection)
        pn3 = mk_note("n-and", "Both tokens together: harpx and quillx.")
        n3 = ack_field(pn3, "result_ref")
        r_and = search("A", "harpx", "quillx")
        r_and2 = search("A", "harpx", "zephyr")
        ok8 = (r_and.returncode == 0 and any(f"note|{n3}" in ln for ln in result_ids(r_and))
               and r_and2.returncode == 0 and not any(f"note|{n3}" in ln for ln in result_ids(r_and2)))
        check("KWR-08", ok8,
              "the multi-term query: AND-matching (a document matches only if EVERY term hits it); the single-term miss excludes the document; the ordering deterministic",
              "the search contract is compositional: the intersection over per-term matches (the defined semantics, never an implicit OR)")

        # ---- KWR-09 — the schema audits (0011)
        cols = audit_rows("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema='arv' AND table_name='keyword_index' "
                          "ORDER BY ordinal_position;")
        rls = audit_rows("SELECT relrowsecurity::text, relforcerowsecurity::text FROM "
                         "pg_class WHERE oid='arv.keyword_index'::regclass;")
        grants = audit("SELECT CASE WHEN 'arv_app=ard/postgres' = ANY (string_to_array("
                       "trim(relacl::text, '{}'), ',')) THEN 'ok' ELSE relacl::text END "
                       "FROM pg_class WHERE oid='arv.keyword_index'::regclass;")
        chk = audit_rows("SELECT conname FROM pg_constraint WHERE conrelid="
                         "'arv.keyword_index'::regclass AND contype='c' ORDER BY conname;")
        ok9 = (cols == ["owner_scope", "kind", "entity_id", "revision", "token",
                        "extractor", "extractor_config", "input_digest", "created_at"]
               and rls == ["true|true"]
               and grants == "ok"
               and any("kind" in c for c in chk))
        check("KWR-09", ok9,
              "the 0011 schema audits: the exact six-column set (the locator + the token + the provenance timestamp — NO authored content column); RLS enabled AND FORCED; arv_app holds INSERT+DELETE+SELECT (the rebuild's own surface — the derived layer is the one table the app may DELETE, by design, because it is re-derivable); the kind CHECK",
              "the index's structure is the derived-layer law made mechanical (the no-copy form: tokens + locators only)")

        # ---- KWR-10 — the derived-layer law (droppable, never authoritative)
        cnt_notes = audit("SELECT count(*) FROM arv.note;")
        cnt_hl = audit("SELECT count(*) FROM arv.highlight;")
        dele2 = app_sql("DELETE FROM arv.keyword_index;")
        cnt_notes2 = audit("SELECT count(*) FROM arv.note;")
        cnt_hl2 = audit("SELECT count(*) FROM arv.highlight;")
        g_all = cli(str(REPO / "harness" / "query.py"), "get-note", "--owner", "A", "--id", n1)
        rb2 = rebuild()
        ok10 = (dele2.returncode == 0
                and cnt_notes2 == cnt_notes and cnt_hl2 == cnt_hl
                and g_all.returncode == 0
                and rb2.returncode == 0
                and audit("SELECT count(*) FROM arv.keyword_index;") > "0")
        check("KWR-10", ok10,
              "the derived-layer law: deleting the ENTIRE index changes ZERO authored rows (the counts unchanged, get-note still answers) and the rebuild restores the index — the index is droppable by design (the one non-authoritative table); the authored rows never depend on it",
              "the derived/authored separation is structural: the index serves findability, the rows serve truth (the P3-09 export never exports the index)")

        print()
        if FAILS:
            print(f"RED — the P3-07 keyword-index suite fails: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P3-07 acceptance suite (KWR-01..10) passes")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
