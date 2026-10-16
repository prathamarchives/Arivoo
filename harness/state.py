#!/usr/bin/env python3
"""harness/state.py — `make state` (S4; OPERATING-MODEL §9: 5s budget).

Prints the current position from the repo's own memory (STATE.md's phase line +
the harness's live status: stack reachable, applied migrations, red records,
proof sheets) — trust it over any agent's recollection (Model 2's rule).
"""
import json
import pathlib
import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])
from harness.adapters import pg  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    state = (REPO / "STATE.md").read_text()
    phase = next((l for l in state.splitlines() if l.startswith("- **Phase:**")), "")
    print(phase)  # the full phase line — the position statement; a [:300] cut truncated it mid-word (found by the fresh-context verifier, record 18 §8)
    r = pg.psql("SELECT count(*) FROM arv.schema_migrations;", db="postgres")
    if r.returncode == 0:
        print(f"- harness stack: REACHABLE · migrations recorded: {r.out}")
    else:
        print("- harness stack: UNREACHABLE (ARV-RIG-001 class — start the rig; checks needing the DB will fail closed)")
    rr = REPO / "harness" / "red-records.json"
    print(f"- red records: {len(json.loads(rr.read_text())) if rr.is_file() else 0} (LAW-11)")
    sheets = sorted((REPO / "harness" / "runs").glob("*/proofsheet.md"))
    print(f"- proof sheets: {len(sheets)}" + (f" (latest: {sheets[-1].parent.name})" if sheets else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
