# SEV round-1 — slice claim-103-remote-mcp (Workstream 7; INT-170)

- reviewer: inline verification (the 101..103 protocol; the battery's own legs
  ARE the probe set — the transport legs drive the REAL ASGI app against a
  REAL migrated db with LIVE kernel-minted credentials; the stdio + agent
  suites re-run as the regression floor)
- head at review: the bookkeeping commit (the battery GREEN 242)
- base: e36d6e3 (origin/main, the PR #144 merge)
- disposition: PASS — zero findings

## The probe table (ARV-API-208..226, all PASS)

| Probe | What | Observed |
|---|---|---|
| 208 | the credential mints through the kernel (the one-time token in the ack) | PASS |
| 209 | the unauthenticated transport: the MCP-level 401 (-32001) before any protocol read | PASS |
| 210/211 | initialize: the honest version negotiation (2025-06-18 honored; an unknown request answered with the adapter's own) | PASS |
| 212 | the notification NEVER answered (202 Accepted — the streamable form) | PASS |
| 213 | ping: the empty result | PASS |
| 214 | tools/list: the EXACT stdio registry (the set-equality — 23 tools, the same names, IMPORTED never copied) | PASS |
| 215 | tools/call: a live read through the SAME query kernel (isError=false, the page contract) | PASS |
| 216 | the unknown tool: ARV-MCP-001 (READ-ONLY, never a passthrough) | PASS |
| 217 | the undeclared argument: ARV-MCP-002 (the inputSchema is the contract) | PASS |
| 218/220 | the invalid AND revoked credentials: the KERNEL's ARV-AGT-001 through isError (the no-oracle class) | PASS |
| 219 | the revocation through the kernel (the owner's final act) | PASS |
| 221/222 | the cross-owner law: B's credential mints + reads ONLY its own scope (A's corpus absent) | PASS |
| 223 | the per-read audit: agent_read_log rows exist for every served read | PASS |
| 224 | the malformed non-object body: the transport's 422 (the bounded reader) | PASS |
| 225 | the unknown method: -32601 (the adapter's closed surface) | PASS |
| 226 | GET /mcp: 405 (the single-response mode; no SSE push stream at this slice) | PASS |

## The regression floor

- the stdio wrapper suite MCPW-01..10 GREEN (harness/mcp.py UNTOUCHED — the preserved law)
- the agent-access suite AGT-01..09 GREEN (the credential machine untouched)
- the RED at d161480 observed (exit 1, 16 failures; 208/219/221 vacuous through
  the kernel's own mint legs — disclosed)

## Not verified (carried to the sheet)

- the five PR-head checks + the D-042 review; a live Supabase token; the deployed
  surface (Workstream 10); the SSE stream form; the MCP session management
