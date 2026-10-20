# PROOF SHEET — slice claim-016-h01b-fixture-hygiene (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 96c40ef633b87c2e5a506a04184961dbca5a89ba
- generated (last record's timestamp): 2026-10-20T13:04:14.197739+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 0a91b3f55844677f · 2026-10-20T13:02:59.494219+00:00
- `python3 tools/isolation_check.py` -> exit 0 · output sha256 85a2f01ed68ee5b4 · 2026-10-20T13:02:59.712219+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 84171ae2951627b4 · 2026-10-20T13:03:05.785306+00:00
- `make verify` -> exit 0 · output sha256 7e33509f25c45c0e · 2026-10-20T13:03:38.029810+00:00
- `python3 /home/z/my-project/scripts/cw_sim.py` -> exit 0 · output sha256 3896a9dc7c1f83ef · 2026-10-20T13:04:05.044940+00:00
- `python3 -I tools/isolation_selftest.py` -> exit 0 · output sha256 0a91b3f55844677f · 2026-10-20T13:04:14.197739+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the CI canonical-layer job's real runs are exercised here only through the LOCAL simulation (the coordinated-weakening sim: the base's 18-case suite judged against this checker over a full-tree copy, exit 0) — the actual GitHub runner executions (isolation_selftest_anchored + isolation_check_anchored --ci + head-tools) are observed at the PR's CI, pending at push; the post-merge selfcheck re-observes
- - the FLOOR-REVIEW-1 independent adversarial review (session 23, the H-01b exit item) ran against the FLOOR files (mutation_runner/verify_selftest — DISJOINT from this slice's files) and its B1/B3/B4 findings are routed to the NEXT slice's repairs, never folded into this one; this slice's own two files received the pre-H-02 discipline only (no SEV, no fresh technical verifier beyond the sim)
- - the symlink-swap RACE (a concurrent attacker swapping a regular file for a symlink between lstat and open) is covered by the O_NOFOLLOW + open-fd re-verify design and asserted indirectly (the refusal paths), but no true concurrent race schedule was executed — the race window is inherent to any same-user filesystem and remains a residual, stated
- - the count budget (2000) and total budget (64 MiB) refusal paths are proven by B4-class fixtures for the TOTAL case only; the COUNT branch shares the same code path and refusal channel but has no dedicated case (the old suite's 18 cases + 6 new cases cover the per-file, total, and race classes; count is enforced by the same refusal protocol)
- - the builder budget overrides (B6's injected total) exist to keep the proof cheap for CI: the PRODUCTION budgets (8 MiB per file / 192 MiB total / 5000 files) are documented constants with ~80x headroom over the live corpus; no source tree at production scale was copied to prove the production values fire — the enforcement mechanism is the same code path the injected values exercise
- - F-003/F-004/F-005's workflow-side trust chain and F-006's gate registry-at-import are H-01b-CI's items, untouched here; Q10 remains owner-gated

## Assembly
- sheet sha256 (of the content above, excluding this line): 72007590c93b02b5a8e9e07189df53e6e28990b064f3bd485f92203f16193c92
