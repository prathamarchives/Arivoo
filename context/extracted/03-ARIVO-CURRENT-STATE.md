# 03 — Arivo Current State (the two Arivoo docs, distilled)

Source: Arivo Agent Execution Specification.md (v2, agent-facing, → docs/agent/EXECUTION.md), Arivo Build Playbook How You Run the Build.md (owner-facing, kept OUTSIDE the repo)
Date of docs: October 13, 2026 — same day the Arivoo repo was created (private, empty).

---

## The split (INT-034)

- **Playbook (owner)**: 13 steps from zero, break tests, drift-symptom table, 7 copy-paste prompts, Context Check key. Lives in `arivo-owner`, never in the agent repo.
- **Agent spec (agents)**: context brief, 29 laws, constraint ladder, kernel, verification loop, ratchet, foundation slices. Lives at `docs/agent/EXECUTION.md` in the repo.

## The goal (as encoded in both docs)

> "Arivo is a reading and study environment. The owner reads, writes, and thinks in it. Nothing the owner does is lost. Each new input adds value to old inputs. The owner's agents can use all of it."

**Claims**: C1 nothing is lost · C2 the agent has the owner's context · C3 old gains value from new · C4 concepts form with provenance and from tags · C5 each derived claim is explainable and reversible.

**Non-goals**: NG-01 no review queue (no stage waits for owner) · NG-02 no agent touches the database (API/MCP only) · NG-03 no generative model in Arivo's pipeline · NG-04 no detailed plan beyond the next phase · NG-05 no calculation engine (default, vetoable).

**Worst failure**: losing a highlight (INT-029).

## Architecture in brief (12 points from the spec)

1. Ground truth append-only (highlights, notes, journal revisions, bookmarks, tags, behavior events, source snapshots); edit = new revision; delete = tombstone.
2. Everything else derived + rebuildable, each row with provenance (run ID, versions, input hash).
3. Every write carries owner scope + actor; RLS enforces owner scope.
4. Client-generated UUIDv7; commands idempotent; acknowledged only after commit; one transaction writes item + revision + search text + outbox job + event.
5. Enrichment runs after capture in staged idempotent jobs — NOT in the foundation.
6. One API core; MCP adapter from the same command registry; scoped tokens; agent actor on every agent write.
7. Fact = fragment with `fact` tag; concept = entity; tag = append-only event; typed vocabulary v1 = {fact, concept}; free tags carry no meaning.
8. Fact tag classifies statement type, never certifies truth — truth lives in relations.
9. Owner-declared concepts are instant + authoritative; auto-detected stay provisional until evidence.
10. Keyword search at once (semantic later); every result carries a reason.
11. Concept page = the personal wiki page (label, gloss, aliases, evidence with provenance, linked fact fragments).
12. Belief aggregation / concept induction / Kev classifier exist in the archive — NOT built in the foundation.

## Memory + authority (the repo IS the memory)

- MEM-01: repo is the only memory; no chat history, no recall, no past session.
- MEM-02: lessons become, in order: constraint → test → FACT → document line.
- MEM-03: AGENTS.md ≤ 80 lines, a map.
- MEM-04: no skills/rules files in the foundation; non-encodable lessons → LESSONS.md with reason codes; owner reviews encodability every 10 slices.
- MEM-05: archive/ loaded ONLY in the Understanding Session or Scribe tasks.
- MEM-06: each fact lives in one file.

Authority ladder: owner words (Intent Ledger) > North Star > Laws > Decision Records > requirements.yaml > slice cards > agent judgment. AUT-02/03: entries carry status (active/clarified/superseded/historical); latest explicit decision governs; nothing is deleted or reworded.

**Actor classes** (resolves the builder-vs-runtime conflict): builder/verifier agents — fixtures only, test DB, no secrets; runtime agents — real data via API/MCP in granted scopes, never the DB; Arivo workers — owner scope of their job via kernel; owner — everything, holds the keys.

## The 29 laws (grouped)

- **Truth**: LAW-01 no result claim without harness proof file · LAW-02 no tool/model/library facts from memory (FACT ID or spike) · LAW-03 no file answers → Question Record · LAW-04 final report lists what was not verified.
- **Scope**: LAW-05 one slice = one behavior in size limits · LAW-06 only card-scope paths · LAW-07 protected paths owner-only · LAW-08 no dependency without approval note · LAW-09 never weaken a constraint (ratchet) · LAW-10 kernel is the only way.
- **Method**: LAW-11 commit each new test alone, see it fail for the stated reason (red record frozen) · LAW-12 real stack per behavior change · LAW-13 tests read state through paths the code under test doesn't control · LAW-14 passing `make fast` record on final commit · LAW-15 defect → failing reproduction before fix · LAW-16 stop after 3 failed cycles (Blocker Record) · LAW-17 no state outside the repo (resume from files) · LAW-18 after a failure, run the ratchet before the next slice.
- **Product**: LAW-19 evidence rows never change after commit (owner purge only) · LAW-20 derived rows carry provenance · LAW-21 every write = owner scope + actor · LAW-22 no cross-owner queries · LAW-23 commands atomic + idempotent + acknowledge after commit · LAW-24 no ambient time/randomness/IDs/network/env outside adapters · LAW-25 closed vocabularies from one schema source · LAW-26 runtime agents never reach the DB · LAW-27 no stage waits for owner · LAW-28 builder/verifier never read real owner data or secrets · LAW-29 no generative model in the pipeline.

**Proactive set** (build early because retrofit is brutal): LAW-07, 08, 19, 21, 22, 23, 24, 25, 28 + harness checks. Everything else via the ratchet after real failures. "Do not invent constraints for failures that have not happened."

**Constraint ladder**: C1 type system → C2 database → C3 lint/architecture → C4 executable test → C5 gate/CI → C6 document (last resort, needs reason code). LAD-01: choose the highest level that works. LAD-03: repeated mistake → move up a level.

## The kernel (ten primitives)

K1 Ids (branded UUIDv7, only IdGen makes them) · K2 Ports (Clock, IdGen, Random, BlobStore, Embedder, Kev, Notifier — each with fakes + contract tests) · K3 Scope (OwnerScope = owner + actor, every data function) · K4 Tx (withOwnerTx — the only transaction; RLS session values; pool not exported) · K5 Command (defineCommand — idempotency via client ID + payload hash, 409 on mismatch, one transaction, outbox row, event row, actor, acknowledge after commit) · K6 Evidence (insertFragment/appendRevision — no update/delete exists) · K7 Derived (writeDerived — run ID, versions, input hash required) · K8 Errors (Result + closed error-code registry → HTTP status + MCP error; no throw across boundaries) · K9 Vocab (schema/vocab → codegen types + DB constraints + docs; drift check) · K10 Registry (each command registered once; HTTP/CLI/MCP derive from it).

**Boundaries**: features import kernel+schema only; kernel imports nothing of features/adapters; only adapters/db imports the driver; adapters/http the HTTP framework; adapters/clock reads time; adapters/ids makes IDs; product code never imports harness; features never import each other (shared → kernel via kernel slice).

**Stack defaults (challengeable in the Understanding Session, not fixed)**: TypeScript strict (noUncheckedIndexedAccess, exactOptionalPropertyTypes) · Node LTS ESM · one pnpm workspace · PostgreSQL in container (pgvector later) · plain SQL forward-only migrations with checksums, types generated from live schema · one validation library at boundaries · one test runner + property + mutation tools · dependency-boundary lint + custom rules · TLA+ for named state machines · `make` as the entry surface. Pick each through a spike or FACT entry (LAW-02).

## The verification loop

Commands: make state (5s) / fast (≤60s) / red / real-run / falsify / prove / gate / verify (≤10min, CI authority) / known-bad / audit / new-slice / entropy.

Slice cycle: make state → understanding.yaml (zero unknowns) → tests committed alone + make red (fail for stated reason) → code in scope + make fast → make real-run (drive as user) → make falsify (fix failures, seeds) → make prove → make gate (exit 0) → PR, CI verify → after 3 failed cycles STOP (LAW-16) → after any failure, ratchet (LAW-18).

**Size limits**: one behavior; ≤8 source files, ≤400 source lines; ≤6 test files, ≤800 test lines, ≤200 fixture lines; ≤3 requirement IDs, 1 migration; context pack ≤12,000 tokens.

**Proof Sheet** (harness-built, never hand-edited): header (slice, commit, harness version, seeds), owner words, claims with proof IDs, real-run summary, must-reject results, independent state reads, fault/differential results, known-bad result, scope report, defaults used, not-verified list, open questions.

**Known-bad builds**: each constraint has a patch that must fail with its code; harness ones live from F-03; product ones activate when the behavior exists; a missed known-bad turns the harness red and stops all building.

**Verifier**: fresh context, didn't write the code, reads only card + proof sheet + diff, writes failing tests only, never edits product code; report is advisory — the gate decides.

**Walls**: main protected (PR + verify check required, no force push) · CODEOWNERS on protected paths · agent credential cannot change workflows or sign · phase gate = owner-signed tag verified by CI against gates/owner.pub · agent never holds the owner key · local verify is preflight, CI is authority.

**Exams**: Context Exam 25 questions, 90% pass, traps 100%, key outside repo · Agent Exam from MCP phase, fresh + sealed sets, 90%, critical classes (fabricated source reference, cross-owner exposure) 100%.

## Foundation slices F-00 → F-09

- **F-00** repo skeleton + walls: clean clone passes make verify; broken file fails it; CI runs verify; CODEOWNERS; lockfile approval check; devcontainer (no personal keys); AGENTS.md per Appendix A; S-01 (host loads AGENTS.md, sentinel + transcript) + S-02 (stack check: strict compile, container DB, one migration).
- **F-01** memory seed: INTENT-LEDGER.yaml (verbatim, OWNER: turns only — make audit-intent verifies quotes against archive); DECISIONS.yaml; NORTH-STAR.md; GLOSSARY.yaml; FACTS.yaml (S-01/S-02 results); constraints/register.yaml (LAW-01..29 with level/mechanism/status; enforced needs a known-bad); make state.
- **F-02** constraint toolchain: lint bans ambient effects (LAW-24), boundaries BND-01..08, swallowed errors, UPDATE/DELETE on evidence tables; every rule prints WHAT/FIX/REF + known-bad fixture.
- **F-03** harness core: run records (seed, commit, versions); make prove; gate runs SCOPE/SIZE/PROT/RED/SKIP/FAST/ratchet/open-questions; known-bad for scope breach, protected-path edit, skipped test, hand-written proof sheet, lowered threshold, missing red, test edited after red, unapproved dependency.
- **F-04** real database foundation: ephemeral Postgres container, deterministic reset; forward-only migrations with checksums (edit fails the gate); independentRead (separate connection/role); real-run script; mutation test on helpers.
- **F-05** kernel v0: K1-K4, K8; compile-fail tests (fragment ID ≠ revision ID; no data function without scope); pool not exported (BND-04 known-bad).
- **F-06** ground-truth schema v0: node, fragment, revision (hash chain), behavior_event, tag_event, outbox, event_log — all with owner_id + actor; RLS on; composite keys; triggers reject UPDATE/DELETE on revision/behavior_event/tag_event; vocab codegen + drift check; negative suite (one violating statement per invariant); two-owner test.
- **F-07** command framework: K5/K6/K10; replay N× = 1 item; same ID different body = 409; fault run kills at each crash point, restart = clean state; TLA+ capture+outbox model with seeded bug; known-bad: skip idempotency, success before commit, skip outbox.
- **F-08** golden path — capture a highlight: the first real behavior; one transaction (highlight, revision, anchors, search text, outbox, event, behavior event); keyword search finds it at once; tags attach at capture; real-run drives CLI; 1,000 kill trials lose zero; NG scans; owner runs 12 adversarial checks + reads the code ONCE; `git tag -s golden-path-1`.
- **F-09** scaffold + one-shot proof: make new-slice from golden path; resume test (new session finishes half-done slice from files); a fresh agent with AGENTS.md + card builds capture-note, passes gate on cycle 1, owner edits zero; second fresh agent does bookmark; deviations become ratchet entries; `foundation-1` tag.

**Foundation exit**: 100% known-bad catch · two one-shots in a row · Context Exam passes for two agents in fresh sessions · make fast ≤60s, verify ≤10min · every law enforced or planned with reason · owner signs `foundation-1` · corpus closed · no blocking questions.

## The owner's 13 steps (playbook)

0. **Desk**: pick daily agent; devcontainer/disposable VM (no home folder, SSH keys, cloud creds, password manager); two places — agent repo `arivo` + owner folder `arivo-owner` (playbook, exam keys, sealed tests, signing notes); install git/make/Node LTS/pnpm/Docker. Check: `ls ~`, `ssh-add -l`, `env` — nothing personal visible.
1. **Walls**: private repo; protect main (PR + verify check, no force push, applies to admins); agent credential (push branches + open PRs ONLY); signing key off the agent machine, pub at gates/owner.pub; one empty commit. Wall check (must all FAIL): push to main · force-push · change .github/workflows · merge with failing/missing verify.
2. **Memory**: archive/ with owner-words/ (every convo, each turn prefixed OWNER: or AI:, named by date), ai-docs/ (ALL earlier design docs including stale: Backend Hardening, Execution System v1, seed pack, verdicts, Q&A), reviews/, principles/ (the two posts); add docs/agent/EXECUTION.md + AGENTS.md; owner commits to main. Check: grep -c '^OWNER:' works; git status clean.
3. **Understanding Session** (plan mode, ~30 min owner time): paste P1; agent returns 9-section Understanding Report (mission, owner intent, decisions, contradictions, unverified facts, questions, foundation plan, stack+layout, risks). Owner grades: Context Check 11/12 with all 4 traps; 5 quotes verified inside OWNER: turns; must find known contradictions (stale Backend Hardening vs later decisions; two numbering schemes E-phases vs execution phases); honesty on unverified facts. On failure: fix the memory, not the agent — fresh session, re-run.
4. **Lock decisions + start foundation**: answer Blockings one line each; accept/change defaults; approve plan; approval mode that still asks before commands; agent runs F-00 then F-01. After F-01: read INTENT-LEDGER (every says/means — the most important read of the build); make state + make audit-intent; fifth wall check (CODEOWNERS change without review must fail).
5. **Verification loop first** (F-02..F-04): no product behavior until verify + known-bad work and the owner has watched them fail on purpose. Owner break tests: Date.now() in src/ → lint fails naming fix; edit harness/ → PROT; skip a test → SKIP; hand-edit proof sheet → PROOF; edit applied migration → fail; make known-bad → 100% catch.
6. **Kernel** (F-05..F-07): paste P2 + P7 (law demo). Owner checks: fragment ID where revision required = compile error; UPDATE revision in psql = rejected; query without scope = won't compile + lint catches workarounds; replay 50× = one row, same ID different body = 409; kill -9 mid-command, restart = no partial state.
7. **Golden path** (F-08): owner runs the 12 adversarial checks; reads the code ONCE (judges whether a copy would stay correct, not style); every nit → ratchet entry; sign golden-path-1.
8. **Scaffold + one-shot** (F-09): fresh sessions, no history, only AGENTS.md + card; measure first-cycle pass + zero owner edits; two one-shots = foundation done, sign foundation-1.
9. **The ratchet** (whenever anything is off): observe → record (P4) → choose level → known-bad FIRST → constrain → sweep → close. Two-strike rule: violated again → move up. Refactor to impossible on the second occurrence of a class.
10. **Session routine** (~10 min/slice): make state → next card → fresh session + P2 → wait (no mid-slice chat except Blockings) → read proof sheet (5 min) → 1-3 adversarial checks → optional Verifier (P3) → accept/merge or reject/ratchet → make state.
11. **Gates + signing**: git tag -s <gate>; CI verifies against gates/owner.pub; owner runs sealed tests locally, reads aggregate only.
12. **Hygiene** (every 10 slices): make entropy; read LESSONS.md (re-try encoding each); failure ledger by class; archive superseded; corpus stays closed.

## Where the build stands RIGHT NOW

- Repo `prathamarchives/Arivoo`: private, ZERO commits, branch main (2026-10-13).
- The two docs exist (in this workspace, not yet in any repo).
- The archive corpus exists in raw form (this workspace's context/raw/) — not yet labeled OWNER:/AI: or placed in archive/.
- Playbook position: BEFORE Step 0. The repo is empty; the walls, memory, and Understanding Session have not started.
- THIS session = the plan-mode whole-context transfer the owner designed (INT-033) + alignment + questions, before one-by-one reasoning and before the repo starts.
