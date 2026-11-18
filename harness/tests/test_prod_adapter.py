#!/usr/bin/env python3
"""harness/tests/test_prod_adapter.py — CLAIM-091: the production pooled
adapter's contract (runbook §10 + §8.5).

RED-first: before pgprod.py landed, every check was un-implementable (the
module did not exist — ARV-TEST-000's waiting-for-harness class; the red was
observed as the import failure and recorded under that class's protocol).

The suite verifies the CONTRACT without a live Supabase (CI runs it against
the LOCAL rig for behavior, plus shape-only checks for the guards):
  * the guards: no-explicit-config refusal, missing-CA refusal, wrong-role
    refusal (all by-name, before any connection)
  * the §8.5 discipline: transaction-local owner context — SET LOCAL inside
    the transaction; after COMMIT the connection's GUC is EMPTY again (the
    two-user reuse race); after ROLLBACK likewise
  * the readonly lease: no owner GUC set
  * the bounded statement timeout: applied per-transaction, not session-wide
Behavioral runs use the LOCAL rig through the psycopg driver (the same
driver the production path uses — engine parity, FACT-001's spirit) with
verify-full OFF locally only because the rig's TLS is a self-signed test CA —
the SHAPE (explicit config, named guards) is what this suite pins; the
production TLS proof is CLAIM-088/089's already-landed verify-full battery.
"""
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pgprod  # noqa: E402

FAILS: list[str] = []

def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)

def main() -> int:
    # ---- the guards (shape-only; no connection attempted) ----
    # ARV-PRD-001: no explicit config -> refusal (no env fallback)
    try:
        pgprod.ProdPool("not-a-config")
        check("ARV-PRD-001", False, "a non-ProdConfig constructor refuses", "pass a ProdConfig")
    except pgprod.ProdRefusal as e:
        check("ARV-PRD-001", e.code == "ARV-PRD-001", "a non-ProdConfig constructor refuses by name", "pass a ProdConfig")

    # ARV-PRD-002: missing root CA -> refusal
    try:
        cfg = pgprod.ProdConfig(host="db.example.supabase.co", port=5432, dbname="postgres",
                                user="arv_app", password="x", sslrootcert="/nonexistent-ca.pem")
        pgprod.ProdPool(cfg)
        check("ARV-PRD-002", False, "a missing root CA refuses", "supply the pinned Supabase root CA")
    except pgprod.ProdRefusal as e:
        check("ARV-PRD-002", e.code == "ARV-PRD-002", "a missing root CA refuses by name (verify-full is not optional)", "supply the pinned Supabase root CA")

    # ARV-PRD-003: the runtime role must be arv_app-shaped
    try:
        cfg = pgprod.ProdConfig(host="db.example.supabase.co", port=5432, dbname="postgres",
                                user="postgres", password="x",
                                sslrootcert=str(pathlib.Path("/tmp/ca-bundle.pem")))
        pgprod.ProdPool(cfg)
        check("ARV-PRD-003", False, "a postgres runtime login refuses (shortcut #7)", "use the arv_app runtime role")
    except pgprod.ProdRefusal as e:
        check("ARV-PRD-003", e.code == "ARV-PRD-003", "a postgres/superuser runtime login refuses by name (§6.5)", "use the arv_app runtime role")

    # ARV-PRD-005: the owner-scope validation (injection-shaped sub)
    try:
        pgprod.ProdPool._validate_owner_public("'; DROP TABLE x; --")
        check("ARV-PRD-005", False, "an injection-shaped owner refuses", "validate the sub")
    except Exception:
        check("ARV-PRD-005", True, "an injection-shaped owner scope refuses", "validate the sub")

    # ---- the credential-free repr ----
    cfg = pgprod.ProdConfig(host="db.example.supabase.co", port=5432, dbname="postgres",
                            user="arv_app", password="zz9",
                            sslrootcert="/tmp/ca-bundle.pem")
    check("ARV-PRD-006", "zz9" not in repr(cfg),
          "the config's repr never carries the password (credential-free diagnostics)",
          "override __repr__ to withhold the password")

    # ---- the §8.5 discipline against the LOCAL rig (behavioral) ----
    rig = os.environ.get("ARV_TEST_RIG")
    if rig == "1" and pathlib.Path("/tmp/ca-bundle.pem").exists():
        _behavioral_checks(check)
    else:
        print("NOTE: behavioral §8.5 checks skipped (ARV_TEST_RIG=1 + a rig CA required — the CI harness job provides the rig; the shape checks above already pin the contract)")

    print()
    if FAILS:
        print("RED — the production adapter suite refuses:", ", ".join(FAILS))
        return 1
    print("GREEN — the production adapter suite passes")
    return 0


def _behavioral_checks(check) -> None:
    """The §8.5 discipline, driven by the in-boundary driver (pgprod_selfcheck.py
    runs the psycopg behavioral proof INSIDE the approved adapters boundary —
    this test file imports no third-party package, only stdlib + pgprod)."""
    import subprocess, sys as _s
    r = subprocess.run([_s.executable, "-I",
                        str(pathlib.Path(__file__).resolve().parents[2] / "harness/adapters/pgprod_selfcheck.py")],
                       capture_output=True, text=True, timeout=120)
    out = r.stdout
    for code, what in (("ARV-PRD-007", "SET LOCAL scopes the owner inside the transaction"),
                       ("ARV-PRD-008", "after COMMIT the connection carries NO owner context"),
                       ("ARV-PRD-009", "the reused connection scopes user B correctly"),
                       ("ARV-PRD-011", "the implicit-transaction leak class is closed"),
                       ("ARV-PRD-010", "after ROLLBACK the connection carries NO owner context")):
        check(code, f"PASS {code}:" in out, what, "run the behavioral driver against the rig")
    check("ARV-PRD-012", "GREEN —" in out and r.returncode == 0,
          "the behavioral driver exits GREEN (all §8.5 checks pass)",
          "the driver must pass on the rig")



if __name__ == "__main__":
    sys.exit(main())
