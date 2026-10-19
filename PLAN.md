# PLAN — Arivo

One phase deep (NG-04). The next phase is planned only when current-phase evidence says what's needed. Predicates close phases, not dates. The slice cycle (OPERATING-MODEL §2) is the unit of execution inside every phase. The growth model (OPERATING-MODEL §6) defines the operating model per stage: how the repo runs, how its memory updates, and how its failures heal at each level of maturity. The law activation map is in LAWS.md (the proactive set and the live-at phase of each law).

## Guardrails from day one (proactive set — never deferred)
Isolated credentials · protected gates · real database test · idempotent writes · immutable evidence · owner scoping · independent state read. Everything else arrives through the ratchet, when it protects a concrete contract. The harness must never postpone the product (P-17). Full doctrine: ENGINEERING.md §4–§10.

## Phase 1 — Execution environment and trust (COMPLETE, 2026-10-14; extended same day by owner turn 10 — LAYER 1.2, INT-100/D-027)
Purpose: the repo is safe to build in, and the trust model is real.
- **W-01 Walls**: protect main (PR-only, no force push, applies to admins); CODEOWNERS on protected paths (deliberately deferred — rides Q-IDENT option (b): with a single identity it would convert every standing-authorization merge into an owner web-UI approval, violating P-06/P-15; session 12 §3 surface #11); required check restricted to the expected source application (mechanism verified + FACT entry — not assumed from docs). Two-stage: rules land now, required-check binding when CI runs.
- **W-02 Host contract + bridges (host-agnostic since D-026, 2026-10-14; Q1 closed by D-028 — agent-agnostic by design)**: the wall defines the **Host Contract** (what any supported host must load — the canonical read order; GLOSSARY) and the **bridge pattern** (a host bridge imports `AGENTS.md`, never duplicates it — one fact, one home). GLM-host verification is behavioral: fresh-context sub-agent proofs (session 13: authority-conflict PASS, unresolved-decision PASS — a fresh session loads canonical instructions and navigates them under pressure). File-import bridges (e.g. `CLAUDE.md` for Claude Code, Codex CLI's `AGENTS.md` conventions) land at host adoption with FACT entries verified on installed versions — instantiation at adoption, never a wall or a phase (INT-097/D-028).
- **W-03 Isolation check**: redacted verification that the agent environment exposes no personal secrets — conditions printed, values never.
- **W-04 CI**: Linux runner, `verify` workflow, owner-controlled; remote CI is authoritative (D-009).
Exit (OBSERVED 2026-10-14, session 13): a broken build cannot merge (probe PR #7: VER-802 red run 115684453018 + merge API 405 "Required status check \"canonical-layer\" is failing\""); a fresh host session loads canonical instructions (verified — GLM-host behavioral proofs, session 13 §6; file-import hosts at adoption); the sandbox is proven secret-free (isolation green, re-run 2026-10-14); verify runs green on a trivial truth (PR #6: both jobs green); a deliberately broken build fails the gate (probe PR #7, observed). Phase 1 is COMPLETE — Phase 2 begins.

**Layer 1.3 (2026-10-14, owner turn 13 — INT-118/D-034; GRADUATED 2026-10-15 by owner turn 14's resequenced gate, D-035: Slices 10/11 landed (PRs #21/#22, 11B 96/100); the candidate-tool gate repaired (PRs #24/#25 — the coordinated-weakening floors, both CI jobs required); the integrated fresh-context proof at the final content SHA passed 96/100 — the seven-part evidence table, record 17 §4.3): the final two slices + the graduation gate.** The owner-forwarded Arivoo review extends Phase 1 once more before any Phase 2 work: **Slice 10 — isolation and diagnostics** (permission-boundary inspection: mechanically prevented vs. detected vs. agent-discipline; the isolation check's false-green classes repaired — embedded remote-credential becomes a failure; mode-required config; end-to-end redaction proof; full negative+positive synthetic matrix) and **Slice 11 — real host bridges and automated gates** (one canonical instruction source; bridges only for hosts in use; the base-anchored isolation checker runs in `canonical-layer`; a fresh-context real-host bounded-task proof with handoff). Then the **Phase-1 graduation gate**: one integrated fresh-context proof on the actual final main SHA — protected PR workflow confirmed, authority recovered from the entry point, state found without a full reread, usable handoff, checker rejects known-bads, isolation gate independently anchored, a fresh agent completes authorized work with evidence. **Phase 2 stays blocked until both slices pass and the graduation gate is satisfied** (the review's words, record 16 §1). Phase 2 = the minimum trustworthy harness/build loop; Phase 3 keeps the name "first real behavior" — the phase boundary is never confused by naming.

**Layer 1.2 (2026-10-14, owner turn 10 — INT-100/D-027):** the exit evidence above remains observed and standing; the owner extended Phase 1 with one more layer — slice 4 (the STATE five-area contract), slice 5 (session handoffs: event-typed worklog/session-record policy + standardized fields), slice 6 (the selective read path + the bounded cold-start proof), plus the replication kit (INT-108). The layers execute in order, each with its own proofs; each is planned as it executes. Phase 1 (layer 1.2 included) completes when the slices' pass criteria hold; Phase 2 still begins only with the owner-approved execution plan. Layer 1.3 (above) supersedes the "Phase 2 still begins" sequencing for the current arc: the turn-13 slices and the graduation gate come first.

## Phase 2 — Minimum trustworthy harness (LANDED 2026-10-16, session 18: owner turn 16, INT-121/D-036 — the 2026-10-16 review's S1–S4 with Rider A folded, executed as PRs #28–#32; the exit criteria below OBSERVED MET via CI at every merge, the uncoached fresh-context clean-clone re-run, and the harness wall probe; evidence: record 18 §4/§7/§12)
One real-stack test · Proof Sheet generated from run records · scope enforcement · representative known-bads for the proactive set only. NOT required before product code: the full constraint system, all architecture checks, every kernel primitive, every planned known-bad.
**Layer 2.1 (LANDED, D-036 — PR #28: S1 real-stack rig + migrations v0 (forward-only, versioned, baseline; Postgres per D-032; a CI service container; a version-parity FACT) · PR #29: S2 the substrate-convention table (owner/actor/provenance/revision/tombstone; append-only triggers with named codes; RLS; a second read role for independent reads) · PR #30: S3 the idempotent command path + crash-injection tooling (command registry; idempotency key; single transaction; ack strictly after commit; kill-at-each-point recovery) · PR #31+#32: S4 the gate assembly, split into two bounded slices by its own SIZE check (Proof Sheet generated from run records, never hand-edited; SIZE/SCOPE enforcement; the proactive-set known-bads — scope breach, protected-path edit, skipped test, hand-written Proof Sheet, lowered threshold, missing red record, test edited after red, unapproved dependency; every failure with a named code; the harness CI job constructed with evidence and bound after a green run is observed — the W-01 stage-2 pattern, executed: required checks = [canonical-layer, head-tools, harness]; the wall probe PR #33 observed the named-code RED + the merge refusal).** Grounded defaults (D-036, each overridable): Python standard library only (zero third-party dependencies); `psql` as the DB client — the app path and the independent verifier differ by role and code path (LAW-13's spirit); test-rig trust auth (ephemeral test databases only). S5/S6 spikes stay owner-gated (Q7/Q8; the review's Riders B stay [P]).
Exit: the harness proves scope, evidence immutability, idempotency, and independent reads on a real database; deliberately broken builds fail with named codes.

## Phase 2 close-out and Phase 3 entry controls

**Phase 2 S1–S4 remains COMPLETE (D-036, session 18). Do not rebuild it or rewrite its evidence.** The current state is documented in STATE.md and record 18. Before product implementation, run the current-SHA preflight below. If a check fails, create one defect slice and repair only that defect. Do not reinterpret the Phase 2 exit or launch a broad harness rewrite.

### P2-CLOSE — current-SHA preflight

At the exact main SHA from which implementation will branch, record the SHA and working-tree state, then run these commands in the intended build environment:

1. python3 tools/verify_canonical_layer.py
2. python3 tools/verify_selftest.py
3. python3 tools/isolation_check.py
4. python3 tools/isolation_selftest.py
5. make harness-health
6. make verify-schema
7. make harness-tests
8. make known-bad
9. make gate
10. make verify

The local database must be the real PostgreSQL rig, not a mock. Do not print environment variables or secrets. Save the actual command, exit status, revision, and material result in the slice run record. Run remote required checks on the same proposed revision. A green remote run at an earlier SHA is historical evidence, not proof that a future PR or new local environment is green.

The current Makefile does not provide the real-run or falsify targets described in parts of the operating-model target surface. Do not claim either target ran until it exists and has actually run. Implement any missing command through a bounded card with red-first tests.

### H-01 — base-anchored harness floor

**Reason:** record 18 §9 identifies a residual: the base-anchored floor for harness tools themselves is not yet proven. Do not reopen Phase 2 S1–S4. Add a single bounded wall-construction slice that tests the candidate harness against a trusted base-controlled floor.

**Scope:** the trusted runner, required assertions, and expected failure classes come from the base revision. Candidate tests may add coverage but cannot replace the base floor. Missing trusted files must fail closed; never silently fall back to a candidate version. Bind any new required check only after a green real pull-request run has been observed, using the recorded W-01 stage-2 procedure.

**Tests to commit first and observe RED:** candidate gate bypass/always-pass; removal or skip of a declared suite; coordinated weakening of the gate and its candidate tests; absence of a trusted base file; a known-bad mutation that changes behavior but would otherwise pass. Every refusal must have a stable reason code.

**Acceptance:** all attacks are rejected by the trusted floor in CI; the positive path is green; the new check is observed in the real PR workflow; a separate fresh-context verifier reproduces the attacks; the Proof Sheet records base/head SHAs, outputs, and not-verified items.

**Security boundary:** do not claim workflow-tamper protection is fully mechanical while Q10 remains open. A PR that can change the workflow definition can alter which steps run. Q10 remains an owner-controlled token/permission decision; this plan does not mint tokens or change credentials.

**Limits:** one behavior, current LAW-05 size limits, zero unapproved dependencies. If the slice exceeds its limit, split it without weakening the limit. Stop after three failed cycles (LAW-16).

### H-02 — systems-engineering verification record and gate

**Purpose:** implement the owner's requirement that each slice receive a systems-engineering review after implementation and independent test verification, before merge.

**Design:** add a standard-library validator and a separately authored Systems Engineering Verification (SEV) record. The record is bound to the reviewed diff using a digest that excludes the SEV file and generated Proof Sheet, avoiding a self-referential commit hash. Required fields: slice ID, base SHA, reviewed-diff digest, owner intent IDs, system requirement IDs, affected C1–C5 claims, changed components/interfaces, component/integration/system/validation proof IDs, failure modes and controls, known-bad evidence, findings/dispositions, not-verified items, builder and reviewer context identifiers, and PASS/BLOCKED disposition.

**Gate behavior:** after H-02 is implemented, the harness must reject a missing, stale, malformed, incomplete, or BLOCKED SEV report. Known-bads must prove refusals for a missing report, stale digest, missing requirement trace, and a P0/P1 finding falsely marked PASS. The base-anchored floor from H-01 must test the SEV validator and gate path.

**Independence limit:** a field naming the reviewer context does not cryptographically prove that it is separate from the builder. The execution protocol must use a fresh context; a separate grader checks the SEV at phase gates. Report identity limitations honestly.

**Acceptance:** the report is required by the gate; every known-bad fails with its named code; the report digest matches the reviewed diff; a fresh-context SEV reviewer who did not implement the slice independently traces requirements to code and evidence; CI blocks missing or rejected reports. LAW-30 remains PLANNED until H-02 and its known-bads are green in CI.

## Phase 3 — Durable capture (first real product behavior)

**Entry condition:** this owner turn opens the Phase 3 execution path. Product-schema migrations begin only after the execution plan is explicitly accepted through the repository change process, P2-CLOSE is green, and H-01/H-02 are installed and proven. Phase 2 S1–S4 stays complete. H-01/H-02 are two bounded closure slices, not permission for an indefinite infrastructure phase.

### A. System requirements

The following SYS identifiers are traceability keys for the product plan, not permission for an agent to change the North Star. Every implementation card cites no more than the existing LAW-05 maximum of three requirement IDs. A requirement change follows the canonical decision/change process.

| ID | Required property | North Star claim |
|---|---|---|
| SYS-01 | Every acknowledged capture is committed at a named durability rung; acknowledgment never overstates persistence. | C1 |
| SYS-02 | Authoritative evidence is immutable after commit; revisions preserve history; deletion uses tombstones except for governed purge. | C1, C5 |
| SYS-03 | Every write has owner scope, actor, stable identity, and required provenance; cross-owner access is rejected. | C1, C2, C5 |
| SYS-04 | A command is atomic and idempotent; same key/body replays the same result; same key/different body is rejected. | C1 |
| SYS-05 | Every Highlight has a stable identity and Anchor tied to a specific Source version; reprocessing cannot silently move it. | C1, C5 |
| SYS-06 | Import/extraction failures are explicit and recoverable; partial imports are never presented as complete; capture does not depend on enrichment. | C1 |
| SYS-07 | Derived passages and indexes are rebuildable and carry processing/input provenance; no unique authored content exists only in derived state. | C1, C3, C5 |
| SYS-08 | Local writes and cloud sync have explicit states, idempotent replay, and crash recovery. | C1 |
| SYS-09 | The supported initial client path can create and retrieve a capture through the real backend boundary. | C1, C2 |
| SYS-10 | Export/restore preserves authoritative data, revision history, and governed purge state without silent loss or resurrection. | C1, C5 |
| SYS-11 | Each implementation slice closes a V-model trace and has independent systems-engineering verification before merge. | C1–C5 |

### B. Proposed system architecture

The architecture below is a proposed implementation baseline. Higher-authority owner words, North Star, locked decisions, and laws govern if there is any conflict. A discrepancy becomes a Question Record, not an agent-chosen compromise.

**Authority versus derivation**

- Authoritative: logical Work identity; imported Source identity/version and acquisition metadata; committed Highlight, Bookmark, Note, and later Journal content/revisions; attribution and command history required to explain writes and recovery.
- Derived: extracted passages, keyword index, embeddings, relationship candidates, concept links/status, rankings, and context packs. Every derived generation has processing/configuration/input lineage and can be discarded and rebuilt.
- A current view can be a projection but cannot be the only remaining copy of authored history.
- Byte-level blob deduplication may reuse identical bytes; it must not merge logical Works or Sources. No semantic auto-merge.

**Minimum domain concepts**

- Work: logical library item.
- Source: a particular imported source version/edition/acquisition instance, as defined in GLOSSARY; not an extraction run.
- Passage: versioned extraction output with its Source version and parser/extractor provenance.
- Highlight: stable capture identity, immutable revisions, selected content, and an Anchor tied to one Source version.
- Bookmark: stable saved location/Anchor, not a copy of the Source.
- Note: owner-authored thinking with immutable revisions and explicit references to relevant Work/Source/Anchor/Highlight/Note.
- Command log/outbox: idempotency and recovery record for accepted mutations and synchronization.
- Journal blocks and stable @-references remain Phase 4. Vector/semantic retrieval, grounded relationship evidence, concepts, and Kev policy/evaluation behavior remain Phase 5. Phase 3 must not implement those complex behaviors prematurely, but must not foreclose them.

**Open identity gate — Q11**

The 2026-10-16 review assumes a repeated identical-file import resolves to the same Work. The known owner preference in prior context is the opposite safety posture: separate logical imports by default, optional duplicate detection. That preference is not yet represented as a verbatim owner-intent entry in the canonical ledger. Until formalized:
- Never automatically merge Works or Sources.
- Do not create uniqueness constraints based on filename, title, or semantic similarity.
- Duplicate detection, if present as a proposal, must leave existing objects unchanged.
- Physical blob reuse may be independent of logical identity.
- Q11 blocks auto-dedup/merge and identity-specific uniqueness constraints only. Other kernel and capture work may continue.

**Anchor contract**

An Anchor identifies a Source version and contains enough format-specific location evidence to re-find the passage. Carry parser/extractor version and fallback matching evidence. Page number or character offset alone is not assumed stable across editions, reflow, re-extraction, or file changes. Run the bounded anchor-stability spike before freezing the schema. Q8's current default remains synthetic documents unless the owner changes it at its named gate; do not claim real-document stability without measurement. Record measured outcomes before deciding thresholds.

**Write, extraction, sync, and index states**

1. Stage source bytes in isolated storage and verify a content digest.
2. Through an idempotent command, persist Source metadata and import-job/outbox state atomically in PostgreSQL.
3. Produce a versioned extraction generation. Publish only when complete; a crash leaves an old valid generation or an explicit failed/retryable state, not a partially ready import.
4. Commit a Highlight/Bookmark/Note mutation with its idempotency record in one database transaction. Acknowledge only after commit.
5. Update keyword search through a distinct, rebuildable derived path. Index failure never loses or hides authoritative capture; it reports lag/failure.
6. Sync local outbox records to Supabase through the same command kernel. Network delivery may occur more than once; idempotency prevents duplicate logical effects. Server-durable status follows verified server acknowledgment.
7. Distinguish local-durable, server-durable, keyword-searchable, semantically indexed, and linked. Every retry uses recorded state, not model memory.

**Storage boundary:** PostgreSQL and object/blob storage do not share one transaction. Do not claim cross-service atomicity. Use staged content-digested blobs; only commit Source metadata that references a verified durable blob; track unfinished imports; recover or clean orphaned staging objects under a tested policy. If the selected host cannot satisfy the contract, open a blocker instead of inventing weaker semantics.

**Minimum kernel only**

Build only what the first real slice needs:
- validated owner scope and actor vocabulary;
- stable typed IDs through the existing ID adapter;
- time through the existing clock adapter;
- provenance/run metadata for evidence and derived output;
- one command registry with transaction/idempotency/ack-after-commit;
- repository/transaction boundaries that keep product modules away from direct DB connections;
- immutable revision/tombstone primitives and standard named errors;
- one canonical source for closed vocabularies as required by LAW-25.

Only adapters may access ambient time, randomness/ID generation, and environment. New code uses the kernel; no second path for the same concern (LAW-10/24). Do not build a generic framework before a real slice proves the need.

### C. Ordered bounded product slices

Every slice gets its own branch/PR, one behavior, pre-registered acceptance tests, a declared file scope, current LAW-05 limits, no unapproved dependency, actual real-stack run, independent state reads, Proof Sheet, independent test verification, and SEV verification. If a slice exceeds size limits, split it; never relax the limit. Stop after three failed cycles.

**P3-00 — Requirements, interfaces, and schema freeze**
- Trace SYS-01–SYS-11 to owning component, interface, tests, C1–C5 claims, and user validation scenario.
- Draw data-lifecycle and state machines for import; capture; revision/tombstone; local outbox; server sync; indexing; export/restore.
- Specify authoritative entities, IDs, ownership, actor, revisions, provenance, transaction boundaries, migration plan, kernel interfaces, and failure behavior.
- Q11 and Q8 must remain visible at their named scopes; other owner decisions block only the dependent work.
- Acceptance: no contradictory source-of-truth rule; every requirement has tests and proof paths; unresolved dependencies have exact boundaries; independent SEV finds no P0/P1. No product schema migration until this gate is accepted.

**P3-01 — Kernel and first real command**
- Create only the kernel contracts needed by the next capture operation and one real command.
- Tests first: missing owner/actor/provenance; same key/body replay; same key/different body; crash before commit; crash after commit before acknowledgment; direct DB access; ambient time/ID use outside adapters.
- Acceptance: atomic, idempotent, attributed behavior, stable named failures, and independent database observation.

**P3-02 — Work and Source intake**
- Implement the resolved identity policy with a minimal supported readable-text/Markdown path, source digest, media type, acquisition metadata, owner/actor, and explicit import state.
- Separate logical identity from byte deduplication. No title/filename/semantic auto-merge.
- Tests: identical bytes imported twice; two similar but different works; retries; failure after staging; failure before metadata commit; missing blob; owner isolation; restart and restore of unfinished import.
- Acceptance: behavior follows ratified identity policy; all partial states are failed/retryable, never falsely complete.

**P3-03 — Extraction generation and Anchor**
- Derive versioned passages and Anchors; source and authored state stay separate from derived passages.
- Run the bounded anchor-stability spike before freezing format-specific location behavior.
- Tests: invalid/empty input, encoding boundary, passage boundary, extraction crash, cosmetic re-save/re-extraction, new edition, source hash mismatch, wrong-source anchor.
- Acceptance: complete-or-failed generation; Anchor never crosses Source versions silently; limitations remain explicit.

**P3-04 — Highlight and immutable revisions**
- Add stable Highlight identity plus append-only revisions carrying selected content, Anchor, Source reference, owner/actor, input digest, and command provenance.
- Reject missing/dangling Anchor and cross-owner Source. Preserve prior revisions; tombstone hides from normal retrieval while retaining governed history.
- Tests: mutation rejection; dangling references; owner isolation; retry; crash at each transactional boundary; source re-import/re-extraction; tombstone/restore.
- Acceptance: independent read sees correct history; current view rebuildable; acknowledgment states actual durability rung.

**P3-05 — Bookmark**
- Represent Bookmark as stable identity and location/Anchor; do not duplicate source text. Define source-version-change behavior.
- Tests: invalid Anchor, cross-owner access, re-import, re-extraction, tombstone/restore, replay and restart.
- Acceptance: return to saved location or report a typed unresolved-anchor state; never silently retarget.

**P3-06 — Note and revision history**
- Persist deep owner-authored Notes with immutable revisions and explicit links. Support diagrams only after their serialization and round-trip format is defined.
- Tests: revisions do not overwrite history; duplicate retries; competing revisions; dangling refs; owner boundary; crash/restart; export/restore.
- Acceptance: every revision is retrievable, attributable, and referenceable; conflict never silently destroys a revision or claims an untested merge.

**P3-07 — Keyword findability**
- Build a rebuildable keyword index for committed sources/passages/captures/notes within the currently supported formats.
- Tests: indexing failure; delete/rebuild; stale entry after revision; tombstone filtering; owner filter; encoding/tokenization boundaries; known query.
- Acceptance: captures become searchable under a defined contract or explicitly report indexing lag/failure; rebuilding restores expected results.

**P3-08 — Local outbox, Supabase sync, and recovery**
- Persist local mutation plus client-outbox intent atomically; apply remote writes through the same kernel; add the server outbox handoff required for future enrichment per D-018/D-032.
- Define ordering, replay, retry and conflict semantics. Do not silently use last-write-wins for authored content. Preserve concurrent immutable revisions; the current view rule must be explicit. No owner review queue or model decision is allowed to block pipeline progress.
- Tests: offline capture; restart before sync; retry after uncertain acknowledgment; duplicate server delivery; out-of-order delivery; server outage; remote/local mismatch; cross-owner sync; process death around outbox acknowledgment.
- Acceptance: each committed local write is either server-durable or explicitly queued/retryable; no lost committed writes or duplicate logical effects; independently read remote state.

**P3-09 — Export/restore and integrated durable-capture proof**
- Define versioned export/restore for authoritative records, source/blob references, revisions, and required purge/retention state. Rebuild derived indexes after restore.
- Tests: export to clean destination, restore, canonical state hash comparison, repeated restore, missing blob, malformed archive, interrupted restore, purge then restore, rebuild corrupt index.
- Acceptance: defined authoritative-state equality holds; a purge cannot be resurrected by restore; errors are explicit/retryable; independent verification uses a separate role/path. This explicitly closes the export/restore gap raised in the 2026-10-16 review.

### D. Mandatory V-model systems-engineering verification after each slice

After implementation tests and an independent test verifier are green, a separate fresh-context Systems Engineering Verifier (SEV) reviews the slice card, reviewed diff, and Proof Sheet only:

1. Trace every changed behavior to owner-intent IDs, approved SYS requirements, and acceptance criteria.
2. Confirm source-of-truth ownership, component responsibility, interfaces, dependency direction, and no second kernel/adapter path.
3. Review failure modes relevant to the change: data loss, stale/wrong anchors, owner leakage, duplicate side effects, stale derived data, crash/restart, sync, provenance loss, and restore/purge behavior.
4. Close the V-model level actually claimed: component proof, real integration-boundary proof, full affected system path, and named user validation. A lower-level green check is not system-level proof.
5. Inspect red-first evidence, real-stack transcript, independent state read, fault/property/mutation results, known-bads, regression coverage and failures.
6. Inspect migration compatibility, security/privacy boundary, dependency changes, protected paths, downstream layer impact, and reversible recovery.
7. Verify evidence provenance, reviewed-diff digest, actual commands/revisions, dispositions, and explicit not-verified list.
8. P0/P1 or a blocking owner question means STOP. P2 is not automatically accepted debt; it requires an owner-approved record with reason and revisit condition.
9. The SEV reviewer did not implement the slice. At phase gates, a separate grader checks the SEV. Context labels alone do not cryptographically prove independence; report this limitation honestly.
10. The owner reviews the Proof Sheet and SEV disposition. Green CI permits review of a merge; the agent cannot resolve owner decisions, change laws, or merge its own review/proposal.

The standard form lives in context/TEMPLATES.md; policy lives in OPERATING-MODEL.md and LAW-30. Once H-02 is live, a missing, stale, incomplete, or BLOCKED report fails the gate.

### E. Phase 3 exit criteria

Phase 3 exits only when all claims are proven on the final main revision:
- Work/Source identity and Anchor contracts are explicit, and owner blockers stay resolved or isolated at their exact scopes.
- A real client/backend path ingests supported input, creates a Highlight with valid Anchor, Bookmark and Note, then finds them via keyword search.
- Accepted captures survive defined crash/restart/replay/offline fault matrices with zero lost committed writes and no duplicate logical effects.
- Local-durable and server-durable are distinct; sync has explicit recoverable outbox states.
- Every write is attributed and owner-scoped; two-owner tests and independent reads pass.
- Revisions are immutable, tombstones work, and a governed purge remains effective after restore.
- Derived passages/indexes rebuild without losing authored state; stale derivations cannot silently appear current.
- Export/restore satisfies the documented equality contract.
- Every SYS requirement traces to tests and Proof Sheet evidence; every slice has passing SEV; all known-bads are refused with named codes.
- Local checks and the three recorded required CI checks pass at final revision; an uncoached clean-clone task agent completes the real user-like acceptance path, and a separate grader passes it with no P0/P1.
- Not-verified items remain explicit. A successful PR or elapsed time is not phase-exit proof.

### F. Boundaries and stop conditions

No reader UI is built in this repository. Phase 4 covers the complete reader/journal/@-reference workflow. Phase 5 covers semantic/vector retrieval, relationships, concept graduation and Kev policy/evaluations. Their schemas must remain compatible, but their advanced behavior must not be pulled into Phase 3.

P-17 applies: H-01 and H-02 are the only new general infrastructure closure slices. Once both are green, start P3-00/P3-01 immediately. No third generic infrastructure phase. A concrete product defect can justify a new guard under the ratchet; speculative future hardening cannot delay durable capture.

## Phase 4 — Reader and journal path (first usable milestone, D-013, D-023)
Open PDF/EPUB → highlight → bookmark → margin notes → durable journal blocks → stable `@` references — **plus the first import path: any readable format (INT-113/D-031, 2026-10-14 — pdf/txt/md/epub/json and every readable format; INT-019 day-one intake; books/articles per the durability ladder)**. Each behavior gets its own small card and verified result.
Exit: the owner's day-one workflow (import → read → capture → note → journal with references) runs end-to-end on the real stack, proven through a real client path with a documented integration boundary to the reader/journal clients (the UI itself is outside this repo).

## Phase 5 — Retrieval and compounding
Keyword lookup → agent reads (API/MCP surface per D-019) → semantic indexing + vector retrieval → relationship candidates → concept formation → Kev policy/eval gates. Compounding probes tested separately: deterministic → semantic → graph.
**Pre-Phase-5 gate (owner turn 13 disposition, D-034): the classification-words rule must be made explicit before Phase 5 begins** — ordinary user text is processed as text; classification words ("concept", "fact", "quote") receive no special tagging behavior or dedicated weighting unless the owner decides otherwise (D-030's removal carried to its semantic conclusion); VER-211/MUT-11 are rewritten then to enforce the clarified rule, not the older tag-feature wording (record 16 §1, the review's P2 disposition).
Exit: C3 demonstrable with reasons and provenance — new inputs resurface old material; automatic relations add value without violating evidence rules.

## Standing open (owner)
- D-014 — calculation engine: open, non-blocking for capture (owner reaffirmed 2026-10-14, INT-114).
- Q6 — research-transcript status (2026-10-16 review §8 Q1; adopt vs reference doctrine) — blocks Part-2 acceptance-scenario finalization + the S5 corpus only.
- Q7 — semantic-spike budget for S6 (review §8 Q2) — blocks S6 only.
- Q8 — extraction-spike documents for S5 (review §8 Q3) — blocks S5's corpus only.
- Q9 — repository visibility (review §8 Q4; observed public 2026-10-16) — blocks nothing; privacy-relevant.
- Q10 — fine-grained PAT hardening (review §8 Q5, from F-7) — blocks F-7's mechanical fix only.

Registered 2026-10-16 (session 18, D-036); entered from the 2026-10-16 review's §8 owner questions. S1–S4 proceed regardless of Q6–Q10 (each blocks only its named dependents, F-07).

Closed 2026-10-14 (owner turn 12, INT-110..INT-117; LOCKED rows D-028..D-033 in DECISIONS): Q1, Q2, Q3, QD-1, F-06, Q-IDENT.

The List is the refinement-debt register (D-020) — cloud sync (L-001) is its live entry; semantic search, pgvector, and vector search are in the active sequence (Phase 5), never on the register. Deployment (D-032): Supabase-hosted, cloud + local synced.

## Supersession note
The F-00..F-09 foundation-slice order from the original execution spec is SUPERSEDED by this phase sequence (D-016; reconciliation brief R-02/R-10). The slice cycle, size limits, proof discipline, and laws carry over unchanged into the new phases — now codified at root: LAWS.md (the 29 laws, phase-mapped) and ENGINEERING.md (the doctrine). The execution contract's canonical home is `/EXECUTION.md` (created by the canonicalization slice, 2026-10-13, D-021): the 12 spec deltas staged in `context/extracted/08-RECONCILIATION-BRIEF.md` are folded into the root layer or closed by owner decision — Q1–Q3 closed 2026-10-14 by D-028/D-029/D-030 (the earlier "explicitly owner-gated (Q1–Q3)" wording is superseded: no open question remains among them) — nothing waits on a further agent-side rewrite.

## Post-product comprehensive refinement pass (P-18, INT-094/INT-096 — named, not scheduled)

Once the end-to-end product exists (Phase 4+ exit evidence), ONE comprehensive refinement pass across the Intent Ledger, decisions, principles, laws, North Star, architecture, and future vision — judged against implementation evidence: which assumptions survived contact with reality, which decisions were superseded, which capabilities were actually delivered, what the next version should become. History stays intact throughout: refinement clarifies the current direction and marks supersessions (append-only, `superseded_by`), never rewrites to pretend the answer was always known. Until that gate: capture continuously, correct only what can mislead current work, leave unrelated editorial debt for the pass (P-18, D-026).

## Growth-model mapping (how this plan grows the repo)
Phase 1 → operating Model 1 (trust environment) · Phase 2 → Model 2 (build loop: harness core, builders, verifier) · Phase 3 → Models 2→3 (substrate laws live; enforced architecture begins) · foundation exit → Model 3 stable · Phases 4–5 → Model 4 (evidence-driven) · post-foundation recurring agents → Model 5 (self-maintaining) · harness evals → Model 6 (self-improving). Each model's full specification (who runs, what's enforced, how memory updates, how failures heal, graduation predicate): OPERATING-MODEL.md §6.
