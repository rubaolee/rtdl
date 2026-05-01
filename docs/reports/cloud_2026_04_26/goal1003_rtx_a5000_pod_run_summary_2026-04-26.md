# Goal1003 RTX A5000 Pod Run Summary

Date: 2026-04-26

## Host

- Pod: `root@69.30.85.167 -p 22005`
- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- VRAM: 24564 MiB
- CUDA toolkit used for build: `/usr/local/cuda-12.4`
- OptiX headers: `/workspace/vendor/optix-dev-9.0.0`
- Commit: `914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`
- Branch: `codex/rtx-cloud-run-2026-04-22`

## Bootstrap

- OptiX backend build: pass
- Build time: 11.55 s
- Focused native OptiX tests: 34/34 pass
- Bootstrap report: `goal1003_rtx_a5000_artifacts_v2/docs/reports/goal763_rtx_cloud_bootstrap_check.json`

## Grouped App Gate Result

- Manifest entries executed: 17
- Final failed entries: 0
- Final artifact report verdict: `ok`
- Final report: `goal1003_rtx_a5000_artifacts_v2/docs/reports/goal762_rtx_cloud_artifact_report.md`
- Final bundle: `goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz`

## Important Incident

The first graph group run failed because the pod image did not include GEOS development files, so the native oracle could not link `-lgeos_c` for graph BFS and triangle-count validation. The failed first bundle is preserved as `goal1003_rtx_a5000_artifacts_with_report_2026-04-26.tgz`.

Remediation performed on the pod:

```bash
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libgeos-dev pkg-config
```

After installing those packages, the graph group was rerun and passed. The final v2 bundle contains the corrected graph artifact.

## Final App Table

| App | Path | Runner | Artifact | Warm query median (s) |
|---|---|---:|---:|---:|
| robot_collision_screening | prepared_pose_flags | ok | ok | 0.000493 |
| outlier_detection | prepared_fixed_radius_density_summary | ok | ok | 0.005828 |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | ok | 0.003751 |
| database_analytics | prepared_db_session_sales_risk | ok | ok | 0.103378 |
| database_analytics | prepared_db_session_regional_dashboard | ok | ok | 0.143968 |
| service_coverage_gaps | prepared_gap_summary | ok | ok | 0.136545 |
| event_hotspot_screening | prepared_count_summary | ok | ok | 0.253894 |
| facility_knn_assignment | coverage_threshold_prepared | ok | ok | 0.003131 |
| road_hazard_screening | road_hazard_native_summary_gate | ok | ok | 0.172010 |
| segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | ok | ok | 0.003996 |
| segment_polygon_anyhit_rows | segment_polygon_anyhit_rows_prepared_bounded_gate | ok | ok | 0.004701 |
| graph_analytics | graph_visibility_edges_gate | ok | ok | 2.584184 |
| hausdorff_distance | directed_threshold_prepared | ok | ok | 0.001364 |
| ann_candidate_search | candidate_threshold_prepared | ok | ok | 0.000755 |
| barnes_hut_force_app | node_coverage_prepared | ok | ok | 0.004754 |
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | ok | 10.052899 |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | ok | 4.152796 |

## Boundary

This pod run proves that the RTX A5000 can build the OptiX backend and execute all 17 current grouped RTX app gates from the validated commit. It does not by itself authorize public speedup claims. Public performance claims still require review of phase separation, correctness parity, and same-semantics baselines.
