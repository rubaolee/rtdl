# Goal910: RTX A5000 OOM-Safe Group Results

Date: 2026-04-24 local / 2026-04-25 UTC on pod

## Environment

- Pod: `root@69.30.85.237 -p 22002`
- GPU: NVIDIA RTX A5000, 24564 MiB
- Driver: `580.126.09`
- CUDA toolkit used for build: `12.4`
- OptiX headers: `optix-dev v9.0.0`
- Source snapshot: local commit `068f75d`

## Bootstrap

Bootstrap artifact:

- `docs/reports/goal763_rtx_cloud_bootstrap_check_goal909_2026-04-24.json`

Result:

- `make build-optix`: OK
- Focused native OptiX tests: 30 tests OK

## Group Results

| Group | Workloads | Result | Key evidence |
| --- | --- | --- | --- |
| A | Robot prepared pose count | PASS | `goal761_group_a_robot_summary_2026-04-24.json`; warm median `0.000368s` |
| B | Outlier + DBSCAN fixed-radius scalar summaries | PASS with `RTDL_OPTIX_PTX_COMPILER=nvcc` | Initial NVRTC run failed on missing `gnu/stubs-32.h`; NVCC rerun passed |
| C | DB sales risk + regional dashboard | PASS | DB native traversal phases recorded separately from exact filter/output pack/Python summary |
| D | Service coverage, event hotspot, facility coverage | PASS | Prepared summary gates completed at manifest scale |
| E | Road hazard, segment/polygon hit-count, bounded pair rows | PASS | Strict native OptiX gates passed |
| F | Graph visibility gate | STOPPED/BLOCKED | 20k-copy manifest run was CPU-bound for 155.9s before termination; smaller 1k-copy direct run also stayed CPU-bound with no GPU activity |
| G | Hausdorff, ANN, Barnes-Hut prepared decisions | PASS at reduced scale | 5k/5-iteration small runs passed for Hausdorff and ANN; 50k-body Barnes-Hut coverage passed |
| H | Polygon overlap/Jaccard native-assisted gates | MIXED | 20k-copy manifest artifacts returned `needs_optix_runtime` due CUDA OOM; 1k-copy direct retries passed |

## Important Findings

1. The OOM-safe group protocol worked: failures in Graph and 20k polygon did
   not lose artifacts from successful groups.
2. NVRTC is unreliable on this pod image for fixed-radius kernels because host
   headers reference missing `gnu/stubs-32.h`. Setting
   `RTDL_OPTIX_PTX_COMPILER=nvcc` and `RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc`
   resolves the fixed-radius run.
3. Graph visibility is not ready for manifest-scale cloud benchmarking. The
   current gate spends too much time in CPU-side preparation/reference work
   before reaching visible GPU execution.
4. Polygon overlap/Jaccard native-assisted paths need scale-aware memory
   limits. They pass at `--copies 1000` but OOM at `--copies 20000` on the
   A5000 pod.
5. Archive-based source sync is efficient, but the runner needs an explicit
   source-commit fallback. Goal910 adds `source_commit` metadata to
   `scripts/goal761_rtx_cloud_run_all.py`.

## Artifact Inventory

Successful or useful artifacts copied locally:

- `docs/reports/goal759_robot_pose_flags_phase_rtx_goal909_2026-04-24.json`
- `docs/reports/goal759_outlier_dbscan_fixed_radius_rtx_goal909_2026-04-24.json`
- `docs/reports/goal759_db_sales_risk_rtx_goal909_2026-04-24.json`
- `docs/reports/goal759_db_regional_dashboard_rtx_goal909_2026-04-24.json`
- `docs/reports/goal811_service_coverage_rtx_goal909_2026-04-24.json.gz`
- `docs/reports/goal811_service_coverage_rtx_goal909_2026-04-24.json.sha256`
- `docs/reports/goal811_event_hotspot_rtx_goal909_2026-04-24.json.gz`
- `docs/reports/goal811_event_hotspot_rtx_goal909_2026-04-24.json.sha256`
- `docs/reports/goal887_facility_service_coverage_rtx_goal909_2026-04-24.json`
- `docs/reports/goal888_road_hazard_native_optix_gate_rtx_goal909_2026-04-24.json.gz`
- `docs/reports/goal888_road_hazard_native_optix_gate_rtx_goal909_2026-04-24.json.sha256`
- `docs/reports/goal807_segment_polygon_optix_mode_gate_rtx_goal909_2026-04-24.json`
- `docs/reports/goal873_native_pair_row_optix_gate_rtx_strict_goal909_2026-04-24.json`
- `docs/reports/goal887_hausdorff_threshold_rtx_small_goal909_2026-04-24.json`
- `docs/reports/goal887_ann_candidate_coverage_rtx_small_goal909_2026-04-24.json`
- `docs/reports/goal887_barnes_hut_node_coverage_rtx_small_goal909_2026-04-24.json`
- `docs/reports/goal877_pair_overlap_phase_rtx_small_goal909_2026-04-24.json.gz`
- `docs/reports/goal877_pair_overlap_phase_rtx_small_goal909_2026-04-24.json.sha256`
- `docs/reports/goal877_jaccard_phase_rtx_small_goal909_2026-04-24.json`

Failure/diagnostic artifacts copied locally:

- `docs/reports/goal761_group_b_fixed_radius_summary_failed_2026-04-24.json`
- `docs/reports/goal761_group_f_graph_summary_stopped_2026-04-24.json`
- `docs/reports/goal877_pair_overlap_phase_rtx_goal909_2026-04-24.json.gz`
- `docs/reports/goal877_pair_overlap_phase_rtx_goal909_2026-04-24.json.sha256`
- `docs/reports/goal877_jaccard_phase_rtx_goal909_2026-04-24.json`

Large row-heavy JSON artifacts are stored as `.json.gz` plus `.sha256` sidecar
instead of plain tracked JSON to avoid bloating the repository while preserving
byte-identical evidence.

## Claim Boundary

These are cloud execution artifacts, not public speedup claims. Public claims
still require correctness review, comparable baselines, phase interpretation,
and 2+ AI consensus.

## Next Work

- Make the graph visibility gate phase-clean and avoid CPU/reference work in
  the cloud timing path.
- Add polygon overlap/Jaccard scale controls or tiling so 20k-copy runs do not
  OOM on 24 GiB GPUs.
- Keep `RTDL_OPTIX_PTX_COMPILER=nvcc` in the cloud runbook unless the pod image
  has proven reliable NVRTC host headers.
