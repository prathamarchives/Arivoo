# Arivoo command surface — Phase 2 Layer 2.1 minimum (D-036; the target surface is
# OPERATING-MODEL.md §9; these are the S1 commands: health, migrate, verify-schema,
# harness-tests. S4 completes the set: state/fast/red/prove/gate/verify/known-bad.)
# Zero third-party dependencies (D-036): Python stdlib + psql + make.
#
# Connection (env, read by harness/adapters/pg.py — the ONLY env-reading module):
#   PGHOST (default 127.0.0.1) · PGPORT (default 5432) · PGUSER (default postgres)
# CI: the postgres:17 service container. Local: the rig cluster (record 18 §2).

.PHONY: harness-health migrate verify-schema harness-tests

harness-health:
	@python3 harness/health.py

migrate:
	@python3 harness/migrate.py

verify-schema:
	@python3 harness/migrate.py --verify

harness-tests:
	@for t in harness/tests/test_*.py; do echo "== $$t"; python3 $$t || exit 1; done

# --- S4a (D-036): the command surface grows — state/fast/red/prove; the gate's
# targets (gate/verify/known-bad) land with S4b (harness/gate.py) ---

.PHONY: state fast red prove

state:
	@python3 harness/state.py

fast:
	@for t in harness/tests/test_*.py; do echo "== $$t"; python3 $$t || exit 1; done

red:
	@python3 harness/red.py --note "$${NOTE:-red run at the test-only commit -- record where it was observed}"

prove:
	@SL=$${SLICE:-main-selfcheck}; 	python3 harness/proofsheet.py --slice $$SL --record "python3 harness/tests/test_migrations.py"; 	python3 harness/proofsheet.py --slice $$SL --record "python3 harness/tests/test_substrate.py"; 	python3 harness/proofsheet.py --slice $$SL --record "python3 harness/tests/test_commands.py"; 	python3 harness/proofsheet.py --slice $$SL


# --- S4b (D-036): the gate lands — OPERATING-MODEL §9's minimum set completes ---
.PHONY: gate known-bad

gate:
	@if [ -n "$$SLICE" ]; then EXTRA="--slice $$SLICE"; else EXTRA=""; fi; \
	if [ -n "$$GATE_DIFF" ]; then EXTRA="$$EXTRA --diff $$GATE_DIFF"; else EXTRA="$$EXTRA --no-diff"; fi; \
	python3 harness/gate.py $$EXTRA

known-bad:
	@python3 harness/gate.py --known-bad-only

verify: fast known-bad
	@python3 harness/gate.py --no-diff --skip-suites
	@python3 tools/verify_canonical_layer.py > /dev/null && echo "canonical layer: 51/0 (verifier green)"
