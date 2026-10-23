# PROOF SHEET — slice claim-036-h01c-authority-raw-lineage (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 52aca28f866df2531fbcf228986864a9685eb02f
- generated (last record's timestamp): 2026-10-23T13:29:28.302092+00:00
- run records: 23

## Run records (command, exit, output digest)
- `python3 harness/tests/test_gate_dispatch.py` -> exit 1 · output sha256 69aa2ef138fc1203 · 2026-10-23T12:51:52.819584+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-23T12:58:31.329522+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-23T12:58:37.380932+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-23T12:58:43.661465+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 0efd1844f6e579b1 · 2026-10-23T12:59:06.398405+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 59575ef775daa0d1 · 2026-10-23T12:59:28.510820+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 690b3222ff857264 · 2026-10-23T12:59:34.689870+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 3240b5485b21f0ad · 2026-10-23T12:59:39.166607+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-23T12:59:46.916820+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 1f8b9cee7c15f090 · 2026-10-23T12:59:53.635005+00:00
- `timeout 900 python3 tools/verify_selftest.py` -> exit 0 · output sha256 a6e6530904683884 · 2026-10-23T13:00:12.279885+00:00
- `make verify` -> exit 0 · output sha256 91653d046bcee987 · 2026-10-23T13:00:58.873724+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-23T13:27:19.755624+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-23T13:27:23.651776+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-23T13:27:28.277716+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 23d85b7b9f735af7 · 2026-10-23T13:27:46.716982+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 22d949e47bf913a7 · 2026-10-23T13:28:07.434671+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 5091e946cdcc2f3e · 2026-10-23T13:28:12.099614+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 f94038838c28278b · 2026-10-23T13:28:15.327712+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-23T13:28:22.400409+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 1f8b9cee7c15f090 · 2026-10-23T13:28:25.477542+00:00
- `timeout 900 python3 tools/verify_selftest.py` -> exit 0 · output sha256 6494530e839d9663 · 2026-10-23T13:28:40.010860+00:00
- `make verify` -> exit 0 · output sha256 3b5d97301169da22 · 2026-10-23T13:29:28.302092+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- not verified (LAW-04 — the H-01c-authority slice's honest limits):
- - VER-805 validates the reanchor row's FORM and the authorization reference's RESOLVABILITY;
- the authorization's GENUINENESS is the review layer's judgment (D-042 + the owner's merge
- authority through the walls) — never a mechanical claim (the §8 register's honest-limit note).
- - the trust chain rests on the canonical-layer CI job running the BASE-ANCHORED judge
- (verify.yml's anchored copies, sha256-verified against main); the host-level
- workflow-definition protection remains H-01b-CI's EXTERNAL item (owner/admin settings,
- recorded never claimed, unchanged); Q10 (token/workflow-tamper hardening) stays owner-gated.
- - the floor's residual boundaries unchanged: the same-user/same-host child, the re-sessioning
- daemon class, the manifest-as-record-not-vault (stated in every floor output, never claimed
- closed).
- - NO raw-file edits (the card's explicit rule): every mutation ran on the disposable fixture;
- the real corpus is byte-unchanged (VER-802/805 green over the real tree).
- - the pushed head's own walls verification is the GitHub five-check run, observed in the PR —
- no in-file result covers the pushed head itself (INT-104).
- - the #71 review round's own honest limits: the anchored authorization resolution proves an
- ACTUAL entry header / decision row exists with the cited ID; whether that entry actually
- authorizes THIS raw change remains the review layer's judgment (unchanged). The three
- fix-probes (118/118 headers, 7/7 designated rows, 5/5 short fragments validate) were run on
- the real tree BEFORE the fixes landed — recorded in the round's commits, not separately
- re-pinned as artifacts. CodeRabbit's Minor on the designated-block hole confirmed Greptile's
- P2 (one finding, two bots) — dispositioned as such, never counted twice.

## Assembly
- sheet sha256 (of the content above, excluding this line): 205b5a7c7acc612bd330abe64bed6ea64cba376d20b12afbb108544535c48f52
