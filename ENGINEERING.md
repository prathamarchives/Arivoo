# ENGINEERING — The Doctrine This Repo Is Built On

Provenance: `context/raw/engineering transcript.txt` (the trust/verification talk), `context/raw/upstream of engineering transcripts.txt` (the agent-native repository treatise), `context/raw/3.txt` (owner doctrine quotes), `context/raw/Arivo Agent Execution Specification.md` (the law book the doctrine produced). Every section below states the principle, the failure it kills, the mechanism that enforces it here, and where it lives in this repo.

This file is the WHY. `/LAWS.md` is the WHAT (the executable rules). `/OPERATING-MODEL.md` is the HOW (who runs what, and how the system grows). When they disagree: INTENT-LEDGER > NORTH-STAR > LAWS > this file > DECISIONS > PLAN > agent judgment. A disagreement is a Question Record, never a silent choice (AUT-05).

---

## 1. The thesis: the environment produces the quality

**Principle.** Trust in agent work is not a property of the model. It is a property of the environment the work happens in: the verification machinery, the constrained codebase, the paved paths, the enforced boundaries. The engineer's job shifts from writing code to building the system that makes agent code trustworthy by construction.

**The trust economics.** The 1:1-to-1:5 babysitting phase — where every chat needs course-correction and nothing happens without you — is the hardest phase to escape, because the exit is not visible from inside it. You do not escape it with confidence or better prompting. You escape it with verification. Spawning a hundred sub-agents before trust exists produces exactly what you would expect: slop pull requests, regressions, bugs shipped.

**The bottleneck inversion.** "I am the bottleneck, and I need to be able to take all of the knowledge that I have as an engineer and impart them into my team of agents." Knowledge leaves your head and enters the repo: as constraints, as tests, as canonical examples, as diagnostics. Every piece of knowledge that stays in your head is a piece every future agent lacks.

**Michelin kitchen, not software factory.** Agents doing the cooking does not make the work mass production. It stays creative work; you still own the final outcome. What determines the outcome is the kitchen setup: the equipment, the training, the ratios, the station design. In repo terms: the toolchain, the laws, the golden path, the size limits.

**Failure it kills:** agent-output quality attributed to model capability, leading to "try a better model" as the fix, when the fix is the environment.

**Mechanism here:** this entire first layer. The 29 laws in `/LAWS.md`, the slice loop in `/OPERATING-MODEL.md`, the constraint ladder below. The maturity of this repo is measured by how little owner intervention a correct change requires — not by how many rules exist.

---

## 2. The two cuts (owner doctrine, verbatim)

Everything else in this file is elaboration of two sentences. The owner pasted them as the doctrine:

> "1. **The agent checks its own work by running the real thing.** If it cannot, you become the test suite. That does not scale.
> 2. **The codebase is the agent's memory.** Agents copy what exists. Every mistake you see is a missing constraint. Turn it into one. Use the strongest kind you can: a type that will not compile, a database rule that rejects the write, a lint rule that names the fix. Prose rules come last."

**Cut one — self-verification.** An agent's claim about its own work is worth nothing; only empirical evidence is: the real stack started, driven as a user, state read through a path the code under test does not control. This is why `make real-run` and independent reads exist, and why the Proof Sheet is built by the harness and never hand-edited (LAW-01, LAW-13, PRF-01).

**Cut two — the codebase is memory.** Agents extend what already exists in their context window. Every pattern present teaches every future agent. Good patterns compound like capital; anti-patterns spread like a virus — one innocent workaround copied for a few days becomes the de facto pattern for all agents.

**Slop is not weather.** Slop is not something that happens to you. It is what a codebase *produces* when constraints are missing. The response to slop is never "be more careful" — it is a constraint, at the strongest level available.

**The foundation-complete moment (owner's definition):** "Your build is a loop that adds constraints until a fresh agent, with a short card and nothing else, produces a passing change on the first try. That moment ends the foundation."

**Failure it kills:** hand-fixing mistakes. The owner's rule: "You never fix a mistake by hand." A hand-fix teaches nothing; the mistake recurs forever. The ratchet turns it into a permanent defense.

---

## 3. The agent-native repository

**Definition (upstream, verbatim):** "A repo should not merely contain the software. It should contain the knowledge, constraints, and verification machinery that make producing the next correct version of that software easier than producing an incorrect one. This is an engineering discipline, not a prompting technique."

**The central rule (verbatim):** "Every important engineering decision should exist in a form that the agent can discover, and every important enforceable decision should exist in a form that the machine can check."

The distinction is critical. Natural-language guidance is for interpretation. Executable constraints are what stop an agent from repeatedly violating the same rule. This file (ENGINEERING.md) is the discoverable form. `/LAWS.md` + the checks it names are the checkable form.

### The five memory systems

A repository is an executable memory system: five subsystems that must agree with each other.

| # | System | Holds | In this repo | Failure when missing |
|---|--------|-------|--------------|----------------------|
| 1 | Intent memory | Why the system exists, what concepts mean, required behavior, decided trade-offs | NORTH-STAR, INTENT-LEDGER, DECISIONS, GLOSSARY | Agents re-derive the goal wrongly, drift silently |
| 2 | Structural memory | Types, module boundaries, APIs, schemas, ownership, dependency directions, approved primitives | LAWS (kernel/boundary rules), future `src/kernel/`, `src/schema/` | Every agent invents its own architecture |
| 3 | Verification memory | Tests, contracts, static analysis, reproducible scenarios, acceptance criteria | OPERATING-MODEL (loop), future `harness/`, known-bad builds | Correctness claims without evidence |
| 4 | Operational memory | Logs, traces, metrics, error reports, tools to reproduce real failures | future run records, diagnostics contract (§8) | Failures are unreproducible; debugging = archaeology |
| 5 | Evolutionary memory | Past mistakes, rejected approaches, decisions, regressions, environment improvements | failures/, questions/, constraints/register, WORKLOG, this corpus | The same lesson is learned and lost every session |

**The agreement requirement.** The systems must not contradict. A design document that contradicts the types is not good memory. A test suite that fails to detect a known bug is not good verification. A log that says an operation failed without exposing relevant state is not good operational memory.

**The objective function:** minimize the distance between (a) what the system should do, (b) what the code actually does, and (c) what the agent can *establish* about that difference. Documentation volume and tool count are inputs, not outcomes — more is not better; agreement is better.

### Memory types and authoritative homes

Not all memory should look the same. Mixing knowledge kinds into one instruction file is how AGENTS.md becomes an unmaintainable brain. Each kind has an authoritative home:

| Memory type | Answers | Authoritative home in this repo |
|-------------|---------|--------------------------------|
| Intent | What should happen? | INTENT-LEDGER (owner words verbatim) |
| Structural | What can depend on what? | LAWS + schema/ (when built) |
| Behavioral | What must keep working? | tests/ (when built) |
| Explanatory | Why is it designed this way? | DECISIONS + this file |
| Operational | What happened; how to reproduce? | run records, diagnostics |
| Temporary | What remains on this change? | slice cards, understanding.yaml, WORKLOG tail |

**Every duplicated fact creates a synchronization obligation.** Some duplication is useful (a summary in an overview plus detail in a record), but the summary must point at the authority, never become a second independent specification. If a value (say, a size limit) is needed in five places, define it once, derive the rest, and validate at the boundaries that matter.

**Plans are not permanent truth.** An execution plan can go stale as implementation changes; the code, accepted spec, tests, and recorded decisions must never silently disagree with it. This is why PLAN.md is one phase deep (NG-04) and why drift between plan and reality is a Question Record.

**AGENTS.md is a map, not a brain.** At most ~80 lines: where authority lives, which commands run, which constraints apply everywhere. Detailed knowledge lives near its domain. (The OpenAI engineering experience: one large instruction file became impossible to maintain, verify, and navigate; a short entry point plus a structured, versioned knowledge base won.)

---

## 4. The constraint ladder

The hierarchy of enforcement, strongest first. A law's level is the rung it sits on; "choose the highest level that works" (LAD-01).

| Level | Name | Example | What it does |
|-------|------|---------|--------------|
| C1 | Type system | Branded ID type; a function requiring `OwnerScope` | The code does not compile |
| C2 | Database | Trigger, foreign key, row-level security | The write does not commit |
| C3 | Lint / architecture rule | Banned import; boundary rule | Lint fails |
| C4 | Executable test | Property test; fault test | The suite fails |
| C5 | Gate / CI | Scope check, red check, signed tag | The merge is blocked |
| C6 | Document | A line in a law file | It depends on the agent |

- **LAD-01** — choose the highest level that works.
- **LAD-02** — a C6 rule MUST carry a reason code: `no-mechanism`, `needs-owner`, or `waiting-for-slice`. Prose is the last resort and must be honest about being the last resort. (Every law in `/LAWS.md` currently at C6 carries `waiting-for-slice` — the codebase is empty; the mechanism arrives with its phase.)
- **LAD-03** — when a mistake repeats, move its constraint up one level or more.

**The selection guide** (what kind of mistake → what rung):

| The mistake is about | Prefer |
|----------------------|--------|
| Passing the wrong kind of value | C1: a distinct or branded type |
| Data that must never change or cross owners | C2: a database rule, plus C1: an API with no such function |
| Calling something that must not be called | C3: a banned-API lint rule |
| Importing across a boundary | C3: a boundary rule |
| A wrong result in one case | C4: a test — then ask if a type could prevent the case |
| A skipped step in the process | C5: a gate check |
| Unclear intent | C6: a document line with a Question Record |

**The direction of travel.** Upstream's version of the ladder runs: prose → canonical examples → approved primitives → types and contracts → static/structural checks → executable verification → enforced invariants. "When an instruction matters enough to repeat, investigate whether it should become an enforced property of the system." The destination is: **the dangerous decision is unavailable; legitimate design choices stay open.**

**Do not ask an agent to remember what the architecture can enforce.** Four designs of the same requirement, increasing strength:
- **Design A** — prompt-only: a rule in the prompt says "check authorization."
- **Design B** — shared implementation: all protected operations go through one authorization service.
- **Design C** — restricted architecture: modules cannot reach protected resources except through the approved boundary.
- **Design D** — restricted capability: components that don't need the capability never receive the credentials or capability at all. The accidental access path does not exist.

Design D removes an entire class of mistakes. It does not eliminate every bug, but it reduces what an agent must remember to zero for that class. Every Arivo law should be pushed toward its Design D.

**Constraints are products and must earn their complexity.** A constraint is a small software product with: an intended outcome, an enforcement means, a way to test the enforcement, and an exception policy. Before adopting any important custom check, answer: Which concrete failure does it prevent? What is its scope? Does it reject valid implementations (precision)? Does its diagnostic teach repair? Can we demonstrate both a forbidden and an allowed case? Can a legitimate exception be made without silently disabling the rule? Will it stay accurate as the architecture changes? **Every enforcement mechanism needs its own failure tests.** A complexity rule that only measures function length can push an agent into 20 tiny functions that obscure control flow — technically passing, actually worse. Rules that make the system worse get removed. False-positive checks get repaired, not learned-around.

---

## 5. Every failure must become an asset

**The central operating rule of an agent-native repository (upstream):** "A failure should either fix the current implementation or permanently improve the system's ability to prevent, detect, or diagnose that class of failure."

This does not mean every typo gets a lint rule. It means recurring or costly failures must not live only in someone's memory or vanish when a chat session ends.

**The loop (the ratchet, specified in OPERATING-MODEL §Self-healing):**

1. **Observe the failure** — bug, review comment, test failure, duplication, architectural drift.
2. **Preserve a reproducible example** — regression test, fixture, trace, failing command, concrete counterexample. The red record.
3. **Identify the missing capability** — missing context, weak abstraction, missing type, missing check, weak test oracle, poor tooling.
4. **Fix at the strongest appropriate layer** — primitive, schema, type, architecture rule, test, diagnostic, or documentation, in that order of preference.
5. **Verify the guard itself** — prove the original failure is now caught or made harder to produce. This is what known-bad builds are for.

**Classify before fixing.** Not every failure needs a new rule:

| Failure class | Likely durable remedy |
|---------------|----------------------|
| Agent misunderstands a product requirement | Clarify the product contract; add an acceptance test |
| Agent guesses an external data shape | Validate the boundary; use a typed SDK |
| Agent reimplements an existing utility | Improve the canonical API; add a check if duplication remains possible |
| Agent changes unrelated modules | Reduce coupling; clarify ownership/dependency boundaries |
| Agent produces complicated code | Improve abstractions; add targeted complexity checks |
| Tests pass despite incorrect behavior | Strengthen the test oracle, not the test count |
| Agent cannot reproduce a bug | Add fixtures, replay tools, better logs, isolated runtime |
| Documentation disagrees with code | Establish a source of truth; generate or validate derived docs |

**Severity policy:** a single low-severity error needs only a code fix. A repeated failure needs a structural response. A single severe security or data-integrity failure justifies a permanent guard immediately. That is how the repo learns without accumulating hundreds of arbitrary rules.

**The weak response and the strong response.** When an agent adds a third implementation of request validation: the weak response is "follow the existing pattern next time" (prose, forgotten). The strong response is asking *why three valid implementations were possible* — duplicated validation? no shared schema? correct primitive not discoverable? — and shipping the shared validator, the schema-driven API, and the static rule that prevents the old pattern from returning. **The strongest fix is not the strictest rule. It is the smallest architectural change that removes the underlying source of repeated error.**

**The two-strike rule (owner's ratchet):** a mistake that happens twice becomes a constraint; the second occurrence of a class triggers the move up the ladder — refactor to impossible (LAD-03, RAT-07).

---

## 6. Proof-carrying changes

**Principle (upstream):** "An agent must not declare a feature complete merely because it has written code or because a test command exited successfully."

Every meaningful change carries an evidence package appropriate to its risk:

| Change type | Evidence package |
|-------------|------------------|
| Bug fix | Regression test showing the original failure + passing run of required checks |
| Behavior slice | Real-run transcript; must-reject results; independent state reads; fault results |
| Database migration | Successful application to clean DB; preservation of existing data; correct behavior after |
| Performance change | Measurements before and after, same workload |

**The evidence answers four questions:**
1. What was the intended behavior?
2. How was the original problem reproduced?
3. What changed?
4. What independent observation demonstrates the fix works?

**Test execution vs test validity — the shared-misunderstanding trap.** The same misunderstanding can infect the implementation AND its tests: the agent implements wrong behavior, then writes a test that confirms the wrong behavior. Two properties must stay separate:
- **Test execution:** does the implementation satisfy the assertions? (mechanically checkable)
- **Test validity:** do the assertions express the correct requirements? (needs independent oracles)

Oracle independence techniques, in increasing strength: product contracts, independently established expected results, reference implementations, known examples, domain invariants, external observations. Mechanically: regression tests (preserve previously failing behavior), property-based tests (general properties across generated inputs), **mutation testing** (deliberately change implementation behavior; tests must notice), contract tests (boundaries respect agreed shapes), acceptance tests (user-visible outcomes through the real system). Coverage alone is insufficient — a test can execute every line without detecting incorrect behavior. For critical paths: a small strong suite with real failure detection beats a large suite with an impressive coverage percentage.

**Made mechanical here:** the Proof Sheet (harness-built from run records, never hand-edited) is this principle at C5. See OPERATING-MODEL §Verification stack.

---

## 7. Protect the verifier

**The risk.** An agent can make a test pass by weakening the test, removing the assertion, skipping the check, or altering the acceptance criteria. A repository must distinguish **changing application behavior** from **changing the machinery that judges behavior**.

**Higher-risk changes (require reason + review, owner approval once walls are live):**
- Removing or weakening tests
- Changing CI gates
- Adding lint suppressions
- Altering security rules
- Modifying migration validation
- Changing expected acceptance results

Otherwise, in the upstream's words: "the system can gradually learn to look correct without becoming more correct."

**Mechanisms here:** frozen red records (hashes recorded; amendments may add assertions, never remove — RED-02/03) · the ratchet check (LAW-09: lowering a threshold, removing a test, reducing a lint level, or widening a scope fails the gate) · CODEOWNERS on protected paths (harness/, gates/, constraints/, .github/, docs/agent/, INTENT-LEDGER, archive/, applied migrations) · the agent credential cannot change workflow files and cannot sign · phase gates are owner-signed tags verified by CI against `gates/owner.pub` · the Verifier writes failing tests only, never edits product code · the known-bad build for a weakened check is itself a harness known-bad ("lowered threshold" and "test edited after red" are on the F-03 list).

**The trust sub-rule (CI):** a required status check named `verify` is not enough if untrusted integrations can supply a status with that name. Restrict the required check to the expected source application where the host supports it, so the trusted gate is not merely a string. Verified on the installed host version, not assumed from docs (Host Contract).

---

## 8. Diagnostics are part of the architecture

**Principle (upstream):** "Most software tools treat errors as messages for human developers. In an agent-native repo, an error is also an instruction to the next reasoning step."

**Weak vs strong, side by side:**

```
Weak:
  Architecture check failed.

Strong:
  ARCH-012: UI module imports a database adapter.
  Violation:
    src/ui/library-view.tsx -> src/adapters/database/library-repository.ts
  Why:
    UI modules must depend on application interfaces,
    not infrastructure implementations.
  Fix:
    Move the operation behind the existing library
    application interface and import that interface.
  Relevant contract:
    docs/architecture/module-boundaries.md
```

The strong form makes the problem, the reason, the approved path, and the relevant knowledge available immediately. The agent does not need to search for the intended architecture, guess the rationale, or burn iterations discovering the repair. This is a major multiplier on the slice loop.

**Every custom lint or structural check must provide:**
1. A **stable rule identifier** (e.g. ARCH-012) — stable so agents and records can cite it.
2. The **exact violation and location** — the file, the import, the line.
3. The **invariant being protected** — why it matters.
4. An **actionable repair path** — the approved alternative.
5. A **reference to the relevant design contract** — where the rule's authority lives.

This is the WHAT/FIX/REF contract in the execution spec (AFA-06), plus WHY. Every failure record the harness prints carries `code`, `what`, `fix`, `ref`, and `seed`.

**Diagnostic commands (implement when they solve real workflow problems):** `verify --changed`, `verify --explain ARCH-012`, `test --related-to <module>`, `diagnose --run-id <id>`. The principle: **make the next correct action easier to identify than the next speculative action.**

**Banned comments (the DUNE lesson).** Agents left comments in code that looked innocent but were justifications for not solving the actual problem — band-aids papered over, with a comment as the alibi. Comments spread like every other pattern. In the agent-friendly architecture: a comment must state a constraint that code cannot express, with a REF — nothing else (AFA-12). Taste-comments and excuse-comments are forbidden.

---

## 9. Locality, search space, and the shape of the codebase

**Reduce the agent's search space.** Every independent implementation path is another opportunity for inconsistency. Six ways to access the same database, four ways to validate requests, three error-reporting patterns — the agent must infer the right combination for every feature, and will sometimes infer wrong. Provide one approved database interface, one error model, one boundary-validation approach, one normal way to add a capability. Add an alternative only when it solves a problem the canonical approach cannot.

**The design test:** *can an agent build a new feature by composing existing capabilities, or must it invent new architecture every time?* The former scales. The latter produces architectural drift.

**The limit:** an abstraction that hides behavior, complicates debugging, or forces unrelated concepts together shrinks the search space while making the system worse. Prefer primitives that reduce duplication without concealing semantics.

**Make violations harder than compliance.** A useful rule has three properties: (1) the approved path is obvious; (2) the approved path requires less work than any alternative; (3) the system detects important deviations. Migrations are the canonical example: "remember not to edit the production database" is nothing; versioned forward-only migrations with checksums, a standard command, a test database, and a CI check that migrations run from clean state make the correct workflow the natural workflow.

**Improve the abstraction when the rule count grows.** A repository with 300 individual rules may be encoding a poor architecture. Many rules prohibiting slightly different forms of the same mistake = find the deeper unifying invariant. The aim is to reduce both the number of mistakes AND the number of rules needed to prevent them. The kernel (K1–K10) is exactly this move: one `defineCommand` replaces every rule about idempotency, transactions, outbox, events, and acknowledgement.

**Measure locality, not just code quality.** If adding one field to a domain object requires changing 35 unrelated files, the agent is not the problem — the architecture spread that concept across too many boundaries. Track: how many modules a typical change touches; how often the same transformation is implemented in multiple places; how frequently one domain's change breaks another. A growing change footprint is evidence of coupling and triggers architectural investigation.

**Types communicate domain meaning.** Avoid undifferentiated strings for every identifier. Branded types (`UserId`, `DocumentId`), typed states (unvalidated request ≠ validated domain object), explicit result types (`Result<T,E>` — success distinguishable from recoverable failure). A branded string alone validates nothing at runtime; safe constructors and boundary parsers do the runtime work. The goal: encode semantic distinctions once, so they propagate instead of being re-explained at every call site.

**Ownership boundaries.** When two modules can directly alter the same data, they develop incompatible assumptions about its lifecycle. One owner per domain concept, an explicit interface for others, dependency directions enforced by static analysis once the codebase justifies it. The criterion is not sophistication — it is whether a change in one part stays within predictable scope.

**The agent-friendly architecture (AFA, summarized — full text in the spec):** one way (each concern has one primitive; two ways become ten) · impossible by construction (prefer a type error or DB rejection to a rule) · locality (schema, handler, bindings, tests of one behavior in one folder) · explicit over clever (no decorators, runtime reflection, global state, dynamic import, deep inheritance) · greppable (unique names, one error code per failure) · diagnostic errors (WHAT/FIX/REF) · fast loop (`make fast` ≤ 60s, `make verify` ≤ 10 min) · golden path (one exemplar slice; `make new-slice` generates from it) · small blast radius · deterministic by construction (ports inject time, IDs, randomness) · performance is a tested budget, not traded for abstraction · no indirection or comments for human taste; no removal of structure that shrinks the search space.

**The gardener.** A standing role (an agent in later stages, the orchestrator now) that watches for what creeps in: workarounds, "innocent" patterns, growing complexity, forbidden dependencies. Weeds are pulled in the bud, before they propagate. The mindset test: keep the codebase in a state you would be happy to have an agent copy — because it will.

---

## 10. Repository garbage collection and the ratchet

**Architectural entropy is continuous.** Even a well-designed repository accumulates drift: a constraint that worked last month becomes insufficient; an agent discovers a workaround; a dependency update changes behavior; a once-reasonable utility becomes redundant; suppressions accumulate. Maintenance cannot depend on occasional bursts of human effort.

**Repo GC — the drift classes to scan:**
1. Duplicated business logic and utilities
2. Growing function or module complexity
3. Forbidden dependencies between modules
4. Stale documentation and broken internal links
5. Unused feature flags, obsolete code paths, outdated workarounds
6. Weak or missing tests around important behavior
7. Lint suppressions and weakened checks
8. Inconsistent error handling or external API access

Some findings use deterministic tools; others (questionable module responsibilities) need semantic review by an agent.

**The cleanup policy (narrow, verifiable changes only):**
1. Find a specific deviation.
2. Explain the invariant it violates.
3. Propose the smallest correction.
4. Run the relevant checks.
5. Submit a focused change.
Track the debt until it is corrected or explicitly accepted. The cleanup agent never rewrites half the codebase because it "would look cleaner."

**The ratchet policy:** for selected quality measures, new code may not make the baseline worse. If legacy code already exceeds an acceptable threshold, establish the baseline, require new code to meet the stronger standard, and improve the legacy baseline incrementally. This prevents cleanup from becoming all-or-nothing. The baseline itself only moves up (LAW-09).

**In this repo now:** entropy is continuous in prose form already — the worklog, the failures ledger when it starts, superseded-file marking, and this doctrine file being kept in agreement with LAWS.md. `make entropy` (dead code, stale FACTs, flaky tests, unused constraints) arrives with the harness phase; the recurring GC agent arrives at the self-maintaining stage (see §12).

---

## 11. The engineering environment needs regression tests too

**Principle (upstream, "one of the more useful extensions of the original thesis"):** most repositories test the product. Agent-native repositories also test whether **the engineering environment remains effective at producing correct changes.**

The failure mode: an edit to AGENTS.md, a shared primitive, or the architecture checks leaves every product test green — while making agents *less effective*. Product tests cannot detect that degradation. Something must.

**The agent-harness regression suite.** Maintain a small collection of representative engineering tasks:
- Add a field to an existing domain object.
- Add an endpoint that accepts malformed input safely.
- Fix a reproduced bug without changing unrelated behavior.
- Extend an existing feature through the approved module boundary.
- Add a UI interaction and validate it in the running application.
- Perform a schema migration without losing existing data.

For each: expected outcome + required evidence. Run when making important changes to the harness. Track successful verification, architectural violations, human interventions, regressions, execution cost. The question it answers: **"Did our latest engineering change make the repository easier or harder for an agent to modify correctly?"**

**In this repo:** the one-shot proof (a fresh agent + AGENTS.md + a card passes the gate on cycle 1) is the live version of this test; the resume test (a new session finishes a half-done slice from files only) is its statelessness version; the Context Exam tests the memory itself. Initially manual and few; automated when change volume justifies it. Do not build a benchmark platform before experience says which tasks predict real engineering performance.

---

## 12. Growth stages — how this repo grows

Do not attempt full autonomy on day one. Autonomy increases as evidence and enforcement improve. Progress happens in response to observed failures, not a calendar. A small project may sit in early stages for a long time; a security-sensitive or fast-growing system needs stricter enforcement earlier.

| Stage | Name | What is true | Arivo mapping |
|-------|------|--------------|---------------|
| 0 | First layer | Canonical memory, laws, plan live; enforcement is prose with reason codes; zero code | NOW (this commit) |
| 1 | Reliable foundation | Clean clone verifies from empty state; golden path exists; one command verifies the implementation | PLAN Phase 1–2 |
| 2 | Legible system | Agent finds authoritative specs, understands module boundaries, runs the application, inspects logs, reproduces failures | PLAN Phase 2–3 |
| 3 | Enforced architecture | Repeated mistakes have become shared primitives, stronger types, boundary validation, tests, structural checks | PLAN Phase 3+ (ratchet) |
| 4 | Evidence-driven changes | Changes carry reproducible acceptance evidence; critical verification paths protected; review focuses on ambiguous and high-risk changes | PLAN Phase 3+ |
| 5 | Self-maintaining repository | Recurring agents identify architectural drift, maintain documentation, remove obsolete patterns, open small cleanup changes | post-foundation |
| 6 | Self-improving harness | Representative engineering tasks evaluate the environment itself; changes to tools/constraints checked for agent-performance regressions | maturity |

**Each stage's operating model — who runs, what is enforced, how memory updates, how failures heal — is specified in `/OPERATING-MODEL.md` §Growth.** The rule that governs transitions: a stage's constraints are built when its failures have been observed (or are catastrophically expensive to retrofit — the proactive set), never invented ahead of need.

---

## 13. What we measure

Judge nothing by how many instructions, agents, linters, or tests it contains — those are inputs, not outcomes.

| Metric | What it reveals |
|--------|-----------------|
| Recurrence of known failure classes | Whether the repository actually learns from mistakes |
| Successful changes without human repair | Whether agents can use the system effectively |
| Regressions that escape verification | Whether the quality controls catch real defects |
| Time from failure to diagnosis | Whether feedback and diagnostics are useful |
| Unrelated modules changed per feature | Whether the architecture supports local changes |
| Verification bypasses and suppressions | Whether constraints are losing effectiveness |
| False-positive rate of checks | Whether enforcement creates unnecessary friction |
| Effectiveness of tests against deliberate mutations | Whether tests detect incorrect behavior rather than merely execute code |

**Investment decision rules:** agents complete tasks but repeatedly introduce cross-domain coupling → invest in architecture boundaries. Clean architecture but agents burn cycles reproducing bugs → invest in fixtures and operational tooling. Large test suite repeatedly misses incorrect behavior → improve oracles before adding tests.

**The objective is not zero errors — that is unrealistic. The objective is errors that are cheaper to discover, cheaper to correct, and less likely to recur.**

---

## 14. The principles on the wall (upstream, verbatim)

1. The repository remembers what the team cannot afford to forget. Important knowledge must survive the chat session, the agent, and the original author.
2. The system must enforce what prose cannot reliably guarantee. Instructions explain; architecture and verification constrain.
3. Every recurring mistake is evidence of a missing capability. Do not respond to the same failure with increasingly elaborate prompts.
4. Prefer one strong primitive over many local rules. Reduce the number of independently invented solutions.
5. Every important change carries evidence. A completion message is not proof that the software works.
6. Verification must be independent enough to catch shared misunderstandings. Passing tests are only as valuable as the requirements they encode.
7. Diagnostics must explain the route to repair. A failure should direct the agent toward the correct next action.
8. Protect the system that judges correctness. Agents must not silently weaken their own tests, policies, or acceptance criteria.
9. Locality is a measure of architectural health. A small change should not require the agent to understand or modify the entire codebase.
10. Constraints must earn their complexity. Measure false positives, exceptions, and unintended consequences. Remove rules that make the system worse.
11. The repository must clean up its own entropy. Drift is continuous, so maintenance cannot depend on occasional bursts of human effort.
12. Test the engineering environment itself. A change that makes agents less reliable is an engineering regression, even if the product still passes its tests.

---

## 15. First-day discipline, and the real objective

**What we did NOT do, and why:** no long AGENTS.md, no elaborate rule catalog, no fleet of specialist agents, no custom framework, no 300 laws — those create the appearance of rigor without a reliable path to working software. The first day's work is: the product contract (NORTH-STAR, INTENT-LEDGER), one complete vertical path (PLAN Phase 3, the capture slice), a way to verify it from a clean environment (Phase 1–2), a short repo map (AGENTS.md), one canonical pattern (the golden path when it exists), strict validation at untrusted boundaries, and the smallest test suite that meaningfully protects the feature.

**On every mistake, the three questions:** why was this mistake possible? is it likely to recur? what inexpensive structural improvement would prevent or detect it? The improvement might be a type, a shared primitive, a regression test, an architecture check, better diagnostics, an operational fixture, or a more precise specification — documentation only when the missing ingredient is genuinely knowledge that cannot be expressed more effectively elsewhere.

**Over time, the repository should need fewer corrective instructions for the same class of work.** The agent spends less effort guessing how the project works and more effort solving the actual problem.

**The real objective (upstream, closing, verbatim):** "not an agent that follows an increasingly long list of rules, but a software system whose design makes correct changes natural, incorrect changes detectable, and engineering knowledge cumulative."
