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


def _q(s: str) -> str:
    """One SQL single-quoted literal (the adapters' own rule: '' doubling)."""
    return "'" + str(s).replace("'", "''") + "'"


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
    # CLAIM-098 (the capture/bookmark families + the 097 named followup's
    # reader-family write legs): the lifecycle alternation and edit-on-
    # tombstoned refusals are conflicts with the object's CURRENT state —
    # the 409 class; the offset/content classes are client-actionable 422s;
    # the absence codes join the no-leak 404 family below
    ("ARV-HLC-002", 409),   # revise on tombstoned (restore first)
    ("ARV-HLC-003", 409),   # the tombstone alternation
    ("ARV-HLC-004", 409),   # the restore alternation
    ("ARV-BMK-002", 409),   # move on tombstoned (restore first)
    ("ARV-BMK-003", 409),   # the bookmark tombstone alternation
    ("ARV-BMK-004", 409),   # the bookmark restore alternation
    ("ARV-CAP-003", 422),   # the capture offsets (never clamped, never guessed)
    ("ARV-POS-003", 422),   # the position offsets (the same law)
    ("ARV-SES-003", 422),   # the session-event offsets (the same law)
    ("ARV-CAP-008", 422),   # the content class (not valid UTF-8 / underivable view)
    # CLAIM-099 (the notes/journal/references families): the authored-content
    # channel/grammar/vocabulary refusals are client-actionable 422s; the note
    # lifecycle alternation joins the 409 family; the absence codes join the
    # no-leak 404 family below
    ("ARV-NTE-006", 422),   # the reference grammar (kind/id/@rev)
    ("ARV-NTE-008", 422),   # the duplicate reference target (a set, not a list)
    ("ARV-NTE-009", 422),   # NUL in the authored content (the lossless law)
    ("ARV-NTE-010", 422),   # the content channel law
    ("ARV-JNL-002", 422),   # the writing lab's kind vocabulary (raw | creative)
    ("ARV-JNL-003", 422),   # the journal content channel law
    ("ARV-JNL-004", 422),   # the empty/NUL journal body (a block is writing)
    ("ARV-REF-002", 422),   # the reference grammar at the resolution boundary
    ("ARV-NTE-002", 409),   # the note revise on tombstoned (restore first)
    ("ARV-NTE-004", 409),   # the note tombstone alternation
    ("ARV-NTE-005", 409),   # the note restore alternation
    # CLAIM-100 (the reading-lists family): the name law is a client-actionable
    # 422; the list/binding no-oracles join the 404 family below
    ("ARV-RLS-003", 422),   # the list name law (1..512, no NULs)
    # CLAIM-101 (the retrieval API): the read-side token bound is a
    # client-actionable 422 (the write-side KWR-002 stays on the fallback
    # map — the map-family followup's own slice)
    ("ARV-KWR-003", 422),   # the over-long search term (the read-side bound)
    # CLAIM-102 (the sync/export/purge families): the delivery/manifest/DTO
    # classes are client-actionable 422s; the state conflicts (the non-clean
    # destination, the append-only ledger law, the purge alternations) are
    # the 409 class — each names the CURRENT state, never an oracle
    ("ARV-SYN-013", 422),   # the undeliverable payload class (invalid input)
    ("ARV-EXP-002", 409),   # the non-clean destination (the current state)
    ("ARV-EXP-003", 422),   # the malformed/tampered manifest (invalid input)
    ("ARV-EXP-004", 422),   # the missing/corrupt archive blob (invalid input)
    ("ARV-EXP-005", 422),   # the unknown manifest format (invalid input)
    ("ARV-PRG-001", 409),   # the append-only ledger law (the current state)
    ("ARV-PRG-002", 422),   # the governed-purge DTO (invalid input)
    ("ARV-PRG-003", 422),   # the purge-target refusal (invalid input)
    ("ARV-PRG-004", 409),   # the already-purged alternation (the current state)
    ("ARV-PRG-005", 409),   # the purge of a purged source's capture (the state)
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
    # (CLAIM-098 extends the family: the capture/bookmark absence codes + the
    # reader-family write legs' source-absence codes — absent and another
    # owner's are the SAME refusal everywhere, never a 403 existence oracle)
    if code.startswith(("ARV-QRY-001", "ARV-QRY-003", "ARV-EXT-004",
                        "ARV-HLC-001", "ARV-BMK-001", "ARV-CAP-002",
                        "ARV-POS-001", "ARV-SES-001", "ARV-NTE-001",
                        "ARV-JNL-001", "ARV-NTE-003", "ARV-JNL-005",
                        "ARV-REF-001", "ARV-RLS-001", "ARV-RLS-002")):
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

    # the shared bounded-list read (the §11.3 list laws: the integer bound,
    # the ARV-QRY-004 refusal, the keyset cursor) over the kernel's own
    # list arms — one implementation, every family
    async def _bounded_list(ctx: dict, arm: str, limit: str, after: str):
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                arm, "--owner", ctx["owner_scope"],
                "--limit", str(limit_i)]
        if after:
            argv += ["--after", after]
        page = _query_kernel(argv, db)
        return JSONResponse(status_code=200, content=page)

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

    # ---- CLAIM-098: the §11.2 Highlights + Bookmarks families (the
    # directive's Workstream 4, families 2-3: the capture lifecycle over the
    # kernel's own machines — create/revise|move/tombstone/restore/list/
    # history; the selected text and anchors are DERIVED server-side, never
    # client-supplied; the lifecycle alternation rides the kernel's own
    # advisory-lock state machine) ----

    async def _offset_body(request: Request) -> tuple:
        """The shared capture write DTO: integer start/end offsets (the
        decoded-text coordinate law — never clamped, never guessed)."""
        body = await _json_body(request, max_bytes=64 * 1024)
        try:
            return int(body["start"]), int(body["end"])
        except (KeyError, TypeError, ValueError):
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry integer start/end offsets "
                                "(decoded-text coordinates)", 422)

    def _capture_argv(command: str, ctx: dict, idem_key: str) -> list:
        return [sys.executable, str(REPO / "harness" / "commands.py"),
                command,
                "--owner", ctx["owner_scope"],
                "--actor", "owner",
                "--client-id", ctx["claims"].get("client_id", "api-v1"),
                "--idem-key", idem_key]

    # POST /api/v1/highlights — 'create': the §11.3 write law; the selected
    # text is DERIVED from the source's stored bytes at the given offsets
    # (a client never supplies anchor truth — the kernel's own §6 law)
    @router.post("/api/v1/highlights")
    async def create_highlight(request: Request, ctx: dict = Depends(verified),
                               idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        body = await _json_body(request, max_bytes=64 * 1024)
        source_id = body.get("source_id")
        if not source_id or not isinstance(source_id, str) or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the body must carry a source_id", 422)
        try:
            start, end = int(body["start"]), int(body["end"])
        except (KeyError, TypeError, ValueError):
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry integer start/end offsets "
                                "(decoded-text coordinates)", 422)
        argv = _capture_argv("create_highlight", ctx, idempotency_key) + \
            ["--source-id", source_id, "--start", str(start), "--end", str(end)]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # GET /api/v1/highlights — 'list': the bounded page over the caller's
    # own captures (tombstoned hidden — the kernel's own LIST_SQL convention)
    @router.get("/api/v1/highlights")
    async def list_highlights(ctx: dict = Depends(verified),
                              limit: str = "50", after: str = ""):
        return await _bounded_list(ctx, "list-captures", limit, after)

    # GET /api/v1/highlights/{id} — 'read': the current revision + the anchor
    # binding; tombstoned is the hidden 404 (the governed history retains it)
    @router.get("/api/v1/highlights/{highlight_id}")
    async def get_highlight(highlight_id: str, ctx: dict = Depends(verified)):
        if not highlight_id or len(highlight_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the highlight id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-capture", "--owner", ctx["owner_scope"],
                "--id", highlight_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            raise KernelRefusal("ARV-QRY-404", "no such highlight for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # GET /api/v1/highlights/{id}/history — 'history': the governed view
    # (every revision + every lifecycle event, tombstoned ids included)
    @router.get("/api/v1/highlights/{highlight_id}/history")
    async def highlight_history(highlight_id: str, ctx: dict = Depends(verified)):
        if not highlight_id or len(highlight_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the highlight id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-history", "--owner", ctx["owner_scope"],
                "--id", highlight_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows:
            raise KernelRefusal("ARV-QRY-404", "no such highlight for this owner", 404)
        return JSONResponse(status_code=200, content=page)

    # PUT /api/v1/highlights/{id} — 'revise': the §11.3 write law; a NEW
    # immutable revision at the new offsets (the kernel's serialized edit
    # transition; tombstoned refuses — restore first)
    @router.put("/api/v1/highlights/{highlight_id}")
    async def revise_highlight(highlight_id: str, request: Request,
                               ctx: dict = Depends(verified),
                               idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not highlight_id or len(highlight_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the highlight id is malformed", 422)
        start, end = await _offset_body(request)
        argv = _capture_argv("revise_highlight", ctx, idempotency_key) + \
            ["--id", highlight_id, "--start", str(start), "--end", str(end)]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # DELETE /api/v1/highlights/{id} — 'tombstone': the §3.3 delete
    # transition (hidden from ordinary retrieval; the governed history keeps
    # everything; the alternation is the kernel's own advisory-lock machine)
    @router.delete("/api/v1/highlights/{highlight_id}")
    async def tombstone_highlight(highlight_id: str, ctx: dict = Depends(verified),
                                  idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not highlight_id or len(highlight_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the highlight id is malformed", 422)
        argv = _capture_argv("tombstone_highlight", ctx, idempotency_key) + \
            ["--id", highlight_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # POST /api/v1/highlights/{id}/restore — 'restore': back to ordinary
    # retrieval; the revisions were never touched
    @router.post("/api/v1/highlights/{highlight_id}/restore")
    async def restore_highlight(highlight_id: str, ctx: dict = Depends(verified),
                                idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not highlight_id or len(highlight_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the highlight id is malformed", 422)
        argv = _capture_argv("restore_highlight", ctx, idempotency_key) + \
            ["--id", highlight_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # POST /api/v1/bookmarks — 'create': the stable return location (identity
    # + the version-tied anchor; NO copy of source content — the row carries
    # no text; the structural law)
    @router.post("/api/v1/bookmarks")
    async def create_bookmark(request: Request, ctx: dict = Depends(verified),
                              idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        body = await _json_body(request, max_bytes=64 * 1024)
        source_id = body.get("source_id")
        if not source_id or not isinstance(source_id, str) or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the body must carry a source_id", 422)
        try:
            start, end = int(body["start"]), int(body["end"])
        except (KeyError, TypeError, ValueError):
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry integer start/end offsets "
                                "(decoded-text coordinates)", 422)
        argv = _capture_argv("create_bookmark", ctx, idempotency_key) + \
            ["--source-id", source_id, "--start", str(start), "--end", str(end)]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # GET /api/v1/bookmarks — 'list': the bounded page (tombstoned hidden)
    @router.get("/api/v1/bookmarks")
    async def list_bookmarks(ctx: dict = Depends(verified),
                             limit: str = "50", after: str = ""):
        return await _bounded_list(ctx, "list-bookmarks", limit, after)

    # GET /api/v1/bookmarks/{id} — 'read': the current location row
    @router.get("/api/v1/bookmarks/{bookmark_id}")
    async def get_bookmark(bookmark_id: str, ctx: dict = Depends(verified)):
        if not bookmark_id or len(bookmark_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the bookmark id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-bookmark", "--owner", ctx["owner_scope"],
                "--id", bookmark_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            raise KernelRefusal("ARV-QRY-404", "no such bookmark for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # GET /api/v1/bookmarks/{id}/history — 'history': every revision in order
    @router.get("/api/v1/bookmarks/{bookmark_id}/history")
    async def bookmark_history(bookmark_id: str, ctx: dict = Depends(verified)):
        if not bookmark_id or len(bookmark_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the bookmark id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-bookmark-history", "--owner", ctx["owner_scope"],
                "--id", bookmark_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows:
            raise KernelRefusal("ARV-QRY-404", "no such bookmark for this owner", 404)
        return JSONResponse(status_code=200, content=page)

    # PUT /api/v1/bookmarks/{id} — 'move': the serialized edit transition (a
    # NEW revision with a NEW anchor at the new offsets, identity-fixed to
    # the SAME Source version; tombstoned refuses — restore first)
    @router.put("/api/v1/bookmarks/{bookmark_id}")
    async def move_bookmark(bookmark_id: str, request: Request,
                            ctx: dict = Depends(verified),
                            idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not bookmark_id or len(bookmark_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the bookmark id is malformed", 422)
        start, end = await _offset_body(request)
        argv = _capture_argv("move_bookmark", ctx, idempotency_key) + \
            ["--id", bookmark_id, "--start", str(start), "--end", str(end)]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # DELETE /api/v1/bookmarks/{id} — 'tombstone'
    @router.delete("/api/v1/bookmarks/{bookmark_id}")
    async def tombstone_bookmark(bookmark_id: str, ctx: dict = Depends(verified),
                                 idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not bookmark_id or len(bookmark_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the bookmark id is malformed", 422)
        argv = _capture_argv("tombstone_bookmark", ctx, idempotency_key) + \
            ["--id", bookmark_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # POST /api/v1/bookmarks/{id}/restore — 'restore'
    @router.post("/api/v1/bookmarks/{bookmark_id}/restore")
    async def restore_bookmark(bookmark_id: str, ctx: dict = Depends(verified),
                               idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not bookmark_id or len(bookmark_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the bookmark id is malformed", 422)
        argv = _capture_argv("restore_bookmark", ctx, idempotency_key) + \
            ["--id", bookmark_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # ---- CLAIM-099: the §11.2 Notes + Journal + References families (the
    # directive's Workstream 4, families 4-6: the authored-content surfaces
    # over the kernel's note/journal machines — the content STAGED to a
    # bounded temp file and passed through the kernel's own --content-file/
    # --file channel (the import route's staging pattern; the long-form
    # authoring surface, never an argv-sized body), the reference set the
    # kernel's own KIND:ID[@REV] grammar; the typed stable-reference
    # resolution over the query kernel's six-state verdict) ----
    MAX_AUTHOR_BYTES = 4 * 1024 * 1024  # the authored-content body cap (F1)

    def _stage_author_body(body: dict):
        """Decode + stage the authored-content DTO: the content string (one
        channel, lossless) + the optional reference list (the kernel's own
        grammar, validated at the kernel). Returns (tmpdir, file, refs)."""
        content = body.get("content")
        if not isinstance(content, str) or not content:
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry a non-empty content string "
                                "(the authored body)", 422)
        refs = body.get("refs", [])
        if not isinstance(refs, list) or any(not isinstance(r, str) or not r or len(r) > 256
                                             for r in refs):
            raise KernelRefusal("ARV-QRY-004",
                                "refs must be a list of reference strings "
                                "(KIND:ID[@REV])", 422)
        tmpdir = tempfile.mkdtemp(prefix="arv_api_author_")
        tmp = pathlib.Path(tmpdir) / "content.txt"
        try:
            tmp.write_bytes(content.encode("utf-8"))
        except UnicodeEncodeError:
            # SEV9-171 (the SEV round's live finding): a lone surrogate is
            # valid JSON but unencodable as UTF-8 — the refusal lands INSIDE
            # the §11.4 envelope (a named 422), never a bare crash outside it
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise KernelRefusal("ARV-QRY-004",
                                "the content carries an unpaired surrogate — it "
                                "cannot be encoded as UTF-8 (the lossless authoring "
                                "surface refuses it, never a lossy interpretation)", 422)
        return tmpdir, tmp, refs

    # POST /api/v1/notes — 'create': the authored note + its version-aware
    # reference set (highlight/note/bookmark/journal_block refs pin the target
    # revision; work/source/anchor refs are bare — the kernel's own grammar)
    @router.post("/api/v1/notes")
    async def create_note(request: Request, ctx: dict = Depends(verified),
                          idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        body = await _json_body(request, max_bytes=MAX_AUTHOR_BYTES)
        tmpdir, tmp, refs = _stage_author_body(body)
        try:
            argv = _capture_argv("create_note", ctx, idempotency_key) + \
                ["--content-file", str(tmp)]
            for r in refs:
                argv += ["--ref", r]
            ack = _run_kernel(argv, db, timeout=120.0)
            return JSONResponse(status_code=200, content=ack)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # GET /api/v1/notes — 'list': the bounded page (tombstoned hidden)
    @router.get("/api/v1/notes")
    async def list_notes(ctx: dict = Depends(verified),
                         limit: str = "50", after: str = ""):
        return await _bounded_list(ctx, "list-notes", limit, after)

    # GET /api/v1/notes/{id} — 'read': the current revision + the reference
    # set; tombstoned is the hidden 404 (the governed history retains it)
    @router.get("/api/v1/notes/{note_id}")
    async def get_note(note_id: str, ctx: dict = Depends(verified)):
        if not note_id or len(note_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the note id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-note", "--owner", ctx["owner_scope"],
                "--id", note_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            raise KernelRefusal("ARV-QRY-404", "no such note for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # GET /api/v1/notes/{id}/history — 'history': the governed view
    @router.get("/api/v1/notes/{note_id}/history")
    async def note_history(note_id: str, ctx: dict = Depends(verified)):
        if not note_id or len(note_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the note id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-note-history", "--owner", ctx["owner_scope"],
                "--id", note_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows:
            raise KernelRefusal("ARV-QRY-404", "no such note for this owner", 404)
        return JSONResponse(status_code=200, content=page)

    # PUT /api/v1/notes/{id} — 'revise': the FULL replacement (the new
    # revision carries its OWN complete content AND reference set)
    @router.put("/api/v1/notes/{note_id}")
    async def revise_note(note_id: str, request: Request,
                          ctx: dict = Depends(verified),
                          idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not note_id or len(note_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the note id is malformed", 422)
        body = await _json_body(request, max_bytes=MAX_AUTHOR_BYTES)
        tmpdir, tmp, refs = _stage_author_body(body)
        try:
            argv = _capture_argv("revise_note", ctx, idempotency_key) + \
                ["--id", note_id, "--content-file", str(tmp)]
            for r in refs:
                argv += ["--ref", r]
            ack = _run_kernel(argv, db, timeout=120.0)
            return JSONResponse(status_code=200, content=ack)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # DELETE /api/v1/notes/{id} — 'tombstone': hidden from ordinary
    # retrieval; the governed history keeps every revision and event
    @router.delete("/api/v1/notes/{note_id}")
    async def tombstone_note(note_id: str, ctx: dict = Depends(verified),
                             idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not note_id or len(note_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the note id is malformed", 422)
        argv = _capture_argv("tombstone_note", ctx, idempotency_key) + \
            ["--id", note_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # POST /api/v1/notes/{id}/restore — 'restore'
    @router.post("/api/v1/notes/{note_id}/restore")
    async def restore_note(note_id: str, ctx: dict = Depends(verified),
                           idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not note_id or len(note_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the note id is malformed", 422)
        argv = _capture_argv("restore_note", ctx, idempotency_key) + \
            ["--id", note_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # POST /api/v1/journal — 'create': the writing lab's block (the closed
    # kind vocabulary raw|creative; the OPTIONAL source binding — a sourceless
    # block is a first-class journal row)
    @router.post("/api/v1/journal")
    async def create_journal_block(request: Request, ctx: dict = Depends(verified),
                                   idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        body = await _json_body(request, max_bytes=MAX_AUTHOR_BYTES)
        kind = body.get("kind")
        if kind not in ("raw", "creative"):
            raise KernelRefusal("ARV-JNL-002",
                                "the journal block kind must be one of the closed "
                                "vocabulary (raw | creative)", 422)
        content = body.get("content")
        if not isinstance(content, str) or not content:
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry a non-empty content string "
                                "(the journal body)", 422)
        source_id = body.get("source_id")
        if source_id is not None and (not isinstance(source_id, str) or len(source_id) > 128):
            raise KernelRefusal("ARV-QRY-004", "the source_id is malformed", 422)
        tmpdir = tempfile.mkdtemp(prefix="arv_api_jnl_")
        tmp = pathlib.Path(tmpdir) / "content.txt"
        tmp.write_bytes(content.encode("utf-8"))
        try:
            argv = _capture_argv("journal_block", ctx, idempotency_key) + \
                ["--kind", kind, "--file", str(tmp)]
            if source_id is not None:
                argv += ["--source-id", source_id]
            ack = _run_kernel(argv, db, timeout=120.0)
            return JSONResponse(status_code=200, content=ack)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # GET /api/v1/journal — 'list': the owner's blocks (bounded page)
    @router.get("/api/v1/journal")
    async def list_journal(ctx: dict = Depends(verified),
                           limit: str = "50", after: str = ""):
        return await _bounded_list(ctx, "list-journal", limit, after)

    # GET /api/v1/journal/{id} — 'read': the current revision, the content
    # WHOLE (the long raw thinking, never truncated)
    @router.get("/api/v1/journal/{journal_id}")
    async def get_journal_block(journal_id: str, ctx: dict = Depends(verified)):
        if not journal_id or len(journal_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the journal id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-journal", "--owner", ctx["owner_scope"],
                "--id", journal_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            raise KernelRefusal("ARV-QRY-404", "no such journal block for this owner", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # GET /api/v1/journal/{id}/history — 'full history': every revision in order
    @router.get("/api/v1/journal/{journal_id}/history")
    async def journal_history(journal_id: str, ctx: dict = Depends(verified)):
        if not journal_id or len(journal_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the journal id is malformed", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-journal-history", "--owner", ctx["owner_scope"],
                "--id", journal_id]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows:
            raise KernelRefusal("ARV-QRY-404", "no such journal block for this owner", 404)
        return JSONResponse(status_code=200, content=page)

    # PUT /api/v1/journal/{id} — 'revise': the writing lab's edit transition
    @router.put("/api/v1/journal/{journal_id}")
    async def revise_journal_block(journal_id: str, request: Request,
                                   ctx: dict = Depends(verified),
                                   idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not journal_id or len(journal_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the journal id is malformed", 422)
        body = await _json_body(request, max_bytes=MAX_AUTHOR_BYTES)
        if "kind" in body:
            # SEV9-123k (the SEV round's live finding): the kind is the
            # block's immutable identity — the kernel's own revise carries
            # the prior revision's kind. A kind in the revise DTO would be a
            # SILENT drop (the F5b class) — refused HERE, named, instead
            raise KernelRefusal("ARV-QRY-004",
                                "the journal block's kind is immutable identity "
                                "(the kernel's revise carries the prior revision's "
                                "kind); the revise body carries the content only", 422)
        content = body.get("content")
        if not isinstance(content, str) or not content:
            raise KernelRefusal("ARV-QRY-004",
                                "the body must carry a non-empty content string "
                                "(the journal body)", 422)
        tmpdir = tempfile.mkdtemp(prefix="arv_api_jnl_")
        tmp = pathlib.Path(tmpdir) / "content.txt"
        try:
            tmp.write_bytes(content.encode("utf-8"))
        except UnicodeEncodeError:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise KernelRefusal("ARV-QRY-004",
                                "the content carries an unpaired surrogate — it "
                                "cannot be encoded as UTF-8 (the lossless surface "
                                "refuses it, never a lossy interpretation)", 422)
        try:
            argv = _capture_argv("revise_journal_block", ctx, idempotency_key) + \
                ["--id", journal_id, "--file", str(tmp)]
            ack = _run_kernel(argv, db, timeout=120.0)
            return JSONResponse(status_code=200, content=ack)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # GET /api/v1/references?ref=KIND:ID[@REV] — the typed stable-reference
    # resolution (the six-state verdict; the kernel's OWN canonical grammar —
    # the query parameter carries it verbatim, never a re-invented path form)
    @router.get("/api/v1/references")
    async def resolve_reference(ctx: dict = Depends(verified), ref: str = ""):
        if not ref or len(ref) > 256:
            raise KernelRefusal("ARV-QRY-004",
                                "the ref query parameter is required "
                                "(KIND:ID[@REV])", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "resolve-reference", "--owner", ctx["owner_scope"],
                "--ref", ref]
        page = _query_kernel(argv, db)
        rows = page.get("rows") or []
        if not rows or not isinstance(rows[0], dict):
            raise KernelRefusal("ARV-QRY-404", "the reference did not resolve", 404)
        return JSONResponse(status_code=200, content={"row": rows[0],
                                                      "api_version": page.get("api_version", 1)})

    # ---- CLAIM-100: the §11.2 Reading lists family (the directive's
    # Workstream 4, family 7 — the last row: create/list/member add/remove/
    # current membership over the kernel's own event machine; the identity
    # is the uuid, NEVER the name — two lists may share one; the current
    # membership is DERIVED from the append-only event rows) ----

    # POST /api/v1/reading-lists — 'create': the owner's own label
    @router.post("/api/v1/reading-lists")
    async def create_reading_list(request: Request, ctx: dict = Depends(verified),
                                  idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        body = await _json_body(request, max_bytes=64 * 1024)
        name = body.get("name")
        if not isinstance(name, str):
            raise KernelRefusal("ARV-QRY-004", "the body must carry a name string", 422)
        argv = _capture_argv("create_reading_list", ctx, idempotency_key) +             ["--name", name]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # GET /api/v1/reading-lists — 'list': the owner's lists with the DERIVED
    # member count (bounded page; NO name uniqueness implied — the identity
    # is the uuid)
    @router.get("/api/v1/reading-lists")
    async def list_reading_lists(ctx: dict = Depends(verified),
                                 limit: str = "50", after: str = ""):
        return await _bounded_list(ctx, "list-lists", limit, after)

    # GET /api/v1/reading-lists/{id} — 'current membership': the derived view
    # over the membership event rows (the last op per pair wins)
    @router.get("/api/v1/reading-lists/{list_id}")
    async def get_reading_list(list_id: str, ctx: dict = Depends(verified),
                               limit: str = "50", after: str = ""):
        if not list_id or len(list_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the list id is malformed", 422)
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "get-list", "--owner", ctx["owner_scope"],
                "--id", list_id, "--limit", str(limit_i)]
        if after:
            argv += ["--after", after]
        # an EMPTY membership is a legitimate 200 answer (the kernel's exit-0
        # header + more=false page); the ABSENT list is the kernel's own
        # exit-1 ARV-QRY-001 refusal — _query_kernel raises it before here,
        # mapped to the no-leak 404 by the §11.4 family. The two shapes never
        # conflated: empty rows serve the empty page.
        page = _query_kernel(argv, db)
        return JSONResponse(status_code=200, content=page)

    # POST /api/v1/reading-lists/{id}/members — 'member add': ONE append-only
    # event; the alternation law lives at the substrate (the honest unknown
    # through §11.4 when it fires)
    @router.post("/api/v1/reading-lists/{list_id}/members")
    async def add_list_member(list_id: str, request: Request,
                              ctx: dict = Depends(verified),
                              idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not list_id or len(list_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the list id is malformed", 422)
        body = await _json_body(request, max_bytes=64 * 1024)
        source_id = body.get("source_id")
        if not source_id or not isinstance(source_id, str) or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the body must carry a source_id", 422)
        argv = _capture_argv("add_to_list", ctx, idempotency_key) +             ["--list", list_id, "--source", source_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # DELETE /api/v1/reading-lists/{id}/members/{source_id} — 'member remove'
    @router.delete("/api/v1/reading-lists/{list_id}/members/{source_id}")
    async def remove_list_member(list_id: str, source_id: str,
                                 ctx: dict = Depends(verified),
                                 idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        if not list_id or len(list_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the list id is malformed", 422)
        if not source_id or len(source_id) > 128:
            raise KernelRefusal("ARV-QRY-004", "the source id is malformed", 422)
        argv = _capture_argv("remove_from_list", ctx, idempotency_key) + \
            ["--list", list_id, "--source", source_id]
        ack = _run_kernel(argv, db, timeout=120.0)
        return JSONResponse(status_code=200, content=ack)

    # ---- CLAIM-101: the §11.2 Retrieval API (the directive's Workstream 5:
    # the keyword search + the bounded context packs over the query kernel's
    # OWN search/pack arms — deterministic, no semantic/model work per Q7;
    # the pipe-framed page contract parsed at ONE place) ----

    def _pipe_page(argv: list) -> dict:
        """Run a query arm whose page contract is the PIPE-framed form (the
        '# api_version=1 col|col|...' header, the pipe rows, the '# more='
        trailer) and return the structured page: rows as dicts over the
        header's own columns + the page metadata. ONE parser, never a second
        framing law."""
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=60.0,
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
        rows, cols, meta, api_version, more = [], [], {}, 1, False
        for ln in out.splitlines():
            ln = ln.strip()
            if ln.startswith("# api_version="):
                # the header line carries BOTH the version and the column
                # names: '# api_version=1 kind|entity_id|...'
                rest = ln.lstrip("# ")
                head, _, cols_str = rest.partition(" ")
                try:
                    api_version = int(head.split("=", 1)[1])
                except Exception:
                    pass
                if cols_str:
                    cols = [c for c in cols_str.split("|")]
            elif ln.startswith("# more="):
                more = ln.split("=", 1)[1].strip().lower() == "true"
                for tok in ln[2:].split():
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        if k != "more":
                            meta[k] = v
                meta["more"] = more
            elif ln.startswith("#"):
                continue
            elif ln:
                if not cols:
                    cols = [c for c in ln.split("|")]
                else:
                    vals = ln.split("|")
                    rows.append(dict(zip(cols, vals)))
        return {"rows": rows, "page_meta": meta, "api_version": api_version}

    async def _terms_query(request: Request) -> list:
        """The retrieval DTO: one or more terms (the AND semantics) — the
        repeated query parameter carries them verbatim to the kernel's own
        positional terms."""
        terms = request.query_params.getlist("terms")
        terms = [t for t in terms if t]
        if not terms:
            raise KernelRefusal("ARV-QRY-004",
                                "at least one terms query parameter is required "
                                "(AND semantics — every term must hit)", 422)
        return terms

    # GET /api/v1/search?terms=a&terms=b — 'keyword search': the deterministic
    # AND-semantics admission over the caller's own corpus (the kernel arm's
    # own contract: the full admission list, no paging parameters of its own —
    # the pack arm carries the bounded-paging surface)
    @router.get("/api/v1/search")
    async def keyword_search(request: Request, ctx: dict = Depends(verified)):
        terms = await _terms_query(request)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "search", "--owner", ctx["owner_scope"]] + terms
        page = _pipe_page(argv)
        return JSONResponse(status_code=200, content=page)

    # GET /api/v1/context-packs?terms=a&budget-bytes=N — 'bounded context
    # packs': the provenance-carrying assembly (trust labels, matched terms,
    # the why; the explicit item-boundary truncation + the trailer metadata)
    @router.get("/api/v1/context-packs")
    async def context_pack(request: Request, ctx: dict = Depends(verified),
                           limit: str = "50", after: str = ""):
        terms = await _terms_query(request)
        budget = request.query_params.get("budget-bytes", "65536")
        try:
            budget_i = int(budget)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "budget-bytes must be an integer", 422)
        if not (1 <= budget_i <= 1048576):
            raise KernelRefusal("ARV-QRY-004",
                                f"budget-bytes {budget} outside [1, 1048576]", 422)
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        argv = [sys.executable, str(REPO / "harness" / "query.py"),
                "pack", "--owner", ctx["owner_scope"]] + terms +             ["--budget-bytes", str(budget_i), "--limit", str(limit_i)]
        if after:
            argv += ["--after", after]
        page = _pipe_page(argv)
        # the trailer's numeric/boolean fields typed at the boundary (never
        # strings the client must re-parse)
        meta = page.get("page_meta", {})
        for k in ("kept", "total", "budget_bytes", "used_bytes"):
            if k in meta:
                try:
                    meta[k] = int(meta[k])
                except (TypeError, ValueError):
                    pass
        if "truncated" in meta:
            meta["truncated"] = str(meta.get("truncated")).lower() == "true"
        return JSONResponse(status_code=200, content=page)

    # ---- CLAIM-102: the §11.2 'Sync' + 'Export/restore' rows + the
    # governed-purge surface (the directive's Workstream 6) — the routes
    # call the kernel's OWN machines: harness/sync.py's two-database outbox
    # delivery (one pass, the typed per-row states), harness/export.py's
    # export/restore (the versioned manifest + the purge-ledger
    # reconciliation), and the substrate's purge ledger (the owner-scoped
    # append-only erasure record, RTM §3.3/SYS-10/D-011/D-029) ----

    def _ws6_kernel(module: str, argv: list, timeout: float = 300.0) -> "tuple[int, str]":
        """Run one Workstream-6 kernel module (sync.py/export.py) as a
        bounded subprocess on the SERVICE's db. Returns (rc, output); never
        raises — the exit code is the machine's own answer, the classification
        happens at the caller."""
        env = dict(os.environ)
        env["PGDATABASE"] = db
        try:
            r = subprocess.run([sys.executable, str(REPO / "harness" / module)] + argv,
                               capture_output=True, text=True, timeout=timeout,
                               cwd=str(REPO), env=env)
        except subprocess.TimeoutExpired:
            raise KernelRefusal("ARV-API-504",
                                "the command exceeded its time bound", 504)
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    def _fail_of(out: str) -> str:
        """The kernel's first named FAIL line (the §11.4 envelope's input)."""
        return next((ln for ln in out.splitlines() if ln.startswith("FAIL ")), "")

    def _map_ws6_failure(out: str, fallback_code: str, fallback_msg: str,
                         fallback_status: int = 500) -> KernelRefusal:
        """One WS6 kernel failure output -> the §11.4 envelope (the SAME
        centralized map; the named code preserved, the raw cause never
        echoed)."""
        line = _fail_of(out)
        if line:
            return _map_kernel_refusal(line)
        return KernelRefusal(fallback_code, fallback_msg, fallback_status)

    # GET /api/v1/sync/outbox — 'the delivery state': the owner's outbox
    # counts by state + the non-terminal rows (the kernel's own status arm;
    # queued rows carry key/state/attempts only — never the payload)
    @router.get("/api/v1/sync/outbox")
    async def sync_outbox_status(ctx: dict = Depends(verified)):
        rc, out = _ws6_kernel("sync.py", ["status", "--owner", ctx["owner_scope"]])
        if rc != 0:
            raise _map_ws6_failure(out, "ARV-API-500",
                                   "the sync status refused without a named code")
        counts, queued = {}, []
        for ln in out.splitlines():
            if ln.startswith("SYNC-STATUS "):
                for tok in ln.split()[2:]:
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        try:
                            counts[k] = int(v)
                        except ValueError:
                            counts[k] = v
            elif ln.startswith("SYNC-QUEUED "):
                # 'key state=pending attempts=0' — the queued row's OWN shape
                q = ln[len("SYNC-QUEUED "):]
                key, rest = (q.split(" ", 1) + [""])[:2]
                row = {"idempotency_key": key}
                for tok in rest.split():
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        try:
                            row[k] = int(v)
                        except ValueError:
                            row[k] = v
                queued.append(row)
        return JSONResponse(status_code=200, content={"counts": counts,
                                                      "queued": queued,
                                                      "api_version": 1})

    # POST /api/v1/sync/deliver — 'the delivery pass': ONE walk over the
    # owner's non-terminal outbox rows (mark-delivered → apply on the target
    # → classify; the typed per-row outcome). The TARGET database is a
    # service-configured value (the deployment's own parameter — the
    # desktop-over-HTTP transport's server side; the kernel's own
    # --server-db contract), NEVER a client value; a service without a
    # configured target refuses named (503) — never a guess.
    @router.post("/api/v1/sync/deliver")
    async def sync_deliver(ctx: dict = Depends(verified)):
        target_db = os.environ.get("ARIVO_SYNC_TARGET_DB", "")
        if not target_db:
            raise KernelRefusal("ARV-SYN-014",
                                "the sync target database is not configured on "
                                "this service (the delivery pass needs the "
                                "deployment's own target parameter)", 503)
        rc, out = _ws6_kernel("sync.py",
                              ["sync", "--owner", ctx["owner_scope"],
                               "--server-db", target_db], timeout=600.0)
        if rc != 0:
            raise _map_ws6_failure(out, "ARV-API-500",
                                   "the delivery pass refused without a named code")
        states, done = {}, 0
        for ln in out.splitlines():
            if ln.startswith("SYNC key="):
                key = ln.split("key=", 1)[1].split()[0]
                state = ln.split(" state=", 1)[1].split()[0] if " state=" in ln else ""
                states[key] = state
            elif ln.startswith("SYNC-DONE "):
                try:
                    done = int(ln.rsplit("rows=", 1)[1])
                except (IndexError, ValueError):
                    done = 0
        return JSONResponse(status_code=200, content={"walked": done,
                                                      "states": states,
                                                      "api_version": 1})

    # GET /api/v1/export — 'the owner-authorized export': the authoritative
    # set + the blob references under the versioned manifest, staged in the
    # service's own export root. The route RETURNS the manifest (the
    # archive's own truth — the client reads it; the blobs stay staged
    # server-side under their digests, fetched by the reference).
    @router.get("/api/v1/export")
    async def export_library(ctx: dict = Depends(verified)):
        export_root = os.environ.get("ARIVO_EXPORT_ROOT", "")
        if not export_root:
            raise KernelRefusal("ARV-EXP-008",
                                "the export root is not configured on this "
                                "service (the archive staging needs the "
                                "deployment's own root parameter)", 503)
        out_dir = os.path.join(export_root, ctx["owner_scope"].replace("/", "_"))
        rc, out = _ws6_kernel("export.py",
                              ["export", "--owner", ctx["owner_scope"],
                               "--out", out_dir], timeout=600.0)
        if rc != 0:
            raise _map_ws6_failure(out, "ARV-API-500",
                                   "the export refused without a named code")
        ack = {}
        for ln in out.splitlines():
            if ln.startswith("EXPORTED "):
                for tok in ln.split():
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        ack[k] = v
        manifest_path = pathlib.Path(out_dir) / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise KernelRefusal("ARV-EXP-003",
                                "the staged manifest is unreadable — the export "
                                "refuses to serve an unverified archive", 500)
        return JSONResponse(status_code=200, content={
            "state": "manifest_complete",
            "manifest": manifest,
            "api_version": 1})

    # POST /api/v1/restore — 'the recovery path': restore a staged archive
    # into THIS service's database (the owner's own recovery surface; the
    # destination's purge ledger wins over older archive content — SYS-10;
    # the once-per-clean-destination law; the typed completion names the
    # adopted ledger's as-of time). The manifest_name addresses an archive
    # ALREADY staged under the service's export root (the export route's own
    # staging): a client never uploads an archive body — the recovery path
    # is server-staged, never an unvalidated client file.
    @router.post("/api/v1/restore")
    async def restore_library(request: Request, ctx: dict = Depends(verified),
                              idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        export_root = os.environ.get("ARIVO_EXPORT_ROOT", "")
        if not export_root:
            raise KernelRefusal("ARV-EXP-008",
                                "the export root is not configured on this "
                                "service (the recovery path needs the "
                                "deployment's own root parameter)", 503)
        body = await _json_body(request, max_bytes=16 * 1024)
        name = body.get("manifest_name")
        if not isinstance(name, str) or not name or len(name) > 128 \
                or "/" in name or "\\" in name or ".." in name:
            raise KernelRefusal("ARV-PRG-002",
                                "the body must carry a manifest_name (a staged "
                                "archive's name under the service's export "
                                "root — no paths, no traversal)", 422)
        arch = pathlib.Path(export_root) / name
        if not (arch / "manifest.json").is_file():
            raise KernelRefusal("ARV-EXP-004",
                                "no staged archive carries that manifest name "
                                "(the recovery path serves the service's own "
                                "staged archives only)", 404)
        # the archive's owner must MATCH the verified caller (the recovery
        # path is the owner's own surface; a cross-owner archive is the
        # same 404 as an absent one — never an existence oracle)
        try:
            staged_owner = json.loads(
                (arch / "manifest.json").read_text(encoding="utf-8")).get("owner")
        except (OSError, json.JSONDecodeError):
            staged_owner = None
        if staged_owner != ctx["owner_scope"]:
            raise KernelRefusal("ARV-EXP-004",
                                "no staged archive carries that manifest name "
                                "for this owner", 404)
        rc, out = _ws6_kernel("export.py",
                              ["restore", "--archive", str(arch)], timeout=600.0)
        if rc != 0:
            raise _map_ws6_failure(out, "ARV-API-500",
                                   "the restore refused without a named code")
        ack = {}
        for ln in out.splitlines():
            if ln.startswith("RESTORED "):
                for tok in ln.split():
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        ack[k] = v
        return JSONResponse(status_code=200, content=ack)

    # GET /api/v1/purge-ledger — 'the erasure record': the owner's own
    # purge ledger rows (the minimal audit surface D-011 leaves; bounded +
    # paginated like every list — the ledger is owner-scoped authoritative
    # state, readable by its owner)
    @router.get("/api/v1/purge-ledger")
    async def list_purge_ledger(ctx: dict = Depends(verified),
                                limit: str = "50", after: str = ""):
        try:
            limit_i = int(limit)
        except ValueError:
            raise KernelRefusal("ARV-QRY-004", "limit must be an integer", 422)
        if not (LIST_LIMIT_BOUNDS[0] <= limit_i <= LIST_LIMIT_BOUNDS[1]):
            raise KernelRefusal("ARV-QRY-004",
                                f"limit {limit} outside [{LIST_LIMIT_BOUNDS[0]}, "
                                f"{LIST_LIMIT_BOUNDS[1]}]", 422)
        after_clause = ""
        if after:
            # the keyset cursor: (kind, entity_id) — strictly after the named
            # pair; a malformed cursor is the same 422 class as the bounds
            parts = after.split("|", 1)
            if len(parts) != 2 or not all(parts):
                raise KernelRefusal("ARV-QRY-004",
                                    "the after cursor must be KIND|ENTITY_ID", 422)
            after_clause = f" AND (kind, entity_id) > ({parts[0]!r}, {parts[1]!r})"
        sql = ("SELECT kind || '|' || entity_id || '|' || "
               "to_char(created_at, 'YYYY-MM-DD\"T\"HH24:MI:SS') "
               "FROM arv.purge_ledger WHERE owner_scope = "
               f"{ctx['owner_scope']!r}{after_clause} "
               "ORDER BY kind, entity_id LIMIT " + str(limit_i + 1) + ";")
        from harness.adapters import pg as _pg
        r = _pg.psql("SET app.current_owner=" +
                     _q(ctx["owner_scope"]) + "; " + sql, db=db, user="arv_app")
        if r.returncode != 0:
            raise KernelRefusal("ARV-API-500",
                                "the purge ledger read refused at the boundary", 500)
        lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        more = len(lines) > limit_i
        rows = []
        for ln in lines[:limit_i]:
            kind, entity_id, created_at = (ln.split("|", 2) + ["", "", ""])[:3]
            rows.append({"kind": kind, "entity_id": entity_id,
                         "created_at": created_at})
        return JSONResponse(status_code=200, content={
            "rows": rows, "more": more,
            "after": f"{rows[-1]['kind']}|{rows[-1]['entity_id']}" if rows else "",
            "api_version": 1})

    # POST /api/v1/purge — 'the governed purge' (D-011: deliberate,
    # owner-only; ordinary delete stays the tombstone). The erasure itself
    # rides the SUBSTRATE's own machine — migration 0021's
    # arv.governed_purge: ONE SECURITY DEFINER procedure that owns the only
    # authorized content-DELETE path (the ledger write + the content drop +
    # the derived-index drop in ONE transaction — all-or-nothing; the
    # append-only triggers stay armed everywhere else). The route's argv is
    # the verified owner (never a client value); the named refusals surface
    # through the §11.4 map.
    @router.post("/api/v1/purge")
    async def governed_purge(request: Request, ctx: dict = Depends(verified),
                             idempotency_key: str = Header(default="")):
        if not idempotency_key or len(idempotency_key) > 200:
            raise KernelRefusal("ARV-API-400",
                                "the Idempotency-Key header is required (the "
                                "§11.3 write law: every write carries one)", 400)
        body = await _json_body(request, max_bytes=16 * 1024)
        kind = body.get("kind")
        entity_id = body.get("entity_id")
        reason = body.get("reason")
        if kind not in ("work", "source", "anchor", "highlight", "bookmark",
                        "note", "journal_block", "reading_list"):
            raise KernelRefusal("ARV-PRG-002",
                                "the kind must be one of the governed-purge "
                                "vocabulary (work|source|anchor|highlight|"
                                "bookmark|note|journal_block|reading_list)", 422)
        if not isinstance(entity_id, str) or len(entity_id) != 36 \
                or entity_id.count("-") != 4:
            raise KernelRefusal("ARV-PRG-002",
                                "the entity_id must be a uuid", 422)
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 512:
            raise KernelRefusal("ARV-PRG-002",
                                "the reason is required (1..512 chars — the "
                                "owner's own erasure record)", 422)
        owner = ctx["owner_scope"]
        from harness.adapters import pg as _pg
        r = _pg.psql("SET app.current_owner=" + _q(owner) + "; "
                     "CALL arv.governed_purge(" + _q(owner) + ", " + _q(kind)
                     + ", " + _q(entity_id) + "::uuid, " + _q(reason) + ");",
                     db=db, user="arv_app")
        if r.returncode != 0:
            err = (r.stderr or "")
            for code, status in (("ARV-PRG-003", 404), ("ARV-PRG-004", 409),
                                 ("ARV-PRG-005", 409), ("ARV-PRG-001", 409)):
                if code in err:
                    msg = err.split(":", 1)[1].strip()[:200] if ":" in err else code
                    # the no-oracle class: absent and another owner's are the
                    # SAME 404; the message carries no other-owner signal
                    if code == "ARV-PRG-003":
                        msg = "no such object for this owner (the purge is " \
                              "the owner's own erasure surface)"
                    raise KernelRefusal(code, msg, status)
            raise KernelRefusal("ARV-API-500",
                                "the governed purge refused without a named "
                                "code", 500)
        return JSONResponse(status_code=200, content={
            "state": "purged",
            "kind": kind,
            "entity_id": entity_id,
            "ledger_recorded": True,
            "content_dropped": True,
            "durability_rung": "local_durable",
            "api_version": 1})

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
