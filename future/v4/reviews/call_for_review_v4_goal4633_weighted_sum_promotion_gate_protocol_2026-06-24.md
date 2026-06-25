# Call For Review: V4 Goal4633 Weighted-Sum Promotion Gate Protocol

Date: 2026-06-24

Requested verdict labels:

- `approve_goal4633_protocol_run_gate`
- `approve_with_required_amendments`
- `reject_goal4633_protocol_wrong_next_goal`
- `reject_goal4633_protocol_metric_or_scope_risk`

Primary file for review:

- `future/v4/v4_goal4633_weighted_sum_promotion_gate_protocol_2026-06-24.md`

Context:

- Antigravity closed the 9 Goal4626-4632 scorecard review-debt items.
- The remaining V4 blockers are engineering/release blockers, not procedural
  review debt.
- Current V4 label remains `development_state_performance_preview_not_release`.
- Weighted-sum is the highest-leverage concrete blocker because
  `triangle_counting` coverage remains candidate-bound through
  `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`.

Please review:

1. Is weighted-sum promotion the correct next engineering goal after Goal4632,
   given the remaining debt file?
2. Is the same-contract comparison fair and bounded?
3. Are the four shapes, 5 warmups, and 30 repeats sufficient for a promotion
   gate?
4. Are the thresholds appropriate: every shape `>=1.20x`, geomean `>=1.50x`,
   with correctness parity at every shape?
5. Does the protocol prevent post-hoc metric gaming?
6. Does it preserve the boundaries: no V4 release, no whole-app claim, no CuPy
   claim, no Tier-3, no true-zero-copy wording?
7. If you reject this goal, what exact engineering goal should replace it?

Please include explicit authorization or non-authorization for running the POD
gate. Do not authorize V4 release.
