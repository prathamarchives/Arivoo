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
