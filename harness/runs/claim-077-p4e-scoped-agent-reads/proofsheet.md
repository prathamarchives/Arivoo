# PROOF SHEET — slice claim-077-p4e-scoped-agent-reads (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 233822644e196862e68b839c7bfa260a2686b24c
- generated (last record's timestamp): 2026-11-11T16:20:55.391885+00:00
- run records: 26

## Run records (command, exit, output digest)
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:11:55.050421+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 1 · output sha256 13f79a0036d820c9 · 2026-11-11T14:11:59.426110+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 1 · output sha256 29cc4ffdf74db7c5 · 2026-11-11T14:12:04.148738+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:13:40.317341+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:13:46.146653+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:13:52.543053+00:00
- `make verify` -> exit 2 · output sha256 5ed2c02c5cabac20 · 2026-11-11T14:17:49.300381+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:35:08.873127+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:35:14.886496+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T14:35:20.787841+00:00
- `make verify` -> exit 0 · output sha256 0f4994b395fe97dc · 2026-11-11T14:42:42.405572+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T15:08:17.041688+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T15:08:22.839483+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 94d65b635b13068e · 2026-11-11T15:08:28.773235+00:00
- `make verify` -> exit 0 · output sha256 92f23c8909248d9a · 2026-11-11T15:15:37.030231+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 ccdfa199994d21d0 · 2026-11-11T15:37:01.222059+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 ccdfa199994d21d0 · 2026-11-11T15:37:07.465213+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 ccdfa199994d21d0 · 2026-11-11T15:37:13.476410+00:00
- `make verify` -> exit 0 · output sha256 d1ecc443b39f4f1d · 2026-11-11T15:44:30.972676+00:00
- `env SLICE=claim-077-p4e-scoped-agent-reads GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 68c1bba86ca6ec92 · 2026-11-11T15:54:34.630348+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-077-p4e-scoped-agent-reads python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 271bead3ffffc462 · 2026-11-11T15:55:03.558280+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-077-p4e-scoped-agent-reads python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 80ab90743178db3f · 2026-11-11T15:55:42.619996+00:00
- `python3 harness/tests/test_agent_access.py` -> exit 0 · output sha256 ccdfa199994d21d0 · 2026-11-11T16:06:31.865574+00:00
- `make verify` -> exit 0 · output sha256 bafbd4c3a46ad6b9 · 2026-11-11T16:13:27.378663+00:00
- `env SLICE=claim-077-p4e-scoped-agent-reads GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 39862538d07dc4a2 · 2026-11-11T16:20:35.587855+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-077-p4e-scoped-agent-reads python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 e0a6ffe9e1687ccf · 2026-11-11T16:20:55.391885+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - CLAIM-077 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json + sev-round-1.md + sev-round-2.md.
- - - F-077-4b (P3, noted, no behavior impact): the one-transition guard refuses even a
- same-value no-op UPDATE on a live credential with the "cannot be cleared" wording
- — stricter than claimed, fail-closed; the wording nuance recorded by round 2.
- - - the historical amendment note in red-records.json still carries the pre-repair
- "alphanumeric" wording (the record of what amendment #3 said at 79b5f43 — append-only,
- the live docstring the corrected truth; the code enforced non-dash at that tree too).
- - - Q10's honest boundary (the access-shape surface, never workflow-tamper hardening):
- the hash comparison non-constant-time (named, not measured); the token visible to
- local ps on a multi-user host (the argv form; the natural home for a non-argv form
- is the MCP wrapper — P4-E slice two); no rotation/expiry windows (a future increment,
- owner-gated); the minting policy and any server-deployment scoping stay owner-gated.
- - - no MCP wrapper (P4-E slice two — the same retrieval core behind the protocol
- adapter); no write scopes (READ-ONLY at first, per the row's own letter); no
- response-budget machinery beyond the shared page bounds (Phase 5's retrieval
- increments — the budget at this phase IS the page-bound law, recorded, never
- overclaimed); no multi-owner credential sharing; no reader-client work (P4-B's repo).
- - - no concurrency or DoS claims tested (single-client rigs; the classes belong to the
- spine's prior families); the revoke's read-before-BEGIN shape reasoning-verified only
- (the worst case a typed ARV-AGT-004 refusal, never a wrong state — round 2's limit).
- - - the invalid-token ATTEMPTS are not audited (no attribution exists for an unknown
- credential — no audit row can land; the refusals are fail-closed and loud, but
- un-attributed by construction).
- - - the standing family-wide classes carry forward unchanged: the F-072-1 _nte_canon_id
- pattern, the F-074-1 leading-dash argv-value family (the minted token now structurally
- unable to hit it — the first-char constraint — but the family itself stays routed),
- the F-073-6 import staging residue, F-075-3/F-076-1..4 (the substrate grammar owner's
- slice), F-075-5 (resolve-anchor's purge-unawareness — D-011's slice).
- - - the SEV rig observation (outside the repo): ~11 stale debug scratch DBs from the
- author's own debugging remain on the shared rig (arv_agtdbg*/agtdebug*/ntr16dbg*/
- d042probe*) — cosmetic rig hygiene, noted by round 2, no shared state affected.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 775cfef45d03e1981dfcdc49ef600d2623cf4f195c1e574c43f4611e1117d8b4
- reviewed_diff_sha256: 13023b93deb6798b65af48ae78205504d601e8dd13c4b12629e76ce07d54533a
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 8

## Assembly
- sheet sha256 (of the content above, excluding this line): 21b2844edc3d719b0a491dcadb1486a6eb2103c8f598335c39f3850337d0f16d
