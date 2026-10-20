# 24 — THE REVIEW SWEEP: the turn-23 late intake, the review-complete-before-merge standing rule, and the bot-finding disposition

> STATUS: SESSION ENGINEERING RECORD (2026-10-20, session 24; the session's intent refs: INT-128 — the late-minted turn-23 standing instruction, honest notation below; INT-129/D-042 — owner turn 24, the review-sweep directive; D refs: D-025/D-026/D-036/D-038/D-041 as cited). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 32. PRs this session: #59 onward (each carries a reasoned review BEFORE merge per D-042).

## §1 — the owner's turn, verbatim

> alll these prs, must have review comments, review them, reason throuhg and fix em... and from now on do not merge a pr without the reviews complete. few reviews are already there few are pending coderabbit/greptile now go do the work

(End of owner turn 24 verbatim. No access credential travelled with this turn; nothing redacted. The turn was transcribed through the session context — the standing byte-level-diff limit applies and is stated per INT-092's precedent.)

**Turn 23, the late intake (INT-128), preserved verbatim at record 23 §1 (committed at PR #58's merge, before this entry — the INT-046/068 class holds for the preservation itself; the MINT is late and that lateness is recorded here honestly):**

> continue as a world class systems enigneer don't stop until phase 4 is done with almost 50+ rounds of verification and iterations

(The session-23 header rationalized this as "no new owner question" and worked seven slices under it without a ledger entry — Greptile's PR #58 finding caught the gap: AGENTS.md's "owner intent enters ONLY through statused ledger entries" makes no new-question exception. The mint is repaired this session; the defect and its catch are recorded in §8.)

## §2 — the observed starting state (session-24 preflight, 2026-10-20)

- live truth re-established first: origin/main == local == `963356b` (the session-23 close), 0 open PRs, clean tree; the stored credential re-verified (never echoed)
- the environment reset had broken the postgres rig again (data-dir permissions corrupted by the reset, `pg_notify` missing) — rebuilt fresh from the exact FACT-001 Debian 17.11-0+deb13u1 packages, port 5433; 3 migrations applied, checksums match; the full preflight green at `963356b`: `make verify` GREEN (13/13 known-bads + gate selfcheck), canonical 51/0, selftest 30/30, isolation GREEN, isolation selftest green
- **the review-coverage audit (the turn's first question — "all these prs, must have review comments"):** all 58 merged PRs enumerated with their review state via the GitHub API —
  - reviewed: #1/#2/#4/#5/#8 (Codex + owner), #35–#38 (Codex), #46–#48 (CodeRabbit + Greptile), #49 (CodeRabbit), #50–#54/#56–#58 (Greptile) — 27 PRs
  - NO review at all: #3, #6, #7, #9–#34, #39–#45, #55 — **31 PRs** (pre-registry doc-era slices mostly, plus the session-20/21 stretch and PR #55 where Greptile skipped)
  - bot coverage pattern (the turn's "few reviews are already there few are pending"): CodeRabbit reviewed #46–#49 then stopped; Greptile reviewed #46–#54/#56–#58, skipping #49 and #55 — neither bot guarantees coverage; per D-042 a host review is the floor, never the bot's arrival
- **the 42 bot findings re-verified at HEAD** (every CodeRabbit/Greptile inline comment on #46–#58 read in full, then verified against the live tree before any edit — CR-48-1/G-48-1/CR-48-4 anchored-name: fixed at `3469b06`+`87ab16b`; G-53-1 env-call: fixed at `7d86557`; G-53-2 unittest-blind: fixed at `a78a947`; CR-48-2's red.py overwrite guard: fixed in-tree; G-50-1's STATE overstatement: superseded by #58's re-derivation): **24 live defects + 2 reasoned no-fixes + the rest already-fixed/stale** — the full disposition table is §5's work product, landed slice by slice

## §3 — the task and scope

- the turn's three jobs: (1) every PR must carry review comments — the 31-review gap closes with honest host reviews (verification of each merged PR's claims against its merge-time tree, findings posted, no rubber stamps); (2) the 42 bot findings reasoned through and the live ones FIXED with stable regressions; (3) the standing rule recorded and enforced as far as the environment honestly permits: **no PR merges without a completed review** (D-042)
- bounded scope: five repair slices (record-evidence; mutation-floor hardening; isolation-tool hardening; gate/scope/known-bad/workflow) + the review sweep itself + this intake; every finding routed to its named slice with its disposition — no finding auto-closed, none dismissed by nominal severity
- non-scope: Q6–Q12/D-014 untouched; no new dependency; no CI-provider change; the one-liner consistency slice and H-01c-authority remain the queued roadmap work after the sweep
- routing (the D-041 pattern — findings to named cards, R-01..R-05 in PLAN): R-01 record-evidence repairs (the record 22 §8 gap + CRLF byte-fidelity + red-records evidence + claim-013/014 annotations + STATE stale phase + CLAIMS duplicate row); R-02 the mutation-floor hardening (walk onerror; process-group kill + RLIMIT_NPROC; truncated/signal-rc rejection; final integrity recheck; manifest-write failure RED; post-read budget charge; manifest type checks; the .git worktree file; test_10's remaining vacuous window); R-03 the isolation-tool hardening (O_NONBLOCK; walk onerror; directory budgets; B5/B6 message assertions); R-04 the gate/scope/known-bad/workflow repairs (the stderr-only stub; S4c `!cancelled`; failure-output capture; scope.py tab/bytes/rename fixes; both KB probes' self-containment + the closed-table-duplicate ratchet); R-05 the review sweep (the 31 host reviews + the disposition replies + the coverage table)
