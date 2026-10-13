# 01 — Engineering Doctrine (from the transcripts + upstream)

> SUPERSEDED by root /ENGINEERING.md (2026-10-13) — the full doctrine with mechanisms, failure modes, and sources. This brief remains as extraction history.

Source: engineering transcript.txt, upstream of engineering transcripts.txt
Status: INTERNALIZED — this is the mindset the orchestrator operates from.

---

## The core thesis (both sources, one idea)

**The environment produces the quality, not the agent.** Trust in agent work is not given by model capability — it is built by the environment: verification machinery, constrained codebase, paved paths, enforced boundaries. "You are the bottleneck" — the engineer's job shifts from writing code to building the system that makes agent code trustworthy by construction.

## The two cuts through all noise

1. **Give the agent a way to verify its own work.** Run the real thing, collect empirical evidence (traces, transcripts, state), never trust self-report.
2. **The codebase is memory.** Agents extend what exists. Every pattern present teaches every future agent. Anti-patterns spread like a virus; good patterns compound like capital.

## From the talk (trust, kitchen, DUNE, gardener)

- **Michelin kitchen, not factory**: creative work; you still own the final outcome; setup (line cooks, sous chefs, equipment, ratios) determines the product.
- **Trust ladder**: 1:1→1:5 babysitting phase is hardest to escape; you escape it with verification, not confidence.
- **Verification skills = CLI + feature map**: a reproducible CLI in the skill directory (same tool every time, invested in, handles edge cases) + materialized memory of how the app works (features, routes, DOM targets, maintained by automation).
- **Correctness ≠ quality**: verification proves the checkout button checks out; quality needs skills that encode real engineering workflows.
- **Trust continuum (strongest first)**: codebase → static analysis → rules/bugbot/skills → style guide. Style-guide-only review is the big hole.
- **Agent-friendly architecture (DUNE)**: agents love shortcuts — design so the shortcut IS the right path. Locked down, conventional, standardized; "annoying for humans, perfect for agents." Even pilots with minimal context (designers, PMs, CEOs) ship well by default.
- **Banned comments**: agents use comments as justification for band-aids. Comments paper over problems instead of solving them — and the pattern spreads.
- **The gardener**: a role that nips weeds (workarounds, anti-patterns) in the bud before they propagate. Keep the codebase in a state you'd be happy if an agent copied it.
- **Lint-rule instinct**: see tech debt → write a lint rule now (stop the bleeding), clean up deliberately. Delete tech debt; enforce single paved path; make the mistake categorically impossible when you can.

## From the upstream (the agent-native repository)

**Definition**: "A repo should not merely contain the software. It should contain the knowledge, constraints, and verification machinery that make producing the next correct version easier than producing an incorrect one. This is an engineering discipline, not a prompting technique."

**The central rule**: "Every important engineering decision should exist in a form that the agent can discover, and every important enforceable decision should exist in a form that the machine can check."

**The five memory systems** (must agree with each other):
1. Intent — why the system exists, concepts, required behavior, decided trade-offs
2. Structural — types, boundaries, APIs, schemas, ownership, dependency directions, approved primitives
3. Verification — tests, contracts, static analysis, reproducible scenarios, acceptance criteria
4. Operational — logs, traces, metrics, tools to reproduce real failures
5. Evolutionary — past mistakes, rejected approaches, decisions, regressions, improvements

**Start small**: one complete reliable path — Requirement → implementation → verification → evidence → merge. Don't build a giant framework first.

**First three assets**: (1) product contract (behavior / invariant / implementation-choice separation — agents get freedom on the last, none on the first two); (2) golden path (one complete vertical slice crossing real boundaries — the canonical example agents copy); (3) one verification command (`./scripts/verify`) — same checks locally and in CI, nonzero exit on failure, names the failing check.

**Every failure must become an asset** — THE central operating rule: observe → preserve reproducible example → identify missing capability → fix at strongest appropriate layer → verify the guard itself.

**Constraint ladder (0→5)**: prose → canonical examples → approved primitives → types and contracts → static/structural checks → executable verification + enforced invariants (CI gates). "When an instruction matters enough to repeat, investigate whether it should become an enforced property of the system."

**Four design principles**:
1. Reduce the agent's search space (one approved way; compose, don't invent; "can an agent build a new feature by composing existing capabilities?")
2. Make violations harder than compliance (approved path obvious, less work, deviations detected)
3. Improve the abstraction when rule count grows (300 rules = missing abstraction; find the unifying invariant)
4. Changes carry their own proof (evidence packages; what was intended / how reproduced / what changed / what independent observation shows it works)

**Test validity vs test execution**: the same misunderstanding can infect implementation AND its tests. Oracles must be independent: product contracts, reference implementations, mutation testing, property-based tests, contract tests, acceptance tests. Coverage is insufficient.

**Protect the verifier**: never let agents weaken tests, CI gates, lint suppressions, acceptance criteria. "Otherwise the system can gradually learn to look correct without becoming more correct."

**Diagnostics are architecture**: errors are instructions for the next reasoning step. Every check prints: rule ID, exact violation, the invariant protected, the actionable repair, the contract reference. "Make the next correct action easier to identify than the next speculative action."

**Memory needs authoritative homes**: intent / structural / behavioral / explanatory / operational / temporary. "Every duplicated fact creates a synchronization obligation."

**Architecture removes classes of mistakes**: Design A (prompt-only) → B (shared implementation) → C (restricted architecture) → D (restricted capability — components without need never receive the capability). "Do not ask an agent to remember a property that the architecture can enforce."

**Repo garbage collection + ratchet**: drift is continuous; maintenance is recurring; quality baseline never gets worse; legacy improves incrementally.

**Harness regression tests**: test the engineering environment itself with representative tasks — "did our latest engineering change make the repo easier or harder for an agent to modify correctly?"

**Maturity stages**: 01 reliable foundation → 02 legible system → 03 enforced architecture → 04 evidence-driven changes → 05 self-maintaining → self-improving harness. Progress on observed failures, not calendar.

**What to measure**: recurrence of failure classes, changes without human repair, escaped regressions, time-to-diagnosis, change footprint (locality), suppressions, false-positive rate, mutation effectiveness. "Inputs, not outcomes" is the trap.

**The 12 principles on the wall**: repo remembers what the team can't afford to forget · system enforces what prose can't · every recurring mistake = missing capability · one strong primitive over many rules · every important change carries evidence · verification independent enough to catch shared misunderstandings · diagnostics explain the route to repair · protect the system that judges correctness · locality measures architectural health · constraints earn their complexity · the repo cleans its own entropy · test the environment itself.

**First day**: product contract, one vertical slice, verify from clean environment, short repo map, one canonical pattern, strict boundary validation, smallest meaningful test suite. Then extend with the agent. On every mistake ask: why was it possible, will it recur, what inexpensive structural improvement prevents or detects it? "Over time, the repository should need fewer corrective instructions for the same class of work."

**The final objective**: "not an agent that follows an increasingly long list of rules, but a software system whose design makes correct changes natural, incorrect changes detectable, and engineering knowledge cumulative."
