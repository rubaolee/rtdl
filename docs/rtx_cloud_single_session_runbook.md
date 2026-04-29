# RTX Cloud Single-Session Runbook

This runbook is for paid NVIDIA RTX pod time. It exists to avoid repeated
restart/stop cycles while RTDL is validating NVIDIA RT-core app evidence.

After Goal1043, every claim-grade pod batch must preserve source traceability
even when the repo is staged with `rsync` instead of `git clone`. After
Goal1072, the current follow-up batch is the post-scale-up path: rerun the two
remaining blocked public wording rows (`facility_knn_assignment` and
`robot_collision_screening`) at the scales proven useful by Goal1071, with
separate correctness-validation and large timing-repeat commands. Barnes-Hut is
not in the active pod batch because Goal1071 showed its current four-node
contract is too small to produce meaningful RTX traversal timing. Do not spend
paid pod time rerunning the other rejected not-reviewed rows until their local
code or scale contracts change. The runner accepts `RTDL_SOURCE_COMMIT` first,
then falls back to git, then to `.rtdl_source_commit`.

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

For the current post-Goal1072 follow-up, also regenerate the Goal1062,
Goal1063, Goal1067, Goal1072, and Goal1073 artifacts locally before starting
paid cloud time:

```bash
PYTHONPATH=src:. python3 scripts/goal1062_blocked_rtx_wording_rerun_manifest.py
PYTHONPATH=src:. python3 scripts/goal1063_pre_pod_local_completion_audit.py
PYTHONPATH=src:. python3 scripts/goal1067_scale_contract_repair_audit.py
PYTHONPATH=src:. python3 scripts/goal1072_post_scale_up_rtx_pod_batch.py
PYTHONPATH=src:. python3 scripts/goal1073_goal1072_artifact_intake.py
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1062_blocked_rtx_wording_rerun_manifest_test \
  tests.goal1063_pre_pod_local_completion_audit_test \
  tests.goal1067_scale_contract_repair_audit_test \
  tests.goal1072_post_scale_up_rtx_pod_batch_test \
  tests.goal1073_goal1072_artifact_intake_test
```

The generated Goal1062, Goal1063, Goal1067, and Goal1072 artifacts must report:

```text
"valid": true
```

The generated Goal1072 runner must contain no `--skip-validation` in the
`facility_knn_assignment` or `robot_collision_screening`
correctness-validation commands. Its large timing rows intentionally use
`--skip-validation`; those rows are timing-only and cannot authorize public
wording without later artifact-intake and 2+ AI review. The Goal1073 intake
should report `needs_cloud_artifacts` before the next pod run and must still
authorize zero public speedup claims.

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

## Current Post-Goal1072 Runner

For the next current v1.0 RTX pod session, prefer the generated Goal1072 runner
over the older Goal1068, Goal1053, or Goal759/Goal761 grouped paths. Goal1072
combines the remaining blocked facility/robot wording rows at the Goal1071
scale-up values that crossed the 100 ms timing floor. It excludes Barnes-Hut
until a richer node/tree traversal contract exists, so the next pod session
does not waste paid GPU time repeating the known four-node Barnes-Hut contract.
The older broad batch lists below are retained for historical fallback and
targeted debugging, but they are not the primary post-Goal1072 procedure.

From the pod checkout root:

```bash
cd /workspace/rtdl_python_only
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so
export RTDL_SOURCE_COMMIT="$(cat /workspace/rtdl_python_only/.rtdl_source_commit 2>/dev/null || git rev-parse HEAD)"

bash scripts/goal1072_post_scale_up_rtx_pod_batch_runner.sh
```

Goal1072 executes exactly four active rows:

- correctness-validation `facility_knn_assignment / coverage_threshold_prepared`
- large timing-repeat `facility_knn_assignment / coverage_threshold_prepared` at 2,500,000 copies
- correctness-validation `robot_collision_screening / prepared_pose_flags`
- large timing-repeat `robot_collision_screening / prepared_pose_flags` at 36,000,000 poses

Do not edit the generated runner on the pod to add `--skip-validation` to the
two correctness-validation rows. If a validation row cannot finish, copy
back the failing artifact and stop interpreting that row as claim-grade
evidence. The two large timing rows already use `--skip-validation`; they are
timing-only evidence and require separate validation rows plus later review.
Barnes-Hut is intentionally absent from the Goal1072 runner and remains blocked
for benchmark-contract redesign.

After Goal1075/Goal1076, Barnes-Hut has a separate rich-contract pod candidate.
Do not merge it into the facility/robot Goal1072 batch. If pod time remains
after Goal1072 artifacts are copied back, run it as a separate small batch:

```bash
bash scripts/goal1076_barnes_hut_rich_rtx_pod_candidate_runner.sh
```

Goal1076 executes exactly two rows:

- correctness-validation `barnes_hut_force_app / node_coverage_prepared_rich`
  at 1,024 bodies, tree depth 6, radius 0.1, hit threshold 4
- large timing-repeat `barnes_hut_force_app / node_coverage_prepared_rich`
  at 1,000,000 bodies, tree depth 8, radius 0.1, hit threshold 4

The Goal1076 timing row is timing-only and uses `--skip-validation`; it requires
the separate validation row and later artifact intake/review before any public
wording can change.

Copy back the entire Goal1072 report directory before stopping the pod:

```bash
scp -r -P <port> -i ~/.ssh/id_ed25519 \
  root@<host>:/workspace/rtdl_python_only/docs/reports/goal1072_post_scale_up_rtx_pod_batch \
  /Users/rl2025/rtdl_python_only/docs/reports/
```

Then run the Goal1073 artifact-intake step before interpreting the copied
artifacts. Until that intake and 2+ AI review exist, copied artifacts
are engineering evidence only:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal1073_goal1072_artifact_intake.py
```

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
