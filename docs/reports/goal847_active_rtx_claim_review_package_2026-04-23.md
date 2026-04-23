# Goal847 Active RTX Claim Review Package

## Scope

Build an internal review package for the active OptiX/NVIDIA RT claim set using:

- the green Goal846 active mandatory-baseline gate
- the RTX 3090 cloud artifact report from Goal762
- the same-semantics baseline artifacts collected through Goals840/842/844/845

## Why This Goal Exists

After Goal846, the active mandatory baseline set is complete, but the repo still lacked one place that answers the engineering question:

- for each active OptiX path, what is the exact matched native-query comparison?
- which baseline is actually faster or slower on that bounded metric?
- where is the remaining time on the RTX path if traversal itself is already small?

This goal answers that without authorizing a public speedup claim.

## Additional Fix During Implementation

While generating the package, the regional-dashboard CPU DB baseline exposed a collector bug:

- Goal840 originally summed only `query_*_sec` timers for DB `native_query`
- the CPU `regional_dashboard` path reports only `cpu_reference_execute_and_postprocess_sec`
- result: the artifact incorrectly encoded `native_query = 0.0`

The collector was fixed to:

1. use `cpu_reference_execute_and_postprocess_sec` when no `query_*_sec` timers exist
2. map `table_construction_sec` into `input_pack_or_table_build` when `input_construction_sec` is absent

That made the CPU regional-dashboard baseline performance-credible again and kept the review package honest.

## What Changed

- Added:
  - `scripts/goal847_active_rtx_claim_review_package.py`
  - `tests/goal847_active_rtx_claim_review_package_test.py`
- Updated:
  - `scripts/goal840_db_prepared_baseline.py`
  - `tests/goal840_db_prepared_baseline_test.py`
- Generated:
  - `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.json`
  - `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.md`
- Refreshed:
  - `docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_cpu_oracle_compact_summary_2026-04-23.json`

## Result

The package now gives a bounded active-OptiX comparison table.

Key current readings:

- DB sales risk:
  - OptiX `native_query`: `0.129264s`
  - CPU baseline `native_query`: `1.904947s`
  - Embree baseline `native_query`: `0.061593s`
- DB regional dashboard:
  - OptiX `native_query`: `0.210792s`
  - CPU baseline `native_query`: `0.516913s`
  - Embree baseline `native_query`: `0.127206s`
- Outlier prepared summary:
  - OptiX `native_threshold_query`: `0.189633s`
  - Embree baseline `native_threshold_query`: `0.206962s`
- DBSCAN core summary:
  - OptiX `native_threshold_query`: `0.184927s`
  - Embree baseline `native_threshold_query`: `0.211451s`
- Robot pose-count summary:
  - OptiX `native_anyhit_query`: `0.000327s`
  - Embree baseline `native_anyhit_query`: `0.581851s`

## Interpretation

- The active OptiX set is not uniformly faster than every baseline.
- The package makes that explicit instead of hiding it:
  - Embree still beats OptiX on both prepared DB paths in the matched query phase.
  - OptiX slightly beats Embree on the prepared fixed-radius summary paths.
  - OptiX is dramatically ahead on the bounded robot scalar pose-count query phase.
- The package also surfaces non-query costs directly:
  - DB paths still have large host-side residual overhead and prepare cost.
  - Fixed-radius paths still spend substantial time outside the native query.
  - Robot still has significant scene/ray preparation overhead relative to the tiny query phase.

## Verification

- `PYTHONPATH=src:. python3 -m unittest -v tests.goal840_db_prepared_baseline_test tests.goal847_active_rtx_claim_review_package_test`
- `python3 scripts/goal840_db_prepared_baseline.py --backend cpu --scenario regional_dashboard --copies 20000 --iterations 10 --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_cpu_oracle_compact_summary_2026-04-23.json`
- `python3 scripts/goal847_active_rtx_claim_review_package.py --output-json docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.json --output-md docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.md`
- `python3 -m py_compile scripts/goal840_db_prepared_baseline.py tests/goal840_db_prepared_baseline_test.py scripts/goal847_active_rtx_claim_review_package.py tests/goal847_active_rtx_claim_review_package_test.py`
- `git diff --check`

Result: focused checks passed.

## Boundary

This is an internal active claim-review package only. It does not authorize a public RTX speedup claim.
