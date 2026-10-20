# PROOF SHEET — slice claim-020-h01b-ci-driver-env-call (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 915ceeab24ac342c125be20ab577868d85835bba
- generated (last record's timestamp): 2026-10-20T14:05:42.446003+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 da9c7487c43f46ed · 2026-10-20T14:05:03.363822+00:00
- `make verify` -> exit 0 · output sha256 b0544d56c0e8ba39 · 2026-10-20T14:05:42.446003+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the find was live at the S4c binding rehearsal (the second rehearsal catch of the session): the driver's env path was dead code at the call site — an env-only invocation refused with a false ARV-TG-001; the repair is pinned by test_08 but the CI form itself is proven only at the binding slice's rehearsal and its PR's CI (the workflow is NOT touched by this slice)
- - the workflow binding (part 2b, the -I flips + the shim removal + the S1b/S4c steps) remains the next slice — sequenced after this repair reaches main, because CI's S4c would otherwise anchor the broken driver and self-RED at its own head
- - the suites phase, the gate phase's re-rooting, the KB trust routing and the F-006 backstop are otherwise unchanged (PRs #53/#54's contract); the metadata validation order is unchanged (event validated before the machinery load — an invalid event still refuses before any candidate tree is read)

## Assembly
- sheet sha256 (of the content above, excluding this line): 6d020890eab354c7832c03f4b3bb3b60f6dd97edff62ea65017ced0b3780f677
