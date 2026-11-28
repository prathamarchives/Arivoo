# PROOF SHEET — slice claim-106c-isolation-budget (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 23f1b63ef4a993461d6a0323210f326f2aab4f64
- generated (last record's timestamp): 2026-11-28T05:43:01.682384+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 -I tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-11-28T05:43:01.503473+00:00
- `python3 harness/tests/test_acceptance_campaign.py` -> exit 0 · output sha256 97483947a90c95b8 · 2026-11-28T05:43:01.682384+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- This slice changes the two merge-enabling code paths only; its evidence is confined to its own run dir so the candidate tree stays under the base judge's 2000-file cap.
- Not verified: (1) ACC-01..18 did NOT execute here — no PostgreSQL rig, no fastapi/jwt/psycopg on this host; the campaign's SKIPPED line is the honest statement, not acceptance evidence (run-02).
- (2) The authoritative confirmation of the count-budget repair is the remote canonical-layer job on this PR's head; the local self-test (run-01) and the CI-shaped reproduction in red.txt are preflight only.
- (3) The 8000 count cap is sized against the measured 1997-file corpus; it is a re-base of an anomaly guard, not a proof about future trees.
- (4) Provisioning fastapi/psql in the venv-less trusted runner (so CI could EXECUTE the campaign) is NOT in this diff — a named follow-up needing its own claim.
- (5) After this lands on main, PR #150 still needs its SEV base re-bound to the new merge-base and its proof sheet regenerated; that is the consuming slice's work, not this one's.
- (6) No production database, storage, host, tunnel or deployed service was touched by this slice.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 36eb99adf646c66158c2d360a1ba85883099df469ddb8e04178d033ee9de4fb9
- reviewed_diff_sha256: f492e9ec4627650cbbb43109556b9805ade36b74bf4b343d369331c7f52cb574
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 001cfbd66df38c5c674197e2cc4e6c170780504ae316bd5ee8488da556ce1023
