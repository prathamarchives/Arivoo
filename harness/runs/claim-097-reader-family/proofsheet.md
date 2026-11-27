# PROOF SHEET — slice claim-097-reader-family (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 6ebb5b3ae5cde4b5475e60a9267efdd1991efb07
- generated (last record's timestamp): 2026-11-26T14:12:50.980811+00:00
- run records: 4

## Run records (command, exit, output digest)
- `.venv-waved/bin/python -I harness/api/routes_selfcheck.py` -> exit 0 · output sha256 b54523163c45363c · 2026-11-26T14:00:32.474357+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 63e0886d6f3cf0b6 · 2026-11-26T14:00:32.688768+00:00
- `python3 /home/z/my-project/scripts/sev097_probe.py (the reviewer's own kernel/ASGI probe set P1-P6)` -> exit 0 · output sha256 e6358e536068807c · 2026-11-26T14:12:50.980811+00:00
- `python3 /home/z/my-project/scripts/sev097_probe.py P7 (the red re-observation at 0ce1be9, detached worktree)` -> exit 0 · output sha256 8be2ec6ff965ef04 · 2026-11-26T14:12:50.980811+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens — never pre-claimed)
- a live Supabase-issued token end-to-end; uvicorn over a real socket; the deployed route surface (the Workstream 10 slice)
- the passage-text serving route (the §11.2 'source/read data' body arm — rides the capture families' slice; the anchor resolution serves the content-addressed form here)
- the remote btree/TOAST parity (carried from record 80 §9)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 904f46c8dc2105e1454eef904420fcd9300365c0b61f0ff97d0ef2b8a0a2b95b
- reviewed_diff_sha256: c089dda41e517a26d27d31a447282e47b6b945f3f8e336f1f20e115ed1e98ed2
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 9

## Assembly
- sheet sha256 (of the content above, excluding this line): 2b1090edc325c5569e0e61e231d99121bcc0b70c7251c3817857337a211e033e
