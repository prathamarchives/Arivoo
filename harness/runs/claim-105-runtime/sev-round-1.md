# SEV round-1 — slice claim-105-runtime (Workstream 10's pre-gate half; INT-172)
- reviewer: inline verification (a declared distinct-context limit; per ARV-SEV-007)
- disposition: PASS — zero findings
| Probe | Observed |
|---|---|
| the fresh-venv locked install (the image's pip layer) | exit 0 |
| /health/live, /health/ready | 200/200 (the served app in the fresh venv) |
| POST /mcp unauthenticated | 401 (the transport law) |
| /api/v1/me unauthenticated | 401 (the auth law) |
| the unconfigured start | ARV-SVC-001 names the variable, exit 1 |
| the release oracle | 22 migrations on a fresh db |
| the CF token's reach | zone + account + 3 tunnels (live) |
| the corpus law | VER-404 caught my own raw-runbook append — repaired (relocated + byte-exact restore), GREEN |
Not-verified: the five PR-head checks; the Q18 gate; the database credential; the docker build; the deployed surface.
