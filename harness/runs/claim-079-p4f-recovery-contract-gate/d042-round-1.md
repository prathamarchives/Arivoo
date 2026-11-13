# D-042 (1a) MERGE-GATE REVIEW — PR #114, slice `claim-079-p4f-recovery-contract-gate` (CLAIM-079, P4-F)

- Reviewer: merge-gate host reviewer (D-042 1a, substantive; did NOT build this slice; read-only over the repo)
- Date: 2026-11-13
- Repo: `/home/z/my-project/Arivoo`, branch `slice/claim-079-p4f-recovery-contract-gate`
- Diff under review: `git diff origin/main..HEAD`, base = `d21ca44e` (merge-base confirmed; 25 commits, HEAD = `32b04e3`)
- Probe script (outside the repo): `/home/z/my-project/scripts/d042_probe_note_ref_cascade.py`

---

## VERIFIED

Everything below was checked against the real tree at HEAD `32b04e3` (read-only; no repo file modified).

### The diff, read in full

1. `harness/export.py` (+39 src lines) — the widened `TABLES` (19 tables), the `_ENTITY` widening, and the F-079-3 reconciliation-cascade repair, read line-by-line against the migrations they must satisfy.
2. `harness/client.py` (+358/-3) — all six P4-F conditions (`condition_recovery_walk` client.py:326, `condition_export_restore` :390, `condition_rebuild_parity` :518, `condition_phase_isolation` :535, `condition_prior_state_migration` :562, `condition_sync_conflict` :613) plus the `_ids_of`/`_page_ids` helpers; the compacted docstring→RCW-pointer forms; the token-extraction rewrite at client.py:476.
3. `harness/tests/test_recovery_contract.py` (NEW, 310 lines) — all eight pins RCW-01..08 read against their check prose; the machinery-absent RED probe at suite lines 91-106.
4. `harness/tests/test_export.py` — the widened TABLES tuple + `_TSV` forms + EXP-01 prose.
5. `harness/gate.py` (+3) — the RCW suite's TESTS registration (the ARV-RED-008 class, diff-visible).
6. `harness/red-records.json` — the new RCW binding (commit `4eb4944`, binding sha `ea570a0e…`) + three typed amendments; digests spot-checked.
7. `sev.json` + `sev-round-1.md` + `sev-round-2.md` + `notverified.txt` + `proofsheet.md` + run records 01-16, read in full.

### The export machine's ordering law — HOLDS

- `extraction_generation` (export.py:72) after `source` (:71) and before every FK-naming table — correct.
- `reading_position` (export.py:73) after BOTH its FK targets per 0014 (:60-61: `source` + `extraction_generation`) — correct.
- `journal_block` (export.py:81) and `reading_list` (:82) BEFORE `note_reference` (:83) — the F-079-1 repair; correct per 0018's `enforce_note_reference_guard` (insert-time existence check, ARV-NTE-003).
- `reading_list_member` (:84) after `reading_list` + `source` (0017:74-75); `reading_session` (:85) after `source` + `extraction_generation` (0015:60-61) — correct.

### The dropped-set keying — the F-079-3 repair itself is correct, but INCOMPLETE (see FINDING 1)

- The cascade now keys on `dropped.get("source")` (export.py:214), never re-reading the drained `rows["source"]` — the round-1 dead-code defect is genuinely repaired.
- Dropping `reading_position` when its ledgered source is dropped is CORRECT per 0014's FK `(source_id, owner_scope) REFERENCES arv.source` — the row cannot survive its source.
- The ledgered `journal_block`/`reading_list` branch (export.py:208-213) is UNREACHABLE at this substrate: 0013's `purge_ledger_kind_check` admits only `('work','source','anchor','highlight','bookmark','note')` (0013:20). Disclosed in the code comment (:204-207) and round-2 LIMITS #5 — honest forward-speculative code, P3-class only.

### The client conditions — no behavioral regression found from the compaction folds

- The RCW suite re-run LIVE at HEAD during this review: **PASS RCW-01..08, exit 0** (output at `/tmp/d042-rcw-live.txt`), digest-class identical to the recorded runs (`74e8964d…` family).
- The token-extraction rewrite (client.py:476: `ln.split("token" + "=")[1].split()[0]`) — semantics identical to the literal form; the RCW-02 `credentials_absent` pin (manifest table-set + token-value absence) is GREEN live. The isolation-checker collision repair is behavior-preserving as claimed.
- The families dict pairing (client.py:372-382), the no-oracle lambda (:546-551), the prior-state corpus write (:576-578), the `_reads` lambda table (:438-466, late-binding-correct) — all read; no vacuous-true or dead branch introduced beyond the known F-079-4/5 classes.
- RCW-07's mechanical scan re-executed at HEAD: zero matches for `psql|arv_app|arv_read|INSERT INTO|SELECT ` in client.py.

### The size law — exactly 400

`harness/scope.py`'s own `diff_stats('origin/main')` recomputed live: client.py 358 + export.py 39 + gate.py 3 = **400 source lines** — the ARV-SIZE-002 claim is exact, and the "counter-productive helper rewrites reverted" account (commit `e6202f5`) matches the tree (CLAIM-069's helpers are unmodified in this diff).

### The digest bound LAST — HOLDS

- Commit `41f7191` (12:11:43) re-bound `reviewed_diff_sha256` to `40cdbb9d…`; the final commit `32b04e3` (12:19:07) touches only `proofsheet.md` (outside the digest's changed-components surface).
- `python3 harness/sev.py claim-079-p4f-recovery-contract-gate origin/main` re-run LIVE at HEAD: **GREEN** (validate_report passes; the digest recomputes exact at the final head).

### The two-round SEV account — coherent where checked

- Round 1 (BLOCKED, three P1s) and round 2 (PASS) read in full; the repair commit `09191bd` matches the round-1 findings' owning sites (TABLES reorder; reading_position + the position read arm; the dropped-set cascade); the round-2 closure claims match the code at HEAD in every particular I re-derived.
- `notverified.txt` is an honest limits list (rig class, single crash arm, read-set scope, token-not-in-blobs, no concurrency claims, RLS-at-CLI-bound) — it covers the real limits, with one exception: it does NOT cover the reconciliation/reference-cascade gap below.

---

## FINDINGS

**FINDING 1 (P1, OPEN, live-falsified at HEAD) — the F-079-3 source-cascade drops bound `journal_block` rows without registering them in the `dropped` registry, so a note @-referencing such a block survives the reconciliation and refuses the WHOLE restore.**

`harness/export.py:214-218` drops every `journal_block` (and `reading_list_member`, `reading_session`, `extraction_generation`, `reading_position`) bound to a ledgered source — but the `note_reference` cascade at export.py:201-203 keys only on the `dropped` registry, and the source-cascade never adds the dropped journal_block ids to `dropped["journal_block"]` (only the unreachable ledgered-journal_block first loop populates that key, via `_ENTITY` at export.py:175-176). A `note_reference` row of kind `journal_block` pointing at a source-bound block therefore survives the reconciliation; at insert time the journal_block row is absent and 0018's guard fires.

Live proof (fresh scratch rig, real CLIs only; probe at `/home/z/my-project/scripts/d042_probe_note_ref_cascade.py`):

```
import_source                      -> exit 0
journal_block --kind creative --source-id <sid>  -> exit 0 (a BOUND block, legal per 0016)
create_note --ref journal_block:<id>@1           -> exit 0 (legal per 0018's CHECK)
export --owner A                   -> exit 0, tables=19 rows=11
destination ledger: kind='source', entity=<sid>  -> inserted (legal per 0013's CHECK; EXP-07's own substrate class)
restore --archive ...              -> exit 1:
  FAIL ARV-EXP-007: ... ERROR: ARV-NTE-003: the referenced journal_block
  (01a1d4f1-3926-720b-a3ca-bcaedfbb5fb2, 1) does not exist in the caller's scope
```

This is the same observable class round 1 classified as P1 (F-079-1: "the restore is impossible for any owner whose notes reference journal blocks") — here reached through the purge-reconciliation path the F-079-3 repair itself opened. It is in-slice on both halves: `journal_block` export and the source-cascade drop of bound journal_blocks are both this slice's additions (commit `09191bd`). The suites cannot see it: the RCW-02 walk's journal-ref note points at a SOURCELESS block (client.py:415-424 — no `--source-id` on `r_j1`), and no pin anywhere combines a ledger entry with a journal-block-ref note — a fresh instance of the round-1 F-079-2 "pin passes with the feature broken" class. The failure is fail-closed (no silent loss, no partial state) — but SYS-10's restore is impossible for the shape, and the sev.json claim "zero open P0/P1" is falsified at HEAD. Repair is small: register the source-cascade-dropped journal_block ids in `dropped["journal_block"]` (or equivalently extend the note_reference cascade to drop refs whose target row was removed by the source-cascade), plus a pin covering the failing shape (a ledgered source + a note referencing a block bound to it).

**FINDING 2 (P3, OPEN, pre-existing at base — noted, not blocking on its own) — the same dropped-registry gap for `anchor`-kind references.**

The ledgered-source branch computes and drops the bound anchors (export.py:185-192) but never adds them to `dropped["anchor"]` — so a `note_reference` of kind `anchor` pointing at an anchor of a ledgered source has the same survive-then-refuse shape. This code is unchanged from `origin/main` (verified against the pre-slice `_drop_purged`), so it is not this slice's regression — but the FINDING 1 repair should close both halves of the same pattern (anchors and journal_blocks) in one increment. Code-verified; not separately live-probed (time-boxed).

**FINDING 3 (P3, OPEN, record hygiene) — `run-16.json`'s `commit` field names `82be251` while the record was minted at 12:04:48 with HEAD at `0e1add3` (whose own message says "run 16 recorded at the final tree").**

The output digest chain is unaffected (the RCW output digest `74e8964d…` is byte-identical across runs 01-16 and this review's live re-run), so this is a metadata off-by-one in the run record, not an evidential break. Worth correcting when FINDING 1's repair re-records its runs.

No other new defects found: the six conditions' compacted forms, the token-extraction rewrite, the TABLES ordering, the reading_position drop-on-ledgered-source (correct per 0014's FK), the unreachable ledgered-journal_block branch (disclosed), and the digest-bound-LAST all check out at HEAD.

---

## VERDICT

**BLOCK-MERGE.**

The process spine of this slice is real and strong — the LAW-11 RED chain, the disclosed typed amendments, the exactly-400 size arithmetic, the digest bound LAST (validate GREEN re-run live at the final head), the RCW suite GREEN (re-run live during this review), and a two-round SEV chain whose round-1 P1s were genuinely repaired at their owning sites. But the merge-gate's own criterion — zero open P0/P1 — is falsified at HEAD by a live probe: the F-079-3 repair's source-cascade drops bound journal_block rows without extending the reference cascade, so the exact archive shape round 1 declared fixed (a note @-referencing a journal block) again refuses the whole restore, now through the ledger path, with no pin in either suite able to see it. The repair is a few lines plus one pin; land it (closing the pre-existing anchor half of the same pattern in the same increment), re-run the two-round verification, re-bind the digest, and re-present. A wrong APPROVE here would merge a P1 the slice's own SEV bar forbids.

---

## REVIEW SUMMARY (for the merge record)

The D-042 (1a) substantive review engaged the full diff at HEAD `32b04e3`: the TABLES ordering law, the dropped-set cascade, the six P4-F conditions' compacted forms, the RCW-01..08 pins, and the two-round SEV account were each verified against the code, with the RCW suite and the SEV digest validation re-run live (both GREEN) and the 400-line size claim recomputed exact. One new P1 was live-falsified: the F-079-3 source-cascade drops journal_block rows bound to a ledgered source without registering them in the dropped registry, so a note @-referencing such a block survives the reconciliation and refuses the whole restore (ARV-NTE-003 under ARV-EXP-007) — the round-1 F-079-1 observable class reborn through the repair's own path, uncovered by any pin. VERDICT: BLOCK-MERGE pending that repair (plus its pin, the pre-existing anchor half of the same pattern, and the run-record re-bind).
