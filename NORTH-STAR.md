# NORTH-STAR — Arivo

The goal, in the owner's words (verbatim, 2026-10-13, `context/raw/3.txt`). Everything in this repo traces here. Authority: owner words (INTENT-LEDGER) > this file > LAWS > ENGINEERING > PRINCIPLES > DECISIONS > PLAN > agent judgment.

## Mission

> "imagine I open my laptop, PC system, or whatever, and I'm reading a book. I'm researching, studying, and everything. I open Arivo... and I import my stuff. It's organized and I share the articles, the research papers, maybe some writings, or some people from social media or other platforms, Reddit and stuff, books of course, and every readable thing, maybe a manga. It's just like a book."

> "Suppose I'm reading books and I have lists, a library, and lists of what I'm currently reading... I highlight sentences and tag them: Is it a fact or a concept? If it is neither, it should be a quote or some writing I like, with some creativity. I take notes, not as brief as shit, but notes with my raw thinking. I reason through it."

> "I want to document my raw thinking while studying what I'm learning, feed that back into my behavior on that specific page, and document that so it compounds. That's valuable: my learning compounds and that's valuable. I can visit it, recognize it, and remember it any day."

> "The goal is like a journal. Suppose it's a reading day, I'm studying, and at the end of the day I just write a page: how was my experience and what I have learned. There I can reference these. I can also reference things while reading... I can reference a specific passage that I remember, or reference the article to the book, or the book to the article."

> "Notes: I want notes not to be short but something in depth that shows me, translates me, and shows me raw. It's not just a set of text notes, but diagrams."

> "Specifically for AI, I can just connect an agent and it has all the context of me."

> "Keep working at it until we have a foundation, a mechanism, and a backend that support our goal and align with it."

## Claims (the promise Arivo makes)
- **C1** Nothing the owner does is lost. Worst failure: losing a highlight.
- **C2** The owner's agents have the owner's context.
- **C3** Old inputs gain value from new inputs.
- **C4** Concepts form with provenance, from tags.
- **C5** Every derived claim is explainable and reversible.

## First usable workflow (D-013)
Read a source → capture highlights/bookmarks → add a note → journal, referencing material with `@`. The complete reader-capture-journal path is the first usable milestone, built from several small slices (never one enormous slice, never deferred). The durability ladder makes C1 testable: `local-durable → server-durable → keyword-searchable → semantically indexed → linked`.

## The seven layers (the substrate contract)

Each layer carries a must-be-true contract — this is how the goal decomposes into checkable structure. Layers 1–3 are the build's center of gravity (Phases 2–3); layer 6 is the product surface; layers 4–5 arrive with retrieval and compounding (Phase 5) through the evidence rules.

| # | Layer | Must be true |
|---|-------|--------------|
| 1 | Ground truth | Evidence, behavior, and agent contributions are immutable and attributed; recovery limits stated honestly |
| 2 | Ingestion | Any readable file becomes work, version, and passages atomically, deduped by work; a bookmark is just a position you return to |
| 3 | Memory index | Keyword immediately, semantic later, all rebuildable |
| 4 | Structure | Evidence means decisions on text pairs or structural facts; everything else is discovery |
| 5 | Concept formation | Provisional concepts mint from independent sources and graduate on out-of-sample evidence |
| 6 | Agent surface | One API core, MCP as an adapter, scoped tokens, context packs, untrusted-content marking |
| 7 | Retrieval | Hybrid, why-payloads, temporal and behavioral queries, response budgets that fit an agent's context window |

**The compounding probe ladder (how C3 is tested, separately per strength):** deterministic probe (a known alias or explicit relationship makes an old highlight retrievable) → semantic probe (a new related work causes saved material to resurface through semantic retrieval) → graph probe (automatic relationship creation adds useful connections without violating the evidence rules). Progressively stronger claims, tested separately — never bundled into one "it compounds" assertion.

## Architecture commitments (P-16)
Semantic indexing, vector retrieval, relationship processing, and concept formation are core capabilities of the architecture, reached through small tested slices in the active sequence — never deferred as architecture, never a "version 2" bolt-on. The backend must evolve cleanly into future versions: agent-native, VR/3D/hardware.

> "I don't want it to be like, 'Okay let's ship version 1 and version 2 can come later (like semantic search, vector search, those cases).' No I don't want to compromise that."

## Non-goals (this build)
- No UI/UX design (owner's separate work; the backend serves it).
- No review queue — no stage waits for the owner (NG-01).
- Agents never touch the database — API/MCP only (NG-02).
- No generative model in Arivo's pipeline (NG-03).
- No detailed plan beyond the next active phase (NG-04).
- Calculation engine: OPEN — not a non-goal, undecided; revisit at math workflow design (D-014).
