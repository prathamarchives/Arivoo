# PROOF SHEET — slice claim-047-p3m0b-substrate-declaration-b (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 58733367ef3ddda7615ee9abbbe167984b655837
- generated (last record's timestamp): 2026-10-25T11:18:58.334415+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-25T10:55:56.422642+00:00
- `make verify` -> exit 0 · output sha256 71b270376576d3e9 · 2026-10-25T10:58:49.607473+00:00
- `python3 harness/gate.py --slice claim-047-p3m0b-substrate-declaration-b --diff origin/main` -> exit 0 · output sha256 0b5857823d379104 · 2026-10-25T11:01:32.613141+00:00
- `make verify` -> exit 0 · output sha256 75d7ffa11e5c45b4 · 2026-10-25T11:16:11.507459+00:00
- `python3 harness/gate.py --slice claim-047-p3m0b-substrate-declaration-b --diff origin/main` -> exit 0 · output sha256 fd54136bb963c0f0 · 2026-10-25T11:18:58.334415+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - this slice's change is a comment-only directive declaration, behaviorally inert at its own head: the -- arv-baseline-bump line is read only by P3-M0's oracle (CLAIM-045, landing immediately after) and by the old runner's destructive-statement check — which 0003's text never trips; the observable effect at THIS slice is the checksum change and the rig's ledger re-derivation, nothing else.
- - the directive's justification (0003's CREATE OR REPLACE FUNCTION ... LANGUAGE plpgsql is procedural) is verified mechanically by the landing oracle's own suite (its grammar-refusal cases); until that slice merges, the declaration's READER does not exist on main — the pair is sequenced by the SIZE-005 split, and the oracle slice's suite is the declaration's acceptance proof.
- - the applied-migration checksum boundary (the #80 CodeRabbit Major's disposition, standing): every database in this repo's contract is disposable (FACT-001/D-036); the product's first real deployment bootstraps fresh; ARV-MIG-005 (landing with the oracle) is the class's permanent guard; any out-of-contract persistent DB repairs by the same recorded full-replay procedure.
- - the ARV-SEV-009 undecidable-base regression (the late #79 nitpick) remains routed as its own bounded follow-up — never folded into this slice (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 5fe1038d31a2fa5457ab5f2974e3162dd9f9b82e478e1e7fd45d15aff717568b
- reviewed_diff_sha256: c05e77885f2e2a23081322664bb04b96152bf2ecbdf394e79032bd954371778c
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 74a49150b8a2f5b3ac39ba3f0f7e318c8eb15ddeb4220caacbe34cacb36ddfd1
