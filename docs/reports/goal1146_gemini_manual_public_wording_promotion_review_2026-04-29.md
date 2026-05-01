# Goal1146 Gemini Manual Public Wording Promotion Review

Date: 2026-04-29

Reviewer: Gemini, manually forwarded by the user

## Verdict

`ACCEPT`

## Reasons

- Promotion of `facility_knn_assignment` to `public_wording_reviewed` is
  justified by Goal1142 evidence: `0.111619` s and `80.60x` versus the
  same-contract CPU oracle. The wording is bounded to the prepared query
  sub-path.
- Promotion of `barnes_hut_force_app` to `public_wording_reviewed` is justified
  by Goal1142 evidence: `0.222256` s and `240.56x` versus the same-contract
  Embree baseline. The wording is bounded to the depth-8 node-coverage
  threshold traversal.
- `robot_collision_screening` should remain `public_wording_blocked`. Its 64M
  RTX timing floor is cleared, but a same-total-work or explicitly normalized
  public baseline is not yet accepted.
- The proposed wording and boundaries exclude whole-app, default-mode,
  Python-postprocess, and broad RT-core acceleration claims.

## Required Fixes

None.

## Boundary

This review accepts only the narrow Goal1146 promotion: facility and Barnes-Hut
may be promoted to reviewed public RTX sub-path wording, while robot remains
blocked. It does not authorize whole-app speedup or release tagging.
