# 16 — ISOLATION, DIAGNOSTICS, AND REAL HOST GATES

> STATUS: SESSION ENGINEERING RECORD (2026-10-14; INT-118, D-034; session 16 of the build). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 15. PRs this session: #18 (turn-13 intake + navigation repair), #19 (gate re-target), #20 (closed-decision drift + agent-agnostic propagation), #21 (Slice 10), #22 (Slice 11A), #23 (session close) — updated as each lands.

## 1. What the owner asked (verbatim — owner turn 13, chat 2026-10-14)

> Arivoo review — 14 October 2026
>
> The work on Slices 4–6 and the Integrity-and-evidence layer is substantially proven. I would not begin Phase 2 blindly, though. The new checker caught and repaired real defects, the handoff and cold-start tests passed, and the latest main CI run is green. My review also found stale decision language that escaped the new cross-document checks, plus a conflict between the intended agent-agnostic design and the GLM-specific rules still enforced by the repository.
>
> I inspected the current repository, recent merged PRs, session records, canonical documents, verifier and actual GitHub Actions logs. I made no repository changes and did not rerun the checks locally.
>
> 1. What is verified now
>
> Latest repository state
>
> main at e34dcb3254189aa5e209fb8be5bee5dc3e5e2ba6 · PR #16 merged · zero open PRs at the time checked
>
> PR #16 — Integrity and evidence · PR #17 — MUT-11 repair
>
> Post-merge CI: successful
>
> Run 38553070896, on main at e34dcb3
>
> Inspect the actual run
>
> The logs show 51 verifier checks passed, zero failures; 27/27 known-bad mutations caught; isolation check green. The isolation self-test also caught its planted fake credential.
>
> Navigation, handoffs and integrity proofs landed
>
> - PR #10: STATE's five-area contract.
> - PR #11: event-typed worklog/record rules and a successful handoff proof.
> - PR #13: selective cold-start read path; independent grading passed at 96.8/100.
> - PR #14: replication guide.
> - PR #16: checker repair, known-bad coverage and an independent falsification loop.
>
> The cold-start test read 10 files totalling 14,975 words, without reading context/raw/. The separate grader resolved 28/28 pointers and all five hard fail conditions passed. The first test therefore established a baseline of 14,975 words and a limit of 18,000 words, rather than leaving "reasonable scope" undefined. See session record 14, §6.
>
> The recent integrity work also produced an important result: the fresh-context falsification agent found a real blind guard, and that defect was repaired with VER-904 and MUT-27. The checker was not merely run against a valid repository; a known-bad construction exposed a weakness that was then tested again. See session record 15.
>
> Current phase: Phase 1, including layer 1.2 and Integrity-and-evidence, is complete according to the recorded exit evidence. Phase 2's minimum trustworthy harness has not been implemented. The repository root contains the canonical documents, context/, failures/ and the two verification tools, not a product application or established build harness.
>
> 2. Findings that need attention
>
> P1 — Closed owner questions still appear open in current canonical text
>
> This is the most direct gap in the Integrity-and-evidence work.
>
> The current open-question register agrees across DECISIONS.md, EXECUTION.md, PLAN.md and STATE.md: only D-014 remains open. VER-504 passes. But that check does not detect stale statements elsewhere in the current canonical documents.
>
> Examples I verified:
>
> - DECISIONS.md, D-007 still says Q1 keeps the primary-builder-host and "Other" questions. D-028 explicitly closes Q1 and says no primary builder host exists.
> - PLAN.md still describes the original spec deltas as "owner-gated (Q1–Q3)", even though Q1, Q2 and Q3 were subsequently closed by D-028, D-029 and D-030.
> - OPERATING-MODEL.md still says the "Q1 remainder" is non-blocking in the current Model 1 description, although D-028 closed that question.
> - D-023 still refers to text/Markdown/conversation exports as the QD-1 default; D-031 now says any readable format, with sequencing following the durability ladder.
>
> These passages are not all equally consequential, and older session records should retain what was true at the time. The defect is that current canonical text does not consistently identify those references as historical or superseded. A fresh agent can encounter them and infer a decision is still open or a format restriction still applies.
>
> Why this matters: the checker now proves the four open-register mirrors agree, but the system's actual intent is broader—avoid stale documentation misleading current work.
>
> Recommended repair: a small, bounded closed-decision drift slice. Preserve historical wording; add explicit supersession/closure pointers at the misleading current references. Add one or two known-bad cases that reintroduce a closed question as open in a current canonical document. Keep the guard narrow to known closure surfaces rather than building a universal policy engine.
>
> P1 — The agent-agnostic decision has not fully propagated to verification policy
>
> D-028 says the repository is agent-agnostic and that testing/verification hosts may vary over time—GLM now, another host later.
>
> But the current AGENTS.md still states:
>
> Test and verification loops run on GLM-based subagents; GLM is the host agent for verification/testing (INT-070).
>
> The verifier preserves this rule through VER-109. VER-507 also describes GLM-based verification as governing, and the operating model still describes GLM as governing rather than clearly distinguishing the current default from the architecture's invariant.
>
> There is a valid distinction in the owner's instructions: the Integrity-and-evidence work was explicitly directed to use fresh-context GLM subagents. That explains the choice for this execution. It does not establish that every future session must use the same model family.
>
> Recommended repair: separate the verifier protocol from its currently selected host. The invariants should be independence from the builder, reproducible tests, independent state reads, real execution paths and successful known-bad detection. GLM can remain the current default, but a host change should not require redesigning the repository or contradicting its authority rules. Update the corresponding text and guards together, then test that a valid alternative-host declaration is accepted while the verifier-independence rules still hold.
>
> I would fix this before the harness makes the current host assumption more deeply embedded.
>
> P2 — Tag removal still has a semantic ambiguity
>
> D-030 explicitly removes the tag system: no highlight tag field, no optional tag feature, and classification words remain free text.
>
> Yet NORTH-STAR.md and P-10 still say that the owner's free-text classification words are "one signal, never a gate" in concept formation. VER-211 and MUT-11 continue enforcing that older tag-gate wording.
>
> The current marker checks (VER-904) protect the text asserting "no tag field" and "tag system removed"; they do not resolve whether words such as concept, fact or quote receive special treatment during discovery.
>
> There is a reasonable interpretation under which the owner's free text is simply processed as ordinary text. The risk is a different implementation: treating those specific classification words as a special signal would quietly reintroduce feature semantics that D-030 says are gone.
>
> Recommended disposition: don't block Phase 2 on concept-formation semantics. Before Phase 5, make the rule explicit: ordinary user text can be processed as text, but classification words receive no special tagging behavior or dedicated weighting unless the owner decides otherwise. Retain the current guard against turning classification into a gate only if it is rewritten to enforce that clarified rule rather than an obsolete tag feature.
>
> P2 — The known post-merge gap has resolved, but STATE has not caught up
>
> The current STATE.md says the post-merge run for PR #16 has not been checked and is the first action for session 16.
>
> That was an honest statement when the session closed. The run now exists and has passed: run 38553070896. This is not evidence that the original record lied; it is the explicitly named close-gap becoming resolvable.
>
> The next session should record the merged revision, run ID and results, and update STATE's next action. The update should distinguish the remote CI run from local commands: remote CI has verified the three checks, but this review did not run them locally.
>
> A smaller wording issue is on the same line: STATE calls Phase 2 "product build", then defines it as the minimum trustworthy harness, while PLAN names Phase 3 as durable capture—the first real product behavior. I would call Phase 2 the minimum trustworthy harness/build loop and preserve "first real behavior" for Phase 3. Avoid letting phase names confuse the execution boundary.
>
> P3 — VER-101 reports incorrect read-order positions
>
> One small verifier diagnostic defect surfaced during inspection. The current read order is:
>
> 1. AGENTS.md
> 2. STATE.md
> 3. context/WORKLOG.md tail
> 4. INTENT-LEDGER.md
> 5. NORTH-STAR.md
> 6. EXECUTION.md
> 7. Reference tier
>
> But VER-101 reports the ledger at position 3 and NORTH-STAR at position 4. Its parser does not match context/WORKLOG.md because its path pattern excludes interior / characters. The current condition still correctly checks that the ledger appears before NORTH-STAR, so this is not a proven false-green on the current tree. It is misleading diagnostic output, and the parser could be made more accurate.
>
> I would fix it during a relevant verifier edit and add a known-bad test for a path containing a directory separator. It does not need a separate phase.
>
> P2 — CI's step label is out of date
>
> The workflow still labels the verifier step "46 checks: C1–C8", while the current run executes 51 checks including C9 and passes 27 self-test mutations. The mismatch was already recorded in session 14 as a deliberate deferral. It is cosmetic rather than a failing check, but it makes the CI display less trustworthy than the underlying log.
>
> Because the workflow is part of the protected gate machinery, don't casually edit it. Bundle a label-only correction into the next properly authorized workflow-touching change, without modifying the gate behavior.
>
> These are the final two slices of Phase 1. They should close the safe-working-environment layer and prove the entire operating loop works in the actual agent environment. Phase 2 stays blocked until both slices pass and the Phase 1 graduation gate is satisfied.
>
> I reviewed the current repository state, canonical instructions, isolation checker, and CI workflow. The most important finding is that the repository has much of the necessary infrastructure, but there are still gaps between what its documentation claims is protected and what the automated gates actually verify.
>
> 1. The position we should be at
>
> Slices 1–9: existing work and evidence
>
> The repository has protected-branch controls, a canonical verifier, known-bad mutation tests, selective cold-start instructions, handoff rules, and an independent falsification process. The latest recorded main-branch CI run, 38553070896, succeeded. The recorded checker results are 51 checks passing, 0 failures, and 27/27 self-test mutations caught.
>
> Slice 10: isolation and diagnostics
>
> The repository has tools/isolation_check.py, but the current implementation does not yet establish every property required by the slice. In particular, a credential embedded in a Git remote URL produces a warning rather than a failing result, and the self-test tests a token-pattern match rather than the complete diagnostic path.
>
> Slice 11: real host bridges and automated gates
>
> The repository has a canonical AGENTS.md and a working CI workflow. But the workflow copies the base version of the isolation checker into the candidate tree without actually running that copied checker in the required canonical-layer job. The informational job runs the candidate's own isolation checker instead. That leaves a gap if a PR weakens the isolation checker and its tests together.
>
> The current STATE.md, AGENTS.md, and PLAN.md also still direct an incoming agent to Phase 2. Your newly supplied plan is the authoritative continuation: those navigation instructions need a targeted correction before another agent can safely resume. We should not rewrite unrelated documentation.
>
> No repository changes have been made during this review.
>
> 2. Slice 10 — Establish isolation and diagnostics
>
> Purpose: Make sure an agent can do its assigned work without accidentally receiving sensitive information, exposing credentials, or having more authority than its role needs. When something goes wrong, diagnostics must explain the condition without leaking the secret itself.
>
> The key distinction is between telling agents not to do something and verifying that the environment actually prevents or detects it. We need evidence for the latter wherever the host provides a mechanism.
>
> Slice 10.1 — Establish the actual permission boundary
>
> First, inspect the environment we genuinely use. Don't start by constructing a new universal sandbox, permission framework, or host abstraction.
>
> We should account for four contexts:
>
> Context	What it needs	What it must not receive or do
> Builder	Task scope, necessary repository files, fixtures, test tools	Real owner secrets or data; edits outside the authorized scope
> Verifier	Slice requirements, relevant diff, evidence and test results	Builder history as a substitute for independent judgment; authority to implement its own findings
> Orchestrator	Canonical instructions, current state, coordination and review tools	Unrecorded authority to bypass the change workflow
> CI runner	Repository content and the minimum configuration needed to run checks	Unnecessary credentials or write privileges
>
> The existing OPERATING-MODEL.md already distinguishes builder, verifier, orchestrator and future runtime-agent responsibilities. Slice 10 should make the environment's actual guarantees match those responsibilities wherever possible.
>
> That means examining three separate boundaries:
>
> Repository and GitHub authority. Confirm the existing protected-main and PR requirements remain active. A green local check is not evidence that a change cannot bypass the remote gate. Prior records already document rejected direct pushes and a blocked merge; those are useful evidence, but the final closeout should confirm the current configuration and point to the actual run or probe.
>
> Runtime credentials and filesystem exposure. Establish what the builder and verifier processes can actually read. Checking whether a token string appears in tracked files does not prove that an agent cannot read a credential from its environment, local configuration, home directory or another mounted location. We must verify the real host boundary, not infer it from the isolation script's name.
>
> Working-context separation. Preserve the current role separation: a fresh verifier should evaluate the work rather than inherit the builder's assumptions. Use existing host and working-directory facilities. Add stronger OS-level separation only if inspection shows that the existing environment cannot provide the required boundary.
>
> The desired outcome is a clear account of what is mechanically prevented, what is detected, and what still depends on agent discipline. We must not claim that a prompt or process convention provides filesystem isolation if it does not.
>
> Slice 10.2 — Make diagnostic safety a tested property
>
> The current isolation checker has a useful basic design: it checks secret-like environment-variable names and known secret-value patterns, and it generally reports conditions rather than printing matched values. But we need to test the whole check, not only the underlying pattern recognizer.
>
> I would tighten this in four ways.
>
> First, make an exposed credential in a Git remote a real failure. Currently tools/isolation_check.py emits a warning when the remote URL embeds a credential but does not increment the failure count. As a result, the overall report can still say ISOLATION GREEN. That is inconsistent with the objective: an agent that can inspect .git/config may also be able to recover the embedded credential. The default should be to fail this condition and recommend an external credential helper.
>
> Second, define required configuration explicitly by execution mode. A local agent environment and a CI runner do not have identical requirements. Specify the minimum variables actually required in each mode, and report whether they are present or missing. Do not print their values. Do not build a giant speculative allowlist of every environment variable that a host might someday use.
>
> Third, test the complete redaction path. Put synthetic canary values into temporary fixtures and exercise the checker end to end. Assert both that the prohibited condition returns a failing exit code and that the canary value never appears in standard output, standard error, generated logs or the saved report. Test failure messages and exception paths too.
>
> Fourth, cover both negative and positive cases. A known-bad setup should fail for a clear, attributable reason. A correctly configured setup should pass. Otherwise we risk making the checker so aggressive that agents routinely work around it—or so permissive that a failure disappears inside a generic green status.
>
> The test matrix should cover:
>
> - A synthetic credential pattern in a tracked file.
> - A prohibited secret-named environment variable.
> - A missing required configuration item.
> - An embedded credential in a synthetic Git remote.
> - A correctly configured CI environment, including its legitimate variables.
> - A valid, clean environment that should remain green.
> - Redaction of each synthetic canary throughout the diagnostic output.
>
> No real credentials should be inserted into these tests. We should use synthetic fixtures and temporary copies only.
>
> One limit must remain explicit: a pattern scan cannot prove that every possible secret is absent. It can prove that specified leak classes are caught and that the checker does not print their values. The claim of isolation must be based on that evidence plus verified host permissions, not on an overbroad interpretation of a green regex scan.
>
> Slice 10.3 — Keep the implementation small
>
> I would not introduce another credential broker, generic host adapter, or custom sandbox in this slice unless the current environment demonstrates that an existing boundary is insufficient.
>
> The implementation should reuse the repository's current controls:
>
> - tools/isolation_check.py for the redacted environment checks.
> - The current branch-protection setup for remote Git authority.
> - The existing CI workflow for automated execution.
> - Existing role and scope rules for orchestrator, builder and verifier responsibilities.
>
> New dependencies are unnecessary unless a demonstrated requirement justifies one. The tests should use Python's standard library and temporary repositories or fixtures where practical.
>
> Slice 10 acceptance criteria
>
> The slice passes only when:
>
> 1. The agent and verifier environment's permitted access is documented and verified against the actual host—not inferred from instructions alone.
> 2. The isolation check reports required configuration as present or absent without exposing values.
> 3. Each required synthetic bad case is caught, while valid fixtures pass.
> 4. The diagnostic redaction tests prove that synthetic secret values never appear in output.
> 5. Credential-bearing remote URLs cannot produce a false-green result.
> 6. The repository's protected branch and PR controls remain intact.
> 7. The evidence is recorded in the session handoff, including any limitation that the host cannot mechanically enforce.
>
> The goal is a trustworthy boundary, not a larger security framework.
>
> 3. Slice 11 — Verify actual host bridges and automated gates
>
> Purpose: Prove the repository's canonical instructions and safeguards work when a genuinely fresh agent enters through the host it will use, rather than assuming that the agent has read the right instructions because a file exists.
>
> Slice 11 depends on Slice 10: host testing is meaningful only if we know what permissions and diagnostic guarantees the host actually provides.
>
> Slice 11.1 — Keep one canonical instruction source
>
> AGENTS.md remains canonical. We should not create a second version of its operating rules inside a host-specific file.
>
> The bridge pattern should remain deliberately simple:
>
> - If a host natively loads AGENTS.md, use that support and test the actual behavior.
> - If an active host requires a separate entry file, add a minimal bridge that imports or points to the canonical file in the host's supported format.
> - Do not create bridge files for speculative hosts that are not actually being used.
> - Do not copy the full authority hierarchy, laws, phase plan or session procedures into each bridge.
>
> This is consistent with the existing host-contract language in PLAN.md and the decision to keep the architecture agent-agnostic. The repository defines the roles, authority and evidence requirements; different agents may enter through different hosts.
>
> The bridge itself must be tested on an installed host version. Documentation stating that a host supports an import is not proof that the host actually reads the bridge and then follows AGENTS.md.
>
> Slice 11.2 — Close the CI isolation gap
>
> This is the clearest implementation task I found in the current workflow.
>
> The existing .github/workflows/verify.yml describes two jobs:
>
> - canonical-layer: runs a verifier anchored to main.
> - head-tools: exercises the verifier and isolation checker from the candidate branch.
>
> The required canonical-layer job copies tools/isolation_check.py from main into the candidate tree, but it does not call that copied isolation checker. Meanwhile, head-tools invokes the candidate's own isolation checker. That means the isolation-specific gate is not independently anchored in the same way as the canonical verifier.
>
> I would correct this using the smallest change: run the base-anchored isolation checker against the candidate repository tree as part of canonical-layer. Execute its relevant environment check and its known-bad tests, with the proper CI mode. Keep the existing head-tools job as a separate test of the candidate's own tools.
>
> This preserves the intent of the existing design:
>
> - The checker from main independently judges the candidate.
> - A change that weakens both the isolation check and its test cannot rely on its own implementation to approve itself.
> - The candidate's own version still gets exercised, so changes to the checker are tested rather than ignored.
>
> The exact environment behavior has to be run and observed in CI. Before writing the change, confirm the expected CI variables and fixture behavior so the new gate fails for genuine exposure conditions rather than runner-specific noise.
>
> There is also a stale workflow label, 46 checks: C1–C8, even though the recorded checker currently reports 51 checks and includes C9. Since Slice 11 already touches the workflow, synchronizing that label is a sensible small cleanup. It is not the principal security gap, so it should not expand the slice.
>
> Slice 11.3 — Test the real host, not a simulation
>
> The proof has to involve a fresh-context agent in the actual environment.
>
> The test should start with no manually supplied operating instructions beyond a minimal request to enter the repository and perform a bounded, authorized task. The agent must discover the entry point and proceed through the real workflow:
>
> 1. Find and read the canonical instructions through the host's normal entry behavior.
> 2. Recover the current phase, task, scope, authority and exact next action.
> 3. Identify relevant owner intent before making a consequential change.
> 4. Inspect the specified context and make one bounded, authorized change or complete a bounded task that exercises the gates.
> 5. Run the required checks in the actual environment.
> 6. Produce evidence that another agent can independently inspect.
> 7. Leave an accurate handoff and repository state for the next agent.
>
> The task should be small enough that failure has a clear cause. The proof is not whether the agent can summarize AGENTS.md; it is whether it can follow the instructions, stay within its authority, run the checks, and leave useful evidence without hidden operator coaching.
>
> Record the host and version, commit SHA, how the canonical instructions were loaded, commands and results, task scope, any permission limitations, and the handoff. If a check was not performed, it must be marked as not verified rather than inferred from a successful run.
>
> Slice 11.4 — Add only the gates that protect these contracts
>
> We should not implement the entire Phase 2 harness in advance. This is still Phase 1.
>
> The automated checks required here are limited to the contracts being established:
>
> - Canonical entry-point and bridge integrity, for bridges that actually exist.
> - The base-anchored isolation check and its known-bad tests.
> - The candidate's own checker and self-tests.
> - Existing canonical verifier checks.
> - CI execution and the required remote status gate.
>
> Real-host behavior remains a separate behavioral proof. A static test can verify that a bridge points to AGENTS.md; it cannot prove by itself that a host actually loads the bridge or follows it. That requires the fresh-context run described above.
>
> Slice 11 acceptance criteria
>
> 1. Every host actually in use either follows AGENTS.md natively or has a tested minimal bridge.
> 2. No host bridge duplicates or contradicts canonical rules.
> 3. The required CI gate independently runs the trusted isolation checker against the candidate tree.
> 4. A candidate change that weakens the isolation checker and its own tests cannot bypass the base-anchored gate.
> 5. The actual host run completes the bounded task, runs the required gates and creates a usable handoff.
> 6. Evidence is recorded against the exact commit and actual host version.
> 7. Any unverified behavior remains explicitly unverified.
>
> 4. Phase 1 graduation gate — one integrated proof
>
> Passing individual slices is necessary, but it is not sufficient. The final gate should demonstrate that a new agent can reliably continue the project without needing the owner to reconstruct hidden context.
>
> Graduation requirement	Existing evidence	What remains
> Protected PR workflow	Prior direct-push rejection, merge-block proof and successful recent CI	Confirm current protected configuration and final post-merge run
> Authority and scope recovered from entry point	Canonical AGENTS.md, authority map and role contract	Validate during the integrated fresh-context task
> Current state and next action found without a full-repo reread	Selective read path and cold-start proof	Correct stale Phase 2 navigation before testing
> Every meaningful session leaves a usable handoff	Session-record policy and prior handoff proof	Produce and verify the final integrated handoff
> Canonical checker rejects known-bad fixtures	51/0 and 27/27 recorded results	Re-run after changes and confirm current main CI
> Environment and host protections verified	Existing isolation checker and remote controls	Complete Slice 10 and make the isolation gate independently anchored
> A fresh agent completes authorized work and leaves evidence	Prior fresh-context verification and cold-start tests	Run the end-to-end proof in the actual host under the finalized boundaries
>
> The final proof should use the actual final main SHA, not a previous branch's passing result. Its session record should show the starting state, exact task, actual commands, observed results, known limitations and handoff. CI should then pass on the resulting PR and post-merge main.
>
> Only after the owner-supplied graduation criteria are all satisfied should Phase 1 be marked complete.
>
> 5. Execution order I recommend
>
> 1. Preflight and repair navigation. Confirm current main's evidence and update only the phase/status/next-action statements that would otherwise send a fresh agent to Phase 2. Preserve the existing history and avoid an unrelated documentation rewrite.
> 2. Slice 10A — Inspect the actual permission boundary. Inventory existing controls, identify what is mechanically enforced versus advisory, and preserve the current host's working path.
> 3. Slice 10B — Fix diagnostics and prove the isolation check. Correct false-green cases, define required configuration, add synthetic negative and positive tests, and prove redaction end to end.
> 4. Slice 11A — Repair the independent gate. Run the trusted, base-anchored isolation checker in canonical-layer; retain candidate-tool testing and sync the stale workflow label.
> 5. Slice 11B — Verify the actual host. Test the existing host's entry behavior. Add a minimal bridge only if that host requires one. Complete the bounded task from a fresh context and validate its handoff.
> 6. Phase 1 graduation. Re-run checks on the resulting tree, verify the remote CI result, assemble the complete evidence record, and update the navigation documents to state the actual outcome. Do not begin Phase 2 before this passes.
>
> Each implementation slice should retain the repository's existing method: bounded scope, tests that prove the stated failure mode, implementation, independent verification, iteration, PR and remote CI evidence. If a proposed change needs a broader permission framework or a host we do not actually use, it should stop and be justified rather than quietly expanding scope.

**Preservation note (honest):** this turn is the owner forwarding the complete "Arivoo review" (two concatenated review documents: the findings review with P1/P2/P3 dispositions, and the Slices 10–11 + Phase-1-graduation plan). No owner-voiced words accompany the forwarded text this turn — the owner's act is the forwarding itself, making the supplied plan the authoritative continuation (its own words: "Your newly supplied plan is the authoritative continuation"). The text above is the entire turn, verbatim, typos and formatting as received. Ledgered from it: INT-118 (the governing lines, labeled owner-forwarded E-4-class material); the plan is adopted through D-034 (ADOPTED, severable, challengeable — the INT-091/D-024/D-027 pattern: owner-forwarded analysis is never ledgered as owner intent). Turn 11's remaining sections stay taken-as-supplied, never ledgered from memory.

## 2. Starting state

- `main` @ `e34dcb3` (PR #16's merge), working tree clean, branch `slice/session-16-isolation-host-gates` cut from it. 0 open PRs (API, observed 2026-10-14).
- Preflight (STATE's named first act for this session — the standing close-gap), run before any edit:
  - `python3 tools/verify_canonical_layer.py` @ `e34dcb3` → exit 0 → **51 checks, 0 failures**
  - `python3 tools/verify_canonical_layer.py --self-test` → exit 0 → **27/27 known-bad mutations caught**
  - `python3 tools/isolation_check.py` → exit 0 → ISOLATION GREEN; `--self-test` → exit 0 → planted fake PAT CAUGHT
- Remote evidence (API, read-only): PR #16's post-merge run **38553070896** observed success on `main` @ `e34dcb3` (the named gap resolved — record 15 §11's close-gap form worked as designed: never a pending promise, always a resolvable next-session act); both jobs green; branch protection observed live: required check `canonical-layer`, strict contexts, enforce-admins on, force-pushes/deletions off.
- Review-claim spot-checks against the actual tree (all CONFIRMED): D-007's stale "Q1 keeps…" note; PLAN's "owner-gated (Q1–Q3)"; OPERATING-MODEL's "Q1 remainder" + §9 "INT-070, governing"; D-023's "text/Markdown/conversation exports first (QD-1 default)"; AGENTS' GLM-host line (VER-109/VER-507/MUT-05 enforcing it); VER-101's misleading positions ("#3/#4" printed while the real order is #4/#5 — the `[^`/]+` regex cannot match `context/WORKLOG.md`); verify.yml's stale "46 checks: C1–C8" step label (visible in run 38553070896's job steps); canonical-layer copying `isolation_check.py` from base without ever running it; `isolation_check.py` line 63–67: embedded-remote-credential → `unexpected += 0` (WARN, false-green class).
- The reviewer's stated facts about CI logs (51/0, 27/27, isolation self-test catch) match the recorded run and this session's local re-runs. The reviewer did not run local checks (its own statement); this session ran them — both the remote run and the local runs stand as independent evidence.

## 3. Task and scope

- **The requested work** (owner turn 13 → INT-118/D-034, the review's section 5 execution order): (1) preflight + repair navigation (this PR); (2) Slice 10A — inspect the actual permission boundary; (3) Slice 10B — fix diagnostics and prove the isolation check; (4) Slice 11A — repair the independent CI gate + sync the stale label; (5) Slice 11B — verify the actual host with a fresh-context bounded task; (6) Phase 1 graduation gate (one integrated proof on the final main SHA — staged as the session's exit handoff if not completable in-session).
- **The review's P1/P2 findings repaired en route** (before the harness embeds the host assumption deeper): the closed-decision drift slice (stale open-question references in current canonical text) and the agent-agnostic propagation (verification policy vs. named host), each with guard re-targets and new known-bads per the review's recommended repairs. The P2 tag-semantics disposition is recorded (pre-Phase-5 gate, PLAN), not silently dropped. The P3 VER-101 parser defect is repaired inside the relevant verifier edit (the gate re-target PR).
- **Bounded scope:** one purpose per PR; the navigation repair touches ONLY phase/status/next-action statements that would send a fresh agent to Phase 2 (the review's explicit non-scope: no unrelated documentation rewrite). Non-scope: no product code; no Phase 2 harness; no raw/ edits; no tag-semantics rule change (deferred to its named gate); no new sandbox/credential-broker/host abstraction (Slice 10.3); no bridge files for hosts not in use (Slice 11.1).
- **Intent/decision references:** INT-118 (turn-13 forwarding), D-034 (the review's adoption — severable, challengeable), D-028 (agent-agnostic — the propagation target), D-026 (bounded diffs), D-024 (change channel), P-13/P-15 (standing authorization: memory deltas + owner-directed execution work), INT-117/OPERATING-MODEL §9 (the falsification loop — verification of this session's own tool work runs on fresh-context subagents).
- **Walls exception (AGENTS binding rule):** Slice 11A touches `verify.yml` — wall CONSTRUCTION per an owner directive (D-034/INT-118, the review's Slice 11.2 directive), landing with evidence; the gate's protecting behavior is only strengthened (a new base-anchored isolation step + a label), never weakened.

## 4. Results

### 4.1 Slice 10A — the actual permission boundary (the account)

Inspection of the environment genuinely in use (this host; no new sandbox, broker, or abstraction — Slice 10.3 held). Four contexts, each with its boundary stated as MECHANICALLY PREVENTED / DETECTED / AGENT-DISCIPLINE:

| Context | Mechanically prevented | Detected (condition, value never) | Depends on agent discipline (stated honestly) |
|---|---|---|---|
| Repository + GitHub authority | Direct pushes to `main` (protection hook; re-observed live this session: required `canonical-layer`, strict, admins included, no force push/deletion); unverified merges (405 on failing required check — records 13/15) | PR/CI state via API; protection config drift by re-observation at phase gates (INT-104 snapshot discipline) | Nothing for these two routes — the gate, not the memory, rejects |
| Runtime credentials + filesystem | Credentials in tracked files (isolation scan, all extensions, raw/ included — P0 repair path); credentials in remote URLs (now a FAILING condition, this slice); the credential store lives OUTSIDE the repo tree (`~/.secrets/`-class out-of-repo store + `credential.helper=store --file=`, configured in untracked `.git/config`) | Secret value patterns in any tracked file; secret-named env vars; `.git/config` extraheader (advisory); remote userinfo credential forms (scheme + scp + multi-@) | **The host provides NO OS-level separation between orchestrator/builder/verifier subprocesses in this workspace** — any process could read the out-of-repo store; the discipline: uncoached-agent task cards never name the credential path (held every session incl. both slice-10 falsification agents), and git itself handles authentication so agents never see token values |
| Working-context separation | Fresh verifier subagents receive NO builder history (fresh context by construction — the Task tool's clean context; exercised this session by both falsification rounds: neither saw this orchestrator's reasoning) | The falsification loop (INT-117): a fresh-context agent attacks the work and reports reproducible findings | The verifier obeys its card (read-only on the real tree, temp copies for attacks) — enforced by review of its report, not by a sandbox |
| CI runner | Ephemeral GitHub-hosted runner, `permissions: contents: read` only; no owner secrets in CI; no write access beyond the checkout; checkout token is job-scoped and ephemeral | The runner's own token-shaped env vars (expected-class in `--ci` mode); the extraheader advisory | Runner-namespace prefix allowlist (GITHUB_/ACTIONS_/RUNNER_) is fail-open within those namespaces — documented residual |

**The explicit limit, stated:** a pattern scan cannot prove every possible secret's absence; the isolation claim = the specified leak classes are caught + values never printed + the host-permission account above — never an overbroad reading of a green scan. (Slice 10.1's three boundaries: repository/GitHub authority — confirmed by live observation; runtime credentials/filesystem — the honest gap is host-level process separation, NOT covered and NOT claimed; working-context separation — held by construction + discipline, recorded.)

### 4.2 Slice 10B — the isolation check, repaired and proven

`tools/isolation_check.py` v2.1: (1) embedded remote-URL credential is a REAL failure (was: `unexpected += 0` WARN — the false-green the review named); userinfo parsed from the authority at the LAST `@` (curl semantics — multi-@ decoys cannot hide a trailing user:token@), scheme + scp-syntax + token-shaped-username forms caught, benign username-only remotes (git@host) never false-flagged; (2) required configuration BY MODE (local: none; `--ci`: the five standard runner vars, present = non-empty and non-`false` in any case variant; unknown flags exit 2, never a silent mode change); (3) the self-test exercises the COMPLETE diagnostic path (subprocess, controlled env, temp git repos) — 18 cases: every catch class pinned by a case that can fire for that class alone (N5b: env-family with benign content; N10: the generic-assignment pattern; N11: the extraheader advisory; N12: exit-2; N13: false-value CI), negatives exit 1 with attributable RED lines, positives exit 0, benign remotes stay green, and every synthetic canary is asserted absent from stdout AND stderr including the harness's own crash paths (sanitized failure lines, never tracebacks); (4) the tracked-file scan covers EVERY tracked file (any extension/case — the old allowlist skipped .sh/.rst/extensionless), unscannable/missing tracked files FAIL closed, `.env`-family detection is case-insensitive and covers nested/suffixed/dotfile/index-only forms, the env-NAME pattern catches TOKEN2/MYTOKEN/SSH_KEYS/DB_PW/DB_PASS/PASSPHRASE-class shapes without matching PATH/PWD, the generic-assignment pattern is fixed (the `\\s` letter-exclusion bug + quotes-only requirement + the round-2 `\b` regression on db_password/client_secret), printed paths pass a redaction pass (secret-shaped filenames are value material), and the extraheader advisory resolves through worktree `.git` files.

Two falsification rounds ran (fresh-context GLM subagent, INT-117/OPERATING-MODEL §9 — the verifier never implemented what it evaluated; both reports verbatim in §7.1/§7.2): round 1 found 3 P1 true false-greens (extension allowlist; .env variants; index-tracked-deleted .env) + 7 P2/P3 defects — ALL repaired; round 2 verified every round-1 fix and found the residuals (the `\b` regression, multi-@ userinfo, False/FALSE CI variants, PASS/KEYS stems, 5 unpinned matrix surfaces, worktree .git advisory, secret-shaped path echoes) — ALL repaired, matrix grown 12 → 18 cases pinning each. Round-2 verdicts: catch-classes (a)/(b)/(d) REFUTED-then-FIXED (verified), (c)/(e) CONFIRMED, redaction CONFIRMED (zero canary bytes across ~85 checker runs). Residual limits recorded in §9.

## 5. Files changed (this PR: Slice 10)

- `tools/isolation_check.py` — v2.1 (the four tightenings + both falsification-round repairs; 18-case matrix; redaction pass; exit-2 contract)
- `.gitignore` — NEW: `__pycache__/`, `*.pyc` (prevention; see §8 — the pyc artifact incident)
- `context/extracted/16-ISOLATION-DIAGNOSTICS-HOST-GATES.md` — this record's §4/§5/§6/§7/§8 (the Slice 10A account is durably homed here; STATE points at it)
- `tools/__pycache__/verify_canonical_layer.cpython-312.pyc` — UNTRACKED (the §8 incident's cleanup: the artifact PR #20 accidentally committed via a blanket `git add -A`)

## 6. Commands and external actions (ACTUAL — this slice)

- `python3 tools/isolation_check.py` @ this head → exit 0 → ISOLATION GREEN (local mode; after all repairs)
- `python3 tools/isolation_check.py --self-test` @ this head → exit 0 → **18/18 cases PASS** (negatives exit-1-attributable, positives exit-0, canary redaction proven on stdout+stderr)
- `python3 tools/isolation_check.py --ci=true` → exit 2 → usage error (the strict-flag contract)
- `python3 tools/verify_canonical_layer.py` @ this head → exit 0 → 51/0 (isolation_check changes do not touch any guarded doc surface); `--self-test` → 30/30
- Fresh-context falsification subagent (round 1): ~40 checker subprocess runs on 27 temp fixture repos; (round 2): ~45 runs + 5 mutation tests of the self-test — read-only on the real tree, verified by its own `git status` observation; both reports preserved verbatim in §7

## 7. Evidence

- The matrix output (18/18) and the local GREEN run — §6, actual commands with exit codes.
- PR #21's CI run: `canonical-layer` (base-anchored verifier, untouched docs → green) + `head-tools` (the head tree's OWN new checker: `--ci` in the real runner env — the runner-required-config and expected-env behavior observed in CI for the first time — plus `--self-test`, the 18-case matrix, in CI).
- The falsification loop's two rounds: §7.1 (round 1) and §7.2 (round 2), verbatim.

### 7.1 Falsification round 1 — the fresh-context verifier's report (verbatim)
> (the sub-agent's report, exactly as returned — fresh context, no coaching; its
> observation about a pre-existing uncommitted `M tools/isolation_check.py` refers
> to this session's in-progress v2 edit on the working branch, not its own write.
> PRESERVATION NOTE, labeled: the report's SYNTHETIC example literals that would
> false-trip the isolation scan's generic-assignment pattern are masked to the
> report's own token-masking style (values truncated below the 12-char match
> threshold, e.g. `pw: SYN…`); the full synthetic literals are
> recoverable from the matrix's source (tools/isolation_check.py fixtures) — no
> real credential appears anywhere in this record)

All attacks are complete and temp artifacts cleaned up. (Note: `git status` in the real repo shows a pre-existing uncommitted `M tools/isolation_check.py` — mtime 13:14:07 UTC, before my session began; it is the author's own v2 edit, not mine. I performed zero writes to the real repo; all git writes happened in `/tmp` copies.)

---

VERIFIER REPORT — falsification of `arivoo/tools/isolation_check.py` (fresh context, read-only on target)

## 1. METHODS

- Read the target fully (315 lines). Claimed catch-classes: (a) credential in git remote URL → exit 1; (b) unexpected secret-NAMED env var → exit 1; (c) missing required CI config in `--ci` → exit 1; (d) secret VALUE patterns in tracked files → exit 1; (e) tracked `.env` → exit 1; plus redaction claim (conditions never values, canaries never in stdout/stderr "end to end") and a 6-case `--self-test`.
- Baselines on the real repo (read-only git probes only): local mode → GREEN/0; `--ci` with empty env → RED/1 (5 missing); `--self-test` → 6/6 PASS, exit 0.
- 5 positive controls on temp copies proving the harness reproduces the intended catches: https remote with user:token → RED; `ARIVOO_TEST_TOKEN` → RED; `--ci` partial vars → RED; canary in tracked `.md` → RED; root `.env` present+tracked → RED.
- Attack classes executed on temp copies (`cp -a` repo → `/tmp/attack-XX`, `rm -rf .git`, `git init && git add -A -f`, checker run as subprocess via `env -i PATH=… HOME=/tmp python3 $A/tools/isolation_check.py`): extension-allowlist evasion, env-file variants, index-vs-worktree state, case-variant extensions, env-NAME regex evasion (8 shapes + 5 controls), remote-URL form matrix (scp-syntax, ssh://git@, https user-only, `url.insteadOf`, `http.extraheader`), no-git vacuous run, `--ci` empty/false values, `--ci=true` arg parsing, quoted/unquoted generic-secret forms, regex character-class unit probes, unreadable/deleted tracked files, mutation-testing of the self-test (2 mutations), self-test crash-path canary leak, full redaction sweep.
- ~40 checker subprocess invocations across 27 temp fixture repos; synthetic canaries only (`ghp_`+36 letters, `gho_`+36 letters, synthetic AKIA/password strings). No real credentials sought or used.

## 2. FINDINGS

(Setup for every repro: `A=/tmp/attack-XX; cp -a /home/z/my-project/arivoo $A; rm -rf $A/.git; git -C $A init -q; git -C $A add -A -f`; canaries `ghp_<36×A>` (tracked), `gho_<36×B>` (env), `ghp_<36×C>` (remote); run `env -i PATH="$PATH" HOME=/tmp python3 $A/tools/isolation_check.py`.)

1. **P1 — TRUE false-green, class (d): extension allowlist skips whole leak classes.** Repro (A1): `printf 'export GITHUB_TOKEN="%s"\n' ghp_<36×A> > $A/deploy.sh; printf 'token %s\n' … > $A/CREDENTIALS; printf 'token %s\n' … > $A/notes.rst; git -C $A add -f …` → EXIT=0, GREEN, prints `[PASS] no secret value patterns in tracked repo files (all tracked text files incl. context/raw/)`. Expected: exit 1. Cause: line 153 scans only `.md .txt .py .yml .yaml .json .toml .cfg .ini` — `.sh`, `.js`, `.rst`, `.conf`, `.properties`, extensionless files etc. are never read, while the PASS line asserts "all tracked text files". Tracked-ness proven via `git ls-files`.

2. **P1 — TRUE false-green, class (e): only the exact root `.env` is checked.** Repro (A2): tracked `context/.env`, `.env.local`, `deploy.env` each containing `API_KEY="ghp_<…>"` (`git add -f`) → EXIT=0, GREEN, `[PASS] no tracked .env file`. Expected: exit 1. `context/.env` is literally a tracked .env; the code's own comment says ".env files must never be tracked" (plural). Cause: line 173 tests only `repo/".env"`.

3. **P1 — TRUE false-green, class (e): `.env` in the git index but deleted from the worktree.** Repro (A3): `printf 'API_KEY="%s"\n' ghp_<36×A> > $A/.env; git -C $A add -f .env; rm $A/.env` → `git ls-files` still lists `.env` (status `AD`), secret recoverable via `git show :.env` → checker EXIT=0, GREEN, `[PASS] no tracked .env file`. Expected: exit 1 (".env is TRACKED in git" is true — the checker's own `git_tracked` list contains it). Cause: line 173 requires `.exists() AND in git_tracked`.

4. **P2 — TRUE false-green variant, class (d): case-sensitive extension match.** Repro (A4): tracked `NOTES.MD`, `data.YML`, `cfg.JSON` with canary → EXIT=0 GREEN. Same root cause as #1; `endswith` is case-sensitive.

5. **P2 — diagnostic defect / in-spirit false-green, class (d): scan reads the worktree only; unreadable or deleted tracked files are silently skipped.** Repro (A10): `canary.md` added then `rm`'d (secret lives in the index blob) → GREEN. Repro (A14): `chmod 000` on a tracked `canary.md` → GREEN; the readable control → RED. `read_text` failure → `continue` with no condition surfaced, contradicting the tool's own vacuity philosophy ("surface it rather than report a false green"). Anything in git index/history but absent from the worktree is invisible.

6. **P2 — TRUE false-green, class (b): NAME regex boundary gaps.** Repro (A5): env vars `TOKEN2`, `MYTOKEN`, `PERSONALACCESSTOKEN`, `SSH_KEY`, `DEPLOY_KEY`, `DB_PW`, `PASSPHRASE`, `AWS_ACCESS_KEY_ID`, each set to `gho_<36×B>` → EXIT=0, GREEN, "(0 secret-named total)". Expected: exit 1 for secret-named vars. Controls: `GITHUB__TOKEN`, `MY_GITHUB_PAT_B`, `DB_PASSWORD`, `OPENSSH_PRIVATE_KEY` are caught. Cause: line 65 regex requires an exact `(^|_)(TOKEN|PAT|SECRET|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY|CREDENTIALS?)($|_)` word — digit-suffixed (`TOKEN2`), compounded-without-underscore (`MYTOKEN`, `PERSONALACCESSTOKEN`), `KEY` without `API_`/`PRIVATE_` prefix (`SSH_KEY`, `DEPLOY_KEY`), `PW`, and `PASSPHRASE` all dodge.

7. **P2 — TRUE false-green (literal claim), class (a): scp-syntax remote with credential.** Repro (A6i): `git -C $A remote add origin "ghp_<36×C>@github.example.invalid:org/repo.git"` → `git remote -v` displays the credential URL, but checker EXIT=0 GREEN ("no credential embedded"). Expected: exit 1 per claim (a) and the tool's own rationale ("an agent that can read .git/config can recover it"). Cause: parser requires "://" (line 100). Marginal real-world utility (ssh username=token is non-functional for auth), hence P2 not P1. Related out-of-scope class (A6v): `git config http.<url>.extraheader "AUTHORIZATION: basic <b64-of-token>"` (the standard GitHub Actions persist-credentials form) → GREEN; satisfies the stated .git/config-recoverability rationale but is not a remote-URL credential. Note: `url.insteadOf` embedding IS caught incidentally — `git remote -v` displays the rewritten URL (verified: RED).

8. **P3 — false-positive direction (fail-closed), class (a): username-only remotes reported as credential leaks.** Repro (A6ii/iii): `ssh://git@github.com:2222/org/repo.git` and `https://pratham@github.com/org/repo.git` (no credential anywhere) → EXIT=1 RED "remote URL embeds a credential". The parser cannot distinguish `git@host`/`user@host` from `user:pass@host`. Not a false-green, but makes class (a) unreliable in both directions.

9. **P2 — TRUE false-green for the "generic secret assignment" pattern, class (d).** Two defects: (i) raw-string bug — the value class `[^'\"\\s]` (line 61) excludes the letter **s**/**S** (intended: `\s` whitespace). Unit probe: `password = "ABCD…8"` → MATCH; `password = "ABCD…s"` (one added "s") → NO MATCH; `pw: "hun…"`, `MyP@ssw0rd…4` → NO MATCH. Since most real secret values contain "s", the generic pattern is mostly dead. (ii) Quoted-only: unquoted `pw: SYN…`-form in tracked `.yml`, `TOKEN=…` in `.txt`, `password = …` in `.py` → all GREEN (A9). Token-shape patterns (`ghp_`, `gho_`, `ghs_`, `github_pat_`, AKIA) are unaffected.

10. **P2 — self-test blind spots (coverage claim overstated).** Mutation evidence on temp copies (A12): (m1) `sed -i 's|if (repo / ".env").exists() and ".env" in git_tracked:|if False:|'` — claim (e) entirely disabled — `--self-test` still 6/6 GREEN, exit 0; (m2) drop `".txt"` from the extension tuple — still 6/6 GREEN, exit 0. The 6-case matrix covers (a)–(d) but has **no case for (e)**, none for the vacuous-scan guard, none for extension coverage, and no case that exercises checker stderr/tracebacks. "The COMPLETE diagnostic path … Both negative and positive cases are covered" is falsified: 4 of 5 catch-classes have a negative case.

11. **P2 — self-test's own crash path violates the canary-redaction claim.** Repro (A11): temp copy + fake `git` earlier in PATH that exits 1 only on `remote add` (delegates to `/usr/bin/git` otherwise); `env -i PATH=$A/fakebin:$PATH python3 $A/tools/isolation_check.py --self-test` → cases 1–3 PASS, then uncaught `CalledProcessError` traceback prints the N4 command — including `https://fakeuser:ghp_<36×C>@github.example.invalid/Arivoo.git` — to the **self-test's stderr** (grep: 1 unique canary); the "asserted absent from stdout AND stderr end to end … including failure messages" property is bypassed (assertions never run). Self-test exit=1 (fail-closed). The checker subprocess's own output never leaked (see verdict).

12. **P2 — vacuous green when `.git` is absent.** Repro (A7): tree copy with `.git` removed and canary written into `STATE.md` → EXIT=0 GREEN, including `[PASS] no secret value patterns in tracked repo files (all tracked text files incl. context/raw/)` — while zero files were scanned (both git probes fail; the anti-vacuity guard at line 146 fires only when `.git` exists). Contradicts the code's own stated intent to surface rather than false-green a vacuous scan.

13. **P3 — `--ci` presence-only semantics + exact-match arg parsing.** Repro (A8/A8b/A8c): `--ci` with all 5 required vars present but empty (`CI= GITHUB_ACTIONS= …`) → GREEN "all required CI configuration present"; `CI=false GITHUB_ACTIONS=false` → GREEN; `--ci=true` (not exact `--ci`) → silently local mode, CI-config check skipped entirely → GREEN. "A --ci run outside a configured runner must FAIL, not silently degrade" is violated in all three.

14. **P3 — exit-code contract note (could not falsify toward false-green).** No uncaught-exception path in `check()` found: the comprehension's `if` filter evaluates before `line.split()[0]`, so even a remote URL containing embedded newlines (which does smuggle a credential past the parser — A13, contrived) yields no IndexError. The only crash path is the self-test harness (#11), which exits 1 (fail-closed).

## 3. VERDICT (per claimed catch-class)

- **(a) Credential in git remote URL: REFUTED.** scp-syntax remote `ghp_<36×C>@host:org/repo.git` exits 0 GREEN (A6i) while the credential sits in `.git/config`; canonical `https://user:pass@host` and `url.insteadOf` forms ARE caught; `http.extraheader` (same rationale, standard Actions form) exits 0; and username-only `ssh://git@`/`https://user@` cause false REDs (A6ii/iii).
- **(b) Unexpected secret-NAMED env var: REFUTED.** Eight secret-named shapes (`TOKEN2`, `SSH_KEY`, `DB_PW`, `PASSPHRASE`, `DEPLOY_KEY`, `MYTOKEN`, `PERSONALACCESSTOKEN`, `AWS_ACCESS_KEY_ID`) set to canaries exit 0 GREEN, "0 secret-named total" (A5); canonical `*_TOKEN`/`*_PASSWORD`/`_PAT_` forms are caught.
- **(c) Missing required CI config in `--ci` mode: CONFIRMED.** `--ci` with only `CI=true GITHUB_ACTIONS=true` → exit 1 RED listing the 3 missing vars (control run); caveat: present-but-empty/false values and `--ci=true` parsing degrade to GREEN (P3, #13).
- **(d) Secret VALUE patterns in tracked files: REFUTED.** Tracked `deploy.sh`/`CREDENTIALS`/`notes.rst`/`NOTES.MD` containing `ghp_<36×A>` exit 0 GREEN while the tool prints "all tracked text files" (A1/A4); the generic-assignment pattern misses any value containing the letter "s" and all unquoted forms (A9/A9b).
- **(e) Tracked `.env`: REFUTED.** Tracked `context/.env` (with a secret inside) and an index-tracked-but-worktree-deleted root `.env` (recoverable via `git show :.env`) both exit 0 GREEN, "[PASS] no tracked .env file" (A2/A3); only the root-present+tracked happy path is caught.
- **Redaction ("prints conditions, never values"): CONFIRMED for the checker itself.** Sweep run with all five leak classes live simultaneously (remote canary + env canary + tracked-file canary + tracked `.env` + missing CI): exit 1, zero canary bytes in stdout and stderr (grep counts 0/0); held across every one of ~40 checker runs — only names, remote names, paths, and labels were ever printed. **REFUTED for the self-test's "end to end … including failure messages" claim**: the harness's own crash path prints its canary to stderr (A11), and mutation tests show the matrix cannot detect loss of claims (e)/(d-extension) (A12).

## 4. NOT TESTED, AND WHY

- A real GitHub Actions runner environment (does `CI_EXPECTED_ENV` suppress runner-set secret-named vars beyond `GITHUB_TOKEN`, or false-positive on them) — no runner available in this sandbox.
- Windows path separators / non-UTF-8 git output (undecodable remote names raise inside `subprocess.run`, caught by the broad `except` → remotes PASS-vacuous, ls-files vacuous-RED if `.git` exists) — reasoned from code, not executed; no Windows host available.
- Git-history scanning (committed-then-`git rm`'d secrets) — not claimed by the tool, so out of scope; the tool's own repair text ("scrub git history") implies it knows the limit.
- Timeout/DoS behavior beyond the 10s git timeouts and 60s subprocess timeout — not reachable with a 5.4 MB repo.
- Real credentials: none used, none searched, per rules; all canaries synthetic (`ghp_`/`gho_` + 36 identical letters, synthetic AKIA/password strings).

No fixes applied; nothing in `/home/z/my-project/arivoo` was modified by me (its pre-existing uncommitted `tools/isolation_check.py` edit predates this session).

### 7.2 Falsification round 2 (re-verification after the repairs) — the fresh-context verifier's report (verbatim)

> (the same sub-agent, resumed with the fix list and a re-attack mandate; it
> verified each round-1 fix and attacked the repaired checker with new ideas)

RE-TEST REPORT — v2.1 of `arivoo/tools/isolation_check.py` (fresh temp copies, synthetic canaries only, repo untouched — its only `git status` entry is the author's pre-existing uncommitted v2.1 edit, mtime 13:33:35, before my attacks)

Setup for all repros: `A=/tmp/r-attack-X; cp -a repo $A; rm -rf $A/.git; git -C $A init -q; git -C $A add -A -f`; run `env -i PATH=… HOME=/tmp python3 $A/tools/isolation_check.py`. Canaries: `ghp_/gho_`+36 letters. ~45 checker runs, 5 mutation tests of the self-test. Canary-absence conclusions use in-sandbox `grep -c` counts (this sandbox's display layer masks ghp_-shaped strings, so I never relied on eyeballing; counts are computed before display).

## 1. RE-VERIFICATION (original findings 1–14)

1. **FIXED.** Canary in tracked `deploy.sh`/`CREDENTIALS`/`notes.rst` → exit 1, all three listed. Matrix pins it: re-inserting the old extension allowlist makes case 7 FAIL → SELF-TEST RED.
2. **FIXED (core).** `context/.env`, `.env.local`, `deploy.env` → exit 1 (env-family FAIL + value FAIL). Residual: weak family names below (new attack N4).
3. **FIXED.** Root `.env` staged then worktree-deleted → exit 1 ("unscannable" + env-family).
4. **FIXED.** `NOTES.MD`/`data.YML` → exit 1.
5. **FIXED.** chmod-000 and deleted tracked files → "unscannable" FAIL, exit 1.
6. **FIXED (core).** All 8 original shapes (TOKEN2, MYTOKEN, PERSONALACCESSTOKEN, SSH_KEY, DB_PW, PASSPHRASE, DEPLOY_KEY, AWS_ACCESS_KEY_ID) → exit 1. PATH/PWD/OLDPWD/HOME/EXPAT/PATCHSET/GITHUB_PATH → still GREEN (no FPs). Residual stems: N5 below.
7. **FIXED.** scp `token@host:path` → exit 1; benign `git@github.com:org/repo.git` stays GREEN. Residual: N1/N3 below.
8. **FIXED.** `ssh://git@host:2222/…`, `https://user@host/…` → GREEN.
9. **STILL BROKEN (regression introduced by the fix).** Unquoted/12+/s-containing values now caught (`pw: SYN…`-form, `TOKEN=…`, the pw = "hun…"-form → exit 1), BUT the new leading `\b` excludes underscore-compounded keys: tracked files with the db_password / client_secret / MY_API_KEY key forms (values 12+ chars) → **exit 0 GREEN** (v1 caught `db_password`; unit probe: all three NO-MATCH). `client_secret`/`db_password` are canonical secret key names → P2, borderline P1. The matrix cannot see it (M2: deleting the generic pattern entirely leaves 12/12 GREEN).
10. **STILL BROKEN (partial).** 12 cases now (docstring still says "10-case" — cosmetic). Extension coverage, unscannable, not-a-repo, benign-remotes, N1–N4b, N3 are genuinely pinned (mutation-verified). But mutation testing shows 5 unpinned surfaces: (i) `_is_env_path` → `return False` (claim (e) fully dead) → **N5 still PASSes, SELF-TEST GREEN** — the case is masked by value-pattern + unscannable findings and its ".env" fragment is satisfied by other lines; (ii) generic-assignment pattern (M2 above); (iii) extraheader advisory (`if False and "extraheader"…` → 12/12 GREEN); (iv) unknown-flag/exit-2 handler (killing it → 12/12 GREEN and `--ci=true` silently exits 0 — the exact finding-13 regression, invisible); (v) `--ci` value semantics (no case with `false`/empty values).
11. **FIXED.** Fake git failing `remote add`: harness prints "case … FAIL — harness/setup error: CalledProcessError (details redacted…)", stderr 0 bytes, no traceback, no canary, exit 1.
12. **FIXED.** No `.git` (tarball tree, canary in STATE.md) → exit 1 "not a git repository". git-unavailable and empty-index branches fail closed by code inspection.
13. **STILL BROKEN (narrow).** Empty values ✓ exit 1; lowercase `false` ✓ exit 1; `--ci=true`/`--bogus` ✓ exit 2. But `GITHUB_ACTIONS=False`, `=FALSE`, `=" false"` (case/whitespace variants of the literal `in ("", "false")` comparison) all count as PRESENT → **exit 0**.
14. **No crash paths found** in `check()` (the `if` filter still short-circuits before `line.split()[0]`); newline-in-URL with a `:pass@` fragment now RED; non-token newline form still missed (N3-class, P3).

## 2. NEW ATTACKS

- **N1 (P2, class a miss — credential confirmed in .git/config):** multi-@ remote `https://fakeuser@team:ghp_<36C>@github.example.invalid/repo.git` → **exit 0 GREEN** even with a token-shaped canary. The parser splits userinfo at the FIRST `@` (`rest.split("@",1)[0]` = "fakeuser"); HTTP stacks (curl) parse userinfo at the LAST `@`, so the trailing `team:TOKEN` is the functional credential. `git remote -v` carries the canary (grep count 2) while the checker reports "no credential embedded".
- **N2 (P3, class a):** percent-encoded credential `https://fakeuser%3Ahunter2secret12@host/…` → GREEN (`%3A` defeats the `":" in userinfo` test; non-token value defeats the pattern test; curl percent-decodes userinfo). With a token-shaped canary it IS caught (pattern hit).
- **N3 (P3, class a):** newline inside the URL (`https://user\n\nhunter2secret12@host/repo.git` via `git config remote.origin.url`) → GREEN (each output line fails the filter). Exotic; requires config hand-editing.
- **N4 (P3, class e):** `.env`-family weak names — tracked `.ENV`, `env`, `.envrc`, `settings.env.local`, `prod.env.bak` with unpatterned content → GREEN (no env-family FAIL). Patterned content is still caught by the value scan (control: `deploy.env` with canary → RED), so this is a family-class gap, not a value gap.
- **N5 (P2/P3, class b):** remaining name stems that dodge: `DB_PASS`, `MY_PASS`, `PASS`, `SSH_KEYS` (KEY guard has no plural-S), `USERPW` (no boundary). `GPG_KEY`/`SIGNING_KEY` are caught. Per the checker's fail-closed philosophy `DB_PASS`/`PASS` should be caught (bare `PW` already is — `PASS` was simply never added as a stem).
- **N6 (P3):** CI-mode allowlist is prefix-wide: `ACTIONS_TOPSECRET=<canary>` → "expected CI env var present … PASS" (any `GITHUB_*`/`ACTIONS_*`/`RUNNER_*` secret-named var is suppressed in `--ci`; documented policy, but fail-open — e.g. `GITHUB_ENTERPRISE_TOKEN` would be silent).
- **N7 (P3, advisory):** worktree checkout (`.git` is a FILE): the advisory reads `repo/.git/config`, which doesn't exist in a worktree → extraheader credential present in the shared config, checker prints GREEN with **no advisory** (verified with a real `git worktree add`).
- **N8 (P3, advisory):** hand-edited config with case-variant key `extraHeader` → advisory silently absent (substring check is case-sensitive; git CLI writes lowercase, so this needs manual editing).
- **N9 (P3, redaction edge):** paths are echoed verbatim — a tracked file NAMED `ghp_<36A>.md` deleted from the worktree puts the secret-shaped string into TWO stdout lines (the unscannable FAIL line and the findings line; grep count 2, stderr 0). Values are never printed, but path bytes can be secret-shaped.
- **N10 (controls, all pass):** IPv6 `https://user:pass@[2001:db8::1]:8443/…` → RED; `ssh://git@[::1]:22/…` and bare-bracket URLs → GREEN; bare PAT as username `https://ghp_<36C>@host` → RED; `url.insteadOf` still RED (git displays the rewritten URL); opaque non-token username (`https://hunter2secret12@host`) → GREEN (username-indistinguishable — undecidable, acceptable); unicode filenames → unscannable RED (fail-closed FP direction, fine); advisory never prints values (static string; grep count 0 for canary/base64).
- **Self-test on temp copy: 12/12 PASS, exit 0** (and on the real repo). Harness crash path sanitized (R11).

## 3. VERDICT

- **(a) Remote-URL credential: REFUTED (one form).** Canonical forms all caught (https user:pass@, bare PAT username, scp token@host:path, IPv6, insteadOf, %3A-with-token) — but a multi-@ URL carrying a token-shaped credential in the (curl-parsed) trailing userinfo exits 0 GREEN with the credential confirmed in `.git/config` (N1). Non-token encoded/newline/opaque-username forms also exit 0 (undecidable or exotic — residual).
- **(b) Secret-named env var: REFUTED (narrow).** All 8 originally-missed shapes now exit 1, but `DB_PASS`/`MY_PASS`/`PASS` (and `SSH_KEYS`/`USERPW`) with canary values exit 0 — bare PASS is as credential-shaped as the caught PW; plus CI-mode prefix-wide suppression of `GITHUB_*`/`ACTIONS_*`/`RUNNER_*` secret-named vars.
- **(c) Missing required CI config: CONFIRMED.** Partial/empty/lowercase-`false` → exit 1 (verified); residual: `False`/`FALSE`/`" false"` case-and-whitespace variants of the literal comparison exit 0.
- **(d) Secret value patterns in tracked files: REFUTED (generic pattern only).** Token-shape patterns (ghp_/gho_/ghs_/github_pat_/AKIA) confirmed on every extension/case/extensionless file; unquoted and s-containing generic assignments now caught — but the fix's leading `\b` re-opens a hole: the db_password / client_secret / MY_API_KEY key forms with 12+ values exit 0 (v1 caught `db_password`), and the self-test cannot detect even total deletion of the generic pattern.
- **(e) Tracked .env: CONFIRMED (as enumerated).** Root, nested (`context/.env`), suffixed (`.env.local`, `deploy.env`), and index-tracked-but-deleted all exit 1. Residual weak names (`.ENV`, `env`, `.envrc`, `x.env.local`) exit 0 unless content matches a value pattern.
- **Redaction ("conditions never values"): CONFIRMED.** Zero canary bytes in stdout/stderr across every checker run (grep -c counts; remote names/env names/labels/paths only; advisory static). Two P3 edges: (i) secret-shaped FILENAME bytes are echoed in path lines (N9); (ii) the usage-error line on exit 2 echoes the offending flag verbatim (caller-supplied argv — not a checker-found secret).

## 4. RESIDUAL LIMITS WORTH RECORDING

1. Undecidable class (a) forms: a non-token-shaped secret used as a bare username (https or scp) is indistinguishable from a username — document rather than "fix".
2. Multi-@ and %-encoded userinfo: parsers disagree; the checker's first-`@` split diverges from curl's last-`@`/percent-decoding semantics — worth a documented decision.
3. The self-test's unpinned surfaces (finding 10 list): .env-family check, generic-assignment pattern, extraheader advisory, unknown-flag exit 2, --ci value semantics — each provably removable without the matrix noticing; N5's fragment `".env"` is too generic and the case is over-determined (masked by two other findings).
4. CI-mode allowlist is prefix-wide (fail-open) for GITHUB_/ACTIONS_/RUNNER_ namespaces.
5. Advisory blind spots: worktree checkouts (`.git` file) and case-variant config keys never see the advisory.
6. Worktree/history/index scope: content scan is worktree-state only (stated design); git-history secrets are out of claimed scope.
7. Docstring drift: "10-case" vs actual 12; `BENIGN_USERINFO` is a dead constant; the remotes PASS line prints "forms checked" even when the git probe failed (masked by section 3's fail-closed exit).
8. Not tested: a real GitHub Actions runner (prefix-allowlist interactions), curl last-@ semantics offline (no network to example.invalid), Windows path/encoding variants.

No fixes applied; nothing in `/home/z/my-project/arivoo` was written by me.

**Round-2 disposition (this session, same-session repairs per the loop's method):** every STILL-BROKEN item and every actionable new attack was repaired before this PR — finding 9's `\b` regression (pattern now matches underscore-compounded keys; pinned by matrix case N10), N1 multi-@ userinfo (authority + LAST-@ split; pinned by case N1b), N5 stems (PASS/KEYS added), N4 weak env-family names (case-insensitive family matcher; pinned by case N5b), finding 10's five unpinned surfaces (matrix grown 12 → 18 cases, each pinning one surface), N7/N8 advisory resolution (worktree .git files + case-insensitive config scan; pinned by case N11), N9 path echoes (redaction pass on all printed paths), finding 13 variants (`_ci_value_missing` casefold+strip; pinned by case N13), docstring drift and the dead constant (removed), and the remotes-probe failure line (now an attributable FAIL, not a masked PASS). Residuals deliberately NOT "fixed" (documented in §9): the undecidable bare-username class, %-encoded non-token userinfo, newline-in-URL, `env`/`USERPW`-class names, the CI prefix-wide allowlist (runner-namespace policy), git-history scope, and the usage-error argv echo.

## 8. Failures (this slice)

- **The .pyc artifact incident (found by the new checker itself):** PR #20's `git add -A` accidentally committed `tools/__pycache__/verify_canonical_layer.cpython-312.pyc` (created by this session's `python3 -m py_compile` syntax check). The v2.1 checker's unscannable-file guard caught it on the very next run ("tracked file missing from worktree or unreadable" — the file had been cleaned from the worktree while remaining in the index). Disposition: untracked in this PR + `.gitignore` (`__pycache__/`, `*.pyc`) added as the regression guard. The guard's first real catch was this session's own mistake — the falsification loop's philosophy working end to end.
- **Round-1 defects (3 P1 false-greens + 7 P2/P3):** all repaired same-session; every repair verified by round 2 (§7.2 §1) and pinned by matrix cases.
- **Round-2 residuals (repaired):** the `\b` regression, multi-@ userinfo, False/FALSE CI variants, PASS/KEYS stems, unpinned matrix surfaces, worktree .git advisory, secret-shaped path echoes — repaired and pinned (§7.2 disposition note).
- **Self-reference false positives (found by local runs, not the sub-agent):** the checker's own fixture literals (keyword=value shaped) matched the generic-assignment pattern when the scan read the checker's source as a tracked file — repaired by concatenation-built fixture strings (the self-reference guard, commented in the source) + the fixture's `__pycache__` exclusion.

## 9. Unverified items (this slice)

- The undecidable class (a) forms (a non-token secret as a bare username; %-encoded non-token userinfo; newline-in-URL) — documented residuals, not "fixed" (a fix would be a heuristic pretending to be a guarantee).
- The CI runner-namespace allowlist (GITHUB_/ACTIONS_/RUNNER_ prefix suppression) is fail-open within those namespaces — observed policy, not a per-var guarantee; a real-runner interaction test happens in this PR's head-tools run (first CI exposure of the v2.1 checker).
- Git-history secret scanning — out of the tool's claimed scope (worktree + index only); the repair text says "scrub history" for the leak classes it does catch.
- Windows path/encoding variants and a second model family's review (optional adversarial coverage, never a prerequisite — INT-117).
