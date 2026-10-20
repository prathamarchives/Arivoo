# PROOF SHEET — slice claim-012-h01b-runner (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 114e026601ab5acc098ec375c678dc542cb0fca8
- generated (last record's timestamp): 2026-10-20T09:05:19.882237+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 47138eefef831252 · 2026-10-20T09:01:04.881541+00:00
- `python3 harness/claims.py` -> exit 0 · output sha256 6beec6ef5d385ac5 · 2026-10-20T09:01:04.950468+00:00
- `make verify` -> exit 2 · output sha256 3d6954205d1ec1fd · 2026-10-20T09:01:19.756714+00:00
- `make verify` -> exit 0 · output sha256 2304877097447700 · 2026-10-20T09:05:19.882237+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the module is INERT in this slice by construction — no repo code imports it yet; its BEHAVIOR (the bounded fixtures, the integrity refusals, the child protocol, the manifest validation) is proven by CLAIM-013's activation suite (16 cases, red-first at the true predecessor e1ef3a0 — the red evidence rides the activation slice), never by this PR's green runs
- - the CI-side anchored launch (python3 -I + ARV_FLOOR_BASE_TOOLS + the runner added to the anchor copy list) lands with CLAIM-013's verify.yml change; this PR touches no workflow
- - the residual boundary text lives in the module and is asserted by CLAIM-013's test_13; the fake-fail two-sided-floor dependency (D-035) is documented there
- - no fresh technical verifier and no SEV — the pre-H-02 discipline (the record-20 §8 honest gap)
- - the KB matrix caught its own probe's live-registry coupling DURING this slice (the make-verify run record with exit 2 is preserved in the proof sheet): the moment the rescope legitimately dropped context/extracted/ from the only OPEN claim, KB-CLM-002 lost its overlap partner and reported a broken guard — the A11 probe-coupling class, third occurrence; repaired in-slice by giving the probe a SYNTHETIC partner row (self-contained forever), the fix recorded in the case file's own text

## Assembly
- sheet sha256 (of the content above, excluding this line): caf40663599f18c172844f7ed558c167c36570a07469f6858000a305a973b5e1
