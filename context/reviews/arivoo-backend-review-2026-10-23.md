# ARIVOO — Backend progress review, 23 October 2026 (What changed, what remains unproven, and the next sequence through Phase 3 and Phase 4)

> STATUS: REVIEW-ONLY ARTIFACT — 2026-10-23. Owner-forwarded (owner turn 27; preservation home: session
> record 26 §1; ledger refs INT-131/INT-132). Per D-022 this file is review evidence, never owner intent:
> the owner's own words for this turn live in INTENT-LEDGER.md (INT-132) and record 26 §1; this review's
> recommendations were adopted severably through D-043, each element challengeable. The review examined
> main at `68722c6d51422be9ef79d41840233fcb8428cbe6` (the PR #66 merge), post-merge Actions run
> `39835784795` (five jobs green), and the merged test code itself — its two live findings on test_11
> (the mixed index space; the comment-matchable credential assertion) are the CLAIM-032 slice's receiving
> work. No repository commands, tests, or application execution were performed by the review itself.

*The owner forwarded this review as `arivoo_backend_review_2026-10-23.pdf`; the text below is the
extraction of that PDF as received, preserved verbatim (the header banner above is the repo's D-022
wrapper, not review content).*

---

## REPOSITORY SNAPSHOT

Checked 23 October 2026. Default branch main is at 68722c6d5142, the merge commit for PR #66.

The post-merge Actions run completed successfully with all five jobs green. There are currently no
open pull requests in the repository.

Current state | Assessment
--- | ---
Latest merge | PR #66 / CLAIM-031: the trusted gate now runs on a separate runner from candidate-controlled suites. The merge is in main and post-merge CI is green.
Preceding repair work | PR #63 R-03 isolation-tool hardening; PR #64 R-04 gate/scope/known-bad/workflow repairs; PR #65 ledger one-line consistency; PR #66 R-06 trusted-path isolation.
Product status | Phase 3 durable-capture behavior has not yet been demonstrated as a real product workflow. Current progress is verification and trust infrastructure that prepares the repo to implement the product safely.
Critical uncertainty | GitHub branch-protection settings could not be independently read in this review. The plan says both harness-suites and harness-trusted must become required checks after green runs. Confirm this in repository settings; a green run alone does not make a check merge-blocking.

**Overall judgment:** the trust-path architecture has materially improved and is green on main. However,
review of the merged test code found two real gaps in the regression pin for that architecture. Fix those
pins and verify required-check enforcement before treating the new gate as durably protected. Then continue
the ordered H-01c / H-02 closures and start the P3 requirements freeze. Do not describe Arivo as having a
working capture product yet.

**How to use this document:** read the review findings first, then the ordered actions. The later sections
translate the roadmap into a systems-engineering lens: requirement, design, implementation, falsifiable
test, evidence, and release gate. This is a decision and navigation document, not a claim that every
requirement has been built.

## 1. Progress since the last review

The last four merged slices closed specific defects in the verification system. The work is real, but its
value is primarily that future product changes can be judged more reliably.

PR / slice | What changed | Plain-language significance
--- | --- | ---
#63 - R-03 | Hardened isolation tooling: non-blocking open for FIFO-swap defense, fail-closed unreadable subtree handling, directory budget accounting, and fixed-message assertions. | The test environment should not hang or silently ignore data when files behave unexpectedly.
#64 - R-04 | Repaired workflow/gate/scope cases: trusted gate is not skipped merely because candidate gate fails; bounded failure-tail output; byte-faithful unusual filenames; correct rename counting; synthetic known-bad rows and stronger regression pins. | The guard must fail for the right reason, preserve the object being checked, and make failures diagnosable.
#65 - ledger consistency | Added VER-213 multiplicity detection for one-line intent records and MUT-31 to test triplicated rows; removed hard-coded count assumptions; canonical verifier reported 52/0 and mutation floor 31/31 in the slice evidence. | The governance ledger can no longer quietly accept a repeated row just because other checks convert rows to a set. Reported totals are derived rather than stale labels.
#66 - R-06 | Split candidate suite execution and trusted judgement into separate GitHub-hosted runners. Added checkout credential hygiene and a workflow-shape regression test. Review escalated from file tampering to runner PATH tampering. | Refreshing files on the same computer is not enough if an untrusted test can also alter the process environment. The trusted judgement now has its own runner.

### Evidence at the current main revision

- Main merge SHA: 68722c6d51422be9ef79d41840233fcb8428cbe6 (PR #66 merge).
- Post-merge run 39835784795 completed with success; jobs: canonical-layer, head-tools, harness,
  harness-suites, harness-trusted - all green.
- The R-06 PR itself also had a green PR-triggered run 39834330304 with all five jobs green.
- The repo search found zero open PRs at review time.

### Progress versus product

More green checks and stronger gates mean a better-controlled engineering process. They do not mean the
owner can yet import a source, save a highlight with a stable anchor, write a note, restart, and recover
the same material from the real backend. That end-to-end behavior remains ahead.

Links: PR #63 | PR #64 | PR #65 | PR #66 | post-merge Actions run

## 2. Review of PR #66: what is now better

The defect was in the trust chain of the development gate, not in Arivo's user data model. A candidate
pull request can contain code that is itself hostile to the checker. The checker cannot let that code alter
the machinery that later decides whether the pull request is acceptable.

| | Before | After |
|---|---|---|
| Untrusted candidate tests | Run in the same runner/workspace as the later trusted gate. | Runner A: harness-suites checks out the candidate and base, anchors the trusted driver, then runs the candidate's required suites. This runner is considered exposed to candidate code. No trusted judgement is consumed after the suites on this runner. |
| Attack path | A candidate suite could replace files under the trusted base machinery after a hash check. A later review round also identified a runner-state attack: plant a fake python3 in a directory added to $GITHUB_PATH. Re-checking repository files alone does not reset that path state. | Runner B: harness-trusted checks out the relevant trees, anchors the trusted driver and runs S4c on a runner where the candidate test code does not execute. The gate's decision is no longer downstream of the candidate test process's workspace or PATH changes. |
| Failure | The gate could potentially report green over a candidate that should be refused. The repository records that a full predecessor forgery was reproduced: the trusted phase went green over a scope-breach candidate. | Credential hygiene: The PR sets persist-credentials: false on the five checkouts that are exposed to candidate code, and regression checks are intended to protect that invariant. |

**Systems-engineering reading:** this is a trust-boundary change. It removes an entire interaction between
untrusted execution and trusted judgement instead of trying to patch every possible side effect. That is
stronger than merely adding another hash check. The actual workflow separation is present in main and its
jobs have passed CI; the next issue is whether the regression test reliably detects future changes that
undo that separation.

Relevant source code: Current workflow: verify.yml | PR #66 review and discussion | R-06 verification limits

## 3. Review findings that still need action

I inspected the merged test implementation, not only the PR summary. The current workflow split looks
right structurally, but test_11 in harness/tests/test_trusted_gate.py has two ways to miss a regression.
These are gaps in the safety pin, not evidence that the current main workflow is already running the
trusted phase on the candidate runner.

### Finding A - the unnamed-step check uses mismatched indexes

The test calculates i_anchor and i_s4c from names_b, which contains only named steps. It then uses those
numbers to slice step_lines, which contains every step entry including unnamed - run: entries. Those are
different lists. Inserting an unnamed step between the anchor and S4c can leave the slice empty, so the
assertion can still pass. The variable entries_b is computed but not used.

**Required regression:** create a mutation fixture that inserts an unnamed `- run: ...` step between the
anchor and S4c. The old test must fail to detect it (RED evidence). The repaired test must fail on the
mutated workflow and pass on the proper workflow. Identify anchor, S4c and all step starts from one common
ordered list of parsed step blocks.

### Finding B - checkout credential assertion can match a comment

The test gathers each checkout block as raw text and checks whether the text contains
persist-credentials: false. The workflow itself has comments that mention that exact phrase. If the active
YAML input were removed while the explanatory comment stayed, a substring assertion could still pass.
That defeats the purpose of checking the actual checkout configuration.

**Required regression:** remove the active `with.persist-credentials: false` setting from a fixture but
leave the comment. The test must fail. Prefer parsing the checkout step mapping and assert that the active
value equals boolean false, or use a parser that demonstrably ignores comments and targets the real input
field.

### Severity and boundary

Treat these as a high-priority test-integrity follow-up before relying on the new jobs as required merge
gates. The split runners reduce the live attack surface now; the pin must prove that the workflow cannot
drift back. A green self-check that cannot detect its named counterexample is not evidence of the property
it claims to establish.

## 4. Exact next actions

Keep each action bounded. Do not combine the test repair, branch-protection change, historical-record
cleanup and first product schema migration into one large pull request.

Order | Action | Acceptance evidence | Why it matters
--- | --- | --- | ---
1 - now | Open a small follow-up PR for test_11. Repair the step-entry indexing and active checkout-input assertion. Add the two discriminating mutation fixtures. | Both mutations make the old implementation fail; repaired test catches each; clean workflow passes; CI green at the exact proposed head; test/proof records bind to that SHA. | Without a falsifiable pin, future workflow drift can look safe while the regression test stays green.
2 | Verify branch protection / rulesets in GitHub Settings. Preserve existing required checks; add harness-suites and harness-trusted as required contexts if they are not already present. | Record a screenshot or text export of the required-check list and the rule target. Confirm the exact check names match the jobs that ran green on main. | A check can be green but optional. Optional checks do not block a bad merge.
3 | Reconcile the current-state and evidence records: STATE.md, the session-25 close / R-06 notes, WORKLOG Task 39, PLAN R-06 wording and CLAIM-031 close row. | One consistent statement of which contexts are required, the settings evidence pointer, post-merge run 39835784795, exact SHA and any external residuals. | The repository currently has state text saying to merge #66 and then bind a context, while main already contains the merge. PLAN names both contexts; actual settings remain unverified here.
4 | Execute H-01c-authority as its own bounded slice. | RED-first regression(s), repaired authority/identity boundary, independent review, proof record and required CI; no unrelated Phase 3 schema changes. | Close the remaining trusted-authority defect family before building the SEV gate.
5 | Execute H-01c-evidence/privacy (F-007), then H-02 systems-engineering verification gate. | Evidence shows the exact privacy/evidence behavior fails at predecessor and passes at fixed revision; H-02's own judging path verified independently. | H-02 is a mechanism for judging product slices, not a substitute for proving the mechanism itself.
6 | Run P3-00: requirements traceability and product contract freeze. No product-domain migration before the plan is accepted through the repository process and P2-CLOSE / H-01 / H-02 entry conditions are green. | Accepted trace from SYS-01..SYS-11 to states, interfaces, schema decisions, failure cases, and acceptance tests. Explicit owner answers or safe non-decisions for Q11/Q12. | This is the point where the work stops being mostly about the build system and begins implementing durable product behavior.
7 | After P3-00: P3-M0 migration oracle and P3-K0 command kernel; then P3-01 through P3-09 in order, with independent review after each slice. | Each slice shows predecessor failure, fixed behavior, replay/crash/isolation tests, trace closure, known-bad results, and exact-SHA evidence. | Build the smallest real vertical slice first; expand only when the current slice's evidence justifies it.

**No bypass:** do not jump directly to P3-01, and do not let H-02 become a green label over its own
unverified validator. Conversely, do not let infrastructure closure become indefinite: the roadmap
deliberately makes the remaining hardening steps bounded and then starts P3-00.

## 5. Phase 3 translated into product behavior

Phase 3 is the durable-capture foundation. In everyday terms: when the owner imports material, highlights a
passage or writes a note, the system must know exactly what was saved, who saved it, what version it
belongs to, and how to recover it after retries or failures.

The eleven system requirements are grouped below by what the owner should be able to trust.

Product promise | Non-technical test question | Engineering evidence to require
--- | --- | ---
Do not lose my work | After the system says saved, can I restart and still find the same highlight or note? | Acknowledgement happens after commit at a named durability rung; crash/restart tests; idempotent replay; export/restore preserves revisions and purge state. SYS-01, 02, 04, 08, 10.
Keep the passage attached to the right source | If the PDF/book is re-imported or changes edition, does the highlight silently jump somewhere else? | Stable Highlight ID; Anchor names a specific Source version; extraction generation/provenance; mismatch becomes explicit unresolved state. SYS-05, 06, 07.
Keep work private and attributable | Can another owner read or alter my material by guessing an ID or using a retry? | Owner scope, actor, provenance, typed IDs, cross-owner negative tests, command-level authorization and retry tests. SYS-03, 04.
Search can be rebuilt | If indexing fails, have I lost the original note or highlight? Can search be rebuilt? | Authored records are authoritative; passages and keyword index are derived/versioned; tests corrupt and rebuild derived state without losing captures. SYS-06, 07.
Prove the real client can use it | Can a real client create and retrieve a capture through the backend, not just a mock? | Independent API/database read, clean external client contract, owner isolation, migration and recovery proof. SYS-09, 11.

### Phase 3 order in plain language

- P3-00: agree the rules before creating product tables. Define identities, source versions, revisions,
  provenance, durability states, command transactions, migration safety and failure states. Trace each
  requirement to a test.
- P3-M0 + P3-K0: build the migration safety check and the one command kernel. The kernel is the standard
  controlled door through which writes pass; avoid creating multiple independent doors that each enforce
  different rules.
- P3-01: one real, idempotent command on the real stack. Prove missing owner/actor/provenance refuse, same
  request replay returns the same result, changed body under the same key refuses, and crash boundaries
  behave honestly.
- P3-02 to P3-06: progressively add Work/Source intake, versioned extraction and Anchors, then Highlights,
  Bookmarks, Notes and immutable revisions.
- P3-07 to P3-09: keyword index that can be rebuilt; explicit local outbox/server sync states;
  export/restore with no silent loss or resurrected purged material.

**Decisions the agent must not silently make:** Q11: do not auto-merge logical Works/Sources or add
title/filename/semantic uniqueness constraints before the owner ratifies identity semantics. Q12: do not
select provider-specific blob schemas or promise cross-store atomicity before storage/staging/recovery is
ratified. Q8: the current extraction corpus default is synthetic; do not claim PDF/EPUB anchor stability
without measured evidence. These are scoped gates, not reasons to stop unrelated work.

## 6. Phase 4 and the V-model view

Phase 4 is the first usable reading-and-thinking workflow, proven through the actual client and real
backend contracts. This repository implements backend behavior; it does not build the separate reader UI.
A CLI or a mock can aid development, but neither proves the product-level workflow by itself.

### The intended journey

Step | What the owner experiences | What the backend must prove
--- | --- | ---
1. Import and open | Bring in readable material and open it without losing the original. | Supported-format capability matrix; malformed/encrypted/unsupported files fail explicitly; extraction readiness is truthful; source/version identity stays stable.
2. Read and return | Leave and reopen the same material and return to a saved position. | Position contract, source-version compatibility, stable IDs and clear unresolved-anchor behavior; no promise of stability beyond the measured corpus.
3. Capture and think | Highlight a passage, bookmark it, revise a note, and write longer free-form thinking. | Real write API, immutable revisions, idempotent retries, owner scope, durable acknowledgement and explicit failure state.
4. Connect material | Reference a book, passage, highlight or note with stable @ references; write a journal thought with or without a source. | Identity vs revision rules; resolution for current/historical/tombstoned/unavailable/ambiguous/purged targets; no leakage across owners.
5. Recover and use an agent | After offline use, uncertain acknowledgement or restart, recover the same material. An authorised agent can read relevant context. | Client/server state distinctions, replay/outbox recovery, export/restore, purge invalidation, scoped read-only agent access through the same API.

### How to think about the V-model

Define before building (left) | Build and verify after (right)
--- | ---
User need: a highlight never disappears. Acceptance test: commit a highlight, restart the process, recover the same stable identity and content. | System requirement: commit before claiming saved; record idempotency and owner provenance. System test: same request replay has one effect; same key with changed body refuses; crash before/after commit yields defined results.
Architecture: Highlight identity separate from source version and derived index. | Integration test: re-extraction or new edition cannot silently move the anchor; indexing failure does not erase authored content.
Interface: the API returns explicit durability and failure states. | Client contract test: actual client distinguishes saved, queued, synced, conflicted and failed; a started request is not called saved.

### The completion test

Phase 4 is not complete because a database has CRUD endpoints or a prototype looks polished. It is
complete when the full import -> read -> position -> highlight/bookmark -> note revision -> journal ->
stable @ reference -> leave/reopen/recover workflow passes through a real client and the real backend,
including offline, uncertain-ack, isolation, recovery and export/restore cases, with independent review
and owner-fidelity review.

## 7. A systems-engineer's field guide for reviewing progress

When reading a PR, run, proof sheet or status file, ask five questions. They turn complicated
implementation details into a practical judgement about what can be trusted.

Question | What a strong answer looks like | Warning sign
--- | --- | ---
1. What exact requirement is being closed? | A named SYS/LAW/claim identifier and the intended behavior are explicit. | A vague phrase such as 'improve reliability' with no acceptance boundary.
2. Can the old version be shown failing? | A RED test reproduces the actual defect at the predecessor. A test fixture itself is verified to represent the intended counterexample. | Only adding an assertion that passes before the fix, or recording a scratch result without explaining what it proves.
3. Does the fixed version pass for the right reason? | A discriminating regression fails when the protection is removed or weakened, and passes with the repair. | String matching, stale expected counts, unreachable branches, comments matching the expected text, or tests that don't exercise the target behavior.
4. Is it enforced in the real workflow? | Remote required checks run against the exact revision; branch protection makes the critical checks merge-blocking; negative cases and merge behavior are verified. | A green local run, optional Actions job, mock-only test or a claim about settings without evidence.
5. Can another reviewer reconstruct the claim? | Commit SHA, exact command, run record, source and limitations are linked. Canonical state agrees with the live repository. | STATE says 'next: merge' after merge, or prose claims a required context was bound without settings evidence.

### Open limitations to keep visible

- Branch-protection/ruleset configuration: not independently verified in this review. Check it directly and
  record evidence for both harness-suites and harness-trusted.
- PR #66's R-06 record itself lists platform-level runner isolation as an external trust boundary. Do not
  describe GitHub-hosted runner isolation as independently audited by this repository.
- The workflow pin is weak in two specific ways (the mixed index space and comment-aware substring check).
  Fix and prove these before treating future drift as caught.
- The current-state snapshot STATE.md still carries pre-merge wording for #66; reconcile it and the session
  record after the required-context setting is actually verified.
- Q11/Q12/Q8 remain scoped product decisions. Keep work moving that doesn't depend on them; never silently
  substitute an agent choice for owner intent.

### Reference register

- Main at merge SHA 68722c6
- Post-merge CI run 39835784795 (five successful jobs)
- PR #66 - R-06 trusted-path isolation and review threads
- PLAN.md - canonical sequence and Phase 3/4 requirements
- STATE.md - current-state snapshot (stale items identified in this review)
- test_trusted_gate.py - test_11 R-06 workflow pin
- verify.yml - current two-runner workflow
- R-06 notverified.txt - stated proof limitations
