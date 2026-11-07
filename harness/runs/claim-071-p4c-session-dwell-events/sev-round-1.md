# SEV round-1 — CLAIM-071 / P4-C slice two (the session/dwell events surface)

- **Agent label:** agent-5e8a71c4
- **Date:** 2026-11-07 (round 1, fresh context, adversarial)
- **Slice:** `slice/claim-071-p4c-session-dwell-events` — D-010's durable behavior data as the reading-session checkpoint events
- **Base:** `fd6fb9f` (origin/main, CLAIM-070's merged head) — **Head at review:** `f425495`
- **Chain:** `fd6fb9f` → `6bdb561` (commit A) → `7804737` (RED) → `1577571` (red record) → `f425495` (GREEN)

## 1. Verdict

**BLOCKED** — one open P1 (the sync dead letter). Zero P0s. All eight claimed surfaces otherwise verified live and green.

## 2. Findings

- **F-071-1 (P1, open at round 1 — REPAIRED at `fc50d3b`, verified by round 2): record_session rides
  the client outbox but has NO sync delivery arm — every session event's outbox row terminally
  dead-letters ARV-SYN-000.** `record_session` was added to `_SYNC_COMMANDS` (commands.py:64), so
  every committed event enqueues a sync-intent row — but `sync.py _cli_args` had no `record_session`
  branch, so the walk hit the fall-through `ARV-SYN-000: the command record_session is not in the
  outbox-carrying set — never delivered`. Observed live on the reviewer's own two-DB rig: all 10
  record_session outbox rows went `state=failed reason=ARV-SYN-000` while import rows delivered —
  D-010's durable behavior data never reaching the server site. The exact defect class the repo
  established law for at CLAIM-066 (the save_position dead-letter P1, repaired in-round with the
  SYN-18 "never a dead letter in the outbox-carrying set" pin).
- **F-071-2 (P3, routed): the dwell bounds and the remaining substrate CHECKs are pinned
  structurally but not exercised by the suite's own probes** (the command-boundary bounds 0 /
  negative / >86400000; the hostile substrate CHECKs for the dwell shape, the inverted span, the
  ordinal floor, the actor vocabulary — all verified live by the reviewer, every one refusing
  correctly).
- **F-071-3 (P3, routed): the command's advisory-lock key uses the raw caller-spelled source id
  while the 0015 trigger uses the canonical uuid text** — a non-canonical spelling takes a divergent
  command-level lock; the substrate's canonical-lock + max+1 backstop keeps ARV-SES-007's law in
  every traced interleaving (worst case a typed SES-007 refusal, never corruption). save_position
  shares the raw-spelling form. Consistency note only.
- **F-071-4 (P3, routed): a non-uuid `--source-id` refuses ARV-CMD-010 with a misleading repair
  hint** — byte-identical to the save_position precedent; a pre-existing shared class, not
  introduced by this slice.
- **F-071-5 (P3, owner-accepted-debt): the provenance columns (owner_scope, run_id,
  idempotency_key) are unconstrained caller text** — the substrate-wide LAW-20/21 convention on
  every table since 0001; the D-010 boundary judged genuinely CLOSED at this surface (every data
  channel the slice introduces is a closed CHECK, an int, or a uuid).

## 3. What was run (the round's own table, summarized)

The suite 6/6 PASS (output sha byte-matching run-01..03); the RED reproduced at the archived tree
(exit 1, ARV-TEST-000, machinery-absent flags matching red-01.txt exactly); the sha chain verified
at every link; `make verify` exit 0 corroborated. Live probes on the reviewer's own scratch rigs:
all four event kinds + the ack grammar; NINE out-of-vocabulary kinds refused ARV-SES-004 with D-010
named (keystroke, search_query, agent_prompt + mouse_move, page_scroll, voice_input,
scroll_delta, focus_change, click — zero rows, zero outbox rows); the dwell shape/bounds (the
boundary 86400000 commits, 0/−5/86400001 refuse); the no-oracle byte-identity; the substrate
guards (UPDATE/DELETE, skipped ordinals, cross-source generations, the vocabulary CHECK by name,
RLS cross-owner writes, arv_read write permission); the read bounds + the empty owner + the keyset
walk; B's isolation; the re-extraction provenance; the position composition; the crash arm (exit
2, effect committed, replay convergence); the two-DB sync run (the P1 observed); the full schema
audit (14 columns, zero DEFAULTs, RLS FORCED, the grants, the FKs, the UNIQUE); `migrate.py
--verify` (15 migrations, checksums match, the baseline-bump directive present); the TODO sweep
clean; the capability row.

## 4. The amendments judged

Both GREEN-commit test amendments judged **additive/strengthening**: (a) the crash arm's dwell
forwarded (the RED draft omitted `--dwell-ms`, making the pin unsatisfiable — ARV-SES-005 refuses
before the crash vocabulary fires; the convergence replay also carries the dwell for the idempotent
body); (b) the ordinal arithmetic corrected (the RED draft's `@6`/`events=7` contradicted its own
`rows_after_crash == "6"` pin; `@5`/`events=6` is the arithmetically consistent expectation). No
pin weakened.

## 5. The disposition

The P1 repaired at `fc50d3b` (the sync delivery branch + the additive SYN-19 pin, RED-first with
the true RED observed at the unrepaired tree). The P3s routed to notverified. Round 2 followed at
the repaired tree.
