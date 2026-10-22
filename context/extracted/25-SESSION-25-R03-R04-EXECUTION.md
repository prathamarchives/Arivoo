# 25 — SESSION 25: THE R-03/R-04 REPAIRS + THE PHASE-3 ENTRY PATH (the directive's canonical order resumes)

> STATUS: SESSION ENGINEERING RECORD (2026-10-22; the session's intent refs: INT-129/INT-130/D-042's routing; D-041). Historical
> process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 36.
> PRs this session: (in progress — CLAIM-028/R-03 first; R-04, the one-liner slice, H-01c-authority/evidence, H-02 follow per the
> STATE-exact next-action order.)

## 1. What the owner asked (verbatim — owner turn 26, 2026-10-22)

> i said do not stop. until phase 4-5 is done.. continue following the the directive... ghp_[REDACTED — a GitHub PAT, redacted at
> ingestion per the standing D-025/INT-092 redaction class; the INT-127 leading-credential precedent] now we must go for the real
> product execute phase 3 and 4 with following the directive and aligned goal. build real backend as a world class engineer and
> systems artitecht. # ARIVOO — EXECUTION DIRECTIVE: PHASE 3 → PHASE 4 REAL PRODUCT
>
> [The directive follows in full — the mission (working product behavior, not more planning documents, infrastructure
> demonstrations, mock implementations, or a green test suite that does not prove the product works), §1 the actual starting
> state (read the canonical documents; verify PR #62 = f190bfa20aa4897384f3cf8d54ea883c5c7461e3 is an ancestor of current main
> rather than assuming; reconcile documentation against merged code and executed evidence), §2 the canonical execution order
> (R-03 → R-04 → the ledger one-liner slice → H-01c authority/evidence → H-02 the SEV validator/gate → P3-00 → P3-M0/P3-K0 →
> P3-01..P3-09 → the Phase 3 exit gate on the final main revision → P4-00 → the Phase 4 backend capabilities → the Phase 4 exit
> gate against the real end-to-end product workflow), §3 Phase 3 durable capture (P3-00 freeze through P3-09 export/restore),
> §4 Phase 4 reader and journal backend path (P4-00 through P4F; backend-only; a mocked API is not proof), §5 the mandatory
> per-slice verification and iteration (claim-before-work; tests first; the real production boundary; the Proof Sheet from
> actual run records; review before merge; never hand-edit a report to make a gate pass), §6 the architecture boundaries
> (authoritative vs derived; the command kernel as the mutation boundary; Q11/Q12 owner decisions preserved at their exact
> scopes), §7 blocker handling (read the exact decision records; never broaden a local blocker; never make an owner decision on
> the owner's behalf), §8 the definition of success (a backend that demonstrably supports the intended product workflow) —
> preserved in full in the session context; the standing byte-level-diff limit applies to this embed.]
>
> (End of owner turn 26. Not minted as a new INT- at intake: the turn is the CONTINUATION directive for INT-129/D-042's routed
> work — R-03/R-04 were already routed by turn 24 and remain READY; the turn's new content (the phase-4-5 "do not stop"
> reaffirmation + the real-product execution directive) is carried by this record §1 and the STATE re-derivation at the session
> close. The trailing credential is redacted per the standing class.)

## 2. Starting state

- **Live truth (re-observed at preflight, 2026-10-22):** `origin/main` = `f190bfa20aa4897384f3cf8d54ea883c5c7461e3` — **PR #62
  IS an ancestor of current main** (it IS the HEAD: the merge commit itself). The local clone was STALE at session start
  (`963356b`, session-23 close); fetched and pulled. The merge's outcome, recorded here per AGENTS/STATE's own requirement
  ("the merge outcome records only after it happens"): **merged BY THE OWNER (`prathamarchives`, 2026-10-22T11:02:24Z)** with
  reviewDecision REVIEW_REQUIRED at merge — the single-actor structural absence (the PR author is the owner's own account)
  closed by the owner's direct command (INT-130, record 24 §13's owner-authorized path), exactly as predicted; the protection
  setting unchanged (1 approving review, strict, admins included); post-merge CI green (run 39767587070 at f190bfa); 0 open PRs.
- **Preflight runs (before any edit):** the rig REBUILT AGAIN (the environment reset corrupted the data dir — `pg_notify`
  gone, the fifth rebuild, the FACT-001 pattern; fresh `initdb` from the surviving Debian 17.11-0+deb13u1 packages,
  `make migrate` applied 3, `make verify-schema` OK) → `make verify` GREEN at fresh main `f190bfa` (3 harness suites + 13/13
  known-bads + gate selfcheck + canonical 51/0). `tools/verify_selftest.py` 30/30 GREEN; `tools/isolation_check.py` local GREEN;
  the canonical count 112 statused intents verified in the preflight read.
- **The next authorized slice (STATE's exact-next-action, confirmed live):** R-03 (the isolation-tool hardening: the G-51
  Greptile findings on #51 in 4 card items) — PR #62's merge is the precondition it waited on.

## 3. Task and scope

**CLAIM-028 — R-03 the isolation-tool hardening** (PLAN's R-03 card, the 4 repair items; the 5 Greptile findings G-51-1..5
routed by record 24 §32):

1. `isolation_check.py`'s `_open_regular_nofollow` lacks O_NONBLOCK (G-51-1 — the same FIFO-swap hang class the mutation
   floor's B3 repair closed in its own sibling helper) → the non-blocking open BEFORE the ISREG check.
2. `isolation_selftest.py`'s `_copy_bounded` walk silently drops unreadable subtrees (G-51 — the copytree it replaced
   reported them) → fail closed as a sanitized FixtureBuildError.
3. Directory creation charges no budget (G-51) → directories count against the fixture's entry budget.
4. B5/B6 discard the exception message (G-51) → the sanitized fixed message asserted directly.

Declared scope (scope.txt): `tools/isolation_check.py`, `tools/isolation_selftest.py`,
`harness/runs/claim-028-r03-isolation-tool-hardening`, `CLAIMS.md`, `STATE.md`, `AGENTS.md`, `context/WORKLOG.md`, this record.
Non-scope: the gate/scope/known-bad/workflow repairs (R-04's 9 items — the next slice, disjoint), the ledger one-liner slice,
H-01c-authority/evidence, H-02, P3-00. The honest widening, declared: the suite's OWN `_open_regular_nofollow` sibling carries
the identical FIFO-swap hang class (item 1's class, both helpers repaired + pinned).

## 4. Results — R-03 LANDED (the 4 repairs, RED-first)

- **RED-first (commit 4cc19d7, the test-only commit over predecessor f190bfa):** the 4 new tool-contract cases observed FAILING
  on actual wrong behavior — **B7** (the checker's bounded open vs a FIFO: the probe child HUNG, killed at the 10s timeout —
  "the open is BLOCKING (the FIFO-swap hang class, R-03(1)); O_NONBLOCK is missing"); **B8** (the suite's own sibling helper:
  the identical hang); **B9** (an unreadable source directory: "raised nothing — the unreadable subtree was SILENTLY DROPPED
  from the fixture copy at the predecessor (R-03(2): os.walk without onerror) — a false-complete fixture is the false-green
  class"); **B10** ("raised nothing — directory creation charged NO entry budget at the predecessor (R-03(3)): 9 directories
  constructed under a 4-entry budget"). All 22 checker cases (v2.1 + v2.2) PASSED at the same run — the new cases discriminate
  the named defects without weakening any existing assertion. The B5/B6 message pins (R-03(4)) pass at the predecessor BY
  DESIGN (the wrapper's fixed message predates them — the defect was the CASES' type-only assertion); their discriminating
  power proven separately (red-02.txt: a scratch-corrupted wrapper — path leak, fixed diagnostic gone — fails B5 AND B6 with
  the named reason).
- **GREEN implementation (commit f64001e):** O_NONBLOCK added to BOTH helpers' opens (the FIFO open returns at once; the
  open-fd ISREG check refuses it — B7/B8 now prompt refusals); `_copy_bounded`'s walk carries `onerror` fail-closed (the
  sanitized FixtureBuildError, never a silently-dropped subtree — B9); every created directory charges the entry budget
  (B10); the B5/B6 pins live. **The suite 28/28 GREEN** (22 checker + 6 builder/tool-contract), **`make verify` GREEN 13/13**,
  **the 30/30 mutation floor GREEN**, **the checker local GREEN**, and **the coordinated-weakening rehearsal GREEN** (the
  BASE's v2.2 suite over this candidate checker — the B1..B6 + 18 v2.1 cases all green against the O_NONBLOCK change; the
  anchored copy used for the rehearsal is CI-runtime state, never committed — the claim-020/021 lesson, held this time).
- **The gate in PR mode over the real diff GREEN** at the content head: scope coverage (every diff path inside the declared
  scope), claims (the open row covers the branch), red records, lint, deps, the 15/15 known-bad matrix, and the Proof Sheet
  re-derives byte-identically from 9 run records (3 harness suites + the isolation suite + the canonical verifier + make
  prove's standard set + make verify at the fully-committed content HEAD).
- **The 13 READY findings' ledger:** R-03's 5 findings (G-51-1..5 → the 4 card items) are now FIXED with stable regressions;
  R-04's 8 findings (+1 ratchet task) remain READY on their card — the next slice.

## 5. Files changed

- `tools/isolation_check.py` — v2.3 note + O_NONBLOCK in `_open_regular_nofollow` (the checker's own bounded-open helper).
- `tools/isolation_selftest.py` — v2.3 note + O_NONBLOCK in the suite's own sibling helper + `_copy_bounded`'s walk
  `onerror` fail-closed + the directory entry-budget charge + the B5/B6 fixed-message pins + the B7/B8/B9/B10 cases
  (`_WRAPPER_REFUSAL`, `_BOUNDED_OPEN_PROBE`, the skip-declared B9 root guard).
- `harness/runs/claim-028-r03-isolation-tool-hardening/` — red-01.txt (the B7-B10 RED observation), red-02.txt (the message
  pins' discriminating power), scope.txt, notverified.txt (LAW-04), run records + proofsheet.md (assembled, never hand-edited).
- `CLAIMS.md` — CLAIM-028's open row + CLAIM-027's rule-4 closed row (the PR-#62 merge outcome recorded).
- `context/WORKLOG.md` — Task 36. This record — §§1-7 (R-03). `STATE.md`/`AGENTS.md` — the re-derivation/phase-line repair.

## 6. Commands and external actions (ACTUAL — never reconstructed)

- `git fetch origin` → `963356b..f190bfa main` (the stale clone repaired; PR #62 verified as HEAD, ancestor-of-main trivially)
  @ preflight.
- `gh pr view 62` (API) → mergedAt 2026-10-22T11:02:24Z, mergedBy prathamarchives, reviewDecision REVIEW_REQUIRED, 27 reviews;
  `gh pr list` → 0 open; `gh run list` → run 39767587070 success at f190bfa. (gh v2.102.0 reinstalled — the env reset removed
  it; the PAT stored outside the repo, redacted at ingestion per D-025.)
- The rig rebuild: `initdb` (fresh data dir; the corrupted `pgdata` set aside, not deleted) → `make migrate` → 3 applied →
  `make verify-schema` → "verify OK: 3 migration(s) applied, checksums match" @ the rebuilt rig.
- `make verify` @ f190bfa → exit 0 → GREEN 13/13 + canonical 51/0 (the preflight baseline).
- `python3 tools/isolation_selftest.py` @ 4cc19d7 (tests-only, predecessor implementations) → exit 1 → the 4 named REDs
  (B7/B8/B9/B10; red-01.txt).
- The B5/B6 discriminating probe (a scratch copy in /tmp, the wrapper's message corrupted; never a repo file) → B5/B6 FAIL
  "the sanitized refusal's fixed message is WRONG" (red-02.txt); scratch removed after the probe.
- `python3 tools/isolation_selftest.py` @ f64001e → exit 0 → 28/28 GREEN.
- `make verify` + `python3 tools/verify_selftest.py` (30/30) + `python3 tools/isolation_check.py` @ f64001e → all exit 0.
- The coordinated-weakening rehearsal: `git show f190bfa:tools/isolation_selftest.py > tools/isolation_selftest_anchored.py`
  → run → exit 0 (the base's suite green over the candidate checker) → the anchored copy REMOVED (CI-runtime state).
- `make prove SLICE=claim-028-r03-isolation-tool-hardening` + `--record` (6 explicit) → 9 run records → ARV-PRF-003/004
  byte-identical re-derivation; `make gate SLICE=... GATE_DIFF=f190bfa` → GREEN (the walls pass over the real diff; the
  first GATE_DIFF attempt with the literal "f190bfa...HEAD" form refused with ARV-DIFF-001 — the correct form is the bare
  base ref, exactly what the Makefile's contract says; recorded, never papered over).

## 7. Evidence

- The red evidence: harness/runs/claim-028-r03-isolation-tool-hardening/red-01.txt (the raw RED output + the named four) and
  red-02.txt (the pins' discriminating power) — both bound to the test-only commit 4cc19d7 over predecessor f190bfa.
- The green evidence: 9 run records + the assembled proofsheet.md at the content head (the 3 harness suites, the isolation
  suite 28/28, the canonical verifier 51/0, make verify 13/13); the cw-rehearsal (base suite over candidate checker) exit 0.
- The registry: CLAIMS.md's CLAIM-028 open row (the branch slice/claim-028-r03-isolation-tool-hardening) + CLAIM-027's closed
  row with the merge outcome; the walls' own gate run GREEN in PR mode over the diff.
- CI: the PR's three required checks (canonical-layer, head-tools, harness) — the run IDs recorded in §12 at the merge.

## 8. Failures (the honest ledger — each with its repair)

- The env reset destroyed the rig AGAIN (the fifth time: `pg_notify` gone; the data dir permissions reset first — the chmod
  700 repaired the FIRST refusal, then the missing-subdir refusal forced the fresh initdb; the corrupted dir set aside for
  autopsy, not deleted) — the FACT-001 rebuild pattern, recorded.
- The env reset also removed `gh` (reinstalled v2.102.0) — recorded; the PAT re-stored outside the repo.
- Two syntax slips in the new cases' first draft (a mismatched bracket in b7/b8's return) caught by the suite's own syntax
  check before any run — the red-first discipline applied to the tests themselves.
- The gate's GATE_DIFF form error (the literal "f190bfa...HEAD" is not a base ref; ARV-DIFF-001 refused it — the wall doing
  its job on my own invocation) — re-run with the bare base ref, GREEN.
- (§8 continues with the R-04 slice's own catches in the sections below when they land.)

## 9. Unverified items (LAW-04 — the slice's honest list)

- The notverified.txt list (the mid-scan FIFO race's determinism window; the O_NONBLOCK-with-live-writer moot case; B9's
  under-root skip; the B5/B6 pins' pass-at-predecessor BY DESIGN; the directory-budget arithmetic pinned at the refusal, not
  the walk order) — the canonical copy in harness/runs/claim-028-r03-isolation-tool-hardening/notverified.txt.
- No fresh technical verifier and no SEV — the pre-H-02 discipline (H-02 is the SEV card; its activation is the next-but-one
  slice after R-04 + the one-liner).

## 10. Open decisions (each blocks only what it names)

- D-014 (calculation engine scope), Q6 (research-transcript status), Q7 (semantic-spike budget), Q8 (extraction corpus —
  synthetic default), Q9 (repository visibility), Q10 (token/workflow-tamper hardening), Q11 (Work/Source identity — no
  auto-merge, no identity uniqueness until ratification), Q12 (blob backend/staging/recovery) — unchanged, each blocking only
  its named dependents; turns 20-26 add no new owner question and close none.
- The Phase-3 entry sequence remains gated on: R-04 → the ledger one-liner slice → H-01c-authority/evidence → H-02 → P3-00.

## 11. Next action

**R-04** (the gate/scope/known-bad/workflow repairs — 9 card items: the stderr-only stub's completion line, S4c `!cancelled()`,
the trusted driver's failing-suite output tail, scope.py's tab-splitting/bytes-mode/rename-endpoints repairs, KB-CLM-006's
synthetic probe rows, KB-SCOPE-006's own README.md declaration, and the closed-table-duplicate ratchet with its own KB case) —
as CLAIM-029, RED-first, disjoint files from R-03 (declared scope: harness/gate.py, harness/scope.py, harness/known-bad/*,
tools/trusted_gate.py + the claim/record/state append-shapes). Then the ledger one-liner consistency slice, then
H-01c-authority, H-01c-evidence/privacy, H-02, then P3-00.

## 12. Session close

(in progress — the R-03 PR's merge SHA, CI run IDs, and the post-merge observations record here at the close)
