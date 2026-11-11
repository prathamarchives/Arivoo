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

commit A (`5358426`: the post-#110 five-area reconciliation + CLAIM-075's rule-4 close row +
THE P4-D REMAINING-INCREMENT CHECK recorded + CLAIM-076 opened + record 68 minted; the branch
pushed EARLY per the standing owner instruction) → **the RED** (`0537873`: the write-completion
pins authored tests-only per LAW-11 — NTR-13..16 in test_note_reference.py + SYN-23 in
test_sync.py; the DB-free machinery-absent probe at the module head (the parse refusal precedes
the spine's connection — the nonexistent probe database never reached); red-01.txt: exit 1,
ARV-TEST-000 machinery-absent + red-02.txt: exit 1, SYN-23 RED with SYN-01..22 green) → the
typed red-record binding (`bd58f08`: red-records.json amendments chained from both suites'
trusted prior states, the note carrying both observations) → **the amendment** (`ee6988b`: the
disclosed pre-GREEN suite repair — NTR-16's layer attribution corrected to the OBSERVED
substrate behavior: the BEFORE-INSERT guard fires BEFORE the CHECK constraints, so the
NULL-revision and out-of-vocabulary-with-a-non-note-target forms die at the guard's
ARV-NTE-003 (fail-closed at both layers), and the kind CHECK is proven by the note-target form
that PASSES the guard's ELSE arm; the row-count strengtheners added (every refusal zero-effect,
every admission exactly-once); the machinery-absent RED RE-OBSERVED at the stashed tree after
the repair — the claim honest, not asserted) → **the GREEN** (`b50f5d9`: migration 0018 — the
0010 CHECK widening with the constraint NAMES unchanged (NTR-11's audit form), exactly the two
kinds admitted to the kind CHECK, both joining the REVISIONED arm of the shape check, the
guard's per-kind arms widened (bookmark → arv.bookmark, journal_block → arv.journal_block, the
ELSE arm staying the note family's own), the arv-baseline-bump directive per ARV-MIG-003;
commands.py — `_REF_KINDS` the seven kinds, the revision branch (bookmark/journal_block REQUIRE
the @rev pin), `_nte_check_targets`' two arms (the same RLS-scoped existence-at-revision read,
the same ARV-NTE-003 no-oracle); sync.py — `_refs_args`' journal stem step (the translated @1
ADDRESS reduced to its uuid stem at the --ref boundary, the same address step the revise branch
takes, never the malformed double-pin); capability.py — the references row's write completion
named) → the measured set at the GREEN tree (runs 01-04: the NTR suite x3 GREEN exit 0 +
`make verify` exit 0 — the canonical layer 54/0) → **the SEV round 1** (agent-ca4c6f8e: PASS
zero open P0/P1 — 94 live probes on the reviewer's own scratch rigs + 13 static/git checks;
every claimed behavior reproduced: the seven-kind round-trip, the shape law, the no-oracle, the
0018 substrate with the guard routing proven by ADMISSION, the two-DB sync delivery with the
journal stem step and the ARV-SYN-009 dependency rest + recovery, the RED reproduced from the
archived tree with the binding digests matching; the NTR suite's output sha256 EQUAL to the
recorded runs' digests — determinism cross-checked; FOUR findings ALL ROUTED: F-076-1 the P2
(the all-digits oversize pin's untyped int() traceback — the commands.py twin of F-075-1,
pre-existing at the CLAIM-057 substrate, composed verbatim per the no-second-implementation
doctrine, fail-closed, routed to the substrate grammar owner), F-076-2 the P3 (the
trailing-newline uuid — the F-075-2 commands.py twin, routed to the _nte_canon_id family-wide
slice), F-076-3 the P3 (the isdigit/leading-zero normalization — the F-075-3 class; the
uppercase-hex write boundary carries NO echo debt — the UUID column canonicalizes), F-076-4
the P3 (the 008 message wording — pre-existing, cosmetic)) → the artifact finalize (this
commit: record 68 §3/§4 + the measured set's run records 01-04 + the SEV round-1 report) →
the artifact re-bind (sev.json + notverified + the proof sheet + the recorded PR-mode gate +
the local trusted-gate reproduction — the digest binding THIS content head, stable through the
run-dir-only re-bind commit per the anti-self-referentiality contract) → the push → the PR →
the five checks → the merge-gate review → **the merge under INT-145** → the post-merge
verification → **THE P4-D EXIT CHECK** → P4-E (the scoped agent reads) → P4-F (the recovery +
contract gate) → the Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).

## §4 The SEV account (the one-round chain)

**Round 1 (agent-ca4c6f8e, PASS zero open P0/P1).** The reviewer independently reproduced on
scratch databases of their own construction (94 live probes + 13 static/git checks, three rigs
— one single-DB and two two-DB sync rigs — all dropped at exit): the seven-kind write
round-trip (the mixed set committing with the per-revision rows, get-note's seven-entry
version-aware rendering, the STORED new-kind refs resolving historical-exactly-as-pinned with
current_revision alongside and current-at-current); the shape law (the bare forms, the
non-digit pin, the duplicate 008, the SHUFFLED replay LAW-23, the conflicting-set 409 — every
refusal zero-effect across note/reference/command_log rows); the no-oracle as BYTE equality
(absent vs cross-owner for both new kinds; the same-revision and pair-normalized
nonexistent-revision classes — with the reviewer's own honest method note: two over-strict
first-attempt probes kept visible in the log beside their corrected re-derivations); the 0018
substrate (the kind CHECK admitting exactly the seven, the shape CHECK's revisioned arm, the
constraint NAMES unchanged, the out-of-vocabulary INSERT dying at the kind CHECK via the
note-target form that passes the guard's ELSE arm, the NULL-revision forms dying at the guard,
the WELL-FORMED direct rows ADMITTED — the guard routing to arv.bookmark/arv.journal_block
proven by acceptance, never by prose; the ghost and cross-owner targets refused at the
substrate; the guard arms read from pg_proc.prosrc — the DB's own truth, not the file's); the
migration mechanics (clean apply + verify on five fresh databases, the constraint-only
statement set, the baseline-bump directive); the two-DB sync delivery (the sabotage pass's
ARV-SYN-009 dependency rest with NEVER a wrong-id delivery, the recovery pass acknowledging
everything, the server's @1 ADDRESS reduced to its stem — never a double-pin, a @3 pin
delivering as <stem>@3, the server's get-note rendering the SERVER's own ids, the server's
resolve-reference composing, zero local-uuid leakage, the second pass touching nothing); the
read arms unchanged (query.py's diff EMPTY; the directly-inserted rows rendering through the
ordinary get-note arm); the RED chain (both REDs reproduced at the archived 0537873 tree via
a detached worktree; the binding digests matching the files at HEAD; the amendment chain
typed); and the determinism cross-check (the reviewer's own NTR run's output sha256 EQUAL to
the recorded run-01/02/03 digests). THE FINDINGS, ALL ROUTED (the four classes are the CLAIM-057
substrate's own pre-existing grammar laws — the exact commands.py twins of the classes
CLAIM-075's SEV round 1 repaired in query.py and routed at commands.py — composed verbatim by
this slice's vocabulary widening per the never-a-second-implementation doctrine, every one
fail-closed with zero writes): F-076-1 the P2 (the oversize all-digits pin's untyped
ValueError — the F-075-1 twin; the repair, a pin-length bound before int(), belongs in the
family-wide `_nte_refs` grammar slice), F-076-2 the P3 (the trailing-newline uuid — the
F-075-2 twin, the $-anchored _UUID_RE, routed to the _nte_canon_id family-wide slice),
F-076-3 the P3 (the unicode-digit/leading-zero pin normalization — the F-075-3 class routed
to the grammar owner; the write boundary carries NO uppercase-echo debt: the UUID column
canonicalizes), F-076-4 the P3 (the 008 message wording — pre-existing, cosmetic, routed). No
P0, no P1: no data loss, no wrong answer, isolation held at both boundaries on both domains,
no dead letter.

## §5 The close

PR #111 merged at 2026-11-11 as `898b9f2ac6679c87f989b52d22941ba3b5f8b546` under INT-145's
standing authorization: the five checks green at the exact final head `c44d17b5` AND on the
merge commit `898b9f2a` (all observed live — re-read at the exact head immediately before the
merge, the post-merge run on the merge commit re-observed green); the merge-gate review D-042
(1a) `5859574863` (the substantive host review engaging the actual diff with the reviewer's
own fresh probes: the oversize-pin identical-class verification on the old vs new kind — the
routing honesty proven live; the seven-kind write + render + compose at the final tree);
CodeRabbit the skip state (noted per D-042 (1c)); zero review threads; the flip/merge/restore
with the protections re-read byte-equivalent (approving=1, dismiss_stale=true, strict=true,
the five contexts, enforce_admins, no force pushes, no deletions); the branch deleted; 0 open
PRs; only main. No ARV-SEV-003 round — the digest bound LAST (`8b5b0c86`, validate_report
GREEN re-verified at the re-bind head) + the local trusted-gate reproduction green before the
push (run-06, FIRST attempt — the anchored BASE driver sha256-verified against the trusted
base reset to the current main `af95e3c0`). THE ONE-ROUND SEV CHAIN (the account in §4):
agent-ca4c6f8e PASS zero open P0/P1 — 94 live probes + 13 static checks, four findings ALL
ROUTED to the substrate grammar owner (F-076-1 the P2 oversize-pin traceback — the F-075-1
commands.py twin, pre-existing, fail-closed; F-076-2/3/4 the P3s). The 6-record proof sheet,
no sheet-lag round.

**THE P4-D EXIT CHECK (2026-11-11, at the #111 merge):** every required P4-D backend behavior
is landed and verified — the stable @-reference RESOLUTION system (CLAIM-075: the six explicit
states, the version-aware resolution over the seven families, the logical identity separated
from the selected revision, the no-oracle byte-equal refusals, the purge precedence, the
hostile-string law, titles/labels changing without breaking references) + the WRITE completion
(CLAIM-076: the seven-kind note --ref vocabulary, the shape law and the no-oracle identical at
the write boundary, the guard routing to the families' own tables, the sync delivery through
the translated ids). A reference to every landed family is STORABLE and RESOLVABLE through the
one system. **P4-D COMPLETE.** Record 69 carries the scoped-agent-access slice (P4-E's
opening).
