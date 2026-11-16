# KEV
## System Engineering Specification, Architecture, V-Model, Roadmap, and Execution Protocol

**Document status:** Initial product and engineering baseline  
**Date:** 16 November 2026  
**Product:** Kev, the autonomous knowledge-base maintainer and creator for Arivoo  
**Repository:** A new, separate repository to be created for Kev  
**Primary language recommendation:** Python  
**Database platform:** Supabase / PostgreSQL  
**Model strategy:** Provider-independent, free-API-first, small and fast reasoning models with primary and fallback providers

---

# 0. Executive definition

Kev is an autonomous knowledge-maintenance and knowledge-creation system that continuously operates on Arivoo's knowledge base.

Its responsibility is to keep the knowledge base healthy, organized, connected, useful, and continuously growing. It should do this without requiring the owner to issue maintenance commands, approve routine actions, classify every object, or interrupt normal work.

The owner uses Arivoo naturally: reading, importing, highlighting, underlining, writing notes, creating journal entries, drawing whiteboards, building maps, making research blueprints, and revising existing material. Those activities should create the information and events Kev needs. Kev should then work asynchronously in the background.

Kev retrieves relevant existing knowledge, interprets new material, identifies concepts and relationships, detects duplicates and contradictions, proposes or performs safe knowledge operations, verifies the results, records what happened, and uses feedback and evaluation results to improve future decisions.

Kev also has an external-discovery responsibility. It may research information outside Arivoo, bring useful findings back into the knowledge base, and connect those findings to existing knowledge. External information must remain distinguishable from owner-created material and must preserve source, date, retrieval context, and evidence.

The core product relationship is:

- **Arivoo owns the knowledge and its durable authored state.** It remains the system of record for sources, notes, highlights, journal material, reading activity, references, and user-created knowledge objects.
- **Kev owns the autonomous maintenance process.** It observes events, retrieves context, makes bounded decisions, evaluates them, and issues authorized changes through stable Arivoo interfaces.
- **The model supplies judgment, not authority.** It interprets evidence and proposes structured decisions. The harness controls tools, permissions, validation, retries, execution, provenance, and evaluation.
- **Supabase supplies hosted PostgreSQL and object storage infrastructure.** It does not replace Arivoo's domain model or become an excuse to duplicate its data model.

The central product promise is **zero-friction knowledge compounding**: the owner's normal activity should continuously improve the knowledge base without the owner having to operate a second workflow.

## 0.1 Non-negotiable principles

1. No routine approval prompts. Routine, reversible, evidence-backed knowledge maintenance happens automatically.
2. No model-owned database authority. Models cannot issue arbitrary SQL, access unrestricted credentials, or bypass the harness.
3. No unsupported facts promoted as established knowledge. Uncertainty is represented explicitly.
4. No loss of original material through reorganization. Derived organization can evolve; source content and authored history remain preserved.
5. No provider lock-in. Any compatible model provider can be swapped without redesigning the agent runtime or decision contracts.
6. No blocking the owner's workflow. Arivoo writes first; Kev processes asynchronously.
7. No silent destructive actions. Permanent deletion, destructive identity merges, and irreversible source changes are not routine autonomous operations.
8. No self-grading as the only evidence of quality. Deterministic checks, fixed evaluation cases, provenance checks, and held-out tests independently evaluate model decisions.
9. No architecture hidden inside prompts. The runtime, policies, tools, and state transitions are explicit, inspectable, versioned software.
10. No premature multi-agent swarm. Begin with one controller and modular capabilities. Parallel workers can be introduced only when measured throughput or isolation needs justify them.

---

# 1. Product intent and operating model

## 1.1 Owner experience

The owner should not have to think about Kev during ordinary use.

Example: the owner reads a paper and highlights three passages. They write a note, add a concept to a map, and make a research blueprint. Arivoo commits those changes. The same transaction, or a reliable event mechanism associated with it, makes the changes visible to Kev.

Kev then:

1. Receives and deduplicates the events.
2. Identifies which knowledge objects changed and their revisions.
3. Retrieves relevant existing material rather than scanning the entire database.
4. Builds a bounded evidence package with identifiers, revisions, provenance, and trust labels.
5. Decides which maintenance and creation operations are useful.
6. Validates every proposed operation against deterministic policy and evidence rules.
7. Executes eligible operations using Arivoo's supported write interface.
8. Verifies the resulting database state.
9. Records the decision, evidence, model/provider, policy version, operation, and verification result.
10. Schedules further work only when the result or unresolved dependency justifies it.

The owner does not click an approval button for routine operations. Kev must achieve safety through constrained authority, reversibility, provenance, and automated verification.

## 1.2 What “autonomous” means

Autonomy does not mean granting a model unrestricted database access. It means the system can complete a defined maintenance task without requiring a human to supervise each step.

Kev should autonomously:

- classify material and identify candidate concepts;
- detect possible duplicate or overlapping concepts;
- maintain aliases and concept descriptions;
- discover relationships between sources, concepts, claims, notes, and projects;
- distinguish evidence-backed relations from hypotheses;
- generate and revise derived summaries;
- detect contradictions and preserve both sides with provenance;
- identify stale, incomplete, or broken derived structures;
- update retrieval metadata and search aids;
- research external material when a task or configured discovery policy calls for it;
- decide to abstain when the evidence is insufficient;
- retry transient failures and fall back between model providers;
- measure its own decision quality against fixed tests and observed outcomes.

Kev should not autonomously:

- permanently delete original sources, owner-authored notes, or historical revisions;
- rewrite original source text;
- silently merge two distinct source identities or works;
- turn semantic similarity into factual truth;
- present external material as though the owner supplied it;
- alter database permissions, authentication rules, RLS policies, secrets, migrations, or its own production code through ordinary knowledge-maintenance tools;
- change evaluation thresholds after seeing a result merely to make the result pass.

## 1.3 Knowledge-base health

“Healthy” means more than having no database errors. Kev should maintain several dimensions:

- **Integrity:** references resolve, revisions are valid, identities are stable, no unintended dangling relations exist.
- **Provenance:** derived claims and relations point to the exact source revision and evidence location that supports them.
- **Coherence:** concepts are understandable, aliases are managed, contradictory claims remain visible, and duplicate structures are detected without destroying distinctions.
- **Retrievability:** old information can be found again when new information or a new question makes it relevant.
- **Freshness:** derived summaries and indices are regenerated when their dependencies change.
- **Coverage:** important topics and research threads can reveal missing links or underdeveloped areas without pretending that every gap must be filled.
- **Reversibility:** organization can evolve without losing original information or historical decisions.
- **Operational reliability:** events are not silently lost; failures can retry; stuck work is observable; model outages do not block Arivoo.

---

# 2. System boundary and repository separation

## 2.1 Separate repositories

Kev must be developed in a new repository, separate from Arivoo.

Arivoo remains the canonical knowledge backend. Kev is a client and autonomous maintenance service that integrates through stable, authorized interfaces. Kev must not copy Arivoo's entire domain model into a second independent source of truth.

The two repositories have different responsibilities:

| Area | Arivoo | Kev |
|---|---|---|
| Original sources and binary references | Owns | Reads through authorized interfaces |
| Notes, highlights, journal, reading objects | Owns | Reads and may request supported derived updates |
| Canonical work/source identity | Owns | Respects; never silently invents merges |
| Knowledge concepts and relations | Owns or hosts the canonical durable representation according to Arivoo's accepted schema | Reasons about, proposes, maintains through supported operations |
| Agent runtime and scheduling | Emits events / exposes interfaces | Owns |
| Model-provider adapters | Not required | Owns |
| Decision policies | Domain constraints and contracts | Agent decision policies, versioned and evaluated |
| Evaluation corpus for Kev decisions | Provides fixtures and real knowledge objects | Owns decision and system-level evaluation harness |
| Model call logs and decision traces | May store domain-linked references | Owns operational records |
| Object storage | Owns source-file contract | Uses supported access paths |

## 2.2 Integration rule

Before implementing integration, the Kev builder must inspect the current Arivoo repository at its live `main` head. The builder must read the canonical onboarding and execution instructions and inspect the actual schema, migrations, query/command interfaces, retrieval API, MCP tools, authorization model, and current plan.

Do not infer interface names or database tables from this document. This document defines desired behavior, not undocumented existing APIs.

The integration layer must be written against the actual Arivoo contracts discovered during preflight. If required capabilities are absent, create a bounded Arivoo-side integration claim and implement the missing contract there; do not bypass the repository's change protocol or write directly into unknown tables.

## 2.3 Existing Arivoo baseline (observed 16 November 2026)

At the time this specification was written, Arivoo's Phase 4 backend exit gate had been recorded as 18/18 verified. Phase 5A authorized retrieval/context packs, Phase 5B an evaluation corpus, and Phase 5C a deterministic semantic-search experiment had landed.

Important limitation: the landed P5-C experiment is not a production semantic understanding system. It uses a local deterministic token-multiset representation and similarity ordering over the existing retrieval arm's admitted set. Its engineering record explicitly discloses that it cannot make the required near-miss semantic exclusion. Real semantic quality, external embeddings, and a real embedding backend remain unverified. This is why Kev should own the broader decision and maintenance loop rather than being equated with the existing semantic spike.

The Arivoo plan still contains subsequent work for versioned semantic indexing, hybrid retrieval, relationship discovery, concept formation, Kev policy/evaluation, user-value validation, and final integration. Kev's architecture must preserve these dependencies and must not claim they are complete merely because the harness exists.

Evidence pointers:

- Arivoo repository: https://github.com/prathamarchives/Arivoo
- Arivoo plan: https://github.com/prathamarchives/Arivoo/blob/main/PLAN.md
- P5-C semantic spike record: https://github.com/prathamarchives/Arivoo/blob/main/context/extracted/74-P5C-SEMANTIC-SPIKE.md
- P5-C implementation: https://github.com/prathamarchives/Arivoo/blob/main/harness/semantic.py
- P5-C acceptance proofsheet: https://github.com/prathamarchives/Arivoo/blob/main/harness/runs/claim-082-p5c-semantic-spike/proofsheet.md

This baseline is a snapshot. Always refresh GitHub before consequential integration work.

---

# 3. Functional requirements

These requirements are the initial product baseline. Every requirement must eventually map to implementation components, interfaces, and one or more verification cases in the Requirements Traceability Matrix.

## 3.1 Continuous operation and event processing

**KEV-FR-001 — Event intake.** Kev shall receive events for relevant Arivoo changes, including source creation/import, source revision, note creation/revision, highlight creation, bookmark changes, journal changes, reading-state changes, whiteboard/map/blueprint changes, and supported deletion or tombstone events.

**KEV-FR-002 — Non-blocking owner activity.** The owner-facing Arivoo operation shall not wait for Kev's model calls or knowledge-maintenance work to finish.

**KEV-FR-003 — Durable processing.** Every committed source event shall either be available for processing or be recorded as intentionally superseded, deduplicated, or rejected with a reason. A worker crash must not silently lose committed work.

**KEV-FR-004 — Idempotency.** Reprocessing the same event, delivery, or task shall not create duplicate concepts, duplicate relations, duplicate summaries, or duplicate external-source imports.

**KEV-FR-005 — Coalescing.** Closely spaced changes to the same object may be coalesced into a task for the latest valid revision, while preserving an audit trail of the underlying events.

**KEV-FR-006 — Priority.** Kev shall distinguish latency-sensitive small tasks from larger background enrichment or external research tasks.

**KEV-FR-007 — Recovery.** Failed or interrupted work shall resume from a known state using bounded retries and explicit dead-letter or needs-attention states.

## 3.2 Retrieval and evidence construction

**KEV-FR-010 — Contextual retrieval.** Kev shall retrieve relevant material from Arivoo through authorized retrieval interfaces. It shall prefer bounded, evidence-rich context over unrestricted full-database dumps.

**KEV-FR-011 — Provenance preservation.** Each retrieved item shall retain its canonical object ID, revision/version, source identity, evidence location where available, trust classification, and origin.

**KEV-FR-012 — Retrieval diversity.** Retrieval may use exact keyword, metadata filters, temporal context, existing relations, semantic retrieval, and other supported query arms. The runtime shall not depend on any one retrieval mechanism.

**KEV-FR-013 — Evidence sufficiency.** A decision must state which retrieved items and evidence spans support it. If evidence cannot be located or is insufficient, Kev shall abstain or record a tentative discovery.

**KEV-FR-014 — Context budget.** Context packages shall be bounded by configurable token and item limits. Large material should be summarized or chunked with stable references instead of blindly truncated.

## 3.3 Knowledge creation and organization

**KEV-FR-020 — Concept discovery.** Kev shall identify candidate concepts from new and existing knowledge, with definitions grounded in source evidence.

**KEV-FR-021 — Concept identity.** Concepts shall have stable identifiers independent of their names. Names and aliases may change without erasing identity history.

**KEV-FR-022 — Alias maintenance.** Kev shall identify possible aliases and alternate expressions, but must retain evidence and an audit trail for alias assignment, correction, split, or merge.

**KEV-FR-023 — Relationship discovery.** Kev shall discover candidate relations between sources, claims, concepts, notes, research projects, and other supported objects.

**KEV-FR-024 — Typed relations.** Relations shall use a bounded, documented vocabulary. Each type shall have a clear meaning, directionality rule, evidence requirement, and permitted endpoint types.

**KEV-FR-025 — Evidence-backed promotion.** Similarity alone shall never promote a candidate into an established factual relation. Stronger relation states require admissible evidence or an explicit owner action already represented in Arivoo.

**KEV-FR-026 — Contradiction preservation.** Conflicting claims shall be represented as conflicting claims with their respective sources and dates. Kev must not erase or silently choose a winner merely to create a tidy graph.

**KEV-FR-027 — Duplicate detection.** Kev shall distinguish duplicate byte content, duplicate acquisitions, editions, paraphrases, related works, and genuinely different works. It shall not silently merge canonical Work or Source identities.

**KEV-FR-028 — Derived summaries.** Kev may create and revise generated summaries, topic descriptions, concept descriptions, and retrieval aids. Each derived item shall record the exact dependencies and generation/policy version used.

**KEV-FR-029 — Reorganization.** The knowledge base shall be allowed to reorganize continuously as new information changes the best structure. Reorganization must preserve stable identities, source history, and reversible change records.

**KEV-FR-030 — Research structure.** Kev shall maintain and enrich research maps, blueprints, and thematic structures when those object types are supported by Arivoo's canonical interfaces.

## 3.4 External discovery and research

**KEV-FR-040 — External research.** Kev shall be capable of searching and retrieving external information through configurable search and source connectors.

**KEV-FR-041 — Origin separation.** Owner-provided material, Kev-generated material, and externally retrieved material shall remain distinguishable.

**KEV-FR-042 — Citation preservation.** External findings shall preserve source URL, title, publisher/domain, retrieval time, publication date where available, relevant quoted/extracted spans, and content fingerprint where practical.

**KEV-FR-043 — Trust assessment.** Kev shall assess source reliability and evidence quality using explicit policies. It shall not treat the first search result or a model-generated answer as authoritative.

**KEV-FR-044 — Research scope.** External research shall be initiated by a configured task, an explicit research request, or a narrowly defined discovery policy. It must not crawl the internet without limits.

**KEV-FR-045 — External content as untrusted input.** Retrieved pages and documents may contain hostile prompt instructions. They must be passed to the model as quoted/untrusted evidence, not as instructions that override system policy.

## 3.5 Decision quality and learning

**KEV-FR-050 — Structured decisions.** Model outputs shall conform to versioned decision schemas. Free-form prose alone is not an executable instruction.

**KEV-FR-051 — Decision trace.** Each decision shall record task ID, event IDs, relevant object revisions, provider/model, prompt/policy version, evidence references, proposed action, validation results, and final outcome.

**KEV-FR-052 — Outcome evaluation.** Kev shall compare decisions against deterministic constraints, fixed evaluation cases, later owner corrections, and observable task outcomes.

**KEV-FR-053 — Policy improvement.** Kev may propose or automatically adopt bounded changes to non-security decision policies only when the change is evaluated against fixed and held-out tests and remains within its authorized policy envelope.

**KEV-FR-054 — Model substitution.** Providers shall implement a common interface. A provider failure shall not corrupt task state or change the meaning of the decision contract.

**KEV-FR-055 — Quality-aware fallback.** Fallback selection shall consider availability, latency, schema compliance, and measured capability for the specific task class. It shall not assume that all providers have equal quality.

**KEV-FR-056 — No self-certification.** The model making a decision cannot be the only evaluator approving that decision. Independent deterministic and evidence-based checks are required.

---

# 4. Quality attributes and engineering targets

These are initial engineering targets to validate in the first implementation. They are not claims of current performance. Baselines should be measured before thresholds are frozen.

| ID | Attribute | Initial target / constraint |
|---|---|---|
| KEV-NFR-001 | Owner-facing latency | Arivoo writes must not wait for Kev. |
| KEV-NFR-002 | Event-to-first-processing latency | Target p50 under 2 seconds and p95 under 10 seconds when provider and infrastructure are healthy; revise after measurement. |
| KEV-NFR-003 | Routine decision latency | Prefer one fast model call plus deterministic verification; target p50 under 3 seconds after context is ready, subject to provider limits. |
| KEV-NFR-004 | Reliability | Durable queue, idempotent processing, retry, explicit terminal state. |
| KEV-NFR-005 | Availability isolation | Provider outage must not block Arivoo or lose events. |
| KEV-NFR-006 | Security | Least privilege, server-side secrets, explicit database access, tested RLS/grants. |
| KEV-NFR-007 | Auditability | Every state-changing action traceable to evidence, policy, and decision record. |
| KEV-NFR-008 | Reversibility | Derived knowledge changes versioned and reversible; original owner content preserved. |
| KEV-NFR-009 | Portability | Model provider and deployment environment replaceable through adapters. |
| KEV-NFR-010 | Cost discipline | Free API-first; per-provider quotas and request budgets prevent runaway calls. No paid endpoint enabled by default. |
| KEV-NFR-011 | Scalability | Bounded concurrency, batching, and queue backpressure. |
| KEV-NFR-012 | Maintainability | Typed interfaces, small modules, tests, migrations, and documented decisions. |

## 4.1 Fast bounded judgment, not long-form reasoning

Kev is not being built to solve difficult mathematics or generate large codebases on every event. Most maintenance tasks need compact judgment: classify, compare, relate, summarize, or abstain.

The default decision path should therefore use:

1. deterministic filtering and cheap rules first;
2. a small, fast model for semantic judgment;
3. structured output with a fixed schema;
4. deterministic validation and evidence checks;
5. a second model or slower path only when a specific task class requires it.

Do not request elaborate hidden reasoning or multiple self-reflection passes for routine tasks. Ask for a concise decision, evidence pointers, uncertainty, and a bounded operation. Reserve deeper analysis for high-impact or ambiguous research tasks.

---

# 5. System architecture

## 5.1 Logical architecture

The recommended runtime is a single orchestrator coordinating modular capabilities.

```text
                         ARIVOO
          user activity / sources / notes / maps
                           |
                           v
                  committed domain change
                           |
                transactional event / outbox
                           |
                           v
                    durable work queue
                           |
                           v
+----------------------------------------------------------+
|                         KEV                              |
|                                                          |
|  Event consumer -> task scheduler -> task state machine  |
|                         |                                |
|                         v                                |
|                 context/retrieval layer                  |
|                         |                                |
|                         v                                |
|                  decision orchestrator                  |
|                         |                                |
|             model provider router                       |
|             /        |         \                         |
|          primary   backup 1   backup 2                   |
|                         |                                |
|                         v                                |
|                 structured decision                      |
|                         |                                |
|           policy + evidence + schema validation         |
|                         |                                |
|                  action planner                         |
|                         |                                |
|               authorized Arivoo tools                   |
|                         |                                |
|                  postcondition check                    |
|                         |                                |
|                decision/eval history                    |
+----------------------------------------------------------+
                           |
                           v
                   ARIVOO knowledge base
```

External research is a separate input connector feeding the evidence layer. It must not bypass the same provenance, trust, and validation rules.

## 5.2 Main components

### A. Event intake and scheduler

Responsibilities:

- accept committed Arivoo events;
- validate event envelopes;
- deduplicate by stable event ID and object revision;
- coalesce bursts of changes;
- classify work priority;
- create idempotent tasks;
- enforce concurrency and rate limits;
- schedule retries and periodic maintenance sweeps;
- expose queue age, failure and backlog metrics.

### B. Retrieval and context builder

Responsibilities:

- call Arivoo's authorized retrieval interfaces;
- retrieve source content only when needed and permitted;
- collect stable object IDs, revisions, evidence spans, trust labels, and origin;
- build bounded context packages;
- avoid duplicate context;
- preserve a machine-readable list of all evidence included and excluded.

The context builder is not the model. It should do as much deterministic work as possible before a model call.

### C. Decision orchestrator

Responsibilities:

- select a task recipe;
- select the relevant capability (classification, relationship discovery, concept maintenance, contradiction detection, summary update, external research, etc.);
- select a model tier;
- make a bounded model call;
- validate structured output;
- request a retry or fallback only under explicit conditions;
- return an abstention when necessary.

### D. Model provider router

Responsibilities:

- provider adapters with one common interface;
- per-provider model identifiers, endpoints, timeouts, rate limits, and capabilities;
- health and circuit-breaker state;
- normalized errors;
- retry and fallback policy;
- provider/model telemetry;
- capability profiles per task type.

A provider adapter should not contain knowledge-base business logic.

### E. Policy and evidence validator

Responsibilities:

- validate schema and required fields;
- verify referenced objects and revisions exist;
- verify evidence spans can be found in the cited source revision when available;
- check allowed relation types and endpoint kinds;
- enforce trust/origin rules;
- prevent forbidden operations;
- check idempotency and duplicate effects;
- enforce operation-specific confidence and evidence requirements;
- determine whether an action is automatic, tentative, rejected, or deferred.

### F. Action executor

Responsibilities:

- execute only typed, allowlisted operations;
- call Arivoo's stable write surface;
- use idempotency keys;
- enforce optimistic concurrency on object revisions;
- record before/after references;
- verify postconditions;
- handle partial failure and compensation;
- never accept model-provided SQL or arbitrary shell commands.

### G. Evaluation and feedback subsystem

Responsibilities:

- maintain evaluation datasets and versioned cases;
- run deterministic checks on model decisions;
- record precision/recall and task-specific measures where meaningful;
- track owner corrections and downstream retrieval outcomes;
- detect regression by provider, prompt, policy, and task class;
- produce a scorecard for each candidate policy/model update;
- separate training/tuning data from held-out evaluation data.

### H. External research connectors

Responsibilities:

- query one or more search providers;
- retrieve the source page or document;
- normalize metadata and text;
- record URL, domain, publication date, access time, and fingerprint;
- label the content as external/untrusted;
- produce candidate findings with exact evidence pointers;
- apply the same decision and action checks as internal material.

### I. Observability and operations

Responsibilities:

- structured logs and traces;
- task timeline and state transitions;
- provider request latency and failure rates;
- event queue depth and oldest-message age;
- retry and dead-letter rates;
- action verification failures;
- cost/request counts, even when providers are free;
- security and permission errors;
- a compact health report.

---

# 6. Technology decisions

## 6.1 Recommended stack

| Concern | Recommendation | Rationale |
|---|---|---|
| Main language | Python 3.12+ (pin exact supported runtime in project config) | Matches Arivoo's backend ecosystem and supports async orchestration, testing, and model integration. |
| Async HTTP | HTTPX | One clear async client for external APIs. |
| Data validation | Pydantic v2 | Versioned, typed decision/event contracts. |
| Runtime state | Explicit Python state machine | Inspectable control flow; no opaque agent framework required. |
| Database | PostgreSQL through Supabase | Durable task, event, policy, evaluation, and application state. |
| PostgreSQL access | psycopg 3 async or synchronous pool as appropriate | Direct SQL and transaction semantics; pin versions and verify pool mode compatibility. |
| Schema/migrations | Supabase CLI and SQL migrations | Reproducible environments and schema history. |
| API (optional) | FastAPI | Only when a network API is needed; not required for the first worker. |
| Test framework | pytest | Unit, contract, integration, property, and system tests. |
| Static quality | Ruff, mypy or pyright, pre-commit | Fast local checks and consistent code. |
| Packaging | `pyproject.toml` with lockfile | Reproducible installation. |
| Deployment | Persistent worker process/container first | Long-running queue consumer and simple operations. |

The exact Python version and package pins must be checked against the current supported deployment runtime when implementation begins.

## 6.2 Why not start with a large agent framework

Do not make LangChain, CrewAI, AutoGen, or a similar high-level framework the core of Kev's runtime.

Kev's critical engineering concerns are explicit task state, idempotency, provenance, bounded tools, failover, transaction boundaries, evidence validation, and measurable outcomes. Those are product-specific and must remain under direct control.

A framework can later be used for a well-isolated component if it demonstrates a clear advantage. It must not own the safety model or obscure the task lifecycle.

## 6.3 Provider abstraction

Define one internal interface, conceptually:

```python
class ModelProvider(Protocol):
    async def generate_decision(
        self,
        *,
        request: DecisionRequest,
        response_schema: type[BaseModel],
        timeout_s: float,
    ) -> ProviderDecision: ...
```

The exact implementation can vary by provider. The rest of Kev should only know the normalized request and response objects.

Provider configuration should include:

- provider name and adapter;
- endpoint and authentication secret reference;
- model name/version;
- supported features (JSON schema, tool calling, context length, streaming);
- timeout and retry limits;
- rate limits and quota ceilings;
- task classes approved for the model;
- measured capability/quality profile;
- enabled/disabled state.

Never hardcode the chosen provider into decision logic. The primary provider is configuration, not architecture.

## 6.4 Multi-provider failover

Use a primary provider and at least one backup. A second backup is optional until there are compatible providers.

Fallback conditions:

- connection failure;
- timeout;
- provider rate limit;
- provider 5xx or explicit temporary unavailability;
- malformed or schema-invalid output after a bounded repair attempt;
- model returns an unsupported capability error.

Do not automatically fall back simply because a model's answer is inconvenient or low-confidence. That creates model-shopping and inconsistent decision behavior. A quality-driven second opinion is a separate, explicitly evaluated task route.

Use circuit breakers and cooldowns to avoid hammering unavailable providers. Keep the original task ID and idempotency key across retries and fallback. Record every attempt.

---

# 7. Data and decision contracts

The schemas below are conceptual starting points. They must be reconciled with Arivoo's real schema and the final Kev migrations before implementation.

## 7.1 Event envelope

Every Arivoo-originated event consumed by Kev should carry:

```json
{
  "event_id": "uuid",
  "event_type": "note.created",
  "occurred_at": "2026-11-16T00:00:00Z",
  "producer": "arivoo",
  "owner_id": "owner-id",
  "object_type": "note",
  "object_id": "canonical-object-id",
  "object_revision": 3,
  "change_id": "transaction-or-change-id",
  "payload_version": 1,
  "payload": {
    "operation": "created"
  }
}
```

Rules:

- Event IDs are globally unique within the owner/project scope.
- Events identify an object revision, not just a mutable object ID.
- The payload should be small. Kev retrieves actual material through authorized APIs.
- Events do not contain secrets or unnecessary full document bodies.
- The event is committed only when the corresponding Arivoo change commits.
- Repeated delivery is expected and harmless.

## 7.2 Task state machine

Recommended states:

`queued -> claimed -> retrieving -> deciding -> validating -> planned -> executing -> verifying -> completed`

Alternative terminal or recoverable states:

- `superseded`: a newer object revision made this task obsolete;
- `deferred`: prerequisite or dependency is not ready;
- `abstained`: insufficient evidence or ambiguous intent;
- `retry_wait`: transient failure with next-attempt time;
- `dead_letter`: retry policy exhausted and explicit investigation required;
- `rejected`: policy or contract violation;
- `partial`: one or more operations succeeded while another failed, with explicit reconciliation state.

Every transition must have an actor, timestamp, reason code, and relevant record pointer. A task must never appear completed before postcondition verification.

## 7.3 Structured decision object

The model returns a bounded object such as:

```json
{
  "schema_version": 1,
  "task_id": "uuid",
  "decision_type": "relationship_candidate",
  "summary": "The two sources discuss the same mechanism from different perspectives.",
  "operations": [
    {
      "operation": "propose_relation",
      "from": {"type": "source", "id": "source-a", "revision": 2},
      "to": {"type": "concept", "id": "concept-b", "revision": 5},
      "relation_type": "discusses",
      "evidence": [
        {
          "object_id": "source-a",
          "revision": 2,
          "locator": "page-or-span-reference",
          "excerpt": "Exact supporting text or a short evidence span"
        }
      ],
      "status": "candidate",
      "confidence": 0.84
    }
  ],
  "uncertainties": ["The second source's context may narrow the relation."],
  "abstain": false
}
```

This is an example contract, not the final relation taxonomy. The exact relation names must be defined in one versioned registry.

The validator must reject:

- unknown operations;
- unknown relation types;
- missing source IDs or revisions;
- mismatched revisions;
- invalid endpoint types;
- evidence with no resolvable source;
- confidence outside the allowed range;
- a supposedly established fact with no admissible evidence;
- any attempt to execute raw SQL or arbitrary code.

## 7.4 Confidence is not evidence

Model confidence is a weak signal about the model's uncertainty. It is not a substitute for source evidence.

Action admission should depend on operation class, evidence quality, source trust, provenance completeness, deterministic rules, and measured model performance. Confidence can adjust routing or status but cannot override missing evidence.

## 7.5 Knowledge change classes

Use at least four internal classes:

1. **Observed:** directly present in an owner or external source, with provenance.
2. **Derived:** generated summary, extraction, classification, or relation that is mechanically or evidentially supported.
3. **Candidate:** plausible but not sufficiently established; retained for later reconsideration.
4. **Rejected/superseded:** not currently accepted, with reason and decision history retained.

Do not collapse these into one generic “fact” field. The system must be able to distinguish owner-authored content, external evidence, generated interpretations, and hypotheses.

---

# 8. The knowledge model: continuous reorganization without identity collapse

## 8.1 Stable identity, evolving organization

The knowledge base must be allowed to reorganize as the owner's understanding changes.

The correct design is not a rigid folder tree and not a graph that rewrites every identity whenever a new idea appears. Use a stable identity layer with versioned, revisable relationships and organization.

Stable identities:

- source/work identities;
- owner-authored notes and journal objects;
- concept identities once established;
- relation/event/decision identities;
- provenance references to exact source revisions.

Evolving state:

- concept names and descriptions;
- aliases;
- topic groupings;
- related-concept relationships;
- generated summaries;
- project/blueprint associations;
- candidate relations and their evidence status;
- suggested parent/child or broader/narrower structure.

## 8.2 Concept lifecycle

Suggested lifecycle:

`candidate -> provisional -> established -> revised`

Other transitions:

- `split`: one concept becomes multiple distinct concepts;
- `merged`: identities are linked through a governed merge record; do not erase the prior IDs;
- `deprecated`: no longer recommended for new organization but historically resolvable;
- `contested`: its meaning or boundary is disputed by evidence or owner correction.

Promotion should require more than repeated model mentions. Useful evidence may include independent source support, repeated owner-authored usage, stable definitions, retrieval utility, and explicit owner behavior. The policy must be measurable and versioned.

## 8.3 Relation lifecycle

Suggested lifecycle:

`candidate -> supported -> established -> challenged -> superseded`

A relation stores:

- stable relation ID;
- typed endpoints and their revisions;
- relation type and directionality;
- supporting evidence references;
- source trust/origin;
- creation and last-evaluated times;
- decision/policy version;
- status and reason;
- contradictions or counter-evidence;
- reversal/supersession pointer.

Similarity can generate candidate relations. It cannot alone establish factual relations.

## 8.4 Reorganization protocol

Kev should treat larger reorganizations as proposed change sets with deterministic validation, not a series of invisible writes.

A reorganization change set should include:

- objective and trigger;
- objects affected;
- before/after graph or organization snapshot;
- evidence for each change;
- dependencies and expected side effects;
- invariant checks;
- reversibility method;
- verification plan;
- model and policy versions.

Safe, low-risk derived changes can execute automatically. If a change would destroy identity, remove original material, alter access/security, or make a broad irreversible change, it must be rejected or routed to an explicit owner decision. Routine user interaction should not be burdened with approval controls.

## 8.5 Contradiction handling

Contradiction is information, not an error to clean up.

Kev should:

1. identify the claims that appear inconsistent;
2. preserve each claim and its source revision;
3. identify whether the contradiction is factual, temporal, definitional, methodological, or apparent;
4. record the context that might reconcile them;
5. maintain a relation that says they conflict or qualify each other;
6. avoid selecting the most recent or most confident model answer as automatically correct.

A newer source can supersede an older statement only when evidence and scope justify it. Historical records must remain retrievable.

---

# 9. Autonomy, permissions, and safety model

## 9.1 Capability-based tools

The model should see a limited tool catalogue. Each tool has:

- name and version;
- purpose;
- typed input and output schema;
- allowed object types;
- permission scope;
- idempotency behavior;
- side-effect classification;
- postcondition check;
- failure codes.

Initial read tools may include:

- `search_knowledge`
- `get_object`
- `get_source_revision`
- `get_evidence_span`
- `get_concept`
- `get_relations`
- `get_research_context`
- `search_external_sources`
- `fetch_external_source`

Initial write tools may include:

- `create_candidate_concept`
- `update_derived_description`
- `propose_relation`
- `promote_supported_relation`
- `record_contradiction`
- `add_alias_candidate`
- `revise_derived_summary`
- `attach_source_to_research_map`
- `record_external_source`
- `create_reorganization_change_set`
- `apply_reversible_change_set`

These names are proposed. The final tools must map onto Arivoo's actual contracts and must be implemented as typed service functions, not prompt-generated SQL.

## 9.2 Autonomy policy matrix

| Operation | Default autonomy | Required controls |
|---|---|---|
| Read authorized knowledge | Automatic | Scope + access checks |
| Create candidate concept | Automatic | Provenance + idempotency |
| Add alias candidate | Automatic | Evidence + reversible history |
| Add candidate relation | Automatic | Evidence references + status candidate |
| Promote low-risk supported relation | Automatic when policy passes | Evidence rule + deterministic validation + evaluation threshold |
| Update generated summary | Automatic | Dependency list + previous version retained |
| Reorganize derived topic groupings | Automatic | Change set + invariant checks + rollback |
| Record contradiction | Automatic | Preserve both claims and sources |
| Add externally sourced material | Automatic under configured discovery policy | Citation/origin/trust labels + content fingerprint |
| Merge canonical works/sources | Not automatic | Preserve identities; require explicit owner-level policy/decision |
| Delete original material permanently | Forbidden to routine Kev tools | Owner-controlled Arivoo operation |
| Change database permissions or RLS | Forbidden | Separate reviewed engineering deployment |
| Run arbitrary SQL/shell/code | Forbidden | No such model tool exists |
| Modify Kev production code or tests | Not an ordinary agent action | Separate software change process and CI |

## 9.3 Prompt injection and hostile content

All source text, imported files, web pages, notes, and model-generated text are data. They are not instructions to the runtime.

The harness must:

- keep system policy and tool definitions outside retrieved content;
- delimit evidence and label it untrusted;
- reject model attempts to expand tool permissions;
- never execute instructions embedded in source material;
- keep secrets out of model context;
- constrain external research to approved connectors and budgets;
- record which external content influenced a decision;
- test adversarial examples that ask the model to reveal secrets, change policies, fabricate sources, or bypass the tool layer.

## 9.4 Security boundary

- No service-role or Supabase secret key in model context, browser code, frontend bundles, or repository files.
- Store secrets in environment variables or a managed secret store.
- Use least-privilege database roles for Kev's worker.
- Avoid exposing internal `kev` tables through the public Data API.
- Enable RLS for every exposed table and test grants and policies independently.
- Treat `service_role` / secret-key access as privileged bypass authority. Prefer a dedicated worker role and narrowly scoped database functions where practical.
- Avoid `SECURITY DEFINER` functions unless their necessity, schema placement, `EXECUTE` grants, owner checks, and RLS implications are explicitly reviewed.
- Keep Auth authorization in trusted claims/role tables. Never make access decisions from user-editable metadata.
- Use TLS for database connections.
- Rotate/revoke compromised credentials and record the incident.

---

# 10. Supabase deployment and storage architecture

## 10.1 Project intent

Create a dedicated Supabase project named **`arivo`** in the existing `catalyst` organization, using Mumbai (`ap-south-1`) as the initial region unless a measured deployment constraint changes that choice.

Do not reuse an inactive unrelated project merely because it exists. Do not delete the existing `meraki`, `phase 0`, or `catalyst.exe` projects as part of this implementation unless the owner explicitly confirms permanent deletion and the data/backups are understood. Creating a new project and deleting old projects are separate actions.

At the time of prior account inspection, the organization was `catalyst`, and the three existing projects were inactive. A project quote was returned as $0/month on 16 November 2026. Recheck the live quote and organization before project creation; costs and project states can change.

## 10.2 One project or two?

Recommended starting point: one dedicated Supabase project for the Arivoo/Kev system, with clear schema and role boundaries, rather than two separately administered databases.

Why:

- Arivoo and Kev need to share a consistent view of object identity and revisions.
- Event creation should be transactionally tied to the Arivoo write that caused it.
- A single PostgreSQL transaction can commit an Arivoo change and its outbox/queue event together.
- Kev's operational tables can be isolated in a non-exposed schema and accessed by a restricted worker role.

This is a logical separation, not a duplication of the domain model. The exact schema names must be discovered from the live Arivoo migrations before choosing where to place Kev's tables.

If operational isolation later requires a separate database, use a transactional outbox in Arivoo and an idempotent relay to Kev. Do not create a cross-database atomicity promise that PostgreSQL cannot provide by itself.

## 10.3 Supabase responsibilities

- PostgreSQL: canonical relational state, event/outbox metadata, Kev tasks, decisions, evaluation records, policy versions, and references.
- Supabase Storage: source files and other binary objects, using private buckets and explicit access policies.
- Supabase Auth: owner identity if/when the product needs hosted user authentication; do not invent a user-auth architecture before checking Arivoo's current identity contract.
- Supabase Queues / `pgmq`: durable asynchronous work queue where the extension and operational model fit.
- Realtime: optional low-latency notification to wake a worker; not the sole durable event store.
- Cron: optional periodic enqueue for bounded maintenance sweeps and reconciliation tasks.

## 10.4 Event transaction

Prefer a transactional outbox or queue operation that commits in the same PostgreSQL transaction as the Arivoo domain change.

Desired property:

- If the Arivoo change rolls back, no Kev event is published.
- If the Arivoo change commits, an event remains durably available even if Kev is offline.
- Consumers may receive a message more than once; idempotency prevents duplicate effects.

Supabase Queues are built on `pgmq` and provide durable message storage, visibility windows, and archival. Current Supabase documentation also describes adding a queue message in the same transaction as the domain write. Verify the exact extension/API behavior and current SDK/CLI versions before implementation.

## 10.5 Storage and Q12 resolution

Use Supabase Storage for original uploaded files if this is consistent with Arivoo's accepted source/blob contract.

PostgreSQL stores the metadata and lifecycle record; Storage stores the object bytes. Because a database transaction and an object-storage operation are not a single atomic transaction, use an explicit staged lifecycle:

1. Create a pending upload record with stable object ID and expected metadata.
2. Upload bytes to a private bucket using a deterministic object path or immutable version path.
3. Verify object existence, byte size, and checksum.
4. Commit the source/blob reference and mark the object available.
5. On failure, keep a retryable state and a cleanup/reconciliation record.
6. A periodic reconciler detects orphaned objects and database rows with missing objects.
7. Deletion first follows Arivoo's governed purge/tombstone process; Storage cleanup is reconciled separately and must not silently break references.

Do not claim cross-store atomicity. Test interrupted uploads, repeated uploads, duplicate delivery, missing objects, checksum mismatch, delete/retry, backup/restore, and reconciliation.

## 10.6 Supabase credentials

Maintain separate credentials for:

- model-provider APIs;
- Supabase publishable client access if needed;
- Supabase server-side secret key / privileged access;
- PostgreSQL direct or pooled connection credentials;
- external search connectors.

Only server-side components may receive secret credentials. Kev's model requests must never include them. `.env` must be gitignored; commit only `.env.example` with variable names and descriptions, never actual values.

The Supabase documentation currently recommends modern publishable and secret keys for new integrations. A secret key has privileged access and must never be exposed to a browser. RLS and grants must be tested as separate controls. Use Supabase's current documentation when implementing because CLI and platform behavior change.

---

# 11. Runtime behavior and decision policies

## 11.1 Fast path and slow path

Use two broad paths.

**Fast path:** event intake, metadata classification, deduplication, low-risk concept/alias candidates, simple relation candidates, summary invalidation, and small evidence-backed updates. The fast path should use deterministic logic and at most one fast model call for most tasks.

**Deep path:** ambiguous relationships, contradiction analysis, broad reorganization, research synthesis, low-confidence external evidence, and tasks with broad downstream effects. These may use more context, a second model, or an additional evaluation pass. They remain asynchronous.

## 11.2 Event-to-task recipes

Different event types should invoke task recipes rather than a generic “think about everything” prompt.

Examples:

- `source.created`: extract metadata, classify content, identify initial concepts, retrieve related sources, create relation candidates, update relevant topic structures.
- `highlight.created`: attach the highlight to its source revision, extract candidate concepts/claims, find relevant prior notes, update derived context.
- `note.created`: detect topic and intent, connect to existing concepts and projects, identify referenced sources, update relevant research map candidates.
- `journal_block.created`: retrieve nearby journal context and related knowledge, classify as reflection/claim/question/plan only if the product contract supports it, preserve owner wording.
- `map.updated`: reconcile changed nodes/edges with canonical concept/relation identities; do not silently discard owner-authored structure.
- `blueprint.updated`: update research objectives, supporting evidence, open questions and related materials without rewriting owner-authored sections.
- `source.revised`: invalidate derived summaries, embeddings, concept evidence, and retrieval caches tied to the old revision; recompute only affected dependents.
- `object.tombstoned`: invalidate or withdraw derived relations and summaries that depend on the removed object according to Arivoo's purge/tombstone contract.

## 11.3 Batching and compounding

Rapid events from the same object should be grouped. For example, ten highlights from one reading session may become one enrichment task over the source and its ten highlight revisions.

Batching must preserve the identities and event history of the individual changes. Coalescing is an optimization, not permission to lose information.

## 11.4 Decision policy versioning

Every decision recipe and policy has:

- stable policy ID;
- semantic version;
- owner/agent authorship metadata;
- intended task class;
- input schema;
- allowed operations;
- admission rules;
- test cases;
- effective date;
- supersession pointer;
- performance/evaluation record.

A policy update is a software/configuration change, not an invisible prompt edit. It must be evaluated against the fixed corpus and held-out set before becoming active.

---

# 12. Evaluation system

Evaluation is central to Kev. A model that produces plausible language but poor knowledge changes is not a successful maintainer.

## 12.1 Evaluation corpus

Use both arbitrary real text and engineered edge cases.

The corpus should include:

- short notes and fragments;
- long-form articles and chapters;
- technical documents;
- overlapping topics;
- synonymous expressions;
- near-duplicate texts;
- two editions of the same work;
- distinct works with shared terminology;
- contradictory claims;
- temporal updates;
- ambiguous passages;
- low-quality sources;
- external research results;
- adversarial instructions embedded in source text;
- empty or malformed content;
- non-English and mixed-language cases if they are in the intended corpus.

Real personal material should be selected and authorized by the owner. Public, non-personal material can be used for broad format and extraction tests. Synthetic cases remain useful for precise known-answer tests; they must supplement, not replace, real-text evaluation.

## 12.2 Evaluation levels

**Level A — Structural validity**

- Is the JSON/schema valid?
- Are all IDs and revisions real?
- Are relation types permitted?
- Is provenance complete?
- Did the operation obey policy?

**Level B — Evidence validity**

- Does the cited span exist in the referenced revision?
- Does the evidence actually support the relation or summary?
- Was contradictory evidence considered?
- Was external origin retained?

**Level C — Decision quality**

- Is the concept classification useful?
- Is the relationship type correct?
- Did the model hallucinate a relation?
- Did it miss an important connection?
- Did it over-merge distinct concepts?
- Did it preserve ambiguity when needed?

**Level D — Product utility**

- Can the owner find previously saved information under new queries?
- Do new sources enrich old research contexts?
- Does the system reduce manual organization work?
- Are generated structures actually useful after real use?
- Are unnecessary changes low enough that the knowledge base remains understandable?

## 12.3 Core metrics

Track by task class, provider, model, policy version, and corpus revision:

- precision of supported relations;
- recall of known required relations;
- unsupported-relation rate;
- concept duplicate/split/merge correctness;
- contradiction detection precision/recall;
- provenance completeness;
- evidence-span validity;
- incorrect revision-reference rate;
- action success and postcondition verification rate;
- rollback/compensation frequency;
- abstention rate and abstention correctness;
- owner correction rate;
- stale derived-object rate;
- retrieval relevance and rediscovery success;
- p50/p95 latency;
- model calls per event and provider fallback rate.

Do not collapse these into a single opaque “Kev score.” Different failure classes have different consequences.

## 12.4 Held-out testing

Split test material into:

- development examples used to design prompts and policies;
- regression examples that must always be rerun;
- held-out examples not used to tune the current decision policy;
- real-use validation material evaluated after normal owner workflows.

Freeze thresholds before a candidate policy is evaluated. A policy cannot be promoted by moving the threshold after seeing its failures.

## 12.5 Feedback and correction

Owner corrections should become structured feedback events, not only chat messages or revised prompts.

Record:

- which decision was corrected;
- what output was changed;
- whether the correction concerns identity, evidence, relation type, concept boundary, source reliability, or preference;
- the relevant object revisions;
- whether the correction is local or generalizable;
- whether it becomes a regression case.

Do not assume every one-off owner correction should become a universal rule. The feedback processor must distinguish local preference, domain-specific correction, and global policy change.

---

# 13. Self-improvement without uncontrolled self-modification

Kev should get better over time, but the improvement loop must be measurable.

## 13.1 What it may improve automatically

- task routing rules within defined bounds;
- retrieval query expansion policies;
- context selection and ranking parameters;
- prompt templates and structured output instructions, where versioned;
- per-provider task routing based on measured quality/latency;
- thresholds only when recalibrated through a predeclared evaluation protocol;
- batch/coalescing policies;
- retry and scheduling parameters within hard operational limits.

## 13.2 What it may only propose

- changes to tool permissions;
- new classes of database writes;
- changes to RLS, grants, secrets, authentication or storage security;
- migrations that alter Arivoo's canonical data contracts;
- changes that weaken evidence requirements;
- changes to immutable-source or provenance rules;
- changes to evaluation thresholds without a predefined statistical/calibration process;
- changes to the production code of Kev itself.

## 13.3 Improvement cycle

1. Identify a measurable failure or inefficiency.
2. Form a bounded hypothesis.
3. Create a candidate policy or configuration change.
4. Run deterministic tests and the regression corpus.
5. Run the held-out evaluation.
6. Compare against the current production policy.
7. Reject if a protected metric regresses beyond its allowed margin.
8. If all gates pass, activate gradually for the relevant task class.
9. Monitor live outcomes and rollback automatically if guardrail metrics deteriorate.
10. Record the result and the policy lineage.

This is policy optimization, not the model secretly rewriting itself.

---

# 14. Repository structure

Initial proposed repository layout:

```text
kev/
├── README.md
├── SYSTEM-SPEC.md
├── EXECUTION.md
├── ROADMAP.md
├── RTM.md
├── DECISIONS.md
├── STATE.md
├── AGENTS.md
├── pyproject.toml
├── uv.lock                         # or another single committed lockfile
├── .env.example
├── .gitignore
├── src/
│   └── kev/
│       ├── __init__.py
│       ├── config/
│       ├── runtime/
│       │   ├── scheduler.py
│       │   ├── consumer.py
│       │   ├── task_state.py
│       │   └── idempotency.py
│       ├── events/
│       │   ├── schemas.py
│       │   ├── intake.py
│       │   └── coalescing.py
│       ├── providers/
│       │   ├── protocol.py
│       │   ├── router.py
│       │   ├── errors.py
│       │   └── adapters/
│       ├── arivoo/
│       │   ├── client.py
│       │   ├── contracts.py
│       │   └── tools.py
│       ├── retrieval/
│       ├── context/
│       ├── decisions/
│       │   ├── schemas.py
│       │   ├── orchestrator.py
│       │   └── recipes/
│       ├── policies/
│       ├── execution/
│       ├── knowledge/
│       │   ├── concepts.py
│       │   ├── relations.py
│       │   ├── contradictions.py
│       │   └── reorganization.py
│       ├── research/
│       │   ├── search.py
│       │   ├── fetch.py
│       │   └── provenance.py
│       ├── evaluation/
│       │   ├── runner.py
│       │   ├── metrics.py
│       │   └── datasets.py
│       ├── feedback/
│       ├── storage/
│       └── observability/
├── supabase/
│   ├── config.toml
│   ├── migrations/
│   └── tests/
├── evals/
│   ├── fixtures/
│   ├── regression/
│   ├── heldout/
│   └── manifests/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── system/
│   ├── security/
│   └── acceptance/
├── scripts/
└── docs/
    ├── architecture/
    ├── operations/
    └── decisions/
```

Do not create empty folders just to imitate this diagram. Create modules when their first bounded claim needs them. Keep the system simpler than the diagram until actual implementation requires the separation.

---

# 15. V-model and requirements traceability

## 15.1 V-model stages

### Left side: definition and decomposition

**V0 — Product mission**

Define frictionless knowledge compounding, scope, owner experience, autonomy boundary, and measurable outcomes.

**V1 — System requirements**

Convert product intent into KEV-FR and KEV-NFR requirements. Identify Arivoo dependencies and external system constraints.

**V2 — Architecture**

Define event flow, scheduler, context builder, provider router, decision engine, policy validator, action executor, evaluation, Supabase layout, and security zones.

**V3 — Component contracts**

Define event envelope, task state machine, provider interface, decision schema, tool contracts, relation/concept registries, database schema and migration rules.

**V4 — Implementation**

Implement the smallest vertical slice that can receive one real Arivoo event, retrieve evidence, make one bounded decision, validate it, apply one safe change, and verify the result.

### Right side: verification and validation

**V4-test — Unit/component verification**

Test individual schemas, adapters, policies, state transitions, idempotency, and validators.

**V3-test — Integration verification**

Test provider routing, queue consumption, Arivoo retrieval, action execution, and database transactions together.

**V2-test — System verification**

Test the entire event-to-verified-change path under failure, load, duplicate delivery, provider outage, stale revisions, hostile content, and recovery.

**V1-test — Requirements acceptance**

Show that every requirement has evidence and the acceptance corpus covers its failure modes.

**V0-test — Product validation**

Use the system in real Arivoo workflows. Prove that knowledge compounds and manual organization work is genuinely reduced without damaging the owner's material.

## 15.2 RTM format

`RTM.md` must contain one row per requirement:

| Requirement | Design component | Interface / data | Implementation claim | Verification case | Evidence | Status |
|---|---|---|---|---|---|---|
| KEV-FR-001 | Event intake | Event envelope v1 | CLAIM-xxx | EVT-001.. | Run record | Planned |

No requirement is considered complete because a module exists. It is complete only when its corresponding verification passes and the evidence points to the exact code head and test run.

## 15.3 Verification evidence

Each implementation slice must preserve:

- exact base/head commit;
- declared scope;
- requirement IDs;
- known-bad tests and observed RED evidence;
- GREEN evidence;
- commands and exit codes;
- test output digests where used by the harness;
- independent review or verification result;
- unresolved/not-verified items;
- security and regression impact;
- final merge and post-merge validation.

Do not replace failed test evidence with a later green run without retaining the failure and explaining the repair.

---

# 16. Phased implementation roadmap

The roadmap is organized around demonstrable capability, not calendar estimates.

## Phase 0 — Product and contract freeze

**Goal:** Turn this document into a testable build contract.

Deliverables:

- create Kev repository;
- commit `SYSTEM-SPEC.md`, `EXECUTION.md`, `ROADMAP.md`, `RTM.md`, `AGENTS.md`, `STATE.md`, `DECISIONS.md`;
- inspect live Arivoo contracts and identify exact integration surface;
- decide whether Kev operational tables share the Arivoo Supabase project/schema boundary or require a separate database;
- establish owner identity and authorization assumptions;
- define first event types and first automated write operation;
- define evaluation corpus governance and held-out split.

Exit criteria:

- every initial functional requirement has a testable statement;
- no guessed Arivoo table or interface is in the contract;
- architecture and trust boundaries are documented;
- first vertical slice has exact acceptance criteria.

## Phase 1 — Supabase and operational foundation

**Goal:** Provision a clean `arivo` project and establish reproducible database operations.

Deliverables:

- dedicated Supabase project in the chosen organization/region;
- secrets configured outside Git;
- PostgreSQL connectivity verified from the worker environment;
- private schemas and roles designed;
- migrations checked into the repository;
- RLS/grants tests for exposed tables;
- private Storage bucket and upload/reconciliation contract;
- database backup/export and recovery procedure;
- operational health/advisor baseline.

Exit criteria:

- clean environment can be recreated from migrations;
- service and worker credentials have least required authority;
- no secret appears in code, logs, or model context;
- upload interruption and missing-object cases are handled;
- database access tests prove allowed and denied paths.

## Phase 2 — Event intake and durable task engine

**Goal:** Kev receives real Arivoo changes without blocking Arivoo.

Deliverables:

- stable event schema;
- transactional outbox or queue integration;
- task state machine;
- queue consumer;
- idempotency keys;
- duplicate delivery handling;
- coalescing for rapid object revisions;
- bounded retry/backoff;
- dead-letter handling;
- task timeline and metrics.

First vertical slice:

1. create a note in Arivoo;
2. event is committed with the note change;
3. Kev receives the event;
4. task is created exactly once in its logical effect;
5. worker records completion without a model call.

Exit criteria:

- Arivoo user operation does not wait for Kev;
- worker crash and redelivery do not lose or duplicate work;
- stale revisions are superseded safely;
- event-to-task latency is measured.

## Phase 3 — Arivoo read integration and context building

**Goal:** Kev can retrieve the right context from Arivoo.

Deliverables:

- typed Arivoo client/adapter;
- integration tests against real backend contracts;
- bounded retrieval and pagination;
- source revision and provenance preservation;
- evidence span representation;
- context packing and token budgeting;
- hostile-content labeling;
- retrieval trace.

Exit criteria:

- Kev can resolve event object and revision;
- it retrieves related source material without dumping the entire database;
- every context item has stable provenance;
- authorization failures are fail-closed;
- context selection is deterministic where possible and reproducible.

## Phase 4 — Model router and first decision loop

**Goal:** A small free-API model can make a structured decision through a replaceable provider interface.

Deliverables:

- provider protocol;
- primary adapter;
- first fallback adapter;
- model capability registry;
- timeout/rate-limit handling;
- circuit breaker;
- decision schema;
- output validation;
- bounded retry and abstention;
- model call logs with redacted metadata.

First model task:

Given a newly created note and a bounded evidence package, return candidate topics/concepts and relevant existing objects, with evidence references and uncertainty.

Exit criteria:

- changing provider requires configuration, not business-logic rewrite;
- provider failure leaves task recoverable;
- malformed output cannot execute;
- every decision has model and policy lineage;
- no unrestricted tools or SQL are available to the model.

## Phase 5 — Safe autonomous knowledge creation

**Goal:** Kev can autonomously enrich Arivoo with useful derived knowledge.

Deliverables:

- concept candidate creation;
- alias candidate creation;
- relation candidate creation;
- summary update with dependency tracking;
- evidence validator;
- idempotent write tools;
- postcondition verification;
- reversal/supersession support;
- autonomy policy matrix implemented in code.

Exit criteria:

- routine safe operations happen without owner approval;
- unsupported relations remain candidate or are rejected;
- source revisions are correctly pinned;
- duplicate events do not produce duplicate effects;
- derived changes can be reversed without losing original material.

## Phase 6 — Continuous organizer and knowledge-health maintainer

**Goal:** Kev improves the organization of the knowledge base as the owner's interests and information evolve.

Deliverables:

- concept identity and alias lifecycle;
- topic structure revision;
- duplicate and near-duplicate detection;
- contradiction records;
- stale summary/index invalidation;
- orphan and broken-reference detection;
- periodic bounded reconciliation jobs;
- change-set preview, validation, execution, and rollback;
- dependency graph for derived material.

Exit criteria:

- new information can reorganize existing derived structures;
- historical identities and owner-authored content remain intact;
- contradictions are preserved;
- broad changes are grouped and verifiable;
- the health report identifies integrity and freshness issues.

## Phase 7 — External discovery and research

**Goal:** Kev can expand the knowledge base beyond owner-provided material.

Deliverables:

- search-provider interface;
- web/document fetcher;
- source normalization;
- date and URL preservation;
- content fingerprints;
- quote/evidence spans;
- external trust labels;
- prompt-injection defenses;
- duplicate external-source detection;
- external finding and synthesis recipes.

Exit criteria:

- every external claim has a retrievable source pointer;
- external material never masquerades as owner-authored material;
- stale and undated sources are treated appropriately;
- untrusted page instructions cannot change Kev's tools or policies;
- research connector failure does not block internal knowledge maintenance.

## Phase 8 — Evaluation, feedback, and self-improvement

**Goal:** Kev gets better through measured feedback rather than uncontrolled prompt edits.

Deliverables:

- real-text evaluation corpus;
- fixed regression corpus;
- held-out set;
- per-task-class metrics;
- owner correction capture;
- policy version registry;
- candidate policy evaluation;
- gradual activation and rollback;
- provider quality and latency scorecards.

Exit criteria:

- unsupported relation and false-positive rates are measurable;
- policy changes cannot bypass fixed tests;
- held-out outcomes are preserved;
- owner corrections can become regression cases;
- improvements are demonstrated across more than one narrow fixture.

## Phase 9 — Product-level validation and hardening

**Goal:** Demonstrate that Kev genuinely compounds knowledge in real use.

Deliverables:

- full RTM closure or explicit accepted residuals;
- security and authorization review;
- recovery and rebuild tests;
- provider outage tests;
- load and latency measurements;
- external research failure tests;
- real workflow evaluation;
- operational runbooks;
- backup/restore rehearsal;
- final independent system verification.

Exit criteria:

- Arivoo remains usable when Kev or every model provider is unavailable;
- no committed event is silently lost;
- the knowledge base can evolve without losing historical information;
- retrieved older material demonstrably becomes useful in new contexts;
- relations and concepts improve navigation without fabricated certainty;
- the owner experiences less manual organization work, not more.

---

# 17. Engineering execution protocol for coding agents

This section is binding for implementation agents working in the Kev repository. The purpose is to keep work incremental, testable, and safe.

## 17.1 Start-of-session procedure

1. Read `AGENTS.md`.
2. Read `STATE.md` and the latest work-log/session record.
3. Read `EXECUTION.md`, the relevant requirements, relevant decisions, and the exact component contract for the task.
4. Inspect live GitHub state: current branch, open PRs, recent commits, checks, review comments, and branch/base relationship.
5. Inspect the actual code and tests. Do not assume a previous agent's description is current.
6. Identify the exact requirement IDs and dependencies.
7. Confirm no other active claim owns overlapping files.
8. Record the exact base commit before editing.

## 17.2 Claim-before-work

Every consequential implementation change requires one bounded claim, one branch, and one pull request.

A claim must state:

- claim ID;
- task objective;
- requirement IDs;
- exact file scope;
- non-goals;
- base commit;
- known-bad/RED tests expected;
- acceptance evidence;
- security/data-loss implications;
- unresolved decisions.

Do not run multiple agents against overlapping files unless the shared-file merge rules are explicit. Shared append-only registries may be touched only with append-shaped edits.

## 17.3 RED-first implementation

For behavior changes:

1. Write a test that expresses the missing behavior or failure.
2. Run it against the current base and preserve the RED output.
3. Implement the smallest change that makes the test pass.
4. Run the focused test.
5. Run adjacent regression tests.
6. Run full required CI.
7. Run a fresh-context reviewer/verifier against the exact diff and evidence.

Do not write the implementation first and then invent a test that merely restates what the code does.

For documentation-only work, explain why a behavioral RED is not applicable and verify links, canonical consistency, and document checks.

## 17.4 One bounded slice

A slice should implement one coherent capability. Avoid combining schema changes, provider adapters, autonomous policy, and external research in one enormous PR.

The recommended first vertical slice is deliberately narrow: one Arivoo note-created event, one retrieval context, one fast model decision, one candidate concept or relation operation, one deterministic validation, one write, and one postcondition verification.

## 17.5 Definition of done

A slice is done only when:

- the change maps to declared requirements;
- tests prove the intended behavior and relevant failure modes;
- no known-bad case regressed;
- database migrations apply cleanly in a fresh environment;
- grants and RLS are tested if tables or roles changed;
- secrets are absent from code, logs, and artifacts;
- provider failure and retry behavior are tested where applicable;
- the action is idempotent or the reason it is not is explicit;
- evidence and unresolved items are recorded;
- CI is green at the exact PR head;
- review findings are dispositioned before merge;
- merge and post-merge state are verified;
- `STATE.md`, worklog, and roadmap reflect the actual result.

## 17.6 No false completion claims

Never say “implemented,” “verified,” “production-ready,” or “complete” because a document describes the feature or a mock test passes.

Classify evidence as:

- designed;
- implemented;
- unit-tested;
- integration-tested;
- system-tested;
- independently reviewed;
- validated in real owner workflow.

These are different levels and must not be conflated.

## 17.7 Arivoo changes

Kev agents must not modify Arivoo as a side effect of a Kev PR. If an Arivoo contract needs a new event or write surface, open a separate bounded Arivoo change under Arivoo's own execution protocol. Record the dependency in Kev's RTM and block only the dependent integration slice.

---

# 18. Initial implementation tickets

The first sequence should be:

1. **KEV-BOOT-001 — Repository foundation.** Create repo, project metadata, formatting/type/test tooling, CI, canonical docs, and a minimal worker entry point.
2. **KEV-ARCH-001 — Arivoo contract discovery.** Inspect live Arivoo schema, retrieval/write surfaces, event possibilities, authorization, and current Supabase/DB state. Produce a signed-off integration boundary note. No guessed writes.
3. **KEV-DB-001 — Supabase project and schema plan.** Create `arivo` project after current cost/org/region checks. Establish secure connection, migration workflow, private schema plan, roles, and test strategy.
4. **KEV-EVT-001 — Event envelope and task state machine.** Define schemas and unit tests before queue wiring.
5. **KEV-EVT-002 — Durable queue integration.** Commit event transactionally with one Arivoo change or via a correct outbox relay. Prove duplicate-delivery safety.
6. **KEV-ARV-001 — Read-only Arivoo adapter.** Retrieve one object and its source revision through existing authorized interfaces.
7. **KEV-CTX-001 — Evidence package builder.** Build bounded context with provenance and revision pins.
8. **KEV-MDL-001 — Provider protocol and first adapter.** Make one structured decision call, test malformed output, timeout, rate limit, and failover.
9. **KEV-DEC-001 — One decision recipe.** For a new note, identify candidate concepts/related objects with evidence and uncertainty.
10. **KEV-POL-001 — Deterministic admission policy.** Reject invalid IDs, stale revisions, missing evidence, unsupported operations, and forbidden actions.
11. **KEV-ACT-001 — One reversible action tool.** Create one candidate knowledge object or relation through Arivoo's supported write surface; verify exact postcondition.
12. **KEV-EVAL-001 — First evaluation corpus.** Include arbitrary text, known-answer cases, near-duplicates, ambiguity, contradiction, and hostile instructions.
13. **KEV-OBS-001 — Operational dashboard/report.** Expose queue lag, task status, provider health, latency, and action verification.

Only after this first end-to-end slice passes should the team expand the agent's capability set.

---

# 19. Initial acceptance scenarios

These scenarios become the first system-level acceptance tests.

### ACC-001 — Normal note compounding

Given an existing knowledge base with sources and concepts, when the owner creates a note, Arivoo commits immediately, Kev receives the event, retrieves relevant material, proposes evidence-backed links, applies permitted changes, and verifies them without owner intervention.

### ACC-002 — Provider outage

Given the primary model provider is unavailable, Kev attempts the configured fallback within limits. If all providers fail, the event remains durable and retryable. Arivoo remains usable.

### ACC-003 — Duplicate event

Given the same event is delivered multiple times, Kev's logical database effect occurs once. The audit log may record multiple delivery attempts, but no duplicate knowledge objects are created.

### ACC-004 — Rapid edits

Given an owner edits the same note several times in quick succession, Kev may coalesce work to the newest revision. It must not attach derived knowledge to a revision that no longer exists or silently overwrite a newer owner edit.

### ACC-005 — Weak evidence

Given two documents appear semantically related but no supporting evidence is found, Kev records a candidate or abstains. It does not promote an unsupported factual relation.

### ACC-006 — Contradiction

Given two sources make conflicting claims, Kev preserves both with provenance and records the conflict. It does not silently discard one.

### ACC-007 — Reorganization

Given new documents change the best grouping of existing concepts, Kev creates a versioned change set, validates invariants, applies reversible derived-structure changes, and preserves stable identities.

### ACC-008 — External research

Given a research task, Kev retrieves external sources, records URL/date/origin/evidence, treats page text as untrusted, and adds only validated findings. External findings remain distinguishable from owner-created material.

### ACC-009 — Hostile source content

Given an imported document includes instructions to reveal secrets or change agent policy, Kev treats those words as data. No credentials or tool permissions are exposed or modified.

### ACC-010 — Stale source revision

Given a source is revised after a task starts, Kev refuses to apply a result that targets a stale revision or explicitly recomputes against the new version.

### ACC-011 — Original preservation

Given Kev reorganizes concepts and relations, original sources and owner-authored notes remain unchanged and retrievable. Derived history supports reversal.

### ACC-012 — Real usefulness

Given the owner adds new research about a topic discussed months earlier, Kev brings relevant older material into the new context with reasons and provenance. This is the core product validation scenario.

---

# 20. Operations and reliability

## 20.1 Worker lifecycle

Workers should:

- start with a validated configuration;
- establish database and provider health;
- consume bounded batches;
- heartbeat while working;
- claim tasks with leases/visibility windows;
- renew leases for long tasks;
- checkpoint task state;
- acknowledge only after verified completion or intentional terminal classification;
- shut down gracefully without losing claimed work.

## 20.2 Retry policy

Use bounded exponential backoff with jitter for transient infrastructure/provider failures. Do not retry deterministic policy failures, malformed source data, or invalid decisions endlessly.

Separate:

- transient: timeout, rate limit, provider 5xx, temporary network error;
- permanent: invalid schema, forbidden tool, missing source revision, policy violation;
- stale: source changed during task;
- ambiguous: abstain or route to deeper evaluation;
- partial: reconciliation required.

## 20.3 Monitoring

Minimum operational metrics:

- events received/processed/superseded;
- queue depth and oldest event age;
- task duration by task type;
- retry/dead-letter counts;
- provider latency/error/fallback rates;
- schema-invalid response rate;
- policy rejection and abstention rates;
- action postcondition failure rate;
- stale revision rate;
- external research fetch errors;
- derived-object freshness;
- rollback/compensation counts.

## 20.4 Recovery

Document and test:

- database backup and restore;
- queue replay;
- event/task deduplication after replay;
- storage/database orphan reconciliation;
- worker restart during model request;
- worker restart after action but before acknowledgment;
- provider credential rotation;
- revoked model provider;
- failed migration recovery;
- policy rollback.

The architecture must make “action committed but acknowledgment lost” safe. This is why idempotency and postcondition reads are required.

---

# 21. Explicit decisions and open questions

## 21.1 Decisions established by the owner in the product discussion

- Kev is the autonomous maintainer and creator of Arivoo's knowledge base.
- Routine work must have no manual approval or maintenance-button friction.
- Kev should operate continuously and with low latency.
- Ordinary decisions should be fast and bounded, not slow extended reasoning by default.
- Use multiple model APIs: a primary and backups.
- The specific provider is an implementation configuration and should not shape the architecture.
- Start with a free API and a small model for routine decisions.
- The knowledge base may continuously reorganize itself as it grows.
- Kev should maintain both owner-created knowledge and external discoveries.
- Use a new repository for Kev.
- Use Supabase for the hosted database/storage direction and create a dedicated project named `arivo`.
- Broaden text evaluation beyond synthetic-only fixtures; test arbitrary real text as well as engineered edge cases.

## 21.2 Decisions to confirm during Phase 0

- Exact existing Arivoo event and write interfaces to integrate with.
- Exact Supabase organization and region at provisioning time; the current proposal is organization `catalyst`, Mumbai `ap-south-1`.
- Whether the old inactive Supabase projects should be permanently deleted. Do not delete them without explicit confirmation and backup understanding.
- The first model provider/model and backup provider/model. Architecture remains provider-independent until selected.
- Whether external research runs only from explicit research tasks at first or also from a bounded background-discovery policy.
- Which owner-authored object types Kev may enrich on day one.

## 21.3 Decisions that must not be guessed

- Work/Source identity and automatic deduplication rules.
- Exact cross-store storage atomicity guarantees.
- How Arivoo's existing auth and owner identity maps into Supabase.
- Whether a particular relation type should be treated as factual, interpretive, causal, or merely topical.
- Whether an owner correction is local or a global preference.
- Whether an external source is reliable enough to support a claim.

---

# 22. Implementation instructions to the first coding agent

Build Kev as a new repository and follow this order.

1. Read this specification completely. Treat owner decisions in §21.1 as requirements, not suggestions.
2. Create the repository foundation and documentation files. Do not implement a generic agent before the system contracts exist.
3. Inspect Arivoo's live `main` branch and discover the actual database schema, migrations, retrieval interface, write interface, MCP surface, identity model, and existing tests. Record evidence and exact commit hashes.
4. Produce an Arivoo integration boundary document. Name each interface Kev will call, its authorization behavior, its request/response schema, and its known limitations. If any interface is missing, create a separate Arivoo-side change request; do not write around it.
5. Inspect the Supabase account and create a dedicated `arivo` project only after rechecking organization, region, quote, and owner confirmation. Do not delete existing projects as part of project creation.
6. Create the first migrations for Kev's operational state in a private schema. Keep the schema small: tasks, task attempts, decision records, policy versions, provider health/config references, feedback, and evaluation run metadata. Avoid duplicating Arivoo's canonical knowledge objects.
7. Implement the event envelope and task state machine. Test transitions and duplicate delivery before connecting a live queue.
8. Implement the durable queue/outbox integration. Prefer same-transaction event enqueue where the actual Arivoo and Supabase architecture permits it. Otherwise use an outbox relay with idempotency and reconciliation.
9. Implement a read-only Arivoo adapter. Verify it against the actual API/commands and source revision semantics.
10. Implement the evidence context builder. The model should receive only task-relevant, provenance-preserving context.
11. Implement the provider protocol and one model adapter. Keep primary and backup selection in config. Add a second provider before claiming failover is implemented.
12. Implement exactly one model decision recipe: note-created -> candidate concepts/related objects with evidence.
13. Implement deterministic validation and one reversible write tool through Arivoo's supported interface.
14. Verify the action's exact postcondition. Record an audit trail and test duplicate task delivery.
15. Add arbitrary-text evaluation cases plus precise known-answer adversarial cases. Keep a held-out set.
16. Measure latency, task success, and error rates. Optimize only after a baseline exists.
17. Expand into the knowledge maintainer, external research, self-reorganization, and feedback loops in roadmap order.
18. Do not start multiple autonomous agents or a broad tool catalogue before the first end-to-end task has passed the V-model gates.

**The first milestone is not “Kev can chat.” The first milestone is: an owner action in Arivoo automatically causes one safe, evidence-backed, verified knowledge improvement in the background, with no extra user action.**

---

# 23. Reference material

Supabase platform and security behavior changes over time. Verify the current documentation and changelog immediately before implementation. The following sources informed the current infrastructure recommendations:

- Supabase changelog and breaking changes: https://supabase.com/changelog?types=breaking-change
- Supabase Queues: https://supabase.com/docs/guides/queues
- PGMQ extension: https://supabase.com/docs/guides/queues/pgmq
- Background job processing guidance: https://supabase.com/kb/faqs/background-jobs/background-job-processing
- PostgreSQL connection methods and pooling: https://supabase.com/docs/guides/database/connecting-to-postgres
- Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
- PostgreSQL roles: https://supabase.com/docs/guides/database/postgres/roles
- Supabase Storage access control: https://supabase.com/docs/guides/storage/security/access-control
- Supabase Storage uploads: https://supabase.com/docs/guides/storage/uploads/standard-uploads

Relevant current notes discovered during document preparation:

- Supabase Queues are built on `pgmq` and provide durable message storage, visibility-window delivery, and archival. Use the current docs and tests to verify the exact operational semantics; assume duplicate delivery is possible at the application boundary and make effects idempotent.
- Supabase documents the value of enqueuing work in the same transaction as the domain write when using PostgreSQL queues.
- Supabase RLS documentation stresses that grants and row policies are separate controls. Exposed tables need both correct grants and correct policies, with allow/deny tests.
- Supabase secret keys are privileged server-side credentials and must not be exposed in browsers or model context.
- Supabase CLI v3 changed to local-first behavior and asks before hosted changes. Pin/verify the CLI version and explicitly target the intended environment during deployment.
- Database direct connections may require IPv6; Supabase's shared session pooler supports IPv4 and may be the appropriate connection method for an IPv4-only worker environment. Confirm the actual runtime's network support before choosing.

---

# 24. Final product definition

Kev is not a chatbot attached to Arivoo. It is not merely a semantic search service. It is not a collection of prompts or a swarm of agents.

Kev is an autonomous, event-driven knowledge-maintenance system with a model inside it.

It receives the consequences of the owner's normal work, gathers relevant context, makes fast bounded judgments, creates and maintains knowledge structures, verifies all changes, preserves evidence and history, learns from corrections and evaluations, and discovers useful external information.

Its intelligence may change providers. Its policies may improve. Its knowledge organization may evolve. Its original evidence and identity history must remain recoverable.

**Arivoo is the knowledge base. Kev keeps it alive and growing.**
