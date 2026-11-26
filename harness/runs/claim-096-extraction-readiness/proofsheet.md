# PROOF SHEET — slice claim-096-extraction-readiness (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 1e4760332f6bf5808790e6adc0afdf61854f3f24
- generated (last record's timestamp): 2026-11-26T13:11:29.361515+00:00
- run records: 2

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 6a54666a9d5ab50b · 2026-11-26T13:11:29.150641+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 74ffd1c7d0667260 · 2026-11-26T13:11:29.361515+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- a live Supabase-issued token end-to-end (needs a real user — the §17.1 class)
- uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the battery's five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- the remote's btree/TOAST parity for the 095 bound (carried from record 80 §9)
- arv_migrate's remote absence re-observed only through this session's pg_roles probe (consistent with the prior sessions' shape; no independent re-derivation)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: da420e33c1a91fe81a5b6a344693024f7b4cf821cb2663e6298279dea0d91cdc
- reviewed_diff_sha256: d5056b7e33846b26ca756b6cdadd2597bc1da47a1475ab654dfe90325567f3c0
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 8

## Assembly
- sheet sha256 (of the content above, excluding this line): 0991e46e2f3ffbc45279ae85c01a14a9da350190995016a80d52568dc78753c7
