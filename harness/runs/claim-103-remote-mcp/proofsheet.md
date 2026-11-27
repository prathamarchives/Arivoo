# PROOF SHEET — slice claim-103-remote-mcp (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 9bd4f0d966244193bf9806d27b78f5b9544d2936
- generated (last record's timestamp): 2026-11-27T14:10:16.284297+00:00
- run records: 4

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 85b0bf9cd123077c · 2026-11-27T13:53:26.499400+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 fc3d72f30368ff31 · 2026-11-27T13:53:26.708540+00:00
- `python3 harness/tests/test_api_routes.py` -> exit 0 · output sha256 37d261d918796822 · 2026-11-27T13:53:44.327898+00:00
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 5a1a59719cae704f · 2026-11-27T14:10:16.284297+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token; uvicorn over a real socket; the deployed /mcp surface (the Workstream 10 slice)
- the server-push SSE stream form of the Streamable transport (this slice serves the single-response JSON mode; the 405 on GET /mcp is the honest answer)
- the MCP session management (Mcp-Session-Id headers, resumability) — the stateless per-POST form only at this slice
- the semantic/model work (Q7 open — deterministic only); the remote btree/TOAST parity (carried)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: f2f04c596836fa2eae953349692fd79d893db82da042380c62f311986224cb82
- reviewed_diff_sha256: 5597cdbf885797d56c6573bf0762e2421caa95b8fa7cea8840e0c51f4a3acffe
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): ea9f91dc5388dcc88f87be13d787393bf06987575888b8d3c7fbc89704444306
