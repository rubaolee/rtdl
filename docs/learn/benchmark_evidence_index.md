# Benchmark Evidence Index

Status: current v2.14 source-tree evidence map.

Use this page when you want to reproduce or audit the ten benchmark-app front
doors. It is intentionally narrower than the full report history: it tells you
which row is current, what hardware it needs, and how to read the result.

For conservative performance interpretation, read the
[RT-Core Evidence Matrix](rt_core_evidence_matrix.md). It separates strong RT
evidence, mixed evidence, partner-led evidence, and coverage evidence.

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
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --materialize-rayjoin-public-cdb \
  --output-dir docs/reports/current_benchmark_scale_profile_rerun
```

The RayJoin public-CDB fixture is materialized only when the explicit
`--materialize-rayjoin-public-cdb` flag is present. Without that flag, the
runner records fixture status and lets the RayJoin row fail clearly if the
data is absent.

Bounded pod-validation bundle:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/rtdl_v2_10_pod_validation_bundle.py --run-front-door --run-scale-profile --materialize-rayjoin-public-cdb --output-dir docs/reports/v2_10_pod_validation_bundle_pod
```

For the full procedure, read
[v2.10 Pod Validation Bundle](../audit/runbooks/v2_10_pod_validation_bundle.md).

v2.11 closeout evidence:

- [v2.11 release package](../release_reports/v2_11/README.md)
- [v2.11 Embree CPU + partner reference packet](../reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md)
- [Backend comparison campaign closeout](../reports/goal4345_backend_comparison_campaign_closeout_2026-06-11.md)
- [Human-scale RT-core vs Embree CPU comparison](../reports/goal4353_human_scale_rt_vs_embree_run_20260612_pod_v3/summary.md)
- [RayJoin original-code same-stream comparison](../reports/goal4354_rayjoin_original_vs_rtdl_pod/goal4354_rayjoin_original_vs_rtdl_same_stream_summary.md)

v2.12 evidence:

- [v2.12 release package](../release_reports/v2_12/README.md)
- [v2.12 scoped RT-core vs Embree CPU comparison](../release_reports/v2_12/public_rt_vs_embree_comparison.md)
- [RTX A4000 RayJoin same-stream packet after Embree LSI repair](../reports/goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13.md)
- [Current OptiX-vs-Embree comparability index with all scoped pairs](../reports/goal4359_current_optix_embree_comparison_index_v2_12_2026-06-13.md)
- [Optimized OptiX-vs-Embree packet with zero active boundary-limited rows](../reports/goal4359_optimized_embree_optix_comparison_packet_v2_12_2026-06-13.md)
- [Robot Collision same-contract prepared-buffer evidence](../reports/goal4363_rtx_a4000_v2_12_robot_collision_same_contract_2026-06-13.md)
- [RayDB-style same-contract prepared grouped-reduction evidence](../reports/goal4364_rtx_a4000_v2_12_raydb_same_contract_2026-06-13.md)

v2.13 evidence:

- [v2.13 release package](../release_reports/v2_13/README.md)
- [v2.13 row-scoped RT-core vs Embree CPU comparison](../release_reports/v2_13/public_rt_vs_embree_comparison.md)
- [v2.13 public wording packet](../reports/goal4370_v2_13_public_wording_packet_2026-06-13.md)
- [Refreshed human-scale RT-core vs Embree CPU comparison](../reports/goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.md)
- [Embree CPU fairness hardening packet](../reports/goal4369_embree_cpu_fairness_hardening_2026-06-13.md)
- [PIP exact prepared-points executor](../reports/goal4368_pip_exact_prepared_points_executor_2026-06-13.md)
- [RayJoin authors-code comparison packet](../reports/goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.md)

v2.14 evidence:

- [v2.14 release package](../release_reports/v2_14/README.md)
- [v2.14 row-scoped RT-core vs Embree CPU comparison](../release_reports/v2_14/public_rt_vs_embree_comparison.md)
- [v2.14 public wording boundaries](../release_reports/v2_14/public_wording_boundaries.md)
- [v2.14 final closeout](../release_reports/v2_14/final_closeout.md)
- [v2.14 app-author implementation strategy](v2_14_app_author_implementation_strategy.md)

## Current Ten-App Rows

| App | Current front-door row | Partner/native note | Pod need |
| --- | --- | --- | --- |
| Hausdorff / X-HD | `hausdorff_xhd_current_optix_threshold` | primitive-first OptiX path; CuPy/Numba are comparison/reference lanes | NVIDIA pod for OptiX timing |
| Spatial RayJoin | `spatial_rayjoin_pip_count_current_prepared_optix` | contract-split RayJoin-style path; scalar/count paths are stronger than full paper reproduction | NVIDIA pod plus public-CDB fixture for representative route |
| RT-DBSCAN | `rt_dbscan_optix_numba_prepared_grid` | OptiX fixed-radius flags plus explicit Numba component continuation | CUDA pod with Numba |
| Robot collision | `robot_collision_optix_prepared_device_count` | primitive-only prepared static-scene collision count path | NVIDIA pod for OptiX timing |
| Contact manifold | `contact_manifold_optix_native_collect_k` | bounded collect/witness primitive path; no manifold-native ABI | NVIDIA pod for OptiX timing |
| RayDB-style | `raydb_style_optix_count_primitive_first` | primitive-first grouped count path; partner rows only for unfused continuations | NVIDIA pod; CUDA pod for CuPy/Numba partner comparison |
| Barnes-Hut | `barnes_hut_prepared_aggregate_frontier_numba` | prepared aggregate-frontier device columns plus Numba weighted-vector continuation; CuPy remains same-contract comparison; CPU/Embree host+Numba baselines are diagnostic only | NVIDIA/CUDA pod with OptiX, CuPy, and Numba |
| LibRTS spatial index | `librts_spatial_index_optix_aabb_index` | prepared AABB-index benchmark slice, not full mutable LibRTS | NVIDIA pod for OptiX timing |
| RTNN | `rtnn_prepared_optix_ranked_summary` | prepared fixed-radius ranked summary path | NVIDIA pod for OptiX timing |
| Triangle counting | `triangle_counting_optix_native_summary` | explicit native graph summary path; candidate-row interpretation stays app code | NVIDIA pod for OptiX timing |

## Evidence Reports

- [Current benchmark front-door registry](../reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md)
- [Current benchmark scale-profile registry](../reports/goal3828_current_benchmark_scale_profile_registry_2026-06-07.md)
- [RTX 4000 Ada scale-profile refresh](../reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md)
- [Large-scale CuPy/Numba partner comparison](../reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md)
- [Barnes-Hut prepared aggregate-frontier partner scale ladder](../reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.md)
- [Barnes-Hut prepared aggregate-frontier app mode](../reports/goal4439_v3_0_m42_barnes_hut_prepared_frontier_app_mode_2026-06-16.md)
- [Barnes-Hut host baselines for the prepared app route](../reports/goal4440_v3_0_m43_barnes_hut_host_baselines_2026-06-16.md)
- [Barnes-Hut host Numba CPU baselines](../reports/goal4441_v3_0_m44_barnes_hut_host_numba_cpu_baselines_2026-06-16.md)

## Reading Rules

- A front-door row proves that the current command executes and keeps claim
  flags clean. It is not a performance leaderboard.
- A ten-app packet is not ten broad RT-core speedup claims. Read each row by
  exact contract before using it as performance evidence.
- The v2.14 release packet keeps mixed rows explicit: Spatial RayJoin PIP is
  near parity and slightly Embree-faster in the refreshed human-scale slice,
  Goal4368 separately records an OptiX-over-Embree exact PIP engineering win
  that still does not beat RayJoin RT, and RTNN remains blocked as RT-core
  neighbor-search speedup wording. RayJoin overlay reports the available 2/8
  exact CDB subset, not a full 8/8 Section 5.7 reproduction.
- A scale-profile row is more useful for performance planning, but still must
  be read by exact app, command, hardware, backend, partner, and dataset.
- CuPy/Numba comparison rows are partner-continuation evidence only. They do
  not become RT-core or whole-application speedup claims.
- For Barnes-Hut, Goal4438 supersedes the old partner-choice wording only for
  the prepared aggregate-frontier device-column weighted-vector contract:
  Numba wins that measured partner route. Goal4439 exposes the route through
  the benchmark app as `prepared_aggregate_frontier_weighted_vector_optix`.
  Goal4440 adds CPU/Embree host-materialized logical baselines for that route;
  Goal4441 replaces the Python host vector continuation with Numba CPU
  continuation and shows the remaining debt is frontier collection and host
  materialization. These rows are correctness and bottleneck evidence, not
  public backend speedup wording. This is not a universal Numba, RT-core, or
  whole N-body speedup claim.
- The RayJoin external comparison is useful for LSI/PIP diagnosis, but it is
  not a full RayJoin paper reproduction and does not authorize RTDL-beats-RayJoin
  wording.
- If a row needs OptiX, use a pod or workstation with `RTDL_OPTIX_LIBRARY`
  pointing to `librtdl_optix`.
- If a row needs Numba, install the CUDA-capable Numba stack on the pod before
  running the packet.

For setup checks before running any benchmark, use the
[Source-Tree Doctor](source_tree_doctor.md).
