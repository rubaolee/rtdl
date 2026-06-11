# Benchmark Evidence Index

Status: current v2.10 source-tree evidence map.

Use this page when you want to reproduce or audit the ten benchmark-app front
doors. It is intentionally narrower than the full report history: it tells you
which row is current, what hardware it needs, and how to read the result.

Machine-readable source:

```bash
PYTHONPATH=src:. python scripts/rtdl_benchmark_evidence_index.py --json
```

Human-readable table:

```bash
PYTHONPATH=src:. python scripts/rtdl_benchmark_evidence_index.py
```

Front-door dry-run:

```bash
PYTHONPATH=src:. python scripts/goal3823_current_benchmark_front_door_runner.py --dry-run
```

Scale-profile pod runner:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/goal3828_current_benchmark_scale_profile_runner.py --output-dir docs/reports/current_benchmark_scale_profile_rerun
```

Bounded pod-validation bundle:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/rtdl_v2_10_pod_validation_bundle.py --run-front-door --run-scale-profile --output-dir docs/reports/v2_10_pod_validation_bundle_pod
```

For the full procedure, read
[v2.10 Pod Validation Bundle](../audit/runbooks/v2_10_pod_validation_bundle.md).

## Current Ten-App Rows

| App | Current front-door row | Partner/native note | Pod need |
| --- | --- | --- | --- |
| Hausdorff / X-HD | `hausdorff_xhd_current_optix_threshold` | primitive-first OptiX path; CuPy/Numba are comparison/reference lanes | NVIDIA pod for OptiX timing |
| Spatial RayJoin | `spatial_rayjoin_pip_count_current_prepared_optix` | contract-split RayJoin-style path; scalar/count paths are stronger than full paper reproduction | NVIDIA pod plus public-CDB fixture for representative route |
| RT-DBSCAN | `rt_dbscan_optix_numba_prepared_grid` | OptiX fixed-radius flags plus explicit Numba component continuation | CUDA pod with Numba |
| Robot collision | `robot_collision_optix_prepared_device_count` | primitive-only prepared static-scene collision count path | NVIDIA pod for OptiX timing |
| Contact manifold | `contact_manifold_optix_native_collect_k` | bounded collect/witness primitive path; no manifold-native ABI | NVIDIA pod for OptiX timing |
| RayDB-style | `raydb_style_optix_count_primitive_first` | primitive-first grouped count path; partner rows only for unfused continuations | NVIDIA pod; CUDA pod for CuPy/Numba partner comparison |
| Barnes-Hut | `barnes_hut_numba_exact_force` | aggregate-frontier pressure plus Numba exact-force reference | CUDA pod with Numba |
| LibRTS spatial index | `librts_spatial_index_optix_aabb_index` | prepared AABB-index benchmark slice, not full mutable LibRTS | NVIDIA pod for OptiX timing |
| RTNN | `rtnn_prepared_optix_ranked_summary` | prepared fixed-radius ranked summary path | NVIDIA pod for OptiX timing |
| Triangle counting | `triangle_counting_optix_native_summary` | explicit native graph summary path; candidate-row interpretation stays app code | NVIDIA pod for OptiX timing |

## Evidence Reports

- [Current benchmark front-door registry](../reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md)
- [Current benchmark scale-profile registry](../reports/goal3828_current_benchmark_scale_profile_registry_2026-06-07.md)
- [RTX 4000 Ada scale-profile refresh](../reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md)
- [Large-scale CuPy/Numba partner comparison](../reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md)

## Reading Rules

- A front-door row proves that the current command executes and keeps claim
  flags clean. It is not a performance leaderboard.
- A scale-profile row is more useful for performance planning, but still must
  be read by exact app, command, hardware, backend, partner, and dataset.
- CuPy/Numba comparison rows are partner-continuation evidence only. They do
  not become RT-core or whole-application speedup claims.
- If a row needs OptiX, use a pod or workstation with `RTDL_OPTIX_LIBRARY`
  pointing to `librtdl_optix`.
- If a row needs Numba, install the CUDA-capable Numba stack on the pod before
  running the packet.

For setup checks before running any benchmark, use the
[Source-Tree Doctor](source_tree_doctor.md).
