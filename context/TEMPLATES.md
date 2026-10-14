# TEMPLATES — The Standardized Forms (Session/Memory/State/Proof/Entry-Map)

> **STATUS: ACTIVE FORMS (D-027(2)/(5), 2026-10-14).** The standardized FORMS this repo writes to — and the portable forms for replicating this system into a new project (INT-108; steps: `context/REPLICATION-GUIDE.md`). Forms, never a second specification: the POLICY homes are `/OPERATING-MODEL.md` §3 (session records), `/GLOSSARY.md` (STATE contract, Evidence labels, Meaningful session, Substantial work), and `/EXECUTION.md` §1 (the contract map). Reference-tier control artifact per D-022 — it never outranks a root document. Historical process artifact class: analysis never authority.

## 1. WORKLOG ENTRY (compact form — every meaningful session; soft target 100–250 words)

```markdown
---
Task ID: <N>
Agent: <name (role)>
Task: <one line — the request + intent refs (INT-…/D-…)>

Work Log:
- <only outcome-relevant steps, evidence-typed>

Stage Summary:
- Outcome: <what changed / what was found>
- Evidence: <one line: command + exit code, or link>
- Pointer: <numbered session record / PR>
- Unresolved: <open items, one line>
- Next: <one deterministic action>
```

The worklog answers "what happened recently, and where should I go next?" — the numbered record answers "what exactly happened, with what evidence, and what remains unresolved?" Detail lives in the record; the entry points at it.

## 2. SESSION RECORD (numbered form — substantial work; ALL fields mandatory, "none" is an honest answer)

File: `context/extracted/NN-<NAME>.md`

```markdown
# NN — <NAME>
> STATUS: SESSION ENGINEERING RECORD (date; the session's intent refs; D refs). Historical
> process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task <N>.
> PRs this session: <numbers + dispositions>.

## 1. What the owner asked (verbatim — owner turn <N>, <date>)
> <the owner's turn, verbatim, typos preserved — the E-2 cross-check for INT- entries>

## 2. Starting state
- commit / branch / working tree clean?; when work crossed a PR: base, head, merged revision
- preflight runs (command + exit code + result) before any edit

## 3. Task and scope
- the requested work · bounded scope · intent/decision references · non-scope

## 4. Results
- what changed, what did not, and why (per bounded scope)

## 5. Files changed
- exact paths + relevant IDs (INT/D/P/FAIL/VER)

## 6. Commands and external actions (ACTUAL — never reconstructed)
- local verification: <command> @ <revision> → exit <code> → <material result>
- tool/API-only: <exact operation, target, result or link>; "no shell command ran" when true
- large raw output: linked, not inlined

## 7. Evidence
- tests · CI runs (run IDs) · PRs (numbers + SHAs) · observations + outcomes

## 8. Failures
- failed attempts · found defects · dispositions · regression guards added

## 9. Unverified items
- what was not run, not observed, or could not be established (non-empty honesty, LAW-04)

## 10. Open decisions
- owner decisions/dependencies still unresolved (each blocks only what it names)

## 11. Next action
- ONE deterministic continuation point ("tests passed" is not a handoff without which
  tests, which revision, what result; "done" is not a status while a proof or owner
  decision is missing)

## 12. Session close
- merge SHAs · post-merge CI run IDs · final tree state
```

## 3. STATE.md (the five-area current-position index — one screen, pointers not detail)

```markdown
# STATE — Current-State and Navigation Index
> STATUS: navigation snapshot — NOT authority … contract (D-027/INT-109/105): one screen,
> pointers not detail, never a second ledger/plan/architecture copy; long-term repo memory
> (INT-101); PR/review section = snapshot at last update, never live status (INT-104).

- **Phase:** <phase + layer + operating model + whether the next phase is planned/approved/started>
- **Active task:** <what the current/last agent is doing, failed at, or left unfinished (≠ next action, INT-102)>
- **Last completed:** <session N — record pointer>
- **Exact next action:** <ONE deterministic continuation point>
- **Blocking open questions — EVERY unresolved owner question, repo-wide (INT-101):**
  <each with blocks-only scope + authoritative home>
- **Outstanding reviews (snapshot at last update — NOT live, INT-104):** <or "none pending as of …">
- **Verification state (label + ONE direct pointer per claim, INT-103):**
  - verified by run: <command/CI job + result + evidence ref>
  - observed live: <external action/API response + link>
  - behaviorally tested: <scenario + test record>
  - proposed: <not yet adopted/approved>
  - not checked: <explicitly not verified>
```

## 4. COLD-START PROOF (the bounded test — rubric fixed BEFORE launch; D-027(4))

```markdown
## Cold-start proof record
- Task agent: fresh context, NO chat history, NO hints — given ONLY the repository path and a
  realistic task; read-only. Instructed to follow the repository's own instructions.
- Task shape: resume the current position (phase, active task, exact next action, relevant
  open decisions, latest evidence, unverified items) + a challenge requiring it to (a) notice
  an open dependency and name what it blocks, (b) distinguish an observed result from an
  unverified claim. Output: the answer with source pointers + the continuation + a READ
  MANIFEST (every file opened, approximate word count, total).
- Verifier: SEPARATE fresh context; given the rubric + the task agent's report + read-only
  repo access; grades, flags unsupported claims; final PASS/FAIL. The task agent never grades
  itself.
- Rubric (weights fixed before launch): factual correctness 40% · authority + unresolved-
  decision handling 25% (four states; recommendations/elapsed time never approval) ·
  deterministic continuation 15% · evidence citations 10% · measured read scope 10%.
- FAIL conditions: reading context/raw/ or unrelated historical records without a
  task-specific reason; claims without pointers; treating proposed/observed as owner-approved.
- Scope: record the measured total (files + words); set the budget from the baseline.
- Rerun triggers: entry point, read order, STATE schema, worklog/session-record protocol, or
  authority-structure changes; phase gates. Never on every documentation edit.
```

## 5. AGENTS.md SKELETON (entry-map form for a new project — the map, never a brain; ≤80 lines)

```markdown
# AGENTS.md — <project> — v1
## What this is
- Objective: <one line — the INT-… objective in the owner's words>
- <project> — <one line>; Repo: <name>; Owner: <handle>
- Phase: <current phase + what is live>
- Operating mode: <who runs, who reviews, how changes land>

## Read order (cold start — selective, position first)
1. `/AGENTS.md` (this file) — read fully
2. `/STATE.md` — where things stand NOW
3. worklog tail (last 3 entries) — what just happened
4. `/INTENT-LEDGER.md` — SELECTIVE: verify the entries behind your task and any
   consequential change (the ONLY intent authority — never blanket boot reading)
5. task-relevant canonical sources only (per the contract map)
6. reference tier — only when the task requires the underlying evidence

## Binding rules
- the repo is the memory (chat is not) · intent enters only through the ledger (verbatim)
- one fact, one home · append-only, supersede by reference, never rewrite
- change channel: findings recorded; changes applied only through reviewed branches
- laws are constraints WITH checks · do not weaken constraints, thresholds, or checks
- credentials never enter repo files, logs, or ledgers
- session exit: worklog entry + STATE refresh + (substantial work) numbered record
- verification runs on fresh-context subagents; language: <chosen canonical language>

## Vocabulary
See `/GLOSSARY.md`. Core: <the ~10 load-bearing terms>
```
