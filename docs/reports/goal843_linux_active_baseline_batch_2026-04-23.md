# Goal843 Linux Active Baseline Batch

## Scope

Collapse the remaining active Linux-only baseline work into one explicit batch runner so the next Linux collection round is one command, not four separate manual steps.

## What Changed

- Added:
  - `scripts/goal843_linux_active_baseline_batch.py`
  - `tests/goal843_linux_active_baseline_batch_test.py`

## Behavior

- The batch plan selects exactly the four remaining active Linux-only baseline actions from Goal838:
  - two PostgreSQL same-semantics DB compact-summary artifacts
  - two robot pose-count artifacts
- Selected statuses:
  - `linux_postgresql_required`
  - `linux_preferred_for_large_exact_oracle`
- The runner supports:
  - dry-run plan generation on non-Linux hosts
  - real command execution on a Linux host with the required environment
- The batch does not include:
  - local-command-ready artifacts
  - optional SciPy/reference artifacts
  - deferred app artifacts

## Why This Matters

Goal842 made the PostgreSQL DB pair explicit. Goal843 makes the remaining active Linux-only baseline gap operationally explicit as a single bounded Linux collection step. That reduces coordination cost and keeps the cloud/local policy intact.

## Verification

- `PYTHONPATH=src:. python3 -m unittest -v tests.goal843_linux_active_baseline_batch_test tests.goal842_postgresql_db_prepared_baseline_test tests.goal841_local_baseline_collect_test tests.goal838_local_baseline_collection_manifest_test`
- `python3 -m py_compile scripts/goal843_linux_active_baseline_batch.py tests/goal843_linux_active_baseline_batch_test.py`
- `git diff --check`

Result: all focused checks passed.

## Boundary

This goal does not collect any new baseline artifact by itself. It only provides the single Linux batch mechanism for the four remaining active Linux-only artifacts.
