#!/usr/bin/env python3
"""harness/tests/test_claims_paths.py — H-01c-claims' RED-first suite (F-001/F-008/ARV-CLM-006).

The three named defects, each with its minimal repro turned into a stable
regression (owner turn 22 §5.1, INT-127/D-041; the session-22 preflight
findings that survived three diff-scoped PRs):

  F-001  the changed-path identity is parsed from HUMAN-format git output
         (quoted filenames mangle; renames show one endpoint), and the
         scope-matching primitive has the sibling-prefix collision: a
         declaration for README.md matches README.md.unrelated through raw
         startswith.
  F-008  claims are enforced by the CONTRIBUTOR-CHOSEN slice name: a PR-diff
         invocation carrying --slice main-selfcheck hits gate.py's exemption
         and skips the branch-claim checks entirely.
  ARV-CLM-006  registry-wide duplicate detection: a claim ID in BOTH the open
         and closed tables is invisible to the diff-scoped checks (the
         CLAIM-007 drift survived three PRs).

All fixtures are self-contained synthetic git repos (real `git diff` output —
no string fixtures pretending to be git).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from harness import claims, scope  # noqa: E402


def _git(repo: Path, *args):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, f"git {args[:2]} failed: {r.stderr[:200]}"
    return r.stdout


def build_repo(td: Path, files: dict[str, str], branch: str = "slice/claim-x-synthetic") -> Path:
    repo = td / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t.local")
    _git(repo, "config", "user.name", "T")
    (repo / "base.txt").write_text("base\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "checkout", "-q", "-b", branch)
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "the pr change")
    return repo


class ClaimsPathTests(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="arvoo-h01c-")
        self.td = Path(self._td.name)
        self.addCleanup(self._td.cleanup)

    # -- F-001: the sibling-prefix collision ---------------------------------

    def test_01_sibling_prefix_never_matches(self):
        """A declaration for README.md must cover EXACTLY README.md — never
        README.md.unrelated. At the predecessor the raw startswith accepts the
        sibling prefix and the out-of-scope change slips through uncovered."""
        repo = build_repo(self.td, {"README.md.unrelated": "sibling\n"})
        decl = repo / "decl"
        decl.mkdir()
        (decl / "scope.txt").write_text("README.md\n")
        old = scope.REPO
        scope.REPO = decl.parent
        try:
            fails = scope.check_scope(["README.md.unrelated"], "claim-x")
        finally:
            scope.REPO = old
        self.assertTrue(any("ARV-SCOPE-002" in f for f in fails),
                        "the sibling-prefix path slipped past the declaration")

    # -- F-001: the machine-safe path identity --------------------------------

    def test_02_exotic_names_survive_the_diff_parse(self):
        """A changed path with SPACES and UNICODE must arrive in the identity
        as the exact bytes git stores — the human format quotes and mangles
        them (quoted names arrive wrapped, a newline-in-name splits lines)."""
        weird = "a dir with spaces/türış–name.txt"
        repo = build_repo(self.td, {weird: "x\n"})
        paths = scope.diff_paths("main", repo=repo)
        self.assertIn(weird, paths, f"the exotic path was mangled by the diff parse: {paths}")

    def test_03_rename_endpoints_are_both_in_the_identity(self):
        """A rename's OLD path is part of the changed-path identity too: a
        declaration covering only the old name must see the change (and a
        scope check over the new name must see it). The predecessor's
        --name-only shows only the destination."""
        repo = build_repo(self.td, {"old-name.txt": "content\n"})
        _git(repo, "mv", "old-name.txt", "new-name.txt")
        _git(repo, "commit", "-q", "-m", "rename")
        paths = scope.diff_paths("main", repo=repo)
        self.assertIn("old-name.txt", paths,
                      "the rename's OLD endpoint is missing from the identity")
        self.assertIn("new-name.txt", paths)

    # -- F-008: claims by trusted invocation mode ------------------------------

    def test_04_main_selfcheck_name_never_disables_claims(self):
        """A PR-diff invocation carrying --slice main-selfcheck must still
        enforce the open-claim requirement (ARV-CLM-005): the invocation MODE
        is trusted state, never the contributor-selected slice label."""
        repo = build_repo(self.td, {"notes.txt": "x\n"})
        registry = repo / "CLAIMS.md"
        registry.write_text(
            "# CLAIMS\n\n## Open claims\n\n"
            "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
            "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
            "| CLAIM-OTHER | 23 | stub | `slice/claim-other-x` | `zzz.txt` | — | 2026-10-20 | none |\n\n"
            "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n",
            encoding="utf-8")
        old = claims.REPO
        claims.REPO = repo
        try:
            fails = claims.check_branch_claim("slice/claim-x-synthetic", ["notes.txt"], repo=repo)
        finally:
            claims.REPO = old
        self.assertTrue(any("ARV-CLM-005" in f for f in fails),
                        "the branch carries NO claim — unclaimed work must refuse regardless of the slice label")
        # and the same registry under a slice NAME of main-selfcheck at the
        # GATE level: the exemption is gone (checked via the gate's condition,
        # pinned here so the condition cannot silently return)
        import inspect
        src = inspect.getsource(scope) + inspect.getsource(claims)
        import harness.gate as gate
        src += inspect.getsource(gate)
        self.assertNotIn('"main-selfcheck",)', src.replace(")", ")"),
                        "the slice-name exemption must not reappear in the gate's claim enforcement")

    # -- ARV-CLM-006: registry-wide duplicate detection -----------------------

    def test_05_open_and_closed_duplicate_refuses(self):
        """A claim ID present in BOTH tables is registry drift — the
        diff-scoped checks missed exactly this for three PRs (CLAIM-007).
        check_registry must sweep the WHOLE registry and refuse ARV-CLM-006."""
        repo = self.td / "reg"
        repo.mkdir()
        (repo / "INTENT-LEDGER.md").write_text("**INT-100 — STUB — active**\n")
        (repo / "CLAIMS.md").write_text(
            "# CLAIMS\n\n## Open claims\n\n"
            "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
            "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
            "| CLAIM-DUP | 23 | stub | `slice/claim-dup-x` | `a.txt` | — | 2026-10-20 | the drift |\n\n"
            "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n"
            "| CLAIM-DUP | landed earlier | 2026-10-19 | PR #1 |\n",
            encoding="utf-8")
        fails = claims.check_registry(repo=repo)
        self.assertTrue(any("ARV-CLM-006" in f for f in fails),
                        "the both-tables duplicate is registry drift and must refuse")


if __name__ == "__main__":
    unittest.main(verbosity=2)
