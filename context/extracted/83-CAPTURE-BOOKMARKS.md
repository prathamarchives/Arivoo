# 83 — CAPTURE-BOOKMARKS (the §11.2 Highlights + Bookmarks families + the 097 named followup)
> STATUS: SESSION ENGINEERING RECORD (2026-11-27; the session's intent refs: INT-162/165; D refs: D-042/D-047/D-053/D-054). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 120. PRs this session: #140 (this slice).

## 1. What the owner asked (verbatim — owner turn 47, 2026-11-27)
> "hey" — then the standing chain's execution turn: the 2026-11-26 end-to-end directive (INT-162, verbatim at context/raw/ARIVOO_END_TO_END_BACKEND_EXECUTION_DIRECTIVE.md) governs this session: "Do not return another plan. Reconcile the current merged state, close the outstanding bookkeeping, and start the next implementation workstream... Continue sequentially through the entire backend end state" — with the freshly supplied provider credentials (GitHub/Cloudflare) stored in the session's persistent secret store, never in any repo file.

## 2. Starting state
- main at `0d4b861` (the PR #139 merge — CLAIM-097's reader family, merged this session under INT-145's standing authorization after its five checks were observed green at the head `c99b8c4` and on the merge commit; the D-042 merge-gate review id 6075783689 carried SEV-097-2's named followup: the cross-owner legs land in CLAIM-098's battery); 0 open PRs; the branch deleted.
- The session rig rebuilt from scratch after the sandbox recycle: PostgreSQL 17.12 built from source into `/home/z/my-project/pgbuild/root` (bison/flex/m4 extracted from the distro packages — the from-source path), the cluster initialized at `/home/z/my-project/pgdata`, the pinned venv recreated (fastapi 0.164.0/starlette 1.10.0/uvicorn 0.54.0/psycopg 3.3.9/psycopg-pool 3.3.3/pyjwt 2.15.1/cryptography).
- Preflight: `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` @ `0d4b861` → exit 0 (the 45-check battery GREEN on the rebuilt rig — the environment proven before any edit).

## 3. Task and scope
- The requested work: the directive's Workstream 4 families 2-3 — the §11.2 Highlights and Bookmarks operation rows over the EXISTING kernel arms (D-053's adapter law: zero kernel changes), plus the 097 review's named followup (the cross-owner battery legs).
- Bounded scope: `harness/api/routes.py` + `routes_selfcheck.py` + `test_api_routes.py` + `red-records.json` + the slice's run records + the shared-append bookkeeping (CLAIMS/STATE/WORKLOG/INTENT-LEDGER/AGENTS) + this record.
- Non-scope: the notes/journal/references/reading-lists families (CLAIM-099+); the passage-text serving arm; the remote MCP transport (Workstream 7); storage/workers (Workstreams 8-9, their gates open); any kernel change (the adapter law); any migration.

## 4. Results
- Fourteen routes added: POST /api/v1/highlights (create — the selected text DERIVED server-side at the given offsets; the §11.3 idempotency law), GET /api/v1/highlights (the bounded page via the shared `_bounded_list` reader — tombstoned hidden by the kernel's own LIST_SQL), GET /api/v1/highlights/{id} (get-capture: the current revision + the anchor binding), GET /api/v1/highlights/{id}/history (the governed view), PUT /api/v1/highlights/{id} (revise — the serialized edit transition), DELETE /api/v1/highlights/{id} (tombstone), POST /api/v1/highlights/{id}/restore; the same seven over /api/v1/bookmarks with PUT = move (the serialized move transition; NO content copy — the structural law).
- The §11.4 map: the lifecycle alternation and edit-on-tombstoned codes are 409s (conflicts with the object's CURRENT state); the offset/content codes are 422s; the absence codes (HLC-001/BMK-001/CAP-002/POS-001/SES-001) join the no-leak 404 family — absent and another owner's are the SAME refusal everywhere, never a 403 existence oracle.
- THE NAMED FOLLOWUP landed: ARV-API-078..088 — owner B's token against owner A's objects across BOTH capture families AND the reader family's write surfaces (the position save/read, the session events, the reading-state, the anchors): empty lists, no-leak 404s with the kernel's own named codes.
- The battery's three mid-slice repairs (the honest account): the ack's parsed `revision` token (the check first asserted the raw ACK-line form `revision=2`, but the adapter parses the line into a dict — the check's own bug, not the route's); the cross-owner READ leg asserts the read path's own ARV-QRY-001 (not the write path's ARV-HLC-001 — the two arms have different absence codes by design); the third was the 098 red-form's own disclosure (see §6).

## 5. Files changed
- `harness/api/routes.py` (the fourteen routes + the map extensions + the shared `_bounded_list`/`_offset_body`/`_capture_argv` helpers) — INT-165
- `harness/api/routes_selfcheck.py` (ARV-API-046..088) — INT-165
- `harness/tests/test_api_routes.py` (the marker list grows 046..088) — INT-165
- `harness/red-records.json` (the RED record bound to 12bcbbf) — INT-165
- `CLAIMS.md` / `STATE.md` / `context/WORKLOG.md` / `INTENT-LEDGER.md` / `AGENTS.md` (the 098 open row, the 097 close row, INT-165, Task 120, the count 146→147) — INT-165
- `harness/runs/claim-098-highlights-bookmarks/` (scope, notverified, the run records, the SEV, the sheet) — INT-165
- this record — INT-165

## 6. Commands and external actions (ACTUAL — never reconstructed)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` @ `12bcbbf` (the test-only commit) → exit 1 → 36 failures: ARV-API-046..057, 059..065, 066..070, 072..075, 077..080, 082..084, 086 (the routes absent); the 404-shaped checks 058/071/076/081/085/087/088 pass vacuously through the absent-route path (the ARV-API-031..033 class, disclosed in the red record's note)
- `python3 harness/red.py --red-commit 12bcbbf --exit 1 --code "ARV-TEST-API-ROUTES (the 098 family reds...)"` → OK ARV-RED-005 (the record bound; test_api_routes.py already in TESTS — no new suite this slice, the 096 registration asymmetry class does not arise)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` @ `acc54ef` → exit 0 → 89 checks GREEN (99 PASS lines: the revalidation guards count the codes twice)
- `python3 tools/verify_canonical_layer.py` @ `acc54ef` → exit 0 (the checker green BEFORE the bookkeeping edits — the pre-edit tree is self-consistent)
- `python3 harness/tests/test_api_routes.py` @ `acc54ef` → exit 0 (the suite's ARV-SUITE-001 + the 046..088 markers green through the pinned venv)
- the SEV (LAW-30) and the proof sheet: the run records at harness/runs/claim-098-highlights-bookmarks/ (the fresh-context SEV round's own commands live in its round report)
- GitHub API: PR #139's checks observed (five green at `c99b8c4` + the merge commit `0d4b861`); the merge executed under INT-145's standing authorization; the branch deleted (204)

## 7. Evidence
- RED: harness/red-records.json (the 098 record, binding_commit 12bcbbf) + the run record of the red observation in this §6
- GREEN: harness/runs/claim-098-highlights-bookmarks/run-01.json (the battery, exit 0) + run-02.json (the canonical layer) + run-03.json (the suite)
- The SEV: harness/runs/claim-098-highlights-bookmarks/sev.json + sev-round-1.md (the fresh-context round; the disposition and findings recorded there)
- The sheet: harness/runs/claim-098-highlights-bookmarks/proofsheet.md (assembled, never hand-edited — ARV-PRF-004 verifies)

## 8. Honest accounting
- The battery's cross-owner READ leg first asserted the WRONG absence code (ARV-HLC-001 — the write path's code) against the read path's own ARV-QRY-001; the check's bug, repaired in-slice before any evidence run was recorded.
- The ack-shape assertion first used the raw ACK-line form (`revision=2`) against the adapter's PARSED dict; the check's bug, repaired in-slice (the 097 battery-repairs precedent class).
- The 404-shaped vacuity class at the red tree (058/071/076/081/085/087/088) is disclosed in the red record's note — the class is inherent to 404-shaped checks (the 096 review's reasoned-accept precedent).

## 9. What remains open (the §11.2 rows)
- Notes (create/read/revise/tombstone/restore/list/history), Journal (create/read/revise/list/history), References (the typed stable resolution), Reading lists (create/list/member add/remove/current membership) — CLAIM-099/100.
- Retrieval (search/pack), Sync, Export/restore — Workstreams 5-6. The remote MCP transport — Workstream 7. Storage/workers — Workstreams 8-9 (their owner gates open). Runtime + Cloudflare domain — Workstream 10 (Q18 open). The acceptance campaign — Workstream 11.
