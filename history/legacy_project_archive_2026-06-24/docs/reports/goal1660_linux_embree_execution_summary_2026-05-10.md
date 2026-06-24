# Goal1660 Linux Embree Execution Summary - 2026-05-10

## Verdict

Current-main Embree product-surface validation is green on local Linux: 13 planned Embree rows ran successfully with 0 failures.

This is not a v1.0-vs-v1.6.11 cross-version comparison. The run validates the current main checkout after the backend-selector fixes, using the current application profiler surfaces with `--backend embree`.

## Run Scope

- Host: `lx1`
- Platform: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Repo checkout: `/home/lestat/work/rtdl_codex_local_check`
- Commit: `7ffd565d0b32e4cd815cc22f9df22e7e035444ef`
- Engine scope: Embree only
- Embree version: not captured by this runner; the raw JSON `embree_version` field is empty
- Result artifact: `docs/reports/goal1660_linux_embree_execution_2026-05-10.json`
- Generated at: `2026-05-10T09:30:27Z`
- Rows: 13 total, 13 ok, 0 failed

## Passing Rows

| App | Status | Elapsed seconds | Artifact status |
| --- | --- | ---: | --- |
| database_analytics | ok | 2.160 | not reported |
| service_coverage_gaps | ok | 0.695 | embree |
| event_hotspot_screening | ok | 0.859 | embree |
| facility_knn_assignment | ok | 3.206 | embree |
| road_hazard_screening | ok | 2.234 | pass |
| segment_polygon_hitcount | ok | 0.251 | pass |
| segment_polygon_anyhit_rows | ok | 0.253 | pass |
| polygon_pair_overlap_area_rows | ok | 20.260 | pass |
| polygon_set_jaccard | ok | 568.634 | diagnostic_chunk_config |
| hausdorff_distance | ok | 5.641 | embree |
| ann_candidate_search | ok | 2.790 | embree |
| robot_collision_screening | ok | 8.343 | embree |
| barnes_hut_force_app | ok | 9.282 | embree |

## Notes

The largest local Embree cost is `polygon_set_jaccard` at 568.634 seconds. That row should not be casually rerun unless the evidence needs to be refreshed.

The earlier pod evidence remains the source for NVIDIA/OptiX rows. This Linux artifact only closes the local Embree current-main execution question.
