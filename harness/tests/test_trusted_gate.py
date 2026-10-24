#!/usr/bin/env python3
"""harness/tests/test_trusted_gate.py — H-01b-CI's RED-first suite (F-004/F-006/B2).

The trusted gate driver (NEW tools/trusted_gate.py — base-owned, copied into the
candidate tree as the sha256-verified anchored copy, launched with `python3 -I`):
NO required check's green result may depend solely on code the PR candidate
controls or edits (the H-01b-CI card; owner turn 22 §5.5, INT-127/D-041).

  F-004  the harness job's evidence no longer comes from candidate-editable
         Make recipes: the driver selects the required suites from the BASE's
         gate.TESTS (trusted state) and runs the candidate's own suite files
         directly — a gutted Makefile cannot fabricate "suites ran".
  F-006  the candidate's gate never executes its own known-bad registry inside
         the trusted run: the BASE's gate machinery, re-rooted over the
         candidate tree (ARV_TRUSTED_ROOT), re-runs the PR-mode obligations —
         the candidate gate's own green is never the only evidence.
  B2     the driver is launched with -I (no script-dir on sys.path) — the
         FLOOR-REVIEW-1 quantified that today's candidate tools/uuid.py-style
         shadow forges the anchored judge's result in-process.

Named codes frozen here BEFORE the implementation (the H-01a convention):
  ARV-TG-001  invalid/missing driver inputs (a non-absolute or nonexistent
              candidate root; untrusted event/branch metadata)
  ARV-TG-002  a required suite is MISSING from the candidate tree (fail-closed)
  ARV-TG-003  a required suite FAILED (nonzero exit)
  ARV-TG-004  a required suite produced NO output (the A03 vacuous class)
  ARV-TG-005  the BASE's gate machinery is missing/incomplete (anchor refused)

Each test builds a SYNTHETIC candidate git repo that satisfies the BASE gate's
obligations (registry, ledger, red records, declarations, proof sheet, machinery
data files) and flips exactly ONE condition. The driver is invoked exactly the
way CI invokes it: a subprocess, -I, the anchored-copy path, env-only metadata.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DRIVER = REPO / "tools" / "trusted_gate.py"
BRANCH = "slice/claim-xyz-synthetic"
SLICE = "claim-xyz-synthetic"
NOTVERIFIED = "- synthetic stub run — every obligation satisfied by construction\n"

# imported lazily (the real gate module import inserts the real repo root on
# sys.path — fine for the test process, which is NOT the trusted judge)
_REAL_GATE = None


def _base_gate():
    """Load the REAL harness/gate.py by file path (the required-suite source
    for the stub trees) — cached for the test process only, which is NOT the
    trusted judge."""
    global _REAL_GATE
    if _REAL_GATE is None:
        sys.path.insert(0, str(REPO))
        import importlib.util
        spec = importlib.util.spec_from_file_location("real_gate", REPO / "harness" / "gate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _REAL_GATE = mod
    return _REAL_GATE


def _stub_suite(name: str, *, fail: bool = False, silent: bool = False,
                stderr_only: bool = False) -> str:
    """A synthetic candidate suite file body: the normal shape, the failing
    shape, the zero-output A03 shape, or the unittest-shaped stderr-only
    reporter (R-04(1): its completion line prints to STDERR so the pin
    discriminates a stdout-only-blind driver)."""
    if silent:
        return "# silent stub\n"
    if stderr_only:
        # the unittest-shaped reporter: EVERYTHING on STDERR, nothing on
        # stdout — INCLUDING the completion line (R-04(1): the predecessor's
        # stub printed its 'Ran 3 tests' line to stdout, so a driver that
        # regressed to stdout-only checking still passed this shape — the
        # pin was twice-vacuous; the line moves to stderr so the pin
        # discriminates the exact blindness it exists to guard)
        return ("import sys\n"
                "print('unittest-shaped stub: reporting on stderr only', file=sys.stderr)\n"
                "print('Ran 3 tests in 0.1s', file=sys.stderr)\n")
    return ("# synthetic candidate suite (stubbed for the trusted-gate tests)\n"
            f"print('stub suite ok: {name}')\n" + ("raise SystemExit(1)\n" if fail else ""))


def build_stub(td: Path, *, suite_mutations: dict | None = None,
               delete_suite: str | None = None, breach: bool = False,
               gutted_makefile: bool = False, hostile_registry: bool = False,
               drop_base_gate: bool = False) -> Path:
    """A synthetic CANDIDATE git repo satisfying the BASE gate's obligations.
    suite_mutations: {suite_path: file_content} overrides; breach adds an
    UNDECLARED path to the PR commit (ARV-SCOPE-002's target)."""
    stub = td / "candidate"
    stub.mkdir()
    run = lambda *a: subprocess.run(a, cwd=stub, check=True, capture_output=True)
    run("git", "init", "-q", "-b", BRANCH)
    run("git", "config", "user.email", "stub@test.local")
    run("git", "config", "user.name", "Stub")

    # machinery data files (the candidate tree carries them; the trusted run
    # never imports them — the tests prove exactly that)
    for rel in ("harness/proofsheet.py", "harness/scope.py", "harness/claims.py",
                "harness/gate.py", "harness/migrate.py", "harness/__init__.py",
                "harness/adapters/__init__.py", "harness/adapters/clock.py"):
        dst = stub / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((REPO / rel).read_bytes())
    kb = stub / "harness" / "known-bad" / "cases.py"
    kb.parent.mkdir(parents=True, exist_ok=True)
    if hostile_registry:
        kb.write_text("# F-006 payload: if this module ever executes inside a trusted judge, the run exits green early\nimport sys\nsys.exit(0)\n")
    else:
        kb.write_bytes((REPO / "harness" / "known-bad" / "cases.py").read_bytes())

    # the required suites (the BASE's TESTS list, whatever it is at this revision).
    # The records are written AFTER the first commit (schema 2: the binding names
    # the stub's own git history — CLAIM-037), with typed amendments chaining
    # from the REAL base records' digests (the gate phase's baseline is this
    # same REPO via ARV_TRUSTED_BASE, so the chain verifies consistently).
    for t in _base_gate().TESTS:
        rel = t
        p = stub / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        content = _stub_suite(t)
        if suite_mutations and rel in suite_mutations:
            content = suite_mutations[rel]
        p.write_text(content, encoding="utf-8")
        if delete_suite and rel == delete_suite:
            p.unlink()
    # commit A: everything except the records and the PR change — the binding's
    # target (the suite files live here); the records follow in commit B so the
    # diff (HEAD~1..HEAD = commit C = notes.txt only) keeps the ORIGINAL shape
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "synthetic base state (the suites)")
    binding_commit = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"],
                                    cwd=stub, check=True, capture_output=True, text=True).stdout.strip()

    # the registry + ledger (valid open claim for BRANCH)
    (stub / "INTENT-LEDGER.md").write_text("**INT-100 — STUB — active**\n\nStatus legend: `active`.\n")
    (stub / "CLAIMS.md").write_text(
        "# CLAIMS (synthetic stub)\n\n## Open claims\n\n"
        "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
        "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        f"| CLAIM-XYZ | 23 | stub | `{BRANCH}` | `notes.txt`, `harness/tests`, `harness/red-records.json`, `CLAIMS.md`, `INTENT-LEDGER.md`, `harness/runs/{SLICE}` | — (synthetic) | 2026-10-20 | the trusted-gate test stub |\n\n"
        "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n")

    # the slice declaration + a real assembled proof sheet (base machinery)
    runs = stub / "harness" / "runs" / SLICE
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "scope.txt").write_text(
        f"# synthetic declaration\nnotes.txt\nharness/tests D-041\nharness/red-records.json D-041\nCLAIMS.md\nINTENT-LEDGER.md\nharness/runs/{SLICE}\n")
    # CLAIM-041: the record binds the stub's OWN root commit (the 40-zero ghost
    # binding is ARV-SEV-008's exact refusal class once the gate step lands) and
    # the stub carries a PLAN.md row + a born-valid SEV report so the positive
    # shape satisfies the wired gate's SEV obligation (the same shape it used
    # to ignore — the fixture modernizes WITH the machinery, never before it:
    # at the pre-wiring predecessor both additions are inert)
    (stub / "PLAN.md").write_text(
        "# PLAN (synthetic stub)\n\n| SYS | property | claims |\n|-----|----------|--------|\n"
        "| SYS-11 | Each implementation slice closes a V-model trace and has independent systems-engineering verification before merge. | C1-C5 |\n")
    sys.path.insert(0, str(REPO))
    from harness import proofsheet as ps
    from harness import sev as sev_mod
    ps.RUNS = runs.parent          # RUNS is the runs ROOT — assemble re-joins the slice name
    rec_path = runs / "run-01.json"
    rec_path.write_text(json.dumps({
        "command": "python3 synthetic-stub-suite", "exit_code": 0,
        "commit": binding_commit, "output_sha256": hashlib.sha256(b"stub output").hexdigest(),
        "recorded_at": "2026-10-20T00:00:00+00:00"}, indent=2) + "\n")
    (runs / "sev.json").write_text(json.dumps({
        "schema_version": 1, "slice_id": SLICE,
        "base_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=stub,
                                   check=True, capture_output=True, text=True).stdout.strip(),
        "reviewed_diff_sha256": sev_mod.reviewed_diff_sha256("HEAD", SLICE, repo=stub),
        "intent_ids": ["INT-100"], "requirement_ids": ["SYS-11"],
        "system_claims": ["C1"], "changed_components": ["notes.txt"],
        "interfaces_reviewed": ["the trusted gate phase over the stub's SEV report"],
        "v_model": {
            "component_verification": ["the stub's validator run, proof run-01"],
            "integration_verification": ["the trusted driver boundary, proof run-01"],
            "system_verification": ["SYS-11 trace, proof run-01"],
            "validation": ["the trusted gate phase green over the stub, proof run-01"],
        },
        "failure_modes": [
            {"id": "FM-01", "scenario": "a stub report drifting from its diff",
             "control": "the digest recomputation refuses (ARV-SEV-003)", "proof_ids": ["run-01"]},
        ],
        "findings": [],
        "not_verified": ["the stub boundary: a synthetic candidate, never real evidence; identity separation is declared, never cryptographic"],
        "builder_context": "stub-builder-ctx",
        "reviewer_context": "stub-reviewer-ctx",
        "disposition": "PASS",
        "review_summary": "the synthetic stub's born-valid report (the module's own digest function built it)",
    }, indent=2) + "\n")
    (runs / "proofsheet.md").write_text(ps.assemble(SLICE, NOTVERIFIED), encoding="utf-8")
    # --verify re-derives the not-verified section from this FILE — the stub
    # must carry it so the re-derivation is byte-identical (PRF-01)
    (runs / "notverified.txt").write_text(NOTVERIFIED, encoding="utf-8")

    # a Makefile whose recipes lie — the driver must never consult it
    mk = stub / "Makefile"
    mk.write_text("harness-tests:\n\t@echo 'FAKE SUCCESS — no suite ran'\nharness-health:\n\t@echo 'FAKE HEALTH'\n"
                   if gutted_makefile else
                   "harness-tests:\n\t@for t in harness/tests/test_*.py; do python3 $$t || exit 1; done\nharness-health:\n\t@echo ok\n")

    # the typed red records (schema 2) — written after the declarations so the
    # PR diff (HEAD~1..HEAD) keeps the ORIGINAL shape (the PR change only);
    # the binding names the suites' commit (the stub's own git history)
    base_records = json.loads((REPO / "harness" / "red-records.json").read_text())
    red_records = {}
    for t in _base_gate().TESTS:
        p = stub / t
        if delete_suite and t == delete_suite:
            continue
        cur = hashlib.sha256(p.read_bytes()).hexdigest()
        # the typed amendment: prior == the REAL record's current (the baseline
        # the gate phase checks against), new == the stub's synthetic form
        prior = (base_records.get(t) or {}).get("current_sha256")
        amendments = []
        if prior and prior != cur:
            amendments.append({"prior_sha256": prior, "new_sha256": cur,
                               "note": "the synthetic stub suite (the trusted-gate test fixture)",
                               "observed_at": "2026-10-23T00:00:00+00:00"})
        red_records[t] = {"schema": 2,
                          "binding_commit": binding_commit,
                          "binding_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                          "red_exit": 1,
                          "red_code": "ARV-STUB-RED (the synthetic stub's own named refusal form)",
                          "red_evidence": "synthetic stub",
                          "current_sha256": cur,
                          "amendments": amendments}
    (stub / "harness" / "red-records.json").write_text(json.dumps(red_records, indent=2) + "\n")
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "the registry + declarations + the typed red records")
    (stub / "notes.txt").write_text("the declared PR change\n")
    if breach:
        (stub / "undeclared-secret.txt").write_text("OUTSIDE the declared scope\n")
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "the PR change under test")
    # CLAIM-041: finalize the SEV report AFTER the PR commit — the binding
    # digest covers the diff the gate will judge (HEAD~1...HEAD = notes.txt),
    # never the earlier tree (the same staleness rule the validator enforces).
    sys.path.insert(0, str(REPO))
    from harness import sev as sev_mod2
    rep_path = stub / "harness" / "runs" / SLICE / "sev.json"
    rep = json.loads(rep_path.read_text())
    rep["base_sha"] = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=stub,
                                     check=True, capture_output=True, text=True).stdout.strip()
    rep["reviewed_diff_sha256"] = sev_mod2.reviewed_diff_sha256("HEAD~1", SLICE, repo=stub)
    rep_path.write_text(json.dumps(rep, indent=2) + "\n")
    codes = sev_mod2.validate_report(SLICE, "HEAD~1", repo=stub)
    if codes:
        raise AssertionError(f"stub sev.json not born-valid at the PR commit: {codes}")
    # the sheet embeds the SEV section — regenerate AFTER the report finalizes
    sys.path.insert(0, str(REPO))
    from harness import proofsheet as ps2
    ps2.RUNS = stub / "harness" / "runs"
    (stub / "harness" / "runs" / SLICE / "proofsheet.md").write_text(
        ps2.assemble(SLICE, NOTVERIFIED), encoding="utf-8")
    return stub


def run_driver(td: Path, stub: Path, phase: str, *, event: str | None = None,
               head: str | None = None, diff_ref: str = "HEAD~1",
               repo: str | None = None, base: str | None = None,
               env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Invoke the driver EXACTLY the way CI invokes it: a subprocess, -I, the
    anchored-copy path, a scrubbed env, and metadata only through the
    environment (the A02 pattern)."""
    if not DRIVER.is_file():
        raise AssertionError("the trusted driver (tools/trusted_gate.py) does not exist at the predecessor — H-01b-CI's named module is unbuilt")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(td)}
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, "-I", str(DRIVER),
           "--repo", repo or str(stub), "--base", base or str(REPO),
           "--phase", phase, "--diff-ref", diff_ref]
    if event is not None:
        cmd += ["--event", event]
    if head is not None:
        cmd += ["--head", head]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=env)


# --- the R-06 workflow-pin machinery (test_11/test_12; the 2026-10-23 backend
#     review's Findings A/B repaired: ONE common ordered step-block list for
#     indexes AND slicing; comment-aware ACTIVE-input credential assertions) ---

_WF_NAME_RE = re.compile(r'^[ ]{6}- name: (?P<name>"[^\n]+"|[^\n]+)')
_WF_PERSIST_RE = re.compile(r"^[ ]+persist-credentials:[ ]*false[ ]*(?:#.*)?$")


def _wf_job(wf_text: str, job_name: str):
    """The job's text span + its ordered STEP BLOCKS — ONE common ordered list
    for indexing AND slicing (Finding A's repair: the #66 form computed i_anchor/
    i_s4c from the NAMED-only list but sliced the EVERY-entry list — two index
    spaces, so an inserted unnamed step was invisible and the window assertion
    passed over it; the #66 second-pass commit claimed "every step entry" but
    the merged code kept the mixed space — red-01.txt).

    A step block starts at a `^ {6}- ` line (named or unnamed — the unnamed
    `- run:` class is Finding A's counterexample) and runs to the next step
    start or the job's end. Returns (job_text, blocks); blocks is a list of
    (start_offset_in_wf_text, [lines]). Raises AssertionError when the job is
    absent — fail-closed, never a vacuous pass over an empty job."""
    m = re.search(rf"^  {job_name}:\n(?P<job>(?:[ ]{{4,}}[^\n]*\n)*)", wf_text, re.M)
    if m is None:
        raise AssertionError(f"the {job_name} job must exist (R-06's split trusted path)")
    job, job_off = m.group("job"), m.start("job")
    blocks: list = []
    cur, cur_off = None, None
    pos = 0
    for ln in job.splitlines(keepends=True):
        if re.match(r"^[ ]{6}- ", ln):
            if cur is not None:
                blocks.append((cur_off, cur))
            cur, cur_off = [], job_off + pos
        if cur is not None:
            cur.append(ln)
        pos += len(ln)
    if cur is not None:
        blocks.append((cur_off, cur))
    return job, blocks


def _wf_step_name(block_lines):
    """The step's name when its first line is `- name: X`; None for an
    UNNAMED step (`- run:` / `- uses:` / ...) — the class the #66 form dropped
    from its index space."""
    m = _WF_NAME_RE.match(block_lines[0])
    return m.group("name").strip().strip('"') if m else None


def _wf_find(blocks, name_prefix):
    """The index of the first block whose NAME starts with the prefix (the
    anchor/S4c/S1b identification — on the SAME block list that gets sliced)."""
    for i, b in enumerate(blocks):
        n = _wf_step_name(b[1])
        if n is not None and n.startswith(name_prefix):
            return i
    return None


def _wf_active_persist_false(block_lines):
    """True iff the checkout block carries the ACTIVE CHECKOUT INPUT
    `persist-credentials: false` — a DIRECT CHILD of the step's `with:`
    mapping, the value exactly boolean false, a trailing comment allowed.
    COMMENT LINES never satisfy (Finding B's repair: the #66 form's raw
    substring assertIn matched a comment mentioning the phrase), and a
    WRONG-MAPPING line never satisfies either (the #67 Greptile round's P1:
    the line-anywhere form stayed green over `persist-credentials: false`
    planted under `env:` while the checkout input was absent — the mapping is
    tracked structurally, never the bare line)."""
    first = block_lines[0]
    step_i = len(first) - len(first.lstrip())     # the `- ` line's own indent
    key_i = step_i + 2                             # the step's keys (with:/env:/run:)
    child_i = step_i + 4                           # a mapping's direct children
    top = None                                     # the step key we are inside
    for ln in block_lines:
        stripped = ln.strip()
        if not stripped or stripped.startswith("#"):
            continue                               # comments/blanks never switch context
        ind = len(ln) - len(ln.lstrip())
        if ind == key_i:
            top = stripped.split(":", 1)[0].strip()   # a new step key ends the prior mapping
        elif ind == child_i and top == "with" and _WF_PERSIST_RE.match(ln):
            return True
    return False


def _wf_mut_unnamed_window_step(wf_text: str) -> str:
    """MUT-A (Finding A's counterexample): an UNNAMED `- run:` step inserted
    between harness-trusted's anchor and S4c. Structural surgery at the S4c
    block's start offset — never exact-line matching, so the fixture tracks the
    live artifact (when the shape changes, the parser refuses first and the
    fixture updates WITH the artifact, never silently drifts)."""
    _, blocks = _wf_job(wf_text, "harness-trusted")
    i_anchor = _wf_find(blocks, "Anchor the trusted gate")
    i_s4c = _wf_find(blocks, "S4c")
    if i_anchor is None or i_s4c is None or not i_s4c > i_anchor:
        raise AssertionError("the MUT-A fixture cannot be built — the harness-trusted "
                             "anchor/S4c shape changed (update the fixture with the artifact)")
    unnamed = ('      - run: |\n'
               '          echo "unnamed window step: an entry the name-only index space cannot see"\n')
    return wf_text[:blocks[i_s4c][0]] + unnamed + wf_text[blocks[i_s4c][0]:]


def _wf_mut_comment_only_credential(wf_text: str) -> str:
    """MUT-B (Finding B's counterexample): the ACTIVE persist-credentials input
    removed from harness-suites' FIRST checkout (Checkout head), an explanatory
    comment carrying the exact phrase left in its place — the raw-substring
    form's blind spot."""
    _, blocks = _wf_job(wf_text, "harness-suites")
    co = [b for b in blocks if "actions/checkout" in "".join(b[1])]
    if not co:
        raise AssertionError("the MUT-B fixture cannot be built — no checkout step in "
                              "harness-suites (update the fixture with the artifact)")
    off0, lines = co[0]
    for i, ln in enumerate(lines):
        if _WF_PERSIST_RE.match(ln):
            comment = ('          # the ACTIVE input was removed by this mutation but the comment still says\n'
                       "          # persist-credentials: false right here — the substring check's blind spot\n")
            old_block = "".join(lines)
            new_block = "".join(lines[:i]) + comment + "".join(lines[i + 1:])
            return wf_text[:off0] + new_block + wf_text[off0 + len(old_block):]
    raise AssertionError("the MUT-B fixture cannot be built — no ACTIVE persist-credentials "
                         "input in harness-suites' first checkout (update the fixture with the artifact)")


def _wf_mut_wrong_mapping_credential(wf_text: str) -> str:
    """MUT-C (the #67 Greptile round's P1 counterexample): the ACTIVE
    persist-credentials input MOVED OUT of harness-suites' FIRST checkout's
    `with:` mapping and re-planted as a step-level `env:` child — an ACTIVE
    line carrying the exact phrase remains, the checkout INPUT is gone. The
    line-anywhere form's blind spot (the check must track the `with:` mapping,
    never the bare line)."""
    _, blocks = _wf_job(wf_text, "harness-suites")
    co = [b for b in blocks if "actions/checkout" in "".join(b[1])]
    if not co:
        raise AssertionError("the MUT-C fixture cannot be built — no checkout step in "
                              "harness-suites (update the fixture with the artifact)")
    off0, lines = co[0]
    step_i = len(lines[0]) - len(lines[0].lstrip())
    key_i, child_i = step_i + 2, step_i + 4
    for i, ln in enumerate(lines):
        ind = len(ln) - len(ln.lstrip())
        if ind == child_i and _WF_PERSIST_RE.match(ln):
            # remove the with:-child; re-plant the phrase as an env: child at the
            # step's end — the phrase stays ACTIVE in the step, the input is gone
            old_block = "".join(lines)
            env_block = (" " * key_i) + "env:\n" + (" " * child_i) + "persist-credentials: false\n"
            new_block = "".join(lines[:i]) + "".join(lines[i + 1:]) + env_block
            return wf_text[:off0] + new_block + wf_text[off0 + len(old_block):]
    raise AssertionError("the MUT-C fixture cannot be built — no ACTIVE persist-credentials "
                         "child in harness-suites' first checkout's with: mapping (update "
                         "the fixture with the artifact)")


def _wf_check_r06_shape(wf_text: str) -> None:
    """The R-06 workflow pin — raises AssertionError on ANY violation. Every
    invariant of the #66 test_11 is preserved; the 2026-10-23 review's two
    findings repaired: (A) the anchor/S4c indexes AND the sliced window come
    from the ONE parsed step-block list (every entry, named or not); (B) the
    per-checkout credential invariant is asserted on the ACTIVE input value
    with comments ignored (test_12 proves both repairs discriminate)."""
    # --- Job B (the judgment runner): S4c present, NO suite step AT ALL, the
    # anchor-to-S4c window EMPTY counting EVERY step entry (named or unnamed) ---
    job_b, blocks_b = _wf_job(wf_text, "harness-trusted")
    names_b = [_wf_step_name(b[1]) for b in blocks_b]
    i_anchor = _wf_find(blocks_b, "Anchor the trusted gate")
    i_s4c = _wf_find(blocks_b, "S4c")
    if i_s4c is None:
        raise AssertionError("harness-trusted must run S4c (the trusted gate re-run)")
    if i_anchor is None:
        raise AssertionError("harness-trusted must anchor the driver from base")
    if any(n and n.startswith("S1b") for n in names_b):
        raise AssertionError("harness-trusted must NEVER run S1b — a suite step on the "
                             "judgment runner reopens the whole candidate-code class (the #66 P1)")
    if any(n and "required suites" in n for n in names_b):
        raise AssertionError("no suite-executing step may exist on the judgment runner")
    window = blocks_b[i_anchor + 1:i_s4c]
    if window:
        raise AssertionError("the anchor-to-S4c window must be EMPTY counting EVERY step entry "
                             "(named or not, from the ONE parsed step-block list) — got " +
                             repr([w[1][0].strip() for w in window]) + " (the structure IS the isolation)")
    if "sha256sum" not in job_b:
        raise AssertionError("the S4c run block keeps the #64 digest re-verification")
    # --- Job A (the suites runner): S1b present, the anchor precedes it ---
    _, blocks_a = _wf_job(wf_text, "harness-suites")
    i_a_anchor = _wf_find(blocks_a, "Anchor the trusted gate")
    i_a_s1b = _wf_find(blocks_a, "S1b")
    if i_a_s1b is None:
        raise AssertionError("harness-suites must run S1b (the trusted suites selection)")
    if i_a_anchor is None:
        raise AssertionError("harness-suites must anchor the driver before S1b")
    if not i_a_anchor < i_a_s1b:
        raise AssertionError("the anchor precedes S1b (the driver launch reads it)")
    # --- the harness job (S1 + S4b, candidate evidence) carries NEITHER trusted phase ---
    _, blocks_h = _wf_job(wf_text, "harness")
    names_h = [_wf_step_name(b[1]) for b in blocks_h]
    if any(n and n.startswith("S4c") for n in names_h):
        raise AssertionError("S4c must NOT run in the harness job — it lives on the harness-trusted runner")
    if any(n and n.startswith("S1b") for n in names_h):
        raise AssertionError("S1b must NOT run in the harness job — it lives on the harness-suites runner")
    # --- the CWE-522 hardening, per checkout step, on the ACTIVE input value ---
    for job_name, expected in (("harness", 1), ("harness-suites", 2), ("harness-trusted", 2)):
        _, blocks = _wf_job(wf_text, job_name)
        co = [b for b in blocks if "actions/checkout" in "".join(b[1])]
        if len(co) != expected:
            raise AssertionError(f"{job_name}: expected {expected} checkout step(s), found {len(co)}")
        for _, lines in co:
            if not _wf_active_persist_false(lines):
                raise AssertionError(
                    f"{job_name}: EVERY checkout reachable by candidate code must carry the ACTIVE "
                    "input persist-credentials: false — a DIRECT CHILD of the checkout's with: "
                    "mapping, value exactly false; a comment mentioning the phrase, or a "
                    "wrong-mapping line (an env: child), never satisfies the invariant "
                    "(the block starts: " + repr(lines[0].strip()) + ")")


class TrustedGateTests(unittest.TestCase):

    def setUp(self):
        """A fresh scratch dir per test (the stub trees are disposable)."""
        import tempfile
        self._td = tempfile.TemporaryDirectory(prefix="arvoo-tg-")
        self.td = Path(self._td.name)
        self.addCleanup(self._td.cleanup)

    def test_01_missing_required_suite_is_refused(self):
        """F-004, fail-closed: a required suite deleted from the candidate tree
        is ARV-TG-002 — the trusted selection never silently skips it (the
        candidate Makefile cannot hide a missing suite; recipes are not asked)."""
        stub = build_stub(self.td, delete_suite=_base_gate().TESTS[0], gutted_makefile=True)
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-002", r.stdout + r.stderr)

    def test_02_failing_required_suite_is_refused(self):
        """F-004: a required suite that FAILS is ARV-TG-003 — a gutted Makefile
        cannot fabricate a green (the driver runs the suite files itself).
        R-04(3): the refusal carries a BOUNDED TAIL of the failing suite's
        captured output — the predecessor discarded it, so the suite's own
        named failure was invisible in the trusted evidence (Greptile: 'a
        bounded tail prints with the refusal')."""
        stub = build_stub(self.td, gutted_makefile=True,
                          suite_mutations={_base_gate().TESTS[1]: _stub_suite("x", fail=True)})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-003", r.stdout + r.stderr)
        self.assertIn("stub suite ok: x", r.stdout + r.stderr,
                      "the failing suite's captured output was DISCARDED — the refusal "
                      "must carry a bounded tail so the named failure is visible in the "
                      "trusted evidence (R-04(3))")

    def test_03_silent_suite_is_the_vacuous_class(self):
        """A suite that exits 0 with NO output is ARV-TG-004 — the A03 vacuous
        pass class, refused by the trusted completion semantics."""
        stub = build_stub(self.td, suite_mutations={_base_gate().TESTS[0]: _stub_suite("x", silent=True)})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-004", r.stdout + r.stderr)

    def test_04_gutted_makefile_cannot_fake_suites_ran(self):
        """F-004's positive control: the stub's Makefile recipes are LIES (echo
        success, run nothing) yet the driver's suites phase runs every required
        suite file directly and is GREEN only because the real suites pass.
        The suites report STDERR-ONLY (the unittest shape — the part-2 binding
        rehearsal caught the driver's first draft refusing them with a false
        ARV-TG-004: zero-OUTPUT meant zero-STDOUT, and unittest never prints
        there); stderr-only reporters count as evidence on either stream."""
        stub = build_stub(self.td, gutted_makefile=True,
                          suite_mutations={t: _stub_suite(t, stderr_only=True)
                                           for t in _base_gate().TESTS})
        r = run_driver(self.td, stub, "suites")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-500:])
        for t in _base_gate().TESTS:
            self.assertIn(t, r.stdout, "the driver must report each required suite it ran")

    def test_05_gate_phase_reroots_and_judges_the_candidate(self):
        """F-006: the BASE's gate machinery re-rooted over the candidate tree.
        A VALID candidate passes every obligation; a candidate whose PR commit
        carries an UNDECLARED path is refused with ARV-SCOPE-002 — judged by the
        BASE's machinery, never the candidate's own gate."""
        stub = build_stub(self.td, gutted_makefile=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("GREEN — the gate passes", r.stdout)
        td2 = Path(str(self.td) + "-breach")
        td2.mkdir()
        stub2 = build_stub(td2, breach=True)
        r2 = run_driver(td2, stub2, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r2.returncode, 0)
        self.assertIn("ARV-SCOPE-002", r2.stdout + r2.stderr)

    def test_06_candidate_knownbad_registry_never_executes_in_the_trusted_run(self):
        """F-006's backstop, the named card case: the candidate's
        harness/known-bad/cases.py is `import sys; sys.exit(0)` — if ANY trusted
        code ever imported it, the run would exit green BEFORE the KB matrix
        prints its case lines. The trusted run must instead complete the WHOLE
        matrix (the BASE's cases judge the candidate) and stay GREEN — the
        candidate registry was never authority."""
        stub = build_stub(self.td, hostile_registry=True, gutted_makefile=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("PASS KB-", r.stdout, "the BASE's known-bad matrix must RUN to completion")
        self.assertIn("GREEN — the gate passes", r.stdout)

    def test_07_invalid_inputs_and_hostile_metadata_are_refused(self):
        """ARV-TG-001/005: a relative or nonexistent candidate root, a base
        without gate.py, and hostile branch metadata (the A02 class: data,
        never syntax) are each refused BEFORE anything executes; a hostile
        branch name with shell metacharacters creates NO side-effect file."""
        stub = build_stub(self.td)
        r = run_driver(self.td, stub, "suites", repo="relative/path")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-001", r.stdout + r.stderr)
        r = run_driver(self.td, stub, "gate", event="pull_request",
                       head="x; touch " + str(self.td / "pwned"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-001", r.stdout + r.stderr)
        self.assertFalse((self.td / "pwned").exists(), "hostile metadata became shell syntax")
        empty_base = self.td / "empty-base"          # EXISTS but carries no harness/gate.py
        empty_base.mkdir()
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH,
                       base=str(empty_base))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-005", r.stdout + r.stderr)

    def test_08_env_only_invocation_is_the_ci_form(self):
        """The CI form: metadata arrives through ARV_EVENT_NAME/ARV_PR_HEAD with
        NO --event/--head flags (the dispatch.py precedent). At the predecessor
        the call site passed the RAW argparse values — an env-only invocation
        handed the gate phase None and refused with a false ARV-TG-001 (found
        live by the S4c binding rehearsal; the other tests never caught it
        because they pass explicit flags). The env-only invocation must reach
        and pass the re-rooted gate, identically to the flag form."""
        stub = build_stub(self.td, gutted_makefile=True)
        r = run_driver(self.td, stub, "gate",
                       env_extra={"ARV_EVENT_NAME": "pull_request",
                                  "ARV_PR_HEAD": BRANCH})
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-500:])
        self.assertIn("GREEN — the gate passes", r.stdout)
        self.assertNotIn("ARV-TG-001", r.stdout + r.stderr,
                         "the env-only form must never be refused as None-metadata")

    def test_09_s4c_step_runs_even_when_s4b_fails(self):
        """R-04(2): the TRUSTED S4c step must carry `!cancelled()` — a plain
        workflow step is SKIPPED by GitHub Actions after any earlier failure,
        so a red S4b (the candidate's own gate, EVIDENCE since H-01b-CI)
        silently skipped the trusted re-run and the trusted evidence never
        flowed. The step's if-condition keeps S4c running over a red S4b
        (Greptile's finding; the pin parses the workflow file itself — the
        artifact under repair, never a copy). REGEX (LAW-11, corrected
        in-slice): the S4c name line is a LONG quoted string — the first
        draft's pattern expected the name to close right after "S4c and
        matched ZERO continuation lines, so the pin was vacuous against the
        real artifact shape; `[^\n]*` first consumes the name line, then the
        step group takes the 8+-space property lines (the next step's
        6-space `- name:` stops the group)."""
        import re
        wf = (REPO / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
        m = re.search(r"- name: \"S4c[^\n]*(?P<step>(?:\n[ ]{8,}[^\n]*)*)", wf)
        self.assertTrue(m, "the S4c step must exist in the verify workflow")
        step = m.group("step")
        self.assertIn("if:", step, "the S4c step group captured no property lines — the "
                     "pin must parse the real workflow shape, never match an empty group")
        cond = re.search(r"(?m)^[ ]{8}if:\s*\$\{\{\s*(?P<expression>[^}\n]+?)\s*\}\}\s*$", step)
        self.assertIsNotNone(cond, "the S4c step must define an executable if: expression")
        expression = cond.group("expression")
        self.assertIn("!cancelled()", expression,
                      "the S4c if-expression lacks `!cancelled()` — a failed S4b would SKIP "
                      "the trusted gate re-run, and the trusted evidence would never flow "
                      "(R-04(2))")
        self.assertIn("steps.checkout_base.outcome == 'success'", expression,
                      "the S4c if-expression must guard on its OWN job's base checkout "
                      "succeeding — a skipped anchor leaves no anchored driver and a bare "
                      "!cancelled() would execute a candidate-committed substitute (#64's "
                      "Major)")
        self.assertIn("steps.anchor_trusted_gate.outcome == 'success'", expression,
                      "the S4c if-expression must guard on its OWN job's anchor succeeding "
                      "— the sha256-verified anchoring is what makes the driver trusted")
        self.assertNotIn("success()", expression,
                         "the success() function would skip S4c on a red S4b — the exact defect")
        # the #64 SECOND review round (CodeRabbit TOCTOU): S4b runs candidate-
        # controlled Python in the same writable workspace, so the anchored
        # driver is RE-VERIFIED at S4c ENTRY (the direct swap-after-anchor
        # channel refuses); the same-job base-machinery residual is R-06's
        # card, named in the workflow comment, never claimed closed here.
        self.assertIn("sha256sum", step,
                      "the S4c run block must re-verify the anchored driver's digest against "
                      "base at entry — the post-anchor driver-swap refuses (the #64 TOCTOU "
                      "round's in-PR hardening)")
        self.assertIn("post-anchor tampering refused", step,
                      "the re-verification's refusal line must be pinned by name")

    def test_10_bounded_tail_keeps_the_end_of_the_output(self):
        """R-04(3) + the #64 review round (Greptile P2 + CodeRabbit,
        independently confirmed): the ARV-TG-003 bounded tail keeps the LAST
        1500 characters — a failing suite's named failure lives at the END of
        its output (unittest reports the traceback and verdict last), so a
        head-window drops the diagnostic behind long normal stdout. The stub
        prints a long normal prefix, then the failure marker."""
        long_stub = ("for i in range(200):\n"
                     "    print('normal output line: ' + str(i))\n"
                     "print('THE-NAMED-FAILURE-MARKER-AT-THE-END')\n"
                     "raise SystemExit(1)\n")
        stub = build_stub(self.td, suite_mutations={_base_gate().TESTS[1]: long_stub})
        r = run_driver(self.td, stub, "suites")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-TG-003", r.stdout + r.stderr)
        self.assertIn("THE-NAMED-FAILURE-MARKER-AT-THE-END", r.stdout + r.stderr,
                      "the bounded tail kept the FIRST 1500 chars — the marker at the END "
                      "of the output was dropped behind the long normal prefix (the #64 "
                      "review round's head-window defect)")
        self.assertIn("the LAST 1500 kept", r.stdout + r.stderr,
                      "the truncation marker must state which window was kept")

    def test_11_r06_isolated_job_shape(self):
        """R-06 (the #64 TOCTOU + the #66 review round's Greptile P1 escalation):
        the trusted phases are SPLIT ACROSS TWO RUNNERS — harness-suites runs
        the candidate suites on its own runner (nothing trusted is consumed
        after them there); harness-trusted runs S4c on a runner where
        candidate code NEVER executes (the #66 escalation: a suite can plant a
        fake interpreter on $GITHUB_PATH and file refreshes revert FILES, never
        the runner's accumulated PATH state — only a separate runner kills the
        class). The pin parses the workflow artifact (the structure IS the
        isolation): Job B carries NO suite-executing step AT ALL, the
        anchor-to-S4c window is EMPTY counting EVERY step entry — named or
        unnamed, from the ONE parsed step-block list (the 2026-10-23 review's
        Finding A: the #66 form mixed two index spaces — named-only indexes
        slicing an every-entry list — so an inserted unnamed step was invisible;
        red-01.txt observed the old form PASS over exactly that mutation) —
        and the harness job carries neither trusted phase. The credential
        invariant (CWE-522) is asserted per checkout step on the ACTIVE input
        value with comments ignored (Finding B; test_12 proves the pin
        discriminates both mutations)."""
        wf = (REPO / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
        _wf_check_r06_shape(wf)

    def test_12_r06_pin_discriminates_the_mutations(self):
        """The 2026-10-23 backend review's two live findings, as the standing
        discriminating regression (its §3: "a green self-check that cannot
        detect its named counterexample is not evidence of the property it
        claims to establish"). Each mutation fixture is VERIFIED to represent
        its named counterexample — the OLD #66 form's blindness is reproduced
        inline against the fixture (the exact defect observed live at the
        predecessor in red-01.txt) — then the REPAIRED check must REFUSE the
        mutated workflow, and the CLEAN workflow must still pass."""
        wf = (REPO / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")

        # --- MUT-A (Finding A): the unnamed step in the anchor-to-S4c window ---
        mut_a = _wf_mut_unnamed_window_step(wf)
        # fixture self-verification 1: the mutation took — an extra entry sits in
        # the window on the every-entry list, and it is the UNNAMED `- run:` form
        _, blocks_b = _wf_job(mut_a, "harness-trusted")
        i_anchor = _wf_find(blocks_b, "Anchor the trusted gate")
        i_s4c = _wf_find(blocks_b, "S4c")
        self.assertGreater(i_s4c - i_anchor, 1,
                           "MUT-A must actually insert a step into the window")
        self.assertTrue(re.match(r"^[ ]{6}- run: ", blocks_b[i_anchor + 1][1][0]),
                        "MUT-A's inserted entry must be the UNNAMED - run: form (the class "
                        "the #66 index space dropped)")
        # fixture self-verification 2: the OLD mixed-index-space form (the #66
        # merged code, re-implemented here as the named historical defect) is
        # BLIND to the mutation — the exact live observation of red-01.txt
        names_b = [n for n in (_wf_step_name(b[1]) for b in blocks_b) if n is not None]
        old_i_anchor = next(i for i, n in enumerate(names_b) if n.startswith("Anchor the trusted gate"))
        old_i_s4c = next(i for i, n in enumerate(names_b) if n.startswith("S4c"))
        old_step_lines = [b[1][0] for b in blocks_b]   # every entry's start line
        self.assertEqual(old_step_lines[old_i_anchor + 1:old_i_s4c], [],
                         "the old form's mixed index space must slice EMPTY over this "
                         "mutation — it is the old form's named blind spot")
        # the repaired check REFUSES the mutated workflow, naming the window
        with self.assertRaises(AssertionError) as cm:
            _wf_check_r06_shape(mut_a)
        self.assertIn("window", str(cm.exception))
        self.assertIn("- run:", str(cm.exception),
                      "the refusal must name the UNNAMED window entry it caught")

        # --- MUT-B (Finding B): the comment-only credential ---
        mut_b = _wf_mut_comment_only_credential(wf)
        # fixture self-verification 1: the mutated first checkout carries the
        # phrase ONLY as comments — no ACTIVE input line remains
        _, blocks_a = _wf_job(mut_b, "harness-suites")
        co = [b for b in blocks_a if "actions/checkout" in "".join(b[1])]
        self.assertEqual(len(co), 2, "the mutation must not change the checkout count")
        self.assertFalse(_wf_active_persist_false(co[0][1]),
                         "MUT-B must leave NO active persist-credentials input in the "
                         "first checkout")
        self.assertIn("persist-credentials: false", "".join(co[0][1]),
                      "MUT-B must leave the phrase present in raw text (as the comment) — "
                      "the substring form's blind spot")
        # fixture self-verification 2: the OLD raw-substring form PASSES over the
        # mutated block — exactly the live observation of red-01.txt
        self.assertTrue(all("persist-credentials: false" in "".join(b[1]) for b in co),
                        "the old per-block substring check must still pass over every "
                        "checkout — the mutation is the old form's named blind spot")
        # the repaired check REFUSES the mutated workflow, naming the job
        with self.assertRaises(AssertionError) as cm:
            _wf_check_r06_shape(mut_b)
        self.assertIn("harness-suites", str(cm.exception))
        self.assertIn("ACTIVE input persist-credentials: false", str(cm.exception),
                      "the refusal must name the ACTIVE-input invariant (never a comment match)")

        # --- MUT-C (the #67 Greptile round's P1): the wrong-mapping credential ---
        mut_c = _wf_mut_wrong_mapping_credential(wf)
        # fixture self-verification 1: the phrase remains as an ACTIVE line in
        # the step (a non-comment input-shaped line) but NO LONGER a child of
        # with: — the checkout INPUT is gone
        _, blocks_a = _wf_job(mut_c, "harness-suites")
        co = [b for b in blocks_a if "actions/checkout" in "".join(b[1])]
        self.assertEqual(len(co), 2, "the mutation must not change the checkout count")
        self.assertFalse(_wf_active_persist_false(co[0][1]),
                         "MUT-C must leave the phrase ACTIVE in the step (under env:) but NOT "
                         "as a with: child — the checkout input is gone")
        self.assertTrue(any((not ln.strip().startswith("#")) and _WF_PERSIST_RE.match(ln)
                            for ln in co[0][1]),
                        "MUT-C must keep an ACTIVE input-shaped line in the step — the "
                        "line-anywhere form's blind spot")
        # fixture self-verification 2: the OLD line-anywhere form (the #67
        # pre-P1-fix form, re-implemented here as the named historical defect —
        # comment-aware but mapping-BLIND) PASSES over the mutated block — the
        # exact observation of red-02.txt at the pushed head 5d4508a
        def _old_line_anywhere(block_lines):
            for ln in block_lines:
                if ln.lstrip().startswith("#"):
                    continue
                if _WF_PERSIST_RE.match(ln):
                    return True
            return False
        self.assertTrue(_old_line_anywhere(co[0][1]),
                        "the line-anywhere form must still pass over the env: child — the "
                        "mutation is that form's named blind spot (Greptile's P1)")
        # the repaired check REFUSES the mutated workflow, naming the mapping
        with self.assertRaises(AssertionError) as cm:
            _wf_check_r06_shape(mut_c)
        self.assertIn("harness-suites", str(cm.exception))
        self.assertIn("with:", str(cm.exception),
                      "the refusal must name the mapping-tracked invariant (a bare line "
                      "under env: is not the checkout input)")

        # --- the control: the CLEAN workflow passes the repaired check ---
        _wf_check_r06_shape(wf)



    def test_15_registered_new_suite_is_accepted_by_the_registration_check(self):
        """The #72 round's Greptile P1: a candidate may legitimately ADD a suite
        (registered in ITS OWN gate.py TESTS — a diff-visible, reviewable change
        — with its red record minted). The registration check must accept it:
        the check's subject is the file invisible to BOTH discovery surfaces,
        never a legitimately-registered addition. The TRUSTED suite SELECTION
        stays base-owned (the new suite is not REQUIRED until main adopts the
        tuple — the next slice's trusted run executes it); this is the
        registration semantics, never described as a trusted-gate bypass
        (CodeRabbit's wording catch). RED at the round's predecessor: the
        registration check compared against the BASE tuple alone and refused
        the candidate's own registered addition with ARV-RED-008."""
        stub = build_stub(self.td, gutted_makefile=True)
        # a NEW suite, registered in the CANDIDATE'S OWN TESTS tuple + a record.
        # The registration edit touches the stub's OWN gate.py — declared in the
        # stub's scope + claim row (the synthetic declaration of exactly this
        # reviewable change), or the scope/claims checks refuse it (the honest
        # form: registering a suite is a gate.py change, never a free edit)
        scope_txt = stub / "harness" / "runs" / SLICE / "scope.txt"
        scope_txt.write_text(
            scope_txt.read_text().replace(
                f"harness/runs/{SLICE}\n", f"harness/runs/{SLICE} D-041\n")
            + "harness/gate.py D-041\n")
        claims_md = stub / "CLAIMS.md"
        ctext = claims_md.read_text()
        claims_md.write_text(ctext.replace(
            "`notes.txt`, `harness/tests`, `harness/red-records.json`",
            "`notes.txt`, `harness/tests`, `harness/red-records.json`, `harness/gate.py`", 1))
        newsuite = stub / "harness" / "tests" / "test_brand_new.py"
        newsuite.write_text("import unittest\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        pass\n\nif __name__ == \"__main__\":\n    unittest.main()\n", encoding="utf-8")
        gp = stub / "harness" / "gate.py"
        gtext = gp.read_text(encoding="utf-8")
        # the CLAIM-040 repair: the anchor is the tuple's FIRST entry (stable),
        # never its mutable tail — the first suite addition after this test's
        # mint (test_sev.py, CLAIM-040) broke the tail-anchor form; the first-
        # entry insertion is equivalent (a registered addition, accepted) and
        # robust to every future tail change
        anchor = "\"harness/tests/test_migrations.py\","
        assert anchor in gtext
        gtext = gtext.replace(anchor, anchor + "\n         \"harness/tests/test_brand_new.py\",", 1)
        gp.write_text(gtext, encoding="utf-8")
        # the suite file lands FIRST (its own commit), THEN the record binds to
        # that commit — the real make-red form: the binding names history that
        # actually carries the file (the fixture's own catch: binding to the
        # repo's FIRST commit named a history that never carried the suite)
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the new suite lands"], cwd=stub,
                       check=True, capture_output=True)
        binding = subprocess.run(["git", "rev-parse", "HEAD"], cwd=stub,
                                 capture_output=True, text=True).stdout.strip()
        rr = stub / "harness" / "red-records.json"
        data = json.loads(rr.read_text())
        data["harness/tests/test_brand_new.py"] = {
            "schema": 2, "binding_commit": binding,
            "binding_sha256": hashlib.sha256(newsuite.read_bytes()).hexdigest(),
            "red_exit": 1, "red_code": "ARV-STUB-RED (the synthetic stub's own named refusal form)",
            "red_evidence": "synthetic new suite", "current_sha256": hashlib.sha256(newsuite.read_bytes()).hexdigest(),
            "amendments": []}
        rr.write_text(json.dumps(data, indent=2) + "\n")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the registered new-suite probe"],
                       cwd=stub, check=True, capture_output=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertEqual(r.returncode, 0,
                         "the trusted phase REFUSED a legitimately-registered new suite — "
                         "the registration check compared against the base tuple alone "
                         "(the #72 round's Greptile P1): " + r.stdout[-800:])

    def test_16_comment_only_registration_is_refused_through_the_trusted_phase(self):
        """The third pass (CodeRabbit Major, CWE-693): a candidate that places
        a new suite's path ONLY in a TESTS COMMENT (with the file present and
        a record minted) must be REFUSED with ARV-RED-008 — the registration
        parse must accept only ACTUAL tuple entries (the regex form extracted
        comment strings too; the AST parse never does). RED at the round's
        head: the comment path registered, the phase passed the suite as if
        legitimate while the trusted required selection would never run it."""
        stub = build_stub(self.td, gutted_makefile=True)
        scope_txt = stub / "harness" / "runs" / SLICE / "scope.txt"
        scope_txt.write_text(
            scope_txt.read_text().replace(f"harness/runs/{SLICE}\n", f"harness/runs/{SLICE} D-041\n")
            + "harness/gate.py D-041\n")
        claims_md = stub / "CLAIMS.md"
        ctext = claims_md.read_text()
        claims_md.write_text(ctext.replace(
            "`notes.txt`, `harness/tests`, `harness/red-records.json`",
            "`notes.txt`, `harness/tests`, `harness/red-records.json`, `harness/gate.py`", 1))
        newsuite = stub / "harness" / "tests" / "test_comment_only.py"
        newsuite.write_text("import unittest\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        pass\n\nif __name__ == \"__main__\":\n    unittest.main()\n", encoding="utf-8")
        gp = stub / "harness" / "gate.py"
        gtext = gp.read_text(encoding="utf-8")
        anchor = '"harness/tests/test_claims_paths.py",'
        # the path ONLY in a comment — never an actual tuple entry
        gpf = gp
        gpf.write_text(gtext.replace(anchor, anchor + '  # "harness/tests/test_comment_only.py"', 1), encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the suite lands"], cwd=stub, check=True, capture_output=True)
        binding = subprocess.run(["git", "rev-parse", "HEAD"], cwd=stub, capture_output=True, text=True).stdout.strip()
        rr = stub / "harness" / "red-records.json"
        data = json.loads(rr.read_text())
        data["harness/tests/test_comment_only.py"] = {
            "schema": 2, "binding_commit": binding,
            "binding_sha256": hashlib.sha256(newsuite.read_bytes()).hexdigest(),
            "red_exit": 1, "red_code": "ARV-STUB-RED (the synthetic stub's own named refusal form)",
            "red_evidence": "synthetic", "current_sha256": hashlib.sha256(newsuite.read_bytes()).hexdigest(),
            "amendments": []}
        rr.write_text(json.dumps(data, indent=2) + "\n")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the comment-only probe"], cwd=stub, check=True, capture_output=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r.returncode, 0,
                            "the trusted phase PASSED a comment-only 'registration' — the parse "
                            "accepted a path the trusted selection would never run (CWE-693): "
                            + r.stdout[-600:])
        self.assertIn("FAIL ARV-RED-008", r.stdout + r.stderr)

    def test_17_function_scoped_tests_assignment_never_registers(self):
        """The fourth pass (CodeRabbit Major, CWE-693): the AST WALK found
        TESTS assignments in ANY scope — a candidate could hide
        TESTS = (".../test_rogue.py",) inside a FUNCTION and pass the
        registration check while the module's real tuple never carries it.
        Only the MODULE-LEVEL assignments count (the last one wins — Python's
        own execution semantics). RED at the walk form: the function-scoped
        path registered and the phase passed the suite as legitimate."""
        stub = build_stub(self.td, gutted_makefile=True)
        scope_txt = stub / "harness" / "runs" / SLICE / "scope.txt"
        scope_txt.write_text(
            scope_txt.read_text().replace(f"harness/runs/{SLICE}\n", f"harness/runs/{SLICE} D-041\n")
            + "harness/gate.py D-041\n")
        claims_md = stub / "CLAIMS.md"
        ctext = claims_md.read_text()
        claims_md.write_text(ctext.replace(
            "`notes.txt`, `harness/tests`, `harness/red-records.json`",
            "`notes.txt`, `harness/tests`, `harness/red-records.json`, `harness/gate.py`", 1))
        newsuite = stub / "harness" / "tests" / "test_function_scoped.py"
        newsuite.write_text("import unittest\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        pass\n\nif __name__ == \"__main__\":\n    unittest.main()\n", encoding="utf-8")
        gp = stub / "harness" / "gate.py"
        gtext = gp.read_text(encoding="utf-8")
        # the path ONLY inside a function-scoped TESTS assignment — never module-level
        gpf_payload = ("\n\ndef _probe_hidden_scope():\n"
                       "    TESTS = (\"harness/tests/test_function_scoped.py\",)\n"
                       "    return TESTS\n")
        gp.write_text(gtext.rstrip() + gpf_payload, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the suite lands"], cwd=stub, check=True, capture_output=True)
        binding = subprocess.run(["git", "rev-parse", "HEAD"], cwd=stub, capture_output=True, text=True).stdout.strip()
        rr = stub / "harness" / "red-records.json"
        data = json.loads(rr.read_text())
        data["harness/tests/test_function_scoped.py"] = {
            "schema": 2, "binding_commit": binding,
            "binding_sha256": hashlib.sha256(newsuite.read_bytes()).hexdigest(),
            "red_exit": 1, "red_code": "ARV-STUB-RED (the synthetic stub's own named refusal form)",
            "red_evidence": "synthetic", "current_sha256": hashlib.sha256(newsuite.read_bytes()).hexdigest(),
            "amendments": []}
        rr.write_text(json.dumps(data, indent=2) + "\n")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the function-scoped probe"], cwd=stub, check=True, capture_output=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r.returncode, 0,
                            "the trusted phase PASSED a function-scoped TESTS 'registration' — the "
                            "AST walk found a scope the module never executes: " + r.stdout[-500:])
        self.assertIn("FAIL ARV-RED-008", r.stdout + r.stderr)

    def test_18_missing_sev_report_is_refused_by_the_trusted_gate_phase(self):
        """H-02 (CLAIM-041): a candidate whose slice carries NO SEV report is
        refused by the BASE's machinery re-rooted over the candidate — the
        obligation is enforced by the trusted path, never only by the
        candidate's own gate. RED at the predecessor: the gate phase had no SEV
        step, so the deletion dispatched green."""
        stub = build_stub(self.td)
        (stub / "harness" / "runs" / SLICE / "sev.json").unlink()
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-SEV-001", r.stdout + r.stderr)

    def test_19_candidate_gate_omitting_the_sev_step_is_still_refused(self):
        """H-02's structural protection (the coordination-weakening class): a
        candidate that GUTS its own gate.py — removing the SEV step entirely —
        is still refused by the trusted phase, because the BASE's machinery
        (never the candidate's gate) carries the obligation. The candidate's
        own green is never the only evidence for the harness check (F-006's
        form, applied to the SEV boundary)."""
        stub = build_stub(self.td)
        gp = stub / "harness" / "gate.py"
        gtext = gp.read_text(encoding="utf-8")
        marker = "sev.check_sev"
        self.assertIn(marker, gtext, "the candidate gate carries the SEV step at this revision (the wiring landed)")
        gtext = gtext.replace(marker, "pass  # the omitted gate invocation (the must-reject)")
        gp.write_text(gtext, encoding="utf-8")
        (stub / "harness" / "runs" / SLICE / "sev.json").unlink()
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ARV-SEV-001", r.stdout + r.stderr)

    def test_13_self_authorized_red_refresh_is_refused(self):
        """CLAIM-037 / F-007's named defect, end-to-end through the trusted
        phase: the candidate edits a frozen suite and refreshes its OWN record
        (the make-red form — the candidate-supplied current_sha256). The
        trusted run must refuse with ARV-RED-006: a changed test is authorized
        ONLY by a typed amendment chaining exactly from the trusted prior
        digest (prior == the baseline's, new == the actual file) — the record
        refresh alone is the self-authorization hole (observed RED at the
        predecessor: the trusted run passed the refreshed form GREEN)."""
        stub = build_stub(self.td, gutted_makefile=True)
        key = _base_gate().TESTS[0]
        t = stub / key
        t.write_text(t.read_text(encoding="utf-8") + "\n# edited after red (the self-authorization probe)\n", encoding="utf-8")
        import hashlib as _h, json as _j
        rr = stub / "harness" / "red-records.json"
        data = _j.loads(rr.read_text())
        data[key]["current_sha256"] = _h.sha256(t.read_bytes()).hexdigest()  # the make-red refresh
        rr.write_text(_j.dumps(data, indent=2) + "\n")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the self-authorized refresh probe"],
                       cwd=stub, check=True, capture_output=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r.returncode, 0,
                            "the trusted run PASSED a self-authorized red refresh — the candidate-"
                            "supplied current_sha256 authorized its own edited test (F-007's named defect)")
        self.assertIn("FAIL ARV-RED-006", r.stdout + r.stderr,
                      "the refusal form is required: the KB runner's broken-guard line "
                      "('expected ARV-RED-006') must never satisfy this probe")

    def test_14_false_revision_binding_is_refused(self):
        """CLAIM-037: the typed record's git binding, end-to-end through the
        trusted phase: a record whose binding digest does not match the file
        at its binding commit is a FALSE binding — the revision claim names
        history that does not carry the claimed content. The trusted run must
        refuse with ARV-RED-007 (observed RED at the predecessor: no binding
        existed to be false — the class was unobservable)."""
        stub = build_stub(self.td, gutted_makefile=True)
        key = _base_gate().TESTS[0]
        rr = stub / "harness" / "red-records.json"
        data = json.loads(rr.read_text())
        data[key]["binding_sha256"] = "e" * 64  # a fabricated digest — no revision carries it
        data[key]["binding_commit"] = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=stub,
            capture_output=True, text=True).stdout.strip() or "0" * 40
        rr.write_text(json.dumps(data, indent=2) + "\n")
        subprocess.run(["git", "add", "-A"], cwd=stub, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "the false-binding probe"],
                       cwd=stub, check=True, capture_output=True)
        r = run_driver(self.td, stub, "gate", event="pull_request", head=BRANCH)
        self.assertNotEqual(r.returncode, 0,
                            "the trusted run PASSED a falsely-bound red record — the revision "
                            "claim named content git does not carry")
        self.assertIn("FAIL ARV-RED-007", r.stdout + r.stderr,
                      "the refusal form is required: the KB runner's broken-guard line "
                      "('expected ARV-RED-007') must never satisfy this probe")


if __name__ == "__main__":
    unittest.main(verbosity=2)
