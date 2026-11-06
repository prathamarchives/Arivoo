# SEV round-2 — CLAIM-063 / P4-00b (the client-contract freeze + the boundary test) — repair verification + re-sweep

- **Agent label:** agent-21fadb2c (fresh-context Systems Engineering Verification, round 2 — verifying round-1 repairs; round-1 report read in full first)
- **Date:** 2026-11-06T04:20Z
- **Slice:** CLAIM-063 — P4-00b: the client-contract freeze + the boundary test
- **Base (origin/main):** `54533c6e18cb5ae00fdd3e584c41261a71419cde`
- **Head under review:** `457e80fb2c4027e4b1603c52d4771c07530a5f67` (branch `slice/claim-063-p400b-contract-boundary`)
- **Commit chain reviewed:** d0667b4 (commit A: reconciliation + record 55) → 61762b8 (RED: test_boundary.py + gate registration) → 357a32f (red-01.txt) → 42c9441 (red-records binding) → 085b13e (GREEN: implementation + disclosed amendments) → 3b0ed71 (scope widening) → **457e80f (the round-1 repairs — the commit under verification)**
- **No repository source file was modified; nothing committed or pushed.** My one write is this report. Scratch DB `arv_sev2_16498_937935172` (created, migrated, probed) was dropped; temp files removed; `git status` clean.

---

## 1. What I ran (commands + exits)

| Command | Exit | Note |
|---|---|---|
| `python3 harness/tests/test_boundary.py` | 0 | BND-01..06 all PASS — the census + cross-owner + typed-limit pins holding |
| `python3 harness/tests/test_capture.py` | 0 | CAP-01..23 GREEN |
| `python3 harness/tests/test_export.py` | 0 | EXP-01..15 GREEN |
| `python3 harness/tests/test_bookmark.py` | 0 | BMK-01..13 GREEN |
| `python3 harness/tests/test_note.py` | 0 | NTE-01..15 GREEN |
| `python3 harness/tests/test_keyword_index.py` | 0 | KWR-01..10 GREEN |
| `python3 harness/tests/test_contract.py` | 0 | CON-01..08 GREEN |
| `python3 harness/tests/test_highlight.py` | 0 | HLG-01..12 GREEN (re-sweep: the hl2 lifecycle fixture's family) |
| `python3 harness/tests/test_anchor.py` | 0 | ANC-01..10 GREEN (re-sweep: ANC-08's own cross-owner form intact) |
| `SLICE=claim-063-p400b-contract-boundary GATE_DIFF=origin/main make gate` | 2 (gate rc 1) | refuses on EXACTLY ARV-PRF-004 + ARV-SEV-001 — the two expected pre-finalize artifact codes; all 24 declared suites PASS inside the gate; scope/claims/red-record/known-bad checks all clean |
| `make verify` | 0 | 23 suites + known-bad matrix + gate selfcheck + canonical layer 54 checks / 0 failures |
| Digest chains (`sha256sum` + `git show <rev>:<file> \| sha256sum`, all three amended suites) | — | all chain correctly (§3) |
| Live probes on my own scratch DB (migrated; 16 CLI invocations for the F1/F3/F7/replay verification) | — | §2/§5 |
| `git show 457e80f` (full repair diff: query.py, red-records.json, red-02.txt, sev-round-1.md, test_boundary.py) + full read of the amended test_boundary.py (533 lines), query.py arms, commands.py REGISTRY | — | the repair review itself |
| Programmatic census cross-check (ALL_VERBS vs commands.py REGISTRY vs the fixture's 28 calls) | — | §2/F2 |

---

## 2. Per-finding repair verdicts

### F1 (P1) — the vacuous cross-owner pin — **REPAIRED**
- **Code read:** test_boundary.py:345-390. The amended BND-04 probes BOTH directions at REAL objects: `r_xo_cap = get-capture --owner B --id hl1` (A's REAL capture) and `r_xo_nt = get-note --owner B --id n1` (A's REAL note), each compared to B's absent-id refusal via `_tmpl(out, qid)` (the queried id normalized to `<id>`) — byte-equality of everything else; PLUS `r_xo_cap.stderr == r_xo_abs.stderr` (capture arm); PLUS reader-independence (`r_abs_A.stdout == r_abs_B.stdout`, the same absent id read as A and as B, un-normalized). The absent-vs-absent-only vacuity is gone: a cross-owner read of an id that EXISTS under another owner is now in the suite, twice (capture + note arms).
- **Live reproduction on my scratch DB (owner A's real highlight + note vs a random absent uuid, all four probes re-run through the pin's exact logic):** every check HOLDS — cross-owner returncode 1 + `FAIL ARV-QRY-001:`; template byte-equality; stderr byte-equality; reader-independence byte-equality.
- **Leak-distinguishing power (the required adversarial construction):** I fed four synthetic LEAKY refusal texts through the pin's own `_tmpl` comparison — (a) "belongs to another owner" wording, (b) refusal naming the owning owner, (c) refusal naming the object's kind, (d) an id-normalization dodge (the id rendered without dashes so `replace(qid)` misses it): **the pin CATCHES all four** (the templates diverge). The only difference structurally invisible to the pin is one contained ENTIRELY inside the id substring itself — which is the no-oracle law's own letter (the refusal may echo what you asked for; nothing else may differ). The pin is no longer vacuous in any round-1 sense.
- Minor (observation, not a defect): the note arm has no stderr-equality term (capture arm only) and reader-independence pins stdout only — both verified byte-equal live; a one-term widening would ride any future touch.

### F2 (P2) — the census width — **REPAIRED**
- **Code read + programmatic count:** the fixture now makes exactly **28 `cmd()`/`extract()` calls before the `CENSUS = list(ACKS)` snapshot** (20 first-walk + 8 replays), and BND-01 pins `len(CENSUS) == 28` (exact — the `>= 14` floor class is dead), `census_verbs == ALL_VERBS`, and `replayed_verbs ==` the exact 8-set. Cross-checked ALL_VERBS against commands.py's REGISTRY **programmatically: 16 == 16, set-equal, no missing, no extra** (revise_highlight / move_bookmark / tombstone_bookmark / restore_bookmark / restore_highlight all now walked; the round-1 census's 5 unwalked verbs + the missing bookmark/note/lifecycle replayed forms all present). A silently-broken verb (FAIL, no ACK line) now fails BND-01 twice over: the count drops below 28 AND the verb vanishes from `census_verbs`.
- **Live:** the suite PASSes with exactly these numbers (BND-01/02/03 observed green; the census is 28 lines, 16 verbs, 8 replayed forms — import/extract/highlight/bookmark/note/record_event/rebuild + the tombstone_note lifecycle replay).
- The suite's own BND-01 message renders "all 28 ack lines" — the f-string bug disclosed in the second amendment is confirmed fixed in the observed output.

### F3 (P3) — the non-integer `--limit` — **REPAIRED**
- **Code read:** query.py:441-444 — `type=int` removed, `default=str(DEFAULT_LIST_LIMIT)`; `_list_arm` (query.py:273-278) does the `int()` conversion with the typed `_refuse_list_bounds` → `FAIL ARV-QRY-004:` exit 1. The help text discloses the shape.
- **Live on my scratch DB (all three arms):** `--limit abc` / `1e3` / `xyz` → `FAIL ARV-QRY-004: --limit '...' is not an integer`, exit 1 (never argparse's exit-2 usage); `--limit 0` / `-5` / `1001` → typed bounds refusal exit 1; `--after not-a-uuid` → typed cursor refusal exit 1. Happy path intact: `--limit 1` / `1000` / default all answer header + ids + `# more=` marker, exit 0.
- The RED for this repair is recorded honestly (red-02.txt: FAIL BND-04, exit 1 — the argparse exit-2 vs frozen exit-1 shape, observed at the pre-repair tree; the census/cross-owner pins passing immediately as disclosed pin-strengthening).

### F4 (P3) — the test_export.py amendment note's copy-paste — **REPAIRED**
- red-records.json's final test_export.py amendment note now names **EXP-09** ("the REAL change is EXP-09's empty-search expectation carrying the P4-00b versioned header '# api_version=1 kind|entity_id|revision|matched_terms'... the digest chain (prior 6711140e -> new c0b89f98) was verified exact by the SEV round BEFORE this prose correction") — the correction is itself disclosed, which is the right form for an evidence record.
- Digest chain re-verified end-to-end (§3): the amendment's `new_sha256` c0b89f98… == `sha256sum harness/tests/test_export.py` NOW; `prior_sha256` 6711140e… == the file at origin/main.

### F5 (P3, routed) — the README surface-docs lag — **PROPERLY ROUTED**
- Recorded in the repair commit's message ("F5 the README's surface-docs lag routes to P4-00c (the capability-matrix slice rewrites the README's examples)"). Confirmed NOT silently repaired: README.md:69 still carries the stale unversioned header example (checked live) — consistent with the routing to P4-00c, README being outside scope.txt. See F9 below for the routing's record placement.

### F6 (P3, routed) — the notverified.txt promissory reference — **PROPERLY ROUTED (finalize-binding)**
- notverified.txt is still absent from the runs dir (checked) — exactly as the routing says: it lands at the finalize, and the gate ENFORCES the obligation (the PR-mode gate refuses on ARV-SEV-001 until the report artifacts land; proofsheet.py's notverified default-empty remains the residual risk round 1 named). Binding next-action unchanged: the finalize's notverified.txt must carry, at minimum, the export.py/migrate.py version-field exclusion named at test_boundary.py:48-50, the F5/F7a/F8 routings, and this round's F9/F10 notes.

### F7 (P3) — get-bookmark's api_version placement — **REPAIRED**
- query.py:397-401: the literal first-key dict is gone; get-bookmark now prints `_versioned(out)` — the same print-boundary injection every other read body uses.
- **Live:** `get-bookmark` body observed with `api_version` as the LAST key, byte-form uniform with get-capture/get-note/get-history rows (all verified on my scratch DB).

### F8 (P3, routed) — suite hygiene — **PROPERLY ROUTED**
- The `tempfile.mkdtemp(prefix="arv-blobs-")` (test_boundary.py:182) remains uncleaned (one bounded /tmp dir per run) and the duplicate commit-message cosmetics (357a32f/42c9441) remain — both disclosed in the repair commit's message as accepted polish. Nothing silently dropped.

---

## 3. Digest chains (re-verified independently)

| Suite | Chain | Verdict |
|---|---|---|
| test_boundary.py | binding `c6646175…` == `git show 61762b8 / 085b13e / 3b0ed71 :…` (unchanged since the RED, re-confirmed) → amendment 1 → `2508f439…` → amendment 2 → `70d9c70f…` == record `current_sha256` == `sha256sum` of the file NOW | **CHAINS** |
| test_capture.py | origin/main `af7683c4…` → amendment → `475a31d3…` == file NOW (4-link history intact) | **CHAINS** |
| test_export.py | origin/main `6711140e…` → amendment → `c0b89f98…` == file NOW (5-link history intact) | **CHAINS** |

- Each amendment's `prior_sha256` equals the previous link's `new_sha256`; each record's `current_sha256` equals the file's digest NOW (programmatic check, all three suites).
- Observation: amendment 1's intermediate digest `2508f439…` (the f-string-bug tree) was never committed — both amendments landed in the single repair commit — so that one link is verifiable only internally (am1.new == am2.prior). Both ENDPOINTS verify against git history (the binding against 61762b8..3b0ed71; the current against 457e80f/HEAD). The amendment discipline (ARV-RED-006 chaining) holds; the two-edit-one-commit form is disclosed in amendment 2's note.

---

## 4. New findings (continuing from F9)

### F9 — P3 — the repair commit's routing attribution overstates the record placement (prose; the routing itself is honest)
- The commit message says the routed P3s are "recorded in the slice's notverified + record 55" — but **notverified.txt does not exist yet** (it lands at the finalize — F6's own disclosed disposition) and **record 55** (context/extracted/55-P400B-CONTRACT-BOUNDARY.md, minted at d0667b4 BEFORE the SEV round; 19 lines) does not mention F5/F6/F8. The routing IS honestly recorded — in the commit message itself, in full detail — so nothing is silently dropped; the attribution names two homes that do not (yet) carry it.
- **Disposition:** accept-with-note + binding finalize obligation: the notverified.txt that lands at the finalize MUST carry F5 (README lag → P4-00c), F6 (its own file), F7a/F7c byte-form notes, F8 (hygiene), and this round's F9/F10.

### F10 — P3 — the frozen ARV-QRY-001 refusal's repair hint names the CAPTURE arm on every get-* arm (pre-existing at base; now frozen byte-level)
- The shared `_refuse` (query.py:216) prints "check the id against the caller's own capture list (query.py list-captures)" — on get-note and get-bookmark refusals too, where the caller's own list is list-notes / list-bookmarks. Pre-existing at origin/main (line 207 at base), unchanged by this slice — but BND-04 now freezes these exact bytes (template-level pins), so the wording can only change through the contract's own change process. Cosmetic (no consumer parses the hint; the hint is advisory text).
- **Disposition:** route to P4-00c (the capability-matrix slice's surface-docs pass) via the frozen contract's change process; flagging now because the freeze makes later fixes heavier.

### Observations (below finding threshold; no action required before merge)
- BND-04's note arm lacks the stderr-equality term the capture arm has, and reader-independence pins stdout only — both verified byte-equal live; a one-term widening could ride any future touch.
- BND-01/BND-03 message prose says "all {len} ack lines the suite observes (the census + the later fixtures)" — rendered at check time len==28, which is the census alone; the 102 later fixture acks (the post-snapshot re-tombstone + owner C's 101 note acks) are not grammar-walked. Immaterial to F2's substance: verb coverage is complete via the census (all 16 verbs, exact-28 structure), and the later acks come from already-censused verbs through the same single spine print site; BND-05 separately pins the C-notes' list output. Prose imprecision only.
- The PR-mode gate's proofsheet detail line prints `FAIL ARV-PRF-002` (no sheet on disk) while the refusal summary counts `ARV-PRF-004` — pre-existing gate cosmetics, identical to round 1's observation; the refusal SET is exactly the two expected pre-finalize codes.

---

## 5. Re-sweep for repair-introduced defects (duty 4 — none found)

1. **The hl2 tombstone → restore → re-tombstone sequence:** census ends hl2 ACTIVE (so restore_highlight is walked), then the 29th ack (th-2b) re-tombstones it AFTER the snapshot so BND-04's ARV-QRY-003 tombstoned-read probe and BND-05's `hl2 not in list-captures` pin keep their objects. Verified consistent in-code and live (suite green: QRY-003 refuses on hl2; list-captures hides hl2, shows hl1).
2. **bm2's create → tombstone → restore → re-tombstone lifecycle:** ends hidden, so BND-05's `list-bookmarks == [bm1]` holds; bm1's move (5..15) leaves get-bookmark/get-bookmark-history correct (BND-06 green; history ≥1 rows with api_version).
3. **The tn-2 lifecycle replay after rn-2's restore:** probed live on my scratch DB — a tombstone_note replay (same key+body) after a restore returns `status=replayed` with the ORIGINAL result_ref and does NOT re-execute (get-note still answers; the note stays restored). The census's replayed-form pin is sound; no state corruption.
4. **Cross-suite state:** every suite runs on its own scratch DB (create/drop in finally); the census widening cannot leak state into other suites — and all 24 suites (gate-run) + the 9 I ran directly are green.
5. **The census snapshot's placement** (before the re-tombstone and the C-owner lab) keeps the 28-line structure pin exact while the later fixtures ride outside it — by construction, not accident (the comment at test_boundary.py:324-326 says so and the code does so).

---

## 6. Verdict

Zero P0. Zero open P1. Zero open P2. The round-1 P1 (F1) and P2 (F2) are genuinely repaired and independently re-verified live (including the adversarial leak-distinguishing constructions); F3/F4/F7 are repaired and verified live; F5/F6/F8 are properly routed with the routing honestly recorded in the repair commit's message. Two new P3s (F9 routing-attribution prose, F10 pre-existing frozen hint wording) — both polish, both with recorded dispositions, neither blocking. The full boundary suite, all consumer suites, `make verify` (canonical 54/0), and the PR-mode gate behave exactly as claimed at this head.

**DISPOSITION: PASS**

### Binding next actions (for the finalize — none block this round)
1. The finalize's notverified.txt MUST land carrying: the export.py/migrate.py version-field exclusion (test_boundary.py:48-50), F5's README routing (P4-00c), F7a/F7c byte-form notes, F8's hygiene disclosure, and this round's F9/F10 notes (F10 routed to P4-00c via the frozen contract's change process).
2. The sev.json + proof sheet artifacts close the gate's two expected refusals (ARV-SEV-001 / ARV-PRF-004).
