#!/usr/bin/env python3
"""harness/tests/test_client_acceptance.py — P4-B slice one acceptance suite
(CLAIM-069, the client-shaped adversarial acceptance path: the clean EXTERNAL
client harness over the landed API; PLAN's P4-B row elaborated one phase deep
at P4-A's landing; record 61 §2).
Red-first (LAW-11): at CLAIM-068's merged head 101e173 the suite fails with
ARV-TEST-000 (machinery-absent; red-01.txt) — harness/client.py (the clean
external client driver, P4-F's named proof vehicle) is absent.

THE CONTRACT (P4-B slice one's letter): the READER CLIENT itself is P4-B's
SEPARATE authorized repo (never this one) — this slice lands the BACKEND's
proof of the client contract through the clean external driver: the full user
walk (import -> open/read -> save position -> highlight/bookmark -> note ->
the reopen round-trip) then P4-B's named adversarial conditions, each pinned
to its typed refusal or truthful answer — never a privileged helper, never a
table write, never a second durability path.

Cases (the CAC registry; each pin's full statement lives at its check()):
  CAC-01 the full user walk at the real boundary (the clean client driver):
         import -> extract -> open/read (get-position answers no_position_
         saved BEFORE any save — the truthful first-open state) -> save
         position -> highlight -> bookmark -> note -> the reopen round-trip
         (fresh invocations answer the durable state: the position, the
         capture, the note) — every ack carrying the frozen grammar
  CAC-02 auth/owner-scope expiration + forbidden source: another owner's
         data is the SAME refusal as absent on BOTH paths (the no-oracle at
         the client boundary — byte-equal refusals, never a leak)
  CAC-03 malformed DTO: the typed refusals at every command boundary (the
         offset law, the content law, the format law, the position law) —
         each zero-effect
  CAC-04 offline transitions + timeout-with-uncertain-ack: the crash
         matrix's lost-ack arm (exit 2, the effect committed, the honest
         unknown) + the replay convergence (retry-after-lost-response)
  CAC-05 duplicate click: the idempotency (same key + same body ->
         status=replayed with the same result_ref; same key + different
         body -> the typed ARV-CMD-409 with zero effect)
  CAC-06 reload/restart: fresh invocations answer the durable state (the
         position + the capture + the note over NEW processes — the state
         is in the store, never the session)
  CAC-07 stale source version: the generation binding honest across a
         re-extraction (generation_matches=false, the saved offsets
         byte-unchanged — never a silent retarget)
  CAC-08 deleted target: the tombstone refusals (the ordinary read refuses
         ARV-QRY-003; the governed history retains; restore returns)
  CAC-09 the no-privileged-path law: the driver's every call is a real CLI
         invocation (no psql, no SQL, no direct table access anywhere in
         harness/client.py — the clean client is CLEAN, mechanically so)

THE BOUNDED EXCLUSIONS (the CLAIMS row's letter): no reader-client UI (the
separate repo); no product tables touched by the harness; no new product
surface (the landed contracts only — the driver is test-side infrastructure).

Run: python3 harness/tests/test_client_acceptance.py   (exit 0 = green)
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

# the machinery-absent probe (the RED gate): the clean external client driver
# is this slice's machinery — absent at the RED tree.
_probe = subprocess.run([sys.executable, "-c",
                         f"import sys; sys.path.insert(0, {str(REPO)!r});\n"
                         "from harness import client\n"
                         "print(callable(client.walk))"],
                        capture_output=True, text=True, timeout=60)
if not (_probe.returncode == 0 and _probe.stdout.strip() == "True"):
    print("FAIL ARV-TEST-000: the P4-B slice one client-acceptance machinery is absent "
          "(machinery-absent class; harness/client.py importable with the walk driver: "
          f"{_probe.returncode == 0}) — the implementation lands after this RED, never "
          "before it (LAW-11)")
    sys.exit(1)

DB = ENV = None

TEXT = ("The client-acceptance corpus opens here.\n"
        "The second paragraph carries the meridian token.\n"
        "The third paragraph closes the walk.\n")


def check(code: str, ok: bool, what: str, repair: str) -> None:
    if ok:
        print(f"PASS {code}: {what}")
    else:
        print(f"FAIL {code}: {what}")
        print(f"      repair: {repair}")
        FAILS.append(code)


def main() -> int:
    global DB, ENV
    DB = pg.create_scratch_db("p4b1")
    blob_dir = tempfile.mkdtemp(prefix="arv-blobs-")
    ENV = dict(os.environ, PGDATABASE=DB, ARV_BLOB_DIR=blob_dir)
    try:
        subprocess.run([sys.executable, str(REPO / "harness" / "migrate.py")],
                       capture_output=True, text=True, timeout=180,
                       env=ENV, check=True)
        from harness import client  # the clean external driver (this slice's machinery)

        # ---- CAC-01 — the full user walk at the real boundary
        walk = client.walk(ENV, TEXT)
        ok1 = (walk["import"]["exit"] == 0 and walk["import"]["frozen"]
               and walk["extract"]["exit"] == 0 and walk["extract"]["frozen"]
               and walk["first_open"]["state"] == "no_position_saved"
               and walk["save_position"]["exit"] == 0 and walk["save_position"]["frozen"]
               and walk["highlight"]["exit"] == 0 and walk["highlight"]["frozen"]
               and walk["bookmark"]["exit"] == 0 and walk["bookmark"]["frozen"]
               and walk["note"]["exit"] == 0 and walk["note"]["frozen"]
               and walk["reopen_position"]["state"] == "saved"
               and walk["reopen_position"]["generation_matches"] is True
               and walk["reopen_capture"]["exit"] == 0
               and "meridian" in walk["reopen_note"]["body"])
        check("CAC-01", ok1,
              "the full user walk at the real boundary (the clean client driver): import -> "
              "extract -> open/read (the FIRST open answers no_position_saved — the truthful "
              "first-open state, a state never a failure) -> save position -> highlight -> "
              "bookmark -> note -> the reopen round-trip (FRESH invocations answer the durable "
              "state: the position with generation_matches=true, the capture, the note's body) "
              "— every ack carrying the frozen grammar (status/result_ref/"
              "durability_rung/api_version)",
              "harness/client.py's walk driver over the real CLIs — the landed contracts "
              "assembled, never a privileged helper")

        # ---- CAC-02 — auth/owner-scope expiration + forbidden source
        cond = client.condition_forbidden_source(ENV, walk)
        ok2 = (cond["read_absent"] == cond["read_foreign"]           # the no-oracle, read path
               and cond["write_absent"] == cond["write_foreign"]     # the no-oracle, write path
               and "FAIL ARV-QRY-001:" in cond["read_absent"]
               and "FAIL ARV-POS-001:" in cond["write_absent"]
               and cond["foreign_extract"].startswith("ARV-EXT-004"))
        check("CAC-02", ok2,
              "auth/owner-scope expiration + forbidden source: another owner's data is the "
              "SAME refusal as absent on BOTH paths (the read arm's ARV-QRY-001 and the write "
              "arm's ARV-POS-001 byte-equal across absent-vs-foreign — the no-oracle at the "
              "client boundary, never a leak that the other owner's object exists); the "
              "foreign extract refuses ARV-EXT-004",
              "the landed no-oracle contracts observed through the clean driver")

        # ---- CAC-03 — malformed DTO
        cond = client.condition_malformed_dto(ENV, walk)
        ok3 = (cond["offset_law"].startswith("ARV-CAP-003")
               and cond["content_law"].startswith("ARV-NTE-010")
               and cond["format_law"].startswith("ARV-FMT-001")
               and cond["position_law"].startswith("ARV-POS-003")
               and cond["zero_effect"])
        check("CAC-03", ok3,
              "malformed DTO: the typed refusals at every command boundary — the offset law "
              "(ARV-CAP-003, never clamped), the content law (ARV-NTE-010 — the channel law: neither/both content channels), the format law "
              "(ARV-FMT-001), the position law (ARV-POS-003) — each zero-effect (the row "
              "counts unchanged across all four)",
              "the landed typed-refusal contracts observed through the clean driver")

        # ---- CAC-04 — offline transitions + timeout-with-uncertain-ack
        cond = client.condition_uncertain_ack(ENV, walk)
        ok4 = (cond["crash_exit"] == 2
               and cond["effect_committed"] is True
               and cond["replay_exit"] == 0
               and cond["replay_replayed"] is True
               and cond["replay_same_ref"] is True)
        check("CAC-04", ok4,
              "offline transitions + timeout-with-uncertain-ack: the crash matrix's lost-ack "
              "arm (exit 2, NO ack — the honest unknown) with the effect COMMITTED (the "
              "reader's write IS durable) and the retry-after-lost-response convergence (the "
              "same-key replay acks status=replayed with the SAME result_ref)",
              "the landed crash matrix + the spine's replay contract observed through the "
              "clean driver")

        # ---- CAC-05 — duplicate click
        cond = client.condition_duplicate_click(ENV, walk)
        ok5 = (cond["same_body_exit"] == 0 and cond["same_body_replayed"] is True
               and cond["same_body_same_ref"] is True
               and cond["diff_body_exit"] == 1
               and cond["diff_body_code"].startswith("ARV-CMD-409")
               and cond["diff_body_zero_effect"] is True)
        check("CAC-05", ok5,
              "duplicate click: the idempotency — the same key + the same body acks "
              "status=replayed with the SAME result_ref (the double-click is safe); the same "
              "key + a different body refuses the typed ARV-CMD-409 with ZERO effect (never a "
              "silent overwrite)",
              "the spine's idempotency contract observed through the clean driver")

        # ---- CAC-06 — reload/restart
        cond = client.condition_reload(ENV, walk)
        ok6 = (cond["position_state"] == "saved"
               and cond["capture_exit"] == 0
               and cond["note_body_matches"] is True)
        check("CAC-06", ok6,
              "reload/restart: fresh invocations answer the durable state (the position, the "
              "capture, the note over NEW processes — the state lives in the store, never the "
              "session; a client restart loses nothing)",
              "the landed durable-read contracts observed through the clean driver")

        # ---- CAC-07 — stale source version
        cond = client.condition_stale_version(ENV, walk)
        ok7 = (cond["reextract_exit"] == 0
               and cond["generation_changed"] is True
               and cond["saved_generation_stable"] is True
               and cond["generation_matches"] is False
               and cond["offsets_unchanged"] is True
               and cond["saved_before_matches"])
        check("CAC-07", ok7,
              "stale source version: the generation binding honest across a re-extraction — "
              "the saved offsets byte-unchanged (before == after the re-extraction), the saved_generation_id stable, "
              "generation_matches=false (the client is TOLD the view moved, never silently "
              "retargeted)",
              "the landed serving-generation contract observed through the clean driver")

        # ---- CAC-08 — deleted target
        cond = client.condition_deleted_target(ENV, walk)
        ok8 = (cond["tombstone_exit"] == 0
               and cond["read_refuses"].startswith("ARV-QRY-003")
               and cond["history_retains"] is True
               and cond["restore_exit"] == 0
               and cond["read_after_restore_exit"] == 0)
        check("CAC-08", ok8,
              "deleted target: the tombstone refusals — the ordinary read refuses the typed "
              "ARV-QRY-003 (hidden from retrieval, never erased), the governed history "
              "retains every revision, and restore returns the target to ordinary retrieval",
              "the landed lifecycle contracts observed through the clean driver")

        # ---- CAC-09 — the no-privileged-path law
        src = (REPO / "harness" / "client.py").read_text(encoding="utf-8")
        ok9 = ("psql" not in src and "arv_app" not in src and "arv_read" not in src
               and "INSERT INTO" not in src and "SELECT " not in src
               and "commands.py" in src and "query.py" in src)
        check("CAC-09", ok9,
              "the no-privileged-path law: the driver's every call is a real CLI invocation — "
              "no psql, no role name, no SQL anywhere in harness/client.py (the clean client "
              "is CLEAN, mechanically so: the same surface the separate reader-client repo "
              "will call, never a privileged helper)",
              "harness/client.py's discipline: subprocess invocations of the real CLIs only")

        if FAILS:
            print(f"\nCLIENT-ACCEPTANCE SUITE RED — {len(FAILS)} open: {', '.join(FAILS)} "
                  "(the client-shaped acceptance contract is broken or unimplemented)")
            return 1
        print("\nCLIENT-ACCEPTANCE SUITE GREEN — CAC-01..09 (the clean external client over "
              "the landed API: the full walk, the no-oracle both paths, the typed refusals, "
              "the uncertain-ack convergence, the idempotency, the reload durability, the "
              "stale-version honesty, the tombstone lifecycle, the no-privileged-path law)")
        return 0
    finally:
        pg.drop_scratch_db(DB)


if __name__ == "__main__":
    sys.exit(main())
