# PROOF SHEET — slice claim-063-p400b-contract-boundary (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): e2bfa2adf9b5e423a9db55b37baee106f42d6f22
- generated (last record's timestamp): 2026-11-06T05:00:16.948077+00:00
- run records: 11

## Run records (command, exit, output digest)
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 76b5ce90bd6bc959 · 2026-11-06T03:00:56.043960+00:00
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 76b5ce90bd6bc959 · 2026-11-06T03:01:10.550536+00:00
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 76b5ce90bd6bc959 · 2026-11-06T03:01:22.595628+00:00
- `make verify` -> exit 0 · output sha256 dbd9f6af60a1408f · 2026-11-06T03:16:38.690217+00:00
- `make verify` -> exit 0 · output sha256 97b2a4e470a8c405 · 2026-11-06T03:21:32.235784+00:00
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 510068fd393f15a7 · 2026-11-06T04:44:27.258124+00:00
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 510068fd393f15a7 · 2026-11-06T04:44:39.715943+00:00
- `python3 harness/tests/test_boundary.py` -> exit 0 · output sha256 510068fd393f15a7 · 2026-11-06T04:44:52.078349+00:00
- `make verify` -> exit 0 · output sha256 2e9b64a0808baa09 · 2026-11-06T04:49:40.349673+00:00
- `SLICE=claim-063-p400b-contract-boundary GATE_DIFF=origin/main make gate` -> exit 0 · output sha256 de9287c5d1167a6c · 2026-11-06T04:58:30.104658+00:00
- `ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-063-p400b-contract-boundary python3 -I tools/trusted_gate_anchored.py --repo /home/z/my-project/Arivoo --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` -> exit 0 · output sha256 250db8dccca5d1e0 · 2026-11-06T05:00:16.948077+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-063 / P4-00b (the client-contract
- freeze + the boundary test; LAW-04; never empty-by-omission).
- WHAT THIS SLICE PROVES: the documented client contract is a FROZEN vocabulary
- exercised END-TO-END as a permanent suite at the REAL boundary — the Phase 3
- exit gate's uncoached acceptance path made mechanical (BND-01..06, the suite
- runs green at the real CLI against a clean migrated database): every write ack
- of every one of commands.py's 16 registered verbs AND extract.py's acks,
- committed AND replayed, carries api_version=1 (the compatibility matrix's
- foundation) and durability_rung=local_durable (the F3 residual closed —
- SYS-01's every-write rule on EVERY acknowledgment path, RTM §4.3 item 3); the
- ack grammar frozen (status in {committed, replayed}; rung in SYS-01's frozen
- four); the typed-error surface as the contract (ARV-CMD-409/CAP-006/CAP-007/
- NTE-006/QRY-001 both directions/QRY-003/QRY-004 — each exit 1 + the FAIL
- prefix + zero effect, the cross-owner no-oracle pinned at the REAL objects);
- the list arms bounded + paginated (--limit default 100 bounds 1..1000 with the
- typed ARV-QRY-004 for every bounds violation INCLUDING the non-integer form,
- --after the uuid-validated keyset cursor, the '# api_version=1' header, the
- observed '# more=' truth marker, the empty owner's header+marker-alone answer);
- the version field on every read surface (the get-* bodies, every history row,
- resolve-anchor's answer, the search header, the list headers). The three-round
- SEV chain: round 1 (agent-837e1143) BLOCKED — one P1 (the vacuous cross-owner
- pin) + one P2 (the census width) both repaired RED-first/disclosed; round 2
- (agent-7493b68e) verified every repair REPAIRED + the routings honest, PASS;
- round 3 (agent-fd75db21) the FINAL independent verdict — 19 adversarial probes
- (uuid-cursor canonicalization, injection cursors, marker-laden content framing,
- tombstone parity under the new header, the crash-path replay's rung+version,
- cross-family cursors), PASS zero open P0/P1/P2.
- THE HONEST LIMITS (what this slice does NOT claim):
- 1. EXPORT.PY'S RESTORED LINE AND MIGRATE.PY'S OPERATOR OUTPUT CARRY NO VERSION
- FIELD — they are not the client API (the operator/deployment surface); the
- call is a later slice's, named here so it is a DECISION, never an omission.
- 2. THE ROUTED P3s (each a bounded gap, its routing recorded — never silently
- dropped): (F5) the README's surface examples lag the frozen contract (the
- stale search-header example at README.md:69; no api_version/list-marker/
- pagination docs) — ROUTED TO P4-00c, whose capability-matrix work rewrites
- the README's surface docs; (F10) the frozen ARV-QRY-001 refusal hint says
- "capture list" on the note/bookmark arms too (pre-existing at base, byte-
- identical there, now frozen byte-level by the template-equality pins) —
- ROUTED TO P4-00c; (F8) one leaked tempfile blob dir per suite run (the
- CON-suite house pattern) + the duplicate commit messages on 357a32f/42c9441
- (cosmetic; history rewrite forbidden) — disclosed, not repaired.
- 3. THE RUN-RECORD PROVENANCE (F9/F11, rounds 2-3): run-01..05's commit field
- names the then-HEAD 42c9441 (the red-record commit) while the measured
- working tree carried the GREEN implementation uncommitted — the SUBSTANCE
- is true (the same content re-verified at the committed tree by SEV rounds
- 2 and 3, by make verify inside the PR-mode gate, and by run-06..09 at the
- true final tree); the field misnames the tree, disclosed here. The repair
- commit's message attributed the F5/F8 routings to "notverified + record 55"
- before either carried them — THIS file is that record (F9's own catch).
- 4. THE PIN-STRENGTHENING DISCLOSURE (round-1 F1): the amended cross-owner pin
- verified GREEN immediately — the defect was the PIN's vacuity, not the
- product (the law held live, independently probed by the SEV round-1 agent
- before the repair); no product-side RED was observable for it.
- 5. THE BYTE-FORM CHANGE (round-1 F7, disclosed): the read bodies and history
- rows now serialize through Python's json.dumps (space-separated pairs)
- where Postgres's row_to_json emitted compact separators — no in-repo
- consumer pinned the byte form (grepped by the SEV round-1); the framing
- law (ONE escaped line per row, U+2028/U+2029 raw) is preserved and probed.
- 6. THE STANDING LIMITS: the CI run is authoritative at PR time (the local runs
- stand in until the five checks observe the exact final head); the SEV
- rounds are fresh-context executions — a differing context label is not
- cryptographic independence (ARV-SEV-007's standing limit; the three rounds
- + the boundary suite are the protocol); the uncoached README walk is not
- re-run this slice — the acceptance path it exercised IS the BND suite's
- own fixtures (that is this slice's point: the gate's uncoached path made
- mechanical); Q6-Q12 and D-014 stand open at their recorded scopes.

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 968e54414191da357812ff5d1250957197cc266b8d4a9675b0fe67ee26951216
- reviewed_diff_sha256: 3ed1e239941b5f8fa3e4d5536b8d1f3649d064c803e055ab5eccbbb46ae90ca3
- disposition: PASS
- findings: 3 (open P0/P1: 0)
- not-verified entries: 4

## Assembly
- sheet sha256 (of the content above, excluding this line): 3991d737dc6ddfbf246a7f54015d12ca94e959b6e8596134dddc5f5cc3213e10
