# LAWS — The Executable Law Book

**What a law is.** A law is a constraint WITH a check. A law with no check is debt. Each law carries: its statement (MUST / MUST NOT / CAN), its ladder level (C1–C6, see `/ENGINEERING.md` §4), its check (the mechanism that catches the violation), and its live-at (the phase where the check turns on). When this file and the code disagree, report the drift — never resolve it silently (same rule as the spec's Part 1).

**Status vocabulary.** `planned` — the check is not built yet (allowed pre-build; every planned law carries a live-at). `enforced` — the check exists and a known-bad build proves it catches the violation. `waived` — owner-approved exception with a reason and a revisit condition. No law rests on prose alone without a LAD-02 reason code.

**How laws change.** Only the owner changes a law. An agent CAN propose a change in a Question Record. Weakening a law — lowering a threshold, removing a test, reducing a lint level, widening a scope — is itself a violation (LAW-09).

**Provenance.** The original 29 laws come from `context/raw/Arivo Agent Execution Specification.md` Part 4, unchanged in meaning. LAW-30 (session 19 part 1: per-slice SEV) and LAW-31 (session 19 part 2: the claims discipline — the ratchet response to the recorded two-agent collision, record 19 §8) are additional owner-directed process laws; they do not rewrite or renumber that original set. The F-slice "live at" values are re-mapped to the reconciled phase order (D-016, superseding the F-band).

---

## The constraint ladder (reference)

| Level | Name | What it does |
|-------|------|--------------|
| C1 | Type system | The code does not compile |
| C2 | Database | The write does not commit |
| C3 | Lint / architecture rule | Lint fails |
| C4 | Executable test | The suite fails |
| C5 | Gate / CI | The merge is blocked |
| C6 | Document | It depends on the agent (last resort, reason code required) |

- **LAD-01** — choose the highest level that works.
- **LAD-02** — a C6 rule carries a reason code: `no-mechanism`, `needs-owner`, `waiting-for-slice`.
- **LAD-03** — when a mistake repeats, move its constraint up one level or more.

---

## Truth laws — epistemic discipline

*Why this group exists: an agent that can assert unverified claims, or hide what it did not check, poisons every decision made downstream. These laws make honesty mechanical.*

| ID | Law | Level | Check | Live at |
|----|-----|-------|-------|---------|
| LAW-01 | You MUST NOT claim a result without a proof file that the harness made. | C5 | The gate compares the Proof Sheet with the run records. | Phase 2 |
| LAW-02 | You MUST NOT state a fact about a tool, model, library, or standard from memory. You MUST cite a FACT ID or run a spike. | C5 | The audit flags a version number or product claim with no FACT ID. | Phase 2 |
| LAW-03 | When no file answers a question, you MUST write a Question Record and follow its class. | C5 | The gate fails while a blocking Question Record is open. | Phase 2 |
| LAW-04 | Your final report MUST list what you did not verify. | C5 | The Proof Sheet schema requires the list. | Phase 2 |

**Failure class killed:** fake-success and silent assumptions. The not-verified list is a required Proof Sheet field, so ignorance is always visible to the reviewer.

## Scope laws — blast radius control

*Why this group exists: agents over-reach. Without scope machinery, every change can touch everything, and everything becomes coupled. These laws make the blast radius a checked property of every change.*

| ID | Law | Level | Check | Live at |
|----|-----|-------|-------|---------|
| LAW-05 | One slice changes one behavior inside the size limits. | C5 | SIZE check (≤8 source files / ≤400 source lines / ≤6 test files / ≤800 test lines / ≤200 fixture lines / ≤3 requirement IDs / 1 migration / context pack ≤12,000 tokens) | Phase 2 |
| LAW-06 | You MUST change only the paths in the card scope. | C5 | SCOPE check on the diff | Phase 2 |
| LAW-07 | You MUST NOT edit a protected path. Only an owner-approved intent-change slice CAN. | C5 | CODEOWNERS + PROT check. Protected: `harness/`, `gates/`, `constraints/`, `.github/`, `docs/agent/`, `docs/product/INTENT-LEDGER*`, `archive/`, applied migrations, frozen tests. | **Phase 1** |
| LAW-08 | You MUST NOT add a dependency without an approval note. | C5 | Lockfile check | **Phase 1** |
| LAW-09 | You MUST NOT weaken a constraint. This means: lower a threshold, remove a test, reduce a lint level, or widen a scope. | C5 | Ratchet check on `gates/` and `constraints/` | Phase 2 |
| LAW-10 | New code MUST use the kernel. You MUST NOT add a second way to do what the kernel does. | C3 | Boundary lint and scaffold conformance | Phase 3 |

## Method laws — the verified path

*Why this group exists: "tests that agree with the implementation" are worthless when both are wrong. These laws force the red-first, real-stack, independent-read discipline that makes verification mean something.*

| ID | Law | Level | Check | Live at |
|----|-----|-------|-------|---------|
| LAW-11 | You MUST commit each new test alone and see it fail for the stated reason before you change code. The red record is frozen. | C5 | RED check: harness hashes the red tests; at the gate each hash MUST match unless a Verifier-approved amendment exists (amendments add assertions, never remove). | Phase 2 |
| LAW-12 | You MUST run the real stack for each behavior change. | C5 | The Proof Sheet needs a real-run transcript. | Phase 2 |
| LAW-13 | A test MUST read system state through a path that the code under test does not control. | C4 | Mutation test and known-bad build (`independentRead` on a separate connection and role). | Phase 2 |
| LAW-14 | The final commit MUST have a passing `make fast` record. | C5 | The gate checks the run record. | Phase 2 |
| LAW-15 | For a defect, you MUST write a failing reproduction before the fix. | C5 | RED check | Phase 2 |
| LAW-16 | After 3 failed cycles, you MUST stop and write a Blocker Record. | C5 | Cycle counter | Phase 2 |
| LAW-17 | You MUST keep no state outside the repo. A new session MUST be able to resume from files. | C4 | Resume test (a new session finishes a half-done slice from files only) | Phase 3 |
| LAW-18 | After a failure, you MUST run the ratchet before the next slice. | C5 | The gate fails while a Failure Record has no constraint or approved debt. | Phase 2 |

## Product laws — the substrate guarantees

*Why this group exists: these encode claims C1–C5 and non-goals NG-01..03 as mechanics. They are the proactive set's core — expensive or impossible to retrofit, so they exist from the moment their substrate exists.*

| ID | Law | Level | Check | Live at |
|----|-----|-------|-------|---------|
| LAW-19 | Evidence rows MUST NOT change after commit. The owner-run purge command is the only exception. | C1+C2 | No update or delete function exists; database triggers reject both; SQL lint (UPDATE/DELETE on evidence tables outside the purge module). | Phase 3 |
| LAW-20 | A derived row MUST carry provenance: run ID, versions, input hash. | C1 | `writeDerived` type; NOT NULL columns. | Phase 3 (first derived table) |
| LAW-21 | Every write MUST carry an owner scope and an actor. | C1 | `OwnerScope` type; NOT NULL columns; row-level security. | Phase 3 |
| LAW-22 | No query MAY cross owners. | C2 | Row-level security; composite keys; the two-owner test. | Phase 3 |
| LAW-23 | A command MUST be atomic and idempotent. It MUST acknowledge after the commit. | C1 | `defineCommand`: replay N times = one item; same client ID with a different body = 409; property and fault tests (kill at each crash point; after restart state equals the clean run). | Phase 3 |
| LAW-24 | Code MUST NOT call ambient time, randomness, ID generation, network, or environment outside adapters. | C3 | Lint (only `adapters/clock` reads time; only `adapters/ids` makes IDs) | Phase 2 |
| LAW-25 | Closed vocabularies MUST come from one schema source. | C3 | Codegen drift check (schema/vocab → types + DB constraints + docs; a difference fails) | Phase 3 |
| LAW-26 | Runtime agents MUST NOT reach the database. They use the API or MCP with scoped tokens. | C3 | Boundary lint + the NG-02 test | Phase 3 (scan), Phase 5 (full, at MCP) |
| LAW-27 | No pipeline stage MAY wait for an owner action. | C4 | NG-01 scan | Phase 3 (scan), Phase 5 (full, at enrichment pipeline) |
| LAW-28 | Builder and verifier agents MUST NOT read real owner data or secrets. | C5 | Secret scan (redacted isolation check — conditions printed, values never); fixture-only repo; sandbox. | **Phase 1** |
| LAW-29 | No generative model MAY run inside Arivo's pipeline. | C4 | NG-03 scan | Phase 5 (at enrichment pipeline) |
| LAW-30 | Every implementation slice MUST receive a separately authored systems-engineering verification after implementation and independent test verification, before merge. The review MUST trace approved owner intent and system requirements through architecture/interfaces to component, integration, system, and validation evidence; list relevant failure modes and not-verified items; it MUST NOT resolve owner questions or weaken constraints. Missing, stale, incomplete, or blocked evidence means STOP. | C5 (record/gate) + C6 (context independence until separately enforced) | H-02: standard-library SEV validator bound to reviewed diff; gate rejects missing/stale/incomplete/blocked reports; known-bads prove the refusals. Fresh-context independence is separately graded and its identity limitation reported honestly. | **LIVE (CLAIM-040/CLAIM-041, PRs #75/#76 — the H-02 card complete): the validator (harness/sev.py, ARV-SEV-001..008) + the gate's PR-mode SEV step + the KB-SEV matrix (8 cases) green in the PR-head CI harness job (S4b — the candidate-controlled leg) + the local PR-mode gate green over the slice's own record (the recorded run); the first enforced record landed with CLAIM-041 itself (the bootstrap-scoped transition, independently reviewed by the fresh-context round) — mechanically enforced from the NEXT slice's PR onward (the CI base carries the wiring once this merges). The phase-gate grader remains the separate SEV authority at the phase gates.** |
| LAW-31 | No consequential change MAY land without an OPEN claim in `CLAIMS.md` whose declared scope covers its diff; two OPEN claims MUST NOT overlap on any non-shared file. Ledger IDs are reserved one at a time through the registry, each exactly previous-max+1. | C5 (the gate) + C2 (no silent cross-agent interference) | The harness gate's claims checks: ARV-CLM-001 (the registry exists and parses, fail-closed), ARV-CLM-002 (scope exclusivity among OPEN claims — the later overlapping claim is refused with the named code), ARV-CLM-003 (reservations unique, gapless, each exactly previous-max+1 of the used set), ARV-CLM-004 (well-formed rows: claim ID, session, agent, branch, scope); known-bad cases prove each refusal. | **Session 19 (the ratchet response to the recorded two-agent collision, record 19 §8/LAW-18): live when the machinery slice's known-bads pass; until then agent-discipline per D-038** |

---

## The proactive set

Built in advance only the constraints that cost much to add later: **LAW-07, 08, 19, 21, 22, 23, 24, 25, and 28, plus the harness checks** (scope, size, proof, red). Everything else arrives through the ratchet after a real failure. **Do not invent constraints for failures that have not happened.** In the reconciled phase order this means:

- **Phase 1 (walls):** LAW-07, 08, 28 — protected paths, dependency approval, builder/verifier isolation.
- **Phase 2 (minimum harness):** LAW-01, 03, 04, 05, 06, 09, 11, 12, 13, 14, 15, 16, 18, 24 — proof, scope, red-first, real stack, independent reads, ratchet protection. Representative known-bads for the proactive set only — NOT every planned known-bad before product code exists.
- **Phase 3 (durable capture):** LAW-10, 17, 19, 20, 21, 22, 23, 25, 26 (+ NG-01/NG-02 scans) — the substrate laws, live the moment their tables, kernel, and commands exist.
- **Phase 5 (retrieval/compounding):** LAW-27, 29 in full — when the enrichment pipeline and agent surface they police exist.

**The activation rule (KB-04):** a known-bad build activates when the behavior it targets exists. A phase exam MUST NOT need a behavior that does not exist. A law scheduled for Phase 5 is not "missing" in Phase 3 — it is `planned` with a named live-at, and building it early would violate the no-invention rule.

## Standing law-adjacent rules (from the spec, carried over)

- **QST-01** — the question's class sets the workflow, not its urgency. **QST-02** — a question that meets a Blocking condition MUST NOT become defaultable. **QST-03** — a default becomes a Decision Record with status `default` and a gate at which it locks.
- **Stop conditions (STOP-01..08):** a blocking Question Record is open · the slice failed 3 cycles · the change needs a path outside scope · the harness is red · two laws conflict · the task asks you to weaken a constraint · owner words conflict with another file · you cannot verify a fact the slice needs. When one is true: write the record, commit it, end the session with a one-line status.
- **Actor classes (the data-law/product-claim conflict resolver):** builder/verifier agents — fixtures only, test database only, no secrets · runtime agents — real owner data through API/MCP in granted scopes, never the database, scoped tokens only · Arivo workers — only the owner scope of their job, through the kernel, service credentials from the environment · the owner — everything, holds the keys.
- **KER-01..04 / BND-01..08** — kernel and boundary rules (feature imports kernel+schema only; kernel imports no feature/adapter; adapters import kernel+schema but never a feature; only `adapters/db` imports the driver; only `adapters/http` imports the HTTP framework; only `adapters/clock` reads time; only `adapters/ids` makes IDs; product code never imports harness; a feature never imports another feature — shared code moves to the kernel through a kernel slice; a missing kernel primitive is a blocking Question Record, never a local substitute; a kernel change needs a `kernel` slice with owner approval).
- **AFA-01..12** — the agent-friendly architecture rules (summarized in `/ENGINEERING.md` §9).
- **RAT-01..08** — the ratchet protocol (specified in `/OPERATING-MODEL.md` §Self-healing).

## Phase gates and signing (target state)

A phase exits on predicates, not dates: all requirements pass; earlier tests pass; known-bad catch rate 100 percent; no critical or high gap open; the Demo Review has no open surprise; two consecutive runs with different seeds pass; the owner signs the tag. `main` is protected: PR + the required `verify` check (restricted to the expected source application), no force push (applies to admins). CODEOWNERS covers protected paths. The agent credential cannot change workflow files and cannot sign. Phase gates are owner-signed tags verified by CI against `gates/owner.pub`. Local `make verify` is preflight; remote CI is the authority (D-009).
