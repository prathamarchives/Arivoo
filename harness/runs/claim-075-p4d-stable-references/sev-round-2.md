# CLAIM-075 — SEV round 2 (the repair verification)

- **Agent:** independent fresh-context SEV reviewer (Task SEV-075-R2; neither the slice author nor the round-1 repairer)
- **Date:** 2026-11-11 10:17 UTC (rig live at 127.0.0.1:5433 the whole round)
- **Round:** 2 (the round-1 repair verified live by fresh eyes)
- **Base:** `4a750db` (origin/main, the PR #109 merge)
- **Head:** `d2ed6b3` (`slice/claim-075-p4d-stable-references`, the SEV round-1 repair commit; full chain base → `b0efb68` → `37917ec` RED → `114231b` binding → `e7aac7d` amendment 1 → `6fde990` GREEN → `d2ed6b3` the repair)
- **Method:** 46 live probes on my own scratch rigs (`arv_sev75r2_*`, both dropped — script `/home/z/my-project/scripts/sev75r2_probe.py` + a 3-probe follow-up, log `sev75r2-log.txt`); the reference suite run once by me independently (GREEN, exit 0); ~12 static/git checks. No writes inside the repo other than this report; nothing committed; every scratch DB I created dropped.

## §1 Verdict

**PASS.** Both repaired classes verified CLOSED live; the boundary behavior exact; no new P0/P1/P2 introduced by the repair; the routing honest; the amendment chain typed and tree-verified. **Zero new findings.**

The PASS conditions, each satisfied: (1) F-075-1's class — the 5000-, 4301-, 4300- and 19-digit all-digits pins ALL answer the typed `FAIL ARV-REF-002` at exit 1 with ZERO tracebacks on stderr, while the 18-digit pin still PARSES (dangling ARV-REF-001 on absent and live targets — never malformed); (2) F-075-2's class — the trailing-newline/trailing-`x`/trailing-space uuid forms all answer ARV-REF-002, never an untyped ARV-QRY-002; (3) no plausible-pin regression — @1..@3 on revised highlight/note/journal_block answer historical/current exactly as before, and the routed/accepted round-1 behaviors (unicode-digit and leading-zero normalization, the uppercase-hex echo) are unchanged; (4) `git diff 4a750db...HEAD -- harness/commands.py` is EMPTY — the substrate untouched; the repair diff is exactly the four declared files; (5) red-records.json carries THREE amendments, prior→new contiguous, each new hash verified against the actual commit tree (RED `9ad1de29` → `b105e84a` → GREEN `7d913c81` → HEAD `8363ccd0`), `binding_commit` unchanged at `37917ec`.

## §2 The repair verification

The repair commit `d2ed6b3` touches exactly: `harness/query.py` (the `\Z` anchor + the 18-length bound before `int()` + the updated repair hint), `harness/red-records.json` (current_sha256 + the third amendment), `harness/tests/test_references.py` (+2 battery entries), and this round's predecessor `sev-round-1.md` — nothing else (`git show HEAD --name-only`).

**F-075-1 — the all-digits oversize pin (the P2).** All probes on my own migrated scratch DB, live target `note:<n1>` (revisions 1..3):

```
[001] note:<n1>@'1'*5000  -> rc=1, FAIL ARV-REF-002: … is malformed — the pinned revision
                             must be a plausible revision number (digits, at most 18, >= 1);
                             stderr: NO Traceback
[002] note:<n1>@'1'*4301  -> rc=1, FAIL ARV-REF-002 (the exact CPython crash boundary) — no traceback
[003] note:<n1>@'1'*4300  -> rc=1, FAIL ARV-REF-002 (below the interpreter limit, above the 18 bound)
[004] note:<n1>@'1'*19    -> rc=1, FAIL ARV-REF-002 (the bound's upper edge)
[005] the repair-hint line names "at most 18" (the updated text present)
```

**The boundary is exact, not narrowed:** an 18-digit pin still PARSES —

```
[006] note:<n1>@'1'*18               -> rc=1, FAIL ARV-REF-001 (parses; the revision is absent
                                        on the LIVE target — the no-oracle dangling class, NOT malformed)
[007] note:<absent>@123456789012345678 -> rc=1, FAIL ARV-REF-001 (parses; absent id, same class)
[008] note:<n1>@000000000000000003   -> rc=0, current, revision 3 (an 18-CHAR leading-zero pin
                                        normalizes to 3 — the substrate's F-075-3 law intact AT the bound)
```

**F-075-2 — the trailing-newline uuid (the P3).** Real `\n` in the argv value, plus the sibling forms:

```
[009] --ref "work:<work1>\n"  -> rc=1, FAIL ARV-REF-002 (… the target id is not a UUID); no ARV-QRY-002
[010] --ref "work:<work1>x"   -> rc=1, FAIL ARV-REF-002
[011] --ref "work:<work1> "   -> rc=1, FAIL ARV-REF-002
[012] --ref "\nwork:<work1>"  -> rc=1, FAIL ARV-REF-002 (the kind '\nwork' — bonus: the ^ start holds too)
```

Every refusal above: exit 1, the `FAIL ARV-REF-002` line on stdout, ZERO JSON answer lines, ZERO `Traceback` on stderr.

**No plausible-pin regression (the length bound did not narrow any legal pin):**

```
[013] highlight:<hl1>@1  -> historical, pinned_revision 1, current_revision 3, resolved_ref …@1
[014] highlight:<hl1>@2  -> historical 2/3        [015] highlight:<hl1>@3 -> current, revision 3
[016] note:<n1>@1        -> historical 1/3        [017] note:<n1>@3       -> current, revision 3
[018] journal_block:<jb>@1 -> historical 1/2      [019] journal_block:<jb>@2 -> current, revision 2
[020] note:<n1>@0 / [021] @x / [022] @-1 -> all FAIL ARV-REF-002 (unchanged)
```

**The routed/accepted round-1 behaviors unchanged by the repair** (follow-up rig): `note:<id>@١` (arabic-indic one) → historical pinned 1; `@0001` → historical pinned 1 (F-075-3, the substrate law, routed); the uppercase-hex uuid → current with the case-preserved echo (F-075-4, owner-accepted debt). F-075-5's surface (the resolve-anchor arm) is untouched by the repair diff — the three query.py hunks are the regex, `_ref_parse`, and `_ref_refuse_malformed` only.

**The suite strengtheners are real:** `python3 harness/tests/test_references.py` run once by me → REF-01..06 all PASS, `REFERENCE SUITE GREEN`, exit 0. The suite source carries both new battery entries (lines 646–647): `f"note:{n1}@" + "1" * 5000` (annotated as the F-075-1 class) and `f"work:{work1}\n"` (annotated as the F-075-2 class), both inside the REF-06 hostile loop asserting ARV-REF-002 with zero answer lines.

**The routing honesty (static):** `git diff 4a750db...HEAD -- harness/commands.py` → EMPTY (0 lines — the substrate's own `_UUID_RE` copy at commands.py is LANDED and untouched, its `$`-form repair correctly deferred to the routed family-wide slice). The full slice diff since base is 15 paths (round-1's 14 + `sev-round-1.md`), every path inside scope.txt's declarations (the runs-directory declaration covers the report files).

**The typed amendment (static):** `red-records.json['harness/tests/test_references.py']` shows THREE amendments, contiguous prior→new, and I verified each hash against the actual git trees: binding_sha256 `9ad1de29…` = the suite at the RED commit `37917ec`; amendment 2's new `7d913c81…` = the suite at the GREEN `6fde990`; amendment 3's new `8363ccd0…` = the suite at HEAD `d2ed6b3` = the worktree file's sha256; `binding_commit` unchanged at `37917ec…`; amend1.prior == binding, amend2.prior == amend1.new, amend3.prior == amend2.new. The RED→GREEN discipline is intact (nothing implementation-shaped precedes the RED; the repair is additive on the GREEN).

## §3 The spot-regression battery

On the same scratch rig (`arv_sev75r2_*`, migrated, fixtures built through the commands surface), 20 probes re-observing the six states:

- **current:** `work:` (no revision key, `resolved_ref` present), `source:`, `anchor:` (current + `generation_id` — the compose proof), `highlight:`/`note:` unpinned at derived max (3), `journal_block:`/`bookmark:` unpinned (2) — all ONE JSON line, `api_version: 1`, exit 0.
- **historical:** `highlight:<hl1>@1` → pinned 1 / current 3, served exactly as pinned (§2 [013]).
- **tombstoned:** a tombstoned highlight and note, each unpinned AND pinned (@1) → `{"kind": …, "state": "tombstoned"}` with NO revision, NO resolved_ref, NO content.
- **unavailable:** the never-extracted source's anchor → `state: unavailable`, `cause: no-current-generation`, no resolved_ref.
- **ambiguous:** the ANC-05 drift fixture replicated (repeated 25-char blocks, the planted non-covering tiling [0,7)+[17,len)) → `state: ambiguous`, `evidence_hits: 2`.
- **purged (beats tombstoned):** the tombstoned+purged highlight → `purged` unpinned AND pinned; the live purged note → `purged` unpinned AND pinned; the purged answers carry no revision/resolved_ref.
- **the no-oracle, raw bytes:** A-asks-B's-real-note vs A-asks-the-absent-uuid, and the same for work — stdout+stderr byte-EQUAL after id normalization (359/359 bytes, note), both exit 1, `FAIL ARV-REF-001`.
- **the command_log law:** count 26 before the entire battery → 26 after (the resolution never writes).
- **the state set:** every state my battery observed is EXACTLY the closed six `{ambiguous, current, historical, purged, tombstoned, unavailable}`.

## §4 Findings

**New findings this round: NONE.** No new P0/P1/P2/P3 introduced by the repair; every observed behavior conforms to the declared contract.

The round-1 dispositions, restated:

- **F-075-1 (P2)** — repaired at `d2ed6b3` and VERIFIED CLOSED live this round (§2 probes 001–008: the oversize all-digits pins all the typed ARV-REF-002, zero tracebacks; the 18-digit pin still parses into the dangling class).
- **F-075-2 (P3)** — repaired at `d2ed6b3` and VERIFIED CLOSED live this round (§2 probes 009–012: the trailing-newline uuid and siblings the typed ARV-REF-002, never the untyped ARV-QRY-002).
- **F-075-3 (P3)** — routed (substrate grammar owner); behavior re-observed unchanged (`@١` and `@0001` still normalize to pin 1 — the substrate's isdigit law, not narrowed by the 18 bound).
- **F-075-4 (P3)** — owner-accepted-debt; behavior re-observed unchanged (the uppercase-hex uuid resolves with the case-preserved echo).
- **F-075-5 (P3)** — routed to D-011's governed-purge slice; the resolve-anchor arm untouched by the repair diff (statically confirmed — no re-probe this round).

## §5 The honest limits

- **Round-2 scope:** I verified the REPAIR and spot-regressed the six states; I did not re-run round-1's full 108-probe battery (the RLS cross-owner purge scoping, the 20-form hostile battery beyond the repair classes, the compose agreement across four anchor verdict classes, and the substrate CHECK probes rest on round-1's documentation plus this round's spot checks and the suite's own REF-01..06).
- **The RED was not re-executed from the archived tree this round** — round-1 reproduced it live; this round I verified the binding chain's hashes against the actual commit trees instead (the binding_commit is unchanged, so the round-1 reproduction remains the evidence).
- **`make verify` was NOT run by me**; the suite run is `test_references.py` alone.
- **No concurrency or performance probes** (unchanged from round 1).
- **Rig hygiene observation (not a slice finding):** a foreign leftover scratch DB `arv_p303b_13612_388705039` (8 command_log rows) predating this round sits on the rig — not created by me, left in place; both of my scratch DBs (`arv_sev75r2_*`, `arv_sev75r2b_*`) and the suite's own `p4d1*` DB are dropped (verified via `pg_database` listing).
- **The untracked run-record JSONs** (run-01..08) remain on disk uncommitted at HEAD — the measured-set commit is the declared next step after this SEV, per the chain's own ordering; I only confirmed their presence, not their contents, this round.
- My probe scripts and logs live OUTSIDE the repo (`/home/z/my-project/scripts/sev75r2_probe.py`, `sev75r2-log.txt`); the only write inside the repo is this report file; nothing was committed.
