#!/usr/bin/env python3
"""harness/tests/test_capability.py — P4-00c acceptance suite (CLAIM-064, the
format capability matrix + extraction readiness; PLAN's elaborated P4-00c
card; the #98 SEV routings F5/F10 ride here — record 56 §2).
Red-first (LAW-11): at CLAIM-063's merged head 647f3cb the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the capability module, the
readiness surface, and the rewritten README are absent.

THE CONTRACT (P4-00c's letter): what the system can do with a format is a
DECLARED, MEASURED, user-visible matrix — never marketing, never a silent
miss:

Cases (the CAP registry; each pin's full statement lives at its check()):
  CAP-01 the declared matrix: capability.py's `matrix` prints one JSON row
         per declared format, each carrying the full capability vocabulary
         (native_text / scan_ocr / layout: reflow|fixed / extraction /
         approved) + api_version; text/plain is the FIRST APPROVED format
         (native text, reflow, no OCR — exactly what the landed machinery
         does, never more)
  CAP-02 the MEASURED row (measured, never asserted): capability.py's
         `measure --owner --source` derives the row from the REAL boundary —
         state=ready with the generation's own facts (passages=3, coverage
         =1.0 over the known corpus, the generation id + ordinal); the
         not-extracted source answers state=not_extracted passages=0 (a
         typed ANSWER, never silence); the crashed extract answers
         state=building (the honest in-flight state)
  CAP-03 the read-position reservation: capability.py's `surfaces` names
         source-open/position with its owning phase (P4-A/B) and the
         contract sketch — the surface RESERVED, never smuggled; the README
         carries the reservation
  CAP-04 the README rewritten to the frozen contract (the F5 routing): the
         versioned search-header example, the list arms' --limit/--after +
         the '# more=' markers documented, the api_version field named, the
         capability/readiness section present
  CAP-05 the per-family refusal hint (the F10 routing): get-note's
         ARV-QRY-001 hint names list-notes, get-bookmark's names
         list-bookmarks, the capture/source arms keep list-captures — and
         the template-level no-oracle equality (absent == cross-owner per
         arm) STILL holds
  CAP-06 the new surface carries the frozen contract: every capability.py
         output carries api_version; the absent AND cross-owner source
         refuse ARV-QRY-001 byte-identically at the template level (the
         P4-00b no-oracle pattern extended to the capability surface)

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no format converters
beyond the first approved format; no OCR work (its own gate); the
reader-client stays the separate repo.

Run: python3 harness/tests/test_capability.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): the capability module is the
# cheapest honest probe — its `matrix` verb answers the declared rows; at
# the RED tree the module is absent. The README's frozen forms double the
# probe (the CON precedent's double form).
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "capability.py"), "matrix"],
                        capture_output=True, text=True, timeout=120)
_readme_txt = (REPO / "README.md").read_text(encoding="utf-8") if (REPO / "README.md").is_file() else ""
_probe_ok = (_probe.returncode == 0
             and "# api_version=1 kind|entity_id|revision|matched_terms" in _readme_txt
             and "--limit" in _readme_txt and "--after" in _readme_txt
             and "api_version" in _readme_txt and "more=" in _readme_txt)
if not _probe_ok:
    print(f"FAIL ARV-TEST-000: the P4-00c capability machinery is absent "
          f"(machinery-absent class; capability.py matrix exit {_probe.returncode}; "
          f"the README's frozen forms present: "
          f"{'# api_version=1 kind|' in _readme_txt and '--limit' in _readme_txt}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None
TEXT = ("Para one lives here.\n\n"
        "Para two follows the first.\n\n"
        "Para three closes the set.")
# the measured facts for THIS corpus (the tiler's own values — pinned by
# measurement, the suite fails if the machinery's answer differs)
N_PASSAGES, COVERAGE = 3, 1.0


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


def cmd(op: str, *args, owner="A", key=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args)


def extract(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "extract.py"), *args)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


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


def _tmpl(out: str, qid: str) -> str:
    return out.replace(qid, "<id>")


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p400c")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)

        # ---- the fixture: three sources (ready / not_extracted / building)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p400c-"))
        f1 = tmp / "one.md"
        f1.write_text(TEXT, encoding="utf-8")
        r1 = cmd("import_source", "--title", "The Measured Corpus",
                 "--file", str(f1), key="imp-1")
        s_ready = ref_of(r1)
        r_ext = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                        "--idem-key", "ext-1", "--source-id", s_ready)
        gen_id = ref_of(r_ext)
        f2 = tmp / "two.md"
        f2.write_text("A second source, imported but never extracted.\n\nTwo blocks.",
                      encoding="utf-8")
        r2 = cmd("import_source", "--title", "The Unextracted Corpus",
                 "--file", str(f2), key="imp-2")
        s_unex = ref_of(r2)
        f3 = tmp / "three.md"
        f3.write_text("A third source for the crash class.\n\nTwo blocks here too.",
                      encoding="utf-8")
        r3 = cmd("import_source", "--title", "The Crash Corpus",
                 "--file", str(f3), key="imp-3")
        s_crash = ref_of(r3)
        r_crash = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                          "--idem-key", "ext-3", "--source-id", s_crash,
                          "--crash-at", "pre-commit")
        # a capture + note for the per-family hint probes (CAP-05)
        r_hl = cmd("create_highlight", "--source-id", s_ready, "--start", "0",
                   "--end", "5", key="hl-1")
        hl1 = ref_of(r_hl)
        r_nt = cmd("create_note", "--content", "the capability note",
                   "--ref", f"highlight:{hl1}@1", key="nt-1")
        n1 = ref_of(r_nt)
        r_bm = cmd("create_bookmark", "--source-id", s_ready, "--start", "0",
                   "--end", "5", key="bm-1")
        bm1 = ref_of(r_bm)

        # ---- CAP-01 — the declared matrix
        r_mat = cap("matrix")
        rows = jlines(r_mat)
        fmts = {row.get("format"): row for row in rows}
        tp = fmts.get("text/plain", {})
        ok1 = (r_mat.returncode == 0
               and len(rows) >= 1
               and all(row.get("api_version") == 1 for row in rows)
               and tp.get("approved") is True
               and tp.get("native_text") is True
               and tp.get("scan_ocr") is False
               and tp.get("layout") == "reflow"
               and tp.get("extraction") == "supported")
        check("CAP-01", ok1,
              "the declared matrix: capability.py matrix prints one JSON row per declared format, each "
              "carrying api_version + the full vocabulary (native_text/scan_ocr/layout/extraction/"
              "approved); text/plain is the FIRST APPROVED format — native text, reflow, NO OCR "
              "(exactly what the landed machinery does, never more)",
              "harness/capability.py's FORMATS registry + the matrix verb (the declaration is data, "
              "the CLI the boundary)")

        # ---- CAP-02 — the MEASURED row (measured, never asserted)
        r_m1 = cap("measure", "--owner", "A", "--source", s_ready)
        m1 = jline(r_m1)
        r_m2 = cap("measure", "--owner", "A", "--source", s_unex)
        m2 = jline(r_m2)
        r_m3 = cap("measure", "--owner", "A", "--source", s_crash)
        m3 = jline(r_m3)
        ok2 = (r_ext.returncode == 0
               and r_m1.returncode == 0
               and m1.get("state") == "ready" and m1.get("api_version") == 1
               and m1.get("passages") == N_PASSAGES and m1.get("coverage") == COVERAGE
               and m1.get("generation_id") == gen_id and m1.get("ordinal") == 1
               and m1.get("media_type") == "text/plain"
               and r_m2.returncode == 0
               and m2.get("state") == "not_extracted" and m2.get("passages") == 0
               and m2.get("api_version") == 1
               and r_crash.returncode == 2  # the crash injector's own vocabulary
               and r_m3.returncode == 0
               and m3.get("state") == "building" and m3.get("api_version") == 1)
        check("CAP-02", ok2,
              "the MEASURED row (measured, never asserted): the ready source answers state=ready with "
              "the generation's OWN facts (passages=3, coverage=1.0, the generation id + ordinal — "
              "derived at the real boundary, the suite fails if the machinery's answer differs); the "
              "unextracted source answers state=not_extracted passages=0 (a typed ANSWER, never "
              "silence); the crashed extract answers state=building (the honest in-flight state)",
              "harness/capability.py's measure verb: the owner-scoped reads over the generation + "
              "passage rows + the blob (the coverage derivation), never a hard-coded row")

        # ---- CAP-03 — the read-position reservation
        r_sur = cap("surfaces")
        srows = jlines(r_sur)
        pos = next((row for row in srows
                    if row.get("surface") == "source-open/position"), {})
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        ok3 = (r_sur.returncode == 0
               and all(row.get("api_version") == 1 for row in srows)
               and pos.get("owner_phase") == "P4-A/B"
               and "position" in str(pos.get("reservation", "")).lower()
               and "source-open/position" in readme)
        check("CAP-03", ok3,
              "the read-position reservation: capability.py surfaces names source-open/position with "
              "its owning phase (P4-A/B) and the contract sketch — the surface RESERVED and declared, "
              "never smuggled; the README carries the reservation",
              "harness/capability.py's RESERVED_SURFACES registry + the README's reservation note")

        # ---- CAP-04 — the README rewritten to the frozen contract (F5)
        ok4 = ("# api_version=1 kind|entity_id|revision|matched_terms" in readme
               and "--limit" in readme and "--after" in readme
               and "more=true" in readme and "more=false" in readme
               and "api_version" in readme
               and "capability" in readme.lower() and "readiness" in readme.lower()
               and "list-notes" in readme and "list-captures" in readme)
        check("CAP-04", ok4,
              "the README rewritten to the frozen P4-00b/P4-00c contract (the F5 routing): the "
              "versioned search-header example, the list arms' --limit/--after + the '# more=' "
              "markers documented, the api_version field named, the capability/readiness section "
              "present (the day-one doc meets the surface the boundary suite froze)",
              "README.md's surface docs: the current forms, never the pre-P4-00b examples")

        # ---- CAP-05 — the per-family refusal hint (F10) + the no-oracle intact
        absent = str(_uuid.uuid4())
        rn_abs = query("get-note", "--owner", "A", "--id", absent)
        rn_xo = query("get-note", "--owner", "B", "--id", n1)
        rb_abs = query("get-bookmark", "--owner", "A", "--id", absent)
        rb_xo = query("get-bookmark", "--owner", "B", "--id", bm1)
        rc_abs = query("get-capture", "--owner", "A", "--id", absent)
        rc_xo = query("get-capture", "--owner", "B", "--id", hl1)
        ok5 = (rn_abs.returncode == 1 and "FAIL ARV-QRY-001:" in rn_abs.stdout
               and "list-notes" in rn_abs.stdout
               and rn_xo.returncode == 1
               and _tmpl(rn_xo.stdout, n1) == _tmpl(rn_abs.stdout, absent)
               and rb_abs.returncode == 1 and "FAIL ARV-QRY-001:" in rb_abs.stdout
               and "list-bookmarks" in rb_abs.stdout
               and rb_xo.returncode == 1
               and _tmpl(rb_xo.stdout, bm1) == _tmpl(rb_abs.stdout, absent)
               and rc_abs.returncode == 1 and "FAIL ARV-QRY-001:" in rc_abs.stdout
               and "list-captures" in rc_abs.stdout
               and rc_xo.returncode == 1
               and _tmpl(rc_xo.stdout, hl1) == _tmpl(rc_abs.stdout, absent))
        check("CAP-05", ok5,
              "the per-family refusal hint (the F10 routing): get-note's ARV-QRY-001 names list-notes, "
              "get-bookmark's names list-bookmarks, the capture arm keeps list-captures — AND the "
              "template-level no-oracle equality (absent == cross-owner per arm) still holds on all "
              "three families",
              "query.py's _refuse: the family parameter naming the caller's own list arm per family")

        # ---- CAP-06 — the new surface carries the frozen contract
        r_abs_src = cap("measure", "--owner", "A", "--source", absent)
        r_xo_src = cap("measure", "--owner", "B", "--source", s_ready)
        ok6 = (r_abs_src.returncode == 1 and "FAIL ARV-QRY-001:" in r_abs_src.stdout
               and r_xo_src.returncode == 1 and "FAIL ARV-QRY-001:" in r_xo_src.stdout
               and _tmpl(r_xo_src.stdout, s_ready) == _tmpl(r_abs_src.stdout, absent)
               and r_abs_src.stderr == r_xo_src.stderr
               and m1.get("api_version") == 1 and m2.get("api_version") == 1
               and m3.get("api_version") == 1
               and all(row.get("api_version") == 1 for row in rows + srows))
        check("CAP-06", ok6,
              "the new surface carries the frozen contract: every capability.py output (the matrix "
              "rows, the surfaces, every measured row — ready/not_extracted/building) carries "
              "api_version; the absent AND the cross-owner source refuse ARV-QRY-001 byte-identically "
              "at the template level (the P4-00b no-oracle pattern extended to the capability "
              "surface — never a new side channel)",
              "harness/capability.py: the version key on every output + the shared refusal form")

        if FAILS:
            print(f"\nCAPABILITY SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the capability contract is broken or unimplemented)")
            return 1
        print("\nCAPABILITY SUITE GREEN — CAP-01..06 (the format capability matrix + extraction "
              "readiness: the declared matrix, the MEASURED row, the read-position reservation, the "
              "rewritten README, the per-family hints, the frozen contract on the new surface)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
