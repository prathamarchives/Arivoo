# 09 — Architecture Review: The Agentic-Repo Stress Test

> STATUS: **SESSION ENGINEERING RECORD** (2026-10-13, stress-test session — INT-072). Historical process artifact per D-022: this is assistant analysis; it is NOT owner intent and outranks nothing. Owner words live only in `/INTENT-LEDGER.md` (INT-069..090 were added this session). Worklog entry: Task 8. Verifier: `tools/verify_canonical_layer.py` (run green at session end).

---

## 1. Mandate (the owner's words, this session)

> "read the repo ... push and give me a report of review it find the gaps to make the artitechture strong, maybe more goal aligned review and reason through the layer ... stress test if the repo is like that. and reason through with the goal of arivo. and my words. my judgement and typa person im and everything you got." (INT-076)

> "i should not give an agent context in the prompt it should read the repo and just know what to do ... and make it immposible to make them there own assumption." (INT-071)

> "doesnt matter how many agents work on it.. like whatever they do gets documented each session somwhere so the other agent can read it as in engineering doc." (INT-072)

> "ai extends what alreayd is in codebase like a garden so treat it like that." (INT-073)

> "and then test against if there are gates and ways for agents to drift away." (INT-074)

> "the test and verification all wil be done by glm based sub agents. so host agent would be glm ig for verification testing loops and iteration" (INT-070)

> "let it be custom tags. i manually write what kind of highlight it is if i want to... so no by deafualt concept/fact tag" (INT-069)

## 2. Method (what was actually done)

1. **Full re-read, before anything else** (INT-068 discipline held): all 11 root canonical files + `context/README.md` + `context/WORKLOG.md` + `2.txt` and `3.txt` in full.
2. **GLM-based subagents** (INT-070's operating model, executed): two extraction agents read the full wrapped corpus (`0.txt` ~1,905 wrapped lines, `1.txt` ~2,932) and returned every owner-voice statement with line references; one fresh-context stress-test agent performed the zero-context cold start (below).
3. **Verification**: all 18 new corpus quotes grep-verified against `context/raw/` before ledgering (one extraction typo corrected: "every decions", `1.txt:1462`); the verifier script run on the edited tree; the fresh agent's git observations re-checked against `git log`.
4. **Reconciliation**: every conflict the new intents created was annotated in its authoritative home (EXR-08; never silently averaged) — see §4.

## 3. The stress test: does a zero-context agent "just know"?

A GLM subagent received only the repo path and the instruction to follow `AGENTS.md`. It had no chat context, no summary, no hints. Results:

**What worked (with citations from its report).**
- The read order is real and load-bearing: INTENT-LEDGER first changed its understanding before opinions formed; all 12 operational questions were answerable from the root layer alone.
- Numbers reconcile: 29 laws, D-001..D-023, P-01..P-17, 50 statused intents (now 72), verifier 27/27 GREEN.
- Conflict-resolution demonstrably ran on this repo itself: D-004↔D-015 reconciled by D-020 with text preserved (AUT-03 discipline).
- It correctly refused to treat `context/raw/` as boot material, correctly answered the "what do you do with new owner chat words" question (verbatim → ledger → commit), and correctly identified LOOP-05, STOP conditions, and the no-code gate.

**Where the fresh agent had to guess (its drift report, condensed — full text in the session transcript):**
1. Read-order step 12 had no quantity, and two cold-start definitions disagreed (AGENTS.md step 12 vs OPERATING-MODEL §7's protocol). A literal agent could read ~75,735 words of raw corpus for zero authority gain — a ~3.7× cold-start cost decided by inference, not by rule.
2. **QD-1 was an orphan reference**: cited by NORTH-STAR, D-023, PLAN, and the ledger — defined only in a superseded brief (violates the repo's own "no orphan authority" invariant).
3. **The worklog tail — the freshest memory a cold agent gets — was factually stale**: it said the push of the canonicalization commit was PENDING and cited `758b7de`, a hash orphaned by an amend (the live commit was `feac373`; the push had since happened). A cold agent inherited a false operational fact.
4. AGENTS.md:3 claimed host bridges exist (present tense) — none exist; they are Phase 1 W-02 work.
5. End-of-session obligations were stated in ≥4 places; "what are the three things" was underdetermined.
6. Rule-ID families (LOOP/QST/STOP/KB/RED/PRF/RAT/WALL/...) had no row in the contract map; their full definitions live only in the Tier-0 raw spec.
7. "Supported hosts" in GLOSSARY did unearned work (no host has passed the Host Contract); "Super Z" and "v1" were undefined terms.
8. If handed a build card, it would still have 12 open questions (stack, card template, kernel K1–K10 home, directory layout, test DB, test framework...) — honest Model-0 state, correctly deferred to Phase 1/2, but worth recording as the measured distance between "memory complete" and "build ready".

**Cold-start cost (measured):** ~28,500 words read to become operational (steps 1–11 + the register). Roughly half the mandatory root read was not needed to operate — the read order optimizes for doctrine depth, not boot budget. The repo sets no token budget for cold start itself (invariant 8 budgets slice packs and AGENTS.md, but not the boot sequence).

**Verdict:** the zero-context property **holds** — every operational question was answerable, the ledger-first boot is genuinely protective — but the failure modes at the edges (findings 1–7) were exactly the drift class the ratchet exists for. All were repaired this session (§4); the protocol gaps became rules (AGENTS v2.2, OPERATING-MODEL §3/§7).

## 4. Findings register (G-01..G-14)

| ID | Finding | Evidence | Severity | Disposition |
|----|---------|----------|----------|-------------|
| G-01 | Read-order step 12 unquantified; two conflicting cold-start definitions | stress-test drift #1 | HIGH | **FIXED**: AGENTS v2.2 step 12 = reference tier (task-scoped, never boot); OPERATING-MODEL §7 protocol gains item 6; the two definitions now agree |
| G-02 | Worklog tail stale: "push PENDING" false; `758b7de` orphaned by amend | stress-test drift #3; git log | HIGH | **FIXED**: Task 8 worklog entry records the push (token provided this session; `feac373` → origin). Root cause: a session ended before its push — the exact P-15 failure mode; Phase 1 walls + CI close it mechanically |
| G-03 | QD-1 orphan reference into superseded history | stress-test drift #2; grep | MED | **FIXED**: QD-1 row added to EXECUTION.md §6 with default + lock gate |
| G-04 | AGENTS.md:3 present-tense claim of nonexistent host bridges | stress-test drift #4 | LOW | **FIXED**: future tense, W-02 reference |
| G-05 | New owner statements would silently contradict root docs if not reconciled (custom tags vs P-10/GLOSSARY/Q3; GLM vs Q1/VRF) | INT-069/070 vs pre-session files | HIGH | **FIXED**: P-10 MECHANISM, GLOSSARY, DECISIONS Q1/Q3, NORTH-STAR, EXECUTION §6 all annotated per EXR-08 (this session). Standing gap: owner-turn ingestion is still a manual protocol — see R-01 |
| G-06 | Rule-ID families absent from the contract map | stress-test drift #6 | MED | **FIXED**: EXECUTION.md §1 row + "restate meaning at every citation" rule |
| G-07 | No mechanical check for session-exit protocol (worklog append, intent capture, verify green) | P-15 is C6 prose today | MED | **PARTIAL**: AGENTS v2.2 binding rule mandates the verifier run on doc changes; full mechanics are Phase 2 (`make audit`). See R-02 |
| G-08 | Cold start has no token budget; ~28.5K words mandatory, ~76K if step 12 misread | stress-test cost analysis | MED | **PARTIAL**: G-01's fix removes the 76K trap; budget line for boot reads is R-03 |
| G-09 | Three phase vocabularies (AGENTS phase line / PLAN phases / OPERATING-MODEL models) mappable but inconsistently reportable | stress-test drift | LOW | **OPEN (accepted)**: mapping exists in PLAN §Growth-model mapping; one pointer could be added to AGENTS — cosmetic |
| G-10 | Builder-facing prerequisites unspecified (12 questions) | stress-test Q12 | INFO | **ACCEPTED**: correct NG-04 discipline — the slice card itself is the designed answer; these land in Phase 1 W-02 / Phase 2 |
| G-11 | "Supported hosts" unearned; "Super Z"/"v1" undefined | stress-test drift #7/8 | LOW | **FIXED**: GLOSSARY wording (Super Z defined; host = passed the contract; "v1" explained) |
| G-12 | PRESENTED-LOCKED tier could be mistaken for owner intent by a skimming agent (rank 4 vs owner words) | stress-test Q8 analysis | LOW | **MITIGATED**: status legend + EXR-02 already; AGENTS v2.2 now states the GLM fact as intent (INT-070), removing the biggest live example |
| G-13 | Remote/local divergence risk: `feac373` sat unpushed for an entire session; the only sync record was the (wrong) worklog tail | this session's git state | INFO | **EVIDENCE for W-01 priority**: walls + required CI checks close this mechanically; until then, session-exit rule (G-07 partial fix) is the guard |
| G-14 | Extraction agents initially returned one misquote ("every decios" for "every decions") | grep verification | LOW | **FIXED pre-ledger**: verbatim verification caught it — the process worked as designed (never ledger an unverified quote) |

## 5. The Intent Ledger (the owner's stated focus #1)

**Before this session** (as the owner saw it on GitHub): 50 entries — INT-019..034 (spec Appendix C), INT-035..046 (3.txt), INT-047..068 (backfill round 1). The owner's complaint: "it only includes few things that ive said recently with glm and only one file i can see most of the thing sonly from em theres so much data on context that should be get extracted... the full day of reasoninggg" — accurate: the full-day-of-reasoning corpus (0.txt/1.txt) contributed only ~10 entries, all via the AI-quoted Appendix C.

**After**: 72 entries. INT-069..076 (this session's owner turn, verbatim) + INT-077..090 (backfill round 2 — the full-day reasoning: division of labor, layer-1 experience, AI-reasoning-secondary, verify-don't-hold-back, the reconciliation method, docs-first, the smallest daily loop, compounding-by-artifacts, service-not-model-rival, agent-does-all-jobs + journal-day-one, pull-up-when-I-read-that, train-on-my-measurement, reject-slow-concepts, the compounding knowledge base). Every substantive owner-voice line in the corpus is now ledgered: the extraction agents mapped owner voice to exactly `0.txt:4/7/33/37/800/1258/1323` and `1.txt:1/27/106/280/437–451/1368/1462/1911/1973–1985`; all are covered.

**Discipline held (INT-075):** the ledger still contains ONLY owner words. The assistant's observations about the owner (§9) live here, in the review — not in the ledger. AI-proposal material was not promoted (AUT-04/EXR-02).

**Assessment:** the ledger is now the strongest file in the repo — 72 verbatim, statused, source-cited entries covering goal, workflow, epistemics, autonomy, sequencing, agent surface, measurement, and evolution. Its remaining weakness is structural, not content: append-only verification is grep-based (manual), and owner-turn ingestion depends on the orchestrator's discipline (R-01).

## 6. PLAN review (the owner's stated focus #2)

Goal-aligned: the five phases map 1:1 to the seven layers and to C1–C5; semantic stays in sequence (D-015/D-020); the product-first guard (P-17) is embedded; one-phase-deep (NG-04) held — Phase 2+ are titles with exits only. The slice loop is the unit inside phases; growth models are mapped.

Findings:
- **Q1's dependency chain is now shorter**: W-02 (host contract + bridges) depended on Q1; INT-070 answers the verification-family half. W-02 can now verify GLM-host instruction loading first, then the Codex/Claude bridges — no longer fully blocked.
- **Model 0's graduation predicate is the plan's real next gate**: "owner approves the execution plan and answers Q1–Q3". That approval is the single remaining owner action before Phase 1. The plan should be presented as a one-page Decision-Review artifact (minutes of owner time, P-13) — recommendation R-04.
- Phase vocabulary triple (G-09) is cosmetic.
- The phase-exit predicates are checkable but not yet machine-checked (correct — harness is Phase 2; verifier covers the Layer-0 slice).

## 7. OPERATING-MODEL review (the owner's stated focus #3)

- **Roles**: the matrix held under real multi-agent use — this session ran orchestrator + 3 GLM subagents (2 research/extraction, 1 fresh-context verifier/adversary). The subagents never wrote repo files; the orchestrator curated and committed. That is Model 0 as now amended (who-runs updated per INT-070).
- **Slice loop**: not exercised (no code) — correctly so. The loop's command surface is Phase 2 target state, honestly labeled.
- **Memory-update protocol**: the 8 invariants were exercised live this session — cold start never regressed (read order only gained clarity), no orphan authority survived (QD-1 fixed), no silent supersession (all conflicts annotated), memory deltas atomic with commits (this commit), corpus closed (no new root docs; EXECUTION §1 map extended instead).
- **Self-healing**: the drift-symptoms table predicted today's findings almost line by line ("a rule is being re-explained in chat repeatedly → it is not enforced"; "agents keep asking the same question → the answer has no authoritative home" — QD-1 exactly). The ratchet is not yet mechanical (no failures/ ledger — none of today's findings were product failures; they were document defects, repaired in-session per Model 0's healing mode).
- **Session documentation (INT-072)**: the worklog law existed but produced orchestrator-only entries; the "engineering doc per session" convention was missing. Now codified (§3, session engineering records; this file is #09, the first).
- **The garden test (INT-073)**: today's session is the first live demonstration — the repo only GREW: 22 new intents, 2 new contract-map rows, 1 new session record, 0 rewrites, 0 deletions, every change an extension of what already was. The garden machinery (append-only, supersession, ratchet, GC-at-Model-5) is specified; its first real pruning was today's finding repair.

## 8. Layer-by-layer goal alignment (reasoned against Arivo's goal)

The goal: a solid learning environment where everything compounds and nothing disappears; worst failure = losing a highlight; agents get all of the owner's context; concepts form and link; every derived claim explainable and reversible.

- **INTENT-LEDGER** → goal: direct, 72 verbatim anchors. Strongest layer. 
- **NORTH-STAR** → goal: direct compilation; C1–C5 testable; first workflow = the owner's own experience words (INT-078/083); import day-one; custom tagging note added. Aligned.
- **PRINCIPLES** → goal: 17 laws, each with mechanism/failure/growth; P-10 updated to INT-069. Aligned.
- **DECISIONS** → goal: 23 statused decisions; D-004↔D-015 conflict closed; Q1/Q3 annotations added. Aligned.
- **LAWS** → goal: 29 laws with checks and live-at phases; proactive set honest. Aligned. (All `planned` with reason codes — correct pre-code.)
- **ENGINEERING** → goal: the why, traced to transcripts. Aligned.
- **OPERATING-MODEL** → goal: growth models + memory protocol + self-healing. Aligned (amended today).
- **PLAN** → goal: phase order reconciled; product-first. Aligned.
- **EXECUTION** → goal: one authority map; now complete (rule families, session records, QD-1). Aligned.
- **GLOSSARY** → goal: vocabulary controlled; custom-tag semantics added; Super Z defined. Aligned.
- **AGENTS** → goal: the map stayed ≤80 lines (41); boot order now unambiguous. Aligned.
- **context/** → goal: archive immutable, briefs banner-marked, register live, session records begun. Aligned.

No layer drifted from the goal. The drift found today was *between* layers (cold-start definitions, orphan refs, staleness) — coordination defects, not goal defects.

## 9. The owner, observed (assistant analysis — deliberately NOT in the ledger, per INT-075)

- **Judgment style**: depth-demanding and allergy-to-vague ("we need depth and specifcations... not vauge or breif"); allergic to "later" (P-07) and to approval queues (P-06); wants agents to reason autonomously, then ask *targeted* questions for the owner's judgment (INT-081) — never to assume on the owner's behalf, and never to stall waiting.
- **Working mode**: the owner operates as editor-in-chief of multiple AI sources — pastes external doctrine (X posts, other AIs' reviews/specs) and demands adjudication ("reason through it 7 times", "reason harder"). The corpus's structure is: short owner turns, long AI responses, many pasted documents. The owner's leverage is judgment + context, not typing.
- **Trust model**: distrusts AI memory and training data (LAW-02's origin: "dont rely on your knowledge and training data, its outdated"); trusts verification machinery, evidence, and the repo over any agent's recollection; assigns roles ("act as a solid world class backend engineer", "as a world class verification engineer dont hold back").
- **Product sensibility**: compounding and durability above all (worst failure = losing a highlight); raw-thinking notes over sticky notes; journal as writing lab; personal-wikipedia concepts; privacy-conscious (narrow behavior scope D-010; purge D-011); future-proof (agent-native, VR/3D, sellable as a service agents invoke — not a model rival).
- **Measurement taste**: artifacts over KPIs (INT-084: concepts, notes, journal pages — "number wont tell its compounding").
- **Implication for the repo**: review artifacts must stay minutes-sized; every assumption must become a question or a rule (never a silent default); the owner's words must stay verbatim forever (typos are identity, not noise); and the assistant's observations about the owner belong in session records — never in the ledgers.

## 10. Recommendations (prioritized; none started without owner approval — Model 0)

- **R-01 — Owner-turn ingestion checklist** (closes G-05's standing gap): add to OPERATING-MODEL §3: on any owner turn, (1) verbatim → ledger entry; (2) conflict scan against affected homes; (3) annotations per EXR-08; (4) worklog + session record; (5) verifier green. Small doc slice, next session.
- **R-02 — Verifier extensions** (G-07): add checks — ledger entry count monotonic; worklog tail cites current HEAD; every root doc that cites INT-069/070 carries the reconciliation annotation. Layer-0 precursor of `make audit`.
- **R-03 — Cold-start budget** (G-08): one line in invariant 8: boot reads ≤ ~35K words; raw corpus excluded by default (already enforced by AGENTS step 12 wording).
- **R-04 — Phase 1 approval artifact** (P-13): a one-page Decision Review: Q1 remainder, Q2, Q3, plan approval — so Model 0 graduates in one owner touch.
- **R-05 — Walls first** (G-13 evidence): nothing in Phase 1 changes order; W-01 (protected main) directly prevents the unpushed-session class.

## 11. Not verified (LAW-04 discipline)

- The GitHub token's scope beyond clone/push was not tested.
- `engineering transcript.txt`, `upstream of engineering transcripts.txt`, and the raw spec were NOT re-read in full this session (read in full in Tasks 6–7; their content is carried by ENGINEERING.md/LAWS.md and the ledger; the extraction agents did not cover them — their owner-voice content is nil per prior extraction passes and the doctrine briefs).
- INT-088's "J2" context bracket and INT-086's question brackets are the extraction agents' context reconstructions, labeled as such in the entries.
- The stress-test agent's word-count measurements are its own counts (plausible; spot-consistent with `wc -w`).
- No verification was run that GitHub renders the pushed markdown as expected.
