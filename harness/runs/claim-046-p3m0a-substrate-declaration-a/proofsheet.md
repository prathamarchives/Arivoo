# PROOF SHEET — slice claim-046-p3m0a-substrate-declaration-a (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): c8a1b1a5fb3725c734e8a3bf6830dc9e367b6d00
- generated (last record's timestamp): 2026-10-25T10:41:46.400505+00:00
- run records: 7

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-25T10:01:12.779065+00:00
- `make verify` -> exit 0 · output sha256 27d0e542464f407c · 2026-10-25T10:03:48.800258+00:00
- `python3 harness/gate.py --slice claim-046-p3m0a-substrate-declaration-a --diff origin/main` -> exit 0 · output sha256 0d632ed04fa40ea7 · 2026-10-25T10:06:32.311098+00:00
- `python3 harness/gate.py --slice claim-046-p3m0a-substrate-declaration-a --diff origin/main` -> exit 0 · output sha256 9bc279772cf6a563 · 2026-10-25T10:09:05.723069+00:00
- `make verify` -> exit 0 · output sha256 bbf97c112dcf5154 · 2026-10-25T10:28:13.213930+00:00
- `python3 harness/gate.py --slice claim-046-p3m0a-substrate-declaration-a --diff origin/main` -> exit 1 · output sha256 fcab190e9267e7cd · 2026-10-25T10:30:43.539133+00:00
- `python3 harness/gate.py --slice claim-046-p3m0a-substrate-declaration-a --diff origin/main` -> exit 0 · output sha256 e6672bb114288f9e · 2026-10-25T10:41:46.400505+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - this slice's change is a comment-only directive declaration, behaviorally inert at its own head: the -- arv-baseline-bump line is read only by P3-M0's oracle (CLAIM-045, landing next) and by the old runner's destructive-statement check — which 0002's text never trips (no DROP TABLE/COLUMN/SCHEMA/TRUNCATE/ALTER-DROP/DELETE-FROM statements); the observable effect at THIS slice is the checksum change and the rig's ledger re-derivation, nothing else.
- - the directive's justification (0002's CREATE OR REPLACE FUNCTION ... LANGUAGE plpgsql is procedural) is verified mechanically by the landing oracle's own suite (its grammar-refusal cases); until that slice merges, the declaration's READER does not exist on main — the pair is sequenced by the SIZE-005 split, and the oracle slice's suite is the declaration's acceptance proof.
- - the ARV-SEV-009 undecidable-base regression (the late #79 nitpick) remains routed as its own bounded follow-up — never folded into this slice (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 378bb875fb38538850167e3b55cb0a6dbe1662cd0273c71449280502d02b5d0c
- reviewed_diff_sha256: d08fcc975c042b19212dcd5d59b2e9bcd1bff9cd777ac45c261368cca615deb2
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 2

## Assembly
- sheet sha256 (of the content above, excluding this line): 0a0db29c00aaeaff4b2d41689fedc36a367f4e4ba258de2f95b0b7d5bfd26b7b
