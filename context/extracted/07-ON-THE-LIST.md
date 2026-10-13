# 07 — On The List (confirmed, deferred capabilities)

The owner's list: capabilities confirmed as NEEDED but not built yet. Per P-07 (No-Later), "later" is never an answer — each entry carries its reopening trigger. Nothing on this list may be silently dropped; removal requires an owner decision.

---

## L-001 — Cloud sync
- Confirmed: owner, 2026-10-13 — "Yes I know I need cloud and sync"
- Need: the environment eventually syncs to cloud (deployment shape decided at the ops band via spike + FACT, per stack defaults)
- Design constraint NOW: nothing in the foundation may preclude cloud sync (append-only ground truth + provenance keeps sync principled)
- Trigger: foundation exit reached, or owner pulls it earlier

## L-002 — Semantic search and retrieval
- Confirmed: owner, 2026-10-13 — "I need synthetic search and retrieval" (verbatim; INTERPRETED as SEMANTIC search — interpretation labeled per AUT-04; correctable by the owner)
- Need: retrieval over the owner's corpus by meaning, not just keyword
- Foundation answer: keyword search first (spec architecture point 10); semantic is a later band
- Trigger: keyword search proven + captured volume makes retrieval the bottleneck; owner pull anytime

## L-003 — pgvector
- Confirmed: owner, 2026-10-13 — "PG vector" (and earlier same day: "postrgres with pg vector")
- Need: vector storage inside Postgres; the data layer is Postgres + pgvector (D-003)
- Plan: extension installed at F-04 (PROP-2 — substrate cheap-early, machinery later); vector columns/schema at the semantic band
- Trigger: L-002 activates

## L-004 — Vector search
- Confirmed: owner, 2026-10-13 — "vector search"
- Need: embedding-based search over highlights/notes/journal; the Embedder is a kernel port (K2) — reserved from day one, implemented at its band
- Trigger: L-002 activates
