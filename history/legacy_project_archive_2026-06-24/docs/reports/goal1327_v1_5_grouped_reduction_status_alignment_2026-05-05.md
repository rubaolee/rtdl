# Goal1327: v1.5 Grouped Reduction Status Alignment

Date: 2026-05-05

## Scope

Align grouped-reduction contract metadata with the post-Goal1323 internal
readiness state.

## Changes

- Robot `prepared_pose_flags` grouped count-to-boolean contract is now
  `pod_verified_generic_non_public`.
- DB sales-risk grouped count and grouped sum contracts are now
  `pod_verified_generic_non_public`.
- Polygon exact-area grouped/sum contract is now
  `pod_verified_generic_non_public`.
- Jaccard bounded candidate scoring remains experimental-diagnostic in
  primitive shape, but its grouped score-reduction contract is now internally
  verified non-public after complete bounded collection.

## Boundary

This does not authorize public v1.5 release wording, public NVIDIA speedup
wording, whole-app claims, or new Vulkan/HIPRT/Apple RT work.

## Validation

Targeted local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1305_v1_5_grouped_reduction_contract_test \
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal1307_v1_5_db_compact_summary_generic_migration_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test

Ran 19 tests in 0.003s
OK
```
