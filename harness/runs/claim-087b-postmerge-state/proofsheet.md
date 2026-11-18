# PROOF SHEET — slice claim-087b-postmerge-state (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): ac977c29432588e3cf2dbe57dd01ec490d24e9b1
- generated (last record's timestamp): 2026-11-18T17:17:13.211570+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 853a728fc8caf711 · 2026-11-18T17:16:37.391209+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 495f40d61a8ee44f · 2026-11-18T17:17:13.211570+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the remote CI on this post-merge slice (runs at the PR)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: bb65a6b7a666afeca4d820318ca8607177db630e79c623372f82be4b84f625dd
- reviewed_diff_sha256: 43a9136c3baa59184613ff164ce0dbde5e29c60318db95670bd865287544d526
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 1

## Assembly
- sheet sha256 (of the content above, excluding this line): 141191f4593214f5407252b343e2cbdce472f26cf9b0d918a208bb78ba8fc8ca
