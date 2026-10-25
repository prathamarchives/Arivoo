# PROOF SHEET — slice claim-048-p3k0-kernel-primitives (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 0b0d1d88f7badb7575c9d9dfe60b5af985ac5657
- generated (last record's timestamp): 2026-10-25T13:54:56.007921+00:00
- run records: 8

## Run records (command, exit, output digest)
- `python3 harness/tests/test_kernel.py` -> exit 0 · output sha256 f9686edbb769e783 · 2026-10-25T13:13:54.527464+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-25T13:13:56.507674+00:00
- `make verify` -> exit 0 · output sha256 247fdb53ac785e04 · 2026-10-25T13:16:44.924386+00:00
- `python3 harness/gate.py --slice claim-048-p3k0-kernel-primitives --diff origin/main` -> exit 1 · output sha256 6a7afa6f7b857dc7 · 2026-10-25T13:19:25.225719+00:00
- `python3 harness/gate.py --slice claim-048-p3k0-kernel-primitives --diff origin/main` -> exit 0 · output sha256 be3cba38357bfcfc · 2026-10-25T13:30:20.896146+00:00
- `make verify` -> exit 0 · output sha256 f91928a06c395e2b · 2026-10-25T13:47:00.989354+00:00
- `python3 harness/gate.py --slice claim-048-p3k0-kernel-primitives --diff origin/main` -> exit 1 · output sha256 913127589c271321 · 2026-10-25T13:49:31.860520+00:00
- `python3 harness/gate.py --slice claim-048-p3k0-kernel-primitives --diff origin/main` -> exit 0 · output sha256 515628169b050531 · 2026-10-25T13:54:56.007921+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the canonical encoding's pinned choices are contracts, not defaults-by-silence: NFC normalization (the same logical text in different normalizations is the SAME body); json-serialized with sorted keys and a version field (the 'arv_body_version' tag); any future change to either is a compatibility decision with its own bounded slice (persisted body_hash values are history — a re-encoding would change same-body equivalence for existing rows).
- - the concurrent same-key semantics resolve through the PK conflict path: the loser re-reads and answers the REPLAY when the winner's row is committed; a winner still INSIDE its transaction blocks the loser's INSERT at the row lock (that window's duration is the winner's transaction length — bounded by the same crash-matrix guarantees); no separate in-flight state row exists (the card allows 'the same recorded result OR an explicit retryable in-flight state' — the recorded-result arm is what landed, tested live).
- - the monotonicity floor is PROCESS-LOCAL: IDs minted by two processes at the same wall-clock instant may share a timestamp (within-ms ordering across processes is the random tail — the v7 property); a cross-process monotonic counter is unnecessary for the SYS-04 contract (index friendliness at ms granularity).
- - the target-mismatch guard pins the LOOPBACK shape ({127.0.0.1, localhost, ::1}) — the rig and CI's service; the owner's eventual deployed target (D-032's Supabase) joins the approved set as its own owner-scoped decision when P4-00's contract lands, never silently widened.
- - ARV-DB-003's mapping covers the connection-level failure classes observed on psql (could not connect / role does not exist / password auth); an exhaustive psql-error taxonomy is out of the kernel's scope — unmapped connection failures still surface raw (never silently swallowed).
- - the ARV-SEV-009 undecidable-base regression remains ROUTED as its own bounded follow-up (CLAIM-044's close row) — never folded here (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 65d1851842fb2770e9637f6aa2e20edf74156dade5e23f2100f899a5fd1fc63f
- reviewed_diff_sha256: 6b9b630dd658a03c4c115fa6c6d26d95d89b7b6e9ca23dea5e8d008389f9c834
- disposition: PASS
- findings: 5 (open P0/P1: 0)
- not-verified entries: 2

## Assembly
- sheet sha256 (of the content above, excluding this line): 9962034be93b1b8453615e5e2484b3aa92a5552898f7e4070aea8be27861835f
