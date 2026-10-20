> STATUS: REVIEW-ONLY ARTIFACT — 2026-10-20 (banner per D-024/D-022). Owner-forwarded third-party review, preserved verbatim as review evidence: NOT a canonical rule, NOT owner intent, NOT an implementation authorization beyond what DECISIONS D-041 records. The owner's words remain authoritative in INTENT-LEDGER.md (INT-127); interpretations, findings and recommendations live here and are triaged/routed to bounded cards per the turn-22 directive §1.3–§1.5 — never auto-adopted. Target reviewed: main at fbd1c13c2417de46334533f6214789011cd39983 (the supplied review's own stated baseline; re-verified live at session-22 preflight — local == origin, 0 open PRs). File received as arivoo-repository-review.md; body verbatim below, original title line included.

# Arivoo: engineering and systems review

Reviewed 2026-10-20 at `fbd1c13c2417de46334533f6214789011cd39983`. This is a review and recommendation, not an adopted repository decision. Repository source was unchanged. All reported test runs are fresh for this review.

## Assessment

Arivo has a coherent product purpose and unusually careful thinking about data ownership, provenance and recovery. The checked-in implementation is a development harness: PostgreSQL migrations, an immutable representative event table, a command ledger, one CLI command, and repository verification tools. Work/Source/Highlight/Note services, authenticated product APIs, local outbox, Supabase integration, retrieval and export/restore remain planned.

My strongest concern is the allocation of effort. The project has invested heavily in describing and checking its engineering process while the smallest valuable product transaction remains unbuilt. Some investment is justified: recovery and source identity are expensive to retrofit. But the process has also developed its own backlog of bookkeeping reconciliation and verification repairs. Its success should now be measured by how quickly it produces a capture that survives a failure and can be retrieved with its origin intact.

I would keep the core architecture, repair the concrete defects below through the existing bounded cards, and require an early product demonstration. I would not broaden the framework or add another general infrastructure phase.

## Findings, ordered by priority

The first five findings are already known in the repository's A03/A04/A05/A06/A09 register. This review independently reproduced them; it does not present them as new discoveries or resolved issues. Severity describes the existing harness contract and the risk of inheriting it into the product, not a production incident.

### 1. High: a successful verifier process can execute zero verification cases

Source: [verify_selftest.py](/home/vercel-sandbox/workspace/repos/github.com/prathamarchives/arivoo/tools/verify_selftest.py:30).

The trusted mutation suite imports the candidate verifier into its own process. In a disposable fixture, I kept the suite unchanged and replaced the candidate module with `raise SystemExit(0)`. Running the trusted suite exited 0 with no test output. The process result alone cannot establish that the trusted floor ran. The suite also treats ordinary checker exceptions as successful catches, weakening the meaning of its named-refusal assertion.

**Recommendation:** finish H-01b. Keep the controller and its dependencies outside candidate import/write authority; execute candidate behavior separately; require the expected cases, semantic outcomes and completion record. A child process by itself is not containment when candidate and judge share filesystem permissions. State the actual boundary honestly.

### 2. High: distinct command bodies can falsely replay the same result

Source: [commands.py](/home/vercel-sandbox/workspace/repos/github.com/prathamarchives/arivoo/harness/commands.py:118).

The command hash concatenates fields with `|`, without escaping or structural encoding. With owner `A`, actor `owner`, and the same idempotency key:

- Request 1: client `c|A|owner|x`, payload `y`.
- Request 2: client `c`, payload `x|A|owner|y`.

Both encode identically. On PostgreSQL 17.11, the second request returned a replay acknowledgment, while an independent read showed that only payload `y` existed. SHA-256 is working correctly; the input representation is ambiguous.

**Recommendation:** use a versioned, unambiguous canonical encoding; define exactly which fields constitute command identity. Test changed bodies, concurrent same-key requests and compatibility with existing recorded hashes before inheriting the primitive into P3-01.

### 3. High: migration failure can leave committed effects while reporting rollback

Source: [migrate.py](/home/vercel-sandbox/workspace/repos/github.com/prathamarchives/arivoo/harness/migrate.py:102).

The runner wraps migration text in `BEGIN` and `COMMIT`, but accepts transaction control inside the file. In a disposable database, a migration containing `CREATE TABLE ...; COMMIT; SELECT 1/0;` exited 1 and reported rollback. The table remained, and the migration bookkeeping row was absent.

**Recommendation:** define and enforce the admitted transaction-safe migration language. Prove rejection before execution, and compare database state after failure. Trusted migration authorship does not make the current unconditional rollback diagnostic accurate.

### 4. Medium: schema verification accepts missing applied history

Source: [migrate.py](/home/vercel-sandbox/workspace/repos/github.com/prathamarchives/arivoo/harness/migrate.py:116).

After applying all three migrations, I removed migration 0003 from a temporary directory and ran `--verify`. It exited 0. Verification iterates files that still exist without requiring every recorded applied version to remain present. It also calls bookkeeping bootstrap code during observation.

**Recommendation:** compare the applied and discovered histories in both directions; distinguish unapplied future files from missing applied files; validate the sequence consistently; make verification read-only.

### 5. Medium: deterministic evidence assembly is weaker than evidence validity

Source: [proofsheet.py](/home/vercel-sandbox/workspace/repos/github.com/prathamarchives/arivoo/harness/proofsheet.py:73).

Only the first 16 characters of each output digest enter the assembled sheet. Changing the final 48 characters left the sheet byte-identical. An independent verification pass also exercised the public CLI: a synthetic failed run, invalid revision identity and empty limitations could still produce a sheet; altered digest suffixes still verified successfully.

**Recommendation:** finish the evidence validation in H-02. Require typed records, full digests, command/fixture/revision binding, explicit expected outcomes and meaningful limitations. Preserve expected failing regression evidence as a distinct category. Reproducible formatting is useful, but cannot authenticate candidate-authored observations on its own.

### 6. Low: the scope matcher admits similarly named sibling paths

Source: [scope.py](/home/vercel-sandbox/workspace/repos/github.com/prathamarchives/arivoo/harness/scope.py:187).

The independent verifier demonstrated that a declaration for `README.md` accepts `README.md.unrelated`, because a raw `startswith(prefix)` supplements separator-aware matching. This is an additional observation beside the already documented A11 shared-path matcher defect. The claim coverage matcher uses stricter boundaries and mitigates a direct bypass when the claim is narrow; a whole-gate bypass was not demonstrated.

**Recommendation:** share one path-matching primitive with explicit file/directory semantics and sibling-prefix counterexamples.

## What I would preserve

- **Authoritative versus derived state.** Authored thought and source identity deserve durable history. Indexes, embeddings and rankings should be disposable and rebuildable. This is the correct foundation for long-lived personal knowledge.
- **Commit before acknowledgment, with durable idempotency.** Effect plus command record in one transaction is sound. The encoding and concurrency details need hardening, but the transaction model is appropriate.
- **Anchors tied to source versions.** A highlight that silently moves to the wrong passage is worse than an explicit unresolved location. Retaining selected text and location evidence is valuable.
- **Capture independent of enrichment.** Search/indexing/semantic failures must not block durable capture or retrieval by stable ID.
- **Small, inspectable code and actual failure injection.** The harness uses a real database, separate read role, replay checks and process-kill boundaries. These are useful proofs within their declared envelope.
- **API core with MCP as an adapter.** Transport should expose one authorization and command model rather than create another application path.

## Systems engineering opinions

### Establish one useful path early

The next product checkpoint should be: import one supported TXT/Markdown document, capture a passage with source/version identity, lose the acknowledgment, restart, retry, and retrieve the same capture through the actual authenticated boundary. Independent reads should confirm content, attribution and exactly one committed logical effect. Give the client an honest durability state.

That checkpoint can precede the complete journal, format ecosystem and semantic pipeline. Preserve their extension contracts; let actual capture behavior test the architecture before more abstractions accumulate. The existing plan already supports this direction.

### Keep the seven layers as logical responsibilities

A modular monolith with PostgreSQL, a deliberate blob boundary and a worker for retryable derived work is a sensible starting shape. Seven responsibilities do not justify seven services. Use transaction boundaries and failure isolation to decide what runs separately.

The subprocess/psql harness is a reasonable dependency-minimal convention proof. For a long-running product API, I would evaluate a maintained PostgreSQL driver under the existing dependency approval process: structured errors, parameter binding, connection lifecycle and transaction handling deserve library support. The current process protocol should not become the product kernel by default.

### Treat local/cloud durability as an interface decision

The local store, local mutation/outbox transaction, server acknowledgment, replay ordering and concurrent revision policy determine what “saved” means. Agree on that interface before code creates an accidental guarantee. Client-selected owner scope and trust-auth RLS tests establish the test setup, not authenticated tenant identity.

Likewise, database and blob storage cannot be atomically committed together. Staging, verified content identity, orphan recovery and restore/purge semantics are necessary contracts. Resolve Q11/Q12 at their dependent gates while provider-neutral work proceeds.

### Quantify the recovery envelope

Translate “nothing is lost” into named states and faults: process crash, uncertain acknowledgment, database restart, offline device, device loss and restoration from backup. State recovery point and recovery time targets for each. Killing a psql connection proves a narrower property than surviving power loss or restoring every source blob.

Test export/restore before accumulating irreplaceable owner data. A real recovery proof must compare authoritative content and references, not just row counts or schema columns.

### Reduce the cost of understanding the repository

The checkout has 13 root Markdown documents containing approximately 58,783 whitespace-separated words. AGENTS.md has 1,822 words; STATE.md has 1,308 despite its one-screen contract. Documentation volume is not automatically a defect, but it consumes agent context and creates synchronization obligations.

There is concrete drift: STATE calls CLAIM-010 active/open even though the checkout includes its merge, and CLAIM-007 appears in both open and closed tables. Current instructions acknowledge the closing-row reconciliation problem; it remains work the protocol creates for its next session. ENGINEERING also describes some controls in present tense that other documents correctly classify as planned or limited.

Keep history, but make the current navigation short and mechanically derived where possible. Distinguish enforced, discipline-only and planned controls at one existing authoritative home. Measure successful product changes, diagnosis time, escaped regressions and maintenance cost. More instructions should not be the default response to every failure.

## Validation and limits

Fresh local results:

- `make verify`: passed all four harness suites on PostgreSQL 17.11, known-bads and main selfcheck gate.
- Canonical verifier: 51 checks, 0 failures.
- Canonical mutation suite: 30/30; isolation selftest: 18/18; dispatcher regression: 45 assertions; gate known-bads: 13/13.
- Five existing defects reproduced in disposable fixtures/database; A09/A11 and the additional scope observation also checked independently.
- Live isolation checker: failed on sandbox-injected credential/metadata environment names. Minimal-environment run passed; the live failure remains a host/checker integration issue. No tracked-file credential leak was observed.

No production deployment, reader, Supabase, local sync, actual backup restoration or semantic retrieval was exercised. Those product flows are not implemented in this checkout. Remote CI/protection settings were not re-observed. Passing current tests does not close the reproduced defects.

## Recommended order

1. Complete the existing H-01 trust repairs with bounded acceptance criteria.
2. Make H-02 evidence and independent verification meaningful at the actual gate caller.
3. Repair P3-K0/P3-M0 primitives before product code inherits them.
4. Accept the minimum identity, storage and capture interfaces at their existing gates.
5. Demonstrate the first real capture/restart/replay/retrieve transaction, then expand from observed behavior.

My overall judgment: the underlying design is worth building. Its next credibility gain will come from a small amount of dependable product behavior, supported by narrowly accurate verification claims.
