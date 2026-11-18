# PROOF SHEET — slice claim-089-remote-apply (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 58cb15497a474a0699fc4dfd5424911c1ddf59ee
- generated (last record's timestamp): 2026-11-18T18:36:00.801975+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 harness/migrate.py (remote apply: ARV_REMOTE_TARGET=wcuuakhdmsmmxagvbdmg; the guarded path; sslmode=verify-full; the migration credential from the release env — NEVER recorded)` -> exit 0 · output sha256 see run-02 (the  · 2026-11-18T18:35:17.941966+00:00
- `python3 harness/migrate.py --verify (remote) + the §7.3 battery (8 verification queries + the no-op rerun + the guard negatives)` -> exit 0 · output sha256 0295d7bef9bf427d · 2026-11-18T18:36:00.801975+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 853a728fc8caf711 · 2026-11-18T18:35:17.941966+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 b4311abaffd0019b · 2026-11-18T18:35:17.941966+00:00
- `python3 harness/tests/test_remote_target.py` -> exit 0 · output sha256 027d587ce7d342c1 · 2026-11-18T18:35:17.941966+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 261410d93eb2b126 · 2026-11-18T18:35:17.941966+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the runtime roles' LOGIN passwords (none exist yet: the chain creates the roles LOGIN-ready but the password grants are the Wave-D runtime-credential slice's own act — the §6.5 table's separation preserved)
- the advisors' function_search_path_mutable WARN lints (23 on the 0002-0018 functions; the 0019 pin exists — named as the P2: a future migration 0020 pins the rest; WARN-level, not a high risk, and the functions are schema-qualified internally)
- the two-owner RLS behavioral test against the REMOTE (the local rig proves the contract; the remote behavioral two-owner run belongs with the API's Wave-D integration tests where a real Auth identity drives owner scope)
- the remote CI runs (execute at the PR)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 62fabf34f864b75fa22a183beaeb573f04b87e6b81af4fe82ebfff09f51dc5e5
- reviewed_diff_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 2ffa1c0b9c45d6e215eae0acebb46814e9361312d2d0b299ef5964756cc7ed21
