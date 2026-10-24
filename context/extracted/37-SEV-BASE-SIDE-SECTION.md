# 37 — The SEV-3 follow-up: the base-side section expectation (CLAIM-044)

> STATUS: SESSION ENGINEERING RECORD (2026-10-24; intent refs INT-134/135/138/139; decision refs D-037/D-038/D-039/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 53. PRs this session: PR #79 (this slice; outcome recorded only after it happens). THE SEV record for this slice: `harness/runs/claim-044-sev-base-side-section/sev.json` (sheet_section TRUE — the rule this slice enforces, applied to its own record).

## 1. What the owner asked (verbatim — the standing chain)

> "start working towards phase 3 and phase 4 do not stop as a world class systems and software engineer" (turn 34 — preserved at record 35 §1; INT-139)

No new owner turn; the standing do-not-stop chain executes the #78 fresh-context review's adopted
recommendation: the SEV-3 follow-up (the #77 reviewer's finding, named in PLAN/TEMPLATES, adopted
at the #78 review — "its own bounded slice immediately after #78 merges, RED-first") — then
P3-M0 ∥ P3-K0.

## 2. Starting state

Main `c19d497` (the PR #78 merge, 2026-10-24T14:19:18Z; post-merge run `40101968643` five green,
observed); the branch deleted; protection verified byte-identical; `make verify` GREEN at the
fresh main (54/0 — VER-806 among the checks). P3-00 LANDED: the product-schema-migration gate
lifted for RTM-citing slices; Phase 3 EXECUTING.

## 3. Task and scope

CLAIM-044 — the base-side sheet_section expectation (ARV-SEV-009): `harness/sev.py` (the rule +
the `_base_renders_sections` helper), `harness/tests/test_sev.py` (the renderer-base fixture +
the expectation group), `harness/tests/test_gate_dispatch.py` + `harness/tests/test_trusted_gate.py`
(the born-valid fixture modernizations), `harness/known-bad/cases.py` (KB-SEV-009 + the born-valid
modernization), `harness/red-records.json` (the typed amendments), `PLAN.md` + `context/TEMPLATES.md`
(the NAMED → ENFORCED flips), `harness/gate.py` + `RTM.md` + `LAWS.md` (the live-doc code-list
drift repairs from the review), `STATE.md`/`AGENTS.md`/`CLAIMS.md`/`context/WORKLOG.md`, this
record, the slice's runs dir.

## 4. Results

**THE RULE (ARV-SEV-009, RED-first):** a slice whose PR's own BASE carries the Proof-Sheet SEV
section renderer MUST set `sheet_section: true` in its committed report — the candidate-controlled
opt-in window closed when the first section-bearing sheet merged (PR #78). The probe is the
switch's own name (`sheet_section`) in the base's proofsheet.py source — the exact signal the
renderer's opt-in reads. Three-state fail-closed: the renderer present → ACTIVE (the opted-out
and absent forms refuse — absence is not opt-in); a POSITIVE absence (the base's proofsheet
without the marker, or no proofsheet at all — the pre-renderer era) → inactive, the historical
slices compatible; an UNDECIDABLE state → the refusal itself, never a silent pass.

**RED→GREEN:** red-01.txt (observed at the predecessor c19d497): the sev suite exit 1 (the two
expectation cases failing with got []; the precision-labeled compliant form passing as designed;
the historical fixture proving no over-refusal) + the KB matrix exit 1 (KB-SEV-009 broken — KB-05,
building stops). GREEN at the fix head: the sev suite 46 PASS lines; the KB matrix 32/32;
`make verify` 54/0.

**THE FIXTURE MODERNIZATIONS (each caught by the machinery itself):** three born-valid reports
over renderer bases gained `sheet_section: true` — the KB probe's (riding with the new case),
the dispatch positive fixture (its own born-valid assert fired 009), and the trusted suite's
build_stub (16 failures, every one the stub's own gate refusing its own report — the rule
working, the fixture stale). The fresh-context reviewer independently confirmed NO missed
fixture (`rg` over every sev.json construction site; the deliberately-broken variants correctly
untouched).

**THE FRESH-CONTEXT REVIEW: PASS — no P0/P1, four P2s** (`fresh-ctx-glm-sev-claim044-20261024`):
SEV-1 (the suite's own RED-path message still saying 001..008) — FIXED in-slice with its
amendment; SEV-2 (gate.py's check-order docstring) — FIXED with the scope widening; SEV-3
(RTM §1's SYS-11 test-path line + LAWS LAW-30's LIVE note) — BOTH FIXED with the scope widening
(live canonical statements, never left stale per P-18); SEV-4 (the probe's three stated
boundaries: the comment-only marker false-positive — unreachable in this repo's history, the
marker's only arrival `ec250a1` in the same commit as the renderer code; the directory-shape
edge — unreachable for wall-controlled main; the undecidable short-circuit — the sibling
ARV-SEV-003 refuses the same condition, fail-closed holds) — RECORDED as the stated residual
in the sev.json. The reviewer's own probes: the RED reproduced verbatim in a worktree at the
RED commit; the historical base-relative behavior verified (claim-041/042's records against
their own bases: no 009; against the current renderer base: 009 — the intended honest form,
and nothing in CI re-validates historical records); its own absent-proofsheet fixture → codes=[];
the undecidable ref → both codes named, no traceback; the git-show error class verified on
git 2.47.3; the amendment chain verified from the c19d497 baseline digests.

**THE REGISTRY CATCH (the second consecutive slice):** the stale CLAIM-043 open row overlapped
CLAIM-044's on PLAN.md/AGENTS.md — ARV-CLM-002 at the dispatch fixture; repaired per rule 4.
The twice-learned lesson is now the chain's standing checklist: **every slice's commit A retires
the previous slice's open row and carries its rule-4 close row in the SAME commit.**

## 5. Files changed

harness/sev.py, harness/tests/test_sev.py, harness/tests/test_gate_dispatch.py,
harness/tests/test_trusted_gate.py, harness/known-bad/cases.py, harness/red-records.json,
harness/gate.py (the docstring), PLAN.md, context/TEMPLATES.md, RTM.md, LAWS.md, STATE.md,
AGENTS.md, CLAIMS.md, context/WORKLOG.md, this record, the slice's runs dir.

## 6. Commands and external actions (ACTUAL — never reconstructed)

- `python3 harness/tests/test_sev.py` → exit 1 at 3ec1897 (the two expectation cases) → exit 0
  at the fix heads (46 PASS lines)
- `python3 harness/gate.py --known-bad-only` → exit 1 at 3ec1897 (KB-SEV-009 broken) → exit 0
  (32 PASS lines)
- `python3 harness/tests/test_gate_dispatch.py` → the born-valid assert catch at 5e8ab7d →
  exit 0 after the modernization; `python3 harness/tests/test_trusted_gate.py` → 16 failures
  at 5e8ab7d (the stub's own gate refusing) → exit 0 after
- `make verify` → exit 0 at the final content head (54/0)
- The proof set captures + the RECORDED PR-mode gate green (the exits in the sheet)
- `make red` × 3 (the suite edit + the two modernizations' amendments)

## 7. Evidence

red-01.txt; the proof records + the section-bearing sheet (PASS ARV-PRF-004); the sev.json
(the reviewer's four P2s with dispositions; the stated probe residual; sheet_section TRUE);
the typed amendments; the CLAIM-043 rule-4 close row.

## 8. Failures (honest)

- **THE REGISTRY CATCH (second consecutive slice):** the stale CLAIM-043 row — the twice-learned
  lesson promoted to the standing checklist (commit A retires the previous row + carries the
  close row, same commit).
- **THE FIXTURE CATCHES (three, all the machinery working):** the dispatch born-valid assert;
  the trusted stub's 16 refusals; each modernization with its scope widened in BOTH homes at
  edit time (the SEV-1 declaration-drift class guarded against).
- **THE RTM/LAWS SCOPE ANCHOR MISS:** the first attempt at the RTM line replacement used a
  paraphrased anchor and asserted-failed — re-anchored on the exact line; never a wrong edit.

## 9. Unverified items

- The trusted-leg enforcement of ARV-SEV-009 begins with the NEXT slice's PR (the base c19d497
  predates the rule — the recorded bootstrap pattern, the same transition as the original SEV
  wiring and the section renderer; this slice's own PR is judged by the base's validator).
- The probe's three stated boundaries (the comment-only marker false-positive; the
  directory-shape edge; the undecidable short-circuit's sibling-code path) — the reviewer's
  residual, recorded in the sev.json; each unreachable in this repo's wall-controlled history
  or fail-closed through a sibling named code.
- The remote CI's five-check run at this PR's head — observed at the PR.
- The identity limit (LAW-30): the fresh-context reviewer, same host/user — declared
  independence of context, never cryptographic.
- The N12 residual unchanged.

## 10. Open decisions

None new; none closed. D-014 + Q6–Q12 at unchanged scopes.

## 11. Next action

Merge the CLAIM-044 PR (#79) once review-complete (D-042), then **P3-M0 (the migration oracle)
∥ P3-K0 (the kernel primitives) → P3-01 (the kernel + first real command — the §1.6 capture
checkpoint) → P3-02..09 → the Phase 3 exit gate** — NO PAUSE (INT-134/135/138/139).

## 12. Session close

This record is written at the slice's finalize commits (the SEV-6 discipline); the proof set,
the section-bearing sheet, and the RECORDED gate green are the merge evidence; the PR's
five-check CI is the walls' verification of the head. The standing chain continues into
P3-M0/P3-K0 the moment #79 merges.
