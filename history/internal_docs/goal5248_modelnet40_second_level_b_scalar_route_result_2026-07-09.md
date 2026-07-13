# Goal5248 - X-HD Second Level-B Workload Scalar Route Result

Date: 2026-07-09

## Verdict

```text
completed_second_level_b_public_workload_scalar_hdresult_gate__modelnet40_airplane_matched
```

Goal5248 applies the current Goal5247 scalar `HDResult` route to a second
large Level-B public workload beyond the Dragon -> scaled AsianDragon graphics
case:

```text
ModelNet40 airplane_0036.off -> airplane_0515.off
```

This pair is from the prior ModelNet40 packet:

```text
Goal5229: all 400 unique ModelNet40 public OFF pairs matched
Goal5230: all 2000 ModelNet40 paper-log records value-covered
Goal5231: denominator-explicit performance matrix for those 400 pairs
```

Goal5248 does not rerun the whole ModelNet40 all-400 batch. It selects one
large, already-proven public pair and runs the current scalar route on it to
check whether the Goal5247 route generalizes beyond the single graphics
workload.

## Input

```text
input1:
  /tmp/xhd-modelnet40/extracted/ModelNet40/airplane/train/airplane_0036.off
input2:
  /tmp/xhd-modelnet40/extracted/ModelNet40/airplane/train/airplane_0515.off
author json:
  /tmp/xhd-goal5229/modelnet40_all400_float32norm/author/0000_airplane_0036__airplane_0515.json
```

Point counts:

```text
input1 points = 370,568
input2 points = 376,741
total points  = 747,309
```

Preprocessing:

```text
normalize_each_input_to_author_float32_unit_box
```

This matches the ModelNet40 paper-branch public-OFF route established in
Goals5222-5231.

## Route

Command shape:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
  --input-type off
  --n-dims 3
  --normalize-each-input-to-author-unit-box
  --author-float32-normalization
  --backend optix
  --grid-shape 96,60,72
  --initial-state local-grid-cell
  --local-grid-seed-executor native_cuda
  --grid-cell-builder native_cuda
  --frontier-inline-nearest
  --global-bound-early-break
  --frontier-row-order native
  --direction-mode directed-a-to-b
  --validation-mode author-only
```

Important validation boundary:

```text
validation_mode = author-only
exact_reference = null
```

The pair has about 747K points. Running an exact all-pairs reference would be
quadratic and is not part of this goal. Correctness is checked against the
same-input author JSON from the prior ModelNet40 author run.

## Evidence Files

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5248_modelnet40_airplane_scalar_route_repeat1_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5248_modelnet40_airplane_scalar_route_repeat2_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5248_modelnet40_airplane_scalar_route_repeat3_2026-07-09.json
```

## Correctness

All three same-POD repeats matched the author rerun:

```text
matched = true, true, true
author_hd_result = 0.09761668741703033
rtdl author_comparison_distance = 0.09761668669590366
author_abs_diff = 7.211266722650933e-10
tolerance = 1e-6
```

This proves scalar `HDResult` agreement for this second Level-B public workload.

It does **not** prove:

```text
exact per-source witness agreement
exact paper byte-input identity
all ModelNet40 cases through this scalar route
full X-HD paper reproduction
author internal Running.AvgTime parity
Figure 5-11 reproduction
```

## Performance

Three same-POD repeats:

```text
repeat1 route_sec = 0.6935913562774658
repeat2 route_sec = 0.6931251287460327
repeat3 route_sec = 0.6952938660979271

median route_sec = 0.6935913562774658
```

Full app time, including input load and author JSON validation:

```text
repeat1 total_sec = 2.5124128833413124
repeat2 total_sec = 2.4659434109926224
repeat3 total_sec = 2.4796682223677635

median total_sec = 2.4796682223677635
```

Median phase timings inside the directed route:

```text
direction_total       = 0.6935194358229637
grid_cell_mbrs        = 0.1875903457403183
initial_state_seed    = 0.12480570375919342
frontier_rows         = 0.15023931860923767
nearest_continuation  = 0.20464890450239182
```

Median route statistics:

```text
frontier_row_count = 39,452
global_bound_early_break_count = 358,412 / 370,568 sources
```

As in Goal5247, this is a scalar `HDResult` route:

```text
per_source_witness_exact = false
```

The global-bound early break removes most source rows from exact witness
continuation. That is valid for the final max-nearest scalar distance, but it
means this route is not an exact per-source witness route.

## Comparison To Prior ModelNet40 Route

The prior Goal5229 exact normalized route for this same pair reported:

```text
rtdl_normalized_route.route_wall_sec = 2.806039124727249
rtdl_normalized_route.total_sec      = 4.602262333035469
author_normalized.process_wall_sec   = 1.3181999996304512
author_normalized.running_avg_time_ms = 7.498
```

Goal5248 current scalar route:

```text
median route_sec = 0.6935913562774658
median total_sec = 2.4796682223677635
```

Diagnostic ratios for this single case:

```text
current scalar route / prior exact normalized route wall = 0.247x
current scalar total / prior exact normalized total      = 0.539x
current scalar route / author process wall              = 0.526x
current scalar route / author internal AvgTime          = 92.5x slower
```

These ratios are diagnostics only. They are not authorized as paper-performance
claims because the route is not the author X-HD RT-core algorithm, and the
author internal `Running.AvgTime` is a different denominator from process wall
or RTDL route wall.

## What This Adds To The X-HD Line

Before Goal5248, the Goal5247 scalar route had been shown on one large public
workload:

```text
Dragon -> scaled AsianDragon
```

Goal5248 adds a second large public workload:

```text
ModelNet40 airplane_0036 -> airplane_0515
```

The route matched author in both workload families:

```text
graphics PLY workload: matched author rerun, abs diff ~= 2.37e-9
ModelNet40 OFF workload: matched author rerun, abs diff ~= 7.21e-10
```

This strengthens Level-B same-input public workload evidence from one workload
to two workload families. It still does not prove complete paper reproduction.

## Claim Boundary

Allowed:

```text
The current scalar Goal5247 route matches author HDResult on a second large
Level-B public workload, ModelNet40 airplane_0036 -> airplane_0515, with
median route time about 0.694s on the current POD.
```

Forbidden:

```text
full X-HD paper reproduction complete
all ModelNet40 cases run through this scalar route
exact per-source witness output
exact paper byte-input identity
paper-log exact input match
Figure 5-11 reproduction
author internal Running.AvgTime parity
author speedup or parity claim
```

## Next Step

Send Goal5248 for strict review. If accepted, update the X-HD status from
"single public workload only" to:

```text
two large Level-B public workload families have scalar HDResult author matches
```

The next technical decisions are separate:

```text
1. whether to run more ModelNet40 cases through the scalar route,
2. whether to pursue exact per-source witnesses for the early-break route, or
3. whether to stop Level-B expansion and return to exact paper dataset
   provenance / Figure reproduction blockers.
```
