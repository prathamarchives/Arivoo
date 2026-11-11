# CLAIM-077 — SEV round 1 (the adversarial fresh-context verification)

- **Agent:** independent fresh-context SEV reviewer (Task SEV-077-R1; not the slice author)
- **Date:** 2026-11-11T15:02:06Z
- **Round:** 1
- **Base:** `898b9f2a`
- **Head:** `f7b6b58` (git ground truth at review time; the task brief named `79b5f43` as head, but `79b5f43` is the measured-set repair — the actual head is its child `f7b6b58`, the LAW-24 repair. All verification below ran at the actual head.)
- **Chain (base → head):** `898b9f2a` → `aad5a43` (commit A: docs/reconciliation only — 8 files, all .md + the run-dir scope.txt, zero code) → `048a1dd` (the RED: tests-only, `harness/tests/test_agent_access.py`, 407 lines) → `6d5e22e` (the binding: red-01.txt + the red-records.json mint + the gate.py TESTS registration, 3 files/34 insertions) → `76dbd74` (the pre-GREEN amendments: the four disclosed pin repairs, tests + red-records only) → `cf0fe44` (the GREEN: migration 0019 + commands.py +118 + query.py +163 + capability.py +27) → `79b5f43` (the measured-set repair: the argv-safe token first char + the AGT-01 strengthener) → `f7b6b58` (the LAW-24 repair: the mint moved to `adapters/ids.py::new_agent_token`, the `secrets` import removed from commands.py)
- **Method:** 56 live probes + 18 static/git checks. 45 numbered probes on my own scratch rig (`sev77r1_probe.py` → `sev77r1-log.txt`, both in `/home/z/my-project/scripts/`): 42 PASS + 3 OBSERVE + 0 FAIL. Plus: the AGT suite run once by me independently (GREEN AGT-01..08, exit 0), the RED reproduced from the archived tree `048a1ddb` via `git worktree` (exit 1, ARV-TEST-000), the REF-01..06 and LIB-01..06 family suites re-run as owner-read regression (both GREEN), the gate's own `scope.check_scope` + `claims.check_branch_claim` + `scope.lint_boundary` invoked live on the base→HEAD diff, a 3000-mint first-char distribution probe at the adapter, an underscore-leading argv-safety probe, and the 4-way sha256 amendment-chain verification of red-records.json. Zero writes inside the repo; all scratch DBs created and dropped by me.

## §1 Verdict

**PASS — zero open P0/P1.** Every claimed behavior in the slice's letter was reproduced live on my own rigs, including the adversarial extras I devised (whole-database token grep, hostile token strings, the write-surface closure on the mint command itself, the superuser un-revoke, the planted write-scoped lookup probe, the forced audit failure with the grant revoked mid-rig). One open **P2** (F-077-1: a scope-declaration drift — `harness/adapters/ids.py` changed at the LAW-24 repair but never added to `scope.txt` or the CLAIMS.md row's file-set cell; the gate's own ARV-SCOPE-002 and ARV-CLM-002 both fire live on the base→HEAD diff, so the slice as it stands cannot pass its own PR gate — fail-closed, a declaration repair never a behavior repair) and three **P3**s (F-077-2/3/4). No wrong answer was ever served, no isolation leaked, no secret persisted, no refusal was untyped where the slice claims typing.

## §2 The live verification

All outputs below are captured verbatim from my rig (`/home/z/my-project/scripts/sev77r1-log.txt`). Scratch DB `arv_sev77r1_<pid>_<ts>`, migrated 0001→0019, fixture: owner A (source + highlight + bookmark + note + journal block) and owner B (source + note).

### §2.1 The mint + the one-time display (claims 1)

- **P02 — the commit and the ONE token line.** `mint_agent_credential --label "research assistant"` → exit 0, and the ack carries exactly one `token=` line:
  `ACK command=mint_agent_credential idem_key=sv-mint1 status=committed result_ref=01a1cb1d-0f53-7d3e-b5dd-50eb9374fcce token=1KfAVtoyCrk2SzowMny-Z-Orshku-i2aT0wNR… durability_rung=local_durable api_version=1` — 1 token line counted.
- **P04 — the replay.** Same key + same body → `status=replayed result_ref=<same id> durability_rung=local_durable api_version=1` with **zero** `token=` lines (the spine's replay path re-prints the recorded ack, and `ack_extra` — where the token rides — is not recorded; verified structurally in `_spine` and empirically by the dump grep below).
- **P05/P06/P07 — only the sha256 is stored, and it binds.** `sha256(displayed token) == token_hash` in the row (exact match); the raw value matches no `token_hash` and no `label`; **`pg_dump` of the entire scratch DB contains the token value 0 times** — the whole-database grep, command_log included (the spine's command_log columns are owner/idem/client/command/body_hash/result_ref/actor/created_at — no ack_extra). Belt-and-braces P41: 25 mint command_log rows, none carrying the value in any column.
- **P08 — the argv-safe property, 21 mints.** Every ack committed, every token's first char alphanumeric across 21 mints (suite pins 12); 21 rows, 21 distinct token_hash. A separate 3000-mint adapter probe: **0 leading dashes**, first chars spanning `[0-9A-Za-z_]` — see F-077-4 for the `_` wording nuance (still argv-safe: a live `--agent-token _underscore-leading-value` parsed and reached the lookup).
- **P09/P10 — the label law.** Empty and 129-char labels refuse ARV-AGT-003 exit 1 with zero rows; the NUL class refused in-process at `_agt_label` (argv cannot carry NUL — the law's own layer, per the disclosed amendment); the 128-char boundary ACCEPTED (no off-by-one clamp). Unicode label stored verbatim (`ünïcode-ラベル`, P42).
- **P11/P12 — the outbox and the body.** Zero outbox rows for mint/revoke (no sync ride); same idem key + different label refuses ARV-CMD-409 (the token is the EFFECT, never part of the canonical body).

### §2.2 The agent read mode (claim 2)

- **P13 — byte-equality on 21 arm shapes**, not just the seven claimed: `list-captures, get-source, get-history, get-capture, get-bookmark, get-bookmark-history, get-note, get-note-history, list-bookmarks, list-library, get-reading-state, list-session-events, list-journal, get-journal, get-journal-history, list-lists, get-position, resolve-anchor, resolve-reference (×2 forms), search` — agent vs owner identical in stdout+stderr+exit on every one; 19 distinct arms served at exit 0 through the credential.
- **P15 — pagination parity + audit facts as REQUESTED.** `--limit 7 --after <id>` byte-equal; the audit row records `req_limit|req_after = 7|<the exact cursor id>`. The read_log schema carries only (id, credential_id, owner_scope, arm, req_limit, req_after, created_at) — **never content**, structurally (no content column exists).
- **P16 — refusals never audit.** Audit count 21 → 21 unchanged across ARV-QRY-001 (bad id), ARV-QRY-004 (oversize limit), ARV-AGT-001 (invalid token), and both ARV-AGT-002 identity refusals. The insert happens only after `rc == 0`.

### §2.3 The no-oracle invalid-token class (claim 3)

- **P17 — unknown vs revoked byte-equal.** Both exit 1 with the identical ARV-AGT-001 two-line refusal; neither output contains the token value.
- **P18 — five hostile strings** (SQL metacharacters `x'; DROP TABLE arv.agent_credential;--`, 10k chars, unicode `𝕏🔥日本語トークン`, empty string, control-char): **1 distinct output** — all five the SAME byte-equal ARV-AGT-001 refusal, never echoed, never a traceback.
- **P18b (observed, routed).** A leading-dash token dies at argparse exit 2 (usage error, no traceback, no DB touch) — the separate-argv F-074-1 class; the mint's first-char constraint makes minted tokens structurally unable to hit it, and the family-wide argv-value convention stays routed to F-074-1's own slice exactly as the measured-set repair's letter discloses.

### §2.4 The identity law (claim 4)

- **P19.** `--owner A --agent-token <tok>` → exit 1 `FAIL ARV-AGT-002: the ambiguous identity — --owner and --agent-token together…`; neither → exit 1 `FAIL ARV-AGT-002: the missing identity — neither --owner nor --agent-token…`. Both typed (named code + repair line), so `--owner` is optional-but-required-in-practice with the refusal naming the law.

### §2.5 Read-only structural (claim 5)

- **P20.** `create_note`, **`mint_agent_credential` itself**, `revoke_agent_credential`, and `import_source` all refuse `--agent-token` at the CLI (`error: unrecognized arguments: --agent-token …`, exit 2, zero rows — note count unchanged). No write subcommand defines the flag; the closure includes the slice's own new commands.

### §2.6 The scope isolation (claim 6)

- **P21.** B's credential's `list-library` lists exactly B's source; A's exactly A's; each invisible to the other.
- **P22.** B's credential asking for A's note == a nonexistent id: the same ARV-QRY-001 refusal byte-equal after id normalization (the id is the caller's own input; no cross-scope existence oracle).
- **P23/P24.** B's reads audited under B's credential (2 rows); the read log is RLS-scoped — arv_app under owner B sees 0 of A's audit rows, under A sees 22.

### §2.7 The revocation (claim 7)

- **P25.** The revoke commits (revoked_at NULL→set); the already-revoked refuses ARV-AGT-004 under a NEW key; absent and cross-owner are the SAME ARV-AGT-001 byte-equal after id normalization; post-revocation reads refuse ARV-AGT-001; the read log PRESERVES all 22 pre-revocation rows.
- **P26.** Same-key replay of the revoke returns `status=replayed` exit 0 (the spine's exactly-once; the alternation refusal only fires for a new key).

### §2.8 The substrate — migration 0019 (claim 8)

- **P27 — the closed scopes CHECK.** A hostile superuser INSERT with `scopes='write'` refused at `agent_credential_scopes_check`.
- **P28 — the one-transition guard.** Real mutations of label / token_hash / owner_scope / scopes via arv_app all refuse ARV-AGT-004; the `scopes='write'` UPDATE refuses at the **guard**, which fires before the CHECK (the layer-ordering law). Even a same-value no-op UPDATE is refused (stricter than the claim, fail-closed — see F-077-4b for the message nuance).
- **P29 — one-way even as superuser.** `revoked_at=now()` via arv_app (owner B, RLS-scoped) succeeds; the un-revoke refused as arv_app AND as superuser (`ARV-AGT-004: … the revocation is one-way`).
- **P30/P31 — DELETE/append-only.** DELETE on the credential refused at both arv_app and superuser (the reject trigger fires for superuser too); read_log UPDATE/DELETE refused via arv_app and UPDATE refused as superuser.
- **P32 — RLS.** `pg_class`: `agent_credential|true|true`, `agent_read_log|true|true` (enabled AND forced).
- **P33 — the grants.** credential arv_app `INSERT|SELECT|UPDATE|DELETE = true|true|true|false`; read_log arv_app `true|true|false|false`; arv_read SELECT-only on both, no DELETE anywhere.
- **P34/P35 — the SECURITY DEFINER lookup.** A live read-scoped hash resolves to EXACTLY `A|<credential_id>`; a revoked hash → 0 rows; a fake hash → 0 rows; a **planted write-scoped row** (CHECK dropped as superuser on my scratch rig for the probe, then restored and the plant deleted, both verified) → 0 rows (the function filters `scopes='read' AND revoked_at IS NULL`).
- **P36 (observed → F-077-2).** `arv_read` CAN execute the lookup: PostgreSQL's default PUBLIC EXECUTE was never revoked (`proacl={=X/postgres,postgres=X/postgres,arv_app=X/postgres}`); arv_read resolved a live hash to 1 row. Least-privilege gap vs the migration letter's "GRANT … TO arv_app" — routed finding, bounded impact.
- **P37 — RLS WITH CHECK.** arv_app under owner A cannot INSERT a B-scoped credential row (row-level security policy violation).

### §2.9 The audit-row honesty (claim 9)

- **P38 — the loud failure, forced live.** With `REVOKE INSERT ON arv.agent_read_log FROM arv_app` (superuser, my rig), an agent read SERVES its rows (`# api_version=1` still on stdout) and then refuses: `FAIL ARV-AGT-005: the agent read was served but the audit row refused — …` **exit 1**. Grant restored → the read audits again. An unaudited agent read is never a silent pass.
- (P16 above: the audit insert only ever follows an exit-0 served read.)

### §2.10 The budget (claim 10)

- **P39.** `--limit 99999` on an agent read refuses ARV-QRY-004 **byte-equal to the owner's own refusal**; `--limit 0`, `--limit abc`, `--after not-a-uuid` all refuse ARV-QRY-004; the 1000 boundary serves. The shared `_page_args` law, identical at both identities.

### §2.11 Q10's honest boundary (claim 11)

- **P40.** `capability.py surfaces` carries the `scoped-agent-access` row (owner_phase P4-E, "LANDED in P4-E slice one") naming exactly: the access-shape surface never workflow-tamper hardening; the local single-user threat model; the non-constant-time hash comparison; no rotation/expiry claims; the MCP wrapper as slice two. The wording matches the code I read (no expiry column, no rotation command, plain sha256 comparison).
- `notverified.txt` does not exist at this head — per the family convention it lands at the artifact finalize (claim-076's landed with its re-bind commit); the Q10 limits today live in the capability row + record 69 §2, both verified. Not a defect at this stage; noted so the finalize carries it.

### §2.12 The RED chain (claim 12)

- **Reproduced from the archived tree:** `git worktree add /tmp/sev77red 048a1ddb` → `python3 harness/tests/test_agent_access.py` → **exit 1**, `FAIL ARV-TEST-000: the P4-E slice one scoped-agent-read machinery is absent (machinery-absent class; the mint_agent_credential command absent from the CLI)…` — DB-free probe, matching red-01.txt exactly (exit 1 + ARV-TEST-000 recorded there).
- **red-01.txt** read and matches the observed form (tree 048a1ddb, exit 1, the machinery-absent output quoted verbatim).
- **The red-records amendment chain verified 4 ways by sha256:** binding `6d95aa81…` == sha256(test_agent_access.py @ 048a1ddb, 407 lines) → amendment 1 `ec4f4a69…` == sha256 @ 76dbd74 → amendment 2 `cccefecc…` == sha256 at HEAD == `current_sha256`. The chain is self-consistent (each prior == previous new) and terminates at the HEAD file.

### §2.13 The AGT suite, run once by me

`python3 harness/tests/test_agent_access.py` at HEAD: **PASS AGT-01..08, exit 0, "GREEN — the P4-E agent-access suite (AGT-01..08) passes."** (433 lines at HEAD: the RED's 407 + the four disclosed pin repairs + the twelve-mint strengthener.)

## §3 The static/git verification

1. **Chain order (git log, base→head):** commit A `aad5a43` is docs-only (8 files: AGENTS/CLAIMS/PLAN/STATE/WORKLOG/extracted-68/69 + scope.txt — zero code); the RED `048a1dd` is tests-only (one file, 407 insertions); the binding `6d5e22e` carries red-01.txt + the red-records mint + the gate.py TESTS registration (3 files, 34 insertions — the ARV-RED-008 class, diff-visible); nothing implementation-shaped precedes the RED. The GREEN `cf0fe44` follows the amendments `76dbd74`.
2. **query.py dispatch refactor (diff 76dbd74→cf0fe44 read line-by-line):** `--owner` changed `required=True`→`default=None` on every arm (the identity law's own letter); the identity law added in `main`; the arm chain moved verbatim into the extracted `_dispatch`; no arm SQL or arm logic changed. Regression-proven live: REF-01..06 GREEN, LIB-01..06 GREEN, plus owner-vs-agent byte-equality on 21 shapes and owner spot checks.
3. **LAW-24:** the gate's own `scope.lint_boundary()` passes at HEAD (invoked live); grep confirms no `secrets`/`random`/ambient-time in commands.py/query.py/capability.py; the mint's randomness lives in `adapters/ids.py::new_agent_token` (the LAW-24 repair `f7b6b58` removed `import secrets` from commands.py — diff read: `-import secrets`, `-token = secrets.token_urlsafe(32)`, `+token = ids.new_agent_token()`).
4. **NO outbox ride:** `_SYNC_COMMANDS` (commands.py:60) does not contain `mint_agent_credential`/`revoke_agent_credential`; live-proven zero outbox rows (P11).
5. **gate.py TESTS registration** present at HEAD (`harness/tests/test_agent_access.py` in the TESTS tuple, line 111).
6. **scope.txt** exists and declares 16 entries — but the base→HEAD diff contains `harness/adapters/ids.py`, which is NOT declared: the gate's own checks fire (see F-077-1).
7. **The measured set** (run-01..11.json, untracked): run-01 GREEN at the GREEN tree; runs 02/03 exit 1 at `cf0fe44` (the disclosed leading-dash RED, evidence kept); run-04 GREEN at `79b5f43`; run-11 `make verify` exit 0 at `f7b6b58`.
8. **CLAIMS.md row + record 69** read: the row's file-set cell matches scope.txt (and shares its omission of adapters/ids.py — part of F-077-1); record 69 §2 carries the Q10 honest-boundary language matching the capability row.
9. **capability.py** read in full: the scoped-agent-access reserved-surface row's claims match the code (no rotation/expiry machinery exists; the comparison is plain sha256 equality).

## §4 Findings

- **F-077-1 — P2 — OPEN (in-slice; must repair before the PR; fail-closed by the repo's own gate).** *The scope-declaration drift: `harness/adapters/ids.py` changed at the LAW-24 repair but never joined the declaration.* The LAW-24 repair `f7b6b58` moved the token mint into `adapters/ids.py` (+16 lines), but `scope.txt` and the CLAIMS.md row's file-set cell were never widened. Live evidence — I invoked the gate's own functions on the base→HEAD diff:
  `FAIL ARV-SCOPE-002: harness/adapters/ids.py outside the declared scope — scope breach (LAW-06)` and
  `FAIL ARV-CLM-002: CLAIM-077: the diff touches 'harness/adapters/ids.py' OUTSIDE its declared scope`.
  The slice as it stands cannot pass its own PR-mode gate. WHERE/WHY in-slice: the omission was made by this slice's repair commit (not pre-existing — the file set was frozen at the RED against a design that did not yet include the adapter move). Repair: add `harness/adapters/ids.py D-041` to scope.txt + the CLAIMS.md row's cell (a declaration repair; the code change itself is lawful and disclosed).
- **F-077-2 — P3 — OPEN (in-slice; routed to a follow-up migration).** *`arv.agent_token_lookup` retains PostgreSQL's default PUBLIC EXECUTE.* The migration grants EXECUTE to arv_app but never revokes PUBLIC (`proacl={=X/postgres,…}`); live: arv_read resolved a live hash to 1 row. Impact bounded — the caller must already possess a valid 190-bit token hash, the disclosed pair (owner_scope + credential_id) is exactly what the token holder legitimately learns at read time, and the Q10 boundary names the local single-user threat model — but the migration's "narrow … GRANT TO arv_app" letter overstates the narrowness. Repair: `REVOKE EXECUTE ON FUNCTION arv.agent_token_lookup(TEXT) FROM PUBLIC;` in a follow-up migration.
- **F-077-3 — P3 — OPEN (in-slice, cosmetic/debt).** *query.py carries the agent functions TWICE, verbatim.* `_agent_resolve` + `_agent_audit` are defined identically at lines 1031-1082 and again at 1084-1135 (byte-equal blocks — verified programmatically), born at the GREEN `cf0fe44`. Behavior-neutral (the second definition shadows the first; they are identical), but 52 duplicated lines in the slice's own new surface, and the repo's custom lint has no redefinition check to catch it. Repair: delete one copy.
- **F-077-4 — P3 — NOTED (in-slice, wording precision; no behavior impact).** (a) The docstring/commit letter says the token's first character is "constrained to the alphanumeric range", but the code enforces `tok[0] != "-"` — a leading `_` can and does occur (43/3000 mints observed; live `--agent-token _underscore-leading-value` parses and reaches the lookup, so the argv-safe property itself holds; the suite's pin checks exactly "no leading dash", matching the code, not the docstring). (b) The one-transition guard refuses even a same-value no-op UPDATE on a live credential, with the "revoked_at cannot be cleared once set" message — a wording that presumes a prior set. Both fail-closed strictness/wording only; the entropy cost and the security properties are unaffected.

No P0. No P1. No routed-to-pre-existing-substrate findings — all four findings are in-slice (the slice's own new surface), which is expected for a slice that composes the existing spine/RLS conventions rather than touching them.

## §5 Honest limits

- **The head-hash discrepancy in my instructions:** the task brief named `79b5f43` as head; git ground truth is `f7b6b58` (the LAW-24 repair, `79b5f43`'s child). I verified at the actual head; had I stopped at `79b5f43`, the LAW-24 state (secrets import removed, adapter mint) would NOT have been what I tested.
- **notverified.txt** does not exist at this head (the family convention lands it at the artifact finalize); I verified the Q10 limits in the capability row and record 69 instead, and flag that the finalize must carry them.
- **Statistical probes:** the 3000-mint distribution is statistical (0 leading dashes observed where ~47 were expected pre-repair; the exclusion is structural in the loop). The timing side channel (non-constant-time comparison) is named in Q10 and not measured beyond existence.
- **I did not re-run the full canonical layer (`make verify`)** — the author's run-11 records it GREEN at this head; I independently ran the AGT suite, the REF and LIB family suites, and the gate's scope/claims/lint functions in-process.
- **No concurrency or DoS claims tested** (single-client rig; those classes belong to the spine's prior families). The revoke's read-before-BEGIN shape was reasoning-verified only: the worst case is a typed ARV-AGT-004 refusal, never a wrong state.
- **The planted write-scoped probe** temporarily dropped the scopes CHECK **on my own scratch DB** (restored and verified restored; the planted row deleted; no shared state touched).
- **Rig hygiene observation (outside the repo):** ~11 stale debug scratch DBs from earlier sessions (`arv_agtdbg*`, `arv_agtdebug*`, `arv_ntr16dbg*`, `arv_d042probe*`, …) remain on the shared rig. None were created by this round; every DB I created is dropped (verified by catalog query).
- My probe artifacts: `/home/z/my-project/scripts/sev77r1_probe.py` (the rig) and `/home/z/my-project/scripts/sev77r1-log.txt` (the captured log). Zero writes inside the repo.
