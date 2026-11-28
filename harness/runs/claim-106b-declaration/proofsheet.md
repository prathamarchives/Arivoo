# PROOF SHEET — slice claim-106b-declaration (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 184cffa47d92e784af8d2987d0493b2649410393
- generated (last record's timestamp): 2026-11-28T05:35:31.892835+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 be53ca0f3f3af262 · 2026-11-27T15:45:26.490574+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 be53ca0f3f3af262 · 2026-11-27T15:50:02.198012+00:00
- `.venv-waved/bin/python -I harness/tests/test_acceptance_campaign.py` -> exit 0 · output sha256 5a666053ca900f3f · 2026-11-27T15:58:46.470963+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 01697530e4879783 · 2026-11-28T05:34:53.623925+00:00
- `python3 -I tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-11-28T05:35:31.718741+00:00
- `python3 harness/tests/test_acceptance_campaign.py` -> exit 0 · output sha256 97483947a90c95b8 · 2026-11-28T05:35:31.892835+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- This slice now carries TWO code repairs beside the declaration artifact (session 66): tools/isolation_check.py's scan-count re-base and the acceptance campaign's explicit ARV-ACC-000 skip.
- Not verified: (1) the campaign's ACC-01..18 were NOT executed in this session — no PostgreSQL rig, no fastapi/jwt/psycopg on this host; the campaign's executed-path evidence remains the session-65 rig run records (run-03).
- (2) The canonical-layer self-test was verified locally in BOTH shapes (in-tree and the CI-shaped anchored copy in a clean clone), but the authoritative confirmation is the remote canonical-layer job on this PR's head.
- (3) The 8000 count cap is sized against today's measured corpus (1997 files); it is a re-base of an anomaly guard, not a proof that no future tree can exceed it.
- (4) The venv-less harness-suites runner's own provisioning of fastapi/psql (the deferred option that would let CI EXECUTE the campaign) is NOT in this diff — it is a named follow-up needing its own claim.
- (5) No production database, storage provider, host, tunnel or deployed service was touched by this slice.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: bb66d597a8d3cc25a90fe98a7fc56bb0207551257068388c8cd6225cc086a822
- reviewed_diff_sha256: 3135eef632d8d9c49a6d248dd06a86c4855583310c2c2abe13a29587490ffcde
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 4565e8083390d8222ceff5ee1411233ac79a0566af8ce0cba60323fed0af3702
