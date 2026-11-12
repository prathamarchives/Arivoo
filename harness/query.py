#!/usr/bin/env python3
"""harness/query.py — the authenticated retrieval surface (P3-01; RTM SYS-09)
+ the typed anchor resolution (P3-03b; RTM §2.9 item 4, SYS-05).

Every query runs through the approved adapter as arv_app WITH the owner GUC
set — RLS scopes every row; an id outside the caller's scope and a nonexistent
id are the SAME refusal (ARV-QRY-001), never a side channel revealing another
owner's object existence (RTM §2.10 on the read path). Reads are
side-effect-free. Exit 0 = rows (one JSON line for get-*; one id per line for
list-captures) AND exit 0 = a typed resolution ANSWER (resolved | unresolved |
ambiguous — SYS-05's states are answers, never failures); exit 1 = the named
refusal.

P4-C slice one (CLAIM-070; record 62 §2): the library + the current-reading
state, over the LANDED substrate (no new table, no second position path) —
  list-library         the owner's imported sources as a stable, bounded,
                       paginated list (the _list_arm keyset contract over
                       arv.source; membership IS the source set — rows are
                       BORN complete at import, the failed import's
                       dead-letter is the journal's, never the library's)
  get-reading-state    the derived current-reading view: every source with
                       its last-saved position + the generation binding, or
                       the honest no_position_saved state — the rows ride
                       _position_row (the SAME builder get-position uses;
                       the derived view can never drift from the arm it
                       derives from)
  list-session-events  the owner's session/dwell event stream (D-010's
                       durable behavior data: the closed vocabulary
                       session_start/checkpoint/dwell/session_end, the
                       coarse spans, the coarse dwell), bounded + paginated
                       on the same list contract — the recorded rows only,
                       never retargeted

P4-C slice three (CLAIM-072; record 64 §2): the journal/blocks surface —
the writing lab (source-optional raw/creative blocks, the long raw
thinking preserved losslessly, no forced short-note funnel):
  list-journal         the owner's journal blocks as a stable, bounded,
                       paginated list (the _list_arm keyset contract over
                       arv.journal_block; one row per block IDENTITY — a
                       revisioned block is one journal row, never one per
                       revision)
  get-journal          the single-block read — the CURRENT revision's
                       whole content (the lossless round-trip's read half;
                       the U+2028-class line-safe form), kind, and the
                       optional source binding (null when sourceless —
                       a first-class row)
  get-journal-history  the governed history — EVERY revision in order,
                       one JSON line per row (the export-ready form)

P4-C slice five (CLAIM-074; record 66 §2): the reading-list surface — the
user-defined lists over the landed library (the North Star owner words'
third surface). The membership is an EVENT HISTORY (every add/remove an
append-only event row); the CURRENT membership is DERIVED (the last op per
pair wins — a projection; the event rows the recovery substrate):
  list-lists           the owner's lists as a stable, bounded, paginated
                       list (one JSON line per list: the id, the name, the
                       derived member count, the created_at; the keyset
                       walk on the list id)
  get-list             one list's CURRENT membership — one JSON line per
                       active member (the source id + the added_at),
                       bounded + paginated on the same list contract; the
                       no-id-echo no-oracle (absent and another owner's
                       the SAME refusal, byte-equal whatever was asked)

THE TYPED RESOLUTION (resolve-anchor; P3-03b): a typed query, NEVER a
nearest-match guess —
  resolved     the location evidence validates WITHIN the anchor's OWN Source
               version against the CURRENT generation: the digest chain (the
               anchor's source_digest == the generation's input_digest) AND a
               contiguous covering of [start_off, end_off) by the passages AND
               the recorded contexts still surround the slice in the derived
               view
  unresolved   the honest miss with a NAMED cause: no-current-generation;
               stale-generation (the digest chain broke — the typed stale
               surface); location-unmatched (no covering and the fallback
               evidence found fewer than two hits — a single candidate is a
               DETECTION, never a retarget)
  ambiguous    the fallback matching evidence (context_before + context_after)
               locates the pattern at TWO OR MORE positions in the derived
               view — the anchor's evidence cannot pick one; the original
               evidence is preserved (the anchor row is immutable)
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import pg  # noqa: E402
from harness.commands import API_VERSION  # noqa: E402  # P4-00b: the version's ONE home (commands.py) — the read surface reports the same value as every write ack

# P4-00b (CLAIM-063): the LIST CONTRACT's bounds — every list response is
# BOUNDED (the default page), the client pages with the --after keyset cursor,
# and an out-of-bounds request is the typed ARV-QRY-004 refusal (never a
# silent clamp, never an unbounded dump). The bounds change only through the
# boundary contract's own change process.
DEFAULT_LIST_LIMIT = 100
MAX_LIST_LIMIT = 1000

# THE P1 SEV FIX (the round-1 BLOCKED finding): free-text fields legally carry
# pipes and newlines, so the output is structured AT THE SQL BOUNDARY (row_to_json
# emits ONE escaped JSON line per row) — never re-parsed by splitting psql text.
CAP_SQL = ("SELECT row_to_json(t)::text FROM (SELECT h.id AS id, h.revision, h.selected_text, "
           "h.source_id, h.anchor_id, a.source_digest, a.start_off AS start, a.end_off AS end, a.context_before, "
           "a.context_after, a.media_type, h.created_at FROM arv.highlight h "
           "JOIN arv.anchor a ON a.id = h.anchor_id WHERE h.id = {id} "
           "ORDER BY h.revision DESC LIMIT 1) t;")
SRC_SQL = ("SELECT row_to_json(t)::text FROM (SELECT s.id AS id, s.work_id, w.title, s.digest, "
           "s.media_type, s.byte_size, s.import_state, s.source_version, s.created_at "
           "FROM arv.source s JOIN arv.work w ON w.id = s.work_id WHERE s.id = {id}) t;")
# P4-A slice two (CLAIM-066; record 58 §2): the position read arm — ONE
# statement, ONE snapshot: the source existence (the outer row — absent under
# RLS yields NO row, the same refusal as get-source), the last-saved position
# (max save_ordinal — the DERIVED current, never a state column), and the
# source's CURRENT generation (the serving-generation binding's other half).
# The flag|payload form rides the SAME structured-at-the-SQL-boundary law: the
# position travels as row_to_json text (pipes/newlines escaped by SQL itself);
# '' means NEVER SAVED (the typed no_position_saved ANSWER, never a failure).
POS_SQL = ("SELECT COALESCE((SELECT row_to_json(p)::text FROM "
           "(SELECT q.save_ordinal, q.start_off, q.end_off, q.generation_id AS saved_generation_id "
           "FROM arv.reading_position q WHERE q.source_id = s.id AND q.owner_scope = s.owner_scope "
           "ORDER BY q.save_ordinal DESC LIMIT 1) p), '') || '|' || "
           "COALESCE((SELECT g.id::text FROM arv.extraction_generation g "
           "WHERE g.source_id = s.id AND g.owner_scope = s.owner_scope AND g.state = 'current' "
           "ORDER BY g.ordinal DESC LIMIT 1), '') FROM arv.source s WHERE s.id = {id};")
# P3-04 (RTM §3.3): tombstoned hides from ordinary retrieval — the list EXCLUDES
# the ids whose committed event parity says tombstoned (tombstone_count >
# restore_count; order-independent, rebuildable — never a state column).  An
# HAVING over zero lifecycle rows yields no row -> NOT EXISTS -> active stays listed.
LIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT DISTINCT h.id FROM arv.highlight h "
            "WHERE {after}NOT EXISTS (SELECT 1 FROM arv.highlight_lifecycle l "
            "WHERE l.highlight_id = h.id AND l.owner_scope = h.owner_scope "
            "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
            "count(*) FILTER (WHERE l.event = 'restore')) ORDER BY h.id LIMIT {limit}) t;")
# P3-04: the governed history — EVERY revision + EVERY lifecycle event, one JSON
# row per line (the ANC-10/#88 newline-only framing contract: row_to_json escapes
# below U+0020 ONLY, so U+2028 travels raw inside the string and the reader splits
# on \n ONLY).  The current view is DERIVED from these rows (HLG-09's rebuild).
HIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT h.id, 'revision' AS kind, h.revision, "
            "h.selected_text, h.anchor_id, NULL::text AS event, h.actor, h.created_at "
            "FROM arv.highlight h WHERE h.id = {id} UNION ALL "
            "SELECT l.highlight_id, 'lifecycle' AS kind, NULL::integer AS revision, "
            "NULL::text AS selected_text, NULL::uuid AS anchor_id, l.event, l.actor, "
            "l.created_at FROM arv.highlight_lifecycle l WHERE l.highlight_id = {id}) t "
            "ORDER BY t.created_at, t.revision NULLS LAST, t.kind;")
# P3-04: the single-id parity read — tombstoned iff tombstones > restores.
STATE_SQL = ("SELECT count(*) FILTER (WHERE event = 'tombstone') || '|' || "
             "count(*) FILTER (WHERE event = 'restore') FROM arv.highlight_lifecycle "
             "WHERE highlight_id = {id};")
ANC_SQL = ("SELECT row_to_json(t)::text FROM (SELECT a.id AS anchor_id, a.source_id, a.source_digest, "
           "a.start_off, a.end_off, a.context_before, a.context_after, g.id AS generation_id, "
           "g.input_digest FROM arv.anchor a LEFT JOIN arv.extraction_generation g "
           "ON g.source_id = a.source_id AND g.state = 'current' WHERE a.id = {id}) t;")
PASS_SQL = ("SELECT row_to_json(t)::text FROM (SELECT id, ordinal, start_off, end_off, text "
            "FROM arv.passage WHERE generation_id = {gid} ORDER BY ordinal) t;")
# P3-05 (RTM §2.5 item 6): the bookmark read — the entity row + the version-tied
# location (the anchor join carries the offsets; NO content column exists)
BM_SQL = ("SELECT row_to_json(t)::text FROM (SELECT b.id AS bookmark_id, b.revision, b.source_id, "
          "b.anchor_id, a.start_off, a.end_off, a.media_type, b.created_at FROM arv.bookmark b "
          "JOIN arv.anchor a ON a.id = b.anchor_id WHERE b.id = {id} "
          "ORDER BY b.revision DESC LIMIT 1) t;")
# the §3.3 parity read — tombstoned iff tombstones > restores (the 0007 convention)
BMSTATE_SQL = ("SELECT count(*) FILTER (WHERE event = 'tombstone') || '|' || "
               "count(*) FILTER (WHERE event = 'restore') FROM arv.bookmark_lifecycle "
               "WHERE bookmark_id = {id};")
# tombstoned hidden from the ordinary listing (the LIST_SQL convention — the
# HAVING-over-zero-rows form keeps active listed)
BMLIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT DISTINCT b.id FROM arv.bookmark b "
              "WHERE {after}NOT EXISTS (SELECT 1 FROM arv.bookmark_lifecycle l "
              "WHERE l.bookmark_id = b.id AND l.owner_scope = b.owner_scope "
              "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
              "count(*) FILTER (WHERE l.event = 'restore')) ORDER BY b.id LIMIT {limit}) t;")
# the governed history — every revision + every lifecycle event, one JSON row per
# line (the newline-only framing law; the revision rows carry the anchor's location
# evidence so the current view rebuilds from history ALONE — BMK-09's projection)
BMHIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT b.id, 'revision' AS kind, b.revision, "
              "b.source_id, b.anchor_id, a.start_off, a.end_off, a.context_before, "
              "a.context_after, NULL::text AS event, b.actor, b.created_at "
              "FROM arv.bookmark b JOIN arv.anchor a ON a.id = b.anchor_id WHERE b.id = {id} "
              "UNION ALL "
              "SELECT l.bookmark_id, 'lifecycle' AS kind, NULL::integer AS revision, "
              "NULL::uuid AS source_id, NULL::uuid AS anchor_id, NULL::integer AS start_off, "
              "NULL::integer AS end_off, NULL::text AS context_before, "
              "NULL::text AS context_after, l.event, l.actor, l.created_at "
              "FROM arv.bookmark_lifecycle l WHERE l.bookmark_id = {id}) t "
              "ORDER BY t.created_at, t.revision NULLS LAST, t.kind;")
# P3-06 slice one (RTM §2.5 item 7 + §3.3): the note read — ONE statement,
# ONE snapshot: the entity's CURRENT revision + the authored content + the
# DERIVED tombstone parity share the same read (the #91 round-3 read-path
# repair — the two-read form let a tombstone commit between the state check
# and the content fetch, returning a tombstoned note's ordinary content; a
# read whose snapshot begins after the commit must NEVER return it).  The
# parity flag rides the line before the payload (the revision|state
# convention — the || concatenation casts the boolean to text as the full
# word true/false, never a pipe, so the one-split parse is exact); zero rows
# P3-06 (RTM §2.5 item 7): the note read — state + content + the OWN
# version-aware reference set in ONE statement, ONE snapshot (the #91 round-3
# repair's form preserved: a post-tombstone read NEVER returns the content,
# and the refs now ride the same consistent snapshot); absent/out-of-scope
# stays the absent/out-of-scope refusal (RLS — never a side channel); the
# content rides the JSON string raw below U+0020 ONLY, so U+2028/U+2029
# travel raw and the framing law holds on this arm too
NOTE_SQL = ("SELECT COALESCE((SELECT count(*) FILTER (WHERE event = 'tombstone') > "
            "count(*) FILTER (WHERE event = 'restore') FROM arv.note_lifecycle "
            "WHERE note_id = {id}), false) || '|' || row_to_json(t)::text FROM "
            "(SELECT n.id AS note_id, n.revision, n.content, n.actor, n.created_at, "
            "(SELECT json_agg(json_build_object('kind', r.ref_kind, 'id', r.ref_id, "
            "'revision', r.ref_revision) ORDER BY r.ref_kind, r.ref_id, "
            "r.ref_revision) FROM arv.note_reference r WHERE r.note_id = n.id AND "
            "r.note_revision = n.revision AND r.owner_scope = n.owner_scope) AS refs "
            "FROM arv.note n WHERE n.id = {id} ORDER BY n.revision DESC LIMIT 1) t;")
# tombstoned hidden from the ordinary listing (the LIST_SQL convention — the
# HAVING-over-zero-rows form keeps active listed)
NOTELIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT DISTINCT n.id FROM arv.note n "
                "WHERE {after}NOT EXISTS (SELECT 1 FROM arv.note_lifecycle l "
                "WHERE l.note_id = n.id AND l.owner_scope = n.owner_scope "
                "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
                "count(*) FILTER (WHERE l.event = 'restore')) ORDER BY n.id LIMIT {limit}) t;")
# the governed history — every revision + every lifecycle event, one JSON row
# per line (the newline-only framing law; the revision rows carry the content
# so the current view rebuilds from history ALONE — the export-ready history)
NOTEHIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT n.id, 'revision' AS kind, "
                "n.revision, n.content, (SELECT json_agg(json_build_object('kind', "
                "r.ref_kind, 'id', r.ref_id, 'revision', r.ref_revision) ORDER BY "
                "r.ref_kind, r.ref_id, r.ref_revision) FROM arv.note_reference r "
                "WHERE r.note_id = n.id AND r.note_revision = n.revision AND "
                "r.owner_scope = n.owner_scope) AS refs, NULL::text AS event, n.actor, "
                "n.created_at FROM arv.note n WHERE n.id = {id} UNION ALL "
                "SELECT l.note_id, 'lifecycle' AS kind, NULL::integer AS revision, "
                "NULL::text AS content, NULL::json AS refs, l.event, l.actor, "
                "l.created_at FROM arv.note_lifecycle l WHERE l.note_id = {id}) t "
                "ORDER BY t.created_at, t.revision NULLS LAST, t.kind;")

# P3-07 (RTM §2.5 the findability rung): the keyword search — the derived
# index queried under the AUTHORITATIVE current view: the tombstone parity
# joins at QUERY time (the index never governs visibility; a tombstoned
# capture is filtered by the lifecycle parity, a restored one returns); the
# multi-term AND semantics (a document matches only when EVERY term hits it
# — HAVING count(DISTINCT token) = the term count); the deterministic
# ordering (kind, entity_id). The result line: kind|id|revision|freq.
SEARCH_SQL = ("SELECT k.kind || '|' || k.entity_id || '|' || k.revision || '|' || "
              "count(DISTINCT k.token)::text FROM arv.keyword_index k WHERE "
              "k.token = ANY ({terms}) AND ("
              "(k.kind = 'note' AND NOT EXISTS (SELECT 1 FROM arv.note_lifecycle l "
              "WHERE l.note_id = k.entity_id AND l.owner_scope = k.owner_scope "
              "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
              "count(*) FILTER (WHERE l.event = 'restore')))"
              " OR (k.kind = 'highlight' AND NOT EXISTS (SELECT 1 FROM arv.highlight_lifecycle l "
              "WHERE l.highlight_id = k.entity_id AND l.owner_scope = k.owner_scope "
              "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
              "count(*) FILTER (WHERE l.event = 'restore')))"
              " OR (k.kind = 'bookmark' AND NOT EXISTS (SELECT 1 FROM arv.bookmark_lifecycle l "
              "WHERE l.bookmark_id = k.entity_id AND l.owner_scope = k.owner_scope "
              "HAVING count(*) FILTER (WHERE l.event = 'tombstone') > "
              "count(*) FILTER (WHERE l.event = 'restore')))"
              " OR k.kind = 'source') "
              "AND (k.kind = 'source' OR k.revision = ("
              "SELECT MAX(e.revision) FROM arv.keyword_index e WHERE e.owner_scope = k.owner_scope "
              "AND e.kind = k.kind AND e.entity_id = k.entity_id)) "
              "GROUP BY k.kind, k.entity_id, k.revision "
              "HAVING count(DISTINCT k.token) = {nterms} ORDER BY k.kind, k.entity_id;")
# P4-C slice one (CLAIM-070; record 62 §2): the library membership list —
# the owner's imported sources (RLS the owner boundary).  A source row is
# BORN complete at import (a failed import never creates one — its
# dead-letter is the import journal's, never the library's), so membership
# IS the arv.source set: stable (append-only, no source tombstone), never
# a hand-maintained second registry.  The {after}/{limit} placeholders
# ride the _list_arm keyset contract.
SRCLIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT s.id FROM arv.source s "
               "WHERE {after}TRUE ORDER BY s.id LIMIT {limit}) t;")
# P4-C slice one (CLAIM-070; record 62 §2): the current-reading state — the
# SET-SHAPED lift of POS_SQL (one statement, one snapshot per page): every
# source carries its last-saved position (max save_ordinal — the DERIVED
# current) and its CURRENT generation, the same derivation get-position
# performs per source.  THE NO-SECOND-PATH LAW: this arm formats its rows
# through _position_row — the SAME row builder get-position uses (never a
# drifting second implementation).  The line form id|pos|cur splits EXACTLY
# on two pipes: the id is a uuid, the payload is row_to_json over ints + a
# uuid (NO free-text field — no pipe can occur inside it; the P1 SEV fix
# class holds by the payload's own vocabulary), the generation a uuid or ''.
READING_SQL = ("SELECT s.id || '|' || COALESCE((SELECT row_to_json(p)::text FROM "
               "(SELECT q.save_ordinal, q.start_off, q.end_off, q.generation_id AS saved_generation_id "
               "FROM arv.reading_position q WHERE q.source_id = s.id AND q.owner_scope = s.owner_scope "
               "ORDER BY q.save_ordinal DESC LIMIT 1) p), '') || '|' || "
               "COALESCE((SELECT g.id::text FROM arv.extraction_generation g "
               "WHERE g.source_id = s.id AND g.owner_scope = s.owner_scope AND g.state = 'current' "
               "ORDER BY g.ordinal DESC LIMIT 1), '') "
               "FROM arv.source s WHERE {after}TRUE ORDER BY s.id LIMIT {limit};")
# P4-C slice two (CLAIM-071; record 63 §2): the session/dwell event listing —
# the owner's behavior-event stream, one JSON row per event (the framing
# law), ordered by the event id (the keyset convention every list arm
# rides).  The row reports the RECORDED facts only (the serving-generation
# binding as written at event time — the behavior history is provenance,
# never retargeted by a later re-extraction); dwell_ms is NULL on every
# non-dwell event (the shape law at the substrate).
SESLIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT e.id AS event_id, e.source_id, "
               "e.event, e.event_ordinal, e.start_off, e.end_off, e.dwell_ms, "
               "e.generation_id, e.created_at FROM arv.reading_session e "
               "WHERE {after}TRUE ORDER BY e.id LIMIT {limit}) t;")

# P4-C slice three (CLAIM-072; record 64 §2): the journal/blocks surface —
# the writing lab's read arms.  The listing is the DISTINCT block identity
# (a revisioned block is ONE journal row, never one per revision), ordered
# by the block id (the keyset convention every list arm rides).  The
# single-block read takes the CURRENT revision (max under the append-only
# law — the row the last write authored); the history takes EVERY revision
# in order (the export-ready governed history).  content rides row_to_json
# (the ANC-10 framing law: JSON escapes the newlines, the id|payload pipes
# never appear raw).
JNLLIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT DISTINCT j.id FROM arv.journal_block j "
               "WHERE {after}TRUE ORDER BY j.id LIMIT {limit}) t;")
# P4-C slice five (CLAIM-074; record 66 §2): the reading-list surface's
# read arms.  The listing carries one JSON line per list (the id, the name,
# the DERIVED member count — the count over the current view, never a
# state column), ordered by the list id (the keyset convention every list
# arm rides).  The member arm derives the CURRENT membership: DISTINCT ON
# the source pair with the last-op-wins ORDER, then the op='added' filter —
# the projection over the event rows (RTM §2 item 9), never a second
# store.  The member cursor rides the derived source-id column aliased id
# (the _page_args keyset form).
RLLIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT l.id, l.name, l.created_at, "
              "(SELECT count(*) FROM (SELECT DISTINCT ON (m.source_id) m.source_id, m.op "
              "FROM arv.reading_list_member m WHERE m.list_id = l.id "
              "ORDER BY m.source_id, m.created_at DESC, m.id DESC) c "
              "WHERE c.op = 'added') AS member_count "
              "FROM arv.reading_list l WHERE {after}TRUE ORDER BY l.id LIMIT {limit}) t;")
RLMEM_SQL = ("SELECT row_to_json(t)::text FROM (SELECT c.id AS source_id, c.added_at FROM "
             "(SELECT DISTINCT ON (m.source_id) m.source_id AS id, m.op, "
             "m.created_at AS added_at FROM arv.reading_list_member m "
             "WHERE m.list_id = {id} ORDER BY m.source_id, m.created_at DESC, m.id DESC) c "
             "WHERE c.op = 'added' AND {after}TRUE ORDER BY c.id LIMIT {limit}) t;")
RL_SQL = ("SELECT row_to_json(t)::text FROM (SELECT l.id, l.name, l.created_at FROM "
          "arv.reading_list l WHERE l.id = {id}) t;")
JNL_SQL = ("SELECT row_to_json(t)::text FROM (SELECT j.id, j.revision, j.kind, j.content, "
           "j.source_id, j.actor, j.created_at FROM arv.journal_block j WHERE j.id = {id} "
           "ORDER BY j.revision DESC LIMIT 1) t;")
JNLHIST_SQL = ("SELECT row_to_json(t)::text FROM (SELECT j.id, j.revision, j.kind, j.content, "
               "j.source_id, j.actor, j.created_at FROM arv.journal_block j WHERE j.id = {id} "
               "ORDER BY j.revision) t;")


def _read(db: str, owner: str, sql: str) -> list:
    """One owner-scoped read: the GUC + the SELECT in ONE batch (RLS enforced).
    Row framing is NEWLINE-ONLY (the ANC-10 contract): PostgreSQL emits one
    JSON row per line, and row_to_json escapes control characters below
    U+0020 ONLY — U+2028/U+2029/U+0085 travel raw inside the JSON string, so a
    str.splitlines() reader would split a row on them and corrupt the framing
    (the observed pre-fix crash: JSONDecodeError 'Unterminated string')."""
    q = "'" + owner.replace("'", "''") + "'"
    r = pg.psql(f"SET app.current_owner={q}; {sql}", db=db, user="arv_app")
    if r.returncode != 0:
        print(f"FAIL ARV-QRY-002: the read failed — {r.stderr.strip()}")
        return None
    return [ln for ln in r.out.split("\n") if ln.strip()]


def _refuse(id_: str, family: str = "capture") -> int:
    print(f"FAIL ARV-QRY-001: no such object ({id_}) in the caller's scope — absent and "
          "another owner's are the SAME refusal, never a side channel")
    # P4-00c (the F10 routing): the repair hint names the caller's OWN list
    # arm per family (the pre-P4-00c form said 'capture list' on every arm —
    # byte-frozen then by the template-equality pins, now unified honestly:
    # the pins compare WITHIN one arm, so the per-family wording is free)
    hints = {"capture": "check the id against the caller's own capture list (query.py list-captures)",
             "note": "check the id against the caller's own note list (query.py list-notes)",
             "bookmark": "check the id against the caller's own bookmark list (query.py list-bookmarks)",
             "source": "the id is the import ack's result_ref (query.py get-source reads it back)",
             "anchor": "the anchor id comes from get-capture's anchor_id; resolve-anchor re-resolves it"}
    print(f"      repair: {hints.get(family, hints['capture'])}")
    return 1


def _refuse_tombstoned(id_: str) -> int:
    """P3-04 (RTM §3.3): the typed tombstone refusal on the ordinary read path —
    hidden from retrieval, never erased; the governed history keeps everything."""
    print(f"FAIL ARV-QRY-003: highlight {id_} is tombstoned — hidden from ordinary retrieval "
          "(the governed history at get-history retains every revision and event)")
    print("      repair: query.py get-history for the governed view; commands.py restore_highlight "
          "returns it to ordinary retrieval (the revisions were never touched)")
    return 1


def _refuse_tombstoned_bookmark(id_: str) -> int:
    """P3-05 (RTM §3.3): the typed tombstone refusal on the bookmark read path —
    the same class as the highlight family's ARV-QRY-003."""
    print(f"FAIL ARV-QRY-003: bookmark {id_} is tombstoned — hidden from ordinary retrieval "
          "(the governed history at get-bookmark-history retains every revision and event)")
    print("      repair: query.py get-bookmark-history for the governed view; commands.py "
          "restore_bookmark returns it to ordinary retrieval (the revisions were never touched)")
    return 1


def _refuse_tombstoned_note(id_: str) -> int:
    """P3-06 (RTM §3.3): the typed tombstone refusal on the note read path —
    the same class as the highlight/bookmark families' ARV-QRY-003."""
    print(f"FAIL ARV-QRY-003: note {id_} is tombstoned — hidden from ordinary retrieval "
          "(the governed history at get-note-history retains every revision, reference, "
          "and event)")
    print("      repair: query.py get-note-history for the governed view; commands.py "
          "restore_note returns it to ordinary retrieval (the revisions were never touched)")
    return 1


def _refuse_list_bounds(msg: str) -> int:
    """P4-00b (CLAIM-063): the list contract's bounds — a typed refusal,
    never a silent clamp and never an unbounded dump (the frozen refusal
    shape: exit 1 + the FAIL prefix + zero effect)."""
    print(f"FAIL ARV-QRY-004: {msg}")
    print(f"      repair: --limit within 1..{MAX_LIST_LIMIT} (the default {DEFAULT_LIST_LIMIT}); "
          "--after a listed id of the same family (the keyset cursor — the next page starts "
          "strictly after it)")
    return 1


def _page_args(limit, after, alias: str):
    """P4-00b (CLAIM-063) + P4-C slice one (CLAIM-070; record 62 §2): the
    list contract's boundary validation — ONE home shared by every bounded
    arm (the ids-only _list_arm AND the row-carrying reading-state arm:
    both new P4-C arms ride the SAME typed law, never a second validator
    that could drift): the request bounds are VALIDATED at the boundary
    (the typed ARV-QRY-004, never a clamp, never argparse's usage exit);
    the keyset cursor takes a valid id of the same family.  Returns
    (limit, after_clause) or None when the refusal already printed."""
    import uuid as _u
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        _refuse_list_bounds(f"--limit {limit!r} is not an integer")
        return None
    if limit < 1 or limit > MAX_LIST_LIMIT:
        _refuse_list_bounds(f"--limit {limit} is outside the bounds 1..{MAX_LIST_LIMIT}")
        return None
    after_clause = ""
    if after is not None:
        try:
            after_clause = f"{alias}.id > '{_u.UUID(after)}' AND "
        except (ValueError, AttributeError, TypeError):
            _refuse_list_bounds(f"--after {after!r} is not a valid id (the keyset cursor "
                               "takes a listed id of the same family)")
            return None
    return limit, after_clause


def _list_arm(db: str, owner: str, sql: str, alias: str, limit, after) -> int:
    """P4-00b (CLAIM-063): the bounded, paginated list arm — the frozen
    contract's ONE implementation (list-captures/list-bookmarks/list-notes
    share it; P4-C slice one adds list-library over arv.source): the
    request bounds are VALIDATED at the boundary through _page_args (a
    typed ARV-QRY-004 refusal, never a clamp); the fetch takes limit+1
    rows so the truth marker is OBSERVED, never inferred; the response
    opens with the version header and closes with '# more=true|false' —
    an empty listing answers header + marker ALONE (never pure silence —
    the P4-00a lesson extended to the lists; the empty answer is
    distinguishable from a truncation)."""
    page = _page_args(limit, after, alias)
    if page is None:
        return 1
    limit, after_clause = page
    rows = _read(db, owner, sql.format(after=after_clause, limit=limit + 1))
    if rows is None:
        return 1
    more = len(rows) > limit
    print(f"# api_version={API_VERSION}")
    for ln in rows[:limit]:
        print(json.loads(ln)["id"])
    print(f"# more={'true' if more else 'false'}")
    return 0


def _verdict(db: str, owner: str, anchor_id: str) -> "dict | None":
    """SYS-05's typed resolution AS A VALUE (P3-05: the bookmark read composes
    it with the entity row; resolve-anchor prints it).  Returns the answer
    dict, None when the read itself failed, {} when the anchor is out of
    scope.  The join never crosses Source versions (the anchor binds its OWN
    version; a new edition is a different source row and cannot appear
    here)."""
    q = "'" + anchor_id.replace("'", "''") + "'"
    rows = _read(db, owner, ANC_SQL.format(id=q))
    if rows is None:
        return None
    if not rows:
        return {}
    a = json.loads(rows[0])
    out = {"anchor_id": anchor_id, "source_id": a["source_id"],
           "start_off": a["start_off"], "end_off": a["end_off"]}
    cb, ca = a["context_before"], a["context_after"]
    if not a["generation_id"]:
        out.update(state="unresolved", cause="no-current-generation", evidence_hits=0)
        return out
    if a["input_digest"] != a["source_digest"]:
        out.update(state="unresolved", cause="stale-generation", evidence_hits=0)
        return out
    rows = _read(db, owner, PASS_SQL.format(gid="'" + a["generation_id"] + "'"))
    if rows is None:
        return None
    ps = [json.loads(r) for r in rows]
    view = "".join(p["text"] for p in ps)          # the derived view, ordinal order
    base = ps[0]["start_off"] if ps else 0           # the view's source-anchor
    span = a["end_off"] - a["start_off"]
    cur, covered, ids = a["start_off"], 0, []         # the primary: a contiguous covering
    for p in sorted(ps, key=lambda p: p["start_off"]):
        if p["start_off"] > cur:
            break
        if p["end_off"] <= cur:
            continue
        covered += min(p["end_off"], a["end_off"]) - cur
        cur = p["end_off"]
        ids.append(p["id"])
        if cur >= a["end_off"]:
            break
    rs, re_ = a["start_off"] - base, a["end_off"] - base
    ok_ev = (covered >= span and cur >= a["end_off"]
             and view[max(0, rs - len(cb)):rs] == cb[max(0, len(cb) - rs):]
             and view[re_:min(len(view), re_ + len(ca))] == ca[:max(0, min(len(view), re_ + len(ca)) - re_)])
    if ok_ev:
        out.update(state="resolved", generation_id=a["generation_id"],
                   passage_ids=",".join(ids))
        return out
    hits = 0                                           # the fallback: cb + gap + ca
    for i in range(len(view)):
        j = i + len(cb) + span
        if view.startswith(cb, i) and j + len(ca) <= len(view) and view.startswith(ca, j):
            hits += 1
    if hits >= 2:
        out.update(state="ambiguous", evidence_hits=hits)
    else:
        out.update(state="unresolved", cause="location-unmatched", evidence_hits=hits)
    return out


def _resolve(db: str, owner: str, anchor_id: str) -> int:
    """resolve-anchor (P3-03b): the typed verdict printed — ONE JSON answer
    line at exit 0; ARV-QRY-001 for out-of-scope/absent (the answer is the
    SAME dict _verdict builds + the P4-00b version key — the ANC suite's
    key-level pins hold; the answer stays ONE line)."""
    v = _verdict(db, owner, anchor_id)
    if v is None:
        return 1
    if not v:
        return _refuse(anchor_id, family="anchor")
    _say(_versioned(v))  # P4-00b: the version key rides the resolution ANSWER too
    return 0


# ------------------------------------------------- P4-D slice one: the stable @-reference resolution (RTM §2 item 10)

# the seven landed families, split by the revision dimension exactly as the
# CLAIM-057 substrate's grammar law splits its kinds (the note-reference
# machine's five + the two P4-C families the resolution surface covers):
# bare = the identity IS the version; revisioned = the (id, revision) pair.
_REF_BARE = ("work", "source", "anchor")
_REF_REV = ("highlight", "bookmark", "note", "journal_block")
# \Z (never $): Python's $ ALSO matches just before a trailing newline, so a
# "<uuid>\n" id would pass the grammar and die at the SQL cast as an untyped
# ARV-QRY-002 — the SEV round-1 F-075-2 class; \Z anchors the true end. (The
# substrate's own _UUID_RE shares the $ form — that LANDED boundary's copy is
# routed to the _nte_canon_id pattern's family-wide slice, the F-072-1
# precedent; this new surface repairs its own copy now.)
_REF_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                          r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z")
# per family: the entity table, its lifecycle table (None = the family
# carries no tombstone machine), and the lifecycle's id column
_REF_FAMILY = {"work": ("arv.work", None, None),
               "source": ("arv.source", None, None),
               "highlight": ("arv.highlight", "arv.highlight_lifecycle", "highlight_id"),
               "bookmark": ("arv.bookmark", "arv.bookmark_lifecycle", "bookmark_id"),
               "note": ("arv.note", "arv.note_lifecycle", "note_id"),
               "journal_block": ("arv.journal_block", None, None)}


def _ref_parse(ref: str):
    """P4-D slice one (CLAIM-075; record 67 §2): parse + shape-validate the
    reference string — the CLAIM-057 substrate's grammar composed at the
    RESOLUTION boundary (the same uuid law, the same per-family revision
    dimension), with the pin OPTIONAL here: the WRITE boundary requires the
    pin (a stored reference is exact — version-aware by construction), the
    resolution boundary answers both 'where is the current?' (unpinned) and
    'exactly as pinned, never a retarget' (@rev).  Returns (kind, id,
    rev|None) or the malformed-reason string."""
    kind, sep, rest = ref.partition(":")
    if not sep or kind not in _REF_BARE + _REF_REV:
        return f"the kind {kind!r} is not in the vocabulary {_REF_BARE + _REF_REV}"
    target, at, rev = rest.partition("@")
    if not _REF_UUID_RE.match(target):
        return "the target id is not a UUID"
    if kind in _REF_BARE:
        if at:
            return (f"the {kind} reference must not name a revision — the "
                    f"{kind} identity IS the version (the substrate's own law)")
        return kind, target, None
    r_ = None
    if at:
        # the length bound BEFORE int() (the SEV round-1 F-075-1 class):
        # CPython 3.11+ raises ValueError above the 4300-digit int-str limit,
        # an untyped crash on an all-digits pin — the hostile-string law
        # demands the named refusal; 18 digits is far above any plausible
        # revision and far below the crash boundary
        if len(rev) > 18 or not rev.isdigit() or int(rev) < 1:
            return "the pinned revision must be a plausible revision number (digits, at most 18, >= 1)"
        r_ = int(rev)
    return kind, target, r_


def _ref_refuse_dangling(ref: str) -> int:
    """ARV-REF-001 — the no-oracle at the resolution boundary (the
    substrate's ARV-NTE-003 law carried to the read side): the absent id,
    another owner's id, and a nonexistent target revision on a live target
    are the SAME refusal, byte-equal whatever was asked — never an
    existence side channel."""
    print(f"FAIL ARV-REF-001: the reference {ref!r} does not resolve in the caller's scope — "
          "absent, another owner's, and a nonexistent target revision are the SAME "
          "refusal, never a side channel")
    print("      repair: reference a target from the caller's own library at an existing "
          "revision (query.py list-* / get-*); resolve-reference answers the six states, "
          "never a guess")
    return 1


def _ref_refuse_malformed(ref: str, why: str) -> int:
    """ARV-REF-002 — the closed grammar, never a clamp and never a guess: a
    reference string is DATA, never an instruction (imported hostile strings
    never acquire authority by being read; the repr echo is framing-safe —
    control characters stay escaped, the one-line refusal law holds)."""
    print(f"FAIL ARV-REF-002: the reference {ref!r} is malformed — {why}")
    print("      repair: supply kind:id[@rev] with kind in "
          "work/source/anchor/highlight/bookmark/note/journal_block; "
          "highlight|bookmark|note|journal_block may pin @rev (a plausible "
          "revision number: digits, at most 18, >= 1); "
          "work|source|anchor never name a revision")
    return 1


def _resolve_reference(db: str, owner: str, ref: str) -> int:
    """resolve-reference (P4-D slice one; CLAIM-075, record 67 §2): the
    typed SIX-STATE resolution — ONE JSON answer line at exit 0 (an answer,
    never a failure); ARV-REF-001 the no-oracle dangling refusal;
    ARV-REF-002 the malformed grammar.  THE PRECEDENCE: the governed purge
    (the 0013 permanence record — RLS scopes the ledger to the caller)
    WINS over every state; the tombstone parity beats the revision
    resolution (a pin never bypasses a tombstone); the anchor family
    composes the P3-03b machinery's typed verdict VERBATIM (resolved ->
    current + the serving generation_id, unresolved -> unavailable + the
    named cause, ambiguous -> ambiguous + the hit count).  The revisioned
    families read max-revision / pin-existence / parity from ONE statement
    (subselects — one snapshot, the #91 read-path law); the unpinned form
    answers current at the DERIVED max revision; the pinned form serves
    EXACTLY as pinned (historical names the current alongside — never a
    silent retarget)."""
    parsed = _ref_parse(ref)
    if isinstance(parsed, str):
        return _ref_refuse_malformed(ref, parsed)
    kind, tid, rev = parsed
    qid = "'" + tid.replace("'", "''") + "'"
    # the precedence's first law: the governed purge invalidates the access
    rows = _read(db, owner, f"SELECT count(*) FROM arv.purge_ledger "
                            f"WHERE kind='{kind}' AND entity_id={qid};")
    if rows is None:
        return 1
    if rows and int(rows[0]) > 0:
        _say(_versioned({"kind": kind, "id": tid, "state": "purged"}))
        return 0
    if kind == "anchor":
        v = _verdict(db, owner, tid)   # the P3-03b machinery composed, never re-implemented
        if v is None:
            return 1
        if not v:
            return _ref_refuse_dangling(ref)
        if v["state"] == "resolved":
            _say(_versioned({"kind": "anchor", "id": tid, "state": "current",
                             "resolved_ref": f"anchor:{tid}",
                             "generation_id": v["generation_id"]}))
        elif v["state"] == "ambiguous":
            _say(_versioned({"kind": "anchor", "id": tid, "state": "ambiguous",
                             "evidence_hits": v["evidence_hits"]}))
        else:
            _say(_versioned({"kind": "anchor", "id": tid, "state": "unavailable",
                             "cause": v["cause"]}))
        return 0
    table, life, lcol = _REF_FAMILY[kind]
    if kind in _REF_BARE:
        rows = _read(db, owner, f"SELECT count(*) FROM {table} WHERE id={qid};")
        if rows is None:
            return 1
        if not rows or int(rows[0]) == 0:
            return _ref_refuse_dangling(ref)
        _say(_versioned({"kind": kind, "id": tid, "state": "current",
                         "resolved_ref": f"{kind}:{tid}"}))
        return 0
    pin = (f"COALESCE((SELECT count(*) FROM {table} WHERE id={qid} AND "
           f"revision={rev if rev is not None else 0}), 0)")
    mx = f"COALESCE((SELECT max(revision) FROM {table} WHERE id={qid}), 0)"
    sql = f"SELECT {mx} || '|' || {pin}"
    if life:
        sql += (f" || '|' || COALESCE((SELECT count(*) FILTER (WHERE event = 'tombstone') > "
                f"count(*) FILTER (WHERE event = 'restore') FROM {life} "
                f"WHERE {lcol}={qid}), false)")
    rows = _read(db, owner, sql + ";")
    if rows is None:
        return 1
    parts = rows[0].split("|")
    cur_rev, pinned = int(parts[0]), int(parts[1])
    tomb = len(parts) > 2 and parts[2] == "true"
    if cur_rev == 0:
        return _ref_refuse_dangling(ref)
    if tomb:
        _say(_versioned({"kind": kind, "id": tid, "state": "tombstoned"}))
        return 0
    if rev is None:
        _say(_versioned({"kind": kind, "id": tid, "state": "current",
                         "resolved_ref": f"{kind}:{tid}@{cur_rev}",
                         "revision": cur_rev}))
        return 0
    if pinned == 0:
        return _ref_refuse_dangling(ref)   # the live target's pinned revision is absent: the same class
    if rev == cur_rev:
        _say(_versioned({"kind": kind, "id": tid, "state": "current",
                         "resolved_ref": f"{kind}:{tid}@{rev}", "revision": rev}))
    else:
        _say(_versioned({"kind": kind, "id": tid, "state": "historical",
                         "resolved_ref": f"{kind}:{tid}@{rev}",
                         "pinned_revision": rev, "current_revision": cur_rev}))
    return 0


def _get_bookmark(db: str, owner: str, bm_id: str) -> int:
    """P3-05's ACCEPTANCE arm (RTM §2.5 item 6): return to the saved location
    or report the typed unresolved-anchor state — the entity row composed
    with SYS-05's typed verdict over its CURRENT revision's anchor, NEVER a
    silent retarget (the answer's offsets are the anchor's own, whatever the
    derived view did; the anchor row is immutable).  A typed state is an
    ANSWER at exit 0; ARV-QRY-001/003 are the named refusals."""
    qid = "'" + bm_id.replace("'", "''") + "'"
    rows = _read(db, owner, BMSTATE_SQL.format(id=qid))
    if rows is None:
        return 1
    t_n, r_n = (int(x) for x in rows[0].split("|"))
    if t_n > r_n:
        return _refuse_tombstoned_bookmark(bm_id)
    rows = _read(db, owner, BM_SQL.format(id=qid))
    if rows is None:
        return 1
    if not rows:
        return _refuse(bm_id, family="bookmark")
    b = json.loads(rows[0])
    v = _verdict(db, owner, b["anchor_id"])
    if v is None:
        return 1
    if not v:
        return _refuse(bm_id, family="bookmark")   # the anchor row vanished under the entity: the honest refusal, never a guess
    out = {"bookmark_id": b["bookmark_id"], "revision": b["revision"]}
    out.update(v)
    # P4-00b: the version key at the SAME print boundary as every other read
    # body (the _versioned form — the uniform placement, SEV round-1 F7 note)
    print(json.dumps(_versioned(out), ensure_ascii=False))
    return 0


def _position_row(pos: str, cur: str, source_id: str) -> dict:
    """P4-C slice one (CLAIM-070; record 62 §2): the position answer's ONE
    construction home — get-position AND the reading-state arm build the
    SAME row (the no-second-path law made STRUCTURAL: one builder, never
    two implementations that could drift).  An empty pos means NEVER SAVED
    (the typed no_position_saved ANSWER — a state, never a failure, the
    capability-measure precedent); otherwise the saved row + the
    serving-generation binding (saved_generation_id byte-stable across a
    re-extraction, current_generation_id the serving one now, the derived
    generation_matches flag — never a silent retarget).  Every row carries
    the version key (P4-00b)."""
    if not pos:
        return _versioned({"state": "no_position_saved", "source_id": source_id})
    p = json.loads(pos)
    return _versioned({"state": "saved", "source_id": source_id,
                       "save_ordinal": p["save_ordinal"], "start_off": p["start_off"],
                       "end_off": p["end_off"], "saved_generation_id": p["saved_generation_id"],
                       "current_generation_id": cur,
                       "generation_matches": bool(cur) and p["saved_generation_id"] == cur})


def _get_position(db: str, owner: str, source_id: str) -> int:
    """P4-A slice two (CLAIM-066; record 58 §2): the reading-position read
    arm — the reopen half of the save->reopen->return round-trip.  ONE
    statement, ONE snapshot carries the source existence, the last-saved
    position, and the current generation (the #91 round-3 class: no two-read
    race between the existence probe and the payload fetch).  THE
    NO-ORACLE: an absent source and another owner's are the SAME refusal as
    get-source's — the shared _refuse form, family="source", byte-equal on
    the same id (never a leak that a position exists).  THE
    SERVING-GENERATION BINDING: the answer names saved_generation_id (the
    generation the reader was reading — byte-stable across a re-extraction)
    AND current_generation_id (the serving one now) AND the derived
    generation_matches flag — never a silent retarget (the offsets are the
    saved row's own, whatever the derived view did).  An in-scope source
    NEVER SAVED is a typed ANSWER at exit 0 (a state, never a failure — the
    capability-measure precedent), carrying the version key."""
    qid = "'" + source_id.replace("'", "''") + "'"
    rows = _read(db, owner, POS_SQL.format(id=qid))
    if rows is None:
        return 1
    if not rows:
        return _refuse(source_id, family="source")
    pos, cur = rows[0].split("|", 1)
    print(json.dumps(_position_row(pos, cur, source_id), ensure_ascii=False))
    return 0


def _reading_state(db: str, owner: str, limit, after) -> int:
    """P4-C slice one (CLAIM-070; record 62 §2): the current-reading state —
    ONE read arm deriving the owner's reading surface from the LANDED
    position rows: every source of the keyset page carries its last-saved
    position + the generation binding, or the honest no_position_saved
    state (the not-yet-open sources are PART of the answer, never silence).
    THE NO-SECOND-PATH LAW: the rows ride _position_row — the SAME builder
    get-position uses, so the derived view can never drift from the arm it
    derives from (every row equals get-position's own answer for that
    source).  Bounded + paginated on the P4-00b contract through
    _page_args (the typed ARV-QRY-004 at the boundary, never a clamp); the
    limit+1 fetch OBSERVES the truth marker; an empty surface answers
    header + more=false ALONE (never pure silence — the P4-00a lesson).
    The view is DERIVED live at every invocation (no materialized copy, no
    second position store — the no-new-table law)."""
    page = _page_args(limit, after, "s")
    if page is None:
        return 1
    limit, after_clause = page
    rows = _read(db, owner, READING_SQL.format(after=after_clause, limit=limit + 1))
    if rows is None:
        return 1
    more = len(rows) > limit
    print(f"# api_version={API_VERSION}")
    for ln in rows[:limit]:
        sid, pos, cur = ln.split("|", 2)
        print(json.dumps(_position_row(pos, cur, sid), ensure_ascii=False))
    print(f"# more={'true' if more else 'false'}")
    return 0


def _session_events(db: str, owner: str, limit, after) -> int:
    """P4-C slice two (CLAIM-071; record 63 §2): the session/dwell event
    listing — the owner's behavior-event stream (D-010's durable behavior
    data), one JSON row per event: the recorded kind (the closed
    vocabulary), the coarse span, the coarse dwell (dwell events only), the
    serving-generation binding AS WRITTEN at event time (the behavior
    history is provenance — never retargeted by a later re-extraction), the
    ordinal, the timestamp.  Bounded + paginated on the P4-00b contract
    through _page_args (the typed ARV-QRY-004 at the boundary, never a
    clamp); the limit+1 fetch OBSERVES the truth marker; the empty stream
    answers header + more=false ALONE (never pure silence — the P4-00a
    lesson).  Every row carries the version key (P4-00b)."""
    page = _page_args(limit, after, "e")
    if page is None:
        return 1
    limit, after_clause = page
    rows = _read(db, owner, SESLIST_SQL.format(after=after_clause, limit=limit + 1))
    if rows is None:
        return 1
    more = len(rows) > limit
    print(f"# api_version={API_VERSION}")
    for ln in rows[:limit]:
        print(json.dumps(_versioned(json.loads(ln)), ensure_ascii=False))
    print(f"# more={'true' if more else 'false'}")
    return 0


def _versioned(obj: dict) -> dict:
    """P4-00b (CLAIM-063): the version key injected at the READ print
    boundary — every JSON body and every history row carries
    "api_version": the same value every write ack names. The SQL stays
    byte-identical (the injection is ONE pattern at one boundary, never a
    per-query rewrite); the re-serialization preserves the parsed key order
    and the newline-only framing law (ensure_ascii=False — U+2028/U+2029
    travel raw, exactly as row_to_json emitted them)."""
    out = dict(obj)
    out["api_version"] = API_VERSION
    return out


def _jline_safe(obj: dict) -> str:
    """P4-C slice three (CLAIM-072; record 64 §2): the journal read rows'
    LINE-SAFE serialization — the writing lab's content is the LONG raw
    thinking, and its framing-law characters include U+2028/U+2029 (the
    line separators) which json.dumps(ensure_ascii=False) emits RAW.  A
    raw U+2028 inside an emitted row would split under any
    splitlines()-class reader (JavaScript's own JSON line hazard), breaking
    the one-JSON-line-per-row framing the whole read surface rides.  The
    journal arms therefore emit those three characters (U+0085 NEL
    included — the same splitlines() class) in the JSON six-character
    \\uXXXX escape form: the PARSED value is byte-identical (json.loads
    decodes the escape to the same character), and the line boundaries
    stay exactly \\n — the ANC-10 newline-only law held honestly at the
    class boundary, not just the \\n case.  The OTHER read arms' bytes are
    frozen by their own suites and are NOT touched (one family, one
    boundary; the escape is the journal's own, where the long raw thinking
    is the product)."""
    return (json.dumps(obj, ensure_ascii=False)
            .replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029")
            .replace("\u0085", "\\u0085"))


def _refuse_journal() -> int:
    """P4-C slice three (CLAIM-072): the journal read boundary's no-oracle —
    absent and another owner's are the SAME refusal (RTM §2.10 on the read
    path).  The journal form names NO id: the refusal bytes stay equal
    WHATEVER id was asked (absent, another owner's, malformed — the block
    id is free-form input on this arm, and nothing about the request echoes
    back), the strongest form of the no-oracle the family carries."""
    print("FAIL ARV-QRY-001: no such journal block in the caller's scope — absent and "
          "another owner's are the SAME refusal, never a side channel")
    print("      repair: check the id against the caller's own journal listing "
          "(query.py list-journal)")
    return 1


def _get_journal(db: str, owner: str, id_: str) -> int:
    """P4-C slice three (CLAIM-072; record 64 §2): the single-block read —
    the lossless round-trip's read half.  ONE statement, ONE snapshot
    carries the current revision (ORDER BY revision DESC LIMIT 1 — the row
    the last write authored under the append-only law; the #91 round-3
    class: no two-read race between the existence probe and the payload
    fetch).  THE NO-ORACLE: an absent block and another owner's are the
    SAME refusal — the journal's no-id-echo form, byte-equal whatever was
    asked.  The content arrives WHOLE (the LONG raw thinking, never a
    truncated form) and rides _jline_safe (the U+2028-class escape — the
    line boundaries stay exactly \\n)."""
    qid = "'" + id_.replace("'", "''") + "'"
    rows = _read(db, owner, JNL_SQL.format(id=qid))
    if rows is None:
        return 1
    if not rows:
        return _refuse_journal()
    print(_jline_safe(_versioned(json.loads(rows[0]))))
    return 0


def _journal_history(db: str, owner: str, id_: str) -> int:
    """P4-C slice three (CLAIM-072; record 64 §2): the governed history —
    EVERY revision of one block, in order, one JSON line per row (the
    export-ready form: the current view rebuilds from history ALONE).  The
    same no-oracle as the ordinary read (absent and another owner's the
    SAME refusal); every row carries the version key (P4-00b) and rides
    _jline_safe (the framing-law characters stay inside their row)."""
    qid = "'" + id_.replace("'", "''") + "'"
    rows = _read(db, owner, JNLHIST_SQL.format(id=qid))
    if rows is None:
        return 1
    if not rows:
        return _refuse_journal()
    for ln in rows:
        print(_jline_safe(_versioned(json.loads(ln))))
    return 0


def _refuse_reading_list() -> int:
    """P4-C slice five (CLAIM-074): the reading-list read boundary's
    no-oracle — absent and another owner's are the SAME refusal (RTM
    §2.10 on the read path).  The journal family's no-id-echo form: the
    refusal bytes stay equal WHATEVER id was asked, the strongest form of
    the no-oracle (the F-072-1 malformed-id class stays routed family-wide
    — the shared _nte_canon_id pattern's own slice)."""
    print("FAIL ARV-QRY-001: no such reading list in the caller's scope — absent and "
          "another owner's are the SAME refusal, never a side channel")
    print("      repair: check the id against the caller's own list-lists answer "
          "(query.py list-lists)")
    return 1


def _lists(db: str, owner: str, limit, after) -> int:
    """P4-C slice five (CLAIM-074; record 66 §2): the owner's lists — one
    JSON line per list (the id, the name, the DERIVED member count over
    the current view, the created_at), bounded + paginated on the P4-00b
    contract through _page_args (the typed ARV-QRY-004 at the boundary,
    never a clamp); the limit+1 fetch OBSERVES the truth marker; the empty
    surface answers header + more=false ALONE (never pure silence).  NO
    name uniqueness is implied or enforced — the identity is the uuid
    (Q11's baseline); two lists may share one name and BOTH appear."""
    page = _page_args(limit, after, "l")
    if page is None:
        return 1
    limit, after_clause = page
    rows = _read(db, owner, RLLIST_SQL.format(after=after_clause, limit=limit + 1))
    if rows is None:
        return 1
    more = len(rows) > limit
    print(f"# api_version={API_VERSION}")
    for ln in rows[:limit]:
        print(json.dumps(_versioned(json.loads(ln)), ensure_ascii=False))
    print(f"# more={'true' if more else 'false'}")
    return 0


def _get_list(db: str, owner: str, id_: str, limit, after) -> int:
    """P4-C slice five (CLAIM-074; record 66 §2): one list's CURRENT
    membership — the DERIVED view (DISTINCT ON the source pair, the last
    op wins, then the op='added' filter), one JSON line per active member
    (the source id + the added_at), bounded + paginated on the same list
    contract (the member cursor rides the derived source-id column).  The
    header read and the member page are the list arm's OWN reads — the
    membership derives live at every invocation (no materialized copy, no
    second store).  THE NO-ORACLE: an absent list and another owner's are
    the SAME refusal (the no-id-echo form, byte-equal whatever was
    asked).  The empty list answers header + more=false ALONE."""
    qid = "'" + id_.replace("'", "''") + "'"
    rows = _read(db, owner, RL_SQL.format(id=qid))
    if rows is None:
        return 1
    if not rows:
        return _refuse_reading_list()
    page = _page_args(limit, after, "c")
    if page is None:
        return 1
    limit, after_clause = page
    mrows = _read(db, owner, RLMEM_SQL.format(id=qid, after=after_clause,
                                              limit=limit + 1))
    if mrows is None:
        return 1
    more = len(mrows) > limit
    print(f"# api_version={API_VERSION}")
    for ln in mrows[:limit]:
        print(json.dumps(_versioned(json.loads(ln)), ensure_ascii=False))
    print(f"# more={'true' if more else 'false'}")
    return 0


def _say(out: dict, **kw) -> None:
    out.update(kw)
    print(json.dumps(out, ensure_ascii=False))


# ------------------------------------------------- P4-E slice one: the scoped agent read mode (CLAIM-077; record 69 §2)

def _agent_resolve(db: str, token: str):
    """The credential resolution: the sha256 -> the narrow SECURITY DEFINER
    lookup (arv.agent_token_lookup — the system's own authentication
    primitive, exposing ONLY the live 'read'-scoped credential's owner scope;
    never an agent-reachable arbitrary read) -> (owner_scope, credential_id).
    ARV-AGT-001 — the no-oracle invalid-token class: unknown, revoked, and
    scope-missing are the SAME refusal, and the TOKEN IS NEVER ECHOED (it is
    a secret — the refusal names the class, never the credential, never the
    scope, never the value)."""
    h = hashlib.sha256(token.encode("utf-8")).hexdigest()
    qh = "'" + h.replace("'", "''") + "'"
    rows = _read(db, "_agent_lookup",
                 f"SELECT owner_scope || '|' || credential_id::text FROM "
                 f"arv.agent_token_lookup({qh});")
    if rows is None:
        return None
    if not rows:
        print("FAIL ARV-AGT-001: the credential does not grant access — unknown, "
              "revoked, and scope-missing are the SAME refusal, never a side channel "
              "(the token is never echoed: it is a secret)")
        print("      repair: use a live credential's token value exactly as "
              "displayed at its mint; mint a new credential if the old was revoked "
              "(the owner's revocation is final)")
        return None
    owner, cid = rows[0].split("|")
    return owner, cid


def _agent_audit(db: str, owner: str, cred_id: str, arm: str, limit, after) -> int:
    """The audit row for one SERVED agent read: the credential + the arm + the
    bounded REQUEST facts (the page limit and the keyset cursor as requested),
    NEVER the content (a read log that stored what was read would be a second
    copy of the library — the structural no-content law). Append-only at the
    substrate (the 0019 immutable trigger); RLS-scoped to the credential's own
    owner. A failure here is LOUD (exit 1 after the served read): an unaudited
    agent read is a contract violation, never a silent pass."""
    qlim = "NULL" if limit is None else str(int(limit))
    qaft = "NULL" if after is None else "'" + str(after).replace("'", "''") + "'"
    qid = "'" + str(cred_id).replace("'", "''") + "'"
    # F2-077-5 (the SEV round-2 repair): the owner travels ESCAPED — the
    # file's own convention (_read's owner.replace), never raw interpolation
    # (a quote-bearing owner's served read left unaudited, observed live by
    # the round-2 reviewer)
    qown = "'" + owner.replace("'", "''") + "'"
    r = pg.psql(f"SET app.current_owner={qown}; INSERT INTO arv.agent_read_log "
                f"(id, credential_id, owner_scope, arm, req_limit, req_after, "
                f"created_at) VALUES (gen_random_uuid(), {qid}, "
                f"{qown}, '{arm}', {qlim}, {qaft}, now());", db=db, user="arv_app")
    if r.returncode != 0:
        print(f"FAIL ARV-AGT-005: the agent read was served but the audit row "
              f"refused — {r.stderr.strip()[:200]} (an unaudited agent read is a "
              "contract violation, never a silent pass)")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the authenticated retrieval surface (P3-01)")
    sub = ap.add_subparsers(dest="what", required=True)
    for name in ("get-capture", "get-source", "get-history"):
        p = sub.add_parser(name)
        p.add_argument("--owner", default=None)
        p.add_argument("--id", required=True)
    for name in ("get-bookmark", "get-bookmark-history"):
        p = sub.add_parser(name)
        p.add_argument("--owner", default=None)
        p.add_argument("--id", required=True)
    for name in ("get-note", "get-note-history", "get-journal", "get-journal-history"):
        p = sub.add_parser(name)
        p.add_argument("--owner", default=None)
        p.add_argument("--id", required=True)
    # P4-C slice five (CLAIM-074): the member page rides the same list
    # contract as the listing (bounded + the keyset cursor)
    p = sub.add_parser("get-list")
    p.add_argument("--owner", default=None)
    p.add_argument("--id", required=True)
    p.add_argument("--limit", default=str(DEFAULT_LIST_LIMIT),
                   help=f"the member page size (bounds 1..{MAX_LIST_LIMIT}, default {DEFAULT_LIST_LIMIT}) — "
                        "a non-integer refuses with the typed ARV-QRY-004, never argparse's usage exit")
    p.add_argument("--after", default=None, metavar="ID",
                   help="the keyset cursor — the next page starts strictly after this listed source id")
    for name in ("list-captures", "list-bookmarks", "list-notes", "list-library",
                 "get-reading-state", "list-session-events", "list-journal",
                 "list-lists"):
        p = sub.add_parser(name)
        p.add_argument("--owner", default=None)
        # P4-00b: the list contract — the bounded page + the keyset cursor
        # (P4-C slice one: the same contract rides list-library +
        # get-reading-state — every list-shaped response is bounded)
        p.add_argument("--limit", default=str(DEFAULT_LIST_LIMIT),
                       help=f"the page size (bounds 1..{MAX_LIST_LIMIT}, default {DEFAULT_LIST_LIMIT}) — "
                            "a non-integer refuses with the typed ARV-QRY-004, never argparse's usage exit")
        p.add_argument("--after", default=None, metavar="ID",
                       help="the keyset cursor — the next page starts strictly after this listed id")
    p = sub.add_parser("get-position")
    p.add_argument("--owner", default=None)
    p.add_argument("--source", required=True,
                   help="the source id (the import ack's result_ref) whose last-saved reading "
                        "position the reopen returns")
    p = sub.add_parser("resolve-anchor")
    p.add_argument("--owner", default=None)
    p.add_argument("--id", required=True)
    # P4-D slice one (CLAIM-075): the stable @-reference resolution — the
    # six-state typed answer over the seven landed families
    p = sub.add_parser("resolve-reference")
    p.add_argument("--owner", default=None)
    p.add_argument("--ref", required=True, metavar="KIND:ID[@REV]",
                   help="the reference to resolve: work/source/anchor bare; "
                        "highlight/bookmark/note/journal_block optionally "
                        "pinned @rev (the pinned form serves exactly as pinned)")
    p = sub.add_parser("search")
    p.add_argument("--owner", default=None)
    p.add_argument("terms", nargs="+", help="the keyword terms (AND semantics — every term must hit the document)")
    # P4-E slice one (CLAIM-077): the scoped agent read mode — --agent-token
    # REPLACES --owner (exactly one of the two, never both, never neither)
    for _p in sub.choices.values():
        _p.add_argument("--agent-token", default=None, metavar="VALUE",
                        help="the scoped agent credential (P4-E): REPLACES --owner — "
                             "the owner scope comes from the credential, never the "
                             "caller's claim; READ-ONLY (no write command accepts it)")
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    # P4-E slice two (CLAIM-078): the env token channel — ARIVO_AGENT_TOKEN as
    # the NON-ARGV token form (the MCP wrapper's natural home; the
    # argv-visible residual's named home). The identity law extends to EXACTLY
    # ONE of --owner / --agent-token / ARIVO_AGENT_TOKEN: the two token
    # channels together is the SAME ambiguous refusal (never a silent
    # preference between channels; the value is never echoed — it is a secret).
    _env_tok = os.environ.get("ARIVO_AGENT_TOKEN")
    if getattr(a, "agent_token", None) is not None and _env_tok is not None:
        print("FAIL ARV-AGT-002: the ambiguous identity — the --agent-token "
              "argument and the ARIVO_AGENT_TOKEN environment together (never "
              "a silent preference between the two token channels; pass the "
              "token exactly once, never both)")
        print("      repair: pass the token through exactly one channel — "
              "either the --agent-token argument or the ARIVO_AGENT_TOKEN "
              "environment (the wrapper's channel)")
        return 1
    if getattr(a, "agent_token", None) is None and _env_tok is not None:
        a.agent_token = _env_tok  # the SAME downstream path as the argv form
    agent_ctx = None
    if getattr(a, "agent_token", None) is not None:
        if a.owner is not None:
            print("FAIL ARV-AGT-002: the ambiguous identity — --owner and "
                  "--agent-token together (never a silent preference between the "
                  "caller's claim and the credential's binding; the credential's "
                  "scope wins NOTHING here, the refusal is the answer; the token "
                  "channel is the argv form or ARIVO_AGENT_TOKEN)")
            print("      repair: pass exactly one of --owner (the owner's own "
                  "read) or --agent-token (the scoped agent read)")
            return 1
        resolved = _agent_resolve(db, a.agent_token)
        if resolved is None:
            return 1
        a.owner, _cred_id = resolved
        agent_ctx = (_cred_id, a.what, getattr(a, "limit", None),
                     getattr(a, "after", None))
    elif a.owner is None:
        print("FAIL ARV-AGT-002: the missing identity — neither --owner nor "
              "--agent-token nor the ARIVO_AGENT_TOKEN environment (every read "
              "is scoped: the owner's own name or the credential's binding, "
              "never an unscoped query)")
        print("      repair: pass exactly one of --owner (the owner's own "
              "read), --agent-token (the scoped agent read), or "
              "ARIVO_AGENT_TOKEN (the wrapper's channel)")
        return 1
    rc = _dispatch(a, db)
    if agent_ctx is not None and rc == 0:
        if _agent_audit(db, a.owner, agent_ctx[0], agent_ctx[1],
                        agent_ctx[2], agent_ctx[3]) != 0:
            return 1
    return rc


def _dispatch(a, db) -> int:
    if a.what == "resolve-anchor":
        return _resolve(db, a.owner, a.id)
    if a.what == "resolve-reference":
        return _resolve_reference(db, a.owner, a.ref)
    if a.what == "search":
        # P3-07: the keyword search — case-folded whole-token terms, the
        # multi-term AND intersection, the tombstone parity joined at query
        # time (the index never governs visibility), RLS the owner boundary
        terms_u = sorted({tm.casefold() for tm in a.terms})  # deduplicated (a repeated term is one term)
        qterms = ", ".join("'" + tm.replace("'", "''") + "'" for tm in terms_u)
        rows = _read(db, a.owner, SEARCH_SQL.format(terms="ARRAY[" + qterms + "]",
                                                    nterms=len(terms_u)))
        if rows is None:
            return 1
        # P4-00a (CLAIM-062) + P4-00b (CLAIM-063): the labeled, versioned form —
        # the header names the api_version AND the columns before the rows
        # (the acceptance run's 'unlabeled search output' finding; the row
        # shape itself unchanged)
        print(f"# api_version={API_VERSION} kind|entity_id|revision|matched_terms")
        for ln in rows:
            print(ln)
        return 0
    if a.what == "get-note":
        # P3-06 (RTM §3.3): the ordinary read refuses tombstoned ids with the
        # typed code; the governed history keeps them addressable — the state
        # decision and the content fetch share ONE statement, ONE snapshot
        # (the #91 round-3 repair: the two-read form raced a committing
        # tombstone and returned the tombstoned note's content; no lock is
        # added to ordinary readers — the snapshot closes the race)
        qid = "'" + a.id.replace("'", "''") + "'"
        rows = _read(db, a.owner, NOTE_SQL.format(id=qid))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id, family="note")
        flag, payload = rows[0].split("|", 1)
        if flag == "true":
            return _refuse_tombstoned_note(a.id)
        print(json.dumps(_versioned(json.loads(payload)), ensure_ascii=False))
        return 0
    if a.what == "get-note-history":
        # the governed history (P3-06): every revision + every lifecycle
        # event — one JSON line per row, each carrying the version key
        # (the framing law; the _versioned injection at the print boundary)
        rows = _read(db, a.owner, NOTEHIST_SQL.format(id="'" + a.id.replace("'", "''") + "'"))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id, family="note")
        for ln in rows:
            print(json.dumps(_versioned(json.loads(ln)), ensure_ascii=False))
        return 0
    if a.what == "list-notes":
        return _list_arm(db, a.owner, NOTELIST_SQL, "n", a.limit, a.after)
    if a.what == "get-bookmark":
        return _get_bookmark(db, a.owner, a.id)
    if a.what == "get-bookmark-history":
        # the governed history (P3-05): every revision + every lifecycle event —
        # one JSON line per row, each carrying the version key (the framing law;
        # the _versioned injection at the print boundary)
        rows = _read(db, a.owner, BMHIST_SQL.format(id="'" + a.id.replace("'", "''") + "'"))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id, family="bookmark")
        for ln in rows:
            print(json.dumps(_versioned(json.loads(ln)), ensure_ascii=False))
        return 0
    if a.what == "list-bookmarks":
        return _list_arm(db, a.owner, BMLIST_SQL, "b", a.limit, a.after)
    if a.what == "list-captures":
        return _list_arm(db, a.owner, LIST_SQL, "h", a.limit, a.after)
    if a.what == "get-history":
        # the governed history (P3-04): every revision + every lifecycle event —
        # one JSON line per row, each carrying the version key (the framing law;
        # the _versioned injection at the print boundary)
        rows = _read(db, a.owner, HIST_SQL.format(id="'" + a.id.replace("'", "''") + "'"))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id)
        for ln in rows:
            print(json.dumps(_versioned(json.loads(ln)), ensure_ascii=False))
        return 0
    if a.what == "get-capture":
        # P3-04 (RTM §3.3): the ordinary read refuses tombstoned ids with the
        # typed code; the governed history keeps them addressable
        qid = "'" + a.id.replace("'", "''") + "'"
        rows = _read(db, a.owner, STATE_SQL.format(id=qid))
        if rows is None:
            return 1
        t_n, r_n = (int(x) for x in rows[0].split("|"))
        if t_n > r_n:
            return _refuse_tombstoned(a.id)
        rows = _read(db, a.owner, CAP_SQL.format(id=qid))
        if rows is None:
            return 1
        if not rows:
            return _refuse(a.id)
        print(json.dumps(_versioned(json.loads(rows[0])), ensure_ascii=False))
        return 0
    if a.what == "get-position":
        # P4-A slice two (CLAIM-066): the position read arm — the reopen
        return _get_position(db, a.owner, a.source)
    if a.what == "list-library":
        # P4-C slice one (CLAIM-070): the library membership list — the
        # owner's imported sources on the P4-00b list contract
        return _list_arm(db, a.owner, SRCLIST_SQL, "s", a.limit, a.after)
    if a.what == "get-reading-state":
        # P4-C slice one (CLAIM-070): the current-reading state — the
        # derived reading surface over the landed position rows
        return _reading_state(db, a.owner, a.limit, a.after)
    if a.what == "list-session-events":
        # P4-C slice two (CLAIM-071): the session/dwell event listing — the
        # owner's behavior-event stream on the P4-00b list contract
        return _session_events(db, a.owner, a.limit, a.after)
    if a.what == "get-journal":
        # P4-C slice three (CLAIM-072): the single-block read — the current
        # revision, the lossless round-trip's read half
        return _get_journal(db, a.owner, a.id)
    if a.what == "get-journal-history":
        # P4-C slice three (CLAIM-072): the governed history — every
        # revision in order
        return _journal_history(db, a.owner, a.id)
    if a.what == "list-journal":
        # P4-C slice three (CLAIM-072): the journal listing — the owner's
        # blocks on the P4-00b list contract
        return _list_arm(db, a.owner, JNLLIST_SQL, "j", a.limit, a.after)
    if a.what == "list-lists":
        # P4-C slice five (CLAIM-074): the reading-list listing — the owner's
        # lists, one JSON line per list with the derived member count
        return _lists(db, a.owner, a.limit, a.after)
    if a.what == "get-list":
        # P4-C slice five (CLAIM-074): one list's CURRENT membership — the
        # derived view over the membership event rows
        return _get_list(db, a.owner, a.id, a.limit, a.after)
    sql = SRC_SQL
    rows = _read(db, a.owner, sql.format(id="'" + a.id.replace("'", "''") + "'"))
    if rows is None:
        return 1
    if not rows:
        return _refuse(a.id, family="source")
    print(json.dumps(_versioned(json.loads(rows[0])), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
