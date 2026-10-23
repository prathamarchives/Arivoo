#!/usr/bin/env python3
"""harness/proofsheet.py — the Proof Sheet generator (S4; D-036; LAW-01/04, PRF-01).

The Proof Sheet is ASSEMBLED from run records (harness/runs/<slice>/run-*.json),
never hand-edited: each record carries the command, exit code, output digest, and
timestamp; the sheet embeds each record's digest and its own assembly hash.
Assembly is DETERMINISTIC (the generation time = the last record's timestamp; the
commit = HEAD), so --verify re-derives the identical bytes — a hand-edit breaks
the equality and fails with ARV-PRF-004. The not-verified list (LAW-04) is a
required section; it cannot be empty-by-omission.

Usage:
  python3 harness/proofsheet.py --slice NAME [--notverified FILE]   (assemble + write)
  python3 harness/proofsheet.py --slice NAME --verify               (re-derive + compare)
"""
import argparse
import glob
import hashlib
import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.adapters import clock  # noqa: E402

def _repo_root() -> pathlib.Path:
    """H-01b-CI (session 23): ARV_TRUSTED_ROOT re-roots this machinery onto the
    candidate tree when the trusted gate driver has validated it (absolute
    existing dir only; anything else keeps the natural root)."""
    root = os.environ.get("ARV_TRUSTED_ROOT", "")
    p = pathlib.Path(root) if root else None
    if p is not None and p.is_absolute() and p.is_dir():
        return p
    return pathlib.Path(__file__).resolve().parents[1]


REPO = _repo_root()
RUNS = REPO / "harness" / "runs"


def _sha(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def write_record(slice_name: str, command: str, exit_code: int, output: str) -> dict:
    d = RUNS / slice_name
    d.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = "(unrecorded)"
    rec = {
        "command": command, "exit_code": exit_code, "commit": commit,
        "output_sha256": _sha(output), "recorded_at": clock.now(),
    }
    # CLAIM-037 (record 29 §8's routed defect, observed live in CLAIM-036): the
    # COUNT-based numbering (len(glob)+1) stalled on one slot whenever a gap
    # made count+1 name an existing record — each overwrite left the count
    # unchanged, so every later capture rewrote the same slot. The repair:
    # MAX-based numbering, and an ambiguous numbering context is a refusal.
    import re as _re
    numbers = []
    for f in glob.glob(str(d / "run-*.json")):
        m = _re.fullmatch(r"run-(\d{2})\.json", pathlib.Path(f).name)
        if m:
            numbers.append(int(m.group(1)))
        else:
            print(f"FAIL ARV-PRF-006: the runs dir for '{slice_name}' carries an unparseable record name ({pathlib.Path(f).name}) — an ambiguous numbering context is a refusal, never a guess (the count-based overwrite class, record 29 §8)")
            raise SystemExit(1)
    n = max(numbers, default=0) + 1
    target = d / f"run-{n:02d}.json"
    if target.exists():
        # unreachable under max-based numbering unless a concurrent writer raced
        # into the slot between the glob and this write — refused fail-closed
        print(f"FAIL ARV-PRF-006: the next record slot ({target.name}) already exists — a concurrent writer is refused, never an overwrite")
        raise SystemExit(1)
    target.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def assemble(slice_name: str, notverified: str) -> str:
    """Deterministic: every line derives from the run records on disk — the
    generation time and commit come from the LAST record (captured when the runs
    executed; committing the sheet afterwards cannot change the derivation —
    that circularity was a real defect, caught by --verify itself, record 18 §4.4)."""
    records = sorted(glob.glob(str(RUNS / slice_name / "run-*.json")))
    if not records:
        print(f"FAIL ARV-PRF-001: no run records for slice '{slice_name}' — a Proof Sheet with no runs behind it is exactly the hand-written class (PRF-01)")
        print("      repair: run the checks through the gate so run records exist, then 'make prove'")
        raise SystemExit(1)
    recs = [json.loads(pathlib.Path(r).read_text()) for r in records]
    generated = max(r["recorded_at"] for r in recs)
    commit = recs[-1].get("commit", "(unrecorded)")
    lines = [f"# PROOF SHEET — slice {slice_name} (harness-built; never hand-edited — PRF-01, LAW-01)", ""]
    lines.append(f"- commit (last run record's): {commit}")
    lines.append(f"- generated (last record's timestamp): {generated}")
    lines.append(f"- run records: {len(records)}")
    lines.append("")
    lines.append("## Run records (command, exit, output digest)")
    for rec in recs:
        lines.append(f"- `{rec['command']}` -> exit {rec['exit_code']} · output sha256 {rec['output_sha256'][:16]} · {rec['recorded_at']}")
    lines.append("")
    lines.append("## Not verified (LAW-04 — required, never empty-by-omission)")
    nv = [l.strip() for l in notverified.splitlines() if l.strip()]
    if nv:
        lines.extend(f"- {l}" for l in nv)
    else:
        lines.append("- (none stated — REPAIR: the not-verified list may not be empty; LAW-04)")
    digest = _sha("\n".join(lines))
    lines.append("")
    lines.append("## Assembly")
    lines.append(f"- sheet sha256 (of the content above, excluding this line): {digest}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", required=True)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--record", metavar="CMD", help="run CMD, capture (command, exit, output digest), append a run record")
    ap.add_argument("--notverified", default=None, help="a file with the not-verified lines (LAW-04)")
    a = ap.parse_args()
    if a.record:
        r = subprocess.run(a.record, shell=True, cwd=REPO, capture_output=True, text=True, timeout=900)
        write_record(a.slice, a.record, r.returncode, r.stdout + r.stderr)
        print(f"OK ARV-PRF-005: run record appended (exit {r.returncode}, output sha256 recorded) for slice '{a.slice}'")
        return 0
    nv_path = RUNS / a.slice / "notverified.txt"
    if a.notverified:
        nv = pathlib.Path(a.notverified).read_text()
    elif nv_path.is_file():
        nv = nv_path.read_text()
    else:
        nv = ""
    sheet = assemble(a.slice, nv)
    out = RUNS / a.slice / "proofsheet.md"
    if a.verify:
        if not out.is_file():
            print(f"FAIL ARV-PRF-002: no Proof Sheet on disk for '{a.slice}' — run 'make prove' first")
            print("      repair: 'make prove SLICE=" + a.slice + "'")
            return 1
        if out.read_text() != sheet:
            print("FAIL ARV-PRF-004: the Proof Sheet on disk does NOT equal the sheet re-derived from the run records — it was hand-edited, or the records changed after assembly (PRF-01/LAW-01)")
            print("      repair: regenerate with 'make prove'; a Proof Sheet is evidence, not prose")
            return 1
        print(f"PASS ARV-PRF-004: '{a.slice}' Proof Sheet re-derives byte-identically from {len(glob.glob(str(RUNS / a.slice / 'run-*.json')))} run records")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(sheet)
    print(f"OK ARV-PRF-003: Proof Sheet written from {len(glob.glob(str(RUNS / a.slice / 'run-*.json')))} run records -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
