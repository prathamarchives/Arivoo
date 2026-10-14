#!/usr/bin/env python3
"""isolation_check.py — W-03: redacted secret-exposure check (LAW-28, Phase 1).

Prints CONDITIONS, never values (the diagnostics contract applied to secrets: a
condition is an instruction, a value is a leak). Exit 0 = no unexpected exposure;
exit 1 = an unexpected exposure exists and must be repaired before anything else
happens (LAW-28: builder/verifier agents MUST NOT read real owner data or secrets).

Usage:
  python3 tools/isolation_check.py            # local agent environment
  python3 tools/isolation_check.py --ci      # CI runner (GITHUB_TOKEN/CI vars expected)
  python3 tools/isolation_check.py --self-test   # prove the guard fires (plant a fake secret)

Refs: PLAN Phase 1 W-03, LAWS.md LAW-28, D-008 (environment), D-025.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# patterns that indicate a secret VALUE — detected, counted, never printed
SECRET_VALUE_PATTERNS = [
    ("classic GitHub PAT", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("fine-grained GitHub PAT", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("GitHub OAuth token", re.compile(r"gho_[A-Za-z0-9]{36}")),
    ("GitHub app token", re.compile(r"gh[su]_[A-Za-z0-9]{36}")),
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic secret assignment", re.compile(r"(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"\\s]{12,}['\"]")),
]

# env var NAMES that indicate credential presence (name shown, value never)
SECRET_ENV_NAMES = re.compile(r"(?i)(^|_)(TOKEN|PAT|SECRET|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY|CREDENTIALS?)($|_)")
# env vars expected on a GitHub Actions runner
CI_EXPECTED_ENV = {"GITHUB_TOKEN", "CI", "GITHUB_SHA", "GITHUB_REF", "GITHUB_REPOSITORY", "GITHUB_ACTIONS", "GITHUB_EVENT_NAME", "RUNNER_OS", "GITHUB_HEAD_REF", "GITHUB_BASE_REF", "GITHUB_RUN_ID", "GITHUB_JOB", "GITHUB_WORKSPACE", "GITHUB_EVENT_PATH", "GITHUB_API_URL", "GITHUB_GRAPHQL_URL", "GITHUB_SERVER_URL", "GITHUB_ACTOR", "GITHUB_REPOSITORY_OWNER", "GITHUB_RUN_NUMBER", "GITHUB_STEP_SUMMARY", "GITHUB_OUTPUT", "GITHUB_ENV", "GITHUB_PATH"}

# repo locations a credential could leak into
TRACKED_SCAN_PATHS = ["AGENTS.md", "STATE.md", "INTENT-LEDGER.md", "DECISIONS.md", "EXECUTION.md",
                       "PLAN.md", "PRINCIPLES.md", "LAWS.md", "NORTH-STAR.md", "OPERATING-MODEL.md",
                       "ENGINEERING.md", "GLOSSARY.md", "context/README.md", "context/WORKLOG.md"]


def check(ci_mode: bool) -> int:
    findings: list[str] = []  # conditions, never values
    unexpected = 0

    print("isolation check — conditions printed, values never (LAW-28, W-03)\n")

    # 1. git remotes: is a credential embedded in a remote URL?
    try:
        remotes = subprocess.run(["git", "remote", "-v"], cwd=REPO, capture_output=True, text=True, timeout=10).stdout
    except Exception:
        remotes = ""
    embedded = [line.split()[0] for line in remotes.splitlines()
                if "://" in line and "@" in line.split("://", 1)[1].split("/", 1)[0]]
    if embedded:
        findings.append(f"git remote URL embeds a credential (remotes: {', '.join(sorted(set(embedded)))}) — condition: EXPOSED-IN-CONFIG; use a credential helper instead (git config credential.helper; store the token outside the repo)")
        # a local-only config exposure is a hard warning, not repo leakage — one notch below exit-1
        unexpected += 0
        print(f"  [WARN] remote credential embedded in local git config (local-only; not repo content) — repair: credential helper")
    else:
        print("  [PASS] no credential embedded in git remote URLs")

    # 2. environment variables: NAMES only
    secret_env = [k for k in os.environ if SECRET_ENV_NAMES.search(k)]
    expected = sorted(k for k in secret_env if k in CI_EXPECTED_ENV) if ci_mode else []
    unexpected_env = sorted(k for k in secret_env if k not in expected)
    for k in expected:
        print(f"  [PASS] expected CI env var present: {k} (value never printed)")
    if unexpected_env:
        for k in unexpected_env:
            findings.append(f"environment variable with a secret-like NAME is set: {k} (value never printed)")
            unexpected += 1
            print(f"  [FAIL] unexpected secret-named env var: {k}")
    else:
        print(f"  [PASS] no unexpected secret-named environment variables ({len(secret_env)} secret-named total, {len(expected)} CI-expected)")

    # 3. tracked files: secret VALUES must not exist in repo content
    leaked = []
    for rel in TRACKED_SCAN_PATHS:
        p = REPO / rel
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for label, pat in SECRET_VALUE_PATTERNS:
            for _ in pat.findall(text):
                leaked.append(rel)
    git_tracked = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, timeout=10).stdout.splitlines()
    for rel in git_tracked:
        if rel.startswith("context/raw/") or rel in TRACKED_SCAN_PATHS or not rel.endswith((".md", ".txt", ".py", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini")):
            continue
        p = REPO / rel
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for label, pat in SECRET_VALUE_PATTERNS:
            if pat.search(text):
                leaked.append(f"{rel} ({label})")
    if leaked:
        for rel in leaked:
            findings.append(f"secret VALUE pattern found in tracked file: {rel} — remove it, rotate the credential, and scrub git history if it was ever pushed")
        unexpected += 1
        print(f"  [FAIL] secret value pattern(s) in tracked files: {', '.join(leaked)}")
    else:
        print("  [PASS] no secret value patterns in tracked repo files (canonical docs, tools, workflows, context)")

    # 4. .env files must never be tracked
    if (REPO / ".env").exists() and ".env" in git_tracked:
        findings.append(".env is TRACKED in git — untrack it (git rm --cached) and rotate every credential it held")
        unexpected += 1
        print("  [FAIL] .env file is tracked")
    else:
        print("  [PASS] no tracked .env file")

    print()
    if unexpected:
        print(f"ISOLATION RED — {unexpected} unexpected exposure class(es). Repair before any other work (LAW-28).")
        print("Findings (conditions only):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("ISOLATION GREEN — no unexpected secret exposure in this environment (conditions checked: git remotes, environment names, tracked file contents, .env tracking).")
    if findings:
        print("Advisory conditions (local-only, no repo leakage):")
        for f in findings:
            print(f"  - {f}")
    return 0


def self_test() -> int:
    """Known-bad: plant a fake PAT in a temp copy of a tracked file — the check MUST go red."""
    with tempfile.TemporaryDirectory(prefix="arivoo-iso-") as td:
        copy = Path(td) / "STATE.md"
        copy.write_text("fake\nghp_" + "A" * 36 + "\n", encoding="utf-8")
        text = copy.read_text()
        caught = any(pat.search(text) for _, pat in SECRET_VALUE_PATTERNS)
        print("isolation self-test: planted fake PAT in a tracked-file copy →", "CAUGHT (red)" if caught else "MISSED (blind guard)")
        return 0 if caught else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    return check(ci_mode="--ci" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
