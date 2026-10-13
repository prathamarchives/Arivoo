# AGENTS.md — Arivoo (product: Arivo) — v2.1

You are an agent in this repository. This file is your map. Read it fully, then follow the read order. Host bridges (e.g. CLAUDE.md) import this file; this file remains canonical.

## What this is
- **Arivo**: the owner's reading/study/reflection environment — backend only (base, foundation, mechanism; no UI/UX). Repo: **Arivoo**. Owner: prathamarchives.
- Phase: **FIRST LAYER CANONICALIZED (v2.1)** — memory, doctrine, law book, decisions, plan, operating models, and the execution contract's one canonical home (`/EXECUTION.md`) live at the repo root. Next: owner answers Q1–Q3, then Phase 1 (walls, host bridges, isolation check, CI).
- Operating mode: the orchestrator runs, the owner reviews (P-13). Commit protocol: every delta lands as a commit and a push (P-15).

## Read order (cold start)
1. `/INTENT-LEDGER.md` — owner words, verbatim, statused. The highest authority. Load it BEFORE forming any understanding of the task.
2. `/NORTH-STAR.md` — the goal in the owner's words; claims C1–C5; the seven-layer contract
3. `/PRINCIPLES.md` — the owner's laws P-01..P-17 (each with mechanism, failure mode, growth)
4. `/LAWS.md` — the executable law book: the 29 laws, ladder C1–C6, phase mapping
5. `/ENGINEERING.md` — the doctrine: why the laws are what they are (transcripts + upstream)
6. `/DECISIONS.md` — statused decisions D-001..D-023 + open Q1–Q3
7. `/EXECUTION.md` — the execution contract's one canonical home: the contract map, the source tiers, the authority order, the change protocol
8. `/PLAN.md` — one phase deep; guardrails; Phase 1 detail
9. `/GLOSSARY.md` — controlled vocabulary (use these exact names)
10. `/OPERATING-MODEL.md` — roles, the slice loop, the growth models (6 stages), the memory update protocol, self-healing, verification
11. `context/WORKLOG.md` (tail) — what has been done, in order
12. `context/extracted/` — historical briefs (banner-marked; 07 = the live register); `context/raw/` — the verbatim mixed corpus, never edit

## Binding rules
- The repo is the memory. Chat history is not (P-02). Every reasoning delta → file → commit → push (P-15).
- Owner intent enters ONLY through INTENT-LEDGER entries (verbatim, statused). `context/raw/` is the verbatim corpus as received from the owner — mixed owner statements, AI analysis, and pasted documents. Never edit it; never treat a raw sentence as owner intent by itself (source tiers: `/EXECUTION.md` §2).
- Ledgers and logs are append-only: supersede by referencing; never rewrite history. One fact, one home; every duplicated fact creates a synchronization obligation.
- A law is a constraint WITH a check (LAWS.md). No product code, dependencies, or CI until the owner approves the execution plan. Documents (memory, laws, plan) are the authorized first layer.
- Do not weaken constraints, thresholds, or checks. The verifier is protected. Do not touch gates/workflows once walls are live.
- Owner words verbatim, typos preserved; interpretations always labeled. Contradictions: name both, Question Record, authority order (`/EXECUTION.md` §3) — never average, never silently choose.
- Slice cards and context packs carry their INT- IDs and the owner quotes (LOOP-05: a requirement with no intent behind it fails the audit).
- The owner-facing build playbook is intentionally NOT in this repo (INT-034). Do not add it.
- Isolation/secrets checks print conditions, never values. No `env` dumps.
- Language: English. Tailored, technical, machine-readable, clean. Stable IDs; reason codes on failures; one fact, one home.
- Layer check: `python3 tools/verify_canonical_layer.py` — the canonicalization conditions on the real files; green means the layer is coherent.

## Vocabulary
See `/GLOSSARY.md`. Core: Arivo (product) · Arivoo (repo) · Owner · Orchestrator · Builder/Verifier · Host/Host Contract/Host Bridge · Work/Source/Highlight/Anchor/Bookmark/Note/Journal block/@-reference · Fact tag (meaning OPEN, Q3) · Concept · Quote · Ground truth/Derived · Tombstone/Purge · Client outbox/Server outbox · Durability ladder · The List (refinement-debt register) · Slice/Card/Proof Sheet/Gate/Ratchet/Known-bad/Walls · Proactive set · Kev · Constraint ladder C1–C6 · Five memory systems · Growth stages · Authoritative home · Source tiers · Authority order · Proof-carrying change · Diagnostics contract · Gardener/Repo GC · One-shot.
