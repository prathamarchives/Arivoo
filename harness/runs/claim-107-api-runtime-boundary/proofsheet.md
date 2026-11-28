# PROOF SHEET — slice claim-107-api-runtime-boundary (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c0da44aab677a09a99c25aba1fd5a429821dac8c
- generated (last record's timestamp): 2026-11-28T06:13:18.133682+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 harness/tests/test_api_runtime.py` -> exit 0 · output sha256 b0bfa0c556d0c09e · 2026-11-28T06:12:44.135819+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 01697530e4879783 · 2026-11-28T06:12:44.505967+00:00
- `python3 -I tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-11-28T06:13:18.133682+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- This is a runtime-boundary slice, not a deployed-service slice. Not verified:
- - No live Supabase authentication was exercised: no fresh arv_app credential and no JWKS fetch on this host (the owner gates the credential).
- - The production DB executor's per-request path still uses pg.psql in the two remaining routes; the pgprod pooled-executor migration is a NAMED FOLLOW-UP, not silently claimed. This slice only declares and validates the production shape at startup.
- - /health/ready's DB leg is a service declaration (ARIVO_DB_READY), not a live probe: a genuine connection check needs a live credential and is named as a follow-up.
- - The new suite's CORS checks are stdlib/structural; the actual starlette middleware behavior was not driven through an ASGI client (no fastapi on this host). The pinned-venv route battery remains the place that exercises the app.
- - No Docker image build, Cloudflare tunnel, DNS, storage provider or deployed endpoint was touched (Q18/Q12/Q17 owner-gated).
- - The five required checks are the authoritative confirmation of this PR; the local runs are preflight.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 734b9ad0f39b553752aaa2d24fbde3c63be2af38355b4269772837466d0af71c
- reviewed_diff_sha256: e6fd43e5fb3ebae6882c8770f6f5b3f647028c41029654330887bca5e8562bf6
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): b7df19b16ac7a25cc9e922a2667d848fc14148aa137d96d0bb07cccfef98c557
