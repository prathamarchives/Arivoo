# SEV round-3 — CLAIM-066 / P4-A slice two (the source-open/position surface — FINAL)

- **Agent label:** agent-3fa1c0d2
- **Date:** 2026-11-06 (round 3, FINAL, fresh context, adversarial close-out)
- **Slice:** `slice/claim-066-p4a-position-surface` — CLAIM-066, P4-A slice two (the source-open/position surface)
- **Base:** `origin/main` = `562b70f` (PR #100, CLAIM-065's merged head)
- **Head:** `8ba4771` (the round-2 repair commit: F4 scope completion + F5 wording + F6 disclosure)
- **Commit chain:** `7105dad` (commit A: post-#100 reconciliation + record 58; NO implementation) → `a571792` (the RED: test_position.py + gate.py TESTS registration + red-01.txt; NO implementation) → `da9967b` (the typed red record, bound to the RED commit) → `d8a1f7a` (the GREEN: save_position + get-position + migration 0014 + crash/sync/capability membership + the five disclosed test amendments) → `057b426` (the round-1 repairs: F1 delivery + SYN-18, F2 sync.py/crash.py scope, F3 comment, run-06..08, sev-round-1.md) → `8ba4771` (the round-2 repairs: F4 test_sync.py scope completion, F5 the RED wording, F6 disclosure — this round's tree)

## 1. What I ran

| # | What | Result |
|---|------|--------|
| 1 | `sev-round-2.md` read in full; `git log --oneline` chain re-read; `git diff --name-only 562b70f...HEAD` | 28 paths; chain matches the round-2 report's letter |
| 2 | `python3 harness/tests/test_position.py` | exit 0 — **6/6 PASS** (POS-01..06) |
| 3 | `python3 harness/tests/test_sync.py` | exit 0 — **18 PASS lines (SYN-01..18)**; final line "GREEN — the P3-08 acceptance suite (SYN-01..18) passes" |
| 4 | Red-records chains, both files | **exact at every link** — see §2 |
| 5 | The gate's own modules live: `scope.check_scope(28 paths, slice)` / `claims.check_branch_claim(branch, paths)` / `claims.check_registry()` | **all three return `[]` (GREEN)** — every diff path declared |
| 6 | Adversarial spot-checks (a)–(d) on my OWN scratch DB (`pg.create_scratch_db("sev3r3")`, migrated incl. 0014, **dropped after — zero `arv_*` databases remain**) | **5/5 OK** — see §4 |
| 7 | Leftover sweep: `git diff 562b70f...HEAD \| rg -i 'todo\|fixme\|xxx\|placeholder'` | **zero matches** |
| 8 | Additivity audit: `git diff a571792..HEAD -- harness/tests/test_position.py` (removed lines) + `git diff 562b70f..HEAD -- harness/tests/test_sync.py` (removed lines) + `check("POS-…")` call counts RED vs HEAD | see §2/§3 — all additive/disclosed |
| 9 | `git status --porcelain` after all probes | clean (this report is the only new file, under the declared runs directory) |

## 2. Repair verification (F4/F5/F6)

**F4 (P1, the repair commit's own undeclared pin file `harness/tests/test_sync.py`) — VERIFIED CLOSED.**
- `scope.txt` line 23 now carries `harness/tests/test_sync.py D-041`; the CLAIMS.md CLAIM-066 row's file list (CLAIMS.md:17) names it too (alongside test_position.py, commands.py, query.py, capability.py, 0014, gate.py, sync.py, crash.py, red-records.json, CLAIMS.md, STATE.md, AGENTS.md, PLAN.md, WORKLOG.md, record 58, the runs directory).
- Cross-check of all **28** `git diff --name-only 562b70f...HEAD` paths against the declarations: **zero undeclared paths** (the 12 runs-directory artifacts ride the `harness/runs/claim-066-p4a-position-surface D-042` directory declaration; this round-3 report rides the same).
- **Live evidence (the gate's own modules, not my reading of the lists):** `scope.check_scope(paths, 'claim-066-p4a-position-surface')` → `[]`; `claims.check_branch_claim('slice/claim-066-p4a-position-surface', paths)` → `[]`; `claims.check_registry()` → `[]`. The round-2 ARV-SCOPE-002/ARV-CLM-002 refusals no longer fire.

**F5 (P3, the RED wording) — VERIFIED.**
- record 58 §3 (context/extracted/58-P4A-POSITION-SURFACE.md:19): "THE RED (LAW-11): test_position.py ALONE at the RED commit (tests-only, the LAW-11 form — red-01.txt honestly records 'migration 0014 present: False'; the migration lands with the GREEN, never the RED)".
- STATE.md:16 ("Exact next action"): "the RED (test_position.py alone — tests-only per LAW-11, migration 0014 lands with the GREEN; the POS registry: …)". Both now state the tests-only truth; the ambiguous "test_position.py + migration 0014" parenthetical is gone from both.

**F6 (P3, run-record convention) — VERIFIED as disclosed, no change required.** The round-2 report §3 finding 3 + §5 carry the full disclosure (run-06/07/08's commit field names the HEAD-at-capture `d8a1f7a`; the digests reproduce byte-exactly at the repair tree — the documented `write_record` capture convention, proofsheet.py). Round-3 concurrence: nothing further to repair.

**Red-records chains (one last time) — exact at every link, both files.**
- `harness/tests/test_position.py`: sha256 at HEAD `f26ca6ed…35b4` = `current_sha256` = the single amendment's `new_sha256`; the amendment's prior `ed98a219…f7b64` = `git show a571792:… \| sha256sum` (re-computed this round) = `binding_sha256` (binding_commit `a571792` = the RED commit).
- `harness/tests/test_sync.py`: sha256 at HEAD `c25318b5…0fdc4` = `current_sha256` = the 3rd amendment's `new_sha256`; the 3rd amendment's prior `4a4d8079…d988` = `git show d8a1f7a:… \| sha256sum` = **also** `git show 562b70f:… \| sha256sum` (re-computed — the pre-SYN-18 form is honestly the untouched base form); the internal chain `d2158263` (binding `e91dc9a`) → `39fa65e1` → `4a4d8079` → `c25318b5` links exactly, each amendment's prior = the previous link's new.

## 3. Findings

**Zero open P0/P1/P2/P3.**

The round-2 findings are all closed (F4 verified live against the gate's own modules; F5 verified in both records; F6 disclosed in the round-2 report per its own disposition). This round's independent sweep found nothing new:

- TODO/FIXME/XXX/placeholder in the full diff: **zero matches**.
- Undeclared changed paths: **zero** (live `check_scope`/`check_branch_claim` GREEN over the full 28-path diff).
- Assertion weakening: **none** —
  - `test_position.py` RED `a571792` → HEAD: exactly **8 removed lines**, each mapping 1:1 onto the GREEN commit's five DISCLOSED amendments (the crash-arm routing through `harness/crash.py --point`, not argparse; the two hostile-INSERT `VALUES` paren fixes; the outbox count moved after the crash arm; the grants comparison's `t|f|f|t` → `true|false|false|true` bool::text form; the UNIQUE audit via `pg_get_constraintdef`). `check("POS-…")` call count is 6 in both forms; no `ok`-condition removed (the one touched condition line is the grants-form correction, disclosed, and strictly truth-preserving — the RED form could never be green).
  - `test_sync.py` base → HEAD: exactly **1 removed line** — the final GREEN banner's `SYN-01..17` → `SYN-01..18`. The SYN-18 case block + check block are pure additions; SYN-01..17 byte-untouched.

Observations (no class, for the record):
- The dead `--crash-at` passthrough branch in `cmd()` (harness/tests/test_position.py:142-143) remains — the round-2 cosmetic observation, unchanged: never invoked (the crash arm routes through `save()`'s crash.py `--point` path), zero effect on any suite.
- The round-2 observations on the outbox terminal policy (P3-08 class) and `make verify`'s non-byte-deterministic captured output stand as written there; neither is a slice defect.

## 4. Spot-checks

All on my OWN scratch DB (rig port 5433; created via `pg.create_scratch_db("sev3r3")`, migrated incl. 0014; **dropped after — `pg_database` shows zero `arv_%` rows; `git status` clean**).

| Probe | Observed |
|---|---|
| setup | `save_position` on an extracted source: exit 0, `status=committed`, `result_ref=<src>@1` |
| **a. write no-oracle** | owner B saving on A's extracted source vs B on an absent uuid: both exit 1, `FAIL ARV-POS-001:`, **stdout byte-equal after id-normalization, stderr byte-equal** |
| **b. hostile INSERT, skipped ordinal** | as `arv_app` (A's scope), `save_ordinal=9` when the next lawful is 2: refused with **ARV-POS-004** in stderr; row count 1 → 1 (zero effect) |
| **c. superuser UPDATE** | as `postgres`: `UPDATE arv.reading_position SET start_off=0` refused with **ARV-POS-005** (the append-only trigger fires even for the superuser); row count still 1 |
| **d. re-extraction honesty** | after `extract` #2 (gen2 ≠ gen1): get-position returns `generation_matches=false`, `saved_generation_id` = gen1 (unchanged), `current_generation_id` = gen2, saved offsets 5/20 unchanged; the row's `generation_id` still gen1 in the table — **never a silent retarget** |

## 5. Disposition

**PASS** — zero open P0/P1/P2/P3.

Every round-2 finding is verified closed at `8ba4771`: F4's scope completion is real against the gate's own live modules (all 28 diff paths declared in both scope.txt and the CLAIMS.md row; `check_scope`/`check_branch_claim`/`check_registry` all GREEN); F5's wording now states the tests-only RED truth in both record 58 §3 and STATE.md; F6 stands as disclosed. The acceptance sweep re-observed green this round (POS 6/6, SYN-01..18 all PASS, both exit 0); both red-records chains re-derived exact at every link (including the prior-form digests re-computed from `git show` at the RED/GREEN commits); the four adversarial spot-checks plus the setup save all passed on my own scratch rig (dropped after); the leftover sweep found zero TODO/FIXME/placeholder, zero undeclared paths, and zero weakened assertions (both files' changes are additive or the five disclosed truth-preserving amendments).

The slice is a **PASS candidate for the artifact re-bind → push → PR → five checks → merge-gate review → merge under INT-145** chain, per STATE.md's exact-next-action.
