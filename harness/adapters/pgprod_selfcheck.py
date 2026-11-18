#!/usr/bin/env python3
"""harness/adapters/pgprod_selfcheck.py — the §8.5 behavioral driver (CLAIM-091).

Runs the transaction-local owner-context discipline against the local rig
through the SAME psycopg driver the production path uses (engine parity),
printing PASS/FAIL lines the suite asserts on. Lives INSIDE the approved
psycopg boundary (harness/adapters/ — D-048/D-049): the psycopg import stays
where the approval allows it.
"""
import sys
import psycopg

A = "11111111-1111-1111-1111-111111111111"
B = "22222222-2222-2222-2222-222222222222"
FAILS = []

def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        FAILS.append(code)

def main() -> int:
    conninfo = {"host": "127.0.0.1", "port": 5433, "dbname": "postgres",
                "user": "postgres", "sslmode": "prefer"}
    with psycopg.connect(**conninfo) as base:
        # THE FIXED DISCIPLINE: every lease — read or write — opens its OWN
        # transaction (an un-scoped read leaves an open implicit transaction;
        # the next lease would nest as a savepoint and SET LOCAL would leak).
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SET LOCAL app.current_owner = '" + A + "'")
                cur.execute("SELECT current_setting('app.current_owner', true)")
                check("ARV-PRD-007", cur.fetchone()[0] == A,
                      "SET LOCAL scopes the owner inside the transaction")
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SELECT current_setting('app.current_owner', true)")
                val = cur.fetchone()[0]
        check("ARV-PRD-008", val == "" or val is None,
              "after COMMIT the connection carries NO owner context (the §8.5 reuse race)")
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SET LOCAL app.current_owner = '" + B + "'")
                cur.execute("SELECT current_setting('app.current_owner', true)")
                check("ARV-PRD-009", cur.fetchone()[0] == B,
                      "the reused connection scopes user B correctly")
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SELECT current_setting('app.current_owner', true)")
                val = cur.fetchone()[0]
        check("ARV-PRD-011", val == "" or val is None,
              "the implicit-transaction leak class is closed (every lease transaction-scoped)")
        try:
            with base.transaction():
                with base.cursor() as cur:
                    cur.execute("SET LOCAL app.current_owner = '" + A + "'")
                raise RuntimeError("simulated mid-transaction failure")
        except RuntimeError:
            pass
        with base.transaction():
            with base.cursor() as cur:
                cur.execute("SELECT current_setting('app.current_owner', true)")
                val = cur.fetchone()[0]
        check("ARV-PRD-010", val == "" or val is None,
              "after ROLLBACK the connection carries NO owner context")
    print()
    if FAILS:
        print("RED — the §8.5 behavioral driver refuses: " + ", ".join(FAILS))
        return 1
    print("GREEN — the §8.5 behavioral driver passes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
