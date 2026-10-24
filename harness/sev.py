#!/usr/bin/env python3
"""harness/sev.py — H-02: the Systems Engineering Verification validator (LAW-30).

PLAN card H-02 (part 1, CLAIM-040): the standard-library validator for the
separately authored SEV record (the form: context/TEMPLATES.md §6). The gate
wiring, the KB-SEV matrix, the dispatch/trusted integration, and the activation
updates land in the part-2 slice (CLAIM-041); until then this module is
exercised by its focused suite and labeled not-mechanically-enforced (the
card's own transition label).

The digest procedure (the card's binding contract): the report binds to the
REVIEWED DIFF — the changed files' content at HEAD, computed over
merge-base(base_ref)...HEAD, EXCLUDING only the slice's own generated /
self-referential artifacts (harness/runs/<slice>/ — the SEV file, the Proof
Sheet, the run records: evidence ABOUT the review, never code under review).
Code under review is NEVER excluded. Base movement is stale through the
merge-base field; candidate movement through the content digest. Base-SIDE
additions do not move a merge-base — the strict=true required-status binding
forces up-to-date branches at merge, so a moved base forces a new head and
revalidation (stated residual, never claimed closed).

Named codes (frozen in harness/tests/test_sev.py BEFORE this implementation):
  ARV-SEV-001  the report is MISSING (fail-closed; a silent pass is the hole)
  ARV-SEV-002  MALFORMED: unparseable JSON / wrong schema_version / a missing
               or mistyped required field / a digest that is not full 64-hex
               (prose is not SHA-256 — the A09 repair)
  ARV-SEV-003  STALE: base_sha != the observed merge-base, or the recomputed
               reviewed-diff digest differs (changed code after review)
  ARV-SEV-004  missing or unresolvable TRACE: empty intent_ids /
               requirement_ids; an INT absent from INTENT-LEDGER.md; a SYS
               absent from PLAN.md; a proof_id binding no existing record; an
               empty v_model wing
  ARV-SEV-005  false-PASS: disposition BLOCKED, or PASS carrying any OPEN P0/P1
  ARV-SEV-006  placeholder limitations (whitespace / 'none' / 'n/a' instead of
               an explicit honest statement — the A09 repair)
  ARV-SEV-007  the same declared builder/reviewer context (the identity LIMIT
               stated: a differing string is not cryptographic independence;
               fresh-context execution and the separate grader remain the
               protocol — PLAN H-02's independence-limit paragraph)
  ARV-SEV-008  malformed proof/run records (the A09 schema: mistyped fields,
               prose digests, a binding commit git cannot show — the
               KB-RED-011 class)

Malformed HISTORICAL records are preserved as historical artifacts with a
disposition, never forged replacements (A09): this validator only ever
REFUSES; it never rewrites a record it finds.

Public surface (the KB cases and the gate call THESE — never an internal
duplicate):
  validate_report(slice_name, base_ref, repo=None) -> list[str]   codes; [] = valid
  check_sev(slice_name, base_ref, repo=None) -> list[str]         the printing gate wrapper
  reviewed_paths(base_ref, slice_name, repo=None) -> list[str]
  reviewed_diff_sha256(base_ref, slice_name, repo=None) -> str
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess

SCHEMA_VERSION = 1
SEV_FILENAME = "sev.json"
DELETED_TOKEN = "(deleted at HEAD)"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
INT_ID = re.compile(r"^INT-(\d{3})$")
SYS_ID = re.compile(r"^SYS-(\d{2})$")
SYSTEM_CLAIMS = {"C1", "C2", "C3", "C4", "C5"}
DISPOSITIONS = ("PASS", "BLOCKED")
SEVERITIES = ("P0", "P1", "P2")
FINDING_STATUSES = ("open", "resolved", "owner-accepted-debt")
PLACEHOLDERS = {"", "none", "n/a", "na", "-", "--", "tbd", "todo", "(none)",
                "none stated", "nothing", "n.a."}

# TEMPLATES.md §6's required fields -> the exact JSON types (A09: typed, never prose)
REQUIRED_FIELDS = {
    "schema_version": int, "slice_id": str, "base_sha": str,
    "reviewed_diff_sha256": str, "intent_ids": list, "requirement_ids": list,
    "system_claims": list, "changed_components": list, "interfaces_reviewed": list,
    "v_model": dict, "failure_modes": list, "findings": list, "not_verified": list,
    "builder_context": str, "reviewer_context": str, "disposition": str,
    "review_summary": str,
}
V_MODEL_KEYS = ("component_verification", "integration_verification",
                "system_verification", "validation")
RUN_RECORD_FIELDS = {
    "command": str, "exit_code": int, "commit": str,
    "output_sha256": str, "recorded_at": str,
}


def _repo_root() -> pathlib.Path:
    """H-01b-CI's pattern: ARV_TRUSTED_ROOT re-roots this machinery onto the
    candidate tree when the trusted driver has validated it (absolute existing
    dir only; anything else keeps the natural root)."""
    root = os.environ.get("ARV_TRUSTED_ROOT", "")
    p = pathlib.Path(root) if root else None
    if p is not None and p.is_absolute() and p.is_dir():
        return p
    return pathlib.Path(__file__).resolve().parents[1]


REPO = _repo_root()


def _git(repo: pathlib.Path, *args, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          timeout=timeout)


def _fail(codes: list, code: str, what: str, repair: str) -> None:
    print(f"FAIL {code}: {what}")
    print(f"      repair: {repair}")
    codes.append(code)


def merge_base_of(base_ref: str, repo: pathlib.Path) -> "str | None":
    """The observed merge-base, or None when the git context cannot answer
    (a named refusal belongs to the caller's diff machinery — ARV-DIFF-002's
    class — this validator then refuses the report as stale, never guesses)."""
    r = _git(repo, "merge-base", base_ref, "HEAD")
    return r.stdout.decode("utf-8", "replace").strip() if r.returncode == 0 else None


def reviewed_paths(base_ref: str, slice_name: str, repo=None) -> list:
    """The reviewed set: every path changed in merge-base(base_ref)...HEAD,
    EXCLUDING only the slice's own harness/runs/<slice>/ artifacts (generated +
    self-referential evidence). Code under review is never excluded."""
    repo = pathlib.Path(repo) if repo else REPO
    # -z: NUL-separated RAW bytes — a path carrying non-ASCII, quotes, tabs, or
    # backslashes never arrives in git's C-quoted form, so the digest binds the
    # exact path (the R-04(5) class; the #75 CodeRabbit round 1: a quoted path
    # made git show fail and the file silently hashed as deleted — an edit to it
    # left the digest UNCHANGED, blinding the staleness check)
    # --no-renames: rename detection would emit ONLY the destination — the
    # deleted SOURCE path vanished from the reviewed set entirely (the #75
    # round 2: a rename INTO the excluded run dir made the whole change
    # invisible). With renames off, BOTH endpoints always bind: the deleted
    # source digests its deletion token, the destination its content, and the
    # run-dir prefix still excludes only the slice's own artifacts.
    r = _git(repo, "diff", "-z", "--name-only", "--no-renames", f"{base_ref}...HEAD")
    if r.returncode != 0:
        return []
    prefix = f"harness/runs/{slice_name}/"
    out = []
    for raw in r.stdout.split(b"\x00"):
        if not raw:
            continue
        p = os.fsdecode(raw)  # surrogateescape round-trips through subprocess args
        if not (p == prefix.rstrip("/") or p.startswith(prefix)):
            out.append(p)
    return sorted(out)


def reviewed_diff_sha256(base_ref: str, slice_name: str, repo=None) -> str:
    """The binding digest: sha256 over 'path  <sha256-of-HEAD-content>' lines,
    sorted. A deleted path digests its DELETED_TOKEN (the deletion IS the
    reviewed state). The slice's own run-dir artifacts are excluded above —
    including this module's own reports — so adding a report never changes
    its own binding (the card's anti-self-referentiality contract)."""
    repo = pathlib.Path(repo) if repo else REPO
    parts = []
    for p in reviewed_paths(base_ref, slice_name, repo):
        r = _git(repo, "show", f"HEAD:{p}")
        if r.returncode == 0:
            content_sha = hashlib.sha256(r.stdout).hexdigest()
        else:
            content_sha = DELETED_TOKEN
        parts.append(f"{p}  {content_sha}")
    return hashlib.sha256("\n".join(parts).encode("utf-8", "surrogateescape")).hexdigest()


def _check_run_records(repo: pathlib.Path, slice_name: str, codes: list) -> list:
    """ARV-SEV-008 (the A09 schema): every run record carries the typed fields;
    digests are FULL 64-hex (prose is not SHA-256); the binding commit is one
    git can show (the KB-RED-011 class — a nonexistent commit is a false claim)."""
    rdir = repo / "harness" / "runs" / slice_name
    names = sorted(p.name for p in rdir.glob("run-*.json"))
    for name in names:
        path = rdir / name
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
            _fail(codes, "ARV-SEV-008", f"run record {name} is unparseable ({e})",
                  "a malformed record is preserved as a historical artifact with a disposition, never forged — repair forward in a new record")
            continue
        if not isinstance(rec, dict):
            _fail(codes, "ARV-SEV-008", f"run record {name} is not a JSON object",
                  "the typed schema is required — a non-object record is a malformed shape, never a crash (A01/A09)")
            continue
        for key, typ in RUN_RECORD_FIELDS.items():
            if key not in rec or not isinstance(rec[key], typ) or isinstance(rec[key], bool) and typ is int:
                _fail(codes, "ARV-SEV-008",
                      f"run record {name}: field '{key}' is missing or mistyped (expected {typ.__name__})",
                      "the typed schema is required — a prose field is not evidence (A09)")
        if not HEX64.match(str(rec.get("output_sha256", ""))):
            _fail(codes, "ARV-SEV-008", f"run record {name}: output_sha256 is not full 64-hex",
                  "prose is not SHA-256 — the digest syntax is validated (A09)")
        commit = str(rec.get("commit", ""))
        # A09: each record is BOUND to a revision — '(unrecorded)' is the
        # proofsheet's own honest degraded form; a 40-hex id must be one git can
        # show; ANY other string (empty, 'HEAD', 'abc123', prose) is a false
        # binding and refuses (the #75 round 1: non-hex strings skipped the
        # check entirely)
        if commit == "(unrecorded)":
            pass  # the honest degraded form — stated, never fabricated
        elif re.fullmatch(r"[0-9a-f]{40}", commit):
            if _git(repo, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
                _fail(codes, "ARV-SEV-008", f"run record {name}: binding commit {commit[:12]} does not exist in git history",
                      "git's inability to show the commit IS the refusal — a nonexistent binding is a false claim (the KB-RED-011 class)")
        else:
            _fail(codes, "ARV-SEV-008", f"run record {name}: the commit field {commit[:20]!r} is neither '(unrecorded)' nor a 40-hex id",
                  "a binding that names no revision is a false claim (A09) — repair the record forward, never forge it")
    return names


def validate_report(slice_name: str, base_ref: str, repo=None) -> list:
    """The PUBLIC validator. Returns the failing codes (empty = valid); the
    gate wrapper below prints them. Every refusal names its code — a missing,
    stale, malformed, incomplete, or BLOCKED report never passes (LAW-30)."""
    repo = pathlib.Path(repo) if repo else REPO
    codes: list = []
    path = repo / "harness" / "runs" / slice_name / SEV_FILENAME
    if not path.is_file():
        _fail(codes, "ARV-SEV-001", f"no SEV report at {SEV_FILENAME} for slice '{slice_name}'",
              "every slice carries a separately authored systems-engineering verification (LAW-30/TEMPLATES §6) — a silent pass is the hole")
        return codes
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        # a non-UTF-8 report is a MALFORMED shape (the #75 round 1): a named
        # refusal, never an uncaught traceback (A01's contract)
        _fail(codes, "ARV-SEV-002", f"the SEV report is unparseable ({e})",
              "a malformed record is preserved as a historical artifact, never forged — repair forward in a new report")
        return codes
    if not isinstance(report, dict):
        _fail(codes, "ARV-SEV-002", "the SEV report is not a JSON object", "the TEMPLATES §6 schema is required")
        return codes
    if report.get("schema_version") != SCHEMA_VERSION:
        _fail(codes, "ARV-SEV-002", f"schema_version {report.get('schema_version')!r} != {SCHEMA_VERSION}",
              "the record schema is versioned; a future schema needs a deliberate migration, never a silent read")
    for key, typ in REQUIRED_FIELDS.items():
        if key not in report:
            _fail(codes, "ARV-SEV-002", f"required field '{key}' is missing", "the TEMPLATES §6 schema is required (LAW-30)")
        elif not isinstance(report[key], typ) or (isinstance(report[key], bool) and typ is int):
            _fail(codes, "ARV-SEV-002", f"field '{key}' is mistyped (expected {typ.__name__})", "typed fields — never prose (A09)")
    if codes:
        return codes  # shape first: nothing below can trust the fields

    # SEV-4 (#76's reviewer round): the report must name THE SLICE under
    # judgment — the run-dir path is not the only binding; a transplant from a
    # sibling must refuse, never ride the judged label
    if report["slice_id"] != slice_name:
        _fail(codes, "ARV-SEV-002", f"slice_id {report['slice_id']!r} does not name the slice under judgment ({slice_name!r})",
              "the report is bound to its slice by ID as well as by path (TEMPLATES §6: slice_id is a required identity field)")

    # CLAIM-042: the OPTIONAL sheet_section field (the Proof-Sheet SEV
    # section's opt-in transition switch, TEMPLATES §6) is TYPED: the field
    # controls the committed sheet's format, so a mistyped value must be a
    # NAMED refusal, never a silent default (A09's typed-fields rule — the
    # #76 CodeRabbit round's mistyped-fields class, closed for the switch)
    if "sheet_section" in report and not isinstance(report["sheet_section"], bool):
        _fail(codes, "ARV-SEV-002", "the optional field 'sheet_section' is mistyped (expected bool)",
              "the field is the Proof-Sheet SEV section's opt-in switch (TEMPLATES §6) — typed fields, never prose (A09)")

    # ARV-SEV-003: staleness — base + candidate movement
    observed_base = merge_base_of(base_ref, repo)
    if observed_base is None:
        _fail(codes, "ARV-SEV-003", "the merge-base is not decidable — the report's base binding cannot be verified",
              "an undecidable git context is a refusal, never a guess (ARV-DIFF-002's class)")
    elif report["base_sha"] != observed_base:
        _fail(codes, "ARV-SEV-003",
              f"base_sha {report['base_sha'][:12]} != the observed merge-base {observed_base[:12]} — the base moved under the report",
              "rebase/update and re-author the report against the new base (no stale SEV reuse)")
    actual_digest = reviewed_diff_sha256(base_ref, slice_name, repo)
    if report["reviewed_diff_sha256"] != actual_digest:
        _fail(codes, "ARV-SEV-003",
              "reviewed_diff_sha256 does not match the recomputed digest — the reviewed code changed after the report",
              "re-run the review over the current diff and re-author the report (LAW-30: stale evidence means STOP)")

    # ARV-SEV-002 (the digest syntax — prose is not SHA-256)
    if not HEX64.match(report["reviewed_diff_sha256"]):
        _fail(codes, "ARV-SEV-002", "reviewed_diff_sha256 is not full 64-hex", "prose is not a digest (A09)")
    if not re.fullmatch(r"[0-9a-f]{40}", report["base_sha"]):
        _fail(codes, "ARV-SEV-002", "base_sha is not a full 40-hex commit id", "prose is not a revision id (A09)")

    # ARV-SEV-004: the trace — intent, requirements, evidence, v_model
    ledger = (repo / "INTENT-LEDGER.md").read_text(encoding="utf-8", errors="replace") \
        if (repo / "INTENT-LEDGER.md").is_file() else ""
    plan = (repo / "PLAN.md").read_text(encoding="utf-8", errors="replace") \
        if (repo / "PLAN.md").is_file() else ""
    if not report["intent_ids"]:
        _fail(codes, "ARV-SEV-004", "intent_ids is empty", "a slice with no owner intent behind it fails the audit (LOOP-05)")
    for iid in report["intent_ids"]:
        if not INT_ID.match(str(iid)) or f"**INT-{iid.split('-')[-1]}" not in ledger:
            _fail(codes, "ARV-SEV-004", f"intent id {iid!r} does not resolve in INTENT-LEDGER.md",
                  "every trace names a real ledger entry — a fabricated authority pointer is the exact false-green class")
    if not report["requirement_ids"]:
        _fail(codes, "ARV-SEV-004", "requirement_ids is empty", "every slice traces its system requirement(s) (SYS-11 at minimum)")
    for sid in report["requirement_ids"]:
        if not SYS_ID.match(str(sid)) or f"| {sid} " not in plan:
            _fail(codes, "ARV-SEV-004", f"requirement id {sid!r} does not resolve in PLAN.md",
                  "the RTM is the single canonical home — trace to a real SYS row")
    for claim in report["system_claims"]:
        if str(claim) not in SYSTEM_CLAIMS:
            _fail(codes, "ARV-SEV-004", f"system claim {claim!r} is not one of C1..C5", "the claim ladder is C1..C5 (GLOSSARY)")
    vm = report["v_model"]
    for wing in V_MODEL_KEYS:
        if not isinstance(vm.get(wing), list) or not vm.get(wing):
            _fail(codes, "ARV-SEV-004", f"the v_model wing '{wing}' is empty",
                  "the V-model trace is four-wing complete (component/integration/system/validation)")
    rdir = repo / "harness" / "runs" / slice_name
    existing = {p.name for p in rdir.iterdir()}
    # a proof id binds by exact filename OR its stem ('run-01' == 'run-01.json')
    existing |= {n[: -len(".json")] if n.endswith(".json") else n for n in existing}
    for fm in report["failure_modes"]:
        if not isinstance(fm, dict):
            _fail(codes, "ARV-SEV-004", "a failure mode entry is not a JSON object",
                  "the TEMPLATES §6 shape is required — a malformed entry is a named refusal, never a crash")
            continue
        for key in ("id", "scenario", "control"):
            if not str(fm.get(key, "")).strip():
                _fail(codes, "ARV-SEV-004", f"failure mode {fm.get('id')!r}: '{key}' is empty", "each failure mode carries id/scenario/control/proof_ids (TEMPLATES §6)")
        _pids = fm.get("proof_ids", [])
        if not isinstance(_pids, list):
            _fail(codes, "ARV-SEV-004", f"failure mode {fm.get('id')!r}: proof_ids is not a list",
                  "the TEMPLATES §6 shape is required — a non-iterable proof binding is a named refusal, never an uncaught TypeError (the gate's named-disposition contract)")
            continue
        for pid in _pids:
            if str(pid) not in existing and not str(pid).startswith("ci-"):
                _fail(codes, "ARV-SEV-004", f"proof id {pid!r} binds no existing record in the slice's run dir",
                      "evidence binds to records that exist — a dangling proof pointer is a fabricated-evidence class")

    # ARV-SEV-005: the disposition class — BLOCKED, or a false PASS, or a
    # value that cannot represent a valid result at all (the #75 round 2: an
    # unknown disposition like 'UNVERIFIED' passed every check while carrying
    # an OPEN P1 — the P0/P1 guard fired only under an exact PASS string)
    if report["disposition"] not in DISPOSITIONS:
        _fail(codes, "ARV-SEV-005", f"the disposition {report['disposition']!r} is not PASS|BLOCKED — a value that cannot represent a valid result",
              "the frozen result vocabulary is PASS and BLOCKED (TEMPLATES §6); every other value refuses")
    elif report["disposition"] == "BLOCKED":
        _fail(codes, "ARV-SEV-005", "the report is BLOCKED", "a blocked review blocks the slice (LAW-30) — resolve the blocker or split the slice")
    for f in report["findings"]:
        if not isinstance(f, dict):
            _fail(codes, "ARV-SEV-005", "a finding entry is not a JSON object",
                  "the findings schema is required — a malformed entry is a named refusal, never a crash")
            continue
        if f.get("severity") not in SEVERITIES:
            _fail(codes, "ARV-SEV-005", f"finding {f.get('id')!r}: severity {f.get('severity')!r} is not P0|P1|P2", "the severities are frozen")
        if f.get("status") not in FINDING_STATUSES:
            _fail(codes, "ARV-SEV-005", f"finding {f.get('id')!r}: status {f.get('status')!r} is not open|resolved|owner-accepted-debt", "the statuses are frozen")
        if f.get("severity") in ("P0", "P1") and f.get("status") == "open" and report["disposition"] == "PASS":
            _fail(codes, "ARV-SEV-005", f"PASS carries the OPEN {f.get('severity')} finding {f.get('id')!r}",
                  "an unresolved P0/P1 fails the slice — resolve it or mark the report BLOCKED (never a false PASS)")

    # ARV-SEV-006: placeholder limitations — an EMPTY list declares no honest
    # limitation at all, the exact "empty-by-omission" form LAW-04 forbids
    if not report["not_verified"]:
        _fail(codes, "ARV-SEV-006", "not_verified is EMPTY — no limitation declared at all",
              "LAW-04 requires an explicit honest statement; the empty list is empty-by-omission (the #75 round 1)")
    for entry in report["not_verified"]:
        if str(entry).strip().lower() in PLACEHOLDERS or len(str(entry).strip()) < 8:
            _fail(codes, "ARV-SEV-006", f"the not-verified entry {entry!r} is a placeholder",
                  "an explicit honest statement is required (LAW-04/A09) — whitespace and 'none' are not limitations")

    # ARV-SEV-007: the declared identity (its LIMIT stated in the module docstring)
    if str(report["builder_context"]).strip() == str(report["reviewer_context"]).strip():
        _fail(codes, "ARV-SEV-007", "builder_context == reviewer_context — the same declared context where policy disallows",
              "the SEV is separately authored; a differing string is still not cryptographic independence (state the limit)")

    # ARV-SEV-008: the proof/run records' own schema (A09)
    _check_run_records(repo, slice_name, codes)
    return codes


def check_sev(slice_name: str, base_ref: str, repo=None) -> list:
    """The gate-side wrapper: invokes the PUBLIC validator (never an internal
    duplicate) and returns its codes (each already printed with its repair)."""
    return validate_report(slice_name, base_ref, repo)


if __name__ == "__main__":
    import sys
    bad = check_sev(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "origin/main")
    print()
    if bad:
        print(f"RED — the SEV report is refused: {', '.join(sorted(set(bad)))}")
        sys.exit(1)
    print("GREEN — the SEV report validates (LAW-30's mechanical form holds)")
