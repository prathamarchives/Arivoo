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

SLICE = "known-bad-probe"  # the scratch slice the probe declaration lives under

# (id, description, expected code, probe(copy_dir) -> None)
CASES = []


def case(cid, desc, code):
    def reg(fn):
        CASES.append((cid, desc, code, fn))
        return fn
    return reg


def _load(copy: pathlib.Path, name: str):
    """Load a module BY FILE PATH from the mutated copy (never the cached one)."""
    path = copy / (name.replace(".", "/") + ".py")
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
