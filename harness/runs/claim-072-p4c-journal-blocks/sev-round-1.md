# SEV round-1 — CLAIM-072 / P4-C slice three (the journal/blocks surface — the writing lab)

- **Agent label:** agent-34277f24
- **Date:** 2026-11-09 (round 1, fresh context, adversarial)
- **Slice:** `slice/claim-072-p4c-journal-blocks` — the journal/blocks surface (source-optional raw/creative blocks, long raw thinking preserved losslessly, no forced short-note funnel)
- **Base:** `78b3654` (origin/main, CLAIM-071's merged head) — **Head at review:** `806ef04`
- **Chain (the ACTUAL git chain — ten commits; the review brief's nine-commit chain omits `966b5dc`, see F-072-5):**
  `78b3654` → `87ffe31` (commit A) → `f22d8d0` (RED) → `3a3dc13` (red record) → `8f1ae13` (suite strengtheners) → `4a35546` (GREEN) → `966b5dc` (typed red-record amendment) → `838b1e9` (SYN-20 RED) → `4baad8f` (red-02 evidence) → `806ef04` (SYN-20 GREEN)

## 1. Verdict

**PASS** — zero P0/P1/P2. All claimed surfaces verified live and green: the lossless long-form round-trip (byte-honest through write, read, revise, history, AND the sync delivery), the closed kind vocabulary, the source-OPTIONAL and no-forced-funnel laws, the serialized revisions with the SAME advisory lock on both the command and the 0016 guard (the F-071-3 spelling class fixed at this family — proven by a live blocking probe), the append-only/contiguity/bind guards refusing hostile psql by name, the owner isolation, and the SYN-20 delivery on the reviewer's own two-DB rig. The RED chain reproduces at every archived tree. Five P3 notes routed below.

## 2. Findings

- **F-072-1 (P3, routed): the read arms' malformed-id class answers ARV-QRY-002 ECHOING the asked
  bytes — the slice's "strongest no-oracle form" claim overstates.** `query.py:683-691`'s docstring
  and the GREEN commit message claim the journal refusal "names NO id … absent, another owner's,
  malformed — … nothing about the request echoes back". Observed live:
  `get-journal --id not-a-uuid-at-all` → `FAIL ARV-QRY-002: the read failed — ERROR: invalid input
  syntax for type uuid: "not-a-uuid-at-all"` (+ the SQL line fragment) — a DIFFERENT refusal line
  that echoes the request (query.py:305-316 `_read`'s failure path; the cast fires in
  `JNL_SQL`/`JNLHIST_SQL` before `_refuse_journal` is reached). `get-note` behaves byte-identically
  (verified live) — a pre-existing family-wide class, not introduced here. The no-oracle law PROPER
  (absent vs cross-owner, valid uuids, byte-equal ARV-QRY-001 — query.py:683) holds, verified live
  both read arms and the write path. Routing: either the docstring/claim narrows to valid-uuid ids,
  or the arms pre-validate the id shape; the class is shared with every landed read family.
- **F-072-2 (P3, routed): sync.py's bridge-clause safety comment is imprecise — "@1 rows are only
  ever CREATES" is false as stated; the clause is nonetheless outcome-neutral (probed live).**
  `sync.py:98` widens `_create_key` to `result_ref IN (id, id||'@1')`. But save_position and
  record_session FIRST ordinals also ack `<source>@1` (commands.py:1858, 1984) — so on a SOURCE
  translation the clause newly matches those rows, not only creates. Live probe (reviewer's two-DB
  rig, both rows genuinely `acknowledged`: `import_source → <sid>` and `save_position → <sid>@1`):
  `_create_key(sid)` returns the IMPORT's key — the create-class `ORDER BY … DESC` preference
  (sync.py:100-101) holds — and `_translate(sid)` returns the bare server uuid. The divergent corner
  (a source's import unacknowledged while a position/session row on it IS acknowledged) is
  unreachable through the driver by induction: that row's own delivery requires the translation it
  would poison. No reproduced defect; consistency/comment note only.
- **F-072-3 (P3, routed): revise_journal_block's CLI accepts `--kind` and silently ignores it**
  (commands.py:2082-2096 — the shared parser loop adds `--kind` to BOTH subcommands; the revise
  dispatch passes no kind; the kind carries forward from the row via the INSERT…SELECT). Observed
  live: `revise_journal_block --kind creative …` acks and the block's kind is unchanged (the flag is
  inert). A caller could believe they re-kind'd a block. The substrate stays honest.
- **F-072-4 (P3, routed): the revise ack's result_ref echoes the RAW CLI spelling while the payload
  canonicalizes** (commands.py:1772: `return f"{id_}@{revision + 1}"`). Observed live: an UPPERCASE
  `--id` acks `result_ref=01A1BF67-…@3` while the idempotency payload carries the canonical form
  (the uppercase-then-canonical same-key replay correctly answers `status=replayed`, same ref). The
  substrate stores the canonical uuid (uuid column). Display-only; matches the save_position/
  record_session family form. Consistency note.
- **F-072-5 (P3, process): the slice's chain summary omits the `966b5dc` typed-amendment commit, and
  that amendment postdates the GREEN tree that needed it by one commit.** The actual chain (git
  rev-list, all single-parent, linear) inserts `966b5dc` (red-records.json only: the ARV-RED-002/006
  amendment authorizing test_journal.py's 8f1ae13 repair) between `4a35546` (GREEN) and `838b1e9`
  (SYN-20 RED). So `4a35546` alone carried the test-digest drift ungated — no gate run is claimed at
  that tree (only the suite run), and the HEAD gate verifies the whole amendment chain green
  (`make verify` exit 0). Also routed here: the CLI's unparseable-id class (`revise --id garbage`,
  `--source-id not-a-uuid`) surfaces the generic `ARV-CMD-010: … psql stalled (repair: the rig's DB
  must be reachable)` — the F-071-4 sibling (misleading repair hint), a pre-existing shared class,
  verified live.

## 3. What was run (command + exit, each observed by this reviewer at the stated tree)

| Command | Tree | Exit |
|---|---|---|
| `python3 harness/tests/test_journal.py` | HEAD `806ef04` | **0** (JNL-01..06 GREEN) |
| `python3 harness/tests/test_sync.py` | HEAD `806ef04` | **0** (SYN-01..20 GREEN) |
| `make verify` | HEAD `806ef04` | **0** (gate green: suites + red records + scope/size + lint + deps + known-bads + proofsheet; canonical layer 54/0) |
| `python3 harness/tests/test_journal.py` | `f22d8d0` (RED, worktree) | **1** — `ARV-TEST-000` machinery-absent (command/list/get/migration flags all match red-01.txt exactly) |
| `python3 harness/tests/test_journal.py` | `8f1ae13` (strengtheners, worktree) | **1** — still machinery-absent RED (the repairs weakened nothing) |
| `python3 harness/tests/test_journal.py` | `4a35546` (GREEN, worktree) | **0** (JNL-01..06) |
| `python3 harness/tests/test_sync.py` | `838b1e9` (SYN-20 RED, worktree) | **1** — `RED — the P3-08 sync suite fails: SYN-20` only; SYN-01..19 green (matches red-02.txt) |
| sha256 chain | — | test_journal `@f22d8d0` = `d399ed44…` (binding) / `@HEAD` = `7484bb76…` (current); test_sync `@838b1e9` = `@HEAD` = `bca5d01a…` (the amendment's new digest) — all equal red-records.json |
| scratch rig | — | `pg.create_scratch_db('sevr1')` migrated 0001→0016 (16 migrations applied); two additional two-DB sync rigs built and dropped for the delivery/clause probes |

Worktrees removed after the archived-tree runs; no tracked file modified by the reviewer (this report is the one written file).

## 4. Probes (each probe + observed outcome, all on the reviewer's own scratch DBs)

1. **The >8 KB lossless round-trip.** A 10,984-byte body (pipes, newlines, U+2028 ×80, U+2029,
   U+0085, a raw CR, TAB, CJK 中文段落, and the LITERAL six-character text `\u2028`) written through
   `--file` → acks the frozen grammar (`status=committed result_ref=<block>@1 revision=1
   durability_rung=local_durable api_version=1`); a FRESH `get-journal` parses to content
   **byte-identical to the raw disk bytes** (10,984/10,984, CR byte included — the file channel is
   `read_bytes`, no newline translation). stdout framing: exactly ONE payload line under BOTH
   `split("\n")` AND `splitlines()`; the raw U+2028/U+2029/U+0085 bytes are ABSENT from stdout and
   the `\uXXXX` escapes are PRESENT (`_jline_safe`, query.py:660-676 — the escape set is exactly the
   three splitlines-class characters json leaves raw; control chars <0x20 json already escapes); the
   literal `\u2028` TEXT round-trips without double-escaping. A body ENDING in U+2028 ditto
   (byte-identical, one line).
2. **Kind "summary" refuses.** `ARV-JNL-002` named, exit 1, zero rows (count unchanged).
3. **Sourceless block.** get-journal answers `source_id: null` (first-class row); a bound block
   carries the binding (verified on the two-DB rig: the server row's source_id IS the translated
   SERVER source).
4. **Revise appends.** Revision 2 is a NEW row; revision 1 intact byte-for-byte; history `[1, 2]`;
   the current read returns revision 2 byte-honest; later `[1,2,3]` after the lock probe's append.
5. **Hostile phantom revision 9** (psql as arv_app, in-scope) → `ARV-JNL-007: … is not the next
   lawful revision (3)`.
6. **Hostile bind of an absent source** → `ARV-JNL-008` (the named code, never a bare FK violation).
7. **Guard ORDER observed live:** a hostile row with BOTH defects (absent bind + phantom revision)
   → `ARV-JNL-008` fires (guard line 18, the bind law FIRST) — the claimed order, reproduced.
8. **UPDATE and DELETE** (superuser psql) → `ARV-JNL-006` both.
9. **Owner isolation.** B's `get-journal` of A's block → `ARV-QRY-001`, byte-equal to B's absent-id
   ask; `get-journal-history` ditto; the write path (revise absent vs cross-owner) byte-equal
   `ARV-JNL-001` after id normalize.
10. **THE LOCK-KEY HUNT (no mismatch — proven live).** `hashtext` is text-level (uppercase diverges:
    −21345106 vs −1485316486), BUT `_nte_canon_id` normalizes upper/braced/no-hyphen spellings to
    the canonical form, and `hashtext(canonical) = hashtext(uuid::text)` — the command's key
    (commands.py:1763) EQUALS the 0016 guard's key (migration line `PERFORM
    pg_advisory_xact_lock(hashtext(NEW.id::text))`). **Blocking proof:** a psql session holding the
    GUARD's key (`pg_sleep(8)`) blocked a CLI revise with an UPPERCASE `--id` for ~7.0 s; it
    committed the instant the holder rolled back. The F-071-3 raw-spelling class is fixed at this
    family; the lock precedes the state read inside the one transaction.
11. **Idempotency.** Same key+body under a DIFFERENT id spelling → `status=replayed`, same
    result_ref; same key+different body → `ARV-CMD-409`, zero rows (substrate revisions unchanged).
12. **Crash matrix (create).** `pre-commit` → exit 2, ZERO rows; `post-commit-pre-ack` → exit 2,
    effect committed (1 row); the replay converges `status=replayed` (the suite covers the revise
    arm; the create arm probed here).
13. **Content boundaries.** NUL byte via `--file` → `ARV-JNL-004` (named, the lossless law);
    invalid UTF-8 → `ARV-JNL-003`; neither/both channels → `ARV-JNL-003` (suite + code read).
14. **Malformed read ids** → `ARV-QRY-002` echoing the bytes (F-072-1); malformed `--source-id` /
    unparseable revise `--id` → the generic `ARV-CMD-010` wrapper (F-072-5's routed sibling class);
    a quote-injection id is contained (the `''` doubling holds — only the cast error, no injection).
15. **The two-DB sync rig (reviewer-built):** import + extract on BOTH sites, save_position,
    source-bound journal_block, revise. Observed: the save acks `<server-source>@1`; the block
    DELIVERS with kind raw and the source binding TRANSLATED to the server's own source;
    server_ref `<server-block>@1`; the revise DELIVERS through the translated block id appending the
    server's revision 2 on the SAME server identity (`<server-block>@2`); the server history reads
    `[1, 2]` with BOTH bodies byte-identical through the delivery (pipes/U+2028/CJK included — the
    temp-file channel, never an argv truncation). Zero leaked `arv-sync-*` staging files in /tmp
    after the passes (the F5 unlink covers the `arv-sync-jnl-` prefix).
16. **The bridge-clause probe (F-072-2):** with the import (bare `result_ref`) AND the save
    (`<sid>@1`) both acknowledged, `_create_key(sid)` returns the import's key and `_translate(sid)`
    the bare server uuid — the create-class preference holds; no cross-entity translation observed.
17. **Substrate/registry audits:** capability.py's `journal/blocks` row renders (owner_phase P4-C,
    the verbs named, the P4-B reader-client exclusion); 0016's `arv-baseline-bump: 2` matches the
    0014/0015 convention; gate.py's TESTS registration landed AT the RED commit `f22d8d0`.

**The amendments judged.** (a) test_journal.py at `8f1ae13`: exactly the two disclosed strengtheners
(`revs ["1","2"] → ["1","2","3"]`; `PARA*60 → *70` = 8,820 chars > the suite's own 8192 self-check) —
verified by direct diff; no pin weakened; the ARV-TEST-000 probes unchanged; the suite observed still
machinery-absent RED at that tree. (b) test_sync.py at `838b1e9`: the SYN-20 pin is purely ADDITIVE
(a new check; SYN-01..19 byte-unchanged and observed green at the unrepaired tree). Both amendment
chains in red-records.json match the observed digests; the HEAD gate verifies the chains green.
