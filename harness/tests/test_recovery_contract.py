#!/usr/bin/env python3
"""harness/tests/test_recovery_contract.py — P4-F acceptance suite (CLAIM-079,
the recovery/regression proof + the contract gate; the PLAN 4F row elaborated
one phase deep at the #113 landing; record 71 §2). Red-first (LAW-11): at
CLAIM-078's merged head d21ca44e the suite fails with ARV-TEST-000
(machinery-absent; red-01.txt) — harness/client.py (the clean external client
driver, P4-F's named proof vehicle) lacks the P4-F condition set.

THE CONTRACT (P4-F's letter): the clean EXTERNAL client extended with the
recovery/regression condition set over the REAL CLIs — the recovery walk (a
crash mid-sequence: the durable prefix survives, the uncertain-ack idempotent
replay, the post-restart reads truthful), the full-lifecycle export/restore
round-trip (every journal REVISION — the lossless law; the note @-references;
the reading lists + membership events; the session/dwell events; the restore
byte-faithful, the post-restore reads byte-equal), the rebuild parity (the
index derived, never governing), the phase-level owner isolation, the
supported-prior-state migration (real prior-state content migrating forward,
surviving, obeying the current substrate), the sync-conflict walk (the typed
conflict, never a silent overwrite), and the no-privileged-path law over the
new conditions — a PROOF slice over the landed surface, no new product
commands (a defect found by the proof repairs the owning family in its own
bounded increment).

Cases (the RCW registry; each pin's full statement lives at its check()):
  RCW-01 the recovery walk: a journal-authoring sequence interrupted mid-write
         by the crash matrix's post-commit-pre-ack arm (exit 2, no ack — the
         honest unknown) — the durable prefix survives (the pre-crash blocks
         readable through fresh reads), the uncertain-ack replay converges
         (the same-key replay acks status=replayed with the SAME result_ref),
         and the post-restart reads are truthful (the whole sequence durable)
  RCW-02 the full-lifecycle export/restore: one owner walk writing every
         landed family (a source + position + highlight + bookmark + notes
         with @-references + journal blocks WITH revisions + a reading list
         with membership events + session/dwell events) exported to an
         archive and restored into a clean destination — the post-restore
         reads BYTE-EQUAL the pre-export reads (the lossless law: every
         journal revision round-trips, never truncated); the agent
         credentials NEVER ride the export (minted before export, absent
         from the archive + the restored reads)
  RCW-03 the rebuild parity: the keyword index rebuilt from the authored rows
         (rebuild_keyword_index) — the search answers unchanged across the
         rebuild (the index derived, never governing visibility)
  RCW-04 the phase-level owner isolation: one walk's cross-family invisibility
         — owner B sees NONE of owner A's families (the library, the journal,
         the lists, the session events), and the byte-equal no-oracle holds
         at the phase level
  RCW-05 the supported-prior-state migration: a database carrying real
         prior-state content (the landed families' rows at a prior baseline
         — 0001..0014 applied, content written) migrates FORWARD through the
         chain to the current head — the content survives, the post-
         migration invariants hold (the append-only triggers live, RLS
         forced), and the post-migration reads answer the prior content
  RCW-06 the sync-conflict walk: the two-DB delivery with a CONFLICTING write
         (the same idem key, different bodies) — the typed conflict refusal
         (ARV-CMD-409 surfaced as the row's failed state with the named
         reason), BOTH bodies preserved, never a silent overwrite
  RCW-07 the no-privileged-path extension: the P4-F conditions hold the same
         law as the walk — no direct database tooling, no role names, no SQL
         anywhere in harness/client.py (the clean client CLEAN, mechanically
         so — the scan extended over the new condition functions)
  RCW-08 the contract-gate check: every P4 family the walk proves is REAL at
         the boundary (each family's read arm answered during the walk — the
         phase gate's mechanical form: the observed families recorded, none
         asserted from memory)

THE BOUNDED EXCLUSIONS (record 71 §2's letter): no reader-client UI (P4-B's
separate repo); no real-user validation (blocked without an actual
reader/journal host); no new product commands (the proof slice over the
landed surface); no diagram rendering (the reference STRUCTURE round-trips);
no Phase 5 retrieval machinery.

Run: python3 harness/tests/test_recovery_contract.py   (exit 0 = green)
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harness.adapters import pg  # noqa: E402

FAILS: list[str] = []

# the machinery-absent probe (the RED gate): the P4-F condition set is this
# slice's machinery — absent at the RED tree (harness/client.py imports fine;
# the condition functions do not exist there).
_probe = subprocess.run([sys.executable, "-c",
                         f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
                         "from harness import client\n"
                         "print(all(callable(getattr(client, n, None)) for n in ("
                         "'condition_recovery_walk', 'condition_export_restore', "
                         "'condition_rebuild_parity', 'condition_phase_isolation', "
                         "'condition_prior_state_migration', 'condition_sync_conflict')))"],
                        capture_output=True, text=True, timeout=60,
                        env=dict(os.environ, PGDATABASE="arv_p4f_red_probe_absent"))
if not (_probe.returncode == 0 and _probe.stdout.strip() == "True"):
    print("FAIL ARV-TEST-000: the P4-F recovery-contract machinery is absent "
          "(machinery-absent class; harness/client.py's P4-F condition set "
          f"(condition_recovery_walk and its siblings) importable: "
          f"{_probe.returncode == 0}) — the implementation lands after this "
          "RED, never before it (LAW-11)")
    sys.exit(1)

DB = ENV = None

TEXT = ("The recovery-contract corpus opens here.\n"
        "The second paragraph carries the meridian token.\n"
        "The third paragraph closes the recovery walk.\n")

# the families the walk writes (RCW-08's phase gate compares against this)
P4_FAMILIES = ("library", "position", "highlight", "bookmark", "note",
               "note_reference", "journal_block", "reading_list",
               "reading_session")


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def jline(r: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(next(ln for ln in r.stdout.splitlines() if ln.strip()))
    except Exception:
        return {}


def jlines(r: subprocess.CompletedProcess) -> list:
    return [json.loads(ln) for ln in r.stdout.splitlines()
            if ln.strip() and not ln.startswith("#")]


def search_ids(r: subprocess.CompletedProcess) -> list:
    out = []
    for ln in r.stdout.split("\n"):
        if ln.strip() and not ln.lstrip().startswith("#"):
            out.append(ln.strip())
    return out


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4f")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    ENV.pop("ARIVO_AGENT_TOKEN", None)  # the suite controls the channel explicitly
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        from harness import client  # the clean external driver (this slice's machinery)

        # ---- RCW-01 — the recovery walk
        cond = client.condition_recovery_walk(ENV, TEXT)
        ok1 = (cond["prefix_survives"] is True
               and cond["crash_exit"] == 2
               and cond["replay_exit"] == 0
               and cond["replay_replayed"] is True
               and cond["post_restart_reads"] is True)
        check("RCW-01", ok1,
              "the recovery walk: a journal-authoring sequence interrupted by the crash "
              "matrix's post-commit-pre-ack arm (exit 2, NO ack — the honest unknown) — the "
              "durable prefix survives (the pre-crash blocks readable through FRESH reads), "
              "the uncertain-ack replay converges (the same-key replay acks status=replayed "
              "with the SAME result_ref), and the post-restart reads answer the whole "
              "sequence truthfully (the state lives in the store, never the session)",
              "harness/client.py's condition_recovery_walk over the crash matrix + the "
              "spine's replay contract — the landed recovery semantics assembled at the "
              "clean boundary")

        # ---- RCW-02 — the full-lifecycle export/restore round-trip
        cond = client.condition_export_restore(ENV, TEXT)
        ok2 = (cond["walk_complete"] is True
               and cond["export_exit"] == 0
               and cond["restore_exit"] == 0
               and cond["journal_revisions"] is True
               and cond["post_restore_byte_equal"] is True
               and cond["credentials_absent"] is True)
        check("RCW-02", ok2,
              "the full-lifecycle export/restore: one walk writing every landed family "
              "(the source + position + highlight + bookmark + notes with @-references + "
              "journal blocks WITH revisions + a reading list with membership events + "
              "session/dwell events) exported and restored into a clean destination — the "
              "post-restore reads BYTE-EQUAL the pre-export reads (the lossless law: every "
              "journal revision round-trips, never truncated); the agent credentials minted "
              "BEFORE the export never ride it (a local access primitive, never owner "
              "content — absent from the archive and the restored reads)",
              "harness/client.py's condition_export_restore over export.py/restore — the "
              "landed export machine widened to the full P4-C family set where the proof "
              "finds the gap (the owning family's bounded repair, record 71 §2's letter)")

        # ---- RCW-03 — the rebuild parity
        cond = client.condition_rebuild_parity(ENV)
        ok3 = (cond["before_exit"] == 0 and cond["rebuild_exit"] == 0
               and cond["after_exit"] == 0
               and cond["parity"] is True)
        check("RCW-03", ok3,
              "the rebuild parity: rebuild_keyword_index re-derives the index from the "
              "authored rows alone and the search answers UNCHANGED across the rebuild "
              "(the same result set before and after — the index derived, never governing "
              "visibility)",
              "harness/client.py's condition_rebuild_parity over the landed rebuild "
              "command — the derived-state law observed at the clean boundary")

        # ---- RCW-04 — the phase-level owner isolation
        cond = client.condition_phase_isolation(ENV, TEXT)
        ok4 = (cond["walk_complete"] is True
               and cond["cross_family_invisible"] is True
               and cond["no_oracle"] is True)
        check("RCW-04", ok4,
              "the phase-level owner isolation: one walk's every family invisible to the "
              "other owner (the library, the journal, the lists, the session events — B "
              "sees NONE of A's content), and the byte-equal no-oracle holds at the phase "
              "level (an absent id and another owner's id are the SAME typed refusal "
              "across the families' read arms)",
              "harness/client.py's condition_phase_isolation — the landed owner-isolation "
              "contracts observed in one walk at the clean boundary")

        # ---- RCW-05 — the supported-prior-state migration
        cond = client.condition_prior_state_migration(ENV)
        ok5 = (cond["prior_written"] is True
               and cond["migrate_exit"] == 0
               and cond["content_survives"] is True
               and cond["invariants_hold"] is True)
        check("RCW-05", ok5,
              "the supported-prior-state migration: a database carrying real prior-state "
              "content (the landed families' rows at a prior baseline) migrates FORWARD "
              "through the chain to the current head — the content survives, the "
              "post-migration invariants hold (the append-only substrate live, RLS "
              "forced), and the post-migration reads answer the prior content",
              "harness/client.py's condition_prior_state_migration over the migration "
              "runner — the empty-database oracle's supported-prior-state complement, "
              "observed at the clean boundary")

        # ---- RCW-06 — the sync-conflict walk
        cond = client.condition_sync_conflict(ENV)
        ok6 = (cond["local_exit"] == 0 and cond["server_exit"] == 0
               and cond["sync_exit"] == 0
               and cond["conflict_failed"] is True
               and cond["typed_409"] is True
               and cond["both_bodies_preserved"] is True)
        check("RCW-06", ok6,
              "the sync-conflict walk: the two-DB delivery with a CONFLICTING write (the "
              "same idem key, different bodies — the competing server-side application) "
              "surfaces the typed conflict (ARV-CMD-409 in the row's failed state with "
              "the named reason, terminal and visible) — BOTH bodies preserved (the "
              "local note and the server note each intact), never a silent last-write-"
              "wins for authored content",
              "harness/client.py's condition_sync_conflict over the sync driver — the "
              "landed typed-conflict contract observed at the clean boundary")

        # ---- RCW-07 — the no-privileged-path extension
        src = (REPO / "harness" / "client.py").read_text(encoding="utf-8")
        ok7 = ("psql" not in src and "arv_app" not in src and "arv_read" not in src
               and "INSERT INTO" not in src and "SELECT " not in src
               and "commands.py" in src and "query.py" in src
               and "export.py" in src and "sync.py" in src
               and "migrate.py" in src)
        check("RCW-07", ok7,
              "the no-privileged-path extension: the P4-F conditions hold the walk's law "
              "— no psql, no role name, no SQL anywhere in harness/client.py, and the "
              "recovery surface's every call a real CLI invocation (commands.py, "
              "query.py, export.py, sync.py, migrate.py — the crash arms through "
              "crash.py): the clean client CLEAN over the extended surface, mechanically "
              "so",
              "harness/client.py's discipline: subprocess invocations of the real CLIs "
              "only — the extension never widens the privilege surface")

        # ---- RCW-08 — the contract-gate check (the phase gate's mechanical form)
        # every P4 family the walk proves is REAL at the boundary: the recovery
        # walk itself names the families its fresh reads ANSWERED (the observed
        # set recorded by the condition, never asserted from memory — the
        # merge-time gate in record 71 §5 rides THIS observed set)
        gate = client.condition_recovery_walk(ENV, TEXT)  # re-observed live
        observed = set(gate.get("families", []))
        ok8 = observed >= set(P4_FAMILIES)
        check("RCW-08", ok8,
              "the contract-gate check: every P4 family the walk proves is REAL at the "
              "boundary — the recovery walk's own read arms observed live naming the "
              "families (the library, the position, the highlight, the bookmark, the "
              "note, the note_reference, the journal_block, the reading_list, the "
              "reading_session), the phase gate's mechanical form (the merge-time record "
              "rides the OBSERVED set, never an assertion from memory)",
              "the walk's observed-families set — each family's read arm answered during "
              "the live walk; a missing family names the read arm to extend")

        if FAILS:
            print(f"\nRECOVERY-CONTRACT SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the recovery/contract-gate contract is broken or unimplemented)")
            return 1
        print("\nRECOVERY-CONTRACT SUITE GREEN — RCW-01..08 (the clean external client "
              "over the landed surface: the recovery walk, the full-lifecycle "
              "export/restore, the rebuild parity, the phase-level isolation, the "
              "prior-state migration, the sync conflict, the no-privileged-path "
              "extension, the contract-gate check)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
