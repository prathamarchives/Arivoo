# Record 30 — H-01C-EVIDENCE-PRIVACY (part 1: the evidence machinery) — CLAIM-037, session 29

> STATUS: EXECUTING (this slice at its PR; the record completes at the merge per rule 4)

## 1. What the owner asked (verbatim — no new owner turn this slice)

The standing do-not-stop chain (INT-131/132/134/135/136; the latest turn: "resumee working towards p3 and p4" — the continuous-execution directive; no stopping to report or ask until the phase gates). The card: PLAN's H-01c-evidence/privacy (F-007) — "evidence records certify what was actually observed."

## 2. Starting state

CLAIM-036 LANDED (PR #71 = `f34f000d`, merged 2026-10-23T13:43:05Z; post-merge run `39963533846` green; branch deleted 204; make verify 53/0 at the fresh main; the rule-4 close row carried by THIS slice's PR). The rig unchanged (the sixth env-reset's rig, DB up at :5433). 118 statused intents; the open register unchanged (D-014 + Q6–Q12, each blocking only its named dependents).

## 3. Task and scope

CLAIM-037 (H-01c-evidence/privacy part 1 — the evidence machinery cluster; F-007's named defect + the typed red records + fail-closed suite registration + record 29 §8's routed numbering rider). The canary-redaction + A16-narrowing cluster is CLAIM-038 (part 2) — routed, no pause between. Scope (the declarations): harness/gate.py, harness/red.py, harness/red-records.json, harness/proofsheet.py, tools/trusted_gate.py, harness/known-bad/cases.py, harness/tests/test_trusted_gate.py, harness/tests/test_record_machinery.py (NEW), Makefile, the shared-append files, this record, the runs dir.

## 4. Results

- **ARV-RED-006 (F-007's named defect, closed):** the gate's RED control resolves the TRUSTED PRIOR STATE (ARV_TRUSTED_BASE — set by trusted_gate.py's gate phase from the BASE checkout; origin/main as the local PR-mode fallback; unresolvable = a printed NOTE, never a hidden skip) and refuses a changed test whose typed amendments do NOT bridge the trusted prior digest to the current form — the bare make-red refresh (the candidate-supplied current_sha256) is the self-authorization hole, closed. KB-RED-008 proves it; trusted test_13 proves it end-to-end through the trusted phase; the KB probe's own ARV_TRUSTED_BASE baseline construction is the deterministic form.
- **ARV-RED-007 (the typed records, schema 2):** binding_commit/binding_sha256 (verified against git in every git context — a false binding refused), red_exit/red_code (the typed observed-red), red_unrecovered (the smash class's honest marker), typed amendments {prior, new, note, observed_at}. The 7 predecessor records migrated with values RECOVERED FROM GIT HISTORY and their own prose (the 4 missing bindings = the files' first commits, verified at migration time; gate_dispatch + mutation_floor carry red_unrecovered — their creation-time evidence was overwritten by the smash, never fabricated). trusted test_14 proves the false-binding refusal end-to-end.
- **ARV-RED-008 (fail-closed registration):** every harness/tests/test_*.py must appear in the ONE TESTS home (gate.py); red.py imports it (the one-fact-two-homes duplication red.py's own docstring named — closed); the discovery gap demonstrated live: make red at the RED-case commit updated only the SEVEN files its old tuple named — the new suite was INVISIBLE (the exact gap, caught as the first commit-message overclaim and corrected before any push).
- **ARV-PRF-006 + max-based numbering (the routed rider, record 29 §8):** the count-based writer stalled on one slot whenever a gap made count+1 name an existing record (observed live in CLAIM-036); the repaired writer numbers by max and refuses the unparseable/occupied context.
- **ARV-RED-009 (the explicit single-writer protocol):** red.py's atomic write (tmp+os.replace) + the changed-since-read refusal.
- **The NEW suite registered the honest way:** test_record_machinery.py — its whole first form was the RED set (observed 6 failures at 048aaa2, red-01.txt), its record minted with the OBSERVED red (--exit 1 + the code set), registered in TESTS, run by every gate — the registration flow dogfooded end-to-end.

## 5. Files changed

`harness/gate.py` (TESTS widened + the rewritten check_red_records: the baseline resolution, the typed validation, the registration enumeration, the chain check), `harness/red.py` (the typed writer: --exit/--code/--red-commit, typed amendments, the atomic write, the changed-since-read guard, the ONE TESTS home imported), `tools/trusted_gate.py` (ARV_TRUSTED_BASE plumbing), `harness/proofsheet.py` (max-based numbering + the unparseable/occupied refusal), `harness/red-records.json` (the schema-2 migration + the bridge), `harness/known-bad/cases.py` (4 probes), `harness/tests/test_trusted_gate.py` (tests 13/14 + build_stub's schema-2 3-commit shape), `harness/tests/test_record_machinery.py` (NEW), `Makefile` (the typed-mint passthrough), CLAIMS.md (the 036 close row + the 037 open row), STATE/AGENTS, context/WORKLOG.md (Task 46), this record, the runs dir.

## 6. The ACTUAL commands (each run ALONE, each exit read — nothing chained, nothing after a gate)

- The FALSE-RED probes BEFORE any fix: the 7 records' git bindings (3 MATCH, 4 missing — the revision-binding defect live), the trusted-gate predecessors' prose commits (212b1f8/00f3453 name predecessors that predate the files — the bindings recovered from the files' first commits instead, never fabricated)
- The RED captures at 048aaa2 (red-01.txt): the record-machinery suite → exit 1 (6 failures: the overwrite, the stall, the no-refusal forms); trusted tests 13/14 → exit 1 (no FAIL ARV-RED-006/007 in the phase output); the KB matrix → exit 1 ("the guard did NOT fire" × 4)
- The fix verification at 15a9c13: all EIGHT suites exit 0 (migrations, substrate, commands, gate_dispatch, mutation_floor, trusted_gate 14/14, claims_paths, record_machinery 4/4) + the KB matrix (the 4 new guards fire) + the verifier 53/0 + make verify GREEN (the selfcheck gate over the MIGRATED records with the origin/main baseline — the bridge verified by the check it was built for)
- The proof set: 11 records (the 8 suites + the known-bad matrix + the verifier + make verify), every exit 0, the sheet re-derived byte-identically (PASS ARV-PRF-004)
- The PR-mode gate: the first run REFUSED with 4 named codes (ARV-CLM-002 × 2 + ARV-SCOPE-002 × 2 + ARV-PRF-004 — the walls catching the undeclared Makefile + the undeclared new suite file + the missing sheet); the declarations widened honestly; the gate re-run

## 7. Evidence

- red-01.txt (at 048aaa2) — every RED case observed: the machinery suite's 6 failures, tests 13/14's discriminated failures, the KB matrix's 4 broken guards
- green-01/02/03 (at 15a9c13) — the machinery suite 4/4, the trusted suite 14/14, the KB matrix with the 4 guards firing
- the proof sheet (11 records, PASS ARV-PRF-004) + the notverified list (LAW-04)
- The pushed head's five-check run: observed in the PR (INT-104)

## 8. Failures (the honest ledger — each with its repair)

- **the first-commit overclaim (the #66/#69 class, caught pre-push):** the opening commit message claimed the new suite's record was "minted via make red" — FALSE at that tree (the old red.py's TESTS tuple did not know the file; make red updated 7 files, not 8). The make-red output read in full caught it; the commit AMENDED before any push with the honest note (the gap itself is the defect the slice closes — recorded, never hidden).
- **the vacuous-pass in the RED cases (the ARV-FLOOR-001 class, caught pre-fix):** tests 13/14 first PASSED at the predecessor — the KB runner's broken-guard line ("expected ARV-RED-006") satisfied the naive assertIn, and the phase's nonzero exit came from the BROKEN KB guards, not the target check. Discriminated to the gate's own refusal form ("FAIL ARV-RED-006") BEFORE the RED capture; the discrimination itself recorded in the red-records amendment.
- **the fixture iterations (three catches in the new suite, all pre-merge):** (1) the work tree lacked harness.adapters (proofsheet's import); (2) red.py's fixed form imports harness.gate — the work tree's module list widened (gate, scope, claims, known-bad, adapters); (3) the racing-writer hook wrote AFTER the read (the guard's re-read never saw the racing content) and red.main RETURNS its code (no SystemExit) — both fixture forms repaired, the suite re-run green. The lesson: a test's own fixture is part of its RED — a fixture that cannot observe the fixed behavior is a vacuous pass waiting to happen.
- **the stub-shape break (caught by the trusted suite itself):** the first build_stub restructure put the records in commit B before the declarations — the PR diff (HEAD~1..HEAD) then included the registry/ledger/Makefile → PROT-002/SCOPE-002 refusals on the positive tests. The 3-commit shape (suites → registry+declarations+records → the PR change) restored the original diff form; the trusted suite 14/14 after.
- **the walls' scope catches (the PR-mode gate working):** the Makefile edit and the new suite file were undeclared — ARV-CLM-002 + ARV-SCOPE-002 named both; the declarations widened in BOTH homes (scope.txt + the registry row).

## 9. Unverified items (LAW-04 — the slice's honest list)

See notverified.txt (the review layer's authority over bridged changes; the observation-is-a-claim-about-the-past limit; the non-git KB degradation; the two-process race residual; the CLAIM-038 routing).

## 10. Open decisions

None new (D-014 + Q6–Q12 unchanged; each blocking only its named dependents).

## 11. Next action

The merge once review-complete (D-042; every thread read + dispositioned BEFORE resolution — the standing fix), then CLAIM-038 (the canary-redaction + A16-narrowing cluster — the card's part 2), NO PAUSE; then H-02 (the SEV gate) → P3-00 (the RTM freeze) → P3-M0 ∥ P3-K0 → P3-01..09 → the Phase 3 exit gate → P4-00 → P4A..P4F → the Phase 4 exit gate.

## 12. Session close

[REPAIR 2026-10-23, the LAW-05 split — the PR gate's size refusal (ARV-SIZE-002: 467 > 400) worked exactly as designed]: the slice genuinely carried two behaviors (F-007's typed-record core + the routed numbering rider); the law's own repair is the split — the core stays in THIS PR (gate.py's RED control + the typed records + the registration + the migration; KB 008-012; tests 13/14/15; machinery cases 3/4/6), and the numbering rider (proofsheet.py's max-based repair + ARV-PRF-006 + machinery cases 1/2/5) moves to the part-2 claim with its RED already observed here (red-01/red-02) and re-observed at its own commit. The #72 review round's five fixes ALL stay in this PR (they are the core's own round).

(complete at this PR's merge — the merge SHA + the CI run IDs + the post-merge observations record in the CLAIM-037 close row, appended by the next slice per rule 4; this record needs no second pass)
