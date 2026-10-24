# PROOF SHEET — slice claim-041-h02b-sev-wiring (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 496cc6111cf16ab12786dfb4676f1d5e1b5b2330
- generated (last record's timestamp): 2026-10-24T09:05:31.392311+00:00
- run records: 14

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-24T08:36:01.270656+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-24T08:36:01.640648+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-24T08:36:04.212711+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 163c9b2959bbdd57 · 2026-10-24T08:37:14.697190+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 642b04b5c41a637e · 2026-10-24T08:37:36.690055+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 77685f37bdc03b7c · 2026-10-24T08:37:50.123702+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 1093f25c9ac4d784 · 2026-10-24T08:37:50.436205+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 babb08f45b8ed6ef · 2026-10-24T08:37:50.651202+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 152633f4291b90a3 · 2026-10-24T08:37:53.667566+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-24T08:38:15.616911+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 2632a4f08b8b19b8 · 2026-10-24T08:38:31.927035+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 04a2d3d3d4b5149e · 2026-10-24T08:38:32.122697+00:00
- `make verify` -> exit 0 · output sha256 b14f8cc74d98a2d3 · 2026-10-24T08:41:01.905104+00:00
- `python3 harness/gate.py --slice claim-041-h02b-sev-wiring --diff origin/main` -> exit 0 · output sha256 b2b8a90a3161a91f · 2026-10-24T09:05:31.392311+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- not verified (LAW-04 — the CLAIM-041 honest limits):
- - the bootstrap transition (the H-02 card's own scope): the CI harness-trusted job
- for THIS PR runs on the base fc8b32e, which predates the wiring — the SEV
- obligation becomes mechanically enforced by CI from the NEXT slice's PR onward;
- this slice's own enforcement is the local PR-mode gate (green at the head) + the
- five-check CI run on the same head. Never a permanent bypass: the transition is
- scoped, independently reviewed (the #76 fresh-context round), and recorded.
- - identity separation is DECLARED, not cryptographic: the fresh-context reviewer
- subagent ran on the same host and OS user as the builder — process-level
- separation only; the separate phase-gate grader remains part of the protocol.
- - base-SIDE additions do not move a merge-base: base-movement staleness rides the
- strict=true required-status binding (up-to-date branches force a new head and
- revalidation at merge) — stated, never claimed closed.
- - the same-host/same-user residual (the mutation floor's BOUNDARY; Q10) is
- unchanged and untouched by this slice.
- - this slice is harness machinery: no product code, no migrations, no C1-C5
- product behavior — the suites' green is machinery evidence, never product proof.
- - the PR merge + post-merge CI observe after the PR opens — recorded in the rule-4
- close row carried by the next slice; never predicted here.
- - the fresh-context reviewer's own not-verified items (the artifacts absent at its
- review head; make verify not run as one command by the reviewer) were true of
- the state it reviewed and are retained in the record 34 + the sev.json.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: d6b8503647dc3061d037c09e2dd41affbe02ed58d7fdb7f51df716936f52fdd6
- reviewed_diff_sha256: ef88bfe2f0a29ca209bfdefe746525275bc98f865841a7c4ea3e8c34b5da479e
- disposition: PASS
- findings: 5 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): ed087f44bb5a38afbcfc49a9ae43666accefada0ffee1b01647d9ad538ead0d8
