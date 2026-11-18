#!/usr/bin/env python3
"""harness/api/auth_selfcheck.py — the ES256 battery (CLAIM-092; in-boundary:
cryptography/pyjwt live only in harness/api/). Prints PASS/FAIL lines."""
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from harness.adapters import clock  # LAW-24

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from harness.api import auth as _auth

FAILS = []

def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + ": " + what)
    if not ok:
        FAILS.append(code)

def main() -> int:
    import jwt as pyjwt
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    import base64
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()

    priv = ec.generate_private_key(ec.SECP256R1())
    raw = priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    jwk = {"kty": "EC", "crv": "P-256", "kid": "test-key-1", "alg": "ES256",
           "x": b64(raw[1:33]), "y": b64(raw[33:65])}
    cfg = _auth.AuthConfig(issuer="https://test-issuer/auth/v1", audience="test-aud",
                           jwks_url="https://test-jwks/.well-known/jwks.json",
                           expected_kid="test-key-1")
    v = _auth.Verifier(cfg)
    v._jwks.prime(jwk)
    mk = lambda **over: pyjwt.encode(
        {"sub": "user-abc", "iss": cfg.issuer, "aud": cfg.audience,
         "exp": clock.now_s() + 600, "iat": clock.now_s(), **over},
        over.pop("_key", priv), algorithm="ES256", headers={"kid": "test-key-1"})

    claims = v.verify(mk())
    check("ARV-AUTH-010", v.derive_owner(claims) == "user-abc",
          "the positive chain: sign -> pinned JWK -> verify -> derive the owner from the VERIFIED sub")
    try:
        v.verify(mk(iss="https://evil/auth/v1")); check("ARV-AUTH-011", False, "issuer refused", )
    except _auth.AuthRefusal as e: check("ARV-AUTH-011", e.code == "ARV-AUTH-003", "a wrong issuer refuses (ARV-AUTH-003)")
    try:
        v.verify(mk(aud="other")); check("ARV-AUTH-012", False, "aud refused")
    except _auth.AuthRefusal as e: check("ARV-AUTH-012", e.code == "ARV-AUTH-003", "a wrong audience refuses")
    try:
        v.verify(mk(exp=clock.now_s() - 10)); check("ARV-AUTH-013", False, "expired refused")
    except _auth.AuthRefusal as e: check("ARV-AUTH-013", e.code == "ARV-AUTH-003", "an expired token refuses")
    try:
        t = pyjwt.encode({"sub": "u", "iss": cfg.issuer, "aud": cfg.audience,
                         "exp": clock.now_s() + 600, "iat": clock.now_s()},
                        "attackers-secret-0123456789abcdef", algorithm="HS256",
                        headers={"kid": "test-key-1"})
        v.verify(t); check("ARV-AUTH-014", False, "HS256 refused")
    except _auth.AuthRefusal as e: check("ARV-AUTH-014", e.code == "ARV-AUTH-003", "an HS256 token refuses (alg confusion closed — the retired signing mode)")
    priv2 = ec.generate_private_key(ec.SECP256R1())
    try:
        t = pyjwt.encode({"sub": "u", "iss": cfg.issuer, "aud": cfg.audience,
                          "exp": clock.now_s() + 600, "iat": clock.now_s()},
                         priv2, algorithm="ES256", headers={"kid": "attacker"})
        v.verify(t); check("ARV-AUTH-015", False, "wrong key refused")
    except _auth.AuthRefusal as e: check("ARV-AUTH-015", e.code == "ARV-AUTH-003", "a wrong-key/unknown-kid token refuses")
    try:
        v.derive_owner({"iss": cfg.issuer, "aud": cfg.audience}); check("ARV-AUTH-016", False, "no-sub refused")
    except _auth.AuthRefusal as e: check("ARV-AUTH-016", e.code == "ARV-AUTH-004", "a token without sub derives no owner")
    tok = mk()
    tam = tok[:-6] + ("AAAAAA" if not tok.endswith("AAAAAA") else "BBBBBB")
    try:
        v.verify(tam); check("ARV-AUTH-017", False, "tampered refused")
    except _auth.AuthRefusal as e: check("ARV-AUTH-017", e.code == "ARV-AUTH-003", "a tampered token refuses")
    print()
    if FAILS:
        print("RED — the ES256 battery refuses: " + ", ".join(FAILS))
        return 1
    print("GREEN — the ES256 battery passes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
