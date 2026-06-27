# Goal1154 Robot Goal1126 Follow-Up Sync

Date: 2026-04-30

## Scope

This goal applies the already accepted Goal1126 3-AI decision to the current
release-facing public wording surface and local gates.

Goal1126 authorizes only this bounded wording:

- `robot_collision_screening / prepared_pose_flags`
- RTX query phase `0.178471` s for 64M poses
- `918.91x normalized per-pose` versus the reviewed 36M chunked Embree any-hit
  baseline
- prepared ray/triangle pose-count query sub-path only

It does not authorize same-total-work wall-time wording, full robot kinematics,
scene construction, ray packing, witness-row output, continuous collision
detection, Python input construction, or whole-app robot-planning speedup.

## Current-State Changes

- Updated `rtdsl.rtx_public_wording_matrix()` so `robot_collision_screening`
  is `public_wording_reviewed` with Goal1126 evidence.
- Updated public docs and generated status pages from `9 reviewed / 1 blocked`
  to `10 reviewed / 0 blocked`.
- Updated stale local gates so Goal1062/Goal1065 no longer ask for a robot-only
  blocked rerun after the Goal1126 promotion.
- Updated release-facing docs to say robot normalized per-pose wording is
  reviewed, while preserving the same-total-work and whole-app exclusions.
- Left historical Goal1123/1146/1152 reports intact. They are historical
  records and are superseded by this Goal1154 follow-up plus Goal1126.

## Verification

- Focused public wording and gate suite: `70 tests OK`.
- Historical candidate/intake compatibility suite: `23 tests OK`.
- Goal1020 public docs RTX boundary audit: `valid: true`.
- Goal1024 final public surface audit: `valid: true`.
- Goal515 public command truth audit: `valid: true`, `296` commands,
  `15` public docs.

## Boundary

This goal does not create new RTX evidence and does not broaden any public
claim. It only applies the existing Goal1126 3-AI accepted robot wording to the
current live matrix, docs, and gates.
