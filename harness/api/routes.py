#!/usr/bin/env python3
"""harness/api/routes.py — the route adapter over the kernel (CLAIM-094;
runbook §11.2/§11.3/§11.4; INT-160/D-053).

THE ADAPTER LAW (the runbook's own): the HTTP surface calls the EXISTING
command/query kernels — never a second domain model, never duplicated business
logic. The write path invokes harness/commands.py as a bounded subprocess
(the kernel's own argv contract: --owner/--actor/--client-id/--idem-key);
the read path invokes harness/query.py the same way. The owner/actor are
DERIVED server-side from the verified token (§8.4): a request body NEVER
carries them.

The durability honest: the kernel's ACK key=value line is the ack
(commit-before-ack is the kernel's own law); this adapter surfaces the
kernel's own durability_rung/result_ref/api_version fields, and maps the
kernel's named ARV-* refusals to the §11.4 HTTP classes (the centralized
map — one place).

The import body: the runbook's §11.2 'begin import' rides the kernel's
phased import (validation -> replay/conflict -> staging -> the metadata
transaction). The FILE arrives as the request body's bytes (the adapter
stages them to a bounded temp file — the kernel's own --file path contract);
the DTO carries title OR work_id (exactly one — ARV-CAP-007's law), media_type
(the MIME grammar — ARV-CAP-009), acquired_via.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse

from harness.api import auth as _auth

REPO = pathlib.Path(__file__).resolve().parents[2]
MAX_IMPORT_BYTES = 32 * 1024 * 1024  # the bounded import body (the kernel's own cap class)
LIST_LIMIT_BOUNDS = (1, 200)          # the bounded list page (the ARV-QRY-004 contract)


class KernelRefusal(Exception):
    """A named kernel refusal (ARV-*) mapped to its §11.4 HTTP class."""

    def __init__(self, code: str, message: str, status: int):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.status = status


# the centralized §11.4 map: the kernel's named refusal families -> HTTP
_HTTP_BY_PREFIX = (
    ("ARV-AUTH", 401),      # the auth boundary's own codes
    ("ARV-QRY-004", 422),   # the list bounds (invalid input)
    ("ARV-CAP-007", 422),   # exactly-one-of title/work-id (invalid input)
    ("ARV-CAP-009", 422),   # the MIME grammar (invalid input)
    ("ARV-FMT", 422),       # the format registry (invalid input)
    ("ARV-CAP-001", 422),  # the missing file (invalid input)
    ("ARV-CMD-409", 409),   # the idempotency conflict
    # CLAIM-096 (the extraction area): the content-class refusals whose
    # kernel messages are clean prose (verified — no raw cause text on these
    # paths) surface as invalid input; ARV-EXT-002/003/006 (which CAN carry
    # observed cause text) stay on the message-replacing 500 default below
    ("ARV-EXT-001", 422),   # the empty source (no content block)
    ("ARV-EXT-005", 422),   # NUL in the text (the literal-transport class)
)


def _map_kernel_refusal(line: str) -> KernelRefusal:
    """One FAIL line of the kernel's output -> the named HTTP refusal."""
    code = line.split(":", 1)[0].replace("FAIL ", "").strip()
    msg = line.split(":", 1)[1].strip() if ":" in line else line
    for prefix, status in _HTTP_BY_PREFIX:
        if code.startswith(prefix):
            return KernelRefusal(code, msg, status)
    # the absence family (the kernel's own no-leak refusals: absent or
    # tombstone-hidden in the caller's scope) keeps the 404 class — §11.4
    if code.startswith(("ARV-QRY-001", "ARV-QRY-003", "ARV-EXT-004")):
        return KernelRefusal(code, msg, 404)
    # every OTHER named-but-unmapped kernel code is a server-side failure the
    # client cannot act on (the live example: F6's ARV-CMD-010, proven
    # reachable through this route): the 500 class, the kernel's named code
    # preserved as the diagnostic surface, the raw cause text NEVER echoed
    # (§11.4: no SQL fragments — the SEV round-1 repair, SEV-094-1)
    return KernelRefusal(code, "the command refused with a named code", 500)


def _kernel_env(db: str) -> dict:
    """The service's runtime db (PGDATABASE — the kernels' own contract;
    a service-set value, never a client one)."""
    env = dict(os.environ)
    env["PGDATABASE"] = db
    return env


async def _json_body(request: Request, max_bytes: int) -> dict:
    """Read one bounded JSON object body (the write DTOs' shared reader).
    A declared over-cap Content-Length is refused before any byte is read;
    a lying/chunked client is cut at the cap mid-stream (the import route's
    own F1 law, applied to every JSON body)."""
    declared = request.headers.get("content-length")
    if declared is not None:
        try:
            if int(declared) > max_bytes:
                raise KernelRefusal("ARV-API-413",
                                    f"the request body exceeds its {max_bytes}-byte cap",
                                    413)
        except ValueError:
            pass
    buf = bytearray()
    async for chunk in request.stream():
        buf.extend(chunk)
        if len(buf) > max_bytes:
            raise KernelRefusal("ARV-API-413",
                                f"the request body exceeds its {max_bytes}-byte cap",
                                413)
    if not buf:
        raise KernelRefusal("ARV-QRY-004", "a JSON body is required", 422)
    try:
        obj = json.loads(bytes(buf))
    except Exception:
        raise KernelRefusal("ARV-QRY-004", "the body is not valid JSON", 422)
    if not isinstance(obj, dict):
        raise KernelRefusal("ARV-QRY-004", "the body must be a JSON object", 422)
    return obj


def _run_kernel(argv: list, db: str, timeout: float = 120.0) -> dict:
    """Run the kernel as a bounded subprocess; parse its ack (the ACK
    key=value line — the kernel's own CLI contract; commit-before-ack is ITS
    law). NEVER return raw stdout to the client (§11.4: no SQL, no stack
    traces, no internal hostnames)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                           cwd=str(REPO), env=_kernel_env(db))
    except subprocess.TimeoutExpired:
        # the bound itself refuses inside the §11.4 envelope (the SEV round-1
        # repair, SEV-094-3): never a bare Starlette 500 outside it
        raise KernelRefusal("ARV-API-504",
                            "the command exceeded its time bound", 504)
    out = (r.stdout or "").strip()
    if r.returncode != 0:
        for src in (out, (r.stderr or "").strip()):
            for ln in src.splitlines():
                if ln.startswith("FAIL "):
                    raise _map_kernel_refusal(ln)
        # an unnamed kernel failure: the generic 500 class, no internals leaked
        raise KernelRefusal("ARV-API-500", "the command refused without a named code", 500)
    ack = {}
    for ln in out.splitlines():
        ln = ln.strip()
        if ln.startswith("ACK "):
            for tok in ln[4:].split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    ack[k] = v
        elif ln.startswith("{"):
            try:
                ack.update(json.loads(ln))
            except Exception:
                pass
    if not ack:
        raise KernelRefusal("ARV-API-500", "the command produced no ack object", 500)
    return ack


def _query_kernel(argv: list, db: str, timeout: float = 60.0) -> dict:
    """Run the query path; return its page: the rows (JSON objects where the
    arm prints objects, ids where the arm prints the bare-id page) + the more
    flag + the api_version (the CLI's own page contract: a '# api_version='
    header, the rows, a '# more=' trailer)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                           cwd=str(REPO), env=_kernel_env(db))
    except subprocess.TimeoutExpired:
        raise KernelRefusal("ARV-API-504", "the query exceeded its time bound", 504)
    out = (r.stdout or "").strip()
    if r.returncode != 0:
        for src in (out, (r.stderr or "").strip()):
            for ln in src.splitlines():
                if ln.startswith("FAIL "):
                    raise _map_kernel_refusal(ln)
        raise KernelRefusal("ARV-API-500", "the query refused without a named code", 500)
    rows, more, api_version = [], False, 1
    for ln in out.splitlines():
        ln = ln.strip()
        if ln.startswith("# api_version="):
            try:
                api_version = int(ln.split("=", 1)[1])
            except Exception:
                pass
        elif ln.startswith("# more="):
            more = ln.split("=", 1)[1].strip().lower() == "true"
        elif ln.startswith("#"):
            continue
        elif ln.startswith("{"):
            try:
                rows.append(json.loads(ln))
            except Exception:
                pass
        elif ln:
            rows.append({"id": ln})
    return {"rows": rows, "more": more, "api_version": api_version}


def build_router(verifier: "_auth.Verifier", db: str) -> APIRouter:
    """Compose the area routers over the kernels. The db: the SERVICE's own
    runtime database name (the pgprod path's own parameter — never a client
    value)."""
    router = APIRouter()

    # ---- the verified context (every route; §8.3/§8.4) ----
    async def verified(authorization: str = Header(default="")) -> dict:
        claims = verifier.verify_bearer(authorization)
        owner = verifier.derive_owner(claims)
        return {"owner_scope": owner, "claims": claims}

    # ---- POST /api/v1/imports: the §11.2 'begin import' ----
    @router.post("/api/v1/imports")
    async def begin_import(request: Request,
                           ctx: dict = Depends(verified),
                           idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        # F1 (the handoff revalidation): the bound is enforced BEFORE and
        # DURING the read — a declared over-cap Content-Length is refused
        # without reading a byte, and a lying/chunked client is cut off at
        # the cap mid-stream (never an unbounded buffer)
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                if int(declared) > MAX_IMPORT_BYTES:
                    raise KernelRefusal(
                        "ARV-API-413",
                        f"the import body exceeds its {MAX_IMPORT_BYTES}-byte cap "
                        "(refused on the declared Content-Length before any byte was read)",
                        413)
            except ValueError:
                pass  # a malformed length: the streaming cap below still bounds it
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > MAX_IMPORT_BYTES:
                raise KernelRefusal("ARV-API-413",
                                    f"the import body exceeds its {MAX_IMPORT_BYTES}-byte cap",
                                    413)
        body = bytes(body)
        # the DTO: the metadata travels the query parameters (the body IS the
        # bytes — the kernel's --file contract); title XOR work_id
        q = request.query_params
        title, work_id = q.get("title"), q.get("work_id")
        media_type = q.get("media_type", "text/plain")
        acquired_via = q.get("acquired_via", "api-import")
        # F5b (the handoff revalidation): BOTH selectors together never reach
        # the kernel (it would see only --title) — the exactly-one-of law is
        # enforced HERE, where the drop would otherwise be silent
        if title is not None and work_id is not None:
            raise KernelRefusal("ARV-CAP-007",
                                "exactly one of title (a new work) or work_id (an "
                                "existing work) is required — never both", 422)
        # stage the bytes to a bounded temp file (the kernel's own path law)
        tmpdir = tempfile.mkdtemp(prefix="arv_api_import_")
        tmp = pathlib.Path(tmpdir) / "import.bin"
        try:
            tmp.write_bytes(body)
            argv = [sys.executable, str(REPO / "harness" / "commands.py"),
                    "import_source",
                    "--owner", ctx["owner_scope"],
                    "--actor", "owner",
                    "--client-id", ctx["claims"].get("client_id", "api-v1"),
                    "--idem-key", idempotency_key,
                    "--file", str(tmp),
                    "--media-type", media_type,
                    "--acquired-via", acquired_via]
            if title is not None:
                argv += ["--title", title]
            elif work_id is not None:
                argv += ["--work-id", work_id]
            ack = _run_kernel(argv, db, timeout=300.0)
            return JSONResponse(status_code=200, content=ack)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # ---- GET /api/v1/sources: the §11.2 'list library' ----
    @router.get("/api/v1/sources")
    async def list_sources(ctx: dict = Depends(verified),
                           limit: str = "50", after: str = ""):
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004",
                                "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "list-library", "--owner", ctx["owner_scope"],
                "--limit", str(limit_i)]
        if after:
            argv += ["--after", after]
        page = _query_kernel(argv, db)
        return JSONResponse(status_code=200, content=page)

    # ---- GET /api/v1/sources/{id}: the §11.2 'detail' ----
    @router.get("/api/v1/sources/{source_id}")
    async def source_detail(source_id: str, ctx: dict = Depends(verified)):
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-source", "--owner", ctx["owner_scope"],
                "--id", source_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict) or "id" not in rows[0]:
            # §11.4: never leak another owner's object existence
            raise KernelRefusal("ARV-QRY-404", "no such source for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # ---- CLAIM-096: the §11.2 'Extraction' area (request, status) ----
    # POST /api/v1/sources/{id}/extraction — 'request extraction'. The write
    # law (§11.3): the Idempotency-Key is required; the SAME key resumes a
    # crashed building generation and replays a terminal one (the kernel's
    # own idempotency machine — the safe RETRY); a NEW key builds a NEW
    # generation (superseding the old — the safe REBUILD). The kernel argv
    # carries ONLY server-derived identity (owner from the verified token).
    @router.post("/api/v1/sources/{source_id}/extraction")
    async def request_extraction(source_id: str,
                                 ctx: dict = Depends(verified),
                                 idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "extract.py"),
                "--owner", ctx["owner_scope"],
                "--actor", "owner",
                "--client-id", ctx["claims"].get("client_id", "api-v1"),
                "--idem-key", idempotency_key,
                "--source-id", source_id]
        ack = _run_kernel(argv, db, timeout=300.0)
        return JSONResponse(status_code=200, content=ack)

    # GET /api/v1/sources/{id}/extraction — 'job status': the truthful
    # readiness state derived from the generation rows (ready / building /
    # failed / never_requested; never a partial extraction presented as
    # complete — passage_count counts only the CURRENT generation's rows)
    @router.get("/api/v1/sources/{source_id}/extraction")
    async def extraction_status(source_id: str, ctx: dict = Depends(verified)):
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "extraction-status", "--owner", ctx["owner_scope"],
                "--id", source_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict) or "source_id" not in rows[0]:
            # §11.4: never leak another owner's object existence
            raise KernelRefusal("ARV-QRY-404", "no such source for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # ---- CLAIM-097: the §11.2 'Reading' area (the directive's Workstream 4,
    # family 1 — content + reading position/session state) ----
    # GET /api/v1/sources/{id}/position — 'get position': the reopen answer
    # (the last-saved window + the serving-generation binding; the honest
    # no_position_saved state is a 200 ANSWER, never a failure — the kernel's
    # own contract)
    @router.get("/api/v1/sources/{source_id}/position")
    async def get_position(source_id: str, ctx: dict = Depends(verified)):
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-position", "--owner", ctx["owner_scope"],
                "--source", source_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            # §11.4: never leak another owner's object existence
            raise KernelRefusal("ARV-QRY-404", "no such source for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # PUT /api/v1/sources/{id}/position — 'save position': the §11.3 write
    # law (idempotency required); the serialized save rides the kernel's own
    # advisory-lock transaction (competing savers serialize; the ordinal law
    # holds by construction). start/end are decoded-text offsets.
    @router.put("/api/v1/sources/{source_id}/position")
    async def save_position(source_id: str, request: Request,
                            ctx: dict = Depends(verified),
                            idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        body = await _json_body(request, max_bytes=64 * 1024)
        try:
            start, end = int(body["start"]), int(body["end"])
        except (KeyError, TypeError, ValueError):
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry integer start/end offsets "
                                "(decoded-text coordinates)", 422)
        argv = [sys.executable, str(REPO / "harness" / "commands.py"),
                "save_position",
                "--owner", ctx["owner_scope"],
                "--actor", "owner",
                "--client-id", ctx["claims"].get("client_id", "api-v1"),
                "--idem-key", idempotency_key,
                "--source-id", source_id,
                "--start", str(start),
                "--end", str(end)]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # POST /api/v1/sources/{id}/session-events — the session/dwell surface
    # (D-010's closed vocabulary; the coarse span + dwell in the body)
    @router.post("/api/v1/sources/{source_id}/session-events")
    async def record_session_event(source_id: str, request: Request,
                                   ctx: dict = Depends(verified),
                                   idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        body = await _json_body(request, max_bytes=64 * 1024)
        ev = body.get("event")
        if ev not in ("session_start", "checkpoint", "dwell", "session_end"):
            raise KernelRefusal("ARV-SES-004",
                                "the event kind must be one of the closed "
                                "vocabulary (session_start|checkpoint|dwell|session_end)", 422)
        try:
            start, end = int(body["start"]), int(body["end"])
        except (KeyError, TypeError, ValueError):
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry integer start/end offsets "
                                "(decoded-text coordinates)", 422)
        argv = [sys.executable, str(REPO / "harness" / "commands.py"),
                "record_session",
                "--owner", ctx["owner_scope"],
                "--actor", "owner",
                "--client-id", ctx["claims"].get("client_id", "api-v1"),
                "--idem-key", idempotency_key,
                "--source-id", source_id,
                "--event", ev,
                "--start", str(start),
                "--end", str(end)]
        if ev == "dwell":
            try:
                argv += ["--dwell-ms", str(int(body["dwell_ms"]))]
            except (KeyError, TypeError, ValueError):
                raise KernelRefusal("ARV-QRY-004",
                                    "a dwell event requires an integer dwell_ms", 422)
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # GET /api/v1/reading-state — the derived current-reading view (every
    # source of the page with its last-saved position or the honest
    # no_position_saved state); bounded + paginated (§11.3)
    @router.get("/api/v1/reading-state")
    async def reading_state(ctx: dict = Depends(verified),
                            limit: str = "50", after: str = ""):
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-reading-state", "--owner", ctx["owner_scope"],
                "--limit", str(limit_i)]
        if after:
            argv += ["--after", after]
        page = _query_kernel(argv, db)
        return JSONResponse(status_code=200, content=page)

    # GET /api/v1/session-events — the owner's session/dwell event stream
    # (bounded + paginated; the recorded rows only, never retargeted)
    @router.get("/api/v1/session-events")
    async def list_session_events(ctx: dict = Depends(verified),
                                  limit: str = "50", after: str = ""):
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "list-session-events", "--owner", ctx["owner_scope"],
                "--limit", str(limit_i)]
        if after:
            argv += ["--after", after]
        page = _query_kernel(argv, db)
        return JSONResponse(status_code=200, content=page)

    # GET /api/v1/anchors/{id} — 'source/read data': the typed anchor
    # resolution (the offsets, the digests, the context windows, the current
    # generation binding — the content-addressed reading surface)
    @router.get("/api/v1/anchors/{anchor_id}")
    async def resolve_anchor(anchor_id: str, ctx: dict = Depends(verified)):
        if not anchor_id or len(anchor_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the anchor id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "resolve-anchor", "--owner", ctx["owner_scope"],
                "--id", anchor_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            raise KernelRefusal("ARV-QRY-404", "no such anchor for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    return router


def install(app, verifier: "_auth.Verifier", db: str):
    """Attach the area router + the centralized error handlers to the app."""
    router = build_router(verifier, db)
    app.include_router(router)

    @app.exception_handler(KernelRefusal)
    async def _kernel_refusal(request: Request, exc: KernelRefusal):
        return JSONResponse(
            status_code=exc.status,
            content={"error": {"code": exc.code,
                              "message": exc.message,
                              "api_version": 1}})
