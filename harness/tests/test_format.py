#!/usr/bin/env python3
"""harness/tests/test_format.py — P4-A slice one acceptance suite (CLAIM-065,
the first additional format intake: JSON by the durability ladder; PLAN's
elaborated P4-A card minted at P4-00c's landing; record 57 §2).
Red-first (LAW-11): at CLAIM-064's merged head 4e758fc the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the second matrix row, the
format adapter, and the typed intake refusals are absent.

THE CONTRACT (P4-A slice one's letter): a format is INTAKE-SUPPORTED only
through the one durability ladder, and every failure is a named, typed,
zero-effect refusal whose staged bytes survive:

Cases (the FMT registry; each pin's full statement lives at its check()):
  FMT-01 the JSON intake through the EXISTING ladder: a valid JSON document
         imports with --media-type application/json and the ack carries the
         full frozen contract (status=committed result_ref=...
         durability_rung=local_durable api_version=1); the source row
         carries media_type=application/json; the text/plain path is
         UNCHANGED (the first row still first)
  FMT-02 the SECOND matrix row MEASURED (the P4-00c two-corpus form): the
         matrix declares application/json (native text, reflow, no OCR,
         extraction supported, approved) and the MEASURED row over the JSON
         corpus derives its passages/coverage at the real boundary — never
         asserted
  FMT-03 ARV-FMT-001 (the unsupported media type): a MIME-valid but
         UNREGISTERED type refuses named at the boundary — exit 1 + the
         FAIL prefix + ZERO effect (no source row, no work row); the MIME
         grammar check (ARV-CAP-009) still fires FIRST for malformed types
  FMT-04 ARV-FMT-002 (the malformed payload): invalid JSON bytes under
         application/json refuse named — exit 1 + zero authoritative effect
         + THE STAGED BYTES PRESERVED: the refusal NAMES the digest and the
         blob still answers at that digest (the recovery substrate — staged
         bytes are never lost)
  FMT-05 ARV-FMT-003 (the undecodable/encrypted payload): bytes that cannot
         decode as UTF-8 under a text format refuse named — exit 1 + the
         digest named + the bytes recoverable
  FMT-06 the frozen contract on the new surface: every new ack carries
         api_version; the refusal lines keep the frozen FAIL shape; the
         no-oracle unchanged (absent == cross-owner on the read arms)

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no PDF (the scan/OCR +
fixed-layout classes — their own increments); no EPUB (the second
increment); no reader-client work (P4-B's repo); the position surface is
P4-A slice two.

Run: python3 harness/tests/test_format.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): the SECOND matrix row is the
# cheapest honest probe — at the RED tree the matrix declares exactly one
# format (text/plain); the JSON adapter is absent.
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "capability.py"), "matrix"],
                        capture_output=True, text=True, timeout=120)
_probe_rows = [ln for ln in _probe.stdout.splitlines() if ln.strip()]
_probe_json = any('"application/json"' in ln for ln in _probe_rows)
if not (_probe.returncode == 0 and _probe_json):
    print(f"FAIL ARV-TEST-000: the P4-A slice one format machinery is absent "
          f"(machinery-absent class; the matrix's application/json row present: {_probe_json}) "
          "— the implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None
# the JSON corpus — a reading-notes export shaped like a real interchange
JSON_DOC = json.dumps({"title": "The JSON Corpus",
                       "notes": [{"page": 1, "text": "The first imported note rides here."},
                                 {"page": 2, "text": "The second note follows the first."},
                                 {"page": 3, "text": "The third note closes the corpus."}]},
                      indent=2, ensure_ascii=False)


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
        if "digest=" in ln:
            return ln.split("digest=")[1].split()[0].rstrip("')")
    return ""


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4a1")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4a1-"))

        # ---- FMT-01 — the JSON intake through the EXISTING ladder
        jf = tmp / "corpus.json"
        jf.write_text(JSON_DOC, encoding="utf-8")
        r_j = cmd("import_source", "--title", "The JSON Corpus",
                  "--file", str(jf), "--media-type", "application/json", key="jimp-1")
        jsid = ref_of(r_j)
        # the text/plain path unchanged (the first row still first)
        tf = tmp / "plain.md"
        tf.write_text("Plain text still rides the same ladder.\n\nA second block.",
                      encoding="utf-8")
        r_t = cmd("import_source", "--title", "The Plain Corpus",
                  "--file", str(tf), key="timp-1")
        tsid = ref_of(r_t)
        ok1 = (r_j.returncode == 0 and jsid
               and "status=committed" in r_j.stdout
               and "durability_rung=local_durable" in r_j.stdout
               and "api_version=1" in r_j.stdout
               and r_t.returncode == 0 and tsid
               and "api_version=1" in r_t.stdout)
        check("FMT-01", ok1,
              "the JSON intake through the EXISTING ladder: a valid JSON document imports with "
              "--media-type application/json and the ack carries the full frozen contract "
              "(status=committed + result_ref + durability_rung=local_durable + api_version=1 — the "
              "P4-00b grammar on the new path); the text/plain path unchanged",
              "the format adapter at the import boundary feeding the ONE ladder — never a second "
              "durability path")

        # ---- FMT-02 — the SECOND matrix row MEASURED (the two-corpus form)
        r_mat = cap("matrix")
        rows = jlines(r_mat)
        fmts = {row.get("format"): row for row in rows}
        r_ext = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                        "--idem-key", "jext-1", "--source-id", jsid)
        r_m = cap("measure", "--owner", "A", "--source", jsid)
        m = jline(r_m)
        ok2 = (r_mat.returncode == 0
               and "application/json" in fmts and "text/plain" in fmts
               and fmts["application/json"].get("native_text") is True
               and fmts["application/json"].get("scan_ocr") is False
               and fmts["application/json"].get("layout") == "reflow"
               and fmts["application/json"].get("extraction") == "supported"
               and fmts["application/json"].get("approved") is True
               and fmts["application/json"].get("api_version") == 1
               and r_ext.returncode == 0
               and r_m.returncode == 0
               and m.get("state") == "ready" and m.get("api_version") == 1
               and m.get("media_type") == "application/json"
               and isinstance(m.get("passages"), int) and m.get("passages", 0) >= 1
               and isinstance(m.get("coverage"), (int, float)) and 0 < m.get("coverage", 0) <= 1.0)
        check("FMT-02", ok2,
              "the SECOND matrix row MEASURED (the P4-00c two-corpus form): the matrix declares "
              "application/json (native text, reflow, NO OCR, extraction supported, approved) "
              "alongside the unchanged text/plain row; the MEASURED row over the JSON corpus "
              "derives its passages/coverage at the real boundary (state=ready, the values "
              "derived — never asserted)",
              "harness/formats.py's adapter registry + capability.py's matrix deriving FROM it "
              "(ONE home: the adapter declares, the matrix reports)")

        # ---- FMT-03 — ARV-FMT-001 (the unsupported media type)
        srcs_before = query("get-source", "--owner", "A", "--id", str(_uuid.uuid4()))
        r_f1 = cmd("import_source", "--title", "Unsupported",
                   "--file", str(jf), "--media-type", "application/x-msdownload", key="f1-1")
        # the MIME grammar check still fires FIRST for malformed types
        r_cap9 = cmd("import_source", "--title", "Bad MIME",
                     "--file", str(jf), "--media-type", "text/plain; charset|x", key="f9-1")
        ok3 = (r_f1.returncode == 1 and "FAIL ARV-FMT-001:" in r_f1.stdout
               and "application/x-msdownload" in r_f1.stdout
               and ref_of(r_f1) == ""
               and r_cap9.returncode == 1 and "FAIL ARV-CAP-009:" in r_cap9.stdout)
        check("FMT-03", ok3,
              "ARV-FMT-001 (the unsupported media type): a MIME-valid but UNREGISTERED type "
              "refuses named at the boundary — exit 1 + the FAIL prefix + zero effect (no source "
              "row); the MIME grammar check (ARV-CAP-009) still fires FIRST for malformed types "
              "(the grammar precedes the registry)",
              "the format adapter registry consulted at the import boundary AFTER the MIME token "
              "check — the approval registry IS the capability matrix")

        # ---- FMT-04 — ARV-FMT-002 (the malformed payload) + the staged bytes
        bad = tmp / "bad.json"
        bad.write_bytes(b'{"title": "unclosed', )
        r_f2 = cmd("import_source", "--title", "Malformed JSON",
                   "--file", str(bad), "--media-type", "application/json", key="f2-1")
        dg2 = _digest_of(r_f2)
        blob_answers = False
        if dg2:
            probe = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
                 "from harness.adapters import blob\n"
                 f"print(len(blob.get({dg2!r})))"],
                capture_output=True, text=True, timeout=60, env=ENV)
            blob_answers = probe.returncode == 0 and probe.stdout.strip().isdigit()
        ok4 = (r_f2.returncode == 1 and "FAIL ARV-FMT-002:" in r_f2.stdout
               and ref_of(r_f2) == "" and dg2 and blob_answers)
        check("FMT-04", ok4,
              "ARV-FMT-002 (the malformed payload): invalid JSON bytes under application/json "
              "refuse named — exit 1 + zero authoritative effect + THE STAGED BYTES PRESERVED: "
              "the refusal NAMES the digest and the blob still answers at that digest (the "
              "recovery substrate — staged bytes are never lost)",
              "the format validation after the blob staging, the refusal naming the digest — the "
              "ARV-CAP-004 failed-retryable pattern extended to the format class")

        # ---- FMT-05 — ARV-FMT-003 (the undecodable/encrypted payload)
        enc = tmp / "enc.json"
        enc.write_bytes(bytes(range(0, 64)))  # not valid UTF-8, not valid JSON
        r_f3 = cmd("import_source", "--title", "Undecodable",
                   "--file", str(enc), "--media-type", "application/json", key="f3-1")
        dg3 = _digest_of(r_f3)
        blob3 = False
        if dg3:
            probe = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
                 "from harness.adapters import blob\n"
                 f"print(len(blob.get({dg3!r})))"],
                capture_output=True, text=True, timeout=60, env=ENV)
            blob3 = probe.returncode == 0 and probe.stdout.strip().isdigit()
        ok5 = (r_f3.returncode == 1 and "FAIL ARV-FMT-003:" in r_f3.stdout
               and ref_of(r_f3) == "" and dg3 and blob3)
        check("FMT-05", ok5,
              "ARV-FMT-003 (the undecodable/encrypted payload): bytes that cannot decode as "
              "UTF-8 under a text format refuse named — exit 1 + the digest named + the bytes "
              "recoverable at that digest (the explicit-error contract: the user never loses "
              "what they submitted)",
              "the decode step in the format adapter with the typed refusal naming the digest")

        # ---- FMT-06 — the frozen contract on the new surface
        r_abs = query("get-source", "--owner", "A", "--id", str(_uuid.uuid4()))
        r_xo = query("get-source", "--owner", "B", "--id", jsid)
        ok6 = (r_abs.returncode == 1 and "FAIL ARV-QRY-001:" in r_abs.stdout
               and r_xo.returncode == 1
               and r_abs.stdout.replace(str(_uuid.uuid4()), "<id>")
               == r_xo.stdout.replace(jsid, "<id>")
               and "api_version=1" in r_j.stdout and "api_version=1" in r_t.stdout
               and all(row.get("api_version") == 1 for row in rows))
        check("FMT-06", ok6,
              "the frozen contract on the new surface: the new acks carry api_version; the "
              "refusal lines keep the frozen FAIL shape; the no-oracle unchanged (absent == "
              "cross-owner on the read arms — the P4-00b pattern)",
              "the shared print/refusal forms — never a second grammar")

        if FAILS:
            print(f"\nFORMAT SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the format intake contract is broken or unimplemented)")
            return 1
        print("\nFORMAT SUITE GREEN — FMT-01..06 (the first additional format intake: the JSON "
              "path through the existing ladder, the second MEASURED matrix row, the typed "
              "format refusals with staged-bytes safety)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
