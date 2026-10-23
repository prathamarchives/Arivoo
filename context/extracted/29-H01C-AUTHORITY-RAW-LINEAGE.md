# 29 — H-01c-authority: the raw manifest/quote lineage (CLAIM-036)

> STATUS: SESSION ENGINEERING RECORD (2026-10-23; the session's intent refs: the standing do-not-stop chain INT-131/132/134/135/136 — no new owner turn this slice; D-041/D-043's H-01c-authority card routing + the review's ordered Action 4 first half). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 44. PRs this session: PR #70 (CLAIM-035, MERGED at `b244c634` — its close observations carried by THIS slice per rule 4) + the CLAIM-036 PR (this branch; its number + merge outcome record in the close row per rule 4).

## 1. What the owner asked (verbatim — no new owner turn this slice)

- No new owner turn arrived between CLAIM-035's merge and this slice's work. The operative authorization is the standing chain: INT-131/INT-132 ("i said do not stop. until phase 4-5 is done.. continue following the the directive..." / the five-action sequence), restated by INT-134 ("then why did you stop, you dont have to stop to fucking tell me... and just keep working towards it until doneee phase 3 and 4..."), INT-135 ("resume whereever u left offf, dont stop until phase 3-4 is done"), and INT-136 ("pushhh") — all preserved verbatim at record 28 §1 (committed in PR #70 before the mints). The review's ordered Action 4 (INT-132/D-043): "Complete H-01c-authority, then H-01c-evidence/privacy, then the H-02 systems-engineering verification gate" — this slice is its first half, worked under D-042's standing per-slice merge authorization with NO PAUSE after PR #70's merge (the do-not-stop form).

## 2. Starting state

- fresh main `b244c63` (PR #70's merge, 2026-10-23T12:38:30Z; local == origin; post-merge run `39954854214` five jobs green; make verify GREEN 52/0 at the fresh main — the CLAIM-035 close observations recorded in the CLAIM-035 close row, carried by this slice)
- the rig running (rebuilt at the session-28 preflight; `make migrate` verified; no environment change since)
- the card's defect surface re-read at the live HEAD: VER-802's `digest not in manifest` is a WHOLE-MANIFEST grep (the candidate controls the manifest copy), the quote extraction is straight-double-quotes-only, and a raw-cited entry with no extractable quote passes silently — each hole confirmed by reading `tools/verify_canonical_layer.py` c8/VER-802/803 paths at `b244c63`

## 3. Task and scope

- the requested work: the H-01c-authority card (PLAN: "raw manifest/quote lineage (A12/A17; disjoint)") — RED-first, its own bounded slice, per D-043's order
- bounded scope: the verifier's raw-lineage binding (VER-805 + the RAW_ANCHORS trusted map), the quote-extraction fail-closed forms (VER-803), the floor's 4 new discriminating cases (MUT-32..35), the manifest's §8 reanchor register (the schema + the lockstep note), the floor-test comment repair
- non-scope: NO raw-file edits (the card's explicit rule: "Never alter actual owner raw files to satisfy a test" — every mutation runs on the disposable fixture); no manifest platform change; no H-01c-evidence/privacy content (F-007 — the NEXT slice); no workflow/gate weakening; no Q10 claims

## 4. Results

- **VER-805 (new, the card's "one behavior"):** a raw source + candidate manifest reanchor cannot pass merely because the candidate changed both — each raw file binds to its OWN manifest row (the wrong-row relocation refused) AND to the trusted prior anchor (`RAW_ANCHORS`, the base-owned map inside the verifier — the canonical-layer CI job runs the BASE-ANCHORED judge, so the map is the state a candidate tree cannot rewrite); the ONLY distinguishable change path is the manifest §8 reanchor register row (prior == the trusted anchor, new == the actual digest, an owner-authorization INT-/D- that RESOLVES, a date)
- **VER-803's fail-closed quote forms:** the extraction now covers straight AND curly spans (fabricated curly-quoted content is checked and refused — the old straight-only regex let it pass), and a raw-cited entry carrying NO supported quotation fails closed (source metadata without a checkable owner word is a fidelity hole, never a silently-validated pass)
- **the floor's 4 new cases (MUT-32..35), RED-first:** all four observed NOT CAUGHT at the predecessor form (commit 6cbcd75's tree: the new driver over the unmodified verifier — ARV-FLOOR-001, red-01.txt), then CAUGHT at the repaired tree (green-01.txt: 4/4; green-02.txt: the FULL floor 35/35, zero regression on MUT-01..31)
- **the manifest §8 register:** the schema + the lockstep obligation recorded in BOTH files (the INT_HEADER-precedent copy pattern: the map is the trusted copy, this file the human-readable register); the register carries NO rows (the corpus is unchanged since D-025) — the "allowed append behavior" path exists and is distinguishable
- **the verifier's check count: 52 → 53** (VER-805 added); the real tree passes 53/0
- the rider: CLAIM-035's close row (PR #70's merge observations — the per-thread pass's observed result: 4 threads read + dispositioned BEFORE resolution, CodeRabbit's second pass confirmed; the merge SHA `b244c634`; the post-merge run `39954854214` five green; the three branch deletions 204; the protection restored verified: 1 review, strict, 5 contexts, admins)

## 5. Files changed

- `tools/verify_canonical_layer.py` — RAW_ANCHORS (the trusted map, lockstep-documented) + VER-805 + VER-803's two fail-closed forms + _fragments' curly outer-mark strip (D-041's card subject-files)
- `tools/verify_selftest.py` — the 4 cases + the 4 helpers (digests read from the manifest at mutation time, never hardcoded — the re-target class) + the case-set range MUT-01..35 (D-041)
- `context/SOURCE-COVERAGE-MANIFEST.md` — §8 the reanchor register (schema, empty, the lockstep note) + the §5 contract list's VER-805 line (D-041)
- `harness/tests/test_mutation_floor.py` — the header comment's derived-count repair (the stale "all 30" form; the count is derived from the case list — the historical GREEN 30/30 comments left as written) (D-041)
- `CLAIMS.md` — CLAIM-036's open row (D-038) + CLAIM-035's rule-4 close row (the rider)
- `STATE.md` / `AGENTS.md` — the post-truth sync (the slice at its PR; next H-01c-evidence/privacy) (D-043)
- `context/WORKLOG.md` — Task 44 (P-15)
- `context/extracted/29-H01C-AUTHORITY-RAW-LINEAGE.md` — this record (D-042)
- `harness/runs/claim-036-h01c-authority-raw-lineage/` — scope.txt, red-01.txt, green-01.txt, green-02.txt, the proof set (D-041/D-042)

## 6. The ACTUAL commands (each run ALONE, each exit read — nothing chained, nothing after a gate)

- the RED capture at commit 6cbcd75's tree (the stash form: the repair material stashed, the tree = the driver cases + the unmodified verifier): `python3 tools/verify_selftest.py --only MUT-32,MUT-33,MUT-34,MUT-35` → exit 1 — SELF-TEST RED, 4 case failures, all ARV-FLOOR-001 (red-01.txt)
- the repair verification: `python3 tools/verify_canonical_layer.py` → exit 0 (53 checks, 0 failures at the repaired tree)
- the GREEN capture: `python3 tools/verify_selftest.py --only MUT-32,MUT-33,MUT-34,MUT-35` → exit 0 (4/4 caught — green-01.txt); the FULL floor `python3 tools/verify_selftest.py` → exit 0 (35/35 — green-02.txt)
- **the floor's own guard caught this slice's first capture attempt (recorded honestly):** writing green-01.txt INTO `harness/runs/` while the floor ran changed the corpus mid-run → ARV-FLOOR-002 "the corpus source changed under the run" → the run REFUSED (exit 1). The repair: capture to /tmp, copy in after the run. The guard worked exactly as designed — the capture note inside green-01.txt records it
- **the walls' second catch, at the proof-set capture itself (run-04, exit 1):** the gate_dispatch suite went RED over the committed tree with three named codes — the honest catch read in full: (1) ARV-CLM-006 + ARV-CLM-002: CLAIM-035's open row still stood in the Open table while its close row landed (the exact KB-CLM-006 drift class, plus the overlap it created) — the open row retired (the ID appears once); (2) ARV-RED-002: test_mutation_floor.py's comment repair changed its digest against the frozen red record (LAW-11) — the amendment recorded via make red (comment-only, zero assertions changed). Both repaired at commit 997fb0a; the suite re-captured GREEN at that head (run-05, exit 0, in the final set). The failed capture itself is PRESERVED in the sheet as run-01 (recovered from git byte-identical after the numbering collision below) — the catch's own evidence, the claim-033 run-11 precedent
- the proof set: the 11-command re-record at the fix head (run-02..12: the suites + the known-bad matrix + the verifier 53/0 + the full floor 35/35 + make verify) — every exit in the run records; the failed capture recovered from git byte-identical as run-01 (its commit field honestly 18c8ed0, exit 1 — the catch's own evidence in the sheet, the claim-033 run-11 precedent); the PR-mode gate ALONE (`--diff origin/main`, exit via PIPESTATUS)
- **the third catch — the proofsheet's count-based numbering (a defect class found, routed, not silently fixed here):** write_record numbers a new record `len(glob(run-*.json)) + 1` — with out-of-sequence pre-existing files (the preserved run-04 alone), the numbering collided and OVERWROTE the middle captures one by one (each overwrite left the count unchanged, so every later capture re-wrote the same slot). The overwrites were caught by reading the assembled sheet ("3 run records" against 12 captures — never trusted the count line); the failed record was safe IN GIT (997fb0a carries it). The repair in-slice: the recovered record as run-01, the clean re-capture run-02..12, the sheet regenerated from the honest 12. The numbering itself (count-based vs max-based — the overwrite class) is ROUTED to the H-01c-evidence/privacy slice (proofsheet/red-record machinery is that card's subject surface); NOT silently fixed here (a harness change outside this slice's declared scope, LAW-06)

## 7. Evidence

- red-01.txt — the observed RED at commit 6cbcd75's tree: all four new cases NOT CAUGHT (ARV-FLOOR-001 × 4) — the holes proven live, never asserted
- green-01.txt — 4/4 caught at the repaired tree (the capture-method note inside records the ARV-FLOOR-002 catch)
- green-02.txt — the FULL floor 35/35 (zero regression: MUT-01..31 unchanged and green)
- the verifier at the real tree: 53 checks, 0 failures (VER-805 green over the unchanged corpus; the manifest §8 register parses; the quote forms green over the real 118 entries — the fail-closed probe ran first: NO raw-cited entry has zero extractable quotes, so the new check cannot false-RED the real ledger)
- the proof sheet at the content head (PASS ARV-PRF-004) + the pushed head's GitHub five-check run (observed in the PR, INT-104)

## 8. Failures (the honest ledger — each with its repair)

- **the registry drift + the red-record miss (run-04's catch, the walls working pre-push):** the CLAIM-035 close row landed with its open row un-retired (the KB-CLM-006 both-tables class + the ARV-CLM-002 overlap), and the test_mutation_floor comment repair went unamended against the frozen red record (ARV-RED-002, LAW-11). BOTH caught by the gate_dispatch suite at the proof-set capture (exit 1, read in full, never skipped); both repaired at 997fb0a; the suite re-captured green at that head. The lesson: the rule-4 close-row append and the open-row retirement are ONE operation — the close row lands only WITH the retirement; and any tracked-test-file edit, however comment-only, needs its red-record amendment in the same slice
- **the capture-into-corpus miss (the floor's own catch):** green-01.txt's first capture attempt redirected the floor's output INTO `harness/runs/` during the run — a mid-run corpus change (the corpus enumeration includes the runs dir) → ARV-FLOOR-002 refused the run, exit 1. Caught by the floor's integrity guard in the same minute; the repair (capture to /tmp, copy after) applied immediately; the note recorded inside green-01.txt. The lesson: a floor/verifier run and its evidence capture NEVER share a live corpus path — the capture lands after the run's exit is read
- **the RED at the predecessor (the expected, honest RED):** all four card holes were REAL — the unmodified verifier passed every mutation (the coordinated reanchor, the wrong-row relocation, the curly fabrication, the stripped quote). Recorded in red-01.txt; the repair closed all four (green-01/02)
- **the stale-comment class in the floor test:** the header comment said "all 30 base mutations" while the case list had 31 — the derived-count rule (CLAIM-030) was already in the assertions; the comment repaired to the derived form in this slice (the historical session-23/24 "GREEN 30/30" comments left as written — they are true records of their time)

## 9. Unverified items (LAW-04 — the slice's honest list)

- VER-805 validates the reanchor row's FORM and the authorization reference's RESOLVABILITY — the authorization's GENUINENESS is the review layer's judgment (D-042 + the owner's merge authority), never a mechanical claim (recorded in the §8 register's honest-limit note)
- the trust chain rests on the canonical-layer CI job running the BASE-ANCHORED judge (verify.yml's anchored copies, sha256-verified against main) — the host-level workflow-definition protection remains H-01b-CI's EXTERNAL item (owner/admin settings, recorded never claimed, unchanged); Q10 (token/workflow-tamper hardening) remains owner-gated
- the floor's residual boundaries unchanged (the same-user/same-host child, the re-sessioning daemon class, the manifest-as-record-not-vault — stated in every floor output, never claimed closed)
- the pushed head's own walls verification is the GitHub five-check run, observed in the PR — no in-file result covers the pushed head itself (INT-104)

## 10. Open decisions

- unchanged: D-014 + Q6–Q12 — each blocks ONLY its named dependents; no new owner question raised or closed by this slice

## 11. Next action

- **H-01c-evidence/privacy (CLAIM-037)** — the F-007 card (the gate's RED control comparing frozen test identity against trusted prior state; the typed red records; the fail-closed suite registration; the canary redaction tests; the A16 narrowing) — RED-first, its own bounded slice, immediately after this PR merges, no pause; then H-02 (the SEV gate), then P3-00 (the RTM freeze)

## 12. Session close

- (complete at this PR's merge — the merge SHA + the CI run IDs + the post-merge observations record in the CLAIM-036 close row, appended by the next slice per rule 4; this record needs no second pass)
