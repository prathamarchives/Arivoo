# PROOF SHEET — slice claim-052-p303a-extraction-generations (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): f2d6d920d6bd17d884066f8e3d70ebe26ef9050f
- generated (last record's timestamp): 2026-10-26T11:31:18.952923+00:00
- run records: 16

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
- THE REPLAY VOCABULARY BOUNDARY (the SEV round's F5): a same-key retry of a
- FAILED generation — or of a building row a LATER key superseded — answers
- exit 0 with status=replayed and state=failed|superseded; the CALLER must read
- the state field. A distinguishing exit code for replayed failures is the
- query surface's own consideration (routed to the read path's slice).
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
- THE CONCURRENT-LOSER PATH: the SEV round's live races (4 concurrent
- process races + 2 concurrent same-key resumes: single-current held, the loser
- ARV-CMD-011 with zero effect) are the evidence; a DETERMINISTIC in-suite
- concurrency case is not pinned (the suite is serial by design).
- THE SEV REVIEWER'S REMOTE OBSERVATIONS: the reviewer's sandbox was GitHub-API
- rate-limited — the CLAIM-051 close-row merge facts (0ce7077, run 40291330001)
- were git-verified by the reviewer (the merge commit + the branch list) and the
- API observations recorded in the close row are the builder's own live reads.
- THE MERGE (D-042): the single-actor 405 bar + the recorded flip path reproduce
- live at the merge — the protection restored and re-read after.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: e19d525a4f62cf486a60a58eed9017e4fb3ff0f06458dec0140ff289f2bda75a
- reviewed_diff_sha256: 58bb8320d039a00d59b62ecd3a72b3b29f12e3590a66131ae5327ef8c8d2d02b
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 8

## Assembly
- sheet sha256 (of the content above, excluding this line): b83c8148e891b5f1e267f5afab7e6b8332c55155df0ede73574e8e22734b647d
