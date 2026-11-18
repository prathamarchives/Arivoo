# PROOF SHEET — slice claim-092-auth-boundary (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 39bbfed40066dfe5f8fb7b5c66277d9499a62f1b
- generated (last record's timestamp): 2026-11-18T20:49:14.736301+00:00
- run records: 9

## Run records (command, exit, output digest)
- `python3 harness/tests/test_auth_boundary.py` -> exit 0 · output sha256 5112ba53b1fa1418 · 2026-11-18T20:48:12.460953+00:00
- `/home/z/my-project/Arivoo/.venv-waved/bin/python -I harness/api/auth_selfcheck.py` -> exit 0 · output sha256 6c3443cfaeecc577 · 2026-11-18T20:48:12.571341+00:00
- `/home/z/my-project/Arivoo/.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 0416535a4612bfba · 2026-11-18T20:48:12.924152+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 5d4f13d6d40faff4 · 2026-11-18T20:48:13.094662+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 8bd065e609f3b180 · 2026-11-18T20:48:40.687832+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 261410d93eb2b126 · 2026-11-18T20:48:46.464109+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-18T20:48:46.510628+00:00
- `python3 harness/tests/test_dep_boundaries.py` -> exit 0 · output sha256 c8f4d054e2585439 · 2026-11-18T20:48:46.949602+00:00
- `python3 harness/tests/test_prod_adapter.py (the interpreter-guard form)` -> exit 0 · output sha256 49b298927425968d · 2026-11-18T20:49:14.736301+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- a LIVE Supabase-issued access token end-to-end (issuing one needs a real user + the email flow — the desktop integration's §17.1 test; the verify chain itself is proven: sign->JWKS->verify->derive + six refusal classes, and the LIVE public JWKS was fetched and pinned by kid/sha256)
- the JWKS fetch against the real endpoint through the module (the endpoint was verified live with curl — ES256, kid 55dac17b; the module's own fetch runs at serve time)
- uvicorn serving over a real socket (the ASGI interface is driven directly — the serve-time deployment slice)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 3b9fd0188b3a024236086fcca25dbb3d61b7704b88eb3a04253e8fdfac3d1162
- reviewed_diff_sha256: 15959a5bed787cae22477f1ed5218134f9d80a625ab57a71a2d733fdce630d72
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 91c38391a1461ab0887351f98d039711ff82787aed43e6455cef75c1edcaefbc
