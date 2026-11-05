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

## §3 — The slice chain (in flight; extended as it lands)

The RED (the EXP suite at `7df713b`, machinery-absent ARV-TEST-000) → the
GREEN (migration 0013 + harness/export.py + the registration) → the measured
set → the SEV round → the artifact re-bind → the push → the PR → the five
checks → the merge-gate review → the merge under INT-145 → the post-merge
verification → the Phase 3 exit gate.
