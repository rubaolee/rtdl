# Goal5152 - Nearest-Cell-MBR Seeded Pruning Result

## Verdict

`completed_generic_nearest_cell_mbr_seeded_pruning`

## What Changed

Goal5152 adds a generic nearest-state initializer:

```text
seed_nearest_witness_from_nearest_cell_mbr_numpy_columns
```

It chooses, for each query point, the closest non-empty target cell MBR, scans
that cell's point span, and returns an initial nearest witness:

```text
source_ids
nearest_item_ids
nearest_distances
seed_cell_ids
```

Those distances are real distances to real target points, so they are valid
upper bounds. The cell-MBR frontier producer can then use them as
`current_best_distances` to prune cells whose MBR lower bound cannot improve the
state.

## API Boundary

This is not an X-HD primitive. It is a generic nearest-state seed over:

- query point columns;
- target point columns;
- generic grid-cell MBR columns.

The local tests include source-window app-neutral scans and a non-Hausdorff
style pruning correctness case.

## Local Test Evidence

```text
py -m unittest tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test

Ran 8 tests OK
```

POD regression:

```text
python3 -m unittest \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 5 tests OK
```

## Representative Sample256 Evidence

Baseline from Goal5151:

```text
unseeded candidate_distance_evaluations = 65,536 per directed pass
```

Goal5152 local NumPy seeded route:

```text
matched = true
author_hd_result = 0.11612465232610703
author_comparison_distance = 0.11612464969699586
rtdl_exact_abs_diff = 0.0

directed_a_to_b:
  initial_candidate_distance_evaluations = 566
  continuation_candidate_distance_evaluations = 631
  total_candidate_distance_evaluations = 1197

directed_b_to_a:
  initial_candidate_distance_evaluations = 604
  continuation_candidate_distance_evaluations = 624
  total_candidate_distance_evaluations = 1228
```

Goal5152 POD OptiX seeded route:

```text
matched = true
backend = optix
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
author_hd_result = 0.11612465232610703
author_comparison_distance = 0.11612464969699586
rtdl_exact_abs_diff = 0.0

directed_a_to_b:
  initial_candidate_distance_evaluations = 566
  continuation_candidate_distance_evaluations = 635
  total_candidate_distance_evaluations = 1201

directed_b_to_a:
  initial_candidate_distance_evaluations = 604
  continuation_candidate_distance_evaluations = 633
  total_candidate_distance_evaluations = 1237
```

Evidence files:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_seeded_numpy_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_seeded_optix_summary_pod.json
```

## Interpretation

This is a real algorithmic-work reduction:

```text
65,536 candidate point distances per direction
  -> about 1,200 total seed + continuation point distances per direction
```

It is not yet a clean performance win. The seed still performs Python-level
cell-MBR tests:

```text
directed_a_to_b initial_cell_mbr_tests = 40,192
directed_b_to_a initial_cell_mbr_tests = 38,912
```

So the next system task is to move the seed/nearest-state update into a native
or otherwise compiled generic route, not to claim performance from this Python
reference implementation.

## Claim Boundary

This goal does not claim:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- author fused RT-core algorithm equivalence;
- performance parity or speedup;
- completion of the full native X-HD RT route.

It proves that a generic nearest-state seed can preserve correctness while
substantially reducing candidate point-distance work on a representative
same-source X-HD fixture.
