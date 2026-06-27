# Goal1163 Pre-Cloud RTX Readiness Supersession

Date: 2026-04-30

Valid: `true`

Goal1163 supersedes the stale Goal1125 pre-cloud prioritization state. It does not run cloud, does not authorize public RTX speedup wording, and does not mark release readiness. It only records that the local pre-cloud remedies for the six previously unresolved app rows are now complete enough for a consolidated pod batch.

## Summary

- Tracked apps: 6
- Local pre-cloud complete for next pod batch: 6
- Public wording authorized by this goal: 0

## Rows

| App | Previous Goal1125 Bucket | Current Status | RT Path | Remedy Goals | Next Pod Action | Public Wording |
|---|---|---|---|---|---|---|
| database_analytics | local_optimization_first | local_pre_cloud_complete_next_pod_batch | OptiX compact summary for DB count/sum/group summaries | Goal1155, Goal1156, Goal1157 | run real OptiX compact-summary batch with same-source artifact intake | blocked_until_real_rtx_artifact_and_review |
| graph_analytics | local_optimization_first | local_pre_cloud_complete_next_pod_batch | OptiX graph ray traversal with raw row-view summary metadata | Goal1158, Goal1159 | run graph visibility/BFS/triangle gate and verify raw-view phase metadata | blocked_until_real_rtx_artifact_and_review |
| road_hazard_screening | local_optimization_first | local_pre_cloud_complete_next_pod_batch | prepared OptiX segment/polygon compact hit-count summary | Goal1160 | run road hazard native OptiX gate and verify summary no-row-materialization metadata | blocked_until_real_rtx_artifact_and_review |
| hausdorff_distance | needs_larger_nontrivial_scale_contract | local_pre_cloud_complete_next_pod_batch | prepared OptiX fixed-radius Hausdorff threshold-decision traversal | Goal1161 | run non-analytic Hausdorff threshold contract in OptiX mode | blocked_until_real_rtx_artifact_and_review |
| polygon_pair_overlap_area_rows | local_optimization_first | local_pre_cloud_complete_next_pod_batch | OptiX LSI/PIP candidate discovery plus native exact bounded area continuation | Goal1162 | rerun v2 polygon pair gate artifact with source/schema metadata | blocked_until_real_rtx_artifact_and_review |
| polygon_set_jaccard | local_optimization_first | local_pre_cloud_complete_next_pod_batch | OptiX LSI/PIP candidate discovery plus native exact bounded Jaccard continuation | Goal1162 | rerun v2 polygon Jaccard gate artifact with source/schema metadata | blocked_until_real_rtx_artifact_and_review |

## Boundary

Goal1163 supersedes the stale Goal1125 pre-cloud prioritization state. It does not run cloud, does not authorize public RTX speedup wording, and does not mark release readiness. It only records that the local pre-cloud remedies for the six previously unresolved app rows are now complete enough for a consolidated pod batch.
