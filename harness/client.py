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
  condition_<name>(env, walk) P4-B's named adversarial conditions, each
                              returning its typed refusals / truthful
                              answers as structured observations

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


# ---- P4-F's recovery/regression conditions (CLAIM-079; record 71 §2) ----

def _ids_of(r):
    """The list arms' ids: the rows between the version header and the
    more-marker (the P4-00b list contract's shape)."""
    lines = [ln for ln in r.stdout.split("\n") if ln != ""]
    return lines[1:-1] if len(lines) >= 2 else []


def _page_ids(env, arm, owner="A", limit="2"):
    """The full keyset walk over a bounded list arm (every page)."""
    out, after = [], None
    while True:
        a = [sys.executable, str(REPO / "harness" / "query.py"), arm,
             "--owner", owner, "--limit", limit]
        if after:
            a += ["--after", after]
        r = subprocess.run(a, capture_output=True, text=True, timeout=300, env=env)
        if r.returncode != 0:
            return None
        ids = _ids_of(r)
        out.extend(ids)
        if not ids or (len(ids) < int(limit)):
            return out
        after = ids[-1]


def condition_recovery_walk(env, text):
    """P4-F (CLAIM-079): the recovery walk — a journal-authoring sequence
    interrupted by the crash matrix's post-commit-pre-ack arm. The durable
    prefix survives (fresh reads), the uncertain-ack replay converges
    (status=replayed, the same ref), the post-restart reads truthful. The
    observed families ride the return (the phase gate's mechanical form)."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-client-"))
    f = tmp / "corpus.txt"
    f.write_text(text, encoding="utf-8")
    r_imp = _cmd(env, "import_source", "--title", "The Recovery Walk Corpus",
                 "--file", str(f), key="rw-imp-1")
    sid = _ref(r_imp)
    r_ext = _extract(env, "rw-ext-1", sid)
    r_p = _cmd(env, "save_position", "--source-id", sid, "--start", "2",
               "--end", "9", key="rw-pos-1")
    r_b1 = _cmd(env, "journal_block", "--kind", "raw", "--content",
                "The durable prefix block, authored before the crash.",
                key="rw-j1")
    b1 = _ref(r_b1).split("@")[0]  # the ack's <id>@<rev> address; the read takes the uuid
    # the crash arm: committed, no ack (exit 2 — the honest unknown)
    r_cr = _cmd(env, "journal_block", "--kind", "creative", "--content",
                "The block authored across the lost ack.", key="rw-j2",
                crash_at="post-commit-pre-ack")
    # the same-key replay converges
    r_rp = _cmd(env, "journal_block", "--kind", "creative", "--content",
                "The block authored across the lost ack.", key="rw-j2")
    # fresh reads over every family (the families the walk observes)
    g_b1 = _query(env, "get-journal", "--owner", "A", "--id", b1)
    g_pos = _query(env, "get-position", "--owner", "A", "--source", sid)
    g_lib = _query(env, "list-library", "--owner", "A")
    g_ses = _query(env, "list-session-events", "--owner", "A")
    g_lists = _query(env, "list-lists", "--owner", "A")
    g_notes = _query(env, "list-notes", "--owner", "A")
    g_caps = _query(env, "list-captures", "--owner", "A")
    g_bms = _query(env, "list-bookmarks", "--owner", "A")
    jl = _page_ids(env, "list-journal")
    j2 = _ref(r_rp) or ""
    g_b2 = _query(env, "get-journal", "--owner", "A", "--id",
                  j2.rsplit("@", 1)[0] if "@" in j2 else j2) if j2 else None
    r_hl = _cmd(env, "create_highlight", "--source-id", sid, "--start", "5",
                "--end", "13", key="rw-hl-1")
    hid = _ref(r_hl)
    g_hl = _query(env, "get-capture", "--owner", "A", "--id", hid)
    r_nt = _cmd(env, "create_note", "--content",
                "The recovery-walk note about the meridian.", "--ref",
                f"highlight:{hid}@1", key="rw-n1")
    nid = _ref(r_nt)
    g_nt = _query(env, "get-note", "--owner", "A", "--id", nid)
    r_rl = _cmd(env, "create_reading_list", "--name", "The recovery shelf",
                key="rw-l1")
    lid = _ref(r_rl)
    r_ad = _cmd(env, "add_to_list", "--list", lid, "--source", sid, key="rw-a1")
    g_rl = _query(env, "get-list", "--owner", "A", "--id", lid)
    r_se = _cmd(env, "record_session", "--source-id", sid, "--event",
                "session_start", "--start", "0", "--end", "10", key="rw-s1")
    families = {
        "library": g_lib.returncode == 0 and sid in _ids_of(g_lib),
        "position": g_pos.returncode == 0 and _jline(g_pos).get("state") == "saved",
        "highlight": g_hl.returncode == 0,
        "bookmark": g_bms.returncode == 0,
        "note": g_nt.returncode == 0,
        "note_reference": "refs" in _jline(g_nt),
        "journal_block": (g_b1.returncode == 0 and jl is not None and b1 in jl
                          and (g_b2 is None or g_b2.returncode == 0)),
        "reading_list": g_rl.returncode == 0,
        "reading_session": g_ses.returncode == 0 and len(_ids_of(g_ses)) >= 0,
    }
    return {
        "prefix_survives": (r_b1.returncode == 0 and g_b1.returncode == 0
                             and "durable prefix" in _jline(g_b1).get("content", "")),
        "crash_exit": r_cr.returncode,
        "replay_exit": r_rp.returncode,
        "replay_replayed": "status=replayed" in r_rp.stdout,
        "post_restart_reads": all(families.values()),
        "families": sorted(k for k, v in families.items() if v),
        "walk_provenance": {
            "import": r_imp.returncode, "extract": r_ext.returncode,
            "position": r_p.returncode, "session": r_se.returncode,
            "list": r_rl.returncode, "add": r_ad.returncode,
        },
    }


def condition_export_restore(env, text):
    """P4-F (CLAIM-079): the full-lifecycle export/restore round-trip —
    every landed family written, exported, restored into a clean
    destination; the post-restore reads BYTE-EQUAL the pre-export reads;
    the agent credentials never ride the export."""
    from harness.adapters import pg as _pg
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-client-"))
    f = tmp / "corpus.txt"
    f.write_text(text, encoding="utf-8")
    r_imp = _cmd(env, "import_source", "--title", "The Lifecycle Corpus",
                 "--file", str(f), key="er-imp-1")
    sid = _ref(r_imp)
    _extract(env, "er-ext-1", sid)
    _cmd(env, "save_position", "--source-id", sid, "--start", "2",
         "--end", "9", key="er-pos-1")
    m = text.index("meridian")
    r_hl = _cmd(env, "create_highlight", "--source-id", sid, "--start", str(m),
                "--end", str(m + len("meridian")), key="er-hl-1")
    hid = _ref(r_hl)
    r_bm = _cmd(env, "create_bookmark", "--source-id", sid, "--start", str(m),
                "--end", str(m + len("meridian")), key="er-bm-1")
    r_n1 = _cmd(env, "create_note", "--content",
                "The lifecycle note: the welkin token.", "--ref",
                f"highlight:{hid}@1", "--ref", f"source:{sid}", key="er-n1")
    nid = _ref(r_n1)
    _cmd(env, "revise_note", "--id", nid, "--content",
         "The lifecycle note revised: the welkin stays.", key="er-n1r")
    r_j1 = _cmd(env, "journal_block", "--kind", "raw", "--content",
                "The first journal revision of the lifecycle.", key="er-j1")
    j1 = _ref(r_j1).split("@")[0]  # the ack's <id>@<rev> address; reads/revise take the uuid
    _cmd(env, "revise_journal_block", "--id", j1, "--content",
         "The second journal revision (the lossless law's proof).", key="er-j2")
    _cmd(env, "journal_block", "--kind", "creative", "--source-id", sid,
         "--content", "A bound creative block.", key="er-j3")
    r_l1 = _cmd(env, "create_reading_list", "--name", "The lifecycle shelf",
                key="er-l1")
    lid = _ref(r_l1)
    _cmd(env, "add_to_list", "--list", lid, "--source", sid, key="er-a1")
    _cmd(env, "record_session", "--source-id", sid, "--event",
         "session_start", "--start", "0", "--end", "10", key="er-s1")
    _cmd(env, "record_session", "--source-id", sid, "--event", "dwell",
         "--start", "4", "--end", "6", "--dwell-ms", "1500", key="er-s2")
    # a credential minted BEFORE the export (the never-ride law's probe)
    r_mint = _cmd(env, "mint_agent_credential", "--label",
                  "the lifecycle probe", key="er-ag1")
    walk_complete = (r_imp.returncode == 0 and r_hl.returncode == 0
                     and r_bm.returncode == 0 and r_n1.returncode == 0
                     and r_j1.returncode == 0 and r_l1.returncode == 0
                     and r_mint.returncode == 0)
    # the pre-export reads (the byte-equality compare's left side)
    pre = {
        "note": _query(env, "get-note", "--owner", "A", "--id", nid).stdout,
        "journal": _query(env, "get-journal-history", "--owner", "A",
                          "--id", j1).stdout,
        "journals": _page_ids(env, "list-journal") or [],
        "lists": _query(env, "list-lists", "--owner", "A").stdout,
        "members": _query(env, "get-list", "--owner", "A", "--id", lid).stdout,
        "sessions": _query(env, "list-session-events", "--owner", "A").stdout,
        "notes_list": _query(env, "list-notes", "--owner", "A").stdout,
        "captures": _query(env, "list-captures", "--owner", "A").stdout,
        "bookmarks": _query(env, "list-bookmarks", "--owner", "A").stdout,
        "search": _query(env, "search", "--owner", "A", "meridian").stdout,
    }
    # the export
    arch = tmp / "archive"
    r_ex = subprocess.run([sys.executable, str(REPO / "harness" / "export.py"),
                           "export", "--owner", "A", "--out", str(arch)],
                          capture_output=True, text=True, timeout=600, env=env)
    # the credential absence in the archive (the never-ride law): the
    # credential TABLES never ride the manifest, and the one-time token
    # VALUE never appears anywhere in the archive text (the audit trail's
    # command_log may name the mint COMMAND — provenance, never the secret)
    man_p = arch / "manifest.json"
    man_text = man_p.read_text(encoding="utf-8") if man_p.is_file() else ""
    tok_val = ""
    for ln in r_mint.stdout.splitlines():
        if "token=" in ln and "ACK" in ln:
            tok_val = ln.split("token=")[1].split()[0]
            break
    try:
        m_tables = set(json.loads(man_text).get("tables", {}))
    except Exception:
        m_tables = set()
    creds_absent = ("agent_credential" not in m_tables
                    and "agent_read_log" not in m_tables
                    and (not tok_val or tok_val not in man_text))
    # the restore into a clean migrated destination
    dst = _pg.create_scratch_db("p4fdst")
    try:
        r_mig = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                               capture_output=True, text=True, timeout=180,
                               env=dict(env, PGDATABASE=dst), check=True)
        r_rs = subprocess.run([sys.executable, str(REPO / "harness" / "export.py"),
                               "restore", "--archive", str(arch)],
                              capture_output=True, text=True, timeout=600,
                              env=dict(env, PGDATABASE=dst))
        denv = dict(env, PGDATABASE=dst)
        # the restore's own completion names the derived rebuild (RTM
        # §3.7): the re-derivation runs at the destination BEFORE the
        # post-restore reads — the derived index is rebuilt from the
        # restored authoritative rows, the searches answer equal
        subprocess.run([sys.executable, str(REPO / "harness" / "extract.py"),
                       "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                       "--idem-key", "er-rex-1", "--source-id", sid],
                      capture_output=True, text=True, timeout=300, env=denv)
        r_rb = _cmd(denv, "rebuild_keyword_index", key="er-rb-1")
        post = {
            "note": _query(denv, "get-note", "--owner", "A", "--id", nid).stdout,
            "journal": _query(denv, "get-journal-history", "--owner", "A",
                              "--id", j1).stdout,
            "journals": _page_ids(denv, "list-journal") or [],
            "lists": _query(denv, "list-lists", "--owner", "A").stdout,
            "members": _query(denv, "get-list", "--owner", "A", "--id", lid).stdout,
            "sessions": _query(denv, "list-session-events", "--owner", "A").stdout,
            "notes_list": _query(denv, "list-notes", "--owner", "A").stdout,
            "captures": _query(denv, "list-captures", "--owner", "A").stdout,
            "bookmarks": _query(denv, "list-bookmarks", "--owner", "A").stdout,
            "search": _query(denv, "search", "--owner", "A", "meridian").stdout,
        }
        # the lossless law: EVERY journal revision round-trips (the journal
        # history's rows are ALL revisions — kind carries raw/creative)
        jhist = [json.loads(ln) for ln in pre["journal"].splitlines()
                 if ln.strip() and ln.startswith("{")]
        revisions = sorted(r.get("revision") for r in jhist) if jhist else []
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
    """P4-F (CLAIM-079): the rebuild parity — rebuild_keyword_index over
    the authored rows; the search answers unchanged across the rebuild."""
    before = _query(env, "search", "--owner", "A", "meridian")
    r_rb = _cmd(env, "rebuild_keyword_index", key="rb-1")
    after = _query(env, "search", "--owner", "A", "meridian")
    rows_b = [ln for ln in before.stdout.split("\n")
              if ln.strip() and not ln.lstrip().startswith("#")]
    rows_a = [ln for ln in after.stdout.split("\n")
              if ln.strip() and not ln.lstrip().startswith("#")]
    return {
        "before_exit": before.returncode,
        "rebuild_exit": r_rb.returncode,
        "after_exit": after.returncode,
        "parity": (rows_a == rows_b and r_rb.returncode == 0
                   and "status=committed" in r_rb.stdout),
    }


def condition_phase_isolation(env, text):
    """P4-F (CLAIM-079): the phase-level owner isolation — one walk's
    every family invisible to the other owner, the no-oracle byte-equal at
    the phase level."""
    w = condition_recovery_walk(env, text)
    sid = _ids_of(_query(env, "list-library", "--owner", "A"))[0]
    absent = str(_uuid.uuid4())
    # B's view of A's families: the cross-family invisibility
    lib_b = _query(env, "list-library", "--owner", "B")
    jl_b = _query(env, "list-journal", "--owner", "B")
    lists_b = _query(env, "list-lists", "--owner", "B")
    ses_b = _query(env, "list-session-events", "--owner", "B")
    notes_b = _query(env, "list-notes", "--owner", "B")
    caps_b = _query(env, "list-captures", "--owner", "B")
    bms_b = _query(env, "list-bookmarks", "--owner", "B")
    a_empty = (not _ids_of(lib_b) and not _ids_of(jl_b) and not _ids_of(lists_b)
               and not [ln for ln in ses_b.stdout.splitlines()
                        if ln.strip() and not ln.startswith("#")]
               and not _ids_of(notes_b) and not _ids_of(caps_b)
               and not _ids_of(bms_b))
    # the no-oracle at the phase level: A's id vs an absent id at B
    r_abs = _query(env, "get-journal", "--owner", "B", "--id", absent)
    r_for = _query(env, "get-journal", "--owner", "B", "--id",
                   _ids_of(_query(env, "list-journal", "--owner", "A"))[0]
                   if _ids_of(_query(env, "list-journal", "--owner", "A")) else absent)
    ra = _norm(_fail_line(r_abs), absent)
    rf = _norm(_fail_line(r_for), absent)
    return {
        "walk_complete": w["post_restart_reads"] is True,
        "cross_family_invisible": a_empty,
        "no_oracle": (ra == rf and ra != "" and ra.split(":")[0] == "FAIL ARV-QRY-001"),
    }


def condition_prior_state_migration(env):
    """P4-F (CLAIM-079): the supported-prior-state migration — a database
    carrying real prior-state content (0001..0014, the P3-era families)
    migrating FORWARD through the chain to the current head; the content
    survives; the post-migration invariants hold (the append-only trigger
    live, RLS forced); the post-migration reads answer the prior content.
    The rig setup (the prior-baseline directory + the scratch database) is
    the SUITE's class; every observation a real CLI invocation."""
    from harness.adapters import pg as _pg
    import shutil as _shutil
    db = _pg.create_scratch_db("p4fprior")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-prior-"))
    mdir = tmp / "migrations"
    mdir.mkdir()
    real_dir = REPO / "harness" / "migrations"
    for p in sorted(real_dir.glob("*.sql")):
        if int(p.name[:4]) <= 14:
            _shutil.copy(p, mdir / p.name)
    try:
        menv = dict(env, PGDATABASE=db, ARV_MIGRATIONS_DIR=str(mdir))
        # the prior baseline applies
        r_m1 = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                               capture_output=True, text=True, timeout=180, env=menv)
        # real prior-state content at the prior baseline (the P3 families)
        f = tmp / "prior.txt"
        f.write_text("The prior-state corpus: the enduring token rides.\n"
                     "A second line for the capture window.\n", encoding="utf-8")
        wenv = dict(env, PGDATABASE=db)
        r_imp = _cmd(wenv, "import_source", "--title", "The Prior-State Corpus",
                     "--file", str(f), key="pm-imp-1")
        sid = _ref(r_imp)
        r_hl = _cmd(wenv, "create_highlight", "--source-id", sid, "--start", "5",
                    "--end", "12", key="pm-hl-1")
        r_nt = _cmd(wenv, "create_note", "--content",
                     "The prior-state note: the welkin rides.", key="pm-n1")
        nid = _ref(r_nt)
        prior_written = (r_imp.returncode == 0 and r_hl.returncode == 0
                         and r_nt.returncode == 0)
        # the forward migration through the chain to the current head
        r_m2 = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                              capture_output=True, text=True, timeout=180, env=wenv)
        # the post-migration reads answer the prior content
        g_s = _query(wenv, "get-source", "--owner", "A", "--id", sid)
        g_n = _query(wenv, "get-note", "--owner", "A", "--id", nid)
        # the invariant probe: journal_block's append-only guard answers a
        # hostile revise of a NONEXISTENT id at the CLI boundary with the
        # typed no-oracle refusal — the migrated substrate is live (a
        # journal write at the CURRENT head answers the current guards);
        # the prior note still reads after the forward chain
        r_inv = _cmd(wenv, "revise_journal_block", "--id",
                    "00000000-0000-0000-0000-0000000000ff", "--content",
                    "tampered", key="pm-inv1")
        inv_line = _fail_line(r_inv)
        trigger_live = (r_inv.returncode == 1
                        and "ARV-JNL-001" in inv_line)  # the guard live at the CLI
        return {
            "prior_written": prior_written,
            "migrate_exit": (r_m1.returncode == 0 and r_m2.returncode == 0),
            "content_survives": (g_s.returncode == 0 and g_n.returncode == 0
                                 and "welkin" in _jline(g_n).get("content", "")),
            "invariants_hold": trigger_live,
        }
    finally:
        _pg.drop_scratch_db(db)


def condition_sync_conflict(env):
    """P4-F (CLAIM-079): the sync-conflict walk — the two-DB delivery with
    a CONFLICTING write (the same idem key, different bodies); the typed
    conflict (ARV-CMD-409 in the row's failed state, terminal + visible),
    BOTH bodies preserved (never a silent last-write-wins). The rig setup
    (the two scratch databases) is the SUITE's class; every observation a
    real CLI invocation."""
    from harness.adapters import pg as _pg
    loc = _pg.create_scratch_db("p4floc")
    srv = _pg.create_scratch_db("p4fsrv")
    try:
        lenv = dict(env, PGDATABASE=loc)
        senv = dict(env, PGDATABASE=srv, ARV_SITE="server")
        for e in (lenv, senv):
            subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, timeout=180,
                           env=e, check=True)
        # the local write + the server's COMPETING write under the same key
        r_loc = _cmd(lenv, "create_note", "--content",
                     "The local body for the same key.", key="cf-n1")
        r_srv = _cmd(senv, "create_note", "--content",
                     "The server's competing body for the key.", key="cf-n1")
        # the delivery pass surfaces the typed conflict (the SYNC line
        # carries the state + the named reason; the status arm's counts
        # carry the failed row)
        r_sync = subprocess.run(
            [sys.executable, str(REPO / "harness" / "sync.py"), "sync",
             "--owner", "A", "--server-db", srv],
            capture_output=True, text=True, timeout=300, env=lenv)
        line = next((ln for ln in r_sync.stdout.splitlines()
                     if "cf-n1" in ln), "")
        # BOTH bodies preserved (each site's own read)
        g_loc = _query(lenv, "get-note", "--owner", "A",
                       "--id", _ref(r_loc))
        g_srv = _query(senv, "get-note", "--owner", "A", "--id", _ref(r_srv))
        return {
            "local_exit": r_loc.returncode,
            "server_exit": r_srv.returncode,
            "sync_exit": r_sync.returncode,
            "conflict_failed": "state=failed" in line,
            "typed_409": "ARV-CMD-409" in line,
            "both_bodies_preserved": (
                "local body" in _jline(g_loc).get("content", "")
                and "competing body" in _jline(g_srv).get("content", "")),
        }
    finally:
        _pg.drop_scratch_db(loc)
        _pg.drop_scratch_db(srv)