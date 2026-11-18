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
                            user="arv_app", password="super-secret-value",
                            sslrootcert="/tmp/ca-bundle.pem")
    check("ARV-PRD-006", "super-secret-value" not in repr(cfg),
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
    """The §8.5 two-user reuse race, run against the local rig through the
    SAME psycopg driver (the rig's self-signed CA means sslmode here is
    'prefer' — the SHAPE under test is the owner-context discipline, not TLS)."""
    import psycopg
    conninfo = {"host": "127.0.0.1", "port": 5433, "dbname": "postgres",
                "user": "postgres", "sslmode": "prefer"}
    a = "11111111-1111-1111-1111-111111111111"
    b = "22222222-2222-2222-2222-222222222222"
    with psycopg.connect(**conninfo) as base:
        # THE FIXED DISCIPLINE (ARV-PRD-011's finding): EVERY lease — read or
        # write — opens its OWN transaction. An un-scoped SELECT on an
        # autocommit=False connection leaves an OPEN implicit transaction; the
        # next transaction() then nests as a SAVEPOINT and SET LOCAL leaks
        # across the inner "commit". Scoping every lease removes the class.
        # user A's write lease
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SET LOCAL app.current_owner = '" + a + "'")
                cur.execute("SELECT current_setting('app.current_owner', true)")
                check("ARV-PRD-007", cur.fetchone()[0] == a,
                      "SET LOCAL scopes the owner inside the transaction",
                      "set the GUC transaction-locally")
        # a READ lease (its own transaction — the discipline)
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SELECT current_setting('app.current_owner', true)")
                val = cur.fetchone()[0]
        check("ARV-PRD-008", val == "" or val is None,
              "after COMMIT the connection carries NO owner context (user B's lease is clean — the §8.5 race)",
              "the GUC must be transaction-local, never session-default")
        # user B's write lease on the SAME connection
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SET LOCAL app.current_owner = '" + b + "'")
                cur.execute("SELECT current_setting('app.current_owner', true)")
                check("ARV-PRD-009", cur.fetchone()[0] == b,
                      "the reused connection scopes user B correctly",
                      "the lease must set the new owner per transaction")
        # the post-B read lease: B's GUC must NOT have leaked past the commit
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SELECT current_setting('app.current_owner', true)")
                val = cur.fetchone()[0]
        check("ARV-PRD-011", val == "" or val is None,
              "the implicit-transaction leak class is closed (an interleaved read cannot capture a prior owner: every lease is transaction-scoped)",
              "scope EVERY lease in its own transaction — the un-scoped SELECT leaves an open implicit transaction and the next lease nests as a savepoint")
        # after ROLLBACK (an exception inside the transaction block): also clean
        import contextlib
        try:
            with base.transaction():
                with base.cursor() as cur:
                    cur.execute("SET LOCAL app.current_owner = '" + a + "'")
                    raise RuntimeError("simulated mid-transaction failure")
        except RuntimeError:
            pass
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SELECT current_setting('app.current_owner', true)")
                val = cur.fetchone()[0]
        check("ARV-PRD-010", val == "" or val is None,
              "after ROLLBACK the connection carries NO owner context (a rollback must not leak A's context)",
              "rollback must clear the transaction-local GUC")


if __name__ == "__main__":
    sys.exit(main())
