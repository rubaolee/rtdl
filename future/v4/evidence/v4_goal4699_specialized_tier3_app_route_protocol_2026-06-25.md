# V4 Goal4699 Specialized Tier-3 App-Route Validation Protocol

Status: frozen protocol, not run

- validation: `passed`
- selected route: `ray_triangle_any_hit_weighted_sum_scalar_reduce`
- selected surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- next goal: `Goal4700 specialized Tier-3 app-route POD implementation`

## Denominators

- correctness: existing Tier-2 built-in weighted-sum device-output route, exact uint64 output
- primary performance: existing Tier-2 built-in weighted-sum fused route on the same fixture
- context: legacy host-scalar/materialized weighted-sum route from Goal4633

## Frozen Parameters

- ray counts: `(32768, 131072, 262144)`
- warmup: `3`
- repeat: `10`
- callback/Tier-2 pass ratio max: `1.2x`
- callback/Tier-2 hard kill ratio: `>1.5x`
- callback/context speedup min: `1.2x`

## Required Telemetry

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

## Boundary

This protocol does not authorize public Tier-3 support, app-level speed claims, or V4 release wording. It only authorizes Goal4700 to run the frozen POD app-route validation.
