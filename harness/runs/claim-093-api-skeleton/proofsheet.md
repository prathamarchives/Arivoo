# PROOF SHEET — slice claim-093-api-skeleton (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 368e5493f0dfdc195be3ee1b3544a519fc6f2f7e
- generated (last record's timestamp): 2026-11-18T21:51:32.998788+00:00
- run records: 9

## Run records (command, exit, output digest)
- `python3 harness/tests/test_auth_boundary.py` -> exit 0 · output sha256 ac2b58d24ac61e9c · 2026-11-18T21:33:23.923030+00:00
- `/home/z/my-project/Arivoo/.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 0416535a4612bfba · 2026-11-18T21:33:24.272676+00:00
- `/home/z/my-project/Arivoo/.venv-waved/bin/python -I harness/api/auth_selfcheck.py` -> exit 0 · output sha256 6c3443cfaeecc577 · 2026-11-18T21:33:24.388268+00:00
- `python3 harness/tests/test_migrations.py (the JNL-06 rendering repair)` -> exit 0 · output sha256 5c402f23f5f63ee4 · 2026-11-18T21:51:32.998788+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 d5cf8c20342c430b · 2026-11-18T21:33:33.763840+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 065edbcf2207ec9c · 2026-11-18T21:34:08.424636+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-18T21:34:08.473163+00:00
- `python3 harness/tests/test_dep_boundaries.py` -> exit 0 · output sha256 c8f4d054e2585439 · 2026-11-18T21:34:08.888804+00:00
- `python3 harness/tests/test_prod_adapter.py` -> exit 0 · output sha256 49b298927425968d · 2026-11-18T21:34:09.144000+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the remote 0020 application (the migration is in the chain; the remote apply runs as its own act through the guarded path with its own run record — the §6.3 test-before-production rule; the local rig's application + the invariant check are this slice's proof)
- a live Supabase-issued token end-to-end (needs a real user — §17.1's desktop test; the verify chain is fully proven)
- uvicorn serving over a real socket (the serve-time deployment slice — Wave F)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 0da67f50beada83b941c1f201a3a6af43b12465e2401e6dda7dae019fee7db3f
- reviewed_diff_sha256: 2a2139af8ca1f924846b707a56c222752dfb6699bf6a7b416d5732c3474c4794
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 1d0af5f30745acb282459e25403c98935c48c79de13486ddc3f1054ed3f73ca8
