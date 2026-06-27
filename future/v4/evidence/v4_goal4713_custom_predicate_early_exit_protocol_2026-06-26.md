# V4 Goal4713 Custom Predicate Early-Exit Protocol

- validation: `passed`
- status: `goal4713_custom_predicate_early_exit_protocol_frozen_not_run`
- app: `ray_triangle_custom_predicate_early_exit_multi_hit`
- next goal: `Goal4714 custom predicate early-exit local runner and POD smoke gate`

## Primary Regimes

| regime | candidates/ray | accept layer |
|---|---:|---:|
| `dense_early_accept_k8` | 8 | 0 |
| `dense_early_accept_k32` | 32 | 0 |
| `sparse_early_accept_k32` | 32 | 0 |

## Control Regimes

| regime | candidates/ray | purpose |
|---|---:|---|
| `dense_late_accept_k32` | 32 | control: little early-exit opportunity; should not be used as primary speed evidence. |
| `dense_reject_all_k32` | 32 | control: callback rejects every candidate; verifies no false positives and exposes worst-case predicate cost. |
| `no_hit_empty` | 0 | control: validates empty traversal and no-hit accounting. |

## Pass Conditions

- correctness must pass for every callback x regime x scale x implementation row
- primary early-accept regimes geomean V4 over V3.0.2 must be >=1.50x
- primary early-accept regimes geomean V4 over V2.14 must be >=1.50x
- every primary early-accept regime at every scale must be >=1.20x over V3.0.2
- control regimes must preserve correctness and must not regress below 0.95x geomean over V3.0.2
- wins from late-accept, reject-all, no-hit, weighted-sum, or post-hit accumulation controls cannot support the primary claim
- all denominators and fallback selections must be recorded before V4 timing

## Kill Conditions

- any correctness failure kills the goal
- missing V2/V3 denominator discovery invalidates the run
- if V4 cannot prove early termination occurred in primary regimes, the run is invalid
- if primary early-accept geomean over V3.0.2 is <1.50x, do not continue toward formal high-performance wording
- if any primary early-accept row is below 1.00x over V3.0.2, stop and diagnose before more POD spend
- if control-regime correctness fails, do not promote the route even if primary speed rows pass

## Non-Authorization

Goal4713 does not authorize POD timing, all-app benchmarking, V4 release, formal high-performance wording, public Tier-3 support, arbitrary callbacks, or raw OptiX callback support.
