# PROOF SHEET — slice claim-064-p400c-capability-matrix (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): d44b3e9fe6c3d97d99978a3e73cbaff698217ff1
- generated (last record's timestamp): 2026-11-06T07:19:25.262009+00:00
- run records: 12

## Run records (command, exit, output digest)
- `python3 harness/tests/test_capability.py` -> exit 0 · output sha256 ced89b21b65dbaa4 · 2026-11-06T05:31:15.382959+00:00
- `python3 harness/tests/test_capability.py` -> exit 0 · output sha256 ced89b21b65dbaa4 · 2026-11-06T05:31:17.224346+00:00
- `python3 harness/tests/test_capability.py` -> exit 0 · output sha256 ced89b21b65dbaa4 · 2026-11-06T05:31:19.068409+00:00
- `make verify` -> exit 0 · output sha256 20fcf45ec2e04e9c · 2026-11-06T05:36:37.531641+00:00
- `make verify` -> exit 0 · output sha256 8d95172c664b8c89 · 2026-11-06T05:46:36.776663+00:00
- `make verify` -> exit 0 · output sha256 0d9bdfb53d9eb694 · 2026-11-06T06:10:26.479339+00:00
- `python3 harness/tests/test_capability.py` -> exit 0 · output sha256 b204d2b54e046816 · 2026-11-06T07:06:22.195738+00:00
- `python3 harness/tests/test_capability.py` -> exit 0 · output sha256 b204d2b54e046816 · 2026-11-06T07:06:24.493987+00:00
- `python3 harness/tests/test_capability.py` -> exit 0 · output sha256 b204d2b54e046816 · 2026-11-06T07:06:26.803032+00:00
- `make verify` -> exit 0 · output sha256 ceaecaf8b10602ab · 2026-11-06T07:11:43.689605+00:00
- `SLICE=claim-064-p400c-capability-matrix GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 54729bdba709ae53 · 2026-11-06T07:18:15.845586+00:00
- `ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-064-p400c-capability-matrix python3 -I /home/z/my-project/verification/anchored/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 441e37519ddf1ad2 · 2026-11-06T07:19:25.262009+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-064 / P4-00c (the format
- capability matrix + extraction readiness; LAW-04; never empty-by-omission).
- WHAT THIS SLICE PROVES: the system's format capabilities are DECLARED,
- MEASURED, and RESERVED — user-visible, never marketing, never a silent miss.
- The DECLARED matrix (capability.py matrix: text/plain the FIRST APPROVED
- format — native text, reflow, NO OCR, the extractor named — declaring
- exactly what the landed machinery does, never more). The MEASURED row
- (capability.py measure: the readiness vocabulary ready/not_extracted/
- building/failed/stale as typed answers at exit 0, derived at the real
- boundary from the owner-scoped generation + passage reads + the blob — the
- derivation pinned by TWO corpora (3/1.0 and 5/1.0) plus the round-3 probes
- (Markdown heading attach-forward 3/1.0, single-word 1/1.0, leading-blank
- 25/27=0.925926 hand-computed, the whitespace-only source refusing
- ARV-EXT-001 at extract and answering not_extracted/0/0.0 at measure). The
- RESERVED surface (source-open/position -> P4-A/B, the contract sketch, the
- README note). The README rewritten to the frozen P4-00b contract (the
- versioned search header, the bounded/paginated lists with their truth
- markers, the api_version field, the capability section). The per-family
- ARV-QRY-001 hints (list-notes/list-bookmarks/list-captures + the source and
- anchor-honest forms) with the template-level no-oracle re-verified on all
- families. The three-round fresh-context SEV chain: round 1 (agent-ee8ed9dd)
- BLOCKED — the re-committed anchored driver (P1, the #98 class re-caught:
- removed from the index AND moved out of the tree) + the failed-state gap
- (P2, repaired: the planted-RAISE fixture + the fail_reason field) + the
- derivation pin (P3, repaired: the second corpus); round 2 (agent-9fd4f420)
- PASS — every repair verified live; round 3 (agent-ce9d9e53) FINAL PASS —
- 13 adversarial probes, zero open P0/P1/P2.
- THE HONEST LIMITS (what this slice does NOT claim):
- 1. THE SERVING-GENERATION FIELD IS P4-A/B's (round-1 F2, ROUTED): measure
- reports the LATEST generation — a crashed or failed RE-extract over an
- existing current generation answers building/failed while the source
- stays fully readable (extract.py's own "previous current STAYS current"
- contract; the round-2 agent re-observed the previous generation serving).
- The serving-generation distinction lands with the read-position surface.
- 2. THE STALE STATE IS STRUCTURALLY UNREACHABLE TODAY (disclosed): the
- source row is immutable and the ARV-CAP-005 append-only trigger refuses
- even a superuser digest UPDATE (the round-3 agent's probe 11 observed
- the refusal); the state is derived honestly at read time and named in
- the vocabulary, but no suite pins it because no legal path reaches it.
- 3. THE UNREADABLE-BLOB FORM (round-1 F7, disclosed): a source whose blob
- cannot be read answers state=ready with coverage=0.0 (the passage
- counts stand; the coverage honestly 0) — the form looks
- self-contradictory; the recovery walk is the repair path (P3-02's
- machinery).
- 4. THE WHITESPACE-ONLY SOURCE (round-3 F12, disclosed): extract refuses
- ARV-EXT-001 (zero content blocks) and measure answers not_extracted —
- honest (no generation exists) but the row does not name the refusal
- that precedes it; naming it would couple the readiness read to the
- extract path's history — a later slice's call.
- 5. THE RUN-RECORD PROVENANCE (the standing F11/F5 class): run-01..06's
- commit fields name the then-HEADs while the measured working trees
- carried the respective GREEN/repair content uncommitted; the substance
- re-verified at the committed final tree by SEV rounds 2-3 and by
- run-07..10 (the final-tree records).
- 6. THE STANDING LIMITS: the export/migrate version-field exclusion (P4-00b's
- notverified) still stands; the CI run is authoritative at PR time; the
- fresh-context labels are not cryptographic independence (ARV-SEV-007);
- no format converters beyond text/plain (P4-A's per-format work), no OCR
- (its own gate), no reader-client work (the separate repo); Q6-Q12 and
- D-014 stand open at their recorded scopes.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: bfaeb62a9d199767aa863b2e122b702f41dc7e640a18c21bae45e9ea5a01fd5f
- reviewed_diff_sha256: 1fac5b54db5b6315b0dc0a4d5de714bfda1783394d0bec0a1ab00ce8acb83c56
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 5

## Assembly
- sheet sha256 (of the content above, excluding this line): 2f759e70160fc5f66abd36c7c0688d06f21da5c179abd278eb39c9fdec4d2f46
