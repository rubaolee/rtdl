# Goal1301 Pod Intake: Outlier And DBSCAN Generic Migration

Date: 2026-05-05

## Scope

Goal1301 migrates outlier and DBSCAN fixed-radius threshold summary paths onto
the Goal1298 generic fixed-radius threshold-count primitive:

- `outlier_detection / rt_count_threshold`
- `outlier_detection / rt_count_threshold_prepared`
- `dbscan_clustering / rt_core_flags`
- `dbscan_clustering / rt_core_flags_prepared`

This is internal v1.5 migration evidence only.

## Source

Pod source commit:

```text
8adb88be41311f79129374aa64887a730d488117
```

## Commands

```text
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode rt_count_threshold_prepared \
  --output-mode density_count

PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode rt_core_flags_prepared \
  --output-mode core_count
```

## Result

| App | OptiX path | Scale | Generic primitive | Summary primitive | Result | Parity |
| --- | --- | --- | --- | --- | --- | --- |
| `outlier_detection` | `rt_count_threshold_prepared / density_count` | 8192 points | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` | 6144 threshold-reached, 2048 outliers | `matches_oracle=true` |
| `dbscan_clustering` | `rt_core_flags_prepared / core_count` | 8192 points | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` | 7168 core points | `matches_oracle=true` |

Focused pod tests:

```text
Ran 22 tests in 0.942s

OK
```

## Artifacts

Copied pod artifacts:

```text
docs/reports/goal1301_v1_5_outlier_dbscan_generic_migration_pod_results/outlier_optix_density_count_1024.json
docs/reports/goal1301_v1_5_outlier_dbscan_generic_migration_pod_results/dbscan_optix_core_count_1024.json
docs/reports/goal1301_v1_5_outlier_dbscan_generic_migration_pod_results/source_commit.txt
docs/reports/goal1301_v1_5_outlier_dbscan_generic_migration_pod_results/unittest_goal1301.txt
```

## Boundary

The result proves the migrated bounded fixed-radius threshold-decision/count
paths use the generic primitive and preserve oracle parity on an RTX pod. It
does not claim complete DBSCAN clustering, broad outlier analytics, neighbor-row
materialization speedup, whole-app acceleration, or public NVIDIA speedup
wording.
