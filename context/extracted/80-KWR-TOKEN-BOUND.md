# 80 — THE F6 TOKEN-BOUND SLICE + THE DIRECTIVE INTAKE
> STATUS: SESSION ENGINEERING RECORD (2026-11-26; INT-162; D-054). Historical
> process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 117.
> PRs this session: (the slice's PR — number recorded in §12 at close).

## 1. What the owner asked (verbatim — owner turn 46, 2026-11-26)
> Read the complete attached ARIVOO_END_TO_END_BACKEND_EXECUTION_DIRECTIVE.md and execute it against the live prathamarchives/Arivoo repository.
>
> This supersedes earlier assistant-generated continuation prompts and hosting assumptions.
>
> Do not return another plan. Reconcile the current merged state, close the outstanding bookkeeping, and start the next implementation workstream.
>
> Batch implementation and verification intelligently. Do not waste time running the complete suite after every small edit. Preserve mandatory PR reviews, slice-level SEV and required CI.
>
> Continue sequentially through the entire backend end state: REST API, remote MCP, Supabase, storage, workers, synchronization, Cloudflare domain, HTTPS, deployment and operational acceptance.
>
> Do not use Railway by default. Do not integrate Graphiti or Kev.
>
> A blocked owner decision blocks only its specific dependency. Continue all other authorized work.
>
> The deliverable is a deployed, secure, fully integrated Arivo backend ready for independent frontend development, not another architecture proposal.

The attached directive document (509 lines) is preserved verbatim at
`context/raw/ARIVOO_END_TO_END_BACKEND_EXECUTION_DIRECTIVE.md` (the §9 register's fourth
growth, SHA-256 `73d9be1dba80e177efe0679091d72bc073c5ed76c3719daab41fe13892ffb8ab`) —
the turn's trailing file-name/storage-location lines are host transport metadata, never
owner words. No access credential traveled with this turn (none needed: the session's
stored credentials were re-verified live — see §2).

## 2. Starting state
- Fresh sandbox (the recycled environment): the secrets store, the rig, and the venv did
  NOT survive the recycle; both tokens re-entered from the session's persistent memory,
  stored at `/home/z/my-project/.secrets/` (gitignored at the workspace root; never in any
  repo file — D-025) + the git credential store for `github.com`.
- Live GitHub observed through the API (2026-11-26): main at `1eab74a132c36c5d2d32fce74030ecb90ae6e571`
  (PR #136's merge, matching the directive's stated continuation point exactly); PR #136
  closed/merged, merge_commit_sha `1eab74a1...`, merged 2026-11-25T09:32:32Z; the merge
  commit's five required check-runs ALL success (canonical-layer 139108968293, head-tools
  139108968582, harness-suites 139108968782, harness-trusted 139108968804, harness
  139108928928 → 139108968928); 0 open PRs; the 094B branch deleted (the remote's stale
  pre-094 branches unchanged — parked/claim-082, 084, 087, 087b, 088, 089, 090, 091, 092,
  093, 093b — a pre-existing condition outside this slice's scope).
- The drift the directive names, CONFIRMED: `CLAIMS.md` still carries CLAIM-094B as the
  only OPEN row and `STATE.md` still names 094B's PR as the exact next action — stale
  post-merge bookkeeping (the rule-4 session-boundary class).
- Maxima verified before reserving IDs: INTENT max INT-161, CLAIMS max CLAIM-094B,
  DECISIONS max D-053, WORKLOG max Task 116, record max 79.
- Environment rebuilt from the workspace's persisted scripts (the §3 reconstruction below).
- Preflight runs before any edit: the rig migration chain `python3 harness/migrate.py`
  (PGDATABASE=arv_harness) → exit 0, `applied 0020_search_path_pins`, `verify OK: 20
  migration(s) applied, checksums match`; the standing routes battery
  `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` → exit 0, GREEN (26/26).

## 3. Task and scope
- **The directive's Workstream 0 + Workstream 2 in one bounded claim (CLAIM-095)**: the
  post-merge bookkeeping close (094B's closed row + the STATE re-derivation + the
  directive intake — INT-162/D-054/the raw growth/the manifest rows) rides the first
  bounded implementation claim, exactly the ride-with-next-bounded-claim order the
  directive's §2.2 item 6 permits; the implementation is the routed F6 kernel defect
  (record 79 §6: "F6's exact minimum trigger size").
- Intent refs: INT-162 (the directive). Decision refs: D-054 (the directive adoption),
  D-053 (the adapter law this slice keeps — the kernel owns the bound, the route adapter
  inherits it), D-041/D-047 (the standing execution order).
- Non-scope: the extraction/readiness routes (CLAIM-096, the next §11.2 slice); the 0020
  remote application (its own act after this slice); Q18/Q12-Q17/Q7 gates untouched.

## 4. Results
- **The F6 spike (the honest defect definition, LAW-02's spike-not-memory path):** the
  naive reading — "a long unbroken token exceeds the btree row limit" — is INCOMPLETE.
  Observed live on the 17.12 rig: `repeat('a', 3000)` and even 4000/8000-byte repeated
  runs INSERT CLEANLY into a btree index, because PostgreSQL TOAST-compresses the datum
  BEFORE the index tuple is built (repeated characters compress to near-nothing); the
  "index row size 3016 exceeds btree version 4 maximum 2704" error fires only when the
  COMPRESSED size exceeds BTMaxItemSize (~2704 for 8k blocks; the limit verified against
  the REL_17_STABLE source — `_bt_findinsertloc` → `_bt_check_third_page`). An
  incompressible 3000-char mixed-case run reproduces the crash exactly. Consequence: the
  kernel cannot predict the server's compression outcome, so the bound must sit on the
  RAW UTF-8 byte length with margin — 512 bytes (≈5× under the effective floor).
- **The fix (the bounded tokenizer/index-input contract):** `KWR_TOKEN_MAX_BYTES = 512`
  at ONE home (`harness/commands.py`, the tokenizer's home); `_kwr_tokens` raises the
  typed `ARV-KWR-002` refusal on an over-bound run (every capture path — notes,
  revisions, the rebuild — guarded at build time through the spine's zero-partial-effect
  contract); `import_source` carries a pre-scan after the format decode (the staged-bytes
  pattern: the journal row records `failed(ARV-KWR-002)` retryable, bytes stay staged and
  recoverable, the metadata transaction is never entered with an over-bound token); the
  read side (`harness/query.py`) imports the kernel constant (never re-declares) and
  refuses over-bound terms with `ARV-KWR-003` on both the search and pack arms (a term
  the index can never hold is a named refusal, never a silent empty result — KWR-07's
  explicit-failure law applied to the read side).
- **What did not change:** the tokenizer's token semantics (case-folded Unicode word
  runs + CJK single chars and whole runs), the word-boundary law, the rebuild/idempotency
  contracts, the standing suites' behaviors (all affected families re-run GREEN), the
  route adapter (the kernel owns the bound; the adapter inherits it — no duplicated logic).
- **The bookkeeping:** CLAIM-094B closed (rule 4: the closed row appended from the live
  merge facts; the open row removed), STATE re-derived (§ below), INT-162 minted, D-054
  adopted, the directive preserved verbatim as the raw corpus's fourth §9-register growth
  (manifest rows + README count), Task 117, this record.
- **The environment reconstruction (sandbox recycle):** the rig (PostgreSQL 17.12, the
  Debian trixie package set `postgresql-17/client-17/libpq5 17.12-0+deb13u1`, extracted
  without root at `/home/z/my-project/pgbuild/`, port 5433, fresh initdb) + the venv
  (`.venv-waved`, the 21 pinned wheels from `harness/api/requirements.lock`, installed
  `--require-hashes --no-deps`) rebuilt through the persisted
  `/home/z/my-project/scripts/rebuild-env.sh` (idempotent, re-runnable at every recycle).

## 5. Files changed
- `harness/commands.py` — the bound constant + the tokenizer refusal + the import
  pre-scan (KWR_TOKEN_MAX_BYTES, ARV-KWR-002).
- `harness/query.py` — the read-side term bound (ARV-KWR-003, the imported constant).
- `harness/tests/test_kwr_bound.py` — the KBND-01..07 suite (RED-first; the red record
  bound at the test-only commit).
- `harness/red-records.json` — the new red record (schema 2, binding 385ad7b).
- `harness/runs/claim-095-kwr-token-bound/` — scope.txt, run-01..run-04, proofsheet.md,
  notverified.txt, sev.json (+ the SEV round reports).
- `CLAIMS.md` / `STATE.md` / `INTENT-LEDGER.md` / `DECISIONS.md` / `AGENTS.md` /
  `context/WORKLOG.md` / `context/README.md` / `context/SOURCE-COVERAGE-MANIFEST.md` —
  the bookkeeping (095's row, 094B's close, INT-162, D-054, count 143→144, Task 117,
  the corpus count, the growth rows).
- `context/raw/ARIVOO_END_TO_END_BACKEND_EXECUTION_DIRECTIVE.md` — the verbatim owner
  document (the fourth §9-register growth).
- `context/extracted/80-KWR-TOKEN-BOUND.md` — this record.

## 6. Commands and external actions (ACTUAL — never reconstructed)
- Live state: `GET /repos/prathamarchives/Arivoo/pulls/136` → closed/merged, merge
  `1eab74a1...`, merged_at 2026-11-25T09:32:32Z; `GET .../commits/1eab74a.../check-runs`
  → 5/5 success (IDs in §2); `GET .../pulls?state=open` → 0; `GET .../branches` → the
  094B branch absent.
- The F6 spike (the defect's honest reproduction, all on the 17.12 rig):
  - `INSERT INTO bt_probe VALUES (1, repeat('a', 3000))` after a page-filling 400-row
    load → NO error (repeated characters TOAST-compress; the naive probe's finding).
  - `INSERT INTO bt_probe VALUES (1, '<incompressible 3000-char mixed run>')` →
    `ERROR: index row size 3016 exceeds btree version 4 maximum 2704 for index
    "bt_probe_tok"` (the F6 class, reproduced).
  - The pre-fix kernel reachability: `commands.py import_source` with a 560-byte
    repeated token → ACK committed (compresses; under the row limit); with the
    incompressible 4000-char run → the DB-side crash class inside the metadata
    transaction (the suite's red evidence).
  - Source verification: REL_17_STABLE `nbtinsert.c` (`_bt_findinsertloc` → the 1/3-page
    check) + `nbtree.h` (the BTMaxItemSize macro) + `nbtutils.c`
    (`_bt_check_third_page`).
- The red run (LAW-11): `python3 harness/tests/test_kwr_bound.py` at the test-only
  commit `385ad7b` → exit 1, 7/7 KBND checks FAIL; recorded via `python3 harness/red.py
  --note ... --exit 1 --code "ARV-TEST-KBND (KBND-01..07...)" --red-commit 385ad7bb...`
  → OK ARV-RED-005.
- The green run: `python3 harness/tests/test_kwr_bound.py` at the implementation head →
  exit 0, GREEN (KBND-01..07).
- The affected standing suites (the batched cadence — INT-162/D-054's §3.3, one pass per
  coherent slice, not per edit): test_keyword_index, test_import, test_note,
  test_journal, test_highlight, test_bookmark, test_retrieval_packs, test_commands →
  all exit 0 GREEN at the implementation head (the exact per-suite GREEN lines in
  run-02.txt).
- The gate (PR mode, the slice's own record): `python3 harness/gate.py --slice
  claim-095-kwr-token-bound --diff origin/main --skip-suites` → GREEN (run-04).
- The canonical layer: `python3 tools/verify_canonical_layer.py` → green at the final
  head (run-04's tail; the count line quoted there).

## 7. Evidence
- `harness/runs/claim-095-kwr-token-bound/` — run-01 (the red run at 385ad7b), run-02
  (the green + the affected-suite batch), run-03 (the F6 spike probes), run-04 (the gate
  + the canonical layer), proofsheet.md, notverified.txt, sev.json (the two-round chain).
- The live GitHub facts (§2) observed through the API this session.
- The red record in `harness/red-records.json` (binding 385ad7b, schema 2).
- CI: the PR's five required checks at the exact PR head (IDs recorded in §12 at close).

## 8. Failures
- The suite's first KBND-05 form asserted absolute index-row counts that forgot the note
  rows created by KBND-03/04 — the check failed against the WORKING fix (a test bug, not
  a code bug); repaired to the global bound assertion (`octet_length(token) > 512` count
  == 0) + the exact 3-token source set.
- The first KBND-05 trigger used a REPEATED-character run — the spike then proved such
  runs TOAST-compress and never crash (the case would have pinned a non-defect); replaced
  with the deterministic incompressible generator (`_incompressible`, an LCG — no ambient
  randomness, LAW-24).
- The venv rebuild's first form passed the prose-carrying lock to pip directly → pip
  refusal; repaired to the pin-line extraction + the `--hash` conversion (the method
  record 79 §3 describes; now persisted in rebuild-env.sh for future recycles).
- No product-code defect found in the fix itself across the affected-suite batch.

## 9. Unverified items
- The bound value's interplay with a SUPABASE-side btree (the remote's block size and
  TOAST settings are Supabase-managed; the local 17.12 rig is engine-parity, not
  config-parity — the 512-byte raw bound sits far enough under any 8k-block ceiling
  that the margin covers it, but the remote observation rides the 0020 application
  session's verification pass).
- The remote migration ledger re-read (0020 still unapplied remotely as of the
  directive's own §2.3 check — the remote application is the next workstream's own act).
- A live Supabase-issued token end-to-end (carried: needs a real user; §17.1's class).
- uvicorn over a real socket; the route surface against the remote db (the deployment
  slice's own acts).
- The btree-limit source reading was verified against REL_17_STABLE (the stable branch),
  not the exact Debian patch level's source tree (17.12-0+deb13u1) — the Debian delta is
  packaging, but this is stated rather than assumed.

## 10. Open decisions
- Q18 (the compute platform) — OPEN; blocks only the deployment choice (Workstream 10).
  The directive records the hostname + Cloudflare direction; no Railway default.
- Q12/Q17 (the storage provider + cross-store recovery) — OPEN; blocks only the
  provider-specific implementation (Workstream 8's gate).
- Q7 (the semantic budget/model) — OPEN; blocks paid model work only.
- Q6, Q8, Q9, Q10, Q11, Q16, Q19, D-014 — unchanged (STATE's register).
- The 0020 remote application — the next workstream (its own act, the guarded path).

## 11. Next action
Workstream 1 (the directive's order): apply migration 0020 to
`wcuuakhdmsmmxagvbdmg` through the guarded canonical remote act (verify the live ledger
is still 1–19 first, verify-full, the migration credential from the release env), then
independently verify the row/checksum/role defaults/RLS/grants. Then CLAIM-096 (the
§11.2 extraction/readiness routes), maxima checked first.

## 12. Session close
- (filled at the slice's merge: the merge SHA, the PR-head five-check run, the
  post-merge close, STATE's re-derivation commit)
