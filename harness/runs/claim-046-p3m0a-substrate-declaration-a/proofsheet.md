# PROOF SHEET — slice claim-046-p3m0a-substrate-declaration-a (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 92c43793e71140fa07e7ae3bf0c3e2685c2d2d39
- generated (last record's timestamp): 2026-10-25T10:09:05.723069+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-25T10:01:12.779065+00:00
- `make verify` -> exit 0 · output sha256 27d0e542464f407c · 2026-10-25T10:03:48.800258+00:00
- `python3 harness/gate.py --slice claim-046-p3m0a-substrate-declaration-a --diff origin/main` -> exit 0 · output sha256 0d632ed04fa40ea7 · 2026-10-25T10:06:32.311098+00:00
- `python3 harness/gate.py --slice claim-046-p3m0a-substrate-declaration-a --diff origin/main` -> exit 0 · output sha256 9bc279772cf6a563 · 2026-10-25T10:09:05.723069+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - this slice's change is a comment-only directive declaration, behaviorally inert at its own head: the -- arv-baseline-bump line is read only by P3-M0's oracle (CLAIM-045, landing next) and by the old runner's destructive-statement check — which 0002's text never trips (no DROP TABLE/COLUMN/SCHEMA/TRUNCATE/ALTER-DROP/DELETE-FROM statements); the observable effect at THIS slice is the checksum change and the rig's ledger re-derivation, nothing else.
- - the directive's justification (0002's CREATE OR REPLACE FUNCTION ... LANGUAGE plpgsql is procedural) is verified mechanically by the landing oracle's own suite (its grammar-refusal cases); until that slice merges, the declaration's READER does not exist on main — the pair is sequenced by the SIZE-005 split, and the oracle slice's suite is the declaration's acceptance proof.
- - the ARV-SEV-009 undecidable-base regression (the late #79 nitpick) remains routed as its own bounded follow-up — never folded into this slice (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 44b397fcbe99bbb6420ded7fed3dd0be8c1f876b604508ece1f843a0d4eaad2c
- reviewed_diff_sha256: 926d5dad29722c763ab8c768a1aebda57227e76eb2caf95c8b5c6204df2eb85f
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 2

## Assembly
- sheet sha256 (of the content above, excluding this line): 279c5d214f5cd036f9ec95bf66448037267add685514abac34f8d2b2e923f0bd
