# Goal840 Local Baseline Collection Progress

Date: `2026-04-23`
Repo: `/Users/rl2025/rtdl_python_only`
Branch: `codex/rtx-cloud-run-2026-04-22`

## Scope

This goal covers the local collector path needed to convert Goal838 "local command ready"
entries into Goal836-valid baseline artifacts, plus the first real-scale local collection pass.

It does not claim release readiness, RTX speedup, or completion of all Goal835 baselines.

## Implemented

1. Added direct prepared-DB baseline collector:
   - `scripts/goal840_db_prepared_baseline.py`
   - Writes Goal836-valid artifacts for:
     - `database_analytics / prepared_db_session_sales_risk / cpu_oracle_compact_summary`
     - `database_analytics / prepared_db_session_sales_risk / embree_compact_summary`
     - `database_analytics / prepared_db_session_regional_dashboard / cpu_oracle_compact_summary`
     - `database_analytics / prepared_db_session_regional_dashboard / embree_compact_summary`
   - Uses Goal756 prepared-session profiler outputs and validates:
     - CPU prepared-session compact summary against CPU one-shot compact summary
     - Embree prepared-session compact summary against CPU prepared-session compact summary

2. Rewired Goal838 manifest DB actions to use the direct Goal840 collector instead of raw Goal756 outputs.

3. Fixed Goal839 fixed-radius CPU collectors to validate against the apps' exact tiled oracle summaries instead of an unnecessary brute-force expansion.

4. Added exact CPU pose-flag / pose-count reference helpers:
   - `src/rtdsl/reference.py`
     - `ray_triangle_pose_flags_cpu(...)`
     - `ray_triangle_pose_count_cpu(...)`
   - Exported through `src/rtdsl/__init__.py`

5. Updated robot baseline oracle work to use exact CPU pose-flag aggregation instead of per-ray row materialization for oracle validation.

## Verification

Focused tests passed:

- `tests.goal632_ray_triangle_any_hit_test`
- `tests.goal839_local_baseline_collectors_test`
- `tests.goal840_db_prepared_baseline_test`
- `tests.goal838_local_baseline_collection_manifest_test`
- `tests.goal836_rtx_baseline_readiness_gate_test`

Mechanical checks passed:

- `python3 -m py_compile ...`
- `git diff --check`

## Real-Scale Local Collection Outcome

Collected and written successfully on this macOS host:

1. `docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_cpu_oracle_compact_summary_2026-04-23.json`
2. `docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_embree_compact_summary_2026-04-23.json`
3. `docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_cpu_oracle_compact_summary_2026-04-23.json`
4. `docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_embree_compact_summary_2026-04-23.json`
5. `docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_cpu_scalar_threshold_count_oracle_2026-04-23.json`
6. `docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_embree_scalar_or_summary_path_2026-04-23.json`
7. `docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_cpu_scalar_threshold_count_oracle_2026-04-23.json`
8. `docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_embree_scalar_or_summary_path_2026-04-23.json`

Not yet collected locally:

1. `robot_collision_screening / cpu_oracle_pose_count`
2. `robot_collision_screening / embree_anyhit_pose_count_or_equivalent_compact_summary`

Reason:

- The robot compact-summary baselines still require expensive exact traversal at Goal835 scale
  (`pose_count=200000`, `obstacle_count=1024`, `iterations=10`).
- The new scalar oracle path removes row-materialization overhead and reduces memory pressure,
  but the full exact CPU traversal remains too slow for an efficient unattended macOS local batch.

## Gate Result

Regenerated Goal836 readiness gate:

- `required_artifact_count`: `23`
- `valid_artifact_count`: `8`
- `missing_artifact_count`: `15`
- `invalid_artifact_count`: `0`

Current missing set is now limited to:

1. Two Linux/PostgreSQL DB baselines
2. Two optional SciPy/reference baselines
3. Two robot baselines, now explicitly marked Linux-preferred for large exact-oracle collection
4. Nine deferred-app baselines

## Follow-On Tooling

The local manifest was further tightened after the first collection pass:

- `scripts/goal838_local_baseline_collection_manifest.py` now classifies the robot pair as
  `linux_preferred_for_large_exact_oracle` instead of `local_command_ready` on this macOS host.
- `scripts/goal841_local_baseline_collect.py` can execute filtered Goal838 local-ready actions,
  which is useful for bounded collection batches and for constructing exact Linux handoff plans.
- The Goal841 dry-run plan for `robot_collision_screening` now intentionally selects zero actions on macOS,
  because the robot pair is no longer part of the local-ready batch.
- Linux robot handoff packet:
  - `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL841_LINUX_ROBOT_BASELINE_COLLECTION_REQUEST_2026-04-23.md`

## Honest Boundary

- No public RTX speedup claim is authorized.
- Goal836 still reports `needs_baselines`.
- The collected artifacts are local same-semantics evidence only.
- Deferred apps remain deferred.

## Next Recommended Work

1. Decide whether robot CPU/Embree baseline collection should continue on this host or be delegated to a stronger Linux machine.
2. Collect the two Linux/PostgreSQL DB baselines.
3. Keep deferred apps out of any public RTX claim package until their own activation gate is selected.
