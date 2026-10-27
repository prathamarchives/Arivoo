# 44 — CLAIM-053: P3-03b — the anchor resolution + the Q8 anchor-stability spike

Session 31 continuation (the standing do-not-stop chain INT-134/135/138/139/140);
PLAN's P3-03 card's anchor half, the bounded split per LAW-05 (the extraction
generations were CLAIM-052's).

> STATUS: SESSION ENGINEERING RECORD (2026-10-27; intent refs INT-127/131/134/135/138/139/140; decision refs D-036/D-038/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 62. PR this session: #88 (this slice; outcome recorded only after it happens). THE SEV record for this slice: `harness/runs/claim-053-p303b-anchor-resolution-q8-spike/sev.json` (the rounds' outcome recorded there only after they run).

## 1. What the owner asked (verbatim)

> 87 is not live. not merged... 86 is the last merge hope you have not lost the work... don't stop why did you even stopped rn??? dont do that again.. 下一步：CLAIM-052 的 commit B — 迁移 0006 + extract.py + EXT-01..12 变为绿色 (GREEN) → 最终确定 (finalize) → 合并 → CLAIM-053 (anchor resolution + Q8 spike) → P3-04..09 → Phase 3 退出网关 (exit gate) → P4。遵循您的一贯指示，在每次 commit 后 push；完整的交接协议已记录在 worklog 中。PAT 轮换提醒持续有效，直至项目完成。now your next echeckpoint is when phase 3 is completed and verified to give the reports do not stop before that
>
> scan the workspace, the work you did give me the report

The binding directives (the standing chain INT-134/135/138/139/140): no pause
through Phase 3 and Phase 4; the push-after-every-commit discipline standing;
the next owner checkpoint fixed at the Phase 3 exit gate's verified completion;
the PAT rotation reminder standing until the project completes. This session
so far: the workspace scan REPORT delivered (nothing lost — the push-early
discipline held); PR #87's round-3 + residual findings fixed, dispositioned,
CodeRabbit-confirmed; PR #87 MERGED under D-042; this slice (CLAIM-053) opened.

## 2. Starting state — the post-#87 preflight

- The remote truth at entry: main `364f30e` (the PR #87 merge, 2026-10-27T07:18:37Z — the D-042 recorded single-actor path reproduced: the self-approve 422, the merge 405, the PUT flip 1->0, the merge, the restore 0->1, the protections re-read byte-equivalent); the post-merge run five green at the merge commit (run ids 122062577006..31 observed live); the branch deleted (204); 0 open PRs.
- The PR #87 review chains closed COMPLETE: the SEV two-rounder (round 1 BLOCKED on the REAL NUL-corruption P1 -> fixed RED-first as EXT-13; round 2 PASS) + the CodeRabbit rounds 1-3 (round 3: the SQLSTATE-vs-message-text classification — the localized genuine 40P01 retryable EXT-16, the P0001 impostor failed EXT-17, EXT-14 hardened to the genuine code; CodeRabbit CONFIRMED at b467a55) + the round-2 RESIDUAL thread (the sev.json proof-pointer finding, missed by the round-2 sweep — found by THIS session's merge-gate thread enumeration over all nine threads via the graphql resolved-state read, the pointer repaired, the disposition posted, CodeRabbit confirmed).
- The SIZE-002 refusals honestly met and repaired in-slice: the round-3 fix's first form (a Session argv kwarg) pushed the slice to 425>400 — the session-command verbosity channel (`\set VERBOSITY verbose` at open, the spine's Session untouched — the MORE bounded diff) + the compression back to exactly 400/400; the ARV-RED-002 pre-amendment refusal the registry's expected step; all preserved in record 43 §8.
- The local workspace: the tenth reset recovery complete (the scan REPORT confirmed everything safe on the remote; the rig rebuilt; the credential store rebuilt from the live PAT).

## 3. Task and scope

CLAIM-053 (P3-03b — PLAN's P3-03 card's anchor half, the bounded split per LAW-05): the typed anchor resolution (RTM §2.9 item 4 + SYS-05) at query.py's resolve-anchor arm — `resolved | unresolved | ambiguous`, a typed query, never a nearest-match guess; the named causes (no-current-generation / stale-generation / location-unmatched); the fallback matching evidence with the hit count (ambiguous at >= 2); the anchor binds its OWN Source version by construction (never crosses versions; new editions never silently retarget) — plus the Q8 anchor-stability spike (harness/spike_anchor.py) on the SYNTHETIC corpus per §7.3 (the freeze claims only synthetic-corpus fidelity; a real-PDF/EPUB stability claim requires a named, permitted, real corpus and measured results). The scope per `harness/runs/claim-053-p303b-anchor-resolution-q8-spike/scope.txt`.

## 4. Results

- **Commit A (the RED declaration)**: the ANC-01..09 contract suite (test_anchor.py — the typed states, the named causes, the fallback hit counting, the edition boundary, the re-extraction stability, the owner boundary, the one-JSON-line output contract) + the gate's TESTS registration + CLAIM-052's rule-4 close row + CLAIM-053's open row + the PLAN/STATE/AGENTS re-derivation + this record + WORKLOG Task 62 + the slice's scope + red-01.txt. RED observed at the predecessor 364f30e (machinery-absent ARV-TEST-000: query.py's resolve-anchor arm + spike_anchor.py absent — the S1/record-18 §4.1 + P3-01/02/03a precedent form). The red-record binding lands at commit A (the binding must verify in git; the ARV-RED-007 refusal of the pre-commit binding attempt recorded).

## 5. Files changed

`harness/tests/test_anchor.py` (NEW), `harness/gate.py` (the TESTS registration), `CLAIMS.md` (CLAIM-052's retirement + close row; CLAIM-053's open row), the run dir (scope, red-01), `STATE.md`/`AGENTS.md`/`PLAN.md`/`context/WORKLOG.md` (the five-area re-derivation), this record. Commit B to come: `harness/query.py` (the resolve-anchor arm), `harness/spike_anchor.py` (NEW).

## 6. Commands and external actions (ACTUAL — never reconstructed)

- The PR #87 close: the D-042 path reproduced live (self-approve 422 "Can not approve your own pull request"; merge 405 "At least 1 approving review is required"; the PUT flip via the full-replace branch-protection endpoint — the PATCH method's 404 honestly probed and diagnosed before the scripts/branch_protection.py proven form was followed; merge 200 at `364f30e`; the restore; the protections re-read: 1 review, dismiss_stale, strict, admins, all five contexts).
- The post-merge observation: the five-check run at `364f30e` GREEN (canonical-layer/head-tools/harness/harness-suites/harness-trusted — run ids 122062577006..31); the branch deleted (204); local main synced.
- The ANC suite RED observed at 364f30e: `python3 harness/tests/test_anchor.py` -> ARV-TEST-000 (red-01.txt).
- `make red` at the pre-commit tree refused ARV-RED-007 (the binding must verify in git — the suite file not yet committed) — the binding lands AT commit A, after the push.

## 7. Evidence

The proof set at `harness/runs/claim-053-p303b-anchor-resolution-q8-spike/`: red-01.txt (the machinery-absent RED at the predecessor), scope.txt, the runs + sev.json + proofsheet to come with commit B and the review chains.

## 8. Failures (each honestly recorded)

- The D-042 merge path's first attempt used the PATCH method on the branch-protection endpoint — a 404 (the endpoint is a full-replace PUT; the scripts/branch_protection.py proven form followed instead); the first merge script's logging crashed on a contexts-parsing bug AFTER the (failed) sequence — the state re-observed honestly before any retry; nothing merged on a blind retry.
- The make-red pre-commit binding attempt refused ARV-RED-007 — the registry's own order: the suite file must exist in git before the binding verifies; the binding lands at commit A.

## 9. Unverified items

To come with commit B + the review chains: the implementation's runs, the spike's measured stability numbers (synthetic-corpus fidelity only per §7.3), the notverified boundaries, the INT-104 pushed-head class, the D-042 merge reproduction for THIS slice.

## 10. Open decisions

None new. Q8 (the extraction-spike corpus): the registered synthetic default STANDS for this spike — the real-corpus stability claim requires the owner gate (never silently widened here). The open register is unchanged: D-014 + Q6–Q12, each blocking only its named dependents.

## 11. Next action

Commit A push + the red-record binding + PR #88 opened EARLY → commit B (query.py's resolve-anchor arm + spike_anchor.py) → the suite GREEN ×3 → make verify → the SEV rounds + the CodeRabbit rounds (the read-every-thread enumeration at the merge gate) → the finalize → the merge under D-042 → **P3-04..09 → the Phase 3 exit gate → P4-00 → P4-A..F → the Phase 4 exit gate** — NO PAUSE (INT-134/135/138/139/140). The next owner checkpoint: the Phase 3 exit gate's verified completion with the reports.

## 12. Session close

This record is OPEN at commit A; it completes at the slice's finalize per the convention. The PAT rotation reminder stays standing until the project completes.
