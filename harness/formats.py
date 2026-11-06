#!/usr/bin/env python3
"""harness/formats.py — P4-A slice one: the format adapter registry (CLAIM-065;
PLAN's elaborated P4-A card; record 57 §2).

ONE HOME for the intake-format truth: an adapter entry DECLARES the format's
capabilities (the capability matrix derives from this registry — never a
second declaration) and CARRIES the decode/validation the import boundary
calls. A format is intake-supported ONLY through this registry, and every
failure is a named, typed, zero-effect refusal whose staged bytes survive
(the explicit-error contract — staged bytes are never lost).

The typed refusal vocabulary (the boundary's named outcomes):
  ARV-FMT-001  the UNSUPPORTED media type — MIME-valid but unregistered:
               the approval registry (this module) IS the capability matrix;
               refused at the boundary, zero effect
  ARV-FMT-002  the MALFORMED payload — the bytes decode but fail the
               format's own grammar (invalid JSON); refused AFTER the blob
               staging with the digest NAMED (the bytes recoverable)
  ARV-FMT-003  the UNDECODABLE/ENCRYPTED payload — the bytes cannot decode
               as UTF-8; refused after staging with the digest NAMED

The registry (stdlib-native only — the honest increments; no external
parsers, no OCR class, no zip container in this slice):
  text/plain        the first approved format (the passthrough decode)
  application/json  the second (validate + the native-text decode)

Exit contract: the callers (commands.py's import path) translate the
_FmtRefusal into the boundary's FAIL lines; this module only raises.
"""
import json


class _FmtRefusal(Exception):
    """A named format refusal at the import boundary (zero effect — RTM §6)."""

    def __init__(self, code: str, msg: str, repair: str, digest: str = ""):
        super().__init__(msg)
        self.code, self.repair, self.digest = code, repair, digest


# THE REGISTRY — the adapter entry IS the capability declaration (the matrix
# derives from this; a new format's row lands with its own increment slice,
# never by editing this comment). native_text: the bytes ARE the text;
# scan_ocr: a scan/OCR path exists (never in this slice); layout: reflow vs
# fixed; extraction: the block tiler over the decoded form.
ADAPTERS = {
    "text/plain": {
        "native_text": True, "scan_ocr": False, "layout": "reflow",
        "extraction": "supported", "approved": True,
        "extractor": "arivoo-text-blocks.v1",
    },
    "application/json": {
        "native_text": True, "scan_ocr": False, "layout": "reflow",
        "extraction": "supported", "approved": True,
        "extractor": "arivoo-text-blocks.v1",
    },
}

# THE BYTES PASSTHROUGH — the landed P3-02 contract (EXT-03's own pin): the
# blob store is content-addressed BYTES storage; an opaque binary imports
# honestly (durable capture never refused for content) and the READABLE-TEXT
# boundary stays at EXTRACTION (ARV-EXT-002, the named refusal — the
# "import anything, extract what's readable" media class). The passthrough
# is INTAKE-legal, never a matrix row (it declares no reading capability)
# and never extractable.
PASSTHROUGH = {"application/octet-stream"}

# every INTAKE-legal media type: the approved reading formats + the bytes
# passthrough — anything else is the typed ARV-FMT-001 refusal.
INTAKE_OK = set(ADAPTERS) | PASSTHROUGH


def check_registered(media_type: str) -> None:
    """The boundary check (after the MIME grammar, before any effect): a
    MIME-valid type that is NEITHER an approved reading format NOR the bytes
    passthrough is the typed ARV-FMT-001 refusal — the approval registry IS
    the capability matrix (plus the landed opaque-bytes class)."""
    if media_type not in INTAKE_OK:
        known = (", ".join(sorted(ADAPTERS)) + " (plus the opaque-bytes passthrough "
                 + ", ".join(sorted(PASSTHROUGH)) + ")")
        raise _FmtRefusal(
            "ARV-FMT-001",
            f"the media type {media_type!r} is not an intake-supported format "
            f"(the supported formats: {known})",
            "import one of the supported media types; a new format lands through "
            "its own capability-matrix increment (never a generic claim)")


def decode(media_type: str, data: bytes, digest: str) -> str:
    """The decode + the format's own grammar check — called AFTER the blob
    staging (the staged-bytes contract: a refusal here NAMES the digest and
    the bytes stay recoverable at it). The BYTES PASSTHROUGH declares no
    reading capability: no decode, no grammar — the readable-text boundary
    stays at extraction (ARV-EXT-002, the landed EXT-03 contract)."""
    if media_type in PASSTHROUGH:
        return ""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise _FmtRefusal(
            "ARV-FMT-003",
            f"the payload at digest {digest} cannot be decoded as UTF-8 "
            "(the undecodable/encrypted class — a text format's bytes must be text)",
            "supply decodable bytes; the STAGED BYTES ARE PRESERVED at the named "
            "digest (recover them from the blob store; the journal row is "
            "failed-retryable)", digest=digest)
    if media_type == "application/json":
        try:
            json.loads(text)
        except (json.JSONDecodeError, ValueError):
            raise _FmtRefusal(
                "ARV-FMT-002",
                f"the payload at digest {digest} is not valid JSON "
                "(the malformed-payload class)",
                "supply a well-formed JSON document; the STAGED BYTES ARE "
                "PRESERVED at the named digest (recover them from the blob "
                "store; the journal row is failed-retryable)", digest=digest)
    return text
