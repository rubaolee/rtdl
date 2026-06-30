# Goal 1048 RTX A5000 Claim-Grade Rerun

Date: 2026-04-27

## Scope

This report records a consolidated RTX cloud rerun for the v1.0 app-readiness line after Goal 1043 removed source-less and skip-validation ambiguity from the active claim-grade path.

This is evidence collection only. It does not authorize public speedup claims or release wording by itself. Claims still require review of the copied JSON artifacts, phase boundaries, comparable baselines, and 2+ AI consensus.

## Host And Source

- Cloud host: Runpod Linux container `8b8db62e9958`
- GPU: NVIDIA RTX A5000
- Driver: 580.126.09
- CUDA runtime reported by `nvidia-smi`: 13.0
- CUDA compiler used: `/usr/local/cuda-12.4/bin/nvcc`, CUDA 12.4.131
- OptiX headers used: `NVIDIA/optix-dev` tag `v9.0.0`, `OPTIX_VERSION 90000`
- RTDL source commit recorded in artifacts: `0c79b64d1b71383080f2e8572612488796d1c16c`
- Local working branch: `codex/rtx-cloud-run-2026-04-22`

## Setup Notes

The first OptiX header attempt used `optix-dev` tag `v9.1.0`, which built but failed runtime focused tests with `OptiX error: Unsupported ABI version`. The pod was corrected by checking out `optix-dev` tag `v9.0.0`, after which the OptiX backend built and focused tests passed.

The graph gate initially failed because the pod lacked `libgeos_c`, causing native oracle build failure for BFS and triangle-count validation. Installing `libgeos-dev` and `pkg-config`, then rebuilding `librtdl_optix.so`, resolved the issue. The rerun of Group F passed.

## Bootstrap Result

- Artifact: `docs/reports/goal763_rtx_cloud_bootstrap_check.json`
- Result: `status: ok`
- Build: `make build-optix` passed
- Focused native OptiX tests: 34 tests passed

## Group Results

| Group | Apps / Paths | Entries | Status | Notes |
| --- | --- | ---: | --- | --- |
| A | `robot_collision_screening / prepared_pose_flags` | 1 | OK | Phase-separated OptiX run copied back. Manifest command uses skip-validation, so this remains diagnostic until reviewed under the baseline contract. |
| B | `outlier_detection`, `dbscan_clustering` fixed-radius scalar summaries | 2 | OK | Validation enabled. Oracle parity passed for threshold/core scalar summaries. |
| C | `database_analytics` sales-risk and regional-dashboard compact summaries | 2 | OK | Strict compact-summary DB sessions passed and exported native traversal/filter/output-pack phases. |
| D | `service_coverage_gaps`, `event_hotspot_screening`, `facility_knn_assignment` prepared spatial summaries | 3 | OK | Service and hotspot summaries passed. Facility coverage ran the manifest path with skip-validation and needs review before claim use. |
| E | `road_hazard_screening`, `segment_polygon_hitcount`, `segment_polygon_anyhit_rows` | 3 | OK | Deferred/experimental segment-polygon paths passed on RTX A5000. |
| F | `graph_analytics` visibility/BFS/triangle native graph-ray gate | 1 | OK after GEOS fix | Initial fail was missing GEOS. Final strict rerun passed. |
| G | `hausdorff_distance`, `ann_candidate_search`, `barnes_hut_force_app` prepared decision paths | 3 | OK | Bounded RT sub-paths passed; not full algorithm speedup claims. |
| H | `polygon_pair_overlap_area_rows`, `polygon_set_jaccard` native-assisted polygon phases | 2 | OK | Native-assisted candidate-discovery plus exact-continuation gates passed. |

## Copied Artifacts

- `docs/reports/goal761_group_a_robot_summary.json`
- `docs/reports/goal761_group_b_fixed_radius_summary.json`
- `docs/reports/goal761_group_c_database_summary.json`
- `docs/reports/goal761_group_d_spatial_summary.json`
- `docs/reports/goal761_group_e_segment_polygon_summary.json`
- `docs/reports/goal761_group_f_graph_summary.json`
- `docs/reports/goal761_group_g_prepared_decision_summary.json`
- `docs/reports/goal761_group_h_polygon_summary.json`
- `docs/reports/goal759_robot_pose_flags_phase_rtx.json`
- `docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json`
- `docs/reports/goal759_db_sales_risk_rtx.json`
- `docs/reports/goal759_db_regional_dashboard_rtx.json`
- `docs/reports/goal811_service_coverage_rtx.json`
- `docs/reports/goal811_event_hotspot_rtx.json`
- `docs/reports/goal887_facility_service_coverage_rtx.json`
- `docs/reports/goal889_graph_visibility_optix_gate_rtx.json`
- `docs/reports/goal887_hausdorff_threshold_rtx.json`
- `docs/reports/goal887_ann_candidate_coverage_rtx.json`
- `docs/reports/goal887_barnes_hut_node_coverage_rtx.json`
- `docs/reports/goal933_road_hazard_prepared_summary_rtx.json`
- `docs/reports/goal933_segment_polygon_hitcount_prepared_rtx.json`
- `docs/reports/goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json`
- `docs/reports/goal877_pair_overlap_phase_rtx.json`
- `docs/reports/goal877_jaccard_phase_rtx.json`

## Claim Boundary

The strongest supported statement from this run is that every active Group A-H manifest path executed on real RTX A5000 hardware after the OptiX backend was built from the recorded source commit, with the final group summaries reporting `status: ok`.

This run does not by itself prove whole-app speedup. Several paths are explicitly bounded sub-paths, deferred paths, native-assisted phase gates, or skip-validation diagnostic runs. Public claims must preserve those distinctions.

## Next Actions

1. Run a mechanical audit over the copied JSON artifacts to verify status, source commit, hardware metadata, and forbidden overclaim wording.
2. Ask external AI review to inspect the Goal 1048 evidence and decide which paths are claim-grade, diagnostic-only, or still blocked.
3. Write a two-AI consensus report before marking Goal 1048 closed.
