"""harness/adapters/blob.py — the Q12-neutral content-addressed blob store (P3-01; RTM §4.4).

The adapter interface: {put(bytes) -> digest, get(digest) -> bytes, exists, delete}.
The rig's implementation is a local filesystem store (the same disposable-by-contract
class as the rig's ephemeral postgres): bytes land under ARV_BLOB_DIR (default
blobs/) at path = sha256 digest. Content addressing makes put() idempotent — a
re-put of the same bytes is a no-op, byte-reuse is STORAGE-level dedup, never
identity (the Q11 baseline). NO provider name, NO signed access, NO cross-store
atomicity or durability promise enters this boundary (Q12 unratified — the
production provider is owner-gated); the Source row stores digest+size+media
type, NEVER the bytes.

Corruption is named, never healed: get() re-hashes its bytes and refuses a
digest that does not re-verify (ARV-BLOB-002) — a corrupt store surfaces as a
named import refusal (ARV-CAP-004 at the command), and the recovery walk that
cleans it is P3-02's. Environment is read ONLY here (LAW-24).
"""
import hashlib
import os
import pathlib
import re

_DEFAULT = pathlib.Path(__file__).resolve().parents[2] / "blobs"
_SAFE = re.compile(r"^[0-9a-f]{64}$")  # the path-traversal guard: a digest is hex-only


def _dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("ARV_BLOB_DIR") or _DEFAULT)


def digest_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def put(data: bytes) -> str:
    """Write bytes; re-put of the same bytes is a no-op (content-addressed)."""
    d = digest_of(data)
    p = _dir() / d
    if not p.exists():
        _dir().mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return d


def get(digest: str) -> bytes:
    """Read bytes back; the read re-verifies the digest (corruption is named)."""
    if not _SAFE.match(digest):
        raise KeyError("ARV-BLOB-001: invalid digest (expected 64 hex chars) — refused before any file access")
    p = _dir() / digest
    if not p.is_file():
        raise KeyError(f"ARV-BLOB-002: blob {digest[:12]} is absent from the store")
    data = p.read_bytes()
    if digest_of(data) != digest:
        raise KeyError(f"ARV-BLOB-003: blob {digest[:12]} failed re-verification (stored bytes do not re-hash to their digest — store corruption, never promoted)")
    return data


def exists(digest: str) -> bool:
    if not _SAFE.match(digest):
        return False
    return (_dir() / digest).is_file()


def delete(digest: str) -> None:
    """Remove one blob (the P3-02 recovery walk's arm; refuses an absent digest)."""
    if not _SAFE.match(digest):
        raise KeyError("ARV-BLOB-001: invalid digest (expected 64 hex chars) — refused")
    p = _dir() / digest
    if not p.is_file():
        raise KeyError(f"ARV-BLOB-002: blob {digest[:12]} is absent from the store")
    p.unlink()
