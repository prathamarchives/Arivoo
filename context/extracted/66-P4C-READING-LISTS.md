# Record 66 — P4-C slice five: the reading-list surface (the post-#108 reconciliation's landing)

> STATUS: SESSION ENGINEERING RECORD (2026-11-10; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 90. PR #108 MERGED (the P4-C slice four journal sync delivery,
> under INT-145); the CLAIM-074 PR follows at this slice's end.

Session 41 (2026-11-10), CLAIM-074, opened at the merged head `3f6922b` (the PR #108 merge —
P4-C slice four). Record 65 carries the journal sync delivery's account (complete, §5 closed
at this commit); this record carries the reading-list slice's contract + chain.

## §1 The #108 merge close (CLAIM-073 LANDED — P4-C slice four)

PR #108 merged at 2026-11-10 as `3f6922bf1a347d90a0ea5635d8b5f324f4c5813d` under INT-145's
standing authorization: the five checks green at the exact final head `5e53682` AND on the
merge commit (all observed live); the merge-gate review D-042 (1a) `5845109949`; CodeRabbit
the skip state (no automatic reviews — noted per D-042 (1c)); zero review threads; the
flip/merge/restore with the protections re-read byte-equivalent; the branch deleted; 0 open
PRs. No ARV-SEV-003 round — the digest bound LAST (`acac4831`) + the local trusted-gate
reproduction green before the push (run-15; run-14 the disclosed sheet-lag RED — caught
BEFORE the push this time). THE TWO-ROUND SEV CHAIN (round 1 BLOCKED the F-073-1 P1 — the
wrong-typed payload VALUE containment escape, repaired RED-first at `45b47ce`; round 2 PASS —
the repair verified live at both boundaries family-wide). The full account: record 65 §4/§5 +
CLAIM-073's rule-4 close row.

## §2 The reading-list slice's contract (the post-#108 reconciliation, one phase deep)

**The reconciliation (the directive's named question):** "The reading-list and collection
requirements must be reconciled against the complete canonical P4-C outcome. Do not silently
assume that the basic library list fulfills them." The evidence: the North Star owner words
name THREE surfaces — "I have lists, a library, and lists of what I'm currently reading" — of
which the library LANDED (CLAIM-070 list-library) and the current-reading lists LANDED
(CLAIM-070 get-reading-state), but the user-defined LISTS did not: CLAIM-070's own bounded
exclusion deferred them ("no reading lists/collections beyond the library itself"), and the
PLAN 4C row's title names "reading lists" ("stable library/list membership"). The RTM's
frozen entity contracts never reserved a list entity — the Phase-4 reservations were
JournalBlock, @Reference, ReadingSession — so the shape elaborates NOW (one phase deep at
slice four's landing, the P4-A..F rule). "Collections" (the directive's word) is the same
surface: a list IS a collection of sources; no separate collection entity is invented
without owner intent.

**The letter:** the user-defined lists over the landed library —

- **Migration 0017_reading_list** (the 0015/0016 substrate pattern):
  - `arv.reading_list` — the list header: id, owner_scope, name TEXT (the owner's own name,
    1..512 chars, no NULs), provenance (actor, run_id, input_hash, idempotency_key,
    created_at), the append-only triggers, RLS enabled AND forced + the owner policy, the
    grants (INSERT+SELECT arv_app / SELECT arv_read / no UPDATE/DELETE), NO DEFAULTs. NO
    name uniqueness — Q11's identity baseline: the identity is the uuid, never the name
    (two lists may share a name; the id disambiguates).
  - `arv.reading_list_member` — the append-only MEMBERSHIP EVENT rows: (id, list_id,
    source_id, owner_scope, op, provenance, created_at) with the closed op vocabulary CHECK
    ('added' | 'removed'), the composite FKs (list + source, both owner-scoped), the same
    substrate laws. The CURRENT membership is DERIVED: the last op per (list, source) wins —
    a projection; the event rows are the recovery substrate (RTM §2 item 9's derived-state
    rule: every add/remove retained, never a destructive delete, the full history
    reconstructable from the events alone).
- **The commands** (commands.py, through the spine's own ack contract — idempotent, the
  frozen grammar, the crash-matrix membership): `create_reading_list --name <n>` (the list
  header row; result_ref=<list-id>, the bare-uuid create class); `add_to_list --list <id>
  --source <id>` (the 'added' event row); `remove_from_list --list <id> --source <id>` (the
  'removed' event row). The typed no-oracle refusals: ARV-RLS-001 the absent/cross-owner
  list; ARV-RLS-002 the absent/cross-owner source at the membership; ARV-RLS-003 the name
  law (empty / oversized / NUL-carrying refused, never clamped).
- **THE OUTBOX RIDE** (the CLAIM-073 law: the enqueue AND the delivery TOGETHER, never the
  dead-letter window): the three commands join `_SYNC_COMMANDS`; sync.py's delivery branches
  carry the translated list id (the create's bare-uuid result_ref — the bridge's existing
  form, no address-form extension needed) + the translated source id; a not-yet-durable
  dependency rests the row retryable ARV-SYN-009.
- **The read arms** (query.py): `list-lists` (the owner's lists, bounded/paginated on the
  P4-00b contract, each row with the derived member count, api_version'd, the empty
  library's honest two-line answer) + `get-list --id` (the CURRENT membership — one row per
  active member, bounded/paginated, the no-oracle byte-equal refusals for absent vs
  cross-owner, the empty list's honest answer).
- **The registry rows**: capability.py's reading-lists reserved-surface row (owner_phase
  P4-C, the LANDED verbs) + crash.py's command membership.

**The design boundary (the acceptance the RED pins):** the create→add→list→read round-trip;
the membership event history complete (every add/remove retained, the current view derived —
remove hides from the current view, the history keeps it; re-add after remove reactivates as
a NEW event row, never a mutation); idempotent writes and replay (same key+body → replayed;
same key+different body → ARV-CMD-409); the outbox delivery round-trip through the
translated ids (both domains' memberships equal); owner isolation (B's lists invisible to A,
the no-oracle byte-equal); the spine's crash matrix (the lost-ack arm); the sibling suites
no-regression (SYN-01..21, JNL-01..06).

**THE BOUNDED EXCLUSIONS:** no list ordering/pinning (a future increment); no list-of-lists
or nested collections; no shared/multi-owner lists; no @-reference resolution over lists
(P4-D's increment); no rename/revision machine on the list header (the name immutable at
this slice — a rename is its own increment); no reader-client work (P4-B's repo).

## §3 The slice chain (EXECUTED — the account of what landed)

commit A `73bfd8c` (the post-#108 five-area reconciliation + CLAIM-074 opened + record 66
minted; the branch pushed EARLY per the standing owner instruction) → the RED `e7e833f`
(the RLS suite authored tests-only per LAW-11 — the ARV-TEST-000 machinery-absent probe
(create_reading_list absent, list-lists/get-list absent, migration 0017 absent) + the
behavioral pins RLS-01..06 + the SYN-22 delivery pin in the sync suite; OBSERVED RED:
red-01.txt — the RLS suite exit 1 at the ARV-TEST-000 probe, the sync suite SYN-01..21
green + SYN-22 FAIL exit 1; the gate's TESTS registration + the scope/CLAIMS amendment
declaring test_sync.py rode the RED commit) → the GREEN `60fab3d` (migration 0017 +
the three commands through the spine + the two read arms + THE OUTBOX RIDE TOGETHER
(_SYNC_COMMANDS membership + the delivery branches) + the capability row + the crash
membership + the four DISCLOSED pre-GREEN test strenghteners riding the typed amendment:
the NUL unit-probe at the law's own layer (argv cannot carry NUL), the keyset cursor's
parsed-id form, the has_table_privilege grants audit, the superuser channel for the
append-only trigger probes — arv_app refused at the PERMISSION layer first, the grants
law's own proof); OBSERVED: the RLS suite GREEN RLS-01..06 exit 0 + the sync suite GREEN
SYN-01..22 exit 0) → the measured set (runs 01-06: the RLS suite x3 + the sync suite +
the journal suite + make verify — all exit 0 at the GREEN tree; the canonical layer 54/0)
→ **the SEV round 1** (agent-caf66233, fresh context; PASS — zero open P0/P1; ~92 live
probes + ~10 static/git checks) → the artifact finalize (this commit: the record-66
account) → the artifact re-bind (sev.json binding the one-round PASS + notverified + the
proofsheet + the recorded PR-mode gate + the trusted-gate reproduction) → the push → the
PR → the five checks → the merge-gate review → **the merge under INT-145** → the
post-merge verification → the P4-C exit check → P4-D..F — NO PAUSE EVEN FOR UPDATES
(INT-146).

## §4 The SEV account (round 1 — the one-round PASS)

**Round 1 (agent-caf66233) — PASS, zero open P0/P1.** The reviewer's own two-DB walk:
the server event history `[added, removed, added]` on the SERVER's list id; the name
byte-identical (a 512-char unicode+newline name delivered whole); the current membership
equal on both domains through the TRANSLATED ids; all outbox rows acknowledged with
server_refs; the second pass a true no-op; the spelling-variant retry REPLAYS (the
id-normalize law). The derived-view law verified (active→hidden→active; the event rows
retained on both domains; the member counts owner-isolated). The alternation law
verified at the substrate (the hostile duplicate-op INSERT refused ARV-RLS-008; the
lawful alternation passes; the held per-pair advisory lock BLOCKS a hostile insert —
the serialization proven). The no-oracles byte-equal (write: after the id-normalize;
read: RAW — the no-id-echo form). The name law, Q11's shared-name law, the bounds, the
substrate audits (RLS forced, the policies, the grants, NO DEFAULTs, the named op CHECK,
the composite FKs), the capability row, the crash arm — all green. The RED chain
git-verified across the three commits (the reviewer independently reproduced the RED at
`e7e833f` itself); the scope clean (19/19 diff paths declared, no residue).

**The findings, dispositioned:**
- **F-074-1 (P2, ROUTED):** a legal leading-dash list name (`--evil`, creatable via the
  `--name=` spelling) enqueues an outbox row whose server-side apply dies at argparse —
  the row rests `uncertain` (honest, visible, the local write durable; the walk
  continues), never landing server-side. Live-reproduced end-to-end — but a
  **pre-existing family-wide argv-value class**: `import_source --title=--eviltoo`
  shows the identical behavior at this tree. ROUTED with the import-title/note-content
  family to the argv-value convention's own slice (the repair is trivial — the `--name=`
  form in `_cli_args` — but the class spans every argv-carrying delivery branch; a
  journal-only fix would fork the convention; the F-072-1/F-073-6 routing precedent).
- **F-074-2 (P3):** a different-key duplicate-op membership write surfaces as the
  generic ARV-CMD-010 (the raw cause naming ARV-RLS-008) — zero effect, the declared
  design boundary (the alternation law's own refusal shape); a precision note for the
  family-wide typed-refusal slice.
- **F-074-3 (P3):** red-01.txt names the commit-A tree as the observation tree rather
  than the RED commit — the standing family convention (F-073-5's class); reasoned
  no-fix (contemporaneous evidence; the exact binding in the typed record naming
  `e7e833f`; the reviewer independently reproduced the RED at the RED commit itself).
- **F-074-4 (P3, assessment):** get-list's two-read shape (the header read then the
  member page, two snapshots) — no vanish class (the header is append-only); a
  momentary member_count/page divergence possible; the family's known bounded class
  (the F-072-1 read-arm family), assess-only.

**The honest not-verified list** (notverified.txt): the routed F-074-1 (the argv-value
family); the standing family-wide classes (the read arms' malformed-id echo, the
`_nte_canon_id` pattern's slice, the two-read shape); no fresh full-suite re-run inside
the SEV round (the recorded runs stand); the single-owner walk shape (B's delivery
verified through the suite's SYN-08 class, not re-walked); no reader-client work
(P4-B's repo).

## §5 The close (CLAIM-074 LANDED — at this commit, the post-#109 reconciliation)

PR #109 merged at 2026-11-10 as `4a750db327fac4d9b7540a6029d74b48e88ce99d` under INT-145's
standing authorization: the five checks green at the exact final head `982b273` AND on the
merge commit `4a750db` (all observed live); the merge-gate review D-042 (1a) `5846447048`;
CodeRabbit the skip state (noted per D-042 (1c)); zero review threads; the flip/merge/restore
with the protections re-read byte-equivalent; the branch deleted; 0 open PRs. No ARV-SEV-003
round — the digest bound LAST (`65c0d342`) + the local trusted-gate reproduction green before
the push (run-08, first attempt). THE ONE-ROUND SEV CHAIN (the account in §4): agent-caf66233
PASS, zero open P0/P1. The routed follow-ups: F-074-1 (the leading-dash argv-value family)
+ the standing family-wide classes.

**THE P4-C EXIT:** with this landing every required P4-C backend behavior is landed and
verified — the library membership, the current-reading state, the reading lists, the
approved session/dwell behavior, the journal/blocks + the sync delivery. **P4-C COMPLETE.**
The full account: CLAIM-074's rule-4 close row + this record. Record 67 carries the
stable-reference slice (P4-D's opening).
