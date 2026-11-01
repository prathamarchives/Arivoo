# Arivo: continuous engineering execution directive — Phase 3 completion → Phase 4 completion (owner-forwarded, 2026-11-01)

> STATUS: REVIEW-ONLY ARTIFACT — 2026-11-01 (banner per D-024/D-022). Owner-forwarded execution directive, preserved verbatim as received (gateway-delivered attachment): the execution orders ride the standing do-not-stop chain (INT-134/135/138/139/140/141/142 + INT-143) and the canonical decisions (D-037/D-041/D-042/D-043), never a second authority; the verbatim preservation home is record 47 §1. Minted as INT-143.

# ARIVO: CONTINUOUS ENGINEERING EXECUTION DIRECTIVE
## Phase 3 completion → Phase 4 completion
### Autonomous systems engineering, scientific verification and continuous delivery

**Mission:** Take the existing Arivo project from its current repository state, finish all remaining Phase 3 requirements, pass the Phase 3 integrated exit gate, execute the complete Phase 4 roadmap, and deliver a verified, usable reader and journal system that satisfies the owner's actual day-one workflow.

**Execution mandate:** Continue from the actual repository state. Do not stop after individual tasks, features, PRs, successful tests, implementation milestones or engineering sessions. Continue through dependent and independent work, preserving the established engineering contracts, until the Phase 4 exit gate has been successfully completed.

This is a continuous execution mandate, not permission to bypass safety requirements, owner decisions, review protocols or evidence standards.

---

# 1. MISSION AND DEFINITION OF SUCCESS

Arivo is the owner's reading, study, reflection and knowledge environment.

Its foundational purpose is to let a person consume information, preserve meaningful material, return to exact locations, write, think, connect ideas and progressively build a durable body of knowledge.

The system must support the complete interaction between:

- Sources and imported material.
- Reading and position tracking.
- Highlights and stable bookmarks.
- Authored Notes and immutable revisions.
- Free-form Journal writing.
- Stable references between entities.
- Keyword findability.
- Local and remote durability.
- Recovery and synchronization.
- Authorized agent access to owner-controlled context.

The product must preserve the owner's material faithfully. It must not silently lose, overwrite, retarget, misattribute, expose or fabricate authored information.

The objective is not to maximize feature count or repository activity.

The objective is to establish an integrated system whose behavior remains correct across ordinary use, concurrent operations, interrupted transactions, process crashes, changing sources, migrations, offline periods, synchronization failures and restoration.

## Final outcome

The owner must be able to:

1. Import readable material.
2. Open and read it.
3. Leave and recover reading position.
4. Highlight passages.
5. Create and return to bookmarks.
6. Write and revise Notes.
7. Capture free-standing Journal thoughts.
8. Reference other material through stable `@` references.
9. Leave the application and return without losing material.
10. Understand whether work is saved, queued, synchronized, conflicted or failed.
11. Recover from interruptions without losing committed information.
12. Allow authorized agents to read relevant context through the same governed API.

Every one of these behaviors must work through the actual reader client and real backend, with independently verified evidence.

An API CRUD inventory is not a completed product.

A successful PR is not a completed phase.

A green test suite is not proof of system-level correctness.

---

# 2. INITIAL STATE RECONSTRUCTION

The first operation is always to reconstruct ground truth.

The previous observation is a starting pointer, not an assumption about the current state.

Last observed:

- Repository: `prathamarchives/Arivoo`
- Main: `6938efa` (PR #89 merge)
- Active claim: CLAIM-055
- Branch: `slice/claim-055-p305-bookmarks`
- PR: #90
- Last observed PR head: `d3893ff`
- Five required CI checks: green at that observed head.
- Outstanding finding: move-bookmark/lifecycle transaction concurrency.
- Phase 3 remaining: P3-05 through P3-09 and the integrated exit gate.
- Phase 4: P4-00 through P4-F and the integrated exit gate.

Re-fetch all information.

Never inherit a previous agent's assumption that a branch, test, review, merge or external action completed.

Read in this order:

1. `AGENTS.md`
2. `STATE.md`
3. `CLAIMS.md`
4. Recent `context/WORKLOG.md`
5. Latest numbered session record.
6. Relevant owner-intent entries in `INTENT-LEDGER.md`.
7. Relevant requirements in `PLAN.md` and `RTM.md`.
8. Relevant laws in `LAWS.md`, principles in `PRINCIPLES.md`, and decisions in `DECISIONS.md`.
9. `OPERATING-MODEL.md` and `EXECUTION.md` wherever the execution protocol requires them.

Inspect the live GitHub state, branch protections, PR discussions, unresolved review threads, actions and checks.

Inspect the working tree before changing anything.

Check open claims before selecting a task. This is a multi-agent repository. Never assume that another agent is not operating on an overlapping scope.

Do not print credentials or expose environment contents. Credentials remain outside the repository.

Reconstruct what has actually landed, what is implemented but unmerged, what is measured, what remains unverified and what is genuinely blocked.

Then continue.

---

# 3. ENGINEERING PHILOSOPHY

Operate as a systems engineer, experimental scientist, software architect and verification engineer.

Do not equate implementation with understanding.

Every material behavior must be expressed as a falsifiable requirement before implementation.

For every requirement, establish:

- What must be true.
- Why it must be true.
- Which owner intent or approved decision establishes it.
- Which component owns the behavior.
- Which data is authoritative.
- Which state transitions are permitted.
- Which transitions must be rejected.
- Which interfaces carry the behavior.
- Which failure modes can violate the requirement.
- Which observable evidence would prove the behavior.
- Which experiment would falsify it.

## 3.1 Reason from mechanisms

For every complex behavior, identify the actual mechanism.

Examples:

A saved bookmark is not merely a UUID. It is a stable entity identity with a version-bound source reference and an anchor whose resolution can change without silently changing the owner's saved meaning.

A synchronized note is not merely a database row. It involves an authoritative local commit, an outbox intent, a remote application, acknowledgment, idempotency and recovery after uncertain outcomes.

A stable reference is not merely a string. It is a governed resolution relationship between an identifier, an entity and potentially a selected historical revision.

A successful API response is not necessarily a durability guarantee. The acknowledgment must describe the actual completed rung.

Understand those mechanisms before modifying code.

## 3.2 Maintain a formal contract

For each stateful feature, document its state machine.

For each operation, document its preconditions, effects, commit point, acknowledgment, replay behavior and failure outcomes.

For each invariant, identify where it is enforced:

- Type or schema constraint.
- Foreign key.
- Row-level security.
- Trigger.
- Transaction protocol.
- Application command boundary.
- API authorization.
- Client behavior.
- Independent verification.

Prefer structural enforcement over conventions.

If a guarantee depends on application behavior, test that behavior. If it must withstand hostile direct writes, test the actual database enforcement.

## 3.3 Reason about concurrency explicitly

For concurrent operations, reason about event order and linearization points.

Distinguish:

- Mutual exclusion.
- Atomicity.
- Isolation.
- Idempotency.
- Ordering.
- Commit acknowledgment.
- Recovery after uncertain acknowledgment.

A passing two-writer test does not prove a move-versus-tombstone invariant.

A unique constraint does not establish that a command was replayed correctly.

A transaction does not automatically guarantee that all preconditions were read under the same serialization boundary.

Use deterministic concurrency tests, independently controlled sessions and real database observations.

## 3.4 Preserve truth

Never use an AI-generated assertion as evidence for its own correctness.

Never let one agent implement and independently approve the same implementation.

Never report an observation that was not made.

Never label an untested behavior as verified.

Keep empirical results, logical deductions, architectural assumptions and untested hypotheses explicitly distinct.

When evidence contradicts the plan, investigate and reconcile it through the established authority process. Do not silently adapt requirements to fit the implementation.

---

# 4. THE CONTINUOUS EXECUTION LOOP

Every slice follows one repeatable engineering process.

### Stage 1: Reconstruct

Establish actual branch, commit, open claims, working-tree state, current requirement, dependencies and outstanding findings.

### Stage 2: Formalize

Create or update the slice understanding artifact in the repository's prescribed format.

Specify:

- Owner INT IDs and relevant verbatim requirements.
- SYS requirements.
- Interfaces.
- Scope and exclusions.
- Invariants.
- State transitions.
- Failure cases.
- Acceptance predicates.
- Verification methods.
- Unknowns and dependencies.

### Stage 3: Design

Determine the smallest valid system change.

Design the transaction boundaries, entity ownership, data model, schema changes, migration behavior, rollback behavior and API contracts before implementation.

Identify architectural consequences beyond the immediate component.

### Stage 4: RED-first verification

Write tests and demonstrate that they fail for the intended reason on the predecessor revision.

Record actual failure evidence.

Keep the red record immutable and use the established typed amendment process when tests or scope change.

### Stage 5: Implementation

Implement the smallest coherent solution within the authorized scope.

Avoid unnecessary refactoring, duplicate abstractions, parallel kernels or unapproved dependencies.

Preserve interfaces already frozen in RTM.

### Stage 6: Real-stack testing

Test the actual PostgreSQL stack, command boundaries, API interfaces, authentication and relevant client interactions.

Mocked tests may test isolated contracts. They cannot substitute for real integration proof.

### Stage 7: Falsification

Use independent state reads, concurrency tests, crash injection, mutation tests, property tests, differential checks and adversarial inputs as appropriate.

The verifier should attempt to demonstrate failure, not help the builder feel successful.

### Stage 8: Systems-engineering verification

A separate fresh-context SEV checks:

- Requirements traceability.
- Architecture and dependency direction.
- Interface correctness.
- Failure modes.
- Transaction integrity.
- Security and privacy.
- Cross-slice effects.
- Migration safety.
- Recovery behavior.
- Evidence provenance.
- Actual level of V-model closure.

### Stage 9: Proof and release

Produce the required proof records, SEV report, notverified list and Proof Sheet.

Run the PR-mode gate.

Push significant commits early.

Observe the required remote checks on the exact proposed revision.

Read every review comment and thread, reproduce findings and record dispositions before resolution.

Complete the owner-authorized merge process.

### Stage 10: Reconcile and advance

Update the relevant authoritative records, worklog, claims and navigation state.

Reconstruct the next available task.

Begin the next slice without an artificial milestone pause.

No completed slice is permission to stop the mission.

---

# 5. PHASE 3: COMPLETE THE DURABLE-CAPTURE FOUNDATION

Follow the authoritative P3 sequence.

P3-00 through P3-04 are previously landed. P3-05 is the active bookmark slice.

## P3-05: Bookmark

Finish the existing PR #90.

The immediate outstanding task is the move-versus-tombstone concurrency defect.

Investigate `move_bookmark` and `_spine` together. The current command implementation reads the bookmark state before beginning the write transaction. The lifecycle insertion trigger takes a per-bookmark advisory transaction lock, but the movement path does not hold that same lock across its state read and revision write.

A move must not commit after tombstoning.

The solution must hold the appropriate serialization lock across the complete transition, including current-state validation, anchor construction, revision insertion and commit.

The existing `_spine` ordering makes this a transaction-boundary problem, not merely a missing SQL statement.

Add a deterministic PostgreSQL regression proving the lawful ordering of both operations.

Also examine move-versus-restore and other competing lifecycle transitions.

Preserve immutable revisions, owner isolation, source-version identity, named refusals and exactly-once command behavior.

Then complete the previously outstanding review rounds, fresh-context verification, proof regeneration and owner-controlled merge.

## P3-06: Notes and revision history

Implement the deep owner-authored Note system.

Requirements:

- Notes contain owner-authored content.
- Revisions are immutable.
- Revision authorship and provenance remain attributable.
- Explicit relationships to other entities are supported.
- Historical revisions remain accessible.
- Conflicting writes do not silently overwrite one another.
- Referential integrity is maintained.
- Tombstone and restoration semantics follow the frozen contracts.
- Export and restore do not discard authored history.
- Diagram support is added only after a defined serialization and round-trip contract exists.

Test competing revisions, repeated requests, crashes, authorization failures, missing references, ownership violations and restoration.

Preserve long-form writing and creative thought. Do not force the Journal into a short-note or summary-only abstraction.

The owner must be able to retain substantial raw thinking without the system silently compressing or transforming it.

## P3-07: Keyword findability

Implement the rebuildable keyword index.

The index is derived data, never the authoritative location of authored information.

Define:

- Indexable entity classes.
- Supported formats.
- Tokenization and normalization.
- Query behavior.
- Ownership filters.
- Revision behavior.
- Tombstone filtering.
- Staleness detection.
- Indexing failures.
- Rebuild behavior.
- Explicit indexing lag or failure reporting.

Test encoding boundaries, malformed data, stale entries, revisions, tombstoned material, multiple owners and deletion/rebuild.

A broken index must not destroy source material or block durable capture.

A rebuild must reproduce expected indexed state from authoritative records.

## P3-08: Local outbox, Supabase sync and recovery

This slice introduces a major distributed-systems boundary.

Design the local outbox and server-side application protocol before implementing synchronization.

Required properties:

- Local authoritative writes and local outbox intent are atomic.
- Remote application is idempotent.
- Duplicate delivery cannot produce duplicate logical effects.
- Retries converge.
- Out-of-order delivery is handled explicitly.
- Conflicting authored revisions are preserved.
- Local and remote identity remain consistent.
- Acknowledgment reflects actual server durability.
- Process death cannot silently lose committed local writes.
- Recovery resumes from recorded state.
- Owner isolation survives synchronization.
- Server and local state can be independently inspected.
- Server failures do not destroy local capture capability.

Do not use last-write-wins for authored content.

Do not claim cross-store atomicity between PostgreSQL and blob storage without an explicitly demonstrated mechanism.

Keep provider-specific commitments inside the owner-approved boundaries of Q12.

Test:

- Offline capture.
- Process restart before synchronization.
- Network loss during delivery.
- Timeout after remote commit but before acknowledgment.
- Repeated delivery.
- Concurrent modifications.
- Conflicting revisions.
- Out-of-order events.
- Server outage.
- Cross-owner isolation.
- Remote/local mismatch.
- Interrupted recovery.

The central acceptance condition: every committed local write must be remotely durable or explicitly queued and recoverable.

## P3-09: Export and restore

Implement a versioned authoritative-state export and restoration contract.

The export must cover authoritative records, source references, revisions, provenance and required retention/purge state.

Derived indexes must be rebuildable.

Define canonical state comparison rather than relying on row counts or successful archive creation.

Test:

- Export to a clean destination.
- Restore.
- Canonical state hash comparison.
- Repeated restoration.
- Missing source blobs.
- Malformed archives.
- Interrupted restoration.
- Corrupt derived indexes.
- Tombstone and purge interactions.
- Attempts to resurrect purged material.

A restore operation must not resurrect a governed purge.

Do not silently ignore a missing blob or incomplete revision history.

---

# 6. PHASE 3 INTEGRATED EXIT GATE

Do not advance on the basis of merged PR counts.

Prove the integrated product path on the final main revision.

All of the following are required:

1. Work, Source and Anchor identity contracts are explicit.
2. Real import creates the correct source records.
3. Capture produces Highlights with valid Anchors.
4. Bookmarks return to saved locations or report typed resolution failures.
5. Notes retain complete revision history.
6. Keyword lookup retrieves the expected material.
7. Local writes survive crash, restart, replay and defined offline faults.
8. Local-durable and server-durable are distinguishable.
9. Synchronization uses explicit recoverable states.
10. Writes are attributed and owner-scoped.
11. Independent owner-isolated reads pass.
12. Revisions remain immutable.
13. Tombstone and restoration work.
14. Governed purge remains effective after restoration.
15. Derived material can be rebuilt without losing authored data.
16. Export/restore satisfies the authoritative-state equality contract.
17. Every SYS requirement traces to executable tests and proof records.
18. Every required slice has passing independent verification.
19. Every known-bad case is caught.
20. The clean-clone user-like acceptance path passes through an uncoached task agent.
21. A separate grader passes the system without P0/P1 defects.
22. Not-verified conditions remain explicit.

A successful PR or elapsed time never constitutes Phase 3 completion.

The Phase 3 exit gate is the next owner checkpoint.

Do not fabricate its approval. Deliver the complete evidence package for the actual owner checkpoint.

---

# 7. PHASE 4: ESTABLISH THE FIRST USABLE PRODUCT

Phase 4 is the reader and Journal path.

The intended product sequence is:

**Open material → read → highlight → bookmark → write Notes → preserve Journal thoughts → reference other material → return and recover.**

Follow the outcome roadmap already established in PLAN.md.

Important: P4's roadmap is an outcome specification. The detailed executable cards must be elaborated one phase deep at the Phase 3 exit using actual implementation evidence. Do not invent a premature second roadmap.

## P4-00: Foundation and integration contract

This must precede broad UI implementation.

Its job is to establish the contract between the backend and the actual reader/Journaling client.

Specify:

**Identity and authorization**

Authenticated client identity, owner scope, authorization on every relevant query and operation, expired-session handling and forbidden-access behavior.

**Core operations**

Import, open, read-position, Highlight, Bookmark, Note, Journal and reference operations.

**Durability states**

Saved, queued, synchronized, conflicted and failed.

Every state must correspond to a real system condition. Never equate request initiation with successful persistence.

**Identity and references**

Stable identifiers and resolution semantics across rename, revision, tombstone, purge, missing targets and ambiguous targets.

**API behavior**

Pagination, bounded responses, typed errors, validation, retry, idempotency and compatibility.

**Offline behavior**

Local state, remote authority, synchronization handoff, invalidation and recovery.

**Format capability**

Format matrix, extraction readiness, unresolved anchors, malformed files and unsupported formats.

**Compatibility and rollback**

Client/API versioning, database migrations, supported prior states, rollback boundaries and mixed-version behavior.

**User scenarios**

Define actual day-one tasks and executable acceptance scenarios before building broad UI.

The critical architectural rule:

The reader client must never write directly to product database tables.

It must use the authorized API boundary.

It must not use a service-role or privileged key to bypass owner-scoped authorization.

A mocked client can support design exploration. It cannot count as integration proof.

P4-00 is accepted only when a real contract test exercises the authenticated API boundary and demonstrates the expected behavior.

## P4-A: Format intake and reader position

Implement the approved document intake and position contracts incrementally.

Cover the approved PDF, EPUB and JSON paths and the broader readable-format intake requirement already recorded in owner intent.

Do not falsely assume that every file is equivalent.

Explicitly distinguish:

- Native text versus scanned images.
- Fixed-layout versus reflowable content.
- Extracted versus unextracted sources.
- Supported versus unsupported formats.
- Valid versus encrypted or malformed inputs.
- Original versus transformed document representations.

For each declared supported format, establish an acceptance corpus.

Test ingestion, opening, reading position, anchor derivation, extraction readiness, source versioning, source changes and recovery.

OCR is a separate capability, not an automatic implication of accepting PDFs.

Respect Q8's corpus limitations. Synthetic results may establish synthetic behavior, not real-world document fidelity.

A format is supported only when its acceptance evidence exists.

## P4-B: Reading and capture integration

Build the reader client in its authorized repository or host, not inside the backend-only Arivoo repository.

First establish where the authorized client codebase lives. Do not invent or create an additional project without respecting owner authorization and the existing product architecture.

Connect the client to the actual API.

Implement:

- Import and open.
- Reading position.
- Highlight capture.
- Bookmark creation and return.
- Margin Notes.
- Saved-state progress.
- Offline behavior.
- Retry behavior.
- Authentication and authorization.
- Uncertain-acknowledgment handling.

The client must communicate the real persistence state.

Test:

- Expired authentication.
- Forbidden source access.
- Malformed request DTOs.
- Offline transitions.
- Timeout with uncertain acknowledgment.
- Duplicate interaction.
- Reload and process restart.
- Stale source version.
- Deleted target.
- Retry after lost response.
- Unresolved or ambiguous anchors.

The client may not report an item as saved merely because the user clicked a button or the request was submitted.

## P4-C: Library, reading lists, resumable behavior and Journal

Implement the owner's higher-level reading and thinking environment.

Library membership and reading-list operations must use stable identities.

Reading progress must remain attributable and recoverable.

Support approved current-reading state and session/coarse-position/dwell events, respecting the established D-010 boundary.

### Journal as a writing environment

This is a critical part of Arivo.

The Journal must preserve free-form owner-authored material.

Support:

- Long-form raw thoughts.
- Free-standing Journal entries.
- Source-linked writing.
- Writing that is not connected to a Source.
- Durable text blocks.
- Explicit relationships.
- Immutable history.
- Reordering and retrieval under the approved contract.
- Diagram blocks only after serialization and round-trip behavior are specified.

Do not turn Journal into a forced summary workflow.

Do not discard formatting or authored text during serialization.

Do not force every thought into a short Note abstraction.

Respect Q6: its research-transcript decision blocks only the specifically dependent acceptance scenarios and corpus. It must never be used to block unrelated Journal and capture work.

## P4-D: Stable @ references

Implement the stable reference system.

The distinction between entity identity and a selected historical revision must remain explicit.

A reference must survive ordinary title or label changes without losing identity.

Define and implement resolution for:

- Current target.
- Historical revision.
- Tombstoned target.
- Unavailable target.
- Ambiguous target.
- Purged target.

Never silently substitute a different target.

Never expose deleted private content.

Never reveal another owner's entity existence.

Imported text containing apparent `@` references is untrusted input. Reading an imported instruction or reference must never grant the imported material authority to create privileged relationships or mutate system state.

Test malformed, forged, ambiguous, inaccessible and obsolete references.

## P4-E: Baseline scoped agent access

This is mandatory for the first usable milestone. It is not deferred automatically to Phase 5.

Authorized agents must be able to retrieve relevant owner Journal and capture context through the same governed API.

First implementation is READ-ONLY.

Every query must enforce:

- Authenticated owner scope.
- Permission boundaries.
- Provenance.
- Source identity.
- Revision identity.
- Anchor information where relevant.
- Trust status.
- Explicit retrieval budgets.
- Bounded response sizes.

Imported text is untrusted.

Agent context must distinguish owner-authored material, imported content and generated/derived material.

No unrestricted database access.

No service-role bypass.

No hidden privilege escalation through an MCP or agent adapter.

Use the same kernel, API authorization and query semantics as the reader client.

Handle Q9 and Q10 honestly. Preserve the repository-visibility and credential-hardening boundaries under owner control. Apply approved conservative technical controls where permitted.

Do not add agent write capabilities before their authorization and state-transition contracts exist.

## P4-F: Recovery, regression proof and phase gate

Integrate the entire user workflow.

Verify supported prior-state migrations, Journal/reference/diagram lifecycle, export/restore, owner isolation, synchronization conflicts, indexing rebuild and recovery.

Prove that:

- Committed writing remains available.
- References remain meaningful.
- Restored state matches authoritative state.
- Purged material cannot be resurrected.
- Derived state can be rebuilt.
- Conflicting changes do not destroy authored history.
- The actual client and backend remain compatible.
- Agents access context only through permitted scopes.

The client must be exercised by a clean external task agent.

An independent grader must verify the task without relying on the builder's explanation.

The owner must review actual product fidelity.

Real UI/user validation remains BLOCKED until a genuine reader/Journaling host exists. Never fabricate user-validation evidence from backend tests, screenshots, mock interfaces or generated demonstrations.

---

# 8. PHASE 4 EXIT GATE: THE REAL OWNER WORKFLOW

The final acceptance scenario is the owner's actual day-one workflow.

Execute this sequence on the real integrated system:

1. Authenticate as the owner.
2. Import a real supported document.
3. Open the document.
4. Read and change position.
5. Save the reading position.
6. Highlight a passage.
7. Create a Bookmark.
8. Return to that Bookmark.
9. Write a Note.
10. Revise the Note without destroying its history.
11. Capture a free-standing Journal thought.
12. Create and follow stable @ references.
13. Close or leave the application.
14. Reopen it.
15. Recover the same document, position, Highlights, Bookmarks, Notes and Journal entries.
16. Verify truthful durability states.
17. Exercise offline, uncertain acknowledgment, retry and synchronization behavior.
18. Exercise stale-source and unresolved-reference behavior.
19. Export and restore.
20. Verify authoritative-state equality.
21. Exercise purge and prove invalidation of derived state.
22. Exercise authorized agent reads through the same API.
23. Attempt forbidden cross-owner and hostile-import operations.
24. Verify that all forbidden operations fail closed.

The proof must include:

- Backend tests.
- API contract tests.
- Actual client integration.
- UI workflow validation.
- Migration and recovery tests.
- Security and owner-isolation tests.
- Independent system grading.
- Current requirements traceability.
- Fresh-context SEV.
- Owner-fidelity review.

The integrated gate passes only when all independent requirements pass.

An unresolved owner-decision sub-gate must be explicitly identified. Complete independent work regardless; never describe a blocked sub-gate as completed.

---

# 9. SEVEN MANDATORY REFINEMENT ROUNDS

Once the Phase 4 path is end-to-end enough to exercise, conduct all seven mandatory refinement rounds.

Seven is the minimum commitment, not the stopping condition.

Every round must record the revision under review, reproduced findings, new regressions, repairs, rerun results and changes to the evidence package.

### Round 1: Requirements and contract traceability

Compare every implemented behavior against owner intent, SYS requirements, PLAN, RTM and acceptance criteria.

Find missing, ambiguous, contradictory, redundant or unsupported behavior.

Repair traceability gaps before accepting architecture claims.

### Round 2: Trust boundaries and authorization

Attack the system.

Test cross-owner access, forged identities, imported instructions, malformed inputs, unsafe references, authorization bypasses, privileged interfaces and agent-scope escalation.

Verify every refusal.

### Round 3: Domain identity, provenance, revisions and anchors

Test stable identities, source-version changes, anchor resolution, historical references, revision integrity, attribution and tombstone behavior.

Attempt silent retargeting and history loss.

### Round 4: Transactions, replay, concurrency and failure injection

Test competing writers, move/lifecycle races, retries, duplicate requests, crash points, partial completion, interrupted commits, uncertain acknowledgments, synchronization ordering and recovery.

Use deterministic interleavings where possible.

Inspect independent database state.

### Round 5: Client/API integration and truthful UX states

Examine the actual user interaction.

Find states where the client displays success without durable completion.

Test timeout, retry, offline transitions, authentication expiry, stale state, conflict presentation and recovery.

Verify that every displayed status reflects the real backend state.

### Round 6: Recovery, migrations, purge, rebuild and resource envelopes

Test supported prior-state migrations, restoration, export integrity, purge propagation, index rebuilding, synchronization recovery, storage failures and realistic resource constraints.

Measure performance at representative data volumes.

Define budgets before accepting performance claims.

### Round 7: Independent clean-room grading and owner-task fidelity

Give a clean environment to an independent agent.

Do not supply the implementation's private assumptions or a step-by-step workaround.

Ask it to complete the owner workflow from the documented product contract.

Have a separate grader evaluate its result.

The owner examines whether the system genuinely serves the intended workflow.

### Reopening rule

A defect discovered in a previously passed round reopens that round and all affected downstream gates.

Do not treat completion of seven rounds as proof of completion.

Continue refinement until the actual Phase 4 exit conditions are satisfied.

---

# 10. SCIENTIFIC VERIFICATION STANDARD

Use experimental reasoning throughout the project.

For every important claim, establish a test capable of disproving it.

Distinguish:

**Safety properties:** something bad never happens. Examples: a bookmark never changes source identity silently; another owner never sees private material; a committed Note is never silently overwritten.

**Liveness properties:** something good eventually happens. Examples: a queued write eventually synchronizes after connectivity returns; recovery progresses after interrupted work.

**Consistency properties:** independently derived representations agree with authoritative state.

**Performance properties:** latency, memory, database load, storage consumption and throughput remain within explicitly defined limits under representative workloads.

These are different classes of requirements. Passing one class does not establish the others.

Use, where appropriate:

- State-transition testing.
- Property-based testing.
- Metamorphic testing.
- Differential testing.
- Mutation testing.
- Fault injection.
- Concurrency scheduling.
- Independent database reads.
- Round-trip serialization tests.
- Differential migration testing.
- Adversarial authorization testing.
- Resource and performance measurements.

Avoid meaningless test volume. A thousand assertions around the same happy path do not replace one discriminating test of the actual failure boundary.

For every discovered defect:

1. Preserve a reproduction.
2. Identify the violated invariant.
3. Identify the missing enforcement mechanism.
4. Establish a regression that fails before the fix.
5. Repair the mechanism.
6. Prove the regression passes.
7. Test related operations for regressions.
8. Update the proof and notverified records.

A defect is closed by evidence, not by a persuasive explanation.

---

# 11. ARCHITECTURAL INVARIANTS ACROSS PHASES

These invariants apply to every new feature.

**Authority:** Authoritative user content must remain distinguishable from derived data, imported data and generated output.

**Identity:** Logical identity must not depend on titles, paths, presentation or accidental storage details.

**Provenance:** Material operations retain owner, actor, source, revision, time and required execution provenance.

**Immutability:** Authored history must not disappear because a newer revision exists.

**Resolution:** An unresolved or ambiguous reference must be represented explicitly, never silently redirected.

**Isolation:** Every owner-scoped read and write enforces the owner boundary.

**Durability:** Acknowledgments represent actual committed or queued states.

**Idempotency:** Repeating an operation with the same identity and body produces no duplicate logical effects.

**Recovery:** Every interrupted operation has a defined and testable recovery path.

**Derived-state separation:** Indexes, embeddings, extraction artifacts and other derivations never become the sole source of authored truth.

**Purge:** Governed deletion must invalidate all relevant derived copies and survive restoration.

**Security:** Imported content never obtains authority simply because a model or application processed it.

**Compatibility:** Each schema and API change must consider supported existing data and clients.

**Resource boundedness:** Query responses, agent context, pagination, indexing and resource-intensive work have explicit limits.

If a new design violates one of these invariants, resolve the conflict before implementation.

---

# 12. MULTI-AGENT EXECUTION MODEL

Use agents to increase independent reasoning and execution capacity, not to multiply uncoordinated changes.

The orchestrator owns project state and task sequencing.

The Builder owns the scoped implementation.

The Test Verifier attempts to falsify the implementation.

The SEV independently evaluates the systems-engineering implications.

The Phase Gate Grader independently evaluates milestone evidence.

The owner controls owner intent and reserved approval decisions.

Every agent must:

- Read repository instructions.
- Check the claim registry.
- Respect its assigned scope.
- Record actual evidence.
- Avoid claiming work owned by another agent.
- Push meaningful changes.
- Leave a durable handoff.

Never allow two open claims to overlap on non-shared files.

Do not permit the Builder to approve its own correctness.

Do not allow agents to silently change canonical requirements.

Disagreements must be recorded and resolved through the documented authority order.

Use different contexts and, where useful, different model families for independent testing. Model identity alone does not establish independence.

---

# 13. CHANGE MANAGEMENT AND REPOSITORY MEMORY

The repository is the project memory.

Every meaningful engineering result must become durable.

For each slice:

- One claim.
- One coherent scope.
- One branch.
- One PR.
- One explicit acceptance contract.
- One RED-first evidence chain.
- One reproducible proof set.
- One independent SEV report.
- One complete review-disposition chain.

Respect the established size and scope limits, branch protections, trusted verification, canonical-layer verifier, harness gates and known-bad tests.

Never weaken a check to get green.

Never hand-edit generated proof artifacts.

Never overwrite historical run records.

Bind digests only after all relevant content changes.

Push significant commits early. An unpushed result is not a durable project result.

At each meaningful session exit, append the correct WORKLOG entry.

For substantial work, create a numbered engineering record following `context/TEMPLATES.md`.

Update STATE as a navigation snapshot.

Keep AGENTS and PLAN synchronized with actual progress, correcting current contradictions without creating duplicate authorities.

Document exact commands, tested revisions, exit codes, observed CI, failures, fixes, not-verified conditions and the next deterministic action.

If the workspace resets, reconstruct from Git and the recorded evidence. Do not assume anything unpushed survived.

---

# 14. CONTINUATION AND STOP CONDITIONS

The standing instruction is to continue from the current state through the Phase 4 exit gate.

Do not stop because:

- A feature is implemented.
- A PR is opened.
- A PR merges.
- CI becomes green.
- A verification report is produced.
- A session ends.
- An agent's context expires.
- A previous checklist has been completed.
- An individual milestone looks impressive.

After every successful slice, select the next valid task.

When a task is blocked, record the exact blocker and proceed with independent work wherever the dependency graph permits.

Do not manufacture work to keep the agent busy.

Do not introduce speculative infrastructure or pull Phase 5 behavior into Phase 4.

### Mandatory safety stops

Stop the affected change and report when:

- A P0/P1 defect is found.
- A data-loss or isolation guarantee cannot be established.
- An irreversible operation lacks the required authorization.
- A blocking owner decision exists.
- Two authoritative requirements conflict.
- A proposed change weakens a law, security boundary or verification gate.
- Three implementation cycles fail under the established operating model.
- The necessary repository or environment permission is unavailable.

A stop condition must produce a durable record containing the finding, evidence, affected scope, unresolved question and exact next action.

Do not silently proceed through a known safety defect.

Owner checkpoints remain owner checkpoints. Do not simulate the owner's approval.

### Final stopping condition

The mission is complete only after:

1. All remaining Phase 3 slices are landed and verified.
2. The Phase 3 integrated exit gate passes.
3. All Phase 4 slices P4-00 through P4-F are completed.
4. All seven mandatory refinement rounds are completed, with any reopened rounds resolved.
5. The actual owner workflow passes through the real client and backend.
6. The Phase 4 integrated exit gate passes.
7. Independent grading passes.
8. Owner-fidelity review is completed.
9. The canonical records and final project state reflect the actual result.
10. All remaining limitations are accurately disclosed.

Do not begin speculative Phase 5 development under this mandate.

At completion, deliver an engineering closure report containing the final revisions, system capabilities, verified requirements, test and CI results, independent verification results, remaining limitations and exact owner-approval status.

---

# 15. FIRST EXECUTION ORDER

Do not spend another session rewriting the roadmap or creating a second architecture specification.

Begin with these operations:

**First:** reconstruct the current live repository, GitHub and PR #90 state.

**Second:** finish the bookmark concurrency defect using deterministic PostgreSQL tests and close the existing review chain.

**Third:** complete P3-05's evidence and authorized merge.

**Fourth:** execute P3-06, P3-07, P3-08 and P3-09 in the authoritative sequence, with bounded claims and independent verification.

**Fifth:** prepare the Phase 3 integrated acceptance scenario and complete the actual exit gate.

**Sixth:** elaborate the Phase 4 executable cards from the real Phase 3 evidence. Preserve the existing P4-00 through P4-F outcomes.

**Seventh:** establish P4-00's actual client/API contract before broad UI work.

**Eighth:** implement and verify P4-A through P4-F, including the external reader/Journaling client and baseline scoped agent access.

**Ninth:** conduct the seven refinement rounds, re-opening any affected gate when new evidence demands it.

**Tenth:** complete the actual Phase 4 user workflow and independent exit grading.

**Continue until the final stopping condition is satisfied.**

---

# FINAL OPERATING PRINCIPLE

Treat Arivo as a real product and a real information system whose users' authored material must survive.

Do not optimize for appearing productive. Optimize for increasing the amount of correct, durable, independently verifiable functionality in the actual system.

Be ambitious about capability, conservative about claims, rigorous about evidence and relentless about closing the distance between intended behavior and demonstrated behavior.

The roadmap establishes what must exist.

The requirements establish what must be true.

The implementation establishes the mechanism.

The experiments establish what survives.

The independent verification establishes what can be trusted.

The integrated workflow establishes whether the product actually works.

**The mission is not complete when the software looks finished. It is complete when the owner can use it, trust it, leave it, return to it and find everything important exactly where the system promised it would be.**