# 08 — Reconciliation Brief (owner turn 3.txt: verdict review + directives + vision)

> STATUS: HISTORICAL process artifact (marked 2026-10-13, canonicalization slice). Its 12 spec deltas are FOLDED into the root layer or explicitly OWNER-GATED (Q1–Q3) — see `/PLAN.md` supersession note and `/EXECUTION.md` provenance. Nothing waits on a further agent-side rewrite. It does not outrank the root documents.

Source: context/raw/3.txt (verbatim, 2026-10-13)
Status: REASONED — each review item carries a disposition: ADOPTED / REGISTERED / OWNER-OPEN. Owner words from the vision narrative are LOCKED intent.

## What 3.txt contains
1. A session protocol directive (continuous commit) → P-15.
2. An engineering review of the execution package (owner-presented; 11 sections, one governing principle, 3 owner questions) → dispositions R-01..R-11 below.
3. A directive to reason through and make the first layer of the repo (rules, principles, intent, aligned goal, operating model) → executed same day (root canonical files).
4. Doctrine quotes (self-verifying agents, codebase-as-memory, slop = missing constraints, the loop) → confirm 01-ENGINEERING-DOCTRINE.md; no deltas.
5. The owner's raw vision narrative ("my real words about what I want from Ivo") → INTENT-LEDGER INT-035+; NORTH-STAR quotes.

## The governing principle (owner-endorsed)
"Build a small, real slice of Arivo. Verify it independently. Refine it until it matches the intended behavior. Turn the lessons into constraints. Repeat."
"The harness and repository memory make this loop safer. They must not become reasons to postpone the product." → codified as P-17.

## Orchestrator's position on the verdict
ENDORSED in full, with one sharpening observation: the review is the doctrine's own ratchet applied to the plan. The upstream explicitly said "Start small: one complete reliable path... Don't build a giant framework first" and the first three assets are product contract → golden path → one verify command. The F-00..F-07 infrastructure-first drift contradicted the doctrine it cited. The correction is drift removal, not compromise. Evidence: the upstream's "first day" list (product contract, one vertical slice, verify from clean env) is exactly the review's proposed phase order.

## Review dispositions

**R-01 — locked decisions table (§1)** → DECISIONS.md D-007..D-014 (status: PRESENTED-LOCKED).
- "Other" host is not a host → Q1.
- Calculation engine: NG-05 default REMOVED; question open, non-blocking for capture; revisit at math workflow design (equation display/extraction vs numerical calculation vs symbolic algebra vs arbitrary code execution).

**R-02 — phase order mismatch (§2)** → ADOPTED (D-016). First real behavior moves forward; initial harness shrinks to the proactive guardrails; system and constraints grow together.
- Kept from day one (proactive set): isolated credentials · protected gates · real database test · idempotent writes · immutable evidence · owner scoping · independent state read.
- NOT required before product code: complete constraint system, all custom architecture checks, every kernel primitive, every planned known-bad. Each lands when it protects a concrete contract.
- First usable workflow = several small slices (reader-capture-journal milestone), not one enormous slice, not deferred.

**R-03 — complete data path (§3)** → ADOPTED (schema v0+ requirements, PLAN phases 3-4): Work/Source split; highlight stable identity + committed text + source anchor; bookmark durable location; notes + journal blocks with committed revisions; stable @ references (not text that looks like one); reading-session events + coarse position/dwell; local capture durability + cloud sync; provenance surviving re-parsing/renaming/re-indexing.
- Two outboxes ADOPTED (D-018): client outbox (offline durability, replays when cloud available) ≠ server outbox (post-commit enrichment). Different problems, separate designs.
- Durability ladder ADOPTED (D-017): local-durable → server-durable → keyword-searchable → semantically indexed → linked. Safety claims never exceed the current rung; "nothing is lost" becomes testable across crashes and outages.

**R-04 — semantic enrichment sequencing (§4)** → ADOPTED + LOCKED BY OWNER WORDS (D-015, P-16). "Meaning-based search comes later" + archived enrichment layers was incompatible with the locked architecture. Resolution: first capture slices need no calibrated autonomous belief system; the architecture provides for semantic indexing, vector retrieval, relationship processing, concept formation; the sequence reaches them through small tested slices; Kev decisions + belief promotion get policy and evaluation gates. "That is incremental implementation, not deferral."
- Compounding probes evolve, tested separately: deterministic (alias/explicit relation makes old highlight retrievable) → semantic (new related work resurfaces saved material) → graph (automatic relations add value without violating evidence rules).

**R-05 — purge contract (§5)** → ADOPTED (D-011 expanded): ordinary delete = tombstone (hidden from normal retrieval, recoverable); owner-only deliberate purge (runtime agents cannot invoke); purge removes content + derived material (embeddings, decisions, edge evidence, candidate records, unreferenced blobs); minimal audit record per retention policy; restores apply the purge ledger before availability. OPEN: backup policy → Q2.

**R-06 — behavior scope (§6)** → ADOPTED (D-010): canonical scope = explicit actions + source/session activity + coarse reading-position/dwell checkpoints. NO raw keystrokes/mouse traces. NO search-query or agent-prompt history (the playbook's additions are NOT canonical). Spec to define event vocabulary, cadence, retention, export; journal text ≠ inferred behavior.
- SECURITY FIX REGISTERED (owner-side, playbook Step 0): `env` inspection can leak secrets into logs → replace with a redacted isolation check that verifies conditions without printing values.

**R-07 — agent-authored layer (§7)** → ADOPTED (D-019): durable agent annotations/links/concept proposals; attributed; retrievable; ZERO belief weight; evidence for inferred relations still comes only from grounded text-pair decisions or structural facts. API/MCP surface: scoped reads, attributed writes, idempotency, bounded responses, stable error codes; one command registry behind reader/CLI/agent adapters.

**R-08 — intent and terminology (§8)** → ADOPTED: active Intent Ledger + Decision Records govern implementation; the archive preserves provenance/history; superseded designs explicitly marked (never competing instructions). fact-tag meaning → Q3 (OWNER). understanding.yaml requirement becomes "zero unclassified or unresolved BLOCKING unknowns"; documented defaults and non-blocking questions may stay open.

**R-09 — harness and language (§9)** → ADOPTED: local verify helps the builder; owner-controlled remote CI is authoritative; agent never holds the signing key or weakens checks. Host compatibility VERIFIED, not assumed: Codex CLI documents AGENTS.md auto-load; Claude Code documents CLAUDE.md with @path imports; host bridges are reasonable — verify on installed versions (FACT entries, phase 1). CI: restrict the required status check to the expected source application where available (verify mechanism + FACT entry at walls time; not assumed from docs). ASD-STE100 issue 9 (Jan 2025) = current official issue; controlled language standard, not proof every sentence rule improves agent code; keep the A/B experiment, let measurement decide enforcement strictness.

**R-10 — execution pass (§10)** → ADOPTED (PLAN.md): reconcile the canonical specification FIRST (no slice cards yet); then the 5-phase sequence: trust env → minimum harness → durable capture → reader+journal → retrieval+compounding. One phase deep; the next phase is planned when current-phase evidence says what's needed.

**R-11 — owner questions (§11)** → staged as Q1 (host: "Other" + primary builder; review rec: one primary + cross-family verifier), Q2 (purge backups: review rec: live + active removal, backup expiry, purge ledger on restore; per-owner encryption + key destruction only if physical erasure required), Q3 (fact tag: reading 1 "intended factual, verification recorded separately" vs reading 2 "verified true"; review rec: reading 1; original owner wording points to reading 2 → owner decides).

## Spec deltas for the canonical EXECUTION.md rewrite (NEXT reasoning pass, after Q1-Q3)
1. NG-05 removed (calculation engine open).
2. understanding.yaml wording: zero unresolved blocking unknowns.
3. Archive authority: ledgers govern; archive = provenance (superseded marks).
4. fact-tag definition per Q3 answer.
5. Behavior event vocabulary per D-010 (no search/agent-query history).
6. Purge contract per R-05 + Q2 answer.
7. Slice order per D-016 / PLAN.md (F-band superseded by the phase sequence; the slice cycle itself unchanged).
8. Enrichment layers: "archived / not in foundation" → "sequenced increments" (D-015).
9. Language standards: STE A/B experiment status recorded.
10. Host contract + bridges per Q1 answer.
11. Schema v0+ expands to the minimum durable model (R-03).
12. Two outboxes + durability ladder in the architecture section.
