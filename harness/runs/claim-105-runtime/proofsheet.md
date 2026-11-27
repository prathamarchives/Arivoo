# PROOF SHEET — slice claim-105-runtime (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 18a9bc40c96a2bfcf1eeff4f0424c0a42b412a37
- generated (last record's timestamp): 2026-11-27T15:05:04.939742+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 1 · output sha256 d36e83583fac7753 · 2026-11-27T15:00:19.990930+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 a4a7b9994c5cc275 · 2026-11-27T15:01:48.173298+00:00
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T15:05:04.939742+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- the Q18 OWNER GATE: the runtime selection (Tunnel new / Tunnel reuse / Containers beta / another host) — the deploy is blocked on the owner's ONE decision
- the production database credential (the Supabase PAT in the store is a dead placeholder — JWT could not be decoded; the remote 0021/0022 application + the deployed service both await it)
- the docker image BUILD itself (no docker/podman in this sandbox — the image's CONTENT contracts verified instead: the fresh-venv pip install of the locked requirements, the api start command serving /health/live /health/ready /mcp 401 /api/v1/me 401, the fail-closed ARV-SVC-001 refusal, the 22-migration release oracle on a fresh db)
- the deployed surface end-to-end (the tunnel, the DNS, the public HTTPS, the origin TLS, the verify-full database TLS, CORS, the rate limits, the host validation) — all post-gate
- the storage provider adapter (the WS8 gate — the owner's ratification pending)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: fba4edb89da1fc2008235ce0c4c146b3642f9597c3dbfb4b65a07412137ae50f
- reviewed_diff_sha256: 04d41102aeb6a4be45d33f0178133f9200814ecd3e142ef1ca8ce27fee0b442c
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 62a8ee5f366266188767451ac1656ac43a7a0e956acf91ac7b513d16982c003a
