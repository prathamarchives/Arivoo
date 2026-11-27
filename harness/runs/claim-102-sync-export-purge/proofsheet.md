# PROOF SHEET — slice claim-102-sync-export-purge (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c93b742567c9ba7d21bad21f5f44e0d5cffdbee6
- generated (last record's timestamp): 2026-11-27T13:21:56.984392+00:00
- run records: 7

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 00df697c545293cd · 2026-11-27T11:48:31.913720+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 1 · output sha256 4836e059e808e8e1 · 2026-11-27T11:48:36.793206+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 25fb44631a0938a6 · 2026-11-27T11:48:53.101008+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 266e48f6c41f7697 · 2026-11-27T11:49:52.751691+00:00
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 4125e78ee1fad064 · 2026-11-27T13:21:36.158822+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 266e48f6c41f7697 · 2026-11-27T13:21:40.576148+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 7f8b2ce5f5586110 · 2026-11-27T13:21:56.984392+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the multi-database restore TOPOLOGY through the route (the route restores into the SERVICE's db; the battery's reconciliation leg drives the kernel directly on a second scratch db — the deployment's topology composes the two)
- the sync delivery's desktop-over-HTTP transport client (Q19's local-store contract open — the backend surface complete; the client side is the desktop repo's own work)
- the 0021 machine on the REMOTE project (applies locally; the remote application is the guarded migration act's own slice — the Supabase migration credential never provided to this session)
- the KWR-002 map row (the map-family followup, unchanged); the semantic/model work (Q7 open — deterministic only)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 4015b073cd32db7a2fcfa7c3bccf945045653e84872e331cc68cb831aa6167f9
- reviewed_diff_sha256: a0f7c96962a29b4fd8d75ff4b689a68b1a99b8ea485254b83fd5d8cb500d1aad
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): f2291d2c08ba11567dad2e3073e16066ac15a119510bbe87bfa08a35cc7cd487
