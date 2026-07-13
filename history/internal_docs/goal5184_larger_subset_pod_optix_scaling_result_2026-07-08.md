# Goal5184 - X-HD Larger Bounded POD/OptiX Subset Scaling Result

Date: 2026-07-08

## Status

```text
completed_larger_bounded_pod_optix_subset_scaling__all_source_pending
```

Goal5184 extends the Goal5183 POD/OptiX explicit-capacity gate to larger
bounded source subsets of the full public Stanford Dragon/HappyBuddha Level-B
candidate.

It keeps exact subset oracle validation for every case.

It does **not** claim:

- all-source full public Dragon/HappyBuddha route completion;
- exact paper dataset identity;
- paper figure reproduction;
- denominator-aligned author-vs-RTDL speedup;
- author performance parity;
- full X-HD paper reproduction.

## POD / Runtime

POD:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Route configuration:

```text
backend: optix
grid_shape: 32,32,32
frontier_row_capacity: 789009
frontier_row_order: native
frontier_inline_nearest: true
frontier_nearest_executor: auto
source_selection_policy: evenly-spaced
preprocessing: translate_each_input_to_min_bound
```

Native symbol:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
```

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset1024_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset2048_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset4096_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
```

## Results

```text
source_limit=256:
  matched=true
  route_abs_diff=0.0
  frontier_rows=1221
  capacity=789009
  policy=explicit
  total_candidate_distance_evaluations=202495
  rtdl_route_wall=1.3786990344524384 s

source_limit=512:
  matched=true
  route_abs_diff=0.0
  frontier_rows=2426
  capacity=789009
  policy=explicit
  total_candidate_distance_evaluations=403005
  rtdl_route_wall=0.7079002931714058 s

source_limit=1024:
  matched=true
  route_abs_diff=0.0
  frontier_rows=4516
  capacity=789009
  policy=explicit
  total_candidate_distance_evaluations=750202
  rtdl_route_wall=1.375817820429802 s

source_limit=2048:
  matched=true
  route_abs_diff=0.0
  frontier_rows=9691
  capacity=789009
  policy=explicit
  total_candidate_distance_evaluations=1617780
  rtdl_route_wall=1.3813620284199715 s

source_limit=4096:
  matched=true
  route_abs_diff=0.0
  frontier_rows=19229
  capacity=789009
  policy=explicit
  total_candidate_distance_evaluations=3203273
  rtdl_route_wall=1.378524236381054 s
```

All cases compare the RTDL route output against a vectorized exact subset
oracle and report `route_abs_diff=0.0`.

## Interpretation

Goal5184 materially increases the validated subset size:

```text
Goal5183 max source_limit: 128
Goal5184 max source_limit: 4096
```

The route still uses the full public HappyBuddha target with 543652 points.
Only the Dragon source side is bounded.

The explicit row capacity `789009` remains far above the observed native
frontier row counts through 4096 source rows:

```text
max_observed_native_frontier_rows = 19229
capacity = 789009
```

The native row count stays small relative to the local NumPy readiness row count
because `inline_nearest=true` lets the native producer reduce inline cell rows
inside traversal and emit only offload rows for the downstream continuation.

The non-monotonic route wall times should not be used as a speedup or scaling
claim. Each run is a separate POD process invocation and includes runtime noise
and setup effects. The authorized claim is correctness/capacity scaling, not
paper performance.

## Remaining Gap

Goal5184 still covers only a bounded subset of the full Dragon source:

```text
4096 / 437645 ~= 0.94%
```

All-source completion remains unproved. Exact subset oracle validation will
become increasingly expensive as the source limit grows:

```text
4096 * 543652 = 2226798592 exact subset pair evaluations
```

The next goal should explicitly decide how to validate larger subsets:

- continue exact subset oracle validation while feasible; or
- switch to route-only/all-source smoke with a clearly weaker claim; or
- obtain/run author `hd_exec` on the same full public candidate for an external
  value comparator.

No all-source or performance claim is authorized until that validation boundary
is settled.

## Validation

Focused local tests after the runner/path/capacity changes:

```text
py -m unittest ^
  tests.goal5182_xhd_explicit_frontier_capacity_test ^
  tests.goal5181_xhd_full_public_subset_scaling_gate_test ^
  tests.goal5180_xhd_full_public_feasibility_gate_test ^
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Observed:

```text
Ran 10 tests in 8.249s
OK
```

The Goal5184 artifacts were downloaded from the POD and parsed locally.

## Next Step

Goal5185 should choose the next validation mode for larger/full source runs.

Recommended decision order:

1. Try a larger exact-oracle subset if feasible (`8192` or `16384` sources).
2. If exact oracle becomes too expensive, add an explicit validation-mode field
   for route-only/all-source smoke and mark the lost evidence.
3. In parallel, locate or rebuild author `hd_exec` on the POD to compare the
   full public candidate's `HDResult` under the same preprocessing.

Do not claim full paper reproduction unless exact inputs or accepted Level-B
scope, author contract, RTDL route, and phase/performance boundaries are all
settled.
