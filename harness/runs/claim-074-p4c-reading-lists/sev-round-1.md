# CLAIM-074 — SEV round 1 (the adversarial fresh-context verification)

- **Agent:** `agent-7d3e08a1` (independent fresh-context SEV reviewer; no authorship of the slice)
- **Date:** 2026-11-10
- **Round:** 1 (slice `CLAIM-074`, P4-C slice five — the reading-list surface)
- **Base:** `3f6922b` (origin/main at the PR #108 merge)
- **Head (the GREEN tree under review):** `60fab3d`
- **Chain:** `3f6922b` → `73bfd8c` (commit A: the post-#108 reconciliation + record 66) →
  `e7e833f` (the RED: test_reading_list.py tests-only + the SYN-22 pin + the gate registration) →
  `60fab3d` (the GREEN: migration 0017 + the three commands + the read arms + the outbox ride
  TOGETHER + the capability row + the crash membership + four disclosed pre-GREEN strengtheners)
- **Method:** live probes only, on the reviewer's own scratch rigs (two-DB walk + four law
  batteries + the RED reproduced from a `git archive` extraction of `e7e833f`); the recorded
  run-01..06 evidence was NOT re-run (spot-read only). ~92 live probe executions + ~10
  static/git checks. Zero repo writes by the reviewer other than this file; nothing committed.

## §1 Verdict

**PASS** — zero open P0/P1. One P2 (F-074-1, a live-reproduced delivery-failure edge on a
legal-but-dash-leading list name — a PRE-EXISTING family-wide argv-value class this slice's
name channel joins, not a class introduced here; routed with a named trivial repair) and three
P3s (F-074-2/3/4 — precision/consistency notes, none blocking). Every claimed behavior of the
slice's letter was independently reproduced live: the two-DB delivery walk end-to-end (the
event history `[added, removed, added]` landing server-side in order on the SERVER's list id,
the current membership equal on both domains through the TRANSLATED ids, both outbox rows
acknowledged with server_refs, the second pass a no-op), the derived-view law, the alternation
law under the advisory lock (including the serialization proof), the no-oracles byte-equal,
the name law, Q11's shared-name identity, the bounds, the substrate audit, the outbox enqueue
atomicity, and the RED chain git-verified and re-observed.

## §2 Findings

### F-074-1 — P2 (routed, pre-existing family-wide): a leading-dash list name is locally durable but never lands server-side (the argv value class)
- **Evidence (live, this rig):** a list named `--evil` — legal under ARV-RLS-003 (6 chars, no
  NUL; the `--name=--evil` CLI spelling creates it, `ACK ... status=committed`, outbox row
  enqueued) — delivers through `sync.py _cli_args` as the argv pair `["--name", "--evil"]`;
  the server-side `commands.py` invocation dies at **argparse** (exit 2, "the next token looks
  like an option"), which the driver classifies as **uncertain** ("the command process died
  mid-flight (the crash class)"). Observed: row `po-1` `uncertain` after pass 1 and still
  `uncertain` after pass 2 (attempts=2; `uncertain` never converts to failed — it is in
  `NON_TERMINAL`), server `reading_list` count unchanged (only the normal control list
  landed). The walk CONTINUES (a later normal list acknowledged on the same pass — not the
  F-073-1 queue-blocking class) and the local write stays durable, but that list never syncs
  and its row never reaches a terminal state.
- **Not introduced by this slice (verified live at the same tree):** `import_source` with
  `--title=--eviltoo` shows the IDENTICAL behavior (row `po-3` `uncertain`) — the class
  predates CLAIM-074 at the import title (and `create_note --content` shares the argv channel).
  The slice's record 66 §2 declares the choice ("the create's name through argv (a bounded
  label)") and the boundedness claim (1..512, no NUL) is true; the losslessness claim is false
  only for this leading-dash edge.
- **Narrowing:** the local space-form `--name --evil` is refused by argparse itself (exit 2,
  zero effect, no outbox row) — only the `=`-spelled local create produces the undeliverable
  row, so the trigger is narrow (a knowing or `=`-form-generated client).
- **Severity rationale:** a legal-input value whose claimed delivery round-trip is false would
  read as P1 in isolation; it is rated P2 because (a) the identical class predates the slice
  family-wide and was not introduced here, (b) the state is honest and visible (`uncertain`
  with the named reason, retried every pass — never a silent loss, never a terminal dead
  letter, never a queue block), and (c) the repair is trivial and family-local.
- **Disposition proposal:** ROUTE family-wide to the argv-value-channel class's own slice
  (import title, note content, reading-list name together): use the `=`-form invocation in
  `sync.py _cli_args` (e.g. `f"--name={p['name']}"` — argparse accepts leading-dash values in
  the `=` form; verified locally that `--name=--evil` commits) or the journal family's
  temp-file channel for every string-valued argv ride. Until then, the honest workaround:
  avoid leading-dash names/titles/contents.

### F-074-2 — P3: a different-key duplicate-op membership write surfaces as the generic ARV-CMD-010 honest-unknown, not a typed code
- **Evidence (live):** `add_to_list` on a pair whose current state is `added`, with a NEW
  idempotency key (no replay, no 409): rc=1, `FAIL ARV-CMD-010: the session died before the
  marker with an unrecognized cause — the honest unknown; raw cause: ERROR: ARV-RLS-008: the
  membership event op added ... duplicates the pair's current state`. Zero effect verified
  (event rows unchanged at 3; zero outbox rows; the ON_ERROR_STOP session death rolls the
  transaction back). The refusal is honest and zero-effect, and the raw cause names
  ARV-RLS-008 — but the top-level code is the generic wrapper, and no test pins this path
  (RLS-03 pins same-key replay + ARV-CMD-409 only).
- **Disposition proposal:** a future increment may add a typed command-layer pre-check in
  `_rls_event.build` (read the pair's current state, raise `_CapRefusal("ARV-RLS-008", ...)`)
  so the ordinary-client duplicate carries the law's own name; the substrate guard stays as
  the structural backstop. Not blocking: the migration's own comment frames ARV-RLS-008 as
  the hostile-write guard with the command layer's idempotency as the client-path protection,
  and the observed behavior matches that declared boundary.

### F-074-3 — P3 (consistency): red-01.txt names the commit-A tree as the observation tree, not the RED commit
- **Evidence:** red-01.txt's header reads `Tree: 73bfd8cda4b...` (commit A) while the RED
  commit is `e7e833f` and red-records.json says "observed RED there" (binding commit
  `e7e833f`). This is the standing family convention (CLAIM-072's and CLAIM-073's red-01.txt
  record their commit-A trees the same way — checked), and it is materially equivalent: I
  extracted `e7e833f` via `git archive` and reproduced the RED there myself —
  `test_reading_list.py` exit 1 (ARV-TEST-000 machinery-absent, the same parenthetical
  values) and `test_sync.py` exit 1 with SYN-01..21 GREEN (21 PASS lines counted) and SYN-22
  the FAIL — byte-consistent with red-01.txt's account.
- **Disposition proposal:** note only; optionally a future red-01 template could name the RED
  commit itself. No action required.

### F-074-4 — P3 (assessment, no fix): the get-list two-read shape (header read, then member page)
- **Evidence/assessment:** `_get_list` reads the list header (RL_SQL) and then the member page
  (RLMEM_SQL) on two separate psql sessions/snapshots. The header cannot vanish between the
  reads (the table is append-only — ARV-RLS-006; no DELETE path exists), so the
  read-then-page race has no vanish/corruption class; a membership event committed between
  the two reads simply joins the page (monotonic append). The residual is the family's known
  bounded class: `list-lists`'s derived `member_count` and `get-list`'s page can
  momentary-diverge under concurrent membership writes. Consistent with how the prior list
  arms were accepted; assess-only per the round's instructions.

## §3 The probes (all live on this rig; scratch DBs created/dropped per probe, nothing left behind)

**Static/git (10 checks):**
1. `git log`/`git status` — HEAD `60fab3d`, clean except the six untracked run-01..06.json
   records (the expected pre-finalize state per record 66 §3's chain). exit 0.
2. `git diff 3f6922b...HEAD --name-only` — 19 paths, every one inside scope.txt's declarations
   (the run-dir declaration covers red-01.txt/scope.txt). exit 0.
3. Residue grep (`git grep -E "reading_list|list-lists|get-list|reading-lists"` over tracked
   files, excluding the declared set) — hits ONLY in the declared docs (AGENTS/CLAIMS/PLAN/
   STATE/WORKLOG/record 66) and the declared run dir. No residue outside scope. exit 0.
4. Red-records sha chain, git-verified: `test_sync.py` `e13aca94` @73bfd8c → `12a8d905`
   @e7e833f (unchanged @60fab3d) = the recorded amendment pair;
   `test_reading_list.py` absent @73bfd8c → `a0f5f339` @e7e833f (the binding) → `ba6ed393`
   @60fab3d (current, after the four disclosed strengtheners). All four strenghteners are
   visible in the final test file (the in-process `_rls_name` NUL unit-probe, the
   parsed-id cursor, `has_table_privilege`, the superuser trigger channel). exit 0 each.
5. Full reads: migration 0017, the commands.py/query.py/sync.py/capability.py/crash.py/
   gate.py diffs, record 66 §2, the CLAIMS row, red-01.txt, run-01..06.json (six exit-0
   records at `60fab3d`; the RLS x3 output shas identical — plausible, the suite prints
   PASS/FAIL lines only).
6. `capability.py surfaces` — the `reading-lists` reserved-surface row present, "LANDED"
   P4-C. exit 0.
7. gate.py TESTS registration — `harness/tests/test_reading_list.py` added (diff-verified).
8. Prior red-01.txt convention check (CLAIM-072/073) — the commit-A tree form is the family
   convention (F-074-3).

**The RED reproduced at `e7e833f` (git archive → /tmp, 2 runs):**
9. `python3 harness/tests/test_reading_list.py` → **exit 1**, `FAIL ARV-TEST-000` (command
   absent: True; list-lists absent: True; get-list absent: True; migration 0017 present:
   False) — matches red-01.txt.
10. `python3 harness/tests/test_sync.py` → **exit 1**, SYN-01..21 GREEN (21 PASS lines),
    SYN-22 FAIL — matches red-01.txt.

**The two-DB delivery walk (`/tmp/sev74/walk.py`, own script, 24 probes — 23 pass, 1 was my
own marker-string expectation; the substance verified):**
11. Two scratch DBs created via the pg adapter + `migrate.py` each; owner A: import → create
    list (`ACK ... status=committed result_ref=<bare uuid>`, 36-char hyphenated) → add →
    remove → re-add (all rc0 committed). Local event history `[added, removed, added]`.
12. `sync.py sync --owner A --server-db <srv>` → exit 0; **all 5 outbox rows `acknowledged`
    with server_refs** (import + create + add + remove + re-add); the create's server_ref
    equals the server ledger's own `result_ref` for the key.
13. **Server list name byte-identical** ("The SEV Walk List"); **server event history
    `[added, removed, added]` on the SERVER's list id**; **server get-list answers exactly 1
    active member bound to the SERVER's source id** (the translated binding, header
    `# api_version=1` + `# more=false`); local get-list equal in count+binding on the local
    ids; **event rows retained 3/3 on BOTH domains** (the history never destructive).
14. Second sync pass → exit 0, `SYNC-DONE owner=A rows=0` (my probe expected the literal
    "delivered=0" — the driver's actual no-op marker is `rows=0`; verified: zero rows
    re-delivered, server count still 3 — the no-op holds).
15. Outbox enqueue atomicity: exactly **5 outbox rows for 5 committed writes**; the same-key
    replay (`status=replayed`, same result_ref) added **0** rows.

**The law batteries (`/tmp/sev74/laws.py` 37 probes + `/tmp/sev74/laws2.py` 18 probes —
every initial "FAIL" was traced to my own assertion/query bugs and re-verified correct in
laws2; no product failure behind any of them):**
16. **Name law:** empty → rc1 ARV-RLS-003; 513 chars → rc1 ARV-RLS-003; 512 chars → rc0
    committed (the boundary); NUL unit-probe on `_rls_name` → ARV-RLS-003 (argv cannot carry
    NUL — the OS refusal precedes); all refusals zero-effect (tables/command_log/outbox
    unchanged).
17. **Q11 identity:** two lists named "Twin Name" both created, distinct uuids, BOTH listed by
    list-lists; the only UNIQUE constraint on `arv.reading_list` is
    `reading_list_id_owner_scope_key` (id, owner_scope) — NO name uniqueness (name carries
    only the 1..512 CHECK).
18. **No-oracles:** absent vs cross-owner LIST (ARV-RLS-001) and absent vs cross-owner SOURCE
    (ARV-RLS-002) byte-equal after id-normalize (rc1 both); the read arm's absent vs
    cross-owner get-list **byte-equal RAW** (ARV-QRY-001, the no-id-echo form); zero effect
    (no event rows, no outbox rows for the probes).
19. **Derived-view law:** active → hidden (after remove) → active again (after re-add); event
    rows `[added, removed, added]`, 3 DISTINCT ids — new rows, never a mutation;
    `list-lists`'s derived `member_count` correct (1/0/0 across the fixture lists).
20. **Idempotency:** same key+body → `status=replayed` (same result_ref); same key+different
    body → rc1 ARV-CMD-409, zero effect; variant-spelling retry (UPPERCASE list+source ids,
    same key) → REPLAY with exactly 1 event row (the `_nte_canon_id` normalize law).
21. **Bounds:** list-lists `--limit 0/1001/x` → rc1 ARV-QRY-004 each; get-list `--limit 0` →
    rc1 ARV-QRY-004; the `--limit 2` keyset walk over list-lists = the exact id union, no
    dups; the member page cursor (`--after <source-id>`) pages 3 members over 2 pages exact.
22. **Owner isolation:** B's list-lists shows only B's list; B's get-list answers B's member;
    A's derived member_counts exclude B's rows (the RLLIST_SQL inner query runs under the
    same RLS context; the composite FK double-protects owner-consistency).
23. **Alternation law (hostile superuser INSERT, proper uuid literals):** duplicate 'added'
    (current='added') → ERROR ARV-RLS-008; lawful 'removed' → passes; duplicate 'removed' →
    ARV-RLS-008; lawful re-'added' → passes; the two hostile alternations appended exactly 2
    rows (history 3 total, all retained). Phantom-list INSERT → FK violation (the composite
    `reading_list_member_list_id_owner_scope_fkey`); out-of-vocabulary op 'evicted' → the
    NAMED CHECK `reading_list_member_op_check`.
24. **Advisory-lock serialization:** a held `pg_advisory_xact_lock(hashtext('<list>:<source>'))`
    in a concurrent session BLOCKS a hostile member INSERT past a 1500ms statement timeout
    (cancelled at ~1.5s inside the trigger's lock acquisition) — hostile writers serialize
    behind the command path.
25. **Substrate audit:** `relrowsecurity=1, relforcerowsecurity=1` on BOTH tables;
    `owner_isolation` policy on both (FOR ALL TO arv_app, USING+WITH CHECK on
    `app.current_owner`); `has_table_privilege`: arv_app INSERT=true SELECT=true UPDATE=false
    DELETE=false, arv_read SELECT=true (both tables); NO DEFAULTs (information_schema
    column_default count 0); both composite FKs present; the append-only triggers refuse
    UPDATE (ARV-RLS-006) and DELETE (ARV-RLS-007) at the superuser channel.
26. **Crash arm:** `crash.py create_reading_list pre-commit` → exit 2, zero reading_list
    rows, zero outbox rows.
27. Empty list's get-list → exactly `# api_version=1` + `# more=false` (the honest two-line
    answer, never pure silence).

**The adversarial delivery probes (`/tmp/sev74/poison.py` 6 observations + `/tmp/sev74/dep.py`
1 probe + `/tmp/sev74/final.py` 4 probes):**
28. F-074-1's class end-to-end (the poison name, the continuing walk, the pre-existing import
    title twin) — see the finding.
29. **ARV-SYN-009 dependency rest:** with the list create resting undelivered (the poison
    name), the membership add rests `retryable` with the named reason "ARV-SYN-009: the
    reading list ... is not yet server-durable — the identity dependency", zero server
    member rows, the sync pass exit 0 — the truthful dependency class, never a dead letter.
30. **The argv channel's losslessness within its legal vocabulary:** a 512-char name carrying
    unicode (Ünïcode—名前), an embedded newline, and padding delivers **byte-identical**
    server-side (len 512 == 512); the membership on that list acknowledges.

## §4 Honest limits

- The recorded evidence (run-01..06.json: the RLS suite x3, the sync suite, the journal
  suite, `make verify`) was **not** re-run — the round's instruction took those records as
  standing and my budget went to independent probes instead. My own walk + law batteries
  cover the same behavioral ground the RLS/SYN-22 suites pin, but the canonical 54/0 `make
  verify` count is taken on the record, not reproduced.
- The two-DB walk exercised one owner, one list, one source, and the add/remove/re-add
  triangle (the SYN-22 shape) — not multi-list fan-out, cross-owner delivery interleavings,
  or the max-attempts terminal policy on reading-list rows (the family's SYN-06/07 pins
  cover the driver machinery generally; I read those branches but did not re-prove them).
- F-074-1's pre-existing-ness was verified against the import-title twin **at this tree**
  (live), plus the code read of `_cli_args`' argv construction; I did not bisect the class's
  introduction commit, and I did not audit whether any prior SEV round already flagged it
  (its absence from CLAIM-073's round-2 findings is inferred from the close rows, not proven).
- The RLS x3 records' identical output sha256s were judged plausible (PASS/FAIL-only output)
  by reading the suite's `check()` — not verified by re-running.
- Probe scripts live under `/tmp/sev74/` (walk.py, laws.py, laws2.py, poison.py, dep.py,
  final.py) and the RED extraction under `/tmp/sev74red/` — nothing was written into the
  repo, no tracked file was modified, nothing was committed, and all scratch DBs were dropped
  in the probes' `finally` blocks.
- The `uncertain`-forever behavior in F-074-1 was observed over two passes (attempts 1→2);
  the never-terminal reading rests on the code read of `NON_TERMINAL`/`_outcome` (uncertain
  has no max-attempts conversion), not on a many-pass exhaustion run.
