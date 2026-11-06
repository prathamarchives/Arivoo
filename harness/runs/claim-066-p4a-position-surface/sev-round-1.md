# SEV round-1 — CLAIM-066 / P4-A slice two (the source-open/position surface)

- **Agent label:** agent-7c41e9d2
- **Date:** 2026-11-06 (round 1, fresh context)
- **Slice:** `slice/claim-066-p4a-position-surface` — CLAIM-066, P4-A slice two (the source-open/position surface)
- **Base:** `origin/main` = `562b70f` (PR #100, CLAIM-065's merged head)
- **Head:** `d8a1f7a`
- **Commit chain:** `7105dad` (commit A: post-#100 reconciliation + record 58 + scope.txt; NO implementation) → `a571792` (the RED: test_position.py + gate.py TESTS registration + red-01.txt; NO implementation — verified by `git show --stat`) → `da9967b` (the typed red record) → `d8a1f7a` (the GREEN: commands.py save_position, query.py get-position, migration 0014, crash.py membership, sync.py cast, capability.py reservation)

## 1. What I ran

| # | What | Result |
|---|------|--------|
| 1 | `python3 harness/tests/test_position.py` | exit 0 — **6/6 PASS** (POS-01..06 GREEN) |
| 2 | `python3 harness/tests/test_commands.py` | exit 0 GREEN (S3 acceptance a-e) |
| 3 | `python3 harness/tests/test_sync.py` | exit 0 GREEN (SYN-01..17) |
| 4 | `python3 harness/tests/test_migrations.py` | exit 0 GREEN (S1 a-e + M0 oracle f-l; the widening's blast radius) |
| 5 | `python3 harness/tests/test_capability.py` / `test_import.py` / `test_extract.py` / `test_gate_dispatch.py` | all exit 0 GREEN |
| 6 | `python3 harness/tests/test_export.py` / `test_capture.py` | exit 0 GREEN (result_ref TEXT consumers) |
| 7 | RED-form re-observation: `git worktree /tmp/sev1_red @ a571792` → `python3 harness/tests/test_position.py` | **exit 1, ARV-TEST-000** — byte-matches `red-01.txt` exactly (save_position absent / get-position absent / 0014 absent) |
| 8 | Red-records chain hashes | HEAD `sha256(test_position.py)` = `f26ca6ed…` = `current_sha256` = amendment `new_sha256`; `git show a571792:…| sha256sum` = `ed98a219…` = `prior_sha256` = `binding_sha256` — **chain exact at every link** |
| 9 | `scope.check_scope(diff 562b70f…HEAD)` + `claims.check_branch_claim(...)` + `claims.check_registry()` (live, the gate's own modules) | **ARV-SCOPE-002 ×2 + ARV-CLM-002** (see F2); registry GREEN |
| 10 | Adversarial probes a–h on own scratch DBs (created via `pg.create_scratch_db`, migrated with 0014, **all dropped after**) | see §3 |

## 2. Findings

1. **[P1] the claimed "outbox ride" is a dead letter: the sync bridge cannot deliver `save_position` — every position save burns to a terminal-`failed` outbox row and never reaches the server site.**
   `harness/commands.py:63` adds `save_position` to `_SYNC_COMMANDS` (the GREEN commit's own claim: "the _SYNC_COMMANDS membership (the outbox ride)"; POS-03 pins only the enqueue count), but `harness/sync.py` `_cli_args` (harness/sync.py:155–195) has **no `save_position` branch** — the fall-through at harness/sync.py:194-195 returns `ARV-SYN-000: the command save_position is not in the outbox-carrying set — never delivered`.
   **Live evidence (two fresh scratch DBs, local+server, both migrated to 0014):** import+extract+save on the local site, then `python3 harness/sync.py sync --owner A --server-db <server>`:
   - pass 1: `SYNC key=sp1 state=retryable reason=ARV-SYN-000` (the import synced `acknowledged` fine)
   - pass 2: `state=retryable reason=ARV-SYN-000`
   - pass 3 (default `--max-attempts 3`): `state=failed reason=ARV-SYN-000` — terminal; `SYNC-STATUS owner=A acknowledged=1 failed=1`
   The server DB never receives the position; every future save leaves a permanently `failed` residue. No test pins delivery coverage of `_SYNC_COMMANDS` members (test_sync.py never references it), which is how this escaped the blast-radius suites. Unit-level confirmation: `_cli_args({"command_name": "save_position", …})` → `(None, "ARV-SYN-000: … never delivered")`.
   *Repair in-slice:* add the `save_position` branch to `_cli_args` (translate `source_id` through `_translate` — the import's result_ref join works, the `s.id::text` cast is already there — then `["--source-id", sid, "--start", str(p["start"]), "--end", str(p["end"])]`) **plus** a delivery pin (extend POS-03 or SYN with a save_position sync round-trip); or, if delivery is genuinely deferred, drop the `_SYNC_COMMANDS` membership and disclose the deferral in the bounded exclusions — the current state claims a ride that cannot complete.

2. **[P1] scope breach: `harness/crash.py` and `harness/sync.py` are changed in the diff but declared in neither `scope.txt` nor the CLAIMS.md CLAIM-066 scope cell — the PR-mode gate refuses this slice as-is.**
   `git diff --name-only 562b70f…HEAD` = 17 paths; `harness/runs/claim-066-p4a-position-surface/scope.txt` and the CLAIMS.md row declare 14 globs (the runs-dir prefix covers red-01.txt/scope.txt). Missing: `harness/crash.py` (the crash-matrix membership — a load-bearing part of this slice's own claims) and `harness/sync.py` (the `s.id::text` join cast, also this slice's claim).
   **Live evidence (the gate's own modules on the real diff):**
   - `scope.check_scope(...)` → `ARV-SCOPE-002: harness/crash.py … OUTSIDE the declared scope` and `ARV-SCOPE-002: harness/sync.py …` (LAW-06)
   - `claims.check_branch_claim("slice/claim-066-p4a-position-surface", …)` → `ARV-CLM-002` (×2, the claim-coverage law)
   The GREEN commit defers the gate ("the full make verify + the gate_dispatch positive shapes follow at the committed tree") — when they run, they refuse. *Repair in-slice:* add both files to scope.txt (with the `D-041` owner ref — `harness/` is a protected prefix) and to the CLAIMS.md scope cell, then re-observe the PR-mode checks.

3. **[P3, repair-in-slice] stale comment: `harness/commands.py:1390-1391` still says "command_log.result_ref is a UUID".**
   Migration 0014 (harness/migrations/0014_reading_position.sql:75) widened `arv.command_log.result_ref` UUID → TEXT; the comment on the `rebuild_keyword_index` build is now false. One-line comment repair; no behavioral effect.

**Observations (no class — informational):**
- The measured-set records `run-01.json`..`run-05.json` exist only as **untracked** working-tree files; the proof-sheet verify at PR time reads committed state — they must ride the record-completion commit before the push (the GREEN commit already says the record completion follows).
- The five disclosed test amendments were **each re-derived from `git diff a571792:…test_position.py HEAD:…test_position.py`** and none weakened a pin: (1) crash arm routed through `harness/crash.py --point` (the RED's `--crash-at` on commands.py was argparse's usage exit — the assertions on the crash outcome are unchanged); (2) the two hostile-INSERT `VALUES (` parens (a syntax error never reached the guards — assertions unchanged); (3) grants `t|f|f|t` → `true|false|false|true` (the SQL-level `||` concatenation's `bool::text` output; the test_import.py:533 precedent verified; still asserts all four privileges); (4) outbox count moved after the crash arm with the **same** `>= 3` threshold (the pre-crash placement could never reach 3 — refusals enqueue nothing, POS-02's own law); (5) the UNIQUE audit narrowed to `pg_get_constraintdef = 'UNIQUE (owner_scope, source_id, save_ordinal)'` (the RED's bare `contype='u'` count was unreachable — two u-constraints exist — and the narrowed form is strictly more precise). **No assertion was removed; no P0.**

## 3. Probes

All probes on own scratch DBs (Postgres rig port 5433; created via `pg.create_scratch_db`, migrated with `harness/migrate.py` incl. 0014; **every DB dropped after — 0 `arv_arv_sev1*`/`arv_p4a2*` remain**).

| Probe | Observed |
|---|---|
| **a. write no-oracle** | owner B saving A's extracted source vs a genuinely absent uuid: both exit 1, both `FAIL ARV-POS-001:`; stdout byte-equal after id-normalization — **same refusal bytes** |
| **b. concurrent saves** | 4 simultaneous fresh-key `save_position` processes (`&`/`wait`): all exit 0, ordinals 3,5,6,4 committed (arbitrary order, **consecutive, no skip, no collision**); a 2-process run gave @1/@2. The per-(owner,source) advisory xact lock serializes as claimed |
| **c. hostile INSERTs as arv_app** (`SET app.current_owner='A';`) | skipped ordinal 99 → `ARV-POS-004` ("not the next lawful save (6 + 1)"); SRC2's generation on SRC1's row → `ARV-POS-006` ("never crosses sources"); row count unchanged after all hostile attempts. Extra: B inserting into A's scope (any shape) is refused fail-closed — the BEFORE-INSERT trigger fires ahead of the RLS WITH CHECK (its own RLS-scoped max/generation reads see nothing) — no leak path found |
| **d. UPDATE/DELETE as superuser** | both refuse `ARV-POS-005` (append-only trigger fires even for postgres) |
| **e. generation binding across re-extraction** | save @6 under gen1; re-extract → new current gen; get-position: `saved_generation_id` byte-stable = gen1, `current_generation_id` = new, `generation_matches:false`, offsets unchanged; **new save binds the new generation** (matches:true). No silent retarget |
| **f. replay/409** | same key+body → `status=replayed`, same `result_ref=<src>@8`; same key+different body → exit 1 `ARV-CMD-409`, rows 7→8 (only the one lawful save) — zero effect |
| **g. old-family honesty** | `import_source` same-key replay acks `status=replayed result_ref=<plain-uuid>` (the TEXT widening lossless; uuid rows verified `~ '^[0-9a-f-]{36}$'` = t, save_position refs = f); different body → ARV-CMD-409. `command_log.result_ref` data_type = `text`; serving index `command_log_result_ref_idx (owner_scope, result_ref)` present |
| **h. read-arm no-oracle** | `get-position` vs `get-source` on the same absent id: exit 1, **stdout byte-equal**; owner B on A's saved source vs B on an absent id: byte-equal after id-normalization — never a leak that a position exists. In-scope never-saved source: typed `no_position_saved` ANSWER at exit 0 with `api_version=1` |
| crash arm | `harness/crash.py --command save_position --point post-commit-pre-ack` → exit 2, effect committed (ordinal 9 readable via get-position), same-key replay converges `status=replayed … @9`. Outbox: 9 save_position intents for 9 committed saves (refusals/replays enqueue nothing) |
| POS-003 offset law | negative / empty (start==end) / beyond-text offsets all refuse `ARV-POS-003` naming the true text length — never clamped (via suite + scratch runs) |
| POS-002/006 substrate | ARV-POS-001 (absent ≡ cross-owner), ARV-POS-002 (unextracted source), zero new rows on every refusal — re-observed live |

## 4. Disposition

**BLOCKED** — two open P1 findings:

- **F1 (P1)** the outbox ride's delivery half is absent: `save_position` outbox rows are undeliverable (`ARV-SYN-000`), observed live burning retryable → terminal `failed`; the server site never receives a position save (harness/sync.py:155–195 vs harness/commands.py:63).
- **F2 (P1)** the scope declarations do not cover the actual diff: `harness/crash.py` + `harness/sync.py` undeclared in scope.txt and the CLAIMS.md scope cell — the PR-mode gate refuses (ARV-SCOPE-002 ×2 + ARV-CLM-002, observed live via the gate's own modules).

P3s: **F3** (stale "result_ref is a UUID" comment, harness/commands.py:1390-1391) — repair-in-slice (one line).

Everything else the slice claims was verified and holds: the POS suite 6/6 at HEAD and a true RED at `a571792` (exit 1, ARV-TEST-000, byte-matching red-01.txt, no implementation smuggled into the RED commit); the red-records chain exact at every link; the five disclosed amendments all strengthening/reaching, none weakening; the no-oracle byte-equality on both the write and read boundaries; the serialized ordinal law under real concurrency; the append-only/generation-bind/ordinal substrate guards incl. superuser UPDATE/DELETE; the generation binding honest across a re-extraction with new saves riding the serving generation; replay/409/crash-convergence through the spine; the 0014 conventions (no DEFAULTs, RLS forced, grants INSERT+SELECT/SELECT with no UPDATE/DELETE, two composite FKs, the (owner, source, ordinal) UNIQUE, no content column, baseline-bump directive, result_ref TEXT widening with the serving index); the old families' replay honesty after the widening; the blast-radius suites (commands/sync/migrations/capability/import/extract/gate_dispatch/export/capture) all green.

*Repair F1 + F2 (+ F3's one-liner) in-slice, disclose the amendments, and re-observe the PR-mode gate green — then this slice is a strong PASS candidate for round 2.*
