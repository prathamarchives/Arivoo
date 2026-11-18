# PROOF SHEET — slice claim-091-prod-adapter (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c9fa679bf21df2603cb968389bac61f53bd89a65
- generated (last record's timestamp): 2026-11-18T20:22:02.169043+00:00
- run records: 7

## Run records (command, exit, output digest)
- `/home/z/my-project/Arivoo/.venv-waved/bin/python harness/tests/test_prod_adapter.py` -> exit 0 · output sha256 7c2c50b010d19461 · 2026-11-18T20:22:02.169043+00:00
- `/home/z/my-project/Arivoo/.venv-waved/bin/python harness/tests/test_prod_adapter.py ({'ARV_TEST_RIG': '1'})` -> exit 0 · output sha256 f6f032e110ed5f34 · 2026-11-18T20:22:02.169043+00:00
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
- report sha256: 431c6bab78670d04030a38ab6cc7693ff51965e9fc2cd864aace71db885b00e3
- reviewed_diff_sha256: 732728009722c19052cbb98fb23058201111bdb72a2c86233421b34e25a7be7a
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 6549cdc7bc48abbebe23b8eec3873d44eb56bcf48367753f491a03157b78667b
