# PRINCIPLES — Arivo (Laws of Execution)

The laws that bind all agents in this repo. Source of truth: the owner's explicit statements, verbatim. Nothing here is assumed. This file supersedes `context/extracted/00-PRINCIPLES.md` (kept as history). Append-only: new laws get new numbers; superseded laws keep their text and status.

---

## P-01 — THE BACKEND LAW
> "This session is solely for the backend." / "Backend: primarily for the base and the foundation and the real mechanism behind the software. It's not UI, it's not for UX."
Scope = base, foundation, real mechanism. Zero UI/UX work. Every plan, phase, commit traces to the mechanism, not the interface.

## P-02 — THE MEMORY LAW
> "The repo is your memory, not recalls, not chat history."
Disk artifacts in this repo are the canonical memory; chat history and recall are NOT trusted state. Seeded 2026-10-13 (D-006). Every session starts by reading this repo.

## P-03 — THE INCREMENTAL LAW
> "We will not execute all backend at once. We will go by small parts and phases, constantly refining and making them more aligned with my goal."
No big-bang execution. Small parts → phases → review → refine against the goal.

## P-04 — THE CONTEXT-SUPREMACY LAW
> "I'll just give you context. You will know."
The goal, architecture, agents, and execution plan arrive through context the owner provides. Extraction over assumption. Never invent the goal; receive it.

## P-05 — IDENTITY
Product = **Arivo**; repo = **Arivoo** ("arivoo is the repo arivo is the name"). Owner = prathamarchives. Arivo is a personal reading/study/reflection environment, built backend-first.

## P-06 — THE AUTONOMY LAW
> "i dont want accept/reject, and i need autonmy"
No review queue in any form; no pipeline stage waits for an owner action. Autonomy = beliefs + bands + canaries + breakers + reversible state changes.

## P-07 — THE NO-LATER LAW
> "im not building V2 nd then wait weeks and months... 'later' really frustates me"
Dependency-ordered, never calendar-ordered. "Later" is a refinement-debt entry with a reopening trigger (The List), never an answer.

## P-08 — THE EPISTEMICS LAW
Discovery is not evidence. Attention is not truth. A fact tag classifies statement type, never certifies truth — truth lives in relations. (Tag semantics: Q3 open.)

## P-09 — THE AGENT-CLIENT LAW
> "not just AIOS any agent user can host a secured API/MCP and expose it to there agents"
Agents are clients: attributed, scoped, capability-gated, weight-0 in belief. The surface is the product. Agents never touch the database.

## P-10 — THE TWO-SPEED CONCEPTS LAW
Owner-declared/tagged concepts are instant and authoritative; auto-detected ones are instant but provisional. The junk gate lives at graduation, not birth.

## P-11 — THE PLAN-MODE TRANSFER LAW
> "giving execution agent whole context in plan mode what arivo is and making them reason through everything we have done to starting the repo"
The first agent session receives the whole corpus in plan mode and reasons through it before the repo starts. (Executed by this build's origin session.)

## P-12 — THE SUBSTRATE LAW
Ground truth is append-only; interpretation is derived and rebuildable; capture never waits for intelligence; every derived claim is explainable and reversible. Test for any design change: can every derived row be deleted and rebuilt with zero loss?

## P-13 — THE OPERATING MODE LAW
> "you run, i review."
The orchestrator executes; the owner reviews at gates. Owner-side actions remain owner-only: signing key, exam keys, arivo-owner folder.

## P-14 — THE PIECE-BY-PIECE LAW
> "we'll start by developing the architecture of the repo, the rules, the laws, the principles, the plan, the design, and then execute small pieces: execute a piece and then refine and iterate... We keep doing it until that piece is aligned to our goal and serving as exactly we want it to serve, and then we'll move on to the next piece."
Architecture first; then small pieces; each piece iterates until exact; only then advance. Guardrail: NG-04 — deep architecture, shallow plans (one phase deep), deep pieces.

## P-15 — THE CONTINUOUS-COMMIT LAW
> "In this session every time you reason and something changes, you add new information, and something changes, you update your memory and repo. Log that in and you commit it so it really pushes on the repo."
Every reasoning delta — decision, law, tension, extraction, plan change — becomes a file update, then a commit, then a push. An unpushed conclusion is a lost conclusion.

## P-16 — THE ARCHITECTURE-EVOLUTION LAW
> "I don't want it to be like, 'Okay let's ship version 1 and version 2 can come later (like semantic search, vector search, those cases).' No I don't want to compromise that. I really want to have this solid updated backend that can evolve into future versions, like an agent-native version or a VR 3D hardware version."
Semantic search, vector retrieval, relationship processing, concept formation are architectural commitments from day one. Implementation is incremental through small slices; deferral of the architecture is forbidden. The backend must evolve cleanly into agent-native / VR-3D-hardware futures.

## P-17 — THE PRODUCT-FIRST LAW
> "The harness and repository memory make this loop safer. They must not become reasons to postpone the product."
The verification system exists to protect the product loop. If it starts delaying the workflow it protects, that is drift — ratchet it. Governing loop: "Build a small, real slice of Arivo. Verify it independently. Refine it until it matches the intended behavior. Turn the lessons into constraints. Repeat."
