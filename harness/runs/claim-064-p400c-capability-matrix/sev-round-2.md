# SEV round-2 — CLAIM-064 / P4-00c (the format capability matrix + extraction readiness) — the round-1 repair verification

- **Agent label:** agent-1bc56354 (fresh-context Systems Engineering Verification, round 2 — the round-1 retry)
- **Date:** 2026-11-06T06:50Z
- **Slice:** CLAIM-064 — P4-00c: the format capability matrix + extraction readiness (harness/capability.py + the README rewrite + query.py's per-family hints + test_capability.py)
- **Base (origin/main):** `647f3cb18fd877acd08689f195b61269e742fd8a` (PR #98 merge, CLAIM-063)
- **Head under review:** `b3a5d1cc3d02e143974bec33de7d3171e68878e0` (branch `slice/claim-064-p400c-capability-matrix`, working tree clean)
- **Round 1:** agent-ee8ed9dd, BLOCKED (sev-round-1.md) — 1×P1 + 2×P2 + 4×P3. The repair commit under review is `b3a5d1c` (7 files: the anchored driver removed, capability.py +9/-1, test_capability.py +66, record 56 §2 fix, the red-record amendment, run-06, sev-round-1.md itself).

---

## 1. What I ran (commands + exit codes)

| Command | Exit | Note |
|---|---|---|
| `git show --stat b3a5d1c` + the full diff | 0 | the repair diff read in full: tools/trusted_gate_anchored.py −206; capability.py `fail_reason`; test_capability.py TEXT2 + the failed-state fixture; record 56 §2 wording; red-records.json amendment; run-06.json |
| `git ls-files \| grep -c anchored` | 0 (7 hits) | all 7 are the pre-existing `harness/runs/claim-014-anchored-name-repair/` run directory (at base, NOT in the diff) — zero `tools/` anchored-driver paths |
| `git diff --name-only origin/main...HEAD \| grep -c tools` | 1 (0 hits) | **no `tools/` file in the slice diff** |
| `ls /home/z/my-project/verification/anchored/trusted_gate_anchored.py` | 0 | present, 12914 bytes, executable — the driver now lives OUTSIDE the worktree, immune to `git add -A` |
| `timeout 300 python3 harness/tests/test_capability.py` | 0 | **CAP-01..06 all PASS (6 PASS)** — the amended suite with the derivation corpus + the planted-RAISE failed-state fixture |
| Live scratch-DB probe (below) on `arv_sev2c_13418_947390052` (created via `pg.create_scratch_db('sev2c')` + `migrate.py` exit 0; **dropped after, verified absent**) | — | 5-paragraph corpus → `measure`: `state=ready, passages=5, coverage=1.0`; planted RAISE → second extract **exit 1** (ARV-EXT-003); trigger+function dropped → `measure`: **`state=failed` with `"fail_reason": "ARV-EXT-003: ERROR:  P0001: X"`** at exit 0; the first source still `ready/5/1.0` |
| `SLICE=claim-064-p400c-capability-matrix GATE_DIFF=origin/main timeout 400 make gate` | nonzero (make Error 1; gate exit 2) | **all 25 suites PASS on the real stack** (incl. capability/extract/boundary/contract) + every KB guard PASS; refuses ONLY: **ARV-PRF-004** (the Proof Sheet absent — proofsheet.py's inline `ARV-PRF-002` consolidated per gate.py:439-449, the H-01a-R design) **+ ARV-SEV-001** (no sev.json) — exactly the two pre-finalize classes; **ARV-SCOPE-002/ARV-CLM-002 GONE** |
| the red-records chain print | 0 | `prior 5b959d2c23f1 → new f54f792f8c7d`; current file sha256 `f54f792f8c7d…` — **new_sha256 == the live file digest**; binding_commit `2f4d3ef…` (the RED commit, red_exit 1 / ARV-TEST-000) |
| `sev.reviewed_diff_sha256('origin/main','claim-064-p400c-capability-matrix')` | 0 | **`1fac5b54db5b6315b0dc0a4d5de714bfda1783394d0bec0a1ab00ce8acb83c56`** |
| `grep -rn trusted_gate_anchored` over the repo | 0 | see F1 verdict — no committed file depends on it; every hit is historical narrative or the round-1 report itself |

No repository source file was modified; nothing committed or pushed; my scratch DB dropped (verified); temp corpus/blob dirs removed. The only write is this report.

---

## 2. Per-finding verdicts (round-1 numbering)

### F1 (P1 — the re-committed `tools/trusted_gate_anchored.py`) — **REPAIRED**
- The file is gone from the index and from the slice diff: `git diff --name-only origin/main...HEAD | grep tools` → 0 hits; `git ls-files | grep anchored` → only the pre-existing claim-014 run directory (at base, untouched by this diff).
- The working copy now lives at `/home/z/my-project/verification/anchored/trusted_gate_anchored.py` — outside the worktree, so no future `git add -A` can sweep it in again (the round-1 failure mode).
- The gate confirms at the PR boundary: round 1's dual refusal (ARV-SCOPE-002 + ARV-CLM-002 on both the candidate and the trusted gate) is GONE — the PR-mode `make gate` now refuses only on the two pre-finalize artifact classes.
- Reference sweep: the remaining `trusted_gate_anchored` mentions in committed files are (a) pre-existing-at-base history (CLAIMS.md's CLAIM-020 row, red-records #64 notes, PLAN.md, records 23/25, the claim-021/061/062/063 run records, `tools/trusted_gate.py`'s own CI-usage docstring) and (b) this slice's legitimate documentation (record 56 §1's #98-close narrative, sev-round-1.md — the finding itself). Zero are execution dependencies; the only trusted-gate paths invoked by any suite are `tools/trusted_gate.py` (pre-existing at base).

### F2 (P2 — measure reports the LATEST generation over a readable current one) — **PROPERLY ROUTED**
- The routing is honest. extract.py's own contract holds — my live probe's failed-extract refusal itself states "the previous current generation STAYS current (never a partial presentation)… the previous current generation was never touched" (and round 1 verified live that the reads keep serving the current generation's passages). The source never becomes unreadable; only the readiness row's vocabulary cannot name the serving generation.
- The latest-generation semantics is disclosed in-tree where the row is defined: capability.py's `_measure` docstring says "the latest generation, its passages"; the README frames `failed` as "the last attempt failed" and `building` as "an extraction in flight" — the states are attempt-scoped by their own documented letter. The fuller fix (a serving-generation/readable field) is genuinely P4-A/B's read-position work, where the reader client consumes readiness; the routing is recorded in the repair commit message with the notverified disclosure due at finalize.
- Residual obligation (for the finalize, not a new finding): the notverified.txt must carry the F2 disclosure when it lands.

### F3 (P2 — the unpinned `failed` state + the docstring's promised `fail_reason`) — **REPAIRED**
- The suite now pins it: the amended CAP-02 plants the EXT-10-form RAISE (`BEFORE INSERT ON arv.passage WHEN (NEW.ordinal = 2)`) over a FRESH source, asserts extract exit 1 with ARV-EXT-003, then (trigger+function dropped, both psql exits pinned) asserts `measure` answers `state=failed` at exit 0 **with the named ARV-EXT-003 reason in the row**.
- The module keeps the docstring's promise: `capability.py:119-124` reads `COALESCE(fail_reason,'')` for the failed generation and sets `row["fail_reason"]` (falling back to `"unnamed"`).
- Verified live end-to-end on my scratch DB: the planted-RAISE extract → exit 1; after the drop, `measure` → `"state": "failed", "fail_reason": "ARV-EXT-003: ERROR:  P0001: X", "passages": 0, "coverage": 0.0` at exit 0. The suite is GREEN (6 PASS).
- The red-record amendment is honest about the epistemics: "no product-side RED existed for F3/F4 (the failures were coverage gaps, not product defects — the fail_reason field is the additive GREEN riding the same repair)" — the correct LAW-11 treatment for a coverage-gap repair.

### F4 (P3 — the single-corpus ready-row pin) — **REPAIRED**
- The amended suite measures a SECOND, different corpus (TEXT2, five blocks) and pins `passages=5, coverage=1.0` alongside the first corpus's `3/1.0` — a conditional hard-code of the first corpus's values can no longer pass CAP-02.
- Cross-checked out-of-suite: my own 5-paragraph corpus answered `passages=5, coverage=1.0` (and the first source re-measured `ready/5/1.0` after the failed second extract — derivation intact).

### F5 (P3 — run-record provenance: runs recorded at a non-final head) — **PROPERLY ROUTED**
- The class is unchanged and disclosed: run-06.json records `make verify` exit 0 at commit `570a23c` (the pre-repair head) — the measurement was taken on the repaired working tree (recorded 06:10:26Z, the repair commit assembled 06:10:41Z), the same label-vs-tree convention as run-01..05 (the claim-058/062/063 precedent). The repair commit message carries the routing: "the finalize re-binds at the final head."
- Obligation for the finalize (standing, already routed): re-record the measured set — or mint a run-07 — at the FINAL content head, especially since sev-round-2.md (this file) and the proofsheet/sev.json will move the head again.

### F6 (P3 — record 56 §2's phantom "timing class") — **REPAIRED**
- Verified in the repair diff: "the passage count, the coverage, the timing class" → "the passage count, the coverage fraction over the actual bytes". The record now names exactly what the row carries; the binding CLAIMS.md row never promised timing.

### F7 (P3 — the unreadable-blob `ready`/`coverage=0.0` form) — **PROPERLY ROUTED**
- `capability.py:130-135` keeps the class by design (blob unreadable → `text_len=0` → coverage honestly 0.0, the passage counts stand), disclosed in the code comment; the user-facing disclosure is assigned to the notverified at finalize, and the routing is recorded verbatim in the repair commit message ("the unreadable-blob ready/coverage=0.0 form — disclosed in the notverified"). The README's capability section does not mention this edge — acceptable for a rig-class blob-store-corruption extreme, with the finalize disclosure as the routed remedy.
- Obligation for the finalize: the notverified must carry the F7 (and F2) disclosures.

---

## 3. New findings

**None at P0/P1/P2.** Observations below are notes, not findings:

- **F8-note (informational):** the gate's summary tallies `ARV-PRF-004` while the inline proof-sheet line prints `ARV-PRF-002` — by-design consolidation (gate.py:439-449 catches proofsheet.py's SystemExit; the H-01a-R comment documents it). Both are the same pre-finalize proof-sheet class; no action.
- **F9-note (housekeeping, outside the tree):** a migrated scratch DB `arv_sev2_7053248` (20 `arv` tables) sits on the cluster. It was NOT created by this round (my own `arv_sev2c_13418_947390052` was dropped and verified absent; the name does not match the harness `create_scratch_db` `prefix_pid_ts` pattern) — likely an earlier session's manual probe. Harmless to the slice; noting for hygiene.
- **F10-note (informational):** `capability.py:120-121` interpolates `gid` into SQL un-escaped — `gid` is a server-generated uuid read from `arv.extraction_generation` in the same measure call, never user input (the user-supplied `--source` is escaped at line 91). No injection surface.
- **F11-note (the digest's own movement):** the digest recorded below is the diff digest at head `b3a5d1c` WITHOUT this report file. Per the digest-binds-LAST discipline (the standing precedent), the finalize must re-bind after the SEV report, proofsheet, and sev.json land — the same obligation every prior slice carried.

---

## 4. The computed digest

`sev.reviewed_diff_sha256('origin/main', 'claim-064-p400c-capability-matrix')` at head `b3a5d1c`:

```
1fac5b54db5b6315b0dc0a4d5de714bfda1783394d0bec0a1ab00ce8acb83c56
```

(Subject to the F11-note: re-bind at finalize after the artifacts land.)

---

## 5. Verdict

Every round-1 P1/P2 is repaired or honestly routed, verified at the real boundary with fresh eyes:

- F1 (P1) REPAIRED — the anchored driver out of the index, out of the diff, out of the tree; both round-1 scope refusals gone at the PR-mode gate.
- F2 (P2) PROPERLY ROUTED — attempt-scoped semantics disclosed in the docstring + README; the source stays readable (extract.py's own contract, re-observed live); the serving-generation field is P4-A/B's.
- F3 (P2) REPAIRED — the failed state pinned by the planted-RAISE fixture + `fail_reason` in the row, verified live and in-suite.
- F4 (P3) REPAIRED — the derivation corpus.
- F5 (P3) PROPERLY ROUTED — the finalize's digest-binds-LAST re-record.
- F6 (P3) REPAIRED — record 56 §2 corrected.
- F7 (P3) PROPERLY ROUTED — the notverified disclosure at finalize.
- New findings: none blocking (four informational notes).

The amended CAP suite is GREEN (exit 0, 6 PASS); the full `make gate` runs all 25 suites GREEN on the real stack and refuses ONLY on the two expected pre-finalize artifact classes (ARV-PRF-004/PRF-002 + ARV-SEV-001); the red-record amendment chain is intact (new_sha256 == the live file digest, chained from the RED-commit sha through the typed amendment); the repo carries no dependency on the removed driver.

**DISPOSITION: PASS**

*— agent-1bc56354, 2026-11-06T06:50Z. Scratch DB `arv_sev2c_13418_947390052` dropped (verified); temp dirs removed; no repository source file modified; nothing committed or pushed; this report is the round's only write.*
