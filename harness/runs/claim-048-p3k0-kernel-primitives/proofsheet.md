# PROOF SHEET — slice claim-048-p3k0-kernel-primitives (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 2bcdb00970dd05b268fa93063044a684c7288cba
- generated (last record's timestamp): 2026-10-25T13:30:20.896146+00:00
- run records: 5

## Run records (command, exit, output digest)
- `python3 harness/tests/test_kernel.py` -> exit 0 · output sha256 f9686edbb769e783 · 2026-10-25T13:13:54.527464+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-25T13:13:56.507674+00:00
- `make verify` -> exit 0 · output sha256 247fdb53ac785e04 · 2026-10-25T13:16:44.924386+00:00
- `python3 harness/gate.py --slice claim-048-p3k0-kernel-primitives --diff origin/main` -> exit 1 · output sha256 6a7afa6f7b857dc7 · 2026-10-25T13:19:25.225719+00:00
- `python3 harness/gate.py --slice claim-048-p3k0-kernel-primitives --diff origin/main` -> exit 0 · output sha256 be3cba38357bfcfc · 2026-10-25T13:30:20.896146+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the canonical encoding's pinned choices are contracts, not defaults-by-silence: NFC normalization (the same logical text in different normalizations is the SAME body); json-serialized with sorted keys and a version field (the 'arv_body_version' tag); any future change to either is a compatibility decision with its own bounded slice (persisted body_hash values are history — a re-encoding would change same-body equivalence for existing rows).
- - the concurrent same-key semantics resolve through the PK conflict path: the loser re-reads and answers the REPLAY when the winner's row is committed; a winner still INSIDE its transaction blocks the loser's INSERT at the row lock (that window's duration is the winner's transaction length — bounded by the same crash-matrix guarantees); no separate in-flight state row exists (the card allows 'the same recorded result OR an explicit retryable in-flight state' — the recorded-result arm is what landed, tested live).
- - the monotonicity floor is PROCESS-LOCAL: IDs minted by two processes at the same wall-clock instant may share a timestamp (within-ms ordering across processes is the random tail — the v7 property); a cross-process monotonic counter is unnecessary for the SYS-04 contract (index friendliness at ms granularity).
- - the target-mismatch guard pins the LOOPBACK shape ({127.0.0.1, localhost, ::1}) — the rig and CI's service; the owner's eventual deployed target (D-032's Supabase) joins the approved set as its own owner-scoped decision when P4-00's contract lands, never silently widened.
- - ARV-DB-003's mapping covers the connection-level failure classes observed on psql (could not connect / role does not exist / password auth); an exhaustive psql-error taxonomy is out of the kernel's scope — unmapped connection failures still surface raw (never silently swallowed).
- - the ARV-SEV-009 undecidable-base regression remains ROUTED as its own bounded follow-up (CLAIM-044's close row) — never folded here (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 8ec9627ec157db736b43d8b9d3d8a6f7e76b987ec4aad89d6a4bc1e6e0e07ec4
- reviewed_diff_sha256: faa39dcaa0d2295f5bf4b1c35ad41676b13cec5eac5d3176678d4083d7d27f68
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 2

## Assembly
- sheet sha256 (of the content above, excluding this line): f550809e838737d0e656444878bd507ba7d157f89fc9fb9daace7c9c86564790
