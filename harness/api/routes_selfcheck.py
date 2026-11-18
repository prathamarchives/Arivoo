#!/usr/bin/env python3
"""harness/api/routes_selfcheck.py — the route battery (CLAIM-092; in-boundary:
fastapi lives only in harness/api/). Drives the raw ASGI interface (stdlib
asyncio; httpx deliberately absent). The JwksCache seam is a TEST seam (a
patched refresh serving the test JWK) — the product module is untouched."""
import asyncio
import base64
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from harness.api.app import create_app
from harness.api import auth as _auth

FAILS = []

def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        FAILS.append(code)

async def call(app, method, path, headers=None):
    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
             "method": method, "scheme": "http", "path": path,
             "raw_path": path.encode(), "query_string": b"", "root_path": "",
             "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
             "client": ("127.0.0.1", 0), "server": ("testserver", 80)}
    sent = []
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    async def send(m):
        if m["type"] == "http.response.start":
            sent.append(("status", m["status"]))
        elif m["type"] == "http.response.body":
            sent.append(("body", m.get("body", b"")))
    await app(scope, receive, send)
    status = [v for k, v in sent if k == "status"][0]
    body = b"".join(v for k, v in sent if k == "body").decode()
    return status, body

def main() -> int:
    import jwt as pyjwt
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    priv = ec.generate_private_key(ec.SECP256R1())
    raw = priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    jwk = {"kty": "EC", "crv": "P-256", "kid": "test-key-1", "alg": "ES256",
           "x": b64(raw[1:33]), "y": b64(raw[33:65])}
    cfg = _auth.AuthConfig(issuer="https://test-issuer/auth/v1", audience="test-aud",
                           jwks_url="https://test-jwks/.well-known/jwks.json",
                           expected_kid="test-key-1")

    # THE TEST SEAM: the JwksCache's refresh serves the test JWK (the product
    # module itself is untouched; the seam exists so the battery can hold the
    # pinned-key positive path without possessing Supabase's private key).
    orig_refresh = _auth._JwksCache._refresh
    def fake_refresh(self):
        self._jwk = jwk
        self._fetched_at = time.monotonic()
    _auth._JwksCache._refresh = fake_refresh
    try:
        app = create_app(health_auth_ready=True, health_db_ready=True)
        s, b = asyncio.run(call(app, "GET", "/health/live"))
        check("ARV-ROUTE-001", s == 200 and '"live"' in b,
              "liveness answers 200 with no dependencies")
        app_nr = create_app()
        s, b = asyncio.run(call(app_nr, "GET", "/health/ready"))
        check("ARV-ROUTE-002", s == 503 and "not-ready" in b,
              "readiness is 503 until the service declares ready")
        s, b = asyncio.run(call(app, "GET", "/health/ready"))
        check("ARV-ROUTE-003", s == 200 and "ready" in b,
              "readiness is 200 once declared ready (auth + db state honest)")
        s, b = asyncio.run(call(app, "GET", "/api/v1/me"))
        check("ARV-ROUTE-004", s == 401, "an unauthenticated product route is 401")
        d = {}
        try:
            d = json.loads(b)
        except Exception:
            pass
        err = d.get("error", {})
        check("ARV-ROUTE-005", err.get("code") == "ARV-AUTH-001" and "api_version" in b
              and "Traceback" not in b,
              "the error body carries the named code + api_version, never a stack trace")
        tok = pyjwt.encode({"sub": "route-user", "iss": cfg.issuer, "aud": cfg.audience,
                            "exp": int(time.time()) + 600, "iat": int(time.time())},
                           priv, algorithm="ES256", headers={"kid": "test-key-1"})
        app_t = create_app(auth_config=cfg, health_auth_ready=True, health_db_ready=True)
        s, b = asyncio.run(call(app_t, "GET", "/api/v1/me",
                                 {"Authorization": "Bearer " + tok}))
        check("ARV-ROUTE-006", s == 200 and "route-user" in b,
              "a verified token reaches /api/v1/me and derives the owner from the sub")
        s, b = asyncio.run(call(app, "GET", "/api/v1/openapi.json"))
        check("ARV-ROUTE-007", s == 200 and '"openapi"' in b[:200],
              "the OpenAPI document exists at /api/v1/openapi.json (generated from the code)")
    finally:
        _auth._JwksCache._refresh = orig_refresh
    print()
    if FAILS:
        print("RED — the routes battery refuses: " + ", ".join(FAILS))
        return 1
    print("GREEN — the routes battery passes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
