# PROOF SHEET — slice claim-065-p4a-format-intake-json (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 2f33f70303248d7b72178403aaa7aaf54673c9a6
- generated (last record's timestamp): 2026-11-06T08:53:21.177284+00:00
- run records: 12

## Run records (command, exit, output digest)
- `python3 harness/tests/test_format.py` -> exit 0 · output sha256 1dfb3f0631cb93ae · 2026-11-06T07:47:58.922192+00:00
- `python3 harness/tests/test_format.py` -> exit 0 · output sha256 1dfb3f0631cb93ae · 2026-11-06T07:48:00.236744+00:00
- `python3 harness/tests/test_format.py` -> exit 0 · output sha256 1dfb3f0631cb93ae · 2026-11-06T07:48:01.547630+00:00
- `make verify` -> exit 0 · output sha256 ef6d8c3d969965fb · 2026-11-06T07:53:18.594842+00:00
- `make verify` -> exit 0 · output sha256 0513f60d3b617276 · 2026-11-06T07:58:38.256493+00:00
- `make verify` -> exit 0 · output sha256 313c58ed2ecd2d0d · 2026-11-06T08:25:29.676877+00:00
- `python3 harness/tests/test_format.py` -> exit 0 · output sha256 1dfb3f0631cb93ae · 2026-11-06T08:32:46.403583+00:00
- `python3 harness/tests/test_format.py` -> exit 0 · output sha256 1dfb3f0631cb93ae · 2026-11-06T08:32:47.752102+00:00
- `python3 harness/tests/test_format.py` -> exit 0 · output sha256 1dfb3f0631cb93ae · 2026-11-06T08:32:49.077437+00:00
- `make verify` -> exit 0 · output sha256 821efce78ae7cb13 · 2026-11-06T08:37:43.661969+00:00
- `SLICE=claim-065-p4a-format-intake-json GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 779f9f4d76300db6 · 2026-11-06T08:52:04.847032+00:00
- `ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-065-p4a-format-intake-json python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 d623ab9fa7a7c793 · 2026-11-06T08:53:21.177284+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-065 / P4-A slice one (the first
- additional format intake: JSON by the durability ladder; LAW-04; never
- empty-by-omission).
- WHAT THIS SLICE PROVES: a format is intake-supported only through the one
- durability ladder, and every failure is a named, typed, zero-effect refusal
- whose staged bytes survive. The adapter registry (harness/formats.py — ONE
- home: the capability matrix derives from it): the approved reading formats
- text/plain + application/json (native text, reflow, the extractor named);
- the BYTES PASSTHROUGH (application/octet-stream — the landed P3-02/EXT-03
- contract: opaque binaries import durably, the readable-text boundary stays
- at extraction's ARV-EXT-002, never a matrix row). The typed refusals:
- ARV-FMT-001 (the unsupported type — refused at the boundary after the
- MIME-grammar check, zero effect, now ASSERTED by the source-count
- equality); ARV-FMT-002 (the malformed payload — after the blob staging,
- the journal failed-retryable, the refusal NAMING the digest, the blob
- answering — the staged-bytes contract verified by the suite's own blob
- probes); ARV-FMT-003 (the undecodable/encrypted payload — the digest
- named, the bytes recoverable). The JSON intake measured through the
- existing ladder (the ack's full frozen contract; the SECOND matrix row
- measured over its own corpus). The two-round fresh-context SEV chain:
- round 1 (agent-6aee153a) PASS zero open P0/P1/P2 with two repair-in-slice
- P3s (both applied: the CAP-009 hint's stale example; the zero-effect arm
- asserted); round 2 (agent-64ccdcc2) FINAL PASS — both repairs verified
- live, the adversarial probes coherent (the replay/409/empty-file arms, the
- follow-the-hint loop terminating).
- THE HONEST LIMITS (what this slice does NOT claim):
- 1. THE STRICT-JSON EDGES (round-1 F3, accepted-with-note): a BOM'd JSON
- document and an empty JSON file both refuse ARV-FMT-002 (the digest
- named, the exact bytes recoverable) — strict by design; a BOM-tolerant
- reader is a later format-increment's call, never silently assumed.
- 2. THE FAILED-INTAKE SEMANTICS (round-1 F4, verified identical to the
- landed CAP-004 pattern): a same-key+same-bytes retry rewinds the
- journal row and re-refuses; a same-key+fixed-payload retry is the
- ARV-CMD-409; a NEW key lands the fixed payload; the recovery window
- ends at the orphan sweep.
- 3. THE CASE-SENSITIVE REGISTRY (round-1 F5, the accepted-as-designed
- narrowness class): Application/JSON refuses ARV-FMT-001 — the
- claim-049 class, never a silent case-fold.
- 4. THE TEXT/PLAIN+NON-UTF-8 NARROWING (round-1 F6, disclosed): the
- pre-P4-A class that committed non-UTF-8 bytes AS text/plain now refuses
- ARV-FMT-003 at intake — the honest route for opaque bytes is the
- octet-stream passthrough (verified end-to-end: import durably, extract
- refuses ARV-EXT-002, capture refuses ARV-CAP-008 — the BMK-02
- amendment's disclosed form).
- 5. THE RUN-RECORD PROVENANCE (the standing class): run-01..05's commit
- fields name the then-HEADs while the measured working trees carried the
- respective GREEN/repair content uncommitted; the substance re-verified
- at the committed final tree by SEV round 2 and by run-06..09 (the
- final-tree records).
- 6. THE PROVENANCE NIT (round 2's note, disclosed): the repair commit's
- message cites round 1 as agent-6aee153a (the task-launch label) while
- the round-1 report self-labels agent-481321aa — the same execution,
- two labels; cosmetic.
- 7. THE STANDING LIMITS: no EPUB (the second increment), no PDF (the
- scan/OCR + fixed-layout classes — their own increments under the Q8
- corpus gate), no reader-client work (P4-B's repo); the position surface
- is P4-A slice two; the CI run is authoritative at PR time; the
- fresh-context labels are not cryptographic independence (ARV-SEV-007);
- Q6-Q12 and D-014 stand open at their recorded scopes.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: f9642157b2569a6313ce2ba8f68064d451d472f30321c04161cceabfec497603
- reviewed_diff_sha256: 2e207fe7d9e5c3d4a3f13e22389e845e83827546ffe890f75eee840f3bb4cb3c
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 39df2d98a79e56c4b499cbba03c69d073a22ea3335b5cb0d4eb301833d2c6ab6
