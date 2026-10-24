# PROOF SHEET — slice claim-044-sev-base-side-section (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 964344598c948594f36288f595c26d063fa8731c
- generated (last record's timestamp): 2026-10-24T15:41:30.337005+00:00
- run records: 16

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
- `make verify` -> exit 0 · output sha256 11a5286a54266478 · 2026-10-24T15:38:54.169359+00:00
- `python3 harness/gate.py --slice claim-044-sev-base-side-section --diff origin/main` -> exit 0 · output sha256 b08a3caef7c6da7c · 2026-10-24T15:41:30.337005+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the trusted-leg enforcement of ARV-SEV-009 begins with the NEXT slice's PR (the base c19d497 predates the rule — the recorded bootstrap pattern, the same transition as the original SEV wiring and the section renderer; this slice's own PR is judged by the base's validator).
- - the probe's three stated boundaries (the reviewer's SEV-4 residual): the comment-only marker false-positive (unreachable in this repo's history — the marker's only arrival ec250a1 rides with the renderer code itself); the directory-shaped-proofsheet edge (unreachable for wall-controlled main); the undecidable short-circuit (the sibling ARV-SEV-003 refuses the same condition — fail-closed holds through the named code).
- - the remote CI's five-check run at this PR's head — observed at the PR, never pre-recorded here.
- - the identity limit (LAW-30): the fresh-context reviewer is a subagent on the same host and user — declared independence of context, never cryptographic; the separate grader at the phase gates remains the protocol.
- - the N12 residual (claim-038's notverified) is unchanged; never silently complete by inference from unrelated checks.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 00e6146aff6ccccb4c6a77227921367c76bf645039ecbb03c836e78677e73413
- reviewed_diff_sha256: 98e850ccfc65d7cf60224b684ccdf737d8edde70aba1e55e15c3eeb88c5b5c04
- disposition: PASS
- findings: 6 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 30d3590b6313927e24acbaa9933af50006e9c8b8a73e6cc12337add07619d326
