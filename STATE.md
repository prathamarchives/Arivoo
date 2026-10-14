# STATE — Current-State and Navigation Index

> **STATUS: navigation snapshot — NOT authority.** This file tells an incoming agent where things stand and what to do next. It holds pointers and current status only, never a second copy of any rule (one fact, one home: `/EXECUTION.md` §1). If this file disagrees with a canonical document, the canonical document wins and this file must be corrected in the same session (authority order: `/EXECUTION.md` §3). **Contract (D-027, INT-109/105): one screen, pointers not detail — never a second Intent Ledger, a second plan, or an architecture copy; repo-scale long-term memory, not short-term session memory (INT-101).** The PR/review section is a **snapshot at the last repository update, not live status** — a committed file cannot guarantee external state hasn't changed since (INT-104). Updated at every session exit (AGENTS.md session-exit rule); a stale record pointer is a drift finding — VER-804 checks it mechanically.

## Where things stand

- **Phase:** **PHASE 1 — layer 1.2 in execution** (owner turn 10: after slices 1–3, the next layer is slices 4–6 — the STATE index, session handoffs, read path, replication; INT-100). Phase-1 exit criteria remain OBSERVED (2026-10-14, D-026); Model 1 (Trust Environment) active; all four walls live; 91 statused intents. **Phase 2 (product build) is NOT started — it begins only with the owner-approved execution plan; each layer is planned as it executes (INT-100).**
- **Active task:** session 14 — layer 1.2, in the owner's order: Slice 4 (STATE contract — this PR) → Slice 5 (session handoffs) → Slice 6 (read path + cold-start proof) → replication kit → close. Record: `context/extracted/14-NAVIGATION-HANDOFFS-READ-PATH.md` (in progress; PRs #10–#15 planned).
- **Last completed:** session 13 — the three slices (authority map, decision states, change discipline), all proofs PASS, Phase-1 exit observed. Record: `context/extracted/13-AUTHORITY-DECISIONS-CHANGE-DISCIPLINE.md`.
- **Exact next action:** land slice 5 (session-record policy + templates, PR #11) after this PR merges, then slice 6 in two steps (gate re-target PR #12, then the read path + cold-start proof PR #13) — per record 14 §1's bounded-slice order. (Active task = what this session is doing; exact next action = the deterministic continuation at the current point. INT-102: they are different lines by design.)
- **Blocking open questions — EVERY unresolved owner question, repo-wide (INT-101: STATE mirrors the whole register, never just the current phase):**
  - Q1 remainder — primary builder host + "Other" host. Blocks ONLY per-host bridge instantiation (adoption-time) — never a wall or a phase (INT-097, D-026). Home: DECISIONS Q1.
  - Q2 — purge vs backups (D-011). Blocks only the Phase 3 storage/purge schema lock. Home: DECISIONS Q2.
  - Q3 — fact-tag meaning. Blocks only the fact-tag vocabulary freeze (custom tags unaffected). Home: DECISIONS Q3.
  - QD-1 — first import formats. Blocks only the Phase 4 import slice design. Home: EXECUTION §6.
  - D-014 — calculation engine. Non-blocking for capture. Home: DECISIONS D-014 / EXECUTION §6.
  - F-06 — deployment precision. Blocks only the deployment-precision statement. Home: EXECUTION §6.
  - Q-IDENT — single-identity merge boundary. Blocks nothing under default (a). Home: DECISIONS Q-IDENT.
- **Outstanding reviews (snapshot at last repository update — NOT live status, INT-104):** none pending as of 2026-10-14 pre-session (0 open PRs, observed via API; evidence: record 14 §2). All prior review findings fully dispositioned (F-01..F-11 repaired or gated; F-08 second half by stage; F-10 rides to Phase 5).
- **Verification state — each claim carries its label AND one direct evidence pointer (INT-103; labels: GLOSSARY "Evidence labels"):**
  - **verified by run:** `python3 tools/verify_canonical_layer.py` 46/0 + `--self-test` 20/20 + `tools/isolation_check.py` green on `main` @ `e8a8259` — evidence: record 14 §2 (this session's preflight runs, exit 0 each); remote CI run `38514278918` green.
  - **observed live:** branch protection (PR-only, `canonical-layer` required + strict, admins included, 0 approving reviews) — evidence: record 13 §5.2 (API JSON) + record 14 §2 (re-observed 2026-10-14); direct-push rejection + broken-PR merge-block 405 — evidence: record 13 §5.2 (probe PR #7, red run `115684453018`).
  - **behaviorally tested:** authority-conflict + unresolved-decision proofs (uncoached fresh-context GLM sub-agents, both PASS) — evidence: record 13 §6.
  - **proposed:** the layer-1.2 corpus itself (STATE contract, session-record policy, read path, replication kit) — D-027 in this session's PRs; each element becomes standing as its PR merges.
  - **not checked:** per-host file-import bridges (land at host adoption with FACT entries); the PR template's first live use (this session's PRs #10–#15, closing a record-13 "not verified" item); the cold-start read-scope baseline (measured at the slice-6 proof, record 14).

## How to use this file

Read it second per the `/AGENTS.md` read order. Then follow the exact next action above, or the active task's record pointer. Do not treat any claim here as evidence: follow the linked session record, run the commands, and trust runs over recollection (P-02, LAW-01's spirit).
