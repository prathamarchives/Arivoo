# context/ — temporary memory seed

Purpose: the owner directed (2026-10-13, D-006): "Make a temporary folder for context in the repo and drop all this lore into that. Your memory problem would be solved." All context and lore accumulated before the build start lives here, so any fresh agent or model cold-starts from the repository alone.

Status: TEMPORARY. At playbook Step 2 / slice F-01 this material is restructured into the designed memory: `archive/owner-words/` (convos labeled OWNER:/AI:), `archive/ai-docs/` (design docs, including stale ones), `INTENT-LEDGER.yaml`, `DECISIONS.yaml`, `NORTH-STAR.md`, `GLOSSARY.yaml`, `FACTS.yaml`, `constraints/register.yaml`, `docs/agent/EXECUTION.md`. Nothing is deleted in that migration — it is reorganized and labeled.

## Structure

- `raw/` — the verbatim corpus as received from the owner (six files: convos 0/1/2, engineering transcript, upstream of engineering transcripts, Arivo Agent Execution Specification). NEVER edit these (AUT-02/04). The owner-facing build playbook is intentionally excluded per INT-034 (tension T-4, surfaced to the owner; it lives outside the agent repo).
- `extracted/` — structured briefs produced from the corpus:
  - `00-PRINCIPLES.md` — laws P-01..P-14, locked decisions D-001..D-006
  - `01-ENGINEERING-DOCTRINE.md` — engineering transcript + upstream, distilled
  - `02-OWNER-VOICE-AND-EVOLUTION.md` — owner words, pivot points, the goal in the owner's terms
  - `03-ARIVO-CURRENT-STATE.md` — the two Arivoo docs distilled (29 laws, constraint ladder, kernel K1-K10, slices F-00..F-09, the owner's 13 steps)
  - `04-OPERATING-MODEL.md` — the orchestrator's morals, beliefs, and approach loop
  - `05-OPEN-QUESTIONS.md` — open questions, each with a default
  - `06-REASONING-LOG.md` — append-only one-by-one reasoning sessions
  - `07-ON-THE-LIST.md` — confirmed-but-deferred capabilities (cloud sync, semantic search + retrieval, pgvector, vector search)
- `WORKLOG.md` — the agent coordination log, append-only (Task IDs)

## Canonical

The ROOT canonical files created 2026-10-13 as the repo's first layer GOVERN where they overlap with these briefs: `/NORTH-STAR.md`, `/INTENT-LEDGER.md`, `/DECISIONS.md`, `/PRINCIPLES.md`, `/ENGINEERING.md` (the doctrine, from transcript + upstream), `/LAWS.md` (the 29 laws, constraint ladder, phase mapping), `/GLOSSARY.md`, `/OPERATING-MODEL.md` (roles, slice loop, growth models, memory update protocol, self-healing, verification), `/PLAN.md`, `/AGENTS.md`. The briefs in `extracted/` are point-in-time process artifacts (extraction and reasoning history) — `00-PRINCIPLES.md` is already marked superseded (by root `/PRINCIPLES.md`); `01-ENGINEERING-DOCTRINE.md` is superseded by root `/ENGINEERING.md`; `03-ARIVO-CURRENT-STATE.md`'s law content is superseded by root `/LAWS.md`; the rest remain valid history until the canonical EXECUTION.md rewrite folds their deltas (see `08-RECONCILIATION-BRIEF.md`). The cold-start read order is defined in `/AGENTS.md`.
