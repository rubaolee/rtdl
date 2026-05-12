# Goal1711 OptiX Source Recovery and Linux Build Validation

Date: 2026-05-12

Status: local and Linux validation follow-up after Goal1710.

## Context

After Goal1710 fixed the local Windows Oracle toolchain environment and the
Linux host `192.168.1.20` validated the synced Embree/oracle path, the Linux
OptiX build exposed a second source-integrity issue in the current Windows
workspace:

- `src/native/optix/rtdl_optix_api.cpp` ended in the middle of the compact
  summary implementation.
- `src/native/optix/rtdl_optix_prelude.h` ended in the middle of the
  `request_count` parameter.
- `src/native/optix/rtdl_optix_workloads.cpp` ended in the middle of a
  `std::call_once` body and still contained stale replay artifacts.

This was source truncation/replay fallout, not a pod or hardware limit.

## Recovery

The OptiX API, prelude, workload, and core source were recovered from
`git HEAD` tails or full source where needed, then the app-agnostic native
migrations were replayed:

- Goal1673 pose-to-group native naming.
- Goal1695 KNN-to-k-closest-hits ABI naming.
- Goal1699 DB-to-columnar-payload ABI naming.
- Goal1704 legacy OptiX purity symbol cleanup.
- Goal1705 field/payload terminology cleanup.

The repaired OptiX source now has zero hits for:

- `pose`
- `db_copy_dataset_table`
- `DB columnar inputs must not be null`
- `field_index_count`
- incomplete `std::st` tail artifact
- `rtdl_optix_db_dataset`
- `rtdl_optix_run_lsi`
- `rtdl_optix_run_overlay`
- `rtdl_optix_run_triangle_probe`

## Local Validation

The following local source/migration slice passes:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1708_source_recovery_and_semantic_cleanup_test \
  tests.goal1710_windows_toolchain_validation_after_source_recovery_test \
  tests.goal1680_current_native_app_leakage_gap_test \
  tests.goal1668_native_engine_app_agnostic_directive_test -q
```

Result:

```text
Ran 26 tests in 0.673s
OK (skipped=1)
```

## Linux Validation

The current Windows workspace was copied to a disposable Linux directory:

```text
/home/lestat/work/rtdl_goal1710_sync
```

The protected old tarball was explicitly excluded:

```text
docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz
```

Linux host:

```text
192.168.1.20
GPU: NVIDIA GeForce GTX 1070
Driver: 580.126.09
OptiX SDK: /home/lestat/vendor/optix-dev
```

Linux source/recovery and Embree/oracle validation passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1708_source_recovery_and_semantic_cleanup_test \
  tests.goal1704_legacy_purity_symbol_cleanup_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1680_current_native_app_leakage_gap_test -q

PYTHONPATH=src:. python3 -m unittest \
  tests.goal903_embree_graph_ray_traversal_test -q
```

Results:

```text
Ran 20 tests in 0.442s
OK

Ran 8 tests in 14.977s
OK
```

After repairing the OptiX source tails, the Linux OptiX build passed:

```bash
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
```

and produced:

```text
build/librtdl_optix.so 792480 bytes
```

The Linux OptiX focused smoke slice also passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal933_prepared_segment_polygon_optix_test -q
```

Result:

```text
Ran 30 tests in 0.621s
OK
```

After copying the Goal1711 report/test and Gemini Goal1712 review into the
disposable Linux sync, the broader Linux gate also passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1711_optix_source_recovery_and_linux_build_validation_test \
  tests.goal1710_windows_toolchain_validation_after_source_recovery_test \
  tests.goal1708_source_recovery_and_semantic_cleanup_test \
  tests.goal1704_legacy_purity_symbol_cleanup_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1697_polygon_to_shape_native_migration_test \
  tests.goal1695_knn_to_k_closest_hits_native_migration_test \
  tests.goal1690_apple_rt_bfs_to_frontier_discover_migration_test \
  tests.goal1688_bfs_to_frontier_edge_traversal_native_migration_test \
  tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test \
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test \
  tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1676_native_leakage_delta_regression_test \
  tests.goal1668_native_engine_app_agnostic_directive_test \
  tests.goal1675_partner_protocol_substrate_test -q

PYTHONPATH=src:. python3 -m unittest \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal933_prepared_segment_polygon_optix_test -q
```

Results:

```text
Ran 83 tests in 1.130s
OK (skipped=1)

Ran 34 tests in 1.908s
OK
```

## Boundary

This validates source recovery, Linux Embree/oracle execution, Linux OptiX
build, and a small Linux OptiX smoke slice on the available GTX 1070 host.

It does not provide accepted pod performance or release hardware evidence.
The GTX 1070 host is useful for smoke testing, but the project memory already
marks it as insufficient for accepted v1.6.11/v1.8 NVIDIA evidence on the
collect-k target path.

Release readiness remains:

```text
needs-more-evidence
```

The next step is independent review of Goal1711, then pod/hardware validation
on suitable NVIDIA hardware if release evidence is required.
