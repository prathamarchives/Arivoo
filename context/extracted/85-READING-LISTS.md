# 85 — READING-LISTS (the §11.2 Reading lists family — the Workstream 4 capture wave complete)
> STATUS: SESSION ENGINEERING RECORD (2026-11-27; the session's intent refs: INT-162/167; D refs: D-042/D-047/D-053). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 122. PRs this session: #142 (this slice).

## 1. What the owner asked (verbatim — owner turn 48, 2026-11-27)
> "resume dont stop until everything done" — the standing chain under INT-162's end-to-end directive: the §11.2 route families in order; this slice completes Workstream 4's seventh and final family.

## 2. Starting state
- main at `ad1c1bb` (the PR #141 merge — CLAIM-099, merged 2026-11-27 under INT-145; five checks green at the head `37f96c7` and on the merge commit; the branch deleted; 0 open PRs).
- The rig green at main (the 099 battery re-verified before the branch opened).

## 3. Task and scope
- The requested work: the directive's Workstream 4 family 7 — the §11.2 Reading lists operations (create/list/member add/remove/current membership) over the EXISTING kernel arms (D-053's adapter law).
- Bounded scope: routes.py + the battery + the markers + the red record + the run records + the shared-append bookkeeping + this record.
- Non-scope: retrieval/sync/export (Workstreams 5-6), the remote MCP transport, storage/workers/runtime, any kernel change, any migration.

## 4. Results
- Five routes: POST /api/v1/reading-lists (the name law at the kernel; the uuid identity — names may duplicate, Q11's baseline held), GET /api/v1/reading-lists (the bounded page with the DERIVED member count), GET /api/v1/reading-lists/{id} (the current membership — the derived view), POST /api/v1/reading-lists/{id}/members + DELETE /api/v1/reading-lists/{id}/members/{source_id} (the append-only event writes).
- The §11.4 map: the RLS-003 422 (the name law); the RLS-001/002 no-oracle 404s (the list and the binding).
- THE ROUTE-SIDE REPAIR (the honest account): the first draft of the membership read 404'd the EMPTY page — conflating "no rows" with "absent list". The kernel's own shapes discriminate cleanly: an existing-but-empty list answers exit 0 with header+more=false (a 200 page); the absent list refuses ARV-QRY-001 at exit 1 (the no-leak 404 through the map). The repair keeps the discriminator at the kernel's exit semantics, never a second existence probe.
- The duplicate-add alternation surfaces as the substrate's ARV-RLS-008 exception through the spine's honest ARV-CMD-010 unknown — the route's §11.4 fallback answers 500 with the named code, the raw cause never echoed (pinned by ARV-API-140).

## 5. Files changed
- `harness/api/routes.py` (five routes + the map rows + the empty-page repair) — INT-167
- `harness/api/routes_selfcheck.py` (ARV-API-132..152) — INT-167
- `harness/tests/test_api_routes.py` (markers 132..152) — INT-167
- `harness/red-records.json` (the RED bound to fd49144) — INT-167
- `CLAIMS.md` / `STATE.md` / `context/WORKLOG.md` / `INTENT-LEDGER.md` / `AGENTS.md` — INT-167
- `harness/runs/claim-100-reading-lists/` — INT-167
- this record — INT-167

## 6. Commands and external actions (ACTUAL — never reconstructed)
- The kernel probes (the alternation behavior pinned BEFORE the battery was written): add_to_list duplicate → exit 1, FAIL ARV-CMD-010 with the raw ARV-RLS-008 cause; remove_from_list duplicate → the same class; list-lists/get-list → the JSON row shapes (the derived member_count; the source_id+added_at membership row)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` @ `fd49144` → exit 1 → 21 failures (132..151 substantive; 152 vacuous — disclosed)
- `python3 harness/red.py --red-commit fd49144 ...` → OK ARV-RED-005
- The battery at the implementation head → exit 1 (one failure: ARV-API-142 the empty-page conflation) → the route repair → exit 0 → 168 PASS
- `python3 tools/verify_canonical_layer.py` → exit 0 (149 intents); `python3 harness/tests/test_api_routes.py` → exit 0
- The run records: three (the battery, the canonical layer, the suite) at harness/runs/claim-100-reading-lists/

## 7. Evidence
- RED: harness/red-records.json (the 100 record, binding_commit fd49144)
- GREEN: harness/runs/claim-100-reading-lists/run-01..03.json (all exit 0)
- The SEV: harness/runs/claim-100-reading-lists/sev.json + the round report
- The sheet: harness/runs/claim-100-reading-lists/proofsheet.md

## 8. Honest accounting
- The empty-page conflation was caught by the battery's own 142 check (the RED-first discipline working as designed) — a route-side bug, repaired before any evidence run was recorded.
- The alternation's HTTP shape (the honest ARV-CMD-010 500) is pinned as OBSERVED behavior, not redesigned: the substrate guard is the kernel's own law; a named-409 mapping would be a map-family decision (the KWR-002 followup's sibling).

## 9. What remains open
- Workstream 5 (the retrieval API: search/context packs), 6 (sync/export/restore/purge), 7 (the remote MCP transport), 8 (storage after its gate), 9 (workers), 10 (runtime+domain after Q18), 11 (the acceptance campaign).
- The KWR-002 map row (the 099 SEV's named followup) — a §11.4 map-family slice candidate, now with the RLS-008/ARV-CMD-010 alternation shape as its second member.
