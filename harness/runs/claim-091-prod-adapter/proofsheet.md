# PROOF SHEET — slice claim-091-prod-adapter (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c9fa679bf21df2603cb968389bac61f53bd89a65
- generated (last record's timestamp): 2026-11-18T20:06:30.888404+00:00
- run records: 7

## Run records (command, exit, output digest)
- `/home/z/my-project/Arivoo/.venv-waved/bin/python harness/tests/test_prod_adapter.py` -> exit 0 · output sha256 7c2c50b010d19461 · 2026-11-18T20:02:30.724519+00:00
- `ARV_TEST_RIG=1 .venv-waved/bin/python harness/tests/test_prod_adapter.py (the behavioral §8.5 form)` -> exit 0 · output sha256 1df8afc27aa9c2cf · 2026-11-18T20:02:30.877245+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 5d4f13d6d40faff4 · 2026-11-18T20:06:30.888404+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 2d108fe4a360bfb2 · 2026-11-18T20:05:23.042443+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 261410d93eb2b126 · 2026-11-18T20:02:36.960806+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-18T20:02:37.009878+00:00
- `python3 harness/tests/test_dep_boundaries.py` -> exit 0 · output sha256 c8f4d054e2585439 · 2026-11-18T20:05:23.042443+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the LIVE Supabase pooled run through pgprod.ProdPool itself (the pool construction against the real host needs the arv_app runtime credential — that is Wave D's credential slice, §6.5's separation; the driver/TLS/owner-context contracts are proven: TLS by CLAIM-088/089's verify-full battery, the §8.5 discipline by this suite's rig run)
- the statement timeout's enforcement live (the shape is set per-transaction; the live bound runs with the API's readiness checks)
- the psycopg pool's eviction/reconnect behaviors under fault injection (psycopg_pool's own documented behaviors; the adapter wraps, does not re-implement)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 4094bc890128750190cc5cad12ebbe22f80424630e96a8a5ed873acab750c752
- reviewed_diff_sha256: 31384304f5f25d76e4c4ed3acfe112b0f23f6720946a1c50040af005d1ff2e0f
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 52d73f2e68bcce0c90d25e4fbe0e9bff37ffad2d6fa659360e28c421eda90a85
