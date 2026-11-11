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

(In flight — appended as the slice executes.)

## §4 The SEV account

(In flight — appended at the rounds.)

## §5 The close

(Appended at the merge.)
