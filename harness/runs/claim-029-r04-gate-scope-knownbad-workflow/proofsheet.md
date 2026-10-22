# PROOF SHEET — slice claim-029-r04-gate-scope-knownbad-workflow (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): d7ea94e144bfc36bf4ac61fe318608afac8879fd
- generated (last record's timestamp): 2026-10-22T16:35:34.099795+00:00
- run records: 10

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T16:34:10.745436+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T16:34:11.096906+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T16:34:12.930384+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 2e151a121d457426 · 2026-10-22T16:34:28.902870+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 a8634cd9c776a3a5 · 2026-10-22T16:34:41.709143+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 9f989735fbbbfa55 · 2026-10-22T16:34:43.289907+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 f43414a5e6384c4e · 2026-10-22T16:34:43.610027+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-22T16:34:50.099408+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 aabc93119fb178b6 · 2026-10-22T16:34:50.254422+00:00
- `make verify` -> exit 0 · output sha256 b9704e66ffe80ecd · 2026-10-22T16:35:34.099795+00:00

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
- - - no fresh technical verifier and no SEV — the pre-H-02 discipline (H-02 is the next-but-one card: the ledger one-liner
- slice, then H-01c-authority/evidence, then H-02's activation)

## Assembly
- sheet sha256 (of the content above, excluding this line): 06cd41b2d741ad433664e7e6749eb0f9a62c451b426972ba288a6a13bf786ce1
