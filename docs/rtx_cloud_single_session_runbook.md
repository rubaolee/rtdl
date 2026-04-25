# RTX Cloud Single-Session Runbook

This runbook is for paid NVIDIA RTX pod time. It exists to avoid repeated
restart/stop cycles while RTDL is validating NVIDIA RT-core app evidence.

## Before Starting A Pod

Run this locally first:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

Start a pod only if the result is:

```text
"valid": true
```

Do not start a pod for one app at a time. Once a pod is running, do not run the
entire active+deferred manifest blindly. Run the OOM-safe groups below, copying
artifacts back after each group.

## Recommended Pod Shape

Use an RTX-class NVIDIA GPU with real RT cores. Acceptable examples:

- RTX 4090
- RTX A5000/A6000
- L4
- A10/A10G

Avoid GTX 1070-class GPUs for RT-core claims. They can test CUDA/OptiX behavior
but not NVIDIA RT-core acceleration.

## Bootstrap On The Pod

After SSH into the pod and checking out the repo, first build and test the
OptiX backend. On driver `550.127.05`, use OptiX SDK headers `v8.0.0`; newer
OptiX 8.1/9.0 headers can fail at runtime with `Unsupported ABI version`.

```bash
cd /workspace/rtdl_python_only
OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 \
CUDA_PREFIX=/usr/local/cuda-12.4 \
NVCC=/usr/local/cuda-12.4/bin/nvcc \
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check.json
```

Do not continue if bootstrap status is not `ok`.

## OOM-Safe Small Batches

Run one group at a time. This prevents a single high-memory workload from
hanging SSH or losing all progress.

Set common environment first:

```bash
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so
```

### Group A: Robot Flagship

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_pose_flags \
  --output-json docs/reports/goal761_group_a_robot_summary.json
```

### Group B: Fixed-Radius Summaries

This command covers both outlier and DBSCAN because they intentionally share
one output artifact.

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
  --only segment_polygon_anyhit_rows_native_bounded_gate \
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

Start with lower scale if the pod previously OOMed. Increase only after the
small run succeeds.

```bash
python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario hausdorff_threshold \
  --mode optix \
  --copies 5000 \
  --iterations 5 \
  --radius 0.4 \
  --skip-validation \
  --output-json docs/reports/goal887_hausdorff_threshold_rtx_small.json

python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario ann_candidate_coverage \
  --mode optix \
  --copies 5000 \
  --iterations 5 \
  --radius 0.2 \
  --skip-validation \
  --output-json docs/reports/goal887_ann_candidate_coverage_rtx_small.json

python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario barnes_hut_node_coverage \
  --mode optix \
  --body-count 50000 \
  --iterations 5 \
  --radius 10.0 \
  --skip-validation \
  --output-json docs/reports/goal887_barnes_hut_node_coverage_rtx_small.json
```

### Group H: Polygon Apps

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only polygon_pair_overlap_optix_native_assisted_phase_gate \
  --only polygon_set_jaccard_optix_native_assisted_phase_gate \
  --output-json docs/reports/goal761_group_h_polygon_summary.json
```

## Artifact Copy Rule

After every group, copy back that group's summary JSON plus any `--output-json`
artifacts it created. Do not wait until all groups finish.

Example:

```bash
scp -P <port> -i ~/.ssh/id_ed25519_rtdl_codex \
  root@<host>:/workspace/rtdl_python_only/docs/reports/goal761_group_a_robot_summary.json \
  /Users/rl2025/rtdl_python_only/docs/reports/
```

## Optional Targeted Deferred Retry

If a small group succeeds except one deferred readiness gate, keep the same pod
running and retry only that deferred target after local diagnosis. Do not
restart the pod per app.

Current deferred targets:

- `graph_analytics`
- `service_coverage_gaps`
- `event_hotspot_screening`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `facility_knn_assignment`
- `barnes_hut_force_app`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Use this targeted retry shape:

```bash
cd /workspace/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --only graph_analytics \
  --include-deferred \
  --output-json docs/reports/goal761_retry_graph_summary.json
```

The deferred batch is allowed to expose failures. Preserve all artifacts and
treat failures as local follow-up work, not as public RTX claim evidence.

## Required Success Conditions

Bootstrap must report:

```text
"status": "ok"
```

Each group summary must report:

```text
"status": "ok"
```

Every non-dry-run artifact must include:

- `cloud_claim_contract`
- `required_phase_groups`
- all required phase keys for that app

If any result is `failed` or `needs_attention`, preserve the generated reports
and stop interpreting performance numbers as claim evidence.

## Files To Copy Back

Copy these files as they appear. Do not wait for all groups to finish before
copying earlier successful group artifacts:

- `docs/reports/goal763_rtx_cloud_bootstrap_check.json`
- `docs/reports/goal761_group_a_robot_summary.json`
- `docs/reports/goal761_group_b_fixed_radius_summary.json`
- `docs/reports/goal761_group_c_database_summary.json`
- `docs/reports/goal761_group_d_spatial_summary.json`
- `docs/reports/goal761_group_e_segment_polygon_summary.json`
- `docs/reports/goal761_group_f_graph_summary.json`
- `docs/reports/goal887_hausdorff_threshold_rtx_small.json`
- `docs/reports/goal887_ann_candidate_coverage_rtx_small.json`
- `docs/reports/goal887_barnes_hut_node_coverage_rtx_small.json`
- `docs/reports/goal761_group_h_polygon_summary.json`
- all manifest `--output-json` artifacts, including `goal759_*`, `goal887_*`,
  `goal888_*`, `goal889_*`, `goal873_*`, `goal877_*`, `goal811_*`, and
  `goal807_*` outputs when present

After all copied group artifacts are local, run Goal762 locally or on the pod
to build the aggregate artifact report. The aggregate report is useful, but it
must not replace per-group artifact copyback.

## Shutdown Rule

After copying artifacts back, stop or terminate the pod. Do not keep it running
while local code/doc review happens.

If the run fails because of a missing dependency or environment problem, fix as
much as possible locally before starting another pod.

## Claim Boundary

This runbook collects evidence. It does not authorize public RTX speedup claims.
Claims still require review of hardware metadata, correctness, phase separation,
artifact contracts, and comparison baselines.
