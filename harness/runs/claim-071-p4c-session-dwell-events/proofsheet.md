# PROOF SHEET — slice claim-071-p4c-session-dwell-events (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 5a99c3de3cec5f6c15ffa82a2456e2ede05d1d95
- generated (last record's timestamp): 2026-11-07T14:00:28.576647+00:00
- run records: 9

## Run records (command, exit, output digest)
- `python3 harness/tests/test_session.py` -> exit 0 · output sha256 8efb2e95327cc070 · 2026-11-07T06:42:54.599623+00:00
- `python3 harness/tests/test_session.py` -> exit 0 · output sha256 8efb2e95327cc070 · 2026-11-07T06:43:00.112531+00:00
- `python3 harness/tests/test_session.py` -> exit 0 · output sha256 8efb2e95327cc070 · 2026-11-07T06:43:05.696491+00:00
- `make verify` -> exit 0 · output sha256 d089dd10a0578d94 · 2026-11-07T06:49:40.535593+00:00
- `make verify` -> exit 0 · output sha256 eff6fe4974f5db70 · 2026-11-07T06:56:02.266210+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 dae07e5a6668a218 · 2026-11-07T07:28:28.607989+00:00
- `make verify` -> exit 0 · output sha256 5831a8bb21d7c2b8 · 2026-11-07T07:34:33.247107+00:00
- `env SLICE=claim-071-p4c-session-dwell-events GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 dd4d5c4ca8f31560 · 2026-11-07T14:00:03.318742+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-071-p4c-session-dwell-events python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 9c27fb7c6eae592b · 2026-11-07T14:00:28.576647+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- CLAIM-071 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json + sev-round-1/2/3.md.
- - NO fine-grained tracing beyond the approved vocabulary (D-010's boundary):
- the closed event set is session_start | checkpoint | dwell | session_end;
- keystroke/mouse-shaped payloads and search-query/agent-prompt kinds refuse
- ARV-SES-004 with D-010 NAMED. The boundary is judged CLOSED at this surface
- (round 1's F-071-5: every data channel the slice introduces is a closed
- CHECK, an int, or a uuid).
- - NO journal/blocks surface (the following P4-C slice); no reader-client work
- (P4-B's separate repo).
- - SEV round-1 F-071-2 (P3, routed): the dwell bounds and the remaining
- substrate CHECKs (the dwell shape, the inverted span, the ordinal floor, the
- actor vocabulary) are pinned structurally but not exercised by the suite's
- own probes — every one verified live by the round-1 reviewer, all refusing
- correctly; the suite-exercised forms remain the named follow-up.
- - SEV round-1 F-071-3 (P3, routed): the command's advisory-lock key uses the
- raw caller-spelled source id while the 0015 trigger uses the canonical uuid
- text — a non-canonical spelling takes a divergent command-level lock; the
- substrate's canonical-lock + max+1 backstop keeps ARV-SES-007's law in every
- traced interleaving (worst case a typed SES-007 refusal, never corruption).
- save_position shares the raw-spelling form — the consistency note, its own
- slice.
- - SEV round-1 F-071-4 (P3, routed): a non-uuid --source-id refuses
- ARV-CMD-010 with a misleading repair hint — byte-identical to the
- save_position precedent; a pre-existing shared class, not introduced here.
- - SEV round-1 F-071-5 (owner-accepted-debt): the provenance columns
- (owner_scope, run_id, idempotency_key) are unconstrained caller text — the
- substrate-wide LAW-20/21 convention on every table since 0001.
- - SEV round-2 F-071-R2-4 (P3, routed): the amendment note's "committed
- WITHOUT its check() call" wording — the reflog shows a clean linear chain;
- the silent-pass form was a working-tree state reconstructed by the reviewer,
- not a commit. The substance honest and reproducible (both forms
- reconstructed).
- - SEV round-2 F-071-R2-5 (P3, routed): the auto-generated substrate CHECK
- names (reading_session_check, _check1) — the 0014 house convention
- (unnamed CHECKs); only the D-010 vocabulary CHECK is deliberately named and
- pinned by name. Cosmetic; precedented.
- - SEV round-3 F-071-R3-1 (P1, REPAIRED at 3a5c9d0): the label divergence —
- the branch slug carried -events while the run-dir label did not; repaired
- by the run-dir rename + the CLAIMS/scope cell alignment; the sev reports'
- own prose left as written (the divergence they named is the finding's own
- evidence). Verified by the exact machinery that refused: the PR-mode gate
- green under the corrected label + the trusted-gate reproduction (run-08/09).
- - The session-event rows are the RECORDED facts only (the serving-generation
- binding as written) — the behavior history is provenance, never retargeted;
- no aggregation/analytics surface is claimed (none exists).
- - The suite's scratch-dir litter (mkdtemp prefixes): the standing cosmetic
- class (the claim-069/070 notverified notes) — the DB is always dropped in
- finally, the temp dirs are not.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: f8bf109104719f2f9ab45c04476051bd78cf6ee9f6605c32612456f9646d4c62
- reviewed_diff_sha256: 0967194337bd4264ae9620123a8b94375290736a1a356c03c84081f378bf9b4d
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 56ff96b782c82f44cbbb8b1cb8ba7af4dbab944e94984eda24f38d6144823d80
