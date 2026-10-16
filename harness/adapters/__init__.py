"""harness/adapters — the only modules allowed to touch the world outside the
harness's own logic (LAW-24: ambient time / randomness / IDs / network /
environment live ONLY in adapters; the S4 boundary lint enforces this).

    pg.py    the DB adapter (the ONLY psql/env module — BND's adapters/db analog)
    clock.py arrives with S2 (the ONLY time reader)
    ids.py   arrives with S2 (the ONLY ID maker)
"""
