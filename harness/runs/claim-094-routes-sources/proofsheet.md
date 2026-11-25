# PROOF SHEET — slice claim-094-routes-sources (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): b02bfa574b0f77bd125af82cac5c775813ae9a3e
- generated (last record's timestamp): 2026-11-25T07:13:18.459997+00:00
- run records: 9

## Run records (command, exit, output digest)
- `python3 harness/tests/test_auth_boundary.py` -> exit 0 · output sha256 ac2b58d24ac61e9c · 2026-11-25T07:07:46.541718+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 5c402f23f5f63ee4 · 2026-11-25T07:07:53.714277+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 d0711c16c2af1945 · 2026-11-25T07:07:53.898445+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 38f134cce44f6b3f · 2026-11-25T07:08:24.330443+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-25T07:08:24.441539+00:00
- `python3 harness/tests/test_dep_boundaries.py` -> exit 0 · output sha256 c8f4d054e2585439 · 2026-11-25T07:08:24.945811+00:00
- `python3 harness/tests/test_prod_adapter.py` -> exit 0 · output sha256 49b298927425968d · 2026-11-25T07:08:25.166742+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 fe12a0c92fb237d7 · 2026-11-25T07:13:16.507608+00:00
- `/home/z/my-project/Arivoo/.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 110d9148a0d30b05 · 2026-11-25T07:13:18.459997+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- a live Supabase-issued token end-to-end (needs a real user — §17.1's desktop test; the verify chain is fully proven with a real ES256 key pair)
- uvicorn serving over a real socket (the serve-time deployment slice — Wave F)
- the route surface against the remote project database (runs when the API service deploys — Wave F's credential slice)
- the remote 0020 application (its own registered act through the guarded path; the remote ledger last live-verified 0001–0019 on 19 Nov; this session observed the project healthy through the management API but did not re-read the migration ledger — the DB route not re-probed from this sandbox)
- F6's exact minimum trigger size (the long-unbroken-token kernel defect against the btree index-row limit — its own follow-up kernel claim with its own RED test; the adapter's 32 MiB cap does not mask it)
- the five required CI checks (they run on the PR head — green only after the PR opens; this evidence set binds to the pre-PR diff)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 87f59af268a1e9b671ab2c89b0e1eeb09e1abbea8eb90159bec0f3e95da01ea0
- reviewed_diff_sha256: 0083ee36e7cd21565c0930c19b5ef3b85a89905163d330fdd086f3fbab65aa00
- disposition: PASS
- findings: 6 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 8e4537fd110d4d75ed48cd7718215ca3e37a592b85acfcd7113ca1b559ae56b4
