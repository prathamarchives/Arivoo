# Arivoo — Principles Ledger (Laws of Execution)

> SUPERSEDED 2026-10-13 by the canonical root `/PRINCIPLES.md` (first layer). This file is kept as extraction history; the root file governs. Do not update this copy.

Source of truth: the user's explicit statements, verbatim. Nothing here is assumed.
Status legend: CONFIRMED = user said it directly. PENDING = awaiting deeper context.

---

## P-01 — THE BACKEND LAW — CONFIRMED
> "This session is solely for the backend."
> "Backend: primarily for the base and the foundation and the real mechanism behind the software. It's not UI, it's not for UX."

Implications:
- Scope of this session = base, foundation, real mechanism. Zero UI/UX work.
- Every plan, every phase, every commit must trace to the mechanism, not the interface.

## P-02 — THE MEMORY LAW — CONFIRMED (deepening pending)
> "The repo is your memory, not recalls, not chat history."

Implications:
- Durable artifacts on disk / in the repo are the canonical memory. Chat history and recall are NOT trusted state.
- Every conclusion, decision, and piece of understanding must be written into files, not left to live only in conversation.
- User note: "we'll go deeper on that once you get all the context." → semantics of repo-as-memory will be refined in Phase 2.
- SEEDED 2026-10-13 (D-006, owner directive): "Make a temporary folder for context in the repo and drop all this lore into that. Your memory problem would be solved." — corpus + ledgers + worklog committed at context/ (temporary; restructured into the designed memory at playbook Step 2 / F-01). The repo is now the canonical memory; every session starts by reading it.

## P-03 — THE INCREMENTAL LAW — CONFIRMED
> "We will not execute all backend at once. We will go by small parts and phases, constantly refining and making them more aligned with my goal."

Implications:
- No big-bang execution. Small parts → phases → review → refine against the goal.
- The goal (arriving via context) is the alignment target for every refinement cycle.

## P-04 — THE CONTEXT-SUPREMACY LAW — CONFIRMED
> "I'll just give you context. You will know."
> "You will extract it, read through it, and understand it."

Implications:
- The goal, architecture, agents, and execution plan arrive through context the user pastes.
- Extraction over assumption. Never invent the goal; receive it.

## P-05 — IDENTITY — CONFIRMED (repo metadata + owner naming)
- Repo: prathamarchives/Arivoo — private, empty, created 2026-10-13
- Description (user's words): "personal studying evniroment"
- Nature: a personal studying / reflection environment (reading, research, writing, practice) — built backend-first.
- Naming (D-002, owner 2026-10-13): product name is **Arivo**; repo slug **Arivoo** stays. Owner: "arivoo is the repo arivo is the name".

---

## Pending (to be filled from context intake)
- [x] The Goal — LOCKED (corpus intake complete; see 02-OWNER-VOICE-AND-EVOLUTION.md): a solid learning environment where study/research/write/read compounds, nothing disappears, agents use all of it; personal wikipedia; journal as writing lab; worst failure = losing a highlight
- [x] The Principles/Laws of the repo — LOCKED in the two Arivoo docs (29 laws, constraint ladder, kernel; see 03-ARIVO-CURRENT-STATE.md)
- [x] Architecture — LOCKED direction (append-only ground truth, derived/rebuildable everything else, one API core + MCP adapter, actor on every write, idempotent commands, belief machinery deferred to later bands); data layer LOCKED (D-003): Postgres with pgvector, local-first now, cloud sync later
- [x] Agent roster & execution plan — LOCKED (owner playbook 13 steps + agent spec F-00..F-09 foundation slices; orchestrator/builder/verifier separation; ratchet)
- [x] Deepened Memory Law (P-02) — owner's exact words: "the repo is the memory. define laws. strict so agent does not drift or fuck up anything and just keep at it until what we need is achieved" (INT-031, INT-032)

## Additional laws confirmed by the corpus

## P-06 — THE AUTONOMY LAW — CONFIRMED
> "i dont want accept/reject, and i need autonmy"
No review queue in any form. No pipeline stage waits for an owner action (NG-01). Autonomy = beliefs + bands + canaries + breakers + reversible state changes.

## P-07 — THE NO-LATER LAW — CONFIRMED
> "im not building V2 nd then wait weeks and months... 'later' really frustates me"
Dependency-ordered, never calendar-ordered. The machine never idles. "Later" is only a refinement-debt ledger entry with a reopening trigger.

## P-08 — THE EPISTEMICS LAW — CONFIRMED (from rounds of hardening)
Discovery is not evidence. Attention is not truth. Facts are fragments (statement types), never truth flags; truth lives in relations. A fact tag classifies, does not certify.

## P-09 — THE AGENT-CLIENT LAW — CONFIRMED
> "not just AIOS any agent user can host a secured API/MCP and expose it to there agents"
Agents are clients: attributed, scoped, capability-gated, weight-0 in belief. Any agent can connect; the surface is the product. Agents never touch the database.

## P-10 — THE TWO-SPEED CONCEPTS LAW — CONFIRMED
> "remove the assumption of slow compounding, slow concepts... i would make it more like personal wikipedia"
Owner-declared/tagged concepts are instant and authoritative; auto-detected ones are instant but provisional. The junk gate lives at graduation, not birth.

## P-11 — THE PLAN-MODE TRANSFER LAW — CONFIRMED
> "giving execution agent whole context in plan mode what arivo is and making them reason through everything we have done to starting the repo"
The first agent session receives the whole corpus in plan mode and reasons through it before the repo starts. (This session executes P-11.)

## P-12 — THE SUBSTRATE LAW — CONFIRMED (from the architecture rounds)
Ground truth is sacred/append-only; interpretation is derived/rebuildable; capture never waits for intelligence; every derived claim is explainable and reversible. Any design change must pass: can every derived row be deleted and rebuilt with zero loss?

## P-13 — THE OPERATING MODE LAW — CONFIRMED (owner, 2026-10-13)
> "you run, i review."

Implications:
- The orchestrator executes (playbook steps, slices, scripts, checks, verification runs); the owner reviews at gates and touchpoints.
- Owner-side actions remain owner-only regardless of mode: signing key, sealed tests/exam keys, arivo-owner folder.
- Nothing enters the repo unreviewed. Plan mode holds until the owner says go.

## P-14 — THE PIECE-BY-PIECE LAW — CONFIRMED (owner, 2026-10-13)
> "we'll start by developing the architecture of the repo, the rules, the laws, the principles, the plan, the design, and then execute small pieces: execute a piece and then refine and iterate... We keep doing it until that piece is aligned to our goal and serving as exactly we want it to serve, and then we'll move on to the next piece."

Implications:
- Order: architecture, rules, laws, principles, plan, design FIRST — then execution in small pieces.
- Each piece iterates until it is aligned to the goal and serves exactly as intended; only then does the next piece start.
- Guardrail (NG-04): detailed plans stay one phase deep. Architecture is deep and stable; plans are shallow; pieces are deep. Architecture-first is NOT big-design-up-front.
- Graduation criteria per piece: acceptance criteria + proof; from F-09 on, one-shot by a fresh agent with zero owner edits.
