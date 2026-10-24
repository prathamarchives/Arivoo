# ARIVOO — Systems-engineering roadmap, Phase 3 through Phase 5, 24 October 2026

> STATUS: REVIEW-ONLY / PLANNING ARTIFACT — 2026-10-24. Owner-requested (owner turn 32; preservation home:
> session record 32 §1; ledger ref INT-137). Per D-022 this file is a planning artifact derived from the
> canonical sources (NORTH-STAR.md, PLAN.md, DECISIONS.md, EXECUTION.md, ENGINEERING.md, OPERATING-MODEL.md,
> LAWS.md, GLOSSARY.md, AGENTS.md, STATE.md, session records 29–31, PRs #71–#73, CI run #39989587479),
> never owner intent: the owner's own words for this turn live in INTENT-LEDGER.md (INT-137) and record 32 §1.
> Its P3→P5 details are engineering elaborations — nothing in it is adopted until P3-00 accepts it through
> the repository process. The artifact was generated as a 25-page PDF and delivered to the owner as
> `arivoo_p3_to_p5_systems_engineering_roadmap_2026-10-24.pdf`; the text below is that PDF's verbatim text
> content (extraction page markers and the PDF's repeated running headers removed; no other change).
> Status labels in the text (CANONICAL / ENGINEERING ELABORATION / OWNER GATE / NOT VERIFIED) are preserved
> exactly as delivered.

---

ARIVOO
Systems-Engineering
Roadmap
From durable capture to context-compounding intelligence
Phase 3 → Phase 4 → Phase 5
A requirements-led architecture, implementation sequence, verification strategy, and final-goal acceptance model.
Prepared from the live Arivoo repository and the current owner-approved roadmap
24 October 2026
Scope: backend and systems engineering. The reader/journal UI is built separately and must be exercised through the real 
API.
A working specification, not a claim of finished implementation.
Reading guide and document status
This document turns the canonical Arivoo North Star and PLAN.md into a systems-engineering execution and 
acceptance model. It preserves the repository’s terms and phase boundaries, expands their engineering consequences, 
and distinguishes what is already evidenced from what is still proposed, blocked, or not verified.
Label Meaning How to use it
CANONICAL / AUTHORITY
A fact or rule already present in the owner 
intent, North Star, canonical plan, decisions, 
laws, or operating model.
Do not overwrite through interpretation. If 
contradictory, use the canonical authority 
order and record a question.
ENGINEERING ELABORATION
A concrete test, interface, failure case, or 
acceptance detail derived from canonical 
goals.
Use as a recommendation or 
implementation criterion; adopt through the 
repo change process where required.
OWNER GATE An unresolved choice that belongs to the 
owner.
Continue independent work. Do not silently 
choose a value or claim acceptance.
NOT VERIFIED No sufficient direct evidence was available 
for the claim in this review.
Keep visible in the session record and proof 
sheet until actually verified.
Critical status distinction  PR #73 merged and its five CI checks passed. That closes the H-01c slices, not H-02, 
not P3-00, and not Phase 3 entry. This roadmap describes what must be demonstrated, not what the repository 
already implements.
Contents
 1. Executive determination and live baseline
 2. The product promise: North Star and measurable claims
 3. Architecture map and state-of-truth rules
 4. Reliability principles that cannot be traded away
 5. Before Phase 3: required entry sequence
 6. Phase 3 — durable capture
 7. P3 system requirements and traceability
 8. Phase 3 integrated exit gate
 9. Phase 4 — reader, journal, and first usable experience
 10. Phase 4 integration contracts and seven refinement rounds
 11. Phase 5 — retrieval, relationships, concepts, and compounding
 12. Phase 5 evaluation and promotion gates
 13. Final-goal acceptance matrix
 14. Open owner decisions and non-inferred choices
 15. Failure modes, anti-patterns, and review checklist
 16. Execution protocol and phase-gate evidence
 17. What “done” means for Arivoo
Canonical source anchors: NORTH-STAR.md; PLAN.md; DECISIONS.md; EXECUTION.md; ENGINEERING.md; OPERATING-MODEL.md; 
LAWS.md; GLOSSARY.md; AGENTS.md; STATE.md; session records 29–31; PRs #71–#73; CI run #39989587479.
1. Executive determination and live baseline
1.1 Verified state at review time
Item Observed fact Interpretation
Main revision 3dfa855013158622309c3e1593b51f92eb9a631c Live main at the end of PR #73.
H-01c-authority PR #71 merged
Trusted-base raw/manifest linkage and quote-
extraction controls landed; mutation 
regressions added.
H-01c-evidence/privacy part 1 PR #72 merged
Trusted-baseline RED control, typed red 
records, fail-closed suite registration, atomic 
single-writer red write.
H-01c-evidence/privacy part 2 PR #73 merged Proof-record numbering, canary masking and 
narrowed scope-lint claims updated.
Main CI Run #39989587479: success
All five named jobs passed: canonical-layer, 
head-tools, harness, harness-suites, harness-
trusted.
H-02 SEV gate Not built in the inspected canonical plan/status Still required before product Phase 3 schema 
migrations.
P3-00 RTM/schema freeze Not built/accepted in current state Still required after H-02 and before P3-M0/P3-
K0 and product schema migrations.
Navigation state STATE.md and AGENTS.md lag the merge Current-state text must be reconciled; stale text 
is not proof of outstanding PR work.
Residual PR #73 record routes N12 self-test-row 
integration / canary-position extension
Not silently complete. Keep the stated limitation 
visible and assess against H-02/SEV scope.
Sources: PR #71 https://github.com/prathamarchives/Arivoo/pull/71 ; PR #72 https://github.com/prathamarchives/Arivoo/pull/72 ; PR 
#73 https://github.com/prathamarchives/Arivoo/pull/73 ; post-merge CI 
https://github.com/prathamarchives/Arivoo/actions/runs/39989587479.
Current decision  Continue with H-02 as the next bounded engineering slice. Do not return to generalized pre-
build hardening; do not start product schema migrations until H-02 passes its activation conditions and P3-00 is 
accepted.
1.2 Verification limits of this review
This review accessed the repository and CI through the GitHub connector. A fresh local clone failed because the 
execution environment could not resolve github.com. Therefore no fresh local make verify was run in this session. 
The remote main CI result above is direct evidence for that revision, but it is not a substitute for the independent P3 
entry review, a fresh local check, a live branch-protection reread, or a completed SEV record.
Repository update limitation: the linked GitHub integration returned HTTP 403 “Resource not accessible by 
integration” when asked to create a branch. That prevented safely publishing the navigation/claim reconciliation 
through a PR in this turn. The stale records are real findings; this document does not pretend they have already been 
changed in main.
2. The product promise: North Star and measurable claims
Arivoo is a persistent reading, research, study, reflection, and reasoning environment—not merely a notes application, 
generic reader, or agent wrapper. The owner can import readable material, read it as a book, capture passages, keep 
substantial raw thinking, journal learning, connect related material, and connect a personal agent that can work with 
the owner’s accumulated context.
Claim Meaning in the intended product Observable acceptance evidence
C1 — Nothing the owner does is lost
Authored content and accepted captures 
survive the failures covered by the declared 
durability contract. Acknowledgment names 
the actual durability rung.
Commit/ack fault injection; independent DB 
read; restart; retry; offline/outbox recovery; 
export/restore equality; purge cannot 
resurrect.
C2 — Agents have owner context
Authorized agents can discover and read 
useful owner material through the same 
authorized API as the client, with limits, 
scope and provenance.
Authenticated read tests; two-owner 
isolation; context-pack traceability; 
budget/truncation tests; hostile input cannot 
expand authority.
C3 — Old inputs gain value from new inputs
New material can make previously saved 
material retrievable through deterministic, 
semantic and grounded graph paths.
Three separate probes: deterministic 
alias/relation; held-out semantic resurfacing; 
grounded graph path with false-link 
controls.
C4 — Concepts form from grounded 
evidence
Concept discovery is allowed; promotion to a 
grounded relationship/concept requires 
permitted evidence and policy.
Evidence spans or structural proof; distinct 
source identities; held-out graduation; 
counterexamples; provenance and 
reversible correction history.
C5 — Derived claims explainable and 
reversible
Derived states can be traced to inputs, 
processing version, policy and evidence; the 
owner can correct/recompute without losing 
source history.
Why-payloads; source+revision+anchor 
links; generation lineage; deterministic 
rebuild; merge/split/retraction history; 
purge invalidation.
2.1 Durability is a ladder, not a boolean
Rung Meaning What it must not be confused with
Local-durable Authoritative mutation and its recovery 
intent are committed locally.
“The request was sent” or “the app showed a 
spinner.”
Server-durable Server-side authoritative state is confirmed 
after a durable remote acknowledgment.
Local persistence or a network request that 
timed out after the server may have 
committed.
Keyword-searchable A rebuildable keyword index reflects the 
committed material.
The source of truth; indexing can be delayed 
or rebuilt.
Semantically indexed A versioned embedding/index generation 
exists for a specific source/revision/config.
Evidence that a semantic hit is true or 
relevant.
Linked A relationship/concept path exists under an 
explicit evidence policy.
Similarity or a model-produced string 
promoted silently to fact.
Every user-visible save state must map to one of these contract states or to an explicit 
queued/conflicted/failed/unresolved state. The UI must never infer “saved” from request 
initiation, and the backend must not report a stronger rung than it independently knows.
3. Architecture map and state-of-truth rules
3.1 Seven product layers
Layer Responsibility Invariant to protect
1. Ground truth Authored records, evidence, immutable 
revisions, attribution, deletion/purge rules.
No unique authored state exists only in a 
derived index or model context.
Layer Responsibility Invariant to protect
2. Ingestion
Readable source intake, content 
identity/digest, source versions, extraction 
generations, anchors.
A source, edition, acquisition and extraction 
run are not treated as interchangeable 
identities.
3. Memory index Keyword index first; semantic index later; 
all derived and rebuildable.
Index failure does not destroy content or 
falsely mark it unavailable as authoritative 
data.
4. Structure Explicit references and admissible 
relationships between versioned endpoints.
Evidence rules distinguish structural fact 
from discovery candidate.
5. Concept formation Provisional concepts, stable IDs, aliases, 
corrections, merge/split and graduation.
No automatic claim promotion from 
similarity; provenance survives every status 
change.
6. Agent surface Scoped API, MCP adapter, retrieval/context 
packs, typed errors and budgets.
Agents never write the database directly; 
adapter and API share one command core.
7. Retrieval Keyword/hybrid/temporal/behavioral 
search, “why” payloads, bounded context.
Hits explain why they were returned and 
carry source/version/trust metadata.
3.2 Authoritative versus derived state
Authoritative state includes logical Work identity; Source-version and acquisition metadata; Highlight, Bookmark, 
Note and later Journal content/revisions; attribution; command history and outbox state needed for idempotency, 
recovery, and explaining changes. Derived state includes extracted passages, keyword indexes, embeddings, 
relationship candidates, concept-link/status projections, rankings, and context packs. Derived state must carry 
processing/configuration/input lineage and be disposable/rebuildable.
A “current” view may be a projection, but cannot be the only surviving copy of authored history. Corrections should 
append a new revision or a typed status transition. Deletion follows the adopted tombstone/purge contract; 
restoration must not resurrect purged material or any derived copy that depends on it.
3.3 Domain boundaries
Entity Contract that should survive implementation
Work Logical library item. Identity policy remains unresolved until Q11 is 
ratified; no automatic merge.
Source Particular imported source version/edition/acquisition instance. Not 
an extraction run.
Passage / extraction generation Versioned derived result tied to Source version and parser/extractor 
provenance; publish complete generations only.
Anchor Locates selected text in a specific Source version, with enough 
fallback evidence to detect ambiguity or drift.
Highlight
Stable capture identity and immutable revisions; selected content 
plus explicit Anchor, Source version, owner/actor and command 
lineage.
Bookmark Stable return location/Anchor, not a duplicate of the source content.
Note Deep owner-authored thinking with immutable revisions and 
explicit references; avoid forcing a short sticky-note model.
Journal block / @ reference Phase 4; source-optional journal thought, stable target identity, 
version-aware resolution states.
Command log / outbox Idempotency, recovery, replay, sync progress and explicit 
acknowledgment semantics.
4. Reliability principles that cannot be traded away
Truthful acknowledgment
A command returns success only after the declared commit point. If the client loses the acknowledgment, the result is 
uncertain until replay/query resolves it; the client cannot assume failure or success.
Idempotency is a semantic contract
The same idempotency key with the same canonical request returns the same result. The same key with a different 
effect-bearing request is rejected. Concurrent same-key requests need an explicit result or a typed retryable in-flight 
outcome; a unique constraint alone is not enough.
Provenance travels with claims
Every stored or derived object has stable identity, owner scope, source/version context, actor where relevant, and 
operation/processing lineage. Derived relationships include the evidence and policy/run that authorized promotion.
Revisions do not disappear
Authored changes are append-only revisions or typed transitions. Concurrent edits to authored content do not silently 
resolve via last-write-wins. Competing revisions remain recoverable and the chosen current-view rule is documented.
Anchors fail honestly
If an Anchor cannot be resolved uniquely within the correct Source version, the system marks it 
unresolved/ambiguous. It never silently retargets to a new edition or a semantically similar paragraph.
Derived failures degrade, not corrupt
Keyword/semantic/graph processing can lag or fail without losing captures. Every derived generation declares its 
input version, config/policy and state; stale generations cannot masquerade as current.
Security is owner-scoped at every boundary
Owner authorization applies at the API query/command itself, not merely in the UI. Imported text is untrusted input, 
never instructions. No service key or direct DB bypass in clients or agents.
Recovery is a designed path
Crashes around commit, blob upload, outbox delivery, remote acknowledgment, indexing, restore and purge are test 
cases, not unexpected mysteries. Orphan handling and retry behavior are explicit.
Claims match evidence
A green lower-level test is component evidence, not integrated user-workflow proof. “Supported”, “durable”, 
“semantic”, “grounded” and “complete” each have separate acceptance conditions.
The harness must serve the product
Keep P3-M0/P3-K0 narrowly tied to concrete migration/kernel defects. Add further guards when a real failure exposes 
a missing control, not to pre-build an abstract universal framework.
5. Before Phase 3: required entry sequence
The H-01c merges are necessary preconditions, but the phase plan is explicit: H-02 and P3-00 remain before product 
schema migrations. The following is the current required order, with the reason each gate exists.
Order Slice / gate Scope and acceptance Must not be inferred
1 H-02 — SEV validator and gate
A standard-library validator and 
separate Systems Engineering 
Verification record, with full 
reviewed-diff digest, required 
traces, evidence bindings, 
limitations, findings and 
PASS/BLOCKED. Known-bads call 
the public validator and actual 
gate caller.
A field naming another review 
context does not cryptographically 
establish independent identity. The 
protocol and phase grader must 
compensate honestly.
2
P3-00 — 
requirement/interface/schema 
freeze
One RTM for SYS-01..SYS-11; 
lifecycles/state machines; 
ownership/revisions/provenance; 
API/command contracts; 
transaction and blob boundaries; 
failure cases and traceable 
acceptance tests; exact Q8/Q11/Q12 
boundaries.
No product schema migrations 
before this record is accepted 
through the repository process.
3a P3-M0 — migration oracle
Fail-closed admitted SQL grammar 
or parser; transaction-control 
rejection; zero effects + no ledger 
entry on failure; bidirectional 
migration history; observation-
only verify; safe filenames; 
security schema + data oracles.
Text matching or row counts do 
not prove safe migration or 
recovery.
3b P3-K0 — kernel primitives
Canonical structured/versioned 
request encoding; UUID 
correctness; approved 
DB/config/time/ID adapters; stable 
named errors; concurrent 
idempotency semantics.
Delimiter-concatenated hashes and 
sequential-only tests do not prove 
collision-safe request identity or 
concurrency.
4 P3-01 — first real command
Use the real stack and a real 
domain mutation; tests exercise 
failure before commit and after 
commit/before ack, direct DB 
escape and ambient clock/ID.
Passing the harness by itself is not 
product progress.
5.1 H-02 must be a real gate, not a template ceremony
 The SEV record binds to the exact reviewed base and implementation/test diff by a full validated digest. 
Exclusions are narrowly scoped to generated/self-referential evidence artifacts; code under review cannot be 
excluded.
 Required fields include slice ID, base SHA, diff digest, owner-intent IDs, approved SYS IDs, affected C1-C5 claims, 
changed interfaces, proof levels, failure modes and controls, known-bad results, findings/dispositions, explicit not-
verified items, builder/reviewer context identifiers, and PASS/BLOCKED.
 The gate refuses missing, stale, malformed, incomplete or BLOCKED records; it refuses a nonempty P0/P1 list 
labelled PASS; and it is tested through the actual gate caller, not an internal duplicate validator.
 The H-01b base-anchored floor must be able to judge the validator and gate path. The bootstrap/transition review 
is specifically scoped and independently checked, not a permanent bypass.
 The SEV reviewer has not implemented the slice and operates in a fresh context. The independent grader reviews 
the SEV at phase gates. The record must name the remaining limits of identity/context separation instead of 
calling it cryptographic isolation.
5.2 P3-00 is the contract freeze, not a premature schema guess
P3-00 must connect requirements to component owner, interface, system state, failure mode, tests, proof IDs and final 
user scenario. The diagram should show each authoritative state transition and each derived path separately. The 
owner decision register remains authoritative; a question should block only the named dependent work, not the 
entire phase.
P3-00 acceptance requires: every SYS requirement traced to tests and proof; no contradictory source-of-truth rule; 
explicit transaction/ack semantics; a migration and compatibility plan; data lifecycle for import, revision, tombstone, 
purge, indexing, sync and restore; source/blob boundary; and no unresolved P0/P1 or blocking owner question 
affecting the approved design.
6. Phase 3 — durable capture
Phase 3 is the first real product behavior. Its core is durable, attributable capture and honest recovery. It should 
produce usable behavior incrementally rather than waiting for every planned operation to be finished before running 
the product path.
Phase 3 engineering objective  A real client/backend path can import supported material, maintain a versioned 
Source and stable Anchor, create Highlight/Bookmark/Note, find the committed material with keyword search, 
survive the declared faults, and restore an equivalent authoritative state.
6.1 P3-01 — kernel plus first real command
Build only the primitives the first real command requires. The first command is the vertical proof that owner scope, 
actor, stable ID, clock adapter, canonical request identity, transaction, idempotency, provenance and acknowledgment 
semantics actually compose on the real stack.
 Red-first inputs: missing owner, actor or provenance; invalid scope; key replay with same body; same key with 
different body; malformed/unsupported body; direct database access outside repository/kernel boundary; 
ambient clock/randomness use outside adapters.
 Fault injection: crash before commit; commit succeeds then process dies before acknowledgment; client retries 
after timeout; two concurrent same-key requests; DB connection points at wrong socket/database; connection 
refusal/timeout yields a named no-ack outcome.
 Independent oracle: read authoritative rows and idempotency result through a separate role/path. Do not accept 
only command output, row counts or the same code’s self-reported “PASS”.
P3-02 — Work and Source intake
Objective: Establish the first honest import path without guessing logical identity rules.
Required behavior and contracts
 Choose a minimal readable-text/Markdown intake only after P3-00 freezes the contract. Record content digest, 
media type, acquisition metadata, owner/actor, import state and source/blob link.
 Separate logical identity from byte-level storage reuse. Similar titles, filenames and semantic similarity never 
auto-merge logical Works or Sources under unresolved Q11.
 Treat staging/upload and PostgreSQL metadata as separate failure domains. Verify the blob before a committed 
Source points at it; record recoverable upload/import states and orphan cleanup policy.
Verification focus
 Identical bytes imported twice; similar but distinct documents; repeated request; retry after uncertain 
acknowledgment.
 Crash after staging/before metadata; crash during metadata commit; missing or corrupt blob; unauthorized 
owner; process restart and unfinished import recovery.
Slice acceptance: Every import resolves to a documented state (complete, queued/retryable, or failed); no partial object is described 
as complete and existing logical identity is not silently merged.
P3-03 — Versioned extraction and Anchor
Objective: Derive readable passages and stable, source-version-specific locations.
Required behavior and contracts
 Each extraction generation binds to Source version, extractor/parser version and input digest; publish only a 
complete generation.
 Anchor stores format-appropriate location evidence and fallback matching evidence; page or character offset 
alone is not assumed stable across edition, reflow or re-extraction.
 Begin with synthetic corpus under Q8. Any real PDF/EPUB stability claim requires a named, permitted corpus and 
measured results; OCR/scanned content is a distinct capability.
Verification focus
 Invalid/empty input, encodings, passage boundaries and over-limit files; extraction crash; previous complete 
generation preserved or explicit failed state.
 Cosmetic re-save, re-extraction, changed edition, input hash mismatch and Anchor submitted against the wrong 
Source.
Slice acceptance: Anchor resolves to the intended text within the intended Source version or reports a typed unresolved/ambiguous 
state; no silent re-targeting.
P3-04 — Highlight and immutable revisions
Objective: Make captured thinking/proof a durable authored record.
Required behavior and contracts
 Highlight has stable identity and append-only revisions with selected content, Source version, Anchor, 
owner/actor, command and input provenance.
 Validate owner access, Source/Anchor membership and allowed state transitions inside the command boundary. 
Tombstone hides normal retrieval but preserves governed history.
 Capture cannot depend on semantic enrichment or concept labels; “concept/fact/quote” remains owner-entered 
free text, not a forced tag system.
Verification focus
 Dangling Anchor, wrong Source version, cross-owner reference, replay, concurrent revision, crash around 
commit/ack, re-import/re-extraction and tombstone/restore.
 Independent read verifies full revision history and current-view derivation, not merely the latest text.
Slice acceptance: Each accepted Highlight is independently retrievable, attributed, revision-preserving and acknowledged only at its 
actual durability rung.
P3-05 — Bookmark
Objective: Save a location to return to, without copying the source.
Required behavior and contracts
 Bookmark has stable identity plus source-versioned Anchor/location; source content remains a separate object.
 Define behavior when the Source is re-imported, re-extracted, replaced by a new edition or purged.
Verification focus
 Invalid Anchor; wrong owner; repeated capture; retry; source re-import/re-extract; tombstone, restore, restart 
and replay.
Slice acceptance: Returning to location works when resolvable; otherwise the API returns an explicit unresolved/ambiguous status 
rather than a plausible but wrong location.
P3-06 — Note and revision history
Objective: Preserve long-form owner thinking and explicit evidence references.
Required behavior and contracts
 Note is authored text with stable identity and immutable revisions. References to 
Work/Source/Anchor/Highlight/Note are explicit and version-aware.
 Diagrams and richer structured blocks are not silently represented as lossy text; specify serialization, 
compatibility and round-trip contract before claiming them.
Verification focus
 Revision history, repeated requests, competing edits, dangling references, owner isolation, crash/restart, export 
and restore; no untested last-write-wins.
Slice acceptance: Every revision is attributable and recoverable; referenced objects resolve to defined states; a conflict does not 
destroy one of the authored inputs.
P3-07 — Rebuildable keyword findability
Objective: Make committed material findable without making the index authoritative.
Required behavior and contracts
 Index committed supported Sources/passages/captures/Notes. Index generation carries source version and 
indexing state.
 Index failure is independent from capture success. Search results respect owner scope, tombstones, purge, 
revision state and supported-format limits.
Verification focus
 Index outage; stale terms after revision; tombstone filtering; owner isolation; encoding/tokenization edges; 
deterministic expected queries; full rebuild from authoritative state.
Slice acceptance: A known committed capture is retrievable through the documented keyword contract, or index lag/failure is 
explicit; rebuilding restores a known expected result set.
P3-08 — Local outbox, Supabase sync and recovery
Objective: Keep local and cloud durable states truthful, replayable and non-destructive.
Required behavior and contracts
 Commit local authored mutation and local outbox intent atomically. Remote application uses the same 
command/idempotency kernel.
 Model queued, delivered, acknowledged, retryable, conflicting and failed states. A timeout after possible server 
commit stays uncertain until queried/replayed.
 Never silently use last-write-wins for authored content. Preserve immutable competing revisions and specify 
current-view behavior. Do not claim a transaction spans PostgreSQL and object storage unless proven.
Verification focus
 Offline capture; restart before delivery; duplicate/out-of-order message; uncertain ACK; server outage; 
local/remote mismatch; cross-owner injection; death immediately before/after ACK update.
 Independent remote read; event/revision count and content equality; replay does not duplicate logical effect.
Slice acceptance: Every locally committed write is server-durable or explicitly queued/retryable; no lost committed write and no 
duplicate logical effect across the declared fault matrix.
P3-09 — Versioned export/restore and integrated proof
Objective: Prove that the durable substrate survives migration, restore and derived-state loss.
Required behavior and contracts
 Export authoritative records, blob references, revision history and governed purge/retention state with an explicit 
versioned manifest.
 Restore into a clean destination; validate references and blob availability before declaring completion. Derived 
keyword indexes rebuild from authoritative state.
 Purge rules apply to backup/import/restore and derived copies; restore must not resurrect purged content.
Verification focus
 Clean restore plus canonical authoritative-state hash comparison; repeated restore; missing blob; 
malformed/interrupted archive; corrupt index; purge then restore; migration from a declared prior schema.
 Independent verification path reads content and relevant security schema/ownership constraints, not only row 
counts.
Slice acceptance: Authoritative-state equality holds under a documented comparison rule; derived state is rebuilt; 
partial/malformed restores fail safely; purge remains effective.
7. P3 system requirements and traceability
The SYS IDs are canonical trace keys in PLAN.md. Every implementation slice should cite the small relevant set of 
requirements rather than dumping the whole RTM into every card. The requirements themselves are not permission 
to alter owner intent.
SYS Required property Primary implementation area Minimum proof class
SYS-01 Acknowledgment reflects named 
durability rung.
Command kernel, capture API, 
client contract, outbox.
Fault/timeout replay plus 
independent authoritative read.
SYS-02
Authoritative evidence immutable 
after commit; revisions preserve 
history; tombstones except 
governed purge.
Highlight/Bookmark/Note revision 
state and lifecycle.
Mutation rejection, revision 
history, tombstone/restore/purge 
tests.
SYS-03
Every write owner-scoped, 
attributed, stable identity and 
provenance; cross-owner rejected.
API auth, command registry, all 
write/read paths.
Two-owner matrix, hostile IDs/refs, 
independent read.
SYS-04
Atomic/idempotent; same key/body 
replays; same key/different body 
rejected.
Canonical request encoder and 
command transaction.
Sequential + concurrent replay, 
conflict and crash tests.
SYS-05
Highlight identity and Anchor 
bound to a particular Source 
version.
Source version, extractor and 
Anchor.
Cross-source/new-edition/re-
extraction and ambiguity tests.
SYS-06
Import/extraction failures explicit 
and recoverable; partial import 
never appears complete.
Staging, blob store, import state 
machine, extractor.
Crash/failure injection at each 
durable transition.
SYS-07
Derived passage/index provenance 
and rebuildability; authored state 
never exists only in derived state.
Extraction and keyword index 
generations.
Delete derived state, rebuild, 
compare expected results.
SYS-08 Local/cloud sync explicit, 
idempotent and crash-recoverable.
Local outbox + server 
application/ack.
Offline/replay/uncertain-ACK/out-
of-order tests.
SYS-09
Real supported client path creates 
and retrieves through the real 
backend boundary.
Product API plus external client. Actual API integration test; mock-
only tests are not enough.
SYS Required property Primary implementation area Minimum proof class
SYS-10
Versioned export/restore retains 
authoritative data, revision and 
purge state.
Export manifest, restore validator 
and rebuilders.
Clean restore equality, 
missing/corrupt input, purge 
resurrection.
SYS-11
Each slice closes a V-model trace 
and independent SEV before 
merge.
H-02 gate, Proof Sheet, RTM, 
independent grader.
Public gate-path known-bads and 
diff-bound reviewed report.
7.1 V-model evidence must match the claim level
Evidence level Question answered Example for Highlight
Component Does the unit enforce its local contract? Anchor validator rejects a cross-Source 
Anchor.
Integration Do real component boundaries compose? Real command/API/DB transaction writes 
Highlight + idempotency record atomically.
System Does the end-to-end state transition survive 
realistic failure?
Capture  uncertain ACK  restart  replay → → →
 one logical Highlight, correct revision and →
durability status.
Validation / owner task Does the product satisfy the actual intended 
workflow?
Use the client to capture in a real source, 
reopen/recover and locate the same 
material.
A green unit suite never proves a full-system claim by implication. Every Proof Sheet and SEV 
must list the revision under test, commands actually run, exit results, independent read, exact 
limitations and P0/P1 disposition. If a new defect invalidates an earlier gate, reopen that gate 
and re-run its dependent proof set.
8. Phase 3 integrated exit gate
Phase 3 is accepted only when every required claim is proven on the final main revision, not merely because P3-09 
merged or all individual slice PRs once passed.
 The Work/Source identity contract and Anchor contract are explicit; Q11/Q12/Q8 are resolved or remain isolated 
within their named scopes.
 A real client/backend path ingests supported input, creates Highlight with valid Anchor, Bookmark and Note, and 
finds the committed material by keyword.
 Accepted captures survive declared crash/restart/replay/offline matrices with zero lost committed writes and no 
duplicate logical effects.
 Local-durable and server-durable are separate; sync uses a recoverable outbox with typed states and correct 
uncertain-ack behavior.
 All writes are owner-scoped and attributed. Two-owner/unauthorized/hostile-input tests fail closed; independent 
reads confirm the actual stored state.
 Revisions are immutable; tombstones work; governed purge remains effective after restore; stale derived state 
cannot masquerade as current.
 Derived passages and keyword indexes rebuild from authoritative data; export/restore satisfies the equality 
contract.
 Every SYS requirement maps to a test, Proof Sheet and SEV. Each relevant known-bad is refused by the live gate 
with the expected named code.
 Current CI passes on the final revision; clean-clone independent task agent completes the user-like path; a 
separate grader passes it with no unresolved P0/P1.
 Unverified items remain accurately stated. External client/UI validation is never fabricated inside this backend-
only repository.
Gate verdict rule  Any lost committed capture, wrong-owner disclosure, silent anchor retarget, false durability 
acknowledgment, purge resurrection, missing provenance on a derived claim, or P0/P1 falsely reported PASS 
blocks Phase 3 acceptance.
9. Phase 4 — reader, journal, and first usable experience
Phase 4 establishes Arivoo as an actual daily environment. The backend repository still does not build the UI; it must 
provide a well-defined, tested API that the real reader/journal client consumes. A CLI can inspect and test contracts, 
but it does not count as the intended reading experience.
P4 outcome  Import  open/read  save position  highlight/bookmark  write or revise a note  capture a free-→ → → → →
standing journal thought  use stable @ references  leave and reopen/recover the same material with honest → →
durability state. The actual client and real backend must be involved.
P4-00 — Foundation and integration contract
Objective: Freeze the real client/API boundary before broad UI implementation.
Required behavior and contracts
 Authenticated client identity and scoped authorization; defined command/query set for import, open, read 
position, capture, bookmark, note, journal and reference resolution.
 Truthful saved/queued/synced/conflicted/failed states; pagination, response budgets, stable typed errors, 
retry/idempotency, offline behavior and uncertain acknowledgments.
 Stable object IDs and @ reference semantics across rename, revision, tombstone, purge, unavailable and 
ambiguous targets; local cache versus server authority and invalidation.
 Format capability matrix, extraction readiness and unresolved-anchor states; client/API compatibility, migration 
and rollback; concrete user scenarios and evidence tests.
Verification focus
 A real contract test invokes the actual API boundary under authorized scope. The UI never writes product tables 
directly or uses a privileged key to bypass owner scope.
 Auth expiry, malformed DTO, stale API version, pagination cap, retry after lost response, offline transitions, stale 
source, deleted/purged target and owner boundary.
Slice acceptance: P4-00 is accepted only when interface behavior, auth, states, compatibility and proof scenarios are frozen; mocks 
remain useful design tools but are not integration evidence.
P4-A — Format intake and reader position
Objective: Support real reading formats with measured location fidelity.
Required behavior and contracts
 Increment PDF/EPUB/JSON and other readable formats along the durability ladder; distinguish native text from 
scanned/OCR and reflow from fixed layout.
 Staged source bytes survive parse failure. Unsupported, encrypted, malformed or over-limit material returns 
explicit typed failure. Position and Anchor capability is format-specific.
Verification focus
 Use the Q8-approved corpus; measure reopen-to-location and highlight resolution across reflow, pagination, edits, 
extraction versions and new editions. Record failures, not only success cases.
Slice acceptance: A format is called supported only after its acceptance corpus, location/anchor tests, failure modes and recovery 
evidence pass. One PDF fixture is not evidence for every PDF.
P4-B — Reading and capture integration
Objective: Make the backend capture contract real inside the actual reader client.
Required behavior and contracts
 Open imported material; update position; capture Highlight/Bookmark/margin Note through API; show persisted 
status; retry safely; return to the saved location.
 No privileged helper and no direct table writes. Handle auth renewal, stale material, ambiguous Anchors and 
honest offline/uncertain states.
Verification focus
 Duplicate click, reload/restart, timeout with unknown server outcome, retry after lost response, wrong owner, 
forbidden source, expired credentials, unsupported format and target deletion.
Slice acceptance: The real client shows the correct state after success, timeout, restart and retry; the same authored content remains 
visible after reopening.
P4-C — Library, reading lists and journal blocks
Objective: Turn reading and reflection into a coherent daily environment.
Required behavior and contracts
 Stable library/list membership and current-reading state; session/position events stay inside the D-010 boundary.
 Journal supports source-optional raw thought and creative blocks; long-form thinking is preserved losslessly 
rather than forced into tiny summaries.
 Define serialization and round-trip fidelity for diagrams/structured blocks before calling them supported.
Verification focus
 Journal revision history, cross-source references, blank/source-optional block, long text, Unicode, diagram round-
trip where implemented, offline/restart, export/restore and ownership isolation.
Slice acceptance: A thought can be written without a source, then later connected to research; raw authored text and prior revisions 
survive round-trip.
P4-D — Stable @ references
Objective: Make links durable without leaking private state or lying about a target.
Required behavior and contracts
 References bind to stable identity; define whether a reference targets current or explicit historical revision.
 Resolve renamed, revised, tombstoned, unavailable, ambiguous and purged targets with typed states and privacy-
preserving behavior.
 Imported text that resembles @ syntax remains inert untrusted content until the owner or authorized command 
creates a real reference.
Verification focus
 Rename and revise targets; delete/purge; stale cache; cross-owner guessed IDs; imported hostile strings; 
export/restore; reference to a historical revision.
Slice acceptance: References never break solely because a label/title changes, and never quietly redirect to unrelated content or 
reveal another owner’s object existence.
P4-E — Baseline scoped agent access
Objective: Expose meaningful owner context to authorized agents at first usable milestone.
Required behavior and contracts
 Read-only first implementation through the same authorized API/core used by the client; stable scope, 
provenance, version and response budgets.
 Agent identity/authorization is explicit; imported content remains untrusted. MCP is an adapter around the API, 
not a second permission or persistence path.
 P5 later improves semantic ranking and relationship discovery, but an agent should already be able to access the 
durable context in the P4 usable product.
Verification focus
 Two-owner access matrix, hostile document instructions, request limits, truncation with provenance, stale 
index/source, tombstone/purge, unauthorized references, API authentication and least privilege.
Slice acceptance: The agent can retrieve and explain the precise allowed material without DB access or broader scope than the 
owner authorized; P4 baseline is not “full intelligence.”
P4-F — Recovery, regression and acceptance gate
Objective: Close the actual day-one workflow as a system, not as a CRUD checklist.
Required behavior and contracts
 Migrate from supported prior state; recover the complete source/capture/note/journal/reference path; 
export/restore authored content; rebuild derived state; ensure purge invalidation.
 Exercise sync conflict semantics and offline/uncertain acknowledgments; test the actual client against the real 
backend. The independent grader gets a clean context and realistic owner task.
Verification focus
 Clean install and upgrade; local/server transitions; crash and restart at every persistence boundary; owner 
isolation; hostile imports; reference integrity; restore equality; client/API compatibility and failure messages.
Slice acceptance: Owner workflow passes on actual client + backend with independent grading and owner-fidelity review. If the 
actual reader/journal client is unavailable, that part is BLOCKED, not silently passed by a mock.
10. Phase 4 integration contracts and refinement rounds
10.1 User-visible state contract
State Meaning to the client Allowed transition pattern
Saving / in flight No persistence promise yet. Request outstanding; do not label Saved.
Local-durable Local authoritative mutation and local 
recovery intent have committed.
May be queued for server sync; can survive 
declared local restart boundary.
Queued / retryable Local state preserved; remote state not 
confirmed.
Retry with same idempotency identity; 
expose offline/remote lag truthfully.
Server-durable Authoritative server state independently 
acknowledged/read under contract.
Update only after confirmed remote commit, 
not on send.
Conflicted
Competing authored state or stale 
assumptions prevent a safe automatic 
resolution.
Preserve inputs; present typed conflict 
behavior; no silent LWW.
Failed The operation did not commit or reached a 
defined unrecoverable condition.
Return reason and recovery path; if commit 
outcome uncertain, label uncertain rather 
than failed.
State Meaning to the client Allowed transition pattern
Anchor unresolved / ambiguous Position could not be re-established 
uniquely.
Do not move to nearest text; preserve the 
original Anchor and surface repair options.
Tombstoned / purged Normal retrieval or all retained copies differ 
according to governed policy.
Invalidate caches and derived copies; 
restore cannot undo a final purge.
10.2 Seven mandatory refinement rounds
The owner-approved plan names seven review-and-repair rounds once the Phase 4 path is sufficiently end-to-end to 
exercise. Seven is a minimum, not a stopping condition; rounds continue until the exit gate is actually green. A defect 
that invalidates a passed gate reopens that gate.
Round Attack surface Example questions
1. Requirements and contracts Traceability, semantics, compatibility
Can each behavior point to intent, SYS/P4 
contract, tests and proof? Are save states 
precise?
2. Trust and hostile inputs Auth, privacy, injection, capabilities
Can a second owner infer or read hidden 
state? Can imported content influence 
authority?
3. Domain and provenance Identity, revision, anchors, @ refs
Can a renamed target break a ref? Can a 
new edition silently move an Anchor? Is 
provenance complete?
4. Transaction and failure Replay, concurrency, crash boundaries
What happens when commit precedes lost 
ACK? Can repeated delivery create duplicate 
writes?
5. Client/API integration Real stack, state displays, errors
Do client-visible states reflect actual 
backend state in offline, retry and conflict 
paths?
6. Recovery and resources Migration, purge, restore, rebuild, envelopes
Does a clean restore preserve authored 
state? Can stale derived data reappear? 
What are latency/resource limits?
7. Independent clean-room grade Uncoached task, product fidelity
Can a fresh agent complete a realistic 
workflow with source pointers and correct 
uncertainty handling?
11. Phase 5 — retrieval, relationships, concepts, and 
compounding
Phase 5 must not turn the substrate into a black box. Search and agents are core capabilities of the architecture, not a 
bolt-on version 2. But intelligence remains bounded by evidence, repeatable evaluation, provenance, owner scope and 
reversibility. A vector hit is a retrieval event, not a fact.
P5-A — Authorized retrieval API and context packs
Objective: Make all retrieval explainable and bounded before adding ranking complexity.
Required behavior and contracts
 Support keyword, stable identity, scope/filter, temporal and behavioral queries, pagination, strict response 
budgets and typed errors.
 Every returned item carries the correct Source/revision/Anchor identity, owner scope, trust status and a 
mechanically true reason (“why”); truncation preserves provenance.
 MCP wraps the same authorized core. No second query semantics, privilege path or direct DB route is introduced 
for agents.
Verification focus
 Wrong-owner and hostile instruction inputs; budget/truncation; pagination; stale/tombstoned/purged records; a 
“why” field that points to the actual evidence and ranking features used.
Slice acceptance: An authorized agent receives precise, explainable context under budget and can identify source/version/trust 
without inferring authority from imported text.
P5-B — Evaluation baseline before ranking changes
Objective: Establish the baseline and evaluation protocol before tuning a new ranker.
Required behavior and contracts
 Create versioned query corpus: relevant, no-result, distractor, conflict, duplicate-group, multilingual, temporal, 
behavioral and owner-isolation cases.
 Split development/calibration from a locked held-out set. Assess keyword and explicit-relation baselines first; 
define acceptance targets for relevance, latency and cost before the run.
 Keep safety/provenance/budget invariants separate from empirical relevance scores. Do not set a 100% relevance 
target or move thresholds after seeing results.
Verification focus
 Precision/recall and ranking metrics; false positives/no-results; p50/p95 latency; cost; reproducible 
model/config/corpus revisions; regression table on all held-out cases.
Slice acceptance: There is a recorded baseline, held-out evaluation protocol and predeclared acceptance targets, including honest 
limitations and cases not represented.
P5-C — Semantic spike under Q7
Objective: Select the semantic mechanism only through a measured, approved experiment.
Required behavior and contracts
 Before any paid/selected call, owner decision Q7 approves budget, model/version, license, runtime, corpus and 
evaluation envelope.
 Compare embeddings/vector behavior against keyword and explicit-relation baselines. Deterministic fakes 
validate interfaces and fault behavior only, never semantic quality.
Verification focus
 Measure precision/recall/ranking, p50/p95 latency, resource/cost and false matches on representative corpus sizes; 
include paraphrase, topic-adjacent distractor, contradiction and multilingual cases.
Slice acceptance: The selected path has measured value over baseline and acceptable cost, or the result honestly recommends no 
activation yet. No budget means paid semantic work remains blocked, not the entire phase.
P5-D — Versioned semantic index and vector retrieval
Objective: Add reversible derived retrieval that never becomes authoritative.
Required behavior and contracts
 Embeddings/index records bind to source and revision, model/config version, generation/run and timestamps as 
appropriate. Jobs support retry, invalidation, deletion, rebuild and purge.
 Owner filters are applied at query and index lifecycle boundaries. Keyword search remains available when 
embeddings, provider or semantic indexing fails.
 No authored content, user belief or unique source record exists only in vectors or model state.
Verification focus
 Interrupted job, duplicate generation, source update, model migration, stale vector, changed model, 
deletion/purge, owner mismatch and complete rebuild from authoritative records.
Slice acceptance: Semantically indexed state is versioned and rebuildable; stale generations cannot appear current; semantic outage 
does not impair durable capture or keyword behavior.
P5-E — Hybrid retrieval with measured why paths
Objective: Combine exact, structural, lexical and semantic retrieval without an unexplainable ranking leap.
Required behavior and contracts
 Declare ranking features, filter order, budget and score semantics. Return a truthful why-payload that points to 
actual features/evidence used, not a generated rationalization.
 Evaluate held-out gains and every material regression relative to keyword/explicit-relation baselines; thresholds 
are fixed before evaluation.
Verification focus
 Queries with no answer, hard distractors, conflicting revisions, duplicates, owner boundary and multilingual 
variants. Score both hit quality and whether the explanation matches the computation.
Slice acceptance: Hybrid retrieval improves predeclared held-out targets or remains an optional/limited path with a precise failure 
report; there is no claim of success from a few good demos.
P5-F — Discovery candidates versus grounded relationships
Objective: Prevent plausible similarity from being promoted to a factual relationship.
Required behavior and contracts
 Candidate discovery is provisional and explicitly labelled. Grounded relationship requires allowed text-pair 
decision or structural fact, valid owner-scoped/versioned endpoints, evidence spans and the authorizing 
policy/run.
 Owner corrections form transparent history; no per-candidate review queue that blocks the general pipeline. 
Unadopted relationships can be rejected, aged or recomputed under defined rules.
Verification focus
 Near duplicates, paraphrases, adjacent topics, contradictory sources, missing evidence, wrong Source/revision, 
endpoint purge, correction and reversibility.
Slice acceptance: Only admissible relationships are promoted; every edge is explainable and reversible, and unsupported 
candidates remain discovery rather than facts.
P5-G — Concept formation and lifecycle
Objective: Allow a useful conceptual memory to emerge without forced tags or ungrounded entity merges.
Required behavior and contracts
 Concepts have stable provisional IDs; alias, correction, merge, split, promotion and retirement are historied and 
reversible.
 No forced “fact/concept/quote” tag system. Owner-authored classification words remain ordinary text unless a 
future explicit owner decision changes the rule.
 Independent-source policy distinguishes byte duplicates, separate acquisitions, editions, paraphrases and 
genuinely independent works. Graduation requires evidence on genuinely held-out material.
Verification focus
 Concept collisions, aliases, near-duplicate sources, independent evidence, held-out graduation, false concept 
growth, split/merge rollback and purge invalidation.
Slice acceptance: Concept utility is measured by useful retrieval and grounded behavior, not by number of concepts, mentions or 
graph edges.
P5-H — Kev policy and evaluation gate
Objective: Make non-generative relationship/evidence policy a gate rather than a self-justifying model output.
Required behavior and contracts
 Use the bounded non-generative output vocabulary and policy version defined by the recorded contracts. Include 
abstention; no output outside the allowed schema is promoted.
 Kev must pass before Kev-backed relationship evidence promotion, concept graduation or graph compounding. A 
Kev result is never its own evidence; similarity never upgrades itself into truth.
Verification focus
 Hard negatives, contradictions, near duplicates, no-evidence pairs, held-out pairs, abstention, malformed outputs 
and reproducibility across policy/model revisions.
Slice acceptance: Promotion paths are disabled until the eval gate passes; a failed/unknown policy leaves a safe discovery path, not 
an ungrounded relation.
P5-I — Three independent compounding grades
Objective: Prove C3 in progressive independent tests rather than one broad “it compounds” claim.
Required behavior and contracts
 Deterministic: known alias or explicit relation makes a previously saved Highlight retrievable; prove absence at 
baseline and explain the post-change path.
 Semantic: a new related Work causes old material to resurface on held-out queries; pin corpus, model/config and 
baseline.
 Graph: a grounded relation adds useful paths without fabricated evidence; include false-link, contradiction, purge 
and reversible-recompute controls.
Verification focus
 Run each grade independently. Include source provenance and evidence trail; validate in actual research use 
rather than retrieval metrics alone.
Slice acceptance: C3 is claimed only for the demonstrated rung. Passing deterministic does not imply semantic, and semantic does 
not imply graph acceptance.
P5-J — Final integrated gate
Objective: Demonstrate the compounding system preserves truth, captures and owner agency under stress.
Required behavior and contracts
 Capture continues while enrichment, semantic provider, embedding generation or relationship discovery is 
unavailable.
 Authorized agents retrieve bounded context; wrong-owner queries and hostile imported instructions fail closed.
 Purge invalidates all derived copies, caches and references within the declared contract; 
rebuild/migration/performance/cost and all RTM/SEV evidence is complete.
Verification focus
 Clean-clone end-to-end owner task, independent read/grade, held-out evaluation, failure-injection, purge/restore, 
provider outage, index rebuild and owner-fidelity review.
Slice acceptance: C3 is demonstrated with actual reasons and provenance; no unknown corpus, budget or policy is quietly reported 
as PASS.
12. Phase 5 evaluation and promotion gates
12.1 Candidate-to-evidence promotion pipeline
1. Ingested text and source metadata stay untrusted as instructions; parsing and retrieval do not confer execution 
authority.
2. Retrieval returns candidate items with source/version/anchor and trust metadata. Similarity or ranking score is 
not evidence of truth.
3. A relationship candidate remains provisional until its evidence policy authorizes a structural/text-pair decision 
with correct endpoints and versioned evidence.
4. Concept discovery can begin provisionally, but promotion/graduation is gated by the Kev policy/evaluation and 
independent-source/held-out rules recorded in PLAN.md.
5. Any changed source, parser, embedding model, ranker, policy, concept merge or endpoint lifecycle invalidates or 
versions dependent derived generations; recomputation is reversible and auditable.
6. Owner corrections are retained as history. They should improve later derivation without editing away original 
sources or silently rewriting prior authored thoughts.
12.2 Evaluation must separate three questions
Question What the metric/test should prove What it cannot prove
Safety invariants
No owner leakage, no policy bypass, no 
provenance loss, no purge resurrection, no 
unsupported promotion.
That retrieval is relevant or useful.
Retrieval quality
On locked held-out corpus, appropriate 
results rank well and distractors/no-result 
cases remain honest.
That the top result is a fact or the system’s 
conceptual explanation is grounded.
Owner usefulness
During actual study/research, old material 
resurfaces at relevant moments and helps 
the owner reason.
That a benchmark score generalizes to every 
corpus or every person.
The quality baseline, test corpus version, held-out boundaries and acceptance targets must be fixed before evaluation. 
Report all material regressions, not only average wins. Safety failures are gates, not trade-offs to be offset by a better 
mean ranking score.
13. Final-goal acceptance matrix
The final goal is the fully realized North Star across layers 1–7 and claims C1–C5. The authoritative roadmap defines 
Phase 5 as the final named phase; it does not establish a P6 specification. Do not invent one. Completion is determined 
by the observable behavior below, not by phase numbers or presentation quality.
Final capability C1–C5 linkage System evidence required Failure that blocks the claim
Preserve intellectual work C1, C5
Immutable authored revisions, 
correct attribution, declared 
durability states, fault recovery, 
independent read and 
export/restore equality.
Any accepted capture lost; silent 
overwrite; false success; purge 
resurrection.
Read/import broadly and honestly C1, C5
Per-format corpus and capabilities; 
source digests; extraction 
generations; explicit 
unsupported/scan/OCR states; 
stable Anchors.
Calling a format supported without 
test corpus; silent anchor move; 
partial import reported complete.
Final capability C1–C5 linkage System evidence required Failure that blocks the claim
Agent has owner context C2, C5
Same scoped API, identity, budgets, 
source/revision/trust provenance; 
MCP adapter; hostile text inert; 
independent two-owner tests.
DB bypass, privileged-key client, 
owner leakage, context without 
source trail.
Material becomes easier to 
rediscover C2, C3, C5
Keyword + semantic baselines; 
versioned index/rebuild; measured 
held-out improvements; why-
payloads and truthful truncation.
Ranking explanation not 
connected to actual logic; stale 
generations presented as current.
Relationships are grounded C3, C4, C5
Versioned endpoints; evidence 
spans/structural facts; policy/run; 
hard negatives; reversible 
corrections and held-out 
graduation.
Similarity promoted to fact; model 
output used as its own evidence; 
silent merge.
Conceptual memory improves over 
use C3, C4, C5
Stable IDs, aliases, merge/split 
history, independent-source policy; 
actual-use compounding probes; 
usefulness not volume.
Concept counts used as success; 
correction wipes history; 
unsupported promotion.
One coherent daily environment C1, C2, C3, C5
Actual client workflow: 
import/read/position/capture/note/j
ournal/@/leave/reopen/recover; 
API integration and owner task 
grade.
API CRUD-only proof; UI path 
mocked; client says saved when 
not saved.
Change is reversible and 
explainable C1–C5
Proof-carrying changes, immutable 
revisions, derived generation IDs, 
why paths, migrations, restore, 
purge and rollback tests.
No way to explain or undo derived 
change; source truth contaminated 
by derived output.
13.1 Final system qualities
 No silent data-loss path is known to remain in the tested contract. This is a bounded assurance statement, not a 
mathematical guarantee of zero possible bugs.
 Every supported input type has a measured capability and failure contract, not an unqualified “all readable 
formats work” marketing label.
 Every agent interaction is scoped, read-only unless an explicitly approved write capability later exists, bounded, 
provenance-carrying and evaluated through the same core API.
 Every derived artifact has lineage, expiration/invalidation rules, reproducible policy/config identity and a safe 
rebuild path.
 Owner-authored content is never reduced to model-generated summaries as the only stored representation. 
Summaries may help retrieval but do not replace source text or raw thinking.
 Performance/cost/resource limits are explicit and measured at representative sizes; no hidden unbounded 
retrieval or enrichment jobs.
 Build and verification processes evolve only where concrete product behavior reveals a missing control. The 
harness is an instrument, not the product.
14. Open owner decisions and non-inferred choices
The following items are owner-gated in the current canonical register. They must remain visible until resolved by the 
prescribed decision process. Each blocks only its named dependent work.
Question Current default / boundary Blocked scope only Safe progress meanwhile
D-014: calculation engine Open; no final calc engine choice. Math workflow design. General capture, notes, journals 
and retrieval architecture proceed.
Question Current default / boundary Blocked scope only Safe progress meanwhile
Q6: research transcript
Reference doctrine unless adopted; 
explicit Part-2 scenario remains 
gated.
Named transcript acceptance 
scenario and S5 corpus.
General P4 journal/capture 
workflow and unrelated tests 
proceed.
Q7: semantic budget Selected/paid semantic work 
deferred until approved.
Spend/model selection and selected 
semantic spike.
Prepare deterministic evaluator, 
fixtures, comparison contract and 
options.
Q8: extraction corpus
Synthetic corpus default; do not 
claim real PDF/EPUB Anchor 
stability without measurement.
Real-document stability/acceptance 
corpus.
Design generic format boundaries 
and use synthetic fixtures; collect 
evidence for owner gate.
Q9: repository visibility
Public at current observation; 
owner-gated, no agent visibility 
change.
Any visibility change.
Product work proceeds; be careful 
about personal raw content and 
exposure boundaries.
Q10: token/workflow-tamper 
hardening
Owner controls token 
minting/scope. Do not claim the 
residual closed by unrelated in-
repo controls.
Specific workflow-tamper 
hardening.
H-01/H-02 and product boundaries 
proceed within verified 
assumptions.
Q11: Work/Source identity
No auto-merge; no 
title/filename/semantic 
uniqueness. Byte storage dedup is 
separate.
Identity-dependent 
merge/dedup/unique constraints.
Kernel and provider-neutral intake 
contracts proceed.
Q12: blob storage/staging/recovery
Provider/local-cache/cross-store 
recovery still needs owner 
ratification; no cross-store 
atomicity claim.
Provider-specific product schema 
and durability promise.
Compare options at P3-00; design 
provider-neutral interface and 
explicit recovery states.
Decision handling  A default is not automatically an owner decision. Silence does not resolve a security, privacy, 
data-loss or irreversible-action question. The exact blocking boundary and authoritative home must travel with 
the decision record.
15. Failure modes, anti-patterns, and review checklist
15.1 High-severity failure classes
Failure class Concrete manifestation Required control/evidence
Lost acknowledged write UI says saved; DB/outbox has no authoritative 
record.
Commit/ack fault injection; truthfully mapped 
status; independent read; restart/retry proof.
Duplicate logical side effect Timeout retry creates a second Highlight, Note 
revision or import identity.
Canonical request encoding; idempotency 
registry; concurrent replay test; independent 
effect count/content.
False source identity Similar filenames auto-merge unrelated Works 
or editions.
Unresolved Q11 default; explicit identities; no 
automatic uniqueness/merge.
Anchor corruption A highlight silently follows a new edition or 
nearby text.
Source-version-bound Anchor; ambiguity/failed 
resolution states; adversarial edition/reflow 
corpus.
Owner data leak API/agent query omits owner filter or exposes 
deleted target existence.
Auth at query/command boundary; two-owner 
hostile tests; deleted/private state privacy 
review.
Stale derived result Old semantic index/relation survives revised 
source or purge.
Generation lineage, invalidation, 
tombstone/purge propagation and full rebuild 
tests.
Failure class Concrete manifestation Required control/evidence
Unsupported promotion Vector/Kev candidate becomes a fact without 
admissible evidence.
Separate discovery and grounding; 
schema/policy gate; hard-negative and held-out 
evidence.
False recovery proof Restore test compares only row counts or the 
same derived index.
Canonical authoritative-state comparison plus 
independent content, references, schema and 
ownership oracle.
Misleading SEV Report stale, self-referential or incomplete but 
gate stays green.
Exact diff digest, base-anchored gate, public 
validator known-bads, fresh-context reviewer 
and independent grader.
15.2 Anti-patterns that should be rejected in review
 Calling a check “independent” because it has a different filename or a self-declared reviewer ID, without checking 
what code and data the reviewer actually trusts.
 Equating green CI with phase exit, integration, reliable recovery or user-task validity.
 Using mocks as proof of real API integration; using CLI flows as proof of the separately built reader UI.
 Choosing a blob provider, Work dedup rule, paid model or new semantic threshold merely because 
implementation is easier that way.
 Using last-write-wins to hide authored revision conflicts, using current title as identity, or moving Anchors to “the 
closest paragraph.”
 Promoting similarity to truth, letting a model result certify itself, or treating generated explanations as if they 
were the ranking computation.
 Adding a universal framework, extra layer or security promise without a corresponding concrete failure, 
requirement and known-bad. Conversely, refusing to add a needed guard after a real defect is reproduced.
 Rewriting history in append-only claim/decision/session records to make the current snapshot look cleaner. 
Correct by append + pointer; regenerate STATE from present facts.
15.3 Review checklist for every slice
 Intent/decision/SYS IDs are valid; requirement change uses canonical change channel; scope is exclusive in 
CLAIMS.
 Diff and tests are bounded; interfaces and source-of-truth boundaries are explicit; no second kernel or privilege 
bypass.
 Expected-RED case is registered before the fix and shown failing for the right reason; regression passes on the 
repaired revision.
 Real stack is exercised for DB/API/migration behavior; independent state read confirms the effect claimed.
 Failure injection covers relevant before/after commit, restart, replay, concurrency, remote acknowledgment and 
rebuild boundaries.
 Known-bads exercise the actual gate and report expected named refusals. Evidence is bound to the exact 
revision/diff and generated sheet.
 Independent SEV review is fresh-context and not authored by the implementation slice’s builder; all findings get 
explicit disposition before merge.
 P0/P1 and blocking owner questions stop acceptance; P2 is not automatically accepted debt and needs owner-
approved disposition.
 On merge, close claim row, append session/worklog evidence, reconcile STATE and AGENTS, and recheck remote 
post-merge CI.
16. Execution protocol and phase-gate evidence
16.1 Slice loop
7. Recover current state from the repo and observe live GitHub state; do not trust a stale STATE/CLAIMS snapshot as 
live API truth.
8. Claim a bounded slice before consequential work; bind it to its requirement/intent and name what is explicitly 
out of scope.
9. Specify the interface, state transitions, oracles and failure matrix before implementation. Preserve open owner 
decisions and the exact dependency they block.
10. Write and observe RED-first regressions that discriminate the named defect. Avoid vacuous assertions and 
tests that borrow live registry entries or trusted state from the candidate.
11. Implement the smallest coherent behavior that meets the complete contract; use the real adapter/kernel 
rather than a second path.
12. Run implementation tests, then independent test verification, then SEV review and actual gate-path known-
bads. Bind evidence to the exact base/diff/revision.
13. Inspect all review findings, disposition each in-thread before resolution, fix real findings in-slice or route a 
named follow-up, then rerun relevant and full gates.
14. Merge only after policy-complete review and gate evidence. Observe post-merge CI; append the claim close 
row, session record and worklog; reconcile STATE/AGENTS.
16.2 Evidence records
A meaningful session should leave a compact WORKLOG entry. Substantial work should leave a numbered session 
engineering record with: the owner request verbatim; starting revision and observed state; scope and non-scope; 
results; exact paths; actual commands/actions; evidence; failures/dispositions; unverified items; open decisions; one 
deterministic next action; and session close information. Never reconstruct command output, pretend an API call 
succeeded, or use a historical run as proof for a later diff.
16.3 Gate closure sequence and no-pause rule
Gate Required result Continuation
H-02
Validator + gate live, known-bads fail, 
digest/fresh-context/limitations verified, trusted 
H-01b floor can judge path.
P3-00. If a security/fidelity P0/P1 exists, repair it 
before proceeding.
P3-00
RTM and interfaces accepted; exact Q8/Q11/Q12 
dependencies mapped; schema freeze and 
failure matrix approved.
P3-M0 and P3-K0 in disjoint scope, then P3-01.
P3-01..09
Each behavior is real and verified; 
migration/kernel safety, authoritative 
durability and recovery proved.
Phase 3 exit gate, not just “last PR green”.
P4-00/A..F
Actual client integration, 
reader/capture/journal/@ flow, baseline scoped 
agent read and recovery.
Phase 4 exit gate plus seven+ refinement 
rounds.
P5-A..J
Retrieval and C3 compounding grades, 
grounding and concept gates, reversible 
derived state.
Final-goal acceptance matrix, held-out evidence 
and owner-use validation.
Continuity means continuing to the next deterministic slice, not skipping review or gates. The 
no-pause directive does not authorize unreviewed merges, hidden owner choices, falsely closed 
issues or unsupported claims. It means do not stop merely to narrate progress when the next 
authorized work can proceed.
17. What “done” means for Arivoo
Arivoo is aligned with its North Star when an owner can use it as a normal, dependable intellectual environment: 
import readable material; read and return to the correct place; capture highlights and bookmarks; write deep notes 
and journal thoughts; reference exact material; preserve the entire authored history; connect a personal agent safely; 
and see old material become more useful as new material arrives—without sacrificing provenance, reversibility, 
privacy, or truthful uncertainty.
The product must preserve raw owner thinking rather than funnel everything into short summaries; operate through 
one authorized API core; keep authored state authoritative and derived indexes rebuildable; and support the path 
from deterministic retrieval to semantic resurfacing to grounded graph relationships. “Intelligent” is not the same as 
“reliable.” The system earns the right to promote a relationship only when its evidence policy and evaluation say so.
Final acceptance questions
 Can we prove every acknowledged authored write is durable at the declared rung and recover it after every 
failure in the published matrix?
 Can a new clean client and an authorized agent access the same owner-scoped material through the same API 
without privileged bypass?
 Can an independent reader trace a retrieved item or promoted relationship to the precise source/revision/Anchor, 
evidence and policy that caused it to appear?
 Can we delete/rebuild any derived index and recover the correct behavior from authoritative state alone?
 Can we correct or retract derived relationships/concepts without erasing authored history or making the evidence 
chain unintelligible?
 Does a genuinely new related input measurably make old material more useful in deterministic, semantic and 
graph tests—and during actual research use?
 Are unsupported inputs, absent budgets, unknown owner decisions and unverified cases shown as blocked or 
limited rather than passed?
Final standard  No lesser product is justified by a phase boundary. The phases sequence the proof and delivery 
of the full vision; they do not shrink the vision. Every phase produces usable behavior while protecting the 
architectural path to the complete system.
Canonical references consulted
 NORTH-STAR.md — owner vision, C1–C5, seven layers, durability ladder, backend/UI boundary.
 PLAN.md — P3 system requirements, P3-00/M0/K0, slices P3-01..09, SEV criteria, P3 exit, P4-00/A–F, seven 
refinement rounds, P5-A–J and three C3 grades; NG-04 one-phase-deep rule.
 DECISIONS.md — D-014 and Q6–Q12 open owner gates and scope limits.
 EXECUTION.md / AGENTS.md / STATE.md — source authority, change channel, current-state and session rules.
 ENGINEERING.md / OPERATING-MODEL.md / LAWS.md / GLOSSARY.md — ratchet, V-model, proof-carrying 
change, evidence, gate and state terminology.
 PR #71, #72, #73 and GitHub Actions run #39989587479 — H-01c merge and remote CI evidence current at 2026-10-
24 review time.
Document limitation: this is a detailed execution/acceptance roadmap based on canonical sources. It is not a new owner decision, a 
merged repository change, evidence that H-02 exists, proof that Phase 3 has begun, or an invented Phase 6 plan.
