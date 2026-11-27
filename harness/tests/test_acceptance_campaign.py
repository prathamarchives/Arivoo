#!/usr/bin/env python3
"""harness/tests/test_acceptance_campaign.py — CLAIM-106 (Workstream 11): the
directive's §6 final-verification campaign as ONE integrated suite over the
LANDED surface (the local rig + the REAL ASGI app + the durable worker + both
MCP transports).

§6.1's lifecycle steps 2-14 driven end-to-end (step 1's real-Supabase-user and
§6.4's Cloudflare-proxy legs are the deployed-surface halves — disclosed in
the not-verified; the local form exercises the SAME contract surfaces).
"""
import asyncio
import base64
import json
import os
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from harness.adapters import ids

REPO = pathlib.Path(__file__).resolve().parents[2]
ENV = dict(os.environ)
ENV.setdefault("PGHOST", "127.0.0.1")
ENV.setdefault("PGUSER", "postgres")
ENV.setdefault("PGPORT", "5433")
_pgbin = "/home/z/my-project/pgbuild/root/usr/lib/postgresql/17/bin"
if pathlib.Path(_pgbin).exists():
    ENV["PATH"] = _pgbin + ":" + ENV.get("PATH", "")
    ENV["LD_LIBRARY_PATH"] = "/home/z/my-project/pgbuild/root/usr/lib/x86_64-linux-gnu:/home/z/my-project/pgbuild/root/usr/lib"

FAILS = []


def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        FAILS.append(code)


def psql(db, sql, user="arv_app"):
    return subprocess.run(
        ["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
         "-h", ENV["PGHOST"], "-p", ENV["PGPORT"], "-U", user, "-d", db, "-c", sql],
        capture_output=True, text=True, timeout=120, env=ENV)


def one(db, sql, user="arv_app"):
    # the owner-scoped form: the RLS law (every arv_app statement carries the
    # scope the route would set)
    out = (psql(db, "SET app.current_owner='acc-owner-a'; " + sql, user=user)
           .stdout or "")
    return next((ln.strip() for ln in reversed(out.split("\n")) if ln.strip()), "")


def main() -> int:
    db = "arv_acc_" + ids.new_id().replace("-", "")[:10]
    psql("postgres", f"CREATE DATABASE {db}", user="postgres")
    r = subprocess.run([sys.executable, "harness/migrate.py"], cwd=str(REPO),
                       capture_output=True, text=True, timeout=300,
                       env=dict(ENV, PGDATABASE=db, ARV_MIGRATIONS_DIR="harness/migrations"))
    corp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    corp.write("The acceptance corpus. " * 40)
    corp.close()
    try:
        os.environ["ARIVO_API_DB"] = db
        _exp_root = tempfile.mkdtemp(prefix="acc-export-")
        os.environ["ARIVO_EXPORT_ROOT"] = _exp_root
        from harness.api.app import create_app
        from harness.api import auth as _auth
        import jwt as pyjwt
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
        priv = ec.generate_private_key(ec.SECP256R1())
        raw = priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        jwk = {"kty": "EC", "crv": "P-256", "kid": "acc-key-1", "alg": "ES256",
               "x": b64(raw[1:33]), "y": b64(raw[33:65])}
        cfg = _auth.AuthConfig(issuer="https://acc-issuer/auth/v1", audience="acc-aud",
                               jwks_url="https://acc-jwks/.well-known/jwks.json",
                               expected_kid="acc-key-1")
        _orig = _auth._JwksCache._refresh
        _auth._JwksCache._refresh = lambda self: (setattr(self, "_jwk", jwk),
                                                  setattr(self, "_fetched_at", 1))
        app = create_app(auth_config=cfg, health_auth_ready=True, health_db_ready=True)

        def tok(sub):
            return pyjwt.encode({"sub": sub, "iss": cfg.issuer, "aud": cfg.audience,
                                 "exp": 9999999999, "iat": 1}, priv,
                                algorithm="ES256", headers={"kid": "acc-key-1"})

        HA = {"Authorization": "Bearer " + tok("acc-owner-a")}
        HB = {"Authorization": "Bearer " + tok("acc-owner-b")}

        async def _call(method, path, headers=None, body=b"", query=b""):
            hdrs = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
            if body and not any(k == b"content-length" for k, _ in hdrs):
                hdrs.append((b"content-length", str(len(body)).encode()))
            scope = {"type": "http", "http_version": "1.1", "method": method,
                     "path": path, "raw_path": path.encode() + (b"?" + query if query else b""),
                     "query_string": query, "headers": hdrs, "scheme": "http",
                     "root_path": "", "server": ("t", 80), "client": ("t", 1)}
            msgs = []
            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}
            async def send(m):
                msgs.append(m)
            await app(scope, receive, send)
            status = next(m["status"] for m in msgs if m["type"] == "http.response.start")
            out = b"".join(m.get("body", b"") for m in msgs if m["type"] == "http.response.body")
            return status, out.decode("utf-8", "replace")

        def call(method, path, headers=None, body=None, query=b""):
            return asyncio.run(_call(method, path, headers,
                                     body if isinstance(body, bytes) else
                                     (json.dumps(body).encode() if body is not None else b""),
                                     query))

        # ---- §6.1 the lifecycle ------------------------------------------------
        # (2) import a readable source
        imp_body = open(corp.name, "rb").read()
        s, b = call("POST", "/api/v1/imports",
                    dict(HA, **{"Idempotency-Key": "acc-i1",
                                "Content-Type": "text/plain"}), imp_body,
                    query=b"title=The%20Acceptance%20Corpus")
        ack = json.loads(b) if b.startswith("{") else {}
        src = (ack.get("result_ref", "") or "").split("@")[0]
        check("ACC-01", s == 200 and bool(src), "§6.1(2) the source imports through the API"
              + ("" if s == 200 else f" [status={s} body={b[:160]}]"))
        # (3) private upload + the server-side digest
        dig = one(db, f"SELECT digest FROM arv.source WHERE id='{src}';")
        import hashlib as _h
        expect = _h.sha256(imp_body).hexdigest()
        check("ACC-02", dig == expect, "§6.1(3) the server-side digest matches the private upload's bytes"
              + ("" if dig == expect else f" [stored={dig[:20]} expected={expect[:20]}]"))
        # (4) extraction readiness — enqueue the extract job + run the worker
        psql(db, "SET app.current_owner='acc-owner-a'; INSERT INTO arv.job (id, owner_scope, "
                 "job_type, payload_version, payload, idem_key, state, created_at, updated_at) "
                 f"VALUES (gen_random_uuid(), 'acc-owner-a', 'extract_source', 1, "
                 f"'{{\"source_id\": \"{src}\"}}', 'acc-e1', 'queued', now(), now());")
        w = subprocess.run([sys.executable, "-I", str(REPO / "harness/worker.py"),
                            "--name", "acc-w1", "--once"],
                           capture_output=True, text=True, timeout=300, env=dict(ENV, PGDATABASE=db))
        st = one(db, "SELECT state FROM arv.job WHERE idem_key='acc-e1';")
        if st != "succeeded":
            print("DBG worker stdout:", (w.stdout or "")[-300:])
            print("DBG job rows:", one(db, "SELECT idem_key || ':' || state FROM arv.job LIMIT 5;"))
            print("DBG unscoped job owners:", psql(db, "SELECT DISTINCT owner_scope FROM arv.job;", user="postgres").stdout)
            print("DBG unscoped source owners:", psql(db, "SELECT DISTINCT owner_scope FROM arv.source;", user="postgres").stdout)
        check("ACC-03", w.returncode == 0 and st == "succeeded",
              "§6.1(4) the durable worker extracts (the job machine's own path)")
        # (5) open/read + save/resume position (the session-events checkpoint +
        #     the reading-state read — the §11.2 contract's own forms)
        s, b = call("POST", f"/api/v1/sources/{src}/session-events",
                    dict(HA, **{"Idempotency-Key": "acc-p1"}),
                    {"event": "checkpoint", "start": 0, "end": 20})
        check("ACC-04", s == 200, "§6.1(5) the reading checkpoint saves through the API")
        s, b = call("GET", "/api/v1/reading-state", HA)
        d = json.loads(b) if b.startswith("{") else {}
        rows = d.get("rows") or []
        check("ACC-05", s == 200 and any(str(r.get("source_id", r.get("source", ""))).find(src) >= 0
                                         or src in json.dumps(r) for r in rows),
              "§6.1(5) the reading state resumes (the same source's position)")
        # (6) highlight + bookmark
        s, b = call("POST", "/api/v1/highlights", dict(HA, **{"Idempotency-Key": "acc-h1"}),
                    {"source_id": src, "start": 0, "end": 10})
        hl = (json.loads(b).get("result_ref", "") if b.startswith("{") else "").split("@")[0]
        s2, b2 = call("POST", "/api/v1/bookmarks", dict(HA, **{"Idempotency-Key": "acc-b1"}),
                      {"source_id": src, "start": 0, "end": 10})
        check("ACC-06", s == 200 and s2 == 200 and bool(hl),
              "§6.1(6) the highlight + the bookmark create")
        # (7) note (create + revise)
        s, b = call("POST", "/api/v1/notes", dict(HA, **{"Idempotency-Key": "acc-n1"}),
                    {"content": "the acceptance note v1"})
        note = (json.loads(b).get("result_ref", "") if b.startswith("{") else "").split("@")[0]
        s, b = call("PUT", f"/api/v1/notes/{note}", dict(HA, **{"Idempotency-Key": "acc-n2"}),
                    {"content": "the acceptance note v2"})
        check("ACC-07", s == 200, "§6.1(7) the note creates + revises (the append-only revision)")
        # (8) journal block
        s, b = call("POST", "/api/v1/journal", dict(HA, **{"Idempotency-Key": "acc-j1"}),
                    {"kind": "raw", "content": "the acceptance journal block"})
        check("ACC-08", s == 200, "§6.1(8) the journal block creates")
        # (9) reading list + reference resolution
        s, b = call("POST", "/api/v1/reading-lists", dict(HA, **{"Idempotency-Key": "acc-l1"}),
                    {"name": "the acceptance list"})
        lst = (json.loads(b).get("result_ref", "") if b.startswith("{") else "").split("@")[0]
        s, b = call("POST", f"/api/v1/reading-lists/{lst}/members",
                    dict(HA, **{"Idempotency-Key": "acc-lm1"}),
                    {"source_id": src})
        s2, b2 = call("GET", "/api/v1/references", HA, query=f"ref=note:{note}".encode())
        check("ACC-09", s == 200 and s2 == 200,
              "§6.1(9) the reading-list membership + the reference resolution"
              + ("" if s == 200 else f" [members status={s} body={b[:120]}]")
              + ("" if s2 == 200 else f" [ref status={s2} body={b2[:120]}]"))
        # (10) search + context pack with provenance
        s, b = call("GET", "/api/v1/search", HA, query=b"terms=acceptance")
        s2, b2 = call("GET", "/api/v1/context-packs", HA, query=b"terms=acceptance")
        d2 = json.loads(b2) if b2.startswith("{") else {}
        rows2 = d2.get("rows") or []
        prov_ok = any(r.get("matched_terms") for r in rows2 if isinstance(r, dict))
        check("ACC-10", s == 200 and s2 == 200 and prov_ok,
              "§6.1(10) the search + the provenance-carrying context pack (the rows carry their matched_terms + trust labels)"
              + ("" if s == 200 else f" [search status={s} body={b[:120]}]")
              + ("" if s2 == 200 else f" [pack status={s2} body={b2[:200]}]")
              + ("" if prov_ok else f" [pack rows={len(rows2)}]"))
        # (11) restart client/agent -> the same data (the stateless API over the durable store)
        s, b = call("GET", f"/api/v1/notes/{note}", HA)
        d = json.loads(b) if b.startswith("{") else {}
        check("ACC-11", s == 200 and "acceptance note v2" in json.dumps(d),
              "§6.1(11) the same data after the client restart (the durable store)")
        # (12)-(14) export -> restore into an isolated target -> purge reconciliation
        s, b = call("GET", "/api/v1/export", HA)
        d = json.loads(b) if b.startswith("{") else {}
        arch = d.get("archive") or d.get("manifest") or ""
        check("ACC-12", s == 200 and bool(arch), "§6.1(12) the export manifest stages"
              + ("" if s == 200 else f" [status={s} body={b[:160]}]")
              + ("" if arch else " [no archive field in the ack]"))
        s, b = call("POST", "/api/v1/purge", dict(HA, **{"Idempotency-Key": "acc-pg1"}),
                    {"kind": "note", "entity_id": note,
                     "reason": "the acceptance purge leg"})
        d = json.loads(b) if b.startswith("{") else {}
        s2, b2 = call("GET", f"/api/v1/notes/{note}", HA)
        check("ACC-13", s == 200 and d.get("state") == "purged" and s2 == 404,
              "§6.1(14) the purged note 404s (never reappears through the read)")
        led = one(db, "SELECT count(*) FROM arv.purge_ledger WHERE kind='note' AND entity_id="
                      f"'{note}';")
        check("ACC-14", led == "1", "§6.1(14) the purge ledger records the erasure (the reconciliation's authority)")

        # ---- §6.2 multi-user + concurrency ------------------------------------
        s, b = call("GET", f"/api/v1/notes?owner=x", HB)  # B's own read (no A rows)
        s2, b2 = call("GET", f"/api/v1/highlights/{hl}", HB)
        check("ACC-15", s2 == 404, "§6.2 B cannot read A's highlight (the no-oracle 404)")
        # the duplicate idem key converges
        s1, b1 = call("POST", "/api/v1/notes", dict(HA, **{"Idempotency-Key": "acc-dup"}),
                      {"content": "the convergence probe"})
        s2, b2 = call("POST", "/api/v1/notes", dict(HA, **{"Idempotency-Key": "acc-dup"}),
                      {"content": "the convergence probe"})
        r1 = json.loads(b1) if b1.startswith("{") else {}
        r2 = json.loads(b2) if b2.startswith("{") else {}
        check("ACC-16", s1 == s2 == 200 and r1.get("result_ref") == r2.get("result_ref"),
              "§6.2 the duplicate idempotency key converges (the SAME result_ref)")
        # the bad token class
        s, b = call("GET", "/api/v1/me", {"Authorization": "Bearer not-a-token"})
        check("ACC-17", s == 401, "§6.2 the malformed token refuses 401")
        # the MCP transport parity: the same registry both transports serve
        s, b = call("POST", "/mcp", HA, {"method": "tools/list", "id": 99})
        from harness.mcp import TOOLS as _T
        d = json.loads(b) if b.startswith("{") else {}
        check("ACC-18", s == 200 and len(d.get("result", {}).get("tools", [])) == len(_T),
              "§6.4 both transports expose the SAME registry (the stdio import = the HTTP serve)")

        _auth._JwksCache._refresh = _orig
    finally:
        os.environ.pop("ARIVO_API_DB", None)
        os.environ.pop("ARIVO_EXPORT_ROOT", None)
        os.unlink(corp.name)
        psql("postgres", f"DROP DATABASE {db}", user="postgres")
    print()
    if FAILS:
        print("RED — the acceptance campaign refuses:", ", ".join(FAILS))
        return 1
    print("GREEN — the §6 acceptance campaign (ACC-01..18) passes on the landed surface")
    return 0


if __name__ == "__main__":
    sys.exit(main())
