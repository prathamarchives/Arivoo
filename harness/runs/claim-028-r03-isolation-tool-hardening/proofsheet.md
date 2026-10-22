# PROOF SHEET — slice claim-028-r03-isolation-tool-hardening (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): abcc29ac353decf1fa9ecb6bfa61981227451380
- generated (last record's timestamp): 2026-10-22T15:20:30.033363+00:00
- run records: 9

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T15:19:28.249691+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T15:19:28.624166+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T15:19:30.869016+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-22T15:19:43.487012+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 aabc93119fb178b6 · 2026-10-22T15:19:43.640301+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T15:19:45.136926+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T15:19:45.511593+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T15:19:47.788596+00:00
- `make verify` -> exit 0 · output sha256 1de42f86f4c29e51 · 2026-10-22T15:20:30.033363+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - not verified (LAW-04 — required, never empty-by-omission; the R-03 slice's honest limits):
- - - the mid-scan FIFO race itself (lstat-regular, then a same-user swap to a FIFO BEFORE the open) cannot be
- triggered deterministically through the checker's tracked-file scan — the B7/B8 child probes realize the
- race's WORST CASE directly (the open happens on an actual FIFO) and pin the non-blocking refusal; the
- lstat-to-open window between them remains the same-user/same-host residual the whole bounded-scan family
- already states (F-002's BOUNDARY, unchanged)
- - - O_NONBLOCK on a FIFO with a live WRITER would let a single capped read return partial data — moot here:
- the ISREG check refuses the fd BEFORE any read is attempted, and a regular file is never O_NONBLOCK-limited;
- stated for completeness, never exercised
- - - B9's unreadable-directory case cannot engage under root (chmod-0 vs CAP_DAC_OVERRIDE) — the case
- skip-declares under root with the reason printed (the R-02 test_20 precedent); the CI runners are non-root,
- the case engages there and in this non-root local environment (uid 1001, observed)
- - - the B5/B6 message pins are regression hardening, not a behavior repair: the wrapper's fixed message
- predates the pin (v2.2), so the pins pass at the predecessor BY DESIGN; their discriminating power is
- proven separately (red-02.txt: a scratch-corrupted wrapper fails B5/B6 with the named reason); the
- predecessor's own vacuity (type-only assertion) is the defect the pins close
- - - the directory-budget arithmetic is pinned at the REFUSAL, not at an exact constructed-entry count
- (B10 asserts the refusal + cleanup, not which specific directory breached) — the budget semantics are
- order-dependent by construction (walk order), and an exact-count pin would couple the case to os.walk's
- traversal order rather than the contract
- - - no fresh technical verifier and no SEV — the pre-H-02 discipline (H-02 is the next-but-one card: the
- ledger one-liner slice, then H-01c-authority/evidence, then H-02's activation)

## Assembly
- sheet sha256 (of the content above, excluding this line): 2e6e4222a61c625a993d0c81a089c29655b333d9d237b79a8cf67be30ee15cfd
