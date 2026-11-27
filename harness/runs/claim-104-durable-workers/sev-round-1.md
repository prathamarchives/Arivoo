# SEV round-1 — slice claim-104-durable-workers (Workstream 9; INT-171)
- reviewer: inline verification (the WRK suite's live probes as the falsification floor)
- head: the bookkeeping commit; base: origin/main (the PR #145 merge)
- disposition: PASS — zero findings
| Probe | Observed |
|---|---|
| WRK-02 (the SKIP LOCKED claim + the token) | PASS |
| WRK-03/05 (the stale token/worker answers 'lost') | PASS |
| WRK-04 (the expired-lease reclaim, token increments) | PASS |
| WRK-06 (the rightful fenced completion) | PASS |
| WRK-07 (the dedupe convergence) | PASS |
| WRK-08 (the poison guard dead at the limit) | PASS |
| WRK-09 (the queue unblocked after the poison) | PASS |
| WRK-10 (the end-to-end loop: claim -> the SAME extract arm -> fence ok -> the generation) | PASS |
Not-verified: the five PR-head checks + the D-042 review; the deployed surface + the supervised polling form (WS10); the remote 0021/0022 application; the storage adapter (the WS8 gate).
