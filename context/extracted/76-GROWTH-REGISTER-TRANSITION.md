# 76 — THE GROWTH-REGISTER TRANSITION FORM (CLAIM-085)

> STATUS: SESSION ENGINEERING RECORD — ACTIVE (session 51, 2026-11-16; owner turn 43's execution directive INT-148 carries on; D-022: historical process artifact, NOT owner intent). PR this session: #123 (CLAIM-085, disposition: open → merged under INT-145's single-actor path).

## §1 — the problem this record closes

The walled era (D-035's base-anchored judges) refused the raw-corpus growth in EVERY single-PR form — the PR #120/#122 wall finding, both closed with disclosure:

- 8-file tree + 8-file checker: the base-anchored canonical judge RED (VER-401/404: the base's seven-file EXPECTED_RAW vs the candidate's eight-file tree).
- 7-file tree + 8-file checker: the candidate's own verifier RED (head-tools: 7 observed vs 8 expected).

Root cause (verified in code, this session): `verify_canonical_layer.py`'s VER-404 was a HARD membership equality `raw_files == sorted(EXPECTED_RAW)` with the list frozen in the checker file itself — a file the base-anchored judge runs from BASE, so any growth must first exist in a BASE. No sequence of raw-file PRs can ever satisfy both runners at once.

## §2 — the adopted form (the fix, mechanically guarded)

The checker's membership rule becomes **SEED ∪ REGISTER**:

- The SEED: the seven anchored files (unchanged — RAW_ANCHORS lockstep intact).
- The REGISTER: the manifest's **§9 growth register** — a row `| name | SHA-256 | owner-auth | date |` in the CANDIDATE's own manifest. The register's auth must resolve like a reanchor's (an INT-xxx header in the ledger or a D-xxx row in DECISIONS — VER-805's resolution form).
- Admission: a file in context/raw must be seed-anchored OR register-bound — a register row's digest must equal the file's actual hash, the file must appear in the per-file coverage table, and the auth must resolve. Every expected member must be present (missing = RED, so the register cannot dangle either).

Two new selftest cases prove the guards: **MUT-40** (an unregistered file planted in context/raw — the smuggled-corpus class, caught by VER-404) and **MUT-41** (a well-formed §9 row whose digest does not bind the file — the phantom-register class, caught by VER-404). The full suite: 41/41 green.

**Why this is safe:** it weakens nothing. The seed files keep their exact RAW_ANCHORS + VER-805 lineage bindings; VER-802 (immutability) is untouched; a growth row must carry a resolvable owner authorization; and the base-anchored judge still runs the BASE's copy of the checker — the register lives in the candidate's manifest, which both judges read from the tree. The form is one checker change admitting ALL future growth (no per-file verifier edit ever again); it follows the reanchor register's own precedent shape (§8, H-01c-authority).

## §3 — the landing sequence (this slice + the next)

1. **THIS slice (CLAIM-085)**: the transition form — the checker's seed∪register membership + MUT-40/41 + this record + D-045 + Q16's note. NO raw file lands; the corpus stays 7; the OLD base judge (which does not know the register) passes over this slice's UNCHANGED corpus (its 7-file expectations all hold).
2. **CLAIM-084 re-push (slice B, branch already parked at `d592321`)**: the spec file lands in context/raw + the §9 register row `| KEV_SYSTEM_ENGINEERING_SPEC.md | 4eceb21c… | INT-148 | 2026-11-16 |` + the manifest coverage row + the README count. The BASE is now CLAIM-085's merge — growth-aware; both judges green (8=8, hash-bound, auth-resolving).

After 084, future corpus growth needs NO verifier edit: the owner's next raw file lands with its §9 row alone.

## §4 — Q16's scope note

Q16 (the corpus-growth AUTHORITY decision) asks WHO may add register rows: the owner explicitly, or the standing owner-authorization form (an INT ledger entry like INT-148 that carries the file). Until the owner answers, the operative default stands mechanically: a row requires an auth that RESOLVES to a real INT-/D- entry — a fabricated authorization fails MUT-36's class checks; the genuineness judgment is the review layer's (D-042's rule), never claimed by the checker. Q16 blocks only future growth rows' authority semantics; it does NOT block CLAIM-084 (whose auth — INT-148 — is already ledgered and genuine).

## §5 — the close

**Also this slice: the CLAIMS registry-drift repair.** The #121 merge (slice A's restructure) landed CLAIM-083's OPEN row without its closed row — the reset-then-reapply class (the slice-A rebuild's phase-2 script wrote the closed row once, then the hard reset to the riding base dropped it, and the re-run's idempotent guard saw the open row and skipped). This slice retires the stale open row and adds the closed row with the merge facts (PR #121 = `275e3f12`, 2026-11-16T14:32:21Z, the five checks green) — the ARV-CLM-005/006 class repaired in the established form.

(merged; see CLAIMS.md's closed rows and the WORKLOG Task 104 entry)
