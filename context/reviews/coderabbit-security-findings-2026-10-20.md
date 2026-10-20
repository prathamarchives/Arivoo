# CodeRabbit Security findings report — prathamarchives/Arivoo (owner-forwarded, 2026-10-20)

> STATUS: REVIEW-ONLY ARTIFACT — 2026-10-20 (banner per D-024/D-022). Owner-forwarded scanner report, preserved as received (PDF text extraction, gateway-delivered): NOT a canonical rule, NOT owner intent, NOT an implementation authorization beyond what DECISIONS D-041 records. Per the turn-22 directive §1.3, these 13 findings are LEADS to reproduce against the live HEAD — "not as independently confirmed truths and not as findings that can be dismissed by their nominal severity. Each must end with a recorded disposition and evidence." Routing to bounded cards is recorded in PLAN (H-01b / H-01c-claims / H-01c-evidence / P3-M0) per the directive §5.5. Generated Oct 20, 2026, 12:09 PM; scan state: Open; filters: State=Open.

## Executive summary

13 findings included. 13 open; 0 open critical or high findings to prioritize for review.

Open: 13 · Fixed: 0 · Dismissed: 0

Findings by severity: Critical 0 · High 0 · Medium 2 · Low 11

Counts cover the included findings and current filters, not the security posture of unscanned code.

## Issue summary

| ID | Issue / location | Severity | Status |
|----|------------------|----------|--------|
| F-001 | Authorization bypass — `harness/scope.py:195-198` | medium | Open |
| F-002 | Denial of service — `tools/isolation_check.py:285` | medium | Open |
| F-003 | Security misconfiguration — `.github/workflows/verify.yml:38-39` | low | Open |
| F-004 | Security misconfiguration — `.github/workflows/verify.yml:84-85` | low | Open |
| F-005 | Injection — `.github/workflows/verify.yml:124-125` | low | Open |
| F-006 | Authorization bypass — `harness/gate.py:56` | low | Open |
| F-007 | Other — `harness/gate.py:107-111` | low | Open |
| F-008 | Other — `harness/gate.py:199-206` | low | Open |
| F-009 | Other — `harness/migrate.py:97-99` | low | Open |
| F-010 | Injection — `harness/migrate.py:106` | low | Open |
| F-011 | Denial of service — `tools/isolation_selftest.py:59` | low | Open |
| F-012 | Sensitive data exposure — `tools/isolation_selftest.py:173` | low | Open |
| F-013 | Denial of service — `tools/verify_selftest.py:509` | low | Open |

## Finding details (as received)

### F-001 · Authorization bypass (medium, Open; CWE n/a; Finding ID 7101a3d3-8cf6-422c-8ee4-76db9672d297)

Location `harness/scope.py:195-198`. Reachability: External. Exploitability: Moderate. Detected Oct 19, 2026, 10:30 PM.

The gate evaluates protected-path authorization using human-formatted Git output rather than complete filesystem identities. Quoted names fail protected-prefix matching, and detected renames omit their source paths, allowing protected changes to escape the owner-reference requirement. The related numstat reader also misclassifies quoted filenames and undercounts bounded changes.

Evidence: PR-controlled filenames and rename operations in the diff against origin/main; protected-path authorization at scope.py:195, with incorrectly parsed paths also consumed by scope coverage, claim coverage, and size checks; the policy readers lack a machine-safe pathname format and a complete set of changed identities, including both endpoints of renames.

Recorded path: `.github/workflows/verify.yml:94` (dispatch runs against the pull-request checkout) → `harness/dispatch.py:59` (the gate receives --diff origin/main) → `harness/gate.py:187` (scope.diff_paths reads changed names) → `harness/scope.py:102` (quoted names remain quoted, rename source paths absent) → `harness/gate.py:195` (check_scope evaluates incorrect/incomplete identities) → `harness/scope.py:195` (a quoted .github pathname fails protected-prefix matching) → `harness/scope.py:111` (diff_stats retains quoted pathname representations) → `harness/scope.py:118` (a closing quote prevents Python/test/migration classification) → `harness/gate.py:196` (check_size receives the resulting undercount) → `harness/gate.py:204` (check_branch_claim receives the incomplete changed-path list).

Suggested fix: Use NUL-delimited Git output and parse pathname records without human-output quoting. Disable rename detection for policy evaluation or include both rename endpoints, and apply the corresponding parsing rules to numstat before classification.

### F-002 · Denial of service (medium, Open; CWE-400)

Location `tools/isolation_check.py:285`. Finding ID 7a4fc0e2-80e4-49ac-a570-638ae46dabb0. Exploitability: Moderate.

The scanner follows tracked symlinks and reads their entire targets before checking content. A tiny repository symlink can point to a nonterminating device stream, causing memory allocation unrelated to the submitted repository object's size and terminating the CI scanner.

Recorded path: `tools/isolation_check.py:357` (main invokes check) → `:258` (check enumerates tracked paths) → `:283` (check constructs the worktree path) → `:285` (read_text follows the symlink and reads until EOF — sink).

Suggested fix: Inspect tracked object modes and scan symlink text rather than following its target. If scanning worktree files, use a race-resistant open that rejects symlinks and nonregular targets, and enforce per-file and total byte budgets.

### F-003 · Security misconfiguration (low, Open)

Location `.github/workflows/verify.yml:38-39`. Finding ID ffe2c8ab-4630-4456-b0ec-e391b03cae1b. Exploitability: Difficult. Assumption A4 (GitHub Actions documented pull_request workflow-selection behavior).

The authoritative verification workflow runs from a revision influenced by the pull request. A contributor can preserve the required job identifiers while replacing their checks with successful commands, invalidating the integrity of those verification results.

Entry → sink: `.github/workflows/verify.yml:38` (pull_request starts the workflow) → `:50` (the selected definition supplies the three jobs) → `:110` (candidate-editable canonical judge steps determine the job result).

Suggested fix: Require verification through a workflow whose definition the candidate cannot change. Treat the candidate checkout as untrusted input, and isolate any candidate execution from trusted verification state and credentials.

### F-004 · Security misconfiguration (low, Open)

Location `.github/workflows/verify.yml:84-85`. Finding ID 7efd2fae-fa12-4179-9dc0-585536424234. Exploitability: Difficult. Assumption A4 (actions/checkout documented pull_request default).

The required real-stack checks are delegated to candidate-controlled Make recipes. The subsequent gate skips its own suites solely because those recipes returned success, so a contributor can obtain a passing harness result without running the required health and test commands.

Recorded path: `:38` (pull_request trigger) → `:74` (event-selected checkout) → `:84` (candidate Makefile recipes) → `:94` (candidate dispatcher) → `harness/dispatch.py:62` (candidate gate subprocess receives control).

Suggested fix: Run the mandatory health and suite commands through a protected driver rather than candidate Make recipes. Allow suite skipping only when that driver has independently verified completion and results.

### F-005 · Injection (low, Open; CWE-427)

Location `.github/workflows/verify.yml:124-125`. Finding ID 3980bd03-3d04-421b-9e64-bc6291d31d55. Exploitability: Difficult. Assumption A4 (script-directory import precedence in ordinary Python startup).

Trusted judge scripts are executed from a directory containing candidate-controlled Python modules. A candidate module can replace a standard-library import and exit successfully before the trusted judge performs verification, forging successful canonical and isolation check results.

Recorded path: `:38` → `:108` (candidate tree checked out under head) → `:114` (main judge copied into head/tools) → `:124` (copied judge launched from head) → `tools/verify_canonical_layer.py:52` (shutil import resolves from the script directory).

Suggested fix: Execute trusted judges from a protected directory with a controlled import path and pass the candidate tree explicitly as data. Run candidate tool implementations in separate constrained processes so their imports and exits cannot determine the trusted driver's completion.

### F-006 · Authorization bypass (low, Open; CWE-807)

Location `harness/gate.py:56`. Finding ID 7a37d1d1-de71-43ef-8aab-a4ad8e69176c. Exploitability: Difficult. Assumption A4.

The gate executes the candidate's known-bad registry inside its own interpreter before running any checks. That code can terminate the interpreter with success, which the dispatcher accepts as a completed verification result.

Recorded path: `.github/workflows/verify.yml:73` (check out candidate code) → `:94` (invoke the candidate dispatcher) → `harness/dispatch.py:62` (launch gate.py) → `harness/gate.py:56` (execute candidate registry code before main) → `harness/dispatch.py:63` (forward a premature successful exit as the job result).

Suggested fix: Keep the authoritative driver and required rejection cases in protected state. Execute candidate code in a separate constrained process and require independently validated, complete check results before reporting success.

### F-007 · Other (low, Open; CWE-345)

Location `harness/gate.py:107-111`. Finding ID e08b1403-710a-4ff3-a002-ed25cbcd7842. Exploitability: Difficult. Assumption A4.

The RED control trusts a current test hash supplied alongside the changed test. A contributor can remove assertions and refresh that hash without obtaining the verifier approval required for amendments, so the gate accepts self-authorized changes to frozen verification evidence.

Recorded path: `Makefile:36` (invoke red.py with the supplied note) → `harness/red.py:31` (hash current test contents) → `:34` (replace the accepted current hash) → `:38` (write the candidate red-record artifact) → `harness/gate.py:175` (invoke check_red_records during verification) → `:108` (accept equality with the self-issued hash).

Suggested fix: Compare test hashes and amendment records against a protected baseline. Accept changed frozen tests only when an independently authenticated verifier approval identifies the exact amendment; keep failure-evidence validation separate from a contributor's descriptive note.

### F-008 · Other (low, Open; CWE-807)

Location `harness/gate.py:199-206`. Finding ID 4392e84e-eed3-4fcb-aee2-e1a813a21bc1. Exploitability: Difficult. Assumption A4.

The gate uses an attacker-selected slice name to decide whether PR claim enforcement applies. Naming the branch main-selfcheck or slice/main-selfcheck suppresses the required open-claim and claim-coverage checks even though the dispatcher explicitly selected PR diff mode.

Recorded path: `.github/workflows/verify.yml:91` (github.head_ref becomes ARV_PR_HEAD) → `harness/dispatch.py:50` (main reads the attacker-selected branch name) → `:59` (main constructs the PR-mode gate command) → `:62` (subprocess.run invokes gate.py) → `harness/gate.py:187` (main computes the PR diff) → `:199` (the main-selfcheck exception skips claim enforcement) — plus the slice_name derivation path (dispatch.py:51 → :59 → :62 → gate.py:199 → :237 success).

Suggested fix: Enforce branch claims whenever PR diff mode is active, regardless of slice name. Reject reserved selfcheck identifiers during PR dispatch and select selfcheck behavior only from trusted event mode. Add a regression covering both main-selfcheck branch spellings.

### F-009 · Other (low, Open)

Location `harness/migrate.py:97-99`. Finding ID b8990927-589d-4489-bcc6-a260f2f6112a. Exploitability: Difficult.

The destructive-operation guard matches selected textual spellings instead of PostgreSQL tokens. A comment between DROP and TABLE bypasses the required baseline-bump directive, allowing an unmarked migration to delete a table that the migration role can drop.

Recorded path: `harness/migrate.py:139` (main calls run) → `:80` (run discovers migration files) → `:89` (run reads the new migration's contents) → `:97` (DESTRUCTIVE_RE fails to recognize comment-separated destructive keywords — security decision) → `:104` (run includes the accepted SQL in its transaction batch) → `:108` (run submits the batch to pg.psql) → `harness/adapters/pg.py:56` (psql executes the batch against PostgreSQL — database sink).

Suggested fix: Evaluate executable SQL with a PostgreSQL-aware parser before applying the directive policy. Require the directive for executable constructs that the checker cannot safely classify, including dynamic or procedural SQL.

### F-010 · Injection (low, Open; CWE-89)

Location `harness/migrate.py:106`. Finding ID 179397cc-72cb-4bc7-b097-a2ffa0749738. Exploitability: Difficult.

The runner inserts a filename-derived migration name into a quoted SQL literal without escaping it. A crafted filename can terminate the ledger value and append SQL that was never inspected by the migration-body safety check.

Recorded path: `harness/migrate.py:139` → `:80` (run calls discover) → `:55` (discover returns the unchecked filename-derived name) → `:106` (run interpolates that name into the ledger INSERT — sink construction) → `:108` → `harness/adapters/pg.py:51` (psql passes the batch to _run_psql) → `:56` (subprocess.run executes psql).

Suggested fix: Use parameter binding or a reliable PostgreSQL literal-quoting mechanism for ledger values. Also restrict migration names to a documented vocabulary such as letters, digits, underscores, and hyphens.

### F-011 · Denial of service (low, Open; CWE-400)

Location `tools/isolation_selftest.py:59`. Finding ID 013a04f5-bc7f-4605-8044-f3a2fd756d58. Exploitability: Difficult. Assumption A2 (attacker-controlled repository file input at the standalone self-test).

The fixture builder follows repository symlinks without checking the target type or limiting copied bytes. A tiny link to a nonterminating device stream can consequently consume the temporary filesystem's free space.

Recorded path: `tools/isolation_selftest.py:219` (standalone entrypoint invokes self_test) → `:173` (self_test invokes _fixture) → `:59` (copytree dereferences repository symlinks while copying — sink).

Suggested fix: Reject repository symlinks and nonregular entries before copying, and enforce a total byte budget during copying. Allocate and construct the fixture inside a cleanup scope that also runs when construction fails.

### F-012 · Sensitive data exposure (low, Open; CWE-209)

Location `tools/isolation_selftest.py:173`. Finding ID 86a622ff-e1f4-4d10-8444-7faf649ef05e. Exploitability: Difficult. Assumption A2.

Fixture-copy errors escape the self-test's sanitized exception handler and reach Python's default traceback output. Because those errors contain filenames, a protected credential embedded in a failing filename can be printed despite the harness's explicit redaction contract.

Recorded path: `:219` (standalone self_test without exception sanitization) → `:173` (fixture construction outside the protected region) → `:59` (copytree raises an exception containing the sensitive filename) → `:219` (the uncaught exception reaches default traceback output — sink).

Suggested fix: Move fixture construction inside the sanitized error boundary and report only a fixed message and exception type on failure. Establish cleanup before construction starts, and add a setup-failure regression case asserting that a synthetic secret-shaped filename is absent from both output streams.

### F-013 · Denial of service (low, Open; CWE-400)

Location `tools/verify_selftest.py:509`. Finding ID 010ca5b2-c9db-458d-96d3-060b37f66b69. Exploitability: Moderate.

The mutation suite follows candidate-repository symlinks while copying fixtures without a byte budget. A short committed link to a nonterminating device stream can make the trusted suite fill the CI runner's temporary filesystem.

Entry → sink: `.github/workflows/verify.yml:108` (candidate tree checked out) → `:127` (copied mutation suite launched) → `tools/verify_selftest.py:503` (suite iterates its mutations) → `:509` (copytree follows candidate symlink — sink).

Suggested fix: Reject symlinks and nonregular entries before constructing mutation fixtures, and enforce a total copied-byte budget. Keep the existing temporary-directory cleanup as protection for ordinary failures.

---

*Report format note: this file preserves the PDF report's content as received (its CSV/JSON/SARIF export pointers and per-page layout are omitted; finding IDs, severities, locations, evidence paths and suggested fixes are complete). Disposition ledger: record 22 §4 tracks each finding's reproduce/triage status against the live HEAD with evidence.*
