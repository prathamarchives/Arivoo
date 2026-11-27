# SEV round-1 — slice claim-102-sync-export-purge (Workstream 6; INT-169)

- reviewer: fresh-context verification (the 097..102 protocol; the round-1
  probe battery at /home/z/my-project/scripts/sev102_probe.py — nothing
  reused from the builder's battery; the builder's repairs re-probed live)
- head at review: c93b742 (the round-2 repair head)
- base: a17f0b5 (origin/main, the PR #143 merge)
- disposition: PASS — zero open findings; six findings repaired in-slice
  (one P1, three P2, two round-2 defect-class), every repair re-probed live

## The probe battery (50 probes, 50 PASS)

| Group | Probes | Observed |
|---|---|---|
| G (the amended rejectors) | G1 (7/7 sub-cases) | the seven amended trigger rejectors keep the ORIGINAL named codes + wording byte-for-byte (EV-001, EV-002, SYN-007, POS-005, SES-006, JNL-006, RLS-006/007) — only the purge-authorized window is new |
| A (the no-oracle law) | A1, A2, A2-SAMEMESSAGE, A3-ALTERNATION | the absent target and the cross-owner target answer the IDENTICAL ARV-PRG-003 message (never 403, never an oracle); the second purge answers ARV-PRG-004 (the ledger-first check order — the permanence record outranks the existence read) |
| A4/A5 (precedence + all-or-nothing) | A4-SETUP, A4-SEEDS2TREE, A4-CAPTUREPRECEDENCE, A5-INJECT, A5-ALLORNOTHING, A5-RETRY | a capture whose source is ledger-purged refuses ARV-PRG-005; an injected cascade abort rolls the LEDGER row back too (no half-purge state exists); after the abort lifts, the same purge completes cleanly |
| B (the authority wall) | B1-MARKERDELETE, B2-GRANTS, B3-SUPERUSERTRIGGER | a plain arv_app session CANNOT delete content even with arv.purge_in_progress set (the grants wall — zero content-table DELETE grants); a superuser DELETE still meets the ARMED ARV-CAP-005 trigger (the marker is definer-frame only) |
| C (the cascades) | C1-SOURCECASCADE, C3-BOOKMARKCASCADE, C4-ANCHORCASCADE, C5-WORKAFTER, C5-WORKFRESH, C6-JOURNALBLOCK, C7-READINGLIST, C6-DBSIDE | the source purge drops the WHOLE tree (anchors/captures/lifecycles/keywords/positions/sessions/generations/passages/bound-journal/members/inbound-refs) keeping work+free entities; the work purge recurses (a ledger row per source) and completes over ledgered sources (the skip law); journal_block + reading_list purges COMPLETE (the 0021 CHECK amendment) |
| D/E (the route laws) | D1, D2, D2B, E1, E2, E3, E4, E5, E5B, E6, E7 | the ledger list's isolation + cursor; the purge DTO's vocabulary/injection shapes; hex-invalid uuid-SHAPED ids refuse 422; quote-bearing cursors refuse the typed 422 (never repr()'s 500, never the cast's) |

## The findings (all repaired in-slice, re-probed live)

| ID | Sev | Finding | Repair |
|---|---|---|---|
| SEV102-C6/C7 | P1 | 0013's ledger CHECK admitted only the six P3-09 families; the journal_block/reading_list ledger INSERT violated it and the whole erasure rolled back — two advertised purge kinds could never succeed (500s) | 0021 amends the CHECK to the eight-family vocabulary; ARV-API-206 + probes C6/C7/C6-DBSIDE prove completion |
| SEV102-E3 | P2 | a hex-invalid uuid-SHAPED entity_id (36 chars, 4 dashes) passed the route's shape check and died at the ::uuid cast — 500, not a client-actionable 422 | the uuid regex law at the boundary; ARV-API-203 |
| SEV102-E5 | P2 | the purge-ledger keyset cursor interpolated via Python repr() — an embedded quote switched repr to double quotes and crashed the statement (500) | the ONE _q() literal home + the cursor's uuid-half validation; ARV-API-204 |
| SEV102-C1/C7-r2 | P2 (round-2) | the reading_list_member/reading_list rejectors (RLS-007/RLS-006) were not amended for the purge window — the source cascade's membership DELETE and the reading-list purge met the armed guards (500s) | both rejectors join the purge-authorized window (original codes byte-for-byte); probes C1/C7 PASS |
| SEV102-C5-WORKAFTER-r2 | P2 (round-2) | the work purge recursed into LEDGERED sources and the nested call refused ARV-PRG-004, aborting the whole work purge (500) | the recursion skips ledgered sources (the permanence record outranks the recursion); the residue drops in the work's own epilogue cascade |
| SEV102-C5-WORKFRESH-r2 | P2 (round-2) | the procedure's epilogue `SET LOCAL arv.purge_in_progress = 'off'` clobbered an enclosing frame's marker — the nested source call switched it off and the outer work DELETE met the armed CAP-005 (500) | NO epilogue: the marker is transaction-scoped, expiring at COMMIT/ROLLBACK — on means on for the whole transaction |

## The v-model wings

- component: the routes battery ARV-API-001..207 GREEN at the head (223 PASS);
  the probe battery 50/50 PASS at the head
- integration: the substrate suites re-observed GREEN after every 0021
  amendment (migrations, substrate, kernel, sync SYN-01..23, export EXP-01..15,
  highlight, bookmark, note, note-reference, journal, reading-list,
  agent-access, recovery-contract RCW-01..08)
- system: verify_canonical_layer GREEN (151 intents); the §11.2 route table
  COMPLETE (Workstream 6 served); D-011's erasure contract now machine-backed
- validation: the SYS trace — SYS-02 (the governed purge's erasure + the
  audit row), SYS-08 (the sync delivery over the outbox contract), SYS-10
  (the export/restore + the ledger reconciliation, the ledger row SURVIVES
  the restore and the ledgered source does NOT resurrect)

## Not verified (carried to the sheet)

- the five PR-head CI checks and this PR's D-042 review (observed after the PR opens)
- a live Supabase-issued token; uvicorn over a real socket; the deployed surface (Workstream 10)
- the multi-database restore topology through the route; the desktop-over-HTTP client (Q19)
- the 0021 machine on the REMOTE project (the guarded migration act — the Supabase
  credential never provided to this session)
- the blob erasure sweep (recover.py's own machine — the purge route registers the
  erasure; the unreferenced-blob sweep is the existing walk's surface)
