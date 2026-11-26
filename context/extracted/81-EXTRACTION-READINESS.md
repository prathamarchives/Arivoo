# 81 — THE EXTRACTION/READINESS AREA + THE REMOTE 0020 APPLICATION
> STATUS: SESSION ENGINEERING RECORD (2026-11-26; INT-163; D-055). Historical
> process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 118.
> PRs this session: #137 (merged, record 80) + this slice's PR (number in §12 at close).

## 1. What the owner asked (verbatim — owner turn 47, 2026-11-26)
> resumeee and execte all workstreams

The governing authority remains the turn-46 directive (INT-162/D-054, record 80 §1;
verbatim at context/raw/ARIVOO_END_TO_END_BACKEND_EXECUTION_DIRECTIVE.md): execute
every remaining workstream in order, batched per §3, gates blocking only their named
scopes.

## 2. Starting state
- main at `5062510743a14a463bced0e553e2b7ce3d36817e` (PR #137's merge — CLAIM-095),
  observed live after fetch; 0 open PRs; CLAIM-095's close pending (this slice carries it).
- The sandbox survived intact this cycle (the rig, the venv, the secrets all present —
  no rebuild needed).
- **Workstream 1's blocker, resolved:** the release-env migration credential (the
  database password) did not survive the recycle and was never recorded (by design —
  record 089's own law). Re-established through the management API:
  `PATCH /v1/projects/{ref}/database/password` (the endpoint found in the live OpenAPI
  spec, not guessed) with a fresh 36-char random value stored ONLY at
  `/home/z/my-project/.secrets/supabase-db-password` (chmod 600; never printed, never
  committed — the §7 credential rules). Consequence honestly noted: the old password is
  invalid; the owner's dashboard-stored password (if any) is superseded.

## 3. Task and scope
- **Workstream 1 (the remote 0020 application):** the live ledger verified still 1–19
  (ARV-MIG-010: 0020 not applied); applied through `harness/migrate.py --remote-target
  wcuuakhdmsmmxagvbdmg` (the guarded canonical path: the pinned pooler host, port 5432,
  sslmode=verify-full, the credential in PGPASSWORD only); re-verify: 20/20 checksums
  match. Independent verification (raw psql through the same guarded env): the ledger
  row (20, `e068284d04e6`), arv_app/arv_read default search_path `pg_catalog, public`,
  agent_token_lookup pinned `pg_catalog, arv` (the ONLY definer function), RLS
  enabled+forced 26/26 owner tables, the arv_app keyword_index grants
  (SELECT/INSERT/DELETE), the arv schema present. `arv_migrate` is not on the remote
  (a local-rig role; consistent with the prior sessions' shape). Recorded as D-055.
- **Workstream 3 (CLAIM-096):** the §11.2 extraction area — the kernel read arm
  (`extraction-status`: ONE statement deriving the truthful readiness from the
  generation rows; the 0006 vocabulary; passage_count from the CURRENT generation
  only; the derived retryable/extractable flags) + the two routes (POST/GET
  /api/v1/sources/{id}/extraction; §11.3 write law; ARV-EXT-004 no-leak 404;
  ARV-EXT-001/005 content-class 422).
- Non-scope: the passage-content serving route (the reader family, Workstream 4); the
  worker-driven extraction (Workstream 9); Q7/Q8 gates untouched.

## 4. Results
- The remote migration chain is COMPLETE and verified (ledger-equivalent local/remote
  at 20). The roles' hijack-proof defaults are live on the remote.
- The extraction area is served: the truthful readiness (never a partial extraction
  presented as complete — the passage count is the CURRENT generation's only), the safe
  retry (the same key replays/resumes), the safe rebuild (a new key supersedes), the
  interrupted-build resume (the kernel's crash point driven directly in the battery),
  the cross-owner no-leak on both arms.
- The 095 close row + STATE re-derivation + Task 118 + this record ride the slice per
  the directive's ride order.

## 5. Files changed
- `harness/query.py` — EXTSTATE_SQL + the extraction-status subparser/dispatch.
- `harness/api/routes.py` — the two routes + the ARV-EXT mappings in §11.4's map.
- `harness/api/routes_selfcheck.py` — ARV-API-022..033.
- `harness/tests/test_api_routes.py` — the marker list extended.
- `harness/red-records.json` — the 096 red record (binding 2891c50).
- `harness/runs/claim-096-extraction-readiness/` — scope.txt, runs, proof sheet, SEV.
- The bookkeeping: CLAIMS/STATE/INTENT-LEDGER (INT-163)/DECISIONS (D-055)/AGENTS
  (145)/WORKLOG (Task 118)/this record.

## 6. Commands and external actions (ACTUAL)
- Live ledger read: `python3 harness/migrate.py --verify` (remote env) → ARV-MIG-010
  (0020 not applied — the directive's expected state, confirmed).
- Apply: `python3 harness/migrate.py` (remote env) → `applied 0020_search_path_pins`,
  exit 0; re-verify → `verify OK: 20 migration(s) applied, checksums match`.
- The independent probes (§3) through `psql` in the same guarded env — outputs in §2/§3.
- The management API password reset: `PATCH .../database/password` → 200
  `{"message":"Successfully updated password"}`.
- RED: `python3 harness/tests/test_api_routes.py` at 2891c50 (impl stash-verified
  absent) → exit 1 (ARV-SUITE-001 + ARV-API-022..030); `harness/red.py` bound it.
- GREEN: `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` at `1e47603` →
  exit 0, 33 route checks GREEN; the extraction-status smoke (never_requested → ready;
  the cross-owner ARV-QRY-001 no-leak).

## 7. Evidence
- `harness/runs/claim-096-extraction-readiness/` (run-01..03 + proofsheet +
  notverified + sev.json).
- The 095 merge facts (record 80 §2, observed live pre-close).

## 8. Failures
- The battery's own ARV-API-023 probe omitted the Authorization header (the auth
  boundary answered 401 before the §11.3 check): a test bug, repaired (the probe now
  rides an authenticated request); the route was correct.
- No product-code defect found.

## 9. Unverified items
- A live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed
  route surface (the Workstream 10 slice); the battery's five PR-head checks and this
  PR's review (observed after the PR opens); the remote's btree/TOAST parity for the
  095 bound (carried from record 80).

## 10. Open decisions
- Q18 (compute) — blocks only the deployment; Q12/Q17 (storage) — block only the
  provider-specific implementation; Q7/Q8 — the semantic/extraction-corpus gates;
  Q19, Q6, Q9, Q10, Q11, Q16, D-014 — unchanged.

## 11. Next action
Workstream 4: the reader/capture route families (position+content serving first, then
highlights, bookmarks, notes, journal, @refs, reading lists — grouped per §3.4), each
family its own bounded claim; maxima checked first.

## 12. Session close
- (filled at the slice's merge)
