# Goal5240 X-HD Nearest Continuation Executor Matrix Result

Date: 2026-07-09

## Verdict

`implemented__nearest_continuation_executor_win__auto_uses_numba_parallel__review_pending`

Goal5240 attacks the dominant Goal5239 bottleneck:

```text
nearest_continuation = 28.124958105385303s
```

The first hypothesis was deliberately conservative:

```text
Before designing a new fused native primitive, test whether an existing generic
frontier-nearest executor already fixes part of the problem.
```

Result:

```text
Yes. Existing generic `numba_parallel` preserves exactness and cuts the
all-source Dragon -> scaled AsianDragon route direction time from ~31.0s to
~9.2-10.1s on the same POD.
```

This is a real RTDL route improvement, not author parity and not Figure
reproduction.

## Fixed Contract

All Goal5240 runs keep the successful exact-value Goal5237 mode fixed:

```text
source = Dragon, 437,645 points
target = scaled AsianDragon, 3,609,600 points
backend = optix
preprocessing = translate_each_input_to_min_bound
global_bound_early_break = false
frontier_row_capacity = 5,000,000
full_pairwise_rows_materialized = false
author HDResult = 0.06536787003278732
author_tolerance = 1e-6
```

Therefore this matrix changes only the generic nearest-continuation executor.

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_goal5240_dragon_asian_scaled_all_source_optix_numba_baseline_rerun_pod_2026-07-09.json
  xhd_goal5240_dragon_asian_scaled_all_source_optix_numba_parallel_pod_2026-07-09.json
  xhd_goal5240_dragon_asian_scaled_all_source_optix_auto_pod_2026-07-09.json
```

POD preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Remote source tree:

```text
/tmp/rtdl_goal5236
RTDL_OPTIX_LIB=/tmp/rtdl_goal5236/build/librtdl_optix.so
```

The remote tree is the current-source rebuilt tree from Goal5236.

## Results

### Baseline rerun: `frontier_nearest_executor=numba`

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
distance/source/target = 0.06536787240753439 / 49577 / 1803033
nearest_executor = numba

direction_total = 31.01092080026865s
nearest_continuation = 28.445445612072945s
frontier_rows = 0.824980191886425s
initial_state_seed = 1.1118629723787308s
grid_cell_mbrs = 0.5946381837129593s

frontier_row_count = 3,306,122
candidate_distance_evaluations = 6,417,800,660
per_source_witness_exact = true
global_bound_early_break = false
```

### Explicit parallel route: `frontier_nearest_executor=numba_parallel`

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
distance/source/target = 0.06536787240753439 / 49577 / 1803033
nearest_executor = numba_parallel

direction_total = 10.097781844437122s
nearest_continuation = 7.6326252073049545s
frontier_rows = 0.827768974006176s
initial_state_seed = 1.0200607404112816s
grid_cell_mbrs = 0.5838241875171661s

frontier_row_count = 3,306,122
candidate_distance_evaluations = 6,417,800,660
per_source_witness_exact = true
global_bound_early_break = false
```

### Recommended/default route: `frontier_nearest_executor=auto`

`auto` resolves to the same generic parallel executor:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
distance/source/target = 0.06536787240753439 / 49577 / 1803033
nearest_executor = numba_parallel

direction_total = 9.171282961964607s
nearest_continuation = 6.6945535987615585s
frontier_rows = 0.8216453343629837s
initial_state_seed = 1.0353290736675262s
grid_cell_mbrs = 0.5838241875171661s

frontier_row_count = 3,306,122
candidate_distance_evaluations = 6,417,800,660
per_source_witness_exact = true
global_bound_early_break = false
```

The top-level route summary for `auto` reports:

```text
load_full_inputs = 0.493181012570858s
median_route_wall_sec = 9.430342733860016s
total = 9.923879362642765s
```

## Improvement

Compared with the same-POD `numba` baseline rerun:

```text
route direction speedup:
  31.01092080026865 / 10.097781844437122 = 3.071062662871113x

nearest continuation speedup:
  28.445445612072945 / 7.6326252073049545 = 3.726823319563585x
```

Using the `auto` run:

```text
route direction speedup:
  31.01092080026865 / 9.171282961964607 ~= 3.38x

nearest continuation speedup:
  28.445445612072945 / 6.6945535987615585 ~= 4.25x
```

Compared with Goal5239's original report:

```text
route direction:
  30.49027620255947s -> 9.171282961964607s

nearest continuation:
  28.124958105385303s -> 6.6945535987615585s
```

This preserves the author match:

```text
author_abs_diff = 2.3747470656587666e-09
matched = true
```

## Interpretation

Goal5239's 28s nearest-continuation mountain was partly an executor-selection
problem:

```text
serial numba loop over grouped frontier queries
  -> numba_parallel grouped query loop
```

The work count is unchanged:

```text
candidate_distance_evaluations = 6,417,800,660
frontier_row_count = 3,306,122
```

So this is not an algorithmic pruning win. It is a generic parallel execution
win over the same exact work.

That distinction matters:

```text
solved:
  serial executor bottleneck

not solved:
  too many candidate point-distance evaluations
  lack of fused author-style RT radius-growth / pruning / payload-state update
```

## Relationship To Author Performance

Goal5239 author measurement:

```text
author process wall = 2.6587867364287376s
author internal Running.AvgTime = 83.49680000000001 ms
```

Goal5240 `auto` RTDL route:

```text
route direction_total = 9.171282961964607s
nearest_continuation = 6.6945535987615585s
```

Diagnostic labelled ratios:

```text
RTDL route direction / author process wall
  = 9.171282961964607 / 2.6587867364287376
  ~= 3.45x slower

RTDL route direction / author internal Running.AvgTime
  = 9.171282961964607 / 0.0834968
  ~= 109.84x slower

RTDL nearest continuation / author internal Running.AvgTime
  = 6.6945535987615585 / 0.0834968
  ~= 80.18x
```

These are denominator-explicit diagnostics only. They are not Figure 6 claims,
not author parity, and not paper speedup ratios.

## Claim Boundary

Allowed:

```text
On the Dragon -> scaled AsianDragon all-source exact-value route, the existing
generic `auto` / `numba_parallel` nearest-continuation executor preserves the
author HDResult match and reduces route direction time from about 31s to about
9-10s on the same POD.
```

Not allowed:

```text
RTDL matches author performance.
RTDL reproduces Figure 6 performance.
The candidate-distance workload has been reduced.
The author's fused RT-core algorithm has been reproduced.
Full X-HD paper reproduction is complete.
This result generalizes to all X-HD workloads.
```

## Next Recommended Work

Goal5240 exits as:

```text
nearest_continuation_executor_win_promote_generic
```

Immediate next route choice:

```text
Use `frontier_nearest_executor=auto` as the recommended exact route setting.
It resolves to `numba_parallel` when Numba is available.
```

Next performance mountain:

```text
Reduce the 6.4B candidate point-distance evaluations, not merely parallelize
them.
```

Recommended Goal5241:

```text
Design a generic fused nearest-continuation / pruning primitive or a stronger
generic seed/frontier policy that reduces candidate work while preserving
per_source_witness_exact=true and avoiding X-HD-specific core semantics.
```

Do not spend next effort on:

```text
PLY loading
max reduction
grid MBR construction
frontier row production
```

Those are no longer the dominant phase under the `auto` route.
