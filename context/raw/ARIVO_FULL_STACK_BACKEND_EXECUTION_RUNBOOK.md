# Arivo Full-Stack Backend Execution Runbook

**Version:** 1.0  
**Prepared:** 18 November 2026  
**Repository:** `prathamarchives/Arivoo`  
**Product:** Arivo  
**Supabase project:** `arivo`  
**Project ref:** `wcuuakhdmsmmxagvbdmg`  
**Region:** `ap-south-1` (Mumbai)  
**Recommended runtime:** Railway, Singapore, subject to account access and cost approval  
**Execution environment:** Cloud coding agent in a sandbox

---

# 0. Mission and non-negotiable boundary

Take the existing Arivo backend from a tested, locally operated PostgreSQL command system to a deployed, authenticated, cloud-connected backend that the desktop application can use over HTTPS.

**Do not rebuild the domain model. Preserve and extend the existing implementation.** The HTTP API is an adapter over the existing command/query core, not a second business-logic implementation.

The target system consists of the Arivo desktop client, Arivo HTTP API, Supabase Auth, Supabase PostgreSQL, Arivo private object storage, Arivo background workers, local persistence/outbox/synchronization, deployment, monitoring, backup and recovery.

Arivo is a standalone product. Do not connect it to unrelated personal infrastructure, external memory systems, other products' databases, or other agents' private services. Do not add their credentials, schemas, URLs, identity models, queues or dependencies to Arivo.

The agent should implement all work that can be completed safely in the repository and sandbox. It must stop at an explicitly owner-gated external or irreversible action, state exactly what is blocked, and continue unrelated work. Do not pretend deployment succeeded if the relevant provider account is not connected.

## 0.1 Core rules

- Every product write continues through the existing command kernel.
- Every product read continues through the existing query layer.
- The desktop never connects directly to PostgreSQL and never writes directly to product tables.
- The API derives owner scope from a verified Auth identity, never from a client-supplied owner field.
- Preserve idempotency, commit-before-acknowledgment, revision/tombstone, provenance, error-code and durability contracts.
- Preserve the local PostgreSQL test adapter and its loopback-only guard. Add a separate explicit production adapter; do not delete the guard.
- Do not create a second migration history.
- Do not use either existing outbox as a general-purpose job queue.
- Do not claim PostgreSQL and object-storage changes are one atomic transaction.
- No secrets in Git, prompts, logs, PRs, worklogs or screenshots.
- No paid infrastructure or plan upgrades without explicit owner approval.

---

# 1. Verified starting state

This starting point was audited on 18 November 2026. Recheck it against current `main` before changing anything.

## 1.1 Repository and implementation

Repository: `prathamarchives/Arivoo`  
Default branch: `main`  
Audited revision: `0c478252469f3690cee61dd6caf0ad08e02dc5f3`

The repository already contains a substantial backend:

| Area | Current implementation |
|---|---|
| Write path | `harness/commands.py`, atomic/idempotent commands, commit-before-ack |
| Read path | `harness/query.py`, owner-scoped reads, bounded pagination |
| Database schema | PostgreSQL migrations under `harness/migrations/`, through `0019_agent_access.sql` |
| Migration runner | `harness/migrate.py`, forward-only/checksummed migration history |
| DB adapter | `harness/adapters/pg.py`, currently loopback-only |
| Blob adapter | `harness/adapters/blob.py`, local content-addressed filesystem store |
| Extraction | `harness/extract.py`, versioned generations/passages |
| Format registry | `harness/formats.py` |
| Sync | `harness/sync.py`, existing two-database outbox delivery |
| Export/restore | `harness/export.py` |
| MCP | `harness/mcp.py`, read-only stdio transport, not a network API |
| Contract client | `harness/client.py` |
| Semantic spike | `harness/semantic.py`, deterministic spike only, not a production embedding backend |

Phase 4 is recorded complete. Phase 5A and 5B are recorded complete. Preserve their contracts and test evidence. No open PRs were observed during the audit; recheck live GitHub state.

## 1.2 Missing production layers

The audit found no production HTTP API, no Supabase Auth-to-owner integration, no remote PostgreSQL connection path, no cloud blob adapter, no hosted worker service, and no final desktop-over-HTTP sync path. The current MCP adapter is stdio-only. The current DB adapter rejects non-loopback hosts. The current blob adapter writes to local disk.

## 1.3 Supabase project state

- Project: `arivo`
- Ref: `wcuuakhdmsmmxagvbdmg`
- Region: `ap-south-1`
- Status: `ACTIVE_HEALTHY`
- PostgreSQL: 17.12
- Arivo migrations applied: 0
- `arv` schema: absent
- Arivo app tables in `public` or `arv`: 0
- `arv_app` and `arv_read` roles: absent
- Arivo Storage buckets: 0
- Arivo Edge Functions: 0
- `vector` extension: available at 0.8.2, not installed

Dashboard: `https://supabase.com/dashboard/project/wcuuakhdmsmmxagvbdmg`  
Project API URL: `https://wcuuakhdmsmmxagvbdmg.supabase.co`

Do not modify or delete any other Supabase project.

---

# 2. Target architecture

```text
Arivo desktop
  |  Supabase Auth token + HTTPS API requests
  v
Supabase Auth  ---> token verification / user UUID
  |
  v
Arivo HTTP API  ---------------------------> private Storage
  |  existing command/query kernel             source objects
  |  authenticated owner context
  v
Supabase PostgreSQL
  |  canonical app records, RLS, migrations
  |  dedicated durable job table
  v
Arivo worker (private service)
  |  extraction, keyword indexing, rebuild, recovery, cleanup
  v
Monitoring / backups / restore / release process
```

Deploy two long-running services from the Arivo repository:

| Service | Public? | Responsibility |
|---|---:|---|
| `arivo-api` | Yes, HTTPS | Auth, HTTP transport, command/query adapters, upload authorization, job submission |
| `arivo-worker` | No public endpoint | Extraction, indexing, rebuilds, recovery and safe cleanup |

Both may use the same application image with different start commands. The API and worker must have separate secrets. The migration process is separate from both and uses a temporary privileged credential.

## 2.1 Recommended application host

Recommended target: **Railway, Singapore region `asia-southeast1-eqsg3a`**, because it supports persistent Python services, separate workers, service variables and HTTPS domains, and Singapore is geographically closer to Mumbai than US/EU regions.

This is a recommendation, not proof that Railway access or billing is available. Before creating services, the agent must verify account/workspace access, review the proposed resources and costs, and stop before any unapproved charge or plan upgrade.

Use Railway's current Infrastructure-as-Code workflow. As of November 2026, the old `railway.toml`/`railway.json` Config-as-Code route is deprecated for new services. Run `railway config init`, inspect `.railway/railway.ts`, then use `railway config plan` before `railway config apply`.

References:
- https://docs.railway.com/deployments/regions
- https://docs.railway.com/build-deploy
- https://docs.railway.com/networking/public-networking
- https://docs.railway.com/networking/domains/working-with-domains
- https://docs.railway.com/variables
- https://railway.com/guides/railway-infrastructure-as-code

Do not provision a second application database on Railway. Supabase remains the canonical database.

---

# 3. Execution protocol and stop conditions

## 3.1 Repository workflow

Before every implementation slice:

1. Read `AGENTS.md` fully.
2. Read `STATE.md` and compare it with live GitHub state.
3. Read `CLAIMS.md`; ensure no overlapping active claim.
4. Read relevant `PLAN.md`, `RTM.md`, `DECISIONS.md`, `EXECUTION.md` and `LAWS.md` sections.
5. Create/reserve an appropriately scoped claim.
6. Branch from the latest verified `main`.
7. Add tests first and observe a meaningful RED.
8. Implement one bounded behavior.
9. Run the real stack and independent-read tests.
10. Run applicable full verification.
11. Produce the required separately authored SEV.
12. Open a PR, disposition every review finding, and merge only through the repository's authorized process.
13. Re-derive `STATE.md` from live state after merge.

Do not push implementation changes directly to `main`. Respect LAW-05 size limits and LAW-31 claim exclusivity. No giant all-at-once PR.

## 3.2 Dependency policy

`LAWS.md` LAW-08 prohibits adding a dependency without an approval note. The current backend uses Python standard library only and has no general production lockfile.

Before adding packages, inspect Python compatibility, propose the minimum set, write the approval note in the repository's accepted form, inspect licenses/transitive dependencies, pin exact versions and create a lockfile. Keep the existing harness working.

Recommended packages for consideration, not automatic approval:

- FastAPI for the HTTP adapter.
- Uvicorn for ASGI serving.
- Psycopg 3 with pool support for production PostgreSQL.
- PyJWT with crypto support for asymmetric JWT verification.
- A small HTTP client only if existing approved code/stdlib cannot safely implement the needed Storage calls.

Keep HTTP framework imports in the approved HTTP adapter boundary and database driver imports in the approved DB adapter boundary. Verify all selected versions against the repository's Python support policy; do not silently raise the minimum Python version.

## 3.3 Credentials and paid actions

Never print or commit secrets. Never put credentials in prompts, issue bodies, PRs, docs, worklogs, screenshots, command arguments or logs. Use the cloud agent's secure secret manager and provider secret-entry UI. Do not ask the owner to paste a password or token into chat.

The following require owner approval if not already present in recorded owner intent: provider-specific blob storage decision (Q12), any Work/Source identity change (Q11), paid resource/plan changes, signing-key rotation, destructive/data-loss-risk migration, backup-retention changes, DNS/custom-domain change, and paid embedding/model calls (Q7).

If access is missing, report only the required secret/permission name and where it must be entered. Never invent a value.

---

# 4. Phase 0 — sandbox and repository preflight

## 4.1 Verify the sandbox

Confirm:

- Working directory and Git remote are `prathamarchives/Arivoo`.
- Current branch, commit SHA and clean working tree.
- Python, `psql`, Docker (if used), Supabase CLI and Railway CLI versions.
- Outbound access to Supabase and the deployment host.
- Which provider integrations are connected.
- Whether credentials can be entered via a secure environment manager.

Do not dump the environment. Print only whether required variable names are present.

## 4.2 Reconcile current repository state

The audit found stale status pointers in `STATE.md` and older phase text in `AGENTS.md`. Re-derive current state from live `main`, PR list, branches, `CLAIMS.md`, recent `context/WORKLOG.md`, `PLAN.md` and the latest merged run records. Repair stale navigation through a bounded documentation slice. Never rewrite historical intent or session records to make them look current.

## 4.3 Read actual implementation

Inspect at minimum:

- `harness/commands.py`, `harness/query.py`, `harness/migrate.py`
- `harness/adapters/pg.py`, `harness/adapters/blob.py`
- `harness/migrations/0001_baseline.sql` through `0019_agent_access.sql`
- `harness/sync.py`, `harness/export.py`, `harness/extract.py`, `harness/formats.py`
- `harness/mcp.py`, `harness/client.py`, `harness/semantic.py`
- `PLAN.md`, `RTM.md` (especially §4.4 and §7.4), `DECISIONS.md`, `EXECUTION.md`, `LAWS.md`, `AGENTS.md`, `STATE.md`, `CLAIMS.md`

Identify the actual desktop/reader repository from an authoritative link in current project documentation. Do not guess the repo name. Inspect its framework, auth integration, redirect/deep-link scheme, local persistence, API client, token storage and offline behavior before implementing desktop integration.

## 4.4 Current-SHA preflight

Follow the current preflight commands in `PLAN.md`. The audited plan listed:

```bash
python3 tools/verify_canonical_layer.py
python3 tools/verify_selftest.py
python3 tools/isolation_check.py
python3 tools/isolation_selftest.py
make harness-health
make verify-schema
make verify
```

If target names changed, inspect the current Makefile and run the current equivalents. Record actual commands, exit codes, SHA and results. An old green run is not proof for a new revision.

---

# 5. Phase 1 — connect the sandbox agent to Supabase

The agent's Supabase administrative connection is separate from the production database connection used by the running API.

## 5.1 Preferred: project-scoped Supabase MCP OAuth

Use the official Supabase MCP server. Start read-only and restricted to the Arivo project:

```text
https://mcp.supabase.com/mcp?project_ref=wcuuakhdmsmmxagvbdmg&read_only=true
```

Complete OAuth in the agent host. Restrict feature groups to what the task needs (initially database, debugging and development/docs). Verify the server sees only project `wcuuakhdmsmmxagvbdmg`.

Before schema changes, switch to project-scoped write access through the supported OAuth flow. Keep SQL confirmation prompts enabled. Do not use account-level access if project scope is available.

Official reference: https://supabase.com/docs/guides/ai-tools/mcp

## 5.2 Fallback: scoped Supabase PAT

If the cloud agent cannot complete OAuth, create a scoped personal access token in Supabase settings. Scope it to this project only and grant only permissions needed. Start read-only; add Database write only for the migration stage. Enter the value through secure credentials, not the prompt or repository. Do not use a classic account-wide PAT when scoped tokens are available.

Reference: https://supabase.com/docs/guides/platform/personal-access-tokens

## 5.3 Verify the project

Using project-scoped access, inspect project ref, region, status, PostgreSQL version, schemas/tables, migration history, installed extensions, Storage buckets, Edge Functions and security/performance/health advisors. Save sanitized results in the run record. Expected initial application state is listed in §1.3.

---

# 6. Phase 2 — database connection and migration authority

This phase prevents duplicate schema histories.

## 6.1 Preserve the current migration history

The canonical SQL is in `harness/migrations/`, applied by `harness/migrate.py`. It has ordered filenames, checksums, a custom migration ledger and fail-closed validation. Preserve it as the one canonical schema history unless a separately reviewed plan deliberately changes that decision.

Do not create copied SQL in a parallel `supabase/migrations/` folder and do not apply the same schema independently with both the custom runner and Supabase CLI. That creates migration drift.

Supabase CLI v3 changed database defaults: commands such as `db push`, `db pull`, `db dump`, `migration list` and `gen types` target the local stack by default; hosted operations require explicit `--remote`. Unattended hosted changes require `--yes`. Do not assume an unqualified command targets production.

References:
- https://supabase.com/docs/guides/local-development/cli/migrating-to-v3
- https://supabase.com/docs/reference/cli/introduction

For this repository, use the existing canonical migrator through a new explicit remote-target path. Do not use `supabase db push` to apply Arivo's schema unless the migration authority has been deliberately changed and reconciled.

## 6.2 Add a remote connection path without weakening local safety

The current `harness/adapters/pg.py` refuses non-loopback hosts. Preserve that local behavior. Add a separate explicit production migration/database path that:

- Requires explicit remote target mode.
- Confirms the exact expected Supabase project ref/host.
- Requires TLS certificate verification.
- Never falls back to localhost or another database.
- Never logs credentials or full connection strings.
- Uses a migration credential separate from runtime API credentials.
- Preserves ordering, checksum, transaction and verification guarantees.

`make migrate` remains local-only. Add a distinct, carefully guarded remote target only after tests prove it cannot silently select the wrong database. Do not merely delete the loopback check.

## 6.3 Test migrations before production

On a clean local PostgreSQL 17 database:

1. Apply the entire existing migration sequence.
2. Verify all versions/checksums.
3. Run the schema verifier and harness.
4. Test a representative prior-state migration forward.
5. Simulate migration failure and verify no partial schema/false ledger row.
6. Verify reruns are no-ops.
7. Verify edited migration files are rejected by checksum validation.
8. Inspect how the test rig bootstraps `arv_app` and `arv_read` roles; reproduce the intended least-privilege production role model.

Do not proceed to remote migration unless the local chain is green.

## 6.4 Choose Supabase PostgreSQL connection mode

Use the Supabase Dashboard's Connect panel. Do not guess the pooler host or username.

- Direct connection is suitable for persistent backends with working IPv6 or an IPv4 add-on.
- Shared session pooler is suitable for persistent backends on IPv4-only networks.
- Transaction pooler is designed for short-lived/serverless connection behavior and has transaction-pooling limitations; do not use it for the current command-kernel session model without explicit adaptation/tests.

For Railway, initially evaluate the shared **session pooler** because it is IPv4 reachable. Copy the exact host, port and username from Connect.

Require TLS. Prefer `sslmode=verify-full` with the current Supabase root certificate. `sslmode=require` encrypts but does not verify server identity. Use finite connection/query timeouts and a bounded pool.

Reference: https://supabase.com/docs/guides/database/connecting-to-postgres

## 6.5 Separate credentials and roles

Use distinct responsibilities:

| Credential | Purpose | Location |
|---|---|---|
| Migration/admin connection | Apply reviewed migrations/bootstrap roles | Temporary protected release environment only |
| `arv_app` login | API command/query transactions | API service secret store |
| Worker DB credential | Claim jobs and run owner-scoped worker operations | Worker service secret store |
| Independent read role | Verification reads if required | Verification environment only |

The API and worker must not use PostgreSQL `postgres` superuser or Supabase service-role credentials as their normal DB login.

Runtime roles must not have `SUPERUSER`, `BYPASSRLS`, `CREATEDB` or `CREATEROLE`. Inspect the role bootstrap in the current rig and migrations. Do not assume test roles are already created by migrations.

---

# 7. Phase 3 — deploy and verify the Supabase schema

Proceed only after Phase 2 passes.

## 7.1 Preflight

Confirm the project ref is exactly `wcuuakhdmsmmxagvbdmg`, project is healthy, full migration chain is green locally, remote adapter is explicitly targeting this project, role bootstrap is understood, migration credential is available securely, and no owner-gated decision is being silently closed.

## 7.2 Apply

Apply all canonical migrations using the repository's remote-aware migration runner. Do not paste ad hoc SQL into the dashboard as a substitute. Capture target project ref, starting ledger, applied versions, checksums, command, exit code and post-migration verification.

If a migration fails, stop. Inspect the real schema and custom ledger before retrying. Do not manually run fragments until the migration state is understood. Write a failing reproduction/repair slice.

## 7.3 Verify

Verify:

- `arv` schema and expected application tables exist.
- Custom migration ledger matches every canonical file and checksum.
- Roles and grants match the least-privilege design.
- RLS is enabled/forced where expected.
- Owner policies, append-only triggers and revision guards exist.
- Indexes and constraints exist.
- No unintended public grants or exposed product tables exist.
- Advisors have no unresolved high-risk security/performance findings.

Keep `arv` private from direct browser Data API use. The Arivo HTTP API is the product access boundary.

## 7.4 Extensions

Do not enable extensions merely because they are available. Leave `vector` uninstalled until the approved semantic-index slice needs it. Do not add `pg_cron`, queues or other extensions without concrete requirements, decisions and tests.

---

# 8. Phase 4 — Supabase Auth and owner identity

## 8.1 Inspect the desktop auth flow

Find the real desktop repository through existing project docs. Identify its framework, Auth client, system-browser/PKCE or OTP flow, exact callback/deep-link URI, secure token storage and logout/refresh behavior. Do not invent a callback URI.

## 8.2 Configure Supabase Auth

Inspect existing settings and enabled providers. Configure only the provider required by the actual application. Set the Site URL and redirect allow-list from the real web origins/callback scheme. Do not use wildcard redirects. Configure confirmation/OTP and session-refresh behavior deliberately. Test sign-up, sign-in, refresh, logout and revoked/expired-session behavior using test users.

Do not enable social providers without a product need and the required OAuth client configuration.

## 8.3 Verify tokens in the API

Every product route requires a valid Bearer access token. Verify signature, allowed algorithm, exact issuer, expected audience, expiry, not-before, `sub`, and key ID. Prefer asymmetric verification against the project's JWKS when the project is configured for asymmetric signing keys. Cache JWKS safely and refresh on an unknown `kid`. Never accept a decoded-but-unverified JWT.

Do not change signing mode or rotate signing keys as an incidental implementation step. If the project uses a legacy signing mode, document it and implement verification for the active configuration. Any signing-mode change is a separately reviewed security operation.

Never use user-editable `user_metadata` for authorization decisions.

References:
- https://supabase.com/docs/guides/auth/signing-keys
- https://supabase.com/docs/guides/auth/jwts

## 8.4 Derive owner and actor on the server

Set production `owner_scope` from the verified token's `sub` UUID. Reject/ignore client-supplied owner/actor authority fields. Ordinary user writes use actor `owner`. Worker writes use actor `worker` and the exact owner scope from the job. Test fixture owners such as `A` or `me` remain test-only.

## 8.5 Pooled DB owner context

The current RLS model uses `app.current_owner`. Set it transaction-locally for each request, never as a persistent session value that can leak between pooled requests.

For every operation:

1. Acquire a pooled connection.
2. Begin one transaction.
3. Set transaction-local owner context from verified identity.
4. Execute the existing command/query path.
5. Commit or roll back.
6. Return the connection only after cleanup.

Test rapid reuse of the same pooled connection across users A and B. A rollback must not leave A's context visible to B.

---

# 9. Phase 5 — private source storage and import staging

This is the still-open Q12 provider decision. The recommended option is private Supabase Storage plus desktop-local staging/cache, but Supabase project creation does not itself ratify that choice.

The agent must read `RTM.md` §7.4 and current Q12. If a newer owner decision authorizes Supabase Storage, record the decision/pointer and proceed. If Q12 remains open, prepare the comparison and continue provider-neutral work; do not silently create provider-specific source schema or promise cross-store atomicity.

## 9.1 Preserve the blob contract

Keep the provider-neutral interface:

```text
put(bytes) -> digest
get(digest) -> bytes
delete(digest)
exists(digest) -> bool
```

Keep the local filesystem adapter for local tests. Add a production Storage adapter behind the same contract.

Recommended private object key:

```text
<supabase-auth-user-uuid>/<sha256-hex-digest>
```

Recommended bucket name: `arivo-sources`, unless existing naming conventions/collision checks require another name.

The adapter must verify returned bytes against SHA-256, refuse corruption/missing objects, avoid silent overwrite/healing, support safe deletion/exists behavior and keep binary bytes out of PostgreSQL rows.

## 9.2 Bucket setup after Q12 authorization

1. Create `arivo-sources` as a **private** bucket.
2. Set an explicit upload size limit based on the actual product import policy.
3. Set MIME allow-list from `harness/formats.py` and current opaque-byte support.
4. Add Storage RLS policies for owner-scoped paths.
5. Use first path segment = authenticated user's UUID.
6. Test user A can upload/read/delete only A's objects.
7. Test user B cannot read A's object by guessing the path.
8. Test anonymous reads fail.
9. Do not make the bucket public.

Use the user's access token plus publishable key for RLS-bound signed-upload authorization where supported. Workers that genuinely need privileged object operations may receive a storage secret only in the worker secret store, with path validation and audit logging. Never expose privileged keys to the desktop.

References:
- https://supabase.com/docs/guides/storage/buckets/fundamentals
- https://supabase.com/docs/guides/storage/security/access-control
- https://supabase.com/docs/reference/python/storage-from-createsigneduploadurl
- https://supabase.com/docs/reference/python/storage-from-uploadtosignedurl

## 9.3 Upload lifecycle

1. Desktop requests an import reservation from the API.
2. API authenticates user and creates an idempotent staging reservation.
3. API returns short-lived signed upload URL and owner-scoped object key.
4. Desktop uploads bytes to private Storage over HTTPS.
5. Desktop calls API finalize endpoint.
6. Server verifies object existence/readability and hashes actual stored bytes.
7. Digest and size must match the reservation.
8. Existing command kernel finalizes Source metadata and command history atomically in PostgreSQL.
9. Extraction job is enqueued.
10. API returns truthful durability and processing states.

Database and object-storage writes are not one transaction. A crash after upload but before metadata commit must leave a recoverable object or safe orphan. A committed Source must never point to a missing/unverified object.

---

# 10. Phase 6 — production PostgreSQL adapter

Add a production adapter with persistent pooled connections, SSL verification, bounded timeouts, parameterized SQL, transaction cleanup, transaction-local owner context, typed errors and safe shutdown.

Keep local and production configs separate:

- Local: existing PostgreSQL test rig and loopback-only adapter.
- Production: Supabase direct/session-pooler selected in §6.4; TLS verification; `arv_app` least-privilege role; no trust auth.

Do not remove the loopback guard or let production selection happen by an accidental environment fallback. Do not add SQL in HTTP route handlers. New product code must use the existing kernel and repository architecture rules.

---

# 11. Phase 7 — production HTTP API

## 11.1 Framework and boundaries

Recommended: FastAPI + Uvicorn, after LAW-08 approval and version compatibility checks. Keep HTTP imports in the approved HTTP adapter. Keep the PostgreSQL driver in the DB adapter. Do not introduce a second command kernel.

Use versioned API namespace `/api/v1` to map the current command `api_version=1`. Generate OpenAPI from the actual implementation.

## 11.2 Minimum route coverage

Implement API operations over existing commands/queries for:

| Area | Required operations |
|---|---|
| Health | liveness, readiness |
| Auth | current verified user/context |
| Sources | begin import, finalize, list library, detail, capabilities/readiness |
| Extraction | request extraction, job status, safe retry/rebuild |
| Reading | source/read data, save/get position |
| Highlights | create/read/revise/tombstone/restore/list/history |
| Bookmarks | create/read/move/tombstone/restore/list/history |
| Notes | create/read/revise/tombstone/restore/list/history |
| Journal | create/read/revise/list/full history |
| References | typed stable-reference resolution |
| Reading lists | create/list/member add/remove/current membership |
| Retrieval | keyword search, bounded context packs, provenance/trust labels |
| Sync | authenticated push/pull or equivalent command delivery |
| Export/restore | owner-authorized export/recovery path |

Use exact command/query contracts as the source of truth. Document route methods, DTOs and errors. Do not guess the desktop's needs without inspecting its actual code.

## 11.3 Write and read rules

Every write route:

- Requires valid auth.
- Derives owner and actor server-side.
- Requires an idempotency key.
- Calls existing command kernel.
- Returns truthful durability rung, effect ID and API version.
- Maps existing stable error codes to HTTP.

Every list route is bounded, paginated and owner-scoped. Reject invalid cursors and limits. Do not reveal another owner's object existence.

## 11.4 Error handling

Centralize mapping. Typical classes: unauthenticated `401`; authorization `403` when safe; invalid input `400/422`; idempotency conflict `409`; rate limit `429`; transient dependency failure `503`; unexpected invariant failure generic `500` plus sanitized server log/correlation ID.

Do not return stack traces, raw SQL, internal hostnames, private object keys, tokens or source contents.

## 11.5 Health endpoints

Implement `GET /health/live` and `GET /health/ready`. Liveness proves the process runs. Readiness checks only dependencies needed to serve traffic, using bounded timeouts. Do not disclose secrets or private DB details.

---

# 12. Phase 8 — durable background workers

The existing client outbox handles client synchronization. The existing server outbox records a post-commit handoff. Neither is a generic job queue. Add a separate durable job state machine.

## 12.1 Job record requirements

At minimum: job ID, owner scope, job type, payload schema version, idempotency/dedupe key, small validated payload, state, attempt count, available-after time, lease owner, lease expiry, monotonic fencing token, last typed error, timestamps and completion time.

States should include queued, leased, succeeded, retryable and terminal/dead-letter. Document transitions and retry limits.

## 12.2 Concurrency and crash safety

Claim using an atomic row-locking pattern such as `FOR UPDATE SKIP LOCKED`, with leases and fencing tokens. A stale worker must not complete a job after another worker reclaimed it. Expired leases must be reclaimable. One poison job must not block the queue. Duplicate job submissions must converge under the declared idempotency contract.

Create the job in the same PostgreSQL transaction as the authoritative state change or transactional handoff. Never commit an import while silently losing its required processing task.

## 12.3 Initial jobs

Start only with current Arivo needs:

1. Extract source.
2. Rebuild keyword index.
3. Recover interrupted import.
4. Rebuild derived state after restore.
5. Clean verified orphaned objects.
6. Retry safe, explicitly retryable storage operations.

Do not put entire documents into job payloads. Use owner-scoped object references and IDs. Do not add generative/model processing to the pipeline.

## 12.4 Worker service behavior

Worker is a private persistent Railway service. It has a worker-specific restricted DB credential, claims jobs, sets transaction-local owner scope from the job, uses bounded polling and timeouts, logs job IDs/codes without content/secrets, handles graceful shutdown and resumes after restart. Do not generate a public worker domain.

---

# 13. Phase 9 — desktop authentication and synchronization

Inspect the actual desktop repository before changing it. Determine framework, Auth library, deep-link callback, OS secure storage, local DB/cache, outbox, file staging and API client.

The desktop must:

- Use Supabase Auth's approved flow.
- Store refresh/access credentials in OS-protected storage.
- Refresh safely and handle expiry/revocation.
- Clear credentials on logout.
- Never contain a database URL or privileged Supabase secret.
- Configure the deployed API base URL, e.g. `ARIVO_API_BASE_URL=https://<actual-api-domain>`.

The existing `harness/sync.py` proves useful two-Postgres delivery contracts, but it is not the final desktop-over-HTTP transport. Preserve its idempotency, explicit local/server durability states, retryable/failed/uncertain/acknowledged states, conflict visibility and no-silent-overwrite behavior. Implement the HTTP transport through the same contracts.

Required desktop behavior:

1. Save locally.
2. Show local-durable only after local commit.
3. Queue sync intent.
4. Send authenticated command over HTTPS.
5. Resolve lost response by same-key replay/query.
6. Record server acknowledgment only when confirmed.
7. Surface conflict rather than silent last-write-wins.
8. Resume after restart.
9. Allow local reading/capture offline.
10. Reconcile after reconnect.

Test two devices for the same user and two different users. Do not claim full device sync because the existing two-Postgres test driver passes.

---

# 14. Phase 10 — Railway deployment and HTTPS

Only proceed when Railway access and the required cost are authorized.

## 14.1 Create service configuration

```bash
railway --version
railway --help
railway config --help
railway config init
```

Inspect `.railway/railway.ts` generated by the current CLI. Configure:

- API service `arivo-api`, public HTTPS domain, Singapore region.
- Worker service `arivo-worker`, private/no public domain, Singapore region.
- Same repository/build/image where practical, separate start commands.
- API health check and restart policy.
- Service-specific secrets.
- No Railway-hosted Postgres.

Review the proposed infrastructure:

```bash
railway config plan
```

Inspect all resources, removals, variables, region and cost. Apply only after the plan is correct and cost has owner approval:

```bash
railway config apply
```

## 14.2 API start command

The API must bind to all interfaces and the platform-provided port. Conceptual command:

```bash
uvicorn <actual_api_module>:app --host 0.0.0.0 --port "$PORT"
```

Replace placeholder with the real module. Worker command should invoke the actual worker runner. Do not run migrations from the API's ordinary startup command.

## 14.3 Secrets

Set variables in Railway's secure service variable interface. Suggested names, only where actually used:

```text
ARIVO_ENV=production
SUPABASE_URL=https://wcuuakhdmsmmxagvbdmg.supabase.co
SUPABASE_PUBLISHABLE_KEY=<public-key>
SUPABASE_JWT_ISSUER=<verified-issuer>
SUPABASE_JWKS_URL=<verified-jwks-url>
DATABASE_URL=<least-privilege-arv-app-session-pooler-url-with-ssl-verification>
ARIVO_STORAGE_BUCKET=arivo-sources
ARIVO_BLOB_BACKEND=supabase
ARIVO_ALLOWED_ORIGINS=<exact-origins>
ARIVO_LOG_LEVEL=INFO
```

The privileged migration connection belongs only in a protected release/migration environment. Never add it to API or worker variables.

Do not put actual values in `.env.example`. Do not print secret values.

## 14.4 Public HTTPS

Generate a Railway-provided domain for the API. Expected shape:

```text
https://<generated-service-name>.up.railway.app
```

The exact name is generated by Railway. Confirm DNS, valid certificate and HTTPS response. Test HTTP behavior so plaintext traffic cannot be used. Configure trusted proxy behavior based on Railway's actual proxy headers. Reject unexpected Host headers. Restrict CORS to actual origins. Enable HSTS only after HTTPS/redirect behavior is verified.

A custom domain is optional. Only add one if the owner provides domain/DNS access. Use the exact CNAME and TXT records supplied by Railway, wait for verification and confirm the certificate. Do not guess a domain or change existing DNS.

Railway references:
- https://docs.railway.com/networking/public-networking
- https://docs.railway.com/networking/domains/working-with-domains
- https://docs.railway.com/networking/troubleshooting/ssl

## 14.5 TLS is required on every hop

HTTPS for the public API is separate from database TLS. Require TLS for desktop→API, API/worker→Supabase PostgreSQL and API/worker→Storage. For PostgreSQL use the current Supabase root certificate and `sslmode=verify-full` where supported. Do not allow silent plaintext fallback. Test from the actual deployed services.

---

# 15. Phase 11 — CI/CD and release discipline

CI must preserve existing canonical/harness checks and add:

1. API unit/contract tests.
2. JWT/JWKS validation tests.
3. PostgreSQL 17 production-adapter tests.
4. Two-owner RLS isolation tests.
5. Pooled connection owner-context leakage test.
6. Storage adapter tests: missing, corrupt, wrong digest and cross-owner denial.
7. Job lease/fencing/retry/recovery tests.
8. API/worker container build.
9. Dependency lockfile verification.
10. Secret scan.

Use separate local, non-production integration and production environments. Never run destructive tests against production. Do not create paid Supabase branches automatically; inspect their cost first.

Release order:

1. CI and SEV green on candidate revision.
2. Review migration diff.
3. Confirm backup/recovery position.
4. Apply forward-only migration with protected migration credential.
5. Verify schema and migration checksums.
6. Deploy API.
7. Verify API health and auth.
8. Deploy worker.
9. Verify it claims and completes a safe test job.
10. Run production smoke tests with test accounts and non-sensitive fixtures.
11. Observe logs/resources.
12. Update repository state and release record.

Do not reverse migrations by deleting production objects. Application rollback must remain compatible with the current schema.

---

# 16. Phase 12 — monitoring, backup and restore

## 16.1 Logs and metrics

Structured logs should contain timestamp, service, environment, request/correlation ID, route/command, Arivo error code, HTTP status, duration, job ID/type/attempt and safe owner identifier where required.

Never log tokens, passwords, database URLs, signed upload/download URLs, source contents, notes or journal content.

Monitor API uptime/latency/5xx, DB pool saturation, import failures, job queue depth/oldest age/retries, worker crashes, Storage errors, sync backlog/conflicts and available backup status.

## 16.2 Backups

Inspect the actual Supabase plan and dashboard backup features. Do not assume a particular backup or point-in-time recovery tier is included.

A complete backup must account for PostgreSQL data, private Storage objects, migrations/configuration, restore ordering, purge ledger precedence and rebuilding derived passages/indexes. A DB backup alone is incomplete if file bytes live in object storage.

Follow existing Arivo backup/purge policy. Do not change retention without owner approval.

## 16.3 Restore drill

Use a dedicated test restore target, never production:

1. Restore database through approved process.
2. Restore or verify object data.
3. Reconcile destination purge ledger.
4. Verify source digests.
5. Verify notes/highlights/bookmarks/journal revisions/references.
6. Rebuild derived state.
7. Confirm purged content does not reappear.
8. Run clean external client.
9. Record actual commands, results and not-verified items.

---

# 17. Phase 13 — production acceptance tests

Do not declare completion until these groups pass on the deployed system.

## 17.1 Auth and identity

- Unauthenticated product route → `401`.
- Valid test user token accepted.
- Expired, malformed, invalid-signature, wrong-issuer and wrong-audience tokens rejected.
- Unknown signing-key ID handled with safe JWKS refresh.
- Owner scope derived only from verified `sub`.
- Client-supplied owner/actor override rejected or ignored.
- User A cannot read/write User B's content.
- Refresh/logout/revocation behavior tested.

## 17.2 Database

- API uses `arv_app`, not superuser.
- Runtime role has no `BYPASSRLS`.
- RLS and same-owner command validation both apply.
- Two users sharing a pooled connection cannot leak owner context.
- Rollback resets context.
- Independent read confirms committed effects.

## 17.3 Command contract

- Same idempotency key/body replays original effect.
- Same key/different body gives typed conflict.
- Lost response after commit resolves by replay.
- Crash before commit gives no acknowledged effect.
- Crash after commit-before-ack converges to original effect.
- Every write uses the existing kernel.
- Every response preserves API version and truthful durability.

## 17.4 Files and storage

- Private bucket denies anonymous download.
- Cross-user object read denied.
- Signed upload path is owner-bound.
- Interrupted upload recoverable.
- Wrong digest rejected.
- Missing object cannot become a committed Source.
- Corruption fails closed.
- Orphan cleanup does not delete referenced files.
- Purge removes copies and restore cannot resurrect them.

## 17.5 Workers

- Job insert atomic with required handoff.
- Two workers cannot hold valid lease simultaneously.
- Expired lease reclaimed.
- Stale fencing token cannot complete reclaimed job.
- Worker crash and restart recover safely.
- Poison job does not block queue.
- Duplicate jobs do not duplicate derived effects.
- Job status queryable through API.
- Each job uses its recorded owner scope.

## 17.6 Actual desktop workflow

Through the real desktop application, not only the CLI test client:

1. Sign in.
2. Import a readable source and upload to private Storage.
3. Verify import completion.
4. Open/read source and save position.
5. Create highlight and bookmark.
6. Create/revise note.
7. Write/revise journal block.
8. Resolve references.
9. Search and retrieve a context pack.
10. Restart and reopen the same material.
11. Verify saved state/durability.
12. Go offline and create a local change.
13. Reconnect and sync.
14. Simulate lost response and replay.
15. Verify conflict behavior.
16. Sign in as a second user and verify isolation.

The existing CLI client is useful contract evidence but cannot replace actual desktop integration.

## 17.7 Backup and TLS

- Export/restore preserves authoritative content.
- Blob digests match after restore.
- Derived state rebuilds.
- Purge ledger wins and purged material cannot reappear.
- API has valid HTTPS certificate.
- Plain HTTP cannot be used for product traffic.
- DB connection uses TLS verification.
- Storage uses HTTPS.
- No privileged key in desktop assets.
- CORS/host validation/rate limits/log redaction verified.
- Supabase advisors have no unresolved high-risk findings.

---

# 18. Remaining Phase 5 retrieval work

Productionizing the backend does not automatically finish the retrieval/compounding roadmap.

| Phase | Work | Status/gate |
|---|---|---|
| 5A | Authorized retrieval API/context packs | Recorded complete; expose through production HTTP |
| 5B | Evaluation baseline | Recorded complete; preserve as ranking regression suite |
| 5C | Semantic spike | Deterministic only; Q7 model/license/runtime/cost/corpus approval required |
| 5D | Versioned semantic index/vector retrieval | Not complete; embeddings, lineage, resumable jobs, invalidation and rebuild |
| 5E | Hybrid retrieval | Not complete; keyword/vector/filter ranking and held-out evaluation |
| 5F | Grounded relationships | Not complete; evidence and valid endpoint requirements |
| 5G | Concept identity/graduation | Not complete; aliases, correction, merge/split history and held-out validation |
| 5H | Policy/evaluation gate | Must precede downstream evidence promotion/graduation that depends on it |
| 5I | Demonstrate compounding | Separate deterministic, semantic and graph evidence in real research use |
| 5J | Final integrated gate | Recovery, security, migration, rebuild, performance/cost and owner validation |

Do not install `vector` or issue paid embedding calls before the approved semantic slice. The current deterministic spike is an evaluator aid, not evidence of production semantic quality.

---

# 19. Execution waves and deliverables

Run the waves in order. Each wave may require several bounded PRs.

## Wave A — readiness and decisions

Deliver: reconciled repository state, current-SHA preflight, claim/slice plan, verified Supabase access, provider-access status, dependency approval proposal, Q12 storage recommendation and architecture record.

Exit: no stale navigation claim, no hidden access blocker, no silently closed owner decision.

## Wave B — Supabase DB foundation

Deliver: remote DB adapter, preserved local guard, runtime role/grants, canonical migration chain deployed, RLS/policy verification, TLS-verified connection and advisor results.

Exit: current Arivo schema exists in the correct Supabase project and passes independent checks.

## Wave C — private Storage and import

After Q12 authorization, deliver: private bucket, owner RLS, production blob adapter, signed upload flow, digest validation, staging/recovery, orphan cleanup and fault tests.

Exit: no committed Source can point to a missing/unverified object.

## Wave D — Auth and HTTP API

Deliver: Supabase Auth/JWT verification, owner derivation, versioned OpenAPI API, route/DTO adapters over existing commands/queries, typed errors and API integration tests.

Exit: API safely authenticates and executes existing Arivo contracts.

## Wave E — workers

Deliver: job state machine, leases/fencing, worker runner, extraction/index jobs, retry/recovery and job status API.

Exit: async tasks survive duplicate requests, worker crashes and restarts.

## Wave F — HTTPS deployment and operations

After account/cost approval, deliver: Railway IaC, API and private worker in Singapore, secure service variables, HTTPS certificate, TLS-verified Supabase connection, health checks, logs, backup and release procedure.

Exit: deployed API and worker are healthy behind the intended secure interfaces.

## Wave G — desktop integration and sync

Deliver: actual client Auth/API integration, secure token storage, local persistence/outbox integration, HTTP sync, offline/replay/conflict tests and real end-to-end user workflow.

Exit: desktop completes §17.6.

## Wave H — final production hardening

Deliver: security review, backup/restore drill, performance/cost profile, updated RTM/SEV/CI and owner-fidelity validation.

Exit: all applicable production predicates pass; advanced Phase 5 work remains separately gated.

---

# 20. Secret and configuration matrix

| Value | Desktop | API | Worker | Migration/release |
|---|---:|---:|---:|---:|
| Supabase project URL | Yes | Yes | Yes | Yes |
| Publishable key | Yes | Only if needed | Only if needed | Optional |
| User access token | Secure storage/per request | Per request only | No by default | No |
| Supabase secret/service key | Never | Only if specifically required | Only if specifically required | Only if specifically required |
| Runtime DB URL (`arv_app`) | Never | Yes | Separate restricted role | No |
| Migration/admin DB URL | Never | Never | Never | Temporary protected secret |
| Storage bucket name | Optional | Yes | Yes | Yes |
| API base URL | Yes | No | No | Yes |
| JWT issuer/JWKS | No | Yes | If required for internal job auth | No |
| Railway credentials | Never | Never | Never | Secure deployment environment only |

Use per-service secret scopes. Do not share the DB administrator credential between API and worker.

## 20.1 `.env.example`

The repository may contain placeholders only:

```dotenv
ARIVO_ENV=development
PORT=8000
SUPABASE_URL=https://wcuuakhdmsmmxagvbdmg.supabase.co
SUPABASE_PUBLISHABLE_KEY=<public-key>
SUPABASE_JWT_ISSUER=<verified-issuer>
SUPABASE_JWKS_URL=<verified-jwks-url>
DATABASE_URL=<runtime-arv-app-connection-with-ssl-verification>
ARIVO_STORAGE_BUCKET=arivo-sources
ARIVO_BLOB_BACKEND=local
ARIVO_API_BASE_URL=http://127.0.0.1:8000
ARIVO_ALLOWED_ORIGINS=<exact-allowed-origins>
ARIVO_LOG_LEVEL=INFO
```

Add a privileged migration connection only to a protected release secret environment. Never add it to API/worker service variables. Never commit actual `.env` files.

---

# 21. Prohibited shortcuts

1. Rebuilding the existing backend from scratch.
2. Replacing the canonical server database with another DB.
3. Removing the loopback guard from the local adapter.
4. Exposing the `arv` schema directly to the desktop Data API.
5. Desktop direct PostgreSQL access.
6. Privileged Supabase keys embedded in the desktop.
7. PostgreSQL superuser as API runtime login.
8. A second migration history.
9. Supabase CLI commands run without explicit local/remote target awareness.
10. Reusing client/server outboxes as the generic job queue.
11. Claiming DB and Storage writes are one atomic transaction.
12. Committing a Source before stored bytes are verified.
13. Inventing a custom domain or changing DNS without owner access.
14. Creating paid services/plan upgrades without owner approval.
15. Installing `vector` or calling paid embedding APIs before Q7 approval.
16. Declaring completion based only on build/schema/HTTP 200.
17. Silently closing Q11, Q12 or Q7.
18. Touching unrelated projects, keys or services.
19. Claiming deployment without provider access and live health verification.
20. Adding unrelated external infrastructure to Arivo's code or schema.

---

# 22. Required executor report

At the end of every wave, report:

1. Starting and final commit SHA.
2. Branch and PR URLs.
3. Files changed.
4. Migrations added/applied and checksums.
5. Supabase project ref verified.
6. Schema, role, RLS and Storage state.
7. Runtime provider, service names, regions and generated HTTPS URL.
8. TLS verification results for public API and database connections.
9. Tests and exact exit codes/CI results.
10. SEV disposition and review findings.
11. Security/advisor results.
12. Credentials/configuration still needed from the owner, named but never shown.
13. Paid-resource/cost status.
14. Open decisions and exact blocked dependents.
15. Not-verified items.
16. Exact next action.

Never report secret values.

---

# 23. Final production definition

The Arivo full-stack backend is ready only when:

- The existing backend kernel runs against the production Supabase PostgreSQL project through the remote adapter.
- The API authenticates users and derives owner scope correctly.
- RLS and command-level ownership rules hold under real concurrent requests.
- Source bytes live in private object storage with verified staging and recovery.
- Background jobs run through a durable crash-safe worker system.
- The actual desktop application uses the API over HTTPS and authenticates through Supabase Auth.
- Offline changes sync without silent loss or duplicate logical effects.
- Import, reading, capture, journal, references and retrieval work end-to-end in the desktop client.
- Backups and restore have been tested, including private source objects and purge behavior.
- CI, SEV, security review and owner-fidelity validation pass.
- Remaining advanced retrieval capabilities stay explicitly separated by their own phase and approval gates.

The target is a working Arivo product, not a collection of deployed services that do not yet form one usable system.

## §17 Deployment (Workstream 10 — the runtime-neutral container + the tunnel front)

1. **The image**: `docker build -t arivo:<sha> .` — python:3.12-slim, the locked
   requirements, the pg client, a non-root user; the three start commands: `api`
   (`python3 -m harness.api`, :8080, the fail-closed secret matrix), `worker`
   (`python3 harness/worker.py --name <id>`, the durable loop), `migrate`
   (`python3 harness/migrate.py`, the release oracle — run before api/worker).
2. **The front** (the Q18-ratified form): the Cloudflare Tunnel — `cloudflared`
   with outbound-only 443; the ingress hostname `arivo.itscatalyst.com` ->
   `http://localhost:8080`; the edge cert + the tunnel's origin cert (no inbound
   ports, no origin IP exposure). DNS: the tunnel's CNAME, proxied.
3. **The release order**: migrate -> api -> worker (the health gate between:
   `/health/ready` green before the worker starts).
4. **The verification** (§16's own list): public HTTPS valid; origin TLS; the
   database `verify-full`; CORS matrix; the rate limits; the host validation;
   the MCP `/mcp` surface answering initialize.
5. **The secrets**: the matrix at `harness/api/env.example.txt` — every name,
   its consumer, its class; the tunnel token and the database password are the
   two secrets the runtime holds; nothing else.
