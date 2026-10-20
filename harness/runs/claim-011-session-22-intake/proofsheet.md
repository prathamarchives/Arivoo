# PROOF SHEET — slice claim-011-session-22-intake (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 1978812dc9756f745443107b323e643ed03f5e12
- generated (last record's timestamp): 2026-10-20T07:55:11.424576+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 47138eefef831252 · 2026-10-20T07:54:44.606154+00:00
- `python3 harness/claims.py` -> exit 0 · output sha256 6beec6ef5d385ac5 · 2026-10-20T07:54:44.674236+00:00
- `python3 tools/isolation_check.py` -> exit 0 · output sha256 4b8f208f23cf8aa4 · 2026-10-20T07:54:44.878488+00:00
- `make verify` -> exit 0 · output sha256 87be35f80cf9ae5e · 2026-10-20T07:55:11.424576+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the two owner-forwarded review artifacts are preserved as received (the CodeRabbit file a faithful structured transcription of the gateway's PDF text extraction — its export pointers omitted, noted in the file); their FINDINGS are triaged static at the live HEAD, but REPRODUCTION is the receiving cards' RED work — nothing is claimed fixed by this intake
- - the 13-finding triage is a source-read verification (record 22 §2), not a behavioral reproduction; the F-008/F-006 behaviors are confirmed by direct code-path reading (gate.py:199's PR-mode exemption; gate.py:56's import-time registry execution) — the RED regressions land in H-01c-claims/H-01b-CI
- - the live-API evidence (protection/PR/run states, the arivodesign observation) is snapshot-at-write — re-observe at preflight (INT-104)
- - no fresh technical verifier and no SEV for this intake slice — the pre-H-02 discipline, the honest gap stated in record 20 §8; it closes when H-02 is live
- - the ARV-CLM-003 catch (the missing retroactive notation on INT-127's reservation) was caught live by the registry check and repaired in-slice; the repair is in the claim row, the catch is recorded here and in the PR body — the proofsheet's recorded claims.py run is the POST-repair green run
- - the SECOND catch, from CI: the harness job's gate refused ARV-PROT-002 (DECISIONS.md protected, the scope declaration carried no owner ref) — and the same gate had passed locally because the local run happened at the MID-SLICE HEAD (part 1 committed only), so the base...HEAD diff judged an incomplete change set; the standing lesson restated: the local gate is evidence only at the FULLY-COMMITTED candidate HEAD. Both the repair (owner refs on the protected-path declarations) and this lesson are recorded here and in the PR body
- - the supabase CLI is provisioned for readiness only; the local Supabase stack requires a container runtime absent from this sandbox; Q12 remains the owner gate — no provider decision made or implied

## Assembly
- sheet sha256 (of the content above, excluding this line): 0e8fe71659b7d907b4909d23f87a4dd990219e9066a633f31eafa896551c9a89
