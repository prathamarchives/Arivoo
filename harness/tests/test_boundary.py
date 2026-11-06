#!/usr/bin/env python3
"""harness/tests/test_boundary.py — P4-00b acceptance suite (CLAIM-063, the
client-contract freeze + the boundary test; PLAN's elaborated P4-00b card;
the Phase 3 exit gate's uncoached acceptance path made mechanical — record 53's
walk re-run as a PERMANENT suite at the REAL boundary).
Red-first (LAW-11): at CLAIM-062's merged head 54533c6 the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — the version field, the replayed
rungs, and the bounded lists are absent.

THE CONTRACT (the freeze — RTM §4.3/SYS-01's letter on every path): the
client-facing surface is a FROZEN vocabulary, pinned here so it changes only
through this contract's own change process:

Cases (the BND registry; each pin's full statement lives at its check()):
  BND-01 the version field on every WRITE ack: every ACK line — commands.py's
         full verb census AND extract.py's acks, committed AND replayed —
         carries api_version=1 (the compatibility matrix's foundation,
         P4-00c's)
  BND-02 the replayed acks carry the rung (the F3 residual, record 54 §3):
         the REPLAYED forms of the capture families' acks and record_event's
         ack (its committed form too) carry durability_rung=local_durable —
         SYS-01's every-write rule holds on EVERY acknowledgment path
  BND-03 the ack grammar frozen (the DTO vocabulary, RTM §4.3 item 3): every
         success ack parses as k=v tokens carrying command/idem_key/status/
         result_ref/durability_rung/api_version — status in the frozen pair
         {committed, replayed}; durability_rung in SYS-01's frozen four
         {in_flight, local_durable, queued, server_durable}; no token repeats
  BND-04 the typed-error surface as the contract: the acceptance run's codes
         each refuse with their frozen shape (exit 1 + 'FAIL ARV-XXX-NNN:' +
         zero effect): ARV-CMD-409 (key/body conflict), ARV-CAP-006/007
         (import refusals), ARV-NTE-006 (malformed ref), ARV-QRY-001
         (absent == cross-owner, byte-identical — no existence oracle),
         ARV-QRY-003 (tombstoned read), ARV-QRY-004 (the list-bounds
         refusal — new with this slice)
  BND-05 the list arms bounded + paginated: --limit (default 100, bounds
         1..1000) + --after (the keyset cursor); every response opens with
         the version header and closes with the truth marker '# more='; the
         default page is bounded (101 fixtures -> exactly 100 + more=true);
         the paged walk's union equals the full walk, monotone, no dups; the
         empty owner answers header + more=false alone (never silence)
  BND-06 the version field on every READ surface: the JSON bodies
         (get-capture/get-source/get-note/get-bookmark/resolve-anchor) and
         every history row carry "api_version": 1; the search header and the
         list headers carry api_version=1

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): the format capability
matrix is P4-00c/P4-A's; the read-position surface is P4-A/B's; no
reader-client work (the separate repo). export.py's RESTORED line and
migrate.py's operator output are NOT the client API — their version field is
a later slice's call, disclosed in notverified.txt.

Run: python3 harness/tests/test_boundary.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): the version field is the
# cheapest honest probe — one record_event ack against a THROWAWAY scratch
# DB; at the RED tree the ack carries no api_version token (LAW-11; the
# CON/EXP machinery-absent precedent). The probe's database is dropped in
# its own finally — a probe never leaks side effects.
_probe_db = pg.create_scratch_db("p400bprobe")
try:
    _pm = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                         capture_output=True, text=True, timeout=180,
                         env=dict(os.environ, PGDATABASE=_probe_db))
    _pe = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                          "record_event", "--owner", "A", "--actor", "owner",
                          "--client-id", "cli-1", "--idem-key", "probe-1",
                          "--payload", "probe"],
                         capture_output=True, text=True, timeout=120,
                         env=dict(os.environ, PGDATABASE=_probe_db))
    _probe_ack = next((ln for ln in _pe.stdout.splitlines()
                       if ln.startswith("ACK ")), "")
    _probe_ok = (_pm.returncode == 0 and _pe.returncode == 0
                 and "api_version=" in _probe_ack)
finally:
    pg.drop_scratch_db(_probe_db)
if not _probe_ok:
    print(f"FAIL ARV-TEST-000: the P4-00b client-contract machinery is absent "
          f"(machinery-absent class; the write ack's api_version token: "
          f"{_probe_ack!r}) — the implementation lands after this RED, never "
          "before it (LAW-11)")
    sys.exit(1)

SRC = ENV = None
TEXT = ("The boundary corpus: the frozen contract rides here.\n"
        "A second line so the pagination walk has somewhere to stand.\n")

# the ack census — every ACK line the suite observes (BND-01/02/03 walk it)
ACKS: list[str] = []


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


def cmd(op: str, *args, owner="A", key=None, env=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    r = cli(*a, *args, env=env)
    ACKS.extend(ln for ln in r.stdout.splitlines() if ln.startswith("ACK "))
    return r


def query(*args, env=None) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args, env=env or ENV)


def extract(*args, env=None) -> subprocess.CompletedProcess:
    r = cli(str(REPO / "harness" / "extract.py"), *args, env=env or ENV)
    ACKS.extend(ln for ln in r.stdout.splitlines() if ln.startswith("ACK "))
    return r


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", SRC, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def ref_of(r: subprocess.CompletedProcess) -> str:
    for ln in r.stdout.splitlines():
        if ln.startswith("ACK") and "result_ref=" in ln:
            return ln.split("result_ref=")[1].split()[0]
    return ""


def ack_tokens(line: str) -> list:
    """The ack grammar's k=v token pairs (BND-03's parser — a token without
    '=' is a grammar break, reported by its absence from the pairs)."""
    out = []
    for t in line.split():
        k, sep, v = t.partition("=")
        if sep:
            out.append((k, v))
    return out


def list_ids(r: subprocess.CompletedProcess) -> list:
    """The list arm's id rows — the '#' label lines are never ids (the
    search-header convention; KWR's own skip form)."""
    return [ln for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def list_more(r: subprocess.CompletedProcess) -> str:
    for ln in r.stdout.splitlines():
        if ln.startswith("# more="):
            return ln.split("=", 1)[1]
    return ""


def main() -> int:
    global SRC, ENV
    SRC = pg.create_scratch_db("p400b")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=SRC, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)

        # ---- the fixture: the day-one path (owner A) + the pagination lab
        # (owner C: 101 notes) + the empty owner (B)
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-p400b-")) / "corpus.md"
        src_file.write_text(TEXT, encoding="utf-8")
        r_imp = cmd("import_source", "--title", "The Boundary Corpus",
                    "--file", str(src_file), key="imp-1")
        sid = ref_of(r_imp)
        r_ext = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                        "--idem-key", "ext-1", "--source-id", sid)
        r_hl = cmd("create_highlight", "--source-id", sid, "--start", "0",
                   "--end", "30", key="hl-1")
        hl1 = ref_of(r_hl)
        r_hl2 = cmd("create_highlight", "--source-id", sid, "--start", "31",
                    "--end", "45", key="hl-2")
        hl2 = ref_of(r_hl2)
        r_bm = cmd("create_bookmark", "--source-id", sid, "--start", "0",
                   "--end", "10", key="bm-1")
        bm1 = ref_of(r_bm)
        # the census fixtures (SEV round-1 F2 repair: EVERY registered verb
        # walks the census — the five unwalked verbs + the bookmark/note
        # replayed forms + one lifecycle replay)
        r_bm2 = cmd("create_bookmark", "--source-id", sid, "--start", "20",
                    "--end", "30", key="bm-2")
        bm2 = ref_of(r_bm2)
        r_nt = cmd("create_note", "--content", "the frozen contract note",
                   "--ref", f"highlight:{hl1}@1", key="nt-1")
        n1 = ref_of(r_nt)
        r_nt2 = cmd("create_note", "--content", "the census note", key="nt-2")
        n2 = ref_of(r_nt2)
        r_ev = cmd("record_event", "--payload", "the boundary census", key="ev-1")
        cmd("revise_note", "--id", n1, "--content", "the frozen contract note, revised",
            key="rev-1")
        cmd("tombstone_note", "--id", n2, key="tn-2")
        cmd("restore_note", "--id", n2, key="rn-2")
        cmd("revise_highlight", "--id", hl1, "--start", "0", "--end", "30", key="rh-1")
        cmd("move_bookmark", "--id", bm1, "--start", "5", "--end", "15", key="mb-1")
        cmd("tombstone_bookmark", "--id", bm2, key="tb-2")
        cmd("restore_bookmark", "--id", bm2, key="rb-2")
        cmd("tombstone_bookmark", "--id", bm2, key="tb-2b")  # ends hidden: the list pin keeps its shape
        cmd("tombstone_highlight", "--id", hl2, key="th-2")
        cmd("restore_highlight", "--id", hl2, key="rhh-2")
        r_rb = cmd("rebuild_keyword_index", key="rb-1")

        # the REPLAYS (same key + same canonical body) — the replayed ack
        # census (BND-02's fixtures: every replayable family)
        r_imp_rp = cmd("import_source", "--title", "The Boundary Corpus",
                       "--file", str(src_file), key="imp-1")
        r_ext_rp = extract("--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                           "--idem-key", "ext-1", "--source-id", sid)
        r_hl_rp = cmd("create_highlight", "--source-id", sid, "--start", "0",
                      "--end", "30", key="hl-1")
        r_bm_rp = cmd("create_bookmark", "--source-id", sid, "--start", "0",
                      "--end", "10", key="bm-1")
        r_nt_rp = cmd("create_note", "--content", "the census note", key="nt-2")
        r_ev_rp = cmd("record_event", "--payload", "the boundary census", key="ev-1")
        r_tn_rp = cmd("tombstone_note", "--id", n2, key="tn-2")  # the lifecycle replay (the spine's shared path)
        r_rb_rp = cmd("rebuild_keyword_index", key="rb-1")
        # THE CENSUS SNAPSHOT — the exact structure pin (SEV round-1 F2: the
        # floor form >= 14 let a silently-broken verb leave the suite green;
        # the snapshot pins the census's exact shape)
        CENSUS = list(ACKS)
        census_verbs = {ack_tokens(ln)[0][1] for ln in CENSUS}
        replayed_verbs = {ack_tokens(ln)[0][1] for ln in CENSUS
                          if "status=replayed" in ln}

        # ---- BND-02 — the replayed acks carry the rung (the F3 residual)
        replayed = [ln for ln in CENSUS if "status=replayed" in ln]
        ok2 = (len(replayed) == 8
               and all("durability_rung=local_durable" in ln for ln in replayed)
               and all("api_version=" in ln for ln in replayed)
               # record_event's COMMITTED ack carries the rung too (the F3
               # residual's other half — its build rode the spine with an
               # empty extra)
               and "durability_rung=local_durable" in r_ev.stdout
               and "durability_rung=local_durable" in r_hl.stdout
               and "durability_rung=local_durable" in r_rb.stdout
               and "durability_rung=local_durable" in r_ext.stdout)
        check("BND-02", ok2,
              "the replayed acks carry the rung: all EIGHT replayed forms in the census (import/extract/"
              "highlight/bookmark/note/record_event/rebuild + the lifecycle replay) AND record_event's "
              "committed ack name durability_rung=local_durable + api_version — SYS-01's every-write "
              "rule holds on EVERY acknowledgment path (the F3 residual, record 54 §3, closed)",
              "commands.py's replay print sites (the spine's replay + conflict paths + record_event's "
              "build extra) and extract.py's replayed ack: append the rung + the version token")

        # ---- BND-01 — the version field on every write ack (the FULL verb
        # census — SEV round-1 F2: every registered verb, exactly)
        ALL_VERBS = {"record_event", "import_source", "create_highlight", "extract_source",
                     "revise_highlight", "tombstone_highlight", "restore_highlight",
                     "create_bookmark", "move_bookmark", "tombstone_bookmark", "restore_bookmark",
                     "create_note", "revise_note", "tombstone_note", "restore_note",
                     "rebuild_keyword_index"}
        ok1 = (len(CENSUS) == 28
               and census_verbs == ALL_VERBS
               and replayed_verbs == {"import_source", "extract_source", "create_highlight",
                                      "create_bookmark", "create_note", "record_event",
                                      "tombstone_note", "rebuild_keyword_index"}
               and all("api_version=1" in ln for ln in ACKS)
               and r_imp.returncode == 0 and r_ext.returncode == 0)
        check("BND-01", ok1,
              f"the version field on every write ack, the FULL census: the 28-line snapshot pins EVERY "
              "one of commands.py's 16 registered verbs (incl. revise_highlight/move_bookmark/"
              "tombstone_bookmark/restore_bookmark/restore_highlight — the SEV round-1 F2 repair) and "
              f"every replayable family's replayed form; all {len(ACKS)} ack lines the suite observes "
              "(the census + the later fixtures) carry api_version=1",
              "every ACK print site carries the api_version token — commands.py's spine/committed/"
              "replay/import sites + extract.py's two ack sites (ONE home: commands.API_VERSION)")

        # ---- BND-03 — the ack grammar frozen (the DTO vocabulary)
        STATUS = {"committed", "replayed"}
        RUNGS = {"in_flight", "local_durable", "queued", "server_durable"}
        REQUIRED = ("command", "idem_key", "status", "result_ref",
                    "durability_rung", "api_version")
        bad = []
        for ln in ACKS:
            toks = ack_tokens(ln)
            keys = [k for k, _ in toks]
            d = dict(toks)
            if (not all(k in d for k in REQUIRED)
                    or len(keys) != len(set(keys))
                    or d.get("status") not in STATUS
                    or d.get("durability_rung") not in RUNGS
                    or d.get("api_version") != "1"):
                bad.append(ln)
        ok3 = len(CENSUS) == 28 and not bad
        check("BND-03", ok3,
              f"the ack grammar frozen: every one of the {len(ACKS)} ack lines the suite observes "
              "(the 28-line census + every later fixture ack) parses as k=v tokens "
              "carrying command/idem_key/status/result_ref/durability_rung/api_version, no token "
              "repeats, status in {committed, replayed}, rung in SYS-01's frozen four "
              "{in_flight, local_durable, queued, server_durable} (RTM §4.3 item 3 — the DTO "
              "vocabulary; changes only through this contract's own change process)",
              "an ack line broke the frozen grammar: " + (bad[0] if bad else "(none)"))

        # ---- BND-04 — the typed-error surface as the contract
        # the QRY-003/list-hiding fixture: hl2 ends the census ACTIVE (the
        # restore_highlight walk) — re-tombstone it AFTER the census snapshot
        # (the 29th ack; not part of the 28-line structure pin)
        cmd("tombstone_highlight", "--id", hl2, key="th-2b")
        notes_before = int(audit("SELECT count(*) FROM arv.note;") or 0)
        srcs_before = int(audit("SELECT count(*) FROM arv.source;") or 0)
        # ARV-CMD-409: the key/body conflict
        r409 = cmd("create_highlight", "--source-id", sid, "--start", "0",
                   "--end", "31", key="hl-1")
        notes_409 = int(audit("SELECT count(*) FROM arv.note;") or 0)
        # ARV-CAP-006: import against a missing work
        miss_work = str(_uuid.uuid4())
        rcap6 = cmd("import_source", "--work-id", miss_work, "--file", str(src_file),
                    key="cap6-1")
        # ARV-CAP-007: both --title and --work-id
        rcap7 = cmd("import_source", "--title", "X", "--work-id", miss_work,
                    "--file", str(src_file), key="cap7-1")
        srcs_after = int(audit("SELECT count(*) FROM arv.source;") or 0)
        # ARV-NTE-006: the malformed reference kind
        rnte6 = cmd("create_note", "--content", "x", "--ref", "bogus:zzz", key="nte6-1")
        notes_after = int(audit("SELECT count(*) FROM arv.note;") or 0)
        # ARV-QRY-001: the no-existence-oracle — TWO directions (SEV round-1
        # F1 repair: the original pin compared absent-vs-absent, vacuous):
        # (a) CROSS-OWNER: B reads A's REAL objects — the refusal must be
        #     byte-identical to B's absent-id refusal at the TEMPLATE level
        #     (the queried id normalized out: a leak would differ anywhere
        #     else — the code, the wording, the shape)
        # (b) READER-INDEPENDENCE: the SAME absent id read as A and as B —
        #     byte-identical (the refusal never depends on the reader)
        absent_id = str(_uuid.uuid4())
        r_abs_A = query("get-capture", "--owner", "A", "--id", absent_id)
        r_abs_B = query("get-capture", "--owner", "B", "--id", absent_id)
        r_xo_cap = query("get-capture", "--owner", "B", "--id", hl1)
        r_xo_abs = query("get-capture", "--owner", "B", "--id", absent_id)
        r_xo_nt = query("get-note", "--owner", "B", "--id", n1)
        r_xo_nt_abs = query("get-note", "--owner", "B", "--id", absent_id)

        def _tmpl(out: str, qid: str) -> str:
            return out.replace(qid, "<id>")
        # ARV-QRY-003: the tombstoned read
        r_qry3 = query("get-capture", "--owner", "A", "--id", hl2)
        # ARV-QRY-004: the list-bounds refusals (the new typed code — incl.
        # the NON-INTEGER limit: the SEV round-1 F3 repair makes every bounds
        # violation the typed exit-1 shape, never argparse's exit-2 usage)
        r_l0 = query("list-notes", "--owner", "C", "--limit", "0")
        r_l1001 = query("list-notes", "--owner", "C", "--limit", "1001")
        r_lbad = query("list-notes", "--owner", "C", "--after", "not-a-uuid")
        r_lnan = query("list-notes", "--owner", "C", "--limit", "abc")
        ok4 = (r409.returncode == 1 and "FAIL ARV-CMD-409:" in r409.stdout
               and notes_409 == notes_before
               and rcap6.returncode == 1 and "FAIL ARV-CAP-006:" in rcap6.stdout
               and rcap7.returncode == 1 and "FAIL ARV-CAP-007:" in rcap7.stdout
               and srcs_after == srcs_before
               and rnte6.returncode == 1 and "FAIL ARV-NTE-006:" in rnte6.stdout
               and notes_after == notes_before
               and r_abs_A.returncode == 1 and "FAIL ARV-QRY-001:" in r_abs_A.stdout
               and r_abs_A.stdout == r_abs_B.stdout
               and r_xo_cap.returncode == 1 and "FAIL ARV-QRY-001:" in r_xo_cap.stdout
               and _tmpl(r_xo_cap.stdout, hl1) == _tmpl(r_xo_abs.stdout, absent_id)
               and r_xo_cap.stderr == r_xo_abs.stderr
               and r_xo_nt.returncode == 1 and "FAIL ARV-QRY-001:" in r_xo_nt.stdout
               and _tmpl(r_xo_nt.stdout, n1) == _tmpl(r_xo_nt_abs.stdout, absent_id)
               and r_qry3.returncode == 1 and "FAIL ARV-QRY-003:" in r_qry3.stdout
               and r_l0.returncode == 1 and "FAIL ARV-QRY-004:" in r_l0.stdout
               and r_l1001.returncode == 1 and "FAIL ARV-QRY-004:" in r_l1001.stdout
               and r_lbad.returncode == 1 and "FAIL ARV-QRY-004:" in r_lbad.stdout
               and r_lnan.returncode == 1 and "FAIL ARV-QRY-004:" in r_lnan.stdout)
        check("BND-04", ok4,
              "the typed-error surface as the contract: ARV-CMD-409 (key/body conflict, zero effect — "
              "note count unchanged), ARV-CAP-006/007 (import refusals, zero effect — source count "
              "unchanged), ARV-NTE-006 (malformed ref, zero effect), ARV-QRY-001 BOTH directions "
              "(cross-owner: B reading A's REAL capture/note refuses byte-identically to B's "
              "absent-id refusal at the template level — no existence oracle; reader-independence: "
              "the same absent id refuses identically for A and B), ARV-QRY-003 (tombstoned "
              "read), ARV-QRY-004 (limit 0 / limit 1001 / non-uuid cursor / non-integer limit) — "
              "each exit 1 + the 'FAIL ARV-XXX-NNN:' prefix (the frozen refusal shape)",
              "the refusal sites keep the typed shape; the list-bounds refusal (ARV-QRY-004) is new "
              "machinery — it lands with this slice")

        # ---- the pagination lab: owner C's 101 notes (the default bound's
        # own fixture — the only honest runtime proof that the DEFAULT page
        # is bounded at 100)
        for i in range(101):
            cmd("create_note", "--content", f"census {i}", key=f"cn-{i:03d}",
                owner="C")
        r_full = query("list-notes", "--owner", "C", "--limit", "1000")
        full = list_ids(r_full)
        r_def = query("list-notes", "--owner", "C")
        d_ids, d_more = list_ids(r_def), list_more(r_def)
        r_tail = query("list-notes", "--owner", "C", "--after", d_ids[-1] if d_ids else "")
        t_ids, t_more = list_ids(r_tail), list_more(r_tail)
        r_p1 = query("list-notes", "--owner", "C", "--limit", "50")
        p1, p1m = list_ids(r_p1), list_more(r_p1)
        r_p2 = query("list-notes", "--owner", "C", "--limit", "50", "--after", p1[-1] if p1 else "")
        p2, p2m = list_ids(r_p2), list_more(r_p2)
        r_p3 = query("list-notes", "--owner", "C", "--limit", "50", "--after", p2[-1] if p2 else "")
        p3, p3m = list_ids(r_p3), list_more(r_p3)
        r_s3 = query("list-notes", "--owner", "C", "--limit", "3")
        s3, s3m = list_ids(r_s3), list_more(r_s3)
        r_empty = query("list-notes", "--owner", "B")
        e_lines = [ln for ln in r_empty.stdout.splitlines() if ln.strip()]
        # the other two arms: the same contract shape (owner A's own fixture)
        r_lcap = query("list-captures", "--owner", "A", "--limit", "5")
        r_lbm = query("list-bookmarks", "--owner", "A")
        ok5 = (r_full.returncode == 0 and len(full) == 101
               and full == sorted(full) and len(set(full)) == 101
               and list_more(r_full) == "false"
               # the default page: bounded at exactly 100 + the truth marker
               and r_def.returncode == 0 and d_ids == full[:100] and d_more == "true"
               and r_def.stdout.splitlines()[0] == "# api_version=1"
               # the tail page: the keyset completes the walk
               and r_tail.returncode == 0 and t_ids == full[100:] and t_more == "false"
               # the paged walk: monotone keyset, union == full, no dups
               and p1 == full[:50] and p1m == "true"
               and p2 == full[50:100] and p2m == "true"
               and p3 == full[100:] and p3m == "false"
               and sorted(set(p1) | set(p2) | set(p3)) == full
               and not (set(p1) & set(p2)) and not (set(p2) & set(p3))
               # the small page shape
               and s3 == full[:3] and s3m == "true"
               # the empty owner: header + more=false ALONE (never silence)
               and r_empty.returncode == 0
               and e_lines == ["# api_version=1", "# more=false"]
               # the sibling arms carry the same contract shape
               and r_lcap.returncode == 0
               and r_lcap.stdout.splitlines()[0] == "# api_version=1"
               and hl1 in list_ids(r_lcap) and hl2 not in list_ids(r_lcap)
               and len(list_ids(r_lcap)) <= 5
               and r_lbm.returncode == 0
               and r_lbm.stdout.splitlines()[0] == "# api_version=1"
               and list_ids(r_lbm) == [bm1] and list_more(r_lbm) == "false")
        check("BND-05", ok5,
              "the list arms bounded + paginated: --limit (default 100, bounds 1..1000) + --after "
              "(the keyset cursor); the default page over 101 fixtures returns EXACTLY 100 + "
              "more=true; the tail page completes; the 50-page walk's union == the full walk "
              "(monotone, no dups, no skips); every response opens '# api_version=1' and closes "
              "'# more=true|false'; the empty owner answers header + more=false alone; the "
              "sibling arms (list-captures/list-bookmarks) carry the same shape (and the "
              "tombstoned highlight stays hidden)",
              "query.py's list arms: the bounded default, the keyset cursor, the truth marker, the "
              "ARV-QRY-004 bounds refusal (BND-04) — the contract's one home")

        # ---- BND-06 — the version field on every read surface
        r_cap = query("get-capture", "--owner", "A", "--id", hl1)
        r_src = query("get-source", "--owner", "A", "--id", sid)
        r_nt = query("get-note", "--owner", "A", "--id", n1)
        r_bm = query("get-bookmark", "--owner", "A", "--id", bm1)
        r_search = query("search", "--owner", "A", "frozen")
        hist_hl = query("get-history", "--owner", "A", "--id", hl1)
        hist_nt = query("get-note-history", "--owner", "A", "--id", n1)
        hist_bm = query("get-bookmark-history", "--owner", "A", "--id", bm1)

        def body(r):
            try:
                return json.loads(next(ln for ln in r.stdout.splitlines() if ln.strip()))
            except Exception:
                return {}

        def rows(r):
            return [json.loads(ln) for ln in r.stdout.splitlines()
                    if ln.strip() and not ln.startswith("#")]
        cap_b, src_b, nt_b, bm_b = body(r_cap), body(r_src), body(r_nt), body(r_bm)
        anchor_id = cap_b.get("anchor_id", "")
        r_res = query("resolve-anchor", "--owner", "A", "--id", anchor_id) if anchor_id else None
        res_b = body(r_res) if r_res is not None else {}
        hist_hl_rows, hist_nt_rows, hist_bm_rows = rows(hist_hl), rows(hist_nt), rows(hist_bm)
        search_first = next((ln for ln in r_search.stdout.splitlines() if ln.strip()), "")
        ok6 = (r_cap.returncode == 0 and cap_b.get("api_version") == 1
               and cap_b.get("selected_text") == TEXT[:30]
               and r_src.returncode == 0 and src_b.get("api_version") == 1
               and src_b.get("import_state") == "complete"
               and r_nt.returncode == 0 and nt_b.get("api_version") == 1
               and nt_b.get("content") == "the frozen contract note, revised"
               and r_bm.returncode == 0 and bm_b.get("api_version") == 1
               and bm_b.get("bookmark_id") == bm1
               and r_res is not None and r_res.returncode == 0
               and res_b.get("api_version") == 1 and res_b.get("state") == "resolved"
               and r_search.returncode == 0
               and search_first.startswith("#") and "api_version=1" in search_first
               and "kind" in search_first and "entity_id" in search_first
               and hist_hl.returncode == 0 and len(hist_hl_rows) >= 1
               and all(row.get("api_version") == 1 for row in hist_hl_rows)
               and hist_nt.returncode == 0 and len(hist_nt_rows) >= 2
               and all(row.get("api_version") == 1 for row in hist_nt_rows)
               and hist_bm.returncode == 0 and len(hist_bm_rows) >= 1
               and all(row.get("api_version") == 1 for row in hist_bm_rows))
        check("BND-06", ok6,
              "the version field on every read surface: the JSON bodies (get-capture with its "
              "selected_text + anchor_id, get-source complete, get-note with the revised content, "
              "get-bookmark, resolve-anchor resolved) each carry \"api_version\": 1; every history "
              "row (highlight/note/bookmark) carries it; the search header carries api_version=1 "
              "with the column labels",
              "query.py's read arms: the version key at every print boundary (the _versioned "
              "injection — ONE home, the SQL untouched)")

        if FAILS:
            print(f"\nBOUNDARY SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the frozen client contract is broken or unimplemented)")
            return 1
        print("\nBOUNDARY SUITE GREEN — BND-01..06 (the client contract frozen: the DTO "
              "vocabulary + the version field + the typed-error surface + the bounded lists; "
              "the Phase 3 exit gate's uncoached acceptance path made mechanical)")
        return 0
    finally:
        pg.drop_scratch_db(SRC)


if __name__ == "__main__":
    sys.exit(main())
