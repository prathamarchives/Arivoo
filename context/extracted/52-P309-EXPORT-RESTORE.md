# Record 52 — P3-09: the export/restore chain (CLAIM-060) + the #94 close account

> STATUS: SESSION ENGINEERING RECORD (2026-11-05; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 76. PR #94 MERGED this session (the CLAIM-059 outbox/sync machine, under INT-145); the CLAIM-060 PR follows at this slice's end.

## §1 — The #94 close (all observed live via the API)

PR #94 (CLAIM-059 — the outbox/sync/recovery machine): the five required
checks green at the exact final head `daafa9e` AND on the merge commit
`7df713b` (canonical-layer 127298938443, head-tools 127298938522, harness
127298938418, harness-suites 127298938526, harness-trusted 127298937946);
the merge-gate review D-042 (1a) `5786360343` posted before the merge; the
recorded flip/merge/restore — the FIRST merge attempt raced the protection
flip's propagation and was refused cleanly ("At least 1 approving review" —
the #92 eventual-consistency class, now observed twice), the recovery the
same: the flip with the immediate read-back polling to 0, the settlement
window, the merge clean; the protections re-read byte-equivalent after the
restore (the five contexts strict, admins, 1 approving, dismiss_stale, no
force pushes, no deletions); the branch deleted (204); 0 open PRs; only
`main` on the remote. Merged 2026-11-05T14:20:03Z.

The CI chain: the first round at `3d40a92` was REFUSED by the trusted gate
(ARV-SEV-003 — the finalize commit's record-51 §3 account rode the reviewed
set past the SEV digest; the exact digest-binds-LAST class #93 hit); the
re-bind at `daafa9e` (the digest recomputed over the final content, the
report re-validated clean, the sheet re-assembled, the LOCAL trusted-gate
reproduction green BEFORE the push — the base's machinery over the tree, the
same S4c path the CI runs). CodeRabbit: no automatic review (the <10-stars
standing state); Greptile: out of credits (the standing state); the host
review floor (D-042 (1c)) carried the merge-gate review.

## §2 — CLAIM-060's card (P3-09) and the contract set

PLAN's P3-09 card; RTM §3.7 (the export/restore state machine:
manifest_complete → restored_pending_validation → restored →
fully_operational, with the failed classes: missing blob, malformed,
interrupted, the unreadable-ledger FAIL-CLOSED rule); SYS-10's purge rule
(the destination's current purge ledger wins over older archive content — a
purge cannot be resurrected by restore); D-029 (the purge/backup expiry
boundary); the 2026-10-16 review's export/restore gap (the card's named
origin).

The design: a versioned EXPORT (a manifest JSON: the format version, the
owner, the exported tables' rows in a canonical sorted form, the blob
references with their digests, the canonical state hash over the whole) +
the blob copies (the rig's filesystem class — the bytes copied into the
archive so the restore is self-contained, the digest re-verified at
restore); the RESTORE into a clean migrated destination: the purge-ledger
reconciliation FIRST (every archive row whose entity is in the destination's
purge ledger is DROPPED — the ledger wins), then the authoritative rows
inserted (the append-only substrate accepts the INSERTs), the outbox state
carried (the RTM §4.4 authoritative set), the validity checks (every blob
present + digest-matched; the manifest well-formed; the canonical hash
matching), the derived-index REBUILD from the restored authoritative rows,
and the EQUALITY verification through the independent role (arv_read on both
databases: the per-family counts + the canonical state hashes equal).

The purge LEDGER (migration 0013): owner_scope, purged_kind, purged_id,
purged_at, reason, provenance — append-only, RLS-forced. The governed purge
COMMAND stays D-011's (a later slice — the owner-facing erasure flow); this
slice lands the LEDGER + the reconciliation + the export/restore carrying
it. The tests insert ledger rows directly at the substrate (the honest
surface for the reconciliation's proof).

The bounded exclusions: the governed purge command D-011's; the
cross-provider blob story Q12's (the rig's filesystem archive class); no
refactor of the landed families.

## §3 — The slice chain (COMPLETED at the final content head a5356e1 + the finalize)

THE RED (LAW-11): the EXP-01..10 suite committed in its RED form at `f6cf5fb`
(machinery-absent ARV-TEST-000, red-01.txt; the typed record bound to the
RED commit). THE GREEN at `190f4b0`: migration 0013 (the purge ledger) +
harness/export.py + the registration; the implementation-cycle amendments
recorded (EXP-04's migrated destination; EXP-10's per-row trigger lesson).

THE THREE-ROUND SEV CHAIN: ROUND 1 (agent exp-sev-r1) BLOCKED — F1 (P1, the
restore-side TOCTOU: a ledger row inserted mid-flight silently overridden)
+ F2 (P1, the promised ON CONFLICT ledger merge never implemented) + F3/F5
(P2s, the reference cascade + the command_log-proxy gate) — repaired
RED-first at `e006897`/`a18a0e2` (EXP-11..14, red-02.txt); F4 (P2,
integrity≠authenticity) ROUTED (the trusted-boundary signature rides the
governed-purge family). ROUND 2 (agent exp-sev-r2) verified F2/F3/F5 but
PROVED F1's SERIALIZABLE form insufficient (a lone rw-edge forms no SSI
cycle for a read-committed writer — 2 of 6 interleavings illegal, the abort
unreachable) and found F6 (the anchor-kind domain bug — the dangling FK
refusing the whole archive); repaired at `a5356e1`: the ACCESS EXCLUSIVE
reconciliation lock (migration 0013's UPDATE grant as the lock enabler —
the ARV-PRG-001 trigger remains the append-only law, firing for every role
incl. the superuser), the anchor-domain direct mapping, EXP-11 strengthened
to the discriminating mid-phase form, EXP-15 pinning the anchor cascade
RED-first (red-03.txt). ROUND 3 (agent exp-sev-r3) PASS zero open P0/P1 —
the decisive DB-level clock_timestamp ordering proof (the blocked writer's
INSERT returning 357µs after the lock release = the restore's COMMIT),
all 13 tables byte-equal, EXP-01..15 green, the law at 328/400 + 599/800.

THE MEASURED SET: 13 run records — EXP-01..10 x3 + verify (the pre-repair
tree), EXP-01..14 x3 + verify (the round-1-repaired tree), EXP-01..15 x3 +
verify (the final tree), and the recorded PR-mode gate at the final
artifact tree (exit 0). The sheet re-derives byte-identically over all
records (the digest binds LAST).

NEXT: the push → the PR → the five checks → the merge-gate review (D-042
(1a)) → the merge under INT-145 → the post-merge verification → the Phase 3
exit gate → P4-00.
