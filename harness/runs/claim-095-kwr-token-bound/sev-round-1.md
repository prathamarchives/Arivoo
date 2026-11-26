# CLAIM-095 — SEV round 1 (the fresh-context systems-engineering verification)

- **Agent:** independent fresh-context SEV reviewer (reviewer-zsubagent-fresh-context-claim-095; not the slice author; no prior involvement in building this slice)
- **Date:** 2026-11-26
- **Round:** 1
- **Base:** `1eab74a132c36c5d2d32fce74030ecb90ae6e571` (origin/main, PR #136's merge — the merge-base observed by `harness.sev.merge_base_of`)
- **Head:** `e870ad2` (git ground truth at review time)
- **Chain (base → head):** `1eab74a1` → `385ad7b` (the RED: tests-only, `harness/tests/test_kwr_bound.py` 326 lines + the CLAIM-095 row + scope.txt + the 094B closed row riding per rule 4) → `b6e5e15` (the GREEN: commands.py +58 / query.py +38 / a 12-line test amendment — record 80 §8's two disclosed test-bug repairs) → `e870ad2` (the bookkeeping: INT-162 + D-054 + the directive raw intake + the manifest/README growth + STATE re-derivation + record 80 + Task 117 + the gate.py TESTS registration + the run records + f6-spike.sh)
- **Method:** every central claim re-executed live by this reviewer on the local PostgreSQL 17.12 rig (`source /home/z/my-project/pgbuild/env.sh`, PGPORT 5433): the KBND suite, the F6 spike script, the RED form at the test-only commit (a detached git worktree, removed afterwards), the two most-affected standing suites, the canonical layer, the gate's red-records / scope / size / claims checks invoked in-process, plus three self-devised probes (the constant import, the F6 crash class reproduced directly on the real `arv.keyword_index` table through the kernel's own role and owner setting, and the binding digest/base recomputation). Writes inside the repo: only this directory (`sev.json`, this report). Probe script kept at `/home/z/my-project/scripts/sev95_probe.py`.

## §1 Verdict

**PASS — zero open P0/P1; one open P2 (documentation debt, repaired at the assembly).** The F6 kernel fix is correct, independently reproduced end to end, and consistent with the repo's laws: the bound lives at ONE kernel home, the import refusal keeps the crash class out of the metadata transaction with the staged-bytes contract intact, the read side refuses named, the idempotency semantics survive the refusal, and the route adapter stays free of duplicated kernel logic. The round's material finding is **SEV-095-1 (P1, resolved-by-assembly, mechanically forced)**: the LAW-11 red record for the new suite is **absent** from `harness/red-records.json` at the reviewed head — the gate refuses `ARV-RED-001` live (I reproduced it), and the session record's claim that the record exists is an overclaim. The repair is mechanical and lands with the evidence commit that carries this report; two controls (the gate refusal and this report's own digest binding) refuse any other outcome. If the assembly lands without the mint, the finding reopens and the slice is BLOCKED.

## §2 The live verification (everything below re-executed by this reviewer, exit codes as observed)

### §2.1 The KBND suite (run-01's claim)

`python3 harness/tests/test_kwr_bound.py` at `e870ad2` → **exit 0**, `GREEN — the F6 token-bound suite (KBND-01..07) passes`, all seven checks PASS:
- **KBND-01** the import refusal: `FAIL ARV-KWR-002` exit 1, the journal row `failed|ARV-KWR-002`, ZERO source/work/command_log/keyword_index rows.
- **KBND-02** the bound edge: a 512-byte token imports green and is whole-token searchable; 513 bytes refuses — the boundary is exact in UTF-8 bytes.
- **KBND-03** the note path + idempotency: refusal with zero rows; the SAME idem key retried with clean content ACKs `created`.
- **KBND-04** the Unicode boundary: normal CJK imports and searches by single character; the 171-char unbroken CJK run (513 bytes) refuses; accented/combining text unchanged.
- **KBND-05** the adversarial class: the INCOMPRESSIBLE 4000-char run refuses `ARV-KWR-002`, never `ARV-CMD-010`, never a DB-side crash; no token over the bound exists anywhere in the index.
- **KBND-06** the query arm parity: over-bound search and pack terms refuse `ARV-KWR-003`; normal terms return the standing corpus.
- **KBND-07** the ONE home: the constant declared in commands.py, imported (never re-declared) by query.py.

### §2.2 The F6 spike reproduction (run-03's claim)

`bash harness/runs/claim-095-kwr-token-bound/f6-spike.sh` → **exit 0**, three probes:
- probe 1: a repeated-character 4000-char run **inserts cleanly** (TOAST-compressed before the index tuple is built).
- probe 2: the incompressible 3000-char mixed run raises `ERROR: index row size 3016 exceeds btree version 4 maximum 2704 for index "bt_probe_tok"`.
- probe 3: the same class through `import_source` refuses with the named `FAIL ARV-KWR-002`.

### §2.3 The RED form at the test-only commit (LAW-11)

`git worktree add --detach … 385ad7b` → `python3 harness/tests/test_kwr_bound.py` → **exit 1**, `RED — 7 check(s) failing: KBND-01, KBND-02, KBND-03, KBND-04, KBND-05, KBND-06, KBND-07` (worktree removed after; the main tree never touched). Structural corroboration: `git show 385ad7b:harness/commands.py | grep -c ARV-KWR-002` → 0 and the same for `ARV-KWR-003` in query.py — the named codes the suite asserts on did not exist pre-slice, so the RED form is guaranteed, and I observed it.

### §2.4 The F6 crash class on the REAL table (this reviewer's own probe)

`python3 /home/z/my-project/scripts/sev95_probe.py` → **exit 0** (scratch db, the full 0020 migration chain, role `arv_app` + `app.current_owner='A'` exactly as the kernel's `Session`):
- **probe A:** INSERT of the incompressible 3000-char token into `arv.keyword_index` → `ERROR: index row size 3048 exceeds btree version 4 maximum 2704 for index "keyword_index_pkey"` — the pre-fix kernel path (the fix only refuses before the INSERT; the INSERT itself is unchanged) crashes on the production table, not just on a bare probe table.
- **probe B:** the 512-byte accepted-bound token inserts cleanly.
- **probe C:** the 512-byte row answers whole-token search — the bound's margin is safe.

### §2.5 The affected standing suites (run-02's claim, the two most-affected re-run)

- `python3 harness/tests/test_keyword_index.py` → **exit 0** (`GREEN — the P3-07 acceptance suite (KWR-01..10) passes`).
- `python3 harness/tests/test_import.py` → **exit 0** (`GREEN — the §3.1 import state machine + the recovery walk + the SEV-7 death classifier hold end-to-end (IMP-01..22)`).
- The remaining six suites of run-02's batch accepted on the recorded green (see §5).

### §2.6 The gate's checks + the canonical layer (in-process, at HEAD)

- `check_red_records()` → **`FAIL ARV-RED-001: no red record for harness/tests/test_kwr_bound.py`** (fails == `['ARV-RED-001']`) — the round's P1 finding (SEV-095-1).
- `scope.check_scope(diff, 'claim-095-kwr-token-bound')` → [] · `scope.check_size(stats)` → [] · `claims.check_registry()` → [] · `claims.check_branch_claim(...)` → [] — the 20-path diff is inside CLAIM-095's declared scope, LAW-05's size limits hold, the registry is coherent, and the open row covers the diff.
- `python3 tools/verify_canonical_layer.py` → **exit 0** (the ledger count 144, STATE's re-derivation, the manifest's fourth growth row, the README's eleven-file count, the 094B closed row — cross-document coherent).
- `python3 harness/sev.py claim-095-kwr-token-bound` (this record) → **GREEN, exit 0**.

### §2.7 The binding fields (recomputed exactly as the validator does)

- `merge_base_of('origin/main', …)` → `1eab74a132c36c5d2d32fce74030ecb90ae6e571` (base_sha).
- `reviewed_diff_sha256('origin/main', 'claim-095-kwr-token-bound')` → `69b3d6464badb2ea937bd443bc95856eef25f3d70188f36f3b7cad3d3c51c1f9` over the 14 reviewed paths (the runs dir excluded).
- `_base_renders_sections('origin/main', …)` → **True** — the base carries the Proof-Sheet SEV section renderer, so this record sets `sheet_section: true` (the CLAIM-044 expectation; no ARV-SEV-009 fires).

## §3 The static/git verification

1. **The diff read in full** (base→head): commands.py +58 (the constant, the tokenizer refusal, the import pre-scan), query.py +38 (the read-side bound on search + pack), gate.py +5 (the TESTS registration), the 328-line suite, and the bookkeeping files skimmed for coherence.
2. **The pre-scan placement verified in the code:** it runs AFTER the blob put+verify and the format decode, and BEFORE the `staging_verified` journal update and the metadata transaction (`build_with_index`); its non-text boundary (`UnicodeDecodeError, KeyError, _FmtRefusal` → empty string) byte-mirrors `build_with_index`'s own boundary — a non-decodable source is not indexed, never refused there.
3. **The one-home law:** `KWR_TOKEN_MAX_BYTES = 512` declared once in commands.py beside the tokenizer; `query.py` imports it (`from harness.commands import API_VERSION, KWR_TOKEN_MAX_BYTES`); no second bound constant in the read kernel.
4. **The directive intake:** `sha256sum` of `context/raw/ARIVOO_END_TO_END_BACKEND_EXECUTION_DIRECTIVE.md` → `73d9be1dba80e177efe0679091d72bc073c5ed76c3719daab41fe13892ffb8ab`, matching the manifest's full-digest row (§9 register's fourth growth), the README's eleven-file count, record 80's quote, INT-162's ledger entry, and D-054's adopted row.
5. **The run records:** run-01..04 all parse, carry the typed A09 fields, and bind to `b6e5e15` (a commit git shows); run-04 honestly records the gate's exit 1 at assembly time.
6. **The red-records state:** `harness/red-records.json` has 45 keys — `harness/tests/test_kwr_bound.py` is NOT among them; `git diff origin/main...HEAD -- harness/red-records.json` is empty (no commit in this slice touched it), while scope.txt, record 80 (§5/§6/§7) and WORKLOG Task 117 all declare or cite the record as landed — the SEV-095-1 evidence.
7. **The 094B close:** CLAIMS.md's closed row quotes the live merge facts (PR #136 = `1eab74a1`, the five merge-commit check-run IDs, the branch deletion, 0 open PRs) observed by the builder through the API; this round corroborates the merge SHA as the actual merge-base of origin/main and the registry checks green at HEAD.
8. **The runbook/directive contract fit:** §11.2's Retrieval row (keyword search, bounded context packs) and §11.3's write rules (kernel called, idempotency key, stable error codes mapped) are served by the kernel's named refusal codes; the directive's Workstream 2 letter (bounded contract; tests for normal tokens, very long unbroken runs, Unicode, adversarial size, named refusal, zero partial effect; query/idempotency semantics preserved; adapter clean) is satisfied item by item.

## §4 Findings

- **SEV-095-1 — P1 — RESOLVED (resolved-by-assembly, mechanically forced; the 094B round-1 precedent for completion-stage P1s).** *The LAW-11 red record for the new suite is absent.* `harness/red-records.json` carries no entry for `harness/tests/test_kwr_bound.py`; the gate's `check_red_records()` refuses `ARV-RED-001` live at HEAD. Record 80 §5/§7 ("the new red record (schema 2, binding 385ad7b)") and WORKLOG Task 117 ("the red record bound") overclaim — the 094B SEV-2 class (citing an artifact before it exists). Likely root cause: the mint was invoked before the suite's registration in gate.py's TESTS (red.py iterates TESTS only; an unregistered suite is a silent no-op behind `OK ARV-RED-005: red records updated for 45 test files`). **Disposition:** the evidence commit that lands this report must also mint the schema-2 record via `harness/red.py` at HEAD (`--red-commit 385ad7b`, `--exit 1`, the KBND codes — the red form re-observed live by this round; the binding verifies in git). Two controls refuse any other outcome: the gate's `ARV-RED-001` at PR time, and this report's digest binding — the mint edits `harness/red-records.json`, a reviewed path, so it cannot land silently after this review without staling this record (ARV-SEV-003 forces the re-bind at the true head, the 094B `513c621` pattern). **If the assembly lands without the mint, this finding is OPEN and the slice is BLOCKED.**
- **SEV-095-2 — P2 — OPEN (documentation debt, repaired at the assembly; no product-code effect).** *Record 80's evidence lines overclaim against the actual artifacts.* §6 claims the gate "→ GREEN (run-04)" while run-04.json records exit_code 1 (the honest RED-at-assembly-time record at b6e5e15); §7 labels run-01 "the red run at 385ad7b" while run-01.json is the GREEN run at b6e5e15 (exit 0) and no run record exists for the red run itself; WORKLOG Task 117's evidence line cites "proofsheet + notverified + sev.json" in the landed tense, none of which exist at the reviewed head. **Disposition:** record 80's close addendum (append-only) corrects the gate line (run-04 = RED at assembly time; the green gate is the final-head run-05) and the run-01 label (the green run; the red run's evidence home is the red-records entry per SEV-095-1's repair).
- **SEV-095-3 — P2 — RESOLVED (reasoned no-fix, declared).** *The nominal claim-numbering drift.* The directive §2.2 names "CLAIM-095 (extraction/readiness routes)" as the canonical next action; the registry's CLAIM-095 is the F6 kernel slice (the routes become CLAIM-096). The directive's own Workstream 2 orders the F6 defect into a "separately scoped follow-up claim" (which this slice is — the first bounded claim after the intake); the ordered work is unchanged (W0 rode this slice; W3 routes next per record 80 §11 and STATE); CLAIMS.md is the claim-ID authority (LAW-31) and the mapping is declared in the CLAIM-095 row and record 80 §3.

No P0. No open P1. No constraint weakened, no owner question resolved, no protected path touched by this round.

## §5 Honest limits (the not-verified list)

- The exact pre-fix classification of the incompressible import inside `import_source` at the red tree (the ARV-CMD-010 journal row): I re-observed the 7/7 KBND red at 385ad7b and reproduced the DB-side crash class directly on `arv.keyword_index` (3048 > 2704 on `keyword_index_pkey`), but did not re-read the red run's journal row.
- The remaining six suites of run-02's batch (test_note, test_journal, test_highlight, test_bookmark, test_retrieval_packs, test_commands) — accepted on run-02's recorded green after re-running the two most-affected suites myself.
- The full gate run at HEAD (known-bad matrix, proof-sheet step): not re-run; I invoked the gate's red-records, scope/size, and claims checks in-process, plus the canonical-layer verifier. Run-04 carries the b6e5e15 form; the sheet is not yet assembled at this stage.
- The five required CI checks at the PR head and the D-042 reasoned PR review — the PR is not yet opened at this round; never pre-claimed.
- The Supabase-side btree/TOAST configuration parity for the bound's margin (provider-managed; carried to the 0020 application session's verification pass per record 80 §9), and the carried items from record 80 §9: the 0020 remote application, a live Supabase-issued token, uvicorn over a real socket, the route surface against the remote database, and the REL_17_STABLE-vs-Debian-patch-level source reading.
- run-01..04's recorded `output_sha256` digests were not re-derived from saved transcripts (the outputs were not preserved in the run dir); I re-executed the underlying commands live and matched their recorded exit codes instead.
- The KBND suite's 12-line amendment between `385ad7b` and `b6e5e15` (record 80 §8's two disclosed test-bug repairs) — the red form was re-observed at the red commit itself; the amendment chain rides the red-record mint's `current_sha256` (absent at the reviewed head, per SEV-095-1).
- **Instruction-vs-reality notes, stated honestly:** (a) the task brief asserted "a red record in harness/red-records.json (bound at the test-only commit 385ad7b)" — verified FALSE at the reviewed head (SEV-095-1); (b) the brief's validator invocation `python3 harness/sev.py --slice <name>` does not match the CLI (positional args: `python3 harness/sev.py claim-095-kwr-token-bound`); (c) the brief anticipated a possible ARV-SEV-009 sheet-section failure at this stage — not applicable here: the base carries the renderer, so this record sets `sheet_section: true` and no 009 fires; the record validates GREEN as written.
- **The identity limit (ARV-SEV-007's own statement):** this is a declared distinct fresh-context reviewer, not cryptographic independence — the protocol's stated limit; fresh-context execution and the separate grader remain the protocol.

## §6 Disposition

**PASS.** The SEV record (`sev.json`, this directory) validates GREEN under `python3 harness/sev.py claim-095-kwr-token-bound` (exit 0). The PASS is conditional exactly as stated in SEV-095-1: the evidence commit must carry the red-record mint (the gate and the digest binding enforce it); without it the finding reopens and the slice is BLOCKED.
