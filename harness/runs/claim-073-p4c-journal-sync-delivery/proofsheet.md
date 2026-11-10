# PROOF SHEET — slice claim-073-p4c-journal-sync-delivery (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 10339be47932e0314701a385246b87daaef3c8dd
- generated (last record's timestamp): 2026-11-10T15:58:38.248861+00:00
- run records: 15

## Run records (command, exit, output digest)
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 04430aea3ed6acb6 · 2026-11-10T13:46:38.545318+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 04430aea3ed6acb6 · 2026-11-10T13:46:52.800773+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 04430aea3ed6acb6 · 2026-11-10T13:47:07.138855+00:00
- `python3 harness/tests/test_journal.py` -> exit 0 · output sha256 bb621c0318508777 · 2026-11-10T13:47:14.406613+00:00
- `python3 harness/tests/test_journal.py` -> exit 0 · output sha256 bb621c0318508777 · 2026-11-10T13:47:18.750193+00:00
- `python3 harness/tests/test_journal.py` -> exit 0 · output sha256 bb621c0318508777 · 2026-11-10T13:47:23.114329+00:00
- `make verify` -> exit 0 · output sha256 dec17d577408c523 · 2026-11-10T13:53:39.937209+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 6c6be3811e8575f3 · 2026-11-10T15:23:22.204607+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 6c6be3811e8575f3 · 2026-11-10T15:23:37.501672+00:00
- `python3 harness/tests/test_sync.py` -> exit 0 · output sha256 6c6be3811e8575f3 · 2026-11-10T15:23:52.302142+00:00
- `python3 harness/tests/test_journal.py` -> exit 0 · output sha256 bb621c0318508777 · 2026-11-10T15:23:56.860531+00:00
- `make verify` -> exit 0 · output sha256 c468c1e88e4d2a06 · 2026-11-10T15:30:46.499646+00:00
- `env SLICE=claim-073-p4c-journal-sync-delivery GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 1c000549e6a1602f · 2026-11-10T15:55:56.175969+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-073-p4c-journal-sync-delivery python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 1 · output sha256 f2b49704f333e85a · 2026-11-10T15:57:06.478501+00:00
- `env ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-073-p4c-journal-sync-delivery python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 c1747e8d729b9408 · 2026-11-10T15:58:38.248861+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- CLAIM-073 — the honest not-verified list (LAW-04: the explicit statement, never
- empty-by-omission). The full SEV account: sev.json + sev-round-1.md + sev-round-2.md.
- - F-073-6 (P3, ROUTED, round 2's new finding): the import_source branch stages its
- blob BEFORE argv construction — a contained refusal (a wrong-typed field value) or
- the canonical ARV-SYN-009 work-dependency leg leaves a staging file behind. The
- F-073-3(a) class on the one family outside this slice's journal-scoped reorder;
- a strict improvement over the pre-repair crash (the row is still named and
- contained; only the staging file lingers). The same reorder (validate/encode
- before staging) recommended in a follow-up slice touching the import delivery.
- - The standing family-wide classes routed by the prior slices' reviews, unchanged
- here: the read arms' malformed-id echo (F-072-1's routing — the _nte_canon_id
- pattern's own family-wide slice, records 47-48 §9) and the landed families'
- raw-spelling boundary locks/bodies.
- - No fresh full-suite re-run inside the SEV rounds themselves: the rounds ran
- targeted probes (the repro, the two-DB walks, the digest checks, the code
- reads); the recorded runs (run-01..12: the sync suite x3 at the GREEN tree +
- the journal suite x3 + make verify; the sync suite x3 at the repair tree + the
- journal suite + make verify) stand as the suite evidence, spot-checked by the
- round-2 reviewer.
- - The SEV round-1 heavy probes were executed by a prior fresh-context agent whose
- context expired before report authorship; its raw captures (/tmp/sev073*) were
- re-verified selectively (digests, the repro, the code reads) by the round-1
- author. The chain is disclosed in sev-round-1.md's header.
- - No reader-client work (P4-B's repo); harness/client.py's surface unchanged at
- this slice — the external client contract proof vehicle was not extended here.
- - No @-reference resolution over journal blocks (P4-D's increment); no
- tombstone/restore machine on journal blocks (the §3.3 increment — D-011's
- governed-erasure question); no new journal read/write surface (CLAIM-072's
- landed arms unchanged — the bounded exclusions held).
- - red-01.txt's Tree header names commit A (f066b46) — the working tree at capture
- time, before the RED commit existed; reasoned no-fix (contemporaneous evidence,
- never rewritten post-hoc; the exact binding lives in the typed red-record
- amendment naming 7756bbd). red-02.txt discloses its working-tree form in its
- parenthetical (the mitigation applied prospectively).
- - The rig's env-reset repairs this session (the recycled pgdata's missing
- subdirectories recreated; the root-owned scratch-dirs cluster moved aside and
- re-initialized — the recorded FACT-001 rebuild pattern): no suite depends on
- any persistent database state; every run creates and drops its own scratch DBs.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: f562e07ea1e601a877fac3c2b877165fa51b6389da1f20abe11253e59ef4011a
- reviewed_diff_sha256: acac4831964c2462165fb4f3adb745293b790b585443d3660a3090a594b4842d
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 090c8f02cd7e2f319093a7adc2850a02fcf6924556eb6f583024e0455f79652e
