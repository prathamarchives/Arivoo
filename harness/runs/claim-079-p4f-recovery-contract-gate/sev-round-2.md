# SEV ROUND-2 RE-VERIFICATION — slice `claim-079-p4f-recovery-contract-gate` (CLAIM-079, P4-F)

- Reviewer: the independent SEV grader (round 2 — the re-verification after repairs; same reviewer identity as round 1, fresh context re-reading everything live)
- Date: 2026-11-13
- Repo: `/home/z/my-project/Arivoo`, branch `slice/claim-079-p4f-recovery-contract-gate`
- Round-1 report: `/home/z/my-project/Arivoo/harness/runs/claim-079-p4f-recovery-contract-gate/sev-round-1.md` (read first; verdict BLOCKED, three P1s + five riders)
- Round-1 HEAD was `f901c7f`; current HEAD is `f80efec`, two commits added since:
  - `09191bd` — the repairs for F-079-1/2/3 (diff read in full: `harness/export.py` +23/−12, `harness/client.py` +27/−2, `harness/tests/test_export.py` +12/−5, `harness/red-records.json` +6/−1)
  - `f80efec` — the round-1 report preserved at the run dir (evidence only, no code)
- Working tree at review time: clean except the two pre-existing untracked drafts (`notverified.txt`, `proofsheet.md`); **no repo file was modified by this round** (verified `git status` before and after; probe scripts live outside the repo at `/home/z/my-project/scripts/`).

---

## VERIFIED

Everything below was observed live against the real repo at HEAD `f80efec` (commands + exact outcomes). The three P1 closures were each verified with a **fresh scratch rig built the way the suite builds one** (`harness/adapters/pg.py create_scratch_db` + `harness/migrate.py` via `ARV` env, real CLIs only: `commands.py` / `query.py` / `extract.py` / `export.py`), not by trusting the suite's own green.

### F-079-1 (P1, round 1) — TABLES insert-order defect: **CLOSED**

Claimed repair: `journal_block` + `reading_list` now insert BEFORE `note_reference` in `export.py` TABLES; the RCW-02 walk writes a note with `--ref journal_block:<id>@1` so the round-trip pin covers the failing shape.

Code state at HEAD (`harness/export.py:88–91`): the dict order is now `…note, note_lifecycle, journal_block, reading_list, note_reference, reading_list_member…` — `note_reference` (line 91) after `journal_block` (line 89) and `reading_list` (line 90), with the F-079-1 comment at line 88. Restore iterates `for t in TABLES` in dict order (`export.py:326`), so the referenced journal-block row exists at note_reference INSERT time (0018's ARV-NTE-003 guard satisfied).

Live probe (`python3 /home/z/my-project/scripts/sev2_f079_1_journal_ref.py`, scratch DBs `sev2f1*`, fresh migrated source + destination):

```
journal_block --kind raw                      → exit 0, result_ref=01a1d46f-8d58-…@1
create_note --ref journal_block:<id>@1        → exit 0, ACK status=committed … durability_rung=local_durable
export --owner A                              → exit 0, "EXPORTED … tables=19 rows=7"
restore --archive … (clean migrated dst)      → exit 0, "RESTORED … tables=19 rows=7 state_hash_match=true state=restored"
post-restore get-note                         → exit 0, content "The journal-ref note.", refs[0].kind=journal_bl[ock]
post-restore get-journal                      → exit 0, content "The referenced journal block."
post-restore resolve-reference journal_block:…@1 → exit 0, state=current, revision=1
```

Round 1 observed this exact shape refusing the whole archive (`exit 1`, `ARV-EXP-007 … ARV-NTE-003: the referenced journal_block … does not exist`). At HEAD it restores and reads back — the defect is closed. The RCW-02 pin genuinely covers the shape: `condition_export_restore` writes `r_n2 = create_note … --ref journal_block:{j1}@1` (`harness/client.py:428–432`) and folds `r_n2` into `walk_complete` (`client.py:443–444`); **pin-strength proof below** shows the widened pin goes RED against the pre-repair machine.

### F-079-2 (P1, round 1) — reading_position not exported: **CLOSED**

Claimed repair: `reading_position` added to TABLES after `extraction_generation`; the condition's read set gains a position arm with the reader's runtime fields (`current_generation_id`, `generation_matches`) normalized out, pinning the authored row's `save_ordinal`/`start_off`/`end_off`/`saved_generation` binding.

Code state at HEAD: `harness/export.py:80` — `"reading_position": "id,owner_scope,source_id,save_ordinal,generation_id,start_off,end_off,actor,run_id,input_hash,idempotency_key,created_at"` placed directly after `extraction_generation` (line 78), i.e. after both its FK targets (source line 76, generation line 78). The owning export suite's TABLES tuple and `_TSV` gained `reading_position` (`test_export.py:160–181`) with the per-table TSV form ordered by `source_id, save_ordinal`.

Live probe (`python3 /home/z/my-project/scripts/sev2_f079_2_position.py`, scratch DBs `sev2f2*`):

```
import_source + extract                      → exit 0 both
save_position --start 2 --end 9              → exit 0, ACK … save=1
pre-export  get-position → {"state": "saved", "save_ordinal": 1, "start_off": 2, "end_off": 9,
                            "saved_generation_id": "01a1d470-0afe-…", "current_generation_id": …,
                            "generation_matches": true, …}
export                                        → exit 0, tables=19 rows=8; manifest carries
                                                reading_position (1 row, full authored shape incl.
                                                save_ordinal + generation_id)
restore (clean dst)                           → exit 0, "RESTORED … tables=19 rows=8 state_hash_match=true"
post-restore get-position → {"state": "saved", "save_ordinal": 1, "start_off": 2, "end_off": 9,
                              "saved_generation_id": "01a1d470-0afe-…", …}
authored-field compare (state/save_ordinal/start_off/end_off/saved_generation_id): EQUAL
full-JSON compare (probe does NOT re-extract at dst, so runtime fields too): EQUAL
```

Round 1 observed `post-restore get-position → {"state": "no_position_saved"}` while the restore declared success. At HEAD the authored family round-trips — closed. The runtime-field normalization in the suite's position arm (`client.py:462–479`) is a legitimate scoping decision, and it is conservative in the right direction: my probe (no destination re-extraction) shows even the raw full row matches byte-for-byte; the walk itself re-extracts at the destination (`client.py:515–518`), which legitimately advances `current_generation_id`, so pinning the authored binding and normalizing the live view is the honest form, not a weakening — the fields that made the family "authored, never rebuildable" (save_ordinal, offsets, saved_generation) are the ones pinned.

### F-079-3 (P1, round 1) — dead source-cascade: **CLOSED**

Claimed repair: the cascade keys on the already-computed `dropped["source"]` set (never the re-read of the drained `rows["source"]`); the bound cascade extended to `reading_position`.

Code state at HEAD (`harness/export.py:227–231`):

```python
gone_sources = dropped.get("source", set())
if gone_sources:
    for t in ("journal_block", "reading_list_member", "reading_session",
              "extraction_generation", "reading_position"):
        drop(t, "source_id", gone_sources)
```

The round-1 dead form (`{r["id"] for r in rows.get("source", []) …}` — always empty because `drop(kind, "id", gone)` at line 201 already drained those rows) is gone; the cascade now consumes the `dropped` registry computed before the drain.

Live probe (`python3 /home/z/my-project/scripts/sev2_f079_3_source_cascade.py`, scratch DBs `sev2f3*`) — the EXP-07-class scenario round 1 falsified, with every bound family present in the archive (manifest row counts: `extraction_generation:1, journal_block:1, reading_list:1, reading_list_member:1, reading_position:1, reading_session:1, source:1, work:1, outbox:6`), destination carrying the ledger entry `('A','source',<sid>)` (the same `arv_app` substrate insert EXP-07 uses):

```
restore → exit 0: RESTORED owner=A ledger_as_of=2026-11-13T10:25:43 … tables=19 rows=14
          state_hash_match=true state=restored derived_state=pending_rebuild
post-restore counts (arv_read):
  source                    0   (dropped — ledger wins)
  extraction_generation     0   (dropped — the round-1 FK refusal is gone)
  reading_position          0   (dropped — the extended cascade fires)
  bound journal_block       0   (dropped — source_id FK binding)
  reading_session           0   (dropped)
  reading_list_member       0   (dropped)
  work                      1   (kept — EXP-07's own designed semantics, work_kept=="1";
                                  only a ledgered kind='work' drops the work row)
  reading_list              1   (kept — not ledgered)
  command_log               6   (kept — the audit trail is never purge material)
  purge_ledger (source row) 1   (kept — the destination's current entry, merged)
```

Round 1 observed this exact scenario refusing with `ARV-EXP-007 … extraction_generation_source_id_owner_scope_fkey … Key is not present in table "source"`. At HEAD the restore completes (no ARV-EXP-007 anywhere in the output) and every row bound to the ledgered source is dropped — the ledger wins, no resurrection, no dangling FK. Note on one probe iteration: my first run asserted `work == 0` and failed; that was **my probe's wrong expectation** (the owning suite pins `work_kept == "1"` at `test_export.py:384–389` — a source purge drops the tree BELOW the source; the work row survives unless ledgered as kind `work`, and `_drop_purged`'s work branch confirms the design). Corrected expectation, re-run, all checks OK. The forward-speculative half (ledgered `journal_block`/`reading_list` branch, `export.py:221–226`) remains unreachable at this substrate — re-confirmed live: a `kind='journal_block'` insert into `arv.purge_ledger` still dies on `purge_ledger_kind_check` — but it is now disclosed in the code comment as riding the ledger CHECK's own future widening, which is the honest disposition round 1 asked for ("either drop the unreachable branch or note it as forward-speculative").

### Pin-strength proof (the round-1 "pins that could pass with the feature broken" concern — answered mechanically)

`git archive f901c7f` into `/tmp/sev2-prerepair` (the pre-repair tree), HEAD's `harness/client.py` overlaid (only `export.py` differs — confirmed by `git diff --no-index --stat`: 23 insertions/12 deletions, exactly the repair), then `python3 /home/z/my-project/scripts/sev2_pin_strength.py` runs HEAD's **widened** `condition_export_restore` against the **pre-repair** export machine:

```
condition_export_restore dict:
  'walk_complete': True, 'export_exit': 0,
  'restore_exit': 1,                      ← the journal-block-ref refusal fires
  'journal_revisions': False,
  'post_restore_byte_equal': False,       ← the position loss / read failure bites
  'credentials_absent': True
RCW-02 pin at pre-repair machine: RED (pin bites)
```

The widened RCW-02 pin is therefore NOT vacuous: it mechanically discriminates the repaired machine from the broken one. Same construction demonstrated in the other direction by the suites below (green at HEAD).

### Suites re-run at HEAD `f80efec`

```
cd /home/z/my-project/Arivoo && source /home/z/my-project/pgbuild/env.sh
timeout 550 python3 harness/tests/test_recovery_contract.py
```
→ `PASS RCW-01` … `PASS RCW-08` (8/8) + `RECOVERY-CONTRACT SUITE GREEN — RCW-01..08 (…)`, **exit 0**. Output sha256 `74e8964da928ad5023ef5104c8d224d54713597f63e8a636da6d5417ebc77003` — byte-identical to the recorded runs 01–03 (the PASS lines' prose is unchanged by the repair; the behavior behind RCW-02 changed, as the pin-strength run proves, and RCW-02's own line is unchanged because it was already passing vacuously at round 1 and now passes honestly — the suite text is identical, the substance under it is not).

```
timeout 300 python3 harness/tests/test_export.py
```
→ `PASS EXP-01` … `PASS EXP-15` (15/15) + `GREEN — the P3-09 acceptance suite (EXP-01..15) passes`, **exit 0** (this suite's file was widened by the repair — `reading_position`/`extraction_generation` in TABLES + `_TSV` — and the red-record `current_sha256` `95b6624400e9…` recomputes byte-exact at HEAD; the RCW suite's digest `a5e64d5bc850…` also matches its record).

Sibling suites at HEAD (regression sweep over the export-widening surface — round 1 ran three; this round ran eight): `test_sync.py` exit 0 (SYN-01..23), `test_journal.py` exit 0 (JNL-01..06), `test_client_acceptance.py` exit 0 (CAC-01..09), `test_position.py` exit 0 (POS-01..06), `test_note_reference.py` exit 0 (NTR-01..16), `test_reading_list.py` exit 0 (RLS-01..06), `test_session.py` exit 0 (SES-01..06), `test_extract.py` exit 0 (EXT-01..17).

### Process spine of the repair commit (checked, not blocking)

- The repair's test changes ride a typed red-record amendment for `test_export.py` (prior `6384e4b1…` → new `95b6624400e9…`, observed 2026-11-13T10:14:45Z, note naming F-079-1/2/3 and both repairs); `test_recovery_contract.py` needed no amendment (unchanged by the repair — the widening lives in `client.py`, whose digest is not a red-record-bound file).
- The RCW-02 walk's new note (`--ref journal_block:<id>@1`) and the position arm are inside `client.py` (the condition functions), consistent with the slice's own contract that pins live at the suite and machinery at the driver.
- `walk_complete` now includes `r_n2` — the walk-refuses-if-the-journal-ref-note-refuses coupling is in place.

---

## REMAINING FINDINGS

None of the three P1s remain open. The round-1 P2/P3 riders carry forward as follows (all were classified P2/P3 at round 1; none is a live product defect):

| id | round-1 severity | status at round 2 | assessment |
|---|---|---|---|
| F-079-4 — RCW-08's observed-families gate has vacuous entries (`bookmark` observed via an empty `list-bookmarks` exit 0; the recovery walk still never writes a bookmark — re-confirmed at HEAD, `client.py:353` reads, no `create_bookmark` in `condition_recovery_walk`) | P2 | **open, accepted debt** | Acceptable for PASS. Pin-strength/process finding: the family IS covered content-level by RCW-02's walk (`create_bookmark` at `client.py:413` + the `bookmarks` read arm), so the underlying behavior is proven, just not by the arm the phase gate's letter names. No product defect; no false product claim rides it. Routed per the round-1 classification. |
| F-079-5 — RCW-01's pin weaker than its prose (result_ref identity + no-duplicate convergence not asserted) | P3 | **open, accepted debt** | Acceptable for PASS. The replay machinery itself is pinned by earlier suites; this is registry-letter debt, not a behavior gap. |
| F-079-6 — ARV-SIZE-002 commit prose "behavioral code untouched" inaccurate | P3 | **open, accepted debt (owner-accepted at round 1)** | Documentation accuracy only; the behavioral claim was verified then and re-verified now (RCW digest reproduced, suites green). |
| F-079-7 — rig provisioning (`create_scratch_db`) inside `harness/client.py` | P3 | **open, accepted debt (owner-accepted at round 1)** | Unchanged by the repair (the repair added one more `create_scratch_db` use in `condition_export_restore`, same class). Disclosed in `notverified.txt`; strictly rig lifecycle; every observation still rides the real CLIs. |
| F-079-8 — measured set lags the content head | P3 | **open — expected to close at the finalize** | Still true at round 2: runs 01–08 record only `09d60b0`/`89a5ba6`; no run record at `09191bd`/`f80efec`; `proofsheet.md` still binds `89a5ba6` and remains an untracked draft. This round's live runs (RCW exit 0 digest-verified, EXP exit 0, eight sibling suites exit 0) close the evidential gap for the review, but the finalize commit must mint the post-repair run records + re-bind the proof sheet at the final head per the repo's own anti-lag rule. Carried as a finalize-time obligation, not a blocker. |
| NEW (round 2, noted) — the recorded runs 01–03 predate the repair | observation | **non-finding** | The recorded RCW digests match HEAD's live output because the suite's printed prose did not change; the recorded runs at `09d60b0` therefore do NOT evidence the repaired behavior — only the post-repair live runs do (this round's). This is exactly the F-079-8 class: the finalize must re-record. No new severity. |

No P0/P1 remains open.

---

## VERDICT

**PASS.**

All three round-1 P1s are genuinely closed, each verified live on fresh scratch rigs with the exact failing shapes round 1 falsified: the journal-block note @-reference now restores and reads back (F-079-1); the authored reading position round-trips with `state=saved`, `save_ordinal`/`start_off`/`end_off`/`saved_generation` byte-equal across export/restore (F-079-2); the ledgered-source cascade completes the restore (no ARV-EXP-007 FK refusal) and drops every row bound to the purged source — `extraction_generation`, `reading_position`, bound `journal_block`, `reading_session`, `reading_list_member` — while the un-ledgered families and the audit trail survive (F-079-3). The repairs carry honest pins: the widened RCW-02 condition run against the pre-repair export machine goes RED (`restore_exit: 1`, `post_restore_byte_equal: False`), so the pins mechanically discriminate repaired from broken — the round-1 "vacuous pin" concern is answered by construction. Both owning suites are green at HEAD (`RCW-01..08` exit 0; `EXP-01..15` exit 0), red-record digests recompute byte-exact with the typed amendment minted, and eight sibling suites (sync, journal, client-acceptance, position, note-reference, reading-list, session, extract) are green — no regression from the export widening. The remaining riders are the round-1 P2/P3 pin-strength/process debt (F-079-4/5), owner-accepted documentation/rig-class debt (F-079-6/7), and the finalize-time obligation to re-bind the measured set at the post-repair head (F-079-8) — none is a live product defect, and PASS may not carry open P0/P1, of which there are none. The finalize commit should mint the post-repair run records and the re-bound proof sheet before the merge gate.

---

## REVIEW SUMMARY

Round 2 re-verified the three P1 falsifications from round 1 on fresh live rigs and found each genuinely closed by the repair commit `09191bd`: the TABLES reorder makes a note @-referencing a journal block restorable (previously the whole archive refused on ARV-NTE-003), `reading_position` now rides the authoritative export and round-trips byte-equal on its authored fields, and the source-cascade keys on the computed dropped set so a ledgered source's restore completes and drops every bound row (extraction_generation, reading_position, bound journal block, sessions, list membership) instead of refusing on the FK. The widened RCW-02 pin was proven non-vacuous by running HEAD's condition against the pre-repair export machine (RED: restore_exit 1), and both owning suites (RCW-01..08, EXP-01..15) plus eight sibling suites are green at HEAD with the red-record digests recompute-exact and a typed amendment minted for the widened export suite. The open riders are only the round-1 P2/P3 accepted debt (RCW-08's vacuous bookmark entry, RCW-01 pin strength, commit-prose accuracy, rig-in-client class) and the finalize-time obligation to re-record the measured runs at the post-repair head — no P0/P1 remains. VERDICT: PASS.

---

## INT TRACE (unchanged from round 1)

INT-127/131/140/143/144/145/146 (the P4-A..F chain and the standing merge authorization), INT-125/INT-122 (the per-slice SEV requirement this round discharges). SYS-10 (PLAN.md:198) — the round-1 violations (restore-impossible reference kind, silent position loss, dead purge reconciliation) are each now observed repaired live. SYS-11 (PLAN.md:199) — this round closes the trace-closure refusal round 1 issued; the Phase 4 exit gate itself remains the merge-time obligation per record 71 §5.

## LIMITS

1. `make verify` in full was not re-run this round (the individual suites named above were; the recorded run-05 verify exit 0 binds `89a5ba6`, pre-repair — re-verification rides the finalize).
2. No PR exists yet; the merge-gate chain is pending (as at round 1).
3. The remaining ~25 sibling suites in gate.py's TESTS tuple beyond the eight run here were not re-run.
4. The token-not-in-blobs bound is unchanged (the never-ride proof sweeps the manifest only — the slice's own disclosed limit).
5. F-079-3's ledgered `journal_block`/`reading_list` branch remains unreachable at this substrate (purge_ledger CHECK re-confirmed live) — disclosed forward-speculative code, not dead-by-mistake.
