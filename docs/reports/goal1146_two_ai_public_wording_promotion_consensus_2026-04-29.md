# Goal1146 Two-AI Public Wording Promotion Consensus

Date: 2026-04-29

Status: `ACCEPT_FACILITY_AND_BARNES_PROMOTE_ROBOT_BLOCKED`

Participants:

- Codex
- Gemini manual external review

## Consensus Decision

Promote two previously held rows to reviewed public RTX sub-path wording:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`
- `barnes_hut_force_app / node_coverage_prepared_rich`

Keep one row blocked:

- `robot_collision_screening / prepared_pose_flags`

## Approved Public Wording

### facility_knn_assignment / coverage_threshold_prepared_recentered

RTDL's prepared facility coverage-threshold RTX query sub-path measured
`0.111619` s and `80.60x` versus the reviewed same-contract CPU oracle
baseline.

Boundary: only the prepared recentered coverage-threshold query decision is
covered. Ranked nearest-facility assignment, KNN fallback output,
facility-location optimization, Python-side setup, and whole-app speedup remain
outside this wording.

### barnes_hut_force_app / node_coverage_prepared_rich

RTDL's prepared Barnes-Hut node-coverage RTX query sub-path measured `0.222256`
s and `240.56x` versus the reviewed same-contract Embree node-coverage
baseline.

Boundary: only the prepared depth-8 node-coverage threshold traversal is
covered. Barnes-Hut opening-rule evaluation, candidate-row output, force-vector
reduction, N-body simulation, and whole-app speedup remain outside this wording.

## Robot Boundary

`robot_collision_screening / prepared_pose_flags` remains blocked for public
speedup wording. Goal1142 gives valid 64M RTX timing evidence, but the public
ratio still needs same-total-work or explicitly normalized baseline review.

## Evidence

- Promotion packet:
  `docs/reports/goal1146_public_wording_promotion_packet_2026-04-29.md`
- Gemini review:
  `docs/reports/goal1146_gemini_manual_public_wording_promotion_review_2026-04-29.md`
- Current-source intake:
  `docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json`

## Boundary

This consensus authorizes only the two bounded public sub-path wording lines
above. It does not authorize robot public speedup wording, whole-app speedup,
default-mode speedup, Python-postprocess speedup, broad RT-core acceleration
claims, or release tagging.
