# PROOF SHEET — slice claim-022-h01c-claims-trust (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 1f931888b82c00b806f2623d1afa5f0b73a0396b
- generated (last record's timestamp): 2026-10-20T14:25:22.716654+00:00
- run records: 2

## Run records (command, exit, output digest)
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 725436301343c9ee · 2026-10-20T14:24:40.936849+00:00
- `make verify` -> exit 0 · output sha256 587bc5b56f2f9095 · 2026-10-20T14:25:22.716654+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the trusted S4c at THIS PR's head runs the BASE's (main's) cases + modules — the two NEW known-bads (KB-SCOPE-006/KB-CLM-006) bind all FUTURE PRs (base-anchored), not this one; the new suite likewise enters the required set at merge (the S1b of future PRs selects it from base's TESTS)
- - the ledger one-liner consistency check (the INT-126 triplication class) is SPLIT to its own next slice: it lives in the canonical verifier + its 30-mutation set + the 51-check count references — a different file family (LAW-05: one behavior per slice); the split is recorded in the claim row and this sheet
- - the numstat -z rename layout ('0\t0\t\0old\0new\0') was probed live on this runner (git 2.47.3) and matched git's documented -z semantics; the copy/rename 2-endpoint emission covers the same classes the identity covers
- - exotic-path handling is proven for spaces + unicode (test_02); a newline-in-filename is theoretically covered by the same -z parse but not fixture-tested (git allows it; the -z format carries it as raw bytes) — the parse is format-driven, not name-driven
- - F-008's test_04 pins the exemption's absence by SOURCE INSPECTION (inspect.getsource) in addition to the behavioral check_branch_claim refusal — the behavioral part is the authority, the inspection is the canary against the condition silently returning

## Assembly
- sheet sha256 (of the content above, excluding this line): 91fce26146ae0b79b1d928e3461655d0b948192a8aa362dd3a24d2fb8628d9fd
