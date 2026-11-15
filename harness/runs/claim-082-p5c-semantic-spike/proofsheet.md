# PROOF SHEET — slice claim-082-p5c-semantic-spike (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): a88c50cfb3d85eea3d8008f0b5b1a25255828f66
- generated (last record's timestamp): 2026-11-15T12:23:40.709181+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 5a541a891a6566e8 · 2026-11-15T08:49:50.822648+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 1 · output sha256 1aa75d4a99927d5f · 2026-11-15T11:16:20.614960+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:40:59.800348+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:42:21.872041+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 7c90c1a081db2612 · 2026-11-15T12:22:22.504691+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 7c90c1a081db2612 · 2026-11-15T12:23:40.709181+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- (none stated — REPAIR: the not-verified list may not be empty; LAW-04)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 3085e302e6b05a9a41509bbf499bb9c4b79b5c921abc61a4916731052b2a9cd0
- reviewed_diff_sha256: 7770a65e1330972dd18f5e66bbf6ed4ecd2a7c24dc2750431a506ffd7826184b
- disposition: PASS
- findings: 4 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): fc54ed331ee5ded3f5c6ddcb52b995764255c01bf0914b930759ce0e0caf7a71
