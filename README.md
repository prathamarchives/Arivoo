# Arivo — your reading and study environment (backend)

Arivo is a personal reading/study environment: you import documents, highlight
and bookmark them, write notes, and find everything again by keyword search —
with a backend that tells you the truth about what is saved, where, at every
step. This repository is the **backend and the command-line contract client**
(the reader UI lives in its own repository and works through the same surface).

- **Day one in five commands** (below)
- Every write answers with an explicit durability state (`durability_rung=…`)
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
#    ACK ... status=committed result_ref=<source-id> work_id=<work-id> durability_rung=local_durable

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
#    # kind|entity_id|revision|matched_terms     <- the header labels the rows
#    source|<source-id>|1|2
#    highlight|<highlight-id>|1|1
#    note|<note-id>|1|2
```

Read things back: `get-source`, `get-capture`, `get-bookmark`, `get-note`,
`list-captures`, `list-bookmarks`, `list-notes`, `get-history`,
`resolve-anchor` — all on `harness/query.py` (`--owner` required; you only
ever see your own material).

## The idempotency contract (accidental double-runs are safe)

Every command takes `--idem-key`. Run the same command with the same key and
body again and you get `status=replayed` with the original result — never a
duplicate. Same key with a *different* body is refused with `ARV-CMD-409`.

## Durability states (what "saved" means)

Every write ack carries `durability_rung=local_durable`: the effect, its
command-log row, and its sync intent committed in ONE transaction on your
database. If you use the sync driver (`harness/sync.py`), the outbox states
are explicit — `pending → delivered → acknowledged` (or `retryable` /
`failed` / `uncertain`, each with a named reason). "Request started" is never
"saved"; only the ack is.

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
