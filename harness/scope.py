#!/usr/bin/env python3
"""harness/scope.py — the SIZE/SCOPE/boundary checks (S4; D-036; LAW-05/06/24/08).

check_size(diff)      LAW-05: one slice changes one behavior inside the size limits
check_scope(diff, decl) LAW-06/07: only declared paths; protected paths need an owner ref
lint_boundary()       LAW-24: ambient time/IDs/randomness only inside adapters/
check_deps()          LAW-08: zero third-party imports without an approval entry

Every failure prints a named code + repair (diagnostics contract).
"""
import ast
import os
import pathlib
import re
import sys


def _repo_root() -> pathlib.Path:
    """H-01b-CI (session 23): ARV_TRUSTED_ROOT re-roots this machinery onto the
    candidate tree when the trusted gate driver has validated it (absolute
    existing dir only; anything else keeps the natural root)."""
    root = os.environ.get("ARV_TRUSTED_ROOT", "")
    p = pathlib.Path(root) if root else None
    if p is not None and p.is_absolute() and p.is_dir():
        return p
    return pathlib.Path(__file__).resolve().parents[1]


REPO = _repo_root()


class GitRefusal(Exception):
    """A failed or hung git operation is a REFUSAL, never an empty diff (H-01a/A10;
    H-01a-R for the timeout).

    Carries the named code in its message: ARV-DIFF-001 (the git operation
    failed) / ARV-DIFF-002 (no merge-base between the declared base and HEAD —
    invalid base or insufficient graph history) / ARV-DIFF-003 (the subprocess
    timed out — a hung git operation is a named refusal, never an unnamed
    TimeoutExpired crash). The gate catches this and refuses; the predecessor
    returned [] silently, which read as a compliant empty diff (the
    vacuous-pass defect, reproduced RED in test_gate_dispatch).
    """


def _git(args: list, repo=None):
    """Run git, refusing on failure (ARV-DIFF-001) or a hang (ARV-DIFF-003).

    R-04(5): the output is BYTES. The -z records carry RAW filename bytes —
    the predecessor's text-mode read applied a strict locale decode (a
    non-UTF-8 filename CRASHED with UnicodeDecodeError) and universal-newline
    translation (a literal CR inside a name was rewritten to LF). The callers
    decode identity-bearing path fields with os.fsdecode (surrogateescape,
    the OS round-trip); DIAGNOSTIC text in refusals decodes with
    errors='replace' — a refusal message may be lossy, an identity never is."""
    import subprocess
    try:
        r = subprocess.run(["git"] + args, cwd=repo or REPO,
                           capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise GitRefusal(
            f"ARV-DIFF-003: git {' '.join(args[:2])} exceeded the 60s timeout — "
            "a hung git operation is a named refusal, never an unnamed crash (H-01a-R)")
    if r.returncode != 0:
        diag = ((r.stderr or r.stdout) or b"").decode("utf-8", "replace").strip()[:200]
        raise GitRefusal(
            f"ARV-DIFF-001: git {' '.join(args[:2])} failed (exit {r.returncode}): "
            f"{diag}")
    return r

# LAW-05's size limits (LAWS.md). Editing these constants is a constraint-weakening
# change (LAW-09) — they live in harness/ (a protected path), so the scope check
# flags any edit without an owner-referenced declaration.
SIZE_LIMITS = {
    "source_files": 8, "source_lines": 400, "test_files": 6,
    "test_lines": 800, "fixture_lines": 200, "requirement_ids": 3,
    "migrations": 1, "context_pack_tokens": 12000,
}

# LAW-07's protected paths (Phase-2 instantiation): edits require an owner-referenced
# scope line ("path-prefix  INT-xxx/D-xxx").
PROTECTED = ("harness/", ".github/", "tools/", "INTENT-LEDGER", "DECISIONS",
             "context/WORKLOG", "harness/migrations/")

TEST_RE = re.compile(r"(^|/)test_[^/]+\.py$")
MIGRATION_RE = re.compile(r"^harness/migrations/\d{4}_.*\.sql$")
SOURCE_RE = re.compile(r"\.py$")


def ensure_merge_base(base: str, repo=None) -> str:
    """ARV-DIFF-002: the declared base must share history with HEAD (A10).

    A triple-dot diff with no merge-base is a failure condition, not a no-op:
    refusing here keeps an invalid base or a shallow/incomplete graph from
    producing a compliant-looking empty diff. A hung merge-base probe is a
    named refusal too (ARV-DIFF-003, H-01a-R)."""
    import subprocess
    try:
        r = subprocess.run(["git", "merge-base", base, "HEAD"], cwd=repo or REPO,
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise GitRefusal(
            f"ARV-DIFF-003: git merge-base for base '{base}' exceeded the 60s timeout — "
            "a hung git operation is a named refusal, never an unnamed crash (H-01a-R)")
    if r.returncode == 1 and not (r.stderr or "").strip():
        # git's own no-merge-base signal: exit 1, empty output
        raise GitRefusal(
            f"ARV-DIFF-002: no merge-base between '{base}' and HEAD — an invalid base or "
            "insufficient graph history; refusing rather than treating it as an empty diff")
    if r.returncode != 0:
        raise GitRefusal(
            f"ARV-DIFF-001: git merge-base failed for base '{base}' (exit {r.returncode}): "
            f"{(r.stderr or '').strip()[:160]}")
    if not r.stdout.strip():
        raise GitRefusal(
            f"ARV-DIFF-002: no merge-base between '{base}' and HEAD — an invalid base or "
            "insufficient graph history; refusing rather than treating it as an empty diff")
    return r.stdout.strip()


def diff_paths(base: str, repo=None) -> list:
    """Changed paths (git diff base...HEAD), for the scope check. Fail-closed (A10).
    H-01c-claims (F-001, session 23): MACHINE-SAFE identity — NUL-delimited
    records (a space/unicode/newline name arrives as exact bytes, never git's
    human rendering: quoted and octal-escaped), rename detection ON so BOTH
    endpoints are in the identity (the old name is part of what changed:
    --name-only ever showed only the destination).
    R-04(5): the -z output parses as BYTES and each path decodes through
    os.fsdecode (surrogateescape) — identity preserved byte-for-byte: a
    non-UTF-8 or CR-bearing filename arrives WHOLE, never a strict-decode
    crash and never a universal-newline rewrite."""
    ensure_merge_base(base, repo)
    out = _git(["diff", "--name-status", "-z", "--find-renames", f"{base}...HEAD"], repo).stdout
    paths: list[str] = []
    parts = out.split(b"\0")
    i = 0
    while i < len(parts):
        rec = parts[i]
        if not rec:
            i += 1
            continue
        status = rec[0:1]
        npaths = 2 if status in (b"R", b"C") else 1   # rename/copy records carry BOTH endpoints
        for j in range(1, npaths + 1):
            if i + j < len(parts) and parts[i + j]:
                paths.append(os.fsdecode(parts[i + j]))
        i += 1 + npaths
    seen, uniq = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def diff_stats(base: str, repo=None) -> list:
    """Per-path added lines, honestly classified: SOURCE = .py non-test; TEST =
    test_*.py; MIGRATION = 1-per-slice; everything else = DATA (evidence
    artifacts — not source lines, but still gated by the SCOPE check).
    Fail-closed (A10): a failed diff refuses, never a compliant empty one.
    H-01c-claims (F-001, session 23): NUL-delimited records — the human
    numstat format QUOTES exotic names (undercounting stats against the
    canonical identity); a rename/copy record carries BOTH endpoints after an
    empty in-record path field (probed live: '0\t0\t\0old\0new\0').
    R-04(4): the numstat record splits on the FIRST TWO TABS ONLY — the path
    field is everything after 'added<TAB>deleted<TAB>', so a literal TAB
    inside a filename arrives WHOLE instead of truncating the identity at the
    tab (the predecessor split on every tab).
    R-04(5): bytes + os.fsdecode — same identity rule as diff_paths.
    R-04(6): a rename/copy counts its added lines ONCE, under the DESTINATION
    endpoint; the old endpoint STAYS in the diff identity (scope coverage)
    but contributes 0 lines — the predecessor emitted the full added count on
    BOTH endpoints, double-counting every rename into the size gate."""
    ensure_merge_base(base, repo)
    out = _git(["diff", "--numstat", "-z", "--find-renames", f"{base}...HEAD"], repo).stdout
    result = []
    parts = out.split(b"\0")
    i = 0
    while i < len(parts):
        rec = parts[i]
        if not rec:
            i += 1
            continue
        i += 1
        fields = rec.split(b"\t", 2)          # R-04(4): the first two tabs ONLY — the path keeps its own tabs
        add = int(fields[0]) if fields and fields[0].lstrip(b"-").isdigit() else 0
        def emit(path: str, lines: int) -> None:
            if TEST_RE.search(path):
                result.append({"path": path, "src_lines": 0, "test_lines": lines, "fixture_lines": 0})
            elif MIGRATION_RE.match(path):
                result.append({"path": path, "src_lines": 0, "test_lines": 0, "fixture_lines": 0})
            elif SOURCE_RE.search(path):
                result.append({"path": path, "src_lines": lines, "test_lines": 0, "fixture_lines": 0})
            else:
                result.append({"path": path, "src_lines": 0, "test_lines": 0, "fixture_lines": 0})
        inline_path = fields[2] if len(fields) > 2 else b""
        if inline_path:
            emit(os.fsdecode(inline_path), add)
        else:
            # rename/copy: BOTH endpoints follow; the added lines count ONCE,
            # under the DESTINATION (the second endpoint) — R-04(6)
            for lines in (0, add):
                if i < len(parts) and parts[i]:
                    emit(os.fsdecode(parts[i]), lines)
                i += 1
    return result


# LAW-24: only adapters may touch time/IDs/randomness.
ADAPTER = "harness/adapters/"
AMBIENT_CALLS = ("time.time", "time.monotonic", "datetime.now", "datetime.today",
                 "uuid.uuid", "random.random", "random.randint", "os.urandom", "secrets.")

# LAW-08: stdlib + harness imports only; anything else needs an approval entry.
STDLIB_ALLOW = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()


def check_size(diff: list) -> list:
    """diff: list of dicts {path, src_lines, test_lines, fixture_lines}."""
    fails = []
    src_files = [d for d in diff if d["src_lines"] > 0 and not TEST_RE.search(d["path"])]
    test_files = [d for d in diff if TEST_RE.search(d["path"])]
    migrations = [d for d in diff if MIGRATION_RE.match(d["path"])]
    if len(src_files) > SIZE_LIMITS["source_files"]:
        fails.append(f"ARV-SIZE-001: {len(src_files)} source files > {SIZE_LIMITS['source_files']} (LAW-05) — split the slice")
    if sum(d["src_lines"] for d in src_files) > SIZE_LIMITS["source_lines"]:
        fails.append(f"ARV-SIZE-002: {sum(d['src_lines'] for d in src_files)} source lines > {SIZE_LIMITS['source_lines']} (LAW-05) — split the slice")
    if len(test_files) > SIZE_LIMITS["test_files"]:
        fails.append(f"ARV-SIZE-003: {len(test_files)} test files > {SIZE_LIMITS['test_files']} (LAW-05)")
    if sum(d["test_lines"] for d in test_files) > SIZE_LIMITS["test_lines"]:
        fails.append(f"ARV-SIZE-004: {sum(d['test_lines'] for d in test_files)} test lines > {SIZE_LIMITS['test_lines']} (LAW-05)")
    if len(migrations) > SIZE_LIMITS["migrations"]:
        fails.append(f"ARV-SIZE-005: {len(migrations)} migrations > {SIZE_LIMITS['migrations']} (LAW-05: one migration per slice)")
    for f in fails:
        print("FAIL " + f)
        print("      repair: one slice changes ONE behavior — move the rest to its own slice (bounded diffs, D-026)")
    return fails


def _declaration(decl_path: pathlib.Path) -> dict:
    """scope.txt: '<path-prefix> [owner-ref]' per line; '#' comments."""
    decl = {}
    if not decl_path.is_file():
        return decl
    for ln in decl_path.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        decl[parts[0].rstrip("/")] = parts[1] if len(parts) > 1 else None
    return decl


def check_scope(diff_paths: list, slice_name: str) -> list:
    """LAW-06 (declared scope) + LAW-07 (protected paths need an owner ref)."""
    fails = []
    decl_path = REPO / "harness" / "runs" / slice_name / "scope.txt"
    decl = _declaration(decl_path)
    if not decl:
        print(f"FAIL ARV-SCOPE-001: no scope declaration for slice '{slice_name}' "
              f"(expected {decl_path}) — every PR declares its bounded diff (D-026/LAW-06)")
        print("      repair: commit the slice's scope.txt (one path-prefix per line; protected prefixes carry the INT-/D- owner ref)")
        return [f"ARV-SCOPE-001:{slice_name}"]
    for path in diff_paths:
        matched = None
        for prefix in decl:
            # H-01c-claims (F-001, session 23): EXPLICIT file/directory
            # semantics — a path matches a declaration only by exact equality
            # or as a directory-boundary descendant. The predecessor's third
            # clause (raw startswith) accepted SIBLING PREFIXES: a declaration
            # for README.md covered README.md.unrelated.
            if path == prefix or path.startswith(prefix + "/"):
                matched = prefix
                break
        if matched is None:
            fails.append(f"ARV-SCOPE-002: {path} is OUTSIDE the declared scope of '{slice_name}' — a scope breach (LAW-06)")
            print(f"FAIL ARV-SCOPE-002: {path} outside the declared scope — scope breach (LAW-06)")
            print("      repair: widen the declaration (with the owner ref if the path is protected) or drop the change from this slice")
            continue
        if any(path == p or path.startswith(p) for p in PROTECTED) and not decl[matched]:
            fails.append(f"ARV-PROT-002: {path} is a PROTECTED path and the declaration line for '{matched}' carries no owner ref (LAW-07)")
            print(f"FAIL ARV-PROT-002: {path} is protected; only an owner-referenced declaration may change it (LAW-07)")
            print("      repair: the scope line must cite the owner intent/decision that authorizes this protected-path change")
    return fails


def lint_boundary() -> list:
    """LAW-24: ambient time/ID/randomness calls only inside harness/adapters/."""
    fails = []
    for py in sorted((REPO / "harness").rglob("*.py")):
        rel = py.relative_to(REPO).as_posix()
        if rel.startswith(ADAPTER) or rel == "harness/adapters/__init__.py":
            continue
        try:
            tree = ast.parse(py.read_text())
        except SyntaxError:
            fails.append(f"ARV-LAW24-001: {rel} does not parse — repair the syntax first")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                try:
                    call = ast.unparse(node.func)
                except Exception:
                    continue
                for amb in AMBIENT_CALLS:
                    if call.startswith(amb):
                        fails.append(f"ARV-LAW24-001: {rel} calls {call} — ambient time/ID/randomness lives ONLY in harness/adapters/ (LAW-24)")
                        print(f"FAIL ARV-LAW24-001: {rel}:{node.lineno} {call} — use adapters/clock, adapters/ids (LAW-24)")
                        print("      repair: import the adapter; the S4 boundary lint is mechanical, not advisory")
                        break
    return fails


def check_deps() -> list:
    """LAW-08: no third-party imports without an approval entry (Phase 2: none exist)."""
    fails = []
    approved = set()
    appr = REPO / "harness" / "approved_deps.txt"
    if appr.is_file():
        approved = {l.split()[0] for l in appr.read_text().splitlines() if l.strip() and not l.startswith("#")}
    for py in sorted((REPO / "harness").rglob("*.py")):
        rel = py.relative_to(REPO).as_posix()
        try:
            tree = ast.parse(py.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    root = a.name.split(".")[0]
                    if root not in STDLIB_ALLOW and root not in approved and root not in ("harness",):
                        fails.append(f"ARV-DEP-008: {rel} imports '{a.name}' — no approved dependency (LAW-08)")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root not in STDLIB_ALLOW and root not in approved and root != "harness":
                    fails.append(f"ARV-DEP-008: {rel} imports from '{node.module}' — no approved dependency (LAW-08)")
    for f in fails:
        print("FAIL " + f)
        print("      repair: use the standard library, or add the dependency with an owner approval entry in harness/approved_deps.txt (LAW-08)")
    return fails
