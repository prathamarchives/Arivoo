# PROOF SHEET — slice claim-014-anchored-name-repair (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 3469b061e79679112b2ff160f0f19fe08c703217
- generated (last record's timestamp): 2026-10-20T09:37:01.528176+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 6c3f8977dcf28434 · 2026-10-20T09:36:28.254947+00:00
- `make verify` -> exit 0 · output sha256 cbd81ae6e5a8c7a1 · 2026-10-20T09:37:01.528176+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the repair is live-verified only at the PR's CI + the post-merge run; the anchored-name path (the _anchored suffix resolution) is exercised end-to-end by test_10's completed fixture (the runner copy under its real name — exactly what the workflow's anchor step does) and by the CI floor step itself
- - the deeper lesson is recorded in record 22 §8 catch #11: the vacuous-pass class my own floor guards against appeared in my own regression test — twice (the early refusal, then the runner-load crash both left the marker absent) — a test that asserts an ABSENCE must also prove the mechanism under test actually RAN
- - no fresh technical verifier and no SEV — the pre-H-02 discipline

## Assembly
- sheet sha256 (of the content above, excluding this line): 3f9c9b4e2e3fa57a4f10441575ebda0e163a88e309b615d9829c793d9d8bdf81
