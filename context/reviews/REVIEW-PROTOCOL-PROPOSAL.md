# Review Protocol Proposal

> **Status:** ACCEPTED CORE FOLDED CANONICAL (2026-10-13, D-024) — the non-negotiables (review is read-only; findings never merge themselves; PR + explicit owner authorization; severity discipline; verification architecture) now live in `/AGENTS.md` binding rules, `/OPERATING-MODEL.md` §3, and `/EXECUTION.md` §5. This file remains as accepted process DETAIL (channel table, finding format, severity rules, PR contract), subordinate to those canonical homes — never a parallel authority. Supersession follows D-021/D-024: further changes to these rules happen in the canonical homes, not here.

## 1. Non-negotiable default: review is read-only

A review request authorizes inspection and reporting, not edits to the reviewed branch.

- Never commit, push, or write directly to `main`. All file changes are proposed on a branch and presented in a pull request. Do not merge a PR unless the owner explicitly authorizes that merge.
- For a review-only request, do not change repository files. Use inline comments on an existing PR when the finding concerns its diff; use an issue when the finding concerns the baseline architecture, policy, or backlog. Avoid opening duplicate issues for the same finding.
- Create a review-report Markdown file only when the owner asks for a durable report or the findings are too interconnected for useful inline comments. Add or update that report in a separate, reviewable docs-only PR. Never treat the report itself as permission to change the reviewed system.
- Honor explicit limits literally. If the owner says not to code or execute, do not run commands, tests, builds, migrations, scripts, or the application; do not make implementation changes. GitHub metadata reads and proposed review documentation are not product execution.
- A reviewer must not silently “fix” a finding while presenting the work as a review. Findings and remediation are separate steps and separate change scopes.

## 2. Choose the right review channel

| Situation | Channel | Permitted change |
|---|---|---|
| A proposed code/doc diff has a localized defect | Inline PR review comment | Comment only; no file edit |
| A baseline architecture, policy, or missing capability needs tracking | GitHub issue | Issue/comment only |
| A connected audit needs a durable, multi-finding record and the owner asked for one | Docs-only PR with a review `.md` | New/updated review artifact only |
| A review rule or canonical policy needs to change | Explicit policy-proposal PR | Proposed docs only; do not edit the canonical source silently |
| An implementation or correction is approved | Separate implementation/revert PR | One coherent, approved change with evidence |

Use one PR per coherent purpose. In particular, do not bundle a review report, policy rewrite, and product implementation into one large diff. A revert of an unauthorized change is its own PR unless the owner explicitly asks for a single corrective PR.

## 3. Review lifecycle

1. **Intake and authority.** Read `AGENTS.md` in its prescribed order, especially `INTENT-LEDGER.md`, then the relevant canonical sources and worklog tail. Capture the exact base commit SHA, owner request, relevant INT IDs, allowed scope, explicit exclusions, and any owner-gated questions.
2. **Freeze scope.** State what is and is not being reviewed. Do not expand a review into implementation, policy adoption, schema changes, or unrelated cleanup.
3. **Inspect without writing.** Collect specific file/line/commit evidence. Separate what the source explicitly says from interpretation, hypothesis, and unknowns. Do not make claims about commands or tests that were not actually run.
4. **Report actionable findings.** Lead with the consequence and location, not a tour of the repository. Explain how the defect can fail, why it conflicts with the product goal or an accepted rule, and what evidence would falsify the finding.
5. **Route decisions correctly.** An owner-intent conflict or irreversible/security/data-loss policy remains open for the owner. Silence or elapsed time is never consent. A question blocks only the work that depends on it; independent safe work can continue.
6. **Triage before remediation.** The owner can accept, reject, defer, or ask for proof on a finding. Do not convert a recommendation into a decision by editing the ledger or canonical docs. Record a rationale when a finding is rejected or deferred.
7. **Implement only when authorized.** Make one small, coherent change on a topic branch. Preserve unrelated changes. Add acceptance tests and deliberate known-bad cases when appropriate. Do not weaken the oracle to make a result green.
8. **Verify independently.** A fresh-context GLM-based subagent performs the test/falsification/retest loop when authorized. The verifier must not implement the code it is judging. A different model family may add adversarial coverage, but is not a hidden mandatory gate that contradicts the declared GLM workflow.
9. **Present a proof-carrying PR.** Include the intent/source links, scope, diff summary, tests or checks actually run, known-bad results when relevant, not-verified items, risks, and rollback/reversal path. The PR should let an owner review the evidence without trusting the author’s confidence.
10. **Owner review and closure.** Do not merge on the owner’s behalf without explicit authorization. After an approved change is merged by the authorized person, update only the appropriate canonical home, worklog, and session record. Keep the issue/report linked to the merged evidence.

## 4. Finding format

Every non-trivial finding should provide:

- **ID and severity** — stable within the report; use the severity definitions below.
- **Confidence** — confirmed, strongly supported, plausible, or unverified.
- **Location** — exact path, relevant line/section, and target commit.
- **Evidence** — quotation, API result, test output, or reproducible condition.
- **Failure mode** — concrete example of what can go wrong.
- **Goal/rule impact** — the user-visible, data-integrity, safety, or repository-governance consequence.
- **Recommendation** — smallest meaningful correction, not an unsolicited implementation.
- **Verification state** — inspected, statically checked, test-executed, independently verified, or not verified.
- **Owner decision needed** — yes/no; state the question and its dependency scope.

Distinguish observed facts, inferences, and recommendations. Cite web/source material when used. Do not include private chain-of-thought; include the evidence and concise rationale necessary to assess the conclusion.

## 5. Severity rules

| Severity | Meaning | Handling |
|---|---|---|
| **P0 — Critical trust/data/safety** | Data loss, privilege/security boundary failure, false-green trust gate, unauthorized irreversible action, or a contradiction that can cause unsafe execution | Block the affected change; provide concrete evidence and a falsifiable acceptance condition |
| **P1 — Core correctness/goal** | Violates a product invariant, makes a core workflow unreliable, or permits durable drift/semantic corruption | Fix before the dependent slice graduates; unrelated independent work may continue |
| **P2 — Reliability/operability** | Failure recovery, maintainability, diagnostics, docs, or test coverage gap with bounded impact | Track and resolve at the nearest appropriate slice/gate |
| **P3 — Polish/optional improvement** | Non-blocking readability, convenience, or design opportunity | Optional, explicitly prioritized |

Severity describes consequence, not rhetorical urgency. A review must not inflate severity to force acceptance. If the evidence does not support a claim, lower confidence or mark it unverified rather than presenting inference as fact.

## 6. Verification architecture

A review is only as strong as its oracle. Prefer layered, independently observable evidence:

1. Requirements and acceptance criteria fixed before implementation.
2. Static/invariant checks with stable reason codes.
3. Known-good fixtures and deliberate known-bad mutations to prove the guard detects violations.
4. Tests of real public workflows—not only internal helper functions.
5. Independent reads of persisted state and recovery behavior.
6. Fault, retry, duplicate, invalidation, and replay cases where relevant.
7. Fresh-context verification separated from implementation.
8. Protected CI/repository gates where configured, with configuration observed rather than assumed.
9. A clear not-verified section for any layer that was not exercised.

A green test suite proves only the behaviors covered by those tests. A passing prose review, a different model family, or a stated checklist does not substitute for a failing known-bad control, a running path, or observed persisted state. Never claim a gate is active until its actual configuration and behavior are checked.

## 7. Review report template

Use this skeleton for a substantial report:

```markdown
# [Target] — Review

> Status: REVIEW ONLY. Target SHA: [full SHA]. Scope: [scope]. Not in scope: [exclusions].

## Verdict
[Decision-useful conclusion in a few sentences.]

## Findings
### F-01 — P0/P1/P2/P3: [failure statement]
- Confidence:
- Evidence and location:
- Failure mode:
- Goal/rule impact:
- Recommendation:
- Verification:
- Owner decision:
- Acceptance condition:

## What is aligned / what is working
[Only useful evidence-backed positives.]

## Not verified
[Exact gaps; no implied execution.]

## Proposed sequence
[Smallest safe order, including dependencies and independent work.]
```

Do not force a report when inline comments or one issue are clearer. Do not turn every observation into a finding. Avoid filler, vague claims like “architecture needs work,” and unsupported statements such as “fully verified.”

## 8. PR contract

Every PR body must answer:

- **Purpose:** one sentence.
- **Owner intent:** relevant INT IDs and exact quotes where the repo requires them.
- **Scope / non-scope:** paths and behaviors included or excluded.
- **Change type:** review artifact, policy proposal, implementation slice, or revert.
- **Acceptance evidence:** exact checks and results actually observed.
- **Known-bad coverage:** which deliberately broken states were rejected, where applicable.
- **Not verified:** what was not run or could not be inspected.
- **Risk and reversibility:** migration/data/security effects and how to back out.
- **Authority:** owner approval needed, protected-path implications, and merge remains owner-controlled.

Keep PRs small enough for the owner to inspect. No quiet canonicalization, no force-push or destructive history rewrite to erase a mistake, no automatic merge, and no claim of success before GitHub reports the resulting state.

## 9. Repository-specific guardrails

- `INTENT-LEDGER.md` is owner intent, not an assistant’s analysis log. Never add an inference, recommendation, or observation about the owner as if it were their words.
- Preserve raw source material unchanged. Extracted/review documents remain lower-authority analysis, not decisions.
- Do not close Q1/Q2/Q3 or any owner-gated question by inference or silence. Respect the named gate and dependency scope.
- GLM-based fresh-context subagents own the test/verification/retest loop. Builders and verifiers have separate task roles; a verifier does not repair its own reviewed implementation.
- Product code and UI are outside a review unless expressly included in the task scope. UI remains outside this backend repository.
- A review should make the next decision or smallest next slice clearer. It should not become a permanent parallel doctrine. Adopted process belongs in the existing canonical home identified by `EXECUTION.md`.
