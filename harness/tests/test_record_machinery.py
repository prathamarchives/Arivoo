#!/usr/bin/env python3
"""harness/tests/test_record_machinery.py — the record/proof machinery suite.

CLAIM-037 (H-01c-evidence/privacy part 1 — F-007 + the record-29 §8 rider):
the proof-record and red-record machinery's own regressions. This suite is
itself the FIRST file registered under the slice's fail-closed registration
(every harness/tests/test_*.py must appear in the TESTS registry and carry a
red record) — the new-record flow exercised end-to-end, never asserted.

Named codes frozen BEFORE the implementation (the H-01a convention; RED-first
— every case below is observed failing at the predecessor, the slice's red-01):

  ARV-PRF-006  a proof-record write into an unparseable/occupied numbering
               context is a REFUSAL — the count-based writer (len(glob)+1)
               stalled on one slot whenever a gap made count+1 name an
               existing record, overwriting middle captures one by one
               (record 29 §8's routed defect, observed live in CLAIM-036)
  ARV-RED-007  an untyped record/mint — a written assertion is not an
               observed failure (F-007)
  ARV-RED-009  a red-record write refused: the file changed since read (the
               concurrent-writer guard — make red is a single-writer flow;
               the refusal makes the protocol explicit, never racy)

Cases (each names its target failure; the numbering cases 1/2/5 ROUTED to the
part-2 claim at the LAW-05 split — the max-based repair + the run-100 boundary
land there, their RED already observed in this slice's red-01/red-02):
  3. the red-record mint refuses an untyped NEW record (no --exit/--code)
     with ARV-RED-007 — RED at the predecessor (the note-only mint passes).
  4. the red-record write refuses when the file changed since read
     (ARV-RED-009) — RED at the predecessor (the blind read-modify-write).
  6. a missing registry bootstraps (the ARV-RED-003 recovery path preserved) —
     RED at the predecessor (the unconditional read crashed).
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILED: list[str] = []

import sys as _sys
_sys.path.insert(0, str(REPO))
from harness.gate import TESTS as TESTS_NAMES  # noqa: E402  (read-only: the registration's one home)
ARGV_BACKUP = None


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(name)


def _load_machinery(work: pathlib.Path):
    """Load the work copy's proofsheet/red modules BY FILE PATH (the KB
    pattern) so the writes land in the copy, never the real tree. red.py (in
    its fixed form) imports harness.gate — the ONE TESTS home — so the work
    tree's harness package must be importable: gate.py is copied alongside
    and the work root joins sys.path for the load, removed after."""
    mods = {}
    saved_path = sys.path[:]
    try:
        for rel in ("harness/__init__.py", "harness/gate.py", "harness/scope.py",
                    "harness/claims.py", "harness/proofsheet.py", "harness/red.py",
                    "harness/known-bad/cases.py",
                    "harness/adapters/__init__.py", "harness/adapters/clock.py"):
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, work / rel)
        sys.path.insert(0, str(work))
        for name in ("proofsheet", "red"):
            spec = importlib.util.spec_from_file_location(
                f"arv_{name}_probe", work / "harness" / f"{name}.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mods[name] = mod
    finally:
        sys.path[:] = saved_path
    return mods


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-recmach-"))
    try:
        # a work copy of the real machinery (module bytes + a scratch runs root)
        work = tmp / "work"
        (work / "harness" / "runs").mkdir(parents=True)
        (work / "harness" / "adapters").mkdir(parents=True)
        for rel in ("harness/proofsheet.py", "harness/red.py", "harness/__init__.py",
                    "harness/adapters/__init__.py", "harness/adapters/clock.py"):
            shutil.copy2(REPO / rel, work / rel)
        ps = _load_machinery(work)["proofsheet"]
        ps.RUNS = work / "harness" / "runs"
        SLICE = "record-machinery-probe"
        runs = ps.RUNS / SLICE
        runs.mkdir(parents=True)

        # ---- case 3: the untyped NEW-record mint refuses (ARV-RED-007)
        # a scratch tree where red.py writes (its own REPO is module-relative —
        # the work copy's red.py resolves to the work copy; point it at a copy
        # of the REAL records so the TEST file set is real, then delete one
        # record to force a NEW-record mint)
        rt = tmp / "redtree"
        shutil.copytree(REPO / "harness", rt / "harness",
                        ignore=shutil.ignore_patterns("__pycache__", "runs"))
        # red.py (in its fixed form) needs the ONE TESTS home it imports from gate.py
        shutil.copy2(REPO / "harness" / "gate.py", rt / "harness" / "gate.py")
        (rt / "harness" / "tests").mkdir(parents=True, exist_ok=True)
        for t in ("test_migrations.py", "test_substrate.py"):
            shutil.copy2(REPO / "harness" / "tests" / t, rt / "harness" / "tests" / t)
        records = json.loads((REPO / "harness" / "red-records.json").read_text())
        del records["harness/tests/test_migrations.py"]  # force the NEW-record path
        (rt / "harness" / "red-records.json").write_text(json.dumps(records, indent=2) + "\n")
        red = _load_machinery(rt)["red"]
        old_argv = sys.argv
        buf2 = io.StringIO()
        rc2 = 0
        try:
            sys.argv = ["red.py", "--note", "the untyped mint must-reject (no --exit/--code)"]
            with contextlib.redirect_stdout(buf2):
                rc2 = red.main() or 0
        finally:
            sys.argv = old_argv
        out2 = buf2.getvalue()
        check("the untyped NEW-record mint refuses with ARV-RED-007",
              rc2 != 0 and "ARV-RED-007" in out2,
              f"rc={rc2} output={out2[:200]!r}")

        # ---- case 4: the changed-since-read write refuses (ARV-RED-009)
        records2 = json.loads((REPO / "harness" / "red-records.json").read_text())
        (rt / "harness" / "red-records.json").write_text(json.dumps(records2, indent=2) + "\n")
        real_read = pathlib.Path.read_text
        state = {"n": 0}

        def racing_read(self, *a, **k):
            if self.name == "red-records.json" and self.parent.name == "harness":
                state["n"] += 1
                if state["n"] == 2:
                    # a concurrent writer landed BEFORE the guard's re-read — the
                    # re-read must SEE the racing content, never the stale text
                    pathlib.Path.write_text(self, json.dumps(
                        {"harness/tests/test_migrations.py": {
                            "current_sha256": "0" * 64, "amendments": [],
                            "red_evidence": "racing"}}, indent=2) + "\n")
            return real_read(self, *a, **k)

        rc3 = 0
        buf3 = io.StringIO()
        pathlib.Path.read_text = racing_read
        try:
            sys.argv = ["red.py", "--note", "the concurrent-writer must-reject"]
            with contextlib.redirect_stdout(buf3):
                rc3 = red.main() or 0
        finally:
            pathlib.Path.read_text = real_read
            sys.argv = old_argv
        out3 = buf3.getvalue()
        check("a red-record write over a changed file refuses with ARV-RED-009",
              rc3 != 0 and "ARV-RED-009" in out3,
              f"rc={rc3} output={out3[:200]!r}")
        # ---- case 6 (the #72 round, Greptile P2): the missing-registry bootstrap
        rt2 = tmp / "redtree2"
        shutil.copytree(REPO / "harness", rt2 / "harness",
                        ignore=shutil.ignore_patterns("__pycache__", "runs"))
        for rel in ("harness/__init__.py", "harness/gate.py", "harness/scope.py",
                    "harness/claims.py", "harness/proofsheet.py", "harness/red.py",
                    "harness/known-bad/cases.py",
                    "harness/adapters/__init__.py", "harness/adapters/clock.py"):
            (rt2 / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, rt2 / rel)
        # copytree already carried harness/tests (the full TESTS set); the
        # mint's binding verification needs real history — the tree git-inits
        # and commits BEFORE the registry is removed (the recovery path's input)
        subprocess.run(["git", "init", "-q"], cwd=rt2, capture_output=True)
        subprocess.run(["git", "config", "user.email", "probe@test.local"], cwd=rt2, capture_output=True)
        subprocess.run(["git", "config", "user.name", "probe"], cwd=rt2, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=rt2, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the bootstrap base"], cwd=rt2, capture_output=True)
        (rt2 / "harness" / "red-records.json").unlink()  # the recovery path's input
        red2 = _load_machinery(rt2)["red"]
        rc4 = 0
        buf4 = io.StringIO()
        _saved_argv = sys.argv
        try:
            sys.argv = ["red.py", "--note", "the bootstrap must-reject-nothing",
                        "--exit", "1", "--code", "ARV-BOOTSTRAP-PROBE"]
            with contextlib.redirect_stdout(buf4):
                rc4 = red2.main() or 0
        finally:
            sys.argv = _saved_argv
        out4 = buf4.getvalue()
        bootstrapped = (rt2 / "harness" / "red-records.json").is_file()
        check("a missing registry bootstraps (the ARV-RED-003 recovery path preserved)",
              rc4 == 0 and bootstrapped,
              f"rc={rc4} bootstrapped={bootstrapped} output={out4[:200]!r} — the recovery path crashed at the round's predecessor (Greptile P2)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILED:
        print(f"RED — {len(FAILED)} failure(s): {', '.join(FAILED)}")
        print("      CLAIM-037: the record machinery must refuse its named classes (F-007's typed-record core)")
        return 1
    print("GREEN — the record machinery refuses its named classes: the untyped mint, "
          "the changed-since-read write, the missing-registry bootstrap "
          "(the numbering cases routed to the part-2 claim at the LAW-05 split)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
