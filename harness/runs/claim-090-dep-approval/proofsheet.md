# PROOF SHEET — slice claim-090-dep-approval (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): fcb4b83034aabcaa11acfb8bda7c6dbcaae44305
- generated (last record's timestamp): 2026-11-18T19:19:07.894703+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_dep_boundaries.py` -> exit 0 · output sha256 c8f4d054e2585439 · 2026-11-18T19:18:35.022059+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 853a728fc8caf711 · 2026-11-18T19:18:35.147054+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 2cd3a82ed8866866 · 2026-11-18T19:19:01.027334+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 261410d93eb2b126 · 2026-11-18T19:19:07.845212+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-18T19:19:07.894703+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the wheels' provenance beyond their PyPI-served SHAs (the SHAs are recorded from the exact downloads; a full reproducible-build attestation is out of scope for this slice)
- the CI runner's wheel-fetch equality (CI installs from the same PyPI pins with --require-hashes; equality is proven at the first API-slice CI run)
- the API runtime itself (no harness/api/ application code exists yet — this slice is the approval + the enforcement, not the API)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 734cfa92179b887e83b836e4168750d79cbc8068324ed47dfc39f6949158255a
- reviewed_diff_sha256: 6bf5b7bcc8f1bfdc6f4667e0cda8fdec70c5b1121c88d36017e3f8d364300ddf
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 27410a80635512b2e02aadec8a9d7c12e014b3fe5756b68615906135675f1087
