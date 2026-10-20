# PROOF SHEET — slice claim-026-r02-floor-hardening (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c1742fa328e9fe35be81ddbf9cc4e42ed27307ad
- generated (last record's timestamp): 2026-10-20T17:06:24.349901+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-20T17:05:43.666021+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-20T17:05:44.014171+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-20T17:05:45.886226+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 260cbc11f7b5e813 · 2026-10-20T17:05:46.072478+00:00
- `make verify` -> exit 0 · output sha256 3080128df7714c48 · 2026-10-20T17:06:24.349901+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- (none stated — REPAIR: the not-verified list may not be empty; LAW-04)

## Assembly
- sheet sha256 (of the content above, excluding this line): 56d105a376d076099f1fa6bfabe5761377af7a2facda80dd53dc17122d73f6fe
