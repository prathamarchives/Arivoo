# PROOF SHEET — slice claim-110-remote-db-user (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): ed6f7685baa8695ddee57149421bbff565a7a39c
- generated (last record's timestamp): 2026-11-28T10:53:24.966696+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 harness/tests/test_remote_db_user.py` -> exit 0 · output sha256 bab9976b186f2e2f · 2026-11-28T10:53:13.686534+00:00
- `docker build -t arivo:verify-local .` -> exit 0 · output sha256 91b4546a7ef0a698 · 2026-11-28T10:53:24.555345+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 31b278d2dcec0d4f · 2026-11-28T10:53:24.966696+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- Not verified: no write/import/export/purge lifecycle was re-run against the deployed surface (the rig campaign remains its evidence); no MCP agent credential was available; no R2 I/O; the image was rebuilt and the containers restarted locally, but no new tunnel/DNS change was made. The five required checks on the PR head are authoritative.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 6f21db2d1d7d37f45998496580b8ceb32606fa1eb01a7f829eddb461f904c0ff
- reviewed_diff_sha256: 0784923dbf2c68cced251c3e401b182c68c8dd51b4c780e9efb2844f5838a94f
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 7b95e950f62bb8ad1832a7301d71e6ae35cc09285596d3c60b2c9335cd95b22b
