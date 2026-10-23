# PROOF SHEET — slice claim-034-d043-appendonly-followup (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 2b8ec0c5926772a3ff0ba7e60600ef2ee879a071
- generated (last record's timestamp): 2026-10-23T06:03:02.716137+00:00
- run records: 11

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-23T06:01:27.861825+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-23T06:01:28.247513+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-23T06:01:30.227780+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 bd6fc24575009419 · 2026-10-23T06:01:48.233973+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 b2fd10b185e83334 · 2026-10-23T06:02:00.116209+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 8151db4255872e6d · 2026-10-23T06:02:01.629622+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 fdb77cf7366a9596 · 2026-10-23T06:02:01.934240+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-23T06:02:09.051159+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 591b298a9b177f15 · 2026-10-23T06:02:09.214191+00:00
- `timeout 900 python3 tools/verify_selftest.py` -> exit 0 · output sha256 d27839014b96df70 · 2026-10-23T06:02:15.467020+00:00
- `make verify` -> exit 0 · output sha256 e3415af80c00dcbd · 2026-10-23T06:03:02.716137+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - not verified (LAW-04 — the follow-up slice's honest limits):
- - - unchanged from the CLAIM-033 slice's list (harness/runs/claim-033-state-record-reconciliation/notverified.txt):
- the binding's actor/timestamp provenance (no audit data on the endpoint; personal repo, no org audit-log
- API); the export a snapshot (INT-104) — each preflight re-reads; the platform's runner isolation (F-03
- EXTERNAL); the prose-consistency bound (the mechanical checks passed 52/0 at the edited tree).
- - - this slice changes NO code and NO test: the regression surface for the registry's append-only rules
- remains the claims-path suite's ARV-CLM checks + the reviewer rounds themselves (the round that caught this
- miss IS the evidence that the append-only violations are reviewable defects — mechanically pinned only at
- the registry layer, never at the DECISIONS prose layer; a mechanical DECISIONS-append-only check, if ever
- wanted, is a scoped decision for the owner, never silently built here).
- - - the thread-resolution sequencing: the reopened DECISIONS.md thread resolves only when THIS repair merges —
- observed in the PR, never claimed before.

## Assembly
- sheet sha256 (of the content above, excluding this line): c28b43a04117f31d8322a8bccebd0b076bd9c50524e277709b9d2aae277ca8f9
