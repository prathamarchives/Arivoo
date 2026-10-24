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


## 6. SYSTEMS-ENGINEERING VERIFICATION RECORD (LAW-30; enforced after H-02)

The governing policy lives in OPERATING-MODEL.md §2/§9 and LAWS.md LAW-30. This is the standard record form, not a second policy source. The record is authored by a fresh-context Systems Engineering Verifier after implementation and independent test verification. It is bound to the reviewed diff using the H-02 digest procedure; do not bind it to a commit hash that changes when the record is added.

Required fields (JSON, standard library only):

    {
      "schema_version": 1,
      "slice_id": "<slice>",
      "base_sha": "<base revision>",
      "reviewed_diff_sha256": "<digest excluding this report and generated proof output>",
      "intent_ids": ["INT-..."],
      "requirement_ids": ["SYS-..."],
      "system_claims": ["C1"],
      "changed_components": ["<paths/components>"],
      "interfaces_reviewed": ["<contract + evidence pointer>"],
      "v_model": {
        "component_verification": ["<requirement + test/proof ID>"],
        "integration_verification": ["<real boundary + proof ID>"],
        "system_verification": ["<system requirement + proof ID>"],
        "validation": ["<user scenario + expected outcome>"]
      },
      "failure_modes": [
        {"id": "FM-...", "scenario": "...", "control": "...", "proof_ids": ["..."]}
      ],
      "findings": [
        {"id": "SEV-...", "severity": "P0|P1|P2", "status": "open|resolved|owner-accepted-debt",
         "evidence": "...", "disposition": "..."}
      ],
      "not_verified": ["<explicit limitation>"],
      "builder_context": "<builder-session identifier>",
      "reviewer_context": "<fresh, separate context identifier>",
      "disposition": "PASS|BLOCKED",
      "review_summary": "<traceability conclusion; no unsupported claims>",
      "sheet_section": true
    }

Rules:
- After H-02, a missing, stale, incomplete, malformed, or BLOCKED report fails the gate.
- An unresolved P0/P1 or blocking owner question fails the slice. P2 debt requires an explicit owner-approved record and revisit condition.
- The report cannot close Q6–Q11, change a law, or promote a proposal to adopted status.
- A reviewer-context identifier does not cryptographically prove independence. Fresh-context execution and a separate grader remain part of the protocol; state the identity limitation honestly.
- The Proof Sheet records report and reviewed-diff digests, disposition, findings, and not-verified items. Generated evidence is never hand-edited.
- **The optional `sheet_section` field (CLAIM-042, boolean, typed — a non-bool value is a named ARV-SEV-002 refusal) is the Proof-Sheet SEV section's OPT-IN transition switch.** The section renders in the committed sheet ONLY when the report sets `sheet_section: true`; absent or false keeps the sheet byte-identical to the base format. Rationale (the cannot-flip-in-the-same-PR rule): the trusted gate re-derives a candidate's committed sheet with the PR's own BASE machinery, so a section may appear in a committed sheet only once the base renders it (observed live: the #76 trusted job's ARV-PRF-004). The FIRST section-bearing sheet is the first slice whose merged base carries the renderer (CLAIM-042's successor); slices landing the section earlier set `sheet_section: false` with the transition stated in their own not-verified list. **Post-transition expectation (the named follow-up, PLAN H-02):** once the first section-bearing sheet has merged, a base-side mechanical expectation — a gate/validator rule requiring `sheet_section: true` for slices whose base carries the renderer — lands as its own bounded slice, RED-first; until then the obligation itself is enforced by the gate on the committed sev.json regardless of the switch (the section is the RECORD in the sheet, never the enforcement).
