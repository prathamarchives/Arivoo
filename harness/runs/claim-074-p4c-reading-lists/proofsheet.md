# PROOF SHEET — slice claim-074-p4c-reading-lists (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): ed3b27aa7333693ec2bb795a833cb2578c27a195
- generated (last record's timestamp): 2026-11-10T17:24:18.970716+00:00
- run records: 8

## Run records (command, exit, output digest)
- `python3 harness/tests/test_reading_list.py` -> exit 0 · output sha256 19d0471dfa8c69c9 · 2026-11-10T16:42:00.538333+00:00
- `python3 harness/tests/test_reading_list.py` -> exit 0 · output sha256 19d0471dfa8c69c9 · 2026-11-10T16:42:05.334594+00:00
- `python3 harness/tests/test_reading_list.py` -> exit 0 · output sha256 19d0471dfa8c69c9 · 2026-11-10T16:42:10.114229+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 ec724b9bb793268a · 2026-11-10T16:42:26.900355+00:00
- `python3 harness/tests/test_journal.py` -> exit 0 · output sha256 bb621c0318508777 · 2026-11-10T16:42:31.505179+00:00
- `make verify` -> exit 0 · output sha256 eb1d252aab604509 · 2026-11-10T16:49:15.778211+00:00
- `env SLICE=claim-074-p4c-reading-lists GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 aaf1cf0edd9c54f2 · 2026-11-10T17:23:59.655444+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-074-p4c-reading-lists python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 5945fa09b0aba8b2 · 2026-11-10T17:24:18.970716+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- CLAIM-074 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json + sev-round-1.md.
- - F-074-1 (P2, ROUTED): the leading-dash argv-value class — a legal list name like
- '--evil' (creatable via the --name= spelling) enqueues an outbox row whose
- server-side apply dies at argparse; the row rests uncertain (honest, visible, the
- local write durable; the walk continues), never landing server-side.
- PRE-EXISTING family-wide: import_source --title=--eviltoo shows the identical
- behavior at this tree. Routed with the import-title/note-content family to the
- argv-value convention's own slice (the repair — the --name= spelling in _cli_args —
- spans every argv-carrying delivery branch; a list-only fix would fork the
- convention; the F-072-1/F-073-6 routing precedent).
- - F-074-2 (P3): a different-key duplicate-op membership write surfaces as the generic
- ARV-CMD-010 (the raw cause naming ARV-RLS-008) — zero effect, the declared design
- boundary (the alternation law's own refusal shape); a precision note for the
- family-wide typed-refusal slice.
- - F-074-3 (P3): red-01.txt names the commit-A tree (73bfd8c) as the observation tree
- rather than the RED commit (e7e833f) — the standing family convention (F-073-5's
- class); reasoned no-fix: contemporaneous evidence, never rewritten post-hoc; the
- exact binding lives in the typed record naming e7e833f; the SEV reviewer
- independently reproduced the RED at the RED commit itself.
- - F-074-4 (P3, assessment): get-list's two-read shape (the header read then the member
- page, two snapshots) — no vanish class (the header is append-only); a momentary
- member_count/page divergence possible; the family's known bounded read-arm class
- (the F-072-1 routing family), assess-only.
- - The standing family-wide classes routed by the prior slices' reviews, unchanged
- here: the read arms' malformed-id echo (F-072-1's routing — the _nte_canon_id
- pattern's own family-wide slice); the import_source staging-before-argv residue
- (F-073-6); the F-073-3(a)-class staging reorder.
- - No fresh full-suite re-run inside the SEV round itself: the round ran ~92 targeted
- live probes + ~10 static/git checks; the recorded runs (01-06: the RLS suite x3 +
- the sync suite + the journal suite + make verify, all exit 0) stand as the suite
- evidence.
- - The single-owner walk shape: the SEV round's own two-DB walk covered owner A;
- B's delivery isolation is verified through the sync suite's SYN-08 class, not
- re-walked by the round.
- - No reader-client work (P4-B's repo); harness/client.py's surface unchanged at this
- slice.
- - The bounded exclusions held: no list ordering/pinning; no list-of-lists or nested
- collections; no shared/multi-owner lists; no @-reference resolution over lists
- (P4-D's increment); no rename/revision machine on the list header (the name
- immutable at this slice — a rename is its own increment).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 7b9407dc0041a0416dfeec5783c1f0bf1c4ab6dc72a6908f6860723e975742fc
- reviewed_diff_sha256: 65c0d3421b1aa7e97f865a5d1094a8d265cca451479f73e69c5e66b3c032878d
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 7

## Assembly
- sheet sha256 (of the content above, excluding this line): cbc0a308c481a7dd5bd0ee321437e4315a3e97d3e4348846230d59c7dadd0595
