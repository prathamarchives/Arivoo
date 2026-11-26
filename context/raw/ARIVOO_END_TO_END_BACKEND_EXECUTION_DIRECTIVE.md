# ARIVOO — End-to-End Backend Execution Directive

**Purpose:** Resume from the current merged repository state and execute continuously toward a complete, deployed, frontend-ready Arivo backend, including REST API, MCP, PostgreSQL, authentication, storage, workers, synchronization, domain routing, HTTPS, operations and final system acceptance.

**Repository:** `https://github.com/prathamarchives/Arivoo`  
**Current verified main SHA at directive creation:** `1eab74a132c36c5d2d32fce74030ecb90ae6e571`  
**Supabase project:** `arivo` / `wcuuakhdmsmmxagvbdmg` / `ap-south-1`  
**Canonical public API hostname selected by owner:** `https://arivo.itscatalyst.com`  
**Canonical REST base:** `https://arivo.itscatalyst.com/api/v1`  
**Proposed remote MCP endpoint:** `https://arivo.itscatalyst.com/mcp` (thin transport adapter; preserve the existing read-only MCP tool registry)

---

# 1. Mission — finish the system, not another plan

Take the existing Arivo backend from its current domain kernel, local test harness, authenticated API skeleton and first source/import routes to a complete, secure, deployed, frontend-ready backend.

The owner explicitly wants execution to move quickly and continuously. Do not stop after every file, small edit, or individual command to produce another plan or request approval. Work through the remaining implementation in ordered, coherent batches. Make reasonable engineering decisions inside already adopted contracts. Do not turn ordinary engineering choices into repeated owner questions.

Do not merely prepare a roadmap. Implement the work, commit it, open and complete the required PR process, continue to the next workstream, and keep the repository resumable after every session boundary.

The desired result is a backend that a separate Arivo desktop frontend can consume through stable HTTPS API contracts, while authorized agents can access the same underlying application data through the read-only MCP surface.

## 1.1 Product intent

Arivo is the owner's personal reading, study, research, annotation, note-taking and journal environment. The owner imports books, papers and other readable sources; reads and studies them; highlights passages; bookmarks locations; writes notes that preserve raw thinking; journals; organizes a library and reading lists; links related items; and finds everything again through retrieval.

The backend must make that workflow dependable, low-friction and recoverable. It must preserve source bytes and authored content, distinguish authoritative content from derived extraction/index data, and provide truthful status for every write.

## 1.2 Absolute scope boundary

Arivo is a standalone product.

**Do not integrate Graphiti, Kev, the owner's separate ecosystem memory engine, personal agent infrastructure, unrelated software databases, or any external knowledge-base service into Arivo.** These are not Arivo components or dependencies. Do not add their endpoints, secrets, schemas, jobs, data models, credentials or runtime requirements.

Do not add an LLM provider or model key to the Arivo backend. Semantic/model work remains governed by its own open decision.

The Arivo reader UI lives in a separate repository. This repository is the backend and contract surface. Do not build the desktop UI here. Make the backend complete and frontend-ready, and use a thin integration client for acceptance.

---

# 2. Current verified continuation point

This is a snapshot. Re-fetch live GitHub and Supabase state at session start; do not assume nothing has changed.

## 2.1 GitHub

- Repository: `prathamarchives/Arivoo`.
- Default branch: `main`.
- Main SHA observed: `1eab74a132c36c5d2d32fce74030ecb90ae6e571`.
- PR #135 (CLAIM-094 sources/import API routes) is merged at `f38a0e13`.
- PR #136 (CLAIM-094B post-merge reconciliation and venv-less harness-suites repair) is merged at `1eab74a`.
- PR #136's merge-commit workflow has all five required checks green: `canonical-layer`, `head-tools`, `harness`, `harness-suites`, `harness-trusted`.
- No open PRs were returned by the latest repository search.

Links:
- PR #135: `https://github.com/prathamarchives/Arivoo/pull/135`
- PR #136: `https://github.com/prathamarchives/Arivoo/pull/136`
- Main: `https://github.com/prathamarchives/Arivoo/tree/main`

## 2.2 Immediate repository drift to repair

The live merged state has advanced, but `CLAIMS.md` still lists CLAIM-094B as OPEN and `STATE.md` still identifies CLAIM-094B's PR as the exact next action. PR #136 is already merged. This is stale post-merge bookkeeping.

First action:
1. Confirm PR #136's merged SHA and five successful checks from GitHub.
2. Follow CLAIM registry rule 4 and append CLAIM-094B's closed row; never rewrite the open/history row.
3. Re-derive `STATE.md` from live GitHub facts and the current ledger maxima.
4. Append the required WORKLOG/session continuation record under the canonical format.
5. Confirm CLAIM-094B is no longer open and no merged claim remains accidentally open.
6. Do not create a new PR merely for status narration if the repository's canonical procedure permits the close/re-derivation to ride with the next bounded claim. Make the state correct before meaningful implementation continues.

The latest canonical next action is CLAIM-095 (extraction/readiness routes), plus the previously routed F6 kernel defect (long unbroken tokenizer input can exceed the PostgreSQL keyword-index btree row limit). Verify current claim and INTENT maxima before reserving IDs; the last observed intent is INT-161 and the last claim is CLAIM-094B.

## 2.3 Supabase — freshly checked in this session

- Project name: `arivo`.
- Project ref: `wcuuakhdmsmmxagvbdmg`.
- Region: `ap-south-1` (Mumbai).
- Status: `ACTIVE_HEALTHY`.
- PostgreSQL: `17.12.0.000`.
- A direct read of `arv.schema_migrations` returned versions **1 through 19 only**.
- `0020_search_path_pins.sql` remains unapplied remotely at the time of this check.

Dashboard: `https://supabase.com/dashboard/project/wcuuakhdmsmmxagvbdmg`.

Use the repository's guarded migration runner and its canonical `harness/migrations/` chain. Do not create a second Supabase migration history and do not apply SQL manually as a shortcut.

## 2.4 Implemented backend foundations

The repository already has a mature domain kernel and real PostgreSQL harness:

- `harness/commands.py`: transactional/idempotent write kernel, durability and acknowledgment contract, typed `ARV-*` errors.
- `harness/query.py`: owner-scoped read kernel, bounded paging and retrieval/context pack surfaces.
- `harness/migrations/` and `harness/migrate.py`: one canonical checksummed, forward-only migration history.
- `harness/adapters/pg.py`: local/test database boundary with loopback-only protection.
- `harness/adapters/pgprod.py`: pooled production PostgreSQL adapter, TLS verification, least-privilege `arv_app`, transaction-local owner context.
- `harness/api/`: FastAPI composition, ES256/JWKS authentication and first source/import routes.
- Existing Source/Work, import/recovery, extraction generations, passages, Anchors, highlights, bookmarks, notes/revisions, reading positions/sessions, journal blocks, reading lists, references, keyword search, client/server outboxes, export/restore/purge and derived-state recovery.
- `harness/mcp.py`: read-only MCP JSON-RPC stdio server using the existing query kernel; its adopted registry is 22 read tools.

CLAIM-094 added:
- `POST /api/v1/imports`
- `GET /api/v1/sources`
- `GET /api/v1/sources/{id}`

CLAIM-094's 29-check route battery and SEV were merged. CLAIM-094B repaired the merge-time venv-less suite degradation and closed the 094/089 bookkeeping records. Preserve this work; do not rebuild it.

## 2.5 Current open owner questions

The current `STATE.md` lists D-014 and Q6–Q12, Q16–Q19. These block only their named scopes, not the whole project.

Important for this directive:
- Q7: semantic budget/model choice. Do not incur paid model calls or install vector infrastructure without its decision.
- Q8: extraction real-document corpus. Synthetic corpus remains the default; do not claim real-PDF/EPUB stability without owner-authorized corpus work.
- Q11: Work/Source identity. Keep the current baseline: no automatic logical merging and no identity uniqueness policy until ratified.
- Q12/Q17: blob provider and cross-store staging/recovery contract. Provider-neutral work proceeds; provider-specific source/blob schema and durability promises remain owner-gated.
- Q18: compute/deployment runtime. The owner has now selected the public hostname and Cloudflare DNS/edge direction, but has NOT selected or approved a compute platform. Do not resurrect Railway as a default.
- Q19: desktop local-store contract. Backend/API work is not blocked; the actual desktop integration must respect the owner-approved contract.
- D-014: math-specific scope only; it does not block reading/capture/backend work.

---

# 3. The owner has changed the execution style: batch intelligently, do not verify every keystroke

The owner explicitly requests that the agent stop wasting time on repeated verification after every tiny step and execute one coherent workstream after another until the backend end state is reached.

Apply this exactly, while preserving the repository's non-negotiable governance and security rules.

## 3.1 What to stop doing

- Do not run `make verify`, the full test suite, every isolation check, every proof generator and a fresh SEV review after every individual file edit.
- Do not pause after every small implementation subtask to produce another long status report.
- Do not repeatedly re-read the same unchanged files or re-run identical successful tests without a failure or changed code.
- Do not create a separate claim/PR for every trivial endpoint when several endpoints form one coherent domain slice and fit the repository's size/scope laws.
- Do not ask the owner for decisions already settled in the repo or ordinary implementation decisions inside adopted architecture.
- Do not stop an entire wave because one narrow owner gate blocks one provider-specific action.
- Do not spend time producing plans for work that can be implemented now.

## 3.2 What remains mandatory

The repository's `AGENTS.md`, `LAWS.md` and adopted decisions remain binding. In particular:
- Claim-before-work and scope exclusivity.
- One coherent bounded claim/branch/PR at a time.
- The independent systems-engineering verification required after an implementation slice (LAW-30).
- The D-042 reasoned PR review and disposition of all review findings before merge.
- The five required CI checks on the exact PR head.
- Canonical-layer and repository verification where required.
- Post-merge claim closure and state reconciliation.

Do not weaken these laws or alter CI to make the process appear faster.

## 3.3 Efficient verification cadence

Use this cadence:

**During implementation:** run the smallest focused test only when needed to diagnose a failure or check a critical local behavior. Do not run the entire system battery after every edit. Batch related implementation changes before the next broad verification pass.

**At the end of one coherent claim/PR:** run its targeted test suite once, then the repository's required integrated verification once, then produce one SEV over the final diff. Assemble the run records and proof sheet from actual runs. Open the PR. Let the five required CI checks run at the exact final PR head. Do not re-run tests that have not been affected by subsequent changes.

**After merge:** observe the merge SHA and required checks once, close the claim, and re-derive STATE. Do not run the entire suite again merely because the PR merged if the exact merge commit already has the required green checks and the repository does not require a separate post-merge test.

**At the end of the entire backend program:** run one comprehensive V-model/system-acceptance campaign across the real Supabase project, deployed API, MCP transport, object storage, worker, desktop contract client, security boundaries, sync, backup and restore. This is the final integrated proof, not a loop repeated after each route.

If a test fails, debug with a focused test, fix the cause, and run the relevant affected suite. Re-run broad verification only when the change could affect a broad invariant or when required by the gate.

## 3.4 Larger but still bounded implementation slices

Group related work into domain/API families, not one PR per endpoint and not one giant PR for the whole backend. Use the current LAW-05 size limits and one coherent purpose per PR. Suggested route families:

1. Extraction/readiness.
2. Reader state and content serving.
3. Highlights/bookmarks.
4. Notes/journal.
5. References/reading lists.
6. Retrieval/context packs.
7. Sync/outbox transport.
8. Export/restore and recovery.

The agent may use parallel subagents only when the repository's claims clearly declare non-overlapping file scopes. Do not create competing claims or parallelize shared-file edits.

---

# 4. Target architecture and public contracts

## 4.1 Canonical REST API

The owner-selected API base is:

```text
https://arivo.itscatalyst.com/api/v1
```

The desktop client must only call this API. It must never connect directly to PostgreSQL, use the Supabase service-role key, or write product tables through the browser Data API.

The API must:
- Authenticate with Supabase-issued JWTs, validating signature, issuer, audience, expiry and signing key.
- Derive owner only from the verified identity's `sub`.
- Derive actor server-side.
- Use the existing command kernel for writes and query kernel for reads.
- Preserve idempotency, commit-before-ack, revisions/tombstones, provenance, typed errors, API version and durability ladder.
- Use the production pooled DB adapter, service-controlled DB target, TLS verify-full and transaction-local owner context.
- Provide a stable, complete OpenAPI schema and versioned DTOs.
- Use bounded pagination, upload/download limits, consistent error envelopes and rate limits.

Complete the route surface in the adopted runbook §11.2, based on actual kernel arms rather than inventing semantics:
- Sources/import.
- Extraction status/readiness and retries/rebuilds.
- Reader content/generation and reading position/session state.
- Highlights and revisions/lifecycle.
- Bookmarks and revisions/lifecycle.
- Notes and revisions/references.
- Journal blocks and revisions.
- Stable `@` references.
- Reading lists and memberships.
- Keyword search/context packs/provenance/trust.
- Sync push/pull/status/conflicts using existing outbox contracts.
- Export/restore/purge/recovery operations using existing safeguards.
- Agent credential mint/revoke operations only where the existing owner-authenticated command contract permits them.

Do not implement domain behavior in HTTP route handlers. They translate HTTP DTOs to commands/queries and translate kernel results to HTTP.

## 4.2 MCP: preserve and complete the existing product surface

The existing `harness/mcp.py` is a read-only stdio MCP server with JSON-RPC 2.0 and the adopted 22 read tools, each reusing the same query kernel. Preserve its tool names, input schemas, output contract, argv-safety and refusal behavior. Do not add write tools or a second retrieval engine.

The owner's current end-state request explicitly includes MCP as well as the REST API. Therefore add a remote MCP transport as a thin protocol adapter over the existing tool registry, unless live canonical docs reveal it has already been implemented:

```text
https://arivo.itscatalyst.com/mcp
```

Use the currently recommended MCP Streamable HTTP transport. Keep stdio support for local clients. Both transports must invoke the same 22 read tools and the same query kernel.

Remote MCP authentication must use the existing owner-minted read-only agent credential contract from migration 0019 (`arv.agent_credential`, hash-only persistence, revocation, owner-scoped reads and audit log). The cleartext token is shown once at mint and never stored/logged. Pass it through a protected header/environment channel; never in argv. Do not treat an arbitrary client `owner` field as identity.

Expose owner-authenticated mint/revoke operations through the REST API only if they can safely wrap the existing commands. MCP itself remains read-only. Do not add mutation tools just because the remote transport exists.

Cloudflare edge configuration must support the MCP transport's streaming/long-lived responses; verify that proxy buffering, timeouts and connection behavior do not break Streamable HTTP. Do not claim this works until tested against the deployed hostname.

## 4.3 Database and Supabase

Supabase is the canonical application PostgreSQL/Auth platform. Keep its app schema private and preserve RLS. The local adapter remains loopback-only. The production adapter is explicit and least privilege.

Apply migration 0020 through the guarded canonical migrator after preflight. The current live ledger contains versions 1–19. Do not apply it by hand or create a second migration chain. Independently verify the new checksum, role search_path defaults and function search_path pins after application.

Verify runtime roles cannot bypass RLS. The API/worker never run as `postgres` and never carry the migration-admin credential.

## 4.4 Storage and import

Keep the provider-neutral blob interface and local implementation. Continue provider-neutral staging/recovery design and tests immediately.

Q12/Q17 remain open for provider-specific backend and cross-store recovery. Prepare one concise recommendation comparing Supabase Storage with a Cloudflare object-store option (including signed uploads, ownership/RLS, lifecycle, costs, egress, digest verification, orphan recovery, backups and restore). Recommend the least-complex compatible default, but do not silently close the owner gate or make irreversible provider-specific schema changes without ratification.

Once approved, implement private bucket/object access, signed upload/download, server-side SHA-256 verification, explicit staged/verified/committed/failed states, safe orphan cleanup and restore/purge integration. Never claim a DB transaction and object-store upload are atomic.

## 4.5 Background jobs and worker

Build a dedicated durable job state machine. Do not repurpose the client outbox or server outbox as a generic queue.

Required behavior:
- Job ID, owner scope, type/version, validated bounded payload and idempotency key.
- Queued/leased/succeeded/retryable/terminal failure states.
- Lease expiry, atomic claim, attempts, bounded backoff, typed errors.
- Fencing token or equivalent stale-worker protection.
- Crash/restart recovery and poison-job isolation.
- Job creation in the same transaction as the authoritative DB change or durable transactional handoff.
- Owner-bound execution and observable job status.

Initial job types: extraction, keyword-index rebuild, interrupted-import recovery, post-restore derived-state rebuild, verified orphan cleanup and safe retryable storage operations. No paid LLM/embedding work until Q7.

## 4.6 Cloudflare and the public domain

The owner has selected `arivo.itscatalyst.com` as the public API hostname and Cloudflare as the DNS/edge direction. Record this as new owner intent in the appropriate ledger during the next claim; do not silently rewrite D-047 or Q18.

Use Cloudflare MCP with access limited to the `itscatalyst.com` zone. Start read-only. Grant DNS edit only when an origin target is selected and exact records are known. Never use a global API key or broad account-wide token.

Do not create the DNS record until the API origin/runtime exists. Use the correct pattern for the chosen host (CNAME/A record or Cloudflare Tunnel). Configure HTTPS, TLS origin validation, restrictive CORS, security headers, rate limits, host validation and API/MCP streaming compatibility.

**No Railway requirement.** Do not create a Railway project or use Railway as a default. The domain is decided; compute is not. Evaluate Cloudflare-native compute/container options against the actual requirements: Python/FastAPI compatibility, production `psycopg_pool`/Postgres TLS, D-053 bounded kernel subprocess behavior, persistent worker execution, durable queues, secrets, logs, networking and cost. If Cloudflare's runtime cannot run the existing architecture without major compromises, recommend a compatible generic container/VPS origin behind Cloudflare DNS/Tunnel. Ask for one consolidated Q18 decision only after preparing the measured options. Continue all code, containerization, health, OpenAPI and deployment-neutral work in the meantime.

## 4.7 Frontend-ready boundary

Do not build the desktop UI in this repository. Deliver:
- Complete OpenAPI spec and stable API contracts.
- Supabase Auth flow and deep-link/redirect details derived from the actual desktop repo.
- A typed/client contract or tested example client.
- Offline/local persistence and sync contract documented and testable.
- A stable API and MCP hostname.
- Real integration tests that prove the backend is usable independently of the UI.

The separate reader repository can then build/rebuild its frontend over the API without changing backend domain logic.

---

# 5. Ordered execution plan — do not stop between waves

At session start, close the CLAIM-094B post-merge bookkeeping drift. Then proceed in this order. Check claim/intent maxima at each new claim, not by rereading the entire history.

## Workstream 0 — Post-merge reconciliation

- Confirm PR #136 merged at `1eab74a` and five checks passed.
- Close CLAIM-094B append-only under rule 4.
- Re-derive STATE and append the post-merge worklog/session record.
- Verify current claim and intent maxima.
- Record this owner directive, the `arivo.itscatalyst.com` hostname decision, Cloudflare DNS/edge intent, and the new non-stop/batched execution cadence through the canonical intent process.
- Leave Q18 compute and Q12/Q17 storage open; narrow their meaning rather than pretending they are settled.

## Workstream 1 — Supabase migration 0020

- Verify the live ledger is still 1–19.
- Re-run the canonical local migration suite only once if the relevant migration code has not changed since its recorded green run; inspect recent evidence first.
- Use the guarded remote migration act, exact project ref, TLS verify-full and migration credential.
- Apply 0020 only if missing.
- Independently verify the migration row/checksum, role defaults, function search paths, RLS, grants and schema exposure.
- Record evidence and continue.

## Workstream 2 — F6 kernel defect

- Create the separately scoped follow-up claim for the long-unbroken-token / keyword-index PostgreSQL btree row-size boundary.
- Add a bounded tokenizer/index-input contract and tests for normal tokens, very long unbroken runs, Unicode, adversarial size, named refusal and zero partial effect.
- Preserve existing query and idempotency semantics.
- Keep this separate from the route adapter; the adapter must not duplicate kernel logic.
- Land and move on.

## Workstream 3 — CLAIM-095 extraction/readiness API

- Wrap existing extraction commands and query readiness states.
- Expose truthful ready/building/failed/retryable/unavailable state; never present partial extraction as complete.
- Add owner-scoped job/status reads and authorized retries/rebuilds.
- Preserve extraction generations, parser provenance, anchors and failure codes.
- Test duplicate requests, interrupted extraction, replay, cross-owner access and old-generation serving.

## Workstream 4 — Reader and capture API families

Build domain families in sequence, grouping related operations into coherent claims:
1. Reading content/generation and reading position/session state.
2. Highlights, revisions, tombstone/restore and Anchors.
3. Bookmarks, movement, revisions and lifecycle.
4. Notes, revisions and note references.
5. Journal blocks, revisions and history.
6. Stable `@` reference resolution.
7. Reading lists and membership history.

Reuse existing command/query arms and domain lifecycle guarantees. Do not invent new product semantics where the kernel already defines them.

## Workstream 5 — Retrieval API

Expose keyword search, authorized context packs, bounded pagination, provenance, trust and source/version identity. Preserve Phase 5A/5B evidence and evaluation corpus. Do not add paid embedding calls, pgvector or model selection until Q7. Keep deterministic fixtures and evaluator preparation moving.

## Workstream 6 — Sync, export, restore and purge API

Expose the existing sync command/outbox contracts over HTTPS. Preserve idempotent replay, uncertain-ack recovery, explicit conflict behavior, cursor semantics and owner isolation. Implement export/restore/purge endpoints only through existing safeguards. Rebuild derived state safely; purge ledger wins over restored stale content.

## Workstream 7 — MCP completion

- Preserve the existing 22-tool stdio MCP behavior.
- Add the remote Streamable HTTP transport on `/mcp` using the exact same read-only registry/query kernel.
- Authenticate via owner-minted agent read credentials; preserve hash-only database storage, one-time token display, revocation and per-read audit.
- Add owner-only credential mint/revoke API wrappers if needed by the client onboarding contract.
- Test initialize, initialized notification, ping, tools/list, tools/call, errors, invalid/revoked credentials, cross-owner, pagination/budget, streaming and reconnect.
- Ensure no MCP write tools exist.

## Workstream 8 — Storage provider ratification and implementation

- Prepare one concise comparison and recommendation for Q12/Q17 while other work continues.
- At the owner gate, present one consolidated decision request, not repeated micro-questions.
- After ratification, implement the selected private object store behind the existing blob interface, signed upload/download, hash verification, staging, crash recovery, orphan cleanup, purge and backup/restore coverage.

## Workstream 9 — Durable workers

- Implement job schema/state machine and bounded worker loop.
- Add extraction, indexing, import recovery and rebuild jobs.
- Implement lease/fencing/retry/dead-letter semantics.
- Add graceful shutdown and restart recovery.
- Do not create external paid services or extensions without the applicable approval.

## Workstream 10 — Production runtime and Cloudflare domain

- Evaluate compatible runtime options; Railway is not the default and must not be provisioned.
- Produce a measured compatibility report for Cloudflare compute/container options and a generic container behind Cloudflare Tunnel.
- Select a runtime only after the one Q18 decision.
- Build a reproducible container image, separate API/worker start commands, health/readiness endpoints, secret matrix and release/migration command.
- Deploy API and private worker.
- Configure `arivo.itscatalyst.com` DNS/Cloudflare proxy/Tunnel as appropriate.
- Verify valid public HTTPS, origin TLS, database TLS verify-full, CORS, rate limits, host validation and MCP streaming.
- REST: `/api/v1`; MCP: `/mcp`.

## Workstream 11 — Frontend contract integration and final hardening

- Inspect the actual reader repository from a canonical link; do not guess its name.
- Validate Supabase Auth redirect/deep-link flow and token storage contract against that client.
- Run a thin contract client through the deployed API; UI implementation remains separate.
- Test offline/outbox behavior and reconnect if the desktop store contract is available; if Q19 blocks a specific local-store choice, complete backend-side sync/API contract and report only that dependency.
- Complete logs, health, backup, object backup, restore drill, purge reconciliation, performance/resource limits, dependency/security review and operational docs.

---

# 6. Final system verification — one integrated campaign at the end

Do not spread this exhaustive campaign across every micro-step. Run it once after the complete backend, MCP, storage, jobs, runtime and integration path are assembled. Before then, each coherent PR still receives its one required slice-level SEV and CI gate.

## 6.1 Real user lifecycle

Using a real Supabase Auth test user and the deployed service:
1. Authenticate.
2. Import a readable source.
3. Verify private upload and server-side digest.
4. Wait for/inspect extraction readiness.
5. Open/read the source and save/resume position.
6. Create/revise a highlight and bookmark.
7. Create/revise a note.
8. Create/revise a journal block.
9. Add to a reading list and resolve references.
10. Search and retrieve a context pack with provenance.
11. Restart client/agent and retrieve the same data.
12. Export and restore into an isolated target.
13. Verify authoritative content survives and derived state rebuilds.
14. Verify purged content cannot reappear.

## 6.2 Multi-user and concurrency

- User A cannot list/read/write User B's records through REST or MCP.
- Pooled DB owner context does not leak across concurrent requests.
- Auth tokens with bad signature, wrong issuer/audience, expiry or revoked state fail.
- Agent credentials are read-only, owner-scoped, revocable and audited.
- Duplicate idempotency keys converge exactly as defined.
- Lost HTTP response can be replayed without duplicate effect.
- Import/job duplicate submissions do not duplicate derived effects.

## 6.3 Worker and storage fault injection

- Interrupted upload before DB finalize.
- Missing/corrupt/wrong-digest object.
- API process crash before/after DB commit.
- Worker crash during extraction/indexing.
- Expired lease and stale fencing token.
- Retryable vs permanent failure.
- Orphan cleanup with referenced and unreferenced objects.
- Restore with purge ledger reconciliation.

## 6.4 MCP acceptance

- Local stdio and remote Streamable HTTP expose the same 22 tools.
- Initialize/capability negotiation and tools/list are valid.
- Every tool uses the same query core.
- Agent credential is never printed, logged or passed in argv.
- No writes are exposed.
- Remote stream survives Cloudflare proxy path, reconnect and configured timeout.

## 6.5 Deployment and operations

- `https://arivo.itscatalyst.com/health/live` works.
- Readiness accurately fails when DB or required dependency is unavailable.
- `https://arivo.itscatalyst.com/api/v1/...` and `/mcp` route to intended services.
- HTTPS certificate valid; insecure HTTP is redirected/rejected appropriately.
- API/worker DB connections use verified TLS and least-privilege roles.
- No secret is in frontend bundles, Git or logs.
- Backups include relational data and selected object storage.
- Restore drill is performed in isolated environment.
- Resource limits, queue depth, latency, errors and health are observable.

## 6.6 Completion declaration

Declare the backend ready for frontend construction only when:
- Full REST API surface is implemented and documented.
- Existing stdio MCP and remote read-only MCP work through the same query core.
- Supabase migrations are applied and independently verified.
- Auth and owner isolation are proven with real tokens/users.
- Selected object storage and recovery are proven.
- Durable jobs and workers survive failure/restart.
- Public subdomain and HTTPS work.
- The deployed integration client completes the full user lifecycle.
- Backup/restore/purge are proven.
- Required tests, SEV, review and CI are green at merged revisions.
- All remaining owner gates are either ratified or explicitly scoped to later refinement; none are hidden or falsely marked complete.

---

# 7. Credential and provider rules

- Use the existing GitHub connection or fresh repository-scoped GitHub App/OAuth/PAT. The old report says a broad GitHub token was exposed in tool output; rotate it rather than reusing it.
- Supabase MCP should be project-scoped to `wcuuakhdmsmmxagvbdmg`, initially read-only, then write only for approved migrations. Supabase PAT and PostgreSQL password are separate.
- Store secrets only in the cloud agent's secure secret manager/provider integration. Do not paste values into prompts or commit them.
- Cloudflare MCP: `https://mcp.cloudflare.com/mcp`; connect by OAuth and restrict to the `itscatalyst.com` zone. Start Zone/DNS read-only; grant DNS edit only when an origin is selected and exact records are ready. Never use a global API key.
- Do not connect Railway or create Railway projects. It is not part of the current selected architecture.
- No OpenRouter, Graphiti, Kev or ecosystem-memory credentials are needed.

---

# 8. Exact agent operating prompt

You are the implementation agent responsible for completing Arivo's backend end-to-end. Read this directive and the repository's canonical docs, reconcile the live state, then execute. Do not return only another plan.

Work quickly by batching related changes. Do not run the full verification battery after every small edit. Run focused checks only when debugging or validating a critical local behavior. At the end of each coherent bounded claim/PR, run its affected test suite and the required integrated gate once, perform the single required independent SEV over the final diff, open the PR, obtain all five required CI checks on that exact head, disposition review findings, and merge under the existing authorized protocol. This satisfies the repository's mandatory verification rules without the repetitive micro-verification loop the owner rejected.

The owner has explicitly directed continuous execution toward the complete backend end state. When one claim merges, close it, refresh state and immediately begin the next predeclared workstream. Do not pause for approval after every ordinary engineering choice. Ask only for decisions that are explicitly owner-gated or require irreversible/billable external action. A gate blocks only its named task; continue everything else.

Start now:
1. Close CLAIM-094B's already-merged lifecycle and repair stale STATE.
2. Apply migration 0020 through the guarded canonical path if it is still missing.
3. Open the next correctly numbered claim for extraction/readiness and a separate bounded claim for the F6 tokenizer kernel issue; use actual current maxima.
4. Continue every REST route family in this directive.
5. Complete the MCP remote transport over the current read-only 22-tool registry.
6. Complete storage and workers after their named gates, continuing provider-neutral implementation meanwhile.
7. Resolve compute through the Cloudflare/domain architecture without defaulting to Railway; deploy API and worker behind `arivo.itscatalyst.com` when the compute decision is made.
8. Perform the final integrated V-model acceptance campaign once the system is assembled.

Never weaken a law, alter a security boundary to make progress look faster, invent evidence, commit secrets, integrate unrelated memory systems, or claim a remote operation succeeded without observing it. Leave the repository and all session evidence resumable after every session. Report blockers narrowly and keep moving.
