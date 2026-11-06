# SEV round-2 — CLAIM-067 / P4-A slice three (the EPUB intake — FINAL)

- **Agent label:** agent-9b3f1d24
- **Date:** 2026-11-06T18:43:49Z (UTC)
- **Slice:** CLAIM-067 — P4-A slice three: the EPUB intake (the zip/XHTML adapter by the stdlib path), branch `slice/claim-067-p4a-epub-intake`
- **Base:** `269921ac` (origin/main, CLAIM-066's merged head) — **Head:** `b670997`
- **Commit chain:** `6e18c51` (commit A: post-#101 reconciliation + CLAIM-067 open + record 59) → `319bed5` (the RED: test_epub.py EPB-01..05) → `34a82e8` (the typed red record bound to 319bed5) → `5cbd3b4` (the GREEN: the adapter + the read_text routing) → `8d14aad` (the CLAIMS registry repair) → `d84b202` (record 59's STATUS banner) → `b670997` (the SEV round-1 repairs: the P1 routing + the EPB-06 pin + the P2 scope completion)

## 1. What I ran

| # | What | Result |
|---|------|--------|
| 1 | Round-1 report read (sev-round-1.md, agent-5d3d9a17: P1 + P2 repaired at b670997, two P3s routed) + `git log`/`git diff --name-only 269921ac...HEAD` (24 paths) | read, every finding re-verified at HEAD |
| 2 | `python3 harness/tests/test_epub.py` | **GREEN 6/6** (EPB-01..06, incl. the new EPB-06 pin), exit 0 |
| 3 | `python3 harness/tests/test_keyword_index.py` | **GREEN 10/10** (KWR-01..10 — the rebuild's blast radius), exit 0 |
| 4 | `python3 harness/tests/test_extract.py` | **GREEN 17/17** (EXT-01..17 — the routing's blast radius), exit 0 |
| 5 | Red-records chain: sha256(test_epub.py) at HEAD / at `319bed5` / vs `current_sha256` / vs the amendments' `new_sha256`; `git diff d84b202..b670997 -- harness/tests/test_epub.py` additivity | all exact, additive (§2.3) |
| 6 | **RED replay**: `git worktree` at `d84b202` (the pre-repair tree) + HEAD's test_epub.py copied in → run | **exit 1 — FAIL EPB-06, EPB-01..05 PASS** — the round-1 P1 defect (the epub bookmark vanishing from search after `rebuild_keyword_index`) reproduced live at the pre-repair tree; worktree removed after |
| 7 | Spot-checks on my own scratch DB `arv_sev2r2_12648_990521260` (my own zipfile-built EPUB, migrated, driven through the CLI; **dropped after** — zero `arv_%` DBs left) | see §4 (all PASS) |
| 8 | Scope: the 24 diff paths vs `scope.txt` + the CLAIMS.md CLAIM-067 open row | **24/24 declared, both homes** (§2.2) |
| 9 | Sweeps: TODO/FIXME/placeholder in the diff's files; `blob.get(...).decode(...)` and every `.decode(` site in `harness/*.py` judged for epub visibility | zero in the diff; **zero second decode paths that can see an epub source** (§2.4) |

## 2. Repair verification (P1/P2 + the routed P3s)

### 2.1 P1 — the rebuild's bookmark arm routed (round-1 F1) — **REPAIRED, VERIFIED LIVE**

- **The code at HEAD** (commands.py:1370–1392): the bookmark arm's SELECT now selects `s.media_type` and **joins `arv.source s ON s.id = a.source_id AND s.owner_scope = a.owner_scope`** (commands.py:1373–1376), and the span re-derives as `src_text = read_text(jr["media_type"], jr["source_digest"])` (commands.py:1387) — the ONE read_text home, the same routing every other text-access site carries. The raw `blob.get(...).decode("utf-8")` is gone from the arm; the `except (UnicodeDecodeError, KeyError, _FmtRefusal)` backstop (commands.py:1388) is the honest corruption-class degrade (the anchor's own recorded context windows still index), matching the pre-slice shape.
- **The pin**: EPB-06 (test_epub.py, additive per the typed amendment) — an epub-anchored bookmark searchable at creation AND after `rebuild_keyword_index`, the source's own row the control. **GREEN at HEAD** (suite 6/6, exit 0).
- **The RED observed pre-repair** (my own replay, run #6): at `d84b202` + HEAD's test file → `FAIL EPB-06 … EPUB SUITE RED — 1 open: EPB-06`, exit 1 — the vanish reproduced exactly as round-1's probe demonstrated.
- **Live spot-check** (§4a): my own epub, my own bookmark, rebuild, search — the bookmark survives, pre==post exactly.

### 2.2 P2 — the undeclared diff path (round-1 F2) — **REPAIRED**

`context/extracted/58-P4A-POSITION-SURFACE.md` is now declared in **both homes**: scope.txt:28 (`context/extracted/58-P4A-POSITION-SURFACE.md D-042`) and the CLAIMS.md CLAIM-067 open row's scope cell. Full re-check of the 24 diff paths against both homes: AGENTS.md, CLAIMS.md, PLAN.md, STATE.md, context/WORKLOG.md, context/extracted/58-…, context/extracted/59-…, harness/{capability,commands,extract,formats,gate}.py, harness/red-records.json, harness/tests/test_epub.py (all individually declared) + the runs-dir glob `harness/runs/claim-067-p4a-epub-intake` (covers red-01.txt, run-01..08.json, scope.txt, sev-round-1.md). **Every diff path declared.**

### 2.3 The red-records chain for test_epub.py — **EXACT AT EVERY LINK**

- `sha256(test_epub.py @ HEAD b670997) = 8baf7471cf141bc6a9fb8a5905cfaeb9df318a888684c41d7437fe8c9bd5d450` == the record's `current_sha256` == the LAST amendment's `new_sha256`.
- `sha256(git show 319bed5:…) = 61aaf0b7b522eb9ffdf9616b6d398e32b165fc2187efef67fcf49f4703012f5a` == `binding_sha256`, with `binding_commit = 319bed55…` (the RED commit, verified by my own `git show | sha256sum`).
- The amendment chain: `61aaf0b7 → 9c60fa11` (the two implementation-cycle amendments round-1 verified) `→ 8baf7471` (the EPB-06 pin).
- **Additivity**: `git diff d84b202..b670997 -- harness/tests/test_epub.py` shows ONLY the EPB-06 docstring entry + the EPB-06 check block + the banner widening "EPB-01..05"→"EPB-01..06". No assertion removed, weakened, or reworded elsewhere. **COHERENT, ADDITIVE.**

### 2.4 The one-home law re-swept at HEAD

`blob.get(...).decode(...)` across `harness/*.py`: **zero matches** (round-1's single genuine survivor was commands.py:1381 — now the routed arm). Every remaining `.decode(` site judged for epub-source visibility: formats.py:131/274/324 (the read_text home itself — excepted), commands.py:1111 (a local `--content-file` argument read, never a stored arv.source blob), migrate.py:426/440 (migration SQL file bytes, `"replace"`), proofsheet.py:136 + scope.py:65 + sev.py:131/246 (run-record JSON / subprocess output), test fixtures. **No second decode path can see an epub source.** The blast-radius suites (run #3, #4) are GREEN — the routing changed nothing it should not have.

### 2.5 The routed P3s (round-1 F3/F4) — **ROUTED, NOT SILENTLY DROPPED**

Both routed by b670997's commit message to the **notverified at the finalize** (the CLAIM-066 precedent: notverified.txt lands with the finalize commit): (a) the decompression bound in the EPUB walk (an 80 MB chapter materializes in ~0.4 s — the hardening note under Q8's synthetic-corpus gate), (b) the partial-spine silent truncation (formats.py:261 — a spine with one missing href and one present derives the partial text rather than refusing; the epub family's honest-boundary note). **Obligation carried forward, not an open finding**: the finalize's notverified.txt MUST carry both.

## 3. Findings

**zero open P0/P1/P2/P3.**

No new findings surfaced by the round-2 sweep: no TODO/FIXME/placeholder in the diff's files (the only grep hits are pre-existing vocabulary in non-diff files — migrate.py's SQL-lexer comments, sev.py/test_sev.py's ARV-SEV-006 placeholder class, known-bad cases); the scope law holds at 24/24 in both homes; the amendments are additive; the repair commit touches only declared paths (its 14-file stat ⊆ the scope); the working tree is clean of source modifications by this review.

## 4. Spot-checks (scratch DB `arv_sev2r2_12648_990521260`, dropped after; zero `arv_%` DBs remain)

1. **(a) The epub bookmark across the rebuild — the P1 repair live.** My own EPUB (spine `[ch2, ch1]`, zip writes ch1 first), imported `--media-type application/epub+zip`; a bookmark anchored over `meridian` (derived-view offsets via `formats.read_text`); search "meridian" BEFORE: `[bookmark|<bm>, source|<sid>]`; `rebuild_keyword_index` exit 0; search AFTER: **the identical two rows** (`bookmark|<bm>|1|1`, `source|<sid>|1|1`) — pre==post exactly. **PASS — the vanish is closed.**
2. **(b) The text/plain control — unchanged.** A text/plain source with a `kumquat` bookmark: search before == search after the same rebuild, both rows present, exact restore (the KWR-05 shape). **PASS.**
3. **(c) The spine-order probe.** Derived text = `'Bravo second chapter text meridian two.\n\nAlfa first chapter text zephyr one.\n'` — the SPINE's order (ch2 first) wins over the zip's write order (ch1 written first). **PASS.**
4. **The RED replay** (§2.1): the pre-repair tree fails exactly the new pin and nothing else — the repair is pinned to the defect it claims, never a vacuous green.

## 5. Disposition

**PASS** — zero open P0/P1/P2/P3.

- Round-1's P1 (the rebuild's raw-decode bookmark arm) is repaired at HEAD, pinned by the additive EPB-06 (RED observed by me at the pre-repair tree, GREEN at HEAD, live-verified on my own rig), and the one-home law re-swept clean.
- Round-1's P2 (the undeclared record-58 path) is repaired in both homes; every diff path of the slice is declared.
- The two routed P3s remain an **obligation on the finalize**: notverified.txt must carry the decompression-bound hardening note and the partial-spine honest-boundary note.
- The slice's claims hold under the final round's fire: the third registry row, the stdlib-only walk (spine order honored), the XHTML strip, the typed FMT-004/005/006 refusals with staged bytes, the read_text routing at every text-access site (now including the rebuild's bookmark arm), the exact red-records chain, and the blast-radius suites all GREEN.

*Review hygiene: my only writes were the scratch DB (dropped, verified gone), /tmp (the spot-check script, the RED-replay worktree `/tmp/sev2red` — added and removed; `/tmp/trusted-base` in `git worktree list` pre-existed this review and was left untouched), and this report. No repo source modified, committed, or pushed; `git status` clean.*
