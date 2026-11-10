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

## §3 The slice chain in flight

commit A (this commit: the post-#109 five-area reconciliation + THE P4-C EXIT CHECK
recorded + CLAIM-075 opened + record 67 minted; the branch pushed EARLY per the standing
owner instruction) → the RED (the REF suite authored tests-only per LAW-11 against the
machinery-absent tree — the ARV-TEST-000 machinery-absent probe + the behavioral pins over
the six states, the entity-family coverage, the version pinning, the no-oracles, the
hostile-string law) → the typed red-record binding (make red) → the GREEN (the resolution
surface + the state machine — the design deciding whether migration 0018 is truly
required; the expectation: NO new table, the resolution DERIVED over the landed entity
rows) → the measured set → the SEV round(s) → the artifact finalize → the artifact
re-bind → the push → the PR → the five checks → the merge-gate review → **the merge under
INT-145** → the post-merge verification → P4-D's remaining increments → P4-E → P4-F → the
Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).
