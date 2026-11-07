# Record 63 — P4-C slice two: the session/dwell events surface (D-010's durable behavior data)

> STATUS: SESSION ENGINEERING RECORD (2026-11-07; the standing do-not-stop chain INT-134..146; D-037/D-041/D-042/D-043). Historical process artifact per D-022: NOT owner intent, outranks nothing. Worklog entry: Task 87. PR #105 MERGED (the P4-C slice one library + current-reading state, under INT-145); the CLAIM-071 PR follows at this slice's end.

Session 41 (2026-11-07), CLAIM-071, opened at the merged head `fd6fb9f` (the PR #105 merge —
P4-C slice one). Record 62 carries the library slice's account (complete, §4 closed); this
record carries the session/dwell slice's contract + chain.

## §1 The #105 merge close (CLAIM-070 LANDED — P4-C slice one)

PR #105 (CLAIM-070 — the library + current-reading state) merged at 2026-11-07T06:12:10Z as
`fd6fb9fb6a9133d39a324447cbc4f0defae37951` under INT-145's standing authorization: the five
checks green at the exact final head `12510a9` AND on the merge commit (all observed live);
the merge-gate review D-042 (1a) `5810504474`; the flip/merge/restore with the protections
re-read byte-equivalent; the branch deleted; 0 open PRs; only main. No ARV-SEV-003 round —
the digest bound LAST (`db023430`) + the local trusted-gate reproduction green BEFORE the
push (run-08; run-07 the disclosed first-attempt RED). THE ONE-ROUND SEV CHAIN: round 1
(agent-4f2b9d6a) PASS, zero open P0/P1/P2, five P3 notes routed/recorded. The full account:
record 62 §4 + CLAIM-070's rule-4 close row + WORKLOG Task 87.

## §2 The session/dwell slice's contract (PLAN's 4C row elaborated one phase deep at P4-C slice one's landing)

**The letter:** D-010's durable behavior data as the reading-session checkpoint events (the
RTM §2.10 reservation: behavior events INSIDE the D-010 boundary):

- **The event vocabulary** — session start/end + coarse-position checkpoints + dwell at
  passage granularity: explicit, durable, owner-scoped rows (ONE append-only migration
  0015_reading_session; the serving-generation binding the position surface established).
- **The write command** — through the spine's own ack contract (idempotent, the frozen
  grammar, the client outbox ride); D-010's boundary as TYPED REFUSALS at the write
  boundary (keystroke/mouse-shaped payloads, search-query/agent-prompt event kinds —
  refused named, never silently stored).
- **The read arm** — the session/dwell listing bounded/paginated on the P4-00b contract;
  the coarse position composes the LANDED position surface (never a second position path).

**The design boundary (the acceptance the RED pins):** the event vocabulary typed + durable;
the D-010 boundary refusals honest at the write boundary; the read arm
bounded/paginated/api_version'd; the owner isolation; the reader-client exclusion held
(P4-B's repo).

## §3 The slice chain in flight

commit A (this commit: the post-#105 five-area reconciliation + CLAIM-071 opened + record 63
minted; the branch pushed EARLY per the standing owner instruction) → the RED
(test_session.py alone at `fd6fb9f`, tests-only per LAW-11) → the typed red-record binding →
the GREEN → the measured set → the SEV round(s) → the artifact finalize → the artifact
re-bind → the push → the PR → the five checks → the merge-gate review (D-042 (1a)) → **the
merge under INT-145** → the post-merge verification → the following P4-C slices + P4-D..F —
NO PAUSE EVEN FOR UPDATES (INT-146).
