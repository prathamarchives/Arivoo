# Arivo — your reading and study environment (backend)

Arivo is a personal reading/study environment: you import documents, highlight
and bookmark them, write notes, and find everything again by keyword search —
with a backend that tells you the truth about what is saved, where, at every
step. This repository is the **backend and the command-line contract client**
(the reader UI lives in its own repository and works through the same surface).

- **Day one in five commands** (below)
- Every write answers with an explicit durability state (`durability_rung=…`)
- Every response names the client/API version (`api_version=1`) — the
  compatibility contract's foundation
- Every error is a named code with a repair hint — never a stack trace
- Your library exports to a self-contained archive and restores byte-identical

## Requirements

- Python 3.9+ (standard library only — no pip packages)
- `psql` (the PostgreSQL client) on your PATH
- A PostgreSQL 14+ server you can reach (17 recommended)

## Connection

The tools read the standard PostgreSQL environment variables —
**`PGHOST`** (default `127.0.0.1`), **`PGPORT`** (default `5432`),
**`PGUSER`** (default `postgres`), and **`PGDATABASE`** (default `postgres`;
set this to the database you want as your library). Set them once per shell:

```sh
export PGHOST=127.0.0.1 PGPORT=5432 PGUSER=postgres PGDATABASE=my_library
```

## Setup

```sh
make migrate          # create/upgrade the schema in PGDATABASE (safe to re-run)
make verify-schema    # observation-only check of what is applied
python3 harness/migrate.py --help   # usage; --verify for the observation-only report
```

## Day one: import → highlight → bookmark → note → search

```sh
# 1. Import a document (a new work by title, or --work-id for another edition)
python3 harness/commands.py import_source --owner me --client-id my-cli \
    --idem-key imp-001 --title "The Quiet Harbor" --file mybook.md

#    The ack names what happened and where it stands:
#    ACK ... status=committed result_ref=<source-id> work_id=<work-id> durability_rung=local_durable api_version=1

# 2. (Optional but recommended) extract the passages and index the source
#    (its own module — not a commands.py verb)
python3 harness/extract.py --owner me --actor owner --client-id my-cli \
    --idem-key ext-001 --source-id <source-id>

# 3. Highlight a passage (character offsets into the stored bytes)
python3 harness/commands.py create_highlight --owner me --client-id my-cli \
    --idem-key hl-001 --source-id <source-id> --start 0 --end 42

# 4. Bookmark a place to come back to
python3 harness/commands.py create_bookmark --owner me --client-id my-cli \
    --idem-key bm-001 --source-id <source-id> --start 0 --end 20

# 5. Write a note — long-form, and able to reference your highlight
python3 harness/commands.py create_note --owner me --client-id my-cli \
    --idem-key nt-001 --content "The harbor scene sets the whole theme." \
    --ref highlight:<highlight-id>@1

# 6. Find your stuff later (multi-term AND search)
python3 harness/query.py search --owner me harbor theme
#    # api_version=1 kind|entity_id|revision|matched_terms   <- the versioned header labels the rows
#    source|<source-id>|1|2
#    highlight|<highlight-id>|1|1
#    note|<note-id>|1|2
```

Read things back: `get-source`, `get-capture`, `get-bookmark`, `get-note`,
`get-history`, `resolve-anchor` — and the three **bounded, paginated** list
arms `list-captures`, `list-bookmarks`, `list-notes` (all on
`harness/query.py`, `--owner` required; you only ever see your own material).
Every list response opens with `# api_version=1`, closes with the truth
marker `# more=true` or `# more=false` (an empty library answers those two
lines alone — never silence), and is **bounded**:

```sh
python3 harness/query.py list-notes --owner me                 # the default page (100)
python3 harness/query.py list-notes --owner me --limit 50      # a smaller page
python3 harness/query.py list-notes --owner me --limit 50 --after <last-id>
#    # api_version=1
#    <note-id> ...
#    # more=true     <- more pages exist; the next --after is the LAST printed id
```

`--limit` accepts 1..1000 (the default 100); a limit outside the bounds, a
non-integer limit, or a non-id `--after` cursor refuses with the typed
`ARV-QRY-004` — never a silent clamp, never an unbounded dump. Every read
body (the get-* JSON, every history row, `resolve-anchor`'s answer) carries
`"api_version": 1` alongside its own fields.

## The idempotency contract (accidental double-runs are safe)

Every command takes `--idem-key`. Run the same command with the same key and
body again and you get `status=replayed` with the original result — never a
duplicate. Same key with a *different* body is refused with `ARV-CMD-409`.

## Durability states (what "saved" means)

Every write ack carries `durability_rung=local_durable` **and**
`api_version=1`: the effect, its command-log row, and its sync intent
committed in ONE transaction on your database — on the committed AND the
replayed form of every acknowledgment. If you use the sync driver
(`harness/sync.py`), the outbox states are explicit — `pending → delivered →
acknowledged` (or `retryable` / `failed` / `uncertain`, each with a named
reason). "Request started" is never "saved"; only the ack is.

## Format capabilities + extraction readiness (what the system can do)

`harness/capability.py` declares, measures, and reserves:

```sh
python3 harness/capability.py matrix      # the declared per-format rows
#    {"format": "text/plain", "native_text": true, "scan_ocr": false,
#     "layout": "reflow", "extraction": "supported", "approved": true,
#     "extractor": "arivoo-text-blocks.v1", "api_version": 1}

python3 harness/capability.py measure --owner me --source <source-id>
#    {"source_id": "...", "media_type": "text/plain", "state": "ready",
#     "generation_id": "...", "ordinal": 1, "passages": 3, "coverage": 1.0,
#     "extractor": "arivoo-text-blocks.v1", "api_version": 1}
```

The readiness states are typed answers, never a silent miss:
`ready` (a current generation, its digest binding verified),
`not_extracted` (imported, no generation yet), `building` (an extraction in
flight — a crashed attempt leaves this row and the same-key retry completes
it), `failed` (the last attempt failed), `stale` (the digest binding broke —
derived honestly, structurally unreachable today since a source row is
immutable). The measured facts (the passage count, the coverage fraction)
are derived from your actual source at read time — never asserted.

**The read-position surface is reserved** (`source-open/position` — opening
a source at a saved position and returning to it): it lands with P4-A/B on
the bookmark/anchor machinery; the reader UI itself is the separate
repository. `python3 harness/capability.py surfaces` prints the reservation
registry.

## Backup / restore (move to a new machine)

```sh
python3 harness/export.py export --owner me --out my-archive-dir
# on the new machine (a clean, migrated database):
python3 harness/export.py restore --archive my-archive-dir
# RESTORED ... state=restored derived_state=pending_rebuild
#             rebuild=extract_source+rebuild_keyword_index
```

The restore is transactional (an interruption leaves nothing half-done), the
destination's purge ledger wins (a purged item cannot be resurrected), and
the completion names the derived-rebuild step: after a restore, re-run
`extract_source` per source and `rebuild_keyword_index` to restore search
and anchor resolution to fully operational.

## Revisions, tombstones

Nothing authored is ever overwritten: `revise_note` / `revise_highlight`
append new immutable revisions; `tombstone_*` hides from ordinary retrieval
and `restore_*` brings an item back; the full history is always readable via
`get-history`.

## Where to read more

`AGENTS.md` (the repository's engineering map), `PLAN.md` (the requirements
and phase plan), `RTM.md` (the requirements traceability matrix). This file
is the user-facing entry; those are the engineering documents behind it.
