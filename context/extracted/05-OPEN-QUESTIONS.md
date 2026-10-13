# 05 — Open Questions for the Owner

Status: awaiting the owner's answers. Each is classified per the Question Record protocol. Defaults exist where marked; silence past the named gate = consent.

---

## UPDATE 2026-10-13 (owner turn 3.txt — verdict review + decisions)

Resolved by owner decisions and the owner-presented verdict:
- QA-1 → RESOLVED (D-001: "you run, i review")
- QB-1 → RESOLVED (D-002: product Arivo, repo Arivoo)
- QA-2 → SUPERSEDED by protocol: the verdict's phase order removes the Understanding-Session-first gate; cold-start proof moves to the Context Exam / phase discipline (revisit when the canonical spec is reconciled)
- QB-2 → ABSORBED into PLAN Phase 1 (W-01 walls; restricted required check + FACT entry)
- QB-3 → ABSORBED into PLAN Phase 1 (W-04 CI, Linux, owner-controlled)
- QB-4 → STANDS (arivo-owner stays owner-only, outside the repo; redacted isolation check replaces env dump — R-06)
- QC-1 / QC-2 → RESOLVED (D-003 / D-004 / D-008: Postgres + pgvector, local-first now, cloud sync on The List; Windows + WSL dev, Linux CI)
- QD-1 → OPEN (import format priority; non-blocking until capture slices)
- QD-2 → OPEN (agent journal-token scope day one; non-blocking)
- QD-3 → ABSORBED into PLAN Phase 5 (agent reads/API-MCP with D-019 surface)
- QE-2 → RESOLVED (owner set the reasoning order by directive; first layer built)
- QE-1 / QE-3 → OPEN (non-blocking calibration)

New owner questions (blocking for their named locks; defaults stand until overridden):

**Q1 — Host decision (blocks PLAN Phase 1 W-02 + builder setup).**
Which host is "Other"? Which is the primary builder for the first slices?
Default: primary builder = the orchestrator + its fresh-context subagents (predictable, whole-context); a verifier from a different model family (Claude Code or Codex CLI) once the host contract is verified; other hosts join by passing the host contract.

**Q2 — Purge vs backups (blocks storage/purge schema lock, PLAN Phase 3).**
What does purge mean for existing backups?
Default: immediate removal from live system + active derived stores; documented backup-expiry retention; purge ledger applied on restore so purged content never silently resurfaces. Per-owner encryption + key destruction only if physical erasure of every backup is required.

**Q3 — fact tag semantics (blocks vocabulary + Scribe/Planner rules).**
Does `fact` mean (a) "a statement intended to be factual, with evidence and verification status recorded separately" or (b) "a statement the system treats as verified true"?
Default: (a) — supports disagreement and uncertainty without losing the source claim. Note: the owner's original corpus wording points to (b); the architecture's later hardening (P-08: a fact tag classifies, never certifies) points to (a). The owner decides.

---

## A. Role and execution of THIS session (Blocking for repo start)

**QA-1. What is my exact role in the build?**
You designed: an execution agent that gets whole context in plan mode (INT-033), plus ME as the orchestrator of a multi-agent subagent system. Three possible shapes:
- (a) I run playbook Steps 0-2 myself (walls via gh, memory seeding with OWNER:/AI: labels, commit EXECUTION.md + AGENTS.md), you review each step — then I orchestrate subagent builders per slice from here.
- (b) You run the steps on your machine; I stay the reasoning/grading partner (the Understanding Session grader + context keeper).
- (c) Hybrid: I prepare everything (scripts, file contents, exact commands) and you paste/execute the owner-side actions that need your hands (signing key, protected settings).
Default: (a) — you already gave me repo access + plan mode, and INT-033 says the execution agent starts with whole context in plan mode. But the signing key and sealed tests must be yours alone either way.

**QA-2. The Understanding Session — who runs it, and against what?**
The playbook's Step 3 has the owner paste P1 to a fresh execution agent against the seeded archive/. Options:
- (a) A subagent of mine with a fresh context runs it against the seeded repo; I grade it against the Context Check (12 questions, 4 traps) and bring you the report + my grading.
- (b) You run it in your own host (Claude Code plan mode) as designed, and paste me the report to grade together.
Default: (a) first (cheapest, tests the system), (b) as the owner-side confirmation of the same.

## B. Repo and infrastructure (Blocking for Step 1-2)

**QB-1. Repo name spelling — Arivo vs Arivoo.**
The repo is `Arivoo`; every doc says `Arivo` (v1-v4 lineage). Which is canonical for the product name in docs/GLOSSARY? (Repo URL can stay Arivoo regardless.)
Default: `Arivo` in all docs (matches the full design lineage), repo slug unchanged.

**QB-2. GitHub walls — proceed with setup now?**
I can execute Step 1 with gh right now: protect main (PR + required `verify` check — note: the check doesn't exist until F-00 adds CI, so protection lands in two stages), no force push, rules apply to admins, CODEOWNERS on protected paths. Your token currently has full admin scopes.
- Should I create a separate restricted agent credential (push branches + open PRs only) so the full-scope PAT stays out of the agent path?
Default: yes — restricted credential for agent work; full PAT used only for owner-side actions (branch protection, CODEOWNERS, secrets), then kept out of day-to-day use.

**QB-3. Where does CI run?**
GitHub Actions on the private repo (included in private repos? — minutes billing applies), or self-hosted runner? The spec says remote CI is the authority. Default: GitHub Actions (ubuntu runner), `verify` workflow at F-00. FACT entry once tested — per LAW-02, I don't assume billing details from memory.

**QB-4. Owner folder — where do you keep `arivo-owner`?**
Playbook, exam keys, sealed tests, signing notes must never enter the agent repo or my workspace. On your machine only? Default: yes — I generate content for it (Context Check key, sealed exam set), you store it.

## C. Stack and deployment (Defaultable — locks at the Understanding Session / F-00)

**QC-1. TypeScript strict + Node LTS + PostgreSQL container + SQL migrations — confirm as the default the Understanding Session may challenge?**
Convo lineage mentioned Supabase early (RLS, cloud hosting, pgvector) and the new spec defaults to plain PostgreSQL in a container with RLS/Postgres-native features. Confirm: Supabase as deployment target later, or self-managed Postgres, or undecided-until-E-band?
Default: plain Postgres in container for the foundation (port-wrapped anyway); deployment target decided at the ops band (E24-era) via spike + FACT.

**QC-2. Local-first or cloud-first runtime?**
Earlier convos: desktop app (Electron as a client of the local service) + Supabase cloud sync. Later: hosted. The foundation builds the API core either way. Confirm the first deployment shape so F-slices don't assume. Default: API core built port-first; deployment shape deferred (it doesn't affect the foundation).

## D. Product scope confirmations (Non-blocking now; locks at their gates)

**QD-1. First import formats — exact priority?** Your day-one list: convos + research + books + articles + lists + X posts. Which convo export formats matter first (Claude/ChatGPT JSON? markdown?), and are the "books" EPUB or PDF-first? (E6-order input; PDF+math is the expensive one at E8.)
Default: MD + JSON convo exports and EPUB before PDF; PDF+math next.

**QD-2. Agent tokens day one — journal scope?** You answered Q5 "yes" (journal access from day one) for YOUR agents; D44 keeps third-party tokens per-scope. Confirm this two-population split stands. Default: stands.

**QD-3. MCP surface timing.** Agent-first by construction: thin MCP read adapter lands with the walking skeleton (E10-era / F-band equivalent in the new slice system). The two docs put MCP at the agent band. Confirm MCP-read ships in the foundation band or the next one — the docs currently imply "after foundation exit." Default: MCP-read v1 as the first post-foundation slice (F-10 candidate).

## E. Knowing you (calibration of the partnership — Non-blocking)

**QE-1. Your cadence: how much time per day/week do you plan to give this?** (Sets slice throughput expectations and how many decisions I batch per touchpoint.)

**QE-2. When you say "we reason through one by one" — preferred order?** My proposed order for the one-by-one sessions: (1) 00-PRINCIPLES + 02-OWNER-VOICE (goal alignment), (2) 03-ARIVO-CURRENT-STATE (the two docs, law by law), (3) the belief/autonomy architecture (archive material for later bands), (4) execution mechanics (slices, harness, walls). Confirm or reorder.

**QE-3. Anything in the corpus I should treat as superseded that the docs still carry?** (You are the final authority on intent status; AUT-03.)
