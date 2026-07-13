# Goal5247 Scalar Global-Bound Native-Grid Route Result

Date: 2026-07-09

## Verdict

```text
completed_scalar_hdresult_global_bound_route__new_scalar_best_with_witness_caveat
```

Goal5247 combines the Goal5246 native CUDA/Thrust grid-cell MBR builder with
the existing generic max-nearest global-bound early-break route.

This is now the fastest RTDL route for the representative Dragon -> scaled
AsianDragon same-source workload **when the required output is the scalar
directed Hausdorff distance (`HDResult`)**.

It is **not** an exact per-source witness route.

## Boundary

Allowed claim:

```text
RTDL matches the author rerun scalar HDResult for the Dragon -> scaled
AsianDragon same-source public workload, using a generic native-grid +
generic max-nearest global-bound route.
```

Forbidden claims:

```text
full X-HD paper reproduction complete
exact paper byte-input identity
paper-log exact match
Figure reproduction
author internal Running.AvgTime parity
exact per-source witnesses
multi-workload Level-B completion
```

## Route

```text
--grid-cell-builder native_cuda
--initial-state local-grid-cell
--local-grid-seed-executor native_cuda
--frontier-inline-nearest
--global-bound-early-break
--frontier-row-order native
--grid-shape 96,60,72
```

The route is generic:

```text
native grid-cell MBR builder        = generic point-grid grouping
local-grid nearest seed             = generic nearest upper-bound seed
cell-MBR frontier traversal         = generic cell-MBR nearest frontier
global-bound early break            = generic max-nearest scalar shortcut
max-nearest reduction               = generic max nearest witness/value
```

No X-HD-specific RTDL core primitive was added.

## POD Evidence

Workload:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
direction = directed-a-to-b
preprocessing = translate_each_input_to_min_bound
author HDResult = 0.06536787003278732
tolerance = 1e-6
```

Evidence files:

```text
history/internal_docs/goal5247_native_grid_global_bound_repeat1_2026-07-09.json
history/internal_docs/goal5247_native_grid_global_bound_repeat2_2026-07-09.json
history/internal_docs/goal5247_native_grid_global_bound_repeat3_2026-07-09.json
```

All three runs:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
per_source_witness_exact = false
global_bound_early_break = true
```

## Performance

Three same-POD repeats:

```text
direction_total = 0.9754644558s, 0.9755396098s, 0.9622887596s
median direction_total = 0.9754644558s

total_sec = 1.7241097316s, 1.7368618175s, 1.7167503238s
median total_sec = 1.7241097316s
```

Phase medians:

```text
grid_cell_mbrs      = 0.4579305202s
initial_state_seed  = 0.2539756373s
frontier_rows       = 0.2216607854s
```

Global-bound telemetry:

```text
early_break_count median = 428,711 / 437,645 sources
per_source_witness_exact = false
```

The frontier phase moved substantially:

```text
Goal5246 exact-witness frontier_rows median = 1.3354s
Goal5247 scalar global-bound frontier median = 0.2217s
```

## Comparison To Recent Routes

| Route | Median direction_total | Witness status |
|---|---:|---|
| Goal5244 best before native grid builder | ~2.3042s | exact per-source |
| Goal5246 native grid builder | 2.0793s | exact per-source |
| Goal5247 native grid + global bound | 0.9755s | scalar exact, per-source witnesses approximate |

## Author Denominators

Two denominators must remain separate.

Author complete process wall from the prior same-POD performance packet:

```text
author process wall = 2.6587867364287376s
```

Current author JSON internal timing:

```text
Running.AvgTime = 82.5102 ms
```

Goal5247 ratios:

```text
RTDL route / author process wall = 0.367x
RTDL total / author process wall = 0.648x
RTDL route / author internal Running.AvgTime = 11.82x slower
```

Interpretation:

- Against full author process wall, RTDL is faster for this bounded public
  same-source run.
- Against the author's internal RT algorithm timing, RTDL remains much slower.
- These are different denominators and must not be collapsed into one headline.

## Why The Route Is Faster

The global-bound route is valid for scalar max-nearest / directed-Hausdorff
value computation:

```text
if a source's current upper-bound nearest distance is <= an already published
global max-nearest value, that source cannot increase the final scalar max.
```

The native traversal can therefore early-abort many sources while preserving the
final scalar HDResult. It does not preserve exact nearest witness columns for
those aborted sources.

## What This Proves

- RTDL can match the author rerun scalar `HDResult` for this large public
  graphics workload.
- The generic global-bound route dramatically reduces the frontier phase.
- The current best scalar route is under 1 second for `direction_total` on this
  POD and workload.

## What This Does Not Prove

- It does not prove exact per-source witnesses.
- It does not prove full X-HD paper reproduction.
- It does not prove paper log byte-input identity.
- It does not reproduce the paper figures.
- It does not prove parity with author internal `Running.AvgTime`.
- It does not prove the same behavior on all X-HD paper target categories.

## Recommendation

Use Goal5247 as the current best scalar `HDResult` route for this Level-B public
workload, with the witness caveat always attached.

Next work should be one of:

1. Run a second large Level-B public workload with the Goal5247 route.
2. Investigate how much of the remaining `~0.46s` grid builder and `~0.25s`
   local-grid seed can be prepared/reused without changing the denominator.
3. Continue the algorithmic gap analysis against author internal `Running.AvgTime`.
