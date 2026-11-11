# Record 68 — P4-D slice two: the note-reference write completion (the seven-family @-reference system's write boundary)

> STATUS: SESSION ENGINEERING RECORD (2026-11-11; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 92. PR #110 MERGED (the P4-D slice one stable @-reference
> system, under INT-145); record 67 §5 closed at this commit (the post-#110 reconciliation).

Session 41 (2026-11-11), CLAIM-076, opened at the merged head `af95e3c0` (the PR #110 merge —
P4-D slice one). Record 67 carries the stable-reference account (complete, §5 closed at this
commit); this record carries the write-completion slice's contract + chain — P4-D's closing
slice.

## §1 The #110 merge close (CLAIM-075 LANDED — P4-D slice one)

PR #110 merged at 2026-11-11 as `af95e3c0940fd0eac3eda4339ded0cd5c80212cd` under INT-145's
standing authorization: the five checks green at the exact final head `7f164c20` AND on the
merge commit `af95e3c0` (all observed live); the merge-gate review D-042 (1a) `5858438424`;
CodeRabbit the skip state (noted per D-042 (1c)); zero review threads; the flip/merge/restore
with the protections re-read byte-equivalent; the branch deleted; 0 open PRs; only main. No
ARV-SEV-003 round — the digest bound LAST (`b712dcf2`) + the local trusted-gate reproduction
green before the push (run-10, first attempt). THE TWO-ROUND SEV CHAIN: round 1
(agent-0b1de793) PASS zero open P0/P1 (108 live probes + 13 static checks; F-075-1 the P2
REPAIRED — the all-digits oversize pin's length bound before int(); F-075-2 the P3 REPAIRED —
the \Z regex anchor; F-075-3/4/5 the P3s routed/accepted); round 2 (agent-c927a15b) PASS —
both repairs verified closed live with the exact boundary (the 18-digit pin parses, the
19-digit refuses), no new findings. The full account: record 67 §4/§5 + CLAIM-075's rule-4
close row.

**THE P4-D REMAINING-INCREMENT CHECK (at the #110 merge):** the resolution system is landed;
ONE named gap remains — the note machine's WRITE vocabulary (the 0010 CHECK + `_REF_KINDS`
at five kinds; `bookmark`/`journal_block` references resolvable but not storable). CLAIM-076
takes exactly that increment; the P4-D exit check follows its merge.

## §2 The write-completion slice's contract (the RTM §2 item 10 reservation's write boundary, one phase deep)

**The letter:** the @Reference reservation covers the seven landed families (CLAIM-075's
entity-family coverage: Work, Source, Anchor, Highlight, Bookmark, Note, Journal block). A
reference system where two of the seven families can be RESOLVED but never STORED is
incomplete: the note machine is the only write surface for references today (the
CLAIM-057 substrate), and its vocabulary predates the bookmark/journal families' landing.

**The design boundary:**
- **Migration 0018** (the 0010 CHECK widening): `ref_kind` gains `'bookmark'` and
  `'journal_block'`; both join the REVISIONED arm of the shape CHECK
  (`ref_revision IS NOT NULL AND ref_revision >= 1` — both families are revision tables;
  a stored reference pins the immutable (id, revision) pair, version-aware by construction,
  the substrate's own law). The drop-and-re-add rides ONE transaction with the
  `-- arv-baseline-bump` directive (the ARV-MIG-003 paper trail; the destructive class is
  the constraint drop, never data).
- **commands.py**: `_REF_KINDS` widened to the seven kinds; `_nte_refs`'s revision branch
  (bookmark/journal_block REQUIRE the `@rev` pin — the same shape law as highlight/note);
  `_nte_check_targets` gains the two arms (the same RLS-scoped existence-at-revision read,
  the same ARV-NTE-003 no-oracle refusal — absent, cross-owner, and nonexistent-revision
  the SAME refusal, never a side channel).
- **The read arms UNCHANGED by construction**: get-note's refs aggregation is kind-agnostic
  (it renders whatever rows exist); resolve-reference already resolves all seven families
  (CLAIM-075 landed). The sync delivery `_refs_args` is kind-generic (the translated target
  through the identity bridge) — verified live by the SEV round, never assumed.
- **The substrate boundaries unchanged**: the 0010 UNIQUE (the set semantics), the
  append-only triggers, RLS, the grants — the widening touches ONLY the two CHECK
  constraints' vocabularies, never the shape of the machine.

**The laws carried:** the set semantics (one reference per target per revision);
replacement semantics (each note revision carries its own set); the canonical body (the
sorted reference set — a shuffled CLI order is the same command, LAW-23); the pinned
immutable (id, revision) pair; the no-oracle at the write boundary; the hostile-string law
(a reference string is data).

**THE BOUNDED EXCLUSIONS:** no new entity families; no reference graph queries (P5's
world); no agent-facing resolution (P4-E's increment); no widening of the 0013 purge
ledger vocabulary; no tombstone machine on journal blocks (the §3.3 increment, D-011's
question); no reader-client work (P4-B's repo).

## §3 The executed chain

(In flight — appended as the slice executes.)

## §4 The SEV account

(In flight — appended at the rounds.)

## §5 The close

(Appended at the merge.)
