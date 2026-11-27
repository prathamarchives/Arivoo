# 91 — ACCEPTANCE (the §6 campaign — the Workstream 11 backend half)

> STATUS: SESSION ENGINEERING RECORD (2026-11-27; intent refs: INT-162/173; D refs: D-042). Historical process artifact per D-022. Worklog: Task 128. PR #148.

## §1 What landed

harness/tests/test_acceptance_campaign.py — the directive's §6 final-verification
campaign as ONE integrated suite over the LANDED surface (the local rig + the REAL
ASGI app + the durable worker + both MCP transports):
- §6.1(2)-(14) the lifecycle: the import (the server-side digest verified against the
  bytes), the durable worker's extraction (the job machine's own path), the reading
  checkpoint + resume, the highlight/bookmark, the note create+revise, the journal
  block, the reading-list membership + the reference resolution, the search + the
  provenance-carrying context pack, the restart-and-reread (the durable store), the
  export manifest, the purge (the note 404s forever + the ledger row records the erasure).
- §6.2: the no-oracle cross-owner 404, the duplicate idempotency-key convergence (the
  SAME result_ref), the malformed-token 401.
- §6.4: both MCP transports expose the SAME registry (the stdio import = the HTTP serve).

## §2 Verification

- RED at the pre-102 tree (a17f0b5e, a worktree): 6 failures — ACC-03/04/12/13/14/18
  (the worker/export/purge/MCP surfaces absent there).
- GREEN at the head: ACC-01..18 all PASS.

## §3 Not verified (LAW-04)

- §6.1(1) the real Supabase test user; §6.4's Cloudflare-proxy legs (the deployed
  halves — the Q18 gate + the database credential pending).
- The reader-repository inspection + the thin contract client's UI legs (the canonical
  link never provided).
- The desktop offline/outbox behavior (Q19 — the owner's local-store choice).
- The storage fault-injection over a real object store (the WS8 gate).
