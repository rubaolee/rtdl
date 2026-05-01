# Goal1170 Clean-Source RTX Batch Manifest

Date: 2026-04-30

Valid: `true`

This manifest prepares one clean-source RTX pod batch. It does not create cloud resources and does not authorize public speedup wording.

## Rows

| Label | App | Public wording state | Validation | Output |
| --- | --- | --- | --- | --- |
| `database_compact_summary` | `database_analytics` | `public_wording_not_reviewed` | `True` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/database_compact_summary.json` |
| `graph_visibility_edges` | `graph_analytics` | `public_wording_not_reviewed` | `True` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/graph_visibility_edges.json` |
| `road_hazard_native_summary` | `road_hazard_screening` | `public_wording_not_reviewed` | `True` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/road_hazard_native_summary.json` |
| `polygon_pair_candidate_discovery` | `polygon_pair_overlap_area_rows` | `public_wording_not_reviewed` | `True` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/polygon_pair_candidate_discovery.json` |
| `polygon_jaccard_safe_chunk` | `polygon_set_jaccard` | `public_wording_not_reviewed` | `True` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/polygon_jaccard_safe_chunk.json` |
| `hausdorff_threshold_prepared` | `hausdorff_distance` | `public_wording_not_reviewed` | `True` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/hausdorff_threshold_prepared.json` |
| `ann_candidate_large_timing_replacement` | `ann_candidate_search` | `public_wording_reviewed` | `False` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/ann_candidate_65536_timing.json` |
| `robot_pose_count_large_timing_replacement` | `robot_collision_screening` | `public_wording_reviewed` | `False` | `docs/reports/goal1170_clean_source_rtx_claim_grade_batch/robot_pose_count_262144_timing.json` |

## Source Policy

Runner refuses claim-grade collection if git status is dirty. Dirty or pod-patched runs are engineering evidence only and must not be used for public wording.

## Boundary

This manifest prepares one clean-source RTX pod batch. It does not create cloud resources and does not authorize public speedup wording.
