#!/usr/bin/env python3
r"""tools/trusted_gate.py — H-01b-CI's trusted-CI driver (F-004/F-006; INT-127/D-041).

Base-owned machinery. NO required check's green result may depend solely on code
the PR candidate controls or edits, so CI anchors this module from main (the
sha256-verified anchored copy) and launches it with `python3 -I` — no script-dir
on sys.path, no PYTHONPATH: a candidate tools/<stdlib>.py shadow cannot reach
this interpreter (the FLOOR-REVIEW-1 B2 quantification: under the old launch a
candidate tools/uuid.py executed IN the trusted judge and forged a full GREEN).

Two phases, both over the CANDIDATE tree as DATA:

  suites  F-004: the required suites are selected from the BASE's gate.TESTS
          (trusted state — never the candidate's Makefile or its own TESTS
          tuple) and the candidate's own suite FILES are run directly as
          subprocesses; a missing suite (ARV-TG-002), a failing suite
          (ARV-TG-003), or a silent zero-output suite (ARV-TG-004 — the A03
          vacuous class) each refuse. Candidate Make recipes are never asked:
          a gutted Makefile cannot fabricate "suites ran".

  gate    F-006: the BASE's gate machinery (gate/scope/claims/proofsheet,
          spec-loaded from the base dir — never the candidate's harness
          package) is re-rooted over the candidate tree via ARV_TRUSTED_ROOT
          and re-runs the PR-mode obligations (scope/size/claims/red/lint/deps/
          known-bads/proofsheet) over the candidate diff. The candidate's own
          known-bad registry never executes inside this run; its own gate's
          green is never the only evidence for the harness check.

Named codes (frozen in harness/tests/test_trusted_gate.py BEFORE this
implementation):
  ARV-TG-001  invalid/missing driver inputs (non-absolute or nonexistent
              candidate root; untrusted event/branch metadata — identifiers
              only, the dispatch A02 pattern)
  ARV-TG-002  a required suite is MISSING from the candidate tree (fail-closed)
  ARV-TG-003  a required suite FAILED
  ARV-TG-004  a required suite produced NO output (the vacuous class)
  ARV-TG-005  the BASE's gate machinery is missing/incomplete (anchor refused)

Residual, stated (never claimed closed): same-host same-user children — the
known-bad probes executed by the base's gate load the candidate's harness
modules in-process (their early-exit/crash forms fail closed by the gate's own
`except SystemExit` + expected-code logic, and in-process tampering is the
documented same-user boundary, never a sandbox claim); the pull_request event's
workflow definition itself remains PR-controlled (F-003 — GitHub has no repo
setting that changes this; observed settings recorded in the slice's evidence:
workflow token permissions read-only + cannot-approve, branch protection
three-check enforcement for everyone). Q10 remains owner-gated.

Usage (the workflow's exact form — all paths absolute, metadata via ARGUMENTS,
validated as identifiers before anything executes):
  python3 -I tools/trusted_gate_anchored.py --repo <candidate> --base <base> \
      --phase suites|gate --event pull_request --head slice/claim-x-slug \
      [--diff-ref origin/main]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

SAFE_REF = re.compile(r"^[A-Za-z0-9._/~^-]+$")
SAFE_SLICE = re.compile(r"^[A-Za-z0-9._-]+$")
EVENTS = ("pull_request", "push")
SUITE_TIMEOUT = 1800


def _refuse(code: str, what: str, repair: str) -> "None":
    print(f"FAIL {code}: {what}")
    print(f"      repair: {repair}")
    sys.exit(1)


def _valid_root(value: str, what: str, code: str = "ARV-TG-001") -> Path:
    p = Path(value or "")
    if not p.is_absolute():
        _refuse(code, f"the {what} must be an ABSOLUTE path (got a relative value) — re-rooting on a relative path is never deterministic", "CI passes $PWD-derived absolute paths; a relative root is refused before anything executes")
    if not p.is_dir():
        _refuse(code, f"the {what} is not an existing directory — re-rooting onto nothing is refused (fail-closed)", "verify the checkout steps ran before this step")
    return p


def _load_base_gate(base: Path):
    gp = base / "harness" / "gate.py"
    if not gp.is_file():
        _refuse("ARV-TG-005", "the BASE's gate machinery is missing (harness/gate.py not found under the base dir) — refusing to run any candidate-substituted gate", "the workflow anchors the trusted driver from main; the base checkout must precede this step")
    spec = importlib.util.spec_from_file_location("arv_base_gate", gp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)   # gate.py inserts the BASE root on sys.path itself: its harness imports resolve to the BASE package, never the candidate's
    return mod


def _phase_suites(repo: Path, base: Path) -> int:
    gate = _load_base_gate(base)
    required = getattr(gate, "TESTS", None)
    if not required:
        _refuse("ARV-TG-005", "the BASE's gate exposes no required-suite list (TESTS) — the trusted selection cannot run", "the base machinery is the authority for the required set; refuse rather than inventing one")
    print(f"trusted suites phase (F-004): {len(required)} required suite(s), selected from the BASE's gate.TESTS — candidate Make recipes are never the evidence")
    env = os.environ.copy()
    for t in required:
        suite = repo / t
        if not suite.is_file():
            _refuse("ARV-TG-002", f"required suite MISSING from the candidate tree: {t} — a deleted or renamed suite is a skipped suite (fail-closed, never a silent pass)", "restore the suite file; deleting a required suite is a constraint-weakening change (LAW-09 class)")
        try:
            r = subprocess.run([sys.executable, t], cwd=repo, env=env,
                               capture_output=True, text=True, timeout=SUITE_TIMEOUT)
        except subprocess.TimeoutExpired:
            _refuse("ARV-TG-003", f"required suite {t} exceeded the {SUITE_TIMEOUT}s timeout — a hung suite is a failed suite, never a green", "run the suite directly for its named failure and repair it")
        if r.returncode != 0:
            # R-04(3): the refusal carries a BOUNDED TAIL of the failing
            # suite's captured output — the predecessor discarded it, so the
            # suite's own named failure was invisible in the trusted evidence
            # (Greptile: 'a bounded tail prints with the refusal'). The tail is
            # bounded by characters (never an unbounded capture printed whole)
            # and clearly fenced as the suite's own output, never the judge's
            tail = ((r.stdout or "") + "\n" + (r.stderr or "")).strip()
            if len(tail) > 1500:
                tail = tail[:1500] + " [...truncated at 1500 chars]"
            _refuse("ARV-TG-003", f"required suite FAILED: {t} (exit {r.returncode}) — a candidate recipe cannot fabricate a green over a red suite"
                    + (f"; the suite's own captured output (bounded tail):\n      {tail}" if tail else ""),
                    "run the suite directly for its named failure and repair it")
        if not r.stdout.strip() and not r.stderr.strip():
            # stdout OR stderr counts: unittest-based suites report to STDERR
            # (found live by the part-2 binding rehearsal — the first driver
            # draft was unittest-blind and refused every real suite with a
            # false ARV-TG-004; the silent-stub regression still refuses a
            # genuinely zero-output suite on BOTH streams)
            _refuse("ARV-TG-004", f"required suite {t} produced NO output on either stream with exit 0 — the A03 vacuous class (zero output is never proof the cases ran)", "the suite must report what it ran; a silent exit-0 stub is refused")
        print(f"  PASS {t} — exit 0, non-empty output (ran as a subprocess over the candidate tree)")
    print("SUITES GREEN — every required suite ran directly and passed (trusted selection; recipes never consulted)")
    return 0


def _phase_gate(repo: Path, base: Path, event: str, head: str, diff_ref: str) -> int:
    # identifiers only — the A02 pattern: untrusted metadata is DATA, never
    # syntax (the workflow delivers it via ENV, exactly like dispatch.py; the
    # argparse flags exist for the tests' explicit invocations)
    if event not in EVENTS:
        _refuse("ARV-TG-001", f"untrusted event metadata: {event!r} is not one of {EVENTS}", "the workflow passes github.event_name via env; an unknown event is never guessed")
    if event == "pull_request":
        slice_name = head[len("slice/"):] if head.startswith("slice/") else head
        if not slice_name or not SAFE_SLICE.match(slice_name):
            _refuse("ARV-TG-001", f"untrusted branch metadata rejected as data: {head!r} does not derive to a safe slice identifier", "branch names carry the claim id (slice/<claim-id>-<slug>, D-038); hostile metadata is refused before any gate execution")
    if not SAFE_REF.match(diff_ref):
        _refuse("ARV-TG-001", f"untrusted diff ref rejected as data: {diff_ref!r} is not a safe git ref token", "the diff base is a fixed ref (origin/main in CI, HEAD~1 in tests)")
    # re-root the BASE's machinery onto the candidate tree BEFORE the import
    os.environ["ARV_TRUSTED_ROOT"] = str(repo)
    gate = _load_base_gate(base)
    print(f"trusted gate phase (F-006): the BASE's gate machinery re-rooted over the candidate tree (ARV_TRUSTED_ROOT set before import); the candidate's harness package and its known-bad registry never load in this process")
    if event == "push":
        argv = ["gate.py", "--no-diff", "--skip-suites"]
        print("dispatch: push event -> main selfcheck over the re-rooted tree")
    else:
        argv = ["gate.py", "--slice", slice_name, "--diff", diff_ref, "--skip-suites"]
        print(f"dispatch: pull_request event -> PR mode (slice={slice_name}, diff={diff_ref}) — the candidate is judged as a PR by the BASE's machinery")
    old_argv, sys.argv = sys.argv, argv
    try:
        rc = gate.main()
    finally:
        sys.argv = old_argv
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="H-01b-CI trusted gate driver")
    ap.add_argument("--repo", required=True, help="the CANDIDATE tree (absolute path; data, never authority)")
    ap.add_argument("--base", required=True, help="the BASE checkout (absolute path; the trusted machinery's home)")
    ap.add_argument("--phase", required=True, choices=("suites", "gate"))
    # untrusted metadata arrives via ENV in CI (the dispatch.py precedent: env is
    # data, never shell); the explicit flags serve the tests' invocations
    ap.add_argument("--event", default=None, help="github.event_name (env ARV_EVENT_NAME; identifier-validated)")
    ap.add_argument("--head", default=None, help="github.head_ref (env ARV_PR_HEAD; identifier-validated for pull_request)")
    ap.add_argument("--diff-ref", default="origin/main", help="the diff base ref (identifier-validated)")
    a = ap.parse_args()
    event = a.event or os.environ.get("ARV_EVENT_NAME", "")
    head = a.head if a.head is not None else os.environ.get("ARV_PR_HEAD", "")
    repo = _valid_root(a.repo, "candidate tree (--repo)")
    base = _valid_root(a.base, "base checkout (--base)")
    if a.phase == "suites":
        return _phase_suites(repo, base)
    # the resolved locals (env-backed), never the raw argparse values — an
    # env-only invocation (exactly how CI calls this driver) passed None at
    # the call site before this repair and the gate phase refused with a
    # false ARV-TG-001 (found live by the S4c binding rehearsal; pinned by
    # test_08)
    return _phase_gate(repo, base, event, head, a.diff_ref)


if __name__ == "__main__":
    sys.exit(main())
