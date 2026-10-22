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
        runs = self.td / "harness" / "runs" / "claim-x"     # check_scope reads REPO/harness/runs/<slice>/scope.txt
        runs.mkdir(parents=True, exist_ok=True)
        (runs / "scope.txt").write_text("README.md\n")
        old = scope.REPO
        scope.REPO = self.td
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
        --name-only shows only the destination. The renamed file must exist
        in the BASE commit — an add-then-rename chain collapses to a plain
        add and carries no rename record."""
        repo = self.td / "repo"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.email", "t@t.local")
        _git(repo, "config", "user.name", "T")
        (repo / "old-name.txt").write_text("content\n")
        (repo / "base.txt").write_text("base\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "base (old-name.txt lives here)")
        _git(repo, "checkout", "-q", "-b", "slice/claim-x-synthetic")
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

    # -- R-04(4): the numstat TAB split ---------------------------------------

    def test_06_numstat_path_with_tab_survives_the_stats_parse(self):
        """A changed path containing a literal TAB must arrive WHOLE in the
        stats identity. The -z numstat record is 'added<TAB>deleted<TAB>path';
        the predecessor split on EVERY tab, so a tab inside the path truncated
        it to the fragment before the tab (identity mangled, classification
        wrong) — Greptile's finding on the H-01c-claims diff."""
        tabname = "ta\tb.py"                    # a .py file whose NAME carries a literal tab
        repo = build_repo(self.td, {tabname: "print('x')\n"})
        stats = scope.diff_stats("main", repo=repo)
        hit = [d for d in stats if d["path"] == tabname]
        self.assertTrue(hit, f"the tab-bearing path was truncated by the tab split: "
                             f"{[d['path'] for d in stats]}")
        self.assertEqual(hit[0]["src_lines"], 1, "the tab path must classify as a SOURCE file")

    # -- R-04(5): -z output is BYTES + surrogateescape (identity preserved) ----

    def test_07_non_utf8_path_identity_preserved(self):
        """A path git stores as non-UTF-8 bytes must pass through BOTH diff
        identities without a UnicodeDecodeError crash and without byte
        rewriting. The predecessor read the -z output TEXT-MODE (strict locale
        codec): the raw byte 0xE9 crashed the decode — Greptile's finding."""
        raw = b"caf\xe9.py"                      # latin-1 'café.py' — invalid UTF-8
        repo = self.td / "repo"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.email", "t@t.local")
        _git(repo, "config", "user.name", "T")
        (repo / "base.txt").write_text("base\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "base")
        _git(repo, "checkout", "-q", "-b", "slice/claim-x-synthetic")
        p = repo / os.fsdecode(raw)              # the OS round-trips the surrogate escape to the raw bytes
        p.write_text("print('x')\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "the non-utf8 path change")
        stats = scope.diff_stats("main", repo=repo)
        self.assertEqual(len(stats), 1, f"the path must arrive as exactly one record: {stats}")
        self.assertEqual(stats[0]["path"].encode("utf-8", "surrogateescape"), raw,
                         "the byte identity was rewritten on the way through the diff parse")
        paths = scope.diff_paths("main", repo=repo)
        self.assertEqual([os.fsencode(pp) for pp in paths], [raw],
                         "the changed-path identity must carry the exact bytes")

    def test_08_cr_in_path_identity_preserved(self):
        """A path containing a literal CR must arrive byte-identical. The
        predecessor's TEXT-MODE read applied universal-newline translation:
        the raw \\r inside the filename was rewritten to \\n — identity
        corrupted (Greptile's finding: 'bytes + surrogateescape, identity
        preserved')."""
        crname = "line\rending.py"               # a literal CR inside the name
        repo = build_repo(self.td, {crname: "print('x')\n"})
        stats = scope.diff_stats("main", repo=repo)
        self.assertEqual([d["path"] for d in stats], [crname],
                         "the CR was rewritten by universal-newline translation")
        paths = scope.diff_paths("main", repo=repo)
        self.assertEqual(paths, [crname], "the CR-in-name identity was corrupted")

    # -- R-04(6): the rename double-count --------------------------------------

    def test_09_rename_counts_added_lines_once_under_the_destination(self):
        """A rename+modify counts its added lines ONCE, under the DESTINATION
        only. The predecessor emitted the FULL added count on BOTH rename
        endpoints — every rename double-counted its lines into the size gate
        (Greptile's finding)."""
        repo = self.td / "repo"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.email", "t@t.local")
        _git(repo, "config", "user.name", "T")
        (repo / "old-name.py").write_text("x = 1\n" * 10, encoding="utf-8")
        (repo / "base.txt").write_text("base\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "base (old-name.py lives here)")
        _git(repo, "checkout", "-q", "-b", "slice/claim-x-synthetic")
        _git(repo, "mv", "old-name.py", "new-name.py")
        (repo / "new-name.py").write_text("x = 1\n" * 40, encoding="utf-8")   # +30 added lines
        _git(repo, "commit", "-q", "-m", "rename plus modify")
        stats = scope.diff_stats("main", repo=repo)
        total = sum(d["src_lines"] for d in stats)
        self.assertEqual(total, 30, f"the rename double-counted its added lines (total {total} != 30): {stats}")

    # -- R-04(9): the intra-table duplicate ratchet -----------------------------

    def test_10_closed_table_duplicate_refuses(self):
        """The same claim ID TWICE in one table is drift too — the duplicate
        CLAIM-021 closed rows (G-58-1) survived every check because ARV-CLM-006
        covers only the BOTH-TABLES drift. check_registry must refuse
        ARV-CLM-007 on an intra-table duplicate (the ratchet's check side; the
        probe side is KB-CLM-007)."""
        repo = self.td / "reg"
        repo.mkdir()
        (repo / "INTENT-LEDGER.md").write_text("**INT-100 — STUB — active**\n")
        (repo / "CLAIMS.md").write_text(
            "# CLAIMS\n\n## Open claims\n\n"
            "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
            "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n\n"
            "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n"
            "| CLAIM-XX | landed | 2026-10-19 | PR #1 |\n"
            "| CLAIM-XX | landed again | 2026-10-19 | PR #1 |\n",
            encoding="utf-8")
        fails = claims.check_registry(repo=repo)
        self.assertTrue(any("ARV-CLM-007" in f for f in fails),
                        "the intra-table duplicate must refuse — the duplicate CLAIM-021 closed-row class")


if __name__ == "__main__":
    unittest.main(verbosity=2)
