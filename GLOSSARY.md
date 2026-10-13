# GLOSSARY — Arivo

Controlled vocabulary. One concept, one name — no synonyms. Terms used in ledgers, laws, cards, and code must come from here. New terms enter by append; renames supersede by reference.

## Identity
- **Arivo** — the product: the owner's reading/study/reflection environment. (The owner also says "Ivo" casually; Arivo is canonical per D-002.)
- **Arivoo** — this repository.
- **Owner** — prathamarchives. The only authority on intent; words recorded verbatim.
- **Orchestrator** — the coordinating agent (Super Z lineage): holds corpus understanding, enforces laws, gates artifacts, runs the ratchet, commits.
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
- **Fact tag / Concept / Quote** — the v1 capture tag vocabulary. **fact meaning: OPEN (Q3)** — (a) intended-factual with separately recorded verification status, vs (b) system-verified true. **Concept** — a growing entity that links to works and carries provenance. **Quote** — creative/writing the owner liked.

## Substrate
- **Ground truth** — append-only evidence (highlights, revisions, behavior events, tag events). Edit = new revision; delete = tombstone.
- **Derived** — rebuildable interpretation; every derived row carries provenance (run ID, versions, input hash). Deletable and rebuildable with zero loss.
- **Tombstone** — ordinary delete: hidden from normal retrieval, recoverable.
- **Purge** — owner-only deliberate erasure of content + derived material (embeddings, decisions, edge evidence, candidate records, unreferenced blobs); minimal audit record; restore applies the purge ledger. Runtime agents cannot invoke.
- **Client outbox** — on-device durability queue; preserves new work offline and replays to the cloud when available.
- **Server outbox** — post-commit job scheduler for enrichment. A different problem from the client outbox.
- **Durability ladder** — `local-durable → server-durable → keyword-searchable → semantically indexed → linked`. Safety claims never exceed the current rung.
- **The List** — confirmed-but-deferred capabilities with reopening triggers (`context/extracted/07-ON-THE-LIST.md`).

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

## Language
- Canonical language: English. Tailored, technical, easy to understand, machine-readable, optimized for agents, clean.
- Every rule/decision/fact carries a stable ID; every check failure carries a reason code.
- **ASD-STE100** (issue 9, Jan 2025) — controlled language standard for technical documentation. Status: EXPERIMENT — A/B measured before any enforcement strictness decision.
