# 92 — API RUNTIME (the Workstream 2 boundary — CORS, readiness, the declared DB path)

> STATUS: SESSION ENGINEERING RECORD (2026-11-28; intent refs: INT-162/D-047 Workstream 2; D refs: D-042, LAW-08). Historical process artifact per D-022. Worklog: Tasks 129/130/131. PR #151 (the base repair), PR #150 (the declaration), this slice.

## §1 The owner's words (verbatim, the runbook's Batch 1)

"Production database integration — Finish the real PostgreSQL runtime execution path, correct API readiness, implement actual CORS and verify authentication."

And: "When one owner decision blocks a specific operation, continue everything else that is independently authorized." The owner's fresh-credential and host gates remain open; authentication verification against a live Supabase project is therefore NOT claimed here.

## §2 What landed

- `harness/api/cors.py` (new, stdlib only): `parse_allowed_origins()` — exact `scheme://host[:port]` entries, comma-separated, at most 16; unset means CORS OFF; wildcard, path, userinfo, empty entry, duplicate and out-of-range port refuse with `ARV-CORS-001`. `is_allowed()` is whole-string membership — no reflected origin.
- `harness/api/app.py`: `/health/ready`'s success predicate now includes `health_db_ready` (the earlier form could answer 200 "ready" while printing `"database": "not-open"`); the response also carries an explicit `db_ready` field. `CORSMiddleware` is installed from the parsed matrix with `allow_credentials=False` and a bounded method/header set.
- `harness/api/__main__.py`: `ARIVO_DB_READY` is the service's declaration (a missing declaration refuses with `ARV-SVC-002`); the production DB shape (`PGHOST`, `PGUSER` with the `arv_app` prefix, `PGSSLMODE=verify-full`, a readable `PGSSLROOTCERT`) is required with `ARV-SVC-003`. The named decision recorded here: **pgprod is the production path; `pg.psql` remains the rig/migration path** — the per-request pooled-executor migration is a named follow-up because it needs a live `arv_app` credential and a verifiable DB.
- `harness/api/env.example.txt`: the two variables documented.
- `harness/tests/test_api_runtime.py` (new, stdlib-only): ARV-RT-001..009; registered in the gate's `TESTS` tuple (the ARV-RED-008 class), with a typed red record and three chained amendments (two test-side probe repairs, one added check).

## §3 Verification (actual commands and exit codes)

- `python3 harness/tests/test_api_runtime.py` at the test-only commit `dbe512c`: **exit 1**, 8 named failures (RED — the parser absent, the predicate missing `health_db_ready`, no middleware, hardcoded startup readiness).
- The same command at the implementation head: **exit 0**, 11 PASS lines (ARV-RT-001..009, with 004 split into four malformed-origin cases).
- `python3 tools/verify_canonical_layer.py` → exit 0 (155 intents); `python3 -I tools/isolation_selftest.py` → exit 0 (no secret pattern introduced).
- `python3 harness/gate.py --slice claim-107-api-runtime-boundary --diff origin/main --skip-suites` → GREEN (red records, scope/size, claim coverage, LAW-24, LAW-08, the known-bad matrix, proof sheet, SEV). Suites skipped locally for lack of the PostgreSQL rig; CI runs them.

## §4 Not verified (LAW-04)

- No live Supabase authentication; no live DB probe (the credential is owner-gated).
- The per-request DB executor still uses `pg.psql` in the two remaining routes — the pooled `pgprod` migration is a follow-up, not claimed here.
- Starlette's CORS behavior was not driven through an ASGI client on this host (no fastapi); the pinned-venv battery remains its home.
- No Docker build, tunnel, DNS, storage or deployed endpoint was touched.

## §5 Conclusion

The runtime boundary is now honest: CORS is exact and off by default, readiness cannot claim an undeclared DB, and startup refuses an incomplete production DB shape with a named code. The remaining production-integration work (live auth, the pooled executor, the deployed surface) is blocked on owner gates and is named, not silently skipped.
