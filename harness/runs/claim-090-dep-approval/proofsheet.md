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
- report sha256: 5306ddfed36360abd84406f5392c06e2a4b6b4e75dea0ce287e6490ebd933fdb
- reviewed_diff_sha256: 6f590036107487de8d17b73249d4448b7569be92621cd6ae4b0c72bcd647c7d3
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 94c48dad51d3bade99c38ba140ee6021b60be65704bd182a1401cbfe3f5c007b
