# Benchmark Evidence Index

Status: current source-tree evidence map for v2.14 release evidence plus V3
internal benchmark work.

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
| Hausdorff / X-HD | `hausdorff_xhd_current_optix_threshold` | Goal4513 closes this as a primitive-first exact nearest-witness/grouped-max route; M113 is not the current path; public speedup and automatic partner-selection wording remain blocked | NVIDIA pod for OptiX timing |
| Spatial RayJoin | `spatial_rayjoin_pip_count_current_prepared_optix` | Goal4514 closes this as a mixed-explicit app: Numba for bounded PIP one-shot, RTDL/OptiX prepared batch execution for repeated PIP, and RTDL/OptiX scalar/active-count primitives for LSI/overlay; Goal4451 fail-closes unsafe prepared-points CUDA graph replay; Goal4533 treats full RayJoin paper and Section 5.7 8/8 wording as future optional claim expansion rather than a current V3 app blocker | NVIDIA pod plus public-CDB fixture for representative route |
| RT-DBSCAN | `rt_dbscan_predicate_direct_status_component_signature` | Generic OptiX fixed-radius count-threshold device columns, now self-query optimized for prepared self-query workloads, plus explicit CuPy predicate direct-status compact component-signature continuation; Goal4510 closes the internal V3 clean target by confirming predicate direct-status wins all 524k/1M same-contract compact-signature rows, while 2M point-column reuse remains caller-owned-column only; Goal4519 refines the future M113 blocker as API-shape-ready, Goal4520 validates live chunk-handle smoke, and Goal4528 validates fixed-iteration prepared graph capture/replay for the future M113 shape without changing the current route; grouped-stream Numba remains the conservative fallback/reference and full rows remain a slower output contract | CUDA pod with CuPy and Numba |
| Robot collision | `robot_collision_prepared_grouped_segment_any_hit_numpy_lowering` | Goal4513 closes this as a no-partner prepared grouped-segment any-hit route; Goal4446 NumPy query lowering remains current; M113 is not needed | NVIDIA pod for OptiX/Embree timing |
| Contact manifold | `contact_manifold_optix_native_collect_k` | Goal4513 closes this as no-partner bounded witness collect; no manifold-native ABI; M113 is not the current path | NVIDIA pod for OptiX timing |
| RayDB-style | `raydb_style_optix_count_primitive_first` | Goal4513 closes this as primitive-first fused grouped reductions; partner rows are only for unfused continuations; M113 is not the current path | NVIDIA pod; CUDA pod for CuPy/Numba partner comparison |
| Barnes-Hut | `barnes_hut_mixed_explicit_cpu_numba_cuda_or_optix_numba` | Goal4512 closes the current V3 route-policy target: use `fused_frontier_force_sum_bucketized_cpu_numba` for tested 8192/16384/32768 rows, `fused_frontier_force_sum_bucketized_numba_cuda` for tested 65536/131072 rows, and prepared RTDL/OptiX+Numba only as OptiX-library CUDA aggregate-frontier device-column evidence; Goal4525/4526 add the RT-native wrapper/ABI surface fail-closed, Goal4527 rejects a naive all-node OptiX any-hit route because it cannot preserve parent-acceptance subtree-skip semantics, and Goal4534 records reviewed hierarchical traversal lowering as future design work rather than a current V3 app blocker | NVIDIA/CUDA pod for Numba CUDA and OptiX; Numba CPU for CPU fused baseline |
| LibRTS spatial index | `librts_spatial_index_optix_aabb_index` | Goal4513 closes this as a no-partner prepared AABB index query slice; not full mutable LibRTS; M113 is not the current path | NVIDIA pod for OptiX timing |
| RTNN | `rtnn_mixed_exact_aggregate_full_batch_or_graph_partner_bridge` | exact float64 aggregate for same-contract OptiX-vs-Embree comparison; full-batch non-graph prepared direct aggregate is the current KITTI-1M aggregate-only RTDL route and Goal4503 exposes it through the app front door with `--point-file`; prepared graph plus explicit CuPy/Numba same-stream partner bridge remains the partner-continuation route for uniform, shell, and clustered resident app evidence; Goal4498 defines the nine paper dataset targets, Goal4499 adds a deterministic KITTI bounded-family recipe layer, Goal4500 exports the same bounded KITTI CSV for RTDL OptiX/Embree exact aggregate gating, Goal4501 adds author same-input comparison, Goal4502 reranks aggregate-only batch size, Goal4504 codifies the size-aware execution-path policy, Goal4505 adds a dry-run 16-chunk plan for 1,048,576-query partner continuation, Goal4506 executes the 1,048,576-query uniform chunked partner route, Goal4507 extends it to shell and clustered, Goal4508 closes RTNN as an internal V3 clean target, Goal4509 lifts the M19 chunk shape into a reusable app-agnostic prepared graph chunk executor contract, and Goal4533 treats exact paper/same-output author wording as future optional claim expansion rather than a current V3 app blocker | NVIDIA/CUDA pod for OptiX, CuPy, Numba, and author-code diagnostics |
| Triangle counting | `triangle_counting_optix_native_summary` | scalar answer stays primitive-first; Goal4511 closes the internal V3 clean target: all three large former-OOM paper rows complete exactly, the current internal route is Goal4479 `numba_direct_sort_rle` prepared segment replay, and the Goal4494 integrated local-hash candidate stays rejected; Goal4521 explains the M113 blocker as generic chunked unique/count associativity, Goal4530 validates the app-agnostic CuPy device key/count payload merge half of the fix, Goal4531 validates a generic prepared weighted-replay device-output stream executor while fail-closing CUDA graph capture for that OptiX launch, Goal4539 confirms the graph-capture failure is capture-mode independent, and Goal4540 accepts the non-graph stream continuation contract to close Triangle as a current V3 target; cuGraph, authors pure kernels, M113 graph readiness, public RT-core speedup wording, app-specific native callbacks, and automatic partner selection remain blocked | NVIDIA/CUDA pod for OptiX, CuPy, and Numba timing |

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
- [Goal4458 Barnes-Hut current route rerank](../reports/goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.md)
- [Goal4483 Barnes-Hut large-scale rerank](../reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_packet_2026-06-16.md)
- [Goal4497 Barnes-Hut RT-native fused feasibility](../reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.md)
- [Goal4517 aggregate-tree fused RT-native contract](../reports/goal4517_v3_0_m121_aggregate_tree_fused_rt_native_contract_2026-06-17.md)
- [Goal4518 Barnes-Hut device-column RT-core boundary audit](../reports/goal4518_v3_0_m122_barnes_hut_device_column_rtcore_boundary_2026-06-17.md)
- [Goal4523 Barnes-Hut RT-native symbol gap](../reports/goal4523_v3_0_m127_barnes_hut_rt_native_symbol_gap_2026-06-17.md)
- [Goal4525 Barnes-Hut RT-native Python wrapper gate](../reports/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.md)
- [Goal4526 Barnes-Hut RT-native fail-closed ABI](../reports/goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_2026-06-17.md)
- [Goal4527 Barnes-Hut RT-native traversal semantic gate](../reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.md)
- [Goal4524 benchmark implementation queue](../reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.md)
- [Goal4533 V3 claim-scope closeout](../reports/goal4533_v3_0_m135_v3_claim_scope_closeout_2026-06-17.md)
- [Goal4534 V3 current app completion gate](../reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.md)
- [Goal4535 V3 completion readiness audit](../reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.md)
- [Goal4536 V3 internal completion packet](../reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md)
- [Goal4538 V3 completion review consensus](../reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md)
- [Goal4512 Barnes-Hut clean-target audit](../reports/goal4512_v3_0_m116_barnes_hut_clean_target_audit_2026-06-17.md)
- [Goal4513 primitive app clean-target audit](../reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md)
- [Goal4515 all benchmark app clean-target closeout](../reports/goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_2026-06-17.md)
- [Goal4443 RTNN large app-front-door graph bridge](../reports/goal4443_v3_0_m47_rtnn_large_app_bridge_2026-06-16.md)
- [Goal4459 RTNN clustered app-front-door graph bridge](../reports/goal4459_v3_0_m63_rtnn_clustered_app_bridge_2026-06-16.md)
- [Goal4460 RTNN shell app-front-door graph bridge](../reports/goal4460_v3_0_m64_rtnn_shell_app_bridge_2026-06-16.md)
- [Goal4498 RTNN paper dataset targets](../reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.md)
- [Goal4499 RTNN KITTI paper-family recipe](../reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.md)
- [Goal4500 RTNN KITTI same-input RTDL gate](../reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.md)
- [Goal4501 RTNN author same-input comparison](../reports/goal4501_v3_0_m105_rtnn_author_same_input_comparison_2026-06-17.md)
- [Goal4502 RTNN full-batch route refresh](../reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.md)
- [Goal4503 RTNN point-file app front door](../reports/goal4503_v3_0_m107_rtnn_point_file_front_door_2026-06-17.md)
- [Goal4504 RTNN execution-path policy refresh](../reports/goal4504_v3_0_m108_execution_path_policy_refresh_2026-06-17.md)
- [Goal4505 RTNN partner-continuation chunk plan](../reports/goal4505_v3_0_m109_rtnn_partner_chunk_plan_2026-06-17.md)
- [Goal4506 RTNN chunked partner runtime](../reports/goal4506_v3_0_m110_rtnn_chunked_runtime_2026-06-17.md)
- [Goal4507 RTNN chunked distribution matrix](../reports/goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.md)
- [Goal4508 RTNN clean-target closeout](../reports/goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.md)
- [Goal4509 prepared graph chunk executor](../reports/goal4509_v3_0_m113_prepared_graph_chunk_executor_2026-06-17.md)
- [Goal4516 prepared graph chunk adoption gate](../reports/goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_2026-06-17.md)
- [Goal4522 route-adequacy consistency](../reports/goal4522_v3_0_m126_route_adequacy_consistency_2026-06-17.md)
- [Goal4444 Triangle Numba direct-binary summary refresh](../reports/goal4444_v3_0_m48_triangle_numba_direct_binary_summary_2026-06-16.md)
- [Goal4445 DBSCAN compact component signature](../reports/goal4445_v3_0_m49_dbscan_component_signature_2026-06-16.md)
- [Goal4446 Robot Collision NumPy lowering](../reports/goal4446_v3_0_m50_robot_numpy_lowering_2026-06-16.md)
- [Goal4447 current benchmark adequacy refresh](../reports/goal4447_v3_0_m51_current_benchmark_adequacy_refresh_2026-06-16.md)
- [Goal4451 RayJoin PIP graph fail-closed](../reports/goal4451_v3_0_m55_rayjoin_pip_graph_fail_closed_2026-06-16.md)
- [Goal4514 RayJoin mixed-explicit clean-target audit](../reports/goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_2026-06-17.md)
- [Goal4452 RT-DBSCAN route decision refresh](../reports/goal4452_v3_0_m56_rtdbscan_route_decision_refresh_2026-06-16.md)
- [Goal4484 RT-DBSCAN compact-signature route matrix](../reports/goal4484_v3_0_m88_rtdbscan_compact_signature_matrix_2026-06-16.md)
- [Goal4485 RT-DBSCAN 1M compact-signature route matrix](../reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.md)
- [Goal4486 RT-DBSCAN self-query count-threshold optimization](../reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_2026-06-17.md)
- [Goal4487 RT-DBSCAN direct-status prepare breakdown](../reports/goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.json)
- [Goal4488 RT-DBSCAN direct-status row-columnization](../reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.md)
- [Goal4489 RT-DBSCAN direct-status caller-owned point columns](../reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.md)
- [Goal4490 RT-DBSCAN point-column app mode](../reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.md)
- [Goal4491 coordinate-column helper build cleanup](../reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.md)
- [Goal4495 RT-DBSCAN 2M point-column reuse](../reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.md)
- [Goal4496 RT-DBSCAN 2M point-column prepare profiles](../reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.md)
- [Goal4510 RT-DBSCAN clean-target audit](../reports/goal4510_v3_0_m114_rtdbscan_clean_target_audit_2026-06-17.md)
- [Goal4519 RT-DBSCAN chunk-handle gate](../reports/goal4519_v3_0_m123_rtdbscan_chunk_handle_gate_2026-06-17.md)
- [Goal4520 RT-DBSCAN chunk-handle smoke](../reports/goal4520_v3_0_m124_rtdbscan_chunk_handle_smoke_2026-06-17.md)
- [Goal4528 RT-DBSCAN prepared graph capture](../reports/goal4528_v3_0_m132_rtdbscan_prepared_graph_capture_2026-06-17.md)
- [Goal4453 Triangle Numba device geometry](../reports/goal4453_v3_0_m57_triangle_numba_device_geometry_2026-06-16.md)
- [Goal4454 Triangle Numba summary fast paths](../reports/goal4454_v3_0_m58_triangle_numba_summary_fast_paths_2026-06-16.md)
- [Goal4455 Triangle partner rerank after M58](../reports/goal4455_v3_0_m59_triangle_partner_rerank_after_m58_2026-06-16.md)
- [Goal4456 Triangle bounded-id remap fast path](../reports/goal4456_v3_0_m60_triangle_bounded_id_remap_fast_path_2026-06-16.md)
- [Goal4457 Triangle CuPy no-host-column summary route](../reports/goal4457_v3_0_m61_triangle_cupy_no_host_columns_2026-06-16.md)
- [Goal4492 Triangle source-group unique feasibility](../reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.md)
- [Goal4493 Triangle local-hash unique prototype](../reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.md)
- [Goal4494 Triangle integrated local-hash candidate](../reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.md)
- [Goal4511 Triangle Counting clean-target audit](../reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.md)
- [Goal4521 Triangle unique-count gate](../reports/goal4521_v3_0_m125_triangle_unique_count_gate_2026-06-17.md)
- [Goal4530 Triangle device key-payload merge](../reports/goal4530_v3_0_m133_triangle_device_key_payload_merge_2026-06-17.md)
- [Goal4531 Triangle weighted replay graph capture](../reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md)
- [Goal4539 Triangle capture-mode audit](../reports/goal4539_v3_0_m140_triangle_capture_mode_audit_2026-06-17.md)
- [Goal4540 Triangle non-graph stream closure gate](../reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md)

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
  same-contract aggregate plus uniform, shell, and clustered app-front-door
  graph-bridge evidence while still not claiming full RTNN paper reproduction
  or arbitrary ANN-index speedup. Goal4498 defines the paper dataset target
  matrix, Goal4499 lets real KITTI-family bounded recipes feed same-contract
  comparison when Velodyne data is present, and Goal4500 exports the same
  bounded KITTI CSV for the RTDL OptiX/Embree gate, with a tie-sensitive kth-id
  checksum caveat; uniform/shell/clustered rows remain scoped to RTDL-internal
  distribution evidence until exact KITTI, Stanford, and Millennium recipes are
  frozen. Goal4508 is the current RTNN reader closeout: internal V3 target
  closed, public speedup and same-output author claims still blocked. Goal4509
  turns the M19 chunk plan shape into a reusable app-agnostic prepared graph
  chunk executor contract for later apps.
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
  Goal4458 reranks the current app front doors under the same force-summary
  contract and confirms fused CPU/Numba is still fastest on the RTX 4000 Ada
  pod at 8192/16384/32768 bodies. Goal4483 extends the rerank to
  65536/131072 bodies and shows fused Numba CUDA becomes the fastest measured
  route there. Goal4497 records the feasibility boundary for the missing
  generic RT-native fused weighted-vector primitive; prepared RTDL/OptiX+Numba
  remains OptiX-library CUDA device-column evidence, not a Barnes-Hut RT-core speedup row.
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
