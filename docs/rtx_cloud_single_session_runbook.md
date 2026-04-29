# RTX Cloud Single-Session Runbook

This runbook is for paid NVIDIA RTX pod time. It exists to avoid repeated
restart/stop cycles while RTDL is validating NVIDIA RT-core app evidence.

After Goal1043, every claim-grade pod batch must preserve source traceability
even when the repo is staged with `rsync` instead of `git clone`. After
Goal1082, the original Goal1072 global-coordinate facility 2.5M timing row is
blocked because the same-scale CPU oracle disagrees with the validation-skipped
RTX artifact. After Goal1083/Goal1084, the next facility pod run must use the
precision-safe `facility_service_coverage_recentered` scenario and must not use
`--skip-validation`. After Goal1093, Barnes-Hut has a superseding depth-8
validation plus 20M timing packet. Robot still needs a same-scale non-OptiX
baseline before public wording review; that baseline is not a cloud-GPU task.
Do not spend paid pod time rerunning rejected rows until their local code or
scale contracts change. The runner accepts `RTDL_SOURCE_COMMIT` first, then
falls back to git, then to `.rtdl_source_commit`.

## Before Starting A Pod

Run this locally first:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
PYTHONPATH=src:. python3 scripts/goal1025_pre_cloud_rtx_app_batch_readiness.py \
  --output-json docs/reports/goal1046_pre_cloud_rtx_app_batch_readiness_2026-04-27.json \
  --output-md docs/reports/goal1046_pre_cloud_rtx_app_batch_readiness_2026-04-27.md
PYTHONPATH=src:. python3 scripts/goal1026_pre_cloud_runner_dry_run_audit.py \
  --output-json docs/reports/goal1046_pre_cloud_runner_dry_run_audit_2026-04-27.json \
  --output-md docs/reports/goal1046_pre_cloud_runner_dry_run_audit_2026-04-27.md
```

Start a pod only if the result is:

```text
"valid": true
```

Do not start a pod for one app at a time. Once a pod is running, do not run the
entire active+deferred manifest blindly. Run the OOM-safe groups below, copying
artifacts back after each group.

The current Goal1025/Goal1026 local gates expect 18 public apps, 16 NVIDIA RTX
targets, 2 non-NVIDIA exclusions, 17 active+deferred manifest entries, and 16
unique manifest commands. If those counts drift, refresh the manifest and the
runbook before starting paid cloud time.

For the current post-Goal1094 follow-up, also regenerate the Goal1084,
Goal1093, Goal1094, and relevant intake/status artifacts locally before
starting paid cloud time:

```bash
PYTHONPATH=src:. python3 scripts/goal1084_facility_recentered_rtx_pod_packet.py
PYTHONPATH=src:. python3 scripts/goal1093_barnes_hut_20m_contract_packet.py
PYTHONPATH=src:. python3 scripts/goal1094_v1_rtx_readiness_status_refresh.py
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1084_facility_recentered_rtx_pod_packet_test \
  tests.goal1093_barnes_hut_20m_contract_packet_test \
  tests.goal1094_v1_rtx_readiness_status_refresh_test
```

The generated Goal1084, Goal1093, and Goal1094 artifacts must report:

```text
"valid": true
```

The generated Goal1084 runner must contain no `--skip-validation`. If the
facility recentered validation is too expensive on the pod, copy back the
partial artifact and stop rather than publishing a speedup ratio. No public
wording can change without later artifact intake and 2+ AI review. The generated
Goal1093 Barnes-Hut runner must run the depth-8 validation row without
`--skip-validation`, then run the 20M timing-only row with `--skip-validation`.

If the only pending follow-up is the historical graph/Jaccard retry, use
Goal914 instead of the full group list:

```bash
PYTHONPATH=src:. python3 scripts/goal914_rtx_targeted_graph_jaccard_rerun.py \
  --mode run \
  --copies 20000 \
  --graph-chunk-copies 0 \
  --jaccard-chunk-copies 100,50,20 \
  --output-json docs/reports/goal914_rtx_targeted_graph_jaccard_rerun_rtx.json
```

Goal914 intentionally runs the fixed graph gate once and then Jaccard
production plus smaller diagnostic chunk sizes in the same pod session. It does
not authorize RTX speedup claims. For the current post-Goal923 v1.0 batch,
prefer the OOM-safe groups below because the DB Goal921 rerun and several
deferred app gates still need consolidated evidence. After Goals933 and 934,
the segment/polygon deferred entries use prepared polygon-BVH profilers rather
than the older one-shot gates, so the next pod can separate setup from warm
query timing.

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
OptiX backend. Match OptiX headers to the installed driver:

- Driver `550.127.05`: use OptiX SDK headers `v8.0.0`; newer OptiX 8.1/9.0
  headers can fail at runtime with `Unsupported ABI version`.
- Driver `580.126.09` or newer: OptiX SDK headers `v9.0.0` worked in the
  previous RTDL A5000 run.

Do not patch `OPTIX_ABI_VERSION` manually. If bootstrap reports
`Unsupported ABI version`, switch to driver-compatible headers or a newer
driver image before running benchmarks.

```bash
cd /workspace/rtdl_python_only
OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 \
CUDA_PREFIX=/usr/local/cuda-12.4 \
NVCC=/usr/local/cuda-12.4/bin/nvcc \
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check.json
```

Do not continue if bootstrap status is not `ok`.

## Current Post-Goal1094 Runner

For the next current v1.0 RTX pod session, run the generated Goal1084 facility
runner and, if pod time remains after copying back Goal1084 artifacts, run the
generated Goal1093 Barnes-Hut runner. The older Goal1072 runner is historical
evidence and should not be used for facility public wording because Goal1082
found same-scale disagreement in its validation-skipped 2.5M global-coordinate
row. The older Goal1076 Barnes-Hut runner is also historical because Goal1093
supersedes its depth-6-validation/depth-8-timing mismatch. The older broad batch
lists below are retained for historical fallback and targeted debugging, but
they are not the primary post-Goal1094 procedure.

From the pod checkout root:

```bash
cd /workspace/rtdl_python_only
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-9.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so
export RTDL_SOURCE_COMMIT="$(cat /workspace/rtdl_python_only/.rtdl_source_commit 2>/dev/null || git rev-parse HEAD)"

bash scripts/goal1084_facility_recentered_rtx_pod_packet_runner.sh
```

Goal1084 executes exactly one active row:

- same-scale validation and timing for `facility_knn_assignment / coverage_threshold_prepared_recentered` at 2,500,000 copies

Do not edit the generated Goal1084 runner on the pod to add
`--skip-validation`. If the row cannot finish, copy back the failing artifact
and stop interpreting it as claim-grade evidence. Robot is intentionally absent
because its next blocker is a same-scale non-OptiX baseline, not another RTX
timing row.

If pod time remains after Goal1084 artifacts are copied back, run the current
Barnes-Hut Goal1093 contract packet as a separate small batch:

```bash
bash scripts/goal1093_barnes_hut_20m_contract_runner.sh
```

Goal1093 executes exactly two rows:

- depth-8 correctness-validation `barnes_hut_force_app / node_coverage_prepared_rich`
  at 4,096 bodies, 65,536 nodes, radius 0.1, hit threshold 4, without `--skip-validation`
- depth-8 20M timing-repeat `barnes_hut_force_app / node_coverage_prepared_rich`
  at 20,000,000 bodies, 65,536 nodes, radius 0.1, hit threshold 4, with `--skip-validation`

The Goal1093 timing row is timing-only and uses `--skip-validation`; it requires
the separate depth-8 validation row and later artifact intake/review before any
public wording can change.

Copy back the entire Goal1084 report directory before stopping the pod:

```bash
scp -r -P <port> -i ~/.ssh/id_ed25519 \
  root@<host>:/workspace/rtdl_python_only/docs/reports/goal1084_facility_recentered_rtx_pod_packet \
  /Users/rl2025/rtdl_python_only/docs/reports/
```

Then write/run a Goal1084 artifact-intake step before interpreting the copied
artifacts. Until that intake and 2+ AI review exist, copied artifacts are
engineering evidence only:

```bash
cd /Users/rl2025/rtdl_python_only
# pending after the pod run: scripts/goal1085_goal1084_artifact_intake.py
```

For Goal1093, copy back the whole Barnes-Hut report directory as well:

```bash
scp -r -P <port> -i ~/.ssh/id_ed25519 \
  root@<host>:/workspace/rtdl_python_only/docs/reports/goal1093_barnes_hut_20m_contract \
  /Users/rl2025/rtdl_python_only/docs/reports/
```

Then write/run a Goal1093 artifact-intake step before interpreting the copied
artifacts. Until that intake and 2+ AI review exist, copied artifacts are
engineering evidence only.

Goal1063 says the broader rejected not-reviewed rows remain local-only until
code or scale changes. Goal1071 superseded the Goal1068 facility/robot timing
scales and blocked Barnes-Hut under the current contract; Hausdorff remains
blocked by its analytic tiled oracle. Do not use the Goal1053 11-command batch
to collect those rows again unless a later local audit supersedes
Goal1063/Goal1071.

## OOM-Safe Small Batches

Historical fallback: Run one group at a time. This prevents a single
high-memory workload from hanging SSH or losing all progress.

Set common environment first:

```bash
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so
export RTDL_SOURCE_COMMIT="$(cat /workspace/rtdl_python_only/.rtdl_source_commit 2>/dev/null || git rev-parse HEAD)"
```

Use `RTDL_OPTIX_PTX_COMPILER=nvcc` on pods where NVRTC tries to include
incomplete host libc headers such as missing `gnu/stubs-32.h`.
Do not continue if `RTDL_SOURCE_COMMIT` is empty; artifacts without a source
commit are engineering diagnostics only, not claim-grade evidence.

### Group A: Robot Flagship

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_pose_flags \
  --output-json docs/reports/goal761_group_a_robot_summary.json
```

### Group B: Fixed-Radius Scalar Counts

This command covers both outlier and DBSCAN because they intentionally share
one output artifact. The manifest command must run
`scripts/goal757_optix_fixed_radius_prepared_perf.py --result-mode
threshold_count`, which maps to the public outlier `density_count` scalar path
and DBSCAN `core_count` scalar path. It must not be interpreted as per-point
outlier labels, per-point core flags, full DBSCAN clustering, or whole-app
speedup. After Goal1043, Group B must run with validation enabled; do not add
`--skip-validation` to the fixed-radius commands.

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

Expected current manifest commands for this group:

- `road_hazard_native_summary_gate` runs
  `scripts/goal933_prepared_segment_polygon_optix_profiler.py` with
  `--scenario road_hazard_prepared_summary`.
- `segment_polygon_hitcount_native_experimental` runs
  `scripts/goal933_prepared_segment_polygon_optix_profiler.py` with
  `--scenario segment_polygon_hitcount_prepared`.
- `segment_polygon_anyhit_rows_prepared_bounded_gate` runs
  `scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py` with
  bounded output metadata (`emitted_count`, `copied_count`, `overflowed`).

### Group F: Graph Gate

This group intentionally uses the regenerated Goal759 manifest command. The
current graph gate must run in summary analytic single-launch mode so it reaches
OptiX before any CPU-reference validation:
`--output-mode summary --validation-mode analytic_summary --chunk-copies 0`.
After Goal913, graph `visibility_edges` uses `rt.visibility_pair_rows(...)`,
not Cartesian `rt.visibility_rows(...)`, so the intended row count is
`4 * copies` rather than all copied observers crossed with all copied targets.

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only graph_visibility_edges_gate \
  --output-json docs/reports/goal761_group_f_graph_summary.json
```

### Group G: Prepared Decision Apps

Use the manifest-sized validated commands first. Goal932 removed
`--skip-validation` from the future Hausdorff/ANN/Barnes-Hut manifest entries,
so a valid Group G artifact must carry real validation status instead of a
manual skipped-validation placeholder.

```bash
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only directed_threshold_prepared \
  --only candidate_threshold_prepared \
  --only node_coverage_prepared \
  --output-json docs/reports/goal761_group_g_prepared_decision_summary.json
```

If the pod OOMs, keep the same pod running and retry only the failed target at a
smaller scale after copying back the failing summary and artifact. Do not add
`--skip-validation`; reduce `--copies` or `--body-count` and keep validation
enabled so the artifact can still be reviewed.

### Group H: Polygon Apps

This group intentionally uses the regenerated Goal759 manifest commands. The
current polygon/Jaccard gates must run in summary analytic/chunked mode so the
20k-copy cloud run does not build full CPU references or full row payloads
before the OptiX candidate-discovery path:
`--output-mode summary --validation-mode analytic_summary --chunk-copies 100`.
After Goal913, the Jaccard artifact emits `candidate_diagnostics`; use those
fields first if parity fails, before changing scale or restarting the pod.

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

Current deferred targets after Goal923:

- `graph_analytics`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `barnes_hut_force_app`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Use this targeted retry shape:

```bash
cd /workspace/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --only graph_visibility_edges_gate \
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
- the `source_commit` captured from `RTDL_SOURCE_COMMIT`, git, or
  `.rtdl_source_commit`

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
- `docs/reports/goal761_group_g_prepared_decision_summary.json`
- `docs/reports/goal761_group_h_polygon_summary.json`
- all manifest `--output-json` artifacts, including `goal759_*`, `goal887_*`,
  `goal889_*`, `goal933_*`, `goal934_*`, `goal877_*`, `goal811_*`,
  `goal807_*`, and historical `goal873_*` / `goal888_*` outputs when present

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
