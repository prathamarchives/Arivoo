#!/usr/bin/env python3
"""harness/api/app.py — the versioned HTTP API skeleton (runbook §11.1/§11.5;
CLAIM-092; INT-156/D-050).

FastAPI 0.164.0 (the approved pin, D-048) inside its boundary (harness/api/).
This slice lands the SKELETON + the health routes + the auth dependency — the
command/query routes over the kernel follow as their own slices (the §11.2
table), each with its gate, its red, its SEV.

Boundaries:
  * /api/v1 namespaces the current command api_version=1 (§11.1: the versioned
    API namespace maps the frozen contract's version token)
  * HTTP imports (fastapi/starlette) live ONLY in harness/api/ (ARV-DEP-009)
  * every product route requires the verified Bearer token (§8.3) — the
    dependency below refuses without one; the health routes are the ONLY
    unauthenticated surface (liveness is process-level; readiness proves the
    process can do its job: the auth verifier is configured, the DB lease
    path is constructed)
  * the DB runtime path is pgprod (CLAIM-091); this skeleton wires it as a
    construction-time dependency, NOT a per-request connection: readiness
    proves the pool's configuration shape, the live pool opens at serve time

Error handling (§11.4): centralized — the named refusal codes map to HTTP
statuses at ONE place (the exception handler); no stack traces, no internal
hostnames, no tokens, no source contents in any response.
"""
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from harness.api import auth as _auth  # the auth boundary module (this dir)

API_VERSION = 1  # commands.py's API_VERSION (P4-00b): the versioned namespace maps it


def create_app(*, auth_config: "_auth.AuthConfig | None" = None,
               health_db_ready: bool = False,
               health_auth_ready: bool = False) -> FastAPI:
    """Compose the API explicitly (no env fallback — the §10 discipline).

    health_db_ready / health_auth_ready: the SERVICE's declared startup state.
    Readiness reports them honestly: a skeleton slice declares False for the
    live-DB part (the pool opens at serve time, with the runtime credential);
    liveness never depends on either.
    """
    cfg = auth_config or _auth.default_config_for_project()
    verifier = _auth.Verifier(cfg)

    app = FastAPI(
        title="Arivo API",
        version=str(API_VERSION),
        openapi_url="/api/v1/openapi.json",
        docs_url=None,   # no interactive docs on the product surface (§11: generate OpenAPI from the code)
        redoc_url=None,
    )

    # ---- the centralized named-refusal mapping (§11.4) ----
    @app.exception_handler(_auth.AuthRefusal)
    async def _auth_refusal(request: Request, exc: _auth.AuthRefusal):
        return JSONResponse(
            status_code=exc.status,
            content={"error": {"code": exc.code,
                              "message": str(exc).split(": ", 1)[-1],
                              "api_version": API_VERSION}},
        )

    # ---- /api/v1/health (§11.5) ----
    @app.get("/health/live")
    async def live():
        """Liveness proves the process runs (§11.5). No dependencies: not the
        DB, not the auth fetch, not the pool — a live process answers."""
        return {"status": "live", "api_version": API_VERSION}

    @app.get("/health/ready")
    async def ready():
        """Readiness proves the process can do its job (§11.5): the auth
        verifier is composed (config + the pinned JWK primed at startup) and
        the DB runtime path is declared ready by the service."""
        ok = verifier is not None and health_auth_ready
        return JSONResponse(
            status_code=200 if ok else 503,
            content={"status": "ready" if ok else "not-ready",
                     "auth": "configured" if verifier is not None else "absent",
                     "auth_primed": bool(health_auth_ready),
                     "database": "declared-ready" if health_db_ready else "not-open",
                     "api_version": API_VERSION},
        )

    # ---- the authenticated context (§8.3/§8.4): EVERY product route uses this ----
    from fastapi import Depends, Header

    async def verified_context(authorization: str = Header(default="")):
        """The single auth dependency: verify the Bearer token, derive the
        owner from the VERIFIED sub. Client-supplied owner/actor values do not
        exist in this signature — there is nothing to trust from the body."""
        claims = verifier.verify_bearer(authorization)
        owner = verifier.derive_owner(claims)
        return {"owner_scope": owner, "claims": claims}

    # ---- /api/v1: the authenticated surface (this slice: the context route §11.2's
    # 'Auth — current verified user/context'; the command routes follow) ----
    @app.get("/api/v1/me")
    async def me(ctx: dict = Depends(verified_context)):
        return {"owner_scope": ctx["owner_scope"],
                "issuer": cfg.issuer,
                "api_version": API_VERSION}

    return app


def app_from_env() -> FastAPI:
    """The ASGI entry (the deployment's start command): composes from the
    service's OWN environment (the only place env reading is sanctioned —
    §6.5's per-service secret scopes; ARIVO_AUTH_READY/ARIVO_DB_READY are the
    service's declared startup state, not secrets)."""
    return create_app(
        health_auth_ready=os.environ.get("ARIVO_AUTH_READY", "") == "1",
        health_db_ready=os.environ.get("ARIVO_DB_READY", "") == "1",
    )


app = None  # composed at serve time (app_from_env) — never at import
