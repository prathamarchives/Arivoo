# PROOF SHEET — slice claim-061-p3-exit-gate (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): a287ce199cc0b20dfa9f074ac386cc65acbce547
- generated (last record's timestamp): 2026-11-05T19:40:07.510243+00:00
- run records: 5

## Run records (command, exit, output digest)
- `make verify` -> exit 0 · output sha256 cce0bf7b5092f2e4 · 2026-11-05T17:49:17.240602+00:00
- `make verify` -> exit 0 · output sha256 0c4c7361082ad770 · 2026-11-05T17:54:15.424907+00:00
- `make verify` -> exit 0 · output sha256 7bb9b745dec0e0b3 · 2026-11-05T17:59:17.880682+00:00
- `SLICE=claim-061-p3-exit-gate GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 3ca1a8bbf2939b17 · 2026-11-05T19:34:24.131174+00:00
- `ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-061-p3-exit-gate python3 -I tools/trusted_gate_anchored.py --repo $PWD --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 5832f02f2088360e · 2026-11-05T19:40:07.510243+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-061 / the Phase 3 exit gate
- (LAW-04; never empty-by-omission)
- WHAT THIS GATE PROVES: every PLAN §3.E exit criterion at the final main
- 3b5ed28 — the full local verification (three recorded make verify runs, exit
- 0; the gate GREEN; the canonical layer 54/0); the RTM all-rows walk executed
- INDEPENDENTLY (grader part 1: every SYS-01..11 row to its named suites RUN
- by the grader itself, all exit 0; 13/13 slice evidence dirs with
- disposition=PASS SEV reports; the KB spot-checks); the uncoached
- clean-clone acceptance path (a fresh-context agent, a clean clone at
- 3b5ed28, two empty databases, a user-like task with no coaching — the full
- capture-and-retrieve walk, the restart byte-identity, the export/restore
- equality, the truthful durability reads, six abnormal events — NO P0/P1);
- the separate grader's final verdict PASS (seven independent probe groups,
- the coverage table, the re-judged findings).
- NOT VERIFIED — the honest limits:
- - The independence limit (PLAN §D-9): the builder, the acceptance agent,
- and both graders ran on the same host and model family. Context separation
- is the protocol's design; it is not cryptographic proof of distinct
- substrates. Reported honestly, never overclaimed.
- - The owner-facing purge flow was NOT walked by the acceptance agent — it
- does not exist (D-011's bounded deferral; the ledger + reconciliation are
- the Phase 3 deliverable). The "governed purge remains effective after
- restore" criterion is proven at the suite level (EXP-07/10..15), never by
- a user-surface walk.
- - The real cross-host network surface and the cloud provider boundary
- remain Q12's (the rig models the two durability domains as two databases
- on the loopback boundary; no provider claim is made or graded).
- - Phase 4+ surfaces (the reader client, journal blocks, @-reference
- resolution states, scoped agent reads, pagination) are NOT graded here —
- they are Phase 4's cards (P4-00..F).
- - The CI evidence is the recorded API snapshot at write time (INT-104's
- class); the merge-gate re-observation is the live proof.
- - The routed P2/P3 register (six repairs) is recorded in record 53 §5 —
- none blocks this gate; each lands in its named P4 home.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: cf3b5548c2a2fcb86e62fd729bc850e9c09eb5fc7cb9378b48892b59ab578462
- reviewed_diff_sha256: c35cf318c6fd44a7f7b42d27fce8809dde5a9baff597e25447b0882e2bb69ef5
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): a6321ee9a1403e107f91424210d4987266bc9b3461430fb4e1daf733aace53d5
