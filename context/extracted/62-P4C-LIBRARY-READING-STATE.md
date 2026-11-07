# Record 62 — P4-C slice one: the library + current-reading state (over the existing substrate)

> STATUS: SESSION ENGINEERING RECORD (2026-11-06; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 86. PR #104 MERGED (the P4-B slice one client-acceptance path, under INT-145); the CLAIM-070 PR follows at this slice's end.

Session 41 (2026-11-06), CLAIM-070, opened at the merged head `9c138a0` (the PR #104 merge — P4-B
slice one). Record 61 carries the client-acceptance account (complete, §4 closed); this record
carries the library slice's contract + chain.

## §1 The #104 merge close (CLAIM-069 LANDED — P4-B slice one)

PR #104 (CLAIM-069 — the client-shaped adversarial acceptance path) merged at 2026-11-06T21:29:06Z
as `9c138a0e10a349a129a31be539bf35f372ee189d` under INT-145's standing authorization: the five
checks green at the exact final head `cd32c19` AND on the merge commit (all observed live); the
merge-gate review D-042 (1a) `5807263269`; the flip/merge/restore with the protections re-read
byte-equivalent; the branch deleted; 0 open PRs; only main. No ARV-SEV-003 round — the digest
bound LAST (`b9b397f0`) + the local trusted-gate reproduction green BEFORE the push (run-07,
first attempt). THE ONE-ROUND SEV CHAIN: agent-5e8c31a7 PASS, zero open P0/P1/P2 (the
clean-client law verified by full-file read — every subprocess target a repo CLI; the walk + the
uncertain-ack + the no-oracle observations reproduced from the raw CLI outputs on the reviewer's
own scratch DB; the sha chain closed; the three amendments additive/strengthening — the NTE-010
wrong-code fix confirmed against commands.py; all 13 diff paths declared; four P3 notes
routed/recorded in notverified). The full account: record 61 §4 + CLAIM-069's rule-4 close row +
WORKLOG Task 86.

## §2 The library slice's contract (PLAN's 4C row elaborated one phase deep at P4-B slice one's landing)

**The letter:** stable library membership + the current-reading state, over the EXISTING
substrate:

- **The library list** — the owner's imported sources as a stable, bounded, paginated list (the
  list-library read arm on the P4-00b contract: the versioned header, the `# more=` markers, the
  keyset cursor, the api_version field) — RLS the owner boundary, the no-oracle unchanged.
- **The current-reading state** — ONE read arm deriving the owner's reading surface from the
  LANDED position rows: the sources with a saved position (the last-saved position + its
  generation binding + the matches flag), the no-position sources (the honest not-yet-open
  state), never a second position path (the derived view; no new table unless the substrate
  requires it — the migration slot reserved).

**The design boundary (the acceptance the RED pins):** the library arm bounded/paginated/
api_version'd; the current-reading state derived with the generation binding honest; the owner
isolation (owner B sees only B's); the reader-client exclusion held (P4-B's repo).

## §3 The slice chain in flight

commit A (this commit: the post-#104 five-area reconciliation + CLAIM-070 opened + record 62
minted; the branch pushed EARLY per the standing owner instruction) → the RED (test_library.py
alone at `9c138a0`, tests-only per LAW-11) → the typed red-record binding → the GREEN → the
measured set → the SEV round(s) → the artifact finalize → the artifact re-bind → the push → the
PR → the five checks → the merge-gate review (D-042 (1a)) → **the merge under INT-145** → the
post-merge verification → the following P4-C slices + P4-D..F — NO PAUSE EVEN FOR UPDATES
(INT-146).

## §4 The #105 merge close (CLAIM-070 LANDED — P4-C slice one)

PR #105 (CLAIM-070 — the library + current-reading state) merged at 2026-11-07T06:12:10Z as
`fd6fb9fb6a9133d39a324447cbc4f0defae37951` under INT-145's standing authorization: the five
checks green at the exact final head `12510a9` AND on the merge commit (all observed live;
the post-merge five-check run at the merge commit green — all suites + the gate + the
canonical layer 54/0); the merge-gate review D-042 (1a) `5810504474`; the flip/merge/restore
with the protections re-read byte-equivalent; the branch deleted; 0 open PRs; only main. No
ARV-SEV-003 round — the digest bound LAST (`db023430`) + the local trusted-gate reproduction
green BEFORE the push (run-08; run-07 the DISCLOSED first-attempt RED — the
sheet-by-construction lag observed honestly, kept in place, never deleted). THE ONE-ROUND SEV
CHAIN: round 1 (agent-4f2b9d6a) PASS, zero open P0/P1/P2 — the RED reproduced at the archived
`35fae66` tree; the no-second-path law verified structurally (`_position_row` the single
construction home) and behaviorally (byte-equal rows on saved/no-position/re-extracted
states); 30 adversarial probes on the reviewer's own scratch DB (the isolation including the
cross-owner cursor + hostile owners, the 16 malformed bound combos, the ghost-uuid + four
uuid spellings, the failed-import library invariance, the saved-set == the audit's distinct
set); the sha chain closed with ZERO amendments (the RED contract held as written — the LIB
suite landed green on the first implementation attempt); five P3 notes routed/recorded in
notverified. LANDED: query.py `list-library` (the owner's imported sources on the P4-00b
list contract — membership IS the arv.source set, rows BORN complete at import, the failed
import's dead-letter the journal's) + query.py `get-reading-state` (the derived
current-reading view over the landed position rows — every row get-position's own answer
through the ONE shared `_position_row` builder; bounded/paginated through the shared
`_page_args`) + capability.py's library/current-reading reserved-surface row (owner_phase
P4-C); NO new table, NO migration 0015 (the declared slot unused per the card's own "only if
the substrate requires it"). The full account: this record + CLAIM-070's rule-4 close row +
WORKLOG Task 87. RECORD 62 COMPLETE.
