# Arivo — Day-One Acceptance Report (Uncoached Clean-Clone Run)

- **Date:** 2026-11-05
- **Who:** a technically capable new user, no prior exposure to the product
- **Repo (clean clone, release revision):** `/home/z/my-project/verification/acceptance-clone` @ `3b5ed28` ("Merge pull request #94 … slice/claim-060-p309-export-restore")
- **Machine:** Python 3.12.16, GNU Make 4.4.1, PostgreSQL 17.11 at 127.0.0.1:5433 (user `postgres`, trust auth), provided databases `arv_acceptance` and `arv_acceptance_2` (both empty at start; no product schema anywhere)
- **Method:** only the repository's own documented surfaces were used — the root documents (AGENTS/STATE/EXECUTION/RTM/PLAN/GLOSSARY), the session records under `context/extracted/`, the `Makefile`, and the CLIs' own `--help`. Product source was read only to resolve one connection question (which env var selects the database). No product table was ever written by hand; the only direct SQL was read-only `SELECT`/`\dt` inspection and one `CREATE DATABASE arv_acceptance_3` (infrastructure, for the interrupted-restore test; contains no hand-written product rows).

---

## 1. Setup log (commands + observed results)

**Orientation.** There is no `README.md`. The repo's self-described entry map is `AGENTS.md` ("You are an agent in this repository…"), which points to `STATE.md`, `CLAIMS.md`, `EXECUTION.md` (the contract map), `RTM.md` (the product contract freeze), `GLOSSARY.md` (vocabulary: Work/Source/Highlight/Anchor/Bookmark/Note, durability ladder). The product is a **backend + command-line contract client** (`harness/commands.py` write path, `harness/query.py` read path, `harness/extract.py`, `harness/sync.py`, `harness/export.py`), per RTM SYS-09 ("the contract client (the CLI — … never the reader UI)").

**Rig.** `psql` is not on the default `PATH`; the health check itself names the repair (verbatim):

```
$ python3 harness/health.py
FAIL ARV-RIG-001: PostgreSQL unreachable through the adapter (PGHOST/PGPORT/PGUSER per harness/adapters/pg.py) — ARV-DB-001: the psql client is missing from PATH — install the PostgreSQL client (CI provisions it; locally: the rig's extracted Debian packages)
      repair: start the rig (locally the .pg cluster, port 5433; CI the postgres:17 service) — FACT-001 records the engine parity requirement
```

Sourcing the rig env (`PATH`, `LD_LIBRARY_PATH`, `PGHOST=127.0.0.1 PGPORT=5433 PGUSER=postgres`):

```
$ python3 harness/health.py
OK ARV-RIG-001: PostgreSQL 17.11 (Debian 17.11-0+deb13u1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
```

**Schema install.** My first migration attempt — `python3 harness/migrate.py --help` — did not print help; it ran and said:

```
ARV-MIG-001: nothing to apply — no-op (all recorded, unchanged)
```

which was confusing: the two acceptance DBs were empty. Cause (found by read-only inspection): the harness defaults to the `postgres` database, which on this rig already carried the `arv` schema from prior engineering use. The Makefile's connection comment documents only `PGHOST · PGPORT · PGUSER` — **`PGDATABASE` is not mentioned anywhere user-facing** (it appears only inside a session-record war story, record 48, and in the source). Setting it explicitly:

```
$ export PGDATABASE=arv_acceptance
$ python3 harness/migrate.py
applied 0001_baseline
applied 0002_evidence_event
...
applied 0013_purge_ledger          (13 migrations total)

$ make verify-schema
verify OK: 13 migration(s) applied, checksums match
```

`arv_acceptance` now has 20 tables in schema `arv` (work, source, anchor, passage, extraction_generation, highlight(+_lifecycle), bookmark(+_lifecycle), note(+_lifecycle,+note_reference), command_log, evidence_event, import_journal, keyword_index, outbox, server_outbox, purge_ledger, schema_migrations) — confirmed by read-only `\dt arv.*`.

**CLI discovery.** `python3 harness/commands.py --help` lists the write surface: `record_event, import_source, create_highlight, create_bookmark, revise_highlight, tombstone_highlight, restore_highlight, move_bookmark, tombstone_bookmark, restore_bookmark, create_note, revise_note, rebuild_keyword_index, tombstone_note, restore_note`. `harness/query.py --help` lists the read surface: `get-capture, get-source, get-history, get-bookmark, get-bookmark-history, get-note, get-note-history, list-captures, list-bookmarks, list-notes, resolve-anchor, search`. `harness/export.py`: `export | restore`. `harness/sync.py`: `sync | status`. `harness/extract.py`: the extraction command. Every subcommand has a working `--help`.

**Self-check (optional sanity):** `python3 harness/tests/test_commands.py` → `GREEN — S3 acceptance (a)-(e) observed: idempotency, atomicity, crash recovery, ack ordering, owner-scoped keyspaces` (exit 0).

**Setup outcome: SUCCESS** (with two friction points: no user README; `PGDATABASE` undocumented).

---

## 2. The walk

I authored a real 6-paragraph essay, `/home/z/my-project/verification/acceptance-scratch/small-winds.md` ("The Cartographer of Small Winds", 1,829 bytes / 1,823 chars, with em-dashes and hard line wraps), containing distinctive searchable words: *lighthouse, kelp, chartreuse, Marta, rumor*.

### Step 1 — Import

```
$ python3 harness/commands.py import_source --owner z --client-id acceptance-cli \
    --idem-key import-small-winds-001 --title "The Cartographer of Small Winds" \
    --file …/small-winds.md --media-type text/markdown --acquired-via local-file
ACK command=import_source idem-key=import-small-winds-001 status=committed result_ref=01a1ace3-24f6-74c8-8247-b23e5a2c73d5 work_id=01a1ace3-24f5-718e-9a81-fa56303cd16a
```

**Acknowledgment language (verbatim):** `status=committed result_ref=<source-uuid> work_id=<work-uuid>`. No durability rung named (see Finding 4).

Read-back (`query.py get-source --owner z --id …`): `import_state: complete, source_version: 1, digest: f9d2ea52…, byte_size: 1829` — digest matches my file's sha256 exactly.

Derived layers (documented as required for search): `extract.py` then `rebuild_keyword_index`:

```
ACK command=extract_source idem_key=extract-small-winds-001 status=committed result_ref=01a1ace3-5d41-… source_id=01a1ace3-24f6-…
ACK command=rebuild_keyword_index idem_key=kwi-001 status=committed result_ref=01a1ace3-5d90-… index=rebuilt durability_rung=local_durable
```

### Step 2 — Highlight, bookmark, note

Highlight (offsets are **character** offsets into the decoded text — discovered by experiment; see Finding 7):

```
$ python3 harness/commands.py create_highlight --owner z --client-id acceptance-cli \
    --idem-key hl-spotlight-001 --source-id 01a1ace3-24f6-… --start 1130 --end 1264
ACK command=create_highlight idem_key=hl-spotlight-001 status=committed result_ref=01a1ace3-8ff3-706b-b6f4-e36da5b0dc13 revision=1 durability_rung=local_durable
```

`get-capture` returned exactly the passage I intended, with context and digest:

```json
{"id": "01a1ace3-8ff3-…", "revision": 1,
 "selected_text": "Attention is not a spotlight that we aim; it is a net that\nwe weave, and the mesh of the net is set by whatever we have loved longest.",
 "source_id": "01a1ace3-24f6-…", "source_digest": "f9d2ea52…", "start": 1130, "end": 1264,
 "context_before": "invisible to\npeople in a hurry. ", "context_after": "\nThat is why two readers can sit",
 "media_type": "text/markdown", "created_at": "2026-11-05T18:05:57.107062+00:00"}
```

Bookmark at the final paragraph (1436..1495):

```
ACK command=create_bookmark idem_key=bmk-proposal-001 status=committed result_ref=01a1ace3-dbea-711a-b7cb-397aeb1a033a revision=1 durability_rung=local_durable
```

`get-bookmark`: `state: "resolved"`, with `anchor_id`, `generation_id`, `passage_ids` (bookmarks expose their anchor; highlights do not — Finding 5).

Note referencing the highlight (the `--ref KIND:ID[@REV]` surface; highlights must pin a revision):

```
$ python3 harness/commands.py create_note --owner z --client-id acceptance-cli \
    --idem-key note-small-winds-001 --content-file …/note-001.md \
    --ref highlight:01a1ace3-8ff3-706b-b6f4-e36da5b0dc13@1
ACK command=create_note idem_key=note-small-winds-001 status=committed result_ref=01a1ace4-0cf1-7ef7-a0e6-0e5dfa0a746a revision=1 durability_rung=local_durable
```

`get-note` round-tripped the content **losslessly** (pipes `|`, em-dashes, quotes, embedded newlines all intact) and shows the reference: `"refs":[{"kind" : "highlight", "id" : "01a1ace3-8ff3-…", "revision" : 1}]`.

I then revised the note once (`revise_note`, new idem key), producing revision 2 with both revisions retrievable via `get-note-history` (revision 1: 569 chars, revision 2: 803 chars, full content each).

### Step 3 — Finding my stuff later

After the revision and other activity:

- `search --owner z chartreuse` → `note|01a1ace4-…|2|1` and `source|01a1ace3-…|1|1` (finds both my note and my source)
- `search --owner z net weave` (AND) → `highlight|…|1|2` + `source|…|1|2`
- `search --owner z zxqvubble` (nonexistent) → empty, exit 0
- `list-captures` / `list-bookmarks` / `list-notes` → each exactly my one item; `get-capture`, `get-bookmark`, `get-note`, `get-note-history` all return the full stored state.

**Truthfulness of durability language (quoted throughout the run):**
- Write acks: `status=committed … durability_rung=local_durable` — the rung names what the *server independently knows*, never "saved" from the request's perspective. This matches the documented ladder (`local_durable → queued → server_durable`).
- `sync.py status --owner z` (before sync): `SYNC-STATUS owner=z pending=5` + one `SYNC-QUEUED <key> state=pending attempts=0` line per authoritative write — an honest queue view; the derived commands (extract, index) are correctly absent.
- `sync.py sync --owner z --server-db arv_acceptance_2`: five `SYNC key=… state=acknowledged server_ref=<same ids>` lines, `SYNC-DONE owner=z rows=5`; status afterwards: `SYNC-STATUS owner=z acknowledged=5`. No duplicates were created on the destination (all five keys already existed there from the restore → replays).

### Step 4 — Leave and come back (fresh start)

Each CLI invocation is a fresh process; to make "reopen" maximal I snapshotted all nine read commands, then re-ran them from a completely clean shell (`env -i`, fresh env sourcing), and diffed:

```
$ diff -r snap-before-reopen snap-after-reopen
IDENTICAL
```

Byte-identical, including note content, history, search results, and list outputs. After all later activity (abnormal events, sync), a final re-check was again **byte-identical**.

### Step 5 — Move to a new machine (backup/restore → `arv_acceptance_2`)

```
$ python3 harness/export.py export --owner z --out …/arivo-export-001
EXPORTED owner=z dir=…/arivo-export-001 tables=13 rows=21 state_hash=380614d377b4ce3f
```

The archive is a directory: `manifest.json` (format `arv-export-1`, owner, canonical-sorted table rows) + `blobs/f9d2ea52…` (my essay, 1,829 bytes — sha256 identical to the original file).

Destination setup + restore:

```
$ PGDATABASE=arv_acceptance_2 python3 harness/migrate.py     (13 migrations applied)
$ PGDATABASE=arv_acceptance_2 python3 harness/export.py restore --archive …/arivo-export-001
RESTORED owner=z ledger_as_of=empty backup_expiry=the D-029 documented window bounds this archive's resurrection exposure tables=13 rows=21 state_hash_match=true
```

Verification through the product's read surfaces, diffed against the pre-export snapshots: `get-source`, `get-capture`, `get-note`, `get-note-history`, and all three `list-*` outputs were **identical**. Two differences, both in derived state:

1. `get-bookmark` on the restored DB initially read `state: "unresolved", cause: "no-current-generation"` (the original read `resolved` with generation/passage ids).
2. `search` initially returned **nothing** on the restored DB.

Running the two documented derived-build commands on the destination (`extract.py` + `rebuild_keyword_index`) fixed both: the bookmark reads `resolved` again (with new derived generation/passage ids — expected for rebuilt state) and search results became **identical** to the original DB. So: all authoritative content, revisions, references and history arrived intact; derived layers must be rebuilt, and the restore output does not tell you that (Finding 1).

The restore ack's honesty about the purge residual is remarkable for a backup tool: `ledger_as_of=empty backup_expiry=the D-029 documented window bounds this archive's resurrection exposure` — it explicitly does not claim purge-safety it cannot know.

### Step 6 — Abnormal-but-realistic events

**(a) Double-click duplicate** (same idem key, same body):

```
ACK command=import_source idem_key=import-small-winds-001 status=replayed result_ref=01a1ace3-24f6-… work_id=01a1ace3-24f5-…
```

Same result_ref, `status=replayed`, still exactly one source, title and `source_version: 1` unchanged.

**(b) Same key, different body** (the "did I edit between retries?" case):

```
FAIL ARV-CMD-409: idempotency key 'import-small-winds-001' is already recorded with a DIFFERENT body (no silent overwrite — exactly-once is a contract, not a preference)
      repair: use a new idempotency key for a new body; the same key must mean the same command
```

Exit 1, zero effect.

**(c) Interrupted restore** (documented crash injection `--crash-at pre-commit`, into a scratch migrated DB): the process was SIGKILLed (exit 137, no output); the destination had **0 authoritative rows** (clean); an immediate retry restored successfully (`tables=13 rows=21 state_hash_match=true`). No half-restored library.

**(d) Repeated restore** into the already-restored `arv_acceptance_2`:

```
FAIL ARV-EXP-002: the destination is not clean (authoritative rows exist for this owner) — a restore is once-per-destination, never a silent mixed state
      repair: restore into a clean migrated destination, or purge the destination through the governed flow first
```

Data intact after the refusal.

**(e) Malformed/hostile inputs** — all typed, named, zero-effect refusals with repair hints:

```
FAIL ARV-NTE-006: the highlight reference 'highlight:01a1ace3-…' must name the target revision (kind:id@rev — version-aware by construction)
FAIL ARV-NTE-003: the referenced highlight (00000000-…@1) does not exist in the caller's scope — absent, another owner's, and a nonexistent target revision are the SAME refusal, never a side channel
FAIL ARV-CAP-003: offsets [500,500) are invalid for a 1823-character text — never clamped, never guessed
FAIL ARV-CAP-003: offsets [100000,100500) are invalid for a 1823-character text — never clamped, never guessed
```

**(f) Cross-owner privacy probe** (SYS-03): as `--owner someone-else`, reading my note by exact id returns the *same* refusal as a nonexistent id (`ARV-QRY-001 … absent and another owner's are the SAME refusal, never a side channel`); `search` and `list-notes` return empty. No existence leakage.

---

## 3. Findings (numbered, with severity)

**No P0 (data loss / wrong data) and no P1 (broken core flow) were observed.** Everything I attempted either worked as documented or failed safely with a named reason.

1. **[P2] Restore leaves the library not-yet-operational and doesn't say so.** After `restore`, `search` silently returns nothing and the bookmark reads `unresolved / no-current-generation` until the user figures out they must re-run `extract.py` and `rebuild_keyword_index` on the destination. The RTM's own state machine distinguishes `restored` from `fully_operational` (via "rebuild derived"), but the `RESTORED` ack doesn't surface which state you're in or name the rebuild step. Worse, the empty search result contradicts the product's own documented search contract ("searchable or explicit lag/failure, never a silent miss") — an empty index and a no-match are indistinguishable to the user. No data was lost (the bookmark's `unresolved` was honest and typed), but a user who restores and immediately searches would reasonably conclude their library didn't arrive.

2. **[P2] No user-facing entry document.** The repository's front door is `AGENTS.md` — an agent-workspace map written in dense internal jargon (claims, SEV rounds, INT-xxx chains), followed by a 570-line requirements-freeze matrix (RTM). The actual product usage (which CLI, which env vars, which order: migrate → import → extract → index → capture) had to be assembled from `--help` surfaces plus engineering session records. For a day-one user this is the single biggest barrier: the machinery is excellent once found, but finding it took longer than the entire functional walk.

3. **[P3] `PGDATABASE` is undocumented in the user-facing connection docs.** The Makefile documents `PGHOST · PGPORT · PGUSER` only; the database selector appears solely in a session-record war story and the source. Following the Makefile alone installs the schema into the `postgres` database. On my rig that DB was already migrated (so I got a misleading `ARV-MIG-001: nothing to apply — no-op`); on a truly fresh machine the user would silently set up the wrong database. Also, `python3 harness/migrate.py --help` does not print help — it executes the migration (argparse has no `--help` at that level and ignores the unknown flag's intent).

4. **[P3] Acknowledgment vocabulary is inconsistent across commands.** RTM SYS-01/§4.3 freezes "every write command returns `{status, durability_rung, …}`". The `import_source` and `extract_source` acks omit `durability_rung` (only `status=committed result_ref=… work_id=…`), while highlight/bookmark/note/index acks name `durability_rung=local_durable`. This is an omission (underclaim), not an overclaim — the commit really happened — but the frozen contract says the rung is always named.

5. **[P3] A highlight's anchor is not observable.** `get-capture` doesn't include the anchor id, and `resolve-anchor` requires one; my attempt to resolve the highlight's anchor using the highlight id was refused (`ARV-QRY-001`). The only anchor id I ever saw came from `get-bookmark`. The documented anchor-resolution surface is therefore effectively unusable for highlights — the entity the RTM calls "a highlight without its anchor is not durable."

6. **[P3] Search output is unlabeled.** Rows like `source|01a1ace3-…|1|2` (apparently kind|id|revision|hit-count) carry no header or explanation; the user infers the format. Minor, but this is the product's findability surface.

7. **[P3] Highlight offset semantics are undocumented at the point of use.** `--start/--end` are character offsets into the decoded text (my file: 1,823 chars vs 1,829 bytes; I learned this from the refusal message "a 1823-character text" after probing). The `--help` doesn't say bytes-vs-chars, and the ack doesn't echo the selected text — I had to `get-capture` to confirm I'd highlighted the right passage. A byte-offset assumption would select a silently-shifted span with no warning.

8. **[P3] Unhandled `BrokenPipeError` traceback** when piping `query.py` output through `head` (cosmetic; the data was already printed).

9. **[Delight] The diagnostics contract is genuinely excellent.** Every single refusal names a code, states the invariant protected, and gives a repair instruction — from the missing-psql health check to `ARV-CMD-409`, `ARV-EXP-002`, `ARV-NTE-003/006`, `ARV-CAP-003`, `ARV-QRY-001`. Errors read as instructions, not stack traces.

10. **[Delight] Exactly-once held everywhere I pressed it.** Double-click duplicate → `replayed` with the same result_ref; same-key-different-body → named conflict with zero effect; sync into an already-populated (restored) database → all five commands replayed, zero duplicates; interrupted restore → destination provably clean, retry clean; repeated restore → refused. And the whole library read byte-identically after a fresh reopen and again after all of the abuse.

---

## 4. Verdict

**Would I trust Arivo with my reading notes today?** For *data integrity*, yes — and this is the strongest such showing I've seen in a day-one backend. Every write was acknowledged in honest, checkable language (`status=committed … durability_rung=local_durable`, never a vague "saved"); every duplicate, conflict, crash, and hostile input produced a typed refusal with zero silent effects; my content survived a fresh reopen byte-identically; and the export/restore moved my entire library — including note revisions, references, and lifecycle history — to a second database with a matching state hash. The one wart in the move (derived index not rebuilt after restore) lost me *findability*, not data, and the bookmark told me so honestly (`unresolved / no-current-generation`) even when search stayed silent.

For *actually living in it as a reader*, not yet. What's missing, in the order I felt it:

1. A front door for humans: a README/quickstart that names the CLIs, the env (`PGDATABASE`!), and the canonical first session (migrate → import → extract → index → highlight/bookmark/note → search).
2. A restore that finishes the job (or at least prints "run extract + rebuild_keyword_index to restore search").
3. A read path: there is no way to *read* my document through the product — no passage/full-text read command, only capture excerpts and search hits pointing at a source id. For a reading environment, I can highlight and find, but not read.
4. Anchor visibility for highlights, labeled search output, and pagination on the list surfaces (the docs place some of this in Phase 4).
5. The governed purge / delete story is explicitly not built yet (the CLI has tombstone/restore for captures; no owner-facing erasure flow — the repo says so itself, which I appreciate).

Net: a trustworthy spine with a thin, sometimes silent, user surface. I would keep using it for real notes **today**, on the strength of its durability behavior — but I'd keep my source files until the restore-rebuild path and a real read surface exist.
