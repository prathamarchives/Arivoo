# 93 — DEPLOYED ACCEPTANCE (the public API/MCP surface)

> STATUS: SESSION ENGINEERING RECORD (2026-11-28; intent refs: INT-162/D-047; D refs: D-042). Historical process artifact per D-022. Worklog: Task 133. PR #154.

## §1 What landed

The `arivo` Cloudflare Tunnel, its DNS record and its ingress were created through the Cloudflare API with the owner-supplied token; the three pre-existing tunnels (`doop`, `econ-lab`, `ecosystem-kb-local`) were untouched. The origin is the owner-chosen local always-on machine, running three Docker containers on the `arivo-net` network: `arivo-api` (the built image, `arv_app` least-privilege DB credential, `verify-full`), `arivo-worker` (the durable loop), and `arivo-tunnel` (the connector). No inbound ports are published. All credentials are in a protected local file outside Git; no value appears in a repo file.

## §2 Observed through the public endpoint

- `GET https://arivo.itscatalyst.com/health/live` -> HTTP/2 200, `{"status":"live","api_version":1}`.
- `GET /health/ready` -> 200 with `db_ready:true`, `database:"declared-ready"`.
- `GET /api/v1/me` without a Bearer token -> 401.
- `GET /api/v1/openapi.json` -> 200.
- `POST /mcp` `initialize` -> `-32001` requiring the owner-minted agent read credential (the expected refusal; no token was supplied).
- CORS preflight -> `access-control-allow-origin: https://arivo.itscatalyst.com` only.

The tunnel's own prechecks passed (DNS resolution, QUIC/TCP connectivity, Cloudflare API reachable).

## §3 Not verified (LAW-04)

- No real Supabase-authenticated REST call (no test user was provided or created).
- No agent credential was available, so only the MCP refusal leg was exercised.
- No import/retrieval/worker end-to-end lifecycle was re-run against the deployed surface (the campaign's rig evidence remains the local run records).
- No R2 object-store I/O (the provider adapter is a separate, unclaimed slice).
- The owner chose the local machine as origin; if it sleeps, the public API goes down. A true always-on host remains an owner option.
