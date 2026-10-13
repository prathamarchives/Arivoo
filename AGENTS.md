# AGENTS.md — Arivoo (product: Arivo) — v0

You are an agent working in this repository. This file is your map. Read it fully, then follow the read order. This is v0 — it will be superseded by the F-00 AGENTS.md (Appendix A format) when the build starts.

## What this is
- Arivo: a personal reading / study / reflection environment (reading, research study, writing, practice). Backend only: base, foundation, real mechanism. No UI/UX (P-01).
- Owner: prathamarchives. Operating mode: the orchestrator runs, the owner reviews (P-13).
- Current phase: PRE-BUILD. Context memory seeded 2026-10-13 (first commit). No product code exists yet.

## Read order (cold start)
1. `context/README.md` — what the context folder is
2. `context/extracted/00-PRINCIPLES.md` — the laws that bind all work here (P-01..P-14, decisions D-001..D-006)
3. `context/extracted/03-ARIVO-CURRENT-STATE.md` — the full design: goal, 29 laws, kernel K1-K10, slices F-00..F-09, owner's 13 steps
4. `context/extracted/06-REASONING-LOG.md` (tail) — latest reasoning, decisions, open proposals
5. `context/WORKLOG.md` (tail) — what has been done, in order
6. `context/extracted/05-OPEN-QUESTIONS.md` and `context/extracted/07-ON-THE-LIST.md` — open questions; confirmed-but-deferred capabilities
- Source material, verbatim, never edit: `context/raw/`

## Binding rules right now
- Nothing is memory unless it is on disk in this repo. Chat history is not memory (P-02).
- `context/raw/` is the verbatim owner corpus: never edit, never reformat (AUT-02/04).
- Ledgers and logs are append-only: correct by appending; supersede by referencing; never rewrite history.
- Do not write product code, dependencies, or CI until the owner approves the execution plan (plan mode for code; the memory seed of 2026-10-13 was the explicitly authorized piece, D-006).
- Do not weaken constraints, thresholds, or checks. The verifier is protected (LAW-09).
- Owner words are quoted verbatim, typos preserved. Interpretations are always labeled as interpretations.
- The owner-facing build playbook is intentionally NOT in this repo (INT-034, tension T-4). Do not add it.
- Communication language: English only.

## Vocabulary
- Arivo = the product. Arivoo = this repository. Owner = prathamarchives.
- Orchestrator = the coordinating agent (Super Z lineage); holds corpus understanding, gates every artifact.
- Builder / verifier = fresh-context subagents; self-contained slice cards, never whole chat history; a builder never verifies its own work.
- The List = confirmed-but-deferred capabilities (cloud sync, semantic search + retrieval, pgvector, vector search) — see `context/extracted/07-ON-THE-LIST.md`.
