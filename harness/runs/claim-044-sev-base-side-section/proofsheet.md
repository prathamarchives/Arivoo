# PROOF SHEET — slice claim-044-sev-base-side-section (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 097ddd8d0c99a6562cceade1c504f7ee9407fae9
- generated (last record's timestamp): 2026-10-24T15:16:18.073868+00:00
- run records: 14

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-24T15:07:16.148939+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-24T15:07:16.552413+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-24T15:07:19.153579+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 791ff1faab1f66be · 2026-10-24T15:08:40.731730+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 947db2d58b6ec34a · 2026-10-24T15:09:06.961015+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 3393297796965960 · 2026-10-24T15:09:21.573300+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 70dc51643694a29f · 2026-10-24T15:09:21.867057+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 4ff391be99427e0a · 2026-10-24T15:09:22.103637+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 72e7284734409332 · 2026-10-24T15:09:25.622066+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-24T15:09:47.869911+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 f79932f6fc02607d · 2026-10-24T15:10:05.846925+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 65d28a02e88932b2 · 2026-10-24T15:10:06.006995+00:00
- `make verify` -> exit 0 · output sha256 6578646789cfb9cc · 2026-10-24T15:12:51.340140+00:00
- `python3 harness/gate.py --slice claim-044-sev-base-side-section --diff origin/main` -> exit 0 · output sha256 c56306132c971d31 · 2026-10-24T15:16:18.073868+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the trusted-leg enforcement of ARV-SEV-009 begins with the NEXT slice's PR (the base c19d497 predates the rule — the recorded bootstrap pattern, the same transition as the original SEV wiring and the section renderer; this slice's own PR is judged by the base's validator).
- - the probe's three stated boundaries (the reviewer's SEV-4 residual): the comment-only marker false-positive (unreachable in this repo's history — the marker's only arrival ec250a1 rides with the renderer code itself); the directory-shaped-proofsheet edge (unreachable for wall-controlled main); the undecidable short-circuit (the sibling ARV-SEV-003 refuses the same condition — fail-closed holds through the named code).
- - the remote CI's five-check run at this PR's head — observed at the PR, never pre-recorded here.
- - the identity limit (LAW-30): the fresh-context reviewer is a subagent on the same host and user — declared independence of context, never cryptographic; the separate grader at the phase gates remains the protocol.
- - the N12 residual (claim-038's notverified) is unchanged; never silently complete by inference from unrelated checks.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: b85d5c94ee855d914ba2ad30f15272018f780a25135323a97ed4d1165836bb54
- reviewed_diff_sha256: 82b4e2a0650b3c6b8bfe8545f13d1a27774350f32c2014f5ec3914099b3012d2
- disposition: PASS
- findings: 4 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): c752d526b54a3736e9fbd1d376e2a2760917ff6be4a5da7fc947d5c2a2ea2d2e
