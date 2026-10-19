#!/usr/bin/env python3
"""harness/tests/test_gate_dispatch.py — H-01a regression: PR dispatch/Git fail-closed.

The card (PLAN 'H-01a', INT-125/D-039; audit findings A01/A02/A10):
  A01  a PR head WITHOUT a scope declaration must reach a REAL gate refusal
       (ARV-SCOPE-001 / ARV-CLM-005 / ARV-PRF-002) — NEVER the main-selfcheck
       fallback (the no-diff path prints 'main-selfcheck'; this suite asserts
       that string is ABSENT from every PR-mode refusal).
  A02  CI event fields are UNTRUSTED: the dispatcher receives them via
       environment (never template interpolation) and refuses hostile branch
       metadata with ARV-DISPATCH-001 before any gate execution — a
       Git-legal hostile name must not execute as shell syntax.
  A10  git failures are failures: a failed diff/rev-parse refuses with
       ARV-DIFF-001; a base with no merge-base with HEAD refuses with
       ARV-DIFF-002 — never an empty-diff vacuous pass.

These tests exercise the REAL dispatcher (harness/dispatch.py, as a subprocess
— the same command CI runs) and the REAL scope.py git path. A dummy module
that exits 0 cannot pass: every case asserts a named refusal code in the
output plus the exact exit shape.

RED state at the predecessor (026fead..6cdd458): harness/dispatch.py does not
exist (subprocess fails) and scope.diff_paths returns [] on git failure
(wrong behavior observed directly). Both RED forms are meaningful: the A10
cases fail on ACTUAL wrong behavior of the existing code, not just absence.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILED = []


def check(name: str, ok: bool, detail: str = "") -> None:
    tag = "PASS" if ok else "FAIL"
    print(f"{tag} {name}: {detail}")
    if not ok:
        FAILED.append(name)


def run_dispatch(cwd: pathlib.Path, env_extra: dict) -> subprocess.CompletedProcess:
    """Invoke the REAL dispatcher exactly as CI does (env-passed context)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("ARV_")}
    env.update(env_extra)
    return subprocess.run([sys.executable, "harness/dispatch.py"], cwd=cwd,
                          capture_output=True, text=True, timeout=900, env=env)


def fixture_clone(tmp: str, name: str) -> pathlib.Path:
    """A real git clone of this repo (full history — the merge-base must be
    decidable), mutated per case. The clone is the candidate tree the
    dispatcher judges."""
    d = pathlib.Path(tmp) / name
    subprocess.run(["git", "clone", "-q", "--no-local", str(REPO), str(d)],
                   check=True, capture_output=True, timeout=300)
    # detach from the branch we cloned: the dispatcher derives the slice from
    # ARV_PR_HEAD, not from the checked-out state.
    return d


def pr_refusal(r: subprocess.CompletedProcess, code: str, label: str) -> None:
    """Every PR-mode case: nonzero exit + the named code + NEVER selfcheck."""
    out = r.stdout + r.stderr
    check(f"{label} exits nonzero", r.returncode != 0, f"exit={r.returncode}")
    check(f"{label} names {code}", code in out, f"got: {out.strip()[:300]}")
    check(f"{label} never falls back to selfcheck", "main-selfcheck" not in out,
          "the A01 bypass: a PR must be judged as a PR")


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="arv_h01a_")
    try:
        # ---- A02: hostile branch metadata is refused as DATA, never executed ----
        # Git-legal branch name carrying a shell breakout (double quotes are
        # allowed in ref names; the OLD dispatch interpolated them into a
        # generated script).
        hostile = 'slice/x"; echo ARV_PWNED_MARKER; "y'
        d = fixture_clone(tmp, "hostile")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request", "ARV_PR_HEAD": hostile})
        out = r.stdout + r.stderr
        pr_refusal(r, "ARV-DISPATCH-001", "A02-hostile-branch")
        check("A02-hostile-branch executes nothing", "ARV_PWNED_MARKER" not in out,
              "the breakout payload must never run as script")
        check("A02-hostile-branch creates no side-effect file",
              not (d / "ARV_PWNED_MARKER").exists(), "a `touch` payload must not land")

        # ---- A01: PR mode without a scope declaration -> real gate refusal ----
        d = fixture_clone(tmp, "noscope")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                             "ARV_PR_HEAD": "slice/claim-999-no-such-slice"})
        pr_refusal(r, "ARV-SCOPE-001", "A01-missing-scope")

        # ---- A01: scope declared but the branch carries NO open claim row ----
        d = fixture_clone(tmp, "noclaim")
        sd = d / "harness" / "runs" / "claim-999-unclaimed"
        sd.mkdir(parents=True)
        (sd / "scope.txt").write_text("harness/tests INT-125/D-039\n")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                             "ARV_PR_HEAD": "slice/claim-999-unclaimed"})
        pr_refusal(r, "ARV-CLM-005", "A01-unclaimed-branch")

        # ---- A01: claimed + scoped but NO proof sheet -> the gate refuses it ----
        d = fixture_clone(tmp, "nosheet")
        sd = d / "harness" / "runs" / "claim-999-nosheet"
        sd.mkdir(parents=True)
        (sd / "scope.txt").write_text("harness/tests INT-125/D-039\n")
        reg = d / "CLAIMS.md"
        row = ("| CLAIM-999 | 20 | test | `slice/claim-999-nosheet` | "
               "`harness/tests/test_gate_dispatch.py` | — | 2026-10-19 | probe |\n")
        text = reg.read_text()
        anchor = "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        reg.write_text(text.replace(anchor, anchor + row, 1))
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                              "ARV_PR_HEAD": "slice/claim-999-nosheet"})
        pr_refusal(r, "ARV-PRF", "A01-missing-sheet")

        # ---- positive: a scoped, claimed, sheeted slice dispatches the gate green ----
        d = fixture_clone(tmp, "positive")
        sname = "claim-999-positive"
        sd = d / "harness" / "runs" / sname
        sd.mkdir(parents=True)
        # declare a scope that covers the diff of an EMPTY slice (no commits ->
        # the triple-dot diff vs origin/main is empty: every check passes
        # vacuously-legitimately; the sheet below carries the honest runs)
        (sd / "scope.txt").write_text("# positive probe\n")
        (sd / "run-01.json").write_text(
            '{"command": "probe", "exit_code": 0, "commit": "' + "0" * 40 + '", '
            '"output_sha256": "' + "0" * 64 + '", "recorded_at": "2026-10-19T00:00:00+00:00"}\n')
        (sd / "notverified.txt").write_text("- probe only\n")
        reg = d / "CLAIMS.md"
        text = reg.read_text()
        row = ("| CLAIM-999 | 20 | test | `slice/" + sname + "` | `harness/tests` | "
               "— | 2026-10-19 | probe |\n")
        reg.write_text(text.replace(anchor, anchor + row, 1))
        # assemble the sheet from the record using the FIXTURE's own module
        sys.path.insert(0, str(d))
        try:
            import importlib
            ps = importlib.import_module("harness.proofsheet")
            ps.REPO = d
            ps.RUNS = d / "harness" / "runs"
            (sd / "proofsheet.md").write_text(ps.assemble(sname, "- probe only\n"))
        except SystemExit:
            raise AssertionError("fixture sheet assembly failed")
        finally:
            sys.path.remove(str(d))
            for mod in [m for m in list(sys.modules) if m.startswith("harness")]:
                del sys.modules[mod]
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                             "ARV_PR_HEAD": "slice/" + sname})
        out = r.stdout + r.stderr
        check("positive-claimed-PR dispatches green", r.returncode == 0,
              f"exit={r.returncode}: {out.strip()[-400:]}")
        check("positive-PR is judged as a PR", "slice=" + sname in out,
              "the gate ran on the named slice, not selfcheck")

        # ---- the main-push surface stays intact: push -> selfcheck, never PR mode ----
        r = run_dispatch(d, {"ARV_EVENT_NAME": "push"})
        out = r.stdout + r.stderr
        check("push-selfcheck stays green", r.returncode == 0,
              f"exit={r.returncode}: {out.strip()[-200:]}")
        check("push-selfcheck names itself", "main-selfcheck" in out,
              "the --no-diff main surface is unchanged by H-01a")

        # ---- A10: a FAILED git operation refuses (ARV-DIFF-001), never [] ----
        # actual-wrong-behavior RED at the predecessor: diff_paths returns [].
        sys.path.insert(0, str(REPO))
        import harness.scope as scope  # noqa: E402
        refused = False
        code = ""
        try:
            scope.diff_paths("refs/heads/no-such-base-xyz-12345")
        except Exception as exc:  # the refusal must be an exception carrying the code
            refused = True
            code = str(exc)
            if not isinstance(exc, Exception):
                refused = False
        check("A10-git-failure refuses with ARV-DIFF-001",
              refused and "ARV-DIFF-001" in code,
              f"refused={refused} code={code[:200]!r}")

        # ---- A10: no merge base with the declared base (ARV-DIFF-002) ----
        u = pathlib.Path(tmp) / "unrelated"
        u.mkdir()
        def gitu(*args):
            subprocess.run(["git"] + list(args), cwd=u, check=True,
                           capture_output=True, timeout=60)
        gitu("init", "-q", "-b", "main")
        gitu("config", "user.email", "t@t"); gitu("config", "user.name", "t")
        (u / "a.txt").write_text("root A\n")
        gitu("add", "-A"); gitu("commit", "-qm", "root A")
        gitu("checkout", "-q", "--orphan", "other")
        (u / "a.txt").unlink(); (u / "b.txt").write_text("root B\n")
        gitu("add", "-A"); gitu("commit", "-qm", "root B")
        gitu("checkout", "-q", "main")  # HEAD and 'other' are now unrelated roots
        refused = False
        code = ""
        try:
            scope.diff_paths("other", repo=u)
        except Exception as exc:
            refused = True
            code = str(exc)
        check("A10-no-merge-base refuses with ARV-DIFF-002",
              refused and "ARV-DIFF-002" in code,
              f"refused={refused} code={code[:200]!r}")

        # ---- A10 positive: a valid base yields the real changed paths ----
        try:
            paths = scope.diff_paths("HEAD", repo=REPO)
            check("A10-valid-base returns a list (no exception)", isinstance(paths, list),
                  f"paths={type(paths)}")
        except Exception as exc:  # the refusal is the RED form at the predecessor
            check("A10-valid-base returns a list (no exception)", False,
                  f"refused: {exc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILED:
        print(f"RED — {len(FAILED)} failure(s): {', '.join(FAILED)}")
        print("      H-01a: the PR dispatch must fail closed (A01/A02/A10 — PLAN's frozen card)")
        return 1
    print("GREEN — the dispatch is fail-closed: PR obligations judged on every PR; "
          "hostile metadata refused as data; git failures refuse, never empty-diff")
    return 0


if __name__ == "__main__":
    sys.exit(main())
