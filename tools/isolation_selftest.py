#!/usr/bin/env python3
r"""isolation_selftest.py — the W-03 self-test, as a separately-invocable module.

Extracted from tools/isolation_check.py (session 17, D-035 — the candidate-tool gate
repair): the TEST SUITE and the IMPLEMENTATION can now be anchored independently,
so the base-anchored CI job runs THIS suite (from main) against the CANDIDATE's
isolation_check.py — the coordinated-weakening floor (a PR that weakens the
checker AND its own self-test together fails these cases in the required job).

The suite invokes tools/isolation_check.py as a SUBPROCESS (implementation-
agnostic: it judges whatever checker file sits beside this module). Content and
semantics are moved verbatim from the v2.1 checker (18 cases; counts unchanged):
negative cases exit 1 with an attributable RED, positives exit 0, canaries never
appear in stdout/stderr, harness crash paths print sanitized lines only.

Usage: python3 tools/isolation_selftest.py   (or isolation_check.py --self-test,
which delegates here for backward compatibility with the recorded commands).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- self-test (Slice 10.2)
# The COMPLETE diagnostic path, exercised on synthetic fixtures in temporary
# repositories, run as subprocesses exactly as CI invokes the checker. Every case
# asserts BOTH the exit code AND an attributable RED/GREEN line AND that the
# synthetic canary value never appears in stdout/stderr — including the
# harness's own crash paths (a self-test exception prints a sanitized line,
# never a traceback that could carry a canary: falsification finding 11).

CANARY_TRACKED = "ghp_" + "A" * 36            # synthetic classic-PAT shape, tracked file
CANARY_ENV = "gho_" + "B" * 36                # synthetic OAuth-token shape, env var value
CANARY_REMOTE = "ghp_" + "C" * 36             # synthetic PAT shape, embedded in a remote URL

CI_LEGIT = {
    "CI": "true",
    "GITHUB_ACTIONS": "true",
    "GITHUB_SHA": "0" * 40,                    # synthetic, not a secret
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_REPOSITORY": "prathamarchives/Arivoo",
    "RUNNER_OS": "Linux",
}


def _fixture() -> Path:
    """A synthetic repository: the real tree (minus .git), re-initialized as a fresh
    git repo with all files staged, so ls-files and remote probes operate on real
    tracked content. Synthetic mutations are applied per-case on top of this."""
    td = Path(tempfile.mkdtemp(prefix="arivoo-iso-"))
    fix = td / "repo"
    shutil.copytree(REPO, fix, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    subprocess.run(["git", "init", "-q"], cwd=fix, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=fix, check=True, capture_output=True)
    return fix


def _run_checker(fix: Path, args: list[str], case_env: dict[str, str]) -> tuple[int, str, str]:
    """Invoke the FIXTURE's own checker (the copy under test) as a subprocess with a
    controlled environment — PATH is preserved so git itself resolves; nothing else
    leaks in from the live environment."""
    merged = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    merged.update(case_env)
    r = subprocess.run(
        [sys.executable, str(fix / "tools" / "isolation_check.py"), *args],
        cwd=fix, env=merged, capture_output=True, text=True, timeout=120,
    )
    return r.returncode, r.stdout, r.stderr


def self_test() -> int:
    """The Slice 10.2 matrix: negative cases must exit 1 with an attributable RED
    line; positive cases must exit 0 with GREEN; canaries must NEVER appear in
    stdout or stderr; the harness's own failures print sanitized lines only."""

    # (prepare, args, env, expected_exit, canaries, required_output_fragments)
    # NOTE (self-reference guard): the fixture contents below are built by string
    # CONCATENATION so the checker's own source never literally contains a
    # keyword=value shape that the generic secret-assignment pattern would match
    # when the scan reads this file (the checker scans itself as a tracked file).
    KW = "API" + "_KEY"  # split so the source line cannot match its own pattern

    def prep_n1(fix: Path) -> None:  # N1 — canary in a tracked .md file
        (fix / "STATE.md").write_text(
            (fix / "STATE.md").read_text(encoding="utf-8") + f"\nprobe {CANARY_TRACKED}\n", encoding="utf-8")

    def prep_n4(fix: Path) -> None:  # N4 — credential embedded in a remote URL (https)
        subprocess.run(["git", "remote", "add", "origin",
                        f"https://fakeuser:{CANARY_REMOTE}@github.example.invalid/Arivoo.git"],
                       cwd=fix, check=True, capture_output=True)

    def prep_n4b(fix: Path) -> None:  # N4b — credential embedded via scp syntax
        subprocess.run(["git", "remote", "add", "upstream",
                        f"{CANARY_REMOTE}@github.example.invalid:org/Arivoo.git"],
                       cwd=fix, check=True, capture_output=True)

    def prep_n5(fix: Path) -> None:  # N5 — the tracked .env family: root, nested, suffixed, index-only
        (fix / ".env").write_text(KW + "=" + CANARY_TRACKED + "\n", encoding="utf-8")
        (fix / "context" / ".env").write_text(KW + "=" + CANARY_TRACKED + "\n", encoding="utf-8")
        (fix / ".env.local").write_text(KW + "=" + CANARY_TRACKED + "\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A", "-f"], cwd=fix, check=True, capture_output=True)
        (fix / ".env").unlink()  # index-tracked but deleted from the worktree

    def prep_n6(fix: Path) -> None:  # N6 — canary in non-allowlisted/case-variant/extensionless files
        (fix / "deploy.sh").write_text("export GITHUB_" + "TOKEN='" + CANARY_TRACKED + "'\n", encoding="utf-8")
        (fix / "NOTES.MD").write_text(f"probe {CANARY_TRACKED}\n", encoding="utf-8")
        (fix / "CREDENTIALS").write_text("to" + "ken " + CANARY_TRACKED + "\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A", "-f"], cwd=fix, check=True, capture_output=True)

    def prep_n8(fix: Path) -> None:  # N8 — tracked file deleted from the worktree (index-only)
        (fix / "secret-notes.md").write_text(f"probe {CANARY_TRACKED}\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A", "-f"], cwd=fix, check=True, capture_output=True)
        (fix / "secret-notes.md").unlink()

    def prep_n9(fix: Path) -> None:  # N9 — benign username-only remotes must stay GREEN
        subprocess.run(["git", "remote", "add", "origin-ssh", "ssh://git@github.com:2222/org/Arivoo.git"],
                       cwd=fix, check=True, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin-user", "https://pratham@github.com/org/Arivoo.git"],
                       cwd=fix, check=True, capture_output=True)

    def prep_n5b(fix: Path) -> None:  # N5b — env-family names with BENIGN content: only the family check fires
        (fix / ".envrc").write_text("PORT=8080\n", encoding="utf-8")
        (fix / ".ENV").write_text("PORT=8081\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A", "-f"], cwd=fix, check=True, capture_output=True)

    def prep_n10(fix: Path) -> None:  # N10 — underscore-compounded generic secret key (no token shape)
        # built by concatenation so the checker's own source cannot match its
        # generic-assignment pattern when it scans itself (self-reference guard)
        (fix / "config.yml").write_text("db_" + "password" + ": " + "SYNTHETICPASSWORD1234\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A", "-f"], cwd=fix, check=True, capture_output=True)

    def prep_n11(fix: Path) -> None:  # N11 — extraheader advisory fires without failing
        cfg = fix / ".git" / "config"
        cfg.write_text(cfg.read_text(encoding="utf-8") + "[http]\n\textraheader = placeholder\n", encoding="utf-8")

    def prep_n1b(fix: Path) -> None:  # N1b — multi-@ remote: trailing user:token@ after a decoy @ (curl semantics)
        subprocess.run(["git", "remote", "add", "multi", f"https://fakeuser@team:{CANARY_REMOTE}@github.example.invalid/Arivoo.git"],
                       cwd=fix, check=True, capture_output=True)

    cases: list[tuple[str, object, list[str], dict[str, str], int, list[str], list[str]]] = [
        ("N1 canary in a tracked .md", prep_n1, [], {}, 1, [CANARY_TRACKED], ["secret VALUE pattern"]),
        ("N1b multi-@ remote with trailing token", prep_n1b, [], {}, 1, [CANARY_REMOTE], ["EXPOSED-IN-CONFIG"]),
        ("N2 unexpected secret-named env var", None, [], {"ARIVOO_TEST_TOKEN": CANARY_ENV}, 1, [CANARY_ENV], ["secret-named env var"]),
        ("N3 required CI config missing", None, ["--ci"], {}, 1, [], ["required CI configuration missing"]),
        ("N4 credential in remote URL (https)", prep_n4, [], {}, 1, [CANARY_REMOTE], ["EXPOSED-IN-CONFIG"]),
        ("N4b credential in remote URL (scp syntax)", prep_n4b, [], {}, 1, [CANARY_REMOTE], ["EXPOSED-IN-CONFIG"]),
        ("N5 tracked .env family (root+nested+suffixed+index-only)", prep_n5, [], {}, 1, [CANARY_TRACKED], ["unscannable"]),
        ("N5b env-family names with benign content (family check pinned alone)", prep_n5b, [], {}, 1, [], ["tracked .env-family file"]),
        ("N6 canary in .sh/.MD/extensionless", prep_n6, [], {}, 1, [CANARY_TRACKED], ["secret VALUE pattern"]),
        ("N7 not a git repository", lambda f: shutil.rmtree(f / ".git"), [], {}, 1, [], ["not a git repository"]),
        ("N8 tracked file deleted from worktree", prep_n8, [], {}, 1, [], ["unscannable"]),
        ("N9 benign username-only remotes stay green", prep_n9, [], {}, 0, [], ["ISOLATION GREEN"]),
        ("N10 underscore-compounded generic secret key", prep_n10, [], {}, 1, [], ["generic secret assignment"]),
        ("N11 extraheader advisory fires without failing", prep_n11, [], {}, 0, [], ["[ADVISORY] http.<url>.extraheader present"]),
        ("N12 unknown flag exits 2 with usage error", None, ["--bogus"], {}, 2, [], ["usage error"]),
        ("N13 --ci with case-variant false value counts as missing", None, ["--ci"], {"CI": "False", "GITHUB_ACTIONS": "true", "GITHUB_SHA": "0" * 40, "GITHUB_REF": "refs/heads/main", "GITHUB_REPOSITORY": "prathamarchives/Arivoo"}, 1, [], ["required CI configuration missing"]),
        ("P1 clean local environment", None, [], {}, 0, [], ["ISOLATION GREEN"]),
        ("P2 correctly configured CI environment", None, ["--ci"], dict(CI_LEGIT), 0, [], ["ISOLATION GREEN"]),
    ]

    print(f"isolation self-test (Slice 10.2, post-falsification v2.1) — complete diagnostic path:")
    print(f"{len(cases)} cases; negative cases exit 1 with an attributable RED, positive cases exit 0;")
    print("no synthetic canary may appear in stdout or stderr, including harness crash paths\n")
    failures = 0
    for i, (name, prep, args, case_env, want_rc, canaries, fragments) in enumerate(cases, 1):
        fix = _fixture()
        try:
            try:
                if prep is not None:
                    prep(fix)
                rc, out, err = _run_checker(fix, args, case_env)
            except Exception as exc:  # sanitized: never a traceback (canary-safe)
                failures += 1
                print(f"  case {i} ({name}) FAIL — harness/setup error: {type(exc).__name__} (details redacted; canary never printed)")
                continue
            problems = []
            if rc != want_rc:
                problems.append(f"exit {rc} (expected {want_rc})")
            if want_rc in (0, 1):
                banner = "ISOLATION RED" if want_rc == 1 else "ISOLATION GREEN"
                if banner not in out:
                    problems.append(f"'{banner}' missing from stdout")
            for frag in fragments:
                if frag not in out:
                    problems.append(f"attributable line missing: '{frag}'")
            for canary in canaries:
                if canary in out or canary in err:
                    problems.append("CANARY VALUE LEAKED INTO OUTPUT")
            if problems:
                failures += 1
                print(f"  case {i} ({name}) FAIL — {'; '.join(problems)}")
            else:
                print(f"  case {i} ({name}) PASS — exit {rc} as required, attributable, canary redaction proven")
        finally:
            shutil.rmtree(fix.parent, ignore_errors=True)

    print()
    if failures:
        print(f"SELF-TEST RED — {failures} case(s) failed: the diagnostic path does not prove the stated properties (Slice 10.2).")
        return 1
    print("SELF-TEST GREEN — every negative case failed with an attributable RED, every positive case stayed green,")
    print("benign username-only remotes never false-flag, and no synthetic canary appeared in stdout or stderr")
    print("(the complete redaction path is tested, including harness crash paths).")
    print("Limit, stated: a pattern scan proves these specified leak classes are caught — never that every secret is absent")
    print("(record 16 §4.1 carries the host-permission side of the isolation claim).")
    return 0




if __name__ == "__main__":
    sys.exit(self_test())
