# PROOF SHEET — slice harness-s4a (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 574572f9f68859759999f41d7196c602623714b9
- generated (last record's timestamp): 2026-10-16T11:59:07.623040+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-16T11:59:04.608036+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-16T11:59:05.007085+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-16T11:59:07.542953+00:00
- `python3 harness/state.py` -> exit 0 · output sha256 e916f2462aec692b · 2026-10-16T11:59:07.623040+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the SIZE check lands IN this slice; its own diff is audited by construction (measured post-commit in record 18 §4.4) and binds from the next slice on (KB-04 activation)
- - no base-anchored floor for the harness tools yet (the D-035 pattern covers the canonical tools; the next gate, not this slice — P-17)
- - the gate + known-bad matrix arrive with S4b; this slice is verified by the suites + the Proof Sheet re-derivation + the canonical verifier

## Assembly
- sheet sha256 (of the content above, excluding this line): 1b5611d5f3a85cea35d1d492057a1d05b2c35dba1f7885d4fac93700d2b16946
