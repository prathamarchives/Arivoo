# PROOF SHEET — slice claim-082-p5c-semantic-spike (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 8187fb3f9ca63010265b170527f327e675d9e803
- generated (last record's timestamp): 2026-11-15T12:22:22.504691+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 5a541a891a6566e8 · 2026-11-15T08:49:50.822648+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 1 · output sha256 1aa75d4a99927d5f · 2026-11-15T11:16:20.614960+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:40:59.800348+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 bbfeebabd5a1eead · 2026-11-15T11:42:21.872041+00:00
- `python3 harness/tests/test_semantic_spike.py` -> exit 0 · output sha256 7c90c1a081db2612 · 2026-11-15T12:22:22.504691+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- (none stated — REPAIR: the not-verified list may not be empty; LAW-04)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: d78bbfab18f4d0658afc4139c0cb5226a493d6c8c6230bbe33da607217645ae2
- reviewed_diff_sha256: 6c6f59367d567cbefa991734b2270e0a57021831ae97868f1d1ae5953caf9e47
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 264511b254c66cb138d30339e4369bbb02f3e7c480d69fa6d1c47a819dd4744b
