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
| Spatial RayJoin | `spatial_rayjoin_pip_count_current_prepared_optix` | contract-split RayJoin-style path; scalar/count paths are stronger than full paper reproduction; Goal4451 fail-closes unsafe prepared-points CUDA graph replay and keeps the batch executor as the repeated-PIP path | NVIDIA pod plus public-CDB fixture for representative route |
| RT-DBSCAN | `rt_dbscan_optix_grouped_stream_component_signature` | Generic OptiX fixed-radius/grouped-stream component labels plus explicit CuPy/Numba compact component-signature continuation; full rows remain a slower output contract | CUDA pod with CuPy and Numba |
| Robot collision | `robot_collision_prepared_grouped_segment_any_hit_numpy_lowering` | primitive-only prepared static-scene grouped-segment any-hit path; Goal4446 removes the major Python query-lowering debt while preserving the M31 same-contract backend comparison | NVIDIA pod for OptiX/Embree timing |
| Contact manifold | `contact_manifold_optix_native_collect_k` | bounded collect/witness primitive path; no manifold-native ABI | NVIDIA pod for OptiX timing |
| RayDB-style | `raydb_style_optix_count_primitive_first` | primitive-first grouped count path; partner rows only for unfused continuations | NVIDIA pod; CUDA pod for CuPy/Numba partner comparison |
| Barnes-Hut | `barnes_hut_mixed_explicit_cpu_numba_cuda_or_optix_numba` | Goal4450 exposes the fused Numba CUDA reusable API as the `fused_frontier_force_sum_bucketized_numba_cuda` app front door, with Goal4448 scale evidence beating the prepared RTDL/OptiX+Numba aggregate-frontier route; fused CPU/Numba remains the strongest CPU fused baseline; prepared RTDL/OptiX+Numba remains device-column RT evidence | NVIDIA/CUDA pod for Numba CUDA and OptiX; Numba CPU for CPU fused baseline |
| LibRTS spatial index | `librts_spatial_index_optix_aabb_index` | prepared AABB-index benchmark slice, not full mutable LibRTS | NVIDIA pod for OptiX timing |
| RTNN | `rtnn_mixed_exact_aggregate_or_graph_partner_bridge` | exact float64 aggregate for same-contract OptiX-vs-Embree comparison; prepared graph plus explicit CuPy/Numba same-stream partner bridge for resident app evidence | NVIDIA/CUDA pod for OptiX, CuPy, and Numba timing |
| Triangle counting | `triangle_counting_optix_native_summary` | scalar answer stays primitive-first; Goal4444 fixes the no-C++ Numba summary-contract staging debt, Goal4453 fills RT-1A2/RT-2A1 Numba geometry from partner-resident device columns, Goal4454 adds dense-label/sorted-key summary fast paths, Goal4455 confirms CuPy remains the large-scale performance partner, and Goal4456 extends Numba's summary remap fast path to bounded gapped ids | NVIDIA/CUDA pod for OptiX, CuPy, and Numba timing |

## Evidence Reports

- [Current benchmark front-door registry](../reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md)
- [Current benchmark scale-profile registry](../reports/goal3828_current_benchmark_scale_profile_registry_2026-06-07.md)
- [RTX 4000 Ada scale-profile refresh](../reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md)
- [Large-scale CuPy/Numba partner comparison](../reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md)
- [Barnes-Hut prepared aggregate-frontier partner scale ladder](../reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.md)
- [Barnes-Hut prepared aggregate-frontier app mode](../reports/goal4439_v3_0_m42_barnes_hut_prepared_frontier_app_mode_2026-06-16.md)
- [Barnes-Hut host baselines for the prepared app route](../reports/goal4440_v3_0_m43_barnes_hut_host_baselines_2026-06-16.md)
- [Barnes-Hut host Numba CPU baselines](../reports/goal4441_v3_0_m44_barnes_hut_host_numba_cpu_baselines_2026-06-16.md)
- [Barnes-Hut fused Numba CPU frontier baseline](../reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_frontier_2026-06-16.md)
- [Barnes-Hut Numba CUDA fused subtree prototype](../reports/goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_2026-06-16.md)
- [Reusable aggregate-tree fused Numba CUDA partner API](../reports/goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_2026-06-16.md)
- [Barnes-Hut fused Numba CUDA app front-door mode](../reports/goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_2026-06-16.md)
- [Goal4443 RTNN large app-front-door graph bridge](../reports/goal4443_v3_0_m47_rtnn_large_app_bridge_2026-06-16.md)
- [Goal4444 Triangle Numba direct-binary summary refresh](../reports/goal4444_v3_0_m48_triangle_numba_direct_binary_summary_2026-06-16.md)
- [Goal4445 DBSCAN compact component signature](../reports/goal4445_v3_0_m49_dbscan_component_signature_2026-06-16.md)
- [Goal4446 Robot Collision NumPy lowering](../reports/goal4446_v3_0_m50_robot_numpy_lowering_2026-06-16.md)
- [Goal4447 current benchmark adequacy refresh](../reports/goal4447_v3_0_m51_current_benchmark_adequacy_refresh_2026-06-16.md)
- [Goal4451 RayJoin PIP graph fail-closed](../reports/goal4451_v3_0_m55_rayjoin_pip_graph_fail_closed_2026-06-16.md)
- [Goal4452 RT-DBSCAN route decision refresh](../reports/goal4452_v3_0_m56_rtdbscan_route_decision_refresh_2026-06-16.md)
- [Goal4453 Triangle Numba device geometry](../reports/goal4453_v3_0_m57_triangle_numba_device_geometry_2026-06-16.md)
- [Goal4454 Triangle Numba summary fast paths](../reports/goal4454_v3_0_m58_triangle_numba_summary_fast_paths_2026-06-16.md)
- [Goal4455 Triangle partner rerank after M58](../reports/goal4455_v3_0_m59_triangle_partner_rerank_after_m58_2026-06-16.md)
- [Goal4456 Triangle bounded-id remap fast path](../reports/goal4456_v3_0_m60_triangle_bounded_id_remap_fast_path_2026-06-16.md)

## Reading Rules

- A front-door row proves that the current command executes and keeps claim
  flags clean. It is not a performance leaderboard.
- A ten-app packet is not ten broad RT-core speedup claims. Read each row by
  exact contract before using it as performance evidence.
- The v2.14 release packet keeps mixed rows explicit: Spatial RayJoin PIP is
  near parity and slightly Embree-faster in the refreshed human-scale slice,
  and prepared-points CUDA graph replay is not a current Spatial RayJoin
  performance lane after Goal4451.
  Goal4368 separately records an OptiX-over-Embree exact PIP engineering win
  that still does not beat RayJoin RT, and RTNN now has large RTDL-internal
  same-contract aggregate and app-front-door graph-bridge evidence while still
  not claiming full RTNN paper reproduction or arbitrary ANN-index speedup.
  RayJoin overlay reports the available 2/8
  exact CDB subset, not a full 8/8 Section 5.7 reproduction.
- A scale-profile row is more useful for performance planning, but still must
  be read by exact app, command, hardware, backend, partner, and dataset.
- CuPy/Numba comparison rows are partner-continuation evidence only. They do
  not become RT-core or whole-application speedup claims.
- For Barnes-Hut, Goal4438/4439 supersede the old partner-choice wording for
  the prepared RTDL/OptiX aggregate-frontier device-column weighted-vector
  contract: Numba wins the prepared RTDL/OptiX device-column partner route,
  while CuPy remains the same-contract GPU comparison partner. Goal4440 adds
  CPU/Embree host-materialized logical baselines for that route; Goal4441
  replaces the Python host vector continuation with Numba CPU continuation and
  shows the remaining debt is frontier collection and host materialization.
  Goal4442 then adds a fused CPU/Numba route that avoids frontier and
  contribution row materialization. Goal4448 adds a Python-source Numba CUDA
  fused-subtree prototype that also avoids those rows and is faster than the
  current prepared RTDL/OptiX+Numba route on the measured scale ladder.
  Goal4449 turns that fused shape into a reusable
  `prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda` app-reference
  partner API, and Goal4450 exposes it through
  `fused_frontier_force_sum_bucketized_numba_cuda` as an app front-door mode.
  These rows are correctness, route-choice, and bottleneck evidence, not public
  backend speedup wording. This is not a universal Numba, RT-core, or whole
  N-body speedup claim.
- The RayJoin external comparison is useful for LSI/PIP diagnosis, but it is
  not a full RayJoin paper reproduction and does not authorize RTDL-beats-RayJoin
  wording.
- If a row needs OptiX, use a pod or workstation with `RTDL_OPTIX_LIBRARY`
  pointing to `librtdl_optix`.
- If a row needs Numba, install the CUDA-capable Numba stack on the pod before
  running the packet.

For setup checks before running any benchmark, use the
[Source-Tree Doctor](source_tree_doctor.md).
