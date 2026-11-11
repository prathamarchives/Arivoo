# Record 67 — P4-D slice one: the stable @-reference system (the RTM §2 item 10 reservation landing)

> STATUS: SESSION ENGINEERING RECORD (2026-11-10; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 91. PR #109 MERGED (the P4-C slice five reading-list surface,
> under INT-145); **P4-C COMPLETE** (the exit check at the #109 merge); the CLAIM-075 PR
> follows at this slice's end.

Session 41 (2026-11-10), CLAIM-075, opened at the merged head `4a750db` (the PR #109 merge —
P4-C slice five). Record 66 carries the reading-list account (complete, §5 closed at this
commit); this record carries the stable-reference slice's contract + chain — P4-D's opening.

## §1 The #109 merge close (CLAIM-074 LANDED — P4-C slice five) + THE P4-C EXIT

PR #109 merged at 2026-11-10 as `4a750db327fac4d9b7540a6029d74b48e88ce99d` under INT-145's
standing authorization: the five checks green at the exact final head `982b273` AND on the
merge commit `4a750db` (all observed live — re-read at the exact head immediately before the
merge); the merge-gate review D-042 (1a) `5846447048`; CodeRabbit the skip state (noted per
D-042 (1c)); zero review threads; the flip/merge/restore with the protections re-read
byte-equivalent; the branch deleted; 0 open PRs. No ARV-SEV-003 round — the digest bound
LAST (`65c0d342`) + the local trusted-gate reproduction green before the push (run-08, first
attempt — the anchored BASE driver at the current main, trusted_gate.py + gate.py proven
byte-identical across the mains). THE ONE-ROUND SEV CHAIN: round 1 (agent-caf66233) PASS
zero open P0/P1 (~92 live probes; F-074-1 the P2 ROUTED — the pre-existing family-wide
leading-dash argv-value class; F-074-2/3/4 the P3s). The full account: record 66 §4 + CLAIM-074's
rule-4 close row.

**THE P4-C EXIT CHECK (2026-11-10, at the #109 merge):** every required P4-C backend
behavior is landed and verified — the library membership (CLAIM-070: list-library over
arv.source), the current-reading state (CLAIM-070: get-reading-state, the derived view), the
reading lists and collections (CLAIM-074: the reading-list surface — the post-#108
reconciliation's landing, the North Star owner words' third surface), the approved
session/dwell behavior (CLAIM-071: migration 0015 + record_session +
list-session-events, D-010's boundary structural), the journal and raw/creative blocks
(CLAIM-072: migration 0016 + the write/read arms; CLAIM-073: the outbox ride — the enqueue
and the delivery together). **P4-C COMPLETE.**

## §2 The stable-reference slice's contract (the RTM §2 item 10 reservation, one phase deep)

**The letter (the RTM's Phase-4 reservation):** "@Reference — a stable-identity reference
with version-aware resolution states and privacy-preserving refusal (never revealing
another owner's object existence)." The North Star's own words: "There I can reference
these. I can also reference things while reading... I can reference a specific passage
that I remember, or reference the article to the book, or the book to the article."

**The design boundary:**
- **The logical target identity separated from the selected historical revision** — a
  reference names an ENTITY (its stable uuid identity); the version pinning is EXPLICIT
  (`@id@rev` — the note machine's CLAIM-057 grammar), never an implicit retarget.
- **The six explicit states** (the typed resolution, never a guess):
  `current` (the target live, the unpinned reference resolving to the current revision) |
  `historical` (a pinned revision resolving exactly as pinned) | `tombstoned` (the target
  lifecycle-tombstoned — the reference answers the tombstone state, never silent
  retargeting) | `unavailable` (the pinned revision superseded-but-retained or the target
  absent from the current view) | `ambiguous` (the locator matches multiple candidates —
  the anchor-resolution class) | `purged` (the governed purge invalidated the access).
- **The entity-family coverage:** Work, Source, Anchor, Highlight, Bookmark, Note, Journal
  block — the reference resolution is ONE surface over the landed families (the
  note-reference machine's resolution is the substrate this composes, never a second
  implementation).
- **The laws:** references survive title changes (the identity is the uuid); stale
  references never silently retarget; cross-owner targets refuse without existence leaks
  (the no-oracle byte-equal); purge invalidates access; malformed and dangling references
  receive typed refusals; imported hostile strings never acquire authority (a reference
  string is DATA, never an instruction).
- **The proof boundary:** the behavior proven through the backend command/API surface
  (the resolution read arm + the note-machine composition).

**THE BOUNDED EXCLUSIONS (elaborated at the RED):** no agent-facing reference resolution
(P4-E's increment); no reference graph queries (P5's world); no new entity families; no
reader-client work (P4-B's repo).

## §3 The executed chain

commit A (`b0efb68`: the post-#109 five-area reconciliation + THE P4-C EXIT CHECK recorded +
CLAIM-075 opened + record 67 minted; the branch pushed EARLY per the standing owner
instruction) → **the RED** (`37917ec`: the REF suite authored tests-only per LAW-11 — 687
lines, the REF-01..06 registry: the seven-family round-trip with the frozen answer shape and
the identity/revision separation; the version pinning and the historical state with the
note-machine compose probe; the tombstoned state across the three lifecycle families for
unpinned AND pinned forms; the unavailable/ambiguous anchor compose; the purged state and the
precedence with the 0013 closed-vocabulary substrate pin; the typed refusals, the no-oracle
byte-equality for every family, the hostile-string battery, and the six-state exclusivity
law; the gate.py TESTS registration riding the same commit, the ARV-RED-008 class; red-01.txt:
exit 1, ARV-TEST-000 machinery-absent) → the typed red-record binding (`114231b`) → **the
amendment** (`e7aac7d`: the disclosed pre-GREEN suite repair — the refs attach PER REVISION
so the revise_note calls must restate the --ref pin; the STRENGTHENER form, the probe reading
the CURRENT revision's own stored reference) → **the GREEN** (`6fde990`: query.py's
resolve-reference — the typed six-state answer; the grammar composed from the CLAIM-057
substrate with the pin OPTIONAL at the resolution boundary; THE PRECEDENCE purge >
tombstone > revision resolution; the anchor compose via _verdict verbatim; the per-family
state read in ONE statement ONE snapshot; the no-oracle ARV-REF-001 byte-equal; the
malformed ARV-REF-002 with the framing-safe repr echo; capability.py's references
reserved-surface row; plus the two disclosed suite repairs riding the same commit — the
anchor-of-revision-1 selection and the 0013 CHECK name) → the measured set at the GREEN tree
(runs 01-04: the suite x3 + make verify, the canonical layer 54/0) → **the SEV round 1**
(agent-0b1de793: PASS zero open P0/P1 — 108 live probes + 13 static checks; the two
NEW-CODE findings: F-075-1 the P2 all-digits-oversize-pin untyped crash, F-075-2 the P3
trailing-newline uuid; the three routed/accepted P3s: F-075-3 the substrate's isdigit law
composed verbatim, F-075-4 the uppercase-echo debt, F-075-5 the landed resolve-anchor's
purge-unawareness routed to D-011) → **the SEV round-1 repair** (the current head: the
length bound BEFORE int() — 18 digits, far above any plausible revision, far below CPython's
4300-digit crash boundary; the \Z regex anchor — the substrate's own $ form routed to the
_nte_canon_id family-wide slice, the F-072-1 precedent; the two suite strengtheners in the
hostile battery, the typed third amendment) → the repair-tree measured set (runs 05-08: the
suite x3 + make verify) → **the SEV round 2** (agent-c927a15b: PASS — both repaired classes
verified closed live with the exact boundary behavior (the 18-digit pin still parses, the
19-digit refuses), no new findings, the routing honest, the amendment chain typed; 46 live
probes + 1 independent suite run + 12 static checks) → the artifact finalize → the artifact
re-bind → the push → the PR → the five checks → the merge-gate review → **the merge under
INT-145** → the post-merge verification → P4-D's remaining increments → P4-E → P4-F → the
Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).

## §4 The SEV account (the two-round chain)

**Round 1 (agent-0b1de793, PASS zero open P0/P1).** The reviewer independently reproduced
on scratch databases of their own construction: the seven-family current round-trip with the
frozen one-line JSON shape and the bare/revisioned split; the historical state on all four
revisioned families serving exactly-as-pinned with current_revision alongside; the
tombstoned state across the three lifecycle families for unpinned AND pinned forms with no
revision/resolved_ref/content keys; the unavailable state for BOTH no-current-generation and
their OWN stale-generation fixture, and the ambiguous state from a replicated ANC-05 drift
plant; the purged state over note/highlight/work/source/anchor beating tombstone, ambiguity,
and pins, with B's ledger rows RLS-invisible to A; the no-oracle as RAW-BYTES equality for
all seven families plus the nonexistent-revision class; a 20-form hostile battery all
ARV-REF-002 at exit 1 with zero answer lines; the command_log count unchanged across every
resolution probe; the 0010/0013 substrate boundaries unchanged; the compose agreement between
resolve-anchor and resolve-reference on four anchors of all four verdict classes; the RED
reproduced independently from the archived 37917ec tree with the binding hash matching; the
amendment chain hashes traced to the actual git trees. THE FINDINGS: F-075-1 (P2) the
all-digits pin ≥4301 chars crashed _ref_parse with an uncaught ValueError (CPython's
int-str limit) instead of the typed ARV-REF-002 — fail-closed but untyped; F-075-2 (P3) a
trailing-newline uuid passed the $-anchored regex and died at the SQL cast as an untyped
ARV-QRY-002; F-075-3 (P3, ROUTED) the unicode-digit/leading-zero pin normalization — the
substrate's own isdigit law (commands.py:1219) composed verbatim, narrowing it here would be
the forbidden second implementation; F-075-4 (P3, owner-accepted-debt) the uppercase-hex
uuid echo case-preserved (RFC 4122 case-insensitivity, cosmetic); F-075-5 (P3, ROUTED) the
landed resolve-anchor arm does not consult the purge ledger — pre-existing landed behavior
outside this slice's diff, routed to D-011's governed-purge command slice.

**The repair (applied in-slice, the CLAIM-058/071 precedent):** F-075-1 closed by the length
bound BEFORE int() (len(rev) > 18 → the typed malformed refusal — every plausible pin's
behavior identical, the crash boundary unreachable); F-075-2 closed by the \Z anchor in
_REF_UUID_RE (the substrate's own copy routed, never modified — the F-072-1 routing
precedent); the two SEV-devised hostile forms added to the suite's battery as the typed
third amendment.

**Round 2 (agent-c927a15b, PASS).** The repair verified by fresh eyes: both classes closed
live (the 5000/4301-digit pins and the trailing-newline/leading-newline/trailing-char uuids
all the typed ARV-REF-002, zero tracebacks); the boundary exact (the 18-digit pin still
PARSES — answering the dangling ARV-REF-001 class, not malformed; a 19-digit pin refuses);
no plausible-pin regression (pins @1..@3 unchanged); the routing honest (git diff over
commands.py EMPTY); the amendment chain typed and tree-verified. The spot-regression battery:
all six states reproduced, the no-oracle byte-equal, the command_log-unchanged law. No new
findings.

## §5 The close (CLAIM-075 LANDED — at this commit, the post-#110 reconciliation)

PR #110 merged at 2026-11-11 as `af95e3c0940fd0eac3eda4339ded0cd5c80212cd` under INT-145's
standing authorization: the five checks green at the exact final head `7f164c20` AND on the
merge commit `af95e3c0` (all observed live — re-read at the exact head immediately before the
merge, and the post-merge run on the merge commit re-observed green); the merge-gate review
D-042 (1a) `5858438424` (posted 2026-11-11T12:06:21Z — the substantive host review engaging
the actual diff: the six-state precedence, the no-oracle, the hostile-string law, the compose
law, the one-statement read, the evidence integrity, each verified against the live tree +
the reviewer's own fresh probes — the REF suite re-run GREEN at the final tree, the 18/19-pin
boundary, the no-oracle byte-equality, the hostile metacharacter refusal); CodeRabbit the
skip state (noted per D-042 (1c)); zero review threads; the flip/merge/restore with the
protections re-read byte-equivalent (approving=1, dismiss_stale=true, strict=true, the five
contexts, enforce_admins, no force pushes, no deletions); the branch deleted; 0 open PRs; only
main. No ARV-SEV-003 round — the digest bound LAST (`b712dcf2`, validate_report GREEN
re-verified at the re-bind head) + the local trusted-gate reproduction green before the push
(run-10, FIRST attempt — the anchored BASE driver sha256-verified against the trusted base
reset to the current main `4a750db`, the exact S4c path the CI runs). THE TWO-ROUND SEV
CHAIN (the account in §4): round 1 (agent-0b1de793) PASS zero open P0/P1 — 108 live probes +
13 static checks, every claimed behavior reproduced on the reviewer's own scratch rigs, the
RED independently reproduced from the archived tree; F-075-1 the P2 (the all-digits oversize
pin's untyped crash) + F-075-2 the P3 (the trailing-newline uuid) both REPAIRED in-slice;
F-075-3/4/5 the P3s routed/accepted. Round 2 (agent-c927a15b) PASS — both repairs verified
closed live with the exact boundary, no new findings. Zero open P0/P1/P2 at the final tree.

**The routed follow-ups:** F-075-3 (the substrate's isdigit pin law — the grammar owner's
slice), F-075-4 (the uppercase-echo cosmetic debt, owner-accepted), F-075-5 (the landed
resolve-anchor's purge-unawareness — D-011's governed-purge command slice), + the standing
family-wide classes (the F-072-1 `_nte_canon_id` pattern incl. the substrate's own
`$`-anchored `_UUID_RE`, the F-074-1 leading-dash argv-value family, the F-073-6 import
staging residue).

**THE P4-D REMAINING-INCREMENT CHECK (at this merge):** the 4D row's resolution system is
landed (the six states, the seven-family coverage, the no-oracle, the version pinning, the
hostile-string law). ONE named gap remains from CLAIM-075's own not-verified list: the note
machine's WRITE vocabulary stays at its five kinds — `bookmark` and `journal_block`
references are RESOLVABLE through the surface but not yet WRITABLE through note `--ref`
(the 0010 CHECK + `_REF_KINDS` would need the widening — a substrate change never made in
the resolution slice). The reference system is not complete over the seven families until a
reference to a bookmark or a journal block can be STORED; CLAIM-076 (P4-D slice two — the
note-reference write completion) takes exactly that bounded increment, then the P4-D exit
check. The full account: CLAIM-075's rule-4 close row + this record. Record 68 carries the
write-completion slice's contract + chain.
