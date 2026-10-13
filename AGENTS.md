# AGENTS.md — Arivoo (product: Arivo) — v2.3

You are an agent in this repository. This file is your map. Read it fully, then follow the read order. Host bridges (e.g. CLAUDE.md) will import this file when written (Phase 1, W-02 — verified on installed hosts, never assumed); this file remains canonical.

## What this is
- **Arivo**: the owner's reading/study/reflection environment — backend only (base, foundation, mechanism; no UI/UX). Repo: **Arivoo**. Owner: prathamarchives.
- Phase: **FIRST LAYER CANONICALIZED + STRESS-TESTED + WALLS STAGE-1 (v2.3)** — memory, doctrine, law book, decisions, plan, operating models, the execution contract's one canonical home (`/EXECUTION.md`), and the current-state index (`/STATE.md`) live at the repo root; 73 statused intents; the review-merge session (session 11) merged PRs #1/#2, folded the review protocol canonical (D-024), and landed protected `main`. Next: owner go/no-go on Phase 1 (Q1 remainder blocks only W-02; Q2/Q3 ride to their named gates).
- Operating mode: the orchestrator runs, the owner reviews (P-13). Commit protocol: memory deltas land as a commit and a push (P-15); analysis/review/proposal artifacts land by PR, merged only with the owner's explicit authorization (D-024).

## Read order (cold start)
1. `/INTENT-LEDGER.md` — owner words, verbatim, statused. The highest authority. Load it BEFORE forming any understanding of the task.
2. `/STATE.md` — where things stand NOW: current phase, active task, exact next action, blocking open questions, verification state. A navigation snapshot, NOT authority — on any disagreement the canonical document wins.
3. `/NORTH-STAR.md` — the goal in the owner's words; claims C1–C5; the seven-layer contract
4. `/PRINCIPLES.md` — the owner's laws P-01..P-17 (each with mechanism, failure mode, growth)
5. `/LAWS.md` — the executable law book: the 29 laws, ladder C1–C6, phase mapping
6. `/ENGINEERING.md` — the doctrine: why the laws are what they are (transcripts + upstream)
7. `/DECISIONS.md` — statused decisions D-001..D-024 + open Q1–Q3
8. `/EXECUTION.md` — the execution contract's one canonical home: the contract map, the source tiers, the authority order, the change protocol
9. `/PLAN.md` — one phase deep; guardrails; Phase 1 detail
10. `/GLOSSARY.md` — controlled vocabulary (use these exact names)
11. `/OPERATING-MODEL.md` — roles, the slice loop, the growth models (6 stages), the memory update protocol, self-healing, verification
12. `context/WORKLOG.md` (tail — last 3–5 entries) — what just happened, what's open
13. Reference tier — task-scoped, never boot material: `context/extracted/` historical briefs and numbered session engineering records (banner-marked; 07 = the live register), `context/reviews/` review-only artifacts, and `context/raw/` — the verbatim mixed corpus, never edit. Read raw files only when a task requires it (quote verification, intent backfill); owner intent is NOT taken from raw (source tiers: `/EXECUTION.md` §2).

## Binding rules
- The repo is the memory. Chat history is not (P-02). Every reasoning delta → file → commit → push (P-15).
- **Change channel (D-024): findings are recorded; changes are applied only through reviewed branches.** Analysis, review, and proposal artifacts NEVER land on `main` directly — they arrive on a branch, through a pull request, and merge only with the owner's explicit authorization. Memory deltas (owner words, decisions, ledgers, worklog, plan, session records) continue to land per P-15. With walls stage-1 live, direct pushes to `main` are rejected by the host.
- Owner intent enters ONLY through INTENT-LEDGER entries (verbatim, statused). `context/raw/` is the verbatim corpus as received from the owner — mixed owner statements, AI analysis, and pasted documents. Never edit it; never treat a raw sentence as owner intent by itself (source tiers: `/EXECUTION.md` §2).
- Ledgers and logs are append-only: supersede by referencing; never rewrite history. One fact, one home; every duplicated fact creates a synchronization obligation.
- A law is a constraint WITH a check (LAWS.md). No product code, dependencies, or CI until the owner approves the execution plan. Documents (memory, laws, plan) are the authorized first layer.
- Do not weaken constraints, thresholds, or checks. The verifier is protected. Do not touch gates/workflows once walls are live.
- Owner words verbatim, typos preserved; interpretations always labeled. Contradictions: name both, Question Record, authority order (`/EXECUTION.md` §3) — never average, never silently choose.
- Slice cards and context packs carry their INT- IDs and the owner quotes (LOOP-05: a requirement with no intent behind it fails the audit).
- The owner-facing build playbook is intentionally NOT in this repo (INT-034). Do not add it.
- Isolation/secrets checks print conditions, never values. No `env` dumps.
- Language: English. Tailored, technical, machine-readable, clean. Stable IDs; reason codes on failures; one fact, one home.
- Test and verification loops run on GLM-based subagents; GLM is the host agent for verification/testing (INT-070).
- Session exit (every agent, every session): append your WORKLOG entry, update `/STATE.md` (current phase, active task, exact next action, verification state), commit every reasoning delta, push, and — if any root document changed — run `python3 tools/verify_canonical_layer.py` and land it green (P-15, INT-072, INT-074). EVERY meaningful session — not only root-document sessions — also leaves a numbered session engineering record in `context/extracted/` (INT-072, broadened per F-04: code, verification, investigation, and review sessions count too).
- Layer check: `python3 tools/verify_canonical_layer.py` — the canonicalization conditions on the real files; green means the layer is coherent.

## Vocabulary
See `/GLOSSARY.md`. Core: Arivo (product) · Arivoo (repo) · Owner · Orchestrator · Builder/Verifier · Host/Host Contract/Host Bridge · Work/Source/Highlight/Anchor/Bookmark/Note/Journal block/@-reference · Custom tag (owner-authored, no default classification — INT-069) · Fact tag (meaning OPEN, Q3 — only when the owner uses it) · Concept · Quote · Ground truth/Derived · Tombstone/Purge · Client outbox/Server outbox · Durability ladder · The List (refinement-debt register) · Slice/Card/Proof Sheet/Gate/Ratchet/Known-bad/Walls · Proactive set · Kev · Constraint ladder C1–C6 · Five memory systems · Growth stages · Authoritative home · Source tiers · Authority order · Proof-carrying change · Diagnostics contract · Gardener/Repo GC · One-shot · STATE.md (current-state index) · Review artifact · Change channel.
