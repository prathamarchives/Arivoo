# PROOF SHEET — slice claim-067-p4a-epub-intake (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): b67099710deceb35c4ef417762c21eb67d810450
- generated (last record's timestamp): 2026-11-06T18:51:14.965646+00:00
- run records: 12

## Run records (command, exit, output digest)
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 5846ed54f199f08a · 2026-11-06T18:05:40.432654+00:00
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 5846ed54f199f08a · 2026-11-06T18:05:42.731421+00:00
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 5846ed54f199f08a · 2026-11-06T18:05:49.211025+00:00
- `python3 harness/tests/test_position.py` -> exit 0 · output sha256 14a843991330adb4 · 2026-11-06T18:05:52.811878+00:00
- `make verify` -> exit 0 · output sha256 e284d67937514cf0 · 2026-11-06T18:11:38.702172+00:00
- `make verify` -> exit 0 · output sha256 732781f582496fd7 · 2026-11-06T18:17:31.339818+00:00
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 ed043118645d115c · 2026-11-06T18:35:47.063627+00:00
- `python3 harness/tests/test_keyword_index.py` -> exit 0 · output sha256 95730366032f329c · 2026-11-06T18:35:51.738651+00:00
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 ed043118645d115c · 2026-11-06T18:45:13.572842+00:00
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 ed043118645d115c · 2026-11-06T18:45:16.321640+00:00
- `python3 harness/tests/test_epub.py` -> exit 0 · output sha256 ed043118645d115c · 2026-11-06T18:45:25.622032+00:00
- `make verify` -> exit 0 · output sha256 8c803a29f4e69244 · 2026-11-06T18:51:14.965646+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- NOT VERIFIED — the honest limits of CLAIM-067 / P4-A slice three (the EPUB
- intake: the zip/XHTML adapter by the stdlib path; LAW-04; never
- empty-by-omission).
- WHAT THIS SLICE PROVES: the application/epub+zip intake through the EXISTING
- durability ladder (the adapter registry's THIRD approved row — never a second
- path); the stdlib-only container walk (zipfile + xml.etree + html.parser —
- ARV-DEP-008); the OPF/container structure verification with the typed
- epub-family refusals (ARV-FMT-004 the not-a-zip container, ARV-FMT-005 the
- broken structure, ARV-FMT-006 the unreadable content set — each zero-effect,
- digest-named, staged bytes recoverable); the XHTML-derived plain text (the
- reflow class) readable at EVERY text-access site through the ONE read_text
- home (extraction, the keyword index at import AND at rebuild, the
- highlight/bookmark/position offset validations, the coverage measure); the
- capability matrix's third MEASURED row; the position surface composing over
- the derived view (the same generation binding, byte-identical machinery).
- THE HONEST LIMITS:
- - THE CORPUS IS SYNTHETIC (Q8's gate, unchanged): the suite's EPUBs are
- stdlib-built fixtures (mimetype + container + OPF + two chapters). Real-world
- EPUB quirks — unusual OPF layouts, encrypted-content.xml wrappers, obfuscated
- fonts, XHTML with entities or CDATA oddities, multi-MB spines — are NOT
- claimed stable. The owner's real-document corpus remains the owner gate.
- - THE WALK HAS NO DECOMPRESSION BOUND (the SEV round-1 routed P3): a
- hostile zip-bomb-shaped container decompresses without limit (an 80 MB
- chapter materialized in 0.40 s in the reviewer's probe). The staged-bytes
- contract holds (the refusal classes still refuse named); the HARDENING (a
- per-entry or total decompressed-size bound) is a follow-up under Q8's
- synthetic gate — NOT claimed here. Imports also walk the container twice
- (the import-boundary validation + the keyword-index ride), a cost note.
- - A PARTIAL SPINE SILENTLY TRUNCATES (the SEV round-1 routed P3,
- formats.py:261): a spine whose itemrefs name one present and one MISSING
- document indexes the present one and drops the missing without a refusal
- (the fully-broken classes refuse; the partial class truncates). The honest
- boundary: a book with a partially-broken reading order imports with its
- readable subset. A stricter refuse-on-any-missing form is a follow-up
- decision (it trades partial readability for strictness), never silently
- claimed either way.
- - NO DRM CIRCUMVENTION SURFACE (the bounded exclusion, held): an encrypted
- EPUB's chapters are the undecodable/unreadable classes — the typed refusal
- with the bytes staged. No decryption is attempted or claimed.
- - NO PDF (the following slice), NO READER CLIENT (P4-B's repo): the derived
- view is backend text; the rendering client is another repo.
- - THE DERIVED TEXT IS THE STRIP'S OWN FORM: block edges break lines,
- style/script/head/title are skipped, paragraphs join with newlines. The
- strip is deterministic but NOT a layout claim (fixed-layout fidelity,
- pagination, CFI-style anchors are out of scope; positions over the EPUB
- view are byte-offsets in the DERIVED text — the mapping-layer question the
- CLAIM-066 notverified disclosed remains open for the reader client).
- - THE mimetype-ENTRY STRICTNESS IS NOT ENFORCED: the walk reads by name
- (zipfile), so a container without the EPUB-spec's first-stored mimetype
- entry still reads if the container/OPF chain holds (a lenient read; the
- spec-strict validation is a follow-up, disclosed).
- - THE SEV CHAIN: round 1 BLOCKED (agent-5d3d9a17: the rebuild's bookmark-arm
- P1 — an epub-anchored bookmark silently vanished from search after
- rebuild_keyword_index — + the record-58 scope P2 + the two routed P3s
- above) repaired RED-first with the additive EPB-06 pin; round 2 FINAL PASS
- (agent-9b3f1d24: zero open P0/P1/P2/P3, the RED replayed by the reviewer
- at the pre-repair tree, the repair live-proved on the reviewer's own rig).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 5c4b63d9eedef866b6c50b26d6a619591c49e306e58f49f0818936de1078e487
- reviewed_diff_sha256: a3aee383eef6cb6f08a8532c5211f8f833b07003a82caeeda4583388e32d52f4
- disposition: PASS
- findings: 0 (open P0/P1: 0)
- not-verified entries: 1

## Assembly
- sheet sha256 (of the content above, excluding this line): 52f66dc879e850fa6dcc64520ede07bd723ca854feb3a628b3b7b95b2dcb2080
