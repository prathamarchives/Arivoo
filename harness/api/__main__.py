"""harness/api/__main__.py — the `api` start command (Workstream 10).

`python3 -m harness.api` — the uvicorn entry over create_app, reading the
service's runtime environment (the secret matrix's names; the §11.4 law —
every refusal typed, never a crash):
  * ARIVO_API_DB          — the database name (the adapter's boundary)
  * ARIVO_API_HOST/PORT   — the bind (defaults 0.0.0.0:8080)
  * ARIVO_AUTH_ISSUER / ARIVO_AUTH_AUDIENCE / ARIVO_AUTH_JWKS_URL /
    ARIVO_AUTH_KID        — the Supabase auth contract (D-032's platform)
  * ARIVO_ALLOWED_ORIGINS — the CORS matrix (comma-separated exact origins;
                             unset means CORS off, never '*')
  * ARIVO_DB_READY          — the runtime DB declaration; must be 1 at start
                             or the service refuses (ARV-SVC-002)
The unconfigured service refuses at startup with the NAMED variable (never a
guess, never a silent default) — the fail-closed law.
"""
import os
import pathlib
import sys


def _require(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"FAIL ARV-SVC-001: the service start requires {name} "
              "(the runtime environment's secret matrix — harness/api/env.example.txt; "
              "no silent defaults at the boundary)")
        sys.exit(1)
    return v


def main() -> int:
    for name in ("ARIVO_API_DB", "ARIVO_AUTH_ISSUER", "ARIVO_AUTH_AUDIENCE",
                 "ARIVO_AUTH_JWKS_URL", "ARIVO_AUTH_KID"):
        _require(name)
    import uvicorn
    from harness.api.app import create_app
    from harness.api import auth as _auth
    host = os.environ.get("ARIVO_API_HOST", "0.0.0.0")
    port = int(os.environ.get("ARIVO_API_PORT", "8080"))
    cfg = _auth.AuthConfig(
        issuer=os.environ["ARIVO_AUTH_ISSUER"],
        audience=os.environ["ARIVO_AUTH_AUDIENCE"],
        jwks_url=os.environ["ARIVO_AUTH_JWKS_URL"],
        expected_kid=os.environ["ARIVO_AUTH_KID"])
    # W-2 (CLAIM-107): readiness is the SERVICE's declaration, never a
    # hardcoded claim. A start without the declared runtime DB path refuses
    # with a named code instead of serving 200 "ready" over a dead DB.
    db_ready = os.environ.get("ARIVO_DB_READY", "") == "1"
    if not db_ready:
        print("FAIL ARV-SVC-002: ARIVO_DB_READY is not 1 — the API refuses to "
              "start claiming database readiness it cannot demonstrate "
              "(deploy/DEPLOYMENT.md's runtime declaration; no silent default)")
        return 1
    # W-2 (CLAIM-107): the production DB path is DECLARED here, not chosen by
    # an accidental libpq fallback. The approved runtime path is pgprod
    # (CLAIM-091: verify-full + pinned CA + arv_app least privilege +
    # transaction-local owner context); pg.psql remains the local rig and
    # migration path. A start missing the declared production shape refuses
    # with ARV-SVC-003. (The per-request pooled executor migration is a named
    # follow-up: it needs a live arv_app credential, which the owner gates.)
    _prod_db = ("PGHOST", "PGUSER", "PGSSLMODE", "PGSSLROOTCERT")
    _missing = [n for n in _prod_db if not os.environ.get(n)]
    if _missing:
        print("FAIL ARV-SVC-003: the production DB path is not declared "
              f"({', '.join(_missing)}) — no local/libpq fallback at the API "
              "boundary (harness/adapters/pgprod.py's §10 rule)")
        return 1
    if os.environ["PGSSLMODE"] != "verify-full":
        print("FAIL ARV-SVC-003: PGSSLMODE must be verify-full (encryption "
              "AND identity verification — §6.4); refusing")
        return 1
    if not os.environ["PGUSER"].startswith("arv_app"):
        print("FAIL ARV-SVC-003: PGUSER must be the arv_app least-privilege "
              "runtime login (never postgres/superuser — §6.5)")
        return 1
    if not pathlib.Path(os.environ["PGSSLROOTCERT"]).is_file():
        print("FAIL ARV-SVC-003: PGSSLROOTCERT names no file — the pinned "
              "Supabase root CA is required for verify-full")
        return 1
    # The CORS matrix is parsed at composition; a malformed origin refuses
    # there with ARV-CORS-001 (harness/api/cors.py).
    app = create_app(auth_config=cfg, health_auth_ready=True,
                     health_db_ready=db_ready)
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
