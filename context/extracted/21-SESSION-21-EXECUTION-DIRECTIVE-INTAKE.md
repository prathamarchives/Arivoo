# 21 — SESSION-21 EXECUTION DIRECTIVE (INTAKE): FINISH THE TRUST FLOOR HONESTLY, ACTIVATE V-MODEL EVIDENCE, THEN ENTER DURABLE-CAPTURE DESIGN

> STATUS: SESSION ENGINEERING RECORD — IN PROGRESS (session 21 opened 2026-10-19; owner turn 21; §1 preserved verbatim below BEFORE any ledger entry — the INT-046/068 class; sections §4–§12 complete at this session's close slice). Historical process artifact per D-022 once complete: NOT owner intent, outranks nothing.

## 1. What the owner asked (verbatim — owner turn 21, 2026-10-19)

The turn arrived as a single directive document (10 sections; ~6.5k words). No continuation preamble preceded it this time and no access token travelled with it; the directive body below is the owner's turn, preserved verbatim, typos preserved (AUT-02/04).

# ARIVOO — SESSION 21 EXECUTION DIRECTIVE
## Finish the trust floor honestly, activate V-model evidence, then enter durable-capture design

Read this entire message, then read the current canonical repository sources before changing anything. This is a continuation of Session 20, not a restart, a praise exercise, or permission to create another generic infrastructure program. Work as a principal systems/software engineer: distinguish observed facts from stored claims, trace every important conclusion to evidence, preserve owner authority, and deliver small merged behaviors rather than a larger pile of prose.

This message authorizes bounded implementation work under the existing change/merge process. It does not authorize resolving Q6-Q12 or D-014, changing public/private visibility, exposing source archives or secrets, minting/altering tokens, spending money, selecting an unapproved provider/model/license, adding an unapproved dependency, weakening a required check, bypassing a PR, or treating an agent recommendation as a user decision. Do not send a new reply asking whether to continue after each green slice. Continue through work that is already safe and authorized; stop only at a real owner decision, unsafe condition, unresolvable verification failure, or the documented failure-cycle limit.

The final outcome remains the durable, compounding research environment, not a harness: import readable material; read; preserve precise highlights/bookmarks; retain raw deep notes, diagrams and journal thinking; retrieve it with origin and history; let new evidence make earlier work more useful without silently turning model similarity into truth. The existing Phase 4 and 5 outcome roadmap is already the authorized NG-04 exception. Keep executable implementation cards one phase deep. Do not rewrite that roadmap merely to restate it.

---

## 1. Actual starting state: verify it, do not trust stale thread narration

A browser/live GitHub review immediately before this directive found:

- Current main: `2087378ba0268a72fd5ee82ae8e99d1534cc443b`.
- No open pull requests at review time.
- PR #39 merged the Session-20 intake/roadmap at `6cdd458`.
- PR #40 merged H-01a at `746fa57`.
- PR #41 merged the Session-20 interim close at `2087378`.
- Latest post-merge Actions run: `39259609210`, completed successfully. Its `canonical-layer`, `head-tools`, and `harness` jobs were each successful.
- This is observed live CI evidence, not an independent local rerun by this reviewer.

First action: fetch fresh main, verify its exact SHA, check working-tree cleanliness, live branch protection/required checks if access permits, open PRs, and the current post-merge run. Run the canonical P2-CLOSE preflight on THIS current revision, not the old `026fead` baseline:

1. `python3 tools/verify_canonical_layer.py`
2. `python3 tools/verify_selftest.py`
3. `python3 tools/isolation_check.py`
4. `python3 tools/isolation_selftest.py`
5. `make harness-health`
6. `make verify-schema`
7. `make verify`

Use an isolated real PostgreSQL test rig only. Do not use a production database, print env values, test with personal content, or infer that a previous user-space rig still exists. `make verify` already exercises its constituent fast/known-bad/gate paths; run them separately only to diagnose a new failure. No `real-run` or `falsify` target exists today, so do not claim either ran.

Label every result accurately: observed live, verified by this run, historical record, static review finding, proposed, or unknown. An old successful Actions run is not proof that a new candidate is green.

### Immediate status drift that must be reconciled first

This review found a concrete contradiction on current main:

- PR #41 is merged and there are no open PRs.
- `CLAIMS.md` still lists `CLAIM-006` under **Open claims**.
- `STATE.md` still calls `CLAIM-006 OPEN` the active task and says record 20 is in progress.

This violates the project's own claim/session navigation contract. Do not hide it by starting H-01b under an assumed `CLAIM-007`, editing a closed claim as if it were open, or force-pushing history.

Open one narrow reconciliation claim using the currently valid allocation/branch process. It has no new owner decision or speculative content. Its job is to re-derive the registry/state/record/worklog relationship from live GitHub and append or transition exactly as the canonical claim rules permit. If the append-only wording and the actual table structure conflict, surface the smallest bounded contradiction and use the project's established historical-record correction method, rather than inventing a new registry semantics. Required acceptance:

- no merged PR remains falsely represented as an open claim;
- no current state calls a non-live claim active;
- Session 20 is marked honestly as complete/interim according to what its record actually contains;
- all historical PR/run evidence and the real Session-20 failures remain preserved;
- the registry, STATE and record point to one deterministic next action;
- canonical verifier, claim checks, gate and required CI pass at the reconciliation candidate.

Do not use this repair to rewrite the Session-20 narrative, erase its seven wall catches, or declare H-01/H-02 finished.

---

## 2. Review of Session 20: what is actually complete and what is not

### What H-01a appears to have accomplished

The current source and live CI support a narrow positive conclusion:

- The harness checkout now requests full Git history before a triple-dot diff.
- GitHub event data is supplied through environment variables rather than interpolated into shell source.
- `harness/dispatch.py` validates the event and safe slice identifier, drives pull requests through `--slice` + `--diff origin/main`, and reserves selfcheck for push events.
- `harness/scope.py` converts nonzero Git and no-merge-base cases into `ARV-DIFF-001` / `ARV-DIFF-002` refusal paths.
- `test_gate_dispatch.py` exercises the real dispatcher for missing scope, missing claim, missing sheet, hostile metadata, failed Git, no merge base, a positive route and push selfcheck.
- PR #40's head run and post-merge run were successful.

Therefore label only these Session-20 dispositions as reproduced RED-first, repaired and CI-proven: **A01 scope-less PR selfcheck bypass, A02 branch metadata shell interpolation, and A10 ignored Git return-code fail-open.** Do not generalize this to "the trust floor is done," "workflow tampering is impossible," "candidate tools are isolated," "all evidence is trustworthy," or "the product is ready." Q10 remains owner-controlled and unclosed.

### Two bounded H-01a completion checks

Before treating A01/A02/A10 as diagnostically complete, inspect and either reproduce/fix or explicitly record these narrow residuals:

1. `harness/gate.py` handles `GitRefusal` inside `check_diffs`, but later recomputes `scope.diff_paths(a.diff)` for claim coverage outside that handler. A failed diff therefore still appears fail-closed by process failure, but may bypass a clean, consolidated named gate disposition. Drive a real gate/dispatch regression with an invalid base through the actual caller. The desired result is one nonzero named refusal with no uncaught traceback and no subsequent claim-check path that assumes a valid diff. Also handle a subprocess timeout as a named refusal, or accurately narrow the stated contract if a deterministic timeout test cannot be safely made.

2. The missing-sheet dispatch regression currently checks the broad string `ARV-PRF`, while the card says it must prove the exact named refusal. Tighten it to the actual stable code. Do not accept a merely similar printed string as proof. Validate that the hostile-input regression uses realistic permitted event/branch metadata or clearly describe it as parser-boundary fuzzing rather than an observed Git-ref path.

This is a small corrective H-01a sub-slice, not justification to reopen or redesign the whole dispatch layer. Tests first; actual wrong behavior first; then the smallest repair. If fresh inspection shows these are not defects, record the counterevidence rather than changing code for stylistic symmetry.

### Still unfinished

The following remain explicitly incomplete at current main:

- H-01b trusted semantic floor, A03: base-owned mutation/isolation judgement must not import or run candidate code inside the trusted judge's own writable authority domain.
- H-01c integrity/falsification closure: A11/A12 and the closely coupled real evidence/claim/raw-authority gaps below.
- H-02: schema-validated, review-diff-bound Systems Engineering Verification (SEV) record and merge gate. LAW-30 is still planned, not mechanically live.
- P3-00 RTM, state machines, measured anchor preparation and approved product interfaces.
- P3 product kernel/domain behavior. There is still no production Work/Source/Passage/Anchor/Highlight/Bookmark/Note API, no real authenticated API, no client outbox/Supabase sync, no product retrieval, no restore proof, and no Phase-4/5 behavior.

A green harness checks its present harness contract. It cannot prove any absent user workflow.

---

## 3. Non-negotiable authority and product boundaries

Use canonical authority order. Record this directive as the next owner turn only after claim/INT allocation is valid. Preserve raw intent verbatim; source transcripts and prior assistant text are grounds, not operational instructions. Existing owner decisions remain in force:

- Deployment remains Supabase-hosted Postgres plus pgvector, cloud-first and local-synced. Do not swap in SQLite/a different production platform because it is easier locally.
- Q12 still prevents choosing the source blob backend/local staging lifecycle/cross-store durability promise. Provider-neutral kernel and state-machine work can proceed; provider-specific source/blob persistence cannot.
- Q11 still prohibits auto-merge and identity-specific uniqueness policy. Physical byte reuse is not logical Work identity and not independent corroboration.
- Q8 defaults to synthetic anchor/extraction fixtures. Do not claim real PDF/EPUB stability without authorized, measured public/nonpersonal corpus evidence.
- Q6 blocks only its named research-transcript acceptance/corpus finalization. Q7 blocks paid/selected semantic work. Q9 blocks no code but forbids unilateral visibility changes. Q10 blocks token/workflow-permission hardening only. D-014 blocks calculation-engine decisions only; mathematical reading, raw notes and diagrams continue.
- No structured tags, compulsory concept/fact/quote classification, forced research funnel, review queue in runtime, or generative model in the Arivo product pipeline.
- D-010 remains: no keystroke/mouse traces, search-query history or agent-prompt history. Only approved explicit actions, reading sessions and coarse position/dwell behavior may exist.
- Product agents use one authorized API/MCP adapter path and never directly access the database. Harness/migration/admin roles are not a product-agent exception.
- Purge/backup contract remains the adopted D-029 contract. Do not reopen it or claim physical erasure without its separate conditions.

No current question blocks unrelated safe work. No silent answer to one question is allowed just because a later slice would be simpler.

---

## 4. Complete H-01 properly: three bounded concerns, no third generic phase

H-01 is not complete after H-01a. It is complete only when the relevant trusted execution/falsification claims are true at their stated boundaries. Each sub-slice gets a current claim, disjoint file scope, explicit red-before-green evidence, independent verifier, Proof Sheet, post-merge CI and clean state closure. Allocate IDs from fresh repository state. Do not hard-code claim numbers from this message.

### H-01b — trusted candidate-tool execution floor (A03)

This is the next core engineering behavior. Its purpose is not merely to change an import statement; it is to make the base-controlled floor genuinely observe whether candidate tools reject the base-controlled mutations.

Current defect model: the anchored mutation suite imports candidate `verify_canonical_layer` in the same process. Candidate import-time code can exit success before cases run, replace verdict objects, or modify later copied anchored tools in the writable candidate checkout after checksum verification. A successful process exit is not proof that every expected case ran. A copied file hash at one time is not a runtime trust boundary.

Before code, publish a small card with named current files, exact allowed scope, expected test count/semantics, data flow, failure codes and test fixture strategy. Keep it within size limits; split only by behavior, not arbitrarily. The implementation must satisfy all of these:

1. The base-owned runner and its critical dependencies remain outside candidate-controlled writable/import resolution. Candidate code must not be imported inside the trusted runner process.
2. Each candidate mutation is executed in a fresh candidate fixture/child process or other resettable boundary so one candidate side effect cannot affect later cases. The base runner must compare actual expected outcome, child exit status and an explicit completion manifest/case count, not accept any exception, printed string or exit 0 as "caught."
3. Candidate code can be exercised as candidate code, but a candidate cannot replace the base runner, mutate later anchors, or cause omitted cases to appear green. Make each fixture disposable and verify trusted runner/integrity inputs before every test where appropriate.
4. Preserve existing base semantics/counts unless a deliberate, separately justified changeset updates the contract and tests. Do not delete tests or reduce mutation coverage to make a floor green.
5. The CI workflow must run the real hardened base floor over a candidate PR. Ensure trusted code has an auditable base SHA/digest and candidate input revision. Do not pretend this supplies OS-level sandboxing or solves Q10.

Commit tests first and observe meaningful RED. Include at minimum:

- candidate module exits `SystemExit(0)` on import;
- candidate has an always-green standalone entry point;
- candidate import/execution attempts to edit a later anchored judge/dependency;
- candidate crashes or produces incomplete case results;
- candidate prints expected words/codes but returns success;
- coordinated candidate verifier plus candidate-owned test weakening;
- missing trusted runner/input;
- a positive valid candidate run completing all expected cases.

The acceptance oracle is a trusted runner result with per-case actual outcomes, not only a test subprocess that did not crash. Run normal and adversarial fixtures through the same integration path CI uses. Then have a fresh technical verifier inspect the diff/evidence independently. Write down the residual boundary: a same-host CI runner is not a malicious-code sandbox.

### H-01c — close remaining integrity-floor gaps, split by coherent behavior

Do not use "H-01c" as a license to bundle all audit findings. Create one or more disjoint cards from the following set after fresh source review.

#### H-01c-claims: claim parser/exclusivity truthfulness (A11)

The current parser/fixture behaviors must fail closed for malformed active registry state. Correct, regression-test and review:

- missing or malformed Open claims section/table/header;
- malformed/truncated competing rows that currently disappear from validation;
- normalized numeric INT reservations, including `INT-125` versus `INT-0125`;
- duplicate claim ID and duplicate branch ownership;
- exact shared-path semantics, so lookalikes such as `STATE.md.py` are not shared;
- declared shared-append edits that are destructive rather than append/re-derivation-shaped;
- self-contained known-bad fixtures for empty, unrelated and populated registries;
- true duplicate-reservation and true overlap probes, not incidental failures for a different reason.

Do not claim a Markdown file atomically reserves work across agents. It cannot. The live GitHub PR state and protected merge path serialize merges; the registry is an integrity check and coordination protocol. Preserve that residual honestly.

#### H-01c-authority: raw manifest/quote lineage (A12/A17)

A raw source + candidate manifest reanchor must not pass merely because the candidate changed both. Create trusted-base comparison rules that bind each protected raw file to its approved prior digest/row. Any legitimate new source, approved reanchor or sourced supersession needs an explicit, distinguishable owner-authorized path; it must not be indistinguishable from an ordinary candidate rewrite. Test coordinated raw+manifest mutation, digest moved to a wrong row, missing record, raw deletion/addition and allowed append behavior.

Also make raw-cited quote validation fail closed when the source metadata exists but no supported quotation is extracted. Test straight and supported non-straight quote forms plus fabricated curly-quote content. Do not alter actual owner raw files to satisfy a test, and do not overclaim coverage for chat-source limitations that are separately documented.

#### H-01c-evidence/privacy: evidence/red-redaction boundaries (A15/A18 and narrow A16)

Repair red records so a current hash alone cannot certify an unobserved/removed assertion. A red record needs a typed observed red result, relevant predecessor/candidate revision, approved amendment semantics, and test suite inclusion. A new test file must not evade red/required-suite obligations simply because Makefile discovery and gate lists differ.

Repair diagnostics so secret-shaped remote names/environment keys are redacted in stdout and stderr with synthetic canaries only. Preserve useful error class; never test real credentials.

A16 scope/size/boundary lint is deliberately bounded static detection. Close the specific current misclaims: deletion-only size counting; actually enforced versus merely declared limits; aliased/from-import ambient calls and relevant environment/network access. Do not build a universal Python security analyzer. If a desired check cannot be enforced, narrow its claim and leave a concrete reopening trigger.

H-01c may overlap H-01b only through explicitly shared append records. Otherwise use disjoint claims/branches. Finish all H-01 trust behavior that the product relies on before saying the H-01 phase is complete.

---

## 5. H-02: make systems-engineering review evidence real, not ceremonial

H-02 design and red-first work can proceed in parallel with H-01b only under disjoint claims. It cannot be activated/merged as a trusted merge gate until the H-01b base floor can judge its validator/gate path. If branches stack, resolve by fresh rebase/diff/evidence reruns; no forced push or stale SEV reuse.

H-02 must implement one standard-library SEV schema, parser and actual gate integration. The SEV report is a reviewable evidence object, not a string-shaped ritual. Required fields at minimum:

- slice/claim, base SHA, candidate/review SHA and reviewed-diff digest;
- owner INT/decision, SYS/claim references, changed components/interfaces and declared scope;
- component, integration, system and user-validation evidence IDs, each with exact revision/run/fixture relationship;
- failure modes/controls, known-bad/mutation evidence, findings/disposition, explicit nonempty not-verified list;
- builder/reviewer context identifiers, identity limitations and PASS/BLOCKED outcome;
- P0/P1 findings that mechanically prevent PASS.

The reviewed-diff digest must include relevant implementation and tests while excluding only narrowly documented generated/self-referential SEV/Proof Sheet artifacts. It must not exclude code under review. Base or candidate movement makes a report stale. Validate file/revision/digest existence and evidence shape where mechanics can, but do not falsely claim a field establishes genuine independent human judgment.

Repair the linked A09 proof/evidence weaknesses at the same boundary:

- validate run-record schema and full digest syntax; do not accept prose as SHA-256;
- bind each record to revision and sufficiently preserved output/artifact/reference to make a digest meaningful;
- distinguish expected RED evidence from successful acceptance evidence;
- reject whitespace/placeholder Not-verified lists and require an explicit, honest statement;
- bind every relevant record, not just a truncated digest or last record;
- preserve malformed historical records as historical artifacts with a disposition, not forged replacement evidence.

A08 is broader than a formatting issue. For new product/migration tests, independently successful, nonempty oracles must compare the authoritative/security-relevant outcome actually claimed. Do not call a row count a recovery equality proof. Put baseline evidence/oracle requirements in H-02 and enforce the concrete content/schema/reference oracle in the applicable P3 card.

Red-first known-bads must exercise the public validator and actual gate caller, not an internal duplicate implementation. Required rejections include: missing report; malformed report; stale base/diff; missing intent/SYS trace; absent/invalid evidence; changed code after review; nonempty P0/P1 falsely marked PASS; same declared builder/reviewer where policy says it is disallowed; validator/test coordination weakening; omitted gate invocation; malformed proof/run records; placeholder limitations. H-02's own transition review must be explicitly bootstrap-scoped and independently checked; it cannot be a permanent opt-out.

Once live, a slice does not merge with missing, stale, blocked or P0/P1 SEV. Before it is live, use the existing independent technical review discipline but label it as not mechanically enforced.

---

## 6. Product-entry prerequisites: fix inherited harness patterns before product schemas reuse them

Do not start product schema migration just because H-01a is green. The product kernel must not copy known-bad test harness conventions.

### P3-M0 / migration-oracle prerequisite (A05/A06 and applicable A08)

Before any product domain migration depends on the runner:

- reject transaction control in migration text or otherwise enforce a proven transaction-safe migration language. An embedded `COMMIT` must never persist partial effects while the runner reports a rollback;
- test normal multi-statement failure and embedded transaction-control failure in disposable PostgreSQL, verifying zero effects and zero bookkeeping for a refused migration;
- verify migration directory/ledger history bidirectionally: missing previously applied tail/interior file, empty directory, gapped sequence, extra ledger entry and edited retained file must each have clear behavior;
- make verification observation-only after bootstrap or declare its bootstrap side effect separately; it must not create bookkeeping under a claimed read-only verify;
- strengthen recovery/schema oracles to compare actual preserved values, security schema/RLS/policies/constraints as relevant, and nonempty successful independent reads.

This is a defect-bound product prerequisite, not a general database framework. It needs its own card, real PostgreSQL and independent reader. No destructive production database operation.

### P3-K0 / kernel primitive prerequisite (A04/A07/A13)

Before a product command is accepted:

- replace delimiter concatenation with unambiguous canonical versioned structured request encoding. Include command, owner/actor/client/key and all effect-bearing fields unambiguously. Test the exact separator collision from the audit plus Unicode/normalization/boundary cases. Same key/same canonical body returns the same result; same key/different canonical body returns a stable conflict with no effect;
- correct UUID variant/version generation and add controlled-randomness tests for version, variant, timestamp ordering/extraction and compatibility. Do not rewrite existing persisted test IDs without a compatibility decision;
- route product connection/configuration and named errors through the approved adapter boundary. No direct `psql` path that can select a different socket/database than migrations; missing client, timeout, connection refusal and target mismatch must yield stable no-ACK refusal;
- make concurrent same-key semantics explicit and tested. A unique constraint can prevent duplicate committed effects, but it does not by itself promise the racing caller a stable replay result. Define either same recorded result or an explicit retryable in-flight state. Sequential crash tests are not concurrency proof.

This may be folded into P3-01 only if its scope/acceptance stays small. Otherwise create a named P3-K0 prerequisite card and immediately follow it with P3-01. Do not hide it as more generic guard work.

---

## 7. P3-00 then P3-01: begin the actual product only when their gates are true

### P3-00: requirements/interfaces/state-machine freeze

After H-01 is complete and H-02 is live, create the one canonical requirements traceability matrix. It must connect owner source/INT -> C1-C5 -> measurable SYS requirement -> normal/failure scenario -> component/interface -> design choice -> red and acceptance tests -> component/integration/system/validation evidence -> revision/fixture/run -> current status and explicit limit. Do not duplicate the matrix into STATE.

Create data and state machines for:

- logical Work / particular Source / source byte identity / import job / extraction generation / Passage / Anchor;
- stable Highlight/Bookmark/Note identities and append-only revisions/current view/tombstone/purge;
- authenticated owner/actor/provenance/idempotent command path;
- local capture/outbox, server command/outbox, acknowledgment and retry states;
- keyword index publication/invalidation;
- export/restore and purge ledger application.

Prepare anchor/extraction measurement before freezing the applicable anchor structure. Q8's synthetic default is acceptable for deterministic baseline work but cannot prove PDF/EPUB behavior. Preserve raw fixture bytes/measurements and record exactly what is unmeasured. Keep Q11/Q12 visible at the exact fields they block. A provider-neutral kernel and abstract verified-blob state can proceed; actual provider storage schema/durability promise cannot be smuggled in.

P3-00 also creates the compact threat/failure review: cross-owner references, forged actor/owner inputs, hostile imported content, stale/ambiguous anchors, partial cross-store state, destructive restore, indexes becoming authoritative, source recreation after purge, and agent-context leakage. Do not introduce a new formal methods platform; specify high-value invariants and executable state/fault transitions.

No product schema migration lands before this P3-00 gate is reviewed with a real SEV and no P0/P1. A plan document alone is not proof of P3-00.

### P3-01: first real product kernel and command

P3-01 must be a typed, authenticated, attributed product behavior—not a second arbitrary `evidence_event` wrapper. Use P3-K0/M0 results. Implement only the minimum needed for the next capture path:

- typed stable IDs; authorized owner and actor derived from trusted request context rather than a CLI flag/GUC; provenance and source of authority;
- canonical command/idempotency/result/error contracts, transaction boundary, current/revision/tombstone primitive and one repository/API access path;
- real domain-facing operation under a provider-neutral baseline, with future Work/Source/Anchor dependencies deliberately declared rather than faked;
- test missing/forged/expired/over-scoped authority, cross-owner read/write/reference, identical replay, changed-body reuse, concurrent same-key request, crash before/after commit/lost acknowledgment, no direct product-agent DB credentials, and adapter-bound ambient time/ID use.

Acknowledge only actual committed durability state. A test-only RLS GUC and caller-supplied owner string are not production authentication. Independent read proves exact owner-scoped authoritative state and command/result linkage.

Then continue the existing Phase 3 sequence without skipping proof: P3-02 Work/Source intake; P3-03 extraction/anchors; P3-04 Highlight; P3-05 Bookmark; P3-06 deep Note; P3-07 keyword; P3-08 local/cloud outbox; P3-09 export/restore/integrated durable proof. The early vertical checkpoint remains: import one permitted document -> capture one anchored passage -> lose ack/restart/replay -> retrieve exact same capture/history/source through a real external client boundary. That is a checkpoint, not Phase-3 completion.

---

## 8. Horizon after Phase 3: maintain the destination without pretending it is built

Keep the existing Phase 4/5 outcome rows as source of truth. Do not invent new phase IDs or code simply to claim forward motion.

Phase 4 is the first usable research workflow: incrementally supported readable formats; reader/API position and capture boundary; library/reading lists/current reading; approved coarse session behavior; margin notes; source-optional creative/raw journal blocks; stable @ references; baseline scoped agent reads; recovery and genuine workflow validation. The real gate is import -> read -> highlight/bookmark -> deep note/journal reference -> offline/restart -> retrieve/reopen the same passage/thought. A CLI is only a contract client, not the reader. Missing reader/journal host means product UI validation is [blocked], not silently passed.

Phase 5 is grounded retrieval/compounding: D-034 classification-word pre-gate; API/context packs with provenance/budgets/untrusted marking; pre-registered evaluation corpus/holdout; Q7-bounded semantic spike; versioned vector/index generations; hybrid retrieval/why; relationship candidates distinct from grounded evidence; concepts with independent out-of-sample graduation; Kev bounded non-generative policy/evaluation; deterministic, semantic and graph C3 probes separately. Kev-backed relation promotion/concept graduation/graph proof must wait for approved Kev policy/evaluation. Explicit structural facts and provisional discovery can proceed only with their already-valid evidence contract.

Never turn similarity, a model score, an agent statement, duplicate imports or repeated generated output into independent corroboration. No generic LLM summary/RAG substitute is permitted. Every derived item must retain inputs, run/config lineage, owner scope, revision, invalidation/rebuild and purge behavior.

---

## 9. Mandatory V-model and evidence discipline for every claim

For each slice:

1. Re-read fresh main, current claims, relevant owner intent/open decision and actual dependency state.
2. Claim before consequential work, one claim/branch/PR, no overlapping non-shared scope. Do not treat the registry as an atomic distributed lock.
3. Freeze one behavior, ≤ current requirement-ID limit, explicit non-goals, exact accepted/must-reject cases, named interfaces, failure envelope, file scope and stop conditions.
4. Commit tests first; observe actual RED. A missing-module bootstrap red is not enough when a real predecessor behavior can be exercised.
5. Implement the minimum. No undeclared dependency, second kernel or direct DB bypass.
6. Run the real stack plus independent nonempty state/oracle reads. Preserve inputs/outputs/fixtures/digests, not prose-only evidence.
7. Fresh technical verifier who did not implement reviews code and reproducible evidence.
8. After H-02 activation, separate SEV checks intent -> requirement -> interface/design -> component/integration/system/user-validation evidence, actual residuals and V-model level proven. It cannot answer owner questions.
9. Gate/Proof Sheet/remote CI at the candidate revision; post-merge CI at final main; if main moved, rebase/recompute/rerun.
10. Close claims, STATE and session/worklog accurately. A PR merged is not a license to leave an open claim or an in-progress record behind.

No green test count substitutes for its assertions. No passing PR converts proposed architecture into user validation. No context label cryptographically proves reviewer independence. P0/P1 blocks. P2 needs the actual recorded decision/disposition, not silent debt.

---

## 10. What I expect at the next handoff

Do not respond with another generic plan. First report briefly:

- exact fresh main SHA/PR/protection/CI state and actual preflight results;
- the CLAIM-006/session-20 reconciliation disposition;
- whether the narrow H-01a completion checks reproduced or were rejected by evidence;
- current claims/branches and the exact disjoint cards selected for H-01b, H-01c and H-02;
- named owner blockers only, with safe work continuing around them.

Then execute the ready reconciliation and H-01b/H-01c/H-02 cards under the rules above. Keep a concise cumulative table: finding -> static/reproduced/fixed/CI-proven/remaining limit -> regression/evidence pointer. Do not erase the original audit wording or historical malformed evidence. Append honest dispositions.

Final goal remains non-negotiable: preserve a piece of meaningful study through interruption and recovery, return it with exact origin and raw thought, and eventually show new grounded evidence making prior work more useful. The infrastructure exists to make that result defensible, not to displace it.

(End of owner turn 21 verbatim. Section numbering and typography preserved as received, including the directive's own internal section sequence and its em-dash conventions. No access token travelled with this turn; nothing was redacted at ingestion. A byte-level mechanical diff against the original message was not possible from this host — transcribed through the session context — the standing limit, stated in every not-verified list.)

## 2. Starting state (observed this session — evidence labels per GLOSSARY)

- **[observed live]** remote main = local main = `2087378ba0268a72fd5ee82ae8e99d1534cc443b` after fetch (the SHA the directive's §1 review named); protection required = [canonical-layer, head-tools, harness], strict, admins included, no force-push; 0 open PRs, 0 open issues; latest post-merge run `39259609210` success at main; PRs #39 (`6cdd458`), #40 (`746fa57`), #41 (`2087378`) all merged. Token verified live by use (gh CLI absent in this environment — the GitHub API was read directly; no credential value printed).
- **[verified by run]** the seven-command P2-CLOSE preflight all GREEN at `2087378`, this session, this environment: verifier 51/0 exit 0 · selftest 30/30 · isolation GREEN · isolation selftest green (redaction path tested) · ARV-RIG-001 (rig REBUILT user-space this session — the prior rig did not survive the environment reset, as the directive predicted it might not: Debian 17.11-0+deb13u1 packages downloaded and extracted without root, `initdb` at port 5433, fresh cluster; `make migrate` applied 3 migrations; `make verify-schema` OK, checksums match) · `make verify` GREEN (all four declared suites + 13/13 known-bads + gate selfcheck + canonical 51/0).
- **[observed live]** the §1 status drift CONFIRMED exactly as the directive stated: PR #41 merged, 0 open PRs, yet CLAIMS.md listed CLAIM-006 open, STATE called CLAIM-006 OPEN the active task, record 20 said IN PROGRESS. Repaired FIRST by CLAIM-007 (PR #42, merged `e78ac8b`, CI run `39268010523` all three checks success at head `1a4607f`): the late closed row by the rule-4 method (the CLAIM-003 precedent; record 20 §12 itself predicted this reconciliation item), record 20 → COMPLETE for the work it contains with an append-only §12 amendment, STATE re-derived. Session 20's four wall-catches and §8 failure log preserved untouched.
- **[reproduced, disposable clone]** the §2 H-01a completion check #1: gate.py:191's claim-coverage `scope.diff_paths(a.diff)` recompute sits OUTSIDE the GitRefusal handler — with the diff base deleted, the gate prints ONE clean `ARV-DIFF-001` refusal inside `check_diffs` and then CRASHES with an uncaught `GitRefusal` traceback (exit 1 by process failure; the refusal printed twice: once as the named disposition, once as the crash message). Defect CONFIRMED — not counterevidence. The sub-slice's RED form is this exact observed wrong behavior through the actual caller (dispatch.py).
- **[static, confirmed]** the §2 H-01a completion check #2: `test_gate_dispatch.py` line 141 asserts the broad string `ARV-PRF` while the frozen H-01a card names the exact code `ARV-PRF-002`; and the hostile-branch fixture `slice/x"; echo ARV_PWNED_MARKER; "y` contains spaces — NOT a `git check-ref-format`-legal ref (the dispatcher's refusal is correct, but the case is parser-boundary fuzzing, not an observed Git-ref attack path). Tightening + relabeling + a genuinely-legal hostile case are the sub-slice's work.
- **[static, confirmed]** A03, A11, A12/A17, A15/A18/A16, A09/A08, A04/A07/A13, A05/A06 all remain at their record-20 §2 confirmations — no new dynamic reproduction this session beyond the two H-01a residuals above; their cards are refreshed in PLAN per this turn's §4–§6.
- **Wall catch this session (the system working):** VER-901 refused the reconciliation slice's own STATE draft — a forward reference to an un-minted `INT-126` (the fabricated-authority class). Repaired to "next INT at ledger-max+1, allocated at the intake claim." The un-minted ID is properly minted only NOW, in this intake slice, per the registry's one-at-a-time rule.

## 3. Task and scope (this slice: INTAKE ONLY — CLAIM-008)

**Task:** import owner turn 21 faithfully (this record §1, verbatim) + reserve INT-126 + record D-040 (the directive's operational adoption) + refresh PLAN's active-phase card set per the turn's §2/§4/§5/§6 (the H-01a completion sub-slice card; the H-01b card with the turn's five-point contract; the H-01c split into three coherent cards; the H-02 card extended with the A09 repairs, the reviewed-diff digest rules, the bootstrap-scoped transition and the H-01b activation dependency; the P3-M0/P3-K0 prerequisite cards) + STATE/AGENTS count sync + CLAIM-007's prompt closed row. Non-goals: NO code changes this slice (the H-01a sub-slice, H-01b, H-01c, H-02 are their own claims); no wall/weakening changes; no raw/ edits; no visibility change (Q9); no reopening of closed decisions; no new laws; no resolution of Q6–Q12/D-014.

**The active-phase card set this directive authorizes** (each a separate claim per D-038/LAW-31; the ready slice first; claim numbers allocated from fresh state at open time, never hard-coded from the turn's text):
- **H-01a-R** (ready, first): the bounded completion-check sub-slice — the consolidated gate refusal + subprocess-timeout named refusal (ARV-DIFF-003 or the narrowed contract) + the ARV-PRF-002 exact-code tightening + the check-ref-format-verified hostile case. Tests first on the observed wrong behavior; smallest repair.
- **H-01b** (next core): the trusted candidate-tool execution floor (A03) per the turn's five-point contract + eight RED cases + the CI real-floor requirement + the stated residual boundary (same-host CI ≠ malicious-code sandbox).
- **H-01c-claims / H-01c-authority / H-01c-evidence** (disjoint cards, A11/A12+A17/A15+A18+narrow-A16): the registry parser fail-closed set; the raw manifest/quote lineage binding; the red-record/redaction repairs. Overlap with H-01b only through explicitly shared append records.
- **H-02** (parallelizable DESIGN/red-first under disjoint claims; ACTIVATION gated on H-01b's floor being able to judge its validator/gate path): the SEV schema/validator/gate with the turn's required-field list, the A09 repairs at the same boundary, the red-first known-bad rejection list, the bootstrap-scoped transition review.
- **P3-M0 / P3-K0** (product-entry prerequisites, with P3-00/P3-01): the migration-oracle card (A05/A06 + applicable A08) and the kernel-primitives card (A04/A07/A13) — product schema/kernel work may not inherit the known-bad harness conventions.
- **P3-00 / P3-01** (after H-01 complete + H-02 live): the RTM + state machines + anchor measurement + threat review; then the first real product kernel command.

**Owner decision list (§3 boundaries, standing):** D-014, Q6, Q7, Q8, Q9, Q10, Q11, Q12 — each blocks ONLY its named dependents; no silent answers; no gate is a general stop-work permission. This turn adds NO new owner question and closes none.

Sections §4–§12 complete at this session's close slice (the slices above are the session's remaining work; every merge carries the three-wall CI proof; the close records actual commands, run IDs, and the dispositions actually achieved this session).
