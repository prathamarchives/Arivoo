# PROOF SHEET — slice claim-062-p400a-truthful-acks (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): d672ec6d90f568f086f17802e72a69c928cd4231
- generated (last record's timestamp): 2026-11-05T22:42:51.824012+00:00
- run records: 11

## Run records (command, exit, output digest)
- `python3 harness/tests/test_contract.py` -> exit 0 · output sha256 6396255bf5ea2367 · 2026-11-05T20:48:49.634928+00:00
- `python3 harness/tests/test_contract.py` -> exit 0 · output sha256 6396255bf5ea2367 · 2026-11-05T20:48:51.714629+00:00
- `python3 harness/tests/test_contract.py` -> exit 0 · output sha256 6396255bf5ea2367 · 2026-11-05T20:48:53.801994+00:00
- `make verify` -> exit 0 · output sha256 4651d02350eef496 · 2026-11-05T20:53:54.976670+00:00
- `make verify` -> exit 0 · output sha256 5f6fe10318935faa · 2026-11-05T20:58:51.415541+00:00
- `python3 harness/tests/test_contract.py` -> exit 0 · output sha256 4d8f5ae13a92503e · 2026-11-05T22:22:04.138805+00:00
- `python3 harness/tests/test_contract.py` -> exit 0 · output sha256 4d8f5ae13a92503e · 2026-11-05T22:22:05.792318+00:00
- `python3 harness/tests/test_contract.py` -> exit 0 · output sha256 4d8f5ae13a92503e · 2026-11-05T22:22:07.444102+00:00
- `make verify` -> exit 0 · output sha256 96378346057152ac · 2026-11-05T22:26:45.619932+00:00
- `SLICE=claim-062-p400a-truthful-acks GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 681098036e02475d · 2026-11-05T22:37:20.164131+00:00
- `ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-062-p400a-truthful-acks python3 -I tools/trusted_gate_anchored.py --repo $PWD --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 1173e868d63be56e · 2026-11-05T22:42:51.824012+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-062 / P4-00a (the
- truthful-acknowledgment contract + the user-facing entry; LAW-04; never
- empty-by-omission)
- WHAT THIS SLICE PROVES: the Phase 3 exit gate's routed register answered at
- the real boundary — the import/extract acks carry SYS-01's durability_rung on
- BOTH forms (the committed and the replayed; the crash-re-drive form verified
- by the SEV round-1 probe); the restore's typed completion names the
- derived-rebuild step (state=restored derived_state=pending_rebuild with the
- two rebuild verbs — RTM §3.7's restored->fully_operational ladder visible at
- the one moment it is needed; the zero-source and all-sources-purged edge
- cases probed truthful); get-capture exposes the anchor_id (the real anchor —
- resolve-anchor answers resolved on it); the search output labels its columns
- (the header always printed; an empty search answers with the header ALONE,
- never pure silence; no consumer in the repo parses the old unlabeled form —
- grepped); migrate.py --help prints usage and exits 0 WITHOUT touching any
- database (verified at a dead port and a nonexistent DB name); the README at
- the repo root carries the runnable day-one path (every command walked
- verbatim by SEV rounds 2 and 3 — every step exit 0; CON-08 pins the
- runnable-shaped class). The SEV three-round chain: round 1 BLOCKED (two P1s
- repaired RED-first + one P2 routed), round 2 BLOCKED (one P1 — the CLAIMS
- scope-cell form — repaired with the parser's own check re-observed GREEN),
- round 3 agent-con-sev-r3 PASS zero open P0/P1 (its own probes: the rogue-
- path sensitivity — the repair not vacuous; the comma-annotation and the
- commaless-annotation defect forms both reproduced; the ack's truth DIRECTION
- probed at the DB substance level — the rung's claim true, not decorative;
- the ladder's two named verbs genuinely completing restored->fully_operational).
- NOT VERIFIED — the honest limits:
- - The capture/bookmark/note families' REPLAYED acks and record_event's ack
- carry no durability_rung — PRE-EXISTING at origin/main (byte-identical,
- never a regression by this slice) and ROUTED to P4-00b's DTO-freeze card
- (the SEV round-1 F3 finding; PLAN's P4-00b line carries the routing).
- - The live CI five-check run, the GitHub merge path, and the S4c
- trusted-gate reproduction — the push/finalize follows this record; the
- local PR-mode gate + the suite set + the canonical layer are the local
- evidence (the CI run is the authoritative proof at PR time).
- - The uncoached-acceptance-agent form was NOT re-run for the README (SEV
- rounds 2 and 3 walked it themselves, verbatim — a fresh-context
- uncoached re-run is P4-00b's boundary-test concern, where the day-one
- path becomes a permanent suite).
- - Real SIGKILL crash injection against the export/restore arms beyond the
- suites' simulated --crash-at points (the EXP suite's own coverage stands).
- - The mutation-floor and canonical-layer internals (taken as green exits:
- 22 suites + known-bads + gate + canonical 54/0, re-observed at this tree
- by SEV round 3).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 3ea40286b0f38b1681e02fc33c70de880975ef4f75cdb0b2e0335a4cde85e8d1
- reviewed_diff_sha256: 7efad5c2dd8cd8b1e04050ada80d9a1372d0465e9bc9ef74fa19552b09d08abd
- disposition: PASS
- findings: 4 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 3ac0d6ee912e4c75e916ea059b5e1551491210fdb1656027c74cabc40d43117a
