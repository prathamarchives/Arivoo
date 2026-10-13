# PLAN — Arivo

One phase deep (NG-04). The next phase is planned only when current-phase evidence says what's needed. Predicates close phases, not dates. The slice cycle (OPERATING-MODEL) is the unit of execution inside every phase.

## Guardrails from day one (proactive set — never deferred)
Isolated credentials · protected gates · real database test · idempotent writes · immutable evidence · owner scoping · independent state read. Everything else arrives through the ratchet, when it protects a concrete contract. The harness must never postpone the product (P-17).

## Phase 1 — Execution environment and trust (NEXT)
Purpose: the repo is safe to build in, and the trust model is real.
- **W-01 Walls**: protect main (PR-only, no force push, applies to admins); CODEOWNERS on protected paths; required check restricted to the expected source application (mechanism verified + FACT entry — not assumed from docs). Two-stage: rules land now, required-check binding when CI runs.
- **W-02 Host contract + bridges**: verify on installed versions how Codex CLI loads `AGENTS.md` and how Claude Code loads `CLAUDE.md` (`@path` imports); write the canonical bridge(s); FACT entries for verified behavior. Depends on Q1 (primary host).
- **W-03 Isolation check**: redacted verification that the agent environment exposes no personal secrets — conditions printed, values never.
- **W-04 CI**: Linux runner, `verify` workflow, owner-controlled; remote CI is authoritative (D-009).
Exit: a broken build cannot merge; a fresh host session loads canonical instructions (verified); the sandbox is proven secret-free; verify runs green on a trivial truth; a deliberately broken build fails the gate.

## Phase 2 — Minimum trustworthy harness
One real-stack test · Proof Sheet generated from run records · scope enforcement · representative known-bads for the proactive set only. NOT required before product code: the full constraint system, all architecture checks, every kernel primitive, every planned known-bad.
Exit: the harness proves scope, evidence immutability, idempotency, and independent reads on a real database; deliberately broken builds fail with named codes.

## Phase 3 — Durable capture (first real behavior)
Schema v0+ per the minimum durable model (GLOSSARY): Work/Source split; highlight with stable identity + anchor + immutable revision; bookmark; note; owner scope + actor on every write; idempotent commands; client outbox; recovery. Server outbox wired for future enrichment.
Exit: capture survives kill -9, restart, replay, offline; keyword search finds it; fault trials lose zero; durability ladder holds to server-durable.

## Phase 4 — Reader and journal path (first usable milestone, D-013)
Open PDF/EPUB → highlight → bookmark → margin notes → durable journal blocks → stable `@` references. Each behavior gets its own small card and verified result.
Exit: the owner's day-one workflow (read → capture → note → journal with references) runs end-to-end, proven on the real stack.

## Phase 5 — Retrieval and compounding
Keyword lookup → agent reads (API/MCP surface per D-019) → semantic indexing + vector retrieval → relationship candidates → concept formation → Kev policy/eval gates. Compounding probes tested separately: deterministic → semantic → graph.
Exit: C3 demonstrable with reasons and provenance — new inputs resurface old material; automatic relations add value without violating evidence rules.

## Standing open (owner)
Q1 primary host + "Other" · Q2 purge-backup policy · Q3 fact-tag meaning. Calculation engine: open, non-blocking for capture. The List (cloud sync et al.) carries reopening triggers.

## Supersession note
The F-00..F-09 foundation-slice order from the original execution spec is SUPERSEDED by this phase sequence (D-016; reconciliation brief R-02/R-10). The slice cycle, size limits, proof discipline, and laws carry over unchanged into the new phases. The canonical EXECUTION.md rewrite (after Q1-Q3) folds the 12 spec deltas from `context/extracted/08-RECONCILIATION-BRIEF.md`.
