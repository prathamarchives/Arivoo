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
    """Load the REAL harness/gate.py by file path (the required-suite source
    for the stub trees) — cached for the test process only, which is NOT the
    trusted judge."""
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
    """A synthetic candidate suite file body: the normal shape, the failing
    shape, the zero-output A03 shape, or the unittest-shaped stderr-only
    reporter (R-04(1): its completion line prints to STDERR so the pin
    discriminates a stdout-only-blind driver)."""
    if silent:
        return "# silent stub\n"
    if stderr_only:
        # the unittest-shaped reporter: EVERYTHING on STDERR, nothing on
        # stdout — INCLUDING the completion line (R-04(1): the predecessor's
        # stub printed its 'Ran 3 tests' line to stdout, so a driver that
        # regressed to stdout-only checking still passed this shape — the
        # pin was twice-vacuous; the line moves to stderr so the pin
        # discriminates the exact blindness it exists to guard)
        return ("import sys\n"
                "print('unittest-shaped stub: reporting on stderr only', file=sys.stderr)\n"
                "print('Ran 3 tests in 0.1s', file=sys.stderr)\n")
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


def run_driver(td: Path, stub: Path, phase: str, *, event: str | None = None,
               head: str | None = None, diff_ref: str = "HEAD~1",
               repo: str | None = None, base: str | None = None,
               env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Invoke the driver EXACTLY the way CI invokes it: a subprocess, -I, the
    anchored-copy path, a scrubbed env, and metadata only through the
    environment (the A02 pattern)."""
    if not DRIVER.is_file():
        raise AssertionError("the trusted driver (tools/trusted_gate.py) does not exist at the predecessor — H-01b-CI's named module is unbuilt")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(td)}
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, "-I", str(DRIVER),
           "--repo", repo or str(stub), "--base", base or str(REPO),
           "--phase", phase, "--diff-ref", diff_ref]
    if event is not None:
        cmd += ["--event", event]
    if head is not None:
        cmd += ["--head", head]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=env)


class TrustedGateTests(unittest.TestCase):

    def setUp(self):
        """A fresh scratch dir per test (the stub trees are disposable)."""
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
        cannot fabricate a green (the driver runs the suite files itself).
        R-04(3): the refusal carries a BOUNDED TAIL of the failing suite's
        captured output — the predecessor discarded it, so the suite's own
        named failure was invisible in the trusted evidence (Greptile: 'a
        bounded tail prints with the refusal')."""
        stub = build_stub(self.td, gutted_makefile=True,
                          suite_mutations={_base_gate().TESTS[1]: _stub_suite("x", fail=True)})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-003", r.stdout + r.stderr)
        self.assertIn("stub suite ok: x", r.stdout + r.stderr,
                      "the failing suite's captured output was DISCARDED — the refusal "
                      "must carry a bounded tail so the named failure is visible in the "
                      "trusted evidence (R-04(3))")

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
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("GREEN — the gate passes", r.stdout)
        td2 = Path(str(self.td) + "-breach")
        td2.mkdir()
        stub2 = build_stub(td2, breach=True)
        r2 = run_driver(td2, stub2, "gate", event="pull_request", head=BRANCH)
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
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
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
        r = run_driver(self.td, stub, "gate", event="pull_request",
                       head="x; touch " + str(self.td / "pwned"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-001", r.stdout + r.stderr)
        self.assertFalse((self.td / "pwned").exists(), "hostile metadata became shell syntax")
        empty_base = self.td / "empty-base"          # EXISTS but carries no harness/gate.py
        empty_base.mkdir()
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH,
                       base=str(empty_base))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-005", r.stdout + r.stderr)

    def test_08_env_only_invocation_is_the_ci_form(self):
        """The CI form: metadata arrives through ARV_EVENT_NAME/ARV_PR_HEAD with
        NO --event/--head flags (the dispatch.py precedent). At the predecessor
        the call site passed the RAW argparse values — an env-only invocation
        handed the gate phase None and refused with a false ARV-TG-001 (found
        live by the S4c binding rehearsal; the other tests never caught it
        because they pass explicit flags). The env-only invocation must reach
        and pass the re-rooted gate, identically to the flag form."""
        stub = build_stub(self.td, gutted_makefile=True)
        r = run_driver(self.td, stub, "gate",
                       env_extra={"ARV_EVENT_NAME": "pull_request",
                                  "ARV_PR_HEAD": BRANCH})
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("GREEN — the gate passes", r.stdout)
        self.assertNotIn("ARV-TG-001", r.stdout + r.stderr,
                         "the env-only form must never be refused as None-metadata")

    def test_09_s4c_step_runs_even_when_s4b_fails(self):
        """R-04(2): the TRUSTED S4c step must carry `!cancelled()` — a plain
        workflow step is SKIPPED by GitHub Actions after any earlier failure,
        so a red S4b (the candidate's own gate, EVIDENCE since H-01b-CI)
        silently skipped the trusted re-run and the trusted evidence never
        flowed. The step's if-condition keeps S4c running over a red S4b
        (Greptile's finding; the pin parses the workflow file itself — the
        artifact under repair, never a copy). REGEX (LAW-11, corrected
        in-slice): the S4c name line is a LONG quoted string — the first
        draft's pattern expected the name to close right after "S4c and
        matched ZERO continuation lines, so the pin was vacuous against the
        real artifact shape; `[^\n]*` first consumes the name line, then the
        step group takes the 8+-space property lines (the next step's
        6-space `- name:` stops the group)."""
        import re
        wf = (REPO / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
        m = re.search(r"- name: \"S4c[^\n]*(?P<step>(?:\n[ ]{8,}[^\n]*)*)", wf)
        self.assertTrue(m, "the S4c step must exist in the verify workflow")
        step = m.group("step")
        self.assertIn("if:", step, "the S4c step group captured no property lines — the "
                     "pin must parse the real workflow shape, never match an empty group")
        cond = re.search(r"(?m)^[ ]{8}if:\s*\$\{\{\s*(?P<expression>[^}\n]+?)\s*\}\}\s*$", step)
        self.assertIsNotNone(cond, "the S4c step must define an executable if: expression")
        expression = cond.group("expression")
        self.assertIn("!cancelled()", expression,
                      "the S4c if-expression lacks `!cancelled()` — a failed S4b would SKIP "
                      "the trusted gate re-run, and the trusted evidence would never flow "
                      "(R-04(2))")
        self.assertIn("steps.checkout_base.outcome == 'success'", expression,
                      "the S4c if-expression must guard on the base checkout succeeding — a "
                      "skipped anchor leaves no anchored driver and a bare !cancelled() "
                      "executes a candidate-committed substitute (#64's Major)")
        self.assertIn("steps.anchor_trusted_gate.outcome == 'success'", expression,
                      "the S4c if-expression must guard on the anchor step succeeding — the "
                      "sha256-verified anchoring is what makes the driver trusted")
        self.assertNotIn("success()", expression,
                         "the success() function would skip S4c on a red S4b — the exact defect")
        # the #64 SECOND review round (CodeRabbit TOCTOU): S4b runs candidate-
        # controlled Python in the same writable workspace, so the anchored
        # driver is RE-VERIFIED at S4c ENTRY (the direct swap-after-anchor
        # channel refuses); the same-job base-machinery residual is R-06's
        # card, named in the workflow comment, never claimed closed here.
        self.assertIn("sha256sum", step,
                      "the S4c run block must re-verify the anchored driver's digest against "
                      "base at entry — the post-anchor driver-swap refuses (the #64 TOCTOU "
                      "round's in-PR hardening)")
        self.assertIn("post-anchor tampering refused", step,
                      "the re-verification's refusal line must be pinned by name")

    def test_10_bounded_tail_keeps_the_end_of_the_output(self):
        """R-04(3) + the #64 review round (Greptile P2 + CodeRabbit,
        independently confirmed): the ARV-TG-003 bounded tail keeps the LAST
        1500 characters — a failing suite's named failure lives at the END of
        its output (unittest reports the traceback and verdict last), so a
        head-window drops the diagnostic behind long normal stdout. The stub
        prints a long normal prefix, then the failure marker."""
        long_stub = ("for i in range(200):\n"
                     "    print('normal output line: ' + str(i))\n"
                     "print('THE-NAMED-FAILURE-MARKER-AT-THE-END')\n"
                     "raise SystemExit(1)\n")
        stub = build_stub(self.td, suite_mutations={_base_gate().TESTS[1]: long_stub})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-003", r.stdout + r.stderr)
        self.assertIn("THE-NAMED-FAILURE-MARKER-AT-THE-END", r.stdout + r.stderr,
                      "the bounded tail kept the FIRST 1500 chars — the marker at the END "
                      "of the output was dropped behind the long normal prefix (the #64 "
                      "review round's head-window defect)")
        self.assertIn("the LAST 1500 kept", r.stdout + r.stderr,
                      "the truncation marker must state which window was kept")


if __name__ == "__main__":
    unittest.main(verbosity=2)
