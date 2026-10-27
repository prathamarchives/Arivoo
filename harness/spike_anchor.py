#!/usr/bin/env python3
"""harness/spike_anchor.py — the Q8 anchor-stability spike (P3-03b; RTM §7.3, Q8).

The bounded stability MEASUREMENT over the SYNTHETIC corpus, run BEFORE the
format-specific location behavior freezes (PLAN's P3-03 element): the same
real machine the suite pins (import -> extract -> create_highlight ->
resolve-anchor), measured across the stability matrix —
  M1 the initial resolution:      every anchor resolves against its OWN Source
                                  version's current generation
  M2 the re-extraction stability: a NEW generation over the SAME version (a new
                                  ordinal, byte-identical passages) — every
                                  anchor still resolves; the passage ids may
                                  differ (§2.9's disposable rows), the offsets
                                  and the evidence never move
  M3 the new-edition boundary:    a NEW source row of the same work (a changed
                                  edition) exists and is extracted — the
                                  ORIGINAL anchors still resolve against THEIR
                                  version; ZERO silent retargets (SYS-05)
                                  the cosmetic re-save rides the same boundary
                                  (identical bytes are a new row too)

Q8's REGISTERED BOUNDARY (§7.3): the corpus is SYNTHETIC — this spike measures
synthetic-corpus fidelity ONLY. Any real-PDF/EPUB location-stability claim
requires a named, permitted, real corpus and measured results at the owner
gate; absent that, the freeze claims nothing about real-format stability.
OCR/scanned content is a distinct capability, never implied.

Exit 0 = the measurement ran; the report (one JSON line) is the evidence.
Run: python3 harness/spike_anchor.py
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from harness.adapters import pg  # noqa: E402

# the synthetic corpus: varied structure (headings, unicode, repeats, single-block)
CORPUS = [
    ("Spike One", "# Heading leads\n\nfirst paragraph of the study.\n\nsecond paragraph carries weight.\n"),
    ("Spike Two", "no heading in this one\n\nplain second paragraph.\n\nplain third paragraph.\n"),
    ("Spike Three", "unicode: 広い空の下で読む本。\n\nsecond block is plain English text.\n"),
    ("Spike Four", "repeated block alpha.\n\nrepeated block alpha.\n\nunique closing line stands alone.\n"),
    ("Spike Five", "# A heading run\n\n# continues\n\ncontent follows the run here.\n"),
    ("Spike Six", "single block only no internal blanks at all in this document\n"),
]


def _cli(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=180, env=ENV)


def _import(key, title, file, work_id=None):
    a = [str(REPO / "harness" / "commands.py"), "import_source", "--owner", "A",
         "--actor", "owner", "--client-id", "spike-1", "--idem-key", key,
         "--file", file, "--media-type", "text/plain"]
    if title is not None:
        a += ["--title", title]
    if work_id:
        a += ["--work-id", work_id]
    return _cli(*a)


def _extract(key, source_id):
    return _cli(str(REPO / "harness" / "extract.py"), "--owner", "A", "--actor", "owner",
                "--client-id", "spike-1", "--idem-key", key, "--source-id", source_id)


def _highlight(key, source_id, start, end):
    p = _cli(str(REPO / "harness" / "commands.py"), "create_highlight", "--owner", "A",
             "--actor", "owner", "--client-id", "spike-1", "--idem-key", key,
             "--source-id", source_id, "--start", str(start), "--end", str(end))
    hid = next((ln.split("result_ref=")[1].split()[0] for ln in p.stdout.splitlines()
                if "result_ref=" in ln), "")
    if not hid:
        return ""
    r = subprocess.run(["psql", "-X", "-A", "-t", "-U", "arv_read", "-d", DB, "-c",
                       f"SELECT anchor_id FROM arv.highlight WHERE id='{hid}';"],
                      capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


class _SpikeFailure(RuntimeError):
    """A MEASUREMENT-INPUT failure (the #88 round-2 finding): a nonzero
    resolver exit, malformed output, invalid JSON, or a failed spike-side DB
    read is NEVER an unresolved answer — it aborts the measurement with the
    named ARV-SPIKE-002, never a silent None counted into the metrics."""


def _dbq(sql: str) -> str:
    """One spike-side verification read (arv_read, the audit role). A failed
    read is a measurement-input failure — raised, never an empty string that
    would silently mislabel every generation comparison below."""
    r = subprocess.run(["psql", "-X", "-A", "-t", "-U", "arv_read", "-d", DB, "-c", sql],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise _SpikeFailure(
            f"ARV-SPIKE-002: the spike's own DB read failed — {r.stderr.strip()[:160]}")
    return r.stdout.strip()


def _resolve(anchor_id):
    p = _cli(str(REPO / "harness" / "query.py"), "resolve-anchor", "--owner", "A",
             "--id", anchor_id)
    if p.returncode != 0:
        raise _SpikeFailure(
            f"ARV-SPIKE-002: the resolver exited {p.returncode} for {anchor_id} — "
            f"a measurement-input failure, never an unresolved answer: {p.stderr.strip()[:160]}")
    # newline-only framing (the query.py side's own contract — one JSON line
    # per answer; a Unicode line separator in a future answer shape must never
    # corrupt the measurement read either)
    lines = [ln for ln in p.stdout.split("\n") if ln.strip()]
    if len(lines) != 1:
        raise _SpikeFailure(
            f"ARV-SPIKE-002: the resolver's output for {anchor_id} is not ONE line "
            f"({len(lines)}) — a malformed measurement input, never an unresolved answer")
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError as e:
        raise _SpikeFailure(
            f"ARV-SPIKE-002: the resolver's answer for {anchor_id} is invalid JSON ({e}) — "
            "a malformed measurement input, never an unresolved answer")


def _anchors_for(sid, text, tag):
    """Three anchors at varied positions: the head of the text, a mid slice, a
    block-boundary-spanning slice (safe offsets into THIS text)."""
    out = []
    bounds = [i for i in range(len(text) - 1) if text[i:i + 2] == "\n\n"]
    picks = [(0, min(5, len(text)))]
    mid = len(text) // 2
    picks.append((mid, min(mid + 7, len(text))))
    if bounds:
        b = bounds[len(bounds) // 2]
        if 0 <= b - 2 and b + 6 <= len(text) and b - 2 < b + 6:
            picks.append((b - 2, b + 6))
    seen, uniq = set(), []
    for s, e in picks:
        if s < e and (s, e) not in seen:
            seen.add((s, e))
            uniq.append((s, e))
    for k, (s, e) in enumerate(uniq, 1):
        aid = _highlight(f"spike-hl-{tag}-{k}", sid, s, e)
        if aid:
            out.append(aid)
    return out


def main() -> int:
    global ENV, DB
    DB = pg.create_scratch_db("spike")
    blob_dir = tempfile.mkdtemp(prefix="arv-spike-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)
        m = {"corpus": "synthetic", "documents": len(CORPUS), "anchors": 0,
             "m1_initial_resolved": 0, "m2_after_reextraction_resolved": 0,
             "m3_after_new_edition_resolved_own_version": 0, "silent_retargets": 0}
        try:
            for i, (title, text) in enumerate(CORPUS, 1):
                d = tempfile.mkdtemp(prefix="arv-spike-src-")
                f = pathlib.Path(d) / "doc.md"
                f.write_text(text, encoding="utf-8")
                p = _import(f"spike-src-{i}", title, str(f))
                work_id = next((ln.split("work_id=")[1].split()[0] for ln in p.stdout.splitlines()
                                if "work_id=" in ln), "")
                sid = next((ln.split("result_ref=")[1].split()[0] for ln in p.stdout.splitlines()
                            if "result_ref=" in ln), "")
                if _extract(f"spike-ext-{i}", sid).returncode != 0:
                    print(f"FAIL ARV-SPIKE-001: the spike's substrate failed at document {i}")
                    return 1
                anchors = _anchors_for(sid, text, f"{i}")
                m["anchors"] += len(anchors)
                own_gen = _dbq(f"SELECT id FROM arv.extraction_generation "
                               f"WHERE source_id='{sid}' AND state='current';")
                for aid in anchors:                      # M1: the initial resolution
                    r = _resolve(aid)
                    m["m1_initial_resolved"] += 1 if (r or {}).get("state") == "resolved" \
                        and r.get("generation_id") == own_gen else 0
                if _extract(f"spike-ext-{i}-b", sid).returncode != 0:   # M2: the re-extraction
                    print(f"FAIL ARV-SPIKE-001: the spike's re-extraction failed at document {i}")
                    return 1
                own_gen = _dbq(f"SELECT id FROM arv.extraction_generation "
                               f"WHERE source_id='{sid}' AND state='current';")
                for aid in anchors:
                    r = _resolve(aid)
                    m["m2_after_reextraction_resolved"] += 1 if (r or {}).get("state") == "resolved" \
                        and r.get("generation_id") == own_gen else 0
                f2 = pathlib.Path(d) / "doc2.md"          # M3: the new EDITION of the same work
                f2.write_text(text + "\na late paragraph arrives in edition two.\n", encoding="utf-8")
                p2 = _import(f"spike-src-{i}-v2", None, str(f2), work_id=work_id)
                sid2 = next((ln.split("result_ref=")[1].split()[0] for ln in p2.stdout.splitlines()
                             if "result_ref=" in ln), "")
                if sid2 and _extract(f"spike-ext-{i}-v2", sid2).returncode == 0:
                    # the retarget DETECTOR is the generation comparison (the #88
                    # round-2 finding): the answer's echoed source_id is the
                    # anchor row's OWN value by construction — structurally
                    # always-equal, incapable of detecting a wrong-generation
                    # resolution. The answer's generation_id is compared against
                    # the anchor's OWN version's CURRENT generation instead.
                    own_gen = _dbq(f"SELECT id FROM arv.extraction_generation "
                                   f"WHERE source_id='{sid}' AND state='current';")
                    for aid in anchors:
                        r = _resolve(aid)
                        ok = (r or {}).get("state") == "resolved" and r.get("generation_id") == own_gen
                        m["m3_after_new_edition_resolved_own_version"] += 1 if ok else 0
                        if r and r.get("state") == "resolved" and r.get("generation_id") != own_gen:
                            m["silent_retargets"] += 1     # SYS-05's forbidden class — must stay 0
                else:
                    print(f"FAIL ARV-SPIKE-001: the spike's new-edition leg failed at document {i}")
                    return 1
        except _SpikeFailure as e:
            print(f"FAIL {e}")
            print("      repair: a measurement-input failure is never an unresolved answer — the "
                  "resolver's contract is the typed states; a failure outside them aborts the measurement")
            return 1
        print(json.dumps(m, ensure_ascii=False))
        return 0
    finally:
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
