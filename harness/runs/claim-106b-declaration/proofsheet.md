# PROOF SHEET — slice claim-106b-declaration (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 184cffa47d92e784af8d2987d0493b2649410393
- generated (last record's timestamp): 2026-11-28T05:35:31.892835+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 be53ca0f3f3af262 · 2026-11-27T15:45:26.490574+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 be53ca0f3f3af262 · 2026-11-27T15:50:02.198012+00:00
- `.venv-waved/bin/python -I harness/tests/test_acceptance_campaign.py` -> exit 0 · output sha256 5a666053ca900f3f · 2026-11-27T15:58:46.470963+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 01697530e4879783 · 2026-11-28T05:34:53.623925+00:00
- `python3 -I tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-11-28T05:35:31.718741+00:00
- `python3 harness/tests/test_acceptance_campaign.py` -> exit 0 · output sha256 97483947a90c95b8 · 2026-11-28T05:35:31.892835+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- This slice is the completion-declaration artifact plus its RED/green evidence; the two code repairs it originally carried landed on main first in PR #151 / CLAIM-106c (the canonical-layer job anchors MAIN's checker, so a candidate-side change cannot take effect).
- Not verified: (1) the campaign's ACC-01..18 were NOT executed in this session — no PostgreSQL rig, no fastapi/jwt/psycopg on this host; the campaign's executed-path evidence remains the session-65 rig run record (run-03).
- (2) The canonical-layer self-test was verified locally in BOTH shapes (in-tree and the CI-shaped anchored copy in a clean clone), but the authoritative confirmation is the remote job on this PR's head.
- (3) The 8000 count cap (now on main) is sized against today's measured corpus (1997 files); it is a re-base of an anomaly guard, not a proof that no future tree can exceed it.
- (4) The venv-less harness-suites runner's own provisioning of fastapi/psql (the deferred option that would let CI EXECUTE the campaign) is NOT in this diff — it is a named follow-up needing its own claim.
- (5) No production database, storage provider, host, tunnel or deployed service was touched by this slice.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 17d4e4a275fb29edbd5e9a9da6e90b7cf9b33ad177de0d8ab84ca5d872436ac1
- reviewed_diff_sha256: b66971f86be1b4ea42e0778aaf3c39ccbc9e5cd0ca61a52b657d655d35533548
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): fbdcab6993e4c2380f9454e461493ac358ae9aeae252d2d5a25aba1b18c50b19
