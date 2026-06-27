# V4 Goal4710 Custom Scored App Protocol

- validation: `passed`
- status: `goal4710_ray_triangle_custom_scored_app_protocol_frozen_not_run`
- app: `ray_triangle_custom_scored_accumulation`
- next goal: `Goal4711 ray-triangle custom scored accumulation focused POD benchmark`
- POD authorized for next goal: `True`

## Callbacks

- primary: affine_score, threshold_score, minmax_score
- control: weighted_sum

## Baselines

- `v2_14_strongest_available` at `/root/rtdl_v2_14_tag`: discover strongest semantically comparable route before timing: built-in fixed reduction if exactly equivalent, materialized hit IDs plus partner/device reduction, then host scalar fallback only if no stronger route exists
- `v3_0_2_strongest_available` at `/root/rtdl_v3_0_2_tag`: discover strongest semantically comparable current route before timing under the same callback semantics
- `v4_specialized_callback_candidate` at `/root/rtdl_v4_candidate_pod`: use the Goal4700-4706 specialized direct-device callback path
- `v4_tier2_builtin_control` at `/root/rtdl_v4_candidate_pod`: weighted_sum only; context/control row, not primary app-level win evidence

## Pass Conditions

- correctness must pass for every callback x regime x scale x implementation row
- primary custom-callback geomean speedup over strongest V2.14 baseline must be >=1.50x
- primary custom-callback geomean speedup over strongest V3.0.2 baseline must be >=1.20x
- every primary callback must be >=1.10x over the strongest V3.0.2 baseline in both dense and sparse regimes
- weighted_sum is a control row only and cannot by itself support the app-level claim
- all denominators and fallback selections must be recorded before reading V4 timing

## Kill Conditions

- any correctness failure kills the goal
- if V2/V3 denominator discovery is missing or only a known-slow fallback is used without proof no stronger route exists, the result is invalid
- if the win comes only from weighted_sum or operator-only rows, the app-level claim is invalid
- if primary custom-callback geomean over V3.0.2 is <1.20x, do not continue toward high-performance wording
- if any primary callback regresses below 0.95x versus V3.0.2, stop and diagnose before more POD spend

## Boundary

Goal4710 authorizes only the next focused POD benchmark under this protocol. It does not authorize app-level speed claims, release wording, public Tier-3 support, or all-app benchmarking.
