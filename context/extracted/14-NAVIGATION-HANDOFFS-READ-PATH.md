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
