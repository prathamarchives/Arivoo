# PROOF SHEET — slice claim-103-remote-mcp (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 1ddd8e10fc158ea327114378f6bb69eda1636357
- generated (last record's timestamp): 2026-11-27T13:53:44.327898+00:00
- run records: 3

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 85b0bf9cd123077c · 2026-11-27T13:53:26.499400+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 fc3d72f30368ff31 · 2026-11-27T13:53:26.708540+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 37d261d918796822 · 2026-11-27T13:53:44.327898+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token; uvicorn over a real socket; the deployed /mcp surface (the Workstream 10 slice)
- the server-push SSE stream form of the Streamable transport (this slice serves the single-response JSON mode; the 405 on GET /mcp is the honest answer)
- the MCP session management (Mcp-Session-Id headers, resumability) — the stateless per-POST form only at this slice
- the semantic/model work (Q7 open — deterministic only); the remote btree/TOAST parity (carried)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 22261d796233ac7e5183e6588f002515960d3e90402c1984d45244819ec6093f
- reviewed_diff_sha256: 05c49978d46a97dd84f23381789f8a18cd9fe82aecc2f591fc4c3fadf2ce7ba3
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 4aa7c99c659e7fb62bf5d784a14be0f6a1ee10ee54e323eb064692081143a053
