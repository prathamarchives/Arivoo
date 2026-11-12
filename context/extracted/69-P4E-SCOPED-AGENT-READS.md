# Record 69 — P4-E slice one: the scoped agent read surface (the authorized agents' access)

> STATUS: SESSION ENGINEERING RECORD (2026-11-11; the standing do-not-stop chain INT-134..146;
> D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks
> nothing. Worklog entry: Task 93. PR #111 MERGED (the P4-D slice two write completion, under
> INT-145); record 68 §5 closed at this commit (the post-#111 reconciliation).

Session 41 (2026-11-11), CLAIM-077, opened at the merged head `898b9f2a` (the PR #111 merge —
P4-D slice two). Record 68 carries the write-completion account (complete, §5 closed at this
commit); this record carries the scoped-agent-access slice's contract + chain — P4-E's opening.

## §1 The #111 merge close (CLAIM-076 LANDED — P4-D slice two) + THE P4-D EXIT

PR #111 merged at 2026-11-11 as `898b9f2ac6679c87f989b52d22941ba3b5f8b546` under INT-145's
standing authorization: the five checks green at the exact final head `c44d17b5` AND on the
merge commit `898b9f2a` (all observed live); the merge-gate review D-042 (1a) `5859574863`;
CodeRabbit the skip state (noted per D-042 (1c)); zero review threads; the flip/merge/restore
with the protections re-read byte-equivalent; the branch deleted; 0 open PRs; only main. No
ARV-SEV-003 round — the digest bound LAST (`8b5b0c86`) + the local trusted-gate reproduction
green before the push (run-06, first attempt). THE ONE-ROUND SEV CHAIN: agent-ca4c6f8e PASS
zero open P0/P1 (94 live probes + 13 static checks; four findings ALL ROUTED — F-076-1 the P2
oversize-pin traceback, the F-075-1 commands.py twin pre-existing at the substrate and
fail-closed; F-076-2/3/4 the P3s). The full account: record 68 §4/§5 + CLAIM-076's rule-4
close row.

**THE P4-D EXIT CHECK (at the #111 merge):** every required P4-D backend behavior landed and
verified — the resolution system (CLAIM-075) + the write completion (CLAIM-076). **P4-D
COMPLETE.**

## §2 The scoped-agent-access slice's contract (the PLAN 4E row, one phase deep at the P4-D exit)

**The letter (the PLAN 4E row):** "authorized agents read the owner's journal and capture
context through the same API with provenance/scope/budgets; READ-ONLY at first; owner-scope
enforced on every query; imported text untrusted; no arbitrary database access; Q9/Q10 handled
honestly." The North Star's own words: "Specifically for AI, I can just connect an agent and
it has all the context of me" (C2 — the owner's agents have the owner's context). The RTM's
SYS-02 matrix: "an agent actor carrying only the owner's authorization never widening scope
(P4-E's agent matrix extends)."

**The design boundary:**
- **Migration 0019 — `arv.agent_credential`**: the owner-minted credential (id, owner_scope,
  label 1..128 no NULs, token_hash — the sha256 of the token VALUE, the value NEVER stored
  and shown ONCE at mint; the closed scopes CHECK `scopes = 'read'` — READ-ONLY at first,
  structural; the spine's provenance columns; the revocation as the ONE-WAY `revoked_at`
  column — NULL live, set dead, never unset, guarded by the substrate's own trigger family
  with the one-transition law; RLS enabled AND forced + the owner policy; the grants —
  INSERT+SELECT arv_app, SELECT arv_read, NO UPDATE/DELETE (the guarded one-way transition
  rides its own trigger, the 0013-style named exception).
- **`arv.agent_read_log`**: the append-only audit trail (credential_id, owner_scope, arm,
  the bounded facts — the limit and the row count served, NEVER the content; created_at);
  append-only triggers; RLS forced; the grants INSERT+SELECT arv_app / SELECT arv_read.
- **commands.py `mint_agent_credential`**: through the spine's own ack contract (idempotent,
  the frozen grammar); the token VALUE generated as 32 bytes of secrets-quality randomness,
  urlsafe-encoded, the sha256 stored, the VALUE shown exactly ONCE in the ack
  (`token=<value>` — the one-time display law, the password-reset convention); the typed
  refusals (ARV-AGT-003 the label law: empty/oversized/NUL-carrying refused). The revocation
  `revoke_agent_credential --id`: the one-way transition with the alternation refusal
  (already-revoked refuses; the absent/cross-owner the no-oracle ARV-AGT-001). NO outbox
  ride: the credential is a LOCAL access primitive, never owner content to replicate (the
  design decision recorded; the SEV may challenge it).
- **query.py — the `--agent-token` mode on the READ arms**: the token identifies the owner
  scope (the credential's owner_scope — the caller NEVER passes --owner on this path); the
  verification (the sha256 lookup, the liveness, the scope) then the SAME arm's read with the
  owner scope from the credential + the audit row appended in the same read transaction's
  follow-up; the typed refusals: ARV-AGT-001 the invalid token (unknown, revoked, or
  scope-missing — the SAME refusal, never a side channel), ARV-AGT-002 the write command
  through the agent path (commands.py refuses --agent-token structurally: READ-ONLY).
- **The budgets**: the shared _page_args bounds ARE the read budget at this phase (every
  agent read bounded by the same limits as the owner's reads); the audit row records the
  served row count against the limit — the observable consumption. The deeper response
  budgets (fitting an agent's context window) are Phase 5's retrieval increments, recorded
  as the bounded exclusion, never claimed here.
- **Q10 handled honestly**: the token primitive is the access-shape surface, NOT
  workflow-tamper hardening (Q10's boundary named in the capability row + notverified: the
  local single-user threat model; the hash comparison not constant-time; no
  replay-window/rotation claims; the narrow remaining owner choice recorded — the minting
  policy and any server-deployment scoping stay owner-gated).

**The laws carried:** the no-oracle (an invalid token never reveals whether a label/id
exists); the owner-scope never widened (the agent of A never sees B — RLS + the
credential-bound scope); the read-only structural; the append-only audit; the one-time
token display; the hostile-string law (the token and the label are DATA).

**THE BOUNDED EXCLUSIONS:** no MCP wrapper (P4-E slice two — the same retrieval core behind
the protocol adapter); no write scopes (READ-ONLY at first, per the row's own letter); no
response-budget machinery beyond the page bounds (Phase 5's retrieval); no token
rotation/expiry windows (a future increment, Q10-honest); no multi-owner credential sharing;
no reader-client work (P4-B's repo).

## §3 The executed chain

commit A (docs: the post-#111 reconciliation + THE P4-D EXIT CHECK + CLAIM-077 opened + record
69 minted; the branch pushed EARLY) → **the RED** (`048a1ddb`: the AGT suite authored
tests-only per LAW-11 — 407 lines, the AGT-01..08 registry; the DB-free machinery-absent
probe; red-01.txt exit 1 ARV-TEST-000) → the typed red-record binding (`6d5e22e`:
red-records.json + red-01.txt + the gate.py TESTS registration — the ARV-RED-008 class,
diff-visible) → **the pre-GREEN amendments** (the four disclosed pin-authoring repairs: the
AGT-02 NUL probe moved to the law's own layer — argv cannot carry NUL, the CLAIM-074 lesson;
AGT-06's bare-id listing form; AGT-07's before/after audit-count form; AGT-08's
has_table_privilege grants audit + the boolean renderings) → **the GREEN** (`cf0fe44`:
migration 0019 + commands.py's mint/revoke + query.py's --agent-token mode + capability.py's
row) → **the measured-set repair** (`79b5f43`: the F-074-1 class caught live by the slice's
OWN measured set — runs 02/03 RED, the disclosed evidence kept: token_urlsafe CAN generate a
leading dash and the separate-argv form then dies at argparse; the repair — the token's first
character constrained non-dash + the AGT-01 twelve-mint strengthener) → **the LAW-24 repair**
(`f7b6b58`: the gate's own boundary lint caught commands.py calling secrets.token_urlsafe —
the token mint moved to its LAW-24 home, adapters/ids.py's new_agent_token) → **the SEV
round-1 repairs** (`20cd5c5`: F-077-1 the P2 — the scope-declaration drift, adapters/ids.py
added to scope.txt + the CLAIMS row; F-077-2 the P3 — the lookup's default PUBLIC EXECUTE
revoked in the still-unmerged 0019; F-077-3 the P3 — the duplicated helper block deleted;
F-077-4 the P3 — the docstring wording) → **the SEV round-2 repair** (the head: F2-077-5 the
P3 — _agent_audit's unescaped owner interpolation, demonstrated live on owner O'Brien; the
repair — the owner travels escaped (the file's own _read convention, BOTH the GUC set and the
VALUES list) + the AGT-09 regression pin) → the measured sets at each tree (runs 01-19: the
GREEN tree x3 + verify, the disclosed flake runs 02/03, the token-repair tree x3 + verify,
the round-1-repair tree x3 + verify, the round-2-repair tree x3 + verify — all exit 0 except
the disclosed 02/03/07) → the artifact finalize (this commit) → the artifact re-bind (sev.json
+ notverified + the proof sheet + the recorded PR-mode gate + the local trusted-gate
reproduction) → the push → the PR → the five checks → the merge-gate review → **the merge
under INT-145** → the post-merge verification → P4-E slice two (the MCP wrapper) → P4-F → the
Phase 4 exit gate — NO PAUSE EVEN FOR UPDATES (INT-146).

## §4 The SEV account (the two-round chain)

**Round 1 (agent-e2095ac5, PASS zero open P0/P1 — 56 live probes + 18 static/git checks).**
Every claimed behavior reproduced on the reviewer's own scratch rigs: the mint + the one-time
display (the replay never re-displaying; the whole-database pg_dump grep finding the token
value ZERO times; the argv-safe first char over 21 mints + a 3000-mint adapter distribution);
the agent read mode byte-equal on TWENTY-ONE arm shapes (not just the seven claimed); the
audit row landing only on served reads (never on refusals); the no-oracle invalid-token class
(unknown vs revoked byte-equal; five hostile strings all the same refusal, never echoed, never
a traceback); the identity law (both/neither refused ARV-AGT-002); the read-only closure
(including the slice's OWN mint/revoke commands refusing --agent-token); the scope isolation
(B's credential seeing only B, the read log RLS-scoped); the revocation (the one-way
transition, the alternation, the no-oracle, the post-revocation refusal, the audit history
preserved); the substrate (the closed scopes CHECK refusing a hostile write-scoped INSERT
— with the reviewer's own CHECK-drop-and-restore probe proving the lookup filters
independently; the one-transition guard incl. the superuser un-revoke refused; the RLS
forced; the grants; the SECURITY DEFINER lookup returning exactly the scope+id pair); the
audit-row honesty FORCED LIVE (the INSERT grant revoked mid-rig → the read serves then fails
LOUD ARV-AGT-005); the budget (ARV-QRY-004 byte-equal to the owner's); Q10's honest boundary
(the capability row matching the code); the RED reproduced from the archived tree + the
4-way sha256 amendment-chain verification. THE FINDINGS, ALL IN-SLICE: F-077-1 the P2 (the
scope-declaration drift — the gate's own ARV-SCOPE-002/ARV-CLM-002 firing live on
adapters/ids.py's omission), F-077-2 the P3 (the lookup's default PUBLIC EXECUTE — arv_read
resolving a live hash), F-077-3 the P3 (query.py's duplicated helper block), F-077-4 the P3
(the alphanumeric-vs-non-dash wording) — ALL FOUR REPAIRED in-slice at 20cd5c5 (the scope
declarations widened; the REVOKE FROM PUBLIC added to the still-unmerged 0019, verified live:
arv_read denied, arv_app resolving; the duplicate block deleted; the wording corrected).

**Round 2 (agent-6a8d56b7, PASS zero open P0/P1 — 19 live probes + 10 static checks + the
regression suites).** All four round-1 repairs verified CLOSED live (the gate's own checks
green over the 28-path diff; the permission matrix; the single definitions; the docstring;
the SECURITY DEFINER census — 0019's lookup the system's only one). The sweep re-verified
every core invariant + the regressions (gate_dispatch, commands). ONE NEW FINDING: F2-077-5
the P3 (_agent_audit's unescaped owner interpolation — a quote-bearing owner's read served
then failed loudly with no audit row, demonstrated live on owner O'Brien; fail-loud, zero
escalation, the one-line repair) — REPAIRED in-slice at the head (the owner escaped with the
file's own convention, BOTH the GUC set and the VALUES list + the AGT-09 regression pin:
O'Brien's credential mints, the read serves, the audit row lands).

## §5 The close

PR #112 merged at 2026-11-11T17:17:39Z as `505cb33632d668f33f1dadf24346dcb37f523949` under INT-145's
standing authorization: the five checks green at the exact final head `169cbd42` AND on the
merge commit `505cb336` (all observed live — the verify run 43057445083 at the head, the run
43066742494 on the merge commit); the merge-gate review D-042 (1a) `5862653355` (the
substantive host review engaging the actual diff — the token-secrecy headline risk verified
against the SEV round's whole-database probe, the no-oracle, the read-only closure, the
substrate audits); CodeRabbit the skip state (fewer than 10 stars, no automatic reviews —
noted per D-042 (1c), the host review the floor); zero review threads; the flip/merge/restore
with the protections re-read byte-equivalent (approving=1, dismiss_stale=true, strict=true,
the five contexts, enforce_admins, no force pushes, no deletions); the branch deleted; 0 open
PRs; only main. No ARV-SEV-003 round — the digest bound LAST (`13023b93` at the final content
head `169cbd42`, the post-scanner-repair re-bind; validate_report GREEN) + the local
trusted-gate reproduction green before the push (run-26, exit 0, the trusted base reset to
the current main `898b9f2a`). THE TWO-ROUND SEV CHAIN (the account in §4): round 1
(agent-e2095ac5) PASS zero open P0/P1 — 56 live probes + 18 static checks, four in-slice
findings ALL REPAIRED at `20cd5c5`; round 2 (agent-6a8d56b7) PASS — all four repairs verified
CLOSED live, one new P3 (F2-077-5 the unescaped-owner interpolation) found and repaired at
the head `88d1e829` with the AGT-09 regression pin. THE SCANNER-COLLISION REPAIR (the two
commits `2338226`/`169cbd42`, the standing lesson applied): the CI secret-scanner's
generic-assignment pattern matching commands.py's token-assignment line + the round-1
report's quoted values — the local renamed, the report's quoted value redacted + the diff
line masked, the repair comment worded without the literal pattern (the self-reference
guard); the whole-diff scan clean; the digest re-bound over the NEW content head per the
anti-lag ordering. The 26-record proof sheet (runs 23/24 the scanner-repair tree's measured
set — the AGT suite GREEN + make verify — + run-25 the PR-mode gate GREEN + run-26 the
trusted-gate reproduction exit 0).

**THE P4-E REMAINING-INCREMENT CHECK (2026-11-12, at the #112 merge):** every slice-one
behavior landed and verified — the credential (the one-time display, the one-way revocation,
the closed scopes CHECK), the mint/revoke commands, the `--agent-token` read mode (byte-equal
to the owner's reads, audited, budgeted, no-oracle), the read-only structure, the scope
isolation. ONE named increment remains from §2's own exclusions: the MCP wrapper (slice two —
the same retrieval core behind the protocol adapter; the non-argv token form's natural home).
CLAIM-078 takes exactly that, then P4-F (the recovery + contract gate) → the Phase 4 exit
gate. Record 70 carries the MCP-wrapper slice.
