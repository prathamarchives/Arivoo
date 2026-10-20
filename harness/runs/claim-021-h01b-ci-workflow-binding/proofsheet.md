# PROOF SHEET — slice claim-021-h01b-ci-workflow-binding (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 7d86557e5b7f40c68331a97b2475d4e0f2e0950a
- generated (last record's timestamp): 2026-10-20T14:13:30.159365+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 -I tools/trusted_gate_anchored.py --repo $PWD --base /tmp/base-main --phase suites` -> exit 0 · output sha256 64141b11935f0d1e · 2026-10-20T14:12:52.237569+00:00
- `make verify` -> exit 0 · output sha256 787a739761bf806b · 2026-10-20T14:13:30.159365+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the CI harness job's new trusted steps are exercised LOCALLY exactly as the workflow runs them (the anchor step, S1b suites, S4c gate re-root over the real candidate diff) — with the base worktree at main (7d86557); the actual GitHub runner executions are observed at this PR's CI and re-observed post-merge
- - F-003 remains STRUCTURAL and EXTERNAL: GitHub provides no repository setting that stops a pull_request event from using the merge-ref workflow file — this PR's own CI runs THIS workflow edit (the boundary demonstrated live in record 22 §8, catch #12); the trust is the BASE-anchored machinery inside the workflow + owner review of workflow diffs. Observed settings: workflow token permissions read-only + cannot-approve-PRs; branch protection three required checks strict for everyone
- - the -I flips are proven by red-01 (the B2 repro: the shadow payload EXECUTES in the judge under the old launch; inert + refused under -I) + test_10's anchored -I launch since CLAIM-013; the full GREEN-30/30 forgery is the reviewer's preserved evidence (floor-review/)
- - S4b (the candidate's own gate) remains as EVIDENCE; its --skip-suites legality now rests on S1b's trusted suite execution; a candidate that guts its own dispatch reds its S4b while the required check still decides through S1b/S4c
- - the shim removal relies on the base runner's counterpart-name resolution (live since 87ab16b); verified by this rehearsal and the CI runs at this PR head (the canonical-layer job no longer creates the alias)

## Assembly
- sheet sha256 (of the content above, excluding this line): 28d48bf4cacb70bd15c0e911faf55bf346fbd7650ca6f4ed9f1e62df59d03487
