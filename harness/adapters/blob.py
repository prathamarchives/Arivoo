"""harness/adapters/blob.py — the Q12-neutral content-addressed blob store (P3-01; RTM §4.4).

The P3-01 arms: put(bytes) -> digest and get(digest) -> bytes (the §4.4
interface's delete/exists arms land WITH their consumer — P3-02's recovery
walk; never dead code shipped ahead of its use). The rig's implementation is
a local filesystem store (disposable-by-contract, the rig class): bytes live
under ARV_BLOB_DIR (default blobs/) at path = sha256 digest.  Content
addressing makes put() idempotent — byte-reuse is STORAGE-level dedup, never
identity (Q11). NO provider name, NO cross-store atomicity or durability
promise enters this boundary (Q12 unratified); the Source row stores
digest+size+media type, NEVER the bytes. Corruption is named, never healed:
get() re-hashes and refuses (ARV-BLOB-002/003) — the named import refusal
(ARV-CAP-004) is the §3.1 fail-closed verify; the cleanup walk is P3-02's.
Environment is read ONLY here (LAW-24).
"""
import hashlib
import os
import pathlib
import re
import tempfile

_DEFAULT = pathlib.Path(__file__).resolve().parents[2] / "blobs"
_SAFE = re.compile(r"^[0-9a-f]{64}$")  # the path-traversal guard: a digest is hex-only


def _dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("ARV_BLOB_DIR") or _DEFAULT)


def digest_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def put(data: bytes) -> str:
    """Write bytes ATOMICALLY (the #84 CodeRabbit Major): the full content
    lands in a same-directory temp file, then ONE os.replace — a reader ever
    sees NO file or the COMPLETE file, never a partial (write_bytes at the
    final path let a concurrent put's exists() see a half-written file and
    false-refuse a valid import; a killed writer left a truncated file that
    poisoned the digest path forever — red-04.txt). A killed writer now
    leaves only an ignorable .put- orphan (the §3.1 staging class, P3-02's
    recovery walk); an EXISTING file is never touched (healing is forbidden
    — CAP-15's corruption refusal stands)."""
    d = digest_of(data)
    p = _dir() / d
    if not p.exists():
        _dir().mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=_dir(), prefix=".put-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, p)  # atomic on the same filesystem
        except BaseException:
            pathlib.Path(tmp).unlink(missing_ok=True)
            raise
    return d


def get(digest: str) -> bytes:
    """Read bytes back; the read RE-VERIFIES the digest (corruption is named)."""
    if not _SAFE.match(digest):
        raise KeyError("ARV-BLOB-001: invalid digest (expected 64 hex chars) — refused before any file access")
    p = _dir() / digest
    if not p.is_file():
        raise KeyError(f"ARV-BLOB-002: blob {digest[:12]} is absent from the store")
    data = p.read_bytes()
    if digest_of(data) != digest:
        raise KeyError(f"ARV-BLOB-003: blob {digest[:12]} failed re-verification (stored bytes do not re-hash to their digest — store corruption, never promoted)")
    return data
