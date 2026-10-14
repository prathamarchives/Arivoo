# 14 — Navigation, Handoffs, Read Path: The Layer-1.2 Slices (STATE index · session records · cold start · replication)

> STATUS: **SESSION ENGINEERING RECORD (IN PROGRESS — 2026-10-14, the layer-1.2 session — INT-100..109/D-027).** Historical process artifact per D-022: assistant analysis and work record; NOT owner intent, outranks nothing. Owner words live only in `/INTENT-LEDGER.md` (INT-100..109 added this session; §1 below is their verbatim preservation home, written BEFORE the ledger entries — the closed INT-046/068 class). Worklog entry: Task 13 (appended at close). Verifier: `tools/verify_canonical_layer.py` + `tools/isolation_check.py` — runs recorded in §8. Sections §3+ are appended as each slice lands; the banner flips to complete at the close PR. PRs this session: #10 (this PR — turn-10 intake + slice 4), #11 (slice 5), #12 (slice-6 gate re-target), #13 (slice-6 read path + cold-start proof), #14 (replication kit), #15 (close). Branches `slice/*`; all merges under the standing P-13/P-15 authorization with this record as the change-channel basis.

## 1. What the owner asked (verbatim — owner turn 10, 2026-10-14)

> Slice 4: Build the current-state index
>
> Create one compact STATE.md as the proposed index for the current working position.
>
> It should answer:
>
> What phase are we in?
>
> What is the active task?
>
> What is the immediate next action?
>
> What has just been completed?
>
> Which owner decisions or dependencies remain open?
>
> Where is the latest evidence?
>
> Which PRs or reviews are pending?
>
> What is verified, what is only proposed, and what has not been checked?
>
> STATE.md is a pointer and status snapshot, not a second Intent Ledger or a second plan.
>
> Slice 5: Make session handoffs reliable
>
> Use existing memory mechanisms rather than inventing multiple overlapping logs.
>
> Every meaningful session appends a short worklog entry. Substantial work also produces a numbered session record. The record includes the starting revision, task, relevant intent references, results, files changed, commands actually run, evidence, failures, unverified items, open decisions, and next action.
>
> A session does not end with "done" or "tests passed" unless the evidence supports that statement.
>
> Proof: A fresh agent, given the repository and no previous chat, can resume a prior task and accurately identify what remains without requiring a full reread of the raw corpus.
>
> Slice 6: Make the read path efficient
>
> The cold-start path should be predictable:
>
> Read AGENTS.md.
>
> Read the current-state index and recent worklog entries.
>
> Read only the canonical documents relevant to the task.
>
> Follow the references to earlier sessions or raw material when necessary.
>
> Verify that any decision relevant to a consequential change is still current.
>
> The raw corpus remains immutable reference material, not mandatory startup reading.
>
> Proof: A cold-start test demonstrates both correctness and reasonable scope: the agent finds the relevant context without reading tens of thousands of unrelated words.
>
> make STATE a reliable current-position index
> I would keep the current file's basic shape and sharpen its contract.
> The index should tell an incoming agent, in a single pass:
> - Position: the phase and operating model, plus whether the next phase is being planned, approved or executed.
> - Work: the active task, what just completed, and one deterministic next action.
> - Dependencies: only the owner decisions and dependencies that affect the current work, with their authoritative homes.
> - Evidence: what has actually been verified, what is proposed, and what remains unverified—with pointers to the underlying evidence.
> - Coordination: pending PRs and reviews, or an explicit statement that none are pending, with a clear status reference.
> It should not copy the relevant history, restate the architecture, or become a second plan. STATE.md should point to the session record for details, DECISIONS.md for decision state, the worklog for recent coordination, and the run or PR for evidence.
> I would also make evidence labels precise. "Verified" should not be a general adjective that covers several very different things:
> - Verified by run: a named command or CI job, its result and an evidence reference.
> - Observed live: an actual external action or API response, with a link to the relevant evidence.
> - Behaviorally tested: a defined scenario passed, with the test record available.
> - Proposed: not yet adopted or approved.
> - Not checked: explicitly not verified, rather than implied to be false or complete.
> The current STATE already separates run, observed and behavioral verification. The missing piece is whether every meaningful claim has a sufficiently direct evidence pointer and a clear proposed/unverified status.
>
> Should slices 4 to 6 be treated as new supporting work under Phase 2 planning? No. It's still Phase 1. It's not Phase 2. It's just the 1.2 layer of Phase 1. It's just the next layer of Phase 1. After executing from the first slice to the third slice, the next layer contains slice 4, slice 5, and slice 6. That's how we are going to execute this.
>
> Should an active task describe work being performed right now, while exact next action describes the next task at session close? Yes, we should draw a line between the exact next action and the active task: the last agent that was doing, failed, or did, whatever. There should be a difference, you get me?
>
> No, bro, we are still executing this, and phase two is not in planning mode, pretty much. Everything is done, and we just have to execute that. Should state explicitly that phase two is in the planning stage and that product implementation still requires the approved execution plan. I guess yes. It's not in the planning stage. We are executing it. We are just at phase one right now, and it's being planned as we go. We execute, we iterate, and we refine each layer, so it will just be done there.
>
> Should the state list every unresolved owner question, or just the ones relevant to the current phase and the next action, with a pointer to the full decision register?
>
> The state should list every unresolved owner question because it's not about phases. It's about the whole repo, bro. It's not even about the long phases. The phases will just be done in a week, so it doesn't matter. The state should be like the repo: not short-term memory, but long-term memory. Treat it like that.
>
> Should every verification claim in state lead directly to one PR or session record? Yeah, it should.
>
> Should the PR review section be a snapshot of the state at the last repository update with evidence links, rather than something presented as live status? Yes, of course. A committed file cannot guarantee that external PR status has not changed since its last update.
>
> Do you want a hard size ceiling for state, or a soft rule that it remains one screen navigable and contains pointers rather than detail? I mean, bro, just don't overengineer it, insert, and write bullshit things in it that aren't necessary or don't make an impact. In the long term, don't treat this as a short-term memory, though. You get that?
>
> The repo already has the right two kinds of memory. I would preserve them rather than introduce another log format.
> The worklog answers: "What happened recently, and where should I go next?"
> A numbered session record answers: "What exactly happened in this substantial piece of work, what evidence supports it, and what remains unresolved?"
> The session record needs to preserve results, evidence and conclusions—not private internal reasoning. An incoming agent needs enough to reproduce or verify the work, not an exhaustive transcript.
> I would make the record fields mandatory and standardized:
> Field
> What it needs to preserve
> Starting state
> Starting commit, branch and relevant working-tree state
> Task and scope
> The requested work, bounded scope and relevant intent/decision references
> Results
> What changed, what did not, and why
> Files changed
> Exact paths and relevant IDs
> Commands and external actions
> Commands actually run, actual results, and links or identifiers for external actions
> Evidence
> Tests, CI runs, PRs, observations and their outcomes
> Failures
> Failed attempts, found defects, their dispositions and any regression guard
> Unverified items
> What was not run, not observed or could not be established
> Open decisions
> Owner decisions or dependencies that remain unresolved
> Next action
> One deterministic continuation point
> The last item is particularly important. "Tests passed" is not a handoff unless the record says which tests, against which revision, with what result. Similarly, "done" is not a useful status if there is still a missing proof or unmade owner decision.
> The existing session 13 record is already fairly detailed, including a real failure found before it could block later work. But its local-verification summary sometimes records results without a consolidated exact command/result tuple. For example, it names the verifier, self-test and isolation check and reports their results, while the proposed protocol could make the exact commands and exit codes consistently explicit. That is the kind of modest reliability improvement worth making.
>
> A substantial work also produces a number record intended to replace the current rule that every meaningful session gets one. Short meaningful sessions can have only a work log entry. define meaningful and substantial by event type, not by time spent. But the distinction itself must be explicit.
>
> What counts as a meaningful session? My proposed definition is any session that:
> - changes repository state
> - produces a material finding or verified result
> - an external system captures an owner decision
> - records a failure disposition
> - changes a task status or next action
>  Routine reading that produces no new finding or decision would not necessarily need its own entry. Yes, it is what I want.
>
> What makes work substantial enough for a numbered record?
> - An implementation slice (like my proposed list is an implementation slice)
> - A meaningful multi-step investigation
> - A review with findings
> - A verification comping
> - A material architecture decision
> - A failure investigation
> - A coordinated multi-agent department system work
>  I would not base this on the number of tokens or minutes because that's dumb.
>
> How short should the worklog entry be? Let's make it a bit more token- and cost-efficient. The last three worklog task entries are about 500 words apiece. That is a useful history, but not especially short for a navigation mechanism. I suggest a soft target of roughly 100, 200, or 250 words:
> - task
> - outcome
> - evidence
> - pointer
> - unresolved items
> - next action
>  The number record holds the detail. You and I would prefer this one.
>
> Yes, the must exact commands will be recorded for all local verification.
> preserve the actual command, the revision tested, the exit status and any material result. Keep raw output elsewhere if it is large, and link it. Do not reconstruct commands later from memory.
>
>  How should tool-only or API-only sessions record their evidence? My recommendation is that the record names the exact operation, its target, and the written result or link. If no shell command runs, say so. Do not create a fictional command log.
>
> How much starting state detail is mandatory enough for an agent, of course, to just not drift away and adapt to my environment in the repo? It should know everything, like the goal, man-type shit. My recommendation is to record the starting commit branch and whether the working tree was clean where work occurred across a PR, its base, head, and the merged revision. That would make stale sound boxes and ambiguous revisions easier to detect.
>
> Should a meaningful session that finds a defect but makes no changes still produce a durable record? My recommendation is yes. A verified finding, failed hypothesis or newly exposed dependency can alter the next correct action even when no file changed. Its record should say what was observed, what remains uncertain and what should happen next.
>
> Should session records reproduce each agent's detailed reasoning? My recommendation is no. Preserve the question, evidence, alternative dispositions where relevant, decision status, and reproducible result. The record is an engineering handoff, not a dump of every thought or every intermediate conversation.
>
> Bro, just don't overengineer shit. Just make it a bit token-efficient, and don't put that much pressure on the agent that it just keeps reading the repo and never gets on the work. It spends half of its usage on reading the repo and everything, so you get that: optimize. Add these optimization verifications, optimization sessions, and everything.
>
> The current boot protocol is predictable, but it is not yet selective. The full Intent Ledger alone is about 7,556 words, and the canonical read order directs agents to several other substantial documents before reaching the worklog tail.
> That order optimizes for having a broad context loaded. Your new proposal optimizes for acquiring enough context to do the current task correctly. Those are not identical objectives.
> My recommended direction is:
> 1. Read AGENTS.md for the purpose of the repository, authority rules and entry contract.
> 2. Read STATE.md and the recent worklog tail to identify the current position and next action.
> 3. Identify the canonical sources relevant to that task.
> 4. Verify the current intent and decision status behind any consequential change.
> 5. Follow references to older session records or context/raw/ only when the current task requires the underlying evidence or original source.
> The raw corpus stays immutable reference material and is not normal startup reading. Historical session records are also reference material, not automatic boot reading.
> There is a subtle authority issue here. The current instructions say the Intent Ledger must be loaded before forming any understanding. Your proposed read path makes STATE and recent worklog entries the first working-context sources after AGENTS.md, with canonical documents selected by relevance. We should explicitly decide whether that means removing full-ledger-first as a boot requirement and retrieving the relevant intent entries when needed, or keeping it and merely moving STATE/worklog earlier. I recommend the former: preserve the Ledger as the authority for owner words, without requiring every agent to read all owner words before knowing which task it is handling. That change must be reconciled in the canonical instructions; it should not remain an implicit exception.
>
> Should the new startup path intentionally supersede the current Intent-Ledger-first boot rule? My recommendation is yes: AGENTS.md → STATE.md → worklog tail → task-relevant canonical sources, with the source tiers and authority rules unchanged. Relevant owner-intent entries must be verified before consequential changes; the entire ledger need not be reread every time. This is the central design decision for Slice 6.
>
> How should an agent find relevant canonical sources when there is no task card? My recommendation is to use the next action in STATE as the entry point, then follow the links and IDs in the existing documents. If the next action is ambiguous, the agent should identify the ambiguity rather than compensate by reading the entire repository.
>
> How do we measure a "reasonable scope"? "Do not read tens of thousands of unrelated words" is the right principle, but the test needs an observable scope measure. My recommendation is to record the files actually read and the aggregate word count or token estimate; a cold-start proof should fail if the agent reads the raw corpus or unrelated historical records without a task-specific reason. Do you want a hard numeric budget, or should the first proof establish a baseline and let us set a budget from the result?
> 22. How much context should be read from the worklog? AGENTS.md currently calls for the last 3–5 entries. My recommendation is to start with the last three compact entries, follow the latest session-record pointer, and read older worklog entries only when necessary. That keeps recent context visible without turning the worklog into a second archive.
> 23. What should the cold-start agent be asked to do? My recommended test gives a fresh-context GLM agent only the repository and a realistic task—no previous chat and no hints about which files to read. It must identify the current phase, task, exact next action, relevant open decisions, latest evidence, and what has not been verified. It must point to sources for its claims and avoid unrelated raw/historical material.
> 24. How should that proof be graded? I recommend fixing a rubric before launching the agent. Grade factual correctness, correct handling of authority and unresolved decisions, a deterministic continuation point, evidence citations, and measured read scope. Use a separate fresh-context verifier to assess the result rather than letting the test agent grade its own success.
> 25. How broad should the first cold-start test be? My recommendation is one representative task from the current Phase 2 planning work, with a challenge that requires the agent to notice an open dependency and distinguish an observed result from an unverified claim. Once that passes, extend the test to other task types rather than making Slice 6 a full benchmark project. Do you want one representative test initially, or two contrasting scenarios from the start?
> 26. When should the cold-start proof run again? My recommendation is to rerun it when the entry point, read order, STATE schema, worklog/session-record protocol or source authority structure changes, and at the relevant phase gate. It should not become a heavyweight test on every unrelated documentation edit. The Phase 2 harness can make it more repeatable when that harness exists.
>
> Slice 4 passes when STATE is demonstrably concise and current, has the required status distinctions, points to authoritative sources instead of duplicating them, and directs a fresh agent to the right next action.
> Slice 5 passes when a real session ends with an honest worklog and, when required by the agreed rule, a numbered engineering record. A fresh agent can use the record to continue correctly without reconstructing the previous chat. The record must contain actual evidence and explicitly name what remains unverified.
> Slice 6 passes when a fresh agent can correctly resume a real task from the repository alone, cites the current sources behind consequential decisions, and stays within an agreed read scope without reading the raw corpus or unrelated history.
>
> I would handle this as three bounded slices in order:
> 1. Slice 4: Audit the existing STATE against the required fields, establish the proposed/adopted/verified distinctions and evidence-pointer convention, and correct only current-task inconsistencies. Avoid rebuilding the index from scratch.
> 2. Slice 5: Resolve the session-record policy conflict first. Then standardize the worklog and numbered-record templates, record the required command/evidence details, and test one handoff from a real completed session.
> 3. Slice 6: Reconcile the boot-order rules, define selective intent/decision lookup for consequential work, and conduct the bounded cold-start test. Update the canonical read order only after the behavior is proven.
>
> Make this whole system replicable. Do not make this whole system just for Arivo. I should be able to migrate and replicate it to my other projects, so take care.

**Provenance note (E-2/E-4 honesty):** this turn interleaves the owner's own voice with owner-forwarded analysis blocks (the "I would / My recommendation is" passages — E-4 class material, owner-presented, never owner-authored). §1 preserves the turn AS RECEIVED, mixed, per the raw-corpus convention for chat turns; the LEDGER quotes only the owner-voiced fragments (INT-100..109), and the forwarded recommendations are adopted through D-027 (ADOPTED, severable) — the exact INT-091/D-024 pattern.

## 2. Starting state and method

- **Starting revision:** `main` @ `e8a8259` (session-13 close; 0 open PRs; clean working tree). **Preflight runs (before any edit, this session):**
  - `python3 tools/verify_canonical_layer.py` → **GREEN — 46 checks, 0 failures** (exit 0)
  - `python3 tools/verify_canonical_layer.py --self-test` → **GREEN — 20/20 mutations caught** (exit 0)
  - `python3 tools/isolation_check.py` → **GREEN — 4/4 conditions** (exit 0)
  - `gh pr list --state open` → `[]` (0 open PRs); `gh api .../branches/main/protection` → `canonical-layer` required + strict, `required_approving_review_count: 0`, `enforce_admins: true`, no force-push/deletion (the Q-IDENT-compatible configuration, re-observed 2026-10-14)
  - `gh run list --branch main --limit 2` → latest run `38514278918` (success, @ `e8a8259`)
- **Method:** three bounded slices in the owner's order, each landing as its own PR chain — slice 4 with the turn-10 intake (this PR); slice 5 (policy first, then templates, then one real handoff test); slice 6 (gate re-target first so the base-anchored judge accepts the read-order change — the session-13 PR #6 pattern — then the supersession with the cold-start proof run BEFORE the canonical read order changes on `main`). Replication kit and close last.
- **Wall discipline honored:** the workflow file is untouched all session; the verifier changes (PR #12 re-target, PR #13 new guard) are gate REPAIR/construction under the owner's slice-6 directive — each its own PR with evidence, strengthening (never weakening) a guard; the PR template's first live use is this session's PRs (closing a standing "not checked" item from record 13).

## 3. Slice 4 — the STATE contract (PR #10, merged `7ec4c89`; CI run `38521337785` both jobs green; post-merge run `38521445871` green)

- **Audit (not a rebuild — the owner's explicit instruction):** STATE v1 (session 11, D-024) already carried phase / active task / next action / open questions / verification state. Defects found by the §1-field audit: (a) "verified" was one adjective covering three different things (run / observed / behavioral) with no `proposed` or `not checked` labels — the exact imprecision the owner named; (b) **QD-1 was missing from the open-question list** (EXECUTION §6 carried it; STATE didn't — a dependencies-completeness defect, the INT-101 class); (c) PR status was presented without the snapshot-not-live disclaimer (INT-104); (d) active task and exact next action were one blurred line (INT-102).
- **Landed:** the five-area contract (position / work / dependencies / evidence / coordination); ALL seven open owner questions (Q1 remainder, Q2, Q3, QD-1, D-014, F-06, Q-IDENT) each with blocks-only scope + authoritative home; the five evidence labels each with ONE direct pointer (INT-103); snapshot semantics; active-task ≠ exact-next-action as two lines. Turn-10 intake landed with it: INT-100..109, D-027, manifest turn-10 row + E-2 extension, ledger audit note 6, PLAN layer-1.2 amendment, GLOSSARY four terms.
- **Verified on the tree:** VER-701 (bold fields), VER-702 (pointer resolves), VER-804 (pointer = highest record = 14) all PASS; verifier 46/0, self-test 20/20, isolation green on the PR head (§8).
- **Deliberately staged:** STATE's how-to-use line still points at the CURRENT (ledger-first) read order; it flips in slice 6's PR #13 with the boot supersession — avoiding a mid-session STATE↔AGENTS inconsistency (the record-13 VER-804 transient was the precedent for not creating another).

## 4. Slice 5 — session handoffs (PR #11)

- **Policy conflict resolved FIRST (as the owner ordered):** the single-tier rule ("EVERY meaningful session leaves a numbered record" — INT-072 broadened per F-04) is superseded BY REFERENCE by the two-tier event-typed policy (D-027(2), INT-106): meaningful → compact worklog entry (100–250 words); substantial → numbered record. The supersession note lives in OPERATING-MODEL §3; INT-072 stays as history.
- **Forms standardized:** `context/TEMPLATES.md` (NEW — reference-tier forms, never policy): the compact worklog entry, the numbered session record (12 mandatory fields), the STATE five-area form, the cold-start proof protocol, the AGENTS entry-map skeleton (the replication seed). Folded into EXECUTION §1 (one row) and context/README.
- **The proof — one handoff from a real completed session (record 13), uncoached fresh-context GLM sub-agent, read-restricted to record 13 + STATE.md only:**
  - **Task/completion extracted correctly** with section-level citations (§1, §3, §6, §10).
  - **Open items exact:** Q1 remainder (blocks only bridge instantiation), F-06, Q-IDENT (default (a)), Q2/Q3/D-014 (gated), plus the not-verified list (one-shot, per-host bridges, PR-template first live use, MUT-17 coverage) and the P-18 deferrals.
  - **Authority handling under staleness:** the agent found record 13 §9's handoff ("Phase 2 planning") STALE relative to STATE (owner turn 10: layer 1.2 first) and correctly let STATE supersede the record — and correctly refused to treat the gating PR status as knowable from committed files (INT-104). This is the drift-handling the whole system is built for, exercised on a real record.
  - **Evidence extraction:** seven concrete items with exact identifiers (PR #6 `fdeeebe`, PR #8 `8019d70`, red run `115684453018`, merge-block 405, protection JSON, verifier 46/0 + 20/20, behavioral proofs).
  - **First command:** `python3 tools/verify_canonical_layer.py` — citing "trust runs, not recollection" (P-02/LAW-01). Correct.
  - **Read scope:** exactly the two permitted files; no raw corpus, no unrelated history. The record form carried the whole handoff.
  - **Verdict: PASS** — the agent could report and direct itself correctly from the record + index alone; it identified precisely which additional source (record 14, in progress) the live continuation lives in — the pointer chain working as designed.
- **4.1. The proof's defect find (the owner's "defect found, no changes" class — durable record, then repair):** record 13 §10's close evidence is incomplete: **PR #9's merge SHA (`e8a8259`) and post-merge run (`38514278918`) were never recorded**, and "final state of `main` at session close: `8019d70`" described the PR-#8 corpus, not the post-#9 tree — a self-referential ambiguity a fresh agent cannot resolve from the record. **Disposition: repaired by append-only addendum to record 13 §10 (this PR); regression guard = the standardized form's §12 "Session close" field — merge SHAs + post-merge CI run IDs for EVERY PR, the close PR included — which record 14 itself now follows.**
- **4.2. Compact worklog form's first use:** the in-repo WORKLOG Task 13 entry at this session's close (PR #15) is written to the new compact template (target 100–250 words) — the form's live exercise.

## 5. Slice 6, step 1 — the gate re-target (PR #12)

- **The landmine (found by pre-implementation reasoning, the MUT-17 class):** the required `canonical-layer` job runs MAIN's verifier — including its SELF-TEST — over every PR head. MUT-08 (the boot-sequence guard) mutates a hard-coded ledger-first step-1 string in AGENTS.md. PR #13 moves the ledger OFF step 1 (the supersession); on that head, main's MUT-08 string would stop matching, the mutation would silently no-op, and the self-test would report a blind guard — RED-blocking the exact PR the owner's slice 6 authorizes. The repo's own gate blocking its own legitimate next change.
- **The repair (the session-13 PR #6 pattern):** MUT-08 genericized — `_drop_ledger_step` removes whichever numbered read-order line names `/INTENT-LEDGER.md`, old order or selective order. VER-101 itself is unchanged (presence + before-NORTH-STAR holds in both orders); the guard's COVERAGE is what was repaired. The workflow file is untouched; the change strengthens a guard and lands as its own PR with evidence.
- **Two-sided proof (both CI jobs on this PR):** `canonical-layer` (main's pre-repair MUT-08 over this head — AGENTS unchanged here, the old string still applies) must stay green; `head-tools` (this head's new generic mutation) must stay green. After this merges, main's judge carries the generic form and PR #13 can change the read order. **Observed: run `38522398530` both jobs green; merged `15bae62`; post-merge run `38522484815` green.**

## 6. Slice 6, step 2 — the read-path supersession + the bounded cold-start proof (PR #13)

### 6.0 The protocol and rubric — FIXED BEFORE LAUNCH (D-027(4); form: `context/TEMPLATES.md` §4)

- **Task agent:** uncoached, fresh-context GLM sub-agent; given ONLY the repository path, the owner's question (a realistic task with two built-in challenges: notice an open dependency and what it blocks; distinguish an observed-live result from a not-checked claim), read-only constraints, the instruction to follow the repository's own startup instructions, and the requirement to produce (1) an answer with a source pointer per claim, (2) the ONE exact next action, (3) a read manifest (every file opened, in order, with approximate word counts and the total). No hints about which files to read; no conversation context.
- **Verifier:** SEPARATE fresh-context GLM sub-agent (did not write the docs, did not run the task); given the rubric + the task agent's full report + read-only repo access; grades each criterion, spot-checks pointers, cross-checks the manifest's word counts against the real files (`wc -w`); final verdict PASS/FAIL. The task agent never grades itself.
- **Rubric (weights fixed before launch):** factual correctness 40% · authority + unresolved-decision handling 25% (four states; recommendations/presence/elapsed time never approval; blocks-only-dependents scoping) · deterministic continuation 15% · evidence citations 10% · measured read scope 10%.
- **FAIL conditions (any one):** reads any `context/raw/` file; reads unrelated historical records (pre-session-13) without a task-specific reason; claims without pointers; treats proposed/observed as owner-approved; wrong phase or wrong next action.
- **Scope policy:** record the measured baseline (files + total words); the read-scope budget is SET FROM the baseline (defaultable default — the owner's open question 21 answered "baseline first" by non-objection; overridable at any touchpoint). The owner's principle: "the agent finds the relevant context without reading tens of thousands of unrelated words."
- **The owner's question given to the task agent:** "Before we begin Phase 2 product work: where exactly does the repo stand, is anything in the open owner decisions blocking the harness work, and can I trust that branch protection actually rejects a bad merge? Point me at the evidence."

### 6.1 The supersession corpus (this PR)

- `AGENTS.md` v2.6: the read order is now the owner's five-step selective path — this file → `/STATE.md` → worklog tail (last 3 compact entries) → `/INTENT-LEDGER.md` marked SELECTIVE (verify the entries behind the task and any CONSEQUENTIAL change; it remains the ONLY intent path; blanket boot reading superseded, INT-107/D-027(3)) → `/NORTH-STAR.md` + `/EXECUTION.md`-mapped task-relevant sources only → reference tier on demand. The ambiguity rule lands too ("report the ambiguity — never compensate by reading the whole repository").
- `EXECUTION.md` §2: the intent rule rewritten as selective verification (the supersession reconciled canonically — never an implicit exception; LOOP-05 unchanged).
- `OPERATING-MODEL.md` §7: the cold-start protocol rewritten to the selective path; invariant 1's parenthetical synced; §9: the cold-start resumption test added as the third standing behavioral proof (rerun triggers: entry point / read order / STATE schema / worklog protocol / authority structure changes + phase gates — never every doc edit).
- `STATE.md`: the how-to-use line now states the supersession; position lines updated to the true mid-session state (slices 4–5 merged with SHAs; slice 6 in progress).
- `GLOSSARY.md`: +Selective intent verification, +Read manifest.
- Verifier: **VER-110** (the supersession guard: the ledger step must carry the SELECTIVE marker AND the worklog tail must be an early numbered boot step) + **MUT-21** (regress to blanket ledger-first boot — content-generic) + **MUT-22** (drop the worklog-tail boot step — content-generic). 47 checks / 22 mutations. Both mutations generic by construction (the MUT-08 lesson applied prospectively).
- The canonical read order on `main` changes only when this PR merges — AFTER the proof below passes on this branch (the owner's rule: "Update the canonical read order only after the behavior is proven").

### 6.2 The proof run (task agent) — RUN 2026-10-14, COMPLETE

- **Agent:** uncoached fresh-context GLM sub-agent (no chat history, no hints — given ONLY the repository path, the owner's question verbatim, read-only constraints, "follow the repository's own startup instructions", and the three deliverables). It followed the branch's new selective read order on its own (AGENTS v2.6 → STATE → worklog tail → record 14 → selective ledger → task-relevant canonical docs) and recognized its own task as the in-flight proof STATE names — the true mid-session position, not a circular dodge.
- **Q1 (where the repo stands) — correct, pointered:** Phase 1, layer 1.2 in execution, session 14 mid-slice-6; PRs #10 `7ec4c89` / #11 `e08af51` / #12 `15bae62` merged; HEAD `7ab512c` one commit ahead, unpushed (verified itself: `git log origin/main..HEAD`, `git ls-remote`, `git status -sb`); PR #13 not yet opened — cross-checked against the §6.2–§6.4 placeholders; Phase 2 NOT started, gated on the owner-approved execution plan (INT-100). It also RAN the verifier itself: **47/0, exit 0**.
- **Q2 (what blocks the harness) — challenge met:** NO open item blocks the harness; an 8-row blocks-only table (Q1 remainder / Q2 / Q3 / QD-1 / D-014 / F-06 / Q-IDENT + record 13 §9 line 154 corroboration), every row pointered to STATE / DECISIONS / EXECUTION §6. The actual gates named correctly: session-14 close + the owner-approved Phase 2 plan — the open dependency noticed and scoped, not averaged away.
- **Q3 (branch protection) — observed vs not-checked distinguished:** both prohibited routes cited to their observed-live evidence (direct-push rejection — record 13 §5.2 Route 1; probe PR #7 red run `115684453018` + merge-block 405 — Route 2); the base-anchored judge mechanism inspected in `verify.yml` directly; two honest caveats raised unprompted — snapshot-not-live (INT-104) and the Q-IDENT attribution boundary ("a green-but-unauthorized merge is not mechanically rejected").
- **Staleness handled by the book:** record 13 §9 ("Phase 2 planning begins") recognized as stale vs STATE/INT-100 → STATE governs; WORKLOG tail lagging at Task 12 mid-session → followed STATE's fresher record pointer — the slice-5 proof's exact behavior, now reproduced by a second uncoached agent.
- **Defect found, no changes (the owner's class):** `verify.yml`'s step label says "(46 checks: C1–C8)" while this branch's verifier runs 47 (VER-110 added in `7ab512c`) — cosmetic; the workflow was deliberately untouched this session (wall discipline, §2). Disposition: fold into the next workflow-touching PR (P-18 deferral, recorded here; the step name is not the check — the run is content-driven).
- **Read manifest (verbatim, in order):** AGENTS.md 1,384 (full) · STATE.md 864 (full) · WORKLOG tail 1,354 (lines 230–287, last 3 entries) · record 14 2,194 (§1 + §2–§6) · record 13 1,437 (§5–§10 — the protection-evidence home STATE points to) · DECISIONS.md 2,381 (full) · PLAN.md 1,214 (full) · EXECUTION.md 2,485 (full) · INTENT-LEDGER 1,359 (selective: turn-10 block + INT-097) · verify.yml 303 (full). **Total ≈ 14,975 words, 10 files.** No `context/raw/` file; no pre-session-13 record; GLOSSARY/LAWS/ENGINEERING/PRINCIPLES/OPERATING-MODEL/NORTH-STAR deliberately unopened (INT-107). One command run: the verifier itself (green).

### 6.3 Independent grading (verifier agent) — RUN 2026-10-14, COMPLETE

- **Agent:** SEPARATE uncoached fresh-context GLM sub-agent — did not write the docs, did not run the task; given the rubric + the task agent's full report + read-only repo access. It re-read the sources, reproduced the git state, re-ran the verifier (**47/0**) AND the self-test (**22/22**, temp-dir-based, repo untouched), and `wc -w`'d every manifest entry and every cited line range.
- **Grades (weights fixed before launch):** factual correctness 97 × 0.40 · authority + unresolved-decision handling 97 × 0.25 · deterministic continuation 98 × 0.15 · evidence citations 94 × 0.10 · measured read scope 96 × 0.10 → **weighted 96.8/100**.
- **Pointer spot-checks: 28/28 resolved** (27 exact; 1 lands on substantively equivalent content — the "cannot weaken its own judge" wording lives at EXECUTION §7 / GLOSSARY / D-025 while `verify.yml` states the same idea in different words, and EXECUTION §7 was cited in the same bullet).
- **Word-count cross-check: every entry EXACT (0% deviation); total 14,975 exact.**
- **Fail conditions: 5/5 PASS** — no `context/raw/` read; no unrelated pre-13 history (record 13 §5–§10 is the evidence home STATE itself points to); no pointerless claims; nothing proposed/observed upgraded to owner-approved; phase and next action both correct.
- **Grading findings (all non-blocking):** (a) the verify.yml label lag — confirmed real, minor (§6.2 disposition stands); (b) the one equivalent-content pointer (trivial); (c) run-output size estimated "~600 words" vs 835 actual — informational, correctly excluded from read scope; (d) ledger read 9th rather than at the step-4 position — defensible under INT-107 for a read-only task, honestly manifest; (e) the task agent declined `--self-test` out of write-caution — over-conservative but honest, and the grader reproduced 22/22 itself; (f) the four decision states applied flawlessly though never explicitly enumerated.
- **VERDICT: PASS (96.8/100, zero fail conditions tripped).** The task agent never graded itself; the grader never ran the task.

### 6.4 Scope baseline + budget — MEASURED 2026-10-14

- **Baseline (§6.2's manifest, cross-checked exact in §6.3): 10 files / 14,975 words** + one verifier run. Against the raw corpus (`wc -w context/raw/*` = **75,735 words**, deliberately unread) the cold start read **≈20% of the corpus wordage** — the owner's principle ("the agent finds the relevant context without reading tens of thousands of unrelated words") is met with margin.
- **Budget SET FROM the baseline (defaultable default — §6.0 scope policy; overridable at any touchpoint):** future cold-start proofs stay **≤ 12 files / ≤ 18,000 words (baseline + 20% headroom)**, never any `context/raw/` file, historical records only with a task-specific reason. Breaching the budget is a finding, not an automatic FAIL — the rubric's read-scope weight (10%) and the fail conditions carry the hard lines.
- **Rerun triggers (TEMPLATES §4, OPERATING-MODEL §9):** entry point, read order, STATE schema, worklog/session-record protocol, or authority-structure changes; phase gates — never every documentation edit.

### 6.5 PR #13 merge evidence (recorded in the next PR per the record-13 §10 addendum pattern)

- **Observed:** CI run `38531302130` on PR #13 head `3c2f94b` — both jobs green (`canonical-layer` success, `head-tools` success); **merged `87e5cf0`**; **post-merge run on `main` `38531369782` success @ `87e5cf0`** (re-observed via API this session). The selective read order is now canonical on `main`; VER-110 + MUT-21/22 live on main's judge from this merge.
- The merge carried the proof's outcome with it (commit message cites record 14 §6.2–§6.4). The record-13 "not verified" item "the PR template's first live use" closes with this session's PR set (#10–#13 observed using it; #14/#15 follow).

## 7. The replication kit (PR #14)

- **Scope (D-027(5), INT-108 verbatim):** "`context/TEMPLATES.md` (the portable forms) + `context/REPLICATION-GUIDE.md` (instantiation steps for other projects); the pattern layer travels, Arivo content stays."
- **Landed:** `context/REPLICATION-GUIDE.md` (NEW) — the seam table (mechanisms + contracts travel; INT/D/Q/VER IDs, raw corpus, phase plan, product vocabulary, Arivo history stay), the seven-pattern inventory (entry map · intent ledger · decision register · STATE · session memory · verifier+walls · proofs, each with its seed contract and TEMPLATES form pointer), the **eight instantiation steps each with a done-when** (scaffold entry map → ledger → decision register → STATE → worklog+first record → minimal verifier with self-test → walls with both rejection routes probed → the first cold-start proof), the adaptation seams (language, canon naming, model family, session cadence, extra gates, verifier growth), and the replication proof: **a copy is proven only when its own cold-start proof passes — files existing is not replication** (the kit's acceptance criterion is behavioral, matching the owner's "take care").
- **Seam rule (the owner's INT-108 made testable):** nothing in the system's mechanics may hardcode this repo as the only possible home — any mechanism that only works here is a defect in the mechanism.
- **Companion folds:** GLOSSARY +Pattern layer (the portable half vs content; homes: TEMPLATES + the guide); EXECUTION §1 +Replication guide row (a guide, never a second specification); context/README structure line + tools count synced 46/20 → 47/22 (VER-110/MUT-21/22, PR #13 `87e5cf0`) — the README lag was the same class as the grader's verify.yml label finding; the workflow label itself stays a P-18 deferral to the next workflow-touching PR (§6.2 disposition; the step name is not the check).
- **Verified on the tree:** verifier 47/0 + self-test 22/22 + isolation green on this branch head before the PR (§8 at close).
