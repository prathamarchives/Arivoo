#!/usr/bin/env python3
"""harness/dispatch.py — the CI gate dispatcher (H-01a; INT-125/D-039; A01/A02).

The workflow's S4b step calls THIS module instead of interpolating event
fields into a generated shell script (A02: github.head_ref reached a `run:`
block as template text — a Git-legal hostile branch name could become shell
syntax). Context arrives via ENVIRONMENT only; every untrusted value is
validated as an identifier before anything executes (ARV-DISPATCH-001).

Fail-closed contract (A01): on a pull request the gate ALWAYS runs in PR mode
(--slice + --diff) — a PR whose scope/claim/sheet obligations are missing is
REFUSED by the gate's existing named codes (ARV-SCOPE-001 / ARV-CLM-005 /
ARV-PRF-002). The main-selfcheck surface exists ONLY for push events; it is
never a fallback that bypasses PR obligations.

Git failures are refusals (A10, via harness/scope.py): ARV-DIFF-001 (a failed
git operation — never an empty-diff vacuous pass) / ARV-DIFF-002 (no
merge-base between the declared base and HEAD).

Exit code: the gate's own exit code (forwarded); a dispatch refusal is 1.
"""
import os
import re
import subprocess
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
SAFE_SLICE = re.compile(r"^[A-Za-z0-9._-]+$")
EVENTS = ("pull_request", "push")


def _refuse(code: str, what: str, repair: str) -> "None":
    print(f"FAIL {code}: {what}")
    print(f"      repair: {repair}")
    sys.exit(1)


def main() -> int:
    event = os.environ.get("ARV_EVENT_NAME", "")
    if event not in EVENTS:
        _refuse("ARV-DISPATCH-001",
                f"untrusted event metadata: ARV_EVENT_NAME={event!r} is not one of {EVENTS}",
                "the workflow passes github.event_name through env only — an unknown event is never guessed")
    if event == "push":
        # the main-selfcheck surface: pushes to main only, never a PR fallback
        cmd = [sys.executable, "harness/gate.py", "--no-diff", "--skip-suites"]
        print("dispatch: push event -> main selfcheck (the PR-only obligations do not apply to a push)")
    else:
        head = os.environ.get("ARV_PR_HEAD", "")
        slice_name = head[len("slice/"):] if head.startswith("slice/") else head
        if not slice_name or not SAFE_SLICE.match(slice_name):
            _refuse("ARV-DISPATCH-001",
                    f"untrusted branch metadata rejected as data: {head!r} does not derive to a safe slice identifier",
                    "branch names carry the claim id (slice/<claim-id>-<slug>, D-038); hostile metadata is refused before any gate execution (A02)")
        # the suites already ran in this job (the S1 step: make harness-health
        # + make harness-tests); --skip-suites is legal exactly because their
        # successful results are bound within this same trusted execution.
        cmd = [sys.executable, "harness/gate.py", "--slice", slice_name,
               "--diff", "origin/main", "--skip-suites"]
        print(f"dispatch: pull_request event -> PR mode (slice={slice_name}, diff=origin/main) — a PR is judged as a PR, never selfchecked")
    r = subprocess.run(cmd, cwd=REPO, timeout=3000)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
