# SEV REVIEW REPORT — slice `claim-079-p4f-recovery-contract-gate` (CLAIM-079, P4-F)

- Reviewer: independent SEV grader (fresh context; did NOT build this slice)
- Date: 2026-11-13
- Repo: `/home/z/my-project/Arivoo`, branch `slice/claim-079-p4f-recovery-contract-gate`
- Diff under review: `git diff origin/main...HEAD` (base = merge-base `d21ca44e`)
- HEAD at review time: `f901c7f` (working tree clean except two untracked run-dir drafts: `harness/runs/claim-079-p4f-recovery-contract-gate/notverified.txt`, `proofsheet.md`)

---

## VERIFIED

Everything below was observed live against the real repo (commands + exact outcomes). No repo file was modified by this review; probe scripts live outside the repo at `/home/z/my-project/scripts/` (`sev_journal_ref_probe.py`, `sev_position_probe.py`, `sev_purge_cascade_probe.py`, `sev_ast_compare.py`).

### 1. The diff was read in full

- `git -C /home/z/my-project/Arivoo diff origin/main...HEAD -- harness/client.py harness/export.py harness/gate.py harness/red-records.json harness/tests/test_export.py` — read completely (client.py +360 lines: six P4-F condition functions + two helpers; export.py +51: five new TABLES rows + `_ENTITY` widening + the reconciliation cascade; gate.py +3: the TESTS registration; red-records.json: one new binding + two amendment entries; test_export.py +17: TABLES/TSV widening + EXP-01 prose).
- `harness/tests/test_recovery_contract.py` read in full at HEAD (311 lines) and at the RED commit via `git show 4eb4944:...`.

### 2. LAW-11 RED chain — VERIFIED, ordering is real

Commit order on the branch (`git log --format='%H %ci %s' d21ca44e..HEAD`):

| commit | time (UTC) | content |
|---|---|---|
| `4eb4944` | 2026-11-12 15:34:39 | RED: tests-only — exactly one file, `harness/tests/test_recovery_contract.py` (+310) |
| `6a04f8c` | 2026-11-12 15:35:34 | binding: red-records.json entry + gate.py TESTS registration + run dir (red-01.txt, scope.txt) |
| `09d60b0` | 2026-11-13 06:27:22 | GREEN: client.py implementation + export.py widening + the two suite amendments |
| `89a5ba6` / `ec2a790` / `5be2e8c` / `f901c7f` | 2026-11-13 06:47–09:16 | red-record amendments / measured runs / ARV-SIZE-002 compaction / CLAIMS scope widen |

- `git show 4eb4944:harness/client.py | grep -n "def condition_"` → only the seven P4-B conditions (`condition_forbidden_source` … `condition_deleted_target`, lines 154–282); none of the six P4-F conditions exist. Same at the base `d21ca44e`.
- **RED reproduced live**: `git archive 4eb4944 | tar -x -C /tmp/sev-red` then `cd /tmp/sev-red && timeout 120 python3 harness/tests/test_recovery_contract.py` →
  `FAIL ARV-TEST-000: the P4-F recovery-contract machinery is absent ...` / **exit 1** — matching `harness/runs/claim-079-p4f-recovery-contract-gate/red-01.txt` byte-for-byte in substance. The probe is genuinely DB-free (the nonexistent probe DB is never reached; the import + `getattr` check fails first).
- Digest chain verified by recomputation:
  - `git show 4eb4944:harness/tests/test_recovery_contract.py | sha256sum` = `ea570a0e497f79916237165100b0548d0d80d0472dd8ed4f5b46017fc55c942d` = the record's `binding_sha256`.
  - `sha256sum harness/tests/test_recovery_contract.py` (HEAD) = `a5e64d5bc850d48fd4e8564c0a6008eed7024ae9074df0635c0e728b92b29076` = the record's `current_sha256`.
  - `sha256sum harness/tests/test_export.py` (HEAD) = `6384e4b1a1d4510ca2c601b19d36508b5721c7434885d09c2d3bad38ce9d16d8` = the export record's `current_sha256`.
- The suite's only change from RED form to HEAD is **one line** (`git diff 4eb4944 HEAD -- harness/tests/test_recovery_contract.py`): RCW-05 `cond["migrate_exit"] == 0` → `cond["migrate_exit"] is True`. The condition returns `"migrate_exit": all(r.returncode == 0 for r in (r_m1, r_m2))` (harness/client.py:600) — a **boolean**. The RED form `True == 0` would always fail; the amendment is the honest pin-type repair matching the returned dict, and it is **not a weakening**: the pin still requires BOTH migration invocations to exit 0 (the boolean is exactly that conjunction). The amendment is disclosed in both red-record entries with the prior→new digests, and the RED evidence (red-01.txt, machinery-absent class) is untouched — the RED never depended on the RCW-05 pin.
- `make verify` at 09d60b0 was recorded as **exit 2** (run-04.json) — the gate's own ARV-RED-006 refusal on the then-un-amended `test_export.py` change, closed by the typed amendment commit `89a5ba6` (run-05 verify exit 0). The intermediate refusal is kept, not hidden. The gate machinery forced the disclosure — process working as designed.
- `harness/gate.py` TESTS registration for the RCW suite rides the binding commit `6a04f8c` (diff-visible, the ARV-RED-008 convention) — verified in the gate.py diff hunk.

### 3. Live suite runs at HEAD (`f901c7f`)

```
cd /home/z/my-project/Arivoo && source /home/z/my-project/pgbuild/env.sh
timeout 550 python3 harness/tests/test_recovery_contract.py
```
→ `PASS RCW-01` … `PASS RCW-08` (8 lines) + `RECOVERY-CONTRACT SUITE GREEN — RCW-01..08 (...)`, **exit 0**. Output sha256 `74e8964da928ad5023ef5104c8d224d54713597f63e8a636da6d5417ebc77003` — **byte-identical to runs 01–03 recorded at the GREEN tree 09d60b0**, which independently confirms the ARV-SIZE-002 compaction did not change the suite's observable output.

```
timeout 300 python3 harness/tests/test_export.py
```
→ `PASS EXP-01` … `PASS EXP-15` + `GREEN — the P3-09 acceptance suite (EXP-01..15) passes`, **exit 0**.

Sibling suites at HEAD: `test_sync.py` **exit 0**, `test_journal.py` **exit 0**, `test_client_acceptance.py` **exit 0**.

### 4. RCW-07 no-privileged-path mechanical scan

`grep -n -i "psql\|arv_app\|arv_read\|INSERT INTO\|SELECT \|UPDATE \|DELETE FROM\|CREATE TABLE\|CREATE DATABASE" harness/client.py` → **no matches** (grep exit 1). Every observation in the six conditions is a `subprocess` invocation of `commands.py` / `query.py` / `crash.py` / `export.py` / `sync.py` / `migrate.py` / `extract.py`. Caveat found and filed (F-079-7): the conditions do `from harness.adapters import pg` and call `create_scratch_db`/`drop_scratch_db` for rig lifecycle — see FINDINGS.

### 5. Export widening — structural checks + three adversarial live probes

TABLES after the slice (harness/export.py:66–90), restore insert order: `work, source, extraction_generation, anchor, highlight, highlight_lifecycle, bookmark, bookmark_lifecycle, note, note_lifecycle, note_reference, journal_block, reading_list, reading_list_member, reading_session, command_log, outbox, purge_ledger`.

FK ordering vs the migrations:
- `extraction_generation` after `source`, before every table naming it by FK — `reading_session` FKs `(generation_id, owner_scope) → extraction_generation` (0015:61) and lands after it. Correct.
- `journal_block` after `source` (0016:64 FK). Correct.
- `reading_list_member` after `reading_list` (0017:74) and after `source` (0017:75). Correct.
- **`note_reference` (export.py:83) BEFORE `journal_block` (export.py:84) — WRONG**: migration 0018 widened `ref_kind` to `journal_block` (0018:28–30 CHECK; revisioned shape 0018:32–35) and `enforce_note_reference_guard` requires the referenced journal_block row to **exist at note_reference INSERT time** (ARV-NTE-003). Probed live — see F-079-1.

Missing tables vs the migrations' CREATE TABLE set (0001–0019, 26 tables): `keyword_index`/`passage` correctly excluded (derived, rebuild — EXP-09 pins this); `agent_credential`/`agent_read_log` correctly excluded (the never-ride law, pinned by RCW-02's `creds_absent`); `schema_migrations`/`server_outbox` out of scope. **`reading_position` (0014) is missing** — probed live, see F-079-2. `evidence_event` (0002) / `import_journal` (0005) also absent (pre-existing P3-09 scoping; filed as a P3 note inside F-079-2, not separately material).

Reconciliation cascade (export.py:206–220) — probed live, see F-079-3. Also probed: the purge ledger's kind CHECK (0013:20) admits only `('work','source','anchor','highlight','bookmark','note')` — a live `INSERT ... kind='journal_block'` into `arv.purge_ledger` is rejected (`violates check constraint "purge_ledger_kind_check"`), so the new ledgered-`journal_block`/`reading_list` branch (export.py:211–216) is unreachable at this substrate.

### 6. Rig confinement

The two-DB sync rig, the 0001..0014 prior-baseline rig (copies migrations into a temp dir, drives `migrate.py` via the documented `ARV_MIGRATIONS_DIR` env — pg.py:40, migrate.py:492), and the restore-destination rig are all built **inside the condition functions / the suite**, not in any product module; no product command or query arm gained rig surface. The rig building is NOT confined to the test file though — it lives in `harness/client.py` itself (filed as F-079-7; the run dir's `notverified.txt` discloses exactly this class).

### 7. ARV-SIZE-002 compaction (`5be2e8c`) — behavior claim

AST comparison of all eight added functions between `09d60b0` and `5be2e8c` with docstrings stripped: **the code differs** (dead variables `g_lists`/`g_notes`/`g_caps` removed, the `walk_provenance` return field removed — no consumer exists, the `_reads` lambda-table refactor replacing two inline dicts, `["--after", after]` concatenation, the vacuous `len(_ids_of(g_ses)) >= 0` term dropped). So the commit message's "the behavioral code untouched" is inaccurate as literal prose. The **byte-equal behavior claim is nonetheless verified for every pinned output**: my live RCW run at HEAD reproduces the recorded 09d60b0 output digest `74e8964d…` exactly, and export/sync/journal/client-acceptance are green at HEAD. The `_reads` lambda table is late-binding-correct (invoked only after `nid`/`j1`/`lid` are bound). Filed as F-079-6 (documentation accuracy).

### 8. Records / docs

- CLAIMS.md: the CLAIM-079 row (opened 2026-11-12) names every file the diff touches, including `harness/tests/test_export.py` after the `f901c7f` scope widen — the row now matches the real diff surface (checked file-by-file).
- run records 01–08 read; run-04 is the disclosed verify exit-2; runs 05–08 green at `89a5ba6`.
- `notverified.txt` (untracked draft) honestly lists the rig-class, single-crash-arm, read-set-scope, and token-not-in-blobs limits — several of which this review confirms and pushes further (see FINDINGS).

---

## FINDINGS

**F-079-1 (P1, open) — the widened export machine cannot restore a note @-reference of kind `journal_block` (TABLES insert-order defect).**
`harness/export.py:83` inserts `note_reference` before `harness/export.py:84` inserts `journal_block`, but migration 0018's `enforce_note_reference_guard` checks target existence at INSERT time (ARV-NTE-003). Live proof (fresh scratch rig, real CLIs only):
```
create_note --ref journal_block:<id>@1        → ACK status=committed (legal per 0018 CHECK)
export --owner A                              → exit 0, tables=18 rows=12
restore --archive ... (clean migrated dst)   → exit 1:
  FAIL ARV-EXP-007: the insert phase failed (the transaction rolled back — nothing
  half-complete) — ERROR: ARV-NTE-003: the referenced journal_block (…, 1) does not
  exist in the caller's scope …
post-restore get-note                          → FAIL ARV-QRY-001 (nothing restored)
```
The whole archive is refused (fail-closed, no partial state — good), but the restore is **impossible** for any owner whose notes reference journal blocks, which record 71 §2 and the PLAN 4F row explicitly claim ("the note @-references (the seven kinds)"). RCW-02 cannot catch it: the lifecycle walk writes only `highlight:` and `source:` refs (harness/client.py:424–425), so the pin is green while a legal reference kind breaks restore. The symptom half-existed pre-slice (journal blocks were not exported at all at `d21ca44e`), but the *claim* and the *table coverage* are this slice's, so the ordering defect is in-slice. Repair: insert `journal_block` (and, defensively, `reading_list`) before `note_reference` in TABLES, and add a journal-block-ref case to the RCW-02 walk / EXP fixture.

**F-079-2 (P1, open) — `reading_position` is not exported: the owner's saved reading position is silently lost across export/restore, and RCW-02's byte-equality pin is vacuous for it.**
Migration 0014 (landed P4-A, CLAIM-066) is an append-only, owner-scoped, **authored** family — not derivable, not rebuildable, not in the PLAN's derived list. It is absent from TABLES (18 tables, confirmed in the live manifest) and absent from RCW-02's `_ARMS` read set (harness/client.py:441–451), even though the walk itself writes a position (harness/client.py:407) and `P4_FAMILIES` counts "position" among the nine families (harness/tests/test_recovery_contract.py:115–117). Live proof:
```
save_position --start 2 --end 9               → ACK committed
export                                          → manifest tables: 18, no reading_position
restore (clean dst) + extract + rebuild         → exit 0 "RESTORED … state_hash_match=true"
pre-export  get-position → {"state": "saved", "save_ordinal": 1, "start_off": 2, "end_off": 9, …}
post-restore get-position → {"state": "no_position_saved", …}
```
The restore declares success while authored owner state is gone — the SYS-10 "without silent loss" class, and SYS-07's "no unique authored content exists only in derived/live state" spirit. The RCW-02 check text claims "every landed family … post-restore reads BYTE-EQUAL the pre-export reads", but the pin can pass with the position family entirely lost — exactly the "assertion that could pass with the feature broken" class. (Minor riders, same root: `evidence_event`/`import_journal` are also unexported — pre-existing P3-09 scoping, P3.) Repair: add `reading_position` to TABLES after `extraction_generation` (it FKs source + generation, 0014:60–61) and add a position arm to `_reads`.

**F-079-3 (P1, open) — the new reconciliation source-cascade is dead code; the claimed "ledgered source drops every row bound to it" is falsified live (and it regresses the EXP-07 scenario for extracted sources).**
`harness/export.py:217–220` re-derives the purged source ids from `rows["source"]` — but `drop(kind, "id", gone)` at export.py:195 has **already removed** those rows, so the comprehension is always empty and the four `drop()` calls never fire. Live proof (ledgered source at the destination, extracted corpus + journal block bound to it in the archive):
```
restore → exit 1: FAIL ARV-EXP-007 … ERROR: insert or update on table "extraction_generation"
          violates foreign key constraint "extraction_generation_source_id_owner_scope_fkey"
          DETAIL: Key is not present in table "source".
```
Pre-slice this scenario **completed** (extraction_generation was not exported, so nothing dangling remained); post-slice the archive carries generation rows for any extracted source and the dead cascade leaves them pointing at the dropped source — the restore that EXP-07 represents now refuses. `test_export.py`'s EXP-07 still passes only because its fixture never extracts the source (no `extract` invocation in the fixture — confirmed) and writes none of the new families, so the broken path has zero content coverage anywhere. Additionally the ledgered `journal_block`/`reading_list` branch (export.py:211–216) is unreachable: `arv.purge_ledger`'s CHECK (0013:20) rejects those kinds (live insert → `purge_ledger_kind_check` violation). Net: the entire "reconciliation cascade extended to the new families" is non-functional — half unreachable by constraint, half dead by ordering. Repair: use the already-computed `dropped["source"]` set directly instead of re-reading `rows["source"]`, and either drop the unreachable branch or note it as forward-speculative.

**F-079-4 (P2, open) — RCW-08's observed-families phase gate has vacuous entries.**
The gate rides `condition_recovery_walk`'s `families` dict (harness/client.py:372–382), and several entries are satisfiable with zero content: the recovery walk **never writes a bookmark**, so `"bookmark": g_bms.returncode == 0` is an empty `list-bookmarks` answer (exit 0) — the family counts as "observed … REAL at the boundary" with no bookmark in the store; `"reading_session"` and `"reading_list"` are exit-code-level only (an empty `list-session-events` is exit 0 — the session event's absence would not flip the entry). The pin `observed >= set(P4_FAMILIES)` (suite:284) therefore over-claims: the "phase gate's mechanical form" can be green with the bookmark family functionally absent from the walk's store (bookmark's only content-level coverage is RCW-02's `walk_complete`). Repair: have the recovery walk author a bookmark (and assert non-empty reads for reading_session/reading_list) or drop "bookmark" from the walk-observed set and gate it from RCW-02's walk instead.

**F-079-5 (P3, open) — RCW-01's pin is weaker than its own stated contract.**
The check prose claims "the same-key replay acks status=replayed with the SAME result_ref", but `ok1` (suite:163–167) pins only `status=replayed` (via `replay_replayed`); neither the result_ref identity nor the no-duplicate convergence (exactly one block for the key) is asserted — `families["journal_block"]` accepts `g_b2.returncode == 0` without comparing content or count. The underlying replay machinery is pinned by earlier suites (per the run dir's notverified.txt), so this is pin-strength debt on the RCW registry's own letter, not a live defect.

**F-079-6 (P3, owner-accepted-debt) — ARV-SIZE-002's "the behavioral code untouched" wording is inaccurate.**
The compaction (`5be2e8c`) refactored the conditions (dead-variable removal, the `walk_provenance` return field removed, the `_reads` lambda-table refactor, a vacuous `>= 0` term dropped) — AST comparison with docstrings stripped differs for all eight functions. The behavioral claim itself is nonetheless **verified**: the RCW suite's output at HEAD is byte-identical to the recorded pre-compaction digest (`74e8964d…`), and the export/sync/journal/client-acceptance suites are green at HEAD. No behavioral regression observed; the prose overstates "untouched".

**F-079-7 (P3, owner-accepted-debt) — the P4-F conditions put rig-provisioning (privileged adapter calls) inside `harness/client.py`.**
`condition_export_restore` / `condition_prior_state_migration` / `condition_sync_conflict` import `harness.adapters.pg` and call `create_scratch_db`/`drop_scratch_db` (client.py:399, 481, 510, 563, 565, 608, 614–615, 649–650) — the first privileged-path usage in the "clean external client" (the base tree had none; a real external client cannot CREATE DATABASE). It is strictly rig lifecycle: no observed content flows through it, every observation still rides the real CLIs, and the run dir's `notverified.txt` discloses exactly this class. The RCW-07 string scan cannot see it by construction (`_pg.create_scratch_db` matches none of the scanned tokens). Accepted as disclosed debt; worth keeping out of future conditions if the client is ever held up as the literal external-client reference.

**F-079-8 (P3, open — expected to close at the artifact finalize) — the measured set lags the content head.**
Runs 01–08 record only trees `09d60b0`/`89a5ba6`; no run record exists at the compaction `5be2e8c` or the scope-widen `f901c7f`, and `proofsheet.md` + `notverified.txt` are untracked drafts binding `89a5ba6`. The 5be2e8c commit message claims sibling-suite greens at the compacted tree without a recorded run. This review's live runs at HEAD close the evidential gap (RCW exit 0 with the byte-identical digest, EXP/sync/journal/client-acceptance exit 0), but the finalize commit must re-bind the proof sheet at the final content head per the repo's own anti-lag ordering rule.

---

## VERDICT

**BLOCKED.**

The process spine of this slice is genuinely sound — the LAW-11 RED chain is real and reproduced live (tests-only commit `4eb4944` failing with ARV-TEST-000 against a client.py that lacks the six conditions, digest-verified binding, honest pin-type amendment for RCW-05, ARV-RED-008 gate registration at the binding commit, the gate's own ARV-RED-006 forcing the test_export.py amendment into the typed record), the RCW and EXP suites are green at HEAD with the recorded digest reproduced byte-for-byte, and the no-privileged-path scan holds for every observation. But the slice's central product claim — "the full-lifecycle export/restore round-trip over every landed family" over the widened export machine — is falsified live in three independent ways that the suite's own fixtures cannot see: a legal note @-reference to a journal block makes the whole archive un-restorable (TABLES insert-order defect, F-079-1); the owner's saved reading position is silently lost on restore while RCW-02's byte-equality pin stays vacuously green (F-079-2); and the newly-claimed reconciliation cascade for a ledgered source is dead code that regresses the EXP-07 scenario to a typed refusal for any extracted source (F-079-3). All three are P1, all three are in the slice's declared scope (record 71 §2's letter, the PLAN 4F row, SYS-10), and all three have concrete one-line-to-few-line repairs (reorder TABLES, add `reading_position` + a read arm, use `dropped["source"]` instead of re-reading `rows["source"]`). PASS may not carry open P0/P1; this carries three. Repair the three P1s (with pins that actually exercise the failing shapes — a journal-block ref in the RCW-02 walk, a position arm in `_reads`, an extracted-source purge case in the EXP fixture), then re-run this SEV round.

---

## INT TRACE

INTENT-LEDGER.md (`/home/z/my-project/Arivoo/INTENT-LEDGER.md`) rows this work serves — the P4-F / Phase-4-exit chain:

- **INT-127** (owner turn 22, ledger line 23) — "complete Phase 3 … establish the Phase 4 foundation and implement Phase 4 (P4-00 + P4-A..P4-F + the exit gate's day-one workflow)". P4-F is the last implementation row of this order.
- **INT-131** (turn 26, line 27) — the ordered slice sequence "… P4-00 → P4A..P4F → the Phase 4 exit gate"; P4-F is its terminal element.
- **INT-140** (turn 35, line 38) — the build-the-product turn with the continuation directive through "P4-A..F → the Phase 4 exit gate".
- **INT-143** (turn 38, line 41) — "the complete Phase 4 roadmap P4-00..P4-F" + "do not stop at writing a plan".
- **INT-144** (turn 39, line 42) — the protocol amendment: the do-not-stop horizon is Phase 4 completion (the P4-F slice + the exit gate are that horizon's last items).
- **INT-145** (turn 41, line 43) — the standing merge authorization ("until phase 4 is ready to go") under which this slice will merge after checks.
- **INT-146** (turn 42, line 44) — the no-pause cadence amendment, horizon restated "until phase 4 is done".
- Background instruments: **INT-125** (the per-slice systems-engineering verification directive + the §7.8 Phase 4 exit gate and §8 seven-rounds protocol) and **INT-122** (the per-slice SEV requirement), which this SEV round itself discharges.

PLAN.md SYS requirement ids:

- **SYS-11** (PLAN.md:199) — "Each implementation slice closes a V-model trace and has independent systems-engineering verification before merge." This review is that verification for CLAIM-079; it is currently refusing the trace closure.
- **SYS-10** (PLAN.md:198) — "Export/restore preserves authoritative data, revision history, and governed purge state without silent loss or resurrection." F-079-1/F-079-2/F-079-3 are SYS-10 violations (restore-impossible for a legal reference kind; silent loss of the position family; non-functional purge reconciliation).
- Supporting traces verified green by the suite: **SYS-08** (crash recovery + idempotent replay — RCW-01), **SYS-07** (derived state rebuildable — RCW-03/EXP-09), **SYS-03/SYS-04** (owner scope, idempotency/conflict — RCW-04/RCW-06).
- PLAN.md:386 (the 4F row) and PLAN.md:408 (the P4-F elaboration, CLAIM-079) are the requirement rows this slice implements; record 71 §2 (`context/extracted/71-P4F-RECOVERY-CONTRACT-GATE.md:28–75`) is the elaborated contract whose export/restore letter the P1 findings falsify.

---

## LIMITS

What this review did NOT verify (honest list):

1. **`make verify` in full** (the whole TESTS tuple + known-bad set + gate dispatch + canonical layer) was not run; the RCW, export, sync, journal, and client-acceptance suites were run individually at HEAD. The recorded run-05 verify exit 0 at `89a5ba6` was not re-executed.
2. **The GitHub-side merge state** — no PR exists yet for CLAIM-079 (the slice is pre-finalize); branch protections, the five required checks, and the merge-gate review chain are all still pending and were not verifiable.
3. **The other ~30 sibling suites** in gate.py's TESTS tuple were not re-run (only the five named above); regressions there from the export.py widening would surface at the finalize verify, not here.
4. **Token never-in-blobs**: the credential-absence proof sweeps the manifest text and table set only, not the blob files' bytes — the same bound the run dir's notverified.txt discloses; not extended here.
5. **The remaining note-reference kinds' restore ordering** beyond `journal_block` (`work/source/anchor/highlight/bookmark/note` were confirmed ordered correctly by table position; only a journal_block-ref probe was executed live).
6. **A same-BODY-different-KEY journal replay** and the other crash-matrix arms (pre-commit, post-ack) — out of this suite's declared scope per its notverified list; not re-proven.
7. **The docs/records prose** (STATE.md, AGENTS.md, WORKLOG Task 95, record 71 §1/§5) was skimmed only for the INT/SYS trace and the CLAIMS scope row; no line-by-line records audit was performed.
8. **RCW-02's per-column coverage** of the new tables: the byte-equality rides the ten read arms; columns not surfaced by any read arm (e.g. `run_id`, `input_hash`, `dwell_ms` beyond the session list line) ride on the manifest hash + restore completion line only — the same bound the slice itself discloses.
