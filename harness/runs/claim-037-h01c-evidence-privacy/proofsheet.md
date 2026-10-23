# PROOF SHEET — slice claim-037-h01c-evidence-privacy (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 948b37d1300c6c9f092fc9fc9a2964dca06cf709
- generated (last record's timestamp): 2026-10-23T14:47:36.716592+00:00
- run records: 22

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-23T14:10:48.192175+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-23T14:10:48.533898+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-23T14:10:54.773242+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 86b36062c4f3999f · 2026-10-23T14:11:17.734731+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 5dd0398fd1581882 · 2026-10-23T14:11:38.148454+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 bfd3cfe45edab3ca · 2026-10-23T14:11:40.533245+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 c0648c34d4dc713a · 2026-10-23T14:11:46.457699+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 2d9c17a22fa36a17 · 2026-10-23T14:11:46.579546+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 a6fa0c273defa14e · 2026-10-23T14:11:53.876359+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 1f8b9cee7c15f090 · 2026-10-23T14:11:54.033834+00:00
- `make verify` -> exit 0 · output sha256 502b5e1d54489186 · 2026-10-23T14:12:50.133253+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-23T14:45:24.195812+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-23T14:45:24.621036+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-23T14:45:27.161240+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 d67e012ae408d78d · 2026-10-23T14:45:55.439817+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 f7df010bc672d49c · 2026-10-23T14:46:18.904248+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 dc4d7f40d8dbf775 · 2026-10-23T14:46:24.664816+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 2f6980ce2b2b7801 · 2026-10-23T14:46:24.979775+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 7406b9554f3b6ac4 · 2026-10-23T14:46:25.233897+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 88f9dc925e52cd8e · 2026-10-23T14:46:29.210519+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 38ae33a60365cce0 · 2026-10-23T14:46:29.380879+00:00
- `make verify` -> exit 0 · output sha256 b2cb4950aa93e911 · 2026-10-23T14:47:36.716592+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- not verified (LAW-04 — the CLAIM-037 honest limits):
- - ARV-RED-006's chain proves the typed amendments bridge the TRUSTED PRIOR digest to the
- current form; whether a bridged change is DESIRABLE is the review layer's judgment (the
- diff is review-visible; the walls serialize the merge) — the same honest limit as VER-805's
- section-8 register (the form is mechanical, the genuineness is reviewed).
- - the typed observed-red (red_exit/red_code) validates the OBSERVATION'S FORM and the
- binding's GIT TRUTH; the historical observation itself is a claim about the past — the
- binding proves the revision carries the recorded content, never that the run happened.
- The two smash-class records carry red_unrecovered (honestly lost, never fabricated).
- - the binding verification runs in every git context (local, CI, the trusted job); the KB
- probe copies are non-git by construction (.git ignored) — there the binding degrades to a
- printed NOTE (stated per-probe); the CI trusted job always runs in a git context.
- - a true two-process make-red race was not deterministically testable in the suite — the
- changed-since-read guard (ARV-RED-009) is exercised through a deterministic mid-flight
- mutation hook, and the write itself is atomic (tmp+os.replace, no torn file possible);
- the surviving race window (two writers past the guard simultaneously) is a stated
- residual of the single-writer protocol, refused fail-closed by the re-read.
- - the canary-redaction + A16-narrowing cluster is CLAIM-038 (part 2 of the card) — routed,
- not silently claimed here.
- - THE LAW-05 SPLIT (the size refusal's own repair, observed at the PR gate: 467 source lines
- > 400): the proof-record numbering rider (proofsheet.py's max-based repair + ARV-PRF-006 +
- the machinery suite's cases 1/2/5) ROUTED to the part-2 claim — its RED stays observed in
- this slice's red-01/red-02 (the overwrite, the stall, the unparseable context, the run-100
- boundary); the defect remains at the predecessor's count-based form in main until the
- part-2 claim lands, never silently fixed here (the size law's own repair: split the slice).

## Assembly
- sheet sha256 (of the content above, excluding this line): 83eb1921e50784a551004b0f64496a5f573e484c8878676e7e13716c2768a40b
