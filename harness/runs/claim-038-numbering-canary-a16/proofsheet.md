# PROOF SHEET — slice claim-038-numbering-canary-a16 (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): cb2e28787390bc010eccac8bf4c2196469943cd6
- generated (last record's timestamp): 2026-10-23T16:26:36.590200+00:00
- run records: 12

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-23T16:24:20.053128+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-23T16:24:20.394755+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-23T16:24:22.371280+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 94a5f2a252b89998 · 2026-10-23T16:24:55.179166+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 f14c30497a668b7b · 2026-10-23T16:25:12.035391+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 4b23e25a054ee54d · 2026-10-23T16:25:16.132631+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 2f6980ce2b2b7801 · 2026-10-23T16:25:16.456010+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 2c891f1bdf213996 · 2026-10-23T16:25:16.616443+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-23T16:25:28.347800+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 6c44222f4a71abc3 · 2026-10-23T16:25:32.772425+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 38ae33a60365cce0 · 2026-10-23T16:25:32.928770+00:00
- `make verify` -> exit 0 · output sha256 f3f13e7bfb9c19bb · 2026-10-23T16:26:36.590200+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- not verified (LAW-04 — the CLAIM-038 honest limits):
- - the env-KEY and remote-NAME masking SITES landed (_redact at both finding sites) and the
- direct probe OBSERVED the masked output (the canary never appears whole); the selftest-
- registry integration (the N12 row) is ROUTED as a named follow-up (the case runner's
- exit-2 usage form) — never silently claimed as selftest-proven.
- - the A16 narrowing: the alias check is concrete (from-import aliases of the ambient set);
- dynamic dispatch (getattr strings), exec/eval payloads, and environment/network access
- outside adapters remain the review layer's with named reopening triggers (record 31).
- - the N12-row routing and any further canary-position coverage (symlink link text beyond
- the existing CANARY_LINK case) are follow-up work under the part-2 claim's umbrella.

## Assembly
- sheet sha256 (of the content above, excluding this line): a91b116c7b72d1d44eb4936c88c378c6c8d12c97c31dbb71235297f75c3d968c
