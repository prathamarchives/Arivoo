# SEV round-1 — CLAIM-063 / P4-00b (the client-contract freeze + the boundary test)

- **Agent label:** agent-7f3a91c4 (fresh-context Systems Engineering Verification, round 1)
- **Date:** 2026-11-06T03:52Z
- **Slice:** CLAIM-063 — P4-00b: the client-contract freeze + the boundary test
- **Base (origin/main):** `54533c6e18cb5ae00fdd3e584c41261a71419cde`
- **Head under review:** `3b0ed71709bc58b42ce330f8bdbaa707a8d3e731` (branch `slice/claim-063-p400b-contract-boundary`)
- **Commit chain reviewed:** d0667b4 (commit A: reconciliation + record 55) → 61762b8 (RED: test_boundary.py + gate registration) → 357a32f (red-01.txt) → 42c9441 (red-records.json binding) → 085b13e (GREEN: implementation + disclosed amendments + run records) → 3b0ed71 (scope widening BEFORE this SEV round)

---

## 1. What I ran (commands + exit codes)

| Command | Exit | Note |
|---|---|---|
| `python3 harness/tests/test_boundary.py` | 0 | BND-01..06 all PASS (18-ack census observed) |
| `python3 harness/tests/test_capture.py` | 0 | CAP-01..23 GREEN |
| `python3 harness/tests/test_export.py` | 0 | EXP-01..15 GREEN (incl. amended EXP-09) |
| `python3 harness/tests/test_contract.py` | 0 | CON-01..08 GREEN |
| `python3 harness/tests/test_keyword_index.py` | 0 | KWR-01..10 GREEN |
| `python3 harness/tests/test_note.py` | 0 | NTE-01..15 GREEN |
| `python3 harness/tests/test_bookmark.py` | 0 | BMK-01..13 GREEN |
| `python3 harness/tests/test_highlight.py` | 0 | HLG-01..12 GREEN |
| `python3 harness/tests/test_anchor.py` | 0 | ANC-01..10 GREEN |
| `make verify` | 0 | full set: all suites + gate (main-selfcheck mode) + canonical layer 54/0 |
| `python3 harness/gate.py --slice claim-063-p400b-contract-boundary --diff origin/main --skip-suites` | 1 | refuses on exactly ARV-PRF-004 + ARV-SEV-001 (the two expected pre-finalize codes — commit 3b0ed71's claim verified) |
| RED reproduction: `git archive 61762b8` → temp tree → `python3 harness/tests/test_boundary.py` | 1 | `FAIL ARV-TEST-000 ... the write ack's api_version token: 'ACK command=record_event ... result_ref=...'` — the RED is real at the RED commit, reproduced live |
| ~35 adversarial CLI probes on my own scratch DB (`arv_sev_28057_936254377`, migrated, dropped after) | see §5 | all at the REAL boundary (commands.py / extract.py / query.py CLIs) |
| `git show <commit>:<file> \| sha256sum` digest-chain checks | — | see §4/F-numbers |

No repository source file was modified; nothing committed or pushed; the scratch DB and all temp files were removed (verified: no `arv_sev*`/`p400b*` databases remain).

---

## 2. Findings

### F1 — P1 — BND-04's "absent == cross-owner, byte-identical" pin is vacuous as written (absent-vs-absent only)
- **Severity:** P1 — a pin that does not actually pin what it says (the SEV scale's own letter).
- **Location:** `harness/tests/test_boundary.py:305-323` (the ARV-QRY-001 arm of BND-04); claim text at `:331-332` ("absent == cross-owner, byte-identical refusals — no existence oracle") and the suite docstring `:31-32`.
- **Reproduction / evidence:**
  - The code probes `r_abs_A = get-capture --owner A --id <random uuid>` and `r_abs_B = get-capture --owner B --id <same random uuid>` — an id that exists in NO owner's scope. `r_abs_A.stdout == r_abs_B.stdout` therefore compares two *absent* refusals. **No read of an id that EXISTS under another owner occurs anywhere in test_boundary.py.**
  - Repo-wide grep: the only byte-level absent-vs-cross-owner pin anywhere is ANC-08 (test_anchor.py:398-403, resolve-anchor arm, with id normalization). The get-capture/get-note/get-bookmark arms are pinned only at code-presence level (test_capture.py:261 `cross.returncode != 0 and "ARV-QRY-001" in ...`; test_note.py:381-382; test_bookmark.py:400-401). A regression that made a cross-owner get-* refusal say e.g. `FAIL ARV-QRY-001: object (X) belongs to another owner` would pass every suite in the repo today.
  - **The live law HOLDS** — my probe: B reading A's real note vs B reading an absent id → exit 1 both, `cross.stdout.replace(A_NOTE, ABSENT) == absent.stdout` → True; stderr byte-equal; same for get-capture. So this is a suite/pin defect, not a product defect.
- **Disposition:** repair-in-slice RED-first — add to BND-04 a cross-owner probe of a REAL id (e.g. owner B reads A's `hl1`) and assert normalized byte-equality with the absent refusal, mirroring ANC-08's own form. Small, suite-only; the machinery already behaves correctly.

### F2 — P2 — the ack census is narrower than the "full verb census" claim; the `>= 14` floor admits silent verb breakage
- **Severity:** P2 — real but bounded (live behavior verified compliant on every verb; the gap is pin strength, with the risk routed to future drift).
- **Location:** `harness/tests/test_boundary.py:15-17` (docstring: "commands.py's full verb census"), `:252` (`len(ACKS) >= 14`), `:232-242` (BND-02's replayed set).
- **Evidence:**
  - commands.py exposes 15 verbs (+ extract_source = 16 client write surfaces). The census walks 10 commands.py verbs + extract_source. **Never walked: `revise_highlight`, `move_bookmark`, `tombstone_bookmark`, `restore_bookmark`, `restore_highlight`.** I probed all five live: every committed ack carries `durability_rung=local_durable` + `api_version=1` (they share the spine's single print site, so the contract holds mechanically — but the freeze suite does not pin them, and import_source/extract_source demonstrate the precedent of verbs with their OWN ack print sites).
  - BND-02's replayed census includes only `create_highlight` among the three capture families; create_note/create_bookmark replayed forms are unpinned by BND (verified live by me: both carry rung+version).
  - **Vacuous-pass demonstration:** with 18 acks observed vs the `>= 14` floor, a regression that silently breaks a walked verb (FAIL + exit 1, no ACK line) leaves BND-01/02/03 green as long as ≥14 lines remain. Concrete case: `restore_note` completely broken → census 17, BND-01..06 ALL still pass (nothing in BND checks nt-2's restored state; BND-06 checks n1's *revised* content, which revise_note — a different verb — provides). The repo-level safety net is the NTE suite, not the boundary suite whose purpose is this freeze.
- **Disposition:** route-to-slice or repair-in-slice — widen the fixture to walk every verb (incl. the five unwalked + a note/bookmark replay), and/or assert per-verb returncode==0 so a vanishing ack fails loudly. If not in-slice, route to P4-00c with the routing recorded; at minimum correct the docstring's "full verb census" wording.

### F3 — P3 — a non-integer `--limit` refuses with argparse exit 2, not the frozen ARV-QRY-004 exit-1 shape
- **Severity:** P3 — fail-closed, zero effect, distinguishable; but off the frozen refusal shape for a degenerate input class.
- **Location:** `harness/query.py:441` (`--limit` declared `type=int`) vs `:273-276` (`_list_arm`'s own `int()` refusal branch — dead code from the CLI, since argparse pre-converts or refuses).
- **Reproduction:** `python3 harness/query.py list-notes --owner P --limit abc` → exit 2, argparse usage on stderr (`error: argument --limit: invalid int value: 'abc'`), no `FAIL ARV-QRY-004:` line. Same for `1e3`. Integer out-of-bounds forms are correct: `--limit 0 / -5 / 1001` → `FAIL ARV-QRY-004:` exit 1 (verified).
- **Disposition:** repair-in-slice (one line: drop `type=int` so the value reaches `_list_arm`'s typed refusal) or accept-with-note. BND-04 pins 0/1001/non-uuid-cursor only — widening the pin to the non-integer form would ride the same repair.

### F4 — P3 — red-records.json: the test_export.py amendment NOTE is a copy-paste of the capture amendment (names CAP-09, not EXP-09)
- **Severity:** P3 — record/prose drift in the evidence chain; the digests themselves chain correctly.
- **Location:** `harness/red-records.json` (the CLAIM-063 amendment appended to the `harness/tests/test_export.py` record, `observed_at 2026-11-06T03:06:41.569362+00:00`).
- **Evidence:** the note reads "CAP-09's empty-listing expectation widened to admit the P4-00b truthful empty answer..." — that describes the test_capture.py amendment. The actual export amendment (test_export.py:414-427) is EXP-09's versioned search header (`_hdr = "# api_version=1 kind|entity_id|revision|matched_terms"`). Digest chain verified: test_export.py `origin/main` = `6711140e...` == the amendment's `prior_sha256`; HEAD = `c0b89f98...` == `new_sha256` (same for test_capture.py: `af7683c4...` → `475a31d3...`).
- **Disposition:** repair-in-slice (JSON prose-only edit; records are evidence, so the note should name what actually changed).

### F5 — P3 — README.md (the user-facing entry) now lags the frozen contract it documents
- **Severity:** P3 — docs drift; README.md is deliberately outside this claim's scope (scope.txt), so this is a routed gap, not a scope violation.
- **Location:** `README.md:69` (stale search header example `#    # kind|entity_id|revision|matched_terms` — the real header is now `# api_version=1 kind|...`); README has no mention of `api_version` on acks/bodies, the list `--limit/--after` contract, or the `# api_version=1` / `# more=true|false` markers.
- **Evidence:** live `search` first line: `# api_version=1 kind|entity_id|revision|matched_terms`. The line-47 ACK example is elided ("ACK ...") so it is not strictly wrong, but the header example is now byte-stale, and the day-one path's list/search outputs changed user-visibly with no doc update.
- **Disposition:** route-to-slice (P4-00c capability-matrix card or a disclosed docs touch under the F1-repair precedent — scope widening BEFORE the next SEV round).

### F6 — P3 — test_boundary.py's disclosed exclusion cites a notverified.txt that does not exist at this head
- **Severity:** P3 — promissory reference; the artifact is scheduled for the finalize (the gate currently refuses only on ARV-PRF-004 + ARV-SEV-001, verified live).
- **Location:** `harness/tests/test_boundary.py:48-50` ("export.py's RESTORED line and migrate.py's operator output are NOT the client API — their version field is a later slice's call, disclosed in notverified.txt") vs the runs dir contents (scope.txt, red-01.txt, run-01..05.json only).
- **Evidence:** `harness/proofsheet.py:192-198` reads `notverified.txt` from the runs dir and defaults to empty when absent — so a finalize that forgets the file would silently assemble a sheet with no not-verified lines while the permanent suite's docstring cites it.
- **Disposition:** accept-with-note + binding next-action for the finalize: the notverified.txt MUST land carrying (at minimum) the export.py/migrate.py version-field exclusion the suite's docstring names, plus the honest limits below.

### F7 — P3 — byte-form notes on the frozen surface (accept-with-note)
- (a) History rows and get-* bodies are now re-serialized through Python `json.dumps` with default separators — `{"id": "…", "kind": "revision", …, "api_version": 1}` — a visible byte-form change from PostgreSQL's compact `row_to_json` form (`{"id":"…"}`). No in-repo consumer pinned the compact form (verified: all suites `json.loads`; export.py/sync.py read the DB directly, never the CLI stdout), and the slice's claim is carefully worded ("the SQL byte-identical, the framing law preserved") — both true. But future clients must not assume compact JSON; worth one line in the capability matrix (P4-00c).
- (b) `api_version` key placement is inconsistent: FIRST key in get-bookmark's body (query.py:397 literal dict) vs LAST key everywhere else (`_versioned` appends). Valid JSON either way; the frozen contract says "carries", not "where". Polish.
- (c) The CAP-09 amendment's widened empty-listing acceptance (`test_capture.py:262-269`) admits ANY all-comment output (`# more=false` present + every non-empty line starts with `#`) — mildly looser than the old empty/`0 rows` pin (retained as a branch). Disclosed, substance (B sees nothing of A's) retained; comment lines cannot carry ids in the current grammar.
- **Disposition:** accept-with-note; fold (a)/(b) into P4-00c's matrix.

### F8 — P3 — suite hygiene
- `test_boundary.py:182` `tempfile.mkdtemp(prefix="arv-blobs-")` is never cleaned — one leaked temp dir per run (bounded, /tmp).
- Commits 357a32f and 42c9441 carry byte-identical commit messages (the red-01.txt write and the red-records write were split) — cosmetic history noise only; both verified to contain exactly what they claim.
- **Disposition:** accept-with-note / polish.

---

## 3. What genuinely holds (verified, not taken on trust)

1. **RED-first (LAW-11) verified live:** the suite at the RED commit 61762b8 (extracted via `git archive`, run against a fresh scratch DB) exits 1 with `ARV-TEST-000`, quoting the version-less record_event ack — exactly red-01.txt's content. RED precedes GREEN in history; the GREEN (085b13e) contains the implementation. The suite is registered in gate.py's TESTS at the RED commit (the ARV-RED-008 class handled).
2. **Digest chains all verify:** test_boundary.py binding: `git show 357a32f:…` = `git show 61762b8:…` = HEAD = `c66461757ec0dbb4…` == the record's `binding_sha256` == `current_sha256` (no amendments — the suite is unchanged since the RED). test_capture.py: origin/main `af7683c4…` == amendment prior → HEAD `475a31d3…` == new. test_export.py: origin/main `6711140e…` → HEAD `c0b89f98…`. Both amendments chain from the trusted baseline.
3. **The F3 closure is real on every path:** committed, replayed, AND crash-path replayed acks carry `durability_rung=local_durable` + `api_version=1` for import_source, extract_source, record_event, and all three capture families — including the five verbs the suite never walks (F2) and the crash-path replay (`crash.py --point post-commit-pre-ack` → retry answers `status=replayed … durability_rung=local_durable api_version=1`). All six ACK print sites in the repo carry both tokens.
4. **The version field is on every surface I could reach:** all 16 write surfaces; get-capture/get-source/get-note/get-bookmark/resolve-anchor bodies; every history row; the search header; the three list headers. JSON parses; prior keys intact; `api_version: 1` exactly.
5. **The framing law holds under the injection:** a note whose content carries a literal newline + U+2028 + U+2029 round-trips byte-exact, ONE stdout line for the body, one line per history row, U+2028/U+2029 raw (not escaped), newline escaped. (Also independently pinned by NTE and ANC-10.)
6. **The list contract holds live:** 7-note keyset walk with `--limit 2` — monotone, no dups, no skips, union == full; `more=true/false` OBSERVED (limit+1 fetch) and truthful vs the actual row count at every page boundary; `--after` the last id and a beyond-all uuid both answer header + `more=false` alone; empty owner (and empty DB) answer exactly `# api_version=1` + `# more=false`; `--limit 1/1000` accepted at the bounds; `--limit 0/-5/1001` refuse typed; a SQL-injection attempt through `--after` is refused typed (uuid validation); a non-canonical uuid spelling (no dashes) is accepted and normalized; **a cross-family cursor (a source id passed to `list-notes --after`) pages honestly by keyset** — safe: owner scoping intact, no leak, deterministic position semantics; the refusal text's "same family" is advisory, not enforced (judged acceptable for an opaque keyset cursor, noted in F7).
7. **SYS-01 honesty:** after a committed ack claiming `local_durable`, the row is readable by a fresh process through arv_read; the crash-path replay's claim is backed by the committed command_log row; no surface claims a rung above `local_durable` (no `queued`/`server_durable` claims exist on any client-facing path here).
8. **The typed-error surface:** ARV-CMD-409 (zero effect verified by counts), ARV-CAP-006/007, ARV-NTE-006, ARV-QRY-003 (tombstoned note read refuses; the governed history still answers with the version key) — each exit 1 + `FAIL <code>:` prefix. ARV-QRY-001 absent-vs-absent byte-identity holds; the cross-owner half see F1 (live law TRUE, pin vacuous).
9. **Consumers:** sync.py's `_outcome` parses `result_ref=`/`FAIL ` tokens — unaffected by the appended `api_version=` token (value parsing is whitespace-delimited). export.py reads the DB directly, never CLI stdout. KWR/EXP/CON header-skip forms intact (suites green). The only lagging consumer is README.md (F5).
10. **LAW-05 budget:** source files 4 (commands.py, extract.py, query.py, gate.py) ≤ 8; source lines 133 insertions / 183 changed ≤ 400; test files 3 ≤ 6; test lines 481 insertions ≤ 800; migrations 0 ≤ 1. PASS (the gate's SIZE check also green).
11. **Scope honesty:** all 21 diff paths are declared in scope.txt after the disclosed pre-SEV widening (commit 3b0ed71, the F1-repair precedent followed — both homes updated BEFORE the round); nothing smuggled; the PR-mode gate's scope/claims/red-record/known-bad checks all pass, refusing only on the two expected pre-finalize artifact codes.

---

## 4. Vacuous-pass hunt (the required ≥3 constructions)

1. **BND-04's no-oracle pin — CONFIRMED vacuous as written** (F1): both ARV-QRY-001 probes use a globally-absent id; no cross-owner read of an existing id exists in the suite; no other suite pins the get-* arms byte-level (ANC-08 covers resolve-anchor only). The suite would stay green if cross-owner refusals leaked existence language on every get-* arm.
2. **The census floor — CONFIRMED:** `len(ACKS) >= 14` vs 18 observed, and no per-verb returncode assertion: `restore_note` silently broken (FAIL, exit 1, no ACK) leaves BND-01..06 all green (only the NTE suite would catch it). Similarly the five unwalked verbs (F2) have zero BND coverage — a future verb with its own ack print site (the import_source precedent) could omit `api_version` and the freeze suite would not notice.
3. **BND-06's `body()`/`rows()` helpers — CONFIRMED (BND-local):** `body()` json-parses only the FIRST non-empty stdout line and `rows()` skips `#` lines, so a framing break that emitted extra lines after a get-* body would not fail BND-06 (the first line still parses with `api_version`). Partially mitigated repo-level: NTE pins `len(lines) != 1` for get-note (test_note.py:239) and ANC-10 for the resolver/passage rows — but get-capture/get-bookmark one-line output is not pinned anywhere.
4. (Bonus) **BND-05's `--after ""` degenerate:** if a page ever returned zero ids, the suite's next `--after ""` would be refused typed (ARV-QRY-004) and the walk check would fail — this one is NOT vacuous; it fails honestly. The pagination pins (`d_ids == full[:100]`, `p1 == full[:50]`, union == full, no-set-overlap) are strong and observed.

---

## 5. Probe log (every probe + observed result)

| # | Probe (all on my scratch DB, at the real CLIs) | Result |
|---|---|---|
| 1 | import_source committed ack | `status=committed … work_id=… durability_rung=local_durable api_version=1`, exit 0 |
| 2 | import_source replay (same key+body) | `status=replayed … durability_rung=local_durable api_version=1`, exit 0 |
| 3 | record_event committed + replay | both carry rung + api_version, same result_ref |
| 4 | extract_source committed + replay | committed: `source_id=… durability_rung=local_durable api_version=1`; replayed: `state=current …` + both tokens |
| 5 | create_highlight / create_bookmark / create_note committed + replayed | all six acks carry rung + api_version (the note/bookmark replayed forms the census misses — compliant) |
| 6 | revise_highlight, move_bookmark, tombstone_bookmark, restore_bookmark, tombstone_highlight, restore_highlight, tombstone_note, restore_note, revise_note committed acks | every one carries `durability_rung=local_durable` + `api_version=1` (the five census-unwalked verbs verified live) |
| 7 | crash-path: create_note killed post-commit-pre-ack, then same-key retry | exit 2, no ack; retry: `status=replayed … durability_rung=local_durable api_version=1` |
| 8 | SYS-01 read-back after the crash-path ack | fresh arv_read process sees the committed row (1 row, content intact) |
| 9 | list-notes full walk (limit 1000, 7 notes) | 7 ids, sorted, unique, `more=false`, header `# api_version=1` |
| 10 | pages with `--limit 2` + `--after` (3 pages) | monotone keyset, no dups, no skips, union == full, `more` truthful at each boundary |
| 11 | `--after` the LAST id / a beyond-all uuid (ffffffff-…) | header + `more=false`, zero ids |
| 12 | `--limit 0` / `-5` / `1001` | `FAIL ARV-QRY-004:` exit 1, typed |
| 13 | `--limit abc` / `1e3` | argparse exit 2 + usage (F3 — not the typed shape) |
| 14 | `--limit 1` / `1000` | accepted at both bounds |
| 15 | `--after not-a-uuid` / `--after ""` | `FAIL ARV-QRY-004:` exit 1 |
| 16 | `--after <source id>` on list-notes (cross-family) | pages by keyset from that position (all 7 notes), exit 0 — honest opaque-cursor behavior, no leak (F7 note) |
| 17 | `--after` non-canonical uuid (no dashes) | accepted, normalized, pages correctly |
| 18 | `--after "00000000-…'); DROP TABLE arv.note;--"` | typed ARV-QRY-004 refusal (uuid validation blocks injection) |
| 19 | empty owner Z: list-notes / list-captures / list-bookmarks | exactly `# api_version=1` + `# more=false`, exit 0 |
| 20 | note with literal newline + U+2028 + U+2029 | get-note ONE line, round-trip byte-exact, api_version present, prior keys intact; history rows one-per-line, U+2028/U+2029 raw, newline escaped, all carry api_version |
| 21 | get-capture / get-source / get-bookmark bodies | api_version:1, prior keys intact, exit 0 |
| 22 | resolve-anchor (resolved anchor) | `state=resolved`, api_version:1, ONE line |
| 23 | search | first line `# api_version=1 kind|entity_id|revision|matched_terms` |
| 24 | cross-owner no-oracle: B reads A's real note/capture vs B reads absent id | exit 1 both; stdout byte-equal after id normalization; stderr byte-equal — the LAW HOLDS live (F1 is the pin, not the behavior) |
| 25 | ARV-CMD-409: create_highlight same key different body | typed refusal exit 1; note count unchanged (11→11); no new highlight row (command_log count for the verb unchanged) |
| 26 | ARV-CAP-006 (missing work), CAP-007 (title+work-id), NTE-006 (bogus ref kind) | each typed `FAIL <code>:` exit 1 |
| 27 | ARV-QRY-003: tombstoned note read | typed refusal exit 1; get-note-history still answers (governed) with api_version on every row |
| 28 | RED reproduction at 61762b8 | exit 1, `ARV-TEST-000`, the version-less record_event ack quoted |
| 29 | make verify (full) | exit 0 — all suites + gate selfcheck + canonical 54/0 |
| 30 | PR-mode gate | exit 1 on exactly ARV-PRF-004 + ARV-SEV-001 (the disclosed pre-finalize artifacts) |
| 31 | digest-chain verification (6 file/commit pairs) | all match (§3.2) |
| 32 | scratch DB teardown | dropped; no residual databases |

---

## 6. Verdict

Zero P0. One open P1 (F1 — the boundary suite's own no-oracle pin is vacuous as written; the live law holds, verified). One P2 (F2 — census coverage vs the "full verb census" claim). Six P3s (F3-F8).

**DISPOSITION: BLOCKED** (one open P1: F1; recommended repair is suite-only and small — add the cross-owner probe with ANC-08-style normalization, RED-first, then re-run this round. F2 should be dispositioned in the same repair or explicitly routed with the routing recorded; F4 is a one-line record fix worth riding the same commit.)

### Next actions (for the builder)
1. F1: repair-in-slice RED-first — the BND-04 cross-owner probe (owner B reads A's real capture; normalized byte-equality with the absent refusal; also cover a get-note or get-bookmark arm if cheap).
2. F2: widen the census to all 16 write surfaces (or, at minimum, add per-verb returncode assertions and fix the "full verb census" docstring) — else route to P4-00c with the routing recorded in notverified.txt.
3. F4: correct the test_export.py amendment note (EXP-09, not CAP-09).
4. F6: the finalize's notverified.txt MUST land carrying the export.py/migrate.py version-field exclusion named by test_boundary.py:48-50, the F2 routing (if routed), the cross-family `--after` advisory wording, and the json-separator byte-form note (F7a).
5. F3/F5/F7/F8: repair or route per the dispositions above.
