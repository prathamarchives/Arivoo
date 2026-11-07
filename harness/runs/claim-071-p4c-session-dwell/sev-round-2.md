# SEV round-2 — CLAIM-071 / P4-C slice two (the session/dwell events surface)

- **Agent label:** b3f7c2a9
- **Date:** 2026-11-07 (round 2, fresh context, adversarial)
- **Slice:** `slice/claim-071-p4c-session-dwell-events`
- **Base:** `fd6fb9f` (origin/main) — **Head at review:** `fc50d3b` (the round-1 repair)
- **Chain:** `fd6fb9f` → `6bdb561` → `7804737` (RED) → `1577571` (red record) → `f425495` (GREEN) → `fc50d3b` (the round-1 repair)

## 1. Verdict

**BLOCKED** — the round-1 P1 (F-071-1) **verified-repaired** and the D-010 boundary held against
every attack, but two declaration/records findings open: one P1 (the PR-mode scope gate refuses the
branch live) + one P2 (the round-1 SEV report absent from the repo). Zero open P0. Both repairs are
declaration/records-only (no product change, no re-RED needed).

## 2. Findings

- **F-071-1 (round 1, P1): VERIFIED-REPAIRED** at harness/sync.py's `_cli_args` record_session
  branch — verified live on the reviewer's own two-DB rig: acknowledged with
  `server_ref=<srv-src>@1/@2`, the dwell forwarded (server row dwell_ms=12345), the site-local
  generation binding (the two sites' uuids differ), the unextracted server resting RETRYABLE with
  the named ARV-SES-002 (never ARV-SYN-000) and delivering on the next pass after the server-side
  extraction, the ARV-SYN-009 dependency resting retryable. The additive SYN-19 pin GREEN; its RED
  reproduced at the pre-repair combination (FAIL SYN-19, exit 1); the disclosed silent-pass form
  reconstructed (the pin minus its check() call → GREEN asserting nothing).
- **F-071-R2-1 (P1, open at round 2 — REPAIRED in the round-2 repair commit): the CLAIMS.md scope
  declaration omitted two diff paths its own commits touch** — `harness/crash.py` (the GREEN's
  crash-matrix membership) and `harness/tests/test_sync.py` (the repair's SYN-19 pin); observed
  live: the claims check RED ARV-CLM-002. The claim-066 round-1 F2 / round-2 F4 class.
- **F-071-R2-2 (P2, open at round 2 — REPAIRED in the round-2 repair commit): the round-1 SEV
  report did not exist anywhere in the repo** — round 1's findings had no durable in-repo record,
  contrary to the claim-066 repair-commit precedent (the round-1 report rides the repair commit).
- **F-071-R2-3 (P3, routed): the repair tree's measured set (run-06/07) untracked** — content
  verified genuine (run-06's digest reproduced byte-exactly; make verify exit 0 reproduced); they
  land with the artifact finalize (the chain's own order).
- **F-071-R2-4 (P3, routed): the amendment note's "committed WITHOUT its check() call" wording** —
  the reflog shows a clean linear chain; the silent-pass form was a working-tree state, not a
  commit. The substance honest and reproducible (both forms reconstructed by the reviewer).
- **F-071-R2-5 (P3, routed): the auto-generated substrate CHECK names** (`reading_session_check`,
  `_check1`) — the 0014 house convention (unnamed CHECKs); only the D-010 vocabulary CHECK is
  deliberately named and pinned by name. Cosmetic; precedented.

## 3. What was run (summarized)

Both suites green with byte-exact digest reproduction (the session suite 6/6 = run-01..03; the
sync suite SYN-01..19 = run-06); `make verify` exit 0 at fc50d3b; the original RED reproduced; the
repair-RED reproduced; the silent-pass form reconstructed; the reviewer's own two-DB rig proving
the delivery/binding/retryable-recovery/dependency quartet; **the D-010 leak probes through the
outbox replay path** (four poisoned payloads — keystroke, agent_prompt, dwell-on-checkpoint,
dwell-without-ms — all refusing server-side with named ARV-SES-004/005, the server table staying
exactly the clean events, the terminal policy firing only at attempts>=3 with the named reason);
the round-1 P3 spot-checks (the dwell bounds, the substrate CHECK name-map, the no-oracle
byte-equality); the enqueue/delivery sweep (all 15 `_SYNC_COMMANDS` members carry `_cli_args`
branches — the F-071-1 class closed set-wide); the red-record hash closure computed at each commit
(both amendment chains close exactly); the TODO sweep clean.

## 4. The disposition

The two blockers repaired in the round-2 repair commit (the CLAIMS row's two declared paths + the
scope.txt + the round-1/round-2 reports on disk). The P3s routed to notverified. Round 3 followed
at the repaired tree.
