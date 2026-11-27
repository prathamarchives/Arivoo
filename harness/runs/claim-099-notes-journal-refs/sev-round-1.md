# CLAIM-099 — SEV round 1 (the independent verification)

- **Agent:** the independent SEV probe context (reviewer-sev099-probe-distinct-context — the 95-probe battery authored and first executed in a separate reviewer task; the subagent-return channel refused twice with context deadlines, disclosed in record 84 §8; a declared distinct context, not cryptographic independence)
- **Date:** 2026-11-27
- **Round:** 1 (with two in-slice repairs re-verified)
- **Base:** `1e11ccebdb3fc2cf8ed495d1efc9b397bc26663d` (origin/main, PR #140's merge)
- **Head:** the repair head (the chain: 83fa734 the RED → e483228 the routes → 79ccb4b the SEV repairs → a811e74 the bookkeeping)
- **Method:** the full diff read hunk-by-hunk; the battery re-executed; the independent 95-probe battery on its own migrated scratch db (A: the note revision chain with per-revision reference sets; B: the reference grammar matrix; C: the journal writing lab — the byte-identical round-trip over multi-line/unicode/pipe/CRLF/U+2028 content, the kind-immutability contract; D: the six-state resolution matrix; E: the cross-owner matrix with a real second owner; F: the idempotency laws on every write leg; G: the _json_body bounds; X: the reviewer's own edges — the temp-dir cleanup law, the surrogate boundary, the post-edge liveness); the RED re-observed at the test-only commit.

## §1 Verdict

**PASS — zero open P0/P1; two findings resolved in-slice (SEV9-171 a real P1 product defect; SEV9-123k a P2 contract correction); one open P2 named followup (the KWR-002 map row, byte-parity with the imports family preserved).** The adapter law held: thirteen routes over the existing kernel arms, zero kernel files in the diff, the content staged through the kernel's own file channels (never argv-sized bodies), the temp-dir cleanup verified live (zero staged dirs remain after the full battery).

## §2 The live verification

- The battery at the repair head: exit 0, 146 PASS (ARV-ROUTE-001..007 + ARV-API-001..131).
- The independent probe: exit 0, 95/95 PASS after the two contract corrections; 92/95 at the pre-repair head with the two live findings.
- The RED at 83fa734: exit 1, 42 failures (089..125, 128..131 substantive; 126/127 vacuous through the absent-route 404 — disclosed).
- The canonical layer at the head: exit 0 (148 intents). The suite: exit 0.

## §3 Findings

- **SEV9-171 (P1, RESOLVED)** — the lone-surrogate content (valid JSON, unencodable as UTF-8) crashed the staging OUTSIDE the §11.4 envelope: a bare 500 Internal Server Error, one leaked staged temp dir. The repair: the UnicodeEncodeError caught at BOTH staging sites, a named ARV-QRY-004 422 in-envelope; the battery's surrogate check and the probe's X3 both pin it.
- **SEV9-123k (P2, RESOLVED)** — the journal revise DTO carried a kind the kernel ignores (the F5b silent-drop class; the kernel's revise arm carries the PRIOR revision's kind — the kind is immutable identity). The repair: the revise boundary refuses a kind named; the battery + the probe corrected to the immutable-identity contract. The finding's original expectation (the kind change takes effect) was wrong per the kernel's own law — disclosed; the repair it drove is real.
- **SEV9-OBS-KWR (P2, OPEN — the named followup)** — an over-bound unbroken token in the authored content surfaces 500 via the fallback map, byte-identical to the pre-existing imports family. Repair deferred to a §11.4 map-family slice that adds the KWR-002 → 422 row for ALL families at once (preserving byte-parity rather than a single-family exception).
- **SEV9-OBS-WS (recorded not charged)** — the space-bearing id's ARV-QRY-002 500: the pre-existing F-072-1 malformed-id class, byte-parity with /sources.

## §4 Not verified

The five PR-head CI checks + this PR's D-042 review; a live Supabase-issued token; uvicorn over a real socket; the deployed surface; the concurrent revise-writer race (the kernel's 0009/0016 advisory-lock evidence — read, not raced); the reading-lists/retrieval/sync/export families; the remote btree/TOAST parity.

## §5 The binding

- base_sha: 1e11ccebdb3fc2cf8ed495d1efc9b397bc26663d
- reviewed_diff_sha256: c70c3437e51c7bdd... (the full value in sev.json; recomputed through harness.sev's public API)
- validated: `python3 harness/sev.py claim-099-notes-journal-refs origin/main` → exit 0
