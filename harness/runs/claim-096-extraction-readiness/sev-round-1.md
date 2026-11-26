# CLAIM-096 — SEV round 1 (the fresh-context systems-engineering verification)

- **Agent:** independent fresh-context SEV reviewer (reviewer-zsubagent-fresh-context-claim-096; not the slice author; no prior involvement in building this slice; a declared distinct context, not cryptographic independence — the protocol's stated limit)
- **Date:** 2026-11-26
- **Round:** 1
- **Base:** `5062510743a14a463bced0e553e2b7ce3d36817e` (origin/main, PR #137's merge — the merge-base observed by `harness.sev.merge_base_of`, and the parents verified from git: `5062510` = merge of `a81b270` (the 095 PR head) and `1eab74a1` (the prior main))
- **Head:** `58be295` (git ground truth at review time)
- **Chain (base → head):** `5062510` → `2891c50` (the RED: the battery only — routes_selfcheck.py's ARV-API-022..033 + the marker list) → `c4dc2ee` (the GREEN: query.py's EXTSTATE_SQL + the extraction-status arm; routes.py's two routes + the §11.4 mappings) → `1e47603` (the battery repair: the idem-key-less probe rides an authenticated request — the check's own bug, disclosed in record 81 §8) → `58be295` (the bookkeeping: INT-163 + D-055 + the 095 close + STATE + record 81 + Task 118 + the evidence runs)
- **Method:** every central claim re-executed live by this reviewer on the local PostgreSQL 17.12 rig (`source /home/z/my-project/pgbuild/env.sh`, PGPORT 5433): the 33-check route suite, the truthful-readiness semantics on this reviewer's OWN scratch db (migrated exactly like the battery), an in-flight-rebuild edge probe the battery does not have, the §11.4 map asserted in-process for all six ARV-EXT codes plus the ARV-EXT-001/005 kernel refusals re-executed live, the RED form re-observed at 2891c50 in a detached worktree (removed after), the gate's red-records/scope/claims/canonical-layer checks invoked in-process, and the binding digest + base recomputed. Writes inside the repo: only this directory (`sev.json`, this report). Probe scripts kept at `/home/z/my-project/scripts/sev096_probe.sh`, `sev096_edge_probe.sh`, `sev096_map_probe.sh`.

## §1 Verdict

**PASS — zero open P0/P1; one P1 and one P2 resolved-by-assembly (mechanically forced, the SEV-095-1 class); one P2 resolved by disclosure. Zero product-code defects.** The extraction/readiness surface is correct and truthful at every layer this round could reach, and the adapter law is kept: the read is ONE statement at ONE snapshot over the generation machine's own vocabulary, the write route adds no retry logic of its own (the kernel's idempotency machine is the single home), and the §11.4 map keeps the internals-leaking refusal classes on the message-replacing 500 default. The round's material finding is **SEV-096-1 (P1, resolved-by-assembly, mechanically forced)**: `claims.check_registry()` REFUSES `ARV-CLM-003` at the reviewed head — CLAIM-096's row mints the already-ledgered INT-163 without the word "retroactive" in the INT cell or Notes, the exact wording the 094 (0c77267), 094B (513c621) and 095 (a81b270) rows each carry for the same-slice mint class. The gate's PR-mode run calls `check_registry()` unconditionally, so the PR cannot pass without the one-wording repair; this report's own digest binding moves with the CLAIMS.md edit, forcing the re-bind. If the evidence commit lands without the repair, the finding reopens and the slice is BLOCKED.

## §2 The live verification (everything below re-executed by this reviewer, exit codes as observed)

### §2.1 The route suite (run-01's claim)

`python3 harness/tests/test_api_routes.py` at `58be295` → **exit 0**, `GREEN — the api routes suite passes`, all 33 route checks (ARV-API-001..033) + ARV-SUITE-001 PASS. The twelve new extraction checks (022..033) cover: never_requested before any extraction (022); the §11.3 Idempotency-Key law through HTTP (023); the honest ack (committed + durability_rung + result_ref, 024); the same-key replay returning the SAME generation (025); ready + the serving generation with passage_count from the CURRENT generation only (026); the new-key rebuild (a new generation, the old superseded, 027); the crashed building row answered `building + retryable` and the SAME key resuming it to current (028/029 — the kernel's own `--crash-at pre-commit` point driven directly); the cross-owner no-leak on both arms (030/031); and the absent source on both arms (032/033).

### §2.2 The truthful-readiness semantics on this reviewer's OWN scratch db

`bash /home/z/my-project/scripts/sev096_probe.sh` → **exit 0** (scratch db created + migrated through the full 0020 chain exactly as the battery does; the kernel's own import_source; then):

- **before any extraction:** `extraction-status` answers `never_requested`, `retryable: false`, `passage_count: 0`, `generation_id: null`, `generation_count: 0` — the honest unavailable, never presented as ready.
- **after extract.py:** `extraction_state: current`, `generation_id` EQUAL to the ack's `result_ref`, `generation_ordinal: 1`, `passage_count: 1`, `readiness: ready`.
- **the cross-owner read:** `--owner other-owner` against the same id → `FAIL ARV-QRY-001` exit 1 — absent and another-owner's are the SAME refusal (the no-leak class), answered by the shared `_refuse(family="source")`.
- **the same idem key** → `status=replayed`, the SAME `result_ref`; **a new key** → a NEW generation at `generation_ordinal: 2`, `generation_count: 2`, readiness still `ready` answering the NEW generation.

### §2.3 The in-flight rebuild edge probe (this reviewer's own, beyond the battery)

`bash /home/z/my-project/scripts/sev096_edge_probe.sh` → a complete extraction (ready/ordinal 1), then a NEW-key extraction crashed `pre-commit` over it: the status answers **`building`, `retryable: true`, with `passage_count: 1` — the STILL-CURRENT old generation's count** (never the half-committed rows, never a false ready), then the same-key resume lands `ready` at ordinal 2. This is the exact mid-rebuild truthfulness the §11.2 'never a partial extraction presented as complete' contract demands, and the battery has no check for it.

### §2.4 The §11.4 map + the content-class kernel refusals

`bash /home/z/my-project/scripts/sev096_map_probe.sh` → **MAP-OK** + both kernel refusals live:

- **in-process, through `_map_kernel_refusal` (all six codes):** ARV-EXT-001 → **422** (message kept — clean prose), ARV-EXT-005 → **422** (message kept), ARV-EXT-004 → **404** (the ARV-QRY-001/003 absence-family tuple), ARV-EXT-002/003/006 → **500 with the message REPLACED** by "the command refused with a named code" (their kernel messages CAN carry observed DB cause text — extract.py's ARV-EXT-003 embeds `observed[:300]` of the DB error — so the map's replacing default is the correct §11.4 behavior).
- **live on a scratch rig:** the empty source → `FAIL ARV-EXT-001` exit 1; the NUL-containing source → `FAIL ARV-EXT-005` exit 1 — both clean prose, no internals, exactly as mapped.

### §2.5 The EXTSTATE_SQL derivation (static review against the schema)

Read in `harness/query.py`: `passage_count` = `count(*) FROM arv.passage p JOIN arv.extraction_generation g ON g.id = p.generation_id WHERE g.source_id = s.id AND g.owner_scope = s.owner_scope AND g.state = 'current'` — **ONLY the CURRENT generation's rows**. The outer query gates existence on `arv.source s WHERE s.id = {id}` (RLS: another owner's source yields NO row → the dispatch's `_refuse(a.id, family="source")`, verified live in §2.2). The id is SQL-escaped by doubling single quotes. The readiness dict `{current: ready, building: building, failed: failed, never_requested: never_requested}` is **total over reachable latest-ordinal states**: migration 0006's CHECK admits a fourth state `superseded`, but extract.py's supersede UPDATE (`WHERE source_id = ... AND state IN ('current','building') AND id <> {gen_id}`) runs in the SAME transaction that flips the NEW MAX+1-ordinal row to current, so the latest-by-ordinal row can never remain `superseded` — the KeyError path is unreachable on any kernel-producible state (verified by reading `_stage_building`/`_complete` plus the live rebuild probes).

### §2.6 The RED form at the test-only commit (LAW-11)

`git worktree add --detach /tmp/sev096_red 2891c50` → the battery run with the repo's pinned venv → **exit 1**: `ARV-SUITE-001` + `ARV-API-022..030` FAIL (the routes and the kernel arm do not exist at that tree); worktree removed after. The red-record chain verified end-to-end: the amendment's `new_sha256` (a8ef5d9e...) equals BOTH the 2891c50 tree's `harness/tests/test_api_routes.py` hash AND the current tree's file hash; `binding_commit` preserved; `red_exit: 1`. The gate's `check_red_records()` → **[]** at HEAD. Honest disclosure (SEV-096-3): ARV-API-031..033 PASS at the red tree — their 404 assertions are reachable pre-slice through the router's absent-route path, so those three checks' red-first form is vacuous by construction; the nine non-vacuous checks (022..030) carry LAW-11's premise.

### §2.7 The gate's checks + the canonical layer (in-process, at HEAD)

- `scope.check_scope(diff, 'claim-096-extraction-readiness')` → **[]** — the 12-path reviewed diff is inside the declared scope.
- `claims.check_branch_claim('slice/claim-096-extraction-readiness', diff)` → **[]** (the gate's own branch form; a bare name without the `slice/` prefix is not the gate's invocation).
- `claims.check_registry()` → **`FAIL ARV-CLM-003`** — the round's P1 (SEV-096-1).
- `gate.check_red_records()` → **[]**; `python3 tools/verify_canonical_layer.py` → **exit 0, 54/0** (run-02 re-executed).
- `python3 harness/sev.py claim-096-extraction-readiness` (this record) → **GREEN, exit 0** — including ARV-SEV-009 (the base `5062510` carries the `sheet_section` renderer in its proofsheet.py — probed by this round — and this report sets `sheet_section: true`).

### §2.8 The binding fields (recomputed exactly as the validator does)

- `merge_base_of('origin/main', HEAD)` → `5062510743a14a463bced0e553e2b7ce3d36817e` — matches `base_sha`.
- `reviewed_diff_sha256('origin/main', 'claim-096-extraction-readiness')` → `dc871bd60406dcc26a959df54167a60be2a3cc62cd3e075146f3f384aad5df9b` — computed by this reviewer through the validator's own public function, over the 12 reviewed paths (the runs dir excluded as the self-referential artifact class).

### §2.9 The bookkeeping coherence

- **CLAIM-095's closed row** vs git ground truth: `5062510` is a merge commit of `a81b270` (the 095 branch head) and `1eab74a1`, dated 2026-11-26 — the row's "PR #137 = merge 50625107, merged 2026-11-26, the five checks green at the PR head a81b270 and on the merge commit, the D-042 review id 6074141065, the branch deleted, 0 open PRs" is consistent with the observed history (the live-API observation is the builder's; this round verified the git-side facts and accepts the API-side facts on record 81's documentation).
- **INT-163** exists in the ledger (one-liner + full entry, `active`, decided 2026-11-26, CLAIM-096); **D-055** in DECISIONS.md (the remote 0020 application — accepted on record 81's documented observation; NOT re-observed by this round, see §4); **STATE** names CLAIM-096 active with Workstream 1 DONE; **record 81** + **Task 118** present and consistent with the diff.

## §3 Findings

| id | severity | status | one-liner |
|---|---|---|---|
| SEV-096-1 | P1 | resolved (resolved-by-assembly, mechanically forced) | `claims.check_registry()` refuses ARV-CLM-003 at HEAD: CLAIM-096's row mints the already-ledgered INT-163 without the retroactive notation (the 094/094B/095 precedent wording); the gate's PR-mode registry check forces the one-wording repair before the PR can pass, and this report's digest binding forces the re-bind. |
| SEV-096-2 | P2 | resolved (resolved-by-assembly) | INTENT-LEDGER.md line 32: the INT-163 one-liner is glued onto INT-125's line (no terminating newline) — two rows in one line, invisible to every current mechanical check (VER-213/sev/canonical all pass); one newline in the same evidence commit. |
| SEV-096-3 | P2 | resolved (by disclosure) | ARV-API-031..033 pass vacuously at the red tree (their 404 assertions are reachable pre-slice through the absent-route path); the red record's red_code note does not name the partial vacuity — disclosed here rather than repaired. |

No P0. Zero product-code defects: the kernel read arm, the two routes, and the §11.4 mappings are correct as reviewed and as probed.

## §4 Not verified (the honest list)

1. The five required CI checks at the PR head and the D-042 reasoned PR review — the PR is not yet opened at this round; never pre-claimed.
2. The Proof Sheet assembly (the sheet + its SEV section) — the builder's own assembly act; this report sets `sheet_section: true` against the base's renderer and the validator's ARV-SEV-009 passes on it.
3. The remote (wcuuakhdmsmmxagvbdmg) state re-observed by this round: D-055's 0020-application facts (ledger 20/20, role defaults, definer pin, RLS 26/26) are accepted on record 81's documented observation + the DECISIONS row; this round did not re-connect to the remote (no credential in this context, by design).
4. A live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice).
5. The remote's btree/TOAST parity for the 095 bound (carried from record 80 §9).
6. ARV-EXT-002 (invalid UTF-8) and ARV-EXT-003 (mid-build failure) verified at the §11.4 MAP level only (in-process class assertion: 500, message replaced); their kernel-side live refusals not re-executed by this round (pre-existing, 096-untouched kernel paths covered by the standing EXT suite).
7. The battery's run under the CI host's own venv-less provisioning (the 093/094B honest-degradation form): this round ran it with the repo's pinned venv (`.venv-waved`) per run-01's recorded command.
8. run-01/run-02's recorded `output_sha256` digests not re-derived from saved transcripts (outputs not preserved in the run dir); the underlying commands were re-executed live and matched the recorded exit codes.

## §5 The re-bind obligation (stated for the builder)

The SEV-096-1/SEV-096-2 repairs edit CLAIMS.md and INTENT-LEDGER.md — both are REVIEWED PATHS in this report's digest. When the evidence commit lands them, `reviewed_diff_sha256` MUST be recomputed (the validator's own `harness.sev.reviewed_diff_sha256('origin/main', 'claim-096-extraction-readiness')`) and this record re-bound, exactly as the 094B slice did at 513c621 (the commit that closed the same ARV-CLM-003/ARV-SEV-003 cycle). The proof sheet then assembles over the re-bound record with the SEV section (`sheet_section` already true).
