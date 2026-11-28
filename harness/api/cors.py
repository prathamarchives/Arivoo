#!/usr/bin/env python3
"""harness/api/cors.py — Workstream 2: the strict CORS origin matrix.

stdlib only (LAW-08: no third-party import outside the approved boundary —
this module is deliberately importable on the trusted, venv-less runner).
The API composes starlette's CORSMiddleware from parse_allowed_origins();
there is NO wildcard, NO origin reflection, NO credentials, and NO path,
userinfo, query or fragment in an accepted origin. An unset matrix means
CORS is OFF — a browser origin gets no CORS headers at all, never a `*`.

Named refusal:
  ARV-CORS-001  a configured origin is malformed (wildcard, path, userinfo,
                empty entry, duplicate, or over the count bound) — the
                service refuses to start rather than serve a permissive
                policy it cannot explain.
"""
import re

ENV_NAME = "ARIVO_ALLOWED_ORIGINS"
MAX_ORIGINS = 16
# scheme://host[:port] — an ORIGIN, never a URL with path/query/fragment and
# never userinfo. Host labels are DNS-safe; localhost is included by the same
# expression. The port is checked numerically below (1..65535).
_ORIGIN_RE = re.compile(
    r"^(?P<scheme>https?)://(?P<host>[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?)"
    r"(?::(?P<port>[0-9]{1,5}))?$")


class OriginsRefusal(Exception):
    """A named refusal of a malformed origin matrix (diagnostics contract)."""

    def __init__(self, what: str):
        super().__init__("ARV-CORS-001: " + what)
        self.code = "ARV-CORS-001"


def parse_allowed_origins(raw: str | None) -> tuple[str, ...]:
    """Parse the service's ARIVO_ALLOWED_ORIGINS into an EXACT tuple.

    Empty/unset -> empty tuple (CORS off, no wildcard). Every configured
    entry must be a full origin; anything else refuses with ARV-CORS-001.
    The result is passed verbatim to CORSMiddleware's allow_origins — no
    normalization, no suffix matching, no reflection of the request origin.
    """
    if raw is None:
        return ()
    if not isinstance(raw, str):
        raise OriginsRefusal("the origin matrix must be a string")
    if not raw.strip():
        return ()
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) > MAX_ORIGINS:
        raise OriginsRefusal(f"at most {MAX_ORIGINS} origins may be configured")
    out: list[str] = []
    for part in parts:
        if not part:
            raise OriginsRefusal("an empty origin entry is not allowed")
        if "*" in part:
            raise OriginsRefusal("wildcard origins are never allowed")
        m = _ORIGIN_RE.match(part)
        if not m:
            raise OriginsRefusal("each entry must be scheme://host[:port] — "
                                 "no path, userinfo, query or fragment")
        port = m.group("port")
        if port is not None and not (1 <= int(port) <= 65535):
            raise OriginsRefusal("the origin port must be in 1..65535")
        if part in out:
            raise OriginsRefusal("duplicate origins are not allowed")
        out.append(part)
    return tuple(out)


def is_allowed(origin: str, allowed: tuple[str, ...] | list[str]) -> bool:
    """Exact whole-string membership — the request's Origin header is never
    used to build the allow list (no reflection class)."""
    return isinstance(origin, str) and origin in allowed
