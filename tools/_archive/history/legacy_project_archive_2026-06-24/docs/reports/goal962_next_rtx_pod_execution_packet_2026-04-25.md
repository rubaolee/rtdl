# Goal962: Next RTX Pod Execution Packet

Date: 2026-04-25

## Verdict

Accepted with 2-AI consensus. Do not start a pod from this packet until an
RTX-class pod is intentionally available and the goal is to execute the grouped
cloud batch.

This packet is the exact next paid RTX pod execution plan after Goals 956-1000.
It is designed to avoid per-app pod churn. Run one RTX-class pod, execute
bootstrap, then run OOM-safe groups A-H, copying artifacts back after every
group.

## Local Preflight

Local pre-cloud readiness probe:

```text
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py --output-json /tmp/goal824_probe.json
```

Result:

```text
"valid": true
active_count: 8
deferred_count: 9
baseline_contract_count: 17
public_command_audit.valid: true
public_command_audit.command_count: 296
goal992_scalar_fixed_radius_command_exact: 4
```

The post-Goal1000 full local suite also passed:

```text
Ran 1927 tests in 156.203s
OK (skipped=196)
```

Recent local closure before the next pod:

- Goal996 refreshed public command truth coverage for the scalar fixed-radius
  commands.
- Goal997 resynced the local pre-cloud gate with the refreshed command audit.
- Goal998 resynced current claim-review packets to scalar
  threshold-count/core-count wording.
- Goal999 repaired stale tests and re-established a green full suite.
- Goal1000 made packed ctypes layouts explicit for Python 3.14+ import hygiene.

## Pod Requirements

Use a real RTX-class NVIDIA GPU:

- RTX 4090
- RTX A5000/A6000
- L4
- A10/A10G

Do not use GTX 1070-class GPUs for RT-core claims.

## Bootstrap

After SSH and checkout:

```bash
cd /workspace/rtdl_python_only
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so

OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 \
CUDA_PREFIX=/usr/local/cuda-12.4 \
NVCC=/usr/local/cuda-12.4/bin/nvcc \
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check.json
```

Stop immediately if bootstrap status is not `ok`.

## Group Commands

Run one group at a time. Copy artifacts back after each group.

### Group A: Robot Flagship

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_pose_flags \
  --output-json docs/reports/goal761_group_a_robot_summary.json
```

### Group B: Fixed-Radius Scalar Counts

This group runs the shared Goal757 fixed-radius profiler in scalar
`threshold_count` mode. Interpret the outlier section as the public
`density_count` scalar path and the DBSCAN section as the public `core_count`
scalar path; do not treat this group as per-point outlier labels, per-point
core flags, full DBSCAN clustering, or whole-app speedup.

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_fixed_radius_density_summary \
  --only prepared_fixed_radius_core_flags \
  --output-json docs/reports/goal761_group_b_fixed_radius_summary.json
```

### Group C: Database Analytics

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_db_session_sales_risk \
  --only prepared_db_session_regional_dashboard \
  --output-json docs/reports/goal761_group_c_database_summary.json
```

### Group D: Spatial Prepared Summaries

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only prepared_gap_summary \
  --only prepared_count_summary \
  --only coverage_threshold_prepared \
  --output-json docs/reports/goal761_group_d_spatial_summary.json
```

### Group E: Segment/Polygon And Road Gates

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only road_hazard_native_summary_gate \
  --only segment_polygon_hitcount_native_experimental \
  --only segment_polygon_anyhit_rows_prepared_bounded_gate \
  --output-json docs/reports/goal761_group_e_segment_polygon_summary.json
```

### Group F: Graph Gate

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only graph_visibility_edges_gate \
  --output-json docs/reports/goal761_group_f_graph_summary.json
```

### Group G: Prepared Decision Apps

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only directed_threshold_prepared \
  --only candidate_threshold_prepared \
  --only node_coverage_prepared \
  --output-json docs/reports/goal761_group_g_prepared_decision_summary.json
```

If Group G OOMs, keep the same pod running and retry only the failed target at
smaller scale after copying back the failing summary and artifact. Do not add
`--skip-validation`; reduce `--copies` or `--body-count` and keep validation
enabled.

### Group H: Polygon Apps

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only polygon_pair_overlap_optix_native_assisted_phase_gate \
  --only polygon_set_jaccard_optix_native_assisted_phase_gate \
  --output-json docs/reports/goal761_group_h_polygon_summary.json
```

If Jaccard fails, inspect `candidate_diagnostics` before changing scale or
restarting the pod.

## Copy-Back Rule

After every group, copy that group summary plus any created `--output-json`
artifact back to:

```text
/Users/rl2025/rtdl_python_only/docs/reports/
```

Do not wait for all groups to finish before copying earlier successful groups.

Required summaries:

- `docs/reports/goal763_rtx_cloud_bootstrap_check.json`
- `docs/reports/goal761_group_a_robot_summary.json`
- `docs/reports/goal761_group_b_fixed_radius_summary.json`
- `docs/reports/goal761_group_c_database_summary.json`
- `docs/reports/goal761_group_d_spatial_summary.json`
- `docs/reports/goal761_group_e_segment_polygon_summary.json`
- `docs/reports/goal761_group_f_graph_summary.json`
- `docs/reports/goal761_group_g_prepared_decision_summary.json`
- `docs/reports/goal761_group_h_polygon_summary.json`

Required per-app artifacts include:

- `docs/reports/goal759_db_sales_risk_rtx.json`
- `docs/reports/goal759_db_regional_dashboard_rtx.json`
- `docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json`
- `docs/reports/goal759_robot_pose_flags_phase_rtx.json`
- `docs/reports/goal811_service_coverage_rtx.json`
- `docs/reports/goal811_event_hotspot_rtx.json`
- `docs/reports/goal887_facility_service_coverage_rtx.json`
- `docs/reports/goal889_graph_visibility_optix_gate_rtx.json`
- `docs/reports/goal933_road_hazard_prepared_summary_rtx.json`
- `docs/reports/goal933_segment_polygon_hitcount_prepared_rtx.json`
- `docs/reports/goal887_hausdorff_threshold_rtx.json`
- `docs/reports/goal887_ann_candidate_coverage_rtx.json`
- `docs/reports/goal887_barnes_hut_node_coverage_rtx.json`
- `docs/reports/goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json`
- `docs/reports/goal877_pair_overlap_phase_rtx.json`
- `docs/reports/goal877_jaccard_phase_rtx.json`

## Shutdown Rule

After artifacts are copied back, stop or terminate the pod. Do not keep it
running while local artifact review happens.

## Boundary

This packet collects evidence only. It does not authorize release, public speedup claims, or broad app-level acceleration wording.
