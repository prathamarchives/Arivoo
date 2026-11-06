# PROOF SHEET — slice claim-068-p4a-pdf-boundary (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): e13a261139980a87d546f71b1167fa193ccf7dd3
- generated (last record's timestamp): 2026-11-06T20:13:10.236370+00:00
- run records: 7

## Run records (command, exit, output digest)
- `python3 harness/tests/test_pdf.py` -> exit 0 · output sha256 cb6a5ad870c83f68 · 2026-11-06T19:46:10.655414+00:00
- `python3 harness/tests/test_pdf.py` -> exit 0 · output sha256 cb6a5ad870c83f68 · 2026-11-06T19:46:12.075147+00:00
- `python3 harness/tests/test_pdf.py` -> exit 0 · output sha256 cb6a5ad870c83f68 · 2026-11-06T19:46:18.851314+00:00
- `make verify` -> exit 0 · output sha256 e1d5db736a931de8 · 2026-11-06T19:52:33.588515+00:00
- `make verify` -> exit 0 · output sha256 ba6293c83c55b6ad · 2026-11-06T19:58:42.849759+00:00
- `env SLICE=claim-068-p4a-pdf-boundary GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 485d950d3dd1ad64 · 2026-11-06T20:12:41.974571+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-068-p4a-pdf-boundary python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 221d574b8a0e3cc0 · 2026-11-06T20:13:10.236370+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-068 / P4-A slice four (the PDF
- boundary: the honest passthrough class, never a text-extraction claim;
- LAW-04; never empty-by-omission).
- WHAT THIS SLICE PROVES: application/pdf is INTAKE-LEGAL as the bytes
- passthrough's NAMED type (a PDF imports durably through the one ladder — the
- blob stores the ORIGINAL bytes, content-addressed, never transformed); the
- readable-text boundary stays at EXTRACTION's named ARV-EXT-002 over the
- binary bytes (zero effect, the staged bytes recoverable at the source's
- digest); the keyword index's non-text boundary (the PDF-internal tokens
- search to nothing — the source commits, findability indexes text only); the
- matrix stays HONEST (NO pdf row — a format appears only through its
- acceptance corpus); the octet-stream equivalence (the same bytes, the same
- letters — one class, never two); the capture/position arms refuse typed
- (ARV-CAP-008 / ARV-POS-002, both zero-effect).
- THE HONEST LIMITS:
- - NO PDF TEXT EXTRACTION (the bounded exclusion, held): this slice lands the
- BOUNDARY, not a reader. The scan/OCR class (reading scanned pages), the
- fixed-layout class (reading positioned text), and any real text extraction
- are FUTURE INCREMENTS under Q8's owner gate (the owner-supplied
- real-document corpus) — never a generic claim from the passthrough.
- - THE ALL-ASCII PDF CLASS (the SEV round-1 routed note): a minimal PDF that
- happens to be valid UTF-8 EXTRACTS (exit 0) with the PDF syntax as its
- text — the DECODE is the boundary, never the media type (the landed
- EXT-02/EXT-03 letter; a media-type refusal would break the one-class
- equivalence PDF-04 pins). The "syntax-as-text" residual rides the future
- scan/OCR increment's acceptance corpus (a real PDF reader distinguishes
- syntax from content; the passthrough honestly does not try).
- - THE SEV ROUND'S OWN NOTES (agent-9c4e2f17, all P3, none
- repair-requiring): (a) the all-ASCII class above; (b) export.py's restore
- validates archive blobs but the destination's blob-store provisioning
- (ARV_BLOB_DIR) is the operator boundary — CLAIM-060's landed design,
- unchanged here, the PDF bytes verified intact through the machine; (c) the
- GREEN commit's "NO TEST AMENDMENTS" message vs the probe-repair commit's
- chained amendment — the message's substance held (the five cases
- untouched; the amendment is the module-level probe replacement only, one
- hunk), the immutable history noted, never rewritten.
- - THE PROBE AMENDMENT (disclosed, the typed chain in red-records.json): the
- machinery-absent probe's import-based first draft depended on the ambient
- database and a fixed idem key (a second run replayed the prior ack and
- misread the machinery; the replay path also bypasses the registry check);
- the replacement is the DB-free INTAKE_OK registry probe —
- environment-independent, idempotent, and the registry IS the machinery.
- - THE SYNTHETIC FIXTURE ONLY: the suite's PDF is a hand-built minimal binary
- document — never a real-PDF stability claim (Q8's gate).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 0d67c44c412ffa3ff2e05ccf55e08d890b0cb90d10381bf49a67b0d6c69eafd8
- reviewed_diff_sha256: ff97db0a9c9a10b84042995d1e517bb1fb6f64957fefba363319950b3628c2ce
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 1

## Assembly
- sheet sha256 (of the content above, excluding this line): da9f5c4e1f9372f315bb69667fc176b04847fdad396b80baaa5f2030af212512
