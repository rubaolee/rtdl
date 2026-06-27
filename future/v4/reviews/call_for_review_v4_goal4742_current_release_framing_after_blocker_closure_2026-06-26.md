# Call For Review: V4 Goal4742 Current Release Framing After Blocker Closure

Date: 2026-06-26

Reviewer requested: Claude and Antigravity when available.

Status: `external_review_requested_debt_allowed`

## Files To Review

- Report:
  `future/v4/v4_goal4742_current_release_framing_after_blocker_closure_2026-06-26.md`
- Evidence:
  `future/v4/evidence/v4_goal4742_current_release_framing_after_blocker_closure_2026-06-26.json`
- Matrix delta:
  `future/v4/v4_goal4739_post_raydb_repair_app_matrix_delta_2026-06-26.md`
- Robot boundary:
  `future/v4/v4_goal4740_robot_collision_boundary_recheck_2026-06-26.md`
- Spatial decision:
  `future/v4/v4_goal4741_spatial_rayjoin_route_reopen_decision_2026-06-26.md`
- Custom predicate chain:
  `future/v4/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md`
  `future/v4/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.md`
  `future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`
  `future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`

## Questions

1. Is the recommended bounded release-candidate label honest?
2. Is it correct to say V4 has three historical benchmark-app candidate rows,
   not all 10 apps faster?
3. Is custom predicate early-exit correctly counted as V4 eDSL/operator-
   pushdown value but not as a legacy 10-app win?
4. Is the blocked wording complete enough to prevent overclaiming?
5. Are the next goals (docs, gates, external review, final decision) the right
   path?

## Requested Verdict Labels

- `accept_goal4742_bounded_release_framing`
- `accept_with_required_amendments`
- `reject_release_framing_overclaim_or_underclaim`

## Non-Authorization

This review must not authorize final V4 tag by itself. It must not authorize
all-benchmark speedup claims, broad V4-over-V2.14 claims, arbitrary callbacks,
raw OptiX callbacks, true-zero-copy wording, non-Python embedding/C ABI, or
app-specific native kernels.
