# PROOF SHEET — slice claim-087-runbook-intake (harness-built; never hand-edited — PRF-01, LAW-01)

- commit (last run record's): 784e4e611e036ece0b727c131e6cc070b616bb66
- generated (last record's timestamp): 2026-11-18T16:41:07.395822+00:00
- run records: 4

## Run records (command, exit, output digest)
- `python3 tools/verify_canonical_layer.py` -> exit 0 · output sha256 853a728fc8caf711 · 2026-11-18T16:33:33.460021+00:00
- `python3 tools/verify_selftest.py` -> exit 0 · output sha256 333917b307eb5d36 · 2026-11-18T16:34:14.135506+00:00
- `make harness-health` -> exit 0 · output sha256 0eedd1f6e490c18c · 2026-11-18T16:34:14.172744+00:00
- `make harness-tests` -> exit 0 · output sha256 8d9010fd09ad69ec · 2026-11-18T16:41:07.395822+00:00

## Not verified (LAW-04 — required, never empty-by-omission)
- the remote CI runs (they execute at the PR — the five checks on the branch head and the merge commit)
- the D-042 review round (it runs at the PR before the merge, per the standing protocol)
- the Supabase project's live state at POST-INTAKE time (verified pre-slice; the next write action re-verifies before acting — the runbook §7.1's own preflight rule)

## Systems-engineering verification (LAW-30; harness/sev.py)
- report sha256: 8eed0493d5e860639ee6e6747b9b5f5c82f418cae26858e46edca16fe1965ea2
- reviewed_diff_sha256: d059ef0059dd83d196ec1f24673c68c07aadd952895892f309567c0eb40d45d8
- disposition: PASS
- findings: 2 (open P0/P1: 0)
- not-verified entries: 3

## Assembly
- sheet sha256 (of the content above, excluding this line): 0ed9a30a5736f54eabc87e2f06d1db6f23770fefb3ce1519ab83aebb93d7580d
