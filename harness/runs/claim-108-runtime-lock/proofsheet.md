# PROOF SHEET — slice claim-108-runtime-lock (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 073a059dcf1a902150ecd71dda4e9e76ef7a7da1
- generated (last record's timestamp): 2026-11-28T09:52:21.489760+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 harness/tests/test_runtime_lock.py` -> exit 0 · output sha256 574defe639149a4c · 2026-11-28T09:51:18.509070+00:00
- `docker build -t arivo:verify-local .` -> exit 0 · output sha256 3ecbb165ca8caf95 · 2026-11-28T09:51:28.561516+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 6209fa9178120cf4 · 2026-11-28T09:51:28.954368+00:00
- `python3 -I tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-11-28T09:52:21.489760+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- The image build and the container's health/CORS behavior were verified locally against the real remote Supabase DB. Not verified:
- - no always-on production host is available yet (Q18 decision given, host access not supplied); the container was run locally, not deployed.
- - no Cloudflare tunnel, DNS, or public HTTPS endpoint was created; no traffic through arivo.itscatalyst.com was exercised.
- - no live authenticated API call (a Supabase test user was not created); auth config was read from the project's JWKS and the verifier only reported 'configured'.
- - no worker process was run; the durable job machine was verified at the SQL level only (0021/0022 applied and arv_app grants present).
- - the wheel hashes were not re-downloaded from PyPI in this session; the lock's own pins/hashes were validated structurally and the image build installed them successfully.
- - the five required checks on this PR's head are the authoritative confirmation; the local runs are preflight.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 24cd5e2558db4a834a708145b4fed873c61ad114a13957cf7f938006c47353a9
- reviewed_diff_sha256: f5523b5690a1aedd719405f36212d7ed9cc6796e65a96b8742a90cfe61eacce5
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 44a3684bda19015ccb0c4670c89571f7689952c96741be3cbeb3274fde9c2c90
