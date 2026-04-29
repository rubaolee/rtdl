# Goal1126 Robot Normalized Public RTX Wording Review

Date: 2026-04-29

Valid: `True`

Goal1126 is a review packet only. It does not edit public wording, authorize release, start cloud resources, or by itself authorize a public speedup claim.

## Decision Under Review

`accept_explicit_normalized_baseline_review`

Current Goal1123 robot decision: `keep_public_wording_blocked_pending_same_scale_baseline`

## Evidence

| Engine | Pose count | Obstacle count | Phase seconds | Per-pose seconds |
| --- | ---: | ---: | ---: | ---: |
| RTX/OptiX | `64000000` | `4096` | `0.178698` | `0.000000002792` |
| Embree | `36000000` | `4096` | `92.249685` | `0.000002562491` |

Normalized per-pose ratio, Embree over RTX: `917.75x`.

## Checks

- same_obstacle_count: `True`
- same_result_contract: `True`
- separate_current_source_validation_ok: `True`
- current_source_intake_ok: `True`
- embree_chunked_baseline_ok: `True`
- pose_counts_differ: `True`
- wording_explicitly_normalized: `True`

## Candidate Public Wording

RTDL's prepared robot collision pose-count RTX query sub-path measured 0.178698 s for 64M poses and 917.75x per-pose throughput versus the reviewed 36M chunked Embree any-hit baseline.

Boundary: This is normalized per-pose wording, not a same-total-work wall-time claim. It covers only the prepared ray/triangle any-hit pose-count query sub-path. Full robot kinematics, scene construction, ray packing, witness-row output, continuous collision detection, Python input construction, and whole-app planning speedup are outside the wording.

## Reviewer Questions

- Is the normalized per-pose comparison acceptable despite 64M RTX versus 36M Embree total pose counts?
- Is the wording narrow enough to avoid same-total-work, whole-app, or robot-planning claims?
- If accepted, should a follow-up update only robot_collision_screening in rtdsl.rtx_public_wording_matrix() and public docs?

## Boundary

This is normalized per-pose wording, not a same-total-work wall-time claim. It covers only the prepared ray/triangle any-hit pose-count query sub-path. Full robot kinematics, scene construction, ray packing, witness-row output, continuous collision detection, Python input construction, and whole-app planning speedup are outside the wording.

