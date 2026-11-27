# PROOF SHEET — slice claim-105-runtime (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): cbb1ca91de19dfd1c374bfe49e010ff7335df80c
- generated (last record's timestamp): 2026-11-27T15:01:48.173298+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 1 · output sha256 d36e83583fac7753 · 2026-11-27T15:00:19.990930+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 a4a7b9994c5cc275 · 2026-11-27T15:01:48.173298+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- the Q18 OWNER GATE: the runtime selection (Tunnel new / Tunnel reuse / Containers beta / another host) — the deploy is blocked on the owner's ONE decision
- the production database credential (the Supabase PAT in the store is a dead placeholder — JWT could not be decoded; the remote 0021/0022 application + the deployed service both await it)
- the docker image BUILD itself (no docker/podman in this sandbox — the image's CONTENT contracts verified instead: the fresh-venv pip install of the locked requirements, the api start command serving /health/live /health/ready /mcp 401 /api/v1/me 401, the fail-closed ARV-SVC-001 refusal, the 22-migration release oracle on a fresh db)
- the deployed surface end-to-end (the tunnel, the DNS, the public HTTPS, the origin TLS, the verify-full database TLS, CORS, the rate limits, the host validation) — all post-gate
- the storage provider adapter (the WS8 gate — the owner's ratification pending)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: afa540c4e39c249bc9bdd4bfc5ea7b72367e109bc6e22b206b72b3f7a5c8d478
- reviewed_diff_sha256: 09e38e16ec0b799b03d67ef09a21f332498651990a853ced8fd00002e9061836
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 5332be01c1f3c6d373c5422269f6b0b37e14da4d4c510d4414943cce8c625ca9
