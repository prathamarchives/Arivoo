# PROOF SHEET — slice claim-101-retrieval-api (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): d65b6946293d3c7c56f53acdf12baf3f50019d8e
- generated (last record's timestamp): 2026-11-27T10:23:58.129869+00:00
- run records: 3

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 c6a6be3786bc04c7 · 2026-11-27T10:23:43.109089+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 fe3ea598cbfefaa4 · 2026-11-27T10:23:43.337254+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 811d988edb8de77c · 2026-11-27T10:23:58.129869+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the KWR-002 map row + the alternation's named-409 candidate (the map-family followup, two members)
- the sync/export/restore/purge families (Workstream 6), the remote MCP transport (7), storage/workers (8-9), runtime+domain (10)
- the semantic/model work (Q7 open — deterministic only); the remote btree/TOAST parity (carried from record 80 §9)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 84829c7d7f02c7ac7fc27c09f995f40b52c840007558226b6719a6daf0935633
- reviewed_diff_sha256: 7f5c551a5d7d018e9195f1515381629485f4771b9beca9c85434f3f4a83698fe
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): e7896a1f410d5f1734db618acca37a1ffeb7b7196b9c1ea287b5ef11988290fe
