#!/usr/bin/env python3
r"""isolation_selftest.py — the W-03 self-test, as a separately-invocable module.

Extracted from tools/isolation_check.py (session 17, D-035 — the candidate-tool gate
repair): the TEST SUITE and the IMPLEMENTATION can now be anchored independently,
so the base-anchored CI job runs THIS suite (from main) against the CANDIDATE's
isolation_check.py — the coordinated-weakening floor (a PR that weakens the
checker AND its own self-test together fails these cases in the required job).

v2.2 (session 23, H-01b-F — F-002/F-011/F-012, INT-127/D-041): the suite's own
fixture machinery is bounded, no-dereference and sanitized (self-contained by
NECESSITY: the anchored copy must never import a candidate-controlled module —
the F-005 class), and the matrix grows six bound-hygiene cases: B1/B2 pin
mode-aware tracked scanning (a symlink's LINK TEXT is the data; the target is
NEVER opened — a tracked link to a non-terminating stream cannot hang the
checker, and a canary hidden in link text is caught); B3/B4 pin the per-file
and total scan budgets (fail-closed named refusals); B5/B6 pin the builder's
own contract (a failed construction cleans up its temp root — cleanup is
established BEFORE construction starts — and the sanitized refusal carries a
fixed diagnostic + the cause's class name only, never a path: a secret-shaped
FILENAME is value material). The standalone entry gains the sanitized
exception boundary (a harness crash prints one sanitized line, never a
traceback). The 18 v2.1 cases are unchanged (assertions never removed).

v2.3 (session 25, R-03 — the G-51 isolation-tool hardening, INT-129/D-042's
routing; the 5 Greptile findings on #51 in 4 repair items): (1) BOTH
`_open_regular_nofollow` helpers (the checker's AND this suite's own) open
O_NONBLOCK — a path lstat'd regular then swapped to a FIFO can no longer hang
the open indefinitely (the same FIFO-swap class the mutation floor's B3
repair closed in its sibling); the ISREG check on the open fd refuses the
FIFO immediately. (2) `_copy_bounded`'s os.walk carries `onerror` — an
unreadable directory's subtree is a fail-closed sanitized FixtureBuildError,
never a SILENT DROP from the fixture copy (the false-complete-fixture class:
shutil.copytree, which this replaced, reported the error). (3) every created
directory charges the fixture entry budget (the predecessor charged only
files: a source of N empty directories constructed under any count budget).
(4) B5/B6 assert the sanitized refusal's FIXED MESSAGE directly (the exact
text, cause class included, path/canary excluded) — the predecessor kept
only the exception's TYPE and discarded the message, so a wrapper that lost
the fixed diagnostic or leaked a path still passed. NEW cases B7/B8 pin the
two helpers' non-blocking FIFO refusal in DISPOSABLE CHILD PROCESSES (the
anchored copy never imports a candidate-controlled module in-process — the
F-005 class held; the child imports by path, the parent judges only the
bounded outcome); B9 pins the walk's fail-closed unreadable-directory
refusal (skip-declared under root, the R-02 test_20 precedent — chmod-0
cannot stop CAP_DAC_OVERRIDE); B10 pins the directory-entry budget. The v2.1
and v2.2 cases are unchanged (assertions never removed).

The suite invokes tools/isolation_check.py as a SUBPROCESS (implementation-
agnostic: it judges whatever checker file sits beside this module). Content and
semantics are moved verbatim from the v2.1 checker (18 cases; counts unchanged):
negative cases exit 1 with an attributable RED, positives exit 0, canaries never
appear in stdout/stderr, harness crash paths print sanitized lines only.

Usage: python3 tools/isolation_selftest.py   (or isolation_check.py --self-test,
which delegates here for backward compatibility with the recorded commands).
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import stat as statmod
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
CANARY_LINK = "ghp_" + "E" * 36              # synthetic PAT shape, hidden in symlink LINK TEXT

CI_LEGIT = {
    "CI": "true",
    "GITHUB_ACTIONS": "true",
    "GITHUB_SHA": "0" * 40,                    # synthetic, not a secret
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_REPOSITORY": "prathamarchives/Arivoo",
    "RUNNER_OS": "Linux",
}


# ---------------------------------------------------------------- H-01b-F (session 23)
# The fixture builder's own contract (F-011/F-012): bounded, no-dereference,
# sanitized — the mutation_runner contract family, kept SELF-CONTAINED because
# this suite runs as the BASE-anchored judge: importing ANY module from the
# candidate tree (e.g. tools/mutation_runner.py) would execute candidate code
# inside the trusted judge — the F-005 class. Cleanup is established BEFORE
# construction starts and runs even when construction fails; the refusal is a
# fixed diagnostic + the cause's class name only (a secret-shaped FILENAME is
# value material — F-012: it must never reach stdout/stderr).
FIX_PER_FILE_BUDGET = 8 * 1024 * 1024
FIX_TOTAL_BUDGET = 192 * 1024 * 1024
FIX_COUNT_BUDGET = 5000
FIX_SKIP_DIRS = {".git", "__pycache__", ".pg"}
_FIX_REFUSAL = ("fixture construction refused: the source tree contains a non-regular "
               "or unreadable entry, or a copy budget was exceeded (F-011) — sanitized: "
               "no path, no filename, no raw error text (F-012)")

# R-03(1) / B7+B8: the wrapper's own fixed sanitized refusal (the _fixture
# wrapper's message shape — cause class name embedded, nothing else). The B5/B6
# message pins assert this EXACT text (a wrapper that loses the fixed diagnostic
# or leaks a path must fail the case, never pass vacuously on the class name).
_WRAPPER_REFUSAL = ("fixture construction refused (FixtureBuildError) — "
                   "sanitized: no path or raw error is printed by design")

# R-03(1) / B7+B8: the child-probe script for the bounded-open contract. The
# child imports the target module BY PATH (a disposable child, never an
# in-process import — the F-005 class held at the anchored copy) and calls its
# _open_regular_nofollow on a FIFO. Under O_NONBLOCK the open returns at once
# and the ISREG check refuses (PROBE-REFUSED); without it the open BLOCKS on
# the FIFO and the parent's timeout names the hang (R-03's RED form).
_BOUNDED_OPEN_PROBE = r"""
import pathlib, sys
spec_path, fifo_path = sys.argv[1], sys.argv[2]
import importlib.util
spec = importlib.util.spec_from_file_location("bounded_open_target", spec_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    mod._open_regular_nofollow(pathlib.Path(fifo_path))
    print("PROBE-OPENED")
except OSError:
    print("PROBE-REFUSED")
sys.exit(0)
"""


class FixtureBuildError(Exception):
    """The sanitized construction refusal: the message is fixed; the cause's
    CLASS NAME travels, its message/path/filename NEVER."""


def _open_regular_nofollow(path: Path) -> int:
    """Race-resistant bounded-open (the mutation_runner contract family):
    symlinks refused (O_NOFOLLOW), open NON-BLOCKING (R-03/G-51-1: a path
    lstat'd regular then swapped to a FIFO between the lstat and the open can
    never hang the builder — the same FIFO-swap class the floor's B3 repair
    closed), the OPEN fd re-verified ISREG. The fd pins the inode: a same-name
    swap after open cannot redirect the copy."""
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
                 | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    try:
        if not statmod.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file")
    except Exception:
        os.close(fd)
        raise
    return fd


def _copy_bounded(src: Path, dst: Path, per_file: int, total: int, count: int) -> None:
    """Walk `src` and copy it into `dst`, bounded and WITHOUT dereference:
    symlinked directories are never traversed; symlinks and every other
    non-regular entry are REFUSED (never copied, never followed — F-011); the
    copy is capped per-file/total/count; a source that changes under the walk
    refuses. Raises FixtureBuildError on any refusal (sanitized message).

    R-03 (the G-51 hardening): walk errors FAIL CLOSED (os.walk `onerror` —
    an unreadable directory's subtree is a sanitized refusal, never a SILENT
    DROP from the copy: a false-complete fixture is the false-green class —
    the shutil.copytree this replaced reported the error), and EVERY created
    directory charges the entry budget (the predecessor charged only files:
    a source of N empty directories constructed under any count budget)."""

    def _walk_fail_closed(err: OSError) -> None:
        raise FixtureBuildError(_FIX_REFUSAL) from None

    seen = 0
    walked = 0
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False, onerror=_walk_fail_closed):
        kept = []
        for d in sorted(dirnames):
            if d in FIX_SKIP_DIRS:
                continue
            if (Path(dirpath) / d).is_symlink():      # a symlinked directory is never traversed
                raise FixtureBuildError(_FIX_REFUSAL) from None
            kept.append(d)
        dirnames[:] = kept
        rel_dir = Path(dirpath).relative_to(src)
        seen += 1                                     # R-03(3): a directory is an entry
        if seen > count:
            raise FixtureBuildError(_FIX_REFUSAL) from None
        (dst / rel_dir).mkdir(parents=True, exist_ok=True)
        for fn in sorted(filenames):
            full = Path(dirpath) / fn
            try:
                st = full.lstat()
            except OSError:
                raise FixtureBuildError(_FIX_REFUSAL) from None
            if not statmod.S_ISREG(st.st_mode):
                raise FixtureBuildError(_FIX_REFUSAL) from None   # never dereferenced, never opened
            if st.st_size > per_file:
                raise FixtureBuildError(_FIX_REFUSAL) from None
            walked += st.st_size
            if walked > total:
                raise FixtureBuildError(_FIX_REFUSAL) from None
            seen += 1
            if seen > count:
                raise FixtureBuildError(_FIX_REFUSAL) from None
            try:
                fd = _open_regular_nofollow(full)
            except OSError:
                raise FixtureBuildError(_FIX_REFUSAL) from None
            try:
                with os.fdopen(fd, "rb") as fh:
                    data = fh.read(per_file + 1)
            except OSError:
                raise FixtureBuildError(_FIX_REFUSAL) from None
            if len(data) != st.st_size or len(data) > per_file:
                raise FixtureBuildError(_FIX_REFUSAL) from None   # changed under the walk
            (dst / rel_dir / fn).write_bytes(data)


def _fixture(source: Path | None = None, *, per_file: int = FIX_PER_FILE_BUDGET,
             total: int = FIX_TOTAL_BUDGET, count: int = FIX_COUNT_BUDGET) -> Path:
    """A synthetic repository: the source tree (default: the real repo), copied
    BOUNDED and WITHOUT dereference into a fresh git repo with all files
    staged, so ls-files and remote probes operate on real tracked content.
    Synthetic mutations are applied per-case on top of this.

    H-01b-F (F-011/F-012): cleanup is established BEFORE construction starts
    and runs even when construction ITSELF fails; the failure is sanitized —
    a fixed diagnostic + the cause's class name only, never a path, a
    filename, a raw error or a traceback. `source`/budget overrides exist so
    the builder cases can prove this contract against poisoned sources."""
    src = Path(source) if source is not None else REPO
    td = Path(tempfile.mkdtemp(prefix="arivoo-iso-"))
    try:
        fix = td / "repo"
        _copy_bounded(src, fix, per_file, total, count)
        subprocess.run(["git", "init", "-q"], cwd=fix, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=fix, check=True, capture_output=True)
        return fix
    except Exception as exc:
        # F-011: the cleanup scope began at mkdtemp — a failed construction
        # still cleans up. F-012: the refusal carries the cause's CLASS only.
        shutil.rmtree(td, ignore_errors=True)
        raise FixtureBuildError(
            f"fixture construction refused ({type(exc).__name__}) — "
            "sanitized: no path or raw error is printed by design"
        ) from None


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

    # H-01b-F preps (F-002): mode-aware tracked scanning + the scan budgets. Each
    # case must be self-contained (the A11 probe-coupling lesson, third occurrence
    # in record 22 §8 — a case never depends on another case's fixture state).
    # NOTE (CLAIM-038, the canary item's honest close): the env-KEY and remote-NAME
    # masking SITES landed in tools/isolation_check.py (_redact at both finding
    # sites) and the direct probe OBSERVED the masked output (TOKEN_test_[REDACTED]BBBB —
    # the canary never appears whole). The selftest-registry integration (the N12
    # row) fought the case runner's exit-2 usage form and is ROUTED as a named
    # follow-up rather than shipped half-proven here — never silently claimed.

    def prep_b1(fix: Path) -> None:  # B1 — tracked symlink -> a non-terminating stream (FIFO)
        os.symlink("../stream.fifo", fix / "stream.link")
        subprocess.run(["git", "add", "-A"], cwd=fix, check=True, capture_output=True)
        os.mkfifo(fix.parent / "stream.fifo")   # AFTER git add: the fifo itself is never tracked

    def prep_b2(fix: Path) -> None:  # B2 — canary in the symlink's LINK TEXT (dangling by construction)
        os.symlink("https://user:" + CANARY_LINK + "@example.invalid/a.git", fix / "creds.link")
        subprocess.run(["git", "add", "-A"], cwd=fix, check=True, capture_output=True)

    def prep_b3(fix: Path) -> None:  # B3 — oversized tracked regular file (sparse; per-file budget)
        fd = os.open(fix / "blob.bin", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        os.ftruncate(fd, 16 * 1024 * 1024)      # 16 MiB sparse > the 8 MiB per-file scan budget
        os.close(fd)
        subprocess.run(["git", "add", "-A"], cwd=fix, check=True, capture_output=True)

    def prep_b4(fix: Path) -> None:  # B4 — tracked content beyond the total scan budget
        for i in range(10):                        # 10 x 7 MiB = 70 MiB > the 64 MiB total budget
            fd = os.open(fix / f"blob-{i:02d}.bin", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            os.ftruncate(fd, 7 * 1024 * 1024)    # each under the per-file budget
            os.close(fd)
        subprocess.run(["git", "add", "-A"], cwd=fix, check=True, capture_output=True)

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
        ("B1 tracked symlink to a non-terminating stream is never opened (F-002; no hang, scanned as link text)", prep_b1, [], {}, 0, [], ["ISOLATION GREEN"]),
        ("B2 canary in a symlink's LINK TEXT is caught (dangling link; target never read)", prep_b2, [], {}, 1, [CANARY_LINK], ["secret VALUE pattern"]),
        ("B3 oversized tracked regular file refuses with the per-file scan budget (F-002)", prep_b3, [], {}, 1, [], ["per-file scan budget"]),
        ("B4 tracked content beyond the total scan budget refuses (F-002)", prep_b4, [], {}, 1, [], ["total scan budget"]),
    ]

    print(f"isolation self-test (Slice 10.2 v2.1 + H-01b-F v2.2 + R-03 v2.3) — complete diagnostic path:")
    print(f"{len(cases)} checker cases + {6} builder/tool-contract cases; negative cases exit 1 with an attributable RED,")
    print("positive cases exit 0; no synthetic canary may appear in stdout or stderr, including harness crash paths\n")
    failures = 0
    for i, (name, prep, args, case_env, want_rc, canaries, fragments) in enumerate(cases, 1):
        fix = None
        try:
            # H-01b-F: construction failure is INSIDE the sanitized boundary — a
            # fixture that cannot be built is a case failure, never a traceback
            # (the predecessor built the fixture outside this try: a copy failure
            # escaped the boundary and printed a raw path/traceback — the F-012
            # class, reproduced as this slice's red-02 probe).
            fix = _fixture()
            if prep is not None:
                prep(fix)
            rc, out, err = _run_checker(fix, args, case_env)
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
        except Exception as exc:  # sanitized: never a traceback (canary-safe)
            failures += 1
            print(f"  case {i} ({name}) FAIL — harness/setup error: {type(exc).__name__} (details redacted; canary never printed)")
        finally:
            if fix is not None:
                shutil.rmtree(fix.parent, ignore_errors=True)

    # H-01b-F builder cases (F-011/F-012): the suite's OWN fixture machinery is
    # under test — bounded copy, cleanup established BEFORE construction, and a
    # sanitized refusal (fixed diagnostic + the cause's class name only). A
    # secret-shaped FILENAME breaking construction is value material: it must
    # never reach stdout/stderr. These run in-process against disposable
    # poisoned sources; class names are compared AS NAMES so the case fails
    # cleanly (not with a NameError) when the API is absent at the predecessor.
    def _iso_roots() -> set:
        return {p.name for p in Path(tempfile.gettempdir()).glob("arivoo-iso-*")}

    def b5_copy_failure_sanitized_and_cleaned() -> list:
        src = Path(tempfile.mkdtemp(prefix="arivoo-iso-poison-"))
        try:
            (src / "readable.txt").write_text("ok\n", encoding="utf-8")
            locked = src / CANARY_LINK              # a secret-shaped FILENAME (value material)
            locked.write_text("x\n", encoding="utf-8")
            locked.chmod(0)                          # unreadable: the copy must fail here
            before = _iso_roots()
            buf_out, buf_err = io.StringIO(), io.StringIO()
            raised = None
            message = ""
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                try:
                    _fixture(source=src)
                except Exception as exc:
                    raised = type(exc).__name__
                    message = str(exc)
            blob = buf_out.getvalue() + buf_err.getvalue()
            problems = []
            if raised != "FixtureBuildError":
                problems.append(f"raised {raised or 'nothing'} — expected the sanitized FixtureBuildError (F-012)")
            if message != _WRAPPER_REFUSAL:            # R-03(4): the FIXED message asserted directly
                problems.append("the sanitized refusal's fixed message is WRONG — "
                                "expected the wrapper's exact fixed diagnostic (R-03(4): the predecessor "
                                "kept the type only and discarded the message)")
            if str(src) in message or str(src) in blob:
                problems.append("the refusal diagnostic carried a PATH (F-012)")
            if CANARY_LINK in message or CANARY_LINK in blob:
                problems.append("CANARY VALUE LEAKED INTO OUTPUT")
            if _iso_roots() - before:
                problems.append("a fixture temp root SURVIVED the failed construction — cleanup was not established before construction (F-011)")
            return problems
        finally:
            shutil.rmtree(src, ignore_errors=True)

    def b6_builder_budget_exhaustion() -> list:
        src = Path(tempfile.mkdtemp(prefix="arivoo-iso-poison-"))
        try:
            (src / "a.bin").write_bytes(b"a" * 700)
            (src / "b.bin").write_bytes(b"b" * 700)   # 1400 bytes declared > the injected total
            before = _iso_roots()
            buf_out, buf_err = io.StringIO(), io.StringIO()
            raised = None
            message = ""
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                try:
                    _fixture(source=src, total=1024)
                except Exception as exc:
                    raised = type(exc).__name__
                    message = str(exc)
            blob = buf_out.getvalue() + buf_err.getvalue()
            problems = []
            if raised != "FixtureBuildError":
                problems.append(f"raised {raised or 'nothing'} — expected the sanitized FixtureBuildError (F-011 budget)")
            if message != _WRAPPER_REFUSAL:            # R-03(4): the FIXED message asserted directly
                problems.append("the sanitized refusal's fixed message is WRONG — "
                                "expected the wrapper's exact fixed diagnostic (R-03(4))")
            if str(src) in message or str(src) in blob:
                problems.append("the refusal diagnostic carried a PATH (F-012)")
            if _iso_roots() - before:
                problems.append("a fixture temp root SURVIVED the refused construction (F-011)")
            return problems
        finally:
            shutil.rmtree(src, ignore_errors=True)

    # R-03 (the G-51 hardening) — the four new tool-contract cases. B7/B8 run
    # the two bounded-open helpers against a FIFO in DISPOSABLE CHILD PROCESSES
    # (bounded by the parent's timeout: the predecessor's blocking open hangs,
    # and the timeout is what turns the hang into a NAMED RED); B9/B10 exercise
    # the builder's walk fail-close and the directory-entry budget in-process
    # (the B5 pattern: disposable poisoned sources, never the real repo).
    def b7_checker_bounded_open_nonblocking() -> list:
        beside = Path(__file__).resolve().parent
        probe = Path(tempfile.mkdtemp(prefix="arivoo-iso-probe-"))
        try:
            fifo = probe / "swapped.fifo"
            os.mkfifo(fifo)                        # the lstat-regular -> FIFO swap, realized
            try:
                r = subprocess.run(
                    [sys.executable, "-I", "-c", _BOUNDED_OPEN_PROBE,
                     str(beside / "isolation_check.py"), str(fifo)],
                    capture_output=True, text=True, timeout=10)
            except subprocess.TimeoutExpired:
                return ["the CHECKER's bounded open did NOT return against a FIFO within "
                        "10s — the open is BLOCKING (the FIFO-swap hang class, R-03(1)); "
                        "O_NONBLOCK is missing"]
            if r.returncode != 0:
                return [f"the probe child exited {r.returncode} — the checker's "
                        "_open_regular_nofollow is missing or raised (the API-absent refusal)"]
            if "PROBE-REFUSED" not in r.stdout:
                return ["the checker's bounded open did not REFUSE the FIFO with the "
                        "ISREG check — opened it or returned wrong (R-03(1))"]
            return []
        finally:
            shutil.rmtree(probe, ignore_errors=True)

    def b8_suite_bounded_open_nonblocking() -> list:
        beside = Path(__file__).resolve().parent
        probe = Path(tempfile.mkdtemp(prefix="arivoo-iso-probe-"))
        try:
            fifo = probe / "swapped.fifo"
            os.mkfifo(fifo)
            try:
                r = subprocess.run(
                    [sys.executable, "-I", "-c", _BOUNDED_OPEN_PROBE,
                     str(beside / "isolation_selftest.py"), str(fifo)],
                    capture_output=True, text=True, timeout=10)
            except subprocess.TimeoutExpired:
                return ["the SUITE's own bounded open did NOT return against a FIFO within "
                        "10s — the open is BLOCKING (the FIFO-swap hang class, R-03(1)); "
                        "O_NONBLOCK is missing"]
            if r.returncode != 0:
                return [f"the probe child exited {r.returncode} — the suite's own "
                        "_open_regular_nofollow is missing or raised (the API-absent refusal)"]
            if "PROBE-REFUSED" not in r.stdout:
                return ["the suite's own bounded open did not REFUSE the FIFO with the "
                        "ISREG check — opened it or returned wrong (R-03(1))"]
            return []
        finally:
            shutil.rmtree(probe, ignore_errors=True)

    def b9_builder_walk_unreadable_dir_fails_closed() -> list | None:
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            print("    (skip under root: chmod-0 cannot make a directory unreadable to "
                  "root — CAP_DAC_OVERRIDE; the case engages on the non-root CI runners; "
                  "the R-02 test_20 precedent, stated here per LAW-04)")
            return None
        src = Path(tempfile.mkdtemp(prefix="arivoo-iso-poison-"))
        try:
            (src / "readable.txt").write_text("ok\n", encoding="utf-8")
            sub = src / "locked-subtree"
            sub.mkdir()
            (sub / "inside.txt").write_text("hidden\n", encoding="utf-8")
            sub.chmod(0)                            # unreadable: the walk must refuse, never drop
            before = _iso_roots()
            raised = None
            message = ""
            try:
                _fixture(source=src)
            except Exception as exc:
                raised = type(exc).__name__
                message = str(exc)
            problems = []
            if raised != "FixtureBuildError":
                problems.append(f"raised {raised or 'nothing'} — the unreadable subtree was "
                                "SILENTLY DROPPED from the fixture copy at the predecessor (R-03(2): "
                                "os.walk without onerror) — a false-complete fixture is the false-green class")
            if message and message != _WRAPPER_REFUSAL:
                problems.append("the sanitized refusal's fixed message is WRONG (R-03(4))")
            if _iso_roots() - before:
                problems.append("a fixture temp root SURVIVED the refused construction (F-011)")
            return problems
        finally:
            # the #63 review round (Greptile P2 + CodeRabbit Minor, independently
            # confirmed): a 0-mode directory cannot be scandir'd, so rmtree left the
            # poisoned source behind on every non-root run — restore readability
            # BEFORE the cleanup, never accumulating unreadable temp dirs
            try:
                (src / "locked-subtree").chmod(0o755)
            except OSError:
                pass
            shutil.rmtree(src, ignore_errors=True)

    def b10_builder_directory_entries_charge_the_budget() -> list:
        src = Path(tempfile.mkdtemp(prefix="arivoo-iso-poison-"))
        try:
            for i in range(8):
                (src / f"dir-{i:02d}").mkdir()      # 8 empty dirs + the root vs a 4-entry budget
            before = _iso_roots()
            raised = None
            try:
                _fixture(source=src, count=4)
            except Exception as exc:
                raised = type(exc).__name__
            problems = []
            if raised != "FixtureBuildError":
                problems.append(f"raised {raised or 'nothing'} — directory creation charged "
                                "NO entry budget at the predecessor (R-03(3)): 9 directories "
                                "constructed under a 4-entry budget")
            if _iso_roots() - before:
                problems.append("a fixture temp root SURVIVED the refused construction (F-011)")
            return problems
        finally:
            shutil.rmtree(src, ignore_errors=True)

    print()
    print("builder cases (the suite's own fixture machinery — in-process, sanitized):")
    for name, fn in (
        ("B5 builder copy failure: sanitized refusal (fixed message asserted) + cleanup-before-construction + secret-shaped name never leaks", b5_copy_failure_sanitized_and_cleaned),
        ("B6 builder budget exhaustion: sanitized refusal (fixed message asserted) + cleanup + no path in the diagnostic", b6_builder_budget_exhaustion),
        ("B7 the CHECKER's bounded open is non-blocking: a FIFO swap is refused promptly, never a hang (R-03(1))", b7_checker_bounded_open_nonblocking),
        ("B8 the SUITE's own bounded open is non-blocking: a FIFO swap is refused promptly, never a hang (R-03(1))", b8_suite_bounded_open_nonblocking),
        ("B9 the builder's walk fails CLOSED on an unreadable directory: never a silently-dropped subtree (R-03(2))", b9_builder_walk_unreadable_dir_fails_closed),
        ("B10 the builder's directory creation charges the entry budget (R-03(3))", b10_builder_directory_entries_charge_the_budget),
    ):
        try:
            problems = fn()
        except Exception as exc:  # sanitized: never a traceback
            problems = [f"harness exception: {type(exc).__name__} (sanitized)"]
        if problems is None:
            print(f"  {name} SKIP — declared, reason printed above (never a vacuous pass, never a failure under root)")
        elif problems:
            failures += 1
            print(f"  {name} FAIL — {'; '.join(problems)}")
        else:
            print(f"  {name} PASS — the tool contract held (sanitized, bounded, fail-closed)")

    print()
    if failures:
        print(f"SELF-TEST RED — {failures} case(s) failed: the diagnostic path does not prove the stated properties (Slice 10.2 + H-01b-F + R-03).")
        return 1
    print("SELF-TEST GREEN — every negative case failed with an attributable RED, every positive case stayed green,")
    print("benign username-only remotes never false-flag, no synthetic canary appeared in stdout or stderr,")
    print("tracked symlinks are scanned as link text with the target never opened, scan/fixture budgets hold,")
    print("both bounded-open helpers refuse a FIFO swap without blocking, the builder's walk fails closed on")
    print("unreadable subtrees, directory creation charges the entry budget, the sanitized refusal carries its")
    print("fixed message, and a failed fixture construction cleans up and prints a sanitized refusal only.")
    print("Limit, stated: a pattern scan proves these specified leak classes are caught — never that every secret is absent")
    print("(record 16 §4.1 carries the host-permission side of the isolation claim).")
    return 0




if __name__ == "__main__":
    # H-01b-F (F-012): the standalone entry's sanitized exception boundary — a
    # harness crash prints ONE sanitized line (the exception's class name only),
    # never a traceback that could carry a canary or a path. SystemExit (the
    # honest exit-code carrier) is not an Exception and propagates untouched.
    try:
        sys.exit(self_test())
    except Exception as exc:  # noqa: BLE001 — the boundary is the point
        print(f"SELF-TEST ABORTED — harness exception ({type(exc).__name__}); sanitized boundary: no traceback, no paths (H-01b-F, F-012)")
        sys.exit(1)
