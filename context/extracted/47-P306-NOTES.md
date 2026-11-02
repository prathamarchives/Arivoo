# 47 — P306-NOTES
> STATUS: SESSION ENGINEERING RECORD (2026-11-01; the standing do-not-stop chain INT-134/135/138/139/140/141/142 + INT-143; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entries: Task 67 (the #90 round-3 account, written pre-merge with the merge as its Next) + Task 68 (the merge + this opening). PRs: #90 MERGED at `f86e52b`; #91 opens with the P3-06 push.

## 1. What the owner asked (verbatim — owner turn 38, 2026-11-01)

> resume

The session-boundary resume word PLUS the owner-forwarded **continuous engineering execution directive** (the full text preserved verbatim at `context/reviews/arivoo-continuous-engineering-execution-directive-2026-11-01.md` under the standing D-022 banner): the mission restated — take the repository from its current state through ALL remaining Phase 3 requirements, the Phase 3 integrated exit gate, the complete Phase 4 roadmap (P4-00 → P4-F), the actual owner workflow, and the seven mandatory refinement rounds; "This is an execution instruction. Do not stop at writing a plan or identifying findings. Inspect, repair, test, document, review and continue through the next eligible slice."; the first execution order — reconstruct the live state, finish the bookmark move-versus-tombstone concurrency defect with deterministic PostgreSQL tests and close the review chain, complete P3-05's evidence and authorized merge, then P3-06/P3-07/P3-08/P3-09 in the authoritative sequence, the Phase 3 exit gate, then the P4 elaboration from real Phase 3 evidence. The turn is minted as INT-143 (the ledger's numbering section updated in this slice's commit A; the standing-chain class, the INT-142 precedent).

## 2. Starting state (every fact re-observed live, INT-104)

- **main = `f86e52b293be0e6b531440d8e98676b09a289783` = the PR #90 merge** (merged BY THE OWNER `prathamarchives` at 2026-11-01T13:48:14Z via the handoff credential — the recorded single-actor path D-042 element 3: the branch protection's approving-review count flipped 1→0 for the merge then restored 0→1, the protections re-read byte-equivalent after — the five required contexts strict, enforce_admins, dismiss_stale, no force pushes, no deletions; the branch deleted by the owner 13:48:28Z, DELETE 204; 0 open PRs; only `main` on the remote).
- **The post-merge five-check run on `f86e52b` ALL GREEN observed live** (canonical-layer/head-tools/harness/harness-suites/harness-trusted — check-run ids 124867189438/493/514/626/676).
- The merge path honestly named: PR #90 carried NO approving review (all reviews COMMENTED — bots + the owner's merge-gate reviews); the D-042 (1a) round-3 merge-gate review addendum posted 13:47:44Z (review 5728361358, engaging the round-3 diff's five risk areas: the serialization itself, the _spine refactor, the substrate guard, exactly-once under the locked path, concurrent moves); the CodeRabbit 14:43Z outside-diff Major's disposition posted in-thread BEFORE the merge (comment 6558809890, D-042 (1b)); CodeRabbit's round at the final head was the paused-review skip (the best-effort bot class, D-042 (1c) — noted, never silently accepted); Greptile remains the 50-credit trial-exhaustion notice.
- The #90 round-3 account (record 46 §8.3, the slice's runs dir): the RED `4628ee3` (BMK-13's deterministic interleaving observed the violation — the move committed revision 2 AFTER the tombstone) → the GREEN `663ae33` (the spine's `build_txn` locked section + the 0008 revision-append guard) → the records `911010d` → the artifacts `aabe85f` (sev.json PASS zero P0/P1 — the round-3 fresh-context reviewer agent-7c31e9f2, its own probes incl. the RED-tree reproduction, five live two-writer races + a 3-writer round, the five P2 notes F5..F9 dispositioned; the 57-record sheet byte-identical; the recorded PR-mode gate run run-57 exit 0 flanked by a direct GREEN re-run). The five GitHub checks at the exact final head `aabe85f` ALL success observed live before the merge.
- The rig: the user-space PostgreSQL 17.11 on 127.0.0.1:5433 (the sandbox-recycle repair at session entry: the data-directory permissions + the recycle-dropped empty subdirectories recreated — nothing persisted lost; the baseline `python3 harness/tests/test_commands.py` exit 0 GREEN before any edit). The dead stored remote credential found at the first push attempt (the D-025 boundary class, record 46 §8 again): the remote URL rebuilt from the standing handoff credential.
- CLAIM-055's row closed by rule 4 in this commit A (CLAIMS.md); the P3-05 close facts: PR #90 = `f86e52b`, final head `aabe85f`, the full chain above.

## 3. Task and scope

- **CLAIM-056: PLAN's P3-06 card — Note and revision history.** RTM §2.5 item 7 (the Note: "the owner's deep raw thinking. Identity + immutable revisions; explicit, version-aware references to Work/Source/Anchor/Highlight/Note; long-form and Unicode preserved losslessly; the diagram/structured-block serialization contract is NOT frozen here — it requires its own round-trip proof before being called supported, P4-C's reservation") + §2.5 item 9 (Note revisions authoritative) + §3.3's machine (authored-entity revisions + tombstone/restore, the §3.3 alternation at the command boundary AND the substrate — the 0007/0008 precedent) + the §3.2 rungs (every ack `durability_rung=local_durable`) + SYS-02/03 primary (RTM's P3-06 row), SYS-01/04 standing.
- The card's tests mapped: revisions never overwrite history (NTE — immutable revision n+1); duplicate retries (the idempotent spine); competing revisions (no silent overwrite — the serialized transition, the 0007/0008 lesson applied to the note family); dangling refs (the typed refusal at the boundary); owner boundary; crash/restart (the spine's crash points); export/restore (the history complete + rebuildable — the authoritative-state contract is P3-09's to exercise end-to-end; this slice proves the history rows carry everything the export needs).
- THE ACCEPTANCE: "every revision is retrievable, attributable, and referenceable; conflict never silently destroys a revision or claims an untested merge."
- The bounded exclusions: the diagram/structured-block contract (NOT frozen — P4-C's reservation, the card's own condition); the keyword index P3-07's; the outbox/sync rungs P3-08's; the governed purge P3-06/09's (D-011 — tombstone is this slice's, purge is the governed erasure's own); no refactor of the landed highlight/bookmark families (their inline derivations + their build_txn/locked-section shapes stay as landed).
- Plus the rule-4 bookkeeping this commit A carries: CLAIM-055's close row (the merge facts in §2, every one live-observed), INT-143, the five-area STATE re-derivation, AGENTS/PLAN re-derivation, Task 68, this record.

## 4. Results

CLOSED at the finalize commit — the complete cycle observed (every fact from the actual runs, never reconstructed):

- **The RED (LAW-11)**: the NTE-01..14 suite in its machinery-absent form observed at the EXACT predecessor `f86e52b` in a temp worktree (create_note absent, get-note absent, migration 0009 absent; exit 1 ARV-TEST-000; `red-01.txt`), committed at `f0a8125` with the gate.py TESTS registration (sixteen → seventeen suites), the typed red record bound (commit `1861540`), and the pre-implementation assertion-form amendments at `3f66355` (the gen_random_uuid native-uuid probe finding + the BMK-11 pg_catalog forms).
- **The GREEN**: migration 0009 + the note family + the read arms + the crash arms at `eb66caf`; the suite GREEN after the implementation-cycle amendments (the audit reads' row_to_json + newline-only framing — the ANC-10 law applied to the test's own readers; the relative crash counts; the restore-order repair; the pg_get_constraintdef PK read; the NTE-13/14 deterministic park on arv.note_reference — arv.note/arv.command_log are touched by the tombstone's pre-lock path, note_reference is the first post-lock write only a reviser touches); make verify GREEN (the seventeen suites + the known-bad matrix + the gate + the canonical layer 54/0).
- **The measured set**: run-01..20 (the suite ×3 + the sixteen siblings + make verify, all exit 0) at `eb66caf`.
- **The independent rounds**: the test verifier (agent `nte-verifier-r1`, PASS zero P0/P1 — its own 45-check adversarial probe: the 31KB Unicode corpus byte-identical, the psql-meta-command-looking content riding as data, live two-writer races, the crash matrix, the hostile matrix, the schema audits; findings V-1..V-4) + the SEV round 1 (agent `nte-sev-r1`, PASS zero open P0/P1, sev.json validated `[]`; findings F1..F3 — F2 convergent with V-1).
- **The review repairs (all three fixed in-PR at `526c3bd`, D-042)**: (1) the phantom-identity + contiguity guard (V-1+F2: the strengthened `enforce_note_revision_guard` — ARV-NTE-001 phantom / the new ARV-NTE-011 gap refusal); (2) the time-honest lifecycle form (F1: tombstone/restore on the spine's build_txn locked section, the timestamp INSIDE); (3) the canonical lock key (F3: revise_note's boundary lock on hashtext(lower(id)) — claim-055 F5's class closed for the note family). The suite grew to NTE-01..15; make verify GREEN again.
- **The regenerated measured set**: run-21..24 (the repaired suite ×3 + make verify) at `526c3bd`; the SEV round 2 (agent `nte-sev-r2`, PASS zero open P0/P1 — each repair verified FROM BOTH ENDS: the defects reproduced live on the pre-repair tree `eb66caf` (phantom/gap appends landing; the split key visible as two granted advisory locks with a revision committing after the tombstone in its race; the tombstone rendered before the first-committed revision) and the repairs holding on `526c3bd`; one new P2 F4 routed — the landed 0007/0008 families still accept hostile phantom/gap appends, only a NEW migration can repair them, never blocking).
- **The finalize**: notverified.txt + the 26-record sheet (run-25 the flanking re-verify + run-26 the recorded PR-mode gate run) + the sev digest bound at the content head; the push + PR #91 + the five GitHub checks observed live.

## 5. Files changed (the slice, commits A..F)

- Commit A `7310960` + the walls-catch `aed0eac`: the claim + the post-#90 reconciliation (§5 of the opening form).
- Commit B `f0a8125` + B2 `1861540` + B3 `3f66355`: `harness/tests/test_note.py` (the NTE-01..15 acceptance suite), `harness/gate.py` (the TESTS registration), `harness/runs/claim-056-p306-notes/red-01.txt`, `harness/red-records.json`.
- Commit C `eb66caf`: `harness/migrations/0009_note_lifecycle.sql` (arv.note + arv.note_lifecycle + arv.note_reference + the four guards + ARV-CAP-005 + RLS + grants), `harness/commands.py` (the note family: _nte_content/_nte_refs/_nte_check_targets/_nte_ref_stmts/_nte_body + create_note + revise_note(build_txn) + tombstone/restore_note + the CLI + the REGISTRY), `harness/query.py` (get-note/list-notes/get-note-history + the SQL arms + the typed ARV-QRY-003 note refusal), `harness/crash.py` (the four note arms).
- Commit D `526c3bd`: the review repairs — `harness/migrations/0009_note_lifecycle.sql` (the strengthened revision guard), `harness/commands.py` (the canonical lock key + the lifecycle build_txn form), `harness/tests/test_note.py` (the pins: NTE-03 phantom/gap, NTE-05 ARV-NTE-011, NTE-14 pattern + the order pin, NTE-15), `harness/red-records.json`.
- The finalize commits: `context/extracted/47-P306-NOTES.md` (this record's completion), `context/WORKLOG.md` (Task 69), `STATE.md`/`AGENTS.md`/`PLAN.md` (the five-area re-derivation at the finalized state), `harness/runs/claim-056-p306-notes/` (run-01..26, proofsheet.md, notverified.txt, sev.json).

## 6. Commands and external actions (ACTUAL — never reconstructed)

- The rig recycle repair at session entry (the record-46 §2 form): `chmod 700 pgdata` + the empty subdirectories recreated + the stale postmaster.pid removed; `pg_isready` → accepting; `python3 harness/tests/test_commands.py` → exit 0.
- The RED observation: `git worktree add /tmp/arv-pred f86e52b` + the suite copied in + `python3 harness/tests/test_note.py` → `FAIL ARV-TEST-000 ... EXIT=1` (red-01.txt); the worktree removed.
- The RED binding: `make red NOTE=... RED_EXIT=1 RED_CODE=ARV-TEST-000` (bound to `f0a8125`); the two amendment `make red` invocations (B3 + the commit-C cycle + the commit-D cycle — the registry's typed amendment chain).
- The suites: `python3 harness/tests/test_note.py` GREEN at `eb66caf` (after the cycle repairs) and at `526c3bd` (NTE-01..15); `make verify` GREEN ×2 (both trees); the sixteen siblings GREEN individually (run-04..19).
- The measured sets: `python3 harness/proofsheet.py --slice claim-056-p306-notes --record ...` ×24 + the flanking re-verify (run-25) + the recorded PR-mode gate (run-26: `make gate SLICE=claim-056-p306-notes GATE_DIFF=origin/main`, exit 0) + the sheet re-assembly + `--verify` (ARV-PRF-004 PASS) + the flanking direct gate re-run (exit 0).
- The independent rounds: the verifier subagent (its own commands in its report — the 45-check probe + the suite ×2) + the SEV subagents ×2 (their own probes: the suite, make verify, the RED reproduction, the both-ends defect reproductions, the races); `sev.validate_report('claim-056-p306-notes', 'origin/main')` → `[]` after each round.
- The push chain: `aed0eac..1861540` (the RED, PUSH-EARLY), `1861540..eb66caf` (the GREEN), `eb66caf..526c3bd` (the repairs) + the finalize push; the API reads for the five checks at the final head (observed live before the merge).

## 7. Evidence

- CLAIM-056's at `harness/runs/claim-056-p306-notes/`: red-01.txt (the machinery-absent RED at the exact predecessor `f86e52b`); run-01..26.json (the measured sets + the flanking re-verify + the recorded PR-mode gate); proofsheet.md (the 26-record sheet, ARV-PRF-004 byte-identical); sev.json (the round-2 re-bind over the repaired diff — PASS, zero open P0/P1; F1..F3 resolved, F4 routed; the digest binding the content head); notverified.txt (the honest limits + the no-fix dispositions V-2/V-3/V-4 + F4's routing). The SEV chains: round 1 agent-nte-sev-r1 + round 2 agent-nte-sev-r2 (the both-ends reproductions); the test verifier agent-nte-verifier-r1 (its 45-check probe account in the session record §4).

## 8. Failures

- The suite's first GREEN run failed 6/14 (the audit-read framing fragmentation on raw newlines/U+2028 — the pipe-delimited reads + splitlines readers; the absolute-vs-relative crash counts; the restore-order assertion; the information_schema PK visibility under arv_read; the NTE-13/14 park point on arv.note blocking the revise at its state SELECT and the tombstone at its replay check) — all repaired in the implementation cycle, recorded as the typed amendments (the #89/#90 precedent class).
- The review findings F1/F2/F3 (+ V-1..V-4): repaired in-PR at `526c3bd` (§4) with the no-fix dispositions recorded (V-2 trigger precedence — fail-closed either way; V-3 empty content — un-ruled by the card, P4-C's product decision; V-4 the spine's NFC canonicalization — K-04's pinned pre-existing choice; F4 routed — the landed 0007/0008 phantom/gap debt needs its own migration).
- The sandbox rig recycle at session entry (the standing class) — repaired before any work; nothing persisted lost.
- The dead-stored-credential class did NOT recur (the remote URL rebuilt from the handoff credential at session entry; the PAT rotation reminder stays standing until the project completes).

## 9. Unverified items

- The concurrent-reader matrix on the new read arms (serially exercised; the standing class).
- The >3-writer race classes and the 4+ mixed interleavings.
- U+001C/1D/1E (the file/record/group separators) unexercised on the content path.
- NUL remains a NAMED note-boundary refusal (ARV-NTE-009) — the spine-level NUL-literal follow-up stays open (the standing residual).
- The spine's NFC canonicalization (K-04): same key + NFD-equivalent body replays the NFC-recorded note — the pinned pre-existing choice, unprobed beyond the verifier's observation.
- Empty content accepted (V-3): un-ruled by the card; the minimum-length product decision is P4-C's.
- F4 (routed): the landed 0007/0008 families still accept hostile phantom/gap revision appends (command-path unreachable; a new migration required — the named follow-up slice).
- The ARV-SEV-009 undecidable-base regression; the N12 self-test-row extension; the Q8 synthetic-only boundary; the isolation undecidable classes; Q10; the host-level workflow protection — the standing documented residuals unchanged.

## 10. Open decisions

D-014 + Q6–Q12, scopes unchanged (each blocks only its named dependents — RTM §7). The slice opens none and closes none. The governed purge (D-011) stays P3-09's — the tombstone/restore machine landed here, the governed erasure never implemented.

## 11. Next action

The merge chain: PR #91 open with the five GitHub checks observed live at the final head → the review dispositions (D-042 (1b): every thread read in full, every finding dispositioned in-thread BEFORE any resolution) → the merge-gate review (D-042 (1a)) → the owner's merge under the recorded single-actor path → the post-merge verification (the five checks on the merge commit + the protections re-read byte-equivalent) → **P3-07 (the keyword index — CLAIM-057's card) → P3-08 → P3-09 → the Phase 3 exit gate** — NO PAUSE (INT-134/135/138/139/140/141/142/143); the next owner checkpoint is the Phase 3 exit gate's verified completion.

## 12. Session close

This record COMPLETES at the slice's finalize (the convention). The PAT rotation reminder stays standing until the project completes.
