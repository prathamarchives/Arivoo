# Record 61 — P4-B slice one: the client-shaped adversarial acceptance path (the clean external client harness over the landed API)

> STATUS: SESSION ENGINEERING RECORD (2026-11-06; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 85. PR #103 MERGED (the P4-A slice four PDF boundary, under INT-145 — THE PHASE MARK: P4-A COMPLETE); the CLAIM-069 PR follows at this slice's end.

Session 41 (2026-11-06), CLAIM-069, opened at the merged head `101e173` (the PR #103 merge — P4-A
slice four). Record 60 carries the PDF account (complete, §4 closed); this record carries the
client-acceptance slice's contract + chain.

## §1 The #103 merge close (CLAIM-068 LANDED — P4-A slice four, P4-A COMPLETE)

PR #103 (CLAIM-068 — the PDF boundary) merged at 2026-11-06T20:21:34Z as
`101e173b27cdff0b9fdcd9e70105d80b0eb96974` under INT-145's standing authorization: the five checks
green at the exact final head `1c8ea11` AND on the merge commit (all observed live); the
merge-gate review D-042 (1a) `5806451549`; the flip/merge/restore with the protections re-read
byte-equivalent; the branch deleted; 0 open PRs; only main. No ARV-SEV-003 round — the digest
bound LAST (`ff97db0a`) + the local trusted-gate reproduction green BEFORE the push (run-07,
first attempt). THE ONE-ROUND SEV CHAIN: agent-9c4e2f17 PASS, zero open P0/P1/P2/P3-blocking
(the probes live: the octet-stream equivalence byte-equal, the export/restore byte-intact with
state_hash_match=true, the BOM'd-text class honest per the landed EXT-02 letter; the
red-records chain exact; all 13 diff paths declared; three P3 notes routed/recorded in
notverified — the all-ASCII syntax-as-text class routed to the future scan/OCR increment, the
restore's operator-boundary blob provisioning noted as CLAIM-060's landed design, the GREEN
message's wording noted against the probe-repair amendment). The probe repair (0360912): the
machinery-absent probe made DB-free (the import-based draft depended on the ambient database +
a fixed idem key — make verify's second run replayed the prior ack and misread the machinery;
the replay path also bypasses the registry check; the replacement is the INTAKE_OK registry
probe — environment-independent, idempotent). THE PHASE MARK: P4-A COMPLETE — all four slices
landed (the JSON intake, the position surface, the EPUB intake, the PDF boundary); the format
story honest end-to-end (three approved reading formats + the bytes passthrough + the PDF's
named boundary).

## §2 The client-acceptance slice's contract (PLAN's P4-B row elaborated one phase deep at P4-A's landing)

**The letter:** the READER CLIENT itself is P4-B's SEPARATE authorized repo (never this one —
the bounded exclusion every P4-A slice carried). This slice lands the BACKEND's proof of the
client contract: a clean EXTERNAL harness acting as the client — a scripted driver over the real
CLIs (commands.py/extract.py/query.py/capability.py), no privileged paths, never a table write —
exercising P4-B's named adversarial conditions at the real boundary:

- **auth/owner-scope expiration** — the owner GUC boundary: another owner's data is the SAME
  refusal as absent (the no-oracle, both read and write paths)
- **forbidden source** — the cross-owner import/extract/capture/position refusals
- **malformed DTO** — the typed CAP/FMT/NTE/BMK/POS refusals at every command boundary
- **offline transitions + timeout-with-uncertain-ack** — the crash matrix's lost-ack arm (exit
  2, the effect committed, the replay converges) + the honest unknown class
- **duplicate click** — the idempotency: same key + same body -> status=replayed with the same
  result_ref; same key + different body -> the typed ARV-CMD-409 with zero effect
- **reload/restart** — the reopen paths (get-position/get-capture/get-note over fresh
  invocations — the durable state answering)
- **stale source version** — the generation binding honest across a re-extraction
  (generation_matches=false, never a silent retarget)
- **deleted target** — the tombstone refusals (ARV-QRY-003 / the lifecycle classes)
- **retry-after-lost-response** — the same-key replay after the crash arm (the convergence)

**The design boundary (the acceptance the RED pins):** the suite runs green on a clean database;
each condition answers with its typed refusal or its truthful answer — never a privileged
helper, never a table write, never a second durability path. The full user walk rides first
(import -> open/read -> save position -> highlight/bookmark -> note -> the reopen round-trip),
then each adversarial condition. THE BOUNDED EXCLUSIONS: no reader-client UI (the separate
repo); no product tables touched by the harness; no new product surface (the landed contracts
only).

## §3 The slice chain in flight

commit A (this commit: the post-#103 five-area reconciliation + CLAIM-069 opened + record 61
minted) → the RED (test_client_acceptance.py alone at `101e173`, tests-only per LAW-11) → the
typed red-record binding → the GREEN (the landed contracts verified; the suite assembles the
proof — no new product surface expected) → the measured set (the suite x3 + make verify x2 at
both trees) → the SEV round(s) → the artifact finalize (notverified + sev.json, the digest bound
LAST) → the artifact re-bind (the PR-mode gate record + the trusted-gate reproduction) → the
push → the PR → the five checks at the exact final head → the merge-gate review (D-042 (1a)) →
**the merge under INT-145** → the post-merge verification (the five checks on the merge commit
observed live) → P4-C..F → the Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).
