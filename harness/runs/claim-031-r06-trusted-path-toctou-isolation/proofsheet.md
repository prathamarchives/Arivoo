# PROOF SHEET — slice claim-031-r06-trusted-path-toctou-isolation (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 3bb575ca6c9a1004906f21399d9077c6475cf56c
- generated (last record's timestamp): 2026-10-22T18:29:56.726021+00:00
- run records: 11

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T18:28:05.509571+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T18:28:05.912198+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T18:28:07.992227+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 b62f05bcdcdbdd6b · 2026-10-22T18:28:29.110538+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 e757231c54cc1b90 · 2026-10-22T18:28:42.235311+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 d19ed4e7348166f8 · 2026-10-22T18:28:44.058494+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 561b13162baabbf2 · 2026-10-22T18:28:44.422482+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-22T18:28:51.512570+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 e9896ddf973cb10c · 2026-10-22T18:28:51.670717+00:00
- `timeout 900 python3 tools/verify_selftest.py` -> exit 0 · output sha256 f5703ab57fe9bccc · 2026-10-22T18:29:05.907956+00:00
- `make verify` -> exit 0 · output sha256 02cdf1749f9046f6 · 2026-10-22T18:29:56.726021+00:00

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
- sheet sha256 (of the content above, excluding this line): a11af35e0c8fd1a673fb9573214dd32ac0a089e7a594db20fc04969ca9327f18
