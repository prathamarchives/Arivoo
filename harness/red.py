#!/usr/bin/env python3
"""harness/red.py — `make red` (S4; LAW-11's mechanical memory).

Records the CURRENT hash of every declared test file into red-records.json
(together with an --note that states WHERE the red run was observed — the
test-only commit). Re-running after an amendment updates current_sha256 and
appends the amendment note (amendments add assertions, never remove).
"""
import argparse
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RR = REPO / "harness" / "red-records.json"
TESTS = ("harness/tests/test_migrations.py", "harness/tests/test_substrate.py",
         "harness/tests/test_commands.py", "harness/tests/test_gate_dispatch.py")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", required=True, help="where the red run was observed (the test-only commit)")
    a = ap.parse_args()
    data = json.loads(RR.read_text()) if RR.is_file() else {}
    for t in TESTS:
        p = REPO / t
        if not p.is_file():
            print(f"FAIL ARV-RED-004: {t} does not exist — nothing to record")
            return 1
        cur = hashlib.sha256(p.read_bytes()).hexdigest()
        if t in data and data[t].get("current_sha256") != cur:
            data[t].setdefault("amendments", []).append({"note": a.note})
        data[t] = {**data.get(t, {}), "current_sha256": cur,
                   "amendments": data.get(t, {}).get("amendments", [])}
        if "red_commit" not in data[t]:
            data[t]["red_evidence"] = a.note
    RR.write_text(json.dumps(data, indent=2) + "\n")
    print(f"OK ARV-RED-005: red records updated for {len(TESTS)} test files (note: {a.note})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
