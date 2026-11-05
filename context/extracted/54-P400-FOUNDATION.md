# Record 54 — P4-00: the foundation chain opens (CLAIM-062) + the #96 close account

> STATUS: SESSION ENGINEERING RECORD (2026-11-05; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 78. PR #96 MERGED this session (the Phase 3 exit gate, under INT-145); the CLAIM-062 PR follows at this slice's end.

## §1 — The #96 close (all observed live via the API) — PHASE 3 EXITED

PR #96 (CLAIM-061 — the Phase 3 exit gate): the five required checks green at the exact final head `83d6a09` (canonical-layer 127489140993, head-tools 127489141470, harness 127489141814, harness-suites 127489141481, harness-trusted 127489141722) AND on the merge commit `b1a4934` (canonical-layer 127493264951, head-tools 127493264108, harness 127493264691, harness-suites 127493264298, harness-trusted 127493264455); the merge-gate review D-042 (1a) `5791116812` posted 2026-11-05T19:50:37Z, two minutes before the merge; the recorded flip/merge/restore — the flip 200, the read-back observing 0 immediately, the settlement window, the merge clean at 2026-11-05T19:52:41Z, the restore 200, the protections re-read BYTE-EQUIVALENT (the five contexts strict, admins, 1 approving, dismiss_stale, no force pushes, no deletions); the branch deleted (204); 0 open PRs; only `main` on the remote. No ARV-SEV-003 refusal round this time — the digest was bound LAST over the final content head `a287ce1` and the LOCAL trusted-gate reproduction (run-05, both phases: the trusted suites + the gate, the exact S4c path) ran green BEFORE the push: the discipline held on the first attempt.

THE GATE'S VERDICT (the substance, not the ceremony): **PASS** — the uncoached clean-clone acceptance run completed the real user-like acceptance path with NO P0/P1 (the full capture-and-retrieve walk through the repo's own documented surface, the restart byte-identity, the export/restore equality, the truthful durability reads, six abnormal events); the separate graders walked every SYS row to passing suites they ran themselves and issued the FINAL VERDICT PASS; every §3.E criterion mapped to its evidence (record 53 §2); the routed register (six P2/P3 repairs) feeds P4-00a's scope directly.

## §2 — The Phase 4 elaboration (one phase deep, from the gate's actual evidence)

The NG-04 exception's own rule: the outcome rows elaborate into executable cards AT Phase-3 exit FROM ACTUAL EVIDENCE. The evidence: the exit gate's acceptance run + grader findings (record 53 §3-§5). The elaboration (PLAN's Phase 4 section, minted in CLAIM-062's commit A):

- **P4-00a (CLAIM-062, this slice)** — the truthful-acknowledgment contract + the user-facing entry: the six routed repairs as one behavior family (import/extract durability_rung; the restore completion naming the derived-rebuild step; get-capture's anchor_id; the labeled search output; a real --help for migrate.py; the README at the repo root).
- **P4-00b** — the client-contract freeze + the boundary test: the gate's uncoached acceptance path made mechanical (the DTO vocabulary frozen, the error-code surface as the contract, the bounded responses + pagination, the version field) — "a REAL contract test calls the API boundary".
- **P4-00c** — the format capability matrix + extraction readiness + the read-position reservation (P4-A's first format with it).
- **P4-A..F** — each elaborates at its own predecessor's landing, never earlier.

The design boundary held: P4-00a is ONE behavior family (the truthful user-facing surface), RED-first, bounded; the contract-test harness and the capability matrix are their own slices.

## §3 — The slice chain (in flight)

THE RED (LAW-11): test_contract.py — the CON registry pinning the six routed repairs, machinery-absent at the merged head `b1a4934` (red-01.txt; the typed record bound to the RED commit). THE GREEN: the ack fields (commands.py's import/extract arms), the restore completion's derived-rebuild naming (export.py), the anchor_id + the search labels (query.py), the real --help (migrate.py), the README (the repo root). The measured set + the SEV round + the artifact re-bind + the push + the PR + the five checks + the merge-gate review + the merge under INT-145 + the post-merge verification follow.
