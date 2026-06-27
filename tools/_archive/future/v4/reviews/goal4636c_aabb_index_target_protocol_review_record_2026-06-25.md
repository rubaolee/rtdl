# V4 Goal4636C AABB Index Target Protocol Review Record

Status: `review_recorded_with_required_amendments_applied_pending_pod_gate`

## Reviewed Target

- Protocol: `future/v4/v4_goal4636c_aabb_index_operator_target_protocol_2026-06-25.md`
- Target module: `src/rtdsl/v4_goal4636_aabb_index_target.py`
- Runner: `scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`
- Test: `tests/v4_goal4636_aabb_index_target_test.py`

## External Review State

- Claude: `approve_with_required_amendments`
- Claude raw output:
  `future/v4/reviews/claude_v4_goal4636c_aabb_index_target_protocol_review_2026-06-25.raw.md`
- Antigravity: empty output; recorded as review debt, not an engineering blocker.

## Required Amendments

1. The existing runner would fail before timing because Embree and OptiX report
   different members of the same generic prepared-AABB contract family.
2. The original asymmetric repeat setting (`embree=240,optix=3200`) made a
   nominal 10x total-time floor imply a much larger per-query ratio, so the
   gate was not numerically honest.
3. The protocol needed to explicitly acknowledge that the large gate skips the
   O(n*m) CPU reference and relies on cross-backend count-signature parity on
   the same fixture.

## Applied Corrections

- The runner now accepts the base contract
  `generic_prepared_aabb_index_query_2d`, the Embree count contract
  `generic_prepared_aabb_index_query_2d_count`, and the qualified OptiX
  prepared-count contract
  `generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count` as one
  `generic_prepared_aabb_index_query_2d` family.
- A first POD attempt confirmed the missing Embree `_count` contract before any
  performance verdict was made; the accepted family was expanded rather than
  weakening the primitive/count-signature requirements.
- The gate repeat overrides are now symmetric: `embree=240,optix=240`.
- The target and protocol now record the correctness oracle as
  `cross_backend_count_match_same_fixture` and explicitly acknowledge the large
  gate skips the CPU oracle.

## Local Verification

```text
py -m unittest tests.v4_goal4636_aabb_index_target_test
Ran 6 tests in 0.001s
OK
```

## Non-Authorization

This record does not authorize V4 release, release-candidate wording, broad
speedup claims, whole-app speedup claims, LibRTS paper reproduction claims,
authors-code comparison claims, public true-zero-copy claims, Tier-3 callback
support, raw OptiX callback support, CuPy performance claims, C ABI, embedding,
non-Python host claims, or app-specific native kernels.
