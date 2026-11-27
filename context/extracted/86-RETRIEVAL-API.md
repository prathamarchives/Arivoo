# 86 — RETRIEVAL-API (the §11.2 Retrieval API — the Workstream 5 slice)
> STATUS: SESSION ENGINEERING RECORD (2026-11-27; the session's intent refs: INT-162/168; D refs: D-042/D-047/D-053). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 123. PRs this session: #143 (this slice).

## 1. What the owner asked (verbatim — owner turn 48, 2026-11-27)
> "resume dont stop until everything done" — the standing chain under INT-162's end-to-end directive; this slice is Workstream 5 (the retrieval API).

## 2. Starting state
- main at `584adb1` (the PR #142 merge — CLAIM-100, the Workstream 4 capture wave COMPLETE; five checks green at the head `33d0168` and on the merge; the branch deleted; 0 open PRs).
- The rig green at main.

## 3. Task and scope
- The requested work: the directive's Workstream 5 — the §11.2 Retrieval row (keyword search + bounded context packs with provenance/trust) over the query kernel's OWN search/pack arms. Deterministic only — Q7's boundary held (no semantic/model work).
- Bounded scope: routes.py + the battery + the markers + the red record + the run records + the shared-append bookkeeping + this record.
- Non-scope: Workstreams 6-11, any kernel change, any migration, any semantic work.

## 4. Results
- Two routes: GET /api/v1/search?terms=a&terms=b (the AND-semantics admission — the kernel arm's own contract: the full admission list, NO paging parameters the arm does not carry) and GET /api/v1/context-packs?terms=a&budget-bytes=N (the provenance-carrying assembly: the trust labels, the matched terms, the why; the trailer metadata kept/total/truncated/budget_bytes/used_bytes/after TYPED at the boundary — integers and booleans, never strings the client re-parses).
- The ONE pipe-framed page parser (`_pipe_page`): the kernel arms' own `# api_version=1 col|col|...` header + pipe rows + `# more=` trailer contract parsed at one place — never a second framing law.
- The §11.4 map grows the KWR-003 422 (the read-side token bound). The write-side KWR-002 stays on the fallback map (the map-family followup, now with the alternation's named-409 candidate — two members).
- THE MID-SLICE REPAIRS (the honest account): (1) the retrieval-routes edit's anchor consumed `remove_list_member`'s tail — the CLAIM-100 checks' own regression (142/143 RED) caught it immediately, restored before evidence; (2) the search arm carries no --limit/--after — the first route draft passed them, the kernel refused (argparse exit 2, the honest ARV-API-500), the fix honors the arm's own contract; (3) the admission list's row ORDER (the corpus's captures admitted alongside the source) — the checks now assert PRESENCE, not position.

## 5. Files changed
- `harness/api/routes.py` (two routes + the `_pipe_page`/`_terms_query` helpers + the map row + the restored remove tail) — INT-168
- `harness/api/routes_selfcheck.py` (ARV-API-153..164) — INT-168
- `harness/tests/test_api_routes.py` (markers 153..164) — INT-168
- `harness/red-records.json` (the RED bound to 15d59f7) — INT-168
- `CLAIMS.md` / `STATE.md` / `context/WORKLOG.md` / `INTENT-LEDGER.md` / `AGENTS.md` — INT-168
- `harness/runs/claim-101-retrieval-api/` — INT-168
- this record — INT-168

## 6. Commands and external actions (ACTUAL — never reconstructed)
- The kernel probes: `search --owner o quick fox` (the pipe rows; AND admission), `pack --owner o quick --budget-bytes 2000` (the trailer: more/kept/total/truncated/budget_bytes/used_bytes/after), the no-match exit-0 empty page, `--budget-bytes 0` → ARV-QRY-004
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` @ `15d59f7` → exit 1 → 12 failures (ALL substantive — no vacuous 404s in this family)
- The battery at the implementation head → three repair rounds → exit 0 → 180 PASS
- `python3 tools/verify_canonical_layer.py` → exit 0 (150 intents); `python3 harness/tests/test_api_routes.py` → exit 0
- The run records: three (the battery, the canonical layer, the suite)

## 7. Evidence
- RED: harness/red-records.json (the 101 record, binding_commit 15d59f7)
- GREEN: harness/runs/claim-101-retrieval-api/run-01..03.json (all exit 0)
- The SEV: harness/runs/claim-101-retrieval-api/sev.json + the round report
- The sheet: harness/runs/claim-101-retrieval-api/proofsheet.md

## 8. Honest accounting
- The anchor-tail consumption (the remove route destroyed by the edit script's anchor) was caught by the PREVIOUS slice's own checks — the battery's cumulative regression net working exactly as designed; the fix preceded any evidence run.
- The search route's first draft invented paging the kernel arm does not carry — the §11.3 lesson in reverse: the adapter must not invent parameters any more than semantics.

## 9. What remains open
- Workstream 6 (sync/export/restore/purge), 7 (the remote MCP transport), 8 (storage after its gate), 9 (workers), 10 (runtime+domain after Q18), 11 (the acceptance campaign).
- The map-family followup (the KWR-002 row + the alternation's named-409 candidate).
