# Call For Review: V4 Goal4636C AABB Index Target Protocol

Please critically review the proposed third Goal4636 candidate.

## Requested Verdict Labels

- `approve_goal4636c_aabb_index_target_and_pod_gate`
- `approve_with_required_amendments`
- `reject_target_as_not_generic_or_not_v4`
- `reject_gate_as_too_weak_or_metric_gaming`

## Files To Review

- `future/v4/v4_goal4636c_aabb_index_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4636_aabb_index_target.py`
- `tests/v4_goal4636_aabb_index_target_test.py`
- `scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`

## Review Questions

1. Is `aabb_index_query_2d_all_ops_count` a valid generic V4 operator target, or
   is it too tied to the LibRTS benchmark identity?
2. Is the `rtdl_native_prepared_runner` scope honest for this gate?
3. Are the large all-ops fixture and the `>=10x` query median/total floors
   material enough, or is this still metric gaming?
4. Does the protocol correctly avoid authors-code, paper reproduction, whole-app,
   and public speedup wording?
5. Is it acceptable that a passing POD gate would require a separate front-door
   catalog goal before measured public catalog promotion?
6. Does this target properly continue Goal4636 after threshold-summary and
   grouped-any-hit both failed promotion?

## Non-Authorization

This review must not authorize V4 release, release-candidate wording, broad
speedup claims, whole-app speedup claims, LibRTS paper reproduction claims,
authors-code comparison claims, public true-zero-copy claims, Tier-3 callback
support, raw OptiX callback support, CuPy performance claims, C ABI, embedding,
non-Python host claims, or app-specific native kernels.
