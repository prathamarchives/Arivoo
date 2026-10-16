# PROOF SHEET — slice harness-s4b (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): cd1f61c36f5cbd663942dd3d9d600ec80136c7dd
- generated (last record's timestamp): 2026-10-16T12:01:36.467761+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-16T12:01:33.214450+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-16T12:01:33.624151+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-16T12:01:36.057332+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 ac7743f482124dd9 · 2026-10-16T12:01:36.467761+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the PR-time probe (a deliberately broken build observed RED in CI and closed unmerged) provides the end-to-end merge-blocking arm — it is the NEXT action after this slice, not inside it
- - no base-anchored floor for the harness tools themselves yet (the D-035 pattern covers the canonical tools; named as the next gate — P-17, never postponed)
- - the harness job is bound as a required check only AFTER its first green run on main is observed (the W-01 stage-2 pattern — binding evidence in record 18 §4.5)

## Assembly
- sheet sha256 (of the content above, excluding this line): 77b68735422ae20b11cf0732d89d00274662da397be685bfcf9987002a2d3320
