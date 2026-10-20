# PROOF SHEET — slice claim-018-h01b-ci-trusted-driver (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 5bd6517c85420f35e9f6cd72a44a31fc92468206
- generated (last record's timestamp): 2026-10-20T13:40:34.416115+00:00
- run records: 3

## Run records (command, exit, output digest)
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 f1379530cbbd1285 · 2026-10-20T13:39:40.258401+00:00
- `make verify` -> exit 0 · output sha256 cca80f2d93e703b5 · 2026-10-20T13:40:21.431639+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 21467a77e115f84b · 2026-10-20T13:40:34.416115+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the CI harness job's TRUSTED steps (S1b/S4c) are NOT yet bound — this slice lands the DRIVER and the machinery re-rooting only; the workflow binding is part 2 (the next slice) because at THIS PR head the base (main) carries no tools/trusted_gate.py and the anchor step would fail here (the CLAIM-013 activation chicken-and-egg, record 22 §8). Until part 2 merges, F-004's recipe-delegation exposure stands as documented — never claimed closed by this slice alone
- - the -I flip and the shim removal are part 2 with the same reasoning; the flip's safety is proven locally (test_10's anchored -I launch since CLAIM-013; the whole trusted_gate suite runs its driver under -I; the four anchored tools are stdlib-only and the driver loads base machinery by absolute path)
- - the KB probes' module-bytes trust routing is proven against the synthetic stubs (all 13 fire; the hostile candidate registry never executes — test_06); the in-process tampering envelope of the trusted gate itself is the documented same-user/same-host residual (a candidate harness module could tamper with the driver process through the probes' DATA if it could execute — it cannot load at all now; the gate's process boundary remains the floor's design, never a sandbox claim)
- - the pull_request workflow-definition trust boundary (F-003) is structural and EXTERNAL: GitHub has no repository setting that stops a pull_request event from using the merge-ref workflow file. Observed settings (recorded, never set by the agent): workflow token permissions read-only + cannot-approve-PRs; branch protection three required checks, strict, admins included. The remaining external item is owner process on workflow-file edits (review discipline), recorded in the record — never claimed fixed
- - the suites phase's completion semantics cover existence + exit code + non-empty output (the A03 vacuous class); a candidate suite that prints fabricated output while exiting 0 is the two-sided floor's problem (the mutation floor + the canonical judge carry that side), stated — the driver is the SELECTION and EXECUTION authority, not the verifier-content oracle

## Assembly
- sheet sha256 (of the content above, excluding this line): e9242e4074063c4b623137369405fa82c291bfaa49b768ff0c166b0401a1db85
