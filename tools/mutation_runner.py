#!/usr/bin/env python3
"""mutation_runner.py — the H-01b trusted child-process runner + manifest contract.

Base-owned machinery for judging a CANDIDATE verifier over known-bad corpus
mutations (PLAN card H-01b, A03 — the card's named runner module). The entry
module (tools/verify_selftest.py) owns the mutation registry and the CLI, and
delegates here; the runner never imports candidate code — stdlib only, loaded
by path (works under `python3 -I`). Named codes ARV-FLOOR-001..006 are frozen
in harness/tests/test_mutation_floor.py; the residual boundary (same-host
same-user children are NOT OS sandboxing; a killed judge is RED, never green;
H-01b-CI owns the workflow boundary; Q10 owner-gated) is stated in every run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat as statmod
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

PER_FILE_BUDGET = 8 * 1024 * 1024      # per corpus file
TOTAL_BUDGET = 192 * 1024 * 1024       # whole corpus
COUNT_BUDGET = 5000
READ_CAP = 1024 * 1024                 # child stdout/stderr read-back cap
CHILD_FSIZE = 8 * 1024 * 1024          # child per-file write cap
CHILD_AS = 512 * 1024 * 1024           # child address-space cap
CHILD_NPROC = 256                      # child process-count cap (RLIMIT_NPROC; the whole-UID form is why the value sits well above a runner's baseline)
DEFAULT_CASE_TIMEOUT = 120             # seconds, per case (wall clock)
SKIP_DIRS = {".git", "__pycache__", ".pg"}  # .pg: gitignored local rig dir — never corpus
POSIX = os.name == "posix"

BOUNDARY = (
    "residual boundary: child processes run on the same host with the same OS user as "
    "this runner — NOT OS-level sandboxing; a hostile child could in principle kill the "
    "judge (the run turns RED, never green); the workflow-definition trust boundary is "
    "H-01b-CI's item; Q10 remains owner-gated. Claims made: no candidate code ran in "
    "this interpreter; every case ran in a fresh disposable fixture; integrity was "
    "re-verified before every case AND after the last case; the manifest records "
    "what actually happened. FLOOR-REVIEW-1 sharpening (session 23): the manifest "
    "artifact is a RECORD, not a tamper-proof store — a surviving same-user daemon "
    "can overwrite it after the run (CI consumes exit codes). R-02 sharpening "
    "(session 24): every case runs in its own process group and is killed with it "
    "on every outcome + RLIMIT_NPROC bounds the child — a daemon that RE-SESSIONS "
    "itself (setsid/double-fork outside the killed group) remains a stated residual, "
    "as does any environmental difference a candidate can probe beyond the seeded "
    ".git channel — stated and never claimed closed"
)

COMPLETION_RE = re.compile(
    r"canonicalization-layer verifier\s+[—-]\s+\d+\s+checks?,\s+\d+\s+failures?", re.I
)


class FloorRefusal(Exception):
    """A named, sanitized refusal. The message NEVER carries a corpus path
    (F-012 class: secret-shaped filenames must not leak into diagnostics)."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _read_capped(path: Path, cap: int = READ_CAP) -> tuple[str, bool]:
    """FLOOR-REVIEW-1 B3 (session 23): bounded, race-resistant read-back. The
    child WRITES these files, but a same-user child can also unlink/swap them
    after it exits — at the predecessor an unbounded read_bytes() HUNG the
    judge on a FIFO swap and read a 200 MB swapped file whole. O_NONBLOCK |
    O_NOFOLLOW + open-fd ISREG: a symlink swap is refused, a FIFO/device swap
    is refused without blocking on the open, and the read is a single capped
    pass. A refused read-back counts as truncated-EMPTY output — fail-closed:
    a case whose evidence cannot be read can only fail, never pass."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    except OSError:
        return "", True
    try:
        if not statmod.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file")
        with os.fdopen(fd, "rb") as fh:
            data = fh.read(cap + 1)
        return data[:cap].decode("utf-8", "replace"), len(data) > cap
    except OSError:
        try:
            os.close(fd)
        except OSError:
            pass
        return "", True


def _open_regular_nofollow(path: Path):
    """Race-resistant open: symlinks/non-regular entries are refused (O_NOFOLLOW)."""
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        if not statmod.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file")
    except Exception:
        os.close(fd)
        raise
    return fd


def enumerate_corpus(root: Path) -> list[dict]:
    """The bounded, no-dereference corpus enumeration: every regular file under
    `root` (minus the documented skips), each within budget, race-resistant.
    Refuses (ARV-FLOOR-004) on non-regular entries or budget breaches — the
    message is static: no path is ever printed."""
    entries: list[dict] = []
    total = 0
    nonreg = 0
    walk_errors: list[OSError] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False,
                                                 onerror=walk_errors.append):
        # R-02 (CR-47-2/G-47-6, session 24): a walk error (an unreadable
        # directory, for example) used to be silently skipped — its files
        # vanished from the corpus/digest/fixture with no refusal. Walk
        # errors count as refused entries: the enumeration fails closed.
        kept = []
        for d in sorted(dirnames):
            if d in SKIP_DIRS:
                continue
            if (Path(dirpath) / d).is_symlink():
                nonreg += 1          # a symlinked directory is never traversed
                continue
            kept.append(d)
        dirnames[:] = kept
        for fn in sorted(filenames):
            if fn in SKIP_DIRS:
                continue          # R-02 (G-52-2): .git may be a FILE (worktree/submodule shape) — never corpus
            full = Path(dirpath) / fn
            try:
                st = full.lstat()
            except OSError:
                nonreg += 1
                continue
            if not statmod.S_ISREG(st.st_mode):
                nonreg += 1
                continue
            if st.st_size > PER_FILE_BUDGET:
                raise FloorRefusal(
                    "ARV-FLOOR-004",
                    "corpus budget exceeded (per-file cap 8 MiB) — the entry's path is not printed by design",
                )
            if len(entries) >= COUNT_BUDGET:
                raise FloorRefusal(
                    "ARV-FLOOR-004",
                    "corpus budget exceeded (file-count cap 5000) — no path is printed by design",
                )
            try:
                fd = _open_regular_nofollow(full)
                with os.fdopen(fd, "rb") as fh:
                    data = fh.read(PER_FILE_BUDGET + 1)
            except OSError:
                nonreg += 1   # raced into a symlink swap — refused, never dereferenced
                continue
            if len(data) > PER_FILE_BUDGET:
                raise FloorRefusal(
                    "ARV-FLOOR-004",
                    "corpus budget exceeded (per-file cap 8 MiB at read time) — no path is printed by design",
                )
            # R-02 (G-47-7, session 24): the total budget is charged against the
            # bytes ACTUALLY READ, never the pre-read st_size — a file that grew
            # between lstat and read used to slip its real size past the cap.
            total += len(data)
            if total > TOTAL_BUDGET:
                raise FloorRefusal(
                    "ARV-FLOOR-004",
                    "corpus budget exceeded (total cap 192 MiB, charged on bytes read) — no path is printed by design",
                )
            entries.append({
                "rel": full.relative_to(root).as_posix(),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "_abs": full,
            })
    nonreg += len(walk_errors)   # R-02: every unreadable directory is a refused entry — fail closed
    if nonreg:
        raise FloorRefusal(
            "ARV-FLOOR-004",
            f"{nonreg} non-regular corpus entr(ies) refused — symlinks/devices/fifos/sockets are never dereferenced or copied; no path is printed by design",
        )
    return entries


def corpus_digest(entries: list[dict]) -> str:
    h = hashlib.sha256()
    for e in sorted(entries, key=lambda x: x["rel"]):
        h.update(e["rel"].encode("utf-8")); h.update(b"\0")
        h.update(str(e["size"]).encode("ascii")); h.update(b"\0")
        h.update(e["sha256"].encode("ascii")); h.update(b"\n")
    return h.hexdigest()


def build_fixture(entries: list[dict], dest: Path) -> None:
    """Copy the enumerated (already verified) files into a fresh fixture. A
    source that changed under the run refuses (ARV-FLOOR-002)."""
    dest.mkdir(parents=True, exist_ok=True)
    for e in entries:
        out = dest / e["rel"]
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = _open_regular_nofollow(e["_abs"])
            with os.fdopen(fd, "rb") as fh:
                data = fh.read(PER_FILE_BUDGET + 1)
        except OSError as exc:
            raise FloorRefusal(
                "ARV-FLOOR-002",
                f"the corpus source changed under the run (a fixture read failed: {type(exc).__name__}) — refusing to judge mutated input",
            ) from None
        if hashlib.sha256(data).hexdigest() != e["sha256"] or len(data) != e["size"]:
            raise FloorRefusal(
                "ARV-FLOOR-002",
                "the corpus source changed under the run (content digest mismatch during fixture copy) — refusing to judge mutated input",
            )
        out.write_bytes(data)
    # FLOOR-REVIEW-1 B1 (session 23): fixture/checkout CONTEXT UNIFORMITY. The
    # independent review's discriminating verifier (a `.git` probe) passed BOTH
    # sides of the two-sided floor: fixtures had no .git, real checkouts do.
    # The fixture now carries a CONTROLLED .git stub — never the candidate's
    # own .git (SKIP_DIRS keeps that untrusted dir out of the corpus and it is
    # never copied). A context probe that answers "real checkout" in CI now
    # answers the same inside the fixture, so the per-case protocol observes
    # the candidate's actual behavior. Any OTHER environmental-difference
    # channel remains a stated residual (BOUNDARY carries it, never claimed).
    gitdir = dest / ".git"
    (gitdir / "objects").mkdir(parents=True, exist_ok=True)
    (gitdir / "refs").mkdir(exist_ok=True)
    (gitdir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (gitdir / "config").write_text("[core]\n\trepositoryformatversion = 0\n", encoding="utf-8")


def _rlimit_preexec() -> None:  # pragma: no cover — runs in the forked child
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (CHILD_FSIZE, CHILD_FSIZE))
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_AS, CHILD_AS))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    # R-02 (CR-47-3, session 24): bound the child's process count. Linux's
    # RLIMIT_NPROC is enforced against the whole real UID's process count at
    # fork time, so the cap must sit well above a runner's legitimate baseline
    # while still killing fork bombs in their first milliseconds.
    resource.setrlimit(resource.RLIMIT_NPROC, (CHILD_NPROC, CHILD_NPROC))


def run_child(fixture: Path, tmpdir: Path, case_timeout: int):
    """Execute the CANDIDATE verifier as a child over the disposable fixture.
    R-02 (CR-47-3/G-47-8, session 24): the child runs in its OWN session /
    process group, and the group is killed on EVERY case outcome (normal exit,
    failure, timeout) — a worker the verifier spawned used to outlive its case
    and could write into later fixtures after the integrity re-verification.
    Returns (returncode|None, stdout, stderr, truncated)."""
    verifier = fixture / "tools" / "verify_canonical_layer.py"
    try:
        st = verifier.lstat()
    except OSError:
        raise FloorRefusal(
            "ARV-FLOOR-005",
            "the candidate verifier is missing from the corpus — a case without it is refused (fail-closed, never a silent skip)",
        ) from None
    if not statmod.S_ISREG(st.st_mode):
        raise FloorRefusal(
            "ARV-FLOOR-004",
            "the candidate verifier is not a regular file — refusing to execute a non-regular entry",
        )
    out_f, err_f = tmpdir / "child.out", tmpdir / "child.err"
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(fixture),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    cmd = [sys.executable, "-B", str(verifier)]
    preexec = _rlimit_preexec if POSIX else None
    with open(out_f, "wb") as fo, open(err_f, "wb") as fe:
        proc = subprocess.Popen(
            cmd, cwd=fixture, stdout=fo, stderr=fe, env=env,
            preexec_fn=preexec, start_new_session=POSIX,
        )
        try:
            rc = proc.wait(timeout=case_timeout)
        except subprocess.TimeoutExpired:
            rc = None
        finally:
            # the WHOLE process group is reaped on every outcome — the direct
            # child AND anything it spawned without re-sessioning itself
            if POSIX:
                import signal
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
            else:
                proc.kill()
            proc.wait()
    out, out_tr = _read_capped(out_f)
    err, err_tr = _read_capped(err_f)
    return rc, out, err, (out_tr or err_tr)


def evaluate_case(expect: str, rc, out: str, err: str, truncated: bool):
    """The per-case protocol: a catch requires ALL of — a positive nonzero
    exit, the expected code's FAIL line, the completion count-line, no
    traceback, and evidence streams that could be read within the cap."""
    if rc is None:
        return False, (
            "child exceeded the case timeout — killed; an unbounded wait is never a catch (ARV-FLOOR-003)"
        ), "ARV-FLOOR-003"
    if truncated:
        # R-02 (G-47-1/G-52-1, session 24): a truncated or refused read-back
        # (a swapped output file, a flood past the cap) used to hide the rest
        # of the evidence stream — stdout alone could prove a "catch" the
        # full stream contradicts. An unreadable evidence stream is never a
        # provable catch, fail-closed.
        return False, (
            "the child's evidence output could not be read within the cap (truncated or refused) — "
            "an unread evidence stream is never a provable catch (ARV-FLOOR-003)"
        ), "ARV-FLOOR-003"
    if rc < 0:
        # R-02 (G-47-2, session 24): a negative return code is a death by
        # signal — the predecessor's `rc != 0` counted the kill as a
        # completed catch. A killed child is not a named-refusal exit.
        return False, (
            f"child died by signal {-rc} — a signal death is not a completed named-refusal exit (ARV-FLOOR-003)"
        ), "ARV-FLOOR-003"
    blob = out + "\n" + err
    if "Traceback (most recent call last)" in blob:
        return False, (
            "child crashed with a traceback — an ordinary exception is not a named refusal "
            "(ARV-FLOOR-003; the predecessor's any-exception acceptance removed)"
        ), "ARV-FLOOR-003"
    caught_line = re.search(rf"^{re.escape(expect)}\s+FAIL\b", out, re.M)
    completion = COMPLETION_RE.search(out)
    if rc > 0 and caught_line and completion:
        return True, "caught", ""
    if rc == 0:
        detail = "with the expected FAIL line printed but exit 0" if caught_line else "without the expected FAIL line and exit 0"
        return False, (
            f"not caught ({detail}) — a vacuous or evasive pass is refused (ARV-FLOOR-001)"
        ), "ARV-FLOOR-001"
    if not caught_line:
        return False, (
            f"exit {rc} but no '{expect} FAIL' line — the expected named refusal is absent (ARV-FLOOR-001)"
        ), "ARV-FLOOR-001"
    if not completion:
        return False, (
            "the expected FAIL line exists but the verifier's completion count-line is absent — "
            "a fabricated or truncated run is not a completed catch (ARV-FLOOR-001)"
        ), "ARV-FLOOR-001"
    return False, "not caught (ARV-FLOOR-001)", "ARV-FLOOR-001"


def validate_manifest(m, expected_codes: list[str]) -> list[str]:
    """The manifest contract: every expected case exactly once, no unknown or
    malformed records, the expected set agrees with the run."""
    fails: list[str] = []
    if not isinstance(m, dict):
        return ["ARV-FLOOR-006: the manifest is not an object"]
    if m.get("schema_version") != 1:
        fails.append("ARV-FLOOR-006: unsupported/missing schema_version (1 required)")
    cases = m.get("cases")
    if not isinstance(cases, list):
        fails.append("ARV-FLOOR-006: the manifest has no case list")
        cases = []
    codes: list = []
    for c in cases:
        if not isinstance(c, dict):
            fails.append("ARV-FLOOR-006: a case record is not an object")
            continue
        if not {"code", "expect", "caught", "disposition"} <= set(c):
            fails.append("ARV-FLOOR-006: a malformed case record (code/expect/caught/disposition required)")
            continue
        # R-02 (G-47-11, session 24): presence was checked, TYPES were not —
        # a record with expect=None and disposition={} used to validate clean.
        if not (isinstance(c.get("code"), str) and isinstance(c.get("expect"), str)
                and isinstance(c.get("disposition"), str)):
            fails.append("ARV-FLOOR-006: a malformed case record (code/expect/disposition must be strings)")
            continue
        if not isinstance(c.get("caught"), bool):
            fails.append("ARV-FLOOR-006: a non-boolean 'caught' field")
            continue
        codes.append(c.get("code"))
        if c.get("code") not in expected_codes:
            fails.append("ARV-FLOOR-006: an unknown case is present (outside the expected set)")
    for want in expected_codes:
        n = codes.count(want)
        if n != 1:
            fails.append(f"ARV-FLOOR-006: expected case {want} appears {n} time(s) — exactly once required")
    if m.get("expected_cases") != list(expected_codes):
        fails.append("ARV-FLOOR-006: the manifest's expected_cases disagrees with the run's expected set")
    return fails

def run_floor(cases: list, cand_root: Path, *, driver_path: Path,
              sibling_module: Path | None = None, floor_base: str | None = None,
              manifest_out: Path | None = None,
              case_timeout: int = DEFAULT_CASE_TIMEOUT) -> int:
    """Execute the floor: every case in a fresh disposable child fixture,
    integrity re-verified before every case, the manifest always written."""
    base = Path(floor_base) if floor_base else Path(os.environ.get("ARV_FLOOR_BASE_TOOLS", ""))
    anchored = bool(floor_base or os.environ.get("ARV_FLOOR_BASE_TOOLS"))
    # the anchored copy carries the _anchored suffix; the BASE original does not —
    # resolve the counterpart name (the post-merge run 39401172275 caught the
    # mismatch: base/verify_selftest_anchored.py does not exist, only the original)
    base_name = driver_path.name
    if base_name.endswith("_anchored.py"):
        base_name = base_name[: -len("_anchored.py")] + ".py"
    if anchored and not (base / base_name).is_file():
        print(f"FAIL ARV-FLOOR-002: the trusted floor anchor is missing ({base}) — refusing to run unanchored")
        return 1
    expected_codes = [m[0] for m in cases]
    driver_sha = hashlib.sha256(driver_path.read_bytes()).hexdigest()
    sibling_sha = hashlib.sha256(sibling_module.read_bytes()).hexdigest() if sibling_module else None
    cand_verifier = cand_root / "tools" / "verify_canonical_layer.py"
    if not cand_verifier.is_file():
        print("FAIL ARV-FLOOR-005: the candidate verifier is missing from the corpus — refusing to run (fail-closed)")
        return 1

    def integrity() -> list[dict]:
        if anchored:
            # FLOOR-REVIEW-1 B4 (session 23): the anchor reads are NAMED
            # refusals — at the predecessor a FileNotFoundError here escaped
            # as a bare exception, swallowed by the finally-return with no
            # code for the anchor loss. Fail-closed WITH the code.
            try:
                driver_bytes = (base / base_name).read_bytes()
            except OSError:
                raise FloorRefusal(
                    "ARV-FLOOR-002",
                    "the trusted base driver became unreadable mid-run — refusing to continue (fail-closed, never a swallowed exception)",
                ) from None
            if hashlib.sha256(driver_bytes).hexdigest() != driver_sha:
                raise FloorRefusal(
                    "ARV-FLOOR-002",
                    "the anchored driver's digest no longer matches the trusted base copy — refusing to continue",
                )
            if sibling_module is not None:
                try:
                    sibling_bytes = (base / sibling_module.name).read_bytes()
                except OSError:
                    raise FloorRefusal(
                        "ARV-FLOOR-002",
                        "the trusted runner module became unreadable mid-run — refusing to continue (fail-closed, never a swallowed exception)",
                    ) from None
                if hashlib.sha256(sibling_bytes).hexdigest() != sibling_sha:
                    raise FloorRefusal(
                        "ARV-FLOOR-002",
                        "the anchored runner module's digest no longer matches the trusted base copy — refusing to continue",
                    )
        current = enumerate_corpus(cand_root)
        if corpus_digest(current) != baseline_digest:
            raise FloorRefusal(
                "ARV-FLOOR-002",
                "the corpus source changed under the run (digest mismatch before a case) — refusing to judge mutated input",
            )
        return current

    temproot_m = tempfile.TemporaryDirectory(prefix="arivoo-floor-")
    temproot = Path(temproot_m.name)
    print(f"floor temp root: {temproot}")
    manifest = {
        "schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "mode": "anchored" if anchored else "local",
        "driver_sha256": driver_sha,
        "runner_sha256": sibling_sha,
        "floor_base": str(base) if anchored else None,
        "candidate_verifier_sha256": hashlib.sha256(cand_verifier.read_bytes()).hexdigest(),
        "candidate_root": str(cand_root),
        "expected_cases": expected_codes,
        "cases": [],
        "verdict": None,
        "boundary": BOUNDARY,
    }
    refusal: FloorRefusal | None = None
    try:
        baseline = enumerate_corpus(cand_root)
        baseline_digest = corpus_digest(baseline)
        manifest["corpus_digest"] = baseline_digest
        manifest["corpus_file_count"] = len(baseline)
        print(f"known-bad self-test — {len(cases)} mutations, each must FAIL its named check (child-process floor)\n")
        for code, desc, mutate, expect in cases:
            current = integrity()          # ARV-FLOOR-002 — before EVERY case
            with tempfile.TemporaryDirectory(dir=temproot, prefix="case-") as cd:
                casedir = Path(cd)
                fixture = casedir / "repo"
                build_fixture(current, fixture)
                try:
                    mutate(fixture)
                except Exception as exc:
                    manifest["cases"].append({
                        "code": code, "expect": expect, "caught": False,
                        "disposition": f"the mutation could not be applied to the fixture ({type(exc).__name__}) — the case cannot be proven caught (ARV-FLOOR-001)",
                    })
                    print(f"{code} FAIL  {desc} → mutation application failed — the case cannot be proven caught (ARV-FLOOR-001)")
                    continue
                rc, out, err, trunc = run_child(fixture, casedir, case_timeout)
                caught, disposition, _fcode = evaluate_case(expect, rc, out, err, trunc)
                manifest["cases"].append({
                    "code": code, "expect": expect, "caught": caught,
                    "disposition": disposition, "child_exit": rc,
                    "output_truncated": bool(trunc),
                })
                if caught:
                    print(f"{code} PASS  {desc} → {expect} FAILed as required")
                else:
                    print(f"{code} FAIL  {desc} → {disposition}")
        # R-02 (G-48-2, session 24): the integrity recheck AFTER the final
        # case. integrity() ran only BEFORE each case, so a mutation of the
        # source corpus during the LAST case (or a --only single-case run)
        # was never re-checked — the run stayed GREEN on a tampered tree.
        integrity()               # ARV-FLOOR-002 — after the LAST case too
    except FloorRefusal as fr:
        refusal = fr
        print(f"FAIL {fr.code}: {fr.message}")
    finally:
        mval_fails = list(validate_manifest(manifest, expected_codes))
        # R-02 (G-48-3, session 24): a failed manifest WRITE used to print a
        # warning while the verdict stayed GREEN and the driver exited 0 —
        # the run's evidence was never recorded, yet it passed. The record's
        # OWN validation/verdict keys are assigned BEFORE serialization; a
        # write/serialize failure IS a validation failure, and the run can
        # only be RED. The failure line PRINTS its named code.
        mpath = Path(manifest_out) if manifest_out else temproot.parent / f"arv-floor-manifest-{manifest['run_id'][:8]}.json"
        caught_n = sum(1 for c in manifest["cases"] if c.get("caught"))
        manifest["manifest_validation_failures"] = mval_fails
        manifest["verdict"] = "REFUSED" if refusal else ("RED" if (caught_n != len(expected_codes) or mval_fails) else "GREEN")
        manifest_write_ok = True
        try:
            mpath.parent.mkdir(parents=True, exist_ok=True)
            mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except (OSError, TypeError, ValueError):
            manifest_write_ok = False
            mval_fails.append("ARV-FLOOR-006: the manifest could not be written — the run's evidence is not recorded, refusing GREEN")
            manifest["manifest_validation_failures"] = mval_fails
            manifest["verdict"] = "REFUSED" if refusal else "RED"
            try:
                mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            except Exception:
                pass          # best-effort: an unwritable target writes nothing — the failure line below carries the code
        if manifest_write_ok:
            print(f"floor manifest: {mpath}")
        else:
            print("floor manifest: <write FAILED — ARV-FLOOR-006: the run is RED; an unwritten evidence record is never a pass>")
        print()
        if manifest["verdict"] == "GREEN":
            print(f"SELF-TEST GREEN — {caught_n}/{len(expected_codes)} known-bad mutations caught by their named checks.")
            print("The guards are themselves tested (KB-01..06 spirit, document-level; each case ran in a disposable child process).")
        else:
            codes = set()
            for c in manifest["cases"]:
                d = c.get("disposition", "")
                if "(ARV-" in d:
                    codes.add(d.split("(ARV-")[1].split(")")[0])
            for f in mval_fails:
                if f.startswith("ARV-"):
                    codes.add(f.split(":")[0].split("ARV-")[1])
            if refusal:
                codes.add(refusal.code)
            print(f"SELF-TEST RED — verdict {manifest['verdict']}: {len(expected_codes) - caught_n} case failure(s) + {len(mval_fails)} manifest failure(s); codes: {sorted(codes)}")
        print(f"{BOUNDARY}")
        rc = 0 if manifest["verdict"] == "GREEN" else 1
        temproot_m.cleanup()
        return rc
