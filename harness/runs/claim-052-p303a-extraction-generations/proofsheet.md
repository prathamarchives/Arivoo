# PROOF SHEET — slice claim-052-p303a-extraction-generations (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): af88591ce6b70cbc3cb713b8d4f41f17f0ffd12f
- generated (last record's timestamp): 2026-10-26T11:54:45.004592+00:00
- run records: 19

## Run records (command, exit, output digest)
- `python3 harness/tests/test_extract.py` -> exit 0 · output sha256 a7423c018d2f4085 · 2026-10-26T10:59:46.443439+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 f29f3bf95d2ce5d6 · 2026-10-26T10:59:51.682989+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-26T10:59:52.085329+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-26T10:59:54.688244+00:00
- `python3 harness/tests/test_kernel.py` -> exit 0 · output sha256 b62ae90e95faf1c6 · 2026-10-26T10:59:56.338047+00:00
- `python3 harness/tests/test_capture.py` -> exit 0 · output sha256 52106db29410e836 · 2026-10-26T10:59:58.618475+00:00
- `python3 harness/tests/test_import.py` -> exit 0 · output sha256 88f804186ff9b6ff · 2026-10-26T11:00:03.004185+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 791ff1faab1f66be · 2026-10-26T11:01:36.734148+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 81e7d2e1f60ca5ca · 2026-10-26T11:02:04.062936+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 4e3bbfaa90eaefd4 · 2026-10-26T11:02:15.987419+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 7cfa04be9de3d2a0 · 2026-10-26T11:02:16.520066+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 4ff391be99427e0a · 2026-10-26T11:02:16.809279+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 cae50aea5cbeffaf · 2026-10-26T11:02:19.571622+00:00
- `make verify` -> exit 2 · output sha256 867e49f40a4a4e91 · 2026-10-26T11:05:35.110229+00:00
- `make verify` -> exit 0 · output sha256 c4f0dbb0379dcffd · 2026-10-26T11:27:17.631663+00:00
- `python3 harness/gate.py --slice claim-052-p303a-extraction-generations --diff main` -> exit 0 · output sha256 696f24d0b17c81c4 · 2026-10-26T11:31:18.952923+00:00
- `python3 harness/tests/test_extract.py` -> exit 0 · output sha256 9ebaf9658a136f75 · 2026-10-26T11:48:36.758921+00:00
- `make verify` -> exit 0 · output sha256 4d630d7215c26066 · 2026-10-26T11:51:48.800166+00:00
- `python3 harness/gate.py --slice claim-052-p303a-extraction-generations --diff main` -> exit 0 · output sha256 2b4464f846eefe02 · 2026-10-26T11:54:45.004592+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-052 / P3-03a (the extraction
- generations; LAW-04; never empty-by-omission)
- WHAT THIS SLICE PROVES, ON WHAT STACK: the derived generation machine
- (building -> current/failed complete-or-failed; the versioned lineage with
- superseded retained; the crash matrix; the same-key resume/replay; the
- disposable §2.9 conventions; the owner isolation) GREEN in the suite EXT-01..13
- on the rig's user-space PostgreSQL 17 (loopback, trust auth) — the five-check
- CI run at the pushed head is the walls' verification of the pushed tree
- (INT-104): no in-file result covers the pushed head itself.
- THE REPLAY VOCABULARY (the SEV round's F5, RESOLVED by the #87 CodeRabbit
- round 2): a same-key retry of a FAILED generation now answers exit 1 with the
- recorded reason (EXT-15 — never a silent success); a superseded generation's
- replay still answers exit 0 with state=superseded (it completed once, then was
- displaced — the recorded outcome is honest); the CALLER reads the state field
- for the displaced class.
- THE SIZE-CAPPED SPLIT (F3): NOT implemented and NOT required by the RTM
- freeze — an over-long single block yields ONE passage (the SEV probe: a 2 MB
- paragraph -> 1|0|2097153); routed to the read-path/indexing slices' own
- bounded work if the corpus ever needs it.
- THE TYPED STALE REPORTING (F4): the SUBSTRATE is proven (the generation's
- input_digest binds the source row it was built from; EXT-09); the typed
- stale-state QUERY surface (reporting a mismatch as a named state) is the read
- path's own slice — never claimed here.
- THE NUL CLASS IN THE SPINE'S OWN LITERAL PATHS (F1's sibling): the psql
- C-string boundary exists for EVERY _q()-built literal — record_event's payload
- and import_source's title carry the same pre-existing class (not this slice's
- regression; THIS slice's path is guarded by ARV-EXT-005 and pinned RED-first).
- Routed as the spine's named follow-up (its own bounded slice, never silently
- dropped).
- THE MEDIA-TYPE GATE: an application/pdf whose bytes decode as UTF-8 extracts
- cleanly — the boundary is the DECODE by design (P3-01's convention, the SEV
- round's H2 probe); a media-type allowlist is NOT this freeze's rule.
- THE SPLITTER'S DOCUMENTED EDGES (not suite-pinned): a trailing heading with
- no following content block is its own passage; a leading blank-line prefix
- precedes the first passage (the passages tile the CONTENT span, not
- necessarily [0, len)); both are the pinned splitter's behavior — verified by
- the SEV round's 24 edge probes, but the suite's fixture carries neither shape.
- THE CONCURRENT-LOSER PATH: the SEV round's live races (4 concurrent process
- races + 2 concurrent same-key resumes: single-current held, the loser
- ARV-CMD-011 with zero effect) are the evidence; the DEADLOCK class is now
- pinned deterministically (EXT-14 — the planted deadlock-raising trigger), but
- a true multi-process in-suite race case is not pinned (the suite is serial by
- design).
- THE SEV REVIEWER'S REMOTE OBSERVATIONS: the reviewer's sandbox was GitHub-API
- rate-limited — the CLAIM-051 close-row merge facts (0ce7077, run 40291330001)
- were git-verified by the reviewer (the merge commit + the branch list) and the
- API observations recorded in the close row are the builder's own live reads.
- THE MERGE (D-042): the single-actor 405 bar + the recorded flip path reproduce
- live at the merge — the protection restored and re-read after.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: ab4e44a3b9f56b9998ba762d8499da34ae998ff3b0e465d73d00ecbad54b71d5
- reviewed_diff_sha256: 31a67ce8ff4b344d44c21c37d0acaecd362edbfecdb9570cf1bce605b06140ed
- disposition: PASS
- findings: 4 (open P0/P1: 0)
- not-verified entries: 8

## Assembly
- sheet sha256 (of the content above, excluding this line): f7563d790f9d29b4ddb53b0fd8e231a8d752b204cc8a086c749f06757795f2a7
