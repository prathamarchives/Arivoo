# PROOF SHEET — slice claim-045-p3m0-migration-oracle (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 628659b845bc8b87ab854b498e2f43cd40dcad3d
- generated (last record's timestamp): 2026-10-25T12:15:22.496418+00:00
- run records: 18

## Run records (command, exit, output digest)
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 4966fdb2170ba60c · 2026-10-25T11:34:44.754433+00:00
- `python3 harness/tests/test_substrate.py` -> exit 0 · output sha256 bd4d723a03ab6c40 · 2026-10-25T11:34:45.167980+00:00
- `python3 harness/tests/test_commands.py` -> exit 0 · output sha256 565088ee26bfb2e9 · 2026-10-25T11:34:47.487373+00:00
- `python3 harness/tests/test_gate_dispatch.py` -> exit 0 · output sha256 791ff1faab1f66be · 2026-10-25T11:36:12.956988+00:00
- `python3 harness/tests/test_mutation_floor.py` -> exit 0 · output sha256 14846efaa82adb46 · 2026-10-25T11:36:38.951730+00:00
- `python3 harness/tests/test_trusted_gate.py` -> exit 0 · output sha256 a090e1896dad4737 · 2026-10-25T11:36:50.694136+00:00
- `python3 harness/tests/test_claims_paths.py` -> exit 0 · output sha256 efd3e683d8b36537 · 2026-10-25T11:36:51.113648+00:00
- `python3 harness/tests/test_record_machinery.py` -> exit 0 · output sha256 4ff391be99427e0a · 2026-10-25T11:36:51.349032+00:00
- `python3 harness/tests/test_sev.py` -> exit 0 · output sha256 f9dd69c26b7a17d4 · 2026-10-25T11:36:54.072982+00:00
- `python3 tools/isolation_selftest.py` -> exit 0 · output sha256 db0ced9ebcfb3551 · 2026-10-25T11:37:12.599055+00:00
- `python3 harness/gate.py --known-bad-only` -> exit 0 · output sha256 f79932f6fc02607d · 2026-10-25T11:37:28.101242+00:00
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 b96415808d37d3f5 · 2026-10-25T11:37:28.262530+00:00
- `make verify` -> exit 0 · output sha256 7ca1899a5ed28b44 · 2026-10-25T11:40:20.033762+00:00
- `python3 harness/gate.py --slice claim-045-p3m0-migration-oracle --diff origin/main` -> exit 1 · output sha256 6d15d58ffde5004d · 2026-10-25T11:43:45.503851+00:00
- `python3 harness/gate.py --slice claim-045-p3m0-migration-oracle --diff origin/main` -> exit 0 · output sha256 5271d612a6864954 · 2026-10-25T11:52:12.568069+00:00
- `python3 harness/tests/test_migrations.py` -> exit 0 · output sha256 ac32f490f5bebc8c · 2026-10-25T12:09:46.863123+00:00
- `make verify` -> exit 0 · output sha256 6a9ff9bb89093aea · 2026-10-25T12:12:39.904663+00:00
- `python3 harness/gate.py --slice claim-045-p3m0-migration-oracle --diff origin/main` -> exit 1 · output sha256 182883eeeb5707ba · 2026-10-25T12:15:22.496418+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- - the identifier-context rule is now BYTE-ORIENTED exactly as PG's scan.l (any codepoint >= U+0080 starts/continues an identifier; astral planes included — SEV-10's cap lesson, closed with ARV-TEST-038/039); the residual lexer-drift classes above remain the fail-closed direction only.
- - the mask-vs-PG-lexer admitted drift, the FAIL-CLOSED (over-refusal) direction only (SEV-6's rewrite + SEV-12's re-review truthfulness): (1) a hex number adjacent to a '$' (the mask enters identifier context at 'x' — the masked text over-scans; observable as a ScanError/ARV-MIG-016 refusal or a false positive on string content, never a silent apply; live probes: PG rejects these shapes too, both reject); (2) the space-separated E 'x\'' shape and identifier-tail nameE'...' shapes — the mask and PG both reject every divergent spelling probed (over-refusal or both-reject, never a valid-file refusal); (3) dollar-quote TAGS containing high-bit characters (PG accepts $café$...$café$; the mask's ASCII-only tag matcher over-scans the body as raw text — a valid string mentioning destructive words is falsely refused ARV-MIG-003 without the directive; the hiding direction is structurally impossible because mask-tags are a strict subset of PG-tags — the reviewer's live-probed SEV-13a class, fail-closed only); (4) U&'...' unicode-escape spellings — every divergent spelling the mask 016-refuses was also rejected by PG in live probing, so no VALID-file over-refusal is demonstrated; the wording keeps the over-caution honest. A perfect-fidelity fix requires a full PG lexer — out of scope for the deliberately narrow accepted grammar (the card's own non-goal: no new migration framework); every residual refuses, never admits.
- - the ARV-MIG-009 'the DB is unchanged (transaction proof)' message is conditional on the scanner's fidelity for the guarded classes — the identifier-aware mask (SEV-1's fix) restores that fidelity for embedded transaction control and destructive statements; a runtime failure therefore rolls back everything the oracle admitted, and what the directive admits is owner-declared (the directive is the paper trail, not a proof).
- - the ledger-name bidirectional check (SEV-5) compares the directory filename's name field against the ledger's name column; applied_at/applied_by are not part of identity and are not compared (0002/0003's rows carry harness/migrate.py; any future runner identity change is its own bounded slice).
- - the pre-scan (SEV-7) reads the ledger observationally to decide pending files; on a ledger that exists, oracle refusals for pending files still happen before the first WRITE, but the (pre-existing, empty-or-populated) ledger table itself remains — the zero-effects claim for those DBs covers application effects, never the scaffolding that predates the run.
- - CREATE EXTENSION is admitted by classification (the card's declared admitted set); extension scripts run inside the migration transaction — UNVERIFIED BY SCOPE, never claimed fail-closed: the extension catalogue's own review is out of the oracle's scope (the SEV reviewer's own not-verified note, adopted; the fail-closed-direction claims in this record cover the LEXER-drift classes only).
- - the migration suite's case count (39 named checks at this slice's close) is its own declaration — never a contract number; the card's coverage contract is the guards + proofs, not the count.
- - concurrency (racing migrators on one DB) — UNVERIFIED BY SCOPE, never claimed fail-closed: the runner is single-writer by protocol; a concurrency guard is its own bounded slice if the owner ever wants parallel migrators.
- - the ARV-SEV-009 undecidable-base test gap (the late #79 nitpick, routed at CLAIM-044's close row): its own bounded regression follow-up — deliberately NOT folded into this slice's SEV machinery scope (scope exclusivity, LAW-06).

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 7f9e2d786be3f17a2e1ef0ef07b75ef05c6e5ca36e3d670cd1994b30d0e30e18
- reviewed_diff_sha256: 9e83ba827c386acf3a01da409dc9fdff0b3077819efe70cc8727e024bc590ad1
- disposition: PASS
- findings: 17 (open P0/P1: 0)
- not-verified entries: 6

## Assembly
- sheet sha256 (of the content above, excluding this line): cd36061aedfe01e0725f2cdff38468106cfb14c10ecfad00623a5e579f53acee
