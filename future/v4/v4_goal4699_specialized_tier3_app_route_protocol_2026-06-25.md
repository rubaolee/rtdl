# V4 Goal4699: Specialized Tier-3 App-Route Validation Protocol

Date: 2026-06-25
Status: `goal4699_specialized_tier3_app_route_validation_protocol_frozen_not_run`

## Result

Goal4699 froze the app-route validation protocol for the specialized Tier-3
callback candidate.

Selected route:

- route: `ray_triangle_any_hit_weighted_sum_scalar_reduce`
- surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- callback contract: Goal4697
  `module_specialized_direct_device_callback / pure scalar Numba C-ABI callback`

This route is chosen because weighted sum is a generic scalar-reduce
hit-event shape with an existing measured Tier-2 fused denominator. The
callback route must compete against the built-in fused route, not only against
a slower host/materialized route.

Evidence:

- `future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.json`
- `future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.md`

## Frozen Denominators

- correctness denominator:
  existing Tier-2 built-in weighted-sum device-output route, exact `uint64`
  output
- primary performance denominator:
  existing Tier-2 built-in weighted-sum fused route on the same fixture
- context denominator:
  legacy host-scalar/materialized weighted-sum route from Goal4633

## Frozen Bars

- ray counts: `32768`, `131072`, `262144`
- warmup: `3`
- repeat: `10`
- parity: exact equality to Tier-2 built-in weighted-hit-sum for every tested
  size
- pass: `tier3_callback_route_median / tier2_builtin_route_median <= 1.20x`
  at every size
- hard kill: any size `> 1.50x` versus Tier-2 built-in route
- context check: callback route must still be at least `1.20x` faster than the
  legacy host-scalar/materialized route

## Required Telemetry

Goal4700 must record:

- `callback_contract_status`
- `compile_cache_key`
- `compile_stage`
- `tier3_callback_route_median_s`
- `tier2_builtin_route_median_s`
- `legacy_host_scalar_route_median_s`
- `callback_over_tier2_ratio`
- `legacy_host_over_callback_ratio`
- `parity_passed`
- `tier3_public_support_authorized_false`

## Verification

Local verification passed:

- `py scripts/v4_goal4699_specialized_tier3_app_route_protocol.py --json-out future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.json --md-out future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.md`
- `py -m unittest tests.v4_goal4699_specialized_tier3_app_route_protocol_test tests.v4_goal4698_specialized_tier3_compile_cache_test tests.v4_goal4697_specialized_tier3_api_contract_test`
  - result: `11 tests OK`
- `py -m py_compile src/rtdsl/v4_goal4699_specialized_tier3_app_route_protocol.py scripts/v4_goal4699_specialized_tier3_app_route_protocol.py src/rtdsl/v4.py`

## Boundary

Not authorized:

- public Tier-3 support
- arbitrary callback support
- raw OptiX callback support
- app-level speedup claims
- V4 release or tag claims

Goal4700 may use the POD to implement and run the frozen app-route validation.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The protocol uses an existing measured Tier-2 fused denominator, so a
   callback route cannot win by comparing only against a slow baseline.

2. If yes, what action made it stupid?
   The bad action would have been to validate against only the legacy
   host-scalar route and claim that as Tier-3 performance. This protocol
   forbids that.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. The callback route must pass both exact parity and a strict overhead
   ratio versus the built-in fused route.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4700 should implement the route and run the frozen POD protocol.
