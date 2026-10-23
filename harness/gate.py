#!/usr/bin/env python3
"""harness/gate.py — the gate (S4; D-036; the Phase 2 exit assembly).

All mechanical checks; exit 0 or 1; every failure a named code (diagnostics
contract). Check order:

  1. ARV-GATE-001/002  the declared test suites EXIST (fail-closed on a missing
                       file) and PASS on the real stack
  2. ARV-RED-001/002   red records: every test file has one (LAW-11) and its
                       current hash matches the record (amendments re-record)
  3. ARV-SCOPE/PROT/SIZE  the diff is inside the declared scope, protected paths
                       carry owner refs, the size limits hold (LAW-05/06/07);
                       a failed/hung git diff is ONE consolidated named refusal
                       (ARV-DIFF-001/002/003 via scope.GitRefusal — the diff is
                       computed ONCE and shared by every consumer; a refused
                       diff skips the claim-coverage check with a named note,
                       never a mid-run crash — H-01a-R);
                       a failed/hung git diff is ONE consolidated named refusal
                       (ARV-DIFF-001/002/003 via scope.GitRefusal — the diff is
                       computed ONCE and shared by every consumer; a refused
                       diff skips the claim-coverage check with a named note,
                       never a mid-run crash — H-01a-R)
  4. ARV-LAW24-001     ambient time/IDs/randomness only inside adapters/
  5. ARV-DEP-008       no unapproved dependencies (LAW-08)
  6. KB-01..06         every known-bad case is REJECTED with its named code
                       (a passing known-bad is a broken guard — KB-05)
  7. ARV-PRF-004       the slice's Proof Sheet re-derives byte-identically (LAW-01)

Diff modes: --diff <base> (git diff base..HEAD vs the slice's declaration) or
--no-diff (main/selfcheck: the diff-scoped checks ran at PR time on the same
changes through the protected workflow). Run records for 'make prove' are
written by --record.
"""
import argparse
import hashlib
import io
import json
import contextlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import proofsheet, scope, claims  # noqa: E402

# known-bad cases load BY FILE PATH (the doc-conventional directory carries a
# hyphen — not a Python package name; spec-loading keeps it importable anyway)
import importlib.util  # noqa: E402

_kb_spec = importlib.util.spec_from_file_location(
    "known_bad_cases", pathlib.Path(__file__).parent / "known-bad" / "cases.py")
kbcases = importlib.util.module_from_spec(_kb_spec)
_kb_spec.loader.exec_module(kbcases)

def _repo_root() -> pathlib.Path:
    """H-01b-CI (session 23): the trusted gate driver (tools/trusted_gate.py)
    re-roots this machinery onto the CANDIDATE tree by setting ARV_TRUSTED_ROOT
    before import, so the BASE's gate judges the candidate's data (suites run
    with cwd=candidate; registry/records/declarations/git-diff all read from
    the candidate). The override is honored ONLY when it names an absolute
    existing directory; anything else keeps the natural root — the modules
    never refuse at import time (the driver validates strictly first). The
    known-bad cases stay __file__-relative: they always come from the BASE."""
    root = os.environ.get("ARV_TRUSTED_ROOT", "")
    p = pathlib.Path(root) if root else None
    if p is not None and p.is_absolute() and p.is_dir():
        return p
    return pathlib.Path(__file__).resolve().parents[1]


REPO = _repo_root()
# The ONE TESTS home (CLAIM-037, F-007): red.py imports this tuple — the
# predecessor DUPLICATED it (red.py's own docstring named the one-fact-two-
# homes defect; the unification is this card's named work). Every file under
# harness/tests/test_*.py MUST appear here (ARV-RED-008 refuses the gap).
TESTS = ("harness/tests/test_migrations.py", "harness/tests/test_substrate.py",
         "harness/tests/test_commands.py", "harness/tests/test_gate_dispatch.py",
         "harness/tests/test_mutation_floor.py",
         "harness/tests/test_trusted_gate.py",
         "harness/tests/test_claims_paths.py",
         "harness/tests/test_record_machinery.py")


def run_cmd(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)


def check_declared_files() -> list:
    """ARV-GATE-001: a deleted/renamed declared test is a skipped test — RED."""
    fails = []
    for t in TESTS:
        if not (REPO / t).is_file():
            print(f"FAIL ARV-GATE-001: declared test {t} is MISSING — a deleted or renamed test is a skipped test (fail-closed)")
            print("      repair: restore the test, or update the declared suite deliberately through a gate change (LAW-09 class)")
            fails.append("ARV-GATE-001")
    return fails


def check_suites() -> list:
    fails = check_declared_files()
    for t in TESTS:
        if not (REPO / t).is_file():
            continue
        r = run_cmd([sys.executable, t])
        if r.returncode != 0:
            print(f"FAIL ARV-GATE-002: {t} exited {r.returncode} — the suite is red")
            print("      repair: run the suite directly for its named failure and repair per its message")
            fails.append("ARV-GATE-002")
        else:
            print(f"PASS {t}: exit 0 on the real stack")
    return fails


def _red_baseline():
    """F-007 (CLAIM-037): the TRUSTED PRIOR STATE of the red records — the state
    a candidate tree cannot rewrite. Resolution order: (1) ARV_TRUSTED_BASE (set
    by the trusted driver from the BASE checkout — the CI authority, and by the
    KB probe for the self-authorization case); (2) origin/main's copy via git
    (the local PR-mode fallback); (3) unresolvable -> None + a printed NOTE
    (stated residual for that run, never a hidden skip).
    Returns (records dict | None, source label | None)."""
    base = os.environ.get("ARV_TRUSTED_BASE", "")
    if base:
        p = pathlib.Path(base) / "harness" / "red-records.json"
        if p.is_file():
            try:
                return json.loads(p.read_text()), "ARV_TRUSTED_BASE"
            except json.JSONDecodeError as e:
                print(f"FAIL ARV-RED-006: ARV_TRUSTED_BASE names an unparseable red-records.json ({e}) — a corrupt trusted baseline is a refusal")
                return "REFUSED", "ARV_TRUSTED_BASE"
        print("NOTE ARV-RED-000: ARV_TRUSTED_BASE names no red-records.json — no trusted baseline for this run (the self-authorization check is inactive; stated, never hidden)")
        return None, None
    r = subprocess.run(["git", "-C", str(REPO), "show", "origin/main:harness/red-records.json"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and r.stdout.strip():
        try:
            return json.loads(r.stdout), "origin/main"
        except json.JSONDecodeError:
            print("NOTE ARV-RED-000: origin/main's red-records.json is unparseable — no trusted baseline for this run")
            return None, None
    print("NOTE ARV-RED-000: no trusted baseline resolvable (no ARV_TRUSTED_BASE, no origin/main in this git context) — the self-authorization check is inactive for this run; the CI trusted job always resolves one (stated residual, never a hidden skip)")
    return None, None


def _git_show_hash(commit: str, rel: str):
    """The sha256 of <rel> as committed at <commit>, or None when the tree is
    not a git context (the KB work copies — .git ignored — and any git failure:
    a NOTE, never a false verification)."""
    try:
        r = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{rel}"],
                           capture_output=True, timeout=60)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return hashlib.sha256(r.stdout).hexdigest()


def check_red_records() -> list:
    fails: list[str] = []
    rr_path = REPO / "harness" / "red-records.json"
    if not rr_path.is_file():
        print("FAIL ARV-RED-003: harness/red-records.json is missing — the red-first discipline has no mechanical memory (LAW-11)")
        print("      repair: 'make red' at the test-only commit, or backfill with the red commit's evidence")
        return ["ARV-RED-003"]
    data = json.loads(rr_path.read_text())

    # ARV-RED-008 (fail-closed suite registration, CLAIM-037): every test file
    # under harness/tests/ must be registered. The #72 round (Greptile P1):
    # registration counts in EITHER tuple — the gate's OWN TESTS (base-owned at
    # trusted time) OR the CANDIDATE'S gate.py TESTS, parsed as DATA (a
    # diff-visible, reviewable addition; candidate code is never imported to
    # learn it). A suite registered in the candidate's own tuple is NOT part of
    # the trusted REQUIRED selection until main adopts the tuple (the next
    # slice's trusted run executes it) — the check's subject is the file
    # invisible to BOTH discovery surfaces, never a legitimately-registered
    # addition (never described as a bypass — CodeRabbit's wording catch).
    cand_tests = set(TESTS)
    gp = REPO / "harness" / "gate.py"
    if gp.is_file() and str(gp.resolve()) != str(pathlib.Path(__file__).resolve()):
        # the third pass (CodeRabbit Major, CWE-693): the AST parse accepts
        # only ACTUAL tuple entries — a quoted path in a COMMENT never
        # registers (the regex form extracted comment strings too; a
        # candidate could 'register' a suite the trusted selection never
        # runs). ast.literal_eval executes nothing — a non-literal TESTS
        # counts no additions (fail-closed, with a NOTE)
        try:
            import ast as _ast
            _tree = _ast.parse(gp.read_text(encoding="utf-8"))
            for _node in _ast.walk(_tree):
                if isinstance(_node, _ast.Assign) and any(
                        isinstance(_t, _ast.Name) and _t.id == "TESTS" for _t in _node.targets):
                    cand_tests |= {str(_x) for _x in _ast.literal_eval(_node.value)}
        except (SyntaxError, ValueError, TypeError):
            print("NOTE ARV-RED-000: the candidate gate.py TESTS tuple is unparseable as a literal — no candidate additions counted (fail-closed)")
    for p in sorted((REPO / "harness" / "tests").glob("test_*.py")):
        rel = str(p.relative_to(REPO))
        if rel not in cand_tests:
            print(f"FAIL ARV-RED-008: {rel} exists under harness/tests/ but is registered NOWHERE — invisible to BOTH discovery surfaces (the trusted required-suite selection and the red control)")
            print("      repair: register it in the gate.py TESTS tuple (a diff-visible, reviewable change) + mint its red record ('make red --exit N --code CODE'), or remove the file")
            fails.append("ARV-RED-008")

    baseline, baseline_src = _red_baseline()
    if baseline == "REFUSED":
        return fails + ["ARV-RED-006"]
    if baseline is not None:
        print(f"NOTE ARV-RED-000: the trusted baseline resolved from {baseline_src} — a changed test is authorized only by a typed amendment chaining from it")

    # the #72 round: the per-record validation covers the UNION — the gate's
    # own TESTS plus the candidate-registered additions (a registered suite's
    # record gets the FULL typed/binding/chain validation; registering without
    # a record is ARV-RED-001, and the unrecovered/typed-red rules reach it)
    for t in sorted(cand_tests):
        if t not in data:
            print(f"FAIL ARV-RED-001: no red record for {t} — every test file must carry its red evidence (LAW-11: committed alone, observed failing)")
            print("      repair: 'make red --exit N --code CODE' at the test-only commit, or backfill the record with the red commit's evidence")
            fails.append("ARV-RED-001")
            continue
        rec = data[t]
        cur = hashlib.sha256((REPO / t).read_bytes()).hexdigest()
        if cur != rec.get("current_sha256"):
            print(f"FAIL ARV-RED-002: {t} changed since its record (hash mismatch, no amendment) — tests edited after red (LAW-11)")
            print("      repair: re-record with 'make red' and an amendment note (amendments add assertions, never remove)")
            fails.append("ARV-RED-002")

        # ARV-RED-007 (typed records, CLAIM-037/F-007): a written assertion is
        # not an observed failure. A record must be schema 2 with EITHER the
        # typed observed-red (red_exit nonzero int + red_code nonempty) OR the
        # honest red_unrecovered marker (the smash class — never a fabricated
        # observation), AND a git-verifiable binding.
        untyped = []
        if rec.get("schema") != 2:
            untyped.append("no schema-2 marker")
        # the #72 round (CodeRabbit Minor): red_unrecovered exists for honestly
        # lost history — records the trusted baseline KNOWS (the smash-class
        # migrations) — never as the typed-red bypass for a suite no baseline
        # has ever seen (a new mint must carry the observed red)
        unrecovered_ok = bool(rec.get("red_unrecovered")) and (
            baseline is None or t in baseline)
        if not unrecovered_ok:
            re_, rc_ = rec.get("red_exit"), rec.get("red_code")
            if not isinstance(re_, int) or re_ == 0:
                untyped.append("red_exit is not a nonzero int")
            if not isinstance(rc_, str) or not rc_.strip():
                untyped.append("red_code is not a nonempty string")
        bc, bs = rec.get("binding_commit"), rec.get("binding_sha256")
        if not bc or not bs:
            untyped.append("no binding_commit/binding_sha256 pair")
        if untyped:
            print(f"FAIL ARV-RED-007: {t}'s red record is untyped ({'; '.join(untyped)}) — a written assertion is not an observed failure; the record needs the typed observed-red (or the honest unrecovered marker, only for records the trusted baseline knows) and the git-verifiable binding (F-007)")
            print("      repair: re-type via 'make red' with the observed --exit/--code; red_unrecovered is for honestly-lost history (baseline-present records), never a new mint's bypass")
            fails.append("ARV-RED-007")
        elif REPO.joinpath(".git").exists() or REPO.joinpath(".git").is_file():
            shown = _git_show_hash(bc, t)
            if shown is None:
                # the #72 round (Greptile P1): in a git context, git's inability
                # to show the commit IS the false claim — a nonexistent revision
                # name is a fabricated binding, never an unverifiable note
                print(f"FAIL ARV-RED-007: {t}'s binding is FALSE — git cannot show {t} at {bc[:10]} (the commit names no history this tree carries; a revision claim must name history that exists)")
                print("      repair: bind the record to a commit that actually exists and carries the recorded content")
                fails.append("ARV-RED-007")
            elif shown != bs:
                print(f"FAIL ARV-RED-007: {t}'s binding is FALSE — the digest recorded for binding commit {bc[:10]} does not match the file as git carries it (a fabricated revision claim)")
                print("      repair: bind the record to the commit that actually carries the recorded content; a revision claim must name history that exists")
                fails.append("ARV-RED-007")
        else:
            print(f"NOTE ARV-RED-000: {t}'s binding is unverifiable in a non-git copy (the KB probe context) — the binding verification runs in every git context (local, CI, the trusted job)")

        # ARV-RED-006 (F-007's named defect, CLAIM-037): the self-authorization
        # refusal. A test file whose digest differs from the TRUSTED PRIOR state
        # is authorized ONLY by a typed amendment chain bridging exactly that
        # transition: some typed amendment starts at the baseline's digest and
        # consecutive typed amendments connect to the current form. The bare
        # make-red refresh (the candidate's own current_sha256) is the hole.
        if baseline is not None:
            b_digest = (baseline.get(t) or {}).get("current_sha256")
            if b_digest is not None and b_digest != cur:
                reachable = {b_digest}
                for am in rec.get("amendments", []):
                    if isinstance(am, dict) and "prior_sha256" in am and "new_sha256" in am:
                        if am["prior_sha256"] in reachable:
                            reachable.add(am["new_sha256"])
                if cur not in reachable:
                    print(f"FAIL ARV-RED-006: {t} changed against the trusted prior state and its record's typed amendments do NOT bridge that state to the current form — the make-red refresh alone is the self-authorization this check refuses (F-007)")
                    print("      repair: the change must be reviewed as what it is — an amendment chaining exactly from the trusted prior digest (prior == the baseline's, new == the actual); the diff is the review layer's authority")
                    fails.append("ARV-RED-006")
    return fails


def run_known_bads() -> list:
    """KB-05: a known-bad that passes is a broken guard — red, stop building.

    H-01b-CI (session 23): the probes are COPY-RELATIVE — each loads machinery
    modules and mutates its own WORK COPY of the tree. In the TRUSTED re-root
    run the module BYTES come from the BASE (ARV_TRUSTED_KB_MACHINERY — the
    candidate's harness package, including its known-bad registry, never
    executes in the trusted judge: a candidate cases.py running SystemExit(0)
    at import made three probes vacuous before this routing, reproduced live
    by test_trusted_gate.test_06), while ARV_TRUSTED_ROOT is re-pointed at
    EACH case's work copy so the freshly-loaded BASE machinery resolves its
    REPO onto the mutated tree. In the LOCAL self-check (no re-root active)
    the legacy form holds: modules from the copy, REPO module-relative."""
    saved_root = os.environ.pop("ARV_TRUSTED_ROOT", None)
    trusted = saved_root is not None
    try:
        if trusted:
            # module BYTES from the BASE (this file's own repo root — gate.py
            # IS the base's copy in the trusted run; _load joins "harness/<mod>"
            # onto this root); DATA stays copy-relative
            os.environ["ARV_TRUSTED_KB_MACHINERY"] = str(pathlib.Path(__file__).resolve().parents[1])
        scratch = pathlib.Path(tempfile.mkdtemp(prefix="arv_kb_"))
        fails = []
        try:
            copy = scratch / "repo"
            shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "harness/runs"))
            probe = copy / "harness" / "runs" / kbcases.SLICE
            probe.mkdir(parents=True, exist_ok=True)
            # the probe declaration: declared-but-UNREFERENCED protected prefixes (the refusals' target)
            (probe / "scope.txt").write_text("harness/tests\nharness/runs\n.github\nharness/scope.py\n")
            (probe / "run-01.json").write_text(json.dumps(
                {"command": "probe", "exit_code": 0, "output_sha256": "0" * 64,
                 "recorded_at": "2026-10-16T00:00:00+00:00"}) + "\n")
            if trusted:
                os.environ["ARV_TRUSTED_ROOT"] = str(copy)
            ps = kbcases._load(copy, "harness.proofsheet")
            ps.RUNS = probe.parent
            (probe / "proofsheet.md").write_text(ps.assemble(kbcases.SLICE, "- probe only"))
            for cid, desc, code, probe_fn in kbcases.CASES:
                work = scratch / cid
                shutil.copytree(copy, work, ignore=shutil.ignore_patterns("__pycache__"))
                if trusted:
                    # each probe's freshly-loaded (BASE) machinery must resolve
                    # its REPO onto THIS case's work copy — the mutations land
                    # there, and module-bytes trust never changes REPO semantics
                    os.environ["ARV_TRUSTED_ROOT"] = str(work)
                buf = io.StringIO()
                try:
                    with contextlib.redirect_stdout(buf):
                        probe_fn(work)
                except SystemExit:
                    pass
                if code in buf.getvalue():
                    print(f"PASS {cid}: {desc} -> REFUSED with {code} (the guard fires)")
                else:
                    print(f"FAIL {cid}: {desc} -> the guard did NOT fire (expected {code}) — a broken guard (KB-05)")
                    print("      repair: fix the check so this known-bad is rejected; building stops until it is")
                    fails.append(cid)
        finally:
            if trusted:
                os.environ.pop("ARV_TRUSTED_KB_MACHINERY", None)
            shutil.rmtree(scratch, ignore_errors=True)
        return fails
    finally:
        if saved_root is not None:
            os.environ["ARV_TRUSTED_ROOT"] = saved_root


def main() -> int:
    ap = argparse.ArgumentParser(description="the gate (S4)")
    ap.add_argument("--slice", default=None, help="the slice whose declaration + Proof Sheet are checked")
    ap.add_argument("--diff", default=None, help="git base for the diff (PR mode), e.g. origin/main")
    ap.add_argument("--no-diff", action="store_true")
    ap.add_argument("--skip-suites", action="store_true", help="CI re-entry: the suites already ran in this job")
    ap.add_argument("--known-bad-only", action="store_true", help="run only the known-bad matrix")
    a = ap.parse_args()
    if a.known_bad_only:
        fails = run_known_bads()
        print()
        if fails:
            print(f"RED — {len(fails)} broken guard(s): {', '.join(fails)} (KB-05 — building stops)")
            return 1
        print("GREEN — every known-bad is rejected with its named code (KB-01..06)")
        return 0
    slice_name = a.slice or "main-selfcheck"
    fails: list[str] = []

    if not a.skip_suites:
        print("declared suites (fail-closed + real-stack):")
        fails += check_suites()
    print("red records (LAW-11):")
    fails += check_red_records()
    # scope/size (LAW-05/06/07) — H-01a-R: the diff is computed ONCE; both
    # consumers (scope/size + the branch-claim coverage below) share it. A
    # GitRefusal is ONE consolidated named disposition — never the
    # print-then-crash the predecessor produced when the claim-coverage path
    # recomputed the diff outside this handler (the reproduced residual #1).
    pr_diff = None
    stats = None
    if a.no_diff or not a.diff:
        print("NOTE ARV-SCOPE-000: no-diff mode (main/selfcheck) — the diff-scoped checks ran at PR time on these same changes")
    else:
        try:
            pr_diff = scope.diff_paths(a.diff)
            stats = scope.diff_stats(a.diff)
        except scope.GitRefusal as refusal:
            code = str(refusal).split(":")[0]
            print(f"FAIL {refusal}")
            print("      repair: verify the base ref exists and shares history with HEAD, and the checkout carries sufficient graph depth (fetch-depth 0 in CI) — a git failure is a refusal, never an empty diff (A10)")
            fails.append(code)
        if pr_diff is not None:
            fails += scope.check_scope(pr_diff, slice_name)
            fails += scope.check_size(stats)
    print("claims registry (LAW-31, D-038 — the collision's ratchet):")
    fails += claims.check_registry()
    if a.diff and not a.no_diff:
        # F-008 (H-01c-claims, session 23): the PR mode is the TRUSTED
        # invocation itself (--diff set by dispatch or the trusted driver) —
        # the contributor-selected slice LABEL never disables claim enforcement.
        # The predecessor exempted a slice NAMED main-selfcheck: a PR whose
        # branch claimed that label skipped its open-claim and coverage checks.
        if pr_diff is None:
            print("NOTE ARV-CLM-000: the diff was refused above (ARV-DIFF-001/002/003) — the branch-claim coverage check cannot run on an invalid diff; the refusal above is the consolidated disposition")
        else:
            branch = slice_name if slice_name.startswith("slice/") else "slice/" + slice_name
            fails += claims.check_branch_claim(branch, pr_diff)
    else:
        print("NOTE ARV-CLM-000: no-diff mode (main/selfcheck) — the branch-claim and diff-coverage checks ran at PR time")
    print("LAW-24 boundary lint:")
    fails += scope.lint_boundary()
    print("LAW-08 dependency check:")
    fails += scope.check_deps()
    print("known-bad matrix (KB-05):")
    fails += run_known_bads()
    if a.slice:
        print(f"Proof Sheet verify ({slice_name}):")
        ps = proofsheet
        argv = sys.argv[:]
        sys.argv = ["proofsheet.py", "--slice", slice_name, "--verify"]
        try:
            if ps.main() != 0:
                fails.append("ARV-PRF-004")
        except SystemExit:
            # H-01a-R: proofsheet refuses a no-records slice BY SystemExit — the
            # gate CATCHES it so the refusal becomes the gate's own consolidated
            # disposition (ARV-PRF-004 in the summary), never a mid-run exit that
            # skips the summary.
            fails.append("ARV-PRF-004")
        finally:
            sys.argv = argv
    else:
        print("NOTE ARV-PRF-000: selfcheck mode (no slice named) — per-slice Proof Sheets verify at slice time")

    print()
    if fails:
        print(f"RED — the gate refuses: {len(fails)} failure(s): {', '.join(sorted(set(fails)))}")
        print("Ref: OPERATING-MODEL §9, LAWS.md, record 18 §4.4 — a red gate blocks the merge (the check is bound)")
        return 1
    print(f"GREEN — the gate passes (slice={slice_name}; suites + red records + scope/size + lint + deps + known-bads + proofsheet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
