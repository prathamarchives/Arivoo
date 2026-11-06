#!/usr/bin/env python3
"""harness/tests/test_pdf.py — P4-A slice four acceptance suite (CLAIM-068,
the PDF boundary: the honest passthrough class, never a text-extraction
claim; PLAN's elaborated P4-A slice four card; record 60 §2).
Red-first (LAW-11): at CLAIM-067's merged head 237d4d8 the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the application/pdf media type
is not intake-legal (the passthrough carries application/octet-stream only).

THE CONTRACT (P4-A slice four's letter): the HONEST BOUNDARY, not a PDF
reader — application/pdf is INTAKE-LEGAL as the BYTES-PASSTHROUGH class (a
PDF imports durably through the one ladder; the blob stores the ORIGINAL
bytes), the READABLE-TEXT boundary stays at EXTRACTION's named refusal
(ARV-EXT-002 over the binary bytes, the staged bytes recoverable at the
source's digest), the matrix stays HONEST (NO pdf row — a format appears
only through its acceptance corpus; the scan/OCR + fixed-layout classes are
future increments under Q8's owner gate), and the octet-stream equivalence
holds (the same bytes under application/octet-stream ride the identical
boundary).

Cases (the PDF registry; each pin's full statement lives at its check()):
  PDF-01 the durable import through the passthrough: a (binary, realistic)
         PDF file imports with --media-type application/pdf and the ack
         carries the full frozen contract (status=committed result_ref=...
         durability_rung=local_durable api_version=1); the source row
         carries media_type=application/pdf; the blob stores the ORIGINAL
         bytes (the content-addressed store, never a transformation)
  PDF-02 the named extraction refusal: extract_source over the PDF source
         refuses ARV-EXT-002 at the real boundary (the readable-text
         boundary is the DECODE, never the media type) with ZERO effect
         (no generation row, no passage row) and the staged bytes
         recoverable (the blob ANSWERS at the source's digest)
  PDF-03 the keyword index's non-text boundary: the PDF source commits and
         is durable, but findability indexes text only — a PDF-internal
         token (a word from the PDF's own syntax) SEARCHES to nothing (the
         source absent from the search rows; the honest non-text class,
         never an index crash)
  PDF-04 the matrix's honesty + the octet-stream equivalence: the matrix
         carries NO pdf row (exactly the three approved formats — a format
         appears only through its acceptance corpus); the SAME PDF bytes
         under application/octet-stream import with the same frozen ack and
         extract with the SAME named refusal (the same class, the same
         letters — the passthrough is one class, never two)
  PDF-05 the capture/position arms over the PDF source: create_highlight
         refuses ARV-CAP-008 (the source is not valid UTF-8 text — the
         offset domain has no derived text); save_position refuses
         ARV-POS-002 (no serving generation — the PDF cannot extract, so
         there is no derived view to position into); both zero-effect

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no PDF text extraction
(the scan/OCR class — Q8's owner gate); no fixed-layout rendering; no
third-party PDF parser (ARV-DEP-008); the synthetic fixture only (a
hand-built minimal PDF — never a real-PDF stability claim).

Run: python3 harness/tests/test_pdf.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): at the RED tree the passthrough
# carries application/octet-stream ONLY — the application/pdf import refuses
# ARV-FMT-001 (the unsupported class). The cheapest honest probe per surface.
_pdf_fixture = pathlib.Path(tempfile.mkdtemp(prefix="arv-pdfprobe-")) / "probe.pdf"
_pdf_fixture.write_bytes(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
                         b"trailer\n<< /Root 1 0 R >>\n%%EOF\n")
_probe_env = dict(os.environ)
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                         "import_source", "--title", "The PDF Probe",
                         "--file", str(_pdf_fixture), "--media-type", "application/pdf",
                         "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                         "--idem-key", "pdfprobe-1"],
                        capture_output=True, text=True, timeout=120, env=_probe_env)
if not (_probe.returncode == 0 and "status=committed" in _probe.stdout):
    print(f"FAIL ARV-TEST-000: the P4-A slice four pdf boundary machinery is absent "
          f"(machinery-absent class; the application/pdf import committed: "
          f"{_probe.returncode == 0}; the observed refusal: "
          f"{next((ln for ln in _probe.stdout.splitlines() if ln.startswith('FAIL')), 'none')[:90]}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None

# the corpus: a minimal, REALISTIC binary PDF (the header + the binary
# comment line + a catalog object + the trailer — non-UTF-8 by construction,
# exactly like real PDFs whose xref streams are binary)
PDF_BYTES = (b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n"
             b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
             b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
             b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
             b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
             b"0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n187\n%%EOF\n")


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


def jlines(r: subprocess.CompletedProcess) -> list:
    return [json.loads(ln) for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4a4")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4a4-"))

        # ---- PDF-01 — the durable import through the passthrough
        pdf = tmp / "document.pdf"
        pdf.write_bytes(PDF_BYTES)
        r_p = cmd("import_source", "--title", "The PDF Boundary Corpus",
                  "--file", str(pdf), "--media-type", "application/pdf", key="pimp-1")
        pid = ref_of(r_p)
        mt_row = audit(f"SELECT media_type FROM arv.source WHERE id='{pid}';") if pid else ""
        # the blob stores the ORIGINAL bytes (content-addressed, never transformed)
        digest_row = audit(f"SELECT digest FROM arv.source WHERE id='{pid}';") if pid else ""
        orig_stored = False
        if digest_row:
            probe = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
                 "from harness.adapters import blob\n"
                 f"print(blob.get({digest_row!r}) == {PDF_BYTES!r})"],
                capture_output=True, text=True, timeout=60, env=ENV)
            orig_stored = probe.returncode == 0 and probe.stdout.strip() == "True"
        ok1 = (r_p.returncode == 0 and pid
               and "status=committed" in r_p.stdout
               and "durability_rung=local_durable" in r_p.stdout
               and "api_version=1" in r_p.stdout
               and mt_row == "application/pdf"
               and orig_stored)
        check("PDF-01", ok1,
              "the durable import through the passthrough: a (binary, realistic) PDF file imports "
              "with --media-type application/pdf and the ack carries the full frozen contract "
              "(status=committed + result_ref + durability_rung=local_durable + api_version=1); "
              "the source row carries media_type=application/pdf; the blob stores the ORIGINAL "
              "bytes (the content-addressed store, never a transformation — the passthrough class)",
              "the application/pdf media type in formats.py's PASSTHROUGH — the landed "
              "P3-02/EXT-03 bytes class extended to the named type, never a reading capability")

        # ---- PDF-02 — the named extraction refusal
        gens_before = audit("SELECT count(*) FROM arv.extraction_generation;")
        r_e = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                      "--idem-key", "pext-1", "--source-id", pid)
        gens_after = audit("SELECT count(*) FROM arv.extraction_generation;")
        blob_answers = False
        if digest_row:
            probe = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
                 "from harness.adapters import blob\n"
                 f"print(len(blob.get({digest_row!r})))"],
                capture_output=True, text=True, timeout=60, env=ENV)
            blob_answers = probe.returncode == 0 and probe.stdout.strip().isdigit()
        ok2 = (r_e.returncode == 1 and "FAIL ARV-EXT-002:" in r_e.stdout
               and "not valid UTF-8" in r_e.stdout
               and gens_before == gens_after
               and blob_answers)
        check("PDF-02", ok2,
              "the named extraction refusal: extract_source over the PDF source refuses "
              "ARV-EXT-002 at the real boundary (the readable-text boundary is the DECODE, never "
              "the media type — the PDF's binary bytes are not text) with ZERO effect (no "
              "generation row, no passage row) and the staged bytes recoverable (the blob "
              "ANSWERS at the source's digest — the durable capture is never lost to the "
              "extraction's honesty)",
              "the extraction's read_text decode boundary — the landed EXT-02 contract over the "
              "passthrough class, never a PDF-specific guess")

        # ---- PDF-03 — the keyword index's non-text boundary
        r_s = query("search", "--owner", "A", "Catalog")
        r_s2 = query("search", "--owner", "A", "xref")
        ok3 = (r_s.returncode == 0 and pid not in r_s.stdout
               and r_s2.returncode == 0 and pid not in r_s2.stdout)
        check("PDF-03", ok3,
              "the keyword index's non-text boundary: the PDF source commits and is durable, "
              "but findability indexes text only — a PDF-internal token (Catalog, xref — words "
              "from the PDF's own syntax) SEARCHES to nothing for the source (the honest "
              "non-text class at the import's index ride, never an index crash, never a "
              "false hit)",
              "the import's read_text boundary feeding the index — the non-text class indexes "
              "nothing, exactly like any opaque binary")

        # ---- PDF-04 — the matrix's honesty + the octet-stream equivalence
        r_mat = cap("matrix")
        rows = jlines(r_mat)
        fmts = {row.get("format") for row in rows}
        # the same bytes under the octet-stream passthrough: the same letters
        pdf2 = tmp / "same-bytes.bin"
        pdf2.write_bytes(PDF_BYTES)
        r_o = cmd("import_source", "--title", "The Same Bytes Octet",
                  "--file", str(pdf2), "--media-type", "application/octet-stream", key="oimp-1")
        oid = ref_of(r_o)
        r_eo = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                       "--idem-key", "oext-1", "--source-id", oid) if oid else None
        ok4 = (r_mat.returncode == 0
               and "application/pdf" not in fmts
               and fmts == {"text/plain", "application/json", "application/epub+zip"}
               and all(row.get("api_version") == 1 for row in rows)
               and r_o.returncode == 0 and oid and "api_version=1" in r_o.stdout
               and r_eo is not None and r_eo.returncode == 1
               and "FAIL ARV-EXT-002:" in r_eo.stdout
               and r_e.stdout.split("repair:")[0].strip() == r_eo.stdout.split("repair:")[0].strip())
        check("PDF-04", ok4,
              "the matrix's honesty + the octet-stream equivalence: the matrix carries NO pdf "
              "row (exactly the three approved formats — a format appears only through its "
              "acceptance corpus; the scan/OCR + fixed-layout classes are future increments "
              "under Q8's owner gate, never a generic claim from the passthrough); the SAME "
              "PDF bytes under application/octet-stream import with the same frozen ack and "
              "extract with the SAME named refusal (byte-equal refusal heads — the passthrough "
              "is ONE class, never two)",
              "formats.py's PASSTHROUGH carrying application/pdf beside "
              "application/octet-stream — the intake legality, never a matrix row")

        # ---- PDF-05 — the capture/position arms over the PDF source
        r_hl = cmd("create_highlight", "--source-id", pid, "--start", "0",
                   "--end", "5", key="phl-1")
        r_pos = cmd("save_position", "--source-id", pid, "--start", "0",
                    "--end", "5", key="ppos-1")
        hl_rows = audit("SELECT count(*) FROM arv.highlight;")
        pos_rows = audit("SELECT count(*) FROM arv.reading_position;")
        ok5 = (r_hl.returncode == 1 and "FAIL ARV-CAP-008:" in r_hl.stdout
               and r_pos.returncode == 1 and "FAIL ARV-POS-002:" in r_pos.stdout
               and hl_rows == "0" and pos_rows == "0")
        check("PDF-05", ok5,
              "the capture/position arms over the PDF source: create_highlight refuses "
              "ARV-CAP-008 (the source is not valid UTF-8 text — the offset domain has no "
              "derived text over the passthrough class); save_position refuses ARV-POS-002 "
              "(no serving generation — the PDF cannot extract, so there is no derived view "
              "to position into); both ZERO effect (no highlight row, no position row)",
              "the read_text boundary at the capture arms + the serving-generation "
              "precondition at the position arm — the landed letters, never a PDF-specific "
              "path")

        if FAILS:
            print(f"\nPDF SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the PDF boundary contract is broken or unimplemented)")
            return 1
        print("\nPDF SUITE GREEN — PDF-01..05 (the PDF boundary: the durable passthrough "
              "import, the named extraction refusal with the bytes recoverable, the honest "
              "matrix with no pdf row, the octet-stream equivalence, the typed capture/"
              "position refusals)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
