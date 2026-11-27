# Arivo — the runtime compatibility report + the Q18 decision request

**Prepared per the directive's Workstream 10** ("Evaluate compatible runtime options;
Railway is not the default and must not be provisioned. Produce a measured compatibility
report for Cloudflare compute/container options and a generic container behind Cloudflare
Tunnel. Select a runtime only after the one Q18 decision.") This is the ONE consolidated
decision request. **Nothing has been provisioned or deployed.**

## What was measured / verified live (2026-11-27)

- The Cloudflare token works for: zone `itscatalyst.com` (id `0be7d7d7…`), the account
  (`Pratham2k26@gmail.com's Account`, id `d6d3436c…`), DNS reads (the zone's A records
  listed below), and **Cloudflare Tunnel management** — 3 named tunnels exist and are
  manageable: `doop` (healthy), `econ-lab` (healthy), `ecosystem-kb-local` (down).
- `arivo.itscatalyst.com` has **no DNS record yet** (clean slate — no conflict).
- The Supabase PAT in the store is a dead placeholder (`JWT could not be decoded`) — the
  production database credential is still missing; see "the standing block" below.
- The app: FastAPI/Starlette (pure-Python, no C extensions beyond `cryptography`),
  `psql` binary + a pg client for the durable workers, a subprocess-spawning worker loop,
  ~10 MB of dependencies. A single uvicorn process serves `/api/v1` + `/mcp` + the
  health endpoints.

## The options compared

| Criterion | A. Generic container behind Cloudflare Tunnel | B. Cloudflare Containers (Workers-attached, beta) | C. Cloudflare Workers (native) |
|---|---|---|---|
| Runtime fit | **FULL** — any Linux process; the `psql` binary, subprocess workers, arbitrary wheels | Full Linux env but orchestrated by a Worker; ~13 s cold starts reported; beta UX | **NONE** — the sandbox forbids subprocess spawning (the worker loop's kernel arms) and native `psql`; a rewrite would be required |
| The durable worker | **Runs as the same image's second start command** (the directive's "separate API/worker start commands" verbatim) | Containers scale-to-zero; a long-polling worker needs the keep-warm workaround | Impossible without an external queue rewrite |
| The MCP /mcp surface | Full HTTP control (single-response mode already served; SSE upgradeable) | Supported via the Worker front | Supported |
| Database connectivity | **Direct egress to Supabase with `sslmode=verify-full`** (§6.4's law) | Direct egress supported | Requires Hyperdrive (a proxy product) for Postgres |
| Where the container runs | **Your own host** (the VPS/box of your choice; the tunnel needs only outbound 443) | Cloudflare's edge (limited regions) | Cloudflare's edge |
| TLS to the public | **The tunnel's origin cert + Cloudflare's edge cert** (no inbound ports, no origin IP exposure) | Cloudflare-managed | Cloudflare-managed |
| Ops surface | `cloudflared` (one daemon; the 3 existing tunnels prove the pattern works on your account) | Wrangler + the beta Containers API | Wrangler |
| Cost | The tunnel is free; your host's cost is whatever it already is | Usage-based; the beta's pricing in flux | Free tier generous |
| Maturity | **GA for years; the `doop`/`econ-lab` tunnels on your account are healthy production proof** | Public beta (breaking changes expected) | GA |

## The recommendation

**Option A: a generic container behind a NEW Cloudflare Tunnel** (`arivo`), DNS
`arivo.itscatalyst.com` → the tunnel CNAME, proxied.

Why: it is the only option that runs the API and the private worker **as-is** (zero code
changes — the built image's two start commands), keeps the §6.4 `verify-full` database
TLS law intact without a proxy product, exposes **no inbound ports** (the tunnel dials
out only), and rides the exact pattern your account already runs in production
(`doop`, `econ-lab`). Option B is a beta with 13 s cold starts and a Worker-coupled
lifecycle; Option C cannot run the worker loop at all.

The alternative that stays on your account with less new surface: **reuse an existing
tunnel** (`doop` or `econ-lab`) with a new ingress hostname rule — same recommendation,
one fewer daemon. I'd still create the dedicated `arivo` tunnel (blast-radius isolation:
one ingress config per service).

## What is already built and waiting (runtime-neutral, no gate needed)

- The reproducible container image (Dockerfile: python:3.12-slim, the locked
  requirements, the pg client binaries, a non-root user; two start commands:
  `api` = uvicorn on :8080, `worker` = `python3 harness/worker.py`).
- `/health/live` + `/health/ready` (the readiness gate checks the DB + the auth state).
- The secret matrix (`harness/api/env.example.txt` + the deployment runbook section:
  every variable, which start command consumes it, which are secrets).
- The release/migration command (`python3 harness/migrate.py` as the container's
  `migrate` start command — the same oracle the CI uses).

## The standing block (independent of Q18)

The **production database credential is missing**: the Supabase PAT in the store is a
dead placeholder (`JWT could not be decoded` — 20 chars, not a real PAT). Even after
you ratify the runtime, the deploy needs a working Supabase connection string (or a
Postgres you designate) with `sslmode=verify-full`. The migrations 0021/0022 (the
governed purge + the durable jobs) also await that credential.

## The gate (the ONE decision)

Reply with one of:
- **"Tunnel, new"** — I create the `arivo` tunnel, route `arivo.itscatalyst.com`,
  build + deploy the container (you name the host that runs it, or I prepare the
  image + the tunnel token for your host).
- **"Tunnel, reuse <name>"** — same, on the `doop` or `econ-lab` tunnel.
- **"Containers beta"** — I build for the Workers-attached Containers beta.
- Or name another host — the container is runtime-neutral.

With the runtime choice, also provide (or point me to) the working Supabase connection
string / PAT.
