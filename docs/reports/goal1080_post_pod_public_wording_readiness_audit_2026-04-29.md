# Goal1080 Post-Pod Public Wording Readiness Audit

Date: 2026-04-29

Valid: `true`

Goal1080 audits post-pod wording readiness only. It does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Summary

- rows audited: `3`
- decision counts: `{'needs_same_scale_baseline_review': 2, 'needs_reviewed_20m_validation_and_baseline': 1}`
- public speedup claims authorized: `0`

## Rows

| App | Path | RTX phase | Decision | Reason |
| --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `0.111038` | `needs_same_scale_baseline_review` | Goal1079 cleared validation and the 100 ms RTX timing floor, but the available same-semantics baseline is at 20k copies while the new RTX timing row is at 2.5M copies. Do not compute or publish a speedup ratio from mismatched scales. |
| `robot_collision_screening` | `prepared_pose_flags` | `0.100071` | `needs_same_scale_baseline_review` | Goal1079 cleared validation and barely cleared the 100 ms RTX timing floor, but the available Embree baseline is at 200k poses / 1,024 obstacles while the new RTX timing row is at 36M poses / 4,096 obstacles. Do not compute or publish a speedup ratio from mismatched scales. |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `0.221393` | `needs_reviewed_20m_validation_and_baseline` | The reviewed Goal1076 1M timing row failed the 100 ms floor. The Goal1079 20M probe passed the floor, but it is timing-only engineering evidence and needs a matching reviewed validation/intake contract plus same-scale baseline before public wording review. |

## Boundary

Goal1080 audits post-pod wording readiness only. It does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

