# SEV round-1 — CLAIM-065 / P4-A slice one (the first additional format intake: JSON by the durability ladder)

- **Agent label:** agent-481321aa (fresh-context adversarial Systems Engineering Verification, round 1)
- **Date:** 2026-11-06T08:17Z
- **Slice:** CLAIM-065 — P4-A slice one: the JSON intake through the EXISTING ladder, the second MEASURED matrix row, the typed refusals ARV-FMT-001/002/003 with the staged-bytes contract
- **Base (origin/main):** `4e758fc2d04220a69cdc94d4fb385fb3c816b8f6` (PR #99 merge, CLAIM-064)
- **Head under review:** `82211b2b8439fe3cd5b9faae8a7223682df0bc18` (branch `slice/claim-065-p4a-format-intake-json`)
- **Commit chain reviewed:** e9fabde (commit A: the post-#99 reconciliation + the P4-A elaboration + CLAIM-065 opened + record 57) → f0e038a (RED: test_format.py FMT-01..06 + the gate registration) → 74bab42 (the typed red-record binding + red-01.txt) → 82211b2 (GREEN: harness/formats.py + the commands.py boundary + the matrix derivation + the BMK-02 amendment + the run records)

No repository source file was modified; nothing committed or pushed; both scratch DBs (`arv_sevf_13393_952102391`, `arv_sevf2_27710_952918609`) were dropped after probing (verified by the drop command's clean exit).

---

## 1. What I ran

| Command | Exit | Note |
|---|---|---|
| `git diff origin/main...HEAD` (full read: formats.py, commands.py hunks, capability.py hunk, gate.py hunk, test_format.py, test_bookmark.py hunk, red-records.json, STATE/CLAIMS/PLAN/AGENTS/WORKLOG/record 57) | — | the slice is exactly the claimed shape: the adapter registry, the FMT-001 check after CAP-009/CAP-007 at validation, the FMT-002/003 decode after the blob verify with the journal failed-retryable update, `FORMATS = ADAPTERS`, the BMK-02 fixture amendment |
| `python3 harness/tests/test_format.py` | 0 | FMT-01..06 all PASS (6/6) |
| `python3 harness/tests/test_extract.py` | 0 | EXT-01..17 GREEN (EXT-03 already used `application/octet-stream` — no amendment needed there) |
| `python3 harness/tests/test_bookmark.py` | 0 | BMK-01..13 GREEN (the amended BMK-02 included) |
| `python3 harness/tests/test_import.py` | 0 | IMP-01..22 GREEN |
| 12 adversarial probes on my own scratch DB (`arv_sevf_13393_952102391`, migrated 0001..0013, dropped after) + a 3-probe case-sensitivity pass on `arv_sevf2_27710_952918609` (dropped after) | see §3 | all at the REAL boundary (commands.py/extract.py/capability.py CLIs + direct `psql -U arv_app` journal/source introspection with the owner GUC) |
| red-records chain: `sha256sum` at HEAD vs `git show <commit>:<file> \| sha256sum` | — | test_format.py: HEAD `3475e7ec…804f4` == `current_sha256` == last amendment `new_sha256`; RED form at f0e038a `84b266bd…73b4` == `binding_sha256`. test_bookmark.py: HEAD `e0b13110…dc656` == `current_sha256` == last amendment `new_sha256`; pre-amend form at 74bab42 `d85309bb…fca0c` == the amendment's `prior_sha256`. Chain intact, both ends verified by git show |
| scope: `git diff --name-only origin/main...HEAD` vs `scope.txt` + the CLAIMS.md row | — | all 20 diff paths ⊆ the declared scope (the runs dir covers its 7 files; `harness/extract.py` is declared-but-untouched — a legal superset); the CLAIMS.md CLAIM-065 row carries the branch, the file list, and the bounded exclusions verbatim |
| `SLICE=claim-065-p4a-format-intake-json GATE_DIFF=origin/main timeout 500 make gate` | 2 | all 26 declared suites PASS on the real stack (incl. test_format.py); the refusal is ONLY the two pre-finalize artifact classes: printed `FAIL ARV-PRF-002` (no Proof Sheet on disk) + `FAIL ARV-SEV-001` (no SEV report at sev.json); the tally line names `ARV-PRF-004, ARV-SEV-001` — the gate's consolidated proofsheet-class label (gate.py:444-450, pre-existing convention, not a slice defect) |

---

## 2. Findings

### F1 — P3 — the CAP-009 repair hint now recommends a media type the boundary refuses (`commands.py:523`)
- **Severity:** P3 (a stale user-facing example, self-correcting in one round trip — NOT the P2 class: no wrong commit, no data loss, no silent behavior).
- **Location:** `harness/commands.py:523` — `repair: pass a MIME pair like text/plain or text/markdown`.
- **Reproduction:** import with a malformed type (`text/plain; charset|x`) → CAP-009's hint says "pass a MIME pair like text/plain or **text/markdown**"; following it literally → the very next check refuses: `FAIL ARV-FMT-001: the media type 'text/markdown' is not an intake-supported format (the supported formats: application/json, text/plain (plus the opaque-bytes passthrough application/octet-stream))` (probe P2). The second refusal DOES carry the honest supported set, so the user self-corrects — but the hint actively points into a refusal. The same class touches the README: the format-capabilities section documents neither the intake-legal set nor the ARV-FMT-001..003 vocabulary (the claim-061 acceptance report even shows a `--media-type text/markdown` command that now refuses at intake).
- **Judgment (as directed):** P3, not P2 — one line of stale example text in an error message whose immediately-following typed refusal names the true boundary; zero durability/correctness impact. But it is exactly the "honesty of the boundary" class this repo polices, and the fix is one line.
- **Disposition:** **repair-in-slice** for the hint (commands.py is in the declared scope D-041; nothing red-record-bound pins that string — CAP-19 pins only the `ARV-CAP-009` token); the README documentation of the intake whitelist + the FMT codes **routes** to the next docs-authorized touch (README.md is OUTSIDE this slice's declared scope — widening it for a docs line is not warranted mid-SEV).

### F2 — P3 — FMT-03's zero-effect arm is unasserted (a dead variable; the pin is weaker than its letter)
- **Severity:** P3 (pin-strength gap, not a behavior bug — my probe P2 verified the zero-effect behavior is real).
- **Location:** `harness/tests/test_format.py:216` — `srcs_before = query("get-source", ...)` is computed and never used; `ok3` asserts only exit 1 + the FAIL prefix + `ref_of(r_f1) == ""` (no ACK line). The check's own letter claims "zero effect (no source row)" — no source/journal count is compared before/after.
- **Reproduction (static):** read lines 215-232; `srcs_before` never appears in `ok3`. My live probe: after three FMT-001 refusals, `arv.source` count unchanged AND `arv.import_journal` has ZERO rows for the refused keys (FMT-001 fires before any staging — the honest zero-effect, stronger than the suite proves).
- **Disposition:** **repair-in-slice** (a two-line count assertion, with the disclosed red-record amendment per the #93..#99 precedent class) — or accept-with-note if the builder prefers to land it with the next suite touch. The behavior itself is correct; this is the "do not claim a guard is enforced until its known-bad proves it" class applied to the suite's own letter.

### F3 — P3 (accept-with-note) — the strict-JSON edges: a UTF-8-BOM'd JSON document refuses ARV-FMT-002
- **Location:** `harness/formats.py` `decode()` — `json.loads` on a `\ufeff`-prefixed string raises (RFC 8259 §8.1 permits, but does not require, ignoring a BOM; the stdlib does not). An empty file under `application/json` also refuses FMT-002 (`json.loads("")`).
- **Reproduction (probe P3/P4):** `\xef\xbb\xbf{"a": 1}` → `FAIL ARV-FMT-002` with the digest named == the file's sha256 and `blob.get(digest)` answering the exact bytes; empty JSON → FMT-002 (digest `e3b0c4…` = sha256 of empty); empty `text/plain` still commits (extract then refuses ARV-EXT-001, the landed form).
- **Disposition:** **accept-with-note** — a typed, zero-effect, staged-bytes-preserved refusal is within the strict-grammar contract ("the bytes must be text; the JSON must be JSON"); the BOM-stripping leniency is a reasonable future adapter refinement, named here so it is a decision, not an accident.

### F4 — observation (accept-with-note) — the "failed-retryable" semantics: same-key + FIXED payload 409s; the recovery window ends at the orphan sweep
- **Reproduction (probe P6):** malformed JSON under key `p6-1` → journal row `failed|ARV-FMT-002`; SAME key + SAME bytes → the staging rewind re-runs and re-refuses identically (no 409, journal stays `failed|ARV-FMT-002`); SAME key + FIXED payload → `ARV-CMD-409` (the crash-domain replay guard, IMP-21's pinned class); NEW key + fixed payload → `status=committed`. So "fix the file and retry" requires a NEW key — the 409's own repair hint says exactly that, so it self-corrects. Second arm: the staged bytes answer at the named digest, but IMP-16's orphan sweep deletes unreferenced artifacts of terminal-FAILED rows — the recovery window is until the sweep runs (the landed ARV-CAP-004 precedent class, extended to the format class exactly as the commit claims).
- **Disposition:** **accept-with-note** — identical to the pre-existing CAP-004 pattern this slice deliberately extends; no new semantics invented.

### F5 — observation (accept-with-note) — registry matching is case-sensitive
- **Reproduction:** `Application/JSON`, `APPLICATION/JSON`, `application/JSON` all pass the CAP-009 grammar and refuse `ARV-FMT-001` (typed, zero effect). RFC 6838 types are case-insensitive; this is the same deliberate narrowness the claim-049 round-2 accepted as-designed for CAP-009's reduced token set, now extended to the registry.
- **Disposition:** **accept-with-note** (same accepted-as-designed class; a refusal is never a wrong commit).

### F6 — observation (judgment) — the text/plain intake path is genuinely NARROWED: non-UTF-8 bytes under text/plain now refuse ARV-FMT-003 (pre-P4-A they committed with `src_text=""`)
- **Reproduction (probe P10):** `b"hello \xff\xfe world"` with the default media type → `FAIL ARV-FMT-003` + digest named + staged bytes; pre-P4-A this committed (the "import-anything" era). The honest route exists and is verified (probe P1): the same bytes under `application/octet-stream` commit `status=committed`, extraction refuses ARV-EXT-002, measure answers `not_extracted`.
- **Judgment:** this is the slice working as designed and as disclosed — the red-record amendment says it in exactly these words ("the pre-P4-A form smuggled binary bytes in as text/plain, a class the format boundary now refuses typed at intake with ARV-FMT-003"), the extractor's own docstring already called text/plain "readable text", and durable capture of opaque bytes is preserved through the passthrough. The FMT-01 "text/plain path unchanged" phrasing is true of the ACK contract, not of the intake boundary — the boundary change is disclosed in the amendment chain but not in README/STATE prose (that gap is F1's routing).
- **Disposition:** **accept-with-note** (the docs gap rides F1).

---

## 3. The probe list (12 probes, one scratch DB, all at the real boundary)

| # | Probe | Result |
|---|---|---|
| P1 | **The passthrough semantics**: binary under `application/octet-stream` | import `status=committed` + `durability_rung=local_durable` + `api_version=1`; extraction refuses `ARV-EXT-002` (the readable-text boundary); measure answers `state=not_extracted` (exit 0, the typed answer — never a silent miss); the matrix has NO octet-stream row. Exactly the claimed design. |
| P2 | **MIME-valid-but-unregistered**: `text/markdown`, `text/csv`, `application/pdf` | all refuse `FAIL ARV-FMT-001` exit 1, no ACK; zero effect verified in-DB: source count unchanged AND zero `import_journal` rows for the refused keys (the check fires before any staging). The FMT-001 repair names the full supported set. |
| P3 | **JSON with a UTF-8 BOM** | refuses `ARV-FMT-002` (F3); the named digest == the file's sha256; `blob.get(digest)` returns the exact original bytes. |
| P4 | **Empty payloads** | empty JSON → `ARV-FMT-002` (digest = sha256 of empty); empty text/plain → commits, extraction refuses `ARV-EXT-001` (unchanged landed form). |
| P5 | **Huge-but-valid JSON** (~10.3MB, 60k notes) | imports `status=committed`; extraction completes; measure: `state=ready`, `passages=1`, `coverage=1.0`, `media_type=application/json`, `api_version=1` (the one-line document is one block — the tiler's honest answer). |
| P6 | **The failed-FMT-002 replay semantics** | journal `failed|ARV-FMT-002`; same key + same bytes → rewind + identical re-refusal (no 409); same key + fixed payload → `ARV-CMD-409`; NEW key + fixed payload → committed. Exactly one source row titled "Malformed". (F4.) |
| P7 | **Cross-owner no-oracle on measure over the JSON source** | B measuring A's JSON source == A measuring an absent id: byte-identical `FAIL ARV-QRY-001` output (modulo the id), same exit 1. The no-oracle holds on the new corpus. |
| P8 | **api_version on every new surface** | matrix: both rows `api_version=1`; measure over the JSON source: `api_version=1`; import acks (JSON, octet-stream, md-as-plain): `api_version=1`; refusals carry NO api_version — consistent with the frozen FAIL shape (refusals never carried it; FMT-06 pins the shape, and the shape holds: `FAIL <code>: msg` + `      repair: …`). |
| P9 | **A .md corpus file as text/plain (the only legal route)** | imports + extracts green; measure `state=ready` (heading attach-forward intact — the extractor is and remains the Markdown-aware tiler; only the media-type LABEL is refused, never the content). Honest boundary: the registry governs the declared type, not the file extension. |
| P10 | **text/plain + non-UTF-8 bytes** | refuses `ARV-FMT-003` with the digest named + staged bytes (F6 — the disclosed narrowing; the pre-P4-A commit path for this class is closed). |
| P11 | **Case sensitivity** (`Application/JSON`, `APPLICATION/JSON`, `application/JSON`) | all refuse `ARV-FMT-001` typed, zero effect (F5 — the accepted-as-designed narrowness class). |
| P12 | **The journal/DB state census** (direct `psql -U arv_app` with the owner GUC) | 9 journal rows exactly as the probes predict (`complete` × 5, `failed|ARV-FMT-002` × 3, `failed|ARV-FMT-003` × 1 — every failed row carries its named reason); 5 sources / 5 works — zero phantom rows for any refused import; the source media types are exactly what was passed (`application/octet-stream`, `text/plain`, `application/json`). |

---

## 4. The three directed judgments

1. **The CAP-009 repair-hint inconsistency — severity?** **P3, not P2.** The hint (`commands.py:523`, "pass a MIME pair like text/plain or text/markdown") predates the registry and now recommends a type the boundary refuses two checks later. It costs the user exactly one extra round trip, and the FMT-001 refusal that catches it carries the true supported set — self-correcting, zero effect, zero data risk. It IS misleading guidance on a frozen user-facing surface and should be repaired (one in-scope line), but it lacks every P2 ingredient (no wrong commit, no lost data, no silent corruption, no broken consumer). The README's missing intake-whitelist documentation is the same defect class routed to the next docs touch (out of the slice's declared scope).
2. **The passthrough design — honest vs the P4-A card's letter?** **Honest.** The card's bounded exclusions (PDF, EPUB, reader-client, position surface) are untouched; the passthrough is the landed P3-02/EXT-03 contract carried forward unchanged and P1 verifies every limb: octet-stream imports durably, the readable-text boundary stays at extraction's ARV-EXT-002, measure answers the typed `not_extracted`, and the matrix never claims a reading capability for opaque bytes (no row). "Imports but never extracts" is the declared design, not a smuggle.
3. **The BMK-02 amendment — substance-preserving?** **Yes, verified.** The fixture's bytes, the pinned refusal (ARV-CAP-008 at the capture boundary), and the pin's structure are unchanged; only the declared media type changed from the smuggled default `text/plain` to the honest `application/octet-stream` — without the amendment the fixture would now refuse at intake (ARV-FMT-003) and never reach the pinned capture refusal, so the amendment is REQUIRED by the new boundary, not cosmetic. The non-UTF-8 source still imports durably (via the passthrough — probe P1's exact class). The digest chain is intact at both ends (§1's sha256 table).

---

## 5. Verdict

The slice does what it claims: one adapter registry (one home — the matrix derives), the JSON intake through the existing ladder with no second durability path, the second matrix row measured never asserted, the three typed refusals with staged bytes that answer at the named digest, and a disclosed, substance-preserving test amendment. The RED is real and bound to the RED commit; the gate refuses only on the two pre-finalize artifact classes; the red-records chain and scope are clean. Open findings: two P3s (F1 the misleading CAP-009 hint — repair-in-slice; F2 the unasserted zero-effect arm — repair-in-slice) and four accept-with-note observations (F3 strict-JSON edges, F4 failed-retryable semantics, F5 case-sensitivity, F6 the disclosed text/plain narrowing). **Zero P0/P1/P2.**

**DISPOSITION: PASS**
