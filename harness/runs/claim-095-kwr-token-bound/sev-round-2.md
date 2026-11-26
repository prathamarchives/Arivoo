# SEV round-2 — the re-bind (CLAIM-095)

The round-1 PASS carried SEV-095-1 (P1): the red-record mint for
`harness/tests/test_kwr_bound.py` was a silent no-op — the first `red.py` invocation ran
before the suite's TESTS registration in `gate.py` (red.py iterates the TESTS tuple
only, the ONE home), so no record existed while record 80 and the worklog claimed one
(an overclaim, SEV-095-2's class).

## The repairs (evidence commit c2acbe8)

1. **The mint re-ran** after the registration landed:
   `python3 harness/red.py --red-commit 385ad7bb... --exit 1 --code "ARV-TEST-KBND
   (KBND-01..07...)" --note "..."` — binding_commit 385ad7b (the test-only commit),
   binding_sha256 the suite's hash at that commit, current_sha256 the repaired suite's
   hash, the no-op disclosed in the record's own red_evidence. The gate's
   ARV-RED-001/002/007 checks pass over the minted record (verified in the final gate
   run below).
2. **The documentation repairs**: record 80 §6/§7/§8 and the WORKLOG Task 117 entry now
   state the assembly-order gate refusal honestly (run-04's three failures: ARV-RED-008
   the registration, ARV-PRF-002 the sheet, ARV-SEV-001 the SEV — the last two the
   expected assembly order), the run-01 label corrected (the GREEN run at the
   implementation head; the RED evidence is the red record), and the artifacts' assembly
   order stated.

## The re-bind

`reviewed_diff_sha256` recomputed at c2acbe8 (the red-records.json edit + the doc
repairs changed the reviewed set): `694cb9f7132031b0d96923c1f876fc89aa3cbaa9d0827d44084a453c6ae8daff`.
base_sha unchanged (`1eab74a1...`, the merge-base). No new findings: the round-1
findings' resolutions are the repairs above; the disposition stands (PASS).

## Validation

`python3 harness/sev.py claim-095-kwr-token-bound` → GREEN (the record's own
staleness control now binds the evidence head; the sheet_section renders from this
record into the assembled proof sheet).
