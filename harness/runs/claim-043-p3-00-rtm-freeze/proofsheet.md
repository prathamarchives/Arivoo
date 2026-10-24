# PROOF SHEET — slice claim-043-p3-00-rtm-freeze (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 9083efe2941306dd4478f431cb8b94e121a0f004
- generated (last record's timestamp): 2026-10-24T13:10:09.009025+00:00
- run records: 14

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-24T13:01:32.837910+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-24T13:01:33.241226+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-24T13:01:35.432364+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 163c9b2959bbdd57 · 2026-10-24T13:02:54.675479+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 4753ce3166b87042 · 2026-10-24T13:03:15.458017+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 4605064f661ccab2 · 2026-10-24T13:03:24.059192+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 4fabda62ffdd1fee · 2026-10-24T13:03:24.414978+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 4ff391be99427e0a · 2026-10-24T13:03:24.601305+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 3b7b286ceb1c8c19 · 2026-10-24T13:03:26.927271+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-24T13:03:42.327140+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 2632a4f08b8b19b8 · 2026-10-24T13:04:00.759438+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 8b30348dbfeebfa1 · 2026-10-24T13:04:00.916258+00:00
- `make verify` -> exit 0 · output sha256 ca8b0d938aa0a35a · 2026-10-24T13:06:30.919539+00:00
- `python3 harness/gate.py --slice claim-043-p3-00-rtm-freeze --diff origin/main` -> exit 0 · output sha256 0adcf542f981ec96 · 2026-10-24T13:10:09.009025+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the freeze is ACCEPTED through this slice's review + merge; the independent phase-gate grader walks RTM.md's matrix at the Phase 3 EXIT gate — never claimed done here.
- - the state machines and test paths are PRE-REGISTERED contracts; their proofs land with the implementation slices (P3-01..09) — this slice freezes, it does not implement.
- - the Q11/Q12/Q8 baselines remain owner-gated at their exact registered scopes (RTM.md §7); the Q12 recommendation awaits the owner's ratification — nothing in the frozen contracts depends on the choice.
- - the four recorded P2 debts (the §6 conflicted-trigger label; §3.4's terminal failed vs PLAN P3-08's letter; the two derived-entity enums' distinguishing note; OBS-1's pre-existing NORTH-STAR layer-2 wording) each carry their named revisit — P3-08/P3-03/P3-07 card time and the owner's Q11 gate.
- - the remote CI's five-check run at this PR's head — observed at the PR, never pre-recorded here.
- - the identity limit (LAW-30): the reviewer is a fresh-context subagent on the same host and user — declared independence of context, never cryptographic; the separate grader at the phase gates remains the protocol.
- - the N12 residual (claim-038's notverified) is unchanged; never silently complete by inference from unrelated checks.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 470d8df1690430500c8c651cc3d05def0e388677196e2bedd2cb061dc279aa72
- reviewed_diff_sha256: e6bd9de4e5671365c8f7d78779c0615959cdd09d0db322278bd1fa4b6ec7cd43
- disposition: PASS
- findings: 10 (open P0/P1: 0)
- not-verified entries: 7

## Assembly
- sheet sha256 (of the content above, excluding this line): b297a72b49427a5c6b1f75c90416ba3ab2a2ee76c1446ec0e648b05cb076aebc
