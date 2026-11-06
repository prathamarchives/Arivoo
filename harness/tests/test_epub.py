#!/usr/bin/env python3
"""harness/tests/test_epub.py — P4-A slice three acceptance suite (CLAIM-067,
the EPUB intake: the zip/XHTML adapter by the stdlib path; PLAN's elaborated
P4-A slice three card; record 59 §2).
Red-first (LAW-11): at CLAIM-066's merged head 269921ac the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the matrix's third row, the
epub adapter, and the typed epub-family refusals are absent.

THE CONTRACT (P4-A slice three's letter): the `application/epub+zip` intake
through the EXISTING durability ladder — the adapter registry's THIRD
approved row (never a second durability path); the zip container walked by
the Python stdlib ALONE (no third-party dependency — ARV-DEP-008); the
OPF/container structure verified; the XHTML-derived plain text (the reflow
class) readable at EVERY text-access site (ONE home: the derived view feeds
extraction, the keyword index, and the highlight/position offset
validations — the slice-two contract composes, never a second position
path); every failure a named, typed, zero-effect refusal whose staged bytes
survive.

Cases (the EPB registry; each pin's full statement lives at its check()):
  EPB-01 the synthetic-EPUB round-trip through the EXISTING ladder: a
         stdlib-built EPUB (mimetype + META-INF/container.xml + the OPF +
         XHTML chapters) imports with --media-type application/epub+zip and
         the ack carries the full frozen contract; the source row carries
         media_type=application/epub+zip; the DERIVED text is the chapters'
         own text (the keyword index rides it — a chapter phrase SEARCHES
         to the source); the text/plain + application/json rows unchanged
  EPB-02 the THIRD matrix row MEASURED (the P4-00c two-corpus form extended):
         the matrix declares application/epub+zip (NOT native text — the
         container is not the text; reflow; no OCR; extraction supported;
         approved; the epub extractor NAMED) and the MEASURED row over the
         synthetic corpus derives passages/coverage at the real boundary —
         never asserted; the matrix row EQUALS the registry entry (one home)
  EPB-03 the typed epub-family refusals with staged bytes: ARV-FMT-004 (the
         not-a-zip container — epub-typed bytes that are not a zip at all),
         ARV-FMT-005 (the broken structure — a zip without the
         container/OPF chain), ARV-FMT-006 (the unreadable content set —
         the structure holds but the reading-order documents yield no
         readable text) — each exit 1 + the FAIL prefix + ZERO effect (the
         source count unchanged) + the digest NAMED + the blob ANSWERS at
         it (staged bytes never lost) + the journal failed-retryable; the
         same key + the same bad bytes -> the SAME refusal (idempotent); a
         NEW key + the good file -> committed (the rewind)
  EPB-04 the composition arm + the unchanged boundaries: a position saved
         over the EPUB-derived view rides the SAME generation binding
         (save=1, matches=true, the reopen answers); a highlight over the
         EPUB source validates its offsets against the DERIVED text (the
         chapter phrase selectable + resolvable); the octet-stream
         passthrough unchanged (an opaque binary still imports durably);
         ARV-FMT-001 still fires for an UNREGISTERED type
  EPB-05 the stdlib-only law + the one-home law: formats.py's imports are
         ALL stdlib (sys.stdlib_module_names — ARV-DEP-008: zipfile +
         html.parser + json, never a third-party parser); the matrix's epub
         row derives FROM the registry (capability.py imports ADAPTERS —
         never a second declaration)

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no DRM circumvention
surface (an encrypted EPUB refuses typed, the bytes staged); no PDF (the
following slice); no reader-client work (P4-B's repo); the synthetic corpus
only (Q8's gate — never a real-EPUB stability claim).

Run: python3 harness/tests/test_epub.py   (exit 0 = green)
"""
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import uuid as _uuid
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pg  # noqa: E402

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the THIRD matrix row is the
# cheapest honest probe — at the RED tree the matrix declares exactly two
# formats (text/plain + application/json); the epub adapter is absent.
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "capability.py"), "matrix"],
                        capture_output=True, text=True, timeout=120)
_probe_rows = [ln for ln in _probe.stdout.splitlines() if ln.strip()]
_probe_epub = any('"application/epub+zip"' in ln for ln in _probe_rows)
if not (_probe.returncode == 0 and _probe_epub):
    print(f"FAIL ARV-TEST-000: the P4-A slice three epub machinery is absent "
          f"(machinery-absent class; the matrix's application/epub+zip row present: {_probe_epub}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None

# ---- the synthetic EPUB corpus (the test builds it with the STDLIB alone) ----
CH1_P1 = "The first chapter opens the synthetic corpus with its own prose."
CH1_P2 = "The first chapter's second paragraph carries the zephyr token."
CH2_P1 = "The second chapter follows with the meridian phrase."
CH2_P2 = "The second chapter closes the reading order."

CONTAINER_XML = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                 '  <rootfiles>\n'
                 '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
                 '  </rootfiles>\n'
                 '</container>\n')

OPF_XML = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">\n'
           '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
           '    <dc:identifier id="uid">urn:uuid:synthetic-corpus-001</dc:identifier>\n'
           '    <dc:title>The Synthetic EPUB Corpus</dc:title>\n'
           '  </metadata>\n'
           '  <manifest>\n'
           '    <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>\n'
           '    <item id="ch2" href="ch2.xhtml" media-type="application/xhtml+xml"/>\n'
           '  </manifest>\n'
           '  <spine>\n'
           '    <itemref idref="ch1"/>\n'
           '    <itemref idref="ch2"/>\n'
           '  </spine>\n'
           '</package>\n')


def _xhtml(title: str, paras: list) -> str:
    body = "".join(f"<p>{p}</p>" for p in paras)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{title}</title></head>'
            f'<body>{body}</body></html>\n')


def build_epub(path, *, with_container=True, chapter_garbage=False) -> None:
    """The synthetic corpus builder — the STDLIB alone (zipfile; the same law
    the adapter carries). The variants: no container (the FMT-005 probe) and
    garbage chapters (the FMT-006 probe)."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        if with_container:
            z.writestr("META-INF/container.xml", CONTAINER_XML)
            z.writestr("OEBPS/content.opf", OPF_XML)
        if chapter_garbage:
            z.writestr("OEBPS/ch1.xhtml", b"\x00\x01\x02\xff\xfe\x00 garbage \xff\x01")
            z.writestr("OEBPS/ch2.xhtml", b"\x00\x02\x04\xff\xfd\x00 more garbage \xfe\x02")
        else:
            z.writestr("OEBPS/ch1.xhtml", _xhtml("Chapter One", [CH1_P1, CH1_P2]))
            z.writestr("OEBPS/ch2.xhtml", _xhtml("Chapter Two", [CH2_P1, CH2_P2]))


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


def _digest_of(r: subprocess.CompletedProcess) -> str:
    """the refusal's named digest (the staged-bytes recovery key)"""
    for ln in r.stdout.splitlines():
        if "[digest=" in ln:
            return ln.split("[digest=")[1].split("]")[0].strip().rstrip("')")
    return ""


def _blob_answers(digest: str) -> bool:
    if not digest:
        return False
    probe = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
         "from harness.adapters import blob\n"
         f"print(len(blob.get({digest!r})))"],
        capture_output=True, text=True, timeout=60, env=ENV)
    return probe.returncode == 0 and probe.stdout.strip().isdigit()


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4a3")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4a3-"))

        # ---- EPB-01 — the synthetic-EPUB round-trip through the EXISTING ladder
        epub = tmp / "corpus.epub"
        build_epub(epub)
        r_e = cmd("import_source", "--title", "The Synthetic EPUB Corpus",
                  "--file", str(epub), "--media-type", "application/epub+zip", key="eimp-1")
        esid = ref_of(r_e)
        mt_row = audit(f"SELECT media_type FROM arv.source WHERE id='{esid}';") if esid else ""
        # the derived text is the chapters' own text: the keyword index rides it
        r_s = query("search", "--owner", "A", "zephyr")
        # the landed rows unchanged (the first two rows still first)
        tf = tmp / "plain.txt"
        tf.write_text("Plain text still rides the same ladder.\n\nA second block.",
                      encoding="utf-8")
        r_t = cmd("import_source", "--title", "The Plain Corpus",
                  "--file", str(tf), key="timp-1")
        ok1 = (r_e.returncode == 0 and esid
               and "status=committed" in r_e.stdout
               and "durability_rung=local_durable" in r_e.stdout
               and "api_version=1" in r_e.stdout
               and mt_row == "application/epub+zip"
               and r_s.returncode == 0 and esid in r_s.stdout
               and r_t.returncode == 0 and "api_version=1" in r_t.stdout)
        check("EPB-01", ok1,
              "the synthetic-EPUB round-trip through the EXISTING ladder: a stdlib-built EPUB "
              "(mimetype + META-INF/container.xml + the OPF + two XHTML chapters) imports with "
              "--media-type application/epub+zip and the ack carries the full frozen contract "
              "(status=committed + result_ref + durability_rung=local_durable + api_version=1); "
              "the source row carries media_type=application/epub+zip; THE DERIVED TEXT IS THE "
              "CHAPTERS' OWN TEXT — the keyword index rides it (a chapter phrase SEARCHES to the "
              "source); the text/plain path unchanged",
              "the epub adapter at the import boundary feeding the ONE ladder + the derived text "
              "at the keyword-index ride — never a second durability path, never a second index")

        # ---- EPB-02 — the THIRD matrix row MEASURED (the two-corpus form extended)
        r_mat = cap("matrix")
        rows = jlines(r_mat)
        fmts = {row.get("format"): row for row in rows}
        r_ext = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                        "--idem-key", "eext-1", "--source-id", esid)
        r_m = cap("measure", "--owner", "A", "--source", esid)
        m = jline(r_m)
        # the one-home law: the matrix's epub row EQUALS the registry entry
        sys.path.insert(0, str(REPO))
        from harness.formats import ADAPTERS  # noqa: E402
        reg_epub = dict(ADAPTERS.get("application/epub+zip", {}))
        mat_epub = {k: v for k, v in fmts.get("application/epub+zip", {}).items()
                    if k not in ("api_version", "format")}
        ok2 = (r_mat.returncode == 0
               and "application/epub+zip" in fmts
               and fmts["application/epub+zip"].get("native_text") is False
               and fmts["application/epub+zip"].get("scan_ocr") is False
               and fmts["application/epub+zip"].get("layout") == "reflow"
               and fmts["application/epub+zip"].get("extraction") == "supported"
               and fmts["application/epub+zip"].get("approved") is True
               and fmts["application/epub+zip"].get("extractor")
               and fmts["application/epub+zip"].get("api_version") == 1
               and r_ext.returncode == 0
               and r_m.returncode == 0
               and m.get("state") == "ready" and m.get("api_version") == 1
               and m.get("media_type") == "application/epub+zip"
               and isinstance(m.get("passages"), int) and m.get("passages", 0) >= 2
               and isinstance(m.get("coverage"), (int, float)) and 0 < m.get("coverage", 0) <= 1.0
               and reg_epub and reg_epub == mat_epub)
        check("EPB-02", ok2,
              "the THIRD matrix row MEASURED: the matrix declares application/epub+zip (NOT native "
              "text — the container is not the text; reflow; no OCR; extraction supported; "
              "approved; the epub extractor NAMED) alongside the unchanged first rows; the "
              "MEASURED row over the synthetic corpus derives passages/coverage at the real "
              "boundary (state=ready, passages >= 2 — the chapters tile, the values derived — "
              "never asserted); the matrix's epub row EQUALS the registry entry (one home: the "
              "adapter declares, the matrix reports)",
              "harness/formats.py's adapter registry (the epub entry) + capability.py's matrix "
              "deriving FROM it + extract.py's text access routed through the adapter's read_text "
              "(the pre-slice form decodes independently and would refuse the zip blob)")

        # ---- EPB-03 — the typed epub-family refusals with staged bytes
        srcs_before = audit("SELECT count(*) FROM arv.source;")
        # (a) ARV-FMT-004: epub-typed bytes that are not a zip at all
        notzip = tmp / "notzip.epub"
        notzip.write_text("This is plain text pretending to be an EPUB container.\n",
                          encoding="utf-8")
        r_004 = cmd("import_source", "--title", "Not A Zip",
                    "--file", str(notzip), "--media-type", "application/epub+zip", key="e004-1")
        d004 = _digest_of(r_004)
        # (b) ARV-FMT-005: a zip without the container/OPF chain
        nostruct = tmp / "nostruct.epub"
        build_epub(nostruct, with_container=False)
        r_005 = cmd("import_source", "--title", "Broken Structure",
                    "--file", str(nostruct), "--media-type", "application/epub+zip", key="e005-1")
        d005 = _digest_of(r_005)
        # (c) ARV-FMT-006: the structure holds but the chapters yield no readable text
        garbage = tmp / "garbage.epub"
        build_epub(garbage, chapter_garbage=True)
        r_006 = cmd("import_source", "--title", "Unreadable Content",
                    "--file", str(garbage), "--media-type", "application/epub+zip", key="e006-1")
        d006 = _digest_of(r_006)
        srcs_after = audit("SELECT count(*) FROM arv.source;")
        journal_004 = audit("SELECT state || '|' || COALESCE(fail_reason, '') FROM arv.import_journal "
                            "WHERE idempotency_key='e004-1';")
        # the idempotent refusal + the rewind (the CAP-004 pattern)
        r_004b = cmd("import_source", "--title", "Not A Zip",
                     "--file", str(notzip), "--media-type", "application/epub+zip", key="e004-1")
        r_fix = cmd("import_source", "--title", "The Fixed Rewind",
                    "--file", str(epub), "--media-type", "application/epub+zip", key="efix-1")
        ok3 = (r_004.returncode == 1 and "FAIL ARV-FMT-004:" in r_004.stdout
               and ref_of(r_004) == "" and d004 and _blob_answers(d004)
               and r_005.returncode == 1 and "FAIL ARV-FMT-005:" in r_005.stdout
               and ref_of(r_005) == "" and d005 and _blob_answers(d005)
               and r_006.returncode == 1 and "FAIL ARV-FMT-006:" in r_006.stdout
               and ref_of(r_006) == "" and d006 and _blob_answers(d006)
               and srcs_before == srcs_after
               and journal_004.startswith("failed") and "ARV-FMT-004" in journal_004
               and r_004b.returncode == 1 and "FAIL ARV-FMT-004:" in r_004b.stdout
               and r_fix.returncode == 0 and ref_of(r_fix))
        check("EPB-03", ok3,
              "the typed epub-family refusals with staged bytes: ARV-FMT-004 (the not-a-zip "
              "container — epub-typed bytes that are not a zip at all), ARV-FMT-005 (the broken "
              "structure — a zip without the container/OPF chain), ARV-FMT-006 (the unreadable "
              "content set — the structure holds but the reading-order documents yield no "
              "readable text) — each exit 1 + the FAIL prefix + ZERO effect (the source count "
              "unchanged across all three) + the digest NAMED + the blob ANSWERS at it (staged "
              "bytes never lost) + the journal failed-retryable; the same key + the same bad "
              "bytes -> the SAME refusal (idempotent); a NEW key + the good file -> committed "
              "(the rewind)",
              "harness/formats.py's epub decode: the zipfile walk + the container/OPF "
              "verification + the XHTML text derivation, each failure a named typed "
              "zero-effect refusal whose staged bytes survive")

        # ---- EPB-04 — the composition arm + the unchanged boundaries
        # a position over the EPUB-derived view rides the SAME generation binding
        gen = m.get("generation_id", "")
        # the derived text length via the source's digest (read from the store)
        digest_row = audit(f"SELECT digest FROM arv.source WHERE id='{esid}';")
        text_len_probe = subprocess.run(
            [sys.executable, "-c",
             f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
             "from harness import formats\n"
             f"print(len(formats.read_text('application/epub+zip', {digest_row!r})))"],
            capture_output=True, text=True, timeout=60, env=ENV)
        derived_len = int(text_len_probe.stdout.strip()) if text_len_probe.returncode == 0 else 0
        start, end = max(0, derived_len // 3), derived_len // 2
        r_pos = cmd("save_position", "--source-id", esid, "--start", str(start),
                    "--end", str(end), key="epos-1")
        r_gp = query("get-position", "--owner", "A", "--source", esid)
        gp = jline(r_gp)
        # a highlight over the EPUB source: the chapter phrase selectable + resolvable
        z_i = None
        r_hl = cmd("create_highlight", "--source-id", esid, "--start", str(start),
                   "--end", str(end), key="ehl-1")
        hid = ref_of(r_hl)
        r_an = query("resolve-anchor", "--owner", "A",
                     "--id", audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{hid}';")) if hid else None
        # the unchanged boundaries: the octet-stream passthrough + ARV-FMT-001
        binq = tmp / "blob.bin"
        binq.write_bytes(b"\x00\x01\x02 opaque bytes ride the passthrough \xff\xfe")
        r_bin = cmd("import_source", "--title", "Opaque Bytes",
                    "--file", str(binq), "--media-type", "application/octet-stream", key="ebin-1")
        r_001 = cmd("import_source", "--title", "Unregistered",
                    "--file", str(binq), "--media-type", "application/x-msdownload", key="e001-1")
        ok4 = (r_pos.returncode == 0 and f"result_ref={esid}@1" in r_pos.stdout
               and "save=1" in r_pos.stdout and "api_version=1" in r_pos.stdout
               and r_gp.returncode == 0
               and gp.get("state") == "saved" and gp.get("save_ordinal") == 1
               and gp.get("saved_generation_id") == gen
               and gp.get("generation_matches") is True
               and r_hl.returncode == 0 and hid
               and r_an is not None and r_an.returncode == 0
               and '"state": "resolved"' in r_an.stdout
               and r_bin.returncode == 0 and ref_of(r_bin)
               and r_001.returncode == 1 and "FAIL ARV-FMT-001:" in r_001.stdout)
        check("EPB-04", ok4,
              "the composition arm + the unchanged boundaries: a position saved over the "
              "EPUB-derived view rides the SAME generation binding (save=1, the frozen ack, "
              "generation_matches=true, the reopen answers — the slice-two contract over the new "
              "derived view, byte-identical machinery); a highlight over the EPUB source "
              "validates its offsets against the DERIVED text and its anchor RESOLVES; the "
              "octet-stream passthrough unchanged (an opaque binary still imports durably); "
              "ARV-FMT-001 still fires for an UNREGISTERED type",
              "the ONE read_text home feeding the position/highlight offset validations + the "
              "unchanged registry boundaries")

        # ---- EPB-05 — the stdlib-only law + the one-home law
        fmt_src = (REPO / "harness" / "formats.py").read_text(encoding="utf-8")
        import re as _re
        imported = set()
        for ln in fmt_src.splitlines():
            mm = _re.match(r"^(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)", ln.strip())
            if mm:
                imported.add(mm.group(1))
        non_stdlib = sorted(m for m in imported
                            if m not in sys.stdlib_module_names and m != "harness")
        cap_src = (REPO / "harness" / "capability.py").read_text(encoding="utf-8")
        ok5 = (not non_stdlib
               and "zipfile" in imported
               and "ADAPTERS" in cap_src
               and "application/epub+zip" not in cap_src)
        check("EPB-05", ok5,
              "the stdlib-only law + the one-home law: formats.py's imports are ALL stdlib "
              "(zipfile + html.parser + json — never a third-party parser; ARV-DEP-008's law) "
              "plus the harness package itself; capability.py's matrix DERIVES from the "
              "registry (ADAPTERS imported, the epub string ABSENT from capability.py — never "
              "a second declaration)",
              "the stdlib zipfile + html.parser walk in formats.py + the matrix's derivation "
              "unchanged from the CLAIM-065 form")

        if FAILS:
            print(f"\nEPUB SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the EPUB intake contract is broken or unimplemented)")
            return 1
        print("\nEPUB SUITE GREEN — EPB-01..05 (the EPUB intake: the synthetic round-trip "
              "through the one ladder, the third measured matrix row, the typed epub-family "
              "refusals with staged bytes, the composition arm over the derived view)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
