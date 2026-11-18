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
- report sha256: b1fe9b0de25d41c9ec26733acec4bb0321b370fe3709bdc00c003a6a9063dd0a
- reviewed_diff_sha256: c144e6a71fb26d68970244d85126cca2bc945444306670f9948a181d3675ee57
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): ed2b2ec1c816d8d1739d4ad54387a600d2107edd9e110527e795b2b11ba12d1f
