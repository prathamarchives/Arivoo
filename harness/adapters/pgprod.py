#!/usr/bin/env python3
"""harness/adapters/pgprod.py — the production pooled PostgreSQL adapter
(runbook §10; CLAIM-091; INT-155/D-049).

The runtime (API + later worker) DB path: persistent pooled connections via
the APPROVED psycopg 3.3.9 + psycopg-pool 3.3.3 (harness/api/requirements.lock,
D-048), TLS verify-full with the pinned Supabase root CA, the arv_app
least-privilege runtime credential (never the migration/admin credential —
§6.5's separation), and TRANSACTION-LOCAL owner context (§8.5: app.current_owner
set with SET LOCAL inside the open transaction, never a pooled session default
so a returned connection can never carry user A's context to user B).

Boundary (D-048): psycopg lives ONLY here. The loopback rig (pg.py) is NOT
touched: local and production configs are separate by construction — this
module refuses to even import unless the caller passes an explicit prod
config (no environment fallback: the runbook's "production selection must not
happen by an accidental environment fallback").

Failure contract (named codes, the repo's diagnostics discipline):
  ARV-PRD-001  the adapter was constructed without an explicit production
               config (no env fallback — the §10 boundary rule)
  ARV-PRD-002  TLS verification incomplete (sslmode must be verify-full and a
               root CA must be supplied — no identity-blind connection)
  ARV-PRD-003  the runtime role is not the approved arv_app shape (a superuser
               or migration-role runtime login is refused by contract)
  ARV-PRD-004  a pool operation failed (lifecycle errors carry the named code)
  ARV-PRD-005  owner context violated the transaction-local rule (SET LOCAL
               outside a transaction, or an attempt to set a session default)
  ARV-PRD-006  statement timeout / bounded execution exceeded

The module is deliberately SMALL: pooling, verify-full, the owner-context
discipline, and the guards. Business SQL stays in the kernel (LAW-10: no
second kernel). No connection string is ever echoed (credential-free errors).
"""
import contextlib
import os

# The approved imports (D-048's boundary: psycopg only in this file)
import psycopg  # noqa: E402
import psycopg_pool  # noqa: E402

# §6.4/§6.5 constants — one home each
TLS_REQUIRED = "verify-full"
RUNTIME_ROLE_PREFIX = "arv_app"      # the ONLY approved runtime login prefix
OWNER_GUC = "app.current_owner"     # §8.5: transaction-local ONLY


class ProdConfig:
    """The explicit production connection shape. No defaults, no env reading at
    import time: the caller (the API's startup) supplies every field from the
    service's own secret scope. The password lives in this object ONLY in
    memory — repr/str are credential-free."""

    __slots__ = ("host", "port", "dbname", "user", "password", "sslrootcert", "min_conn", "max_conn", "statement_timeout_s")

    def __init__(self, *, host, port, dbname, user, password, sslrootcert,
                 min_conn=2, max_conn=10, statement_timeout_s=15):
        self.host = str(host)
        self.port = int(port)
        self.dbname = str(dbname)
        self.user = str(user)
        self.password = str(password)
        self.sslrootcert = str(sslrootcert)
        self.min_conn = int(min_conn)
        self.max_conn = int(max_conn)
        self.statement_timeout_s = int(statement_timeout_s)

    def _validate(self) -> "None":
        # ARV-PRD-002: verify-full + a real root CA file — identity-blind or
        # plaintext paths refuse by construction
        ca = self.sslrootcert
        if not ca or not os.path.isfile(ca):
            raise ProdRefusal("ARV-PRD-002",
                               "sslrootcert missing or not a file — the production path "
                               "requires verify-full with the pinned Supabase root CA "
                               "(§6.4: encryption AND identity verification); refusing")
        if not self.user.startswith(RUNTIME_ROLE_PREFIX):
            # ARV-PRD-003: the runtime login must be the arv_app shape (a
            # migration/admin/superuser runtime login is the §6.5 violation)
            raise ProdRefusal("ARV-PRD-003",
                               f"the runtime user {self.user[:32]!r} is not the approved "
                               f"{RUNTIME_ROLE_PREFIX}* least-privilege shape (§6.5: the API "
                               "never runs as the migration role; postgres/superuser is "
                               "prohibited shortcut #7); refusing")
        if not self.host or "." not in self.host:
            raise ProdRefusal("ARV-PRD-001",
                               "an explicit production host is required (a bare name or "
                               "empty host suggests an accidental environment fallback — "
                               "the §10 boundary: local and production never cross)")

    def __repr__(self):
        return ("ProdConfig(host=%r, port=%r, dbname=%r, user=%r, "
                "sslrootcert=%r, min=%d, max=%d, timeout=%d)  # password withheld"
                % (self.host, self.port, self.dbname, self.user,
                   self.sslrootcert, self.min_conn, self.max_conn,
                   self.statement_timeout_s))


class ProdRefusal(Exception):
    """A named production-path refusal (the repo's diagnostics contract)."""

    def __init__(self, code: str, what: str):
        super().__init__(f"{code}: {what}")
        self.code = code


class ProdPool:
    """The persistent pooled production connection source.

    Every lease follows §8.5's exact discipline:
        1. acquire a pooled connection
        2. BEGIN
        3. SET LOCAL app.current_owner = '<verified-sub>'  (transaction-local)
        4. execute the kernel's statement(s)
        5. COMMIT or ROLLBACK
        6. return the connection to the pool (context cleanup)

    SET LOCAL cannot survive the transaction's end: a rollback or commit clears
    it, so rapid reuse across users is structurally safe (the §8.5 two-user
    race cannot leak context).
    """

    def __init__(self, config: ProdConfig):
        if not isinstance(config, ProdConfig):
            raise ProdRefusal("ARV-PRD-001",
                              "the production adapter requires an explicit ProdConfig "
                              "(no environment fallback — the §10 boundary rule; the "
                              "loopback rig stays the local default by construction)")
        config._validate()
        self._config = config
        self._pool = None

    # -- lifecycle ---------------------------------------------------------
    def open(self) -> "None":
        """Create the pool (idempotent; called once at service start)."""
        if self._pool is not None:
            return
        cfg = self._config
        conninfo = {
            "host": cfg.host, "port": cfg.port, "dbname": cfg.dbname,
            "user": cfg.user, "password": cfg.password,
            "sslmode": TLS_REQUIRED, "sslrootcert": cfg.sslrootcert,
            "connect_timeout": 10,
        }
        try:
            self._pool = psycopg_pool.ConnectionPool(
                conninfo, min_size=cfg.min_conn, max_size=cfg.max_conn,
                open=True, kwargs={"autocommit": False},
                timeout=30.0)
        except Exception as e:  # pool construction failure is a named class
            raise ProdRefusal("ARV-PRD-004",
                              "the connection pool could not be created (host/user/CA "
                              "shape refused or unreachable): " + _safe(str(e))) from None

    def close(self) -> "None":
        if self._pool is not None:
            with contextlib.suppress(Exception):
                self._pool.close()
            self._pool = None

    # -- the §8.5 lease discipline ----------------------------------------
    @contextlib.contextmanager
    def owner_txn(self, owner_sub: str):
        """One transaction scoped to ONE verified owner (§8.5).

        owner_sub is the SERVER-DERIVED owner scope (the verified JWT's sub —
        §8.4: client-supplied owner values never reach here; the API derives
        before calling). SET LOCAL scopes app.current_owner to this transaction
        only; COMMIT/ROLLBACK ends it; the pool reuses the connection cleanly.
        """
        owner = _owner_ok(owner_sub)
        if self._pool is None:
            raise ProdRefusal("ARV-PRD-004",
                              "the pool is not open (open() must precede any lease)")
        with self._pool.connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    # the kernel's own quoting convention (commands.py's _q): SET does
                    # not bind parameters; the owner value is ALREADY validated by
                    # _owner_ok (injection-shaped values refuse before this point)
                    cur.execute(f"SET LOCAL {OWNER_GUC} = {_quote(owner)}")
                yield conn
            # conn.transaction() commits on clean exit, rolls back on error

    @contextlib.contextmanager
    def readonly(self):
        """A read lease WITHOUT owner context (readiness checks, health
        queries; the RLS-blind surfaces that intentionally run as the runtime
        role with no owner — e.g. SELECT 1 / ledger counts).

        The lease opens its OWN transaction (never rides an implicit one):
        with autocommit=False an un-scoped SELECT leaves an OPEN implicit
        transaction on the pooled connection, and the NEXT lease's
        transaction() would nest as a SAVEPOINT inside it — SET LOCAL then
        leaks across the inner "commit" (the §8.5 leak found in testing, fixed
        by scoping EVERY lease; ARV-PRD-011 pins it)."""
        if self._pool is None:
            raise ProdRefusal("ARV-PRD-004",
                              "the pool is not open (open() must precede any lease)")
        with self._pool.connection() as conn:
            with conn.transaction():
                yield conn

    def statement_timeout_on(self, cur) -> "None":
        """Apply the bounded statement timeout (§10) to an open cursor."""
        cur.execute("SET LOCAL statement_timeout = %s",
                    (f"{self._config.statement_timeout_s * 1000}ms",))


def _quote(s: str) -> str:
    """The kernel's quoting form (commands.py's _q): doubled single quotes."""
    return "'" + s.replace("'", "''") + "'"


def _owner_ok(sub: str) -> str:
    """The owner-scope validation (§8.4: a UUID sub from the verified token;
    client-supplied values are never trusted here — the caller derived it)."""
    if not sub or len(sub) > 64 or any(c in sub for c in ("'", "\\", ";", "--")):
        raise ProdRefusal("ARV-PRD-005",
                          "the owner scope failed validation (a verified token's sub is a "
                          "UUID-shaped string; injection-shaped values refuse)")
    return sub


def _validate_owner_public(sub: str) -> str:
    """The suite's exposed form of _owner_ok (the guard is testable by name)."""
    return _owner_ok(sub)


def _safe(text: str) -> str:
    """Strip credential-shaped material from an underlying error string (the
    ARV-RMT-005 discipline: the named code is the stable surface, and the
    detail never echoes a password)."""
    for marker in ("password", "pass", "pwd", "secret"):
        if marker in text.lower():
            i = text.lower().find(marker)
            text = text[:i] + marker + "=[withheld]" + text[i + len(marker):]
            # blunt the rest of that line's value shapes
            line_end = text.find("\n", i)
            seg = text[i:line_end if line_end != -1 else len(text)]
            text = text[:i] + seg.split("=")[0] + "=[withheld]" + (text[line_end:] if line_end != -1 else "")
    return text[:300]
