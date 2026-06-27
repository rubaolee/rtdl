# Goal929 RTX 3090 Cloud Group Results

Date: 2026-04-25

## Verdict

Status: evidence captured; no public speedup claim authorized by this report.

The RunPod RTX 3090 session reached the intended OptiX/RTX paths for the current OOM-safe app groups and copied artifacts back after each group. Two initial attention cases were handled in-session:

- `graph_analytics`: the app artifact passed, but the analyzer initially required both CPU-reference and analytic-reference labels for an `analytic_summary` run. The local contract was narrowed so analytic-summary artifacts require analytic labels, OptiX labels, and strict fields only. The focused rerun passed with analyzer `status: ok`.
- `polygon_set_jaccard`: the `chunk-copies=100` and diagnostic `chunk-copies=50` runs missed candidate rows and failed parity. The production manifest was narrowed to the RTX-proven `chunk-copies=20` shape. The focused rerun passed with analyzer `status: ok`.

This report records cloud evidence and required follow-up. It does not promote any app to a public RTX speedup claim without separate baseline review and 2+ AI consensus.

## Environment

| Field | Value |
|---|---|
| Provider | RunPod |
| Host | `2f7110a266f5` |
| GPU | NVIDIA GeForce RTX 3090 |
| GPU memory | 24576 MiB |
| Driver | 580.126.20 |
| CUDA runtime shown by `nvidia-smi` | 13.0 |
| Build CUDA used for OptiX PTX | `/usr/local/cuda-12.4` |
| OptiX headers | `/workspace/vendor/optix-dev-9.0.0` |
| Python | 3.11.10 |
| Commit checkout | `7f569829fbad00f9bfa58e758b0fc4ee0324b410` |

## Bootstrap

| Check | Result |
|---|---|
| OptiX backend build | pass |
| Focused native OptiX tests | 30 tests OK |
| Bootstrap artifact | `docs/reports/cloud_2026_04_25/runpod_3090_2026_04_25/goal763_rtx_cloud_bootstrap_check.json` |

The fixed-radius OptiX kernels used `RTDL_OPTIX_PTX_COMPILER=nvcc` and `RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc` to avoid the pod image's NVRTC `gnu/stubs-32.h` issue.

## Group Results

| Group | Apps / paths | Runner | Analyzer | Key RTX phase timing |
|---|---|---:|---:|---|
| A | `prepared_pose_flags` | ok | ok | pose flags warm query median `0.000308 s` |
| B | `prepared_fixed_radius_density_summary`, `prepared_fixed_radius_core_flags` | ok | ok | fixed-radius warm query medians about `0.00131 s` |
| C | `prepared_db_session_sales_risk`, `prepared_db_session_regional_dashboard` | ok | ok | DB warm query medians `0.080087 s` and `0.111494 s`; native counters exported |
| D | `prepared_gap_summary`, `prepared_count_summary`, `coverage_threshold_prepared` | ok | ok | service coverage `0.211814 s`; event hotspot `0.350607 s`; facility coverage `0.000670 s` |
| E | `road_hazard_native_summary_gate`, `segment_polygon_hitcount_native_experimental`, `segment_polygon_anyhit_rows_native_bounded_gate` | ok | ok | road hazard native `1.876493 s`; segment gates passed strict/parity checks |
| F rerun | `graph_visibility_edges_gate` | ok | ok | visibility any-hit `1.353729 s`; native graph-ray BFS `0.775787 s`; native graph-ray triangle-count `0.952663 s` |
| G manual | Hausdorff, ANN, Barnes-Hut prepared decision profilers | ok | not run through Goal762 | small-scale RTX artifacts captured for later intake |
| H rerun | `polygon_pair_overlap_optix_native_assisted_phase_gate`, `polygon_set_jaccard_optix_native_assisted_phase_gate` | ok | ok | pair candidate discovery `2.899272 s`; Jaccard candidate discovery `2.908417 s` |

## Important Boundaries

- The DB artifacts show native OptiX phase counters, but public DB claims still require same-semantics baseline review.
- Polygon overlap and Jaccard use RTX/OptiX for candidate discovery only; exact area and Jaccard refinement remain CPU/Python-owned.
- Graph visibility uses ray/triangle any-hit. BFS and triangle counting use native OptiX graph-ray candidate generation; visited/frontier bookkeeping and set-intersection remain outside RT traversal.
- The manual Hausdorff, ANN, and Barnes-Hut artifacts are evidence candidates only; they still need analyzer integration or explicit intake before promotion.
- Road hazard passed strict correctness but remains performance-held unless a later baseline review finds the native path competitive.

## Artifacts

All copied artifacts for this run are under:

`docs/reports/cloud_2026_04_25/runpod_3090_2026_04_25/`

Key rerun artifacts:

- `goal761_group_f_graph_summary_rerun.json`
- `goal762_f_graph_artifact_report_rerun.json`
- `goal762_f_graph_artifact_report_rerun.md`
- `goal889_graph_visibility_optix_gate_rtx.json`
- `goal761_group_h_polygon_summary_rerun.json`
- `goal762_h_polygon_artifact_report_rerun.json`
- `goal762_h_polygon_artifact_report_rerun.md`
- `goal877_pair_overlap_phase_rtx.json`
- `goal877_jaccard_phase_rtx.json`

## Follow-Up

1. Intake-review the RTX 3090 artifacts app by app before changing public readiness labels.
2. Keep `polygon_set_jaccard` at `chunk-copies=20` until the larger-chunk candidate loss is root-caused.
3. Add analyzer coverage for the manual Group G prepared decision artifacts before using them in any release matrix.
4. Run external/AI review on this report and the generated artifacts before release-level promotion.
