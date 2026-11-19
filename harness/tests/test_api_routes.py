#!/usr/bin/env python3
"""harness/tests/test_api_routes.py — CLAIM-094: the kernel-backed route suite.

Drives harness/api/routes_selfcheck.py as a subprocess (the venv's third-party
imports — fastapi/cryptography — live in the pinned venv; the suite itself
stays third-party-free). The battery's checks cover the §11.2 sources area:
the import write (the idem key law, ARV-CAP-007, the honest ack, the replay,
the 409 conflict) + the reads (the bounded page, the detail, the isolation
law, the 404 no-leak class) + the auth guard on every route.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILS: list[str] = []


def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)


def main() -> int:
    venv = REPO / ".venv-waved/bin/python"
    if venv.exists():
        r = subprocess.run([str(venv), "-I",
                            str(REPO / "harness/api/routes_selfcheck.py")],
                           capture_output=True, text=True, timeout=600)
        out = r.stdout
    else:
        # the venv-less host: the battery cannot run (fastapi/cryptography);
        # CI's harness-suites job exercises the same battery through its own
        # provisioning — this suite degrades honestly (the 093 lesson)
        print("NOTE: no pinned venv on this host — the route battery rides the venv")
        out = ""
    for code in ("ARV-API-001", "ARV-API-002", "ARV-API-003", "ARV-API-004",
                 "ARV-API-005", "ARV-API-006", "ARV-API-007", "ARV-API-008",
                 "ARV-API-009", "ARV-API-010", "ARV-API-011", "ARV-API-012",
                 "ARV-API-013", "ARV-API-014"):
        check(code, f"PASS {code}:" in out, f"the kernel-backed route check {code}",
              "run harness/api/routes_selfcheck.py in the pinned venv")
    print()
    if FAILS:
        print("RED — the api routes suite refuses:", ", ".join(FAILS))
        return 1
    print("GREEN — the api routes suite passes (the §11.2 sources area over the kernel)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
