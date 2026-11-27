# PROOF SHEET — slice claim-105-runtime (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): a50df3805a0a742138a1089e79b4bd9bb3008564
- generated (last record's timestamp): 2026-11-27T15:10:33.231129+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 1 · output sha256 d36e83583fac7753 · 2026-11-27T15:00:19.990930+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 a4a7b9994c5cc275 · 2026-11-27T15:01:48.173298+00:00
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T15:05:04.939742+00:00
- `.venv-waved/bin/python -I harness/tests/test_workers.py` -> exit 0 · output sha256 2171699afad38e18 · 2026-11-27T15:10:33.231129+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- the Q18 OWNER GATE: the runtime selection (Tunnel new / Tunnel reuse / Containers beta / another host) — the deploy is blocked on the owner's ONE decision
- the production database credential (the Supabase PAT in the store is a dead placeholder — JWT could not be decoded; the remote 0021/0022 application + the deployed service both await it)
- the docker image BUILD itself (no docker/podman in this sandbox — the image's CONTENT contracts verified instead: the fresh-venv pip install of the locked requirements, the api start command serving /health/live /health/ready /mcp 401 /api/v1/me 401, the fail-closed ARV-SVC-001 refusal, the 22-migration release oracle on a fresh db)
- the deployed surface end-to-end (the tunnel, the DNS, the public HTTPS, the origin TLS, the verify-full database TLS, CORS, the rate limits, the host validation) — all post-gate
- the storage provider adapter (the WS8 gate — the owner's ratification pending)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 00957542fdb54458dd6c1a60d247e359d7445a57f6cb3a8cd5af3b4870edfe62
- reviewed_diff_sha256: 5bd3c06f59c1d3a30da34d25be209173b44127554c7c06c6281b1ce921e19343
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 1b2cfd3d006a9872ab13b6782e1ddf5c1abd3c0046305a2367cbcd2ef53cc95b
