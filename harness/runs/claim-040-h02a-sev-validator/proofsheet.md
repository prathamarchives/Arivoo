# PROOF SHEET — slice claim-040-h02a-sev-validator (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 5f47a6247be55396790bb3e3b1bece962c658b4f
- generated (last record's timestamp): 2026-10-24T07:03:11.209400+00:00
- run records: 13

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-24T07:00:07.195498+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-24T07:00:07.567173+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-24T07:00:09.751598+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 86b36062c4f3999f · 2026-10-24T07:00:45.459448+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 b3f00a6c200a9bdd · 2026-10-24T07:01:05.972190+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 973fc2285eef6b98 · 2026-10-24T07:01:11.288697+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 856409f17fac817c · 2026-10-24T07:01:11.685138+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 2c891f1bdf213996 · 2026-10-24T07:01:11.880636+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 f66bbe66738fd1ee · 2026-10-24T07:01:13.576730+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-24T07:01:27.509883+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 6c44222f4a71abc3 · 2026-10-24T07:01:37.613431+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 04a2d3d3d4b5149e · 2026-10-24T07:01:37.768651+00:00
- `make verify` -> exit 0 · output sha256 dfe86213e9fd4450 · 2026-10-24T07:03:11.209400+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- not verified (LAW-04 — the CLAIM-040 honest limits):
- - the GATE does not yet enforce the SEV obligation: the gate step, the KB-SEV matrix,
- the dispatch/trusted integration cases, the Proof-Sheet SEV section, and the
- PLAN/LAWS activation updates are the part-2 slice (CLAIM-041). Until it lands this
- module is exercised by its suite and labeled not-mechanically-enforced (the H-02
- card's own transition label) — never claimed live at the gate.
- - identity separation is DECLARED, not cryptographic: ARV-SEV-007 refuses the same
- builder/reviewer string; a differing string proves nothing about the context behind
- it. Fresh-context execution and the separate grader remain the protocol.
- - base-SIDE additions do not move a merge-base: base-movement staleness rides the
- strict=true required-status binding (up-to-date branches force a new head and
- revalidation at merge) — stated, never claimed closed.
- - this slice is a tools/harness slice: no product code, no migrations, no behavior of
- the C1-C5 product claims — the suites' green is machinery evidence.
- - the same-host/same-user residual (Q10, the mutation floor's BOUNDARY) is unchanged.
- - the PR merge + post-merge CI observe after the PR opens — recorded in the rule-4
- close row carried by CLAIM-041; never predicted here.

## Assembly
- sheet sha256 (of the content above, excluding this line): 93549c894db7a192376c612adc00bee485a6201b68d7caa9aff4b7f4728e1d6e
