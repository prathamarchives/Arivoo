#!/usr/bin/env python3
"""harness/extract.py — the extraction command (P3-03a; RTM §2.3/§3.6, SYS-06/07).

The generation machine (§3.6's derived-state pattern, the extraction's first
instantiation — the suite EXT-01..12 pins every transition):
  (empty) --extract--> building               [the staging row, its OWN transaction]
  building --complete generation--> current   [supersede + passages + current in ONE
                                               transaction — complete-or-failed: a
                                               partial generation is never presented]
  building --crash--> building                [persists; the SAME-key retry completes
                                               it; a NEW-key extract supersedes it]
  building --failure--> failed                [the named ARV-EXT-003; the previous
                                               current generation STAYS current]
  current --new extraction, SAME source--> current(new) + superseded(old)
  current --new edition, a NEW source row--> the new source's generation only —
                                               a generation NEVER crosses source rows

§2.9's DERIVED class: the generation + passage rows are disposable, rebuildable,
NEVER authoritative — NO append-only trigger (state transitions are lawful
UPDATEs, the 0005 disposable precedent), NO command_log row (a derived build is
never an owner command); the idempotency record rides the generation row itself
(UNIQUE(owner_scope, idempotency_key) + body_hash, the 409 guard).

The pinned readable-text/Markdown extractor (arivoo-text-blocks.v1): UTF-8
decode under the source's digest (a decode failure is the named ARV-EXT-002 —
the boundary is the DECODE, never the media type); the NUL guard (a valid-UTF-8
text containing U+0000 is the named ARV-EXT-005 — the psql literal transport
cannot carry a NUL byte-exactly, and a passage must be the EXACT slice its
offsets and digest claim: the refusal, never a corrupted commit); the
blank-line block split with a Markdown heading ATTACHED FORWARD to the content
block that follows it (a heading with NO following content block is its own
passage — the tiling keeps coverage exact); the passages TILE the content span
(end_off equals the next start_off; the last ends at len(text); a leading
blank-line prefix precedes the first passage) — exact, complete location
evidence, never a guess; each passage digest re-hashes its text.

The shared spine pieces (Session, _q, _sess_row, canonical_body, _dead_exit)
come from harness.commands — ONE session machinery (the P3-01 DRY); what
differs is the protocol (no command_log), never the session.

Exit 0 = acked (committed or replayed); exit 1 = refused (named); exit 2 =
crashed (no ack — the crash injector's vocabulary).
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import blob, clock, ids  # noqa: E402
from harness.commands import (MARK_BEGUN, MARK_COMMITTED, MARK_INSERTS,  # noqa: E402
                              Session, _CONN, _DUP, _dead_exit, _q, _sess_row,
                              canonical_body)

EXTRACTOR = "arivoo-text-blocks.v1"
EXTRACTOR_CONFIG = json.dumps({"block": "blank-line", "encoding": "utf-8",
                               "heading": "attach-forward", "tiling": "contiguous"},
                              sort_keys=True, separators=(",", ":"))
_HEADING = re.compile(r"^#{1,6}(?:\s|$)")


def split_passages(text: str) -> list:
    """The pinned readable-text/Markdown split: blank-line blocks; a Markdown
    heading block ATTACHES FORWARD to the content block that follows it (a
    heading with NO following content block is its own passage — the tiling
    keeps coverage exact); the passages TILE the content span (each end_off ==
    the next start_off; the last ends at len(text); a leading blank-line prefix
    precedes the first passage).
    Returns [(start, end), ...]; empty when the text carries no content block
    (the ARV-EXT-001 class)."""
    n = len(text)

    def _line_end(k):  # the index just past the line starting at k
        eol = text.find("\n", k)
        return n if eol == -1 else eol + 1

    blocks, i = [], 0
    while i < n:
        while i < n and text[i:_line_end(i)].strip() == "":
            i = _line_end(i)
        if i >= n:
            break
        start, k = i, i
        while k < n and text[k:_line_end(k)].strip() != "":
            k = _line_end(k)
        blocks.append((start, k))
        i = k
    if not blocks:
        return []
    groups, pend = [], None  # a heading run attaches forward to the next content block
    for s, e in blocks:
        if _HEADING.match(text[s:e].split("\n", 1)[0]):
            if pend is None:
                pend = s
        else:
            groups.append([pend if pend is not None else s, e])
            pend = None
    if pend is not None:  # a trailing heading with no following content: its own passage
        groups.append([pend, blocks[-1][1]])
    return [(groups[g][0], groups[g + 1][0] if g + 1 < len(groups) else n)
            for g in range(len(groups))]


def _stage_building(sess: "Session", *, gen_id, source_id, ordinal, digest, idem_key,
                    body_hash, owner, actor, client_id) -> bool:
    """Phase 1 — the building row in its OWN transaction (the crash substrate: a
    pre-commit crash of the completion leaves this row with ZERO passages)."""
    ts, run_id, ih = clock.now(), "run-" + client_id, body_hash[:16]
    stmt = (f"INSERT INTO arv.extraction_generation (id, source_id, ordinal, state, extractor, "
            f"extractor_config, input_digest, idempotency_key, body_hash, owner_scope, actor, "
            f"run_id, input_hash, created_at, updated_at) VALUES ({_q(gen_id)}, {_q(source_id)}, "
            f"{ordinal}, 'building', {_q(EXTRACTOR)}, {_q(EXTRACTOR_CONFIG)}, {_q(digest)}, "
            f"{_q(idem_key)}, {_q(body_hash)}, {_q(owner)}, {_q(actor)}, {_q(run_id)}, {_q(ih)}, "
            f"{_q(ts)}, {_q(ts)});")
    try:
        sess.send("BEGIN;")
        sess.send(stmt)
        sess.send("COMMIT;")
        sess.send(f"\\echo {MARK_COMMITTED}")
        sess.read_until(MARK_COMMITTED)
        return True
    except TimeoutError:
        rc = _dead_exit(sess, idem_key=idem_key)
        if rc is None:
            print(f"FAIL ARV-CMD-010: the building transaction for key {idem_key!r} did not "
                  "reach its commit marker — the honest unknown")
            print("      repair: inspect the rig's health; the same-key retry is safe "
                  "(nothing partial was presented)")
        return False


def _mark_failed(*, db, owner, gen_id, cause, idem_key) -> int:
    """The §3.6 failure transition — building -> failed with the NAMED reason, on
    a FRESH session (the completing session is dead); the previous current
    generation was never touched (the completion rolled back atomically)."""
    line = next((ln.strip() for ln in cause.splitlines() if "ERROR" in ln),
                cause.strip() or "unrecognized cause")
    observed = line[line.find("ERROR"):] if "ERROR" in line else line[:300]
    try:
        sess = Session(db, "arv_app", owner)
    except RuntimeError as e:
        print(f"FAIL ARV-EXT-003: the extraction failed mid-build and the failed-state update "
              f"could not open a session — {e}")
        return 1
    try:
        sess.send("BEGIN;")
        sess.send(f"UPDATE arv.extraction_generation SET state='failed', "
                  f"fail_reason={_q('ARV-EXT-003: ' + observed[:300])}, "
                  f"updated_at={_q(clock.now())} WHERE id={_q(gen_id)};")
        sess.send("COMMIT;")
        sess.send(f"\\echo {MARK_COMMITTED}")
        sess.read_until(MARK_COMMITTED)
    except TimeoutError:
        print(f"FAIL ARV-CMD-010: the failed-state update for key {idem_key!r} did not reach "
              "its commit marker — the generation stays building; the same-key retry completes it")
        print("      repair: inspect the rig's health; the retry is safe (no partial generation "
              "was presented)")
        return 1
    finally:
        sess.close()
    print("FAIL ARV-EXT-003: the extraction failed mid-build — the generation is failed with "
          "the named reason; the previous current generation STAYS current (never a partial "
          "presentation)")
    print(f"      observed cause: {observed[:200]}")
    print("      repair: retry with a NEW key (the same key answers the recorded failure); "
          "the previous current generation was never touched")
    return 1


def _dead_classify(sess: "Session", *, db, owner, gen_id, idem_key) -> int:
    """A dead completing session: the DRAINED observed cause classifies — an SQL
    error (outside the duplicate-key/connection classes) is the named mid-build
    failure (ARV-EXT-003, the failed row); the spine's death classes (011/012/
    010) answer the rest; a live stall is the honest ARV-CMD-010."""
    cause = sess.dead_reason()
    if cause is not None and "ERROR" in cause and _DUP not in cause \
            and not any(s in cause for s in _CONN):
        return _mark_failed(db=db, owner=owner, gen_id=gen_id, cause=cause, idem_key=idem_key)
    rc = _dead_exit(sess, idem_key=idem_key)
    if rc is not None:
        return rc
    print("FAIL ARV-CMD-010: the completing session stalled without the marker — the honest "
          "unknown; raw cause unavailable (the session is live)")
    print("      repair: inspect the rig's health; the same-key retry is safe")
    return 1


def _complete(sess: "Session", *, db, owner, actor, client_id, idem_key, gen_id,
              source_id, text, spans, body_hash, crash_at: str = None) -> int:
    """Phase 2 — ONE completion transaction: supersede the source's current and
    stale building rows, insert every passage, flip this generation current,
    COMMIT, ack. A crash at pre-commit rolls it ALL back (the building row
    persists with zero passages — complete-or-failed); a SQL failure mid-build
    marks the generation failed (ARV-EXT-003) on a fresh session."""
    run_id, ih = "run-" + client_id, body_hash[:16]
    stmts = [f"UPDATE arv.extraction_generation SET state='superseded', "
             f"updated_at={_q(clock.now())} WHERE source_id={_q(source_id)} "
             f"AND state IN ('current', 'building') AND id <> {_q(gen_id)};"]
    for ordinal, (s, e) in enumerate(spans, 1):
        chunk = text[s:e]
        stmts.append(f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, "
                     f"text, digest, owner_scope, actor, run_id, input_hash, created_at) VALUES "
                     f"({_q(ids.new_id())}, {_q(gen_id)}, {ordinal}, {s}, {e}, {_q(chunk)}, "
                     f"{_q(blob.digest_of(chunk.encode('utf-8')))}, {_q(owner)}, {_q(actor)}, "
                     f"{_q(run_id)}, {_q(ih)}, {_q(clock.now())});")
    stmts.append(f"UPDATE arv.extraction_generation SET state='current', "
                 f"updated_at={_q(clock.now())} WHERE id={_q(gen_id)};")
    try:
        sess.send("BEGIN;")
        sess.send(f"\\echo {MARK_BEGUN}")
        sess.read_until(MARK_BEGUN)
    except TimeoutError:
        return _dead_classify(sess, db=db, owner=owner, gen_id=gen_id, idem_key=idem_key)
    if crash_at == "after-begin":
        sess.kill()
        return 2
    for s in stmts:
        sess.send(s)
    sess.send(f"\\echo {MARK_INSERTS}")
    try:
        sess.read_until(MARK_INSERTS)
    except TimeoutError:
        return _dead_classify(sess, db=db, owner=owner, gen_id=gen_id, idem_key=idem_key)
    if crash_at == "pre-commit":
        sess.kill()
        return 2
    sess.send("COMMIT;")
    sess.send(f"\\echo {MARK_COMMITTED}")
    try:
        sess.read_until(MARK_COMMITTED)
    except TimeoutError:
        return _dead_classify(sess, db=db, owner=owner, gen_id=gen_id, idem_key=idem_key)
    if crash_at == "post-commit-pre-ack":
        sess.kill()
        return 2
    print(f"ACK command=extract_source idem_key={idem_key} status=committed "
          f"result_ref={gen_id} source_id={source_id}")
    return 0


def extract_source(*, db, owner, actor, client_id, idem_key, source_id,
                   crash_at: str = None) -> int:
    """The extraction command: validation (the source read under RLS, the blob
    verify, the decode, the split) precedes ANY row; the idempotency record
    rides the generation row; the same key resumes a crashed building row and
    replays a terminal one; the completion publishes complete-or-failed."""
    body = json.dumps({"source_id": source_id}, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)
    body_hash = hashlib.sha256(canonical_body(command="extract_source", client_id=client_id,
                                               owner_scope=owner, actor=actor,
                                               payload=body).encode()).hexdigest()
    sess = Session(db, "arv_app", owner)
    try:
        digest = _sess_row(sess, f"SELECT digest || '|' FROM arv.source "
                                 f"WHERE id={_q(source_id)};").split("|")[0]
        if not digest:
            print(f"FAIL ARV-EXT-004: source {source_id} does not exist in the caller's scope — "
                  "a cross-owner or dangling extraction target is REFUSED at the boundary (RTM §6)")
            print("      repair: import the source first; an extraction may only read a source "
                  "version visible to this owner")
            return 1
        try:
            data = blob.get(digest)
        except KeyError as e:
            print(f"FAIL ARV-CAP-004: the source's blob failed to verify — "
                  f"{e.args[0] if e.args else e}")
            print("      repair: the store is corrupt at this digest; never an extraction "
                  "against unverifiable bytes")
            return 1
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            print("FAIL ARV-EXT-002: the source is not valid UTF-8 text — the readable-text "
                  "boundary (the DECODE, never the media type); the extraction never guesses a text")
            print("      repair: import readable UTF-8 text bytes — the boundary is the decode, "
                  "not the media type; binary formats land with their own slices")
            return 1
        if "\x00" in text:
            print("FAIL ARV-EXT-005: the source text contains a NUL character (U+0000) — the "
                  "psql literal transport cannot carry it byte-exactly (the C-string boundary "
                  "truncates the statement mid-literal); the extraction refuses rather than "
                  "commit a passage that is not the EXACT slice its offsets and digest claim")
            print("      repair: remove the NUL from the source and re-import as a new edition — "
                  "the complete-or-failed contract: a text that cannot survive the literal path "
                  "byte-exactly is a named refusal, never a corrupted commit")
            return 1
        spans = split_passages(text)
        if not spans:
            print("FAIL ARV-EXT-001: the source is empty (no content block to derive passages "
                  "from) — an empty input is a named refusal, never an empty current generation")
            print("      repair: import a non-empty source; the refusal precedes any row")
            return 1
        grow = _sess_row(sess, f"SELECT state || '|' || id || '|' || body_hash FROM "
                              f"arv.extraction_generation WHERE owner_scope={_q(owner)} "
                              f"AND idempotency_key={_q(idem_key)};")
        if grow:
            gstate, gid, ghash = (grow.split("|") + ["", ""])[:3]
            if ghash != body_hash:
                print(f"FAIL ARV-CMD-409: idempotency key {idem_key!r} is already recorded "
                      "with a DIFFERENT body (no silent overwrite — exactly-once is a contract)")
                print("      repair: use a new idempotency key for a new body; the same key "
                      "must mean the same command")
                return 1
            if gstate != "building":
                print(f"ACK command=extract_source idem_key={idem_key} status=replayed "
                      f"result_ref={gid} source_id={source_id} state={gstate}")
                return 0
            gen_id = gid  # the crashed attempt: the SAME key resumes THIS ordinal
        else:
            gen_id = ids.new_id()
            ordinal = _sess_row(sess, f"SELECT (COALESCE(MAX(ordinal), 0) + 1) || '|' FROM "
                                      f"arv.extraction_generation WHERE "
                                      f"source_id={_q(source_id)};").split("|")[0] or "1"
            if not _stage_building(sess, gen_id=gen_id, source_id=source_id,
                                   ordinal=int(ordinal), digest=digest, idem_key=idem_key,
                                   body_hash=body_hash, owner=owner, actor=actor,
                                   client_id=client_id):
                return 1
        return _complete(sess, db=db, owner=owner, actor=actor, client_id=client_id,
                         idem_key=idem_key, gen_id=gen_id, source_id=source_id, text=text,
                         spans=spans, body_hash=body_hash, crash_at=crash_at)
    except TimeoutError as e:
        print(f"FAIL ARV-CMD-010: {e}")
        return 1
    finally:
        try:
            sess.close()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser(description="the extraction command path (P3-03a: the "
                                             "derived-build generations — §2.9's disposable class)")
    ap.add_argument("--owner", required=True)
    ap.add_argument("--actor", default="owner",
                    choices=["owner", "runtime-agent", "worker", "model-decision"])
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--idem-key", required=True)
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--crash-at", default=None,
                    choices=["after-begin", "pre-commit", "post-commit-pre-ack"])
    a = ap.parse_args()
    return extract_source(db=os.environ.get("PGDATABASE", "postgres"), owner=a.owner,
                          actor=a.actor, client_id=a.client_id, idem_key=a.idem_key,
                          source_id=a.source_id, crash_at=a.crash_at)


if __name__ == "__main__":
    sys.exit(main())
