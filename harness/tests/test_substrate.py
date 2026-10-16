#!/usr/bin/env python3
"""harness/tests/test_substrate.py — S2 acceptance suite (Phase 2 Layer 2.1; D-036).

Red-first (LAW-11): committed BEFORE the implementation; the red run fails with
ARV-TEST-011 (waiting-for-harness: the substrate table does not exist) — preserved
in record 18 §4.2.

S2 acceptance (the 2026-10-16 review §7, mapped to named codes):
  (a) UPDATE and DELETE on the evidence table are REJECTED by triggers with the
      named code ARV-EV-001 (LAW-19 analog)                          ARV-TEST-012
  (b) two-owner isolation: owner B's arv_app session sees ZERO of owner A's
      rows (LAW-22 analog); the arv_read auditor sees ALL            ARV-TEST-013
  (c) an unattributed write (no owner_scope / no actor) is REJECTED at
      the schema level (LAW-21 analog)                               ARV-TEST-014
  (d) the independent role reads state the writer cannot influence:
      arv_read reads directly, and arv_app CANNOT alter the read
      boundary (RLS/policy tamper denied)                            ARV-TEST-015
  (e) tombstone: a delete-flag lands as a NEW row; the original stays
      recoverable; the effective view excludes it                    ARV-TEST-016
  (f) revision: a revision lands as a NEW row referencing the
      original; the original is intact                               ARV-TEST-017
  (g) writer-session fail-closed: an arv_app session with NO owner set
      sees/writes nothing (current_owner NULL -> policy false)       ARV-TEST-018
Run: python3 harness/tests/test_substrate.py   (exit 0 = green)
"""
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


try:
    from harness.adapters import pg  # noqa: E402
    from harness.adapters import clock, ids  # noqa: E402
except ImportError as e:  # ARV-TEST-011 (the waiting-for-harness class)
    print("FAIL ARV-TEST-011: the substrate adapters do not exist yet (waiting-for-harness) —", e)
    sys.exit(1)


def sql(db: str, query: str, *, user: str = None, owner: str = None, fail_ok: bool = True) -> subprocess.CompletedProcess:
    """A direct psql invocation (independent of the app path). owner -> PGOPTIONS
    (the session GUC the RLS policy reads — set at connection time, per-session)."""
    env = dict(os.environ)
    if owner is not None:
        env["PGOPTIONS"] = f"-c app.current_owner={owner}"
    cmd = ["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1"]
    if user:
        cmd += ["-U", user]
    cmd += ["-d", db, "-c", query]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)


def ins(db: str, owner: str, *, event_type: str = "event", actor: str = "owner",
        payload: str = "p", omit_owner: bool = False, omit_actor: bool = False,
        ref_id: str = None, run_id: str = "run-test", input_hash: str = "ih-test") -> str:
    """Build+run one INSERT through the APP conventions (ids/clock adapters make
    the ID and the timestamp — LAW-24: no ambient time/IDs in test logic)."""
    i = ids.new_id()
    ts = clock.now()
    cols = ["id", "event_type", "payload", "run_id", "input_hash", "created_at"]
    vals = [f"'{i}'", f"'{event_type}'", f"'{payload}'", f"'{run_id}'", f"'{input_hash}'", f"'{ts}'"]
    if not omit_owner:
        cols.append("owner_scope")
        vals.append(f"'{owner}'")
    if not omit_actor:
        cols.append("actor")
        vals.append(f"'{actor}'")
    if ref_id:
        cols.append("ref_id")
        vals.append(f"'{ref_id}'")
    q = f"INSERT INTO arv.evidence_event ({', '.join(cols)}) VALUES ({', '.join(vals)});"
    r = sql(db, q, user="arv_app", owner=owner, fail_ok=True)
    return i if r.returncode == 0 else None


def main() -> int:
    db = pg.create_scratch_db("s2")
    try:
        # migrate the full chain (0001 + 0002)
        env = dict(os.environ, PGDATABASE=db)
        r = subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                           capture_output=True, text=True, env=env, timeout=120)
        exists = sql(db, "SELECT count(*) FROM information_schema.tables "
                         "WHERE table_schema='arv' AND table_name='evidence_event';").stdout.strip()
        check("ARV-TEST-011", r.returncode == 0 and exists == "1",
              "the substrate-convention table exists after migrate (0001+0002 applied)",
              "apply 0002_evidence_event.sql — the S2 red state is exactly its absence")

        # (a) immutability: TWO layers — the app role lacks the privilege; even a
        #     privileged session (the migrator) hits the trigger's named code
        a = ins(db, "A", payload="alpha")
        ru_app = sql(db, f"UPDATE arv.evidence_event SET payload='x' WHERE id='{a}';", user="arv_app", owner="A")
        ru = sql(db, f"UPDATE arv.evidence_event SET payload='x' WHERE id='{a}';")
        rd = sql(db, f"DELETE FROM arv.evidence_event WHERE id='{a}';")
        check("ARV-TEST-012",
              ru_app.returncode != 0 and "permission denied" in ru_app.stderr
              and ru.returncode != 0 and "ARV-EV-001" in ru.stderr
              and rd.returncode != 0 and "ARV-EV-001" in rd.stderr,
              "mutations are rejected on BOTH layers: arv_app UPDATE = permission denied (no grant), and even the migrator's UPDATE/DELETE hit the trigger's named code ARV-EV-001 (LAW-19 analog)",
              "the BEFORE UPDATE/DELETE trigger must RAISE with 'ARV-EV-001: ...' (guarding even privileged paths), and arv_app must never receive UPDATE/DELETE grants")

        # (b) two-owner isolation + the auditor sees all
        b1 = ins(db, "A", payload="a-row")
        b2 = ins(db, "B", payload="b-row")
        see_b = sql(db, "SELECT count(*) FROM arv.evidence_event;", user="arv_app", owner="B").stdout.strip()
        see_a = sql(db, "SELECT count(*) FROM arv.evidence_event;", user="arv_app", owner="A").stdout.strip()
        audit = sql(db, "SELECT count(*) FROM arv.evidence_event;", user="arv_read").stdout.strip()
        check("ARV-TEST-013", see_b == "1" and see_a == "2" and audit == "3",
              f"owner B sees zero A-rows (B's view={see_b}: only B's own row), owner A sees zero B-rows (A's view={see_a}: A's two rows), arv_read sees all ({audit}) — LAW-22 analog",
              "RLS policy owner_isolation must compare owner_scope to current_setting('app.current_owner', true) for arv_app; arv_read is the BYPASSRLS auditor")

        # (c) unattributed writes rejected at the schema level
        c1 = ins(db, "A", omit_owner=True)
        c2 = ins(db, "A", omit_actor=True)
        check("ARV-TEST-014", c1 is None and c2 is None,
              "writes without owner_scope or without actor are REJECTED (NOT NULL — LAW-21 analog)",
              "owner_scope and actor are NOT NULL; attribution is a schema property, not a convention")

        # (d) the independent read + the writer cannot alter the boundary
        d = ins(db, "A", payload="audited")
        seen = sql(db, f"SELECT payload FROM arv.evidence_event WHERE id='{d}';", user="arv_read").stdout.strip()
        tamper = sql(db, "ALTER TABLE arv.evidence_event DISABLE ROW LEVEL SECURITY;", user="arv_app", owner="A")
        tamper2 = sql(db, "DROP POLICY owner_isolation ON arv.evidence_event;", user="arv_app", owner="A")
        check("ARV-TEST-015", seen == "audited" and tamper.returncode != 0 and tamper2.returncode != 0,
              "arv_read reads the writer's row directly (independent path), and the writer CANNOT disable RLS or drop the policy (permission denied)",
              "the independent read must not depend on any arv_app-controlled code path; DDL on the substrate is migrator-only")

        # (e) tombstone: new row, original recoverable, effective view excludes
        e1 = ins(db, "A", payload="to-retire")
        t = ins(db, "A", event_type="tombstone", ref_id=e1)
        still = sql(db, f"SELECT count(*) FROM arv.evidence_event WHERE id='{e1}';", user="arv_read").stdout.strip()
        eff = sql(db, f"SELECT count(*) FROM arv.evidence_event WHERE id='{e1}' AND event_type='event';",
                  user="arv_read").stdout.strip()
        effview = sql(db, f"SELECT count(*) FROM arv.evidence_event e WHERE e.id='{e1}' "
                          "AND e.event_type='event' "
                          "AND NOT EXISTS (SELECT 1 FROM arv.evidence_event t "
                          "WHERE t.event_type='tombstone' AND t.ref_id = e.id);", user="arv_read").stdout.strip()
        check("ARV-TEST-016", t is not None and still == "1" and eff == "1" and effview == "0",
              f"tombstone lands as a NEW row (original recoverable: still={still}; e1 outside the effective view: {effview} — the view excludes exactly the tombstoned row)",
              "delete = a tombstone row referencing the target; the original is never mutated (ARV-EV-001 guards it)")

        # (f) revision: new row referencing the original; original intact
        f1 = ins(db, "A", payload="v1")
        f2 = ins(db, "A", event_type="revision", ref_id=f1, payload="v2")
        orig = sql(db, f"SELECT payload FROM arv.evidence_event WHERE id='{f1}';", user="arv_read").stdout.strip()
        rev = sql(db, f"SELECT payload FROM arv.evidence_event WHERE id='{f2}';", user="arv_read").stdout.strip()
        check("ARV-TEST-017", f2 is not None and orig == "v1" and rev == "v2",
              "a revision lands as a NEW row referencing the original; the original is intact (append-only revision chain)",
              "revisions are new rows with event_type='revision' and ref_id=original — never an UPDATE (ARV-EV-001)")

        # (g) fail-closed: an app session with NO owner set sees/writes nothing
        blind = sql(db, "SELECT count(*) FROM arv.evidence_event;", user="arv_app").stdout.strip()
        noins = sql(db, f"INSERT INTO arv.evidence_event (id, event_type, payload, owner_scope, actor, run_id, input_hash, created_at) "
                        f"VALUES ('{ids.new_id()}', 'event', 'x', 'A', 'owner', 'r', 'h', '{clock.now()}');",
                    user="arv_app", fail_ok=True)
        check("ARV-TEST-018", blind == "0" and noins.returncode != 0,
              "an arv_app session with no app.current_owner set reads nothing and cannot write (the policy fails closed on NULL)",
              "current_setting('app.current_owner', true) returns NULL when unset — the WITH CHECK must reject, never default to a wildcard owner")

    finally:
        pg.drop_scratch_db(db)

    print()
    if FAILS:
        print(f"RED — {len(FAILS)} failure(s): {', '.join(FAILS)} — S2 acceptance not met")
        return 1
    print("GREEN — S2 acceptance (a)-(g) observed: immutability, owner isolation, attribution, independent reads, tombstone, revision, fail-closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
