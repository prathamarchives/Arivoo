# PRINCIPLES — The Owner's Laws (P-01..P-17)

The owner's laws, in the owner's verbatim words. Each entry carries five things: **WORDS** (verbatim, typos preserved), **MEANING** (the precise interpretation), **MECHANISM** (how it is enforced — the constraint-ladder level, the laws and checks that carry it, and the phase the mechanism arrives in), **FAILURE MODE** (the drift this law exists to prevent), and **GROWTH** (how the law behaves as the repo grows). Prose is the weakest rung (C6); every principle here is on its way up the ladder as the substrate is built (LAD-01/02/03).

Append-only: new laws get new numbers. Superseded laws keep their text and status. This file supersedes `context/extracted/00-PRINCIPLES.md` (kept as history).

---

## P-01 — THE BACKEND LAW

**WORDS.** "This session is solely for the backend." / "Backend: primarily for the base and the foundation and the real mechanism behind the software. It's not UI, it's not for UX."

**MEANING.** This build's scope is the base, the foundation, and the real mechanism. Not the interface. The backend is not "the part behind the UI" — it is the product at this stage; the UI arrives as a separate owner workstream that this backend must serve, not anticipate.

**MECHANISM.** C6 now (scope discipline: every plan, phase, card, and commit traces to the mechanism). From Phase 2: the audit's intent-trace check — a slice whose requirements do not trace to backend intent fails (LOOP-05). UI/UX work never gets a card.

**FAILURE MODE.** Scope creep into interface design — debating layout while capture durability is unproven; a beautiful shell over an unreliable mechanism.

**GROWTH.** Unchanged as the product grows: even when a reader client exists (Phase 4), it stays a client of the API, never a dependency of the backend, and backend slices never carry UI obligations.

## P-02 — THE MEMORY LAW

**WORDS.** "The repo is your memory, not recalls, not chat history." / "Make a temporary folder for context in the repo and drop all this lore into that. Your memory problem would be solved."

**MEANING.** Disk artifacts in this repo are the canonical memory. Chat history, session recall, and "what the model remembers" are not trusted state. Anything the next agent needs must exist as a file it can read.

**MECHANISM.** Partially mechanical already: the cold-start read order in `/AGENTS.md`; the worklog protocol (every task reads the log first, appends after); ledgers are append-only files. From Phase 2: the resume test (LAW-17) makes it a C4 property — a new session must be able to finish a half-done slice from files alone. From Phase 3: `make state` prints the live status from the repo, not from any agent's head.

**FAILURE MODE.** The compounding lie: work that "happened" in a chat but never landed on disk is work that never happened. Knowledge locked in a session dies with the session.

**GROWTH.** The memory gets more structured as it grows (raw corpus → extracted briefs → root canonical files → designed memory with OWNER:/AI: labels, FACTS, constraints register), but the law never changes: if it is not in the repo, it does not exist.

## P-03 — THE INCREMENTAL LAW

**WORDS.** "We will not execute all backend at once. We will go by small parts and phases, constantly refining and making them more aligned with my goal."

**MEANING.** No big-bang execution. The unit of work is a small part that gets built, verified, and refined against the goal — then the next part. Phases organize the work; they do not batch it.

**MECHANISM.** SIZE limits (LAW-05: ≤8 files / ≤400 source lines per slice); one behavior per slice; the phase loop (LOOP-01: a phase is a loop of build → exam → repair → repeat, no time limit). From Phase 2, the SIZE check is C5.

**FAILURE MODE.** The mega-slice: weeks of accumulated unverified code, one catastrophic integration moment, no idea which piece broke.

**GROWTH.** The slices stay small forever; only their subject matter grows (schema slices → feature slices → enrichment slices). What grows is the fraction of a feature that composes existing verified pieces.

## P-04 — THE CONTEXT-SUPREMACY LAW

**WORDS.** "I'll just give you context. You will know."

**MEANING.** The goal, architecture, and plan arrive through owner-provided context, not agent invention. Extraction over assumption. The agent's job is to receive, internalize, and reason — never to originate the goal.

**MECHANISM.** C6 (epistemic discipline, enforced by morals 1–7 in OPERATING-MODEL): intent traces to owner words; interpretations are always labeled; the Understanding Report copies owner statements rather than summarizing them (UNS-04). From Phase 2: the audit's intent-trace check (a requirement with no owner words or adopted decision behind it fails — LOOP-05).

**FAILURE MODE.** The agent that "knows better": silent substitution of its own design preferences for the owner's stated intent.

**GROWTH.** The corpus grows; the discipline stays. Every new owner statement lands verbatim in the Intent Ledger with a status; nothing gets reworded into "what the agent understood."

## P-05 — IDENTITY

**WORDS.** "arivoo is the repo arivo is the name."

**MEANING.** Product = **Arivo**. Repo = **Arivoo**. Owner = prathamarchives. Arivo is the owner's personal reading/study/reflection environment, built backend-first, designed to evolve into agent-native and VR/3D futures.

**MECHANISM.** C6 (naming discipline): the GLOSSARY fixes the vocabulary; terms used in ledgers, laws, cards, and code must come from it; renames supersede by reference, never rewrite.

**FAILURE MODE.** Naming drift — "Ivo", "Arivoo app", "the system" — which greppability (AFA-05) then can't save, and every future agent inherits the ambiguity.

**GROWTH.** One concept, one name, forever. The glossary only appends.

## P-06 — THE AUTONOMY LAW

**WORDS.** "i dont want accept/reject, and i need autonmy"

**MEANING.** No review queue in any form. No pipeline stage ever waits for an owner action. The system runs; the owner observes at gates, not at approval steps.

**MECHANISM.** NG-01 as a law: LAW-27 (no stage waits for an owner action; NG-01 scan, live Phase 3–5). Question classes keep autonomy honest without approval steps: blocking questions stop only the affected slice; defaultable questions proceed on a recorded default that the owner can override at the next touchpoint; silence past a named gate is consent for DEFAULTABLE questions only (D-012, QST-03 — scoped per the F-02 correction, 2026-10-13); blocking questions — owner intent, irreversible actions, security, data loss — stay open until the owner answers.

**FAILURE MODE.** The approval trap — a "quick sign-off" stage that quietly becomes a queue, and the build stalls exactly when the owner is busy. Autonomy designed as reversibility: every state change is reversible, so acting is safe without permission.

**GROWTH.** Autonomy widens with evidence: orchestrator-only now → builders at Phase 2 → recurring GC agents at the self-maintaining stage. Each widening is earned by the verification machinery of the stage before it, never by optimism.

## P-07 — THE NO-LATER LAW

**WORDS.** "like dont assume this way im not building V2 nd then wait weeks and months. but im dividing execution phases. so 'later' really frustates me. we will go like this engineer and run up execution in small phases build one part each time, test, verify, tweak, refine until its aligned with what we decided and our goal then move on to the next."

**MEANING.** Dependency-ordered, never calendar-ordered, never deferral-ordered. "Later" is not an answer; it is a refinement-debt entry with a reopening trigger. Phases sequence work by dependency and evidence — they do not postpone it.

**MECHANISM.** The List — the refinement-debt register (`context/extracted/07-ON-THE-LIST.md`, D-020): implementation slices sequenced out of the active order, each with a reopening trigger; core capabilities can never leave the active sequence through it. NG-04 (no detailed plan beyond the next phase) — one phase deep, because deep planning of unpromised future work is deferral in disguise. Audit: a capability confirmed by owner words that appears nowhere in the active sequence is a drift finding.

**FAILURE MODE.** The "V2 parking lot": core capabilities quietly reclassified as future enhancements, then silently dropped (the exact failure the verdict's §4 attacked: "Meaning-based search comes later" contradicting the locked architecture).

**GROWTH.** The List shrinks as items enter the active sequence with their trigger conditions; it never becomes a graveyard. Architecture-level commitments (P-16) can never enter The List at all — only implementation slices can.

## P-08 — THE EPISTEMICS LAW

**WORDS.** "the system must not miss or loose concepts after a session of resoning through research, and studying" + the fact/concept definition (INT-025).

**MEANING.** Discovery is not evidence. Attention is not truth. A fact tag classifies a statement type; it never certifies truth — truth lives in relations between fragments, decided by Kev policy on grounded evidence. Auto-detected concepts are provisional until out-of-sample evidence graduates them.

**MECHANISM.** C6 now; C4/C5 from Phase 5: agent-authored material carries zero belief weight (D-019) — it is stored as attributed information about what the agent said, never as corroboration; evidence for inferred relations comes only from grounded text-pair decisions or structural facts. Fact-tag semantics: OPEN (Q3) — intended-factual with separate verification status is the staged default.

**FAILURE MODE.** The system that manufactures truth: agent assertions counted as evidence, popularity counted as confirmation, junk concepts minted automatically and never pruned.

**GROWTH.** The belief machinery arrives late and calibrated (Kev policy + evaluation gates at its band), but the epistemic boundary is wired from the first derived table: provenance on every derived row (LAW-20), explainability and reversibility on every derived claim (C5).

## P-09 — THE AGENT-CLIENT LAW

**WORDS.** "not just AIOS any agent user can host a secured API/MCP and expose it to there agents" / "doesnt matter which agent API/MCP exposed would let any agent connect so it could be multiple"

**MEANING.** Agents are clients of Arivo, never components of it. Attributed, scoped, capability-gated, zero-weight in belief. The API/MCP surface IS a product surface — layer 6, "the product, and only agents can test it."

**MECHANISM.** NG-02 as law: LAW-26 (runtime agents never reach the database; API or MCP with scoped tokens; boundary lint + NG-02 test). NG-03 as law: LAW-29 (no generative model inside Arivo's pipeline — the owner's external agents reason; Arivo's pipeline only computes). One command registry behind HTTP, CLI, and MCP adapters (K10) so no client invents its own mutation path. The surface contract (D-019): scoped reads, attributed writes, idempotency, bounded responses, stable error codes.

**FAILURE MODE.** The privileged agent: a client that can touch the database, silently becomes part of the mechanism, and its outputs start manufacturing truth inside the system.

**GROWTH.** More agent families connect (INT-030: any agent, multiple simultaneously) — none of them gains authority. The MCP adapter is read-first (F-10-era decision, MCP-read), writes when the attribution layer is proven.

## P-10 — THE TWO-SPEED CONCEPTS LAW

**WORDS.** "i dont wanna miss or loose concepts after a session" / "remove the assumption of slow compounding, slow concepts" / "we can do like tags while i highlight... for intial stage we can do that and system trains on it when it is good enough but thats not my first priority i would make it more like personal wikipedia"

**MEANING.** Two formation speeds, one junk gate. Owner-declared and owner-tagged concepts are instant and authoritative. Auto-detected concepts are also instant (not slow — the assumption of slow compounding is removed) but provisional. The junk gate lives at graduation, not birth: provisional concepts graduate on out-of-sample evidence, never on volume.

**MECHANISM.** C6 now (model semantics in GLOSSARY); C4 from Phase 5: concept induction with provenance, graduation tests, and the Kev classifier behind policy/eval gates. Capture-time tags are custom and owner-authored (INT-069, 2026-10-13): the owner manually writes what kind of highlight it is, if they want — there is NO default fact/concept classification; the fact/concept/quote vocabulary stays available to the owner, never imposed, and the system trains on owner-authored tags when good enough (INT-028, INT-088). *(Supersedes the earlier "typed tags (`fact`, `concept`, free)" mechanism per EXR-08 — the latest owner statement governs; the WORDS above are history.)*

**FAILURE MODE.** Two symmetric failures: concepts lost after a reasoning session (owner's stated worst-of-class), and junk concepts minted automatically with no graduation discipline.

**GROWTH.** Concept pages become the personal wiki (label, gloss, aliases, evidence with provenance, linked fact fragments) — growing entities, never static categories.

## P-11 — THE PLAN-MODE TRANSFER LAW

**WORDS.** "giving execution agent whole context in plan mode what arivo is and making them reason through everything we have done to starting the repo"

**MEANING.** The first agent session receives the whole corpus in plan mode and reasons through all prior work before the repo starts. Context transfer is an event, not a trickle: full corpus → read-only reasoning → Understanding Report → owner grade.

**MECHANISM.** Executed by this build's origin session (this first layer is its output). Repeatable as the Understanding Session protocol (UNS-01..07) whenever a fresh orchestrator takes over: read AGENTS.md → canonical files → corpus; copy owner statements, never summarize; mark claims with sources; end with the report.

**FAILURE MODE.** The successor agent that starts from a summary and inherits the summarizer's blind spots — context decay compounding at every generation.

**GROWTH.** As the repo's own memory becomes complete, the corpus-reading requirement narrows: the designed-memory migration closes the corpus (FX-07), and cold-start becomes AGENTS.md → canonical files → `make state`. The law's invariant survives: a fresh session must be able to acquire everything it needs from the repo alone.

## P-12 — THE SUBSTRATE LAW

**WORDS.** (from the architecture line the owner locked): ground truth is append-only; everything else is derived and rebuildable; capture never waits for intelligence; every derived claim is explainable and reversible.

**MEANING.** The data substrate is a two-tier architecture: an append-only evidence tier (highlights, notes, journal revisions, bookmarks, tags, behavior events, source snapshots — edit = new revision, delete = tombstone) and a derived tier that is entirely rebuildable (every derived row carries provenance: run ID, versions, input hash).

**MECHANISM.** The substrate laws: LAW-19 (evidence immutable, C1+C2: no update/delete function exists; triggers reject both), LAW-20 (provenance on derived rows, C1), LAW-23 (commands atomic + idempotent + acknowledged after commit, C1), LAW-21/22 (owner scope + actor on every write; RLS; two-owner test). The standing design test for ANY schema change: **can every derived row be deleted and rebuilt with zero loss?** If not, derived state has leaked into ground truth — a design defect.

**FAILURE MODE.** Silent data mutation and unrebuildable derived state — the two ways "nothing is lost" dies without anyone noticing.

**GROWTH.** More derived layers (keyword index → embeddings → relations → concepts) each rebuildable from the evidence tier; the purge path (D-011) is the only authorized exception, itself ledgered.

## P-13 — THE OPERATING MODE LAW

**WORDS.** "you run, i review."

**MEANING.** The orchestrator executes everything; the owner reviews at gates. The owner is the authority on intent and the holder of keys — not a queue participant.

**MECHANISM.** Role table in OPERATING-MODEL: owner-only actions are enumerated (signing key, exam keys, sealed test sets, the arivo-owner folder, phase-gate tags, protected-path approvals, purge) — everything else the agents run. Review artifacts are designed for minutes of owner time: the Proof Sheet, the Demo Review, the adversarial check lists.

**FAILURE MODE.** Mode inversion — agents waiting for instructions (idling the machine), or the owner dragged into micro-approval (killing autonomy, P-06).

**GROWTH.** Owner review effort per unit of work shrinks as verification machinery matures — that is the entire point of the trust ladder. The owner's irreducible roles (intent, keys, judgment at gates) never delegate.

## P-14 — THE PIECE-BY-PIECE LAW

**WORDS.** "we'll start by developing the architecture of the repo, the rules, the laws, the principles, the plan, the design, and then execute small pieces: execute a piece and then refine and iterate... We keep doing it until that piece is aligned to our goal and serving as exactly we want it to serve, and then we'll move on to the next piece."

**MEANING.** Architecture first — deeply. Then small pieces. Each piece iterates until it is EXACTLY right, then and only then does the next piece start. Depth distribution: deep architecture, shallow plans (one phase, NG-04), deep pieces.

**MECHANISM.** This first layer is the architecture-first half, executed. The piece loop is the phase/slice loop with its exit predicates (LOOP-04): all requirements pass, known-bads at 100%, no critical/high gap, two consecutive seed-different runs, owner-signed gate. "Aligned to our goal" is measured bidirectionally (intent traces to tests; requirements trace to owner words).

**FAILURE MODE.** Moving on from a "mostly working" piece — unrefined foundations accumulate, and every later piece inherits their error.

**GROWTH.** The definition of a "piece" scales (a slice → a feature band → a phase), but the exit discipline is invariant: no piece is left half-aligned.

## P-15 — THE CONTINUOUS-COMMIT LAW

**WORDS.** "In this session every time you reason and something changes, you add new information, and something changes, you update your memory and repo. Log that in and you commit it so it really pushes on the repo."

**MEANING.** Every reasoning delta — a decision, a law, a tension, an extraction, a plan change, a failure, a question — becomes a file update, then a commit, then a push. Same-session. Chat is where understanding is built; the repo is where it lives.

**MECHANISM.** The commit protocol in OPERATING-MODEL (the delta → file → commit → push pipeline, with the worklog append). From Phase 1, the walls make this safe (protected main, PR-only) — memory commits are still direct to main by the owner's design (doc-only commits; code goes through the slice gate once code exists).

**FAILURE MODE.** The lost conclusion: a brilliant session that ends unpushed. It never happened (P-02).

**GROWTH.** Once code exists, commits split: memory deltas (doc commits, immediate) vs code changes (slice-gated, PR + CI). Both remain continuous — neither kind waits for a batch.

## P-16 — THE ARCHITECTURE-EVOLUTION LAW

**WORDS.** "I don't want it to be like, 'Okay let's ship version 1 and version 2 can come later (like semantic search, vector search, those cases).' No I don't want to compromise that. I really want to have this solid updated backend that can evolve into future versions, like an agent-native version or a VR 3D hardware version. Keep that vision in mind."

**MEANING.** Semantic indexing, vector retrieval, relationship processing, concept formation are architectural commitments from day one — in the active implementation sequence, implemented through small tested slices (D-015). Deferral of the ARCHITECTURE is forbidden; incremental delivery of the IMPLEMENTATION is mandatory. The backend must evolve cleanly into agent-native and VR/3D futures.

**MECHANISM.** The phase sequence ends at retrieval + compounding, not at capture (PLAN Phase 5); the compounding probes ladder (deterministic → semantic → graph) makes C3 testable at each strength; pgvector on the data-layer decision (D-003); every schema/kernel contract designed with the later layers in view (two outboxes, provenance on derived rows, typed vocabularies). The audit flags any "comes later" language attached to a locked architectural capability.

**FAILURE MODE.** The V1 trap: a capture-only design whose contracts can't carry semantic retrieval, forcing a rewrite instead of an evolution.

**GROWTH.** This law is the repo's teleport anchor: agent-native and VR/3D-hardware are evolution targets the substrate must be able to grow into, never rewrites.

## P-17 — THE PRODUCT-FIRST LAW

**WORDS.** "Build a small, real slice of Arivo. Verify it independently. Refine it until it matches the intended behavior. Turn the lessons into constraints. Repeat." / "The harness and repository memory make this loop safer. They must not become reasons to postpone the product."

**MEANING.** The verification system exists to protect the product loop. The governing loop is the product loop. If the harness starts delaying the workflow it protects, that is drift — and it gets ratcheted like any other failure.

**MECHANISM.** The phase order (D-016): trust environment → minimum harness → durable capture → reader+journal → retrieval+compounding. The minimum harness is PROACTIVE GUARDRAILS ONLY (isolated credentials, protected gates, real database test, idempotent writes, immutable evidence, owner scoping, independent state read) — not the complete constraint system, not all architecture checks, not every kernel primitive, not every planned known-bad. Each further mechanism arrives when it protects a concrete contract, through the ratchet.

**FAILURE MODE.** The meta-project: a perfect harness for a product that doesn't exist; the setup process becomes a project in itself (the verdict's central warning — the F-band's first real behavior at F-08 was exactly this failure).

**GROWTH.** The equilibrium this law holds forever: harness capability and product capability grow together, each responding to the other's real failures. Neither leads by more than one phase.
