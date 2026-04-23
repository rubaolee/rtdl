# Goal842 PostgreSQL Baseline Collector Progress

## Scope

Add a direct Goal836-valid PostgreSQL prepared DB compact-summary baseline collector for the two active database analytics paths, while preserving the existing policy that live PostgreSQL baselines are collected on Linux rather than on this macOS host.

## What Changed

- Added direct collector:
  - `scripts/goal842_postgresql_db_prepared_baseline.py`
- Added focused tests:
  - `tests/goal842_postgresql_db_prepared_baseline_test.py`
- Updated the local collection manifest so the Linux PostgreSQL rows now have explicit collector commands and `collector_kind`, rather than only a status label:
  - `scripts/goal838_local_baseline_collection_manifest.py`
  - `tests/goal838_local_baseline_collection_manifest_test.py`
- Regenerated:
  - `docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.json`
  - `docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.generated.md`

## Technical Behavior

- The new collector writes Goal836-valid artifacts for:
  - `prepared_db_session_sales_risk`
  - `prepared_db_session_regional_dashboard`
- Baseline name:
  - `postgresql_same_semantics_on_linux_when_available`
- The collector runs live PostgreSQL bounded DB semantics directly through `rtdsl.db_postgresql` helpers and compares the resulting compact summary against the CPU prepared compact-summary app path from Goal756.
- The collector is same-semantics evidence only. It does not claim PostgreSQL is a public app backend and does not authorize any speedup claim.
- For grouped-count and grouped-sum, the fake PostgreSQL test path now sets the normalized grouped query explicitly before executing the SQL helper so the portable tests exercise the real collector logic.

## Policy Result

- Manifest status remains `linux_postgresql_required` for both DB PostgreSQL actions.
- The difference is that Linux collection is now operationally explicit: each missing PostgreSQL artifact has a direct collector command instead of a manual recipe.

## Verification

- `PYTHONPATH=src:. python3 -m unittest -v tests.goal842_postgresql_db_prepared_baseline_test tests.goal838_local_baseline_collection_manifest_test`
- `python3 -m py_compile scripts/goal842_postgresql_db_prepared_baseline.py tests/goal842_postgresql_db_prepared_baseline_test.py tests/goal838_local_baseline_collection_manifest_test.py`
- `git diff --check`

Result: all focused checks passed.

## Boundary

This goal does not reduce the current Goal836 active missing count on this macOS host because the PostgreSQL artifacts still require a live Linux PostgreSQL environment to collect honestly.
