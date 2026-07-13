# Goal5182 - X-HD Explicit Frontier Capacity Readiness Result

Date: 2026-07-08

## Status

```text
completed_local_explicit_capacity_readiness__pod_optix_execution_pending
```

Goal5182 threads an explicit fail-closed frontier row capacity through the
X-HD full-public subset route runners and records a local readiness artifact
for the next POD/OptiX bounded gate.

This goal does **not** claim:

- all-source full public Dragon/HappyBuddha route completion;
- native/POD OptiX capacity validation;
- exact paper dataset identity;
- paper figure reproduction;
- author performance parity or a speedup ratio;
- full X-HD paper reproduction.

## Code Changes

### Generic RTDL helper metadata

`src/rtdsl/partner_continuations.py` now exposes explicit-capacity metadata
from the dimension-generic NumPy `cell_mbr_nearest_frontier_numpy_columns`
reference path:

```text
row_capacity
full_row_capacity
row_capacity_policy
row_capacity_attempts
attempted_count
```

The helper already failed closed when `row_capacity` was too small. Goal5182
adds metadata so the capacity policy is visible to callers and review artifacts.

### X-HD route runner plumbing

`Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py`
now accepts and forwards:

```text
frontier_row_capacity
```

to both:

```text
rt.cell_mbr_nearest_frontier_native_3d_optix_columns(...)
rt.cell_mbr_nearest_frontier_numpy_columns(...)
```

The route summary now records:

```text
frontier_row_capacity_requested
frontier_row_capacity
frontier_full_row_capacity
frontier_row_capacity_policy
frontier_row_capacity_attempts
frontier_attempted_count
```

### Full-public runners

The Goal5180 and Goal5181 runners now accept:

```text
--frontier-row-capacity <int>
```

and pass it through to the shared route helper.

Goal5181's scaling runner also accepts:

```text
--run-goal <label>
```

so a reused runner can produce a Goal5182-labeled readiness artifact without
changing the schema.

## Local Readiness Artifact

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_explicit_capacity_readiness_goal5182_graphics_dragon_happy_buddha_2026-07-08.json
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_full_public_subset_scaling_gate.py ^
  --run-goal Goal5182 ^
  --bridge Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json ^
  --profile Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json ^
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_full_public_explicit_capacity_readiness_goal5182_graphics_dragon_happy_buddha_2026-07-08.json ^
  --backend numpy ^
  --grid-shape 32,32,32 ^
  --source-limits 16,64,128 ^
  --source-selection-policy evenly-spaced ^
  --translate-each-input-to-min-bound ^
  --frontier-nearest-executor auto ^
  --frontier-row-order native ^
  --frontier-inline-nearest ^
  --frontier-row-capacity 789009 ^
  --max-exact-pair-evaluations 100000000 ^
  --tolerance 1e-9
```

Result:

```text
goal: Goal5182
all_matched: true
max_frontier_row_count: 526006
frontier_row_capacity_requested: 789009
```

Per-case:

```text
source_limit=16:  matched=true, route_abs_diff=0.0, frontier_rows=58518,  capacity=789009, policy=explicit
source_limit=64:  matched=true, route_abs_diff=0.0, frontier_rows=306165, capacity=789009, policy=explicit
source_limit=128: matched=true, route_abs_diff=0.0, frontier_rows=526006, capacity=789009, policy=explicit
```

The capacity value `789009` is the Goal5181 planning value:

```text
ceil(526006 * 1.5) = 789009
```

## Regression Tests

Added:

```text
tests/goal5182_xhd_explicit_frontier_capacity_test.py
```

The test covers:

1. a direct route helper fixture where the true frontier row count is 4;
2. `frontier_row_capacity=3` raises `RuntimeError` with
   `fail_closed_overflow`;
3. `frontier_row_capacity=4` succeeds and records explicit capacity metadata;
4. the full-public subset scaling runner carries capacity metadata into the
   case summary;
5. claim-boundary flags remain false for full-paper/performance claims.

Validation command:

```text
py -m unittest ^
  tests.goal5182_xhd_explicit_frontier_capacity_test ^
  tests.goal5181_xhd_full_public_subset_scaling_gate_test ^
  tests.goal5180_xhd_full_public_feasibility_gate_test ^
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Observed:

```text
Ran 10 tests in 1.748s
OK
```

The Windows Python launcher printed:

```text
Could not find platform independent libraries <prefix>
```

This is the known local environment noise and did not affect the passing tests.

## Interpretation

Goal5182 closes the gap between Goal5181's capacity planning number and the
route runners used by the full-public subset gates.

It proves locally that:

- explicit capacity can be supplied by the paper-app runner;
- capacity is forwarded into the generic RTDL frontier helper;
- too-small explicit capacity fails closed rather than truncating rows;
- capacity metadata is written into the route artifacts;
- the existing bounded 16/64/128 source-subset cases still match exact subset
  oracles with explicit capacity enabled.

It does **not** prove that the POD/OptiX native backend accepts this capacity
on the full public candidate. That remains the next goal.

## Next Step

Goal5183 should run the same bounded source-limit set on a CUDA/OptiX POD with
explicit capacity:

```text
--backend optix
--source-limits 16,64,128
--frontier-row-capacity 789009
```

The acceptance criteria should require:

- `matched=true` for every source limit;
- `route_abs_diff=0.0` against exact subset oracles;
- native frontier metadata records `row_capacity_policy=explicit`;
- no native overflow;
- no all-source/full-paper/performance-ratio claim.
