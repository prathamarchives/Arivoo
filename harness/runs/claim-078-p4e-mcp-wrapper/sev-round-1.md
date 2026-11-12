# CLAIM-078 — SEV round 1

| field | value |
|---|---|
| **Agent** | independent fresh-context SEV reviewer (SEV round 1, CLAIM-078) |
| **Date** | 2026-11-12 (rig local) |
| **Round** | SEV round 1 (P4-E slice two: the MCP wrapper over the same retrieval core) |
| **Base** | `505cb336` (main, CLAIM-077's merge) — verified |
| **Head** | `169f9de62a1aa347279ef1bf668547d6a632835d` on `slice/claim-078-p4e-mcp-wrapper` — **matches the brief exactly**; working tree clean |
| **Chain** | `96aeda4` (docs/records) → `e090ba2` (RED, tests-only) → `db0ead9` (red record + gate TESTS) → `ec46d46` (3 disclosed pin amendments, tests only) → `63143e4` (GREEN: mcp.py NEW + query.py env form + capability.py row) → `169f9de` (measured set) — verified via `git log --oneline 505cb336..HEAD` |
| **Method** | own scratch DB (`arv_sev78r1_*`, created/migrated/dropped by me), own two-owner fixture (sources/highlight/notes/journal/bookmark/position/session-events/reading-list for A; source+note for B; two minted credentials), own probe rig `/home/z/my-project/scripts/sev78r1_probe.py` driving `harness/mcp.py` as a live stdio subprocess (reader thread, timeouts everywhere, hostile-input sessions), log at `/home/z/my-project/scripts/sev78r1-log.txt`. ZERO writes inside the repo worktree (the RED reproduction used a throwaway `git worktree` at `/tmp/sev78red`, removed afterwards; `git worktree list` and `git status` re-checked clean). |
| **Probe count** | **57 probes: 52 PASS, 0 FAIL, 5 OBSERVE** (P00–P54b; OBSERVEs are honest-behavior notes / out-of-letter findings, graded in §1) |

---

## §1 Verdict

## **PASS** (no open P0/P1; one P2 + three P3 findings, all with live evidence below)

Every behavior claimed in the slice letter reproduced live on my own rig: the stdio transport (nothing but valid MCP messages on stdout, clean exit 0 on stdin close), the full protocol surface (version negotiation, notification silence, ping, tools/list, tools/call, -32601/-32700/-32600/-32602 hygiene, string-id echo), the 22-arm read-only registry with the ARV-MCP-001 refusal, the same-retrieval-core law (16 arms byte-equal wrapper-vs-direct, typed refusals as `isError` byte-equal to the direct CLI), the token-by-environment channel (identity matrix, token value never echoed, no wrapper auth answers), the audit law (served reads audited with arm+req facts, refused reads not, B's isolation with B's audit rows), the shared budgets and the argv-safety convention, the RED at `e090ba2`, the sha-linked amendment chain, the scope declaration (gate's own `check_scope` clean), and the sibling regressions (AGT 9/9, references, library, MCPW 8/8 — all exit 0 on my own runs).

### Open findings

**F-078-1 (P2) — a NUL-bearing or over-long string tool argument crashes the wrapper process (the request is never answered).**
- *Behavior:* `tools/call` with a declared, scalar string argument containing `\u0000` (or a string longer than the OS per-argv limit, demonstrated at 200k chars) raises inside `subprocess.run` in `harness/mcp.py::_tools_call` — the `except` arm catches only `subprocess.TimeoutExpired`, so `ValueError: embedded null byte` (resp. `OSError: [Errno 7] Argument list too long`) propagates: the process dies with exit 1, a traceback goes to stderr, the JSON-RPC request gets NO response, and the client sees the pipe close.
- *Live evidence (P36c/P36d):* `search` with terms `["sesquine\x00marker"]` → `NO ANSWER: recv='EOF'; server exit=1; stderr tail='…subprocess.py", line 1885, in _execute_child … ValueError: embedded null byte'`; `get-journal` with id `"y"*200000` → `OSError: [Errno 7] Argument list too long`. In both: stdout stayed clean (no invalid MCP line was ever emitted), no data escaped, the credential table untouched.
- *Severity reasoning:* it cannot serve a wrong answer, leak scope, or expose a secret — the process simply dies on hostile/buggy client input, and the only client in the declared threat model is the local single user (stdio, no listener — verified). It is **not** a falsification of a lettered claim: the letter's crash-freedom is scoped to malformed JSON lines (-32700), non-object lines (-32600), and unknown methods (-32601), and the argument law's refusal classes are undeclared-key / non-scalar / missing-required / empty-terms — a NUL-bearing or oversized *scalar* is outside those named classes (it is also unrepresentable in a direct CLI invocation: the OS argv layer refuses it before query.py could ever see it, which is why no typed product rule exists for it). It is nonetheless a real robustness defect in the in-slice new code (`mcp.py`, the one `subprocess.run`). P2 per the rubric.
- *Routing:* in-slice new code (`harness/mcp.py::_tools_call`). Suggested repair for a follow-up slice: catch `(ValueError, OSError)` at the spawn and answer the JSON-RPC `-32603` (or a typed ARV-MCP-003) — the convention the timeout arm already follows.

**F-078-2 (P3) — a `tools/call` sent BEFORE any `initialize` is served.**
- *Live evidence (P40):* fresh server, `tools/call list-library {"limit":"2"}` as the very first message → served (`isError=false`, correct scoped rows). The MCP spec makes the ordering a client-side SHOULD NOT; the slice letter claims no pre-init rejection (verified: it does not). Honest note only — many MCP servers answer `-32002` here; this one serves. No wrong answer results (the read is still credential-scoped and audited). Out-of-letter; P3.

**F-078-3 (P3) — a request with `"id": null` is answered with `"id": null`.**
- *Live evidence (P47):* `{"jsonrpc":"2.0","id":null,"method":"ping"}` → `{"jsonrpc": "2.0", "id": null, "result": {}}`. JSON-RPC discourages null ids from clients; the echo is faithful and harmless. P3 note.

**F-078-4 (P3) — invalid UTF-8 on stdin survives on the delivered rig; a strict-encoding override would not.**
- *Live evidence (P45):* raw bytes `\xff\xfe not utf8 \xff` on stdin → the server answers `{"jsonrpc":"2.0","id":null,"error":{"code":-32700,…}}` for that line, answers both surrounding pings, and exits 0 on stdin close (3 stdout lines, all valid JSON). This holds under the rig's default locale (UTF-8 mode with surrogateescape). Under an operator-forced `PYTHONIOENCODING=utf-8:strict` the same input kills the process with `UnicodeDecodeError` before any response (verified separately). The letter claims a UTF-8, newline-delimited transport and -32700 for malformed JSON *lines* — on the environment as delivered both hold; the strict-override case is an environment caveat, not a lettered claim. P3.

No P0 (no wrong answer served, no isolation leak, no secret persisted — the token value never appeared in any response, list, or error across all sessions) and no P1 (every lettered behavior reproduced; no containment escape — stdout stayed valid MCP messages in every session including the hostile ones).

---

## §2 The live verification

All outputs below are verbatim from `/home/z/my-project/scripts/sev78r1-log.txt` (my own rig, my own fixture, my own scratch DB).

### Claim 1 — the transport (P12/P12b/P13/P45)

```
### [P12] PASS — exit code after stdin close = 0; stderr=''
### [P12b] PASS — immediate close exit = 0; stderr=''
### [P13] PASS — 16/16 stdout lines valid JSON; exit 0; stderr 0 chars
### [P13b] PASS — stderr empty or diagnostics-only (no traceback)
### [P45] OBSERVE — invalid UTF-8: exit=0, 3 stdout lines, all-JSON=True, survived
```
P13 is one long adversarial session (initialize, notification, blank line, whitespace-only line, `{bad json`, `[1,2,3]`, `null`, ping, unknown method, unknown notification, a served read, refused write-name call, empty-terms call, dict-id call, leading-dash id, oversize limit, a 2k-char unicode string id echo, a legal paged read, more garbage JSON, tools/list, then stdin close): every one of the 16 stdout lines parsed as JSON, exit 0, stderr completely empty. The invalid-UTF-8 probe (P45) shows the bad line itself answered as `-32700` with id null and the session continuing (see F-078-4 for the strict-locale caveat).

### Claim 2 — the protocol surface (P01–P11)

```
{"jsonrpc": "2.0", "id": 100, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "arivo", "title": "Arivo — the owner's reading and reflection context", "version": "1"}, "instructions": "READ-ONLY scoped agent access …"}}
### [P01] PASS — initialize answers the supported version, tools capability, arivo
["2025-06-18", "2025-06-18"]
### [P02] PASS — unsupported versions answered with the server's own   (requested 2024-11-05 and 1999-01-01 — never an echo)
### [P03] PASS — missing/non-string version -> the server's own 2025-06-18
### [P04] PASS — silence=True; ping after answered=True               (notifications/initialized NEVER answered)
### [P05] PASS — {"jsonrpc": "2.0", "id": 108, "result": {}}           (ping → the empty result)
{"jsonrpc": "2.0", "id": 110, "error": {"code": -32601, "message": "Method not found: resources/list (the adapter's surface is initialize/ping/tools/list/tools/call)"}}
### [P07] PASS — -32601 with the id carried
{"jsonrpc": "2.0", "id": null, "error": {"code": -32700, "message": "Parse error: the line is not valid JSON"}}
### [P08] PASS — -32700 id null; ping still answered
### [P09] PASS — array/number/string/null lines all -32600              (batching refused; scalar JSON lines too)
### [P10] PASS — silence=True, ping answered after                      (unknown NOTIFICATION → no response)
{"jsonrpc": "2.0", "id": "sev-id-☃-123", "result": {}}
### [P11] PASS — unicode string id + numeric id echoed verbatim
```

### Claim 3 — the tool registry (P06/P37/P24)

```
count=22 sorted=['get-bookmark', 'get-bookmark-history', 'get-capture', 'get-history', 'get-journal', 'get-journal-history', 'get-list', 'get-note', 'get-note-history', 'get-position', 'get-reading-state', 'get-source', 'list-bookmarks', 'list-captures', 'list-journal', 'list-library', 'list-lists', 'list-notes', 'list-session-events', 'resolve-anchor', 'resolve-reference', 'search']
### [P06] PASS — 22 arms exact; every entry name/description/inputSchema; no write tool (leaked=[])
  name 'record_session': -32602=True echoed=False
  name 'import_source': -32602=True echoed=False
  name '../../etc/passwd': -32602=True echoed=False
  name 'harness/query.py': -32602=True echoed=False
  name 'tools/call': -32602=True echoed=False
  name '': -32602=True echoed=False
  name 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx': -32602=True echoed=False        (a 10k-char name)
  name 'search ' / 'SEARCH' / 'list-library\x00evil' / 'ping' / '-h' / '--help': all -32602=True echoed=False
### [P37] PASS — write commands / path-like / huge / empty / NUL names refused ARV-MCP-001 without echo; server keeps answering
  command_log rows before/after refused write-name calls: 15 -> 15
### [P24] PASS — … refused write names execute nothing (no passthrough)
```
Every refusal message names ARV-MCP-001 in the -32602 form and does NOT echo the requested name; after the barrage the server still answered a ping and a served `list-library`. The command_log delta of 0 confirms no passthrough executed anything.

### Claim 4 — the same retrieval core, byte-for-byte (P14/P22)

16 arms driven through `tools/call` on one server instance, each compared to a direct `query.py <arm> --agent-token <value> …` invocation on the same data:

```
  list-library: byte-equal=True isError=False (direct rc=0, len=66)
  get-journal: byte-equal=True isError=False (direct rc=0, len=240)
  list-notes: byte-equal=True isError=False (direct rc=0, len=103)
  resolve-reference: byte-equal=True isError=False (direct rc=0, len=166)
  search: byte-equal=True isError=False (direct rc=0, len=148)
  get-position: byte-equal=True isError=False (direct rc=0, len=297)
  get-reading-state: byte-equal=True isError=False (direct rc=0, len=326)
  get-note: byte-equal=True isError=False (direct rc=0, len=392)      (note content carries 🎉/café unicode)
  get-source: byte-equal=True isError=False (direct rc=0, len=364)
  list-journal: byte-equal=True isError=False (direct rc=0, len=66)
  list-captures: byte-equal=True isError=False (direct rc=0, len=66)
  get-list: byte-equal=True isError=False (direct rc=0, len=149)
  list-lists: byte-equal=True isError=False (direct rc=0, len=187)
  list-bookmarks: byte-equal=True isError=False (direct rc=0, len=66)
  list-session-events: byte-equal=True isError=False (direct rc=0, len=673)
  get-bookmark: byte-equal=True isError=False (direct rc=0, len=360)
### [P14] PASS — 16 arms byte-equal wrapper-vs-direct (incl. unicode content)
```
All 7 arms named in the claim plus 9 more. Nonzero CLI exits surface as `isError: true` with the CLI's own typed text, byte-equal:

```
  AGT-001 via wrapper (bad env token): FAIL ARV-AGT-001: the credential does not grant access — unknown, revoked, and scope-missing are the SAME refusal, never a side ch…
### [P22a] PASS — the no-oracle ARV-AGT-001 surfaced as isError, byte-equal, token never echoed
  QRY-001 via wrapper: FAIL ARV-QRY-001: no such journal block in the caller's scope — absent and another owner's are the SAME refusal…
### [P22b] PASS — the no-object ARV-QRY-001 as isError, byte-equal
  QRY-004 via wrapper: FAIL ARV-QRY-004: --limit 5000 is outside the bounds 1..1000
### [P22c] PASS — the bounds ARV-QRY-004 as isError, byte-equal
  no-identity via wrapper: FAIL ARV-AGT-002: the missing identity — neither --owner nor --agent-token nor the ARIVO_AGENT_TOKEN environment…
### [P22d] PASS — no env token -> the CLI's own ARV-AGT-002 missing-identity refusal (never a wrapper auth answer)
```

### Claim 5 — the token by environment (P24/P25/P25b + static §3)

```
  token A/B value in responses: False/False; '--agent-token' in responses: False; env-var NAME mentioned (instructions, disclosed): True
### [P24] PASS — the credential value never in any response text (lists/calls/errors); refused write names execute nothing
  owner-only=True(rc=0); argv-token-only=True(rc=0); env-token-only=True(rc=0); argv+env-token=True(rc=1); owner+env-token=True(rc=1); none=True(rc=1)
### [P25] PASS  (all six identity combinations behave; the three refusals all name ARV-AGT-002)
### [P25b] PASS — env-token answer byte-equal to the argv-token answer (the SAME downstream path)
```
The identity matrix, run directly against query.py: `--owner` alone serves; `--agent-token` alone serves (the pre-existing argv form unchanged); `ARIVO_AGENT_TOKEN` alone serves; argv-token+env-token together refuses ARV-AGT-002; `--owner`+env-token refuses ARV-AGT-002; neither refuses ARV-AGT-002. The wrapper works with the token ONLY in env (P14/P22/P26–P28 all ran that way), and since argv-token+env-token together would refuse (P25), the wrapper demonstrably passes NO token in the child argv. The initialize `instructions` mention the env-var NAME (the documented channel) — the VALUE never appears anywhere.

### Claim 6 — the audit (P26/P27/P28)

```
  delta=4 (expect 4); last 4 rows (arm|req_limit|req_after):
  list-library|7|
  search||
  get-journal||
  list-library|100|
  agent_read_log columns: id, credential_id, owner_scope, arm, req_limit, req_after, created_at
### [P26] PASS — 4 served reads -> 4 rows (arm/req_limit/req_after under A's credential; never content)
  refused reads: delta=0 (expect 0)
### [P27] PASS — AGT-001/QRY-004/QRY-001 refusals land no audit row
  B's wrapper list-library byte-equal=True; SID_B visible=True; SID_A invisible=True
  B's audit delta=2 (expect 2: the two wrapper reads under B's credential)
### [P28] PASS — B sees only B (byte-equal, A's ids invisible); audit rows under B's credential
```
Audit rows carry the arm and the bounded REQUEST facts (req_limit as requested — `7` when `limit:"7"` was passed, the default `100` when omitted — and req_after), never content (no row carries the note/journal text markers). Refused reads (bad token, oversize limit, absent id, non-integer limit) land zero rows. B's credential through the wrapper returns B's library byte-equal to B's direct read with A's source id invisible, and B's wrapper reads audit under B's credential id.

### Claim 7 — the budgets + argv-safety + the argument law (P29/P32/P35)

```
### [P29a] PASS — limit "5000" -> the same ARV-QRY-004 refusal, isError      (byte-equal to the direct read)
### [P29b] PASS — limit "abc" -> the same ARV-QRY-004 refusal
### [P29c] PASS — limit as JSON integer 5000 -> coerced -> the same ARV-QRY-004 refusal
  limit 3 + after cursor: isError=False
### [P29d] PASS — a legal limit+after page serves
  search '-dashy': isError=False direct rc=0; first line: '# api_version=1 kind|entity_id|revision|matched_terms'; direct stderr=''
### [P32a] PASS — the leading-dash term reaches the product's typed rule, never argparse's usage exit
  get-journal '-not-a-real-id': direct rc=1; first line: 'FAIL ARV-QRY-002: the read failed — ERROR:  invalid input syntax for type uuid: "-not-a-real-id"'
### [P32b] PASS — the leading-dash id reaches the product's typed rule, never argparse's usage exit
  malformed uuid: 'FAIL ARV-QRY-002: the read failed — ERROR:  invalid input syntax for type uuid: "not-a-uuid"'
### [P32c] PASS — the malformed uuid id -> the product's typed ARV-QRY-002 (byte-equal to direct)
  undeclared key / dict value / list value / bool value / float value / missing required / empty terms / dict term / list term / bool term: all OK -32602/ARV-MCP-002
### [P35] PASS
  arguments missing: {"jsonrpc": "2.0", "id": 175, "error": {"code": -32602, "message": "ARV-MCP-002: the arguments must be an object …
  arguments {} on id-arm: {"jsonrpc": "2.0", "id": 176, "error": {"code": -32602, "message": "ARV-MCP-002: the required argument 'id' is missing …
  arguments {} on list-arm serves: isError=False
### [P35b] PASS
  params missing name: {"jsonrpc": "2.0", "id": 178, "error": {"code": -32602, "message": "ARV-MCP-001: unknown tool — the registry is EXACTLY the landed READ arms …
### [P35c] PASS — tools/call without name -> -32602 ARV-MCP-001
### [P35d] PASS — tools/call with non-object params -> -32602 ARV-MCP-001
  integer source coerced: 'FAIL ARV-QRY-002: the read failed — ERROR:  invalid input syntax for type uuid: "12345"'
### [P35e] PASS — integer scalar coerced to the typed CLI rule (no usage exit)
```
No "usage:" text and no argparse exit-2 signature surfaced anywhere; every hostile DATA value reached the product's own typed rules.

### Claim 8 — the Q10 boundary (P13/P45 + static §3)

Stdio only — the AST-level static check found no socket/listener machinery, no HTTP/SSE server code (see §3). The long adversarial session (P13) kept stdout 100% valid MCP messages with empty stderr; a second concurrent instance (P42) behaved identically. Diagnostics never appeared on stdout in any probe.

### Adversarial extras (P36/P40/P41/P42/P47)

```
  sql-meta: answered=True isError=True first line: 'FAIL ARV-QRY-002: … invalid input syntax for uuid: "\'; DROP T…
  unicode-id: answered=True isError=True …  10k id: answered=True isError=True …
  sql term: answered=True isError=False …  unicode term: answered=True isError=False
### [P36] PASS — hostile values answered as MCP results; byte-equal SQL=True, 10k-term=True; server alive
### [P36b] PASS — agent_credential still 2 rows after hostile data (2)
### [P36c] OBSERVE — a NUL-bearing string argument kills the server (exit=1, request unanswered, traceback on stderr only — stdout stayed clean)   → F-078-1
### [P36d] OBSERVE — a 200k-char argument kills the server (exit=1, request unanswered)                                                       → F-078-1
### [P40] OBSERVE — pre-initialize tools/call SERVES (spec ordering is SHOULD NOT; the letter claims no pre-init rejection)                    → F-078-2
### [P41] PASS — 6 sequential requests answered in order [219, 220, 221, 222, 223, 224]
### [P42] PASS — concurrent A/B instances each scope-correct
### [P47] OBSERVE — id:null treated as a request and answered with id null                                                                     → F-078-3
```

### Claim 9 — the RED (P48)

```
  exit=1
  stdout:
    FAIL ARV-TEST-000: the P4-E slice two MCP-wrapper machinery is absent (machinery-absent class; harness/mcp.py not on disk) — the implementation lands after this RED, never before it (LAW-11)
### [P48] PASS — RED at e090ba2: exit 1, ARV-TEST-000 machinery-absent (worktree cleaned up)
```
Reproduced from a throwaway `git worktree add /tmp/sev78red e090ba2` (with `PGDATABASE=arv_sev78_red_probe_absent` — the nonexistent probe DB was never reached); the worktree was removed afterwards and `git worktree list` re-checked clean.

### Claim 10 — the amendment chain (P49)

```
  binding_commit=e090ba2b899e binding_sha256 matches e090ba2 tree: True      (5fdc2463… == sha256 of git show e090ba2:…test_mcp_wrapper.py)
  current_sha256 matches HEAD file: True; amendment chain links (1 amendment): True   (e8d63b41… == sha256 of the file at HEAD)
  red_exit=1 red_code=ARV-TEST-000
### [P49] PASS — binding commit/sha + current sha + the amendment prior/new chain all link
```
The single amendment's `prior_sha256` equals the binding sha, its `new_sha256` equals the current sha — the chain links exactly, and the amendment note discloses the three pre-GREEN pin repairs (MCPW-03 audit-count form, MCPW-06 QRY-002 pin, MCPW-07 id-set form).

### Claim 11 — the scope declaration (P50)

```
  diff paths (base...HEAD): AGENTS.md, CLAIMS.md, PLAN.md, STATE.md, context/WORKLOG.md,
    context/extracted/69-…, context/extracted/70-…, harness/capability.py, harness/gate.py,
    harness/mcp.py, harness/query.py, harness/red-records.json,
    harness/runs/claim-078-p4e-mcp-wrapper/{red-01,run-01..04,scope}.txt/.json,
    harness/tests/test_mcp_wrapper.py
  check_scope fails: []
  gate.py TESTS tuple: 36 suites; MCPW registered: True
  CLAIMS.md row covers every diff path: True (missing=[])
### [P50] PASS — scope.txt covers the diff (gate check_scope clean); CLAIMS.md row the same set; TESTS registration present
```
Run through the gate's own machinery (`harness.scope.diff_paths("505cb336")` + `check_scope(paths, "claim-078-p4e-mcp-wrapper")`): zero failures; every diff path is covered by a scope line (the run-dir prefix covers the runs artifacts); the CLAIMS.md open row declares the identical set; the gate.py TESTS tuple registers the new suite (the ARV-RED-008 class, parsed from gate.py's AST).

### Claim 12 — the sibling regression (P51/P52/P53)

```
### [P51] PASS — AGT suite exit 0, 9/9 PASS      (test_agent_access.py at HEAD — AGT-01..09 all PASS, incl. AGT-09 the F2-077-5 quote-bearing-owner pin)
### [P52] PASS — references exit 0, library exit 0
### [P53] PASS — MCPW-01..08 all PASS, exit 0     (the slice's own suite, my own run on my own scratch DB)
```
The query.py identity-law extension did not break slice one; two other read-family suites are green; the slice's own suite is green under my own rig (corroborating the measured set's run records).

---

## §3 Static verification

I read `harness/mcp.py` in full (342 lines) and re-verified every structural claim mechanically with an AST-level probe (P54/P54b) — comments and docstrings excluded from the assertions, so only CODE is checked:

```
  [OK] imports are stdlib-only + harness.commands.API_VERSION (no adapters, no sockets)
  [OK] never reads the environment (no os.environ / getenv anywhere in code)
  [OK] no randomness/time/uuid in code (LAW-24)
  [OK] no socket/listener machinery in code
  [OK] no DB path in code (no psql call, no adapters import, no SQL string)
  [OK] exactly ONE subprocess.run — the query.py child
  [OK] the child call passes NO env= (the inherited environment)
  [OK] the child call has the timeout bound
  [OK] exactly ONE stdout write site in code (the _out writer; flush is its own)
  [OK] the -- separator + the --opt=value form in the argv assembly
  imports: ['json', 'os', 'pathlib', 'subprocess', 'sys', 'from harness.commands: API_VERSION']
  subprocess.run calls: 1 args=['[sys.executable, QUERY, name, *argv]'] kwargs=['capture_output', 'text', 'timeout', 'cwd']
### [P54] PASS
  lint_boundary fails: []; check_deps fails: []
### [P54b] PASS — LAW-24 boundary lint clean; LAW-08 deps clean (mcp.py included)
```

- **Secrets:** the wrapper never reads, parses, or echoes the credential — no `os.environ`/`getenv` anywhere in code (the only `os` uses are path computations; the string "ARIVO_AGENT_TOKEN" appears only in comments/docstrings and in `initialize`'s `instructions`, which names the CHANNEL, never a value).
- **LAW-24:** no `random`/`time`/`uuid`/`secrets`/`datetime` in code; the gate's own `lint_boundary()` and `check_deps()` are clean over the whole harness tree.
- **No second retrieval path:** exactly ONE `subprocess.run` in the file — `[sys.executable, QUERY, name, *argv]` with `cwd=REPO` — and no SQL string, no psql, no adapters import, no DB connection. `QUERY` is `harness/query.py` itself. The only data path is the child.
- **One stdout writer:** a single `sys.stdout.write` call site (`_out`), no `print` anywhere; `sys.stdout.flush` is the writer's own flush. Every probe's stdout observation corroborates (P13: all lines valid JSON, stderr empty).
- **Env inheritance:** the child call passes no `env=` — the inherited environment (including `ARIVO_AGENT_TOKEN`) flows to query.py; the child argv (arm name + `--opt=value` forms + `--` before positional search terms) carries no secret. Confirmed live: env-token+argv-token together would refuse ARV-AGT-002 (P25), and the wrapper serves with env-only — so no argv token is passed.
- **Q10:** no sockets/listeners/HTTP/SSE machinery in code; stdio only, as claimed.
- One nuance verified in the source (line 292): the tool text is the child's stdout VERBATIM; the child's stderr surfaces only when stdout is empty — never a rewrite. (Consistent with all observed refusals, which print their typed text to stdout.)

---

## §4 The honest limits

1. **The measured-set run records** (runs 01–04 in `harness/runs/claim-078-p4e-mcp-wrapper/`) were not re-verified artifact-by-artifact; I re-ran the four most relevant suites myself instead (P51–P53, all green), which corroborates run-04's substance but not its JSON record fields.
2. **I did not run the full `make verify`** (36 suites + known-bad + canonical layer). I ran the MCPW, AGT, references, and library suites plus the gate's own scope/LAW-24/LAW-08 checks; the rest of the tuple is outside this slice's blast radius.
3. **Byte-equality was verified as decoded-UTF-8 string equality** between the wrapper's `content[0].text` and the direct CLI stdout (both sides decode the same bytes; unicode content — 🎉, café, 中文 — round-tripped exactly). The transport's `ensure_ascii=False` re-encoding was exercised, not byte-inspected.
4. **The no-token-in-argv proof is behavioral + static**, not a ptrace: the two-channel refusal (P25) plus env-only serving plus the AST argv inspection jointly establish it; I did not trace the child's execve.
5. **F-078-1's full exception surface was sampled, not enumerated**: I demonstrated the NUL and E2BIG vectors; other OS-level spawn failures (e.g. ENOMEM) plausibly share the uncaught path but were not fired.
6. **F-078-4's locale dependence**: the invalid-UTF-8 survival was verified under the rig's default locale (UTF-8 mode/surrogateescape); I characterized (but did not "fix") the strict-`PYTHONIOENCODING` failure mode — the delivered rig and CI default are the surviving configuration.
7. **MCP spec conformance beyond the letter** (e.g. `-32002` for pre-init requests, `jsonrpc`-field validation of `"2.0"`, `notifications/cancelled`) was observed where probed but is not claimed by the slice; I graded only the letter's claims.

**Verdict: PASS** — CLAIM-078's letter is reproducibly true on an independent rig; the one P2 (F-078-1, the NUL/oversize-argument crash of the wrapper process itself — out-of-letter, no wrong answer possible) and the three P3 notes are routed for a follow-up slice, none blocking.
