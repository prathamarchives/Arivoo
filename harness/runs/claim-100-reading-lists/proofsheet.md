# PROOF SHEET — slice claim-100-reading-lists (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): b4c232549c654448dc0752d6824cc8e4085e56b7
- generated (last record's timestamp): 2026-11-27T10:00:06.335246+00:00
- run records: 3

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 c03cc3042bfcb4e6 · 2026-11-27T09:59:51.439536+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 8f2382607c0c7943 · 2026-11-27T09:59:51.687274+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 0a610f22b1d3c351 · 2026-11-27T10:00:06.335246+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the KWR-002 map row (the named followup from the 099 SEV — byte-parity with the imports family)
- the retrieval/sync/export families (Workstreams 5-6)
- the remote btree/TOAST parity (carried from record 80 §9)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: abee6d9f722a6c4dd3471592b2e9e97d24264098a9f4f4c09aa0aa69e64b8ce6
- reviewed_diff_sha256: 2111836e4425e47cc74a72ac4e42bce9dfea31757dbcb0b924c5850b28317113
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 4f13416db328429ad43ab509e39a479ed60a1a99dc647e63ff294b4edd273b5f
