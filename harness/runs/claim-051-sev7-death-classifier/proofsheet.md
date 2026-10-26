# PROOF SHEET — slice claim-051-sev7-death-classifier (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): b782c4b96cc56a6c9f1a464055e4de6bfd6247f4
- generated (last record's timestamp): 2026-10-26T07:52:37.224797+00:00
- run records: 14

## Run records (command, exit, output digest)
- `python3 harness/tests/test_import.py` -> exit 0 · output sha256 88f804186ff9b6ff · 2026-10-26T07:09:55.828877+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 9a74cebc12826061 · 2026-10-26T07:10:05.043792+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-26T07:10:05.527521+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-26T07:10:08.498391+00:00
- `python3 harness/tests/test_kernel.py` -> exit 0 · output sha256 a5a0c2b235d60d22 · 2026-10-26T07:10:10.346651+00:00
- `python3 harness/tests/test_capture.py` -> exit 0 · output sha256 1437686f2678ccca · 2026-10-26T07:10:12.853167+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 791ff1faab1f66be · 2026-10-26T07:11:51.291394+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 00168dc39a9bef27 · 2026-10-26T07:12:22.266464+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 b4e31c532b98467c · 2026-10-26T07:12:37.166743+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 4aa7d3a2bb221b2d · 2026-10-26T07:12:37.656763+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 4ff391be99427e0a · 2026-10-26T07:12:37.919822+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 6afbec250658f4e7 · 2026-10-26T07:12:41.493578+00:00
- `make verify` -> exit 0 · output sha256 87c923b2f078d973 · 2026-10-26T07:15:59.821706+00:00
- `python3 harness/gate.py --slice claim-051-sev7-death-classifier --diff main` -> exit 0 · output sha256 8fda8ee2a7cdc36d · 2026-10-26T07:52:37.224797+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-051 / the SEV-7 death classifier
- (LAW-04; never empty-by-omission)
- WHAT THIS SLICE PROVES, ON WHAT STACK: the spine's dead-session classification
- reads the DRAINED, OBSERVED stderr cause (the Session's second pump from
- construction + dead_reason's wait()-certain read) — the duplicate-key class
- names ARV-CMD-011 with zero effect and the same-key-retry repair; the
- connection-class names the NEW ARV-CMD-012 (the §4.1 UNCERTAIN class — the
- client never assumes committed-or-rolled-back; the same-key replay resolves
- it); an unrecognized death stays the honest ARV-CMD-010 with the raw cause
- appended. Wired at every spine marker (BEGIN/INSERTS/COMMITTED) and the
- journal-phase transactions; a LIVE session's stall raises to the existing
- 010 path unchanged. Pinned by IMP-18 (the planted-trigger deterministic
- dup-key arm) and IMP-19 (the killed-backend probe + the replay resolution),
- plus the capture suite's own CAP-21 arm (the real unique-index race still
- classifies 011 — from the drained stderr now).
- THE EXPLICIT BOUNDARIES (named, never silently narrowed):
- 1. The classification is by SUBSTRING over the drained stderr — the named
- psql/server error phrases (duplicate-key, connection-loss classes), not a
- structured protocol. A server message outside the phrase lists falls to
- the honest ARV-CMD-010 with the raw cause appended — named, never guessed;
- extending a phrase list is a bounded future refinement, never urgent.
- 2. The TRUE mid-commit network partition remains undecidable to stage
- deterministically (the honest class the P3-01 SEV-11 record already
- named): IMP-19's deterministic arm terminates the backend BEFORE the
- spine's BEGIN (from the client's view the marker flow broke — the same
- unknowability); the 012 CONTRACT (uncertain + the same-key replay
- resolves) is what is pinned, and it is position-independent by §4.1's
- semantics.
- 3. The classifier names the OBSERVED cause of the session's death only — it
- does not and cannot know whether the server committed before the
- connection dropped (that is 012's whole point); the replay IS the
- resolution and it is the client's only safe move.
- 4. The stderr pump is a daemon thread reading a pipe — under a catastrophic
- host failure both pumps can die with the process; dead_reason then
- returns what was drained (possibly empty), and the classification falls
- to the honest 010. The wait()+join ordering makes this the exhausted-
- buffer class, never the lagging-read class (IMP-18/19 pin the ordering).
- 5. The 011/012 exit codes and repair texts preserve the frozen kernel
- vocabulary (010/011 unchanged; 012 NEW — declared in the suite, the
- records, and the RTM §4.1/§6 alignment is the record's text, never a
- schema change); the S3/K0 suites' pins (test_commands, test_kernel) pass
- over the re-wiring (make verify green).
- 6. CI-host observation only (the standing class): the five checks green on
- the service container; host-level claims remain Q10/EXTERNAL.
- 7. The follow-ups still routed and never lost: the ARV-SEV-009
- undecidable-base regression; the N12 self-test-row extension; the sweep
- micro-gap + the _fail version-guard (P3-08's serialization); the
- num_nonnulls DB CHECK (its own migration slice); the read-side state
- filter (query.py's own slice).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 111d15d2d5f639f685aa313256bfbebd1c472bb7dbc684fe784c4f5348ddf2c1
- reviewed_diff_sha256: d99d8ee954a1360caa87da62c02a60c889b2bb2502407072138aa15bdd9c6d70
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 3daf3384074ecbd9cf8de3272db5c588b9e044c7bf600daae678ed424d36ca10
