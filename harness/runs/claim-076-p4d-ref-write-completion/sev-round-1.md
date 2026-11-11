# CLAIM-076 — SEV round 1 (the adversarial fresh-context verification)

- **Agent:** independent fresh-context SEV reviewer (Task SEV-076-R1; not the slice author)
- **Date:** 2026-11-11T13:07:51Z
- **Round:** 1
- **Base:** `af95e3c0` (origin/main, the PR #110 merge)
- **Head:** `b50f5d98` (`slice/claim-076-p4d-ref-write-completion`, the GREEN)
- **Chain (base → head), verified from git (parents checked with `rev-parse <c>^`):** `af95e3c0` base → `5358426` commit A (the post-#110 reconciliation: CLAIM-075 LANDED / record 67 closed, CLAIM-076 opened, record 68 minted — docs-only, verified: exactly AGENTS.md, CLAIMS.md, PLAN.md, STATE.md, context/WORKLOG.md, records 67+68, scope.txt) → `0537873` **the RED** (LAW-11, tests-only: exactly test_note_reference.py NTR-13..16 + test_sync.py SYN-23) → `bd58f08` the typed red-record binding (red-records.json + red-01.txt + red-02.txt) → `ee6988b` the typed pre-GREEN suite amendment (NTR-16's layer-attribution correction + row-count strengtheners — assertions only grew) → `b50f5d9` **the GREEN** (exactly migration 0018 + commands.py + sync.py + capability.py).
- **Method:** 94 live probes on my own scratch rigs (script at `/home/z/my-project/scripts/sev76r1_probe.py`, log at `sev76r1-log.txt` — three rigs: one single-DB `sev76r1a`, two two-DB sync rigs `sev76r1loc/srv` and `sev76r1loc2/srv2`, all created via `pg.create_scratch_db` and dropped at exit; audits through the independent `arv_read` role, hostile writes through `arv_app`) + 13 static/git checks; the NTR and SYN suites run once by me independently. Two of my own probe assertions were over-strict (see §2.3's method note on the no-oracle normalization) and were re-derived as supplementary probes in the same run — the log is the single run of record, the failed first attempts kept visible.

## §1 Verdict

**PASS** — zero open P0/P1. Every claim in the slice's contract reproduced live on my own rigs: the seven-kind write round-trip commits and renders, the stored new-kind refs resolve through the untouched read arm (historical with `pinned_revision`+`current_revision` when superseded, current when current), the shape law and the no-oracle hold at the widened boundary with zero effect, the 0018 substrate widens exactly the two named kinds with the guard routing proven by admission (not prose), the two-DB sync delivers through the identity bridge with the journal stem step producing the uuid stem (never a double-pin) and the not-yet-durable note resting retryable with the named ARV-SYN-009, and the RED chain is honest (both REDs reproduced at `0537873` via a detached git worktree; the binding digests match the files at HEAD). I found four hostile-input classes at the write boundary — all four are the CLAIM-057 substrate's own pre-existing grammar laws (the `int()` oversize-pin traceback, the `$`-anchored uuid regex, the isdigit/leading-zero normalization, the 008 message wording) which this slice composed verbatim per the "never a second implementation" doctrine, extending their reach to the two new kinds; all are fail-closed with zero writes, all are the exact commands.py twins of the classes CLAIM-075's SEV round 1 repaired in query.py and routed at commands.py (F-075-1/2/3). They are dispositioned here as routed findings (F-076-1 the P2 routed, F-076-2/3/4 the P3s routed), not defects opened by this diff.

## §2 The live verification

### §2.0 The suites, run by me independently at HEAD `b50f5d9`

- `python3 harness/tests/test_note_reference.py` → **GREEN — the P3-06 acceptance suite, slice two (NTR-01..16) passes, exit 0** (my captured output's sha256 exactly equals the digests recorded in the slice's run-01/02/03.json — the recorded runs are honest and the suite deterministic).
- `python3 harness/tests/test_sync.py` → **GREEN — the P3-08 acceptance suite (SYN-01..23) passes, exit 0**.

### §2.1 Claim 1 — the seven-kind write round-trip (P010–P020)

Fixture: import (work+source), bookmark created then moved (max rev 2), journal_block created then revised twice (max rev 3), highlight rev 1, a target note. The seven-kind create:

```
[P012] ACK command=create_note idem_key=sev-nt1 status=committed result_ref=01a1cab5-186a-… revision=1 durability_rung=local_durable api_version=1
[P013] rendered: [{"kind": "anchor", …, "revision": null}, {"kind": "bookmark", "id": "01a1cab5-15a7-…", "revision": 1},
                  {"kind": "highlight", …, "revision": 1}, {"kind": "journal_block", "id": "01a1cab5-1667-…", "revision": 2},
                  {"kind": "note", …, "revision": 1}, {"kind": "source", …, "revision": null}, {"kind": "work", …, "revision": null}]
[P015] the substrate holds exactly 7 rows for revision 1 (P014 shows the per-kind rows)
```

resolve-reference over the STORED new-kind refs (P016–P020):

```
bookmark@1 (superseded by rev 2): {"state": "historical", "pinned_revision": 1, "current_revision": 2, …}
bookmark@2 (current):             {"state": "current", "revision": 2, …}
journal_block@2 (superseded by 3):{"state": "historical", "pinned_revision": 2, "current_revision": 3, …}
journal_block@3 (current):        {"state": "current", "revision": 3, …}
bookmark (unpinned):              {"state": "current", "revision": 2, …}   # the read arm's optional pin, untouched
```

### §2.2 Claim 2 — the shape law at the widened boundary (P021–P028)

```
[P021] bare bookmark:<uuid>        → exit 1 FAIL ARV-NTE-006 … must name the target revision
[P022] bare journal_block:<uuid>   → exit 1 FAIL ARV-NTE-006
[P023] bookmark:<uuid>@x           → exit 1 FAIL ARV-NTE-006
[P024] bookmark:<id>@1 twice       → exit 1 FAIL ARV-NTE-008 … the reference set is a set
[P026] every shape refusal left ZERO note rows, ZERO reference rows, ZERO command_log rows (note 2->2 ref 7->7 cmd_log 12->12)
[P027] the SHUFFLED order under the same idem key → exit 0, status=replayed, SAME result_ref (LAW-23)
[P028] a DIFFERENT set under the same key → exit 1 FAIL ARV-CMD-409 … no silent overwrite
```

(P025 additionally shows the same kind:id at TWO revisions is also the 008 duplicate — the substrate's one-per-(kind,target) set law, unchanged from the old kinds.)

### §2.3 Claim 3 — the no-oracle for the new kinds (P029–P031, P033, P073–P076)

All six classes (absent bookmark/journal_block, owner-B's bookmark/journal_block, nonexistent revision on a live bookmark/journal_block) refuse exit 1 ARV-NTE-003 with zero note rows and zero command_log rows (P030: note 3->3, cmd_log 13->13). Byte-equality of stdout+stderr:

```
[P031] absent vs ANOTHER OWNER's bookmark:  BYTE-EQUAL after normalizing the asked uuid (309B == 309B)
[P033] absent vs ANOTHER OWNER's journal_block: BYTE-EQUAL
```

**Honest method note:** my first two byte-comparison probes (P032/P034) compared absent@**1** against nonexistent-revision@**99** normalizing only the uuid — they differ in exactly the echoed asked pair (`(<uuid>@1)` vs `(<uuid>@99)`), because the refusal framing-safely echoes the asked reference. The corrected comparisons, in the same run of record, prove the template equality: same-revision absent@99 vs live@99 byte-equal after uuid normalization (P073/P075), and pair-normalized absent vs live byte-equal (P074/P076). The no-oracle holds: the refusal text distinguishes nothing beyond the caller's own input echo. The read arm shows the same law (P072, P080: ARV-REF-001 byte-equal cross-owner vs absent, and live@99 vs absent@99).

### §2.4 Claim 4 — the 0018 substrate (P004–P009, P035–P046)

From `pg_constraint` on my fresh rig (P004/P005/P006): the kind CHECK admits **exactly** work/source/anchor/highlight/note/bookmark/journal_block; the shape CHECK puts bookmark/journal_block in the REVISIONED arm (`ref_revision IS NOT NULL AND >= 1`); the constraint NAMES `note_reference_ref_kind_check` / `note_reference_ref_shape_check` are unchanged (P007). Direct `arv_app` INSERTs:

```
[P035] kind='reading_list' + a REAL note target @1 → ERROR: new row … violates check constraint "note_reference_ref_kind_check"
       (passes the guard's ELSE arm — the note exists — and dies at the kind CHECK: the widening is exactly two kinds)
[P036] kind='reading_list' + a bookmark target     → guard's ARV-NTE-003 (the non-note target never passes the ELSE arm)
[P037] kind='bookmark' + NULL revision             → guard's ARV-NTE-003 ("the referenced bookmark (<uuid>, -)")
[P038] kind='journal_block' + NULL revision        → guard's ARV-NTE-003
[P039] every refused form: ZERO rows (9 -> 9)
[P040] WELL-FORMED bookmark (real uuid, rev 1)     → ADMITTED  — the guard routes bookmark -> arv.bookmark
       (had the note ELSE arm run, the bookmark uuid would have refused: the routing proven by acceptance)
[P041] WELL-FORMED journal_block (real block, rev 2) → ADMITTED
[P042] the two admitted rows land exactly-once (9 -> 11)
[P043] ghost bookmark target                       → guard's ARV-NTE-003
[P044/P045] owner-B's bookmark / journal_block     → guard's ARV-NTE-003
[P046] zero further rows (11 -> 11)
```

### §2.5 Claim 5 — the migration mechanics (P001–P003, P008/P009)

`migrate.py` exit 0 on the fresh rig with `applied 0018_note_ref_kinds` (P001); `--verify` clean over all 18 (P002). The file is constraint-only — statement heads are ALTER/ALTER/CREATE OR REPLACE FUNCTION only, zero data-statement hits (P003). The guard's per-kind chain read **from the DB** (`pg_proc.prosrc`): the `bookmark` arm (offset 1333) and `journal_block` arm (1579) precede the ELSE (1814), reading `arv.bookmark` / `arv.journal_block` at the pinned revision, owner-scoped (P008/P009).

### §2.6 Claim 6 — the sync delivery, two-DB rig (P081–P094)

Fixture: local import + bookmark + journal_block + note carrying `--ref bookmark:<id>@1 --ref journal_block:<id>@1`. The sabotage pass (a wrong ARV_BLOB_DIR makes the import row rest retryable, which cascades):

```
[P082] state=retryable reason=ARV-SYN-009: the referenced bookmark 01a1cab7-4b5c-… is not yet server-durable —
       the identity dependency (the creating command has no server answer; ordering resolves it on the next pass)
[P083] sr-imp=retryable | sr-bm=retryable | sr-jb=acknowledged | sr-nt=retryable   (never a wrong-id delivery)
[P085] recovery pass (correct blob dir): sr-imp/sr-bm/sr-jb/sr-nt ALL acknowledged
[P086] srv_bm=01a1cab7-4e71-…  srv_jb=01a1cab7-4cdb-…@1  srv_nt=01a1cab7-4efa-…   (ARV-SYN-008: server_refs present)
[P087] the server's journal ack IS the @1 ADDRESS form <uuid>@1
[P088] server get-note refs: [{"kind":"bookmark","id":"<SERVER bm>","revision":1},{"kind":"journal_block","id":"<SERVER jb stem>","revision":1}]
[P089] stem=01a1cab7-4cdb-… vs address=01a1cab7-4cdb-…@1 — the @1 ADDRESS reduced to its uuid stem, NEVER <id>@1@rev
[P090] server resolve-reference over the delivered bookmark: {"state":"current","kind":"bookmark","revision":1}
[P091] server resolve-reference over the delivered journal_block: {"state":"current","kind":"journal_block"}
[P092] no LOCAL uuid leaked into the server's note_reference rows (count 0)
[P093] a second pass touches nothing
[P094] reviewer's extension: a journal_block ref pinned @3 (block revised twice locally) delivers as <stem>@3 —
       all six rows acknowledged, the server renders its own stem at revision 3 (the stem step never mangles a non-@1 pin)
```

### §2.7 Claim 7 — the read arms unchanged (P047/P048, §3)

`git diff af95e3c0..HEAD -- harness/query.py` is **EMPTY** (P048, 0 bytes — also verified as a static check). get-note's refs aggregation is kind-agnostic, proven live: the DIRECTLY-inserted well-formed bookmark/journal_block rows (admitted at P040/P041 through the substrate, never through the note command) render through the ordinary read arm (P047).

### §2.8 Claim 8 — the RED chain, reproduced from the archived tree

`git worktree add /tmp/sev76red 0537873` (removed after):

```
python3 harness/tests/test_note_reference.py → exit 1
  FAIL ARV-TEST-000: the P4-D slice two write-completion machinery is absent
  (machinery-absent class; the note --ref vocabulary still refuses the bookmark kind …)
python3 harness/tests/test_sync.py → exit 1
  PASS SYN-01 … PASS SYN-22, FAIL SYN-23 … RED — the P3-08 sync suite fails: SYN-23
```

Both match `red-01.txt` / `red-02.txt` in the slice's runs dir byte-for-byte in substance. The NTR probe is DB-free as claimed (it exits on the parse refusal before any connection). Binding chain (static): `test_note_reference.py`'s original CLAIM-057 binding `1937d2af` retained; the latest amendment has `new_sha256 96ded73a…` = the file's actual sha256 at HEAD = the record's `current_sha256`; the two latest amendments name CLAIM-076's RED at 0537873 (with red-01/red-02 evidence) and the pre-GREEN NTR-16 layer-attribution repair. `test_sync.py`: binding `e91dc9a`, latest amendment = actual sha256 at HEAD, naming CLAIM-076's RED. `red-01.txt`/`red-02.txt` exist (committed at bd58f08); run-01..04.json present (the in-flight measured set).

### §2.9 Claim 10 — the adversarial battery (P049–P072, P077–P080)

Sixteen hostile forms devised by me. The grammar-owned forms — the 10k string, SQL metacharacters (`' OR '1'='1`), empty kind, uppercase kind (`BOOKMARK:`), double-at (`@1@2`, `@@1`), leading/trailing whitespace, `DROP TABLE arv.note;--@1` — ALL refuse exit 1 with the typed ARV-NTE-006 and zero tracebacks (P065), zero note/reference/command_log writes (P070/P071). Cross-owner isolation probed at BOTH boundaries (write P029–P033, substrate P044/P045, read arm P072). The command_log-unchanged law held across every refusal battery. Three characterized classes (see §4): the oversize all-digits pin (P063/P064/P069/P077 — untyped ValueError traceback, identical on the OLD kind highlight), the trailing-newline uuid (P060/P078 — typed ARV-CMD-010 at the session layer, identical on the old kind), and the unicode-digit/leading-zero/uppercase-hex normalizations (P066–P068/P079 — the substrate's isdigit law and UUID-column canonicalization).

## §3 The static/git verification

1. **Chain order** (§ header): parents verified; the RED precedes the GREEN; nothing implementation-shaped precedes the RED (commit A is docs-only — the eight files listed above).
2. **RED diff** = exactly the two test files (211+ / 61+ lines, tests-only). **GREEN diff** = exactly migration 0018 + commands.py + sync.py + capability.py (+124/−7). **Binding diff** = red-records.json + red-01.txt + red-02.txt. **Amendment diff** = test_note_reference.py + red-records.json, assertions only grew (the ovck probe + row counts; no assertion removed or weakened).
3. **Scope honesty:** every path in `git diff --name-status af95e3c0..HEAD` appears in the slice's scope.txt (the scope's larger allowed set — query.py/crash.py/gate.py — is untouched, permitted). Diff paths: the 4 implementation files, the 2 test files, red-records.json, the runs dir, and the six docs/record files, all in scope.
4. **`_REF_KINDS` vs the 0018 CHECK vocabulary:** programmatically compared — both exactly `work/source/anchor/highlight/note/bookmark/journal_block`, no drift between the two homes.
5. **The argparse `--ref` help** names the seven kinds (run live: "highlight/note/bookmark/journal_block MUST name the target revision, work/source/anchor MUST NOT").
6. **capability.py's references row** names slice two's write completion ("LANDED in P4-D slice one (CLAIM-075) + slice two (CLAIM-076 — the write completion) … the note --ref WRITE vocabulary over the same seven families … the sync delivery … the journal family's @1 address reduced to its uuid stem").
7. **query.py untouched** (empty diff base..HEAD).
8. **red-records.json binding chain** verified (§2.8): current digests match the files at HEAD for both suites; the amendment notes name this slice's RED and pre-GREEN repair; the amendment count and prior chaining intact.
9. **Migration 0018** carries the `-- arv-baseline-bump: 1` directive (ARV-MIG-003, the destructive DROP CONSTRAINT class) and the CREATE OR REPLACE guard (the procedural construct the admitted grammar cannot classify — the 0010 convention), verified by reading the file and by the clean apply on fresh rigs.
10. **Suite determinism cross-check:** my independent NTR run's output sha256 equals the recorded run-01/02/03 digests exactly.
11. The slice's run-04.json records `make verify` exit 0 at HEAD (not independently re-run by me — see §5).

## §4 Findings

- **F-076-1 — P2 — routed (open at the substrate grammar owner, NOT opened by this diff).** The all-digits oversize pin (≥4301 digits) crashes the note `--ref` parser with an untyped traceback instead of a typed refusal: live, `create_note --ref bookmark:<uuid>@` + `'1'*5000` → exit 1, stdout EMPTY, stderr `Traceback … ValueError: Exceeds the limit (4300 digits) for integer string conversion` (P063/P064/P069/P077); the identical crash reproduces on the OLD kind `highlight:<uuid>@` + 5000 digits — the class is pre-existing at the CLAIM-057 substrate (`commands.py _nte_refs` calls `int(rev)` after only `isdigit()`), which this slice composed verbatim by adding the two kinds to the same tuple (the "never a second implementation" doctrine). Fail-closed: zero note/reference/command_log writes (P070/P071). **Routing:** this is the exact commands.py twin of CLAIM-075's F-075-1 (repaired in query.py `_ref_parse` with the len>18 bound) left to the substrate grammar owner under F-075-3's routing; the repair belongs in the family-wide `_nte_refs` grammar slice (a pin-length bound before `int()`), never duplicated here.
- **F-076-2 — P3 — routed (the F-075-2 commands.py twin).** A trailing-newline uuid (`bookmark:<uuid>\n@1`) passes the substrate's `$`-anchored `_UUID_RE` and dies at the session-marker layer with the typed `ARV-CMD-010` ("session marker MARK:CHECK not observed — psql stalled") rather than the grammar's own ARV-NTE-006 malformed-id refusal; identical behavior on the old kind highlight (P060/P078); typed, fail-closed, zero rows. **Routing:** commands.py `_UUID_RE`'s `$` anchor — already routed at CLAIM-075's SEV round 1 to the `_nte_canon_id` pattern's family-wide slice (the F-072-1 precedent); the `\Z` re-anchor lands there.
- **F-076-3 — P3 — routed/owner-accepted-debt (the F-075-3/F-075-4 classes).** The substrate's isdigit/int normalization composes over the new kinds: `journal_block:<uuid>@٣` (arabic-indic THREE) stores revision **3** (P067), `bookmark:<uuid>@001` stores revision **1** (P068) — accepted-and-normalized rather than refused, the pre-existing substrate law routed to the grammar owner (narrowing it here would be the forbidden second implementation). The uppercase-hex uuid ask is canonicalized to lowercase by the substrate's UUID column — the stored/rendered id is canonical (P066/P079), i.e. the write boundary carries NO F-075-4-style echo debt (that class remains read-side only).
- **F-076-4 — P3 — routed (cosmetic, pre-existing substrate message).** The ARV-NTE-008 message says "one reference per target per revision" while the enforced law is one reference per (kind, target) regardless of revision — `bookmark:<id>@1` + `bookmark:<id>@2` also refuses 008 (P025), consistent with the old kinds' set semantics but slightly mis-worded. Pre-existing message text in `_nte_refs`, unchanged by this diff; routes with the substrate grammar owner.

No P0 (no data loss/corruption, no wrong answer served), no P1 (every claimed behavior reproduced; isolation held at both boundaries on both domains; no dead letter — the not-yet-durable case rests retryable with the named reason and recovers).

## §5 Honest limits

- I did **not** independently re-run `make verify` / the trusted gate (the slice's run-04.json records exit 0; my NTR-run output hash matching the recorded digests cross-checks the suite's determinism and the recorded runs' honesty, but not the gate's other 53 tests).
- The no-oracle byte-equality is **template** equality modulo the framing-safe echo of the asked (id, revision) pair; my run-of-record contains the two over-strict first-attempt probes (P032/P034) alongside their corrected re-derivations (P073–P076) — I chose to keep the failed first attempts visible in the log rather than hide my own probe-wording repairs.
- The oversize-pin and trailing-newline classes were probed on the `create_note` path; `revise_note`'s `--ref` shares the same `_nte_refs` parse by code reading, not by a separate live probe.
- Sync delivery was probed with journal pins @1 and @3 and a bookmark @1, single-owner, single-pass sequencing; concurrent sync passes, two-writer interleavings, and deeper revision ladders under sync were not devised (the standing no-concurrency limit of the prior SEV rounds).
- Migration 0018's failure/rollback path (ARV-MIG-009) was not deliberately fault-injected; I verified clean apply + verify on five fresh databases.
- The crash matrix (crash.py) around new-kind refs was not re-probed by me — NTR-10 covers refs generically and passed in my suite run; my probes covered the commit, refusal, substrate, and delivery paths.
- I verified `test_note_reference.py`/`test_sync.py` binding digests and the amendment chain, but did not re-derive the pre-CLAIM-076 amendment history of `test_sync.py` beyond reading the recorded notes.
