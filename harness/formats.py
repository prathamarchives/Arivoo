#!/usr/bin/env python3
"""harness/formats.py — P4-A slice one: the format adapter registry (CLAIM-065;
PLAN's elaborated P4-A card; record 57 §2) + P4-A slice three: the EPUB
intake (CLAIM-067; the zip/XHTML adapter by the stdlib path; record 59 §2).

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
  ARV-FMT-004  the NOT-A-ZIP container (the epub family) — epub-typed bytes
               that are not a zip container at all; refused after staging
               with the digest NAMED (the bytes recoverable)
  ARV-FMT-005  the BROKEN STRUCTURE (the epub family) — a zip without the
               container/OPF reading chain; refused after staging with the
               digest NAMED
  ARV-FMT-006  the UNREADABLE CONTENT SET (the epub family) — the structure
               holds but the reading-order documents yield no readable
               text; refused after staging with the digest NAMED

The registry (stdlib-native only — the honest increments; no external
parsers, no OCR class):
  text/plain           the first approved format (the passthrough decode)
  application/json     the second (validate + the native-text decode)
  application/epub+zip the third (the zip container walk + the
                       XHTML-derived plain text — the reflow class; the
                       container is NOT the text: native_text False)

Exit contract: the callers (commands.py's import path, extract.py's text
access, the offset-validating commands) translate the _FmtRefusal into
their boundary's FAIL lines; this module only raises. read_text is the ONE
home for 'the readable text of a stored source' — the text formats decode,
the epub walks the container, every caller routes through it (never a
second decode path).
"""
import io
import json
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


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
    "application/epub+zip": {
        "native_text": False, "scan_ocr": False, "layout": "reflow",
        "extraction": "supported", "approved": True,
        "extractor": "arivoo-epub-xhtml.v1",
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
    if media_type == "application/epub+zip":
        # P4-A slice three (CLAIM-067): the container walk + the XHTML text
        # derivation — the derived plain text IS the decode's return (the
        # staged-bytes contract rides the epub family's own refusals; the
        # walk precedes the UTF-8 decode: a zip container IS binary bytes,
        # never a text decode's subject)
        return _epub_text(data, digest)
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


# ---- P4-A slice three (CLAIM-067): the EPUB walk, stdlib only ----

class _XhtmlText(HTMLParser):
    """The XHTML strip (the stdlib html.parser): the text nodes of the BODY,
    with style/script/head/title skipped and block edges breaking lines —
    the derived plain text is the reflow class's own view, never a layout
    claim (fixed-layout PDFs are their own slices)."""

    _SKIP = {"style", "script", "head", "title"}
    _BREAK = {"p", "div", "br", "li", "ul", "ol", "table", "tr", "td",
              "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._buf: list = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip += 1
        elif tag in self._BREAK:
            self._buf.append("\n")

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip:
            self._skip -= 1
        elif tag in self._BREAK:
            self._buf.append("\n")

    def handle_data(self, data):
        if not self._skip and data.strip():
            self._buf.append(data)

    def text(self) -> str:
        lines = [ln.strip() for ln in "".join(self._buf).splitlines()]
        return "\n".join(ln for ln in lines if ln)


def _local(tag: str) -> str:
    """ElementTree's namespaced tag -> the local name (namespace-tolerant)."""
    return tag.rsplit("}", 1)[-1]


def _epub_text(data: bytes, digest: str) -> str:
    """The EPUB derivation: the zip container (stdlib zipfile) -> the OPF via
    META-INF/container.xml -> the spine's reading order -> the XHTML-derived
    plain text. Every failure is a named typed refusal with the digest NAMED
    (the staged-bytes contract); the walk never circumvents DRM (an encrypted
    container is the undecodable class — the bytes stay staged)."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as e:
        raise _FmtRefusal(
            "ARV-FMT-004",
            f"the payload at digest {digest} is not a zip container ({e}) "
            "(the not-a-zip class — epub-typed bytes must be a zip)",
            "supply an EPUB container (a zip with META-INF/container.xml + "
            "the OPF reading chain); the STAGED BYTES ARE PRESERVED at the "
            "named digest (recover them from the blob store; the journal row "
            "is failed-retryable)", digest=digest)
    names = set(zf.namelist())
    if "META-INF/container.xml" not in names:
        raise _FmtRefusal(
            "ARV-FMT-005",
            f"the payload at digest {digest} is a zip without META-INF/container.xml "
            "(the broken-structure class — the container chain is the reading root)",
            "supply an EPUB with the container/OPF chain; the STAGED BYTES ARE "
            "PRESERVED at the named digest (recover them from the blob store; "
            "the journal row is failed-retryable)", digest=digest)
    try:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
    except ET.ParseError as e:
        raise _FmtRefusal(
            "ARV-FMT-005",
            f"the container at digest {digest} is not parseable XML ({e}) "
            "(the broken-structure class)",
            "supply a well-formed META-INF/container.xml; the STAGED BYTES ARE "
            "PRESERVED at the named digest", digest=digest)
    opf_path = ""
    for el in container.iter():
        if _local(el.tag) == "rootfile" and el.get("full-path"):
            opf_path = el.get("full-path")
            break
    if not opf_path or opf_path not in names:
        raise _FmtRefusal(
            "ARV-FMT-005",
            f"the container at digest {digest} names no readable OPF rootfile "
            f"({opf_path or 'none named'}) — the broken-structure class",
            "supply an EPUB whose container.xml points at the OPF inside the "
            "zip; the STAGED BYTES ARE PRESERVED at the named digest", digest=digest)
    try:
        opf = ET.fromstring(zf.read(opf_path))
    except ET.ParseError as e:
        raise _FmtRefusal(
            "ARV-FMT-005",
            f"the OPF at digest {digest} is not parseable XML ({e}) "
            "(the broken-structure class)",
            "supply a well-formed OPF package; the STAGED BYTES ARE PRESERVED "
            "at the named digest", digest=digest)
    base = opf_path.rsplit("/", 1)[0]
    manifest, spine = {}, []
    for el in opf.iter():
        if _local(el.tag) == "item" and el.get("id") and el.get("href"):
            href = el.get("href")
            manifest[el.get("id")] = (base + "/" + href if base else href)
        elif _local(el.tag) == "itemref" and el.get("idref"):
            spine.append(el.get("idref"))
    docs = [manifest[i] for i in spine if i in manifest and manifest[i] in names]
    if not docs:
        raise _FmtRefusal(
            "ARV-FMT-005",
            f"the OPF at digest {digest} carries no reading order (an empty "
            "spine, or itemrefs naming no manifest document) — the "
            "broken-structure class",
            "supply an EPUB whose OPF spine lists its reading-order documents; "
            "the STAGED BYTES ARE PRESERVED at the named digest", digest=digest)
    parts = []
    for href in docs:
        raw = zf.read(href)
        try:
            xhtml = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise _FmtRefusal(
                "ARV-FMT-006",
                f"the reading-order document {href} at digest {digest} cannot be "
                "decoded as UTF-8 text (the unreadable-content class — every "
                "spine document must be readable XHTML)",
                "supply readable XHTML documents in the spine; the STAGED BYTES "
                "ARE PRESERVED at the named digest (recover them from the blob "
                "store; the journal row is failed-retryable)", digest=digest)
        stripper = _XhtmlText()
        try:
            stripper.feed(xhtml)
            stripper.close()
        except Exception as e:  # the unparseable-markup class: named, never a crash
            raise _FmtRefusal(
                "ARV-FMT-006",
                f"the reading-order document {href} at digest {digest} cannot be "
                f"parsed as XHTML ({type(e).__name__}: {e}) — the "
                "unreadable-content class",
                "supply well-formed XHTML documents in the spine; the STAGED "
                "BYTES ARE PRESERVED at the named digest", digest=digest)
        t = stripper.text()
        if t:
            parts.append(t)
    if not parts:
        raise _FmtRefusal(
            "ARV-FMT-006",
            f"the reading order at digest {digest} yields no readable text "
            "(every spine document is empty of text nodes) — the "
            "unreadable-content class",
            "supply an EPUB whose reading-order documents carry text; the "
            "STAGED BYTES ARE PRESERVED at the named digest (recover them from "
            "the blob store; the journal row is failed-retryable)", digest=digest)
    return "\n\n".join(parts) + "\n"


def read_text(media_type: str, digest: str) -> str:
    """P4-A slice three (CLAIM-067): the ONE home for 'the readable text of a
    stored source' — every text-access site routes through this (extract.py's
    decode, the keyword-index ride, the highlight/bookmark/position offset
    validations; never a second decode path). The blob is the ORIGINAL bytes
    (content-addressed, never transformed): the text formats decode, the epub
    re-derives (the walk is deterministic over digest-verified bytes), and
    the octet-stream passthrough decodes too (the readable-text boundary is
    the DECODE, never the media type — the landed EXT-02/EXT-03 contract)."""
    from harness.adapters import blob
    data = blob.get(digest)
    if media_type == "application/epub+zip":
        return _epub_text(data, digest)
    return data.decode("utf-8")
