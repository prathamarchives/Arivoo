# SOURCE-COVERAGE-MANIFEST — Raw Corpus Coverage Control

> **STATUS: ACTIVE CONTROL** (D-025, 2026-10-14; implements stress-review finding F-09). This file is a **coverage map and immutability anchor** for `context/raw/` — NOT an intent authority (source tiers: `/EXECUTION.md` §2, D-022). Owner words live only in `/INTENT-LEDGER.md`; assistant interpretation lives only in session records. This manifest exists so that "every substantive owner intent has been captured" is a **checked claim, not a human assertion** (F-09's exact words), and so that raw-corpus immutability (AUT-02) is mechanically enforced (VER-802, C3-level — was prose-only before this file).

**What this file guarantees:**

1. Every raw file is classified (owner voice / AI analysis / third-party / pasted document) with its reviewed range.
2. Every owner-voice region is mapped to the INT entries that cover it — or listed as an exclusion WITH a reason.
3. Every ledger quote that cites a raw file is mechanically validated against it by `tools/verify_canonical_layer.py` (VER-803) — fabrication and transcription drift are caught, not trusted.
4. Every raw file's SHA-256 is anchored here; any edit to `context/raw/` fails the verifier (VER-802).
5. Deviations between ledger quotes and raw text are enumerated exceptions (§E), never silent.

**How this file changes:** when raw files are added (owner-supplied), when new owner turns are preserved, or when an exception class changes. Every change updates the SHA-256 anchors and lands by PR under the change channel. This file is a Tier-4 control artifact (reference tier) — it never outranks root documents.

---

## 1. Per-file coverage register

| File | Classification | Lines | Reviewed | Owner-voice regions → INT coverage | SHA-256 |
|------|---------------|-------|----------|-----------------------------------|---------|
| `0.txt` | Convo 1 (mixed): pasted "Arivo V4" architecture document + owner commentary + AI analysis | 1628 | full (2-pass: canonicalization + backfill-2) | `4` (INT-047) · `7–8` (INT-047/054/055, pasted-doc boundary noted §E-4) · `33–34` (INT-047/048) · `37` (INT-049..052, 062, 077–080, 090) · `800` (INT-081) · `1258` (INT-060) · `1323` (INT-081) | `139249210b45…e6edfea` |
| `1.txt` | Convo 2 (mixed): the full day of reasoning — owner Q&A + AI analysis + pasted doc repeats | 2063 | full (2-pass + targeted probes 2026-10-14) | `1–2` (INT-047/054) · `27` (INT-055) · `106` (INT-049..052, 062, 077–080, 090) · `280` (INT-081) · `437–451` (INT-056–059, 083–088) · `1368` (INT-060) · `1462` (INT-082) · `1911` (INT-081) · `1973–1985` (INT-019–030, 061, 086, 089) | `6a7b33774062…491af95` |
| `2.txt` | Convo 3 (mixed): architecture paste repeat + owner directives | 122 | full | `1–2` (INT-047/054) · `29` (INT-055: the Kev note) · `65` (INT-033/034) · `89` (INT-031/032) | `0ca484496f0b…4f73f` |
| `3.txt` | Owner turn 3 (the plan-mode corpus transfer): owner directives throughout, AI material interleaved | 239 | full | `5` (INT-035) · `13` (INT-036, owner-presented) · `15` (INT-037, owner-presented) · `207` (INT-042) · `230` (INT-044) · `233` (INT-043) · `235` (INT-040) · `237` (INT-041) · `239` (INT-039/045 + owner turn context) | `f24ff61d4769…151e24a` |
| `engineering transcript.txt` | Third-party engineering material (owner-supplied transcript). NO owner intent lives here. | 84 | full — **INCOMPLETE SOURCE: ends mid-sentence (F-11); captured excerpt, not a complete transcript** | none — excluded §X-1 | `dd133446a3e3…cdb446` |
| `upstream of engineering transcripts.txt` | Third-party upstream source of the engineering doctrine. NO owner intent here (the "I love writing / I never let agents write for me" passage is third-party — never misattributed). | 591 | full | none — excluded §X-1 | `29cf75295d2c…e2074` |
| `Arivo Agent Execution Specification.md` | AI-authored execution spec (Tier 0 rule families: LOOP/QST/STOP/KB/RED/PRF/RAT/WALL/UNS/MEM/FX/AFA/KER/BND/AUT/LAD). NOT owner words. | 718 | full (LAWS/EXECUTION provenance) | none — excluded §X-2 | `06c9f7a91628…e2646a` |

Full SHA-256 values (the register above is abbreviated; the verifier compares the full hash):

```
0.txt                                      139249210b458d23d909761c069db9db3dc855ce18633145419dc942ae6edfea
1.txt                                      6a7b337740620a08d28ea2f41313a74b3636aee8bd864b2bcd2e297dc491af95
2.txt                                      0ca484496f0bb0ea7b33476952ec498c65116362c2d252c52ad5a1bfc824f73f
3.txt                                      f24ff61d4769c6740090268a213e9fa5474f84958c78e1db63d60ede4515e24a
Arivo Agent Execution Specification.md     06c9f7a9162808ca9c032a3d2a9ea152390b557ec95b33cfce806927c5e2646a
engineering transcript.txt                 dd133446a3e3f84ed3ecdf5157779e1d261e3299b2594b9dcd5aadb1ebcdb446
upstream of engineering transcripts.txt    29cf75295d2c81169435489642c6788aab4346dab779fcc66218f3bee7202074
```

## 2. Non-raw owner-turn provenance (chat turns, 2026-10-13+)

| Turn | Date | Durable home(s) | INT coverage |
|------|------|-----------------|--------------|
| Owner turn 4 | 2026-10-13 | The ledger entry itself (first verbatim preservation — §E-2) | INT-046 |
| Owner turn 5 | 2026-10-13 | The ledger entry itself (§E-2) | INT-068 |
| Owner turn 6 | 2026-10-13 | `context/extracted/09-ARCHITECTURE-REVIEW.md` (quotes preserved verbatim) + ledger | INT-069–076 |
| Owner turn 7 | 2026-10-13 | `context/extracted/11-REVIEW-MERGE-AND-STATE-SLICE.md` §1 + ledger | INT-091 |
| Owner turn 8 | 2026-10-14 | `context/extracted/12-GAP-CLOSURE-AND-WALLS-STAGE-2.md` §1 + ledger | INT-092 |
| Reasoning-log session owner words | 2026-10-13 | `context/extracted/06-REASONING-LOG.md` | INT-053, 064–067 |

**Boundary, stated honestly:** owner words that arrived in chat before this control existed are verbatim-preserved where the ledger or a session record holds them; the raw corpus never received them. From turn 8 onward, the numbered session record's §1 is the required verbatim preservation home for every owner turn, BEFORE the ledger entry is written (OPERATING-MODEL §3 session-record requirement; this closes the INT-046/068 class — a quote whose only home is the ledger itself).

## 3. Exception register (validated deviations — checked by VER-803, never silent)

| ID | Class | Applies to | Reason |
|----|-------|-----------|--------|
| **E-1** | Elided excerpt (`...`) | INT-040, INT-045 | The ledger quote skips raw text between two verbatim segments of the same owner passage. Both fragments must match raw (the verifier enforces exactly this). |
| **E-2** | Chat-sourced quote | INT-046, INT-068, INT-069–076, INT-091, INT-092 | The owner's words arrived in chat, not in `context/raw/`. The durable home is the ledger entry + the named session record. Not mechanically validatable against raw — the session record's §1 quote is the cross-check. |
| **E-3** | Incomplete source capture | `engineering transcript.txt` | Ends mid-sentence (F-11). Kept as-is (AUT-02). Do not describe as complete. |
| **E-4** | Owner-presented (not owner-authored) | INT-036, INT-037, INT-054, INT-068 (forwarded-review portion) | Text the owner pasted/forwarded approvingly. Labeled "owner-presented" in the ledger per AUT-04; never treated as the owner's own words. |
| **E-5** | Inner-quote style normalization | INT-039 | The raw uses double quotes inside the sentence; the ledger renders them single. Fragments match after quote-style normalization (verifier normalizes `"`/`'`/curly variants on both sides). |
| **E-6** | Bracketed editorial gloss inside quote | INT-086 | `[answering: ...]` labels are ledger editorial, not owner text; the verifier strips bracketed segments before matching. |

## 4. Exclusion register (why non-quoted regions are not owner intent)

| ID | Region | Reason |
|----|--------|--------|
| **X-1** | `engineering transcript.txt`, `upstream of engineering transcripts.txt` (entire files) | Third-party engineering material supplied by the owner as DOCTRINE INPUT, not intent. Its content is derived into ENGINEERING.md (with provenance), never into the Intent Ledger. |
| **X-2** | `Arivo Agent Execution Specification.md` (entire file) | AI-authored spec (Tier 0 rule-family definitions). Rules derived from it live in LAWS/OPERATING-MODEL with citations; it is never owner intent. |
| **X-3** | The pasted "Arivo V4" architecture document body (bulk of `0.txt`, repeats in `1.txt`/`2.txt`) | A document the owner AUTHORED EARLIER and pasted as context. Owner commentary around it is ledgered (INT-047 etc.); the document's own text is treated as owner-presented material — only its lines the ledger explicitly quotes (INT-054, labeled) carry any status, and never as verbatim owner speech. |
| **X-4** | AI assistant analysis and proposals across `0.txt`/`1.txt`/`2.txt` (the bulk of all three) | Assistant material, not intent (D-022: raw is a MIXED archive). AI recommendations became decisions only through DECISIONS ADOPTED/PRESENTED-LOCKED entries, never through raw presence. |

## 5. Mechanical validation contract (what the verifier now checks)

- **VER-801 — manifest structure:** this file exists, carries all seven raw-file rows with classification, lines, reviewed range, INT coverage, SHA-256, and the required sections (§2 provenance, §E exceptions, §X exclusions).
- **VER-802 — raw immutability:** each raw file's current SHA-256 equals the anchored hash above. Any edit to `context/raw/` — even a whitespace change — fails the layer (AUT-02 at C3, was C6-prose).
- **VER-803 — quote fidelity:** every ledger entry that cites a raw source must have its quote fragments found in the cited file(s), after E-1/E-5/E-6 normalizations; entries with no raw citation must name a durable home (session record / reasoning log / chat-turn label per §2/E-2). A missing Source line fails (this caught the five real defects repaired 2026-10-14, §6).
- **VER-804 — STATE freshness:** `/STATE.md`'s last-completed session record must be the highest-numbered record in `context/extracted/` (staleness is caught, not remembered).

## 6. Provenance repairs executed under this control (2026-10-14, session 12)

| Repair | Before | After |
|--------|--------|-------|
| INT-035 Source line | missing entirely | `context/raw/3.txt:5` (located by search; quote matches) |
| INT-036 Source line | missing entirely | `context/raw/3.txt:13` (owner-presented; E-4) |
| INT-037 Source line | missing entirely | `context/raw/3.txt:15` (owner-presented; E-4) |
| INT-046 Source line | missing entirely | owner turn 4, chat — §E-2 (no earlier durable record; session-record rule now closes the class) |
| INT-068 Source line | missing entirely | owner turn 5, chat — §E-2 (same closure) |

Quote fidelity at repair time: 54/58 raw-citable quotes matched on first probe; the 4 deviations are exactly classes E-1/E-5 — no fabricated quote, no silent mismatch. After repairs: every ledger entry carries a Source line; every raw-citable quote validates mechanically.

## 7. Known limits (honest)

- Quote validation proves **fidelity to the raw corpus**, not the completeness of the corpus itself: an owner statement that never entered any captured source cannot be validated into existence (E-2 turns are cross-checked only against session records, not raw).
- The reviewed-range column is the record of human/agent multi-pass reading; a line-level proof that every owner-voice line was ledgered is impossible without an owner-voice oracle — the mapping above is the auditable claim (each INT cites its lines; each owner-voice region maps to INTs), and the burden shifts to the owner to flag anything missed (Question Record → ledger).
- SHA-256 anchors protect against **post-capture mutation**, not against the owner supplying already-incomplete material (E-3 stands).
