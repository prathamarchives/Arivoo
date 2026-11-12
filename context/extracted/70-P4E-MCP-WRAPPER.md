# Record 70 — P4-E slice two: the MCP wrapper over the same retrieval core (the agent's connection layer)

> STATUS: SESSION ENGINEERING RECORD (2026-11-12; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 94. PR #112 MERGED (the P4-E slice one scoped agent read
> surface, under INT-145); record 69 §5 closed at this commit (the post-#112 reconciliation).

Session 41 (2026-11-12), CLAIM-078, opened at the merged head `505cb336` (the PR #112 merge —
P4-E slice one). Record 69 carries the scoped-agent-read slice's account (complete, §5 closed
at this commit); this record carries the MCP-wrapper slice's contract + chain — P4-E's
completion at the connection layer.

## §1 The #112 merge close (CLAIM-077 LANDED — P4-E slice one)

The full merge account: record 69 §5 (closed at this commit) + CLAIM-077's rule-4 close row.
The short form: PR #112 = merge `505cb336` (2026-11-11T17:17:39Z, under INT-145); the five
checks green at the final head `169cbd42` AND on the merge commit; the merge-gate review
D-042 (1a) `5862653355`; the two-round SEV chain (round 1 agent-e2095ac5 PASS with four
in-slice repairs at `20cd5c5`; round 2 agent-6a8d56b7 PASS with F2-077-5 repaired at the head
`88d1e829`); the scanner-collision repair (the standing lesson) with the digest re-bound LAST
(`13023b93`); the branch deleted; 0 open PRs; only main.

**THE P4-E REMAINING-INCREMENT CHECK (at the #112 merge):** slice one complete (the
credential + the read mode + the audit + the refusals); the ONE named remaining increment
from record 69 §2's exclusions: the MCP wrapper — "the same retrieval core behind the
protocol adapter". CLAIM-078 (this slice) takes it; then P4-F → the Phase 4 exit gate.

## §2 The MCP-wrapper slice's contract (the PLAN 4E row's completion at the connection layer)

**The letter (the PLAN 4E row):** "authorized agents read the owner's journal and capture
context through the same API with provenance/scope/budgets; READ-ONLY at first; owner-scope
enforced on every query; imported text untrusted; no arbitrary database access; Q9/Q10
handled honestly." The North Star's own words: "Specifically for AI, I can just connect an
agent and it has all the context of me" (C2 — the connection this slice completes). Record 69
§2's named exclusion landing: "no MCP wrapper (P4-E slice two — the same retrieval core
behind the protocol adapter)".

**The design boundary:**
- **harness/mcp.py — the MCP server (the protocol adapter):** the stdio transport (JSON-RPC
  2.0, newline-delimited messages); the protocol surface: `initialize` (the version
  negotiation + the server info + the tools capability), `notifications/initialized` (a
  notification NEVER answered), `ping`, `tools/list`, `tools/call`; the tool registry =
  EXACTLY the landed READ arms (the same API, zero translation — the tool names ARE the arm
  names: get-capture/get-source/get-history, get-bookmark/get-bookmark-history,
  get-note/get-note-history, get-journal/get-journal-history, list-captures/list-bookmarks/
  list-notes/list-library, get-reading-state, list-session-events, list-journal, list-lists,
  get-list, get-position, resolve-anchor, resolve-reference, search — the 22 read arms);
  every `tools/call` invokes query.py as a subprocess with the arm's arguments (the SAME
  retrieval core — the wrapper is a protocol translation, never a second retrieval path);
  the tool result = the CLI's stdout VERBATIM as the text content (byte-preserving — the
  adapter never rewrites the payload); a nonzero CLI exit = isError with the CLI's typed
  refusal text (the product's own refusals surfaced as the tool errors: the no-oracle
  ARV-AGT-001, the bounds ARV-QRY-004 — the wrapper generates NO auth answers of its own;
  the only wrapper-level refusals are the protocol-level ones).
- **The token by environment — `ARIVO_AGENT_TOKEN`:** the server's subprocess argv carries
  NO secret end-to-end — the token travels by environment from the server's own environment
  through to query.py (the argv-visible-token residual's named home, record 69 §2 + the
  notverified entry).
- **query.py's env form:** `ARIVO_AGENT_TOKEN` read as an alternative token channel (the
  `--agent-token` argv form unchanged for humans); the identity law extended: EXACTLY ONE
  of `--owner` / `--agent-token` / `ARIVO_AGENT_TOKEN` (two together = the typed ARV-AGT-002
  ambiguous refusal; none = the missing-identity refusal; the token from either channel
  verified through the same lookup, the same audit row, the same refusals).
- **The argv-safety convention at the wrapper boundary:** the wrapper assembles the child
  argv defensively (the `--opt=value` equals form for every option, the `--` separator
  before the positional search terms) — a hostile DATA value (a leading dash) reaches the
  product's own typed rules, never argparse's usage exit (the F-074-1 class closed AT THE
  WRAPPER boundary; the CLI's own direct argv exposure remains the routed family class).
- **The budgets:** the tool arguments carry the page parameters (limit/after where the arm
  accepts them) — the shared `_page_args` bounds ARE the read budget, unchanged; no new
  budget machinery (Phase 5's retrieval increments, never claimed here).
- **The audit:** every served read through the wrapper lands the SAME audit row (the arm +
  the bounded request facts, never the content) — the wrapper adds NO second audit path and
  NO bypass (the only path to the data is query.py's; a wrapper-served read unauditable is
  impossible by construction).
- **Q10 handled honestly:** the stdio-only transport (the local single-user threat model —
  no HTTP/SSE exposure, never claimed); the token in the environment is visible to the same
  user's processes (the env form narrows argv exposure; it is NOT a multi-user isolation
  mechanism — the boundary named in the capability row + notverified).

**The laws carried:** the same-API law (byte-equality against the direct CLI — the wrapper
adds translation, never a second path); the no-secret-in-argv law (end-to-end); the
read-only structural (the registry is the read arms; a hostile `tools/call` naming anything
else refuses typed ARV-MCP-001, never a passthrough); the no-oracle (ARV-AGT-001 surfaced
identically through the wrapper; the token never echoed in any response); the
byte-preserving payload law; the append-only audit (the same row, the same table); the
hostile-string law (the tool arguments are DATA — the argv-safety convention).

**THE BOUNDED EXCLUSIONS:** no write scopes (READ-ONLY per the 4E row's own letter); no MCP
resources/prompts surfaces (tools only — the read arms; the other surfaces a future increment
if the owner wants them); no HTTP/SSE transports (stdio only); no token rotation/expiry
windows (unchanged from slice one); no new migration (the 0019 substrate serves unchanged —
the wrapper is an adapter over the landed surface, never a schema change); no reader-client
work (P4-B's repo); no Phase 5 retrieval machinery (the deeper response budgets).

**Cases (the MCPW registry; each pin's full statement lives at its check()):**
  MCPW-01 the handshake: initialize → the server info + the protocol version + the tools
          capability; notifications/initialized answered with NOTHING; ping → the empty
          result
  MCPW-02 the token by environment: without ARIVO_AGENT_TOKEN the read call fails with the
          typed identity refusal surfaced as the tool error (never a traceback, never a
          crash); with a minted credential's token the read serves
  MCPW-03 the same-API law + the audit: tools/call byte-equal to the direct --agent-token
          CLI read (the library + the journal + the notes + the references); the audit row
          per served read; the tool result text byte-preserving
  MCPW-04 the read-only registry: tools/list = EXACTLY the read arms (no write tool); a
          hostile tools/call naming a write command refuses typed ARV-MCP-001, never a
          passthrough
  MCPW-05 the no-oracle through the wrapper: unknown/revoked tokens → the SAME ARV-AGT-001
          tool error; the token never echoed in any response (list, call, or error)
  MCPW-06 the budgets + the argv-safety: the page params through the tool arguments (the
          same ARV-QRY-004 bounds refusal as the direct read); a leading-dash DATA value
          reaches the product's typed rules, never argparse's usage exit
  MCPW-07 the scope isolation: B's credential through the wrapper reads B's scope (A's
          content invisible; byte-equal to B's direct reads)
  MCPW-08 the protocol hygiene: unknown method → -32601; malformed JSON → -32700 (the parse
          error, never a crash); the responses carry the request id; the server exits
          cleanly on EOF

(The machinery-absent probe — the module-level ARV-TEST-000 at the pre-GREEN tree, DB-free —
precedes the registry per the AGT form.)

## §3 The executed chain

commit A (`96aeda4`: docs — the post-#112 reconciliation + THE P4-E REMAINING-INCREMENT
CHECK + CLAIM-077's rule-4 close row + CLAIM-078 registered + record 70 minted; the branch
pushed EARLY per the standing owner instruction) → **the RED** (`e090ba2`: the MCPW-01..08
suite authored tests-only per LAW-11 — 540 lines; the DB-free machinery-absent probe at the
module head; red-01.txt exit 1 ARV-TEST-000) → the typed red-record binding (`db0ead9`:
red-records.json + the gate.py TESTS registration — the ARV-RED-008 class, diff-visible —
+ the run dir opened with red-01.txt + scope.txt) → **the pre-GREEN amendments**
(`ec46d46`: the three disclosed pin-authoring repairs — MCPW-03's audit-count
baselines-first form (every direct --agent-token baseline read lands its own audit row);
MCPW-06's leading-dash ID pin corrected to the OBSERVED typed refusal (the UUID-keyed
arm's ARV-QRY-002 for a malformed id — the argv-safety claim itself unchanged); MCPW-07's
id-set form (list-library emits BARE ids, never titles — the AGT-06 lesson repeated and
caught) + B's audit count 2) → **the GREEN** (`63143e4`: harness/mcp.py — the MCP server —
+ query.py's ARIVO_AGENT_TOKEN env form (the identity law extended to exactly one of the
three channels) + capability.py's scoped-agent-access row completed) → the measured set at
the GREEN tree (`169f9de`: runs 01-04 — the MCPW suite x3 + make verify 54/0) → **the SEV
round-1 repair pin** (`1506df3`: MCPW-09 added — the spawn-refusal regression — with its
own RED observed and kept as red-02.txt + run-05) → **the SEV round-1 repair** (`865ac1c`:
the spawn arm's (ValueError, OSError) catch — the typed ARV-MCP-003 refusal in the -32603
form) → the measured set at the repair tree (`bd5d719`: runs 06-09) → **the SEV round-2
repair pin** (`7c4ec1e`: MCPW-10 added — the parse-refusal regression — with its own RED
observed and kept as red-03.txt + run-10) → **the SEV round-2 repair** (`511dc0a`: the
parse arm's (ValueError, RecursionError) catch — the deep-nesting class joins the
malformed-JSON class as the -32700 answer) → the measured set at the round-2-repair tree
(`26904b5`: runs 11-14 — the MCPW suite x3 (MCPW-01..10) + make verify 54/0) → the
artifact finalize (this commit — the content head) → the artifact re-bind (sev.json binding
the two-round SEV chain + notverified + the two round reports + the proof sheet + the
recorded PR-mode gate + the local trusted-gate reproduction) → the push → the PR → the
five checks → the merge-gate review (D-042 (1a)) → **the merge under INT-145** → the
post-merge verification → **THE P4-E EXIT CHECK** → P4-F (the recovery + contract gate) →
the Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).

## §4 The SEV account (the two-round chain)

**Round 1 (agent-1adef410, PASS zero open P0/P1 — 57 probes: 52 PASS + 5 OBSERVE).**
Every claimed behavior reproduced live on the reviewer's own scratch rig: the transport
(a long adversarial session — 16/16 stdout lines valid JSON, stderr empty, the clean
exit; the invalid-UTF-8 line answered -32700 and the session continuing under the rig's
default locale); the protocol surface (the version negotiation incl. the missing/hostile
versions; the notification silence; the string-id echo incl. unicode; -32601/-32700/
-32600; a blank line no message); the registry (22 arms exact; write names, path names,
a 10k name, a NUL name, an empty name — all ARV-MCP-001 in the -32602 form, NO echo of
the requested name, the command_log delta ZERO proving no passthrough); THE SAME-CORE
LAW on SIXTEEN arms (beyond the suite's four — byte-equal wrapper-vs-direct incl.
unicode content; the typed refusals byte-equal as isError); the token by environment
(the six-form identity matrix on query.py; the token VALUE never in any response; the
env answer byte-equal to the argv answer); the audit (served reads +1 each with the arm
+ the REQUEST facts; refused reads zero; B's isolation with B's audit rows); the budgets
+ the argv-safety (the leading-dash term/id to the product's typed rules; the
malformed-uuid ARV-QRY-002; the argument law across ten hostile forms); the RED
reproduced from the archived tree e090ba2; the amendment chain linked; the scope
declaration clean through the gate's own check_scope; the siblings GREEN (AGT 9/9,
references, library — and the MCPW suite 8/8 on the reviewer's own rig); the AST static
sweep (stdlib-only imports; NO os.environ read anywhere in code — the wrapper is
credential-blind; no randomness/time (LAW-24); no sockets; no DB path — exactly ONE
subprocess.run (the query.py child) and exactly ONE stdout writer). THE FINDINGS:
F-078-1 the P2 (the NUL-bearing/over-long string argument crashing the spawn arm —
ValueError/OSError escaping the TimeoutExpired-only catch; the process dying with the
request unanswered) — REPAIRED in-slice at `865ac1c` with the MCPW-09 pin (its own RED
observed, red-02.txt); F-078-2/3/4 the P3s (the pre-initialize serving — the spec's
SHOULD NOT ordering; the id-null echo; the strict-locale environment caveat) — ROUTED,
out of letter, honestly noted in notverified.

**Round 2 (agent-99b5afc0, PASS — 19 probes + a 21-form OS-hostile sweep).** F-078-1
VERIFIED CLOSED live: both hostile forms answered -32603/ARV-MCP-003 (the exception
TYPE only in the message, never the value); the SAME session answering the next ping
and exiting 0 on the stdin close; the 21-form sweep all answered (control characters,
a 2MB id, 240KB of unicode, NUL in every declared key, 2000 search terms, a 2.8MB argv
— never a crash). The invariants re-verified: byte-equality; the audit law (the
refused-spawn ZERO rows); the identity matrix (8 forms — all three single-identity
forms byte-equal); the registry; the hygiene; the pin's RED reproduced from the
archived pre-repair tree 1506df3; the amendment chain 3-linked (every sha verified
against git); the measured-set records verified (runs 06-09 at 865ac1c exit 0; run-05
the RED kept in place); the AGT sibling GREEN 9/9; the repair exactly the except arm
(the diff 12 lines, nothing else). ONE NEW FINDING: F2-078-1 the P2 (a deep VALID-JSON
line — nesting beyond the interpreter's json recursion cliff — RecursionError escaping
the ValueError-only parse arm; PRE-EXISTING at the pre-repair tree, verified by the
reviewer against 1506df3, outside round 1's spawn-arm sweep) — REPAIRED in-slice at
`511dc0a` with the MCPW-10 pin (its own RED observed, red-03.txt); F2-078-2 the P3
(the retrieval core's own untyped E2BIG traceback at pg.py's _run_psql for
~131k-char arguments — PRODUCT-side, pre-existing, outside this slice's diff) — ROUTED
to the substrate owner (the same family as F-075-1/F-076-1: the untyped-traceback
class at the oversize boundary).

## §5 The close

PR #113 merged at 2026-11-12 as `d21ca44e9984b40931432fb8e33f8e639e1892e9` under INT-145's
standing authorization: the five checks green at the exact final head `fa09e6c` AND on the
merge commit `d21ca44e` (all observed live — the verify runs 43179237216 at the head, the
run 43180625779 on the merge commit); the merge-gate review D-042 (1a) `5871123952` (the
substantive host review engaging the actual diff — the same-core law, the token's
end-to-end secrecy, the read-only registry, both repaired crash classes with their
observed REDs, the audit + the budgets, the identity-law extension, the process evidence);
CodeRabbit the skip state (fewer than 10 stars — noted per D-042 (1c), the host review
the floor); zero review threads; the flip/merge/restore with the protections re-read
byte-equivalent (approving=1, dismiss_stale=true, strict=true, the five contexts,
enforce_admins, no force pushes, no deletions); the branch deleted; 0 open PRs; only
main. No ARV-SEV-003 round — the digest bound LAST (`42fcff79` at the final content head
`9f526e6`, re-bound twice as the size repair and the scanner-collision repair moved the
head — the anti-lag ordering held each time; validate_report GREEN re-verified) + the
local trusted-gate reproduction green before the push (run-23, exit 0, FIRST attempt —
the anchored BASE driver at the trusted base reset to the current main `505cb336`). THE
TWO-ROUND SEV CHAIN (the account in §4): round 1 (agent-1adef410) PASS zero open P0/P1 —
57 probes, F-078-1 the P2 repaired at `865ac1c` with the MCPW-09 pin; round 2
(agent-99b5afc0) PASS — the repair verified CLOSED live + F2-078-1 the P2 repaired at
`511dc0a` with the MCPW-10 pin; the P3s routed (F-078-2/3/4 + F2-078-2 product-side).
The in-slice catches: the ARV-SIZE-002 repair (407→388 — the docstring condensed to the
summary + pointer form, the one-fact-one-home repair) + the scanner-collision class
caught LOCALLY by the whole-diff scan BEFORE the push (the fixture kwarg renamed). The
23-record proof sheet (PRF-004 byte-identical; runs 01-21 the measured sets across the
five trees incl. the three DISCLOSED RED runs 05/10 kept + run-22 the PR-mode gate GREEN
+ run-23 the trusted-gate reproduction exit 0).

**THE P4-E EXIT CHECK (2026-11-12, at the #113 merge):** every required P4-E backend
behavior is landed and verified — the scoped agent read surface (CLAIM-077: the
owner-minted credential with the one-time display + the one-way revocation, the
mint/revoke commands, the `--agent-token` read mode with the credential-bound owner scope
+ the append-only audit row + the page bounds, the no-oracle invalid-token class, the
read-only structure) + the connection layer (CLAIM-078: the MCP wrapper over the same
retrieval core — the tool registry = exactly the 22 read arms, every tools/call through
query.py byte-preserving with the same audit row and budgets, the ARIVO_AGENT_TOKEN env
channel, the argv-safety convention, the typed wrapper refusals). **P4-E COMPLETE.**
Record 71 carries the recovery/contract-gate slice (P4-F's opening — the Phase 4 exit).
