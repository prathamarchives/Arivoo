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
| CLAIM-003 | 19 (part 2) | Super Z (GLM host) | `slice/claim-003-session-19-close` | `context/extracted/19-PHASE3-ENTRY-AND-SYSTEMS-ENGINEERING-EXECUTION.md`, `STATE.md`, `context/WORKLOG.md`, `CLAIMS.md`, `harness/known-bad/`, `harness/runs/claim-003-session-19-close/` | — (no new owner turn) | 2026-10-19 | The close slice: record 19 completed (the true two-part account — including the record-side rebase incident repair), STATE exit, WORKLOG Task 19, the registry's own closes. |

## Closed claims

| Claim | Result | Closed | Evidence |
|-------|--------|--------|----------|
| CLAIM-001 | The concurrency protocol landed (PR #36, `9a63579` — CLAIMS.md + AGENTS + LAWS LAW-31 + GLOSSARY + OPERATING-MODEL + EXECUTION) | 2026-10-19 | PR #36 = `9a63579`, post-merge run `39238984928` success |
| CLAIM-002 | The enforcement machinery landed (PR #37, `04eae39` — ARV-CLM-001..005, five known-bads 13/13 in CI, the gate wiring; LAW-31 LIVE) | 2026-10-19 | PR #37 = `04eae39`, run `39239243662` all checks success |

Pre-registry history (PRs #1–#35, sessions 1–19 part 1) is NOT backfilled as claims; the registry governs work from this adoption onward (D-038). Session 19's two-part collision is the founding incident, preserved verbatim in record 19 §8 — the rules above are its ratchet response (LAW-18).
