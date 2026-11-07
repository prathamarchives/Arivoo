# PROOF SHEET — slice claim-070-p4c-library-reading-state (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): d3b47caf4c7feb6c129f479a6445931e986183db
- generated (last record's timestamp): 2026-11-07T06:01:57.908872+00:00
- run records: 8

## Run records (command, exit, output digest)
- `python3 harness/tests/test_library.py` -> exit 0 · output sha256 c1f1435d34119a21 · 2026-11-07T05:15:36.925949+00:00
- `python3 harness/tests/test_library.py` -> exit 0 · output sha256 c1f1435d34119a21 · 2026-11-07T05:15:42.895431+00:00
- `python3 harness/tests/test_library.py` -> exit 0 · output sha256 c1f1435d34119a21 · 2026-11-07T05:15:48.910106+00:00
- `make verify` -> exit 0 · output sha256 c7e759e36d959f90 · 2026-11-07T05:21:54.491744+00:00
- `make verify` -> exit 0 · output sha256 2c7beb6536d3af65 · 2026-11-07T05:28:18.548772+00:00
- `env SLICE=claim-070-p4c-library-reading-state GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 f8ebeec80f53a955 · 2026-11-07T05:59:03.472471+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-070-p4c-library-reading-state python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 1 · output sha256 1bc8d429ce8fde41 · 2026-11-07T05:59:29.542728+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-070-p4c-library-reading-state python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 61632878222cc7b5 · 2026-11-07T06:01:57.908872+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-070 / P4-C slice one (the library +
- current-reading state over the existing substrate; LAW-04; never
- empty-by-omission).
- WHAT THIS SLICE PROVES: the library membership list (query.py list-library —
- the owner's imported sources as a stable, bounded, paginated list on the
- P4-00b contract; membership IS the arv.source set — rows BORN complete at
- import, the failed import's dead-letter is the journal's, never the
- library's) + the current-reading state (query.py get-reading-state — the
- derived reading surface over the LANDED position rows: every source with its
- last-saved position + the generation binding honest across a re-extraction,
- or the typed no_position_saved state; every row get-position's own answer
- through the ONE shared _position_row builder — the no-second-path law, held
- structurally and pinned behaviorally at exact JSON equality) + the owner
- isolation through RLS + the no-new-table law + the reserved-surface registry
- row (owner_phase P4-C, the reader-client exclusion held).
- THE HONEST LIMITS (including the SEV round's five P3 notes, routed/recorded —
- never silently dropped):
- 1. NO CONCURRENCY OBSERVATION FOR THE DERIVED VIEW (SEV round 1, the
- standing record-47 §9 class): two interleaved get-reading-state walks
- with a mid-walk save (page-boundary races) are untested; the contract
- pins ONE-snapshot-per-page semantics, never cross-page consistency. The
- same class the earlier list arms carry.
- 2. THE FAILED/BUILDING EXTRACTION STATES NEVER EXERCISED AGAINST
- GET-READING-STATE (SEV round 1): only healthy and re-extracted
- generations were probed, so the current_generation_id="" +
- generation_matches=false shape for a source with NO serving generation
- (all generations failed/building) is unpinned by suite and probes alike —
- the row shape is the SQL's own COALESCE-'' form, never an observed
- answer.
- 3. SCALE UNTESTED ON THE NEW ARMS (SEV round 1): at most five sources were
- present, so the default page (100), the 1000 bound at real volume, and
- the correlated-subquery plan/latency of READING_SQL at real library
- scale are unmeasured. The default-limit value itself is pinned only
- INDIRECTLY (structurally shared with the frozen arms through
- DEFAULT_LIST_LIMIT; BND-05 pins it exactly on the older arms — a drift
- breaks those pins, not this suite's).
- 4. RLS EXERCISED ONLY THROUGH arv_app (SEV round 1): the arv_read
- bypass-auditor's view of the two new arms (and any audit use of them)
- was not probed.
- 5. THE READER-CLIENT CONSUMPTION CONTRACT IS INVISIBLE HERE (the slice's
- own bounded exclusion): nothing verifies how P4-B's separate repo will
- page, render, or reconcile the more=/keyset cursors against these arms.
- 6. THE NO-DRIFT PIN COMPARES PARSED JSON DICTS, NOT RAW BYTES (SEV round
- 1): byte equality was verified in the round's own probes and by the
- shared print path (one builder, one serializer); a future divergence in
- serialization ORDER alone would pass LIB-04 undetected.
- 7. THE PIN-WEAKER-THAN-PROSE NOTES (SEV round 1, F2/F3): LIB-02 pins the
- typed bounds refusal's FAIL line + exit + zero-effect but not the
- repair-hint line's presence (the reviewer probed all 16 malformed
- combos live — every one prints it); the default page size is indirectly
- pinned (note 3). The substance holds; the pins are one line short of
- the prose.
- 8. THE make verify OUTPUT DIGEST IS NOT BYTE-DETERMINISTIC (SEV round 1,
- F4): the full gate output varies between runs (timestamps, scratch-db
- names); the run records' output_sha256 for make-verify attests exit +
- content class, not bit-reproducibility. The LIB suite digest IS
- byte-reproducible (the reviewer's fresh run matched run-01..03 exactly).
- 9. THE --after CURSOR ACCEPTS EVERY uuid.UUID FORM (SEV round 1, F5):
- braced/urn/no-hyphen/uppercase spellings all normalize to the canonical
- form before interpolation (safe, no injection — the interpolation only
- ever sees str(uuid.UUID(...))), wider than the strict hyphenated
- spelling; the typed refusal still fires for non-uuid garbage.
- 10. THE STANDING RESIDUALS (unchanged from the prior slices): the OS/
- process-level separation and host-level workflow protection (Q10) are
- outside the harness's observability; the isolation undecidable classes
- documented at the substrate suite stand.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 9ec6e89346fa2f69dbad99a8d5f5336abbfeea2a1e772ec165c86523b529fecc
- reviewed_diff_sha256: db023430a5d2d6944367330846a4fc1598d882a46060fb8fb578186641909516
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): fb6ef4ae21aea3d68c195165653b10992203ebd82ba84748d753448221dbe2e9
