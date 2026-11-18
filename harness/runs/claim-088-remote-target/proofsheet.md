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
- report sha256: 290276396b87d80a2661050f176d179f0c7cbf5669eab890bc36cde6ccd05589
- reviewed_diff_sha256: 42c5b44e834f69078f85c50e6fbc715fef83c64766a49431b45c33c71be3bf43
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): d614a2cfd05b57125b69f8602352759db00b62a3bc6741c64ec665614a7ed26e
