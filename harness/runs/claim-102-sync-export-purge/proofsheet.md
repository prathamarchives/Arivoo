# PROOF SHEET — slice claim-102-sync-export-purge (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 89c30e8c6afb5a23424045142daca5afd2196513
- generated (last record's timestamp): 2026-11-27T13:36:09.203039+00:00
- run records: 8

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 00df697c545293cd · 2026-11-27T11:48:31.913720+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 1 · output sha256 4836e059e808e8e1 · 2026-11-27T11:48:36.793206+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 25fb44631a0938a6 · 2026-11-27T11:48:53.101008+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 266e48f6c41f7697 · 2026-11-27T11:49:52.751691+00:00
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 4125e78ee1fad064 · 2026-11-27T13:21:36.158822+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 266e48f6c41f7697 · 2026-11-27T13:21:40.576148+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 7f8b2ce5f5586110 · 2026-11-27T13:21:56.984392+00:00
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 025a07f7f432ef16 · 2026-11-27T13:36:09.203039+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the multi-database restore TOPOLOGY through the route (the route restores into the SERVICE's db; the battery's reconciliation leg drives the kernel directly on a second scratch db — the deployment's topology composes the two)
- the sync delivery's desktop-over-HTTP transport client (Q19's local-store contract open — the backend surface complete; the client side is the desktop repo's own work)
- the 0021 machine on the REMOTE project (applies locally; the remote application is the guarded migration act's own slice — the Supabase migration credential never provided to this session)
- the KWR-002 map row (the map-family followup, unchanged); the semantic/model work (Q7 open — deterministic only)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: abf271dc893df04bf56f174ad23db977c73642a957b634dd8256989b01332ed2
- reviewed_diff_sha256: 12f4d6c3b25a01520ecb16a3308150df5423ea1285562b9fdc845811363f677b
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): cf3c5fcacc52550442c7ed45b890120c2c191514c262335136dc6760c66f729d
