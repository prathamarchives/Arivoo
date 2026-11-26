# PROOF SHEET — slice claim-095-kwr-token-bound (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): e870ad2691d11026afc3e2f1f3c66ab5b47c4b32
- generated (last record's timestamp): 2026-11-26T12:26:59.638517+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_kwr_bound.py` -> exit 0 · output sha256 5e3ce88509fbc8a2 · 2026-11-26T12:07:25.140380+00:00
- `for t in test_keyword_index test_import test_note test_journal test_highlight test_bookmark test_retrieval_packs test_commands; do python3 harness/tests/$t.py > /tmp/suite-$t.out 2>&1 || { echo "RED $t"; cat /tmp/suite-$t.out; exit 1; }; grep -m1 '^GREEN\|SUITE GREEN\|GREEN —' /tmp/suite-$t.out | head -1; done` -> exit 0 · output sha256 77147e6e52f950e7 · 2026-11-26T12:08:19.181609+00:00
- `bash harness/runs/claim-095-kwr-token-bound/f6-spike.sh` -> exit 0 · output sha256 b22e5cea8af947a7 · 2026-11-26T12:08:53.533096+00:00
- `python3 harness/gate.py --slice claim-095-kwr-token-bound --diff origin/main --skip-suites` -> exit 1 · output sha256 c084ba05769545b1 · 2026-11-26T12:09:13.932602+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 f4f216fccd6032af · 2026-11-26T12:26:59.638517+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the bound value's interplay with a SUPABASE-side btree (the remote's block size and TOAST settings are Supabase-managed; the local 17.12 rig is engine-parity, not config-parity — the 512-byte raw bound sits far enough under any 8k-block ceiling that the margin covers it, but the remote observation rides the 0020 application session's verification pass)
- the remote migration ledger re-read (0020 still unapplied remotely as of the directive's own §2.3 check — the remote application is the next workstream's own act)
- a live Supabase-issued token end-to-end (carried: needs a real user — §17.1's class)
- uvicorn over a real socket; the route surface against the remote db (the deployment slice's own acts)
- the btree-limit source reading was verified against REL_17_STABLE (the stable branch), not the exact Debian patch level's source tree (17.12-0+deb13u1) — the Debian delta is packaging, but this is stated rather than assumed
- the five required PR-head CI checks and the D-042 merge-gate review (observed after the PR opens — never pre-claimed)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: ba338470b832888e4c4dc3f8b3df80618757e13ae6a317da8a7693a338a0406e
- reviewed_diff_sha256: 694cb9f7132031b0d96923c1f876fc89aa3cbaa9d0827d44084a453c6ae8daff
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 8

## Assembly
- sheet sha256 (of the content above, excluding this line): 3166c4f9a3a3be7360f406efca3f9a19e941580144cca023e21270fea815b175
