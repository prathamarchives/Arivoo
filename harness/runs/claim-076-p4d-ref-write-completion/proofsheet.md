# PROOF SHEET — slice claim-076-p4d-ref-write-completion (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 9aad97d404790110eed0fb964980e38d8ae881fc
- generated (last record's timestamp): 2026-11-11T13:24:27.906444+00:00
- run records: 6

## Run records (command, exit, output digest)
- `python3 harness/tests/test_note_reference.py` -> exit 0 · output sha256 18e734ac08a245b1 · 2026-11-11T12:41:59.933185+00:00
- `python3 harness/tests/test_note_reference.py` -> exit 0 · output sha256 18e734ac08a245b1 · 2026-11-11T12:42:08.326361+00:00
- `python3 harness/tests/test_note_reference.py` -> exit 0 · output sha256 18e734ac08a245b1 · 2026-11-11T12:42:17.103724+00:00
- `make verify` -> exit 0 · output sha256 29128a93e359597a · 2026-11-11T12:49:22.927360+00:00
- `env SLICE=claim-076-p4d-ref-write-completion GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 6786dd0614cdc4bd · 2026-11-11T13:23:33.615599+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-076-p4d-ref-write-completion python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 ef329be1f6fce872 · 2026-11-11T13:24:27.906444+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - CLAIM-076 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json + sev-round-1.md.
- - - F-076-1 (P2, ROUTED): the all-digits oversize pin (>= 4301 digits) crashes the
- note --ref parser with an untyped ValueError traceback (CPython's int-str limit)
- instead of the typed ARV-NTE-006 — the exact commands.py twin of CLAIM-075's
- F-075-1 (repaired in query.py _ref_parse with the len>18 bound), PRE-EXISTING at
- the CLAIM-057 substrate's _nte_refs (reproduced by the reviewer on the OLD kind
- highlight identically), composed verbatim by this slice's vocabulary widening per
- the never-a-second-implementation doctrine; fail-closed, zero writes. Routed to
- the family-wide _nte_refs grammar slice (the pin-length bound before int()).
- - - F-076-2 (P3, ROUTED): a trailing-newline uuid passes the substrate's
- $-anchored _UUID_RE and dies at the session-marker layer as a typed ARV-CMD-010
- rather than the grammar's own ARV-NTE-006 — the F-075-2 commands.py twin; routed
- to the _nte_canon_id pattern's family-wide slice (the F-072-1 precedent, where
- CLAIM-075's SEV round 1 already routed the $ anchor).
- - - F-076-3 (P3, ROUTED): the unicode-digit and leading-zero pin normalization —
- the substrate's own isdigit law composed VERBATIM over the new kinds (the
- F-075-3 class); narrowing it here would be the forbidden second implementation;
- routed to the substrate grammar owner. The uppercase-hex uuid ask is
- canonicalized by the UUID column — the write boundary carries NO F-075-4-style
- echo debt (that class remains read-side only).
- - - F-076-4 (P3, ROUTED): the ARV-NTE-008 message says "one reference per target
- per revision" while the enforced law is one per (kind, target) — pre-existing
- substrate message wording, cosmetic, unchanged by this diff; routed with the
- grammar owner.
- - - the standing family-wide classes routed by the prior slices' reviews
- (unchanged): the read arms' malformed-id echo + the substrate's own $-anchored
- _UUID_RE (F-072-1's routing), the leading-dash argv-value family (F-074-1), the
- import_source staging-before-argv residue (F-073-6), F-075-5 (the landed
- resolve-anchor's purge-unawareness — D-011's governed-purge command slice).
- - - no agent-facing reference resolution (P4-E's increment); no reference graph
- queries (P5's world); no new entity families; no reader-client work (P4-B's
- repo).
- - - no concurrency probes — the single-statement/one-transaction laws verified
- structurally and behaviorally, never under actual parallel writes (the SEV
- round's honest limit, the standing class).
- - - no performance/DoS measurements (the F-076-1 crash class verified
- functionally; no cost curves measured).
- - - the journal-block family carries no tombstone machine at this slice (the
- §3.3 increment — D-011's governed-erasure question; a tombstoned-state
- reference answer for journal_block targets is therefore unreachable by
- construction, not unimplemented drift).
- - - the revise_note --ref path shares create_note's _nte_refs parse by code
- reading (the SEV round probed create_note live; revise_note's arm not
- separately probed).
- - - migration 0018's failure/rollback path not deliberately fault-injected (the
- clean apply + verify observed on five fresh databases; ARV-MIG-009's own suite
- covers the runner's rollback law).
- - - the crash matrix (crash.py) around new-kind refs covered by NTR-10's generic
- refs pins (GREEN in the suite run), not re-probed individually by the SEV rig.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: baae71e2c01a4486c81d8991607fd54e5379a9b561d213ba31c4a7ce42cd8194
- reviewed_diff_sha256: 8b5b0c8667e18565ae2a3784821893eb8215afd1c1636f51fad02d7ecb9c3cec
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 12

## Assembly
- sheet sha256 (of the content above, excluding this line): bbc42f560711a341af9d8d95c0b076525b2db359b05e0f350cf20b8a6501cd59
