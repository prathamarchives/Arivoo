"""harness/api/testkeys.py — the ES256 test-token forging helper (the approved
boundary's own surface for the auth contract's test legs — the battery and the
acceptance campaigns mint their tokens through here, never importing jwt/
cryptography outside harness/api/; ARV-DEP-009's scoped law)."""
import base64

import jwt as pyjwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from harness.api import auth as _auth


def mint_key(kid: str = "test-key-1"):
    """A fresh ES256 keypair + its JWK dict (the JWKS cache's own injection form)."""
    priv = ec.generate_private_key(ec.SECP256R1())
    raw = priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    jwk = {"kty": "EC", "crv": "P-256", "kid": kid, "alg": "ES256",
           "x": b64(raw[1:33]), "y": b64(raw[33:65])}
    return priv, jwk


def auth_config(issuer="https://test-issuer/auth/v1", audience="test-aud",
                jwks_url="https://test-jwks/.well-known/jwks.json", kid="test-key-1"):
    return _auth.AuthConfig(issuer=issuer, audience=audience,
                            jwks_url=jwks_url, expected_kid=kid)


def bind_jwks(jwk):
    """Pin the JWKS cache to the forged key (the test injection — never a fetch)."""
    _orig = _auth._JwksCache._refresh
    _auth._JwksCache._refresh = lambda self: (setattr(self, "_jwk", jwk),
                                              setattr(self, "_fetched_at", 1))
    return _orig


def mint_token(priv, cfg, sub, kid="test-key-1"):
    return pyjwt.encode({"sub": sub, "iss": cfg.issuer, "aud": cfg.audience,
                         "exp": 9999999999, "iat": 1}, priv,
                        algorithm="ES256", headers={"kid": kid})
