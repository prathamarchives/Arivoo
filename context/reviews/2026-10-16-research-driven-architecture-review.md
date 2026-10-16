# Arivo — Research-Driven Architecture Review and Phase 1/2 Foundation Plan

> STATUS: REVIEW-ONLY ARTIFACT — 2026-10-16 (banner per D-024/D-022). Agent-authored review, preserved verbatim as review evidence: NOT a canonical rule, NOT owner intent, NOT an implementation authorization beyond what DECISIONS D-036 records. The [P] markers are proposals that carry their own owner-decision gates. The owner's words remain authoritative in INTENT-LEDGER.md (INT-120/INT-121); interpretations and recommendations live here. Target reviewed: main at 224e5b8f6a413fe54accbe439af8fe0b5dffb000 (read-only evidence pass; no repository mutation during the review session, per the turn-15 constraint). Reviewer role: principal systems architect + research workflow designer + backend engineer + independent verification engineer. Merged into the repo by the owner's explicit authorization (owner turn 16, INT-121: "update the repo on everything we did rightnow in last convos") — the review artifact itself never becomes a parallel authority; adopted items fold into DECISIONS/PLAN (D-036).

*(body follows verbatim from the session deliverable; its original title line is preserved below)*


**Execution pass, 2026-10-16.** Role: principal systems architect + independent verification engineer. Constraint honored: **no repository mutation this session** — no code, no file edits, no commits, no PRs, no branches. Read-only evidence was gathered by running the repo's own verification suites, git forensics, a live GitHub API probe, and one uncoached fresh-context agent exam.

**Evidence labels** (per repo GLOSSARY, extended for this review): `[V]` verified this session (I ran it or read the live artifact) · `[R]` recorded in-repo, not independently re-verified · `[P]` proposed — my recommendation, NOT an adopted decision · `[I]` inferred · `[U]` unknown.

**Inputs**: (a) the designated research-method transcript (`/home/z/my-project/upload/Pasted text.txt`, a ~30:42 video transcript with timestamps, "Deep research is easy if you have a good system for it…"); (b) a second transcript by the same creator pasted inline (the "original thinking" video, 22:15); (c) the repository at `main` = `224e5b8`; (d) the eight-part review directive. The two transcripts are DIFFERENT videos; the upload file is the research-methods north star the directive names, the inline paste is treated as a corroborating second source.

---

## 1. The current verified repository state and phase status

### 1.1 Mechanical state (all verified this session)

| Claim | Result | Evidence |
|---|---|---|
| Local HEAD | `224e5b8f6a413fe54accbe439af8fe0b5dffb000` (PR #26 merge) | `git rev-parse HEAD` `[V]` |
| Local = remote | identical; `main...origin/main` shows no ahead/behind | `git status -b` + GitHub `/git/refs/heads` `[V]` |
| Working tree | clean (no uncommitted changes, no untracked repo files) | `git status --porcelain` empty `[V]` |
| Open PRs | **0** | GitHub API `/pulls?state=open` `[V]` |
| Branch protection | PRESENT: required = `[canonical-layer, head-tools]`, strict=true, enforce_admins=true, allow_force_pushes=false, allow_deletions=false, no required reviews (single identity, Q-IDENT D-033) | GitHub API `/branches/main/protection` `[V]` — matches STATE.md's "observed live" claim exactly |
| CI on main | run `38686615817` (push, `224e5b8`) **SUCCESS**; jobs `canonical-layer` (11 steps) and `head-tools` (9 steps) both success; 22 runs on main, recent five all success | GitHub API `/actions/runs?branch=main` `[V]` |
| Verifier | `python3 tools/verify_canonical_layer.py` → **51/0, exit 0** (51 unique VER-IDs) | re-run this session `[V]` |
| Known-bad suite | `python3 tools/verify_selftest.py` → **30/30, exit 0** | re-run this session `[V]` |
| Isolation | `python3 tools/isolation_check.py` → **GREEN, exit 0**; `isolation_selftest.py` → **18/18, exit 0** | re-run this session `[V]` |
| Raw-corpus integrity | all 7 `context/raw/` files hash-identical to manifest anchors, re-derived with coreutils `sha256sum` (second implementation agreeing with the verifier's Python hashlib) | `[V]` |
| Git object integrity | `git fsck --full` clean (only harmless dangling objects) | `[V]` |
| Ledger | 101 statused entries INT-019..INT-119, contiguous, unique; INT-118/119 present with owner-forwarded review quotes | coreutils count + VER-201/903 PASS `[V]` |
| Repo visibility | **API reports `private=False` (public)** — was private at clone time (2026-10-13, worklog Task 0.5). Owner action presumed; see §8 Q4 | `[V]` observed |

**Standing close-gap closed this session:** STATE.md listed PR #26's post-merge run as "not checked" (session 18's preflight duty). Run `38686615817` is now observed **SUCCESS, both jobs** `[V]`. Session 18's preflight can record this fact rather than re-derive it.

**Fresh-context cold-start re-verification** `[V]`: an uncoached sub-agent (no conversation memory, no coaching) entered via AGENTS.md, followed the selective read path (13 files, ~20.4k words, **zero `context/raw/` reads**), answered 6 exam questions (phase, exact next action, change rules, verification commands, open questions, credential rules) **6/6 correct with file/line pointers**, re-ran the verifier and isolation check itself (exit 0 each), and — notably — found real documentation defects (§4). This independently corroborates the graduation claim's core mechanism: the repo alone is sufficient for a cold agent to recover position, authority, and rules.

### 1.2 Phase status under the canonical plan

- **Phase 1 (execution environment and trust)**: COMPLETE incl. Layer 1.2 (navigation/handoffs) and Layer 1.3 (integrity-and-evidence, final slices 10/11), **GRADUATED 2026-10-15** per D-035's resequenced gate: integrated fresh-context proof at final content SHA `563b19a`, graded 96/100 by a separate fresh-context grader, both reports verbatim in record 17 §7 `[R]` — corroborated this session by the four green suites, the live protection/CI observation, and the cold-start re-run `[V]`.
- **Phase 2 (minimum trustworthy harness/build loop, P-17-scoped)**: **UNBLOCKED**; exact next action = "session 18 — Phase 2 begins: Layer 2.1 … preflight FIRST" (STATE.md) `[V]`.
- **Open owner decisions**: D-014 (calculation engine) only, non-blocking, gate at math-workflow design — register agrees across all four mirrors (VER-504 PASS) `[V]`.
- **Phase 2 layer plan section**: the owner's turn-11 execution plan "arrives as supplied/confirmed" — not yet in the repo; nothing planned from memory `[R]`.

### 1.3 Phase-numbering reconciliation (different scopes, one current truth)

| System | Scope | Status |
|---|---|---|
| Execution phases (PLAN): 1 trust env → 2 minimum harness → 3 durable capture → 4 reader+journal → 5 retrieval+compounding | The build sequence | Canonical, current `[V]` |
| Product substrate layers (NORTH-STAR): 7 layers (ground truth…retrieval) | The architecture decomposition; mapping recorded: layers 1–3 = Phases 2–3 gravity, layer 6 = product surface, layers 4–5 with Phase 5 | Canonical, consistent with PLAN `[V]` |
| Intra-phase layers ("Layer 1.2", "Layer 1.3", "Layer 2.1") | Sub-layers of an execution phase, from the owner's turn-11 plan lineage | Current; mild terminology collision with substrate layers — see §4 F-8 |
| F-slice band (F-00..F-09) | The original execution spec's slice order | SUPERSEDED by D-016, marked as such in PLAN `[V]` |
| Growth models 0–6 (OPERATING-MODEL §6) | Operating maturity per stage; Model 0 complete → Model 1 now → Model 2 at Phase 2 | Mapping recorded in PLAN `[V]` |

No numbering contradiction exists among the live systems. The one wrinkle is vocabulary: "Layer 2.1" (phase sub-layer) vs "layer 2 Ingestion" (substrate layer) — a glossary clarification candidate, not a defect (`[P]`, §4 F-8).

### 1.4 Phase 1 acceptance vs. stated requirements

| Requirement (PLAN W-01..04, Layers 1.2/1.3, graduation) | Verdict | Evidence class |
|---|---|---|
| Protected changes & review authority (PR-only, no force push, admins included, both required checks bound) | PASS | `[V]` live API + recorded behavioral rejections (records 13/15/17) `[R]` |
| Canonical source-of-truth rules (one home per concern, tiers, authority order) | PASS | EXECUTION.md + 51/0 verifier `[V]` |
| Current-state indexing & session handoffs (STATE five-area contract, event-typed records) | PASS with findings | VER-701/702/804 PASS `[V]`; stale-text findings F-1/F-2 (§4) `[V]` |
| Selective context loading (read order, read manifests) | PASS | cold-start re-run today: selective, zero raw/ `[V]`; records 14/17 `[R]` |
| Canonical verification + known-bad tests | PASS | 51/0 + 30/30 re-run `[V]`; mutation families reviewed |
| Isolation & diagnostic redaction | PASS | GREEN + 18/18 re-run `[V]`; two falsification rounds repaired (record 16) `[R]` |
| Host bridges, CI gates, independent verification, integrated graduation | PASS | live CI + protection `[V]`; graduation 96/100 `[R]` with today's corroboration `[V]` |

**Phase 1 verdict: graduated and standing.** No slice reopens: the graduation requirements were behavioral, were observed, and re-verified green today. What today's pass found is post-graduation navigation-text drift (F-1/F-2, §4) — repairable in one narrow PR, exactly the drift class Phase 1's machinery is designed to surface (a fresh-context agent surfaced it).

---

## 2. Research principles extracted from the transcript — and their Arivo implications

### 2.0 An honest note first

The review directive's Part 2 enumerates research behaviors (citation snowballing, source evaluation, rephrasing, journaling…). The attached transcript **does contain all of them** — the upload file is a research-methods video, timestamped 0:06–30:42. The inline paste is a *different* video (originality/creative thinking) that additionally evidences capture-pain and retrieval desire. I extracted principles from what is actually in the transcripts, flagged the author's personal practices and sponsored segments as non-requirements, and kept the mandatory-capability / optional-practice split explicit. Nothing below is a feature request by volume; each principle maps to the smallest underlying capability.

### 2.1 Principles from the research transcript (primary north star)

| # | Timestamp → passage (anchor) | Principle | User behavior | System responsibility | Requirement | Acceptance scenario |
|---|---|---|---|---|---|---|
| T1 | 0:00–1:01 "Deep research is easy if you have a good system… game for your curiosity" | Research quality is a property of the system, not credentials | Owner studies as a hobbyist across levels | Arivo IS the system; no skill gating anywhere | Backend serves any reading level identically | A first-time import+highlight works with zero configuration |
| T2 | 1:35–2:34 "listen to your curiosity… not what I thought I should like" | Genuine curiosity selects material; exploration without a predefined question | Captures what actually interests them, obligation-free | Capture never blocked or pre-classified (layer-2 contract) | Zero-friction ingestion of any readable thing (INT-113/D-031) | A capture lands durable with no taxonomy step; capture never waits for intelligence |
| T3 | 3:22–4:35 "like foraging… the topic emerges from the research" | Questions emerge from accumulated material | Collects broadly, then formulates | Concept formation + relationships on grounded evidence (layers 4–5) | Concept pages with provenance; discovery ≠ belief (P-08) | New input resurfaces old captures and mints provisional concepts from ≥2 independent sources |
| T4 | 2:41–3:17 "choose your title… You know where to go" + 4:05 "narrow down" | Focused, question-driven investigation | Pursues a defined question directly | Hybrid retrieval over all captured text; journals as focused collections | Semantic + keyword retrieval (layer 7); journal blocks with @-references (D-013) | A question retrieves all relevant passages across works, with why-payloads |
| T5 | 5:30–6:44 depth/breadth matrix + 7:42–9:13 "shallow media… gave me the map" | Switching between broad orientation and deep, narrow study | Skims for the map, dives when relevant | Multi-granularity anchors; bookmarks; reading state; per-work structure | Anchor to any span; bookmark = durable position (GLOSSARY) | Re-enter a skimmed work later at the exact passage; orientation view per work |
| T6 | 7:11–7:18 "the source you're reading will point you to the next source through the citations" | Literature discovery is incremental via references | Follows citations while reading | Citations representable as links between Works (relationship candidates, grounded) | Work/Source split; citation capture as evidence (layer 4) | A citation in text becomes a captured, resolvable reference to another Work |
| T7 | 9:19–9:56 tools + access pragmatics | Acquiring sources is part of the workflow | Uses libraries, search engines, archives | Import of acquired files of any readable format; provenance of how obtained | Any-readable-format import (D-031) | PDF/EPUB/TXT/MD/JSON import paths land per the durability ladder |
| — | 9:51 Anna's Archive / SciHub mention | **Author's personal (legally gray) practice — NOT a requirement** | — | Explicitly out: no scraping/piracy features | — | — |
| T8 | 10:15–11:03 "inspect them… stick to the sections that are relevant" | Triage before deep reading | Partial reading, section selection | Passage-level (not document-level) objects | Highlights/notes anchor to arbitrary passages | Highlight a 2-sentence span; system retains exact anchor |
| T9 | 11:16–11:48 + 23:35–24:22 "you absolutely need multiple sources… where one maybe lies… the others will audit" | Multi-source comparison; disagreements are signal | Reads several takes on one subject | Same-concept passages across works linkable with per-source provenance | Concept formation from independent sources (NORTH-STAR layer 5) | A concept carries evidence pointers into ≥2 distinct works; conflicting evidence both visible |
| T10 | 11:54–12:19 + 27:42–28:12 "Translations are not 100% literal… It's a filter" | Edition/version awareness | Compares translations/editions | Work/Source split: two editions = two Sources of one Work | Source = specific version, provenance survives re-parse (GLOSSARY) | Re-import a new edition; old anchors remain; concepts link at Work level |
| T11 | 12:25–12:51 "nothing worse than writing something down and forgetting where it came from… Back them up. Don't lose them." | Provenance durability is non-negotiable | Keeps references everywhere | Immutable evidence + stable anchors + @-references; export/backup | C1/C5; LAW-19/20; D-029 backup default | Every note/highlight resolves to its source passage forever; export round-trip preserves it |
| T12 | 13:18–14:08 "fall to the level of your systems… visit something old" | Continuity via system, not motivation | Returns to material after gaps | Durable reading state; resumable position/context | Bookmarks + reading sessions (D-010 coarse events) | After any gap, "where was I" is recoverable from the repo/store alone |
| T13 | 15:03–15:48 "a quick little journal just puts you back on track… even if there's breaks" | Journaling = resumption after interruption | Writes day-page journals referencing material | Revisioned journal blocks with @-references | Journal block (GLOSSARY); D-013 first workflow | Journal + captures reconstruct working context after a break |
| T14 | 17:04–17:56 "a funnel… inspection → to read → insights → order" | Progressive refinement of captured material | Organizes captures as they prove useful | **Voluntary** organization only — no enforced funnel, no queue (NG-01) | Bookmarks/notes/concepts; no pipeline stage waits for the owner | The owner CAN organize; nothing REQUIRES staging before capture is durable |
| T15 | 17:56–18:36 + 19:50–20:12 "a place where ideas can meet… unexpected random links" | Synthesis = connections across sources, incl. unexpected | Brings distant material together | Relationship candidates (grounded text-pair/structural evidence only) + concept formation | D-019 evidence rules; zero belief weight for agent material | Graph probe: automatic relations add value without violating evidence rules |
| T16 | 19:07–19:26 "clip out… and please rephrase them in your own words" | Comprehension via rephrasing | Highlights + writes own formulation | Highlight (verbatim) and note (owner thinking) as SEPARATE attributed objects | Note = deep, revisioned, owner-authored (GLOSSARY, INT-044) | Both coexist on one anchor; attribution distinguishes owner text from source text |
| T17 | 19:31–19:44 + 26:11–26:42 "identify problems… what they disagree on… have they made assumptions?" | Extract tensions, assumptions, open questions | Annotates limitations and unanswered questions | Free-form notes that are never lost and always findable; @-references | Notes searchable (keyword→semantic); immutable revisions | An open-question note resurfaces when related material arrives |
| T18 | 21:18–23:29 CRAP test (Current/Relevance/Authority/Accuracy/Purpose) | Source evaluation on five axes | Judges sources before trusting them | Evaluation is the OWNER's judgment — the system stores it, links it, and makes it queryable (esp. temporally) | Source metadata (date/venue/author) as data; notes as evaluation records; temporal queries (layer 7) | Temporal query finds sources by date; an evaluation note references its source durably |
| T19 | 24:28–26:05 "I want to be proven wrong… seek things that you disagree with" | Actively seek contradicting evidence | Reads opposing views | Retrieval must not systematically hide disagreement; multi-source linking makes conflict visible | No popularity-only ranking that buries minority evidence; why-payloads expose the basis | For a concept with conflicting evidence, retrieval surfaces both sides |
| T20 | 28:18–30:32 "the final step is some sort of output… everything I read and write is ultimately ordered towards something I'm going to produce" | Outputs drive and discipline research | Writes essays/videos/notes from material | Journal as drafting surface with durable citations; export of owner-authored material | @-references survive renames; export path preserves owner material | A journal references 20 captures; export → restore → every reference resolves |

### 2.2 Corroborating principles from the second transcript (originality video)

| # | Passage anchor | Principle | Arivo implication |
|---|---|---|---|
| O1 | "you are what you consume… thoughts are the sum of your bookshelf… cook with what's in the fridge" | Input quality/diversity determines thought quality | Diverse ingestion + the index IS the inventory of the fridge (what's in it must be knowable) |
| O2 | "allow time to think… processing happens when you're not consuming" | Capture and digestion are different phases | Resurfacing/processing rhythm without forced immediate organization; no capture-blocking processing |
| O3 | "graveyard of all these random voice notes that I never got around to sorting" + transcription/summary desire (AudioNotes — **sponsored segment, flagged; treated as market evidence of the pain, not a design mandate**) | Zero-friction capture, else captures rot | The strongest user-need signal in either transcript: capture must be effortless and self-organizing; audio transcription is a plausible future format (INT-113 "every readable format") |
| O4 | "live first, create after… get out into the world" | Life experience is source material | Notes/journal capture beyond documents (already the model — notes are owner raw thinking) |
| O5 | "the very act of creation inspires more ideas… every paragraph a bridging point" | Writing surfaces connections | The write loop (journal + retrieval while drafting) is a first-class surface, not an afterthought |
| O6 | "mix your passions… overlap them… nobody can copy who you are" | Unique cross-domain intersections define the owner | Cross-source/cross-domain concept formation is the compounding engine (C3) |
| O7 | "magic chat… pull answers from your bank of notes whenever you ask it a question" | Conversational retrieval over personal knowledge | C2 made concrete: the agent surface + retrieval layers are the "magic chat", with provenance the sponsored tool lacks |

### 2.3 Mandatory capabilities vs. optional practices

**Mandatory system capabilities** (each serves several principles): durable capture of any readable thing (T2/T7/O3) · passage-level anchors + immutable highlights (T8/T11/T16) · owner-authored revisioned notes (T16/T17/O4) · journal blocks + @-references (T13/T20/O5) · Work/Source split + citation linkability (T6/T9/T10) · keyword→semantic retrieval with why-payloads (T4/T17/T19/O7) · concepts from grounded multi-source evidence (T3/T9/T15/O6) · resumable reading state (T12/T13) · export/backup (T11/T20) · agent access via API/MCP (O7, C2).

**Optional owner practices — supported, never enforced** (per P-06/D-030/NG-01): morning routines, the funnel stages, CRAP ratings as structure, rephrasing discipline, topic-selection method, reading order, specific tools (Zotero/Obsidian), paywall workarounds (**never a feature**), output cadence. The transcript's author organizes via a to-read funnel; Arivo's equivalent is voluntary bookmarks/notes — never a required staging queue, never compulsory tags.

**Smallest-capability analysis:** the eight mandatory capabilities above collapse into five substrate primitives already in the recorded design — (1) stable anchor, (2) immutable attributed evidence row, (3) revisioned owner note/journal, (4) rebuildable derived tier (indexes, relationships, concepts), (5) scoped agent-facing command surface. The seven-layer contract already decomposes exactly these. The transcripts do not demand a new layer; they **confirm the recorded one** and sharpen acceptance scenarios (esp. disagreement visibility T19, temporal queries T18, resumability T12/T13, and capture friction O3).
---

## 3. Traceable review of the seven product layers

Method: for each NORTH-STAR layer — single primary responsibility, capability enabled, data owned vs. derived, contracts, dependencies, failure modes, decide-now / spike / defer, acceptance tests. Then cross-layer analysis, the full data-lifecycle trace, and compliance with the recorded decisions (no resurrection of vetoed designs).

### 3.1 Layer 1 — Ground truth

- **Responsibility:** hold the immutable, attributed, owner-scoped record of everything that happened (source snapshots, highlights, bookmarks, note/journal revisions, behavior events).
- **Capability enabled:** "nothing is lost" (C1) and "everything is explainable/reversible" (C5) — the evidential floor for every other layer.
- **Owns:** append-only evidence rows (edit = new revision; delete = tombstone). **Derives:** nothing.
- **Contracts:** LAW-19 (no update/delete; triggers reject), LAW-21 (owner scope + actor on every write), LAW-22 (no cross-owner query, RLS), purge = the only authorized mutation, itself ledgered (D-011/D-029).
- **Dependencies:** none (bottom layer).
- **Failure modes:** silent mutation; provenance loss; cross-owner leak; tombstone-purge confusion; unrecoverable backup gap.
- **Decide now:** identity scheme (UUIDv7-class time-ordered IDs from `adapters/ids` — LAW-24 lands Phase 2), actor/authorship vocabulary (owner / runtime-agent / worker / model-decision), revision model, purge-ledger shape. **Spike:** none needed. **Defer:** nothing load-bearing.
- **Acceptance tests:** immutability trigger rejection with named code; tombstone recovery; purge contract (content + derived + blobs removed, audit row remains, restore applies ledger); export→restore round-trip equality (hash-level).

### 3.2 Layer 2 — Ingestion

- **Responsibility:** turn any readable file into Work + Source + version + passages, atomically, deduped by Work; bookmarks are positions.
- **Capability enabled:** day-one import (INT-019) and zero-friction capture (T2/O3).
- **Owns:** parse artifacts (passage texts, structural facts). **Derives:** the mapping file→passages (re-runnable; provenance survives re-parse).
- **Contracts:** atomicity (partial ingest never visible), capture never waits for intelligence, dedup by Work identity, anchor stability per Source.
- **Dependencies:** layer 1 (writes evidence of import), layer 3 (invalidates indexes).
- **Failure modes:** non-atomic ingest (crash mid-import leaves half a work); anchor drift on re-parse; format rot; capture blocked by extraction intelligence.
- **Decide now:** Work-dedup identity convention; the anchor spec is the single most retro-expensive decision in the architecture (couples 1/2/3/4/7). **Spike now:** extraction quality + anchor stability on 3–5 real documents (§7 S5). **Defer:** exotic formats, external-platform integrations (incremental, INT-024).
- **Acceptance tests:** crash mid-import → zero partial rows (transaction proof); re-import same file → same Work, no duplicates; re-import new edition → new Source, same Work, old anchors intact; capture path works while extraction pipeline is down.

### 3.3 Layer 3 — Memory index

- **Responsibility:** make captured material findable — keyword immediately, semantic later — entirely rebuildable.
- **Capability enabled:** retrieval over the bank (T4/O7); resurfacing (T3).
- **Owns:** nothing (derived tier). **Derives:** keyword index; later, embeddings + vector index.
- **Contracts:** rebuildability (delete-and-rebuild with zero loss — the P-12 standing design test), invalidation on evidence revision, provenance on every derived row (LAW-20).
- **Dependencies:** layer 1 (source of truth), layer 2 (passages).
- **Failure modes:** stale index after revision; unrebuildable index (state leaked into derived); capture blocked on indexing; silent ranking that hides disagreement (T19).
- **Decide now:** the derivation-ledger pattern (run ID, versions, input hash) and invalidation contract — schema-coupled, cheap now, expensive later. **Spike now:** embedding quality/latency/cost on a golden set (§7 S6). **Defer:** hybrid ranking policy, pgvector tuning (Phase 5).
- **Acceptance tests:** index delete → rebuild → hash-identical results; note revision → stale entries invalidated; a golden-set query must return the expected passage in top-k; conflicting-evidence queries surface both sides.

### 3.4 Layer 4 — Structure and relationships

- **Responsibility:** hold evidence for decisions on text pairs or structural facts; everything else is discovery.
- **Capability enabled:** citation following (T6), cross-source comparison (T9), synthesis (T15/O6).
- **Owns:** relationship-evidence rows (grounded). **Derives:** relationship candidates (discovery-class, zero belief weight).
- **Contracts:** D-019 — evidence for inferred relations only from grounded text-pair decisions or structural facts; agent-authored material is attributed information, never corroboration (P-08: discovery ≠ evidence).
- **Dependencies:** layers 1–2 (pairs, anchors), layer 3 (candidate surfacing), feeds 5 and 7.
- **Failure modes:** manufactured truth (agent assertions counted as evidence); junk relation minting; provenance loss on derived edges.
- **Decide now:** the evidence-table shape (text-pair references, structural-fact vocabulary, provenance columns) — retro-expensive. **Defer:** relation-inference policy, Kev's decision boundaries (Phase 5 gates).
- **Acceptance tests:** a relation without grounded evidence is rejected (named code); deleting the derived graph and rebuilding from evidence yields the identical edge set; a known-bad "agent-asserted relation" fails.

### 3.5 Layer 5 — Concept formation

- **Responsibility:** mint provisional concepts from independent sources; graduate on out-of-sample evidence.
- **Capability enabled:** "personal wikipedia" (P-10), concept pages with aliases; compounding (C3).
- **Owns:** concept entities (label, gloss, aliases, provenance). **Derives:** graduation status, evidence links.
- **Contracts:** instant-but-provisional auto-concepts (P-10 — the slow-compounding assumption removed); graduation on out-of-sample evidence, never volume; zero system-imposed labels (D-030 — the tag system is REMOVED; owner free-text words are one signal, never a gate); C4 provenance.
- **Dependencies:** layers 3–4 (candidates + evidence).
- **Failure modes:** concepts lost after a session (the owner's stated worst-of-class, P-08); junk concepts that never prune; classification words silently regaining gate semantics (the VER-904/MUT-27 guarded class).
- **Decide now:** concept identity + provenance schema (shared with layer 4's evidence design). **Defer:** Kev policy/eval gates, classifier calibration (Phase 5 — no fabricated assumptions).
- **Acceptance tests:** concept minted from ≥2 independent sources with per-source pointers; out-of-sample graduation gate observable; a concept's every claim traceable to evidence rows; the tag-removal regression guard stays green (MUT-27).

### 3.6 Layer 6 — Agent surface

- **Responsibility:** one API core, MCP as adapter, scoped tokens, context packs, untrusted-content marking.
- **Capability enabled:** C2 — the owner's agents have the owner's context (O7 made real: the "magic chat" with provenance).
- **Owns:** command registry, scopes, attribution on writes. **Derives:** context packs (bounded, recomposable).
- **Contracts:** D-019 surface contract — scoped reads, attributed writes, idempotency, bounded responses, stable error codes; one command registry behind HTTP/CLI/MCP (no client invents a mutation path); NG-02 (agents never touch the DB); MCP read-first.
- **Dependencies:** all data layers; layer 7 for retrieval.
- **Failure modes:** the privileged agent (P-09's failure mode — a client that touches the DB becomes part of the mechanism and starts manufacturing truth); unattributed writes; context overflow (response budgets ignored).
- **Decide now:** attribution is schema-level (actor on every write — lands with layer 1's conventions); command registry pattern (lands with the first command). **Defer:** MCP write enablement (after attribution is proven), multi-agent concurrency policy.
- **Acceptance tests:** an agent write without attribution rejected; token scope crossing denied with a stable code; a response exceeding its budget is truncated with a continuation token; an agent attempting direct DB connection fails (boundary lint + NG-02 test).

### 3.7 Layer 7 — Retrieval

- **Responsibility:** hybrid (keyword + semantic) query with why-payloads, temporal and behavioral queries, response budgets sized to an agent's context window.
- **Capability enabled:** focused investigation (T4), disagreement visibility (T19), evaluation queries (T18 temporal), resurfacing (T3).
- **Owns:** nothing (query surface over derived tier). **Derives:** rankings, packs.
- **Contracts:** no cross-owner (LAW-22), why-payloads mandatory (C5), budgets enforced, stable error codes.
- **Dependencies:** layers 3–5.
- **Failure modes:** answers without provenance; ranking that buries disagreement; unbounded responses breaking agent contexts.
- **Decide now:** the query-surface vocabulary must exist in the schema (timestamps, behavior events — D-010 coarse events), i.e., nothing new to decide beyond layers 1–3 conventions. **Spike:** ranking quality (S6). **Defer:** full hybrid policy.
- **Acceptance tests:** every result carries a why-payload resolving to evidence rows; temporal query by source date works; response byte-budget enforced; golden-set precision@k threshold met (measured, not asserted).

### 3.8 Cross-layer findings

- **Overlap:** none material. Layer 3 vs. 4 boundary (index vs. relationship evidence) is clean: derived-findability vs. derived-belief. The one soft spot: "relationship candidates" surface via layer 3 search but live in layer 4 — ownership is assigned (layer 4) and correct.
- **Missing responsibility (genuine gap):** **export/restore** is not a named layer or a named phase-exit criterion. It is implied (C1, D-029, P-12 rebuildability) but the phase plan never requires proving the round trip. This review flags it and proposes the smallest fix: an explicit exit criterion, not a new layer (§5, §6). Also unnamed: **provenance-of-acquisition** (T7/T11 want "which edition, obtained how") — satisfiable within Source metadata; no new structure needed.
- **Hidden coupling:** the anchor spec couples layers 1/2/3/4/7 (identity of a highlight, passage indexing, text-pair evidence, why-payloads all point through it). The actor/authorship vocabulary couples 1/6 (and every write). The derivation-ledger pattern couples 3/4/5. These three are exactly the retro-expensive decisions — the §5 boundary challenge centers on them.
- **Decisions that would be expensive to change after implementation:** anchor spec; evidence-table shape; concept identity; attribution columns; ID adapter conventions. All are schema-level and all land in Phase 3's "schema v0+" — which is why Phase 2's harness must exercise their patterns first (§5).

### 3.9 The full data lifecycle (source → invalidation), with authorship checkpoints

A PDF enters (import): layer 2 parses → Work + Source + version + passages with anchors; import event lands in layer 1 with actor=owner. The owner highlights a passage (T16): immutable evidence row + stable anchor, attribution=owner. They rephrase it in a note: revisioned owner-authored row on the same anchor. Keyword index updates (layer 3, derived, provenance=run). Weeks later a related paper arrives (T6): a citation in its text is captured; a text-pair relationship *candidate* is derived (discovery, zero belief); a provisional concept mints from the two independent sources (layer 5, provenance per source). The owner asks a question (O7): hybrid retrieval returns passages + concept with why-payloads resolving to evidence rows (C5). The owner revises their note: new revision, old preserved. A new edition of the book is imported (T10): new Source, same Work; per-source anchors survive; concept links hold at Work level. An extraction defect is found and the derivation re-run: derived rows (index, candidates) are deleted and rebuilt — zero loss, hash-equal; evidence rows never moved. A capture is deleted: tombstone; retrieval hides it; it remains recoverable; only the owner-run purge (D-029) truly erases, leaving the audit row. At every hop: authorship distinguishable (owner vs. runtime-agent vs. worker vs. model-decision), provenance present, and the derived half rebuildable or reversible.

### 3.10 Compliance with the recorded decisions (no resurrected designs)

Checked against DECISIONS/LAWS/GLOSSARY: no review queue anywhere above (NG-01/P-06 honored — the funnel became voluntary bookmarks); no compulsory tags (D-030 — classification words stay free text); stable identity + provenance throughout (P-12/LAW-19/20); semantic retrieval kept as committed architecture in the active sequence (P-16/D-15 — never "version 2"); Kev bounded, non-generative, policy/eval-gated (NG-03, P-08, GLOSSARY); API/MCP controlled, agents-are-clients (NG-02/P-09/D-019); two-outbox design intact (D-018); deployment Supabase cloud-first (D-032) — which fixes the Phase 2 real-database choice to Postgres, not SQLite. Nothing in this review reintroduces a superseded design; where I propose additions they are marked `[P]` and carry their owner-decision gate.

---

## 4. Phase 1 findings — real defects vs. acceptable residual limits

Phase 1 is reviewed as a **completed development-environment milestone**. Findings below are defects I can evidence, not perfection opportunities. Severity: P1 = blocks a stated requirement, P2 = can mislead current work, P3 = editorial/hygiene.

| ID | Sev | Finding (exact evidence) | Failure mode & goal impact | Smallest responsible correction | Regression proof |
|---|---|---|---|---|---|
| F-1 | **P2** | `AGENTS.md` line 8 contains BOTH "Phase 2 … is UNBLOCKED: begins with Layer 2.1" AND the stale "Phase 2 … is BLOCKED until the graduation gate is satisfied (D-034)… only after graduation." `[V]` (file text; found independently by the fresh-context exam AND present in my read) | A cold-start agent receives contradictory phase status and must resolve it via other files — it demonstrably confused a fresh agent today (it flagged the contradiction itself). P-18's own test ("never let stale documentation cause a real implementation mistake") is at its edge | Delete the stale sentence(s) in one narrow drift-repair PR (navigation-repair precedent: D-034 item 1) | `[P]` MUT-31: reintroduce a contradicting phase-status clause → a content-generic VER-905 (phase-status coherence across AGENTS/STATE) fails it |
| F-2 | **P2** | `STATE.md` line 7 same class: trailing bold text still says "The Phase-1 graduation gate is the ONE remaining condition… Phase 2 … stays BLOCKED until it passes" while lines 9–10 record graduation and "session 18 — Phase 2 begins" `[V]` | Same as F-1; STATE is read SECOND by every fresh agent, so this is the first text a cold agent sees after AGENTS | Same PR as F-1 (one purpose: post-graduation phase-status drift repair) | Same VER-905 proposal |
| F-3 | P3 | `AGENTS.md` line 8: "with the required check bound to `main`" (singular) vs "BOTH CI jobs required" + live protection `[canonical-layer`, `head-tools`] `[V]` | Minor intra-line drift; could understate the doubled gate | One wording fix, rides F-1's PR | VER text covers the mirrored claims in EXECUTION §7 (already correct) |
| F-4 | P3 | `EXECUTION.md` §7: the sentence "Local runs are preflight; the remote run is the proof." appears twice back-to-back `[V]` | Editorial duplication only | One-line deletion; may ride F-1's PR or wait for the post-product refinement pass (P-18) | None needed |
| F-5 | P3 | `DECISIONS.md` D-014 row status column reads PRESENTED-LOCKED while its content and all four register mirrors treat it as OPEN `[V]` | Label/content mismatch can confuse status semantics (the fresh agent flagged it) | One clarifying sentence in the DECISIONS legend ("status labels record provenance; row content governs decision state") — editorial, P-18-class | VER-504 already guards the register's substance |
| F-6 | P3 (workspace only) | Local clone retains ~19 stale `slice/*` branches (12 on remote; several `[gone]`); record 17 says "branches cleaned" (true on remote) `[V]` | No repo impact; local clutter only | Optional local `git branch -d` cleanup; never a repo PR | N/A |
| F-7 | P3 (proposal) | The workflow-file self-modification class is guarded by C6 discipline (LAW-09 + "do not touch gates/workflows") + the Q-IDENT single-identity acceptance (D-033), not by mechanics: a PR editing `verify.yml` to vacuous steps would still produce green required checks (the anchored judges live INSIDE the workflow). No verifier check covers the workflow file (51 VER-IDs reviewed — none) `[V]` | A compromised agent merge path could silently neuter the wall. Documented, accepted residual (record 16 §4.1 "agent-discipline" class; D-033) — NOT a failure against a stated Phase 1 requirement | `[P]` Cheap mechanical hardening exists: mint a fine-grained PAT with contents:write but workflows:read — GitHub then mechanically rejects pushes that modify workflow files. Owner action only; rides D-033's boundary without reopening it | `[P]` A red-team probe PR attempting a workflow-file edit under the new token (expect rejection) |
| F-8 | P3 (proposal) | "Layer" terminology collision: substrate layers 1–7 (NORTH-STAR) vs. phase sub-layers 1.2/1.3/2.1 (owner's plan lineage) `[V]` | Ambiguity risk in future records; no current misuse | `[P]` One GLOSSARY clarification ("phase layer" vs "substrate layer") | None (vocabulary) |

**Closed this session (not a defect):** the standing close-gap — PR #26's post-merge run observed SUCCESS (run `38686615817`, both jobs) `[V]`. **Observed (owner judgment, §8 Q4):** repository API visibility is currently public (`private=False`); it was private at clone. If intentional, nothing to do — isolation is green and credentials hygiene held `[V]`; if not, flip it back (the raw corpus is personal material).

**Acceptable residual limits (documented, NOT reopened):** isolation's undecidable pattern-scan classes and the CI runner-namespace allowlist (record 16 §9/§4.1); no OS-level process separation (accepted, discipline-bound); single-identity attribution (Q-IDENT, revisit trigger = unauthorized-merge incident); tag-semantics clarification gated before Phase 5 (D-034's P2 disposition — on schedule, not late); CODEOWNERS deferral (rides Q-IDENT option (b), correctly reasoned). The grader's three read-manifest word-count underestimates (record 17 §4.4) — rubric note carried, no conclusion affected.

**Phase 1 status (defensible close):** GRADUATED and standing. Every stated graduation requirement was observed when claimed `[R]` and re-verified independently today `[V]` (four green suites at HEAD; live protection with both required checks; green CI at HEAD; 0 open PRs; a fresh-context agent recovering full position/rules/next-action 6/6). The defects found are post-graduation navigation-text drift (F-1/F-2) — caught by exactly the mechanism Phase 1 built (an uncoached fresh-context reader), repairable in one narrow PR, and by themselves evidence the loop works. Phase 2 is legitimately unblocked.

---

## 5. Recommended Phase 2 scope — and a challenge to the boundary

### 5.1 What the recorded boundary says

Phase 2 = the minimum trustworthy harness (P-17-scoped): one real-stack test · Proof Sheet generated from run records · scope enforcement · representative known-bads for the proactive set only. Exit: the harness proves **scope, evidence immutability, idempotency, independent reads on a real database**; broken builds fail with named codes. Phase 3 = durable capture: schema v0+ (Work/Source split; highlight stable identity + anchor + immutable revision; bookmark; note; owner scope + actor; idempotent commands; client outbox; recovery). Phase 5 = retrieval/compounding. The proactive guardrail set is fixed from day one.

### 5.2 The challenge, answered honestly

"Do not treat minimum as a ceiling" — so I tested each retro-expensive foundation against the question: *if Phase 3 froze the schema tomorrow, what would be missing?*

| Foundation | Status under the recorded plan | Verdict |
|---|---|---|
| Real DB in tests + independent reads | Explicitly in Phase 2's exit | Included `[V]` |
| Identity conventions (IDs via adapter, LAW-24) | LAW-24 live-at Phase 2 | Included `[V]` |
| Owner scope + actor + provenance + tombstone patterns | Phase 2's exit requires proving "evidence immutability … on a real database" — which forces a representative evidence-shaped table with exactly these conventions | Included, but IMPLICIT — make it explicit `[P]` |
| Migrations machinery (versioned, forward-only, baseline) | Not named anywhere in Phase 2/3 text | **Gap — include now** `[P]`: cheap to establish, brutal to retrofit (schema evolution discipline is the harness's own substrate) |
| Idempotency + transaction boundaries | Phase 2 exit (idempotency) + Phase 3 (LAW-23) | Included `[V]` |
| Crash/restart injection TOOLING | Phase 3 exit (kill -9 trials) needs the injection harness; building the injector in Phase 2 is trivial; building it in Phase 3 under feature pressure is not | Include the tool, defer the trials `[P]` |
| Index derivation-ledger pattern (rebuild + invalidation) | Phase 3 exit has keyword search; the derivation-ledger pattern is P-12's standing test but no Phase 2 item exercises it | `[P]` One rebuildable derived table proven in the harness (delete → rebuild → hash-equal) |
| Anchor spec | Phase 3/4 territory; quality UNKNOWN | **Spike now** (S5) — design Phase 3's schema against measurements, not guesses |
| Semantic path | Phase 5 per plan; P-16 forbids deferring the ARCHITECTURE, not the sequencing. The schema decisions semantic needs (passage text retention, stable anchors, rebuildable derived tier) are ALL Phase 3 substrate commitments — nothing forecloses Phase 5 | No scope change. `[P]` add a measurement spike (S6) so Phase 5's design is evidence-based, and a Phase-3 exit sub-check: "schema does not foreclose layers 4/5/7" (passage text retained; derived rebuildable; evidence immutable) |
| API/MCP + attribution | Attribution = schema columns (Phase 3); command registry = first command (Phase 3); MCP read-first later | Correctly sequenced `[V]` |
| Export/restore round-trip | NOWHERE named as an exit criterion — C1's ultimate escape hatch is never required to be proven | **Gap — add an explicit exit criterion** `[P]`: earliest honest home = Phase 3 exit ("owner-authored material exportable; restore is lossless") — see §6/§7 |
| Outboxes, background jobs, Kev policy, MCP writes | Phase 3/5 per plan; no evidence exists to calibrate them earlier | Correctly deferred (no fabricated assumptions) `[V]` |

### 5.3 The proposed revision (explicit, severable, owner-gated)

**No phase is renamed or resequenced.** Phase 2 keeps its name, scope discipline, and P-17 guard. Three narrow additions are proposed `[P]`, each a severable rider on the existing Layer 2.1 definition:

1. **Rider A — make the implicit explicit + migrations:** the harness's representative table carries ALL substrate conventions (owner, actor, provenance, revision, tombstone) and is managed by a migrations runner from day one (forward-only, baseline, re-runnable).
2. **Rider B — two measured spikes run alongside the harness** (evidence-gathering, not implementation): extraction/anchor stability (S5) and semantic-retrieval quality/cost (S6). Both produce archived measurements + design notes; neither writes product code.
3. **Rider C — export/restore becomes a named Phase-3 exit criterion** (one line in PLAN when Phase 3's section is next touched; the owner's plan section arrives as supplied, so this is flagged now, adopted only with the plan intake).

Consequences if adopted: Phase 2 grows by roughly one slice's worth of harness work and two bounded spikes; Phase 3 starts with measured anchors and a proven migration/derivation discipline; C1 gains a testable escape hatch. Consequences if rejected: the recorded plan remains coherent, with the two gaps (migrations machinery, export exit) carried as named risk items R-mig/R-exp on the risk list until their natural homes.

**Grounded defaults chosen (not asked, per §8 discipline):** the Phase 2 real database is **Postgres** (D-032 Supabase = hosted Postgres+pgvector; a SQLite detour would diverge from the decided stack and re-litigate D-003/D-032) `[I→default]`; CI uses a Postgres service container; local dev uses the same engine. Verification independence uses a **second connection/role** (psql) — not the application's driver path (LAW-13's spirit).
---

## 6. Risk-ranked issues that must be resolved before relevant implementation

| Rank | Issue | Why now | Evidence | Guard / owner gate |
|---|---|---|---|---|
| R1 | **Anchor/extraction quality unknown** — the most retro-expensive schema decision (couples layers 1/2/3/4/7) has zero measured evidence | Phase 3 schema freezes against it | `[U]` — no spike has run | S5 spike (§7); anchor spec decision follows the measurement |
| R2 | **Semantic retrieval quality/cost unknown** — P-16/D-15 commit it as core; designing Phase 5 (or validating the schema supports it) blind is a real risk | The compounding probes (C3) are the product's differentiator | `[U]` | S6 spike (§7); golden-set thresholds fixed BEFORE the spike runs |
| R3 | **Phase-status text drift has no mechanical guard** (F-1/F-2 class survived 51 green checks) | Fresh agents are the primary readers; drift was observed today | `[V]` (fresh-agent exam + file text) | Narrow drift-repair PR + `[P]` VER-905/MUT-31 |
| R4 | **Migrations machinery unnamed in Phase 2** | Retro-brutal; cheap now | `[V]` (PLAN/EXECUTION text) | Rider A (§5.3) |
| R5 | **Export/restore never an exit criterion** — C1's escape hatch unproven by design | The promise's ultimate test | `[V]` (PLAN exits reviewed) | Rider C (§5.3); Phase 3 exit line |
| R6 | **Workflow-tamper class rests on C6 discipline** (F-7) | Single-identity trust boundary; accepted, but a mechanical hardening exists | `[V]` (verify.yml analysis + 51 VER-IDs reviewed) | Fine-grained PAT (§8 Q5 rider; §4 F-7) |
| R7 | **Postgres/pgvector local↔Supabase parity** — extension availability differs by host/version | Phase 2 rig must not validate on a stack Phase 3 can't deploy | `[I]` | Version-parity check in the Phase 2 rig (S1); a FACT entry (LAW-02) |
| R8 | **Time-to-first-capture (the P-17 meta-project risk)** — 17 sessions of trust infrastructure, zero product capture to date | The transcript's own evidence (graveyard of voice notes) says capture rot is the owner's live pain | `[V]` (repo history vs. empty product tree) | Slice discipline: S1–S4 stay minimal; spikes bounded; Phase 3 starts immediately after |
| R9 | **Single-identity attribution** (Q-IDENT) — agent merges authenticate as the owner | Accepted with a recorded revisit trigger | `[R]` D-033 | Standing; revisit on unauthorized-merge incident only |

---

## 7. The next executable slices (with acceptance tests and independent proofs)

All slices are `[P]` — proposals aligned to the standing P-17-scoped Layer 2.1 definition, awaiting the owner's confirmation as the plan section is supplied. Sequenced S1→S4 (harness), with S5/S6 as parallel bounded spikes; Phase 3's opening slice is sketched as the handoff only (NG-04: one phase deep).

**S1 — Real-stack rig + migrations v0.** *Purpose:* make "real database" real. *Need:* Phase 2 exit requires it; R4/R7. *Preconditions:* Phase 2 unblocked (done); Postgres available in CI (service container) and locally. *Scope:* CI job + `make`-equivalent commands: migrate, verify-schema, health; a migrations directory with runner (forward-only, versioned, baseline); version-parity FACT entry (R7). *Non-goals:* any product table, any business logic, any API. *Acceptance (each observable):* (a) fresh Postgres → migrate → schema present, verified via an INDEPENDENT psql client (second connection, not the app driver); (b) second migrate run = no-op (idempotent); (c) migrate on a populated DB preserves every row (row-count + checksum before/after); (d) drop DB → replay all migrations → identical schema hash; (e) CI green on a PR exercising it. *Must-reject:* a migration containing a destructive operation without an explicit baseline bump is REFUSED with a named code; a migration that would run twice is refused. *Fail-first test:* before S1, `migrate` does not exist — the harness test fails with `waiting-for-harness`-class named code. *Independent proof:* a fresh-context sub-agent re-runs the full sequence from a clean clone and reports raw outputs; CI is the remote authority. *Stop conditions:* Postgres-in-CCI cannot reach parity with Supabase (R7) → Blocker Record. *Handoff:* S2 builds its table through S1's runner.

**S2 — The substrate-convention table + immutability + independent reads.** *Purpose:* prove evidence immutability, owner scoping, and independent reads on the real DB (the Phase 2 exit's core). *Need:* Phase 2 exit; Rider A. *Scope:* ONE representative table (evidence-event analog) carrying owner, actor, provenance (run ID, versions, input hash), created-at via the clock adapter; append-only trigger; tombstone pattern; RLS enabled; a second DB role for reads. *Non-goals:* product objects (Work/Highlight/etc. are Phase 3), API, indexes. *Acceptance:* (a) UPDATE and DELETE on the table are rejected by triggers with named codes (LAW-19 analog); (b) a two-owner test: owner B's connection sees zero of owner A's rows (LAW-22 analog); (c) a write without owner or actor is rejected at the schema level (LAW-21 analog); (d) the independent role reads state the writer path cannot influence (LAW-13 analog); (e) tombstone: delete-flag lands as a new row, original recoverable. *Must-reject:* an unattributed write; a cross-owner read; an in-place mutation. *Fail-first:* before S2, each of (a)–(c) has no guard to reject it — each test fails for the stated reason (no trigger / no RLS / no NOT NULL). *Independent proof:* fresh-context verifier writes ONLY failing tests against a seeded DB and reports; the gate (CI) decides. *Stop:* RLS semantics differ across Postgres versions (R7). *Handoff:* S3's command writes through S2's conventions.

**S3 — Idempotent command path + crash-injection tooling.** *Purpose:* prove idempotency, atomicity, and recovery on the real stack (Phase 2 exit; LAW-23's pattern early). *Scope:* one command ("record event") via a command-registry pattern with client ID + idempotency key, single transaction boundary, acknowledgment strictly after commit; a crash-injection helper (kill −9 at pre-commit / in-transaction / post-commit-pre-ack). *Non-goals:* outboxes, sync, any product semantics. *Acceptance:* (a) replay the same command N times → exactly one row (transaction + key); (b) same key + different body → named conflict code, no silent overwrite; (c) kill at each injection point → restart → state equals the clean run (compared via the independent read from S2); (d) acknowledgment never precedes commit (observable ordering). *Must-reject:* duplicate row; silent overwrite; post-crash divergence. *Fail-first:* no command exists → idempotency test fails for the stated reason. *Independent proof:* fresh-context sub-agent re-runs the fault matrix from a clean clone; all raw outputs archived. *Handoff:* S4 wraps S1–S3 into the gate.

**S4 — Proof Sheet, scope/size enforcement, representative known-bads, named codes (Phase 2 exit assembly).** *Purpose:* assemble the harness into the gate: `make`-surface per OPERATING-MODEL §9 (state/fast/red/prove/gate/verify/known-bad, at minimum), Proof Sheet generated from run records (never hand-edited), SIZE/SCOPE checks, the proactive-set known-bads (scope breach, protected-path edit, skipped test, hand-written Proof Sheet, lowered threshold, missing red record, test edited after red, unapproved dependency), every failure with a reason code. *Acceptance:* a deliberately broken build fails with its NAMED code (observed in CI, not locally); a green slice's Proof Sheet is reproducible from run records; a hand-edited Proof Sheet fails the gate; `make verify` ≤10 min in CI. *Fail-first:* before S4, no gate exists — the known-bad build merges-blocking check cannot fire. *Independent proof:* the known-bad run is executed by CI (remote authority) and re-run by a fresh-context verifier. *Stop:* three failed cycles → Blocker Record (LAW-16). *Handoff:* Phase 3 Layer 3.1 opens with schema v0 through S1's migrations and S2's conventions.

**S5 — Spike: extraction + anchor stability (bounded, parallel, no product code).** *Purpose:* measure what Phase 3's schema depends on (R1). *Scope:* 3–5 real documents (owner-supplied: a PDF paper, an EPUB chapter, a web article + 2 synthetic), extraction to passages, anchors, re-extraction after cosmetic file changes (rename, re-save, metadata touch). *Measurements (archived raw):* extraction success rate per format; anchor stability rate across re-extraction (same passage → same anchor); passage segmentation sanity (spot-checked against the doc); wall-clock per document. *Acceptance:* the spike produces numbers + a written anchor-spec recommendation with its evidence; go/no-go criteria fixed BEFORE running (e.g., anchor stability <90% on PDFs ⇒ anchor spec must include content-hashing fallback). *Non-goals:* production ingestion code, all formats. *Stop:* one day of effort or the documents run out — whichever first. *Handoff:* the anchor spec decision (owner-reviewed) feeds Phase 3's schema slice.

**S6 — Spike: semantic retrieval micro-benchmark (bounded, parallel, budget-gated → §8 Q2).** *Purpose:* measure quality/latency/cost before Phase 5 design (R2); validate the schema doesn't foreclose it. *Scope:* embed ~300–500 passages (S5's corpus); a golden set of ~20–30 queries with expected passages (owner-approved); compare keyword-only vs embedding hybrid; measure precision@5, latency, and cost per 1k passages. *Acceptance:* archived raw measurements + a written note: which thresholds Phase 5's design should assume; explicitly NO production index. *Non-goals:* pgvector tuning, production pipeline. *Stop:* budget exhausted or numbers stable. *Handoff:* Phase 5 pre-design evidence + the compounding semantic probe's realistic baseline.

**Phase 3 opening slice (sketch, handoff only):** schema v0 — Work/Source split, Highlight (stable identity + anchor + immutable revision), Bookmark, Note, owner scope + actor, through S1's migrations and S2's conventions, with S5's anchor spec as input. Its acceptance: fault trials lose zero (kill −9 per S3's injector), keyword search finds a capture, export/restore round-trip if Rider C is adopted. Deeper Phase 3 planning waits for its gate per NG-04.

**Parallelism:** S5 and S6 may run alongside S1–S4 (no shared files, evidence-only); S1→S2→S3→S4 are strictly sequential (each builds on the last). Nothing else parallelizes.

---

## 8. Only the questions that genuinely require your judgment

Everything else had a grounded default, chosen and stated (Postgres for the rig; S1–S4 sequence; no resequencing of phases; drift-repair as one PR; terminology clarifications as editorial riders).

**Q1 — Status of the two transcripts (blocks: Part 2's table finalization + the next session's intake).**
The review directive names "the attached research transcript" as the designated product north star. The upload file is the research-methods video; the inline paste is a second video (originality/creative thinking) by the same creator. The repo's NORTH-STAR.md quotes `context/raw/3.txt` (your mission interview). Options: **(a)** adopt the research transcript as an additional adopted north-star source (method-level) alongside 3.txt, and the originality video as corroborating reference — intake both into `context/raw/` + manifest + ledger next session *(my recommendation: the directive's own language designates it; (a) honors that without rewriting NORTH-STAR's mission)*; **(b)** treat both as reference doctrine only (like the engineering transcripts), with Part 2's table informing design but not entering the intent layer; **(c)** something narrower you name. Trade-off: (a) makes the research principles intent-grade (traceable, quoted, hard to drift from); (b) keeps the intent layer minimal but the principles stay advisory. Blocked until answered: the intake ledger entries and whether acceptance scenarios in §2 become requirement-grade.

**Q2 — Spike budget for S6 (blocks: S6's realism).**
Options: **(a)** ~$10–30 of embedding API spend for 300–500 passages × 20–30 queries *(recommended — enough for stable precision@5 numbers)*; **(b)** $0 — local/mock models only (weaker evidence, still validates the pipeline shape); **(c)** defer S6 to Phase 5 (leaves R2 unmeasured). Blocked: S6 only (S5 is local-only and needs no budget).

**Q3 — Sample documents for S5 (blocks: S5's realism).**
Options: **(a)** you supply 3 real documents (a PDF paper, an EPUB chapter, a web article) — processed locally only, never committed *(recommended — real extraction behavior is the evidence)*; **(b)** synthetic documents only (no privacy surface, weaker ecological validity); **(c)** both (3 real + 2 synthetic — my actual preference, stated under (a)). Blocked: S5's corpus selection.

**Q4 — Repository visibility (blocks: nothing downstream; privacy-relevant).**
The API reports the repo as **public** (`private=False`); it was private at clone time (2026-10-13). If making it public was your deliberate act, nothing to do — isolation is green and credential hygiene held `[V]`. If it was not deliberate, flip it back (the `context/raw/` corpus contains your personal messages and thinking). Options: (a) intentional — keep public; (b) unintentional — revert to private; (c) keep public but move nothing further into raw/ without a visibility decision. No recommendation beyond: confirm intent.

**Q5 — Fine-grained PAT hardening (blocks: F-7's mechanical fix only).**
Mint a fine-grained PAT with contents:write + workflows:read so the agent credential mechanically cannot push workflow-file changes (closes the F-7 class; costs you one token mint; does not reopen Q-IDENT/D-033). Options: (a) do it at next session start *(recommended — cheap, mechanical, independent of trust in agents)*; (b) keep the classic PAT and rely on the documented discipline (status quo, accepted residual); (c) defer to an org/ruleset migration later. Blocked: nothing else.

---

## 9. Final assessment — does the foundation support Arivo's promise?

**C1 — nothing is lost.** At the repository/process level: *proven and re-proven* — raw-corpus immutability (SHA-256 anchored, independently re-hashed this session), append-only ledgers, quote fidelity, purge/backup policy recorded, four green suites, live walls `[V]`. At the product level: *not yet provable — honestly so* — no capture exists; the path is Phase 3's fault trials plus the proposed export/restore exit criterion (Rider C). The promise is institutionalized; its product proof is correctly scheduled, and one escape-hatch test (export round-trip) is currently missing from the plan — a real but small gap, now named.

**C2 — the owner's agents have the owner's context.** Repo-level: *proven behaviorally* — graduation 96/100 `[R]` and today's uncoached re-run 6/6 with pointers `[V]`; the read path held selective discipline with zero raw-corpus reads. Product-level: *designed, not yet built* — layer 6/7 (scoped tokens, context packs, bounded responses, why-payloads) plus the transcripts' own "magic chat" demand (O7) define it precisely; MCP is read-first and attribution is schema-level from Phase 3. The strongest evidence that this promise will hold is that its repo-level analog already does.

**C3 — new inputs make old inputs more useful.** *Zero product evidence yet — by design* — but the architecture commits it structurally: rebuildable derived tier, grounded-evidence relationships, two-speed concepts with a junk gate, and the compounding probe ladder (deterministic → semantic → graph) that tests each strength separately instead of bundling an "it compounds" assertion. The two unknowns that could still defeat it are exactly R1 (anchors) and R2 (retrieval quality) — both now have bounded measurement spikes instead of guesses.

**Overall verdict.** The foundation-first strategy is coherent with all three promises, and the discipline that built it is genuinely working — today's pass found real defects through the repo's own designed mechanism (a fresh-context reader), which is the system doing its job, not failing it. The residual risks are named, ranked, and mostly cheap: fix the phase-status drift (one PR), decide the five questions above, run the two spikes, and hold Phase 2 to its P-17 floor. The single strategic danger is not any architectural flaw — it is R8, the meta-project trap: the longer the harness runs, the more the product's reason to exist (the owner's live capture pain, evidenced in both transcripts) waits unmet. The slices above are sized to make Phase 2 the *last* phase with zero product motion, and nothing in this review requires reopening anything already proven.

*No check was claimed passed without this session's run or the live artifact behind it. All recommendations are `[P]` until you adopt them.*
