# PROOF SHEET — slice claim-075-p4d-stable-references (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 2988f560ba1eaa63099567ba03202af0ffcc3012
- generated (last record's timestamp): 2026-11-11T10:31:18.502204+00:00
- run records: 10

## Run records (command, exit, output digest)
- `python3 harness/tests/test_references.py` -> exit 0 · output sha256 4eebc013c0d0cc1b · 2026-11-11T09:29:41.527381+00:00
- `python3 harness/tests/test_references.py` -> exit 0 · output sha256 4eebc013c0d0cc1b · 2026-11-11T09:29:50.876083+00:00
- `python3 harness/tests/test_references.py` -> exit 0 · output sha256 4eebc013c0d0cc1b · 2026-11-11T09:30:00.262603+00:00
- `make verify` -> exit 0 · output sha256 45d9d77a4b38d01f · 2026-11-11T09:36:45.057672+00:00
- `python3 harness/tests/test_references.py` -> exit 0 · output sha256 4eebc013c0d0cc1b · 2026-11-11T10:02:48.419359+00:00
- `python3 harness/tests/test_references.py` -> exit 0 · output sha256 4eebc013c0d0cc1b · 2026-11-11T10:02:57.653791+00:00
- `python3 harness/tests/test_references.py` -> exit 0 · output sha256 4eebc013c0d0cc1b · 2026-11-11T10:03:06.726424+00:00
- `make verify` -> exit 0 · output sha256 40f43878fdf01565 · 2026-11-11T10:09:29.745399+00:00
- `env SLICE=claim-075-p4d-stable-references GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 84033a6a33e72216 · 2026-11-11T10:30:51.001978+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-075-p4d-stable-references python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 048b09f6e496ddf4 · 2026-11-11T10:31:18.502204+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - CLAIM-075 — the honest not-verified list (LAW-04: the explicit statement, never
- - empty-by-omission). The full SEV account: sev.json + sev-round-1.md + sev-round-2.md.
- - - F-075-3 (P3, ROUTED): the unicode-digit and leading-zero pin normalization — the
- - CLAIM-057 substrate's own isdigit law (commands.py:1219) composed VERBATIM at the
- - resolution boundary; narrowing it here would be the forbidden second implementation.
- - Routed to the substrate grammar owner (tighten both boundaries together if ASCII-only
- - pins are wanted).
- - - F-075-4 (P3, owner-accepted-debt): the uppercase-hex uuid resolves and is echoed
- - case-preserved (RFC 4122 case-insensitivity; the regex allows A-F, the same as the
- - substrate) — cosmetic identity-echo debt.
- - - F-075-5 (P3, ROUTED): the landed resolve-anchor arm does not consult the purge
- - ledger (a purged anchor: resolve-reference answers purged, resolve-anchor still answers
- - its P3-03b verdict) — pre-existing landed behavior outside this slice's diff; routed to
- - D-011's governed-purge command slice.
- - - the standing family-wide classes routed by the prior slices' reviews (unchanged):
- - the read arms' malformed-id echo + the substrate's own $-anchored _UUID_RE (F-072-1's
- - routing — the _nte_canon_id pattern's slice; this slice repaired only ITS OWN copy to
- - \Z), the leading-dash argv-value family (F-074-1), the import_source staging-before-argv
- - residue (F-073-6).
- - - no agent-facing reference resolution (P4-E's increment); no reference graph queries
- - (P5's world); no reader-client work (P4-B's repo).
- - - no concurrency probes — the single-statement single-snapshot law verified
- - structurally (the per-family state read IS one statement), never under actual parallel
- - writes (both SEV rounds' honest limits).
- - - the note machine's WRITE vocabulary stays at its five kinds this slice (the 0010
- - CHECK would need a migration to widen — a substrate change never made here;
- - bookmark/journal_block references are RESOLVABLE through the surface but not yet
- - WRITABLE through note --ref).
- - - no performance/DoS measurements (the F-075-1 crash class verified functionally;
- - no cost curves measured).
- - - the purge-vs-malformed precedence corner (a caller's ledger row naming another
- - owner's entity id) reasoned but not probed — requires contrived uuid collisions.
- - - the location-unmatched unavailable cause covered by the landed ANC suite, not
- - re-derived from scratch by the SEV rigs (the compose agreement verified on the other
- - three verdict classes).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 9f31ca4c81290ffec947ace042ac0ce58433dd35ab9b4623285d89b21582c825
- reviewed_diff_sha256: b712dcf27a7a83aa1084ebe848bba19729083ecb0d9ab9cae8b6720e595bf47f
- disposition: PASS
- findings: 1 (open P0/P1: 0)
- not-verified entries: 11

## Assembly
- sheet sha256 (of the content above, excluding this line): 03e64461a919a6c26c63f5d34b90aaa996a9c094cc5734d71bd3bb0e7f899874
