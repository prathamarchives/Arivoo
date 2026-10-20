# PROOF SHEET — slice claim-025-r01-record-evidence (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): cb13b0f75fbadeacf2af9bf8d2238b9a1d059f96
- generated (last record's timestamp): 2026-10-20T16:21:53.858086+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-20T16:21:36.842798+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-20T16:21:37.227488+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-20T16:21:39.427708+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 260cbc11f7b5e813 · 2026-10-20T16:21:39.610533+00:00
- `make verify` -> exit 2 · output sha256 7ae5390a80b507da · 2026-10-20T16:21:53.858086+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the record-22 CRLF restoration produces a large MECHANICAL diff on that one file (544 insertions / 541 deletions) — the change is byte-verified: the restored file's prefix is BYTE-IDENTICAL to bc30575 (the last CRLF-faithful revision), the close's §12 block preserved, the repair recorded as a dated amendment; a reviewer re-deriving `git show bc30575:... | head -c N` against the restored prefix confirms it mechanically
- - the mutation-floor red_evidence repair is an honest UNRECOVERABLE statement, not a restored value: no committed revision ever carried the creation note (verified by walking every commit containing the record); the surviving evidence is cited (red-01/red-02 outputs, CI 39400826353, the post-merge observations)
- - the claim-013/014 run-record annotations label historical defects WITHOUT regenerating the records — a re-run at a later HEAD would exercise different code and prove nothing about those slices
- - no test file changed in this slice: no new red records are owed; the five suites + make verify re-ran green at this head unchanged
- - the intra-table-duplicate ratchet (R-04(9)) is NOT in this slice — the removal here is the data repair; the guard extension lands with its RED-first test in R-04 per LAW-05's one-behavior rule

## Assembly
- sheet sha256 (of the content above, excluding this line): 0a97139de14f7e4327ac58151b512a78f464d04c402cf77d8571d7758e4930d4
