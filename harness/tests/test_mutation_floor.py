#!/usr/bin/env python3
"""harness/tests/test_mutation_floor.py — H-01b's RED-first regression suite (A03).

The trusted candidate-tool execution floor (PLAN card H-01b; owner turns 21/22,
INT-126/INT-127, D-040/D-041; the CodeRabbit F-005/F-013 routing): the base-owned
mutation suite must observe candidate verifier behavior in DISPOSABLE CHILD
PROCESSES over bounded fixtures — never by importing candidate code into its own
interpreter (the reproduced A03 hole: tools/verify_selftest.py:30 imports the
candidate verifier in-process; a `SystemExit(0)` at import exits the whole suite
green with zero output; a checker exception counts as a "caught guard").

Named codes frozen here BEFORE the implementation (the H-01a card's convention):
  ARV-FLOOR-001  an expected case was NOT caught (exit 0 / no expected-code FAIL
                 line / no completion line) — the vacuous-pass/blind-guard class
  ARV-FLOOR-002  integrity failure (driver/base-anchor digest mismatch, corpus
                 source changed mid-run, trusted anchor missing) — fail-closed
  ARV-FLOOR-003  an invalid catch form (child traceback, timeout, output-budget
                 hit) — an ordinary exception is NEVER a named refusal
  ARV-FLOOR-004  fixture construction refusal (non-regular entry, per-file /
                 total / count budget) — sanitized diagnostics, never raw paths
  ARV-FLOOR-005  the candidate verifier is missing — fail-closed, never a skip
  ARV-FLOOR-006  manifest validation failure (missing/duplicate/unknown case,
                 malformed record, count mismatch)

Driver CLI contract frozen here: `tools/verify_selftest.py [--repo DIR]
[--only MUT-XX[,MUT-YY..]] [--floor-base DIR] [--manifest-out PATH]
[--case-timeout SECONDS]`. Exit 0 only when every expected case is caught, every
integrity anchor verifies, and the completion manifest validates.

Each test exercises the REAL runner path (the driver is invoked as a subprocess,
exactly the way CI invokes it) against a disposable candidate tree. The positive
path (the real corpus + the real verifier) proves the floor still enforces all 30
base mutations. The residual demonstration (fake-fail) documents the boundary the
floor alone does not claim: a verifier that prints the expected failure protocol
without checking is caught by the POSITIVE 51/0 step of the same required job,
not by this floor — stated, never hidden.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DRIVER = REPO / "tools" / "verify_selftest.py"

CANARY = "ghp_SECRET_CANARY_9f8e7d6c5b4a"


# --------------------------------------------------------------------------
# fixture helpers (test-side; the DRIVER has its own bounded builder — these
# build the disposable CANDIDATE trees the driver is pointed at)
# --------------------------------------------------------------------------

STUB_CORPUS = {
    "AGENTS.md": "# AGENTS\nread order stub\n1. `/STATE.md`\n2. `/CLAIMS.md`\n",
    "STATE.md": (
        "# STATE\n\n## Where things stand\n- **Exact next action:** stub\n"
    ),
    "INTENT-LEDGER.md": "**INT-091 — STUB — active**\n\nStatus legend: `active`.\n",
    "NORTH-STAR.md": "# NORTH-STAR\nno tag field\n",
    "EXECUTION.md": "# EXECUTION\n| Q1 | stub |\n",
    "DECISIONS.md": "# DECISIONS\n| D-007 | stub | Update 2026-10-14 (D-028)\n",
    "OPERATING-MODEL.md": "# OM\nhost-agnostic (D-028) INT-070 GLM\n",
    "GLOSSARY.md": "# GLOSSARY\nstub\n",
    "PRINCIPLES.md": "# PRINCIPLES\nstub\n",
    "LAWS.md": "# LAWS\nstub\n",
    "ENGINEERING.md": "# ENGINEERING\nstub\n",
    "PLAN.md": "# PLAN\nstub\n",
    "CLAIMS.md": "# CLAIMS\n## Open claims\n| a | b |\n|---|---|\n",
    "context/raw/0.txt": "stub raw corpus\n",
    "context/extracted/01-STUB.md": "# 1\n> STATUS: stub\n",
    "context/reviews/r.md": "# r\n",
    "context/SOURCE-COVERAGE-MANIFEST.md": "# manifest\n",
    "failures/FAIL-001.yaml": "id: FAIL-001\n",
}


def build_candidate(td: Path, verifier: str | None = "print('stub')\n",
                    extra: dict[str, str | bytes] | None = None) -> Path:
    """A disposable minimal candidate tree: stub corpus + a candidate verifier."""
    cand = td / "candidate"
    for rel, text in STUB_CORPUS.items():
        p = cand / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if verifier is not None:
        vt = cand / "tools" / "verify_canonical_layer.py"
        vt.parent.mkdir(parents=True, exist_ok=True)
        vt.write_text(verifier, encoding="utf-8")
    for rel, val in (extra or {}).items():
        p = cand / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(val, bytes):
            p.write_bytes(val)
        else:
            p.write_text(val, encoding="utf-8")
    return cand


def run_driver(cand: Path | None = None, only: str | None = None,
               floor_base: str | None = None, timeout: int = 420,
               manifest_out: Path | None = None, case_timeout: int | None = None,
               validate_manifest: Path | None = None,
               extra_env: dict[str, str] | None = None,
               driver_path: Path | None = None) -> subprocess.CompletedProcess:
    """Invoke the REAL driver exactly the way CI does (a subprocess; -I isolated
    when an anchor is in play, matching the workflow's floor step). driver_path
    overrides the driver location — the anchored-copy launch (CI copies the
    base judge INTO the candidate tree and runs it from there)."""
    cmd = [sys.executable]
    if floor_base is not None:
        cmd.append("-I")
    cmd += [str(driver_path or DRIVER)]
    if cand is not None:
        cmd += ["--repo", str(cand)]
    if only:
        cmd += ["--only", only]
    if floor_base is not None:
        cmd += ["--floor-base", floor_base]
    if manifest_out is not None:
        cmd += ["--manifest-out", str(manifest_out)]
    if case_timeout is not None:
        cmd += ["--case-timeout", str(case_timeout)]
    if validate_manifest is not None:
        cmd += ["--validate-manifest", str(validate_manifest)]
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)


# the adversarial candidate verifiers ------------------------------------------------

V_EARLY_EXIT = "import sys\nsys.exit(0)\n"                                  # A03 form 1
V_ALWAYS_GREEN = (
    "print('canonicalization-layer verifier — 51 checks, 0 failures')\n"
    "print('GREEN — stub')\n"
)
V_WORDS_EXIT_0 = (
    "print('VER-701 FAIL  fake')\n"
    "print('canonicalization-layer verifier — 51 checks, 1 failures')\n"
)
V_CRASH = "1 / 0\n"                                                          # any-exception class
V_MIDRUN_WRITER = (
    "# A03 form 2: the child mutates the SOURCE corpus mid-run. The source path\n"
    "# travels as corpus data (source-path.txt) — in CI the source IS the\n"
    "# candidate's own tree, so this is exactly the real attack surface; the\n"
    "# floor must detect it at the next case's integrity re-verification.\n"
    "import os\n"
    "here = os.path.dirname(os.path.abspath(__file__))\n"
    "src = open(os.path.join(here, '..', 'source-path.txt'), encoding='utf-8').read().strip()\n"
    "with open(src, 'a', encoding='utf-8') as f:\n"
    "    f.write('\\n# mutated by candidate child\\n')\n"
    "print('canonicalization-layer verifier — 51 checks, 0 failures')\n"
)
V_FAKE_FAIL = (
    "import sys\n"
    "print('VER-701 FAIL  fake')\n"
    "print('canonicalization-layer verifier — 51 checks, 1 failures')\n"
    "sys.exit(1)\n"
)
V_SHADOW_PROBE = (
    "# a candidate tools/shutil.py shadow probe: if the TRUSTED driver ever\n"
    "# imports shutil with this directory on sys.path, this payload runs.\n"
    "import os\n"
    "here = os.path.dirname(os.path.abspath(__file__))\n"
    "open(os.path.join(here, '..', 'SHADOW_MARKER.txt'), 'w').write('shadowed')\n"
)


V_FLOOD = (
    "import sys\n"
    "for _ in range(400):\n"
    "    sys.stdout.write('x' * 65536)\n"
)
V_HANG = (
    "import time\n"
    "time.sleep(600)\n"
)


# --------------------------------------------------------------------------
# the RED-first suite
# --------------------------------------------------------------------------

class MutationFloorTests(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="arvoo-floor-test-")
        self.td = Path(self._td.name)
        self.addCleanup(self._td.cleanup)

    # -- the reproduced A03 hole, now a stable regression ---------------------

    def test_01_early_exit_candidate_must_fail_the_floor(self):
        """A03 form 1: candidate `SystemExit(0)` at import. The floor must exit
        RED with the not-caught disposition — at the predecessor the whole suite
        imports the candidate in-process and exits 0 with ZERO output."""
        cand = build_candidate(self.td, verifier=V_EARLY_EXIT)
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0,
                            "the vacuous pass MUST be refused — exit code was 0")
        self.assertIn("ARV-FLOOR-001", r.stdout + r.stderr)

    def test_02_words_without_refusal_must_fail_the_floor(self):
        """A candidate that PRINTS the expected failure words but returns
        success (exit 0) must be refused — printing is not refusing."""
        cand = build_candidate(self.td, verifier=V_WORDS_EXIT_0)
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-001", r.stdout + r.stderr)

    def test_03_checker_crash_is_not_a_named_refusal(self):
        """The narrowed any-exception semantics: an ordinary child exception
        (traceback) is NOT a valid catch — ARV-FLOOR-003, never a green."""
        cand = build_candidate(self.td, verifier=V_CRASH)
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-003", r.stdout + r.stderr)

    def test_04_missing_candidate_verifier_fails_closed(self):
        """No tools/verify_canonical_layer.py in the candidate tree →
        ARV-FLOOR-005, never a silent skip, never a green."""
        cand = build_candidate(self.td, verifier=None)
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-005", r.stdout + r.stderr)

    # -- integrity: the write-after-checksum class (A03 form 2) --------------

    def test_05_midrun_source_mutation_must_be_detected(self):
        """A03 form 2: a candidate child that mutates the SOURCE corpus mid-run
        must trip the per-case integrity re-verification — ARV-FLOOR-002 — and
        the floor must end RED."""
        cand = build_candidate(self.td, verifier=V_MIDRUN_WRITER)
        # the source path travels as corpus data into the fixture (in CI the
        # source IS the candidate's own tree — no secrecy, only detection)
        (cand / "source-path.txt").write_text(str(cand / "AGENTS.md") + "\n", encoding="utf-8")
        r = run_driver(cand, only="MUT-04,MUT-13")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-002", r.stdout + r.stderr)

    def test_06_missing_trusted_anchor_fails_closed(self):
        """An explicit --floor-base that does not exist must refuse — the
        trusted anchor is required, never assumed."""
        cand = build_candidate(self.td, verifier=V_ALWAYS_GREEN)
        r = run_driver(cand, only="MUT-04",
                       floor_base=str(self.td / "no-such-base"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-002", r.stdout + r.stderr)

    # -- fixture hygiene (F-013/F-012 classes, the directive §4.3) -----------

    def test_07_corpus_symlink_must_be_rejected_sanitized(self):
        """A tracked-path symlink inside the corpus must refuse with
        ARV-FLOOR-004 — never dereferenced, never a hang — and the fixture
        temp space must be cleaned up."""
        cand = build_candidate(self.td, verifier=V_ALWAYS_GREEN)
        (cand / "context" / "raw").mkdir(parents=True, exist_ok=True)
        os.symlink("/dev/null", cand / "context" / "raw" / "evil-link")
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-004", r.stdout + r.stderr)

    def test_08_oversized_file_must_trip_the_budget(self):
        """A 16 MiB regular corpus file (per-file budget 8 MiB) must refuse
        with ARV-FLOOR-004 — bounded by construction."""
        cand = build_candidate(self.td, verifier=V_ALWAYS_GREEN,
                               extra={"context/raw/huge.bin": b"\0" * (16 * 1024 * 1024)})
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-004", r.stdout + r.stderr)

    def test_09_secret_shaped_failure_never_leaks(self):
        """F-012 class: a secret-shaped filename that breaks fixture
        construction must appear in NEITHER stdout NOR stderr."""
        cand = build_candidate(self.td, verifier=V_ALWAYS_GREEN)
        os.symlink("/dev/null", cand / f"{CANARY}.md")
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        combined = r.stdout + r.stderr
        self.assertNotIn(CANARY, combined,
                         "a secret-shaped path leaked into the floor's diagnostics")

    # -- import shadowing (F-005) ---------------------------------------------

    def test_10_candidate_shadow_module_never_reaches_the_driver(self):
        """F-005, the REAL CI path: the trusted judge is copied INTO the
        candidate tree (the anchored copy) and launched from there — a candidate
        tools/shutil.py must never execute inside it. The marker file the shadow
        payload would write must not exist after the run. At the predecessor the
        in-process suite imports shutil from the script directory BEFORE its
        verifier import — the shadow runs — RED."""
        cand = build_candidate(self.td, verifier=V_ALWAYS_GREEN,
                               extra={"tools/shutil.py": V_SHADOW_PROBE})
        anchored = cand / "tools" / "verify_selftest_anchored.py"
        shutil.copyfile(DRIVER, anchored)
        # the CI anchor step ALSO copies the runner module (under its real name)
        # before the floor step runs — the fixture must mirror that or the driver
        # cannot load its machinery at all (the first draft crashed silently)
        shutil.copyfile(REPO / "tools" / "mutation_runner.py",
                        cand / "tools" / "mutation_runner.py")
        r = run_driver(cand, only="MUT-04", floor_base=str(REPO / "tools"),
                       driver_path=anchored)
        # the floor must actually RUN (the anchored-name repair's own lesson:
        # the first draft of this test passed VACUOUSLY — the driver refused
        # ARV-FLOOR-002 before any case, so the marker assertion never engaged)
        self.assertNotIn("ARV-FLOOR-002", r.stdout + r.stderr,
                         "the anchored launch must resolve the base counterpart name and RUN")
        self.assertIn("MUT-04", r.stdout,
                      "the floor must run its case — a refusal that skips every case is a vacuous pass")
        self.assertFalse((cand / "SHADOW_MARKER.txt").exists(),
                         "the candidate shadow module executed inside the trusted driver")

    # -- the completion manifest (contract point 2/3) --------------------------

    def test_11_manifest_validator_refuses_incomplete_and_malformed(self):
        """The PUBLIC validator surface (the driver's --validate-manifest CLI —
        never an internal duplicate): a good manifest validates; a missing
        case, a duplicate case, an unknown case and a malformed record are
        each refused with ARV-FLOOR-006."""
        good = {
            "schema_version": 1,
            "expected_cases": ["MUT-04", "MUT-13"],
            "cases": [
                {"code": "MUT-04", "expect": "VER-701", "caught": True, "disposition": "caught"},
                {"code": "MUT-13", "expect": "VER-701", "caught": True, "disposition": "caught"},
            ],
        }
        missing = json.loads(json.dumps(good)); missing["cases"] = missing["cases"][:1]
        dup = json.loads(json.dumps(good)); dup["cases"][1]["code"] = "MUT-04"
        unknown = json.loads(json.dumps(good)); unknown["cases"][1]["code"] = "MUT-99"
        malformed = json.loads(json.dumps(good)); del malformed["cases"][1]["caught"]

        def mfile(obj, n: int) -> Path:
            p = self.td / f"manifest-{n}.json"
            p.write_text(json.dumps(obj), encoding="utf-8")
            return p

        r = run_driver(validate_manifest=mfile(good, 0), only="MUT-04,MUT-13")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ARV-FLOOR-006", r.stdout)  # the OK line names the check
        for i, bad in enumerate((missing, dup, unknown, malformed), 1):
            r = run_driver(validate_manifest=mfile(bad, i), only="MUT-04,MUT-13")
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("ARV-FLOOR-006", r.stdout + r.stderr)
        # a non-JSON file is refused too (fail-closed on unreadable evidence)
        junk = self.td / "manifest-junk.json"
        junk.write_text("this is not json", encoding="utf-8")
        r = run_driver(validate_manifest=junk, only="MUT-04,MUT-13")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-006", r.stdout + r.stderr)

    def test_12_green_run_writes_complete_manifest(self):
        """The positive path over the REAL corpus: 30/30 caught, exit 0, and a
        complete manifest whose case set covers all 30 base codes exactly once."""
        with tempfile.TemporaryDirectory(prefix="arv-floor-manifest-") as md:
            mout = Path(md) / "manifest.json"
            r = run_driver(only=None, timeout=900, manifest_out=mout)  # the real repo, the real verifier
            self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
            m = json.loads(mout.read_text())
            self.assertEqual(m["verdict"], "GREEN")
            codes = [c["code"] for c in m["cases"]]
            self.assertEqual(len(codes), 30)
            self.assertEqual(len(set(codes)), 30)
            self.assertTrue(all(c["caught"] for c in m["cases"]))
            self.assertIn("corpus_digest", m)
            self.assertIn("candidate_verifier_sha256", m)
            self.assertIn("boundary", m)

    # -- the honest residual, demonstrated not hidden --------------------------

    def test_13_fake_fail_passes_the_floor_protocol_by_design(self):
        """RESIDUAL DEMONSTRATION (labeled, never a security claim): a verifier
        that prints the expected failure protocol and exits 1 WITHOUT checking
        satisfies this floor's per-case contract. It is caught by the POSITIVE
        51/0 step of the same required CI job (the two-sided floor, D-035) —
        the driver states the boundary in its output; this test pins that
        statement so the residual stays written down."""
        cand = build_candidate(self.td, verifier=V_FAKE_FAIL)
        r = run_driver(cand, only="MUT-04")
        self.assertEqual(r.returncode, 0)
        self.assertIn("boundary", r.stdout.lower())

    # -- bounded execution (the directive §4.2 point 2) -------------------------

    def test_14_hanging_child_is_a_named_timeout_refusal(self):
        """A child that hangs is killed at the case timeout and recorded as
        ARV-FLOOR-003 — never an unbounded wait, never a green."""
        cand = build_candidate(self.td, verifier=V_HANG)
        r = run_driver(cand, only="MUT-04", timeout=120, case_timeout=2)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-FLOOR-003", r.stdout + r.stderr)

    def test_15_output_flood_is_bounded_and_fails_closed(self):
        """A child flooding stdout is capped by the per-process output budget
        (RLIMIT_FSIZE) and the driver's bounded read; the case fails closed
        with no fabricated completion line accepted, and the flood content is
        never echoed into the driver's own output."""
        cand = build_candidate(self.td, verifier=V_FLOOD)
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        # the driver's captured child output must be bounded (<= the 1 MiB read cap)
        self.assertLessEqual(len(r.stdout), 2 * 1024 * 1024)
        # the flood content itself is never echoed back
        self.assertNotIn("x" * 1024, r.stdout + r.stderr)

    def test_16_failed_construction_still_cleans_the_temp_root(self):
        """The cleanup scope is established BEFORE any construction: after a
        fixture refusal the driver's printed temp root must be gone."""
        cand = build_candidate(self.td, verifier=V_ALWAYS_GREEN,
                               extra={"context/raw/huge.bin": b"\0" * (16 * 1024 * 1024)})
        r = run_driver(cand, only="MUT-04")
        self.assertNotEqual(r.returncode, 0)
        m = re.search(r"floor temp root: (\S+)", r.stdout)
        self.assertIsNotNone(m, "the driver must print its temp root for auditability")
        self.assertFalse(Path(m.group(1)).exists(),
                         "the temp root survived a failed construction")


if __name__ == "__main__":
    unittest.main(verbosity=2)
