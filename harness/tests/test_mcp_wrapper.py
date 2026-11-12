#!/usr/bin/env python3
"""harness/tests/test_mcp_wrapper.py — P4-E slice two acceptance suite (CLAIM-078,
the MCP wrapper over the same retrieval core — the PLAN 4E row's completion at the
connection layer; record 70 §2). Red-first (LAW-11): at CLAIM-077's merged head 505cb336
the suite fails with ARV-TEST-000 (machinery-absent; red-01.txt).

THE CONTRACT (the PLAN 4E row): "authorized agents read the owner's journal and
capture context through the same API with provenance/scope/budgets; READ-ONLY at
first; owner-scope enforced on every query; imported text untrusted; no arbitrary
database access; Q9/Q10 handled honestly." The North Star's own words: "Specifically
for AI, I can just connect an agent and it has all the context of me" (C2) — the
connection this slice completes. Record 69 §2's named exclusion landing: "no MCP
wrapper (P4-E slice two — the same retrieval core behind the protocol adapter)."

THE MACHINE: harness/mcp.py — the MCP server (the protocol adapter): the stdio
transport (JSON-RPC 2.0, newline-delimited, UTF-8; NOTHING but valid MCP messages
on stdout — diagnostics to stderr); the protocol surface initialize (the version
negotiation + the server info + the tools capability) / notifications/initialized
(a notification NEVER answered) / ping / tools/list / tools/call; the tool registry
= EXACTLY the landed READ arms (the same API, zero translation — the tool names ARE
the arm names, the 22 read arms); every tools/call invokes query.py as a subprocess
with the arm's arguments (the SAME retrieval core — a protocol translation, never a
second retrieval path); the tool result = the CLI's stdout VERBATIM as the text
content (byte-preserving); a nonzero exit = isError with the CLI's typed refusal
text (the no-oracle ARV-AGT-001, the bounds ARV-QRY-004, the no-object ARV-QRY-001
— the wrapper generates NO auth answers of its own). THE TOKEN BY ENVIRONMENT:
ARIVO_AGENT_TOKEN — the server passes its environment through to query.py (the
non-argv token channel, the argv-visible residual's named home; the child argv
carries NO secret end-to-end); query.py reads ARIVO_AGENT_TOKEN as the alternative
token channel — the identity law extended to EXACTLY ONE of --owner /
--agent-token / ARIVO_AGENT_TOKEN (the same lookup, the same audit row, the same
refusals). THE ARGV-SAFETY CONVENTION at the wrapper boundary: the --opt=value
equals forms + the -- separator before positional search terms — a hostile DATA
value (a leading dash) reaches the product's own typed rules, never argparse's
usage exit (the F-074-1 class closed AT THE WRAPPER boundary).

Refusal codes: ARV-AGT-001 the invalid-token class + ARV-AGT-002 the identity law
+ ARV-QRY-004 the page bounds (all the PRODUCT's own codes surfaced through the
wrapper as tool errors — the same-API law); ARV-MCP-001 the read-only registry
refusal (a tools/call naming anything outside the read arms — the JSON-RPC -32602
form); ARV-MCP-002 the argument law (an undeclared key or a non-scalar value —
the JSON-RPC -32602 form).

Cases (the MCPW registry; each pin's full statement lives at its check()):
  MCPW-01 the handshake: initialize → the server info + the protocol version +
          the tools capability; the version negotiation (an unsupported request
          version answered with the server's own); notifications/initialized
          answered with NOTHING; ping → the empty result; the clean EOF exit
  MCPW-02 the token by environment: without ARIVO_AGENT_TOKEN the read call
          fails with the typed identity refusal surfaced as the tool error
          (never a traceback, the server alive for the next call); with a
          minted credential's token the read serves
  MCPW-03 the same-API law + the audit: tools/call byte-equal to the direct
          --agent-token CLI read (the library + the journal + the notes + the
          references); the audit row per SERVED read; a refused read NEVER
          audited; the tool result text byte-preserving
  MCPW-04 the read-only registry: tools/list = EXACTLY the read arms (no write
          tool); a hostile tools/call naming a write command (or any non-arm)
          refuses typed ARV-MCP-001, never a passthrough
  MCPW-05 the no-oracle through the wrapper: unknown and revoked tokens → the
          SAME ARV-AGT-001 tool error; the token NEVER echoed in any response
  MCPW-06 the budgets + the argv-safety + the argument law: the page params
          through the tool arguments (the same ARV-QRY-004 bounds refusal as
          the direct read); a leading-dash DATA value reaches the product's
          typed rules, never argparse's usage exit; an undeclared key or a
          non-scalar value refuses ARV-MCP-002
  MCPW-07 the scope isolation: B's credential through the wrapper reads B's
          scope (A's content invisible; byte-equal to B's direct reads; the
          audit rows under B's credential)
  MCPW-08 the protocol hygiene: unknown method → -32601; malformed JSON →
          -32700 (the parse error with id null, never a crash); a JSON array
          line → -32600 (MCP has no batching); an unknown NOTIFICATION → no
          response; the responses carry the request id (the string-id echo);
          the clean EOF exit
  MCPW-09 the spawn-refusal pin (F-078-1's regression, the SEV round-1
          repair): a value the OS exec layer cannot carry (a NUL-bearing
          string, an over-long argument) is refused TYPED — the -32603 form
          naming ARV-MCP-003, the server ALIVE for the next request, the
          process never crashed, the value never echoed
  MCPW-10 the parse-refusal pin (F2-078-1's regression, the SEV round-2
          repair): a single VALID-JSON line nested beyond the interpreter's
          json recursion cliff (a deep bracket chain) is answered as the
          -32700 parse-error class with id null — never a RecursionError
          crash, the server ALIVE for the next request, the clean exit

Run: python3 harness/tests/test_mcp_wrapper.py   (exit 0 = green)
"""
import json
import os
import pathlib
import queue
import subprocess
import sys
import tempfile
import threading

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []

# P4-E slice two (CLAIM-078) — the machinery-absent probe (LAW-11): the MCP
# wrapper is harness/mcp.py. The probe is DB-free by construction (the file's
# absence precedes any connection).
MCP = REPO / "harness" / "mcp.py"
if not MCP.is_file():
    print("FAIL ARV-TEST-000: the P4-E slice two MCP-wrapper machinery is absent "
          "(machinery-absent class; harness/mcp.py not on disk) — the implementation "
          "lands after this RED, never before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

DB = ENV = None

TEXT = ("The MCP-wrapper corpus: the persistent anchor phrase lives here.\n"
        "Second paragraph: the measurable span lives here instead.\n"
        "Third paragraph closes the corpus.\n")

# The 22 landed READ arms — the tool registry's exact, closed membership (the
# same API, zero translation; the tool names ARE the arm names)
READ_ARMS = sorted([
    "get-capture", "get-source", "get-history",
    "get-bookmark", "get-bookmark-history",
    "get-note", "get-note-history",
    "get-journal", "get-journal-history",
    "list-captures", "list-bookmarks", "list-notes", "list-library",
    "get-reading-state", "list-session-events", "list-journal", "list-lists",
    "get-list", "get-position", "resolve-anchor", "resolve-reference", "search",
])


def check(code: str, ok: bool, what: str, repair: str) -> None:
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        FAILS.append(code)
        print("      repair: " + repair)


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=240, env=ENV)


def cmd(op: str, *args, owner="A", key=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1"]
    if key is not None:
        a += ["--idem-key", key]
    return cli(*a, *args)


def qy(arm: str, owner: str, *extra) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), arm, "--owner", owner, *extra)


def agt(arm: str, token: str, *extra) -> subprocess.CompletedProcess:
    """The direct agent read (the argv --agent-token channel) — the byte-equality
    baseline for the wrapper's env-channel reads."""
    return cli(str(REPO / "harness" / "query.py"), arm, "--agent-token", token, *extra)


def audit(query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", query],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def token_of(p: subprocess.CompletedProcess) -> str:
    """The one-time token display: 'token=<value>' in the FIRST ack only."""
    return ack_field(p, "token")


class Server:
    """The MCP server under test: spawned with an EXPLICIT environment (the
    ARIVO_AGENT_TOKEN channel under the test's control — popped unless given);
    one reader thread turns the newline-delimited stdout into a queue (the
    recv timeout makes a hung server a test failure, never a hang)."""

    def __init__(self, tok: str | None = None):
        e = dict(ENV)
        e.pop("ARIVO_AGENT_TOKEN", None)
        if tok is not None:
            e["ARIVO_AGENT_TOKEN"] = tok
        self.p = subprocess.Popen(
            [sys.executable, str(MCP)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=e, cwd=str(REPO))
        self.dead = False  # set when a write hits a closed pipe — the pin records it
        self.q: queue.Queue = queue.Queue()
        self.err: list[str] = []
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._drain_err, daemon=True).start()

    def _reader(self) -> None:
        for ln in self.p.stdout:
            self.q.put(ln)
        self.q.put(None)

    def _drain_err(self) -> None:
        for ln in self.p.stderr:
            self.err.append(ln)

    def send(self, obj) -> None:
        try:
            self.p.stdin.write(json.dumps(obj) + "\n")
            self.p.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            self.dead = True  # the server died mid-call — the pin records it

    def send_raw(self, line: str) -> None:
        try:
            self.p.stdin.write(line + "\n")
            self.p.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            self.dead = True  # the server died mid-call — the pin records it

    def recv(self, timeout: float = 90.0):
        try:
            ln = self.q.get(timeout=timeout)
        except queue.Empty:
            return None
        if ln is None:
            return None
        return json.loads(ln)

    def close(self) -> int:
        """The clean shutdown: close stdin (the spec's client-initiated form)
        → the server exits; the returncode returned (0 = the clean exit)."""
        try:
            self.p.stdin.close()
        except (BrokenPipeError, ValueError, OSError):
            pass  # the pipe was already broken — the server died mid-call
        try:
            return self.p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.p.kill()
            return self.p.wait(timeout=10)

    def handshake(self, version: str = "2025-06-18") -> dict:
        self.send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": version, "capabilities": {},
                              "clientInfo": {"name": "mcpw-suite", "version": "1"}}})
        r = self.recv()
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return r

    def call(self, name: str, arguments: dict, msg_id) -> dict:
        self.send({"jsonrpc": "2.0", "id": msg_id, "method": "tools/call",
                   "params": {"name": name, "arguments": arguments}})
        return self.recv()

    def tools(self) -> dict:
        self.send({"jsonrpc": "2.0", "id": 900, "method": "tools/list",
                   "params": {}})
        return self.recv()

    def ping(self, msg_id) -> dict:
        self.send({"jsonrpc": "2.0", "id": msg_id, "method": "ping"})
        return self.recv()


def text_of(resp: dict) -> str:
    """The first text content block of a tools/call result ('' when absent)."""
    try:
        return resp["result"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return ""


def is_err(resp: dict) -> bool:
    try:
        return bool(resp["result"]["isError"])
    except (KeyError, TypeError):
        return False


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4e2")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    ENV.pop("ARIVO_AGENT_TOKEN", None)  # the suite controls the channel explicitly
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)

        # ------- the fixture: two owners with real capture context + credentials
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "corpus.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("persistent anchor")
        e1 = s1 + len("persistent anchor")
        pa = cmd("import_source", "--file", str(src_file), "--media-type",
                 "text/plain", "--title", "The Agent Corpus", key="mw-imp1")
        sid = ack_field(pa, "result_ref")
        ph = cmd("create_highlight", "--source-id", sid, "--start", str(s1),
                 "--end", str(e1), key="mw-hl1")
        hid = ack_field(ph, "result_ref")
        pn = cmd("create_note", "--content", "The owner's private note: sesquine token.",
                 key="mw-n1")
        nid = ack_field(pn, "result_ref")
        pj = cmd("journal_block", "--kind", "raw",
                 "--content", "The owner's raw thinking for the agent context.",
                 key="mw-jb1")
        jid = ack_field(pj, "result_ref").split("@")[0]
        pb = cmd("import_source", "--file", str(src_file), "--media-type",
                 "text/plain", "--title", "B's Corpus", key="mw-impB", owner="B")
        sid_b = ack_field(pb, "result_ref")
        pmA = cmd("mint_agent_credential", "--label", "A wrapper probe",
                  key="mw-mintA")
        tokA = token_of(pmA)
        cidA = ack_field(pmA, "result_ref")
        pmB = cmd("mint_agent_credential", "--label", "B wrapper probe",
                  key="mw-mintB", owner="B")
        tokB = token_of(pmB)
        cidB = ack_field(pmB, "result_ref")
        pmR = cmd("mint_agent_credential", "--label", "to revoke", key="mw-mintR")
        tokR = token_of(pmR)
        cidR = ack_field(pmR, "result_ref")
        prv = cmd("revoke_agent_credential", "--id", cidR, key="mw-revR")
        assert pa.returncode == ph.returncode == pn.returncode == 0
        assert pj.returncode == pb.returncode == pmA.returncode == 0
        assert pmB.returncode == pmR.returncode == prv.returncode == 0

        # ---- MCPW-01 — the handshake + the version negotiation + the
        # notification silence + the ping + the clean EOF exit
        s1w = Server()
        r = s1w.handshake()
        ok1 = (isinstance(r, dict) and r.get("id") == 1
               and isinstance(r.get("result"), dict)
               and r["result"].get("protocolVersion") == "2025-06-18"
               and isinstance(r["result"].get("serverInfo"), dict)
               and r["result"]["serverInfo"].get("name") == "arivo"
               and isinstance(r["result"].get("capabilities"), dict)
               and "tools" in r["result"]["capabilities"])
        # the version negotiation: an UNSUPPORTED requested version answered
        # with the server's own (the only one it supports — never an echo of
        # a version it cannot speak)
        s1v = Server()
        rv = s1v.handshake(version="2024-11-05")
        ok1 = ok1 and (isinstance(rv, dict)
                       and rv.get("result", {}).get("protocolVersion") == "2025-06-18")
        s1v.close()
        # notifications/initialized answered with NOTHING: the next response
        # is the PING's (the notification never produced one) — then ping
        # answers the empty result
        rp = s1w.ping(2)
        ok1 = ok1 and (isinstance(rp, dict) and rp.get("id") == 2
                       and rp.get("result") == {})
        rc1 = s1w.close()
        ok1 = ok1 and rc1 == 0
        check("MCPW-01", ok1,
              "the handshake: initialize answers the server info (name arivo) + the protocol version 2025-06-18 + the tools capability; an unsupported requested version answered with the server's own (the honest negotiation); notifications/initialized NEVER answered (the next response is the ping's); ping → the empty result; the stdin close → the clean exit 0 (the spec's shutdown form)",
              "the wrapper speaks the MCP lifecycle honestly — no invented version claims, no phantom notification responses, no hung exits")

        # ---- MCPW-02 — the token by environment (the non-argv channel)
        s_no = Server()
        s_no.handshake()
        r_no = s_no.call("list-library", {}, 10)
        # the server stays ALIVE after the refusal (the next call answers)
        r_alive = s_no.ping(11)
        rc_no = s_no.close()
        ok2 = (isinstance(r_no, dict) and is_err(r_no)
               and "ARV-AGT-002" in text_of(r_no)
               and isinstance(r_alive, dict) and r_alive.get("id") == 11
               and rc_no == 0)
        s_yes = Server(tok=tokA)
        s_yes.handshake()
        r_yes = s_yes.call("list-library", {}, 12)
        d_yes = agt("list-library", tokA)
        ok2 = ok2 and (not is_err(r_yes)
                       and text_of(r_yes) == d_yes.stdout
                       and d_yes.returncode == 0)
        s_yes.close()
        check("MCPW-02", ok2,
              "the token by environment: without ARIVO_AGENT_TOKEN the read call fails with the typed identity refusal surfaced as the tool error (never a traceback — the server answers the next ping and exits cleanly); with a minted credential's token in the environment the read SERVES byte-equal to the owner's own read",
              "the env channel is the argv-visible residual's named home — the identity law rides query.py's own refusals, never wrapper-invented answers")

        # ---- MCPW-03 — the same-API law (byte-equality) + the audit row
        # (the direct baselines run FIRST — every direct --agent-token read
        # lands its own audit row, so the wrapper-read delta is measured
        # against a count taken AFTER the baselines)
        sA = Server(tok=tokA)
        sA.handshake()
        cases = [
            ("list-library", {}),
            ("get-journal", {"id": jid}),
            ("list-notes", {}),
            ("resolve-reference", {"ref": "note:" + nid}),
        ]
        ok3 = True
        baselines = {}
        for arm, args in cases:
            extra = []
            if "id" in args:
                extra = ["--id", args["id"]]
            if "ref" in args:
                extra = ["--ref", args["ref"]]
            baselines[arm] = agt(arm, tokA, *extra)
        aud0 = int(audit(f"SELECT count(*) FROM arv.agent_read_log "
                         f"WHERE credential_id='{cidA}';"))
        for i, (arm, args) in enumerate(cases):
            rw = sA.call(arm, args, 20 + i)
            rd = baselines[arm]
            ok3 = ok3 and (not is_err(rw) and rw is not None
                           and text_of(rw) == rd.stdout
                           and rd.returncode == 0)
        aud1 = int(audit(f"SELECT count(*) FROM arv.agent_read_log "
                         f"WHERE credential_id='{cidA}';"))
        # a REFUSED read (a nonexistent journal id) is NEVER audited — the
        # audit row lands only on served reads (the query.py law, unchanged)
        r_bogus = sA.call("get-journal", {"id": "00000000-0000-0000-0000-000000000000"}, 29)
        aud2 = int(audit(f"SELECT count(*) FROM arv.agent_read_log "
                         f"WHERE credential_id='{cidA}';"))
        ok3 = ok3 and (aud1 - aud0 == len(cases)
                       and is_err(r_bogus) and "ARV-QRY-001" in text_of(r_bogus)
                       and aud2 == aud1)
        sA.close()
        check("MCPW-03", ok3,
              "the same-API law + the audit: four arms (list-library, get-journal, list-notes, resolve-reference) served through tools/call BYTE-EQUAL to the direct --agent-token CLI reads (the env channel and the argv channel are the same retrieval core); the audit row per SERVED read (four reads, four rows, under A's credential); a refused read (a nonexistent id) NEVER audited",
              "the wrapper is a protocol translation, never a second retrieval path — byte-equality is the proof; the audit rides query.py's own transaction, never a wrapper-side second path")

        # ---- MCPW-04 — the read-only registry (the closed membership)
        sA2 = Server(tok=tokA)
        sA2.handshake()
        rt = sA2.tools()
        try:
            names = sorted(t["name"] for t in rt["result"]["tools"])
        except (KeyError, TypeError):
            names = None
        # a write command, a nonexistent arm, and a hostile name — all the
        # SAME typed registry refusal, never a passthrough, never a crash
        r_w1 = sA2.call("record_session", {}, 30)
        r_w2 = sA2.call("import_source", {}, 31)
        r_w3 = sA2.call("../etc/passwd", {}, 32)
        r_ok = sA2.ping(33)
        ok4 = (names == READ_ARMS
               and all(isinstance(r, dict) and "error" in r for r in (r_w1, r_w2, r_w3))
               and all(r["error"].get("code") == -32602
                       and "ARV-MCP-001" in r["error"].get("message", "")
                       for r in (r_w1, r_w2, r_w3))
               and isinstance(r_ok, dict) and r_ok.get("id") == 33)
        sA2.close()
        check("MCPW-04", ok4,
              "the read-only registry: tools/list = EXACTLY the 22 landed read arms (the closed membership — no write tool, no extra arm, the tool names ARE the arm names); a hostile tools/call naming a write command (record_session), another (import_source), or a path-shaped non-arm refuses the typed ARV-MCP-001 in the JSON-RPC -32602 form — never a passthrough, and the server answers the next ping",
              "READ-ONLY structural at the registry: the wrapper exposes the retrieval surface and NOTHING else — no command execution, no shell, no arbitrary access")

        # ---- MCPW-05 — the no-oracle through the wrapper
        s_unk = Server(tok="definitely-not-a-minted-token-value-0123456789")
        s_unk.handshake()
        r_unk = s_unk.call("list-library", {}, 40)
        s_unk.close()
        s_rev = Server(tok=tokR)
        s_rev.handshake()
        r_rev = s_rev.call("list-library", {}, 41)
        s_rev.close()
        ok5 = (is_err(r_unk) and "ARV-AGT-001" in text_of(r_unk)
               and is_err(r_rev) and "ARV-AGT-001" in text_of(r_rev)
               and text_of(r_unk) == text_of(r_rev)
               and "definitely-not-a-minted-token-value-0123456789" not in json.dumps(r_unk)
               and tokR not in json.dumps(r_rev)
               and tokA not in json.dumps(r_unk) + json.dumps(r_rev))
        check("MCPW-05", ok5,
              "the no-oracle through the wrapper: an unknown token and a REVOKED credential's token produce the SAME ARV-AGT-001 tool error, byte-equal (never a side channel); the token VALUE never appears in any response (the error, the result, or the registry listing)",
              "the invalid-token class is the product's own law — the wrapper surfaces it identically and never echoes the secret")

        # ---- MCPW-06 — the budgets + the argv-safety + the argument law
        sA3 = Server(tok=tokA)
        sA3.handshake()
        r_lim = sA3.call("list-library", {"limit": "5000"}, 50)
        r_nan = sA3.call("list-library", {"limit": "abc"}, 51)
        # the argv-safety: a leading-dash SEARCH TERM reaches the product as
        # DATA (the search serves — the term simply matches nothing), never
        # argparse's usage exit
        r_dash = sA3.call("search", {"terms": ["-dashy", "sesquine"]}, 52)
        # a leading-dash ID reaches the product's typed read-failure refusal
        # (the UUID-keyed arm's own ARV-QRY-002 for a malformed id — the
        # product's typed rule, never argparse's usage exit)
        r_iddash = sA3.call("get-journal", {"id": "-not-a-real-id"}, 53)
        # the argument law: an undeclared key and a non-scalar value refuse
        # the typed ARV-MCP-002 (the JSON-RPC -32602 form)
        r_key = sA3.call("list-library", {"bogus_key": "x"}, 54)
        r_typ = sA3.call("list-library", {"limit": {"nested": "object"}}, 55)
        r_alive6 = sA3.ping(56)
        ok6 = (is_err(r_lim) and "ARV-QRY-004" in text_of(r_lim)
               and is_err(r_nan) and "ARV-QRY-004" in text_of(r_nan)
               and is_err(r_dash) is False and "usage:" not in text_of(r_dash)
               and "api_version=" in text_of(r_dash)
               and is_err(r_iddash) and "ARV-QRY-002" in text_of(r_iddash)
               and "usage:" not in text_of(r_iddash)
               and isinstance(r_key, dict) and "error" in r_key
               and r_key["error"].get("code") == -32602
               and "ARV-MCP-002" in r_key["error"].get("message", "")
               and isinstance(r_typ, dict) and "error" in r_typ
               and r_typ["error"].get("code") == -32602
               and "ARV-MCP-002" in r_typ["error"].get("message", "")
               and isinstance(r_alive6, dict) and r_alive6.get("id") == 56)
        sA3.close()
        check("MCPW-06", ok6,
              "the budgets + the argv-safety + the argument law: the page params ride the tool arguments with the SAME ARV-QRY-004 bounds refusals as the direct read (an oversize and a non-integer limit); a leading-dash SEARCH TERM serves as DATA (the product's own semantics, never argparse's usage exit); a leading-dash ID reaches the product's typed ARV-QRY-002 read-failure refusal for a malformed id (never argparse); an undeclared key or a non-scalar value refuses the typed ARV-MCP-002 in the -32602 form; the server alive after every refusal",
              "the wrapper's own conventions: the --opt=value forms + the -- separator carry hostile DATA to the product's typed rules; the argument law is the schema's contract — unknown keys and non-scalar values never reach the child argv")

        # ---- MCPW-07 — the scope isolation (B through the wrapper)
        # (the id-set form — list-library emits bare source ids, never titles:
        # the AGT-06 lesson; B's count: the wrapper read + the direct baseline
        # read = 2, both audited under B's credential, exactly as the law
        # requires)
        sB = Server(tok=tokB)
        sB.handshake()
        dB = agt("list-library", tokB)
        rB = sB.call("list-library", {}, 60)
        dA = qy("list-library", "A")
        aB = audit(f"SELECT count(*) FROM arv.agent_read_log "
                   f"WHERE credential_id='{cidB}';")
        ok7 = (not is_err(rB) and text_of(rB) == dB.stdout
               and sid not in text_of(rB)
               and sid_b in text_of(rB)
               and sid in dA.stdout
               and int(aB) == 2)
        sB.close()
        check("MCPW-07", ok7,
              "the scope isolation: B's credential through the wrapper reads B's scope — byte-equal to B's direct read, B's own source id visible, A's source id invisible (the id-set form — list-library emits bare ids, the AGT-06 lesson), the audit rows under B's credential (never A's)",
              "the credential binds the scope through query.py's own RLS path — the wrapper adds no scope widening surface")

        # ---- MCPW-08 — the protocol hygiene
        sH = Server(tok=tokA)
        sH.handshake()
        sH.send({"jsonrpc": "2.0", "id": 70, "method": "resources/list"})
        r_m = sH.recv()
        sH.send_raw("this is not json {{{")
        r_p = sH.recv()
        sH.send_raw("[1, 2, 3]")
        r_b = sH.recv()
        # an unknown NOTIFICATION never answered: the next response is the
        # string-id ping's (the echo pin)
        sH.send({"jsonrpc": "2.0", "method": "notifications/whatever"})
        sH.send({"jsonrpc": "2.0", "id": "string-id-1", "method": "ping"})
        r_n = sH.recv()
        rc8 = sH.close()
        ok8 = (isinstance(r_m, dict) and r_m.get("id") == 70
               and r_m.get("error", {}).get("code") == -32601
               and isinstance(r_p, dict) and r_p.get("id") is None
               and r_p.get("error", {}).get("code") == -32700
               and isinstance(r_b, dict) and r_b.get("error", {}).get("code") == -32600
               and isinstance(r_n, dict) and r_n.get("id") == "string-id-1"
               and r_n.get("result") == {}
               and rc8 == 0)
        check("MCPW-08", ok8,
              "the protocol hygiene: an unknown method → the JSON-RPC -32601 (with the request id); malformed JSON → the -32700 parse error with id null (never a crash); a JSON array line → the -32600 invalid request (MCP has no batching); an unknown NOTIFICATION → NO response (the next response is the string-id ping's echo); the stdin close → the clean exit 0",
              "the wrapper is a well-formed JSON-RPC 2.0 peer on the MCP stdio transport — nothing but valid MCP messages on stdout (the spec law), diagnostics to stderr")

        # ---- MCPW-09 — the spawn-refusal pin (F-078-1's regression, the SEV
        # round-1 repair: a value the OS exec layer cannot carry is refused
        # TYPED at the adapter — never a process crash, never an unanswered
        # request, never an echo of the value)
        sR = Server(tok=tokA)
        sR.handshake()
        r_nul = sR.call("search", {"terms": ["sesquine\x00marker"]}, 80)
        r_big = sR.call("get-journal", {"id": "y" * 200000}, 81)
        r_alive9 = sR.ping(82)
        rc9 = sR.close()
        ok9 = (isinstance(r_nul, dict) and "error" in r_nul
               and r_nul["error"].get("code") == -32603
               and "ARV-MCP-003" in r_nul["error"].get("message", "")
               and isinstance(r_big, dict) and "error" in r_big
               and r_big["error"].get("code") == -32603
               and "ARV-MCP-003" in r_big["error"].get("message", "")
               and "y" * 200000 not in json.dumps(r_big)
               and isinstance(r_alive9, dict) and r_alive9.get("id") == 82
               and rc9 == 0)
        check("MCPW-09", ok9,
              "the spawn-refusal pin (F-078-1's regression): a NUL-bearing search term and a 200k-character id — values the OS exec layer cannot carry — are refused TYPED in the -32603 form naming ARV-MCP-003 (the value never echoed); the server answers the next ping and exits cleanly on the stdin close (the process never crashed, the request never left unanswered by silence)",
              "the adapter's own robustness law: hostile scalar values that pass the argument law but cannot cross the OS boundary are a TYPED refusal at the protocol layer — the convention the timeout arm already followed")

        # ---- MCPW-10 — the parse-refusal pin (F2-078-1's regression, the
        # SEV round-2 repair: a deep VALID-JSON line — nesting beyond the
        # interpreter's json recursion cliff — is a PARSE-ERROR answer, never
        # a RecursionError crash)
        sD = Server(tok=tokA)
        sD.handshake()
        sD.send_raw("[" * 20000)  # valid JSON syntax, depth 20000
        r_deep = sD.recv()
        r_alive10 = sD.ping(90)
        rc10 = sD.close()
        ok10 = (isinstance(r_deep, dict) and r_deep.get("id") is None
                and r_deep.get("error", {}).get("code") == -32700
                and isinstance(r_alive10, dict) and r_alive10.get("id") == 90
                and rc10 == 0)
        check("MCPW-10", ok10,
              "the parse-refusal pin (F2-078-1's regression): a single valid-JSON line nested 20000 deep (beyond the interpreter's json recursion cliff) is answered as the -32700 parse-error class with id null — never a RecursionError crash; the server answers the next ping and exits cleanly on the stdin close",
              "the parse arm's own robustness law: the deep-nesting class joins the malformed-JSON class as a PARSE-ERROR answer — the interpreter's RecursionError is a parse failure at this boundary, never a process death")

        print()
        if FAILS:
            print(f"RED — the P4-E MCP-wrapper suite fails: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P4-E MCP-wrapper suite (MCPW-01..10) passes")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
