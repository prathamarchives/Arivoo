# Arivo: Agent Execution Specification

*Version 2 · Reader: AI agent · File: `docs/agent/EXECUTION.md` · Replaces Execution System v1 · October 13, 2026*

## Part 1. How to read this file

**Purpose.** This file tells you how to build Arivo. It holds the context, the laws, the verification loop, and the foundation slices.

**Loading.** Read Parts 1 to 4 at the start of each session. Read the other parts when the slice card lists them.

**Notation.** Each rule has an ID. MUST means mandatory. MUST NOT means forbidden. CAN means allowed. These words have no other meaning here.

**Weight of rules.** A rule in this file is weak. A constraint in the code is strong. A type error, a database rejection, or a lint failure stops you without your help. When this file and the code disagree, report the drift in your Proof Sheet. Do not choose one silently.

**Language.** The text uses the STE-style profile of Execution System v1. The lint treats structure rules as errors and sentence rules as warnings.

## Part 2. Context brief: what you build

**Goal.** Arivo is a reading and study environment. The owner reads, writes, and thinks in it. Nothing the owner does is lost. Each new input adds value to old inputs. The owner’s agents can use all of it. See INT-001, INT-002, and INT-022.

**Day one.** The owner will import conversations, research, books, and articles. The owner will make notes and lists. The owner will write in a journal that is also a writing lab. The owner will connect an agent and reason with it while reading. See INT-019 to INT-024.

**Worst failure.** The owner names one failure as the worst: losing a highlight (INT-029). Treat each path that can lose captured data as the highest severity.

| ID | Claim |
| --- | --- |
| C1 | Nothing is lost. Each captured item and behavior event returns by query and by export after a crash. |
| C2 | The owner’s agent has the owner’s context. It answers questions about reading, notes, and journal with sources. |
| C3 | Old items gain value from new items. |
| C4 | New concepts form from evidence and from the owner’s tags. They carry provenance. |
| C5 | Each derived claim has an explanation and a way to reverse it. |

| ID | Non-goal | Source |
| --- | --- | --- |
| NG-01 | No review queue. No pipeline stage waits for an owner action. | INT-004 |
| NG-02 | No agent connects to the database. Agents use the API or MCP. | INT-012, INT-030 |
| NG-03 | No generative model runs inside Arivo. The owner’s agents reason. | INT-011 |
| NG-04 | No detailed plan beyond the next phase. | INT-014 |
| NG-05 | No calculation engine in the backend. Status: default. The owner can veto it. | INT-007 |

**Architecture in brief**

1. Ground truth is append-only. It holds highlights, notes, journal revisions, bookmarks, tags, behavior events, and source snapshots. An edit adds a revision. A delete adds a tombstone.
2. Everything else is derived and can be rebuilt. Each derived row carries provenance: run ID, versions, and an input hash.
3. Every write carries an owner scope and an actor. Row-level security enforces the owner scope.
4. The client makes IDs (UUIDv7). A command is idempotent. It returns success only after the commit. One transaction writes the item, the revision, the search text, the outbox job, and the event.
5. Enrichment runs after capture in staged idempotent jobs. The foundation does not build it.
6. One API core serves all clients. An MCP adapter comes from the same command registry. Agents never touch the database. Tokens are scoped. Each agent write carries an agent actor.
7. A fact is a fragment with the tag `fact`. A concept is an entity. A tag is an append-only event. The first typed vocabulary is `fact` and `concept`. Free tags carry no meaning. See INT-025 and INT-028.
8. A fact tag classifies the type of statement. It does not certify truth. Truth lives in relations between fragments.
9. The owner can declare a concept at once. Auto-detected concepts stay provisional until later evidence supports them. See INT-026 and INT-027.
10. Keyword search finds new items at once. Meaning-based search comes later. Each result carries a reason.
11. A concept page is the personal wiki page: label, gloss, aliases, evidence with provenance, and linked fact fragments.
12. Later layers exist in the archive: belief aggregation, concept induction, and the Kev classifier. Do not build them in the foundation.

**What exists now.** Nothing. There is no product code. You build from an empty repo.

**Source of truth.** This brief is a map. The archive is the source. If they disagree, write a Question Record.

## Part 3. Memory and authority

**Memory rules**

- MEM-01 The repo is your only memory. You MUST NOT rely on chat history, recall, or a past session.
- MEM-02 When the next agent needs something you learned, you MUST turn it into one of these, in this order: a constraint, a test, a FACT, a document line.
- MEM-03 `AGENTS.md` is a map. It has at most 80 lines. It points to deeper files.
- MEM-04 You MUST NOT add skills, rules files, or prompt libraries in the foundation. A lesson that cannot become a constraint goes in `docs/agent/LESSONS.md` with a reason code. The owner reviews each line for encodability every 10 accepted slices.
- MEM-05 You MUST NOT load `archive/` except in the Understanding Session or in a Scribe task.
- MEM-06 Each fact lives in one file. Other files link to it.

**Memory map**

| Path | Holds | Edited by |
| --- | --- | --- |
| `AGENTS.md` | Entry map, at most 80 lines | Owner |
| `docs/agent/EXECUTION.md` | This file | Doc slice with owner approval |
| `docs/product/INTENT-LEDGER.yaml` | Owner words, verbatim | Scribe task only |
| `docs/product/DECISIONS.yaml` | Decision Records with status | Doc slice |
| `docs/product/NORTH-STAR.md` | One page: goal, claims, non-goals | Owner |
| `docs/product/GLOSSARY.yaml` | Terms and banned synonyms | Doc slice |
| `docs/facts/FACTS.yaml` | Verified Facts with expiry | Spike slice |
| `constraints/register.yaml` | Each constraint and its proof | The ratchet |
| `slices/ID/` | Card, records, proof | The slice |
| `failures/`, `questions/` | Failure, Question, and Blocker Records | Any agent |
| `STATE.md` | Generated status | The harness only |
| `archive/` | Read-only history | No one |

**Authority order**

| Level | Source | Changed by |
| --- | --- | --- |
| 1 | Owner words (Intent Ledger) | Owner only |
| 2 | North Star: goal, claims, non-goals | Owner only |
| 3 | Laws (Part 4) | Owner |
| 4 | Decision Records | Owner |
| 5 | Requirements (`requirements.yaml`) | Planner |
| 6 | Slice cards | Planner |
| 7 | Agent judgment | No one |

- AUT-01 A higher level overrides a lower level.
- AUT-02 Each Intent Ledger entry has a status: active, clarified, superseded, or historical. No one deletes or rewords an entry.
- AUT-03 The latest explicit owner decision that supersedes an earlier one governs. The earlier entry stays as history with a `superseded_by` link.
- AUT-04 The Scribe MUST NOT turn a normalized meaning into a locked decision without owner approval.
- AUT-05 When two active items at one level conflict, write a blocking Question Record. Do not choose.
- AUT-06 A default MUST NOT override a law or a higher level.

**Actor classes.** The classes remove the conflict between the data laws and the product claims.

| Actor | Real owner data | Database | Secrets |
| --- | --- | --- | --- |
| Builder agent | No. Fixtures only. | Test database only | None |
| Verifier agent | No. Fixtures only. | Test database only | None |
| Runtime agent | Yes, through the API or MCP, in granted scopes | Never | A scoped token only |
| Arivo worker | Only the owner scope of its job | Through the kernel | Service credentials from the environment |
| Owner | All | Through owner commands | Holds the keys |

## Part 4. Laws

A law is a constraint with a check. A law with no check is debt. The file `constraints/register.yaml` lists each law, its level, its mechanism, and its status.

**The constraint ladder**

| Level | Name | Example | What it does |
| --- | --- | --- | --- |
| C1 | Type system | A branded ID type. A function that needs an `OwnerScope`. | The code does not compile. |
| C2 | Database | A trigger, a foreign key, row-level security. | The write does not commit. |
| C3 | Lint and architecture rule | A banned import. A boundary rule. | Lint fails. |
| C4 | Executable test | A property test. A fault test. | The suite fails. |
| C5 | Gate and CI | Scope check, red check, signed tag. | The merge is blocked. |
| C6 | Document | A line in this file. | It depends on you. |

- LAD-01 Choose the highest level that works.
- LAD-02 A C6 rule MUST carry a reason code: `no-mechanism`, `needs-owner`, or `waiting-for-slice`.
- LAD-03 When a mistake repeats, move its constraint up one level or more.

**Truth**

| ID | Law | Level | Check | Live at |
| --- | --- | --- | --- | --- |
| LAW-01 | You MUST NOT claim a result without a proof file that the harness made. | C5 | The gate compares the Proof Sheet with the run records. | F-03 |
| LAW-02 | You MUST NOT state a fact about a tool, model, library, or standard from memory. You MUST cite a FACT ID or run a spike. | C5 | The audit flags a version number or product claim with no FACT ID. | F-03 |
| LAW-03 | When no file answers a question, you MUST write a Question Record and follow its class. | C5 | The gate fails while a blocking Question Record is open. | F-03 |
| LAW-04 | Your final report MUST list what you did not verify. | C5 | The Proof Sheet schema requires the list. | F-03 |

**Scope**

| ID | Law | Level | Check | Live at |
| --- | --- | --- | --- | --- |
| LAW-05 | One slice changes one behavior inside the size limits. | C5 | SIZE check | F-03 |
| LAW-06 | You MUST change only the paths in the card scope. | C5 | SCOPE check on the diff | F-03 |
| LAW-07 | You MUST NOT edit a protected path. Only an owner-approved intent-change slice CAN. | C5 | CODEOWNERS and PROT check | F-00 |
| LAW-08 | You MUST NOT add a dependency without an approval note. | C5 | Lockfile check | F-00 |
| LAW-09 | You MUST NOT weaken a constraint. This means: lower a threshold, remove a test, reduce a lint level, or widen a scope. | C5 | Ratchet check on `gates/` and `constraints/` | F-03 |
| LAW-10 | New code MUST use the kernel. You MUST NOT add a second way to do what the kernel does. | C3 | Boundary lint and scaffold conformance | F-02 |

**Method**

| ID | Law | Level | Check | Live at |
| --- | --- | --- | --- | --- |
| LAW-11 | You MUST commit each new test alone and see it fail for the stated reason before you change code. The red record is frozen. | C5 | RED check | F-03 |
| LAW-12 | You MUST run the real stack for each behavior change. | C5 | The Proof Sheet needs a real-run transcript. | F-04 |
| LAW-13 | A test MUST read system state through a path that the code under test does not control. | C4 | Mutation test and known-bad build | F-04 |
| LAW-14 | The final commit MUST have a passing `make fast` record. | C5 | The gate checks the run record. | F-03 |
| LAW-15 | For a defect, you MUST write a failing reproduction before the fix. | C5 | RED check | F-03 |
| LAW-16 | After 3 failed cycles, you MUST stop and write a Blocker Record. | C5 | Cycle counter | F-03 |
| LAW-17 | You MUST keep no state outside the repo. A new session MUST be able to resume from files. | C4 | Resume test | F-09 |
| LAW-18 | After a failure, you MUST run the ratchet before the next slice. | C5 | The gate fails while a Failure Record has no constraint or approved debt. | F-03 |

**Product**

| ID | Law | Level | Check | Live at |
| --- | --- | --- | --- | --- |
| LAW-19 | Evidence rows MUST NOT change after commit. The owner-run purge command is the only exception. | C1 | No update or delete function exists. Database triggers reject both. SQL lint. | F-06 |
| LAW-20 | A derived row MUST carry provenance: run ID, versions, input hash. | C1 | `writeDerived` type. NOT NULL columns. | First derived table |
| LAW-21 | Every write MUST carry an owner scope and an actor. | C1 | `OwnerScope` type. NOT NULL columns. Row-level security. | F-05 |
| LAW-22 | No query MAY cross owners. | C2 | Row-level security. Composite keys. Two-owner test. | F-06 |
| LAW-23 | A command MUST be atomic and idempotent. It MUST acknowledge after the commit. | C1 | `defineCommand`. Property and fault tests. | F-07 |
| LAW-24 | Code MUST NOT call ambient time, randomness, ID generation, network, or environment outside adapters. | C3 | Lint | F-02 |
| LAW-25 | Closed vocabularies MUST come from one schema source. | C3 | Codegen drift check | F-06 |
| LAW-26 | Runtime agents MUST NOT reach the database. They use the API or MCP with scoped tokens. | C3 | Boundary lint and the NG-02 test | F-08 |
| LAW-27 | No pipeline stage MAY wait for an owner action. | C4 | NG-01 scan | F-08 |
| LAW-28 | Builder and verifier agents MUST NOT read real owner data or secrets. | C5 | Secret scan. Fixture-only repo. Sandbox. | F-00 |
| LAW-29 | No generative model MAY run inside Arivo’s pipeline. | C4 | NG-03 scan | F-08 |

**The proactive set.** The foundation builds in advance only the constraints that cost much to add later: LAW-07, 08, 19, 21, 22, 23, 24, 25, and 28, plus the harness checks. All other constraints come from the ratchet (Part 8) after a real failure. Do not invent constraints for failures that have not happened.

**Question classes**

| Class | Use when | Action |
| --- | --- | --- |
| Blocking | The answer affects data loss, a security boundary, owner intent, an irreversible action, a protected path, the kernel, or a law. | Stop the slice. Write the Question Record. Continue only independent slices. |
| Defaultable | The choice is low risk and one file or one constant reverses it. | Write the Question Record with a default and a reason. Use the default. List it in the Proof Sheet. The owner CAN override it at the next touchpoint. |
| Non-blocking | The answer does not affect the current slice. | Write the Question Record. Continue. |

- QST-01 The question sets the class. Speed does not.
- QST-02 A question that meets a Blocking condition MUST NOT become defaultable.
- QST-03 A default becomes a Decision Record with status `default` and a gate at which it locks.

**Stop conditions.** When one is true, write the record, commit it, and end the session with a one-line status.

- STOP-01 A blocking Question Record is open for the slice.
- STOP-02 The slice failed 3 cycles.
- STOP-03 The change needs a path outside the scope.
- STOP-04 The harness is red.
- STOP-05 Two laws conflict.
- STOP-06 The task asks you to weaken a constraint.
- STOP-07 The owner words conflict with another file.
- STOP-08 You cannot verify a fact that the slice needs.

**Changing a law.** Only the owner changes a law (class C2). You CAN propose a change in a Question Record.

## Part 5. Session 0: the Understanding Session

The owner starts your first session in plan mode. Plan mode limits your permissions. It is not a thinking limit and not a hard sandbox. Obey the rules below.

- UNS-01 The session is read-only. You MUST NOT modify a file.
- UNS-02 Read in this order: `AGENTS.md`, this file, `archive/principles/`, `archive/owner-words/`, `archive/ai-docs/`, `archive/reviews/`.
- UNS-03 If the corpus does not fit in your context, work in passes and say so. Pass 1: owner statements. Pass 2: decisions. Pass 3: contradictions. Pass 4: plan.
- UNS-04 You MUST copy owner statements. You MUST NOT summarize them.
- UNS-05 You MUST take owner statements from `OWNER:` turns only.
- UNS-06 You MUST mark each claim with its source path. If no file says it, write `not in the repo`.
- UNS-07 You MUST NOT start work. You MUST end with the report.

**The Understanding Report** has these sections in this order.

1. Mission: the goal in 10 lines, in your own words.
2. Owner intent: a table with ID, verbatim quote, source file and line, meaning, tag, and status.
3. Decisions: each decision in the archive with status locked, default, superseded, or unclear. Cite the owner words that adopted it.
4. Contradictions: each place where two files disagree. Name both files. Name the authority rule that resolves it, or say that none does.
5. Unverified facts: each claim about a tool, model, library, or platform that you could not verify from the repo. Do not assert them.
6. Questions: each one classified as Blocking, Defaultable, or Non-blocking. Give a default and a reason for each Defaultable one.
7. Foundation plan: restate F-00 to F-09. List each change you propose and why.
8. Stack and layout: confirm or challenge Part 6 with reasons.
9. Risks: the five most likely ways this build drifts, and the constraint that stops each.

## Part 6. Agent-friendly architecture

Code in this repo is for agents first. The owner reads behavior, not code. Humans no longer pay the cost of unreadable code. Agents pay the cost of a large search space, hidden state, and silent failure. These principles cut those costs.

- AFA-01 One way. Each concern has one primitive. Agents copy what exists. Two ways become ten.
- AFA-02 Impossible by construction. Prefer a type error or a database rejection to a rule.
- AFA-03 Locality. The schema, the handler, the bindings, and the tests of one behavior sit in one folder.
- AFA-04 Explicit over clever. No decorators, no runtime reflection, no global state, no dynamic import, no deep inheritance.
- AFA-05 Greppable. Names are unique. Each failure has one error code.
- AFA-06 Diagnostic errors. Each lint rule and each runtime error prints WHAT, FIX, and REF.
- AFA-07 Fast loop. `make fast` takes at most 60 seconds. `make verify` takes at most 10 minutes.
- AFA-08 Golden path. One exemplar slice exists. New code copies it. `make new-slice` generates from it.
- AFA-09 Small blast radius. The size limits in Part 7 apply.
- AFA-10 Deterministic by construction. Ports inject time, IDs, and randomness.
- AFA-11 Performance is a tested budget. Do not trade it for abstraction. Add a budget test when a hot path exists.
- AFA-12 Do not add indirection, layers, or comments for human taste. Do not remove structure that shrinks the search space. A comment MUST state a constraint that code cannot express, with a REF.

**The kernel.** The kernel is the small framework that makes anti-patterns impossible. Each primitive has one job.

| ID | Primitive | Contract | Makes impossible |
| --- | --- | --- | --- |
| K1 | Ids | Branded UUIDv7 types for each entity. Only `IdGen` makes them. | Passing the wrong ID. Ambient randomness. |
| K2 | Ports | `Clock`, `IdGen`, `Random`, `BlobStore`, `Embedder`, `Kev`, `Notifier`. Each has a fake and a contract test. | Ambient effects. Untestable code. |
| K3 | Scope | `OwnerScope` holds the owner ID and the actor. Each data function takes it. | Cross-owner access. A write with no actor. |
| K4 | Tx | `withOwnerTx(scope, fn)` is the only way to get a transaction. It sets the session values for row-level security. The driver pool is not exported. | A query with no scope. A partial write. |
| K5 | Command | `defineCommand` wraps a handler. It does idempotency (client ID plus payload hash, 409 on mismatch), one transaction, an outbox row, an event row, the actor, and acknowledge after commit. | A non-idempotent write. Success before commit. A missing outbox row. |
| K6 | Evidence | `insertFragment` and `appendRevision`. No update or delete function exists. | Evidence mutation. |
| K7 | Derived | `writeDerived(kind, rows, provenance)` needs run ID, versions, and input hash. | A derived row with no provenance. |
| K8 | Errors | `Result` with a closed error-code registry. Each code maps to an HTTP status and an MCP error. No throw crosses a boundary. | A swallowed error. An untyped failure. |
| K9 | Vocab | Closed vocabularies live in `schema/vocab/`. Codegen makes types, database constraints, and docs. | A mistyped kind. Drift between code and database. |
| K10 | Registry | Each command is registered once. HTTP routes, CLI commands, and MCP tools come from the registry. | Adapter privilege. Hand-written routes that diverge. |

- KER-01 A feature imports the kernel and the schema only.
- KER-02 The kernel imports no feature and no adapter.
- KER-03 A kernel change needs a `kernel` slice and owner approval (class C2).
- KER-04 If a feature needs a primitive that the kernel lacks, write a blocking Question Record. Do not write a local substitute.

**Layout (a proposal; the Understanding Session confirms it)**

```
src/
  app.ts              composition root: the only file that wires features to adapters
  kernel/             primitives K1 to K10
  schema/             vocab sources, SQL migrations, generated types
  features/<name>/    one folder for each behavior: schema, command, sql, tests
  adapters/           db, http, cli, mcp, clock, ids, blob (implement the ports)
harness/              checks, known-bad builds, proof, exams      (protected)
gates/                thresholds, owner.pub, signatures           (protected)
constraints/          register.yaml, lint rules                   (protected)
docs/agent/  docs/product/  docs/facts/  docs/adr/
slices/  phases/  fixtures/  exam/  evidence/  failures/  questions/
archive/              read-only history
```

- BND-01 A feature imports `kernel` and `schema` only.
- BND-02 The kernel imports no feature and no adapter.
- BND-03 An adapter imports `kernel` and `schema`. It MUST NOT import a feature.
- BND-04 Only `adapters/db` imports the database driver.
- BND-05 Only `adapters/http` imports the HTTP framework.
- BND-06 Only `adapters/clock` reads time. Only `adapters/ids` makes IDs.
- BND-07 Product code MUST NOT import `harness`.
- BND-08 A feature MUST NOT import another feature. Shared code moves to the kernel through a kernel slice.

**Stack defaults.** Library names are not fixed. Pick each one through a spike or a FACT entry. Do not pick from memory (LAW-02).

| Concern | Default | Why | Verify with |
| --- | --- | --- | --- |
| Language | TypeScript with strict flags, including `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` | One language covers the API, workers, MCP adapter, CLI, and the later desktop client. Branded types cover K1 to K9. | Spike S-02 |
| Runtime | Node LTS with ESM | One runtime for all parts | FACT |
| Packages | One pnpm workspace | One lockfile | FACT |
| Database | PostgreSQL in a container. pgvector later. | Triggers, constraints, and row-level security carry laws at level C2. | Spike S-02 |
| Migrations | Plain SQL files. Forward-only. Checksums. Types generated from the live schema. | SQL states C2 constraints most directly. | F-04 |
| Validation | One schema library at every boundary | One way to validate | FACT |
| Tests | One runner, one property-test library, one mutation-test tool | One way to test | FACT |
| Architecture checks | A dependency-boundary tool plus custom lint rules | Mechanical enforcement | F-02 |
| Formal models | TLA+ for the named state machines | Finds state-machine bugs before code | F-07 |
| Entry point | `make` | One command surface for every host | F-00 |

Rust gives stronger guarantees but a slower edit-verify loop and a second toolchain for the client. Python has weak static guarantees. If you find a strong reason to change the stack, write a blocking Question Record.

**The golden path**

- GP-01 Slice F-08 is the golden path. It is the first real behavior.
- GP-02 The scaffolder copies its structure.
- GP-03 A new behavior MUST match the scaffold. A conformance check compares the folder shape and the imports.
- GP-04 If the golden path has a defect, fix the golden path first. Then sweep every copy.

## Part 7. The verification loop

**Commands**

| Command | Result | Budget |
| --- | --- | --- |
| `make state` | Print `STATE.md`: phase, open slices, open questions, constraint status, last gate | 5 seconds |
| `make fast SLICE=id` | Typecheck, lint, unit tests, and the slice database tests | 60 seconds |
| `make red SLICE=id` | Run the committed tests. Record the failures against the test commit |  |
| `make real-run SLICE=id` | Start the real stack. Drive it as a user. Record the transcript and state snapshots |  |
| `make falsify SLICE=id` | Run property, fault, differential, and mutation tests with fresh seeds |  |
| `make prove SLICE=id` | Build the Proof Sheet from run records |  |
| `make gate SLICE=id` | Run all mechanical checks. Exit 0 or 1 |  |
| `make verify` | Run every check for the whole repo. CI runs this | 10 minutes |
| `make known-bad` | Apply each known-bad build. Expect each failure code |  |
| `make audit` | Intent trace, requirement sync, drift, banned terms, secrets, FACT IDs, language lint |  |
| `make new-slice NAME=x` | Generate a slice folder from the golden path |  |
| `make entropy` | Report dead code, stale FACTs, flaky tests, and unused constraints |  |

Each failure prints one record with these fields: `code`, `what`, `fix`, `ref`, and `seed`. Read the record. It names the cause and the repair.

**The slice cycle**

1. Run `make state`. Read the card.
2. Write `understanding.yaml`. It MUST have zero unknowns.
3. Write the tests from the card. Commit them alone. Run `make red`. Each test MUST fail for the stated reason.
4. Write code inside the scope. Run `make fast` after each change.
5. Run `make real-run`. Drive the real stack as a user.
6. Run `make falsify`. Fix each failure. A failure prints its seed.
7. Run `make prove`.
8. Run `make gate`. It MUST exit 0.
9. Open the pull request. CI runs `make verify`. CI is the authority.
10. A cycle covers steps 3 to 8. After 3 failed cycles, stop (LAW-16).
11. If a failure occurred, run the ratchet before the next slice (LAW-18).

**Size limits.** The numbers are starting values in `gates/thresholds.yaml`. Only the owner raises or lowers them.

- SIZE-01 One slice changes one behavior.
- SIZE-02 At most 8 source files and 400 source lines.
- SIZE-03 At most 6 test files, 800 test lines, and 200 fixture lines. A generated file does not count if a command makes it again byte for byte.
- SIZE-04 At most 3 requirement IDs and 1 migration.
- SIZE-05 The context pack has at most 12,000 tokens.

When a card exceeds a limit, the Planner MUST split the card.

**Proof Sheet and red record**

- PRF-01 The harness builds the Proof Sheet from run records. You MUST NOT edit it.
- PRF-02 The sheet holds: header (slice, commit, harness version, seeds), owner words, claims with proof IDs, real-run summary, must-reject results, independent state reads, fault and differential results, known-bad result, scope report, defaults used, not-verified list, and open questions.
- RED-01 The harness hashes the red tests and records their failures.
- RED-02 At the gate, each red test hash MUST match, unless an amendment record exists.
- RED-03 An amendment CAN add assertions. It MUST NOT remove or weaken them. The Verifier approves it.

**Known-bad builds**

- KB-01 Each constraint MUST have a known-bad build.
- KB-02 A known-bad build is a patch in `harness/known-bad/` with a target law, an expected failure code, and an `active_from` slice.
- KB-03 The runner applies each active patch to a clean copy, runs the check, and expects the code.
- KB-04 The harness known-bad builds are active from F-03. A product known-bad build is active when the behavior it targets exists. A phase exam MUST NOT need a behavior that does not exist.
- KB-05 A missed known-bad build makes the harness red. All build slices stop until a harness slice repairs it.
- KB-06 Each Failure Record adds a known-bad build, or states why none is possible.

**The Verifier**

- VRF-01 The Verifier uses a fresh context and did not write the code.
- VRF-02 The Verifier reads the card, the Proof Sheet, and the diff only.
- VRF-03 The Verifier writes failing tests. It MUST NOT edit product code.
- VRF-04 The Verifier reports only failures it can reproduce, with test, seed, and command.
- VRF-05 The report is advisory. The gate decides. The Verifier CAN use another model.

**Walls, CI, and signed gates**

- WALL-01 `main` is protected. A pull request and the check `verify` are required. No force push.
- WALL-02 CODEOWNERS covers the protected paths. The owner approves changes to them.
- WALL-03 The agent credential cannot change workflow files and cannot sign.
- WALL-04 A phase gate is a tag that the owner signs. CI verifies it against `gates/owner.pub`.
- WALL-05 You MUST NOT hold the owner private key.
- WALL-06 Local `make verify` is a preflight. CI is the authority.

**Exams and thresholds**

- EXAM-01 The Context Exam has 25 questions. The harness prints the questions with no key. You answer in a file. The owner grades it with a key that stays outside the repo.
- EXAM-02 The pass mark is 90 percent, with every trap question correct.
- EXAM-03 The Agent Exam starts in the phase that exposes MCP. It has a fresh set and a sealed set about the Fixture Life.
- EXAM-04 Each Agent Exam set needs 90 percent. The critical classes need 100 percent: a fabricated source reference, and a cross-owner exposure.
- EXAM-05 The sealed set stays outside the repo. The owner runs it. The report shows the aggregate score only. The owner replaces part of the set at each gate.
- EXAM-06 Each run records the model, the host, the test version, the seed, and the score.
- EXAM-07 Fixture seeds and fault seeds are separate sets.

**The phase loop**

- LOOP-01 A phase is a loop: build slices, run the Phase Exam, repair gaps, repeat. It has no time limit.
- LOOP-02 Gap weights: critical 8, high 4, medium 2, low 1.
- LOOP-03 After 5 loops with no drop in the weighted gap score and no gain on a measured dimension, the Planner MUST freeze the phase and write a Stuck Report. The owner decides.
- LOOP-04 A phase exits when all requirements pass, earlier tests pass, the known-bad catch rate is 100 percent, no critical or high gap is open, the Demo Review has no open surprise, two consecutive runs with different seeds pass, and the owner signs the tag.
- LOOP-05 An owner preference that is not ratified MUST NOT become a mandatory test. Each active requirement traces to owner words or an adopted decision. A requirement with no intent fails the audit.

## Part 8. The constraint ratchet

Every mistake becomes a constraint. Agents copy what exists, so an unfixed mistake teaches the next agent.

- RAT-01 Record the failure in `failures/FAIL-NNN.yaml` in the same session.
- RAT-02 Write the known-bad build first. It reproduces the failure and fails the gate. Do not fix the symptom before this step.
- RAT-03 Choose the highest ladder level that works (Part 4).
- RAT-04 Build the constraint. Run the known-bad build. It MUST fail with the stated code.
- RAT-05 Sweep. Search the whole repo for the same pattern. Fix every instance in the same slice.
- RAT-06 Register the constraint in `constraints/register.yaml`.
- RAT-07 If the same class repeats, move the constraint up a level. If a C1 or C2 design exists, build it.
- RAT-08 If no constraint is possible, write a lesson with a reason code (MEM-04).

| The mistake is about | Prefer |
| --- | --- |
| Passing the wrong kind of value | C1: a distinct or branded type |
| Data that must never change or cross owners | C2: a database rule, and C1: an API with no such function |
| Calling something that must not be called | C3: a banned-API lint rule |
| Importing across a boundary | C3: a boundary rule |
| A wrong result in one case | C4: a test. Then ask if a type could prevent the case. |
| A skipped step in the process | C5: a gate check |
| Unclear intent | C6: a document line with a Question Record |

## Part 9. Foundation slices

The slices run in this order. A slice starts after the previous slice is accepted. The Planner writes each card in `slices/F-NN/card.yaml` from this part. Spike S-01 and spike S-02 run inside F-00.

### F-00. Repository skeleton and walls

- Goal: a repo that verifies itself from an empty state.
- A clean clone runs `make verify` and passes: typecheck, lint, tests, audit, secret scan.
- A deliberately broken file makes `make verify` fail.
- CI runs `make verify` as the required check `verify`.
- CODEOWNERS covers `harness/`, `gates/`, `constraints/`, `.github/`, `docs/agent/`, `docs/product/INTENT-LEDGER.yaml`, `archive/`, and applied migrations.
- A lockfile check rejects a dependency with no approval note.
- A devcontainer file defines the sandbox. It holds no personal keys.
- `AGENTS.md` matches Appendix A.
- S-01 records which host loads `AGENTS.md`, with a sentinel line and a transcript. S-02 records the stack check: strict compile, container database start, one migration.
- Proof: E1, E4, known-bad. Constraints: LAW-07, 08, 28.

### F-01. Memory seed

- Goal: the memory files exist and agree with the archive.
- `INTENT-LEDGER.yaml` holds each owner statement verbatim with ID, source line, meaning, tag, and status.
- `make audit-intent` accepts a quote only if it sits inside an `OWNER:` turn in `archive/owner-words/`. A known-bad ledger with a false quote fails.
- `DECISIONS.yaml` lists each decision with status locked, default, or superseded, and the owner words that adopted it.
- `NORTH-STAR.md` has one page. `GLOSSARY.yaml` defines the terms. `FACTS.yaml` holds the S-01 and S-02 results.
- `constraints/register.yaml` lists LAW-01 to LAW-29 with level, mechanism, and status. The status `planned` is allowed. The status `enforced` needs a known-bad build.
- `make state` prints open questions and constraint status.

### F-02. Constraint toolchain

- Goal: the first mechanical constraints, with diagnostics.
- Lint rules ban ambient time, randomness, ID generation, network, and environment access outside adapters (LAW-24).
- Boundary rules enforce BND-01 to BND-08.
- A rule bans a `catch` that swallows an error.
- An SQL lint bans UPDATE and DELETE on evidence tables outside the purge module.
- Each rule prints WHAT, FIX, and REF. Each rule has a known-bad fixture that fails with the right code.
- Constraints: LAW-10, 24, and the SQL part of LAW-19.

### F-03. Harness core

- Goal: proof, scope, and gate checks that agents cannot fake.
- Run records hold seed, commit, tool versions, and result.
- `make prove` builds the Proof Sheet from run records. A hand-edited sheet fails the gate.
- The gate runs the SCOPE, SIZE, PROT, RED, SKIP, FAST, ratchet, and open-question checks.
- `make known-bad` runs these harness known-bad builds: scope breach, protected-path edit, skipped test, hand-written Proof Sheet, lowered threshold, missing red record, test edited after red, unapproved dependency.
- A missed known-bad build sets the harness to red. The gate then fails for every slice.
- Constraints: LAW-01, 03, 04, 05, 06, 09, 11, 14, 15, 16, 18.

### F-04. Real database foundation

- Goal: tests and real runs use a real database, and migrations cannot be rewritten.
- One command starts an ephemeral PostgreSQL container and resets it the same way each time.
- The migration runner is forward-only and stores checksums. An edit to an applied migration fails the gate.
- `independentRead` uses a separate connection and role. Tests use it for assertions.
- `make real-run` starts the stack, runs a script as a user, and stops the stack.
- A mutation test on the test helpers shows that a test which trusts the code under test fails.
- Constraints: LAW-12, 13, and PROT-04.

### F-05. Kernel v0

- Goal: IDs, ports, results, and scope that make wrong code fail to compile.
- K1 branded IDs. K2 ports `Clock`, `IdGen`, and `Random` with fakes. K3 `OwnerScope`. K4 `withOwnerTx`. K8 `Result` with an error-code registry.
- Compile-fail tests prove: a fragment ID cannot pass as a revision ID. A data function cannot run without a scope.
- The driver pool is not exported. A known-bad build that imports it fails BND-04.
- Constraints: LAW-21 and the type part of LAW-24.

### F-06. Ground-truth schema v0

- Goal: tables whose rules the database enforces.
- Tables: node, fragment, revision (with a hash chain), behavior\_event, tag\_event, outbox, event\_log. Each row has `owner_id` and `actor`.
- Row-level security is on. Composite keys block cross-owner references.
- Triggers reject UPDATE and DELETE on revision, behavior\_event, and tag\_event.
- Closed vocabularies come from `schema/vocab/`. Codegen makes types and constraints. A drift check fails when they differ.
- The negative suite has one violating statement for each invariant. The database rejects each one.
- The two-owner test shows no cross-owner read or write.
- Constraints: LAW-19, 22, 25.

### F-07. Command framework

- Goal: one way to write. It is idempotent, atomic, and acknowledged after the commit.
- K5 `defineCommand`, K6 the evidence API, K10 the registry.
- Replaying a command N times makes one item. The same ID with a different body returns 409.
- A fault run kills the process at each crash point. After restart, the state equals the clean run.
- A TLA+ model of capture and the client outbox passes. Its seeded bug is found.
- Known-bad builds: skip the idempotency check, return success before commit, skip the outbox write.
- Constraint: LAW-23.

### F-08. Golden path: capture a highlight

- Goal: the first real behavior. All later slices copy it.
- One command registers `captureHighlight`. The HTTP and CLI bindings come from the registry.
- One transaction writes the highlight, the first revision, the anchors, the search text, the outbox row, the event row, and the behavior event.
- A keyword search finds the new highlight at once.
- A tag attaches at capture: typed (`fact`, `concept`) or free. Each tag is an event.
- `make real-run` drives the CLI as a user. 1,000 kill trials lose zero acknowledged highlights.
- The scans for NG-01, NG-02, and NG-03 pass.
- The owner runs the 12 adversarial checks and reads the code once.
- Claim shown: part of C1. Constraints: LAW-26, 27, 29.

### F-09. Scaffold and one-shot proof

- Goal: show that the repo is memory enough for a fresh agent.
- `make new-slice NAME=x` generates a folder from the golden path with a card, test skeletons, and a conformance check.
- The resume test passes: a new session finishes a half-done slice from files only.
- A fresh agent with `AGENTS.md` and a card builds capture-note. It passes the gate on cycle 1. The owner makes zero edits.
- A second fresh agent does the same for capture-bookmark.
- Each deviation becomes a ratchet entry before the next attempt.
- Constraint: LAW-17.

## Part 10. Foundation exit

- FX-01 The known-bad catch rate is 100 percent.
- FX-02 Two one-shots in a row pass (F-09).
- FX-03 The Context Exam passes for two agents in fresh sessions.
- FX-04 `make fast` takes at most 60 seconds. `make verify` takes at most 10 minutes in CI.
- FX-05 Each law is `enforced`, or `planned` with an owner-approved reason. No law rests on prose alone without a LAD-02 reason code.
- FX-06 The owner signs the tag `foundation-1`. CI verifies the signature.
- FX-07 The corpus is closed. No top-level document exists outside the memory map.
- FX-08 No blocking Question Record is open. Each default has a lock gate.

After the exit, the product phase map in `docs/product/` governs. Plan one phase ahead only (NG-04).

## Appendix A. `AGENTS.md`

```
# Arivo: agent entry file

Arivo is a reading and study environment. Nothing is lost. New input raises the value of old input.
The owner's agents can use all of it.
This file is a map. Rules live in docs/agent/EXECUTION.md. Proof lives in the harness.

## Boot
1. Run: make state
2. Read the active card: slices/<ID>/card.yaml
3. Read docs/agent/EXECUTION.md Parts 1 to 4, and the parts the card lists.
4. Write slices/<ID>/understanding.yaml
5. Follow the cycle in EXECUTION.md Part 7.

## Commands
make state | fast | red | real-run | falsify | prove | gate | verify | known-bad | audit | new-slice NAME=x

## Hard rules
- The repo is your memory. Do not rely on chat history or recall.
- Change only the paths in the card scope.
- Do not edit protected paths: harness/, gates/, constraints/, .github/, applied migrations,
  frozen tests, docs/agent/, docs/product/INTENT-LEDGER.yaml, archive/.
- Do not claim a result without a harness proof file.
- When no file answers a question, write a Question Record and follow its class.
- After 3 failed cycles, stop and write a Blocker Record.
- Do not read real owner data or secrets.
- A mistake that happens twice becomes a constraint. Run the ratchet: EXECUTION.md Part 8.

## Where things are
docs/agent/EXECUTION.md     rules, laws, loop, slices
docs/product/               intent, decisions, north star, glossary
docs/facts/FACTS.yaml       verified facts
constraints/register.yaml   every constraint and its proof
src/kernel/                 primitives. Features import the kernel and schema only.
src/features/               one folder for each behavior
slices/<ID>/                card, records, proof
failures/  questions/       records
archive/                    read-only history. Load only in the Understanding Session.
```

## Appendix B. Templates

**Slice card**

```yaml
id: F-08
type: build               # build, kernel, spike, defect, doc, intent-change
title: Capture a highlight
intent: [INT-002, INT-029]
requirements: [CAP-01, CAP-02]
scope:
  allow: [src/features/capture-highlight/, src/schema/migrations/0008*]
  deny: [harness/, gates/, constraints/]
acceptance:
  - given: an empty database
    when: the CLI captures highlight H1 with body A
    then: the API returns 201 and one revision exists
must_reject:
  - {input: highlight H1 with body B, error: 409 IDEMPOTENCY_CONFLICT}
proof: [E2, E3, E4, E5, E7, E8]
known_bad: [KB-F08-01, KB-F08-02]
context_pack: [LAWS, K5, K6, GP]
budget: {cycles: 3}
```

**Understanding Record**

```yaml
slice: F-08
intent_restated: The owner must never lose a highlight. A repeat send must not make a second item.
scope_restated: [src/features/capture-highlight/]
must_reject_restated: [The same ID with a different body returns 409.]
unknowns: []              # a list that is not empty stops the slice
facts_used: [FACT-007]
plan: [write tests, write handler, run the real stack]
```

**Question Record.** A Blocker Record has the fields `id`, `slice`, `cycles`, `last_failure`, `tried`, and `need`.

```yaml
id: QR-012
class: defaultable        # blocking, defaultable, non-blocking
slice: F-08
question: The card does not give the settle time for a draft.
options: {A: 3 seconds idle, B: 30 seconds idle}
default: A
reason: A loses less text after a crash.
locks_at: foundation-1
```

**Failure Record and Constraint Record**

```yaml
id: FAIL-004
class: scope              # misread, gap, gaming, scope, fake-success, regression, flaky, harness, drift
slice: F-03
what: The agent edited a frozen test to pass the gate.
cause: The guard did not cover the test folder.
constraint: CON-014
known_bad: KB-F03-05
---
- id: CON-014
  law: LAW-07
  statement: The agent MUST NOT edit a frozen test.
  level: C5               # C1 type, C2 database, C3 lint, C4 test, C5 gate, C6 document
  mechanism: harness/checks/protected-paths
  proof: KB-F03-05
  origin: FAIL-004
  status: enforced        # enforced, planned, waived
```

**Intent Ledger entry and Verified Fact**

```yaml
- id: INT-029
  says: 'losing a highlight'       # verbatim, from an OWNER: turn
  source: archive/owner-words/2026-10-13.md:412
  means: The worst failure is losing a captured highlight.
  tag: constraint                  # goal, constraint, preference, decision, non-goal, question
  status: active                   # active, clarified, superseded, historical
  superseded_by: null
  legacy_ids: []
---
- id: FACT-001
  statement: The agent host loads AGENTS.md at session start.
  method: spike S-01               # spike, search, official document
  proof: proofs/S-01/
  verified_on: 2026-10-13
  expires: when the host version changes, or after 90 days
```

## Appendix C. Owner words added since Execution System v1

INT-001 to INT-018 are in Appendix A of the archived Execution System v1. Carry them into the ledger unchanged. The two posts the owner pasted are principles, not owner words. They live in `archive/principles/`. If an ID here collides with an ID from another document, keep both. Record the old ID in `legacy_ids`.

```yaml
- {id: INT-019, tag: goal, says: 'the day arivo works i would import my convos and research and start reasoning through it make notes and everything, and also add books then make lists and all, articles tooo', means: 'On day one the owner imports conversations, research, books, and articles. The owner reasons, makes notes, and makes lists.'}
- {id: INT-020, tag: goal, says: 'i would connect my agent... i would reason with it maybe while reading.. or off reading.. maybe a summary', means: 'The owner connects an agent and reasons with it, while reading or away from reading.'}
- {id: INT-021, tag: preference, says: 'add small features like dictonory with meanings and you know raw pen/pencil where i can like do rough work on jorunals/book', means: 'Later features: a dictionary with meanings, and a pen layer for rough work on journals and books.'}
- {id: INT-022, tag: goal, says: 'everything compounds like its a whole new brain forming up of my research, reading, learning, studying, writing', means: 'Everything compounds into a new brain built from the owner research, reading, learning, study, and writing.'}
- {id: INT-023, tag: goal, says: 'i would make journal my writing lab. where i write posts, experimnent, raw writing, test writing, creative writings yk', means: 'The journal is the owner writing lab for posts, experiments, raw writing, and creative writing.'}
- {id: INT-024, tag: preference, says: 'i would keep working on it adding features like connecting x', means: 'Later the owner adds connectors, for example for X, to import posts.'}
- {id: INT-025, tag: constraint, says: 'it should be divided into facts and concepts. Facts are objective statements that can be verified and are known to be true, while concepts are abstract ideas that help us categorize and understand those facts.', means: 'Content divides into facts and concepts. A fact is an objective, verifiable statement. A concept is an abstract idea that categorizes facts.'}
- {id: INT-026, tag: constraint, says: 'i dont wanna miss or loose concepts after a session of resoning through research, and studying', means: 'The system must not miss or lose concepts after a session.'}
- {id: INT-027, tag: constraint, says: 'remove the assumption of slow compounding, slow concepts', means: 'Do not assume slow compounding or slow concept formation.'}
- {id: INT-028, tag: decision, says: 'we can do like tags while i highlight make notes i can give each thing a tag of fact/concept or whatever for intial stage we can do that and system trains on it when it is good enough but thats not my first priority i would make it more like personal wikipedia', means: 'The owner tags items fact or concept at capture. The system learns from tags later. The product behaves like a personal wiki.'}
- {id: INT-029, tag: constraint, says: 'losing a highlight', means: 'The worst failure is losing a captured highlight. Answer to the question which failure breaks trust most.'}
- {id: INT-030, tag: decision, says: 'doesnt matter which agent API/MCP exposed would let any agent connect so it could be multiple', means: 'Any agent connects through the API or MCP. Many agents can connect.'}
- {id: INT-031, tag: constraint, says: 'the repo is the memory. define laws. strict so agent does not drift', means: 'The repo is the agent memory. Laws are strict so agents do not drift.'}
- {id: INT-032, tag: constraint, says: 'just keep at it until what we need is achieved', means: 'Work continues until the goal is achieved.'}
- {id: INT-033, tag: goal, says: 'giving execution agent whole context in plan mode what arivo is and making them reason through everything we have done to starting the repo', means: 'The first agent session gets the whole context in plan mode and reasons through all prior work before the repo starts.'}
- {id: INT-034, tag: goal, says: 'actually design 2 in depth docs one for me one for agent execution. for me state step by step process.', means: 'Two documents: one for the owner with a step by step process, one for agent execution.'}
```
