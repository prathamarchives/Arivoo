# 17 — CANDIDATE-TOOL GATE AND PHASE-1 GRADUATION

> STATUS: SESSION ENGINEERING RECORD (2026-10-15; INT-119, D-035; session 17 of the build). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 16. PRs this session: #24 (turn-14 intake + selftest extraction), #25 (the candidate-tool gate + fail-closed anchoring + head-tools required), #26 (graduation + close) — updated as each lands.

## 1. What the owner asked (verbatim — owner turn 14, chat 2026-10-15)

> **[CREDENTIAL REDACTED AT INGESTION — an owner-supplied access token, identical to the standing out-of-repo session credential (verified programmatically, value never printed); stored only outside the repo, never recorded in any file, log, or record (D-025, the INT-092/turn-8 precedent).]**
>
> I reviewed the current `main` branch and the merged work for Slices 10 and 11.
>
> The implementation work appears complete; Phase 1 graduation is not yet proven complete. The repository's own `STATE.md` identifies one remaining task: run the integrated fresh-context proof at the final main-branch SHA, assemble the seven-part graduation evidence, and then update the phase status. I'm keeping those two claims separate rather than treating successful slice-level checks as proof of the entire system.
>
> Current main is `8e5b1e93f6235228da5958ce44066ce0ad31c1f9`. Its post-merge verification run [38578692377](https://github.com/prathamarchives/Arivoo/actions/runs/38578692377) succeeded, and there are no open PRs in the repository snapshot I checked.
>
> ## Review findings
>
> P1
>
> Candidate tool changes are not necessarily merge-blocking.
>
> `.github/workflows/verify.yml`, lines 48–85
>
> The required `canonical-layer` job replaces the candidate's verifier and isolation checker with copies from `main`. That is appropriate for independently judging the candidate's repository content. But the candidate's own tools run in `head-tools`, which the workflow describes as informational. The repository's state also identifies `canonical-layer` as the required check.
>
> Consequently, a PR could weaken `tools/isolation_check.py` and its self-test together. The base-anchored job would still test the repository using the trusted copy; the candidate's weakened implementation would be exercised only in the non-required job. A red result there would not necessarily block the merge. The same structural concern applies to changes to the candidate verifier.
>
> Why it matters: the new gate protects the documents against a weakened checker, but does not reliably prevent a weakened checker from entering `main`. That is weaker than the stated objective that changes to the candidate's own tools are exercised and safely gated.
>
> P2
>
> The missing-anchor check is not fully fail-closed.
>
> `.github/workflows/verify.yml`, lines 48–60
>
> The anchor step conditionally copies the base isolation checker only if `base/tools/isolation_check.py` exists. The following check verifies that `tools/isolation_check.py` exists in the candidate working tree, not that the file actually came from `main`.
>
> If the base copy were absent, the workflow could continue using the candidate's own file while presenting the result as base-anchored. The file currently exists on `main`, so this is a latent fallback path, not evidence that the latest run used the wrong checker.
>
> Fix: explicitly fail if the base copy is absent, then copy it and verify that the anchored file is the one being executed. Never fall back silently to the candidate's version.
>
> ### What looks solid
>
> - Slice 10: The isolation checker now treats embedded remote credentials as failures, checks tracked files more broadly, distinguishes local and CI modes, and tests complete diagnostic paths with an 18-case matrix. Two recorded falsification rounds found defects that were subsequently repaired.
> - Diagnostic redaction: The self-test checks that synthetic canary values do not appear in standard output or standard error, including the harness's exception paths. That is materially stronger than testing regexes alone.
> - Honest boundary accounting: The session record explicitly says the host does not provide OS-level separation between orchestrator, builder and verifier subprocesses. It does not misrepresent process separation as mechanically enforced.
> - Slice 11B: The fresh-context task agent completed its bounded task, and a separate grader independently reran the checks and awarded 96/100 — PASS. The grader also recorded the limitations rather than claiming the proof covered everything.
> - Current CI: [The post-merge run on ](https://github.com/prathamarchives/Arivoo/actions/runs/38578692377)[`8e5b1e9`](https://github.com/prathamarchives/Arivoo/actions/runs/38578692377) passed both `canonical-layer` and `head-tools`. The recorded verification results are 51/0 for the canonical verifier, 30/30 for its self-test, and 18/18 for the isolation matrix.
>
> One qualification: a green run shows the current workflow passed; it does not resolve the P1 design issue above. Both jobs passing on the current commit is not proof that a future PR weakening the candidate tools would be blocked.
>
> ## Phase 1 graduation status
>
> The final SHA's post-merge CI run is now available. The remaining work is the integrated graduation proof and its evidence record, including a fresh observation of branch protection. The previous 96/100 result is for Slice 11B at an earlier SHA, not the final integrated graduation run.
>
> I would therefore not mark Phase 1 graduated yet. First resolve the candidate-tool gate issue and the missing-anchor fallback, run the required checks through the protected PR workflow, and then complete the integrated fresh-context proof at the resulting final `main` SHA.
>
> I made no repository changes during this review.

**Preservation note (honest):** the turn opened with an owner-supplied access token (redacted above per the standing credentials-hygiene rule — D-025/INT-092; verified programmatically identical to the out-of-repo session credential; the value never entered any file, log, or record of this repo). The remainder is the complete owner-forwarded review, verbatim as received, formatting included. Ledgered from it: INT-119 (the governing lines, E-4-class labeled); the plan is adopted through D-035 (ADOPTED, severable, challengeable) and executed through this session's slices — the review's own recommended ordering governs: gate repairs first, then the integrated graduation proof at the resulting final SHA.

## 2. Starting state

- `main` @ `8e5b1e9` (PR #23's merge), working tree clean; branch `slice/turn14-intake-extraction` cut from it. 0 open PRs (API, observed 2026-10-15).
- Preflight (STATE's standing close-gap pattern — record 16 §12 named this session's first act): `python3 tools/verify_canonical_layer.py` @ `8e5b1e9` → exit 0 → **51/0**; `--self-test` → **30/30**; `tools/isolation_check.py` → GREEN; `--self-test` → **18/18** (exit 0 each).
- Remote (API, read-only, 2026-10-15): PR #23's post-merge run **38578692377 observed SUCCESS on main @ `8e5b1e9`** (both jobs green — the reviewer's claim verified); branch protection observed live: required = **[`canonical-layer`] ONLY** (head-tools NOT required — the review's P1 confirmed against the live config), strict, admins included, force-push/deletion off.
- Review-claim spot-checks (all CONFIRMED): the anchor step's conditional copy (`if [ -f base/tools/isolation_check.py ]`) and the `test -f tools/isolation_check.py` existence-only check (the P2 latent fallback — the anchored file is never verified to BE the base's); head-tools described as informational in the workflow header; the workflow comment "informational job exercises the head tree's tools"; STATE/AGENTS name only `canonical-layer` as required.
- The credential at the turn's head: identical to the standing store (verified without printing either value); the store unchanged; nothing recorded (§1's redaction note).

## 3. Task and scope

- **The requested work** (owner turn 14 → INT-119/D-035, the review's own order): (1) resolve the candidate-tool gate issue — candidate tool changes must be merge-blocking, and the coordinated-weakening class (a PR weakening a tool AND its self-test together) must be caught mechanically in the REQUIRED job; (2) fix the missing-anchor fallback — fail if the base copy is absent, verify the anchored file is the one being executed, never silently fall back to the candidate's version; (3) run the required checks through the protected PR workflow (the graduation PR merges under the strengthened protection); (4) complete the integrated fresh-context graduation proof at the resulting final `main` SHA, with a fresh observation of branch protection, the seven-part evidence record, and only then the phase-status update.
- **Bounded scope:** the gate work = two mechanical extractions (the self-test suites become separately-invocable modules so the BASE's suite can judge the CANDIDATE's implementation — the same base-anchoring philosophy extended from documents to tools) + the workflow re-architecture (anchored files under distinct names + sha256 verification + fail-closed existence checks) + binding `head-tools` as a required check after a green run is observed (the W-01 stage-2 pattern). The graduation = one fresh-context task agent + one separate fresh-context grader at the final content SHA + the seven-row evidence record + the phase update.
- **Non-scope:** no product code; no Phase 2 harness; no change to the checks' semantics (the suites move, they do not change — counts stay 51/30/18); no raw/ edits; no new owner questions; Phase 1 is not marked graduated until the integrated proof passes at the final SHA (the review's explicit sequencing — slice-level green is never conflated with system-level proof).
- **Intent/decision references:** INT-119 (turn-14 forwarding), D-035 (the review's adoption — severable, challengeable), D-034 item 6 (the graduation gate), D-025/D-026 (walls + bounded diffs), P-13/P-15 (standing authorization), INT-117/OPERATING-MODEL §9 (verification on fresh-context subagents).
