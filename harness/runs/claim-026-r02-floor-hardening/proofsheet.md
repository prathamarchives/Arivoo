# PROOF SHEET — slice claim-026-r02-floor-hardening (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 91cbad9ec039d7cf185df5e9542f3919a67b66eb
- generated (last record's timestamp): 2026-10-20T17:23:19.813511+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 c738a1d358389965 · 2026-10-20T17:22:36.476585+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-20T17:22:36.821036+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-20T17:22:39.231819+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 260cbc11f7b5e813 · 2026-10-20T17:22:39.425272+00:00
- `make verify` -> exit 0 · output sha256 869c3b54b6ea2741 · 2026-10-20T17:23:19.813511+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the growing-file budget race (G-47-7's live form: a file APPENDED between lstat and read) is untestable deterministically at suite speed — the repair (the total budget charges bytes ACTUALLY READ, post-read) is correct by construction and the class is fail-closed (the per-file cap at read time); stated here per LAW-04, never fake-tested
- - the finally-return's suppression of non-FloorRefusal machinery errors is now CONVERTED to a named ARV-FLOOR-006 RED (the #61 review's class fix); the residual that remains: the crash's OWN traceback is not captured into the manifest — the class name is, the traceback is not (fail-closed held in the observed incident: the Popen TypeError surfaced as RED, never green)
- - RLIMIT_NPROC's value (256) is reasoned, not tuned: whole-UID semantics mean the cap must clear a runner's legitimate baseline (observed single-digit in this env) while killing fork bombs in their first milliseconds; the cap clamps to the inherited hard limit; a busy shared-UID host could still see EAGAIN in the child's legitimate spawns — that boundary is stated, CI's dedicated runners are the design point
- - test_20's walk-error case cannot engage under root (CAP_DAC_OVERRIDE) — the test skips under root with the reason stated (#61 review); the CI runners are non-root, the case engages there
- - no fresh technical verifier and no SEV — the pre-H-02 discipline

## Assembly
- sheet sha256 (of the content above, excluding this line): c45141259ff0875715efa2932e3ffcd16a96d94069016ffedd23ff0106e22fbd
