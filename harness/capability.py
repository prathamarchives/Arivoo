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
from harness.query import _read, _refuse  # noqa: E402  # the shared owner-scoped read + the shared refusal form (one machinery, never a second)

# P4-00c: the DECLARED matrix — exactly what the landed machinery does, never
# more. text/plain is the FIRST APPROVED format (the readable-text block
# tiler, arivoo-text-blocks.v1: blank-line blocks, headings attach-forward,
# contiguous tiling). A new format's row lands with its own converter slice
# (P4-A's per-format work) — never by editing this comment.
FORMATS = {
    "text/plain": {
        "native_text": True,     # the bytes ARE the text (no OCR needed)
        "scan_ocr": False,       # no scan/OCR path exists
        "layout": "reflow",      # reflowed text (not a fixed-layout page grid)
        "extraction": "supported",
        "approved": True,
        "extractor": "arivoo-text-blocks.v1",
    },
}

# P4-00c: the RESERVED-SURFACE registry — the named surfaces later phases own,
# declared here so the contract sketch is visible from day one, never smuggled
# in later. The reader UI itself is the separate repository.
RESERVED_SURFACES = {
    "source-open/position": {
        "owner_phase": "P4-A/B",
        "reservation": ("the read-position surface — open a source at a saved "
                        "position, save the reading position, return to it; the "
                        "bookmark/anchor machinery is the substrate, the "
                        "surface itself lands with P4-A/B (no reader-client "
                        "work in this repository)"),
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
    # current -> ready (the user-facing word), building/failed as themselves.
    row["state"] = ("ready" if gdigest == digest and gstate == "current"
                    else ("stale" if gdigest != digest else gstate))
    prow = _read(db, owner, f"SELECT count(*) || '|' || COALESCE(sum(p.end_off - p.start_off), 0) "
                            f"FROM arv.passage p WHERE p.generation_id = '{gid}';")
    if prow is None:
        return 1
    count, covered = (int(x) for x in prow[0].split("|"))
    try:
        text_len = len(blob.get(digest).decode("utf-8"))
    except Exception:
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
