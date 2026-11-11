#!/usr/bin/env python3
"""harness/capability.py — P4-00c: the format capability matrix + extraction
readiness (CLAIM-064; PLAN's elaborated P4-00c card; RTM §7.3/Q8's boundary
respected — the synthetic-corpus class, never a real-document stability
claim).

WHAT THIS MODULE IS: the user-visible declaration of what the system can do
with a format — DECLARED (the matrix), MEASURED (the per-source readiness
row, derived at the real boundary, never asserted), and RESERVED (the named
surfaces that later phases own). Three verbs:

  matrix               the declared per-format capability rows (one JSON line
                       per format) — the vocabulary: native_text / scan_ocr /
                       layout (reflow|fixed) / extraction (supported|unsupported)
                       / approved
  surfaces             the reserved-surface registry (the named surfaces with
                       their owning phase — the read-position reservation)
  measure --owner --source
                       the MEASURED row for one source: the extraction
                       readiness state + the generation's own facts (the
                       passage count, the coverage fraction, the generation id
                       + ordinal + extractor), derived from the owner-scoped
                       reads + the blob — never a hard-coded row

THE READINESS VOCABULARY (typed answers at exit 0, never a silent miss):
  ready           a current generation exists and its input digest binds
  not_extracted   the source is imported, no generation ever built
  building        an extraction is in flight (the crash-persisted staging row)
  failed          the last attempt failed (the named reason is in the row)
  stale           the generation's input digest no longer binds the source
                  (derived honestly; structurally unreachable today — the
                  source row is immutable — and disclosed as such)
Absent and another owner's source are the SAME refusal (ARV-QRY-001), never
a side channel (the P4-00b no-oracle pattern extended to this surface).

Every output carries api_version (the frozen client contract — P4-00b).
Exit 0 = a row or a typed readiness ANSWER; exit 1 = the named refusal.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import blob  # noqa: E402
from harness.commands import API_VERSION  # noqa: E402  # the version's ONE home
from harness.formats import ADAPTERS, _FmtRefusal, read_text  # noqa: E402  # P4-A slice one: the matrix DERIVES from the adapter registry (formats.py) — ONE home: the adapter declares, the matrix reports; P4-A slice three (CLAIM-067): read_text — the coverage's text domain is the DERIVED view (the epub's raw bytes are a zip, never a text decode's subject)
from harness.query import _read, _refuse  # noqa: E402  # the shared owner-scoped read + the shared refusal form (one machinery, never a second)

# P4-00c/P4-A: the DECLARED matrix — derived from formats.py's ADAPTERS (the
# intake registry IS the capability declaration: a format appears here
# exactly when its adapter lands, with exactly the capabilities the adapter
# carries — never a second hand-maintained table). text/plain is the first
# approved format; application/json the second (P4-A slice one); a new
# format's row lands with its own increment slice (P4-A's EPUB/PDF cards).
FORMATS = ADAPTERS

# P4-00c: the RESERVED-SURFACE registry — the named surfaces later phases own,
# declared here so the contract sketch is visible from day one, never smuggled
# in later. The reader UI itself is the separate repository.
RESERVED_SURFACES = {
    # P4-D slice one (CLAIM-075; record 67 §2): the stable @-reference
    # system LANDED — the RTM §2 item 10 reservation's own row (the same
    # promotion every landed surface took at its landing)
    "references": {
        "owner_phase": "P4-D",
        "reservation": ("LANDED in P4-D slice one (CLAIM-075): the backend verb is real — "
                        "resolve-reference (query.py — the typed SIX-STATE resolution over "
                        "the seven landed families work/source/anchor/highlight/bookmark/"
                        "note/journal_block: current | historical | tombstoned | "
                        "unavailable | ambiguous | purged; the logical target identity "
                        "separated from the selected historical revision; the explicit "
                        "version pinning serving exactly as pinned; the purge-ledger "
                        "precedence; the no-oracle byte-equal refusals — composing the "
                        "CLAIM-057 note-reference substrate, never a second "
                        "implementation); the agent-facing resolution and the reference "
                        "graph queries are the later increments (P4-E / P5); the reader "
                        "CLIENT that renders references is P4-B's separate repo (no "
                        "client work here)"),
    },
    # P4-C slice five (CLAIM-074; record 66 §2): the reading-list surface
    # LANDED — the user-defined lists over the landed library (the North
    # Star owner words' third surface, the post-#108 reconciliation's
    # landing)
    "reading-lists": {
        "owner_phase": "P4-C",
        "reservation": ("LANDED in P4-C slice five (CLAIM-074): the backend verbs are real — "
                        "create_reading_list + add_to_list + remove_from_list (commands.py — "
                        "the list header + the append-only MEMBERSHIP EVENT rows through the "
                        "spine's own ack contract, the closed op vocabulary, the derived "
                        "current view, the outbox ride) + list-lists / get-list (query.py — "
                        "the bounded/paginated listing with the derived member counts, the "
                        "current-membership read on the P4-00b contract, the no-id-echo "
                        "no-oracle); the reader CLIENT that renders the lists is P4-B's "
                        "separate repo (no client work here)"),
    },
    # P4-C slice three (CLAIM-072; record 64 §2): the journal/blocks surface
    # LANDED — the writing lab's own row (the same promotion the library and
    # session rows took at their landings)
    "journal/blocks": {
        "owner_phase": "P4-C",
        "reservation": ("LANDED in P4-C slice three (CLAIM-072): the backend verbs are real — "
                        "journal_block + revise_journal_block (commands.py — the append-only "
                        "raw/creative blocks through the spine's own ack contract, the LONG raw "
                        "thinking preserved losslessly, the revisions as NEW rows, the "
                        "source-OPTIONAL binding, no forced note funnel — the two surfaces "
                        "separate by construction) + list-journal / get-journal / "
                        "get-journal-history (query.py — the bounded/paginated listing on the "
                        "P4-00b contract, the lossless single-block read, the governed "
                        "history); the reader CLIENT that renders the writing lab is P4-B's "
                        "separate repo (no client work here)"),
    },
    "source-open/position": {
        "owner_phase": "P4-A/B",
        "reservation": ("LANDED in P4-A slice two (CLAIM-066): the backend verbs are real — "
                        "save_position (commands.py — the append-only save through the spine, "
                        "the serving-generation binding) + get_position (query.py get-position — "
                        "the last-saved position, its generation binding honest across a "
                        "re-extraction, the no-oracle); the reader CLIENT that opens a source "
                        "at the saved position is P4-B's separate repo (no client work here)"),
    },
    # P4-C slice two (CLAIM-071; record 63 §2): the session/dwell surface
    # LANDED — the reserved registry's third row promoted from the 4C plan
    # row (D-010's durable behavior data; the RTM §2.10 reservation)
    "session/dwell-events": {
        "owner_phase": "P4-C",
        "reservation": ("LANDED in P4-C slice two (CLAIM-071): the backend verbs are real — "
                        "record_session (commands.py — the append-only event through the "
                        "spine, the D-010 closed vocabulary session_start/checkpoint/dwell/"
                        "session_end, the coarse spans + the coarse dwell, the typed "
                        "ARV-SES-004 boundary refusals: keystroke/mouse-shaped payloads and "
                        "search-query/agent-prompt event kinds refused named, never stored) + "
                        "list-session-events (query.py list-session-events — the owner's "
                        "behavior-event stream, bounded/paginated, the recorded "
                        "serving-generation binding as written at event time); the reader "
                        "CLIENT that renders the reading sessions is P4-B's separate repo "
                        "(no client work here)"),
    },
    # P4-C slice one (CLAIM-070; record 62 §2): the library surface LANDED —
    # the reserved registry's second row promoted from the 4C plan row to
    # the named landed contract (the same promotion source-open/position
    # took at P4-A slice two)
    "library/current-reading": {
        "owner_phase": "P4-C",
        "reservation": ("LANDED in P4-C slice one (CLAIM-070): the backend verbs are real — "
                        "list-library (query.py list-library — the owner's imported sources "
                        "as a stable, bounded, paginated list on the P4-00b contract) + "
                        "get-reading-state (query.py get-reading-state — the derived "
                        "current-reading view over the landed position rows: the last-saved "
                        "position per source, its generation binding honest, the no-position "
                        "sources the honest not-yet-open state; every row get-position's own "
                        "answer — never a second position path); the reader CLIENT that "
                        "renders the library is P4-B's separate repo (no client work here)"),
    },
}


def _row(d: dict) -> None:
    out = dict(d)
    out["api_version"] = API_VERSION
    print(json.dumps(out, ensure_ascii=False))


def _measure(db: str, owner: str, source_id: str) -> int:
    """The MEASURED row — derived at the real boundary, never asserted: the
    owner-scoped source read, the latest generation, its passages, and the
    blob-backed coverage fraction. Absent/cross-owner refuses through the
    SHARED form (the no-oracle)."""
    qid = "'" + source_id.replace("'", "''") + "'"
    rows = _read(db, owner, f"SELECT s.media_type || '|' || s.digest FROM arv.source s "
                            f"WHERE s.id = {qid};")
    if rows is None:
        return 1
    if not rows:
        return _refuse(source_id, family="source")
    media_type, digest = rows[0].split("|", 1)
    row = {"source_id": source_id, "media_type": media_type}
    gens = _read(db, owner, f"SELECT g.id || '|' || g.state || '|' || g.ordinal || '|' || "
                            f"g.input_digest || '|' || g.extractor FROM arv.extraction_generation g "
                            f"WHERE g.source_id = {qid} ORDER BY g.ordinal DESC LIMIT 1;")
    if gens is None:
        return 1
    if not gens:
        row.update({"state": "not_extracted", "generation_id": None, "ordinal": 0,
                    "passages": 0, "coverage": 0.0, "extractor": None})
        _row(row)
        return 0
    gid, gstate, gordinal, gdigest, gextractor = gens[0].split("|", 4)
    row.update({"generation_id": gid, "ordinal": int(gordinal), "extractor": gextractor})
    # the digest binding: the generation's input digest vs the source's own —
    # the stale detector's substrate, derived honestly at read time. The
    # generation row's machine state maps onto the READINESS vocabulary:
    # current -> ready (the user-facing word), building/failed as themselves;
    # a failed generation carries its NAMED reason (the docstring's promise).
    row["state"] = ("ready" if gdigest == digest and gstate == "current"
                    else ("stale" if gdigest != digest else gstate))
    if gstate == "failed":
        frow = _read(db, owner, f"SELECT COALESCE(fail_reason, '') FROM arv.extraction_generation "
                                f"WHERE id = '{gid}';")
        if frow is None:
            return 1
        row["fail_reason"] = frow[0] if frow and frow[0] else "unnamed"
    prow = _read(db, owner, f"SELECT count(*) || '|' || COALESCE(sum(p.end_off - p.start_off), 0) "
                            f"FROM arv.passage p WHERE p.generation_id = '{gid}';")
    if prow is None:
        return 1
    count, covered = (int(x) for x in prow[0].split("|"))
    try:
        # P4-A slice three (CLAIM-067): the ONE read_text home — the epub's
        # coverage derives over its DERIVED view, exactly like the text
        # formats' own bytes
        text_len = len(read_text(media_type, digest))
    except (UnicodeDecodeError, KeyError, _FmtRefusal):
        text_len = 0  # the unreadable-blob class: the counts stand, the coverage honestly 0
    row.update({"passages": count,
                "coverage": round(covered / text_len, 6) if text_len else 0.0})
    _row(row)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the format capability matrix + extraction "
                                             "readiness (P4-00c: declared, measured, reserved — "
                                             "never asserted, never a silent miss)")
    sub = ap.add_subparsers(dest="what", required=True)
    sub.add_parser("matrix", help="the declared per-format capability rows")
    sub.add_parser("surfaces", help="the reserved-surface registry")
    p = sub.add_parser("measure", help="the MEASURED readiness row for one source")
    p.add_argument("--owner", required=True)
    p.add_argument("--source", required=True)
    a = ap.parse_args()
    db = os.environ.get("PGDATABASE", "postgres")
    if a.what == "matrix":
        for fmt, cap in sorted(FORMATS.items()):
            _row({"format": fmt, **cap})
        return 0
    if a.what == "surfaces":
        for surface, r in sorted(RESERVED_SURFACES.items()):
            _row({"surface": surface, **r})
        return 0
    return _measure(db, a.owner, a.source)


if __name__ == "__main__":
    sys.exit(main())
