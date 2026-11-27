#!/bin/bash
# claim-098 SEV round 1 — the RED re-observation (the independent reviewer's own)
# Re-creates the detached worktree at the RED-first commit 12bcbbf (the battery
# only, routes absent), runs the pinned battery there, removes the worktree.
# The expected exit is 1 (the battery refuses: the capture/bookmark routes do
# not exist at that tree) — the observed red, never an assertion.
set -u
bash /home/z/my-project/scripts/rig-pg.sh start
cd /home/z/my-project/arivoo
export PATH=/home/z/my-project/pgbuild/root/usr/lib/postgresql/17/bin:/usr/local/bin:/usr/bin:/bin
export LD_LIBRARY_PATH=/home/z/my-project/pgbuild/root/usr/lib/x86_64-linux-gnu:/home/z/my-project/pgbuild/root/usr/lib
export PGHOST=127.0.0.1 PGPORT=5433 PGUSER=postgres
git worktree remove --force /tmp/sev098red 2>/dev/null
git worktree add --detach /tmp/sev098red 12bcbbf || exit 90
/home/z/my-project/arivoo/.venv-waved/bin/python -I /tmp/sev098red/harness/api/routes_selfcheck.py
rc=$?
git worktree remove --force /tmp/sev098red
exit $rc
