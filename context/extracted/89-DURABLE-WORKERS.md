# 89 — DURABLE-WORKERS (the job machine + the worker loop — the Workstream 9 slice)

> STATUS: SESSION ENGINEERING RECORD (2026-11-27; the session's intent refs: INT-162/171; D refs: D-042). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 126. PRs this session: #146 (this slice).

## §1 What landed

1. **MIGRATION 0022** — the durable job machine (runbook §12.1's column set exact):
   arv.job (id/owner/job_type/payload_version/payload/idem_key/state/attempts/available_after/
   lease_owner/lease_expires_at/fencing_token/last_error/timestamps; the closed type vocabulary —
   extract_source, rebuild_keyword_index, recovery_walk, rebuild_derived; the dedupe
   UNIQUE(owner, type, idem_key); RLS owner-scoped); arv.job_claim (SELECT ... FOR UPDATE
   SKIP LOCKED over the due rows — queued/retryable due OR the expired lease; the lease +
   the MONOTONIC fencing token granted in the same statement; SECURITY DEFINER per the 0019
   precedent); arv.job_complete (the FENCED completion: WHERE id + lease_owner + fencing_token
   AND state='leased' — a stale worker's write matches ZERO rows and observes 'lost', never a
   double-complete; the closed outcome vocabulary; the 30s*attempts backoff); the poison guard
   (retryable at attempts>=8 goes dead — the terminal class; one poison job never blocks the queue).
2. **harness/worker.py** — the private worker loop: claim -> the SAME kernel arms through the
   bounded subprocess (extract.py / commands.py / recover.py — never a second domain model) ->
   the fenced completion. The bounded payload law (owner-scoped references only, §12.3); the
   idempotent same-key re-run on timeout (the honest unknown); the ARV-CMD-409 dead class
   (the same key a different body never converges — terminal); the code-only logging (§12.4).
3. **The WS8 storage decision request** riding this slice (context/storage-decision-request-2026-11-27.md):
   the ONE consolidated owner gate — R2 RECOMMENDED (zero egress, the S3 API, the landed
   crash-matrix evidence); Supabase Storage fully supported by the neutral boundary; the
   ratification is the owner's; it blocks ONLY the provider-specific adapter slice.

## §2 Verification

- **RED observed** at the suite-only commit 88a1b5c (exit 1, 9 failures — the machine absent).
- **GREEN** at the head: WRK-01..10 (the §12.2 laws: the SKIP LOCKED claim + the token;
  the stale-token and stale-worker 'lost' answers; the expired-lease reclaim with the token
  increment; the dedupe convergence; the poison-guard dead through the trigger's own path;
  the unblocked queue; the END-TO-END loop — claim -> the SAME extract arm -> the fenced
  completion -> the extraction generation created).

## §3 Not verified (LAW-04)

- the five PR-head checks + the D-042 review; the deployed surface (WS10); the persistent
  polling form under a supervisor (the --once batch proven; the deployment is WS10's slice);
  the remote 0021/0022 application (the Supabase credential); the provider adapter (the WS8 gate).
