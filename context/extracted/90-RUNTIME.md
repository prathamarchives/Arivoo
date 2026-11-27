# 90 — RUNTIME (the deployment substrate's pre-gate half — the Workstream 10 slice)

> STATUS: SESSION ENGINEERING RECORD (2026-11-27; intent refs: INT-162/172; D refs: D-042/D-032). Historical process artifact per D-022. Worklog: Task 127. PR #147.

## §1 What landed (runtime-neutral; the Q18 gate UNTOUCHED)

1. **The measured compatibility report + the Q18 decision request** (context/runtime-decision-request-2026-11-27.md): the three Cloudflare options compared (the generic container behind a Tunnel — RECOMMENDED; the Containers beta; native Workers — incompatible with the subprocess worker); the live verification (the CF token reaches the zone + the account + the tunnels; `arivo.itscatalyst.com` unclaimed; the Supabase PAT a dead placeholder).
2. **Dockerfile** — the reproducible image: python:3.12-slim, the locked requirements, the pg client, the non-root user, the HEALTHCHECK; the three start commands (`api` / `worker` / `migrate`).
3. **harness/api/__main__.py** — the `api` start command: the fail-closed secret matrix (ARV-SVC-001 names the missing variable — verified live, exit 1), uvicorn on :8080, the auth contract from the environment.
4. **The secret matrix** (harness/api/env.example.txt): every variable, its consumer, its class; the §6.4 verify-full law for the remote.
5. **The runbook §17** (append-only): the release order (migrate -> api -> worker, the readiness gate between), the tunnel front, the verification list.

## §2 Verification (the image's CONTENT contracts — no docker in this sandbox, disclosed)

- the fresh-venv pip install of the locked requirements (7 pins) — exit 0;
- the api start command in that venv: /health/live 200 {"status":"live"}, /health/ready 200,
  POST /mcp unauth 401 (the transport law), /api/v1/me 401 (the auth law), clean shutdown;
- the fail-closed refusal: ARV-SVC-001 names the variable, exit 1;
- the release oracle: the 22 migrations apply on a fresh db (through 0022_durable_jobs).

## §3 Not verified (LAW-04)

- the five PR-head checks + the D-042 review; the Q18 OWNER GATE (the runtime selection);
- the production database credential (the Supabase PAT is a dead placeholder);
- the docker BUILD itself (no docker in the sandbox — the content contracts verified instead);
- the deployed surface (the tunnel/DNS/TLS/CORS/rate-limits — all post-gate).
