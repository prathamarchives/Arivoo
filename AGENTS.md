# AGENTS.md — Arivoo (product: Arivo) — v1

You are an agent in this repository. This file is your map. Read it fully, then follow the read order. Host bridges (e.g. CLAUDE.md) import this file; this file remains canonical.

## What this is
- **Arivo**: the owner's reading/study/reflection environment — backend only (base, foundation, mechanism; no UI/UX). Repo: **Arivoo**. Owner: prathamarchives.
- Phase: **FIRST LAYER COMPLETE** — canonical memory, laws, decisions, plan, and operating model live at the repo root. Next: owner answers Q1-Q3, canonical execution spec is reconciled, then Phase 1 (walls, host bridges, isolation check, CI).
- Operating mode: the orchestrator runs, the owner reviews (P-13). Commit protocol: every delta lands as a commit and a push (P-15).

## Read order (cold start)
1. `/NORTH-STAR.md` — the goal, in the owner's words
2. `/PRINCIPLES.md` — the laws P-01..P-17
3. `/DECISIONS.md` — statused decisions D-001..D-019 + open Q1-Q3
4. `/PLAN.md` — one phase deep; guardrails; Phase 1 detail
5. `/GLOSSARY.md` — controlled vocabulary (use these exact names)
6. `/OPERATING-MODEL.md` — roles, the slice loop, morals, commit protocol
7. `context/WORKLOG.md` (tail) — what has been done, in order
8. `context/extracted/` — process briefs (doctrine, owner voice, reconciliation); `context/raw/` — verbatim corpus, never edit

## Binding rules
- The repo is the memory. Chat history is not (P-02). Every reasoning delta → file → commit → push (P-15).
- `context/raw/` is verbatim owner material: never edit, never reformat.
- Ledgers and logs are append-only: supersede by referencing; never rewrite history.
- No product code, dependencies, or CI until the owner approves the execution plan. Documents (memory, laws, plan) are the authorized first layer.
- Do not weaken constraints, thresholds, or checks. The verifier is protected. Do not touch gates/workflows once walls are live.
- Owner words verbatim, typos preserved; interpretations always labeled.
- The owner-facing build playbook is intentionally NOT in this repo (INT-034). Do not add it.
- Isolation/secrets checks print conditions, never values. No `env` dumps.
- Language: English. Tailored, technical, machine-readable, clean. Stable IDs; reason codes on failures; one fact, one home.

## Vocabulary
See `/GLOSSARY.md`. Core: Arivo (product) · Arivoo (repo) · Owner · Orchestrator · Builder/Verifier · Host/Host Contract/Host Bridge · Work/Source/Highlight/Anchor/Bookmark/Note/Journal block/@-reference · Fact tag (meaning OPEN, Q3) · Concept · Quote · Ground truth/Derived · Tombstone/Purge · Client outbox/Server outbox · Durability ladder · The List · Slice/Card/Proof Sheet/Gate/Ratchet/Known-bad/Walls · Proactive set · Kev.
