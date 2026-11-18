# PROOF SHEET — slice claim-086-arch-turn (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 0c478252469f3690cee61dd6caf0ad08e02dc5f3
- generated (last record's timestamp): 2026-11-18T15:22:31.482181+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 ab60b0d1bc7de5eb · 2026-11-18T15:14:36.265697+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 bfc29bb1f5eb1c37 · 2026-11-18T15:15:09.894081+00:00
- `make harness-health` -> exit 0 · output sha256 0eedd1f6e490c18c · 2026-11-18T15:15:09.929169+00:00
- `make harness-tests` -> exit 0 · output sha256 2ef563a61d77b551 · 2026-11-18T15:22:10.608354+00:00
- `python3 harness/gate.py --slice claim-086-arch-turn --diff origin/main --skip-suites` -> exit 1 · output sha256 17e293dd9bda9d60 · 2026-11-18T15:22:31.482181+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the local isolation check's ZCODE_OFFICIAL_ENDPOINT_TOKEN finding (the sandbox harness's own env var — the local agent environment, never the CI runner; the tracked-file scan is clean; disclosed, not repaired)
- the remote CI runs (they execute at the PR — the five checks on the branch head and the merge commit)
- the D-042 review round (it runs at the PR before the merge, per the standing protocol)
- the Supabase project's live state (the report's own audit stands as the observation; workstream 2 re-verifies against the real project)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 8101ef0dc1f4c88e9d60bca046b64fcd8ff0c178f42307bd669d0f023823f20f
- reviewed_diff_sha256: af030dc19a4fb3c8192e127d45255ec92533e469fe40fa125c0911c067d818cc
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 3a08d6e99274bb52832eb90ddd885d56196a8486d2baff92f30772fc04f405e8
