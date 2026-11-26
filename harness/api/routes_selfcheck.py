#!/usr/bin/env python3
"""harness/api/routes_selfcheck.py — the route battery (CLAIM-093 + CLAIM-094;
in-boundary: fastapi lives only in harness/api/). Drives the raw ASGI interface
(stdlib asyncio; httpx deliberately absent). The JwksCache seam is a TEST seam
(a patched refresh serving the test JWK) — the product module is untouched.

CLAIM-094 adds the kernel-backed route checks: the sources/import area against
a REAL migrated scratch db on the local rig (the kernel's own contracts are
exercised end-to-end through the HTTP surface)."""
import asyncio
import base64
import json
import pathlib
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from harness.adapters import clock  # LAW-24

from harness.api.app import create_app
from harness.api import auth as _auth

FAILS = []

def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        FAILS.append(code)

async def call(app, method, path, headers=None, body=b"", query=b""):
    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
             "method": method, "scheme": "http", "path": path,
             "raw_path": path.encode() + (b"?" + query if query else b""),
             "query_string": query, "root_path": "",
             "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
             "client": ("127.0.0.1", 0), "server": ("testserver", 80)}
    sent = []
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}
    async def send(m):
        if m["type"] == "http.response.start":
            sent.append(("status", m["status"]))
        elif m["type"] == "http.response.body":
            sent.append(("body", m.get("body", b"")))
    await app(scope, receive, send)
    status = [v for k, v in sent if k == "status"][0]
    body_s = b"".join(v for k, v in sent if k == "body").decode()
    return status, body_s


def _token(priv, cfg, kid, sub="route-user"):
    import jwt as pyjwt
    return pyjwt.encode({"sub": sub, "iss": cfg.issuer, "aud": cfg.audience,
                         "exp": clock.now_s() + 600, "iat": clock.now_s()},
                        priv, algorithm="ES256", headers={"kid": kid})


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

    orig_refresh = _auth._JwksCache._refresh
    def fake_refresh(self):
        self._jwk = jwk
        self._fetched_at = clock.mono()
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
        d = json.loads(b)
        err = d.get("error", {})
        check("ARV-ROUTE-005", err.get("code") == "ARV-AUTH-001" and "api_version" in b
              and "Traceback" not in b,
              "the error body carries the named code + api_version, never a stack trace")
        tok = _token(priv, cfg, "test-key-1")
        app_t = create_app(auth_config=cfg, health_auth_ready=True, health_db_ready=True)
        s, b = asyncio.run(call(app_t, "GET", "/api/v1/me",
                                 {"Authorization": "Bearer " + tok}))
        check("ARV-ROUTE-006", s == 200 and "route-user" in b,
              "a verified token reaches /api/v1/me and derives the owner from the sub")
        s, b = asyncio.run(call(app, "GET", "/api/v1/openapi.json"))
        check("ARV-ROUTE-007", s == 200 and '"openapi"' in b[:200],
              "the OpenAPI document exists at /api/v1/openapi.json (generated from the code)")

        # ---------------- CLAIM-094: the kernel-backed routes ----------------
        import subprocess, os
        env = dict(os.environ)
        env.update({"PATH": "/home/z/my-project/pgbuild/root/usr/lib/postgresql/17/bin:/usr/local/bin:/usr/bin:/bin",
                    "LD_LIBRARY_PATH": "/home/z/my-project/pgbuild/root/usr/lib/x86_64-linux-gnu:/home/z/my-project/pgbuild/root/usr/lib",
                    "PGHOST": "127.0.0.1", "PGPORT": "5433", "PGUSER": "postgres"})
        def psql(db, sql):
            return subprocess.run(["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                                   "-h", "127.0.0.1", "-p", "5433", "-U", "postgres", "-d", db,
                                   "-c", sql], capture_output=True, text=True, timeout=60,
                                  env=env)
        db = psql("postgres", "SELECT 'arv_r094_'||floor(random()*100000)::text").stdout.strip()
        psql("postgres", f"CREATE DATABASE {db}")
        r = subprocess.run(["python3", "harness/migrate.py"], cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                           capture_output=True, text=True, timeout=300,
                           env=dict(env, PGDATABASE=db, ARV_MIGRATIONS_DIR="harness/migrations"))
        check("ARV-API-001", r.returncode == 0,
              "the route battery's scratch db migrated (the kernel-backed tests run on the real stack)")
        try:
            os.environ["ARIVO_API_DB"] = db
            app_k = create_app(auth_config=cfg, health_auth_ready=True, health_db_ready=True)
            H = {"Authorization": "Bearer " + tok}

            # 1) the import write: the idem key required (§11.3)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports", H, body=b"hello arivo"))
            check("ARV-API-002", s == 400 and "Idempotency-Key" in b,
                  "the write route refuses without the idempotency key (the §11.3 law)")
            # 2) the import write: title XOR work-id (the kernel's ARV-CAP-007 law)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                     dict(H, **{"Idempotency-Key": "k-094-a"}),
                                     body=b"hello arivo"))
            check("ARV-API-003", s == 422 and "ARV-CAP-007" in b,
                  "the import without title/work-id maps to the kernel's ARV-CAP-007 refusal (422)")
            # 3) the positive import: the commit-before-ack ack carries the durability
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                     dict(H, **{"Idempotency-Key": "k-094-b"}),
                                     body=b"hello arivo", query=b"title=Test+Work"))
            ack = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-004", s == 200 and str(ack.get("api_version")) == "1"
                  and ack.get("durability_rung") == "local_durable",
                  "the positive import returns the kernel's honest ack (durability + api_version)")
            check("ARV-API-005", bool(ack.get("result_ref")),
                  f"the ack carries the effect's result_ref (got: {ack.get('result_ref', '')[:40]!r})")
            # 4) the idempotent replay: the same key + body -> the replayed ack
            s2, b2 = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                      dict(H, **{"Idempotency-Key": "k-094-b"}),
                                      body=b"hello arivo", query=b"title=Test+Work"))
            ack2 = json.loads(b2) if b2.startswith("{") else {}
            check("ARV-API-006", s2 == 200 and ack2.get("result_ref") == ack.get("result_ref"),
                  "the same key+body replays the SAME effect (the idempotency law through HTTP)")
            # 5) the conflict: the same key + a DIFFERENT body -> ARV-CMD-409
            s3, b3 = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                      dict(H, **{"Idempotency-Key": "k-094-b"}),
                                      body=b"different bytes", query=b"title=Test+Work"))
            check("ARV-API-007", s3 == 409 and "ARV-CMD-409" in b3,
                  "the same key + different body refuses ARV-CMD-409 through HTTP (the conflict law)")
            # 6) the list route: the bounded page contract (§11.3's list laws)
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/sources", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-008", s == 200 and isinstance(d.get("rows"), list) and str(d.get("api_version")) == "1",
                  f"GET /api/v1/sources lists the owner's library (rows: {len(d.get('rows', []))})")
            # 7) the list bounds: limit=0 / limit=1001 / a non-integer -> 422
            for q, why in ((b"limit=0", "0"), (b"limit=1001", "1001"), (b"limit=abc", "non-integer")):
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/sources", H, query=q))
                check("ARV-API-009" if q != b"limit=abc" else "ARV-API-010",
                      s == 422 and "ARV-QRY-004" in b,
                      f"the list bound {why} refuses ARV-QRY-004 (the bounded page contract)")
            # 8) the owner isolation: another owner's token sees nothing
            tok_b = _token(priv, cfg, "test-key-1", sub="owner-b")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/sources",
                                     {"Authorization": "Bearer " + tok_b},
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-011", s == 200 and d.get("rows") == [],
                  "owner B's list is EMPTY over owner A's rows (the isolation law through HTTP)")
            # 9) the detail: an existing source -> the row; an ABSENT one -> the 404
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/sources", H, query=b"limit=50"))
            dA = json.loads(b) if b.startswith("{") else {}
            real_id = (dA.get("rows") or [{}])[0].get("id", "")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/sources/{real_id}", H))
            check("ARV-API-012", s == 200 and "api_version" in b,
                  "GET /api/v1/sources/{id} returns the owner's source detail")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/sources/00000000-0000-0000-0000-000000000000", H))
            check("ARV-API-013", s == 404,
                  "an absent source is a 404 (never another owner's object existence)")
            # 10) the unauthenticated GET on the kernel-backed routes
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/sources"))
            check("ARV-API-014", s == 401 and "ARV-AUTH-001" in b,
                  "the kernel-backed read routes are auth-guarded like every product route")

            # 11) the handoff revalidation (F5b): BOTH selectors -> the kernel
            # cannot see the XOR (the adapter drops work-id silently) -> the
            # adapter must refuse ARV-CAP-007 itself
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                     dict(H, **{"Idempotency-Key": "k-094-x"}),
                                     body=b"hello arivo",
                                     query=b"title=Both&work_id=00000000-0000-0000-0000-000000000000"))
            check("ARV-API-015", s == 422 and "ARV-CAP-007" in b,
                  "title AND work_id together refuse 422 (exactly-one-of, enforced where the kernel cannot see it)")
            # 12) the handoff revalidation (F1): an over-cap DECLARED body is
            # refused 413 before any byte is read (the early bound)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                     dict(H, **{"Idempotency-Key": "k-094-y",
                                                "Content-Length": "999999999"}),
                                     body=b"hello arivo", query=b"title=Early+Bound"))
            check("ARV-API-016", s == 413,
                  "a declared over-cap Content-Length refuses 413 before the body is read")
            # 13) the handoff revalidation (F1, the streaming half): the cap
            # holds DURING the read (a lying/chunked client cannot exhaust
            # memory) — regression guard over the streaming cap
            from harness.api import routes as _routes_mod
            _saved_cap = _routes_mod.MAX_IMPORT_BYTES
            _routes_mod.MAX_IMPORT_BYTES = 100
            try:
                s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                        dict(H, **{"Idempotency-Key": "k-094-z"}),
                                        body=b"x" * 200, query=b"title=Stream+Cap"))
                check("ARV-API-017", s == 413,
                      "the streamed body over the cap refuses 413 (the cap holds during the read)")
            finally:
                _routes_mod.MAX_IMPORT_BYTES = _saved_cap
            # 14) the handoff revalidation (F2): a kernel write in flight does
            # NOT block the loop — health answers concurrently (measured: the
            # blocking hypothesis was DISPROVEN; this check pins it stays that way)
            async def _probe():
                async def _timed(mk):
                    t0 = clock.mono()  # LAW-24: the only sanctioned monotonic read
                    r = await mk()
                    return clock.mono() - t0, r
                return await asyncio.gather(
                    _timed(lambda: call(app_k, "POST", "/api/v1/imports",
                                dict(H, **{"Idempotency-Key": "k-094-c"}),
                                body=b"concurrency probe", query=b"title=Conc+Work")),
                    _timed(lambda: call(app_k, "GET", "/health/live")))
            ((imp_t, (imp_s, _ib)), (hl_t, (hl_s, _hb))) = asyncio.run(_probe())
            check("ARV-API-018", imp_s == 200 and hl_s == 200 and hl_t < imp_t * 0.5,
                  f"health answers while a kernel write is in flight (the loop is not blocked; "
                  f"health {hl_t:.3f}s vs import {imp_t:.3f}s)")

            # 15) the SEV round-1 repairs (SEV-094-1/-3): the refusal map's
            # DEFAULT is the 500 class for named-but-unmapped kernel codes —
            # F6's ARV-CMD-010 is the live example: a server-side failure
            # must never wear the no-leak 404; the timeout bound stays
            # inside the §11.4 named-error envelope
            kr = _routes_mod._map_kernel_refusal(
                "FAIL ARV-CMD-010: index row requires 8192 bytes, maximum size 8191")
            check("ARV-API-019",
                  kr.status == 500 and kr.code == "ARV-CMD-010"
                  and "index row" not in kr.message,
                  "a named-but-unmapped kernel refusal maps to the 500 class (the named code kept; the kernel's raw cause text never echoed — §11.4)")
            kr2 = _routes_mod._map_kernel_refusal(
                "FAIL ARV-QRY-001: no such object (abc) in the caller's scope")
            check("ARV-API-020", kr2.status == 404,
                  "the absence family (ARV-QRY-001/003) keeps the no-leak 404 class")
            try:
                _routes_mod._run_kernel(
                    [sys.executable, "-c", "import time; time.sleep(5)"], db, timeout=0.2)
                check("ARV-API-021", False,
                      "a kernel exceeding its time bound refuses ARV-API-504 inside the envelope")
            except _routes_mod.KernelRefusal as e:
                check("ARV-API-021",
                      e.code == "ARV-API-504" and e.status == 504,
                      "a kernel exceeding its time bound refuses ARV-API-504 inside the envelope")

            # ---------------- CLAIM-096: the extraction/readiness area ----------------
            # 16) the truthful readiness BEFORE any extraction: never_requested
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{real_id}/extraction", H))
            d = json.loads(b) if b.startswith("{") else {}
            row = d.get("row", {})
            check("ARV-API-022",
                  s == 200 and row.get("readiness") == "never_requested"
                  and row.get("retryable") is False
                  and row.get("passage_count") == 0
                  and row.get("generation_id") is None,
                  "GET /sources/{id}/extraction answers never_requested before any extraction (never presented as ready)")

            # 17) the extraction write: the idem key law + the honest ack
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/extraction", H))
            check("ARV-API-023", s == 400 and "Idempotency-Key" in b,
                  "POST /sources/{id}/extraction refuses without the idempotency key (the §11.3 law)")
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/extraction",
                                     dict(H, **{"Idempotency-Key": "k-096-e1"})))
            ack_x = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-024",
                  s == 200 and ack_x.get("status") == "committed"
                  and bool(ack_x.get("result_ref"))
                  and ack_x.get("durability_rung") == "local_durable"
                  and str(ack_x.get("api_version")) == "1",
                  "POST /sources/{id}/extraction returns the kernel's honest ack (committed, durability, result_ref=generation)")

            # 18) the safe retry: the same key replays the SAME generation
            s2, b2 = asyncio.run(call(app_k, "POST",
                                       f"/api/v1/sources/{real_id}/extraction",
                                       dict(H, **{"Idempotency-Key": "k-096-e1"})))
            ack_x2 = json.loads(b2) if b2.startswith("{") else {}
            check("ARV-API-025",
                  s2 == 200 and ack_x2.get("status") == "replayed"
                  and ack_x2.get("result_ref") == ack_x.get("result_ref"),
                  "the same idempotency key replays the SAME generation (the safe retry through HTTP)")

            # 19) the truthful readiness AFTER extraction: ready + the generation
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{real_id}/extraction", H))
            d = json.loads(b) if b.startswith("{") else {}
            row = d.get("row", {})
            check("ARV-API-026",
                  s == 200 and row.get("readiness") == "ready"
                  and row.get("generation_id") == ack_x.get("result_ref")
                  and row.get("passage_count", 0) >= 1
                  and row.get("generation_ordinal") == 1,
                  "GET /sources/{id}/extraction answers ready with the serving generation (passage_count from the CURRENT generation only)")

            # 20) the safe rebuild: a NEW key builds a NEW generation
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/extraction",
                                     dict(H, **{"Idempotency-Key": "k-096-e2"})))
            ack_r = json.loads(b) if b.startswith("{") else {}
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{real_id}/extraction", H))
            row = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-027",
                  s == 200 and ack_r.get("status") == "committed"
                  and ack_r.get("result_ref") != ack_x.get("result_ref")
                  and row.get("generation_id") == ack_r.get("result_ref")
                  and row.get("generation_count") == 2
                  and row.get("generation_ordinal") == 2
                  and row.get("readiness") == "ready",
                  "a NEW idempotency key builds a NEW generation (the safe rebuild: the old superseded, the readiness answers the new)")

            # 21) the interrupted extraction + the resume: a crashed building
            # row (the kernel's own crash point, driven directly) is answered
            # 'building + retryable', and the SAME key resumes it to current
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                     dict(H, **{"Idempotency-Key": "k-096-c2"}),
                                     body=b"crash class corpus for the interrupted extraction\nsecond passage line\n",
                                     query=b"title=Crash+Class"))
            ack_c = json.loads(b) if b.startswith("{") else {}
            crash_sid = ack_c.get("result_ref", "")
            subprocess.run([sys.executable, "harness/extract.py",
                            "--owner", "route-user", "--actor", "owner",
                            "--client-id", "api-v1", "--idem-key", "k-096-x1",
                            "--source-id", crash_sid, "--crash-at", "pre-commit"],
                           cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                           capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PGDATABASE=db))
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{crash_sid}/extraction", H))
            row = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-028",
                  s == 200 and row.get("readiness") == "building"
                  and row.get("retryable") is True,
                  "a crashed building generation answers 'building + retryable' (never failed, never ready — the truthful interrupted state)")
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{crash_sid}/extraction",
                                     dict(H, **{"Idempotency-Key": "k-096-x1"})))
            ack_z = json.loads(b) if b.startswith("{") else {}
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{crash_sid}/extraction", H))
            row = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-029",
                  s == 200 and ack_z.get("status") in ("committed", "replayed")
                  and row.get("readiness") == "ready"
                  and row.get("generation_id") == (ack_z.get("result_ref") or row.get("generation_id")),
                  "the SAME key resumes the crashed building generation to current (the interrupted-extraction recovery through HTTP)")

            # 22) the cross-owner no-leak: owner B's token against A's source
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/extraction",
                                     {"Authorization": "Bearer " + tok_b,
                                      "Idempotency-Key": "k-096-b"}))
            check("ARV-API-030",
                  s == 404 and "ARV-EXT-004" in b,
                  "owner B's extraction request against A's source is the no-leak 404 (ARV-EXT-004 mapped)")
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{real_id}/extraction",
                                     {"Authorization": "Bearer " + tok_b}))
            check("ARV-API-031", s == 404,
                  "owner B's readiness read against A's source is the same no-leak 404")

            # 23) the absent source: 404 on both arms
            s, b = asyncio.run(call(app_k, "POST",
                                     "/api/v1/sources/00000000-0000-0000-0000-000000000000/extraction",
                                     dict(H, **{"Idempotency-Key": "k-096-no"})))
            check("ARV-API-032", s == 404,
                  "an extraction request for an absent source is a 404 (never another owner's object existence)")
            s, b = asyncio.run(call(app_k, "GET",
                                     "/api/v1/sources/00000000-0000-0000-0000-000000000000/extraction", H))
            check("ARV-API-033", s == 404,
                  "a readiness read for an absent source is the same 404")

            # ---------------- CLAIM-097: the reader family ----------------
            # 24) the position round-trip: save then reopen the same window
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{real_id}/position", H))
            d = json.loads(b) if b.startswith("{") else {}
            row = d.get("row", {})
            check("ARV-API-034",
                  s == 200 and row.get("state") == "no_position_saved",
                  "GET /sources/{id}/position answers the honest no_position_saved state (a 200 ANSWER, never a failure)")
            s, b = asyncio.run(call(app_k, "PUT",
                                     f"/api/v1/sources/{real_id}/position",
                                     dict(H, **{"Idempotency-Key": "k-097-p1",
                                                "Content-Type": "application/json"}),
                                     body=json.dumps({"start": 0, "end": 5}).encode()))
            ack_p = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-035",
                  s == 200 and ack_p.get("status") == "committed"
                  and ack_p.get("durability_rung") == "local_durable",
                  "PUT /sources/{id}/position returns the kernel's honest ack (the serialized save)")
            s, b = asyncio.run(call(app_k, "GET",
                                     f"/api/v1/sources/{real_id}/position", H))
            row = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-036",
                  s == 200 and row.get("state") == "position_saved"
                  and row.get("start_off") == 0 and row.get("end_off") == 5
                  and bool(row.get("saved_generation_id")),
                  "the reopen returns the saved window + the serving-generation binding (the round-trip)")
            # the replay: the same key + body
            s2, b2 = asyncio.run(call(app_k, "PUT",
                                       f"/api/v1/sources/{real_id}/position",
                                       dict(H, **{"Idempotency-Key": "k-097-p1",
                                                  "Content-Type": "application/json"}),
                                       body=json.dumps({"start": 0, "end": 5}).encode()))
            ack_p2 = json.loads(b2) if b2.startswith("{") else {}
            check("ARV-API-037",
                  s2 == 200 and ack_p2.get("status") == "replayed"
                  and ack_p2.get("result_ref") == ack_p.get("result_ref"),
                  "the same position key replays the same save (the idempotency law)")
            # the malformed body: a non-integer offset
            s, b = asyncio.run(call(app_k, "PUT",
                                     f"/api/v1/sources/{real_id}/position",
                                     dict(H, **{"Idempotency-Key": "k-097-p2",
                                                "Content-Type": "application/json"}),
                                     body=json.dumps({"start": "zero", "end": 5}).encode()))
            check("ARV-API-038", s == 422 and "ARV-QRY-004" in b,
                  "a malformed position body (non-integer offsets) refuses 422")

            # 25) the session events: the closed vocabulary + the round-trip
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/session-events",
                                     dict(H, **{"Idempotency-Key": "k-097-s1",
                                                "Content-Type": "application/json"}),
                                     body=json.dumps({"event": "nonsense",
                                                      "start": 0, "end": 3}).encode()))
            check("ARV-API-039", s == 422 and "ARV-SES-004" in b,
                  "a session event outside the closed vocabulary refuses ARV-SES-004 (422)")
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/session-events",
                                     dict(H, **{"Idempotency-Key": "k-097-s2",
                                                "Content-Type": "application/json"}),
                                     body=json.dumps({"event": "session_start",
                                                      "start": 0, "end": 3}).encode()))
            ack_s = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-040",
                  s == 200 and ack_s.get("status") == "committed",
                  "POST /sources/{id}/session-events records a session_start (the D-010 vocabulary)")
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/session-events",
                                     dict(H, **{"Idempotency-Key": "k-097-s3",
                                                "Content-Type": "application/json"}),
                                     body=json.dumps({"event": "dwell",
                                                      "start": 0, "end": 3,
                                                      "dwell_ms": 1500}).encode()))
            ack_d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-041",
                  s == 200 and ack_d.get("status") == "committed",
                  "a dwell event with dwell_ms records (the coarse dwell)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/session-events", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            evs = [r for r in (d.get("rows") or []) if isinstance(r, dict) and r.get("kind")]
            check("ARV-API-042",
                  s == 200 and len(evs) >= 2,
                  f"GET /session-events lists the recorded stream (rows observed: {len(evs)})")

            # 26) the reading state: the derived view carries the saved position
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/reading-state", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)]
            mine = [r for r in rows if r.get("source_id") == real_id]
            check("ARV-API-043",
                  s == 200 and mine and mine[0].get("state") == "position_saved"
                  and mine[0].get("start_off") == 0,
                  "GET /reading-state derives the current-reading view (the saved position present)")

            # 27) the anchor resolution: the content-addressed reading surface
            # (the highlight route itself is CLAIM-098 — this probe mints the
            # anchor through the kernel CLI, then resolves it through the route)
            out = subprocess.run([sys.executable, "harness/commands.py",
                                  "create_highlight", "--owner", "route-user",
                                  "--actor", "owner", "--client-id", "api-v1",
                                  "--idem-key", "k-097-kh1", "--source-id", real_id,
                                  "--start", "0", "--end", "5",
                                  "--selected-text", "hello"],
                                 cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                                 capture_output=True, text=True, timeout=120,
                                 env=dict(os.environ, PGDATABASE=db))
            hl_ref, aid = "", ""
            for ln in out.stdout.splitlines():
                if ln.startswith("ACK "):
                    for tok in ln.split():
                        if tok.startswith("result_ref="):
                            hl_ref = tok.split("=", 1)[1]
            if hl_ref:
                cap = subprocess.run([sys.executable, "harness/query.py",
                                      "get-capture", "--owner", "route-user",
                                      "--id", hl_ref],
                                     cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                                     capture_output=True, text=True, timeout=120,
                                     env=dict(os.environ, PGDATABASE=db))
                try:
                    aid = json.loads(cap.stdout.strip().splitlines()[-1]).get("anchor_id", "")
                except Exception:
                    aid = ""
            check("ARV-API-044", bool(aid),
                  "the kernel mints a highlight whose anchor reads back (the anchor surface's fixture; the highlight ROUTES are CLAIM-098)")
            if aid:
                s, b = asyncio.run(call(app_k, "GET", f"/api/v1/anchors/{aid}", H))
                row = (json.loads(b) if b.startswith("{") else {}).get("row", {})
                check("ARV-API-044",
                      s == 200 and row.get("anchor_id") == aid
                      and "start_off" in json.dumps(row),
                      "GET /anchors/{id} resolves the content-addressed reading surface (the offsets + the digests + the generation binding)")
            # the no-leak: an absent anchor
            s, b = asyncio.run(call(app_k, "GET",
                                     "/api/v1/anchors/00000000-0000-0000-0000-000000000000", H))
            check("ARV-API-045", s == 404,
                  "an absent anchor is the no-leak 404")

        finally:
            os.environ.pop("ARIVO_API_DB", None)
            psql("postgres", f"DROP DATABASE {db}")
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
