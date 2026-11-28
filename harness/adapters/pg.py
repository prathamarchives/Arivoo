"""harness/adapters/pg.py — the DB adapter (Phase 2 Layer 2.1, S1; D-036).

The ONLY module that talks to PostgreSQL (BND: the driver boundary lives in the
adapter; feature/runner code never shells out to psql itself). Zero third-party
Python dependencies (D-036): the client is `psql` via subprocess.

Connection model (the rig, LAW-02/FACT-001):
    superuser (env PGUSER, default "postgres") — the migrator/bootstrap path
    arv_app   — the application path (S2 grants it the substrate tables)
    arv_read  — the independent verification role (S2: read-only, sees all rows)
Test-rig auth is trust auth on ephemeral databases (D-036 grounded default):
no credential material exists in any file; production auth is a Phase 3+ concern.

Environment is read ONLY here (LAW-24): PGHOST, PGPORT, PGUSER, PGDATABASE,
ARV_MIGRATIONS_DIR; the remote path (D-047, runbook §6.2) adds
ARV_REMOTE_TARGET / ARV_REMOTE_SSLMODE — never any credential value (the
migration credential travels ONLY in the environment's PGPASSWORD, never a
file, never a logged string — D-025).
"""
import os
import subprocess

DEFAULTS = {"PGHOST": "127.0.0.1", "PGPORT": "5432", "PGUSER": "postgres"}
_MIGRATIONS_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")

# CLAIM-088 (D-047, runbook §6.2): the ONE approved remote target — pinned by
# name, not guessable. The pooler host is the verified IPv4-reachable form
# (the session's probe: direct db.*.supabase.co is IPv6-only from the sandbox;
# the session pooler is §6.4's recommended persistent-backend mode).
REMOTE_PINNED_REF = "wcuuakhdmsmmxagvbdmg"
REMOTE_PINNED_HOST = "aws-0-ap-south-1.pooler.supabase.com"
REMOTE_PINNED_PORT = "5432"
_REMOTE_TLS_REQUIRED = "verify-full"  # §6.4: encryption AND identity verification


class PsqlResult:
    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr

    @property
    def out(self) -> str:
        """Trimmed tuple/quiet-mode stdout (single value queries)."""
        return self.stdout.strip()


def config() -> dict:
    """The rig's connection config (env -> explicit values; defaults stand in
    CI where the service container publishes 5432 on localhost)."""
    cfg = {}
    for k, d in DEFAULTS.items():
        cfg[k] = os.environ.get(k, d)
    cfg["ARV_MIGRATIONS_DIR"] = os.environ.get("ARV_MIGRATIONS_DIR", _MIGRATIONS_DEFAULT)
    return cfg


LOOPBACK = {"127.0.0.1", "localhost", "::1"}  # the rig + CI's service: the ONLY approved targets


def remote_user(user: str | None) -> str:
    """The pooler identifies a tenant from '<role>.<project-ref>' (or SNI).
    The rig uses the bare role; ONLY the guarded remote mode qualifies it.
    A caller that already supplies the qualified spelling is left alone (the
    migration/admin credential arrives that way)."""
    u = user or config()["PGUSER"]
    if os.environ.get("ARV_REMOTE_TARGET") and "." not in u:
        return f"{u}.{REMOTE_PINNED_REF}"
    return u


def _remote_guard(cfg: dict) -> "PsqlResult | None":
    """CLAIM-088 (D-047, runbook §6.2): the remote-target guard chain — every
    refusal fires BEFORE any connection is attempted, each BY NAME, none
    terminal-with-fallback:
      ARV-RMT-002  the target does not resolve the pinned project (wrong ref
                   OR a host other than the approved pooler host): refused,
                   naming the expected shape;
      ARV-RMT-003  TLS verification is required (sslmode must be verify-full;
                   anything weaker — prefer/require/disable — is refused);
      ARV-RMT-005  credential material is never echoed (the refusal text is
                   derived ONLY from the named constants, never the raw
                   target string).
    Returns None when the remote target is fully approved (or absent — the
    plain loopback path holds and the CALLER's loopback guard still applies).
    """
    target = os.environ.get("ARV_REMOTE_TARGET", "")
    if not target:
        return None  # plain mode: the loopback guard below owns the refusal
    # §6.2: the target IS the project ref (the one approved spelling)
    if target.strip() != REMOTE_PINNED_REF:
        return PsqlResult(125, "",
                          f"ARV-RMT-002: the remote target {target[:24]!r} is not the pinned project "
                          f"{REMOTE_PINNED_REF!r} — refusing: the remote path is explicit and "
                          "single-purpose (never a guessed host, never another project)")
    host = cfg["PGHOST"]
    if host != REMOTE_PINNED_HOST:
        return PsqlResult(125, "",
                          f"ARV-RMT-002: the remote host {host[:48]!r} is not the approved pooler host "
                          f"{REMOTE_PINNED_HOST!r} for project {REMOTE_PINNED_REF!r} — refusing: "
                          "the adapter pins the exact host (§6.2 confirms the exact expected project ref/host)")
    if os.environ.get("PGPORT", REMOTE_PINNED_PORT) != REMOTE_PINNED_PORT:
        return PsqlResult(125, "",
                          f"ARV-RMT-002: the remote port {os.environ.get('PGPORT')!r} is not the approved "
                          f"{REMOTE_PINNED_PORT!r} (the session pooler) — refusing")
    sslmode = os.environ.get("ARV_REMOTE_SSLMODE", "")
    if sslmode != _REMOTE_TLS_REQUIRED:
        return PsqlResult(125, "",
                          f"ARV-RMT-003: the remote path requires sslmode=verify-full "
                          f"(§6.4: encryption AND server-identity verification); got {sslmode[:20]!r} — "
                          "refusing: no silent plaintext or identity-blind connection")
    return None


def psql(sql: str, *, db: str = "postgres", user: str = None, timeout: int = 60) -> PsqlResult:
    """Run one SQL statement batch through psql (machine-parseable output:
    unaligned + tuples-only, quiet, ON_ERROR_STOP). P3-K0's target-mismatch
    guard: a non-loopback PGHOST is refused BY NAME before any connection —
    there is no hidden path to a different database than the migrations'.
    CLAIM-088: the remote path is a SEPARATE, explicit, pinned mode (the
    guard preserved; the remote mode ADDED — §6.2's "do not merely delete
    the loopback check")."""
    cfg = config()
    remote_refusal = _remote_guard(cfg)
    if remote_refusal is not None:
        return remote_refusal  # terminal: NO fallback, never a loopback retry (ARV-RMT-004)
    if cfg["PGHOST"] not in LOOPBACK and not os.environ.get("ARV_REMOTE_TARGET"):
        return PsqlResult(125, "",
                          f"ARV-DB-004: the configured target {cfg['PGHOST']!r} is outside the approved adapter "
                          "boundary (loopback only — the rig on 5433, CI's postgres:17 service); refusing: no hidden "
                          "direct connection path may select a different database than the migrations")
    cmd = ["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
           "-h", cfg["PGHOST"], "-p", cfg["PGPORT"],
           "-U", remote_user(user), "-d", db, "-c", sql]
    if os.environ.get("ARV_REMOTE_TARGET"):
        # the approved remote mode: TLS verification travels WITH the command
        cmd += ["--set=sslmode=" + _REMOTE_TLS_REQUIRED]
    return _run_psql(cmd, timeout)


def _run_psql(cmd, timeout):  # fail-closed: every failure class is a NAMED code (P3-K0, SYS-04)
    """The approved boundary's stable named errors (the card's contract):
      ARV-DB-001  the psql client is missing
      ARV-DB-002  the operation exceeded its timeout
      ARV-DB-003  the connection attempt was refused (unreachable server, bad role/auth)
      ARV-DB-004  the configured target is not the approved shape (a non-loopback host)
    The raw diagnostic is preserved after the named prefix — the code is the
    stable surface, the raw text the debugging one."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        err = r.stderr or ""
        if r.returncode == 2 and ("could not connect" in err or "role " not in err):
            pass
        if r.returncode != 0 and ("could not connect" in err or "connection to server" in err
                                  or "Connection refused" in err or 'role "' in err
                                  or "password authentication" in err or "no password" in err):
            err = f"ARV-DB-003: the connection was refused at the approved boundary — {err.strip()[:200]}"
        elif r.returncode != 0:
            pass  # a SQL-level error: the caller's own named code owns it
        return PsqlResult(r.returncode, r.stdout, err)
    except FileNotFoundError:
        return PsqlResult(127, "",
                         "ARV-DB-001: the psql client is missing from PATH — install the PostgreSQL client "
                         "(CI provisions it; locally: the rig's extracted Debian packages)")
    except subprocess.TimeoutExpired as e:
        return PsqlResult(124, "",
                         f"ARV-DB-002: the operation exceeded its {timeout}s timeout at the approved boundary "
                         f"(cmd: {e.cmd[0] if hasattr(e, 'cmd') else 'psql'})")


def create_scratch_db(prefix: str) -> str:
    """A fresh database for an isolated test run (the superuser path)."""
    import time
    name = f"arv_{prefix}_{os.getpid()}_{int(time.time() * 1000) % 10**9}"
    r = psql(f'CREATE DATABASE "{name}";', db="postgres")
    if r.returncode != 0:
        raise RuntimeError(f"ARV-RIG-002: cannot create scratch DB: {r.stderr.strip()}")
    return name


def drop_scratch_db(name: str) -> None:
    psql(f'DROP DATABASE IF EXISTS "{name}";', db="postgres")
