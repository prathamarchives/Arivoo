# CLAIM-094 revalidation run record — the handoff pack's 10 questions

Date: 2026-11-25
Branch: slice/claim-094-routes-sources (revalidation commit, on top of 467ac0e)
Environment: local sandbox; PostgreSQL 17 rig at 127.0.0.1:5433 (fresh initdb
after a sandbox rollback corrupted the prior data directory); Python 3.12.16
venv, 21-wheel pinned closure (fastapi/uvicorn/pyjwt/cryptography + deps).
Command: `.venv-waved/bin/python -I harness/api/routes_selfcheck.py`
Exit code: 0 — GREEN — the routes battery passes (26 checks: 21 carried +
ARV-API-015..018 the revalidation additions).
Log: run-battery.log (this directory).

## Context

The owner-supplied handoff pack (ARIVOO_NEW_CLOUD_AGENT_HANDOFF, baseline
2026-11-24) required, before the CLAIM-094 PR, a revalidation of ten
verification questions against the live branch — treated as verification
questions, not pre-decided defects. Each was reproduced or measured before
any code changed.

## Findings and dispositions

- F1 — bounded request size enforced before unbounded buffering: DEFECT
  (adapter). `await request.body()` buffered the entire body before the cap
  check; a lying or chunked client could exhaust memory. FIXED: the declared
  Content-Length is refused 413 before any byte is read; the streamed body is
  cut off at MAX_IMPORT_BYTES mid-read. Checks ARV-API-016 (RED before the
  fix) and ARV-API-017 (regression guard) pin both halves.

- F2 — synchronous subprocess blocking the ASGI event loop: HYPOTHESIS
  DISPROVEN BY MEASUREMENT. Probes (both requests inside one event loop via
  gather, on a migrated rig db) ran real kernel writes of 0.09s–1.6s alongside
  a concurrent /health/live: health answered in 0.001s every time
  (health_delayed=no across four sizes, three repetitions). The route battery
  originally printed PASS for this question before the probes because the
  import kernel call fails fast (no db) in the battery context — the probe
  script closed that gap by migrating a dedicated db first. Disposition: no
  code change; ARV-API-018 pins the non-blocking behavior with a measured
  concurrency check so a future regression surfaces.

- F3 — service-controlled database configuration: OK. `_kernel_env` sets
  PGDATABASE from the app-level `db` parameter only (app.py reads
  ARIVO_API_DB at create_app); no client-supplied target exists on any route.

- F4 — unknown kernel errors misreported as 404: OK. Unnamed kernel failures
  raise ARV-API-500 (routes.py `_run_kernel`/`_query_kernel`); the 404 class
  is reserved for the no-leak absent-object case.

- F5 — mutually exclusive import selectors validated: DEFECT (adapter).
  The kernel validates title XOR work-id, but the adapter built argv with
  `if title ... elif work_id ...` — BOTH present silently dropped work_id.
  FIXED: the adapter refuses ARV-CAP-007 422 itself (the kernel cannot see
  what the adapter would have dropped). Check ARV-API-015 (RED before fix).

- F5b-note — malformed query output fails closed: OK. `_query_kernel`
  returns rows only from parseable lines; unparseable JSON lines are skipped
  but the page contract (api_version/more markers) governs; the detail route
  404s when no well-formed row returns. No silent drop of a refusal.

- F6 — large import bodies die at the KERNEL boundary: DEFECT (KERNEL,
  out of this slice's adapter scope). A body whose decoded text contains a
  very long unbroken token run (probe: a 2–24 MiB single-token body) reaches
  `_kwr_tokens`, which emits the whole run as ONE keyword token;
  `keyword_index_token` (btree on owner_scope, token, kind, entity_id,
  migration 0011) then exceeds the btree index-row size limit and the
  transaction dies ARV-CMD-010 ('index row requires ...'). Not fixed here:
  the adapter law forbids duplicating kernel behavior in routes, and the
  one-slice-per-claim discipline keeps this out of the routes slice.
  Disposition: register a follow-up kernel claim (tokenizer token-length
  cap + its own RED test). The adapter's 32 MiB body cap does NOT mask it
  (a 9 KB unbroken run in a normal-size document triggers the same path).

- F7 — owner/actor not overridable by the request: OK. `verified()` derives
  owner from the verified token's sub; the write argv hardcodes
  --actor owner; no route signature accepts owner/actor/client-supplied
  identity fields.

- F8 — credentials/connection strings never returned or logged: OK. Kernel
  refusals surface only the named code + message; acks carry the kernel's
  own fields; no env, DSN, or credential value is echoed. (The ARV-CMD-010
  raw-cause text from the kernel can include SQL error text — flagged as a
  minor follow-up for the F6 claim to tighten, not an adapter leak of
  credentials.)

- F9 — the test wrapper checks subprocess return codes and required output
  markers: OK. The battery asserts exit codes and named markers; the
  migrated-scratch-db pattern (ARV-API-001) gates the kernel-backed checks.

- F10 — readiness fails if a required DB check fails: OK in scope.
  /health/ready reports the service's declared state honestly (503 until
  declared); the pool-opening-at-serve-time contract is the adopted
  D-047/D-052 design; full live-DB readiness proof remains a
  deployment-slice item (already on the not-verified list).

## Sandbox incident (recorded for honesty)

Mid-revalidation the sandbox rolled the working tree back to a stale
CLAIM-084b-era snapshot: the uncommitted fixes, /tmp evidence, rig data
directory and venv were lost or corrupted. Everything was rebuilt from the
pushed branch head 467ac0e: the two adapter fixes re-applied, rig re-initdb'd,
venv re-created from the pinned closure, and the full battery re-run to the
GREEN above on the rebuilt stack. The run log in this directory is from the
rebuilt environment, post-rollback.

## Not verified (this revalidation)

- Remote Supabase: the live migration ledger read timed out from this
  sandbox (direct host unresolvable; pooler SNI route not reachable) — 0020's
  remote application state remains to be re-read from a working environment.
- A live Supabase-issued token end-to-end; uvicorn over a real socket;
  the route surface against the remote database (unchanged from the report's
  not-verified list).
- F6's exact minimum trigger size (a bounded-size RED test belongs to the
  follow-up kernel claim, not this record).
