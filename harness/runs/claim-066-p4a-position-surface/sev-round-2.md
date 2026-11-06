# SEV round-2 — CLAIM-066 / P4-A slice two (the source-open/position surface)

- **Agent label:** agent-9f27c4ab
- **Date:** 2026-11-06 (round 2, fresh context, adversarial re-sweep)
- **Slice:** `slice/claim-066-p4a-position-surface` — CLAIM-066, P4-A slice two (the source-open/position surface)
- **Base:** `origin/main` = `562b70f` (PR #100, CLAIM-065's merged head)
- **Head:** `057b426` (the round-1 repair commit)
- **Commit chain:** `7105dad` (commit A: post-#100 reconciliation + record 58 + scope.txt; NO implementation) → `a571792` (the RED: test_position.py + gate.py TESTS registration + red-01.txt; NO implementation — `git show --stat` re-verified) → `da9967b` (the typed red record, bound to the RED commit) → `d8a1f7a` (the GREEN: save_position + get-position + migration 0014 + crash/sync/capability membership) → `057b426` (the round-1 repairs: the F1 delivery branch + SYN-18, the F2 scope amendment for sync.py/crash.py, the F3 comment, the run records 06-08, the round-1 report)

## 1. What I ran

| # | What | Result |
|---|------|--------|
| 1 | `git diff 562b70f...HEAD` (every hunk, 27 paths) + the round-1 report | read in full; the repair diff `git diff d8a1f7a..057b426` isolated to: sync.py `_cli_args` branch, test_sync.py SYN-18, commands.py comment, scope.txt/CLAIMS.md +2 paths, red-records.json amendment, run-06..08, sev-round-1.md |
| 2 | `python3 harness/tests/test_position.py` | exit 0 — **6/6 PASS** (POS-01..06); output sha256 `14a84399…` **byte-identical to run-01/02/03/06's recorded digest** |
| 3 | `python3 harness/tests/test_commands.py` | exit 0 GREEN (S3 a-e) |
| 4 | `python3 harness/tests/test_migrations.py` | exit 0 GREEN (S1 a-e + M0 f-l; the widening's blast radius) |
| 5 | `python3 harness/tests/test_sync.py` | exit 0 — **SYN-01..18 all PASS** (18 PASS lines); output sha256 `4e0c3543…` **byte-identical to run-07's recorded digest** |
| 6 | `make verify` | exit 0 — gate GREEN (suites + red records + scope/size + lint + deps + known-bads + proofsheet selfcheck), canonical layer **54 checks / 0 failures** |
| 7 | RED re-observation: `git worktree @ a571792` → `python3 harness/tests/test_position.py` | **exit 1, ARV-TEST-000**, first line byte-identical to `red-01.txt`; the RED commit carries only test_position.py + gate.py + red-01.txt (no implementation smuggled) |
| 8 | Red-records chains (both amended files) | **exact at every link** — see §2 F1/F4 below |
| 9 | The gate's own modules live: `scope.check_scope(diff)` / `claims.check_branch_claim(...)` / `claims.check_registry()` + the full PR-mode gate `python3 harness/gate.py --slice claim-066-p4a-position-surface --diff 562b70f --skip-suites` | **ARV-SCOPE-002 + ARV-CLM-002 on `harness/tests/test_sync.py` — gate exit 1** (the new P1, finding 1); registry GREEN |
| 10 | Two-DB F1 probes on own scratch rigs (created via `pg.create_scratch_db`, migrated incl. 0014, **dropped after**) | delivery + site-local generation binding verified; the unextracted-server case verified retryable with the named ARV-POS-002 — see §2 |
| 11 | Adversarial battery (a)–(f) + extras on own scratch DB (**dropped after**) | see §4 |
| 12 | Run-records audit run-01..08 | all exist, all `exit_code: 0`; commit-field analysis under §3 finding 3 |

## 2. Repair verification

**F1 (P1, the dead letter) — VERIFIED LIVE, the repair is real and complete.**
- `python3 harness/tests/test_sync.py`: exit 0, **SYN-01..18 all PASS**, SYN-01..17 untouched; the suite's output digest reproduces run-07's record byte-exactly.
- Own two-DB rig (fresh scratch LOC+SRV, both migrated to 0014): import + extract on both sites, `save_position` on LOC, one sync pass → the outbox row rests **`acknowledged` with `server_ref=<server-source>@1`**; the server's `arv.reading_position` row binds **the SERVER's own serving generation** (server gen ≠ local gen — no cross-site uuid transplant; the site-local binding law holds); the server's read arm answers `state=saved, save_ordinal=1` with the delivered offsets.
- The unextracted-server probe (second fresh rig, server NOT extracted): the delivered save rests **`retryable` with `last_reason='FAIL ARV-POS-002: source … has no current extraction generation — …'`** — the command's own named reason, **not ARV-SYN-000**; the server holds 0 position rows; after extracting on the server, the next pass **acknowledges** (`server_ref=<srv>@1`, offsets correct) — recovery observed. After the default `--max-attempts 3` the row flips terminal `failed` still naming ARV-POS-002 — that is the pre-existing P3-08 outbox terminal policy (sync.py's module law, the same law as the outage/ARV-SYN-009 dependency classes), not a new defect; the claim "a truthful state, never a dead letter" holds (delivery is possible and the reason names the true blocker).
- `_cli_args` coverage cross-check: every `_SYNC_COMMANDS` member (incl. `save_position`) now has a delivery branch — no other dead letters.

**F2 (P1, the scope declarations) — PARTIALLY VERIFIED, and the repair reintroduced the same breach on a third path.**
- The two round-1 files ARE now declared: `harness/sync.py D-041` + `harness/crash.py D-041` added to scope.txt and to the CLAIMS.md CLAIM-066 scope cell (git diff d8a1f7a..057b426 confirms exactly those two additions).
- **BUT the repair commit itself also modified `harness/tests/test_sync.py` (the SYN-18 pin) and left it undeclared in both** — live refusals: `scope.check_scope` → `ARV-SCOPE-002: harness/tests/test_sync.py outside the declared scope`; `claims.check_branch_claim` → `ARV-CLM-002`; the full PR-mode gate exits 1. See finding 1.

**F3 (P3, the stale comment) — VERIFIED.** `harness/commands.py:1390-1394` now reads "command_log.result_ref carries each family's address form — a uuid text for entity commands, `<source>@<ordinal>` for positions, TEXT since 0014; the owner name is NOT a valid ref…" — the post-0014 truth, no stale UUID claim remains.

**Red-records chains (both amended files) — exact at every link, every amendment additive.**
- `test_position.py`: sha256 at HEAD `f26ca6ed…` = `current_sha256` = the amendment's `new_sha256`; the prior `ed98a219…` = `git show a571792:… | sha256sum` = `prior_sha256` = `binding_sha256` (binding_commit `a571792` exists and carries that exact form).
- `test_sync.py`: sha256 at HEAD `c25318b5…` = `current_sha256` = the last amendment's `new_sha256`; the prior `4a4d8079…` = `git show d8a1f7a:… | sha256sum` (= also the untouched `562b70f` form — the GREEN commit did not touch this file, so the amendment's prior is honestly the pre-SYN-18 form).
- Additivity re-derived from `git diff d8a1f7a..057b426 -- harness/tests/test_sync.py`: the docstring's SYN-18 case block, the SYN-18 check block, and the final GREEN line's `SYN-01..17`→`SYN-01..18` — **no assertion removed, SYN-01..17 byte-untouched**.

## 3. Findings

1. **[P1] the repair's own pin file is undeclared: `harness/tests/test_sync.py` is in the diff (the SYN-18 addition) but in neither `scope.txt` nor the CLAIMS.md CLAIM-066 scope cell — the PR-mode gate refuses this slice as-is (the round-1 F2 class, reintroduced by the F1 repair itself).**
   `git diff --name-only 562b70f...HEAD` = 27 paths; the declarations name 16 globs; `harness/tests/test_sync.py` is the one path outside them (the F2 repair added only `harness/sync.py` + `harness/crash.py`, overlooking that the F1 repair's pin rides a THIRD file). **Live evidence (the gate's own modules + the full PR-mode gate):** `scope.check_scope(...)` → `ARV-SCOPE-002: harness/tests/test_sync.py outside the declared scope — scope breach (LAW-06)`; `claims.check_branch_claim(...)` → `ARV-CLM-002: CLAIM-066: the diff touches 'harness/tests/test_sync.py' OUTSIDE its declared scope`; `python3 harness/gate.py --slice claim-066-p4a-position-surface --diff 562b70f --skip-suites` → exit 1 with both refusals. The committed run-08 (`make verify`) passed because it runs in selfcheck/no-diff mode — the refusal fires exactly at PR time. *Repair in-slice:* add `harness/tests/test_sync.py D-041` to scope.txt and to the CLAIMS.md scope cell (the CLAIM-065 precedent declares its amended blast-radius suite `harness/tests/test_bookmark.py` the same way), then re-observe the PR-mode checks green. Cite: harness/runs/claim-066-p4a-position-surface/scope.txt (declaration list), CLAIMS.md CLAIM-066 scope cell, harness/scope.py:259, harness/claims.py:249.

2. **[P3, wording] record 58 §3 and STATE.md's exact-next-action phrase "the RED (test_position.py + migration 0014 — the POS registry …)" can be misread as the RED commit carrying migration 0014.** The RED commit `a571792` is tests-only (test_position.py + gate.py + red-01.txt) and red-01.txt itself records `migration 0014 present: False` (machinery-absent) — the honest form; but the phrasing names the migration inside the RED's parenthetical. One-clause clarification ("the RED (test_position.py — pinning the POS registry incl. the 0014 schema conventions)"). Cite: context/extracted/58-P4A-POSITION-SURFACE.md §3, STATE.md "Exact next action".

3. **[P3, completeness/disclosure] run-06/07/08 record `commit: d8a1f7a…` although they were observed at the (pre-commit) repair tree that became `057b426`.** `write_record` captures `git rev-parse HEAD` at run time (harness/proofsheet.py:47-58); the three records' `recorded_at` (15:48:29 / 15:48:48 / 15:54:02) precede the `057b426` commit time (15:54:30), and the CLAIM-065 run-06 precedent records the pre-repair GREEN HEAD `82211b2` the same way — the convention is documented (proofsheet.py:84-96) and the validator only requires the commit to exist (sev.py `_check_run_records`). Truthfulness is independently established here: run-06's digest (POS suite) and run-07's digest (SYN suite) **reproduce byte-exactly at the 057b426 tree** — digests only reachable with SYN-18 present, proving the runs observed the repair content. Disclosed so the push-time sheet derivation and any later reader do not misread the commit field as "the runs ran at the GREEN tree".

**Zero open P0. One open P1 (finding 1). Two P3s (findings 2, 3).**

Observations (no class):
- The unextracted-server delivery rests retryable with the truthful ARV-POS-002 reason and auto-recovers once the server extracts (observed); the terminal flip after `--max-attempts 3` is the pre-existing outbox policy (sync.py module law), identical for the outage/dependency classes — not a slice defect.
- `make verify`'s captured output is not byte-deterministic across runs (run-04 ≠ run-05 at the same tree), so those digests are informational; the deterministic suites (POS/SYN) reproduce byte-exactly. Exit 0 reproduced.
- The PR-mode gate also raises `ARV-PRF-002: no Proof Sheet on disk` — the expected pre-push state (the sheet assembles at the artifact re-bind step); noted because until finding 1 is repaired the gate refuses regardless.
- test_position.py's `cmd()` helper retains a dead `--crash-at` passthrough branch (harness/tests/test_position.py:142-143) — a leftover from the RED form; the crash arm correctly routes through `harness/crash.py --point`. Cosmetic, never invoked.

## 4. Probes

All probes on own scratch DBs (rig on port 5433; `pg.create_scratch_db`, migrated incl. 0014; **all dropped after — zero `arv_*` databases remain; `git status` clean apart from this report**).

| Probe | Observed |
|---|---|
| **F1 delivery (two-DB rig)** | outbox `acknowledged`, `server_ref=<server-source>@1`; server row `start|end` correct and its `generation_id` IS the server's own current generation (server gen ≠ local gen — site-local binding law); server get-position answers `state=saved, save_ordinal=1` |
| **F1 unextracted-server (second rig)** | row rests `retryable`, `last_reason` names **ARV-POS-002** in full, server holds 0 rows, **not ARV-SYN-000**; pass 2 stays retryable (attempts 2); after the server extracts, the next pass **acknowledges** with correct offsets (recovery); pass 3 without extraction flips `failed` per the standing max-attempts policy, reason unchanged |
| **a. write no-oracle** | owner B on A's extracted source vs B on an absent uuid: both exit 1, `FAIL ARV-POS-001:`, **stdout byte-equal after id-normalization** (verified with BOTH ids normalized; stderr equal) |
| **b. hostile INSERTs as arv_app** | skipped ordinal 99 → `ARV-POS-004` ("not the next lawful save (1 + 1)"); SRC2's generation on SRC1's row → `ARV-POS-006` ("never crosses sources"); B inserting into A's scope refused fail-closed (the guard's RLS-scoped generation read sees nothing → ARV-POS-006 fires ahead of the WITH CHECK); row count unchanged after every attempt |
| **c. UPDATE/DELETE as superuser** | both refuse `ARV-POS-005` (the append-only trigger fires even for postgres) |
| **d. generation binding across re-extraction** | saved `saved_generation_id` byte-stable = gen1, `current_generation_id` = the new gen, `generation_matches:false`, saved offsets unchanged; a NEW save binds the new generation (`matches:true`, ordinal advances) — no silent retarget |
| **e. replay/409** | same key+body → `status=replayed`, same `result_ref=<src>@3`; same key+different body → exit 1 `ARV-CMD-409`, rows 3→3 (zero effect) |
| **f. import_source plain-uuid replay** | `status=replayed`, `result_ref` a plain 36-char uuid (widening lossless); `command_log.result_ref` data_type `text`; every import row matches `^[0-9a-f-]{36}$` while every save_position row does not; serving index `command_log_result_ref_idx (owner_scope, result_ref)` present |
| **read-arm no-oracle (extra)** | get-position vs get-source on the same absent id: exit 1, **stdout byte-equal**; B reading A's saved source vs B reading an absent id: byte-equal after id-normalization — never a leak that a position exists; in-scope never-saved source: typed `no_position_saved` ANSWER at exit 0 with `api_version=1` |
| **POS-003 offset law (extra)** | negative / empty (start==end) / beyond-text offsets all refuse `ARV-POS-003` exit 1 — never clamped |

## 5. Disposition

**BLOCKED** — one open P1:

- **Finding 1 (P1)** `harness/tests/test_sync.py` (the F1 repair's own SYN-18 pin) is changed in the diff but undeclared in scope.txt and the CLAIMS.md CLAIM-066 scope cell — the PR-mode gate refuses live (ARV-SCOPE-002 + ARV-CLM-002, gate exit 1). The round-1 F2 class, reintroduced by the repair commit itself.

P3s (repair-in-slice, no re-SEV required beyond re-observing the gate): **finding 2** (the record-58 §3 / STATE.md "RED (test_position.py + migration 0014)" wording ambiguity) and **finding 3** (run-06..08's commit field naming the pre-commit HEAD `d8a1f7a` — truthful under the documented capture convention and proven by byte-exact digest reproduction at `057b426`, disclosed for the push-time reader).

Everything else the slice claims was re-verified and holds: the F1 delivery is real end-to-end on my own two-site rig (translated source, site-local generation binding, `server_ref` ack, server read arm answering); the unextracted-server case is a truthful retryable ARV-POS-002 with observed recovery; the F3 comment now states the TEXT truth; the POS suite 6/6, commands/migrations/sync suites green, `make verify` green (canonical 54/0); a true RED at `a571792` re-observed byte-identical to red-01.txt with no implementation in the RED commit; the red-records chains exact at every link with the SYN-18 amendment purely additive; the no-oracle byte-equality on both boundaries; the ordinal/append-only/generation-bind substrate guards incl. superuser and cross-scope hostile writes; the generation binding honest across re-extraction; replay/409; the TEXT widening lossless for the uuid families; all eight run records exit 0.

*Repair finding 1 (one line in scope.txt + one entry in the CLAIMS.md scope cell), apply the two P3 one-liners if desired, re-observe the PR-mode gate green — then this slice is a PASS candidate for round 3.*
