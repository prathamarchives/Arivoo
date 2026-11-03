# Arivoo continuation directive — PR #91 round 3: the read-path race, the STATE threads, and the merge preparation (owner-forwarded, 2026-11-03)

> STATUS: REVIEW-ONLY ARTIFACT — 2026-11-03 (banner per D-024/D-022). Owner-forwarded continuation directive, preserved verbatim as received (the gateway-delivered chat message of 2026-11-03, owner turn 40): the execution orders ride the standing do-not-stop chain (INT-134..144) and the canonical decisions (D-037/D-041/D-042/D-043), never a second authority; the verbatim preservation home is record 48 §1. No new intent minted beyond the standing chain (the directive's own order: the work continues under INT-144's horizon; INT reservation only for genuinely new owner intent — none stated here beyond the continuation).

# Arivoo Systems Engineering Continuation Directive
## Active work: PR #91 / CLAIM-056 / P3-06 Note core

You are continuing work in `prathamarchives/Arivoo` as the systems-engineering orchestrator. This is an execution directive, not a request to write another plan and stop. Inspect, repair, test, independently verify, document, push, review, and continue to the next eligible claim. Continue through the Phase 4 exit gate, as required by INT-144. Do not interpret this horizon as permission to bypass evidence, owner decisions, review gates, or the merge process.

### 1. Reconstruct the exact live state

Repository: `prathamarchives/Arivoo`.

Current active branch: `slice/claim-056-p306-notes`.

Last observed head: `c58182c968628977035ffe96622e6f31988551b1`.

Base: `main` at `f86e52b293be0e6b531440d8e98676b09a289783`.

Active claim: CLAIM-056, P3-06 slice one, the Note core machine. PR: #91.

The branch is 16 commits ahead and zero behind its base. PR #91 is open and reported mergeable. The GitHub Actions `verify` run associated with the observed head completed successfully: all five required jobs passed (`canonical-layer`, `head-tools`, `harness`, `harness-suites`, `harness-trusted`). These results apply to the observed head only. Any subsequent change requires fresh evidence.

Before working, reload `AGENTS.md`, `STATE.md`, `CLAIMS.md`, the last three worklog entries, record 47, the P3-06 section of `PLAN.md`, and the relevant parts of `INTENT-LEDGER.md`, `LAWS.md`, `ENGINEERING.md`, and `RTM.md`. Follow the repository's actual read order and authority rules. Inspect the current branch, working tree, remote head, open claims, PR threads, and workflow runs. Do not assume this handoff is newer than the repository.

Stay on the existing CLAIM-056 branch. Do not create a competing claim or branch for work already covered by its scope. Do not merge PR #91.

### 2. Repair the Note read-path race before merge

Review `harness/query.py`, especially `NOTE_SQL`, `NOTESTATE_SQL`, `_read()`, and the `get-note` command path around lines 332–343.

The present command checks tombstone state through one `_read()` and fetches content through a second `_read()`. Those reads do not share a guaranteed transaction snapshot. A tombstone can commit between them, after which the ordinary read can still return the note's content.

Treat this as a P2 correctness finding. Do not silently move it into `notverified.txt` and pretend the current behavior is acceptable.

First write the regression. Reproduce the defect against the exact current predecessor `c58182c` in an isolated temporary worktree. Use a deterministic two-session interleaving that makes the tombstone commit after the state check but before the content read. Capture the actual output and exit code. Register the RED observation using the repository's existing red-record protocol and the next valid record identifier. Do not reconstruct transcripts or claim a RED based only on code inspection.

Then repair the retrieval path so the state and content decision share a single consistent database snapshot. One owner-scoped SQL statement is preferred if it makes the result and error-state handling clear. A single explicit transaction with a consistent snapshot is also acceptable. Preserve the distinction between absent/inaccessible and tombstoned notes. `get-note-history` must retain its governed historical access behavior. Owner RLS must remain the authority; do not introduce a privileged read bypass.

The acceptance condition is precise: a read whose snapshot begins after the tombstone commits must never return the note's ordinary content. A read whose snapshot begins before the tombstone commits may legitimately observe the active state. Test both outcomes and the owner boundary. Do not add an unnecessary lock to all readers merely to hide the race.

Keep this repair within the current Note scope. Do not refactor the landed Highlight or Bookmark families. Respect the repository's hard size limits: `harness/tests/test_note.py` is currently exactly 800 lines. Do not exceed the limit, remove existing assertions, weaken the size gate, or hide tests from the trusted runner. Fit the new regression into the existing acceptance structure where valid. If a lawful bounded split becomes necessary, follow LAW-05, update the claim scope and gate registration, and give the split its own RED-first proof. Never solve a size violation by relaxing the law.

### 3. Close the two current STATE review findings

PR #91 currently has seven review threads. Five older threads are resolved and outdated. Two current threads remain unresolved on `STATE.md`.

First finding: shorten the active-task entry. Keep the claim identity, the slice label, and authoritative pointers. Move implementation details, run IDs, and review-round history to record 47 or the appropriate new session record. `STATE.md` is a navigation snapshot, not a duplicated worklog.

Second finding: repair the exact-next-action entry. The round-2 artifact rebind, run-32 through run-36 evidence, and SEV round 4 are already recorded as complete. Do not direct the next agent to repeat completed work. After repairing the code and documentation, the next action should reflect the new evidence chain: the repair-tree verification, push, live checks, review dispositions, merge-gate review, and owner-controlled merge.

Inspect each thread in full. Verify the finding against the current branch. Fix it, then reply in the thread with the concrete disposition and evidence. Resolve only after the disposition is visible and the repaired state is confirmed. Do not resolve a thread merely because the code or document changed.

Update the outstanding-review snapshot so it reflects the actual live thread state. Do not treat the committed snapshot as a substitute for querying GitHub.

### 4. Reconcile the acceptance and evidence descriptions

The final branch now contains NTE-01 through NTE-14. NTE-14 is the round-2 UUID-spelling canonicalization regression. The current P3-06 status in `PLAN.md` still cites NTE-01 through NTE-13. Update it to describe the final branch accurately, explicitly distinguishing the new NTE-14 from old pre-split assertions that were moved during LAW-05.

Update PR #91's description to include the round-2 RED/GREEN repair, the final NTE-01..14 result, SEV round 4, and the final artifact set through run-36. Clearly distinguish historical pre-split evidence, split-tree evidence, and repaired-tree evidence. Do not make historical runs appear to test a later tree.

Clarify the PLAN wording around the "reference guard." Migration 0009 contains the Note lifecycle-target same-owner existence and alternation guard. The version-aware `arv.note_reference` machine, its reference surface, and the `--ref` behavior are CLAIM-057's work in migration 0010. Do not claim that the deferred reference machine landed in CLAIM-056.

Do not rewrite record 47 to make history look cleaner. It is append-only historical evidence. Record new findings and dispositions in a new numbered session record, following `context/TEMPLATES.md`. Update `context/WORKLOG.md` with a truthful entry, the applicable claim state, evidence pointers, unresolved boundaries, and the exact next action. Re-derive the five areas of `STATE.md` from the canonical sources.

### 5. Re-run the complete evidence chain

After the implementation and documentation repairs, run the exact Note suite three consecutive times against the final repaired tree. Run `make verify`, the trusted PR-mode gate, the known-bad matrix, and the canonical-layer verifier. Verify every affected sibling suite required by the scope and preserve the seventeen-suite registration truth unless the repository's manifest requires a different count.

Use a fresh-context test verifier. It must independently inspect the acceptance criteria and attempt to falsify the regression and the existing Note contract. It must not be the builder re-reading its own work.

Then run a new independent SEV round over the repaired diff. The previous SEV round 4 applies to the previous repaired diff; it does not automatically cover a new read-path fix. The new SEV reviewer must inspect the transaction snapshot behavior, lifecycle semantics, RLS/owner isolation, immutable revisions, idempotency, content losslessness, failure handling, migration compatibility, and proof provenance. Require zero open P0/P1. P2 findings require reasoned disposition and an owner-approved record where the laws require it.

Regenerate the proof sheet from actual run records. Validate the record manifest, the RED chain, the known-bad results, the review dispositions, and the SEV report. Bind the final evidence digest last, after the reviewed content has stopped moving. If any later edit changes the bound content, repeat the required evidence binding.

Commit and push at every significant checkpoint, following the standing push-early instruction. After the final push, verify all five required GitHub jobs on the exact final branch SHA. Do not cite a previous head's green checks as proof for the repaired head.

### 6. Complete D-042 review and merge preparation

Read every PR #91 review thread in full, including outdated threads. The observed state was seven threads total: five resolved/outdated and two unresolved/current. Re-query GitHub before acting because this is external state.

Every real finding must have a visible disposition: fixed in the PR, fixed in a named follow-up claim with its rationale, or reasoned no-fix with the required approval and revisit conditions. The two current STATE findings must be disposed of before resolution. The read-path race found during this review must be addressed and included in the final substantive review.

Prepare the D-042 merge-gate review against the final content head. It must cover the actual changed risk surface: migration 0009, schema invariants, append-only triggers, forced RLS, owner scoping, serialized transitions, idempotency and replay, lossless Note content, read behavior, lifecycle history, crash handling, independent tests, proof-sheet provenance, SEV results, scope limits, and unresolved residuals.

The review must be reasoned and substantive, not an empty approval marker or a generated summary. Follow the repository's documented single-actor merge procedure where applicable. Re-read the current branch protections and compare them with the required configuration. Do not weaken a required check, turn off strictness, or bypass the review contract to manufacture a merge.

The owner controls the merge. Do not merge PR #91 without the owner's explicit authorization. After the owner merges, verify the resulting main commit and all five post-merge checks. Re-read branch protection and confirm it is byte-equivalent to the required configuration. Verify the branch cleanup and the actual PR state. Record the merge facts from GitHub, not recollection.

### 7. Open CLAIM-057 at the correct boundary

After CLAIM-056 is merged and the post-merge proof is complete, open the next slice at the exact merged head. CLAIM-057 is P3-06 slice two: the version-aware Note reference machine.

Its scope includes the `arv.note_reference` model, migration 0010, the `--ref` command/read surface, source/version-aware reference semantics, owner-scoped target validation, dangling/shape/duplicate refusals, historical revision pinning, and reference projection in governed history, as defined by the canonical plan and requirements. It owns the assertions removed during the CLAIM-056 LAW-05 split.

Create and register the claim correctly before implementation. Reserve the next valid intent ID only if new owner intent actually needs recording; never fabricate an intent to satisfy a process step. Build the missing-feature RED first at CLAIM-056's merged head, register its real observed transcript, and then implement. Do not let CLAIM-056 silently absorb CLAIM-057's reference machinery.

Keep the same slice discipline: bounded scope, no overlapping claims, real PostgreSQL, immutable evidence, independent reads, hostile probes, fresh-context verification, SEV review, proof sheet, review dispositions, exact-head CI, and owner-controlled merge.

### 8. Continue Phase 3 without losing its boundaries

After CLAIM-057, continue through P3-07, P3-08, and P3-09 in the order and scope defined by `PLAN.md`.

P3-07 delivers rebuildable keyword findability. Prove owner filtering, tombstone filtering, revision freshness, indexing failure, delete/rebuild, encoding and tokenization boundaries, and explicit indexing lag/failure. The index is derived state and must never become the only authoritative copy.

P3-08 delivers the local outbox, Supabase synchronization, and recovery contract. Local mutation and outbox intent must be atomic. Prove ordering, retry, duplicate delivery, uncertain acknowledgments, out-of-order delivery, process death, outage recovery, and independent remote reads. Never silently apply last-write-wins to authored content. Preserve immutable concurrent revisions and explicit conflict semantics. Do not choose an unratified blob backend or promise cross-store atomicity.

P3-09 delivers versioned export/restore and integrated durable-capture proof. Export and restore must preserve authoritative records, source/blob references, revisions, and purge/retention state. Test clean-destination restore, canonical state equality, repeated restore, missing blobs, malformed archives, interrupted restore, purge followed by restore, and corrupt-index rebuild. A purge must never be resurrected by restore.

Do not close a phase because the PR merged or because the test count looks impressive. Close it only when the canonical exit predicates and evidence are satisfied.

### 9. Phase 3 exit, then Phase 4

At the Phase 3 exit gate, evaluate the complete capture substrate: real client/backend use, import and source state, extraction and anchors, highlight/bookmark/note revisions, owner isolation, crash/restart/replay, local durability, export/restore, purge semantics, rebuildable derived state, source provenance, and explicit remaining limits. Require traceability, independent SEV, a clean-clone task agent, and separate grading. Do not confuse backend test success with a complete owner workflow.

Elaborate Phase 4 cards from the actual Phase 3 exit evidence, one phase deep as NG-04 requires. Complete P4-00's integration contract before broad UI implementation. It must define authenticated client identity, scoped API operations, stable IDs, truthful durability states, local/server data ownership, pagination, bounded responses, errors, retries, offline behavior, invalidation, supported format capabilities, unresolved-anchor behavior, compatibility, migration, and recovery. The integration test must call the real API boundary.

Phase 4's reader and journal UI belongs in its actual authorized client repository, not in Arivoo's backend-only repository. Discover the actual client repository from reliable workspace evidence. Do not invent a repository name, build a duplicate UI here, or declare integration complete using mock-only calls.

Proceed through P4-A to P4-F as separate bounded slices. P4-A must prove supported format intake and reader position against real acceptance corpora. P4-B must integrate import, reading, position, highlight, bookmark, note capture, authentication, offline/retry, and honest acknowledgment states through the actual client. P4-C must prove library/list behavior and lossless Journal blocks; diagram or structured-block support is not valid until its serialization and round-trip contract is proven. P4-D must implement stable `@` references across revision, rename, tombstone, purge, and historical-target states. P4-E must provide baseline scoped, read-only agent access through the same authenticated API. P4-F must prove migration, export/restore, recovery, purge invalidation, regression, and independent grading.

Run the seven mandatory Phase 4 refinement rounds: requirements traceability; trust and authorization; identity/provenance/revisions/anchors; transactions/replay/concurrency/failure; client/API integration and truthful UX; recovery/migrations/purge/rebuild/resource bounds; independent clean-room grading and owner-task fidelity. Seven is a minimum, not a stopping quota. Any defect that invalidates a previous round reopens that round.

Phase 4 exits only when the actual owner workflow runs end-to-end through the real client and backend: import, open/read, save position, capture highlight/bookmark, write/revise a Note, create a free-standing Journal thought, use stable `@` references, leave, reopen, and recover with truthful durability state. Prove online/offline, uncertain acknowledgment, stale-source behavior, owner isolation, hostile-import refusal, export/restore, purge invalidation, scoped agent reads, UI/API/backend integration, independent grading, and owner fidelity. If the actual client is unavailable, mark that sub-gate blocked and continue independent backend work. Never fabricate a UI pass.

### 10. Owner decisions and handoff discipline

Keep D-014 and Q6–Q12 at their exact canonical scopes. They block only their named dependents, never unrelated work. In particular, do not make unapproved semantic-spike purchases, infer extraction stability from synthetic corpora, change repository visibility, alter credential/workflow-tamper ownership, invent Work/Source deduplication policy, or choose an unratified blob provider.

Maintain a workspace-level `RESUME.md` outside the Git worktree. Before creating or editing it, verify that its resolved path is outside the repository. Keep it operational: current phase, active claim, branch and head, last verified test head, exact next action, current open review threads, unresolved questions, notverified boundaries, and the commands needed to resume. No credentials or secrets may appear in it. Update it after meaningful commits, pushes, merges, and session boundaries. It is a handoff aid, not a canonical plan or a tracked repository file.

At every meaningful session exit, append the worklog entry and numbered engineering record, re-derive `STATE.md`, commit and push all durable reasoning deltas, and preserve actual commands and exit codes. Never invent a run, reconstruct a transcript, or treat a previous session's summary as evidence.

Continue until the Phase 4 exit gate is genuinely complete under INT-144. Do not start speculative Phase 5 implementation ahead of that gate. Do not stop at a plan, a long report, a green PR, or a clean-looking repository. The finished product workflow and its evidence are the completion criteria.
