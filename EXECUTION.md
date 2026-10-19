# EXECUTION — The Execution Contract, Canonically

**What this file is.** The single canonical home of Arivoo's execution contract: which files constitute the contract, which sources exist and how they rank, how conflicts resolve, and how the contract changes. It is an **authority map** — it creates no new rules; it states where every kind of rule lives. No other file may define execution authority, and no parallel execution specification may be created (D-021). Every authority-order statement elsewhere in the repo points here.

**Provenance.** Created by the canonicalization slice, 2026-10-13, executing the owner-endorsed review (INT-068). It replaces the three divergent authority-order statements previously embedded in NORTH-STAR, ENGINEERING, and OPERATING-MODEL. The 12 spec deltas staged in `context/extracted/08-RECONCILIATION-BRIEF.md` are either folded into the root layer already or explicitly owner-gated (§6) — none waits on a further agent-side rewrite.

---

## 1. The execution contract — what it consists of

| Concern | Authoritative home | Holds |
|---------|--------------------|-------|
| The goal and claims | `/NORTH-STAR.md` | Mission in owner words; C1–C5; the seven-layer contract; non-goals |
| Owner intent | `/INTENT-LEDGER.md` | Owner words, verbatim, statused — the ONLY intent authority |
| Owner laws | `/PRINCIPLES.md` | P-01..P-18: WORDS / MEANING / MECHANISM / FAILURE MODE / GROWTH |
| Decisions | `/DECISIONS.md` | D-001..D-037, statused; open owner questions in §6 (D-014, Q6–Q11; Q1/Q2/Q3/QD-1/F-06/Q-IDENT closed 2026-10-14 → D-028..D-033) |
| Executable law | `/LAWS.md` | The 30 laws: statement, ladder level, check, live-at; LAD rules; proactive set |
| Doctrine | `/ENGINEERING.md` | Why the laws are what they are (transcript + upstream) |
| Roles, loop, growth, healing, verification | `/OPERATING-MODEL.md` | The slice loop; six operating models; memory-update protocol; self-healing; the verification stack |
| Phase sequence | `/PLAN.md` | One phase deep (NG-04); guardrails; Phase 1 detail |
| Vocabulary | `/GLOSSARY.md` | Term definitions — the definitional authority (§4) |
| Entry map | `/AGENTS.md` | Cold-start read order; binding rules (≤80 lines) |
| Current-state index | `/STATE.md` | Where things stand NOW: the five-area contract (D-027) — position, work (active task ≠ exact next action), dependencies (every unresolved owner question, repo-wide), evidence (label + one direct pointer per claim), coordination (snapshot at last update, never live). A navigation snapshot pointing at authority — never a second authority, ledger, or plan; canonical wins on conflict (D-024/D-027) |
| Coordination log | `context/WORKLOG.md` | Append-only task log (operational memory) |
| Session/memory forms | `context/TEMPLATES.md` | The standardized FORMS (compact worklog entry · numbered session record · STATE five-area · cold-start proof · AGENTS skeleton) — forms, never a second specification; policy homes: OPERATING-MODEL §3, GLOSSARY. Portable to new projects (INT-108; steps: `context/REPLICATION-GUIDE.md`) |
| Replication guide | `context/REPLICATION-GUIDE.md` | The instantiation steps for other projects (D-027(5), INT-108): what travels (the pattern layer + contracts) vs what stays (Arivo content), the seven-pattern inventory with seed contracts, the eight instantiation steps (each with a done-when), the adaptation seams, and the replication proof (a copy is proven only when its own cold-start proof passes). A guide pointing at forms and policy homes — never a second specification |
| Rule families (LOOP/QST/STOP/KB/RED/PRF/RAT/WALL/UNS/MEM/FX/AFA/KER/BND/AUT/LAD) | `context/raw/Arivo Agent Execution Specification.md` (Tier 0 — full definitions, immutable) + inline restatements at citation points in LAWS/OPERATING-MODEL | Stable rule IDs; root documents restate a family's meaning at every citation — a bare ID with no meaning inline is a defect |
| Session engineering records | `context/extracted/09+` (numbered session records) | Per-session self-contained engineering docs (INT-072): what was asked, what was done, evidence, what changed, what's open |
| Refinement debt | `context/extracted/07-ON-THE-LIST.md` | The refinement-debt register (D-020) — the one live mechanism in `extracted/` |
| Review artifacts | `context/reviews/` | Agent-authored reviews and protocol proposals — banner-marked review-only documents. They land on a branch via PR and merge only with the owner's explicit authorization; accepted rules fold into their canonical home, never stay a parallel authority (D-024) |
| Source-coverage control | `context/SOURCE-COVERAGE-MANIFEST.md` | The coverage map and immutability anchor for `context/raw/` (D-025, F-09): per-file classification, owner-voice→INT mapping, SHA-256 anchors, exception and exclusion registers. A control, never an intent authority |

**The rule:** each concern has exactly ONE authoritative home. Other files may summarize, but a summary must point at the authority and never become a second specification. Every duplicated fact creates a synchronization obligation — duplication is a defect to be paid down, not convenience.

## 2. Source tiers (what sources exist — and what they are NOT)

| Tier | Source | What it is |
|------|--------|-----------|
| 0 | `context/raw/` | The verbatim corpus **as received from the owner** — a MIXED archive: owner statements, AI analysis and proposals, pasted documents and reviews, repeated across files. Immutable (AUT-02). **Not owner-only material**: no sentence in `raw/` is an owner decision by virtue of being there. |
| 1 | `/INTENT-LEDGER.md` | Owner words, verbatim, with source and status. The only path by which owner intent becomes authority. |
| 2 | `/DECISIONS.md` | Explicit decisions, statused (LOCKED / PRESENTED-LOCKED / ADOPTED / OPEN). AI recommendations rank ADOPTED at most — challengeable, never silently requirements. |
| 3 | Root canonical documents | The derived authority layer (NORTH-STAR, PRINCIPLES, LAWS, ENGINEERING, OPERATING-MODEL, PLAN, GLOSSARY). |
| 4 | `context/extracted/` | Historical process artifacts — extraction and reasoning history, banner-marked. They never outrank root documents. Exception: `07-ON-THE-LIST.md` is the live register (D-020). |

**The intent rule (selective verification — D-027(3)/INT-107, 2026-10-14).** Owner intent enters this repo ONLY through INTENT-LEDGER entries — owner words, verbatim, statused. A raw-corpus sentence, an AI proposal, or an extracted-brief statement is NOT intent until it is a ledger entry or an adopted decision (LOOP-05: a requirement with no intent behind it fails the audit). A fresh agent verifies the intent entries RELEVANT to its task **before any consequential change**: the ledger is the highest authority, but blanket ledger-first BOOT reading is superseded by the owner's selective read path (AGENTS → STATE → worklog tail → task-relevant sources; INT-107) — knowing the task does not require all owner words; changing something consequential does require the owner words behind it. Every slice card / context pack still carries its INT- IDs and the owner quotes.

## 3. The authority order (conflict resolution)

| Rank | Source | Notes |
|------|--------|-------|
| 1 | Owner words — INTENT-LEDGER entries | Verbatim; the highest authority |
| 2 | NORTH-STAR | Owner words compiled; claims and layers derived from them |
| 3 | PRINCIPLES — the WORDS fields | Verbatim owner law text (MEANING/MECHANISM/GROWTH are labeled interpretation and rank with the derived layer) |
| 4 | DECISIONS — LOCKED and PRESENTED-LOCKED entries | Owner-ratified decisions |
| 5 | LAWS | Derived executable law book — must trace upward (update invariant 3) |
| 6 | ENGINEERING | Doctrine (the why) |
| 7 | OPERATING-MODEL | Execution-contract detail |
| 8 | PLAN | One phase deep — most volatile |
| 9 | Slice cards / context packs | Concretize; never broaden |
| 10 | Agent judgment | Last |

Rules:

- **EXR-01** — Verbatim owner text at any level outranks ALL derived text: a PRINCIPLES WORDS quote beats a LAWS row; a NORTH-STAR quote beats a DECISIONS entry.
- **EXR-02** — DECISIONS entries with status ADOPTED rank BELOW LAWS. A conflict between an ADOPTED decision and a law or owner word is a blocking Question Record — never a silent pick, never an average (AUT-05).
- **EXR-03** — A default never overrides a law or a higher level (AUT-06).
- **EXR-04** — Two active items at the SAME level conflict → blocking Question Record; do not choose (AUT-05).
- **EXR-05** — GLOSSARY resolves conflicts about what a term MEANS (§4), regardless of the rank of the files using it.
- **EXR-06** — Plans are not permanent truth: when implementation evidence disagrees with PLAN, the plan yields — via a Question Record that names the disagreement, then a plan update (update invariant 6).
- **EXR-07** — When a law and a file disagree, report the drift — never resolve it silently (LAWS.md preamble).
- **EXR-08** — The latest explicit owner decision that supersedes an earlier one governs; the earlier entry stays as history with its `superseded_by` link (AUT-03).

## 4. Term meaning

`/GLOSSARY.md` is the definitional authority for vocabulary. Its "one concept, one name — no synonyms" policy governs the repo's **documentation and architecture vocabulary only**: Arivo's knowledge graph deliberately supports synonyms, aliases, and multiple surface forms for the same concept (P-10: concept pages carry aliases). No agent may enforce the documentation-vocabulary policy against user material.

## 5. How this contract changes

- **Append-only.** Ledgers, laws, and decisions supersede by reference; text is never rewritten; numbering never recycles. A status marker plus a pointer is the only permitted in-place change (the repo's supersession convention).
- **The change channel (D-024).** Memory deltas land by PR under P-15's standing continuous-commit authorization (merged without per-merge owner approval — the owner reviews at gates, P-13). Analysis, review, and proposal artifacts never merge themselves: they require the owner's explicit authorization per merge; a review request authorizes inspection and reporting, never edits. `main` is protected (PR-only, no force push, applies to admins) and requires the `canonical-layer` CI check (W-01 stage-2, D-025): the host rejects direct pushes and unverified merges, so the discipline is checked in the workflow, not remembered in prose. Known boundary (Q-IDENT, DECISIONS): the agent credential authenticates as the owner — attribution between agent and owner merges is canonical, not mechanical. Process detail: `context/reviews/REVIEW-PROTOCOL-PROPOSAL.md` (accepted, subordinate to this section).
- **Bounded diffs with a stated purpose (D-026, INT-099).** Every PR carries ONE coherent purpose and a bounded diff — small enough for the owner to inspect, scoped to what its purpose names. `.github/PULL_REQUEST_TEMPLATE.md` mechanizes the review protocol's §8 PR contract (purpose, owner intent, scope/non-scope, change type, acceptance evidence, known-bad coverage, not-verified, risk/reversibility, authority — the protocol file remains the canonical home; the template is the form, never a second specification).
- **Implementation and revert changes are proposed separately when appropriate (D-026, INT-099).** A fix and its revert never ride in one PR: a revert is its own bounded change with its own evidence, so each direction is reviewable on its own.
- **Who changes what.** The owner directly for NORTH-STAR and the INTENT-LEDGER (owner words enter only through owner turns — never authored by an agent; INT-092 shows a supplied credential being redacted, never recorded); the orchestrator for worklog/registers/session records within protocol; other root documents change through doc slices that land by PR under P-15's standing authorization — with ONE hard exception: **weakening a constraint, threshold, check, gate, or law (LAW-09) always requires an owner decision, as does any analysis/review/proposal artifact per the change channel**. The earlier wording ("doc slices with owner approval") is clarified by D-025 to remove the seam: routine memory deltas to root documents flow per P-15; constraint-weakening and analysis artifacts are the owner-gated classes.
- **The update invariants bind every change.** The eight invariants in `/OPERATING-MODEL.md` §7 (cold start never regresses; read order acyclic and total; no orphan authority; no silent supersession; corpus closed; plans yield to evidence; memory deltas atomic with commits; context budget is a budget) apply to this file and to every edit made under this contract.
- **The corpus stays closed.** A new root-level document requires folding its concern into §1's map in the same commit (FX-07 discipline). One canonical home per concern, forever.

## 6. Open owner decisions (visibly open — gates, not gaps)

| ID | Question | Default (stands until overridden) | Locks at |
|----|----------|-----------------------------------|----------|
| D-014 | Calculation engine scope | OPEN, non-blocking for capture; revisit at math workflow design (owner reaffirmed 2026-10-14, INT-114) | Math workflow design |
| Q6 | Research-transcript status (2026-10-16 review §8 Q1): adopt the research-methods transcript as a north-star source (intake to `context/raw/` + ledger) or keep it reference doctrine | Stays reference doctrine; the review's Part-2 table informs design without entering the intent layer | Next owner turn / Part-2 acceptance-scenario finalization |
| Q7 | Semantic-spike budget for S6 (review §8 Q2) | Defer S6 to Phase 5 (local/mock evidence only) — leaves R2 unmeasured until then | Phase-5 pre-design |
| Q8 | Sample documents for the S5 extraction spike (review §8 Q3) | Synthetic documents only (no privacy surface, weaker ecological validity) | Phase-3 schema slice |
| Q9 | Repository visibility (review §8 Q4; API observed public 2026-10-16, private at clone 2026-10-13) | Keep public; confirm intent — `context/raw/` contains personal material | Owner confirmation |
| Q10 | Fine-grained PAT hardening (review §8 Q5, from F-7: workflows:read closes the workflow-tamper class mechanically) | Keep the classic PAT; rely on the documented discipline (status quo, accepted residual D-033) | Owner token mint |
| Q11 | Work/Source identity and duplicate-import semantics; review assumption conflicts with working-context notes whose source is not yet canonical | No automatic merge/dedup or identity uniqueness rule until owner ratifies the identity contract | Phase 3 schema freeze (P3-00) |

Closed 2026-10-14 (owner turn 12, chat 2026-10-14; INT-110..INT-117 → DECISIONS D-028..D-033): Q1 (agent-agnostic design — no primary builder host; verification hosts may vary), Q2 (the purge default adopted), Q3 (the tag system removed entirely), QD-1 (any readable format), F-06 (Supabase-hosted, cloud + local synced — supersedes D-003's ordering), Q-IDENT (documented acceptance, option (a)). Closures land as LOCKED decision rows with owner words, never as silent removal from prose; the table above is the complete current register, mirrored in DECISIONS' open section, PLAN's standing-open line, and STATE's blocking-questions list (checked mechanically by VER-504).

These stay open until their named gates. Defaults lock at their named gates; silence past a named gate is consent for DEFAULTABLE questions only (QST-03). Blocking questions — owner intent, irreversible actions, security, data-loss — stay open until the owner answers; an agent never closes them by interpretation or elapsed time. Each open question blocks ONLY the work that depends on it; independent safe work continues (F-07). Q6–Q10 entered 2026-10-16 (session 18, D-036) from the 2026-10-16 review's §8 — each blocks only its named dependents; S1–S4 proceed under D-036 regardless.

## 7. Verifying this layer

`python3 tools/verify_canonical_layer.py` checks the canonicalization conditions against the real repository files: the read order, the ledger's coverage and statuses, decision supersession, the register's semantics, the archive's historical marking, this file's singular authority, and the open-question register's cross-document agreement (§6). Run it with `--self-test` to apply its known-bad mutations and prove the guards catch the failure classes they exist for (F-01: a green checker with untested blind spots gives agents unjustified confidence). Exit 0 = green; every failure prints rule ID, violation, and repair (diagnostics contract, C6 with reason code `waiting-for-harness`).

The C8 family (D-025, F-09) checks the source-coverage control: manifest structure (VER-801), raw-corpus SHA-256 immutability (VER-802), **mechanical quote fidelity of every raw-cited ledger entry** (VER-803 — missing Source lines and quote/source mismatches FAIL), and STATE.md's record-pointer freshness (VER-804). The C9 family (session 15, owner turn 12 — the Integrity-and-evidence slice, INT-117) checks cross-document integrity: every INT-/D- reference in a root canonical document resolves to a real ledger entry or decision row (VER-901 — dangling references FAIL), the stated statused-intent count agrees with the observed ledger everywhere it appears (VER-902), the entry splitter and the strict header view see the same entries (VER-903 — malformed headers FAIL), and the known-conflict normative markers hold — a reintroduced superseded rule is caught (VER-904, the slice-9 falsification loop's repair). VER-504 was re-targeted the same session: the open-owner-question register must agree across its four mirrors (DECISIONS' open section, EXECUTION §6, PLAN's standing-open, STATE's blocking-questions) — a question closes only by a LOCKED decision row carrying the owner's words, never by silent removal from prose. `tools/isolation_check.py` is the W-03 redacted secret scan (LAW-28) — conditions printed, values never; it carries its own known-bad self-test.

**Remote CI is live and authoritative (D-009, W-04, D-025; extended D-034/D-035/D-036):** `.github/workflows/verify.yml` runs on every PR and push to `main`. The three required checks are `canonical-layer`, `head-tools`, and `harness` (the third was bound after its green run was observed in session 18, record 18 §6). `canonical-layer` anchors four trusted judges from `main` under distinct SHA-256-verified names: the base verifier and isolation checker judge the candidate documents and tree, and the base self-test suites judge the candidate tool implementations. `head-tools` exercises candidate tools and fails closed on missing files. `harness` runs the real PostgreSQL suites and slice gate. Local runs are preflight; the remote run is authoritative. This is the Layer-0 precursor of the planned `make audit` surface: the proof is the run, not prose (LAW-01). The Makefile's actual command inventory is checked at session start; no absent target may be claimed as run.
