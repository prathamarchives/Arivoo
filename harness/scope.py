#!/usr/bin/env python3
"""harness/scope.py — the SIZE/SCOPE/boundary checks (S4; D-036; LAW-05/06/24/08).

check_size(diff)      LAW-05: one slice changes one behavior inside the size limits
check_scope(diff, decl) LAW-06/07: only declared paths; protected paths need an owner ref
lint_boundary()       LAW-24: ambient time/IDs/randomness only inside adapters/
check_deps()          LAW-08: zero third-party imports without an approval entry

Every failure prints a named code + repair (diagnostics contract).
"""
import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


class GitRefusal(Exception):
    """A failed git operation is a REFUSAL, never an empty diff (H-01a/A10).

    Carries the named code in its message: ARV-DIFF-001 (the git operation
    failed) / ARV-DIFF-002 (no merge-base between the declared base and HEAD —
    invalid base or insufficient graph history). The gate catches this and
    refuses; the predecessor returned [] silently, which read as a compliant
    empty diff (the vacuous-pass defect, reproduced RED in test_gate_dispatch).
    """


def _git(args: list, repo=None):
    """Run git, refusing on failure (ARV-DIFF-001) instead of trusting stdout."""
    import subprocess
    r = subprocess.run(["git"] + args, cwd=repo or REPO,
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise GitRefusal(
            f"ARV-DIFF-001: git {' '.join(args[:2])} failed (exit {r.returncode}): "
            f"{(r.stderr or r.stdout).strip()[:200]}")
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
    producing a compliant-looking empty diff."""
    import subprocess
    r = subprocess.run(["git", "merge-base", base, "HEAD"], cwd=repo or REPO,
                       capture_output=True, text=True, timeout=60)
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
    """Changed paths (git diff base...HEAD), for the scope check. Fail-closed (A10)."""
    ensure_merge_base(base, repo)
    return [l for l in _git(["diff", "--name-only", f"{base}...HEAD"], repo).stdout.splitlines() if l]


def diff_stats(base: str, repo=None) -> list:
    """Per-path added lines, honestly classified: SOURCE = .py non-test; TEST =
    test_*.py; MIGRATION = 1-per-slice; everything else = DATA (evidence
    artifacts — not source lines, but still gated by the SCOPE check).
    Fail-closed (A10): a failed diff refuses, never a compliant empty one."""
    ensure_merge_base(base, repo)
    r = _git(["diff", "--numstat", f"{base}...HEAD"], repo)
    out = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            add = int(parts[0]) if parts[0].isdigit() else 0
            path = parts[2]
            if TEST_RE.search(path):
                out.append({"path": path, "src_lines": 0, "test_lines": add, "fixture_lines": 0})
            elif MIGRATION_RE.match(path):
                out.append({"path": path, "src_lines": 0, "test_lines": 0, "fixture_lines": 0})
            elif SOURCE_RE.search(path):
                out.append({"path": path, "src_lines": add, "test_lines": 0, "fixture_lines": 0})
            else:
                out.append({"path": path, "src_lines": 0, "test_lines": 0, "fixture_lines": 0})
    return out


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
            if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix):
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
