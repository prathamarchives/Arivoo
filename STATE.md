# STATE — Current-State and Navigation Index

> **STATUS: navigation snapshot — NOT authority.** This file tells an incoming agent where things stand and what to do next. It holds pointers and current status only, never a second copy of any rule (one fact, one home: `/EXECUTION.md` §1). If this file disagrees with a canonical document, the canonical document wins and this file must be corrected in the same session (authority order: `/EXECUTION.md` §3). Updated at every session exit (AGENTS.md session-exit rule); a stale STATE.md is a drift finding — VER-804 checks it mechanically.

## Where things stand

- **Phase:** Model 0 — first layer canonicalized + stress-tested, **walls stage-2 live** (protected `main` with PR-only/no-force-push/admin-included since stage-1, D-024; remote CI `verify` workflow + `verify / canonical-layer` required check + isolation check + source-coverage control since stage-2, D-025). Phase 1's remaining wall: W-02 host bridges — blocked ONLY on Q1's remainder (primary builder host + "Other" host). Then Phase 2 (minimum harness).
- **Active task:** none open mid-session. (When a slice is open, this line names its card, scope, and cycle count.)
- **Exact next action:** the owner answers the compact Decision Review in the session-12 record §8 — Q1 remainder (primary builder host + "Other": needed for W-02, the last Phase-1 wall), F-06 (one deployment-precision statement), Q-IDENT (accept documented single-identity boundary or create a bot identity). Defaultable meanwhile: none urgent — F-09 is DONE (this session); the next defaultable slice is Phase-2 preparation reading only if the owner defers W-02.
- **Last completed:** session 12 — `context/extracted/12-GAP-CLOSURE-AND-WALLS-STAGE-2.md` (gap closure + walls stage-2: source-coverage control with mechanical quote fidelity — 7 ledger defects found and repaired; CI live + required check bound; isolation check; drift analysis with dispositions; D-025, INT-092).
- **Blocking open questions (each blocks ONLY its dependent work):**
  - Q1 remainder — primary builder host + "Other" host. Blocks only W-02 host bridges (the last Phase-1 wall).
  - Q2 — purge vs backups (D-011). Blocks only the Phase 3 storage/purge schema lock.
  - Q3 — fact-tag meaning (re-scoped by INT-069). Blocks only the fact-tag vocabulary freeze; custom tags are unaffected.
  - D-014 — calculation engine. Non-blocking for capture.
  - F-06 — cloud vs local-first vs cross-device-sync deployment precision. Blocks only the deployment-precision statement — nothing current.
  - Q-IDENT — single-identity merge boundary (new, DECISIONS). Blocks nothing under the default (documented acceptance).
- **Outstanding reviews:** none pending. The stress review's findings are fully dispositioned: F-01..F-08 repaired (F-08 second half impossible until product code — by stage), F-09 DONE (this session), F-10 rides to Phase 5 (belief-policy simulator gate), F-11 noted in the manifest (E-3), F-12 held by claim-scoped verification state below.
- **Verification state (never trust prose over runs):**
  - **verified (run):** `python3 tools/verify_canonical_layer.py` GREEN on this tree — 46 checks, 0 failures (C1–C8 incl. mechanical quote fidelity of all 74 ledger entries); `--self-test` 20/20 known-bad mutations caught; `tools/isolation_check.py` GREEN (conditions-only) with its known-bad caught.
  - **verified (observed):** remote CI ran the `verify` workflow on the session-12 PR — both jobs green — and the `canonical-layer` check is bound as required on `main` (merge-blocking, strict, admin-included); branch protection rejects direct pushes (break-test, session 11).
  - **not verified:** host bridges unwritten (W-02, blocked on Q1 remainder); the real one-shot coding test is impossible until product code exists (F-08 second half — by stage, not by omission); quote fidelity covers E-2 chat-sourced turns only via session-record cross-checks, not raw (manifest §7).

## How to use this file

Read it second — after `/AGENTS.md` step 1 loads the owner words (`/INTENT-LEDGER.md`) and before the rest of the read order. Then follow the exact next action above, or the active task's card. Do not treat any claim here as evidence: follow the linked session record, run the commands, and trust runs over recollection (P-02, LAW-01's spirit).
