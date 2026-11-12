# CLAIM-078 — SEV round 2

- **Agent:** independent fresh-context SEV round-2 reviewer (no shared context with the slice author; round 1 was a different reviewer whose P2 the author repaired)
- **Date:** 2026-11-12T06:50:37Z (observed live)
- **Round:** 2 — the repair-verification round for CLAIM-078 (P4-E slice two: the MCP wrapper over the same retrieval core)
- **Base:** `505cb336` (CLAIM-077's merged head) · **Head (actual, verified):** `bd5d71999405507988c40e7137d69c4791db0db2` (`bd5d719`, as expected)
- **Chain (base→head, git-verified):** `96aeda4` commit A → `e090ba2` RED (tests-only) → `db0ead9` binding → `ec46d46` pre-GREEN amendments → `63143e4` GREEN → `169f9de` measured set → `1506df3` round-1 repair PIN (MCPW-09, red-02.txt) → `865ac1c` round-1 REPAIR (mcp.py spawn arm) → `bd5d719` measured set at the repair tree
- **Method:** own scratch rig (scratch DB `sev78r2`, own minted A/B credentials, `ARIVO_AGENT_TOKEN` set only in the server's env), a binary-pipe MCP client with per-read timeouts, 19 numbered probes + a 21-form OS-hostile sweep; probe at `scripts/sev78r2_probe.py`, full log at `scripts/sev78r2-log.txt`; ZERO writes inside the repo worktree (`git status --porcelain` clean before AND after; the RED reproduction ran in a `/tmp` git worktree, removed afterwards); no commits made
- **Probe counts:** **19 probes — 14 PASS / 4 OBSERVE / 1 FAIL** (the FAIL is P06, the evidence probe for the new finding F2-078-1, not a failure of the repair); the P05 sweep additionally drove 21 hostile forms, all answered

---

## §1 Verdict

**PASS** (verdict rule: any open P0/P1 = BLOCKED; else PASS — no P0/P1 is open).

**F-078-1 (round 1's P2): VERIFIED CLOSED, live.** The repair (commit `865ac1c`) is confirmed at the actual head on my own rig: the NUL-bearing scalar argument and the 200k-character id are both answered as JSON-RPC `-32603` errors naming `ARV-MCP-003` (the exception TYPE name only — `ValueError`/`OSError`), never a dead process; the value never appears in the response; the SAME server session answers the next ping and exits 0 on the stdin close (P02/P03/P04). The regression pin MCPW-09 is GREEN at head (P14) and its disclosed RED reproduces from the archived pre-repair tree `1506df3` (P15). No regression around the touched code: byte-equality, the audit law, the identity matrix, the registry, and the protocol hygiene all re-verified live (P07–P11), the sibling AGT suite GREEN (P16).

**Open findings (this round's sweep):**

- **F2-078-1 (P2, open, routed — the headline NEW finding).** A single VALID-JSON line nested deeper than the interpreter's json recursion cliff (cliff bracketed live: depth 9000 parses, depth 10000 raises; demonstrated at 20000, a ~40KB line of brackets) kills the wrapper: `RecursionError` from `json.loads` is NOT a `ValueError`, so it escapes the parse arm's `except ValueError` (mcp.py `main()`), the process dies with the request unanswered (stdout clean — nothing invalid written), exit 1, a traceback on stderr only. Live evidence P06: `resp=None; rc=1; stderr-tail … 'RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string'`. Same impact class as round 1's F-078-1 (hostile input → process death → unanswered request), at the parse arm instead of the spawn arm. **Pre-existing, NOT introduced by the repair** — verified against the pre-repair tree `1506df3`'s mcp.py (identical parse arm): same crash (`response: None; rc: 1; RecursionError: True`); it was outside round 1's spawn-arm sweep. Outside the letter's explicit claims (the letter's "-32700 … never a crash" is tied to malformed JSON; deep VALID JSON is unclaimed), hence P2 routed, not a letter breach. Repair shape: catch `RecursionError` alongside `ValueError` at the parse arm (the same one-line convention the spawn arm now follows), with a pin in the MCPW registry.
- **F2-078-2 (P3, open, routed, product-side — the substrate's, not the wrapper's).** The retrieval core itself dies with an UNTYPED `OSError: [Errno 7] Argument list too long: 'psql'` traceback when a read argument pushes the SQL past the psql `-c` argv limit: direct `query.py get-journal --id <131000 U's>` → rc 1, empty stdout, traceback (no `ARV-` code anywhere), because `pg.py`'s `_run_psql` catches only `FileNotFoundError`/`TimeoutExpired`, not `OSError` — violating the substrate's own "every failure class is a NAMED code" law. Boundary measured live: 130000 chars answers the typed `ARV-QRY-002`, 131000 tracebacks. **At the wrapper boundary this is only an isError answer** (sweep form #105: the child's traceback surfaced verbatim, `isError: true`, the wrapper never crashed, no audit row) — the wrapper's own claims (byte-preserving, nonzero-exit→isError) hold. Pre-existing, untouched by this slice's diff; routed to the retrieval-core/adapter owner.
- **Carried round-1 P3s — verified carrying honestly, no fixes expected:** **F-078-2** (P12: a tools/call BEFORE any initialize is SERVED — the letter claims no pre-init rejection), **F-078-3** (P11: `"id": null` answered with `"id": null` — faithful JSON-RPC echo), **F-078-4** (P13/P13b: invalid UTF-8 on stdin SURVIVES the rig's default locale — the raw byte echoed back in the id, server alive, exit 0; a strict `PYTHONIOENCODING=utf-8:strict` override kills the process on the invalid byte — the disclosed environment caveat, out of letter).

---

## §2 The live verification

### The repair closure (the headline), on my own rig (P01–P07)

P01 [PASS] — the rig: scratch DB + migrate + fixture (A+B sources, note, journal block, two minted credentials) all rc 0.

**P02 [PASS] — repair (a), the NUL-bearing scalar string argument:**
```
(a) NUL term resp: {"jsonrpc": "2.0", "id": 80, "error": {"code": -32603, "message": "ARV-MCP-003: the argument value cannot be carried to the read (the OS exec layer refused it: ValueError) — a hostile or oversized value is refused typed,...
```
`tools/call search` with terms `["sesquine\u0000<sev78r2 marker>"]` → the `-32603` error naming ARV-MCP-003, `ValueError` (the type name) in the message, NO `result` key, the marker and the `sesquine` fragment absent from the response — not a dead process.

**P03 [PASS] — repair (b), the 200k-character id:**
```
(b) 200k id resp:  {"jsonrpc": "2.0", "id": 81, "error": {"code": -32603, "message": "ARV-MCP-003: the argument value cannot be carried to the read (the OS exec layer refused it: OSError) — a hostile or oversized value is refused typed, ne...
```
`tools/call get-journal` with a 200000-char id → the same form, `OSError` named, the full 200k string AND its unique `sev78r2big` marker absent from the response.

**P04 [PASS] — repair (c), the server survives BOTH:**
```
(c) ping resp: {"jsonrpc": "2.0", "id": 82, "result": {}}; stdin-close rc=0; dead=False
```
After both hostile calls the SAME session answers ping and exits 0 on the stdin close.

**P05 [PASS] — the OS-hostile sweep (21 forms, one shared server session, all answered, never a crash):**
```
    #101 get-journal (control chars \x01\x02\x1f\x7f)  -> product-typed ARV-QRY-002
    #102 search (newline/CR/VT term)                   -> served
    #103 search (100k-char term)                       -> served
    #104 get-journal (2MB id)                          -> ARV-MCP-003/-32603
    #105 get-journal (131000-char id)                  -> isError-UNtyped (child traceback)
    #106 get-journal (131070-char id)                  -> ARV-MCP-003/-32603
    #107 get-journal ("𝕏🔥"×30000, 240KB UTF-8)       -> ARV-MCP-003/-32603
    #108 get-journal (200k id + NUL)                   -> ARV-MCP-003/-32603
    #109 get-position (source with NUL)                -> ARV-MCP-003/-32603
    #110 resolve-reference (ref with NUL)              -> ARV-MCP-003/-32603
    #111 tool NAME with NUL                            -> rpc-error -32602 (ARV-MCP-001, no spawn)
    #112 undeclared key with NUL value                 -> rpc-error -32602 (ARV-MCP-002, no spawn)
    #113 200001-digit JSON number id                   -> rpc-error -32700 (the interpreter's own int-string guard)
    #1132 4001-digit int id (scalar-coerced)           -> product-typed ARV-QRY-002
    #114 search with an int term (42)                  -> served
    #115 search, 2000 terms                            -> served
    #116 depth-300 nested value under "id"             -> rpc-error -32602 (ARV-MCP-002)
    #117 depth-300 nested under an undeclared key      -> rpc-error -32602 (ARV-MCP-002)
    #118 arguments: null                               -> rpc-error -32602 (ARV-MCP-002)
    #119 100k-char tool NAME                           -> rpc-error -32602 (ARV-MCP-001, no echo)
    #120 search, 4000×700-char terms (2.8MB argv)      -> ARV-MCP-003/-32603
    2MB-value no-echo: True; final ping id=122; rc=0
```
Every form answered (adapter-typed, protocol-typed, or served/product-typed) — except #105, which is answered as an isError carrying the child's untyped traceback (the product-side F2-078-2; the wrapper itself never crashed, no data escaped, no hang). The per-argv-entry boundary behaves exactly as designed: 131000 chars carries to the child, 131070 is refused ARV-MCP-003 at the adapter.

**P06 [FAIL — the F2-078-1 evidence] — the deep-JSON-line probe:**
```
  json.loads depth-5000 self-check: parsed
  json.loads depth-9000 self-check: parsed
  json.loads depth-10000 self-check: RecursionError (ValueError? False)
  json.loads depth-20000 self-check: RecursionError (ValueError? False)
  deep line (depth 20000): resp=None; rc=1; stderr-tail: ...'RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string\n'
```
**P06b [PASS] — the contrast:** a depth-5000 line (under the cliff) parses and is answered `-32600` (`{"jsonrpc": "2.0", "id": null, "error": {"code": -32600, "message": "Invalid Request: an MCP message is a JSON object (MCP has no batching)"}}`), rc=0 — the crash is specific to the deep class. Cross-check at the pre-repair tree `1506df3` (identical parse arm): `response: None; rc: 1; RecursionError: True` — the crash PRE-EXISTS the repair (not introduced by it).

**P07 [PASS] — the refusal is the ADAPTER's typed answer, not a product refusal:** the ARV-MCP-003 response is a JSON-RPC `error` object (code -32603, no `result`, no `isError`, no `ARV-AGT-*`/`ARV-QRY-*` code anywhere in it); contrast the well-formed absent id, which answers the product's own isError form carrying `FAIL ARV-QRY-001: no such journal block in the caller's scope…`. The two layers are distinct and not confusable.

### The invariant re-checks around the touched code (P08–P11)

**P08 [PASS] — byte-equality + the audit law + scope:**
```
  byte-equality: list-library=True get-journal=True search=True
  audit rows cidA: baselines->7, +3 wrapper reads->10, after ARV-MCP-003 refused spawn->10, after product-refused read->10
  B scope: byte-equal=True; A's sid invisible=True; B's sid visible=True; audit delta=1
```
Three served reads through `tools/call` byte-equal to the direct `--agent-token` CLI reads; +1 audit row per served read; **the ARV-MCP-003 refused spawn lands ZERO audit rows** (no read was served); the product-refused read also zero; B's credential through the wrapper reads B's scope byte-equal with A's source id invisible.

**P09 [PASS] — the identity matrix on query.py (8 forms):**
```
  --owner only                     rc=0 code=served token-echoed=False
  --agent-token only (argv)        rc=0 code=served token-echoed=False
  ARIVO_AGENT_TOKEN only (env)     rc=0 code=served token-echoed=False
  --owner + --agent-token          rc=1 code=ARV-AGT-002 token-echoed=False
  --owner + env token              rc=1 code=ARV-AGT-002 token-echoed=False
  --agent-token + env token        rc=1 code=ARV-AGT-002 token-echoed=False
  no identity                      rc=1 code=ARV-AGT-002 token-echoed=False
  all three                        rc=1 code=ARV-AGT-002 token-echoed=False
  the three single-identity forms byte-equal: True
```
Exactly one of the three channels serves (all byte-equal); argv+env tokens together refuse ARV-AGT-002; the missing-identity refusal names the env channel; the token never echoed.

**P10 [PASS] — the read-only registry:** `tools/list membership == the 22 read arms: True (22 tools)`; `record_session`, `import_source`, and `../etc/passwd` all refuse ARV-MCP-001 in the -32602 form with no echo of the requested name; server alive; clean exit 0.

**P11 [PASS] — the protocol hygiene:** `-32601: -32601 | -32700 id: None | -32600: -32600`; a blank line is no message; an unknown notification NEVER answered (the next response is the string-id ping's echo, `string-id-1`); clean exit 0. Honest observations carried: `"id": null` answered with `"id": null` (F-078-3), and a 200k-char method name answered -32601 with the method echoed (the client's own non-secret input reflected; no letter claim violated, no crash, bounded by the input's own size).

**P12/P13/P13b [OBSERVE] — the carried P3s:** F-078-2 (`pre-init tools/call: served=True (isError=False); rc=0`), F-078-4 default locale (`raw \xff\xfe id line: echoed-back=True; next ping id=190; rc=0`), F2-078-4 strict (`resp=None; rc=1; stderr names UnicodeDecodeError=True`).

**P17 [OBSERVE] — the F2-078-2 evidence (product-side):**
```
  direct query.py get-journal --id <131000 U's>: rc=1; stdout-empty=True; E2BIG-psql-traceback=True
  stderr tail: ...'OSError: [Errno 7] Argument list too long: \'psql\'\n'
```

### The suites (P14–P16)

**P14 [PASS]** — the full MCPW suite at head `bd5d719`: `rc=0; PASS lines=9/9; tail: GREEN — the P4-E MCP-wrapper suite (MCPW-01..09) passes` (including the round-1 pin MCPW-09).

**P15 [PASS]** — the pin's RED reproduced from the archived pre-repair tree `1506df3` (worktree `/tmp/sev78r2red`): `PASS MCPW-01 … PASS MCPW-08`, `FAIL MCPW-09`, `rc=1; MCPW-01..08 PASS=8/8; MCPW-09 FAIL=True` — the disclosed RED (red-02.txt); worktree removed afterwards.

**P16 [PASS]** — the sibling regression suite at head: `test_agent_access.py` `rc=0; PASS lines=9/9; GREEN — the P4-E agent-access suite (AGT-01..09) passes`.

---

## §3 Static verification

1. **Head/chain:** `git rev-parse HEAD` = `bd5d71999405507988c40e7137d69c4791db0db2` on `slice/claim-078-p4e-mcp-wrapper`; the nine-commit chain base→head matches the task's chain exactly (`git log 505cb336..HEAD`).
2. **The repair is exactly the except arm:** `git diff 169f9de..865ac1c -- harness/mcp.py` shows ONLY the new `except (ValueError, OSError)` arm after the timeout arm — 12 added lines, nothing else changed in the file.
3. **The no-echo property, statically:** the arm's message is fixed text plus `type(e).__name__` only (mcp.py:290–301) — the exception class name, never the value, never `str(e)`.
4. **The amendment chain (red-records.json, MCPW entry) links exactly, every sha verified:**
   - binding `e090ba2b…` → file sha `5fdc2463…` = `git show e090ba2:harness/tests/test_mcp_wrapper.py | sha256sum` ✓
   - amendment 1: prior `5fdc2463…` → new `e8d63b41…` = the file at `ec46d46` (pre-GREEN amendments) ✓
   - amendment 2: prior `e8d63b41…` → new `4d769e36…` = the file at `1506df3` (the pin) ✓
   - `current_sha256` `4d769e36…` = the file at `865ac1c` = at head `bd5d719` = the working tree ✓ (the repair commit touched only mcp.py; the test file is unchanged since the pin).
5. **The measured-set records at the repair tree:** runs 06/07/08 (`python3 harness/tests/test_mcp_wrapper.py`) each `exit_code 0` with the commit field `865ac1c6fb432c6de781f979a4d4c732e34a18ef` (the full sha of the repair; identical output_sha256 across the three); run-09 (`make verify`) `exit_code 0` at the same commit; run-05 — the disclosed RED — kept in place at the pre-repair tree `169f9de…`, `exit_code 1`; red-01.txt (the LAW-11 machinery-absent RED at e090ba2) and red-02.txt (the pin's observed RED) both present; runs 01–04 name `63143e4` (the GREEN tree).
6. **Zero repo-worktree writes:** `git status --porcelain` empty before and after the whole verification; both temp worktrees removed and pruned; no commits made.

---

## §4 The honest limits

- I did not re-run `make verify` (run-09) myself this round; I re-ran live the two suites that matter for this slice's regression surface (MCPW at head, the AGT sibling) plus the RED reproduction. The full tuple stands on the author's recorded run-09 (output_sha256 `60f433de…`, exit 0, at 865ac1c).
- The json recursion cliff is interpreter-dependent: bracketed live at (9000 parses, 10000 raises) on THIS rig's CPython 3.12.16; F2-078-1 is therefore stated as "≈10k-deep nesting on one line", demonstrated at 20000. A wrapper-level depth budget would make the pin interpreter-independent.
- The P05 sweep is a broad sample, not an exhaustive enumeration of hostile inputs. The resource-exhaustion class was NOT driven to its end: a search with ~100k terms would ride the unchanged 240s `READ_TIMEOUT` arm (answered -32603 without ARV-MCP-003) — I did not spend 240s confirming an arm that is not part of the repair; the timeout arm is unchanged by `865ac1c`. Memory-exhaustion (a 100MB line) is equally unprobed — the same exposure any line-based JSON-RPC peer has, and no letter claim covers it.
- The -32700 answer for 200k-digit JSON numbers (form #113) is the interpreter's native int-string guard (≥4300 digits), not a wrapper-authored rule — an honest accident of the stack, noted as observed.
- F2-078-2's boundary (~131000 chars) is the kernel's `MAX_ARG_STRLEN` at the psql `-c` spawn, measured on this rig; the finding is about the missing `OSError` arm in `pg.py`'s `_run_psql` (named-code law), which predates this slice and sits outside its diff.
- The strict-locale kill (F-078-4's caveat) and the surrogateescape survival are environment properties of the rig's C locale (verified: stdin/stdout `utf-8/surrogateescape`), not wrapper behavior; a different deployment locale changes that half.
- My byte-equality re-check covered list-library / get-journal / search through the wrapper (the AGT-03 arm-set covers the wider product surface and re-ran GREEN); MCPW-03's four-arm byte-equality plus audit law was additionally exercised inside P14's suite run.
