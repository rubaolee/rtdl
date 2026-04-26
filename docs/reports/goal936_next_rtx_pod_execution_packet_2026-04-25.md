# Goal936 Next RTX Pod Execution Packet

Date: 2026-04-25

Purpose: exact command packet for the next paid RTX pod session. This packet is
derived from the current Goal759 manifest and the synchronized single-session
runbook after Goals933-935.

Boundary: this is an execution checklist only. It does not authorize RTX speedup
claims. Claims require copied artifacts, Goal762 analysis, app-by-app intake,
and independent review.

## Local Gate Before Starting Pod

Run locally first:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

Start a pod only if the result contains:

```text
"valid": true
```

## Pod Bootstrap

On the pod:

```bash
cd /workspace/rtdl_python_only
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so

PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check.json
```

Do not continue unless bootstrap status is `ok`.

## Group Commands

Run one group at a time and copy back artifacts after each group.

### Group A: Robot Flagship

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_pose_flags \
  --output-json docs/reports/goal761_group_a_robot_summary.json
```

### Group B: Fixed-Radius Summaries

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

### Group E: Prepared Segment/Polygon And Road Gates

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only road_hazard_native_summary_gate \
  --only segment_polygon_hitcount_native_experimental \
  --only segment_polygon_anyhit_rows_prepared_bounded_gate \
  --output-json docs/reports/goal761_group_e_segment_polygon_summary.json
```

Expected artifacts include:

- `docs/reports/goal933_road_hazard_prepared_summary_rtx.json`
- `docs/reports/goal933_segment_polygon_hitcount_prepared_rtx.json`
- `docs/reports/goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json`

### Group F: Graph Gate

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only graph_visibility_edges_gate \
  --output-json docs/reports/goal761_group_f_graph_summary.json
```

### Group G: Prepared Decision Apps

Use manifest-sized validated commands first. If the pod OOMs, use the small
manual fallback in `docs/rtx_cloud_single_session_runbook.md`.

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only directed_threshold_prepared \
  --only candidate_threshold_prepared \
  --only node_coverage_prepared \
  --output-json docs/reports/goal761_group_g_prepared_decision_summary.json
```

### Group H: Polygon Apps

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only polygon_pair_overlap_optix_native_assisted_phase_gate \
  --only polygon_set_jaccard_optix_native_assisted_phase_gate \
  --output-json docs/reports/goal761_group_h_polygon_summary.json
```

## Copyback Rule

After every group, copy back:

- the group summary JSON;
- every app artifact named in the group summary command;
- `docs/reports/goal763_rtx_cloud_bootstrap_check.json`;
- any `.sha256`, `.log`, or diagnostic sidecar produced by the group.

Do not wait until all groups finish to copy back earlier successful artifacts.

## Aggregate Analysis

After copied artifacts are available locally:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal762_rtx_cloud_artifact_report.py \
  --summary-json docs/reports/<group-or-combined-summary>.json \
  --output-json docs/reports/goal936_rtx_artifact_analysis_2026-04-25.json \
  --output-md docs/reports/goal936_rtx_artifact_analysis_2026-04-25.md
```

If separate group summaries are copied back, either analyze each group
separately or combine them only after preserving the raw group files.

## Stop Rule

Stop or terminate the pod after artifacts are copied back. Do not keep the pod
running while local review, docs, or app-promotion decisions happen.

## Local Dry-Run Verification

The two highest-risk command groups were dry-run checked locally:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --include-deferred \
  --only road_hazard_native_summary_gate \
  --only segment_polygon_hitcount_native_experimental \
  --only segment_polygon_anyhit_rows_prepared_bounded_gate \
  --output-json build/goal936_group_e_dry_run.json
```

Result: `status: ok`, `entry_count: 3`, `failed_count: 0`.

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --include-deferred \
  --only directed_threshold_prepared \
  --only candidate_threshold_prepared \
  --only node_coverage_prepared \
  --output-json build/goal936_group_g_dry_run.json
```

Result: `status: ok`, `entry_count: 3`, `failed_count: 0`.

`git diff --check` also passed after this packet was written.
