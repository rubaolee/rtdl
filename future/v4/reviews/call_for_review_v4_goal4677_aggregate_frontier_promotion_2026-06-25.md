# Call For Review: V4 Goal4677 Aggregate-Frontier Promotion

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4677_promote_aggregate_frontier_measured_route_no_release`
- `accept_with_required_amendments`
- `reject_goal4677_promotion_reopen_goal4676`

## Files To Review

- `future/v4/v4_goal4677_aggregate_frontier_promotion_2026-06-25.md`
- `future/v4/evidence/v4_goal4677_aggregate_frontier_promotion_2026-06-25.json`
- `future/v4/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.md`
- `future/v4/evidence/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.json`
- `src/rtdsl/v4_goal4677_aggregate_frontier_promotion.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_aggregate_frontier.py`
- `tests/v4_goal4677_aggregate_frontier_promotion_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_frontdoor_test.py`

## Review Questions

1. Does Goal4676 evidence justify promoting
   `v4_aggregate_frontier_device_columns_2d_prepared_runner` from candidate to
   measured V4 route?
2. Are the measured partner scopes honest: `rtdl_native` frontier-only and
   explicit `cupy` downstream continuation, with `torch` and `numba` still
   unmeasured/deferred?
3. Does the catalog correctly prevent partner migration from being treated as a
   broad V4 speed win?
4. Does the V3.0.2 parity caveat block any accidental V4-over-V3 claim?
5. Are the frontdoor/scope/test updates consistent: 9 measured surfaces, 1
   candidate surface, release still unauthorized?
6. Should any public/user-facing docs be amended before this promotion is kept?
7. Does this review preserve all non-authorization boundaries?

## Expected Non-Authorization

Even if accepted, this review must not authorize V4 release, public speedup
wording, whole-app high-performance wording, broad V4-over-V2/V3 claims,
V4-over-V3 speed claims for aggregate-frontier, RT-core speedup wording,
true-zero-copy wording, Tier-3 callback/PTX support, raw OptiX callbacks, C ABI,
embedding, non-Python hosts, automatic partner selection, or app-identity native
kernels.
