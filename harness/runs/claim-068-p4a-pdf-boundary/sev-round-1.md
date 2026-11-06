# SEV round-1 — CLAIM-068 / P4-A slice four (the PDF boundary)

- **Agent label:** agent-9c4e2f17
- **Date:** 2026-11-06 (UTC)
- **Slice:** CLAIM-068 — P4-A slice four: the PDF boundary (the honest passthrough class, never a text-extraction claim)
- **Base:** `237d4d8` (origin/main, CLAIM-067's merged head) · **Head:** `0360912` (slice/claim-068-p4a-pdf-boundary)
- **Chain:** `a61993c` (open + records) → `e4a52b8` (RED, suite bound) → `927629d` (typed red record) → `24a8a92` (GREEN, the one-liner) → `0360912` (the probe repair, the disclosed amendment)

## 1. What I ran

Rig: pg 17 on 127.0.0.1:5433 (`pgbuild` PATH/LD_LIBRARY_PATH), cwd `/home/z/my-project/Arivoo`, HEAD `0360912`. No repo source modified; writes only to scratch DBs (all dropped — `pg_database` re-checked empty), `/tmp`, and this report.

- `git diff 237d4d8...HEAD` (full, all 13 paths) + the per-file diffs for `formats.py`, `test_pdf.py`, `red-records.json`, `scope.txt`, `red-01.txt`, `CLAIMS.md`.
- `python3 harness/tests/test_pdf.py` → **exit 0, PDF-01..05 all PASS** ("PDF SUITE GREEN").
- `python3 harness/tests/test_format.py` → **exit 0** (FMT-01..06 GREEN — the passthrough's blast radius).
- `python3 harness/tests/test_epub.py` → **exit 0** (EPB-01..06 GREEN, incl. the round-1-repair pin EPB-06).
- Red-records chain: `sha256sum harness/tests/test_pdf.py` at HEAD; `git show e4a52b8:harness/tests/test_pdf.py | sha256sum`; the amendment diff `git diff e4a52b8:…test_pdf.py HEAD:…test_pdf.py` (hunk count + full body); the RED-tree passthrough via `git show 237d4d8:harness/formats.py`.
- Scope: `git diff --name-only 237d4d8...HEAD` vs `scope.txt` vs the CLAIMS.md CLAIM-068 open row.
- Sweep: TODO/FIXME/placeholder/XXX over the diff; the matrix's no-pdf-row honesty (PDF-04 ran live).
- Adversarial probes a–d on my own scratch DBs (`arv_sev8_a..d`, all dropped): see §3.

## 2. Findings

**Zero open P0/P1/P2.** Three P3 observations, all routed/notes — none requiring in-slice repair:

- **F1 (P3, observation — judged honest per the landed letter, routed to the future scan/OCR increment):** probe (a) shows an ALL-ASCII PDF (valid UTF-8 by construction) not only imports but **extracts with exit 0** — its PDF syntax becomes the derived text. Judgment: **the landed contract's honest behavior, not a defect.** The pins: `harness/extract.py:299` (ARV-EXT-002 fires only on "not valid UTF-8 text" — *the DECODE, never the media type*), `harness/formats.py:84-98` (the passthrough "declares no reading capability… never extractable" — i.e. it declares no *refusal* either; the boundary lives at extraction) and `harness/formats.py:122-127` (the passthrough decode arm returns `""`, leaving the text domain to the decode). A media-type-based refusal of a decode-valid PDF would (i) contradict EXT-02's letter and (ii) break the slice's own PDF-04 one-class equivalence (the same ASCII bytes under `application/octet-stream` extract identically — refusing only the pdf label would make the named type a *second* class). The residual risk (syntax-as-text mistaken for content) sits inside the claim's bounded exclusions ("no PDF text extraction — the scan/OCR class, Q8's owner gate"). Routed to that increment's owner; nothing to repair here.
- **F2 (P3, pre-existing — out of slice scope):** probe (d): `export.py restore` *validates* every archive blob (present + digest-matched, `harness/export.py` do_restore step 5) but does not provision the destination's blob store — `ARV_BLOB_DIR` remains the operator's boundary (the module header's own statement). This is CLAIM-060's landed design, untouched by this slice; the PDF-relevant substance verified fully (see §3d). No CLAIM-068 action.
- **F3 (P3, note):** the GREEN commit `24a8a92`'s message says "NO TEST AMENDMENTS", yet the follow-up `0360912` chains exactly one amendment. Verified the amendment is confined to the module-level machinery-absent **probe** (the e4a52b8→HEAD diff is exactly **1 hunk / 44 lines**: the import-based ambient-DB probe → the DB-free `INTAKE_OK` registry probe); **no assertion changed, the five cases untouched** — so the message's substance (the *cases* unmodified, first-run GREEN on the case body) holds, and the disclosure + chain are exact and honest in `0360912` + `red-records.json`. Commit messages are immutable; the record is coherent. No action.

Verified-clean items (no findings): the one-liner is exactly `PASSTHROUGH = {"application/octet-stream", "application/pdf"}` (`harness/formats.py:98`) with `INTAKE_OK = set(ADAPTERS) | PASSTHROUGH` (`:102`) — no decode arm, no matrix row, no PDF-specific path anywhere; `decode()` returns `""` for the whole passthrough class (`:127-128`); `gate.py` TESTS registers `test_pdf.py` (ARV-RED-008); scope — all 13 diff paths declared in `scope.txt` (which pre-declares the superset `commands.py`/`capability.py`, unchanged this slice — fine); CLAIMS.md carries the CLAIM-068 open row with the matching glob set + the CLAIM-067 rule-4 close row; sweep — zero TODO/FIXME/placeholder in added lines (the single rg hit is `ARV-XXX-NNN`, the repo's own generic-code idiom, in a *context* line of PLAN.md's pre-existing P4-00b card; `git diff -- PLAN.md | rg '^[-+].*(TODO|FIXME|placeholder|XXX)'` → none); no-pdf-row honesty observed live (PDF-04 asserts `fmts == {text/plain, application/json, application/epub+zip}`, all `api_version=1` — PASS).

Red-records chain (exact at every link): HEAD sha256 `11508528…831f` == `current_sha256` == the sole amendment's `new_sha256`; binding `git show e4a52b8:… | sha256sum` = `c2f9837a…5451` == `binding_sha256` at the RED commit `e4a52b8435b56f4b49026f82e0377651f4e0eaac`; the amendment ADDITIVE (probe replacement only); the RED re-observable by construction — at `237d4d8` `PASSTHROUGH = {"application/octet-stream"}` (verified via `git show`), so the amended registry probe exits 1 there; `red-01.txt` records the original import-based probe's observed exit 1 + ARV-TEST-000/ARV-FMT-001.

## 3. Probes

All on fresh scratch DBs (`pg.create_scratch_db` + `migrate.py`), dropped after (re-checked: zero `arv_sev8%` rows).

- **(a) ALL-ASCII PDF under `application/pdf`:** import → `status=committed durability_rung=local_durable api_version=1`; **extract → exit 0, ACK committed** (the syntax-as-text accepted). Zero-effect N/A (it is a success, not a refusal). Judgment: honest per EXT-02's letter — see F1.
- **(b) octet-stream equivalence, live:** the SAME binary PDF bytes under both media types → **same content digest** (one content-addressed blob; `blob.get == ORIGINAL` for both); import acks **byte-equal modulo ids** (result_ref/work_id/idem_key — the idem keys differ by my own choice; every other field — command, status, durability_rung, api_version — byte-equal); extraction refusal **heads byte-equal**: `FAIL ARV-EXT-002: the source is not valid UTF-8 text — the readable-text boundary (the DECODE, never the media type); the extraction never guesses a text…`; **zero generation rows** added by either refusal. One class, never two — observed.
- **(c) BOM'd UTF-8 text renamed `.pdf` under `application/pdf`:** import committed; **extract committed (exit 0)** — the decode succeeds, so it extracts exactly as it would under any label; the blob keeps the ORIGINAL bytes **with the BOM intact**. Matches the landed contract (the decode is the boundary, never the media type — the media type declares the passthrough class only).
- **(d) export/restore over a PDF source:** export → `EXPORTED owner=A tables=13 rows=4 state_hash=c49bd7ed…`; restore into a clean migrated DB → `RESTORED … state_hash_match=true state=restored derived_state=pending_rebuild`; the restored source row carries `media_type=application/pdf` with the SAME digest; the archive's blob at that digest is **byte-equal to the ORIGINAL PDF bytes** (207 bytes, verified). The PDF rides the export/restore machine like any source. (Destination blob-store provisioning is the operator's `ARV_BLOB_DIR` boundary — F2, pre-existing.)

## 4. Disposition

**PASS** — zero open P0/P1/P2 (three P3 observations: F1 routed to the future scan/OCR increment's owner gate, F2 pre-existing out-of-slice, F3 a historical-message note with the chain exact). The slice's claims all verified live: the one-line named-type passthrough, the durable import with original bytes, the extraction boundary at the named ARV-EXT-002 decode, no pdf matrix row, the octet-stream equivalence, the exact red-records chain with one additive disclosed amendment, the clean scope, and the clean sweep.
