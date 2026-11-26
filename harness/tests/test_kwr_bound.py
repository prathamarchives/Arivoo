#!/usr/bin/env python3
"""harness/tests/test_kwr_bound.py — F6's kernel follow-up suite (CLAIM-095;
the long-unbroken-token / keyword-index btree row-size boundary; runbook
§11.2's routed defect — record 79 §6: "F6's exact minimum trigger size").
Red-first (LAW-11): at the pre-slice main `1eab74a` the suite fails with the
named-code class (the bound ARV-KWR-002/003 does not exist; the over-bound
import dies inside the metadata transaction with the DB-side crash class the
F6 finding named — ARV-CMD-010, proven reachable through the import route;
the query arm accepts any term length).

THE CONTRACT (the bounded tokenizer/index-input law): every token the
keyword layer writes or queries is bounded in UTF-8 BYTES at ONE home
(commands.py's KWR_TOKEN_MAX_BYTES — the kernel constant; query.py imports
it, never re-declares it). PostgreSQL's btree leaf insert refuses a single
index row over BTMaxItemSize (~2704 bytes for the 8k default block size —
"index row size X exceeds btree version 4 maximum 2704"; the keyword_index
composite PK and the keyword_index_token secondary index both carry the
token column). THE F6 SPIKE FINDING (observed live on the 17.12 rig, this
slice's red work): the limit fires on the TOAST-COMPRESSED datum, so a
repeated-character run compresses to near-nothing and inserts FINE — the
actual crash class requires an INCOMPRESSIBLE unbroken run (~3000 mixed
chars observed crashing; compressible runs never do). The kernel cannot
predict the server's compression outcome, so the bound is on the RAW UTF-8
byte length of the token: 512 bytes, far under the ~2620 effective floor
(2704 minus the composite key's fixed members) with margin for any
production owner identifier. A capture whose text produces an over-bound
token is REFUSED with the named ARV-KWR-002 code and ZERO partial effect on
the authoritative layer (the import's staged-bytes contract holds: the
journal row records failed(ARV-KWR-002) retryable, the bytes stay
recoverable, no Source/Work/command_log/index row is born). A query term
over the same bound refuses ARV-KWR-003 — a term the index can never hold
is a named refusal, never a silent empty result (the KWR-07 explicit-failure
law applied to the read side). All NORMAL tokens, Unicode, CJK, accents and
multi-term semantics are UNCHANGED (the no-regression pins); the
idempotency semantics are preserved (a refused key records nothing on the
command_log — the retry with corrected input reuses the key cleanly).

Refusal codes: ARV-KWR-002 the index-input token bound (write side);
ARV-KWR-003 the term bound (read side — search and pack arms). The
highlight/bookmark windows are safe BY CONSTRUCTION (a window's runs are
sub-runs of the source's runs; an over-bound window implies the over-bound
source that was already refused).

Cases (the KBND registry):
  KBND-01 the import refusal: an over-bound unbroken token in a source
         text → FAIL ARV-KWR-002, exit 1, the journal row
         failed(ARV-KWR-002) retryable, ZERO Source/Work/command_log/
         keyword_index rows, the staged bytes preserved (recoverable)
  KBND-02 the bound edge: a token AT the bound (512 ASCII bytes) imports
         GREEN, is searchable whole-token, and rebuilds; one byte over
         refuses — the boundary is exact, never a fuzzy clamp
  KBND-03 the note path + idempotency: create_note with an over-bound
         token → FAIL ARV-KWR-002, zero note/index/command_log rows, and
         the SAME idem key retried with clean content ACKs status=created
         (a refusal records nothing — the key stays reusable)
  KBND-04 the Unicode/CJK boundary: normal CJK text (single chars + the
         whole-run token under the bound) imports and searches as before;
         an unbroken CJK run over the BYTE bound (171 chars = 513 bytes)
         refuses; accented/combining text is unchanged
  KBND-05 the adversarial class (F6's exact trigger): a 4000-char unbroken
         Latin run (the btree-exceeding class) → the NAMED refusal
         ARV-KWR-002, never ARV-CMD-010, never a DB-side crash, zero
         partial effect
  KBND-06 the query arm parity: search with an over-bound term refuses
         ARV-KWR-003; pack with an over-bound term the same; normal
         terms return the standing corpus results unchanged
  KBND-07 the ONE home: query.py imports KWR_TOKEN_MAX_BYTES from
         commands.py (no second bound constant anywhere in the repo's
         kernel modules — the parity is structural, both sides fire at
         the same threshold)

Run: python3 harness/tests/test_kwr_bound.py   (exit 0 = green)
"""
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


from harness.adapters import pg  # noqa: E402

DB = ENV = None
BOUND = 512  # KWR_TOKEN_MAX_BYTES's value — the suite pins the boundary itself


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


def mk_note(key, content, owner="A") -> subprocess.CompletedProcess:
    return cmd("create_note", "--content", content, key=key, owner=owner)


def search(owner, *terms) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), "search", "--owner", owner,
               *[t for t in terms])


def pack(owner, *terms) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), "pack", "--owner", owner,
               *[t for t in terms])


def audit(query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-U", "arv_read", "-d", DB, "-c", query],
                           capture_output=True, text=True, timeout=60,
                           env=ENV).stdout.strip()


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def result_ids(p: subprocess.CompletedProcess) -> list:
    out = []
    for ln in p.stdout.split("\n"):
        if ln.strip() and not ln.lstrip().startswith("#"):
            out.append(ln.strip())
    return out


def _src_file(text: str) -> str:
    p = pathlib.Path(tempfile.mkdtemp(prefix="arv-kbnd-")) / "src.txt"
    p.write_text(text, encoding="utf-8")
    return str(p)


def _incompressible(n: int, seed: int = 7) -> str:
    """A deterministic mixed-case alphanumeric run of n chars — the pglz
    class TOAST compression cannot shrink (the F6 spike's finding: a repeated
    character run compresses to near-nothing BEFORE the index tuple is built,
    so only incompressible long runs actually hit the btree row limit; a
    deterministic LCG keeps the suite reproducible, no ambient randomness
    (LAW-24))."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    out, s = [], seed
    for _ in range(n):
        s = (s * 1103515245 + 12345) % (2 ** 31)
        out.append(alphabet[s % len(alphabet)])
    return "".join(out)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p95")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)

        # ---- KBND-01 — the import refusal (named code + zero partial effect)
        tok = "q" * (BOUND + 48)  # 560 bytes — comfortably over, well under the crash class
        p1 = import_src("kbnd-1", "The Long Run", _src_file("plain lead text " + tok + " tail"))
        jr = audit("SELECT state || '|' || COALESCE(fail_reason,'') FROM arv.import_journal "
                   "WHERE idempotency_key='kbnd-1';")
        no_source = audit("SELECT count(*) FROM arv.source;") == "0"
        no_work = audit("SELECT count(*) FROM arv.work;") == "0"
        no_log = audit("SELECT count(*) FROM arv.command_log;") == "0"
        no_index = audit("SELECT count(*) FROM arv.keyword_index;") == "0"
        ok1 = (p1.returncode == 1 and "FAIL ARV-KWR-002" in p1.stdout
               and jr == "failed|ARV-KWR-002"
               and no_source and no_work and no_log and no_index)
        check("KBND-01", ok1,
              "the import refusal: a source text with an over-bound unbroken token refuses "
              "FAIL ARV-KWR-002 (exit 1), the journal row records failed(ARV-KWR-002) retryable, "
              "and ZERO authoritative rows are born (no source, no work, no command_log, no index "
              "rows) — the staged bytes stay recoverable per the import state machine",
              "the kernel's tokenizer bound must refuse BEFORE the metadata transaction; the "
              "journal row must carry the named code, never a DB-side crash (F6's class)")

        # ---- KBND-02 — the bound edge (at-bound OK; one over refuses)
        at_bound = "b" * BOUND  # exactly 512 bytes — the largest accepted token
        p2a = import_src("kbnd-2a", "At The Bound", _src_file("edge " + at_bound + " end"))
        sid = ack_field(p2a, "result_ref")
        r2 = search("A", at_bound)
        p2b = import_src("kbnd-2b", "One Over", _src_file("edge " + "c" * (BOUND + 1) + " end"))
        ok2 = (p2a.returncode == 0 and sid
               and r2.returncode == 0 and any(f"source|{sid}" in ln for ln in result_ids(r2))
               and p2b.returncode == 1 and "FAIL ARV-KWR-002" in p2b.stdout
               and audit("SELECT count(*) FROM arv.source;") == "1")
        check("KBND-02", ok2,
              "the bound edge: a token AT the bound imports green, is searchable whole-token; "
              "one byte over refuses the same named code — the boundary is exact (never a fuzzy "
              "clamp, never a silent truncation)",
              "the byte-length comparison must be exact: > bound refuses, == bound is accepted "
              "and indexable")

        # ---- KBND-03 — the note path + the idempotency preservation
        p3a = mk_note("kbnd-3", "note lead " + "d" * (BOUND * 2) + " tail")
        no_note = audit("SELECT count(*) FROM arv.note;") == "0"
        no_log3 = audit("SELECT count(*) FROM arv.command_log;") == "1"  # import kbnd-2a's row only
        no_index3 = audit("SELECT count(*) FROM arv.keyword_index WHERE kind='note';") == "0"
        p3b = mk_note("kbnd-3", "the corrected note content with normal words")
        n3 = ack_field(p3b, "result_ref")
        ok3 = (p3a.returncode == 1 and "FAIL ARV-KWR-002" in p3a.stdout
               and no_note and no_log3 and no_index3
               and p3b.returncode == 0 and n3
               and audit(f"SELECT count(*) FROM arv.note WHERE id='{n3}';") == "1")
        check("KBND-03", ok3,
              "the note path: an over-bound token in note content refuses ARV-KWR-002 with zero "
              "note/index/command_log rows, and the SAME idem key retried with corrected content "
              "ACKs created — a refusal records nothing on the command_log, so the key stays "
              "reusable (idempotency semantics preserved)",
              "the refusal must precede the command_log write; the retry with the same key and "
              "a clean body must never see a 409")

        # ---- KBND-04 — the Unicode/CJK boundary
        cjk_ok = "正常的中文笔记，带标点断句。独占一行的词汇。"
        p4a = mk_note("kbnd-4a", cjk_ok)
        r4a = search("A", "中")
        cjk_over = "汉" * 171  # 171 × 3 bytes = 513 bytes — one over the bound
        p4b = mk_note("kbnd-4b", "lead " + cjk_over)
        acc = "café über ﬁne—note with é and combining maïs"
        p4c = mk_note("kbnd-4c", acc)
        r4c = search("A", "maïs")
        ok4 = (p4a.returncode == 0 and r4a.returncode == 0 and result_ids(r4a)
               and p4b.returncode == 1 and "FAIL ARV-KWR-002" in p4b.stdout
               and p4c.returncode == 0 and r4c.returncode == 0 and result_ids(r4c))
        check("KBND-04", ok4,
              "the Unicode boundary: normal CJK text (punctuation-broken runs) imports and "
              "searches by single character exactly as before; an unbroken CJK run over the BYTE "
              "bound (171 chars = 513 bytes) refuses; accented/combining text is unchanged — "
              "the bound is measured in UTF-8 bytes, never code points",
              "the tokenizer's bound check must use the run's UTF-8 encoded length; every "
              "standing CJK/accent behavior must be byte-identical to the pre-slice suite")

        # ---- KBND-05 — the adversarial class (F6's exact trigger)
        # incompressible content is REQUIRED: the spike proved repeated-character
        # runs are TOAST-compressed before the index tuple is built (they insert
        # fine); the btree row limit fires only on the COMPRESSED size — an
        # incompressible 4000-char run is the proven crash class
        crash_tok = _incompressible(4000)
        p5 = import_src("kbnd-5", "The Crash Class", _src_file("lead " + crash_tok + " tail"))
        # the index bound holds GLOBALLY (no over-bound token anywhere, any kind);
        # the only committed source remains kbnd-2a's with its exact 3-token set
        ok5 = (p5.returncode == 1 and "FAIL ARV-KWR-002" in p5.stdout
               and "ARV-CMD-010" not in p5.stdout
               and "error" not in (p5.stderr or "").lower()
               and audit("SELECT count(*) FROM arv.source;") == "1"
               and audit("SELECT count(*) FROM arv.keyword_index WHERE "
                         "octet_length(token) > 512;") == "0"
               and audit("SELECT count(*) FROM arv.keyword_index WHERE kind='source';") == "3")
        check("KBND-05", ok5,
              "the adversarial class: an INCOMPRESSIBLE 4000-char unbroken run (the btree "
              "row-size exceeding class — F6's exact trigger: the spike observed 'index row "
              "size 3016 exceeds btree version 4 maximum 2704' live on the 17.12 rig for a "
              "3000-char incompressible token, proven reachable through the import route) "
              "refuses with the NAMED ARV-KWR-002, never ARV-CMD-010, never a DB-side crash; "
              "no token over the bound exists anywhere in the index and the one committed "
              "source keeps its exact 3-token set",
              "the bound must fire at validation time on the RAW byte length — the INSERT "
              "must never be reached with an over-bound token (the pre-slice tree dies "
              "inside the metadata transaction on the incompressible class)")

        # ---- KBND-06 — the query arm parity (search + pack)
        r6a = search("A", "w" * (BOUND + 10))
        r6b = search("A", at_bound)  # normal-length term still works
        r6c = pack("A", "v" * (BOUND + 10))
        ok6 = (r6a.returncode == 1 and "FAIL ARV-KWR-003" in r6a.stdout
               and r6b.returncode == 0 and any(f"source|{sid}" in ln for ln in result_ids(r6b))
               and r6c.returncode == 1 and "FAIL ARV-KWR-003" in r6c.stdout)
        check("KBND-06", ok6,
              "the query arm parity: an over-bound search term refuses ARV-KWR-003 (a term the "
              "index can never hold is a named refusal, never a silent empty result, never a "
              "crash); the pack arm refuses the same; normal terms return the standing corpus "
              "results unchanged",
              "the read side must enforce the same bound at the term boundary with its own "
              "named code — imported from the kernel's single constant, never re-declared")

        # ---- KBND-07 — the ONE home (the structural parity)
        src_c = pathlib.Path(REPO / "harness" / "commands.py").read_text(encoding="utf-8")
        src_q = pathlib.Path(REPO / "harness" / "query.py").read_text(encoding="utf-8")
        ok7 = ("KWR_TOKEN_MAX_BYTES = " in src_c
               and "from harness.commands import" in src_q
               and "KWR_TOKEN_MAX_BYTES" in src_q
               and "KWR_TOKEN_MAX_BYTES = " not in src_q)
        check("KBND-07", ok7,
              "the ONE home: the bound constant is declared exactly once (commands.py, the "
              "tokenizer's home) and imported by query.py — no second bound constant exists in "
              "the read kernel (the structural parity: both sides fire at the same threshold)",
              "the write and read kernels must share the single kernel constant; a re-declared "
              "bound would drift (the one-fact-one-home law)")

        if FAILS:
            print(f"\nRED — {len(FAILS)} check(s) failing: {', '.join(FAILS)}")
            return 1
        print("\nGREEN — the F6 token-bound suite (KBND-01..07) passes")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
