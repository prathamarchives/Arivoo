# PROOF SHEET — slice claim-053-p303b-anchor-resolution-q8-spike (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 0bea5d956a35e8dc976cb6a7d7f2a283661b663b
- generated (last record's timestamp): 2026-10-27T15:52:33.027165+00:00
- run records: 23

## Run records (command, exit, output digest)
- `python3 harness/tests/test_anchor.py` -> exit 0 · output sha256 6524242680a49821 · 2026-10-27T12:19:15.431832+00:00
- `python3 harness/tests/test_anchor.py` -> exit 0 · output sha256 6524242680a49821 · 2026-10-27T12:19:17.738679+00:00
- `python3 harness/tests/test_anchor.py` -> exit 0 · output sha256 6524242680a49821 · 2026-10-27T12:19:19.967459+00:00
- `python3 harness/spike_anchor.py` -> exit 0 · output sha256 1db4ac79b0085764 · 2026-10-27T12:19:25.784318+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 f29f3bf95d2ce5d6 · 2026-10-27T12:19:31.191555+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-27T12:19:31.614352+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-27T12:19:34.192773+00:00
- `python3 harness/tests/test_kernel.py` -> exit 0 · output sha256 292f7577ed04694c · 2026-10-27T12:19:35.895433+00:00
- `python3 harness/tests/test_capture.py` -> exit 0 · output sha256 6a1a9ff73dc8ee77 · 2026-10-27T12:19:38.400505+00:00
- `python3 harness/tests/test_import.py` -> exit 0 · output sha256 88f804186ff9b6ff · 2026-10-27T12:19:43.035676+00:00
- `python3 harness/tests/test_extract.py` -> exit 0 · output sha256 831c5a272c88ae88 · 2026-10-27T12:19:45.304896+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 791ff1faab1f66be · 2026-10-27T12:21:25.645183+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 d80aac70af124495 · 2026-10-27T12:21:45.669036+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 3bb37fbeefc59a07 · 2026-10-27T12:21:58.500344+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 eb840bfebca3e830 · 2026-10-27T12:21:58.815336+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 4ff391be99427e0a · 2026-10-27T12:21:59.015714+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 fe42694443c98836 · 2026-10-27T12:22:02.543128+00:00
- `make verify` -> exit 0 · output sha256 f5482f97063c6fef · 2026-10-27T12:25:05.531043+00:00
- `python3 harness/gate.py --slice claim-053-p303b-anchor-resolution-q8-spike --diff origin/main` -> exit 1 · output sha256 64c8d3ddd3ad0c8d · 2026-10-27T12:51:34.604701+00:00
- `python3 harness/gate.py --slice claim-053-p303b-anchor-resolution-q8-spike --diff origin/main` -> exit 0 · output sha256 29da4321a826ac5e · 2026-10-27T13:02:03.953729+00:00
- `python3 harness/gate.py --slice claim-053-p303b-anchor-resolution-q8-spike --diff origin/main` -> exit 1 · output sha256 64c8d3ddd3ad0c8d · 2026-10-27T13:16:43.376652+00:00
- `python3 harness/gate.py --slice claim-053-p303b-anchor-resolution-q8-spike --diff origin/main` -> exit 0 · output sha256 da91f4a34bd95eff · 2026-10-27T13:24:13.071309+00:00
- `python3 harness/gate.py --slice claim-053-p303b-anchor-resolution-q8-spike --diff origin/main` -> exit 0 · output sha256 a9b4d060e7a80d55 · 2026-10-27T15:52:33.027165+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - NOT VERIFIED — the honest limits of CLAIM-053 / P3-03b (the anchor
- resolution + the Q8 synthetic-corpus spike; LAW-04; never empty-by-omission)
- - WHAT THIS SLICE PROVES, ON WHAT STACK: the typed anchor resolution
- (SYS-05's resolved | unresolved | ambiguous at query.py's resolve-anchor
- arm) holds end-to-end over the REAL boundary (the ANC-01..10 suite, three
- consecutive GREEN runs at the final tree; the generation-integrity pins
- ANC-06/07 compare the answer's generation_id and passage_ids against the
- anchor's OWN version's CURRENT generation rows; the one-hit DETECTION
- ANC-04; the byte-equal refusal normalization ANC-08; the U+2028
- row-protocol framing ANC-10) + the Q8 spike re-measured 17/17 anchors
- with the generation-id comparison live in every leg (M1/M2/M3 all 17/17
- own-version, ZERO silent retargets). The spike's failures now abort by
- name (ARV-SPIKE-002), never a silent unresolved count (the pre-fix
- silent-None and the M3 structurally-always-false echo both observed and
- repaired in this slice, red-02.txt).
- - Q8's REGISTERED BOUNDARY (§7.3) STANDS UNCHANGED: the corpus is SYNTHETIC
- (six documents: headings, unicode, repeated blocks, a single-block doc;
- 17 anchors at head/mid/boundary positions). The measured 17/17 is
- SYNTHETIC-CORPUS FIDELITY ONLY. NO real-PDF/EPUB location-stability claim
- is made or implied; a real-format claim requires a named, permitted, real
- corpus and measured results at the owner gate (Q8's registered default).
- OCR/scanned content is a distinct capability, never implied.
- - THE SPIKE'S ANCHOR PLACEMENT: three anchors per document chosen by
- structural position (head / mid / block-boundary), not an exhaustive
- positional sweep; the corpus does not exercise every tiling shape a real
- extractor may produce (the drifted-tiling classes are exercised
- synthetically in the ANC suite's planted generations, not in the spike's
- measured corpus).
- - THE FALLBACK EVIDENCE WINDOW: context_before + context_after at capture
- time are 32 chars each side (commands.py's create_highlight); the
- ambiguity and one-hit behaviors are measured against THAT window size. A
- future change to the window is a different contract surface.
- - NOT VERIFIED — the resolve-anchor surface at CONCURRENT readership
- (multiple simultaneous resolvers over one source): the typed answer is a
- read-only surface over committed rows and the suites exercise it serially;
- the concurrent-reader matrix belongs to the read-path scale slice.
- - NOT VERIFIED — the passage-row framing for control characters ABOVE
- U+2028's class that PostgreSQL also leaves raw in other encodings (the
- fix binds the reader to NEWLINE-ONLY framing, which is framing-safe for
- every character PostgreSQL can emit in a JSON string; the untested
- surface is other psql OUTPUT FORMATS (-A tuples, CSV), which this slice
- never reads).
- - THE KNOWN-BAD BASELINE's TWELVE SEV/PRF/CLM/RED/SCOPE GUARDS: verified by
- the gate's own negative probes at every run (the KB-SEV/KB-PRF/etc. PASS
- lines in the gate output), not re-proven by independent adversarial
- attempts in this slice.
- - THE MERGE-CHAIN FACTS (the D-042 reproduction for THIS slice, the
- post-merge five-check observation, the branch deletion, the protections
- re-read): recorded only after they happen, in the next slice's commit A
- (the convention; a committed file cannot guarantee external state, INT-104).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: ece63a9a49ebe6e4e0cd0b8c37b23c01748a361d5f5745488c74a81ef365ff83
- reviewed_diff_sha256: 1542466c1ceddeea879135834d8712220f7018faa3d2da1aca123c9b8da2c202
- disposition: PASS
- findings: 6 (open P0/P1: 0)
- not-verified entries: 7

## Assembly
- sheet sha256 (of the content above, excluding this line): d76a9c3f58e27ce373149ec0562fabd4deda8a50a1be752d9af6ef28c23f1214
