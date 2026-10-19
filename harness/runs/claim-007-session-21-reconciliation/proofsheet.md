# PROOF SHEET — slice claim-007-session-21-reconciliation (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 0c5a8666f44f7f65da1612f56be714bbcae093eb
- generated (last record's timestamp): 2026-10-19T14:19:01.098287+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 3ca757dfb6c98197 · 2026-10-19T14:18:53.518562+00:00
- `python3 harness/claims.py` -> exit 0 · output sha256 6beec6ef5d385ac5 · 2026-10-19T14:18:53.588223+00:00
- `make harness-tests` -> exit 0 · output sha256 31a85ea727989bdf · 2026-10-19T14:19:01.098287+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the live-API observations in this slice's STATE entry (main SHA, PR/merge state, run conclusions, protection shape) are re-observations at preflight time, not properties of this tree (INT-104's class); a committed file cannot carry live status
- - no fresh technical verifier and no SEV for this slice — the pre-H-02 discipline, the same honest gap record 20 §8 states; it closes when H-02's machinery is live
- - the turn-21 H-01a residual reproductions (gate.py:191's uncaught GitRefusal; the broad ARV-PRF assertion; the not-check-ref-format-legal hostile fixture) were preflight inspections in disposable clones — the registered RED + regressions land in the bounded H-01a completion sub-slice, not here
- - PR #41's three-check-green history (runs 39259218809, 39259609210) is GitHub's record re-observed via API, not re-executed on this host
- - no browser was used this session; the live state was read through the GitHub API with the standing out-of-repo token — the token's validity is observed-by-use, not independently audited

## Assembly
- sheet sha256 (of the content above, excluding this line): 710bc3a8b837f8eef2989d18df794848db3bb89393fca048096155d6be45e16a
