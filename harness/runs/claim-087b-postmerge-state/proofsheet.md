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
- report sha256: dabc64367798ac84e2f046bea15f2cd0daa26dc61dc120556664714b6d00ccb5
- reviewed_diff_sha256: 33d6c0425c67e5b6648a6e1606037ad410d44da3d7dd1b60db96e056214a5806
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 1

## Assembly
- sheet sha256 (of the content above, excluding this line): 9ca202c6967d731aa336199eb2b150cafef22618c1b312b976b80e5b24be98e1
