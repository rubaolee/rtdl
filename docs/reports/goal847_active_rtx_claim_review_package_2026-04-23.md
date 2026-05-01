# Goal847 Active RTX Claim Review Package

This package is for internal active OptiX claim review only. It compares same-semantics native-query phases for the active mandatory baseline set and highlights remaining non-query bottlenecks. It does not authorize a public RTX speedup claim.

## Summary

- active rows: `5`
- reviewed public wording rows in active set: `2`
- blocked public wording rows in active set: `1`
- Goal846 status: `ok`
- Goal762 status: `ok`

## Comparable Native-Phase Table

| App | Path | Public wording status | Cloud query metric | Cloud query (s) | Fastest baseline | Fastest ratio (baseline/cloud) | Non-claim |
|---|---|---|---|---:|---|---:|---|
| database_analytics | prepared_db_session_sales_risk | public_wording_not_reviewed | native_query | 0.129264 | cpu_oracle_compact_summary | 14.737 | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | public_wording_not_reviewed | native_query | 0.210792 | cpu_oracle_compact_summary | 2.452 | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| outlier_detection | prepared_fixed_radius_density_summary | public_wording_reviewed | native_threshold_query | 0.189633 | embree_scalar_or_summary_path | 1.091 | not per-point outlier labels, row-returning outputs, broad anomaly detection, or whole-app speedup |
| dbscan_clustering | prepared_fixed_radius_core_flags | public_wording_reviewed | native_threshold_query | 0.184927 | embree_scalar_or_summary_path | 1.143 | not per-point core flags, cluster expansion, full DBSCAN clustering, or whole-app speedup |
| robot_collision_screening | prepared_pose_flags | public_wording_blocked | native_anyhit_query | 0.000327 | cpu_oracle_pose_count | 1817901.555 | not continuous collision detection, full robot kinematics, or mesh-engine replacement |

## database_analytics / prepared_db_session_sales_risk

- claim scope: `prepared OptiX DB session behavior and Python/interface cost split`
- public wording status: `public_wording_not_reviewed`
- public wording boundary: Prepared DB compact-summary traversal/filter/grouping is RT-core ready, but no public speedup wording is authorized yet.
- cloud comparable phase: `native_query` = `0.129264s`
- review note: DB review stays bounded to prepared compact-summary semantics. Warm-query comparison is meaningful, but one-shot totals still include substantial non-query work. Local Goals850/851 removed grouped row materialization on compact-summary paths; a fresh RTX rerun is still required before that reduction appears in this package.

| Baseline | Backend | Comparable phase (s) | Ratio baseline/cloud |
|---|---|---:|---:|
| cpu_oracle_compact_summary | cpu | 1.904947 | 14.737 |
| embree_compact_summary | embree | 0.061593 | 0.476 |
| postgresql_same_semantics_on_linux_when_available | postgresql | 0.103802 | 0.803 |

Top non-query phases on RTX path:
- `one_shot_total_sec` = `1.903282s`
- `residual_host_overhead_sec` = `1.187389s`
- `prepare_total_sec` = `0.585884s`
- `close_sec` = `0.000745s`

## database_analytics / prepared_db_session_regional_dashboard

- claim scope: `prepared OptiX DB session behavior and Python/interface cost split`
- public wording status: `public_wording_not_reviewed`
- public wording boundary: Prepared DB compact-summary traversal/filter/grouping is RT-core ready, but no public speedup wording is authorized yet.
- cloud comparable phase: `native_query` = `0.210792s`
- review note: DB review stays bounded to prepared compact-summary semantics. Warm-query comparison is meaningful, but one-shot totals still include substantial non-query work. Local Goals850/851 removed grouped row materialization on compact-summary paths; a fresh RTX rerun is still required before that reduction appears in this package.

| Baseline | Backend | Comparable phase (s) | Ratio baseline/cloud |
|---|---|---:|---:|
| cpu_oracle_compact_summary | cpu | 0.516913 | 2.452 |
| embree_compact_summary | embree | 0.127206 | 0.603 |
| postgresql_same_semantics_on_linux_when_available | postgresql | 0.147856 | 0.701 |

Top non-query phases on RTX path:
- `one_shot_total_sec` = `2.024602s`
- `residual_host_overhead_sec` = `1.071766s`
- `prepare_total_sec` = `0.741265s`
- `close_sec` = `0.000779s`

## outlier_detection / prepared_fixed_radius_density_summary

- claim scope: `prepared fixed-radius scalar threshold-count traversal only`
- public wording status: `public_wording_reviewed`
- public wording boundary: Only the prepared fixed-radius scalar threshold-count sub-path is covered; per-point labels and full anomaly-detection behavior are outside this wording.
- cloud comparable phase: `native_threshold_query` = `0.189633s`
- review note: Fixed-radius review stays bounded to prepared scalar-summary semantics. Optional SciPy/reference baselines remain excluded from the active mandatory gate.

| Baseline | Backend | Comparable phase (s) | Ratio baseline/cloud |
|---|---|---:|---:|
| cpu_scalar_threshold_count_oracle | cpu_oracle | 0.027044 | 0.143 |
| embree_scalar_or_summary_path | embree | 0.206962 | 1.091 |

Top non-query phases on RTX path:
- `residual_misc_sec` = `1.623651s`
- `pack_points_sec` = `0.260237s`
- `postprocess_median_sec` = `0.113743s`
- `prepare_sec` = `0.003406s`

## dbscan_clustering / prepared_fixed_radius_core_flags

- claim scope: `prepared fixed-radius scalar core-count traversal only`
- public wording status: `public_wording_reviewed`
- public wording boundary: Only the prepared fixed-radius scalar core-count sub-path is covered; per-point core flags and Python cluster expansion are outside this wording.
- cloud comparable phase: `native_threshold_query` = `0.184927s`
- review note: Fixed-radius review stays bounded to prepared scalar-summary semantics. Optional SciPy/reference baselines remain excluded from the active mandatory gate.

| Baseline | Backend | Comparable phase (s) | Ratio baseline/cloud |
|---|---|---:|---:|
| cpu_scalar_threshold_count_oracle | cpu_oracle | 0.024832 | 0.134 |
| embree_scalar_or_summary_path | embree | 0.211451 | 1.143 |

Top non-query phases on RTX path:
- `residual_misc_sec` = `0.664261s`
- `pack_points_sec` = `0.246226s`
- `postprocess_median_sec` = `0.114049s`
- `prepare_sec` = `0.005275s`

## robot_collision_screening / prepared_pose_flags

- claim scope: `prepared OptiX ray/triangle any-hit pose-flag summary`
- public wording status: `public_wording_blocked`
- public wording boundary: The prepared ray/triangle any-hit scalar pose-count path is a real RT-core path, but larger RTX repeats stayed below the 100 ms public-review timing floor.
- cloud comparable phase: `native_anyhit_query` = `0.000327s`
- review note: Robot review is bounded to scalar colliding-pose count semantics. The structured Goal762 row exposes scene/ray/query phases, but not the full Python input phase now described separately in Goal772.

| Baseline | Backend | Comparable phase (s) | Ratio baseline/cloud |
|---|---|---:|---:|
| cpu_oracle_pose_count | cpu_oracle | 594.651925 | 1817901.555 |
| embree_anyhit_pose_count_or_equivalent_compact_summary | embree | 0.581851 | 1778.768 |

Top non-query phases on RTX path:
- `prepare_scene_sec` = `1.101614s`
- `prepare_rays_sec` = `0.019577s`
- `prepare_pose_indices_sec` = `0.000968s`
- `oracle_validate_sec` = `0.000000s`
