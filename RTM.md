# RTM — Requirements Traceability Matrix and the P3 Contract Freeze

> STATUS: CANONICAL (root layer). The single canonical home of the requirements traceability
> matrix (D-039 element 3: "ONE requirements traceability matrix at a single canonical home
> (created at P3-00; not duplicated into navigation files)"). The requirement STATEMENTS live in
> `/PLAN.md`'s SYS table; the term DEFINITIONS live in `/GLOSSARY.md`; the owner decisions live
> in `/DECISIONS.md`. This document holds the TRACE (owning component, interfaces, pre-registered
> test paths, claims, validation scenario) and the P3 CONTRACT FREEZE (entity contracts, state
> machines, transaction/acknowledgment semantics, the migration plan, the failure-behavior
> matrix, the open-question boundaries). Created at P3-00 (CLAIM-043, session 30, 2026-10-24).
> Product schema migrations are gated on this freeze's acceptance through the repository process
> (PLAN's P3-00 card); a change to any frozen contract here follows the canonical change process
> — never a silent edit. On conflict, the authority order is `/EXECUTION.md` §3.

## 0. What this freeze freezes, and what it deliberately does not

**Frozen by this document (Phase 3 builds on these without re-litigating them per slice):**

- The trace of SYS-01..SYS-11 to owning components, interfaces, test paths, claims, and user
  validation scenarios (§1) — every future SYS row added to PLAN.md must land with its RTM
  trace in the same change (VER-806 refuses the gap).
- The authoritative entity contracts: identity, ownership, actor, revisions, provenance, and
  the authoritative-vs-derived boundary for every Phase 3 entity (§2).
- The seven state machines with their honest terminal states (§3).
- The transaction and acknowledgment semantics: commit points, the durability rung vocabulary,
  idempotency, and the provider-neutral blob boundary (§4).
- The migration and compatibility plan (§5) and the named-failure matrix (§6).

**Deliberately NOT frozen (visible at their exact named scopes, §7):**

- Q11 (Work/Source identity policy): the baseline holds — no auto-merge, no identity-dependent
  uniqueness constraints; physical byte-reuse is never logical identity. P3-02 implements the
  baseline; any identity policy beyond it waits for owner ratification.
- Q12 (blob backend, staging lifecycle, cross-store recovery): the freeze is provider-neutral —
  the schema carries a content-addressed blob-reference contract only. The comparison and
  recommendation live in §7.4 as evidence-preparation; no provider-specific migration or
  cross-store atomicity claim until ratification.
- Q8 (extraction-spike corpus): synthetic by default; any real-PDF/EPUB location-stability
  claim requires a named permitted corpus and measured results (P3-03's spike).
- Q6, Q7, D-014: unchanged scopes (research-transcript status; the semantic-spike budget; the
  calculation engine) — none blocks Phase 3 capture work.

**Phase 4 reservations:** the Journal block, @-reference, and agent-surface ENTITY contracts
appear in §2 as reservations only (identity/ownership/revision shape); their interface freeze is
P4-00's deliverable, never claimed here.

## 1. The trace — SYS-01..SYS-11

Each section: the requirement pointer (the statement lives in PLAN.md's table — never
duplicated here), the owning component, the frozen interfaces, the PRE-REGISTERED test paths
(the suite/case shapes that will prove it, named before the implementation slices run), the
North Star claim ladder, and the user validation scenario (the V-model validation wing).

### SYS-01 — truthful acknowledgment at a named durability rung

- **Requirement:** PLAN.md SYS-01 (C1).
- **Owning component:** the command kernel (`harness/commands.py`, P3-K0) + the capture
  commands (P3-04/05/06) + the client acknowledgment contract (P3-01's §1.6 path) + the outbox
  (P3-08).
- **Interfaces:** every write command returns `{status, durability_rung, effect_id, …}` where
  `durability_rung ∈ {in_flight, local_durable, queued, server_durable}` (one serialized
  vocabulary — §3.2/§4's exact tokens) — the acknowledgment
  names the rung the SERVER independently knows, never the request's send state; the derived
  rungs (`keyword-searchable`, later `semantically indexed`, `linked`) are reported by their
  own generation queries, never by the write acknowledgment.
- **Pre-registered test paths:** crash-before-commit → no acknowledgment, no effect; commit
  then death-before-ack → the client's retry replays to the SAME recorded result (the
  uncertainty resolved by query, never assumed); timeout after possible server commit → the
  typed `uncertain` outcome until replay/query resolves; the independent read (the `arv_read`
  auditor role) confirms the rung the acknowledgment claimed (P3-01's crash matrix; P3-08's
  uncertain-ack cases).
- **User validation scenario:** the owner captures a passage, the client shows "local-durable"
  (not "saved" from the request), a restart preserves it, and sync later moves it to
  "server-durable" — each state the client shows is one the backend independently knows.
- **Proof-path class:** fault-injected system proof with an independent authoritative read —
  a green unit test never proves a rung claim (the V-model level rule).

### SYS-02 — immutable evidence, revisions, tombstones, governed purge

- **Requirement:** PLAN.md SYS-02 (C1, C5).
- **Owning component:** the entity revision state (P3-04/06) + the substrate's append-only
  triggers (`ARV-EV-001/002` — the 0002/0003 migrations' convention, extended per entity).
- **Interfaces:** authored content changes ONLY by appending a new immutable revision (a new
  row bound to the entity id + revision number + actor + provenance); delete = a tombstone
  event (hidden from normal retrieval, recoverable); the governed purge (D-011: owner-only,
  never a runtime agent) is the sole erasure path and records a minimal audit row; restore
  applies the purge ledger — purged material and its derived copies cannot resurrect (SYS-10's
  coupling).
- **Pre-registered test paths:** UPDATE/DELETE on an authored row → refused by the trigger with
  its named code; a revision append → the prior revision byte-unchanged (independent read);
  tombstone → normal retrieval hides, governed history retains, restore recovers; purge → the
  audit row exists, the content and derived copies are gone, restore-after-purge cannot
  resurrect (P3-04/06/09's cases).
- **User validation scenario:** the owner edits a note; both versions remain attributable and
  retrievable; deleting hides it from the reader but a governed restore brings it back —
  while a deliberate purge stays final.
- **Proof-path class:** mutation-rejection + history-preservation tests at the real DB, plus
  the purge-invalidation proof at P3-09.

### SYS-03 — owner scope, actor, identity, provenance on every write

- **Requirement:** PLAN.md SYS-03 (C1, C2, C5).
- **Owning component:** the API/command boundary (P3-01) + every write path; the substrate
  convention (owner_scope/actor/run_id/input_hash NOT NULL, RLS by `app.current_owner`, the
  `arv_read` BYPASSRLS auditor — the 0002 migration's shape, reused by every product table).
- **Interfaces:** `owner_scope` is SERVER-DERIVED from the authenticated principal (never a
  client-supplied authority claim — D-041's rule); `actor ∈ {owner, runtime-agent, worker,
  model-decision}` (the closed vocabulary); every row carries stable identity (the ids adapter)
  and provenance (`run_id`/`input_hash`-shaped fields per entity); cross-owner reads/writes are
  refused at the DB (RLS) AND at the command boundary — never only in the UI.
- **Pre-registered test paths:** the two-owner matrix (A cannot read/write B's objects by id
  guess, list, or reference); hostile ids/refs (cross-owner Highlight referencing B's Source);
  the independent `arv_read` audit read confirming the stored owner/actor; an agent actor
  carrying only the owner's authorization never widening scope (P3-01/04's cases; P4-E's
  agent matrix extends).
- **User validation scenario:** two owners import and capture independently; neither ever sees
  the other's material through any command or search; an audit read shows who created what.
- **Proof-path class:** the authorization matrix at the real boundary + the independent read.

### SYS-04 — atomic, idempotent commands

- **Requirement:** PLAN.md SYS-04 (C1).
- **Owning component:** the command kernel (P3-K0: the canonical versioned structured request
  encoding, UUID correctness, the approved adapters) + the command registry (P3-01) + the
  0003 migration's ledger shape: `(owner_scope, idempotency_key)` PK, `body_hash`, `result_ref`.
- **Interfaces:** same key + same canonical body → the SAME recorded result (the replay
  answer); same key + different canonical body → the named conflict `ARV-CMD-409`, no effect;
  concurrent same-key → the recorded result OR a typed retryable in-flight state (a unique
  constraint is not a replay promise — P3-K0's explicit concurrency semantics); a command's
  effect and its command-log row commit atomically (one transaction, one commit point).
- **Pre-registered test paths:** the separator-collision/Unicode/boundary encoding cases; the
  sequential + CONCURRENT same-key replay; the key/body conflict; crash at each transactional
  boundary → zero-or-one effect, never partial; the direct-DB-escape and ambient-clock/ID
  refusals (P3-K0 + P3-01's RED set).
- **User validation scenario:** the owner double-clicks capture on a flaky connection; exactly
  one highlight exists afterward, and the client shows one result — never two, never zero
  after an acknowledgment.
- **Proof-path class:** crash/concurrency-injected proof with the independent count+content
  read.

### SYS-05 — Highlight identity and the version-bound Anchor

- **Requirement:** PLAN.md SYS-05 (C1, C5).
- **Owning component:** the Anchor contract (P3-03) + Highlight (P3-04).
- **Interfaces:** an Anchor stores (a) the Source-version id it was created against, (b)
  format-appropriate location evidence, and (c) fallback matching evidence sufficient to
  DETECT drift/ambiguity; resolution returns `{resolved, unresolved, ambiguous}` — a typed
  state, never a nearest-match guess; re-import/re-extraction/new-edition NEVER silently moves
  an Anchor (the wrong-source-version anchor is refused at the command boundary).
- **Pre-registered test paths:** the anchor submitted against the wrong Source version →
  refused; cosmetic re-save/re-extraction → resolution holds or reports the typed state; the
  changed-edition case → `unresolved`/`ambiguous`, the original evidence preserved; SYS-05's
  cross-source/new-edition/re-extraction matrix (P3-03/04).
- **User validation scenario:** the owner reopens a highlight months later, after a re-import;
  it either lands on the same passage or the UI shows an explicit "cannot locate — the source
  changed" state — never a plausible-but-wrong location.
- **Proof-path class:** the location-fidelity corpus (Q8-synthetic by default) with the
  typed-state discriminators.

### SYS-06 — explicit, recoverable import/extraction states

- **Requirement:** PLAN.md SYS-06 (C1).
- **Owning component:** the intake state machine (P3-02) + the extraction generations
  (P3-03) + the staging/blob boundary (Q12-neutral, §4.4).
- **Interfaces:** every import resolves to exactly one documented state — `complete`,
  `queued/retryable`, or `failed` (with the named reason); staging/upload and metadata commit
  are SEPARATE failure domains (a committed Source never points at an unverified blob; an
  orphaned staging artifact never becomes a Source); extraction publishes complete generations
  or an explicit failed state — a partial generation is never presented; capture NEVER depends
  on extraction/enrichment success (the layer-2 contract).
- **Pre-registered test paths:** crash after staging/before metadata; crash during metadata
  commit; the missing/corrupt blob; restart + the unfinished-import recovery; the identical-
  bytes-twice and similar-but-distinct cases under the Q11 baseline (P3-02); invalid/empty/
  over-limit extraction inputs (P3-03).
- **User validation scenario:** the owner imports a file on a dying connection; the library
  shows either the imported work, a retryable state, or a typed failure — never a phantom
  "complete" item that cannot be opened.
- **Proof-path class:** crash injection at each durable transition + the recovery walk.

### SYS-07 — rebuildable derived state with provenance

- **Requirement:** PLAN.md SYS-07 (C1, C3, C5).
- **Owning component:** the extraction generations (P3-03) + the keyword index (P3-07); the
  derived-state rule (§2.9) governs all later derived layers.
- **Interfaces:** every derived generation carries (input version, extractor/indexer version +
  config, input digest, generation state, timestamps); derived state is disposable/rebuildable
  from authoritative state; index failure NEVER blocks or corrupts capture (independent
  failure domains); stale generations cannot masquerade as current (the generation state is
  queried, not assumed); no unique authored content exists only in derived state.
- **Pre-registered test paths:** delete the index → rebuild from authoritative rows → the
  known expected result set returns; stale-terms after revision; tombstone/purge filtering;
  the index-outage capture path (capture succeeds while search is down); the extraction-
  crash → previous complete generation preserved (P3-03/07).
- **User validation scenario:** the owner's search returns exactly the committed captures it
  should; after an index rebuild (or a provider outage), nothing authored was lost and search
  returns to the same answers.
- **Proof-path class:** delete-and-rebuild equality + the independence proof.

### SYS-08 — explicit, idempotent, crash-recoverable sync

- **Requirement:** PLAN.md SYS-08 (C1).
- **Owning component:** the local outbox (P3-08) + the server application path (the SAME
  command/idempotency kernel — one command core, two execution sites).
- **Interfaces:** the local authoritative mutation and its outbox intent commit ATOMICALLY
  (one local transaction); outbox states `{pending, delivered, acknowledged, retryable,
  failed, uncertain}`; a timeout after possible server commit stays `uncertain` until
  queried/replayed — never silently failed or assumed successful; delivery is idempotent (the
  server replays by the same key semantics); competing authored revisions are PRESERVED (no
  last-write-wins for authored content — the current-view rule is explicit and documented);
  NO cross-store atomicity is claimed (D-032/Q12's boundary: local and cloud are separate
  durability domains bridged by the outbox, never one transaction).
- **Pre-registered test paths:** offline capture; restart before delivery; duplicate and
  out-of-order delivery; uncertain-ACK; server outage; local/remote mismatch; the
  death-immediately-before/after-ACK-update cases; the independent remote read + the
  event/revision count-and-content equality; replay-never-duplicates (P3-08's matrix).
- **User validation scenario:** the owner works offline all day; every capture survives
  locally with an honest "queued" state, syncs exactly once when reconnected, and the server
  ends with the same set the local journal shows — no duplicates, no losses.
- **Proof-path class:** the declared fault matrix end-to-end with the independent remote read.

### SYS-09 — the real client path

- **Requirement:** PLAN.md SYS-09 (C1, C2).
- **Owning component:** the product API (P3-01 onward) + the contract client (the CLI —
  GLOSSARY's boundary: a contract client, never the reader UI; the UI is the separate client
  repo, exercised at P4-B).
- **Interfaces:** the supported initial client path creates and retrieves captures through the
  REAL backend boundary (authenticated, owner-scoped, the same command core); mock-only tests
  are never acceptance evidence for this row; the API surface is the SAME one a later agent
  adapter wraps (one authorized API core — D-039(5)).
- **Pre-registered test paths:** the §1.6 capture checkpoint (import → persist identity →
  highlight with version-tied anchor → lost-ack → restart/retry → exactly-one-effect →
  authenticated retrieval → independent read) through the real API + real DB (P3-01, extended
  by each slice's integration case).
- **User validation scenario:** a fresh agent, given only the repo and the contract client,
  completes the capture-and-retrieve workflow on a real running backend — the cold-start proof
  form applied to the product path.
- **Proof-path class:** the real-stack integration run (never a mock), observed by an
  independent reader.

### SYS-10 — versioned export/restore with purge permanence

- **Requirement:** PLAN.md SYS-10 (C1, C5).
- **Owning component:** the export manifest + restore validator + the rebuilders (P3-09).
- **Interfaces:** export = authoritative records + blob references + revision history + the
  governed purge/retention state, under an explicit versioned manifest; restore validates
  references and blob availability BEFORE declaring completion; derived indexes rebuild from
  the restored authoritative state. **The purge-ledger reconciliation rule (#78's round-1
  Major, adopted):** the purge ledger is owner-scoped authoritative state maintained OUTSIDE
  any single archive; restore RECONCILES the archive's content against the destination's
  CURRENT purge ledger before declaring completion — a current-ledger entry WINS over older
  archive content (an export made before a purge cannot resurrect the purged item into a
  destination that carries the purge). **The no-ledger path is FAIL-CLOSED (#78 round 3): it requires a POSITIVE absence
  determination — the destination's ledger store must affirmatively answer that no ledger
  exists; a read error, timeout, or outage is a typed NON-RESTORING outcome naming the
  reason, never a silent downgrade to the archive-only path (an unreadable ledger is not
  an absent ledger — the honest-state rule of §3's preamble). Bound to the owner's LOCKED
  default (D-029 — "documented backup expiry, purge ledger applied on restore"):** a
  genuinely clean destination (no live ledger anywhere — the archive is the only surviving
  owner state, the disaster-recovery case) does NOT silently claim purge-safety: the restore
  completes as an EXPLICITLY scoped owner action whose typed completion state names (a) the
  adopted ledger's as-of time, (b) the documented backup-expiry window that bounds the
  archive's validity (D-029's own mechanism — an archive past its expiry window is not a
  restore source), and (c) the residual, stated in the open: a purge recorded after the
  archive's as-of time, in a ledger that no longer exists, can return in this path — the
  resurrection is OBSERVABLE, ATTRIBUTABLE, and re-purgeable (the restore event itself is
  recorded in the new ledger), never silent; partial/malformed/interrupted restores fail safely (no half-restored "complete"
  library).
- **Pre-registered test paths:** clean restore + the canonical authoritative-state hash
  comparison (the documented equality rule); repeated restore; missing blob; malformed/
  interrupted archive; corrupt index → rebuild; purge-then-restore; migration from a declared
  prior schema (P3-09).
- **User validation scenario:** the owner moves to a new machine, restores, and finds every
  capture, note, and revision — and the item they deliberately purged is still gone.
- **Proof-path class:** the equality contract on content (never row counts — A08's oracle
  rule) + the purge-invalidation proof.

### SYS-11 — per-slice V-model trace and independent SEV

- **Requirement:** PLAN.md SYS-11 (C1–C5).
- **Owning component:** the SEV protocol (LAW-30, live since H-02: the gate-enforced record +
  the fresh-context reviewer + the separate phase-gate grader) + this RTM (the trace home).
- **Interfaces:** every implementation slice cites its SYS rows (≤3 per card, LAW-05), carries
  its Proof Sheet + run records + the gate's green, its sev.json binding the reviewed diff,
  and the fresh-context review's findings with dispositions; a defect that invalidates an
  earlier gate reopens that gate.
- **Pre-registered test paths:** the standing machinery (ARV-SEV-001..008, the KB matrix 31
  cases, the trusted leg) — live and enforced per PR; the phase exit gates run the independent
  grader over THIS matrix's rows.
- **User validation scenario:** at the Phase 3 exit gate, an independent grader walks every
  SYS row of this matrix to its tests, proof, and SEV — no row passes by implication.
- **Proof-path class:** the gate-path known-bads + the grader's walk (the phase-gate evidence).

## 2. The authoritative entity contracts (Phase 3)

Conventions common to every authoritative table (the 0002/0003 substrate, extended): `id`
UUID PK with NO default (the ids adapter supplies it — LAW-24; the version/variant/timestamp
correctness is P3-K0's acceptance); `owner_scope` NOT NULL server-derived; `actor` NOT NULL in
the closed vocabulary; `created_at` TIMESTAMPTZ NOT NULL with NO default (the clock adapter);
provenance fields (`run_id`/`input_hash`-shaped) NOT NULL; append-only enforced by named
triggers; RLS by `app.current_owner` with `arv_read` as the independent auditor. Revisions are
new rows; tombstones are typed events; purge is owner-governed (D-011) and audited.

1. **Work** (P3-02): the logical library item. Identity: a UUID with NO uniqueness constraint
   on title/filename/content (the Q11 baseline — no auto-merge under this freeze; owner ratification
   is the only change path). Fields: display title
   (owner-editable via revision), created/provenance, owner. Two Works may reference identical
   bytes as separate Sources; byte-reuse is storage-level, never identity-level.
2. **Source** (P3-02): a specific imported version/edition/acquisition instance of a Work.
   Fields: work_id, content digest (sha256 of the exact imported bytes), media type, byte
   size, acquisition metadata (when, via what channel, actor), the blob reference (§4.4),
   the import state, and `source_version` — a new edition/re-import is a NEW Source row
   (never a mutation of the old); which Source is "current" for a Work is a documented
   current-view pointer, never a destructive update.
3. **ExtractionGeneration** (P3-03, DERIVED): the versioned derived passages of one Source
   version. Fields: source_id, extractor name+version+config, input digest, generation
   state (`building|current|superseded|failed`), timestamps. Publishes complete-or-failed
   (SYS-06/07). Never authoritative (§2.9).
4. **Anchor** (P3-03): the durable pointer INTO a specific Source version. Fields:
   source_id (the version it was created against), the format-appropriate location evidence
   (per media type — passage id, offset range, or the format's own locator), the fallback
   matching evidence (the selected text + context for drift detection), media-type tag.
   Resolution is a typed query: `resolved | unresolved | ambiguous` (SYS-05). An Anchor
   never references a different Source version than it was created against.
5. **Highlight** (P3-04): the committed selected text. Identity: a stable UUID + append-only
   immutable revisions. Revision fields: selected content, source_id, anchor_id, owner/actor,
   command provenance (the command-log row), input digest, created_at. State transitions (§3.3 governs):
   edit appends a new revision row (the entity stays active); delete → tombstoned (a typed event;
   hidden from normal retrieval, history retained); → [governed purge only]. The free-text quote words ride the
   content (D-030: no tag/classification system).
6. **Bookmark** (P3-05): the stable return location. Identity + the source-versioned
   Anchor/location reference; NO copy of source content. Behavior on re-import/re-extraction/
   new-edition/purge is the typed resolution contract (SYS-05's states), never duplication.
7. **Note** (P3-06): the owner's deep raw thinking. Identity + immutable revisions; explicit,
   version-aware references to Work/Source/Anchor/Highlight/Note; long-form and Unicode
   preserved losslessly; the diagram/structured-block serialization contract is NOT frozen
   here (it requires its own round-trip proof before being called supported — P4-C's
   reservation).
8. **CommandLog** (landed, 0003 — the migration is the authority; this row is abridged): the
   idempotency ledger — `(owner_scope, idempotency_key)`
   PK, body_hash, result_ref, actor, created_at; append-only (SYS-04).
9. **The derived-state rule (authoritative vs derived):** authoritative = everything an
   owner would call their data (Work, Source, Highlight/Bookmark/Note revisions, tombstone/
   purge events, the command log, the outbox state). Derived = extraction generations,
   keyword (and later semantic) indexes, rankings, context packs, relationship candidates.
   Derived rows carry their full processing lineage and are disposable; NO unique authored
   content exists only in derived state (SYS-07); a "current" view may be a projection, but
   the authoritative rows are always the recovery substrate.
10. **Phase 4 reservations (identity/ownership/revision shape only):** **JournalBlock** — a
    revisioned writing unit, source-optional; **@Reference** — a stable-identity reference
    with version-aware resolution states and privacy-preserving refusal (never revealing
    another owner's object existence); **ReadingSession checkpoints** — behavior events
    inside the D-010 boundary. Their interface freeze is P4-00's, never claimed here.

## 3. The seven state machines

Honest-state rule: every machine's states are EXCLUSIVE, OBSERVABLE (an independent read can
name the state), and FAIL-CLOSED (an unknown/indecidable state is a named refusal, never a
guess). The machines below are the freeze; per-slice tests pre-register the transition cases.

### 3.1 Import (Work/Source intake — P3-02)

```
(nonexistent) --request--> staging
staging --blob verified--> staging_verified     [the digest computed; the blob readable]
staging --blob absent/corrupt--> failed          [named reason; the staging artifact cleaned]
staging --crash--> staging                       [recovery re-walks; no phantom Source]
staging_verified --metadata commit--> complete   [the Source row + blob ref committed atomically]
staging_verified --commit crash--> staging_verified [zero-or-one effect; the recovery walk re-drives]
staging_verified --invalid metadata--> failed    [named reason]
complete --re-import (same bytes)--> complete    [a NEW Source row per the Q11 baseline; the old stays]
```

### 3.2 Capture (Highlight/Bookmark/Note — P3-04/05/06)

```
(nonexistent) --command--> in_flight            [no persistence promise yet]
in_flight --local commit--> local_durable       [the revision + command-log row committed]
in_flight --validation refusal--> failed        [named code; no effect]
in_flight --crash before commit--> (no effect)  [the retry is a fresh command by the same key semantics]
local_durable --outbox enqueue--> queued        [sync intent recorded; the same local transaction]
queued --server ack--> server_durable           [independently read-confirmed]
queued --timeout after possible commit--> uncertain [until replay/query resolves — SYS-08]
uncertain --query resolves--> server_durable | queued [the typed resolution; never an assumption]
queued --server refusal (conflict)--> conflicted [inputs preserved; typed conflict behavior; no LWW]
```

### 3.3 Revision / tombstone / purge (authored entities — P3-04/06)

```
active --edit--> active(revision n+1)           [the prior revision immutable; history complete]
active --delete request--> tombstoned           [hidden from normal retrieval; recoverable]
tombstoned --restore--> active(current revision unchanged)
tombstoned --governed purge--> purged           [owner-only (D-011); minimal audit row; final]
purged --restore attempt--> refused             [the purge ledger applies; no resurrection (SYS-10)]
```

### 3.4 Local outbox (P3-08)

```
(empty) --local commit (same transaction as the mutation)--> pending
pending --delivery attempt--> delivered         [the server may have applied it]
delivered --server acknowledgment--> acknowledged
delivered --timeout/lost response--> uncertain  [replay by the SAME idempotency key resolves it]
pending/delivered/uncertain --retryable failure--> retryable   [named reason; backoff]
retryable --terminal failure policy--> failed   [visible; the local mutation remains local-durable]
uncertain --replay/query--> acknowledged | retryable
```

### 3.5 Server sync application (the server side — P3-08)

The server applies a delivered command through the SAME command kernel and idempotency
semantics as a direct API call (one command core): an unknown key → apply; a known key +
same body → the recorded result (no duplicate logical effect); a known key + different body
→ `ARV-CMD-409` surfaced as the delivery's typed conflict. No authored-content LWW: competing
revisions both persist; the current-view rule (latest revision wins per entity, documented)
is a projection, never a destruction.

### 3.6 Indexing (the keyword index — P3-07; the pattern for every later derived index)

```
(empty) --build job--> building
building --complete generation--> current       [the generation row: input version, indexer
                                                 version+config, input digest, timestamps]
building --crash/failure--> failed              [named reason; the previous generation stays current]
current --authoritative change--> stale         [detected by input version; never masquerading as current]
stale --rebuild--> building
current/stale/failed --purge of the source material--> invalidated   [purge invalidates derived copies]
any --delete + rebuild from authoritative rows--> the known expected result set (SYS-07's equality)
```

### 3.7 Export / restore (P3-09)

```
(live library) --export--> manifest_complete    [versioned; authoritative + blob refs + history +
                                                  purge state; the canonical hash computed]
manifest_complete --restore into clean destination--> restored_pending_validation
restored_pending_validation --references+blobs valid--> restored   [equality contract holds;
                                                 the purge-ledger reconciliation ran FIRST:
                                                 the destination's current ledger wins over
                                                 older archive content (SYS-10's rule)]
restored_pending_validation --missing blob/malformed/interrupted--> failed [safely; nothing half-complete]
restored_pending_validation --ledger unreadable (error/timeout/outage)--> failed [FAIL-CLOSED: a
                                                 typed non-restoring outcome naming the reason — an
                                                 unreadable ledger is never treated as absent]
restored --rebuild derived--> fully_operational [indexes rebuilt from the restored authoritative state]
```

## 4. Transaction and acknowledgment semantics (frozen)

1. **Commit-before-acknowledgment** (D-041's rule): a command's success response is emitted
   only after the declared commit point; a lost acknowledgment leaves the outcome UNCERTAIN
   until replay/query resolves it — the client never assumes failure or success.
2. **One commit point per command**: the effect rows + the command-log row (+ the outbox row,
   when local) commit in ONE transaction. No multi-store transaction is ever claimed
   (Q12/D-032): local and cloud durability are bridged by the outbox, not by a distributed
   transaction.
3. **The write-side acknowledgment vocabulary** (SYS-01's frozen set — the states a write
   acknowledgment may name; the canonical five-rung durability LADDER in GLOSSARY/NORTH-STAR
   governs claimable findability and is unchanged by this set): `in_flight` (no promise) →
   `local_durable` (the local authoritative commit) → `queued`/`retryable` (sync intent
   recorded) → `server_durable` (independently read-confirmed on the server). The derived
   findability rungs (`keyword-searchable`, later `semantically indexed`, `linked`) are
   generation states of derived systems — reported by their own queries, never by the write
   acknowledgment.
4. **The blob boundary (Q12-neutral)**: source bytes live in a content-addressed blob store
   behind an adapter interface `{put(bytes) → digest, get(digest) → bytes, delete(digest),
   exists(digest)}`; the Source row stores the digest + size + media type, NEVER the bytes.
   Staging is a separate failure domain: a Source commits only after its blob is verified
   readable and digest-matched; orphaned staging artifacts are cleaned by the recovery walk
   (never promoted). No provider name, no signed-access detail, no cross-store atomicity
   claim enters the schema (§7.4).

## 5. Migration and compatibility plan (frozen)

- The harness migration machinery (forward-only, versioned, checksummed, the M0 oracle's
  fail-closed grammar) is the ONLY schema change path; the current state is `0001..0003`
  (baseline, evidence_event, command_log).
- Phase 3 product migrations (P3-02 onward) extend the substrate conventions (§2) — each
  product table lands in its slice with its tests, never a big-bang schema.
- Forward compatibility: persisted IDs are never rewritten without an explicit compatibility
  decision (P3-K0); a migration from any declared prior schema version is part of P3-09's
  acceptance; the export manifest's version is the cross-version contract (SYS-10).
- The pre-freeze rule (the P3-00 gate): NO product schema migration lands before this freeze
  is accepted; after acceptance, every migration cites the RTM section that freezes its
  shape.

## 6. The failure-behavior matrix (named outcomes, frozen vocabulary)

| Named failure | Typed outcome (the client sees) | Never |
|---|---|---|
| `ARV-CMD-409` key/body conflict | the named conflict; zero effect | silent overwrite |
| uncertain ACK (timeout after possible commit) | `uncertain` + the replay resolution | assumed success/failure |
| validation refusal (missing owner/actor/provenance, invalid scope) | the named refusal code; zero effect | a partial write |
| an Anchor referencing a Source version it was not created against (the wrong-version/dangling class) | REFUSED at the command boundary (a validation failure, SYS-05's first clause) | accepted into the store |
| an Anchor that cannot be re-resolved WITHIN its own Source version (drift/ambiguity) | `unresolved`/`ambiguous` (the typed resolution states) | nearest-match retarget |
| blob absent/corrupt at verify | `failed` (named); staging cleaned | a complete Source without bytes |
| extraction crash/invalid input | the previous generation stays; the failed generation named | a partial generation as current |
| index outage | capture unaffected; search reports honestly | capture blocked by derived failure |
| sync conflict (competing revisions) | `conflicted`; both inputs preserved | last-write-wins destruction |
| purge/restore interaction | the destination's current purge ledger wins over older archive content; the no-ledger path is FAIL-CLOSED (a positive absence determination required; an unreadable ledger is a typed non-restoring outcome, never treated as absent) and the disaster path completes as an explicitly scoped owner action (the typed state names the ledger as-of time + the D-029 backup-expiry window + the stated residual; the restore event recorded in the new ledger) | silent resurrection (an export predating a purge re-importing the purged item into a ledger-carrying destination; or a no-ledger restore claiming purge-safety it cannot know) |
| cross-owner access | refused at command AND DB boundary | existence leakage |

## 7. The open-question boundary register (exact scopes)

The authoritative register is `/DECISIONS.md` (VER-504's mirrors: DECISIONS/EXECUTION/PLAN/
STATE). This section records each question's EXACT boundary against this freeze — what is
frozen AROUND it and what it blocks. No question is closed or narrowed here.

### 7.1 D-014 (calculation engine scope)
Blocks math-workflow design only. No Phase 3 contract depends on it.

### 7.2 Q6 (research-transcript status)
Blocks the Part-2 acceptance-scenario finalization + the S5 corpus only. The general owner
workflow (§1's validation scenarios) never waits on it.

### 7.2b Q7 (semantic-spike budget)
Blocks paid/selected semantic work only (Phase 5's S6); the deterministic fixtures,
evaluator, and options preparation proceed. No Phase 3 contract depends on it.

### 7.3 Q8 (extraction-spike corpus)
The registered default is synthetic. The P3-03 anchor-stability spike runs on the synthetic
corpus; any real-PDF/EPUB location-stability CLAIM requires a named, permitted, real corpus
and measured results — absent that, the freeze claims only synthetic-corpus fidelity.
OCR/scanned content is a distinct capability, never implied by "PDF support".

### 7.4 Q12 (blob backend, staging lifecycle, cross-store recovery) — the comparison
The freeze (§4.4) is provider-neutral. Per PLAN's P3-00 review element, the options compared
(evidence-preparation for the owner's gate, NEVER a ratification):

| Criterion | Supabase Storage (the D-032-consistent option) | S3-compatible third party | DB bytea blobs |
|---|---|---|---|
| Deployment fit | Same platform as the DB (D-032: hosted Supabase, cloud + local synced) — one operator surface | Second vendor/credential domain | No second store at all |
| Durability/backup | Platform-managed with the project's backup story | Vendor SLA; separate from the DB backup | Inherits the DB backup exactly |
| Content identity | Object keys can be the content digest (content-addressed, §4.4) | Same | Same |
| Offline operation | Local staging + the outbox bridge (no cross-store claim) | Same | The DB sync covers it (but large blobs stress WAL/replication) |
| Upload completion | Named completion semantics; staged verify before commit (§3.1) | Multipart complexity owned by the adapter | Transactional (but the blob/row size ceiling is real) |
| Signed access | Platform-native | Presigned URLs | Via the API only |
| Purge/restore integration | One platform's lifecycle | Two vendors to align | One |
| Orphan cleanup | The recovery walk (§3.1) over the platform listing | Same | Same |
| Local/cloud recovery | The outbox + digest verification (§4.4) | Same | DB-level, but bytea bloats the replication path |

**Recommendation (for the owner's ratification, not adopted here):** Supabase Storage as the
blob backend — consistent with D-032, one operator surface, content-addressed keys, and the
provider-neutral adapter (§4.4) already isolates the choice. The byte sizes (readable text
documents) are far below the ceilings that would justify bytea. **Nothing in the frozen
contracts changes under either alternative** — that is the point of the neutral boundary.

### 7.5 Q11 (Work/Source identity)
The frozen baseline: no auto-merge; no identity-dependent uniqueness constraints; byte-reuse
is storage-level, never identity-level (§2.1/2.2). P3-02 implements exactly this baseline. An
identity policy beyond it (duplicate detection as a feature, identity uniqueness) is owner
work; until ratified, NOTHING in Phase 3 depends on it.

## 8. The P3 slice acceptance trace (which rows each slice closes)

| Slice | Closes (RTM rows) | Its own acceptance adds |
|---|---|---|
| P3-M0 | (the migration oracle — §5's machinery) | the fail-closed grammar; zero-effects proofs; bidirectional history |
| P3-K0 | SYS-04 (the kernel half) | the encoding/UUID/adapter/concurrency primitives |
| P3-01 | SYS-03, SYS-04, SYS-09 (primary; SYS-11 is the standing per-slice protocol for EVERY card, never a per-card closure row) | the §1.6 capture checkpoint end-to-end |
| P3-02 | SYS-06, SYS-03 | the import state machine + the Q11 baseline |
| P3-03 | SYS-05, SYS-06, SYS-07 | the Anchor contract + the Q8 spike |
| P3-04 | SYS-01, SYS-02, SYS-05 (primary; SYS-03's matrix re-exercised, its closure row stays P3-01's) | Highlight + the revision/tombstone machine |
| P3-05 | SYS-01, SYS-05 | Bookmark + the typed resolution |
| P3-06 | SYS-02, SYS-03 | Note + the revision history |
| P3-07 | SYS-07 | the rebuildable keyword index |
| P3-08 | SYS-01, SYS-08 | the outbox + the sync fault matrix |
| P3-09 | SYS-10 (+ SYS-02/07's purge/rebuild coupling) | the export/restore equality + purge permanence |
| Phase 3 exit gate | ALL rows | the independent grader's walk of this matrix |
