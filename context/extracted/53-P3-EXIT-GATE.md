# Record 53 — the Phase 3 exit gate (CLAIM-061)

> STATUS: SESSION ENGINEERING RECORD (2026-11-05; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 77. PR #95 MERGED this session's opening (the CLAIM-060 export/restore machine, under INT-145); the exit-gate PR follows at this slice's end.

## §1 — The #95 close (all observed live via the API)

PR #95 (CLAIM-060 — the export/restore + purge-ledger machine): the five required checks green at the exact final head `7800919` (canonical-layer 127374604712, head-tools 127374605686, harness-trusted 127374605780, harness-suites 127374605501, harness 127374605324) AND on the merge commit `3b5ed28` (canonical-layer 127377458899, head-tools 127377458789, harness-trusted 127377458637, harness-suites 127377458609, harness 127377458100); the merge-gate review D-042 (1a) `5788371151` posted 2026-11-05T16:30:49Z, thirteen seconds before the merge; the merge clean at 2026-11-05T16:31:02Z (no flip race this round — the authorization path ran its checks, the merge proceeded); the protections re-read byte-equivalent after the merge (the five contexts strict, admins enforced, 1 approving review, dismiss_stale, no force pushes, no deletions); the branch deleted; 0 open PRs; only `main` on the remote.

The CI chain: the first round at the finalize head `cf085dd` was REFUSED by the trusted gate (ARV-SEV-003 — the finalize commit's record-52 §3 account rode the reviewed set past the SEV digest; the #93/#94 digest-binds-LAST class observed a THIRD time — harness-trusted 127371777679 + harness 127371777537 failure, the other three green); the re-bind at `7800919` (the digest recomputed over the final content, the report re-validated clean, the sheet re-derived, the LOCAL trusted-gate reproduction green BEFORE the push — the exact S4c path the CI runs). CodeRabbit: skipped (the <10-stars standing state); Greptile: out of credits (the standing state); the host review floor (D-042 (1c)) carried the merge-gate review.

The session's FACT-001 recycle class (the fourth observed): the rig's data directory came up with recycled permissions (0700 lost) + the damaged `pg_notify` subdirectory — re-initdb'd from `pgbuild/rig.sh` (the rig is ephemeral test infrastructure; all state per-run from migrations); all 13 migrations applied; ARV-RIG-001 healthy.

## §2 — The gate's contract (what Phase 3 must prove, and where each proof lives)

PLAN §3.E's exit criteria, each with its evidence home at the final main `3b5ed28`:

1. Work/Source identity and Anchor contracts explicit; owner blockers resolved/isolated at exact scopes — RTM §2 (the entity contracts), §7 (the open-question boundary register: Q11/Q12/Q8's exact scopes); the Q11 baseline pinned at IMP-02/03; the Anchor contract at ANC-01..10 + the Q8 synthetic-corpus spike.
2. The real client/backend path: ingest → Highlight with valid Anchor → Bookmark → Note → keyword search — the §1.6 checkpoint (CAP-01..23), the family suites (HLG/BMK/NTE), the search arm (KWR-01..10); THE EXIT-GATE RE-PROOF: the uncoached clean-clone acceptance agent (§3).
3. The crash/restart/replay/offline fault matrices — SYS-08's matrix at SYN-01..17 (the SEV-repair pins included); the import crash matrix IMP-05..10; the capture checkpoint's two crash points.
4. Local-durable and server-durable distinct; sync's recoverable outbox states — RTM §4.2's one-commit-point law; the two outboxes (migration 0012); the state machine enforced at the substrate.
5. Every write attributed and owner-scoped; two-owner tests + independent reads — SYS-03's matrix (CAP); RLS on every authoritative table; arv_read the independent auditor (the export equality's read role).
6. Revisions immutable, tombstones work, governed purge effective after restore — HLG/BMK/NTE revision machines; EXP-08's purge-then-restore (the ledger WINS).
7. Derived passages/indexes rebuild; stale derivations never silently current — EXT's complete-or-failed generations; KWR's rebuild + the query-time tombstone parity; EXP-09's post-restore rebuild.
8. Export/restore satisfies the equality contract — EXP-01..15.
9. Every SYS requirement traces to tests + Proof Sheet evidence; every slice passing SEV; known-bads refused with named codes — RTM §1's traces + §8's slice-acceptance table; the runs dirs' proof sheets + sev.json per slice; the KB matrix.
10. Local checks + the recorded required CI checks at the final revision; THE UNCOACHED CLEAN-CLONE TASK AGENT + THE SEPARATE GRADER (no P0/P1) — §3/§4 of this record.
11. Not-verified items explicit — §5 + the per-slice notverified.txt registers.

## §3 — The uncoached clean-clone acceptance agent (SYS-09's cold-start form)

(in flight — the agent's report lands here with its verbatim task, its commands, and its observed outcomes)

## §4 — The separate grader (the all-rows walk + the acceptance grade)

(in flight — the grader's report lands here: every SYS row walked to its tests/proof/SEV, the acceptance run graded, the verdict)

## §5 — The gate verdict + the not-verified register

(in flight — lands at the finalize)
