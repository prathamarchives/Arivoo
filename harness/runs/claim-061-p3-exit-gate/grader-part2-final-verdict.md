# GRADER REPORT — Part 2 (FINAL verdict), Phase 3 exit gate, Arivo

- **Grader:** independent part-2 grader (acceptance grade + final verdict; no stake in the outcome; adversarial stance — every claim was pushed toward FAIL before being accepted).
- **Graded tree:** `/home/z/my-project/verification/acceptance-clone` @ `3b5ed28` ("Merge pull request #94 … slice/claim-060-p309-export-restore"), clean checkout confirmed (`git log` verified).
- **Date:** 2026-11-05/06 (grader wall clock).
- **Environment:** PostgreSQL 17.11 at `127.0.0.1:5433` (user `postgres`, trust). My OWN scratch databases `arv_grader2` (primary), `arv_grader2b` (restore destination), `arv_grader2c` (crash-restore destination) — each created and migrated by me (`python3 harness/migrate.py` → 13/13 applied, `--verify` → "verify OK: 13 migration(s) applied, checksums match"). My own blob dir (`ARV_BLOB_DIR=…/grader2/blobs`, empty at start). I did NOT touch `arv_acceptance`/`arv_acceptance_2` (read-only count checks only) or `arv_grader` (never connected). I did not re-run `make verify` (part 1 already ran it green; its raw logs spot-verified by me: `make-verify-exit.txt` = `MAKE_VERIFY_EXIT=0`, `suite-results.txt` all rc=0, gate line "GREEN — the gate passes … canonical layer: 54 checks, 0 failures").
- **Inputs read in full:** `MATRIX-WALK.md` (part 1), `ACCEPTANCE-REPORT.md` (the uncoached run), `PLAN.md` §3.E (lines 353–366), `RTM.md` §1/§3.7/§4, `context/extracted/50-P307-KEYWORD-INDEX.md`, `harness/export.py`, `harness/commands.py` (index paths), `harness/query.py` (search SQL).

---

## 1. Acceptance coverage (required vs covered)

The exit criteria are PLAN.md §3.E lines 356–366 (read by me directly). The **required acceptance path** per §3.E line 357 plus the user-facing durability/restore lines (358–363) that a "real user-like acceptance path" must exercise:

| # | Exit criterion (PLAN §3.E) | Acceptance run (ACCEPTANCE-REPORT.md) | Part-1 matrix walk | My independent probe |
|---|---|---|---|---|
| 1 | Work/Source identity + Anchor contracts explicit; owner blockers isolated at exact scopes | Step 1–2: digest round-trip (`f9d2ea52…` = file sha256), `source_version: 1`, highlight read-back with derived selected_text + context; anchor evidenced via bookmark `resolved` | SYS-05 PASS (ANC-01..10, HLG-07/08, CAP-03/04/22); Q11/Q12 isolated (PLAN standing-open) | Anchor row verified in DB: `digest_match=true start=328 end=449` |
| 2 | **Real client/backend path: ingest → Highlight with valid Anchor, Bookmark, Note → keyword search** | **COVERED** — Steps 1–3: import → extract/index → highlight → bookmark → note(+ref) → `search` finds note+source+highlight; lists exactly one each | SYS-09 PASS (real-boundary checkpoint CAP-01..10) | **Reproduced end-to-end** (Probe A): `search treachery` → `highlight\|…`, `note\|…`, `source\|…` |
| 3 | Crash/restart/replay/offline matrices; zero lost committed writes; no duplicate logical effects | Step 4 (fresh-shell reopen: `diff -r` IDENTICAL — I re-verified the artifacts), Step 6a (replay), 6b (ARV-CMD-409) | SYS-01/04/06/08 suites PASS | Probe B (replays, zero-duplicate counts) + crash-restore probe (exit 137 → 0 authoritative rows → retry converges) |
| 4 | Local-durable ≠ server-durable; explicit recoverable outbox states | Step 3: `SYNC-STATUS pending=5` → sync → `acknowledged=5`, same server refs | SYS-08 PASS (SYN-01..19) | Probe E: `pending=4` → 4× `SYNC … state=acknowledged server_ref=<same ids>` → `acknowledged=4`; destination still 1/1/1/1 rows |
| 5 | Every write attributed + owner-scoped; two-owner tests + independent reads | Step 6f: cross-owner note-by-id = same refusal as nonexistent; search/list empty | SYS-03 PASS (CAP-09/10/11/20, EXT-12, KWR-02, EXP-10) | **Probe D — ALL TWELVE read surfaces** (get-source/capture/bookmark/note, get-history, get-note-history, resolve-anchor ×2 ids, search ×2, all three lists) + cross-owner EXPORT: byte-identical refusals, empty lists, `rows=0` export |
| 6 | Revisions immutable; tombstones work; governed purge effective after restore | Note revision exercised (both revisions via `get-note-history`); tombstone/purge NOT walked by the agent (no owner-facing purge command exists — documented deferral; the report says so honestly) | SYS-02/10 PASS (HLG-01/02/06; EXP-07/10..15 purge permanence + ledger append-only) | — (suite-covered; see §3 note) |
| 7 | Derived passages/indexes rebuildable; stale derivations never silently current | Step 5: rebuild on destination restored search + bookmark resolution | SYS-07 PASS (KWR-03/04/05/07/10, EXP-09) | Probe C: rebuild → search byte-identical to source; bookmark `resolved` with fresh derived ids |
| 8 | Export/restore satisfies documented equality contract | Step 5: `state_hash` match, all authoritative reads identical; two derived diffs named | SYS-10 PASS (EXP-01..15) | **Probe C — full reproduction on my own data** (see §2) |
| 9 | Every SYS traces to tests + Proof Sheets; SEV per slice; known-bads refused with named codes | (not the acceptance remit) | **All 11 SYS rows PASS; 13/13 slice evidence (proofsheet + sev.json disposition=PASS); 32/32 KB PASS** | Part-1 raw logs spot-verified |
| 10 | Local checks + three recorded CI checks at final revision; uncoached agent completes the path; separate grader passes with no P0/P1 | The uncoached run = ACCEPTANCE-REPORT.md | `make verify` exit 0 (gate GREEN, canonical 54/0); claim-060 proofsheet carries 3× make verify + recorded PR-mode gate exit 0 + the five GitHub checks at the head | **This report is the separate grader — verdict below** |
| 11 | Not-verified items explicit | Report's own verdict names the gaps (no read surface, no purge flow, pagination) | RTM §7 names Q6–Q12; SEV reports carry `not_verified` lists | — |

**Anything required but not covered?** No. The one line the acceptance agent did not personally walk — tombstones and governed purge (row 6) — has no owner-facing purge surface in Phase 3 (the ledger mechanism + reconciliation is the Phase-3 deliverable, owned by P3-06/P3-09 per the repo's own bounded-exclusion notes and D-011; the owner-facing flow is later-phase), and its proof requirement ("a governed purge remains effective after restore") is suite-covered (EXP-07/10..15, independently run green by part 1). The required acceptance path itself (row 2 + restart/recovery + export/restore equality + truthful durability states) is fully covered by the report AND reproduced by me.

---

## 2. My independent re-runs (all against my own `arv_grader2*` databases, my own blob store)

Env for every command: `PATH=…/pgbuild/root/… PGHOST=127.0.0.1 PGPORT=5433 PGUSER=postgres PGDATABASE=arv_grader2 ARV_BLOB_DIR=…/grader2/blobs`, run from the graded tree. My own 726-char ASCII essay (`grader-essay.md`, sha256 `37c3ca87…`) with distinctive terms (*harbormaster, treachery, tides, Nadia, quokka-free*).

### Probe A — the full user path (exit criterion line 357)

```
$ python3 harness/commands.py import_source --owner grader2 --client-id grader2-cli \
    --idem-key g2-import-001 --title "The Harbor Master's Ledger" \
    --file …/grader-essay.md --media-type text/markdown --acquired-via local-file
ACK command=import_source idem_key=g2-import-001 status=committed result_ref=01a1ad19-94c2-7949-ad06-1b539019b26f work_id=01a1ad19-94c2-7b6e-8642-cd8f05c3f137
$ python3 harness/extract.py --owner grader2 … --idem-key g2-extract-001 --source-id 01a1ad19-94c2-…
ACK command=extract_source … status=committed …
$ python3 harness/commands.py rebuild_keyword_index --owner grader2 … --idem-key g2-kwi-002
ACK command=rebuild_keyword_index … status=committed … index=rebuilt durability_rung=local_durable
$ python3 harness/commands.py create_highlight … --start 328 --end 449
ACK command=create_highlight idem_key=g2-hl-001 status=committed result_ref=01a1ad1a-0332-7312-acf1-91bb33f91e5e revision=1 durability_rung=local_durable
$ python3 harness/commands.py create_bookmark … --start 630 --end 688
ACK command=create_bookmark idem_key=g2-bmk-001 status=committed result_ref=01a1ad1a-037a-7043-a96c-d44c3e0faee5 revision=1 durability_rung=local_durable
$ python3 harness/commands.py create_note … --idem-key g2-note-001 --content-file …/grader-note.md \
    --ref highlight:01a1ad1a-0332-7312-acf1-91bb33f91e5e@1
ACK command=create_note idem_key=g2-note-001 status=committed result_ref=01a1ad1a-3d53-720e-90be-cb13d57e1be1 revision=1 durability_rung=local_durable
```

Read-backs: `get-source` digest = my file's sha256 exactly, `import_state: complete`, `source_version: 1`; `get-capture` selected_text = **exactly** my intended 121-char span with correct context; `get-bookmark` → `state: "resolved"` with anchor/generation/passage ids; `get-note` round-tripped the content losslessly (em-dashes, newlines, quotes) with `"refs":[{"kind":"highlight","id":"01a1ad1a-0332-…","revision":1}]`. Anchor validity in the DB (read-only, `arv_read`): `hl_anchor=01a1ad1a-0332-7533-9fd7-8bcc509d0fdc digest_match=true start=328 end=449` — the anchor is tied to the source version by digest.

```
$ python3 harness/query.py search --owner grader2 treachery
highlight|01a1ad1a-0332-7312-acf1-91bb33f91e5e|1|1
note|01a1ad1a-3d53-720e-90be-cb13d57e1be1|1|1
source|01a1ad19-94c2-7949-ad06-1b539019b26f|1|1
$ search harbormaster → note + source;  $ search herring → source only;  $ search zxqvubble → empty, exit 0
$ list-captures / list-bookmarks / list-notes → exactly my one id each
```

**Finding all three entities via keyword search: CONFIRMED on my own data.** The exit-criteria user path holds end-to-end through the real boundary.

### Probe B — idempotent replay (exactly-once)

```
$ <exact same create_note command, third run>
ACK command=create_note idem_key=g2-note-001 status=replayed result_ref=01a1ad1a-3d53-720e-90be-cb13d57e1be1     (same result_ref)
$ <exact same import_source command>
ACK command=import_source idem_key=g2-import-001 status=replayed result_ref=01a1ad19-94c2-… work_id=01a1ad19-94c2-…
$ <same key, DIFFERENT body>
FAIL ARV-CMD-409: idempotency key 'g2-note-001' is already recorded with a DIFFERENT body (no silent overwrite — exactly-once is a contract, not a preference)   (exit 1)
```

Row counts after the replays (read-only): `sources=1 highlights=1 bookmarks=1 notes=1`, `command_log` rows for the note key = **1**. **Zero duplicate logical effect: CONFIRMED.**

### Probe C — export/restore equality + the restore-derived-state P2

```
$ python3 harness/export.py export --owner grader2 --out …/g2-export-001
EXPORTED owner=grader2 dir=… tables=13 rows=18 state_hash=fbe580edfe133bd5
$ PGDATABASE=arv_grader2b python3 harness/migrate.py        (13 applied)
$ PGDATABASE=arv_grader2b python3 harness/export.py restore --archive …/g2-export-001
RESTORED owner=grader2 ledger_as_of=empty backup_expiry=the D-029 documented window bounds this archive's resurrection exposure tables=13 rows=18 state_hash_match=true
```

Diffing all nine read surfaces source-vs-destination (snap-source.txt vs snap-restored-before-rebuild.txt), the ONLY differences:
1. `get-bookmark`: original `state: "resolved"` (generation/passage ids) → restored `"state": "unresolved", "cause": "no-current-generation", "evidence_hits": 0` — honest and typed.
2. Both searches → **completely empty** on the restored DB.

Everything else — source metadata+digest, highlight selected_text/contexts/offsets, note content+refs, all three lists — **byte-identical**. Then, on the destination:

```
$ python3 harness/extract.py … && python3 harness/commands.py rebuild_keyword_index …
→ search treachery / harbormaster now BYTE-IDENTICAL to the source DB; get-bookmark back to
  "resolved" with NEW derived generation/passage ids (expected: derived state is disposable, SYS-07)
```

**Content equality: CONFIRMED. The report's derived-state P2 (search silently empty + bookmark honestly unresolved until rebuild, with no mention of the rebuild step in the restore ack): REPRODUCED EXACTLY, verbatim ack captured above.**

### Probe D — cross-owner privacy through EVERY read surface (walking beyond the report)

As `--owner intruder` against my populated `arv_grader2`: `get-source`, `get-capture`, `get-bookmark`, `get-note`, `get-history`, `get-note-history`, `resolve-anchor` — each by my exact id AND by a nonexistent id — every single one returns the byte-identical refusal:

```
FAIL ARV-QRY-001: no such object (<id>) in the caller's scope — absent and another owner's are the SAME refusal, never a side channel
```

`search treachery` / `search harbormaster` → empty (exit 0); `list-captures`/`list-bookmarks`/`list-notes` → empty; and the write-adjacent read surface `export.py export --owner intruder` → `EXPORTED owner=intruder … tables=13 rows=0` (RLS holds on the export path too). **A second owner sees nothing of the first owner's data on any surface I could reach; no existence oracle anywhere. No new finding.**

### Probe E — sync (distinct durability rungs, no duplicates)

```
$ python3 harness/sync.py status --owner grader2
SYNC-STATUS owner=grader2 pending=4
SYNC-QUEUED g2-import-001 state=pending attempts=0   (×4 — the derived extract/index correctly absent)
$ python3 harness/sync.py sync --owner grader2 --server-db arv_grader2b
SYNC key=g2-import-001 state=acknowledged server_ref=01a1ad19-94c2-…   (×4, same ids as local)
SYNC-DONE owner=grader2 rows=4
$ sync.py status → SYNC-STATUS owner=grader2 acknowledged=4
```

Destination (already populated via restore) still `src=1 hl=1 bmk=1 note=1` — all four server applications were replays, **zero duplicates**. Local-durable → server-durable are distinct, honestly named states. **CONFIRMED.**

### Probe F — crash-interrupted restore + retry + repeated restore

```
$ PGDATABASE=arv_grader2c python3 harness/export.py restore --archive …/g2-export-001 --crash-at pre-commit
→ process SIGKILLed (exit 137); destination authoritative rows = 0 (clean, nothing half-restored)
$ retry → RESTORED owner=grader2 … tables=13 rows=18 state_hash_match=true
$ repeat → FAIL ARV-EXP-002: the destination is not clean (authoritative rows exist for this owner) — a restore is once-per-destination, never a silent mixed state   (exit 1)
```

**CONFIRMED** (matches the report's Step 6c/6d exactly).

### Probe G — search before any index rebuild (fresh user, walking beyond the report)

A brand-new owner (`newbie`), no `extract`, no `rebuild_keyword_index` ever run: import → highlight → note, then search. Source, highlight and note are ALL findable immediately (`search quokka` → `highlight|…`, `note|…`, `source|…`) — the keyword index rides each capture's transaction (KWR-07's explicit-lag contract, verified at the data level: `keyword_index` rows exist per entity at creation; tokenization is whole-word — a half-cut "manifest" does not match "manifesto"). **Consequence (see my finding N2): on a live library the user NEVER needs `rebuild_keyword_index`; a restore is the unique path into the empty-index state.**

### Setup-level verifications

- No `README.md` at the repo root (front door is `AGENTS.md`) — report Finding 2 confirmed.
- Makefile documents only `PGHOST · PGPORT · PGUSER` — `PGDATABASE` absent from the user-facing connection docs — Finding 3 confirmed; and `python3 harness/migrate.py --help` **executes the migration** instead of printing help (verbatim: `ARV-MIG-001: nothing to apply — no-op (all recorded, unchanged)`) — Finding 3's footgun confirmed.
- Import/extract acks omit `durability_rung` while capture acks name `local_durable` — Finding 4 confirmed from my own acks above.
- `create_highlight --help` says nothing about offset semantics (they are character offsets into the decoded text) — Finding 7 confirmed.
- The acceptance run's own artifacts re-verified: `diff -r snap-before-reopen snap-after-reopen` → IDENTICAL; `snap-final-original` vs `snap-restored` → only the two derived-state diffs; `snap-restored-rebuilt` → bookmark resolved again; read-only counts on `arv_acceptance`/`arv_acceptance_2` (owner z, 1 source each) — the run really happened as described.

---

## 3. The re-judged findings (the report's P2/P3s — fair / unfair / missed)

**No P0/P1 claimed by the report. My judgment: correct.** I reasoned through every finding against the two bar definitions — P0 = data loss / wrong data; P1 = broken core flow — and pressed each one myself:

1. **[P2] Restore leaves the library not-yet-operational and doesn't say so — FAIR, reproduced exactly.** Against the RTM §3.7 contract, this is the crux the part-2 brief asked me to judge, and my verdict is two-layered:
   - **It is NOT a truthfulness violation of the frozen contract.** RTM §3.7 explicitly defines `restored` (post-validation, equality contract holds, ledger reconciled) as a DISTINCT state from `fully_operational`, with `--rebuild derived-->` as an explicit, separate transition ("indexes rebuilt from the restored authoritative state"). The restore ack lands the library in exactly the contracted `restored` state and never claims `fully_operational`; every claim it does print (rows, `state_hash_match=true` over the authoritative set, `ledger_as_of`, the D-029 window) is literally true, and the equality contract SYS-10 freezes (authoritative + history + purge state) is fully delivered — my Probe C proved content equality with only derived differences, which SYS-07/§3.9 classify as disposable by design. The un-rebuilt derived state is therefore an **honest intermediate state by contract**, not an overclaim. (The export.py docstring even says "Derived state … is NEVER exported — it rebuilds" — but that is source, not user-facing output.)
   - **It IS a genuine user-surface gap, and P2 is the right severity.** (a) The state machine's own `restored` vs `fully_operational` distinction is never surfaced to the user — the ack gives no hint a rebuild step exists or is needed. (b) The search surface cannot distinguish "index empty" from "no match": the P3-07 slice's own search contract ("searchable or explicit lag/failure, never a silent miss" — `context/extracted/50-P307-KEYWORD-INDEX.md`, CLAIM-058) is defeated on the restore path; the only honest signal is the bookmark's typed `unresolved/no-current-generation`, a surface the user must think to consult. (c) My Probe G sharpens it: on a live library the user never needs `rebuild_keyword_index` (captures index at commit), so restore is the UNIQUE path into the empty-index state — the one moment the command is needed is the one moment it is unmentioned. A user who restores and immediately searches would reasonably conclude their library did not arrive. Still not P1: zero data loss (my diff proves all authoritative content arrived), zero wrong data (the empty search returns nothing false; the bookmark refuses to pretend), and the core flow is intact on the live library.
2. **[P2] No user-facing entry document — FAIR.** Confirmed: no README; the front door is an agent-workspace map plus a 570-line freeze matrix; `PGDATABASE` and the canonical first-session order had to be assembled from `--help` and session records. No functional impairment (everything worked once found), so P2-for-a-day-one-user is defensible (an argument for P3 exists; either way non-blocking).
3. **[P3] `PGDATABASE` undocumented; `migrate.py --help` executes the migration — CONFIRMED VERBATIM by me.** Fair P3. (Borderline P2 on a truly fresh machine — the schema would silently land in the `postgres` database — but no data loss, discoverable, recoverable.)
4. **[P3] Ack vocabulary inconsistent (import/extract omit `durability_rung`) — CONFIRMED from my own acks.** Fair P3: it is an UNDERclaim (the commit really happened; nothing overstates persistence, which is SYS-01's actual law), though I note the letter of RTM SYS-01/§4.3 ("every write command returns `{status, durability_rung, …}`") makes it a frozen-vocabulary conformance footnote to close in Phase 4.
5. **[P3] Highlight's anchor "not observable" — PARTIALLY INACCURATE (the report MISSED a surface).** `get-capture` indeed omits the anchor id, and `resolve-anchor` with the highlight id is refused (I reproduced both). BUT `get-history --id <highlight-id>` **does** return `"anchor_id":"01a1ad1a-0332-7533-9fd7-8bcc509d0fdc"` (verbatim from my run), after which `resolve-anchor --id <anchor-id>` resolves fine (verified). The accurate residue is a read-surface inconsistency (the primary read doesn't show what the history read does), not "effectively unusable". Severity stays P3 — the report overstated a defect, which is the safe direction, but the claim as written is wrong.
6. **[P3] Search output unlabeled — CONFIRMED** (`kind|id|revision|freq`, no header). Fair.
7. **[P3] Offset semantics undocumented at point of use — CONFIRMED** (`--help` silent; character offsets; the refusal text is where the char-count surfaces; the ack doesn't echo the span, `get-capture` does). Fair P3 — the most wrong-data-adjacent of the P3s (a byte-offset assumption on multi-byte content would silently shift the span), but pure-ASCII content is unaffected and the verification surface exists.
8. **[P3] BrokenPipeError on `| head` — not re-verified; cosmetic and immaterial to the gate.**
9. **Delights — consistent with my own experience** (every refusal I hit named a code, an invariant, and a repair; exactly-once held everywhere I pressed it).

**Did the report MISS anything a real user would hit?** I walked beyond it on four axes — every read surface cross-owner (12 surfaces + export, all clean), search-before-index-build (clean — captures searchable at commit), crash/retry/refuse restore dynamics (clean), sync replay against a restored destination (clean) — and found **no new defect**. The report's verdict section already names the misses I would otherwise add (no document read path, no pagination, no owner-facing purge flow — the last a documented later-phase deferral owned by D-011/P3-09's ledger mechanism, which part 1's EXP-07/10..15 evidence proves effective after restore).

---

## 4. My findings (numbered)

1. **[P3 — report accuracy]** The acceptance report's Finding 5 is partially inaccurate: a highlight's anchor IS observable via `get-history` (verbatim: `"anchor_id":"01a1ad1a-0332-7533-…"`), so the documented anchor-resolution surface is usable for highlights through that path. The true gap is only that `get-capture` (the primary read surface) omits the anchor id. No severity change (P3 either way); corrected for the record.
2. **[P3 — informational, sharpens the report's P2 #1]** On a live library the user never needs `rebuild_keyword_index` (source/highlight/bookmark/note all index at commit riding the capture transaction — data-verified via `arv.keyword_index` rows at creation). A restore is therefore the *only* ordinary path into an empty index, which makes the restore ack's silence about the rebuild step more user-hostile than a generic "derived state lags" note would be. Not a new defect; a strengthening of the report's P2.
3. **[P3 — confirmed]** `python3 harness/migrate.py --help` executes the migration rather than printing help (observed verbatim). Combined with `PGDATABASE` being absent from the Makefile's connection docs, a fresh-machine user following only the Makefile installs the product schema into the `postgres` database. No data loss; recoverable.
4. **[P3 — confirmed]** `import_source` and `extract_source` acknowledgments omit `durability_rung`, deviating from the letter (not the spirit — no overclaim) of RTM SYS-01/§4.3's frozen ack vocabulary. Close in Phase 4's ack unification.

**No P0. No P1. No new P2 beyond the report's own two P2s, both of which I independently reproduced and judge fairly severitized.**

---

## 5. FINAL VERDICT

# PASS — the Phase 3 exit gate holds.

**Exact reasoning, against the three gate conditions:**

1. **Part 1's matrix walk holds.** Its verdict is "Does the matrix walk hold? YES" — all 11 SYS rows traced to pre-registered paths, all 21 suites exit 0 on the grader's own fresh DB, 13/13 Phase-3 slice evidence sets present with SEV `disposition=PASS`, 32/32 known-bads firing their named codes, one full `make verify` exit 0 (gate GREEN, canonical layer 54/0) — and its findings are four P3 cosmetic/informational notes, **no P0/P1** (and no P2). I spot-verified its raw logs (`make-verify-exit.txt`, `suite-results.txt`, `make-verify.log` tail) and they match its claims.
2. **The acceptance run covered the required user path with no P0 and no P1.** The exit-criteria user-path line — a real client/backend path ingesting supported input, creating a Highlight with a valid Anchor, a Bookmark and a Note, then finding them via keyword search — is covered end-to-end (report Steps 1–3), together with restart/recovery (fresh-process reopen, byte-identical — artifacts re-verified by me), export/restore equality (content equality with only derived differences, exactly as SYS-07/§3.7 classify them), and truthful durability states (`local_durable` rungs, honest pending/acknowledged sync views, typed refusals everywhere). The report claims no P0/P1, and my severity re-judgment agrees: neither of its P2s implies data loss, wrong data, or a broken core flow — the restore/derived P2 is a findability/usability gap in a state the RTM itself defines as the honest `restored` intermediate (the ack never claims `fully_operational`), and the documentation P2 impairs discovery, not function. The one accuracy error I found in the report (Finding 5, anchor observability) *overstates* a defect — it cannot manufacture a P0/P1.
3. **My own probes found no new P0/P1.** Seven probe groups on my own scratch databases (full user-path reproduction; replay/409 zero-duplicate; export/restore content equality + derived-state reproduction; crash-interrupted restore clean-and-converging; sync replay without duplicates; twelve-surface cross-owner isolation including the export path; search-at-commit behavior) — every product claim I pressed held, and the two defects I confirmed are the report's own P2/P3s, fairly severitized.

**Non-blocking repairs recommended for the owner's P2/P3 register** (the repo's own review law #8 requires owner-approved records with revisit conditions for P2s): (a) name the rebuild step — or the `restored` vs `fully_operational` distinction — in the `RESTORED` ack, and give the search surface a way to distinguish an empty index from a no-match; (b) a human front door (README/quickstart naming the CLIs, `PGDATABASE`, and the first-session order); (c) add `durability_rung` to the import/extract acks; (d) include `anchor_id` in `get-capture`; (e) document character-offset semantics in `create_highlight --help`; (f) make `migrate.py` respect `--help`. None of these is a Phase-3 exit condition: the gate's own text requires the uncoached path plus this grader's pass "with no P0/P1", and no P0/P1 exists — in the report, in part 1's walk, or in anything I could find by trying to break it.

**The Phase 3 exit gate PASSES at revision `3b5ed28`.**
