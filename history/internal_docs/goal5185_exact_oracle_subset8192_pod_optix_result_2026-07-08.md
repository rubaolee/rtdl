# Goal5185 - X-HD Exact-Oracle Subset8192 POD/OptiX Result

Date: 2026-07-08

## Status

```text
completed_exact_oracle_subset8192_pod_optix__validation_cost_now_dominant
```

Goal5185 pushes the full-public Dragon/HappyBuddha Level-B bounded POD/OptiX
gate from source_limit `4096` to source_limit `8192` while keeping exact subset
oracle validation.

It does **not** claim:

- all-source route completion;
- exact paper dataset identity;
- paper figure reproduction;
- denominator-aligned author-vs-RTDL speedup;
- author performance parity;
- full X-HD paper reproduction.

## Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset8192_optix_goal5185_graphics_dragon_happy_buddha_2026-07-08.json
```

## Result

```text
goal: Goal5185
backend: optix
source_limit: 8192
full_target_count: 543652
matched: true
route_abs_diff: 0.0
frontier_rows: 38249
frontier_row_capacity: 789009
row_capacity_policy: explicit
native_symbol: rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
total_candidate_distance_evaluations: 6388308
exact_subset_pair_evaluations: 4453597184
rtdl_route_wall_sec: 1.4313380420207977
exact_subset_reference_sec: 62.3426823168993
```

## Interpretation

This is the largest current exact-oracle-validated subset for the full public
Stanford Dragon/HappyBuddha Level-B candidate:

```text
Goal5184 max exact subset: 4096 sources
Goal5185 max exact subset: 8192 sources
```

The route still uses the full public HappyBuddha target with `543652` points.
Only the Dragon source side is bounded:

```text
8192 / 437645 ~= 1.87%
```

The explicit native frontier row capacity remains safe:

```text
observed frontier rows: 38249
capacity: 789009
```

The exact subset oracle is now the expensive part of the validation protocol:

```text
exact subset oracle: 62.34s
RTDL route wall:      1.43s
```

This does not make the route a paper-performance result. It only shows that
continuing to increase exact-oracle subset size will soon be dominated by the
oracle itself. A future all-source route may need a weaker validation mode or an
author `hd_exec` comparator.

## Next Decision

Goal5186 should choose one of these paths:

1. Run source_limit `16384` with exact subset oracle if the extra validation
   cost is acceptable.
2. Add an explicit route-only/all-source smoke mode and label it weaker
   evidence.
3. Locate/build author `hd_exec` on the POD and run the same full public
   Dragon/HappyBuddha candidate to obtain an external `HDResult` comparator.

The third option is the strongest path toward the user's requested state:

```text
Python/RTDL/partner implementation and author C++/CUDA/OptiX implementation
produce the same result for the same full public candidate.
```

Until then, do not claim all-source correctness or full paper reproduction.
