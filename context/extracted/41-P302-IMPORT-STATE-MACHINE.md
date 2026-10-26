# 41 — P3-02: the import state machine + the recovery walk (CLAIM-050)

Session 31 continuation (the standing do-not-stop chain INT-134/135/138/139/140);
the turn-36 execution directive: P3-01's merge → P3-02 (the §3.1 machine) → P3-03..09 → the gates.

## 1. What the owner asked (verbatim)

The standing chain (INT-134/135/138/139/140): "work towards it, P3-01 — the first
real product command through the kernel + the §1.6 capture checkpoint (import →
capture → replay → retrieve through the real boundary), then P3-02..09 → the
Phase 3 exit gate → P4-00 → P4-A..F → the Phase 4 exit gate — no pause." The
turn-35 product directive (INT-140): the actual-product build — backend,
database, schemas, retrieval — the compounding goal. At this slice's session
entry the owner added: "continue working towards phase 3 and 4... ig the work is
lost after pr #83 so i would suggest you to commit and push to prs often so it
doesnt disappear like this when your workspace reset" — the PUSH-EARLY
DISCIPLINE is now standing owner instruction: the branch pushes at every
significant commit; a workspace reset may never eat in-flight work again (the
first P3-02 attempt was lost entire to a workspace reset — its rehearsal
lessons are baked into this slice from the first line).

## 2. Starting state — the preflight, the EIGHTH env-reset repair, and the lost-work recovery

The workspace had been RESET: the local main sat three days stale (the #69
merge), the session's earlier P3-02 attempt (its branch, its commits) was
entirely lost — never pushed. The recovery: the PAT re-verified live (login
prathamarchives; the stale stored token replaced), the true remote read (PR #84
MERGED at ab22029 — P3-01 landed end-to-end: the post-merge run 40219243398 five
green, the branch deleted, the protection restored byte-identical), and the
dangling-commit scan of the stale clone (all Oct-13..20 residue, no P3-02
remnant). The rig: DOWN with the documented pair (the pgdata perms + the missing
pg_notify) — the EIGHTH env-reset corruption, rebuilt initdb→migrate→
verify-schema→health, make verify GREEN 54/0 at the fresh ab22029.

## 3. Task and scope

PLAN's P3-02 card; RTM §3.1's frozen machine + SYS-06/SYS-03's primary trace;
the Q11 baseline at §7.5; the P3-01 notverified's named P3-02 promises: the
staging/staging_verified states, the recovery walk, the blob delete arm, the
corrupt-blob + orphaned-staging-artifact cleanup. The scope (CLAIMS-050):
0005_import_journal.sql, commands.py, recover.py, blob.py, crash.py, the suite,
gate.py, the registry/ledger/navigation homes.

## 4. Results

THE MACHINE (§3.1 walked at every transition): the phased import — request
validation (CAP-001/009/007 at phase 0), the replay/conflict check BEFORE any
staging (IMP-15: a refused command stages NOTHING — the P3-01 notverified's
409-orphan class dead by construction), the staging journal UPSERT (its own
transaction; the same-key retry REWINDS a crashed row), put+verify INSIDE
staging (the machine's staging exit condition; CAP-004 names a verify failure
and marks the row failed-retryable), staging_verified, then ONE metadata
transaction carrying the work insert (when --title), the Source row BORN
complete, the command_log row, AND the journal's complete update ATOMICALLY —
the lost-ack converges in-transaction (IMP-09's stronger form; the journal can
never lag the commit). THE WALK (recover.py): oldest-first (created_at,id),
row_to_json one-escaped-line-per-row reads (IMP-11: pipes/newlines/'MARK' in a
title can never corrupt — the P3-01 SEV round's F1/F2 classes dead by
construction), the canonical body reconstructed from the row's recorded
FIELDS and hash-checked against body_hash BEFORE any drive (ARV-IMP-001 on
mismatch — never a drive with an invented body), the phantom-closure re-verify
(IMP-10: a blob that vanishes after verify means failed(ARV-BLOB-002), NEVER a
complete Source without bytes), terminal rows never touched (IMP-12: two more
walks change NOTHING, updated_at byte-identical), the orphan sweep (IMP-16:
journal-less residue deleted; live-staging and referenced blobs protected —
the cross-owner arv_read count, an unreadable check fail-closed to KEEP), and
named machinery failures (ARV-IMP-003 — a refused batch is never a silent
zero-rows guess; the walk's fetch ORDER BY bug — the subquery missing
created_at — was exactly that class, caught live at the first walk debug and
repaired fail-closed). THE JOURNAL (0005): the §2.9 disposable substrate —
RLS-scoped (IMP-14: both layers fail closed), the state CHECK (IMP-17's
badstate probe), UNIQUE(owner_scope, idempotency_key), NO append-only trigger
and NO DELETE grant — mutable BY DESIGN (rows transition, never erased; the
declared absence pinned as the design). THE Q11 BASELINE (IMP-02/03): identical
bytes twice = two Sources, ONE blob; same title twice = two works; no
auto-merge, no uniqueness. THE CRASH MATRIX (IMP-05..10): after-staging →
failed(absent) → the same-key retry completes; after-put → the walk verifies →
re-drives → complete; corrupt → failed(ARV-BLOB-003) + the unreferenced
artifact DELETED (the delete arm) + the retry re-puts; after-verify → the walk
re-drives → complete exactly-once; post-commit-pre-ack → complete
in-transaction + the replay answers; the vanished blob → failed, no phantom.
CRASH.PY: the three import-phase points + --work-id; a usage error is a named
exit-1, never the argparse exit-2 crash masquerade. THE SUITE: 17 cases
GREEN (three consecutive full runs at the final tree), 607→final test lines,
RED-first machinery-absent at 1c556b36 (red-01.txt).

THE SPLIT (this slice's own honest event): SIZE-002 refused the first
assembled diff at 519 > 400. The repair was the routing's own split form — the
SEV-7 stderr-classification work (the P3-01 SEV-11 routing: duplicate-key →
011 from the DRAINED stderr; the connection-class → the NEW ARV-CMD-012 §4.1
uncertain class resolved by the same-key replay; the suite's IMP-18/19 with
the planted-trigger deterministic dup-key arm and the killed-backend probe)
moved to CLAIM-051's own bounded slice, its predecessor = this slice's merge.
The spine's INSERTS-block 011 stayed EXACTLY main's poll()-inferred form with
the in-code routing comment; the Session's stderr pump/dead_reason and
_dead_exit were REMOVED from this slice (they land RED-first in 051);
blob.exists() removed (dead code — it lands WITH its consumer); the source
diff landed at 384/400 with the headroom the review rounds need. The
ARV-CLM-002 catch: pre-opening CLAIM-051's row while 050 was open was refused
by the gate itself (the scope overlap) — rule 4 (a claim opens in the PR that
carries its first work commit) honored; the routing carried in four homes
(the spine comment, the suite header, the red-records amendment, the Notes).

## 5. Files changed

harness/migrations/0005_import_journal.sql (NEW); harness/recover.py (NEW);
harness/commands.py (the phased import + _qn + _import_body/_import_build +
_journal_txn; the spine reverted to main's 011 form with the 051 routing
comment); harness/adapters/blob.py (delete + residents; exists removed);
harness/crash.py (the phase points + --work-id + the exit-2 lesson);
harness/tests/test_import.py (NEW, IMP-01..17); harness/gate.py (TESTS);
harness/red-records.json (the typed binding + the amendment chain); CLAIMS.md
(the 050 open row + the 049 rule-4 close + the split note);
harness/runs/claim-050-p302-import-state-machine (scope, red-01, the proof
set, notverified, the sheet, sev.json); STATE/AGENTS/PLAN/WORKLOG (the
re-derivation); this record.

## 6. Commands and external actions (ACTUAL — never reconstructed)

- git fetch/pull → main ab22029; the dangling-commit scan; the PAT verify.
- The rig rebuild: chmod 700 → initdb (exit 0) → start (accepting) →
  make migrate (applied 0004, then 0005 after the GREEN) → verify-schema
  ("4 migrations" then "5") → harness-health (OK ARV-RIG-001) → make verify
  (GREEN 54/0 at ab22029; GREEN at each content head).
- The suite: python3 harness/tests/test_import.py — the RED (exit 1,
  ARV-TEST-000, red-01.txt) then the GREEN iterations (exit 0, 17/17, three
  consecutive runs); the forensic keep-runs (ARV_KEEP_DB) for the IMP-17/18
  debug; the standalone replications (probe/walkdbg/dbg18b scratch DBs — all
  dropped after use).
- The proof set: run-01 (the import suite) run-02..12 (the eleven machinery
  suites, all exit 0) run-13 (make verify, exit 0) run-14 (the PR-mode gate,
  exit 1 — the HONEST pre-finalize RED: the notverified/sev/sheet not yet
  assembled, the #80 run-06 class, preserved never smoothed) + the final
  re-assembly and the green RECORDED run after the finalize.
- git push at 1c556b36 (the RED, branch created, PR #85 opened EARLY per the
  owner's push-often instruction), 3230330 (the GREEN), 7973c91 (the split),
  and the finalize push; the CI observed at each head.

## 7. Evidence

The slice's runs dir: scope.txt (the owner-referenced protected paths), red-01
(the machinery-absent RED), the proof set (the command list above), the
re-derived Proof Sheet (PASS ARV-PRF-004 byte-identical at the finalize), the
notverified (eleven named boundaries), sev.json (the two-round chain's
record, sheet_section true). The registry: CLAIM-050's open row + the 049
close row. The red-records chain: the binding at 1c556b36 + the amendments
(the nine suite-shape repairs and the split, each with the honest note).

## 8. Failures (each honestly recorded, each repaired in-slice)

- _q(None) crashed the journal INSERT (the first GREEN run's cascade) — the
  _qn NULL-safe helper; the suite's resident() pathlib fix (mkdtemp's str).
- The walk's fetch ORDER BY created_at failed (the subquery did not select
  it) AND _batch swallowed the refusal as zero rows — created_at added to the
  projection AND _batch → None + the named ARV-IMP-003 exit (the
  silent-empty class killed, not patched over).
- _referenced parsed a count(*) output as a DIGEST LIST — always-False — a
  REFERENCED corrupt blob would have been deleted (the worst class, caught by
  review-of-self before any suite run tripped it); rebuilt as the count
  comparison, unreadable → fail-closed KEEP.
- str(KeyError) carries repr quotes: the fail_reason stored 'ARV-BLOB-002
  (a stray quote, observed in the kept-DB forensics) — e.args[0] everywhere.
- The suite-shape repairs (the byte-reuse lesson: IMP-05's fixture bytes were
  resident from IMP-03; IMP-13's --work-id crash needs an existing work; the
  no-GUC SELECT is the fail-closed ZERO-ROWS not an error; the grants read
  must come from the superuser; has_table_privilege renders true/false) — all
  amendment-chained, none weakened.
- SIZE-002 519>400 → the CLAIM-051 split (the repair line's own
  prescription); ARV-CLM-002 → rule 4 honored (051's row opens with its own
  PR). The stale CLAIMS registry: the fixture's positive-PR dispatch went red
  on the OVERLAP between the stale open 049 row and 050 — the close work was
  this slice's first duty (the #84 merge observations in 049's rule-4 row).
- The pre-split commands.py surgery (the stderr pump + _dead_exit) was
  REVERTED to main's exact spine form when the split was adopted — the
  classifier work belongs to 051, and this slice's diff must not carry it.

## 9. Unverified items

The notverified's eleven named boundaries (the standing credential layer; the
SEV-7 routing to 051; the disposable-journal semantics; the
unreferenced-only cleanup + the .put- residual; the rig-store sweep boundary;
the sequential-walk concurrency class; the id-order fallback; the oracle's
standing residuals; the CI-host class; the born-complete source; the
session-fact RED files).

## 10. Open decisions

D-014 + Q6–Q12 (scopes unchanged; Q11's baseline IMPLEMENTED per §7.5 — the
identity policy beyond it remains owner-gated; Q12 unratified — the blob
backend comparison stands as the RTM's evidence-preparation table).

## 11. Next action

Push the finalize; watch PR #85's five checks at the exact head; the
CodeRabbit round (Greptile's credit exhausted — NOTED); every finding
RED-first-fixed or reasoned-no-fix in-PR, every thread dispositioned BEFORE
resolution; merge under D-042 (the 405 bar → the recorded flip → RESTORE);
the post-merge five-check run + the branch deletion + the protection re-read;
then CLAIM-051 (the SEV-7 classifier — its own RED at this slice's merge as
the predecessor, its PR opening its claim row per rule 4) → P3-03 (Extraction
+ Anchor) → P3-04..09 → the Phase 3 exit gate → P4-00 → P4-A..F → the Phase 4
exit gate — NO PAUSE (INT-134/135/138/139/140).

## 12. Session close

The push-early discipline is STANDING owner instruction from this session
(recorded at §1); the PAT rotation reminder stands for the project's
completion; the worklog's host-side mirror carries the session's task
entries. The routed follow-ups remain recorded and never lost: the
ARV-SEV-009 undecidable-base regression; the N12 self-test-row extension; and
now CLAIM-051 (this slice's own routing, four homes).
