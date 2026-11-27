"""harness/api/__main__.py — the `api` start command (Workstream 10).

`python3 -m harness.api` — the uvicorn entry over create_app, reading the
service's runtime environment (the secret matrix's names; the §11.4 law —
every refusal typed, never a crash):
  * ARIVO_API_DB          — the database name (the adapter's boundary)
  * ARIVO_API_HOST/PORT   — the bind (defaults 0.0.0.0:8080)
  * ARIVO_AUTH_ISSUER / ARIVO_AUTH_AUDIENCE / ARIVO_AUTH_JWKS_URL /
    ARIVO_AUTH_KID        — the Supabase auth contract (D-032's platform)
  * ARIVO_ALLOWED_ORIGINS — the CORS matrix (comma-separated; the desktop
                            app's origin among them)
The unconfigured service refuses at startup with the NAMED variable (never a
guess, never a silent default) — the fail-closed law.
"""
import os
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
    app = create_app(auth_config=cfg, health_auth_ready=True, health_db_ready=True)
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
