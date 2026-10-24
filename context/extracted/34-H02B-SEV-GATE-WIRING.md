# Record 34 — H-02 part 2 (b): the SEV gate wiring, the KB matrix, the activation — CLAIM-041, session 30

> STATUS: SESSION ENGINEERING RECORD (2026-10-24; intent refs INT-126/INT-127/INT-134/135/138; decision refs D-037/D-040/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 50. PRs this session: PR #76 (this slice; outcome recorded only after it happens). THE SEV record for this slice: `harness/runs/claim-041-h02b-sev-wiring/sev.json` (the first enforced record).

## 1. What the owner asked (verbatim — the standing chain)

> "lets get to work act as a world class systems engineer and a expert SWE.... setup g and cli and depdendcies and do not lose this token until the whole thing is done like long term final project" (turn 33 — preserved at record 32 §1's addendum)

The standing chain (INT-134/135/138) executes D-043's order: CLAIM-039 (LANDED, PR #74) → H-02 (part 1 LANDED as PR #75; this slice is part 2) → P3-00 → the phase gates.

## 2. Starting state

- Fresh main `fc8b32e` (PR #75's merge; post-merge run `40075690710` five green; make verify GREEN — 9 suites, 53/0, 24 known-bads).
- The SEV validator LIVE on main (harness/sev.py, ARV-SEV-001..008, its 35-group suite) but not enforced: no gate step, no KB matrix, no sheet section, no activation.

## 3. Task and scope

PLAN card H-02 part 2: wire the obligation into the gate (PR mode requires the report; selfcheck NOTEs it — the scope/claims pattern) + the KB-SEV matrix (001 missing / 002 malformed / 003 stale / 004 trace / 005 false-PASS / 006 placeholder / 007 identity / 008 the coordination-weakening form through the unweakened machinery source) + the ACTUAL-caller case (the real dispatcher, PR mode, end-to-end) + the trusted cases (18: a missing report refused by the base machinery; 19: a candidate gate omitting the step still refused — the structural protection) + the Proof-Sheet SEV section (TEMPLATES §6's rule) + the PLAN/LAWS activation (LAW-30: PLANNED → LIVE) + the bootstrap-scoped SEV record (the fresh-context reviewer authors the review fields; the identity limit stated).

## 4. Results

- The gate's step 8: PR mode invokes `sev.check_sev(slice_name, a.diff)` — the PUBLIC validator's wrapper, never an internal duplicate; selfcheck NOTEs (ARV-SEV-000).
- The KB-SEV matrix: 8/8 firing (32 known-bads total). KB-SEV-008 proves the coordination class: a stubbed own-validator + stubbed own suite still refused through the unweakened machinery source (the KB-RED-008 trusted-routing form; the case's env default unsets itself — SEV-5).
- The dispatch case: the missing report refused END-TO-END through the real dispatcher in a real clone (ARV-SEV-001 + never-selfcheck). The positive fixture modernized WITH the machinery (a born-valid sev.json + a real record binding — both inert at the predecessor, never before their time).
- The trusted cases 18/19: the base machinery enforces the obligation; a candidate that guts its own gate's SEV step is still refused (the candidate's own green is never the only evidence — F-006's form applied at this boundary).
- The Proof-Sheet SEV section: the report + reviewed-diff digests, the disposition, the findings with the open-P0/P1 count, the not-verified count — deterministic from the committed sev.json (ARV-PRF-004 unchanged).
- **THE FIRST ENFORCED SEV REVIEW (the fresh-context subagent round):** the reviewer (independent, read-only, did not implement the slice) reviewed the mid-slice wiring state and returned **BLOCKED** — a live-reproduced P1 (the declarations missing `test_record_machinery.py` — the third occurrence of the class this session, caught by the reviewer's own gate run) + four evidence-carrying P2s: the non-iterable proof_ids TypeError at the wired gate (named-disposition violation, fail-closed but unnamed), the printed digest excluding the SEV section it claims to cover, the unbound slice_id (the transplant edge), the KB-SEV-008 env default leaking. ALL FIVE ACCEPTED and fixed RED-first (red-02: each discriminating case observed at the pre-fix form — the proof_ids case DIED with the reviewer's exact traceback); the final record (sev.json) carries them RESOLVED with the fixes and dispositions.
- LAW-30: PLANNED → LIVE (the status cell, by pointer); PLAN's H-02 card marked COMPLETE with the observed acceptance.

## 5. Files/artifacts

- `harness/gate.py` (+the SEV step, the docstring's step 8, the sev import), `harness/proofsheet.py` (+the SEV section; the digest computed after it — SEV-3), `harness/sev.py` (+the proof_ids guard, the slice_id binding), `harness/known-bad/cases.py` (+KB-SEV-001..008), `harness/tests/test_gate_dispatch.py` (+the missing-report case, the positive fixture's SEV surface), `harness/tests/test_trusted_gate.py` (+tests 18/19, the stub's SEV surface + the finalize_stub_sev helper), `harness/tests/test_record_machinery.py` (+the sheet-section + digest-coverage cases), `harness/tests/test_sev.py` (+the SEV-2/SEV-4 cases), `harness/red-records.json` (the amendments), `LAWS.md`/`PLAN.md` (the activation), `CLAIMS.md`/`STATE.md`/`AGENTS.md`/`context/WORKLOG.md`, `harness/runs/claim-041-h02b-sev-wiring/` (scope, red-01/red-02, the 13 records, the sev.json, the sheet, notverified).

## 6. Commands (each alone, each exit read)

- At the test-only commit `5447477`: the three RED groups — the dispatch case (exit 1: the PR dispatches green with no report — the hole itself), trusted 18/19 (exit 1: nothing refuses), the machinery case (exit 1: the sheet silent) — red-01.txt.
- At the wiring `a668286`: all 9 suites green; the KB matrix 32/32; make verify GREEN (after the finalize-helper amendment — test_15's own catch: its legitimate addition left the stub's report STALE at the wired gate, ARV-SEV-003, the staleness rule working as designed).
- The reviewer round at `a668286` (the subagent's own runs, recorded in its returned record): the PR-mode gate refusing this very slice (ARV-SEV-001 — the designed mid-slice stop), the 32/32 matrix, the four suites green.
- At `da4c52b`: the reviewer's five fixes; red-02 (the discriminating cases at the stashed pre-fix form — the proof_ids crash, the slice-id transplant, the byte-identical printed digest); make verify GREEN.
- The proof set: 13 records at the head, every exit 0; the sev.json validated (VALID); the sheet derived (13 records + the SEV section); **the PR-mode gate GREEN over the actual diff with the SEV obligation enforced on this slice's own report**.

## 7. Evidence

- The proof set + the SEV record: `harness/runs/claim-041-h02b-sev-wiring/` (run-01..13, sev.json, proofsheet.md, red-01/red-02, notverified).
- The fresh-context reviewer's returned record: preserved verbatim in this session's transcript + the resolved form in sev.json (its not-verified items retained; its agent id recorded in the reviewer_context).
- This slice's PR: PR #76 (opened from `slice/claim-041-h02b-sev-wiring`; outcome records only after it happens).

## 8. Failures (honest)

- **SEV-1 (the reviewer's P1):** the declarations missed `test_record_machinery.py` — the third declaration-drift instance this session (claim-040's anchor repair, claim-041's machinery case, now this); each caught pre-merge (the gate, the reviewer). The class's lesson recorded: EVERY touched path declares in BOTH homes at edit time, never at gate time.
- **SEV-2/3/4/5 (the reviewer's P2s):** all real, all fixed with discriminating regressions; the proof_ids crash was the exact fail-closed-but-unnamed form the named-disposition contract forbids.
- **test_15's stale stub:** the fixture's legitimate addition moved HEAD and the wired gate refused the stale report — the test re-finalizes (the legitimate-candidate path: an addition is a new diff, the SEV re-authorizes over it).
- **The KB-SEV-008 machinery-root index:** the first draft double-joined `harness/` (FileNotFoundError at the matrix run); fixed to the repo root — the matrix run caught it immediately.
- **SEV-6 (the reviewer's second-round P1 — the finalize-sequencing drift):** the committed sev.json's reviewed_diff_sha256 bound the `da4c52b` tree; the artifacts commit `194a114` then changed seven COVERED paths (STATE/AGENTS/CLAIMS/LAWS/PLAN/WORKLOG/record-34), and the slice's own wired gate refused its own record with ARV-SEV-003 at the committed head — the staleness rule catching the builder's own finalize sequencing, live and deterministic (red-03.txt). The repair order the reviewer prescribed: the covered-path fixes land FIRST, then the record re-finalizes over the committed tree, then the re-derived sheet + the RECORDED PR-mode gate green — the record's own re-finalization changes only excluded paths, so the binding is stable (the anti-self-referentiality contract). The reviewer's judgment on the round: the review CONTENT was faithful (all five findings resolved, nothing dropped or downgraded), the record's BINDING was dishonest-by-staleness — both true; the first enforced SEV record caught its own author's drift.

## 9. Unverified items

- The bootstrap transition: the CI trusted job for THIS PR runs on the base `fc8b32e` (pre-wiring) — CI-enforced SEV begins with the NEXT slice's PR (the base carries the wiring once this merges). This slice's own enforcement: the local PR-mode gate (green) + the five-check CI run on the head.
- Identity separation is declared, never cryptographic (the same host/user; the separate grader remains).
- Base-side staleness rides strict=true; the same-host residual (Q10) unchanged.
- The reviewer's own not-verified items retained (its review state's honest limits).

## 10. Open decisions

- D-014, Q6–Q12 — unchanged; none closed by this slice (LAW-30's row and the SEV record cannot close owner questions).

## 11. Next action

P3-00 — freeze the RTM (SYS-01..SYS-11 traced to components/tests/proof), the interfaces, the state machines, the failure matrix, and the schema contract through the repository acceptance process (the roadmap's P3→P5 details are engineering elaborations adopted/corrected/rejected there — never silently promoted). Product schema migrations stay gated behind P3-00's acceptance. NO PAUSE.

## 12. Session close

- At this slice's content commit: the branch carries the RED commit `5447477`, the wiring `a668286`, the reviewer-round fixes `da4c52b`, and the records/artifacts commit. PR #76 opens from it; the merge + post-merge CI record only after they happen (the rule-4 close row carried by the next slice).
- The rig is up (FACT-001-exact); make verify GREEN at the final tree (9 suites, 53/0, 32 known-bads); the PR-mode gate GREEN over the diff with the SEV obligation enforced — the RECORDED green (run-14) captured after the SEV-6 re-finalization, never the authoring-state inference.
