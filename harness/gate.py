#!/usr/bin/env python3
"""harness/gate.py — the gate (S4; D-036; the Phase 2 exit assembly).

All mechanical checks; exit 0 or 1; every failure a named code (diagnostics
contract). Check order:

  1. ARV-GATE-001/002  the declared test suites EXIST (fail-closed on a missing
                       file) and PASS on the real stack
  2. ARV-RED-001/002   red records: every test file has one (LAW-11) and its
                       current hash matches the record (amendments re-record)
  3. ARV-SCOPE/PROT/SIZE  the diff is inside the declared scope, protected paths
                       carry owner refs, the size limits hold (LAW-05/06/07)
  4. ARV-LAW24-001     ambient time/IDs/randomness only inside adapters/
  5. ARV-DEP-008       no unapproved dependencies (LAW-08)
  6. KB-01..06         every known-bad case is REJECTED with its named code
                       (a passing known-bad is a broken guard — KB-05)
  7. ARV-PRF-004       the slice's Proof Sheet re-derives byte-identically (LAW-01)

Diff modes: --diff <base> (git diff base..HEAD vs the slice's declaration) or
--no-diff (main/selfcheck: the diff-scoped checks ran at PR time on the same
changes through the protected workflow). Run records for 'make prove' are
written by --record.
"""
import argparse
import hashlib
import io
import json
import contextlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import proofsheet, scope  # noqa: E402

# known-bad cases load BY FILE PATH (the doc-conventional directory carries a
# hyphen — not a Python package name; spec-loading keeps it importable anyway)
import importlib.util  # noqa: E402

_kb_spec = importlib.util.spec_from_file_location(
    "known_bad_cases", pathlib.Path(__file__).parent / "known-bad" / "cases.py")
kbcases = importlib.util.module_from_spec(_kb_spec)
_kb_spec.loader.exec_module(kbcases)

REPO = pathlib.Path(__file__).resolve().parents[1]
TESTS = ("harness/tests/test_migrations.py", "harness/tests/test_substrate.py",
         "harness/tests/test_commands.py")


def run_cmd(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)


def check_declared_files() -> list:
    """ARV-GATE-001: a deleted/renamed declared test is a skipped test — RED."""
    fails = []
    for t in TESTS:
        if not (REPO / t).is_file():
            print(f"FAIL ARV-GATE-001: declared test {t} is MISSING — a deleted or renamed test is a skipped test (fail-closed)")
            print("      repair: restore the test, or update the declared suite deliberately through a gate change (LAW-09 class)")
            fails.append("ARV-GATE-001")
    return fails


def check_suites() -> list:
    fails = check_declared_files()
    for t in TESTS:
        if not (REPO / t).is_file():
            continue
        r = run_cmd([sys.executable, t])
        if r.returncode != 0:
            print(f"FAIL ARV-GATE-002: {t} exited {r.returncode} — the suite is red")
            print("      repair: run the suite directly for its named failure and repair per its message")
            fails.append("ARV-GATE-002")
        else:
            print(f"PASS {t}: exit 0 on the real stack")
    return fails


def check_red_records() -> list:
    fails = []
    rr_path = REPO / "harness" / "red-records.json"
    if not rr_path.is_file():
        print("FAIL ARV-RED-003: harness/red-records.json is missing — the red-first discipline has no mechanical memory (LAW-11)")
        print("      repair: 'make red' at the test-only commit, or backfill with the red commit's evidence")
        return ["ARV-RED-003"]
    data = json.loads(rr_path.read_text())
    for t in TESTS:
        if t not in data:
            print(f"FAIL ARV-RED-001: no red record for {t} — every test file must carry its red evidence (LAW-11: committed alone, observed failing)")
            print("      repair: 'make red' at the test-only commit, or backfill the record with the red commit's evidence")
            fails.append("ARV-RED-001")
            continue
        cur = hashlib.sha256((REPO / t).read_bytes()).hexdigest()
        if cur != data[t].get("current_sha256"):
            print(f"FAIL ARV-RED-002: {t} changed since its record (hash mismatch, no amendment) — tests edited after red (LAW-11)")
            print("      repair: re-record with 'make red' and an amendment note (amendments add assertions, never remove)")
            fails.append("ARV-RED-002")
    return fails


def check_diffs(base: str, slice_name: str) -> list:
    if not base:
        print("NOTE ARV-SCOPE-000: no-diff mode (main/selfcheck) — the diff-scoped checks ran at PR time on these same changes")
        return []
    fails = scope.check_scope(scope.diff_paths(base), slice_name)
    fails += scope.check_size(scope.diff_stats(base))
    return fails


def run_known_bads() -> list:
    """KB-05: a known-bad that passes is a broken guard — red, stop building."""
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="arv_kb_"))
    fails = []
    try:
        copy = scratch / "repo"
        shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "harness/runs"))
        probe = copy / "harness" / "runs" / kbcases.SLICE
        probe.mkdir(parents=True, exist_ok=True)
        # the probe declaration: declared-but-UNREFERENCED protected prefixes (the refusals' target)
        (probe / "scope.txt").write_text("harness/tests\nharness/runs\n.github\nharness/scope.py\n")
        (probe / "run-01.json").write_text(json.dumps(
            {"command": "probe", "exit_code": 0, "output_sha256": "0" * 64,
             "recorded_at": "2026-10-16T00:00:00+00:00"}) + "\n")
        ps = kbcases._load(copy, "harness.proofsheet")
        ps.RUNS = probe.parent
        (probe / "proofsheet.md").write_text(ps.assemble(kbcases.SLICE, "- probe only"))
        for cid, desc, code, probe_fn in kbcases.CASES:
            work = scratch / cid
            shutil.copytree(copy, work, ignore=shutil.ignore_patterns("__pycache__"))
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    probe_fn(work)
            except SystemExit:
                pass
            if code in buf.getvalue():
                print(f"PASS {cid}: {desc} -> REFUSED with {code} (the guard fires)")
            else:
                print(f"FAIL {cid}: {desc} -> the guard did NOT fire (expected {code}) — a broken guard (KB-05)")
                print("      repair: fix the check so this known-bad is rejected; building stops until it is")
                fails.append(cid)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(description="the gate (S4)")
    ap.add_argument("--slice", default=None, help="the slice whose declaration + Proof Sheet are checked")
    ap.add_argument("--diff", default=None, help="git base for the diff (PR mode), e.g. origin/main")
    ap.add_argument("--no-diff", action="store_true")
    ap.add_argument("--skip-suites", action="store_true", help="CI re-entry: the suites already ran in this job")
    ap.add_argument("--known-bad-only", action="store_true", help="run only the known-bad matrix")
    a = ap.parse_args()
    if a.known_bad_only:
        fails = run_known_bads()
        print()
        if fails:
            print(f"RED — {len(fails)} broken guard(s): {', '.join(fails)} (KB-05 — building stops)")
            return 1
        print("GREEN — every known-bad is rejected with its named code (KB-01..06)")
        return 0
    slice_name = a.slice or "main-selfcheck"
    fails: list[str] = []

    if not a.skip_suites:
        print("declared suites (fail-closed + real-stack):")
        fails += check_suites()
    print("red records (LAW-11):")
    fails += check_red_records()
    print("scope/size (LAW-05/06/07):")
    fails += check_diffs("" if (a.no_diff or not a.diff) else a.diff, slice_name)
    print("LAW-24 boundary lint:")
    fails += scope.lint_boundary()
    print("LAW-08 dependency check:")
    fails += scope.check_deps()
    print("known-bad matrix (KB-05):")
    fails += run_known_bads()
    if a.slice:
        print(f"Proof Sheet verify ({slice_name}):")
        ps = proofsheet
        argv = sys.argv[:]
        sys.argv = ["proofsheet.py", "--slice", slice_name, "--verify"]
        try:
            if ps.main() != 0:
                fails.append("ARV-PRF-004")
        finally:
            sys.argv = argv
    else:
        print("NOTE ARV-PRF-000: selfcheck mode (no slice named) — per-slice Proof Sheets verify at slice time")

    print()
    if fails:
        print(f"RED — the gate refuses: {len(fails)} failure(s): {', '.join(sorted(set(fails)))}")
        print("Ref: OPERATING-MODEL §9, LAWS.md, record 18 §4.4 — a red gate blocks the merge (the check is bound)")
        return 1
    print(f"GREEN — the gate passes (slice={slice_name}; suites + red records + scope/size + lint + deps + known-bads + proofsheet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
