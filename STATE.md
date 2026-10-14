# STATE — Current-State and Navigation Index

> **STATUS: navigation snapshot — NOT authority.** This file tells an incoming agent where things stand and what to do next. It holds pointers and current status only, never a second copy of any rule (one fact, one home: `/EXECUTION.md` §1). If this file disagrees with a canonical document, the canonical document wins and this file must be corrected in the same session (authority order: `/EXECUTION.md` §3). Updated at every session exit (AGENTS.md session-exit rule); a stale STATE.md is a drift finding — VER-804 checks it mechanically.

## Where things stand

- **Phase:** **PHASE 1 COMPLETE — exit observed 2026-10-14 (D-026); Model 1 (Trust Environment) active.** All four Phase-1 walls live: W-01 (protected `main`: PR-only, no force push, admins included, `canonical-layer` required + strict), W-02 (host-agnostic since D-026: Host Contract + bridge pattern; Q1's remainder gates per-host instantiation only, never the wall), W-03 (isolation check), W-04 (remote CI, authoritative). 81 statused intents. **Next: Phase 2 — the minimum trustworthy harness (P-17-scoped).**
- **Active task:** none open mid-session. (When a slice is open, this line names its card, scope, and cycle count.)
- **Exact next action:** Phase 2 planning — the minimum trustworthy harness slice per PLAN Phase 2 (one real-stack test, Proof Sheets from run records, scope enforcement, representative known-bads for the proactive set only). No open question blocks it (Q1 re-scoped to instantiation-only, INT-097/D-026). The owner may answer the compact Decision Review in the session-13 record §8 (Q1 remainder — non-blocking; F-06; Q-IDENT) whenever convenient.
- **Last completed:** session 13 — `context/extracted/13-AUTHORITY-DECISIONS-CHANGE-DISCIPLINE.md` (the three-slices session: INT-093..099 + P-18 + D-026; four decision states; W-02 host-agnostic → Phase-1 exit observed; bounded-diff change rules + PR template; MUT-17 genericized; the two behavioral proofs and two live path proofs, all PASS).
- **Blocking open questions (each blocks ONLY its dependent work):**
  - Q1 remainder — primary builder host + "Other" host. Blocks only per-host bridge instantiation (adoption-time) — never a wall or a phase (INT-097, D-026).
  - Q2 — purge vs backups (D-011). Blocks only the Phase 3 storage/purge schema lock.
  - Q3 — fact-tag meaning (re-scoped by INT-069). Blocks only the fact-tag vocabulary freeze; custom tags are unaffected.
  - D-014 — calculation engine. Non-blocking for capture.
  - F-06 — deployment precision. Blocks only the deployment-precision statement — nothing current.
  - Q-IDENT — single-identity merge boundary. Blocks nothing under the default (documented acceptance).
- **Outstanding reviews:** none pending. All prior review findings fully dispositioned (F-01..F-11 repaired or gated; F-08 second half by stage; F-10 rides to Phase 5; F-12 held by claim-scoped verification state below).
- **Verification state (never trust prose over runs):**
  - **verified (run):** `python3 tools/verify_canonical_layer.py` GREEN on this tree — 46 checks, 0 failures; `--self-test` 20/20 known-bad mutations caught (MUT-17 now content-generic); `tools/isolation_check.py` GREEN (conditions-only, remote de-credentialed).
  - **verified (observed, this session):** direct push to `main` REJECTED by protection (route 1); a deliberately broken PR REJECTED — `canonical-layer` red via VER-802 naming the tampered file, merge API 405 "Required status check failing" (route 2, probe PR #7, closed unmerged); PR #6's CI green both jobs; protection config observed via API (0 required approvals — Q-IDENT-compatible).
  - **verified (behavioral, fresh-context sub-agents):** authority-conflict test PASS (identifies EXECUTION §3 / D-020; rejects averaging AND last-read-wins); unresolved-decision test PASS (four states + homes; refuses recommendation/presence/elapsed-time as approval).
  - **not verified:** per-host file-import bridges (land at host adoption with FACT entries); the real one-shot coding test (impossible until product code exists — F-08 second half, by stage); the PR template's first live use (the next session's PRs).

## How to use this file

Read it second — after `/AGENTS.md` step 1 loads the owner words (`/INTENT-LEDGER.md`) and before the rest of the read order. Then follow the exact next action above, or the active task's card. Do not treat any claim here as evidence: follow the linked session record, run the commands, and trust runs over recollection (P-02, LAW-01's spirit).
