# Record 64 — P4-C slice three: the journal/blocks surface (the writing lab)

> STATUS: SESSION ENGINEERING RECORD (2026-11-07; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 88. PR #106 MERGED (the P4-C slice two session/dwell events
> surface, under INT-145); the CLAIM-072 PR follows at this slice's end.

Session 41 (2026-11-07), CLAIM-072, opened at the merged head `78b3654` (the PR #106 merge —
P4-C slice two). Record 63 carries the session/dwell account (complete, §4 closed); this record
carries the journal/blocks slice's contract + chain.

## §1 The #106 merge close (CLAIM-071 LANDED — P4-C slice two)

PR #106 merged at 2026-11-07T14:11:33Z as `78b3654a10366d7228fe054ca9499dc50278fb8c` under
INT-145's standing authorization: the five checks green at the exact final head `89bfcf6` AND on
the merge commit (all observed live); the merge-gate review D-042 (1a) `5812693494`; the
flip/merge/restore with the protections re-read byte-equivalent; the branch deleted; 0 open PRs;
only main. No ARV-SEV-003 round — the digest bound LAST (`09671943`) + the local trusted-gate
reproduction green before the push (run-09, first attempt). THE THREE-ROUND SEV CHAIN, every
blocker repaired and verified (the sync dead-letter P1 RED-first at `fc50d3b`; the
declaration/records blockers at `c8fed14`; the label-divergence P1 at `3a5c9d0`, verified by the
exact machinery that refused). The full account: record 63 §4 + CLAIM-071's rule-4 close row.

## §2 The journal/blocks slice's contract (PLAN's 4C journal letter elaborated one phase deep)

**The letter:** journal as a writing lab — source-optional raw/creative blocks, long raw thinking
preserved losslessly, no forced short-note funnel:

- **The block rows** — append-only, owner-scoped, the raw/creative kind vocabulary CLOSED at the
  substrate (the 0015 D-010 pattern: the named CHECK refuses out-of-vocabulary kinds below the
  command); the LONG raw thinking preserved LOSSLESSLY (the full text stored — never a truncated
  form, never a funneled rewrite; the write->read round-trip byte-honest); revisions are NEW rows
  (the governed-history convention every landed family carries).
- **The write** — through the spine's own ack contract (idempotent, the frozen grammar, the
  client-outbox ride, the crash-matrix membership via crash.py): result_ref=<block>@<revision>.
- **The read arms** — the journal listing (bounded/paginated on the P4-00b contract, the keyset
  cursor, the version key) + the single-block read (the lossless round-trip; the current revision
  + the governed history at its own arm).
- **The source-OPTIONAL law** — a block binds a source only when the author says so (an optional
  location-class field, never a forced binding; a sourceless block is a FIRST-CLASS journal row).
- **The no-forced-funnel law** — the journal never forces the short-note form: the landed note
  machine stays its own surface, the boundary typed and named (a journal block is NOT a note and
  a note is NOT a journal block — no silent conversion either way).

**The design boundary (the acceptance the RED pins):** the lossless round-trip; the closed kind
vocabulary; the source-optional law; the no-forced-funnel boundary; the bounded/paginated listing;
the owner isolation; the 0016 substrate conventions (the 0014/0015 pattern).

## §3 The slice chain in flight

commit A (this commit: the post-#106 five-area reconciliation + CLAIM-072 opened + record 64
minted; the branch pushed EARLY per the standing owner instruction) → the RED (test_journal.py
alone, tests-only per LAW-11) → the typed red-record binding → the GREEN (the write command + the
read arms + migration 0016 + whatever the substrate requires) → the measured set → the SEV
round(s) → the artifact finalize → the artifact re-bind → the push → the PR → the five checks →
the merge-gate review (D-042 (1a)) → **the merge under INT-145** → the post-merge verification →
the following P4-C slices + P4-D..F — NO PAUSE EVEN FOR UPDATES (INT-146).
