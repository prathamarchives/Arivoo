# PROOF SHEET — slice claim-057-p306-refs (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): b6b447b6b6e0f7f4afdb4b07aeacbc95a0ef0f95
- generated (last record's timestamp): 2026-11-04T12:32:58.710614+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 harness/tests/test_note_reference.py` -> exit 0 · output sha256 4b3299867eb440e9 · 2026-11-04T12:02:44.576819+00:00
- `python3 harness/tests/test_note_reference.py` -> exit 0 · output sha256 4b3299867eb440e9 · 2026-11-04T12:02:48.098156+00:00
- `python3 harness/tests/test_note_reference.py` -> exit 0 · output sha256 4b3299867eb440e9 · 2026-11-04T12:02:51.630376+00:00
- `python3 harness/tests/test_note.py` -> exit 0 · output sha256 1afeb21646e5c40b · 2026-11-04T12:02:58.647812+00:00
- `make verify` -> exit 0 · output sha256 c7f202aa0a6ef1fb · 2026-11-04T12:06:36.327812+00:00
- `SLICE=claim-057-p306-refs GATE_DIFF=36e34920f1da028495b7857b137442957b3a8d9f make gate` -> exit 0 · output sha256 b7fc1e1826bba078 · 2026-11-04T12:32:58.710614+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - NOT VERIFIED — the honest limits of CLAIM-057 / P3-06 SLICE TWO (the
- version-aware reference machine; LAW-04; never empty-by-omission)
- - WHAT THIS SLICE PROVES, ON WHAT STACK: the reference machine of RTM §2.5
- item 7 holds end-to-end over the REAL PostgreSQL boundary (17.11: the local
- rig + CI's postgres:17 service): the explicit per-revision references
- (kind work/source/anchor/highlight/note; highlight/note MUST name the
- target revision, work/source/anchor MUST NOT — the shape law at the parse,
- the CHECK, and the guard; the set semantics UNIQUE per (note, revision,
- kind, target)); the referenced (id, revision) pair PINNED at write time
- (a historical highlight/note reference never silently retargets through
- the target's later revises or its tombstone); the target-existence +
- caller-scope guards at BOTH boundaries (absent, another owner's, and a
- nonexistent target revision are the SAME ARV-NTE-003 refusal — the SEV
- reviewer's own template byte-comparison, including the anchor kind beyond
- the suite's coverage); the whole-command crash contract (content and
- references commit as ONE effect at every spine point; the replay converges
- lost acks with the refs intact); the backward-compatible body (a no-refs
- payload byte-identical to the pre-0010 form — cross-slice retries REPLAY,
- never a false 409); the read arms render refs INSIDE the #91 round-3
- single-statement one-snapshot form (a post-tombstone read leaks neither
- content nor refs) and the history carries each revision's OWN set (the
- export-ready history). All verified by the NTR-01..12 suite (GREEN x3,
- run-01..03) + the note-core NTE-01..15 no-regression run (run-04) + make
- verify (run-05) + the fresh-context SEV round (agent ntr-sev-r1, PASS,
- zero open P0/P1 — its own scratch-DB probe set incl. TEN hostile direct-SQL
- classes, the crash matrix with --ref, the catalog audits, the split-honesty
- diff greps, and both suites re-run with outputs byte-identical to the
- recorded run hashes).
- - THE ROUTED FOLLOW-UPS (F1/F2, one root cause, never silently dropped):
- --ref target UUID spellings are not canonicalized before the body hash
- (F1: a case-variant retry of the same logical target meets ARV-CMD-409 —
- the #91 round-2 _nte_canon_id precedent class, this time on the TARGET
- side; F2: a case-variant in-command duplicate escapes the 008 seen-set and
- surfaces as a misattributed ARV-CMD-011 with zero effect). Both ROUTED to
- one small canonicalization follow-up (mirror _nte_canon_id over ref targets
- inside _nte_refs); both fail-closed; neither merge-blocking.
- - THE SEV REVIEWER'S OWN HONEST LIMITS (verbatim in substance): the full
- make verify did not run as ONE command inside the reviewer's sandbox
- (background processes killed between tool invocations — environment, never
- repo; its components were reproduced individually and the builder's
- recorded run-05 carries the complete sequential exit 0); the suites
- outside the diff's blast radius were not re-run by the reviewer (their
- files byte-untouched; the builder's run-05 + the PR's five-check run cover
- them on the real stack); the remote CI run is the walls' own evidence;
- the deterministic tombstone-vs-read interleaving (NTE-15's race machinery)
- was verified structurally (the single-statement NOTE_SQL read) + post-hoc
- (the post-tombstone refusal probe), the race pin resting on the NTE
- suite's green re-runs; the reviewer's own multi-writer concurrency round
- on note_reference inserts was not run (the guard's serialization evidenced
- by the lock-key equality with the 0009 guards + NTE-12/13's green
- re-runs).
- - THE STANDING RESIDUALS (inherited, unchanged): the no-GUC RLS-invisibility
- fence (the 0002/0004/0007/0008/0009 convention — the sync/purge revisit
- condition); the raw-uuid-cast boundary class (a PostgreSQL-REFUSED
- spelling on --ref surfaces the generic session-death wrapper — the shared
- landed-family class, routed with the standing sibling classes); Q10's
- host-level workflow protection; the OS-separation boundary.
- - OUT OF SCOPE BY THE CARD'S OWN BOUNDARIES (never claimed): the
- diagram/structured-block serialization contract (P4-C's reservation — its
- own round-trip proof required before "supported"); the keyword index
- (P3-07's); the outbox/sync rungs (P3-08's); the governed purge (P3-06/09's,
- D-011); P3-09's export/restore round-trip of references (only the
- history-rebuild property re-observed here); reference behavior under the
- governed purge (refs to tombstoned targets at existing revisions were
- observed ACCEPTED — the revision rows persist per §3.3 — recorded as
- observed behavior, never adjudicated in this slice).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: e0252a8b6b943b9c30b67570f3842827586839d87259377f44e205de9bb85277
- reviewed_diff_sha256: 5c32d5d457e2d3279166b19247f9e1d9667bb1c748871c360281d48372cac9f6
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 032c02b9de2874f864c8e979980cb3b6618201445dfb840057a4a9dd041b7d31
