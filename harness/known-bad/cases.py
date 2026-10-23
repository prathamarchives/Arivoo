#!/usr/bin/env python3
"""harness/known-bad/cases.py — the proactive-set known-bads (S4; D-036; KB-01..06).

Each case is a deliberately broken state + the failure code the gate MUST emit
when judging it (F-03's set, per the review's S4): scope breach · protected-path
edit · skipped test · hand-written Proof Sheet · lowered threshold (a protected-
path edit without an owner ref) · missing red record · test edited after red ·
unapproved dependency.

Each case is SELF-CONTAINED: it mutates its own temp copy, then invokes the
TARGETED check loaded from that copy (spec-loaded — no module-cache pollution).
A known-bad that passes is a broken guard (KB-05): the harness goes red and
building stops.
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import re

SLICE = "known-bad-probe"  # the scratch slice the probe declaration lives under

# (id, description, expected code, probe(copy_dir) -> None)
CASES = []


def case(cid, desc, code):
    def reg(fn):
        CASES.append((cid, desc, code, fn))
        return fn
    return reg


def _load(copy: pathlib.Path, name: str):
    """Load a module BY FILE PATH (never the cached one).

    H-01b-CI (session 23): in the TRUSTED gate re-run, module BYTES come from
    the BASE's machinery (ARV_TRUSTED_KB_MACHINERY, set by gate.run_known_bads
    to the base's own harness dir) while all DATA (records, declarations,
    registry, trees) comes from the mutated work copy — the candidate's
    harness modules, including its known-bad registry, never execute inside
    the trusted judge (F-006; a candidate cases.py that runs SystemExit(0) at
    import made three probes vacuous before this routing — reproduced live by
    test_trusted_gate.test_06). Unset, the legacy self-check form holds:
    modules load from the copy (the candidate's own gate proving its own
    checks fire — the S4b self-report semantics, unchanged)."""
    import os
    mach = os.environ.get("ARV_TRUSTED_KB_MACHINERY", "")
    root = pathlib.Path(mach) if mach else copy
    path = root / (name.replace(".", "/") + ".py")
    spec = importlib.util.spec_from_file_location(name.replace(".", "_") + "_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@case("KB-SCOPE-001", "a diff touching a path OUTSIDE the slice's declared scope",
      "ARV-SCOPE-002")
def kb_scope(copy: pathlib.Path) -> None:
    _load(copy, "harness.scope").check_scope(["docs/unrelated/outside.txt"], SLICE)


@case("KB-PROT-002", "a protected-path edit with no owner-referenced declaration line",
      "ARV-PROT-002")
def kb_prot(copy: pathlib.Path) -> None:
    _load(copy, "harness.scope").check_scope([".github/workflows/verify.yml"], SLICE)


@case("KB-TEST-003", "a declared test file removed (skipped test) — the gate fails closed",
      "ARV-GATE-001")
def kb_test(copy: pathlib.Path) -> None:
    (copy / "harness" / "tests" / "test_migrations.py").unlink()
    _load(copy, "harness.gate").check_declared_files()


@case("KB-PRF-004", "a hand-edited Proof Sheet (a line appended after assembly)",
      "ARV-PRF-004")
def kb_prf(copy: pathlib.Path) -> None:
    sheet = copy / "harness" / "runs" / SLICE / "proofsheet.md"
    sheet.write_text(sheet.read_text() + "\n- hand-added claim (the must-reject)\n")
    ps = _load(copy, "harness.proofsheet")
    ps.RUNS = copy / "harness" / "runs"
    derived = ps.assemble(SLICE, "- probe only")
    if derived != sheet.read_text():
        print("FAIL ARV-PRF-004: the sheet on disk does not equal the re-derived sheet — hand-edited")


@case("KB-LAW09-005", "a constraint-weakening edit (a protected-path file with no owner ref on its declaration)",
      "ARV-PROT-002")
def kb_threshold(copy: pathlib.Path) -> None:
    _load(copy, "harness.scope").check_scope(["harness/scope.py"], SLICE)


@case("KB-RED-006", "a red record missing for a test file", "ARV-RED-001")
def kb_missing_red(copy: pathlib.Path) -> None:
    rr = copy / "harness" / "red-records.json"
    data = json.loads(rr.read_text())
    data.pop("harness/tests/test_substrate.py")
    rr.write_text(json.dumps(data, indent=2) + "\n")
    _load(copy, "harness.gate").check_red_records()


@case("KB-RED-007", "a test file edited AFTER its red record (no amendment)", "ARV-RED-002")
def kb_edited_after_red(copy: pathlib.Path) -> None:
    t = copy / "harness" / "tests" / "test_migrations.py"
    t.write_text(t.read_text() + "\n# edited after red (the must-reject)\n")
    _load(copy, "harness.gate").check_red_records()


@case("KB-DEP-008", "an unapproved third-party import added", "ARV-DEP-008")
def kb_dep(copy: pathlib.Path) -> None:
    m = copy / "harness" / "migrate.py"
    m.write_text(m.read_text() + "\nimport requests  # the must-reject\n")
    _load(copy, "harness.scope").check_deps()


# --- session 19, CLAIM-002 (D-038/LAW-31): the claims-registry guards (red-first) ---

_CLAIMS_ROW_OVERLAP_PARTNER = (
    "| CLAIM-998 | 19 | Test Agent | `slice/claim-998-overlap-partner` | `context/extracted/99-PROBE-PARTNER.md` "
    "| — (probe: no reservation) | 2026-10-19 | the SYNTHETIC overlap partner — the probe is self-contained, "
    "never coupled to a live claim's scope (the A11 probe-coupling class, caught by its own matrix a third time "
    "at the H-01b split when a legitimate rescope dropped context/extracted/ from the only OPEN claim; fixed for real) |\n"
)
_CLAIMS_ROW_OVERLAP = (
    "| CLAIM-999 | 19 | Test Agent | `slice/claim-999-overlap-probe` | `context/extracted/`, `docs/unrelated/` "
    "| INT-125 | 2026-10-19 | the overlap probe: overlaps the synthetic partner's context/extracted/99-PROBE-PARTNER.md |\n"
)


def _open_claims_row(text: str, probe_row: str) -> str:
    """Insert probe_row as the LAST row of the OPEN table (structure-anchored since
    the CLAIM-001-row anchor went blind the moment that claim CLOSED — the KB
    matrix caught its own regression at the session-19 close; never anchor a
    probe to a mutable row: anchor to the section's table shape)."""
    import re as _re
    m = _re.search(r"^## Open claims\s*$", text, _re.M)
    if not m:
        return text
    tail = text[m.end():]
    m2 = _re.search(r"^## ", tail, _re.M)
    section = tail[:m2.start()] if m2 else tail
    rows = [ln for ln in section.split("\n") if ln.strip().startswith("|")
            and not set(ln.strip()) <= {"|", "-", " ", ":"}
            and not ln.strip().startswith("| Claim |")]
    if rows:
        last = rows[-1]
        return text.replace(last, last + "\n" + probe_row, 1)
    sep = "|-------|---------|-------|--------|----------------|---------------|---------|-------|"
    return text.replace(sep, sep + "\n" + probe_row, 1) if sep in text else text + "\n" + probe_row


@case("KB-CLM-001", "the claims registry deleted (LAW-31 has no substrate)",
      "ARV-CLM-001")
def kb_clm_missing(copy: pathlib.Path) -> None:
    (copy / "CLAIMS.md").unlink()
    _load(copy, "harness.claims").check_registry()


@case("KB-CLM-002", "two OPEN claims overlapping on a non-shared file (the session-19 collision class)",
      "ARV-CLM-002")
def kb_clm_overlap(copy: pathlib.Path) -> None:
    c = copy / "CLAIMS.md"
    text = c.read_text()
    text = _open_claims_row(text, _CLAIMS_ROW_OVERLAP_PARTNER)
    c.write_text(_open_claims_row(text, _CLAIMS_ROW_OVERLAP))
    _load(copy, "harness.claims").check_registry()


@case("KB-CLM-003", "a duplicate INT reservation (the merge-order race the registry prevents)",
      "ARV-CLM-003")
def kb_clm_dup_reservation(copy: pathlib.Path) -> None:
    c = copy / "CLAIMS.md"
    text = c.read_text()
    dup = (
        "| CLAIM-998 | 19 | Test Agent | `slice/claim-998-dup-probe` | `docs/unrelated/` "
        "| INT-124 | 2026-10-19 | the duplicate-reservation probe |\n"
    )
    c.write_text(_open_claims_row(text, dup))
    _load(copy, "harness.claims").check_registry()


@case("KB-CLM-004", "a malformed OPEN row (branch does not carry the claim id)",
      "ARV-CLM-004")
def kb_clm_malformed(copy: pathlib.Path) -> None:
    c = copy / "CLAIMS.md"
    text = c.read_text()
    bad = (
        "| CLAIM-997 | 19 | Test Agent | `slice/wrong-branch-name` | `docs/unrelated/` "
        "| INT-125 | 2026-10-19 | the well-formedness probe: branch lacks claim-997 |\n"
    )
    c.write_text(_open_claims_row(text, bad))
    _load(copy, "harness.claims").check_registry()


@case("KB-CLM-005", "a PR-mode diff with no OPEN claim for its branch (unclaimed work)",
      "ARV-CLM-005")
def kb_clm_unclaimed(copy: pathlib.Path) -> None:
    _load(copy, "harness.claims").check_branch_claim(
        "slice/claim-777-unclaimed-probe", ["docs/unrelated/file.txt"])


@case("KB-SCOPE-006", "a SIBLING-PREFIX path against a file declaration (README.md vs README.md.unrelated)",
      "ARV-SCOPE-002")
def kb_scope_sibling(copy: pathlib.Path) -> None:
    """The sibling-prefix regression probe: README.md.unrelated must REFUSE
    against a REAL README.md declaration (the raw-startswith defect would
    match it and the guard would go silent — the broken guard, KB-05).

    R-04(8) + the #64 review round (Greptile P1 + CodeRabbit, independently
    confirmed): the probe's OWN declaration (the predecessor's scratch
    declaration named no README.md, so the refusal fired for the trivial
    outside-declaration reason and could not detect the restored defect — P3,
    red-01.txt) AND the positive call's stdout is captured SEPARATELY — the
    first draft inspected only the RETURN list while check_scope's own PRINT
    of ARV-SCOPE-002 leaked into the expected-code channel, so an
    over-refusing boundary masqueraded as the sibling-prefix catch.
    """
    # R-04(8): the probe's OWN declaration. The predecessor checked
    # README.md.unrelated against the scratch declaration that names NO
    # README.md — the refusal fired for the trivial OUTSIDE-DECLARATION
    # reason, and a scope.py with the sibling-prefix DEFECT restored (raw
    # startswith) still passed the probe: it could not detect the regression
    # it exists to backstop (P3, the vacuous form — red-01.txt). Declaring
    # README.md makes the sibling-prefix boundary the ONLY discriminating
    # reason the refusal can fire, and the POSITIVE side below guards the
    # over-refusal direction the same probe-run.
    (copy / "harness" / "runs" / SLICE / "scope.txt").write_text("README.md\n",
                                                                encoding="utf-8")
    scope = _load(copy, "harness.scope")
    # the POSITIVE side: the declared file itself MUST match (exact equality).
    # The positive call's stdout is captured SEPARATELY — check_scope PRINTS
    # its failures, so an un-nested call would leak ARV-SCOPE-002 into the
    # expected-code channel and the over-refusal would masquerade as the
    # sibling-prefix catch (the #64 review round's finding). A violation is
    # named on the captured channel and the expected code is NEVER printed:
    # the case fails as the broken guard it is (KB-05).
    positive_out = io.StringIO()
    with contextlib.redirect_stdout(positive_out):
        positive_fails = scope.check_scope(["README.md"], SLICE)
    if any("ARV-SCOPE-002" in f for f in positive_fails):
        print("FAIL ARV-SCOPE-006: the DECLARED file README.md was itself refused — the "
              "boundary over-refuses; the sibling-prefix refusal below would be vacuous")
        return
    # the SIBLING PREFIX: README.md.unrelated must refuse — a raw-startswith
    # regression matches it and the guard goes silent (the broken guard KB-05)
    scope.check_scope(["README.md.unrelated"], SLICE)


@case("KB-CLM-006", "a claim ID present in BOTH the open and closed tables (registry drift)",
      "ARV-CLM-006")
def kb_clm_dup(copy: pathlib.Path) -> None:
    """The both-tables registry-drift probe — SYNTHETIC rows, self-contained
    (never borrowing live registry state: the predecessor borrowed the first
    live open row; on a reconciled registry its regex reached into the CLOSED
    table and the guard never fired — P2, red-01.txt)."""
    # R-04(7): SYNTHETIC rows. The predecessor borrowed the FIRST live open
    # row — masked only because a live row happened to exist (Greptile:
    # latent); on a reconciled (empty-open) registry its open-row regex
    # reached into the CLOSED table, duplicated a closed ID into the closed
    # table, and the guard never fired (P2 — a broken-guard RED against a
    # legitimate live state, red-01.txt). The synthetic registry is
    # self-contained: the probe never touches live registry state.
    (copy / "CLAIMS.md").write_text(
        "# CLAIMS (synthetic probe registry)\n\n## Open claims\n\n"
        "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
        "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n"
        "| CLAIM-DUP | 99 | probe | `slice/claim-dup-both-tables-probe` | `notes.txt` | — (synthetic probe row) | 2026-10-22 | the synthetic both-tables drift target |\n\n"
        "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n"
        "| CLAIM-DUP | the synthetic closed row carrying the SAME id | 2026-10-22 | probe |\n",
        encoding="utf-8")
    _load(copy, "harness.claims").check_registry()


@case("KB-CLM-007", "the same claim ID TWICE in one table (intra-table drift — the duplicate-CLAIM-021 class)",
      "ARV-CLM-007")
def kb_clm_intra_dup(copy: pathlib.Path) -> None:
    """The intra-table duplicate probe (ARV-CLM-007's own known-bad — the
    duplicate-CLAIM-021 class): the same claim ID twice in one table is
    drift the both-tables check can never see."""
    # R-04(9)'s probe side: the duplicate survived every check at the
    # predecessor because ARV-CLM-006 covers only the BOTH-TABLES class —
    # the ratchet's own known-bad, synthetic (P2's lesson: never borrow live
    # registry state)
    (copy / "CLAIMS.md").write_text(
        "# CLAIMS (synthetic probe registry)\n\n## Open claims\n\n"
        "| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |\n"
        "|-------|---------|-------|--------|----------------|---------------|---------|-------|\n\n"
        "## Closed claims\n\n| Claim | Result | Closed | Evidence |\n|-------|--------|--------|----------|\n"
        "| CLAIM-TWIN | the first synthetic row | 2026-10-22 | probe |\n"
        "| CLAIM-TWIN | the duplicate synthetic row (intra-table drift) | 2026-10-22 | probe |\n",
        encoding="utf-8")
    _load(copy, "harness.claims").check_registry()


# --- CLAIM-037 (H-01c-evidence/privacy, part 1 — F-007's named defect + the typed records +
#     fail-closed registration + the proofsheet numbering rider). Named codes frozen BEFORE
#     the implementation (the H-01a convention; RED-first — every case below is observed
#     NOT CAUGHT at the predecessor, captured in the slice's red-01.txt):
#       ARV-RED-006  a changed test self-authorized by a bare make-red refresh — the
#                    candidate-supplied record alone cannot authorize; the amendment
#                    must chain EXACTLY from the trusted prior digest (F-007 §5.3)
#       ARV-RED-007  an untyped or falsely-bound red record — a written assertion is
#                    not an observed failure; the binding must verify against git
#       ARV-RED-008  an unregistered test file under harness/tests/ (the
#                    discovery/registration gap — fail-closed suite registration)
#       ARV-PRF-006  a proof-record write into an unparseable/occupied numbering
#                    context (the count-based overwrite class, record 29 §8)

@case("KB-RED-008", "a test edited + its record self-refreshed (the make-red form) against a trusted baseline — no chaining amendment",
      "ARV-RED-006")
def kb_self_authorized_refresh(copy: pathlib.Path) -> None:
    """F-007's named defect, the exact self-authorization: the candidate edits a
    frozen test and refreshes its OWN record (the make-red form). Under the
    trusted-baseline repair the refresh alone must refuse — the changed test is
    authorized only by an amendment chaining exactly from the trusted prior
    digest (prior == the baseline's, new == the actual file)."""
    import hashlib
    import json
    import os
    import tempfile
    key = "harness/tests/test_migrations.py"
    rr = copy / "harness" / "red-records.json"
    original = json.loads(rr.read_text())
    with tempfile.TemporaryDirectory() as td:
        bdir = pathlib.Path(td) / "base"
        (bdir / "harness").mkdir(parents=True)
        (bdir / "harness" / "red-records.json").write_text(json.dumps(original, indent=2) + "\n")
        t = copy / key
        t.write_text(t.read_text(encoding="utf-8") + "\n# edited after red (the self-authorization must-reject)\n", encoding="utf-8")
        data = json.loads(rr.read_text())
        data[key]["current_sha256"] = hashlib.sha256(t.read_bytes()).hexdigest()
        rr.write_text(json.dumps(data, indent=2) + "\n")
        os.environ["ARV_TRUSTED_BASE"] = str(bdir)
        try:
            _load(copy, "harness.gate").check_red_records()
        finally:
            del os.environ["ARV_TRUSTED_BASE"]


@case("KB-RED-009", "a prose-only red record (no typed observed-red, no honest unrecovered marker)",
      "ARV-RED-007")
def kb_untyped_record(copy: pathlib.Path) -> None:
    """The typed-record guard: a record reduced to the predecessor's prose-only
    schema — no typed observed-red (red_exit/red_code), no git-verifiable
    binding, no red_unrecovered marker — must refuse. A written assertion is
    not an observed failure (the card's own words)."""
    import json
    rr = copy / "harness" / "red-records.json"
    data = json.loads(rr.read_text())
    key = "harness/tests/test_migrations.py"
    data[key] = {"red_evidence": "the author asserts it failed (a written assertion is not an observed failure)",
                 "current_sha256": data[key]["current_sha256"],
                 "amendments": data[key].get("amendments", [])}
    rr.write_text(json.dumps(data, indent=2) + "\n")
    _load(copy, "harness.gate").check_red_records()


@case("KB-RED-010", "an unregistered test file under harness/tests/ (the discovery/registration gap)",
      "ARV-RED-008")
def kb_unregistered_suite(copy: pathlib.Path) -> None:
    """Fail-closed suite registration: a test file that exists under
    harness/tests/ but appears in NEITHER the TESTS registry NOR the red records
    sails through every discovery surface at the predecessor (the Makefile glob
    runs it locally, but the trusted selection and the red control never see
    it) — the registration gap must refuse."""
    (copy / "harness" / "tests" / "test_rogue_probe.py").write_text(
        "# an unregistered suite file — the must-reject (fail-closed registration)\n", encoding="utf-8")
    _load(copy, "harness.gate").check_red_records()


@case("KB-PRF-006", "a proof-record write into an unparseable numbering context (the count-based overwrite class)",
      "ARV-PRF-006")
def kb_slot_unparseable(copy: pathlib.Path) -> None:
    """The proofsheet numbering rider (record 29 §8's routed defect): the
    count-based writer stalled on one slot whenever a gap made count+1 name an
    existing record, overwriting middle captures one by one. The repaired
    writer numbers by max(existing)+1 and refuses fail-closed when the runs
    dir carries a record name it cannot parse — an ambiguous numbering
    context is a refusal, never a guess."""
    import json
    runs = copy / "harness" / "runs" / SLICE
    ps = _load(copy, "harness.proofsheet")
    ps.RUNS = copy / "harness" / "runs"
    seed = json.dumps({"command": "probe", "exit_code": 0, "output_sha256": "0" * 64,
                       "recorded_at": "2026-10-16T00:00:00+00:00"}, indent=2) + "\n"
    for n in ("01", "02", "03"):
        (runs / f"run-{n}.json").write_text(seed)
    (runs / "run-05.json").write_text(seed)  # the gap that stalls count-based numbering on run-05
    (runs / "run-ab.json").write_text(seed)  # the unparseable name — an ambiguous numbering context
    try:
        ps.write_record(SLICE, "probe-write", 0, "out")
    except SystemExit:
        pass

# --- CLAIM-037, the #72 review round (Greptile 2 P1 + 2 P2, CodeRabbit Minor + Major).
#     Named codes frozen BEFORE the round's fixes (RED-first; every case observed
#     NOT CAUGHT at the round's head 625396d, captured in red-02.txt):
#       ARV-RED-007 also fires for: (a) a binding naming history git CANNOT SHOW
#               (a nonexistent commit — the predecessor printed a NOTE and passed
#               the false claim); (b) red_unrecovered on a record with NO trusted
#               prior state (a new suite's mint — the marker exists for honestly
#               lost history, never as the typed-red bypass)

@case("KB-RED-011", "a record whose binding_commit does not exist in git history",
      "ARV-RED-007")
def kb_nonexistent_binding(copy: pathlib.Path) -> None:
    """Greptile P1 (the #72 round): a fabricated commit NAME (40 hex chars that
    name no revision) sailed through as 'unverifiable' — a NOTE without a
    failure. In a git context, git's inability to show the commit IS the false
    claim: a revision binding must name history that exists."""
    import json, subprocess
    # the git-context form: the work copies are non-git by construction, so the
    # probe git-inits its own copy — the binding check's git context must be
    # REAL for the nonexistent-commit refusal to be exercisable
    subprocess.run(["git", "init", "-q"], cwd=copy, capture_output=True)
    subprocess.run(["git", "config", "user.email", "probe@test.local"], cwd=copy, capture_output=True)
    subprocess.run(["git", "config", "user.name", "probe"], cwd=copy, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=copy, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "probe base"], cwd=copy, capture_output=True)
    rr = copy / "harness" / "red-records.json"
    data = json.loads(rr.read_text())
    key = "harness/tests/test_migrations.py"
    data[key]["binding_commit"] = "f" * 40  # names nothing in any history
    rr.write_text(json.dumps(data, indent=2) + "\n")
    _load(copy, "harness.gate").check_red_records()


@case("KB-RED-012", "red_unrecovered on a record with NO trusted prior state (the new-mint bypass)",
      "ARV-RED-007")
def kb_unrecovered_without_baseline(copy: pathlib.Path) -> None:
    """CodeRabbit Minor (the #72 round): a NEW suite's record is absent from the
    trusted baseline, so ARV-RED-006 skips it; a schema-2 record carrying
    red_unrecovered (instead of the typed observed-red) then bypasses
    red_exit/red_code. The marker is for honestly-lost history — records that
    EXIST in the baseline (the two smash-class migrations) — never a new
    mint's bypass."""
    import hashlib
    import json
    import os
    import tempfile
    rr = copy / "harness" / "red-records.json"
    original = json.loads(rr.read_text())
    key = "harness/tests/test_migrations.py"
    rogue = "harness/tests/test_new_suite_probe.py"
    data = json.loads(rr.read_text())
    # the rogue suite FILE must exist for the TESTS loop to examine its record
    # (the probe's own second catch: registering a file that is not there is
    # the ARV-GATE-001 class, not the bypass case under test)
    (copy / "harness" / "tests" / "test_new_suite_probe.py").write_text(
        "# the bypass probe's suite file (must exist for its record to be examined)\n", encoding="utf-8")
    # the rogue suite must be REGISTERED in the copy's own gate.py TESTS (the
    # registered-addition form) — otherwise the per-record check never examines
    # its record and the bypass stays invisible (the probe's own first miss)
    gpf = copy / "harness" / "gate.py"
    gtext = gpf.read_text(encoding="utf-8")
    # a MIDDLE tuple entry as the anchor — stable across the real tuple AND the
    # test stubs whose tuples end with their own additions (the probe's own
    # third catch: anchoring on the LAST entry crashed against test_15's stub)
    anchor = '"harness/tests/test_claims_paths.py",'
    assert anchor in gtext
    gpf.write_text(gtext.replace(anchor, anchor + '\n         "harness/tests/test_new_suite_probe.py",', 1), encoding="utf-8")
    data[rogue] = {"schema": 2,
                   "binding_commit": original[key].get("binding_commit", "0" * 40),
                   "binding_sha256": "0" * 64,
                   "red_unrecovered": True,  # the bypass attempt: no red_exit/red_code
                   "red_evidence": "the new suite's record, never in any baseline",
                   "current_sha256": "0" * 64, "amendments": []}
    rr.write_text(json.dumps(data, indent=2) + "\n")
    with tempfile.TemporaryDirectory() as td:
        bdir = pathlib.Path(td) / "base"
        (bdir / "harness").mkdir(parents=True)
        (bdir / "harness" / "red-records.json").write_text(json.dumps(original, indent=2) + "\n")
        os.environ["ARV_TRUSTED_BASE"] = str(bdir)
        try:
            _load(copy, "harness.gate").check_red_records()
        finally:
            del os.environ["ARV_TRUSTED_BASE"]
