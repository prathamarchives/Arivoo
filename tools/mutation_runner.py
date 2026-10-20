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
DEFAULT_CASE_TIMEOUT = 120             # seconds, per case (wall clock)
SKIP_DIRS = {".git", "__pycache__", ".pg"}  # .pg: gitignored local rig dir — never corpus
POSIX = os.name == "posix"

BOUNDARY = (
    "residual boundary: child processes run on the same host with the same OS user as "
    "this runner — NOT OS-level sandboxing; a hostile child could in principle kill the "
    "judge (the run turns RED, never green); the workflow-definition trust boundary is "
    "H-01b-CI's item; Q10 remains owner-gated. Claims made: no candidate code ran in "
    "this interpreter; every case ran in a fresh disposable fixture; integrity was "
    "re-verified before every case; the manifest records what actually happened."
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
    data = path.read_bytes()
    return data[:cap].decode("utf-8", "replace"), len(data) > cap


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
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
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
            total += st.st_size
            if total > TOTAL_BUDGET:
                raise FloorRefusal(
                    "ARV-FLOOR-004",
                    "corpus budget exceeded (total cap 192 MiB) — no path is printed by design",
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
            entries.append({
                "rel": full.relative_to(root).as_posix(),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "_abs": full,
            })
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


def _rlimit_preexec() -> None:  # pragma: no cover — runs in the forked child
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (CHILD_FSIZE, CHILD_FSIZE))
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_AS, CHILD_AS))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run_child(fixture: Path, tmpdir: Path, case_timeout: int):
    """Execute the CANDIDATE verifier as a child over the disposable fixture.
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
        try:
            r = subprocess.run(
                cmd, cwd=fixture, stdout=fo, stderr=fe, env=env,
                timeout=case_timeout, preexec_fn=preexec, check=False,
            )
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = None
    out, out_tr = _read_capped(out_f)
    err, err_tr = _read_capped(err_f)
    return rc, out, err, (out_tr or err_tr)


def evaluate_case(expect: str, rc, out: str, err: str, truncated: bool):
    """The per-case protocol: a catch requires ALL of — nonzero exit, the
    expected code's FAIL line, the completion count-line, no traceback."""
    if rc is None:
        return False, (
            "child exceeded the case timeout — killed; an unbounded wait is never a catch (ARV-FLOOR-003)"
        ), "ARV-FLOOR-003"
    blob = out + "\n" + err
    if "Traceback (most recent call last)" in blob:
        return False, (
            "child crashed with a traceback — an ordinary exception is not a named refusal "
            "(ARV-FLOOR-003; the predecessor's any-exception acceptance removed)"
        ), "ARV-FLOOR-003"
    caught_line = re.search(rf"^{re.escape(expect)}\s+FAIL\b", out, re.M)
    completion = COMPLETION_RE.search(out)
    if rc != 0 and caught_line and completion:
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
