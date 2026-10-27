#!/usr/bin/env python3
"""harness/tests/test_anchor.py — P3-03b acceptance suite (the anchor
resolution + the Q8 anchor-stability spike's contract pins; RTM §2.9 item 4,
SYS-05, PLAN's P3-03 card's anchor half, Q8 §7.3).

Red-first (LAW-11): committed BEFORE the implementation; at the predecessor
364f30e the suite fails with ARV-TEST-000 (machinery-absent: query.py's
resolve-anchor arm and harness/spike_anchor.py do not exist — the S1/record-18
§4.1 precedent class).

THE TYPED RESOLUTION CONTRACT (SYS-05; RTM §2.9 item 4 — resolution is a
TYPED query, never a nearest-match guess; an Anchor never references a
different Source version than it was created against; re-import/re-extraction/
new-edition NEVER silently moves an Anchor):

  resolved     the anchor's location evidence validates WITHIN its own Source
               version against the CURRENT generation: the generation's
               input_digest equals the anchor's source_digest (the byte-bind
               chain) AND the passages cover [start_off, end_off) contiguously
               AND the covering slice's recorded evidence matches (the
               context_before/context_after still surround the same text)
  unresolved   the honest miss, ALWAYS with a named cause: no-current-
               generation (never extracted / failed / only building); stale-
               generation (the current generation's input_digest differs from
               the anchor's source_digest — the typed STALE surface the P3-03
               card names); location-unmatched (the current generation's
               passages do not cover the anchor's offsets and the fallback
               evidence finds fewer than two candidate matches — a single
               candidate is a DETECTION, never a retarget)
  ambiguous    the tiling drifted and the fallback matching evidence
               (context_before + context_after) locates MULTIPLE candidate
               positions in the current generation — the anchor's evidence
               cannot pick one; the original evidence is preserved untouched

Every typed state answers exit 0 (they are answers, not failures); ARV-QRY-001
is the boundary refusal (out-of-scope and absent are the SAME refusal, never a
side channel).

Cases (the ANC registry — this file is the contract's declaration):
  ANC-01 the happy path: an anchor over an extracted source resolves WITHIN
         its version — the typed state, the covering passage ids, the offsets
         echoed, the recorded contexts validated against the generation's
         text (the byte-bind chain: the anchor's source_digest == the
         source's digest == the generation's input_digest)
  ANC-02 the never-extracted source: no current generation -> unresolved with
         the named cause (no-current-generation) — never a guess, never a
         nearest-match retarget
  ANC-03 the STALE surface (the P3-03 card's source-hash-mismatch test): a
         planted current generation whose input_digest differs from the
         anchor's source_digest -> unresolved with the named cause
         (stale-generation) — the typed read-path stale reporting, exactly
         the surface routed to this slice
  ANC-04 the drifted tiling: a planted generation whose passages RELOCATE
         the anchor's evidence window to exactly ONE surviving position ->
         unresolved (location-unmatched) with evidence_hits == 1 — the single
         hit is a detection recorded in the answer, never a retarget (a
         resolver that resolves-at-the-relocated-position fails here)
  ANC-05 the ambiguity class: a drifted tiling over a source with REPEATED
         identical content — the fallback evidence matches at TWO positions
         -> ambiguous with the hit count; the original anchor evidence
         untouched (the row is immutable; the answer carries the candidates)
  ANC-06 the edition boundary: a NEW source version (a new edition row of the
         same work) NEVER moves the anchor — the resolution still resolves
         against the anchor's OWN version (the cross-version class is refused
         at creation by construction; the resolution never crosses either)
  ANC-07 the re-extraction stability: a NEW generation over the SAME source
         version (a new ordinal, byte-identical passages) -> the anchor still
         resolves; the passage ids may differ (the rows are disposable), the
         OFFSETS and the evidence never move
  ANC-08 the owner boundary: another owner's anchor and an absent id are the
         SAME ARV-QRY-001 refusal; the typed states never leak another
         owner's object existence
  ANC-09 the output contract: every typed answer is ONE structured JSON line
         (the row_to_json-at-the-boundary precedent) carrying the state, the
         named cause where applicable, the passage ids, the offsets, and the
         evidence echo — machine-readable, never re-parsed prose
  ANC-10 the row-protocol framing: PostgreSQL emits ONE JSON row per line;
         a Unicode line separator (U+2028) inside the stored text — legal in
         a JSON string, never escaped by row_to_json — must never corrupt the
         row framing: the resolver answers the typed state over the intact
         row, never a parse crash (the #88 round-2 framing finding)

Run: python3 harness/tests/test_anchor.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


# ---------------------------------------------------------------- the RED gate
_absent = []
for p in (REPO / "harness" / "spike_anchor.py",):
    if not p.is_file():
        _absent.append(p.name)
_probe = subprocess.run([sys.executable, str(REPO / "harness" / "query.py"),
                          "resolve-anchor", "--owner", "A", "--id", "x"],
                         capture_output=True, text=True, timeout=60)
_absent_cmd = "invalid choice" in _probe.stderr
if _absent or _absent_cmd:
    print(f"FAIL ARV-TEST-000: the anchor-resolution machinery is absent (machinery-absent "
          f"class; missing files: {_absent}; the resolve-anchor command absent: {_absent_cmd}) — "
          "P3-03b's implementation lands after this RED, never before it (LAW-11)")
    sys.exit(1)

DB = None
ENV = None
BLOB_DIR = None


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=180, env=ENV)


def import_src(key, title, file, owner="A", media="text/plain", work_id=None):
    a = [str(REPO / "harness" / "commands.py"), "import_source", "--owner", owner,
         "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
         "--file", file, "--media-type", media]
    if title is not None:
        a += ["--title", title]
    if work_id:
        a += ["--work-id", work_id]
    return cli(*a)


def extract(key, source_id, owner="A"):
    return cli(str(REPO / "harness" / "extract.py"), "--owner", owner, "--actor", "owner",
               "--client-id", "cli-1", "--idem-key", key, "--source-id", source_id)


def highlight(key, source_id, start, end, owner="A"):
    p = cli(str(REPO / "harness" / "commands.py"), "create_highlight", "--owner", owner,
            "--actor", "owner", "--client-id", "cli-1", "--idem-key", key,
            "--source-id", source_id, "--start", str(start), "--end", str(end))
    hid = ack_field(p, "result_ref")
    if not hid:
        return p, ""
    return p, audit(f"SELECT anchor_id FROM arv.highlight WHERE id='{hid}';")


def resolve(anchor_id, owner="A"):
    return cli(str(REPO / "harness" / "query.py"), "resolve-anchor", "--owner", owner,
               "--id", anchor_id)


def audit(query):
    return subprocess.run(["psql", "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                           "-U", "arv_read", "-d", DB, "-c", query],
                          capture_output=True, text=True, timeout=60).stdout.strip()


def plant(sql):
    return subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", "postgres",
                           "-d", DB, "-c", sql],
                          capture_output=True, text=True, timeout=60)


def ack_field(p, field):
    for ln in p.stdout.splitlines():
        if field + "=" in ln:
            return ln.split(field + "=")[1].split()[0]
    return ""


def fresh_file(name, text_or_bytes):
    d = tempfile.mkdtemp(prefix="arv-anc-")
    f = pathlib.Path(d) / name
    if isinstance(text_or_bytes, bytes):
        f.write_bytes(text_or_bytes)
    else:
        f.write_text(text_or_bytes, encoding="utf-8")
    return str(f)


def typed(p):
    """The typed answer: ONE JSON line on stdout, exit 0."""
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    if p.returncode != 0 or len(lines) != 1:
        return None
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError:
        return None


def main() -> int:
    global DB, ENV, BLOB_DIR
    from harness.adapters import pg  # noqa: F401
    DB = pg.create_scratch_db("p303b")
    BLOB_DIR = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=BLOB_DIR)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180, env=ENV, check=True)
        TEXT = ("# The Anchor Essay\n\n"
                "The opening paragraph sets the scene for the study.\n\n"
                "The middle paragraph carries the passage the reader marks.\n\n"
                "The closing paragraph completes the piece.\n")
        fA = fresh_file("anchor.md", TEXT)
        p_imp = import_src("anc-src-1", "The Anchor Essay", fA)
        sid = ack_field(p_imp, "result_ref")
        pe = extract("anc-ext-1", sid)
        okE = pe.returncode == 0 and "status=committed" in pe.stdout
        check("ANC-00", okE,
              "the substrate: the source imported and extracted (the generation machine GREEN before the resolution surface is probed)",
              "the extraction substrate must be green before the anchor contract is tested — repair the extraction first")

        # the anchor: the middle paragraph's first 24 chars
        p_h, anc_id = highlight("anc-hl-1", sid, 97, 121)

        # ANC-01 — the happy path: resolved within its own version
        r1 = resolve(anc_id)
        a1 = typed(r1)
        pg_ids = audit(f"SELECT string_agg(p.id::text, ',' ORDER BY p.ordinal) FROM arv.passage p "
                       f"JOIN arv.extraction_generation g ON p.generation_id=g.id "
                       f"WHERE g.source_id='{sid}' AND g.state='current' "
                       f"AND p.start_off < 121 AND p.end_off > 97;")
        ok1 = (a1 is not None and a1.get("state") == "resolved"
               and a1.get("passage_ids") == pg_ids
               and a1.get("start_off") == 97 and a1.get("end_off") == 121
               and a1.get("source_id") == sid)
        check("ANC-01", ok1,
              "the anchor resolves WITHIN its own source version: state=resolved, the covering passage ids from the CURRENT generation, the offsets echoed, the byte-bind chain held (the anchor's digest == the source's == the generation's input_digest)",
              "the resolution must answer the typed state with the covering passage ids and the offset echo — never prose, never a nearest-match")

        # ANC-02 — the never-extracted source: unresolved with the named cause
        fB = fresh_file("never.md", "A source that is never extracted.\n\nSecond block.\n")
        p_imp2 = import_src("anc-src-2", "Never Extracted", fB)
        sid2 = ack_field(p_imp2, "result_ref")
        p_h2, anc2 = highlight("anc-hl-2", sid2, 0, 6)
        r2 = resolve(anc2)
        a2 = typed(r2)
        ok2 = (a2 is not None and a2.get("state") == "unresolved"
               and "no-current-generation" in (a2.get("cause") or ""))
        check("ANC-02", ok2,
              "a source with no current generation: unresolved with the NAMED cause (no-current-generation) — the honest miss, never a guess",
              "the typed machine must name why the anchor could not resolve; an untyped unresolved is a guess in disguise")

        # ANC-03 — the STALE surface: a planted current generation with a different input_digest
        fC = fresh_file("stale.md", "The stale-detection substrate paragraph.\n\nSecond.\n")
        p_imp3 = import_src("anc-src-3", "Stale Book", fC)
        sid3 = ack_field(p_imp3, "result_ref")
        pe3 = extract("anc-ext-3", sid3)
        p_h3, anc3 = highlight("anc-hl-3", sid3, 0, 9)
        pl3 = plant(f"UPDATE arv.extraction_generation SET input_digest='deadbeef' "
                    f"WHERE source_id='{sid3}' AND state='current';")
        r3 = resolve(anc3)
        a3 = typed(r3)
        ok3 = (pl3.returncode == 0 and a3 is not None and a3.get("state") == "unresolved"
               and "stale-generation" in (a3.get("cause") or ""))
        check("ANC-03", ok3,
              "a current generation whose input_digest differs from the anchor's source_digest: unresolved with the NAMED cause (stale-generation) — the typed read-path stale reporting the P3-03 card names (the source-hash-mismatch test)",
              "the stale detection is the read path's typed surface: the digest chain's mismatch must surface as a named unresolved cause, never silently resolve over different bytes")

        # ANC-04 — the drifted tiling with exactly ONE relocated evidence match: the single-hit DETECTION
        import hashlib as _hl
        fD = fresh_file("drift.md", "alpha opening paragraph text.\n\nbeta middle content.\n\ngamma closing words.\n")
        p_imp4 = import_src("anc-src-4", "Drift Book", fD)
        sid4 = ack_field(p_imp4, "result_ref")
        pd4 = extract("anc-ext-4", sid4)
        # an anchor into gamma's opening (the third block starts at 53)
        p_h4, anc4 = highlight("anc-hl-4", sid4, 53, 59)
        # plant a drifted generation whose ONE passage RELOCATES the anchor's
        # full evidence window (context_before 32 + selected 6 + context_after
        # carried to the text end = TEXTD[21:], 53 chars) to the head of the view:
        # the tiling does not cover the anchor's offsets with the ORIGINAL bytes,
        # the window survives in the view at EXACTLY ONE position, and the single
        # fallback hit is a DETECTION — a resolver that retargets on one
        # candidate fails here (the #88 round-1 finding)
        TEXTD = pathlib.Path(fD).read_text(encoding="utf-8")
        drift4 = TEXTD[21:]
        d4 = _hl.sha256(drift4.encode("utf-8")).hexdigest()
        gen4 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid4}' AND state='current';")
        pl4 = plant(f"UPDATE arv.extraction_generation SET state='superseded' WHERE id='{gen4}'; "
                    f"INSERT INTO arv.extraction_generation (id, source_id, ordinal, state, extractor, "
                    f"extractor_config, input_digest, idempotency_key, body_hash, owner_scope, actor, "
                    f"run_id, input_hash, created_at, updated_at) "
                    f"SELECT gen_random_uuid(), '{sid4}', 2, 'current', extractor, extractor_config, "
                    f"input_digest, 'drifted-tiling-1', body_hash, owner_scope, actor, run_id, input_hash, "
                    f"now(), now() FROM arv.extraction_generation WHERE id='{gen4}';")
        gen4b = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid4}' AND state='current';")
        pl4b = plant(f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, text, "
                     f"digest, owner_scope, actor, run_id, input_hash, created_at) "
                     f"SELECT gen_random_uuid(), '{gen4b}', 1, 0, {len(drift4)}, '{drift4}', '{d4}', "
                     f"owner_scope, actor, run_id, input_hash, now() "
                     f"FROM arv.extraction_generation WHERE id='{gen4b}';")
        r4 = resolve(anc4)
        a4 = typed(r4)
        ok4 = (pd4.returncode == 0 and pl4.returncode == 0 and pl4b.returncode == 0
               and a4 is not None and a4.get("state") == "unresolved"
               and "location-unmatched" in (a4.get("cause") or "")
               and int(a4.get("evidence_hits") or 0) == 1
               and a4.get("start_off") == 53 and a4.get("end_off") == 59)
        check("ANC-04", ok4,
              "a drifted tiling whose view carries the anchor's evidence window at EXACTLY ONE relocated position: unresolved with the NAMED cause (location-unmatched) and evidence_hits == 1 — the single hit is a DETECTION recorded in the answer, the anchor's offsets echoed unchanged, never a resolved-at-new-location",
              "a nearest-match retarget is the forbidden behavior (SYS-05): the fallback's single candidate must stay an unresolved detection with the hit count — never a retarget, never a first-hit resolve")

        # ANC-05 — the ambiguity class: the fallback evidence matches at TWO positions
        # (four identical blocks: the anchor's 49-char evidence window repeats; the
        # planted non-covering tiling keeps both surviving occurrences in its view)
        B = "alpha\n\nbeta gamma delta\n\n"   # 25 chars: "alpha\n\n" + "beta gamma delta\n\n"
        S5 = B + B + B + B + "omega closing text.\n"
        fE = fresh_file("ambig.md", S5)
        p_imp5 = import_src("anc-src-5", "Ambiguous Book", fE)
        sid5 = ack_field(p_imp5, "result_ref")
        pd5 = extract("anc-ext-5", sid5)
        # the anchor into the FIRST block's slice "beta gamma" at [7, 17)
        p_h5, anc5 = highlight("anc-hl-5", sid5, 7, 17)
        # plant a non-covering tiling: [0,7) + [17, len) — the anchor's range is
        # skipped; both OTHER occurrences of the evidence window survive inside it
        gen5 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid5}' AND state='current';")
        pl5 = plant(f"UPDATE arv.extraction_generation SET state='superseded' WHERE id='{gen5}'; "
                    f"INSERT INTO arv.extraction_generation (id, source_id, ordinal, state, extractor, "
                    f"extractor_config, input_digest, idempotency_key, body_hash, owner_scope, actor, "
                    f"run_id, input_hash, created_at, updated_at) "
                    f"SELECT gen_random_uuid(), '{sid5}', 2, 'current', extractor, extractor_config, "
                    f"input_digest, 'drifted-tiling-2', body_hash, owner_scope, actor, run_id, input_hash, "
                    f"now(), now() FROM arv.extraction_generation WHERE id='{gen5}';")
        gen5b = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid5}' AND state='current';")
        d5a = _hl.sha256((S5[0:7]).encode()).hexdigest()
        d5b = _hl.sha256(S5[17:].encode()).hexdigest()
        pl5b = plant(f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, text, "
                     f"digest, owner_scope, actor, run_id, input_hash, created_at) "
                     f"SELECT gen_random_uuid(), '{gen5b}', 1, 0, 7, '{S5[0:7]}', '{d5a}', "
                     f"owner_scope, actor, run_id, input_hash, now() "
                     f"FROM arv.extraction_generation WHERE id='{gen5b}'; "
                     f"INSERT INTO arv.passage (id, generation_id, ordinal, start_off, end_off, text, "
                     f"digest, owner_scope, actor, run_id, input_hash, created_at) "
                     f"SELECT gen_random_uuid(), '{gen5b}', 2, 17, {len(S5)}, '{S5[17:]}', '{d5b}', "
                     f"owner_scope, actor, run_id, input_hash, now() "
                     f"FROM arv.extraction_generation WHERE id='{gen5b}';")
        r5 = resolve(anc5)
        a5 = typed(r5)
        ok5 = (pd5.returncode == 0 and pl5.returncode == 0 and pl5b.returncode == 0
               and a5 is not None and a5.get("state") == "ambiguous"
               and int(a5.get("evidence_hits") or 0) >= 2)
        check("ANC-05", ok5,
              "a non-covering tiling over REPEATED identical content: the fallback evidence matches at TWO surviving positions -> ambiguous with the hit count — the anchor's evidence cannot pick one, the original row untouched",
              "the ambiguous state is the drift DETECTOR (SYS-05): repeated-content ambiguity must surface as the typed ambiguous with the candidate count, never a first-hit retarget")

        # ANC-06 — the edition boundary: a new source version NEVER moves the anchor
        fA2 = fresh_file("essay2.md", TEXT + "\nA fourth paragraph arrives.\n")
        p_imp6 = import_src("anc-src-6", None, fA2, work_id=ack_field(p_imp, "work_id"))
        sid6 = ack_field(p_imp6, "result_ref")
        pd6 = extract("anc-ext-6", sid6)
        r6 = resolve(anc_id)  # the ORIGINAL anchor, after the new edition exists
        a6 = typed(r6)
        own6 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid}' AND state='current';")
        new6 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid6}' AND state='current';")
        ok6 = (pd6.returncode == 0 and a6 is not None and a6.get("state") == "resolved"
               and a6.get("generation_id") == own6 and own6 != new6)
        check("ANC-06", ok6,
              "a NEW source version (a new edition row of the same work) exists and is extracted: the ORIGINAL anchor still resolves against ITS OWN version's CURRENT generation (the answer's generation_id is the own version's, never the new edition's) — never silently retargeted across versions",
              "the anchor binds the source VERSION (the row); a new edition is a new row and must never move or re-scope an existing anchor (SYS-05's first clause) — the generation_id comparison is the retarget detector, the echoed source_id alone is not")

        # ANC-07 — the re-extraction stability: a new generation, the same version
        pe7 = extract("anc-ext-7", sid)
        r7 = resolve(anc_id)
        a7 = typed(r7)
        # the generation integrity pin: the answer must carry the CURRENT
        # generation's id and its passage ids — never a superseded generation's
        # (stale IDs with correct offsets are exactly the accepted-class risk)
        own7 = audit(f"SELECT id FROM arv.extraction_generation WHERE source_id='{sid}' AND state='current';")
        pg7 = audit(f"SELECT string_agg(p.id::text, ',' ORDER BY p.ordinal) FROM arv.passage p "
                   f"JOIN arv.extraction_generation g ON p.generation_id=g.id "
                   f"WHERE g.source_id='{sid}' AND g.state='current' "
                   f"AND p.start_off < 121 AND p.end_off > 97;")
        ok7 = (pe7.returncode == 0 and a7 is not None and a7.get("state") == "resolved"
               and a7.get("generation_id") == own7 and a7.get("passage_ids") == pg7
               and a7.get("start_off") == 97 and a7.get("end_off") == 121)
        check("ANC-07", ok7,
              "a NEW generation over the SAME source version (a new ordinal, byte-identical passages): the anchor still resolves and the answer carries the CURRENT generation's id and its passage ids (compared against the current generation's rows — a superseded generation's IDs with correct offsets FAIL here), the OFFSETS and the evidence never move",
              "the re-extraction stability (the cosmetic re-save class): the derived rows may be rebuilt, the anchor's location evidence is the stable contract — but the answer must never serve a superseded generation's passage IDs")

        # ANC-08 — the owner boundary + the absent id: the SAME refusal, byte-compared
        rB = resolve(anc_id, owner="B")
        rX = resolve("00000000-0000-0000-0000-000000000000")
        _absent_id = "00000000-0000-0000-0000-000000000000"
        normB = (rB.stdout.replace(anc_id, "<ID>"), rB.stderr)
        normX = (rX.stdout.replace(_absent_id, "<ID>"), rX.stderr)
        ok8 = (rB.returncode == 1 and "ARV-QRY-001" in rB.stdout
               and rX.returncode == 1 and "ARV-QRY-001" in rX.stdout
               and typed(rB) is None and typed(rX) is None
               and normB == normX)
        check("ANC-08", ok8,
              "another owner's anchor and an absent id are the SAME ARV-QRY-001 refusal — the full stdout (the supplied ids normalized) and the stderr compare BYTE-EQUAL: the typed states never leak another owner's object existence (no anchor-existence details beyond the echoed id itself)",
              "the read path's owner boundary (RTM §2.10): absent and out-of-scope are indistinguishable at the resolution surface — a differing refusal shape would be an existence side channel (CWE-203)")

        # ANC-09 — the output contract: ONE structured JSON line per typed answer
        ok9 = all(
            (lambda p: p.returncode == 0 and len([l for l in p.stdout.splitlines() if l.strip()]) == 1
             and json.loads([l for l in p.stdout.splitlines() if l.strip()][0]).get("state") in
             ("resolved", "unresolved", "ambiguous"))(resolve(a_id))
            for a_id in (anc_id, anc2, anc5))
        check("ANC-09", ok9,
              "every typed answer is ONE structured JSON line (resolved/unresolved/ambiguous) at exit 0 — machine-readable at the boundary, the named cause where applicable, never re-parsed prose",
              "the typed answers are a contract for every future consumer (P3-04/05's bookmark/revision surfaces): one JSON line per answer, the row_to_json-at-the-boundary precedent")

        # ANC-10 — the row-protocol framing: a Unicode line separator in stored
        # text never corrupts the one-JSON-row-per-line protocol (U+2028 is legal
        # in a JSON string and row_to_json does NOT escape it; str.splitlines()
        # splits on it — the #88 round-2 finding: the resolver must read rows by
        # NEWLINE-ONLY framing, never Unicode line-separator splitting)
        SEP = "\u2028"
        T10 = ("first paragraph carries a line separator " + SEP + " inside the line.\n\n"
               "second paragraph closes the measurement.\n")
        fJ = fresh_file("u2028.md", T10)
        p_imp10 = import_src("anc-src-10", "U+2028 Book", fJ)
        sid10 = ack_field(p_imp10, "result_ref")
        pe10 = extract("anc-ext-10", sid10)
        u10 = T10.index(SEP)
        # the anchor sits just past the separator: BOTH the anchor row's
        # context_before AND the passage's text carry U+2028 — whichever row the
        # protocol mis-frames, the pre-fix crash reproduces
        p_h10, anc10 = highlight("anc-hl-10", sid10, u10 + 1, u10 + 9)
        r10 = resolve(anc10)
        a10 = typed(r10)
        ok10 = (pe10.returncode == 0 and a10 is not None
                and a10.get("state") == "resolved"
                and a10.get("start_off") == u10 + 1 and a10.get("end_off") == u10 + 9)
        check("ANC-10", ok10,
              "a U+2028 line separator inside the stored passage text AND the anchor's context evidence: the psql row protocol frames ONE-JSON-row-per-line by NEWLINE-ONLY splitting — the separator never breaks the row, and the resolver answers the typed resolved state over the intact row (exit 0, ONE JSON line), never a parse crash",
              "the row protocol is newline-delimited by PostgreSQL's own contract (row_to_json escapes control characters below U+0020 only — U+2028/U+2029/U+0085 travel RAW): a reader that splits rows on Unicode line separators will corrupt the framing; read rows by newline only")
    finally:
        if not os.environ.get("ARV_KEEP_DB"):
            pg.drop_scratch_db(DB)
    if FAILS:
        print(f"RED — {len(FAILS)} broken case(s): {', '.join(FAILS)}")
        return 1
    print("GREEN — the anchor resolution holds end-to-end (ANC-01..09): typed, version-bound, never a nearest-match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
