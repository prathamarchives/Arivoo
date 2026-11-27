# Arivo — the deployment runbook (Workstream 10; CLAIM-105/INT-172)

## §17 Deployment (the runtime-neutral container + the tunnel front)

1. **The image**: `docker build -t arivo:<sha> .` — python:3.12-slim, the locked
   requirements, the pg client, a non-root user; the three start commands: `api`
   (`python3 -m harness.api`, :8080, the fail-closed secret matrix), `worker`
   (`python3 harness/worker.py --name <id>`, the durable loop), `migrate`
   (`python3 harness/migrate.py`, the release oracle — run before api/worker).
2. **The front** (the Q18-ratified form): the Cloudflare Tunnel — `cloudflared`
   with outbound-only 443; the ingress hostname `arivo.itscatalyst.com` ->
   `http://localhost:8080`; the edge cert + the tunnel's origin cert (no inbound
   ports, no origin IP exposure). DNS: the tunnel's CNAME, proxied.
3. **The release order**: migrate -> api -> worker (the health gate between:
   `/health/ready` green before the worker starts).
4. **The verification** (the runbook §16's own list): public HTTPS valid; origin
   TLS; the database `verify-full`; CORS matrix; the rate limits; the host
   validation; the MCP `/mcp` surface answering initialize.
5. **The secrets**: the matrix at `harness/api/env.example.txt` — every name,
   its consumer, its class; the tunnel token and the database password are the
   two secrets the runtime holds; nothing else.

## The gates (the standing owner decisions)

- **Q18** — the runtime selection (the request: context/runtime-decision-request-2026-11-27.md;
  the recommendation: a generic container behind a Cloudflare Tunnel).
- **The database credential** — the Supabase PAT in the store is a dead placeholder
  (verified live: `JWT could not be decoded`); the deployed service + the remote
  0021/0022 migrations await a working connection string (`sslmode=verify-full`).
- **WS8** — the storage provider ratification (R2 recommended).
