# STATE — Current-State and Navigation Index

> **STATUS: navigation snapshot — NOT authority.** This file tells an incoming agent where things stand and what to do next. It holds pointers and current status only, never a second copy of any rule (one fact, one home: `/EXECUTION.md` §1). If this file disagrees with a canonical document, the canonical document wins and this file must be corrected in the same session (authority order: `/EXECUTION.md` §3). Updated at every session exit (AGENTS.md session-exit rule); a stale STATE.md is a drift finding.

## Where things stand

- **Phase:** Model 0 — first layer canonicalized + stress-tested, with **walls stage-1 live early** (protected `main`: PR-only, no force push, applies to admins; D-024, W-01 first stage). Full Phase 1 (W-02 host bridges, W-03 isolation check, W-04 CI) awaits the owner's explicit go.
- **Active task:** none open mid-session. (When a slice is open, this line names its card, scope, and cycle count.)
- **Exact next action:** the owner reviews the merged review set (PRs #1/#2, `context/reviews/`) and D-024, then says go/no-go on Phase 1. Defaultable independent work that may proceed meanwhile (blocking rules respected): the source-coverage manifest slice (stress-review F-09).
- **Last completed:** session 11 — `context/extracted/11-REVIEW-MERGE-AND-STATE-SLICE.md` (PRs #1/#2 reviewed + merged owner-authorized; review protocol folded canonical via D-024; STATE.md created; verifier extended with known-bad self-test; FAIL-001 recorded; `main` protected).
- **Blocking open questions (each blocks ONLY its dependent work):**
  - Q1 remainder — primary builder host + "Other" host. Blocks only W-02 host bridges.
  - Q2 — purge vs backups (D-011). Blocks only the Phase 3 storage/purge schema lock.
  - Q3 — fact-tag meaning (re-scoped by INT-069). Blocks only the fact-tag vocabulary freeze; custom tags are unaffected.
  - D-014 — calculation engine. Non-blocking for capture.
  - F-06 — cloud vs local-first vs cross-device-sync deployment precision (stress-review F-06). Owner ratification needed; blocks only the deployment-precision statement — nothing current.
  - Phase 1 go/no-go — the owner's explicit go for W-02..W-04. Blocks Phase 1 execution only.
- **Outstanding reviews:** none pending. Latest: `context/reviews/2026-10-13-goal-aligned-architecture-review.md` (merged via PR #2); its open findings F-06, F-08 (second half), F-09, F-10, F-11 are tracked in the session-11 record with owners and gates.
- **Verification state (never trust prose over runs):**
  - **verified (run):** `python3 tools/verify_canonical_layer.py` GREEN on this tree, including `--self-test` known-bad mutations caught (see session-11 record for the count).
  - **verified (observed):** branch protection on `main` rejects direct pushes (break-test executed in session 11).
  - **not verified:** no remote CI yet (W-04 pending); host bridges unwritten (W-02, blocked on Q1 remainder); the real one-shot coding test is impossible until product code exists (F-08 second half — by stage, not by omission).

## How to use this file

Read it second — after `/AGENTS.md` step 1 loads the owner words (`/INTENT-LEDGER.md`) and before the rest of the read order. Then follow the exact next action above, or the active task's card. Do not treat any claim here as evidence: follow the linked session record, run the commands, and trust runs over recollection (P-02, LAW-01's spirit).
