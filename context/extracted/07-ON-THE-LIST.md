# 07 — The List: the refinement-debt register

> STATUS: **ACTIVE MECHANISM** (the one live file in `context/extracted/`) — the refinement-debt register referenced by P-07, D-020, GLOSSARY, and PLAN. Rewritten 2026-10-13 by the canonicalization slice (D-020); the original "confirmed-but-deferred capabilities" framing is superseded — its text is preserved below as history.

**What the register is (D-020).** Implementation slices sequenced out of the active order, each with a reopening trigger — the mechanical replacement for "later" (P-07). **What it is NOT:** a parking lot for capabilities. A capability confirmed by owner words never leaves the active sequence, and architecture-level commitments (P-16: semantic indexing, vector retrieval, relationship processing, concept formation) can never enter the register at all. The register shrinks as items enter the sequence; it never becomes a graveyard. Removal of an entry requires an owner decision.

---

## Live entries

### L-001 — Cross-device sync (the live register entry)
- Confirmed: owner, 2026-10-13 — "Yes I know I need cloud and sync" (INT-053; recorded verbatim in `06-REASONING-LOG.md:113`)
- Decomposed by D-020 into three separate concerns, so this entry can no longer bundle them:
  - **Cloud-hosted backend** — ACTIVE (D-003, INT-052), not a register item
  - **Local durable capture** — ACTIVE substrate (client outbox, D-018; the durability ladder), not a register item
  - **Cross-device synchronization + conflict resolution** — active capability, sequenced; THIS is the register item
- Design constraint NOW: nothing in the foundation may preclude sync (append-only ground truth + provenance keeps sync principled)
- Trigger: foundation exit reached, or owner pulls it earlier

## Closed entries (kept as history — closed 2026-10-13, D-020)

### L-002 — Semantic search and retrieval — CLOSED: in the active sequence
- Confirmed: owner, 2026-10-13 — "I need synthetic search and retrieval" (INT-053, verbatim; INTERPRETED as SEMANTIC search — interpretation labeled per AUT-04, correctable by the owner)
- CLOSED because: semantic indexing + retrieval are core capabilities IN the active implementation sequence (D-015, INT-039, INT-054; PLAN Phase 5). Incremental implementation through small tested slices — keyword first on the durability ladder, semantic next, never deferred as architecture. This entry can never be reopened as a deferral; it would violate P-16.

### L-003 — pgvector — CLOSED: in the active sequence
- Confirmed: owner, 2026-10-13 — "PG vector" / "postrgres with pg vector" (INT-053, INT-065)
- CLOSED because: the data layer is Postgres + pgvector (D-003, LOCKED). Substrate reserved early (extension installed with the container), machinery at its band (PLAN Phase 5).

### L-004 — Vector search — CLOSED: in the active sequence
- Confirmed: owner, 2026-10-13 — "vector search" (INT-053)
- CLOSED because: embedding-based search is a core capability in the active sequence (D-015, P-16, PLAN Phase 5); the Embedder is a kernel port (K2) reserved from day one.

---

*History — the original framing (superseded 2026-10-13 by D-020): "The owner's list: capabilities confirmed as NEEDED but not built yet. Per P-07 (No-Later), 'later' is never an answer — each entry carries its reopening trigger. Nothing on this list may be silently dropped; removal requires an owner decision." The original entries L-001..L-004 carried deferral-style wording ("Foundation answer: keyword search first (spec architecture point 10); semantic is a later band") that conflicted with D-015/P-16; that conflict is what D-020 resolved.*
