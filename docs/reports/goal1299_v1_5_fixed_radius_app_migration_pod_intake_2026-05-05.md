# Goal1299: Fixed-Radius App Migration Pod Intake

Date: 2026-05-05

## Source

- Commit: `13ec1e6e1f2af405cddc73b1fec67b650949d9a1`
- Pod repo: `/workspace/rtdl_goal1292`
- Pod env: reused Goal1292 OptiX/CUDA environment from
  `docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.sh`

## Commands

```text
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py \
  --backend optix \
  --copies 1024 \
  --optix-summary-mode gap_summary_prepared \
  --require-rt-core
```

```text
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py \
  --backend optix \
  --copies 1024 \
  --optix-summary-mode count_summary_prepared \
  --require-rt-core
```

## Result

Both migrated app paths ran successfully on the pod through the generic
fixed-radius threshold-count wrapper while preserving their bounded app
summaries and RT-core gate metadata.

| App path | Copies | Input scale | Scalar result | Native continuation | RT-core gate |
| --- | ---: | --- | ---: | --- | --- |
| `service_coverage_gaps / gap_summary_prepared` | 1024 | 4096 households, 3072 clinics | 3072 covered households | `optix_threshold_count` | true |
| `event_hotspot_screening / count_summary_prepared` | 1024 | 6144 events | 5119 hotspots | `optix_threshold_count` | true |

Focused pod tests passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1299_v1_5_fixed_radius_app_migration_test \
  tests.goal810_spatial_apps_optix_summary_surface_test \
  tests.goal955_spatial_prepared_native_continuation_test
```

Result: 13 tests OK.

## Artifacts

- `docs/reports/goal1299_v1_5_fixed_radius_app_migration_pod_results/service_coverage_optix_gap_summary_1024.json`
- `docs/reports/goal1299_v1_5_fixed_radius_app_migration_pod_results/event_hotspot_optix_count_summary_1024.json`
- `docs/reports/goal1299_v1_5_fixed_radius_app_migration_pod_results/source_commit.txt`
- `docs/reports/goal1299_v1_5_fixed_radius_app_migration_pod_results/unittest_goal1299.txt`

## Boundary

This is internal v1.5 migration evidence for two bounded fixed-radius
threshold-count app paths. It does not claim whole-app acceleration, row-output
acceleration, clinic-load calculation, hotspot-id materialization, ANN, DBSCAN,
Hausdorff, Barnes-Hut, or public NVIDIA speedup performance.
