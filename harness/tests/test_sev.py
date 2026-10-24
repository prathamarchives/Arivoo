#!/usr/bin/env python3
"""harness/tests/test_sev.py — H-02 part 1: the SEV validator's focused suite (RED-first).

The card (PLAN 'H-02'; LAW-30/D-037; the turn-21 requirements INT-126/D-040 —
the A09 repairs at this boundary). Named codes frozen BEFORE the
implementation (the diagnostics contract):

  ARV-SEV-001  the SEV report is MISSING for a slice (fail-closed; a silent
               pass is the exact hole the card exists to close)
  ARV-SEV-002  MALFORMED: unparseable JSON; wrong schema_version; a missing or
               mistyped required field; a digest that is not full 64-hex —
               prose is not SHA-256 (the A09 repair)
  ARV-SEV-003  STALE: base_sha != the observed merge-base, or the recomputed
               reviewed-diff digest differs — changed code after review;
               candidate movement. (Base-SIDE additions do not move the
               merge-base; the strict=true required-status binding forces
               up-to-date branches at merge, so base movement forces a new
               head and revalidation — stated, never claimed closed.)
  ARV-SEV-004  missing or unresolvable TRACE: empty intent_ids/requirement_ids;
               an INT id absent from the ledger; a SYS id absent from PLAN.md;
               a proof_id binding no existing record; an empty v_model wing
  ARV-SEV-005  false-PASS: disposition BLOCKED, or PASS carrying any OPEN P0/P1
  ARV-SEV-006  placeholder limitations (whitespace / 'none' / 'n/a' instead
               of an explicit honest statement — the A09 repair)
  ARV-SEV-007  the same declared builder/reviewer context where policy
               disallows (the identity LIMIT stated: a differing string is
               not cryptographic independence — fresh-context execution and
               the separate grader remain the protocol)
  ARV-SEV-008  malformed proof/run records (the A09 schema: mistyped fields,
               prose digests, a binding commit git cannot show)

RED state at the predecessor (no harness/sev.py): every case reports the
module ABSENT and the suite exits 1 (red-01.txt) — the target refusals
unprovable, never silently green. The spec-load pattern (module BY PATH, never
the cached one) is the KB registry's own form: no import-time crash, a clean
per-case refusal.

The validator's PUBLIC surface exercised here (never an internal duplicate):
  validate_report(slice_name, base_ref, repo=None) -> list[str]   (codes; [] = valid)
  reviewed_diff_sha256(base_ref, slice_name, repo=None) -> str     (the binding digest)
  reviewed_paths(base_ref, slice_name, repo=None) -> list[str]
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILED = []

SLICE = "claim-900-fixture-slice"
BASE_REF = "main"

LEDGER = "# INTENT-LEDGER — fixture\n\n- **INT-100** — fixture entry one-liner.\n"
LEDGER += "\n**INT-100 — FIXTURE (TURN 1): A FIXTURE ENTRY — active (fixture)**\n> \"fixture owner words\"\n\nSource: owner turn 1, fixture chat (session record 90 fixture; fixture class).\n"
PLAN = "# PLAN — fixture\n\n| SYS | property | claims |\n|-----|----------|--------|\n| SYS-11 | Each implementation slice closes a V-model trace and has independent systems-engineering verification before merge. | C1-C5 |\n"
SRC_A = "print('a')\n"
SRC_B = "print('b')\n"


def _load_sev(repo_dir: pathlib.Path):
    """Spec-load harness/sev.py BY PATH from repo_dir (None when absent — the RED form)."""
    path = pathlib.Path(repo_dir) / "harness" / "sev.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("sev_probe_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo: pathlib.Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)


def build_fixture(tmp: str, commit_run_records: bool = True) -> pathlib.Path:
    """A real git fixture: main (base) + a slice branch with a diff, a run dir
    with a VALID run record + red evidence, and a valid sev.json written by the
    caller. Returns the fixture root."""
    root = pathlib.Path(tmp) / "fixture"
    root.mkdir(parents=True)
    (root / "harness").mkdir()
    (root / "INTENT-LEDGER.md").write_text(LEDGER, encoding="utf-8")
    (root / "PLAN.md").write_text(PLAN, encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text(SRC_A, encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "fixture@test.local"],
                ["config", "user.name", "fixture"], ["checkout", "-q", "-b", "main"],
                ["add", "-A"], ["commit", "-q", "-m", "base"]):
        _git(root, *cmd)
    _git(root, "checkout", "-q", "-b", SLICE)
    (root / "src" / "a.py").write_text(SRC_A + "print('changed')\n", encoding="utf-8")
    (root / "src" / "b.py").write_text(SRC_B, encoding="utf-8")
    rdir = root / "harness" / "runs" / SLICE
    rdir.mkdir(parents=True)
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    if commit_run_records:
        rec = {"command": "python3 harness/tests/test_fixture.py", "exit_code": 0,
               "commit": head, "output_sha256": "0" * 64,
               "recorded_at": "2026-10-24T00:00:00+00:00"}
        (rdir / "run-01.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    (rdir / "red-01.txt").write_text("the fixture's observed red\n", encoding="utf-8")
    (rdir / "notverified.txt").write_text("the fixture's honest limit\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "slice content")
    return root


def merge_base(root: pathlib.Path) -> str:
    return _git(root, "merge-base", BASE_REF, "HEAD").stdout.strip()


def valid_report(sev, root: pathlib.Path) -> dict:
    """A COMPLETE, valid report for the fixture (digests derived from the module
    itself — the positive self-consistency form)."""
    return {
        "schema_version": 1,
        "slice_id": SLICE,
        "base_sha": merge_base(root),
        "reviewed_diff_sha256": sev.reviewed_diff_sha256(BASE_REF, SLICE, repo=root),
        "intent_ids": ["INT-100"],
        "requirement_ids": ["SYS-11"],
        "system_claims": ["C1"],
        "changed_components": ["harness/sev.py"],
        "interfaces_reviewed": ["validate_report(slice, base, repo) — this suite"],
        "v_model": {
            "component_verification": ["the field set validated by this suite, proof run-01"],
            "integration_verification": ["the real git boundary, proof red-01.txt"],
            "system_verification": ["SYS-11 trace, proof run-01"],
            "validation": ["the refusal matrix observed green, proof run-01"],
        },
        "failure_modes": [
            {"id": "FM-01", "scenario": "a stale report binds reviewed code",
             "control": "the recomputed digest refuses (ARV-SEV-003)", "proof_ids": ["run-01"]},
        ],
        "findings": [],
        "not_verified": ["the fixture boundary: identity separation is stated, never cryptographic"],
        "builder_context": "builder-fixture-ctx",
        "reviewer_context": "reviewer-fixture-ctx",
        "disposition": "PASS",
        "review_summary": "fixture report: every field present and resolvable",
    }


def write_report(root: pathlib.Path, report: dict) -> None:
    p = root / "harness" / "runs" / SLICE / "sev.json"
    p.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def expect_codes(sev, root, want: str, name: str, detail: str = "") -> None:
    got = sev.validate_report(SLICE, BASE_REF, repo=root)
    ok = want in got if want else got == []
    tag = "PASS" if ok else "FAIL"
    print(f"{tag} {name}: expected {want or '[]'}; got {got} {detail}")
    if not ok:
        FAILED.append(name)


def run_all(tmp):
        sev = _load_sev(REPO)
        if sev is None:
            for n in ("positive", "missing", "malformed", "stale", "trace", "falsepass",
                      "placeholder", "identity", "runrecords", "digest"):
                print(f"FAIL {n}: harness/sev.py is ABSENT — the target refusals are unprovable (the RED form)")
                FAILED.append(n)
            return

        # --- the positive path (a complete report validates) ---
        root = build_fixture(tmp + "/pos")
        write_report(root, valid_report(sev, root))
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "report")
        expect_codes(sev, root, None, "positive")

        # --- ARV-SEV-001: missing ---
        root = build_fixture(tmp + "/missing")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "no report")
        expect_codes(sev, root, "ARV-SEV-001", "missing")

        # --- ARV-SEV-002: malformed (unparseable / schema / missing field / prose digest) ---
        for name, mutate in (
            ("malformed-json", lambda r, p: p.write_text("{not json", encoding="utf-8")),
            ("malformed-schema", lambda r, p: p.write_text(json.dumps({**r, "schema_version": 0}), encoding="utf-8")),
            ("malformed-missing-field", lambda r, p: p.write_text(json.dumps({k: v for k, v in r.items() if k != "review_summary"}), encoding="utf-8")),
            ("malformed-prose-digest", lambda r, p: p.write_text(json.dumps({**r, "reviewed_diff_sha256": "the diff, honestly reviewed"}), encoding="utf-8")),
            ("malformed-typed-field", lambda r, p: p.write_text(json.dumps({**r, "intent_ids": "INT-100 (a string, not a list)"}), encoding="utf-8")),
        ):
            root = build_fixture(tmp + "/" + name)
            p = root / "harness" / "runs" / SLICE / "sev.json"
            mutate(valid_report(sev, root), p)
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", name)
            expect_codes(sev, root, "ARV-SEV-002", "malformed", f"({name})")

        # --- ARV-SEV-003: stale (base moved under the report; code changed after review) ---
        root = build_fixture(tmp + "/stale-base")
        report = valid_report(sev, root)
        _git(root, "checkout", "-q", "main")
        (root / "src" / "a.py").write_text(SRC_A + "# base moved\n", encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "base side moves")
        _git(root, "checkout", "-q", SLICE)
        _git(root, "merge", "-q", "--no-edit", "main")
        write_report(root, report)  # the report still names the OLD merge-base
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "stale base")
        expect_codes(sev, root, "ARV-SEV-003", "stale", "(base movement)")

        root = build_fixture(tmp + "/stale-code")
        write_report(root, valid_report(sev, root))
        (root / "src" / "a.py").write_text(SRC_A + "print('changed after review')\n", encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "code changed after review")
        expect_codes(sev, root, "ARV-SEV-003", "stale", "(changed code after review)")

        # --- ARV-SEV-004: trace (empty ids; unresolvable INT/SYS; dangling proof; empty wing) ---
        for name, mutate in (
            ("trace-no-intent", lambda r: {**r, "intent_ids": []}),
            ("trace-unknown-intent", lambda r: {**r, "intent_ids": ["INT-777"]}),
            ("trace-no-req", lambda r: {**r, "requirement_ids": []}),
            ("trace-unknown-req", lambda r: {**r, "requirement_ids": ["SYS-99"]}),
            ("trace-dangling-proof", lambda r: {**r, "failure_modes": [{**r["failure_modes"][0], "proof_ids": ["run-99"]}]}),
            ("trace-empty-wing", lambda r: {**r, "v_model": {**r["v_model"], "system_verification": []}}),
        ):
            root = build_fixture(tmp + "/" + name)
            write_report(root, mutate(valid_report(sev, root)))
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", name)
            expect_codes(sev, root, "ARV-SEV-004", "trace", f"({name})")

        # --- ARV-SEV-005: false-PASS (BLOCKED; open P0; open P1; resolved P2 stays valid) ---
        open_p0 = [{"id": "SEV-1", "severity": "P0", "status": "open", "evidence": "e", "disposition": "d"}]
        open_p1 = [{"id": "SEV-1", "severity": "P1", "status": "open", "evidence": "e", "disposition": "d"}]
        resolved_p2 = [{"id": "SEV-2", "severity": "P2", "status": "resolved", "evidence": "e", "disposition": "fixed in fixture"}]
        for name, mutate in (
            ("falsepass-blocked", lambda r: {**r, "disposition": "BLOCKED"}),
            ("falsepass-open-p0", lambda r: {**r, "findings": open_p0}),
            ("falsepass-open-p1", lambda r: {**r, "findings": open_p1}),
        ):
            root = build_fixture(tmp + "/" + name)
            write_report(root, mutate(valid_report(sev, root)))
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", name)
            expect_codes(sev, root, "ARV-SEV-005", "falsepass", f"({name})")
        root = build_fixture(tmp + "/resolved-p2")
        write_report(root, {**valid_report(sev, root), "findings": resolved_p2})
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "resolved p2")
        expect_codes(sev, root, None, "falsepass", "(resolved P2 under PASS stays valid)")

        # --- ARV-SEV-006: placeholder limitations ---
        for name, mutate in (
            ("placeholder-none", lambda r: {**r, "not_verified": ["none"]}),
            ("placeholder-space", lambda r: {**r, "not_verified": ["   "]}),
            ("placeholder-na", lambda r: {**r, "not_verified": ["N/A"]}),
        ):
            root = build_fixture(tmp + "/" + name)
            write_report(root, mutate(valid_report(sev, root)))
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", name)
            expect_codes(sev, root, "ARV-SEV-006", "placeholder", f"({name})")

        # --- ARV-SEV-007: the same declared builder/reviewer ---
        root = build_fixture(tmp + "/identity")
        write_report(root, {**valid_report(sev, root), "builder_context": "same-ctx", "reviewer_context": "same-ctx"})
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "identity")
        expect_codes(sev, root, "ARV-SEV-007", "identity")

        # --- ARV-SEV-008: malformed proof/run records ---
        for name, rec in (
            ("rr-prose-digest", {"command": "x", "exit_code": 0, "commit": "0" * 40, "output_sha256": "sha of output (prose)", "recorded_at": "2026-10-24T00:00:00+00:00"}),
            ("rr-string-exit", {"command": "x", "exit_code": "0", "commit": "0" * 40, "output_sha256": "0" * 64, "recorded_at": "2026-10-24T00:00:00+00:00"}),
            ("rr-missing-key", {"command": "x", "exit_code": 0, "commit": "0" * 40, "output_sha256": "0" * 64}),
            ("rr-short-digest", {"command": "x", "exit_code": 0, "commit": "0" * 40, "output_sha256": "0" * 16, "recorded_at": "2026-10-24T00:00:00+00:00"}),
        ):
            root = build_fixture(tmp + "/" + name)
            write_report(root, valid_report(sev, root))
            (root / "harness" / "runs" / SLICE / "run-01.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", name)
            expect_codes(sev, root, "ARV-SEV-008", "runrecords", f"({name})")
        # a binding commit git cannot show (the KB-RED-011 form — the fixture repo lacks it)
        root = build_fixture(tmp + "/rr-ghost-commit")
        write_report(root, valid_report(sev, root))
        rec = json.loads((root / "harness" / "runs" / SLICE / "run-01.json").read_text())
        rec["commit"] = "f" * 40
        (root / "harness" / "runs" / SLICE / "run-01.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "ghost commit")
        expect_codes(sev, root, "ARV-SEV-008", "runrecords", "(a commit git cannot show)")

        # --- the digest procedure (the binding itself) ---
        root = build_fixture(tmp + "/digest")
        paths = sev.reviewed_paths(BASE_REF, SLICE, repo=root)
        if any(str(p).startswith(f"harness/runs/{SLICE}") for p in paths):
            print(f"FAIL digest: the slice's own run-dir paths leaked into the reviewed set: {paths}")
            FAILED.append("digest")
        elif not any("src" in str(p) for p in paths):
            print(f"FAIL digest: the changed source files are missing from the reviewed set: {paths}")
            FAILED.append("digest")
        else:
            print(f"PASS digest: the reviewed set excludes the slice's own artifacts and carries the code ({len(paths)} paths)")

        # the #75 CodeRabbit round 1, case (1): a NON-ASCII path must bind by its
        # EXACT bytes — the C-quoted form made git show fail and the file hashed
        # as deleted, blinding the staleness check for exactly such files
        root = build_fixture(tmp + "/digest-nonascii")
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / "caf\u00e9.py").write_text("print('nonascii')\n", encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "nonascii path")
        paths = sev.reviewed_paths(BASE_REF, SLICE, repo=root)
        if not any("caf\u00e9" in str(p) for p in paths):
            print(f"FAIL digest-nonascii: the non-ASCII path did not bind into the reviewed set: {paths}")
            FAILED.append("digest-nonascii")
        else:
            d1 = sev.reviewed_diff_sha256(BASE_REF, SLICE, repo=root)
            (root / "src" / "caf\u00e9.py").write_text("print('nonascii CHANGED after review')\n", encoding="utf-8")
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "nonascii changed")
            d2 = sev.reviewed_diff_sha256(BASE_REF, SLICE, repo=root)
            if d1 == d2:
                print("FAIL digest-nonascii: an edit to the non-ASCII file left the digest UNCHANGED — the staleness blind spot")
                FAILED.append("digest-nonascii")
            else:
                print("PASS digest-nonascii: the non-ASCII path binds by exact bytes and its edit moves the digest")

        # the #75 round 1, case (2): a non-UTF-8 report is a NAMED refusal, never a traceback
        root = build_fixture(tmp + "/report-bytes")
        (root / "harness" / "runs" / SLICE / "sev.json").write_bytes(b"\xff\xfe{not utf8}")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "non-utf8 report")
        expect_codes(sev, root, "ARV-SEV-002", "malformed", "(non-UTF-8 bytes: a named refusal, never a crash)")

        # the #75 round 1, case (3): a non-object failure-mode entry — a named 004, never a crash
        root = build_fixture(tmp + "/fm-string")
        write_report(root, valid_report(sev, root))
        rep = json.loads((root / "harness" / "runs" / SLICE / "sev.json").read_text())
        rep["failure_modes"] = ["just a string, not an object"]
        (root / "harness" / "runs" / SLICE / "sev.json").write_text(json.dumps(rep), encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "fm string")
        expect_codes(sev, root, "ARV-SEV-004", "trace", "(a non-object failure mode)")

        # the #75 round 1, case (4): a non-40-hex commit string is a false binding
        for name, commit in (("rr-commit-head", "HEAD"), ("rr-commit-empty", ""), ("rr-commit-prose", "the commit where it ran")):
            root = build_fixture(tmp + "/" + name)
            write_report(root, valid_report(sev, root))
            rec = json.loads((root / "harness" / "runs" / SLICE / "run-01.json").read_text())
            rec["commit"] = commit
            (root / "harness" / "runs" / SLICE / "run-01.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
            _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", name)
            expect_codes(sev, root, "ARV-SEV-008", "runrecords", f"({name})")

        # the #75 round 1, case (5): an EMPTY not-verified list — empty-by-omission
        root = build_fixture(tmp + "/placeholder-empty")
        write_report(root, {**valid_report(sev, root), "not_verified": []})
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "empty not_verified")
        expect_codes(sev, root, "ARV-SEV-006", "placeholder", "(the empty list)")

        # the #76 reviewer round, SEV-2: a NON-ITERABLE proof_ids is a named 004,
        # never an uncaught TypeError at the gate boundary (the named-disposition
        # contract; observed live by the fresh-context reviewer: the wired gate
        # crashed with a traceback instead of a code)
        root = build_fixture(tmp + "/pids-int")
        write_report(root, valid_report(sev, root))
        rep = json.loads((root / "harness" / "runs" / SLICE / "sev.json").read_text())
        rep["failure_modes"] = [{**rep["failure_modes"][0], "proof_ids": 5}]
        (root / "harness" / "runs" / SLICE / "sev.json").write_text(json.dumps(rep), encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "pids int")
        expect_codes(sev, root, "ARV-SEV-004", "trace", "(a non-iterable proof_ids — a named refusal, never a crash)")

        # the #76 reviewer round, SEV-4: the report must name THE SLICE under
        # judgment — a transplant from a byte-identical sibling refuses
        root = build_fixture(tmp + "/slice-id-mismatch")
        write_report(root, valid_report(sev, root))
        rep = json.loads((root / "harness" / "runs" / SLICE / "sev.json").read_text())
        rep["slice_id"] = "claim-999-some-other-slice"
        (root / "harness" / "runs" / SLICE / "sev.json").write_text(json.dumps(rep), encoding="utf-8")
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "slice id mismatch")
        expect_codes(sev, root, "ARV-SEV-002", "malformed", "(the report names another slice — the transplant refuses)")

        # the #75 round 2: an UNKNOWN disposition cannot represent a valid
        # result — and it previously carried an OPEN P1 past every check
        root = build_fixture(tmp + "/disposition-unknown")
        write_report(root, {**valid_report(sev, root), "disposition": "UNVERIFIED",
                            "findings": [{"id": "SEV-1", "severity": "P1", "status": "open", "evidence": "e", "disposition": "d"}]})
        _git(root, "add", "-A"); _git(root, "commit", "-q", "-m", "unknown disposition")
        expect_codes(sev, root, "ARV-SEV-005", "falsepass", "(unknown disposition + open P1 — the exact carried-past hole)")

        # the #75 round 2: rename detection emitted ONLY the destination — the
        # deleted source vanished from the reviewed set (worst case: a rename
        # INTO the excluded run dir made the whole change invisible). The
        # renamed file must EXIST AT THE MERGE-BASE (src/a.py — created in the
        # fixture's base commit), or base-side cancellation erases the rename
        # from the diff entirely (the case's own first-draft error: renaming a
        # file the slice itself had added).
        root = build_fixture(tmp + "/digest-rename")
        _git(root, "mv", "src/a.py", "src/renamed.py")
        # a PURE rename (R100): the destination carries the BASE content — the
        # case's own second-draft fix: the fixture's slice-commit content drift
        # on src/a.py kept similarity below git's 50% threshold, so no rename
        # was detected and the pre-fix form PASSED vacuously (the suppression
        # never fired). Identical content forces the R100 form.
        (root / "src" / "renamed.py").write_text(SRC_A, encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "rename a -> renamed")
        paths = sev.reviewed_paths(BASE_REF, SLICE, repo=root)
        if "src/a.py" not in paths or "src/renamed.py" not in paths:
            print(f"FAIL digest-rename: the rename endpoints did not both bind: {paths}")
            FAILED.append("digest-rename")
        else:
            print("PASS digest-rename: both rename endpoints bind (the deleted source + the new destination)")
        # the worst case: a rename INTO the slice's own run dir — the destination
        # stays excluded, but the DELETED SOURCE must still bind
        _git(root, "mv", "src/renamed.py", f"harness/runs/{SLICE}/renamed.py")
        _git(root, "commit", "-q", "-m", "rename into the run dir")
        paths = sev.reviewed_paths(BASE_REF, SLICE, repo=root)
        if "src/a.py" not in paths or f"harness/runs/{SLICE}/renamed.py" in [str(p) for p in paths]:
            print(f"FAIL digest-rename-run: the deleted source lost or the run-dir destination leaked: {paths}")
            FAILED.append("digest-rename-run")
        else:
            print("PASS digest-rename-run: the run-dir destination excluded; the deleted source still binds")


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="sev-fixture-")
    try:
        run_all(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print()
    if FAILED:
        print(f"RED — {len(FAILED)} failing case(s): {', '.join(FAILED)}")
        print("      the SEV validator must refuse its named classes (ARV-SEV-001..008)")
        return 1
    print("GREEN — the SEV validator's refusal matrix holds: every named code discriminated "
          "(missing/malformed/stale/trace/false-PASS/placeholder/identity/run-records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
