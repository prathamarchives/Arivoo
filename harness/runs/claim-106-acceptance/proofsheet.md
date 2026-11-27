# PROOF SHEET — slice claim-106-acceptance (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): da782e8092cc8b59c9ecabdcb118ead80da1a5c0
- generated (last record's timestamp): 2026-11-27T15:29:18.182062+00:00
- run records: 2

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/tests/test_acceptance_campaign.py` -> exit 0 · output sha256 5a666053ca900f3f · 2026-11-27T15:29:17.970374+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 be53ca0f3f3af262 · 2026-11-27T15:29:18.182062+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- §6.1(1) the real Supabase Auth test user + §6.4's Cloudflare-proxy stream legs (the DEPLOYED-surface halves — the Q18 gate + the database credential pending; the local form exercises the SAME contract surfaces with the ES256 contract)
- the reader repository inspection (WS11's frontend-contract half — the canonical link never provided to this session; the thin contract client's UI-facing legs ride it)
- the desktop offline/outbox behavior (Q19 — the local-store choice the owner's; the backend sync/API contract complete and observed)
- the storage fault-injection legs over a real object store (the WS8 gate — the provider adapter pending; the digest/staging/orphan laws covered on the local blob surface)
- the deployed surface end-to-end (the tunnel/DNS/TLS/CORS/rate-limits — all post-Q18)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: b0fa1211137f41ac624367a131e96f0e078f90b1351dc7abcbaf1fb6ef2efa9b
- reviewed_diff_sha256: ec91e78d32191f544f58124bb1769c29dc29bf615f3e558718ada3ed1b714b68
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 9ae62d2861ce09257f98f5af690209aaf904a1a938dcfb5cfe0e9a32c7fecad3
