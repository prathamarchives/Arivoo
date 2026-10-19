# PLAN — Arivo

One phase deep (NG-04). The next phase is planned only when current-phase evidence says what's needed. Predicates close phases, not dates. The slice cycle (OPERATING-MODEL §2) is the unit of execution inside every phase. The growth model (OPERATING-MODEL §6) defines the operating model per stage: how the repo runs, how its memory updates, and how its failures heal at each level of maturity. The law activation map is in LAWS.md (the proactive set and the live-at phase of each law).

## Guardrails from day one (proactive set — never deferred)
Isolated credentials · protected gates · real database test · idempotent writes · immutable evidence · owner scoping · independent state read. Everything else arrives through the ratchet, when it protects a concrete contract. The harness must never postpone the product (P-17). Full doctrine: ENGINEERING.md §4–§10.

## Phase 1 — Execution environment and trust (COMPLETE, 2026-10-14; extended same day by owner turn 10 — LAYER 1.2, INT-100/D-027)
Purpose: the repo is safe to build in, and the trust model is real.
- **W-01 Walls**: protect main (PR-only, no force push, applies to admins); CODEOWNERS on protected paths (deliberately deferred — rides Q-IDENT option (b): with a single identity it would convert every standing-authorization merge into an owner web-UI approval, violating P-06/P-15; session 12 §3 surface #11); required check restricted to the expected source application (mechanism verified + FACT entry — not assumed from docs). Two-stage: rules land now, required-check binding when CI runs.
- **W-02 Host contract + bridges (host-agnostic since D-026, 2026-10-14; Q1 closed by D-028 — agent-agnostic by design)**: the wall defines the **Host Contract** (what any supported host must load — the canonical read order; GLOSSARY) and the **bridge pattern** (a host bridge imports `AGENTS.md`, never duplicates it — one fact, one home). GLM-host verification is behavioral: fresh-context sub-agent proofs (session 13: authority-conflict PASS, unresolved-decision PASS — a fresh session loads canonical instructions and navigates them under pressure). File-import bridges (e.g. `CLAUDE.md` for Claude Code, Codex CLI's `AGENTS.md` conventions) land at host adoption with FACT entries verified on installed versions — instantiation at adoption, never a wall or a phase (INT-097/D-028).
- **W-03 Isolation check**: redacted verification that the agent environment exposes no personal secrets — conditions printed, values never.
- **W-04 CI**: Linux runner, `verify` workflow, owner-controlled; remote CI is authoritative (D-009).
Exit (OBSERVED 2026-10-14, session 13): a broken build cannot merge (probe PR #7: VER-802 red run 115684453018 + merge API 405 "Required status check \"canonical-layer\" is failing\""); a fresh host session loads canonical instructions (verified — GLM-host behavioral proofs, session 13 §6; file-import hosts at adoption); the sandbox is proven secret-free (isolation green, re-run 2026-10-14); verify runs green on a trivial truth (PR #6: both jobs green); a deliberately broken build fails the gate (probe PR #7, observed). Phase 1 is COMPLETE — Phase 2 begins.

**Layer 1.3 (2026-10-14, owner turn 13 — INT-118/D-034; GRADUATED 2026-10-15 by owner turn 14's resequenced gate, D-035: Slices 10/11 landed (PRs #21/#22, 11B 96/100); the candidate-tool gate repaired (PRs #24/#25 — the coordinated-weakening floors, both CI jobs required); the integrated fresh-context proof at the final content SHA passed 96/100 — the seven-part evidence table, record 17 §4.3): the final two slices + the graduation gate.** The owner-forwarded Arivoo review extends Phase 1 once more before any Phase 2 work: **Slice 10 — isolation and diagnostics** (permission-boundary inspection: mechanically prevented vs. detected vs. agent-discipline; the isolation check's false-green classes repaired — embedded remote-credential becomes a failure; mode-required config; end-to-end redaction proof; full negative+positive synthetic matrix) and **Slice 11 — real host bridges and automated gates** (one canonical instruction source; bridges only for hosts in use; the base-anchored isolation checker runs in `canonical-layer`; a fresh-context real-host bounded-task proof with handoff). Then the **Phase-1 graduation gate**: one integrated fresh-context proof on the actual final main SHA — protected PR workflow confirmed, authority recovered from the entry point, state found without a full reread, usable handoff, checker rejects known-bads, isolation gate independently anchored, a fresh agent completes authorized work with evidence. **Phase 2 stays blocked until both slices pass and the graduation gate is satisfied** (the review's words, record 16 §1). Phase 2 = the minimum trustworthy harness/build loop; Phase 3 keeps the name "first real behavior" — the phase boundary is never confused by naming.

**Layer 1.2 (2026-10-14, owner turn 10 — INT-100/D-027):** the exit evidence above remains observed and standing; the owner extended Phase 1 with one more layer — slice 4 (the STATE five-area contract), slice 5 (session handoffs: event-typed worklog/session-record policy + standardized fields), slice 6 (the selective read path + the bounded cold-start proof), plus the replication kit (INT-108). The layers execute in order, each with its own proofs; each is planned as it executes. Phase 1 (layer 1.2 included) completes when the slices' pass criteria hold; Phase 2 still begins only with the owner-approved execution plan. Layer 1.3 (above) supersedes the "Phase 2 still begins" sequencing for the current arc: the turn-13 slices and the graduation gate come first.

## Phase 2 — Minimum trustworthy harness (LANDED 2026-10-16, session 18: owner turn 16, INT-121/D-036 — the 2026-10-16 review's S1–S4 with Rider A folded, executed as PRs #28–#32; the exit criteria below OBSERVED MET via CI at every merge, the uncoached fresh-context clean-clone re-run, and the harness wall probe; evidence: record 18 §4/§7/§12)
One real-stack test · Proof Sheet generated from run records · scope enforcement · representative known-bads for the proactive set only. NOT required before product code: the full constraint system, all architecture checks, every kernel primitive, every planned known-bad.
**Layer 2.1 (LANDED, D-036 — PR #28: S1 real-stack rig + migrations v0 (forward-only, versioned, baseline; Postgres per D-032; a CI service container; a version-parity FACT) · PR #29: S2 the substrate-convention table (owner/actor/provenance/revision/tombstone; append-only triggers with named codes; RLS; a second read role for independent reads) · PR #30: S3 the idempotent command path + crash-injection tooling (command registry; idempotency key; single transaction; ack strictly after commit; kill-at-each-point recovery) · PR #31+#32: S4 the gate assembly, split into two bounded slices by its own SIZE check (Proof Sheet generated from run records, never hand-edited; SIZE/SCOPE enforcement; the proactive-set known-bads — scope breach, protected-path edit, skipped test, hand-written Proof Sheet, lowered threshold, missing red record, test edited after red, unapproved dependency; every failure with a named code; the harness CI job constructed with evidence and bound after a green run is observed — the W-01 stage-2 pattern, executed: required checks = [canonical-layer, head-tools, harness]; the wall probe PR #33 observed the named-code RED + the merge refusal).** Grounded defaults (D-036, each overridable): Python standard library only (zero third-party dependencies); `psql` as the DB client — the app path and the independent verifier differ by role and code path (LAW-13's spirit); test-rig trust auth (ephemeral test databases only). S5/S6 spikes stay owner-gated (Q7/Q8; the review's Riders B stay [P]).
Exit: the harness proves scope, evidence immutability, idempotency, and independent reads on a real database; deliberately broken builds fail with named codes.

## Phase 2 close-out and Phase 3 entry controls

**Phase 2 S1–S4 remains COMPLETE (D-036, session 18). Do not rebuild it or rewrite its evidence.** The current state is documented in STATE.md and record 18. Before product implementation, run the current-SHA preflight below. If a check fails, create one defect slice and repair only that defect. Do not reinterpret the Phase 2 exit or launch a broad harness rewrite.

### P2-CLOSE — current-SHA preflight

At the exact main SHA from which implementation will branch, record the SHA and working-tree state, then run these commands in the intended build environment:

1. python3 tools/verify_canonical_layer.py
2. python3 tools/verify_selftest.py
3. python3 tools/isolation_check.py
4. python3 tools/isolation_selftest.py
5. make harness-health
6. make verify-schema
7. make verify

The local database must be the real PostgreSQL rig, not a mock. `make verify` already runs the fast test suite, the known-bad matrix, the integrated gate, and the canonical verifier; do not rerun those same suites separately unless diagnosing a failure. Do not print environment variables or secrets. Save the actual command, exit status, revision, and material result in the slice run record. Run remote required checks on the same proposed revision. A green remote run at an earlier SHA is historical evidence, not proof that a future PR or new local environment is green.

The current Makefile does not provide the real-run or falsify targets described in parts of the operating-model target surface. Do not claim either target ran until it exists and has actually run. Implement any missing command through a bounded card with red-first tests.

### H-01 — base-anchored harness floor

**Reason:** record 18 §9 identifies a residual: the base-anchored floor for harness tools themselves is not yet proven. Do not reopen Phase 2 S1–S4. Add a single bounded wall-construction slice that tests the candidate harness against a trusted base-controlled floor.

**Scope:** the trusted runner, required assertions, and expected failure classes come from the base revision. Candidate tests may add coverage but cannot replace the base floor. Missing trusted files must fail closed; never silently fall back to a candidate version. Bind any new required check only after a green real pull-request run has been observed, using the recorded W-01 stage-2 procedure.

**Tests to commit first and observe RED:** candidate gate bypass/always-pass; removal or skip of a declared suite; coordinated weakening of the gate and its candidate tests; absence of a trusted base file; a known-bad mutation that changes behavior but would otherwise pass. Every refusal must have a stable reason code.

**Acceptance:** all attacks are rejected by the trusted floor in CI; the positive path is green; the new check is observed in the real PR workflow; a separate fresh-context verifier reproduces the attacks; the Proof Sheet records base/head SHAs, outputs, and not-verified items.

**Security boundary:** do not claim workflow-tamper protection is fully mechanical while Q10 remains open. A PR that can change the workflow definition can alter which steps run. Q10 remains an owner-controlled token/permission decision; this plan does not mint tokens or change credentials.

**Limits:** one behavior, current LAW-05 size limits, zero unapproved dependencies. If the slice exceeds its limit, split it without weakening the limit. Stop after three failed cycles (LAW-16).

### H-01a — ready card: PR dispatch/Git fail-closed (CLAIM-005; owner turn 20, INT-125/D-039; audit findings A01/A02/A10)

**One behavior:** a pull request can no longer reach a green required `harness` check without its PR obligations (scope/size, branch-claim/coverage, Proof Sheet) being judged, and no untrusted CI event field can alter or terminate the dispatch.

**Subject files:** `.github/workflows/verify.yml`, `harness/gate.py`, `harness/scope.py`, NEW `harness/dispatch.py` (the YAML-inline dispatch logic extracted so the ACTUAL dispatcher is executable and judgable — a YAML run block cannot be imported by tests; the workflow calls the same command CI runs), NEW regression `harness/tests/test_gate_dispatch.py`. **Requirement refs (≤3):** H-01 (this slice's own gate ID) + INT-125/D-039 (authority) — one requirement; defects A01 (selfcheck fallback bypass), A02 (event-field interpolation), A10 (unchecked git → empty diff).

**Named codes, frozen before code:** `ARV-DISPATCH-001` (hostile/invalid branch metadata — the derived slice name fails identifier validation; refuse before any gate run); missing scope/claim/sheet in PR mode refuse with the EXISTING semantically-correct codes (ARV-SCOPE-001 / ARV-CLM-005 / ARV-PRF-002 — never a selfcheck fallback); `ARV-DIFF-001` (a git diff/rev-parse operation exits nonzero — the gate refuses, never an empty-diff vacuous pass); `ARV-DIFF-002` (the declared base has no merge-base with HEAD — invalid base/shallow graph; refuse).

**Design decisions:** `github.head_ref`/`GITHUB_EVENT_NAME` reach the script via the workflow `env:` block ONLY (never `${{ }}` interpolation inside `run:`); the slice-name identifier validates `^[A-Za-z0-9._-]+$` after the `slice/` strip (fail-closed ARV-DISPATCH-001); `scope.diff_paths`/`diff_stats` check returncodes + merge-base existence (ARV-DIFF-001/002); the harness job fetches full main history (`fetch-depth: 0` on checkout or `git fetch --unshallow`-equivalent) so the merge-base check is decidable in CI; PR mode with a missing `scope.txt` invokes the gate in PR mode (the gate's own ARV-SCOPE-001 refusal is the correct behavior — the `else` selfcheck branch is DELETED); `harness/tests/test_gate_dispatch.py` joins gate.py `TESTS` + red.py `TESTS` (the red-first obligation covers the new suite; it is DB-free so the gate can run it everywhere).

**RED-first tests (observed RED on the actual predecessor before implementation):** hostile branch metadata (quote/dollar/semicolon-breakout forms — Git-legal names) must exit nonzero with ARV-DISPATCH-001 and the gate must NOT have run to a selfcheck pass; PR mode with no `scope.txt` must invoke the real gate and refuse ARV-SCOPE-001 (assert the selfcheck path is unreachable — the A01 class); unclaimed branch → ARV-CLM-005; missing sheet → ARV-PRF-002; invalid base revision → ARV-DIFF-001; no-merge-base (unrelated history) → ARV-DIFF-002; main-push selfcheck stays green (the `--no-diff` surface unchanged); deletion/omission of the new suite itself → ARV-GATE-001/ARV-RED-001 (registration proven).

**Acceptance:** the new regression runs directly + all predecessor suites + 13/13 known-bads green; `python3 harness/gate.py --slice claim-005-h01a-pr-dispatch-git-fail-closed --diff origin/main` GREEN at the candidate; remote CI three-check green at the PR head; fresh technical verifier (pre-H-02 discipline, identity limits stated) + slice Proof Sheet from actual run records + A01/A02/A10 dispositions recorded in record 20 §4.

**Non-goals:** no gate semantics changes beyond the named repairs; no `real-run`/`falsify` targets; no workflow-tamper token work (Q10 stays owner-gated); no isolation-architecture changes (H-01b's floor is its own card); no weakening of any existing check.

### H-01a-R — ready card: the bounded H-01a completion checks (owner turn 21, INT-126/D-040; the directive's §2 residuals)

**One behavior:** an invalid diff base produces ONE consolidated nonzero named gate refusal — no uncaught traceback, no claim-coverage path that assumes a valid diff; a hung git subprocess is a named refusal; and the missing-sheet regression proves the exact code, with hostile metadata that is actually ref-legal.

**Observed defects (reproduced/static, session-21 preflight — record 21 §2):** (1) `harness/gate.py:191` recomputes `scope.diff_paths(a.diff)` for claim coverage OUTSIDE the `GitRefusal` handler — with the base deleted, the gate prints one clean `ARV-DIFF-001` in `check_diffs` then crashes with an uncaught traceback (exit 1 by process failure, the refusal printed twice); (2) `test_gate_dispatch.py:141` asserts the broad string `ARV-PRF`, not the card's exact `ARV-PRF-002`; (3) the hostile-branch fixture contains spaces — not `git check-ref-format`-legal (parser-boundary fuzzing, not an observed Git-ref path); (4) `_git`/`ensure_merge_base` use `subprocess.run(timeout=...)` whose `TimeoutExpired` propagates unnamed.

**Named codes, frozen before code:** `ARV-DIFF-001/002` (existing); NEW `ARV-DIFF-003` (a git subprocess timeout — a named refusal, never an unnamed crash; added to `GitRefusal`'s docstring and the dispatch doc; deterministically tested by simulating `TimeoutExpired`, never by requiring a real hang). The missing-records/sheet refusals assert the EXACT stable codes the implementation prints — corrected by the tightening itself: a slice with NO run records fires `ARV-PRF-001` (proofsheet.assemble runs before the disk check; the original ARV-PRF-002 assumption held only the WITH-records condition, now proven reachable by its own dedicated fixture), and the refusal must land in the gate's consolidated disposition (ARV-PRF-004 in the summary), never a mid-run SystemExit. The assemble-before-disk-check ordering is recorded as a static finding for H-02's boundary (proofsheet machinery).

**Subject files:** `harness/gate.py`, `harness/scope.py`, `harness/tests/test_gate_dispatch.py`, `harness/red-records.json` (amendment), `harness/runs/claim-XXX-h01a-completion-checks` (the slice's evidence). **Requirement refs (≤3):** H-01a + INT-126/D-040.

**RED-first tests (actual wrong behavior observed first):** the consolidated-refusal case through the REAL dispatcher in a real clone with the base ref deleted — asserts exactly one ARV-DIFF-001 line, NO traceback, exit nonzero, and that the branch-claim check did not run on the invalid diff (the ARV-CLM-000 skip note is the observable); the timeout cases (simulated `TimeoutExpired` from `_git` and `ensure_merge_base` → `ARV-DIFF-003` named refusal); the no-records PRF case asserts `ARV-PRF-001` exactly + the gate's consolidated summary (RED: the predecessor exited via mid-run SystemExit, skipping the summary); the with-records/no-sheet fixture proves `ARV-PRF-002` reachable (passes at the predecessor — precision addition, recorded as such, never claimed RED); the relabeled fuzz case asserts `git check-ref-format` REJECTS the old fixture (proving it is fuzzing, honestly labeled); NEW genuinely-legal hostile case — a `check-ref-format`-accepted branch name carrying a no-space breakout payload → `ARV-DISPATCH-001` + no execution + no side-effect file (passes at the predecessor; regression protection for the realistic class).

**Acceptance:** the full suite green (all predecessor cases unchanged — assertions only tightened/added, never removed; red record amended additively per LAW-11); local gate PR-mode GREEN; CI three-check green at the PR head; dispositions recorded in record 21 §4.

**Non-goals:** no dispatch redesign; no new gate semantics beyond the named consolidation; no Q10 claims; no fixture-environment coupling (all cases self-contained).

### H-01b — ready card: the trusted candidate-tool execution floor (A03; owner turn 21, INT-126/D-040; the directive's §4 contract)

**One behavior:** the base-controlled floor genuinely observes whether candidate tools reject the base-controlled mutations — candidate code never runs inside the trusted judge's process, and a candidate cannot make omitted, crashed, or fake-completed cases appear green.

**Current defect model (confirmed static, record 20 §2; to be reproduced RED):** the anchored mutation suite (`tools/verify_selftest.py`, CI's `verify_selftest_anchored.py` path) imports the candidate `verify_canonical_layer` IN-PROCESS. Candidate import-time code can `SystemExit(0)` before cases run, replace verdict objects, or modify later-copied anchored tools in the writable candidate checkout after checksum verification. A successful process exit is not proof that every expected case ran; a copied-file hash at one time is not a runtime trust boundary.

**Contract (all required):** (1) the base-owned runner + critical dependencies stay outside candidate-controlled writable/import resolution — candidate code is never imported inside the trusted runner process; (2) each candidate mutation case executes in a fresh disposable candidate fixture/CHILD PROCESS with a resettable boundary — one candidate side effect cannot affect later cases; the base runner compares actual expected outcome, child exit status, and an explicit per-case completion manifest/case count (never any-exception/printed-string/exit-0 acceptance); (3) candidate code is exercised AS candidate code, but cannot replace the base runner, mutate later anchors, or cause omitted cases to appear green — fixtures are disposable and trusted-runner/integrity inputs verified before every case; (4) existing base semantics/counts preserved unless a deliberate separately-justified changeset updates the contract and tests — no test deletion, no mutation-coverage reduction; (5) CI runs the real hardened base floor over a candidate PR with an auditable base SHA/digest and candidate input revision; this does NOT supply OS-level sandboxing or solve Q10 (the residual boundary is stated in the card's acceptance, never claimed away).

**Subject files (current, named):** `tools/verify_selftest.py` (the suite — becomes the trusted-runner driver), NEW `tools/mutation_runner.py` (the base-owned child-process runner + manifest contract) or equivalent inside the suite, `.github/workflows/verify.yml` (the canonical-layer job's floor steps run the real hardened floor), NEW `harness/tests/test_mutation_floor.py` (registered in gate/red TESTS), plus the anchored copies mechanism (`verify_selftest_anchored.py`) if its anchoring needs the digest-recording step. **Requirement refs (≤3):** H-01 (the floor) + A03 + INT-126/D-040.

**RED-first tests (committed first, meaningful RED observed — each exercises the real runner path CI uses):** candidate module `SystemExit(0)` at import; always-green standalone candidate entry point; candidate import/exec attempts to edit a later anchored judge/dependency (post-checksum mutation); candidate crash mid-cases; incomplete case results (manifest count mismatch); candidate printing expected words/codes but returning success; coordinated candidate-verifier + candidate-owned-test weakening; missing trusted runner/input (fail-closed); a positive valid candidate run completing ALL expected cases. The acceptance oracle = the trusted runner's per-case actual-outcome report, not a test subprocess that merely didn't crash.

**Acceptance:** all adversarial fixtures rejected by the trusted floor through the SAME integration path CI uses; the positive path green; base semantics/counts unchanged (30 mutations still enforced); CI three-check green at the PR head with the real hardened floor active on the PR; fresh technical verifier inspects the diff/evidence independently (pre-H-02 discipline, identity limits stated); Proof Sheet from actual runs; the residual boundary written down (same-host CI ≠ malicious-code sandbox; Q10 untouched).

**Non-goals:** no OS-sandbox claims; no candidate-identity/blockchain machinery; no weakening of the existing 30-mutation set; no registry/parser changes (H-01c's cards own those).

### H-01c-claims — card: claim parser/exclusivity truthfulness (A11; the directive's §4 split, disjoint from H-01b)

**One behavior:** the registry checks fail closed for malformed ACTIVE registry state. Confirmed defects (session-21 source read, record 21 §2): a missing `## Open claims` header silently yields zero rows (no ARV-CLM-001 fire — the `_COLS` check only greps the whole text); truncated/malformed competing rows (`< 8` cells) vanish from validation; INT reservations compare numerically for the ledger check but as strings for duplicate detection (`INT-125` vs `INT-125` with a leading zero collide as integers, not strings); duplicate claim IDs and duplicate branch ownership are unchecked (`check_branch_claim` takes the first match); `_shared` uses `startswith(s)` so lookalikes (`STATE.md.py`) count as shared; declared shared-append edits are not checked for append shape.

**Required cases (self-contained known-bad fixtures — empty, unrelated, and populated registries; true duplicate-reservation and true overlap probes, not incidental failures):** missing/malformed Open-claims section/header/table; vanishing truncated row; normalized numeric reservation collision; duplicate claim ID; duplicate branch; lookalike non-shared paths; destructive (non-append) edits to shared files; each refusing with its existing or newly named ARV-CLM code. **Residual, stated honestly:** a Markdown file never atomically reserves work across agents — the live GitHub PR state and protected merge path serialize merges; the registry is an integrity check and coordination protocol, nothing more. **Subject files:** `harness/claims.py`, `harness/known-bad/cases.py` (new KB cases), `harness/tests/` registration as needed. **Non-goals:** no registry semantics redesign; no distributed-lock claims.

### H-01c-authority — card: raw manifest/quote lineage (A12/A17; disjoint)

**One behavior:** a raw source + candidate manifest reanchor cannot pass merely because the candidate changed both. Trusted-base comparison rules bind each protected raw file to its approved prior digest/row (the prior MAIN digest — verified against the base checkout, not the candidate's copy); a legitimate new source, approved reanchor, or sourced supersession requires an explicit, distinguishable owner-authorized path, never indistinguishable from an ordinary candidate rewrite. Tests: coordinated raw+manifest mutation; digest moved to a wrong row; missing record; raw deletion/addition; allowed append behavior. Also: raw-cited quote validation fails closed when source metadata exists but no supported quotation is extracted — straight and supported non-straight quote forms plus fabricated curly-quote content. Never alter actual owner raw files to satisfy a test; never overclaim chat-source coverage beyond its documented limits. **Subject files:** `tools/verify_canonical_layer.py` (C8/VER-802/803 paths), `context/SOURCE-COVERAGE-MANIFEST.md` (schema rows if needed), the manifest mechanism's home. **Non-goals:** no new manifest platform; no raw-file edits.

### H-01c-evidence/privacy — card: evidence/red-record + redaction boundaries (A15/A18 + narrow A16; disjoint)

**One behavior:** evidence records certify what was actually observed. Confirmed defects: red records carry a hash but no typed observed-red result / predecessor-candidate revision binding / approved amendment semantics — a current hash alone can certify an unobserved or removed assertion; a NEW test file can evade red/required-suite obligations because Makefile discovery and gate TESTS lists differ; secret-shaped remote names/env keys are printed unredacted in some diagnostic paths (synthetic canaries only — never real credentials); A16 lint misclaims — deletion-only size counting (renames/deletions under-count), declared-vs-enforced limits, aliased/from-import ambient calls bypassing the AST walk, and environment/network access outside adapters. **Fix shape:** typed red records (observed-red result, revisions, amendment note, suite inclusion), fail-closed suite registration (a new test file without a red record refuses), canary-based redaction tests in stdout+stderr, and NARROWED A16 claims with concrete reopening triggers where a check cannot be enforced — never a universal Python security analyzer. **Subject files:** `harness/red.py`, `harness/red-records.json` (schema), `harness/gate.py` (TESTS registration check), `tools/isolation_check.py` (diagnostic paths), `harness/scope.py` (lint narrowing). **Non-goals:** no taint analysis; no real credential material anywhere.

### P3-M0 — card: the migration-oracle prerequisite (A05/A06 + applicable A08; with P3-00/P3-01, BEFORE product schema migrations depend on the runner)

**One behavior:** the migration runner refuses what it cannot prove transaction-safe, and verification observes rather than fabricates. Required: reject transaction control in migration text (an embedded `COMMIT` must never persist partial effects while the runner reports a rollback); disposable-PostgreSQL tests for normal multi-statement failure AND embedded transaction-control failure proving zero effects + zero bookkeeping for a refused migration; bidirectional directory/ledger history verification (missing applied tail/interior file, empty directory, gapped sequence, extra ledger entry, edited retained file — each with clear behavior); observation-only verify after bootstrap (or the bootstrap side effect declared separately — no bookkeeping under a claimed read-only verify); recovery/schema oracles compare actual preserved values + security schema/RLS/policies/constraints as relevant + nonempty successful independent reads. A defect-bound product prerequisite, NOT a general database framework. **Subject files:** `harness/migrate.py`, `harness/tests/test_migrations.py`. **Non-goals:** no production-database operations; no new migration framework.

### P3-K0 — card: the kernel-primitive prerequisite (A04/A07/A13; BEFORE a product command is accepted — may fold into P3-01 only if scope/acceptance stays small)

**One behavior:** product command identity/encoding/connection primitives are correct before the kernel builds on them. Required: canonical versioned structured request encoding replacing delimiter concatenation (command, owner/actor/client/key, all effect-bearing fields unambiguous; the exact separator-collision case + Unicode/normalization/boundary tests; same key + same canonical body → same result; same key + different canonical body → stable conflict, no effect); UUID variant/version correctness with controlled-randomness tests (version, variant, timestamp ordering/extraction, compatibility — no rewriting of persisted test IDs without a compatibility decision); product connection/configuration + named errors through the approved adapter boundary only (no direct psql path that can select a different socket/database than migrations; missing client, timeout, connection refusal, target mismatch → stable no-ACK refusal); explicit concurrent same-key semantics (same recorded result OR explicit retryable in-flight state — a unique constraint is not a replay promise; sequential crash tests are not concurrency proof). **Subject files:** `harness/commands.py`, `harness/ids.py` (adapters), `harness/state.py` (Session/adapter-consistent defaults), their tests. **Non-goals:** no product domain types yet; no provider persistence (Q12).

### H-02 — systems-engineering verification record and gate

**Purpose:** implement the owner's requirement that each slice receive a systems-engineering review after implementation and independent test verification, before merge.

**Design:** add a standard-library validator and a separately authored Systems Engineering Verification (SEV) record. The record is bound to the reviewed diff using a digest that excludes the SEV file and generated Proof Sheet, avoiding a self-referential commit hash. Required fields: slice ID, base SHA, reviewed-diff digest, owner intent IDs, system requirement IDs, affected C1–C5 claims, changed components/interfaces, component/integration/system/validation proof IDs, failure modes and controls, known-bad evidence, findings/dispositions, not-verified items, builder and reviewer context identifiers, and PASS/BLOCKED disposition.

**Gate behavior:** after H-02 is implemented, the harness must reject a missing, stale, malformed, incomplete, or BLOCKED SEV report. Known-bads must prove refusals for a missing report, stale digest, missing requirement trace, and a P0/P1 finding falsely marked PASS. The base-anchored floor from H-01 must test the SEV validator and gate path.

**Independence limit:** a field naming the reviewer context does not cryptographically prove that it is separate from the builder. The execution protocol must use a fresh context; a separate grader checks the SEV at phase gates. Report identity limitations honestly.

**Turn-21 requirements (INT-126/D-040, the directive's §5 — this card's completion conditions):** the reviewed-diff digest includes relevant implementation AND tests while excluding only narrowly documented generated/self-referential SEV/Proof Sheet artifacts — it must never exclude code under review; base or candidate movement makes a report stale. The A09 repairs land at this card's boundary: run-record schema + FULL digest syntax validated (prose is not SHA-256); each record bound to revision and sufficiently preserved output/artifact/reference; expected-RED evidence distinguished from acceptance evidence; whitespace/placeholder not-verified lists rejected (an explicit honest statement required); every relevant record bound, not just a truncated digest or the last record; malformed historical records preserved as historical artifacts with a disposition, never forged replacements. A08 baseline: for new product/migration tests, independently successful nonempty oracles must compare the authoritative/security-relevant outcome actually claimed — a row count is not a recovery equality proof; concrete content/schema/reference oracle requirements are enforced in the applicable P3 cards. Red-first known-bads exercise the PUBLIC validator and the ACTUAL gate caller (never an internal duplicate): missing report; malformed report; stale base/diff; missing intent/SYS trace; absent/invalid evidence; changed code after review; nonempty P0/P1 falsely marked PASS; same declared builder/reviewer where policy disallows; validator/test coordination weakening; omitted gate invocation; malformed proof/run records; placeholder limitations. **Sequencing (the directive is explicit):** H-02 design and red-first work MAY proceed in parallel with H-01b under disjoint claims; H-02 CANNOT be activated/merged as a trusted merge gate until the H-01b base floor can judge its validator/gate path; stacked branches resolve by fresh rebase/diff/evidence reruns — no forced push, no stale SEV reuse. H-02's own transition review is explicitly bootstrap-scoped and independently checked — never a permanent opt-out. Until activation, the existing independent-review discipline continues, labeled not-mechanically-enforced.

**Acceptance:** the report is required by the gate; every known-bad fails with its named code; the report digest matches the reviewed diff; a fresh-context SEV reviewer who did not implement the slice independently traces requirements to code and evidence; CI blocks missing or rejected reports. LAW-30 remains PLANNED until H-02 and its known-bads are green in CI.

## Phase 3 — Durable capture (first real product behavior)

**Entry condition:** this owner turn opens the Phase 3 execution path. Product-schema migrations begin only after the execution plan is explicitly accepted through the repository change process, P2-CLOSE is green, and H-01/H-02 are installed and proven. Phase 2 S1–S4 stays complete. H-01/H-02 are two bounded closure slices, not permission for an indefinite infrastructure phase.

### A. System requirements

The following SYS identifiers are traceability keys for the product plan, not permission for an agent to change the North Star. Every implementation card cites no more than the existing LAW-05 maximum of three requirement IDs. A requirement change follows the canonical decision/change process.

| ID | Required property | North Star claim |
|---|---|---|
| SYS-01 | Every acknowledged capture is committed at a named durability rung; acknowledgment never overstates persistence. | C1 |
| SYS-02 | Authoritative evidence is immutable after commit; revisions preserve history; deletion uses tombstones except for governed purge. | C1, C5 |
| SYS-03 | Every write has owner scope, actor, stable identity, and required provenance; cross-owner access is rejected. | C1, C2, C5 |
| SYS-04 | A command is atomic and idempotent; same key/body replays the same result; same key/different body is rejected. | C1 |
| SYS-05 | Every Highlight has a stable identity and Anchor tied to a specific Source version; reprocessing cannot silently move it. | C1, C5 |
| SYS-06 | Import/extraction failures are explicit and recoverable; partial imports are never presented as complete; capture does not depend on enrichment. | C1 |
| SYS-07 | Derived passages and indexes are rebuildable and carry processing/input provenance; no unique authored content exists only in derived state. | C1, C3, C5 |
| SYS-08 | Local writes and cloud sync have explicit states, idempotent replay, and crash recovery. | C1 |
| SYS-09 | The supported initial client path can create and retrieve a capture through the real backend boundary. | C1, C2 |
| SYS-10 | Export/restore preserves authoritative data, revision history, and governed purge state without silent loss or resurrection. | C1, C5 |
| SYS-11 | Each implementation slice closes a V-model trace and has independent systems-engineering verification before merge. | C1–C5 |

### B. Proposed system architecture

The architecture below is a proposed implementation baseline. Higher-authority owner words, North Star, locked decisions, and laws govern if there is any conflict. A discrepancy becomes a Question Record, not an agent-chosen compromise.

**Authority versus derivation**

- Authoritative: logical Work identity; imported Source identity/version and acquisition metadata; committed Highlight, Bookmark, Note, and later Journal content/revisions; attribution and command history required to explain writes and recovery.
- Derived: extracted passages, keyword index, embeddings, relationship candidates, concept links/status, rankings, and context packs. Every derived generation has processing/configuration/input lineage and can be discarded and rebuilt.
- A current view can be a projection but cannot be the only remaining copy of authored history.
- Byte-level blob deduplication may reuse identical bytes; it must not merge logical Works or Sources. No semantic auto-merge.

**Minimum domain concepts**

- Work: logical library item.
- Source: a particular imported source version/edition/acquisition instance, as defined in GLOSSARY; not an extraction run.
- Passage: versioned extraction output with its Source version and parser/extractor provenance.
- Highlight: stable capture identity, immutable revisions, selected content, and an Anchor tied to one Source version.
- Bookmark: stable saved location/Anchor, not a copy of the Source.
- Note: owner-authored thinking with immutable revisions and explicit references to relevant Work/Source/Anchor/Highlight/Note.
- Command log/outbox: idempotency and recovery record for accepted mutations and synchronization.
- Journal blocks and stable @-references remain Phase 4. Vector/semantic retrieval, grounded relationship evidence, concepts, and Kev policy/evaluation behavior remain Phase 5. Phase 3 must not implement those complex behaviors prematurely, but must not foreclose them.

**Open identity gate — Q11**

The 2026-10-16 review assumes a repeated identical-file import resolves to the same Work. Working-context notes indicate a preference for separate logical imports by default and optional duplicate detection, but no verbatim source entry currently exists in the canonical ledger. That preference is not an adopted policy. Until the owner ratifies the identity rule:
- Never automatically merge Works or Sources.
- Do not create uniqueness constraints based on filename, title, or semantic similarity.
- Duplicate detection, if present as a proposal, must leave existing objects unchanged.
- Physical blob reuse may be independent of logical identity.
- Q11 blocks auto-dedup/merge and identity-specific uniqueness constraints only. Other kernel and capture work may continue.

**Anchor contract**

An Anchor identifies a Source version and contains enough format-specific location evidence to re-find the passage. Carry parser/extractor version and fallback matching evidence. Page number or character offset alone is not assumed stable across editions, reflow, re-extraction, or file changes. Run the bounded anchor-stability spike before freezing the schema. Q8's current default remains synthetic documents unless the owner changes it at its named gate; do not claim real-document stability without measurement. Record measured outcomes before deciding thresholds.

**Write, extraction, sync, and index states**

1. Stage source bytes in isolated storage and verify a content digest.
2. Through an idempotent command, persist Source metadata and import-job/outbox state atomically in PostgreSQL.
3. Produce a versioned extraction generation. Publish only when complete; a crash leaves an old valid generation or an explicit failed/retryable state, not a partially ready import.
4. Commit a Highlight/Bookmark/Note mutation with its idempotency record in one database transaction. Acknowledge only after commit.
5. Update keyword search through a distinct, rebuildable derived path. Index failure never loses or hides authoritative capture; it reports lag/failure.
6. Sync local outbox records to Supabase through the same command kernel. Network delivery may occur more than once; idempotency prevents duplicate logical effects. Server-durable status follows verified server acknowledgment.
7. Distinguish local-durable, server-durable, keyword-searchable, semantically indexed, and linked. Every retry uses recorded state, not model memory.

**Storage boundary:** PostgreSQL and object/blob storage do not share one transaction. Do not claim cross-service atomicity. Use staged content-digested blobs; only commit Source metadata that references a verified durable blob; track unfinished imports; recover or clean orphaned staging objects under a tested policy. If the selected host cannot satisfy the contract, open a blocker instead of inventing weaker semantics.

**Q12 storage decision.** D-032 does not itself select an object-storage provider or specify local staging/cache semantics. At P3-00, compare the existing Supabase Storage option against any alternative using durability/backup guarantees, offline operation, content identity, upload completion, signed access, purge and restore integration, orphan cleanup, and local/cloud failure recovery. Recommend one option with evidence; do not implement provider-specific migrations or claim cross-store atomicity until the owner ratifies the choice.

**Minimum kernel only**

Build only what the first real slice needs:
- validated owner scope and actor vocabulary;
- stable typed IDs through the existing ID adapter;
- time through the existing clock adapter;
- provenance/run metadata for evidence and derived output;
- one command registry with transaction/idempotency/ack-after-commit;
- repository/transaction boundaries that keep product modules away from direct DB connections;
- immutable revision/tombstone primitives and standard named errors;
- one canonical source for closed vocabularies as required by LAW-25.

Only adapters may access ambient time, randomness/ID generation, and environment. New code uses the kernel; no second path for the same concern (LAW-10/24). Do not build a generic framework before a real slice proves the need.

### C. Ordered bounded product slices

Every slice gets its own branch/PR, one behavior, pre-registered acceptance tests, a declared file scope, current LAW-05 limits, no unapproved dependency, actual real-stack run, independent state reads, Proof Sheet, independent test verification, and SEV verification. If a slice exceeds size limits, split it; never relax the limit. Stop after three failed cycles.

**P3-00 — Requirements, interfaces, and schema freeze**
- Trace SYS-01–SYS-11 to owning component, interface, tests, C1–C5 claims, and user validation scenario.
- Draw data-lifecycle and state machines for import; capture; revision/tombstone; local outbox; server sync; indexing; export/restore.
- Specify authoritative entities, IDs, ownership, actor, revisions, provenance, transaction boundaries, migration plan, kernel interfaces, and failure behavior.
- Q11, Q12, and Q8 must remain visible at their named scopes; other owner decisions block only the dependent work.
- Acceptance: no contradictory source-of-truth rule; every requirement has tests and proof paths; unresolved dependencies have exact boundaries; independent SEV finds no P0/P1. No product schema migration until this gate is accepted.

**P3-01 — Kernel and first real command**
- Create only the kernel contracts needed by the next capture operation and one real command.
- Tests first: missing owner/actor/provenance; same key/body replay; same key/different body; crash before commit; crash after commit before acknowledgment; direct DB access; ambient time/ID use outside adapters.
- Acceptance: atomic, idempotent, attributed behavior, stable named failures, and independent database observation.

**P3-02 — Work and Source intake**
- Implement the resolved identity policy with a minimal supported readable-text/Markdown path, source digest, media type, acquisition metadata, owner/actor, and explicit import state.
- Separate logical identity from byte deduplication. No title/filename/semantic auto-merge.
- Tests: identical bytes imported twice; two similar but different works; retries; failure after staging; failure before metadata commit; missing blob; owner isolation; restart and restore of unfinished import.
- Acceptance: behavior follows ratified identity policy; all partial states are failed/retryable, never falsely complete.

**P3-03 — Extraction generation and Anchor**
- Derive versioned passages and Anchors; source and authored state stay separate from derived passages.
- Run the bounded anchor-stability spike before freezing format-specific location behavior.
- Tests: invalid/empty input, encoding boundary, passage boundary, extraction crash, cosmetic re-save/re-extraction, new edition, source hash mismatch, wrong-source anchor.
- Acceptance: complete-or-failed generation; Anchor never crosses Source versions silently; limitations remain explicit.

**P3-04 — Highlight and immutable revisions**
- Add stable Highlight identity plus append-only revisions carrying selected content, Anchor, Source reference, owner/actor, input digest, and command provenance.
- Reject missing/dangling Anchor and cross-owner Source. Preserve prior revisions; tombstone hides from normal retrieval while retaining governed history.
- Tests: mutation rejection; dangling references; owner isolation; retry; crash at each transactional boundary; source re-import/re-extraction; tombstone/restore.
- Acceptance: independent read sees correct history; current view rebuildable; acknowledgment states actual durability rung.

**P3-05 — Bookmark**
- Represent Bookmark as stable identity and location/Anchor; do not duplicate source text. Define source-version-change behavior.
- Tests: invalid Anchor, cross-owner access, re-import, re-extraction, tombstone/restore, replay and restart.
- Acceptance: return to saved location or report a typed unresolved-anchor state; never silently retarget.

**P3-06 — Note and revision history**
- Persist deep owner-authored Notes with immutable revisions and explicit links. Support diagrams only after their serialization and round-trip format is defined.
- Tests: revisions do not overwrite history; duplicate retries; competing revisions; dangling refs; owner boundary; crash/restart; export/restore.
- Acceptance: every revision is retrievable, attributable, and referenceable; conflict never silently destroys a revision or claims an untested merge.

**P3-07 — Keyword findability**
- Build a rebuildable keyword index for committed sources/passages/captures/notes within the currently supported formats.
- Tests: indexing failure; delete/rebuild; stale entry after revision; tombstone filtering; owner filter; encoding/tokenization boundaries; known query.
- Acceptance: captures become searchable under a defined contract or explicitly report indexing lag/failure; rebuilding restores expected results.

**P3-08 — Local outbox, Supabase sync, and recovery**
- Persist local mutation plus client-outbox intent atomically; apply remote writes through the same kernel; add the server outbox handoff required for future enrichment per D-018/D-032.
- Define ordering, replay, retry and conflict semantics. Do not silently use last-write-wins for authored content. Preserve concurrent immutable revisions; the current view rule must be explicit. No owner review queue or model decision is allowed to block pipeline progress.
- Tests: offline capture; restart before sync; retry after uncertain acknowledgment; duplicate server delivery; out-of-order delivery; server outage; remote/local mismatch; cross-owner sync; process death around outbox acknowledgment.
- Acceptance: each committed local write is either server-durable or explicitly queued/retryable; no lost committed writes or duplicate logical effects; independently read remote state.

**P3-09 — Export/restore and integrated durable-capture proof**
- Define versioned export/restore for authoritative records, source/blob references, revisions, and required purge/retention state. Rebuild derived indexes after restore.
- Tests: export to clean destination, restore, canonical state hash comparison, repeated restore, missing blob, malformed archive, interrupted restore, purge then restore, rebuild corrupt index.
- Acceptance: defined authoritative-state equality holds; a purge cannot be resurrected by restore; errors are explicit/retryable; independent verification uses a separate role/path. This explicitly closes the export/restore gap raised in the 2026-10-16 review.

### D. Mandatory V-model systems-engineering verification after each slice

After implementation tests and an independent test verifier are green, a separate fresh-context Systems Engineering Verifier (SEV) reviews the slice card, reviewed diff, and Proof Sheet only:

1. Trace every changed behavior to owner-intent IDs, approved SYS requirements, and acceptance criteria.
2. Confirm source-of-truth ownership, component responsibility, interfaces, dependency direction, and no second kernel/adapter path.
3. Review failure modes relevant to the change: data loss, stale/wrong anchors, owner leakage, duplicate side effects, stale derived data, crash/restart, sync, provenance loss, and restore/purge behavior.
4. Close the V-model level actually claimed: component proof, real integration-boundary proof, full affected system path, and named user validation. A lower-level green check is not system-level proof.
5. Inspect red-first evidence, real-stack transcript, independent state read, fault/property/mutation results, known-bads, regression coverage and failures.
6. Inspect migration compatibility, security/privacy boundary, dependency changes, protected paths, downstream layer impact, and reversible recovery.
7. Verify evidence provenance, reviewed-diff digest, actual commands/revisions, dispositions, and explicit not-verified list.
8. P0/P1 or a blocking owner question means STOP. P2 is not automatically accepted debt; it requires an owner-approved record with reason and revisit condition.
9. The SEV reviewer did not implement the slice. At phase gates, a separate grader checks the SEV. Context labels alone do not cryptographically prove independence; report this limitation honestly.
10. The owner reviews the Proof Sheet and SEV disposition. Green CI permits review of a merge; the agent cannot resolve owner decisions, change laws, or merge its own review/proposal.

The standard form lives in context/TEMPLATES.md; policy lives in OPERATING-MODEL.md and LAW-30. Once H-02 is live, a missing, stale, incomplete, or BLOCKED report fails the gate.

### E. Phase 3 exit criteria

Phase 3 exits only when all claims are proven on the final main revision:
- Work/Source identity and Anchor contracts are explicit, and owner blockers stay resolved or isolated at their exact scopes.
- A real client/backend path ingests supported input, creates a Highlight with valid Anchor, Bookmark and Note, then finds them via keyword search.
- Accepted captures survive defined crash/restart/replay/offline fault matrices with zero lost committed writes and no duplicate logical effects.
- Local-durable and server-durable are distinct; sync has explicit recoverable outbox states.
- Every write is attributed and owner-scoped; two-owner tests and independent reads pass.
- Revisions are immutable, tombstones work, and a governed purge remains effective after restore.
- Derived passages/indexes rebuild without losing authored state; stale derivations cannot silently appear current.
- Export/restore satisfies the documented equality contract.
- Every SYS requirement traces to tests and Proof Sheet evidence; every slice has passing SEV; all known-bads are refused with named codes.
- Local checks and the three recorded required CI checks pass at final revision; an uncoached clean-clone task agent completes the real user-like acceptance path, and a separate grader passes it with no P0/P1.
- Not-verified items remain explicit. A successful PR or elapsed time is not phase-exit proof.

### F. Boundaries and stop conditions

No reader UI is built in this repository. Phase 4 covers the complete reader/journal/@-reference workflow. Phase 5 covers semantic/vector retrieval, relationships, concept graduation and Kev policy/evaluations. Their schemas must remain compatible, but their advanced behavior must not be pulled into Phase 3.

P-17 applies: H-01 and H-02 are the only new general infrastructure closure slices. Once both are green, start P3-00/P3-01 immediately. No third generic infrastructure phase. A concrete product defect can justify a new guard under the ratchet; speculative future hardening cannot delay durable capture.

## Phase 4 — Reader and journal path (first usable milestone, D-013, D-023)
Open PDF/EPUB → highlight → bookmark → margin notes → durable journal blocks → stable `@` references — **plus the first import path: any readable format (INT-113/D-031, 2026-10-14 — pdf/txt/md/epub/json and every readable format; INT-019 day-one intake; books/articles per the durability ladder)**. Each behavior gets its own small card and verified result.

**Outcome roadmap (owner turn 20, INT-125/D-039 — the NG-04 owner-directed exception: outcome rows only; executable cards are elaborated ONE PHASE DEEP at Phase-3 exit from actual evidence, never earlier; the verbatim text is session record 20 §1 §8):**
- **4A Format intake and reader position** — approved PDF/EPUB/JSON paths incrementally by the durability ladder; native-text vs scan/OCR, reflow vs fixed layout distinguished; real corpora measured under the corpus gate (Q8); unsupported/encrypted/malformed → explicit errors, staged bytes never lost; source-open/position/anchor-resolution contracts + version compatibility.
- **4B Reading/capture integration** — the reader client (in its authorized repo, never this one) works through the API: import/open, position recording, highlight/bookmark/margin-note capture, auth + DTO serialization + saved-state progress + offline/retry + return-to-location; wrong/ambiguous anchors visible; no privileged client helper writes tables.
- **4C Library, reading lists, resumable behavior + Journal/blocks** — stable library/list membership, current-reading state, approved session/coarse-position/dwell events (D-010's boundary respected); journal as a writing lab: source-optional raw/creative blocks, long raw thinking preserved losslessly, no forced short-note funnel.
- **4D Stable @ references** — target identity vs selected historical revision; current/historical/tombstoned/unavailable/ambiguous/purged resolution states without leaking deleted private content; titles/labels change without breaking references.
- **4E Baseline scoped agent access (REQUIRED at first-usable, not Phase 5)** — authorized agents read the owner's journal and capture context through the same API with provenance/scope/budgets.
- **4F Recovery/regression proof and phase gate** — supported-prior-state migration, full journal/reference/diagram lifecycle export/restore, owner isolation, sync conflicts, rebuild; clean external client + independent grader; owner reviews concrete product fidelity. **Real UI/user validation is [blocked] without an actual reader/journal host — backend contracts are proven through a clean external client, never fabricated.**

Exit: the owner's day-one workflow (import → read → capture → note → journal with references) runs end-to-end on the real stack, proven through a real client path with a documented integration boundary to the reader/journal clients (the UI itself is outside this repo). An API CRUD inventory is not this exit.

## Phase 5 — Retrieval and compounding
Keyword lookup → agent reads (API/MCP surface per D-019) → semantic indexing + vector retrieval → relationship candidates → concept formation → Kev policy/eval gates. Compounding probes tested separately: deterministic → semantic → graph.
**Pre-Phase-5 gate (owner turn 13 disposition, D-034): the classification-words rule must be made explicit before Phase 5 begins** — ordinary user text is processed as text; classification words ("concept", "fact", "quote") receive no special tagging behavior or dedicated weighting unless the owner decides otherwise (D-030's removal carried to its semantic conclusion); VER-211/MUT-11 are rewritten then to enforce the clarified rule, not the older tag-feature wording (record 16 §1, the review's P2 disposition).

**Outcome roadmap (owner turn 20, INT-125/D-039 — NG-04 exception scope as above; verbatim: session record 20 §1 §9):**
- **5A Authorized retrieval API/context packs** — keyword/identity/filter/temporal/behavioral queries, pagination, strict budgets; MCP wraps the same core; every item carries source/revision/anchor + trust status + mechanically true why; imported content untrusted — an embedded instruction cannot widen scopes or mutate state; explicit truncation retaining provenance.
- **5B Evaluation baseline BEFORE ranking changes** — versioned query corpus (relevant/no-result/distractor/conflict/duplicate-group/multilingual/owner-isolation cases); dev/calibration set separate from a LOCKED held-out; keyword baseline assessed first; targets (quality/latency/cost) defined BEFORE acceptance runs, never invented as 100% relevance; safety/provenance/budget invariants are separate from empirical quality.
- **5C Semantic spike under Q7** — approved model/version/license/runtime/cost + corpus + budget; measured precision/recall/rank + p50/p95 latency + cost at representative sizes vs keyword and explicit-relation baselines; NO paid call before budget approval; deterministic fakes prove contracts only, never quality.
- **5D Versioned semantic index/vector retrieval** — approved embeddings, revision lineage, model/config/generation, resumable outbox job, retry/invalidation, delete/rebuild, purge/owner filters; no unique authored state in the vector index; failures leave the keyword path alive.
- **5E Hybrid retrieval** — exact/vector/filters with declared ranking and actual why paths; measured held-out change vs baseline with ALL regressions reported; thresholds never moved after seeing results.
- **5F Discovery vs grounded relationships** — candidates are discovery only; grounded relation requires permitted text-pair decision or structural fact + valid owner-scoped versioned endpoints + evidence spans/run/policy; user correction is transparent history; no per-candidate owner queue.
- **5G Concept formation** — stable provisional IDs, alias/correction/merge/split history; independent-source policy distinguishes duplicate bytes/acquisitions/editions/paraphrases/works; graduation only against genuinely held-out material; usefulness counted, not concept volume.
- **5H Kev policy/evaluation — THE GATE (dependency correction, owner turn 20): 5H must pass BEFORE Kev-backed 5F evidence promotion, 5G graduation, or graph compounding.** Bounded non-generative output vocabulary recovered from the recorded contracts (never invented); abstention path; reproducible policy version; hard negatives/contradictions/near-duplicates/no-evidence/held-out pairs evaluated; a Kev output is never its own evidence and never upgrades similarity into truth.
- **5I C3 proven in three separate grades** — deterministic (alias/relation → previously-saved highlight retrievable, baseline absence + post-change reason), semantic (new related Work → OLD material resurfaces under a held-out query, pinned benchmark + provenance), graph (admissible grounded relations add paths without fabricated evidence; false-link/contradiction controls; reversible recomputation); validated in actual research use, not retrieval metrics alone.
- **5J Final integrated gate** — capture continues while enrichment/index/provider fail; agent retrieves precise bounded context; wrong-owner and hostile-document paths fail; purge/restore invalidates all derived copies; rebuild; migration + performance/cost envelope; complete RTM + independent SEV/grader/owner fidelity validation.

Exit: C3 demonstrable with reasons and provenance — new inputs resurface old material; automatic relations add value without violating evidence rules. Unknown policy/corpus/budget or absent user validation is [blocked] at its exact boundary, never a synthetic PASS.

## Standing open (owner)
- D-014 — calculation engine: open, non-blocking for capture (owner reaffirmed 2026-10-14, INT-114).
- Q6 — research-transcript status (2026-10-16 review §8 Q1; adopt vs reference doctrine) — blocks Part-2 acceptance-scenario finalization + the S5 corpus only.
- Q7 — semantic-spike budget for S6 (review §8 Q2) — blocks S6 only.
- Q8 — extraction-spike documents for S5 (review §8 Q3) — blocks S5's corpus only.
- Q9 — repository visibility (review §8 Q4; observed public 2026-10-16) — blocks nothing; privacy-relevant.
- Q10 — fine-grained PAT/workflow-tamper hardening (review §8 Q5, from F-7) — blocks mechanical workflow-tamper hardening only; credential/permission choice stays owner-controlled.
- Q11 — Work/Source identity and duplicate-import semantics (raised 2026-10-19, session 19, record 19 §8) — working-context notes indicate a preference for separate logical imports by default and optional duplicate detection, but this is not yet canonical owner intent in the ledger. Do not auto-merge or add identity-specific uniqueness constraints until the owner ratifies the identity rule. Blocks auto-dedup/merge only; unrelated capture/kernel work continues. Home: DECISIONS Q11; gate: P3-00 schema freeze.
- Q12 — source-file blob backend, local staging/cache lifecycle, and cross-store recovery are not specified by D-032. Do not pick a provider or promise cross-store atomicity by assumption. It blocks the source/blob persistence schema and durability promises only; command-kernel work can continue. Home: DECISIONS Q12; gate: P3-00 review, before P3-02.

Q6–Q10 were registered 2026-10-16 (session 18, D-036); Q11 and Q12 added 2026-10-19 (session 19, record 19 §8/§10) to keep the Work/Source identity and source-blob persistence gaps explicit. Each blocks only its named dependents (F-07); directed work proceeds regardless. Phase 2 S1–S4 remain complete.

Closed 2026-10-14 (owner turn 12, INT-110..INT-117; LOCKED rows D-028..D-033 in DECISIONS): Q1, Q2, Q3, QD-1, F-06, Q-IDENT.

The List is the refinement-debt register (D-020) — cloud sync (L-001) is its live entry; semantic search, pgvector, and vector search are in the active sequence (Phase 5), never on the register. Deployment (D-032): Supabase-hosted, cloud + local synced.

## Supersession note
The F-00..F-09 foundation-slice order from the original execution spec is SUPERSEDED by this phase sequence (D-016; reconciliation brief R-02/R-10). The slice cycle, size limits, proof discipline, and laws carry over unchanged into the new phases — now codified at root: LAWS.md (the original 29 source laws plus owner-directed LAW-30) and ENGINEERING.md (the doctrine). The execution contract's canonical home is `/EXECUTION.md` (created by the canonicalization slice, 2026-10-13, D-021): the 12 spec deltas staged in `context/extracted/08-RECONCILIATION-BRIEF.md` are folded into the root layer or closed by owner decision — Q1–Q3 closed 2026-10-14 by D-028/D-029/D-030 (the earlier "explicitly owner-gated (Q1–Q3)" wording is superseded: no open question remains among them) — nothing waits on a further agent-side rewrite.

## Post-product comprehensive refinement pass (P-18, INT-094/INT-096 — named, not scheduled)

Once the end-to-end product exists (Phase 4+ exit evidence), ONE comprehensive refinement pass across the Intent Ledger, decisions, principles, laws, North Star, architecture, and future vision — judged against implementation evidence: which assumptions survived contact with reality, which decisions were superseded, which capabilities were actually delivered, what the next version should become. History stays intact throughout: refinement clarifies the current direction and marks supersessions (append-only, `superseded_by`), never rewrites to pretend the answer was always known. Until that gate: capture continuously, correct only what can mislead current work, leave unrelated editorial debt for the pass (P-18, D-026).

## Growth-model mapping (how this plan grows the repo)
Phase 1 → operating Model 1 (trust environment) · Phase 2 → Model 2 (build loop: harness core, builders, verifier) · Phase 3 → Models 2→3 (substrate laws live; enforced architecture begins) · foundation exit → Model 3 stable · Phases 4–5 → Model 4 (evidence-driven) · post-foundation recurring agents → Model 5 (self-maintaining) · harness evals → Model 6 (self-improving). Each model's full specification (who runs, what's enforced, how memory updates, how failures heal, graduation predicate): OPERATING-MODEL.md §6.
