# PROOF SHEET — slice claim-104-durable-workers (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 90f7be7d0c654b2921762fea28eebacc3568b5f0
- generated (last record's timestamp): 2026-11-27T14:28:51.023700+00:00
- run records: 2

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T14:28:50.818450+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 137dc134f8293560 · 2026-11-27T14:28:51.023700+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token; uvicorn over a real socket; the deployed surface (the Workstream 10 slice)
- the persistent (polling) worker form under a supervisor — the --once batch form proven; the service deployment is Workstream 10's own slice
- the remote 0021/0022 application (the Supabase migration credential never provided to this session)
- the storage provider adapter (the WS8 gate: the owner's ratification pending — the decision request prepared)
- the semantic/model work (Q7 open — deterministic only)

## Assembly
- sheet sha256 (of the content above, excluding this line): 4508126294a06a110bff6d6789c3dcd793d24788c5709dc2d927b8f082773208
