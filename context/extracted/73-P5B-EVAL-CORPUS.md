# Record 73 — P5-B: the eval corpus (CLAIM-081, session 48)

> STATUS: SESSION RECORD — 2026-11-15 (session 48; the banner per the standing records law). The #116 landing's first successor slice: the versioned query corpus — the
> evaluation baseline BEFORE any ranking change (the owner's fixed dependency
> order: the corpus lands before 5C's semantic spike and 5E's hybrid ranking
> so they can only be measured against it). The PLAN 5B row elaborated one
> phase deep.

## §1 The INT ledger sync

- **INT-147** (the standing Phase 5 continuation reservation, ledgered
  2026-11-14 at CLAIM-080's commit A): the do-not-stop chain continuing into
  Phase 5 — this slice rides it (the retroactive notation in the CLAIMS row).
- **INT-145** (the standing merge authorization): the single-actor merge path
  applies at PR #117 when the D-042 review approves — the #116 form (the
  account + the protection snapshot posted BEFORE the change, the
  flip/merge/restore, the byte-equivalent re-read).
- No new owner question opened; Q6–Q12 scopes unchanged (Q7 gates only the
  5C semantic spike — this slice's deterministic corpus needs no budget).

## §2 The corpus letter (the 5B contract elaborated one phase deep)

A **versioned query corpus** — a JSON file under the slice runs carrying the
corpus id + revision + the four case classes; the run is **deterministic**
(the same corpus id + revision re-runs byte-equal — no clock, no randomness,
no environment-dependent ordering: the verdict sorts, the ids are fixed, the
loop iterates the cases in their file order); the verdict is **mechanical**
(the expected vs the actual id sets; precision/recall computed over the
counts and printed with the corpus id + revision + the per-class breakdown —
never an LLM narration); the corpus is **DATA** (a case whose query embeds
hostile instruction-like content is evaluated like any other — nothing
executes it); the run rides the **owner boundary** (RLS through the standing
search arm — the evaluator never re-implements retrieval, it calls the arm
and compares).

The four case classes (the corpus's own law):
- **relevant** — the query's expected admissions (multi-term AND included:
  only items bearing EVERY term).
- **no-result** — queries whose honest answer is the empty set, with the
  explicit marker: never a fabricated match, never a similar-material
  fallback, never an error.
- **distractor** — near-miss material (adjacent in meaning, sharing NO query
  term) that must NOT be admitted; the miss is mechanically detectable
  because the corpus records the near-miss ids.
- **conflated** — the same term spanning two distinct documents: BOTH
  admitted, disambiguated by provenance (the item's own source id in the
  why), never by rank.

## §3 The executed chain (the RED->GREEN->measured form)

- **The RED** (LAW-11, commit `1588092`): the EVC-01..10 suite minted
  against the machinery-absent tree at CLAIM-080's merged head `2e35d59` —
  10 FAILs, red-01.txt, harness/eval.py absent.
- **The GREEN**: `harness/eval.py` (the loader + the deterministic runner +
  the mechanical verdict + the typed ARV-EVL-001/002/003 refusals + the
  run-record JSONL) + `corpus.json` (7 cases, the four classes) + the
  suite's own fixture seeding (the four documents — the two-document
  conflated pair, the near-miss distractor, the hostile query doc — and two
  owners). The GREEN's own catch: the conflated pair needed the SAME term
  in BOTH documents (TEXT_A gained "meridian" — the EVC-05 diagnostic RED
  fixed in the fixture, the corpus's design lesson: a conflated-terms case
  is meaningless unless the term actually spans the two documents).
- **The five binding repairs** (each observed as a gate failure, each
  fixed in-slice): (1) the conflated pair's same-term; (2) the runs
  directory declaration (the F-001 session-23 semantics: exact equality or
  directory-boundary descendant — the individual-file lines collapsed into
  the directory form); (3) the CLAIMS row's scope widened to the honest
  full diff (the staged close's residue included); (4) the legal import
  form (the sibling suite's pattern: `sys.path.insert(REPO)` + `from
  harness.adapters import pg` — the DEP-008 root name is `harness`);
  (5) the sev.json completed in the full 18-field schema (the four v_model
  verification strata + system_claims + the severity law — the P3 class
  does not exist in the finding schema, the JSONL-growth debt honestly
  P2).
- **The measured set**: the proofsheet (ARV-PRF-005 run record + the
  ARV-PRF-003 re-derivation), sev.json (the seven failure modes + the
  honest debts F-081-1..5, the digest bound), the make-red amendments
  chained at each suite edit, the RPK sibling re-verified (10/10 — the
  standing suites never regressed).
- **The gate**: GREEN in PR mode (`--slice claim-081-p5b-eval-corpus
  --diff origin/main`) — suites + red records + scope/size + lint + deps +
  known-bads + proofsheet.

### The D-042 round 1 (the fresh-context review at PR #117)

**BLOCK-MERGE — four findings, each real, each repaired in-slice** (the
expected multi-round shape; the #116 lesson standing: the repair's own
blind spot):

1. **The stale digest at the head** (P0): the records commit `7fac5b1`
   widened the reviewed path set without re-binding sev.json — the gate
   itself refused at the head offered for merge. Repair: the digest
   re-bound at the repair head.
2. **The dead distractor tautology over a self-contradictory fixture**
   (P1): the control was `clean = miss == len(actual)` (identically true)
   over a near-miss text that CONTAINED the query token ("quartz") — the
   committed run printed `admitted=3 near-miss-excluded=true` (the
   distractor admitted while labeled excluded), and FM-02 (the rank-creep
   failure the corpus exists to catch) was undetectable. Repair: the
   tautology deleted; the fixture's near-miss rewritten disjoint (the
   wharf/fog/jetty/tar text); the verdict compares the admitted count
   against the recorded expectation — over-admission is fp, the shortfall
   is fn.
3. **The fp-blind verdict** (P1): the relevant class counted admissions as
   tp unconditionally — precision was structurally 1.0, over-admission
   invisible, a ranking change that admits junk shows only as tp
   inflation. Repair: the count-based channel with the over-admission fp
   arm (expect_count authoritative; precision can actually drop).
4. **The fail-open** (P1): `_search` never checked the arm's return code —
   a dead DB, a refused RLS read, or an arm-side typed refusal was
   silently converted into "the honest empty set" with exit 0 (the
   evaluation baseline's worst possible inversion: a broken environment
   reporting no-result cases as honest). Repair: the arm's refusal
   propagates typed as ARV-EVL-004.

Plus the P2 strengthenings: the EVC-08 pin was vacuous (stdout never
contains ids in any state — the pin passed with or without RLS; the real
observation now goes through the standing arm: B's own copy admitted, A's
id absent) and the honest expect_counts over the fixture (R1=1: only doc A
bears xylophone; R2=2; D1=2; C1=2; H1=1).

**What survived the adversarial probing untouched** (the reviewer's own
verifications): the determinism (byte-equal re-runs, the sorted-case loop,
no clock/randomness/dict-order dependence); the corpus-as-data law (zero
eval/exec/compile references; hostile corpora load and run with the same
mechanical verdict shape, no execution effects); the LAW-11 red-first
chain (reproduced at the tests-only commit in a detached worktree; the
digests bind exactly); the typed registration refusals; the suites 10/10;
the proofsheet re-derivation.

## §4 The SEV account

The failure modes the corpus exists to catch: FM-01 the fabricated match
(no-result); FM-02 the distractor's rank-creep admission; FM-03 the
conflated term's rank suppression; FM-04 the corpus-as-data execution;
FM-05 the non-deterministic drift; FM-06 the owner-boundary crossing; FM-07
the silent corpus default. Each carries its control (the EVC pin that
refuses it). The honest debts: F-081-1/2 (the symbolic expect_ids + the
count-based verdict — the runtime-seeded-uuid consequence: the suite's
fixture seeds uuids in a fresh scratch DB, so the corpus cannot carry them
statically; the evaluator compares against the run's own admissions — the
deterministic shape, not the static id; the conflated/distractor/no-result
classes ARE id-exact in the suite's own pins); F-081-3 (the eval-runs.jsonl
append growth — bounded by the repository's own history discipline);
F-081-4 (the standing harness.adapters dependency — the legal form
adopted; eval.py itself imports only the standard library + subprocess to
the standing query arm); F-081-5 (the hostile-as-data marker is a presence
count, not a behavioral differential — the stronger probe routed to the
D-042 review). Disposition: PASS, zero open P0/P1.

## §5 The close

(Appended at the merge.)
