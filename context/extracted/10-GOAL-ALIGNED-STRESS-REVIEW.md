# 10 — Goal-Aligned Architecture and Agentic-Repo Stress Review

> STATUS: SESSION ENGINEERING RECORD — 2026-10-13. This is an engineering assessment, not owner intent and not a decision record. It does not amend the Intent Ledger or silently resolve an owner question. Target reviewed: main at 4b19d803481dce7427ff2cb276b4420b3afb3131. The owner’s words remain authoritative in INTENT-LEDGER.md; interpretations and recommendations live here.

## 1. Verdict

Arivoo’s first layer now expresses a coherent product thesis and a serious agent-engineering doctrine. The Intent Ledger has 72 contiguous, unique, statused entries (INT-019–INT-090). The root files distinguish intent, principles, laws, decisions, execution authority, plan, vocabulary, and operating model. The engineering doctrine reflects the two critical ideas from the supplied engineering material: agents need direct ways to test real behavior, and the codebase must make good patterns easy to extend while preventing recurring bad patterns.

But the claim must be precise: **the repo is a strong specification of an intended agent-native system; it is not yet an enforced agent-native development environment.** The repo declares Model 0 — repository memory, no product code. The current tree has no Makefile, CI workflow, active slice-card directory, generated state command, or product implementation. This is not a failure of the declared stage. It means the zero-context property has been tested as document understanding, not yet as a real implementation-and-verification task.

The highest-risk problem found is not missing documentation. It is that the current canonical-layer checker can report green while missing later Intent Ledger entries and while its status validation cannot catch an invalid status. A trust system whose own regression check has blind spots can give agents unjustified confidence.

No root canonical document was changed during this review. The recommendations below are candidates for narrow slices; they are not silently adopted decisions.

## 2. Method and limits

Reviewed the live main tree, all root canonical files, the complete Intent Ledger, the operating model, plan, decisions, execution authority, the current canonical-layer checker, the previous session review, worklog tail, raw engineering transcript, and upstream engineering treatise. Ran source-text checks against the current GitHub-fetched files for ledger ID continuity, checker coverage, rule conflicts, file presence, and selected cross-document contradictions.

The ledger check found 72 IDs, INT-019 through INT-090, with no gaps or duplicates. The live checker was inspected but **tools/verify_canonical_layer.py was not executed in this review session**. The current commit has no reported commit-status checks. I could not verify the repository’s branch-protection configuration through the available GitHub connector. Therefore this report does not claim that remote walls or CI are absent or present; it records them as unverified. The tree itself does not contain a GitHub Actions workflow or the other listed live harness assets.

The raw engineering transcript included in the repository ends mid-sentence. Preserve the raw archive unchanged, but do not describe that file as a complete transcript of the source talk unless its completeness is verified.

## 3. Goal alignment: what the architecture gets right

### 3.1 Arivo is a compounding environment, not a pile of notes

The product goal is to make reading, study, research, writing, reasoning, highlights, bookmarks, notes, and journal entries accumulate into a usable personal knowledge environment. The system must help retrieve something read earlier, preserve what the owner thought about it, and connect material across sources. The journal is a writing and thinking surface, not merely a daily log. Notes are not disposable sticky notes.

That is reflected in NORTH-STAR’s claims, the Work/Source split, stable highlight identity and anchors, revisioned notes and journal blocks, durable @-references, the day-one import requirement, and the separate compounding probes. This is directionally correct.

The test of C3 should remain behavioral: a known link retrieves older material; a new related source causes relevant prior material to resurface; automatic relationship creation adds useful connections without turning discovery into evidence. A generic “search works” test does not prove compounding.

### 3.2 Persistence and provenance lead the design

The durability ladder and two-outbox model are good foundations. Capturing an action must not wait for semantic extraction or model decisions. The system must be honest about whether an item is only local-durable, server-durable, searchable, semantically indexed, or linked. Ground-truth evidence and derived interpretation are different kinds of data. Derived output needs enough provenance to explain, rebuild, invalidate, and reverse it.

This directly serves the worst failure the owner named: losing a highlight. The first implementation should prove persistence and recovery before it makes broad claims about intelligence.

### 3.3 Agents are clients, not authorities

The API/MCP boundary, scoped access, attributed writes, idempotency, and zero belief weight for agent-authored material align with the owner’s multi-agent intention. More than one agent should be able to read and contribute. An agent’s annotation or proposal is durable evidence of what that agent said, not independent corroboration that the content is true.

That distinction has to exist in the eventual schema and command registry, not just in prose. No agent should gain direct database access as a convenience.

### 3.4 Concepts need to emerge quickly without forcing labels on every highlight

INT-069 clearly sets the capture rule: tags are optional, custom, and owner-authored; there is no automatic default fact/concept classification at highlight time. P-10 also says auto-detected concepts should appear quickly as provisional and graduate only with stronger evidence. These are compatible if they are expressed precisely: a tag is one optional input, not a prerequisite for discovery.

The current C4 wording does not yet make that distinction clearly enough. See finding F-05.

### 3.5 Small verified slices are the right execution unit

The piece-by-piece law and one-phase-deep plan protect against both giant speculative architecture and premature deferral. Semantic indexing, vector retrieval, relationship processing, and concept formation are core capabilities in the active sequence. They must not become a vague “version two” promise. The implementation can be incremental without making the architecture disposable.

The harness must serve delivery. It should block unsafe or unverifiable changes, not demand a complete future testing platform before the first real behavior exists.

## 4. Findings: concrete gaps and corrections to consider

### F-01 — P0: The canonical-layer checker has false-green paths

Evidence in tools/verify_canonical_layer.py:
- The Intent Ledger range check is hard-coded to INT-019..INT-068, even though the current ledger includes INT-069..INT-090. The newest owner decisions can disappear from the checker’s scope while the checker remains green.
- The status parser’s regular expression only extracts the permitted strings active, clarified, superseded, or historical. The later “bad status” check examines only the already-filtered results, so an invalid or missing status can evade that check.
- The current checks do not prove that intent IDs are unique and monotonic, that a quoted owner statement matches its source text, that a cited INT-ID exists, or that required owner decisions are reconciled across every affected canonical home.
- The checker does not appear to have a mutation suite proving that it fails when its protected properties are deliberately broken.

The prior “27 checks green” establishes only that those particular string conditions passed. It does not establish that the whole layer is drift-proof.

**Recommended slice:** extend the verifier to discover the ledger’s current ID range rather than freeze the end at 068; detect duplicate, missing, invalid, and unexpectedly reused IDs; parse status independently of the allowed-status validation; validate source anchors and exact quote matches where practical; validate all references to INT/D/Q/LAW IDs; and check key cross-file contracts rather than only selected phrases. Add known-bad mutations for each detector: remove INT-090, duplicate an ID, corrupt a status, break a source quote, remove the GLM verifier rule, reintroduce the old deferral wording, and weaken a protection rule. Every known-bad must produce a named failure code. The verifier itself must be tested before it is trusted.

### F-02 — P0: “Silence past a named gate is consent” is unsafe and lacks an explicit owner basis

EXECUTION.md §6 says: “Silence past a named gate is consent.” This can be read to let an agent close an unresolved owner decision because time passed. The same contract says an agent must never close an open decision by interpretation; the question policy says blocking questions cannot be reclassified as defaultable. For a destructive, security, data-loss, or owner-intent decision, silence is not informed approval.

**Recommended correction:** distinguish three cases explicitly. A blocking question stops only the slice that depends on its answer; independent work continues. A defaultable, reversible choice may proceed with a recorded default, rationale, expiry/revisit condition, and lock gate. A decision that needs owner judgment—especially irreversible purge behavior, secrets, protected-path policy, or an ambiguous product requirement—stays open until the owner answers. Do not let a generic “consent” sentence override the question class.

This is a recommendation for owner-governance policy, not a change I have made to the canonical files.

### F-03 — P0: The GLM verification choice is not consistently authoritative

INT-070 says test and verification loops are run by GLM-based subagents and GLM is the host for verification/testing/iteration. AGENTS.md and Model 0 acknowledge this. However, DECISIONS.md and EXECUTION.md still describe the default as a cross-family verifier, and OPERATING-MODEL.md says a different model family is recommended where possible. A cold agent could follow either rule.

**Recommended correction:** make the current operating contract unambiguous: GLM-based, fresh-context subagents perform the test, falsification, verification, and fix/retest loops. Keep builder and verifier roles separate at the session/task level: the verifier does not implement the code it is judging, and the gate—not the verifier’s prose report—decides. A second model family can be an optional additional adversarial audit, never a hidden prerequisite that contradicts the chosen GLM workflow.

Independence must come from the verification design, not from the model brand: acceptance criteria fixed before implementation; a verifier that did not write the implementation; a real running path; independent state reads; fault, property, and mutation tests; frozen known-bad cases; protected gates; and checks that the verifier cannot quietly weaken. A same-family GLM verifier can still find defects if those controls hold. A different-family reviewer can still agree with a shared misunderstanding if the oracle is weak.

### F-04 — P1: Session memory rules are weaker than the requested handoff guarantee

INT-072 states that whatever agents do should be documented so another agent can resume from the repo. AGENTS.md requires a numbered engineering record when root documents or extraction state change, but a meaningful code, test, investigation, or verification session that leaves those areas untouched could finish without a self-contained engineering record.

**Recommended correction:** every meaningful work session gets a numbered session record, irrespective of which files changed. The WORKLOG remains the short coordination index and points to the record. The record should identify the owner request and INT IDs, task/slice, starting commit, scope, files changed, exact commands and results, evidence links, regressions/failures found, not-verified items, unresolved questions, and the next deterministic action. Do not require a private chain-of-thought dump: preserve decisions, grounds, tests, and the reproducible work state, not internal monologue.

For multi-agent runs, each subagent’s useful result must land in the shared task record or a linked artifact before the orchestrator closes the task. “It was in a subagent transcript” is not durable repo memory.

### F-05 — P1: C4 risks making tags a gate for concept formation

NORTH-STAR says “Concepts form with provenance, from tags,” then says there is no default fact/concept classification and concept formation reads owner-authored tags. P-10 separately permits immediate, provisional auto-detected concepts. A literal agent may conclude that an untagged highlight cannot contribute to discovery, or may start assigning system-owned labels to compensate.

**Recommended correction:** preserve the owner’s tag control exactly. The owner may add any custom tag or none. Owner-declared concepts and explicit owner tags are authoritative expressions of the owner’s intent. The system may also detect provisional concepts and relations from material, recurring attention, structural relationships, and grounded evidence without forcing a capture label on the owner. These machine-discovered objects are provisional, attributed, and reversible; they must not be represented as verified truth or graduate merely because a large volume of similar generated material exists. Source independence and out-of-sample tests belong at graduation, not at concept birth.

This wording change should explicitly say “tags are a signal, not the only creation path.” Q3 remains open only for how an optional manually applied fact tag is interpreted; it must not become a blocker for arbitrary custom tags or ordinary capture.

### F-06 — P1: Cloud deployment and local-first capture are described ambiguously

D-003 says “Postgres + pgvector; local-first now; cloud sync later.” D-020 calls the cloud-hosted backend active and distinguishes local durable capture from cross-device sync. The owner’s corpus also records the intention to host the backend in the cloud. As written, “local-first” may refer to local durability, local database authority, or local-only hosting. Those are materially different architectures.

**Recommended correction:** separate three meanings in one explicit deployment decision: where the authoritative backend/Postgres instance runs; how the client accepts durable work offline through the client outbox; and when cross-device synchronization and conflict resolution become operational. Do not assume “local-first” means the app’s primary database must be local, and do not silently rewrite D-003 based on the newer interpretation. Ask the owner to ratify one precise statement at the deployment decision gate.

### F-07 — P1: Q1–Q3 appear to block more work than their actual decision gates require

The operating model says the machine does not idle and a blocking question stops only dependent work. Yet Model 0 graduation and AGENTS.md describe answering Q1–Q3 before Phase 1. Q2 is specifically a purge/backup question whose gate is Phase 3; Q3 matters at the Phase 3 vocabulary/fact-tag gate only if the owner uses a fact tag; D-014 is explicitly non-blocking for capture; Q1’s remaining ambiguity concerns the primary builder host and host bridges.

This makes it appear that Phase 1 walls, isolation checks, and CI cannot advance until questions whose decisions are not yet needed are answered. It also risks turning a desire for precise owner control into a global approval queue.

**Recommended correction:** keep phase approval as its own explicit gate, but classify open questions by the slice they affect. Run independently safe Phase 1 work when the phase is authorized; block only a host-specific bridge on the host question if that is the only dependency. Carry Q2/Q3 to their named Phase 3 gates. This follows the written question model; it does not authorize changing owner-only security or purge decisions by default.

### F-08 — P1: “A fresh agent just knows what to do” is not yet proven on an actual task

The prior stress test is valuable: a fresh GLM subagent was able to answer repository questions from the docs and found several drift edges. But the repo currently has no product code, CI workflow, Makefile, generated STATE, or active self-contained slice card. The actual one-shot property—fresh agent, repo only, bounded change, first-cycle pass with proof—has not yet been tested because the implementation loop does not yet exist.

A repository can provide the global context and constraints without a long prompt. It cannot select an unambiguous next task from an unlimited product vision unless it has a canonical active-work pointer.

**Recommended correction:** make cold start produce an explicit state and next action from the repo: current phase, current slice/card, its owner INT IDs and direct quotes, scope, allowed files, must-reject cases, acceptance criteria, commands, known-bads, open blocking questions, and continuation conditions. A generic prompt should only tell the agent to enter the repository workflow; it should not repeat the product background. The repo must say whether the current next action is (a) a safe slice, (b) a question record for an actual blocker, or (c) a completed gate. Test this using a fresh GLM session with no chat context and measure first-cycle success.

The next useful proof is not another large document pass. It is a tiny self-contained card and an enforced end-to-end task through the first live harness.

### F-09 — P1: The corpus extraction is larger, but completeness is not mechanically auditable

The ledger itself is now cleanly numbered and substantially broader. The archive is mixed material with repetitions, pasted external writing, assistant proposals, and owner statements. Current audit notes point to selected regions of 0.txt and 1.txt; the previous review also notes that some engineering sources were not re-read in full during that particular extraction session. That does not prove the ledger is incomplete, but it means “every substantive owner intent has been captured” remains partly a human assertion.

**Recommended correction:** add a source-coverage manifest separate from the Intent Ledger. For each source file and section, record whether it contains owner words, assistant analysis, third-party material, or generated documents; identify the reviewed range; map each genuine owner statement to an INT ID; and record exclusions or duplicates with reasons. Validate every ledger quote against its source. Mark the source transcript that ends mid-sentence as incomplete. Keep the raw files immutable. The manifest is a coverage control, not a place to add assistant interpretation into owner intent.

The existing ledger must remain owner-words-only. Notes about the owner’s preferences, judgment patterns, or behavior belong in clearly labeled review/session records like this one, not in the Intent Ledger.

### F-10 — P1 before Phase 5: Belief and relationship claims need a falsifiable policy model before they reach production data

Current docs correctly say discovery is not evidence, agent-authored material has zero belief weight, evidence for inferred links comes from grounded text-pair decisions or structural facts, and every derived claim must be explainable and reversible. Those are necessary constraints, but not yet enough to choose and lock the belief substrate.

Before the belief/relationship implementation is schema-locked, create a small deterministic simulator and known-bad cases for at least:
- The same work repeated in several imported forms must not masquerade as multiple independent sources.
- Owner notes, journal entries, and agent annotations about a source must not be counted as independent corroborating works merely because they refer to it.
- Generated/discovered candidate links must not supply their own evidence.
- The same model’s prior confidence must not circularly reinforce its later decisions without independent grounding.
- Invalidated or superseded source/model outputs must be removable and replayable; non-revisit or recency alone must not be treated as truth decay.
- Relationship hubs and repeated near-duplicates must not swamp independent-work evidence.
- All derived edges and concepts must be reconstructible from cited evidence, model/rule version, and run provenance.

Use actual proposed Kev behavior and versioned policy as simulator inputs when available; do not speculate about thresholds before measuring. This is an engineering recommendation for a Phase 5 design gate, not owner intent and not a revival of any old proposal that was superseded by later autonomy/evidence decisions.

### F-11 — P2: Verify the raw engineering source’s completeness

The raw engineering transcript in the repo ends mid-sentence. The doctrine in ENGINEERING.md covers most of the material that is present: real-app verification, feature maps as operational memory, a constraint ladder, restricted capabilities, one paved path, proof-carrying changes, gardening, self-maintenance, and testing the engineering environment itself. Still, the repo should distinguish “captured source excerpt” from “complete source transcript.”

**Recommended correction:** leave the raw archive unchanged and note its incomplete capture in the source-coverage manifest. Retrieve or recapture the remainder only if it is available and needed to substantiate a claim. Do not manufacture an ending or claim the absent part was reviewed.

### F-12 — P2: Some completion language is stronger than the evidence

AGENTS.md calls the first layer canonicalized and stress-tested, and the previous review says the zero-context property “holds.” That is fair for the specific document Q&A and selected text checks that were run. It should not be read as proof that all source intent has been captured, every authority conflict is automatically detected, all host bridges are installed, remote CI is authoritative, or a real coding agent can one-shot a feature. Some of those are explicitly future stages; others were not verified.

**Recommended correction:** label claims by scope: document consistency tested; source coverage manually reviewed or mechanically verified; host behavior verified on named version; local test executed; CI gate observed; product acceptance test passed. A claim must never imply a stronger rung of evidence than actually exists.

## 5. Owner/project fit — interpretation, not owner intent

The review of the owner’s words and working requests suggests these constraints matter especially for Arivo:

- The owner wants specificity and depth where architectural ambiguity matters, but not a ritual of documenting everything for its own sake. Reconcile enough to build, then validate decisions through real slices.
- The owner repeatedly rejects deferring core capabilities into a vague future version. Incremental delivery should preserve the whole architecture from the beginning.
- The owner values autonomous agents but does not delegate product judgment by default. Agents should propose a concrete choice, show its grounds and alternatives, record what remains open, and proceed on independent reversible work.
- The owner distrusts confidence, stale model memory, and AI-generated self-confirmation more than a reproducible test or a repository fact. Independent evidence should settle implementation claims.
- The goal is leverage from a growing body of reading, research, raw thinking, writing and connections—not vanity metrics or a generic notes database. Useful outcomes include retrieving a passage from prior reading, seeing a connection, preserving a nuanced note, and producing new writing.
- The user is designing Arivo’s interface independently through HTML prototypes. This repository should own the backend contracts and working API; it should not silently grow a competing UI. Define the contract clearly enough that the separate UI can integrate against it.

These are review interpretations of recurring patterns, not new Intent Ledger entries. I have not added them to the owner’s ledger. Also, the external “I love writing / I never let agents write for me” passage in the upstream file is third-party source material; it must not be misattributed to the owner.

## 6. Recommended repair sequence — small slices, no architectural restart

1. **Repair the checker first.** Make INT-019..INT-090 and future append-only entries part of the same audit; repair status parsing; check uniqueness, stale/orphan references, quote sources, required cross-document reconciliations; add known-bad mutations that prove each guard fires. Keep the output diagnostic and actionable. This is the highest-value trust repair.
2. **Reconcile the authority seams.** Resolve the GLM verifier wording to match INT-070. Remove or replace the unsupported silence-as-consent behavior. Correct the C4 tag/concept phrasing. Surface the cloud/local wording as an explicit owner decision if the intended deployment statement cannot be represented unambiguously. These are separate edits, not one broad rewrite.
3. **Make session handoff a real invariant.** Extend the session-record requirement to every meaningful task; add a source-coverage manifest and mechanically validate owner quotes and IDs; make the worklog point to the exact session record and commit.
4. **Close only true dependencies.** Present the remaining owner-gated decisions in a compact Decision Review. Do not let Phase 3 questions hold up unrelated safe Phase 1 work if the phase is approved and the dependency can be isolated. Do not close any owner-only question by silence.
5. **Build the first live trust loop and then product slices.** Set up the host contract, repository walls and owner-controlled CI; introduce a generated current-state/next-slice command and self-contained slice cards. Then implement and prove durable capture. Continue through the reader-capture-journal flow and day-one text/Markdown/conversation import. Bring in keyword, semantic/vector retrieval, relationship processing, concept formation, and Kev through small verified slices in the active sequence. Before Phase 5 schema lock, prove the belief policy in a simulator. Keep UI integration at the documented API boundary.

Do not write a giant implementation plan for every future layer. Let the current phase produce evidence that selects the next slice.

## 7. Acceptance conditions for the next review

A later review should be able to prove—not merely state—that:
- The canonical checker catches missing, duplicate, malformed, stale, and source-mismatched intent records, including the newest range.
- Deliberately broken policies make the checker fail with stable reason codes; valid edge cases pass.
- GLM-based builder and fresh-context verifier workflows do not conflict in the governing docs, and the verifier cannot quietly weaken the acceptance test or gate.
- No unresolved blocking or irreversible owner decision is converted to consent by elapsed time.
- Every meaningful agent session leaves enough durable evidence for a different agent to resume without chat context.
- A source-coverage manifest differentiates owner statements from AI analysis and third-party excerpts; raw data remains unchanged.
- A completely fresh GLM agent, given only the repository entry point, can discover the active slice, perform the approved work, run the real system, produce proof, and leave a correct handoff.
- Remote protections and CI are actually observed and recorded before the repository claims that those walls are live.
- The first product behavior is verified end-to-end, rather than inferred from document quality.

## 8. Not verified in this review

- The Python canonical-layer checker was inspected but not run locally in this review session.
- No CI workflow is present in the current tree; the latest commit has no reported status checks. Branch-protection settings could not be read through the available connector.
- The raw engineering transcript is incomplete at its ending.
- No product code, database schema, Kev evaluation behavior, running API, or actual slice was available to test. The belief-policy simulator is a future gate recommendation, not a result of a current implementation test.

**Final judgment:** preserve the direction and the first layer. The highest leverage now is not to add more doctrine. It is to make the existing claims mechanically testable, remove the few remaining authority contradictions, and move into the first real, narrow build-and-verify loop. The repository should grow like a garden: every change leaves better working patterns, better evidence, and a more reliable next change—not merely a longer memory.
