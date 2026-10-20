# PROOF SHEET — slice claim-013-h01b-activation (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 0dc6aaf3e6ca7755aefd800372d2c3ab8e60bac5
- generated (last record's timestamp): 2026-10-20T09:20:12.696580+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 81f13cc867679e21 · 2026-10-20T09:19:31.820169+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 7fb9efacdb43abcb · 2026-10-20T09:19:39.137639+00:00
- `make verify` -> exit 0 · output sha256 16b5411e50a5a0d2 · 2026-10-20T09:20:12.426060+00:00
- `python3 harness/claims.py` -> exit 0 · output sha256 6beec6ef5d385ac5 · 2026-10-20T09:20:12.492422+00:00
- `python3 tools/isolation_check.py` -> exit 0 · output sha256 4b8f208f23cf8aa4 · 2026-10-20T09:20:12.696580+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the CI real-floor run (the anchored python3 -I launch with ARV_FLOOR_BASE_TOOLS + mutation_runner.py in the anchor loops) is exercised by the same integration path locally (test_10's anchored-copy launch) but the actual GitHub runner execution is observed only at the PR's CI — pending at push; the post-merge selfcheck re-observes
- - the residual boundary is INHERENT and stated in every run: children share the host and OS user — NOT OS sandboxing; a hostile child could kill the judge (RED, never green); F-003/F-004 (workflow-definition trust) and F-006 (the candidate gate's registry-at-import) are H-01b-CI's items; Q10 owner-gated
- - the fake-fail residual is demonstrated, not hidden (test_13): the two-sided floor (this per-case protocol + the positive 51/0 step of the same required job) is the documented dependency
- - run_floor landed in THIS slice, not part 1: part 1's module was inert and its missing orchestration was invisible to part 1's CI by construction — the trim incident and the honest re-attribution are in record 22 §8
- - no fresh technical verifier and no SEV — the pre-H-02 discipline; the card's "an independent review tries to break the new mechanism" exit item is OPEN (the next session's first candidate)
- - the sandbox /tmp quirk (intermittently blind fresh /tmp lookups in driver-spawned children under this host's unittest context) is recorded in record 22 §8; CI's ubuntu runners share /tmp; the test's delivery mechanism is deterministic regardless

## Assembly
- sheet sha256 (of the content above, excluding this line): f99ba14b4128b23da59e556374213f84c9ca2240edeabb0fc55d31c8952beda8
