# PROOF SHEET — slice claim-088-remote-target (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 41a7775350a0a5088901c497e0c5a452160b38d1
- generated (last record's timestamp): 2026-11-18T18:09:36.605912+00:00
- run records: 7

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 853a728fc8caf711 · 2026-11-18T18:08:46.070606+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 ea1447d917ee8b44 · 2026-11-18T18:09:12.437364+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-18T18:09:12.486001+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 261410d93eb2b126 · 2026-11-18T18:09:21.210829+00:00
- `python3 harness/tests/test_kernel.py` -> exit 0 · output sha256 2135a6f6bc84b816 · 2026-11-18T18:09:23.239354+00:00
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 510068fd393f15a7 · 2026-11-18T18:09:36.574368+00:00
- `make harness-health` -> exit 0 · output sha256 0eedd1f6e490c18c · 2026-11-18T18:09:36.605912+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the LIVE remote application (CLAIM-089's own slice: the guards prove the path's shape; the actual connection + application happens there with the migration credential in the release environment)
- sslmode=verify-full's CA-bundle mechanics against the real pooler (needs the live connection; noted for CLAIM-089's preflight)
- the remote CI runs (execute at the PR)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 99ee6d96f33dfbf542d00558f6ed031b6c873e468b8ce5fda5c9c9823d3d2926
- reviewed_diff_sha256: 380cfd0d674e1a9e98f46219ec68ebdf4ba7e55c2861ae3e800ac7e7f86c7d65
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 76eff0e6101c702e237d1f671b61b288711b3ed87ebfff9460ee186cebd7d89a
