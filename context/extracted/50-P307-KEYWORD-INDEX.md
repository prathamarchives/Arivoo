# 50 — P307-KEYWORD-INDEX
> STATUS: SESSION ENGINEERING RECORD (2026-11-04; the standing do-not-stop chain INT-134..145; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 74. PRs: #92 MERGED this session (the CLAIM-057 reference machine, under INT-145); the CLAIM-058 PR follows at this slice's end.

## 1. What the owner asked (verbatim — owner turn 41, 2026-11-04)

The standing directive (preserved at `context/reviews/arivoo-merge-authorization-2026-11-04.md`, INT-145): "resume, merge it yourself after checks. dont stop to make me merge manually. now resume and dont stop until phase 4 is ready to go" — the merge authorization exercised twice this session (PR #91 at `36e34920`, PR #92 at `b698608d`), the no-stop horizon continuing (the Phase 3 exit gate + P4-00 minimum, the INT-144 Phase-4-completion ceiling standing). This slice (CLAIM-058, P3-07) is the next card in that chain. No new owner question; no stop-work permission.

## 2. Starting state (every fact re-observed live, INT-104)

- main = `b698608d52cb036027fd410e3737d1f11903cb43` = the PR #92 merge (merged under INT-145; the post-merge five-check run ALL GREEN observed live; the protections re-read byte-equivalent after the flip/merge/restore; the branch deleted 204; 0 open PRs; only main on the remote).
- P3-06 FULLY LANDED (both slices): CLAIM-056 (the note core, #91/`36e34920`) + CLAIM-057 (the version-aware reference machine, #92/`b698608d` — the SEV round 1 PASS zero open P0/P1 with F1/F2 routed, the merge-gate review `5768367044`, the 6-record sheet, the NTR-01..12 suite).
- The first #92 merge attempt raced the protection flip's propagation (the 405 "at least 1 approving review" refusal — the flip had returned 200 but not yet propagated); the clean re-flip + immediate read-back (count 0) + merge succeeded; the restore landed; byte-equivalence re-verified. Recorded as the eventual-consistency class (the #91 500/405 window's sibling).
- The rig live (PostgreSQL 17.11, port 5433); `make verify` GREEN at `b698608d`'s tree (the #92 post-merge observation + the artifact head runs).

## 3. Task and scope

CLAIM-058 — P3-07: the keyword findability machine. A REBUILDABLE keyword index over the committed sources/passages/captures/notes within the currently supported formats: the derived layer (never an authority — delete/rebuild restores expected results), the defined search contract (searchable or explicit lag/failure, never a silent miss), stale-entry handling after revision, tombstone filtering, owner filter, encoding/tokenization boundaries, the known-query pin. RED-first at `b698608d`. The bounded exclusions: the semantic/vector rungs P5's; the outbox/sync P3-08's; the export/restore P3-09's; the governed purge D-011's; no refactor of the landed note/reference families.

## 4. Results (in flight — extended at the records commit)

- CLAIM-057's rule-4 close row + the five-area re-derivation landed in this slice's commit A (the same-session close work, rule 4).
- The P3-07 design (the derived-index contract): the index rows are DERIVED from the authoritative rows (source passages via the extraction generations; captures: highlights/bookmarks/notes through their CURRENT revisions only — tombstoned filtered by the parity rule); the search surface rides query.py (a `search` arm); the rebuild is a command that re-derives the whole index from the authored rows (the acceptance pin); the indexing lag/failure contract is explicit (the index write rides the same transaction as the capture — local indexing is synchronous on this rig, with the lag contract named for the future sync rungs).

## 5. Files changed (in flight)

(the slice's files — extended at the records commit)

## 6. Failures and honest limits (named, never hidden)

- The #92 merge's first attempt refused (the protection-flip propagation race): the state re-observed (count read-back 1 → the flip had not propagated), re-flipped with an immediate read-back (count 0), merged clean, restored — the eventual-consistency class recorded (the #91 500/405 window's sibling; the merge path's standing caveat).
- The SEV round's F1/F2 (the --ref target UUID-spelling canonicalization class) ROUTED to a small follow-up slice (never silently dropped — record 49 §9).

## 7. Verification evidence

(the measured set's run records — extended at the records commit; the base evidence: the #92 post-merge five checks green observed live, the protections byte-equivalent)

## 8. What is NOT verified (the honest fences)

- The routed F1/F2 follow-up; the standing routed sibling classes from #91/#92; Q6–Q12 + D-014 unchanged (each blocking only its named dependents).

## 9. Routed follow-ups

- F1/F2 (the --ref target UUID-spelling canonicalization — the `_nte_canon_id` mirror over ref targets inside `_nte_refs`): one small follow-up slice.
- The standing sibling classes (record 48 §9 + record 47 §9): the landed read arms' two-read shape; the bookmark raw-spelling boundary; F4's phantom/gap revision-append guards.

## 10. Session boundary

(extended at session exit)

## 11. Next action

The P3-07 chain: the RED (the keyword-index suite at `b698608d`, machinery-absent) → the GREEN (migration 0011 + the index machinery + the search surface + the rebuild command) → the measured set → the records → the push → the PR → the five checks → the SEV round → the artifact re-bind → the merge-gate review → the merge under INT-145 → P3-08 (outbox/sync) → P3-09 (export/restore) → the Phase 3 exit gate → P4-00 — NO PAUSE until Phase 4 is ready to go (turn 41).
