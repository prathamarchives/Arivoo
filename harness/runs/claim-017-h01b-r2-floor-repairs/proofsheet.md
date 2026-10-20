# PROOF SHEET — slice claim-017-h01b-r2-floor-repairs (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 25df5f6e0ff1dae2cb7ce9f8b46111242c4e75a4
- generated (last record's timestamp): 2026-10-20T13:17:59.553654+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 72c80f4a8669213f · 2026-10-20T13:17:18.129108+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 770ffc593b8ea561 · 2026-10-20T13:17:24.607148+00:00
- `make verify` -> exit 0 · output sha256 d3f68c79ec3482ae · 2026-10-20T13:17:59.553654+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the CI real-floor runs (the anchored python3 -I launch with ARV_FLOOR_BASE_TOOLS) are exercised by the same integration path locally (test_10's anchored-copy launch) and by this session's FLOOR-REVIEW-1 clone-based attacks; the actual GitHub runner executions are observed at the PR's CI — pending at push; the post-merge selfcheck re-observes
- - the .git context channel is CLOSED by the controlled stub, but context uniformity is proven for that channel ONLY: any OTHER environmental difference a candidate can probe (env vars, mount points, hostname, runner files) remains a discrimination channel — stated in BOUNDARY, never claimed closed
- - the manifest artifact is a RECORD, not a tamper-proof store: a surviving same-user daemon can overwrite it after the run (the reviewer's 11b proved a forged GREEN manifest passing --validate-manifest while the driver's exit code stayed 1); CI consumes exit codes — no process-group kill or RLIMIT_NPROC today; that residual is H-01b-CI/H-02 material, stated not claimed
- - the /proc/<ppid>/environ read-back path in test_19 is Linux-specific (the sandbox and GitHub's ubuntu runners); on a non-Linux host the payload's deletion no-ops and the test degrades to a RED-floor assertion on the disposable base copy — recorded as an environment-coupled fixture, like the record-22 /tmp quirk note
- - no fresh technical verifier and no SEV beyond FLOOR-REVIEW-1 itself — the pre-H-02 discipline; H-02's activation gate remains dependent on H-01b-CI's -I flip landing first

## Assembly
- sheet sha256 (of the content above, excluding this line): 2c76f2dac6ad587197def37afcca4f8c83b04ebab1826f8b7c04d54983fbd4ee
