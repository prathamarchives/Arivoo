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

Cases (each names its target failure):
  1. write_record numbers by MAX (a seeded gap 01,02,03,05 must yield run-06,
     never touch run-05 — the overwrite class) — the routed rider, its RED
     observed in claim-037's red-01/red-02 AND re-observed at this slice.
  2. write_record refuses the unparseable context (run-ab.json) with
     ARV-PRF-006.
  3. the red-record mint refuses an untyped NEW record (no --exit/--code)
     with ARV-RED-007.
  4. the red-record write refuses when the file changed since read
     (ARV-RED-009).
  5. the 100-capture boundary (run-100 must parse — the writer's own :02d
     output past 99).
  6. a missing registry bootstraps (the ARV-RED-003 recovery path preserved).
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

        # ---- case 1 (the routed rider, re-observed at THIS slice's commit):
        # max-based numbering never overwrites (the count-based stall class)
        seed = json.dumps({"command": "probe", "exit_code": 0, "output_sha256": "0" * 64,
                           "recorded_at": "2026-10-23T00:00:00+00:00"}, indent=2) + "\n"
        for n in ("01", "02", "03", "05"):
            (runs / f"run-{n}.json").write_text(seed)
        before = (runs / "run-05.json").read_text()
        ps.write_record(SLICE, "the-first-write", 0, "out-1")
        wrote_run06 = (runs / "run-06.json").is_file()
        run05_intact = (runs / "run-05.json").read_text() == before
        check("max-based numbering: a seeded gap yields run-06",
              wrote_run06,
              "the new record did not land at max+1")
        check("max-based numbering: the existing run-05 is byte-unchanged",
              run05_intact,
              "the write OVERWROTE an existing record (the count-based stall class, record 29 §8)")
        ps.write_record(SLICE, "the-second-write", 0, "out-2")
        check("max-based numbering: the second write advances to run-07",
              (runs / "run-07.json").is_file(),
              "the numbering stalled on one slot (each overwrite left the count unchanged)")

        # ---- case 2: the unparseable context is a refusal (ARV-PRF-006)
        runs2 = ps.RUNS / "record-machinery-probe-2"
        runs2.mkdir()
        for n in ("01", "02"):
            (runs2 / f"run-{n}.json").write_text(seed)
        (runs2 / "run-ab.json").write_text(seed)  # an unparseable record name
        refused, code = False, ""
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                ps.write_record(SLICE + "-2", "probe-write", 0, "out")
        except SystemExit:
            refused = True
            code = buf.getvalue()
        check("the unparseable numbering context refuses with ARV-PRF-006",
              refused and "ARV-PRF-006" in code,
              f"refused={refused} output={code[:160]!r}")

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
        # ---- case 5 (the routed rider): the 100-capture boundary
        runs3 = ps.RUNS / "record-machinery-probe-3"
        runs3.mkdir()
        for n in range(1, 100):
            (runs3 / f"run-{n:02d}.json").write_text(seed)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                ps.write_record(SLICE + "-3", "the-hundredth", 0, "out")
        except SystemExit:
            pass
        wrote_100 = (runs3 / "run-100.json").is_file()
        stalled = False
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                ps.write_record(SLICE + "-3", "the-hundred-first", 0, "out")
        except SystemExit:
            stalled = True
        check("the hundredth capture lands at run-100 and the writer keeps going",
              wrote_100 and not stalled,
              f"wrote_100={wrote_100} stalled_after={stalled} — the writer's own :02d output must be parseable by its own reader (the #72 round's Greptile P2)")

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

        # CLAIM-041 (H-02 part 2): the Proof Sheet's SEV section — the sheet
        # records the report + reviewed-diff digests, the disposition, the
        # findings, and the not-verified count when the slice carries sev.json
        # (the TEMPLATES §6 rule the card names). RED at the predecessor: no
        # section existed, the sheet was silent about the SEV record entirely.
        work5 = pathlib.Path(tmp) / "sev-sheet"
        work5.mkdir(parents=True)
        (work5 / "harness" / "runs" / "claim-901-sev-sheet-probe").mkdir(parents=True)
        rec5 = {"command": "python3 probe", "exit_code": 0, "commit": "0" * 40,
                "output_sha256": "0" * 64, "recorded_at": "2026-10-24T00:00:00+00:00"}
        (work5 / "harness" / "runs" / "claim-901-sev-sheet-probe" / "run-01.json").write_text(
            json.dumps(rec5, indent=2) + "\n", encoding="utf-8")
        sev_report = {
            "schema_version": 1, "slice_id": "claim-901-sev-sheet-probe",
            "base_sha": "0" * 40, "reviewed_diff_sha256": "1" * 64,
            "intent_ids": ["INT-100"], "requirement_ids": ["SYS-11"],
            "system_claims": [], "changed_components": ["harness/proofsheet.py"],
            "interfaces_reviewed": ["assemble(slice, nv)"],
            "v_model": {"component_verification": ["c"], "integration_verification": ["i"],
                        "system_verification": ["s"], "validation": ["v"]},
            "failure_modes": [{"id": "FM-01", "scenario": "s", "control": "c", "proof_ids": ["run-01"]}],
            "findings": [{"id": "SEV-1", "severity": "P2", "status": "resolved",
                          "evidence": "e", "disposition": "fixed in probe"}],
            "not_verified": ["the probe boundary: a synthetic slice, never real evidence"],
            "builder_context": "probe-builder", "reviewer_context": "probe-reviewer",
            "disposition": "PASS", "review_summary": "probe report for the sheet-section case",
        }
        sev_bytes = json.dumps(sev_report, indent=2) + "\n"
        (work5 / "harness" / "runs" / "claim-901-sev-sheet-probe" / "sev.json").write_text(
            sev_bytes, encoding="utf-8")
        import hashlib as _hl
        _mods5 = _load_machinery(work5)
        ps5 = _mods5["proofsheet"]
        ps5.RUNS = work5 / "harness" / "runs"
        sheet5 = ps5.assemble("claim-901-sev-sheet-probe", "- probe only\n")
        import hashlib as _h2
        want_digest = _h2.sha256(sev_bytes.encode()).hexdigest()
        check("the sheet embeds the SEV section (report digest + disposition + findings)",
              "Systems-engineering verification" in sheet5
              and want_digest in sheet5
              and "disposition: PASS" in sheet5
              and "findings: 1" in sheet5
              and "1111111111111111111111111111111111111111111111111111111111111111" in sheet5,
              "the TEMPLATES §6 rule: the sheet records the report + reviewed-diff digests, "
              "the disposition, the findings, and the not-verified count — RED at the predecessor "
              "(the sheet was silent about the SEV record entirely)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILED:
        print(f"RED — {len(FAILED)} failure(s): {', '.join(FAILED)}")
        print("      CLAIM-037: the record machinery must refuse its named classes (F-007's typed-record core)")
        return 1
    print("GREEN — the record machinery refuses its named classes: max-based numbering, "
          "the unparseable context, the untyped mint, the changed-since-read write, "
          "the run-100 boundary, the registry bootstrap, the SEV sheet section")
    return 0


if __name__ == "__main__":
    sys.exit(main())
