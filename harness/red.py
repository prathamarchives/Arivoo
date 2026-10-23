#!/usr/bin/env python3
"""harness/red.py — `make red` (S4; LAW-11's mechanical memory) — the TYPED writer.

CLAIM-037 (F-007): schema 2 per record — binding_commit/binding_sha256 (the
git-verified revision binding), red_exit/red_code (the typed OBSERVED red,
required for a NEW record: a written assertion is not an observed failure),
red_unrecovered (the smash class's honest marker, baseline-present records
only), current_sha256, and TYPED amendments {prior_sha256, new_sha256, note,
observed_at} — the gate's ARV-RED-006 accepts a changed test only through a
typed chain bridging the trusted prior state. The TESTS tuple imports from
harness/gate.py (the ONE home). The write is atomic (tmp+os.replace) and a
file changed since read refuses (ARV-RED-009 — the single-writer protocol).
The full schema description: record 30 §4 and the slice's opening commit.
"""
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RR = REPO / "harness" / "red-records.json"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.gate import TESTS  # noqa: E402  — the ONE home (this slice's unification)


def _now() -> str:
    from harness.adapters import clock
    return clock.now()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", required=True, help="where the red run was observed (the test-only commit) / the amendment's reason")
    ap.add_argument("--exit", dest="red_exit", type=int, default=None,
                    help="the OBSERVED nonzero exit of the red run — REQUIRED for a NEW record (the typed observed-red)")
    ap.add_argument("--code", default=None,
                    help="the OBSERVED named refusal code(s) of the red run — REQUIRED for a NEW record")
    ap.add_argument("--red-commit", default=None,
                    help="the commit carrying the red form (default: HEAD; the binding must verify in git)")
    a = ap.parse_args()
    for t in TESTS:
        p = REPO / t
        if not p.is_file():
            print(f"FAIL ARV-RED-004: {t} does not exist — nothing to record")
            return 1

    # the #72 round (Greptile P2): the missing-registry recovery path — the
    # predecessor bootstrapped an empty registry; the rewrite's unconditional
    # read crashed. The ARV-RED-003 recovery path is preserved (every TESTS
    # file below then mints a NEW record, each requiring --exit/--code).
    original_text = RR.read_text() if RR.is_file() else ""
    data = json.loads(original_text) if original_text.strip() else {}
    if not RR.is_file():
        print("NOTE ARV-RED-000: harness/red-records.json is absent — bootstrapping an empty registry (the ARV-RED-003 recovery path; every TESTS file mints a NEW record below, each requiring the observed --exit/--code)")
    red_commit = a.red_commit or subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()

    for t in TESTS:
        p = REPO / t
        cur = hashlib.sha256(p.read_bytes()).hexdigest()
        is_new = t not in data
        if is_new:
            if a.red_exit is None or not a.code or a.red_exit == 0:
                print(f"FAIL ARV-RED-007: a NEW record for {t} requires the OBSERVED red (--exit nonzero + --code the named refusal) — a written assertion is not an observed failure (F-007)")
                return 1
            binding = subprocess.run(["git", "show", f"{red_commit}:{t}"], cwd=REPO, capture_output=True)
            if binding.returncode != 0:
                print(f"FAIL ARV-RED-007: the binding for {t} does not verify — git carries no {t} at {red_commit[:10]} (a revision claim must name history that exists)")
                return 1
            data[t] = {
                "schema": 2,
                "binding_commit": red_commit,
                "binding_sha256": hashlib.sha256(binding.stdout).hexdigest(),
                "red_exit": a.red_exit,
                "red_code": a.code,
                "red_evidence": a.note,
                "current_sha256": cur,
                "amendments": [],
            }
        elif data[t].get("current_sha256") != cur:
            prior = data[t]["current_sha256"]
            # the H-01b-CI smash repair kept red_evidence set only at creation;
            # the typed redesign adds the EXACT changed content to amendments
            data[t].setdefault("amendments", []).append({
                "prior_sha256": prior,
                "new_sha256": cur,
                "note": a.note,
                "observed_at": _now(),
            })
            data[t]["current_sha256"] = cur
        # unchanged digest: no-op (the note rides the invocation's output only)

    current_text = RR.read_text() if RR.is_file() else ""
    if current_text != original_text:
        print("FAIL ARV-RED-009: harness/red-records.json changed since it was read — a concurrent writer is refused (make red is a single-writer flow; the protocol is explicit, never racy)")
        return 1
    tmp = RR.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, RR)
    print(f"OK ARV-RED-005: red records updated for {len(TESTS)} test files (note: {a.note})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
