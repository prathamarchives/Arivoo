# REVIEW-ONLY ARTIFACT — preserved verbatim, D-022 (never edited; the owner's
# words as received; typos preserved; analysis lives in the session records)

Received: 2026-10-28 (owner turn 36, the continuation directive attached to the
bookkeeping-reconciliation turn; INT-141; preservation home: record 45 §1 +
this file). The directive's own header states its status: "a continuation aid,
not a replacement for AGENTS.md, EXECUTION.md, PLAN.md, RTM.md, LAWS.md,
DECISIONS.md, CLAIMS.md, or the execution templates."

---

## Owner turn 36 — the attached directive, verbatim

Repository bookkeeping needs reconciliation take care of this. the repostiry is the garden you gotta miantain or anyone works maintains it..

Arivoo: Live Review + Non-Stop Phase 3 → Phase 4 Continuation
Prepared: 2026-10-28
Repository: prathamarchives/Arivoo
Purpose: Live-state handoff and execution directive. Use the repository's canonical documents as authority; this file is a continuation aid, not a replacement for AGENTS.md, EXECUTION.md, PLAN.md, RTM.md, LAWS.md, DECISIONS.md, CLAIMS.md, or the execution templates.
A. Live review snapshot
Verified GitHub state
- main was observed at b200e55521a8f6082be5231d9e4e409b3bcef1b4, merge of PR #88, committed 2026-10-27 16:04:27 UTC.
- PR #87 / CLAIM-052 / P3-03a is merged: https://github.com/prathamarchives/Arivoo/pull/87
- PR #88 / CLAIM-053 / P3-03b is merged: https://github.com/prathamarchives/Arivoo/pull/88
- PR #88's final head was 9560f1ed401fc83bbb337f9d13c6fabc76001a8e.
- Post-merge workflow run 40537300422 succeeded on b200e55521a8f6082be5231d9e4e409b3bcef1b4. All five required jobs succeeded: canonical-layer, head-tools, harness, harness-suites, harness-trusted.
- At the last live read, GitHub returned zero open PRs and only the main branch. The next implementation slice has not yet appeared as a remote branch/PR in that snapshot.
- PR #88 implemented typed anchor resolution (resolved | unresolved | ambiguous) and the Q8 synthetic-corpus anchor-stability spike. Its documented results are limited to synthetic-corpus fidelity; they do not establish real PDF/EPUB location stability.
Real reconciliation gap: start here
The live main files are stale relative to the merged PR:
- STATE.md still says CLAIM-053 / PR #88 is at the merge gate and that merging #88 is the exact next action.
- AGENTS.md still describes CLAIM-053 as at finalize / merge next.
- CLAIMS.md still contains CLAIM-053 in the open claims section. The repository's rule-4 protocol expects the previous claim's close row to be appended by the subsequent slice, so do not misinterpret the row alone; perform the canonical close-row procedure as part of CLAIM-054's opening commit. Confirm the exact current schema/rules before editing.
- The PR #88 GraphQL read returned 11 inline review threads with unresolved status even though their timeline contains author dispositions and reviewer confirmations for several fixes. Do not state that every GitHub thread is formally resolved. Read the actual current thread states and history. Record the truth in the next slice's evidence/record. Resolve only if the repo's authority rules permit it and the disposition is already visible; never resolve before reading and dispositioning.
The first action is therefore a bounded post-merge state reconciliation within the opening of CLAIM-054, followed by P3-04. Correct the live status pointers and close-row accounting in their canonical manner. Do not patch main ad hoc or create an unclaimed branch.
B. Current roadmap position
Already landed: P3-00; P3-M0; P3-K0; P3-01; P3-02; P3-03a (CLAIM-052 / PR #87); P3-03b (CLAIM-053 / PR #88).

Next implementation slice: P3-04 — Highlight and immutable revisions.

Then proceed through P3-05, P3-06, P3-07, P3-08, P3-09, and the Phase 3 exit gate. Only after Phase 3 exit evidence passes should work proceed to P4-00 and P4-A through P4-F, ending at the Phase 4 exit gate.

Canonical roadmap: PLAN.md. Frozen contracts: RTM.md. Decision boundaries: DECISIONS.md and RTM §7. The descriptions below summarize the roadmap; canonical text wins if this aid differs.
C. Copy/paste execution directive
Mission
Continue prathamarchives/Arivoo from the latest verified main state until the Phase 3 and Phase 4 exit gates pass under the repository's actual acceptance criteria. This is an execution instruction, not a request for another plan. Inspect, implement, test, review, preserve evidence, reconcile status, merge through the required process, and proceed to the next eligible slice without asking the owner to repeat the standing continuation request.

Do not claim completion unless code, tests, independent verification, review dispositions, exact-head CI, and repository records establish it. Do not fabricate progress, test results, approvals, or evidence.
1. Cold start and live-truth preflight
1. Read AGENTS.md, STATE.md, CLAIMS.md, the last compact entries in context/WORKLOG.md, then the referenced latest session record. Follow the selective read order; consult EXECUTION.md and only the task-relevant canonical documents, including PLAN.md, RTM.md, LAWS.md, ENGINEERING.md, DECISIONS.md, INTENT-LEDGER.md, and context/TEMPLATES.md.
2. Query live main, open PRs, branches, recent commits, check-runs, review threads, reviews, and branch protections if the current connector has access. The latest prior known state above is a starting point, not proof of present state.
3. Inspect the current tree and worktree before changing anything. Never overwrite uncommitted owner work or create a duplicate/overlapping claim branch.
4. Reconcile stale STATE.md/AGENTS.md and the CLAIM-053 close row in CLAIM-054's first commit according to the registry's rule-4 convention. Update the pointers to the latest actual session record. Preserve STATE.md's one-screen pointer-only contract; detail belongs in session records and claim rows, not duplicated in the navigation file.
5. Enumerate PR #88's review threads and accurately report their actual resolved state. The review timeline contains dispositions, but the live review-thread listing reported 11 unresolved threads. Do not silently call them formally resolved. Follow current repository rules and record any residual status honestly.
2. CLAIM-054 / P3-04 — Highlight and immutable revisions
This is the next bounded product slice after the merged P3-03a/b work. Use the exact authoritative P3-04 card and requirements in PLAN.md and RTM.md.

Required behavior:
- Add stable Highlight identity and append-only revisions carrying selected content, Anchor, Source reference, owner/actor, input digest, and command provenance.
- Reject missing/dangling Anchor references and cross-owner Source references.
- Preserve prior revisions. Tombstone behavior hides content from ordinary retrieval while retaining governed history.
- Keep current views rebuildable and return acknowledgments that reflect the actual durability rung.
Required test classes from the roadmap:
- Mutation rejection and immutable-history preservation.
- Dangling references and cross-owner isolation.
- Same-key retry/replay and conflicting request behavior.
- Crashes at each transactional boundary; lost acknowledgments and independent rereads.
- Source re-import/re-extraction and stale anchor handling.
- Tombstone/restore behavior.
Acceptance: an independent read sees the correct revision history; current views are rebuildable; no stale or wrong-version Anchor is silently retargeted; a tombstone affects ordinary retrieval without erasing governed history. Implement only this slice's bounded behavior. Do not pull bookmark, notes, keyword indexing, sync, or export/restore into P3-04 unless the authoritative card identifies a prerequisite and the scope gate allows it.
3. Mandatory slice cycle for P3-04 through P3-09
For every slice:
1. Verify the active claim registry, reserve the required intent IDs and claim the scope before implementation. Open claims must not overlap on non-shared paths. The first work commit contains the claim row and RED-first evidence declaration according to the repository rules.
2. Record the actual predecessor SHA and reproduce the missing/incorrect behavior at that predecessor. Preserve the failure transcript as red evidence. Never substitute a hand-written expected output or a self-reported status for an observed RED.
3. Keep the slice small and behavior-bounded. Push significant commits early to reduce workspace-reset loss. Open the PR when the required early-push/red-first checkpoint is satisfied.
4. Test the exact behavior, negative paths, adversarial neighbors, ownership/provenance boundaries, idempotency, transaction failure and recovery where relevant. Use the real PostgreSQL rig and actual API/kernel boundary required by the contract; a helper-only unit test is not integration proof.
5. Run focused regressions first, then the registered suite, make verify, proof-sheet validation, and the PR-mode gate. Record exact commands, environment, exit status, counts, revision, and artifact digests. An unexplained empty result, malformed report, missing artifact, or undecidable result fails closed.
6. Run the fresh-context SEV review and required independent technical review. Read every new review thread and every review submission; validate comments against current code. Fix valid findings RED-first; record evidence-backed no-fix/routed/duplicate dispositions for the rest. A reviewer response, CI green, or a comment author's acknowledgement does not automatically prove a thread is formally resolved.
7. Rebind the SEV report to the final reviewed diff after all content edits and reassemble the Proof Sheet. A later edit to any reviewed content may invalidate the binding. Re-run the applicable gates after rebinding.
8. Re-derive CLAIMS.md, STATE.md, AGENTS.md, PLAN.md, context/WORKLOG.md, session record and proof pointers. Verify no status count, path, claim row, or evidence digest is stale.
9. Merge only after all required reviews, dispositions and five checks pass at the exact final PR head. Use the authorized D-042 path, never bypass protected review controls. After merge, verify post-merge CI, branch deletion, and the protection state restoration/readback when the procedure requires it.
10. Append the close facts under the canonical rule-4 protocol in the receiving slice, verify the prior claim is correctly represented as closed, and proceed immediately to the next eligible dependency.
The five required CI contexts are canonical-layer, head-tools, harness, harness-suites, and harness-trusted. Do not claim all green based on a predecessor SHA or on make verify alone.
4. Remaining Phase 3 slices
Follow the actual P3 card order in PLAN.md; the following is a summary of current canonical scopes.

P3-05 — Bookmark
- Stable identity and location/Anchor; do not duplicate source text.
- Define source-version-change behavior.
- Test invalid Anchor, owner isolation, re-import/re-extraction, tombstone/restore, replay and restart.
- Acceptance: return to the saved location or return a typed unresolved-anchor state; never silently retarget.
P3-06 — Note and revision history
- Persist deep owner-authored Notes with immutable revisions and explicit links.
- Define diagram serialization/round-trip before implementing diagram persistence. Preserve raw/creative writing losslessly.
- Test revision preservation, duplicate retry, competing revisions, dangling references, owner boundary, crash/restart, export/restore.
- Acceptance: every revision is retrievable, attributable and referenceable; conflicts never silently destroy a revision or claim an untested merge.
P3-07 — Keyword findability
- Build a rebuildable keyword index for committed supported sources, passages, captures and notes.
- Test indexing failure, delete/rebuild, stale entries after revision, tombstone filtering, ownership filter, encoding/tokenization boundaries, and known queries.
- Acceptance: captures are findable under a defined contract or indexing lag/failure is explicit; rebuilding restores expected results.
P3-08 — Local outbox, sync and recovery
- Persist local mutation and client-outbox intent atomically; route remote writes through the same kernel; implement the required server-outbox handoff for later enrichment per the canonical decisions.
- Specify ordering, replay, retry and conflict semantics. Do not silently use last-write-wins for authored content. Preserve concurrent immutable revisions and define the current-view rule. A user review queue or model decision must not block pipeline progress.
- Test offline capture, restart before sync, retry after uncertain acknowledgment, duplicate/out-of-order delivery, server outage, remote/local mismatch, cross-owner sync, and death around outbox acknowledgment.
- Acceptance: every committed local write is either server-durable or explicitly queued/retryable, with no lost committed writes or duplicate logical effects and independently read remote state.
P3-09 — Export/restore and integrated durable-capture proof
- Define versioned export/restore for authoritative records, source/blob references, revisions and required purge/retention state. Rebuild derived indexes after restore.
- Test clean-destination restore, canonical authoritative-state equality, repeated restore, missing blob, malformed archive, interrupted restore, purge-then-restore and corrupt-index rebuild.
- Acceptance: defined authoritative-state equality holds; purge cannot be resurrected by restore; failures are explicit/retryable; independent verification uses a separate role/path.
5. Phase 3 exit gate
Do not declare Phase 3 complete because P3-09 merges. Run the canonical gate against the final main revision and satisfy every acceptance condition in PLAN.md.

Evidence must establish, at minimum:
- Work/Source identity and Anchor contracts are explicit; unresolved owner decisions remain blocked only at their exact dependents.
- A real client/backend path imports supported input, creates a valid Highlight/Anchor, Bookmark and Note, and finds them through keyword search.
- Crash/restart/replay/offline fault matrices demonstrate zero lost committed writes and no duplicate logical effects.
- Local-durable and server-durable are distinct and sync has explicit recoverable outbox states.
- Every write is attributed and owner-scoped; two-owner tests and independent reads pass.
- Revisions are immutable, tombstones work, and purge remains effective after restore.
- Derived passages/indexes rebuild without losing authored state; stale derivations cannot silently appear current.
- Export/restore passes the documented equality contract.
- Every SYS requirement has traceable tests and Proof Sheet evidence; all applicable slices have passing SEV; known-bads are refused with named codes.
- Required CI passes at final main. An uncoached clean-clone agent completes the user-like acceptance path and a separate grader passes it with no P0/P1.
- Not-verified classes and residuals remain explicit. A PR merge is not itself the phase-exit proof.
If the gate fails, isolate the smallest failing contract, claim it properly, add/reproduce a regression and repair it. Do not label a real failure an acceptable limitation unless the authoritative contract explicitly allows that limitation.
6. Phase 4 — P4-00, P4-A through P4-F
Once Phase 3 exit evidence passes, begin P4-00. Do not build a broad UI before the actual authenticated client/backend integration contract is established. This repository is backend/foundation only; its CLI is a contract client, not the reader UI.

P4-00 — Foundation and integration contract
- Authenticated client identity and scoped authorization.
- Import/open/read-position/capture/bookmark/note/journal operations.
- Truthful saved / queued / synced / conflicted / failed acknowledgments.
- Stable identities and @ reference resolution across rename, revision, tombstone and purge.
- Pagination, bounded responses, explicit errors, retry/idempotency, offline behavior, local cache vs server authority and invalidation.
- Format capability matrix, extraction readiness and unresolved-anchor states.
- Client/API version compatibility, migration, rollback, user scenarios and contract tests.
- A real contract test must call the API boundary. The UI must never write product tables directly or bypass owner scoping with privileged credentials.
P4-A — Format intake and reader position
- Add approved PDF/EPUB/JSON paths according to the durability ladder; distinguish native text from scan/OCR and reflow from fixed layout.
- Measure actual corpora under Q8's corpus gate. Unsupported, encrypted and malformed input must fail explicitly without losing staged bytes.
- A format is supported only after corpus, position/anchor, failure and recovery evidence pass.
P4-B — Reading/capture integration
- The reader client in its authorized repository calls the API for import/open, position, highlight, bookmark and margin-note capture.
- Cover auth expiration, forbidden source, malformed DTO, offline, timeout/uncertain acknowledgment, duplicate click, reload/restart, stale source version, deleted target, and retry after lost response.
- No privileged client helper writes product tables directly, and request-start never means saved.
P4-C — Library, reading lists, resumable behavior and Journal/blocks
- Implement stable library/list membership, current-reading state, approved coarse events within privacy decisions, and a writing-lab journal that preserves long raw/creative thought losslessly.
- Q6 blocks only its specified transcript-dependent scenario/corpus, never unrelated journal/capture work.
P4-D — Stable @ references
- Separate target identity from selected historical revision.
- Expose current/historical/tombstoned/unavailable/ambiguous/purged states without leaking private deleted content or revealing whether another owner's entity exists.
- Title/label changes must not break references. Imported hostile @ strings are untrusted data, never authority.
P4-E — Baseline scoped agent access (required at first usable milestone)
- Agents read owner journal/capture context through the same API with provenance, scope and budgets.
- Read-only at first; enforce owner scope on every query; imported text stays untrusted; no arbitrary database access.
- Record any Q9/Q10 owner choice exactly; do not overclaim credential/workflow hardening.
P4-F — Recovery/regression proof and phase gate
- Validate migration from supported prior states, lifecycle export/restore for journal/reference/diagram state, owner isolation, sync conflicts and rebuild.
- Use a clean external client and independent grader; obtain owner-fidelity review against concrete product behavior.
- Real UI/user validation is blocked without the actual reader/journal host. Prove backend/client contract honestly, never fabricate UI validation.
Phase 4 exit target: through the actual client and real backend, the owner can import, open/read, save position, highlight/bookmark, write/revise a note, capture a free-standing journal thought, use stable @ references, leave/reopen and recover the same material with truthful durability status. Online/offline/uncertain acknowledgment/stale source behavior is tested; export/restore preserves authoritative content; purge invalidates derived state; scoped agent reads use the same core; ownership and hostile-import tests fail closed; traceability is current; API integration, backend/system tests, independent grading and owner-fidelity review pass; no blocking defect is mislabeled as a pass.
7. Required refinement rounds
Use the canonical seven-round refinement protocol in PLAN.md / session records. These are minimum review dimensions, not seven cosmetic rounds:
1. Requirements and traceability.
2. Trust, hostile input and authority boundaries.
3. Identity, revisions and anchors.
4. Transactions, replay, concurrency and uncertain acknowledgments.
5. Client/API contract and truthful user-visible state.
6. Recovery, resources, migrations and lifecycle.
7. Clean-room, uncoached end-to-end grade and owner-fidelity review.
Continue beyond seven rounds until all exit criteria actually pass. Each round must find and address a real risk, failure, or measurable quality issue. Do not manufacture rounds, pad logs, or tune metrics to make a report look better. Evaluate the evidence independently from the builder's claims.
8. Preserve owner decision boundaries and future architecture
D-014 and Q6–Q12 remain open at their exact documented scopes. Do not silently ratify them. Continue unrelated work outside those scopes.
- Q8: this anchor spike proves synthetic-corpus behavior only. Do not claim PDF/EPUB stability without its real-document gate and measured results.
- Q11: no automatic logical identity merging or identity-dependent uniqueness beyond the ratified baseline.
- Q12: maintain provider-neutral blob contracts until the owner ratifies the backend/staging/recovery choice; no provider-specific schema or cross-store atomicity claims before then.
- Q10: repairs to executable trust defects do not imply credential/workflow-tamper hardening is complete.
- The recursive Type 1 decision engine, C-based inference harness, automated concept admission, wikilinking and full whiteboard UI are future intelligence/surface work. Preserve identities, provenance, revisions, anchors and APIs needed by them, but do not pull speculative Phase 5 behavior into Phase 3/4.
9. Merge, authority and stop conditions
- Claim-before-work, exclusive path scope, intent reservation, RED-first, independent review, exact-head CI, proof-sheet digest binding and rule-4 claim closure are mandatory.
- The five required contexts are canonical-layer, head-tools, harness, harness-suites, and harness-trusted.
- Use the required authorized D-042 merge path and explicitly authorized merge/proposal process. Never bypass required review or weaken branch protection.
- After merge, observe post-merge checks, branch deletion and protection restoration/readback. If the connector cannot read the protection endpoint, do not claim that you verified it; use the authorized host/session or record the exact limitation.
- If infrastructure, credentials, an owner decision, or review capability truly blocks an action, record evidence and scope, finish independent permitted work, and continue elsewhere. Do not hide the blocker or fabricate a pass.
- A status message is not a durable handoff. Update/push the actual state files and session evidence as prescribed.
D. Exact next action
Start with a fresh live preflight, reconcile the merged #88 status and CLAIM-053 close facts in CLAIM-054's opening commit, then implement P3-04 — Highlight and immutable revisions. Continue through P3-05…P3-09, the Phase 3 exit gate, P4-00, P4-A…P4-F, and the Phase 4 exit gate. Do not stop after a plan, PR opening, first green run, or seven refinement rounds. Stop only at the genuine Phase 4 exit gate or a precisely documented permission/owner-decision boundary.
