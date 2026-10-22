# PROOF SHEET — slice claim-031-r06-trusted-path-toctou-isolation (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 03475d9254c618f2f09b943dfbad94d08c0e7b53
- generated (last record's timestamp): 2026-10-22T18:12:17.581757+00:00
- run records: 11

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T18:10:34.782191+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T18:10:35.149922+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T18:10:37.284010+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 dc60100a65827746 · 2026-10-22T18:10:56.150653+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 e8a25937d1974342 · 2026-10-22T18:11:09.600737+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 95b6ad1cb9ae1535 · 2026-10-22T18:11:11.612408+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 f5d03f9d5820626f · 2026-10-22T18:11:11.998585+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-22T18:11:17.952650+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 e9896ddf973cb10c · 2026-10-22T18:11:18.101437+00:00
- `timeout 900 python3 tools/verify_selftest.py` -> exit 0 · output sha256 6c18ac0ffbf6699d · 2026-10-22T18:11:26.863068+00:00
- `make verify` -> exit 0 · output sha256 b58a170c317465b8 · 2026-10-22T18:12:17.581757+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - not verified (LAW-04 — required, never empty-by-omission; the R-06 slice's honest limits):
- - - the isolation is STRUCTURAL, verified by the pinned workflow shape (test_11) + the RED/GREEN scratch simulation
- (red-01.txt): the live end-to-end CI proof (a genuinely tampering suite on a real PR, refused by the refresh) is
- observed only if such a PR occurs — no synthetic PR was fabricated to force it, and the first draft of the RED
- itself showed why honesty matters: the scope-only tamper was CAUGHT by the gate's own defense-in-depth (the
- independent claims check + the KB-05 broken-guard machinery), so the full forgery targets the judgment entry point
- - - the HEAD re-fresh's clean semantics are actions/checkout@v4's documented behavior (clean: true = git clean of the
- worktree): the structure pin proves the step's presence and ordering; the checkout action itself is externally
- trusted infrastructure (the same trust as the original checkout — never claimed audited here)
- - - the canonical-layer job's four anchored launches and the head-tools job retain the same-job same-user execution
- class the floor's BOUNDARY states (F-003 EXTERNAL: GitHub-hosted runners, candidate code never executes in those
- jobs' interpreters, but runner-level isolation is the platform's claim, not this repo's) — R-06 closed the S1b->S4c
- filesystem channel; the runner-level boundary remains the platform's
- - - S1b's WITHIN-PROCESS exposure is analyzed and accepted: the driver loads base gate.py ONCE before any suite runs,
- and a suite tampering the on-disk copy cannot affect the already-loaded process; the RED proves the cross-PROCESS
- channel (S4c's fresh load) was the live forgery path and R-06 closes it with the fresh re-checkouts
- - - the branch protection's addition of the harness-trusted required context happens AFTER the job's first green run is
- observed (the W-01 stage-2 pattern, recorded in the PR/merge sequence — never before the evidence exists)

## Assembly
- sheet sha256 (of the content above, excluding this line): 713fab3e8e049e3f24053950f3e22f2174986f8ef53b2795eadf177ac1c30e27
