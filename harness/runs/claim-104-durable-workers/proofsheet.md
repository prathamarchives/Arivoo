# PROOF SHEET — slice claim-104-durable-workers (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): a40ffd1d3fe189cacb8d56cecc7a15b0e9ab1bbc
- generated (last record's timestamp): 2026-11-27T14:31:02.332269+00:00
- run records: 3

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T14:28:50.818450+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 137dc134f8293560 · 2026-11-27T14:28:51.023700+00:00
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T14:31:02.332269+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token; uvicorn over a real socket; the deployed surface (the Workstream 10 slice)
- the persistent (polling) worker form under a supervisor — the --once batch form proven; the service deployment is Workstream 10's own slice
- the remote 0021/0022 application (the Supabase migration credential never provided to this session)
- the storage provider adapter (the WS8 gate: the owner's ratification pending — the decision request prepared)
- the semantic/model work (Q7 open — deterministic only)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: fed17744006812ead8f68d76b37c2bc851a9dfb017afd5072e6acedd6ed82a6b
- reviewed_diff_sha256: 29288bcea2812776a26eba2ab784e9d419b32eb5161f60457d429dfa2f624dac
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 345119cce17355d194e1a7c21ee7848987d41719ff53b253875209391df0f3ee
