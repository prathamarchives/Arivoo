# PROOF SHEET — slice claim-047-p3m0b-substrate-declaration-b (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 8492721fa7a985b779a645f0f27ca1b2607fce36
- generated (last record's timestamp): 2026-10-25T11:01:32.613141+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-25T10:55:56.422642+00:00
- `make verify` -> exit 0 · output sha256 71b270376576d3e9 · 2026-10-25T10:58:49.607473+00:00
- `python3 harness/gate.py --slice claim-047-p3m0b-substrate-declaration-b --diff origin/main` -> exit 0 · output sha256 0b5857823d379104 · 2026-10-25T11:01:32.613141+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - this slice's change is a comment-only directive declaration, behaviorally inert at its own head: the -- arv-baseline-bump line is read only by P3-M0's oracle (CLAIM-045, landing immediately after) and by the old runner's destructive-statement check — which 0003's text never trips; the observable effect at THIS slice is the checksum change and the rig's ledger re-derivation, nothing else.
- - the directive's justification (0003's CREATE OR REPLACE FUNCTION ... LANGUAGE plpgsql is procedural) is verified mechanically by the landing oracle's own suite (its grammar-refusal cases); until that slice merges, the declaration's READER does not exist on main — the pair is sequenced by the SIZE-005 split, and the oracle slice's suite is the declaration's acceptance proof.
- - the applied-migration checksum boundary (the #80 CodeRabbit Major's disposition, standing): every database in this repo's contract is disposable (FACT-001/D-036); the product's first real deployment bootstraps fresh; ARV-MIG-005 (landing with the oracle) is the class's permanent guard; any out-of-contract persistent DB repairs by the same recorded full-replay procedure.
- - the ARV-SEV-009 undecidable-base regression (the late #79 nitpick) remains routed as its own bounded follow-up — never folded into this slice (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 2902b31a41737c720bc2b741830d3a615ab326584f65468fa6c82d62b36574ff
- reviewed_diff_sha256: 13e35aea97de77ba99e09096aad6c8a78175152a308e2e7240250c78477da230
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 17f63408435d633e7f3a74d289fa094cb04c14c14934eb4811857acc5869ba97
