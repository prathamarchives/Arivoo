# PROOF SHEET — slice claim-079-p4f-recovery-contract-gate (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 2c8075325885061f5b7b79e3ea285d317fd79244
- generated (last record's timestamp): 2026-11-13T15:45:59.515438+00:00
- run records: 23

## Run records (command, exit, output digest)
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T06:28:24.522185+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T06:28:36.808728+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T06:28:49.311846+00:00
- `make verify` -> exit 2 · output sha256 599d1b370c05a32f · 2026-11-13T06:32:47.024910+00:00
- `make verify` -> exit 0 · output sha256 a9ddb603b49996bc · 2026-11-13T07:01:12.385105+00:00
- `python3 harness/tests/test_export.py` -> exit 0 · output sha256 a38628469c906935 · 2026-11-13T07:01:21.079216+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 671195a850ef8754 · 2026-11-13T07:01:36.387976+00:00
- `python3 harness/tests/test_journal.py` -> exit 0 · output sha256 bb621c0318508777 · 2026-11-13T07:01:39.900846+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T10:32:41.112318+00:00
- `python3 harness/tests/test_export.py` -> exit 0 · output sha256 a38628469c906935 · 2026-11-13T10:32:52.034043+00:00
- `make verify` -> exit 0 · output sha256 cbdc4f26795799db · 2026-11-13T10:40:10.543109+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T11:28:00.410493+00:00
- `python3 harness/tests/test_export.py` -> exit 0 · output sha256 a38628469c906935 · 2026-11-13T11:28:10.722912+00:00
- `make verify` -> exit 0 · output sha256 bb1611ba48e38396 · 2026-11-13T11:42:33.373697+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T11:57:18.066018+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T12:04:48.529335+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T14:50:00.235509+00:00
- `python3 harness/tests/test_export.py` -> exit 0 · output sha256 a38628469c906935 · 2026-11-13T14:50:10.028608+00:00
- `make verify` -> exit 0 · output sha256 bdd97ebb8c4e7e48 · 2026-11-13T14:57:02.270102+00:00
- `make verify` -> exit 0 · output sha256 89af6ef1658b4475 · 2026-11-13T15:11:22.261752+00:00
- `python3 harness/tests/test_recovery_contract.py` -> exit 0 · output sha256 74e8964da928ad50 · 2026-11-13T15:31:08.676723+00:00
- `python3 harness/tests/test_export.py` -> exit 0 · output sha256 a38628469c906935 · 2026-11-13T15:31:18.211781+00:00
- `make verify` -> exit 0 · output sha256 cce0435678fe9bdc · 2026-11-13T15:45:59.515438+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - CLAIM-079 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json (+ the review summary inside it).
- - - the RCW suite's rigs are CLASS-scoped, not tool-level: the prior-baseline migration
- rig copies 0001..0014 and the sync rig's two scratch databases are assembled by the
- SUITE (test_recovery_contract.py's own setup), the conditions observe through the
- real CLIs only — the rig-building itself (create_scratch_db, the SQL-file copying) is
- harness code, not a product surface, and is not itself a "verified through the client"
- claim.
- - - the crash matrix rides ONE arm (post-commit-pre-ack, exit 2): the other crash arms
- (pre-commit, post-ack) are CLAIM-void classes proven by earlier suites' pins
- (test_commands/CAC), not re-proven here; the walk's replay is the same-KEY
- (idempotency) convergence) — a same-BODY different-body-different replay (the
- 409 class at the sync layer) is covered by the sync-conflict condition's two-DB form,
- not the journal arm.
- - - the export round-trip's byte-equality is over the READS the client issues (the
- ten-arm set incl. search): columns NOT in any read arm ride unverified-by-observation
- (they ride by the manifest's table-set pin + the restore's own completion line, the
- machine's integrity contract, not a per-column byte compare).
- - - the credential never-ride proof is manifest-tables + token-string-absence: the
- blob store's contents are not swept for the token VALUE (the probe mints no blob);
- the command_log's provenance rows may lawfully NAME the mint command.
- - - no concurrency or load claims (the two-DB sync rig is sequential delivery; no
- interleaved-writer matrix); no cross-version migration matrix (0001..0014 is THE
- supported prior baseline; a 0015-intermediate carrying P4-C content migrating forward
- is covered by the chain's monotonicity argument, not a second live run).
- - - RLS and the append-only trigger are probed at the CLI boundary (the hostile revise's
- typed refusal): the pg_catalog-level policy definitions themselves are migration
- 0015..0019's own pins (test_substrate/test_migrations), not re-proven by this slice.
- - - the Phase 4 exit gate (record 71 §5) is the MERGE-time obligation: every P4 outcome
- row verified landed AT the merge — this slice's own proof covers the P4-F row; the
- gate itself runs at the merge, never inside this PR.
- - - the standing family-wide classes carry forward unchanged: the F-072-1 _nte_canon_id
- pattern, the F-074-1 leading-dash argv-value family (the = forms closed at the
- wrapper boundary by CLAIM-078; the CLI's direct exposure routed), F-073-6,
- F-075-3/F-076-1..4 + F2-078-2 (the substrate grammar owner's slice),
- F-075-5 (D-011's governed-purge widening).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: af8895cbb057850a51fa8fecb4dd23d5055cfa7b9abcfca83a8c894c889448b7
- reviewed_diff_sha256: 2f003076bfc482eb54c7d8a2849108425274015a3e69c5363571100d3629c085
- disposition: PASS
- findings: 5 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): 4d8f4796fe86ca50e497e60348e2f96dcb1681bd8d14eb14cae713d0d153c099
