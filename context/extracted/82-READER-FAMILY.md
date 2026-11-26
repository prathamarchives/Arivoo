# 82 — THE READER FAMILY (STATE + CONTENT SERVING)
> STATUS: SESSION ENGINEERING RECORD (2026-11-26; INT-164). Historical
> process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 119.
> PRs this session: #137/#138 (merged) + this slice's PR (number in §12 at close).

## 1. What the owner asked (verbatim — owner turn 47, 2026-11-26)
> resumeee and execte all workstreams

The governing authority: the turn-46 directive (INT-162/D-054) — every remaining
workstream in order, batched per §3, gates blocking only their named scopes.

## 2. Starting state
- main at `e14fea1663ab71026d9b33a272c2410b19f34eac` (PR #138's merge — CLAIM-096),
  the 0020 remote application complete (D-055), 0 open PRs.
- The battery at this slice's start: 33 route checks (ARV-API-001..033).

## 3. Task and scope
- The §11.2 Reading area family 1 (the directive's Workstream 4 item 1): the position
  round-trip, the session events, the derived reading state, the anchor resolution —
  six routes over the EXISTING kernel arms (no kernel change: query.py's get-position/
  get-reading-state/list-session-events/resolve-anchor and commands.py's save_position/
  record_session), plus the shared bounded JSON-body reader.
- Non-scope: the capture families (CLAIM-098/099/100), the passage-text serving
  decision (the anchor resolution carries the offsets+digests+context windows; the
  passage rows are the extraction generation's own — the reader-content serving rides
  the capture families' slice where the highlight/bookmark windows need them), Q19.

## 4. Results
- The position contract through HTTP: the honest no_position_saved ANSWER (a 200
  state, never a failure) before any save; the serialized save (the kernel's
  advisory-lock transaction — competing savers serialize); the reopen's saved window
  + saved_generation_id + current_generation_id + the derived generation_matches
  (never a silent retarget); the idempotent replay.
- The session surface: the D-010 closed vocabulary enforced at the adapter
  (ARV-SES-004 → 422 for anything outside session_start/checkpoint/dwell/session_end);
  the dwell_ms requirement on dwell; the recorded stream bounded + paginated.
- The reading state: the derived view over the SAME _position_row builder the reopen
  uses (the no-second-path law — the view cannot drift from the arm it derives from).
- The anchor resolution: the typed content-addressed answer (the offsets, the digests,
  the context windows, the current generation binding) — the §11.2 'source/read data'
  surface in its content-addressed form.
- THE BATTERY'S OWN DISCOVERY (the honest shape-learning): save_position/record_session
  require the source EXTRACTED first (the position binds to the serving generation —
  the kernel's own law, ARV-CAP-005's class); the battery's flow now extracts first
  through the 096 route — the prerequisite is itself pinned as ARV-API-034's first half.

## 5. Files changed
- `harness/api/routes.py` — the six routes + `_json_body` (the bounded shared reader).
- `harness/api/routes_selfcheck.py` — ARV-API-034..045.
- `harness/tests/test_api_routes.py` — the marker list.
- `harness/red-records.json` — the 097 red record (binding 0ce1be9).
- `harness/runs/claim-097-reader-family/` — scope.txt, runs, sheet, SEV.
- The bookkeeping: CLAIMS/STATE/INTENT-LEDGER (INT-164)/AGENTS (146)/WORKLOG (Task 119)/this record.

## 6. Commands and external actions (ACTUAL)
- RED: `python3 harness/tests/test_api_routes.py` at 0ce1be9 (impl stash-verified
  absent) → exit 1 (12 failures); `harness/red.py` bound it.
- GREEN: `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` → exit 0,
  45 route checks GREEN at the final head.
- The shape probes (the kernel's own outputs on a scratch rig db): get-position's
  saved/no_position_saved answers, list-session-events' JSON rows, get-reading-state's
  derived rows, create_highlight's ack (result_ref only — the anchor read through
  get-capture).

## 7. Evidence
- `harness/runs/claim-097-reader-family/` (run records + proofsheet + notverified + SEV).

## 8. Failures
- The battery's first form asserted a "position_saved" state and a session-events
  row shape the kernel does not produce — three shape-learning repairs (the kernel's
  own vocabulary is the contract; the battery learned it, the routes needed no change).
- The battery's first position save ran before extraction (the kernel refused — the
  serving-generation law); the flow now extracts first.
- No product-code defect: the routes needed no repair across the whole battery run.

## 9. Unverified items
- The five PR-head checks + this PR's review (after the PR opens); a live Supabase
  token; uvicorn on a real socket; the deployed surface; the carried items from
  records 80/81.

## 10. Open decisions
- Q18/Q12/Q17/Q7/Q8/Q19/Q6/Q9/Q10/Q11/Q16, D-014 — unchanged, each blocking only
  its named scope.

## 11. Next action
CLAIM-098 — the highlights + bookmarks capture families (create/revise/tombstone/
restore/list/history through the kernel's own revision/lifecycle machines), maxima
checked first.

## 12. Session close
- (filled at the slice's merge)
