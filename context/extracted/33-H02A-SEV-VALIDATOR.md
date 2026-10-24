# Record 33 — H-02 part 1 (a): the SEV validator module — CLAIM-040, session 30

> STATUS: SESSION ENGINEERING RECORD (2026-10-24; intent refs INT-126/INT-127/INT-134/135/138; decision refs D-037/D-040/D-041/D-042). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 49. PRs this session: PR #75 (this slice; outcome recorded only after it happens).

## 1. What the owner asked (verbatim — the standing chain)

> "lets get to work act as a world class systems engineer and a expert SWE.... setup g and cli and depdendcies and do not lose this token until the whole thing is done like long term final project" (turn 33, the credential-resume turn — preserved at record 32 §1's addendum)

The standing chain (INT-128/131/134/135: no stopping to report or ask; continuous work through Phase 3 and Phase 4) executes the ordered sequence (D-043): CLAIM-039 (the reconciliation, LANDED as PR #74) → **H-02** → P3-00 → the phase gates. This slice is H-02's part 1.

## 2. Starting state

- Fresh main `7bcea00` (PR #74's merge; post-merge run `40070999202` five jobs green; local `make verify` GREEN 53/0).
- H-01c complete (PRs #71/#72/#73); the H-01b trusted floor live (the two-runner split, all five required checks bound; the mutation floor 39 cases; the trusted KB machinery routing ARV_TRUSTED_KB_MACHINERY).
- H-02's activation precondition MET (the #66 binding observed with evidence — PLAN's sequencing note); the documented order (H-01c-authority → H-01c-evidence/privacy ×2 → H-02) satisfied by the merged state.

## 3. Task and scope

PLAN card H-02 part 1: the SEV validator itself — the standard-library module `harness/sev.py` (LAW-30's mechanical form) + its focused suite `harness/tests/test_sev.py` + the fail-closed TESTS registration + the typed red mint. The named refusal codes frozen in the suite's docstring BEFORE the implementation. The gate wiring, the KB-SEV matrix, the dispatch/trusted integration, the Proof-Sheet section, and the PLAN/LAWS activation updates are the part-2 slice (CLAIM-041) — one behavior per slice (LAW-05/D-026). Until part 2 lands, the module is exercised by its suite and labeled not-mechanically-enforced (the card's own transition label).

Non-scope: no product code, no migrations, no decision closures, no PLAN/RTM changes (P3-00 owns the freeze), no Phase 3 entry.

## 4. Results

- `harness/sev.py` (320 lines): the PUBLIC `validate_report` + the gate wrapper `check_sev` (invokes the public validator — never an internal duplicate) + the binding digest procedure (`reviewed_paths` / `reviewed_diff_sha256`: the changed files' content at HEAD over merge-base...HEAD, excluding ONLY the slice's own `harness/runs/<slice>/` artifacts — code under review NEVER excluded; a deleted path digests its deletion token; adding a report never changes its own binding — the anti-self-referentiality contract).
- The A09 repairs at this boundary: FULL 64-hex digest syntax (prose is not SHA-256); typed run-record fields (command/exit_code/commit/output_sha256/recorded_at); binding commits must exist in git history (the KB-RED-011 class — git's inability to show a commit IS the refusal); placeholder limitation lists rejected (whitespace/'none'/'n/a' — an explicit honest statement required); malformed HISTORICAL records preserved, never forged (the validator only refuses).
- The refusal matrix: ARV-SEV-001 (missing) / 002 (malformed: unparseable JSON, wrong schema_version, missing/mistyped fields, prose digests) / 003 (stale: base movement via the merge-base field; candidate movement via the recomputed digest — changed code after review) / 004 (trace: empty or unresolvable INT/SYS ids, dangling proof ids, empty v_model wings) / 005 (false-PASS: BLOCKED; open P0/P1 under PASS) / 006 (placeholders) / 007 (the same declared builder/reviewer — the identity LIMIT stated: a differing string is not cryptographic independence) / 008 (malformed proof/run records).
- RED→GREEN held: the RED observed at the test-only commit `3a9e595` (the module ABSENT: ten failing case groups, exit 1 — the target refusals unprovable, never silently green; the typed mint with the observed exit/code); GREEN at the fix commit `98a0e8b` (29 PASS / 0 FAIL, exit 0 — every named code discriminated).
- The suite's own in-slice catch: the proof-id binding initially required exact filenames (`run-01.json`) while reports cite stems (`run-01`) — the positive cases failed, the matrix caught it immediately, repaired in-slice (stem ≡ filename equivalence).

## 5. Files/artifacts

- `harness/sev.py` — the validator (NEW; D-037/LAW-30).
- `harness/tests/test_sev.py` — the focused suite (NEW; 24 case groups; 314 lines).
- `harness/gate.py` — the TESTS registration (+1 line; ARV-RED-008's discovery class closed for the new suite).
- `harness/red-records.json` — the typed mint for test_sev.py (binding `3a9e595`, observed exit 1) + the test_15 amendment (prior → new sha, the reason in the note).
- `harness/tests/test_trusted_gate.py` — the test_15 anchor repair (the tail-anchored TESTS form broke on the first legitimate suite addition; the anchor moved to the stable first entry; identical semantics).
- `harness/runs/claim-040-h02a-sev-validator/` — scope.txt, red-01.txt, the proof set, the Proof Sheet.
- `CLAIMS.md` (the CLAIM-040 open row + CLAIM-039's rule-4 close row), `STATE.md`, `AGENTS.md`, `context/WORKLOG.md` (Task 49).

## 6. Commands and external actions (ACTUAL — each alone, each exit read)

- At the test-only commit `3a9e595`: `python3 harness/tests/test_sev.py` → exit 1 (the ten absent-module refusals — red-01.txt).
- `make red --note ... --exit 1 --code "ARV-SEV-001..008 all unprovable at the predecessor"` → the typed mint (9 files scanned; the new record added).
- At the fix commit `98a0e8b`: `python3 harness/tests/test_sev.py` → exit 0 (29 PASS / 0 FAIL).
- The working-tree transient: `make verify` → exit 2 (test_gate_dispatch's 3 clone-at-HEAD artifacts + the trusted suite's test_15 anchor — both resolved by the committed states: the dispatch cases re-verified green inside `make verify` at `9c0d753`).
- `python3 harness/tests/test_trusted_gate.py` → OK (17/17 after the anchor repair).
- `make red --note <the amendment>` → the typed amendment (ARV-RED-006's authorized form).
- `make verify` at `9c0d753` → GREEN (all 9 suites, the verifier 53/0, the gate selfcheck, 24 known-bads firing).

## 7. Evidence

- The proof set: `harness/runs/claim-040-h02a-sev-validator/` (the N-record capture at the content head; PASS ARV-PRF-004 at the PR-mode gate).
- The typed red record: `harness/red-records.json["harness/tests/test_sev.py"]` (schema 2; binding `3a9e595`; observed exit 1; red-01.txt).
- This slice's PR: PR #75 (opened from `slice/claim-040-h02a-sev-validator`; its merge outcome records only after it happens).

## 8. Failures (honest)

- **The proof-id stem binding (the suite's own catch):** the first implementation required exact filenames; the suite's positive cases failed (ARV-SEV-004 on `run-01`); repaired to stem ≡ filename equivalence in the same slice.
- **test_15's tail anchor:** the trusted suite's own case anchored the TESTS tuple's mutable last entry; the first legitimate suite addition (this slice's) broke it before any fixture ran. Repair: the anchor moved to the stable first entry + the typed amendment. The fragility class (a fixture anchoring a mutable registry shape) is recorded here for the next suite addition.
- **The uncommitted-tree transients:** the dispatch suite's 3 failures at the working tree were clone-at-HEAD artifacts (the clone carried the committed red-state; sev.py and the mint were not yet committed) — resolved by the commits, re-verified inside the full make verify.
- **The commit-A script's duplicate-row transient:** the CLAIMS edit script asserted AFTER its write; the first (assert-failing) run had already written the rows, and the re-run duplicated the closed/open rows — caught by the registry check itself (ARV-CLM-007/002) within the minute, deduplicated, registry GREEN. The lesson recorded: an edit script must be idempotent or assert before writing.

## 9. Unverified items

- The gate does NOT yet enforce the SEV obligation (part 2, CLAIM-041: the gate step, the KB matrix, the dispatch/trusted integration, the Proof-Sheet section, the activation updates). Until then: not-mechanically-enforced (the card's label) — the independent-review discipline continues.
- Identity separation is DECLARED, not cryptographic (ARV-SEV-007's refusal is the same-string check; fresh-context execution and the separate grader remain the protocol — the card's independence-limit paragraph).
- Base-SIDE additions do not move a merge-base; the strict=true required-status binding forces up-to-date branches at merge (base movement forces a new head and revalidation) — stated, never claimed closed.
- The same-host/same-user residual (Q10, the mutation floor's BOUNDARY) is unchanged and untouched by this slice.

## 10. Open decisions

- D-014, Q6, Q7, Q8, Q9, Q10, Q11, Q12 — unchanged scopes; this slice adds none and closes none. The roadmap's P3→P5 details remain a D-022 planning artifact until P3-00 accepts them.

## 11. Next action

CLAIM-041 — H-02 part 2: the gate's SEV step (PR mode requires the report; selfcheck NOTEs it) + the KB-SEV-001..008 matrix (the public validator + the ACTUAL gate caller + the coordination-weakening form via the trusted-machinery routing) + the dispatch/trusted integration cases + the Proof Sheet's SEV section + the PLAN/LAWS activation updates (LAW-30: PLANNED → LIVE once the known-bads are green in CI) + this slice's own SEV record (the bootstrap-scoped transition review, independently checked). Then P3-00. NO PAUSE.

## 12. Session close

- At this slice's content commit: the branch carries the RED commit `3a9e595`, the fix `98a0e8b`, the anchor repair `9c0d753`, and the record/state commits. PR #75 opens from it; the merge and post-merge CI record only after they happen (the rule-4 close row carried by the next slice).
- The rig is up (FACT-001-exact); `make verify` GREEN at `9c0d753` (9 suites, verifier 53/0, 24 known-bads).
