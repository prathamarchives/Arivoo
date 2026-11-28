# PROOF SHEET — slice claim-109-deployed-acceptance (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c47f6aaea9f3d5c8dff74378c293b1bcbd5b51f5
- generated (last record's timestamp): 2026-11-28T10:36:02.470067+00:00
- run records: 4

## Run records (command, exit, output digest)
- `curl -s --max-time 20 https://arivo.itscatalyst.com/health/ready` -> exit 0 · output sha256 e603fe7d63cf53bc · 2026-11-28T10:35:59.807736+00:00
- `curl -s -o /dev/null -w '%{http_code}' --max-time 20 https://arivo.itscatalyst.com/api/v1/me` -> exit 0 · output sha256 dcaadad1cfce4377 · 2026-11-28T10:36:00.581033+00:00
- `curl -s -o /dev/null -w '%{http_code}' --max-time 20 https://arivo.itscatalyst.com/api/v1/openapi.json` -> exit 0 · output sha256 27badc983df1780b · 2026-11-28T10:36:01.912706+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 31b278d2dcec0d4f · 2026-11-28T10:36:02.470067+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- This slice records the public surface; it changes no code or infrastructure definition.
- Not verified: no real Supabase-authenticated REST call (no test user); no agent credential, so only the MCP refusal leg was exercised; no deployed end-to-end import/retrieval/worker campaign; no R2 object-store I/O; no always-on remote host (the owner chose the local machine, which goes down when it sleeps). The five required checks on the PR head are the authoritative confirmation; the local probes are preflight.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: c22bd95ea99722030debb006838028c50dbc5148242341d4fe4fab23d08d6742
- reviewed_diff_sha256: d70775da5405d93f8ca2778b25e830dfdf72fb7542a6617dae35b3a26cb6ba94
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): ca1f8857a405398763cc7d0b887b2410f28fff4722fd65621bb466d78b67b19e
