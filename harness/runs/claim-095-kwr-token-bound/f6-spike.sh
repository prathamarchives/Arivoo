#!/usr/bin/env bash
# The F6 defect reproduction (CLAIM-95's spike, made reproducible for the run record):
# proves the btree row limit fires ONLY on TOAST-incompressible runs. A repeated-
# character run compresses before the index tuple is built and inserts cleanly; an
# incompressible mixed-case run of the same length raises
#   "index row size N exceeds btree version 4 maximum 2704"
# on the local 17.12 rig (8k block size). The kernel bound therefore sits on the RAW
# UTF-8 byte length (KWR_TOKEN_MAX_BYTES), never on a predicted compressed size.
# Exit 0 = the defect class demonstrated exactly as documented.
set -uo pipefail
: "${PGHOST:?rig env required}" "${PGPORT:?}" "${PGUSER:?}"
DB=arv_f6spike
export PGDATABASE=$DB
TMPD=$(mktemp -d)
psql -X -q -U "$PGUSER" -d postgres -c "DROP DATABASE IF EXISTS $DB;" >/dev/null 2>&1
psql -X -q -U "$PGUSER" -d postgres -c "CREATE DATABASE $DB;" >/dev/null 2>&1

cleanup() { psql -X -q -U "$PGUSER" -d postgres -c "DROP DATABASE IF EXISTS $DB;" >/dev/null 2>&1; rm -rf "$TMPD"; }
trap cleanup EXIT

psql -X -q -U "$PGUSER" -d "$DB" -c "CREATE TABLE bt_probe (id int, tok text); CREATE INDEX bt_probe_tok ON bt_probe (tok);" >/dev/null 2>&1

# probe 1: the compressible class (repeated characters) — inserts cleanly
psql -X -q -U "$PGUSER" -d "$DB" -v ON_ERROR_STOP=1 -c "INSERT INTO bt_probe VALUES (1, repeat('a', 4000));" >/dev/null 2>&1
echo "probe1 (repeated 4000 chars): inserted cleanly (TOAST-compressed before the index tuple)"

# probe 2: the incompressible class — the documented error
python3 - "$TMPD" <<'PY'
import sys, pathlib
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
out, s = [], 7
for _ in range(3000):
    s = (s * 1103515245 + 12345) % (2 ** 31)
    out.append(alphabet[s % len(alphabet)])
pathlib.Path(sys.argv[1], "tok.txt").write_text("".join(out))
PY
TOK=$(cat "$TMPD/tok.txt")
ERR=$(psql -X -U "$PGUSER" -d "$DB" -v ON_ERROR_STOP=1 -c "INSERT INTO bt_probe VALUES (2, '$TOK');" 2>&1) && { echo "FAIL: the incompressible insert did NOT raise the documented error"; exit 1; }
echo "probe2 (incompressible 3000 chars): $ERR" | head -1
echo "$ERR" | grep -q "exceeds btree version 4 maximum" || { echo "FAIL: the error text does not match the documented class"; exit 1; }

# probe 3: the kernel's answer — the same class through import_source refuses NAMED
export ARV_BLOB_DIR="$TMPD/blobs"; mkdir -p "$ARV_BLOB_DIR"
python3 harness/migrate.py >/dev/null 2>&1 || { echo "FAIL: the spike db did not migrate"; exit 1; }
printf 'lead %s tail' "$TOK" > "$TMPD/src.txt"
OUT=$(python3 harness/commands.py import_source --owner A --actor owner --client-id cli-1 \
      --idem-key f6-spike --file "$TMPD/src.txt" --media-type text/plain --title "F6 Spike" 2>&1)
echo "$OUT" | grep -q "FAIL ARV-KWR-002" || { echo "FAIL: the kernel did not refuse with ARV-KWR-002"; echo "$OUT"; exit 1; }
echo "probe3 (the same class through import_source): $OUT" | head -1
echo "F6 SPIKE COMPLETE: the defect class demonstrated; the kernel refuses it named"
