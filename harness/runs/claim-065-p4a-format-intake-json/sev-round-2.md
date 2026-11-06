# SEV round-2 (FINAL) — CLAIM-065 / P4-A slice one (the JSON format intake)

- **Agent label:** agent-6eb065b0 (fresh-context adversarial Systems Engineering Verification, round 2 — final)
- **Date:** 2026-11-06T08:31Z
- **Round:** ROUND 2 — FINAL (verifies the round-1 repair commit only; round 1 = the full-slice review, PASS with two repair-in-slice P3s)
- **Base (origin/main):** `4e758fc2d04220a69cdc94d4fb385fb3c816b8f6`
- **Head under review:** `5f02ca907b2059f4c67c363e388c06c191d171da` (branch `slice/claim-065-p4a-format-intake-json`; the GREEN commit is 82211b2, 5f02ca9 carries the repairs)
- **Repair commit read:** `git show 5f02ca9` — commands.py (one line, the CAP-009 hint), test_format.py (the audit helper + the FMT-05 equality arm), red-records.json (the disclosed amendment, `current_sha256` advanced 3475e7ec… → 8f7ca45b…), run-06.json (the make-verify record), sev-round-1.md (the round-1 report itself)

No repository source file was modified; nothing committed or pushed; the one scratch DB (`arv_sev2f_10816_953642974`, migrated 0001..0013) was dropped after probing (verified: zero rows in pg_database for the name); temp probe files and the temp blob dir removed. This report file is my only write.

---

## 1. What I ran

| Command | Exit | Note |
|---|---|---|
| `git show 5f02ca9` (full diff) | — | exactly the two repairs + the disclosed red-record amendment + the run-06 record + the round-1 report; nothing else in the commit |
| `timeout 300 python3 harness/tests/test_format.py` | **0** | **6 PASS** (FMT-01..06) — FMT-05 green WITH the new zero-effect assertion live |
| Scratch DB `arv_sev2f_10816_953642974` (`pg.create_scratch_db('sev2f')` + `migrate.py` 0001..0013), 4 probe arms at the real CLI boundary, dropped after | see §3 | CAP-009 hint, ARV-FMT-001 coherence, the replay/409/empty-file arms, plus an in-DB census |
| red-records chain for `harness/tests/test_format.py` | — | `current_sha256` `8f7ca45b…b49a` == last amendment `new_sha256` == `sha256sum` of the file at HEAD; amendment prior `3475e7ec…` == `git show 5f02ca9^:harness/tests/test_format.py`; RED binding re-verified: `git show f0e038a:…` == `84b266bd…73b4` (the first amendment's prior / the RED form) |
| `sev.reviewed_diff_sha256('origin/main','claim-065-p4a-format-intake-json')` | — | **digest: `2e207fe7d9e5c3d4a3f13e22389e845e83827546ffe890f75eee840f3bb4cb3c`** |

---

## 2. The repair verdicts

### F1 — the CAP-009 repair hint (round-1 P3, repair-in-slice) — **REPAIRED**
- **The change** (`commands.py:523`): `pass a MIME pair like text/plain or text/markdown` → `pass a MIME pair like text/plain or application/json (the intake-supported formats — see \`python3 harness/capability.py matrix\`; opaque bytes ride the application/octet-stream passthrough)`.
- **Verified live** (probe a): malformed type `text/plain; charset|x` → exit 1, `FAIL ARV-CAP-009`, and the hint names **application/json** ✓, the **matrix pointer** (`python3 harness/capability.py matrix`) ✓, and the **octet-stream passthrough** ✓ — and **zero occurrences of the stale `text/markdown`** in the refusal text.
- **The follow-the-hint loop now terminates**: both suggested types are actually accepted — probe c4 committed a real `text/plain` import and probe c1 committed a real `application/json` import (both `status=committed`, `durability_rung=local_durable`, `api_version=1`). Probe (b) confirms the hint is coherent with the ARV-FMT-001 refusal it used to contradict: `text/markdown` → `FAIL ARV-FMT-001` naming the same supported set (`application/json, text/plain (plus the opaque-bytes passthrough application/octet-stream)`).
- The README documentation gap remains routed to the next docs-authorized touch (out of slice scope — round 1's disposition, unchanged, not a repair item for this commit).

### F2 — FMT-05's unasserted zero-effect arm (round-1 P3, repair-in-slice) — **REPAIRED**
- **The change** (`test_format.py:215-223, 281-286`): a `psql -U arv_read` audit helper; `srcs_before = audit("SELECT count(*) FROM arv.source;")` taken BEFORE the FMT-03 refusal block; `ok5` now asserts `audit("SELECT count(*) FROM arv.source;") == srcs_before` — so the equality spans **all three refusals** (ARV-FMT-001, ARV-FMT-002, ARV-FMT-003), exactly the commit's claim. The dead-variable class is gone: `srcs_before` is now consumed.
- **The assertion is meaningful, not vacuous**: at the point `srcs_before` is taken, FMT-01/FMT-02's valid imports have already landed (count ≥ 2), so the equality proves the three refusals added ZERO source rows. The choice of the SOURCE count (not the journal count) is the correct one — FMT-002/003 legitimately write `failed` journal rows and stage bytes (the recovery substrate), so "zero effect" means zero AUTHORITATIVE effect, which is precisely the check's letter ("no source row").
- **Verified live**: the suite runs green (exit 0, 6 PASS) with the assertion in place on a fresh scratch DB — the count equality holds across all three refusals at the real boundary. The red-record amendment is disclosed with the correct prior/new hashes (§1) and an honest note.
- In-DB confirmation from my own probe DB: the two refused imports (CAP-009, FMT-001) and the 409 left zero `arv.source` rows and zero `import_journal` rows (census: 2 sources / 2 complete journal rows for exactly the two committed imports — nothing phantom).

---

## 3. Probe results (one scratch DB, all at the real CLI boundary)

| # | Probe | Result |
|---|---|---|
| a | **CAP-009** — `--media-type "text/plain; charset|x"` | exit 1, `FAIL ARV-CAP-009` + the NEW hint: `text/plain or application/json (the intake-supported formats — see python3 harness/capability.py matrix; opaque bytes ride the application/octet-stream passthrough)`. No `text/markdown` anywhere in the output. (F1 verified.) |
| b | **ARV-FMT-001** — `--media-type text/markdown` | exit 1, `FAIL ARV-FMT-001: the media type 'text/markdown' is not an intake-supported format (the supported formats: application/json, text/plain (plus the opaque-bytes passthrough application/octet-stream))` + the repair hint (`import one of the supported media types; a new format lands through its own capability-matrix increment`). Coherent with the CAP-009 hint — the two messages now name the SAME boundary. Zero rows in source/journal for this key. |
| c1 | **Valid JSON, first import** (key `sev2f-c1`, `application/json`) | exit 0, `ACK … status=committed result_ref=01a1aff9-66d1-… durability_rung=local_durable api_version=1` — the full frozen ack on the new surface. |
| c2 | **Replay: same key + same payload** | exit 0, `ACK … status=replayed` with the IDENTICAL `result_ref`/`work_id` — the idempotent replay ack shape; in-DB census shows exactly ONE `complete` journal row for the key (the replay adds nothing — exactly-once holds on the JSON surface). |
| c3 | **Same key + DIFFERENT payload** | exit 1, `FAIL ARV-CMD-409: idempotency key 'sev2f-c1' is already recorded with a DIFFERENT body (no silent overwrite…)` + the honest repair hint. The existing ladder's replay guard carries to the new format surface unchanged — no format-specific divergence. |
| c4 | **Adversarial edge: an EMPTY file as `text/plain`** (key `sev2f-c4`) | import COMMITS (exit 0, `status=committed`, `local_durable`, `api_version=1`) — empty bytes are valid UTF-8 text, so intake admits them; the boundary then lives where it always did: extraction refuses typed, `FAIL ARV-EXT-001: the source is empty … never an empty current generation` (exit 1). No silent empty generation, no crash, no untyped path. |
| census | **`arv.source` + `arv.import_journal`** (direct psql) | exactly 2 sources (`application/json`, `text/plain`) + 2 journal rows (both `complete`): zero phantom rows for the CAP-009/FMT-001 refusals and the 409; the replay added no second journal row. The matrix prints exactly the two rows (`application/json`, `text/plain`), both `api_version=1`, no octet-stream row (the passthrough stays a non-row, as designed). |

---

## 4. The digest

`sev.reviewed_diff_sha256('origin/main', 'claim-065-p4a-format-intake-json')` =

```
2e207fe7d9e5c3d4a3f13e22389e845e83827546ffe890f75eee840f3bb4cb3c
```

---

## 5. Observations (non-blocking, for the finalize's ledger)

1. **Agent-label provenance nit (cosmetic, P4-class):** the repair commit's message cites the round-1 SEV as "agent-6aee153a" while the round-1 report file self-labels "agent-481321aa". One label is wrong; the round-1 artifact itself (sev-round-1.md at this slice's runs dir, PASS with the two repair-in-slice P3s) is the record of either way, and the repairs verify on their merits. Note for the finalize; no action required in this slice.
2. Round 1's accepted-with-note classes (F3 strict-JSON edges, F4 failed-retryable semantics, F5 case sensitivity, F6 the disclosed text/plain narrowing) are unchanged by the repair commit — it touches a hint string and a test assertion only — and remain accepted-with-note, notverified at the finalize, exactly as round 1 recorded them.

---

## 6. Verdict

Both round-1 repair-in-slice P3s are repaired and verified at the real boundary: the CAP-009 hint now names only intake-legal types with the matrix pointer and the passthrough note (F1), and FMT-05's zero-effect arm is asserted with a meaningful, spanning, non-vacuous source-count equality that runs green (F2). The red-records chain is intact at every link (RED form 84b266bd… → amendment 3475e7ec… → amendment 8f7ca45b… == the file at HEAD), the suite is 6/6 exit 0, and my probes found no new defect. **Zero open P0/P1/P2/P3.**

**DISPOSITION: PASS**
