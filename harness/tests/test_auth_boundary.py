#!/usr/bin/env python3
"""harness/tests/test_auth_boundary.py — CLAIM-092: the auth boundary + the
health routes (runbook §8.3/§8.4 + §11.5).

RED-first: before this slice, harness/api/ had no application code at all —
the module imports failed (the waiting-for-harness class; recorded under that
protocol).

The suite drives the ASGI interface directly (httpx is deliberately NOT a
dependency — the repo's own stdlib driver below calls the app as an ASGI
callable). The ES256 positive/negative battery:
  * the positive chain: sign with a test key -> the pinned JWK -> verify ->
    derive the owner from the VERIFIED sub
  * six refusal classes: wrong issuer, wrong audience, expired, HS256
    alg-confusion (the retired signing mode), wrong key/unknown kid, tampered
  * the /api/v1/me route: the dependency wiring (401 without a token; the
    named code in the JSON error body)
  * the health routes: liveness (200 always) + readiness (503 until the
    service declares ready; 200 when it does) + the centralized error shape
    (the named code + api_version, never a stack trace)
"""
import asyncio
import base64
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []

def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)


def main() -> int:
    # the ES256 battery runs in the pinned venv (cryptography is an approved
    # dep in harness/api/; THIS file stays third-party-free: the battery is
    # driven as a subprocess — the pgprod_selfcheck pattern)
    r = subprocess.run(
        [str(REPO / ".venv-waved/bin/python"), "-I",
         str(REPO / "harness/api/auth_selfcheck.py")],
        capture_output=True, text=True, timeout=180)
    out = r.stdout
    for code in ("ARV-AUTH-010", "ARV-AUTH-011", "ARV-AUTH-012",
                 "ARV-AUTH-013", "ARV-AUTH-014", "ARV-AUTH-015",
                 "ARV-AUTH-016", "ARV-AUTH-017"):
        check(code, f"PASS {code}:" in out, f"the ES256 battery's {code}",
              "run harness/api/auth_selfcheck.py in the pinned venv")
    check("ARV-AUTH-018", "GREEN —" in out and r.returncode == 0,
          "the auth battery exits GREEN", "the battery must pass in the venv")

    # the app routes: driven through the raw ASGI interface (stdlib only)
    r2 = subprocess.run(
        [str(REPO / ".venv-waved/bin/python"), "-I",
         str(REPO / "harness/api/routes_selfcheck.py")],
        capture_output=True, text=True, timeout=180)
    out2 = r2.stdout
    for code, what in (("ARV-ROUTE-001", "liveness answers 200 with no dependencies"),
                       ("ARV-ROUTE-002", "readiness is 503 until the service declares ready"),
                       ("ARV-ROUTE-003", "readiness is 200 once declared ready (auth + db state honest)"),
                       ("ARV-ROUTE-004", "an unauthenticated product route is 401 ARV-AUTH-001"),
                       ("ARV-ROUTE-005", "the error body carries the named code + api_version, never a stack trace"),
                       ("ARV-ROUTE-006", "a verified token reaches /api/v1/me and derives the owner from the sub"),
                       ("ARV-ROUTE-007", "the OpenAPI document exists at /api/v1/openapi.json (generated from the code)")):
        check(code, f"PASS {code}:" in out2, what, "run harness/api/routes_selfcheck.py")
    check("ARV-ROUTE-008", "GREEN —" in out2 and r2.returncode == 0,
          "the routes battery exits GREEN", "the routes battery must pass")

    print()
    if FAILS:
        print("RED — the auth boundary suite refuses:", ", ".join(FAILS))
        return 1
    print("GREEN — the auth boundary suite passes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
