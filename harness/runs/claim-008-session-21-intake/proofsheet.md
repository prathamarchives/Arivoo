# PROOF SHEET — slice claim-008-session-21-intake (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): e78ac8ba6b553aab809cf1a81eed133ec2f81e26
- generated (last record's timestamp): 2026-10-19T14:33:10.548484+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 6538b12d68c9f17b · 2026-10-19T14:33:03.202144+00:00
- `python3 harness/claims.py` -> exit 0 · output sha256 6beec6ef5d385ac5 · 2026-10-19T14:33:03.269299+00:00
- `make harness-tests` -> exit 0 · output sha256 fe538ca05df12ed1 · 2026-10-19T14:33:10.548484+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the verbatim §1 transcription was made through the session context — a byte-level mechanical diff against the original message was not possible from this host (the standing limit, stated in the record's §1 close)
- - no fresh technical verifier and no SEV for this slice — the pre-H-02 discipline, the record-20 §8 honest gap; it closes when H-02's machinery is live
- - the live-API observations in §2 (main SHA, PR states, run conclusions, protection shape) are re-observations at preflight time, not properties of this tree (INT-104's class)
- - the H-01a residual reproductions were preflight inspections in disposable clones — the registered RED + regressions land in the H-01a-R sub-slice, not here
- - the card refresh records contracts, not implementations — A03/A11/A12/A09/A08/A04/A07/A13/A05/A06 stay 'static, confirmed' until their slices' RED-first regressions pass
- - no code was exercised beyond the repo's own check suites this slice; no product behavior exists yet to validate

## Assembly
- sheet sha256 (of the content above, excluding this line): 643b6b457db96a76c0d101382abacef034a0d0385a7227f75863308fcee43220
