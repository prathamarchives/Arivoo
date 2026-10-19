#!/usr/bin/env python3
"""harness/tests/test_gate_dispatch.py — H-01a regression: PR dispatch/Git fail-closed.

The card (PLAN 'H-01a', INT-125/D-039; audit findings A01/A02/A10), completed by the
H-01a-R card (PLAN, INT-126/D-040; owner turn 21's §2 bounded completion checks):
  A01  a PR head WITHOUT a scope declaration must reach a REAL gate refusal
       (ARV-SCOPE-001 / ARV-CLM-005 / ARV-PRF-002) — NEVER the main-selfcheck
       fallback (the no-diff path prints 'main-selfcheck'; this suite asserts
       that string is ABSENT from every PR-mode refusal).
  A02  CI event fields are UNTRUSTED: the dispatcher receives them via
       environment (never template interpolation) and refuses hostile branch
       metadata with ARV-DISPATCH-001 before any gate execution. TWO classes,
       labeled honestly: the space-carrying fixture is NOT a `git
       check-ref-format`-legal ref (asserted below — it is parser-boundary
       FUZZING, never claimed an observed Git-ref path); the LEGAL-hostile
       case IS check-ref-format-accepted (asserted below) — a genuinely
       creatable branch carrying a no-space `$(...)`/`${IFS}` breakout.
  A10  git failures are failures: a failed diff/rev-parse refuses with
       ARV-DIFF-001; a base with no merge-base with HEAD refuses with
       ARV-DIFF-002; a hung git subprocess (simulated TimeoutExpired — a real
       hang is never safe to require) refuses with ARV-DIFF-003 — never an
       unnamed crash. H-01a-R's consolidated-refusal contract: an invalid
       base through the ACTUAL caller produces ONE nonzero named refusal,
       NO uncaught traceback, and the branch-claim coverage check does not
       run on the invalid diff (the ARV-CLM-000 skip note is the observable).
       Stated boundary: ARV-DIFF-003 covers scope.py's git operations; a
       suite-runner subprocess timeout remains a process failure (a named
       follow-up if ever observed — the contract is not claimed broader).

These tests exercise the REAL dispatcher (harness/dispatch.py, as a subprocess
— the same command CI runs) and the REAL scope.py git path. A dummy module
that exits 0 cannot pass: every case asserts a named refusal code in the
output plus the exact exit shape.

RED state at the predecessor (2087378..41a4a70): the consolidated-refusal
case fails on the ACTUAL wrong behavior (an uncaught GitRefusal traceback at
gate.py:191 — the claim-coverage diff_paths recompute outside the handler;
the refusal printed twice) and the timeout cases fail because TimeoutExpired
propagates unnamed. Two additions pass at the predecessor and are labeled as
such in their detail strings (precision/regression additions, never claimed
RED): the ARV-PRF-002 exact-code tightening (the implementation already
prints the exact code; the broad 'ARV-PRF' would also have matched
ARV-PRF-001/004 — the card requires the exact code) and the legal-hostile
refusal (the defense already covers permitted metadata; the case proves it
stays true). The original 026fead RED forms are preserved in the red record.
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
    """A real git clone of this repo at the candidate tree (full history), mutated
    per case. The gate diffs against 'origin/main', so the clone MUST carry that
    ref: in CI the parent workspace is a detached merge checkout with no local
    branches (a plain clone inherits none) — derive the base from the merge
    commit's second parent there, from the local 'main' branch elsewhere."""
    d = pathlib.Path(tmp) / name
    subprocess.run(["git", "clone", "-q", "--no-local", str(REPO), str(d)],
                   check=True, capture_output=True, timeout=300)
    base = ""
    # candidate bases, first that resolves wins: HEAD^2 = the PR merge commit's
    # main parent (CI); origin/main (a dev clone's remote-tracking ref — plain
    # rev-parse never DWIMs to it, so try it explicitly); a local main branch.
    for candidate in ("HEAD^2", "origin/main", "main"):
        r = subprocess.run(["git", "rev-parse", candidate], cwd=d,
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            base = r.stdout.strip()
            break
    if not base:
        raise AssertionError("fixture cannot derive the origin/main base for the clone")
    # the gate diffs against the literal ref 'origin/main' — set it explicitly
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", base], cwd=d,
                   check=True, capture_output=True, timeout=60)
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
        # TWO classes, honestly labeled (H-01a-R): the ORIGINAL fixture below is
        # NOT `git check-ref-format`-legal (it contains spaces — asserted right
        # here, so the case is labeled parser-boundary FUZZING, never claimed an
        # observed Git-ref path). The LEGAL hostile class follows it.
        hostile = 'slice/x"; echo ARV_PWNED_MARKER; "y'
        fmt = subprocess.run(["git", "check-ref-format", "--branch", hostile],
                             capture_output=True, text=True, timeout=60)
        check("A02-fuzz-fixture is honestly NOT a legal ref",
              fmt.returncode != 0,
              f"check-ref-format exit={fmt.returncode} — the space-carrying fixture is parser-boundary fuzzing (labeled, never an observed Git-ref path)")
        d = fixture_clone(tmp, "hostile")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request", "ARV_PR_HEAD": hostile})
        out = r.stdout + r.stderr
        pr_refusal(r, "ARV-DISPATCH-001", "A02-hostile-branch")
        # the refusal echoes the untrusted input ONCE (as data, inside the
        # 'rejected as data' line); if the payload had EXECUTED, its output
        # would appear on lines that are not that refusal echo.
        non_refusal = "\n".join(l for l in out.splitlines() if "rejected as data" not in l)
        check("A02-hostile-branch executes nothing", "ARV_PWNED_MARKER" not in non_refusal,
              "the breakout payload must never run as script")
        check("A02-hostile-branch creates no side-effect file",
              not (d / "ARV_PWNED_MARKER").exists(), "a `touch` payload must not land")

        # ---- A02 (H-01a-R): the LEGAL hostile class — genuinely creatable ----
        # No spaces (so ${IFS} expands at RUN time, not in the name); every
        # character is check-ref-format-legal (asserted below), so a hostile
        # actor could REALLY push this branch name. The defense must refuse it
        # as data and never execute the breakout.
        legal = 'slice/x"$(touch${IFS}ARV_PWNED_LEGAL)"y'
        fmt = subprocess.run(["git", "check-ref-format", "--branch", legal],
                             capture_output=True, text=True, timeout=60)
        check("A02-legal-hostile IS a genuinely legal ref",
              fmt.returncode == 0,
              f"check-ref-format exit={fmt.returncode} — the case exercises permitted metadata, not fuzzing (passes at the predecessor; regression protection, never claimed RED)")
        d = fixture_clone(tmp, "legalhostile")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request", "ARV_PR_HEAD": legal})
        pr_refusal(r, "ARV-DISPATCH-001", "A02-legal-hostile-branch")
        out = r.stdout + r.stderr
        non_refusal = "\n".join(l for l in out.splitlines() if "rejected as data" not in l)
        check("A02-legal-hostile executes nothing", "ARV_PWNED_LEGAL" not in non_refusal,
              "the no-space breakout payload must never run as script")
        check("A02-legal-hostile creates no side-effect file",
              not (d / "ARV_PWNED_LEGAL").exists(), "a `touch` payload must not land")

        # ---- A01: PR mode without a scope declaration -> real gate refusal ----
        d = fixture_clone(tmp, "noscope")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                             "ARV_PR_HEAD": "slice/claim-999-no-such-slice"})
        pr_refusal(r, "ARV-SCOPE-001", "A01-missing-scope")

        # ---- A01: scope declared but the branch carries NO open claim row ----
        d = fixture_clone(tmp, "noclaim")
        sd = d / "harness" / "runs" / "claim-999-unclaimed"
        sd.mkdir(parents=True)
        # fixture scopes deliberately avoid CLAIM-005's own declared scope —
        # the registry's real exclusivity check would otherwise (correctly)
        # refuse the probe as an overlap with the live claim
        (sd / "scope.txt").write_text("harness/tests/test_migrations.py INT-125/D-039\n")
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                             "ARV_PR_HEAD": "slice/claim-999-unclaimed"})
        pr_refusal(r, "ARV-CLM-005", "A01-unclaimed-branch")

        # ---- A01: claimed + scoped but NO proof sheet -> the gate refuses it ----
        # TWO refusal conditions, both asserted exactly (H-01a-R's tightening —
        # the original broad 'ARV-PRF' masked WHICH code fired, and the
        # tightening itself exposed that the card's assumed code was wrong for
        # the no-records path): a slice with NO run records and NO sheet fires
        # ARV-PRF-001 (proofsheet.assemble runs before the disk check), and the
        # SystemExit must not crash the gate (a clean named disposition — fixed
        # with this slice, RED: the predecessor crashed with a traceback); a
        # slice WITH records but no sheet fires ARV-PRF-002 (the card's named
        # condition, reachable only there). The assemble-before-disk-check
        # ordering is recorded as a static finding for H-02's boundary.
        d = fixture_clone(tmp, "nosheet")
        sd = d / "harness" / "runs" / "claim-999-nosheet"
        sd.mkdir(parents=True)
        (sd / "scope.txt").write_text("harness/tests/test_migrations.py INT-125/D-039\n")
        reg = d / "CLAIMS.md"
        row = ("| CLAIM-999 | 20 | test | `slice/claim-999-nosheet` | "
               "`harness/tests/test_migrations.py` | — | 2026-10-19 | probe |\n")
        text = reg.read_text()
        anchor = "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        reg.write_text(text.replace(anchor, anchor + row, 1))
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                              "ARV_PR_HEAD": "slice/claim-999-nosheet"})
        pr_refusal(r, "ARV-PRF-001", "A01-missing-records-and-sheet")
        out = r.stdout + r.stderr
        check("A01-missing-records has NO uncaught traceback", "Traceback" not in out,
              "a missing Proof Sheet is a named gate disposition (ARV-PRF-001), never a SystemExit crash — the exact class residual #1 names, same repair slice")
        check("A01-missing-records gets the gate's consolidated disposition",
              "RED — the gate refuses" in out and "ARV-PRF-004" in out,
              "the gate must CATCH the proofsheet refusal and print its own consolidated summary — a mid-run SystemExit that skips the summary is the same clean-disposition class (RED at the predecessor: the summary never printed)")
        # the reachable form of the card's named code: records exist, sheet missing
        d = fixture_clone(tmp, "nosheet2")
        sd = d / "harness" / "runs" / "claim-999-nosheet2"
        sd.mkdir(parents=True)
        (sd / "scope.txt").write_text("harness/tests/test_migrations.py INT-125/D-039\n")
        (sd / "run-01.json").write_text(
            '{"command": "probe", "exit_code": 0, "commit": "' + "0" * 40 + '", '
            '"output_sha256": "' + "0" * 64 + '", "recorded_at": "2026-10-19T00:00:00+00:00"}\n')
        reg = d / "CLAIMS.md"
        text = reg.read_text()
        row = ("| CLAIM-999 | 20 | test | `slice/claim-999-nosheet2` | "
               "`harness/tests/test_migrations.py` | — | 2026-10-19 | probe |\n")
        reg.write_text(text.replace(anchor, anchor + row, 1))
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                              "ARV_PR_HEAD": "slice/claim-999-nosheet2"})
        pr_refusal(r, "ARV-PRF-002", "A01-missing-sheet-only")

        # ---- positive: a VALID scoped/claimed/sheeted PR dispatches green ----
        # ENVIRONMENT-INDEPENDENT by design (three walls-catches at PR #41 drove
        # this to its final form): (1) the case once exercised the LIVE claim-005
        # row and broke when that claim legitimately closed (ARV-CLM-005 — the
        # gate was right); (2) stripping the live rows then broke the KB-CLM-002
        # probe, which needs a pre-existing row to overlap against (the A11
        # probe-coupling defect, exactly as the audit states it). Final design:
        # registry INTACT (probes keep their partners), the base ref reset to
        # HEAD (the fixture's diff is empty — the case proves dispatch routing,
        # not diff evaluation, which the negative cases cover), and a synthetic
        # non-overlapping row that ALSO carries a guaranteed probe partner.
        d = fixture_clone(tmp, "positive")
        subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=d,
                       check=True, capture_output=True, timeout=60)
        sname = "claim-998-positive-shape"
        sd = d / "harness" / "runs" / sname
        sd.mkdir(parents=True)
        (sd / "scope.txt").write_text(
            "README.md INT-125/D-039\n"
            "context/extracted/21-fixture-probe.md INT-125/D-039\n")
        reg = d / "CLAIMS.md"
        text = reg.read_text()
        anchor = "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        row = ("| CLAIM-998 | 20 | test | `slice/" + sname + "` | "
               "`README.md`, `context/extracted/21-fixture-probe.md` | "
               "— | 2026-10-19 | positive probe — non-overlapping, and the 21- entry is the KB-CLM-002 probe's guaranteed overlap partner (A11's coupling, made deterministic) |\n")
        reg.write_text(text.replace(anchor, anchor + row, 1))
        nv_text = "- fixture probe record (self-contained; no real evidence touched)\n"
        (sd / "run-01.json").write_text(
            '{"command": "probe", "exit_code": 0, "commit": "' + "0" * 40 + '", '
            '"output_sha256": "' + "0" * 64 + '", "recorded_at": "2026-10-19T00:00:00+00:00"}\n')
        (sd / "notverified.txt").write_text(nv_text)
        # assemble the sheet from the record using the FIXTURE's own module
        sys.path.insert(0, str(d))
        try:
            import importlib
            ps = importlib.import_module("harness.proofsheet")
            ps.REPO = d
            ps.RUNS = d / "harness" / "runs"
            (sd / "proofsheet.md").write_text(ps.assemble(sname, nv_text))
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

        # ---- H-01a-R residual #1: the CONSOLIDATED gate refusal through the ----
        # ---- ACTUAL caller (dispatch.py) — no uncaught traceback, no claim  ----
        # ---- check that assumes a valid diff.                               ----
        # RED at the predecessor: an uncaught GitRefusal traceback at gate.py:191
        # (the claim-coverage diff_paths recompute outside the handler), the
        # refusal printed twice — exit 1 by process failure, not a named gate
        # disposition. The fixture carries a CLAIMED branch + scope + runs dir so
        # the gate would reach the claim-coverage path if the diff were valid.
        d = fixture_clone(tmp, "badbase")
        sname = "claim-999-badbase"
        sd = d / "harness" / "runs" / sname
        sd.mkdir(parents=True)
        (sd / "scope.txt").write_text("README.md INT-126/D-040\n")
        reg = d / "CLAIMS.md"
        text = reg.read_text()
        anchor = "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        row = ("| CLAIM-999 | 21 | test | `slice/" + sname + "` | `README.md` | "
               "— | 2026-10-19 | probe |\n")
        reg.write_text(text.replace(anchor, anchor + row, 1))
        subprocess.run(["git", "update-ref", "-d", "refs/remotes/origin/main"], cwd=d,
                       check=True, capture_output=True, timeout=60)
        r = run_dispatch(d, {"ARV_EVENT_NAME": "pull_request",
                             "ARV_PR_HEAD": "slice/" + sname})
        out = r.stdout + r.stderr
        check("H01aR-bad-base exits nonzero", r.returncode != 0, f"exit={r.returncode}")
        check("H01aR-bad-base prints ONE ARV-DIFF-001 disposition",
              len([l for l in out.splitlines() if l.startswith("FAIL ARV-DIFF-001")]) == 1,
              "the named refusal prints as a disposition exactly once; the summary lists the code (that IS the consolidated disposition) — but a second FAIL disposition or a crash-repeated code is the defect (amendment: the first draft of this assertion counted raw substring mentions, which the skip note and the required summary legitimately contain; narrowed to the disposition form, no assertion removed)")
        check("H01aR-bad-base has NO uncaught traceback", "Traceback" not in out,
              "a failed diff is a named gate disposition, never a process crash")
        check("H01aR-bad-base skips the claim check on an invalid diff",
              "ARV-CLM-000" in out and "invalid diff" in out,
              "the branch-claim coverage check must not run on a refused diff; the skip note is the observable")
        check("H01aR-bad-base never falls back to selfcheck", "main-selfcheck" not in out,
              "the A01 boundary: a PR is judged as a PR even when its diff refuses")

        # ---- H-01a-R residual #1b: a hung git subprocess is a NAMED refusal ----
        # (ARV-DIFF-003), never an unnamed TimeoutExpired crash. A real hang is
        # never safe to require, so the timeout is simulated deterministically:
        # subprocess.run raises TimeoutExpired exactly as a 60s hang would, and
        # scope.py's contract is to convert it into GitRefusal(ARV-DIFF-003).
        # RED at the predecessor: TimeoutExpired propagates unnamed.
        real_run = subprocess.run
        def _hang(*a, **k):
            raise subprocess.TimeoutExpired(cmd=(a[0] if a else k.get("args", [])),
                                            timeout=k.get("timeout", 60))
        subprocess.run = _hang
        try:
            refused = False
            code = ""
            try:
                scope._git(["diff", "--name-only", "x...HEAD"])
            except Exception as exc:
                refused = isinstance(exc, scope.GitRefusal)
                code = str(exc)
            check("H01aR-timeout in _git refuses with ARV-DIFF-003",
                  refused and "ARV-DIFF-003" in code,
                  f"refused={refused} code={code[:160]!r} — a hung git op is a named refusal, never an unnamed crash")
            refused = False
            code = ""
            try:
                scope.ensure_merge_base("origin/main")
            except Exception as exc:
                refused = isinstance(exc, scope.GitRefusal)
                code = str(exc)
            check("H01aR-timeout in ensure_merge_base refuses with ARV-DIFF-003",
                  refused and "ARV-DIFF-003" in code,
                  f"refused={refused} code={code[:160]!r}")
        finally:
            subprocess.run = real_run
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
