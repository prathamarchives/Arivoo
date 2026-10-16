#!/usr/bin/env python3
"""harness/health.py — ARV-RIG-001: is the real stack reachable, and what is it?

Prints the engine version (FACT-001's local-side evidence) and exits 0/1 with a
named code + repair on failure (diagnostics contract).
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])
from harness.adapters import pg  # noqa: E402


def main() -> int:
    r = pg.psql("SELECT version();", db="postgres")
    if r.returncode != 0:
        print("FAIL ARV-RIG-001: PostgreSQL unreachable through the adapter "
              f"(PGHOST/PGPORT/PGUSER per harness/adapters/pg.py) — {r.stderr.strip()[:200]}")
        print("      repair: start the rig (locally the .pg cluster, port 5433; "
              "CI the postgres:17 service) — FACT-001 records the engine parity requirement")
        return 1
    print(f"OK ARV-RIG-001: {r.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
