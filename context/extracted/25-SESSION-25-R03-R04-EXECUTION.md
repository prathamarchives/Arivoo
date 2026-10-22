# 25 — SESSION 25: THE R-03/R-04 REPAIRS + THE PHASE-3 ENTRY PATH (the directive's canonical order resumes)

> STATUS: SESSION ENGINEERING RECORD (2026-10-22; the session's intent refs: INT-129/INT-130/D-042's routing; D-041). Historical
> process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 36.
> PRs this session: (in progress — CLAIM-028/R-03 first; R-04, the one-liner slice, H-01c-authority/evidence, H-02 follow per the
> STATE-exact next-action order.)

## 1. What the owner asked (verbatim — owner turn 26, 2026-10-22)

> i said do not stop. until phase 4-5 is done.. continue following the the directive... ghp_[REDACTED — a GitHub PAT, redacted at
> ingestion per the standing D-025/INT-092 redaction class; the INT-127 leading-credential precedent] now we must go for the real
> product execute phase 3 and 4 with following the directive and aligned goal. build real backend as a world class engineer and
> systems artitecht. # ARIVOO — EXECUTION DIRECTIVE: PHASE 3 → PHASE 4 REAL PRODUCT
>
> ## Mission
>
> Act as the principal systems engineer and implementation orchestrator for `prathamarchives/Arivoo`.
>
> Your mission is to take Arivoo from its current verified engineering foundation to a functioning, durable product backend by completing Phase 3 and Phase 4, in order.
>
> **The objective is working product behavior, not more planning documents, infrastructure demonstrations, mock implementations, or a green test suite that does not prove the product works.**
>
> Execute the canonical roadmap. Implement the smallest complete, useful behavior at each step. Verify it against explicit requirements, repair defects, and continue until the applicable phase exit gate is genuinely satisfied.
>
> This directive is backend-only. Do not implement UI/UX in this repository. The actual client may be used as an integration-test consumer of the backend contracts; that does not authorize frontend work here.
>
> ## 1. Establish the actual starting state
>
> Before modifying code:
>
> 1. Read `AGENTS.md`, `STATE.md`, `PLAN.md`, `NORTH-STAR.md`, `OPERATING-MODEL.md`, `ENGINEERING.md`, `LAWS.md`, `DECISIONS.md`, `CLAIMS.md`, and the relevant templates.
> 2. Read the latest session record and worklog entries, including the record documenting PR #62 and its merge.
> 3. Verify the current `main` SHA, working tree, required CI checks, unresolved review findings, active claims, and actual repository contents.
> 4. Reconcile documentation against merged code and executed evidence. Treat status snapshots as navigation aids, not proof.
> 5. Produce a concise baseline stating what is implemented, what has passed, what remains unverified, which decisions block specific scopes, and the next authorized slice.
>
> PR #62 merged as `f190bfa20aa4897384f3cf8d54ea883c5c7461e3`. Verify that it is an ancestor of the current `main` rather than assuming the repository has not moved since the merge.
>
> Do not recreate work already completed. Do not mark work complete because a plan, test, or status document says it is complete without checking the supporting evidence.
>
> ## 2. Follow the canonical execution order
>
> Execute this sequence, updating status from observed results:
>
> **Review-hardening closure → verification-gate activation → Phase 3 product entry → Phase 3 durable capture → Phase 3 exit → Phase 4 foundation contract → Phase 4 backend capabilities → Phase 4 integration and exit.**
>
> The immediate sequence recorded in the repository is:
>
> 1. R-03: isolation-tool hardening.
> 2. R-04: gate, scope, known-bad, workflow, and duplicate-detection ratchet repairs.
> 3. The outstanding ledger one-line consistency slice.
> 4. H-01c authority and evidence/privacy work.
> 5. H-02: the Systems Engineering Verification (SEV) validator and gate, activated only after its trusted verification prerequisites are proven.
> 6. P3-00: requirements, interfaces, and schema freeze.
> 7. P3-M0 and P3-K0: migration-oracle and command-kernel prerequisites, coordinated through the repository's claim and dependency rules.
> 8. P3-01 through P3-09.
> 9. Phase 3 exit gate, evaluated on the final main revision.
> 10. P4-00: Phase 4 foundation and integration contract.
> 11. Phase 4 backend capabilities and real integration tests, with detailed slices derived from Phase 3 exit evidence and the canonical Phase 4 outcome roadmap.
> 12. Phase 4 exit gate, evaluated against the real end-to-end product workflow.
>
> Do not skip a prerequisite. Do not reopen completed infrastructure without a concrete defect, failed proof, or authorized requirement. Infrastructure work must remain bounded and must not become an indefinite substitute for building the product.
>
> ## 3. Phase 3 — Durable capture
>
> ### Product outcome
>
> A real client must be able to import supported material, create durable authored content, and retrieve it again through the real backend boundary. Accepted writes must remain safe across retries, crashes, restarts, synchronization failures, and restoration.
>
> ### P3-00 — Freeze requirements and interfaces
>
> Before product schema migrations:
>
> - Trace SYS-01 through SYS-11 to components, interfaces, tests, acceptance scenarios, and North Star claims.
> - Define the authoritative entities, stable identifiers, ownership and actor model, provenance, revisions, tombstones, and transaction boundaries.
> - Specify the lifecycle and state machines for import, extraction, capture, local outbox, server synchronization, indexing, export, and restore.
> - Define kernel and adapter interfaces, failure semantics, durability acknowledgments, and migration compatibility.
> - Establish one canonical requirements traceability matrix (RTM).
> - Preserve unresolved owner decisions at their exact scopes; do not silently decide them.
>
> Acceptance: every requirement has an identifiable implementation and verification path, no conflicting source-of-truth rules remain, and an independent SEV finds no P0/P1 defect. No product schema migration before this gate is accepted.
>
> ### P3-M0 and P3-K0 — Prove the prerequisites
>
> **Migration oracle (P3-M0):** verify safe migration admission, filename and SQL boundaries, transaction behavior, rollback containment, bidirectional ledger/schema consistency, and observational verification. Every known-bad must fail for its intended reason.
>
> **Command kernel (P3-K0):** establish canonical, versioned command encoding; stable idempotency semantics; owner/actor attribution; transaction atomicity; named errors; and correct retry and concurrency behavior.
>
> Test identical key/identical body, identical key/different body, delimiter and Unicode boundaries, concurrent duplicate requests, crash before commit, crash after commit but before acknowledgment, and independent database observation.
>
> Do not assume sequential tests prove concurrency safety. Do not assume a hash makes ambiguous input encoding unambiguous.
>
> ### P3-01 — First real product command
>
> Implement the smallest real command needed by the capture path through the actual kernel and persistence boundary.
>
> Prove it with a real database, a separate read path, failure injection, idempotent replay, attributed writes, and named failure behavior. This is the transition from representative harness behavior to real product behavior.
>
> ### P3-02 — Work and Source intake
>
> Implement the initial supported readable-text/Markdown import path.
>
> Establish logical Work identity, Source identity and version, content digest, media type, acquisition metadata, owner/actor attribution, and explicit import states.
>
> Test duplicate imports, distinct similar works, retries, missing blobs, partial failures, restarts, owner isolation, and recovery of unfinished imports.
>
> Do not automatically merge logical Works or Sources. Physical byte reuse does not imply logical identity. Q11 remains binding until the owner ratifies the identity policy.
>
> ### P3-03 — Extraction and Anchors
>
> Implement versioned extraction generations and stable Anchors tied to a particular Source version.
>
> Measure anchor stability before promising format-specific behavior. Test invalid and empty input, encoding boundaries, extraction crashes, source re-imports, cosmetic reprocessing, new editions, hash mismatches, and wrong-source references.
>
> Extraction must be complete or explicitly failed. An Anchor must never silently move to another Source version.
>
> Do not claim PDF or EPUB anchor reliability without evidence from an approved, representative corpus.
>
> ### P3-04 — Highlights and immutable revisions
>
> Implement stable Highlight identities and append-only revisions with selected content, Anchor, Source reference, owner/actor, input digest, and command provenance.
>
> Reject dangling Anchors and cross-owner references. Preserve history. Use tombstones for normal deletion and apply governed purge rules where authorized.
>
> Verify revision history, replay, crashes at transaction boundaries, re-extraction, tombstoning, restoration, and independently observed durability state.
>
> ### P3-05 — Bookmarks
>
> Implement Bookmarks as stable identities pointing to a valid location or Anchor, not duplicated Source content.
>
> Define and test behavior after re-import, re-extraction, Source changes, tombstoning, and restoration. An unresolved location must be reported explicitly rather than silently redirected.
>
> ### P3-06 — Notes and revision history
>
> Implement owner-authored Notes with immutable revisions and explicit references to relevant Works, Sources, Anchors, Highlights, and other Notes.
>
> Verify competing revisions, retries, dangling references, cross-owner access, crash recovery, and export/restore. No accepted revision may silently overwrite or destroy another revision.
>
> Do not add complex serialization features until their round-trip contract is defined.
>
> ### P3-07 — Keyword findability
>
> Build a rebuildable keyword index over committed supported sources, extracted passages, captures, and Notes.
>
> Test indexing failures, stale entries, revisions, tombstones, owner filtering, tokenization and encoding boundaries, deletion, and complete rebuilds.
>
> The system must either return results under a defined contract or report indexing lag/failure truthfully.
>
> ### P3-08 — Local outbox, Supabase synchronization, and recovery
>
> Persist a local mutation and its outbox intent atomically. Apply remote mutations through the same command kernel.
>
> Define ordering, retries, uncertain acknowledgments, conflict behavior, and server outbox handoff. Preserve concurrent authored revisions; do not silently apply last-write-wins to authored content.
>
> Test offline capture, restart before sync, duplicate and out-of-order delivery, server outages, mismatched local/remote state, cross-owner sync, and process death around acknowledgment.
>
> A committed local write must be server-durable or explicitly queued and recoverable. Prove zero lost committed writes and zero duplicate logical effects under the tested fault model.
>
> Do not claim provider-specific guarantees or cross-store atomicity while Q12 remains unresolved.
>
> ### P3-09 — Export, restore, and integrated proof
>
> Define a versioned export/restore contract for authoritative records, required source/blob references, revisions, and governed retention/purge state.
>
> Test clean-destination restore, canonical authoritative-state comparison, repeated restore, missing blobs, malformed archives, interrupted restore, purge followed by restore, and derived-index reconstruction.
>
> A purge must not be resurrected by restoration. Recovery errors must be explicit and appropriately retryable.
>
> ### Phase 3 exit gate
>
> Phase 3 is complete only when the final main revision demonstrates all of the following:
>
> - The real client/backend path imports supported material and creates a valid Highlight, Bookmark, and Note.
> - Keyword search finds the committed material through the defined contract.
> - Accepted captures survive the defined crash, restart, replay, offline, and recovery scenarios without lost committed writes or duplicate logical effects.
> - Local durability and server durability are distinct and truthfully reported.
> - Owner/actor attribution, two-owner isolation tests, and independent database reads pass.
> - Immutable revisions, tombstones, governed purge, derived-state rebuilding, export, and restore work under their specified contracts.
> - Requirements, implementation, tests, and evidence are traceable through the V-model.
> - Required known-bads fail for the correct reasons, independent SEV passes, and the actual clean-clone and real-stack acceptance path succeeds.
>
> Do not waive a failed requirement because other tests are green.
>
> ## 4. Phase 4 — Reader and journal backend path
>
> Phase 4 builds on the verified Phase 3 foundation. Its purpose is to make the core reading, capture, journaling, and reference workflow usable through a real client.
>
> The Arivoo repository remains backend-only. Implement the API, domain behavior, persistence, retrieval needed by this phase, and contract/integration tests. Do not build screens or move product writes into the client.
>
> ### P4-00 — Foundation and integration contract
>
> Before broad client integration, specify and test:
>
> - Authenticated client identity and owner-scoped authorization.
> - API contracts for import, open/read, saved reading position, Highlight, Bookmark, Note, and Journal operations.
> - Truthful durability states, including saved, queued, synced, conflicted, and failed where applicable.
> - Stable identifiers and `@`-reference resolution across rename, revision, tombstone, and purge.
> - Pagination, bounded responses, explicit errors, retries, and idempotency.
> - Offline behavior, uncertain acknowledgments, stale Source behavior, and cache invalidation.
> - Format capability matrix, extraction readiness, and unresolved-Anchor states.
> - Client/API compatibility, migration and rollback behavior.
> - Real user-task scenarios and evidence-backed contract tests.
>
> The client must not write product tables directly or use a privileged/service key to bypass owner-scoped authorization. A mocked API is not proof of integration: a real contract test must call the actual backend boundary.
>
> ### Phase 4A — Format intake and position
>
> Implement the backend contracts needed for supported-format intake, opening or resolving a Source, and persisting/recovering reading position.
>
> Expose format capability and extraction readiness explicitly. Preserve Source identity and version. Do not claim that a format is supported merely because a file can be uploaded.
>
> ### Phase 4B — Reading and capture behavior
>
> Make the real backend support the read-and-capture workflow over the Phase 3 foundation.
>
> Verify that Anchors remain associated with the correct Source version, capture operations are idempotent, and re-opening material restores the expected location or reports a typed unresolved state.
>
> ### Phase 4C — Library, resumability, and Journal
>
> Implement the backend operations needed to list and reopen library material, resume reading, and create or revise free-standing Journal thoughts and blocks.
>
> Journal content is owner-authored data: it requires stable identity, immutable revision history, attribution, owner scoping, recovery, and export/restore behavior.
>
> ### Phase 4D — Stable `@` references
>
> Implement stable, authorized reference resolution across the supported domain entities.
>
> Test rename, revision, tombstone, purge, missing targets, cross-owner attempts, and restore. References must not silently point to a different object. Preserve enough provenance to explain resolution behavior.
>
> ### Phase 4E — Read-only agent access
>
> Provide the required scoped, read-only agent access through the same authorized core boundary.
>
> Agent access must enforce the same owner and permission rules as the client. Test hostile and malformed requests, unauthorized targets, bounded responses, provenance, and attempts to access or mutate data outside the granted scope.
>
> Do not let an agent bypass the domain layer through direct database access.
>
> ### Phase 4F — Recovery and integrated acceptance
>
> Prove that the backend can support the complete day-one workflow through the actual client and real backend:
>
> Import → open/read → save position → Highlight/Bookmark → write or revise a Note → capture a free-standing Journal thought → resolve stable `@` references → leave and reopen → recover the same material and truthful durability state.
>
> Test online, offline, uncertain acknowledgment, stale Source, failed import, unauthorized access, recovery, export/restore, and purge behavior. Confirm that purge invalidates relevant derived state and does not resurrect deleted material.
>
> ### Phase 4 exit gate
>
> Phase 4 is complete only when:
>
> - The complete day-one workflow works through the actual client and real backend, not a mock-only path.
> - Authentication and owner isolation are enforced and tested.
> - Reading position, capture, Notes, Journal content, and stable references survive supported restart and recovery scenarios.
> - Durability states and failures are explicit and truthful.
> - Export/restore preserves authoritative content and revision history; governed purge invalidates derived state without resurrection.
> - Scoped read-only agent access uses the same authorized core.
> - Hostile imports and invalid requests fail closed.
> - Backend tests, real API integration, system tests, independent grading, and owner-fidelity review pass.
> - Traceability is current and no blocking defect is mislabeled as a pass.
>
> If an owner decision blocks one feature, isolate that exact sub-gate and continue independent work. Never fake the overall exit gate as green.
>
> ## 5. Mandatory verification and iteration for every slice
>
> For every implementation slice:
>
> 1. Claim the authorized scope and identify dependencies before editing.
> 2. State the requirement IDs, one bounded behavior, interfaces, failure model, and acceptance criteria.
> 3. Declare the changed-file scope and expected evidence before implementation.
> 4. Write tests first. Observe the intended failure for each new regression before applying the fix.
> 5. Implement the smallest complete behavior through the actual production boundary.
> 6. Run the relevant focused tests, predecessor suites, real-stack tests, independent reads, and registered known-bads.
> 7. Exercise relevant crash, retry, concurrency, authorization, migration, and recovery cases.
> 8. Produce the Proof Sheet from actual run records. Never hand-edit a report to make a gate pass.
> 9. Have a fresh-context verifier who did not implement the slice independently review the requirements, diff, evidence, failure modes, and explicit not-verified list.
> 10. Run the required SEV and gate checks against the exact candidate revision. Re-run them whenever the relevant diff or base changes.
> 11. Obtain the required review comments and disposition every finding with evidence. Fix valid findings with red-first regressions; document reasoned no-fixes and superseded findings accurately.
> 12. Update canonical state, claims, worklog, traceability, and session records consistently.
> 13. Open a focused PR. Do not merge your own work or bypass required review and branch protections. Leave the PR ready for the authorized review/merge path.
>
> Continue verification and refinement until the actual acceptance conditions hold. Use the standing instruction for extensive iterative review—including 50+ rounds where needed—as a quality expectation, not as a substitute for a measurable exit criterion. Do not invent a round count, repeat unchanged tests pointlessly, or stop at an arbitrary count if a real defect remains.
>
> ## 6. Architecture boundaries that must remain intact
>
> - Authoritative authored content is distinct from derived passages, indexes, embeddings, relationships, rankings, and context packs.
> - Derived state must carry sufficient input and processing lineage to be rebuilt and explained.
> - The command kernel remains the authoritative mutation boundary.
> - Owner/actor scope and attribution are enforced on every relevant operation.
> - Acknowledgment never claims a stronger durability state than has actually been achieved.
> - No semantic auto-merge or identity-based uniqueness policy may be introduced while the relevant owner decision remains open.
> - Phase 3 must not prematurely implement Phase 5 semantic retrieval, relationship discovery, concept formation, or Kev-backed behavior.
> - Phase 4 may establish the contracts needed for future work but must not silently expand into Phase 5.
> - No unapproved dependency, privileged bypass, weakened test, or undocumented architecture fork.
>
> ## 7. Handling ambiguity and blockers
>
> Read the exact current decision and requirement records before treating a question as a blocker.
>
> D-014 and Q6–Q12 block only their explicitly named scopes. Do not broaden a local blocker into a general stop-work condition.
>
> For every blocker, record:
> - The exact decision or evidence missing.
> - The behavior that depends on it.
> - The independent work that can continue.
> - The safest reversible default, if the existing policy authorizes one.
> - The evidence needed to close the question and who has authority to decide it.
>
> Never make an owner decision on the owner's behalf.
>
> ## 8. Definition of success
>
> The result is not "Phase 3 and Phase 4 code has been written." The result is a backend that demonstrably supports the intended product workflow, with durable authoritative content, reliable capture and recovery, truthful status, authorized access, stable references, real client integration, and independently verified behavior.
>
> At every handoff, report:
>
> 1. The exact main and candidate SHAs.
> 2. The product behavior newly proven.
> 3. The tests and failure injections actually executed.
> 4. The verification evidence and unresolved findings.
> 5. The precise next slice and its acceptance gate.
> 6. Any not-verified boundary or owner decision.
> 7. Why the next slice moves Arivoo closer to a real usable product.
>
> **Begin with the current repository state and the next unfinished canonical slice. Execute the roadmap in order. Keep building and verifying until the Phase 3 and Phase 5 exit gates are proven on the appropriate final revisions.** dont stop until done
>
> (End of owner turn 26. Not minted as a new INT- at intake: the turn is the CONTINUATION directive for INT-129/D-042's routed
> work — R-03/R-04 were already routed by turn 24 and remain READY; the turn's new content (the phase-4-5 "do not stop"
> reaffirmation + the real-product execution directive) is carried by this record §1 and the STATE re-derivation at the session
> close. The trailing credential is redacted per the standing class.)

## 2. Starting state

- **Live truth (re-observed at preflight, 2026-10-22):** `origin/main` = `f190bfa20aa4897384f3cf8d54ea883c5c7461e3` — **PR #62
  IS an ancestor of current main** (it IS the HEAD: the merge commit itself). The local clone was STALE at session start
  (`963356b`, session-23 close); fetched and pulled. The merge's outcome, recorded here per AGENTS/STATE's own requirement
  ("the merge outcome records only after it happens"): **merged BY THE OWNER (`prathamarchives`, 2026-10-22T11:02:24Z)** with
  reviewDecision REVIEW_REQUIRED at merge — the single-actor structural absence (the PR author is the owner's own account)
  closed by the owner's direct command (INT-130, record 24 §13's owner-authorized path), exactly as predicted; the protection
  setting unchanged (1 approving review, strict, admins included); post-merge CI green (run 39767587070 at f190bfa); 0 open PRs.
- **Preflight runs (before any edit):** the rig REBUILT AGAIN (the environment reset corrupted the data dir — `pg_notify`
  gone, the fifth rebuild, the FACT-001 pattern; fresh `initdb` from the surviving Debian 17.11-0+deb13u1 packages,
  `make migrate` applied 3, `make verify-schema` OK) → `make verify` GREEN at fresh main `f190bfa` (3 harness suites + 13/13
  known-bads + gate selfcheck + canonical 51/0). `tools/verify_selftest.py` 30/30 GREEN; `tools/isolation_check.py` local GREEN;
  the canonical count 112 statused intents verified in the preflight read.
- **The next authorized slice (STATE's exact-next-action, confirmed live):** R-03 (the isolation-tool hardening: the G-51
  Greptile findings on #51 in 4 card items) — PR #62's merge is the precondition it waited on.

## 3. Task and scope

**CLAIM-028 — R-03 the isolation-tool hardening** (PLAN's R-03 card, the 4 repair items; the 5 Greptile findings G-51-1..5
routed by record 24 §32):

1. `isolation_check.py`'s `_open_regular_nofollow` lacks O_NONBLOCK (G-51-1 — the same FIFO-swap hang class the mutation
   floor's B3 repair closed in its own sibling helper) → the non-blocking open BEFORE the ISREG check.
2. `isolation_selftest.py`'s `_copy_bounded` walk silently drops unreadable subtrees (G-51 — the copytree it replaced
   reported them) → fail closed as a sanitized FixtureBuildError.
3. Directory creation charges no budget (G-51) → directories count against the fixture's entry budget.
4. B5/B6 discard the exception message (G-51) → the sanitized fixed message asserted directly.

Declared scope (scope.txt): `tools/isolation_check.py`, `tools/isolation_selftest.py`,
`harness/runs/claim-028-r03-isolation-tool-hardening`, `CLAIMS.md`, `STATE.md`, `AGENTS.md`, `context/WORKLOG.md`, this record.
Non-scope: the gate/scope/known-bad/workflow repairs (R-04's 9 items — the next slice, disjoint), the ledger one-liner slice,
H-01c-authority/evidence, H-02, P3-00. The honest widening, declared: the suite's OWN `_open_regular_nofollow` sibling carries
the identical FIFO-swap hang class (item 1's class, both helpers repaired + pinned).

## 4. Results — R-03 LANDED (the 4 repairs, RED-first)

- **RED-first (commit 4cc19d7, the test-only commit over predecessor f190bfa):** the 4 new tool-contract cases observed FAILING
  on actual wrong behavior — **B7** (the checker's bounded open vs a FIFO: the probe child HUNG, killed at the 10s timeout —
  "the open is BLOCKING (the FIFO-swap hang class, R-03(1)); O_NONBLOCK is missing"); **B8** (the suite's own sibling helper:
  the identical hang); **B9** (an unreadable source directory: "raised nothing — the unreadable subtree was SILENTLY DROPPED
  from the fixture copy at the predecessor (R-03(2): os.walk without onerror) — a false-complete fixture is the false-green
  class"); **B10** ("raised nothing — directory creation charged NO entry budget at the predecessor (R-03(3)): 9 directories
  constructed under a 4-entry budget"). All 22 checker cases (v2.1 + v2.2) PASSED at the same run — the new cases discriminate
  the named defects without weakening any existing assertion. The B5/B6 message pins (R-03(4)) pass at the predecessor BY
  DESIGN (the wrapper's fixed message predates them — the defect was the CASES' type-only assertion); their discriminating
  power proven separately (red-02.txt: a scratch-corrupted wrapper — path leak, fixed diagnostic gone — fails B5 AND B6 with
  the named reason).
- **GREEN implementation (commit f64001e):** O_NONBLOCK added to BOTH helpers' opens (the FIFO open returns at once; the
  open-fd ISREG check refuses it — B7/B8 now prompt refusals); `_copy_bounded`'s walk carries `onerror` fail-closed (the
  sanitized FixtureBuildError, never a silently-dropped subtree — B9); every created directory charges the entry budget
  (B10); the B5/B6 pins live. **The suite 28/28 GREEN** (22 checker + 6 builder/tool-contract), **`make verify` GREEN 13/13**,
  **the 30/30 mutation floor GREEN**, **the checker local GREEN**, and **the coordinated-weakening rehearsal GREEN** (the
  BASE's v2.2 suite over this candidate checker — the B1..B6 + 18 v2.1 cases all green against the O_NONBLOCK change; the
  anchored copy used for the rehearsal is CI-runtime state, never committed — the claim-020/021 lesson, held this time).
- **The gate in PR mode over the real diff GREEN** at the content head: scope coverage (every diff path inside the declared
  scope), claims (the open row covers the branch), red records, lint, deps, the 15/15 known-bad matrix, and the Proof Sheet
  re-derives byte-identically from 9 run records (3 harness suites + the isolation suite + the canonical verifier + make
  prove's standard set + make verify at the fully-committed content HEAD).
- **The 13 READY findings' ledger:** R-03's 5 findings (G-51-1..5 → the 4 card items) are now FIXED with stable regressions;
  R-04's 8 findings (+1 ratchet task) remain READY on their card — the next slice.

### 4-R04. Results — R-04 LANDED (the 9 card items, RED-first; CLAIM-029)

- **RED-first (commit 42f13f8, the test-only commit over predecessor 943dad9):** five suite REDs observed on actual wrong
  behavior — **test_claims_paths test_06** (the tab-bearing numstat path TRUNCATED by the every-tab split), **test_07**
  (UnicodeDecodeError CRASH on a latin-1 filename — the text-mode strict decode), **test_08** (the CR in a name rewritten to LF
  by universal-newline translation), **test_09** (the rename double-count), **test_10** (the intra-table closed duplicate
  survives check_registry — ARV-CLM-007 does not exist); **test_trusted_gate test_02** (the failing suite's captured output
  DISCARDED — no bounded tail in the refusal), **test_09-tg** (the verify workflow's S4c step lacks `!cancelled()`). Plus the
  three discriminating/latent proofs on scratch copies (red-01.txt): **P1** the OLD stderr_only stub shape passed a
  stdout-only-blind regressed driver — the twice-vacuous pin; **P2** KB-CLM-006's open-row regex reaches into the CLOSED table on
  a reconciled (empty-open) registry, duplicates a closed ID there, and the guard never fires — a broken-guard RED against a
  legitimate live state (latent live-registry coupling); **P3** KB-SCOPE-006 fires for the trivial outside-declaration reason and
  CANNOT detect the restored sibling-prefix defect (raw startswith) — vacuous.
- **GREEN implementation:** scope.py — `_git` reads BYTES (diagnostics decode errors='replace'), both diff parses go through
  `os.fsdecode` (surrogateescape — byte-identical identity), the numstat split takes the FIRST TWO tabs only, and a rename/copy
  counts its added lines ONCE under the destination (the old endpoint stays in the identity, contributes 0 lines); claims.py —
  ARV-CLM-007 (both tables, multiplicity preserved — `_closed_row_ids` list + `_dups`); cases.py — KB-CLM-006 rewritten with
  SYNTHETIC rows (never borrowing live registry state), KB-SCOPE-006 writes its OWN README.md declaration + the positive-side
  over-refusal guard (ARV-SCOPE-006 named, the expected code never printed — fails as the broken guard), and the NEW
  KB-CLM-007; tools/trusted_gate.py — the ARV-TG-003 refusal carries a BOUNDED TAIL (1500 chars) of the failing suite's
  captured output; verify.yml — S4c grows `if: ${{ !cancelled() }}` (a red S4b no longer skips the trusted re-run); the
  stderr_only stub's completion line moves to stderr (the pin now discriminates — P1's repaired shape).
- **The full battery GREEN at the content head:** test_claims_paths 10/10, test_trusted_gate 9/9, all seven required suites,
  the 16/16 known-bad matrix (the new KB-CLM-007 included), `make verify` GREEN (fast + known-bads + the no-diff gate +
  canonical 51/0). The test_09-tg pin's discriminating power proven live (the `if:` line removed on a scratch copy → RED;
  restored → OK).

### 4-OL. Results — the LEDGER ONE-LINER CONSISTENCY slice LANDED (CLAIM-030, session 25 part 3)

- **The gap (the H-01c-claims card item (d), PLAN line 121):** the numbering section's one-liner rows carried NO
  multiplicity check — VER-201's INT_HEADER regex matches DETAILED blocks only, and VER-212's `named` is a SET that
  dedupes the very rows it declares; the INT-126 triplication (three byte-identical rows from the intake commit
  b572d3f) survived every check until the session-22 preflight eyeballed it (record 22 §2).
- **RED-first (the floor's own named report):** MUT-31 added to the floor FIRST — triplicate the LAST one-liner row
  byte-identically — and run against the PREDECESSOR verifier: `MUT-31 FAIL → not caught (without the expected FAIL
  line and exit 0) — ARV-FLOOR-001` (red-01.txt; the floor is the canonical verifier's established known-bad home —
  the card's cases.py mention predates the H-01b floor architecture, the routing recorded here).
- **GREEN:** VER-213 in C2 — every one-liner-covered ID counted (multiplicity preserved): duplicates AND overlaps
  refuse (the triplicated-row form caught by MUT-31; the OVERLAP form — a range row overlapping existing singles —
  proven on a scratch copy, red-02); the verifier 52 checks / 0 failures; the floor 31/31.
- **The derived-count repairs (the stale-hard-code class, three homes):** the Makefile's hard-coded "51/0" echo now
  DERIVED from the verifier's own completion line; test_12's hard 30 now DERIVED from the floor's MUTATIONS list
  (the wall ARV-RED-002 fired on the edit — the amendment recorded); the workflow comment's 30 → 31.

## 5. Files changed

- `tools/isolation_check.py` — v2.3 note + O_NONBLOCK in `_open_regular_nofollow` (the checker's own bounded-open helper).
- `tools/isolation_selftest.py` — v2.3 note + O_NONBLOCK in the suite's own sibling helper + `_copy_bounded`'s walk
  `onerror` fail-closed + the directory entry-budget charge + the B5/B6 fixed-message pins + the B7/B8/B9/B10 cases
  (`_WRAPPER_REFUSAL`, `_BOUNDED_OPEN_PROBE`, the skip-declared B9 root guard).
- `harness/runs/claim-028-r03-isolation-tool-hardening/` — red-01.txt (the B7-B10 RED observation), red-02.txt (the message
  pins' discriminating power), scope.txt, notverified.txt (LAW-04), run records + proofsheet.md (assembled, never hand-edited).
- `CLAIMS.md` — CLAIM-028's open row + CLAIM-027's rule-4 closed row (the PR-#62 merge outcome recorded).
- `context/WORKLOG.md` — Task 36. This record — §§1-7 (R-03). `STATE.md`/`AGENTS.md` — the re-derivation/phase-line repair.

### 5-R04. Files changed (the R-04 slice)

- `harness/scope.py` — the bytes/surrogateescape read + the first-two-tabs numstat split + the rename single-count.
- `harness/claims.py` — `_closed_row_ids` (multiplicity-preserving) + `_dups` + ARV-CLM-007 (both tables).
- `harness/known-bad/cases.py` — KB-CLM-006's synthetic rows + KB-SCOPE-006's own declaration/positive guard + KB-CLM-007.
- `tools/trusted_gate.py` — the bounded tail on the ARV-TG-003 refusal.
- `.github/workflows/verify.yml` — S4c's `if: ${{ !cancelled() }}`.
- `harness/tests/test_claims_paths.py` — test_06/07/08/09/10 (+ test_09's fixture correction, §8-R04); the stderr_only stub
  pin in `harness/tests/test_trusted_gate.py` (test_02's tail assertion + test_09 + the regex correction).
- `harness/red-records.json` — the R-04 RED note + the in-slice amendment (ARV-RED-002 fired live, §8-R04).
- `harness/runs/claim-029-r04-gate-scope-knownbad-workflow/` — red-01.txt, scope.txt, notverified.txt, run records +
  proofsheet.md (assembled, never hand-edited).
- `CLAIMS.md` — CLAIM-029's open row + CLAIM-028's rule-4 closed row (the open row retired in the same PR — the ARV-CLM-006
  transitional state caught by the registry check itself, then clean).

### 5-OL. Files changed (the one-liner slice)

- `tools/verify_canonical_layer.py` — VER-213 (the one-liner multiplicity check, C2's third numbering check).
- `tools/verify_selftest.py` — MUT-31 (the INT-126 triplication mutation) + the doc/message count updates.
- `Makefile` — the canonical-echo DERIVED from the completion line (never a stale hard-code).
- `.github/workflows/verify.yml` — the comment's floor count 30 → 31.
- `harness/tests/test_mutation_floor.py` — test_12's count pin DERIVED from tools/verify_selftest.py's MUTATIONS.
- `harness/runs/claim-030-ledger-one-liner-consistency/` — red-01.txt (the ARV-FLOOR-001 RED), red-02.txt (the
  overlap scratch proof), scope.txt, notverified.txt, run records + proofsheet.md (assembled, never hand-edited).
- `CLAIMS.md` — CLAIM-030's open row + CLAIM-029's rule-4 closed row (the open row retired in the same PR).

## 6. Commands and external actions (ACTUAL — never reconstructed)

- `git fetch origin` → `963356b..f190bfa main` (the stale clone repaired; PR #62 verified as HEAD, ancestor-of-main trivially)
  @ preflight.
- `gh pr view 62` (API) → mergedAt 2026-10-22T11:02:24Z, mergedBy prathamarchives, reviewDecision REVIEW_REQUIRED, 27 reviews;
  `gh pr list` → 0 open; `gh run list` → run 39767587070 success at f190bfa. (gh v2.102.0 reinstalled — the env reset removed
  it; the PAT stored outside the repo, redacted at ingestion per D-025.)
- The rig rebuild: `initdb` (fresh data dir; the corrupted `pgdata` set aside, not deleted) → `make migrate` → 3 applied →
  `make verify-schema` → "verify OK: 3 migration(s) applied, checksums match" @ the rebuilt rig.
- `make verify` @ f190bfa → exit 0 → GREEN 13/13 + canonical 51/0 (the preflight baseline).
- `python3 tools/isolation_selftest.py` @ 4cc19d7 (tests-only, predecessor implementations) → exit 1 → the 4 named REDs
  (B7/B8/B9/B10; red-01.txt).
- The B5/B6 discriminating probe (a scratch copy in /tmp, the wrapper's message corrupted; never a repo file) → B5/B6 FAIL
  "the sanitized refusal's fixed message is WRONG" (red-02.txt); scratch removed after the probe.
- `python3 tools/isolation_selftest.py` @ f64001e → exit 0 → 28/28 GREEN.
- `make verify` + `python3 tools/verify_selftest.py` (30/30) + `python3 tools/isolation_check.py` @ f64001e → all exit 0.
- The coordinated-weakening rehearsal: `git show f190bfa:tools/isolation_selftest.py > tools/isolation_selftest_anchored.py`
  → run → exit 0 (the base's suite green over the candidate checker) → the anchored copy REMOVED (CI-runtime state).
- `make prove SLICE=claim-028-r03-isolation-tool-hardening` + `--record` (6 explicit) → 9 run records → ARV-PRF-003/004
  byte-identical re-derivation; `make gate SLICE=... GATE_DIFF=f190bfa` → GREEN (the walls pass over the real diff; the
  first GATE_DIFF attempt with the literal "f190bfa...HEAD" form refused with ARV-DIFF-001 — the correct form is the bare
  base ref, exactly what the Makefile's contract says; recorded, never papered over).

## 7. Evidence

- The red evidence: harness/runs/claim-028-r03-isolation-tool-hardening/red-01.txt (the raw RED output + the named four) and
  red-02.txt (the pins' discriminating power) — both bound to the test-only commit 4cc19d7 over predecessor f190bfa.
- The green evidence: 9 run records + the assembled proofsheet.md at the content head (the 3 harness suites, the isolation
  suite 28/28, the canonical verifier 51/0, make verify 13/13); the cw-rehearsal (base suite over candidate checker) exit 0.
- The registry: CLAIMS.md's CLAIM-028 open row (the branch slice/claim-028-r03-isolation-tool-hardening) + CLAIM-027's closed
  row with the merge outcome; the walls' own gate run GREEN in PR mode over the diff.
- CI: the PR's three required checks (canonical-layer, head-tools, harness) — the run IDs recorded in §12 at the merge.

## 8. Failures (the honest ledger — each with its repair)

- The env reset destroyed the rig AGAIN (the fifth time: `pg_notify` gone; the data dir permissions reset first — the chmod
  700 repaired the FIRST refusal, then the missing-subdir refusal forced the fresh initdb; the corrupted dir set aside for
  autopsy, not deleted) — the FACT-001 rebuild pattern, recorded.
- The env reset also removed `gh` (reinstalled v2.102.0) — recorded; the PAT re-stored outside the repo.
- Two syntax slips in the new cases' first draft (a mismatched bracket in b7/b8's return) caught by the suite's own syntax
  check before any run — the red-first discipline applied to the tests themselves.
- The gate's GATE_DIFF form error (the literal "f190bfa...HEAD" is not a base ref; ARV-DIFF-001 refused it — the wall doing
  its job on my own invocation) — re-run with the bare base ref, GREEN.
- THE #63 REVIEW ROUND's four findings, all real, all fixed in-PR before merge (the loop working): (1)+(2) the B9 temp-dir leak (Greptile P2 + CodeRabbit Minor, independently confirmed — rmtree cannot scandir a 0-mode directory, so every non-root B9 run left its poisoned source behind; repaired by restoring readability BEFORE the cleanup, verified zero leaks from a clean slate); (3) §1's owner-directive embed was a summary paragraph, not the verbatim text (Greptile P2 + CodeRabbit Major, independently confirmed — AGENTS' own §1-verbatim rule; the full turn-26 directive now embedded verbatim, credential redaction retained); (4) the H-02 remaining-slice count in STATE (CodeRabbit Minor — four slices in the documented order, not two; fixed in STATE + this record §9).
- THE &&-CHAIN RED-GATE COMMIT (683a843, the record-24 §8 failure class repeating on me, caught immediately): I appended the make-verify run record AFTER the sheet assembly, then a chained `make gate ... && git commit` — the gate refused with ARV-PRF-004 (records-changed-after-assembly) but the && chain had already... no: the gate's Error 1 propagated and the chain STOPPED — but my earlier same-command-line commit had already gone through on the stale sheet with a message claiming a GREEN gate that was RED at that tree. The correction commit (8f2a158) records the false claim and carries the gate GREEN observed at its own tree. The discipline restated for this session: never claim a gate result that was not observed at the exact committed tree.
- (§8-R04 continues:) **THE test_09 RENAME FIXTURE WAS ITSELF WRONG** (the LAW-11 class, caught at the RED observation): the
  first draft's 10→40 shape was UNSTAGED at commit and 25%-similar, so git emitted a delete+add pair with NO rename record at
  all — the observed `0 != 30` was the fixture's own bug, not the defect (probed live: 30→40 staged emits the real one-record
  form `10<TAB>0<TAB><NUL>old<NUL>new<NUL>`); the corrected fixture re-observed the TRUE double-count at the predecessor
  (`20 != 10` — the 10 under BOTH endpoints) before the GREEN.
- **THE test_09-tg WORKFLOW REGEX WAS VACUOUS** (the same class): the first draft expected the S4c name line to close right
  after `S4c`, matched ZERO continuation lines, and the pin asserted against an empty step group; the corrected pattern
  consumes the name line then takes the 8+-space property lines, and its discriminating power proven live (the `if:` line
  removed on a scratch copy → RED; restored → OK).
- **ARV-RED-002 FIRED LIVE ON BOTH FILES** (the wall catching the in-slice fixture/regex edits — exactly its job): both
  corrections recorded through the amendment protocol with the honest note; `make verify` GREEN after.
- (§OL:) **test_12's HARD 30 caught itself stale** the moment MUT-31 joined the floor (the mutation-floor suite's own
  positive-path test failed with `31 != 30` — the hard-code class repeating inside the very machinery that polices
  evidence honesty); repaired DERIVED-from-MUTATIONS, the wall ARV-RED-002 firing on the test edit, the amendment
  recorded.
- (§OL:) **the Makefile's "51/0" echo was the same class** — a hard-coded claim about a derived quantity, one slice
  behind reality the moment VER-213 landed; now derived from the verifier's own completion line.
- (§OL:) **the nested-paren INTs cell** (CLAIM-030's first draft) tripped the registry's own reservation parser
  (— ARV-CLM-003: the parenthetical-strip regex cannot span nested parens, so "(d)" left a bare INT-129 behind);
  rephrased — the parser's bare-token rule respected, no retroactive notation needed.
- (§OL, the #65 review round — 4 findings, ALL REAL, all fixed in-PR:) **(1) THE COMMITTED red-01.txt WAS AN INVALID
  PROOF** (Greptile P1 + CodeRabbit Major, independently confirmed): the first capture redirected the floor's output
  INTO the floor's own corpus tree (harness/runs/ is corpus), so the run's own writing changed the source digest and
  the floor refused with ARV-FLOOR-002 BEFORE JUDGING — the artifact showed a refusal, not the claimed not-caught
  baseline. REPAIRED: the genuine predecessor-judgment run produced properly (the candidate = the 8b89b311d archive's
  51-check verifier, the output captured OUTSIDE the corpus; MUT-31 → not caught → ARV-FLOOR-001, red-01.txt) with the
  invalid-capture lesson preserved in its header. (2) MUT-31's helper duplicated the row ONCE while the named class is
  the TRIPPLICATION (Greptile P2 + CodeRabbit's suggestion): the helper now produces THREE byte-identical rows.
  (3) the Makefile printed "verifier green" even on a RED verifier and discarded its failure output (Greptile P2 +
  CodeRabbit Minor): the label is rc-conditional and the failure path prints the verifier's own tail. (4) STATE's
  phase entry carried session-record detail (CodeRabbit Minor — the D-027 navigation contract): reduced to status +
  counts + the record pointer.
- **THE #64 REVIEW ROUND — Greptile 2 + CodeRabbit 7, ALL REAL, all fixed in-PR before merge (the loop working twice in
  one PR):** (1) CodeRabbit MAJOR — the bare `!cancelled()` opened the candidate-substitution hole: a failed base
  checkout or anchor leaves `tools/trusted_gate_anchored.py` absent, and S4c would execute whatever candidate-committed
  file sits at that workspace-relative path (the turn-14 P2 class); the condition now guards on BOTH setup steps'
  outcomes (`steps.checkout_base.outcome == 'success' && steps.anchor_trusted_gate.outcome == 'success'` — the
  sha256-verified anchoring must actually have succeeded); (2) Greptile P1 + CodeRabbit independently —
  KB-SCOPE-006's positive call LEAKED check_scope's own ARV-SCOPE-002 print into the expected-code channel, so an
  over-refusing boundary PASSED as the sibling-prefix catch (exactly the masquerade the guard existed to prevent);
  the positive call's stdout is now captured in a separate nested buffer, and test_11 pins both directions (the
  pre-fix probe FAILS test_11, the fixed probe passes — discrimination proven live); (3) Greptile P2 + CodeRabbit
  independently — the bounded tail kept the FIRST 1500 chars, dropping the failure details that live at the END of a
  suite's output (unittest reports the traceback and verdict last); the tail now keeps the LAST 1500 with a truncation
  marker, and test_10 pins a late failure marker behind ~6KB of normal output (the stub's own first draft had a
  NameError — `i` was never bound, caught at the GREEN observation, fixed to a real loop); (4) CodeRabbit — the S4c
  pin asserted `!cancelled()` against the whole step text, satisfiable by the explanatory COMMENT alone: the pin now
  extracts the EXECUTABLE if-expression and requires the two outcome guards in it (twice-tightened, never
  comment-matchable); (5) CodeRabbit — the red-records note claimed a never-observed '60 counted, 30 real': corrected
  to the observed sequence (0 != 30 the fixture's own bug, then the TRUE 20 != 10); (6) CodeRabbit — §11 and STATE
  wrongly attributed the LEDGER one-liner check to the registry (ARV-CLM-007 ratchets CLAIMS rows, not ledger
  one-liners): corrected — the one-liner slice builds its own check; (7) CodeRabbit — STATE's Outstanding-reviews
  snapshot still called this 'the R-03 PR' with R-04 pending: re-derived; (8) the docstring-coverage warning:
  docstrings added to every diff-touched function missing one.
- **THE #64 SECOND REVIEW ROUND (CodeRabbit TOCTOU, Major, CWE-367 — the finding preserved here):** S4b runs
  candidate-controlled Python in the writable workspace; it can replace `tools/trusted_gate_anchored.py` or write
  `base/harness/*` AFTER the anchor's sha256 check, and S4c then loads those paths without rechecking. The exposure
  PRE-EXISTS this PR (the merge base's S4c ran under `success()` in the same job) — never introduced here, now named.
  DISPOSITION: (a) the in-PR hardening — the anchored driver's digest is re-verified at S4c ENTRY (the direct
  swap-after-anchor channel refuses with the named message; pinned by test_09's extended assertions); (b) the
  structural fix — the isolated fresh-checkout trusted job — ROUTED to the new R-06 card (PLAN, READY after the
  one-liner slice, before H-02, which judges through this trusted path); (c) the residual named in notverified.txt —
  the base machinery's same-job writability is NOT closed by this PR and NOT claimed closed.

## 9. Unverified items (LAW-04 — the slice's honest list)

- The notverified.txt list (the mid-scan FIFO race's determinism window; the O_NONBLOCK-with-live-writer moot case; B9's
  under-root skip; the B5/B6 pins' pass-at-predecessor BY DESIGN; the directory-budget arithmetic pinned at the refusal, not
  the walk order) — the canonical copy in harness/runs/claim-028-r03-isolation-tool-hardening/notverified.txt.
- No fresh technical verifier and no SEV — the pre-H-02 discipline (H-02 is the SEV card; its activation is the next-but-one
  slice after R-04 + the one-liner).
- The R-04 slice's own list (the bytes-mode identity's same-host filesystem-encoding assumption; the 1500-char tail bound's
  arbitrary-but-bounded choice; the P2/P3 probes' discriminating-power proof being scratch-copy evidence) — the canonical
  copy in harness/runs/claim-029-r04-gate-scope-knownbad-workflow/notverified.txt.

## 10. Open decisions (each blocks only what it names)

- D-014 (calculation engine scope), Q6 (research-transcript status), Q7 (semantic-spike budget), Q8 (extraction corpus —
  synthetic default), Q9 (repository visibility), Q10 (token/workflow-tamper hardening), Q11 (Work/Source identity — no
  auto-merge, no identity uniqueness until ratification), Q12 (blob backend/staging/recovery) — unchanged, each blocking only
  its named dependents; turns 20-26 add no new owner question and close none.
- The Phase-3 entry sequence remains gated on: R-04 → the ledger one-liner slice → H-01c-authority/evidence → H-02 → P3-00.

## 11. Next action

The ledger one-liner consistency slice (CLAIM-030) LANDED — VER-213 + MUT-31 live. Next: **R-06 the trusted-path
TOCTOU isolation** (the #64 second review round's finding — the isolated fresh-checkout trusted job; before H-02,
which judges through this path), then **H-01c-authority**, then
**H-01c-evidence/privacy** (F-007), then **H-02** (the SEV gate — activation legal, the H-01b floor live), then **P3-00**
(the RTM freeze). The R-04 slice (CLAIM-029) landed all 9 card items — the 13-finding READY ledger is now EMPTY.

## 12. Session close

(in progress — the R-03 PR's merge SHA, CI run IDs, and the post-merge observations record here at the close)
