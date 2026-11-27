# 88 — REMOTE-MCP (the Streamable HTTP transport — the Workstream 7 slice)

> STATUS: SESSION ENGINEERING RECORD (2026-11-27; the session's intent refs: INT-162/170; D refs: D-042/D-055). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 125. PRs this session: #145 (this slice).

## §1 What landed

1. **POST /mcp** — the remote MCP Streamable HTTP transport (single-response JSON
   mode) over the EXACT SAME read-only registry/query kernel as the stdio wrapper:
   - `harness/mcp.py` UNTOUCHED (its stdio behavior is the preserved law — the
     directive's own "Preserve the existing 22-tool stdio MCP behavior"; the suite
     re-observed GREEN);
   - the route IMPORTS `TOOLS`/`REGISTRY`/`_assemble` — zero duplication, the
     registry served is byte-identical (the battery proves the set equality);
   - NO write tool exists (ARV-MCP-001's closed-membership refusal, verbatim).
2. **The auth** — the owner-minted agent read credential (D-055's P4-E surface):
   the Bearer token rides `ARIVO_AGENT_TOKEN` to the query.py child; the
   credential's own sha256 resolution (the narrow SECURITY DEFINER lookup), the
   owner scope FROM the credential, the per-read audit row, the hash-only storage,
   the one-time token display, the final revocation — ALL the kernel's own laws.
   The route never parses, stores, or echoes the token. The unauthenticated
   transport refuses the MCP-level 401 (-32001) before any protocol read.
3. **The protocol surface** — initialize (the honest version negotiation:
   2025-06-18 the only claimed version, an unknown request answered with the
   adapter's own), ping, tools/list (the EXACT 23-tool registry — one more arm
   landed since the "22" count: the reading-lists family), tools/call (the
   argv-safety convention, byte-preserving results, isError on nonzero exit),
   notifications never answered (202 Accepted — the streamable form), -32601 the
   unknown method, -32602 the typed argument law, the bounded body (32 MiB cap,
   the non-object 422).
4. **GET /mcp answers 405** — the single-response Streamable mode only; no
   server-push SSE stream at this slice (disclosed in the not-verified lines;
   the desktop/agent clients polled per-call need no stream).

## §2 Verification

- **RED observed** at the battery-only commit `d161480` (exit 1, 16 failures —
  the route absent; 208/219/221 pass vacuously as the mint/revoke legs run
  through the kernel, disclosed here).
- **GREEN** at the implementation head: the full battery passes (ARV-API-208..226
  all PASS; the battery total 242).
- The stdio MCP wrapper suite re-observed GREEN (MCPW-01..10) — the preserved law.
- The agent-access suite re-observed GREEN (AGT-01..09) — the credential machine
  untouched.
- The battery's legs: the transport auth; the negotiation; the notification law;
  the registry set-equality; a live tools/call through the SAME kernel; the
  no-oracle invalid/revoked classes (the kernel's own ARV-AGT-001); the
  cross-owner scope (B's credential never sees A's corpus); the per-read audit
  rows (agent_read_log counted); the malformed body; the unknown method; the 405.

## §3 Not verified (LAW-04)

- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens)
- a live Supabase-issued token; uvicorn over a real socket; the deployed /mcp
  surface (the Workstream 10 slice)
- the server-push SSE stream form of the Streamable transport (this slice serves
  the single-response JSON mode; the 405 on GET /mcp is the honest answer)
- the MCP session management (Mcp-Session-Id headers, resumability) — the
  stateless per-POST form only at this slice
- the stdio wrapper's 22-tool count is now 23 (the reading-lists family landed
  after the count was frozen in prose; the registry itself is the truth, the
  battery proves the set equality)

## §4 Residuals / follow-ups

- The one-time token display: the mint command's ack is the ONLY place the token
  appears (the spine's replay never re-runs build); the battery reads it from
  the ack line — the desktop onboarding contract wraps this in the owner UI.
- Workstream 8 (the storage ratification) opens next.
