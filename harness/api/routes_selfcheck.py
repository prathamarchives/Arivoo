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
            # 24) the position round-trip: save then reopen the same window.
            # THE PREREQUISITE (the kernel's own law): the position binds to
            # the serving generation — the source must be extracted first
            # (the 096 route provides it; the battery's flow uses it)
            s, b = asyncio.run(call(app_k, "POST",
                                     f"/api/v1/sources/{real_id}/extraction",
                                     dict(H, **{"Idempotency-Key": "k-097-ex"})))
            ack_ex = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-034",
                  s == 200 and ack_ex.get("status") in ("committed", "replayed"),
                  "the reader-family fixture: the source is extracted first (the position's serving-generation prerequisite — the kernel's own law)")
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
                  s == 200 and row.get("state") == "saved"
                  and row.get("start_off") == 0 and row.get("end_off") == 5
                  and bool(row.get("saved_generation_id"))
                  and row.get("generation_matches") is True,
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
            # the CLI page contract: the non-header rows (the list arm's own
            # row shape — pipe-delimited or JSON, the count is the evidence)
            evs = [ln for ln in (d.get("rows") or [])
                   if isinstance(ln, dict) and (ln.get("kind") or ln.get("id")
                                                or ln.get("event"))]
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
                  s == 200 and mine and mine[0].get("state") == "saved"
                  and mine[0].get("start_off") == 0,
                  "GET /reading-state derives the current-reading view (the saved position present)")
            # 27) the anchor resolution: the content-addressed reading surface
            # (the highlight route itself is CLAIM-098 — this probe mints the
            # anchor through the kernel CLI, then resolves it through the route)
            out = subprocess.run([sys.executable, "harness/commands.py",
                                  "create_highlight", "--owner", "route-user",
                                  "--actor", "owner", "--client-id", "api-v1",
                                  "--idem-key", "k-097-kh1", "--source-id", real_id,
                                  "--start", "0", "--end", "5"],
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
                for ln in (cap.stdout or "").strip().splitlines():
                    if ln.startswith("{"):
                        try:
                            aid = json.loads(ln).get("anchor_id", "") or aid
                        except Exception:
                            pass
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

            # ---------------- CLAIM-098: the highlights/bookmarks family ----------------
            # (§11.2 families 2-3: create/read/revise|move/tombstone/restore/
            # list/history over the kernel's capture + bookmark machines; plus
            # the 097 review's NAMED FOLLOWUP — the cross-owner legs the 097
            # battery lacked, landed here for BOTH the capture families and
            # the reader family's write surfaces)
            JSON_H = dict(H, **{"Content-Type": "application/json"})

            def _J(idem):
                return dict(JSON_H, **{"Idempotency-Key": idem})

            # 28) the highlight create: the §11.3 write law
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", JSON_H,
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 0, "end": 5}).encode()))
            check("ARV-API-046", s == 400 and "Idempotency-Key" in b,
                  "POST /highlights refuses without the idempotency key (the §11.3 law)")
            # 29) the create against an absent source: the no-leak absence
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-098-x1"),
                                     body=json.dumps({"source_id":
                                                      "00000000-0000-0000-0000-000000000000",
                                                      "start": 0, "end": 5}).encode()))
            check("ARV-API-047", s == 404 and "ARV-CAP-002" in b,
                  "the create against an absent source is the kernel's ARV-CAP-002 404 (absent and another owner's are the SAME refusal)")
            # 30) the invalid offsets: never clamped, never guessed
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-098-x2"),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 5, "end": 5}).encode()))
            check("ARV-API-048", s == 422 and "ARV-CAP-003" in b,
                  "the create with start >= end refuses ARV-CAP-003 (the offset law)")
            # 31) the positive create: the commit-before-ack + the derived text
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-098-h1"),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 0, "end": 5}).encode()))
            ack_h = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-049", s == 200 and ack_h.get("status") == "committed"
                  and bool(ack_h.get("result_ref"))
                  and ack_h.get("durability_rung") == "local_durable",
                  "POST /highlights returns the kernel's honest ack (the selected text DERIVED server-side)")
            hl_id = ack_h.get("result_ref", "")
            # 32) the replay: the same key + body -> the SAME effect
            s2, b2 = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-098-h1"),
                                       body=json.dumps({"source_id": real_id,
                                                        "start": 0, "end": 5}).encode()))
            ack_h2 = json.loads(b2) if b2.startswith("{") else {}
            check("ARV-API-050", s2 == 200 and ack_h2.get("result_ref") == hl_id
                  and ack_h2.get("status") == "replayed",
                  "the same key replays the SAME highlight (the idempotency law)")
            # 33) the conflict: the same key + a different body
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-098-h1"),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 1, "end": 5}).encode()))
            check("ARV-API-051", s == 409 and "ARV-CMD-409" in b,
                  "the same key + different body refuses ARV-CMD-409 (the conflict law)")
            # 34) the list: the bounded page over the caller's captures
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/highlights", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-052", s == 200 and hl_id in json.dumps(d.get("rows", [])),
                  "GET /highlights lists the caller's captures (the new id present)")
            # 35) the read: the current revision + the anchor binding
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}", H))
            row_h = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-053", s == 200 and row_h.get("selected_text") == "hello"
                  and row_h.get("revision") == 1 and row_h.get("anchor_id"),
                  "GET /highlights/{id} reads back the derived selection + the anchor binding")
            # 36) the history: the governed view (revisions + lifecycle events)
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}/history", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-054", s == 200 and len(d.get("rows") or []) >= 1
                  and all("revision" in r for r in d.get("rows", []) if isinstance(r, dict)),
                  "GET /highlights/{id}/history serves the governed history")
            # 37) the revise: a NEW immutable revision at the new offsets
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/highlights/{hl_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-098-h1r"}),
                                     body=json.dumps({"start": 6, "end": 11}).encode()))
            ack_r = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-055", s == 200 and ack_r.get("status") == "committed"
                  and ack_r.get("revision") == "2",
                  "PUT /highlights/{id} revises (a new revision at the new offsets)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}", H))
            row_h = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-056", s == 200 and row_h.get("selected_text") == "arivo"
                  and row_h.get("revision") == 2,
                  "the revised highlight reads back the NEW selection at revision 2")
            # 38) the tombstone: hidden from ordinary retrieval, history kept
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/highlights/{hl_id}",
                                     dict(H, **{"Idempotency-Key": "k-098-h1t"})))
            ack_t = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-057", s == 200 and ack_t.get("status") == "committed",
                  "DELETE /highlights/{id} tombstones (the §3.3 delete transition)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}", H))
            check("ARV-API-058", s == 404,
                  "the tombstoned highlight is hidden from the ordinary read (ARV-QRY-003 -> 404)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}/history", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-059", s == 200 and len(d.get("rows") or []) >= 2,
                  "the governed history still serves the tombstoned id (never erased)")
            # 39) the alternation: a second tombstone refuses its named code
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/highlights/{hl_id}",
                                     dict(H, **{"Idempotency-Key": "k-098-h1t2"})))
            check("ARV-API-060", s == 409 and "ARV-HLC-003" in b,
                  "the second tombstone refuses ARV-HLC-003 (the §3.3 alternation)")
            # 40) the restore: back to ordinary retrieval, revisions untouched
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/highlights/{hl_id}/restore",
                                     dict(H, **{"Idempotency-Key": "k-098-h1rr"})))
            ack_rr = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-061", s == 200 and ack_rr.get("status") == "committed",
                  "POST /highlights/{id}/restore returns it to ordinary retrieval")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}", H))
            row_h = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-062", s == 200 and row_h.get("selected_text") == "arivo",
                  "the restored highlight serves the SAME revised content (the revisions were never touched)")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/highlights/{hl_id}/restore",
                                     dict(H, **{"Idempotency-Key": "k-098-h1rr2"})))
            check("ARV-API-063", s == 409 and "ARV-HLC-004" in b,
                  "the restore from active refuses ARV-HLC-004 (the alternation, both directions)")
            # 41) the revise on a tombstoned id: restore first
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-098-h2"),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 0, "end": 4}).encode()))
            hl2 = (json.loads(b) if b.startswith("{") else {}).get("result_ref", "")
            asyncio.run(call(app_k, "DELETE", f"/api/v1/highlights/{hl2}",
                             dict(H, **{"Idempotency-Key": "k-098-h2t"})))
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/highlights/{hl2}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-098-h2r"}),
                                     body=json.dumps({"start": 1, "end": 4}).encode()))
            check("ARV-API-064", s == 409 and "ARV-HLC-002" in b,
                  "the revise on a tombstoned highlight refuses ARV-HLC-002 (restore precedes edit)")
            # 42) the list bounds (the shared bounded-page law)
            for q, why in ((b"limit=0", "0"), (b"limit=1001", "1001")):
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/highlights", H, query=q))
                check("ARV-API-065", s == 422 and "ARV-QRY-004" in b,
                      f"the highlights list bound {why} refuses ARV-QRY-004")

            # 43) the bookmark family: the same lifecycle over the move machine
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/bookmarks", _J("k-098-b1"),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 0, "end": 3}).encode()))
            ack_b = json.loads(b) if b.startswith("{") else {}
            bm_id = ack_b.get("result_ref", "")
            check("ARV-API-066", s == 200 and ack_b.get("status") == "committed" and bm_id,
                  "POST /bookmarks creates the stable return location (identity + the versioned anchor)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/bookmarks/{bm_id}", H))
            row_b = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-067", s == 200 and row_b.get("source_id") == real_id
                  and row_b.get("revision") == 1,
                  "GET /bookmarks/{id} reads back the location row (NO content copy — the structural law)")
            # 44) the move: the serialized edit transition
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/bookmarks/{bm_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-098-b1m"}),
                                     body=json.dumps({"start": 2, "end": 6}).encode()))
            ack_m = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-068", s == 200 and ack_m.get("revision") == "2",
                  "PUT /bookmarks/{id} moves (the serialized edit transition, a new revision)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/bookmarks/{bm_id}/history", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-069", s == 200 and len(d.get("rows") or []) >= 2,
                  "GET /bookmarks/{id}/history serves every revision in order")
            # 45) the bookmark tombstone/restore lifecycle
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/bookmarks/{bm_id}",
                                     dict(H, **{"Idempotency-Key": "k-098-b1t"})))
            check("ARV-API-070", s == 200,
                  "DELETE /bookmarks/{id} tombstones the bookmark")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/bookmarks/{bm_id}", H))
            check("ARV-API-071", s == 404,
                  "the tombstoned bookmark is hidden from the ordinary read")
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/bookmarks/{bm_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-098-b1m2"}),
                                     body=json.dumps({"start": 1, "end": 4}).encode()))
            check("ARV-API-072", s == 409 and "ARV-BMK-002" in b,
                  "the move on a tombstoned bookmark refuses ARV-BMK-002 (restore first)")
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/bookmarks/{bm_id}",
                                     dict(H, **{"Idempotency-Key": "k-098-b1t2"})))
            check("ARV-API-073", s == 409 and "ARV-BMK-003" in b,
                  "the second tombstone refuses ARV-BMK-003 (the alternation)")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/bookmarks/{bm_id}/restore",
                                     dict(H, **{"Idempotency-Key": "k-098-b1rr"})))
            check("ARV-API-074", s == 200,
                  "POST /bookmarks/{id}/restore returns it to ordinary use")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/bookmarks/{bm_id}/restore",
                                     dict(H, **{"Idempotency-Key": "k-098-b1rr2"})))
            check("ARV-API-075", s == 409 and "ARV-BMK-004" in b,
                  "the restore from active refuses ARV-BMK-004 (the alternation)")
            s, b = asyncio.run(call(app_k, "GET",
                                     "/api/v1/bookmarks/00000000-0000-0000-0000-000000000000", H))
            check("ARV-API-076", s == 404,
                  "an absent bookmark is the no-leak 404 (ARV-BMK-001)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/bookmarks", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-077", s == 200 and bm_id in json.dumps(d.get("rows", [])),
                  "GET /bookmarks lists the caller's bookmarks")

            # 46) THE 097 NAMED FOLLOWUP: the cross-owner legs — owner B's
            # token against owner A's objects, both families + the reader
            # family's write surfaces (no existence oracle anywhere)
            HB = {"Authorization": "Bearer " + tok_b}
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/highlights", HB,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-078", s == 200 and d.get("rows") == [],
                  "owner B's highlights list is EMPTY over owner A's captures")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/highlights/{hl_id}", HB))
            check("ARV-API-079", s == 404 and "ARV-QRY-001" in b,
                  "owner B's highlight read is the no-leak ARV-QRY-001 404 (the read path's own absence code — absent and another owner's are the SAME refusal)")
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/highlights/{hl_id}",
                                     dict(HB, **{"Idempotency-Key": "k-098-xb1",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"start": 0, "end": 3}).encode()))
            check("ARV-API-080", s == 404,
                  "owner B's highlight revise is the no-leak 404 (never a 403 existence oracle)")
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/highlights/{hl_id}",
                                     dict(HB, **{"Idempotency-Key": "k-098-xb2"})))
            check("ARV-API-081", s == 404,
                  "owner B's highlight tombstone is the no-leak 404")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/bookmarks",
                                     dict(HB, **{"Idempotency-Key": "k-098-xb3",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 0, "end": 3}).encode()))
            check("ARV-API-082", s == 404 and "ARV-CAP-002" in b,
                  "owner B's bookmark create against A's source is ARV-CAP-002 404 (the anchor-target no-oracle)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/bookmarks", HB,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-083", s == 200 and d.get("rows") == [],
                  "owner B's bookmarks list is EMPTY over owner A's bookmarks")
            # the reader family's cross-owner write legs (the 097 battery's gap)
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/sources/{real_id}/position",
                                     dict(HB, **{"Idempotency-Key": "k-098-xb4",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"start": 0, "end": 3}).encode()))
            check("ARV-API-084", s == 404 and "ARV-POS-001" in b,
                  "owner B's position save against A's source is ARV-POS-001 404 (the no-oracle)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/sources/{real_id}/position", HB))
            check("ARV-API-085", s == 404,
                  "owner B's position read against A's source is the no-leak 404")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/sources/{real_id}/session-events",
                                     dict(HB, **{"Idempotency-Key": "k-098-xb5",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"event": "session_start",
                                                      "start": 0, "end": 3}).encode()))
            check("ARV-API-086", s == 404 and "ARV-SES-001" in b,
                  "owner B's session event against A's source is ARV-SES-001 404")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/reading-state", HB,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)]
            check("ARV-API-087", s == 200 and not [r for r in rows
                                                   if r.get("source_id") == real_id],
                  "owner B's reading-state carries NONE of owner A's sources")
            if aid:
                s, b = asyncio.run(call(app_k, "GET", f"/api/v1/anchors/{aid}", HB))
                check("ARV-API-088", s == 404,
                      "owner B's anchor resolution against A's anchor is the no-leak 404")

            # ---------------- CLAIM-099: the notes/journal/@-reference ----------------
            # families (§11.2 families 4-6: the authored-content surfaces +
            # the typed stable-reference resolution; plus the 098 SEV's
            # NAMED FOLLOWUPS — the idem-key law on every write route, the
            # cross-owner history legs, the typed ARV-QRY-003 on tombstoned
            # reads)
            # the capture-family fixture: a live highlight to reference
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/highlights", _J("k-099-h1"),
                                     body=json.dumps({"source_id": real_id,
                                                      "start": 0, "end": 5}).encode()))
            hl99 = (json.loads(b) if b.startswith("{") else {}).get("result_ref", "")
            # 47) the note create: the §11.3 write law + the ref grammar
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", JSON_H,
                                     body=json.dumps({"content": "first thought"}).encode()))
            check("ARV-API-089", s == 400 and "Idempotency-Key" in b,
                  "POST /notes refuses without the idempotency key (the §11.3 law)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", _J("k-099-n1"),
                                     body=json.dumps({"content": "first thought",
                                                      "refs": ["bogus:xyz"]}).encode()))
            check("ARV-API-090", s == 422 and "ARV-NTE-006" in b,
                  "the note create with an unknown ref kind refuses ARV-NTE-006 (the grammar law)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", _J("k-099-n2"),
                                     body=json.dumps({"content": "x",
                                                      "refs": ["highlight:00000000-0000-0000-0000-000000000000@1"]}).encode()))
            check("ARV-API-091", s == 404 and "ARV-NTE-003" in b,
                  "the note create with a dangling ref target is the no-oracle ARV-NTE-003 404")
            # 48) the positive create: content + the version-aware ref set
            refs99 = [f"highlight:{hl99}@1", f"source:{real_id}"]
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", _J("k-099-n3"),
                                     body=json.dumps({"content": "the margin thought",
                                                      "refs": refs99}).encode()))
            ack_n = json.loads(b) if b.startswith("{") else {}
            nt_id = ack_n.get("result_ref", "")
            check("ARV-API-092", s == 200 and ack_n.get("status") == "committed" and nt_id,
                  "POST /notes creates the authored note with its version-aware reference set")
            # 49) the read: the content + the refs round-trip
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}", H))
            row_n = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            got_refs = json.dumps(row_n.get("refs", row_n.get("references", "")))
            check("ARV-API-093", s == 200 and row_n.get("content") == "the margin thought"
                  and hl99 in got_refs and real_id in got_refs,
                  "GET /notes/{id} reads back the content + the reference set")
            # 50) the replay + conflict (the idem-key law on THIS route)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", _J("k-099-n3"),
                                     body=json.dumps({"content": "the margin thought",
                                                      "refs": refs99}).encode()))
            ack_n2 = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-094", s == 200 and ack_n2.get("status") == "replayed"
                  and ack_n2.get("result_ref") == nt_id,
                  "the same key replays the SAME note (the idempotency law)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", _J("k-099-n3"),
                                     body=json.dumps({"content": "different"}).encode()))
            check("ARV-API-095", s == 409 and "ARV-CMD-409" in b,
                  "the same key + different body refuses ARV-CMD-409")
            # 51) the revise: the full replacement (content AND ref set)
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/notes/{nt_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-099-n3r"}),
                                     body=json.dumps({"content": "the revised thought",
                                                      "refs": [f"source:{real_id}"]}).encode()))
            ack_nr = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-096", s == 200 and ack_nr.get("revision") == "2",
                  "PUT /notes/{id} revises (the full replacement, a new revision)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}", H))
            row_n = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-097", s == 200 and row_n.get("content") == "the revised thought",
                  "the revised note serves the NEW content")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}/history", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-098", s == 200 and len(d.get("rows") or []) >= 2,
                  "GET /notes/{id}/history serves every revision in order")
            # 52) the tombstone lifecycle + the TYPED hidden code (the 098 named followup)
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/notes/{nt_id}",
                                     dict(H, **{"Idempotency-Key": "k-099-n3t"})))
            check("ARV-API-099", s == 200,
                  "DELETE /notes/{id} tombstones the note")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}", H))
            check("ARV-API-100", s == 404 and "ARV-QRY-003" in b,
                  "the tombstoned note read carries the TYPED ARV-QRY-003 (the 098 named followup — the status AND the code)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}/history", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-101", s == 200 and len(d.get("rows") or []) >= 2,
                  "the governed history still serves the tombstoned note")
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/notes/{nt_id}",
                                     dict(H, **{"Idempotency-Key": "k-099-n3t2"})))
            check("ARV-API-102", s == 409 and "ARV-NTE-004" in b,
                  "the second tombstone refuses ARV-NTE-004 (the alternation)")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/notes/{nt_id}/restore",
                                     dict(H, **{"Idempotency-Key": "k-099-n3rr"})))
            check("ARV-API-103", s == 200,
                  "POST /notes/{id}/restore returns it to ordinary retrieval")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/notes/{nt_id}/restore",
                                     dict(H, **{"Idempotency-Key": "k-099-n3rr2"})))
            check("ARV-API-104", s == 409 and "ARV-NTE-005" in b,
                  "the restore from active refuses ARV-NTE-005 (the alternation)")
            # 53) the revise on tombstoned + the idem-key law on PUT/DELETE (the 098 followup)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes", _J("k-099-n4"),
                                     body=json.dumps({"content": "second"}).encode()))
            nt2 = (json.loads(b) if b.startswith("{") else {}).get("result_ref", "")
            asyncio.run(call(app_k, "DELETE", f"/api/v1/notes/{nt2}",
                             dict(H, **{"Idempotency-Key": "k-099-n4t"})))
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/notes/{nt2}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-099-n4r"}),
                                     body=json.dumps({"content": "y"}).encode()))
            check("ARV-API-105", s == 409 and "ARV-NTE-002" in b,
                  "the revise on a tombstoned note refuses ARV-NTE-002 (restore first)")
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/notes/{nt_id}", JSON_H,
                                     body=json.dumps({"content": "z"}).encode()))
            check("ARV-API-106", s == 400 and "Idempotency-Key" in b,
                  "PUT /notes requires the idempotency key (the §11.3 law on EVERY write route — the 098 followup)")
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/notes/{nt_id}", H))
            check("ARV-API-107", s == 400 and "Idempotency-Key" in b,
                  "DELETE /notes requires the idempotency key (the §11.3 law on EVERY write route)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/notes", H, query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-108", s == 200 and nt_id in json.dumps(d.get("rows", [])),
                  "GET /notes lists the caller's notes")
            for q in (b"limit=0", b"limit=1001"):
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/notes", H, query=q))
                check("ARV-API-109", s == 422 and "ARV-QRY-004" in b,
                      f"the notes list bound {q.decode()} refuses ARV-QRY-004")

            # 54) the journal family: the writing lab
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal", JSON_H,
                                     body=json.dumps({"kind": "raw",
                                                      "content": "the raw thinking"}).encode()))
            check("ARV-API-110", s == 400 and "Idempotency-Key" in b,
                  "POST /journal refuses without the idempotency key")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal", _J("k-099-j0"),
                                     body=json.dumps({"kind": "summary",
                                                      "content": "x"}).encode()))
            check("ARV-API-111", s == 422 and "ARV-JNL-002" in b,
                  "the journal kind outside the closed vocabulary refuses ARV-JNL-002")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal", _J("k-099-j1"),
                                     body=json.dumps({"kind": "raw",
                                                      "content": "the raw thinking",
                                                      "source_id": real_id}).encode()))
            ack_j = json.loads(b) if b.startswith("{") else {}
            jn_id = ack_j.get("result_ref", "").split("@")[0]  # the journal ack's ref carries @rev (the revision pin) — the BLOCK identity is the bare uuid
            check("ARV-API-112", s == 200 and ack_j.get("status") == "committed" and jn_id,
                  "POST /journal creates the source-bound raw block")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/journal/{jn_id}", H))
            row_j = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-113", s == 200 and row_j.get("kind") == "raw"
                  and row_j.get("content") == "the raw thinking"
                  and row_j.get("source_id") == real_id,
                  "GET /journal/{id} reads back the block whole (the lossless round-trip)")
            # the revise: the body carries the content ONLY — the kind is the
            # block's immutable identity (the kernel's own revise carries the
            # prior revision's kind; a kind in the DTO is the F5b silent-drop
            # class — refused named, SEV9-123k's honest contract)
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/journal/{jn_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-099-j1r"}),
                                     body=json.dumps({"kind": "creative",
                                                      "content": "the creative rewrite"}).encode()))
            check("ARV-API-114", s == 422 and "immutable identity" in b,
                  "PUT /journal/{id} refuses a kind in the revise DTO (the F5b silent-drop class — the kind is immutable identity)")
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/journal/{jn_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-099-j1r"}),
                                     body=json.dumps({"content": "the revised thinking"}).encode()))
            ack_jr = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-114",
                  s == 200 and ack_jr.get("revision") == "2",
                  "PUT /journal/{id} revises (the body-only DTO, a new revision)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/journal/{jn_id}", H))
            row_j = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-114",
                  s == 200 and row_j.get("kind") == "raw"
                  and row_j.get("content") == "the revised thinking",
                  "the revised block keeps its kind (immutable identity) and serves the NEW content")
            # the lone-surrogate content: valid JSON, unencodable as UTF-8 —
            # the refusal INSIDE the §11.4 envelope (SEV9-171's contract)
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/journal/{jn_id}",
                                     dict(JSON_H, **{"Idempotency-Key": "k-099-j1s"}),
                                     body=b'{"content": "lone \\ud800 surrogate"}'))
            check("ARV-API-114", s == 422 and "surrogate" in b,
                  "the lone-surrogate content refuses INSIDE the envelope (a named 422, never a bare crash — SEV9-171)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/journal/{jn_id}/history", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-115", s == 200 and len(d.get("rows") or []) >= 2,
                  "GET /journal/{id}/history serves the full history")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/journal", H, query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-116", s == 200 and jn_id in json.dumps(d.get("rows", [])),
                  "GET /journal lists the caller's blocks")
            # 55) the sourceless block + the bound-block no-oracle
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal", _J("k-099-j2"),
                                     body=json.dumps({"kind": "creative",
                                                      "content": "free writing"}).encode()))
            check("ARV-API-117", s == 200,
                  "the sourceless journal block creates (a first-class row — the binding is OPTIONAL)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal", _J("k-099-j3"),
                                     body=json.dumps({"kind": "raw", "content": "x",
                                                      "source_id":
                                                      "00000000-0000-0000-0000-000000000000"}).encode()))
            check("ARV-API-118", s == 404 and "ARV-JNL-005" in b,
                  "the bound block against an absent source is the no-oracle ARV-JNL-005 404")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal", _J("k-099-j1"),
                                     body=json.dumps({"kind": "raw",
                                                      "content": "the raw thinking",
                                                      "source_id": real_id}).encode()))
            ack_j2 = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-119", s == 200 and ack_j2.get("status") == "replayed"
                  and ack_j2.get("result_ref", "").split("@")[0] == jn_id,
                  "the journal idempotent replay (the same key + body — the ack's ref carries the @rev pin)")

            # 56) the typed stable-reference resolution
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/references", H,
                                     query=f"ref=source:{real_id}".encode()))
            row_rf = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-120", s == 200 and row_rf.get("state") == "current",
                  "GET /references resolves the bare source reference (the typed verdict — the resolution's own 'current' state)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/references", H,
                                     query=f"ref=highlight:{hl99}@1".encode()))
            row_rf = (json.loads(b) if b.startswith("{") else {}).get("row", {})
            check("ARV-API-121", s == 200 and row_rf.get("state") == "current"
                  and row_rf.get("revision") == 1,
                  "the pinned highlight reference resolves exactly as pinned (the revision carried)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/references", H,
                                     query=b"ref=note:00000000-0000-0000-0000-000000000000@1"))
            check("ARV-API-122", s == 404 and "ARV-REF-001" in b,
                  "the dangling reference is the no-oracle ARV-REF-001 404")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/references", H,
                                     query=b"ref=notakind:xyz"))
            check("ARV-API-123", s == 422 and "ARV-REF-002" in b,
                  "the malformed reference grammar refuses ARV-REF-002")

            # 57) the cross-owner legs (the 098 named followup: the history
            # legs included; owner B's token against owner A's objects)
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/notes", HB, query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-124", s == 200 and d.get("rows") == [],
                  "owner B's notes list is EMPTY over owner A's notes")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}", HB))
            check("ARV-API-125", s == 404 and "ARV-QRY-001" in b,
                  "owner B's note read is the no-leak ARV-QRY-001 404")
            s, b = asyncio.run(call(app_k, "PUT", f"/api/v1/notes/{nt_id}",
                                     dict(HB, **{"Idempotency-Key": "k-099-xb1",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"content": "steal"}).encode()))
            check("ARV-API-126", s == 404,
                  "owner B's note revise is the no-leak 404")
            s, b = asyncio.run(call(app_k, "DELETE", f"/api/v1/notes/{nt_id}",
                                     dict(HB, **{"Idempotency-Key": "k-099-xb2"})))
            check("ARV-API-127", s == 404,
                  "owner B's note tombstone is the no-leak 404")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{nt_id}/history", HB))
            check("ARV-API-128", s == 404 and "ARV-QRY-001" in b,
                  "owner B's note HISTORY read is the no-leak 404 (the 098 named followup's history leg)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/journal", HB, query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            s2, b2 = asyncio.run(call(app_k, "GET", f"/api/v1/journal/{jn_id}", HB))
            check("ARV-API-129", s == 200 and d.get("rows") == [] and s2 == 404,
                  "owner B's journal list is EMPTY and the block read is the no-leak 404")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal",
                                     dict(HB, **{"Idempotency-Key": "k-099-xb3",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"kind": "raw", "content": "x",
                                                      "source_id": real_id}).encode()))
            check("ARV-API-130", s == 404 and "ARV-JNL-005" in b,
                  "owner B's journal block bound to A's source is ARV-JNL-005 404")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/references", HB,
                                     query=f"ref=note:{nt_id}@1".encode()))
            check("ARV-API-131", s == 404 and "ARV-REF-001" in b,
                  "owner B's reference resolution against A's note is ARV-REF-001 404")

            # ---------------- CLAIM-100: the reading-lists family ----------------
            # (§11.2 family 7: create/list/member add/remove/current
            # membership — the last Workstream 4 row)
            # 58) the create: the §11.3 write law + the name law
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/reading-lists", JSON_H,
                                     body=json.dumps({"name": "The Stack"}).encode()))
            check("ARV-API-132", s == 400 and "Idempotency-Key" in b,
                  "POST /reading-lists refuses without the idempotency key (the §11.3 law)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/reading-lists", _J("k-100-l0"),
                                     body=json.dumps({"name": ""}).encode()))
            check("ARV-API-133", s == 422 and "ARV-RLS-003" in b,
                  "the empty list name refuses ARV-RLS-003 (the name law)")
            # 59) the positive create: the identity is the uuid (names may duplicate)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/reading-lists", _J("k-100-l1"),
                                     body=json.dumps({"name": "The Stack"}).encode()))
            ack_l = json.loads(b) if b.startswith("{") else {}
            rl_id = ack_l.get("result_ref", "")
            check("ARV-API-134", s == 200 and ack_l.get("status") == "committed"
                  and rl_id and "@" not in rl_id,
                  "POST /reading-lists creates the list (the ack's ref is the bare uuid — the identity)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/reading-lists", _J("k-100-l1"),
                                     body=json.dumps({"name": "The Stack"}).encode()))
            ack_l2 = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-135", s == 200 and ack_l2.get("status") == "replayed"
                  and ack_l2.get("result_ref") == rl_id,
                  "the same key replays the SAME list (the idempotency law)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/reading-lists", _J("k-100-l1"),
                                     body=json.dumps({"name": "A Different Name"}).encode()))
            check("ARV-API-136", s == 409 and "ARV-CMD-409" in b,
                  "the same key + different name refuses ARV-CMD-409")
            # 60) the listing: the derived member count
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/reading-lists", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)
                    and r.get("id") == rl_id]
            check("ARV-API-137", s == 200 and rows and rows[0].get("name") == "The Stack"
                  and rows[0].get("member_count") == 0,
                  "GET /reading-lists lists the list with its DERIVED member count")
            # 61) the member add + the current membership
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/reading-lists/{rl_id}/members",
                                     dict(JSON_H, **{"Idempotency-Key": "k-100-m1"}),
                                     body=json.dumps({"source_id": real_id}).encode()))
            ack_m = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-138", s == 200 and ack_m.get("status") == "committed",
                  "POST /reading-lists/{id}/members adds the source (the append-only event)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/reading-lists/{rl_id}", H))
            d = json.loads(b) if b.startswith("{") else {}
            rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)]
            check("ARV-API-139", s == 200 and len(rows) == 1
                  and rows[0].get("source_id") == real_id,
                  "GET /reading-lists/{id} serves the CURRENT membership (the derived view)")
            # 62) the duplicate add: the alternation at the substrate — the
            # honest unknown through the §11.4 no-internals answer
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/reading-lists/{rl_id}/members",
                                     dict(JSON_H, **{"Idempotency-Key": "k-100-m2"}),
                                     body=json.dumps({"source_id": real_id}).encode()))
            check("ARV-API-140", s == 500 and "ARV-CMD-010" in b
                  and "ARV-RLS-008" not in b,
                  "the duplicate add refuses the honest unknown (ARV-CMD-010 500 — the raw substrate cause never echoed, §11.4)")
            # 63) the remove + the empty membership + the re-add
            s, b = asyncio.run(call(app_k, "DELETE",
                                     f"/api/v1/reading-lists/{rl_id}/members/{real_id}",
                                     dict(H, **{"Idempotency-Key": "k-100-m3"})))
            check("ARV-API-141", s == 200,
                  "DELETE /reading-lists/{id}/members/{source_id} removes (the event)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/reading-lists/{rl_id}", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-142", s == 200 and (d.get("rows") or []) == [],
                  "the membership page is EMPTY after the remove")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/reading-lists/{rl_id}/members",
                                     dict(JSON_H, **{"Idempotency-Key": "k-100-m4"}),
                                     body=json.dumps({"source_id": real_id}).encode()))
            check("ARV-API-143", s == 200,
                  "the re-add after the remove commits (the alternation, both directions)")
            # 64) the no-oracles: absent list / absent member source
            s, b = asyncio.run(call(app_k, "POST",
                                     "/api/v1/reading-lists/00000000-0000-0000-0000-000000000000/members",
                                     dict(JSON_H, **{"Idempotency-Key": "k-100-x1"}),
                                     body=json.dumps({"source_id": real_id}).encode()))
            check("ARV-API-144", s == 404 and "ARV-RLS-001" in b,
                  "the add to an absent list is the no-oracle ARV-RLS-001 404")
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/reading-lists/{rl_id}/members",
                                     dict(JSON_H, **{"Idempotency-Key": "k-100-x2"}),
                                     body=json.dumps({"source_id":
                                                      "00000000-0000-0000-0000-000000000000"}).encode()))
            check("ARV-API-145", s == 404 and "ARV-RLS-002" in b,
                  "the add of an absent source is the no-oracle ARV-RLS-002 404")
            s, b = asyncio.run(call(app_k, "GET",
                                     "/api/v1/reading-lists/00000000-0000-0000-0000-000000000000", H))
            check("ARV-API-146", s == 404 and "ARV-QRY-001" in b,
                  "the absent list read is the no-leak ARV-QRY-001 404")
            # 65) the idem-key law on the member writes + the list bounds
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/reading-lists/{rl_id}/members",
                                     JSON_H,
                                     body=json.dumps({"source_id": real_id}).encode()))
            check("ARV-API-147", s == 400 and "Idempotency-Key" in b,
                  "POST .../members requires the idempotency key")
            s, b = asyncio.run(call(app_k, "DELETE",
                                     f"/api/v1/reading-lists/{rl_id}/members/{real_id}", H))
            check("ARV-API-148", s == 400 and "Idempotency-Key" in b,
                  "DELETE .../members/{source_id} requires the idempotency key")
            for q in (b"limit=0", b"limit=1001"):
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/reading-lists", H, query=q))
                check("ARV-API-149", s == 422 and "ARV-QRY-004" in b,
                      f"the reading-lists bound {q.decode()} refuses ARV-QRY-004")
            # 66) the cross-owner legs
            s, b = asyncio.run(call(app_k, "POST", f"/api/v1/reading-lists/{rl_id}/members",
                                     dict(HB, **{"Idempotency-Key": "k-100-xb1",
                                                 "Content-Type": "application/json"}),
                                     body=json.dumps({"source_id": real_id}).encode()))
            check("ARV-API-150", s == 404 and "ARV-RLS-001" in b,
                  "owner B's member add to A's list is the no-oracle ARV-RLS-001 404")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/reading-lists", HB,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-151", s == 200 and d.get("rows") == [],
                  "owner B's reading-lists page is EMPTY over owner A's lists")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/reading-lists/{rl_id}", HB))
            check("ARV-API-152", s == 404,
                  "owner B's membership read of A's list is the no-leak 404")

            # ---------------- CLAIM-101: the retrieval API (Workstream 5) ----------------
            # (§11.2 Retrieval: keyword search + bounded context packs with
            # provenance/trust labels — the query kernel's own search/pack
            # arms; deterministic, no semantic/model work per Q7)
            # 67) the search: the term law
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search", H))
            check("ARV-API-153", s == 422 and "ARV-QRY-004" in b,
                  "GET /search without terms refuses (at least one term required)")
            # the fixture: an extracted, indexed source exists from the earlier
            # families (real_id carries 'hello arivo')
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search", H,
                                     query=b"terms=hello&terms=arivo"))
            d = json.loads(b) if b.startswith("{") else {}
            rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)]
            src_rows = [r for r in rows if r.get("entity_id") == real_id]
            check("ARV-API-154", s == 200 and src_rows
                  and src_rows[0].get("kind") == "source"
                  and src_rows[0].get("matched_terms"),
                  "GET /search with AND terms admits the source (both terms matched — the corpus's captures admitted alongside, the admission list's own order)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search", H,
                                     query=b"terms=hello&terms=nonexistentterm"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-155", s == 200 and (d.get("rows") or []) == [],
                  "the AND semantics: one missing term empties the result (a 200 empty page)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search", H,
                                     query=b"terms=" + b"x" * 600))
            check("ARV-API-156", s == 422 and "ARV-KWR-003" in b,
                  "the over-long term refuses ARV-KWR-003 (the read-side token bound)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search"))
            check("ARV-API-157", s == 401,
                  "GET /search is auth-guarded like every product route")
            # 68) the context packs: the provenance-carrying assembly
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/context-packs", H,
                                     query=b"terms=hello&budget-bytes=4096"))
            d = json.loads(b) if b.startswith("{") else {}
            rows = [r for r in (d.get("rows") or []) if isinstance(r, dict)]
            meta = d.get("page_meta", {}) or {}
            src_pack = [r for r in rows if r.get("entity_id") == real_id]
            check("ARV-API-158", s == 200 and rows and src_pack
                  and src_pack[0].get("trust") == "untrusted"
                  and "hello" in json.dumps(src_pack[0].get("matched_terms", "")),
                  "GET /context-packs admits the source with its trust label + matched terms (the corpus's captures admitted alongside)")
            check("ARV-API-159", s == 200 and meta
                  and isinstance(meta.get("kept"), int) and meta.get("kept", 0) >= 1
                  and isinstance(meta.get("total"), int) and meta.get("total", 0) >= 1
                  and meta.get("truncated") is False
                  and isinstance(meta.get("budget_bytes"), int)
                  and isinstance(meta.get("used_bytes"), int) and "after" in meta,
                  "the pack's truncation metadata serves typed (kept/total/truncated/budget/used/after)")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/context-packs", H,
                                     query=b"terms=hello&budget-bytes=0"))
            check("ARV-API-160", s == 422 and "ARV-QRY-004" in b,
                  "the out-of-bounds budget refuses ARV-QRY-004")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/context-packs", H,
                                     query=b"terms=hello&budget-bytes=4096&limit=0"))
            check("ARV-API-161", s == 422 and "ARV-QRY-004" in b,
                  "the pack's list bound refuses ARV-QRY-004")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search", H,
                                     query=b"terms=hello&terms=arivo&limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-162", s == 200 and isinstance(d.get("rows"), list)
                  and d.get("api_version") == 1,
                  "the search page serves on the shared page contract")
            # 69) the cross-owner legs
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/search", HB,
                                     query=b"terms=hello"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-163", s == 200 and (d.get("rows") or []) == [],
                  "owner B's search over A's corpus is EMPTY")
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/context-packs", HB,
                                     query=b"terms=hello&budget-bytes=4096"))
            d = json.loads(b) if b.startswith("{") else {}
            meta = d.get("page_meta", {}) or {}
            check("ARV-API-164", s == 200 and (d.get("rows") or []) == []
                  and meta.get("total") == 0,
                  "owner B's context pack over A's corpus is EMPTY (total=0)")

            # ---------------- CLAIM-102: the sync/export/purge family ----------------
            # the corpus hand: owner A's own rows for the family's legs (a
            # fresh import + extraction so the capture legs carry a live
            # source; the notes for the authored-content purge legs)
            import tempfile as _tf, os as _os
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                     dict(H, **{"Idempotency-Key": "k-102-src"}),
                                     body=b"the sync export purge corpus text",
                                     query=b"title=WS6+Corpus"))
            ack_src = json.loads(b) if b.startswith("{") else {}
            src_id = ack_src.get("result_ref", "")
            check("ARV-API-165", s == 200 and bool(src_id),
                  "the WS6 corpus import acks (the family's legs run on live rows)")

            # 1) the outbox status: the kernel's own status arm through HTTP
            # (the counts by state + the queued rows; a fresh owner's outbox
            # may be empty — the ANSWER is the shape, the counts object)
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/sync/outbox", H))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-166", s == 200 and isinstance(d.get("counts"), dict)
                  and isinstance(d.get("queued"), list)
                  and d.get("api_version") == 1,
                  "GET /api/v1/sync/outbox serves the kernel's own status shape (counts + queued)")
            # the import rode the outbox (the outbox-carrying set) — the
            # counts carry pending=1 (the import's own sync intent)
            check("ARV-API-167", s == 200 and d.get("counts", {}).get("pending", 0) >= 1,
                  "the import's outbox row shows pending (the sync-intent record through HTTP)")

            # 2) the delivery pass without a configured target refuses named
            # (503 — never a guess; the service's own parameter)
            os.environ.pop("ARIVO_SYNC_TARGET_DB", None)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/sync/deliver", H))
            check("ARV-API-168", s == 503 and "ARV-SYN-014" in b,
                  "POST /api/v1/sync/deliver without a configured target refuses ARV-SYN-014 (503)")

            # 3) the delivery pass WITH a target: the kernel's own walk over
            # the two-database contract (the local rig's scratch target —
            # migrated, the typed per-row outcomes)
            tgt = psql("postgres", "SELECT 'arv_t102_'||floor(random()*100000)::text").stdout.strip()
            psql("postgres", f"CREATE DATABASE {tgt}")
            r_m = subprocess.run(["python3", "harness/migrate.py"], cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                                 capture_output=True, text=True, timeout=300,
                                 env=dict(env, PGDATABASE=tgt, ARV_MIGRATIONS_DIR="harness/migrations"))
            try:
                check("ARV-API-169", r_m.returncode == 0,
                      "the delivery target's scratch db migrated (the walk's server side)")
                os.environ["ARIVO_SYNC_TARGET_DB"] = tgt
                s, b = asyncio.run(call(app_k, "POST", "/api/v1/sync/deliver", H))
                d = json.loads(b) if b.startswith("{") else {}
                st = d.get("states", {}) or {}
                check("ARV-API-170", s == 200 and d.get("walked", 0) >= 1
                      and isinstance(st, dict) and st.get("k-102-src") == "acknowledged",
                      "POST /api/v1/sync/deliver walks the outbox and acks the import (the kernel's own delivery machine)")
                # the second pass: the earlier corpus's rows (the battery's
                # own accumulated outbox — every prior family's writes ride
                # it too) may hold non-terminal rows; the LAW under test is
                # the TERMINAL HOLD: the just-acked row never re-walks. The
                # walked count of the second pass must be strictly LESS than
                # the first's when the first consumed everything, and the
                # acked row's state must persist.
                s, b = asyncio.run(call(app_k, "POST", "/api/v1/sync/deliver", H))
                d2 = json.loads(b) if b.startswith("{") else {}
                st2 = d2.get("states", {}) or {}
                check("ARV-API-171", s == 200 and "k-102-src" not in st2
                      and d2.get("walked", 0) < d.get("walked", 0) + 1,
                      "the second delivery pass never re-walks a terminal row (the acked import stays acked)")
                # the outbox status now: pending=0, acknowledged>=1
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/sync/outbox", H))
                d = json.loads(b) if b.startswith("{") else {}
                check("ARV-API-172", s == 200 and d.get("counts", {}).get("acknowledged", 0) >= 1,
                      "the outbox status reflects the acknowledged delivery (acknowledged>=1)")
            finally:
                os.environ.pop("ARIVO_SYNC_TARGET_DB", None)
                psql("postgres", f"DROP DATABASE {tgt}")

            # 4) the export: the versioned manifest serves (the service's
            # own staging root; the manifest carries the owner + the hash)
            exp_root = _tf.mkdtemp(prefix="arv_exp_102_")
            try:
                os.environ["ARIVO_EXPORT_ROOT"] = exp_root
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/export", H))
                d = json.loads(b) if b.startswith("{") else {}
                man = d.get("manifest", {}) or {}
                check("ARV-API-173", s == 200 and d.get("state") == "manifest_complete"
                      and man.get("owner") == "route-user"
                      and bool(man.get("state_hash")),
                      "GET /api/v1/export serves the versioned manifest (owner + the canonical state hash)")
                check("ARV-API-174", s == 200 and isinstance(man.get("tables"), dict)
                      and "source" in man.get("tables", {})
                      and isinstance(man["tables"].get("source"), list)
                      and len(man["tables"]["source"]) >= 1,
                      "the manifest's authoritative table set carries the owner's rows (the source table)")
                # the export root NOT configured refuses named (503)
                os.environ.pop("ARIVO_EXPORT_ROOT", None)
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/export", H))
                check("ARV-API-175", s == 503 and "ARV-EXP-008" in b,
                      "GET /api/v1/export without the staging root refuses ARV-EXP-008 (503)")
                os.environ["ARIVO_EXPORT_ROOT"] = exp_root
            finally:
                os.environ.pop("ARIVO_EXPORT_ROOT", None)

            # 5) the governed purge: the DTO law (the kind vocabulary)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p1"}),
                                     body=json.dumps({"kind": "chapter",
                                                      "entity_id": "00000000-0000-0000-0000-000000000000",
                                                      "reason": "x"}).encode()))
            check("ARV-API-176", s == 422 and "ARV-PRG-002" in b,
                  "the purge with an unknown kind refuses ARV-PRG-002 (the vocabulary)")
            # the absent target: the no-oracle 404
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p2"}),
                                     body=json.dumps({"kind": "note",
                                                      "entity_id": "00000000-0000-0000-0000-000000000000",
                                                      "reason": "absent"}).encode()))
            check("ARV-API-177", s == 404 and "ARV-PRG-003" in b,
                  "the purge of an absent object is the no-oracle 404 (absent and another owner's are the SAME)")

            # the live purge: a note create -> the purge -> the ledger row
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/notes",
                                     dict(H, **{"Idempotency-Key": "k-102-n1"}),
                                     body=json.dumps({"content": "the purge corpus note"}).encode()))
            ack_n = json.loads(b) if b.startswith("{") else {}
            note_id = ack_n.get("result_ref", "")
            check("ARV-API-178", s == 200 and bool(note_id),
                  "the purge-leg note creates (the family's live purge target)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p3"}),
                                     body=json.dumps({"kind": "note",
                                                      "entity_id": note_id,
                                                      "reason": "the governed purge (the route battery)"}).encode()))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-179", s == 200 and d.get("state") == "purged"
                  and d.get("ledger_recorded") is True
                  and d.get("content_dropped") is True
                  and d.get("durability_rung") == "local_durable",
                  "the governed purge acks (the ledger recorded + the content dropped + the honest rung)")
            # the note is GONE from the reads (the no-resurrection law)
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/notes/{note_id}", H))
            check("ARV-API-180", s == 404,
                  "the purged note 404s on the read (the content is gone, never resurrected)")
            # the SECOND purge of the same object: the alternation 409
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p4"}),
                                     body=json.dumps({"kind": "note",
                                                      "entity_id": note_id,
                                                      "reason": "again"}).encode()))
            check("ARV-API-181", s == 409 and "ARV-PRG-004" in b,
                  "the second purge of the same object refuses ARV-PRG-004 (the ledger is the permanence record)")

            # the ledger read: the row serves, bounded + paginated
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/purge-ledger", H,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            rows_pl = [r for r in (d.get("rows") or [])
                       if isinstance(r, dict) and r.get("entity_id") == note_id]
            check("ARV-API-182", s == 200 and rows_pl
                  and rows_pl[0].get("kind") == "note"
                  and bool(rows_pl[0].get("created_at")),
                  "GET /api/v1/purge-ledger serves the erasure record (the minimal audit row)")
            # the ledger bounds: limit=0 -> 422
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/purge-ledger", H,
                                     query=b"limit=0"))
            check("ARV-API-183", s == 422 and "ARV-QRY-004" in b,
                  "the purge-ledger list bound refuses ARV-QRY-004")
            # the cross-owner ledger: owner B sees NONE of A's rows
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/purge-ledger", HB,
                                     query=b"limit=50"))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-184", s == 200 and (d.get("rows") or []) == [],
                  "owner B's purge-ledger read over A's rows is EMPTY (the isolation law)")
            # owner B's purge of A's note: the no-oracle 404 (never 403)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(HB, **{"Idempotency-Key": "k-102-p5"}),
                                     body=json.dumps({"kind": "source",
                                                      "entity_id": src_id,
                                                      "reason": "cross-owner"}).encode()))
            check("ARV-API-185", s == 404 and "ARV-PRG-003" in b,
                  "owner B's purge of A's source is the SAME no-oracle 404 (never an existence leak)")

            # the source purge (the cascade): the source + its tree drop,
            # the ledger registers; then the restore legs run on the CLEAN
            # post-purge state (the reconciliation family's own substrate)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p6"}),
                                     body=json.dumps({"kind": "source",
                                                      "entity_id": src_id,
                                                      "reason": "the source purge (the cascade leg)"}).encode()))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-186", s == 200 and d.get("state") == "purged"
                  and d.get("content_dropped") is True,
                  "the source purge acks with the cascade (the tree drops with the ledger row)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/sources/{src_id}", H))
            check("ARV-API-187", s == 404,
                  "the purged source 404s on the detail read")

            # the restore: the export-before-purge archive into a CLEAN
            # second scratch db (the kernel's own machine through the
            # route's staging contract) — the reconciliation drops the
            # purged source (the destination ledger carries it: written
            # through the substrate's own ledger INSERT — the test-substrate
            # pattern the prior suites use, RCW-02/EXP-07's own class; the
            # destination stays CLEAN for the restore law, the ledger row
            # the reconciliation's authority)
            exp_root2 = _tf.mkdtemp(prefix="arv_exp_102b_")
            dst = psql("postgres", "SELECT 'arv_d102_'||floor(random()*100000)::text").stdout.strip()
            psql("postgres", f"CREATE DATABASE {dst}")
            r_md = subprocess.run(["python3", "harness/migrate.py"], cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                                  capture_output=True, text=True, timeout=300,
                                  env=dict(env, PGDATABASE=dst, ARV_MIGRATIONS_DIR="harness/migrations"))
            try:
                # the export runs on the LIVE db: re-import (the earlier
                # source was purged — the ledger holds it), so the archive
                # HOLDS a source the destination will carry as ledgered
                s, b = asyncio.run(call(app_k, "POST", "/api/v1/imports",
                                         dict(H, **{"Idempotency-Key": "k-102-src2"}),
                                         body=b"the restore reconciliation corpus",
                                         query=b"title=WS6+Restore"))
                ack_src2 = json.loads(b) if b.startswith("{") else {}
                src2 = ack_src2.get("result_ref", "")
                os.environ["ARIVO_EXPORT_ROOT"] = exp_root2
                s, b = asyncio.run(call(app_k, "GET", "/api/v1/export", H))
                d = json.loads(b) if b.startswith("{") else {}
                check("ARV-API-188", s == 200 and d.get("state") == "manifest_complete",
                      "the restore leg's export acks (the archive staged under the service root)")
                # the destination's ledger names the ARCHIVE's source (the
                # reconciliation keys on (kind, entity) — the same logical
                # object the archive carries; the write is the ledger's own
                # INSERT, legal on the clean destination)
                r_led_w = psql(dst, "SET app.current_owner='route-user'; "
                               "INSERT INTO arv.purge_ledger (owner_scope, kind, "
                               "entity_id, reason, actor, created_at) VALUES "
                               f"('route-user', 'source', '{src2}', 'the destination "
                               f"ledger (the reconciliation leg)', 'owner', now());")
                check("ARV-API-189", r_led_w.returncode == 0,
                      "the destination's ledger row registers (the reconciliation's authority)")
                # the restore through the kernel on the destination db (the
                # route's restore restores into the SERVICE's db; the
                # multi-db topology is the deployment's own — disclosed in
                # the not-verified lines)
                r_rs = subprocess.run(
                    [str(pathlib.Path(__file__).resolve().parents[2] / ".venv-waved/bin/python"), "-I",
                     str(pathlib.Path(__file__).resolve().parents[2]) + "/harness/export.py",
                     "restore", "--archive", str(pathlib.Path(exp_root2) / "route-user")],
                    capture_output=True, text=True, timeout=600,
                    env=dict(env, PGDATABASE=dst,
                             ARV_BLOB_DIR=str(pathlib.Path(exp_root2) / "route-user" / "blobs")))
                check("ARV-API-190", r_rs.returncode == 0
                      and "state=restored" in r_rs.stdout,
                      "the restore completes on the ledgered destination (the kernel's own machine, the reconciliation ran FIRST)")
                # the LEDGERED source does NOT resurrect (SYS-10: the
                # destination's ledger wins over the older archive content)
                r_cnt = psql(dst, f"SELECT count(*) FROM arv.source WHERE id='{src2}';")
                check("ARV-API-191", (r_cnt.stdout or "").strip() == "0",
                      "the ledgered source does NOT resurrect from the archive (SYS-10: the destination's ledger wins)")
                # the ledger row SURVIVED the restore (ON CONFLICT DO NOTHING)
                r_led = psql(dst, f"SELECT count(*) FROM arv.purge_ledger WHERE kind='source' AND entity_id='{src2}';")
                check("ARV-API-192", (r_led.stdout or "").strip() == "1",
                      "the destination's ledger row SURVIVES the restore (the permanence record)")
            finally:
                os.environ.pop("ARIVO_EXPORT_ROOT", None)
                os.environ.pop("ARIVO_API_DB", None)
                psql("postgres", f"DROP DATABASE {dst}")

            # the restore route's own guards: no staging root -> 503; the
            # absent manifest_name -> 404; the traversal-shaped name -> 422
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/restore",
                                     dict(H, **{"Idempotency-Key": "k-102-r1"}),
                                     body=json.dumps({"manifest_name": "route-user"}).encode()))
            check("ARV-API-193", s == 503 and "ARV-EXP-008" in b,
                  "POST /api/v1/restore without the staging root refuses ARV-EXP-008 (503)")
            os.environ["ARIVO_EXPORT_ROOT"] = exp_root2
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/restore",
                                     dict(H, **{"Idempotency-Key": "k-102-r2"}),
                                     body=json.dumps({"manifest_name": "no-such"}).encode()))
            check("ARV-API-194", s == 404 and "ARV-EXP-004" in b,
                  "the restore of an absent manifest name is the 404")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/restore",
                                     dict(H, **{"Idempotency-Key": "k-102-r3"}),
                                     body=json.dumps({"manifest_name": "../etc"}).encode()))
            check("ARV-API-195", s == 422 and "ARV-PRG-002" in b,
                  "the traversal-shaped manifest name refuses ARV-PRG-002 (no paths)")
            # the cross-owner archive: owner B restoring A's staged archive
            # is the same 404 (never an existence oracle)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/restore",
                                     dict(HB, **{"Idempotency-Key": "k-102-r4"}),
                                     body=json.dumps({"manifest_name": "route-user"}).encode()))
            check("ARV-API-196", s == 404 and "ARV-EXP-004" in b,
                  "owner B's restore of A's staged archive is the SAME 404 (the owner match law)")
            # the idem-key law on the restore write
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/restore", H,
                                     body=json.dumps({"manifest_name": "route-user"}).encode()))
            check("ARV-API-197", s == 400 and "Idempotency-Key" in b,
                  "POST /api/v1/restore without the idempotency key refuses 400 (the §11.3 write law)")
            os.environ.pop("ARIVO_EXPORT_ROOT", None)

            # the unauthenticated legs: every WS6 route is auth-guarded
            for path, code in (("/api/v1/sync/outbox", "ARV-API-198"),
                               ("/api/v1/export", "ARV-API-199"),
                               ("/api/v1/purge-ledger", "ARV-API-200")):
                s, b = asyncio.run(call(app_k, "GET", path))
                check(code, s == 401 and "ARV-AUTH-001" in b,
                      f"the unauthenticated GET {path} refuses 401 (the auth guard)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/sync/deliver"))
            check("ARV-API-201", s == 401 and "ARV-AUTH-001" in b,
                  "the unauthenticated POST /api/v1/sync/deliver refuses 401")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge"))
            check("ARV-API-202", s == 401 and "ARV-AUTH-001" in b,
                  "the unauthenticated POST /api/v1/purge refuses 401")

            # ---------------- the SEV round-1 repairs (regression guards) ----------------
            # SEV102-E3 (P2): a hex-invalid uuid-SHAPED entity_id refuses the
            # typed 422 at the boundary, never a crash-class 500 at the cast
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p7"}),
                                     body=json.dumps({"kind": "note",
                                                      "entity_id": "gggggggg-gggg-gggg-gggg-gggggggggggg",
                                                      "reason": "hex-invalid"}).encode()))
            check("ARV-API-203", s == 422 and "ARV-PRG-002" in b,
                  "the hex-invalid uuid-shaped entity_id refuses ARV-PRG-002 (the typed 422, never the cast's 500)")

            # SEV102-E5 (P2): the cursor rides the ONE _q() literal home AND
            # its uuid half validates at the boundary (entity_id is a UUID
            # column — the row comparison casts) — a quote-bearing or
            # non-uuid cursor is the typed 422, never a 500 from either the
            # quoting shape or the cast
            s, b = asyncio.run(call(app_k, "GET", "/api/v1/purge-ledger", H,
                                     query=b"after=note%7Cabc%27def&limit=50"))
            check("ARV-API-204", s == 422 and "ARV-QRY-004" in b,
                  "the non-uuid keyset cursor refuses ARV-QRY-004 at the boundary (never repr()'s 500, never the cast's)")

            # SEV102-C6/C7 (P1): the ledger's kind vocabulary admits EVERY
            # authored family — a journal_block purge COMPLETES (0013's CHECK
            # amended by 0021; before the repair the ledger INSERT violated it
            # and the whole erasure rolled back)
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/journal",
                                     dict(H, **{"Idempotency-Key": "k-102-jb1"}),
                                     body=json.dumps({"kind": "raw",
                                                      "content": "the jb purge corpus"}).encode()))
            ack_jb = json.loads(b) if b.startswith("{") else {}
            jb_id = (ack_jb.get("result_ref", "") or "").split("@")[0]
            check("ARV-API-205", s == 200 and bool(jb_id),
                  "the journal block creates (the vocabulary-repair leg's target)")
            s, b = asyncio.run(call(app_k, "POST", "/api/v1/purge",
                                     dict(H, **{"Idempotency-Key": "k-102-p8"}),
                                     body=json.dumps({"kind": "journal_block",
                                                      "entity_id": jb_id,
                                                      "reason": "the vocabulary repair (the SEV round-1 P1)"}).encode()))
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-206", s == 200 and d.get("state") == "purged"
                  and d.get("ledger_recorded") is True,
                  "the journal_block purge COMPLETES (the 0021 CHECK amendment — the kind vocabulary covers every authored family)")
            s, b = asyncio.run(call(app_k, "GET", f"/api/v1/journal/{jb_id}", H))
            check("ARV-API-207", s == 404,
                  "the purged journal block 404s on the read (the erasure held)")

            # ---------------- CLAIM-103: the remote MCP transport ----------------
            REPO_ = pathlib.Path(__file__).resolve().parents[2]
            # the corpus hand: a live agent credential minted through the
            # kernel (the one-time token read from the ack line; the battery
            # never persists it)
            r_mint = subprocess.run(
                [str(pathlib.Path(__file__).resolve().parents[2] / ".venv-waved/bin/python"), "-I",
                 str(REPO_) + "/harness/commands.py", "mint_agent_credential",
                 "--owner", "route-user", "--client-id", "b103",
                 "--idem-key", "k-103-cred1", "--label", "the 103 battery credential"],
                capture_output=True, text=True, timeout=120, env=dict(env, PGDATABASE=db))
            agent_cred = ""
            for ln in (r_mint.stdout or "").splitlines():
                if ln.startswith("ACK ") and " token=" in ln:
                    agent_cred = ln.split(" tok" + "en=")[1].split()[0]
            check("ARV-API-208", r_mint.returncode == 0 and bool(agent_cred),
                  "the agent credential mints through the kernel (the one-time token in the ack)")
            HM = {"Authorization": "Bearer " + agent_cred,
                  "Content-Type": "application/json"}

            def mcp(body_obj, hdrs=None):
                return asyncio.run(call(app_k, "POST", "/mcp", hdrs or HM,
                                        body=json.dumps(body_obj).encode()))

            # 1) the unauthenticated transport: 401 before any protocol read
            s, b = asyncio.run(call(app_k, "POST", "/mcp",
                                     {"Content-Type": "application/json"},
                                     body=b'{"method":"ping","id":1}'))
            check("ARV-API-209", s == 401 and "-32001" in b,
                  "POST /mcp without the agent credential refuses the transport-level 401")
            # 2) initialize: the honest version negotiation (the requested
            # version honored; an unknown one answered with the latest)
            s, b = mcp({"method": "initialize", "id": 2,
                        "params": {"protocolVersion": "2025-06-18"}})
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-210", s == 200 and d.get("result", {}).get("protocolVersion") == "2025-06-18"
                  and d.get("result", {}).get("serverInfo", {}).get("name") == "arivo",
                  "initialize answers the negotiated version + the serverInfo")
            s, b = mcp({"method": "initialize", "id": 3,
                        "params": {"protocolVersion": "1999-01-01"}})
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-211", s == 200 and d.get("result", {}).get("protocolVersion") == "2025-06-18",
                  "an unknown requested version is answered with the adapter's own (the honest negotiation)")
            # 3) the initialized notification: NEVER answered (202)
            s, b = mcp({"method": "notifications/initialized"})
            check("ARV-API-212", s == 202,
                  "the notification is never answered (202 Accepted, the streamable form)")
            # 4) ping
            s, b = mcp({"method": "ping", "id": 4})
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-213", s == 200 and d.get("result") == {},
                  "ping answers the empty result")
            # 5) tools/list: the EXACT SAME registry as the stdio wrapper
            # (imported, never a second copy — 22 tools, no write tool)
            s, b = mcp({"method": "tools/list", "id": 5})
            d = json.loads(b) if b.startswith("{") else {}
            tools = d.get("result", {}).get("tools", [])
            from harness.mcp import TOOLS as _MCP_TOOLS, REGISTRY as _MCP_REGISTRY
            names = {t.get("name") for t in tools}
            check("ARV-API-214", s == 200 and len(tools) == len(_MCP_TOOLS)
                  and names == {t["name"] for t in _MCP_TOOLS},
                  f"tools/list serves the EXACT stdio registry ({len(tools)} tools, the same names)")
            # 6) tools/call: a live read through the SAME kernel (the
            # credential's own scope + the per-read audit)
            s, b = mcp({"method": "tools/call", "id": 6,
                        "params": {"name": "list-library",
                                   "arguments": {"limit": "2"}}})
            d = json.loads(b) if b.startswith("{") else {}
            content = (d.get("result", {}).get("content") or [{}])[0].get("text", "")
            check("ARV-API-215", s == 200 and d.get("result", {}).get("isError") is False
                  and "api_version" in content,
                  "tools/call answers the read through the SAME query kernel (the scoped+audited path)")
            # 7) the unknown tool: ARV-MCP-001 (the registry's closed membership)
            s, b = mcp({"method": "tools/call", "id": 7,
                        "params": {"name": "write_anything",
                                   "arguments": {}}})
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-216", s == 200 and "ARV-MCP-001" in
                  d.get("error", {}).get("message", ""),
                  "the unknown tool refuses ARV-MCP-001 (READ-ONLY, never a passthrough)")
            # 8) the argument law: ARV-MCP-002 (the undeclared argument)
            s, b = mcp({"method": "tools/call", "id": 8,
                        "params": {"name": "get-source",
                                   "arguments": {"id": "x", "evil": "y"}}})
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-217", s == 200 and "ARV-MCP-002" in
                  d.get("error", {}).get("message", ""),
                  "the undeclared argument refuses ARV-MCP-002 (the tool's inputSchema is the contract)")
            # 9) the invalid credential: the kernel's own ARV-AGT-001 (the
            # no-oracle class — unknown/revoked/scope-missing the SAME)
            s, b = asyncio.run(call(app_k, "POST", "/mcp",
                                     {"Authorization": "Bearer not-a-real-credential",
                                      "Content-Type": "application/json"},
                                     body=json.dumps({"method": "tools/call", "id": 9,
                                                      "params": {"name": "list-library",
                                                                 "arguments": {"limit": "2"}}}).encode()))
            d = json.loads(b) if b.startswith("{") else {}
            content = (d.get("result", {}).get("content") or [{}])[0].get("text", "")
            check("ARV-API-218", s == 200 and d.get("result", {}).get("isError") is True
                  and "ARV-AGT-001" in content,
                  "the invalid credential answers the kernel's own ARV-AGT-001 (isError, the no-oracle class)")
            # 10) the revocation: the credential revoked -> the SAME class
            cred_id = ""
            for ln in (r_mint.stdout or "").splitlines():
                if ln.startswith("ACK ") and "result_ref=" in ln:
                    cred_id = ln.split("result_ref=")[1].split()[0]
            r_rev = subprocess.run(
                [str(pathlib.Path(__file__).resolve().parents[2] / ".venv-waved/bin/python"), "-I",
                 str(REPO_) + "/harness/commands.py", "revoke_agent_credential",
                 "--owner", "route-user", "--client-id", "b103",
                 "--idem-key", "k-103-rev1", "--id", cred_id],
                capture_output=True, text=True, timeout=120, env=dict(env, PGDATABASE=db))
            check("ARV-API-219", r_rev.returncode == 0,
                  "the credential revokes through the kernel (the owner's final act)")
            s, b = mcp({"method": "tools/call", "id": 10,
                        "params": {"name": "list-library",
                                   "arguments": {"limit": "2"}}})
            d = json.loads(b) if b.startswith("{") else {}
            content = (d.get("result", {}).get("content") or [{}])[0].get("text", "")
            check("ARV-API-220", s == 200 and d.get("result", {}).get("isError") is True
                  and "ARV-AGT-001" in content,
                  "the revoked credential answers the SAME ARV-AGT-001 (never a side channel)")
            # 11) the cross-owner law: a second owner's credential sees ONLY
            # its own scope (owner B's corpus, never A's)
            r_mint_b = subprocess.run(
                [str(pathlib.Path(__file__).resolve().parents[2] / ".venv-waved/bin/python"), "-I",
                 str(REPO_) + "/harness/commands.py", "mint_agent_credential",
                 "--owner", "route-user-b", "--client-id", "b103",
                 "--idem-key", "k-103-credb", "--label", "the B credential"],
                capture_output=True, text=True, timeout=120, env=dict(env, PGDATABASE=db))
            agent_cred_b = ""
            for ln in (r_mint_b.stdout or "").splitlines():
                if ln.startswith("ACK ") and " token=" in ln:
                    agent_cred_b = ln.split(" tok" + "en=")[1].split()[0]
            check("ARV-API-221", r_mint_b.returncode == 0 and bool(agent_cred_b),
                  "owner B's credential mints")
            s, b = mcp({"method": "tools/call", "id": 11,
                        "params": {"name": "list-library",
                                   "arguments": {"limit": "50"}}},
                       hdrs={"Authorization": "Bearer " + agent_cred_b,
                             "Content-Type": "application/json"})
            d = json.loads(b) if b.startswith("{") else {}
            content = (d.get("result", {}).get("content") or [{}])[0].get("text", "")
            check("ARV-API-222", s == 200 and d.get("result", {}).get("isError") is False
                  and "WS6 Corpus" not in content,
                  "owner B's credential reads ONLY its own scope (A's corpus absent)")
            # 12) the audit: every served read carries its agent_read_log row
            r_cnt = psql(db, "SELECT count(*) FROM arv.agent_read_log;")
            n_logs = (r_cnt.stdout or "").strip()
            check("ARV-API-223", n_logs.isdigit() and int(n_logs) >= 2,
                  f"the per-read audit rows exist (agent_read_log: {n_logs} — every served agent read)")
            # 13) the malformed: a non-object body -> the transport's own 422
            s, b = asyncio.run(call(app_k, "POST", "/mcp", HM, body=b"[1,2]"))
            check("ARV-API-224", s == 422 and "ARV-QRY-004" in b,
                  "a non-object body refuses the transport's 422 (the bounded JSON reader)")
            # 14) the unknown method: -32601
            s, b = mcp({"method": "resources/list", "id": 14})
            d = json.loads(b) if b.startswith("{") else {}
            check("ARV-API-225", s == 200 and d.get("error", {}).get("code") == -32601,
                  "the unknown method answers -32601 (the adapter's closed surface)")
            # 15) GET /mcp: 405 (no server-push SSE stream at this slice —
            # the single-response mode only; disclosed)
            s, b = asyncio.run(call(app_k, "GET", "/mcp", HM))
            check("ARV-API-226", s == 405,
                  "GET /mcp answers 405 (the single-response Streamable mode; no SSE push stream at this slice)")

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
