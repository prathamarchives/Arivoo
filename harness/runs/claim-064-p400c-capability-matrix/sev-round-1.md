# SEV round-1 — CLAIM-064 / P4-00c (the format capability matrix + extraction readiness)

- **Agent label:** agent-ee8ed9dd (fresh-context Systems Engineering Verification, round 1)
- **Date:** 2026-11-06T06:01Z
- **Slice:** CLAIM-064 — P4-00c: the format capability matrix + extraction readiness (the #98 SEV routings F5/F10 riding here)
- **Base (origin/main):** `647f3cb18fd877acd08689f195b61269e742fd8a` (PR #98 merge, CLAIM-063)
- **Head under review:** `570a23cdeafbde286583828ec22b4e8108016a9d` (branch `slice/claim-064-p400c-capability-matrix`)
- **Commit chain reviewed:** 0712989 (commit A: the post-#98 reconciliation + CLAIM-064 open + record 56) → 2f4d3ef (RED: test_capability.py CAP-01..06 + gate registration) → 3c2aa2c (red-01.txt + the typed red-record binding) → 570a23c (GREEN: harness/capability.py + the README rewrite + the per-family hint + run records)

---

## 1. What I ran (commands + exit codes)

| Command | Exit | Note |
|---|---|---|
| `python3 harness/tests/test_capability.py` | 0 | CAP-01..06 all PASS; my output byte-identical to the recorded run-01..03 (sha256 `ced89b21…91679d7`) |
| `python3 harness/tests/test_boundary.py` | 0 | BND-01..06 GREEN (the `_refuse` change regressed nothing) |
| `python3 harness/tests/test_contract.py` | 0 | CON-01..08 GREEN |
| `python3 harness/tests/test_capture.py` | 0 | CAP-01..23 GREEN |
| `python3 harness/tests/test_export.py` | 0 | EXP-01..15 GREEN |
| `python3 harness/tests/test_note.py` | 0 | NTE-01..15 GREEN |
| `python3 harness/tests/test_bookmark.py` | 0 | BMK-01..13 GREEN |
| `python3 harness/tests/test_highlight.py` | 0 | HLG-01..12 GREEN |
| `python3 harness/tests/test_anchor.py` | 0 | ANC-01..10 GREEN |
| `python3 harness/tests/test_extract.py` | 0 | EXT-01..17 GREEN |
| `python3 harness/gate.py --slice claim-064-p400c-capability-matrix --diff origin/main --skip-suites` | 1 | **REFUSES: ARV-SCOPE-002 + ARV-CLM-002 (tools/trusted_gate_anchored.py outside the declared scope) + ARV-PRF-002 + ARV-SEV-001 (the two expected pre-finalize codes)** — see F1 |
| `ARV_EVENT_NAME=pull_request ARV_PR_HEAD=slice/claim-064-p400c-capability-matrix python3 -I tools/trusted_gate_anchored.py --repo … --base /home/z/my-project/verification/trusted-base --phase gate --diff-ref origin/main` | 1 | the TRUSTED gate (the BASE's machinery — exactly what CI's `harness-trusted` job runs) **REFUSES on the same ARV-SCOPE-002 + ARV-CLM-002** (+ the two expected pre-finalize codes) — F1 dual-confirmed |
| RED reproduction: `git archive 2f4d3ef` → temp tree → `python3 harness/tests/test_capability.py` | 1 | `FAIL ARV-TEST-000: … capability.py matrix exit 2 …` — the RED is real at the RED commit, reproduced live |
| sha256 chain: `sha256sum harness/tests/test_capability.py` at HEAD and `git show 2f4d3ef:harness/tests/test_capability.py \| sha256sum` | — | both `5b959d2c…84ed7af` == red-records.json `binding_sha256` == `current_sha256`; `git cat-file -e 2f4d3ef:harness/capability.py` → absent (RED honest) |
| ~20 adversarial CLI probes on my own scratch DB (`arv_sevc_30968_944315085`, migrated 0001..0013, **dropped after** — verified no `arv_sevc*`/`arv_p400c*` remains) | see §4 | all at the REAL boundary (capability.py / extract.py / query.py / commands.py CLIs + direct psql cross-checks) |
| LAW-05 recount from `git diff origin/main...HEAD --numstat` | — | source 382 lines / 4 files, test 335 lines / 1 file, 0 migrations — inside the limits but 95.5% of the source-line budget (F1) |

No repository source file was modified; nothing committed or pushed; the scratch DB and all temp trees were removed.

---

## 2. Findings

### F1 — P1 — an undeclared protected-path file in the diff: `tools/trusted_gate_anchored.py` — both gates REFUSE the slice as it stands
- **Severity:** P1 — scope violation (the SEV scale's own letter) + a broken consumer (the PR cannot go green).
- **Location:** `tools/trusted_gate_anchored.py` (206 new lines, added in commit A `0712989`); the declarations it escapes: `harness/runs/claim-064-p400c-capability-matrix/scope.txt` (no `tools/` line) and the CLAIMS.md CLAIM-064 scope cell (no `tools/` glob).
- **Reproduction / evidence:**
  - `git diff origin/main...HEAD --numstat` lists `tools/trusted_gate_anchored.py` — a byte-identical copy of `tools/trusted_gate.py` (both sha256 `82edf12b…bcc38`, equal to the trusted-base's driver). It exists at HEAD, NOT at origin/main.
  - `python3 harness/gate.py --slice claim-064-p400c-capability-matrix --diff origin/main --skip-suites` → exit 1 with `FAIL ARV-SCOPE-002: tools/trusted_gate_anchored.py outside the declared scope — scope breach (LAW-06)` and `FAIL ARV-CLM-002: CLAIM-064: the diff touches 'tools/trusted_gate_anchored.py' OUTSIDE its declared scope`.
  - The trusted gate (BASE machinery, the exact `harness-trusted` CI check) refuses identically. The `ARV-PRF-002`/`ARV-SEV-001` refusals in the same run are the EXPECTED pre-finalize codes (the proof sheet + sev.json land after this round); the two scope refusals are not — they persist to push time.
  - The repo's own history names this exact class: record 56 §1 — at #98 the anchored-driver file "entering the diff" was "the ARV-SEV-003 class, amended out of the re-bind commit"; STATE.md's CLAIM-063 row repeats it ("restored after the anchored-driver amendment caught locally pre-push"). Commit A re-committed the amended-out artifact.
  - LAW-05 impact: the file consumes 206 of the 400 source-line budget (382/400 = 95.5% — one small future change in this slice trips ARV-SIZE-002).
- **Why it is inert (mitigation, not absolution):** CI's anchor step `cp base/tools/trusted_gate.py tools/trusted_gate_anchored.py` (verify.yml S4b/S4c) overwrites the committed copy before any execution, and `harness/tests/test_trusted_gate.py` invokes `tools/trusted_gate.py` (not the anchored path) — so no suite or check depends on the committed file. It exists only so the LOCAL trusted-gate reproduction command can run without a manual `cp`.
- **Disposition recommendation: repair-in-slice** — drop the file from the tree (amend out before the push, the #98 precedent's own resolution; the workflow re-creates it, and the local reproduction can `cp` from the trusted-base exactly as CI does). No RED is required (no behavior or test changes — no suite pins the file); the diff digest re-binds at finalize per the digest-binds-LAST discipline. The alternative (widening scope.txt + the CLAIMS.md cell with an owner-referenced `tools/` line, LAW-07) buys a permanent duplicate of a protected tool for no mechanical gain — not recommended.

### F2 — P2 — the measured readiness row reports the LATEST attempt; `building`/`failed` over an existing current generation hides the still-readable extraction
- **Severity:** P2 — a bounded semantic gap in the new user-facing contract (routed).
- **Location:** `harness/capability.py:100-129` (`_measure`: `ORDER BY g.ordinal DESC LIMIT 1` + passages/coverage counted for THAT generation only).
- **Reproduction / evidence (live, scratch DB):** source sA extracted (ordinal 1 `current`, 5 passages); a new-key extract `--crash-at pre-commit` → states `current,building`; `measure` answers `state=building, generation_id=<ord-2>, passages=0, coverage=0.0` while the DB's current generation still serves its 5 passages (get-capture/resolve-anchor read it). Then the EXT-10-style planted RAISE → states `current,building,failed`; `measure` answers `state=failed, passages=0, coverage=0.0` — again with a fully readable current generation underneath. extract.py's own contract says "the previous current generation STAYS current".
- **Judgment:** every individual fact in the row is TRUE of the generation it names (`generation_id`/`ordinal` identify the latest attempt), so this is not a lying pin; but the user-facing readiness question ("can I read this source?") gets `failed`/`passages=0` while the source is readable, and the row has no field disclosing the serving current generation. The vocabulary cannot express "ready via generation N; latest attempt building/failed".
- **Disposition recommendation: route-to-slice** — minimal in-slice repair is a disclosure (module docstring + README: the row describes the LATEST generation attempt; a previous current generation may still serve reads); the fuller fix (a `current_generation_id`/`readable` field) belongs to P4-A/B, where the reader client consumes readiness.

### F3 — P2 — the `failed` readiness state has ZERO suite coverage, and the module docstring promises a field the row does not carry
- **Severity:** P2 — a claimed contract state that no pin protects + a doc-vs-implementation mismatch in the new module.
- **Location:** `harness/capability.py:29` (docstring: "failed … the named reason is in the row") vs `harness/capability.py:110-130` (no `fail_reason` in the measured row); `harness/tests/test_capability.py:218-244` (CAP-02 pins ready/not_extracted/building only — `failed` and `stale` unpinned).
- **Reproduction / evidence (live):** the planted-RAISE failure over sA → `measure` answers `state=failed` at exit 0 (the state itself works — verified only by THIS probe, not by any suite case); the row carries no `fail_reason` although `arv.extraction_generation.fail_reason` exists and extract.py surfaces it on same-key replay. The README (the user-facing doc) does NOT promise the reason — the over-promise is the module docstring's alone. `stale` is also unpinned but is structurally unreachable AND enforced (see F-note in §4 P3 — the ARV-CAP-005 trigger refuses even a superuser UPDATE of arv.source), disclosed as such; `failed` is reachable and reachable-only-unpinned.
- **Disposition recommendation: repair-in-slice, RED-first** — a CAP-07 pinning the failed state (the EXT-10 planted-RAISE fixture pattern already exists in test_extract.py) + either adding `fail_reason` to the failed row (fulfilling the docstring) or fixing the docstring's parenthetical. If the owner prefers, the pin can route to P4-A/B with F2 — but the docstring mismatch should be fixed in-slice either way.

### F4 — P3 — CAP-02's ready-row pin is single-corpus: a conditional hard-code would pass it (the derivation itself is honest — verified live)
- **Severity:** P3 — test-strength note; NOT a vacuous pass hiding a defect (the implementation verifiably derives).
- **Location:** `harness/tests/test_capability.py:86-91,218-244` (one ready corpus; `N_PASSAGES, COVERAGE = 3, 1.0`).
- **Reproduction / evidence:** the suite measures exactly ONE ready corpus. A `measure` that hard-codes `passages=3, coverage=1.0` whenever a generation exists (keeping the honest `not_extracted` branch for the no-generation case) would satisfy every CAP-02 assertion: m1 (ready) matches, m2 (not_extracted) takes the separate branch, m3 (building) asserts no passage facts. The out-of-suite probe (§4 P1/P2) proves the REAL implementation derives: a 5-paragraph corpus → `passages=5, coverage=1.0` (psql: count=5, sum=244, len=244); a leading-blank-line corpus → `passages=2, coverage=0.948718` (psql: 2|37, len=39). `generation_id`/`ordinal` ARE derivation-pinned (matched against the extract ack's own values).
- **Disposition recommendation:** accept-with-note (this round's live probe is the discriminator) or fold a second-corpus pin into F3's RED when it lands.

### F5 — P3 — run-01..05 record commit `3c2aa2c`, a tree where the recorded commands cannot pass
- **Severity:** P3 — evidence-labeling note (established convention, finalize must re-bind).
- **Location:** `harness/runs/claim-064-p400c-capability-matrix/run-01..05.json` (`"commit": "3c2aa2c…"` for `test_capability.py` exit 0 ×3 and `make verify` exit 0 ×2).
- **Reproduction / evidence:** at 3c2aa2c's TREE `harness/capability.py` does not exist (verified: `git cat-file -e 3c2aa2c:harness/capability.py` fails), so the CAP suite exits 1 there — the runs were taken on the GREEN working tree (570a23c's content) with HEAD still at 3c2aa2c. This matches the merged-slice convention (claim-063's run-01 records `42c9441`, its red-record commit; claim-062's run-11 records `d672ec6`) and the finalize's digest-binds-LAST re-record discipline (the claim-058 precedent). My independent CAP run reproduced the recorded output byte-identically (sha256 `ced89b21…`), so the measurements themselves are genuine.
- **Disposition recommendation:** accept-with-note — the finalize MUST re-record the measured set at the final content head (as claim-058's re-bind did), especially after F1's repair moves the head.

### F6 — P3 — record 56 §2 names "the timing class" among the measured facts; no timing exists in the delivered row
- **Severity:** P3 — process-record precision.
- **Location:** `context/extracted/56-P400C-CAPABILITY-MATRIX.md:13` ("the passage count, the coverage, the timing class").
- **Evidence:** the measure row carries state/passages/coverage/generation_id/ordinal/extractor/media_type/api_version — no timing. The binding CLAIMS.md row does NOT promise timing; record 56 is a D-022 process artifact ("NOT owner intent, outranks nothing").
- **Disposition recommendation:** accept-with-note, or a one-line record correction at finalize.

### F7 — P3 — the unreadable-blob class answers `state=ready, passages=N, coverage=0.0` (disclosed in a code comment only)
- **Severity:** P3 — polish on an extreme edge (rig-class blob-store corruption).
- **Location:** `harness/capability.py:123-128`.
- **Reproduction / evidence (live):** with sB's blob file deleted, then tampered: `measure` answers `state=ready, passages=2, coverage=0.0` at exit 0 (the except-branch: "the counts stand, the coverage honestly 0"); with the blob restored: `coverage=0.948718`. A "ready, 2 passages, 0% covered" row reads self-contradictory; the class is disclosed only in the code comment, not the README. The extract/resolution paths name this class (ARV-CAP-004/ARV-BLOB-002/003) — measure keeps answering at exit 0 by design.
- **Disposition recommendation:** accept-with-note (or a README sentence in F2's disclosure pass).

### What was verified CLEAN (no finding): the no-oracle on the new surface (absent == cross-owner, template-level AND stderr byte-equality — §4 P4); matrix/surfaces need no owner and leak nothing; the per-family `_refuse` hints are correct on every arm with the P4-00b template equality intact per arm (§4 P5) and NO suite anywhere asserted the old capture-arm hint text (grep: zero hits in harness/tests/); every README-documented form is TRUE to the actual output (§4 P6 — list header/markers, --limit/--after + ARV-QRY-004 bounds incl. 0/1001/non-integer/non-id, empty-library two-line answer, versioned search header, the matrix/measure examples key-for-key); the RED chain is genuine (binding sha verified at HEAD and at 2f4d3ef, the RED reproduced live exit 1, capability.py absent at the RED commit, gate TESTS registration honest); the "stale structurally unreachable" claim is TRUE and ENFORCED (the ARV-CAP-005 append-only trigger refuses a superuser UPDATE of arv.source — live-probed); the shared-machinery imports are real (API_VERSION from commands.py, `_read`/`_refuse` from query.py — no duplication); the five-area re-derivation (AGENTS/STATE/PLAN/WORKLOG/record 56) is consistent with the diff and with CLAIMS.md.

---

## 3. Verdict

**DISPOSITION: BLOCKED** — one open P1 (F1: the undeclared `tools/trusted_gate_anchored.py` breaches the declared scope; the candidate gate AND the trusted gate refuse the slice as it stands), plus the routed P2s (F2 readiness semantics over a current generation; F3 the unpinned `failed` state + the docstring's promised `fail_reason`). F1's repair is mechanical (amend the file out — the #98 precedent's own resolution); F2/F3 are small and in-slice-repairable or explicitly routable to P4-A/B. Everything else the slice claims was verified delivered and honest at the real boundary.

---

## 4. The adversarial probe list (all on my own scratch DB, dropped after)

| # | Probe | Observed |
|---|---|---|
| P1 | **MEASURED derivation, different corpus**: 5-paragraph corpus → extract → measure vs direct psql counts of `arv.passage` | `passages=5, coverage=1.0, ordinal=1, state=ready`; psql count=5, sum(end-start)=244, len(text)=244 — DERIVED, not hard-coded (a hard-code of the suite's 3/1.0 would have answered 3) |
| P2 | **Coverage edges**: leading blank-line prefix; single character; whitespace-only; Markdown heading + trailing heading | leading-blank: `passages=2, coverage=0.948718` (<1.0, honest — the tiler's skipped prefix shows in the fraction; psql 2\|37/39); single char "x": 1 passage, coverage 1.0; whitespace-only: extract refuses ARV-EXT-001 (exit 1), `measure` answers the typed `not_extracted, passages=0, coverage=0.0` at exit 0 (never silence); heading corpus: 2 passages (attach-forward + trailing-heading-own), coverage 1.0, psql 59/59 |
| P3 | **Readiness states**: `building` via `--crash-at pre-commit` (fresh source); `building` and `failed` OVER an existing current generation (new-key crash; EXT-10-style planted RAISE); `not_extracted` | fresh crash: exit 2, `state=building, passages=0, ordinal=1`; over-current crash: states `current,building`, measure says `building/0/0.0` (→ F2); planted failure: exit 1 ARV-EXT-003, states `current,building,failed`, measure says `failed/0/0.0`, `fail_reason` NOT in the row (→ F2/F3); the current generation keeps its 5 passages throughout |
| P4 | **No-oracle on the NEW surface**: `measure --owner B --source <A's>` vs absent uuid | both exit 1; template equality after id-substitution TRUE; stderr byte-equal (both empty); `matrix`/`surfaces` need no owner and print only the declared registries (no owner data reachable) |
| P4b | **Unreadable-blob class**: delete then tamper sB's blob, measure, restore | missing → `ready, passages=2, coverage=0.0`; tampered → same; restored → `0.948718` (→ F7) |
| P5 | **The `_refuse` per-family hints + per-arm no-oracle**: get-note/get-bookmark/get-capture/get-source/resolve-anchor/get-history, absent vs cross-owner | hints: list-notes / list-bookmarks / list-captures / source-honest ("the import ack's result_ref") / anchor-honest / capture (history) — all correct; template equality absent==cross-owner TRUE on every arm; stderr equal; grep: NO suite asserts the old capture-arm wording on the note/bookmark arms |
| P6 | **README truth**: the documented list-notes shapes, bounds, search header, matrix/measure examples | `# api_version=1` opener + `# more=false` closer; `--limit 50` + `--after <last-id>` work; limit 0/1001/abc and `--after not-an-id` all refuse ARV-QRY-004; empty library = exactly the two lines; search header `# api_version=1 kind|entity_id|revision|matched_terms`; the README's matrix and measure examples match the real outputs key-for-key |
| P7 | **LAW-05 recount** (numstat) | source: 4 files, 382 lines (capability 157 + query 18 + gate 1 + **trusted_gate_anchored 206**) ≤ 8/400 — passes only WITH the undeclared file counted (95.5% of budget); test: 1 file, 335 lines ≤ 6/800; migrations 0 ≤ 1 |
| P8 | **The RED chain**: red-01.txt, sha256 binding, live reproduction | red-01.txt carries the observed exit-1 ARV-TEST-000; `binding_sha256 == current_sha256 == sha(test at HEAD) == sha(test at 2f4d3ef)` = `5b959d2c…`; `git archive 2f4d3ef` → suite exits 1 ARV-TEST-000 (reproduced); capability.py absent at 2f4d3ef; red-records.json binding names an existent commit |
| P9 | **The stale claim**: superuser `UPDATE arv.source SET digest=…` | REFUSED by the ARV-CAP-005 append-only trigger even as postgres — "structurally unreachable" is enforced, not merely asserted; the stale branch stays defensive dead code as disclosed |
| P10 | **Scope/gate**: candidate PR-mode gate + the trusted anchored gate over `origin/main...HEAD` | both refuse ARV-SCOPE-002 + ARV-CLM-002 on `tools/trusted_gate_anchored.py` (+ the expected pre-finalize ARV-PRF-002/ARV-SEV-001) — F1 |

*— agent-ee8ed9dd, 2026-11-06T06:01Z. Scratch DB `arv_sevc_30968_944315085` dropped; temp trees removed; no repository source file modified; nothing committed or pushed.*
