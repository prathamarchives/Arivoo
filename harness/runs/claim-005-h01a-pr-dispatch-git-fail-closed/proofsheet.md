# PROOF SHEET — slice claim-005-h01a-pr-dispatch-git-fail-closed (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): d2ce708d447a51d1412ab5ffe49f4cb1be27ea83
- generated (last record's timestamp): 2026-10-19T12:50:55.296930+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 1c11046b9c24031a · 2026-10-19T12:50:10.861266+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 3ca757dfb6c98197 · 2026-10-19T12:50:11.010330+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 df0456842e9b11ee · 2026-10-19T12:50:24.954273+00:00
- `python3 tools/isolation_check.py` -> exit 0 · output sha256 4b8f208f23cf8aa4 · 2026-10-19T12:50:25.142281+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 e6d25aa311b358de · 2026-10-19T12:50:55.296930+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - The dispatch repairs are proven on the real dispatcher/gate path in fixture clones of THIS branch tip; a live never-merge hostile-branch PR against the protected main was NOT opened (owner-authorized probes only; A02's class is proven by the in-vitro subprocess cases, not a production push)
- - The CI event-field path is exercised in the real workflow only at this PR's own run (the harness job's env-passing + fetch-depth 0); the dispatch module's identifier validation covers ^[A-Za-z0-9._-]+$ derived names — Git-legal but exotic names outside that class (e.g. non-ASCII) are refused ARV-DISPATCH-001 (fail-closed, never executed) and are not separately fuzzed
- - ARV-DISPATCH-001/ARV-DIFF-001/ARV-DIFF-002 known-bad REGISTRATIONS (the coordinated harness+test weakening class) are H-01b's floor work, not this slice's; this slice proves the refusals through the dedicated regression suite
- - The remaining audit findings (A03, A04..A09, A11..A18) are untouched here — their dispositions stay 'static, confirmed' per record 20 §2
- - Q10 (workflow-tamper token hardening) remains owner-gated: this slice does NOT claim token or permission hardening — a PR can still change the workflow file itself

## Assembly
- sheet sha256 (of the content above, excluding this line): 9abb690787c8ac490c5961a2550c7ba8d39e468b90f178882e9227db6c425e86
