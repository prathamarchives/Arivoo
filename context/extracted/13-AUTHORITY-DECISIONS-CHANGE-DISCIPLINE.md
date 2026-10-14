# 13 — Authority Map, Decision States, Change Discipline: The Three Slices and Their Proofs

> STATUS: **SESSION ENGINEERING RECORD** (2026-10-14, the three-slices session — INT-093..099/D-026). Historical process artifact per D-022: assistant analysis and work record; NOT owner intent, outranks nothing. Owner words live only in `/INTENT-LEDGER.md` (INT-093..099 added this session). Worklog entry: Task 12. Verifier: `tools/verify_canonical_layer.py` (46 checks, C1–C8) + `tools/isolation_check.py` — runs recorded in §5. PRs this session: #6 (verifier repair, merged `fdeeebe`), #7 (known-bad probe, closed unmerged by design), #8 (this session's corpus), #9 (close).

## 1. What the owner asked (verbatim — owner turn 9, 2026-10-14)

> read the repo, fair, now the goal is Objective: Any capable agent can enter Arivo's repository, understand the project, identify the next correct action, work within its authority, verify its work, and leave the repository easier to continue from.
>
> Slice 1: Establish the authority map
>
> Make the entry point explain the purpose of each existing canonical source:
>
> Intent Ledger: what the owner actually said.
>
> Principles: enduring guiding principles.
>
> Laws: constraints that must have mechanisms or checks.
>
> Decisions: adopted choices and open owner questions.
>
> North Star: what Arivo is supposed to accomplish.
>
> Engineering and operating model: how to build and verify it.
>
> Plan: current phase, dependencies, and exit gates.
>
> Every concern should have one authoritative home. References elsewhere point to that home rather than copying its rules.
>
> Proof: Give a fresh agent conflicting instructions in a test scenario. It identifies the authority that governs the conflict instead of averaging the instructions or silently choosing whichever it read last.
>
> We should build Arivo first, let implementation and real usage expose what the architecture actually needs, and do the comprehensive refinement pass once the product exists. We shouldn't spend the next few weeks making the repository's documentation internally perfect while the product remains unbuilt.
> There are two separate jobs here.
> During execution: preserve the evolving truth.
> The Intent Ledger, Decisions, Principles, and architecture documents are allowed to evolve as you learn. The repository needs to capture meaningful new instructions, preserve the history of decisions, and make the current direction clear enough that the next agent doesn't guess.
> But that doesn't mean every insight requires a broad documentation reconciliation. Update what the current task needs. If an existing decision becomes wrong, supersede it properly. If a future architectural question doesn't affect the current slice, leave it open.
> Most importantly, don't let stale documentation cause a real implementation mistake. Fix contradictions that affect the current work; leave unrelated editorial debt for later.
> After Arivo is built: refine the whole system.
> Once the end-to-end product exists, you'll have something much more valuable than today's theoretical architecture: evidence from the actual implementation.
> Then you can conduct a comprehensive refinement pass across the Intent Ledger, decisions, principles, laws, North Star, architecture, and future vision. Determine which assumptions survived contact with reality, which decisions were superseded, which capabilities were actually delivered, and what the next version should become.
> Historical owner statements should remain intact. Refinement means clarifying the current direction and marking superseded decisions—not rewriting history to pretend you always knew the answer.
>
> Capture continuously. Correct what can mislead today's work. Defer comprehensive refinement until implementation gives you evidence.
>
> then execute these other slices
>
> Slice 2: Make unresolved decisions safe
>
> An agent must distinguish four states: owner decision, adopted decision, proposed recommendation, and unresolved question.
>
> When something is unresolved, the agent records the question, its consequence, and exactly which work depends on the answer. Unrelated safe work can continue.
>
> The identity of the builder is not an architectural blocker. The system must define responsibilities and verification obligations, not require a particular named agent to remain available.
>
> Proof: A fresh agent can identify an unresolved architecture decision and refrain from treating a recommendation or elapsed time as approval.
>
> Slice 3: Enforce scope and change authority
>
> Establish the actual branch-and-PR workflow.
>
> No direct commits to main.
>
> Each change has a coherent purpose and a bounded diff.
>
> Review-only requests result in findings, comments, issues, or a report—not unsolicited implementation changes.
>
> Implementation and revert changes are proposed separately when appropriate.
>
> Merging remains owner-controlled unless explicitly delegated.
>
> The repository's access settings, branch protection, and required checks must be observed working rather than described as if they already exist.
>
> Proof: A test change travels through the intended review path, and the protected branch rejects any prohibited route that the configured system is supposed to block.
>
> refine and iterate until algined and strong and then we'll reason through nexts

## 2. Starting state and method

- Starting commit: `b510baa` (main, post session 12; PRs #1–#5 all merged, 0 open; branch protection observed live: PRs required, `canonical-layer` required + strict, admins included, no force push, no deletions, required_approving_review_count 0 — the Q-IDENT-compatible configuration). Verifier at start: 46 checks green, self-test 20/20, isolation green (re-run before any edit — trust runs, not recollection).
- Cold-start read as a fresh agent (AGENTS v2.4 read order: ledger → STATE → NORTH-STAR → PRINCIPLES → LAWS → DECISIONS → EXECUTION → PLAN → GLOSSARY → OPERATING-MODEL → worklog tail → session records 11/12 → manifest → review protocol).
- Method: map the three slices against the current repo (gap analysis, §3); repair the drift landmines FIRST (PR #6: the MUT-17 content-coupling — the repo's own required check would have RED-blocked the next legitimate record-adding PR); run the two live path proofs (§5.2); land the corpus refinements (§4); run the two behavioral proofs as fresh-context GLM sub-agents (§6); then STATE/worklog/record close.
- Wall discipline honored: the verifier change (PR #6) is gate REPAIR under the owner's "refine and iterate until aligned and strong" directive — landed as its own PR with evidence, strengthening (never weakening) a guard; the workflow file itself was never touched.
