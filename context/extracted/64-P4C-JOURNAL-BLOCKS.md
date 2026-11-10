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

## §4 The LAW-05 split (the in-slice account, 2026-11-09)

The first PR-mode gate run at the pre-split head `806ef04` REFUSED — the observed codes:
ARV-SIZE-002 (422 source lines > 400) + ARV-SCOPE-002/ARV-CLM-002 (test_sync.py outside the
declared scope). The law's own repair — "split the slice", the P3-06 two-slice precedent (record
47 §43: the reference machine re-homed to CLAIM-057; record 30 §67 and record 22 §641 the same
class) — executed: **the journal sync delivery re-homes to the FOLLOWING slice (CLAIM-073)** —
the `_SYNC_COMMANDS` membership (the enqueue) AND `sync.py`'s `_cli_args` journal branches AND
the identity bridge's address-form extension (the `IN (id, id||'@1')` create-ref match) AND the
SYN-20 pin land TOGETHER there. The enqueue-without-delivery intermediate state is the dead-letter
P1 class the CLAIM-066/071 SEV rounds established law for — the split NEVER creates it: this
slice's tree carries NO journal outbox rows at all (the JNL-04 pin's ZERO-outbox-row form), and
CLAIM-073 adds the enqueue and the delivery in one slice.

The re-homed work's own history (kept true, never rewritten): the SYN-20 pin was authored and
observed RED at `838b1e9` (red-02.txt — the dead letter live, the CLAIM-071 round-1 F1 class
found pre-SEV by the executor), GREEN at `806ef04` (the branches + the bridge extension), then
RE-HOMED at the split commit — its RED re-observes at CLAIM-073's own commit (the P3-06
re-home precedent). The SEV round-1 (agent-34277f24, PASS zero P0/P1/P2 over the ten-commit
pre-split chain) reviewed the pre-split tree; the split-tree verification follows this section
(the re-run suites + the SEV round over the SPLIT diff, exactly the P3-06 "split-tree measured
set" pattern).

## §5 The #107 merge close (CLAIM-072 LANDED — P4-C slice three, 2026-11-10)

PR #107 merged as `7286b3cf2555686476569e4c3663f7ecd2b8885e` under INT-145's standing
authorization (the agent-performed merge after checks): the five required green at the exact
final head `d1c1190` AND on the merge commit — all observed live (canonical-layer, head-tools,
harness, harness-suites, harness-trusted, success on both heads; the closing agent additionally
re-ran the JNL suite locally at `d1c1190` — JNL-01..06 GREEN exit 0 — and `validate_report` —
codes `[]`, GREEN). The merge-gate review D-042 (1a) posted as review `5840270161` BEFORE the
merge (the substantive risk surface engaged: the lossless law, the split's no-dead-letter window,
the serialized revision + the 0016 guards read at the migration, the no-oracle discipline, the
test provenance + digest integrity, the three-round SEV chain).

THE CODERABBIT CHAIN (D-042 (1b), this PR's review coverage): three Minor findings, each with an
explicit in-thread disposition BEFORE the merge —
- `4512207526` (the `standard_conforming_strings` hypothetical): reasoned no-fix, evidence-based
  (live probes at `d1c1190`: the setting `on` as the spine's own session flags observe it —
  `psql -X -A -t` against the rig's PG 17.11; a backslash-heavy raw body ENDING IN A TRAILING
  BACKSLASH written through the real spine — exit 0, the frozen ack grammar — and read back
  byte-identical, 92/92). CodeRabbit's correction ACCEPTED and recorded in-thread: under the
  counterfactual `off`, the embedded-escape class (`\n` et al.) could land LOSSY, not merely
  fail closed — the disposition's counterfactual statement sharpened; the operative conclusion
  unchanged (the premise exists in no supported configuration); the named follow-up (a transport
  GUC pin at `Session` construction — a cross-family change, its own bounded slice) stands.
- `4512207541` (the malformed journal IDs): fixed-in-named-followup-slice — the documented
  raw-cast class (SEV round-1 F-072-1/F-072-5, the `_nte_canon_id` docstring's own routing,
  records 47 §9/48 §9); the live probe reproduced the exact documented behavior (exit 1,
  `ARV-CMD-010`, ZERO effect); the journal arm shares the one canonicalization home — a
  journal-only pre-validation would fork the pattern.
- `4512207548` (the buffered history read): reasoned no-fix — the export-ready whole-history
  design for ONE identity (the JNL-04 pin; the current view rebuilds from history ALONE); the
  bounded-response law rides the list arms (P4-00b); a streaming fork would diverge the shared
  ANC-10 framing across every read arm.
All three threads RESOLVED after the dispositions (the host's resolve-before-merge gate — the
merge API refused with "All comments must be resolved" until the resolutions landed; the
dispositions are the resolutions' substance).

The flip/merge/restore with the protections re-read byte-equivalent after the restore
(approving=1, dismiss_stale=true, require_code_owner=false, require_last_push_approval=false,
strict=true, the five contexts, enforce_admins, restrictions none, no force pushes, no
deletions). The branch deleted; 0 open PRs; only main on the remote. No ARV-SEV-003 round —
the digest bound LAST (`8c835b06`) + the local trusted-gate reproduction green before the push
(run-14, FIRST attempt).

The full account of the chain: CLAIMS.md's CLAIM-072 close row. The following slice:
CLAIM-073 (the journal sync delivery — the LAW-05 split's re-home), opened at `7286b3c` in
record 65.
