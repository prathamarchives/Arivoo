#!/usr/bin/env python3
"""harness/mcp.py — P4-E slice two: the MCP wrapper (the protocol adapter over the
same retrieval core; CLAIM-078, record 70 §2; the PLAN 4E row's completion at the
connection layer).

THE CONTRACT: "authorized agents read the owner's journal and capture context
through the same API with provenance/scope/budgets; READ-ONLY at first;
owner-scope enforced on every query; imported text untrusted; no arbitrary
database access; Q9/Q10 handled honestly." The North Star's own words:
"Specifically for AI, I can just connect an agent and it has all the context of
me" (C2) — the connection this adapter completes.

THE DESIGN (record 70 §2, the binding form):
- THE TRANSPORT: stdio — JSON-RPC 2.0, newline-delimited, UTF-8. NOTHING but
  valid MCP messages is ever written to stdout (the spec law); there is no
  other stdout writer in this file. The stdin close (the spec's client-initiated
  shutdown) ends the loop and the process exits 0.
- THE PROTOCOL SURFACE: initialize (the version negotiation + the server info +
  the tools capability) / notifications/initialized (a notification is NEVER
  answered) / ping (the empty result) / tools/list / tools/call. An unknown
  method is the JSON-RPC -32601; malformed JSON is the -32700 parse error with
  id null (never a crash); a non-object line (an array — MCP has no batching)
  is the -32600 invalid request; a blank line is no message at all.
- THE TOOL REGISTRY: EXACTLY the landed READ arms of query.py — the same API,
  zero translation (the tool names ARE the arm names, the 22 read arms). NO
  write tool, NO arbitrary-command tool: a tools/call naming anything outside
  the registry refuses ARV-MCP-001 (the -32602 form) — READ-ONLY structural.
- THE SAME RETRIEVAL CORE: every tools/call invokes harness/query.py as a
  subprocess with the arm's arguments. The wrapper is a protocol translation,
  NEVER a second retrieval path: the tool result is the CLI's stdout VERBATIM
  (byte-preserving), and a nonzero exit is isError with the CLI's typed refusal
  text (the no-oracle ARV-AGT-001, the bounds ARV-QRY-004, the no-object
  ARV-QRY-001 — the wrapper generates NO auth answers of its own).
- THE TOKEN BY ENVIRONMENT: the wrapper never reads, parses, or echoes the
  credential — ARIVO_AGENT_TOKEN (query.py's non-argv token channel, the
  argv-visible residual's named home) passes through the inherited environment
  to the child, so the child argv carries NO secret end-to-end. The identity
  law (EXACTLY ONE of --owner / --agent-token / ARIVO_AGENT_TOKEN) and the
  audit row per served read are query.py's own laws, unchanged here.
- THE ARGV-SAFETY CONVENTION (the F-074-1 class closed AT THE WRAPPER
  boundary): every option is assembled in the --opt=value equals form and the
  positional search terms ride after the -- separator — a hostile DATA value
  (a leading dash) reaches the product's own typed rules, never argparse's
  usage exit. The argument law (ARV-MCP-002, the -32602 form): an undeclared
  key, a non-scalar value, a missing required argument, or an empty terms
  array never reaches the child argv.

Q10 honestly: stdio only (the local single-user threat model — no HTTP/SSE
transport, never claimed); the environment channel narrows argv exposure and
is NOT a multi-user isolation mechanism (the boundary named in the capability
row + notverified).
"""
import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.commands import API_VERSION  # noqa: E402  # the version's ONE home (commands.py) — the wrapper reports the same value as the read surface

REPO = pathlib.Path(__file__).resolve().parents[1]
QUERY = str(pathlib.Path(__file__).resolve().parent / "query.py")

# The protocol version this adapter speaks — the ONLY version it claims (the
# honest negotiation: a requested version it cannot speak is answered with its
# own, never an echo; the spec's rule).
SUPPORTED_VERSIONS = ("2025-06-18",)
LATEST_VERSION = SUPPORTED_VERSIONS[-1]

READ_TIMEOUT = 240  # the child runs psql per read; the generous bound


# --------------------------------------------------------------- the tool registry

def _id_prop() -> dict:
    return {"type": "string",
            "description": "the target id (the family's ack result_ref form)"}


def _limit_prop() -> dict:
    return {"type": "string",
            "description": "the page size (bounds 1..1000, default 100) — the "
                           "shared budget law; an out-of-bounds form is the typed "
                           "ARV-QRY-004 refusal"}


def _after_prop() -> dict:
    return {"type": "string",
            "description": "the keyset cursor — the next page starts strictly "
                           "after this listed id"}


def _tool(name: str, description: str, props: dict, required: list) -> None:
    TOOLS.append({"name": name, "description": description,
                  "inputSchema": {"type": "object", "properties": props,
                                  "required": required}})


TOOLS: list = []

# the id-bearing read arms (one target each)
for _arm, _desc in (
    ("get-capture", "one capture's current versioned row (the checkpoint's read half)"),
    ("get-source", "one imported source's row (the import ack's result_ref read back)"),
    ("get-history", "one capture's governed history — every revision in order"),
    ("get-bookmark", "one bookmark's current versioned row"),
    ("get-bookmark-history", "one bookmark's governed history — every revision in order"),
    ("get-note", "one note's current versioned row with its @-reference array"),
    ("get-note-history", "one note's governed history — every revision in order"),
    ("get-journal", "one journal block's current revision — the lossless round-trip's read half"),
    ("get-journal-history", "one journal block's governed history — every revision in order"),
    ("resolve-anchor", "one anchor's typed resolution (resolved | unresolved | ambiguous)"),
):
    _tool(_arm, _desc, {"id": _id_prop()}, ["id"])

# the list arms (the bounded page + the keyset cursor)
for _arm, _desc in (
    ("list-captures", "the owner's captures as a bounded, paginated id list"),
    ("list-bookmarks", "the owner's bookmarks as a bounded, paginated list"),
    ("list-notes", "the owner's notes as a bounded, paginated list"),
    ("list-library", "the owner's imported sources — the library membership — as a bounded, paginated list"),
    ("get-reading-state", "the derived current-reading view: every source with its last-saved position, or the honest no_position_saved state"),
    ("list-session-events", "the owner's session/dwell event stream (the closed vocabulary), bounded + paginated"),
    ("list-journal", "the owner's journal blocks as a bounded, paginated list"),
    ("list-lists", "the owner's reading lists with their derived member counts, bounded + paginated"),
):
    _tool(_arm, _desc, {"limit": _limit_prop(), "after": _after_prop()}, [])

# get-list: the member page rides the same list contract
_tool("get-list",
      "one reading list's current membership — the derived view over the "
      "append-only membership events, bounded + paginated",
      {"id": _id_prop(), "limit": _limit_prop(), "after": _after_prop()}, ["id"])

# get-position: the last-saved reading position for one source
_tool("get-position",
      "one source's last-saved reading position (the reopen's answer; the "
      "honest no_position_saved state when none is saved)",
      {"source": {"type": "string",
                  "description": "the source id (the import ack's result_ref)"}},
      ["source"])

# resolve-reference: the stable @-reference resolution (P4-D)
_tool("resolve-reference",
      "one @-reference's typed six-state answer "
      "(current/historical/tombstoned/unavailable/ambiguous/purged) over the "
      "seven landed families — work/source/anchor bare; the others optionally "
      "pinned @rev (the pinned form serves exactly as pinned)",
      {"ref": {"type": "string",
               "description": "the reference to resolve: KIND:ID[@REV]"}},
      ["ref"])

# search: the keyword terms (AND semantics)
_tool("search",
      "the keyword search over the owner's indexed content — case-folded "
      "whole-token terms, the multi-term AND intersection",
      {"terms": {"type": "array", "items": {"type": "string"},
                 "description": "the keyword terms (AND semantics — every "
                                "term must hit the document)"}},
      ["terms"])

REGISTRY = {t["name"]: t for t in TOOLS}
assert len(REGISTRY) == 22, "the closed membership: the 22 landed read arms"


# --------------------------------------------------------------- the argument law

class Refusal(Exception):
    """The typed wrapper-level refusal (ARV-MCP-001/002) — rendered as the
    JSON-RPC -32602 form, never a crash, never an echo of a secret-bearing
    input (the class is named; the value is not)."""


def _scalar(value, key: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise Refusal(f"ARV-MCP-002: the argument '{key}' must be a string "
                      "(or an integer, coerced) — a non-scalar value never "
                      "reaches the child argv")
    return str(value)


def _assemble(name: str, arguments: object) -> list:
    """The child argv tail for one tools/call — the argv-safety convention:
    every option in the --opt=value equals form, the positional search terms
    after the -- separator (a hostile leading-dash DATA value reaches the
    product's own typed rules, never argparse's usage exit)."""
    if not isinstance(arguments, dict):
        raise Refusal("ARV-MCP-002: the arguments must be an object (the "
                      "tool's inputSchema is the contract)")
    schema = REGISTRY[name]["inputSchema"]
    props = schema["properties"]
    for k in arguments:
        if k not in props:
            raise Refusal("ARV-MCP-002: an undeclared argument (the tool's "
                          "inputSchema names the accepted arguments — an "
                          "unknown key never reaches the child argv)")
    for k in schema["required"]:
        if k not in arguments:
            raise Refusal(f"ARV-MCP-002: the required argument '{k}' is "
                          f"missing (the inputSchema is the contract)")
    argv: list = []
    for k in ("id", "source", "ref", "limit", "after"):
        if k in arguments:
            argv.append(f"--{k}={_scalar(arguments[k], k)}")
    if name == "search":
        terms = arguments["terms"]
        if not isinstance(terms, list) or not terms:
            raise Refusal("ARV-MCP-002: the terms must be a non-empty array "
                          "of strings (an empty search never reaches the "
                          "child argv)")
        for t in terms:
            if isinstance(t, bool) or not isinstance(t, (str, int)):
                raise Refusal("ARV-MCP-002: every term must be a string (a "
                              "non-scalar term never reaches the child argv)")
        argv.append("--")  # the separator: the terms are DATA, never flags
        argv.extend(str(t) for t in terms)
    return argv


# --------------------------------------------------------------- the JSON-RPC layer

def _out(msg: dict) -> None:
    """The ONE stdout writer — a valid MCP message per line, always flushed
    (nothing else in this file ever writes to stdout)."""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _resp(msg_id, result: dict) -> None:
    _out({"jsonrpc": "2.0", "id": msg_id, "result": result})


def _err(msg_id, code: int, message: str) -> None:
    _out({"jsonrpc": "2.0", "id": msg_id,
          "error": {"code": code, "message": message}})


def _initialize(msg_id, params: dict) -> None:
    requested = params.get("protocolVersion")
    version = requested if requested in SUPPORTED_VERSIONS else LATEST_VERSION
    _resp(msg_id, {
        "protocolVersion": version,
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "arivo",
                       "title": "Arivo — the owner's reading and reflection context",
                       "version": str(API_VERSION)},
        "instructions": "READ-ONLY scoped agent access to the owner's Arivo "
                        "context. Every read is credential-scoped (the "
                        "ARIVO_AGENT_TOKEN environment names the credential; "
                        "the owner scope binds from it, never from a claim) "
                        "and audited; the page bounds are the read budget.",
    })


def _tools_list(msg_id) -> None:
    _resp(msg_id, {"tools": TOOLS})


def _tools_call(msg_id, params: dict) -> None:
    name = params.get("name")
    if not isinstance(name, str) or name not in REGISTRY:
        # ARV-MCP-001 — the read-only registry refusal. The class is named,
        # never the requested name echoed (a hostile name is DATA; the
        # registry's closed membership is public through tools/list).
        _err(msg_id, -32602,
             "ARV-MCP-001: unknown tool — the registry is EXACTLY the landed "
             "READ arms (READ-ONLY structural: no write tool, no arbitrary "
             "command, never a passthrough); call tools/list for the closed "
             "membership")
        return
    try:
        argv = _assemble(name, params.get("arguments"))
    except Refusal as r:
        _err(msg_id, -32602, str(r))
        return
    # THE SAME RETRIEVAL CORE: the child is query.py with the arm's arguments.
    # The credential (when present) travels by the inherited environment —
    # the child argv carries NO secret (ARIVO_AGENT_TOKEN is query.py's own
    # non-argv channel; this wrapper never reads, parses, or echoes it).
    try:
        r = subprocess.run([sys.executable, QUERY, name, *argv],
                           capture_output=True, text=True, timeout=READ_TIMEOUT,
                           cwd=str(REPO))
    except subprocess.TimeoutExpired:
        _err(msg_id, -32603,
             "the read did not complete within the adapter's bound "
             f"({READ_TIMEOUT}s) — no result is claimed")
        return
    # byte-preserving: the CLI's stdout VERBATIM; the stderr surfaces only
    # when stdout is empty (nothing is silently swallowed, never a rewrite)
    text = r.stdout if r.stdout.strip() else r.stderr
    _resp(msg_id, {"content": [{"type": "text", "text": text}],
                   "isError": r.returncode != 0})


def _dispatch(msg_id, method: str, params: dict) -> None:
    if method == "initialize":
        _initialize(msg_id, params)
    elif method == "ping":
        _resp(msg_id, {})
    elif method == "tools/list":
        _tools_list(msg_id)
    elif method == "tools/call":
        _tools_call(msg_id, params)
    else:
        _err(msg_id, -32601, f"Method not found: {method} (the adapter's "
                             "surface is initialize/ping/tools/list/tools/call)")


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue  # a blank line is no message — never a response
        try:
            msg = json.loads(line)
        except ValueError:
            _err(None, -32700, "Parse error: the line is not valid JSON")
            continue
        if not isinstance(msg, dict):
            _err(None, -32600, "Invalid Request: an MCP message is a JSON "
                               "object (MCP has no batching)")
            continue
        method = msg.get("method")
        if not isinstance(method, str):
            if "id" in msg:
                _err(msg["id"], -32600, "Invalid Request: the method is "
                                        "missing or not a string")
            continue
        if "id" not in msg:
            continue  # a notification is NEVER answered — even an unknown one
        params = msg.get("params")
        if not isinstance(params, dict):
            params = {}
        _dispatch(msg["id"], method, params)
    return 0  # the stdin close: the clean exit (the spec's shutdown form)


if __name__ == "__main__":
    sys.exit(main())
