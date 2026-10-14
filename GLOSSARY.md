# GLOSSARY — Arivo

Controlled vocabulary. One concept, one name — no synonyms. **Scope: this policy governs the repo's documentation and architecture vocabulary only.** Arivo's knowledge graph deliberately supports synonyms, aliases, and multiple surface forms for the same concept (P-10: concept pages carry aliases) — no agent may enforce the documentation-vocabulary policy against user material. Terms used in ledgers, laws, cards, and code must come from here. New terms enter by append; renames supersede by reference.

## Identity
- **Arivo** — the product: the owner's reading/study/reflection environment. (The owner also says "Ivo" casually; Arivo is canonical per D-002.)
- **Arivoo** — this repository.
- **Owner** — prathamarchives. The only authority on intent; words recorded verbatim.
- **Orchestrator** — the coordinating agent (Super Z lineage): holds corpus understanding, enforces laws, gates artifacts, runs the ratchet, commits. **Super Z** — the GLM-based host agent family that runs the orchestrator role (the current default per D-028/INT-070 — agent-agnostic by design: GLM also runs the test/verification subagents as the current default, never a requirement; a host change is a default change, never a redesign).
- **Builder** — fresh-context subagent working from a self-contained card. Never verifies its own work.
- **Verifier** — fresh-context subagent: reads card + proof sheet + diff only; writes failing tests only; advisory — the gate decides.
- **Host** — a coding-agent environment operating on this repo (GLM-based agent/CLI, Claude Code, Codex CLI). Supported = passed the Host Contract.
- **Host Contract** — verified requirements for a host to be supported (loads canonical instructions, respects walls, cannot fabricate verification).
- **Host Bridge** — a host-specific file (e.g. `CLAUDE.md`) that imports the canonical `AGENTS.md`. Verified on installed versions, never assumed.

## Product objects (minimum durable model)
- **Work** — a readable thing (book, article, paper, post, manga...). Identity separate from any imported file.
- **Source** — a specific version/edition of a Work that was imported. Provenance survives re-parsing, renaming, re-indexing.
- **Highlight** — committed selected text with stable identity, immutable revision, and an **Anchor**.
- **Anchor** — the durable pointer into a Source (page/passage/position). A highlight without its anchor is not durable.
- **Bookmark** — a durable saved location in a Source.
- **Note** — the owner's raw thinking attached to a page/passage; deep, revisioned, may contain diagrams (data support required). Not a sticky note (INT-044).
- **Journal block** — a revisioned writing unit of the day-page journal.
- **@-reference** — a stable reference to another object (highlight, note, work, concept). Survives renames. Not text that happens to look like a reference.
- **Reading session** — a period of reading a Source; emits coarse position/dwell checkpoints as behavior events.
- **Fact tag / Concept / Quote — tag vocabulary REMOVED (D-030, INT-112, 2026-10-14; supersedes INT-069's custom-tag re-scope):** highlights carry no tag field; a classification word ("concept", "fact", "quote"), if the owner writes one, is free text — never a structured feature, never system-imposed. **Concept** — unchanged: a growing entity that links to works and carries provenance (formed by concept formation on grounded evidence, never by capture tags). **Quote** — creative/writing the owner liked — an owner's free-text description, never a system vocabulary.
- **Decision states (the four)** — owner decision / adopted decision / proposed recommendation / unresolved question (INT-098, D-026): the explicit mapping onto DECISIONS statuses (LOCKED/PRESENTED-LOCKED / ADOPTED / OPEN) + `context/reviews/` artifacts. Elapsed time is never approval (QST-03). Home: `/DECISIONS.md` legend.
- **Evolving truth / comprehensive refinement pass** — P-18 (INT-094/095/096): during execution, documentation updates repair only what can mislead current work (supersede properly, never rewrite); after the product exists, ONE comprehensive refinement pass judged against implementation evidence, history intact. Homes: `/PRINCIPLES.md` P-18, `/PLAN.md` post-product pass.
- **Behavioral proof** — a fresh-context sub-agent scenario testing an agent-layer property under pressure: the authority-conflict test (identify the governing authority — never average, never last-read-wins) and the unresolved-decision test (never treat recommendation, presence, or elapsed time as owner approval). Standing method at wall milestones; home: `/OPERATING-MODEL.md` §9.

## Substrate
- **Ground truth** — append-only evidence (highlights, revisions, behavior events; tag events removed with the tag system — D-030/INT-112, 2026-10-14). Edit = new revision; delete = tombstone.
- **Derived** — rebuildable interpretation; every derived row carries provenance (run ID, versions, input hash). Deletable and rebuildable with zero loss.
- **Tombstone** — ordinary delete: hidden from normal retrieval, recoverable.
- **Purge** — owner-only deliberate erasure of content + derived material (embeddings, decisions, edge evidence, candidate records, unreferenced blobs); minimal audit record; restore applies the purge ledger. Runtime agents cannot invoke.
- **Client outbox** — on-device durability queue; preserves new work offline and replays to the cloud when available.
- **Server outbox** — post-commit job scheduler for enrichment. A different problem from the client outbox.
- **Durability ladder** — `local-durable → server-durable → keyword-searchable → semantically indexed → linked`. Safety claims never exceed the current rung.
- **The List** — the refinement-debt register (`context/extracted/07-ON-THE-LIST.md`, D-020): implementation slices sequenced out of the active order, each with a reopening trigger. NOT "confirmed-but-deferred capabilities": a capability confirmed by owner words never leaves the active sequence, and architecture-level commitments (P-16) can never enter the register at all. The register shrinks as items enter the sequence; it never becomes a graveyard.

## Execution
- **Slice** — one behavior, size-limited, one card. The unit of build.
- **Card** — the self-contained slice spec (context pack) a fresh agent works from.
- **Proof Sheet** — harness-built evidence for a slice. Never hand-edited.
- **Gate / verify** — the command surface + CI authority. Local verify helps the builder; remote CI (owner-controlled) is authoritative.
- **Ratchet** — failure → constraint at the strongest layer; baseline never regresses. Two-strike: a repeated class moves up a level.
- **Known-bad** — a deliberately broken build that must fail with its code. A miss turns the harness red and stops building.
- **Walls** — repo protections: protected main, PR-only, no force push, required check restricted to the trusted source, CODEOWNERS.
- **Proactive set** — the guardrails present from day one: isolated credentials · protected gates · real database test · idempotent writes · immutable evidence · owner scoping · independent state read.
- **Kev** — the decision/classification machinery (kernel port; policy + evaluation gates at its band).
- **Compounding probes** — the C3 test series, tested separately: deterministic → semantic → graph.
- **EXECUTION.md** — the canonical execution-contract authority: the contract map (one authoritative home per concern), the source tiers, the authority order, and the change protocol. Other files point to it; no parallel execution spec exists (D-021).
- **Source tiers** — the five source classes (raw archive / intent ledger / decision ledger / root canonical docs / extracted briefs) and their authority roles. Defined in `/EXECUTION.md` §2.
- **STATE.md** — the current-state and navigation index. **Contract (D-027, owner turn 10): five areas, one screen, pointers not detail** — position (phase + operating model + whether the next phase is planned/approved/started) · work (active task — what the current/last agent is doing, failed at, or left unfinished — DISTINCT from the exact next action, INT-102; last completed) · dependencies (EVERY unresolved owner question repo-wide, each with its authoritative home — long-term repo memory, INT-101) · evidence (label + ONE direct PR/session-record pointer per claim, INT-103) · coordination (PR/review snapshot at last repository update, never live status, INT-104). Never a second Intent Ledger, plan, or architecture copy. A snapshot that points at authority and never becomes one — on any disagreement the canonical document wins (D-024). Refreshed at every session exit; a stale STATE.md is a drift finding. `make state` will generate it from run records when it exists (Model 2+, OPERATING-MODEL §9).
- **Evidence labels (the five)** — the precision taxonomy for every verification claim (D-027, GLOSSARY home): **verified by run** (a named command or CI job, its result, one evidence reference) · **observed live** (an actual external action or API response, with the link to the evidence) · **behaviorally tested** (a defined scenario passed, test record available) · **proposed** (not yet adopted or approved) · **not checked** (explicitly not verified — never implied to be false or complete). "Verified" alone is never an acceptable label.
- **Meaningful session** — any session that (event-typed, never time/token-based, INT-106): changes repository state · produces a material finding or verified result · captures an owner decision in an external system · records a failure disposition · changes a task status or next action. Appends a compact WORKLOG entry (100–250 words: task, outcome, evidence, pointer, unresolved items, next action). Routine reading with no new finding or decision needs no entry. Home: OPERATING-MODEL §3.
- **Substantial work** — any of (event-typed, INT-106): an implementation slice · a meaningful multi-step investigation · a review with findings · a verification campaign · a material architecture decision · a failure investigation · coordinated multi-agent work. Produces a numbered session record (context/extracted/, standardized fields). Home: OPERATING-MODEL §3.
- **Selective intent verification** — the read-path rule (D-027(3)/INT-107): the Intent Ledger is the ONLY intent authority, but an agent verifies the entries RELEVANT to its task and any consequential change — never blanket boot reading. Supersedes the ledger-first boot requirement (owner turn 10); reconciled canonically in AGENTS read order, EXECUTION §2, OPERATING-MODEL §7. Home: EXECUTION §2.
- **Read manifest** — the cold-start proof's observable scope measure (D-027(4)): every file the test agent opened, with approximate word counts and the total. Baseline first; the read-scope budget is set from the measured baseline. Home: `context/TEMPLATES.md` §4 + OPERATING-MODEL §9 (the cold-start resumption test).
- **Pattern layer (the replication kit)** — the portable half of this system, as distinct from Arivo's content: the mechanisms (entry map · intent ledger · decision register · STATE index · session memory · verifier + walls · proofs) and their contracts, instantiable in any project. INT-108: nothing in the system's mechanics may hardcode this repo as the only possible home; the seam rule is the kit's own acceptance criterion. Forms: `context/TEMPLATES.md`; instantiation steps: `context/REPLICATION-GUIDE.md` (D-027(5)). A copy is proven only when its own cold-start proof passes — files existing is not replication.
- **Review artifact** — an agent-authored review, analysis, or protocol-proposal document under `context/reviews/`, banner-marked review-only. Lands on a branch via PR; merges only with the owner's explicit authorization; accepted rules fold into their canonical home — never a parallel authority (D-024).
- **Change channel** — the rule separating memory deltas (owner words, decisions, ledgers, worklog, plan, session records — land by PR under the standing P-13/P-15 authorization, owner reviews at gates) from analysis/review/proposal artifacts (PR + explicit per-merge owner authorization, D-024). The workflow, not prose, enforces it: `main` is protected.
- **Failure Record** — `failures/FAIL-NNN.yaml`: a failure, its class and severity, evidence, cause, the constraint added, and its known-bad proof (RAT-01/02 as executed 2026-10-13, FAIL-001). A failure with no record and no guard is scheduled to repeat.
- **Source-coverage manifest** — `context/SOURCE-COVERAGE-MANIFEST.md` (D-025, F-09): the coverage map and immutability anchor for `context/raw/` — per-file classification (owner voice / AI analysis / third-party / pasted doc), owner-voice→INT mapping, SHA-256 anchors (raw immutability at C3), and the exception (E-*) and exclusion (X-*) registers. Backs verifier checks VER-801..804, including mechanical quote fidelity: a ledger quote that does not trace to its cited raw source FAILS the layer. A control, never an intent authority.
- **Isolation check** — `tools/isolation_check.py` (W-03, LAW-28, D-025): the redacted secret-exposure scan — conditions printed, values never. Checks git remote URLs, secret-named environment variables, secret value patterns in tracked files, and `.env` tracking; carries its own known-bad self-test. Exit 1 = unexpected exposure = repair first.
- **Remote CI / required check** — `.github/workflows/verify.yml` (W-04, D-009, D-025): the `verify` workflow — the `canonical-layer` job runs the verifier anchored from `main` over the PR head (a PR cannot weaken its own judge); `canonical-layer` is required to merge into `main` (the check-run name the `verify` workflow reports) (W-01 stage-2). Local runs are preflight; the remote run is authoritative.

## Doctrine (from the transcripts and upstream — full text in /ENGINEERING.md)
- **Trust ladder** — the escape from 1:1 babysitting via verification, not confidence. Trust continuum strongest-first: codebase → static analysis → rules/skills → style guide (human-only, the big hole).
- **Five memory systems** — a repo is an executable memory system: intent, structural, verification, operational, evolutionary. They must agree; the objective is to minimize the distance between what the system should do, what the code does, and what the agent can establish about that difference.
- **Authoritative home** — the single file where a fact lives. Every duplicated fact creates a synchronization obligation.
- **Constraint ladder (C1–C6)** — type system → database → lint/architecture → executable test → gate/CI → document. Choose the highest level that works (LAD-01); repeated mistakes move up (LAD-03).
- **Design D (restricted capability)** — components that don't need a capability never receive it; the accidental access path does not exist. "Do not ask an agent to remember a property that the architecture can enforce."
- **Proof-carrying change** — every meaningful change carries an evidence package: intended behavior, reproduction, what changed, independent observation that it works.
- **Test execution vs test validity** — satisfying the assertions vs the assertions expressing the correct requirements. The shared-misunderstanding trap; oracles must be independent.
- **Oracle** — the independent authority a test's assertions are checked against: product contract, reference implementation, known example, mutation test, external observation.
- **Protect the verifier** — agents must not weaken tests, gates, suppressions, or acceptance criteria; "the system can gradually learn to look correct without becoming more correct."
- **Diagnostics contract** — every check failure prints: rule ID, violation + location, invariant protected, repair path, contract reference (WHAT/FIX/REF + WHY). An error is an instruction to the next reasoning step.
- **Gardener** — the standing role that nips anti-patterns before they propagate; keep the codebase in a state you would be happy to have an agent copy — because it will.
- **Repo GC** — recurring maintenance that scans the drift classes and submits narrow, verifiable cleanup changes; the baseline only moves up.
- **Harness regression suite** — representative engineering tasks that test the engineering environment itself: did our latest change make the repo easier or harder for agents to modify correctly?
- **Growth stages** — first layer → reliable foundation → legible system → enforced architecture → evidence-driven changes → self-maintaining → self-improving harness. Progress on observed failures, not calendar. Each stage's operating model is specified in /OPERATING-MODEL.md §6.
- **Locality** — a change's footprint: how many modules a typical change touches. Growing footprint = coupling evidence = architectural investigation.
- **One-shot** — a fresh agent with AGENTS.md + a card passes the gate on cycle 1 with zero owner edits. Two in a row end the foundation.
- **Anti-pattern virus** — agents copy every pattern present; one innocent workaround becomes the de facto pattern for all agents within days.

## Language
- Canonical language: English. Tailored, technical, easy to understand, machine-readable, optimized for agents, clean.
- Every rule/decision/fact carries a stable ID; every check failure carries a reason code.
- **ASD-STE100** (issue 9, Jan 2025) — controlled language standard for technical documentation. Status: EXPERIMENT — A/B measured before any enforcement strictness decision.
