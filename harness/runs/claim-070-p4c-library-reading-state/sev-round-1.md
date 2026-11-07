# SEV round-1 — CLAIM-070 / P4-C slice one (the library + current-reading state)

- **Agent label:** agent-4f2b9d6a
- **Date:** 2026-11-07 (round 1, fresh context, adversarial)
- **Slice:** `slice/claim-070-p4c-library-reading-state` — the library membership list + the derived current-reading state over the LANDED substrate
- **Base:** `9c138a0` (origin/main, CLAIM-069's merged head) — **Head:** `a99da0b`
- **Chain:** `9c138a0` → `f8f38bd` (commit A: the post-#104 reconciliation + CLAIM-070 open + record 62) → `35fae66` (RED: the suite in RED form, machinery absent) → `b7ae0c1` (the typed red record bound to the RED commit) → `a99da0b` (GREEN: the two arms + the shared builders + the registry row)

## 1. What I ran

| # | Command / probe | Result |
|---|---|---|
| 1 | `rig.sh status` + chain check `origin/main..HEAD` | rig UP on 5433; chain exactly `9c138a0 → f8f38bd → 35fae66 → b7ae0c1 → a99da0b` (HEAD = a99da0b) |
| 2 | `python3 harness/tests/test_library.py` (twice) | **6/6 PASS (LIB-01..06), exit 0**; stdout sha256 = `c1f1435d…` = run-01/02/03's recorded digest exactly; stderr empty |
| 3 | `git archive 35fae66` → run the suite in the extracted tree | **exit 1, `FAIL ARV-TEST-000` (machinery-absent: both arms absent)** — byte-matches red-01.txt |
| 4 | Own scratch DB `arv_sev70_*` (bootstrap: `pg.create_scratch_db` → `migrate.py` → the real CLIs import/extract/save/capability), 30 adversarial checks | **30/30 OK** — (a) the twice-saved source shows the newest (ord=2) + **byte-equal** to get-position's line (also for once-saved and no-position sources); (b) re-extraction: saved offsets/ordinal/generation preserved, current=new, matches=false, the no-drift law re-held, a new save binds the current generation (ord=3, matches=true); (c) B sees only B's on both arms; B `--after` A's id leaks nothing; (d) 16 malformed bound combos → the typed ARV-QRY-004, exit 1, no header/rows; `--limit 1000` accepted; (e) the empty owner: exactly `["# api_version=1", "# more=false"]` on BOTH arms, exit 0, empty stderr; (f) the no-new-table count=0; (g) a ghost-uuid + the four uuid-variant `--after` forms continue the keyset cleanly; (h) `--limit 1` → 1 row + more=true on both arms; (i) the framing law holds (one JSON dict per body line, every row carrying api_version); (j) five hostile `--owner` strings safe (the `_read` escaping path); (k) a failed import (missing file) refuses and the library is unchanged; (l) the capability row P4-C + both verbs + "separate repo" + the CAP-03 regression row present; (m) the arm's saved-row set == the audit's distinct set. DB dropped |
| 5 | `make verify` at HEAD | **exit 0** — all suites GREEN (incl. `LIBRARY SUITE GREEN`), the gate GREEN, the canonical layer 54 checks/0 failures |
| 6 | Sweeps | `TODO/FIXME/XXX/placeholder/debug-print` in the new paths: none (the single hit is the docstring phrase "The {after}/{limit} placeholders" describing the SQL placeholders); no second position-row construction site (`_position_row` at query.py:490 is the single home, called at :534 and :564); no SQL-injection shape (`--owner` rides `_read`'s escaping; hostile owners `O'Brien` / `A'; SELECT 1; --` / backslash all answer an empty header+more=false, never stderr) |

## 2. Findings

**Zero open P0/P1/P2. Five P3 notes (non-blocking):**

- **P3-1 (F1) — the five measured-set records are on disk but untracked at HEAD.** `run-01..05.json` carry `commit: a99da0b` and exist in the run dir; git does not track them at the GREEN head. This is consistent with the chain's own declared order (record 62 §3: measured set → SEV round(s) → artifact finalize → artifact re-bind → push) and the same mid-chain state existed at CLAIM-069's round 1. Judgment: not a defect; the artifact re-bind MUST commit the records before the PR.
- **P3-2 (F2) — LIB-02's refusal pin is one line short of the prose.** The pin asserts exit 1 + `FAIL ARV-QRY-004:` + no header, but not the repair-hint line's presence. I probed all 16 malformed combos (0/1001/abc/-1/1.5/non-uuid/empty/injection-shaped `--after`) on both arms: every one prints the FAIL line + the indented repair hint, exit 1, zero rows/header. The substance holds.
- **P3-3 (F3) — the default page size is only indirectly pinned on the new arms.** Any default ≤1000 would pass LIB-01..04 with 5 fixtures. It is structurally shared (one argparse loop, one DEFAULT_LIST_LIMIT constant) and BND-05 pins the default exactly on the older arms, so a drift would break those pins. Indirect but real.
- **P3-4 (F4) — the make-verify output digest is not byte-deterministic.** The two records at the same commit carry different output_sha256; my own fresh run differs again (timestamps, scratch-db names). Both records (and mine) show exit 0 + GREEN gate + canonical 54/0. The LIB suite digest IS byte-reproducible (my run matched run-01/02/03 exactly). The digest field for make-verify runs attests exit + content class, not bit-reproducibility.
- **P3-5 (F5) — the `--after` cursor accepts every `uuid.UUID` form.** Braced, `urn:uuid:…`, no-hyphen, uppercase all normalize to the canonical lowercase form before interpolation — the keyset cursor is safe but wider than the strict hyphenated spelling. No breach of the typed-refusal contract (non-uuid still refuses); no injection (the interpolation only ever sees `str(uuid.UUID(...))`).

**Explicitly sought and NOT found:** no second position-row construction site; no SQL-injection shape; no TODO/FIXME/XXX/placeholder/debug prints in the new paths; no `arv library/current_reading/reading_state` relation; no stray output between header and marker; no cross-owner leak through either arm or through a cross-owner `--after` cursor; no crash on a valid-but-unlisted ghost uuid.

## 3. Probes

**(a) The no-second-path law (full read of the implementation).** `_position_row` (query.py:476-494) is the position answer's ONE construction home; `_get_position` (:519-520) and `_reading_state` (:548-550) both print through it with the same serializer (`json.dumps(..., ensure_ascii=False)`). Behaviorally: on my own scratch DB, every get-reading-state row — saved (twice-saved newest, once-saved), no_position_saved, and the re-extracted mismatch case — is byte-equal to get-position's own line for the same source. The `id|pos|cur` split is exact: the payload is row_to_json over ints + a uuid (no free-text field, so no pipe can occur inside it).

**(b) The bounds + the cursor law.** 16 malformed combos across both arms: `--limit 0 / 1001 / abc / -1 / 1.5`, `--after` non-uuid/empty/injection-shaped — every one refuses with exit 1 + `FAIL ARV-QRY-004:` + the repair hint + zero rows/header. `--limit 1000` accepted; `--limit 1` → 1 row + more=true; the keyset walk unions to the full set, monotone, no dups; a ghost uuid (valid, unlisted) continues the keyset cleanly; the four uuid spellings normalize safely.

**(c) The isolation + the empty forms.** Owner B (one own source) sees exactly B's rows on both arms; B's `--after` with A's id yields nothing of A's; the empty owner answers exactly `["# api_version=1", "# more=false"]` on both arms, exit 0, empty stderr — never silence, never a leak. Five hostile `--owner` strings (quote/backslash/SQL-shaped) all ride the `_read` escaping to an empty clean answer.

**(d) The membership derivation.** A failed import (missing file) refuses ARV-IMP/ARV-CMD-class and leaves list-library unchanged — the dead-letter is the journal's, never the library's. The arm's saved-row set equals the audit's distinct positioned-source set ({a1, a2} on my DB). information_schema carries no library/current_reading/reading_state relation; capability surfaces carries the P4-C row naming both verbs + "separate repo", and the source-open/position row (CAP-03 regression) stands.

## 4. The sha chain (closed)

`binding_commit = 35fae66`, `binding_sha256 = 7e342b74…9630` = the sha256 of the RED form at that commit (verified via `git show`) = `current_sha256` = the HEAD worktree file; git blob hashes identical; `git diff 35fae66..HEAD -- harness/tests/test_library.py` is EMPTY and `amendments: []` — zero amendments, the RED contract held as written. The RED itself reproduced by me at the archived 35fae66 tree (exit 1, ARV-TEST-000, byte-matching red-01.txt; the observation tree f8f38bd is machinery-identical to 35fae66 — the declared precedent class). The measured set: run-01..05 on disk record commit a99da0b (= HEAD) — 3× the suite exit 0 (digest reproduced byte-exactly by my own run) + 2× make verify exit 0 (reproduced exit 0 by my own run); the untracked-state and digest-variance notes are P3-1/P3-4 above.

## 5. Verdict

**PASS** — zero open P0/P1/P2. The five P3 notes are routed/recorded in notverified.txt (notes 1-9). The slice proceeds to artifact finalize + re-bind with the run records committed.
