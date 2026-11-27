# 87 — SYNC-EXPORT-PURGE (the §11.2 Sync + Export/restore rows + the governed purge — the Workstream 6 slice)
> STATUS: SESSION ENGINEERING RECORD (2026-11-27; the session's intent refs: INT-162/169; D refs: D-011/D-029/D-042/D-053). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 124. PRs this session: #144 (this slice).


Session 65, 2026-11-27. The directive's Workstream 6: the §11.2 'Sync' + 'Export/restore'
rows + the governed-purge surface, over the kernel's own machines and MIGRATION 0021's
erasure procedure. Branch `slice/claim-102-sync-export-purge`, base main `a17f0b5`.

## §1 What landed

1. **GET /api/v1/sync/outbox** — harness/sync.py's own `status` arm through the
   adapter: the counts-by-state object + the queued rows (key/state/attempts only —
   the payload never served). The import's outbox row observable through HTTP
   (pending=1 after a fresh import — the sync-intent record).
2. **POST /api/v1/sync/deliver** — the kernel's own two-database outbox walk
   (`sync.py sync`): mark-delivered → apply through the SAME command kernel on the
   target db (ARV_SITE=server, D-018) → the typed per-row states
   (acknowledged/retryable/failed/uncertain). The TARGET database is a SERVICE
   parameter (ARIVO_SYNC_TARGET_DB) — never a client value; an unconfigured service
   refuses the named ARV-SYN-014 503, never a guess. The walk's per-row line
   protocol parsed to the states map; the second pass never re-walks a terminal row.
3. **GET /api/v1/export** — harness/export.py's versioned manifest (format
   arv-export-1) staged under the SERVICE's root (ARIVO_EXPORT_ROOT, the owner's
   own subdirectory); the route serves the manifest (the authoritative table set +
   the canonical state hash); the blobs stay staged server-side under their
   digests. An unconfigured root refuses the named ARV-EXP-008 503.
4. **POST /api/v1/restore** — the recovery path over the OWNER-MATCHED staged
   archives only: the manifest_name is a bounded name (no paths, no traversal —
   ARV-PRG-002), the archive's owner must MATCH the verified caller (a cross-owner
   archive is the same 404 as an absent one — the no-oracle law at the archive
   boundary), the idempotency key required (§11.3).
5. **GET /api/v1/purge-ledger** — the owner's own erasure record (D-011's minimal
   audit surface), bounded + paginated (the (kind, entity_id) keyset cursor).
6. **POST /api/v1/purge** — the governed purge over MIGRATION 0021's
   `arv.governed_purge`.
7. **MIGRATION 0021 (the erasure machine)** — D-011's missing erasure half, until
   now test-substrate-only (the prior suites wrote ledger rows directly; the
   content DELETE was refused by every trigger — the exact gap ARV-CAP-005's
   letter names: "the owner-run purge is the only authorized erasure"). The
   design: ONE SECURITY DEFINER procedure `arv.governed_purge(p_owner, p_kind,
   p_entity_id, p_reason)` holding the ONLY authorized content-DELETE path:
   - the LEDGER-FIRST check order (the permanence record outranks the existence
     read — a purged object's content rows are gone, so existence-first would
     answer the no-oracle 404 for an already-purged object instead of the
     ARV-PRG-004 alternation);
   - the no-oracle existence check (absent and another owner's are the SAME
     ARV-PRG-003 404);
   - the capture precedence (a capture whose SOURCE is already purged refuses
     ARV-PRG-005 — the source's erasure carried the tree);
   - ONE transaction: the ledger write + the family cascade (the note's
     lifecycle/references BOTH directions; the capture's anchors/lifecycle; the
     source's whole tree incl. passages/generations/positions/sessions/
     list-memberships/source-bound journal blocks; the work's recursive source
     cascade) + the derived keyword-index rows + the inbound reference cleanup —
     all-or-nothing (a failed cascade rolls the LEDGER row back too);
   - the append-only triggers stay ARMED everywhere else: the definer-scoped
     `SET LOCAL arv.purge_in_progress` marker (transaction-local, set INSIDE the
     definer frame after the checks pass); the six amended rejector functions
     consult `arv.purge_authorized()` and keep the ORIGINAL named codes and
     wording byte-for-byte (EV-001/EV-002/SYN-007/POS-005/SES-006/JNL-006 — the
     suites' assertions pin them);
   - the EXECUTE grant to arv_app at the PROCEDURE level only (nobody holds
     table-level DELETE).
8. **The §11.4 map grows** — SYN-013 422, EXP-002 409, EXP-003/004/005 422,
   PRG-001 409, PRG-002/003 422, PRG-004/005 409 (the centralized map, one place).

## §2 Verification

- **RED observed** at the battery-only commit `368eb8d` (pre-slice main `a17f0b5` +
  the battery + the markers): exit 1, 32 checks failing — the routes and the
  migration do not exist (165 vacuous through the import hand — the corpus itself
  lands; the rest substantive).
- **GREEN** at the implementation head (218 PASS total in the battery) — after
  three real repairs the RED discipline caught:
  1. the substrate refused the content DELETE (ARV-CAP-005) — the erasure machine
     did not exist; migration 0021 written (the SEV-class catch: the route's first
     draft did the ledger write + drops through the adapter and the battery
     refused on the first run);
  2. the procedure's uuid-vs-text comparison on keyword_index.entity_id (uuid
     column — the ::text casts dropped);
  3. the check order (existence before ledger) — the alternation test caught it:
     the second purge of a purged note answered 404 instead of 409;
  4. the guard-message drift (my rewrites carried different codes — POS-004/SES-005
     instead of the originals POS-005/SES-006; test_sync's SYN-11 assertion caught
     every one; the amended rejectors restored byte-for-byte).
- **The substrate-affected suites re-observed GREEN**: test_migrations, test_substrate,
  test_kernel, test_sync (SYN-01..23), test_export (EXP-01..15), test_highlight,
  test_bookmark, test_note, test_note_reference, test_journal, test_reading_list,
  test_agent_access, test_recovery_contract (RCW-01..08) — the 0021 trigger
  amendments change nothing the prior suites assert.
- The battery's restore leg: the SYS-10 reconciliation proof (the destination's
  ledger row survives the restore; the ledgered source does NOT resurrect from
  the archive; the archive's non-ledgered content restores).

## §3 Not verified (LAW-04)

- the five PR-head CI checks and this PR's D-042 review (observed after the PR
  opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the
  deployed route surface (the Workstream 10 slice)
- the multi-database restore TOPOLOGY through the route (the route's restore
  restores into the SERVICE's db; the battery's reconciliation leg drives the
  kernel directly on a second scratch db — the deployment's own topology
  composes the two)
- the sync delivery's desktop-over-HTTP transport client (Q19's local-store
  contract open — the backend surface is complete; the client side is the
  desktop repo's own work)
- the 0021 machine on the REMOTE project (the migration applies locally; the
  remote application is the guarded migration act's own slice — the Supabase
  migration credential never provided to this session)
- the KWR-002 map row (the map-family followup, unchanged from the prior slices)

## §4 Residuals / follow-ups

- The purge of a WORK recursively calls the source cascade per source (each
  source its own ledger row) — the work's own ledger row lands LAST; a crash
  mid-recursion leaves the already-ledgered sources final (correct) and the work
  row un-purged (the re-run refuses ARV-PRG-004 for the done sources and
  completes the remainder — the honest re-run shape, disclosed here).
- The blob erasure (D-011's "unreferenced blobs" clause) rides the recovery
  walk's sweep (recover.py) — the blob store's content-addressed residents are
  swept when unreferenced; the purge route does not itself unlink blobs (the
  sweep is the existing machine, its own evidence in RCW/IMP suites).
- STATE re-derived; the 101 close row appended (rule 4); Task 124 + this record.
