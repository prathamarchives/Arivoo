# PROOF SHEET — slice claim-029-r04-gate-scope-knownbad-workflow (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): a62a8fa2de7974105c3c1ae88db4b2b8fde0ac94
- generated (last record's timestamp): 2026-10-22T16:15:11.469769+00:00
- run records: 10

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-22T16:13:46.840836+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-22T16:13:47.212587+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-22T16:13:49.251788+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 18876b0cab587a41 · 2026-10-22T16:14:04.098388+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 1550cce29bce20a3 · 2026-10-22T16:14:16.804348+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 c8cd4165138ac753 · 2026-10-22T16:14:18.476853+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 71b9180f20e6811a · 2026-10-22T16:14:18.810464+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 912813bf36889c80 · 2026-10-22T16:14:24.751830+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 aabc93119fb178b6 · 2026-10-22T16:14:24.901454+00:00
- `make verify` -> exit 0 · output sha256 076bc15b826ab21d · 2026-10-22T16:15:11.469769+00:00

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
- sheet sha256 (of the content above, excluding this line): 6a29c178e0cbf504439158934a7faca7c96d87e6c3179e961ab46eca80f696a7
