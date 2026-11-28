#!/usr/bin/env python3
"""harness/tests/test_remote_db_user.py — the production DB path's user contract.

The pooler identifies a tenant from the role name (`<role>.<project-ref>`) or
SNI. The API's read routes pass the bare `arv_app` (correct on the local rig),
which the pooler refuses with ENOIDENTIFIER. This stdlib-only suite proves the
adapter qualifies the user ONLY in the guarded remote mode and leaves the
loopback path byte-identical.
"""
import importlib.util
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
FAILS: list[str] = []


def check(code, ok, what, repair):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        print("      repair: " + repair)
        FAILS.append(code)


def _pg():
    p = REPO / "harness" / "adapters" / "pg.py"
    spec = importlib.util.spec_from_file_location("arivo_pg_under_test", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    pg = _pg()
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "1\n", "")

    old = pg.subprocess.run
    pg.subprocess.run = fake_run
    try:
        os.environ.update({"ARV_REMOTE_TARGET": pg.REMOTE_PINNED_REF,
                           "PGHOST": pg.REMOTE_PINNED_HOST,
                           "PGPORT": pg.REMOTE_PINNED_PORT,
                           "PGUSER": "arv_app." + pg.REMOTE_PINNED_REF,
                           "PGSSLMODE": "verify-full",
                           "PGSSLROOTCERT": "/tmp/nonexistent-ca.pem"})
        r = pg.psql("SELECT 1;", user="arv_app")
        cmd = captured.get("cmd", [])
        check("ARV-RMT-006", r.returncode == 0
              and "-U" in cmd
              and cmd[cmd.index("-U") + 1] == "arv_app." + pg.REMOTE_PINNED_REF,
              "the guarded remote path pooler-qualifies the runtime user (arv_app.<ref>)",
              "map a bare role to '<role>.<pinned ref>' when ARV_REMOTE_TARGET is set")
        check("ARV-RMT-007", "--set=sslmode=verify-full" in cmd,
              "the remote path still carries verify-full with the command",
              "keep the existing TLS pin unchanged")
        os.environ.pop("ARV_REMOTE_TARGET", None)
        os.environ["PGHOST"] = "127.0.0.1"
        os.environ["PGPORT"] = "5433"
        os.environ["PGUSER"] = "arv_app"
        r2 = pg.psql("SELECT 1;", user="arv_app")
        cmd2 = captured.get("cmd", [])
        check("ARV-RMT-008", r2.returncode == 0 and "-U" in cmd2
              and cmd2[cmd2.index("-U") + 1] == "arv_app",
              "the local rig path keeps the bare arv_app user",
              "the mapping must be remote-only — never alter the rig contract")
    finally:
        pg.subprocess.run = old
    print()
    if FAILS:
        print(f"RED — the production DB user contract is broken: {len(FAILS)} check(s) failed.")
        return 1
    print("GREEN — the remote path pooler-qualifies the user; the rig path is unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
