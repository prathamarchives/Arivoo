#!/usr/bin/env python3
"""harness/tests/test_runtime_lock.py — the runtime dependency lock contract.

The Dockerfile installs `pip install -r harness/api/requirements.lock`; a lock
that is a prose document rather than a pip-parseable requirements file breaks
the image build. This stdlib-only suite proves:

  * ARV-LOCK-001  every non-comment, non-blank line is a pinned requirement
                  with at least one sha256 --hash (the LAW-08 approval record
                  stays as COMMENTS, never as pip input)
  * ARV-LOCK-002  the approved minimum set is pinned (D-047 §3.2)
  * ARV-LOCK-003  no unpinned/duplicate requirement

No third-party imports (LAW-08); the actual install is exercised by the
image build in the slice's run records.
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
LOCK = REPO / "harness" / "api" / "requirements.lock"
FAILS: list[str] = []
_LINE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*==[0-9][A-Za-z0-9.+_-]*( --hash=sha256:[0-9a-f]{64})+$")
_REQUIRED = ("fastapi", "starlette", "uvicorn", "psycopg", "psycopg-binary",
             "psycopg-pool", "pyjwt")


def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)


def main() -> int:
    lines = LOCK.read_text(encoding="utf-8").splitlines() if LOCK.is_file() else []
    effective = [(i + 1, ln) for i, ln in enumerate(lines)
                 if ln.strip() and not ln.lstrip().startswith("#")]
    bad = [(n, ln[:80]) for n, ln in effective if not _LINE.match(ln)]
    check("ARV-LOCK-001", not bad,
          f"every effective line ({len(effective)}) is a pinned requirement with sha256 hashes",
          f"comment out the prose ({bad[:2]}) and use 'name==version --hash=sha256:<digest>' lines")
    pins = {}
    for _, ln in effective:
        name = ln.split("==", 1)[0]
        pins[name] = pins.get(name, 0) + 1
    check("ARV-LOCK-002", all(p in pins for p in _REQUIRED),
          "the approved minimum set is pinned",
          "pin fastapi/starlette/uvicorn/psycopg/psycopg-binary/psycopg-pool/pyjwt")
    check("ARV-LOCK-003", not bad and all(v == 1 for v in pins.values()),
          "no unpinned or duplicate requirement",
          "one pinned line per requirement; hashes on every line")
    print()
    if FAILS:
        print(f"RED — the runtime lock is not pip-installable: {len(FAILS)} check(s) failed.")
        return 1
    print(f"GREEN — the runtime lock is pip-installable ({len(effective)} pinned requirements).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
