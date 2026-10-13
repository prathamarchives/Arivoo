# context/ — temporary memory seed

Purpose: the owner directed (2026-10-13, D-006): "Make a temporary folder for context in the repo and drop all this lore into that. Your memory problem would be solved." All context and lore accumulated before the build start lives here, so any fresh agent or model cold-starts from the repository alone.

Status: TEMPORARY. At the designed-memory migration (corpus closure, FX-07 / OPERATING-MODEL §7) this material is restructured into the designed memory: `archive/owner-words/` (convos labeled OWNER:/AI:), `archive/ai-docs/` (design docs, including stale ones), `INTENT-LEDGER.yaml`, `DECISIONS.yaml`, `NORTH-STAR.md`, `GLOSSARY.yaml`, `FACTS.yaml`, `constraints/register.yaml`, `docs/agent/EXECUTION.md`. Nothing is deleted in that migration — it is reorganized and labeled. (The F-band migration step of the original spec is superseded by the D-016 phase sequence; the migration's trigger is corpus closure, not a slice number.)

## Structure

- `raw/` — the verbatim corpus as received from the owner (**seven files**: convos `0.txt`, `1.txt`, `2.txt`, owner turn `3.txt`, `engineering transcript.txt`, `upstream of engineering transcripts.txt`, `Arivo Agent Execution Specification.md`). This is a **mixed archive**: owner statements, AI analysis and proposals, pasted documents and reviews — with material repeated across files. It is preserved exactly as received and NEVER edited (AUT-02); it is NOT owner-only intent (source tiers: `/EXECUTION.md` §2, D-022) — owner intent is extracted into `/INTENT-LEDGER.md` with status, never taken from raw directly. The owner-facing build playbook is intentionally excluded per INT-034 (tension T-4, surfaced to the owner; it lives outside the agent repo).
- `extracted/` — structured briefs produced from the corpus. **All are historical process artifacts** (banner-marked; they do not outrank the root canonical documents and their content must never be promoted into requirements — LOOP-05), with ONE exception:
  - `00-PRINCIPLES.md` — superseded by root `/PRINCIPLES.md`
  - `01-ENGINEERING-DOCTRINE.md` — superseded by root `/ENGINEERING.md`
  - `02-OWNER-VOICE-AND-EVOLUTION.md` — superseded by root `/INTENT-LEDGER.md` (the backfilled ledger is the traceable form; this brief remains the distilled reading history)
  - `03-ARIVO-CURRENT-STATE.md` — superseded by root `/LAWS.md` + `/PLAN.md`
  - `04-OPERATING-MODEL.md` — superseded by root `/OPERATING-MODEL.md`
  - `05-OPEN-QUESTIONS.md` — superseded by `/DECISIONS.md` open questions + `/EXECUTION.md` §6
  - `06-REASONING-LOG.md` — historical (append-only reasoning sessions; the record of owner words from the build sessions)
  - `07-ON-THE-LIST.md` — **ACTIVE: the refinement-debt register (D-020)** — the one live mechanism in this directory, referenced by P-07, DECISIONS, and PLAN
  - `08-RECONCILIATION-BRIEF.md` — historical (its 12 spec deltas are folded into the root layer or owner-gated; see `/PLAN.md` supersession note)
- `WORKLOG.md` — the agent coordination log, append-only (Task IDs)

## Canonical

The ROOT canonical files created 2026-10-13 and deepened/canonicalized since GOVERN where they overlap with these briefs: `/NORTH-STAR.md`, `/INTENT-LEDGER.md` (the only intent authority — backfilled with the corpus intents 2026-10-13), `/DECISIONS.md`, `/PRINCIPLES.md`, `/ENGINEERING.md` (the doctrine, from transcript + upstream), `/LAWS.md` (the 29 laws, constraint ladder, phase mapping), `/GLOSSARY.md`, `/OPERATING-MODEL.md` (roles, slice loop, growth models, memory update protocol, self-healing, verification), `/PLAN.md`, `/EXECUTION.md` (the execution contract's one canonical home), `/AGENTS.md`. The cold-start read order is defined in `/AGENTS.md`; the source tiers and authority order live in `/EXECUTION.md` §2–§3.
