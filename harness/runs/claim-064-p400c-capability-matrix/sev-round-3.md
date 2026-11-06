# SEV round-3 — FINAL — CLAIM-064 / P4-00c (the format capability matrix + extraction readiness)

- **Agent label:** agent-8a9d9a45 (fresh-context Systems Engineering Verification, round 3 — THE FINAL ROUND)
- **Date:** 2026-11-06T07:04Z
- **Slice:** CLAIM-064 — P4-00c: the format capability matrix + extraction readiness (harness/capability.py NEW + the README rewrite + query.py's `_refuse` per-family hints + test_capability.py CAP-01..06)
- **Base (origin/main):** `647f3cb18fd877acd08689f195b61269e742fd8a` (PR #98 merge, CLAIM-063)
- **Head under review:** `b3a5d1cc3d02e143974bec33de7d3171e68878e0` (branch `slice/claim-064-p400c-capability-matrix`; working tree clean apart from round-2's untracked report)
- **Prior rounds:** round 1 (agent-ee8ed9dd) BLOCKED — 1×P1 + 2×P2 + 4×P3, every P1/P2 repaired or routed at `b3a5d1c`; round 2 (agent-1bc56354) PASS — no new blocking findings. This round re-verified the load-bearing claims INDEPENDENTLY (nothing taken on the prior rounds' word).

---

## 1. What I ran (commands + exit codes)

| Command | Exit | Note |
|---|---|---|
| `git diff origin/main...HEAD --stat` + the FULL diffs of `harness/capability.py` (164 new lines) and `harness/query.py` (+ `gate.py` TESTS registration, README, STATE/CLAIMS/AGENTS/PLAN, record 56) | 0 | the load-bearing files read line-by-line before anything was executed |
| `timeout 300 python3 harness/tests/test_capability.py` | **0** | **CAP-01..06 all PASS (6 PASS)** — the derivation corpus + the planted-RAISE failed state included |
| `timeout 300 python3 harness/tests/test_boundary.py` | **0** | **BND-01..06 all PASS (6 PASS)** — the frozen P4-00b contract intact after the `_refuse` family change |
| `python3 harness/gate.py --slice claim-064-p400c-capability-matrix --diff origin/main --skip-suites` | 1 | **32 PASS; refuses ONLY `ARV-PRF-002` (Proof Sheet) + `ARV-SEV-001` (sev.json)** — exactly the two pre-finalize artifact classes; **zero scope/claims/law/size refusals** |
| Scratch DB `arv_sev3c_1981_948083847` (`pg.create_scratch_db('sev3c')` + `migrate.py` 0001..0013, blob dir under /tmp) — 12 adversarial probes (§3) | — | **dropped after (verified: 0 `arv_%` databases remain)**; round-2's F9-note stray `arv_sev2_7053248` is also gone |
| The red-record chain + digest + scope checks (§4) | 0 | all three of round-2's load-bearing claims re-derived independently |

No repository source file was modified; nothing committed or pushed; the scratch DB and all temp corpus/blob dirs removed. This report is the round's only write.

---

## 2. The claim, as verified

`harness/capability.py` delivers exactly what the slice claims, at the real boundary:

- **`matrix`** — the DECLARED row: `{"format": "text/plain", "native_text": true, "scan_ocr": false, "layout": "reflow", "extraction": "supported", "approved": true, "extractor": "arivoo-text-blocks.v1", "api_version": 1}` — exactly what the landed tiler machinery does, never more (no second format, no OCR, verified against live extraction behavior on six different corpora).
- **`surfaces`** — the RESERVED registry: `source-open/position` with `owner_phase P4-A/B` + the read-position contract sketch (no reader-client work smuggled).
- **`measure --owner --source`** — the MEASURED row: state in {ready, not_extracted, building, failed, stale} + passages + the blob-backed coverage fraction + generation_id/ordinal/extractor + `fail_reason` on failed; absent and cross-owner are the SAME typed `ARV-QRY-001` refusal (template-identical, stderr-identical — the no-oracle extended to the new surface).
- **README** — rewritten to the frozen P4-00b contract (the versioned search header, the bounded/paginated list arms with `# more=` truth markers, `api_version` on every ack/read) + the capability/readiness section + the reservation note. **Every documented form checked TRUE to live output** (§3 P13).
- **query.py `_refuse`** — the per-family repair hints (note → list-notes, bookmark → list-bookmarks, capture → list-captures, source/anchor honest forms) with the per-arm template equality intact — BND-04/CAP-05 re-verified green.

---

## 3. The adversarial probe list (all on my own scratch DB, dropped after)

| # | Probe | Observed |
|---|---|---|
| P1 | **Markdown-heading corpus** (`# Heading One` / content / `# Heading Two` / content / trailing `# Trailing`): extract → measure | `state=ready, passages=3, coverage=1.0, ordinal=1` — the heading attaches FORWARD to the following content block, the trailing heading is its OWN passage, the tiling covers everything. Per the tiler's pinned rule. |
| P2 | **Single-word corpus** (`hello`, no newline): extract → measure | `passages=1, coverage=1.0` — the degenerate corpus extracts cleanly. |
| P3 | **Whitespace-only source** (`"  \n\n \n\t\n"`): import → extract → measure | import ACKs (committed); extract refuses the typed `ARV-EXT-001` (exit 1 — "an empty input is a named refusal… the refusal precedes any row"); `measure` answers the TYPED `not_extracted, passages=0, coverage=0.0, generation_id=null` at exit 0 — never silence, never a lie (no generation row exists → not_extracted is the honest state; see F12-note). |
| P4 | **Leading-blank-line corpus** (`"\n\nAlpha block.\n\nBeta block."`): extract → measure | `passages=2, coverage=0.925926` — the HONEST fraction (25/27, hand-computed match: the tiler's skipped leading-blank prefix shows in the fraction, exactly as the tiling contract says). |
| P5 | **Seven-hashes line** (`####### seven hashes` — outside `^#{1,6}`): extract → measure | `passages=2, coverage=1.0` — 7 hashes is NOT a heading (the CommonMark-conformant reading of the pinned regex); two content blocks, two passages. |
| P6 | **No-oracle on the new surface**: `measure --owner B --source <A's real source>` vs `measure --owner A --source <absent uuid>` | both exit 1 `FAIL ARV-QRY-001:` with the source-family hint; stdout template-identical after id-substitution (True); **stderr byte-identical (both empty)** — no side channel. |
| P7 | **Injection-shaped source id** (`x' OR '1'='1` and `not-a-uuid`) | typed `ARV-QRY-002` (the read failed — invalid uuid syntax) at exit 1 — the quote-escaping held (`''` doubling visible in the refused literal; no injection, the DB rejected the value). **The same class and form as origin/main's `get-source`** (probed side-by-side: identical behavior) — pre-existing shared machinery, not a new surface's defect. |
| P8 | **matrix/surfaces**: exit codes, line shape, version | one JSON row each, exit 0, empty stderr, `api_version: 1` on every row; no owner argument needed, no owner data reachable. |
| P9 | **Marker-laden note** (content `state=ready coverage=0.0 # more=true api_version=9 not_extracted`) + measure + search | `measure` over the source UNCHANGED after the note (`ready/3/1.0` — the readiness path reads source/generation/passage rows only, no note content can confuse it); `search --owner A ready` → the note (`matched_terms=1`); `search --owner A state=ready` → header-only at exit 0 (see F13-note); the search header is the README's exact `# api_version=1 kind|entity_id|revision|matched_terms`. |
| P10 | **Supersede/ordinal/replay**: new-key re-extract of P1's source → measure; same-key replay → measure | new-key extract ACKs committed; `measure` answers `ordinal=2, generation_id=<the NEW id>, ready/3/1.0` — the LATEST generation, the DB truth confirmed (`ordinal 1 superseded, 2 current` via psql); the same-key replay ACKs `status=replayed` and measure is unchanged. |
| P11 | **Stale simulation**: superuser `UPDATE arv.source SET digest=…` | **REFUSED by the `ARV-CAP-005` append-only trigger even as postgres** — "stale structurally unreachable" is ENFORCED, not merely asserted; the source unchanged, measure still `ready/0.925926`. (The stale branch stays disclosed defensive dead code.) |
| P12 | **The failed state, planted independently of the suite**: `BEFORE INSERT ON arv.passage WHEN (NEW.ordinal = 2)` trigger raising `ARV-R3-TEST` → extract → drop trigger → measure | extract exits 1 with the named `ARV-EXT-003` + the observed cause; `measure` answers **`state=failed, "fail_reason": "ARV-EXT-003: ERROR:  P0001: ARV-R3-TEST: planted round-3 failure", passages=0, coverage=0.0`** at exit 0 — the row's reason byte-matches the generation row's own `fail_reason` column (psql cross-checked). The F3 repair verified live with my own fixture, not just the suite's. |
| P13 | **README truth**: `list-notes --limit 50`, empty owner, `--limit 0/1001`, search header, import-ack form, matrix/measure examples | `# api_version=1` opener + id rows + `# more=false` closer; the empty owner answers exactly the two lines; `ARV-QRY-004` at 0 and 1001; the import ack carries `durability_rung=local_durable api_version=1`; **the README's matrix and measure examples match the live outputs key-for-key** (key sets equal: {source_id, media_type, state, generation_id, ordinal, passages, coverage, extractor, api_version} / {format, native_text, scan_ocr, layout, extraction, approved, extractor, api_version}). |

---

## 4. The load-bearing spot-checks (round-2's claims re-derived)

- **The anchored driver (round-1 F1, the P1):** `git diff --name-only origin/main...HEAD` lists 21 files — **zero under `tools/`** (grep exit 1). The gate run confirms at the PR boundary: no `ARV-SCOPE-002`/`ARV-CLM-002`. **REPAIR HOLDS.**
- **The red-record chain:** `binding_commit 2f4d3ef` exists (`git cat-file -t` → commit); `harness/capability.py` ABSENT at 2f4d3ef (`git cat-file -e` fails — the RED is honest machinery-absent); `sha256(test_capability.py at 2f4d3ef) = 5b959d2c…84ed7af` == `binding_sha256`; `sha256(test_capability.py at HEAD) = f54f792f…31a1bc` == `current_sha256` == the sole amendment's `new_sha256` — **the chain is intact and the amendment honestly discloses "no product-side RED existed for F3/F4"** (coverage-gap repairs, the correct LAW-11 treatment). `red-01.txt` carries the observed exit-1 `ARV-TEST-000` with `capability.py matrix exit 2`.
- **The computed digest:** `sev.reviewed_diff_sha256('origin/main','claim-064-p400c-capability-matrix')` at head `b3a5d1c` = **`1fac5b54db5b6315b0dc0a4d5de714bfda1783394d0bec0a1ab00ce8acb83c56`** — identical to round-2's recorded value (sev-round-2.md is untracked and both reports live under the excluded `harness/runs/<slice>/` prefix, so writing the round reports does not move the binding; the finalize's digest-binds-LAST re-bind remains the standing obligation).
- **Round-1/round-2 dispositions vs my observation:** F1 REPAIRED (verified above); F2 ROUTED (the attempt-scoped wording is live in the module docstring — "the latest generation" — and the README — "failed (the last attempt failed)", "building (an extraction in flight…)"; my P10/P12 confirm the source stays readable through building/failed attempts via the serving generation; the notverified disclosure obligation stands for the finalize); F3 REPAIRED (P12 — live fail_reason, plus the suite's CAP-02 pin, green in my run); F4 REPAIRED (TEXT2, the five-block second corpus, green in my run — a hard-code of 3/1.0 cannot pass both); F5 ROUTED (run-06 records `make verify` exit 0 at `570a23c`, the pre-repair head — the label-vs-tree convention; **no run record pins `b3a5d1c`**, so the finalize MUST re-record/mint run-07 at the final content head — standing); F6 REPAIRED (record 56 §2 now reads "the passage count, the coverage fraction over the actual bytes" — verified in the file); F7 ROUTED (the unreadable-blob `ready/coverage=0.0` form disclosed in the code comment, `capability.py:126-128`; the notverified obligation stands).
- **Scope coverage:** all 21 diff files are covered by `scope.txt`'s declarations (`harness/extract.py`/`commands.py` declared-but-untouched — allowed; the gate's scope arm PASSed live).

---

## 5. Findings

**None at P0/P1/P2. None new blocking.** Notes continuing the rounds' F-numbering (rounds 1-2 closed through F11-equivalents):

- **F12-note (informational):** the `ARV-EXT-001` empty-source refusal precedes any generation row (extract.py's own contract), so `measure` answers `not_extracted` — not `failed` — after a refused empty-source extract (P3). Every fact in the row is true of the DB state, the refusal itself was typed at the extract boundary (the user just saw it), and the README's state wordings are generation-row-scoped. Optionally a half-sentence in the finalize's notverified alongside the F2/F7 disclosures; no action required.
- **F13-note (informational, pre-existing at base):** a search CLI term carrying `=` (e.g. `state=ready`) matches no indexed keyword (header-only answer at exit 0) — the tokenizer splits note CONTENT on non-alphanumerics but not the CLI terms. This is origin/main search behavior; this slice's query.py diff is `_refuse`-only (verified line-by-line). No slice action.
- **F14-note (the standing finalize obligations, re-confirmed — routed, not open defects):** (a) re-record the measured set (or mint run-07) at the FINAL content head — run-06 pins `570a23c`, not `b3a5d1c` (F5's routing); (b) the notverified must carry the F2 (latest-generation semantics over a readable current) + F7 (unreadable-blob ready/coverage=0.0) disclosures; (c) the digest re-binds after the SEV reports, proofsheet, and sev.json land (digest-binds-LAST). These are the same obligations every prior slice carried at this stage.
- **Hygiene:** round-2's F9-note stray DB `arv_sev2_7053248` is gone; after this round the cluster carries ZERO `arv_%` databases (mine dropped and verified).

---

## 6. The computed digest

`sev.reviewed_diff_sha256('origin/main', 'claim-064-p400c-capability-matrix')` at head `b3a5d1c`:

```
1fac5b54db5b6315b0dc0a4d5de714bfda1783394d0bec0a1ab00ce8acb83c56
```

(Subject to the F14-note: re-bind at finalize after the artifacts land.)

---

## 7. Verdict

Round 3 — FINAL. The slice's claim was verified adversarially and independently at the real boundary:

- The amended CAP suite is GREEN (exit 0, 6 PASS) and the frozen P4-00b boundary contract is intact after the `_refuse` change (BND-01..06, exit 0, 6 PASS).
- Twelve probes of my own design — heading attach-forward/trailing, single-word, whitespace-only (ARV-EXT-001 → typed not_extracted), the honest sub-1.0 coverage fraction (0.925926 = 25/27, hand-verified), the seven-hashes non-heading, the no-oracle on the new surface (template + stderr equality), the injection-shaped id (typed, same class as the base's get-source), matrix/surfaces versioning, the marker-laden note (readiness unconfused), supersede/ordinal/replay, the enforced stale-unreachability (ARV-CAP-005 refuses a superuser UPDATE), and my own planted-RAISE failed state with the named reason — **every one behaved per the contract or refused typed**.
- Every README-documented form is TRUE to live output (key-for-key on the matrix/measure examples).
- The gate refuses only the two expected pre-finalize artifact classes; the round-1 P1 repair holds at the diff and at the gate; the red-record chain and the digest verify independently; the round-1/round-2 dispositions all match what I observe.
- No new P0/P1/P2. The residual items are the standing, already-routed finalize obligations (F14-note).

**DISPOSITION: PASS**

*— agent-8a9d9a45, 2026-11-06T07:04Z. Scratch DB `arv_sev3c_1981_948083847` dropped (verified: 0 `arv_%` databases remain); temp corpus/blob dirs removed; no repository source file modified; nothing committed or pushed; this report is the round's only write.*
