# D-042 (1a) MERGE-GATE REVIEW, ROUND 2 — PR #114, slice `claim-079-p4f-recovery-contract-gate` (CLAIM-079, P4-F)

- Reviewer: merge-gate host reviewer, round 2 (D-042 1a substantive re-review; did NOT build this slice; read-only over the repo)
- Date: 2026-11-13
- Repo: `/home/z/my-project/Arivoo`, branch `slice/claim-079-p4f-recovery-contract-gate`, HEAD = `83091c4` (the claimed final head; working tree clean)
- Round-1 report read first: `harness/runs/claim-079-p4f-recovery-contract-gate/d042-round-1.md` (verdict BLOCK-MERGE, one P1 + two P3s)
- Round-2 probes (outside the repo, per protocol): `/home/z/my-project/scripts/d042_r2_probe_ledgered_source.py` (the round-1 P1 shape, standalone form) and `/home/z/my-project/scripts/d042_r2_probe_p3_shapes.py` (the anchor/work P3 shapes; parameterized `PROBE_REPO` so the same probe ran against an extracted `origin/main` tree at `/tmp/basecheck` for the pre-existence check)

---

## VERIFIED

### 1. The ordering repair in `_drop_purged` — CORRECT and COMPLETE for the slice's surface (the round-1 P1's owning site)

Read line-by-line at HEAD (`harness/export.py:160-224`) and diffed three ways (`origin/main..HEAD`, `32b04e3..HEAD` for the repair commits `3b99d3a`/`e90e1b8`, and `2c80753..83091c4` for the compaction):

- **The registration now precedes the F3 filter.** The per-kind ledgered loop (`export.py:206-212`) registers ledgered `journal_block`/`reading_list` ids in `dropped` (`dropped[kind] = dropped.get(kind, set()) | gone`, :210) and drops `reading_list_member` rows of a ledgered list (:211-212). The ledgered-source cascade (`export.py:213-219`) computes `gone_sources = dropped.get("source")` — populated by the `_ENTITY` loop's `dropped[kind] |= gone` (:194) — and registers EVERY cascade-dropped id for `journal_block`, `reading_list_member`, `reading_session`, `extraction_generation`, `reading_position` (`dropped[t] = dropped.get(t, set()) | {...}`, :217-218) BEFORE `drop(t, "source_id", gone_sources)` (:219). The F3 filter (`rows["note_reference"] = [...]`, :221-223) is now the LAST statement of the function before `return rows` (:224). The `git diff 32b04e3..HEAD -- harness/export.py` shows exactly this relocation: the F3 block moved from before the F-079-3 block to after it, and the two `dropped[t] |= ...` registration lines added. The e90e1b8 commit message's account (the intermediate repair registered after the filter — the second falsification) matches the diff history.
- **The `gone_sources` keying is sound**: it reads `dropped["source"]` (the registry), never a re-read of the drained `rows["source"]` — the round-1 dead-code class stays repaired.

### 2. The ref_kind walk — every kind's registration path traced (the review job's exhaustiveness demand)

Against 0018's `note_reference_ref_kind_check` enum (`work`, `source`, `anchor`, `highlight`, `note`, `bookmark`, `journal_block`) and 0013's `purge_ledger_kind_check` (`work`,`source`,`anchor`,`highlight`,`bookmark`,`note`):

- `journal_block` — THE P1 KIND: ledgered → registered (:210); source-bound under a ledgered source → registered (:217). **No unregistered path remains.** Live-verified below.
- `highlight`/`bookmark` — ledgered → registered (:194); under a ledgered anchor/source/work → registered in the capture-tree branch (`dropped[t] |= ents`, :189). Complete.
- `note` — ledgered → registered (:194) and its refs drop by `note_id` (:197); a ref to a ledgered note drops via the F3 filter. Complete.
- `source` — ledgered → registered (:194). Sources under a ledgered WORK are neither dropped nor registered — see FINDING 2 (pre-existing at base).
- `work` — ledgered → registered (:194). Complete for the ref filter (the work-branch FK shape is FINDING 2).
- `anchor` — ledgered → registered (:194, the F6 direct branch); anchors under a ledgered SOURCE/WORK are dropped (:192) but NOT registered — round-1's P3, unchanged by this slice (verified: the source/anchor/work branch is byte-identical between `origin/main` and HEAD), see FINDING 1.
- `reading_session`/`extraction_generation`/`reading_position` drops are FK-required (0015/0006/0014's `REFERENCES arv.source`), not ref_kind targets — their registration (:217) is harmless completeness; the DROP is what satisfies the insert order.

### 3. The pin — REAL, non-vacuous, correctly wired

- `harness/client.py:540-566` (`condition_ledgered_source_restore`): import → a SOURCE-BOUND creative journal block (`--source-id sid`, :546-547) → a note `--ref journal_block:{j1}@1` (:549-550) → export → clean migrated destination → the caller's `ledger(sid, denv)` hand (:557) → restore (:558) → `get-note` refs re-read (:559-560) → `dangling_refs = sum(1 for r in refs if r.get("id") == j1)` (:563), returned as an INT.
- The wiring (`harness/tests/test_recovery_contract.py:179-225`): `ls_ledger` (:190-198) is the SUITE's substrate hand — a direct `psql ... INSERT INTO arv.purge_ledger` with `SET app.current_owner='A'` (the EXP-07 app_sql pattern) — passed as the `ledger` callable into the condition (:201-202); the conjunction `ok2` (:205-213) requires `led["written"]`, `led["export_exit"] == 0`, `led["restore_exit"] == 0`, AND `led["dangling_refs"] == 0` alongside the round-trip's own six clauses.
- **Non-vacuous**: `query.py`'s NOTE_SQL (:205-213) builds refs as `json_build_object('kind', r.ref_kind, 'id', r.ref_id, 'revision', r.ref_revision)`, so `r.get("id")` IS the ref_id — the note carries exactly one ref (to `j1`) pre-restore; a survived ref yields `dangling_refs == 1` and the conjunction goes RED. The round-1 refusal (ARV-NTE-003 under ARV-EXP-007, exit 1) trips `restore_exit == 0`. Both halves of the failing shape are mechanically discriminated.

### 4. The round-1 P1 shape — LIVE-VERIFIED PASSING at HEAD

My standalone probe (real CLIs only, fresh scratch DBs, the ledger row written probe-side — NOT through the pin's own code path): `import=0 block=0 note=0 export=0 ledger=0 restore=0 dangling_refs=0 note_read=0` — **PASS**. The restore completes (exit 0) and the restored note reads back with zero refs to the cascade-dropped bound block. The round-1 falsification (`restore exit 1, FAIL ARV-EXP-007 ... ARV-NTE-003: the referenced journal_block ... does not exist`) does not reproduce.

### 5. RCW-07's source scan — GREEN, re-executed

`grep -n "psql|arv_app|arv_read|INSERT INTO|SELECT " harness/client.py` at HEAD: **zero matches** (grep exit 1). The pin's design genuinely moved the privileged ledger write to the suite side (`test_recovery_contract.py:190-198`), keeping `client.py` clean of every privileged path.

### 6. The size law — exactly 400, the gate's own arithmetic

`git diff --numstat origin/main..HEAD -- '*.py' ':(exclude)harness/tests/*'`: `harness/client.py` +353/-7, `harness/export.py` +44/-10, `harness/gate.py` +3/-0 — **added = 400 exactly** (the compaction moved the split from 358/39/3 to 353/44/3; the total holds at the ARV-SIZE-002 bound).

### 7. No counter-productive CLAIM-069 alteration

All seven pre-existing `condition_*` bodies shared between `origin/main` and HEAD extracted and diffed: five are byte-identical; `condition_deleted_target` differs by ONE blank line (whitespace only); `condition_malformed_dto`'s inline `subprocess.run(...)` was folded to the shared `_cli(env, "commands.py", ...)` form (`client.py:199-202` → :199-202 area) — `harness/client.py:65-68`'s `_cli` is the identical invocation (same interpreter, same script path, same arg list, `capture_output=True, text=True`, `timeout=300` → `t=300`, same `env`), i.e. **semantically identical, no behavioral change**. No pre-existing condition was semantically altered. (Note: the 2c80753 commit message says the touched bodies were restored "byte-identical" — the malformed_dto fold is semantically-identical rather than byte-identical; a wording nit on the commit message, not a code defect.)

### 8. The merge-gate criteria — all five green at the exact final head

- **CI at `83091c4`** (confirmed via the API, check-runs at the commit): `harness` success, `harness-trusted` success, `canonical-layer` success, `harness-suites` success, `head-tools` success; `CodeRabbit` skipped (the sub-10-star rule). All completed.
- **sev.json**: the findings list contains ONLY `F-079-4`/`F-079-5`/`F-079-6`/`F-079-7` (P2, owner-accepted-debt) and `F-079-8` (P2, resolved) — **zero P0/P1, zero open P0/P1**. The round-1 P1 (the dropped-registry gap) is closed per sev-round-2.md §F-079-3 (CLOSED, with the live closure claims).
- **validate_report**: `python3 harness/sev.py claim-079-p4f-recovery-contract-gate origin/main` re-run LIVE at HEAD during this review: **GREEN — the SEV report validates**.
- **The digest bound LAST**: `reviewed_diff_sha256` = `2f003076bfc482eb...` rides in sev.json at HEAD; the final commit `83091c4` (15:48:36) is the head and its stat touches ONLY `proofsheet.md`, `run-21/22/23.json`, and `sev.json` (the 2-line re-bind) — no source after the bind, no commits after the head.
- **The measured set**: runs 17-23 recorded (`48a2d64` and `83091c4`); run-23 (`make verify`, exit 0, at the compacted tree `2c80753`) and the proof sheet header says "run records: 23" with 23 `run-*.json` files present.

### 9. The two round-1 P3s — the route-not-block assessments VERIFIED

- **The anchor-ref registry gap (round-1 FINDING 2)**: live-probed at HEAD — a note @-ref to an anchor of a ledgered source still refuses the restore (`restore=1`, ARV-NTE-003 on the referenced anchor). Live-probed AGAINST an extracted `origin/main` tree (`PROBE_REPO=/tmp/basecheck`) — **it fails identically at base**, and the source/anchor/work branch of `_drop_purged` is byte-identical between base and HEAD. Pre-existing at base, not this slice's regression → the round-1 routing (note, not merge blocker) is CORRECT.
- **run-16's commit field off-by-one (round-1 FINDING 3)**: confirmed — `run-16.json` names `82be251` (11:57:23) but was recorded at 12:04:48 when HEAD was `0e1add3` ("run 16 recorded at the final tree"). Metadata only; the output-digest chain is unaffected (the RCW digest `74e8964d…` is byte-identical across runs), and the FINAL measured set (runs 21-23) is recorded at the correct trees (run-23 names `2c80753`, where it actually executed). The hygiene debt is superseded by the re-measured set.

---

## FINDINGS

**FINDING 1 (P3, OPEN, pre-existing at base — routes as a note per the slice's protocol, NOT a merge blocker) — the anchor-ref registry gap, confirmed live at HEAD AND at origin/main.**

A `note_reference` of kind `anchor` pointing at an anchor of a ledgered source survives the reconciliation (the anchors drop at `export.py:192` but never register in `dropped["anchor"]` in the source branch) and refuses the whole restore at ARV-NTE-003. Live probe at HEAD: `restore=1` ("the referenced anchor ... does not exist in the caller's scope"). The SAME probe against the extracted `origin/main` tree fails identically, and the owning code branch is unchanged by this slice — pre-existing at base, exactly as round-1 assessed. The round-1 suggestion that the P1 repair "close both halves in one increment" was not taken; that is a protocol-permissible routing (P3 pre-existing = note), and the gap remains a candidate for a future bounded increment (a one-line `dropped["anchor"] |= anchors` in the source branch plus its pin).

**FINDING 2 (P3, OPEN, pre-existing at base — noted, NEW observation not in round 1) — the ledgered-WORK shape: sources under a ledgered work are neither dropped nor registered, so the restore refuses at the source→work FK.**

A destination ledger row of kind `work` (admitted by 0013's CHECK) drops the work row (`export.py:181,193`) but leaves its sources in the archive's content — the insert then fails `source_work_id_owner_scope_fkey` (live probe at HEAD: `restore=1`, "insert or update on table source violates foreign key constraint ... Key is not present in table work", the whole transaction rolled back). The owning branch (the work arm of the `_ENTITY` loop) is byte-identical between `origin/main` and HEAD — the same pre-existing class as FINDING 1 (the work branch extends `gone` with the bound source ids at :181 but never drops or registers them as sources). Fail-closed (no partial state, no silent loss); pre-existing at base; routes as a note per the slice's protocol. Code-identity verified via the three-way diff; live-probed at HEAD (the base-tree live run was time-boxed out — the branch's byte-identity is the pre-existence evidence).

**FINDING 3 (P3, OPEN, record hygiene — confirmed as round 1 filed it) — `run-16.json`'s `commit` field off-by-one.**

`run-16.json` names `82be251` while the record was minted at 12:04:48 with HEAD at `0e1add3`. Metadata only; the digest chain and the final measured set are unaffected (see VERIFIED #9). Superseded in practice by runs 17-23 being recorded at their true trees.

No P0 or P1 findings. The round-1 P1 is repaired at its owning site (`harness/export.py:206-223`), pinned non-vacuously (`harness/client.py:540-566` + `harness/tests/test_recovery_contract.py:179-225`), and live-verified passing by this review's independent probe.

---

## VERDICT

**APPROVE-MERGE.**

The round-1 P1 is genuinely and completely repaired at its owning site: every cascade-dropped id — the ledgered `journal_block`/`reading_list` drops and the ledgered-source cascade's `journal_block`/`reading_list_member`/`reading_session`/`extraction_generation`/`reading_position` — now REGISTERS in `dropped` BEFORE the F3 `note_reference` filter (which is now the function's last statement, `export.py:221-223`), and my ref_kind walk over all seven kinds finds no unregistered path on any surface this slice touched (the two remaining unregistered paths — anchors under a ledgered source, sources under a ledgered work — are byte-identical pre-existing code at origin/main, live-confirmed for the anchor half, and route as P3 notes per the slice's own protocol, exactly as round 1 assessed). The pin is real and mechanically discriminating: the suite's substrate hand writes the ledger row (client.py stays clean — RCW-07's scan re-executed, zero matches), the conjunction requires `restore_exit == 0` AND `dangling_refs == 0` over the refs array that `query.py`'s NOTE_SQL genuinely populates with the ref_id, and my standalone live probe of the exact round-1 failing shape passes (restore exit 0, zero dangling refs). The process spine holds at the final head: CI five-for-five green at `83091c4` (CodeRabbit skipped per rule), sev.json carries zero P0/P1 (only P2 owner-accepted-debt and one resolved), validate_report GREEN re-run live, the digest `2f003076` is bound in the final commit which touches no source after the bind, the size arithmetic recomputes at exactly 400 non-test .py lines, and no pre-existing CLAIM-069 body was semantically altered (one behavior-preserving `_cli` fold, one blank line). The remaining P3s are pre-existing-at-base or record-hygiene notes that the protocol routes below the merge bar; a wrong BLOCK here would hold a repaired, pinned, measured, CI-green slice hostage to defects the base already carries.

---

## REVIEW SUMMARY (for the merge record)

The D-042 (1a) round-2 substantive re-review engaged the repaired tree at HEAD `83091c4`: the `_drop_purged` ordering repair was verified line-by-line (every cascade-dropped id registers in `dropped` BEFORE the F3 note_reference filter, now the function's last statement) with a full ref_kind walk over all seven kinds; the round-1 P1's exact failing shape was re-falsified live through an independent standalone probe and now PASSES (restore exit 0, zero dangling refs); the `condition_ledgered_source_restore` pin was read against `query.py`'s real refs shape and confirmed non-vacuous, with the ledger row riding the suite's substrate hand and RCW-07's privileged-path scan re-executed clean; the size arithmetic recomputes at exactly 400 non-test .py lines with no semantically altered CLAIM-069 body; and all five merge-gate criteria hold at the final head (CI green, sev.json zero open P0/P1, validate GREEN live, digest bound LAST). Three P3s route as notes per the slice's protocol — the anchor-ref registry gap and the newly-noted ledgered-work shape (both live-confirmed or code-identity-confirmed as pre-existing at origin/main), and the run-16 commit-field off-by-one. VERDICT: APPROVE-MERGE.
