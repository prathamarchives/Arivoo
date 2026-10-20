#!/usr/bin/env python3
"""harness/tests/test_trusted_gate.py — H-01b-CI's RED-first suite (F-004/F-006/B2).

The trusted gate driver (NEW tools/trusted_gate.py — base-owned, copied into the
candidate tree as the sha256-verified anchored copy, launched with `python3 -I`):
NO required check's green result may depend solely on code the PR candidate
controls or edits (the H-01b-CI card; owner turn 22 §5.5, INT-127/D-041).

  F-004  the harness job's evidence no longer comes from candidate-editable
         Make recipes: the driver selects the required suites from the BASE's
         gate.TESTS (trusted state) and runs the candidate's own suite files
         directly — a gutted Makefile cannot fabricate "suites ran".
  F-006  the candidate's gate never executes its own known-bad registry inside
         the trusted run: the BASE's gate machinery, re-rooted over the
         candidate tree (ARV_TRUSTED_ROOT), re-runs the PR-mode obligations —
         the candidate gate's own green is never the only evidence.
  B2     the driver is launched with -I (no script-dir on sys.path) — the
         FLOOR-REVIEW-1 quantified that today's candidate tools/uuid.py-style
         shadow forges the anchored judge's result in-process.

Named codes frozen here BEFORE the implementation (the H-01a convention):
  ARV-TG-001  invalid/missing driver inputs (a non-absolute or nonexistent
              candidate root; untrusted event/branch metadata)
  ARV-TG-002  a required suite is MISSING from the candidate tree (fail-closed)
  ARV-TG-003  a required suite FAILED (nonzero exit)
  ARV-TG-004  a required suite produced NO output (the A03 vacuous class)
  ARV-TG-005  the BASE's gate machinery is missing/incomplete (anchor refused)

Each test builds a SYNTHETIC candidate git repo that satisfies the BASE gate's
obligations (registry, ledger, red records, declarations, proof sheet, machinery
data files) and flips exactly ONE condition. The driver is invoked exactly the
way CI invokes it: a subprocess, -I, the anchored-copy path, env-only metadata.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DRIVER = REPO / "tools" / "trusted_gate.py"
BRANCH = "slice/claim-xyz-synthetic"
SLICE = "claim-xyz-synthetic"
NOTVERIFIED = "- synthetic stub run — every obligation satisfied by construction\n"

# imported lazily (the real gate module import inserts the real repo root on
# sys.path — fine for the test process, which is NOT the trusted judge)
_REAL_GATE = None


def _base_gate():
    global _REAL_GATE
    if _REAL_GATE is None:
        sys.path.insert(0, str(REPO))
        import importlib.util
        spec = importlib.util.spec_from_file_location("real_gate", REPO / "harness" / "gate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _REAL_GATE = mod
    return _REAL_GATE


def _stub_suite(name: str, *, fail: bool = False, silent: bool = False,
                stderr_only: bool = False) -> str:
    if silent:
        return "# silent stub\n"
    if stderr_only:
        # the unittest-shaped reporter: everything on STDERR, nothing on stdout
        return ("import sys\n"
                "print('unittest-shaped stub: reporting on stderr only', file=sys.stderr)\n"
                "print('Ran 3 tests in 0.1s')\n")
    return ("# synthetic candidate suite (stubbed for the trusted-gate tests)\n"
            f"print('stub suite ok: {name}')\n" + ("raise SystemExit(1)\n" if fail else ""))


def build_stub(td: Path, *, suite_mutations: dict | None = None,
               delete_suite: str | None = None, breach: bool = False,
               gutted_makefile: bool = False, hostile_registry: bool = False,
               drop_base_gate: bool = False) -> Path:
    """A synthetic CANDIDATE git repo satisfying the BASE gate's obligations.
    suite_mutations: {suite_path: file_content} overrides; breach adds an
    UNDECLARED path to the PR commit (ARV-SCOPE-002's target)."""
    stub = td / "candidate"
    stub.mkdir()
    run = lambda *a: subprocess.run(a, cwd=stub, check=True, capture_output=True)
    run("git", "init", "-q", "-b", BRANCH)
    run("git", "config", "user.email", "stub@test.local")
    run("git", "config", "user.name", "Stub")

    # machinery data files (the candidate tree carries them; the trusted run
    # never imports them — the tests prove exactly that)
    for rel in ("harness/proofsheet.py", "harness/scope.py", "harness/claims.py",
                "harness/gate.py", "harness/migrate.py", "harness/__init__.py",
                "harness/adapters/__init__.py", "harness/adapters/clock.py"):
        dst = stub / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((REPO / rel).read_bytes())
    kb = stub / "harness" / "known-bad" / "cases.py"
    kb.parent.mkdir(parents=True, exist_ok=True)
    if hostile_registry:
        kb.write_text("# F-006 payload: if this module ever executes inside a trusted judge, the run exits green early\nimport sys\nsys.exit(0)\n")
    else:
        kb.write_bytes((REPO / "harness" / "known-bad" / "cases.py").read_bytes())

    # the required suites (the BASE's TESTS list, whatever it is at this revision)
    red_records = {}
    for t in _base_gate().TESTS:
        rel = t
        p = stub / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        content = _stub_suite(t)
        if suite_mutations and rel in suite_mutations:
            content = suite_mutations[rel]
        p.write_text(content, encoding="utf-8")
        if delete_suite and rel == delete_suite:
            p.unlink()
        else:
            red_records[rel] = {"current_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                               "amendments": [], "red_evidence": "synthetic stub"}
    (stub / "harness" / "red-records.json").write_text(json.dumps(red_records, indent=2) + "\n")

    # the registry + ledger (valid open claim for BRANCH)
    (stub / "INTENT-LEDGER.md").write_text("**INT-100 — STUB — active**\n\nStatus legend: `active`.\n")
    (stub / "CLAIMS.md").write_text(
        "# CLAIMS (synthetic stub)\n\n## Open claims\n\n"
        "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
        "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        f"| CLAIM-XYZ | 23 | stub | `{BRANCH}` | `notes.txt`, `harness/tests`, `harness/red-records.json`, `CLAIMS.md`, `INTENT-LEDGER.md`, `harness/runs/{SLICE}` | — (synthetic) | 2026-10-20 | the trusted-gate test stub |\n\n"
        "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n")

    # the slice declaration + a real assembled proof sheet (base machinery)
    runs = stub / "harness" / "runs" / SLICE
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "scope.txt").write_text(
        f"# synthetic declaration\nnotes.txt\nharness/tests\nharness/red-records.json\nCLAIMS.md\nINTENT-LEDGER.md\nharness/runs/{SLICE}\n")
    sys.path.insert(0, str(REPO))
    from harness import proofsheet as ps
    ps.RUNS = runs.parent          # RUNS is the runs ROOT — assemble re-joins the slice name
    rec_path = runs / "run-01.json"
    rec_path.write_text(json.dumps({
        "command": "python3 synthetic-stub-suite", "exit_code": 0,
        "commit": "0" * 40, "output_sha256": hashlib.sha256(b"stub output").hexdigest(),
        "recorded_at": "2026-10-20T00:00:00+00:00"}, indent=2) + "\n")
    (runs / "proofsheet.md").write_text(ps.assemble(SLICE, NOTVERIFIED), encoding="utf-8")
    # --verify re-derives the not-verified section from this FILE — the stub
    # must carry it so the re-derivation is byte-identical (PRF-01)
    (runs / "notverified.txt").write_text(NOTVERIFIED, encoding="utf-8")

    # a Makefile whose recipes lie — the driver must never consult it
    mk = stub / "Makefile"
    mk.write_text("harness-tests:\n\t@echo 'FAKE SUCCESS — no suite ran'\nharness-health:\n\t@echo 'FAKE HEALTH'\n"
                   if gutted_makefile else
                   "harness-tests:\n\t@for t in harness/tests/test_*.py; do python3 $$t || exit 1; done\nharness-health:\n\t@echo ok\n")

    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "synthetic base state (the claim row + declarations)")
    (stub / "notes.txt").write_text("the declared PR change\n")
    if breach:
        (stub / "undeclared-secret.txt").write_text("OUTSIDE the declared scope\n")
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "the PR change under test")
    return stub


def run_driver(td: Path, stub: Path, phase: str, *, event: str = "pull_request",
               head: str = BRANCH, diff_ref: str = "HEAD~1",
               repo: str | None = None, base: str | None = None) -> subprocess.CompletedProcess:
    if not DRIVER.is_file():
        raise AssertionError("the trusted driver (tools/trusted_gate.py) does not exist at the predecessor — H-01b-CI's named module is unbuilt")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(td)}
    cmd = [sys.executable, "-I", str(DRIVER),
           "--repo", repo or str(stub), "--base", base or str(REPO),
           "--phase", phase, "--event", event, "--head", head,
           "--diff-ref", diff_ref]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=env)


class TrustedGateTests(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._td = tempfile.TemporaryDirectory(prefix="arvoo-tg-")
        self.td = Path(self._td.name)
        self.addCleanup(self._td.cleanup)

    def test_01_missing_required_suite_is_refused(self):
        """F-004, fail-closed: a required suite deleted from the candidate tree
        is ARV-TG-002 — the trusted selection never silently skips it (the
        candidate Makefile cannot hide a missing suite; recipes are not asked)."""
        stub = build_stub(self.td, delete_suite=_base_gate().TESTS[0], gutted_makefile=True)
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-002", r.stdout + r.stderr)

    def test_02_failing_required_suite_is_refused(self):
        """F-004: a required suite that FAILS is ARV-TG-003 — a gutted Makefile
        cannot fabricate a green (the driver runs the suite files itself)."""
        stub = build_stub(self.td, gutted_makefile=True,
                          suite_mutations={_base_gate().TESTS[1]: _stub_suite("x", fail=True)})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-003", r.stdout + r.stderr)

    def test_03_silent_suite_is_the_vacuous_class(self):
        """A suite that exits 0 with NO output is ARV-TG-004 — the A03 vacuous
        pass class, refused by the trusted completion semantics."""
        stub = build_stub(self.td, suite_mutations={_base_gate().TESTS[0]: _stub_suite("x", silent=True)})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-004", r.stdout + r.stderr)

    def test_04_gutted_makefile_cannot_fake_suites_ran(self):
        """F-004's positive control: the stub's Makefile recipes are LIES (echo
        success, run nothing) yet the driver's suites phase runs every required
        suite file directly and is GREEN only because the real suites pass.
        The suites report STDERR-ONLY (the unittest shape — the part-2 binding
        rehearsal caught the driver's first draft refusing them with a false
        ARV-TG-004: zero-OUTPUT meant zero-STDOUT, and unittest never prints
        there); stderr-only reporters count as evidence on either stream."""
        stub = build_stub(self.td, gutted_makefile=True,
                          suite_mutations={t: _stub_suite(t, stderr_only=True)
                                           for t in _base_gate().TESTS})
        r = run_driver(self.td, stub, "suites")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-500:])
        for t in _base_gate().TESTS:
            self.assertIn(t, r.stdout, "the driver must report each required suite it ran")

    def test_05_gate_phase_reroots_and_judges_the_candidate(self):
        """F-006: the BASE's gate machinery re-rooted over the candidate tree.
        A VALID candidate passes every obligation; a candidate whose PR commit
        carries an UNDECLARED path is refused with ARV-SCOPE-002 — judged by the
        BASE's machinery, never the candidate's own gate."""
        stub = build_stub(self.td, gutted_makefile=True)
        r = run_driver(self.td, stub, "gate")
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("GREEN — the gate passes", r.stdout)
        td2 = Path(str(self.td) + "-breach")
        td2.mkdir()
        stub2 = build_stub(td2, breach=True)
        r2 = run_driver(td2, stub2, "gate")
        self.assertNotEqual(r2.returncode, 0)
        self.assertIn("ARV-SCOPE-002", r2.stdout + r2.stderr)

    def test_06_candidate_knownbad_registry_never_executes_in_the_trusted_run(self):
        """F-006's backstop, the named card case: the candidate's
        harness/known-bad/cases.py is `import sys; sys.exit(0)` — if ANY trusted
        code ever imported it, the run would exit green BEFORE the KB matrix
        prints its case lines. The trusted run must instead complete the WHOLE
        matrix (the BASE's cases judge the candidate) and stay GREEN — the
        candidate registry was never authority."""
        stub = build_stub(self.td, hostile_registry=True, gutted_makefile=True)
        r = run_driver(self.td, stub, "gate")
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("PASS KB-", r.stdout, "the BASE's known-bad matrix must RUN to completion")
        self.assertIn("GREEN — the gate passes", r.stdout)

    def test_07_invalid_inputs_and_hostile_metadata_are_refused(self):
        """ARV-TG-001/005: a relative or nonexistent candidate root, a base
        without gate.py, and hostile branch metadata (the A02 class: data,
        never syntax) are each refused BEFORE anything executes; a hostile
        branch name with shell metacharacters creates NO side-effect file."""
        stub = build_stub(self.td)
        r = run_driver(self.td, stub, "suites", repo="relative/path")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-001", r.stdout + r.stderr)
        r = run_driver(self.td, stub, "gate", head="x; touch " + str(self.td / "pwned"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-001", r.stdout + r.stderr)
        self.assertFalse((self.td / "pwned").exists(), "hostile metadata became shell syntax")
        empty_base = self.td / "empty-base"          # EXISTS but carries no harness/gate.py
        empty_base.mkdir()
        r = run_driver(self.td, stub, "gate", base=str(empty_base))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-005", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
