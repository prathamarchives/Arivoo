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

## §3 The slice chain (EXECUTED — the account of what landed)

commit A `f066b46` (the post-#107 five-area reconciliation + CLAIM-073 opened + record 65
minted; the branch pushed EARLY per the standing owner instruction) → the RED `7756bbd`
(the SYN-20 pin re-added to test_sync.py, tests-only per LAW-11 — the P3-06 re-home
precedent; OBSERVED RED: SYN-01..19 green, SYN-20 FAIL exit 1, red-01.txt; the machinery-
absent state: no `_SYNC_COMMANDS` membership, no delivery branches, no journal outbox row)
→ the GREEN `1ceb8b9` (commands.py's `_SYNC_COMMANDS` membership + sync.py's `_cli_args`
journal branches + the identity bridge's address-form extension + the JNL-04 SUPERSESSION —
the pin's ZERO-outbox-row form superseded by the delivery-carrying form, the amendment
typed and disclosed; OBSERVED: the sync suite SYN-01..20 exit 0 + the journal suite
JNL-01..06 exit 0; the measured set runs 01-07: the sync suite x3 + the journal suite x3
+ make verify, all exit 0 at that tree) → **the SEV round 1** (agent-41d77e6c, fresh
context — the heavy probes by a prior fresh-context agent whose raw captures the round
re-verified; BLOCKED: F-073-1 the P1) → the round-1 RED `094eb07` (the SYN-21 pin,
tests-only; OBSERVED RED: SYN-21 FAIL exit 1, red-02.txt) → **the round-1 repair**
`45b47ce` (the driver-boundary all-string argv guard INSIDE the per-row containment + the
journal branches' validation-before-staging order + the gettempdir()-based staging-cleanup
prefix + the F-073-4 docstring sharpening; OBSERVED: the repro contained — the hostile row
failed ARV-SYN-013 named, the walk continues, both passes exit 0; the sync suite SYN-01..21
exit 0; the re-measured set runs 08-12: the sync suite x3 + the journal suite + make
verify, all exit 0 at the repair tree) → **the SEV round 2** (agent-0361ce20, fresh
context; PASS — the P1 verified repaired live at both boundaries, family-wide, no new
P0/P1/P2; F-073-6 the new P3 routed) → the artifact finalize (this commit: the record-65
account) → the artifact re-bind (sev.json binding the two-round chain + notverified +
the proofsheet + the recorded PR-mode gate) → the push → the PR → the five checks →
the merge-gate review → **the merge under INT-145** → the post-merge verification →
the following P4-C reconciliation (the reading-list/collection question) + P4-D..F —
NO PAUSE EVEN FOR UPDATES (INT-146).

## §4 The SEV account (the two-round chain)

**Round 1 (agent-41d77e6c) — BLOCKED, F-073-1 the P1:** the wrong-typed payload VALUE
containment escape. A hostile outbox row whose payload parses as JSON but carries a
wrong-typed value (`{"kind":5,...}` on a journal row — the SYN-16 substrate-insertion
technique; the pre-existing note-content twin) passed through `_cli_args` without raising
and crashed the driver at the argv-consumption sites OUTSIDE the per-row containment
(`AttributeError: 'int' object has no attribute 'startswith'` at the tmp_file scan;
`_apply`'s Popen behind it): the row rested delivered-unapplied with no named reason,
every later pass crashed identically — **the queue permanently blocked**, falsifying the
SYN-16 containment law's own text ("never an unhandled crash, never a blocked queue").
Independently reproduced by the orchestrator (repro_073_f1.py: sync exit 1 twice, the
identical traceback) and by the round's own two-DB walks. The P3s: F-073-2 the walk-2
probe-side expectation errors (adjudicated — the correct server-row count 6, the printed
states already the correct behavior); F-073-3 the staging-residue classes ((a) the
crash-path leak — subsumed by the P1 repair; (b) the hard-coded `/tmp` prefix missing
TMPDIR-steered runs — one staging file leaked per successful delivery); F-073-4 the
"@1 rows are only ever CREATES" docstring imprecision (the conclusion holds — the
creator-preference ORDER BY; the wording repaired); F-073-5 red-01.txt's Tree header
naming commit A (reasoned no-fix: contemporaneous evidence, never rewritten post-hoc;
the exact binding lives in the typed amendment naming 7756bbd).

**The repair `45b47ce` (RED-first — SYN-21 at 094eb07):** (1) the driver-boundary
all-string argv guard INSIDE the containment — a non-string argv element is the named
ARV-SYN-013 undeliverable class, never a str() coercion, never an unhandled crash — the
family-wide net (the journal kind AND the note-content pass-through class); (2) the
journal branches' validation order — the kind type-checked and the content encoded
BEFORE the staging file exists (zero residue on the contained paths); (3) the
staging-cleanup prefix through tempfile.gettempdir(); (4) the F-073-4 docstring
sharpening.

**Round 2 (agent-0361ce20) — PASS:** the P1 verified repaired LIVE at both boundaries
(the repro re-run: the hostile row failed ARV-SYN-013 named, the walk continues, both
passes exit 0; the reviewer's own two-DB probe: the note twin `{"content":5}` and a third
family representative contained; the guard placement confirmed by code read; the
well-formed bound journal delivery still acknowledges — no regression). F-073-3 both
legs verified live (zero staging files on the contained paths; the steered TMPDIR ends
empty). F-073-2/4/5 adjudicated. **F-073-6 (new P3, ROUTED):** the import_source branch
stages its blob BEFORE argv construction — a contained refusal or the ARV-SYN-009
work-dependency leg leaves a staging file behind (the F-073-3(a) class on the one family
outside this slice's journal-scoped reorder; a strict improvement over the pre-repair
crash; the same reorder recommended in a follow-up).

**The honest not-verified list** (notverified.txt): the routed F-073-6; the standing
family-wide classes (the read arms' malformed-id echo — the F-072-1 routing; the
`_nte_canon_id` family-wide slice); no fresh full-suite re-run inside the SEV rounds
themselves (the recorded runs stand); no reader-client work (P4-B's repo); the
`harness/client.py` surface unchanged at this slice.
