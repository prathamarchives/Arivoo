# PROOF SHEET — slice claim-004-session-20-intake (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 026feada046f78c4e0b61e6b3a3e20074ce97e89
- generated (last record's timestamp): 2026-10-19T12:37:58.471165+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 3ca757dfb6c98197 · 2026-10-19T12:37:27.698057+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 df0456842e9b11ee · 2026-10-19T12:37:32.596460+00:00
- `python3 tools/isolation_check.py` -> exit 0 · output sha256 4b8f208f23cf8aa4 · 2026-10-19T12:37:32.774612+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 e6d25aa311b358de · 2026-10-19T12:37:58.471165+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - The A01–A18 audit findings are confirmed STATICALLY only (direct source read at 026fead) — none is dynamically exploited or RED-first reproduced in THIS slice; reproduction is the named cards' work (H-01a/H-01b/H-02/kernel/migration-oracle), and no finding is claimed fixed here
- - The turn-20 directive's verbatim §1 was transcribed through the session host, not byte-dumped: one transcription defect (the A03 block dropped; A04..A18 shifted one letter) occurred in the record's first draft and was caught by self-check BEFORE any commit and repaired in place — the incident and repair are recorded in the record itself; a byte-level diff against the original message was not mechanically possible from this host
- - H-01b, H-02, P3-00 RTM: not built in this slice (specifications/cards only); LAW-30 remains PLANNED until H-02's validator, gate wiring, known-bads, and CI evidence exist
- - The local rig (user-space Debian 17.11-0+deb13u1, port 5433) is a rebuilt convenience for local iteration, never evidence; the remote CI run at the PR head is the authoritative proof for this slice
- - The intake PR's own CI three-check result was not yet observed at record-assembly time (the runs directory is assembled before push); the post-merge observation is recorded at the session close

## Assembly
- sheet sha256 (of the content above, excluding this line): ddd3e410a9c99e4188b01381c78617c932372300d4cdc38aa7be8c3c776476ac
