# PROOF SHEET — slice claim-029-r04-gate-scope-knownbad-workflow (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 688917f0c3af7263bc09992180f23648b0827083
- generated (last record's timestamp): 2026-10-22T16:52:57.895599+00:00
- run records: 10

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T16:51:38.945562+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T16:51:39.308888+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T16:51:41.192550+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 bdcf4e9c89e246a3 · 2026-10-22T16:51:56.559913+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 19136a855547dd33 · 2026-10-22T16:52:07.716609+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 e268826c5dc33895 · 2026-10-22T16:52:09.159915+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 78585cdc7fb559c8 · 2026-10-22T16:52:09.454512+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-22T16:52:15.826784+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 aabc93119fb178b6 · 2026-10-22T16:52:15.976172+00:00
- `make verify` -> exit 0 · output sha256 fa4a1390f6498a6b · 2026-10-22T16:52:57.895599+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - not verified (LAW-04 — required, never empty-by-omission; the R-04 slice's honest limits):
- - - the bytes-mode identity assumes the same-host filesystem-encoding round-trip (os.fsdecode/os.fsencode with
- surrogateescape): the byte-identity preservation is proven on UTF-8-locale Linux (CI ubuntu-latest and this rig) — a
- non-UTF-8 filesystem locale is the same-host/same-OS residual the OS-round-trip contract already states; the identity
- contract itself (byte-in == byte-out) is what the regressions pin
- - - the 1500-character tail bound on the ARV-TG-003 refusal is bounded-by-choice, not measured-against-observed-suite-output:
- it is large enough for a unittest traceback head and small enough to bound hostile floods; if a future suite's named
- failure lands beyond 1500 chars the truncation marker states it — a larger bound is a one-line amendment, never silently
- re-chosen
- - - the P1/P2/P3 discriminating-power/latent-vacuity proofs (red-01.txt) are SCRATCH-COPY evidence: the regressed driver, the
- reconciled registry, and the sibling-prefix defect were each realized on disposable copies, never committed artifacts; the
- committed regressions pin the POSITIVE side (the fixed shapes refuse/pass for the named reasons), the scratch side proves
- the OLD shapes could not
- - - KB-SCOPE-006's positive-side guard prints ARV-SCOPE-006 (over-refusal) through the captured channel and the case then
- fails via the expected-code-absent path (the honest broken-guard direction); the KB driver itself only knows the
- expected-code protocol — a dedicated over-refusal case type remains a possible H-01c-evidence refinement, not silently
- assumed
- - - S4c's `!cancelled()` semantics are pinned by parsing the workflow artifact (test_09) and by the GitHub Actions
- documented step-scheduling behavior; the LIVE end-to-end proof (a genuinely red S4b on a real PR with S4c still running)
- is observed only if such a PR occurs — no synthetic PR was fabricated to force it
- - - the #64 second review round's TOCTOU residual (CodeRabbit Major, CWE-367, PRE-EXISTING at the merge base): the
- harness job runs candidate-controlled code (S1's health.py, S1b's suite subprocesses, S4b) in the same writable
- workspace BEFORE the trusted S4c step, so the base/harness machinery remains tamperable after the anchor check;
- R-04's in-PR hardening re-verifies only the ANCHORED DRIVER's digest at S4c entry (the direct swap channel refuses) —
- the structural isolation (the R-06 card: an isolated fresh-checkout trusted job) is NOT built and NOT claimed
- - - no fresh technical verifier and no SEV — the pre-H-02 discipline (H-02 is the next-but-one card: the ledger one-liner
- slice, then H-01c-authority/evidence, then H-02's activation)

## Assembly
- sheet sha256 (of the content above, excluding this line): dbd80755af5203c0be64bbc119398270faafe28f3a7df2760cb76da88fd4b5e2
