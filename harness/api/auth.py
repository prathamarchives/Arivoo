#!/usr/bin/env python3
"""harness/api/auth.py — the auth boundary (runbook §8.3/§8.4; CLAIM-092; INT-156/D-050).

EVERY product route requires a valid Bearer access token. This module is the
single verification surface:
  * signature: ES256 only, verified against the project's PUBLIC JWKS (the
    in-use signing key is asymmetric — kid 55dac17b-cd6c-475d-b599-2588575f15ef;
    the retired HS256 key is never accepted: PyJWT's algorithms pin accepts
    exactly what we allow, so alg-confusion tokens refuse by construction)
  * issuer: exact-match https://wcuuakhdmsmmxagvbdmg.supabase.co/auth/v1
  * audience: the pinned project ref
  * expiry: verified (leeway 0 — a stale token refuses; no slack)
  * owner derivation: the VERIFIED sub becomes owner_scope. The module takes
    no owner argument anywhere — a client-supplied owner/actor value has no
  * user_metadata is NEVER read (§8.3: the user-editable surface is not an
    authorization input; this file contains no reference to it)

The JWKS is fetched from the pinned URL (https-only, bounded: 10s timeout,
64 KiB cap). A failed fetch refuses; a stale cache entry may serve ONLY
within its TTL, and an unknown kid triggers one bounded refresh then refuses.

Failure contract (named codes):
  ARV-AUTH-001  no/invalid Bearer header shape (401)
  ARV-AUTH-002  the JWKS fetch failed (fail-closed; 503 — never a fallback to accept)
  ARV-AUTH-003  signature/algorithm/issuer/audience/expiry verification failed (401)
  ARV-AUTH-004  the verified token carries no sub (401 — not a user, not an owner)

Config (explicit, like ProdConfig — no environment fallback): issuer, audience,
jwks_url, expected_kid. The service supplies them at startup.
"""
import json
import time
import urllib.request

import jwt  # pyjwt 2.15.1 — the approved pin (D-048's boundary: harness/api/)

ALLOWED_ALGS = ("ES256",)  # the project's in-use key; HS256 is retired and refused
JWKS_TTL_S = 3600.0
JWKS_MAX_BYTES = 65536
JWKS_TIMEOUT_S = 10.0


class AuthRefusal(Exception):
    """A named auth-boundary refusal (the diagnostics contract)."""

    def __init__(self, code: str, what: str, status: int):
        super().__init__(f"{code}: {what}")
        self.code = code
        self.status = status


class AuthConfig:
    """The explicit auth-boundary shape (no env reading, no defaults)."""

    __slots__ = ("issuer", "audience", "jwks_url", "expected_kid")

    def __init__(self, *, issuer, audience, jwks_url, expected_kid):
        if not (issuer.startswith("https://") and jwks_url.startswith("https://")):
            raise AuthRefusal("ARV-AUTH-002",
                              "the issuer and the JWKS URL must be https (a plaintext "
                              "auth path is refused by construction)", 503)
        self.issuer = str(issuer)
        self.audience = str(audience)
        self.jwks_url = str(jwks_url)
        self.expected_kid = str(expected_kid)

    def __repr__(self):
        return ("AuthConfig(issuer=%r, audience=%r, jwks_url=%r, "
                "expected_kid=%r)" % (self.issuer, self.audience,
                                      self.jwks_url, self.expected_kid))


class _JwksCache:
    """The bounded, fail-closed JWKS cache: TTL + size + timeout caps; an
    unknown kid triggers exactly ONE refresh, then refuses."""

    def __init__(self, cfg: AuthConfig):
        self._cfg = cfg
        self._jwk = None
        self._fetched_at = 0.0

    def jwk_for(self, kid: str):
        now = time.monotonic()
        fresh = self._jwk is not None and (now - self._fetched_at) < JWKS_TTL_S
        if fresh and kid == self._cfg.expected_kid:
            return self._jwk
        if fresh and kid != self._cfg.expected_kid:
            # an unknown kid: one bounded refresh (a rotation may have JUST
            # happened), then refuse — never accept an unpinned key
            self._refresh()
            if self._jwk is not None and kid == self._jwk.get("kid"):
                return self._jwk
            raise AuthRefusal("ARV-AUTH-003",
                              f"the token's kid {kid[:12]!r} is not the pinned "
                              f"signing key (the JWKS refresh did not carry it)",
                              401)
        self._refresh()
        if self._jwk is None:
            raise AuthRefusal("ARV-AUTH-002",
                              "the JWKS is unavailable (fail-closed: verification "
                              "refuses rather than degrade)", 503)
        if kid != self._jwk.get("kid"):
            raise AuthRefusal("ARV-AUTH-003",
                              f"the token's kid {kid[:12]!r} does not match the "
                              "served key", 401)
        return self._jwk

    def _refresh(self):
        try:
            req = urllib.request.Request(
                self._cfg.jwks_url,
                headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=JWKS_TIMEOUT_S) as r:
                raw = r.read(JWKS_MAX_BYTES + 1)
            if len(raw) > JWKS_MAX_BYTES:
                raise ValueError("the JWKS exceeds its size cap")
            doc = json.loads(raw)
            keys = doc.get("keys") if isinstance(doc, dict) else None
            if not keys:
                raise ValueError("the JWKS carries no keys")
        except Exception as e:
            # the previous entry may stay within TTL; a FAILED refresh never
            # extends trust: if we had nothing, we refuse now
            if self._jwk is None:
                raise AuthRefusal("ARV-AUTH-002",
                                  "the JWKS fetch failed (bounded; fail-closed) — "
                                  + str(e)[:120], 503) from None
            return
        jwk = None
        for k in keys:
            if k.get("kid") == self._cfg.expected_kid:
                jwk = k
                break
        if jwk is None:
            jwk = keys[0] if len(keys) == 1 else None
        self._jwk = jwk
        self._fetched_at = time.monotonic()

    def prime(self, jwk: dict):
        """Seed the cache with an already-verified JWK (startup pinning)."""
        self._jwk = jwk
        self._fetched_at = time.monotonic()


class Verifier:
    """The token verification + owner derivation surface (§8.3/§8.4)."""

    def __init__(self, cfg: AuthConfig):
        if not isinstance(cfg, AuthConfig):
            raise AuthRefusal("ARV-AUTH-002",
                              "the auth boundary requires an explicit AuthConfig "
                              "(no environment fallback)", 503)
        self._cfg = cfg
        self._jwks = _JwksCache(cfg)

    def verify_bearer(self, header: str) -> dict:
        """The Bearer-header entry point (ARV-AUTH-001 on shape, ARV-AUTH-003 on
        verification). Returns the VERIFIED claims; the caller derives the owner
        via derive_owner (never from any client-supplied field)."""
        if not header or not header.startswith("Bearer "):
            raise AuthRefusal("ARV-AUTH-001",
                              "the Authorization header must be a Bearer token", 401)
        token = header[len("Bearer "):].strip()
        if not token or len(token) > 8192:
            raise AuthRefusal("ARV-AUTH-001",
                              "the token is empty or oversized", 401)
        return self.verify(token)

    def verify(self, token: str) -> dict:
        try:
            header = jwt.get_unverified_header(token)
        except Exception:
            raise AuthRefusal("ARV-AUTH-003",
                              "the token header does not parse", 401) from None
        alg = header.get("alg")
        if alg not in ALLOWED_ALGS:
            raise AuthRefusal("ARV-AUTH-003",
                              f"the token's algorithm {alg!r} is not the pinned "
                              f"{ALLOWED_ALGS} (alg confusion refused)", 401)
        kid = header.get("kid") or ""
        jwk = self._jwks.jwk_for(kid)
        try:
            key = jwt.PyJWK.from_dict(jwk).key
        except Exception:
            raise AuthRefusal("ARV-AUTH-002",
                              "the served JWK does not build a verification key",
                              503) from None
        try:
            claims = jwt.decode(
                token, key,
                algorithms=list(ALLOWED_ALGS),
                audience=self._cfg.audience,
                issuer=self._cfg.issuer,
                options={"require": ["exp", "sub", "iss", "aud", "iat"]},
            )
        except Exception as e:
            raise AuthRefusal("ARV-AUTH-003",
                              "verification failed (signature/issuer/audience/"
                              "expiry): " + str(e)[:120], 401) from None
        return claims

    def derive_owner(self, claims: dict) -> str:
        """§8.4: the owner scope IS the verified sub. No client-supplied owner
        value exists anywhere in this module's signatures — by construction."""
        sub = claims.get("sub")
        if not sub or not isinstance(sub, str) or len(sub) > 64:
            raise AuthRefusal("ARV-AUTH-004",
                              "the verified token carries no usable sub "
                              "(not a user, not an owner)", 401)
        return sub


def default_config_for_project() -> AuthConfig:
    """The pinned project's auth shape (the runbook §20.1's verified values).
    Kept as a FUNCTION (not module state) so the service composes explicitly."""
    return AuthConfig(
        issuer="https://wcuuakhdmsmmxagvbdmg.supabase.co/auth/v1",
        audience="wcuuakhdmsmmxagvbdmg",
        jwks_url="https://wcuuakhdmsmmxagvbdmg.supabase.co/auth/v1/.well-known/jwks.json",
        expected_kid="55dac17b-cd6c-475d-b599-2588575f15ef",
    )
