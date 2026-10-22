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
import importlib.util
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
    # A violation is named on the captured channel and the expected code is
    # never printed — the case fails as the broken guard it is (KB-05), so an
    # over-refusing boundary can never masquerade as the sibling-prefix catch
    if any("ARV-SCOPE-002" in f for f in scope.check_scope(["README.md"], SLICE)):
        print("FAIL ARV-SCOPE-006: the DECLARED file README.md was itself refused — the "
              "boundary over-refuses; the sibling-prefix refusal below would be vacuous")
        return
    # the SIBLING PREFIX: README.md.unrelated must refuse — a raw-startswith
    # regression matches it and the guard goes silent (the broken guard KB-05)
    scope.check_scope(["README.md.unrelated"], SLICE)


@case("KB-CLM-006", "a claim ID present in BOTH the open and closed tables (registry drift)",
      "ARV-CLM-006")
def kb_clm_dup(copy: pathlib.Path) -> None:
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
