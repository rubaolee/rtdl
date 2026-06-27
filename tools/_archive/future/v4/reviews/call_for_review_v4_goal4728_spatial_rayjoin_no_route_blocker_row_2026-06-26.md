# Call For Review: V4 Goal4728 Spatial RayJoin No-Route Blocker Row

Please review:

- `future/v4/v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.md`
- `future/v4/evidence/v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.json`
- `tests/v4_goal4728_spatial_rayjoin_no_route_blocker_row_test.py`

Context:

- `future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/summary.json`
- `future/v4/v4_goal4681_shape_pair_relation_pod_benchmark_2026-06-25.md`
- `src/rtdsl/v4_goal4681_shape_pair_relation_result.py`
- `future/v4/evidence/v4_goal4724_remaining_5_app_route_gap_audit_2026-06-26.json`

## Questions For Reviewer

1. Is it correct to close spatial_rayjoin as a no-current-V4-route blocker?
2. Does the row correctly treat the shape-pair measurement as a focused subprobe
   that failed speed-credit bars, not a full app result?
3. Does it correctly block RayJoin paper reproduction wording and hidden V2/V3
   fallback?
4. Is the reopen condition strict enough: full V4 relation-topology app route,
   frozen V2.14 denominator, correctness parity, and material bars before POD?

## Requested Verdict Labels

- `accept_goal4728_spatial_rayjoin_no_route_blocker_row`
- `accept_with_required_amendments`
- `reject_goal4728_row_overclaims_or_should_reopen`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims,
spatial-RayJoin speedup wording, RayJoin paper reproduction claims, whole-app
high-performance claims, all-benchmark speedups, POD spend, arbitrary callback
support, raw OptiX callbacks, app-specific native kernels, or hidden V2/V3
fallbacks.

