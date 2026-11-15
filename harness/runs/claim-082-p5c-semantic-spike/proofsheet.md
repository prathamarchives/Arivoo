# PROOF SHEET — slice claim-082-p5c-semantic-spike (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): a5d8c972b2a22bd8a27d649c00412697b3099576
- generated (last record's timestamp): 2026-11-15T11:42:21.872041+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 5a541a891a6566e8 · 2026-11-15T08:49:50.822648+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 1 · output sha256 1aa75d4a99927d5f · 2026-11-15T11:16:20.614960+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:40:59.800348+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:42:21.872041+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- (none stated — REPAIR: the not-verified list may not be empty; LAW-04)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 4a0c94b67e53f04a4c85d523613df54f6ac0c76352a7bc72c63d2d9697f838b9
- reviewed_diff_sha256: 6c6f59367d567cbefa991734b2270e0a57021831ae97868f1d1ae5953caf9e47
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 2

## Assembly
- sheet sha256 (of the content above, excluding this line): 054a4a31c6887b603f298c492182f87988d0624b8b2d8fc3572c1b88ee2ecbf2
