"""harness/tests/test_remote_target.py — CLAIM-088: the guarded remote-target
migration path (runbook §6.2, D-047; RED-first).

The contract (§6.2's seven rules, each with its named refusal):
  ARV-RMT-001  remote mode is EXPLICIT: without ARV_REMOTE_TARGET the adapter
               stays loopback-only (the guard preserved, never deleted);
  ARV-RMT-002  the exact expected project ref/host is CONFIRMED: a target whose
               host does not resolve the pinned ref form is refused BY NAME
               before any connection;
  ARV-RMT-003  TLS certificate verification is REQUIRED: a target without TLS
               is refused;
  ARV-RMT-004  no silent fallback: a refused remote target never retries at
               localhost or another database (the refusal is terminal);
  ARV-RMT-005  credentials are never logged: the DSN's password component is
               never echoed (refusal text redacts it);
  ARV-RMT-006  the migrator's remote mode is a distinct explicit flag: plain
               `migrate` stays local-only (`make migrate` unchanged);
  ARV-RMT-007  the local chain is untouched: the loopback guard still fires on
               a non-loopback host WITHOUT remote mode (the preserved law).

No network is needed for these tests: they exercise the CONFIG resolution and
the refusals (the guards fire BEFORE any connection is attempted — the point
of §6.2's "tests prove it cannot silently select the wrong database").
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from harness.adapters import pg  # noqa: E402

PINNED_REF = "wcuuakhdmsmmxagvbdmg"
PINNED_HOST = "aws-0-ap-south-1.pooler.supabase.com"


def _clean_env():
    """The tests must see a deterministic environment (LAW-24 hygiene)."""
    for k in ("ARV_REMOTE_TARGET", "PGHOST", "PGPORT", "PGUSER", "PGDATABASE"):
        os.environ.pop(k, None)


class TestRemoteTargetGuards(unittest.TestCase):
    def setUp(self):
        _clean_env()

    def tearDown(self):
        _clean_env()

    # ARV-RMT-001: no remote target -> the adapter stays loopback-only
    def test_01_no_remote_mode_stays_loopback(self):
        os.environ["PGHOST"] = "10.0.0.9"  # non-loopback WITHOUT remote mode
        r = pg.psql("SELECT 1;", db="postgres")
        self.assertEqual(r.returncode, 125)
        self.assertIn("ARV-DB-004", r.stderr)

    # ARV-RMT-002: the pinned ref form is confirmed BY NAME
    def test_02_wrong_ref_refused_by_name(self):
        os.environ["ARV_REMOTE_TARGET"] = "wcuuakhdmsmmxagvbdXX"  # wrong ref
        r = pg.psql("SELECT 1;", db="postgres")
        self.assertEqual(r.returncode, 125)
        self.assertIn("ARV-RMT-002", r.stderr)
        self.assertIn(PINNED_REF, r.stderr)  # names the expected, not just the refusal

    # ARV-RMT-002: a host that is not the pooler host is refused even with the right ref
    def test_03_wrong_host_refused_by_name(self):
        os.environ["ARV_REMOTE_TARGET"] = PINNED_REF
        os.environ["PGHOST"] = "db.example-attacker.com"  # not the approved pooler host
        r = pg.psql("SELECT 1;", db="postgres")
        self.assertEqual(r.returncode, 125)
        self.assertIn("ARV-RMT-002", r.stderr)

    # ARV-RMT-003: TLS is required on the remote path
    def test_04_remote_without_tls_refused(self):
        os.environ["ARV_REMOTE_TARGET"] = PINNED_REF
        os.environ["PGHOST"] = PINNED_HOST
        os.environ["ARV_REMOTE_SSLMODE"] = "prefer"  # not verification
        r = pg.psql("SELECT 1;", db="postgres")
        self.assertEqual(r.returncode, 125)
        self.assertIn("ARV-RMT-003", r.stderr)

    # ARV-RMT-005: credentials never appear in any refusal or echo
    def test_05_password_redacted_in_refusals(self):
        os.environ["ARV_REMOTE_TARGET"] = PINNED_REF + ":5432:postgres:secret-password-xyz"  # wrong shape + a secret
        r = pg.psql("SELECT 1;", db="postgres")
        self.assertEqual(r.returncode, 125)
        self.assertNotIn("secret-password-xyz", r.stderr)
        self.assertNotIn("secret-password-xyz", r.stdout)

    # ARV-RMT-004: a refused remote target never falls back to loopback
    def test_06_no_fallback_to_localhost(self):
        os.environ["ARV_REMOTE_TARGET"] = "wrong-ref-abc"
        r = pg.psql("SELECT 1;", db="postgres")
        # the refusal is terminal: the stderr names the remote refusal, NOT a
        # loopback retry (and never a "could not connect" from a local attempt)
        self.assertEqual(r.returncode, 125)
        self.assertIn("ARV-RMT-002", r.stderr)
        self.assertNotIn("127.0.0.1", r.stderr)
        self.assertNotIn("localhost", r.stderr)

    # ARV-RMT-006: the migrator's plain run stays local-only (config-level proof)
    def test_07_migrator_plain_run_is_local(self):
        cfg = pg.config()
        self.assertIn(cfg["PGHOST"], pg.LOOPBACK)  # plain mode: loopback default holds

    # ARV-RMT-007: the loopback guard still fires WITHOUT remote mode
    def test_08_loopback_guard_preserved(self):
        os.environ["PGHOST"] = "db.wcuuakhdmsmmxagvbdmg.supabase.co"  # non-loopback, no remote mode
        r = pg.psql("SELECT 1;", db="postgres")
        self.assertEqual(r.returncode, 125)
        self.assertIn("ARV-DB-004", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
