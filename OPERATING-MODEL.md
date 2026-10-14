# OPERATING-MODEL — How This Repo Runs, and How It Grows

Binding for every agent in this repo: orchestrator, builders, verifiers, and (as they arrive) runtime agents, workers, and maintenance agents. This file specifies four things: **who operates** (roles), **the unit of work** (the slice loop), **how the repo grows** (operating models by stage — how context gets updated, how repo memory gets updated, and what keeps nothing from breaking), and **the self-healing and verification machinery** that makes growth safe.

The governing loop (INT-036): *Build a small, real slice of Arivo. Verify it independently. Refine it until it matches the intended behavior. Turn the lessons into constraints. Repeat.* The harness serves that loop (P-17); it never postpones it.

---

## 1. Roles

| Role | Context | Reads | Writes | Never does |
|------|---------|-------|--------|------------|
| **Owner** (prathamarchives) | Outside the repo | Everything, at gates (minutes per slice) | Owner-only artifacts: phase-gate signatures, exam grades, intent answers | Writes code; holds no obligation to respond mid-slice |
| **Orchestrator** | Persistent understanding of the corpus and laws (cold-started per P-11) | All canonical files, worklog tail, `make state` | Memory deltas (all ledgers, this file, PLAN), slice cards, commits, worklog | Verifies its own work; touches gates/workflows once walls live; holds the signing key |
| **Builder** | Fresh context, no history | The card, the context pack it lists, the files in its scope | Only the paths in its card scope | Verifies its own work; reads real owner data or secrets (fixtures + test DB only); edits protected paths |
| **Verifier** | Fresh context; did NOT write the code under review | Card + Proof Sheet + diff only | Failing tests only | Edits product code; resolves its own findings |
| **Runtime agent** (future) | External, connected via API/MCP | Scoped reads in granted scopes | Attributed writes (annotations, links, concept proposals) — zero belief weight | Reaches the database (NG-02); purges; holds unscoped tokens |
| **Arivo worker** (future) | Kernel-driven job runner | The owner scope of its job | Derived rows via `writeDerived`, outbox effects | Improvises beyond its job; holds more than service credentials |
| **Gardener / GC agent** (future, stage 5) | Recurring maintenance runs | Drift scan outputs, constraint register | Small cleanup changes through the normal gate | Rewrites broadly; accepts debt without a record |

**Role separation is load-bearing.** The builder-never-verifies rule exists because the shared-misunderstanding trap (ENGINEERING §6) means an author's tests confirm the author's beliefs. The verifier-writes-only-failing-tests rule keeps the adversarial stance pure: its job is to break the slice, not to rescue it. The verifier's report is advisory — **the gate decides** (VRF-05) — so a verifier cannot veto a change any more than a builder can bless one.

**The owner's enumerated exclusive powers:** the signing key and `gates/owner.pub`; exam keys and sealed test sets (outside the repo); protected-path approvals (CODEOWNERS); phase-gate tag signatures; purge invocation; intent answers (the only source of new Intent Ledger entries). Everything else, agents run (P-13).

---

## 2. The slice loop (the unit of execution inside every phase)

One behavior, one card, one loop. Steps 3–8 are a **cycle**; after 3 failed cycles stop (LAW-16); after any failure, ratchet before the next slice (LAW-18).

| # | Step | Specification |
|---|------|---------------|
| 1 | `make state` → read the card | The repo's generated status (phase, open slices, open questions, constraint status, last gate) — never an agent's memory of it (P-02) |
| 2 | Write `understanding.yaml` | Slice ID, **intent IDs (INT-*) with the owner quotes**, intent restated, scope restated, must-reject restated, **unknowns: []** — meaning zero *unclassified or unresolved blocking* unknowns (D-012; the correction of the original "zero unknowns"). Facts used, plan. A non-empty blocking list stops the slice |
| 3 | Write the tests from the card. Commit them ALONE. `make red` | Each test MUST fail for the stated reason (LAW-11). The harness hashes the red tests and freezes the record (RED-01/02). Amendments add assertions, never remove (RED-03) |
| 4 | Write code inside card scope. `make fast` after each change | ≤60s (AFA-07). SIZE and SCOPE limits apply (LAW-05/06) |
| 5 | `make real-run` | Start the real stack, drive it as a user, record the transcript + state snapshots (LAW-12). Real stack, never a mock that looks successful |
| 6 | `make falsify` | Property, fault, differential, and mutation tests with fresh seeds (LAW-13: state read through paths the code under test does not control). Fix each failure; each failure prints its seed |
| 7 | `make prove` | The harness builds the Proof Sheet from run records. Hand-editing it fails the gate (PRF-01) |
| 8 | `make gate` → exit 0 | All mechanical checks: SCOPE, SIZE, PROT, RED, SKIP, FAST, ratchet, open blocking questions. Then PR |
| 9 | CI runs `make verify` | Remote CI is the authority (D-009, WALL-06). Local verify is preflight |
| 10 | Owner reads the proof → **accept, or ratchet** | The acceptance review: minutes, not hours — the Proof Sheet is designed for exactly this |
| 11 | Any failure occurred → run the ratchet (§6) before the next slice | LAW-18. No exceptions |

**Stop conditions (STOP-01..08, any one true):** a blocking Question Record is open for the slice · the slice failed 3 cycles · the change needs a path outside scope · the harness is red · two laws conflict · the task asks you to weaken a constraint · owner words conflict with another file · you cannot verify a fact the slice needs. Action: write the record, commit it, end the session with a one-line status.

---

## 3. The commit protocol (P-15)

Every reasoning delta becomes a file update, then a commit, then a push — same session. An unpushed conclusion is a lost conclusion.

**What counts as a delta:** a new owner statement captured · a decision adopted · a law added or superseded · a tension surfaced · an extraction produced · a plan change · a failure observed · a question raised · a worklog-worthy action completed. If none of these happened, nothing was reasoned; if any did and it is not on disk, it is lost.

**The write path (memory deltas):** identify the memory type → find its authoritative home (ENGINEERING §3 table) → append with a stable ID → supersede by reference (never rewrite) → commit with a message naming the IDs → land it same-session. From walls stage-1 (2026-10-13, D-024/FAIL-001) the landing is branch + PR + merge under the STANDING authorization of P-13/P-15 — `main` is PR-only for everyone, the owner reviews at gates, not per-merge. Once code exists, code changes go through the slice gate with CI; memory deltas keep their standing path. Never batch deltas for a single end-of-session commit — FAIL-002 records what batching costs.

**The change channel (D-024) — findings vs applications.** Memory deltas (owner words, decisions, ledger/worklog/plan/session-record updates) flow per P-15 above. Analysis, review, and proposal artifacts — a stress review, a protocol proposal, any agent-authored assessment — NEVER land on `main` directly: they arrive on a branch, through a pull request, and merge only with the owner's explicit authorization. A review request authorizes inspection and reporting, never edits; a reviewer never silently "fixes" a finding while presenting the work as a review. With walls stage-1 live (2026-10-13), the host itself rejects direct pushes to `main` — the discipline is checked in the workflow, not remembered in prose. Full channel table, finding format, and severity rules: `context/reviews/REVIEW-PROTOCOL-PROPOSAL.md` (accepted process detail, subordinate to this section and `/EXECUTION.md` §5).

**P-18 discipline (evolving truth, 2026-10-14):** a documentation update repairs what the CURRENT task needs — the contradiction that could mislead current work — and defers unrelated editorial debt to the post-product comprehensive refinement pass; supersession is always by reference, never rewriting; if a future architectural question does not affect the current slice, it stays open. The full law: PRINCIPLES P-18 (INT-094/095/096).

**The worklog law:** every agent reads the worklog before working and appends after — Task ID, agent, task, work log, stage summary. The worklog is the operational memory of coordination; the ledgers are the canonical memory of record. Neither substitutes for the other.

**The session engineering record (INT-072, broadened per F-04, 2026-10-13; two-tier event-typed policy per D-027/INT-106, 2026-10-14):** session records are event-typed, never time- or token-based. Two tiers:
- **A MEANINGFUL session** (GLOSSARY; any of: changes repository state · produces a material finding or verified result · an external system captures an owner decision · records a failure disposition · changes a task status or next action) appends a **compact WORKLOG entry** — task, outcome, evidence, pointer, unresolved items, next action; soft target 100–250 words; the numbered record holds the detail. Routine reading with no new finding or decision needs no entry.
- **SUBSTANTIAL work** (GLOSSARY; any of: an implementation slice · a meaningful multi-step investigation · a review with findings · a verification campaign · a material architecture decision · a failure investigation · coordinated multi-agent work) ALSO produces a **numbered session record** — `context/extracted/NN-<NAME>.md`, self-contained, written to the standardized form (`context/TEMPLATES.md`): **starting state** (starting commit, branch, and whether the working tree was clean; when work crossed a PR: its base, head, and merged revision) · **task and scope** (the requested work, bounded scope, intent/decision references) · **results** (what changed, what did not, why) · **files changed** (exact paths + relevant IDs) · **commands and external actions** (the ACTUAL commands with the revision tested, exit status, and material result for every local verification — never reconstructed from memory; large raw output is linked, not inlined; tool-only/API-only sessions name the exact operation, its target, and the written result or link, and say so when no shell command ran — no fictional command logs) · **evidence** (tests, CI runs, PRs, observations, outcomes) · **failures** (failed attempts, found defects, dispositions, any regression guard) · **unverified items** · **open decisions** · **next action** (ONE deterministic continuation point).
**Handoff honesty rules:** "tests passed" is not a handoff unless the record names which tests, against which revision, with what result; "done" is not a status while a proof is missing or an owner decision unmade. A meaningful session that finds a defect but changes nothing still leaves a durable record (the verified finding, what remains uncertain, what happens next — the finding can alter the next correct action with zero file changes). Records preserve results, evidence, and conclusions — never private internal reasoning: an incoming agent needs enough to reproduce or verify the work, not an exhaustive transcript. Any later agent reads ONE file instead of reconstructing the session from the worklog tail alone; the worklog entry points at it; `/STATE.md` points at the latest one (VER-804 checks the pointer's freshness). For multi-agent runs, each subagent's useful results land in the shared record (or a linked artifact) BEFORE the orchestrator closes the task — "it was in a subagent transcript" is not durable repo memory. **The record's §1 preserves the owner's turn verbatim BEFORE the ledger entry is written (2026-10-14, closing the INT-046/068 class): a quote whose only durable home is the ledger itself has no cross-check; the session record is that cross-check.** `09-ARCHITECTURE-REVIEW.md` (2026-10-13 stress-test session) is the first; numbering continues the extracted-brief sequence; records are banner-marked historical process artifacts (D-022) — analysis lives there, never in the ledgers. (The number 10 is re-homed: the goal-aligned stress review lives in `context/reviews/` per the change channel.) *Supersession note: the earlier single-tier rule ("EVERY meaningful session leaves a numbered record", INT-072 as broadened per F-04) is superseded by this two-tier policy (D-027(2), INT-106) — by reference; INT-072 stays as history and the numbered record remains the substantial-work form.*

---

## 4. Question classes and records (D-012)

| Class | Use when | Action |
|-------|----------|--------|
| **Blocking** | The answer affects data loss, a security boundary, owner intent, an irreversible action, a protected path, the kernel, or a law | Stop the slice. Write the Question Record. Continue only independent slices. QST-02: a question meeting a Blocking condition can NEVER be reclassified defaultable |
| **Defaultable** | Low risk; one file or one constant reverses it | Record with a default + reason. Use the default. List it in the Proof Sheet. Owner can override at the next touchpoint. Silence past the named gate = consent (QST-03: a default becomes a Decision Record with a lock gate) |
| **Non-blocking** | Does not affect the current slice | Record it. Continue. Never stops unrelated work |

QST-01: the question's *class* sets the workflow — not its urgency, not the schedule's convenience.

---

## 5. Morals and beliefs

### Morals (non-negotiable, enforced by records and gates)

1. **No claim without proof.** Prose is a summary, never evidence. A result claim without a harness proof file violates LAW-01.
2. **No unverified tool/model/platform facts.** FACT ID or spike, or explicitly marked "not verified" (LAW-02). Version numbers from memory are the canonical example of the failure.
3. **No averaging contradictions.** When two sources disagree, name both, surface the conflict as a Question Record, and let the authority order resolve it (AUT-05: never choose silently).
4. **Never weaken a constraint to pass.** The verifier is protected (LAW-09, ENGINEERING §7).
5. **Builder/verifier roles never touch real owner data or secrets.** Fixtures and test DB only (LAW-28). Runtime isolation checks print conditions, never values.
6. **Owner words verbatim, typos preserved.** Interpretations always labeled as interpretations (AUT-02/04; the Scribe may not lock a normalized meaning without owner approval).
7. **Every report carries an honest, non-empty not-verified list.** LAW-04; the Proof Sheet schema requires it.
8. **Nothing is memory unless it is on disk in this repo.** P-02 in its operational form.
9. **No hidden not-verified.** A claim quietly dropped is a claim silently made — the not-verified list is where honesty becomes checkable.
10. **No chat-as-memory.** Decisions made in conversation do not exist until they are in the repo (P-15).

### Beliefs (operating assumptions — each with what it implies operationally)

- **The environment produces quality** → invest in constraints and verification, not in longer prompts or model upgrades, when output is bad.
- **Agents copy what exists** → every pattern in the repo is an instruction to every future agent; anti-patterns are viruses (the gardener exists for this).
- **Mistakes are assets** → a failure properly ratcheted is a permanent defense; a failure hand-fixed is a failure scheduled to repeat.
- **The strongest constraint wins** → LAD-01; when a fix is possible at C1 and C6, the C1 fix is the fix.
- **Small is fast** → size limits, 60-second fast loop, one behavior per slice; speed of the loop is speed of the learning.
- **Autonomy requires reversibility** → every agent action is reversible (tombstones, supersession, rebuildable derived data), which is exactly why acting without permission is safe.
- **Discovery is not evidence** → P-08 operationalized; retrieval hits are suggestions, never confirmations.
- **The machine never idles** → no stage waits for an owner (NG-01); defaultable questions proceed on defaults; the system is always doing the next independent useful thing.
- **Owner time is the scarcest resource** → review artifacts are minutes-sized; exams are graded once per phase, not per slice.
- **Honesty compounds** → every not-verified line and every open question is recorded, so trust in the repo's claims grows with use instead of decaying.

---

## 6. Growth — the operating models by stage

The repo does not have one operating model. It has six, one per maturity stage (ENGINEERING §12). Each model specifies: **who runs**, **what is enforced**, **how memory updates**, **how failures heal**, and **the graduation predicate** that upgrades the repo to the next model. A model is never upgraded on a calendar — only on its predicate, in response to observed capability. (Stage names map to PLAN phases; the mapping is in PLAN.md.)

### Model 0 — First Layer (2026-10-13 → 2026-10-14; COMPLETE — graduated to Model 1)

- **Who runs:** the orchestrator with GLM-based research/verification subagents (INT-070: test and verification loops run on GLM subagents — the 2026-10-13 stress-test session used them for corpus extraction and the cold-start stress test), in continuous-commit mode; the owner reviews at touchpoints. No product-code builders, no product code; remote CI for the document layer is live (D-025).
- **What is enforced:** prose at C6 with reason codes (`waiting-for-slice` on every law — the codebase is empty; that is honest, not weak). Enforced NOW: append-only ledgers, verbatim owner words, the worklog protocol, the read order, no-product-code-without-approved-plan, the change channel (D-024: review/analysis/proposal artifacts go by PR, merged owner-authorized only), walls stage-1 (protected `main` — PR-only, no force push, applies to admins), the canonical-layer verifier with its known-bad self-test (F-01 repaired), and since 2026-10-14 (D-025, walls stage-2): remote CI (the `verify` workflow, D-009 — the `canonical-layer` check required to merge), the source-coverage control (raw SHA-256 immutability at C3, mechanical quote fidelity of every raw-cited ledger entry, STATE freshness — VER-801..804), the W-03 isolation check (LAW-28's redacted secret scan), and credentials hygiene (values never recorded; INT-092's redaction is the pattern).
- **How memory updates:** every reasoning delta → authoritative home → append with ID → commit → push (§3); `/STATE.md` (the current-state index) refreshes at every session exit. Contradictions become Question Records with defaults; silence past a named gate is consent for defaultable questions only (QST-03).
- **How failures heal:** process failures (a misread, a drift, a tension) become Reasoning Log entries, reconciliation briefs, superseded files — and, from 2026-10-13, failure records with guards (FAIL-001: the direct-to-main incident class; the host gate plus VER-107 now catch its recurrence). Structural failure is impossible — there is no structure yet.
- **Graduation (→ Model 1):** ACHIEVED 2026-10-14 (session 13, D-026): the owner's turn-9 directive executes the plan (INT-093..099); walls live through stage-2 AND W-02 landed host-agnostically (the identity question gates instantiation, never the wall — INT-097); Phase-1 exit criteria observed (broken-build merge-block 405 + VER-802 red run; fresh-session canonical-instruction loading proven behaviorally; secret-free sandbox; green verify; red probe). Q2/Q3/F-06/Q-IDENT ride to their named gates (F-07: each blocks only its dependents).

### Model 1 — Trust Environment (walls live, CI authority) — NOW (since 2026-10-14)

- **Who runs:** orchestrator + builder sessions per the role table (Q1 remainder non-blocking: builders are any capable agent working a card — identity never gates a wall or a phase, INT-097; GLM-based by default per INT-070). The owner runs the wall checks.
- **What is enforced:** LAW-07 (protected paths, CODEOWNERS), LAW-08 (dependency approval), LAW-28 (isolation, redacted). Protected `main`: PR-only, no force push, the required check restricted to the expected source application, verified on installed host versions — never assumed from docs.
- **How memory updates:** same as Model 0, plus FACTS entries for every verified host behavior (the Host Contract: how each host actually loads canonical instructions — AGENTS.md auto-load, CLAUDE.md `@path` imports — verified by sentinel + transcript, not documentation claims).
- **How failures heal:** wall failures are break tests — the owner deliberately attempts forbidden operations and each must fail. A wall that doesn't hold is fixed before anything else happens.
- **Graduation (→ Model 2):** a broken build cannot merge; a fresh host session loads canonical instructions (proven); the sandbox is proven secret-free (conditions printed, values never); `verify` runs green on a trivial truth; a deliberately broken build fails the gate.

### Model 2 — Build Loop (harness core + builders + verifier)

- **Who runs:** builders from cards (fresh context), an independent verifier, the orchestrator as planner/gater.
- **What is enforced:** the method laws — LAW-01, 03, 04, 05, 06, 09, 11, 14, 15, 16, 18, 24. Proof Sheets built from run records; frozen red records; scope and size checks; the ratchet check; representative known-bads FOR THE PROACTIVE SET ONLY (scope breach, protected-path edit, skipped test, hand-written Proof Sheet, lowered threshold, missing red record, test edited after red, unapproved dependency). One real-stack test on a real database.
- **How memory updates:** build knowledge lands as constraints (register entries), FACTS, and failures/ records — agent-learned lessons encoded per MEM-02 (constraint → test → FACT → document line, in that order). LESSONS.md holds only non-encodable lessons, each with a reason code; the owner reviews encodability every 10 accepted slices.
- **How failures heal:** the ratchet (§7) in full. Three failed cycles = Blocker Record and stop.
- **Graduation (→ Model 3):** deliberately broken builds fail with named codes; the harness proves scope, evidence immutability, idempotency, independent reads on a real database; the first one-shot passes (a fresh agent with AGENTS.md + a card passes the gate on cycle 1).

### Model 3 — Enforced Architecture (kernel + substrate laws live)

- **Who runs:** builders on golden-path scaffolds (`make new-slice`), the verifier, the orchestrator; the owner accepts slices via Proof Sheets.
- **What is enforced:** the product laws — LAW-10, 17, 19, 20, 21, 22, 23, 25, 26 — at C1/C2/C3 where the substrate makes them construction-level: branded types that don't compile when wrong, triggers that reject the write, boundary lints, RLS, the two-owner test. The golden path is the canonical example; conformance checks compare every new slice's shape to it.
- **How memory updates:** product knowledge lands in schema/vocab sources and codegen outputs (single-source closed vocabularies); behavior knowledge lands as regression tests; every mistake that repeats moves its constraint up the ladder (LAD-03).
- **How failures heal:** the ratchet plus the sweep (RAT-05: fix every instance of the same pattern in the same slice). Known-bad builds activate as their behaviors exist (KB-04).
- **Graduation (→ Model 4):** foundation exit — 100% known-bad catch rate, two one-shots in a row, the Context Exam passes for two agents in fresh sessions, `make fast` ≤60s and `make verify` ≤10min in CI, every law enforced or planned with an owner-approved reason, the owner signs the foundation tag, no blocking questions open.

### Model 4 — Evidence-Driven (proof-carrying changes, protected verification)

- **Who runs:** multiple builder/verifier pairs; review focuses on ambiguous and high-risk changes.
- **What is enforced:** §6 of ENGINEERING as machinery: evidence packages per risk class; independent oracles (mutation testing live); verification-file changes treated as higher-risk (CODEOWNERS + reason + owner review).
- **How memory updates:** intent continues appending; decisions begin locking at their named gates (QST-03); defaults convert to locked Decision Records as their lock-gates pass.
- **How failures heal:** escaped regressions get both a fix and an oracle upgrade (a regression that passed the suite is a test-oracle failure first, a code failure second).
- **Graduation (→ Model 5):** recurring change volume with stable known-bad catch; the agent surface (API/MCP) is real enough that agent-authored material needs governing.

### Model 5 — Self-Maintaining (the repo cleans its own entropy)

- **Who runs:** recurring maintenance agents (the gardener), doc-maintenance agents, and the build loop of Model 4 continuing.
- **What is enforced:** everything prior, plus entropy policy: the GC agent scans the drift classes (duplicated logic, complexity growth, forbidden dependencies, stale docs, unused flags/paths, weak tests around important behavior, suppressions, inconsistent error handling) and submits NARROW, verifiable cleanup changes through the normal gate — never broad rewrites.
- **How memory updates:** documentation is actively maintained (stale links fixed, superseded docs archived); the constraint register loses dead rules (constraints that earn their complexity get kept; rules that make the system worse get REMOVED — ENGINEERING §4).
- **How failures heal:** `make entropy` reports dead code, stale FACTs, flaky tests, unused constraints; the ratchet and GC run continuously; the baseline only moves up.
- **Graduation (→ Model 6):** engineering-task regression evals justify automation.
- **Model 6 — Self-Improving Harness:** representative engineering tasks (add-a-field, fix-a-reproduced-bug, extend-through-boundary, migrate-without-loss) evaluate changes to tools, conventions, and constraints for agent-performance regressions. The harness itself is under test: "did our latest engineering change make the repo easier or harder for an agent to modify correctly?"

**The invariant across all models:** every stage widens WHO can act and WHAT can be trusted without review — and every widening is paid for with enforcement machinery from the previous stage. Autonomy is purchased with verification, never granted on credit.

---

## 7. The memory update protocol — how context updates and nothing breaks

This is the protocol that makes "the repo is the memory" survivable at every scale. It has three parts: the write path (§3), the append-only semantics below, and the update invariants that keep updates from breaking the system.

### Append-only ledger semantics

- **Statuses, not deletions.** Every intent entry carries a status: `active`, `clarified`, `superseded`, `historical` (AUT-02). No entry is ever deleted or reworded. A superseded entry keeps its text, gains `superseded_by: <ID>`, and the LATEST explicit owner decision governs (AUT-03).
- **Supersede by reference.** A decision that replaces an older one is a NEW record pointing at the old. The old record is history with a link, never an edited memory. Renames in the glossary work the same way.
- **Numbering never recycles.** IDs are stable forever (INT, D, P, LAW, QR, FAIL, CON, KB, FACT, task IDs). A recycled ID is a corrupted index.
- **Scribe discipline.** Normalized meanings are NOT locked decisions: an interpretation of owner words is always labeled, and locking one requires owner approval (AUT-04).

### One fact, one home

Every fact has exactly one authoritative home (§3's table / ENGINEERING §3). Summaries may exist elsewhere but must POINT at the authority, never become a second specification. **Every duplicated fact creates a synchronization obligation** — the moment a fact lives in two independently editable places, the repo has a built-in future contradiction. Duplication is a defect to be paid down, not convenience.

When two files disagree: they disagree BECAUSE of a missing question record or a broken authority — the fix is the Question Record plus the authority-order resolution, never a silent pick, never an average.

### The authority order (conflict resolution)

The authority order, the source tiers, and all conflict-resolution rules live in `/EXECUTION.md` §2–§3 — the canonical home (D-021). Carried over unchanged: a default never overrides a law or a higher level (AUT-06); two active items at the SAME level conflict → blocking Question Record; do not choose (AUT-05); the latest explicit owner decision governs, earlier text stays as history (AUT-03).

### Update invariants — what "nothing breaks" means, mechanically

These hold at every stage, checked by audit where mechanical and by review where not:

1. **Cold start never regresses.** A fresh session must always be able to acquire full operational context from the repo alone (AGENTS.md → STATE.md → worklog tail → task-relevant canonical files → `make state` when it exists; the read order's selective form, D-027(3)). Any file a cold start depends on is load-bearing: moving or renaming it requires updating AGENTS.md in the same commit.
2. **Read order stays acyclic and total.** The read order in AGENTS.md is a total order; a document may only point forward or to already-read material. No loops, no "read everything."
3. **No orphan authority.** Every law, decision, and requirement traces upward: LAW → owner intent or adopted decision; requirement → owner words or decision record (LOOP-05: a requirement with no intent fails the audit). An orphan rule is drift.
4. **No silent supersession.** If file A contradicts file B, one of them must say so. Every superseded document carries its supersession marker and pointer; a contradiction with no marker is a Question Record.
5. **The corpus is closed.** Top-level canonical documents change only through the defined owners (doc slices with owner approval once walls are live; the owner directly for NORTH-STAR and the Intent Ledger). `context/raw/` is never edited (AUT-02 in its strongest form: it is the verbatim record).
6. **Plans are not permanent truth.** PLAN.md is one phase deep (NG-04); when implementation evidence disagrees with the plan, the plan yields — via a Question Record that names the disagreement, then a plan update.
7. **Memory deltas are atomic with their commits.** A reasoning delta, its file update, and its commit are one unit. A commit that says one thing and leaves the ledgers saying another is a broken update.
8. **The context budget is a budget.** Slice context packs ≤12,000 tokens (SIZE-05) and AGENTS.md stays a map (~80 lines, MEM-03): the repo grows by adding authoritative homes, never by fattening the entry point.

### The cold-start protocol (every session, every agent — selective, position first; D-027(3)/INT-107)

1. Read `/AGENTS.md` fully — it is the map.
2. Read `/STATE.md` (where things stand: the five-area contract — phase, active task, exact next action, open owner questions, evidence; a navigation snapshot; on any disagreement, canonical authority wins) and the worklog tail (last 3 compact entries; follow the latest session-record pointer).
3. Identify the canonical sources RELEVANT to the task (STATE's pointers + `/EXECUTION.md` §1's map); read only those.
4. Verify the intent and decision status behind any CONSEQUENTIAL change — the relevant `/INTENT-LEDGER.md` entries and `/DECISIONS.md` rows (the ledger stays the intent authority; blanket ledger-first boot reading is superseded — INT-107/D-027(3): knowing the task does not require all owner words; changing something consequential does).
5. When `make state` exists (Model 2+): run it; trust it over any agent's recollection.
6. Never rely on chat history or session recall for anything (P-02, MEM-01, LAW-17's spirit pre-code).
7. `context/raw/`, historical briefs, and older session records are reference material, never boot material — read them only when a task requires it (quote verification, intent backfill, prior-work evidence). If STATE's next action is ambiguous, report the ambiguity — never compensate by reading the whole repository.

---

## 8. The self-healing system

Four mechanisms, in increasing order of permanence. All of them exist because of one sentence: **agents copy what exists, so an unfixed mistake teaches the next agent.**

### 8.1 The ratchet (RAT-01..08) — every failure becomes a constraint

1. **Record the failure** in `failures/FAIL-NNN.yaml` in the same session (class: misread, gap, gaming, scope, fake-success, regression, flaky, harness, drift).
2. **Write the known-bad build FIRST.** It reproduces the failure and fails the gate. Do not fix the symptom before this step — a fix without a reproducer is an unverifiable claim.
3. **Choose the highest ladder level that works** (LAD-01; the selection guide in LAWS.md).
4. **Build the constraint. Run the known-bad. It MUST fail with the stated code** — this is "verify the guard itself."
5. **Sweep.** Search the whole repo for the same pattern; fix every instance in the same slice (RAT-05).
6. **Register the constraint** in `constraints/register.yaml` (law, level, mechanism, proof, origin, status).
7. **If the same class repeats, move the constraint up a level.** If a C1/C2 design exists, build it (two-strike rule, LAD-03).
8. **If no constraint is possible**, write a lesson with a reason code (MEM-04: LESSONS.md, reviewed for encodability every 10 accepted slices).

**The severity policy (upstream):** single low-severity error → code fix only. Repeated failure → structural response. Single severe security/data-integrity failure → permanent guard immediately.

**The never rule:** you never fix a mistake by hand. A hand-fix is a failure postponed, and it teaches nothing to the next agent.

### 8.2 Known-bad builds (KB-01..06) — the guards are themselves tested

- Each constraint has a known-bad build: a patch in `harness/known-bad/` with a target law, an expected failure code, and an `active_from` point.
- The runner applies each active patch to a clean copy, runs the check, and EXPECTS the code. A constraint whose known-bad passes is a broken guard: the harness goes red and all building stops until a harness slice repairs it (KB-05).
- Known-bads activate when the behavior they target exists (KB-04) — never before (a phase exam must not need a behavior that doesn't exist).
- Every Failure Record adds a known-bad build or states why none is possible (KB-06).
- The harness known-bad set (from F-03, now Phase 2): scope breach · protected-path edit · skipped test · hand-written Proof Sheet · lowered threshold · missing red record · test edited after red · unapproved dependency.

### 8.3 Repository garbage collection — entropy is continuous

The recurring maintenance process (gardener role, Model 5; orchestrator duty in prose form until then). Scans the drift classes; for each finding: find the specific deviation → explain the violated invariant → propose the smallest correction → run the checks → submit a focused change. Narrow, verifiable changes only; never "cleaner" rewrites. Track the debt until corrected or explicitly accepted. The ratchet policy holds throughout: new code never worsens a baseline; legacy baselines improve incrementally; the baseline only moves up.

### 8.4 The diagnostics contract — failures are instructions

Every custom check, lint rule, and runtime error prints: a stable **rule ID**, the exact **violation and location**, the **invariant protected** (why), the actionable **repair path**, and the **contract reference** (where). Record form: `code`, `what`, `fix`, `ref`, `seed`. A check whose failure message doesn't teach the repair is itself a defect — it burns agent cycles on rediscovery. "Make the next correct action easier to identify than the next speculative action."

### Failure classification (remedy guide)

| Failure class | Likely durable remedy |
|---------------|----------------------|
| Agent misunderstands a product requirement | Clarify the product contract; add an acceptance test |
| Agent guesses an external data shape | Validate the boundary; use a typed SDK |
| Agent reimplements an existing utility | Improve the canonical API; add a check if duplication remains possible |
| Agent changes unrelated modules | Reduce coupling; clarify ownership/dependency boundaries |
| Agent produces complicated code | Improve abstractions; add targeted complexity checks |
| Tests pass despite incorrect behavior | Strengthen the test oracle, not the test count |
| Agent cannot reproduce a bug | Add fixtures, replay tools, better logs, isolated runtime |
| Documentation disagrees with code | Establish the source of truth; generate or validate derived docs |

### Drift symptoms and responses (the standing table)

| Symptom | Response |
|---------|----------|
| A rule is being re-explained in chat repeatedly | It is not enforced — move it up the ladder |
| Agents keep asking the same question | The answer has no authoritative home — give it one |
| A law and a file disagree | Question Record + authority order; fix the loser |
| Reviewer keeps catching the same class | The class is ratchet-eligible; run it |
| Proof Sheets getting glossier, checks getting weaker | Verifier-protection audit; the system is "learning to look correct" |
| Context packs bloating past budget | The map is fattening into a brain; split authoritative homes |

---

## 9. The verification stack

### Command surface (target state, arriving with Phase 2)

| Command | Result | Budget |
|---------|--------|--------|
| `make state` | STATE.md: phase, open slices, open questions, constraint status, last gate | 5s |
| `make fast SLICE=id` | Typecheck, lint, unit tests, slice DB tests | ≤60s |
| `make red SLICE=id` | Run committed tests; record failures against the test commit | — |
| `make real-run SLICE=id` | Start the real stack; drive as a user; record transcript + state snapshots | — |
| `make falsify SLICE=id` | Property, fault, differential, mutation tests; fresh seeds | — |
| `make prove SLICE=id` | Build the Proof Sheet from run records | — |
| `make gate SLICE=id` | All mechanical checks; exit 0 or 1 | — |
| `make verify` | Every check, whole repo; CI runs this | ≤10 min |
| `make known-bad` | Apply each known-bad patch; expect each failure code | — |
| `make audit` | Intent trace, requirement sync, drift, banned terms, secrets, FACT IDs, language lint | — |
| `make new-slice NAME=x` | Generate a slice folder from the golden path | — |
| `make entropy` | Dead code, stale FACTs, flaky tests, unused constraints | — |

### The Proof Sheet (harness-built; never hand-edited)

Holds: header (slice, commit, harness version, seeds) · owner words · claims with proof IDs · real-run summary · must-reject results · **independent state reads** · fault and differential results · known-bad result · scope report · defaults used · **the not-verified list** · open questions. PRF-01: the harness builds it from run records; a hand-edited sheet fails the gate. LAW-04's honesty requirement is a schema field — the not-verified list cannot be empty-by-omission.

### The Verifier (VRF-01..05)

Fresh context; did not write the code. Reads the card, the Proof Sheet, and the diff ONLY. Writes failing tests; never edits product code. Reports only failures it can reproduce, with test, seed, and command. The report is advisory — **the gate decides**. The verification family is GLM-based subagents (INT-070, governing): a different model family CAN add optional adversarial coverage, but it is never a required gate and never overrides the declared GLM workflow. Independence comes from the verification design, not the model brand: acceptance criteria fixed before implementation, a verifier that did not write the implementation, real running paths, independent state reads, known-bad controls, and protected gates the verifier cannot quietly weaken. **The falsification loop (INT-117, 2026-10-14):** GLM-based fresh-context subagents run the testing, falsification, and retesting loop — real tests, independent state reads, deliberately broken cases, actual protected gates; a known-bad change must be rejected, the failure diagnosed, the correction reviewed, and the catch confirmed. The verifier never implements the code it evaluates.

### Walls, CI, and signed gates (WALL-01..06)

`main` protected: PR + required check, no force push, applies to admins. CODEOWNERS on protected paths. The agent credential cannot change workflow files and cannot sign. Phase gates are owner-signed tags verified by CI against `gates/owner.pub`. The agent never holds the owner key. Local `make verify` is preflight; remote CI is the authority. The required status check is restricted to the expected source application so an untrusted integration cannot supply a look-alike status — verified on the installed host version (Host Contract), never assumed.

**W-02, host-agnostic (D-026, 2026-10-14).** The Host Contract defines what any supported host must load (the canonical read order — `AGENTS.md` is itself the GLM-host bridge, verified behaviorally by every session's cold start and by the session-13 proofs under pressure); a host bridge imports the entry map, never duplicates it (one fact, one home). File-import bridges land per host at adoption, with FACT entries verified on installed versions. **The behavioral proofs (session 13, INT-093/INT-098 — the standing verification method for the agent layer):** (1) the **authority-conflict test** — a fresh-context sub-agent given conflicting instructions must identify the governing authority and the recorded resolution, never averaging and never last-read-wins; (2) the **unresolved-decision test** — a fresh-context sub-agent must distinguish the four decision states and refuse to treat a recommendation, presence, or elapsed time as owner approval. **(3) The cold-start resumption test (D-027(4), 2026-10-14):** a fresh-context agent, given ONLY the repository and a realistic task, must identify the current position, relevant open decisions, latest evidence, and unverified items, cite its sources, and stay within the agreed read scope (a read manifest — files + word counts; no raw corpus or unrelated history without task-specific reason); it is graded by a SEPARATE fresh-context verifier against a rubric fixed before launch. Rerun when the entry point, read order, STATE schema, worklog/session-record protocol, or authority structure changes, and at phase gates — never on every documentation edit. They run at wall milestones and any phase-exit claim; the harness exam system supersedes them at Phase 2+ (C6 now, reason code `no-mechanism` — manual fresh-context GLM sub-agent scenarios per INT-070).

### Exams

**Context Exam** (25 questions, printed with no key; answered in a file; owner grades with a key that stays outside the repo; pass = 90% with every trap question correct) — tests the memory itself: does a fresh agent actually absorb the repo? **Agent Exam** (from the MCP phase; fresh + sealed sets; 90% each; critical classes — fabricated source reference, cross-owner exposure — need 100%; the sealed set lives outside the repo; each run records model, host, version, seed, score). Exams record: the memory is only as good as its absorption.

---

## 10. Discipline sections

### Security standing rules

- The agent never holds the owner signing key; never edits gates/workflows once walls are live; never prints secret VALUES (isolation checks print conditions only — never `env` dumps: dumping the environment to check it for secrets is itself the leak).
- Builder/verifier: fixtures + test database only, never real owner data or secrets (LAW-28). Runtime agents: scoped API/MCP tokens only, never the database (NG-02). Purge is owner-only (D-011).
- Isolation verification is redacted by construction: required conditions listed, values never emitted.

### Host discipline

Hosts are supported only after passing the Host Contract on installed versions: how the host actually loads canonical instructions (AGENTS.md auto-load; CLAUDE.md `@path` imports), with a sentinel line and a transcript as proof — FACT entries required (LAW-02: never assume host behavior from documentation alone; reports conflict, spikes settle it). One canonical AGENTS.md; host bridges import it; bridges are verified artifacts, not conveniences.

### Language discipline

English. Tailored, technical, machine-readable, agent-optimized, clean. Stable IDs and reason codes everywhere; every check failure carries a reason code. One fact, one home. Supersede, never rewrite. ASD-STE100 (issue 9, Jan 2025) remains an EXPERIMENT — structure rules (IDs, reject examples, glossary) are the enforced part; sentence rules stay A/B-measured before any strictness decision; the fallback keeps the structure if plain prose scores better.
