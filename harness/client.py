#!/usr/bin/env python3
"""harness/client.py — P4-B slice one (CLAIM-069; record 61 §2): the CLEAN
EXTERNAL CLIENT DRIVER — P4-F's named proof vehicle ("backend contracts are
proven through a clean external client, never fabricated").

A thin scripted client over the REAL CLIs (commands.py / extract.py /
query.py) — the same surface the separate reader-client repo (P4-B's own
repo) will call. THE NO-PRIVILEGED-PATH LAW (CAC-09's pin, mechanically
enforced by the suite's source scan): no direct database tooling, no role
names, no SQL, no
table access of any kind — every observation comes from a subprocess invocation of the
public boundary, exactly as a client would see it.

Two surfaces:
  walk(env, text)             the full user walk (import -> extract -> the
                              first open's truthful no_position_saved ->
                              save position -> highlight -> bookmark -> note
                              -> the reopen round-trip), returning the
                              structured observations + the ids
  condition_<name>(env, ...) P4-B's adversarial + P4-F's recovery
                              conditions (each pinned in its owning suite),
                              returning typed refusals / answers as
                              structured observations

Exit contract: the driver never crashes on a refusal — a typed refusal is
DATA (the code + the line), exactly what a client consumes; the suite judges.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import uuid as _uuid

REPO = pathlib.Path(__file__).resolve().parents[1]


def _cmd(env, op, *args, owner="A", key=None, crash_at=None):
    """A write through commands.py (or crash.py for the crash arms)."""
    if crash_at is not None:
        a = [sys.executable, str(REPO / "harness" / "crash.py"), "--command", op,
             "--point", crash_at, "--owner", owner, "--actor", "owner",
             "--client-id", "cli-1", "--idem-key", key]
        return subprocess.run(a + list(args), capture_output=True, text=True,
                              timeout=300, env=env)
    a = [sys.executable, str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return subprocess.run(a + list(args), capture_output=True, text=True,
                          timeout=300, env=env)


def _query(env, *args):
    return subprocess.run([sys.executable, str(REPO / "harness" / "query.py"), *args],
                          capture_output=True, text=True, timeout=300, env=env)


def _extract(env, key, source_id, owner="A"):
    return subprocess.run([sys.executable, str(REPO / "harness" / "extract.py"),
                           "--owner", owner, "--actor", "owner", "--client-id", "cli-1",
                           "--idem-key", key, "--source-id", source_id],
                          capture_output=True, text=True, timeout=300, env=env)


def _ref(r):
    for ln in r.stdout.splitlines():
        if ln.startswith("ACK") and "result_ref=" in ln:
            return ln.split("result_ref=")[1].split()[0]
    return ""


def _frozen(r):
    """The frozen ack grammar (the P4-00b contract) on a committed ack."""
    return (r.returncode == 0 and "status=committed" in r.stdout
            and "durability_rung=local_durable" in r.stdout
            and "api_version=1" in r.stdout)


def _jline(r):
    try:
        return json.loads(next(ln for ln in r.stdout.splitlines() if ln.strip()))
    except Exception:
        return {}


def _fail_line(r):
    """The FIRST FAIL line (the typed refusal a client consumes), ids normalized."""
    for ln in r.stdout.splitlines():
        if ln.startswith("FAIL "):
            return ln.strip()
    return ""


def _norm(line, *ids):
    """Normalize the ids out of a refusal line (the byte-equality compare)."""
    out = line
    for i in ids:
        if i:
            out = out.replace(i, "<id>")
    return out


# ---- the full user walk ----

def walk(env, text):
    """The full user walk at the real boundary. Returns the observations +
    the ids (the conditions consume them)."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-client-"))
    f = tmp / "corpus.txt"
    f.write_text(text, encoding="utf-8")
    out = {}
    r = _cmd(env, "import_source", "--title", "The Client Walk Corpus",
             "--file", str(f), key="cw-imp-1")
    out["import"] = {"exit": r.returncode, "frozen": _frozen(r)}
    sid = _ref(r)
    out["sid"] = sid
    r = _extract(env, "cw-ext-1", sid)
    out["extract"] = {"exit": r.returncode, "frozen": _frozen(r)}
    r = _query(env, "get-position", "--owner", "A", "--source", sid)
    out["first_open"] = _jline(r)
    start, end = len(text) // 3, len(text) // 2
    r = _cmd(env, "save_position", "--source-id", sid, "--start", str(start),
             "--end", str(end), key="cw-pos-1")
    out["save_position"] = {"exit": r.returncode, "frozen": _frozen(r)}
    out["pos_ref"] = _ref(r)
    out["pos_start"], out["pos_end"] = start, end
    m = text.index("meridian")
    r = _cmd(env, "create_highlight", "--source-id", sid, "--start", str(m),
             "--end", str(m + len("meridian")), key="cw-hl-1")
    out["highlight"] = {"exit": r.returncode, "frozen": _frozen(r)}
    hid = _ref(r)
    out["hid"] = hid
    r = _cmd(env, "create_bookmark", "--source-id", sid, "--start", str(m),
             "--end", str(m + len("meridian")), key="cw-bm-1")
    out["bookmark"] = {"exit": r.returncode, "frozen": _frozen(r)}
    out["bid"] = _ref(r)
    r = _cmd(env, "create_note", "--content",
             "A client-walk note about the meridian token.", key="cw-n1")
    out["note"] = {"exit": r.returncode, "frozen": _frozen(r)}
    nid = _ref(r)
    out["nid"] = nid
    r = _query(env, "get-position", "--owner", "A", "--source", sid)
    out["reopen_position"] = _jline(r)
    r = _query(env, "get-capture", "--owner", "A", "--id", hid)
    out["reopen_capture"] = {"exit": r.returncode}
    r = _query(env, "get-note", "--owner", "A", "--id", nid)
    out["reopen_note"] = {"body": _jline(r).get("content", "")}
    return out


# ---- P4-B's named adversarial conditions ----

def condition_forbidden_source(env, w):
    """Auth/owner-scope expiration + forbidden source: the no-oracle on BOTH
    paths (byte-equal absent-vs-foreign), never a leak."""
    absent = str(_uuid.uuid4())
    r_ra = _query(env, "get-position", "--owner", "A", "--source", absent)
    r_rf = _query(env, "get-position", "--owner", "B", "--source", w["sid"])
    r_wa = _cmd(env, "save_position", "--source-id", absent, "--start", "0",
                "--end", "5", key="cf-abs-1")
    r_wf = _cmd(env, "save_position", "--source-id", w["sid"], "--start", "0",
                "--end", "5", key="cf-for-1", owner="B")
    r_fe = _extract(env, "cf-ext-1", w["sid"], owner="B")
    return {
        "read_absent": _norm(_fail_line(r_ra), absent),
        "read_foreign": _norm(_fail_line(r_rf), w["sid"]),
        "write_absent": _norm(_fail_line(r_wa), absent),
        "write_foreign": _norm(_fail_line(r_wf), w["sid"]),
        "foreign_extract": _fail_line(r_fe).split(":")[0].replace("FAIL ", ""),
    }


def condition_malformed_dto(env, w):
    """The typed refusals at every command boundary — each zero-effect (the
    CLI-observable counts unchanged: the captures list, the notes list, the
    position's ordinal)."""
    caps_before = _query(env, "list-captures", "--owner", "A").stdout
    notes_before = _query(env, "list-notes", "--owner", "A").stdout
    pos_before = _jline(_query(env, "get-position", "--owner", "A", "--source", w["sid"]))
    r_off = _cmd(env, "create_highlight", "--source-id", w["sid"], "--start", "5",
                 "--end", "5", key="cm-off-1")           # the empty window
    r_cnt = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                            "create_note", "--owner", "A", "--actor", "owner",
                            "--client-id", "cli-1", "--idem-key", "cm-cnt-1"],
                           capture_output=True, text=True, timeout=300, env=env)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-client-"))
    bad = tmp / "bad.bin"
    bad.write_bytes(b"\x00\x01 bad type bytes \xff")
    r_fmt = _cmd(env, "import_source", "--title", "Bad Type", "--file", str(bad),
                 "--media-type", "text/x-fancy", key="cm-fmt-1")
    r_pos = _cmd(env, "save_position", "--source-id", w["sid"], "--start", "10",
                 "--end", "10", key="cm-pos-1")           # the empty window
    caps_after = _query(env, "list-captures", "--owner", "A").stdout
    notes_after = _query(env, "list-notes", "--owner", "A").stdout
    pos_after = _jline(_query(env, "get-position", "--owner", "A", "--source", w["sid"]))
    return {
        "offset_law": _fail_line(r_off).split(":")[0].replace("FAIL ", ""),
        "content_law": _fail_line(r_cnt).split(":")[0].replace("FAIL ", ""),
        "format_law": _fail_line(r_fmt).split(":")[0].replace("FAIL ", ""),
        "position_law": _fail_line(r_pos).split(":")[0].replace("FAIL ", ""),
        "zero_effect": (caps_before == caps_after and notes_before == notes_after
                        and pos_before.get("save_ordinal") == pos_after.get("save_ordinal")),
    }


def condition_uncertain_ack(env, w):
    """Offline transitions + timeout-with-uncertain-ack: the lost-ack arm
    (exit 2, the effect committed) + the retry-after-lost-response
    convergence (the same-key replay)."""
    start, end = 2, 9
    r_cr = _cmd(env, "save_position", "--source-id", w["sid"], "--start", str(start),
                "--end", str(end), key="cu-pos-1", crash_at="post-commit-pre-ack")
    g = _jline(_query(env, "get-position", "--owner", "A", "--source", w["sid"]))
    r_rp = _cmd(env, "save_position", "--source-id", w["sid"], "--start", str(start),
                "--end", str(end), key="cu-pos-1")
    return {
        "crash_exit": r_cr.returncode,
        "effect_committed": (g.get("start_off") == start and g.get("end_off") == end),
        "replay_exit": r_rp.returncode,
        "replay_replayed": "status=replayed" in r_rp.stdout,
        "replay_same_ref": _ref(r_rp) == f"{w['sid']}@{g.get('save_ordinal')}",
    }


def condition_duplicate_click(env, w):
    """Duplicate click: the idempotency (same key + same body -> replayed
    with the same ref; same key + different body -> the typed 409)."""
    r1 = _cmd(env, "create_note", "--content", "The duplicate-click note.",
              key="cd-n1")
    ref1 = _ref(r1)
    r2 = _cmd(env, "create_note", "--content", "The duplicate-click note.",
              key="cd-n1")
    body_before = _jline(_query(env, "get-note", "--owner", "A", "--id", ref1)).get("content", "")
    r3 = _cmd(env, "create_note", "--content", "A DIFFERENT body under the same key.",
              key="cd-n1")
    body_after = _jline(_query(env, "get-note", "--owner", "A", "--id", ref1)).get("content", "")
    return {
        "same_body_exit": r2.returncode,
        "same_body_replayed": "status=replayed" in r2.stdout,
        "same_body_same_ref": _ref(r2) == ref1,
        "diff_body_exit": r3.returncode,
        "diff_body_code": _fail_line(r3).split(":")[0].replace("FAIL ", ""),
        "diff_body_zero_effect": body_before == body_after,
    }


def condition_reload(env, w):
    """Reload/restart: fresh invocations answer the durable state."""
    r_p = _query(env, "get-position", "--owner", "A", "--source", w["sid"])
    r_c = _query(env, "get-capture", "--owner", "A", "--id", w["hid"])
    r_n = _query(env, "get-note", "--owner", "A", "--id", w["nid"])
    return {
        "position_state": _jline(r_p).get("state", ""),
        "capture_exit": r_c.returncode,
        "note_body_matches": "meridian" in _jline(r_n).get("content", ""),
    }


def condition_stale_version(env, w):
    """Stale source version: the generation binding honest across a
    re-extraction (never a silent retarget)."""
    before = _jline(_query(env, "get-position", "--owner", "A", "--source", w["sid"]))
    r_re = _extract(env, "cs-ext-1", w["sid"])
    after = _jline(_query(env, "get-position", "--owner", "A", "--source", w["sid"]))
    return {
        "reextract_exit": r_re.returncode,
        "generation_changed": after.get("current_generation_id") != before.get("current_generation_id"),
        "saved_generation_stable": (after.get("saved_generation_id")
                                    == before.get("saved_generation_id")),
        "generation_matches": after.get("generation_matches"),
        # the offsets compare BEFORE-vs-AFTER the re-extraction (the honest
        # form: the re-extraction changes NOTHING about the saved row — the
        # earlier conditions may have advanced the position, and that advance
        # is the saved row the re-extraction must not touch)
        "offsets_unchanged": (after.get("start_off") == before.get("start_off")
                              and after.get("end_off") == before.get("end_off")),
        "saved_before_matches": before.get("generation_matches") is True,
    }


def condition_deleted_target(env, w):
    """Deleted target: the tombstone refusals (hidden from retrieval, never
    erased; the history retains; the restore returns)."""
    r_t = _cmd(env, "tombstone_highlight", "--id", w["hid"], key="ct-t1")
    r_read = _query(env, "get-capture", "--owner", "A", "--id", w["hid"])
    r_hist = _query(env, "get-history", "--owner", "A", "--id", w["hid"])
    r_restore = _cmd(env, "restore_highlight", "--id", w["hid"], key="ct-r1")
    r_after = _query(env, "get-capture", "--owner", "A", "--id", w["hid"])
    return {
        "tombstone_exit": r_t.returncode,
        "read_refuses": _fail_line(r_read).split(":")[0].replace("FAIL ", ""),
        "history_retains": r_hist.returncode == 0 and "revision" in r_hist.stdout,
        "restore_exit": r_restore.returncode,
        "read_after_restore_exit": r_after.returncode,
    }


# ---- P4-F's recovery/regression conditions (CLAIM-079; record 71 §2). Each
# condition's full contract statement lives at its check() in the RCW suite
# (test_recovery_contract.py) — the one-fact-one-home law.

def _ids_of(r):
    """The list arms' ids (the P4-00b shape: rows between header/marker)."""
    lines = [ln for ln in r.stdout.split("\n") if ln != ""]
    return lines[1:-1] if len(lines) >= 2 else []


def _page_ids(env, arm, owner="A", limit="2"):
    """The full keyset walk over a bounded list arm (every page)."""
    out, after = [], None
    while True:
        a = [sys.executable, str(REPO / "harness" / "query.py"), arm,
             "--owner", owner, "--limit", limit] + (["--after", after] if after else [])
        r = subprocess.run(a, capture_output=True, text=True, timeout=300, env=env)
        if r.returncode != 0:
            return None
        ids = _ids_of(r)
        out.extend(ids)
        if not ids or len(ids) < int(limit):
            return out
        after = ids[-1]


def condition_recovery_walk(env, text):
    """RCW-01's contract: crash mid-sequence -> prefix survives, replay
    converges, post-restart reads truthful (families ride the return)."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-client-"))
    (tmp / "corpus.txt").write_text(text, encoding="utf-8")
    r_imp = _cmd(env, "import_source", "--title", "The Recovery Walk Corpus",
                 "--file", str(tmp / "corpus.txt"), key="rw-imp-1")
    sid = _ref(r_imp)
    _extract(env, "rw-ext-1", sid)
    _cmd(env, "save_position", "--source-id", sid, "--start", "2", "--end", "9",
         key="rw-pos-1")
    r_b1 = _cmd(env, "journal_block", "--kind", "raw", "--content",
                "The durable prefix block, authored before the crash.", key="rw-j1")
    b1 = _ref(r_b1).split("@")[0]  # <id>@<rev> address; the read takes the uuid
    # the crash arm (exit 2) + the same-key replay
    _body = "The block authored across the lost ack."
    r_cr = _cmd(env, "journal_block", "--kind", "creative", "--content",
                _body, key="rw-j2", crash_at="post-commit-pre-ack")
    r_rp = _cmd(env, "journal_block", "--kind", "creative", "--content",
                _body, key="rw-j2")
    # fresh reads over every family
    g_b1 = _query(env, "get-journal", "--owner", "A", "--id", b1)
    g_pos = _query(env, "get-position", "--owner", "A", "--source", sid)
    g_lib = _query(env, "list-library", "--owner", "A")
    g_ses = _query(env, "list-session-events", "--owner", "A")
    g_bms = _query(env, "list-bookmarks", "--owner", "A")
    jl = _page_ids(env, "list-journal")
    j2 = (_ref(r_rp) or "").rsplit("@", 1)[0]
    g_b2 = _query(env, "get-journal", "--owner", "A", "--id", j2) if j2 else None
    r_hl = _cmd(env, "create_highlight", "--source-id", sid, "--start", "5",
                "--end", "13", key="rw-hl-1")
    hid = _ref(r_hl)
    g_hl = _query(env, "get-capture", "--owner", "A", "--id", hid)
    r_nt = _cmd(env, "create_note", "--content",
                "The recovery-walk note about the meridian.",
                "--ref", f"highlight:{hid}@1", key="rw-n1")
    nid = _ref(r_nt)
    g_nt = _query(env, "get-note", "--owner", "A", "--id", nid)
    r_rl = _cmd(env, "create_reading_list", "--name", "The recovery shelf", key="rw-l1")
    lid = _ref(r_rl)
    _cmd(env, "add_to_list", "--list", lid, "--source", sid, key="rw-a1")
    g_rl = _query(env, "get-list", "--owner", "A", "--id", lid)
    _cmd(env, "record_session", "--source-id", sid, "--event", "session_start",
         "--start", "0", "--end", "10", key="rw-s1")
    families = {
        "library": g_lib.returncode == 0 and sid in _ids_of(g_lib),
        "position": g_pos.returncode == 0 and _jline(g_pos).get("state") == "saved",
        "highlight": g_hl.returncode == 0, "bookmark": g_bms.returncode == 0,
        "note": g_nt.returncode == 0, "note_reference": "refs" in _jline(g_nt),
        "journal_block": (g_b1.returncode == 0 and jl is not None and b1 in jl
                          and (g_b2 is None or g_b2.returncode == 0)),
        "reading_list": g_rl.returncode == 0, "reading_session": g_ses.returncode == 0,
    }
    return {
        "prefix_survives": (r_b1.returncode == 0 and g_b1.returncode == 0
                            and "durable prefix" in _jline(g_b1).get("content", "")),
        "crash_exit": r_cr.returncode,
        "replay_exit": r_rp.returncode,
        "replay_replayed": "status=replayed" in r_rp.stdout,
        "post_restart_reads": all(families.values()),
        "families": sorted(k for k, v in families.items() if v),
    }


def condition_export_restore(env, text):
    """RCW-02's contract: every family written, exported, restored
    clean; post-restore reads byte-equal; no credentials in the archive."""
    from harness.adapters import pg as _pg
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-client-"))
    f = tmp / "corpus.txt"
    f.write_text(text, encoding="utf-8")
    r_imp = _cmd(env, "import_source", "--title", "The Lifecycle Corpus",
                 "--file", str(f), key="er-imp-1")
    sid = _ref(r_imp)
    _extract(env, "er-ext-1", sid)
    _cmd(env, "save_position", "--source-id", sid, "--start", "2", "--end", "9",
         key="er-pos-1")
    m = text.index("meridian")
    r_hl = _cmd(env, "create_highlight", "--source-id", sid, "--start", str(m),
                "--end", str(m + len("meridian")), key="er-hl-1")
    hid = _ref(r_hl)
    r_bm = _cmd(env, "create_bookmark", "--source-id", sid, "--start", str(m),
                "--end", str(m + len("meridian")), key="er-bm-1")
    r_n1 = _cmd(env, "create_note", "--content",
                "The lifecycle note: the welkin token.",
                "--ref", f"highlight:{hid}@1", "--ref", f"source:{sid}", key="er-n1")
    nid = _ref(r_n1)
    _cmd(env, "revise_note", "--id", nid, "--content",
         "The lifecycle note revised: the welkin stays.", key="er-n1r")
    r_j1 = _cmd(env, "journal_block", "--kind", "raw", "--content",
                "The first journal revision of the lifecycle.", key="er-j1")
    j1 = _ref(r_j1).split("@")[0]  # <id>@<rev>; the read takes the uuid
    _cmd(env, "revise_journal_block", "--id", j1, "--content",
         "The second journal revision (the lossless law's proof).", key="er-j2")
    _cmd(env, "journal_block", "--kind", "creative", "--source-id", sid,
         "--content", "A bound creative block.", key="er-j3")
    # F-079-1's pinned shape: the journal-block @-reference rides the walk
    r_n2 = _cmd(env, "create_note", "--content", "The journal-ref note.",
                "--ref", f"journal_block:{j1}@1", key="er-n2")
    r_l1 = _cmd(env, "create_reading_list", "--name", "The lifecycle shelf", key="er-l1")
    lid = _ref(r_l1)
    _cmd(env, "add_to_list", "--list", lid, "--source", sid, key="er-a1")
    _cmd(env, "record_session", "--source-id", sid, "--event", "session_start",
         "--start", "0", "--end", "10", key="er-s1")
    _cmd(env, "record_session", "--source-id", sid, "--event", "dwell",
         "--start", "4", "--end", "6", "--dwell-ms", "1500", key="er-s2")
    # a credential minted BEFORE the export (the never-ride law's probe)
    r_mint = _cmd(env, "mint_agent_credential", "--label",
                  "the lifecycle probe", key="er-ag1")
    walk_complete = all(r.returncode == 0 for r in
                        (r_imp, r_hl, r_bm, r_n1, r_n2, r_j1, r_l1, r_mint))
    # the pre/post read set (the byte-equality compare's both sides)
    _ARMS = (("note", "get-note", lambda: nid),
             ("journal", "get-journal-history", lambda: j1),
             ("journals", "list-journal", None), ("lists", "list-lists", None),
             ("members", "get-list", lambda: lid),
             ("sessions", "list-session-events", None),
             ("notes_list", "list-notes", None), ("captures", "list-captures", None),
             ("bookmarks", "list-bookmarks", None), ("position", "get-position", "sid"),
             ("search", "search", ("--owner", "A", "meridian")))

    def _reads(e):
        out = {}
        for k, arm, tgt in _ARMS:
            if arm == "list-journal":
                out[k] = _page_ids(e, arm) or []
            elif arm == "get-position":
                # pins the AUTHORED row (ordinal + window + the saved
                # generation binding); the LIVE serving-generation fields
                # ride NORMALIZED OUT (the search arm's runtime class)
                j = _jline(_query(e, arm, "--owner", "A", "--source", sid))
                out[k] = json.dumps({
                    "state": j.get("state"), "save_ordinal": j.get("save_ordinal"),
                    "start_off": j.get("start_off"), "end_off": j.get("end_off"),
                    "saved_generation_id": j.get("saved_generation_id"),
                }, sort_keys=True) + "\n"
            elif callable(tgt):
                out[k] = _query(e, arm, "--owner", "A", "--id", tgt()).stdout
            else:
                out[k] = _query(e, arm, *(tgt or ("--owner", "A"))).stdout
        return out

    pre = _reads(env)
    # the export; the never-ride law: no credential TABLES, no token VALUE
    arch = tmp / "archive"
    r_ex = subprocess.run([sys.executable, str(REPO / "harness" / "export.py"),
                           "export", "--owner", "A", "--out", str(arch)],
                          capture_output=True, text=True, timeout=600, env=env)
    man_text = (arch / "manifest.json").read_text(encoding="utf-8") \
        if (arch / "manifest.json").is_file() else ""
    tok_val = next((ln.split("token=")[1].split()[0] for ln in
                    r_mint.stdout.splitlines() if "token=" in ln), "")
    try:
        m_tables = set(json.loads(man_text).get("tables", {}))
    except Exception:
        m_tables = set()
    creds_absent = ("agent_credential" not in m_tables
                    and "agent_read_log" not in m_tables
                    and (not tok_val or tok_val not in man_text))
    # the clean migrated destination (the derived rebuild BEFORE the reads)
    dst = _pg.create_scratch_db("p4fdst")
    try:
        denv = dict(env, PGDATABASE=dst)
        r_mig = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                               capture_output=True, text=True, timeout=180,
                               env=denv, check=True)
        r_rs = subprocess.run([sys.executable, str(REPO / "harness" / "export.py"),
                               "restore", "--archive", str(arch)],
                              capture_output=True, text=True, timeout=600, env=denv)
        subprocess.run([sys.executable, str(REPO / "harness" / "extract.py"),
                       "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                       "--idem-key", "er-rex-1", "--source-id", sid],
                      capture_output=True, text=True, timeout=300, env=denv)
        _cmd(denv, "rebuild_keyword_index", key="er-rb-1")
        post = _reads(denv)
        # the lossless law: EVERY journal revision round-trips
        jhist = [json.loads(ln) for ln in pre["journal"].splitlines()
                 if ln.startswith("{")]
        revisions = sorted(r["revision"] for r in jhist)
        return {
            "walk_complete": walk_complete,
            "export_exit": r_ex.returncode,
            "restore_exit": r_rs.returncode,
            "journal_revisions": (r_mig.returncode == 0 and revisions == [1, 2]
                                  and post["journal"] == pre["journal"]),
            "post_restore_byte_equal": all(post[k] == pre[k] for k in pre),
            "credentials_absent": creds_absent,
        }
    finally:
        _pg.drop_scratch_db(dst)


def condition_rebuild_parity(env):
    """RCW-03's contract: search answers unchanged across the rebuild
    (the index derived, never governing)."""
    _rows = lambda r: [ln for ln in r.stdout.split("\n")
                       if ln.strip() and not ln.lstrip().startswith("#")]
    before = _query(env, "search", "--owner", "A", "meridian")
    r_rb = _cmd(env, "rebuild_keyword_index", key="rb-1")
    after = _query(env, "search", "--owner", "A", "meridian")
    return {
        "before_exit": before.returncode,
        "rebuild_exit": r_rb.returncode,
        "after_exit": after.returncode,
        "parity": (_rows(after) == _rows(before) and r_rb.returncode == 0
                   and "status=committed" in r_rb.stdout),
    }


def condition_phase_isolation(env, text):
    """RCW-04's contract: every family invisible to the other owner;
    the no-oracle byte-equal."""
    w = condition_recovery_walk(env, text)
    absent = str(_uuid.uuid4())
    # B's view of A's families: the cross-family invisibility (the plain
    # list arms answer ids; the session rows are JSON between the markers)
    a_ids = [_ids_of(_query(env, a, "--owner", "B")) for a in
             ("list-library", "list-journal", "list-lists", "list-notes",
              "list-captures", "list-bookmarks")]
    ses_b = _query(env, "list-session-events", "--owner", "B")
    a_empty = (not any(a_ids)
               and not [ln for ln in ses_b.stdout.splitlines()
                        if ln.strip() and not ln.startswith("#")])
    # the no-oracle at the phase level: A's id vs an absent id at B
    a_jl = _ids_of(_query(env, "list-journal", "--owner", "A"))
    q = lambda i: _query(env, "get-journal", "--owner", "B", "--id", i)
    r_abs, r_for = q(absent), q(a_jl[0] if a_jl else absent)
    ra = _norm(_fail_line(r_abs), absent)
    rf = _norm(_fail_line(r_for), absent)
    return {
        "walk_complete": w["post_restart_reads"] is True,
        "cross_family_invisible": a_empty,
        "no_oracle": (ra == rf and ra != "" and ra.split(":")[0] == "FAIL ARV-QRY-001"),
    }


def condition_prior_state_migration(env):
    """RCW-05's contract: 0001..0014 prior content migrates forward,
    survives, the guards live at the CLI."""
    from harness.adapters import pg as _pg
    from shutil import copy as _copy
    db = _pg.create_scratch_db("p4fprior")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-prior-"))
    mdir = tmp / "migrations"
    mdir.mkdir()
    for p in sorted((REPO / "harness" / "migrations").glob("*.sql")):
        if int(p.name[:4]) <= 14:
            _copy(p, mdir / p.name)
    try:
        menv = dict(env, PGDATABASE=db, ARV_MIGRATIONS_DIR=str(mdir))
        wenv = dict(env, PGDATABASE=db)
        # the prior baseline applies; real P3-era content lands on it; the
        # forward chain runs to the current head
        r_m1 = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                               capture_output=True, text=True, timeout=180, env=menv)
        (tmp / "prior.txt").write_text(
            "The prior-state corpus: the enduring token rides.\n"
            "A second line for the capture window.\n", encoding="utf-8")
        r_imp = _cmd(wenv, "import_source", "--title", "The Prior-State Corpus",
                     "--file", str(tmp / "prior.txt"), key="pm-imp-1")
        sid = _ref(r_imp)
        r_hl = _cmd(wenv, "create_highlight", "--source-id", sid, "--start", "5",
                    "--end", "12", key="pm-hl-1")
        r_nt = _cmd(wenv, "create_note", "--content",
                     "The prior-state note: the welkin rides.", key="pm-n1")
        nid = _ref(r_nt)
        r_m2 = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                              capture_output=True, text=True, timeout=180, env=wenv)
        # the post-migration reads answer the prior content; the invariant
        # probe: a hostile journal revise answers the typed no-oracle refusal
        g_s = _query(wenv, "get-source", "--owner", "A", "--id", sid)
        g_n = _query(wenv, "get-note", "--owner", "A", "--id", nid)
        r_inv = _cmd(wenv, "revise_journal_block", "--id",
                    "00000000-0000-0000-0000-0000000000ff", "--content",
                    "tampered", key="pm-inv1")
        return {
            "prior_written": all(r.returncode == 0 for r in (r_imp, r_hl, r_nt)),
            "migrate_exit": all(r.returncode == 0 for r in (r_m1, r_m2)),
            "content_survives": (g_s.returncode == 0 and g_n.returncode == 0
                                 and "welkin" in _jline(g_n).get("content", "")),
            "invariants_hold": (r_inv.returncode == 1
                                and "ARV-JNL-001" in _fail_line(r_inv)),
        }
    finally:
        _pg.drop_scratch_db(db)


def condition_sync_conflict(env):
    """RCW-06's contract: the typed ARV-CMD-409 failed row, BOTH bodies
    preserved — never a silent LWW."""
    from harness.adapters import pg as _pg
    loc, srv = _pg.create_scratch_db("p4floc"), _pg.create_scratch_db("p4fsrv")
    try:
        lenv = dict(env, PGDATABASE=loc)
        senv = dict(env, PGDATABASE=srv, ARV_SITE="server")
        for e in (lenv, senv):
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=180,
                           env=e, check=True)
        # the local write + the server's COMPETING write under the same key;
        # the delivery pass surfaces the typed conflict (the SYNC line)
        r_loc = _cmd(lenv, "create_note", "--content",
                     "The local body for the same key.", key="cf-n1")
        r_srv = _cmd(senv, "create_note", "--content",
                     "The server's competing body for the key.", key="cf-n1")
        r_sync = subprocess.run(
            [sys.executable, str(REPO / "harness" / "sync.py"), "sync",
             "--owner", "A", "--server-db", srv],
            capture_output=True, text=True, timeout=300, env=lenv)
        line = next((ln for ln in r_sync.stdout.splitlines()
                     if "cf-n1" in ln), "")
        # BOTH bodies preserved (each site's own read)
        g_loc = _query(lenv, "get-note", "--owner", "A", "--id", _ref(r_loc))
        g_srv = _query(senv, "get-note", "--owner", "A", "--id", _ref(r_srv))
        return {
            "local_exit": r_loc.returncode,
            "server_exit": r_srv.returncode,
            "sync_exit": r_sync.returncode,
            "conflict_failed": "state=failed" in line,
            "typed_409": "ARV-CMD-409" in line,
            "both_bodies_preserved": ("local body" in _jline(g_loc).get("content", "")
                                      and "competing body" in _jline(g_srv).get("content", "")),
        }
    finally:
        _pg.drop_scratch_db(loc)
        _pg.drop_scratch_db(srv)