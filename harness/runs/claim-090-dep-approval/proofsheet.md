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
- report sha256: 0d45b8645ca4808020f6969570e9fe39545073edbfe3e0100c6a7451ee6c982a
- reviewed_diff_sha256: 6c116b8da4e4f19ea48dc32231c8fd21a624cd2f9db76985c6621095978dea57
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 39d2bb009f91f4a95e9baaf1c642c01e89aab881538db95c740a8013d4baea5f
