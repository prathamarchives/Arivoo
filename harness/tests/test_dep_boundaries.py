#!/usr/bin/env python3
"""test_dep_boundaries.py — CLAIM-090: the LAW-08 approval + the scoped boundary.
RED-first: before scope.py's upgrade the boundary rule did not exist (ARV-DEP-009
was impossible), so the wrong-place import PASSED — the RED state. The upgrade
makes it fail closed. The suite asserts both directions."""
import os, pathlib, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from harness import scope  # noqa: E402

FAILS: list[str] = []

def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)

def run_check_deps_in(tree: pathlib.Path) -> list[str]:
    # run check_deps with REPO pointed at the tree (it reads approved_deps + walks harness/)
    old = os.getcwd()
    os.chdir(tree)
    try:
        scope.REPO = tree
        out = []
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = scope.check_deps()
        return [f for f in out if f.startswith("ARV-DEP-")]
    finally:
        os.chdir(old)

def mk_tree(approved: str, harness_files: dict) -> pathlib.Path:
    tree = pathlib.Path(tempfile.mkdtemp(prefix="arv_dep_"))
    (tree/"harness").mkdir()
    (tree/"harness/approved_deps.txt").write_text(approved)
    for rel, text in harness_files.items():
        p = tree/rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return tree

APPROVED = "fastapi 0.164.0 harness/api/\njwt 2.15.1 harness/api/\n"

def main() -> int:
    # 1) the approval registry exists and is honored (ARV-DEP-008 still fires without it)
    t = mk_tree("# empty registry\n", {"harness/api/app.py": "import fastapi\n"})
    fs = run_check_deps_in(t)
    check("ARV-DEP-010", any("ARV-DEP-008" in f for f in fs),
          "an unapproved import still refuses (the registry governs)",
          "keep approved_deps.txt as the single LAW-08 registry")

    # 2) the boundary rule: the SAME import outside its boundary refuses
    t = mk_tree(APPROVED, {"harness/kernel_side.py": "import fastapi\n"})
    fs = run_check_deps_in(t)
    check("ARV-DEP-009", any("ARV-DEP-009" in f and "kernel_side" in f for f in fs),
          "fastapi outside harness/api/ refuses (the approval is scoped)",
          "move the import into its approved boundary")

    # 3) inside the boundary it passes
    t = mk_tree(APPROVED, {"harness/api/app.py": "import fastapi\nimport jwt\n"})
    fs = run_check_deps_in(t)
    check("ARV-DEP-011", not fs,
          "the approved imports inside harness/api/ pass cleanly",
          "the boundary rule must not over-block its own approval")

    # 4) the real repo's own tree passes (the lock is consistent with the code)
    fs = run_check_deps_in(REPO)
    check("ARV-DEP-012", not fs,
          "the repository's current imports are all approved and in-boundary",
          "fix the flagged import or extend the approval with a note")

    # 5) the lock's pin set matches the registry (no drift)
    lock = (REPO/"harness/api/requirements.lock").read_text()
    reg = (REPO/"harness/approved_deps.txt").read_text()
    missing = [ln.split()[0] for ln in reg.splitlines()
               if ln.strip() and not ln.startswith("#")
               and f"{ln.split()[1]}" not in lock]
    check("ARV-DEP-013", not missing,
          "every registry pin appears in requirements.lock (no pin drift)",
          "re-pin the lock; the registry and the lock are ONE decision")

    print()
    if FAILS:
        print("RED — the dependency boundary suite refuses:", ", ".join(FAILS))
        return 1
    print("GREEN — the dependency boundary suite passes (5 checks)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
