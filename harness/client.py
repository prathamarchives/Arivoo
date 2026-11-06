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
