# PROOF SHEET — slice claim-098-highlights-bookmarks (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): ab56883eda262e745ac37bf2bdabcf348832081b
- generated (last record's timestamp): 2026-11-27T06:51:31.616255+00:00
- run records: 6

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 e83d26fefe58e69c · 2026-11-27T06:26:11.433085+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 b51fc97abae6104a · 2026-11-27T06:26:11.597342+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 abd3536cc7cdc9a9 · 2026-11-27T06:26:20.155246+00:00
- `.venv-waved/bin/python -I /home/z/my-project/scripts/sev098_probe.py` -> exit 0 · output sha256 6bc9dd6c952af1a8 · 2026-11-27T06:49:25.772682+00:00
- `bash harness/runs/claim-098-highlights-bookmarks/red-observation.sh` -> exit 1 · output sha256 460b41e4835e85a6 · 2026-11-27T06:49:37.105330+00:00
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 fbc1718223d74c3b · 2026-11-27T06:51:31.616255+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the passage-text serving route (the §11.2 'source/read data' body arm — rides the notes/journal slice's content decision; the anchor resolution serves the content-addressed form here)
- the notes/journal/references/reading-lists families (CLAIM-099+ — the §11.2 rows that remain)
- the remote btree/TOAST parity (carried from record 80 §9)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 43186980c19450598a8cf529fab0541b8e029db9216f27b4df6633442585ad0e
- reviewed_diff_sha256: acba09ba2b033880c40c9eca44fd2cc421a6bf44a0e370eae6b8b1c170a17ced
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 7

## Assembly
- sheet sha256 (of the content above, excluding this line): 1532dc3beb7738539d74d3855ec29fd8e2c88f846de357bb33bc01932726e019
