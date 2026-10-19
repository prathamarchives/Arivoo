# CLAIMS — the coordination registry (multi-agent concurrency; D-038/INT-124/LAW-31)

> **Append-only.** One row per claim. NEVER edit a closed row; supersede by pointer. The LIVE truth is the GitHub API (open PRs and branches); this file is the repo-side mirror (INT-104's class — re-observe at preflight, never trust the snapshot alone). A claim opens in the SAME PR that carries its first work commit — the registry row and the work land together through the walls. This registry exists because two agents collided on one branch in session 19 (record 19 §8); until the machinery slice (ARV-CLM-001..004) lands with its known-bads, enforcement is agent-discipline backed by the walls; after it lands, the gate checks this file mechanically on every PR.

## The rules (authoritative homes: AGENTS.md binding rules · LAWS.md LAW-31 · D-038)

1. **Claim-before-work.** No consequential change lands without an OPEN claim whose declared scope covers its diff. Trivial fixes and review comments are exempt; anything that changes a canonical file, a tool, the harness, or a record is consequential.
2. **Scope exclusivity.** Two OPEN claims MUST NOT overlap on any non-shared file — the second overlap is refused with a named code. Declare scope as file globs. The **shared-append class** (`INTENT-LEDGER.md`, `DECISIONS.md`, `context/WORKLOG.md`, `CLAIMS.md`, `STATE.md`, `context/SOURCE-COVERAGE-MANIFEST.md`, session records under their own IDs) is overlap-legal: every claim may touch these, but only append-shaped edits (the append-only law); STATE is re-derived at session exit, so its conflicts resolve by regeneration — it is a snapshot, never authority.
3. **INT reservation.** Ledger IDs are reserved ONE AT A TIME through registry rows: each reservation is exactly previous-max+1 (the Notes column records it). A merge-order race (two sessions reserving the same ID) is caught at the gate and the LATER claim amends pre-merge — unmerged rows are their author's own in-flight edits. No range reservations, no gaps.
4. **One claim, one branch, one PR.** The branch name carries the claim ID (`slice/<claim-id>-<slug>`). A PR without an OPEN claim row for its branch is refused. A claim whose PR merges CLOSES the claim (the closing agent appends the closed row in the same session's close work).
5. **Stale claims.** An OPEN claim whose PR has been idle for 7+ days is marked STALE by any agent (append a Notes entry, never edit the row); the original agent renews or releases it. Released claims release their reserved-but-unused INTs (a Notes line; the next claim takes previous-max+1 of the USED set — unused reservations never burn an ID).
6. **Honesty.** The Agent column states the real agent identity (host + model, or integration name). Two parts of one session may share a claim; both are named.

## Open claims


| Claim | Session | Agent | Branch | Scope (globs) | INTs reserved | Opened | Notes |
|-------|---------|-------|--------|----------------|---------------|---------|-------|
| CLAIM-006 | 20 | Super Z (GLM host) | `slice/claim-006-session-20-close` | `CLAIMS.md`, `STATE.md`, `context/WORKLOG.md`, `context/extracted/20-SYSTEMS-ENGINEERING-EXECUTION-DIRECTIVE-INTAKE.md`, `harness/runs/claim-006-session-20-close`, `harness/tests/test_gate_dispatch.py`, `harness/red-records.json` | — (close work: no new owner turn) | 2026-10-19 | The session-20 interim close: CLAIM-005's closed row; record 20 §4 (the A01/A02/A10 dispositions landed this session: reproduced RED-first, repaired, regression-proven in CI at run 39255875913, merged) + §8 (the session's honest failure/limit log); STATE's exact next action -> H-01b. The session may continue (H-01b next); this close is the registry/record honesty work, not a session end. The test/red-records scope carries the suite-stability repair the close's own CI exposed (scope widened honestly, the record-19 precedent). |

## Closed claims

| Claim | Result | Closed | Evidence |
|-------|--------|--------|----------|
| CLAIM-001 | The concurrency protocol landed (PR #36, `9a63579` — CLAIMS.md + AGENTS + LAWS LAW-31 + GLOSSARY + OPERATING-MODEL + EXECUTION) | 2026-10-19 | PR #36 = `9a63579`, post-merge run `39238984928` success |
| CLAIM-002 | The enforcement machinery landed (PR #37, `04eae39` — ARV-CLM-001..005, five known-bads 13/13 in CI, the gate wiring; LAW-31 LIVE) | 2026-10-19 | PR #37 = `04eae39`, run `39239243662` all checks success |
| CLAIM-003 | The session-19 close landed (PR #38, `026fead` — record 19 COMPLETE §§1–12, STATE exit, WORKLOG Task 19) | 2026-10-19 (late close appended 2026-10-19, session 20 — rule 4's closing append was missed by session 19 part 2; reconciled at session-20 preflight, noted in record 20 §2) | PR #38 = `026fead`, post-merge run `39240443928` success |
| CLAIM-004 | The session-20 intake landed (PR #39, `6cdd458` — owner turn 20 verbatim in record 20 §1, INT-125, D-039, the NG-04-exception outcome roadmap rows, the frozen H-01a ready card, CLAIM-003's late close) | 2026-10-19 | PR #39 = `6cdd458` (merge of `9c6841e`), post-merge run `39253982971` success; three checks green at the head (run `39253749733`) |
| CLAIM-005 | H-01a landed (PR #40, `746fa57` — the fail-closed dispatcher: A01's selfcheck fallback deleted, A02's interpolation replaced by env-passing + identifier validation, A10's git failures refuse with ARV-DIFF-001/002; the new suite RED-first at c7c1633, GREEN at the head; the real CI S4b step ran dispatch PR-mode green at the head — run 39255875913, all three checks) | 2026-10-19 (closed promptly, same session) | PR #40 = `746fa57` (merge of `54aae98`), post-merge run `39256240219` success; red-first evidence harness/runs/claim-005-h01a-pr-dispatch-git-fail-closed/red-01.txt |

Pre-registry history (PRs #1–#35, sessions 1–19 part 1) is NOT backfilled as claims; the registry governs work from this adoption onward (D-038). Session 19's two-part collision is the founding incident, preserved verbatim in record 19 §8 — the rules above are its ratchet response (LAW-18).
