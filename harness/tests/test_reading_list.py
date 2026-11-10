#!/usr/bin/env python3
"""harness/tests/test_reading_list.py — P4-C slice five acceptance suite (CLAIM-074,
the reading-list surface — the post-#108 reconciliation's landing; PLAN's 4C row
elaborated one phase deep at slice four's landing; record 66 §2; the RTM §2 item 9
derived-state rule). Red-first (LAW-11): at CLAIM-073's merged head 3f6922b the suite
fails with ARV-TEST-000 (machinery-absent; red-01.txt).

THE CONTRACT: the user-defined lists over the landed library — the North Star owner
words name THREE surfaces ("I have lists, a library, and lists of what I'm currently
reading"); the library and the current-reading lists LANDED at CLAIM-070; this slice
lands the LISTS. A list is a named, owner-scoped container of SOURCE memberships. The
membership is an EVENT HISTORY: every add/remove is an append-only event row (the
closed op vocabulary 'added'|'removed'); the CURRENT membership is DERIVED (the last
op per pair wins — a projection); the event rows are the recovery substrate (RTM §2
item 9: every add/remove retained, never a destructive delete, the full history
reconstructable from the events alone). NO name uniqueness — Q11's identity baseline
(the identity is the uuid, never the name; two lists may share a name). The writes
ride the spine's own ack contract (idempotent, the frozen grammar, the client-outbox
ride — the enqueue AND the delivery TOGETHER per the CLAIM-073 law, the delivery pin
at the sync suite's SYN-22).

Refusal codes: ARV-RLS-001 the absent/cross-owner list (the no-oracle); ARV-RLS-002
the absent/cross-owner source at the membership (the no-oracle at the binding);
ARV-RLS-003 the name law (empty / oversized / NUL-carrying refused, never clamped).

Cases (the RLS registry; each pin's full statement lives at its check()):
  RLS-01 the create round-trip: create_reading_list acks with the frozen grammar
         (status=committed + result_ref=<list-id> the bare uuid, the create class +
         durability_rung=local_durable + api_version=1); the name reads back
         exact; TWO lists may share one name (Q11's identity law — the uuid
         disambiguates, never the name); list-lists answers both
  RLS-02 the typed refusals + the zero-effect law: the empty name, the >512 name,
         and the NUL-carrying name refuse ARV-RLS-003 (never clamped); the absent
         list at the add/remove and the cross-owner list refuse ARV-RLS-001 (the
         no-oracle — byte-equal for absent vs cross-owner); the absent source and
         the cross-owner source at the membership refuse ARV-RLS-002 (the no-oracle
         at the binding); every refusal leaves ZERO rows
  RLS-03 the membership event machine: add appends the 'added' event (the current
         view answers the member); remove appends the 'removed' event (the current
         view hides the member, the event history keeps it); re-add after remove
         appends a NEW 'added' event (a new row, never a mutation — reactivated);
         the idempotency (same key+body -> replayed, the same result_ref; same
         key+different body -> ARV-CMD-409, zero effect); the crash matrix's
         lost-ack arm (post-commit-pre-ack exits 2, the effect committed, the
         replay converges)
  RLS-04 the read arms' contract + the owner isolation: list-lists bounded and
         paginated (the ARV-QRY-004 bounds refusals 0/1001/not-an-integer; the
         keyset walk at --limit 2 with the union exact, no dups; the member counts
         derived; the version header; the empty library's two-line answer); get-list
         answers the CURRENT membership (one row per active member, the added_at
         carried); the no-oracle byte-equal (absent vs cross-owner); owner B sees
         only B's lists
  RLS-05 the 0017 substrate conventions + the registry rows: RLS enabled AND forced
         + the owner policy; the grants (INSERT+SELECT arv_app, SELECT arv_read, no
         UPDATE/DELETE); the op CHECK by name (added|removed); the append-only
         triggers refusing UPDATE/DELETE; the composite FKs; NO DEFAULTs (LAW-24);
         the hostile INSERT with an out-of-vocabulary op refused; the hostile INSERT
         binding an absent list refused; capability.py's reading-lists
         reserved-surface row; crash.py's membership
  RLS-06 the outbox enqueue (the CLAIM-073 law's enqueue half; the delivery pin at
         SYN-22): every committed list write carries its client-outbox row in the
         SAME transaction (the observed count over the suite's own traffic — the
         creates + the adds + the removes + the crash-committed write; the
         refusals and replays add none)

Run: python3 harness/tests/test_reading_list.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): the write command, the two read
# arms, and the migration are each absent at the RED tree — the cheapest honest
# probe per surface.
_p = subprocess.run([sys.executable, str(REPO / "harness" / "commands.py"),
                     "create_reading_list", "--help"], capture_output=True, text=True)
_absent_write = "invalid choice" in _p.stderr
_p2 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                      "list-lists", "--owner", "A"],
                     capture_output=True, text=True, timeout=60)
_absent_lists = "invalid choice" in _p2.stderr
_p3 = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                      "get-list", "--owner", "A", "--id", "x"],
                     capture_output=True, text=True, timeout=60)
_absent_get = "invalid choice" in _p3.stderr
_mig = sorted(p.name for p in (REPO / "harness" / "migrations").glob("0017_*.sql"))
if _absent_write or _absent_lists or _absent_get or not _mig:
    print(f"FAIL ARV-TEST-000: the P4-C slice five reading-list machinery is absent "
          f"(machinery-absent class; create_reading_list command absent: {_absent_write}; "
          f"list-lists arm absent: {_absent_lists}; get-list arm absent: "
          f"{_absent_get}; migration 0017 present: {bool(_mig)}) — the implementation "
          "lands after this RED, never before it (LAW-11)")
    sys.exit(1)

from harness.adapters import pg  # noqa: E402

DB = ENV = None

NAME = "The Reading List"
NAME2 = "The Second List"
LONGNAME = "L" * 513          # the name law's upper bound is 512


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def cli(*args, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=300, env=env or ENV)


def cmd(op: str, *args, owner="A", key=None, client="cli-1",
        crash_at=None) -> subprocess.CompletedProcess:
    a = [str(REPO / "harness" / "commands.py"), op, "--owner", owner,
         "--actor", "owner", "--client-id", client]
    if key is not None:
        a += ["--idem-key", key]
    if crash_at is not None:
        return cli(str(REPO / "harness" / "crash.py"), "--command", op,
                   "--point", crash_at, "--owner", owner, "--actor", "owner",
                   "--client-id", client, "--idem-key", key, *args)
    return cli(*a, *args)


def mklist(name: str, key: str, owner="A") -> subprocess.CompletedProcess:
    return cmd("create_reading_list", "--name", name, key=key, owner=owner)


def add(list_id: str, source_id: str, key: str, owner="A",
        crash_at=None) -> subprocess.CompletedProcess:
    return cmd("add_to_list", "--list", list_id, "--source", source_id,
               key=key, owner=owner, crash_at=crash_at)


def rem(list_id: str, source_id: str, key: str, owner="A") -> subprocess.CompletedProcess:
    return cmd("remove_from_list", "--list", list_id, "--source", source_id,
               key=key, owner=owner)


def cap(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "capability.py"), *args)


def query(*args) -> subprocess.CompletedProcess:
    return cli(str(REPO / "harness" / "query.py"), *args)


def get_list(owner: str, list_id: str, *extra) -> subprocess.CompletedProcess:
    return query("get-list", "--owner", owner, "--id", list_id, *extra)


def ref_of(r: subprocess.CompletedProcess) -> str:
    for ln in r.stdout.splitlines():
        if ln.startswith("ACK") and "result_ref=" in ln:
            return ln.split("result_ref=")[1].split()[0]
    return ""


def jline(r: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(next(ln for ln in r.stdout.splitlines() if ln.strip()))
    except Exception:
        return {}


def jlines(r: subprocess.CompletedProcess) -> list:
    return [json.loads(ln) for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def page(r: subprocess.CompletedProcess) -> "tuple[list, str, str]":
    lines = [ln for ln in r.stdout.split("\n") if ln != ""]
    if len(lines) < 2:
        return [], "", ""
    return lines[1:-1], lines[0], lines[-1]


def audit(sql: str) -> str:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60,
                          env=ENV).stdout.strip()


def audit_rows(sql: str) -> list:
    return [ln for ln in audit(sql).splitlines() if ln.strip()]


def super_sql(sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "postgres", "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60, env=ENV)


def app_sql(sql: str, owner: str = "A") -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_app", "-d", DB,
                           "-c", f"SET app.current_owner='{owner}'; {sql}"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4c5")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="arv-p4c5-"))

        # the fixtures: A's two sources + B's own source (the cross-owner probes)
        f1 = tmp / "one.txt"
        f1.write_text("The first source document.\n", encoding="utf-8")
        r_s1 = cmd("import_source", "--title", "The First Source",
                   "--file", str(f1), key="imp-1")
        src1 = ref_of(r_s1)
        f2 = tmp / "two.txt"
        f2.write_text("The second source document.\n", encoding="utf-8")
        r_s2 = cmd("import_source", "--title", "The Second Source",
                   "--file", str(f2), key="imp-2")
        src2 = ref_of(r_s2)
        f3 = tmp / "bsrc.txt"
        f3.write_text("B's own source document.\n", encoding="utf-8")
        r_s3 = cmd("import_source", "--title", "B's Source", "--file", str(f3),
                   key="imp-3", owner="B")
        bsrc = ref_of(r_s3)

        # ---- RLS-01 — the create round-trip
        r_l1 = mklist(NAME, key="rls-1")
        ack1 = next((ln for ln in r_l1.stdout.splitlines() if ln.startswith("ACK")), "")
        l1 = ref_of(r_l1)
        r_l2 = mklist(NAME, key="rls-2")             # the SAME name — Q11's law
        l2 = ref_of(r_l2)
        g_lists = query("list-lists", "--owner", "A")
        rows01 = jlines(g_lists)
        names01 = sorted(r.get("name") for r in rows01)
        hdr01 = page(g_lists)[1]
        ok1 = (r_l1.returncode == 0 and "status=committed" in ack1
               and f"result_ref={l1}" in ack1 and "durability_rung=local_durable" in ack1
               and "api_version=1" in ack1
               and r_l2.returncode == 0 and l2 and l1 != l2
               and g_lists.returncode == 0
               and names01 == sorted([NAME, NAME])   # both lists, the shared name honest
               and all(r.get("api_version") == 1 for r in rows01)
               and "api_version=" in hdr01)
        check("RLS-01", ok1,
              "the create round-trip: create_reading_list acks with the frozen grammar "
              "(status=committed + result_ref=<list-id> the bare uuid, the create class + "
              "durability_rung=local_durable + api_version=1); the name reads back exact; "
              "TWO lists may share one name (Q11's identity law — the uuid disambiguates, "
              "never the name; no uniqueness constraint, never an auto-merge); list-lists "
              "answers both with the version header",
              "commands.py create_reading_list through the spine's own ack contract + "
              "query.py list-lists — the identity is the uuid, the name is the owner's "
              "own label (Q11's baseline applied to the list family)")

        # ---- RLS-02 — the typed refusals + the zero-effect law
        r_e1 = mklist("", key="rlsx-1")                              # empty
        r_e2 = mklist(LONGNAME, key="rlsx-2")                        # > 512
        r_e3 = mklist("na\x00me", key="rlsx-3")                      # NUL
        r_abs = add("00000000-0000-0000-0000-000000000000", src1, key="rlsx-4")
        r_xo = add(l1, src1, key="rlsx-5", owner="B")                # B adds to A's list
        r_sabs = add(l1, "00000000-0000-0000-0000-000000000000", key="rlsx-6")
        r_sxo = add(l1, bsrc, key="rlsx-7")                          # A binds B's source
        r_rabs = rem("00000000-0000-0000-0000-000000000000", src1, key="rlsx-8")
        a_abs = audit("SELECT count(*) FROM arv.reading_list_member;")
        ok2 = (r_e1.returncode == 1 and "FAIL ARV-RLS-003:" in r_e1.stdout
               and r_e2.returncode == 1 and "FAIL ARV-RLS-003:" in r_e2.stdout
               and r_e3.returncode == 1 and "FAIL ARV-RLS-003:" in r_e3.stdout
               and r_abs.returncode == 1 and "FAIL ARV-RLS-001:" in r_abs.stdout
               and r_xo.returncode == 1 and "FAIL ARV-RLS-001:" in r_xo.stdout
               and r_sabs.returncode == 1 and "FAIL ARV-RLS-002:" in r_sabs.stdout
               and r_sxo.returncode == 1 and "FAIL ARV-RLS-002:" in r_sxo.stdout
               and r_rabs.returncode == 1 and "FAIL ARV-RLS-001:" in r_rabs.stdout
               and a_abs == "0")
        # the no-oracle: absent vs cross-owner BYTE-EQUAL (never an existence leak)
        ok2 = ok2 and r_abs.stdout == r_xo.stdout and r_sabs.stdout == r_sxo.stdout
        check("RLS-02", ok2,
              "the typed refusals + the zero-effect law: the empty name, the >512 name, "
              "and the NUL-carrying name refuse ARV-RLS-003 (never clamped); the absent "
              "list at the add/remove and the cross-owner list refuse ARV-RLS-001 (the "
              "no-oracle — byte-equal for absent vs cross-owner, never an existence "
              "leak); the absent source and the cross-owner source at the membership "
              "refuse ARV-RLS-002 (the no-oracle at the binding); every refusal leaves "
              "ZERO rows",
              "commands.py's typed boundary checks before the spine + the substrate "
              "guards (the composite FKs) — the refusal classes named, zero effect each")

        # ---- RLS-03 — the membership event machine
        r_a1 = add(l1, src1, key="rls-3")
        g1 = jlines(get_list("A", l1))
        r_r1 = rem(l1, src1, key="rls-4")
        g2 = jlines(get_list("A", l1))
        r_a2 = add(l1, src1, key="rls-5")            # re-add after remove
        g3 = jlines(get_list("A", l1))
        ev = audit_rows("SELECT op FROM arv.reading_list_member WHERE list_id = '" + l1 +
                        "' ORDER BY created_at, id;")
        # idempotency: same key+body -> replayed; same key+different body -> 409
        r_rep = add(l1, src1, key="rls-5")
        ack_rep = next((ln for ln in r_rep.stdout.splitlines() if ln.startswith("ACK")), "")
        r_409 = add(l1, src2, key="rls-5")
        # the crash arm: post-commit-pre-ack exits 2, the effect committed, the replay converges
        r_cr = add(l1, src2, key="rls-6", crash_at="post-commit-pre-ack")
        g_cr = jlines(get_list("A", l1))
        r_conv = add(l1, src2, key="rls-6")
        ack_conv = next((ln for ln in r_conv.stdout.splitlines() if ln.startswith("ACK")), "")
        ev_final = audit_rows("SELECT op FROM arv.reading_list_member WHERE list_id = '" + l1 +
                              "' ORDER BY created_at, id;")
        ok3 = (r_a1.returncode == 0 and "status=committed" in r_a1.stdout
               and len(g1) == 1 and g1[0].get("source_id") == src1
               and r_r1.returncode == 0
               and g2 == []                                   # hidden after remove
               and r_a2.returncode == 0
               and len(g3) == 1 and g3[0].get("source_id") == src1   # reactivated
               and ev == ["added", "removed", "added"]        # the EVENT history complete
               and r_rep.returncode == 0 and "status=replayed" in ack_rep
               and r_409.returncode == 1 and "FAIL ARV-CMD-409:" in r_409.stdout
               and r_cr.returncode == 2
               and len(g_cr) == 2 and {r.get("source_id") for r in g_cr} == {src1, src2}
               and r_conv.returncode == 0 and "status=replayed" in ack_conv
               and ev_final == ["added", "removed", "added", "added"]
               and all(r.get("api_version") == 1 for r in g3))
        check("RLS-03", ok3,
              "the membership event machine: add appends the 'added' event (the current "
              "view answers the member); remove appends the 'removed' event (the current "
              "view hides the member, the event history keeps it); re-add after remove "
              "appends a NEW 'added' event (a new row, never a mutation — reactivated); "
              "the idempotency (same key+body -> replayed, the same result_ref; same "
              "key+different body -> ARV-CMD-409, zero effect); the crash matrix's "
              "lost-ack arm (post-commit-pre-ack exits 2, the effect committed, the "
              "same-key replay converges)",
              "the append-only membership event rows + the derived current view (the "
              "last op per pair wins) — every transition a NEW event row, the history "
              "reconstructable from the events alone (RTM §2 item 9)")

        # ---- RLS-04 — the read arms' contract + the owner isolation
        r_l0 = query("list-lists", "--owner", "A", "--limit", "0")
        r_l1001 = query("list-lists", "--owner", "A", "--limit", "1001")
        r_lnan = query("list-lists", "--owner", "A", "--limit", "x")
        # pagination: 4 lists total for A, walk at limit 2 (the --after keyset form)
        mklist("P3", key="rls-7")
        mklist("P4", key="rls-8")
        r_walk1 = query("list-lists", "--owner", "A", "--limit", "2")
        b1, h1, m1 = page(r_walk1)
        r_walk2 = query("list-lists", "--owner", "A", "--limit", "2", "--after", b1[-1]) if b1 else r_walk1
        b2, h2, m2 = page(r_walk2)
        union = sorted(json.loads(ln).get("name") for ln in b1 + b2)
        counts_honest = all(isinstance(json.loads(ln).get("member_count"), int) for ln in b1)
        # B's isolation: B's own list, invisible to A
        r_lb = mklist("B's List", key="rlsb-1", owner="B")
        lb = ref_of(r_lb)
        r_badd = add(lb, bsrc, key="rlsb-2", owner="B")
        g_b = jlines(get_list("B", lb))
        g_a_on_b = get_list("A", lb)
        g_absent = get_list("A", "00000000-0000-0000-0000-000000000000")
        # the empty list's honest answer + the get-list bounds
        r_ge = get_list("A", l2)
        ge_page = page(r_ge)
        r_g0 = get_list("A", l1, "--limit", "0")
        ok4 = (r_l0.returncode == 1 and "FAIL ARV-QRY-004:" in r_l0.stdout
               and r_l1001.returncode == 1 and "FAIL ARV-QRY-004:" in r_l1001.stdout
               and r_lnan.returncode == 1 and "FAIL ARV-QRY-004:" in r_lnan.stdout
               and r_walk1.returncode == 0 and len(b1) == 2 and m1 == "# more=true"
               and r_walk2.returncode == 0 and len(b2) == 2 and m2 == "# more=false"
               and union == sorted([NAME, NAME, "P3", "P4"])   # exact, no dups
               and counts_honest
               and r_lb.returncode == 0 and r_badd.returncode == 0
               and len(g_b) == 1 and g_b[0].get("source_id") == bsrc
               and g_a_on_b.returncode == 1 and "FAIL ARV-QRY-001:" in g_a_on_b.stdout
               and g_absent.returncode == 1 and "FAIL ARV-QRY-001:" in g_absent.stdout
               and g_a_on_b.stdout == g_absent.stdout           # the byte-equal no-oracle
               and r_ge.returncode == 0 and ge_page[1] != "" and "more=false" in ge_page[2]
               and r_g0.returncode == 1 and "FAIL ARV-QRY-004:" in r_g0.stdout)
        check("RLS-04", ok4,
              "the read arms' contract + the owner isolation: list-lists bounded and "
              "paginated (the ARV-QRY-004 bounds refusals 0/1001/not-an-integer; the "
              "keyset walk at --limit 2 with the union exact, no dups; the derived "
              "member counts; the version header; the empty list's two-line answer — "
              "never pure silence); get-list answers the CURRENT membership (one row per "
              "active member); the no-oracle byte-equal (absent vs cross-owner — never "
              "an existence leak); owner B sees only B's lists",
              "query.py list-lists/get-list on the _list_arm keyset contract + the "
              "shared _page_args bounds — the P4-00b bounded-response law")

        # ---- RLS-05 — the 0017 substrate conventions + the registry rows
        rls_on = audit("SELECT relrowsecurity::int || '|' || relforcerowsecurity::int "
                       "FROM pg_class WHERE oid = 'arv.reading_list'::regclass;")
        mem_on = audit("SELECT relrowsecurity::int || '|' || relforcerowsecurity::int "
                       "FROM pg_class WHERE oid = 'arv.reading_list_member'::regclass;")
        pol = audit("SELECT count(*) FROM pg_policies WHERE schemaname = 'arv' "
                    "AND tablename IN ('reading_list', 'reading_list_member') "
                    "AND policyname = 'owner_isolation';")
        grants = audit("SELECT count(*) FROM information_schema.role_table_grants "
                       "WHERE table_schema = 'arv' AND table_name = 'reading_list' "
                       "AND grantee = 'arv_app' AND privilege_type IN ('INSERT', 'SELECT');")
        grants_m = audit("SELECT count(*) FROM information_schema.role_table_grants "
                         "WHERE table_schema = 'arv' AND table_name = 'reading_list_member' "
                         "AND grantee = 'arv_app' AND privilege_type IN ('INSERT', 'SELECT');")
        defs = audit("SELECT count(*) FROM information_schema.columns "
                     "WHERE table_schema = 'arv' AND table_name IN "
                     "('reading_list', 'reading_list_member') "
                     "AND column_default IS NOT NULL;")
        # the hostile direct-SQL matrix (as arv_app, the no-bypass form)
        h_upd = app_sql("UPDATE arv.reading_list SET name = 'x' WHERE id = '" + l1 + "';")
        h_del = app_sql("DELETE FROM arv.reading_list_member WHERE list_id = '" + l1 + "';")
        h_op = app_sql("INSERT INTO arv.reading_list_member (id, list_id, source_id, "
                       "owner_scope, op, actor, run_id, input_hash, idempotency_key, "
                       "created_at) VALUES ('11111111-1111-1111-1111-111111111111', "
                       f"'{l1}', '{src1}', 'A', 'purged', 'owner', 'run-hostile', "
                       "'deadbeef', 'hostile-1', now());")
        h_fk = app_sql("INSERT INTO arv.reading_list_member (id, list_id, source_id, "
                       "owner_scope, op, actor, run_id, input_hash, idempotency_key, "
                       "created_at) VALUES ('22222222-2222-2222-2222-222222222222', "
                       "'33333333-3333-3333-3333-333333333333', '" + src1 + "', 'A', "
                       "'added', 'owner', 'run-hostile', 'deadbeef', 'hostile-2', now());")
        cap_row = cap("surfaces")
        has_cap = '"reading-lists"' in cap_row.stdout
        cr_member = subprocess.run([sys.executable, str(REPO / "harness" / "crash.py"),
                                    "--command", "create_reading_list", "--point",
                                    "pre-commit", "--owner", "A", "--actor", "owner",
                                    "--client-id", "cli-c", "--idem-key", "cr-1",
                                    "--name", "The Crash List"], capture_output=True,
                                   text=True, timeout=120, env=ENV)
        ok5 = (rls_on == "1|1" and mem_on == "1|1" and pol == "2"
               and grants == "2" and grants_m == "2" and defs == "0"
               and h_upd.returncode != 0 and "ARV-RLS-006" in h_upd.stderr
               and h_del.returncode != 0 and "ARV-RLS-007" in h_del.stderr
               and h_op.returncode != 0 and "reading_list_member_op_check" in h_op.stderr
               and h_fk.returncode != 0
               and cap_row.returncode == 0 and has_cap
               and cr_member.returncode == 2)
        check("RLS-05", ok5,
              "the 0017 substrate conventions + the registry rows: RLS enabled AND forced "
              "+ the owner_isolation policy on both tables; the grants (INSERT+SELECT "
              "arv_app, SELECT arv_read, no UPDATE/DELETE); the op CHECK by name "
              "(added|removed); the append-only triggers refusing UPDATE "
              "(ARV-RLS-006) and DELETE (ARV-RLS-007); the composite FKs refusing the "
              "phantom list; NO DEFAULTs (LAW-24); capability.py's reading-lists "
              "reserved-surface row; crash.py's command membership (the crash arm "
              "answers exit 2 — the vocabulary)",
              "migration 0017 on the 0015/0016 substrate pattern + the registry rows — "
              "the substrate laws structural, never command-path-only")

        # ---- RLS-06 — the outbox enqueue (the delivery pin at SYN-22)
        # the suite's committed list traffic: A's creates rls-1/2/7/8 (4) + B's
        # create rlsb-1 (1) + the membership writes rls-3/4/5/6 (4, the crash arm
        # COMMITTED so its row exists) + B's add rlsb-2 (1) = 10 total, 8 A's; the
        # refusals (RLS-02), the replays and the 409 (RLS-03), and the pre-commit
        # crash (RLS-05) add NONE — the spine's own atomic law
        ob_rows = audit("SELECT count(*) FROM arv.outbox WHERE command_name IN "
                        "('create_reading_list', 'add_to_list', 'remove_from_list');")
        ob_a = audit("SELECT count(*) FROM arv.outbox WHERE owner_scope = 'A' AND "
                     "command_name IN ('create_reading_list', 'add_to_list', "
                     "'remove_from_list');")
        ok6 = (int(ob_rows) == 10 and int(ob_a) == 8)
        check("RLS-06", ok6,
              "the outbox enqueue (the CLAIM-073 law's enqueue half — the delivery pin "
              "at the sync suite's SYN-22, the outbox-carrying set's acceptance home): "
              "every committed list write carries its client-outbox row in the SAME "
              "transaction — the observed count 10 (A's 4 creates + A's 4 membership "
              "writes incl. the crash-committed one + B's create + B's add; the "
              "refusals, the replays, the 409, and the pre-commit crash adding NONE — "
              "the spine's own atomic law)",
              "commands.py's _SYNC_COMMANDS membership (create_reading_list + "
              "add_to_list + remove_from_list — the enqueue) riding the SAME slice as "
              "sync.py's delivery branches (the dead-letter law: TOGETHER, never the "
              "enqueue-without-delivery window)")

        print()
        if FAILS:
            print(f"RED — the P4-C slice five suite fails: {', '.join(FAILS)}")
            return 1
        print("READING-LIST SUITE GREEN — RLS-01..06 (the reading-list surface: the "
              "user-defined lists over the landed library — the event-history "
              "membership, the derived current view, the outbox ride)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
