# 22 — the Arivoo execution directive intake: current state through Phase 4 completion

> STATUS: SESSION ENGINEERING RECORD — IN PROGRESS (session 22, 2026-10-20; owner turn 22, INT-127; §1 preserved verbatim below BEFORE any ledger entry — the INT-046/068 class; the access credential in the turn's first line is REDACTED at ingestion per INT-092/D-025, the record-20 precedent; nothing else was redacted). §4–§12 land at this session's close slice. Historical process artifact per D-022: NOT owner intent, outranks nothing; owner words live only in `/INTENT-LEDGER.md`.

## §1 — the owner's turn, verbatim

The turn arrived as an IM message with three attachments. The message text (credential redacted; the owner's typography preserved, including "dependiencies", "reaosn", and "an execute"):

> ghp_[REDACTED — access credential; never recorded in repo files (INT-092/D-025)] setup gh, cli, dependiencies, postgres, supabase. review repo, get context, read reviews, debug ruthlessly... think as a systems engineer... an execute the 3rd attached aka pasted content.... divide this directive in layers in your workspace and reason through those layers to divide sub layers and reaosn with each of em plan, reason and reason step by step and then execute through each

Attachment dispositions (the turn's own instruction: the third attachment — the pasted content — is the directive to EXECUTE; the first two are the review context to read):

1. `security-findings-prathamarchives-2026-10-20.pdf` — the CodeRabbit security findings report (13 open findings). Preserved as received at `context/reviews/coderabbit-security-findings-2026-10-20.md` (review-only artifact, D-022 banner; triaged in §2, routed in PLAN per the directive §1.3/§5.5).
2. `arivoo-repository-review.md` — the engineering and systems review at `fbd1c13`. Preserved verbatim at `context/reviews/arivoo-repository-review-2026-10-20.md` (review-only artifact, D-022 banner; its six concrete defects map onto the EXISTING defect register A03/A04/A05+A06/A09/A11 — independently reproduced by the reviewer, never presented as new discoveries; its claim-bookkeeping observation is confirmed and repaired in this slice, §2).
3. `Pasted Content_1792480917297.txt` — **the execution directive, the turn's operative content, preserved verbatim below.**

The directive verbatim (542 lines as received; section numbering, typography, and the owner's em-dash conventions preserved):

---

# Arivoo execution directive: current state through Phase 4 completion

**Prepared:** 2026-10-20  
**Primary repository:** `prathamarchives/Arivoo`  
**Related client repository:** `prathamarchives/arivodesign` where client integration is required  
**Observed backend baseline in the supplied review:** `fbd1c13c2417de46334533f6214789011cd39983`  
**Purpose:** Execute the existing roadmap, repair trust and data-integrity defects before the product inherits them, complete Phase 3, establish the Phase 4 foundation, implement Phase 4, and carry out seven documented refinement rounds. This is an execution brief, not an adopted repository decision. The live repository may have advanced; verify the actual checkout before editing.

---

## 1. Current picture: what exists, what does not, and what the evidence means

### 1.1 Product and implementation reality

Arivoo's product thesis is coherent: durable reading, capture, writing, provenance and research context that compounds over time. The engineering decisions worth preserving are authoritative state separated from derived state, version-aware source anchors, idempotent commands, commit-before-acknowledgment, rebuildable search/enrichment, bounded authorization, export/restore and an API core that can later be exposed through thin adapters.

The checked-in implementation observed by the supplied review is still primarily a **development harness**, not the product backend. It contains PostgreSQL migrations, a representative immutable event table, a command ledger, one CLI command and repository-verification tools. The following product capabilities were still planned rather than implemented in that review: Work/Source/Highlight/Bookmark/Note services, authenticated product APIs, real client workflows, local outbox and cloud sync, retrieval, and export/restore.

That distinction must control every status statement. A passing harness is evidence about the harness contracts that ran; it is not proof that capture, authentication, sync, restore, the reader or semantic retrieval works. Do not use future-tense plans as if they were present capabilities. Do not mark a Phase 3 or Phase 4 requirement complete because a schema, mock, CLI placeholder or synthetic fixture exists.

### 1.2 Existing verification is useful but does not clear the reproduced defects

The supplied engineering review reports a fresh `make verify` pass on PostgreSQL 17.11, including four harness suites, known-bads and the main selfcheck gate. It reports a canonical verifier with 51 checks and zero failures, mutation suite 30/30, isolation selftest 18/18, dispatcher regression 45 assertions and gate known-bads 13/13.

The same review also independently reproduced defects in disposable fixtures/databases. The passing suites did not detect them, so the first task is not to announce green CI as sufficient; it is to make the gate demonstrate that it actually ran, accepted only valid results, and refuses known-bad inputs.

The engineering review additionally reports stale claim bookkeeping: `STATE.md` describes `CLAIM-010` as active/open even though the referenced merged work is present, and `CLAIM-007` appears in both open and closed tables. Reconcile this using the existing closure protocol and preserve history. Do not rewrite history or turn bookkeeping cleanup into a new infrastructure phase.

### 1.3 Security scanner snapshot

The supplied CodeRabbit report was generated on 2026-10-20 and lists **13 open findings: 2 medium, 11 low, 0 critical and 0 high** under the report's filters. It warns that the count covers the included findings and current filters, not all security posture. Treat these as leads to reproduce against the live HEAD, not as independently confirmed truths and not as findings that can be dismissed by their nominal severity. Each must end with a recorded disposition and evidence: reproduced/fixed, reproduced/not yet fixed, not reproducible with stated reason, duplicate of a more precise finding, or requires repository-host configuration/owner action.

The engineering review and scanner overlap in the path matcher, candidate trust boundaries and migrations. Merge overlapping work into the existing bounded cards instead of creating parallel fixes that fight each other.

### 1.4 Six concrete defects from the engineering review

1. **Verifier completion can be forged by a successful early exit.** The unchanged trusted mutation suite was made to import a candidate verifier that executed `raise SystemExit(0)`. The suite exited zero with no output. Ordinary checker exceptions can also be treated as successful catches. Process exit status alone does not prove the required cases ran.
2. **Command identity encoding is ambiguous.** Fields concatenated with `|` can encode distinct command bodies identically. In the supplied PostgreSQL reproduction, the second request received a replay acknowledgment while an independent database read showed that only the first payload existed.
3. **Migration rollback reporting is false in a transaction-control case.** A migration containing `CREATE TABLE ...; COMMIT; SELECT 1/0;` exited nonzero and reported rollback, yet the table remained and the migration ledger row did not.
4. **Migration verification accepts missing applied history.** Removing an already-applied migration file still allowed `--verify` to exit zero. Verification also bootstraps bookkeeping while claiming to be observational.
5. **Proof-sheet digests and records are not sufficiently validated.** Only the first 16 hex characters of a digest enter the assembled sheet; changing the suffix left the sheet byte-identical. Invalid revision identity, synthetic failed runs and empty limitations could also pass parts of the public CLI path.
6. **Path matching accepts a sibling-prefix collision.** A file declaration for `README.md` accepted `README.md.unrelated` due to raw prefix matching. The review notes an additional shared-path matcher defect and recommends one explicit file/directory matching primitive.

The review says the first five findings were already tracked in the repository's defect register; do not present them as new discoveries or mark them resolved merely because this review is now attached.

### 1.5 The 13 scanner findings to triage and route

- **F-001 — authorization/scope path parsing:** Git's human-formatted diff parsing can mishandle quoted filenames and renames; paths can escape protected-prefix matching and diff statistics can be undercounted. Use machine-safe NUL-delimited records, correctly account for both rename endpoints, and apply one parsing contract to scope, claims and size accounting.
- **F-002 — scanner resource exhaustion:** `tools/isolation_check.py` may follow symlinks and read a target without bounds. Reject unsafe file types, scan symlink text rather than dereferencing repository targets, and impose per-file/total byte budgets with race-resistant handling where worktree reads are needed.
- **F-003 — candidate-controlled workflow definition:** the PR can influence the workflow that purports to run authoritative verification. Verify what the host actually executes and whether the workflow is protected independently of the candidate. A code-only change to the same candidate-controlled workflow cannot, by itself, prove the trust boundary it claims.
- **F-004 — candidate-controlled Make recipes:** the workflow accepts candidate-edited recipes as proof that required suites ran and may skip its own checks after they return success. The trusted driver must independently select required commands and validate completion.
- **F-005 — candidate import shadowing:** trusted judges launched from a candidate-controlled directory may import a candidate `shutil.py` or other shadow module and exit before judging. Run judges from trusted locations with a controlled/isolated import path and pass candidate paths as data.
- **F-006 — candidate known-bad registry executes inside the gate:** top-level candidate code can terminate the gate successfully before required checks. Keep the required case registry/driver protected or independently validate it; execute untrusted candidate behavior outside judge authority.
- **F-007 — RED test hashes can self-authorize changes:** the candidate may alter a frozen test and update the hash in the candidate registry. Compare frozen test identity to trusted prior state and require independently authorized amendments to exact content.
- **F-008 — branch name can suppress claim checks:** an attacker-selected `main-selfcheck`-style name may select an exemption despite PR diff mode. Enforce claims based on trusted invocation mode, not contributor-selected branch or slice labels.
- **F-009 — destructive migration policy uses fragile text matching:** comments between SQL keywords can evade the destructive-operation guard. Use a PostgreSQL-aware parser or a deliberately narrow accepted SQL grammar that fails closed when it cannot classify executable constructs.
- **F-010 — migration filename is interpolated into SQL:** restrict migration names to a documented safe alphabet and use safe literal handling/parameter binding for ledger values; prove a crafted filename cannot inject a statement.
- **F-011 — isolation self-test fixture copy follows symlinks:** reject symlinks/non-regular entries before copying and enforce a total copy budget; ensure cleanup is established before fixture construction starts.
- **F-012 — setup failure may leak secret-shaped filenames:** put fixture construction inside the sanitized error boundary; output a fixed safe diagnostic and exception type, not raw filenames/tracebacks; test with synthetic secret-shaped paths and assert they are absent from stdout/stderr.
- **F-013 — verifier self-test fixture copy follows symlinks:** apply the same bounded, no-dereference fixture strategy to `tools/verify_selftest.py`; do not let a tiny symlink trigger an unbounded stream read or fill the runner filesystem.

For each finding, independently check whether the exact path, code and trust boundary still exist in the current checkout. If the relevant line has moved, follow the behavior rather than relying on line numbers. Do not claim the repository-host settings (workflow protection, required checks, branch protection) are fixed unless those settings were actually inspected and the result recorded. If a remedy requires owner/admin settings unavailable to the agent, implement all safe repository-side mitigations and record the exact external configuration still required.

### 1.6 Product checkpoint that matters

The earliest meaningful product demonstration is not a large dashboard or a full format ecosystem. It is this end-to-end path:

1. Import one supported TXT or Markdown document.
2. Persist its logical identity and source-version identity.
3. Capture a passage as a Highlight with a location/anchor tied to that exact Source version.
4. Simulate a lost acknowledgment or process interruption.
5. Restart and retry the same command.
6. Prove exactly one logical effect committed and the retry returns the correct stored result.
7. Retrieve the capture through the real authenticated product boundary, including its source and provenance.
8. Independently read persisted state; do not validate a write only through the command's own response.

This checkpoint should arrive early in Phase 3. It must then expand to Bookmarks, Notes/revisions, keyword retrieval, owner isolation, local/cloud durability boundaries, and recovery.

---

## 2. Operating mandate for the coding agent

**Execute code and tests; do not return another roadmap instead of implementation.** Use the repository's existing `PLAN.md` as canonical roadmap, `DECISIONS.md` for open decisions, `CLAIMS.md` and the existing claim protocol for slice ownership/evidence, and `STATE.md` as a snapshot that must be updated only after the underlying state changes. Read `AGENTS.md`, `OPERATING-MODEL.md`, `EXECUTION.md`, the current defect registers, and relevant tests before changing anything. The supplied reviews inform the work but are not adopted repository decisions by themselves.

### Non-negotiable rules

1. **Re-establish live truth first.** Fetch the current repository state; record the real HEAD, branch, worktree status, required checks and available environments. The supplied SHA is a reference point, not an assumption that HEAD is still there. Do not overwrite user changes. Work on an appropriate feature branch and preserve existing PR/protection protocols.
2. **Follow the existing bounded-card discipline.** Finish and close a card with specific acceptance evidence before taking dependent work as complete. Do not add a new generic infrastructure phase. Do not broaden the framework to compensate for a concrete failed test.
3. **Protect the test oracle.** Never allow the code being evaluated to decide which tests ran, what results count, where the trusted judge writes, or whether failed checks are silently skipped. Process isolation without filesystem/authority separation is not enough.
4. **Reproduce before fixing; preserve a regression test after fixing.** Every reproduced defect needs a minimal red test, a fix, a passing targeted test, adjacent counterexamples, and a fresh full relevant suite. Scanner findings must be triaged, not blindly believed or blindly closed.
5. **No success from a single green exit code.** Check the expected case list, counts, semantic outcomes, artifact/revision binding and completion manifest. Zero tests, missing output, malformed evidence, unexpected exceptions and incomplete manifests must fail closed.
6. **Separate authoritative from derived state.** Source identity, captures, authored notes and revisions are durable authoritative data. Keyword indexes, vectors, embeddings, rankings and enrichment candidates are derivable. Derived-work failure must not erase, delay or falsify a committed capture.
7. **Commit before acknowledgment.** A command's domain effect and idempotency/command record must commit atomically in the same datastore transaction. Never acknowledge durability before commit. Where database and object/blob storage differ, explicitly model staging and recovery; never promise cross-store atomicity.
8. **Never invent owner approval.** Keep Q6/Q7/Q8/Q9/Q10/Q11/Q12 and D-014 constraints visible at their exact dependent boundaries. Resolve reversible implementation details from existing conventions and document the choice. Do not invent identity/deduplication policy, raw-context visibility, token scopes or provider-specific persistence decisions. Keep all unblocked work moving while a genuinely owner-gated boundary remains pending.
9. **Do not make Phase 5 semantic claims early.** Phase 4 includes scoped baseline agent access as specified in the plan, but vector/semantic ranking, Kev-backed evidence promotion, concept graduation and graph compounding are Phase 5 gates. Do not introduce them as a way to mask weak keyword retrieval or missing product capture.
10. **No silent widening of identity or privacy.** Do not merge logical Works/Sources because titles, filenames or bytes match. Physical blob deduplication, when approved, is not logical-entity deduplication. Use server-derived authenticated identity, not a client-supplied owner ID as the authorization authority.
11. **Truthful status only.** Distinguish implemented, tested locally, verified in CI, verified in a clean clone, manually inspected, blocked by owner choice and not tested. Synthetic fixtures can validate mechanics; they cannot prove real PDF/EPUB anchor stability, production identity, remote workflow protection or an actual backup restore.
12. **Small, reviewable increments.** Prefer the smallest useful end-to-end vertical slice; write the test first for an identified defect; implement only the necessary abstraction; run targeted and regression tests; inspect the diff; commit with traceable intent. Avoid large speculative rewrites.
13. **Update documentation after the behavior is real.** Keep claims, `STATE.md`, work log, proof sheets, plan and decisions synchronized through existing procedures. Do not write “enforced” when a rule is discipline-only or merely planned.
14. **Continue autonomously across phases.** Do not stop after presenting findings or an implementation plan. Execute the unblocked sequence in this directive in one sustained run/session when repository tools permit. Pause only for a real permission boundary, a destructive action needing approval, or an owner decision that would otherwise force an irreversible or privacy-sensitive product assumption. When blocked, finish independent work and state the exact minimum decision required.

---

## 3. Startup and baseline procedure

Before modifying source:

1. Fetch/reopen the current `prathamarchives/Arivoo` HEAD. Record SHA, branch, dirty state, open PR/work in progress, available CI workflows and required checks. If relevant client access is available, inspect `prathamarchives/arivodesign` independently; do not assume the repositories share a transaction, branch or release state.
2. Read and follow `AGENTS.md`, `PLAN.md`, `STATE.md`, `EXECUTION.md`, `DECISIONS.md`, `CLAIMS.md`, `OPERATING-MODEL.md`, the defect register and the existing proof-sheet/RED protocols. Identify the canonical files and avoid duplicate sources of truth.
3. Run the documented baseline on a clean worktree and record the exact commands, exit codes, environment versions, output artifacts and known failures. Run relevant tests in a clean clone if practical. Confirm whether PostgreSQL is real and what database/version the test uses.
4. Check the current `make verify` path end to end. Trace from the CI event through workflow selection, checkout, dispatch, gate, trusted judge, child candidate execution, result parsing, and final green/red decision. Inspect repository-host protection separately when permissions allow.
5. Reconcile `CLAIM-010` and the duplicate `CLAIM-007` table state through normal repository procedure. Prove the reconciliation with current merge/closure evidence. Do not alter historical commits or make a claim disappear merely to pass a checker.
6. Create/update a concise current work ledger: finding/card, baseline reproduction, assigned files, red test, fix, required validation, status and dependency. This ledger must reduce context switching, not add a new document system.

Deliverable from baseline: a verified starting SHA; an honest list of current baseline failures; each review/scanner finding mapped to an existing or newly split *bounded card*; and the first implementation card started immediately. Do not wait for a perfect inventory before fixing H-01b.

---

## 4. Immediate next step: H-01b trusted candidate-tool execution floor

This is the first engineering execution card after the tiny claim-bookkeeping reconciliation. It blocks trust in the rest of the verification pipeline and therefore must be repaired before product code inherits its claims.

### 4.1 Attack model to make explicit

Treat every file, test, tool, Make recipe, branch name and generated artifact from a PR candidate as untrusted input. The candidate may try to:

- exit successfully before the judge reaches a test;
- replace or shadow a Python standard-library/dependency import;
- execute top-level code when a candidate registry/module is imported;
- edit the runner, expected-case list, completion manifest, RED record or anchor file;
- return no output, partial output, duplicate case names, fabricated results or malformed results;
- mutate the shared fixture or delete evidence while the trusted process is still relying on it;
- exploit a symlink, special file, race or oversized file to hang or exhaust memory/disk;
- raise a generic exception that gets misclassified as a successful refusal;
- change a Make recipe or workflow step so it returns success without running mandatory tests.

A subprocess by itself is not containment if the child can write the judge's files, overwrite the case registry, alter trusted fixtures, or share mutable authority with the judge.

### 4.2 Implement a trusted controller and separately constrained candidate execution

1. Keep the controller, expected-case registry, harness anchors and result validator in a trusted location that candidate execution cannot modify. Launch trusted logic from outside the candidate tree with an isolated/controlled import path. Pass the candidate worktree as an explicit data path; do not import candidate modules into the judge's interpreter.
2. Execute candidate behavior in a separate process with an explicit timeout, bounded stdout/stderr, controlled environment and appropriate resource limits where supported. Record the actual isolation envelope and its limitations. Do not claim stronger OS/container isolation than the runner supplies.
3. The controller must know the exact required cases from trusted state. Require every expected case exactly once, with a valid semantic result and a completion record bound to the specific run, candidate SHA, fixture identity and expected-case-set digest. Missing, duplicate, unknown or malformed cases fail closed.
4. Validate results independently of candidate exit status. A zero exit with no output, truncated manifest, incomplete case set, malformed JSON, unexplained exception or self-declared “passed” status must fail. Expected red regression outcomes are a separate typed category from acceptance-test passes.
5. Prevent candidate code from changing the judge's trusted files and result anchors. Use immutable/read-only fixtures where possible; separate candidate-owned writable temp space from controller-owned output; verify fixture identity before and after runs. If the implementation cannot prevent a class of mutation, narrow the claim and add an explicit residual-risk gate.
6. Remove import-shadowing paths for the trusted judge. Test candidate-added `shutil.py` and similarly named local modules, altered `PYTHONPATH`, startup hooks and malicious known-bad registry code. Do not execute candidate code at trusted module import time.
7. Do not accept `make harness-health` or `make harness-tests` as proof that tests ran just because candidate-defined recipes return success. The trusted driver itself must select and invoke the required suites, then verify their expected case manifest.
8. Determine whether GitHub Actions actually executes candidate-controlled workflow definitions. If a protected reusable workflow or other independent trust boundary is needed, implement available repository-side changes and specify any required repository-host/admin configuration separately. Never claim this finding is fixed by editing a candidate-controlled workflow alone.

### 4.3 Harden fixture construction and cleanup within this card

- Inspect tracked object modes; do not dereference arbitrary repository symlinks for scanner/self-test fixtures.
- Reject or safely represent symlinks, devices, sockets, FIFOs and other non-regular entries before copy/read. Apply file-count, per-file-byte and total-byte budgets. Use race-resistant open semantics when scanning a mutable worktree is unavoidable.
- Put temporary-directory creation and fixture-copy work inside one cleanup/error-handling scope that begins before copy starts. Ensure cleanup is attempted even when fixture construction itself fails.
- Sanitize setup failures. Emit a fixed diagnostic plus a safe exception class; do not print raw filenames, traceback locals or path components that may contain secrets. Add synthetic credential-shaped path tests that assert the secret-shaped value never appears in either output stream.
- Test non-terminating stream targets, oversized regular files, dangling links, symlink swaps/races where feasible, failed copy cleanup and total-budget exhaustion. Do not allow a fixture test to consume the runner's disk or hang CI.

### 4.4 Required red tests for H-01b

At minimum, add or preserve regressions proving the trusted gate fails for each of these mutations:

- candidate verifier replaced with `raise SystemExit(0)`;
- candidate returns success but writes no result manifest;
- expected test omitted, duplicated, renamed or replaced by an unknown test;
- malformed/truncated result output and an ordinary exception not matching the expected refusal;
- candidate `tools/shutil.py` shadows the standard library if the judge is launched incorrectly;
- candidate known-bad registry executes `SystemExit(0)` at import;
- candidate Make recipe reports success without invoking the suite;
- candidate attempts to modify the controller, expected cases or evidence file;
- symlink/FIFO/device-like target, oversized file and failed fixture-copy cleanup;
- secret-shaped filename during fixture failure;
- bounded stdout/stderr overflow or timeout;
- the valid unchanged candidate runs every expected case and produces a complete independently validated result.

Make each regression fail for the right reason; do not count an arbitrary exception or any nonzero exit as proof of the named security control. Keep acceptance and expected-red assertions distinct.

### 4.5 H-01b exit gate

H-01b is complete only when:

- the original premature-success exploit is a stable regression and fails closed;
- valid code can still complete all required cases;
- the controller validates exact expected case identity, cardinality and semantic outcomes;
- candidate code cannot modify the controller/result authority within the claimed boundary;
- test fixtures have bounded resource consumption and safe cleanup/diagnostics;
- required checks run through the trusted CI path, not merely a developer local command;
- the actual isolation boundary and residual risks are written accurately;
- full baseline verification passes, and an independent review tries to break the new mechanism.

Once this gate is green, continue directly to the H-01c splits below. Do not pause for a broad status memo.

---

## 5. Finish H-01c and H-02: claims, authority, path scope, evidence and privacy

Keep these as separate bounded cards with disjoint file ownership where parallel work is helpful. Do not let parallel agents edit the same gate/claim files without explicit coordination. H-02 activation remains dependent on the trusted H-01b floor.

### 5.1 H-01c-claims: strict parsing and complete path identity

- Make claim parsing fail closed on missing sections, malformed rows, truncated/disappearing rows, unexpected duplicate IDs, duplicate open/closed entries and unknown status vocabulary.
- Normalize and validate integer/numeric issue identifiers without accepting ambiguous alternate rows.
- Reconcile `CLAIM-010` and `CLAIM-007` using the existing closure protocol; retain closure evidence and history.
- Use machine-safe Git diff output (NUL-delimited records) instead of parsing human-quoted filenames. Account for both source and destination of a rename. Apply one validated path list to protected-scope checking, claim coverage, file-size/stat accounting and related policy checks.
- Centralize path matching with explicit semantics: exact file match, directory path boundary, rename endpoints, deleted paths, quoted/unusual names and path normalization. A declaration for `README.md` must not match `README.md.unrelated`. A declaration for a directory must match descendants but not sibling prefixes.
- Do not let contributor-controlled branch or slice names suppress claim enforcement. Claims remain mandatory whenever the trusted invocation is PR-diff mode. Reserved selfcheck names must not alter the trust mode.
- Test spaces, quotes, newlines, Unicode, leading dashes, nested directories, sibling prefixes, add/delete/rename/copy and mixed file/directory declarations. Where Git's path model and the policy model differ, document the exact conversion rather than guessing.

### 5.2 H-01c-authority: trusted references and quoted evidence

- Bind trusted reference digests and critical anchors to a trusted base/revision, not to a candidate-editable artifact that can simply refresh its own digest.
- Make a re-anchor a distinct owner/verifier-authorized operation that records which trusted baseline changed, why it changed and what exact new content is approved.
- Validate cited quote/span content against the trusted raw evidence that it claims to represent. Missing, altered, stale or ambiguous source text fails closed.
- Ensure the controller does not infer authority solely from filenames, branch labels, a PR-provided hash or candidate-supplied metadata.
- Add negative tests for edited anchors plus refreshed candidate hashes, changed quoted spans, wrong revision, path aliases and a forged re-anchor record.

### 5.3 H-01c-evidence-privacy: RED semantics, observations and diagnostics

- Freeze the identity/hash of regression tests against trusted prior state. An update to a test is not independently authorized merely because a contributor ran `red.py --note` or updated a candidate JSON hash. Require the existing independent approval/amendment procedure for changed frozen tests.
- Validate typed observed RED results, suite inclusion, expected refusal semantics and test identities. A written assertion or self-reported finding is not the same thing as an observed failure.
- Redact secret-shaped data from stdout, stderr, exception messages and generated artifacts. Test a synthetic canary through normal and failure paths. Do not dump environment variables or raw exception tracebacks into evidence.
- Preserve the distinction between a known-bad expected to fail and a happy-path acceptance test expected to pass; do not make the whole suite green by weakening the expected outcome.
- Ensure shared-file/append operations cannot destroy existing records silently. Make append/rewrite semantics explicit and test collisions and concurrent writers if the protocol allows them.

### 5.4 H-02: meaningful proof sheets and evidence verification

- Use a versioned typed record schema. Require full digest strings and validate the entire value, not a prefix. Validate format, length, identity and allowed algorithm.
- Bind every record to the actual command, test/case, fixture, candidate revision/SHA, trusted reference revision, run ID and expected semantic outcome as applicable. Recompute the digest over a documented canonical representation.
- Reject invalid revision identity, placeholder or “not verified” claims presented as verification, empty/meaningless limitations, absent required records, unknown record types, duplicate contradictory records and candidate-invented results.
- The trusted verifier must verify the evidence, not merely format it. Altering any digest suffix must cause verification failure. A synthetic failed run must not produce an acceptance PASS. A proof sheet must show its limits.
- Bind the sheet to the trusted run/manifest and validate the full expected case set. Distinguish observed failing RED evidence from passing acceptance evidence and from unverified/manual notes.
- Test the public CLI, the actual gate caller and the artifact consumer. Fixing only the helper is insufficient if the caller still accepts invalid evidence.
- Do not describe evidence as cryptographically authenticated if it is only deterministic formatting. State what protects the signer/runner, what is candidate-controlled and what remains trusted by convention.

### 5.5 Route the CodeRabbit findings into these cards

- F-001 -> H-01c-claims path parsing, rename coverage and shared path matcher.
- F-005 and F-006 -> H-01b protected judge startup/import path and candidate registry execution.
- F-007 -> H-01c-evidence-privacy trusted RED baseline/amendment validation.
- F-008 -> H-01c-claims trusted PR mode rather than branch-name exemptions.
- F-002, F-011, F-012 and F-013 -> H-01b bounded file scanning/fixture construction/cleanup/privacy.
- F-003 and F-004 -> H-01b or a clearly linked CI trust sub-card; identify host-level protection requirements separately.

Do not close any card until the live code, the real gate caller and the regression all demonstrate the intended behavior.

---

## 6. Phase 3: tighten the contracts, then implement the real product backend

Phase 3 must not become another general harness-polishing campaign. Once H-01b/H-01c/H-02 are accepted, execute the Phase 3 cards in the canonical `PLAN.md`. Freeze the minimum interfaces, then build the smallest real vertical slice and expand it. Use the exact identifiers in the live roadmap if they have changed; do not create parallel competing naming systems.

### 6.1 P3-00 — requirements, boundaries and interface freeze

Before product migrations, produce a traceability matrix mapping each `SYS-01` through `SYS-11` to:

- the component/layer responsible;
- authoritative data and lifecycle states;
- public/internal interfaces and identity/provenance fields;
- transaction boundary and failure semantics;
- migration and compatibility behavior;
- specific automated test(s), adversarial test(s) and independent verification evidence;
- acceptance requirement and remaining limitation;
- relevant claim/card and upstream dependency.

Define Work, Source, SourceVersion/extraction generation, Highlight, Bookmark, Note and revision identifiers; owner/actor/provenance; tombstone/purge semantics; idempotency scope; source-version anchor fields; transaction boundaries; read models; index invalidation; command errors; API DTOs; outbox event contract; export/restore envelope; and data-retention states.

The interface freeze is not a giant implementation spec. It is a concise, testable contract. Keep Q11 and Q12 visible at the boundaries they affect. Do not add title/filename uniqueness or automatic logical-entity merges. Do not pick a provider-specific blob schema or promise database/blob atomicity before the Q12 contract is ratified. Keep provider-neutral staging and identity work moving.

P3-00 is accepted when each SYS requirement has an owner, an observable test and a named component; dependent interfaces do not contradict one another; the recovery and authorization invariants are explicit; and the remaining open decisions are accurately scoped. No product migration should precede this acceptance.

### 6.2 P3-M0 — migration safety and observation-only verification

Harden the migration substrate before product schemas build on it:

1. Define an admitted migration language/contract. Reject transaction control embedded in migration bodies before executing any SQL. Do not rely on a naïve regex for SQL policy. Use a PostgreSQL-aware parser where suitable, or restrict executable syntax and fail closed whenever the checker cannot safely classify it.
2. Reproduce and fix the reported `CREATE TABLE; COMMIT; failing statement` case. A rejected migration must have zero schema/data/ledger effects. Compare real database state before and after, not just exit output.
3. Make `--verify` observational/read-only. It must not bootstrap, repair or modify the bookkeeping state it is inspecting.
4. Compare discovered migrations and applied ledger in both directions. Missing already-applied files, duplicates, sequence gaps, altered applied content, unknown ledger entries and invalid ordering must be handled explicitly. Distinguish legitimate unapplied future files from missing history.
5. Fix destructive-operation detection so comments, quoted identifiers and line breaks cannot turn a dangerous statement into a false safe result. For syntax that cannot be classified, reject or require the approved explicit path.
6. Restrict migration filenames to a documented safe alphabet. Never interpolate an untrusted filename/name into SQL unsafely. Use safe parameter/literal handling through the approved database adapter.
7. Prove migration failure leaves no effects or false success claims. Test transaction-control statements, comment-separated destructive tokens, crafted filenames, modified/missing applied migrations, read-only verification and bootstrap on an initially empty test database.
8. Keep migrations forward-compatible and review schema changes for constraints, indexes, ownership and RLS behavior. A schema existing is not proof of authorization behavior.

Route CodeRabbit F-009 and F-010 here, along with the engineering-review transaction rollback and missing-history findings. Add explicit red tests before fixes.

### 6.3 P3-K0 — command kernel primitives

1. Replace separator concatenation with a versioned canonical structured encoding. Define exactly which fields constitute command identity and payload equivalence. Serialize deterministically with explicit types and unambiguous boundaries; do not invent normalization of authored user content. Where Unicode normalization is part of identity, make that a documented versioned rule and test it; otherwise preserve content bytes/semantics exactly as contracted.
2. Define a versioned command envelope: command type, request-schema version, authenticated owner/actor context, stable idempotency key, payload, expected revision/version where needed, and provenance. The owner identity must come from authenticated server-side context, not a caller-selected `owner_id` used as authority.
3. Define same-key/same-body replay, same-key/different-body refusal, unique-key concurrency, transaction retry and acknowledgment behavior. Use database constraints/locking/serializable strategy as appropriate and test real concurrent requests against PostgreSQL.
4. Preserve compatibility with any existing recorded hashes/ledger entries through an explicit versioned migration/compatibility plan. Do not silently reinterpret old command hashes.
5. Validate UUID version/variant and stable-ID behavior where the repository contract requires it; preserve timestamp/compatibility semantics and reject malformed identifiers.
6. Evaluate the approved maintained PostgreSQL driver for long-lived application use. The current `psql` subprocess can remain a dependency-minimal harness proof, but must not automatically become the product kernel. Follow the existing dependency approval process and test parameter binding, transaction lifecycle, connection cleanup and structured error mapping.
7. Maintain named domain errors and a single command path for mutation. Each mutation must pass through the same auth, ownership, transaction, idempotency and provenance checks; avoid privileged side doors.

Required tests: delimiter collision from the review; Unicode and boundary cases; reordered structured keys; changed owner/actor/type/schema/body; repeated key; same key with different body; two concurrent same-key identical requests; two concurrent same-key conflicting requests; process killed before commit; process killed after commit but before acknowledgment; database disconnect with uncertain result; retry after restart; independent DB read verifies effect and ledger consistency.

### 6.4 P3-01 — first real product command and capture transaction

Build one real, attributed, scoped and atomic product command—not another representative harness event. It must take an authenticated actor/owner context, validate a typed request, write the domain effect and command/idempotency record atomically, commit, and only then acknowledge. It must be independently inspectable in PostgreSQL and recover correctly across uncertainty/replay.

Use this to validate the P3-00 contracts in running code. Inject failures at meaningful transaction boundaries and prove the invariants. Demonstrate the TXT/Markdown import + passage capture checkpoint from Section 1.6 as early as possible. If the repository currently lacks a suitable API/auth skeleton, build the smallest product boundary needed for that path rather than creating all services before one command works.

P3-01 acceptance: actual persisted domain rows and command ledger agree; exactly one logical effect after replay; conflicting same-key request refuses; unauthorized owner cannot access or mutate the record; success response is post-commit; independent DB read confirms content, provenance and owner; process-crash/uncertain-ack tests pass; no reliance on mocked database behavior for these claims.

### 6.5 P3-02 — Work/Source intake

- Implement supported TXT/Markdown intake with explicit media type, acquisition metadata, source digest/content identity, import state and stable IDs.
- Validate size/encoding/content boundaries. Treat malformed/unsupported input as explicit errors, not silent success.
- Keep logical Work identity separate from Source/acquisition identity. Duplicate imports remain distinct logical records by default unless a decision explicitly authorizes another behavior. Byte-level blob reuse must not silently merge Works or Sources.
- A missing title, identical filename or equal content hash must not cause a logical entity merge.
- Staged bytes and authoritative source references must have clear state, cleanup/recovery rules and observable failure results.

### 6.6 P3-03 — source versions, extraction generations and anchors

- Represent Source versions and extraction generations with explicit version/provenance state. Incomplete or failed extraction must never be labeled ready.
- Implement a stable anchor contract that stores enough location evidence and selected text to resolve a Highlight against the exact source version it came from.
- A stale/unresolved anchor must be surfaced as unresolved; never silently move a highlight to a different passage.
- Start with bounded TXT/Markdown stability. Use real documents only under the Q8 corpus gate. Do not claim PDF/EPUB or OCR/scanned-document anchor stability from synthetic text fixtures.
- Add re-extraction, source revision, deleted/replaced document, whitespace/layout change, duplicated passage, empty passage and ambiguous match cases.

### 6.7 P3-04 — Highlight and immutable revisions

Implement capture with source ID, source version, anchor/location, selected text or permitted excerpt, actor/owner, creation time and provenance. Define the immutable revision/event behavior before edits; if a highlight can be edited, represent revision history explicitly rather than mutating historical evidence in place. Verify capture does not depend on keyword/semantic enrichment being available.

### 6.8 P3-05 — Bookmark and saved location

Persist bookmarks through the same command kernel. Define what a bookmark points to (source/version/location) and what happens when the source version changes or the anchor no longer resolves. Do not encode a UI-only scroll coordinate as a permanent cross-format anchor without a contract. Test open/resume behavior and stale-source states.

### 6.9 P3-06 — Note and revision history

Persist Notes with provenance, stable identity and revision history. Support source-attached notes and source-optional personal writing where called for by the product model. Preserve arbitrary-length raw thought; do not force every jot into a tiny summary. Defer diagram persistence until the serialized schema and round-trip contract are defined. Test edit history, conflicting revisions, restore, tombstone and purge behavior.

### 6.10 P3-07 — rebuildable keyword index

Build a keyword-search path from authoritative records. The index is derived and disposable. Test full rebuild, incremental update, source deletion/purge, stale revisions, indexing failure and startup recovery. A failed index update must not invalidate committed capture; a stable-ID lookup must still retrieve the saved record even if the index is down.

### 6.11 P3-08 — local outbox, cloud sync and recovery contract

Define the local mutation/outbox atomicity contract and server acknowledgment contract before claiming offline durability. Model queued, sent, acknowledged, conflicted, retryable, terminal-failure and tombstoned/purged states as applicable. Test duplicate delivery, uncertain acknowledgment, restart, offline period, out-of-order update, concurrent edits, stale revision, retry exhaustion and account/owner mismatch.

Do not silently use last-write-wins for authored notes or source positions without an approved, visible revision/conflict policy. Keep local and server durability states distinct in API and UI. The sync mechanism must preserve command identity and provenance. A client-selected owner field is never the tenant authorization mechanism. If Supabase is part of the current target, independently verify authenticated identity and RLS through the actual authenticated connection/context, not only through a privileged test connection that sets an owner value.

### 6.12 P3-09 — export/restore, purge and integrated proof

Define a versioned export envelope with authoritative content, IDs, revisions, provenance, source/blob references, relationships needed for correct restoration and explicit schema compatibility. Prove restoration into an empty/disposable target and compare content/identity/revision/reference equality, not merely row counts.

Test purge/retention semantics and ensure purge cannot be undone by an older outbox event, a stale search index, a semantic derivative or a restore path that is supposed to honor deletion. If blobs live outside PostgreSQL, exercise staging, orphan cleanup, missing/corrupt blob detection and restore ordering. Do not state that database and blob storage commit atomically.

### 6.13 Phase 3 exit gate

Phase 3 is complete only when a real client/API/backend path can:

- import supported text/Markdown input and persist Work/Source identity;
- create a version-aware Highlight, Bookmark and Note through the command kernel;
- retrieve authored data by stable ID and via rebuildable keyword retrieval;
- survive tested crash/restart/replay/uncertain acknowledgment without lost committed writes or duplicate logical effects;
- demonstrate owner isolation and authentication behavior with at least two owners;
- preserve revision history and correct tombstone/purge semantics;
- distinguish local and server durability and handle documented conflict/retry states;
- export and restore authoritative content/revisions/references, with derived indexes rebuildable;
- pass the real migration, security, regression and trusted verification gates;
- trace every `SYS-01..SYS-11` requirement to an accepted test/evidence item and stated limitation;
- pass a clean-clone, user-like task that is graded independently of the implementing agent.

Do not pull broad PDF/EPUB support, semantic retrieval or graph autonomy into Phase 3 merely to make the scope look larger. The phase's proof is durable capture and recovery, not feature count.

---

## 7. Phase 4 foundation: establish integration contracts before expanding workflows

Once Phase 3 is accepted, start Phase 4 immediately. Keep Phase 4's outcome map in the plan, but expand detailed task cards only as their upstream evidence makes them executable. Phase 4 crosses the backend repo and the actual reader/journal client repo; the repos remain separate, and integration must cross the approved authenticated API rather than bypassing it.

### 7.1 P4-00 — foundation and integration contract

Before broad UI implementation, freeze the minimal contracts for:

- authenticated client identity and scoped authorization;
- import/open/read-position/capture/bookmark/note/journal operations;
- saved/queued/synced/conflicted/failed durability state and truthful user-visible acknowledgment;
- stable IDs and `@`-reference resolution across rename, revision, tombstone and purge;
- pagination, bounded response sizes, explicit errors, retry/idempotency and offline behavior;
- local cache versus server-authoritative data and cache invalidation;
- format capability/support matrix, extraction readiness and unresolved anchor states;
- client/API version compatibility, migration and rollback behavior;
- user task scenarios and evidence/acceptance tests.

Create a real contract test that calls the API boundary. Do not allow the UI to write product tables directly or use a service/privileged database key to bypass owner-scoped API behavior. If the design prototype uses mocks, keep mocks for local design iteration, but add a path that runs the actual backend contract before any feature can be called integrated.

### 7.2 P4-A — format intake and reading position

Expand format support incrementally under an explicit capability matrix. Distinguish native text PDF from OCR/scanned PDF, and reflowable EPUB from fixed-layout content. Malformed, encrypted, unsupported and over-budget documents must produce explicit states and error details safe for the user; staged source bytes must not vanish on parser failure.

Implement source opening and position persistence. State how positions and anchors relate to source versions and how they resolve after re-import/re-extraction. Use real documents only when the Q8 corpus gate and the relevant storage boundary allow it. Record a format as supported only after its acceptance corpus, position/anchor tests, failure cases and recovery evidence pass. Do not claim generic “PDF supported” when only one narrow text PDF case works.

### 7.3 P4-B — integrate the actual reader and capture interactions

In the authorized client repo, implement/import/open/read/position/highlight/bookmark/margin-note flows through the API contract. Preserve the product's visual direction; do not replace the prototype with a generic SaaS dashboard. The engineering requirements are that real UI state corresponds to real persisted state, and failure/retry behavior is honest.

Test authentication expiration, forbidden source, malformed DTO, offline transitions, timeout with uncertain acknowledgment, duplicate click, reload/restart, stale source version, deleted target, retry after success-but-lost-response and return-to-location behavior. The UI must distinguish “saved locally,” “sync pending,” “synced,” “conflict” and “failed” where those states exist. Do not show a success toast simply because a network request started.

### 7.4 P4-C — library, reading lists, resumability and journal writing lab

Implement stable reading-list identity and membership, current-reading state and position/resume semantics. Apply the approved reading-session/coarse-position/dwell rules from the plan's D-010; do not infer more precise attention or behavior than the system actually observes.

Build the journal/writing lab with source-optional blocks for raw thought and creative writing. Long thought dumps must remain durable and searchable without being forced into short-note templates. Separate source-attached notes from free-standing journal blocks while allowing intentional references between them. Preserve revisions and safe autosave/offline behavior; diagrams remain gated until serialization and round-trip behavior are explicitly defined.

Q6 transcript-block decisions should constrain only the specific Part-2 acceptance scenario/S5 corpus they govern, not unrelated journal or source capture. Keep the scope narrow and continue unblocked work.

### 7.5 P4-D — stable `@` references

Implement stable reference targets independent of display titles. Distinguish current revision, historical revision, tombstoned, unavailable, ambiguous and purged states. References must survive renames and should not silently retarget to a similarly named object. Authorization must be checked during resolution so reference previews do not leak hidden content or reveal the existence of another owner's private entity.

Test forward references, rename, alias change, merge/split only if a later approved operation exists, deletion, purge, historical links, missing access, duplicate title, and import of content containing hostile or misleading `@` strings. Raw imported content is untrusted; text that looks like a command or reference must not gain authority by being read.

### 7.6 P4-E — baseline scoped agent access

Phase 4's first usable milestone includes a minimal scoped agent read path; do not defer all agent access to Phase 5. It should read the owner's own selected journal/capture context using the same authorization/API core as the client, with explicit scope, provenance, bounded payload and query budgets, clear exclusions and traceable access behavior. Keep MCP or another transport as a thin adapter to the same core, not a second access-control path.

Start read-only. Derive identity from authenticated context, enforce owner scope on every query, limit page size and context budget, retain source/revision/anchor provenance, treat imported text as untrusted data and refuse cross-owner lookup even when the agent guesses an ID. Do not grant arbitrary database access.

Q9 (visibility of raw personal context) and Q10 (workflow token/owner scope) must be handled honestly. Implement conservative technical defaults and test them where they are already approved, but do not claim complete privacy/authorization guarantees while a required owner decision or repository-host permission remains open. Record the narrow remaining choice and complete all work that does not depend on it.

### 7.7 P4-F — integrated regression, recovery and exit

Run the client through the actual API and persistence stack. Validate migrations/backward compatibility, export/restore for journal blocks and references, owner isolation, source/capture/revision semantics, offline and sync conflict, reference resolution, index rebuild and purge. Add independent checks of stored state, not just screenshots or UI success states.

A design review can confirm visual intent, but it cannot substitute for end-to-end functionality. A backend test cannot alone confirm that the actual reader/journal experience works. Both are required.

### 7.8 Phase 4 exit gate

Phase 4 is complete only when an owner can perform the day-one workflow through the actual client and real backend:

**import -> open/read -> save position -> highlight/bookmark -> write or revise a note -> capture free-standing journal thought -> use stable `@` references -> leave/reopen and recover the same material with truthful durability state.**

The following must also be true:

- actual authenticated owner-scoped API access; no client-side privileged-table shortcut;
- stable identity and revision/provenance are preserved through read/capture/journal/reference flows;
- online, offline/retry, uncertain-acknowledgment and stale-source states are explicit and tested;
- unsupported or failed format handling cannot silently lose staged source bytes or mislabel extraction as ready;
- exports/restores preserve authoritative content and references; purge invalidates applicable derived state;
- scoped agent read works through the same access-control core where required by P4-E;
- owner isolation and hostile-import cases fail closed;
- actual UI workflow tests, API integration tests, backend/system tests, independent grading and owner-fidelity review pass;
- requirements traceability and limitations are current;
- no unresolved blocking defect is mislabeled as a pass.

If a genuinely required owner decision prevents a sub-gate, finish all independent gates and present the exact remaining decision and why it blocks the exit. Never pretend Phase 4 is complete merely to satisfy a deadline or because seven review passes elapsed.

---

## 8. Seven mandatory refinement rounds after the Phase 4 workflow exists

These are seven distinct review-and-repair rounds, not seven cosmetic passes and not permission to stop with known failures. Begin them once the Phase 4 path is end-to-end enough to exercise. Each round must inspect the implementation, attempt to break it, add/fix tests where needed, repair defects, rerun affected and full suites, review the diff, update evidence and record what changed. Use an independent reviewer or independent test path whenever possible; the implementing agent's own explanation is not independent verification.

### Round 1 — Requirements and contract traceability

Re-walk every SYS requirement and Phase 3/4 acceptance criterion from user-visible task to API, command, transaction, schema, persisted state, failure behavior and test evidence. Find missing links, untested “must” statements, duplicate sources of truth and requirements satisfied only by a mock. Fix implementation or tests; update the traceability matrix. Any requirement with no executable oracle remains open.

### Round 2 — Trust boundaries, authorization and hostile inputs

Attack the gate, migration paths, import/parser paths, API identity, owner scoping, reference resolution, agent retrieval, fixture copying and error diagnostics. Include two-owner adversarial tests, guessed IDs, branch/path trickery, untrusted imported instructions, oversized inputs, malformed structured requests and unauthorized revision/reference probes. Confirm forbidden requests fail without leaking other-owner existence/content. Fix every reproducible defect. Recheck repository-host protections and state the boundary honestly.

### Round 3 — Domain identity, provenance, revisions and anchors

Challenge Work versus Source identity, duplicate imports, stable IDs, source revisions, extraction generations, Highlight anchors, Bookmark locations, Note revisions and historical `@` references. Try renamed/replaced files, identical bytes under separate acquisitions, changed whitespace/layout, ambiguous repeated passages, edited and purged records, stale anchors and conflicting revisions. Prove no accidental logical merging and no silent anchor drift. Correct data contracts and regressions, not just UI labels.

### Round 4 — Transactions, replay, concurrency and failure injection

Inject a crash before commit, after commit but before acknowledgment, on retry, during concurrent same-key commands, during conflicting same-key commands, during sync replay and while a client is offline. Restart the process/database as supported by the environment. Compare independent authoritative state before and after. Prove exactly-once logical effects where the command contract promises idempotency and explicit conflict behavior where concurrent edits cannot be merged safely. Do not overstate resilience beyond faults actually simulated.

### Round 5 — Client/API integration and truthful UX states

Exercise the real reader and journal UI against real API contracts: import, open, position, highlight, bookmark, note, journal capture, reference navigation, restart and return to prior state. Test slow responses, timeouts, canceled requests, lost response after server commit, offline queue, auth expiration, server validation errors, conflict and recovery. The client must never equate “request started” with “saved”; it must not silently drop unsynced data or write through a privileged shortcut. Review layout/interaction against the established design, but do not substitute a redesign for backend correctness.

### Round 6 — Recovery, migrations, purge, rebuild and resource envelopes

Run migration history tampering tests, observation-only verification tests, schema compatibility, export/restore into a clean target, restoration of references/revisions, blob-staging/orphan states, purge invalidation, search/index rebuild, sync recovery and bounded request/parser behavior. Set and measure reasonable payload, file, memory/time and pagination limits supported by the deployment; test over-budget inputs. Compare restored authoritative content and references—not only counts. Fix the real recovery or resource issue, then run upgrade and clean-install paths.

### Round 7 — Independent clean-room grade and owner-task fidelity

Have a fresh checkout/independent agent follow the repository's concise instructions without access to the implementing agent's assumptions. It should run the verification path, set up the required datastore, start the real stack, and complete the canonical owner task with an independent grader inspecting stored state and provenance. It should attempt known-bad mutations and verify they fail for the intended reason. It should report setup friction, missing env contracts, misleading docs, false green routes and unexplained manual steps. Resolve the findings; update concise entry instructions and current status. An independent pass is not a rubber stamp: disagreement or inability to reproduce a claim reopens it.

### Round protocol and continuation rule

At the start of each round, record the exact revision under test and the round's hypotheses. For every finding: reproduce it; add a minimal regression; implement the smallest safe repair; test neighboring cases; rerun the relevant suites and `make verify`/canonical gate; inspect the diff; validate the claim through the actual caller; and record evidence/limitations. If a round discovers a defect that crosses a previously passed gate, reopen that gate.

After Round 7, **continue with additional focused rounds until Phase 4's exit gate is actually green**. Seven rounds are the minimum refinement commitment, not a fixed cap. Do not stop because the list is exhausted, the assistant has produced a long report, the UI looks complete, the CI has one green run, or the implementation agent believes it is finished.

---

## 9. Execution order and dependency rules

Use this order, keeping safe work moving in parallel only when file ownership and dependencies are disjoint:

1. Re-establish live HEAD, run baseline and reconcile stale claim table state.
2. H-01b trusted candidate-tool execution floor, including bounded fixture handling and truthful CI trust boundary.
3. H-01c-claims, H-01c-authority and H-01c-evidence/privacy; independently reproduce and route F-001 through F-013.
4. H-02 typed proof-sheet schema and actual-gate verification. Do not activate a new evidence gate before the H-01b trusted floor is accepted.
5. P3-00 requirements/contract/interface freeze.
6. P3-M0 migration oracle and P3-K0 command kernel primitives; parallelize only where the contracts and files truly do not overlap.
7. P3-01 first real product command plus TXT/Markdown capture/replay/retrieve checkpoint.
8. P3-02 through P3-09, in dependency order, with early real product demonstrations after each meaningful vertical slice.
9. Phase 3 exit gate. Do not silently skip export/restore, owner isolation or crash/replay proof.
10. P4-00 integration contract and foundation; inspect and use the authorized client repository for actual client workflows.
11. P4-A through P4-F with real integration tests and visible blocked decisions at their exact boundaries.
12. Run refinement Rounds 1-7. Continue beyond Round 7 if a blocker or regression remains.
13. Produce the final evidence-backed completion report only after actual Phase 4 exit criteria pass or explicitly identify any owner-gated remaining blocker without calling it complete.

Do not run unrelated work in parallel if it can affect the same core contract, migration sequence, claim register, runner or verification artifacts. Do not merge a phase's work just because its code was written; merge/close only after required checks and review succeed under the existing repository workflow.

---

## 10. Required evidence and reporting format for every slice

For each bounded card, maintain a compact record with:

- **Card and requirement:** canonical ID, relevant SYS/Phase 3/4 criterion and dependency.
- **Before state:** revision SHA, relevant files, baseline test and exact failing behavior.
- **Red evidence:** the test/fixture that fails before the fix and what result was expected.
- **Change:** concise description of code/contracts changed and why the boundary is correct.
- **Validation:** exact command, environment/database version, outcome, expected case count, full output/artifact digest when the repository protocol requires it, and independent oracle used.
- **Adversarial neighbors:** counterexamples attempted and their outcomes.
- **Claim limits:** what was not tested, what remains a synthetic test, which fault envelope was actually exercised, whether CI/host settings were observed, and any residual limitations.
- **Status:** open, implemented-not-verified, local-verified, CI-verified, independent-verified, blocked on owner decision, or closed under the canonical protocol.

At the end of the whole execution, report:

1. The final backend and client revisions/PRs and whether any worktree changes remain uncommitted.
2. A current capability map: implemented and verified versus planned or blocked.
3. A finding matrix for all six engineering-review defects and all 13 CodeRabbit findings, with current reproduction/disposition and evidence—not merely “fixed.”
4. The Phase 3 traceability and exit-gate results.
5. The Phase 4 traceability and exit-gate results.
6. Results of all seven refinement rounds and any extra rounds.
7. Commands/tests run, environments, independent checks and exact residual failures.
8. External repository-host settings or owner decisions that the agent could not make.
9. A short list of remaining work only if it genuinely remains; do not bury blockers in a general “future improvements” section.

### Completion bar

The objective is not a longer plan or a larger test-count number. The objective is a trustworthy verification path and a real owner workflow whose captured material survives uncertainty, retains source/revision/provenance, can be found and recovered, respects authorization, and has evidence that an independent reviewer can reproduce. Keep the architecture, reduce unnecessary process, fix the known faults, and move from harness confidence to demonstrable product behavior.

---

(End of owner turn 22 verbatim — the directive body above is a byte-faithful embed of the received file `Pasted Content_1792480917297.txt` (66,094 bytes, SHA-256 recorded in §2); no transcription was performed by the recording agent for the directive body, unlike records 20/21 whose turns were transcribed through session context — the standing byte-level-diff limit is therefore NOT applicable to §1 this time; the only redaction is the turn's leading access credential, noted above. The two review attachments are preserved at their `context/reviews/` homes; their bodies are also file-native embeds.)

## §2 — the observed starting state (session-22 preflight, 2026-10-20)

All observations fresh this session, at the live HEAD, before any source change (the directive §3's startup procedure):

**Live truth re-established (the directive §3.1):**
- `main` = `fbd1c13c2417de46334533f6214789011cd39983` — local == origin after `git fetch --prune`; the supplied review's observed baseline is STILL the live HEAD (no drift since session 21's close); 0 open PRs; working tree clean.
- Branch protection re-observed live via the API (fresh PAT, full scopes, `prathamarchives`): required checks `[canonical-layer, head-tools, harness]`, strict contexts, admins included, no force-push/deletions. Latest post-merge run `39273338657` success at `fbd1c13`.
- The client repository observed independently (the directive §3.1's second sentence): `prathamarchives/arivodesign` — public, default branch `main`, last push 2026-10-19T10:22:58Z (`ec99aab`, "INT-027 / pass 18" — WAAPI view-transition design work). Separate transaction/branch/release state; no shared assumptions; no integration work this session (Phase 4's P4-B/P4-C own that, per the directive §7).

**The local rig and the baseline (the directive §3.3/§3.4):**
- The environment reset between sessions destroyed the prior cluster's data directory (missing `pg_notify` — the same reset-survival prediction record 18 §9 made). Rig REBUILT user-space from the exact FACT-001 Debian `17.11-0+deb13u1` packages (port 5433, fresh `initdb`, trust auth): `make migrate` applied 3 migrations; `make verify-schema` OK, checksums match; `make harness-health` ARV-RIG-001 green.
- The seven P2-CLOSE commands, all GREEN at `fbd1c13`, this environment, this session: `python3 tools/verify_canonical_layer.py` 51/0 exit 0 · `python3 tools/verify_selftest.py` 30/30 · `python3 tools/isolation_check.py` GREEN · `python3 tools/isolation_selftest.py` green (redaction path tested) · `make verify` GREEN (all four declared suites + 13/13 known-bads + gate selfcheck + canonical 51/0). Fresh `python3 harness/claims.py` green (registry checks pass at the predecessor — the drift items below are checker-coverage gaps, not checker failures; see the F-CLM note).
- The CI path traced end to end (the directive §3.4): `verify.yml` pull_request → the three jobs → the harness job's event-env dispatch (H-01a's fail-closed surface) → the canonical-layer job's four base-anchored judges → head-tools' candidate-tool runs. The trace confirmed the scanner's three workflow findings statically (F-003/F-004/F-005 — see the triage table); the mutation floor's in-process import defect (A03) is visible at `tools/verify_selftest.py:30` (`from verify_canonical_layer import INT_HEADER, REPO, Layer`) — reproduced in BOTH forms at record 21 §4, the H-01b card's RED evidence.

**Registry/ledger drift — CONFIRMED, reconciled in this slice (the directive §1.2/§3.5):**
1. **CLAIM-010 is still OPEN in the registry** although its PR #45 merged (main = `fbd1c13`, post-merge run `39273338657` success) — record 21 §12's own prediction, exactly as claimed. Repaired: the rule-4 late closed row (the CLAIM-006/CLAIM-003 precedent; a claim cannot append its own closed row inside its own PR).
2. **CLAIM-007 appears in BOTH the open and the closed tables** — the engineering review's observation, confirmed live. The closed row (PR #42 = `e78ac8b`, full evidence) is correct and complete; the OPEN row is a stale leftover that PR #43's close step should have migrated but did not. A real coverage finding: the gate's ARV-CLM checks are **diff-scoped** (they validate the rows a slice touches), not **registry-wide** — no check fires for a claim ID present in both tables when no slice touches its rows, which is how this duplication survived PRs #43/#44/#45 and the 51-check verifier. Repaired: the stale open row removed (the closed row was already the complete record); the coverage gap routed to the H-01c-claims card as a required case (duplicate claim ID in both tables must refuse with a named ARV-CLM code, registry-wide, not diff-scoped).
3. **NEW preflight discovery (not in either review): the INT-126 one-liner row is TRIPLECTED in the ledger.** Three byte-identical `- **INT-126** — ...` rows sit at the one-liner section (introduced in ONE diff hunk at `b572d3f` = PR #43's intake commit; the commit message and the audit note both claim "contiguous and unique", which is true only of the DETAILED blocks). Root cause, verified in source: C2/VER-201's `INT_HEADER` pattern matches **detailed-block headers only** (`^\*\*INT-(\d{3})\s+—\s+...\*\*$`), so the one-liner summary section has NO uniqueness/consistency check — the triplication is invisible to the 51-check verifier and survived CI. Repaired: two exact-duplicate rows removed — a mechanical transcription repair, the INT-092 precedent class ("defect repair under the source-coverage control, not history rewriting": quotes and statuses untouched; the removed rows were byte-identical to the kept row), documented in the ledger's session-22 audit note. Coverage gap routed to H-01c-claims (one-liner-section uniqueness/consistency against the detailed view).

**The 13 scanner findings — triaged at the live HEAD (the directive §1.3/§1.5): every location and behavior verified by direct source read this session (static), reproduction scheduled in each finding's card; none dismissed by severity; none auto-closed:**

| Finding | Live-HEAD verification (this session, static) | Route (card) |
|---------|-----------------------------------------------|--------------|
| F-001 scope path parsing | confirmed: `scope.py:102` `--name-only` human-format; `:111` numstat quoted-name retention; `:195` raw `startswith` prefix matching (also the review's sibling-prefix defect, A11); rename endpoints absent | H-01c-claims (NUL-delimited records; both rename endpoints; one validated path list for scope/claims/size) |
| F-002 scanner read_text | confirmed: `isolation_check.py:285` `p.read_text()` unbounded, follows tracked symlinks | H-01b-F (bounded, mode-aware, race-resistant reads) |
| F-003 candidate-controlled workflow | confirmed: `verify.yml:37-39` pull_request selects the merge-revision definition (documented GitHub behavior, assumption A4) | H-01b-CI (repo-side: a base-anchored trusted-gate required job; host-level: workflow-definition protection is a GitHub settings item — recorded as the exact external requirement, never claimed fixed by a code-only change) |
| F-004 candidate Make recipes | confirmed: `verify.yml:84-85` `make harness-health`/`make harness-tests` from the candidate tree; the gate skips its own suites on recipe success | H-01b-CI (the trusted driver selects and validates required suites itself) |
| F-005 import shadowing | confirmed: `verify.yml:114/124-125` trusted judges copied INTO `head/tools` and launched from there — script-dir import precedence exposes them to candidate `shutil.py` | H-01b (the floor driver: `python3 -I` isolated launch, stdlib-only, no sibling imports; the candidate tree passed as data) + H-01b-CI (anchored-judge launch hardening) |
| F-006 candidate registry at gate import | confirmed: `gate.py:54-56` `_kb_spec.loader.exec_module(kbcases)` executes the candidate's `known-bad/cases.py` top-level code inside the gate interpreter before any check; a `SystemExit(0)` there is forwarded by `dispatch.py:63` as the job result | H-01b-CI (the base-anchored gate re-run is the backstop; the candidate gate's own green is never the only evidence for the harness check) |
| F-007 RED hash self-authorization | confirmed: `gate.py:107-111` compares the test file hash against the CANDIDATE-SUPPLIED `current_sha256` in `red-records.json` (refreshable by the contributor via `make red`) — the frozen `red_sha256` is not the compared authority | H-01c-evidence (typed observed-red records, revision binding, protected-baseline comparison, approved-amendment semantics) |
| F-008 branch-name claim suppression | confirmed: `gate.py:199` — `slice_name not in ("main-selfcheck",)` gates the claim checks; a PR branch named exactly `main-selfcheck` (or `slice/main-selfcheck`) suppresses open-claim and coverage enforcement despite PR diff mode | H-01c-claims (claims enforced by TRUSTED invocation mode, never by branch/slice labels; reserved selfcheck names rejected at dispatch; RED case for both spellings) |
| F-009 destructive-SQL text matching | confirmed: `migrate.py:97` `DESTRUCTIVE_RE` over raw text — comments between keywords evade; fail-open for unclassifiable syntax | P3-M0 (admitted-language contract, fail-closed classification) |
| F-010 migration-name SQL interpolation | confirmed: `migrate.py:106` `'{name}'` interpolated into the ledger INSERT from a filename-derived value | P3-M0 (safe alphabet + parameter binding) |
| F-011 isolation selftest copytree | confirmed: `isolation_selftest.py:59` `shutil.copytree(REPO, fix, ...)` default symlink-dereference, no budgets | H-01b-F |
| F-012 fixture-failure filename leak | confirmed: `isolation_selftest.py:172-175` `_fixture()` runs BEFORE the sanitized `try:`; the standalone `:219` entry has no exception boundary — copytree errors with filenames reach the default traceback | H-01b-F (construction inside the sanitized boundary; fixed diagnostics + exception class only; synthetic secret-shaped-path regression) |
| F-013 mutation-suite copytree | confirmed: `verify_selftest.py:509` `shutil.copytree(repo, copy, ignore=...)` — unbounded, follows candidate symlinks | H-01b (the floor's own fixture builder: reject non-regular entries, per-file/total budgets, cleanup-before-construction, sanitized failures) |

**The review's six concrete defects (§1.4) — all already in the defect register (the reviewer's own statement, honored):** (1) verifier early-exit = A03, REPRODUCED both forms (record 21 §4), H-01b's RED; (2) command `|`-concatenation ambiguity = A04, P3-K0; (3) migration false-rollback = A05, P3-M0; (4) verify accepts missing applied history = A06, P3-M0; (5) proof-sheet 16-char digest prefix = A09, H-02; (6) sibling-prefix path matching = A11 (with F-001), H-01c-claims. No new defect IDs minted; the review's independent reproductions are recorded as confirming evidence, never as closures.

**Environment provisioning (the turn's "setup" clause):** gh CLI v2.102.0 installed user-space, authenticated as `prathamarchives` (fresh PAT, full scopes; stored OUTSIDE the repo at the workspace credential store — never in a repo file, D-025); the Postgres rig rebuilt (above). Supabase: the CLI is installed for readiness, but **no Supabase project, schema, or provider decision is made** — Q12 (blob backend/staging/recovery) remains the owner gate; "setup" provisions tooling only, never ratifies a provider. The local Supabase stack additionally requires a container runtime absent from this sandbox — recorded as an environment fact, not a blocker (no Q12-dependent work is scheduled this session).

**Provenance digests (the §1 embeds):** directive file (`Pasted Content_1792480917297.txt`, 66,094 bytes) SHA-256 `3cf2156fa7dd48f038d7cf8af043503ab114f917550820f92c3d41e6523b36a6`; review file (`arivoo-repository-review.md`) SHA-256 `f86ab326cccd7a4ebe62ec3b9e6225ba655d804602627bd77e24c08484c37d52`. Both embeds are file-native (no agent transcription). The CodeRabbit PDF's text arrived gateway-extracted (embedded in the turn, not as a standalone file) — its `context/reviews/` preservation is a faithful structured transcription of the received extraction, with the PDF's export pointers omitted and that omission noted in the file itself.

## §3 — the intake scope (what this slice is and is not)

**This slice (CLAIM-011, the session-22 intake + reconciliation):**
- The two review artifacts preserved at `context/reviews/` (D-022 banners; review-only, never authority).
- Record 22 §1 (the turn verbatim, credential redacted) + §2 (the observed state above) + §3 (this scope). §4–§12 land at the session's close slice.
- INT-127 reserved and ledgered (one-liner + detailed block + the session-22 audit note carrying the three reconciliation items and the coverage findings).
- D-041 (the operational adoption of turn 22): severable, challengeable — the baseline procedure; the 14 non-negotiable rules as session-operating constraints; the F-001..F-013 triage/routing; the execution order (§9); the per-slice evidence form (§10); the Phase 4 exit gate (§7.8) and the seven-rounds protocol (§8) as outcome-row annotations; the truthful-status vocabulary (§2 rule 11); "setup supabase" = tooling only, Q12 untouched.
- PLAN refresh: the H-01b card extended with the directive §4 fixture/trust requirements (F-005/F-006/F-013 routing); NEW sub-cards recorded under the H-01b contract — **H-01b-F** (bounded fixture/read hygiene: F-002/F-011/F-012 in `isolation_check.py`/`isolation_selftest.py`) and **H-01b-CI** (the trusted-CI driver: F-003/F-004 + the anchored-judge launch hardening of F-005 + the F-006 gate re-run backstop; the host-level GitHub settings requirement recorded as external, never claimed fixed in-repo); H-01c-claims extended (F-001/F-008 + the registry-wide duplicate-ID case + the ledger one-liner uniqueness gap); H-01c-evidence extended (F-007 cross-ref); P3-M0 extended (F-009/F-010 cross-refs); the P4 outcome rows refreshed to the directive §7's P4-00 + P4-A..P4-F sequence; the §8 rounds protocol added as the post-Phase-4 refinement commitment (minimum seven rounds, continue-until-green).
- The three reconciliations: CLAIM-010's late closed row; CLAIM-007's stale open row removed; the INT-126 one-liner dedup + audit note.
- STATE re-derived; AGENTS phase/count sync (109 statused); WORKLOG Task 28; the slice's runs/scope/proof-sheet.

**Non-goals (honored):** no code changes this slice (H-01b is the next claim — the directive §3's "do not wait for a perfect inventory before fixing H-01b" is answered by the card being READY and claimed next, not by widening this intake); no owner question opened or closed (Q6–Q12 + D-014 scopes unchanged; the directive adds gates to EXISTING cards, never new authority); no roadmap rewrite (the NG-04 outcome-row exception continues under D-039; turn 22's §7/§8 rows extend it); no history rewriting (all three reconciliations are append/migrate/dedup with evidence, the canonical methods); the credential never enters any repo file.

## §4 — the disposition ledger (slices as they land)

| Item | Disposition | Evidence |
|------|-------------|----------|
| CLAIM-011 (the intake + the three reconciliations) | LANDED | PR #46 = `e1ef3a0`, CI `39390452755` three-check green, post-merge `39390799806` success |
| H-01b part 1 (CLAIM-012: the runner module) | LANDED | PR #47 = `0dc6aaf`, CI `39398823620` three-check green; the card's named mutation_runner.py; the KB-CLM-002 probe made self-contained |
| H-01b part 2 (CLAIM-013: the activation) | THIS SLICE | The 16-case suite 16/16 GREEN (7.6s); make verify GREEN (13/13 + suites + canonical 51/0); the --self-test delegation 30/30 through the child-process floor; the run_floor orchestration completed (part 1 landed it inert — its absence was invisible to part 1's CI by construction, caught by this slice's first suite run) |
| A03 (the verifier early-exit + write-after-checksum) | FIXED with stable regressions | test_01/test_05: the early-exit candidate refused (ARV-FLOOR-001); the mid-run source mutation detected (ARV-FLOOR-002); RED observed at the predecessor (red-01/red-02: 15/16) |
| F-005 (import shadowing) | REPAIRED at this boundary | The driver: stdlib-only, launched `python3 -I` in CI, the runner loaded BY PATH; test_10's anchored shadow probe never fires |
| F-013 (the suite's copytree) | REPAIRED | The bounded no-dereference builder (lstat + O_NOFOLLOW; budgets; the .pg skip); tests 07/08/09/16 |
| F-002/F-011/F-012 (the isolation tools' fixture class) | NOT this slice — H-01b-F owns them | Routed in the PLAN refresh; no triage-only closure |
| F-003/F-004/F-006 (the CI trust chain) | NOT this slice — H-01b-CI owns them | Routed; the host-level GitHub settings requirement recorded EXTERNAL |
| The INT-126 one-liner triplication + both ARV-CLM coverage gaps | REPAIRED (CLAIM-011) + ROUTED (H-01c-claims) | record 22 §2/§3; the registry-wide duplicate case + the one-liner consistency case added to the card |

## §8 — the honest failure log (every catch, this session)

1. **ARV-CLM-003** (the intake slice): the missing retroactive notation on INT-127's same-PR reservation — caught live by the registry check, repaired in the claim row.
2. **ARV-PROT-002** (the intake slice, from CI): DECISIONS.md protected, the scope declaration carried no owner ref — AND the local gate had passed because it ran at the MID-SLICE HEAD (part 1 committed only): the base...HEAD diff judged an incomplete set. Standing lesson restated in notverified: the local gate is evidence only at the FULLY-COMMITTED candidate HEAD.
3. **The ARV-SIZE-002 split** (H-01b): the single-PR floor was refused at 537 source lines (LAW-05) — repaired by the card's own named module: part 1 the runner, part 2 the activation, each bounded.
4. **The KB-CLM-002 probe coupling** (part 1): the matrix caught its own probe still depending on a LIVE claim's scope — the A11 probe-coupling class, third occurrence — repaired with the synthetic partner row, the exit-2 run record preserved.
5. **ARV-CLM-002** (part 1, from CI): the claim ROW's scope cell lacked harness/known-bad/cases.py while the scope.txt had it — the registry's coverage check (not the scope check) refused; repaired; the local-PR-mode-gate lesson applied a third time.
6. **ARV-DEP-008** (the activation): the suite's in-process `import verify_selftest` correctly refused (harness/ imports stdlib+harness only) — repaired by STRENGTHENING the surface: the public `--validate-manifest` CLI mode, tested as a subprocess (amendment 5).
7. **The run_floor trim incident** (the activation): part 1's module landed WITHOUT run_floor — the pre-commit trim script cut from `def select_cases(` to EOF, and the inert module's missing orchestration was invisible to part 1's CI by construction; caught by this slice's first suite run (AttributeError), repaired by completing the orchestration here. Honest note: part 1's commit message overstated the module as "the runner + manifest contract" — the orchestration belongs to this slice, and §4 records it as such.
8. **The sandbox /tmp quirk** (the activation): driver-spawned children's fresh /tmp lookups were intermittently blind in this host's unittest context (never in plain subprocess chains, never on CI's shared-tmpfs runners) — test_05's delivery made deterministic via source-path.txt as corpus data; the DETECTION property under test is unchanged.
9. Five red-record amendments (LAW-11): three strengthenings + two fixture corrections — every one assertions-added/replaced-stronger, none removed, all recorded in the red records' amendment notes.
