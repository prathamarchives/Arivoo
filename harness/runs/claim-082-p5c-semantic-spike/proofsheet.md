# PROOF SHEET — slice claim-082-p5c-semantic-spike (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 939f7c49cefe2a9e195f350b2cba9c30d8bcf12a
- generated (last record's timestamp): 2026-11-15T11:40:59.800348+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 5a541a891a6566e8 · 2026-11-15T08:49:50.822648+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 1 · output sha256 1aa75d4a99927d5f · 2026-11-15T11:16:20.614960+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:40:59.800348+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- (none stated — REPAIR: the not-verified list may not be empty; LAW-04)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 7ac15cb047158b709904d1989e00edfa79578b26646c40e2a658ee27357d0383
- reviewed_diff_sha256: 95886a4f108f3e7628bd9a516f37ef8537eea4633d675027aac30c3fb0c92927
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 2

## Assembly
- sheet sha256 (of the content above, excluding this line): 94ec7dd12727c8ef194665a6fd67a087b6a26d12ce80ca7b720e2c2fd85954bb
