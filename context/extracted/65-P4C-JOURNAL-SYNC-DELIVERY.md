# Record 65 — P4-C slice four: the journal sync delivery (the LAW-05 split's re-home)

> STATUS: SESSION ENGINEERING RECORD (2026-11-10; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 89. PR #107 MERGED (the P4-C slice three journal/blocks surface,
> under INT-145); the CLAIM-073 PR follows at this slice's end.

Session 41 (2026-11-10), CLAIM-073, opened at the merged head `7286b3c` (the PR #107 merge —
P4-C slice three). Record 64 carries the journal/blocks account (complete, §5 closed); this
record carries the sync-delivery slice's contract + chain — the LAW-05 split's named re-home
landing.

## §1 The #107 merge close (CLAIM-072 LANDED — P4-C slice three)

PR #107 merged at 2026-11-10 as `7286b3cf2555686476569e4c3663f7ecd2b8885e` under INT-145's
standing authorization: the five checks green at the exact final head `d1c1190` AND on the
merge commit (all observed live); the merge-gate review D-042 (1a) `5840270161`; the
CodeRabbit chain — three Minor findings, each with an explicit in-thread disposition before
the merge (the s_c_s hypothetical: reasoned no-fix with live probes + the correction accepted;
the malformed-id raw-cast class: routed family-wide; the buffered history read: reasoned
no-fix) — all three threads resolved; the flip/merge/restore with the protections re-read
byte-equivalent; the branch deleted; 0 open PRs; only main. No ARV-SEV-003 round — the digest
bound LAST (`8c835b06`) + the local trusted-gate reproduction green before the push (run-14,
first attempt). THE THREE-ROUND SEV CHAIN, every blocker repaired and verified (the pre-split
PASS; the split's scope-residue P1 repaired at `be413b8`; the round-3 PASS verifying the repair
by the exact machinery that refused). THE LAW-05 SPLIT executed in-slice — this slice (CLAIM-073)
is its named re-home. The full account: record 64 §5 + CLAIM-072's rule-4 close row.

## §2 The sync-delivery slice's contract (the split's own letter, one phase deep)

**The letter:** the writing lab's no-lost-writes law — the journal family joins the
outbox-carrying set, the enqueue AND the delivery landing TOGETHER in one slice:

- **The enqueue** — `journal_block` + `revise_journal_block` join `_SYNC_COMMANDS`: every
  journal write rides the client outbox like every landed family (the JNL-04 pin's
  ZERO-outbox-row form was the SPLIT tree's honest state — at this slice it is SUPERSEDED by
  the delivery-carrying form, the amendment typed and disclosed).
- **The delivery** — sync.py `_cli_args` carries the journal branches: the journal_block row
  re-executes server-side with the RECORDED kind and the content re-materialized through the
  TEMP FILE channel (the lossless law rides the delivery — the long raw thinking is unbounded
  and argv is not, the framing-law characters travel byte-identical); the OPTIONAL source
  binding translated through the identity bridge (a not-yet-durable source resting the row
  retryable ARV-SYN-009 — the dependency class every translated binding carries); the
  revise_journal_block row re-executes through the TRANSLATED block id (the uuid stem of the
  server's acknowledged @1 address) with the server appending its own next revision on the
  SAME identity — the governed history rides the delivery.
- **The identity bridge's ADDRESS-FORM extension** — `_create_key` matches
  `result_ref IN (id, id||'@1')`: the two house shapes of entity creates (the bare uuid and
  the revision-1 address); `journal_block` joins the creator-preference list. @1 rows are only
  ever creates, so the clause adds no cross-entity risk.
- **The SYN-20 pin** — re-observing its RED at this slice's own commit (the P3-06 re-home
  precedent): the original RED at `838b1e9` + GREEN at `806ef04` are preserved in CLAIM-072's
  chain, never rewritten; this slice's tree re-adds the pin and observes the RED against its
  own machinery-absent state (no enqueue → no journal outbox row → the delivered block never
  observed → SYN-20 FAILS at the RED commit).

**The design boundary (the acceptance the RED pins):** the journal_block outbox row DELIVERS
(the server-side block through the TRANSLATED source binding with the recorded kind, the
content BYTE-IDENTICAL); the revise DELIVERS through the TRANSLATED block id appending the
server's revision 2 on the SAME server identity; the server's read arms answer the delivered
block and its full history; SYN-01..19 no-regression; the journal suite JNL-01..06
no-regression in the delivery-carrying form.

## §3 The slice chain in flight

commit A (this commit: the post-#107 five-area reconciliation + CLAIM-073 opened + record 65
minted; the branch pushed EARLY per the standing owner instruction) → the RED (the SYN-20 pin
re-added to test_sync.py, tests-only per LAW-11, observed RED at this tree — the machinery
absent: no `_SYNC_COMMANDS` membership, no delivery branches) → the typed red-record binding →
the GREEN (the enqueue + the delivery branches + the bridge extension, all together — never
the dead-letter window) → the JNL-04 supersession amendment (typed, disclosed) → the measured
set → the SEV round(s) → the artifact finalize → the artifact re-bind → the push → the PR →
the five checks → the merge-gate review → **the merge under INT-145** → the post-merge
verification → the following P4-C reconciliation (the reading-list/collection question) +
P4-D..F — NO PAUSE EVEN FOR UPDATES (INT-146).
