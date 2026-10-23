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
     never touch run-05 — the overwrite class) — RED at the predecessor (the
     count-based writer overwrites run-05 and stalls).
  2. write_record refuses the unparseable context (run-ab.json) with
     ARV-PRF-006 — RED at the predecessor (the count-based writer sails past).
  3. the red-record mint refuses an untyped NEW record (no --exit/--code)
     with ARV-RED-007 — RED at the predecessor (the note-only mint passes).
  4. the red-record write refuses when the file changed since read
     (ARV-RED-009) — RED at the predecessor (the blind read-modify-write).
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILED: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(name)


def _load_machinery(work: pathlib.Path):
    """Load the work copy's proofsheet/red modules BY FILE PATH (the KB
    pattern) so the writes land in the copy, never the real tree."""
    mods = {}
    for name in ("proofsheet", "red"):
        spec = importlib.util.spec_from_file_location(
            f"arv_{name}_probe", work / "harness" / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mods[name] = mod
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

        # ---- case 1: max-based numbering never overwrites (the routed rider)
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
        import contextlib, io
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
        refused2 = False
        try:
            sys.argv = ["red.py", "--note", "the untyped mint must-reject (no --exit/--code)"]
            with contextlib.redirect_stdout(buf2):
                red.main()
        except SystemExit as e:
            refused2 = e.code not in (0, None)
        finally:
            sys.argv = old_argv
        out2 = buf2.getvalue()
        check("the untyped NEW-record mint refuses with ARV-RED-007",
              refused2 and "ARV-RED-007" in out2,
              f"refused={refused2} output={out2[:200]!r}")

        # ---- case 4: the changed-since-read write refuses (ARV-RED-009)
        records2 = json.loads((REPO / "harness" / "red-records.json").read_text())
        (rt / "harness" / "red-records.json").write_text(json.dumps(records2, indent=2) + "\n")
        real_read = pathlib.Path.read_text
        state = {"n": 0}

        def racing_read(self, *a, **k):
            out = real_read(self, *a, **k)
            if self.name == "red-records.json" and self.parent.name == "harness":
                state["n"] += 1
                if state["n"] == 2:
                    # a concurrent writer landed between red.py's read and write
                    pathlib.Path.write_text(self, json.dumps(
                        {"harness/tests/test_migrations.py": {
                            "current_sha256": "0" * 64, "amendments": [],
                            "red_evidence": "racing"}}, indent=2) + "\n")
            return out

        refused3 = False
        buf3 = io.StringIO()
        pathlib.Path.read_text = racing_read
        try:
            sys.argv = ["red.py", "--note", "the concurrent-writer must-reject"]
            with contextlib.redirect_stdout(buf3):
                red.main()
        except SystemExit as e:
            refused3 = e.code not in (0, None)
        finally:
            pathlib.Path.read_text = real_read
            sys.argv = old_argv
        out3 = buf3.getvalue()
        check("a red-record write over a changed file refuses with ARV-RED-009",
              refused3 and "ARV-RED-009" in out3,
              f"refused={refused3} output={out3[:200]!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILED:
        print(f"RED — {len(FAILED)} failure(s): {', '.join(FAILED)}")
        print("      CLAIM-037: the record machinery must refuse its named classes (F-007 + the record-29 §8 rider)")
        return 1
    print("GREEN — the record machinery refuses its named classes: max-based numbering, "
          "the unparseable context, the untyped mint, the changed-since-read write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
