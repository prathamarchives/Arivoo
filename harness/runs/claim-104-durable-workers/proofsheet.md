# PROOF SHEET — slice claim-104-durable-workers (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): e1c549e468ca645e6f52206d44804507c63a7a2e
- generated (last record's timestamp): 2026-11-27T14:45:13.537502+00:00
- run records: 4

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T14:28:50.818450+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 137dc134f8293560 · 2026-11-27T14:28:51.023700+00:00
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T14:31:02.332269+00:00
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T14:45:13.537502+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token; uvicorn over a real socket; the deployed surface (the Workstream 10 slice)
- the persistent (polling) worker form under a supervisor — the --once batch form proven; the service deployment is Workstream 10's own slice
- the remote 0021/0022 application (the Supabase migration credential never provided to this session)
- the storage provider adapter (the WS8 gate: the owner's ratification pending — the decision request prepared)
- the semantic/model work (Q7 open — deterministic only)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 9dd834ef838b80a8f7d789b5ef95ac8e7e12536f6a8ea7355dbabd670eb32c11
- reviewed_diff_sha256: e337bfc22187e59ebddf8b7340253ba7201762f42eb388a52054f8942a054048
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 90bb64390e63026a343cde3624909b865fa5398f3581585ae9fc6794b5625141
