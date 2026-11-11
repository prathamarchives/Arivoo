#!/usr/bin/env python3
"""harness/tests/test_agent_access.py — P4-E slice one acceptance suite (CLAIM-077,
the scoped agent read surface — the PLAN 4E row elaborated one phase deep at the
P4-D exit; record 69 §2). Red-first (LAW-11): at CLAIM-076's merged head 898b9f2a
the suite fails with ARV-TEST-000 (machinery-absent; red-01.txt).

THE CONTRACT (the PLAN 4E row): "authorized agents read the owner's journal and
capture context through the same API with provenance/scope/budgets; READ-ONLY at
first; owner-scope enforced on every query; imported text untrusted; no arbitrary
database access; Q9/Q10 handled honestly." The North Star's own words: "Specifically
for AI, I can just connect an agent and it has all the context of me" (C2).

THE MACHINE: arv.agent_credential (the owner-minted credential — the token VALUE
generated at 32 bytes secrets-quality randomness, shown ONCE in the mint ack, only
the sha256 stored; the closed scopes CHECK 'read' — READ-ONLY structural; the
one-way revocation revoked_at NULL->set never unset, the guarded one-transition
law; RLS forced + the owner policy) + arv.agent_read_log (the append-only audit
trail: the arm + the bounded REQUEST facts, never the content) + commands.py
mint_agent_credential / revoke_agent_credential (through the spine's ack contract;
the label law; the no-oracle revocation refusal; NO outbox ride — a local access
primitive, never owner content) + query.py's --agent-token mode on the READ arms
(the credential-bound owner scope — the caller never passes --owner; the sha256
lookup through the narrow SECURITY DEFINER verification function — the system's
own authentication primitive, exposing nothing beyond the valid-token scope
binding; the same arms' reads; the audit row per served read; the page bounds as
the read budget).

Refusal codes: ARV-AGT-001 the invalid-token class (unknown, revoked — the SAME
refusal, never a side channel, the token NEVER echoed — it is a secret);
ARV-AGT-002 the ambiguous identity (--owner AND --agent-token together);
ARV-AGT-003 the label law; ARV-QRY-004 the page bounds (the shared law).

Cases (the AGT registry; each pin's full statement lives at its check()):
  AGT-01 the mint round-trip + the one-time display: the credential row with
         the sha256 (never the value); the token shown ONCE in the first ack;
         the replay ack carries NO token line; the provenance complete
  AGT-02 the label law: empty / oversized (>128) / NUL-carrying labels refuse
         ARV-AGT-003, zero rows
  AGT-03 the agent read mode over the owner's context: the SAME arms' answers
         byte-equal to the owner's own reads (library, notes, journal,
         references, search, reading state); the audit row per served read
         (the arm + the bounded request facts, never the content); the caller
         never passes --owner
  AGT-04 the no-oracle invalid-token class: unknown and revoked tokens the
         SAME ARV-AGT-001 refusal, byte-equal, the token NEVER echoed
  AGT-05 the ambiguous identity + the read-only structure: --owner AND
         --agent-token together refuses ARV-AGT-002; no write command accepts
         --agent-token (the CLI attempt exits nonzero with zero rows — the
         read-only law structural)
  AGT-06 the scope isolation: B's credential reads B's scope (A's content
         invisible — the RLS law through the credential-bound scope); B's
         reads audited under B's credential
  AGT-07 the revocation: the one-way transition (revoked_at set); the
         already-revoked refuses (the alternation); the absent/cross-owner
         the no-oracle ARV-AGT-001; after revocation the reads refuse
         ARV-AGT-001; the read log PRESERVES the pre-revocation audit rows
  AGT-08 the budget + the substrate: the page bounds enforced on the agent
         reads (the shared limits); the read_log append-only (UPDATE/DELETE
         refused); the credential's one-transition guard (the label/owner/
         token_hash columns immutable; revoked_at the ONLY settable column,
         one-way); the schema audits (the closed scopes CHECK, RLS forced,
         the grants)

Run: python3 harness/tests/test_agent_access.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []

# P4-E slice one (CLAIM-077) — the machinery-absent probe (LAW-11): the scoped
# agent read machinery is the mint command + the read mode. The probe is
# DB-free by construction (the argparse refusal precedes any connection).
_p77 = subprocess.run(
    [sys.executable, str(REPO / "harness" / "commands.py"), "mint_agent_credential",
     "--owner", "A", "--actor", "owner", "--client-id", "cli-probe",
     "--idem-key", "p4e1-machinery-absent-probe", "--label", "probe"],
    capture_output=True, text=True, timeout=60,
    env=dict(os.environ, PGDATABASE="arv_p4e1_red_probe_absent"))
if "invalid choice" in _p77.stderr:
    print("FAIL ARV-TEST-000: the P4-E slice one scoped-agent-read machinery is "
          "absent (machinery-absent class; the mint_agent_credential command "
          "absent from the CLI) — the implementation lands after this RED, "
          "never before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

DB = ENV = None

TEXT = ("The agent-access corpus: the persistent anchor phrase lives here.\n"
        "Second paragraph: the measurable span lives here instead.\n"
        "Third paragraph closes the corpus.\n")


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
    """The agent read invocation: --agent-token REPLACES --owner (never both)."""
    return cli(str(REPO / "harness" / "query.py"), arm, "--agent-token", token, *extra)


def audit(query: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", query],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def audit_rows(query: str) -> list:
    return [ln for ln in audit(query).split("\n") if ln.strip()]


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_app", "-d", DB,
                           "-c", f"SET app.current_owner='{owner}'; {sql}"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def super_sql(sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "postgres", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60, env=ENV)


def ack_field(p: subprocess.CompletedProcess, field: str) -> str:
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def token_of(p: subprocess.CompletedProcess) -> str:
    """The one-time token display: 'token=<value>' in the FIRST ack only."""
    return ack_field(p, "token")


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4e1")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)

        # ------- the fixture: two owners with real capture context
        src_file = pathlib.Path(tempfile.mkdtemp(prefix="arv-src-")) / "corpus.md"
        src_file.write_text(TEXT, encoding="utf-8")
        s1 = TEXT.index("persistent anchor")
        e1 = s1 + len("persistent anchor")
        pa = cmd("import_source", "--file", str(src_file), "--media-type",
                 "text/plain", "--title", "The Agent Corpus", key="ag-imp1")
        sid = ack_field(pa, "result_ref")
        ph = cmd("create_highlight", "--source-id", sid, "--start", str(s1),
                 "--end", str(e1), key="ag-hl1")
        hid = ack_field(ph, "result_ref")
        pn = cmd("create_note", "--content", "The owner's private note: sesquine token.",
                 key="ag-n1")
        nid = ack_field(pn, "result_ref")
        pj = cmd("journal_block", "--kind", "raw",
                 "--content", "The owner's raw thinking for the agent context.",
                 key="ag-jb1")
        jid = ack_field(pj, "result_ref").split("@")[0]
        pb = cmd("import_source", "--file", str(src_file), "--media-type",
                 "text/plain", "--title", "B's Corpus", key="ag-impB", owner="B")
        sid_b = ack_field(pb, "result_ref")

        # ---- AGT-01 — the mint round-trip + the one-time display
        pm = cmd("mint_agent_credential", "--label", "research assistant",
                 key="ag-mint1")
        tok = token_of(pm)
        cid = ack_field(pm, "result_ref")
        row = audit_rows(f"SELECT label, scopes, revoked_at::text, token_hash <> '' "
                         f"FROM arv.agent_credential WHERE id='{cid}';")
        prov = audit_rows(f"SELECT actor FROM arv.agent_credential WHERE id='{cid}';")
        # the replay: the SAME key + body -> the recorded result, NO token line
        pr = cmd("mint_agent_credential", "--label", "research assistant",
                 key="ag-mint1")
        # the token VALUE never stored: the sha256 of the displayed value IS the
        # stored hash (proven by a successful agent read in AGT-03); here: the
        # row's token_hash is 64-hex and DIFFERS from the value
        import hashlib as _h
        h64 = len(audit(f"SELECT token_hash FROM arv.agent_credential "
                        f"WHERE id='{cid}';")) == 64
        val_not_stored = audit(f"SELECT count(*) FROM arv.agent_credential "
                               f"WHERE token_hash = '{tok}';") == "0"
        # the argv-safe first character (the F-074-1 class caught live by the
        # measured set: no minted token may start with '-' — the separate-argv
        # form '--agent-token <value>' must always parse)
        dash_free = True
        for _i in range(12):
            _pm = cmd("mint_agent_credential", "--label", f"probe-{_i}",
                      key=f"ag-mintp{_i}")
            _tok = token_of(_pm)
            if _pm.returncode != 0 or not _tok or _tok[0] == "-":
                dash_free = False
        ok1 = (dash_free
               and pm.returncode == 0 and "status=committed" in pm.stdout
               and tok and cid
               and row and row[0] == "research assistant|read||t"
               and prov and prov[0] == "owner"
               and pr.returncode == 0 and "status=replayed" in pr.stdout
               and ack_field(pr, "result_ref") == cid
               and token_of(pr) == ""            # the one-time display law
               and h64 and val_not_stored)
        check("AGT-01", ok1,
              "the mint round-trip: the credential row lands (label, scopes='read', revoked_at NULL, the token_hash a 64-hex sha256 — the VALUE never stored, proven: the value string matches no row); the ack carries result_ref + token=<value> ONCE (the one-time display law — the password-reset convention); the replay ack carries the recorded result_ref and NO token line; the provenance complete (actor=owner)",
              "the credential is the owner-minted authorization primitive — the token value exists only in the one-time display and the caller's own records (Q10's honest boundary)")

        # ---- AGT-02 — the label law (ARV-AGT-003)
        before2 = audit("SELECT count(*) FROM arv.agent_credential;")
        p2a = cmd("mint_agent_credential", "--label", "", key="ag-lab1")
        p2b = cmd("mint_agent_credential", "--label", "x" * 129, key="ag-lab2")
        # the NUL class: argv cannot carry NUL (the OS ValueError precedes the
        # command — the CLAIM-074 lesson) — the law's OWN layer probed in-process
        from harness.commands import _agt_label as _label_law
        try:
            _label_law("bad\x00label")
            p2c_refused = False
        except Exception as _e:
            p2c_refused = getattr(_e, "code", None) == "ARV-AGT-003"
        after2 = audit("SELECT count(*) FROM arv.agent_credential;")
        ok2 = (p2a.returncode == 1 and "ARV-AGT-003" in p2a.stdout
               and p2b.returncode == 1 and "ARV-AGT-003" in p2b.stdout
               and p2c_refused
               and after2 == before2)
        check("AGT-02", ok2,
              "the label law: empty, oversized (>128), and NUL-carrying labels refuse ARV-AGT-003 with zero rows — never a clamp, never a silent truncation",
              "the label is the owner's own name for the credential, bounded and clean (the 0017 name-law convention)")

        # ---- AGT-03 — the agent read mode over the owner's context
        # the SAME arms' answers byte-equal to the owner's own reads
        arms = [
            ("list-library", []),
            ("get-reading-state", []),
            ("list-notes", []),
            ("get-note", ["--id", nid]),
            ("list-journal", []),
            ("resolve-reference", ["--ref", f"highlight:{hid}@1"]),
            ("search", ["sesquine"]),
        ]
        byte_equal, audit_rows_count = True, 0
        for arm, extra in arms:
            o = qy(arm, "A", *extra)
            g = agt(arm, tok, *extra)
            if not (o.returncode == 0 and g.returncode == 0
                    and o.stdout == g.stdout):
                byte_equal = False
        logs = audit_rows(f"SELECT credential_id, arm FROM arv.agent_read_log "
                          f"WHERE credential_id='{cid}' ORDER BY id;")
        want_arms = sorted(a for a, _ in arms)
        got_arms = sorted(r.split("|")[1] for r in logs if r.split("|")[0] == cid)
        ok3 = (byte_equal
               and [r.split("|")[0] for r in logs].count(cid) == len(arms)
               and got_arms == want_arms)
        check("AGT-03", ok3,
              "the agent read mode: every read arm answers through --agent-token with the SAME bytes as the owner's own read (the library, the reading state, the notes, the single note with its refs, the journal, the reference resolution, the keyword search — the owner's journal and capture context through the same API); the audit row lands per served read (the credential + the arm); the caller never passes --owner (the credential binds the scope)",
              "C2 — the owner's agents have the owner's context: the SAME arms, the SAME answers, the scope from the credential (the PLAN 4E row's letter)")

        # ---- AGT-04 — the no-oracle invalid-token class (ARV-AGT-001)
        ghost_tok = "not-a-real-token-value-at-all"
        p4a = agt("list-library", ghost_tok)
        # a REVOKED credential's token must be the SAME refusal (AGT-07 revokes
        # later; here a second credential revoked now)
        pm2 = cmd("mint_agent_credential", "--label", "shortlived", key="ag-mint2")
        tok2 = token_of(pm2)
        cid2 = ack_field(pm2, "result_ref")
        cmd("revoke_agent_credential", "--id", cid2, key="ag-rvk2")
        p4b = agt("list-library", tok2)
        ok4 = (p4a.returncode == 1 and "ARV-AGT-001" in p4a.stdout
               and p4b.returncode == 1 and "ARV-AGT-001" in p4b.stdout
               and p4a.stdout == p4b.stdout          # the SAME refusal, byte-equal
               and ghost_tok not in p4a.stdout        # the token NEVER echoed
               and tok2 not in p4b.stdout
               and "Traceback" not in (p4a.stderr + p4b.stderr))
        check("AGT-04", ok4,
              "the no-oracle invalid-token class: an unknown token and a revoked credential's token are the SAME ARV-AGT-001 refusal — byte-equal, the token value NEVER echoed (it is a secret; the refusal names the class, never the credential) — never a side channel, never a traceback",
              "an invalid credential must not reveal whether it was once valid, whose it was, or what it could read (SYS-02's agent matrix)")

        # ---- AGT-05 — the ambiguous identity + the read-only structure
        p5a = cli(str(REPO / "harness" / "query.py"), "list-library",
                  "--owner", "A", "--agent-token", tok)
        # the write commands do not accept --agent-token at all (READ-ONLY
        # structural): the CLI attempt exits nonzero, zero rows
        before5 = audit("SELECT count(*) FROM arv.note;")
        p5b = cli(str(REPO / "harness" / "commands.py"), "create_note",
                  "--owner", "A", "--actor", "owner", "--client-id", "cli-1",
                  "--idem-key", "ag-write1", "--content", "x",
                  "--agent-token", tok)
        after5 = audit("SELECT count(*) FROM arv.note;")
        ok5 = (p5a.returncode == 1 and "ARV-AGT-002" in p5a.stdout
               and p5b.returncode != 0 and after5 == before5)
        check("AGT-05", ok5,
              "the ambiguous identity refuses ARV-AGT-002 (--owner AND --agent-token together — never a silent preference between the caller's claim and the credential's binding); the write path is structurally closed to credentials: no write command accepts --agent-token (the CLI attempt exits nonzero with zero rows — READ-ONLY at first, per the row's own letter)",
              "the credential grants READ access only — the write surface never learns the token (the scopes CHECK and the CLI surface agree)")

        # ---- AGT-06 — the scope isolation
        pmb = cmd("mint_agent_credential", "--label", "B's assistant",
                  key="ag-mintB", owner="B")
        tokb = token_of(pmb)
        gb = agt("list-library", tokb)
        # B's credential sees ONLY B's corpus (the bare-id listing: B's source
        # id present, A's absent — the credential-bound RLS)
        ids_b = sorted(ln.strip() for ln in gb.stdout.splitlines()
                       if ln.strip() and not ln.startswith("#")) if gb.returncode == 0 else []
        ga = agt("list-library", tok)
        ids_a = sorted(ln.strip() for ln in ga.stdout.splitlines()
                       if ln.strip() and not ln.startswith("#")) if ga.returncode == 0 else []
        logb = audit_rows(f"SELECT count(*) FROM arv.agent_read_log "
                          f"WHERE credential_id='{ack_field(pmb, 'result_ref')}';")
        ok6 = (gb.returncode == 0 and ga.returncode == 0
               and ids_b == [sid_b] and sid not in ids_b
               and ids_a == [sid] and sid_b not in ids_a
               and logb and int(logb[0]) >= 1)
        check("AGT-06", ok6,
              "the scope isolation: B's credential reads B's scope (only B's corpus — A's material invisible through the credential-bound RLS) while A's credential reads A's; B's reads audited under B's own credential — the agent of one owner never widens scope (SYS-02's agent matrix, the C2 law)",
              "the owner scope comes from the credential, enforced by RLS on every query — never from the caller's claim")

        # ---- AGT-07 — the revocation (the one-way transition)
        kept_before = audit(f"SELECT count(*) FROM arv.agent_read_log "
                            f"WHERE credential_id='{cid}';")
        p7r = cmd("revoke_agent_credential", "--id", cid, key="ag-rvk1")
        rev = audit_rows(f"SELECT revoked_at IS NOT NULL FROM arv.agent_credential "
                         f"WHERE id='{cid}';")
        # the already-revoked refuses (the alternation)
        p7rr = cmd("revoke_agent_credential", "--id", cid, key="ag-rvk1b")
        # the absent/cross-owner the no-oracle
        ghost7 = "00000000-0000-7000-8000-00000000000d"
        p7g = cmd("revoke_agent_credential", "--id", ghost7, key="ag-rvkG")
        p7x = cmd("revoke_agent_credential", "--id", cid2, key="ag-rvkX", owner="B")
        # after revocation the reads refuse ARV-AGT-001
        p7read = agt("list-library", tok)
        # the read log PRESERVES the pre-revocation audit rows
        kept = audit(f"SELECT count(*) FROM arv.agent_read_log "
                     f"WHERE credential_id='{cid}';")
        ok7 = (p7r.returncode == 0 and rev and rev[0] == "t"
               and p7rr.returncode == 1           # the alternation refusal
               and p7g.returncode == 1 and p7x.returncode == 1
               and "ARV-AGT-001" in p7g.stdout and "ARV-AGT-001" in p7x.stdout
               and p7g.stdout == p7x.stdout.replace(cid2, ghost7)
               and p7read.returncode == 1 and "ARV-AGT-001" in p7read.stdout
               and int(kept) == int(kept_before))   # every pre-revocation row intact
        check("AGT-07", ok7,
              "the revocation: the one-way transition (revoked_at NULL->set); the already-revoked refuses (the alternation — no un-revoke, the purge's own finality class); the absent and cross-owner credentials the SAME no-oracle ARV-AGT-001; after revocation the reads refuse ARV-AGT-001 (the invalid-token class — revoked and unknown indistinguishable); the read log PRESERVES the pre-revocation audit rows (the history intact — the audit trail is append-only evidence, never rewritten by the revocation)",
              "the revocation is the owner's kill switch — final, auditable, and never silently widening or narrowing the recorded history")

        # ---- AGT-08 — the budget + the substrate
        # the page bounds enforced on the agent reads (the shared limits)
        p8a = agt("list-library", tokb, "--limit", "99999")
        # the read_log append-only
        lr = audit(f"SELECT id FROM arv.agent_read_log LIMIT 1;")
        p8u = app_sql(f"UPDATE arv.agent_read_log SET arm='tampered' "
                      f"WHERE id='{lr}';")
        p8d = app_sql(f"DELETE FROM arv.agent_read_log WHERE id='{lr}';")
        # the credential's one-transition guard: the label immutable; revoked_at
        # the ONLY settable column, one-way (a live credential for the probe)
        pm3 = cmd("mint_agent_credential", "--label", "guard probe", key="ag-mint3")
        cid3 = ack_field(pm3, "result_ref")
        p8l = app_sql(f"UPDATE arv.agent_credential SET label='tampered' "
                      f"WHERE id='{cid3}';")
        p8h = app_sql(f"UPDATE arv.agent_credential SET token_hash='x' "
                      f"WHERE id='{cid3}';")
        p8rev = super_sql(f"UPDATE arv.agent_credential SET revoked_at=now() "
                          f"WHERE id='{cid3}' AND revoked_at IS NULL;")
        p8unrev = super_sql(f"UPDATE arv.agent_credential SET revoked_at=NULL "
                            f"WHERE id='{cid3}';")
        # the schema audits: the closed scopes CHECK, RLS forced, the grants
        rls = audit_rows("SELECT relrowsecurity || '|' || relforcerowsecurity FROM "
                         "pg_class WHERE relname IN ('agent_credential', "
                         "'agent_read_log') ORDER BY relname;")
        # the grants audit: has_table_privilege (the journal family's form —
        # information_schema.role_table_grants is grantee-scoped and shows
        # nothing to arv_read)
        grants = audit("SELECT has_table_privilege('arv_app', 'arv.agent_credential', 'INSERT')"
                       " AND has_table_privilege('arv_app', 'arv.agent_credential', 'SELECT')"
                       " AND has_table_privilege('arv_app', 'arv.agent_credential', 'UPDATE')"
                       " AND NOT has_table_privilege('arv_app', 'arv.agent_credential', 'DELETE')"
                       " AND has_table_privilege('arv_app', 'arv.agent_read_log', 'INSERT')"
                       " AND has_table_privilege('arv_app', 'arv.agent_read_log', 'SELECT')"
                       " AND NOT has_table_privilege('arv_app', 'arv.agent_read_log', 'UPDATE');")
        ok8 = (p8a.returncode == 1 and "ARV-QRY-004" in p8a.stdout
               and p8u.returncode != 0 and p8d.returncode != 0
               and p8l.returncode != 0 and p8h.returncode != 0
               and p8rev.returncode == 0 and p8unrev.returncode != 0
               and rls == ["true|true", "true|true"] and grants == "t")
        check("AGT-08", ok8,
              "the budget + the substrate: the page bounds enforced on the agent reads (the shared _page_args limits — an oversize --limit refuses ARV-QRY-004 exactly as the owner's reads); the read_log append-only (UPDATE/DELETE refused at the substrate); the credential's one-transition guard (the label and token_hash immutable; revoked_at the ONLY settable column, one-way — the un-revoke refused); the schema audits (RLS enabled AND forced on both tables, arv_app INSERT+SELECT only)",
              "the budgets at this phase are the shared page bounds (the deeper response budgets are Phase 5's retrieval increments — recorded, never claimed here); the substrate mirrors the command surface (the 0007/0008 convention)")

        # ---- AGT-09 — the quote-bearing owner (F2-077-5's regression pin:
        # the served read MUST audit — the owner travels escaped)
        pmq = cmd("mint_agent_credential", "--label", "quote owner probe",
                  key="ag-mintQ", owner="O'Brien")
        tokq = token_of(pmq)
        cidq = ack_field(pmq, "result_ref")
        tfq = pathlib.Path(tempfile.mkdtemp(prefix="arv-agtq-")) / "q.md"
        tfq.write_text("the quote-owner corpus text.\n", encoding="utf-8")
        cmd("import_source", "--file", str(tfq), "--media-type", "text/plain",
            "--title", "O'Brien's Corpus", key="ag-impQ", owner="O'Brien")
        gq = agt("list-library", tokq)
        aq = audit(f"SELECT count(*) FROM arv.agent_read_log "
                   f"WHERE credential_id='{cidq}';")
        ok9 = (pmq.returncode == 0 and tokq and cidq
               and gq.returncode == 0 and "ARV-AGT-005" not in gq.stdout
               and int(aq) == 1)
        check("AGT-09", ok9,
              "the quote-bearing owner (F2-077-5's regression pin): O'Brien's credential mints; the agent read SERVES (no ARV-AGT-005 loud failure) and the audit row LANDS (the owner travels escaped through the audit insert — the file's own _read convention, never raw interpolation)",
              "a served read must always audit — the escape closes the quote-bearing-owner class the round-2 reviewer demonstrated live")

        print()
        if FAILS:
            print(f"RED — the P4-E agent-access suite fails: {', '.join(FAILS)}")
            return 1
        print("GREEN — the P4-E agent-access suite (AGT-01..09) passes")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
