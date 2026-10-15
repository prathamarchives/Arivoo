#!/usr/bin/env python3
r"""isolation_check.py — W-03: redacted secret-exposure check (LAW-28, Phase 1).

Slice 10 (D-034, session 16 — the Arivoo review's Slice 10.2): diagnostic safety
is a TESTED property, not a design intention. The check prints CONDITIONS, never
values (the diagnostics contract applied to secrets: a condition is an
instruction, a value is a leak). Exit 0 = no unexpected exposure; exit 1 = an
unexpected exposure exists and must be repaired before anything else happens
(LAW-28: builder/verifier agents MUST NOT read real owner data or secrets).

v2.1 (session 16, after TWO falsification rounds — record 16 §7; the
fresh-context verifier found 3 P1 false-greens + 7 P2/P3 defects in round 1 and
verified the repairs + found the round-2 residuals in round 2, all repaired):
the tracked-file scan covers EVERY tracked file, any extension, any case (was:
an .md/.txt/.py/... allowlist — a .sh or extensionless file skipped whole leak
classes); a tracked file that is missing from the worktree or unreadable FAILS
closed (was: silently skipped — the index copy stayed unscanned); the `.env`
check covers every tracked `.env`-family path — nested, suffixed (.env.local),
case-insensitive (.ENV), dotfile (.envrc), and index-tracked-but-deleted (was:
root .env, present, only); the remote-credential detector handles scheme and
scp-syntax URLs, takes the userinfo from the authority split at the LAST @
(curl semantics — a trailing user:token@ behind a decoy @ cannot hide), flags
user:pass@ and token-shaped userinfo, and does NOT flag benign username-only
remotes (git@host, user@host — was: any @ in the authority false-REDDed the
standard ssh form); the env-NAME pattern catches compounded, digit-suffixed,
bare-KEY/KEYS, PW, PASS and PASSPHRASE forms (TOKEN2, MYTOKEN, SSH_KEYS,
DB_PW, DB_PASS, PASSPHRASE...) without matching PATH/PWD; the generic
secret-assignment pattern's value class is fixed (\s excluded the letter 's'
— most real secrets — and demanded quotes; now any 12+ non-space value,
quoted or not, and underscore-compounded keys like db_password match); --ci
requires non-empty, non-false values in any case/whitespace variant; unknown
flags exit 2 instead of silently degrading to local mode; a missing .git or an
unavailable git FAILS closed (vacuous scans can never print green);
http.<url>.extraheader in the git config prints an advisory (the
actions/checkout persist-credentials form — resolved through worktree .git
files too; a real config credential, reported without failing CI, whose
remote-URL sibling is the failing class); printed paths are passed through a
redaction pass (a secret-shaped FILENAME is value material); the self-test is
an 18-case complete-path matrix — every catch class pinned by a case that can
fire for that class alone, attributable-failure and canary-redaction asserts
on stdout AND stderr, including the harness's own crash paths (a self-test
crash prints a sanitized line, never a traceback carrying a canary).

Explicit limit (stated, never papered over): a pattern scan cannot prove that
every possible secret is absent. It proves that the specified leak classes are
caught and that the checker does not print their values. The isolation claim
rests on this evidence PLUS verified host permissions (record 16 §4.1 — the
Slice 10A boundary account), never on an overbroad reading of a green regex scan.

Usage:
  python3 tools/isolation_check.py            # local agent environment
  python3 tools/isolation_check.py --ci       # CI runner (required CI config checked)
  python3 tools/isolation_check.py --self-test   # the full negative+positive matrix
  (any other flag exits 2 with usage — never a silent mode change)

Refs: PLAN Phase 1 W-03 + layer 1.3 (Slice 10), LAWS.md LAW-28, D-008, D-025, D-034.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# patterns that indicate a secret VALUE — detected, counted, never printed.
# The generic-assignment form accepts quoted OR unquoted values of 12+ non-space
# chars (falsification finding 9: the old class excluded the letter 's' and
# demanded quotes — most real secret values never matched).
SECRET_VALUE_PATTERNS = [
    ("classic GitHub PAT", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("fine-grained GitHub PAT", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("GitHub OAuth token", re.compile(r"gho_[A-Za-z0-9]{36}")),
    ("GitHub app token", re.compile(r"gh[su]_[A-Za-z0-9]{36}")),
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic secret assignment", re.compile(r"(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*['\"]?\S{12,}")),
]

# env var NAMES that indicate credential presence (name shown, value never).
# Falsification rounds 1+2: the old word-boundary form missed compounded
# (MYTOKEN, PERSONALACCESSTOKEN), digit-suffixed (TOKEN2), bare-KEY (SSH_KEY,
# DEPLOY_KEY), PW/PASS (DB_PW, DB_PASS, MY_PASS) and PASSPHRASE shapes. Substring
# stems for the unambiguous words; boundary-guarded PAT/KEY/PW/PASS so
# PATH/PWD never match. KEY takes an optional plural S (SSH_KEYS).
SECRET_ENV_NAMES = re.compile(
    r"(?i)(TOKEN|SECRET|PASSW|PASSPHRASE|CREDENTIAL|API_?KEY|ACCESS_?KEY|PRIVATE_?KEY"
    r"|(^|_)PAT($|_|S)|(^|_)KEYS?($|_)|(^|_)PW($|_)|(^|_)PASS($|_))"
)

# env vars EXPECTED on a GitHub Actions runner when a name matches the pattern
# above. The GITHUB_/ACTIONS_/RUNNER_ prefixes are the runner's own namespaces:
# their token-shaped members (e.g. ACTIONS_RUNTIME_TOKEN) are expected in CI
# mode, never counted as unexpected exposure.
CI_EXPECTED_ENV = {"GITHUB_TOKEN"}
CI_EXPECTED_PREFIXES = ("GITHUB_", "ACTIONS_", "RUNNER_")

# REQUIRED configuration by execution mode (Slice 10.2 #2): names only, values
# never. Local agent environment: no environment variables are required
# (repo-file checks only). CI runner: the standard GitHub Actions variables the
# --ci contract relies on — PRESENT means set, non-empty, and not the literal
# "false" in any case/whitespace variant (round-2 finding 13: False/FALSE/" false"
# must count as missing); a --ci run outside a configured runner must FAIL, not
# silently degrade.
def _ci_value_missing(value: str) -> bool:
    return value.strip().lower() in ("", "false")

REQUIRED_CI = {"CI", "GITHUB_ACTIONS", "GITHUB_SHA", "GITHUB_REF", "GITHUB_REPOSITORY"}


def _userinfo_embeds_credential(url: str) -> bool:
    """True when a remote URL's userinfo carries a credential: user:pass@host
    (any scheme), a token-shaped userinfo (bare PATs work as usernames), or the
    scp-syntax token@host:path form. Username-only remotes (git@host, user@host)
    are benign and never flagged (falsification findings 7/8). The userinfo is
    taken from the AUTHORITY (up to the first path separator) and split at the
    LAST @ — curl's semantics, so a trailing user:token@ after a decoy @ cannot
    hide the functional credential (round-2 finding N1)."""
    rest = url.split("://", 1)[1] if "://" in url else url
    authority = re.split(r"[/?#]", rest, 1)[0]
    if "@" not in authority:
        return False
    userinfo = authority.rsplit("@", 1)[0]
    if not userinfo:
        return False
    if ":" in userinfo:
        return True
    if any(pat.search(userinfo) for _, pat in SECRET_VALUE_PATTERNS):
        return True
    if "://" not in url and not re.match(r"^[A-Za-z0-9._-]+$", userinfo):
        return True  # opaque scp-syntax userinfo that is not a plain username
    return False


def _redact(text: str) -> str:
    """Mask any secret-shaped substring in a string before it is printed — a
    CONDITION may name a path, but a secret-shaped FILENAME is still value
    material (round-2 finding N9: defense in depth for path echoes)."""
    for _, pat in SECRET_VALUE_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


def _git_config_path(repo: Path) -> Path | None:
    """Resolve .git/config for a normal repo OR a worktree checkout (.git is a
    FILE pointing at the real gitdir — round-2 finding N7: the advisory must
    still see the shared config)."""
    dg = repo / ".git"
    try:
        if dg.is_file():
            m = re.search(r"gitdir:\s*(\S+)", dg.read_text(encoding="utf-8", errors="replace"))
            if m:
                p = Path(m.group(1))
                return (p if p.is_absolute() else (repo / p)) / "config"
            return None
        return dg / "config"
    except Exception:
        return None


def check(ci_mode: bool, env: dict[str, str] | None = None, repo_root: Path | None = None) -> int:
    """Run the isolation check. env/repo_root default to the live environment/repo;
    the self-test overrides them to exercise synthetic fixtures."""
    env = os.environ if env is None else env
    repo = repo_root if repo_root is not None else REPO
    findings: list[str] = []  # conditions, never values
    advisories: list[str] = []
    unexpected = 0

    print("isolation check — conditions printed, values never (LAW-28, W-03)\n")

    # 1. git remotes: is a credential embedded in a remote URL?
    #    (Slice 10.2 #1: a REAL failure, never a warning — an agent that can read
    #    .git/config can recover the embedded credential; repair = credential helper)
    git_missing = shutil.which("git") is None
    try:
        remotes_proc = subprocess.run(["git", "remote", "-v"], cwd=repo, capture_output=True, text=True, timeout=10)
        remotes, remotes_ok = remotes_proc.stdout, remotes_proc.returncode == 0
    except Exception:
        remotes, remotes_ok = "", False
    if not remotes_ok:
        findings.append("git remote probe failed — the remote-URL credential check cannot run (condition, not a pass)")
        unexpected += 1
        print("  [FAIL] git remote probe failed — remote-URL check cannot run")
    else:
        embedded = [line.split()[0] for line in remotes.splitlines()
                    if line.strip() and _userinfo_embeds_credential(line.split("\t")[-1].split(" ")[0] if "\t" in line else line)]
        if embedded:
            findings.append(f"git remote URL embeds a credential (remotes: {', '.join(sorted(set(embedded)))}) — condition: EXPOSED-IN-CONFIG; use a credential helper instead (git config credential.helper; store the token outside the repo)")
            unexpected += 1
            print("  [FAIL] remote credential embedded in git config (remote names only, URL never printed) — repair: external credential helper")
        else:
            print("  [PASS] no credential embedded in git remote URLs (scheme and scp-syntax forms checked; username-only remotes are benign)")

    # 1b. advisory: http.<url>.extraheader in the git config (the
    #     actions/checkout persist-credentials form — a real .git/config
    #     credential, reported without failing: CI checkouts set it by design;
    #     rotate if unexpected. Resolved through the worktree indirection too
    #     (.git as a FILE — round-2 finding N7).
    cfg_path = _git_config_path(repo)
    gitcfg = ""
    if cfg_path is not None:
        try:
            gitcfg = cfg_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            gitcfg = ""
    if "extraheader" in gitcfg.lower():
        advisories.append("git config sets http.<url>.extraheader (credential material in the git config — standard actions/checkout persist-credentials form; advisory, not the remote-URL failure class)")
        print("  [ADVISORY] http.<url>.extraheader present in the git config (conditions only, value never printed)")

    # 2. environment variables: NAMES only
    def _ci_expected(k: str) -> bool:
        if k in CI_EXPECTED_ENV:
            return ci_mode
        return ci_mode and k.startswith(CI_EXPECTED_PREFIXES)

    secret_env = [k for k in env if SECRET_ENV_NAMES.search(k)]
    expected = sorted(k for k in secret_env if _ci_expected(k))
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

    # 2b. required configuration BY MODE (Slice 10.2 #2) — present/absent, values never
    if ci_mode:
        missing = sorted(v for v in REQUIRED_CI if _ci_value_missing(env.get(v, "")))
        for v in sorted(REQUIRED_CI):
            if not _ci_value_missing(env.get(v, "")):
                print(f"  [PASS] required CI config present: {v} (value never printed)")
        if missing:
            for v in missing:
                findings.append(f"required CI configuration missing or false: {v} (name only) — the --ci mode is running outside a configured runner")
                unexpected += 1
                print(f"  [FAIL] required CI config missing: {v}")
        else:
            print("  [PASS] all required CI configuration present (names only, values never)")
    else:
        print("  [PASS] local mode: no required environment variables (repo-file checks only)")

    # 3. tracked files: secret VALUES must not exist in repo content. EVERY
    #    tracked file, any extension, any case (falsification findings 1/4: the
    #    old extension allowlist skipped .sh/.rst/extensionless/uppercase whole).
    #    context/raw/ included — a live credential in the owner-received corpus
    #    is a P0 leak even though removal needs an owner decision (VER-802).
    #    A missing .git, an unavailable git, or an empty index FAILS CLOSED — a
    #    vacuous scan can never print green (findings 5/12).
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True, timeout=10)
        git_tracked = proc.stdout.splitlines() if proc.returncode == 0 else []
        lsfiles_ok = proc.returncode == 0
    except Exception:
        git_tracked, lsfiles_ok = [], False
    if git_missing:
        findings.append("git is not available — the tracked-file scan cannot run (condition, not a pass)")
        unexpected += 1
        print("  [FAIL] git unavailable — tracked-file scan cannot run")
    elif not lsfiles_ok:
        if not (repo / ".git").exists():
            findings.append("no .git directory — not a git repository; the tracked-file scan cannot run (condition, not a pass)")
            unexpected += 1
            print("  [FAIL] not a git repository — tracked-file scan cannot run")
        else:
            findings.append("git ls-files failed — the tracked-file scan cannot run (git error, condition not a pass)")
            unexpected += 1
            print("  [FAIL] git ls-files failed — tracked-file scan cannot run")
    elif not git_tracked:
        findings.append("git repository has no tracked files — the tracked-file scan is vacuous (condition, not a pass)")
        unexpected += 1
        print("  [FAIL] no tracked files visible to git ls-files — tracked-file scan vacuous")
    else:
        leaked, unscannable = [], []
        for rel in git_tracked:
            p = repo / rel
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                unscannable.append(rel)
                continue
            for label, pat in SECRET_VALUE_PATTERNS:
                if pat.search(text):
                    leaked.append(f"{rel} ({label})")
        if unscannable:
            for rel in unscannable:
                findings.append(f"tracked file missing from worktree or unreadable: {_redact(rel)} — the index copy is unscanned; inspect the indexed copy before trusting this run")
            unexpected += 1
            print(f"  [FAIL] tracked file(s) unscannable (worktree-missing/unreadable): {_redact(', '.join(unscannable))}")
        if leaked:
            for rel in leaked:
                raw_note = " — RAW CORPUS HIT: rotate the credential immediately; removal requires an owner decision (raw is VER-802-anchored — scrub with a manifest re-anchor)" if rel.startswith("context/raw/") else ""
                findings.append(f"secret VALUE pattern found in tracked file: {_redact(rel)} — remove it, rotate the credential, and scrub git history if it was ever pushed{raw_note}")
            unexpected += 1
            print(f"  [FAIL] secret value pattern(s) in tracked files: {_redact(', '.join(leaked))}")
        if not leaked and not unscannable:
            print("  [PASS] no secret value patterns in tracked repo files (every tracked file, all extensions, incl. context/raw/)")

    # 4. .env files must never be tracked — ANY .env-family path: root, nested,
    #    suffixed (.env.local), case-insensitive (.ENV), dotfile forms (.envrc)
    #    and index-tracked-but-deleted (falsification findings 2/3 + round-2 N4:
    #    only root-present .env was checked before).
    def _is_env_path(rel: str) -> bool:
        name = Path(rel).name.lower()
        return (name == ".env" or name.endswith(".env") or name.startswith(".env")
                or ".env." in name)
    tracked_env = [rel for rel in git_tracked if _is_env_path(rel)]
    if tracked_env:
        for rel in tracked_env:
            findings.append(f".env-family file is TRACKED in git: {_redact(rel)} — untrack it (git rm --cached) and rotate every credential it held")
        unexpected += 1
        print(f"  [FAIL] tracked .env-family file(s): {_redact(', '.join(tracked_env))}")
    elif lsfiles_ok and (repo / ".git").exists() and git_tracked:
        print("  [PASS] no tracked .env-family file (root, nested, suffixed, and index-only forms all checked)")

    print()
    if unexpected:
        print(f"ISOLATION RED — {unexpected} unexpected exposure class(es). Repair before any other work (LAW-28).")
        print("Findings (conditions only):")
        for f in findings:
            print(f"  - {f}")
        if advisories:
            print("Advisories (conditions only):")
            for a in advisories:
                print(f"  - {a}")
        return 1
    print("ISOLATION GREEN — no unexpected secret exposure in this environment (conditions checked: git remotes incl. scp-syntax, environment names, required config by mode, tracked file contents, .env-family tracking).")
    if advisories:
        print("Advisories (conditions only, never values):")
        for a in advisories:
            print(f"  - {a}")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if any(a not in ("--self-test", "--ci") for a in argv):
        print(f"usage error: unknown flag(s) {[a for a in argv if a not in ('--self-test', '--ci')]} —")
        print("  python3 tools/isolation_check.py [--ci | --self-test]   (never a silent mode change)")
        return 2
    if "--self-test" in argv:
        # delegate to the extracted suite module (session 17 / D-035: suite and
        # implementation are separately anchorable; the flag stays for backward
        # compatibility with every recorded command)
        r = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parent / "isolation_selftest.py")],
            timeout=900,
        )
        return r.returncode
    return check(ci_mode="--ci" in argv)


if __name__ == "__main__":
    sys.exit(main())
