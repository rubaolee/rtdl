# Goal1123 Public RTX Wording Review After Goal1142

Date: 2026-04-29

Goal1123 is a public-wording review packet after Goal1142 same-source RTX evidence. It proposes narrow wording for two prepared RTX query sub-paths, keeps robot speedup wording blocked, and does not itself edit public docs or authorize release.

## Summary

- candidate reviewed rows proposed: `2`
- blocked rows retained: `1`
- public speedup claim authorized by this packet: `false`

## Decisions

| App | Path | Decision | RTX median query | Ratio |
| --- | --- | --- | ---: | ---: |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `candidate_public_wording_reviewed` | `0.111619` | `80.60x` |
| `robot_collision_screening` | `prepared_pose_flags` | `keep_public_wording_blocked_pending_same_scale_baseline` | `0.178471` | `n/a` |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `candidate_public_wording_reviewed` | `0.222256` | `240.56x` |

## Candidate Public Wording

### facility_knn_assignment / coverage_threshold_prepared_recentered

RTDL's prepared facility coverage-threshold RTX query sub-path measured 0.111619 s and 80.60x versus the reviewed same-contract CPU oracle baseline.

Boundary: Only the prepared recentered coverage-threshold query decision is covered; ranked nearest-facility assignment, KNN fallback output, facility-location optimization, Python-side setup, and whole-app speedup are outside this wording.

### robot_collision_screening / prepared_pose_flags

No public RTX speedup wording is authorized for robot_collision_screening yet.

Boundary: The prepared ray/triangle any-hit pose-flag path is real RT-core work and now has timing-floor evidence, but public ratio wording remains blocked until a same-scale or explicitly normalized baseline review is accepted.

### barnes_hut_force_app / node_coverage_prepared_rich

RTDL's prepared Barnes-Hut node-coverage RTX query sub-path measured 0.222256 s and 240.56x versus the reviewed same-contract Embree node-coverage baseline.

Boundary: Only the prepared depth-8 node-coverage threshold traversal is covered; Barnes-Hut opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup are outside this wording.

## Reviewer Questions

- Are the facility and Barnes-Hut wording lines narrow enough to avoid whole-app or default-mode claims?
- Is robot correctly kept blocked despite timing-floor evidence because the public ratio still needs same-scale or accepted normalized baseline review?
- Are the evidence sources sufficient to update `rtdsl.rtx_public_wording_matrix()` and user-facing docs in a follow-up goal?

