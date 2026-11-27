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

## Assembly
- sheet sha256 (of the content above, excluding this line): ed07d2af9c53a5180caecbf5f8d110353e3aad18ae1a0e4e64d3e27f4303792d
