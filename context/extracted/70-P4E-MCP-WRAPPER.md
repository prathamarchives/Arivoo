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

(In flight — appended at the rounds.)

## §4 The SEV account

(In flight — appended at the rounds.)

## §5 The close

(Appended at the merge.)
