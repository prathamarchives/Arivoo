# SEV round-3 — CLAIM-063 / P4-00b (the client-contract freeze + the boundary test) — FINAL

- **Agent label:** agent-4f9c2e17 (fresh-context Systems Engineering Verification, round 3 — the FINAL round; rounds 1–2 read in full, every load-bearing assertion re-verified independently, none taken on trust)
- **Date:** 2026-11-06T04:41Z
- **Slice:** CLAIM-063 — P4-00b: the client-contract freeze + the boundary test
- **Base (origin/main):** `54533c6e18cb5ae00fdd3e584c41261a71419cde`
- **Head under review:** `457e80fb2c4027e4b1603c52d4771c07530a5f67` (branch `slice/claim-063-p400b-contract-boundary`)
- **Commit chain reviewed:** d0667b4 (commit A) → 61762b8 (RED: test_boundary.py + gate registration) → 357a32f (red-01.txt) → 42c9441 (red-records binding) → 085b13e (GREEN: implementation + disclosed amendments + run records) → 3b0ed71 (scope widening) → 457e80f (the round-1 repairs; round-2's verified head)
- **ROUND 3 — FINAL**

**No repository source file was modified; nothing committed or pushed.** My one write is this report. Scratch DB `arv_sev3_19803_939162082` (created, migrated, probed) was dropped; the `git archive` RED-reproduction trees under /tmp were removed; `git status` clean of my actions (only the pre-existing untracked sev-round-2.md and this file).

---

## 1. What I ran (commands + exits)

| Command | Exit | Note |
|---|---|---|
| `python3 harness/tests/test_boundary.py` | 0 | BND-01..06 all PASS — exit 0, 6 PASS as claimed |
| `python3 harness/tests/test_export.py` | 0 | EXP-01..15 GREEN (incl. the amended EXP-09) |
| `python3 harness/tests/test_capture.py` | 0 | CAP-01..23 GREEN (incl. the amended CAP-09) |
| `python3 harness/tests/test_contract.py` | 0 | CON-01..08 GREEN |
| `python3 harness/tests/test_sync.py` | 0 | SYN-01..17 GREEN |
| `python3 harness/tests/test_keyword_index.py` | 0 | KWR-01..10 GREEN |
| `SLICE=claim-063-p400b-contract-boundary GATE_DIFF=origin/main make gate` | 2 (gate rc 1) | **all 24 declared suites exit 0 inside the gate**; scope/claims/red-record/LAW/known-bad checks clean; refuses on EXACTLY `ARV-PRF-004` + `ARV-SEV-001` — the two expected pre-finalize artifact codes |
| Scratch DB rig: `pg.create_scratch_db('sev3')` + `harness/migrate.py` | 0 | 13 migrations applied; 19 adversarial probes at the REAL CLIs (§2); DB dropped after |
| RED reproduction A: `git archive 61762b8` → temp tree → `test_boundary.py` | 1 | `FAIL ARV-TEST-000` machinery-absent, quoting the version-less record_event ack — red-01.txt's class reproduced live |
| RED reproduction B: `git archive 085b13e` + HEAD's amended `test_boundary.py` | 1 | **the F3 TRUE RED reproduced**: BND-04 alone fails (red-02.txt's claim); direct CLI delta confirmed — pre-repair `--limit abc` = argparse exit 2, HEAD = typed `ARV-QRY-004` exit 1 |
| RED reproduction C: `git archive 42c9441` → `test_boundary.py` | 1 | machinery-absent at that commit — the evidence for finding F11 (run-record attribution) |
| Digest chains (`sha256sum` vs `red-records.json` `current_sha256`) | — | 3/3 EXACT: test_boundary.py `70d9c70f…`, test_capture.py `475a31d3…`, test_export.py `c0b89f98…` |
| AST census count + REGISTRY cross-check | — | 28 `cmd()/extract()` calls before the `CENSUS = list(ACKS)` snapshot (line 249); 16 distinct verbs; `ALL_VERBS` == commands.py `REGISTRY` (16, set-equal, no missing, no extra) |
| Scope coverage check (23 diff paths vs scope.txt) | — | every diff path declared (files + the runs-dir prefix); the PR-mode gate's own scope check also green |

---

## 2. Adversarial probes (my own design, on my own scratch DB — all at the real CLIs)

| # | Probe | Observed result |
|---|---|---|
| 1 | `list-notes --limit 1` (exactly 1, 2 alive notes) | header + exactly 1 id + `# more=true`, exit 0 — the observed truth marker, not inferred |
| 2 | `list-notes --limit 1000` (exactly 1000, only 2 rows) | both alive ids + `# more=false`, exit 0; the tombstoned note stays hidden |
| 3 | `--after <UPPERCASE-UUID>` | accepted, normalized by `uuid.UUID()`, correct keyset page (the suffix page) — same answer as the canonical lowercase form |
| 4 | `--after {braced-uuid}` / `--after urn:uuid:…` | both accepted, normalized, identical keyset page — uuid-format edges degrade to the canonical behavior, never an error |
| 5 | cross-family cursor: a SOURCE id as `list-notes --after` | graceful keyset page from that position (all alive notes), exit 0 — owner scoping intact, no leak, deterministic position semantics; the refusal text's "same family" is advisory, not enforced (round-1 F7's own note — confirmed) |
| 6a | injection: `--after "' OR '1'='1"` | typed `FAIL ARV-QRY-004` exit 1 (uuid validation fires before any SQL); `arv.note` count unchanged |
| 6b | injection: `--limit "1; DROP TABLE arv.note;--"` | typed `FAIL ARV-QRY-004` exit 1 (int() refusal) |
| 6c | `--after ""` (empty string) | typed `FAIL ARV-QRY-004` exit 1 |
| 7 | note whose content carries the literal `# more=true`, `# api_version=1`, pipes, and newlines | `get-note` → ONE stdout line, parseable JSON, content byte-intact, `api_version: 1`; the flag\|payload split survives the pipes (maxsplit=1); no data line ever starts with `#` — labels can never be confused with data on this surface |
| 8 | `get-note-history` on the same note | one JSON row, `api_version: 1`, parseable (newline-only framing law holds under the re-serialization) |
| 9 | `search` for the marker-laden note's unique term | row `note\|<id>\|1\|1` under the `# api_version=1 kind\|…` header, exit 0 — no parser confusion |
| 10 | `search` for a term appearing ONLY in a tombstoned note | **header ALONE**, exit 0 — tombstone parity at query time holds under the new versioned header |
| 11 | `get-capture` whose `selected_text` AND `context_after` contain pipes + a newline | ONE stdout line, parseable JSON, fields byte-intact, `api_version: 1` |
| 12 | `resolve-anchor` on an absent id | typed `FAIL ARV-QRY-001` exit 1, no side channel |
| 13 | `--limit` int-parsing edges: `' 5 '`, `'5.0'`, `'+5'`, `'-1'` | `' 5 '`/`'+5'` accepted as 5 (int() semantics — still an integer value, in bounds); `'5.0'` → typed non-integer refusal; `'-1'` → typed bounds refusal — every refusal the frozen exit-1 shape |
| 14 | `list-captures --after <own capture id>` | empty page: header + `# more=false` alone, exit 0 |
| 15 | cross-owner list: owner B lists on A's populated DB | header + `# more=false` ALONE — zero of A's ids (RLS holds at the list boundary) |
| 16 | `resolve-anchor` on the real anchor | one-line versioned JSON answer (`state=resolved`, `api_version: 1`) |
| 17 | crash-path: `crash.py --command create_note --point post-commit-pre-ack`, then same-key retry | kill: exit 2, no ack; retry: `status=replayed … durability_rung=local_durable api_version=1` — the F3 residual closed on the crash path too, independently |
| 18 | cross-owner no-oracle, the F1-repair substance re-run with the pin's exact logic: B reads A's REAL capture and REAL note vs B reads an absent id | all HOLDS: exit 1 + `ARV-QRY-001:` both; template-normalized byte-equality; stderr byte-equality (capture arm); reader-independence (same absent id as A and as B, un-normalized byte-equal) |
| 19 | `extract_source` replay (its own ack print sites) | `status=replayed … state=current durability_rung=local_durable api_version=1`, exit 0 |

**Verdict on the probes:** every probe behaved per the frozen contract or refused typed. No parser-confusion, no injection reach, no framing break, no cross-owner leak, no marker/data confusion — including the marker-laden-content probe (7–9) and the tombstoned-term search parity (10), neither of which any prior round ran.

---

## 3. Load-bearing spot-checks (prior rounds' claims re-verified, not trusted)

1. **RED-first chain (LAW-11) — reproduced live, twice.** At the RED commit 61762b8 (an ancestor of HEAD; `commands.py` there has no `API_VERSION`, `query.py` no list machinery — checked via `git show`), the suite exits 1 with `ARV-TEST-000` quoting the version-less record_event ack: red-01.txt's exact class. The F3 TRUE RED also reproduces: HEAD's amended suite against the 085b13e implementation (which still had `type=int`) fails BND-04 alone — and the direct CLI delta is observed (`--limit abc`: exit 2 pre-repair vs typed `ARV-QRY-004` exit 1 at HEAD). red-02.txt is an honest capture (it even preserves the pre-f-string-fix `{len(ACKS)}` literal, itself disclosed as amendment 2 in red-records.json).
2. **Digest chains — 3/3 exact.** `current_sha256` for test_boundary.py / test_capture.py / test_export.py equals `sha256sum` of each file at HEAD; the amendment chains (including the two-edits-one-commit form round 2 disclosed) hold; test_export.py's final amendment note names EXP-09 (round-1 F4 repair confirmed).
3. **The census claim — honest.** AST count: exactly 28 `cmd()/extract()` calls before the `CENSUS` snapshot (line 249), 16 distinct verbs, set-equal to commands.py's REGISTRY (programmatically: no missing, no extra); the live suite passes BND-01 with `len(CENSUS) == 28` and the exact 8-verb replayed set. A silently-broken verb now breaks both the count and the verb set. Round-1 F2's repair is real and complete.
4. **The F1 repair's substance — holds live** (probe 18): the amended BND-04 cross-owner pins are non-vacuous and the law they pin is true at the real boundary.
5. **Round-2's two new P3s — both genuinely routable, neither a hidden defect.**
   - *F10 (the `ARV-QRY-001` repair-hint wording):* the shared `_refuse` hint ("check the id against the caller's own capture list (query.py list-captures)") is byte-identical at **origin/main line 207** — pre-existing, unchanged by this slice. It is advisory prose; no consumer parses it (sync.py's `_outcome` parses `result_ref=`/`FAIL ` tokens; export.py reads the DB directly). The freeze makes later rewording heavier (it must ride the contract's own change process), which is exactly why round 2 routed it to P4-00c now. Routed correctly.
   - *F5/F9 (README lag + the routing-attribution prose):* README.md is NOT in scope.txt; its search-header example (README.md:69) is byte-stale against the live versioned header — a real, visible docs gap that was routed to P4-00c rather than smuggled in. The routing's record placement is exactly as round 2 described: the repair commit's message carries it in full; `notverified.txt` does not exist yet (it lands at the finalize — the gate enforces the obligation via `ARV-SEV-001`); record 55 predates the SEV round and does not carry the F5/F6/F8 routing. Accurate observation, correctly classified as prose polish.
6. **The gate at this head:** PR-mode refuses on exactly `ARV-PRF-004` + `ARV-SEV-001` (the proof sheet + sev.json that land at the finalize), with all 24 declared suites green inside the gate — matching both prior rounds.
7. **Scope honesty:** all 23 diff paths are declared in scope.txt (the runs-dir prefix covers the artifact files); the two disclosed consumer-suite amendments (CAP-09, EXP-09) only widen acceptance forms, never remove assertions — re-read in the diff.
8. **Round-2's below-threshold observation confirmed independently:** BND-01/BND-03's check-time prose ("the census + every later fixture ack") renders at len==28 — the 102 later fixture acks (the post-snapshot re-tombstone + owner C's 101 create_note acks) are not grammar-walked by BND-03. Immaterial to the freeze's substance: verb coverage is complete via the exact-28 census, and the later acks flow through the same censused print sites (the spine's committed/replay prints). Prose imprecision only — agreeing with round 2's classification; no new finding raised.

---

## 4. Findings (continuing from F11)

### F11 — P3 — run-01..05.json's `commit` field names a commit at whose tree the recorded result cannot reproduce
- The five run records (`harness/runs/claim-063-p400b-contract-boundary/run-01..05.json`) record `exit_code: 0` with `commit: 42c9441f…`, timestamps 03:00:56–03:21:32. Commit 42c9441 was made 02:51:24; the GREEN (085b13e, which first contains the implementation AND these records) landed 03:21:49 — i.e., **the runs measured the uncommitted working tree that became 085b13e, with HEAD-at-capture = 42c9441**. Verified live: `git archive 42c9441` → `test_boundary.py` exits 1 (`ARV-TEST-000`, machinery-absent; `query.py`/`commands.py` at that commit carry no list machinery / no `API_VERSION` — checked directly). A verifier checking out 42c9441 cannot reproduce "exit 0 at 42c9441".
- **Why P3, not higher:** the runs' SUBSTANCE is true — the tree that is 085b13e passes (my run at HEAD descends from it; round 1, round 2, and my gate run all re-verified it; `make verify`'s equivalents recorded in run-04/05 also re-verified by the gate's 24-suite sweep). The GREEN commit's own message discloses the runs as "MEASURED at this tree," and the records were committed INTO that very tree, so the provenance is reconstructible. The sibling slice claim-062 followed the stricter convention (runs recorded AFTER the GREEN commit, so `commit` names the measured tree: 109b9a5). This is evidence-record provenance polish — the record does not lie about the result, it misnames the tree under the field's natural reading.
- **Disposition:** routed to the finalize (this slice's own next step, F6's home): record fresh run records at the final head (or a disclosed amendment naming the measured tree), and carry the field-semantics note ("HEAD at capture time") in the notverified.txt that lands there. Neither prior round caught it; neither blocks.

**No other new findings.** Zero P0. Zero open P1. Zero open P2. One new P3 (F11, routed). All round-1 findings (F1–F8) and round-2 findings (F9–F10) verified as repaired or properly routed, matching both reports' dispositions exactly.

---

## 5. Verdict

The claim is delivered and frozen as stated: `api_version=1` observed on every write ack surface (all 16 verbs via the exact-28 census, committed AND replayed — including the crash-path replay and extract.py's own print sites — re-verified live outside the fixture) and every read surface (get-* bodies, all three history families' rows, resolve-anchor, the search header, the list headers); the replayed acks + record_event's committed ack carry `durability_rung=local_durable` (F3 residual closed on every path I could reach, including the killed-writer retry); the ack grammar is frozen and pinned (BND-03); the typed-error surface refuses in the frozen shape from both directions with zero effect; the list contract holds at every boundary I probed (1, 1000, defaults, keyset walks, empty owners, marker-laden content, injection attempts); the permanent suite is green and its pins are non-vacuous after the round-1 repairs. The RED chain is real (reproduced live at both links), the digest chains are exact, the census is honest, and the two routed P3s are genuinely route-able polish. The one new finding (F11) is evidence-record provenance polish, routed to the finalize.

**DISPOSITION: PASS**

### Routed forward (for the finalize — none block)
1. F11: fresh run records at the final head (or a disclosed amendment naming 085b13e as the measured tree) + the field-semantics note in notverified.txt.
2. The finalize's notverified.txt remains obligated to carry (per rounds 1–2): the export.py/migrate.py version-field exclusion (test_boundary.py:48–50), F5's README routing (P4-00c), F7a/F7c byte-form notes, F8 hygiene, F9's attribution note, F10's hint-wording routing (P4-00c via the frozen contract's change process), and now F11.
